"""Run the full Urban Rental Intelligence Copilot pipeline end-to-end.

Executes notebooks 01 → 07 in order in the active env via nbconvert,
re-saving each in place. Stops on first failure.

Usage (from the repo root, with kpmg-airbnb-capstone env active):
    python run_pipeline.py

Run a specific range:
    python run_pipeline.py --from 03
    python run_pipeline.py --from 03 --to 05
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
NOTEBOOK_DIR = REPO_ROOT / "notebooks"

# Canonical notebook order
PIPELINE = [
    "01_barcelona_data_preparation_clean.ipynb",
    "02_london_data_preparation_clean.ipynb",
    "03_feature_engineering.ipynb",
    "04_neighbourhood_kpis.ipynb",
    "05_eda_barcelona_london.ipynb",
    "06_knowledge_layer_lock.ipynb",
    "07_golden_answers.ipynb",
]


def stage_number(filename: str) -> str:
    """Extract '01' from '01_barcelona_data_preparation_clean.ipynb'."""
    return filename.split("_", 1)[0]


def execute_notebook(path: Path, timeout: int = 900) -> None:
    """Execute a notebook in place via nbconvert. Raises on failure."""
    cmd = [
        sys.executable, "-m", "jupyter", "nbconvert",
        "--to", "notebook",
        "--execute",
        "--inplace",
        f"--ExecutePreprocessor.timeout={timeout}",
        str(path),
    ]
    print(f"\n>>> Running {path.name}")
    result = subprocess.run(cmd, cwd=NOTEBOOK_DIR)
    if result.returncode != 0:
        print(f"\nFAILED at {path.name}")
        sys.exit(result.returncode)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from", dest="start", default="01",
                        help="Stage to start from (e.g. 03). Default: 01")
    parser.add_argument("--to", dest="end", default="99",
                        help="Stage to stop after (inclusive). Default: 99 (run all)")
    parser.add_argument("--timeout", type=int, default=900,
                        help="Per-notebook timeout in seconds. Default: 900")
    args = parser.parse_args()

    selected = [
        nb for nb in PIPELINE
        if args.start <= stage_number(nb) <= args.end
    ]
    if not selected:
        print(f"No notebooks match --from {args.start} --to {args.end}")
        sys.exit(1)

    print(f"Pipeline plan ({len(selected)} notebooks):")
    for nb in selected:
        print(f"  - {nb}")

    for nb_name in selected:
        execute_notebook(NOTEBOOK_DIR / nb_name, timeout=args.timeout)

    print("\nPipeline complete.")


if __name__ == "__main__":
    main()
