"""Listing-level feature engineering for the Urban Rental Intelligence Copilot.

Each function takes a listings DataFrame (and optionally a monthly DataFrame),
returns the same DataFrame with new columns added. Functions are pure: no IO,
no side effects, no global state — safe to call from notebooks, tests, or
downstream pipelines.

Schema entering: the output of Member 1's cleaning notebooks (Section 7.5
applied — lat/lon and star_rating rescaled, geo flags added).

Public entry point: ``engineer_all_features(listings, monthly, city)``.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

# --- A1. Activity & occupancy --------------------------------------------------

def add_activity_flags(listings: pd.DataFrame, monthly: pd.DataFrame) -> pd.DataFrame:
    """Add ``is_active_recent`` and ``high_intensity_flag``.

    - ``is_active_recent``: True if the listing had at least one ``active`` month
      in the trailing 12 months of the monthly panel.
    - ``high_intensity_flag``: True if ``ttm_days_booked >= 180`` — a half-year
      booking floor that proxies "de facto full-time STR".
    """
    cutoff = monthly["month_date"].max() - pd.DateOffset(months=12)
    recent = monthly.loc[monthly["month_date"] >= cutoff, ["listing_id", "active"]]
    active_recent = (
        recent.groupby("listing_id")["active"].any().rename("is_active_recent")
    )

    listings = listings.merge(
        active_recent, left_on="listing_id", right_index=True, how="left"
    )
    listings["is_active_recent"] = listings["is_active_recent"].fillna(False).astype(bool)

    listings["high_intensity_flag"] = (
        listings["ttm_days_booked"].fillna(0).astype(float) >= 180
    )
    return listings


def _safe_qcut(series: pd.Series, q: int, labels: list[str]) -> pd.Series:
    """qcut that tolerates duplicate bin edges.

    When the input has many ties (e.g. lots of zeros in revenue/occupancy),
    duplicate quantile edges get dropped, which reduces the number of bins.
    We trim the label list to match. If the input has fewer than 2 unique
    non-null values, returns all-NaN.
    """
    non_null = series.dropna()
    if non_null.empty or non_null.nunique() < 2:
        return pd.Series([np.nan] * len(series), index=series.index, dtype="object")

    _, edges = pd.qcut(non_null, q=q, retbins=True, duplicates="drop")
    n_bins = len(edges) - 1
    if n_bins < 1:
        return pd.Series([np.nan] * len(series), index=series.index, dtype="object")

    return pd.qcut(series, q=q, labels=labels[:n_bins], duplicates="drop")


def add_occupancy_band(listings: pd.DataFrame) -> pd.DataFrame:
    """Add ``occupancy_band`` (quartile of ``l90d_occupancy``)."""
    occ = listings["l90d_occupancy"]
    bands = _safe_qcut(occ, 4, ["low", "med", "high", "very_high"])
    listings["occupancy_band"] = (
        bands.astype(object).where(occ.notna(), "unknown")
    )
    return listings


# --- A2. Pricing & revenue ----------------------------------------------------

def add_pricing_features(listings: pd.DataFrame) -> pd.DataFrame:
    """Add ``price_band``, ``revenue_band`` and ``revenue_per_active_day``."""
    price = listings["ttm_avg_rate"]
    price_bands = _safe_qcut(price, 4, ["budget", "mid", "premium", "luxury"])
    listings["price_band"] = (
        price_bands.astype(object).where(price.notna(), "unknown")
    )

    rev = listings["ttm_revenue"]
    rev_bands = _safe_qcut(rev, 4, ["low", "med", "high", "very_high"])
    listings["revenue_band"] = (
        rev_bands.astype(object).where(rev.notna(), "unknown")
    )

    days = listings["ttm_days_booked"].astype(float)
    listings["revenue_per_active_day"] = (
        listings["ttm_revenue"].astype(float) / days.replace(0, np.nan)
    )
    return listings


# --- A3. Regulatory / policy flags --------------------------------------------

def add_breach_flags(listings: pd.DataFrame) -> pd.DataFrame:
    """Add 90/60/30-night breach flags and the Barcelona RESIDE flag.

    Breach flags target entire homes only — both London's 90-night cap and
    Barcelona's RESIDE phase-out apply to entire-home tourist lets.
    """
    eh = listings["entire_home_flag"].astype(bool)
    days = listings["ttm_days_booked"].fillna(0).astype(float)

    listings["breach_90_flag"] = eh & (days > 90)
    listings["breach_60_flag"] = eh & (days > 60)
    listings["breach_30_flag"] = eh & (days > 30)

    # RESIDE proxy: entire-home + no registration on record.
    # has_registration is already a boolean from Member 1's cleaning.
    listings["reside_unregistered_flag"] = eh & (~listings["has_registration"].astype(bool))
    return listings


# --- A4. Geographic fallback --------------------------------------------------

def add_geo_key(listings: pd.DataFrame) -> pd.DataFrame:
    """Add ``geo_key`` (subdivision when present, else neighborhood) and ``geo_level``.

    Prevents ~10% of listings (those with null subdivision) from silently
    dropping out of neighbourhood-level aggregations.
    """
    sub_present = listings["subdivision"].notna()
    nbh_present = listings["neighborhood"].notna()

    listings["geo_key"] = listings["subdivision"].fillna(listings["neighborhood"])
    listings["geo_level"] = np.where(
        sub_present,
        "subdivision",
        np.where(nbh_present, "neighborhood", "unknown"),
    )
    return listings


# --- A5. Host commercialisation ----------------------------------------------

def add_host_commercialisation(listings: pd.DataFrame) -> pd.DataFrame:
    """Add host-level commercialisation features.

    - ``host_revenue_total``: total ttm_revenue across all of a host's listings
    - ``host_active_listings``: how many of a host's listings are active_recent
    - ``host_commercial_tier``: casual / multi / commercial / super_commercial
    """
    host_rev = (
        listings.groupby("host_id")["ttm_revenue"].sum().rename("host_revenue_total")
    )
    listings = listings.merge(
        host_rev, left_on="host_id", right_index=True, how="left"
    )

    host_active = (
        listings.loc[listings["is_active_recent"]]
        .groupby("host_id")
        .size()
        .rename("host_active_listings")
    )
    listings = listings.merge(
        host_active, left_on="host_id", right_index=True, how="left"
    )
    listings["host_active_listings"] = (
        listings["host_active_listings"].fillna(0).astype(int)
    )

    n = listings["host_listing_count"].astype(int)
    listings["host_commercial_tier"] = np.select(
        [n >= 10, n >= 5, n >= 2],
        ["super_commercial", "commercial", "multi"],
        default="casual",
    )
    return listings


# --- Orchestration ------------------------------------------------------------

PIPELINE = [
    add_activity_flags,    # needs monthly
    add_occupancy_band,
    add_pricing_features,
    add_breach_flags,
    add_geo_key,
    add_host_commercialisation,
]


def engineer_all_features(
    listings: pd.DataFrame, monthly: pd.DataFrame, city: str
) -> pd.DataFrame:
    """Run the full Phase A feature pipeline on a single city.

    Returns a new DataFrame with all engineered columns added and a ``city``
    column at the front. Does not mutate the input.
    """
    out = listings.copy()
    out.insert(0, "city", city.lower())

    out = add_activity_flags(out, monthly)
    out = add_occupancy_band(out)
    out = add_pricing_features(out)
    out = add_breach_flags(out)
    out = add_geo_key(out)
    out = add_host_commercialisation(out)
    return out
