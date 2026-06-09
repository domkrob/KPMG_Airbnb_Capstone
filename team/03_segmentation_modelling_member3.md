# Member 3 — Segmentation, Price Modelling & Policy Simulation

**Owner:** Member 3
**Status:** ⏳ Pending
**Sequence:** 3 of 4
**Depends on:** Member 2

---

## Scope

- **KPMG slide steps:** Segmentation Strategies + Price Prediction Modeling + Evaluation and Metrics
- **Handover phases:** completes **Phase 3** (ML) → finalises **Phase 4** (knowledge layer)
- **Canonical questions served:**
  - Q5 — Which neighbourhoods are saturated vs emerging hotspots?
  - Q6 — How does STR pressure compare between Barcelona and London?
  - Q7 — Policy simulation: if entire-home listings were capped at X nights/year, how many listings and which neighbourhoods would be affected?

---

## Tasks

### A. Neighbourhood clustering (main ML showpiece)

- Cluster subdivisions on the STR-pressure profile from Member 2's KPI table
  (features: density, entire-home share, commercial host share, occupancy, breach rate)
- Try KMeans with k=3–5; validate with silhouette score
- Label clusters interpretably: `saturated`, `emerging`, `low-impact`
- Set `random_state` so labels are reproducible across runs

### B. Light price prediction model (KPMG slide requirement)

- Target: `ttm_avg_rate` at listing level
- Features: subdivision, room type, beds, baths, guests, host concentration flags
- Try: linear regression, random forest, gradient boosting
- Report **RMSE, MAE, R²** on a held-out test set
- Save feature importance plot

### C. Composite Risk Priority Score

- Weighted 0–100 score per subdivision combining: density, entire-home share, commercialisation, breach rate
- Document weights and rationale in markdown

### D. Policy simulation (Q7 — the standout feature)

- **London:** count entire homes per subdivision with `ttm_days_booked > N` for **N = 90 / 60 / 30** — output: listings impacted per subdivision per cap
- **Barcelona:** count entire homes per subdivision without `has_registration` (RESIDE proxy) — output: potential housing units recoverable per subdivision

### E. Finalise the knowledge layer

Single clean table `knowledge_layer.csv`. Schema:

```text
city, neighborhood, subdivision,
str_density, entire_home_share, commercial_host_share,
median_nightly_price, avg_occupancy, breach_rate,
risk_priority_score, cluster_label,
listings_impacted_90, listings_impacted_60, listings_impacted_30
```

This is the **single source of truth** for the chatbot. Member 4 retrieves from it via function calls — nothing else.

---

## Deliverables

- `notebooks/05_clustering.ipynb`
- `notebooks/06_price_model.ipynb`
- `notebooks/07_policy_simulation.ipynb`
- `data/processed/knowledge_layer.csv` (final)
- `models/price_model.joblib` (saved regressor)
- `reports/figures/clustering/` (cluster maps)
- `reports/model_metrics.md` (RMSE, MAE, R², silhouette, feature importance)

---

## Acceptance criteria

- Cluster labels stable across reruns (random_state set)
- Price model metrics (RMSE, MAE, R²) reported on held-out test set
- Policy simulation fully reproducible from clean data
- `knowledge_layer.csv` columns documented in `reports/model_metrics.md`

---

## Handover to Member 4

Pass `knowledge_layer.csv` — must be retrieval-ready. Every column documented. Anything not in this file is not in the chatbot's universe.
