# Knowledge Layer — Lock Report
_Locked on 2026-06-11_

## Status

All 19 validation checks **PASS**.

## Files Member 3 inherits

| File | Rows | Cols | Purpose |
|---|---|---|---|
| `data/processed/neighbourhood_kpis.csv` | 560 | 27 | Knowledge layer — cluster on this |
| `data/processed/barcelona/barcelona_listings_features.csv` | 2,594 | 50 | Per-listing features for the price model |
| `data/processed/london/london_listings_features.csv` | 9,643 | 50 | Same, for London |
| `data/processed/data_dictionary.md` | — | — | Column definitions for every file |
| `data/processed/dictionaries/` | — | — | Per-file CSV dictionaries (for chatbot tooling) |
| `data/processed/subdivision_name_map.csv` | 18 | — | Apply before joining geojson |

## What Member 3 still needs to add

- `cluster_label` per (city, geo_key) — saturated / emerging / low-impact
- `risk_priority_score` — weighted 0–100 composite
- Optionally widen the policy simulation columns at custom cap thresholds

## Reproducibility

Run notebooks 01 → 06 in order in the `kpmg-airbnb-capstone` env to regenerate everything.
