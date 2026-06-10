"""app/tools.py — knowledge-layer query tools for the Urban Rental Intelligence Copilot.

The Claude model calls these tools; this module returns structured results from the
knowledge layer (and the regulatory corpus). The model then turns those results into
a cited, natural-language answer. The model is told to invent nothing — so every
function here returns either real data or an explicit "not available" signal. There
are no silent defaults and no fabricated zeros.

Two design decisions worth knowing about
----------------------------------------
1. Schema aliasing. Member 3 ships the final ``data/processed/knowledge_layer.csv``
   (columns: ``subdivision, breach_rate, risk_priority_score, cluster_label,
   listings_impacted_90/60/30`` ...). Until then the live file is Member 2's
   ``neighbourhood_kpis.csv`` (columns: ``geo_key, breach_rate_90, breach_count_90``
   ..., and *no* risk/cluster columns). ``_CANON`` below maps both layouts onto one
   canonical name set, so this module works against whichever file is present and
   keeps working after M3's handover. Missing columns are reported, never faked.

2. RAG is retrieval-only. ``query_regulations`` returns the most relevant passages
   (TF-IDF over the corpus) with their source citations. It does NOT call an LLM —
   the orchestrating model in ``streamlit_app.py`` synthesises the grounded answer.
   This keeps tools.py pure, fast and unit-testable, and keeps all model calls in
   one place.
"""
from __future__ import annotations

import re
import unicodedata
from functools import lru_cache
from pathlib import Path

import pandas as pd

# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #
REPO_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = REPO_ROOT / "data" / "processed"
REGULATIONS_DIR = REPO_ROOT / "data" / "regulations"

# Preferred file first. The first one that exists wins.
_KNOWLEDGE_LAYER_CANDIDATES = (
    PROCESSED_DIR / "knowledge_layer.csv",      # Member 3's final deliverable
    PROCESSED_DIR / "neighbourhood_kpis.csv",   # Member 2's current file (fallback)
)

VALID_CITIES = ("barcelona", "london")
DEFAULT_MIN_DENSITY = 30  # matches the golden-answers Q2/Q3 density floor
VALID_CAPS = (90, 60, 30)
VALID_CLUSTERS = ("saturated", "emerging", "low_impact")  # Member 3's KMeans labels

# --------------------------------------------------------------------------- #
# Canonical schema: canonical_name -> tuple of accepted source column names
# (checked in order; first match wins). Add new aliases here, never in the tools.
# --------------------------------------------------------------------------- #
_CANON: dict[str, tuple[str, ...]] = {
    "city": ("city",),
    "subdivision": ("subdivision", "geo_key", "neighborhood", "neighbourhood"),
    "geo_level": ("geo_level",),
    "str_density": ("str_density",),
    "active_listings": ("active_listings",),
    "entire_home_count": ("entire_home_count",),
    "entire_home_share": ("entire_home_share",),
    "commercial_host_share": ("commercial_host_share",),
    "multi_listing_host_share": ("multi_listing_host_share",),
    "median_nightly_price": ("median_nightly_price",),
    "avg_occupancy": ("avg_occupancy",),
    "total_revenue": ("total_revenue",),
    # single breach_rate (M3) OR per-cap (M2). breach_rate aliases to the 90-night rate.
    "breach_rate": ("breach_rate", "breach_rate_90"),
    "breach_rate_90": ("breach_rate_90", "breach_rate"),
    "breach_rate_60": ("breach_rate_60",),
    "breach_rate_30": ("breach_rate_30",),
    # listings impacted at a cap (M3) == breach_count at that cap (M2)
    "listings_impacted_90": ("listings_impacted_90", "breach_count_90"),
    "listings_impacted_60": ("listings_impacted_60", "breach_count_60"),
    "listings_impacted_30": ("listings_impacted_30", "breach_count_30"),
    "reside_unregistered_count": ("reside_unregistered_count",),
    "professional_management_share": ("professional_management_share",),
    # M3-only — absent in the fallback file. Tools must check before using.
    "risk_priority_score": ("risk_priority_score",),
    "cluster_label": ("cluster_label",),
}

