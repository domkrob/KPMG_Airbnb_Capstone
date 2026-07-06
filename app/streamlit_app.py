"""app/streamlit_app.py — UrbanLens (AI-powered STR-regulation policy advisor).

A grounded housing-policy chatbot over the STR knowledge layer for Barcelona and
London. Architecture is function/tool calling (NOT context dumping, NOT RAG for the
core questions): the model calls the eight tools in app/tools.py, we execute them
locally, feed the structured results back, and the model composes a cited, caveated
answer with risk-tier-led policy recommendations.

LLM backend: Anthropic via the ``anthropic`` SDK (claude-haiku-4-5), using the
Messages API tool-use loop. The tool/function-calling loop is unchanged — only the
provider changed.

Run:  streamlit run app/streamlit_app.py
Needs ANTHROPIC_API_KEY in the environment or a .env file at the repo root.
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
# Anthropic Claude Haiku 4.5 — cheapest/fastest Claude with reliable tool use.
# Override with CHATBOT_MODEL if you need a different Claude model.
import os  # noqa: E402

MODEL = os.getenv("CHATBOT_MODEL", "claude-haiku-4-5")
MAX_TOKENS = 4096
MAX_TOOL_ROUNDS = 6  # safety cap on the agentic loop

# --------------------------------------------------------------------------- #
# Tool schemas (what the model sees) + dispatch table (what we run)
#
# TOOL_SCHEMAS below are authored in the Anthropic shape (name/description/
# input_schema) — exactly what the Messages API `tools` parameter expects, passed
# through as ANTHROPIC_TOOLS further down.
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
        "name": "get_risk_tier_areas",
        "description": (
            "Return every neighbourhood in a city at a given RISK TIER (1, 2, or 3), "
            "sorted by risk_priority_score descending. Tiers are computed per city: "
            "Tier 1 = top third (highest priority for action), Tier 2 = middle third, "
            "Tier 3 = bottom third. Call this for 'which areas are highest priority / "
            "Tier 1', 'what should <city> focus on', or to get the action shortlist for "
            "a tier. Lead policy advice with this classification."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "enum": CITY_ENUM},
                "tier": {"type": "integer", "enum": list(T.VALID_RISK_TIERS)},
            },
            "required": ["city", "tier"],
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

# Integer params the model could occasionally emit as strings. Claude's tool use
# returns proper typed integers, so the schemas stay standard ("type": "integer");
# this is just a defensive coercion in run_tool() below. tools.py also coerces
# (int(top_n), int(cap_nights), _coerce_tier), so it is belt-and-braces.
_INT_PARAMS = ("top_n", "cap_nights", "tier", "top_k")


DISPATCH = {
    "get_neighbourhood_metrics": T.get_neighbourhood_metrics,
    "rank_neighbourhoods": T.rank_neighbourhoods,
    "compare_cities": T.compare_cities,
    "policy_simulation": T.policy_simulation,
    "list_subdivisions": T.list_subdivisions,
    "list_by_cluster": T.list_by_cluster,
    "get_risk_tier_areas": T.get_risk_tier_areas,
    "query_regulations": T.query_regulations,
}


def run_tool(name: str, tool_input: dict) -> dict:
    fn = DISPATCH.get(name)
    if fn is None:
        return {"error": "unknown_tool", "name": name}
    # Coerce stringified integers (the model sometimes sends top_n="10"). Non-numeric
    # strings (e.g. tier="Tier 1") are left as-is for the tool's own parser.
    tool_input = dict(tool_input)
    for key in _INT_PARAMS:
        if isinstance(tool_input.get(key), str):
            try:
                tool_input[key] = int(tool_input[key])
            except (TypeError, ValueError):
                pass
    try:
        return fn(**tool_input)
    except TypeError as e:
        return {"error": "bad_arguments", "detail": str(e)}
    except Exception as e:  # noqa: BLE001 — never let a tool crash the chat
        return {"error": "tool_failed", "detail": str(e)}


# --------------------------------------------------------------------------- #
# Anthropic tools payload — TOOL_SCHEMAS are already authored in the Anthropic
# shape (name / description / input_schema), so this is a straight pass-through
# of exactly those keys (the standard `tools` format the Messages API expects).
# --------------------------------------------------------------------------- #
ANTHROPIC_TOOLS = [
    {"name": s["name"], "description": s["description"], "input_schema": s["input_schema"]}
    for s in TOOL_SCHEMAS
]


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
# Anthropic client
# --------------------------------------------------------------------------- #
@st.cache_resource(show_spinner=False)
def get_client():
    """Load .env, read ANTHROPIC_API_KEY and return a configured Anthropic client.

    Raises if the key is missing so the UI can show a clear setup message.
    """
    try:
        from dotenv import load_dotenv

        load_dotenv(REPO_ROOT / ".env")
    except Exception:
        pass

    import anthropic

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set (looked in the environment and .env).")
    return anthropic.Anthropic(api_key=api_key)


def _to_anthropic_messages(history: list[dict]) -> list[dict]:
    """Map the app's plain {role, content} turns onto Anthropic Messages. The system
    prompt is NOT a message here — it is passed via the `system=` parameter."""
    return [
        {"role": "assistant" if m["role"] == "assistant" else "user", "content": m["content"]}
        for m in history
    ]


def chat_turn(client, system_prompt: str, history: list[dict]) -> tuple[str, list[dict]]:
    """Run one manual tool-use loop against the Anthropic Messages API.
    Returns (answer_text, tool_trace).

    ``history`` is the app's provider-agnostic [{role, content}] list whose final
    entry is the current user message. Each round we send the conversation; if Claude
    emits tool_use blocks we run them, append the assistant turn and the tool_result
    blocks, and loop until it returns a plain-text answer.
    """
    messages = _to_anthropic_messages(history)
    tool_trace: list[dict] = []

    for _ in range(MAX_TOOL_ROUNDS):
        try:
            resp = client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                system=system_prompt,
                tools=ANTHROPIC_TOOLS,
                messages=messages,
            )
        except Exception as e:  # noqa: BLE001 — surface API errors as chat text, not a crash
            detail = str(e)
            if "429" in detail or "rate_limit" in detail.lower() or "overloaded" in detail.lower():
                return (
                    "The Anthropic API is rate-limited or overloaded. Please wait a "
                    "moment and retry.",
                    tool_trace,
                )
            return (f"The Anthropic API call failed: {detail}", tool_trace)

        tool_uses = [b for b in resp.content if getattr(b, "type", None) == "tool_use"]

        if not tool_uses:
            text = "".join(
                b.text for b in resp.content if getattr(b, "type", None) == "text"
            ).strip()
            return text or "(The model returned no text.)", tool_trace

        # Record Claude's assistant turn (its full content, incl. tool_use blocks).
        messages.append({"role": "assistant", "content": resp.content})

        # Execute each tool and feed the results back as one user turn of tool_results.
        tool_results = []
        for tu in tool_uses:
            args = dict(tu.input)
            out = run_tool(tu.name, args)
            tool_trace.append({"name": tu.name, "input": args, "output": out})
            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": tu.id,
                    "content": json.dumps(out, ensure_ascii=False),
                }
            )
        messages.append({"role": "user", "content": tool_results})

    return (
        "I wasn't able to resolve that within the tool-call limit. Please rephrase or "
        "narrow the question.",
        tool_trace,
    )


# --------------------------------------------------------------------------- #
# Inline visualisations — bar charts for ranked / comparison tool results.
#
# Additive presentation only: these read the structured output already captured in
# the tool trace and render a chart in the consulting palette (cobalt bars), themed
# to match the UI light/dark toggle via `_chart_theme()`. They never raise into the
# chat — on any problem they return None and nothing is drawn.
# --------------------------------------------------------------------------- #
import matplotlib  # noqa: E402

matplotlib.use("Agg")  # headless backend — render to PNG for st.pyplot
import matplotlib.pyplot as plt  # noqa: E402

_COBALT = "#1E49E2"
_NAVY = "#0B1F33"
_SLATE = "#5B6B7C"
_GRID = "#E0E4EA"

# Pretty axis labels per canonical metric column.
_METRIC_LABELS = {
    "str_density": "STR density (listings)",
    "risk_priority_score": "Risk priority score",
    "breach_rate": "Breach rate (90-night)",
    "breach_rate_90": "Breach rate (90-night)",
    "breach_rate_60": "Breach rate (60-night)",
    "breach_rate_30": "Breach rate (30-night)",
    "entire_home_share": "Entire-home share",
    "commercial_host_share": "Commercial-host share",
    "multi_listing_host_share": "Multi-listing-host share",
    "median_nightly_price": "Median nightly price",
    "avg_occupancy": "Average occupancy",
    "listings_impacted_90": "Listings impacted (90-night cap)",
    "listings_impacted_60": "Listings impacted (60-night cap)",
    "listings_impacted_30": "Listings impacted (30-night cap)",
    "reside_unregistered_count": "Unregistered entire homes",
}


def _metric_label(col: str | None) -> str:
    if not col:
        return "value"
    return _METRIC_LABELS.get(col, col.replace("_", " ").capitalize())


def _fmt(v) -> str:
    if isinstance(v, bool):
        return str(v)
    if isinstance(v, float):
        if v.is_integer():
            return f"{int(v):,}"
        return f"{v:.2f}" if abs(v) < 1 else f"{v:,.1f}"
    if isinstance(v, int):
        return f"{v:,}"
    return str(v)


def _chart_theme() -> dict:
    """Colour palette for charts, mirroring the UI light/dark toggle.

    `text` styles titles and value labels; `muted` styles axis labels and ticks
    (in dark mode both are the same off-white, per spec).
    """
    if st.session_state.get("dark_mode", False):
        return {
            "fig_bg": "#1A1A24",   # figure background — matches the assistant bubble
            "ax_bg": "#222230",    # axes background — slightly lighter
            "text": "#E8E8F0",     # titles / value labels — off-white
            "muted": "#E8E8F0",    # axis labels / ticks — off-white
            "bar": "#1E49E2",      # cobalt (same as light)
            "bar2": "#9A9AB8",     # second compare bar — visible on near-black
            "grid": "#2A2A3A",     # subtle grid lines
        }
    return {
        "fig_bg": "#FFFFFF",
        "ax_bg": "#FFFFFF",
        "text": _NAVY,
        "muted": _SLATE,
        "bar": _COBALT,
        "bar2": _NAVY,
        "grid": _GRID,
    }


def _style_axes(ax, theme: dict) -> None:
    ax.set_facecolor(theme["ax_bg"])
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(theme["grid"])
    ax.tick_params(colors=theme["muted"], labelsize=9, length=0)
    ax.set_axisbelow(True)


def _hbar_fig(labels, values, value_label, title, max_bars=10):
    """Horizontal bar chart with the #1 result on top. Returns a Figure or None."""
    pairs = [(lab, v) for lab, v in zip(labels, values) if lab and v is not None]
    if not pairs:
        return None
    pairs = pairs[:max_bars][::-1]  # take top N, reverse so rank #1 sits at the top
    labels = [p[0] for p in pairs]
    values = [float(p[1]) for p in pairs]

    theme = _chart_theme()
    fig, ax = plt.subplots(figsize=(7.2, max(2.0, 0.5 * len(labels) + 0.7)), dpi=120)
    fig.patch.set_facecolor(theme["fig_bg"])
    ax.barh(labels, values, color=theme["bar"], height=0.62)
    ax.set_xlabel(value_label, fontsize=9, color=theme["muted"])
    ax.set_title(title, fontsize=11, fontweight="bold", loc="left", pad=10, color=theme["text"])
    ax.xaxis.grid(True, color=theme["grid"], linewidth=0.8)
    _style_axes(ax, theme)

    span = max(values) or 1.0
    for y, v in enumerate(values):
        ax.text(v + span * 0.012, y, _fmt(v), va="center", ha="left",
                fontsize=8, color=theme["text"])
    ax.set_xlim(0, span * 1.16)
    fig.tight_layout()
    return fig


