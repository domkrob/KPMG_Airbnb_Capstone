"""Exploratory Data Analysis helpers for the Urban Rental Intelligence Copilot.

Functions in this module return DataFrames or simple Python objects — they do
not produce plots. Plotting stays in the notebook so it's easy to iterate on.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from src.data_io import RAW_DIR

# London borough name prefixes that appear in the AirDNA `neighborhood` field
# but not in the geojson `neighbourhood` field.
LONDON_BOROUGH_PREFIXES = (
    "London Borough of ",
    "Royal Borough of ",
    "City of ",
)

# AirDNA records 13 Westminster sub-areas at the neighbourhood level instead of
# rolling them up to the borough. Without this mapping, Westminster appears
# empty on the LDN borough choropleth and the borough-level KPI table loses
# ~10% of the LDN sample. See subdivision_name_map.csv for documentation.
LDN_SUBAREA_TO_BOROUGH = {
    "Bayswater": "Westminster",
    "Belgravia": "Westminster",
    "Knightsbridge": "Westminster",
    "Maida Hill": "Westminster",
    "Maida Vale": "Westminster",
    "Marylebone": "Westminster",
    "Mayfair": "Westminster",
    "Millbank": "Westminster",
    "Paddington": "Westminster",
    "Pimlico": "Westminster",
    "Queen's Park": "Westminster",
    "St. John's Wood": "Westminster",
    "Victoria": "Westminster",
}

GEOJSON_NAME_FIELD = "neighbourhood"

# Manually verified BCN subdivision name mismatches between AirDNA and the
# Inside Airbnb geojson. Apply with .replace() before joining.
BCN_NAME_MAP = {
    "Gothic Quarter": "el Barri Gòtic",
    "Sants-Badal": "Sants - Badal",
    "Sant Andreu de Palomar": "Sant Andreu",
    "el Poble-sec": "el Poble Sec",
    "el Putget i Farró": "el Putxet i el Farró",
}


# --- Overview & rankings ------------------------------------------------------

def citywide_overview(features: pd.DataFrame) -> pd.DataFrame:
    """One row per city — top-line totals and medians for the executive view.

    Occupancy metrics are computed on **active listings only** because the
    inactive fleet (zombies) drags the median to zero and obscures the real
    occupancy story.
    """
    grouped = features.groupby("city")
    active = features[features["is_active_recent"]].groupby("city")
    out = pd.DataFrame({
        "total_listings": grouped.size(),
        "unique_hosts": grouped["host_id"].nunique(),
        "unique_subdivisions": grouped["subdivision"].nunique(),
        "active_listings": grouped["is_active_recent"].sum().astype(int),
        "entire_homes": grouped["entire_home_flag"].sum().astype(int),
        "entire_home_share": (
            grouped["entire_home_flag"].sum() / grouped.size()
        ).round(3),
        "median_nightly_price": grouped["ttm_avg_rate"].median().round(2),
        "median_occupancy_active": active["l90d_occupancy"].median().round(3),
        "mean_occupancy_active": active["l90d_occupancy"].mean().round(3),
        "total_revenue": grouped["ttm_revenue"].sum().round(0),
        "breach_90_total": grouped["breach_90_flag"].sum().astype(int),
        "reside_unregistered_total": grouped["reside_unregistered_flag"].sum().astype(int),
    })
    return out


def top_n_by(
    kpis: pd.DataFrame,
    metric: str,
    n: int = 10,
    city: str | None = None,
    min_density: int | None = None,
    ascending: bool = False,
    cols: list[str] | None = None,
) -> pd.DataFrame:
    """Return the top-N rows of ``kpis`` sorted by ``metric``."""
    df = kpis.copy()
    if city is not None:
        df = df[df["city"] == city]
    if min_density is not None:
        df = df[df["str_density"] >= min_density]
    df = df.sort_values(metric, ascending=ascending).head(n)
    if cols is None:
        cols = ["city", "geo_key", "str_density", metric]
    # Preserve order while deduplicating (e.g. when metric is str_density itself)
    cols = list(dict.fromkeys(cols))
    return df[cols].reset_index(drop=True)


# --- Host concentration -------------------------------------------------------

def host_concentration_summary(features: pd.DataFrame) -> pd.DataFrame:
    """How much of total revenue and listings is held by top X% of hosts."""
    rows = []
    for city, sub in features.groupby("city"):
        host_rev = (
            sub.groupby("host_id")["ttm_revenue"].sum().sort_values(ascending=False)
        )
        host_cnt = sub.groupby("host_id").size().sort_values(ascending=False)
        total_rev = host_rev.sum()
        total_listings = len(sub)
        for pct in (0.01, 0.05, 0.10, 0.20):
            top_n_hosts = max(int(len(host_rev) * pct), 1)
            rev_share = host_rev.head(top_n_hosts).sum() / total_rev if total_rev else 0
            listings_share = host_cnt.head(top_n_hosts).sum() / total_listings
            rows.append({
                "city": city,
                "top_pct_hosts": pct,
                "n_hosts": top_n_hosts,
                "revenue_share": round(rev_share, 4),
                "listings_share": round(listings_share, 4),
            })
    return pd.DataFrame(rows)


# --- Time-series / hotspots ---------------------------------------------------

def monthly_neighbourhood_panel(
    features: pd.DataFrame, monthly: pd.DataFrame
) -> pd.DataFrame:
    """Join monthly metrics with listing geo_key; aggregate to (city, geo_key, month_date).

    Drops a ``city`` column from ``monthly`` if present so the merge doesn't
    create a suffix collision and break the downstream groupby.
    """
    geo_map = features[["listing_id", "city", "geo_key", "geo_level"]]
    monthly_for_merge = monthly.drop(columns=["city"], errors="ignore")
    panel = monthly_for_merge.merge(geo_map, on="listing_id", how="inner")
    return (
        panel.groupby(["city", "geo_key", "month_date"], dropna=False)
        .agg(
            active_listings=("active", "sum"),
            avg_occupancy=("occupancy", "mean"),
            total_revenue=("revenue", "sum"),
        )
        .reset_index()
    )


def emerging_hotspots(
    features: pd.DataFrame,
    monthly: pd.DataFrame,
    recent_months: int = 6,
    prior_months: int = 6,
    top_n: int = 15,
    min_prior_active: int = 5,
) -> pd.DataFrame:
    """Subdivisions whose active-listing count grew most in recent vs prior window."""
    panel = monthly_neighbourhood_panel(features, monthly)
    max_date = panel["month_date"].max()
    recent_start = max_date - pd.DateOffset(months=recent_months - 1)
    prior_end = recent_start - pd.DateOffset(months=1)
    prior_start = prior_end - pd.DateOffset(months=prior_months - 1)

    recent = (
        panel[panel["month_date"] >= recent_start]
        .groupby(["city", "geo_key"])
        .agg(recent_active=("active_listings", "mean"),
             recent_revenue=("total_revenue", "mean"))
    )
    prior = (
        panel[(panel["month_date"] >= prior_start) & (panel["month_date"] <= prior_end)]
        .groupby(["city", "geo_key"])
        .agg(prior_active=("active_listings", "mean"),
             prior_revenue=("total_revenue", "mean"))
    )
    growth = recent.join(prior, how="inner")
    growth["active_growth_pct"] = (
        (growth["recent_active"] - growth["prior_active"])
        / growth["prior_active"].replace(0, np.nan) * 100
    ).round(2)
    growth["revenue_growth_pct"] = (
        (growth["recent_revenue"] - growth["prior_revenue"])
        / growth["prior_revenue"].replace(0, np.nan) * 100
    ).round(2)

    growth = growth.reset_index()
    growth = growth[growth["prior_active"] >= min_prior_active]
    return growth.sort_values("active_growth_pct", ascending=False).head(top_n)


# --- Geo / choropleth helpers -------------------------------------------------

def load_geojson(city: str):
    """Load the neighbourhood geojson as a GeoDataFrame."""
    import geopandas as gpd
    if city == "barcelona":
        path = RAW_DIR / "Barcelona" / "Barcelona neighbourhoods.geojson"
    elif city == "london":
        path = RAW_DIR / "London" / "London neighbourhoods.geojson"
    else:
        raise ValueError(f"Unknown city: {city}")
    return gpd.read_file(path)


def normalise_london_borough(name) -> str:
    """Map an AirDNA `neighborhood` value to a borough name that matches the geojson.

    Two steps:
    1. Strip prefixes like 'London Borough of ' / 'Royal Borough of '.
    2. Roll up the 13 known Westminster sub-areas (Mayfair, Belgravia, …) into
       'Westminster' — otherwise that borough is empty on the choropleth and
       ~10% of LDN listings get hidden from borough-level analysis.
    """
    if pd.isna(name):
        return name
    stripped = name
    for prefix in LONDON_BOROUGH_PREFIXES:
        if stripped.startswith(prefix):
            stripped = stripped[len(prefix):].strip()
            break
    return LDN_SUBAREA_TO_BOROUGH.get(stripped, stripped)


def aggregate_to_london_boroughs(features: pd.DataFrame) -> pd.DataFrame:
    """Re-aggregate London features at borough level for borough choropleths."""
    ldn = features[features["city"] == "london"].copy()
    ldn["borough"] = ldn["neighborhood"].apply(normalise_london_borough)
    ldn = ldn[ldn["borough"].notna()]
    grouped = ldn.groupby("borough", dropna=True)
    out = pd.DataFrame({
        "str_density": grouped.size(),
        "entire_home_count": grouped["entire_home_flag"].sum().astype(int),
        "breach_count_90": grouped["breach_90_flag"].sum().astype(int),
        "avg_occupancy": grouped["l90d_occupancy"].mean(),
        "median_nightly_price": grouped["ttm_avg_rate"].median(),
        "total_revenue": grouped["ttm_revenue"].sum(),
    })
    out["entire_home_share"] = (out["entire_home_count"] / out["str_density"]).round(4)
    out["breach_rate_90"] = np.where(
        out["entire_home_count"] > 0,
        out["breach_count_90"] / out["entire_home_count"],
        np.nan,
    ).round(4)
    return out.reset_index()


def check_name_alignment(geo_names, kpi_keys) -> dict:
    """Compare geojson feature names against KPI geo_key values.

    Filters out non-string entries (NaN) before set comparison.
    """
    geo_set = {x for x in geo_names if isinstance(x, str)}
    kpi_set = {x for x in kpi_keys if isinstance(x, str)}
    return {
        "geo_features": len(geo_set),
        "kpi_geo_keys": len(kpi_set),
        "matched": len(geo_set & kpi_set),
        "match_rate": round(len(geo_set & kpi_set) / max(len(geo_set), 1), 4),
        "only_in_geojson": sorted(geo_set - kpi_set),
        "only_in_kpis": sorted(kpi_set - geo_set),
    }