# Metrics a user / the model may rank or compare by -> canonical column.
RANKABLE_METRICS: dict[str, str] = {
    "str_density": "str_density",
    "entire_home_share": "entire_home_share",
    "commercial_host_share": "commercial_host_share",
    "multi_listing_host_share": "multi_listing_host_share",
    "median_nightly_price": "median_nightly_price",
    "avg_occupancy": "avg_occupancy",
    "breach_rate_90": "breach_rate_90",
    "breach_rate": "breach_rate",
    "risk_priority_score": "risk_priority_score",
    "listings_impacted_90": "listings_impacted_90",
    "reside_unregistered_count": "reside_unregistered_count",
}


# --------------------------------------------------------------------------- #
# Loading + normalisation
# --------------------------------------------------------------------------- #
def _source_path() -> Path:
    for candidate in _KNOWLEDGE_LAYER_CANDIDATES:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        "No knowledge layer found. Expected one of: "
        + ", ".join(str(p) for p in _KNOWLEDGE_LAYER_CANDIDATES)
    )


@lru_cache(maxsize=1)
def load_knowledge_layer() -> pd.DataFrame:
    """Load the knowledge layer and rename columns to the canonical schema.

    Cached for the process lifetime. Call ``load_knowledge_layer.cache_clear()``
    after the file changes (e.g. when M3 re-runs the pipeline).
    """
    path = _source_path()
    df = pd.read_csv(path, encoding="utf-8")

    rename: dict[str, str] = {}
    for canon, aliases in _CANON.items():
        if canon in df.columns:
            continue  # already canonical
        for alias in aliases:
            if alias in df.columns:
                rename[alias] = canon
                break
    df = df.rename(columns=rename)

    if "city" in df.columns:
        df["city"] = df["city"].astype(str).str.strip().str.lower()
    # Tag provenance so the app can show which file is backing it.
    df.attrs["source_file"] = path.name
    return df


def knowledge_layer_status() -> dict:
    """Diagnostics for the app's 'About' page: which file, which columns are missing."""
    df = load_knowledge_layer()
    present = set(df.columns)
    missing_optional = [c for c in ("risk_priority_score", "cluster_label") if c not in present]
    return {
        "source_file": df.attrs.get("source_file"),
        "rows": int(len(df)),
        "columns": sorted(present),
        "cities": sorted(df["city"].unique().tolist()) if "city" in present else [],
        "missing_member3_columns": missing_optional,
        "ready_for_q5_clustering": "cluster_label" in present,
    }


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _validate_city(city: str) -> str | None:
    c = (city or "").strip().lower()
    return c if c in VALID_CITIES else None


def _require_column(df: pd.DataFrame, col: str) -> dict | None:
    """Return an error dict if ``col`` is absent, else None."""
    if col not in df.columns:
        return {
            "error": "column_not_available",
            "column": col,
            "detail": (
                f"'{col}' is not in the current knowledge layer "
                f"({df.attrs.get('source_file')}). It is produced by Member 3 and "
                "is not available yet."
            ),
        }
    return None


def _clean_records(rows: pd.DataFrame, cols: list[str]) -> list[dict]:
    """Serialise rows -> list of dicts, turning NaN into None (never a fake 0)."""
    out = rows[cols].where(pd.notna(rows[cols]), None)
    records = out.to_dict("records")
    for r in records:
        for k, v in r.items():
            if isinstance(v, float) and v.is_integer():
                r[k] = int(v)
    return records


