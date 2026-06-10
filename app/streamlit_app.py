"""app/streamlit_app.py — Urban Rental Intelligence Copilot.

A grounded housing-policy chatbot over the STR knowledge layer for Barcelona and
London. Architecture is function/tool calling (NOT context dumping, NOT RAG for the
core questions): Gemini calls the seven tools in app/tools.py, we execute them
locally, feed the structured results back, and Gemini composes a cited, caveated
answer.

LLM backend: Google Gemini via the ``google-generativeai`` SDK (gemini-2.0-flash,
free tier). The tool/function-calling loop is preserved — only the provider changed.

Run:  streamlit run app/streamlit_app.py
Needs GEMINI_API_KEY in the environment or a .env file at the repo root.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st

# Make `tools` importable whether run via `streamlit run app/streamlit_app.py`
# (app/ on path already) or from the repo root.
APP_DIR = Path(__file__).resolve().parent
REPO_ROOT = APP_DIR.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

import tools as T  # noqa: E402

# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #
# Gemini 2.0 Flash (free tier) is the default backend. Override with CHATBOT_MODEL
# (e.g. gemini-2.0-flash, gemini-1.5-pro) if you need a different Gemini model.
import os  # noqa: E402

MODEL = os.getenv("CHATBOT_MODEL", "gemini-2.0-flash")
MAX_TOKENS = 4096
MAX_TOOL_ROUNDS = 6  # safety cap on the agentic loop

# --------------------------------------------------------------------------- #
# Tool schemas (what the model sees) + dispatch table (what we run)
#
# TOOL_SCHEMAS below are authored in the Anthropic shape (name/description/
# input_schema) because it is the clearest to read and edit. They are converted to
# Gemini function declarations at module load by `_to_gemini_tools()` further down.
# --------------------------------------------------------------------------- #
CITY_ENUM = list(T.VALID_CITIES)
METRIC_ENUM = sorted(T.RANKABLE_METRICS)

TOOL_SCHEMAS = [
    {
        "name": "get_neighbourhood_metrics",
        "description": (
            "Return all KPIs for one named neighbourhood/subdivision in a city. "
            "Call this when the user asks about a specific named area (e.g. 'el Raval', "
            "'Westminster'). Matching is accent- and case-insensitive."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "enum": CITY_ENUM},
                "subdivision": {"type": "string", "description": "Neighbourhood name."},
            },
            "required": ["city", "subdivision"],
        },
    },
    {
        "name": "rank_neighbourhoods",
        "description": (
            "Return the top-N subdivisions in a city by a metric. Call this for "
            "'which neighbourhoods have the highest/most X' questions. Defaults to a "
            "minimum STR density of 30 to exclude thinly-sampled areas."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "enum": CITY_ENUM},
                "metric": {"type": "string", "enum": METRIC_ENUM},
                "top_n": {"type": "integer", "minimum": 1, "maximum": 50, "default": 10},
                "min_density": {"type": "integer", "minimum": 0, "default": 30},
            },
            "required": ["city", "metric"],
        },
    },
    {
        "name": "compare_cities",
        "description": (
            "Side-by-side comparison of Barcelona vs London on one metric (totals for "
            "count-like metrics, medians for rate/price metrics). Call this for "
            "'how does Barcelona compare to London on X' questions."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"metric": {"type": "string", "enum": METRIC_ENUM}},
            "required": ["metric"],
        },
    },
    {
        "name": "policy_simulation",
        "description": (
            "Estimate the impact of an annual entire-home night cap (90/60/30). "
            "Returns total listings that would breach the cap in the AirDNA sample plus "
            "the most-impacted subdivisions. For Barcelona also returns RESIDE "
            "unregistered-entire-home counts. Call this for cap / '90-night rule' / "
            "RESIDE policy-impact questions."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "enum": CITY_ENUM},
                "cap_nights": {"type": "integer", "enum": list(T.VALID_CAPS)},
                "top_n": {"type": "integer", "minimum": 1, "maximum": 50, "default": 10},
            },
            "required": ["city", "cap_nights"],
        },
    },
    {
        "name": "list_subdivisions",
        "description": (
            "Return all valid subdivision names for a city. Call this to resolve a "
            "fuzzy, misspelled, or partial area name before another tool call."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"city": {"type": "string", "enum": CITY_ENUM}},
            "required": ["city"],
        },
    },
    {
        "name": "list_by_cluster",
        "description": (
            "List a city's subdivisions by KMeans cluster — 'saturated', 'emerging', or "
            "'low_impact' — ordered by risk_priority_score. Call this for Q5 ('which "
            "neighbourhoods are saturated / emerging hotspots'). Omit cluster_label to get "
            "cluster counts plus the top of each cluster."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "enum": CITY_ENUM},
                "cluster_label": {"type": "string", "enum": list(T.VALID_CLUSTERS)},
                "top_n": {"type": "integer", "minimum": 1, "maximum": 50, "default": 10},
            },
            "required": ["city"],
        },
    },
    {
        "name": "query_regulations",
        "description": (
            "RAG over the regulatory corpus for a city (Barcelona Plan RESIDE; London "
            "Deregulation Act 2015 / 90-night rule). Returns the most relevant sourced "
            "passages. Call this for ANY question about the law, registration "
            "requirements, what is permitted, or policy mechanics — and answer ONLY "
            "from the passages it returns, citing the source filename."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "enum": CITY_ENUM},
                "question": {"type": "string", "description": "The regulatory question."},
                "top_k": {"type": "integer", "minimum": 1, "maximum": 8, "default": 4},
            },
            "required": ["city", "question"],
        },
    },
]

DISPATCH = {
    "get_neighbourhood_metrics": T.get_neighbourhood_metrics,
    "rank_neighbourhoods": T.rank_neighbourhoods,
    "compare_cities": T.compare_cities,
    "policy_simulation": T.policy_simulation,
    "list_subdivisions": T.list_subdivisions,
    "list_by_cluster": T.list_by_cluster,
    "query_regulations": T.query_regulations,
}


def run_tool(name: str, tool_input: dict) -> dict:
    fn = DISPATCH.get(name)
    if fn is None:
        return {"error": "unknown_tool", "name": name}
    try:
        return fn(**tool_input)
    except TypeError as e:
        return {"error": "bad_arguments", "detail": str(e)}
    except Exception as e:  # noqa: BLE001 — never let a tool crash the chat
        return {"error": "tool_failed", "detail": str(e)}


# --------------------------------------------------------------------------- #
# Anthropic input_schema -> Gemini function declaration converter
#
# Gemini's parameter schema is a strict OpenAPI subset: it accepts type,
# description, properties, required, items, enum, nullable and format — but rejects
# JSON-Schema extras like `default`, `minimum` and `maximum`, and only allows `enum`
# on STRING-typed fields. We therefore strip the unsupported keys (the validation
# they encoded lives in tools.py anyway) and drop integer enums (e.g. cap_nights),
# whose valid values are already spelled out in each tool's description.
# --------------------------------------------------------------------------- #
_GEMINI_SCHEMA_KEYS = {"type", "description", "properties", "required", "items", "nullable", "format"}


def _clean_schema(schema: dict) -> dict:
    """Recursively reduce an Anthropic/JSON-Schema dict to Gemini-accepted keys."""
    out: dict = {}
    for key, value in schema.items():
        if key == "properties":
            out[key] = {prop: _clean_schema(sub) for prop, sub in value.items()}
        elif key == "items":
            out[key] = _clean_schema(value)
        elif key == "enum":
            if schema.get("type") == "string":  # Gemini only allows string enums
                out[key] = list(value)
        elif key in _GEMINI_SCHEMA_KEYS:
            out[key] = value
    return out


def _to_gemini_tools(schemas: list[dict]) -> list[dict]:
    """Convert the Anthropic-style TOOL_SCHEMAS into a Gemini `tools` payload."""
    declarations = [
        {
            "name": s["name"],
            "description": s["description"],
            "parameters": _clean_schema(s["input_schema"]),
        }
        for s in schemas
    ]
    return [{"function_declarations": declarations}]


GEMINI_TOOLS = _to_gemini_tools(TOOL_SCHEMAS)


# --------------------------------------------------------------------------- #
# System prompt: static file + runtime-injected caveats and data status
# --------------------------------------------------------------------------- #
@st.cache_data(show_spinner=False)
def build_system_prompt() -> str:
    base = (APP_DIR / "system_prompt.md").read_text(encoding="utf-8")
    caveats = json.loads((REPO_ROOT / "reports" / "caveats.json").read_text(encoding="utf-8"))
    status = T.knowledge_layer_status()

    caveat_lines = ["\n## Binding caveats (from reports/caveats.json)\n"]
    items = caveats.values() if isinstance(caveats, dict) else caveats
    for c in items:
        if isinstance(c, dict):
            title = c.get("title") or c.get("key") or ""
            applies = c.get("applies_to") or c.get("applies") or "all"
            text = c.get("body") or c.get("text") or c.get("caveat") or ""
            caveat_lines.append(f"- **{title}** (applies to: {applies}) — {text}")
    data_note = (
        f"\n## Live data status\n"
        f"- Knowledge layer: `{status['source_file']}` "
        f"({status['rows']} rows, cities: {', '.join(status['cities'])}).\n"
    )
    if status["missing_member3_columns"]:
        data_note += (
            f"- NOT yet available (Member 3 pending): "
            f"{', '.join(status['missing_member3_columns'])}. If asked about cluster "
            f"labels or risk scores, say they are not yet in the knowledge layer.\n"
        )
    return base + "\n" + "\n".join(caveat_lines) + data_note


# --------------------------------------------------------------------------- #
# Gemini client
# --------------------------------------------------------------------------- #
@st.cache_resource(show_spinner=False)
def get_client():
    """Load .env, read GEMINI_API_KEY and configure the Gemini SDK.

    Returns the configured ``google.generativeai`` module. Raises if the key is
    missing so the UI can show a clear setup message.
    """
    try:
        from dotenv import load_dotenv

        load_dotenv(REPO_ROOT / ".env")
    except Exception:
        pass

    import google.generativeai as genai

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set (looked in the environment and .env).")
    genai.configure(api_key=api_key)
    return genai


def _args_to_dict(args) -> dict:
    """Convert a Gemini function_call args proto (MapComposite) to a plain dict.

    Handles nested maps/lists defensively; our tool args are flat scalars in practice.
    """
    def conv(v):
        if isinstance(v, (str, int, float, bool)) or v is None:
            return v
        if hasattr(v, "items"):
            return {k: conv(x) for k, x in v.items()}
        try:
            return [conv(x) for x in v]
        except TypeError:
            return v

    return {k: conv(v) for k, v in args.items()}


def _to_gemini_history(history: list[dict]) -> list[dict]:
    """Map the app's plain {role, content} turns onto Gemini chat history."""
    return [
        {"role": "model" if m["role"] == "assistant" else "user", "parts": [m["content"]]}
        for m in history
    ]


