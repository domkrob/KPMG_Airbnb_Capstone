# Member 2 — Execution Plan (Mohammed)

A concrete, step-by-step checklist for the Feature Engineering + EDA + draft Knowledge Layer phase.

Each step lists:
- **What** to do
- **Output** it produces
- **Why downstream needs it** — Member 3 (M3) clustering / price model / policy sim, or Member 4 (M4) chatbot

The bias of this plan: **anticipate everything M3 and M4 will need so they don't have to recompute or guess.**

---

## Phase A — Listing-level feature engineering

Goal: extend `*_listings_clean.csv` with every per-listing feature any downstream task will need. Save once, use everywhere.

### A1. Activity & occupancy flags

- `is_active_recent` — listing had `active=True` in any of the last 12 months from the monthly dataset
- `high_availability_flag` — true if `ttm_available_days + ttm_unavailable_days >= 270` (full-time STR proxy)
- `occupancy_band` — quartile of `l90d_occupancy` (low / med / high / very_high)

**For M3:** clustering features. **For M4:** chatbot can filter to "active listings only" when answering count questions.

### A2. Pricing & revenue features

- `price_band` — quartile bucket of `ttm_avg_rate` (city-relative)
- `revenue_band` — quartile bucket of `ttm_revenue`
- `revenue_per_active_day` — `ttm_revenue / max(ttm_days_booked, 1)` (sanity-check on rate)

**For M3:** price model target context, clustering inputs. **For M4:** "show me cheap/mid/premium subdivisions" queries.

### A3. Regulatory / policy flags (the centrepiece for Q7)

- `breach_90_flag` — entire-home AND `ttm_days_booked > 90` (London cap)
- `breach_60_flag` — entire-home AND `ttm_days_booked > 60`
- `breach_30_flag` — entire-home AND `ttm_days_booked > 30`
- `reside_unregistered_flag` (Barcelona only) — entire-home AND `has_registration == False` (RESIDE proxy)

**For M3:** these are exactly what the policy simulation aggregates. Pre-compute at listing level so M3 can `groupby(subdivision).sum()`. **For M4:** Q7 chatbot answers cite these directly.

### A4. Geographic fallback

- `geo_key` — `subdivision` if present, else `neighborhood`. Single key Member 3 and 4 can group by without missing rows.
- `geo_level` — `"subdivision"` or `"neighborhood"` indicator (so downstream knows the resolution)

**For M3:** clustering needs every listing to land in some group, otherwise ~10% of listings vanish from the analysis. **For M4:** answers can say "Whitechapel (subdivision)" vs "Lambeth (borough — finer breakdown unavailable)" honestly.

### A5. Host commercialisation refinement

- `host_revenue_total` — sum of `ttm_revenue` across all listings for each host
- `host_active_listings` — count of listings per host where `is_active_recent` is true
- `host_commercial_tier` — `casual` (1 listing) / `multi` (2–4) / `commercial` (5–9) / `super_commercial` (10+)

**For M3:** clearer commercialisation signal than the raw boolean flags. **For M4:** "which subdivisions are dominated by super-commercial hosts?"

**Deliverables:**
- `notebooks/03_feature_engineering.ipynb`
- `data/processed/barcelona/barcelona_listings_features.csv`
- `data/processed/london/london_listings_features.csv`

---

## Phase B — Neighbourhood-level KPI aggregation

Goal: produce the **one** neighbourhood table that Member 3 finalises and Member 4 queries.

### B1. Group by `geo_key` + `city` and compute

| KPI column | Definition |
|---|---|
| `str_density` | count of listings |
| `active_listings` | count where `is_active_recent` |
| `entire_home_count` | count where `entire_home_flag` |
| `entire_home_share` | `entire_home_count / str_density` |
| `commercial_host_share` | % listings from hosts with `host_commercial_tier in (commercial, super_commercial)` |
| `multi_listing_host_share` | % listings from `multi_listing_host == True` |
| `median_nightly_price` | median of `ttm_avg_rate` |
| `p25_price`, `p75_price` | quartiles |
| `avg_occupancy` | mean of `l90d_occupancy` |
| `total_revenue` | sum of `ttm_revenue` |
| `breach_count_90`, `breach_rate_90` | sum / share of `breach_90_flag` (of entire homes) |
| `breach_count_60`, `breach_rate_60` | same at 60 nights |
| `breach_count_30`, `breach_rate_30` | same at 30 nights |
| `reside_unregistered_count`, `reside_unregistered_share` | BCN only — RESIDE proxy |
| `professional_management_share` | of `professional_management_known == True` only (avoid the null-imputed False bias) |

### B2. Stack both cities

Output one CSV with a `city` column. M3 will add `cluster_label` and `risk_priority_score` columns on top.

**For M3:** clustering operates row-wise on this table. **For M4:** chatbot tool `get_neighbourhood_metrics(city, neighbourhood)` reads this table.

### B3. Subdivision name harmonisation (critical — easy to miss)

- Load both geojson files
- Extract the list of subdivision/neighbourhood names from each geojson
- Compare against the names in your KPI table
- Build a `subdivision_name_map.csv` if any spelling mismatches (e.g., "St James" vs "St. James's")
- Apply the map before saving the KPI table

**For M3:** choropleth maps fail silently when names don't match the geojson. **For M4:** users will type "Camden" — the table must contain the same string the geojson uses, so chatbot lookups succeed.

**Deliverables:**
- `data/processed/neighbourhood_kpis.csv`
- `data/processed/subdivision_name_map.csv` (if needed)

---

## Phase C — Exploratory Data Analysis

Goal: produce the visual + statistical findings that ground the chatbot's tone and give M4 the "facts to cite".

### C1. Citywide overview tables

