
# Data Dictionary

## JODI source fields

| Field | Description |
| --- | --- |
| REF_AREA | Reporting economy code |
| TIME_PERIOD | Monthly observation period |
| ENERGY_PRODUCT | Energy product classification |
| FLOW_BREAKDOWN | Production, trade, stock, or other flow classification |
| UNIT_MEASURE | Original measurement unit |
| OBS_VALUE | Original observation value |
| ASSESSMENT_CODE | JODI assessment classification |

## Processed fields

| Field | Description |
| --- | --- |
| OBS_VALUE_NUMERIC | Parsed numerical observation |
| OBS_VALUE_STATUS | Classification of original value |
| OBSERVATION_DATE | Standardized monthly date |
| SOURCE_FILE | Original CSV filename |
| COUNTRY_NAME | Human-readable country name |
| INDICATOR | Human-readable indicator description |
| EXPECTED_UNIT | Expected physical measurement unit |

## Measurement units

| Unit | Meaning |
| --- | --- |
| KBD | Thousand barrels per day |
| KBBL | Thousand barrels |
| KL | Thousand kilolitres |
| KTONS | Thousand metric tonnes |
| CONVBBL | Barrel conversion factor |

Different units must not be combined without an explicit and documented conversion.

## EIA data fields

### Chokepoint dataset

| Field | Description |
| --- | --- |
| Quarter | Reporting quarter |
| Route | Maritime chokepoint or route |
| Flow_million_barrels_per_day | Average daily oil flow |
| Data_status | Estimate or other source status |
| Source_report | EIA publication |
| Publication_date | Publication date |
| Source_URL | Source location |

### Production shut-in dataset

| Field | Description |
| --- | --- |
| Country | Reporting producer |
| Feb_2026_production_kbd | February production baseline |
| Mar_Jul_average_shutins_kbd | Estimated average production shut-ins |
| Aug_2026_shutins_kbd | Estimated August shut-ins |
| Sep_2026_shutins_kbd | Estimated September shut-ins |
| Q4_2026_forecast_shutins_kbd | Aggregate forecast |
| Q1_2027_forecast_shutins_kbd | Aggregate forecast |

EIA estimates and forecasts must not be represented as direct production observations.

## Missing-value handling

Original markers are preserved.

Missing or unavailable values must never be silently replaced with zero.
