# Golden Answers — 7 Canonical Questions

_Generated on 2026-06-15._

Member 4 evaluates the chatbot against these numbers. Target: ≥90% accuracy. Numbers come directly from `data/processed/neighbourhood_kpis.csv`.

---

## Q1 — Which neighbourhoods have the highest concentration of STRs?

_Method: Top 10 subdivisions per city by str_density._

### Barcelona

|   rank | geo_key                               |   str_density | tier   | recommended_action                                                                                                                             |
|-------:|:--------------------------------------|--------------:|:-------|:-----------------------------------------------------------------------------------------------------------------------------------------------|
|      1 | la Dreta de l'Eixample                |           295 | tier_1 | Priority inspection target (Tier 1 — high concentration AND high price.). 295 listings concentrated here — size enforcement capacity to match. |
|      2 | el Raval                              |           203 | tier_2 | Priority inspection target (Tier 2 — elevated on density or price.). 203 listings concentrated here — size enforcement capacity to match.      |
|      3 | Sant Pere, Santa Caterina i la Ribera |           163 | tier_2 | Priority inspection target (Tier 2 — elevated on density or price.). 163 listings concentrated here — size enforcement capacity to match.      |
|      4 | Gothic Quarter                        |           160 | tier_2 | Priority inspection target (Tier 2 — elevated on density or price.). 160 listings concentrated here — size enforcement capacity to match.      |
|      5 | l'Antiga Esquerra de l'Eixample       |           148 | tier_2 | Priority inspection target (Tier 2 — elevated on density or price.). 148 listings concentrated here — size enforcement capacity to match.      |
|      6 | la Sagrada Família                    |           144 | tier_1 | Priority inspection target (Tier 1 — high concentration AND high price.). 144 listings concentrated here — size enforcement capacity to match. |
|      7 | el Poble-sec                          |           118 | tier_1 | Priority inspection target (Tier 1 — high concentration AND high price.). 118 listings concentrated here — size enforcement capacity to match. |
|      8 | la Nova Esquerra de l'Eixample        |           114 | tier_2 | Priority inspection target (Tier 2 — elevated on density or price.). 114 listings concentrated here — size enforcement capacity to match.      |
|      9 | la Vila de Gràcia                     |           104 | tier_1 | Priority inspection target (Tier 1 — high concentration AND high price.). 104 listings concentrated here — size enforcement capacity to match. |
|     10 | Sant Antoni                           |            79 | tier_1 | Priority inspection target (Tier 1 — high concentration AND high price.). 79 listings concentrated here — size enforcement capacity to match.  |

### London

|   rank | geo_key                  |   str_density | tier   | recommended_action                                                                                                                             |
|-------:|:-------------------------|--------------:|:-------|:-----------------------------------------------------------------------------------------------------------------------------------------------|
|      1 | Whitechapel              |           242 | tier_2 | Priority inspection target (Tier 2 — elevated on density or price.). 242 listings concentrated here — size enforcement capacity to match.      |
|      2 | Westbourne Green         |           210 | tier_1 | Priority inspection target (Tier 1 — high concentration AND high price.). 210 listings concentrated here — size enforcement capacity to match. |
|      3 | Marylebone               |           178 | tier_1 | Priority inspection target (Tier 1 — high concentration AND high price.). 178 listings concentrated here — size enforcement capacity to match. |
|      4 | Earl's Court             |           168 | tier_1 | Priority inspection target (Tier 1 — high concentration AND high price.). 168 listings concentrated here — size enforcement capacity to match. |
|      5 | Paddington               |           152 | tier_1 | Priority inspection target (Tier 1 — high concentration AND high price.). 152 listings concentrated here — size enforcement capacity to match. |
|      6 | Fulham                   |           139 | tier_1 | Priority inspection target (Tier 1 — high concentration AND high price.). 139 listings concentrated here — size enforcement capacity to match. |
|      7 | West Kensington          |           127 | tier_2 | Priority inspection target (Tier 2 — elevated on density or price.). 127 listings concentrated here — size enforcement capacity to match.      |
|      8 | Chelsea                  |           123 | tier_1 | Priority inspection target (Tier 1 — high concentration AND high price.). 123 listings concentrated here — size enforcement capacity to match. |
|      9 | Notting Hill             |           119 | tier_1 | Priority inspection target (Tier 1 — high concentration AND high price.). 119 listings concentrated here — size enforcement capacity to match. |
|     10 | London Borough of Ealing |           117 | tier_2 | Priority inspection target (Tier 2 — elevated on density or price.). 117 listings concentrated here — size enforcement capacity to match.      |

---

## Q2 — Where is Airbnb most likely removing homes from the long-term residential market?

_Method: Top 10 subdivisions per city by entire_home_share, restricted to neighbourhoods with str_density >= 30._

### Barcelona

|   rank | geo_key                            |   str_density |   entire_home_count |   entire_home_share | recommended_action                                                                                                                  |
|-------:|:-----------------------------------|--------------:|--------------------:|--------------------:|:------------------------------------------------------------------------------------------------------------------------------------|
|      1 | les Corts                          |            32 |                  28 |               0.875 | 87.5% of listings are entire homes — strong candidate for change-of-use planning restriction. Recoverable housing units: up to 28.  |
|      2 | el Camp d'en Grassot i Gràcia Nova |            37 |                  29 |               0.784 | 78.4% of listings are entire homes — strong candidate for change-of-use planning restriction. Recoverable housing units: up to 29.  |
|      3 | la Sagrada Família                 |           144 |                 106 |               0.736 | 73.6% of listings are entire homes — strong candidate for change-of-use planning restriction. Recoverable housing units: up to 106. |
|      4 | la Barceloneta                     |            68 |                  50 |               0.735 | 73.5% of listings are entire homes — strong candidate for change-of-use planning restriction. Recoverable housing units: up to 50.  |
|      5 | la Vila de Gràcia                  |           104 |                  76 |               0.731 | 73.1% of listings are entire homes — strong candidate for change-of-use planning restriction. Recoverable housing units: up to 76.  |
|      6 | el Poblenou                        |            59 |                  43 |               0.729 | 72.9% of listings are entire homes — strong candidate for change-of-use planning restriction. Recoverable housing units: up to 43.  |
|      7 | Sant Gervasi - Galvany             |            44 |                  32 |               0.727 | 72.7% of listings are entire homes — strong candidate for change-of-use planning restriction. Recoverable housing units: up to 32.  |
|      8 | el Poble-sec                       |           118 |                  83 |               0.703 | 70.3% of listings are entire homes — strong candidate for change-of-use planning restriction. Recoverable housing units: up to 83.  |
|      9 | la Dreta de l'Eixample             |           295 |                 201 |               0.681 | 68.1% of listings are entire homes — strong candidate for change-of-use planning restriction. Recoverable housing units: up to 201. |
|     10 | Sant Antoni                        |            79 |                  51 |               0.646 | 64.6% of listings are entire homes — strong candidate for change-of-use planning restriction. Recoverable housing units: up to 51.  |

