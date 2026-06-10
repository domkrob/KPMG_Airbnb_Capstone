# Golden Answers — 7 Canonical Questions

_Generated on 2026-06-10._

Member 4 evaluates the chatbot against these numbers. Target: ≥90% accuracy. Numbers come directly from `data/processed/neighbourhood_kpis.csv`.

---

## Q1 — Which neighbourhoods have the highest concentration of STRs?

_Method: Top 10 subdivisions per city by str_density._

### Barcelona

|   rank | geo_key                               |   str_density |
|-------:|:--------------------------------------|--------------:|
|      1 | la Dreta de l'Eixample                |           295 |
|      2 | el Raval                              |           203 |
|      3 | Sant Pere, Santa Caterina i la Ribera |           163 |
|      4 | Gothic Quarter                        |           160 |
|      5 | l'Antiga Esquerra de l'Eixample       |           148 |
|      6 | la Sagrada Família                    |           144 |
|      7 | el Poble-sec                          |           118 |
|      8 | la Nova Esquerra de l'Eixample        |           114 |
|      9 | la Vila de Gràcia                     |           104 |
|     10 | Sant Antoni                           |            79 |

### London

|   rank | geo_key                  |   str_density |
|-------:|:-------------------------|--------------:|
|      1 | Whitechapel              |           242 |
|      2 | Westbourne Green         |           210 |
|      3 | Marylebone               |           178 |
|      4 | Earl's Court             |           168 |
|      5 | Paddington               |           152 |
|      6 | Fulham                   |           139 |
|      7 | West Kensington          |           127 |
|      8 | Chelsea                  |           123 |
|      9 | Notting Hill             |           119 |
|     10 | London Borough of Ealing |           117 |

---

## Q2 — Where is Airbnb most likely removing homes from the long-term residential market?

_Method: Top 10 subdivisions per city by entire_home_share, restricted to neighbourhoods with str_density >= 30._

### Barcelona

|   rank | geo_key                            |   str_density |   entire_home_count |   entire_home_share |
|-------:|:-----------------------------------|--------------:|--------------------:|--------------------:|
|      1 | les Corts                          |            32 |                  28 |               0.875 |
|      2 | el Camp d'en Grassot i Gràcia Nova |            37 |                  29 |               0.784 |
|      3 | la Sagrada Família                 |           144 |                 106 |               0.736 |
|      4 | la Barceloneta                     |            68 |                  50 |               0.735 |
|      5 | la Vila de Gràcia                  |           104 |                  76 |               0.731 |
|      6 | el Poblenou                        |            59 |                  43 |               0.729 |
|      7 | Sant Gervasi - Galvany             |            44 |                  32 |               0.727 |
|      8 | el Poble-sec                       |           118 |                  83 |               0.703 |
|      9 | la Dreta de l'Eixample             |           295 |                 201 |               0.681 |
|     10 | Sant Antoni                        |            79 |                  51 |               0.646 |

### London

|   rank | geo_key                      |   str_density |   entire_home_count |   entire_home_share |
|-------:|:-----------------------------|--------------:|--------------------:|--------------------:|
|      1 | Brompton                     |           100 |                  95 |               0.95  |
|      2 | London Borough of Wandsworth |            36 |                  34 |               0.944 |
|      3 | Mayfair                      |            33 |                  31 |               0.939 |
|      4 | Chelsea                      |           123 |                 112 |               0.911 |
|      5 | Notting Hill                 |           119 |                 106 |               0.891 |
|      6 | South Kensington             |            87 |                  76 |               0.874 |
|      7 | Holborn                      |            74 |                  64 |               0.865 |
|      8 | Earl's Court                 |           168 |                 145 |               0.863 |
|      9 | Marylebone                   |           178 |                 153 |               0.86  |
|     10 | Shoreditch                   |            63 |                  54 |               0.857 |

---