# --------------------------------------------------------------------------- #
# Core tool 1: get_neighbourhood_metrics
# --------------------------------------------------------------------------- #
def get_neighbourhood_metrics(city: str, subdivision: str) -> dict:
    """Return all KPIs for one named neighbourhood/subdivision in a city.

    Use when the user asks about a specific named area (e.g. "el Raval",
    "Westminster"). Matching is accent- and case-insensitive.
    """
    c = _validate_city(city)
    if c is None:
        return {"error": "invalid_city", "detail": f"city must be one of {VALID_CITIES}"}

    df = load_knowledge_layer()
    sub = df[df["city"] == c]

    target = _norm(subdivision)
    mask = sub["subdivision"].map(_norm) == target
    if not mask.any():  # fall back to substring contains
        mask = sub["subdivision"].map(_norm).str.contains(re.escape(target), na=False)
    matches = sub[mask]

    if matches.empty:
        return {
            "error": "not_found",
            "city": c,
            "query": subdivision,
            "detail": "No matching subdivision. Use list_subdivisions to see valid names.",
            "suggestions": _closest_subdivisions(sub, target, n=5),
        }
    if len(matches) > 1:
        return {
            "ambiguous": True,
            "city": c,
            "query": subdivision,
            "matches": matches["subdivision"].tolist(),
        }

    row = matches.iloc[[0]]
    metric_cols = [c for c in df.columns if c not in ("city", "geo_level")]
    return {"city": c, "metrics": _clean_records(row, metric_cols)[0]}


# --------------------------------------------------------------------------- #
# Core tool 2: rank_neighbourhoods
# --------------------------------------------------------------------------- #
def rank_neighbourhoods(
    city: str, metric: str, top_n: int = 10, min_density: int = DEFAULT_MIN_DENSITY
) -> dict:
    """Return the top-N subdivisions in a city by a given metric.

    Use for "which neighbourhoods have the highest X" questions (Q1–Q4).
    ``min_density`` filters out thinly-sampled areas (default 30, matching the
    golden-answers methodology). Rows where the metric is null are dropped.
    """
    c = _validate_city(city)
    if c is None:
        return {"error": "invalid_city", "detail": f"city must be one of {VALID_CITIES}"}
    if metric not in RANKABLE_METRICS:
        return {
            "error": "invalid_metric",
            "detail": f"metric must be one of {sorted(RANKABLE_METRICS)}",
        }

    df = load_knowledge_layer()
    col = RANKABLE_METRICS[metric]
    if (err := _require_column(df, col)) is not None:
        return err

    sub = df[df["city"] == c].copy()
    if "str_density" in sub.columns and min_density:
        sub = sub[sub["str_density"] >= min_density]
    sub = sub.dropna(subset=[col])

    top_n = max(1, min(int(top_n), 50))
    ranked = sub.nlargest(top_n, col)

    keep = ["subdivision", col]
    for extra in ("str_density", "entire_home_count"):
        if extra in ranked.columns and extra not in keep:
            keep.append(extra)
    records = _clean_records(ranked, keep)
    for i, r in enumerate(records, start=1):
        r["rank"] = i
    return {
        "city": c,
        "metric": col,
        "min_density": min_density,
        "count": len(records),
        "results": records,
    }


# --------------------------------------------------------------------------- #
# Core tool 3: compare_cities
# --------------------------------------------------------------------------- #
def compare_cities(metric: str) -> dict:
    """Side-by-side comparison of Barcelona vs London for one metric (Q6).

    Returns per-city total (sum) for count-like metrics and median for rate/price
    metrics, plus the neighbourhood-level median either way.
    """
    if metric not in RANKABLE_METRICS:
        return {
            "error": "invalid_metric",
            "detail": f"metric must be one of {sorted(RANKABLE_METRICS)}",
        }
    df = load_knowledge_layer()
    col = RANKABLE_METRICS[metric]
    if (err := _require_column(df, col)) is not None:
        return err

    is_countlike = col in (
        "str_density",
        "active_listings",
        "entire_home_count",
        "listings_impacted_90",
        "listings_impacted_60",
        "listings_impacted_30",
        "reside_unregistered_count",
    )
    out: dict[str, dict] = {}
    for c in VALID_CITIES:
        sub = df[df["city"] == c][col].dropna()
        if sub.empty:
            out[c] = {"available": False}
            continue
        stats = {
            "n_neighbourhoods": int(sub.shape[0]),
            "median": round(float(sub.median()), 4),
        }
        if is_countlike:
            stats["total"] = int(sub.sum())
        out[c] = stats
    return {"metric": col, "metric_type": "count" if is_countlike else "rate/price", "by_city": out}


