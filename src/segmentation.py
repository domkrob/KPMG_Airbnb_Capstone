"""Member 3 — Phase 3 (ML) segmentation + Phase 4 (final knowledge layer).

Pure functions, importable from notebooks. Three responsibilities:

1. ``compute_clusters``      — KMeans (k=3) on the STR-pressure profile, with
                               *semantic* labels (saturated / emerging / low_impact)
                               assigned by centroid pressure rank so they are stable
                               across reruns regardless of KMeans' arbitrary numbering.
2. ``compute_risk_score``    — per-city min-max weighted composite, 0–100.
3. ``assemble_knowledge_layer`` — append the three M3 columns to Member 2's KPI
                               table and emit the final ``knowledge_layer.csv``.

Design notes
------------
* Clustering features mix a count (``str_density``, 0–295) with shares (0–1), so we
  **StandardScale** before KMeans — feeding raw values would let str_density dominate.
* Scaling is pooled across both cities so a "saturated" profile means the same thing
  in Barcelona and London (Q6 cross-city comparability). The risk score, by contrast,
  is min-maxed *per city* because BCN and LDN absolute scales differ.
* ``breach_rate_90`` is NaN where a neighbourhood has zero entire homes (undefined,
  not zero). For clustering/scoring only, we treat that as 0 pressure — documented.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
CLUSTER_FEATURES: list[str] = [
    "str_density",
    "entire_home_share",
    "commercial_host_share",
    "multi_listing_host_share",
    "avg_occupancy",
    "breach_rate_90",
]

# Weights used both to (a) rank centroids for semantic labelling and (b) build the
# risk priority score. Heavier weight on displacement (entire-home) and regulatory
# breach, per the Member 3 starter guide.
RISK_WEIGHTS: dict[str, float] = {
    "str_density": 0.20,            # size of the STR footprint
    "entire_home_share": 0.30,      # displacement proxy — weighted heavily
    "commercial_host_share": 0.20,  # commercialisation
    "breach_rate_90": 0.30,         # regulatory risk
}

RANDOM_STATE = 42
K = 3
LABELS_BY_PRESSURE = ["low_impact", "emerging", "saturated"]  # ascending pressure

# A neighbourhood needs a minimum footprint before its share-based signals
# (entire_home_share, breach_rate_90 ...) are statistically meaningful — a single
# entire home that breaches the 90-night cap gives breach_rate_90 == 1.0, which is
# noise, not a priority. We shrink the raw score by a density-confidence factor
# str_density / (str_density + SAMPLE_K0): density 1 -> 0.17, 5 -> 0.50, 25 -> 0.83,
# 100 -> 0.95. This stops 1–2 listing areas dominating the priority ranking and
# aligns the score with Member 2's tier_sample_adequate flag (threshold 5).
SAMPLE_K0 = 5


# --------------------------------------------------------------------------- #
# 1. Clustering
# --------------------------------------------------------------------------- #
def _prep_matrix(kpis: pd.DataFrame) -> pd.DataFrame:
    """Return the cluster feature matrix with NaN breach rates treated as 0."""
    X = kpis[CLUSTER_FEATURES].copy()
    # breach_rate_90 is NaN when entire_home_count == 0 (undefined). For the
    # geometry of clustering we read that as "no regulatory pressure" -> 0.
    return X.fillna(0.0)


def compute_clusters(
    kpis: pd.DataFrame,
    *,
    k: int = K,
    random_state: int = RANDOM_STATE,
) -> tuple[pd.DataFrame, dict]:
    """Fit KMeans on the STR-pressure profile and return labelled rows + metadata.

    Returns
    -------
    (df, meta)
        ``df`` is a copy of ``kpis`` with three new columns:
        ``cluster_label`` (semantic), ``cluster_id`` (raw KMeans id),
        ``cluster_distance`` (euclidean distance to assigned centroid in scaled
        space — lower = more typical of its cluster = higher confidence).
        ``meta`` carries the silhouette score, centroid table, and label map.
    """
    df = kpis.copy()
    X = _prep_matrix(df)

    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)

    km = KMeans(n_clusters=k, random_state=random_state, n_init=10)
    raw_id = km.fit_predict(Xs)

    # Distance to assigned centroid (scaled space) = confidence proxy.
    dists = np.linalg.norm(Xs - km.cluster_centers_[raw_id], axis=1)

    # --- Semantic labelling: rank centroids by a weighted pressure score -----
    # Convert centroids back to original units, then score each with RISK_WEIGHTS
    # after a 0–1 min-max across centroids (so weights are comparable).
    centroids = pd.DataFrame(
        scaler.inverse_transform(km.cluster_centers_), columns=CLUSTER_FEATURES
    )
    w = pd.Series(RISK_WEIGHTS)
    cmm = centroids[w.index].copy()
    rng = (cmm.max() - cmm.min()).replace(0, 1)
    pressure = ((cmm - cmm.min()) / rng).mul(w, axis=1).sum(axis=1)

    order = pressure.sort_values().index.tolist()  # ascending pressure
    label_map = {cid: LABELS_BY_PRESSURE[rank] for rank, cid in enumerate(order)}

    df["cluster_id"] = raw_id
    df["cluster_label"] = df["cluster_id"].map(label_map)
    df["cluster_distance"] = np.round(dists, 4)

    sil = float(silhouette_score(Xs, raw_id)) if k > 1 else float("nan")

    centroids_out = centroids.copy()
    centroids_out["pressure_score"] = pressure.round(3)
    centroids_out["cluster_label"] = [label_map[i] for i in centroids_out.index]
    centroids_out["n_members"] = pd.Series(raw_id).value_counts().sort_index().values

    meta = {
        "silhouette": round(sil, 4),
        "k": k,
        "random_state": random_state,
        "features": CLUSTER_FEATURES,
        "label_map": label_map,
        "centroids": centroids_out,
        "scaler_mean": dict(zip(CLUSTER_FEATURES, scaler.mean_.round(4))),
        "scaler_scale": dict(zip(CLUSTER_FEATURES, scaler.scale_.round(4))),
    }
    return df, meta


# --------------------------------------------------------------------------- #
# 2. Risk priority score
# --------------------------------------------------------------------------- #
def compute_risk_score(
    kpis: pd.DataFrame,
    *,
    weights: dict[str, float] = RISK_WEIGHTS,
    sample_k0: int = SAMPLE_K0,
) -> pd.Series:
    """Per-city min-max weighted composite, sample-shrunk, rescaled to [0, 100].

    Steps (per city, so BCN/LDN absolute scales never mix):
      1. min-max scale each weighted component to 0–1 within the city,
      2. weighted sum -> raw composite,
      3. multiply by a density-confidence factor ``d / (d + sample_k0)`` so tiny
         neighbourhoods cannot top the priority list on n=1 noise,
      4. rescale the shrunk score so the city max = 100 (keeps it interpretable
         as "share of the worst neighbourhood's priority").

    NaN breach rates -> 0 (undefined regulatory pressure reads as none).
    """
    cols = list(weights)
    w = pd.Series(weights)
    out = pd.Series(0.0, index=kpis.index)

    for _, idx in kpis.groupby("city").groups.items():
        block = kpis.loc[idx, cols].fillna(0.0)
        rng = (block.max() - block.min()).replace(0, 1)
        scaled = (block - block.min()) / rng
        composite = scaled.mul(w, axis=1).sum(axis=1)

        density = kpis.loc[idx, "str_density"].astype(float)
        confidence = density / (density + sample_k0)
        shrunk = composite * confidence

        peak = shrunk.max() or 1.0
        out.loc[idx] = shrunk / peak * 100.0

    return out.round(2)


# --------------------------------------------------------------------------- #
# 3. Knowledge-layer assembly
# --------------------------------------------------------------------------- #
def assemble_knowledge_layer(kpis: pd.DataFrame, clustered: pd.DataFrame) -> pd.DataFrame:
    """Build the final knowledge layer: Member 2's KPIs + the three M3 columns,
    plus explicit canonical aliases (``subdivision``, ``breach_rate``,
    ``listings_impacted_{90,60,30}``) that Member 4's tool layer documents.
    """
    df = kpis.copy()
    df["cluster_label"] = clustered["cluster_label"].values
    df["cluster_distance"] = clustered["cluster_distance"].values
    df["risk_priority_score"] = compute_risk_score(df).values

    # Canonical aliases (tools.py also aliases these, but make the file self-describing)
    df["subdivision"] = df["geo_key"]
    df["breach_rate"] = df["breach_rate_90"]
    for cap in (90, 60, 30):
        df[f"listings_impacted_{cap}"] = df[f"breach_count_{cap}"]

    # Stable ordering: highest risk first within each city
    df = df.sort_values(["city", "risk_priority_score"], ascending=[True, False])
    return df.reset_index(drop=True)


def tier_cluster_crosstab(df: pd.DataFrame) -> pd.DataFrame:
    """Sanity cross-check: tier_1 areas should concentrate in 'saturated'."""
    return pd.crosstab(df["tier_concentration_price"], df["cluster_label"])