## Q3 — Which neighbourhoods are dominated by commercial/professional hosts?

_Method: Top 10 subdivisions per city by commercial_host_share (commercial+super_commercial tiers, ≥5 listings/host), restricted to str_density >= 30._

### Barcelona

|   rank | geo_key                         |   str_density |   commercial_host_share |   multi_listing_host_share |
|-------:|:--------------------------------|--------------:|------------------------:|---------------------------:|
|      1 | la Nova Esquerra de l'Eixample  |           114 |                   0.404 |                      0.57  |
|      2 | el Poble-sec                    |           118 |                   0.364 |                      0.559 |
|      3 | l'Antiga Esquerra de l'Eixample |           148 |                   0.345 |                      0.635 |
|      4 | Sant Antoni                     |            79 |                   0.329 |                      0.595 |
|      5 | Sant Gervasi - Galvany          |            44 |                   0.318 |                      0.659 |
|      6 | la Sagrada Família              |           144 |                   0.285 |                      0.479 |
|      7 | Hostafrancs                     |            32 |                   0.281 |                      0.469 |
|      8 | el Fort Pienc                   |            67 |                   0.269 |                      0.522 |
|      9 | la Dreta de l'Eixample          |           295 |                   0.264 |                      0.651 |
|     10 | la Vila de Gràcia               |           104 |                   0.25  |                      0.519 |

### London

|   rank | geo_key                 |   str_density |   commercial_host_share |   multi_listing_host_share |
|-------:|:------------------------|--------------:|------------------------:|---------------------------:|
|      1 | Bayswater               |            31 |                   0.387 |                      0.645 |
|      2 | Notting Hill            |           119 |                   0.37  |                      0.538 |
|      3 | Earl's Court            |           168 |                   0.357 |                      0.607 |
|      4 | Brondesbury             |            55 |                   0.309 |                      0.582 |
|      5 | Mayfair                 |            33 |                   0.303 |                      0.727 |
|      6 | Paddington              |           152 |                   0.289 |                      0.52  |
|      7 | South Kensington        |            87 |                   0.287 |                      0.609 |
|      8 | South Hampstead         |            36 |                   0.278 |                      0.444 |
|      9 | London Borough of Brent |            59 |                   0.271 |                      0.407 |
|     10 | King's Cross            |            85 |                   0.271 |                      0.6   |

---

## Q4 — In which neighbourhoods does high STR density coincide with high prices?

_Method: Subdivisions in top quartile of BOTH str_density AND median_nightly_price per city (str_density >= 30)._

### Barcelona

Correlation between density and price: **0.298**

| geo_key                |   str_density |   median_nightly_price |
|:-----------------------|--------------:|-----------------------:|
| la Dreta de l'Eixample |           295 |                  265.6 |

### London

Correlation between density and price: **0.258**

| geo_key          |   str_density |   median_nightly_price |
|:-----------------|--------------:|-----------------------:|
| Westbourne Green |           210 |                  250.2 |
| Marylebone       |           178 |                  273.4 |
| Earl's Court     |           168 |                  245.2 |
| Paddington       |           152 |                  301.5 |
| Fulham           |           139 |                  235.7 |
| Chelsea          |           123 |                  405.2 |
| Notting Hill     |           119 |                  234.1 |
| Fitzrovia        |           104 |                  224.8 |
| Brompton         |           100 |                  306.6 |
| South Kensington |            87 |                  409.9 |
| Holborn          |            74 |                  299.9 |
| Kensington       |            74 |                  273.7 |

---

## Q5 — Which neighbourhoods are saturated, and which are emerging hotspots?

_Method: Saturated = composite of high density + entire-home share + commercial-host share + occupancy. Emerging = top active-listing growth (recent 6 mo vs prior 6 mo). Member 3 will replace the saturated heuristic with the proper KMeans cluster label._

### Saturated — across both cities

**Barcelona**

