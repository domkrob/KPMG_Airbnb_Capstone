# Member 2 — Feature Engineering, EDA & Knowledge Layer

**Owner:** Mohammed
**Status:** ✅ **COMPLETE**
**Sequence:** 2 of 4
**Handoff:** Member 3 starts from `data/processed/neighbourhood_kpis.csv`. See `team/M3_starter_guide.md` for the 5-minute on-ramp.

---

## TL;DR for Member 3 (or any AI agent picking up this project)

> All five phases (A–E) of Member 2 work are complete and validated. The pipeline is one command (`python run_pipeline.py`). The knowledge layer is a single CSV at `data/processed/neighbourhood_kpis.csv` (560 rows × 25 cols, both cities stacked). Every column is documented in `data/processed/data_dictionary.md`. Ground-truth answers to the 7 canonical questions are in `reports/golden_answers.json`. **Start by reading `team/M3_starter_guide.md`.**

---

## 1. What Member 2 did

Member 2 took the cleaned datasets from Member 1 and built every analytical artefact Member 3 and Member 4 need before they touch the project.

### Phase summary

| Phase | What was built | Key output |
|---|---|---|
| **Audit of Member 1** | Found and fixed 3 cleaning bugs (lat/lon ×1e8, star_rating ×100, missing `has_subdivision`/`professional_management_known` flags) | Cleaning notebooks re-run, 34-col cleaned CSVs |
| **A — Feature engineering** | Added 16 listing-level features: activity flags, occupancy bands, price bands, 90/60/30-night breach flags, RESIDE proxy, geo_key fallback, host commercialisation tiers | `*_listings_features.csv` (50 cols, identical schema across both cities) |
| **B — Neighbourhood KPIs** | Aggregated to one row per (city, geo_key). 25 KPI columns. Dedup fix for 4 LDN areas appearing at both subdivision and neighborhood level | `neighbourhood_kpis.csv` (560 rows, 25 cols) |
| **C — EDA** | Built 7 distribution / time-series PNGs, 8 interactive HTML choropleths (4 BCN at subdivision level + 4 LDN at borough level), 16 ranking CSVs, narrative findings doc. Geojson alignment check applied (BCN 89%, LDN 94%) + name harmonisation map | `reports/figures/`, `reports/maps/`, `reports/tables/`, `eda_findings.md` |
| **D — Knowledge layer lock + dictionary** | 19-check validation gate (no nulls, schema parity, reconciliation, share bounds, no dup keys). Master data dictionary covering every column in every file | `data_dictionary.md`, `knowledge_layer_validation.csv` |
| **E — Golden answers + caveats** | Computed ground-truth answers to all 7 canonical questions. 9 disclaimers the chatbot must surface | `golden_answers.json/md`, `caveats.json/md` |

### Bonus deliverables added during review

- `README.md` at repo root (was 22 bytes — now a real onboarding doc)
- `run_pipeline.py` — one-command end-to-end runner with `--from`/`--to` flags
- `team/M3_starter_guide.md` — 5-min on-ramp for Member 3 with code snippets
- `team/M4_starter_guide.md` — 5-min on-ramp for Member 4 with tool function signatures
- `subdivision_name_map.csv` — name harmonisation for choropleth merges

---

## 2. Pipeline architecture

### File chain

```
data/raw/{Barcelona,London}/listings_*_CONVERT_FROM_PARQUET.csv
data/raw/{Barcelona,London}/*_neighbourhoods.geojson
                │
                │ Member 1 cleaning  (notebooks 01, 02)
                ▼
data/processed/{barcelona,london}/{city}_listings_clean.csv          ← 34 cols
data/processed/{barcelona,london}/{city}_monthly_metrics_clean.csv   ← 17 cols
                │
                │ Phase A — features  (notebook 03 + src/features.py)
                ▼
data/processed/{barcelona,london}/{city}_listings_features.csv       ← 50 cols
                │
                │ Phase B — KPI aggregation  (notebook 04 + src/kpis.py)
                ▼
data/processed/neighbourhood_kpis.csv                                ← 25 cols, 560 rows
                │
                │ Phase C — EDA  (notebook 05 + src/eda.py)
                ▼
reports/figures/, reports/maps/, reports/tables/, reports/eda_findings.md
                │
                │ Phase D — Lock + dictionary  (notebook 06 + src/dictionary.py)
                ▼
data/processed/data_dictionary.md, reports/knowledge_layer_validation.csv
                │
                │ Phase E — Golden answers  (notebook 07 + src/golden.py)
                ▼
reports/golden_answers.json/md, reports/caveats.json/md
```

### Code organisation

