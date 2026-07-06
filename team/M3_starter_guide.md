# Member 3 — Starter Guide

You inherit a locked, validated knowledge layer. This document is a 5-minute on-ramp.

---

## Your job in one sentence

Add **`cluster_label`**, **`risk_priority_score`**, and a **price model** to the pipeline — then the knowledge layer is final and ready for Member 4's chatbot.

## What's already done for you

| File | What it gives you |
|---|---|
| `data/processed/neighbourhood_kpis.csv` | 560 rows × 25 numeric KPIs per (city, geo_key) — your clustering input |
| `data/processed/{barcelona\|london}/{city}_listings_features.csv` | 50 cols per listing — your price model input |
| `data/processed/data_dictionary.md` | Every column defined |
| `data/processed/subdivision_name_map.csv` | Name harmonisation for choropleths |
| `reports/eda_findings.md` | EDA narrative you can cite |
| `reports/golden_answers.json` | Ground-truth answers — your clustering output should be consistent with these |

## Five-minute on-ramp

```python
import sys, pandas as pd
from pathlib import Path
sys.path.insert(0, str(Path('.').resolve()))  # from repo root

# Load everything
from src.data_io import PROCESSED_DIR
kpis = pd.read_csv(PROCESSED_DIR / 'neighbourhood_kpis.csv')
bcn = pd.read_csv(PROCESSED_DIR / 'barcelona' / 'barcelona_listings_features.csv')
ldn = pd.read_csv(PROCESSED_DIR / 'london' / 'london_listings_features.csv')
features = pd.concat([bcn, ldn], ignore_index=True)

# Cluster on these columns (numeric, all 0–1 normalised or pre-scaled)
CLUSTER_FEATURES = [
    'str_density',
    'entire_home_share',
    'commercial_host_share',
    'multi_listing_host_share',
    'avg_occupancy',
    'breach_rate_90',
]
X = kpis[CLUSTER_FEATURES].fillna(0)
```

## Recommended approach

### 1. Clustering (the main ML showpiece)

- Try **KMeans (k=3)** first, labels: `saturated` / `emerging` / `low_impact`
- Set `random_state=42` so labels are reproducible
- Validate with **silhouette score** (target > 0.4)
- Inspect cluster centroids — they should match intuition:
  - `saturated` = high density + high entire-home share + high commercial host + high occupancy
  - `low_impact` = low across the board
  - `emerging` = somewhere in between, ideally with growth signal

### 2. Risk Priority Score

Suggested starting formula (refine as needed):

```python
weights = {
    'str_density':         0.20,  # how big is the STR footprint
    'entire_home_share':   0.30,  # displacement proxy — weight heavily
    'commercial_host_share': 0.20,  # commercialisation
    'breach_rate_90':      0.30,  # regulatory risk
}
# Min-max scale each column to 0–1 across the city before weighting
```

Save as `risk_priority_score` (0–100). Document weights in `reports/model_metrics.md`.

### 3. Price model

- Target: `ttm_avg_rate` at listing level
- Features: subdivision (one-hot), room_type, beds, baths, guests, host concentration flags
- Models: linear, random forest, gradient boosting
- Report **RMSE, MAE, R²** on a held-out test set
- KPMG slide requirement, not core to the chatbot

### 4. Policy simulation (already done at neighbourhood level — extend if needed)

`breach_count_90/60/30` and `reside_unregistered_count` are pre-computed per neighbourhood. If you want **custom** cap thresholds (e.g., 45 nights), use the listing-level `ttm_days_booked` column.

## Output you produce

Extend `neighbourhood_kpis.csv` (or save a new `knowledge_layer.csv`) with:

| New column | Type | Notes |
|---|---|---|
| `cluster_label` | string | `saturated` \| `emerging` \| `low_impact` |
| `cluster_distance` | float | distance to cluster centroid (confidence) |
| `risk_priority_score` | float 0–100 | weighted composite |

Also save:
- `models/price_model.joblib`
- `reports/model_metrics.md` (RMSE, MAE, R², silhouette, feature importance)
- `reports/figures/clustering/` (cluster maps, scatter plots)

## Gotchas to avoid

1. **Don't group by `geo_level`** — the KPI table is already deduplicated to one row per (city, geo_key). Member 2 spent time catching the 4 LDN dup rows.
2. **Apply `subdivision_name_map.csv`** before joining to the BCN geojson — 5 spelling mismatches will silently drop neighbourhoods from your maps.
3. **For LDN borough analysis**, use `london_borough_kpis.csv` (Westminster sub-areas already rolled up).
4. **RESIDE is BCN-only** — `reside_unregistered_count` for LDN is data context, not a regulatory breach. Don't use it in LDN policy simulation.
5. **Don't overwrite `neighbourhood_kpis.csv`** without re-running notebooks 04 → 06 — those are the validation gates.

## Importable building blocks

```python
from src.features import engineer_all_features    # if you re-build features
from src.kpis import compute_neighbourhood_kpis    # if you re-build KPIs
from src.eda import emerging_hotspots, load_geojson, normalise_london_borough
from src import golden                              # ground-truth answers
from src import dictionary as dct                   # data dictionary
```

## Hand-off to Member 4

When you're done, M4 expects:

- `cluster_label` populated in the knowledge layer
- `risk_priority_score` populated
- Updated `data_dictionary.md` documenting your new columns
- A short `reports/model_metrics.md` summarising your model performance

Update `team/04_chatbot_evaluation_responsibleai_member4.md` if the schema you produce differs from what M4 expected.
