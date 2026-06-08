# Member 4 — Starter Guide

You inherit a locked knowledge layer, a tested evaluation set, and a list of caveats. This document is your 5-minute on-ramp to building the chatbot.

---

## Your job in one sentence

Build a Streamlit chatbot that answers the **7 canonical questions** with grounded, cited numbers from `knowledge_layer.csv` — and **never fabricates**.

## What's already done for you

| File | What it gives you |
|---|---|
| `data/processed/neighbourhood_kpis.csv` (+ M3's cluster/risk columns) | Your retrieval source |
| `data/processed/data_dictionary.md` | Column definitions — lift into tool docstrings |
| `data/processed/dictionaries/*.csv` | Per-file dictionaries — load programmatically |
| `reports/golden_answers.json` | Ground-truth answer set — your eval harness reads this |
| `reports/caveats.json` | Disclaimers — inject into system prompt |
| `reports/eda_findings.md` | Narrative — copy into system prompt for context |

## Architecture (recommendation)

**Function calling, NOT RAG, NOT context dumping.** Define a small set of tools that query the knowledge layer; the model calls them; you serialise the result as natural language.

```
User question
   ↓
Claude Sonnet (Anthropic API)
   ↓
Tool call → query knowledge_layer.csv
   ↓
Structured result
   ↓
Claude formats as natural-language answer + cites numbers + appends caveat
   ↓
User
```

## Recommended tool functions

```python
# app/tools.py

def get_neighbourhood_metrics(city: str, geo_key: str) -> dict:
    """Return all KPIs for one neighbourhood. Use when the user asks
    about a specific named area."""

def rank_neighbourhoods(city: str, metric: str, top_n: int = 10,
                        min_density: int = 30) -> list[dict]:
    """Return the top-N neighbourhoods by a given KPI for a city.
    Use for 'which neighbourhoods have the highest X' questions."""

def compare_cities(metric: str) -> dict:
    """Side-by-side median + total per city for a metric.
    Use for Q6 questions."""

def policy_simulation(city: str, cap_nights: int) -> dict:
    """Return total impacted listings + top neighbourhoods at a given cap.
    Use for Q7 — the standout feature."""

def list_subdivisions(city: str) -> list[str]:
    """Return all valid geo_key values for a city. Use to fuzzy-match
    user-typed neighbourhood names."""

def get_caveat(key: str) -> str:
    """Look up a caveat by key from reports/caveats.json. Always called
    before formatting an answer."""
```

## Five-minute on-ramp

```python
import json, pandas as pd
from pathlib import Path

REPO = Path('.').resolve()  # from repo root
PROCESSED = REPO / 'data' / 'processed'
REPORTS = REPO / 'reports'

kpis = pd.read_csv(PROCESSED / 'neighbourhood_kpis.csv')
caveats = json.loads((REPORTS / 'caveats.json').read_text(encoding='utf-8'))
golden = json.loads((REPORTS / 'golden_answers.json').read_text(encoding='utf-8'))

# Example tool: rank by metric
def rank_neighbourhoods(city, metric, top_n=10):
    sub = kpis[kpis['city'] == city.lower()]
    return sub.nlargest(top_n, metric)[['geo_key', metric]].to_dict('records')

rank_neighbourhoods('barcelona', 'breach_count_90', 5)
# → [{'geo_key': "la Dreta de l'Eixample", 'breach_count_90': 95}, ...]
```

## System prompt skeleton

```
You are a housing policy analyst assistant for city councils evaluating
short-term rental (STR) impact in Barcelona and London.

Your knowledge comes entirely from the tools available. You DO NOT have
opinions, training-data facts, or made-up numbers. Every figure you cite
must come from a tool call.

Tone: precise, evidence-grounded, honest about uncertainty.

You MUST surface these caveats:
- AirDNA is a sample (~14% BCN, ~10% LDN of the full market)
- Association, not causation — never claim Airbnb causes rent rises
- RESIDE flag is meaningful for Barcelona only

If a user asks something the knowledge layer cannot answer (e.g., "should
the council ban Airbnb?"), refuse and redirect to data-grounded questions.
```

## Evaluation

The eval harness is straightforward:

```python
import json
golden = json.loads((REPORTS / 'golden_answers.json').read_text(encoding='utf-8'))

# For each Q1..Q7, send the question text to the chatbot, parse the answer,
# compare against golden['Q1']['answers'], score:
#   - groundedness (cites the right number)
#   - completeness (covers expected top-N)
#   - caveat correctness (right disclaimers appear)
#   - refusal correctness (refuses when appropriate)
# Target: ≥90% overall accuracy
```

Build the eval as a notebook `notebooks/08_chatbot_evaluation.ipynb` so each pass is reproducible.

## Gotchas to avoid

1. **Don't retrieve the whole knowledge layer into the prompt** — function calling beats context dumping. Token cost + hallucination risk.
2. **Westminster queries** — the LDN borough KPI has Westminster as one row (sub-areas were rolled up). The neighbourhood KPI table still has Mayfair, Belgravia etc. as separate rows. Be consistent.
3. **NaN values** — for shares (e.g., `breach_rate_90`) of neighbourhoods with 0 entire homes, the rate is NaN. Filter or format as "n/a — no entire homes recorded".
4. **Localised characters** — BCN neighbourhood names contain accents (`la Sagrada Família`). Use UTF-8 everywhere.
5. **Numbers must match `golden_answers.json` exactly** — if M3 re-runs and numbers change, refresh the golden file. Eval relies on it.

## Importable building blocks

```python
from src.golden import (
    q1_top_density, q2_top_entire_home_share, q3_top_commercial_host_share,
    q4_density_price_intersection, q5_saturated_vs_emerging,
    q6_city_comparison, q7_policy_simulation, CAVEATS,
)
# Each function returns the exact structured answer the chatbot should produce.
```

## Final deliverables

- `app/streamlit_app.py`
- `app/tools.py`
- `app/system_prompt.md`
- `notebooks/08_chatbot_evaluation.ipynb`
- `reports/evaluation_results.md`
- `reports/final_slides.pdf`
- Updated `README.md` with how-to-run instructions