|   rank | geo_key                            |   str_density |   entire_home_share |   commercial_host_share |   avg_occupancy |   saturation_score |
|-------:|:-----------------------------------|--------------:|--------------------:|------------------------:|----------------:|-------------------:|
|      1 | la Dreta de l'Eixample             |           295 |               0.681 |                   0.264 |           0.23  |               4.21 |
|      2 | el Poble-sec                       |           118 |               0.703 |                   0.364 |           0.233 |               3.06 |
|      3 | la Sagrada Família                 |           144 |               0.736 |                   0.285 |           0.245 |               2.98 |
|      4 | l'Antiga Esquerra de l'Eixample    |           148 |               0.635 |                   0.345 |           0.206 |               2.26 |
|      5 | la Nova Esquerra de l'Eixample     |           114 |               0.526 |                   0.404 |           0.241 |               2.2  |
|      6 | la Vila de Gràcia                  |           104 |               0.731 |                   0.25  |           0.228 |               1.67 |
|      7 | el Camp d'en Grassot i Gràcia Nova |            37 |               0.784 |                   0.135 |           0.32  |               1.4  |
|      8 | Sant Antoni                        |            79 |               0.646 |                   0.329 |           0.217 |               1.37 |
|      9 | Sant Gervasi - Galvany             |            44 |               0.727 |                   0.318 |           0.168 |               0.54 |
|     10 | les Corts                          |            32 |               0.875 |                   0.25  |           0.139 |               0.25 |

**London**

|   rank | geo_key          |   str_density |   entire_home_share |   commercial_host_share |   avg_occupancy |   saturation_score |
|-------:|:-----------------|--------------:|--------------------:|------------------------:|----------------:|-------------------:|
|      1 | Notting Hill     |           119 |               0.891 |                   0.37  |           0.161 |               6.36 |
|      2 | Earl's Court     |           168 |               0.863 |                   0.357 |           0.105 |               6.18 |
|      3 | Westbourne Green |           210 |               0.848 |                   0.262 |           0.106 |               6.14 |
|      4 | Paddington       |           152 |               0.842 |                   0.289 |           0.167 |               6.08 |
|      5 | Whitechapel      |           242 |               0.612 |                   0.157 |           0.17  |               5.16 |
|      6 | Marylebone       |           178 |               0.86  |                   0.191 |           0.112 |               4.74 |
|      7 | Chelsea          |           123 |               0.911 |                   0.268 |           0.106 |               4.44 |
|      8 | South Kensington |            87 |               0.874 |                   0.287 |           0.145 |               4.19 |
|      9 | Shoreditch       |            63 |               0.857 |                   0.222 |           0.217 |               4.14 |
|     10 | Waterloo         |            30 |               0.767 |                   0.267 |           0.259 |               3.87 |

### Emerging — across both cities

**Barcelona**

|   rank | geo_key               |   prior_active |   recent_active |   active_growth_pct |
|-------:|:----------------------|---------------:|----------------:|--------------------:|
|      1 | Can Baró              |            5   |             6   |                20   |
|      2 | la Sagrera            |            5   |             5   |                 0   |
|      3 | la Font de la Guatlla |            9   |             9   |                 0   |
|      4 | les Corts             |           21.5 |            21.2 |                -1.6 |
|      5 | el Baix Guinardó      |           12   |            11.2 |                -6.9 |

**London**

