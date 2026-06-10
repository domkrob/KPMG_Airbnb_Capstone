# Capstone Gap Report (v2) — post-pipeline validation

_Revalidated 2026-06-10, after notebooks 01–07 ran clean. Supersedes the v1 report._

## Headline

The Member 1/2 pipeline is complete and the chatbot is **runnable for 6 of the 7
canonical questions today**. But one premise in the request is incorrect and matters:

> ⚠️ **`data/processed/knowledge_layer.csv` does not exist.** It was not produced by
> this pipeline run. The knowledge layer the chatbot queries is
> `data/processed/neighbourhood_kpis.csv` (560×25). `knowledge_layer.csv` is
> *Member 3's* deliverable, and **Member 3's work has not run** — so `cluster_label`,
> `risk_priority_score`, and the `listings_impacted_*`-named columns are still absent.
> `tools.py` handles this automatically (alias layer + graceful fallback), which is
> why the chatbot still works.

## 1. File existence

| Expected | Status | Location |
|---|---|---|
| `knowledge_layer.csv` | ❌ **absent** | (M3 deliverable — not produced) |
| `neighbourhood_kpis.csv` | ✅ | `data/processed/` (the actual knowledge layer, 560×25) |
| `barcelona_listings_features.csv` | ✅ **now present** | `data/processed/barcelona/` |
| `london_listings_features.csv` | ✅ **now present** | `data/processed/london/` |
| city `*_listings_clean.csv`, `*_monthly_metrics_clean.csv` | ✅ | both city folders now populated |
| `golden_answers.json` | ✅ | `reports/` (not `data/processed/`) |
| `caveats.json` | ✅ | `reports/` (not `data/processed/`) |
| `eda_findings.md` | ✅ | `reports/` |
| `data_dictionary.md` | ✅ | `data/processed/` (still not in `reports/`) |

The big change since v1: `data/raw/` clearly got populated and the city-level feature
files now exist — the pipeline genuinely ran end to end.

## 2. Knowledge-layer schema (`neighbourhood_kpis.csv`, 560×25, BCN+LDN)

| Requested column | Status |
|---|---|
| `cluster_label` | ❌ **MISSING** (Member 3) |
| `risk_priority_score` | ❌ **MISSING** (Member 3) |
| `listings_impacted_90/60/30` | ⚠️ present as `breach_count_90/60/30` — `tools.py` aliases them, so `policy_simulation` works |
| `reside_unregistered_count` | ✅ present |
| `reside_unregistered_share` | ✅ present |
| density / shares / prices / breach rates | ✅ all present |

## 3. Golden answers

✅ `golden_answers.json` covers **all 7** questions (Q1–Q7) with concrete numbers.
Note Q5's `saturated`/`emerging` lists are still the **heuristic** placeholder
(per the file's own method note, Member 3 will replace with KMeans `cluster_label`).

## 4. Caveats

✅ Well-formed: a JSON list of 9 objects, each with `key`/`title`/`body`/`applies_to`.

## 5. App folder

✅ `app/tools.py`, `app/streamlit_app.py`, `app/system_prompt.md` all present
(plus `app/__init__.py`, `.env.example`, `data/regulations/`).

## 6. Tool smoke test (against the live data)

All returned **data, not errors**, and cross-check exactly against golden answers:

| Tool call | Result |
|---|---|
| `rank_neighbourhoods('barcelona','str_density',5)` | ✅ la Dreta de l'Eixample 295 … |
| `get_neighbourhood_metrics('barcelona','el Raval')` | ✅ full KPI dict |
| `compare_cities('str_density')` | ✅ BCN total 2354 / LDN total 9599 |
| `policy_simulation('barcelona',90)` | ✅ 611 impacted (**matches golden Q7**) |
| `policy_simulation('london',90)` | ✅ 1482 impacted |
| cross-check Q1 top BCN density | ✅ golden 295 == tool 295 |
| cross-check Q7 BCN cap-90 | ✅ golden 611 == tool 611 |

`knowledge_layer_status()` correctly reports the backing file as
`neighbourhood_kpis.csv` and flags `risk_priority_score`, `cluster_label` as missing.

## 7. Are you clear to add the API key and run the chatbot?

**Yes — go.** Copy `.env.example` → `.env`, set `ANTHROPIC_API_KEY`, then
`streamlit run app/streamlit_app.py`. The data layer is validated and grounded.

Run it knowing these three limits (none block launch):

1. **Q5 (saturated vs emerging) is the weak spot.** There is no `cluster_label`, so
   the chatbot can only approximate Q5 by ranking — it will **not** reproduce the
   golden Q5 cluster answer. Holds until Member 3 ships clustering; then regenerate
   `golden_answers.json` and rerun eval.
2. **Regulations RAG is empty.** `query_regulations` returns `no_corpus` until you
   add the Plan RESIDE / Deregulation Act texts to `data/regulations/{city}/`.
3. **Q6 city-comparison nuance.** `compare_cities` aggregates the KPI table
   (e.g. density total 2354 BCN), whereas golden Q6 `citywide_totals` uses
   listing-level totals (2594 BCN). Both are correct but computed on different
   denominators — your eval harness should compare like-for-like, not expect the
   chatbot's `compare_cities` to equal golden Q6 exactly.

## Still outstanding (your M4 list, not yet built)

- `notebooks/08_chatbot_evaluation.ipynb` + `reports/evaluation_results.md`
- Member 3 dependency: `knowledge_layer.csv` with `cluster_label` + `risk_priority_score`
  (then refresh golden answers + re-eval Q5)
