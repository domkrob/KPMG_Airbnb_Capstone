# Member 3 — Model Metrics

**Owner:** Member 3 · **Phase 3 (ML) + Phase 4 (final knowledge layer)**
**Inputs:** `data/processed/neighbourhood_kpis.csv` (560×27), `data/processed/{city}/{city}_listings_clean.csv`
**Outputs:** `data/processed/knowledge_layer.csv` (560×35), `models/price_model.joblib`, figures under `reports/figures/clustering/`

---

## 1. Neighbourhood clustering (KMeans)

- **Algorithm:** KMeans, `k=3`, `random_state=42`, `n_init=10`, on **StandardScaler**-transformed features (a count and several shares share the matrix, so scaling is mandatory — raw `str_density` would otherwise dominate).
- **Features:** `str_density`, `entire_home_share`, `commercial_host_share`, `multi_listing_host_share`, `avg_occupancy`, `breach_rate_90`
- **Scaling scope:** pooled across both cities, so a *saturated* profile means the same thing in Barcelona and London (supports the Q6 cross-city comparison).
- **`breach_rate_90` NaN** (neighbourhoods with zero entire homes → rate undefined) is read as **0 pressure** for clustering geometry only.

### Cluster validity — silhouette across k

k=2: 0.2631 · k=3: 0.2715 · k=4: 0.2368 · k=5: 0.248 · k=6: 0.2291

