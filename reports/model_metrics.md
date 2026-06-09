# Model Metrics — Urban Rental Intelligence Copilot

## Clustering — KMeans (k=3)

| Metric | Value |
|---|---|
| Algorithm | KMeans |
| k | 3 |
| random_state | 42 |
| Scaling | MinMaxScaler |
| Silhouette score | 0.2804 |

### Cluster label rationale

| Label | Distinguishing signal |
|---|---|
|  | Highest STR density AND highest entire-home share |
|  | Highest 90-night breach rate AND high occupancy |
|  | Low values across all features |

### Cluster sizes

| cluster_label   |   count |
|:----------------|--------:|
| saturated       |     297 |
| low_impact      |     174 |
| emerging        |      89 |

## Price Prediction Model

| Model | RMSE | MAE | R² |
|---|---|---|---|
| Ridge Regression | 99.3 | 54.1 | 0.704 |
| Random Forest | 81.2 | 36.7 | 0.802 |
| Gradient Boosting | 80.9 | 39.6 | 0.804 |

**Best model:** Gradient Boosting (lowest RMSE on 20%% held-out test set)
- Training set: 1460 listings | Test set: 365
- City: Barcelona
- Saved model: models/price_model.joblib

## Composite Risk Priority Score

| Component | Weight | Rationale |
|---|---|---|
| str_density | 0.20 | Raw STR footprint |
| entire_home_share | 0.30 | Housing displacement proxy |
| commercial_host_share | 0.20 | Professionalisation signal |
| breach_rate_90 | 0.30 | Regulatory non-compliance risk |

## Policy Simulation Results

### London — night cap

| Cap | Listings |
|---|---|
| 90 nights | 1,482 |
| 60 nights | 1,863 |
| 30 nights | 2,260 |

### Barcelona — RESIDE

| Metric | Count |
|---|---|
| Unregistered entire-home listings | 421 |