# --------------------------------------------------------------------------- #
# Core tool 4: policy_simulation
# --------------------------------------------------------------------------- #
def policy_simulation(city: str, cap_nights: int, top_n: int = 10) -> dict:
    """Estimate the impact of an annual entire-home night cap (Q7 — standout feature).

    Returns the total listings that would breach the cap in the AirDNA sample, plus
    the most-impacted subdivisions. For Barcelona it also reports
    ``reside_unregistered`` counts (entire homes with no registration on record) —
    regulatorily meaningful for the RESIDE phase-out. For London, reside figures are
    NOT a regulatory breach and are omitted.
    """
    c = _validate_city(city)
    if c is None:
        return {"error": "invalid_city", "detail": f"city must be one of {VALID_CITIES}"}
    try:
        cap = int(cap_nights)
    except (TypeError, ValueError):
        cap = -1
    if cap not in VALID_CAPS:
        return {"error": "invalid_cap", "detail": f"cap_nights must be one of {VALID_CAPS}"}

    df = load_knowledge_layer()
    col = f"listings_impacted_{cap}"
    if (err := _require_column(df, col)) is not None:
        return err

    sub = df[df["city"] == c].copy().dropna(subset=[col])
    top_n = max(1, min(int(top_n), 50))
    top = sub.nlargest(top_n, col)

    result: dict = {
        "city": c,
        "cap_nights": cap,
        "total_listings_impacted": int(sub[col].sum()),
        "top_impacted": _clean_records(top, ["subdivision", col]),
        "basis": "AirDNA sample — not the full market",
    }
    if c == "barcelona" and "reside_unregistered_count" in df.columns:
        rsub = sub.dropna(subset=["reside_unregistered_count"])
        rtop = rsub.nlargest(top_n, "reside_unregistered_count")
        result["reside_simulation"] = {
            "total_unregistered_entire_homes": int(rsub["reside_unregistered_count"].sum()),
            "top_subdivisions": _clean_records(rtop, ["subdivision", "reside_unregistered_count"]),
            "note": "RESIDE phase-out context — entire homes without registration on record.",
        }
    return result


# --------------------------------------------------------------------------- #
# Core tool 5: list_subdivisions
# --------------------------------------------------------------------------- #
def list_subdivisions(city: str) -> dict:
    """Return all valid subdivision names for a city. Use to fuzzy-match user input."""
    c = _validate_city(city)
    if c is None:
        return {"error": "invalid_city", "detail": f"city must be one of {VALID_CITIES}"}
    df = load_knowledge_layer()
    names = sorted(df[df["city"] == c]["subdivision"].dropna().unique().tolist())
    return {"city": c, "count": len(names), "subdivisions": names}


