# Member 1 — Data Preparation

**Status:** ✅ Complete
**Sequence:** 1 of 4

---

## Scope

- **KPMG slide step:** Data Optimization
- **Handover phase:** Phase 2 — Cleaning & Feature Engineering (base layer)
- **Canonical questions served:** foundation for all 7

---

## What was done

- Loaded raw AirDNA parquet → CSV for Barcelona and London
- Audited duplicates and nulls across all 81 raw columns
- Selected 25 core columns relevant to the capstone
- Standardised geographic variables: `neighborhood` (district/borough) and `subdivision` (barrio/local neighbourhood)
- Engineered base flags:
  - `entire_home_flag`
  - `host_listing_count`, `multi_listing_host`, `host_5_plus_listings`, `host_10_plus_listings`
  - `professional_management_flag`
  - `has_registration`
- Exploded the `months` JSON column into a monthly panel (1 row = 1 listing × 1 month)
- Wrote the Data Preparation Handover document

---

## Deliverables (in repo)

| File | Rows |
|---|---|
| `notebooks/01_barcelona_data_preparation_clean.ipynb` | – |
| `notebooks/02_london_data_preparation_clean.ipynb` | – |
| `data/processed/barcelona/barcelona_listings_clean.csv` | 2,594 |
| `data/processed/barcelona/barcelona_monthly_metrics_clean.csv` | 88,821 |
| `data/processed/london/london_listings_clean.csv` | 9,643 |
| `data/processed/london/london_monthly_metrics_clean.csv` | 306,822 |

---

## Handover notes for Member 2

- Use `subdivision` as the main geographic key for neighbourhood-level analysis
- Time coverage: **March 2021 – February 2026**
- Source: **AirDNA only** — Inside Airbnb is not in scope
- Original `past_rates` files remain in `data/raw/` for reference only — monthly history already extracted into `*_monthly_metrics_clean.csv`