def chat_turn(genai, system_prompt: str, history: list[dict]) -> tuple[str, list[dict]]:
    """Run one manual tool-use loop against Gemini. Returns (answer_text, tool_trace).

    ``history`` is the app's provider-agnostic [{role, content}] list whose final
    entry is the current user message. Prior turns seed the Gemini chat; the last
    message is sent to open the loop, and tool results are fed back as
    FunctionResponse parts until the model produces a plain-text answer.
    """
    model = genai.GenerativeModel(
        model_name=MODEL,
        system_instruction=system_prompt,
        tools=GEMINI_TOOLS,
        generation_config={"max_output_tokens": MAX_TOKENS},
    )
    *prior, last = history
    chat = model.start_chat(history=_to_gemini_history(prior))
    message = last["content"]
    tool_trace: list[dict] = []

    for _ in range(MAX_TOOL_ROUNDS):
        try:
            resp = chat.send_message(message)
        except Exception as e:  # noqa: BLE001 — surface API errors as chat text, not a crash
            detail = str(e)
            if "429" in detail or "RESOURCE_EXHAUSTED" in detail or "quota" in detail.lower():
                return (
                    "The Gemini API quota was exceeded (free-tier rate / daily limit). "
                    "Please wait a minute and retry, or check your plan at "
                    "https://ai.google.dev/gemini-api/docs/rate-limits.",
                    tool_trace,
                )
            return (f"The Gemini API call failed: {detail}", tool_trace)
        parts = resp.candidates[0].content.parts
        calls = [p.function_call for p in parts if p.function_call and p.function_call.name]

        if not calls:
            text = "".join(p.text for p in parts if getattr(p, "text", "")).strip()
            return text or "(The model returned no text.)", tool_trace

        # Execute every requested call and send all results back in one turn.
        responses = []
        for fc in calls:
            args = _args_to_dict(fc.args)
            out = run_tool(fc.name, args)
            tool_trace.append({"name": fc.name, "input": args, "output": out})
            responses.append(
                genai.protos.Part(
                    function_response=genai.protos.FunctionResponse(
                        name=fc.name, response={"result": out}
                    )
                )
            )
        message = responses

    return (
        "I wasn't able to resolve that within the tool-call limit. Please rephrase or "
        "narrow the question.",
        tool_trace,
    )


