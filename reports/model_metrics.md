# Model Metrics — Urban Rental Intelligence Copilot

_Member 3 outputs: clustering, price model, risk score, policy simulation._
_All numbers trace back to `data/processed/knowledge_layer.csv`._

---

## 1. Neighbourhood Clustering — KMeans (k=3)

| Metric | Value |
|---|---|
| Algorithm | KMeans |
| k | 3 |
| random_state | 42 |
| Scaling | MinMaxScaler (across full combined dataset) |
| Silhouette score | **0.2804** |
| Rows clustered | 560 (66 BCN + 494 LDN) |

### Clustering features

`str_density`, `entire_home_share`, `commercial_host_share`, `multi_listing_host_share`, `avg_occupancy`, `breach_rate_90`

### Cluster label rationale

| Label | Distinguishing signal | Policy implication |
|---|---|---|
| `saturated` | **Highest STR density** + **highest entire-home share** | Priority for housing displacement review |
| `emerging` | **Highest 90-night breach rate** + high occupancy | Enforcement priority — commercial activity already exceeding legal limits |
| `low_impact` | Low values across all features | Minimal policy concern under current data |

### Cluster sizes

| cluster_label | Neighbourhoods |
|---|---|
| saturated | 297 |
| low_impact | 174 |
| emerging | 89 |

### Cluster centroids (original scale) — key features

| Cluster | str_density | entire_home_share | commercial_host_share | avg_occupancy | breach_rate_90 |
|---|---|---|---|---|---|
| saturated | ~32 | 0.75 | 0.16 | 0.10 | 0.18 |
| emerging | ~14 | 0.61 | 0.15 | 0.19 | 0.65 |
| low_impact | ~6 | 0.27 | 0.09 | 0.07 | 0.06 |

### Figures
- `reports/figures/clustering/elbow_silhouette.png`
- `reports/figures/clustering/silhouette_plot.png`
- `reports/figures/clustering/cluster_scatter.png`
- `reports/figures/clustering/cluster_by_city.png`

---

## 2. Price Prediction Model

| Model | RMSE (€) | MAE (€) | R² |
|---|---|---|---|
| Ridge Regression | 99.3 | 54.1 | 0.704 |
| Random Forest | 81.2 | 36.7 | 0.802 |
| **Gradient Boosting** | **80.9** | **39.6** | **0.804** |

**Best model:** Gradient Boosting (lowest RMSE on 20% held-out test set)

### Training details

| Detail | Value |
|---|---|
| Target | `ttm_avg_rate` — trailing 12-month average nightly rate (€) |
| Training set | 1,460 listings |
| Test set | 365 listings |
| Train/test split | 80/20, random_state=42 |
| City | Barcelona (London listing-level data not in repo due to size) |
| Numeric features | `guests`, `bedrooms`, `beds`, `baths`, `host_listing_count`, `num_reviews` |
| Categorical (one-hot) | `room_type`, `host_commercial_tier`, `occupancy_band`, `price_band`, `geo_key` |
| Boolean flags | `entire_home_flag`, `multi_listing_host`, `host_5_plus_listings`, `has_registration`, `superhost` |
| Saved model | `models/price_model.joblib` |

### Figures
- `reports/figures/clustering/price_model_feature_importance.png`

---

## 3. Composite Risk Priority Score

### Weight specification

| Component | Weight | Rationale |
|---|---|---|
| `str_density` | 0.20 | Raw STR footprint — larger presence = larger potential impact |
| `entire_home_share` | **0.30** | Strongest housing displacement proxy — highest weight |
| `commercial_host_share` | 0.20 | Professionalised activity harder to regulate |
| `breach_rate_90` | **0.30** | Direct regulatory non-compliance signal — highest weight |

**Scaling:** MinMaxScaler across the full combined dataset (both cities) so BCN and LDN scores are directly comparable.  
**Output range:** 0 (minimal STR pressure) → 100 (maximum STR pressure)

### Score summary

| Stat | Value |
|---|---|
| Mean | 26.7 |
| Median | 29.5 |
| Std | 14.2 |
| Max | 60.2 |

### Figures
- `reports/figures/clustering/risk_score_distribution.png`