|   rank | geo_key      |   prior_active |   recent_active |   active_growth_pct |
|-------:|:-------------|---------------:|----------------:|--------------------:|
|      1 | Greenford    |            5   |             5.7 |                13.3 |
|      2 | Abbey Wood   |            5.8 |             6.5 |                11.4 |
|      3 | Gants Hill   |            5   |             5.5 |                10   |
|      4 | North Sheen  |            9.8 |            10   |                 1.7 |
|      5 | Earlsfield   |           13.5 |            13.7 |                 1.2 |
|      6 | East Sheen   |            6   |             6   |                 0   |
|      7 | Edmonton     |            5   |             5   |                 0   |
|      8 | Finchley     |            8.3 |             8.2 |                -2   |
|      9 | Highams Park |            9.5 |             9.2 |                -3.5 |
|     10 | Selhurst     |            9   |             8.7 |                -3.7 |

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
| barcelona |            10 |               0.53  |                   0.134 |           0.132 |                 118.85 |            0.447 |
| london    |             8 |               0.625 |                   0     |           0.086 |                 142.75 |            0.188 |

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

|   rank | geo_key                               |   listings_impacted |   entire_home_count |   breach_rate |
|-------:|:--------------------------------------|--------------------:|--------------------:|--------------:|
|      1 | la Dreta de l'Eixample                |                  95 |                 201 |         0.473 |
|      2 | la Sagrada Família                    |                  53 |                 106 |         0.5   |
|      3 | el Poble-sec                          |                  46 |                  83 |         0.554 |
|      4 | l'Antiga Esquerra de l'Eixample       |                  43 |                  94 |         0.457 |
|      5 | la Vila de Gràcia                     |                  34 |                  76 |         0.447 |
|      6 | Sant Pere, Santa Caterina i la Ribera |                  31 |                 100 |         0.31  |
|      7 | la Nova Esquerra de l'Eixample        |                  31 |                  60 |         0.517 |
|      8 | el Raval                              |                  28 |                  86 |         0.326 |
|      9 | Sant Antoni                           |                  26 |                  51 |         0.51  |
|     10 | el Poblenou                           |                  21 |                  43 |         0.488 |

**London**

|   rank | geo_key          |   listings_impacted |   entire_home_count |   breach_rate |
|-------:|:-----------------|--------------------:|--------------------:|--------------:|
|      1 | Whitechapel      |                  44 |                 148 |         0.297 |
|      2 | Paddington       |                  42 |                 128 |         0.328 |
|      3 | Westbourne Green |                  41 |                 178 |         0.23  |
|      4 | Marylebone       |                  35 |                 153 |         0.229 |
|      5 | Chelsea          |                  26 |                 112 |         0.232 |
|      6 | North Kensington |                  26 |                  82 |         0.317 |
|      7 | Barnsbury        |                  24 |                  77 |         0.312 |
|      8 | West Kensington  |                  24 |                  90 |         0.267 |
|      9 | Earl's Court     |                  23 |                 145 |         0.159 |
|     10 | Shoreditch       |                  23 |                  54 |         0.426 |

### Top impacted neighbourhoods — 60-night cap

**Barcelona**

|   rank | geo_key                               |   listings_impacted |   entire_home_count |   breach_rate |
|-------:|:--------------------------------------|--------------------:|--------------------:|--------------:|
|      1 | la Dreta de l'Eixample                |                 111 |                 201 |         0.552 |
|      2 | la Sagrada Família                    |                  57 |                 106 |         0.538 |
|      3 | el Poble-sec                          |                  49 |                  83 |         0.59  |
|      4 | l'Antiga Esquerra de l'Eixample       |                  46 |                  94 |         0.489 |
|      5 | la Vila de Gràcia                     |                  39 |                  76 |         0.513 |
|      6 | Sant Pere, Santa Caterina i la Ribera |                  35 |                 100 |         0.35  |
|      7 | la Nova Esquerra de l'Eixample        |                  34 |                  60 |         0.567 |
|      8 | el Raval                              |                  32 |                  86 |         0.372 |
|      9 | Sant Antoni                           |                  28 |                  51 |         0.549 |
|     10 | Gothic Quarter                        |                  23 |                  71 |         0.324 |

**London**