# --------------------------------------------------------------------------- #
# Streamlit UI
# --------------------------------------------------------------------------- #
st.set_page_config(
    page_title="Urban Rental Intelligence Copilot",
    page_icon="🏙️",  # browser-tab favicon only; the in-app title carries no emoji
    layout="centered",
)

# --------------------------------------------------------------------------- #
# Presentation layer — consulting aesthetic (navy/white/cobalt, flat, minimal).
# Pairs with .streamlit/config.toml. Styling only; no behaviour depends on it.
# --------------------------------------------------------------------------- #
st.markdown(
    """
    <style>
      /* ---------- Global ---------- */
      html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                     Helvetica, Arial, sans-serif;
        color: #0B1F33;
      }
      [data-testid="stAppViewContainer"] { background: #F7FAFC; }
      [data-testid="stHeader"] { background: transparent; }
      [data-testid="stDecoration"] { display: none; }            /* drop the rainbow bar */
      [data-testid="stMainBlockContainer"] { padding-top: 2.5rem; max-width: 1080px; }

      /* ---------- Header ---------- */
      .uric-header { margin-bottom: 1.75rem; }
      .uric-header h1 {
        font-size: 1.95rem; font-weight: 700; letter-spacing: -0.01em;
        color: #0B1F33; margin: 0 0 0.35rem 0; line-height: 1.2;
      }
      .uric-header p {
        font-size: 0.95rem; color: #5B6B7C; margin: 0 0 0.9rem 0; line-height: 1.45;
      }
      .uric-rule { height: 3px; width: 64px; background: #1E49E2; }

      /* ---------- Sidebar ---------- */
      [data-testid="stSidebar"] { background: #FFFFFF; border-right: 1px solid #E0E4EA; }
      .uric-label {
        font-size: 0.7rem; font-weight: 700; text-transform: uppercase;
        letter-spacing: 0.12em; color: #5B6B7C; margin: 0 0 0.6rem 0;
      }
      .uric-kv {
        display: flex; justify-content: space-between; gap: 1rem;
        font-size: 0.85rem; padding: 0.32rem 0; border-bottom: 1px solid #F0F2F6;
      }
      .uric-kv span { color: #5B6B7C; white-space: nowrap; }
      .uric-kv b { color: #1E49E2; font-weight: 600; text-align: right; word-break: break-word; }
      .uric-note {
        font-size: 0.8rem; color: #8A5A00; background: #FFF8E6;
        border: 1px solid #F2E2B3; padding: 0.5rem 0.6rem; margin-top: 0.7rem; line-height: 1.4;
      }
      .uric-divider { height: 1px; background: #E0E4EA; margin: 1.4rem 0; }
      .uric-list { font-size: 0.85rem; }
      .uric-list > div {
        padding: 0.5rem 0 0.5rem 0.85rem; border-left: 2px solid #1E49E2;
        margin-bottom: 0.5rem; line-height: 1.45; color: #0B1F33;
      }

      /* ---------- Buttons ---------- */
      .stButton button {
        border-radius: 2px; border: 1px solid #1E49E2; background: #FFFFFF;
        color: #1E49E2; font-weight: 600; font-size: 0.85rem; padding: 0.4rem 0.9rem;
        transition: all 0.15s ease;
      }
      .stButton button:hover { background: #1E49E2; color: #FFFFFF; }
      /* Example-question buttons read as a left-aligned list, not centred CTAs. */
      [data-testid="stSidebar"] .stButton button {
        text-align: left; justify-content: flex-start; line-height: 1.3; margin-bottom: 0.35rem;
      }
      .uric-list b { color: #1E49E2; font-weight: 600; }

      /* ---------- Chat messages ---------- */
      /* Avatars stay in the DOM (needed by the :has() selectors) but are hidden. */
      [data-testid="stChatMessageAvatarUser"],
      [data-testid="stChatMessageAvatarAssistant"] { display: none; }

      [data-testid="stChatMessage"] {
        width: fit-content; max-width: 82%; border-radius: 2px;
        padding: 0.9rem 1.15rem; margin: 0.55rem 0;
        box-shadow: 0 1px 2px rgba(11, 31, 51, 0.04);
      }
      /* Assistant: left-aligned, white, thin cobalt left border */
      [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
        background: #FFFFFF; border: 1px solid #E0E4EA; border-left: 3px solid #1E49E2;
        margin-right: auto;
      }
      /* User: right-aligned, light cobalt fill */
      [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
        background: #EEF2FF; border: 1px solid #D6E0FF; margin-left: auto;
      }
      [data-testid="stChatMessage"] p { font-size: 0.92rem; line-height: 1.55; }

      /* ---------- Chat input ---------- */
      [data-testid="stBottom"] { background: transparent; }
      [data-testid="stChatInput"] {
        border: 1px solid #E0E4EA; border-radius: 2px; background: #FFFFFF;
      }
      [data-testid="stChatInput"]:focus-within {
        border-color: #1E49E2; box-shadow: 0 0 0 1px #1E49E2;
      }
      [data-testid="stChatInput"] textarea::placeholder { color: #9AA7B4; }

      /* ---------- Tool-call expander ---------- */
      [data-testid="stExpander"] {
        border: 1px solid #E0E4EA; border-radius: 2px; background: #FFFFFF;
      }
      [data-testid="stExpander"] summary { font-size: 0.82rem; color: #5B6B7C; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="uric-header">
      <h1>Urban Rental Intelligence Copilot</h1>
      <p>Grounded short-term-rental policy analytics for Barcelona &amp; London —
         every figure is tool-sourced.</p>
      <div class="uric-rule"></div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Canonical golden questions (reports/golden_answers.json) offered as one-click
# prompts: Q1, Q2, a Barcelona-vs-London comparison (Q6), and the cap simulation (Q7).
# Cities/caps are made concrete so each tool call has unambiguous arguments.
EXAMPLE_QUESTIONS = [
    ("Q1 · STR concentration",
     "Which Barcelona neighbourhoods have the highest concentration of short-term rentals?"),
    ("Q2 · Residential loss",
     "In London, where is Airbnb most likely removing homes from the long-term "
     "residential market?"),
    ("Q6 · Barcelona vs London",
     "How does short-term-rental pressure compare between Barcelona and London?"),
    ("Q7 · 90-night cap",
     "If entire-home listings in Barcelona were capped at 90 nights per year, how many "
     "listings and which neighbourhoods would be affected?"),
]

with st.sidebar:
    _status = T.knowledge_layer_status()

    st.markdown('<div class="uric-label">Key Data</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="uric-kv"><span>Barcelona</span><b>2,594 listings</b></div>'
        '<div class="uric-kv"><span>London</span><b>9,643 listings</b></div>'
        '<div class="uric-kv"><span>Coverage</span><b>Mar 2021 – Feb 2026</b></div>'
        f'<div class="uric-kv"><span>Cities</span><b>{", ".join(_status["cities"])}</b></div>',
        unsafe_allow_html=True,
    )
    if _status["missing_member3_columns"]:
        st.markdown(
            f'<div class="uric-note">Pending Member 3: '
            f'{", ".join(_status["missing_member3_columns"])}</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="uric-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="uric-label">Regulatory Context</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="uric-list">'
        '<div><b>Barcelona</b> — Plan RESIDE: tourist-flat licences frozen and being '
        'phased out; no new STR licences issued.</div>'
        '<div><b>London</b> — Deregulation Act 2015: entire-home lets capped at '
        '90 nights per calendar year.</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="uric-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="uric-label">Example Questions</div>', unsafe_allow_html=True)
    for _label, _question in EXAMPLE_QUESTIONS:
        if st.button(_label, key=f"ex_{_label}", use_container_width=True):
            st.session_state["pending_prompt"] = _question

    st.markdown('<div class="uric-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="uric-label">Limitations</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="uric-list">'
        '<div>All figures are from the AirDNA sample, not the full market.</div>'
        '<div>Association, not causation.</div>'
        '<div>The assistant refuses questions it cannot ground in the data.</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="uric-divider"></div>', unsafe_allow_html=True)
    if st.button("Clear conversation"):
        st.session_state.pop("display", None)
        st.session_state.pop("history", None)
        st.rerun()

# Two parallel histories: `display` for the UI, `history` for the API.
st.session_state.setdefault("display", [])
st.session_state.setdefault("history", [])

for msg in st.session_state.display:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("trace"):
            with st.expander(f"🔧 {len(msg['trace'])} tool call(s)"):
                for t in msg["trace"]:
                    st.markdown(f"**`{t['name']}`** — input: `{t['input']}`")
                    st.json(t["output"], expanded=False)

# A typed message takes priority; otherwise a clicked example question (set in the
# sidebar this run) is consumed. Both flow through the identical processing path below.
_typed = st.chat_input("Ask about STR density, hotspots, city comparisons, caps, or regulations…")
prompt = _typed or st.session_state.pop("pending_prompt", None)
if prompt:
    st.session_state.display.append({"role": "user", "content": prompt})
    st.session_state.history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            client = get_client()
        except Exception as e:  # noqa: BLE001
            st.error(
                "Could not initialise the Gemini client — set GEMINI_API_KEY "
                f"(in .env or the environment). Details: {e}"
            )
            st.stop()

        with st.spinner("Querying the knowledge layer…"):
            answer, trace = chat_turn(client, build_system_prompt(), st.session_state.history)

        st.markdown(answer)
        if trace:
            with st.expander(f"🔧 {len(trace)} tool call(s)"):
                for t in trace:
                    st.markdown(f"**`{t['name']}`** — input: `{t['input']}`")
                    st.json(t["output"], expanded=False)

    st.session_state.history.append({"role": "assistant", "content": answer})
    st.session_state.display.append({"role": "assistant", "content": answer, "trace": trace})