### London

|   rank | geo_key                      |   str_density |   entire_home_count |   entire_home_share | recommended_action                                                                                                                  |
|-------:|:-----------------------------|--------------:|--------------------:|--------------------:|:------------------------------------------------------------------------------------------------------------------------------------|
|      1 | Brompton                     |           100 |                  95 |               0.95  | 95.0% of listings are entire homes — strong candidate for change-of-use planning restriction. Recoverable housing units: up to 95.  |
|      2 | London Borough of Wandsworth |            36 |                  34 |               0.944 | 94.4% of listings are entire homes — strong candidate for change-of-use planning restriction. Recoverable housing units: up to 34.  |
|      3 | Mayfair                      |            33 |                  31 |               0.939 | 93.9% of listings are entire homes — strong candidate for change-of-use planning restriction. Recoverable housing units: up to 31.  |
|      4 | Chelsea                      |           123 |                 112 |               0.911 | 91.1% of listings are entire homes — strong candidate for change-of-use planning restriction. Recoverable housing units: up to 112. |
|      5 | Notting Hill                 |           119 |                 106 |               0.891 | 89.1% of listings are entire homes — strong candidate for change-of-use planning restriction. Recoverable housing units: up to 106. |
|      6 | South Kensington             |            87 |                  76 |               0.874 | 87.4% of listings are entire homes — strong candidate for change-of-use planning restriction. Recoverable housing units: up to 76.  |
|      7 | Holborn                      |            74 |                  64 |               0.865 | 86.5% of listings are entire homes — strong candidate for change-of-use planning restriction. Recoverable housing units: up to 64.  |
|      8 | Earl's Court                 |           168 |                 145 |               0.863 | 86.3% of listings are entire homes — strong candidate for change-of-use planning restriction. Recoverable housing units: up to 145. |
|      9 | Marylebone                   |           178 |                 153 |               0.86  | 86.0% of listings are entire homes — strong candidate for change-of-use planning restriction. Recoverable housing units: up to 153. |
|     10 | Shoreditch                   |            63 |                  54 |               0.857 | 85.7% of listings are entire homes — strong candidate for change-of-use planning restriction. Recoverable housing units: up to 54.  |

---

## Q3 — Which neighbourhoods are dominated by commercial/professional hosts?

_Method: Top 10 subdivisions per city by commercial_host_share (commercial+super_commercial tiers, ≥5 listings/host), restricted to str_density >= 30._

### Barcelona

|   rank | geo_key                         |   str_density |   commercial_host_share |   multi_listing_host_share | recommended_action                                                                                                       |
|-------:|:--------------------------------|--------------:|------------------------:|---------------------------:|:-------------------------------------------------------------------------------------------------------------------------|
|      1 | la Nova Esquerra de l'Eixample  |           114 |                   0.404 |                      0.57  | 40.4% of listings owned by commercial-scale hosts. Focus commercial-letting compliance audits and licensing checks here. |
|      2 | el Poble-sec                    |           118 |                   0.364 |                      0.559 | 36.4% of listings owned by commercial-scale hosts. Focus commercial-letting compliance audits and licensing checks here. |
|      3 | l'Antiga Esquerra de l'Eixample |           148 |                   0.345 |                      0.635 | 34.5% of listings owned by commercial-scale hosts. Focus commercial-letting compliance audits and licensing checks here. |
|      4 | Sant Antoni                     |            79 |                   0.329 |                      0.595 | 32.9% of listings owned by commercial-scale hosts. Focus commercial-letting compliance audits and licensing checks here. |
|      5 | Sant Gervasi - Galvany          |            44 |                   0.318 |                      0.659 | 31.8% of listings owned by commercial-scale hosts. Focus commercial-letting compliance audits and licensing checks here. |
|      6 | la Sagrada Família              |           144 |                   0.285 |                      0.479 | 28.5% of listings owned by commercial-scale hosts. Focus commercial-letting compliance audits and licensing checks here. |
|      7 | Hostafrancs                     |            32 |                   0.281 |                      0.469 | 28.1% of listings owned by commercial-scale hosts. Focus commercial-letting compliance audits and licensing checks here. |
|      8 | el Fort Pienc                   |            67 |                   0.269 |                      0.522 | 26.9% of listings owned by commercial-scale hosts. Focus commercial-letting compliance audits and licensing checks here. |
|      9 | la Dreta de l'Eixample          |           295 |                   0.264 |                      0.651 | 26.4% of listings owned by commercial-scale hosts. Focus commercial-letting compliance audits and licensing checks here. |
|     10 | la Vila de Gràcia               |           104 |                   0.25  |                      0.519 | 25.0% of listings owned by commercial-scale hosts. Focus commercial-letting compliance audits and licensing checks here. |

### London

