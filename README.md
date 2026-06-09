# Urban Rental Intelligence Copilot

IE × KPMG Capstone 2026. A GenAI decision-support assistant for city housing policy analysts — comparing **Barcelona** (Plan RESIDE total phase-out) and **London** (90-night cap) on the same short-term-rental KPIs.

> The tool surfaces associations and risk indicators. It does NOT claim Airbnb causes rent rises.

## Pipeline at a glance

```
raw AirDNA CSV  →  cleaning  →  features  →  neighbourhood KPIs  →  EDA  →  lock + dictionary  →  golden answers
   data/raw/        nb 01–02     nb 03         nb 04                 nb 05    nb 06               nb 07
                    src/(M1)     src/features  src/kpis              src/eda  src/dictionary      src/golden
```

Every stage chains off the previous one's output. Notebooks are thin orchestrators; logic lives in `src/`.

## Setup

```powershell
conda env create -f environment.yml
conda activate kpmg-airbnb-capstone
```

## Run the whole pipeline

```powershell
python run_pipeline.py
```

Or run notebooks 01 → 07 in order via Jupyter.

## Folder map

| Folder | What's in it |
|---|---|
| `data/raw/` | AirDNA exports for Barcelona + London (gitignored, large) |
| `data/processed/` | Cleaned + featurised CSVs, KPI table, data dictionary |
| `notebooks/` | Pipeline notebooks 01 – 07 |
| `src/` | All pipeline logic — pure Python modules |
| `reports/` | Figures, choropleths, tables, golden answers, caveats |
| `team/` | Per-member work plans + starter guides |

## Team

- **Member 1** — Data cleaning + base flags ✅ done
- **Member 2** (Mohammed) — Feature engineering + EDA + knowledge layer ✅ done
- **Member 3** — Clustering + price model + risk score ⏳ next. **Start here:** `team/M3_starter_guide.md`
- **Member 4** — Streamlit + Claude chatbot + evaluation ⏳ after M3. **Start here:** `team/M4_starter_guide.md`

## Key outputs

- `data/processed/neighbourhood_kpis.csv` — the knowledge layer (560 rows × 25 cols, both cities stacked)
- `data/processed/data_dictionary.md` — every column documented
- `reports/golden_answers.json` — ground truth for chatbot evaluation
- `reports/caveats.json` — disclaimers the chatbot must surface

## Anchors

The chatbot must answer the **7 canonical questions** from the project handover. If a feature, model, or chatbot tool doesn't serve one of those questions, it doesn't belong in the MVP.
