# Regulatory corpus — RAG source for `query_regulations`

This folder is the source of truth for the chatbot's 6th tool,
`query_regulations(city, question)` (the KPMG "Alternative: Agentic Multimodal
Decision System" capability). The tool builds a TF-IDF index over whatever is in
here and returns the most relevant **sourced passages** — the model answers
regulatory questions *only* from these, never from prior knowledge.

> **Status: empty.** No documents are indexed yet, so `query_regulations` returns
> `status: "no_corpus"` by design. Drop the official texts in and it works
> immediately (the index rebuilds on next call — no code change needed).

## What to add

| Folder | Document | Suggested source |
|---|---|---|
| `barcelona/` | Pla Especial Urbanístic d'Allotjaments Turístics (PEUAT) / **Plan RESIDE** phase-out of HUTs | Ajuntament de Barcelona official text |
| `london/` | **Deregulation Act 2015**, s.44–45 (the 90-night rule for short-term lets) | legislation.gov.uk |

## Accepted formats

`.txt`, `.md`, `.pdf` (PDF needs `pdfplumber`, now in `environment.yml`).
Plain `.txt`/`.md` retrieve best — if you have a PDF, a text export is preferable.

## Naming

Use descriptive filenames; the tool cites the **filename** as the source, e.g.
`barcelona/plan_reside_2024.txt` → answers cite `plan_reside_2024.txt`.

## Do not invent legal text

Only add genuine, sourced regulatory material. The whole point of this tool is to
keep the chatbot grounded in real law — fabricated text would defeat it.

## How retrieval works

`app/tools.py::query_regulations` → paragraph-chunks every file (≥40 chars) →
`TfidfVectorizer(ngram_range=(1,2))` → cosine similarity → top-k passages with
relevance scores. To upgrade to semantic embeddings later, swap `_build_index`
and `query_regulations`' scoring; the tool's return shape stays the same.
