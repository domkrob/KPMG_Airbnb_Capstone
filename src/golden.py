"""Ground-truth answers to the 7 canonical questions.

Member 4 uses this as the evaluation set for the chatbot:
- The chatbot must reproduce these numbers when asked the canonical questions
- Target: ≥90% accuracy on the answer set

Each function takes the analytical tables in and returns a structured dict the
chatbot can be evaluated against. The matching docstring is the question text.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

# Minimum neighbourhood size below which we don't trust shares/rates
MIN_DENSITY_FOR_SHARES = 30


# --- Item D: policy-advisor recommendations ---------------------------------
# Mentor feedback (June 2026): reframe answers as a "policy advisor" rather than
# pure descriptive Q&A. Each canonical question now carries:
#   - a ``policy_guidance`` field at the question level (one-liner the chatbot can
#     surface as the framing for the answer)
#   - a ``recommended_action`` field on each result row (per-neighbourhood
#     prescription the chatbot can lift into its response)
# These are additive. Existing fields are unchanged so the M4 evaluation harness
# does not break.

def _tier_for(kpis: pd.DataFrame, city: str, geo_key: str) -> str:
    """Look up tier_concentration_price for a (city, geo_key). Returns 'tier_3'
    if column or row missing (safe default — chatbot will simply not escalate)."""
    if "tier_concentration_price" not in kpis.columns:
        return "tier_3"
    row = kpis[(kpis["city"] == city) & (kpis["geo_key"] == geo_key)]
    if row.empty:
        return "tier_3"
    return str(row["tier_concentration_price"].iloc[0])


def _tier_phrase(tier: str) -> str:
    return {
        "tier_1": "Tier 1 — high concentration AND high price.",
        "tier_2": "Tier 2 — elevated on density or price.",
        "tier_3": "Tier 3 — lower combined risk.",
    }.get(tier, "Tier unclassified.")


# --- Q1 -----------------------------------------------------------------------

def q1_top_density(kpis: pd.DataFrame, top_n: int = 10) -> dict:
    """Q1 — Which neighbourhoods have the highest concentration of STRs?"""
    out = {"question": q1_top_density.__doc__.strip(),
           "method": f"Top {top_n} subdivisions per city by str_density.",
           "policy_guidance": ("These neighbourhoods host the largest STR footprints. "
                               "Allocate enforcement capacity here first — inspection "
                               "yield scales with concentration."),
           "answers": {}}
    for city in ("barcelona", "london"):
        df = kpis[kpis["city"] == city].nlargest(top_n, "str_density")
        rows = []
        for i, r in enumerate(df.to_dict("records")):
            tier = _tier_for(kpis, city, r["geo_key"])
            rows.append({
                "rank": i + 1,
                "geo_key": r["geo_key"],
                "str_density": int(r["str_density"]),
                "tier": tier,
                "recommended_action": (
                    f"Priority inspection target ({_tier_phrase(tier)}). "
                    f"{int(r['str_density'])} listings concentrated here — "
                    "size enforcement capacity to match."
                ),
            })
        out["answers"][city] = rows
    return out


# --- Q2 -----------------------------------------------------------------------

def q2_top_entire_home_share(
    kpis: pd.DataFrame,
    top_n: int = 10,
    min_density: int = MIN_DENSITY_FOR_SHARES,
) -> dict:
    """Q2 — Where is Airbnb most likely removing homes from the long-term residential market?"""
    out = {"question": q2_top_entire_home_share.__doc__.strip(),
           "method": (f"Top {top_n} subdivisions per city by entire_home_share, "
                      f"restricted to neighbourhoods with str_density >= {min_density}."),
           "policy_guidance": ("Entire-home share is the strongest displacement signal. "
                               "These neighbourhoods are the clearest candidates for "
                               "change-of-use planning restrictions to recover housing stock."),
           "answers": {}}
    for city in ("barcelona", "london"):
        df = (
            kpis[(kpis["city"] == city) & (kpis["str_density"] >= min_density)]
            .nlargest(top_n, "entire_home_share")
        )
        rows = []
        for i, r in enumerate(df.to_dict("records")):
            share_pct = round(float(r["entire_home_share"]) * 100, 1)
            rows.append({
                "rank": i + 1,
                "geo_key": r["geo_key"],
                "str_density": int(r["str_density"]),
                "entire_home_count": int(r["entire_home_count"]),
                "entire_home_share": round(float(r["entire_home_share"]), 3),
                "recommended_action": (
                    f"{share_pct}% of listings are entire homes — strong candidate for "
                    "change-of-use planning restriction. Recoverable housing units: "
                    f"up to {int(r['entire_home_count'])}."
                ),
            })
        out["answers"][city] = rows
    return out


# --- Q3 -----------------------------------------------------------------------

def q3_top_commercial_host_share(
    kpis: pd.DataFrame,
    top_n: int = 10,
    min_density: int = MIN_DENSITY_FOR_SHARES,
) -> dict:
    """Q3 — Which neighbourhoods are dominated by commercial/professional hosts?"""
    out = {"question": q3_top_commercial_host_share.__doc__.strip(),
           "method": (f"Top {top_n} subdivisions per city by commercial_host_share "
                      f"(commercial+super_commercial tiers, ≥5 listings/host), "
                      f"restricted to str_density >= {min_density}."),
           "policy_guidance": ("Concentration of commercial hosts (≥5 listings each) "
                               "signals professional letting operations rather than "
                               "casual home-sharing. Compliance audits here have the "
                               "highest yield per inspector-hour."),
           "answers": {}}
    for city in ("barcelona", "london"):
        df = (
            kpis[(kpis["city"] == city) & (kpis["str_density"] >= min_density)]
            .nlargest(top_n, "commercial_host_share")
        )
        rows = []
        for i, r in enumerate(df.to_dict("records")):
            comm_pct = round(float(r["commercial_host_share"]) * 100, 1)
            rows.append({
                "rank": i + 1,
                "geo_key": r["geo_key"],
                "str_density": int(r["str_density"]),
                "commercial_host_share": round(float(r["commercial_host_share"]), 3),
                "multi_listing_host_share": round(float(r["multi_listing_host_share"]), 3),
                "recommended_action": (
                    f"{comm_pct}% of listings owned by commercial-scale hosts. "
                    "Focus commercial-letting compliance audits and licensing checks here."
                ),
            })
        out["answers"][city] = rows
    return out


# --- Q4 -----------------------------------------------------------------------

def q4_density_price_intersection(
    kpis: pd.DataFrame,
    top_quartile: float = 0.75,
    min_density: int = MIN_DENSITY_FOR_SHARES,
) -> dict:
    """Q4 — In which neighbourhoods does high STR density coincide with high prices?"""
    out = {"question": q4_density_price_intersection.__doc__.strip(),
           "method": (f"Subdivisions in top quartile of BOTH str_density AND median_nightly_price "
                      f"per city (str_density >= {min_density}). These are the tier-1 areas — "
                      "see tier_concentration_price column for the full classification."),
           "policy_guidance": ("Tier-1 neighbourhoods carry both volume and revenue intensity. "
                               "Enforcement here delivers the largest market signal — high visibility "
                               "to the industry, high recovery of housing units, and strong public-"
                               "interest defensibility."),
           "answers": {},
           "correlations": {}}
    for city in ("barcelona", "london"):
        df = kpis[(kpis["city"] == city) & (kpis["str_density"] >= min_density)].copy()
        if df.empty:
            out["answers"][city] = []
            out["correlations"][city] = None
            continue
        d_thresh = df["str_density"].quantile(top_quartile)
        p_thresh = df["median_nightly_price"].quantile(top_quartile)
        intersect = (
            df[(df["str_density"] >= d_thresh)
               & (df["median_nightly_price"] >= p_thresh)]
            .sort_values(["str_density", "median_nightly_price"], ascending=False)
        )
        out["answers"][city] = [
            {
                "geo_key": r["geo_key"],
                "str_density": int(r["str_density"]),
                "median_nightly_price": round(float(r["median_nightly_price"]), 1),
                "tier": "tier_1",
                "recommended_action": (
                    f"Tier 1 priority. {int(r['str_density'])} listings at "
                    f"€/£{round(float(r['median_nightly_price']), 0):.0f} median nightly — "
                    "lead with this area in any phased enforcement rollout."
                ),
            }
            for r in intersect.to_dict("records")
        ]
        out["correlations"][city] = round(
            float(df["str_density"].corr(df["median_nightly_price"])), 3
        )
    return out


# --- Q5 -----------------------------------------------------------------------

def q5_saturated_vs_emerging(
    kpis: pd.DataFrame,
    features: pd.DataFrame,
    monthly: pd.DataFrame,
    top_n: int = 10,
    min_density: int = MIN_DENSITY_FOR_SHARES,
) -> dict:
    """Q5 — Which neighbourhoods are saturated, and which are emerging hotspots?"""
    from src.eda import emerging_hotspots

    out = {"question": q5_saturated_vs_emerging.__doc__.strip(),
           "method": ("Saturated = composite of high density + entire-home share + "
                      "commercial-host share + occupancy. "
                      "Emerging = top active-listing growth (recent 6 mo vs prior 6 mo). "
                      "Member 3 will replace the saturated heuristic with the proper KMeans cluster label."),
           "policy_guidance": ("Saturated areas need SUSTAINED presence to prevent backslide. "
                               "Emerging areas benefit from PRE-EMPTIVE action — intervention is "
                               "cheaper and more politically tractable before saturation sets in."),
           "answers": {"saturated": {}, "emerging": {}}}

    # Saturated — composite heuristic
    for city in ("barcelona", "london"):
        df = kpis[(kpis["city"] == city) & (kpis["str_density"] >= min_density)].copy()
        if df.empty:
            out["answers"]["saturated"][city] = []
            continue
        for col in ("str_density", "entire_home_share", "commercial_host_share", "avg_occupancy"):
            s = df[col].fillna(0).astype(float)
            df[f"_z_{col}"] = (s - s.mean()) / (s.std() if s.std() else 1)
        df["_saturation_score"] = df[[f"_z_{c}" for c in
            ("str_density", "entire_home_share", "commercial_host_share", "avg_occupancy")
        ]].sum(axis=1)
        top = df.nlargest(top_n, "_saturation_score")
        out["answers"]["saturated"][city] = [
            {
                "rank": i + 1,
                "geo_key": r["geo_key"],
                "str_density": int(r["str_density"]),
                "entire_home_share": round(float(r["entire_home_share"]), 3),
                "commercial_host_share": round(float(r["commercial_host_share"]), 3),
                "avg_occupancy": round(float(r["avg_occupancy"]), 3),
                "saturation_score": round(float(r["_saturation_score"]), 2),
                "recommended_action": (
                    "Saturated — maintain visible enforcement; monitor for displacement to "
                    "adjacent neighbourhoods; resist political pressure to relax existing rules."
                ),
            }
            for i, r in enumerate(top.to_dict("records"))
        ]

    # Emerging — reuse eda helper
    hot = emerging_hotspots(features, monthly, recent_months=6, prior_months=6,
                            top_n=top_n * 2, min_prior_active=5)
    for city in ("barcelona", "london"):
        sub = hot[hot["city"] == city].nlargest(top_n, "active_growth_pct")
        out["answers"]["emerging"][city] = [
            {
                "rank": i + 1,
                "geo_key": r["geo_key"],
                "prior_active": round(float(r["prior_active"]), 1),
                "recent_active": round(float(r["recent_active"]), 1),
                "active_growth_pct": round(float(r["active_growth_pct"]), 1),
                "recommended_action": (
                    f"Emerging hotspot (+{round(float(r['active_growth_pct']), 0):.0f}% active "
                    "listings in 6 months). Pre-emptive monitoring; consider "
                    "early intervention before saturation triggers stronger displacement."
                ),
            }
            for i, r in enumerate(sub.to_dict("records"))
        ]
    return out


# --- Q6 -----------------------------------------------------------------------

def q6_city_comparison(kpis: pd.DataFrame, features: pd.DataFrame) -> dict:
    """Q6 — How does STR pressure compare between Barcelona and London?"""
    out = {"question": q6_city_comparison.__doc__.strip(),
           "method": ("Side-by-side comparison of citywide totals and neighbourhood-level medians."),
           "policy_guidance": ("Barcelona's RESIDE phase-out is the stronger regulatory instrument "
                               "and is reflected in lower commercialisation per neighbourhood. London's "
                               "90-night cap is comparatively permissive — use this contrast when "
                               "sizing the political ambition of any proposed change."),
           "answers": {}}

    citywide = {}
    for city in ("barcelona", "london"):
        sub = features[features["city"] == city]
        active = sub[sub["is_active_recent"]]
        citywide[city] = {
            "total_listings": int(len(sub)),
            "unique_hosts": int(sub["host_id"].nunique()),
            "unique_subdivisions": int(sub["subdivision"].nunique()),
            "entire_homes": int(sub["entire_home_flag"].sum()),
            "entire_home_share": round(float(sub["entire_home_flag"].mean()), 3),
            "active_listings_last_12m": int(sub["is_active_recent"].sum()),
            "breach_90_total": int(sub["breach_90_flag"].sum()),
            "reside_unregistered_total": int(sub["reside_unregistered_flag"].sum()),
            "ttm_revenue_total": round(float(sub["ttm_revenue"].sum()), 0),
            "median_nightly_price": round(float(sub["ttm_avg_rate"].median()), 2),
            "median_occupancy_active": round(float(active["l90d_occupancy"].median()), 3)
                if len(active) else None,
            "mean_occupancy_active": round(float(active["l90d_occupancy"].mean()), 3)
                if len(active) else None,
        }
    out["answers"]["citywide_totals"] = citywide

    # Neighbourhood-level medians
    nh_medians = {}
    metrics = ["str_density", "entire_home_share", "commercial_host_share",
               "avg_occupancy", "median_nightly_price", "breach_rate_90"]
    for city in ("barcelona", "london"):
        sub = kpis[kpis["city"] == city]
        nh_medians[city] = {
            m: round(float(sub[m].median()), 3) if sub[m].notna().any() else None
            for m in metrics
        }
    out["answers"]["neighbourhood_medians"] = nh_medians
    return out


# --- Q7 -----------------------------------------------------------------------

def q7_policy_simulation(kpis: pd.DataFrame, caps: tuple = (90, 60, 30)) -> dict:
    """Q7 — If entire-home listings were capped at X nights/year, how many listings and which neighbourhoods would be affected?"""
    out = {"question": q7_policy_simulation.__doc__.strip(),
           "method": ("Sum of breach_count_{cap} per city (city totals), plus top-impacted "
                      "neighbourhoods per cap per city. RESIDE simulation: count of "
                      "reside_unregistered listings per Barcelona neighbourhood (entire homes "
                      "without registration on record)."),
           "policy_guidance": ("Q7 is the flagship policy decision. The cap-level choice should be "
                               "sized to enforcement capacity, not theoretical recovery — under-resourced "
                               "enforcement erodes regulatory credibility. Sequence rollout starting with "
                               "tier-1 neighbourhoods to maximise early signal."),
           "answers": {}}

    # City totals per cap. NOTE: sums over neighbourhoods exclude listings with
    # unknown geo (no subdivision and no neighborhood). Citywide totals from
    # listings_features may be slightly higher; the gap is documented below.
    totals = {}
    for city in ("barcelona", "london"):
        sub = kpis[kpis["city"] == city]
        totals[city] = {f"cap_{cap}_listings_impacted": int(sub[f"breach_count_{cap}"].sum())
                        for cap in caps}
        totals[city]["entire_homes_total"] = int(sub["entire_home_count"].sum())
        totals[city]["reside_unregistered_total"] = int(sub["reside_unregistered_count"].sum())
        totals[city]["note"] = (
            "Sum over neighbourhoods; excludes listings with no subdivision/neighborhood. "
            "City-wide totals from listings_features may differ by a few listings."
        )
    out["answers"]["city_totals"] = totals

    # Top impacted neighbourhoods per cap per city
    top_impacted = {}
    for city in ("barcelona", "london"):
        top_impacted[city] = {}
        for cap in caps:
            col = f"breach_count_{cap}"
            df = kpis[kpis["city"] == city].nlargest(10, col)
            top_impacted[city][f"cap_{cap}"] = [
                {"rank": i + 1,
                 "geo_key": r["geo_key"],
                 "listings_impacted": int(r[col]),
                 "entire_home_count": int(r["entire_home_count"]),
                 "breach_rate": round(float(r[f"breach_rate_{cap}"]), 3)
                 if pd.notna(r[f"breach_rate_{cap}"]) else None,
                 "tier": _tier_for(kpis, city, r["geo_key"]),
                 "recommended_action": (
                     f"At {cap}-night cap, {int(r[col])} listings recoverable here "
                     f"({_tier_phrase(_tier_for(kpis, city, r['geo_key']))}). "
                     "Sequence enforcement against this list, starting from tier 1."
                 )}
                for i, r in enumerate(df.to_dict("records"))
            ]
    out["answers"]["top_impacted_neighbourhoods"] = top_impacted

    # RESIDE — Barcelona-meaningful
    bcn = kpis[kpis["city"] == "barcelona"].nlargest(10, "reside_unregistered_count")
    out["answers"]["reside_top_neighbourhoods_barcelona"] = [
        {"rank": i + 1,
         "geo_key": r["geo_key"],
         "reside_unregistered_count": int(r["reside_unregistered_count"]),
         "entire_home_count": int(r["entire_home_count"]),
         "reside_share": round(float(r["reside_unregistered_share"]), 3)
         if pd.notna(r["reside_unregistered_share"]) else None,
         "recommended_action": (
             f"{int(r['reside_unregistered_count'])} entire-home listings without "
             "registration on record. Priority RESIDE compliance target — issue "
             "compliance notices and confirm phase-out timeline alignment."
         )}
        for i, r in enumerate(bcn.to_dict("records"))
    ]
    return out


# --- Orchestration ------------------------------------------------------------

def compute_all_answers(
    kpis: pd.DataFrame, features: pd.DataFrame, monthly: pd.DataFrame
) -> dict:
    """Compute all 7 canonical-question answers and return as one structured dict."""
    return {
        "Q1": q1_top_density(kpis),
        "Q2": q2_top_entire_home_share(kpis),
        "Q3": q3_top_commercial_host_share(kpis),
        "Q4": q4_density_price_intersection(kpis),
        "Q5": q5_saturated_vs_emerging(kpis, features, monthly),
        "Q6": q6_city_comparison(kpis, features),
        "Q7": q7_policy_simulation(kpis),
    }


# --- Caveats ------------------------------------------------------------------

CAVEATS = [
    {
        "key": "airdna_sample",
        "title": "AirDNA is a sample, not the full market",
        "body": ("All counts and shares reflect the AirDNA sample (~14% of Barcelona's "
                 "STR universe, ~10% of London's). Market-wide totals are larger. "
                 "Present numbers as 'in the AirDNA sample' for honesty."),
        "applies_to": "all"
    },
    {
        "key": "association_not_causation",
        "title": "Association, not causation",
        "body": ("High STR density correlates with rent pressure but does NOT prove "
                 "Airbnb causes rent rises. The tool surfaces risk indicators for "
                 "policy attention — it does not establish causality."),
        "applies_to": "all"
    },
    {
        "key": "subdivision_coverage",
        "title": "Subdivision coverage gaps",
        "body": ("9% of Barcelona and 12% of London listings have no subdivision in raw data. "
                 "These were rolled up to borough-level via the geo_key fallback (geo_level "
                 "indicates which resolution). Some neighbourhoods may be undercounted."),
        "applies_to": "all"
    },
    {
        "key": "professional_management_bias",
        "title": "Professional-management share is conservative",
        "body": ("~54% of London raw professional_management values were null. The KPI uses only "
                 "reported cases (professional_management_known == True). Treat the share as a "
                 "lower bound — true commercialisation may be higher."),
        "applies_to": "Q3"
    },
    {
        "key": "reside_meaning",
        "title": "RESIDE flag is Barcelona-only",
        "body": ("reside_unregistered_count counts entire homes without a registration on record. "
                 "This is regulatorily meaningful for Barcelona (RESIDE phase-out). For London the "
                 "same number is data context — not a policy breach. Do not present LDN "
                 "reside_unregistered as a regulatory violation."),
        "applies_to": "Q7"
    },
    {
        "key": "date_range",
        "title": "Time coverage",
        "body": ("Data spans March 2021 – February 2026. Emerging-hotspot growth compares "
                 "the most recent 6 months against the prior 6 months."),
        "applies_to": "Q5"
    },
    {
        "key": "ldn_geojson_resolution",
        "title": "London geojson is borough-level",
        "body": ("Choropleth maps for London are at borough level (33 boroughs). "
                 "Subdivision-level KPIs exist but cannot be mapped without a finer geojson."),
        "applies_to": "Q6"
    },
    {
        "key": "westminster_subareas",
        "title": "Westminster sub-areas in AirDNA",
        "body": ("AirDNA records 13 Westminster sub-areas (Mayfair, Belgravia, Paddington, "
                 "Marylebone, Pimlico etc.) at neighbourhood level rather than rolling them up "
                 "to Westminster. subdivision_name_map.csv documents the rollup. For Westminster "
                 "queries, sum the relevant rows."),
        "applies_to": "Q6"
    },
    {
        "key": "city_of_london_missing",
        "title": "City of London and Westminster missing from KPI",
        "body": ("The AirDNA sample contains zero listings in 'City of London' (the financial "
                 "district borough) and listings tagged 'Westminster' directly. Both appear in "
                 "the geojson but not in our KPI table. The Westminster sub-areas above are "
                 "where the Westminster activity actually lives."),
        "applies_to": "Q6"
    },
]
