"""Master data dictionary for all processed files.

Single source of truth for column definitions across the pipeline. Member 3
references this to know what columns mean; Member 4 lifts entries verbatim
into chatbot tool docstrings.

Public entry points:
- ``make_file_dictionary(df, spec, file_label)`` — augment hand-written spec
  with auto-detected dtype, null count, and example value from the actual file.
- ``assemble_markdown(file_blocks)`` — render the final master dictionary.
- ``validate_knowledge_layer(kpis, listings_features)`` — gate Phase D: confirm
  the knowledge layer is internally consistent and reconciles with Phase A.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd


# --- Column specs (hand-written) ----------------------------------------------
# Each row: (column, source, definition, unit, notes)

LISTINGS_CLEAN = [
    ("listing_id", "raw AirDNA", "Unique listing identifier.", "—", ""),
    ("host_id", "raw AirDNA", "Anonymous host identifier.", "—", ""),
    ("professional_management", "raw AirDNA", "Whether the listing is managed by a professional company.", "True/False/null", "~54% null in LDN raw — use professional_management_known to filter."),
    ("superhost", "raw AirDNA", "Whether the host has Airbnb Superhost status.", "True/False", ""),
    ("cohost", "raw AirDNA", "Whether the listing has a cohost.", "True/False/null", ""),
    ("neighborhood", "raw AirDNA", "District (BCN) or borough (LDN).", "string", "LDN values are prefixed e.g. 'London Borough of Camden'."),
    ("subdivision", "raw AirDNA", "Barrio (BCN) or local neighbourhood (LDN).", "string", "Null in 9% BCN / 12% LDN. Main key for neighbourhood analysis."),
    ("latitude", "raw AirDNA (rescaled)", "Listing latitude in decimal degrees.", "degrees", "Raw value was ×1e8; rescaled in cleaning Section 7.5."),
    ("longitude", "raw AirDNA (rescaled)", "Listing longitude in decimal degrees.", "degrees", "Raw value was ×1e8; rescaled in cleaning Section 7.5."),
    ("listing_type", "raw AirDNA", "Full listing-type label e.g. 'Entire rental unit'.", "string", ""),
    ("room_type", "raw AirDNA", "Normalised room type.", "entire_home|private_room|shared_room|hotel_room", ""),
    ("guests", "raw AirDNA", "Max guests advertised.", "count", ""),
    ("bedrooms", "raw AirDNA", "Bedrooms.", "count", ""),
    ("beds", "raw AirDNA", "Beds.", "count", ""),
    ("baths", "raw AirDNA", "Bathrooms.", "count", ""),
    ("num_reviews", "raw AirDNA", "Total reviews to date.", "count", ""),
    ("star_rating", "raw AirDNA (rescaled)", "Average star rating, 0–5.", "stars", "Raw value was ×100; rescaled in cleaning Section 7.5."),
    ("registration", "raw AirDNA", "Whether a registration/licence is on record.", "True/False/null", ""),
    ("ttm_revenue", "raw AirDNA", "Trailing-twelve-month revenue.", "EUR or GBP", ""),
    ("ttm_days_booked", "raw AirDNA", "Days booked in last 12 months.", "days", "Drives the 90-night breach flag."),
    ("ttm_avg_rate", "raw AirDNA", "TTM average nightly rate.", "EUR or GBP/night", ""),
    ("l90d_revenue", "raw AirDNA", "Last-90-day revenue.", "EUR or GBP", ""),
    ("l90d_occupancy", "raw AirDNA", "Last-90-day occupancy ratio.", "ratio 0–1", ""),
    ("l90d_revpar", "raw AirDNA", "Last-90-day revenue per available room.", "EUR or GBP", ""),
    ("months", "raw AirDNA", "Embedded JSON list of monthly performance.", "JSON string", "Exploded into *_monthly_metrics_clean.csv."),
    ("host_listing_count", "cleaning", "Number of listings owned by this host across the dataset.", "count", ""),
    ("multi_listing_host", "cleaning", "host_listing_count > 1.", "True/False", ""),
    ("host_5_plus_listings", "cleaning", "host_listing_count >= 5.", "True/False", ""),
    ("host_10_plus_listings", "cleaning", "host_listing_count >= 10.", "True/False", ""),
    ("entire_home_flag", "cleaning", "room_type == 'entire_home'.", "True/False", "Tightened to explicit equality after audit."),
    ("professional_management_flag", "cleaning", "professional_management coerced to bool, nulls -> False.", "True/False", "Use with professional_management_known to filter to reported-only."),
    ("has_registration", "cleaning", "registration is not null.", "True/False", ""),
    ("has_subdivision", "cleaning Section 7.5", "subdivision is not null.", "True/False", "Use to filter when aggregating at subdivision level."),
    ("professional_management_known", "cleaning Section 7.5", "professional_management was reported (not null).", "True/False", "Filter on this for honest professional-management share."),
]

MONTHLY_METRICS = [
    ("date", "raw AirDNA (months JSON)", "Month timestamp in milliseconds since epoch.", "epoch ms", ""),
    ("month_date", "cleaning", "Parsed month timestamp.", "datetime", ""),
    ("listing_id", "cleaning", "Listing identifier, joins back to *_listings_clean.csv.", "—", ""),
    ("available_days", "raw AirDNA", "Days the listing was available for booking that month.", "days", ""),
    ("unavailable_days", "raw AirDNA", "Days the listing was booked or blocked.", "days", ""),
    ("occupancy", "raw AirDNA", "Occupancy ratio for the month.", "ratio 0–1", ""),
    ("avg_daily_rate", "cleaning (renamed)", "Average daily rate for the month.", "EUR or GBP/night", "Renamed from rate_avg in raw."),
    ("native_rate_avg", "raw AirDNA", "Average daily rate in host's reporting currency.", "native ccy/night", ""),
    ("revenue", "raw AirDNA", "Revenue earned that month.", "EUR or GBP", ""),
    ("native_revenue", "raw AirDNA", "Revenue in host's reporting currency.", "native ccy", ""),
    ("active", "raw AirDNA", "Whether the listing was active that month.", "True/False", "Drives Phase A's is_active_recent flag."),
    ("booking_lead_time_avg", "raw AirDNA", "Average days from booking to check-in.", "days", "Frequently null."),
    ("length_of_stay_avg", "raw AirDNA", "Average length of stay.", "nights", "Frequently null."),
    ("booked_rate_avg", "raw AirDNA", "Average rate of booked nights only.", "EUR or GBP/night", "Null when no bookings."),
    ("native_booked_rate_avg", "raw AirDNA", "Booked rate in host's currency.", "native ccy/night", ""),
    ("revpar", "cleaning (renamed)", "Revenue per available room.", "EUR or GBP", "Renamed from rev_par in raw."),
    ("native_rev_par", "raw AirDNA", "RevPAR in host's currency.", "native ccy", ""),
]

LISTINGS_FEATURES = LISTINGS_CLEAN + [
    ("city", "Phase A", "City label.", "barcelona|london", ""),
    ("is_active_recent", "Phase A", "Listing had active=True in any of the last 12 months.", "True/False", "Use to filter to live listings."),
    ("high_intensity_flag", "Phase A", "ttm_days_booked >= 180 (half-year booking floor).", "True/False", "Full-time STR proxy."),
    ("occupancy_band", "Phase A", "Quartile bucket of l90d_occupancy.", "low|med|high|very_high|unknown", ""),
    ("price_band", "Phase A", "Quartile bucket of ttm_avg_rate.", "budget|mid|premium|luxury|unknown", ""),
    ("revenue_band", "Phase A", "Quartile bucket of ttm_revenue.", "low|med|high|very_high|unknown", ""),
    ("revenue_per_active_day", "Phase A", "ttm_revenue / ttm_days_booked.", "currency/day", "Null when no booked days."),
    ("breach_90_flag", "Phase A", "entire_home AND ttm_days_booked > 90.", "True/False", "London 90-night cap proxy."),
    ("breach_60_flag", "Phase A", "entire_home AND ttm_days_booked > 60.", "True/False", "Stretch policy scenario."),
    ("breach_30_flag", "Phase A", "entire_home AND ttm_days_booked > 30.", "True/False", "Aggressive policy scenario."),
    ("reside_unregistered_flag", "Phase A", "entire_home AND has_registration is False.", "True/False", "Regulatorily meaningful for Barcelona (RESIDE). Context-only for London."),
    ("geo_key", "Phase A", "subdivision when present, else neighborhood.", "string", "Single key for neighbourhood-level grouping. Avoids 9–12% loss from null subdivisions."),
    ("geo_level", "Phase A", "Resolution of geo_key.", "subdivision|neighborhood|unknown", "Drop 'unknown' before maps/aggregation."),
    ("host_revenue_total", "Phase A", "Sum of ttm_revenue across all listings of this host.", "currency", ""),
    ("host_active_listings", "Phase A", "Number of this host's listings that are is_active_recent.", "count", ""),
    ("host_commercial_tier", "Phase A", "Host scale class.", "casual|multi|commercial|super_commercial", "casual=1, multi=2-4, commercial=5-9, super_commercial=10+."),
]

NEIGHBOURHOOD_KPIS = [
    ("city", "Phase B", "City label.", "barcelona|london", ""),
    ("geo_key", "Phase B", "Neighbourhood key (subdivision or borough).", "string", "Join key for geojson choropleths after applying subdivision_name_map.csv."),
    ("geo_level", "Phase B", "Resolution of geo_key.", "subdivision|neighborhood", ""),
    ("str_density", "Phase B", "Total listings in the neighbourhood.", "count", "Q1 metric."),
    ("active_listings", "Phase B", "Listings active in last 12 months.", "count", ""),
    ("active_share", "Phase B", "active_listings / str_density.", "ratio 0–1", ""),
    ("entire_home_count", "Phase B", "Listings flagged entire-home.", "count", ""),
    ("entire_home_share", "Phase B", "entire_home_count / str_density.", "ratio 0–1", "Q2 — primary displacement proxy."),
    ("commercial_host_share", "Phase B", "Share of listings owned by commercial+super-commercial hosts (≥5 listings).", "ratio 0–1", "Q3 metric."),
    ("multi_listing_host_count", "Phase B", "Listings whose host owns ≥2 listings.", "count", ""),
    ("multi_listing_host_share", "Phase B", "multi_listing_host_count / str_density.", "ratio 0–1", ""),
    ("median_nightly_price", "Phase B", "Median TTM nightly rate.", "currency", "Q4 metric."),
    ("p25_price", "Phase B", "25th percentile nightly rate.", "currency", ""),
    ("p75_price", "Phase B", "75th percentile nightly rate.", "currency", ""),
    ("avg_occupancy", "Phase B", "Mean l90d_occupancy across listings in the neighbourhood.", "ratio 0–1", "Defaults to 0.0 (not NaN) when AirDNA has no occupancy data for any listing. Only affects tiny peripheral subdivisions; pair with tier_sample_adequate when reading."),
    ("total_revenue", "Phase B", "Sum of ttm_revenue across listings.", "currency", ""),
    ("breach_count_90", "Phase B", "Entire homes with ttm_days_booked > 90.", "count", "Q7 — listings impacted at a 90-night cap."),
    ("breach_count_60", "Phase B", "Entire homes with ttm_days_booked > 60.", "count", "Q7 stretch scenario."),
    ("breach_count_30", "Phase B", "Entire homes with ttm_days_booked > 30.", "count", "Q7 aggressive scenario."),
    ("breach_rate_90", "Phase B", "breach_count_90 / entire_home_count.", "ratio 0–1", ""),
    ("breach_rate_60", "Phase B", "breach_count_60 / entire_home_count.", "ratio 0–1", ""),
    ("breach_rate_30", "Phase B", "breach_count_30 / entire_home_count.", "ratio 0–1", ""),
    ("reside_unregistered_count", "Phase B", "Entire homes without a registration on record.", "count", "Q7 RESIDE simulation (BCN-meaningful)."),
    ("reside_unregistered_share", "Phase B", "reside_unregistered_count / entire_home_count.", "ratio 0–1", "BCN-meaningful only."),
    ("professional_management_share", "Phase B", "Share of professionally-managed listings, computed only over reported cases.", "ratio 0–1", "Avoids null-imputation bias."),
    ("tier_concentration_price", "Phase B (mentor update)", "Risk tier combining concentration and price: tier_1 (top quartile in both str_density AND median_nightly_price), tier_2 (top quartile in one), tier_3 (neither). Thresholds computed per city.", "tier_1|tier_2|tier_3", "Drives the 'policy advisor' framing. Reads in pair with tier_sample_adequate."),
    ("tier_sample_adequate", "Phase B (mentor update)", "True if str_density >= 5 — i.e., enough listings for the tier label to be meaningful.", "True/False", "Chatbot should caveat tier conclusions for any row where this is False."),
]

LONDON_BOROUGH_KPIS = [
    ("borough", "Phase C", "London borough name (normalised to match geojson).", "string", "Stripped of borough prefixes AND Westminster sub-areas (Mayfair, Belgravia, …) are rolled up into Westminster."),
    ("str_density", "Phase C", "Listings in borough.", "count", ""),
    ("entire_home_count", "Phase C", "Entire-home listings in borough.", "count", ""),
    ("breach_count_90", "Phase C", "Entire homes > 90 nights in borough.", "count", ""),
    ("avg_occupancy", "Phase C", "Mean l90d_occupancy in borough.", "ratio 0–1", ""),
    ("median_nightly_price", "Phase C", "Median TTM nightly rate in borough.", "GBP", ""),
    ("total_revenue", "Phase C", "Sum of TTM revenue in borough.", "GBP", ""),
    ("entire_home_share", "Phase C", "entire_home_count / str_density.", "ratio 0–1", ""),
    ("breach_rate_90", "Phase C", "breach_count_90 / entire_home_count.", "ratio 0–1", ""),
]

SUBDIVISION_NAME_MAP = [
    ("city", "Phase C", "Which city the row applies to.", "barcelona|london", ""),
    ("airdna_name", "Phase C", "Name as it appears in our AirDNA-derived data.", "string", ""),
    ("geojson_name", "Phase C", "Name as it appears in the Inside Airbnb geojson.", "string", "Apply this rename before joining to the geojson."),
    ("notes", "Phase C", "Why the rename is needed.", "string", ""),
]


# --- Build dictionary tables --------------------------------------------------

def make_file_dictionary(
    df: pd.DataFrame, spec: list[tuple], file_label: str
) -> pd.DataFrame:
    """Augment a hand-written column spec with auto-detected dtype, null %, and example."""
    rows = []
    for col, source, defn, unit, notes in spec:
        if col not in df.columns:
            continue
        series = df[col]
        n_null = int(series.isna().sum())
        null_pct = round(100 * n_null / max(len(series), 1), 1)
        non_null = series.dropna()
        example = non_null.iloc[0] if len(non_null) else ""
        if isinstance(example, float):
            example = round(example, 3)
        rows.append({
            "column": col,
            "dtype": str(series.dtype),
            "source": source,
            "definition": defn,
            "unit": unit,
            "null_pct": null_pct,
            "example": str(example)[:60],
            "notes": notes,
        })
    return pd.DataFrame(rows)


# --- Markdown rendering -------------------------------------------------------

@dataclass
class FileBlock:
    title: str
    path: str
    unit_of_analysis: str
    rows: int
    notes: str
    dictionary: pd.DataFrame


def assemble_markdown(blocks: Iterable[FileBlock], generated_on: str) -> str:
    lines: list[str] = []
    lines.append("# Data Dictionary — Urban Rental Intelligence Copilot")
    lines.append("")
    lines.append(f"_Generated on {generated_on}._")
    lines.append("")
    lines.append(
        "Single source of truth for every column in every file under "
        "`data/processed/`. Member 3 references this to know what to feed the "
        "clustering and price models. Member 4 lifts column definitions "
        "verbatim into chatbot tool docstrings."
    )
    lines.append("")
    lines.append("## Files in this dictionary")
    lines.append("")
    lines.append("| File | Unit of analysis | Rows | Notes |")
    lines.append("|---|---|---|---|")
    for b in blocks:
        lines.append(f"| `{b.path}` | {b.unit_of_analysis} | {b.rows:,} | {b.notes} |")
    lines.append("")

    for b in blocks:
        lines.append(f"## `{b.path}`")
        lines.append("")
        lines.append(f"**Unit of analysis:** {b.unit_of_analysis}  ")
        lines.append(f"**Rows:** {b.rows:,}  ")
        if b.notes:
            lines.append(f"**Notes:** {b.notes}")
        lines.append("")
        lines.append(b.dictionary.to_markdown(index=False))
        lines.append("")

    return "\n".join(lines)


# --- Knowledge layer validation ----------------------------------------------

def validate_knowledge_layer(
    kpis: pd.DataFrame, features: pd.DataFrame
) -> pd.DataFrame:
    """Run a battery of checks on the locked knowledge layer.

    Returns a DataFrame of (check, status, detail). Empty 'detail' on PASS.
    Any FAIL means the table is not safe to hand off.
    """
    checks: list[dict] = []

    def add(name: str, ok: bool, detail: str = "") -> None:
        checks.append({"check": name, "status": "PASS" if ok else "FAIL", "detail": detail})

    # 1. Cities present
    cities = sorted(kpis["city"].unique())
    add("both cities present", set(cities) == {"barcelona", "london"}, f"cities={cities}")

    # 2. Critical columns no nulls.
    # Counts are always defined; the str_density denominator is always positive
    # in the KPI table (otherwise the row would not exist), so every share
    # computed against it must also be non-null. avg_occupancy is filled to 0
    # in compute_neighbourhood_kpis so it must never be null here.
    critical = [
        "str_density", "entire_home_count",
        "breach_count_90", "breach_count_60", "breach_count_30",
        "entire_home_share", "commercial_host_share",
        "multi_listing_host_share", "active_share",
        "avg_occupancy",
    ]
    null_cols = [c for c in critical if c in kpis.columns and kpis[c].isna().any()]
    add("no nulls in critical columns", not null_cols, f"nulls in: {null_cols}")

    # 3. Schema parity across cities
    bcn_cols = set(kpis[kpis["city"] == "barcelona"].dropna(axis=1, how="all").columns)
    ldn_cols = set(kpis[kpis["city"] == "london"].dropna(axis=1, how="all").columns)
    add("schema parity (BCN vs LDN)", bcn_cols == ldn_cols,
        f"diff: {bcn_cols ^ ldn_cols}")

    # 4. Density reconciles with listings_features (excluding unknown geo)
    for city in ("barcelona", "london"):
        sub = features[(features["city"] == city) & (features["geo_level"] != "unknown")]
        kpi_sum = int(kpis.loc[kpis["city"] == city, "str_density"].sum())
        add(f"density reconciles ({city})", len(sub) == kpi_sum,
            f"features={len(sub)}, kpis_sum={kpi_sum}")

    # 5. Entire-home reconciles
    for city in ("barcelona", "london"):
        sub = features[(features["city"] == city) & (features["geo_level"] != "unknown")]
        eh_features = int(sub["entire_home_flag"].sum())
        eh_kpis = int(kpis.loc[kpis["city"] == city, "entire_home_count"].sum())
        add(f"entire_home reconciles ({city})", eh_features == eh_kpis,
            f"features={eh_features}, kpis_sum={eh_kpis}")

    # 6. Breach 90 reconciles
    for city in ("barcelona", "london"):
        sub = features[(features["city"] == city) & (features["geo_level"] != "unknown")]
        b90_features = int(sub["breach_90_flag"].sum())
        b90_kpis = int(kpis.loc[kpis["city"] == city, "breach_count_90"].sum())
        add(f"breach_90 reconciles ({city})", b90_features == b90_kpis,
            f"features={b90_features}, kpis_sum={b90_kpis}")

    # 7. Shares in [0, 1]
    share_cols = [c for c in kpis.columns if c.endswith("_share") or c.endswith("_rate_90") or c.endswith("_rate_60") or c.endswith("_rate_30")]
    for c in share_cols:
        s = kpis[c].dropna()
        ok = ((s >= 0) & (s <= 1)).all() if len(s) else True
        add(f"{c} in [0,1]", ok, "" if ok else f"min={s.min()}, max={s.max()}")

    # 8. No duplicate (city, geo_key) rows
    dup = kpis.duplicated(["city", "geo_key"]).sum()
    add("no duplicate (city, geo_key)", dup == 0, f"duplicates={dup}")

    return pd.DataFrame(checks)