|   rank | geo_key                 |   str_density |   commercial_host_share |   multi_listing_host_share | recommended_action                                                                                                       |
|-------:|:------------------------|--------------:|------------------------:|---------------------------:|:-------------------------------------------------------------------------------------------------------------------------|
|      1 | Bayswater               |            31 |                   0.387 |                      0.645 | 38.7% of listings owned by commercial-scale hosts. Focus commercial-letting compliance audits and licensing checks here. |
|      2 | Notting Hill            |           119 |                   0.37  |                      0.538 | 37.0% of listings owned by commercial-scale hosts. Focus commercial-letting compliance audits and licensing checks here. |
|      3 | Earl's Court            |           168 |                   0.357 |                      0.607 | 35.7% of listings owned by commercial-scale hosts. Focus commercial-letting compliance audits and licensing checks here. |
|      4 | Brondesbury             |            55 |                   0.309 |                      0.582 | 30.9% of listings owned by commercial-scale hosts. Focus commercial-letting compliance audits and licensing checks here. |
|      5 | Mayfair                 |            33 |                   0.303 |                      0.727 | 30.3% of listings owned by commercial-scale hosts. Focus commercial-letting compliance audits and licensing checks here. |
|      6 | Paddington              |           152 |                   0.289 |                      0.52  | 28.9% of listings owned by commercial-scale hosts. Focus commercial-letting compliance audits and licensing checks here. |
|      7 | South Kensington        |            87 |                   0.287 |                      0.609 | 28.7% of listings owned by commercial-scale hosts. Focus commercial-letting compliance audits and licensing checks here. |
|      8 | South Hampstead         |            36 |                   0.278 |                      0.444 | 27.8% of listings owned by commercial-scale hosts. Focus commercial-letting compliance audits and licensing checks here. |
|      9 | London Borough of Brent |            59 |                   0.271 |                      0.407 | 27.1% of listings owned by commercial-scale hosts. Focus commercial-letting compliance audits and licensing checks here. |
|     10 | King's Cross            |            85 |                   0.271 |                      0.6   | 27.1% of listings owned by commercial-scale hosts. Focus commercial-letting compliance audits and licensing checks here. |

---

## Q4 — In which neighbourhoods does high STR density coincide with high prices?

_Method: Subdivisions in top quartile of BOTH str_density AND median_nightly_price per city (str_density >= 30). These are the tier-1 areas — see tier_concentration_price column for the full classification._

### Barcelona

Correlation between density and price: **0.298**

| geo_key                |   str_density |   median_nightly_price | tier   | recommended_action                                                                                              |
|:-----------------------|--------------:|-----------------------:|:-------|:----------------------------------------------------------------------------------------------------------------|
| la Dreta de l'Eixample |           295 |                  265.6 | tier_1 | Tier 1 priority. 295 listings at €/£266 median nightly — lead with this area in any phased enforcement rollout. |

### London

Correlation between density and price: **0.258**

| geo_key          |   str_density |   median_nightly_price | tier   | recommended_action                                                                                              |
|:-----------------|--------------:|-----------------------:|:-------|:----------------------------------------------------------------------------------------------------------------|
| Westbourne Green |           210 |                  250.2 | tier_1 | Tier 1 priority. 210 listings at €/£250 median nightly — lead with this area in any phased enforcement rollout. |
| Marylebone       |           178 |                  273.4 | tier_1 | Tier 1 priority. 178 listings at €/£273 median nightly — lead with this area in any phased enforcement rollout. |
| Earl's Court     |           168 |                  245.2 | tier_1 | Tier 1 priority. 168 listings at €/£245 median nightly — lead with this area in any phased enforcement rollout. |
| Paddington       |           152 |                  301.5 | tier_1 | Tier 1 priority. 152 listings at €/£302 median nightly — lead with this area in any phased enforcement rollout. |
| Fulham           |           139 |                  235.7 | tier_1 | Tier 1 priority. 139 listings at €/£236 median nightly — lead with this area in any phased enforcement rollout. |
| Chelsea          |           123 |                  405.2 | tier_1 | Tier 1 priority. 123 listings at €/£405 median nightly — lead with this area in any phased enforcement rollout. |
| Notting Hill     |           119 |                  234.1 | tier_1 | Tier 1 priority. 119 listings at €/£234 median nightly — lead with this area in any phased enforcement rollout. |
| Fitzrovia        |           104 |                  224.8 | tier_1 | Tier 1 priority. 104 listings at €/£225 median nightly — lead with this area in any phased enforcement rollout. |
| Brompton         |           100 |                  306.6 | tier_1 | Tier 1 priority. 100 listings at €/£307 median nightly — lead with this area in any phased enforcement rollout. |
| South Kensington |            87 |                  409.9 | tier_1 | Tier 1 priority. 87 listings at €/£410 median nightly — lead with this area in any phased enforcement rollout.  |
| Holborn          |            74 |                  299.9 | tier_1 | Tier 1 priority. 74 listings at €/£300 median nightly — lead with this area in any phased enforcement rollout.  |
| Kensington       |            74 |                  273.7 | tier_1 | Tier 1 priority. 74 listings at €/£274 median nightly — lead with this area in any phased enforcement rollout.  |

---

## Q5 — Which neighbourhoods are saturated, and which are emerging hotspots?

_Method: Saturated = composite of high density + entire-home share + commercial-host share + occupancy. Emerging = top active-listing growth (recent 6 mo vs prior 6 mo). Member 3 will replace the saturated heuristic with the proper KMeans cluster label._

### Saturated — across both cities

**Barcelona**