---

## 4. Policy Simulation Results

### London — entire-home night cap (Q7)

Counts entire-home listings per subdivision with `ttm_days_booked > N` for each cap threshold.

| Cap threshold | Listings impacted | % of London entire-home listings |
|---|---|---|
| 90 nights/year | **1,482** | ~22.7% |
| 60 nights/year | **1,863** | ~28.5% |
| 30 nights/year | **2,260** | ~34.6% |

### Barcelona — RESIDE registration compliance (Q7 BCN)

Entire-home listings without `has_registration` = unregistered under RESIDE proxy.

| Metric | Count |
|---|---|
| Unregistered entire-home listings | **421** |
| Potential housing units recoverable (upper bound) | **421** |

### Figures
- `reports/figures/clustering/policy_simulation.png`

---

## 5. knowledge_layer.csv — Column Documentation

_This is the single source of truth for Member 4's chatbot. Every column below is retrieval-ready._

| Column | Type | Definition | Notes |
|---|---|---|---|
| `city` | str | `barcelona` or `london` | — |
| `neighborhood` | str | Same as subdivision (geo_key fallback) | Alias for chatbot lookup consistency |
| `subdivision` | str | Primary geo key — barrio (BCN) or local neighbourhood (LDN) | Use this for all joins |
| `geo_level` | str | `subdivision` or `neighborhood` | Resolution indicator from Member 2 |
| `str_density` | int | Total STR listings in the subdivision | Includes inactive listings |
| `entire_home_share` | float 0–1 | Fraction of listings that are entire homes | Housing displacement proxy |
| `commercial_host_share` | float 0–1 | Fraction of listings from commercial/super-commercial hosts | Hosts with 5+ listings |
| `median_nightly_price` | float | Median TTM average nightly rate (€ / £) | `0` where no active listings |
| `avg_occupancy` | float 0–1 | Mean L90D occupancy rate | Active listings only where possible |
| `breach_rate` | float 0–1 | Fraction of entire-home listings > 90 booked nights/year | London cap proxy |
| `risk_priority_score` | float 0–100 | Weighted composite risk score (Member 3) | Higher = more enforcement priority |
| `cluster_label` | str | `saturated` / `emerging` / `low_impact` | Member 3 KMeans output |
| `cluster_distance` | float | Distance to cluster centroid | Lower = more "typical" of its cluster |
| `listings_impacted_90` | int | Entire-home listings > 90 booked nights/yr | London cap simulation (Q7) |
| `listings_impacted_60` | int | Entire-home listings > 60 booked nights/yr | London cap simulation (Q7) |
| `listings_impacted_30` | int | Entire-home listings > 30 booked nights/yr | London cap simulation (Q7) |
| `active_listings` | int | Listings active in any of the past 12 months | Excludes zombie listings |
| `entire_home_count` | int | Count of entire-home listings (all activity levels) | Numerator for `entire_home_share` |
| `reside_unregistered_count` | int | BCN: entire-home listings without RESIDE registration | LDN: use `listings_impacted_*` instead |
| `reside_unregistered_share` | float 0–1 | BCN: fraction of entire homes without registration | RESIDE compliance signal |
| `p25_price` | float | 25th percentile nightly price (€ / £) | — |
| `p75_price` | float | 75th percentile nightly price (€ / £) | — |
| `total_revenue` | float | Sum of TTM revenue across all listings (€ / £) | — |
| `multi_listing_host_share` | float 0–1 | Fraction of listings from hosts with ≥2 properties | — |
| `professional_management_share` | float 0–1 | Fraction managed by professional property managers | ~54% LDN nulls imputed 0 by M2 |
| `active_share` | float 0–1 | Fraction of listings active in past 12 months | — |

> **Caveats (for chatbot system prompt):**
> - AirDNA sample covers ~14% of BCN universe, ~10% of LDN.
> - `professional_management_share` imputed False (~54% of LDN) — treat with caution.
> - `reside_unregistered_count` is a proxy, not ground-truth RESIDE data.
> - Data range: March 2021 – February 2026.
> - Association ≠ causation. All findings support decision-making; they do not make decisions.