def _vbar_compare_fig(cities, values, value_label, title):
    """Side-by-side Barcelona vs London comparison. Returns a Figure or None."""
    pairs = [(c, v) for c, v in zip(cities, values) if c and v is not None]
    if not pairs:
        return None
    cities = [p[0] for p in pairs]
    values = [float(p[1]) for p in pairs]
    theme = _chart_theme()
    colors = [theme["bar"], theme["bar2"]][: len(cities)]

    fig, ax = plt.subplots(figsize=(5.2, 3.5), dpi=120)
    fig.patch.set_facecolor(theme["fig_bg"])
    bars = ax.bar(cities, values, color=colors, width=0.55)
    ax.set_ylabel(value_label, fontsize=9, color=theme["muted"])
    ax.set_title(title, fontsize=11, fontweight="bold", loc="left", pad=10, color=theme["text"])
    ax.yaxis.grid(True, color=theme["grid"], linewidth=0.8)
    _style_axes(ax, theme)

    span = max(values) or 1.0
    for bar, v in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, v + span * 0.02, _fmt(v),
                ha="center", va="bottom", fontsize=9, color=theme["text"])
    ax.set_ylim(0, span * 1.2)
    fig.tight_layout()
    return fig


def _fig_for_tool(name: str, output: dict):
    """Build the right chart for a chartable tool result, else None."""
    if not isinstance(output, dict) or "error" in output:
        return None

    if name == "rank_neighbourhoods":
        metric = output.get("metric")
        rows = output.get("results") or []
        city = (output.get("city") or "").title()
        return _hbar_fig(
            [r.get("subdivision") for r in rows],
            [r.get(metric) for r in rows],
            _metric_label(metric),
            f"{city} — top areas by {_metric_label(metric).lower()}",
        )

    if name == "get_risk_tier_areas":
        rows = output.get("results") or []
        city = (output.get("city") or "").title()
        tier = output.get("tier")
        return _hbar_fig(
            [r.get("subdivision") for r in rows],
            [r.get("risk_priority_score") for r in rows],
            _metric_label("risk_priority_score"),
            f"{city} — Tier {tier} areas by risk priority score",
        )

    if name == "policy_simulation":
        cap = output.get("cap_nights")
        col = f"listings_impacted_{cap}"
        rows = output.get("top_impacted") or []
        city = (output.get("city") or "").title()
        return _hbar_fig(
            [r.get("subdivision") for r in rows],
            [r.get(col) for r in rows],
            _metric_label(col),
            f"{city} — most-impacted areas at a {cap}-night cap",
        )

    if name == "compare_cities":
        by_city = output.get("by_city") or {}
        metric = output.get("metric")
        use_total = output.get("metric_type") == "count"
        cities, values = [], []
        for c in ("barcelona", "london"):
            d = by_city.get(c) or {}
            if d.get("available") is False:
                continue
            val = d.get("total") if use_total else d.get("median")
            if val is None:
                val = d.get("median")
            cities.append(c.title())
            values.append(val)
        stat = "total" if use_total else "median"
        return _vbar_compare_fig(
            cities, values,
            f"{_metric_label(metric)} ({stat})",
            f"Barcelona vs London — {_metric_label(metric).lower()}",
        )

    return None


