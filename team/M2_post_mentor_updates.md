# Member 2 — Post-Mentor-Meeting Updates

**Owner:** Mohammed (Member 2)
**Date:** 2026-06-10
**Trigger:** Mentor (Angela) feedback documented in `Mentor_meeting_minutes.md`, plus an audit-follow-up to close out responsibility correctly.
**Scope:** Three additive changes (two mentor-driven, one audit-driven) that do **not** break the existing pipeline. All validations pass; 82/82 audit checks green.

This document tells Members 3 and 4 exactly what changed, why, and what to take into account in their work.

---

## TL;DR (60 seconds)

1. **`neighbourhood_kpis.csv` gained two columns:** `tier_concentration_price` (tier_1/2/3) and `tier_sample_adequate` (bool).
2. **`reports/golden_answers.json` and `.md` gained two new keys per question:** `policy_guidance` (one-liner framing) and `recommended_action` per result row (prescriptive sentence).
3. Validation gate still passes 19/19. M4's `app/tools.py` still loads cleanly. M3's clustering inputs are unchanged.

---

## 1. Mentor feedback addressed in this update

| Item | Mentor quote | What I did |
|---|---|---|
| **C** | *"Flag risk-tier areas (tier 1/2/3) by concentration and price, then suggest specific policy actions."* | Added `tier_concentration_price` and `tier_sample_adequate` to the KPI table. |
| **D** | *"Suggested question framing: 'which areas are emerging risks and what policy should be introduced?' rather than 'which neighborhood has the highest concentration?'"* | Added `policy_guidance` (one-liner per question) and `recommended_action` (per result row) to every golden answer. Tier-aware where relevant. |
| **E** | Audit follow-up (own initiative) | Closed the `avg_occupancy` NaN gap inside Member 2's aggregation rather than passing it downstream. Tightened the Phase D validation gate to catch any future regression. |

## 2. Mentor feedback **not** addressed (deferred / out of scope)

| Item | Why deferred |
|---|---|
| COVID years anomaly check | Team agreed to keep 2021 data as-is. No change. |
| Column-count reduction (30 → fewer) | User concern: risks breaking M3 (clustering inputs) and M4 (tool schema). Held off. |
| Gemini API blocker, agent branding, app UI redesign | Owned by Member 4 — not in Member 2's scope. |
| K-means cluster labels, gradient-boost price model | Owned by Member 3 — additive changes here do not interfere. |

---

## 3. Item C — Risk tier columns

### What was added

| Column | Type | Values | Definition |
|---|---|---|---|
| `tier_concentration_price` | string | `tier_1` / `tier_2` / `tier_3` | tier_1 = top quartile in BOTH `str_density` AND `median_nightly_price` (per city); tier_2 = top quartile in one; tier_3 = neither |
| `tier_sample_adequate` | bool | `True` / `False` | True if `str_density >= 5`; below that, tier defaults to `tier_3` and should be presented with a caveat |

Thresholds are computed **per city** (BCN vs LDN absolute scales differ). Logic lives in `src/kpis.py::add_concentration_price_tier()` and is invoked automatically inside `compute_neighbourhood_kpis()`.

### Distribution (run on the regenerated KPI table)

| | tier_1 | tier_2 | tier_3 | Total |
|---|---|---|---|---|
| Barcelona | 6 | 14 | 46 | 66 |
| London | 31 | 94 | 369 | 494 |

Sample-adequate share: BCN 49 / 66 (74%); LDN 310 / 494 (63%).

### Sample tier-1 areas (sanity check)

- **Barcelona tier 1**: la Dreta de l'Eixample, la Sagrada Família, el Poble-sec, la Vila de Gràcia, Sant Antoni
- **London tier 1**: Westbourne Green, Marylebone, Earl's Court, Paddington, Fulham, Chelsea, …

These match the intuitive "central tourist-saturated, premium-priced" expectation. Tier assignments are reproducible (deterministic — no randomness involved).

### What Member 3 should know

