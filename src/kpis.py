"""Neighbourhood-level KPI aggregation for the Urban Rental Intelligence Copilot.

Reads listing-level features produced by ``src.features`` and aggregates them
into one row per (city, geo_key). The output is the input that Member 3 will
cluster on and Member 4's chatbot will query.

Public entry point: ``compute_neighbourhood_kpis(features)``.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

COMMERCIAL_TIERS = {"commercial", "super_commercial"}

# Group by (city, geo_key) only — geo_level is derived after.
# A small number of London areas (Belgravia, Knightsbridge, Maida Hill, Maida Vale)
# appear in BOTH the AirDNA subdivision column AND the neighborhood column for
# different listings. Grouping by geo_level too would split them into two rows.
GROUP_KEYS = ["city", "geo_key"]


def _safe_share(numer: pd.Series, denom: pd.Series) -> pd.Series:
    """Element-wise share that returns NaN when the denominator is 0."""
    return np.where(denom > 0, numer / denom, np.nan)


def compute_neighbourhood_kpis(features: pd.DataFrame) -> pd.DataFrame:
    """Aggregate listing-level features into the neighbourhood KPI table.

    Groups by (``city``, ``geo_key``, ``geo_level``). Listings with no known
    geographic key (``geo_level == "unknown"``) are dropped — they cannot be
    placed on a map or aggregated honestly.

    Returns a DataFrame with one row per neighbourhood and the KPI columns
    Member 3 will cluster on and Member 4 will retrieve.
    """
    df = features.loc[features["geo_level"] != "unknown"].copy()

    # Pre-compute helpers so we can group once
    df["_is_commercial_host"] = df["host_commercial_tier"].isin(COMMERCIAL_TIERS)

    grouped = df.groupby(GROUP_KEYS, dropna=False, observed=True)

    out = pd.DataFrame({
        "str_density": grouped.size(),
        "active_listings": grouped["is_active_recent"].sum().astype(int),
        "entire_home_count": grouped["entire_home_flag"].sum().astype(int),
        "median_nightly_price": grouped["ttm_avg_rate"].median(),
        "p25_price": grouped["ttm_avg_rate"].quantile(0.25),
        "p75_price": grouped["ttm_avg_rate"].quantile(0.75),
        # avg_occupancy defaults to 0 for neighbourhoods where AirDNA reports no
        # occupancy data for any listing. Verified safe: the 26 affected rows
        # (June 2026) are all tiny peripheral subdivisions (max 3 listings each),
        # all flagged tier_sample_adequate=False, with zero policy signal.
        # Using NaN would break M3's clustering and leak NaN into M4's chatbot;
        # 0 is the honest semantic (no measurable activity).
        "avg_occupancy": grouped["l90d_occupancy"].mean().fillna(0),
        "total_revenue": grouped["ttm_revenue"].sum(),
        "breach_count_90": grouped["breach_90_flag"].sum().astype(int),
        "breach_count_60": grouped["breach_60_flag"].sum().astype(int),
        "breach_count_30": grouped["breach_30_flag"].sum().astype(int),
        "reside_unregistered_count": grouped["reside_unregistered_flag"].sum().astype(int),
        "multi_listing_host_count": grouped["multi_listing_host"].sum().astype(int),
        "commercial_host_share": grouped["_is_commercial_host"].mean(),
    })

    # Share columns — pure functions of counts already in `out`
    out["entire_home_share"] = _safe_share(out["entire_home_count"], out["str_density"])
    out["multi_listing_host_share"] = _safe_share(
        out["multi_listing_host_count"], out["str_density"]
    )
    out["active_share"] = _safe_share(out["active_listings"], out["str_density"])

    for cap in (90, 60, 30):
        out[f"breach_rate_{cap}"] = _safe_share(
            out[f"breach_count_{cap}"], out["entire_home_count"]
        )

    out["reside_unregistered_share"] = _safe_share(
        out["reside_unregistered_count"], out["entire_home_count"]
    )

    # Professional-management share — only over listings where the field is known
    known = df.loc[df["professional_management_known"]]
    if not known.empty:
        prof = (
            known.groupby(GROUP_KEYS, dropna=False, observed=True)[
                "professional_management_flag"
            ]
            .mean()
            .rename("professional_management_share")
        )
        out = out.join(prof, how="left")
    else:
        out["professional_management_share"] = np.nan

    # Derive geo_level: prefer 'subdivision' if any source row was subdivision-level
    geo_level = (
        df.groupby(GROUP_KEYS, observed=True)["geo_level"]
        .agg(lambda s: "subdivision" if (s == "subdivision").any() else "neighborhood")
        .rename("geo_level")
    )
    out = out.join(geo_level)

    # Tidy: reset index, round floats, sort, move geo_level next to geo_key
    out = out.reset_index().sort_values(["city", "geo_key"], ignore_index=True)

    # Item C (mentor feedback): tier 1/2/3 by concentration + price.
    # Added at the end so it can reference the computed str_density and
    # median_nightly_price. Pure additive operation — does not alter any
    # existing column. Re-run via notebook 04.
    out = add_concentration_price_tier(out)

    cols = ["city", "geo_key", "geo_level"] + [
        c for c in out.columns if c not in ("city", "geo_key", "geo_level")
    ]
    out = out[cols]

    float_cols = out.select_dtypes(include="float").columns
    out[float_cols] = out[float_cols].round(4)

    return out


# --- Item C: concentration + price risk tier ---------------------------------

def add_concentration_price_tier(
    kpis: pd.DataFrame,
    min_density: int = 5,
    quantile: float = 0.75,
) -> pd.DataFrame:
    """Add ``tier_concentration_price`` and ``tier_sample_adequate`` columns.

    Mentor feedback (June 2026): the policy-advisor framing wants a clean
    tier-1/2/3 signal driven by concentration AND price together.

    - tier_1: top-quartile str_density AND top-quartile median_nightly_price (per city)
    - tier_2: top-quartile in exactly one of the two
    - tier_3: top-quartile in neither

    Neighbourhoods below ``min_density`` listings are still labelled (defaulted to
    tier_3 for sorting cleanliness) but flagged via ``tier_sample_adequate=False``
    so the chatbot can caveat the tier honestly. Thresholds are per-city quartiles
    because BCN and LDN have different absolute scales.
    """
    out = kpis.copy()
    out["tier_concentration_price"] = "tier_3"
    out["tier_sample_adequate"] = out["str_density"] >= min_density

    for city in out["city"].unique():
        city_mask = out["city"] == city
        eligible = city_mask & out["tier_sample_adequate"] & out["median_nightly_price"].notna()
        if eligible.sum() == 0:
            continue
        d_thresh = out.loc[eligible, "str_density"].quantile(quantile)
        p_thresh = out.loc[eligible, "median_nightly_price"].quantile(quantile)
        high_d = (out["str_density"] >= d_thresh) & city_mask
        high_p = (out["median_nightly_price"] >= p_thresh) & city_mask
        out.loc[eligible & high_d & high_p, "tier_concentration_price"] = "tier_1"
        out.loc[eligible & (high_d ^ high_p), "tier_concentration_price"] = "tier_2"

    return out


def kpi_data_dictionary() -> pd.DataFrame:
    """Return a documentation DataFrame describing every KPI column.

    Member 3 uses this to know what to feed the clustering model;
    Member 4 lifts entries into chatbot tool docstrings.
    """
    rows = [
        ("city", "string", "City label (barcelona | london).", "—"),
        ("geo_key", "string", "Neighbourhood key — subdivision when available, else neighborhood.", "—"),
        ("geo_level", "string", "Resolution of geo_key: subdivision | neighborhood.", "—"),
        ("str_density", "int", "Total short-term-rental listings in the neighbourhood.", "count"),
        ("active_listings", "int", "Listings active in any of the last 12 months.", "count"),
        ("active_share", "float", "active_listings / str_density.", "ratio 0–1"),
        ("entire_home_count", "int", "Listings flagged entire-home.", "count"),
        ("entire_home_share", "float", "entire_home_count / str_density. Primary displacement proxy.", "ratio 0–1"),
        ("commercial_host_share", "float", "Share of listings owned by commercial+super-commercial hosts (>=5 listings).", "ratio 0–1"),
        ("multi_listing_host_count", "int", "Listings owned by hosts with >=2 listings.", "count"),
        ("multi_listing_host_share", "float", "multi_listing_host_count / str_density.", "ratio 0–1"),
        ("median_nightly_price", "float", "Median TTM average daily rate in EUR/GBP.", "currency"),
        ("p25_price", "float", "25th percentile of TTM nightly rate.", "currency"),
        ("p75_price", "float", "75th percentile of TTM nightly rate.", "currency"),
        ("avg_occupancy", "float", "Mean l90d_occupancy across listings in the neighbourhood. Defaults to 0.0 when AirDNA reports no occupancy data for any listing (only happens in tiny peripheral subdivisions; cross-check tier_sample_adequate before drawing conclusions).", "ratio 0–1"),
        ("total_revenue", "float", "Sum of TTM revenue across all listings (local currency).", "currency"),
        ("breach_count_90", "int", "Entire-home listings with ttm_days_booked > 90 — listings impacted at a 90-night cap.", "count"),
        ("breach_count_60", "int", "Entire-home listings with ttm_days_booked > 60.", "count"),
        ("breach_count_30", "int", "Entire-home listings with ttm_days_booked > 30.", "count"),
        ("breach_rate_90", "float", "breach_count_90 / entire_home_count.", "ratio 0–1"),
        ("breach_rate_60", "float", "breach_count_60 / entire_home_count.", "ratio 0–1"),
        ("breach_rate_30", "float", "breach_count_30 / entire_home_count.", "ratio 0–1"),
        ("reside_unregistered_count", "int", "Entire homes without a registration on record. Regulatory signal for Barcelona (RESIDE) — for London it's context only, not a breach.", "count"),
        ("reside_unregistered_share", "float", "reside_unregistered_count / entire_home_count.", "ratio 0–1"),
        ("professional_management_share", "float", "Share of professionally-managed listings, computed only over listings where the field was reported (avoids null-imputation bias).", "ratio 0–1"),
        ("tier_concentration_price", "string", "Policy-advisor risk tier (mentor update). tier_1 = top-quartile str_density AND median_nightly_price (per city); tier_2 = top-quartile in one; tier_3 = neither.", "tier_1|tier_2|tier_3"),
        ("tier_sample_adequate", "bool", "True if str_density >= 5; below that, the tier label is set to tier_3 but should be presented with a caveat.", "True/False"),
    ]
    return pd.DataFrame(rows, columns=["column", "dtype", "definition", "unit"])