_CHARTABLE = {
    "rank_neighbourhoods",
    "get_risk_tier_areas",
    "policy_simulation",
    "compare_cities",
}


# --------------------------------------------------------------------------- #
# Choropleth maps (folium) + bubble charts (plotly) — additional inline views.
#
# Maps colour each neighbourhood by the metric from the tool result; bubbles read
# the full per-neighbourhood knowledge layer (tool results don't carry every column).
# All heavy imports are lazy and wrapped by the caller's try/except, so a missing
# dependency or unmatched geometry degrades to "no extra chart", never a crash.
# --------------------------------------------------------------------------- #
_RAW_DIR = REPO_ROOT / "data" / "raw"
_GEOJSON_PATHS = {
    "barcelona": _RAW_DIR / "Barcelona" / "Barcelona neighbourhoods.geojson",
    "london": _RAW_DIR / "London" / "London neighbourhoods.geojson",
}
_GEO_NAME_FIELD = "neighbourhood"  # confirmed: Barcelona matches the subdivision name


@st.cache_data(show_spinner=False)
def _load_geojson(city: str) -> dict | None:
    path = _GEOJSON_PATHS.get(city)
    if not path or not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _plotly_layout(fig, title: str):
    """Apply the light/dark consulting theme to a plotly figure (in place)."""
    dark = st.session_state.get("dark_mode", False)
    paper = "#1A1A24" if dark else "#FFFFFF"
    grid = "#2A2A3A" if dark else "#E0E4EA"
    text = "#E8E8F0" if dark else "#0B1F33"
    fig.update_layout(
        title=dict(text=title, font=dict(size=14)),
        paper_bgcolor=paper, plot_bgcolor=paper, font_color=text,
        margin=dict(l=10, r=10, t=44, b=10), legend_title_text="",
    )
    fig.update_xaxes(gridcolor=grid, zeroline=False)
    fig.update_yaxes(gridcolor=grid, zeroline=False)
    return fig