|   rank | geo_key                            |   str_density |   entire_home_share |   commercial_host_share |   avg_occupancy |   saturation_score | recommended_action                                                                                                                                |
|-------:|:-----------------------------------|--------------:|--------------------:|------------------------:|----------------:|-------------------:|:--------------------------------------------------------------------------------------------------------------------------------------------------|
|      1 | la Dreta de l'Eixample             |           295 |               0.681 |                   0.264 |           0.23  |               4.21 | Saturated — maintain visible enforcement; monitor for displacement to adjacent neighbourhoods; resist political pressure to relax existing rules. |
|      2 | el Poble-sec                       |           118 |               0.703 |                   0.364 |           0.233 |               3.06 | Saturated — maintain visible enforcement; monitor for displacement to adjacent neighbourhoods; resist political pressure to relax existing rules. |
|      3 | la Sagrada Família                 |           144 |               0.736 |                   0.285 |           0.245 |               2.98 | Saturated — maintain visible enforcement; monitor for displacement to adjacent neighbourhoods; resist political pressure to relax existing rules. |
|      4 | l'Antiga Esquerra de l'Eixample    |           148 |               0.635 |                   0.345 |           0.206 |               2.26 | Saturated — maintain visible enforcement; monitor for displacement to adjacent neighbourhoods; resist political pressure to relax existing rules. |
|      5 | la Nova Esquerra de l'Eixample     |           114 |               0.526 |                   0.404 |           0.241 |               2.2  | Saturated — maintain visible enforcement; monitor for displacement to adjacent neighbourhoods; resist political pressure to relax existing rules. |
|      6 | la Vila de Gràcia                  |           104 |               0.731 |                   0.25  |           0.228 |               1.67 | Saturated — maintain visible enforcement; monitor for displacement to adjacent neighbourhoods; resist political pressure to relax existing rules. |
|      7 | el Camp d'en Grassot i Gràcia Nova |            37 |               0.784 |                   0.135 |           0.32  |               1.4  | Saturated — maintain visible enforcement; monitor for displacement to adjacent neighbourhoods; resist political pressure to relax existing rules. |
|      8 | Sant Antoni                        |            79 |               0.646 |                   0.329 |           0.217 |               1.37 | Saturated — maintain visible enforcement; monitor for displacement to adjacent neighbourhoods; resist political pressure to relax existing rules. |
|      9 | Sant Gervasi - Galvany             |            44 |               0.727 |                   0.318 |           0.168 |               0.54 | Saturated — maintain visible enforcement; monitor for displacement to adjacent neighbourhoods; resist political pressure to relax existing rules. |
|     10 | les Corts                          |            32 |               0.875 |                   0.25  |           0.139 |               0.25 | Saturated — maintain visible enforcement; monitor for displacement to adjacent neighbourhoods; resist political pressure to relax existing rules. |

**London**

|   rank | geo_key          |   str_density |   entire_home_share |   commercial_host_share |   avg_occupancy |   saturation_score | recommended_action                                                                                                                                |
|-------:|:-----------------|--------------:|--------------------:|------------------------:|----------------:|-------------------:|:--------------------------------------------------------------------------------------------------------------------------------------------------|
|      1 | Notting Hill     |           119 |               0.891 |                   0.37  |           0.161 |               6.36 | Saturated — maintain visible enforcement; monitor for displacement to adjacent neighbourhoods; resist political pressure to relax existing rules. |
|      2 | Earl's Court     |           168 |               0.863 |                   0.357 |           0.105 |               6.18 | Saturated — maintain visible enforcement; monitor for displacement to adjacent neighbourhoods; resist political pressure to relax existing rules. |
|      3 | Westbourne Green |           210 |               0.848 |                   0.262 |           0.106 |               6.14 | Saturated — maintain visible enforcement; monitor for displacement to adjacent neighbourhoods; resist political pressure to relax existing rules. |
|      4 | Paddington       |           152 |               0.842 |                   0.289 |           0.167 |               6.08 | Saturated — maintain visible enforcement; monitor for displacement to adjacent neighbourhoods; resist political pressure to relax existing rules. |
|      5 | Whitechapel      |           242 |               0.612 |                   0.157 |           0.17  |               5.16 | Saturated — maintain visible enforcement; monitor for displacement to adjacent neighbourhoods; resist political pressure to relax existing rules. |
|      6 | Marylebone       |           178 |               0.86  |                   0.191 |           0.112 |               4.74 | Saturated — maintain visible enforcement; monitor for displacement to adjacent neighbourhoods; resist political pressure to relax existing rules. |
|      7 | Chelsea          |           123 |               0.911 |                   0.268 |           0.106 |               4.44 | Saturated — maintain visible enforcement; monitor for displacement to adjacent neighbourhoods; resist political pressure to relax existing rules. |
|      8 | South Kensington |            87 |               0.874 |                   0.287 |           0.145 |               4.19 | Saturated — maintain visible enforcement; monitor for displacement to adjacent neighbourhoods; resist political pressure to relax existing rules. |
|      9 | Shoreditch       |            63 |               0.857 |                   0.222 |           0.217 |               4.14 | Saturated — maintain visible enforcement; monitor for displacement to adjacent neighbourhoods; resist political pressure to relax existing rules. |
|     10 | Waterloo         |            30 |               0.767 |                   0.267 |           0.259 |               3.87 | Saturated — maintain visible enforcement; monitor for displacement to adjacent neighbourhoods; resist political pressure to relax existing rules. |

### Emerging — across both cities

**Barcelona**

|   rank | geo_key               |   prior_active |   recent_active |   active_growth_pct | recommended_action                                                                                                                                         |
|-------:|:----------------------|---------------:|----------------:|--------------------:|:-----------------------------------------------------------------------------------------------------------------------------------------------------------|
|      1 | Can Baró              |            5   |             6   |                20   | Emerging hotspot (+20% active listings in 6 months). Pre-emptive monitoring; consider early intervention before saturation triggers stronger displacement. |
|      2 | la Sagrera            |            5   |             5   |                 0   | Emerging hotspot (+0% active listings in 6 months). Pre-emptive monitoring; consider early intervention before saturation triggers stronger displacement.  |
|      3 | la Font de la Guatlla |            9   |             9   |                 0   | Emerging hotspot (+0% active listings in 6 months). Pre-emptive monitoring; consider early intervention before saturation triggers stronger displacement.  |
|      4 | les Corts             |           21.5 |            21.2 |                -1.6 | Emerging hotspot (+-2% active listings in 6 months). Pre-emptive monitoring; consider early intervention before saturation triggers stronger displacement. |
|      5 | el Baix Guinardó      |           12   |            11.2 |                -6.9 | Emerging hotspot (+-7% active listings in 6 months). Pre-emptive monitoring; consider early intervention before saturation triggers stronger displacement. |