# --------------------------------------------------------------------------- #
# Core tool 5b: list_by_cluster (Member 3's KMeans clusters — Q5)
# --------------------------------------------------------------------------- #
def list_by_cluster(city: str, cluster_label: str | None = None, top_n: int = 10) -> dict:
    """List a city's subdivisions by KMeans cluster ('saturated' / 'emerging' /
    'low_impact'), ordered by risk_priority_score. Use for Q5 — "which neighbourhoods
    are saturated, and which are emerging hotspots". Omit cluster_label to get cluster
    counts plus the top of each cluster.

    Returns ``column_not_available`` if the knowledge layer lacks cluster_label (i.e.
    Member 3's clustering has not been merged yet).
    """
    c = _validate_city(city)
    if c is None:
        return {"error": "invalid_city", "detail": f"city must be one of {VALID_CITIES}"}
    df = load_knowledge_layer()
    if (err := _require_column(df, "cluster_label")) is not None:
        return err

    sub = df[df["city"] == c].copy()
    has_risk = "risk_priority_score" in sub.columns
    keep = ["subdivision", "cluster_label"]
    for extra in ("risk_priority_score", "str_density", "entire_home_share"):
        if extra in sub.columns:
            keep.append(extra)
    cap = max(1, min(int(top_n), 50))

    def _ordered(rows):
        return rows.sort_values("risk_priority_score", ascending=False) if has_risk else rows

    if cluster_label is None:
        by_cluster = {}
        for cl in sorted(sub["cluster_label"].dropna().unique()):
            by_cluster[cl] = _clean_records(_ordered(sub[sub["cluster_label"] == cl]).head(cap), keep)
        return {
            "city": c,
            "cluster_counts": sub["cluster_label"].value_counts().to_dict(),
            "by_cluster": by_cluster,
        }

    cl = str(cluster_label).strip().lower()
    if cl not in VALID_CLUSTERS:
        return {"error": "invalid_cluster", "detail": f"cluster_label must be one of {VALID_CLUSTERS}"}
    rows = _ordered(sub[sub["cluster_label"] == cl])
    return {
        "city": c,
        "cluster": cl,
        "count": int(len(rows)),
        "results": _clean_records(rows.head(cap), keep),
    }


# --------------------------------------------------------------------------- #
# Tool 6: query_regulations — lightweight RAG over the regulatory corpus
# --------------------------------------------------------------------------- #
_CITY_REG_LABEL = {
    "barcelona": "Barcelona — Plan RESIDE / STR regulations",
    "london": "London — Deregulation Act 2015 (90-night rule)",
}


def _norm(text: str) -> str:
    """Lowercase, strip accents — for robust name/text matching."""
    text = unicodedata.normalize("NFKD", str(text))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return text.strip().lower()


def _closest_subdivisions(sub: pd.DataFrame, target: str, n: int = 5) -> list[str]:
    names = sub["subdivision"].dropna().unique().tolist()
    scored = sorted(names, key=lambda s: (target not in _norm(s), len(s)))
    return scored[:n]


def _load_regulation_chunks(city: str) -> list[dict]:
    """Read + paragraph-chunk every .txt/.md/.pdf under data/regulations/<city>/."""
    city_dir = REGULATIONS_DIR / city
    if not city_dir.exists():
        return []
    chunks: list[dict] = []
    for path in sorted(city_dir.iterdir()):
        if path.name.startswith("."):
            continue
        text = ""
        if path.suffix.lower() in (".txt", ".md"):
            text = path.read_text(encoding="utf-8", errors="ignore")
        elif path.suffix.lower() == ".pdf":
            try:
                import pdfplumber

                with pdfplumber.open(path) as pdf:
                    text = "\n\n".join((pg.extract_text() or "") for pg in pdf.pages)
            except Exception:  # noqa: BLE001 — corrupt/locked PDF shouldn't kill the tool
                continue
        else:
            continue
        for para in re.split(r"\n\s*\n", text):
            para = para.strip()
            if len(para) >= 40:  # skip headers/page numbers
                chunks.append({"text": para, "source": path.name})
    return chunks


@lru_cache(maxsize=4)
def _build_index(city: str):
    """Build a TF-IDF index for a city's corpus. Returns (vectorizer, matrix, chunks)."""
    from sklearn.feature_extraction.text import TfidfVectorizer

    chunks = _load_regulation_chunks(city)
    if not chunks:
        return None, None, []
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=1)
    matrix = vectorizer.fit_transform([c["text"] for c in chunks])
    return vectorizer, matrix, chunks