def _render_choropleth(name: str, output: dict, key: str) -> None:
    """Interactive choropleth for a single-city rank / risk-tier result.

    Colours each neighbourhood by the metric value from the tool result on a
    white→cobalt (light) / dark-navy→cobalt (dark) scale. Skips silently if the
    GeoJSON is missing or too few neighbourhoods match (e.g. London's borough-level
    boundaries vs. neighbourhood-level subdivisions).
    """
    if not isinstance(output, dict) or "error" in output:
        return
    city = output.get("city")
    geo = _load_geojson(city)
    if geo is None:
        return

    metric = "risk_priority_score" if name == "get_risk_tier_areas" else output.get("metric")
    rows = output.get("results") or []
    vals = {(r.get("subdivision") or r.get("borough")): r.get(metric) for r in rows if r.get(metric) is not None}
    if not vals:
        return

    import copy

    geo = copy.deepcopy(geo)  # don't mutate the cached object
    feats = geo["features"]
    n_match = sum(1 for f in feats if f["properties"].get(_GEO_NAME_FIELD) in vals)
    # Need a real overlap, else the map is misleading. London's GeoJSON is
    # borough-level while its subdivisions are neighbourhood-level, so only a few
    # names coincide (~3%) — those skip here; Barcelona matches ~80% and renders.
    if n_match < 2 or n_match / len(vals) < 0.3:
        return

    import folium
    import branca.colormap as cm
    from streamlit_folium import st_folium

    dark = st.session_state.get("dark_mode", False)
    nums = list(vals.values())
    vmin, vmax = min(nums), max(nums)
    if vmin == vmax:
        vmax = vmin + 1
    low_colour = "#0A0A0F" if dark else "#FFFFFF"
    colormap = cm.LinearColormap(
        [low_colour, "#1E49E2"], vmin=vmin, vmax=vmax, caption=_metric_label(metric)
    )
    no_data = "#222230" if dark else "#ECEFF3"
    edge = "#3A3A4A" if dark else "#C8CDD6"

    for f in feats:  # stash a display value for the tooltip
        nm = f["properties"].get(_GEO_NAME_FIELD)
        f["properties"]["_metric_value"] = _fmt(vals[nm]) if nm in vals else "n/a"

    def _style(feat):
        v = vals.get(feat["properties"].get(_GEO_NAME_FIELD))
        return {
            "fillColor": colormap(v) if v is not None else no_data,
            "color": edge, "weight": 0.5,
            "fillOpacity": 0.85 if v is not None else 0.15,
        }

    m = folium.Map(
        tiles="CartoDB dark_matter" if dark else "CartoDB positron",
        zoom_start=11, control_scale=False,
    )
    gj = folium.GeoJson(
        geo, style_function=_style,
        tooltip=folium.GeoJsonTooltip(
            fields=[_GEO_NAME_FIELD, "_metric_value"],
            aliases=["Neighbourhood", _metric_label(metric) + ":"],
        ),
    )
    gj.add_to(m)
    colormap.add_to(m)
    m.fit_bounds(gj.get_bounds())
    st.caption(f"🗺️ {city.title()} — {_metric_label(metric).lower()} by neighbourhood")
    st_folium(m, key=key, height=420, use_container_width=True, returned_objects=[])


