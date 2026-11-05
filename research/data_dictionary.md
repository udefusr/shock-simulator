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

## Processed JODI fields

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

## Reserve profile dataset

File: `data/processed/reserve_profiles_initial.csv`

| Field | Description |
| --- | --- |
| country | Country covered by the record |
| source_organization | Government or stockholding agency publishing the information |
| stock_category | Definition of the stock category; categories differ by country |
| reference_date | Source observation date or date qualifier |
| inventory_quantity | Reported inventory quantity; blank means unknown/not reported |
| inventory_unit | Native unit for the inventory quantity |
| capacity_quantity | Reported storage capacity; not necessarily usable inventory |
| capacity_unit | Native unit for storage capacity |
| stock_cover_days | Reported stock-cover days, only where available |
| stock_cover_basis | Denominator and calculation definition for the day count |
| nominal_release_rate | Published nominal release capability, if available |
| release_rate_unit | Unit of the release rate |
| release_lead_time_days | Published lead time to first market delivery, if available |
| release_procedure | Text description of legal/operational release procedure |
| source_url | Direct source page |
| data_quality_notes | Scope, comparability and uncertainty notes |

Reserve profile records preserve native units and category definitions. Missing numeric fields mean not reported or not established; they do not mean zero.

## Reserve response event dataset

File: `data/raw/other/reserve_response_events.csv`

| Field | Description |
| --- | --- |
| event_id | Stable identifier for the event |
| country | Country associated with the policy action |
| decision_date | Date of the official decision or announcement |
| event_type | Government stock release or stockholding-obligation policy change |
| stock_category | Stock category affected |
| announced_quantity | Announced physical quantity, when specified |
| quantity_unit | Native unit of the announced quantity |
| equivalent_days | Officially stated days-of-supply equivalent, where available |
| obligation_reduction_days | Reduction in a stockholding obligation, where applicable |
| announcement_status | Decision/announcement status and wording |
| implementation_start | Stated start of implementation |
| implementation_end | Stated end of implementation, if available |
| source_organization | Issuing authority |
| source_url | Direct official notice |
| data_quality_notes | Distinguishes announced plans from verified physical withdrawals |

The Japan entries record official announcements and a temporary obligation reduction. Announced release volumes must not be treated as verified physical withdrawals.

## Reserve validation outputs

`src/reserve_data.py` provides:
- `load_reserve_profiles()` and `validate_reserve_profiles()`
- `load_reserve_response_events()` and `validate_reserve_response_events()`

The validation script checks required columns, numeric values, non-negative quantities, duplicate record identifiers, source URLs, and date consistency.

## Missing-value handling

Original JODI markers are preserved.

Missing or unavailable values in reserve datasets remain blank/NaN. They must never be silently replaced with zero.
