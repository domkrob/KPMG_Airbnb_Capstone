# Member 3 — Completion Notes

**Owner:** Member 3 (Dom)
**Status:** ✅ **COMPLETE**
**Builds on:** Member 2's post-mentor `dev` (`neighbourhood_kpis.csv` 560×27, tier columns + golden-answer policy framing).

This document tells Member 4 exactly what landed and what changed in the shared pipeline.

---

## TL;DR (60 seconds)

1. **Final knowledge layer shipped:** `data/processed/knowledge_layer.csv` (560×35) = Member 2's 27 KPI columns **unchanged** + 3 model columns (`cluster_label`, `cluster_distance`, `risk_priority_score`) + 4 canonical aliases (`subdivision`, `breach_rate`, `listings_impacted_90/60/30`).
2. **`app/tools.py` now loads `knowledge_layer.csv`** automatically (it was already coded to prefer it). `knowledge_layer_status()` → `ready_for_q5_clustering: true`, `missing_member3_columns: []`. **Q5 is unblocked.**
3. **Price model + metrics** saved (`models/price_model.joblib`, `reports/model_metrics.md`).
4. **Notebook renumber:** Member 4's eval notebook moved `08 → 11` so numeric order = execution order (M3 sits at 08–10, between golden answers and eval). Content untouched.

---

## 1. What Member 3 added

| Column (in `knowledge_layer.csv`) | Meaning |
|---|---|
| `cluster_label` | KMeans (k=3) segment: `saturated` / `emerging` / `low_impact`. Stable across reruns (centroid-pressure-rank labelling, `random_state=42`). |
| `cluster_distance` | Distance to assigned centroid (scaled space) — confidence proxy, lower = more typical. |
| `risk_priority_score` | Per-city weighted composite 0–100, sample-shrunk so 1-listing areas don't top the ranking. Higher = higher policy priority. |
| `subdivision` | Alias of `geo_key` (the name the chatbot exposes). |
| `breach_rate` | Alias of `breach_rate_90`. |
| `listings_impacted_90/60/30` | Aliases of `breach_count_90/60/30` (Q7). |

Every original Member 2 column is carried through verbatim. Nothing removed, nothing renamed in place.

## 2. Validation highlights (see `reports/model_metrics.md`)

- **Clustering:** silhouette 0.27 at k=3 (best in the k=2..6 sweep; moderate but interpretable). **All 37 tier-1 neighbourhoods land in `saturated`** — independent corroboration of Member 2's rule-based tiers.
- **Risk score top priorities** are the expected central premium areas: BCN la Dreta de l'Eixample (100), el Poble-sec, la Sagrada Família; LDN Westbourne Green (100), Paddington, Earl's Court, Marylebone, Whitechapel.
- **Price model:** gradient boosting wins, R² 0.69 on held-out test (Barcelona in the cloud env; **retrains on Barcelona + London automatically** on a full local clone — the loader globs whatever `*_listings_clean.csv` are present). RMSE €102 / MAE €66 vs €207 mean.

## 3. What Member 4 should know

- Your tool layer needs **no code change** — `cluster_label` and `risk_priority_score` are present; `list_by_cluster()` works (verified).
- Recommended Q5 wiring: `list_by_cluster(city, 'saturated')` for "saturated" areas; sort by `risk_priority_score` for the priority list; prefer `tier_sample_adequate == True` rows when presenting rankings.
- Your eval notebook is now `notebooks/11_chatbot_evaluation.ipynb` (was 08). Run order: `python run_pipeline.py` executes 01→11.
- The price model is **not** a chatbot data source — don't wire it into tools.

## 4. Files changed / added

| File | Change |
|---|---|
| `src/segmentation.py` | **new** — clustering + risk score + knowledge-layer assembly |
| `src/price_model.py` | **new** — listing-level price regressor |
| `data/processed/knowledge_layer.csv` | **new** — final 560×35 knowledge layer (whitelisted in `.gitignore`) |
| `models/price_model.joblib` | **new** — saved gradient-boosting pipeline |
| `reports/model_metrics.md` | **new** — clustering + risk + price metrics |
| `reports/figures/clustering/*.png` | **new** — 4 cluster/risk figures |
| `reports/figures/price_model_feature_importance.png` | **new** |
| `data/processed/data_dictionary.md` | added a `knowledge_layer.csv` section documenting the 3 new columns + aliases |
| `notebooks/08_segmentation.ipynb`, `09_price_model.ipynb`, `10_policy_simulation.ipynb` | **new** — executed |
| `notebooks/11_chatbot_evaluation.ipynb` | renamed from `08_…` (content unchanged) |
| `run_pipeline.py` | PIPELINE list extended to 08–11 |
| `team/04_…member4.md`, `team/M4_starter_guide.md` | notebook reference 08 → 11 |

## 5. Regenerate

```bash
conda activate kpmg-airbnb-capstone
python run_pipeline.py --from 08 --to 10   # M3 only (needs both cities' *_listings_clean.csv locally)
```