def _render_bubble_compare(output: dict, key: str) -> None:
    """Bubble chart for compare_cities: STR density × breach rate, sized by listings,
    one bubble per neighbourhood, both cities (Barcelona red, London cobalt)."""
    if not isinstance(output, dict) or "error" in output:
        return
    df = T.load_knowledge_layer()
    metric = output.get("metric")
    y = metric if (metric and metric != "str_density" and metric in df.columns) else "breach_rate_90"
    if y not in df.columns and "breach_rate" in df.columns:
        y = "breach_rate"
    need = ["city", "subdivision", "str_density", "active_listings", y]
    if any(c not in df.columns for c in need):
        return
    sub = df[need].dropna(subset=["str_density", "active_listings", y])
    sub = sub[sub["active_listings"] > 0]
    if sub.empty:
        return

    import plotly.express as px

    sub = sub.assign(City=sub["city"].str.title())
    fig = px.scatter(
        sub, x="str_density", y=y, size="active_listings", color="City",
        hover_name="subdivision", size_max=42,
        color_discrete_map={"Barcelona": "#E63946", "London": "#1E49E2"},
        labels={"str_density": _metric_label("str_density"),
                y: _metric_label(y), "active_listings": "Active listings"},
    )
    fig.update_traces(marker=dict(line=dict(width=0), opacity=0.7))
    _plotly_layout(fig, f"Barcelona vs London — {_metric_label(y).lower()} vs STR density")
    st.plotly_chart(fig, use_container_width=True, key=key)


def _render_bubble_risk(output: dict, key: str) -> None:
    """Bubble chart for get_risk_tier_areas: STR density × risk score, sized by
    listings, coloured by risk tier (1 red, 2 amber, 3 green) across the city."""
    if not isinstance(output, dict) or "error" in output:
        return
    city = output.get("city")
    df = T.load_knowledge_layer()
    need = ["city", "subdivision", "str_density", "risk_priority_score",
            "active_listings", "risk_tier"]
    if any(c not in df.columns for c in need):
        return
    sub = df[df["city"] == city][need].dropna(
        subset=["str_density", "risk_priority_score", "active_listings"]
    )
    sub = sub[sub["active_listings"] > 0]
    if sub.empty:
        return

    import plotly.express as px

    tier_label = {1: "Tier 1", 2: "Tier 2", 3: "Tier 3"}
    sub = sub.assign(Tier=sub["risk_tier"].map(tier_label).fillna("—"))
    fig = px.scatter(
        sub, x="str_density", y="risk_priority_score", size="active_listings",
        color="Tier", hover_name="subdivision", size_max=42,
        color_discrete_map={"Tier 1": "#E63946", "Tier 2": "#F4A261", "Tier 3": "#2A9D8F"},
        category_orders={"Tier": ["Tier 1", "Tier 2", "Tier 3"]},
        labels={"str_density": _metric_label("str_density"),
                "risk_priority_score": _metric_label("risk_priority_score"),
                "active_listings": "Active listings"},
    )
    fig.update_traces(marker=dict(line=dict(width=0), opacity=0.75))
    _plotly_layout(fig, f"{city.title()} — risk score vs STR density (by tier)")
    st.plotly_chart(fig, use_container_width=True, key=key)


def render_tool_charts(trace, key_prefix: str = "c") -> None:
    """Render the inline charts beneath the answer for each chartable tool call:
    the bar chart first, then (where relevant) a choropleth map and/or bubble chart.
    `key_prefix` keeps folium/plotly widget keys unique across chat messages."""
    if not trace:
        return
    for idx, t in enumerate(trace):
        name, output = t.get("name"), t.get("output")
        if name not in _CHARTABLE:
            continue

        # 1) Bar chart (existing).
        try:
            fig = _fig_for_tool(name, output)
        except Exception:  # noqa: BLE001 — a chart must never break the chat
            fig = None
        if fig is not None:
            st.pyplot(fig)
            plt.close(fig)

        # 2) Choropleth map — single-city ranked / risk-tier results.
        if name in ("rank_neighbourhoods", "get_risk_tier_areas"):
            try:
                _render_choropleth(name, output, key=f"{key_prefix}_map_{idx}")
            except Exception:  # noqa: BLE001
                pass

        # 3) Bubble chart — comparison and risk-tier results.
        if name == "compare_cities":
            try:
                _render_bubble_compare(output, key=f"{key_prefix}_bub_{idx}")
            except Exception:  # noqa: BLE001
                pass
        elif name == "get_risk_tier_areas":
            try:
                _render_bubble_risk(output, key=f"{key_prefix}_bub_{idx}")
            except Exception:  # noqa: BLE001
                pass


# --------------------------------------------------------------------------- #
# Streamlit UI
# --------------------------------------------------------------------------- #
st.set_page_config(
    page_title="UrbanLens",
    page_icon="🏙️",  # browser-tab favicon only; the in-app title carries no emoji
    layout="centered",
)

# Theme state — light by default; the sidebar toggle flips it within the session.
st.session_state.setdefault("dark_mode", False)
_dark = st.session_state["dark_mode"]