- The new columns are **additive** — every existing clustering input column is unchanged. If your clustering inputs are `str_density, entire_home_share, commercial_host_share, multi_listing_host_share, avg_occupancy, breach_rate_90`, **nothing changes for you**.
- If you want, you can use `tier_concentration_price` as either:
  - A **categorical feature** for the price model (one-hot)
  - A **validation cross-check** for your `cluster_label` — tier_1 areas should mostly land in your "saturated" cluster
  - A **fallback** in case your clustering misses obvious priority neighbourhoods
- `tier_sample_adequate` should mask any chart/output where you want to drop tiny-sample neighbourhoods.

**Null-handling cleanup (fixed in Member 2's pipeline, not a downstream task):**
- `avg_occupancy` previously emitted `NaN` for 26 tiny peripheral subdivisions (max 3 listings each, all `tier_sample_adequate=False`, zero policy signal — verified empirically).
- Fixed in `compute_neighbourhood_kpis()`: `avg_occupancy` is now `.fillna(0)` on the group mean. Honest semantic: "no measurable activity → 0 occupancy".
- **You no longer need any null handling for `avg_occupancy`** — feed it directly to KMeans. Validation gate now blocks any future regression that re-introduces NaN here.
- The rate columns (`breach_rate_*`, `reside_unregistered_share`, `professional_management_share`) deliberately remain `NaN` when their denominator is zero — that's semantically meaningful (e.g., "no entire homes here, breach rate undefined") and you should preserve it.

### What Member 4 should know

- `app/tools.py` still loads cleanly against the updated KPI table (verified).
- If your `get_neighbourhood_metrics()` returns "all columns", these two new keys will appear automatically — no code change needed.
- Suggested chatbot behaviour: when a user asks about a specific neighbourhood, include the tier as standard context ("X is a tier-1 area — high concentration and high price").
- If you want a clean "show me tier 1 areas" tool, just call `kpis[kpis.tier_concentration_price == "tier_1"]`.

**Null-handling cleanup (fixed in Member 2's pipeline — affects how you format answers):**
- `avg_occupancy` will never be NaN any more — Member 2's KPI aggregation now fills 0 for the ~26 tiny subdivisions where every listing has null occupancy in raw AirDNA. So `0.0` is now a real value the chatbot may quote.
- **When `avg_occupancy == 0` AND `tier_sample_adequate == False`**, surface the caveat: "no measurable activity in this peripheral subdivision" instead of "0% occupancy" — the latter would mislead the user into thinking it's been measured and is genuinely empty. Both flags are on the same KPI row, so the check is one line.
- The rate columns (`breach_rate_90`, `reside_unregistered_share`, `professional_management_share`) deliberately remain `NaN` when their denominator is zero — surface those as `"n/a — no entire homes recorded"` (or equivalent). Do **not** convert these to `0.0` — that would falsely imply 100% compliance.

---

## 4. Item D — Policy-advisor framing in golden answers

### What was added

Every question (Q1–Q7) in `reports/golden_answers.json` and `.md` now has:

| New field | Where it lives | Purpose |
|---|---|---|
| `policy_guidance` | At the question level (alongside `question` / `method`) | One-liner the chatbot can use as the framing intro before listing results |
| `recommended_action` | On each result row (alongside `geo_key`, ranks, metrics) | Prescriptive sentence — what the policy analyst should do about this specific neighbourhood |
| `tier` | On result rows for Q1, Q4, Q7 | Tier label for the row, looked up from the KPI table |

### Sample (Q1, Barcelona, top 2)

```json
{
  "rank": 1,
  "geo_key": "la Dreta de l'Eixample",
  "str_density": 295,
  "tier": "tier_1",
  "recommended_action": "Priority inspection target (Tier 1 — high concentration AND high price.). 295 listings concentrated here — size enforcement capacity to match."
}
```

### Sample (Q7, Barcelona, 90-night cap, top 1)

```json
{
  "rank": 1,
  "geo_key": "la Dreta de l'Eixample",
  "listings_impacted": 95,
  "entire_home_count": 201,
  "breach_rate": 0.473,
  "tier": "tier_1",
  "recommended_action": "At 90-night cap, 95 listings recoverable here (Tier 1 — high concentration AND high price.). Sequence enforcement against this list, starting from tier 1."
}
```

### What Member 4 should know

- `golden_answers.json` is fully backwards-compatible. **Existing keys are unchanged**, just two new ones added per question + new `tier` and `recommended_action` keys per row.
- If your evaluation harness reads specific keys, it continues to work without modification.
- Suggested chatbot integration:
  - Open every answer with the question's `policy_guidance` as the framing line.
  - For each top-N item, present the row's `recommended_action` after the number.
  - For tier-1 rows, emphasise the tier badge.
- Question-level policy guidance is short and lift-ready for your system prompt or per-answer template.

### What Member 3 should know

- These additions are downstream of your work — they read the KPI table. Nothing you need to change.
- If your `cluster_label` lands and we want to expose it in the recommendations too, the change in `src/golden.py` is a one-line lookup similar to `_tier_for()`.

---

## 5. Pipeline-integrity confirmation

- **Validation gate (`src/dictionary.validate_knowledge_layer`):** 19/19 PASS after the update — now includes stricter null-checks on `avg_occupancy`, `entire_home_share`, `commercial_host_share`, `multi_listing_host_share`, and `active_share`. Any future regression that reintroduces a null in any of these will trip the gate at Phase D.
- **Schema parity:** Both BCN and LDN have the new columns. Schema-parity check still passes.
- **Reconciliation:** All density / entire-home / breach-90 totals still match between `*_listings_features.csv` and `neighbourhood_kpis.csv`.
- **`app/tools.py` import:** Loads cleanly. Schema aliasing in `_CANON` continues to work — the new columns are additive and ignored unless explicitly queried.
- **Notebook 04, 05, 06, 07 re-ran successfully** via `python run_pipeline.py --from 04 --to 07`.

---

## 6. Files changed

| File | Change |
|---|---|
| `src/kpis.py` | Added `add_concentration_price_tier()` function; called inside `compute_neighbourhood_kpis()`; new columns documented in `kpi_data_dictionary()`. Also: `avg_occupancy` now `.fillna(0)` with a clear inline comment explaining why. |
| `src/dictionary.py` | Added two rows in `NEIGHBOURHOOD_KPIS` spec for the new tier columns. Updated `avg_occupancy` definition to mention the 0-default. Expanded the `validate_knowledge_layer()` critical-columns list. |
| `src/golden.py` | Added `_tier_for()` and `_tier_phrase()` helpers; added `policy_guidance` + `recommended_action` to each Q1–Q7 function |
| `data/processed/neighbourhood_kpis.csv` | Regenerated (560 × 27 cols, was 560 × 25) |
| `data/processed/data_dictionary.md` | Regenerated to include the new columns |
| `data/processed/data_dictionary_neighbourhood_kpis.csv` | Regenerated |
| `reports/golden_answers.json` and `.md` | Regenerated with policy_guidance + recommended_action |
| `team/M2_post_mentor_updates.md` | This document (new) |

No notebook code was modified. No M3/M4 code was modified.

## 7. How to regenerate everything

```powershell
conda activate kpmg-airbnb-capstone
python run_pipeline.py --from 04 --to 07
```

Total runtime: under one minute on this hardware. The earlier stages (01–03) do not need to be re-run; nothing they produce was touched.

---

## 8. Open questions for the team

- **For M3:** does it make sense to publish `cluster_label` alongside `tier_concentration_price` as separate columns, or merge into a single `risk_classification` field? Recommendation: keep them separate — cluster_label is data-driven, tier is rule-based. They corroborate each other.
- **For M4:** do you want me to wire `policy_guidance` into a default chatbot template, or do you prefer to handle the framing yourself in the system prompt?
- **For both:** if anyone wants more tier granularity (e.g., a tier_0 for "extreme priority"), say the word. The function is a single threshold change away.