**London**

|   rank | geo_key      |   prior_active |   recent_active |   active_growth_pct | recommended_action                                                                                                                                         |
|-------:|:-------------|---------------:|----------------:|--------------------:|:-----------------------------------------------------------------------------------------------------------------------------------------------------------|
|      1 | Greenford    |            5   |             5.7 |                13.3 | Emerging hotspot (+13% active listings in 6 months). Pre-emptive monitoring; consider early intervention before saturation triggers stronger displacement. |
|      2 | Abbey Wood   |            5.8 |             6.5 |                11.4 | Emerging hotspot (+11% active listings in 6 months). Pre-emptive monitoring; consider early intervention before saturation triggers stronger displacement. |
|      3 | Gants Hill   |            5   |             5.5 |                10   | Emerging hotspot (+10% active listings in 6 months). Pre-emptive monitoring; consider early intervention before saturation triggers stronger displacement. |
|      4 | North Sheen  |            9.8 |            10   |                 1.7 | Emerging hotspot (+2% active listings in 6 months). Pre-emptive monitoring; consider early intervention before saturation triggers stronger displacement.  |
|      5 | Earlsfield   |           13.5 |            13.7 |                 1.2 | Emerging hotspot (+1% active listings in 6 months). Pre-emptive monitoring; consider early intervention before saturation triggers stronger displacement.  |
|      6 | East Sheen   |            6   |             6   |                 0   | Emerging hotspot (+0% active listings in 6 months). Pre-emptive monitoring; consider early intervention before saturation triggers stronger displacement.  |
|      7 | Edmonton     |            5   |             5   |                 0   | Emerging hotspot (+0% active listings in 6 months). Pre-emptive monitoring; consider early intervention before saturation triggers stronger displacement.  |
|      8 | Finchley     |            8.3 |             8.2 |                -2   | Emerging hotspot (+-2% active listings in 6 months). Pre-emptive monitoring; consider early intervention before saturation triggers stronger displacement. |
|      9 | Highams Park |            9.5 |             9.2 |                -3.5 | Emerging hotspot (+-4% active listings in 6 months). Pre-emptive monitoring; consider early intervention before saturation triggers stronger displacement. |
|     10 | Selhurst     |            9   |             8.7 |                -3.7 | Emerging hotspot (+-4% active listings in 6 months). Pre-emptive monitoring; consider early intervention before saturation triggers stronger displacement. |

---

## Q6 — How does STR pressure compare between Barcelona and London?

_Method: Side-by-side comparison of citywide totals and neighbourhood-level medians._

### Citywide totals

| city      |   total_listings |   unique_hosts |   unique_subdivisions |   entire_homes |   entire_home_share |   active_listings_last_12m |   breach_90_total |   reside_unregistered_total |   ttm_revenue_total |   median_nightly_price |   median_occupancy_active |   mean_occupancy_active |
|:----------|-----------------:|---------------:|----------------------:|---------------:|--------------------:|---------------------------:|------------------:|----------------------------:|--------------------:|-----------------------:|--------------------------:|------------------------:|
| barcelona |             2594 |           1637 |                    66 |           1539 |               0.593 |                       1655 |               642 |                         421 |         5.21592e+07 |                  156   |                     0.044 |                   0.21  |
| london    |             9643 |           7312 |                   455 |           6536 |               0.678 |                       5967 |              1485 |                        2572 |         1.22631e+08 |                  174.7 |                     0     |                   0.137 |

### Neighbourhood-level medians

| city      |   str_density |   entire_home_share |   commercial_host_share |   avg_occupancy |   median_nightly_price |   breach_rate_90 |
|:----------|--------------:|--------------------:|------------------------:|----------------:|-----------------------:|-----------------:|
| barcelona |            10 |               0.53  |                   0.134 |           0.124 |                 118.85 |            0.447 |
| london    |             8 |               0.625 |                   0     |           0.078 |                 142.75 |            0.188 |

---

## Q7 — If entire-home listings were capped at X nights/year, how many listings and which neighbourhoods would be affected?

_Method: Sum of breach_count_{cap} per city (city totals), plus top-impacted neighbourhoods per cap per city. RESIDE simulation: count of reside_unregistered listings per Barcelona neighbourhood (entire homes without registration on record)._

### City totals at each cap

| city      |   cap_90_listings_impacted |   cap_60_listings_impacted |   cap_30_listings_impacted |   entire_homes_total |   reside_unregistered_total | note                                                                                                                                               |
|:----------|---------------------------:|---------------------------:|---------------------------:|---------------------:|----------------------------:|:---------------------------------------------------------------------------------------------------------------------------------------------------|
| barcelona |                        611 |                        689 |                        751 |                 1414 |                         421 | Sum over neighbourhoods; excludes listings with no subdivision/neighborhood. City-wide totals from listings_features may differ by a few listings. |
| london    |                       1482 |                       1863 |                       2260 |                 6504 |                        2563 | Sum over neighbourhoods; excludes listings with no subdivision/neighborhood. City-wide totals from listings_features may differ by a few listings. |

### Top impacted neighbourhoods — 90-night cap

**Barcelona**