def query_regulations(city: str, question: str, top_k: int = 4) -> dict:
    """RAG over the regulatory corpus for a city (the Alternative's added capability).

    Retrieves the most relevant passages from the official regulatory texts
    (Barcelona Plan RESIDE; London Deregulation Act 2015) and returns them with
    source citations and relevance scores. The model then composes a grounded,
    cited answer — it must NOT answer regulatory questions from prior knowledge.

    Returns ``status='no_corpus'`` when no documents have been indexed yet, so the
    model can tell the user instead of inventing law.
    """
    c = _validate_city(city)
    if c is None:
        return {"error": "invalid_city", "detail": f"city must be one of {VALID_CITIES}"}
    if not (question or "").strip():
        return {"error": "empty_question"}

    vectorizer, matrix, chunks = _build_index(c)
    if not chunks:
        return {
            "status": "no_corpus",
            "city": c,
            "corpus": _CITY_REG_LABEL.get(c, c),
            "detail": (
                f"No regulatory documents are indexed for {c}. Add the official text "
                f"(.txt/.md/.pdf) under data/regulations/{c}/ and retry. The model must "
                "not answer regulatory questions without sourced passages."
            ),
        }

    from sklearn.metrics.pairwise import cosine_similarity

    q_vec = vectorizer.transform([question])
    scores = cosine_similarity(q_vec, matrix)[0]
    top_k = max(1, min(int(top_k), len(chunks)))
    order = scores.argsort()[::-1][:top_k]

    passages = []
    for idx in order:
        score = float(scores[idx])
        if score <= 0.0:
            continue
        passages.append(
            {
                "text": chunks[idx]["text"],
                "source": chunks[idx]["source"],
                "relevance": round(score, 4),
            }
        )
    if not passages:
        return {
            "status": "no_match",
            "city": c,
            "detail": "No passage in the corpus matched the question.",
        }
    return {
        "status": "ok",
        "city": c,
        "corpus": _CITY_REG_LABEL.get(c, c),
        "question": question,
        "passages": passages,
        "instruction": "Answer ONLY from these passages. Cite the source filename for each claim.",
    }


# --------------------------------------------------------------------------- #
# Bonus helper: caveats (used by the system prompt / Responsible-AI footers)
# --------------------------------------------------------------------------- #
@lru_cache(maxsize=1)
def _load_caveats() -> dict:
    import json

    path = REPO_ROOT / "reports" / "caveats.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def get_caveat(key: str) -> dict:
    """Look up a caveat by key from reports/caveats.json (for per-answer footers)."""
    caveats = _load_caveats()
    return {"key": key, "caveat": caveats.get(key), "available_keys": sorted(caveats)}


# --------------------------------------------------------------------------- #
# Manual smoke test:  python -m app.tools   (run from repo root)
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    import json

    print("STATUS:", json.dumps(knowledge_layer_status(), indent=2, ensure_ascii=False))
    print("\nrank_neighbourhoods(barcelona, str_density, 3):")
    print(json.dumps(rank_neighbourhoods("barcelona", "str_density", 3), indent=2, ensure_ascii=False))
    print("\ncompare_cities(str_density):")
    print(json.dumps(compare_cities("str_density"), indent=2, ensure_ascii=False))
    print("\npolicy_simulation(barcelona, 90, 3):")
    print(json.dumps(policy_simulation("barcelona", 90, 3), indent=2, ensure_ascii=False))
    print("\nget_neighbourhood_metrics(barcelona, el Raval):")
    print(json.dumps(get_neighbourhood_metrics("barcelona", "el Raval"), indent=2, ensure_ascii=False))
    print("\nquery_regulations(barcelona, registration):")
    print(json.dumps(query_regulations("barcelona", "registration requirement"), indent=2, ensure_ascii=False))