# --------------------------------------------------------------------------- #
# Presentation layer — consulting aesthetic (navy/white/cobalt, flat, minimal).
# Colours flow from CSS variables so light/dark mode is a single palette swap; the
# accent (cobalt #1E49E2) is constant across both. Styling only; no behaviour
# depends on it. Pairs with .streamlit/config.toml.
# --------------------------------------------------------------------------- #
_PALETTE_LIGHT = {
    "bg": "#F7FAFC",          # app background
    "sidebar-bg": "#FFFFFF",  # sidebar (split from surface for the dark theme)
    "surface": "#FFFFFF",     # cards, bubbles, input
    "text": "#0B1F33",        # primary text
    "brand": "#0B1F33",       # the "Urban" wordmark
    "muted": "#5B6B7C",       # secondary text
    "border": "#E0E4EA",
    "kv-border": "#F0F2F6",
    "accent": "#1E49E2",      # cobalt — constant in both modes
    "user-bg": "#EEF2FF",     # user chat bubble
    "user-border": "#D6E0FF",
    "btn-hover-bg": "#EEF2FF",
    "placeholder": "#9AA7B4",
    "note-bg": "#FFF8E6",
    "note-border": "#F2E2B3",
    "note-text": "#8A5A00",
}
_PALETTE_DARK = {
    "bg": "#0A0A0F",          # main background — near black
    "sidebar-bg": "#111118",  # sidebar
    "surface": "#1A1A24",     # cards, chat bubbles, input
    "text": "#E8E8F0",        # primary text
    "brand": "#E8E8F0",
    "muted": "#9A9AB8",
    "border": "#2A2A3A",
    "kv-border": "#222230",
    "accent": "#1E49E2",      # cobalt — constant in both modes
    "user-bg": "#20253A",     # user chat bubble — subtle cobalt tint
    "user-border": "#2E3A5A",
    "btn-hover-bg": "#20202E",
    "placeholder": "#6B6B8A",
    "note-bg": "#2A2410",
    "note-border": "#4A3F1A",
    "note-text": "#E8C66A",
}

_BASE_CSS = """
      /* ---------- Global ---------- */
      html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                     Helvetica, Arial, sans-serif;
        color: var(--text);
      }
      [data-testid="stAppViewContainer"] { background: var(--bg); }
      [data-testid="stHeader"] { background: transparent; }
      [data-testid="stDecoration"] { display: none; }            /* drop the rainbow bar */
      [data-testid="stMainBlockContainer"] { padding-top: 2.5rem; max-width: 1080px; }

      /* ---------- Header ---------- */
      .uric-header { margin-bottom: 1.75rem; }
      .uric-header h1 {
        <div style="display:flex; align-items:flex-end; gap:0.75rem; margin-bottom:0.35rem;">
        font-size: 1.95rem; font-weight: 700; letter-spacing: -0.01em;
        margin: 0 0 0.35rem 0; line-height: 1.2;
      }
      .uric-logo { width: 1.55rem; height: 1.55rem; flex: 0 0 auto; }
      .uric-brand { color: var(--brand); }       /* "Urban" — navy / off-white */
      .uric-brand-accent { color: var(--accent); }   /* "Lens" — cobalt accent */
      .uric-header p {
        font-size: 0.95rem; color: var(--muted); margin: 0 0 0.9rem 0; line-height: 1.45;
      }
      .uric-rule {
        height: 3px; width: 120px; border-radius: 2px;
        background: linear-gradient(90deg, var(--accent) 0%, rgba(30, 73, 226, 0) 100%);
      }

      /* ---------- Sidebar ---------- */
      [data-testid="stSidebar"] { background: var(--sidebar-bg); border-right: 1px solid var(--border); }
      .uric-label {
        font-size: 0.7rem; font-weight: 700; text-transform: uppercase;
        letter-spacing: 0.12em; color: var(--muted); margin: 0 0 0.6rem 0;
      }
      .uric-kv {
        display: flex; justify-content: space-between; gap: 1rem;
        font-size: 0.85rem; padding: 0.32rem 0; border-bottom: 1px solid var(--kv-border);
      }
      .uric-kv span { color: var(--muted); white-space: nowrap; }
      .uric-kv b { color: var(--accent); font-weight: 600; text-align: right; word-break: break-word; }
      .uric-note {
        font-size: 0.8rem; color: var(--note-text); background: var(--note-bg);
        border: 1px solid var(--note-border); padding: 0.5rem 0.6rem; margin-top: 0.7rem; line-height: 1.4;
      }
      .uric-divider { height: 1px; background: var(--border); margin: 1.7rem 0; }
      .uric-list { font-size: 0.85rem; }
      .uric-list > div {
        padding: 0.5rem 0 0.5rem 0.85rem; border-left: 2px solid var(--accent);
        margin-bottom: 0.5rem; line-height: 1.45; color: var(--text);
      }

      /* ---------- Buttons ---------- */
      .stButton button {
        border-radius: 2px; border: 1px solid var(--accent); background: var(--surface);
        color: var(--accent); font-weight: 600; font-size: 0.85rem; padding: 0.4rem 0.9rem;
        transition: all 0.15s ease;
      }
      .stButton button:hover { background: var(--accent); color: #FFFFFF; }
      /* Example-question buttons read as a left-aligned list, not centred CTAs. */
      [data-testid="stSidebar"] .stButton button {
        text-align: left; justify-content: flex-start; line-height: 1.3; margin-bottom: 0.35rem;
      }
      /* Subtle cobalt-tint on hover so they feel clickable (not a full fill). */
      [data-testid="stSidebar"] .stButton button:hover {
        background: var(--btn-hover-bg); color: var(--accent); border-color: var(--accent);
      }
      .uric-list b { color: var(--accent); font-weight: 600; }

      /* ---------- Chat messages ---------- */
      /* Avatars stay in the DOM (needed by the :has() selectors) but are hidden. */
      [data-testid="stChatMessageAvatarUser"],
      [data-testid="stChatMessageAvatarAssistant"] { display: none; }

      [data-testid="stChatMessage"] {
        width: fit-content; max-width: 82%; border-radius: 2px;
        padding: 0.9rem 1.15rem; margin: 0.55rem 0;
        box-shadow: 0 1px 2px rgba(11, 31, 51, 0.04);
      }
      /* Assistant: left-aligned, surface fill, thin cobalt left border */
      [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
        background: var(--surface); border: 1px solid var(--border); border-left: 3px solid var(--accent);
        margin-right: auto;
      }
      /* User: right-aligned, cobalt-tinted fill */
      [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
        background: var(--user-bg); border: 1px solid var(--user-border); margin-left: auto;
      }
      [data-testid="stChatMessage"] p { font-size: 0.92rem; line-height: 1.55; }

      /* ---------- Chat input ---------- */
      [data-testid="stBottom"] { background: transparent; }
      [data-testid="stBottomBlockContainer"] { background: transparent; }
      [data-testid="stChatInput"] {
        border: 1px solid var(--border); border-radius: 2px; background: var(--surface);
      }
      [data-testid="stChatInput"]:focus-within {
        border-color: var(--accent); box-shadow: 0 0 0 1px var(--accent);
      }
      /* Force the inner input/textarea to the theme — Streamlit otherwise leaves
         these light. !important beats Streamlit's own inline/base styles. */
      .stTextInput input,
      .stChatInput textarea,
      [data-testid="stChatInput"] textarea,
      [data-testid="stChatInputTextArea"] {
        background: var(--surface) !important;
        color: var(--text) !important;
        border-color: var(--border) !important;
        -webkit-text-fill-color: var(--text) !important;
      }
      .stTextInput input::placeholder,
      .stChatInput textarea::placeholder,
      [data-testid="stChatInput"] textarea::placeholder,
      [data-testid="stChatInputTextArea"]::placeholder {
        color: var(--placeholder) !important;
        -webkit-text-fill-color: var(--placeholder) !important;
      }

      /* ---------- Tool-call expander ---------- */
      [data-testid="stExpander"] {
        border: 1px solid var(--border); border-radius: 2px; background: var(--surface);
      }
      [data-testid="stExpander"] summary { font-size: 0.82rem; color: var(--muted); }
"""

