"""Member 3 — Phase 3 (ML) listing-level price prediction.

KPMG slide requirement ("Price Prediction Modeling" + "Evaluation and Metrics").
Not consumed by the chatbot — it is a standalone model + metrics artefact.

Trains three regressors (linear / random forest / gradient boosting) inside an
sklearn ``Pipeline`` (so the saved ``.joblib`` is a self-contained predictor that
carries its own preprocessing), evaluates on a held-out test set, and reports
RMSE / MAE / R² in original currency units.

The target ``ttm_avg_rate`` is right-skewed, so we model ``log1p(price)`` and invert
for metric reporting. Geography enters as ``neighborhood`` (district/borough — low
cardinality) plus ``city``; ``subdivision`` is too high-cardinality to one-hot cleanly.

City-agnostic: ``load_price_frame`` globs whatever ``*_listings_clean.csv`` files are
present, so the same code trains on Barcelona alone (cloud env) or Barcelona + London
(local clone with both cleaned files).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from src.data_io import PROCESSED_DIR

TARGET = "ttm_avg_rate"
NUMERIC = ["beds", "bedrooms", "baths", "guests", "host_listing_count"]
BOOLEAN = [
    "entire_home_flag",
    "multi_listing_host",
    "host_5_plus_listings",
    "host_10_plus_listings",
    "professional_management_flag",
    "has_registration",
]
CATEGORICAL = ["room_type", "listing_type", "city", "neighborhood"]
RANDOM_STATE = 42


def load_price_frame() -> pd.DataFrame:
    """Concatenate every available ``{city}_listings_clean.csv`` into one frame.

    Returns rows with a valid positive target only. Works with whatever cities are
    present on disk (BCN-only in the cloud env; BCN+LDN on a full local clone).
    """
    frames = []
    for city_dir in sorted(p for p in PROCESSED_DIR.iterdir() if p.is_dir()):
        f = city_dir / f"{city_dir.name}_listings_clean.csv"
        if f.exists():
            df = pd.read_csv(f)
            df["city"] = city_dir.name
            frames.append(df)
    if not frames:
        raise FileNotFoundError(
            f"No *_listings_clean.csv found under {PROCESSED_DIR}. "
            "Populate the city folders from your local clone first."
        )
    data = pd.concat(frames, ignore_index=True)
    data = data[data[TARGET].notna() & (data[TARGET] > 0)].copy()
    return data


def build_xy(data: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, list[str]]:
    """Assemble the feature matrix X, log-target y, and the feature column list."""
    cols = [c for c in NUMERIC + BOOLEAN + CATEGORICAL if c in data.columns]
    X = data[cols].copy()
    for b in [c for c in BOOLEAN if c in X.columns]:
        X[b] = X[b].astype(float)
    for c in [c for c in CATEGORICAL if c in X.columns]:
        X[c] = X[c].fillna("unknown").astype(str)
    y = np.log1p(data[TARGET].astype(float))
    return X, y, cols


def _preprocessor(cols: list[str]) -> ColumnTransformer:
    num = [c for c in NUMERIC if c in cols]
    boo = [c for c in BOOLEAN if c in cols]
    cat = [c for c in CATEGORICAL if c in cols]
    return ColumnTransformer(
        transformers=[
            ("num", SimpleImputer(strategy="median"), num),
            ("boo", SimpleImputer(strategy="most_frequent"), boo),
            ("cat", OneHotEncoder(handle_unknown="ignore", min_frequency=5), cat),
        ],
        remainder="drop",
    )


def _models() -> dict[str, object]:
    return {
        "linear": LinearRegression(),
        "random_forest": RandomForestRegressor(
            n_estimators=300, max_depth=None, min_samples_leaf=2,
            random_state=RANDOM_STATE, n_jobs=-1,
        ),
        "gradient_boosting": GradientBoostingRegressor(
            n_estimators=400, max_depth=3, learning_rate=0.05,
            subsample=0.9, random_state=RANDOM_STATE,
        ),
    }


def _score(y_true_log, y_pred_log) -> dict[str, float]:
    """Metrics in ORIGINAL currency units (invert the log)."""
    yt, yp = np.expm1(y_true_log), np.expm1(y_pred_log)
    rmse = float(np.sqrt(mean_squared_error(yt, yp)))
    return {
        "rmse": round(rmse, 2),
        "mae": round(float(mean_absolute_error(yt, yp)), 2),
        "r2": round(float(r2_score(yt, yp)), 4),
    }


def train_and_select(data: pd.DataFrame | None = None) -> dict:
    """Train all models, evaluate on a held-out test set, pick the best by test R².

    Returns a dict with the fitted best pipeline, the metrics table, the chosen
    model name, the train/test sizes, and feature-importance (best tree model).
    """
    if data is None:
        data = load_price_frame()
    X, y, cols = build_xy(data)
    pre = _preprocessor(cols)

    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE
    )

    results, fitted = {}, {}
    for name, est in _models().items():
        pipe = Pipeline([("pre", pre), ("model", est)])
        pipe.fit(X_tr, y_tr)
        test_m = _score(y_te, pipe.predict(X_te))
        cv_r2 = cross_val_score(pipe, X_tr, y_tr, cv=5, scoring="r2", n_jobs=-1)
        test_m["cv_r2_mean"] = round(float(cv_r2.mean()), 4)
        test_m["cv_r2_std"] = round(float(cv_r2.std()), 4)
        results[name] = test_m
        fitted[name] = pipe

    metrics = pd.DataFrame(results).T[["rmse", "mae", "r2", "cv_r2_mean", "cv_r2_std"]]
    best_name = metrics["r2"].idxmax()
    best = fitted[best_name]

    importances = _feature_importance(best, best_name)

    return {
        "best_name": best_name,
        "best_pipeline": best,
        "metrics": metrics,
        "n_train": len(X_tr),
        "n_test": len(X_te),
        "cities": sorted(data["city"].unique().tolist()),
        "feature_importance": importances,
        "target_describe": data[TARGET].describe().round(2).to_dict(),
    }


def _feature_importance(pipe: Pipeline, name: str, top: int = 20) -> pd.DataFrame | None:
    """Return a tidy importance table for tree models (None for linear)."""
    model = pipe.named_steps["model"]
    if not hasattr(model, "feature_importances_"):
        return None
    feat_names = pipe.named_steps["pre"].get_feature_names_out()
    imp = (
        pd.DataFrame({"feature": feat_names, "importance": model.feature_importances_})
        .sort_values("importance", ascending=False)
        .head(top)
        .reset_index(drop=True)
    )
    return imp