**Logic lives in `src/` — notebooks are thin orchestrators.** Each `src/` module exports pure functions that Member 3 can import directly.

```
src/
├── data_io.py       Path constants + load/save helpers
├── features.py      Phase A — listing-level feature engineering
├── kpis.py          Phase B — neighbourhood aggregation
├── eda.py           Phase C — EDA helpers + geojson/borough utilities
├── dictionary.py    Phase D — column specs + validation gate
└── golden.py        Phase E — canonical-question answers + caveats list
```

---

## 3. How to run the pipeline

### One-time setup

```powershell
conda env create -f environment.yml
conda activate kpmg-airbnb-capstone
```

### Run everything

```powershell
python run_pipeline.py
```

This executes notebooks 01 → 07 in order, takes ~5 minutes total.

### Run a specific range

```powershell
python run_pipeline.py --from 03           # start at Phase A
python run_pipeline.py --from 03 --to 05   # just Phase A, B, C
python run_pipeline.py --from 06           # just lock + golden answers
```

### Manual single-notebook run (for debugging)

```powershell
jupyter nbconvert --to notebook --execute --inplace notebooks/04_neighbourhood_kpis.ipynb
```

### What you'll know it worked

- `python run_pipeline.py` prints `Pipeline complete.` with no errors
- `reports/knowledge_layer_validation.csv` shows 19 PASS rows, 0 FAIL
- `data/processed/neighbourhood_kpis.csv` is 560 rows × 25 cols

---

## 4. Outputs catalog — every file Member 2 produced

### Data files

| Path | Rows | Cols | Purpose |
|---|---|---|---|
| `data/processed/barcelona/barcelona_listings_clean.csv` | 2,594 | 34 | M1 cleaning + Section 7.5 fixes |
| `data/processed/london/london_listings_clean.csv` | 9,643 | 34 | Same for London |
| `data/processed/barcelona/barcelona_monthly_metrics_clean.csv` | 88,821 | 17 | Listing × month panel (Mar 2021 – Feb 2026) |
| `data/processed/london/london_monthly_metrics_clean.csv` | 306,822 | 17 | Same for London |
| `data/processed/barcelona/barcelona_listings_features.csv` | 2,594 | 50 | + 16 Phase A engineered features |
| `data/processed/london/london_listings_features.csv` | 9,643 | 50 | Same for London (identical schema) |
| **`data/processed/neighbourhood_kpis.csv`** | **560** | **25** | **THE KNOWLEDGE LAYER — Member 3 starts here** |
| `data/processed/london_borough_kpis.csv` | 32 | 9 | Borough-level rollup (Westminster sub-areas merged) |
| `data/processed/subdivision_name_map.csv` | 18 | 4 | Apply with `df.replace()` before joining to geojson |

### Documentation

| Path | What it contains |
|---|---|
| `data/processed/data_dictionary.md` | **Master reference** — every column in every file with dtype, source, definition, unit, null %, example, notes (~46 KB) |
| `data/processed/dictionaries/*.csv` | Per-file CSV dictionaries (machine-readable, 6 files) |
| `data/processed/data_dictionary_neighbourhood_kpis.csv` | Standalone dictionary for the knowledge layer |

### Reports

| Path | What it contains |
|---|---|
| `reports/golden_answers.json` | **Ground truth for all 7 canonical questions** — M4 uses this as eval set |
| `reports/golden_answers.md` | Human-readable narrative of the answers |
| `reports/caveats.json` | **9 disclaimers** the chatbot must surface |
| `reports/caveats.md` | Human-readable caveats |
| `reports/eda_findings.md` | EDA narrative — M4 can lift sentences into system prompt |
| `reports/knowledge_layer_validation.csv` | 19 validation checks, all PASS |
| `reports/knowledge_layer_lock_report.md` | Lock summary |
| `reports/figures/` | 7 static PNGs (distributions, Pareto, time-series, choropleth) |
| `reports/maps/` | 8 interactive HTML choropleths (4 BCN + 4 LDN, on density / EH share / breach rate / price) |
| `reports/tables/` | 16 ranking CSVs (top-10 per metric per city) + summaries |

### Code