- Total listings, unique hosts, unique subdivisions, active vs zombie split
- Median nightly price, median occupancy, total annual revenue (estimated)
- Side-by-side BCN vs LDN comparison table

### C2. Distributions

- Histograms: nightly price, occupancy, revenue per listing (one set per city)
- Boxplots: price by room type, price by entire-home flag
- Pareto chart: % of revenue captured by top X% of hosts

### C3. Rankings (top 10 / bottom 10 per KPI)

Save as tables — these become canonical "facts" the chatbot will recite.

- Top 10 subdivisions by STR density
- Top 10 by entire-home share
- Top 10 by commercial host share
- Top 10 by 90-night breach count (the "enforcement priority list")
- Top 10 by median nightly price

### C4. Choropleth maps

- One map per KPI per city (overlay KPI value on the geojson)
- Save as PNG + interactive HTML if time
- Use a consistent colour scale per metric for BCN vs LDN comparability

### C5. Time-series view (uses `*_monthly_metrics_clean.csv`)

- Monthly active-listings count per city
- Monthly average occupancy per city
- Per-subdivision growth: subdivisions whose listing count or occupancy grew most in the last 12 months → **emerging hotspots** (Q5)

### C6. Q6 BCN vs LDN comparison plots

- Side-by-side bars or paired dots for each KPI
- Highlight where the two cities diverge

**Deliverables:**
- `notebooks/04_eda_barcelona_london.ipynb`
- `reports/figures/eda/` — all PNGs
- `reports/figures/maps/` — all choropleths
- `reports/eda_findings.md` — a 1-page narrative of the top 10 findings, written so M4 can lift sentences for the chatbot's system prompt and disclaimers

---

## Phase D — Draft knowledge layer

Goal: hand M3 a table that's already ~80% of the final knowledge layer.

### D1. Final `data/processed/neighbourhood_kpis.csv`

- All columns from Phase B, sorted by city then geo_key
- No nulls in the metric columns (use 0 or document where 0 means "no data")
- Sanity check: row count = unique geo_keys × cities

### D2. Data dictionary

- `data/processed/data_dictionary.md` — every column in every processed file: name, type, unit, definition, example value, source
- Write once, link from each member's docs

**For M3:** they will spend zero time guessing column meanings. **For M4:** they'll lift definitions verbatim into the chatbot's tool docstrings.

---

## Phase E — Documentation & golden answers (for M4)

Goal: don't make M4 reverse-engineer your numbers for the evaluation set.

### E1. Golden-answer file

`reports/golden_answers.md` — answer each of the 7 canonical questions using the KPI table, with the exact numbers. Example:

> **Q1 — Highest STR concentration:** Eixample (Barcelona) with 4,210 listings; Westminster (London) with 1,890 listings.

M4 will use these as the evaluation ground truth (target ≥90% chatbot accuracy).

### E2. Caveats file

`reports/caveats.md` — every limitation the chatbot must surface:
- AirDNA sample (~14% of BCN universe, ~10% of LDN)
- Association ≠ causation
- Subdivision coverage gaps (`has_subdivision` flag)
- `professional_management` imputed False in ~54% of LDN
- Date range March 2021 – Feb 2026

M4 will paste these into the system prompt and per-answer footers.

---

## Phase F — Sanity & reproducibility

### F1. End-to-end reproducibility

- All three notebooks (03, 04 + any helpers) run top-to-bottom in the `kpmg-airbnb-capstone` env
- Set `random_state` everywhere a sample or shuffle is involved
- No hardcoded absolute paths — use `Path("..")` from `notebooks/` like Member 1

### F2. Pre-commit checks

- Notebook outputs cleared OR re-executed cleanly before committing (whichever team convention)
- `data/processed/` files match what the notebooks produce (delete + regen test)
- No `.env` or API keys committed

### F3. Repo housekeeping

- Update root `README.md` with:
  - Project one-liner
  - How to set up the conda env
  - How to run the cleaning + feature notebooks in order
  - Where to find the team work plan

---

## Final handover checklist (before passing to M3)

- [ ] `notebooks/03_feature_engineering.ipynb` runs clean
- [ ] `notebooks/04_eda_barcelona_london.ipynb` runs clean
- [ ] `barcelona_listings_features.csv` saved (with all Phase A columns)
- [ ] `london_listings_features.csv` saved (same schema as BCN)
- [ ] `neighbourhood_kpis.csv` saved (both cities stacked)
- [ ] `data_dictionary.md` complete
- [ ] `golden_answers.md` complete
- [ ] `caveats.md` complete
- [ ] `reports/figures/eda/` populated
- [ ] `reports/figures/maps/` populated
- [ ] `subdivision_name_map.csv` saved (if any mismatches found)
- [ ] Choropleth maps render correctly against the geojson (verified visually)
- [ ] All KPI columns documented in the data dictionary
- [ ] README updated with run instructions
- [ ] Brief M3 in person / in writing on what's in the table and what they still need to add

---

## Things that will make M3 struggle if you skip them

1. **Subdivision name mismatch with geojson** → maps silently break
2. **Different feature names for BCN vs LDN** → can't stack the cities for clustering
3. **No `geo_key` fallback** → ~10% of listings disappear from any aggregation
4. **Pre-aggregated KPIs that hide listing-level detail** → M3 can't recompute the policy sim at custom thresholds
5. **No data dictionary** → M3 spends hours guessing what columns mean

## Things that will make M4 struggle if you skip them

1. **No golden answers** → M4 has nothing to evaluate the chatbot against
2. **No caveats file** → M4 invents disclaimers or skips them, evaluators flag it
3. **Inconsistent subdivision spellings** → user queries fail lookup
4. **Numbers that don't match the EDA narrative** → chatbot quotes one number, slide deck says another, KPMG notices