|   rank | geo_key                               |   listings_impacted |   entire_home_count |   breach_rate | tier   | recommended_action                                                                                                                                         |
|-------:|:--------------------------------------|--------------------:|--------------------:|--------------:|:-------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------|
|      1 | la Dreta de l'Eixample                |                  95 |                 201 |         0.473 | tier_1 | At 90-night cap, 95 listings recoverable here (Tier 1 — high concentration AND high price.). Sequence enforcement against this list, starting from tier 1. |
|      2 | la Sagrada Família                    |                  53 |                 106 |         0.5   | tier_1 | At 90-night cap, 53 listings recoverable here (Tier 1 — high concentration AND high price.). Sequence enforcement against this list, starting from tier 1. |
|      3 | el Poble-sec                          |                  46 |                  83 |         0.554 | tier_1 | At 90-night cap, 46 listings recoverable here (Tier 1 — high concentration AND high price.). Sequence enforcement against this list, starting from tier 1. |
|      4 | l'Antiga Esquerra de l'Eixample       |                  43 |                  94 |         0.457 | tier_2 | At 90-night cap, 43 listings recoverable here (Tier 2 — elevated on density or price.). Sequence enforcement against this list, starting from tier 1.      |
|      5 | la Vila de Gràcia                     |                  34 |                  76 |         0.447 | tier_1 | At 90-night cap, 34 listings recoverable here (Tier 1 — high concentration AND high price.). Sequence enforcement against this list, starting from tier 1. |
|      6 | Sant Pere, Santa Caterina i la Ribera |                  31 |                 100 |         0.31  | tier_2 | At 90-night cap, 31 listings recoverable here (Tier 2 — elevated on density or price.). Sequence enforcement against this list, starting from tier 1.      |
|      7 | la Nova Esquerra de l'Eixample        |                  31 |                  60 |         0.517 | tier_2 | At 90-night cap, 31 listings recoverable here (Tier 2 — elevated on density or price.). Sequence enforcement against this list, starting from tier 1.      |
|      8 | el Raval                              |                  28 |                  86 |         0.326 | tier_2 | At 90-night cap, 28 listings recoverable here (Tier 2 — elevated on density or price.). Sequence enforcement against this list, starting from tier 1.      |
|      9 | Sant Antoni                           |                  26 |                  51 |         0.51  | tier_1 | At 90-night cap, 26 listings recoverable here (Tier 1 — high concentration AND high price.). Sequence enforcement against this list, starting from tier 1. |
|     10 | el Poblenou                           |                  21 |                  43 |         0.488 | tier_1 | At 90-night cap, 21 listings recoverable here (Tier 1 — high concentration AND high price.). Sequence enforcement against this list, starting from tier 1. |

**London**

|   rank | geo_key          |   listings_impacted |   entire_home_count |   breach_rate | tier   | recommended_action                                                                                                                                         |
|-------:|:-----------------|--------------------:|--------------------:|--------------:|:-------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------|
|      1 | Whitechapel      |                  44 |                 148 |         0.297 | tier_2 | At 90-night cap, 44 listings recoverable here (Tier 2 — elevated on density or price.). Sequence enforcement against this list, starting from tier 1.      |
|      2 | Paddington       |                  42 |                 128 |         0.328 | tier_1 | At 90-night cap, 42 listings recoverable here (Tier 1 — high concentration AND high price.). Sequence enforcement against this list, starting from tier 1. |
|      3 | Westbourne Green |                  41 |                 178 |         0.23  | tier_1 | At 90-night cap, 41 listings recoverable here (Tier 1 — high concentration AND high price.). Sequence enforcement against this list, starting from tier 1. |
|      4 | Marylebone       |                  35 |                 153 |         0.229 | tier_1 | At 90-night cap, 35 listings recoverable here (Tier 1 — high concentration AND high price.). Sequence enforcement against this list, starting from tier 1. |
|      5 | Chelsea          |                  26 |                 112 |         0.232 | tier_1 | At 90-night cap, 26 listings recoverable here (Tier 1 — high concentration AND high price.). Sequence enforcement against this list, starting from tier 1. |
|      6 | North Kensington |                  26 |                  82 |         0.317 | tier_1 | At 90-night cap, 26 listings recoverable here (Tier 1 — high concentration AND high price.). Sequence enforcement against this list, starting from tier 1. |
|      7 | Barnsbury        |                  24 |                  77 |         0.312 | tier_2 | At 90-night cap, 24 listings recoverable here (Tier 2 — elevated on density or price.). Sequence enforcement against this list, starting from tier 1.      |
|      8 | West Kensington  |                  24 |                  90 |         0.267 | tier_2 | At 90-night cap, 24 listings recoverable here (Tier 2 — elevated on density or price.). Sequence enforcement against this list, starting from tier 1.      |
|      9 | Earl's Court     |                  23 |                 145 |         0.159 | tier_1 | At 90-night cap, 23 listings recoverable here (Tier 1 — high concentration AND high price.). Sequence enforcement against this list, starting from tier 1. |
|     10 | Shoreditch       |                  23 |                  54 |         0.426 | tier_1 | At 90-night cap, 23 listings recoverable here (Tier 1 — high concentration AND high price.). Sequence enforcement against this list, starting from tier 1. |

### Top impacted neighbourhoods — 60-night cap

**Barcelona**

