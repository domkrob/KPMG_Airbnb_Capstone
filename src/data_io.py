"""Path constants and load/save helpers for processed datasets."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"


def load_clean_listings(city: str) -> pd.DataFrame:
    """Load the Member 1 cleaned listings CSV for a city."""
    city = city.lower()
    return pd.read_csv(PROCESSED_DIR / city / f"{city}_listings_clean.csv")


def load_monthly_metrics(city: str) -> pd.DataFrame:
    """Load the Member 1 monthly metrics CSV for a city. Parses month_date."""
    city = city.lower()
    return pd.read_csv(
        PROCESSED_DIR / city / f"{city}_monthly_metrics_clean.csv",
        parse_dates=["month_date"],
    )


def save_features(df: pd.DataFrame, city: str) -> Path:
    """Save the feature-engineered listings CSV for a city."""
    city = city.lower()
    out = PROCESSED_DIR / city / f"{city}_listings_features.csv"
    df.to_csv(out, index=False)
    return out
