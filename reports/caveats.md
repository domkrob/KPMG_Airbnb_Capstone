# Chatbot Caveats

_Generated on 2026-06-08._

Disclaimers Member 4 must surface in the chatbot. These belong in:

- The system prompt (every answer respects these caveats)
- Per-answer footers when a specific caveat applies (e.g., Q7 → RESIDE caveat)
- The static "About" / "Limitations" page of the Streamlit app

## Caveats

### AirDNA is a sample, not the full market

**Applies to:** all

All counts and shares reflect the AirDNA sample (~14% of Barcelona's STR universe, ~10% of London's). Market-wide totals are larger. Present numbers as 'in the AirDNA sample' for honesty.

### Association, not causation

**Applies to:** all

High STR density correlates with rent pressure but does NOT prove Airbnb causes rent rises. The tool surfaces risk indicators for policy attention — it does not establish causality.

### Subdivision coverage gaps

**Applies to:** all

9% of Barcelona and 12% of London listings have no subdivision in raw data. These were rolled up to borough-level via the geo_key fallback (geo_level indicates which resolution). Some neighbourhoods may be undercounted.

### Professional-management share is conservative

**Applies to:** Q3

~54% of London raw professional_management values were null. The KPI uses only reported cases (professional_management_known == True). Treat the share as a lower bound — true commercialisation may be higher.

### RESIDE flag is Barcelona-only

**Applies to:** Q7

reside_unregistered_count counts entire homes without a registration on record. This is regulatorily meaningful for Barcelona (RESIDE phase-out). For London the same number is data context — not a policy breach. Do not present LDN reside_unregistered as a regulatory violation.

### Time coverage

**Applies to:** Q5

Data spans March 2021 – February 2026. Emerging-hotspot growth compares the most recent 6 months against the prior 6 months.

### London geojson is borough-level

**Applies to:** Q6

Choropleth maps for London are at borough level (33 boroughs). Subdivision-level KPIs exist but cannot be mapped without a finer geojson.

### Westminster sub-areas in AirDNA

**Applies to:** Q6

AirDNA records 13 Westminster sub-areas (Mayfair, Belgravia, Paddington, Marylebone, Pimlico etc.) at neighbourhood level rather than rolling them up to Westminster. subdivision_name_map.csv documents the rollup. For Westminster queries, sum the relevant rows.

### City of London and Westminster missing from KPI

**Applies to:** Q6

The AirDNA sample contains zero listings in 'City of London' (the financial district borough) and listings tagged 'Westminster' directly. Both appear in the geojson but not in our KPI table. The Westminster sub-areas above are where the Westminster activity actually lives.