|   rank | geo_key                               |   listings_impacted |   entire_home_count |   breach_rate | tier   | recommended_action                                                                                                                                          |
|-------:|:--------------------------------------|--------------------:|--------------------:|--------------:|:-------|:------------------------------------------------------------------------------------------------------------------------------------------------------------|
|      1 | la Dreta de l'Eixample                |                 111 |                 201 |         0.552 | tier_1 | At 60-night cap, 111 listings recoverable here (Tier 1 — high concentration AND high price.). Sequence enforcement against this list, starting from tier 1. |
|      2 | la Sagrada Família                    |                  57 |                 106 |         0.538 | tier_1 | At 60-night cap, 57 listings recoverable here (Tier 1 — high concentration AND high price.). Sequence enforcement against this list, starting from tier 1.  |
|      3 | el Poble-sec                          |                  49 |                  83 |         0.59  | tier_1 | At 60-night cap, 49 listings recoverable here (Tier 1 — high concentration AND high price.). Sequence enforcement against this list, starting from tier 1.  |
|      4 | l'Antiga Esquerra de l'Eixample       |                  46 |                  94 |         0.489 | tier_2 | At 60-night cap, 46 listings recoverable here (Tier 2 — elevated on density or price.). Sequence enforcement against this list, starting from tier 1.       |
|      5 | la Vila de Gràcia                     |                  39 |                  76 |         0.513 | tier_1 | At 60-night cap, 39 listings recoverable here (Tier 1 — high concentration AND high price.). Sequence enforcement against this list, starting from tier 1.  |
|      6 | Sant Pere, Santa Caterina i la Ribera |                  35 |                 100 |         0.35  | tier_2 | At 60-night cap, 35 listings recoverable here (Tier 2 — elevated on density or price.). Sequence enforcement against this list, starting from tier 1.       |
|      7 | la Nova Esquerra de l'Eixample        |                  34 |                  60 |         0.567 | tier_2 | At 60-night cap, 34 listings recoverable here (Tier 2 — elevated on density or price.). Sequence enforcement against this list, starting from tier 1.       |
|      8 | el Raval                              |                  32 |                  86 |         0.372 | tier_2 | At 60-night cap, 32 listings recoverable here (Tier 2 — elevated on density or price.). Sequence enforcement against this list, starting from tier 1.       |
|      9 | Sant Antoni                           |                  28 |                  51 |         0.549 | tier_1 | At 60-night cap, 28 listings recoverable here (Tier 1 — high concentration AND high price.). Sequence enforcement against this list, starting from tier 1.  |
|     10 | Gothic Quarter                        |                  23 |                  71 |         0.324 | tier_2 | At 60-night cap, 23 listings recoverable here (Tier 2 — elevated on density or price.). Sequence enforcement against this list, starting from tier 1.       |

**London**

|   rank | geo_key          |   listings_impacted |   entire_home_count |   breach_rate | tier   | recommended_action                                                                                                                                         |
|-------:|:-----------------|--------------------:|--------------------:|--------------:|:-------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------|
|      1 | Paddington       |                  51 |                 128 |         0.398 | tier_1 | At 60-night cap, 51 listings recoverable here (Tier 1 — high concentration AND high price.). Sequence enforcement against this list, starting from tier 1. |
|      2 | Westbourne Green |                  48 |                 178 |         0.27  | tier_1 | At 60-night cap, 48 listings recoverable here (Tier 1 — high concentration AND high price.). Sequence enforcement against this list, starting from tier 1. |
|      3 | Whitechapel      |                  48 |                 148 |         0.324 | tier_2 | At 60-night cap, 48 listings recoverable here (Tier 2 — elevated on density or price.). Sequence enforcement against this list, starting from tier 1.      |
|      4 | Marylebone       |                  38 |                 153 |         0.248 | tier_1 | At 60-night cap, 38 listings recoverable here (Tier 1 — high concentration AND high price.). Sequence enforcement against this list, starting from tier 1. |
|      5 | Earl's Court     |                  35 |                 145 |         0.241 | tier_1 | At 60-night cap, 35 listings recoverable here (Tier 1 — high concentration AND high price.). Sequence enforcement against this list, starting from tier 1. |
|      6 | Chelsea          |                  33 |                 112 |         0.295 | tier_1 | At 60-night cap, 33 listings recoverable here (Tier 1 — high concentration AND high price.). Sequence enforcement against this list, starting from tier 1. |
|      7 | Fulham           |                  33 |                 113 |         0.292 | tier_1 | At 60-night cap, 33 listings recoverable here (Tier 1 — high concentration AND high price.). Sequence enforcement against this list, starting from tier 1. |
|      8 | Notting Hill     |                  32 |                 106 |         0.302 | tier_1 | At 60-night cap, 32 listings recoverable here (Tier 1 — high concentration AND high price.). Sequence enforcement against this list, starting from tier 1. |
|      9 | West Kensington  |                  30 |                  90 |         0.333 | tier_2 | At 60-night cap, 30 listings recoverable here (Tier 2 — elevated on density or price.). Sequence enforcement against this list, starting from tier 1.      |
|     10 | Brompton         |                  28 |                  95 |         0.295 | tier_1 | At 60-night cap, 28 listings recoverable here (Tier 1 — high concentration AND high price.). Sequence enforcement against this list, starting from tier 1. |

### Top impacted neighbourhoods — 30-night cap

**Barcelona**

|   rank | geo_key                               |   listings_impacted |   entire_home_count |   breach_rate | tier   | recommended_action                                                                                                                                          |
|-------:|:--------------------------------------|--------------------:|--------------------:|--------------:|:-------|:------------------------------------------------------------------------------------------------------------------------------------------------------------|
|      1 | la Dreta de l'Eixample                |                 119 |                 201 |         0.592 | tier_1 | At 30-night cap, 119 listings recoverable here (Tier 1 — high concentration AND high price.). Sequence enforcement against this list, starting from tier 1. |
|      2 | la Sagrada Família                    |                  61 |                 106 |         0.576 | tier_1 | At 30-night cap, 61 listings recoverable here (Tier 1 — high concentration AND high price.). Sequence enforcement against this list, starting from tier 1.  |
|      3 | el Poble-sec                          |                  54 |                  83 |         0.651 | tier_1 | At 30-night cap, 54 listings recoverable here (Tier 1 — high concentration AND high price.). Sequence enforcement against this list, starting from tier 1.  |
|      4 | l'Antiga Esquerra de l'Eixample       |                  51 |                  94 |         0.543 | tier_2 | At 30-night cap, 51 listings recoverable here (Tier 2 — elevated on density or price.). Sequence enforcement against this list, starting from tier 1.       |
|      5 | la Vila de Gràcia                     |                  43 |                  76 |         0.566 | tier_1 | At 30-night cap, 43 listings recoverable here (Tier 1 — high concentration AND high price.). Sequence enforcement against this list, starting from tier 1.  |
|      6 | Sant Pere, Santa Caterina i la Ribera |                  40 |                 100 |         0.4   | tier_2 | At 30-night cap, 40 listings recoverable here (Tier 2 — elevated on density or price.). Sequence enforcement against this list, starting from tier 1.       |
|      7 | la Nova Esquerra de l'Eixample        |                  36 |                  60 |         0.6   | tier_2 | At 30-night cap, 36 listings recoverable here (Tier 2 — elevated on density or price.). Sequence enforcement against this list, starting from tier 1.       |
|      8 | el Raval                              |                  35 |                  86 |         0.407 | tier_2 | At 30-night cap, 35 listings recoverable here (Tier 2 — elevated on density or price.). Sequence enforcement against this list, starting from tier 1.       |
|      9 | Sant Antoni                           |                  29 |                  51 |         0.569 | tier_1 | At 30-night cap, 29 listings recoverable here (Tier 1 — high concentration AND high price.). Sequence enforcement against this list, starting from tier 1.  |
|     10 | Gothic Quarter                        |                  26 |                  71 |         0.366 | tier_2 | At 30-night cap, 26 listings recoverable here (Tier 2 — elevated on density or price.). Sequence enforcement against this list, starting from tier 1.       |