# Dark-mode-only overrides. Injected solely when dark is active, so light mode is
# never touched. These use hard-coded hex + !important to beat Streamlit's own base
# styles on the bottom chat-input container and the sidebar text colour.
_DARK_OVERRIDE_CSS = """
      /* Outer bottom bar — the strip the input floats in. */
      [data-testid="stBottom"],
      [data-testid="stBottom"] > div,
      section[data-testid="stBottom"],
      [data-testid="stBottomBlockContainer"],
      .stChatFloatingInputContainer,
      .stChatInputContainer {
        background-color: #0A0A0F !important;
        border-top: 1px solid #2A2A3A !important;
      }
      /* The white pill is [data-testid="stChatInput"] itself plus its inner wrapper
         divs — Streamlit's emotion CSS keeps them white, so override by testid with
         !important (a class*="stChatInput" selector matches nothing — Streamlit uses
         st-emotion-cache-* classes). */
      [data-testid="stChatInput"],
      [data-testid="stChatInput"] > div,
      [data-testid="stChatInput"] div {
        background-color: #1A1A24 !important;
        border-color: #2A2A3A !important;
      }
      /* The text field. */
      [data-testid="stChatInput"] textarea,
      [data-testid="stChatInputTextArea"],
      .stChatInput textarea {
        background-color: #1A1A24 !important;
        color: #E8E8F0 !important;
      }
      /* Submit button + arrow icon — keep them visible on the dark pill. */
      [data-testid="stChatInput"] button,
      [data-testid="stChatInputSubmitButton"] {
        background-color: #1A1A24 !important;
      }
      [data-testid="stChatInput"] button svg,
      [data-testid="stChatInput"] button path,
      [data-testid="stChatInputSubmitButton"] svg,
      [data-testid="stChatInputSubmitButton"] path {
        fill: #E8E8F0 !important;
        color: #E8E8F0 !important;
      }
      /* Sidebar text → off-white so labels are legible... */
      [data-testid="stSidebar"] * {
        color: #E8E8F0 !important;
      }
      /* ...but keep cobalt for the accent value bolds, and amber for the note. */
      [data-testid="stSidebar"] .uric-kv b,
      [data-testid="stSidebar"] .uric-list b {
        color: #1E49E2 !important;
      }
      [data-testid="stSidebar"] .uric-note {
        color: #E8C66A !important;
      }
      /* Assistant/user chat bubble text → off-white so it's readable on the dark
         surface (the var(--text)-driven rule isn't winning over Streamlit's base). */
      [data-testid="stChatMessage"] p,
      [data-testid="stChatMessage"] li,
      [data-testid="stChatMessage"] span,
      [data-testid="stChatMessage"] div,
      .stChatMessage p,
      .stChatMessage li,
      .stChatMessage span {
        color: #E8E8F0 !important;
      }
      /* Inline markdown inside bubbles: bold, italic, links, and code. */
      [data-testid="stChatMessage"] strong,
      [data-testid="stChatMessage"] b,
      [data-testid="stChatMessage"] em,
      [data-testid="stChatMessage"] i,
      [data-testid="stChatMessage"] a,
      [data-testid="stChatMessage"] code,
      [data-testid="stChatMessage"] pre {
        color: #E8E8F0 !important;
      }
      /* Tool-call expander: header label and the JSON/markdown inside it. */
      [data-testid="stExpander"] summary,
      [data-testid="stExpander"] p,
      [data-testid="stExpander"] li,
      [data-testid="stExpander"] span,
      [data-testid="stExpander"] div,
      [data-testid="stExpander"] code,
      [data-testid="stExpander"] pre {
        color: #E8E8F0 !important;
      }
"""