|   rank | geo_key          |   listings_impacted |   entire_home_count |   breach_rate |
|-------:|:-----------------|--------------------:|--------------------:|--------------:|
|      1 | Paddington       |                  51 |                 128 |         0.398 |
|      2 | Westbourne Green |                  48 |                 178 |         0.27  |
|      3 | Whitechapel      |                  48 |                 148 |         0.324 |
|      4 | Marylebone       |                  38 |                 153 |         0.248 |
|      5 | Earl's Court     |                  35 |                 145 |         0.241 |
|      6 | Chelsea          |                  33 |                 112 |         0.295 |
|      7 | Fulham           |                  33 |                 113 |         0.292 |
|      8 | Notting Hill     |                  32 |                 106 |         0.302 |
|      9 | West Kensington  |                  30 |                  90 |         0.333 |
|     10 | Brompton         |                  28 |                  95 |         0.295 |

### Top impacted neighbourhoods — 30-night cap

**Barcelona**

|   rank | geo_key                               |   listings_impacted |   entire_home_count |   breach_rate |
|-------:|:--------------------------------------|--------------------:|--------------------:|--------------:|
|      1 | la Dreta de l'Eixample                |                 119 |                 201 |         0.592 |
|      2 | la Sagrada Família                    |                  61 |                 106 |         0.576 |
|      3 | el Poble-sec                          |                  54 |                  83 |         0.651 |
|      4 | l'Antiga Esquerra de l'Eixample       |                  51 |                  94 |         0.543 |
|      5 | la Vila de Gràcia                     |                  43 |                  76 |         0.566 |
|      6 | Sant Pere, Santa Caterina i la Ribera |                  40 |                 100 |         0.4   |
|      7 | la Nova Esquerra de l'Eixample        |                  36 |                  60 |         0.6   |
|      8 | el Raval                              |                  35 |                  86 |         0.407 |
|      9 | Sant Antoni                           |                  29 |                  51 |         0.569 |
|     10 | Gothic Quarter                        |                  26 |                  71 |         0.366 |

**London**

|   rank | geo_key          |   listings_impacted |   entire_home_count |   breach_rate |
|-------:|:-----------------|--------------------:|--------------------:|--------------:|
|      1 | Paddington       |                  58 |                 128 |         0.453 |
|      2 | Whitechapel      |                  57 |                 148 |         0.385 |
|      3 | Westbourne Green |                  51 |                 178 |         0.286 |
|      4 | Marylebone       |                  48 |                 153 |         0.314 |
|      5 | Earl's Court     |                  43 |                 145 |         0.297 |
|      6 | Fulham           |                  43 |                 113 |         0.381 |
|      7 | Chelsea          |                  42 |                 112 |         0.375 |
|      8 | Notting Hill     |                  36 |                 106 |         0.34  |
|      9 | Brompton         |                  35 |                  95 |         0.368 |
|     10 | West Kensington  |                  34 |                  90 |         0.378 |

### RESIDE simulation — Barcelona top 10

|   rank | geo_key                               |   reside_unregistered_count |   entire_home_count |   reside_share |
|-------:|:--------------------------------------|----------------------------:|--------------------:|---------------:|
|      1 | la Dreta de l'Eixample                |                          59 |                 201 |          0.293 |
|      2 | Sant Pere, Santa Caterina i la Ribera |                          39 |                 100 |          0.39  |
|      3 | Gothic Quarter                        |                          31 |                  71 |          0.437 |
|      4 | el Raval                              |                          31 |                  86 |          0.36  |
|      5 | la Sagrada Família                    |                          30 |                 106 |          0.283 |
|      6 | la Vila de Gràcia                     |                          20 |                  76 |          0.263 |
|      7 | la Barceloneta                        |                          19 |                  50 |          0.38  |
|      8 | la Nova Esquerra de l'Eixample        |                          19 |                  60 |          0.317 |
|      9 | el Poble-sec                          |                          18 |                  83 |          0.217 |
|     10 | l'Antiga Esquerra de l'Eixample       |                          17 |                  94 |          0.181 |

---