**London**

|   rank | geo_key          |   listings_impacted |   entire_home_count |   breach_rate | tier   | recommended_action                                                                                                                                         |
|-------:|:-----------------|--------------------:|--------------------:|--------------:|:-------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------|
|      1 | Paddington       |                  58 |                 128 |         0.453 | tier_1 | At 30-night cap, 58 listings recoverable here (Tier 1 — high concentration AND high price.). Sequence enforcement against this list, starting from tier 1. |
|      2 | Whitechapel      |                  57 |                 148 |         0.385 | tier_2 | At 30-night cap, 57 listings recoverable here (Tier 2 — elevated on density or price.). Sequence enforcement against this list, starting from tier 1.      |
|      3 | Westbourne Green |                  51 |                 178 |         0.286 | tier_1 | At 30-night cap, 51 listings recoverable here (Tier 1 — high concentration AND high price.). Sequence enforcement against this list, starting from tier 1. |
|      4 | Marylebone       |                  48 |                 153 |         0.314 | tier_1 | At 30-night cap, 48 listings recoverable here (Tier 1 — high concentration AND high price.). Sequence enforcement against this list, starting from tier 1. |
|      5 | Earl's Court     |                  43 |                 145 |         0.297 | tier_1 | At 30-night cap, 43 listings recoverable here (Tier 1 — high concentration AND high price.). Sequence enforcement against this list, starting from tier 1. |
|      6 | Fulham           |                  43 |                 113 |         0.381 | tier_1 | At 30-night cap, 43 listings recoverable here (Tier 1 — high concentration AND high price.). Sequence enforcement against this list, starting from tier 1. |
|      7 | Chelsea          |                  42 |                 112 |         0.375 | tier_1 | At 30-night cap, 42 listings recoverable here (Tier 1 — high concentration AND high price.). Sequence enforcement against this list, starting from tier 1. |
|      8 | Notting Hill     |                  36 |                 106 |         0.34  | tier_1 | At 30-night cap, 36 listings recoverable here (Tier 1 — high concentration AND high price.). Sequence enforcement against this list, starting from tier 1. |
|      9 | Brompton         |                  35 |                  95 |         0.368 | tier_1 | At 30-night cap, 35 listings recoverable here (Tier 1 — high concentration AND high price.). Sequence enforcement against this list, starting from tier 1. |
|     10 | West Kensington  |                  34 |                  90 |         0.378 | tier_2 | At 30-night cap, 34 listings recoverable here (Tier 2 — elevated on density or price.). Sequence enforcement against this list, starting from tier 1.      |

### RESIDE simulation — Barcelona top 10

|   rank | geo_key                               |   reside_unregistered_count |   entire_home_count |   reside_share | recommended_action                                                                                                                                             |
|-------:|:--------------------------------------|----------------------------:|--------------------:|---------------:|:---------------------------------------------------------------------------------------------------------------------------------------------------------------|
|      1 | la Dreta de l'Eixample                |                          59 |                 201 |          0.293 | 59 entire-home listings without registration on record. Priority RESIDE compliance target — issue compliance notices and confirm phase-out timeline alignment. |
|      2 | Sant Pere, Santa Caterina i la Ribera |                          39 |                 100 |          0.39  | 39 entire-home listings without registration on record. Priority RESIDE compliance target — issue compliance notices and confirm phase-out timeline alignment. |
|      3 | Gothic Quarter                        |                          31 |                  71 |          0.437 | 31 entire-home listings without registration on record. Priority RESIDE compliance target — issue compliance notices and confirm phase-out timeline alignment. |
|      4 | el Raval                              |                          31 |                  86 |          0.36  | 31 entire-home listings without registration on record. Priority RESIDE compliance target — issue compliance notices and confirm phase-out timeline alignment. |
|      5 | la Sagrada Família                    |                          30 |                 106 |          0.283 | 30 entire-home listings without registration on record. Priority RESIDE compliance target — issue compliance notices and confirm phase-out timeline alignment. |
|      6 | la Vila de Gràcia                     |                          20 |                  76 |          0.263 | 20 entire-home listings without registration on record. Priority RESIDE compliance target — issue compliance notices and confirm phase-out timeline alignment. |
|      7 | la Barceloneta                        |                          19 |                  50 |          0.38  | 19 entire-home listings without registration on record. Priority RESIDE compliance target — issue compliance notices and confirm phase-out timeline alignment. |
|      8 | la Nova Esquerra de l'Eixample        |                          19 |                  60 |          0.317 | 19 entire-home listings without registration on record. Priority RESIDE compliance target — issue compliance notices and confirm phase-out timeline alignment. |
|      9 | el Poble-sec                          |                          18 |                  83 |          0.217 | 18 entire-home listings without registration on record. Priority RESIDE compliance target — issue compliance notices and confirm phase-out timeline alignment. |
|     10 | l'Antiga Esquerra de l'Eixample       |                          17 |                  94 |          0.181 | 17 entire-home listings without registration on record. Priority RESIDE compliance target — issue compliance notices and confirm phase-out timeline alignment. |

---