| Path | What it does |
|---|---|
| `src/*.py` | 6 pure-Python modules — see "Code organisation" above |
| `notebooks/01..07.ipynb` | Pipeline orchestrators (read top-down to see each phase's logic) |
| `run_pipeline.py` | Repo-root entry point — runs all notebooks in order |
| `environment.yml` | Conda env spec — Python 3.10+, pandas, geopandas, folium, streamlit, anthropic, etc. |

---

## 5. Headline numbers (so Member 3 knows what to expect)

### Citywide totals (AirDNA sample — NOT full market)

| | Barcelona | London |
|---|---|---|
| Total listings | 2,594 | 9,643 |
| Unique hosts | 1,637 | 7,312 |
| Subdivisions | 66 | 455 |
| Entire homes | 1,539 (59.3%) | 6,536 (67.8%) |
| Active in last 12 months | 1,655 | 5,967 |
| 90-night breaches | 642 | 1,485 |
| Total TTM revenue | €52.2M | £122.6M |
| Mean active occupancy | 0.21 | 0.14 |
| RESIDE unregistered entire homes | 421 (BCN-meaningful) | 2,572 (LDN context only) |

### Q7 — Policy simulation (the standout finding)

| Cap (nights/yr) | BCN listings impacted | LDN listings impacted |
|---|---|---|
| 90 | 611 | 1,482 |
| 60 | 689 | 1,863 |
| 30 | 751 | 2,260 |

Top BCN at 90-night cap: la Dreta de l'Eixample (95), la Sagrada Família (53), el Poble-sec (46)
Top LDN at 90-night cap: Whitechapel (44), Paddington (42), Westbourne Green (41)

---

## 6. Where Member 3 starts

**Read `team/M3_starter_guide.md` first.** Then:

1. Load `data/processed/neighbourhood_kpis.csv` — that's your input
2. Cluster on these columns (numeric, ready to feed KMeans):
   `str_density, entire_home_share, commercial_host_share, multi_listing_host_share, avg_occupancy, breach_rate_90`
3. Add three columns to the table:
   - `cluster_label` — `saturated` / `emerging` / `low_impact`
   - `cluster_distance` — distance to centroid (confidence)
   - `risk_priority_score` — weighted 0–100 composite
4. Save as either `data/processed/knowledge_layer.csv` (M4's expected name) or append in place
5. Build a separate price-prediction notebook with RMSE / MAE / R² on a held-out test set (KPMG slide requirement)
6. Document new columns in `data_dictionary.md` and run `python run_pipeline.py --from 06` to re-validate

### Importable building blocks

```python
from src.data_io import PROCESSED_DIR, load_clean_listings, load_monthly_metrics
from src.features import engineer_all_features              # if you re-build features
from src.kpis import compute_neighbourhood_kpis, kpi_data_dictionary
from src.eda import emerging_hotspots, load_geojson, normalise_london_borough
from src.dictionary import validate_knowledge_layer        # the gate you must keep passing
from src.golden import compute_all_answers, CAVEATS         # ground truth + disclaimers
```

---

## 7. Known caveats (not bugs — judgement calls Member 3 should know about)

1. **LDN median active occupancy = 0.0** even after filtering to active listings. The distribution is heavily zero-skewed. Use the mean (0.137 LDN, 0.21 BCN) for any narrative — not the median.
2. **Westminster rollup is a simplification.** AirDNA records 13 sub-areas (Mayfair, Belgravia, Knightsbridge, Paddington, etc.) at neighbourhood level. The borough KPI rolls them all to Westminster — but Belgravia and Knightsbridge actually straddle Westminster and Kensington & Chelsea. Documented in `subdivision_name_map.csv`.
3. **Q6 vs Q7 totals differ slightly.** Q6 (642 BCN, 1,485 LDN) sums all listings; Q7 (611, 1,482) sums neighbourhood rows. Gap = 31 BCN + 3 LDN listings with no subdivision/neighborhood (`geo_level == "unknown"`). Documented in Q7's `note` field. Pick one source and stick with it in any single chart or chatbot answer.

---

## 8. Pre-flight checklist for Member 3

Before starting:

- [ ] `conda activate kpmg-airbnb-capstone` works
- [ ] `python run_pipeline.py` runs end-to-end with `Pipeline complete.` at the end
- [ ] `reports/knowledge_layer_validation.csv` shows 19 PASS, 0 FAIL
- [ ] You have read `team/M3_starter_guide.md`
- [ ] You have skimmed `data/processed/data_dictionary.md` to know what each column means
- [ ] You have skimmed `reports/golden_answers.md` so you know what the chatbot's expected answers look like

---

## Reference docs (in order of usefulness for Member 3)

1. **`team/M3_starter_guide.md`** — your 5-minute on-ramp with code snippets and gotchas
2. **`data/processed/data_dictionary.md`** — every column defined
3. **`reports/golden_answers.md`** — ground-truth answers (don't break these)
4. **`reports/eda_findings.md`** — EDA narrative
5. **`README.md`** at repo root — high-level project overview
6. **`team/04_chatbot_evaluation_responsibleai_member4.md`** — what M4 expects from you
