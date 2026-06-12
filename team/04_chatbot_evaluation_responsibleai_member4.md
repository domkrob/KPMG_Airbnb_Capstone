# Member 4 — GenAI Chatbot, Evaluation & Responsible AI

**Owner:** Member 4
**Status:** ⏳ Pending
**Sequence:** 4 of 4
**Depends on:** Member 3

---

## Scope

- **KPMG slide step:** Generate AI Chatbot
- **Handover phases:** **Phase 5** (chatbot build) → **Phase 6** (evaluation) → **Phase 7** (Responsible AI) → **Phase 8** (deliverables)
- **Canonical questions served:** all 7 — the chatbot must answer each one with grounded, cited responses

---

## Tasks

### A. Streamlit chatbot

- Front end: Streamlit
- LLM: Claude Sonnet via Anthropic API
- **Architecture: function/tool calling — NOT RAG, NOT context dumping**

### B. Tool functions (query `knowledge_layer.csv`)

- `get_neighbourhood_metrics(city, subdivision)`
- `rank_neighbourhoods(city, metric, top_n)`
- `compare_cities(metric)`
- `policy_simulation(city, cap_nights)`
- `list_subdivisions(city)`

The model calls these; the chatbot returns numbers from the table only. Zero fabrication.

### C. System prompt

- **Persona:** housing policy analyst assistant for city councils
- Must cite specific numbers from tool outputs
- Always flag caveats: AirDNA sample, association not causation, data freshness
- Refuse to answer questions outside the knowledge layer

### D. Evaluation (Phase 6)

- Build a ground-truth answer set from the 7 canonical questions (~30–50 test queries)
- **Target: ≥90% answer accuracy** vs known data rows
- Track:
  - **Groundedness** — cites the correct number from the table
  - **Refusal correctness** — says "I don't know" when the data isn't there
  - **Zero fabrication** — no hallucinated figures

### E. Responsible AI (Phase 7)

- Confidence flags on every answer (sample size, data freshness)
- Standing disclaimer block: AirDNA is a sample; STR ≠ Airbnb only; association ≠ causation
- Human-in-the-loop framing — the chatbot supports decisions, it does not make them
- No personally identifying host or listing info exposed beyond what the council already has

### F. Final deliverables (Phase 8)

- Streamlit app deployment + README section on how to run
- All notebooks committed and runnable
- Final consulting-style slide deck for KPMG presentation
- Demo plan / video for the KPMG meeting Angela will arrange

---

## Deliverables

- `app/streamlit_app.py`
- `app/tools.py` (tool function implementations)
- `app/system_prompt.md`
- `notebooks/11_chatbot_evaluation.ipynb`
- `reports/evaluation_results.md`
- `reports/final_slides.pdf`
- Updated repo `README.md` with run instructions

---

## Acceptance criteria

- All 7 canonical questions answered with grounded, cited responses
- ≥90% accuracy on the evaluation set
- **Zero fabricated figures** — all numbers traceable to `knowledge_layer.csv`
- App runs locally: `streamlit run app/streamlit_app.py`
- Anthropic API key loaded from `.env`; never committed

---

## Final handover

Repo is the deliverable. Tag the release. Brief Angela. Run the KPMG demo.