_palette = _PALETTE_DARK if _dark else _PALETTE_LIGHT
_root_vars = ":root {\n" + "\n".join(f"  --{k}: {v};" for k, v in _palette.items()) + "\n}\n"
st.markdown(
    "<style>\n" + _root_vars + _BASE_CSS + (_DARK_OVERRIDE_CSS if _dark else "") + "</style>",
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="uric-header">
      <div style="display:flex; flex-direction:row; align-items:center; gap:0.75rem; margin-bottom:0.75rem;">
        <svg style="width:3rem; height:3rem; flex:0 0 auto;" viewBox="0 0 48 48" fill="none"
             xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
          <defs><clipPath id="lc"><circle cx="21" cy="21" r="15"/></clipPath></defs>
          <g clip-path="url(#lc)">
            <rect x="11" y="20" width="4" height="16" fill="var(--brand)"/>
            <rect x="17" y="14" width="4" height="22" fill="var(--brand)" opacity="0.6"/>
            <rect x="23" y="9"  width="4" height="27" fill="var(--brand)"/>
            <rect x="29" y="13" width="4" height="23" fill="var(--brand)" opacity="0.6"/>
            <rect x="12" y="22" width="2" height="1.5" fill="#E8006E"/>
            <rect x="23" y="11" width="2" height="1.5" fill="#E8006E"/>
          </g>
          <circle cx="21" cy="21" r="15" stroke="#E8006E" stroke-width="2.5"/>
          <line x1="32" y1="32" x2="43" y2="43" stroke="#E8006E" stroke-width="3" stroke-linecap="round"/>
          <circle cx="43" cy="43" r="2.5" fill="#E8006E"/>
        </svg>
        <div style="display:flex; flex-direction:column; gap:2px;">
          <div style="font-size:1.95rem; font-weight:700; letter-spacing:-0.01em; line-height:1.1;">
            <span class="uric-brand">Urban</span>&nbsp;<span class="uric-brand-accent">Lens</span>
          </div>
          <div style="font-size:0.6rem; font-weight:700; letter-spacing:0.15em; color:var(--muted); text-transform:uppercase;">Short-Term Rental Intelligence</div>
        </div>
      </div>
      <p>AI-powered policy advisor for short-term-rental regulation — Barcelona
         &amp; London. Risk-tiered priorities, every figure tool-sourced.</p>
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
    # Theme toggle — flips st.session_state["dark_mode"], which the CSS above reads
    # on the next rerun to swap the palette.
    st.toggle(
        "🌙 Dark mode",
        key="dark_mode",
        help="Switch between the light and dark consulting themes.",
    )
    st.markdown('<div class="uric-divider"></div>', unsafe_allow_html=True)

    _status = T.knowledge_layer_status()

    st.markdown('<div class="uric-label">Key Data</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="uric-kv"><span>Barcelona</span><b>2,594 listings</b></div>'
        '<div class="uric-kv"><span>London</span><b>9,643 listings</b></div>'
        '<div class="uric-kv"><span>Coverage</span><b>Mar 2021 – Feb 2026</b></div>'
        f'<div class="uric-kv"><span>Cities</span>'
        f'<b>{", ".join(c.title() for c in _status["cities"])}</b></div>',
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

for _mi, msg in enumerate(st.session_state.display):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("trace"):
            render_tool_charts(msg["trace"], key_prefix=f"h{_mi}")
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
                "Could not initialise the Anthropic client — set ANTHROPIC_API_KEY "
                f"(in .env or the environment). Details: {e}"
            )
            st.stop()

        with st.spinner("Querying the knowledge layer…"):
            answer, trace = chat_turn(client, build_system_prompt(), st.session_state.history)

        st.markdown(answer)
        if trace:
            render_tool_charts(trace, key_prefix=f"live{len(st.session_state.display)}")
            with st.expander(f"🔧 {len(trace)} tool call(s)"):
                for t in trace:
                    st.markdown(f"**`{t['name']}`** — input: `{t['input']}`")
                    st.json(t["output"], expanded=False)

    st.session_state.history.append({"role": "assistant", "content": answer})
    st.session_state.display.append({"role": "assistant", "content": answer, "trace": trace})
