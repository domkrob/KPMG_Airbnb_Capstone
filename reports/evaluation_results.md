# Chatbot Evaluation Results

_Generated 2026-06-10 by `notebooks/08_chatbot_evaluation.ipynb`._

Tools in `app/tools.py` were called directly (no live LLM) and scored against `reports/golden_answers.json`. This isolates data grounding from LLM phrasing.

**Backing knowledge layer:** `knowledge_layer.csv` (560 rows). **Missing Member 3 columns:** none.

## Overall accuracy: **100.0%**  (target 90%)

✅ **PASS** — meets the ≥ 90% target.

## Score per question

| Question | Score | Groundedness | Completeness | Caveat | Refusal | Status |
|---|---|---|---|---|---|---|
| **Q1** — Which neighbourhoods have the highest concentration of… | 100% | 100% | 100% | 100% | — | — |
| **Q2** — Where is Airbnb most likely removing homes from the lo… | 100% | 100% | 100% | 100% | — | — |
| **Q3** — Which neighbourhoods are dominated by commercial/profe… | 100% | 100% | 100% | 100% | — | — |
| **Q4** — In which neighbourhoods does high STR density coincide… | 100% | 100% | 100% | 100% | — | — |
| **Q5** — Which neighbourhoods are saturated, and which are emer… | 100% | 100% | 100% | 100% | — | — |
| **Q6** — How does STR pressure compare between Barcelona and Lo… | 100% | 100% | 100% | 100% | — | — |
| **Q7** — If entire-home listings were capped at X nights/year, … | 100% | 100% | 100% | 100% | — | — |
| **Refusal** — Refusal / not-available handling | 100% | — | — | — | 100% | — |

## Notes per question

- **Q4** — Composite of two tool rankings; reproduced exactly from the knowledge layer.
- **Q5** — Scored against Member 3's real cluster_label via list_by_cluster (faithful retrieval of all three clusters, both cities). golden_answers.json Q5 still encodes the heuristic saturated/emerging — regenerate notebook 07 to a cluster-based Q5 for a clean live-LLM eval.
- **Q6** — Like-for-like: compare_cities medians vs golden neighbourhood_medians (citywide listing-level totals intentionally excluded).

## Method & scoring

- **Groundedness** — top-ranked value(s) match the golden number(s) within tolerance (±0.01 for shares/prices, exact for counts). For Q5, `list_by_cluster` faithfully returns the table's cluster membership.
- **Completeness** — fraction of the golden top-N neighbourhoods reproduced (accent/case-insensitive name match), averaged across cities; for Q5, cluster counts match the table for all three clusters.
- **Caveat correctness** — every caveat mapped to the question (via `applies_to` in `caveats.json`) exists, and question-specific triggers are wired (e.g. RESIDE appears for Barcelona Q7 and is absent for London). Caveat *wording* in the final answer requires a live-LLM eval — out of scope here.
- **Refusal correctness** — the tool returns the correct error/status (not a fabricated value) when data is unavailable (unknown area, invalid metric/cap/cluster, empty corpus).

## Known limitations / pending

- **Q5 is now scored against Member 3's real `cluster_label`** via the `list_by_cluster` tool (faithful retrieval of all three clusters, both cities — no longer PENDING). `golden_answers.json` Q5 still encodes the heuristic saturated/emerging, so regenerate notebook 07 to a cluster-based Q5 for a clean end-to-end / live-LLM eval. The heuristic-vs-KMeans `saturated` agreement is high in London, partial in Barcelona.
- **Q6** is scored like-for-like (medians vs medians). The listing-level citywide totals (BCN 2594) are a different denominator from `compare_cities` KPI sums (BCN 2354) and are intentionally not compared.
- This harness validates **data grounding only**. A live-LLM pass (with an API key) is still needed to score answer phrasing, caveat wording, and end-to-end tool selection.