**k=3 is the best-separated solution in the sweep** and is the value the project requires for the three-label scheme (`saturated` / `emerging` / `low_impact`). The absolute silhouette (**0.2715**) is moderate — expected for socio-economic neighbourhood data with continuous gradients rather than crisp gaps. Cluster *interpretability* (below) is strong and the labels reproduce exactly across reruns because `random_state` is fixed and labels are assigned by centroid pressure rank (not by KMeans' arbitrary cluster ids).

### Cluster centroids (raw units, ascending pressure)

| cluster | n | str_density | entire_home_share | commercial_host_share | multi_host_share | avg_occupancy | breach_rate_90 | pressure |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| saturated | 189 | 46.069 | 0.719 | 0.194 | 0.467 | 0.118 | 0.243 | 0.79 |
| low_impact | 293 | 9.218 | 0.469 | 0.019 | 0.118 | 0.052 | 0.084 | 0.011 |
| emerging | 78 | 6.987 | 0.642 | 0.032 | 0.217 | 0.242 | 0.614 | 0.521 |

- **saturated** — large footprint, high entire-home + commercial + multi-listing-host shares. The enforcement-priority cluster.
- **emerging** — small footprint but elevated breach rate and occupancy: high pressure *per listing*, not yet commercialised at scale. The "watch list".
- **low_impact** — low across the board.

`cluster_distance` (euclidean distance to the assigned centroid in scaled space) is published per row as a confidence proxy: lower = more typical of its cluster.

### Cluster composition by city

| city | saturated | emerging | low_impact |
| --- | --- | --- | --- |
| barcelona | 35 | 12 | 19 |
| london | 154 | 66 | 274 |


### Cross-check against Member 2's rule-based tiers

Member 2's `tier_concentration_price` (top-quartile in density AND price) is an *independent*, rule-based signal. Our data-driven clusters should corroborate it:

| tier | saturated | emerging | low_impact |
| --- | --- | --- | --- |
| tier_1 | 37 | 0 | 0 |
| tier_2 | 73 | 9 | 26 |
| tier_3 | 79 | 69 | 267 |


**All 37 tier-1 neighbourhoods land in `saturated`** — independent confirmation the clustering captures the intended STR-pressure structure.

---

## 2. Risk Priority Score (0–100)

Composite per (city, neighbourhood), published as `risk_priority_score`.

- **Weights:** str_density 0.2; entire_home_share 0.3; commercial_host_share 0.2; breach_rate_90 0.3
- **Per-city min-max:** each component is scaled within its city before weighting (BCN and LDN absolute scales differ), so the score ranks neighbourhoods *within* a city.
- **Sample-confidence shrinkage:** the weighted composite is multiplied by `str_density / (str_density + 5)`, then rescaled so each city's worst neighbourhood = 100. Without this, single-listing peripheral areas (`entire_home_share`=1.0, `breach_rate_90`=1.0 on n=1) would top the ranking on noise. The threshold mirrors Member 2's `tier_sample_adequate` (density ≥ 5). Consumers ranking priorities should still prefer `tier_sample_adequate == True` rows.
- **Validation:** post-shrinkage top priorities are the expected central, tourist-saturated, premium areas — BCN: la Dreta de l'Eixample (100), el Poble-sec, la Sagrada Família; LDN: Westbourne Green (100), Paddington, Earl's Court, Marylebone, Whitechapel. These match Member 2's tier-1 list and the Q7 enforcement-priority neighbourhoods.

---

## 3. Price prediction model (KPMG slide requirement)

Listing-level regression. **Not consumed by the chatbot** — a standalone model + metrics artefact.

- **Target:** `ttm_avg_rate` (right-skewed → modelled as `log1p`, metrics inverted to currency units).
- **Features:** beds, bedrooms, baths, guests, host_listing_count; entire-home / multi-listing / 5+ / 10+ / professional-management / registration flags; room_type, listing_type, city, neighborhood (one-hot, rare levels grouped).
- **Split:** 80/20 hold-out, `random_state=42`, plus 5-fold CV on the train fold.
- **Training data in this run:** barcelona (1460 train / 365 test rows). The module globs whatever `*_listings_clean.csv` files are present, so a **full local clone (Barcelona + London) retrains the combined model with one command** — no code change.

### Held-out metrics (original currency units)

| model | RMSE | MAE | R² | CV R² mean | CV R² std |
| --- | --- | --- | --- | --- | --- |
| linear | 118.48 | 72.77 | 0.5785 | 0.5381 | 0.0351 |
| random_forest | 111.31 | 68.65 | 0.6281 | 0.5492 | 0.023 |
| gradient_boosting | 102.05 | 65.94 | 0.6873 | 0.5675 | 0.0236 |


**Selected model: `gradient_boosting`** (highest hold-out R²). For context, the target has mean ≈ 207.21 and median ≈ 162.9, range 14.5–2246.4.

### Top feature importance (gradient_boosting)

| feature | importance |
| --- | --- |
| num__beds | 0.2563 |
| cat__listing_type_Private room in rental unit | 0.1899 |
| num__guests | 0.1879 |
| num__baths | 0.0563 |
| num__host_listing_count | 0.0445 |
| num__bedrooms | 0.0315 |
| cat__room_type_entire_home | 0.0278 |
| cat__neighborhood_Eixample | 0.0217 |
| cat__listing_type_Room in hotel | 0.02 |
| cat__listing_type_Room in boutique hotel | 0.017 |
| cat__room_type_shared_room | 0.0166 |
| boo__professional_management_flag | 0.0114 |


Property capacity (beds, guests, baths) and room/listing type dominate, as expected for nightly rate. Figure: `reports/figures/price_model_feature_importance.png`.

---

## 4. Figures

| File | Shows |
|---|---|
| `reports/figures/clustering/cluster_scatter.png` | density × entire-home share, coloured by cluster, sized by risk |
| `reports/figures/clustering/cluster_centroids_heatmap.png` | centroid profile per cluster |
| `reports/figures/clustering/cluster_by_city.png` | cluster composition, BCN vs LDN |
| `reports/figures/clustering/risk_priority_top15.png` | top-15 risk-priority neighbourhoods per city |
| `reports/figures/price_model_feature_importance.png` | price model drivers |

---

## 5. Reproducibility

- All randomness seeded (`random_state=42`): clustering, train/test split, both tree models.
- Cluster labels are deterministic across reruns (centroid-pressure-rank assignment).
- Regenerate everything: `python run_pipeline.py --from 08 --to 10` (after a full local clone with both cities' cleaned CSVs in place).
