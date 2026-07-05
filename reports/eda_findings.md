# EDA Findings — Urban Rental Intelligence Copilot

Auto-generated narrative for Member 4 to lift into the chatbot system prompt.

## Citywide overview

| city      |   total_listings |   unique_hosts |   unique_subdivisions |   active_listings |   entire_homes |   entire_home_share |   median_nightly_price |   median_occupancy_active |   mean_occupancy_active |   total_revenue |   breach_90_total |   reside_unregistered_total |
|:----------|-----------------:|---------------:|----------------------:|------------------:|---------------:|--------------------:|-----------------------:|--------------------------:|------------------------:|----------------:|------------------:|----------------------------:|
| barcelona |             2594 |           1637 |                    66 |              1655 |           1539 |               0.593 |                  156   |                     0.044 |                   0.21  |     5.21592e+07 |               642 |                         421 |
| london    |             9643 |           7312 |                   455 |              5967 |           6536 |               0.678 |                  174.7 |                     0     |                   0.137 |     1.22631e+08 |              1485 |                        2572 |

## Headline rankings

### Barcelona — top 10 by `str_density`

| city      | geo_key                               |   str_density |
|:----------|:--------------------------------------|--------------:|
| barcelona | la Dreta de l'Eixample                |           295 |
| barcelona | el Raval                              |           203 |
| barcelona | Sant Pere, Santa Caterina i la Ribera |           163 |
| barcelona | Gothic Quarter                        |           160 |
| barcelona | l'Antiga Esquerra de l'Eixample       |           148 |
| barcelona | la Sagrada Família                    |           144 |
| barcelona | el Poble-sec                          |           118 |
| barcelona | la Nova Esquerra de l'Eixample        |           114 |
| barcelona | la Vila de Gràcia                     |           104 |
| barcelona | Sant Antoni                           |            79 |

### London — top 10 by `str_density`

| city   | geo_key                  |   str_density |
|:-------|:-------------------------|--------------:|
| london | Whitechapel              |           242 |
| london | Westbourne Green         |           210 |
| london | Marylebone               |           178 |
| london | Earl's Court             |           168 |
| london | Paddington               |           152 |
| london | Fulham                   |           139 |
| london | West Kensington          |           127 |
| london | Chelsea                  |           123 |
| london | Notting Hill             |           119 |
| london | London Borough of Ealing |           117 |

### Barcelona — top 10 by `breach_count_90`

| city      | geo_key                               |   str_density |   breach_count_90 |
|:----------|:--------------------------------------|--------------:|------------------:|
| barcelona | la Dreta de l'Eixample                |           295 |                95 |
| barcelona | la Sagrada Família                    |           144 |                53 |
| barcelona | el Poble-sec                          |           118 |                46 |
| barcelona | l'Antiga Esquerra de l'Eixample       |           148 |                43 |
| barcelona | la Vila de Gràcia                     |           104 |                34 |
| barcelona | Sant Pere, Santa Caterina i la Ribera |           163 |                31 |
| barcelona | la Nova Esquerra de l'Eixample        |           114 |                31 |
| barcelona | el Raval                              |           203 |                28 |
| barcelona | Sant Antoni                           |            79 |                26 |
| barcelona | el Poblenou                           |            59 |                21 |

### London — top 10 by `breach_count_90`

| city   | geo_key          |   str_density |   breach_count_90 |
|:-------|:-----------------|--------------:|------------------:|
| london | Whitechapel      |           242 |                44 |
| london | Paddington       |           152 |                42 |
| london | Westbourne Green |           210 |                41 |
| london | Marylebone       |           178 |                35 |
| london | North Kensington |           104 |                26 |
| london | Chelsea          |           123 |                26 |
| london | Barnsbury        |           109 |                24 |
| london | West Kensington  |           127 |                24 |
| london | Earl's Court     |           168 |                23 |
| london | Shoreditch       |            63 |                23 |

## Emerging hotspots (recent 6 months vs prior 6 months)

| city      | geo_key               |   recent_active |   recent_revenue |   prior_active |   prior_revenue |   active_growth_pct |   revenue_growth_pct |
|:----------|:----------------------|----------------:|-----------------:|---------------:|----------------:|--------------------:|---------------------:|
| barcelona | Can Baró              |         6       |          8778.33 |        5       |        14625    |               20    |               -39.98 |
| london    | Greenford             |         5.66667 |          3695.17 |        5       |         4442    |               13.33 |               -16.81 |
| london    | Abbey Wood            |         6.5     |          4787.5  |        5.83333 |         5040    |               11.43 |                -5.01 |
| london    | Gants Hill            |         5.5     |          7942.5  |        5       |        13511.7  |               10    |               -41.22 |
| london    | North Sheen           |        10       |          8711.83 |        9.83333 |        19660    |                1.69 |               -55.69 |
| london    | Earlsfield            |        13.6667  |         24511.7  |       13.5     |        31707.8  |                1.23 |               -22.7  |
| barcelona | la Sagrera            |         5       |         11060.3  |        5       |         9022.5  |                0    |                22.59 |
| barcelona | la Font de la Guatlla |         9       |         27400.7  |        9       |        43386.2  |                0    |               -36.84 |
| london    | East Sheen            |         6       |          8280.17 |        6       |         9813.5  |                0    |               -15.62 |
| london    | Edmonton              |         5       |          4860.5  |        5       |         8040    |                0    |               -39.55 |
| barcelona | les Corts             |        21.1667  |         29723    |       21.5     |        58216.8  |               -1.55 |               -48.94 |
| london    | Finchley              |         8.16667 |          1637.67 |        8.33333 |         6933.17 |               -2    |               -76.38 |
| london    | Highams Park          |         9.16667 |         15716.7  |        9.5     |        19005.3  |               -3.51 |               -17.3  |
| london    | Selhurst              |         8.66667 |          8066.5  |        9       |         8935.5  |               -3.7  |                -9.73 |
| london    | Clapton               |        30       |         29211.7  |       31.3333  |        60828    |               -4.26 |               -51.98 |

## Cross-city comparison medians

| metric                       | city      |     value |
|:-----------------------------|:----------|----------:|
| Median STR density           | barcelona |  10       |
| Median STR density           | london    |   8       |
| Median entire-home share     | barcelona |   0.5298  |
| Median entire-home share     | london    |   0.625   |
| Median commercial host share | barcelona |   0.1342  |
| Median commercial host share | london    |   0       |
| Mean avg_occupancy           | barcelona |   0.12405 |
| Mean avg_occupancy           | london    |   0.07775 |
| Median nightly price         | barcelona | 118.85    |
| Median nightly price         | london    | 142.75    |
| Median 90-night breach rate  | barcelona |   0.4474  |
| Median 90-night breach rate  | london    |   0.1875  |

## Caveats to surface in the chatbot

- AirDNA is a sample (~14% of BCN, ~10% of LDN STR universe). Numbers are directional, not market-wide totals.
- Association, not causation — high STR density correlates with rent pressure but does not prove causation.
- `professional_management` was null in ~54% of LDN raw — share computed only over reported cases.
- Subdivision coverage gap: 9% BCN / 12% LDN listings have no subdivision; LDN choropleths roll up to borough.
- Time coverage: March 2021 – February 2026.