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


## Reserve calibration outputs

The evidence-aware adapter in src/reserve_calibration.py derives the following fields. These are calculated model inputs, not original source observations.

| Field | Description |
| --- | --- |
| derived_stock_cover_days | Reported inventory divided by the analyst-supplied physical daily-flow denominator |
| nominal_release_as_share_of_daily_demand | Reported nominal daily release rate divided by the same physical denominator |
| physical_daily_demand | User-supplied physical daily-flow denominator |
| physical_daily_demand_unit | Required compatible unit, e.g. million barrels per day |
| demand_denominator_basis | Analyst's written definition of the chosen denominator |
| model_daily_demand | Chosen daily demand in normalized simulation units |
| initial_reserves_model_units | Derived stock-cover days multiplied by model daily demand |
| reserve_release_limit_model_units | Nominal release share multiplied by model daily demand |
| reserve_release_start_day | Lead time plus one, because simulation day 1 is the decision day |
| calibration_status | Statement identifying the values as derived from reported evidence and a user-supplied denominator |

The reserve simulation daily output includes reserve_release_active, indicating whether reserve deployment is enabled and past its configured mobilisation day. This flag is distinct from reserve_release, which can remain zero when there is no deficit.

## Announced-release denominator check

The Japan event adapter calculates announced_quantity / equivalent_days as an implied daily-supply denominator. It is not a physical release rate, actual withdrawal series, or implementation schedule. The calculation is kept separate from reserve calibration.


## Deterministic uncertainty outputs

The full-factorial design output in src/uncertainty.py contains:

| Field | Description |
| --- | --- |
| shock_loss_multiplier | Multiplier applied to the scenario's baseline shock percentage |
| shock_loss_pct | Resulting supply-loss percentage |
| shock_duration_multiplier | Multiplier applied to the scenario shock duration |
| shock_duration_days | Resulting duration rounded to the nearest whole day |
| reserve_inventory_fraction | Fraction of baseline normalized reserve inventory |
| initial_reserves_model_units | Initial reserve inventory after applying the fraction |
| release_limit_fraction | Fraction of baseline normalized daily reserve release cap |
| release_limit_model_units_per_day | Daily release cap after applying the fraction |
| recovery_rate_multiplier | Multiplier applied to the baseline supply recovery rate |
| recovery_rate | Resulting daily recovery rate |
| additional_mobilization_delay_days | Additional delay beyond the base mobilisation day |
| reserve_release_start_day | First day on which reserve delivery is enabled |
| total_unmet_demand | Cumulative unmet demand over the simulation horizon |
| shortage_days | Number of days with positive unmet demand |
| critical_days | Days classified Critical or Severe |
| severe_days | Days classified Severe |
| maximum_shortage_percentage | Largest daily unmet-demand percentage |
| remaining_reserves | Reserve inventory remaining at the end of the simulation |
| total_reserve_released | Initial reserve inventory minus remaining inventory |

The factor-effect output reports the low and high factor levels, mean total unmet demand at each level averaged across the other factors, the signed high-minus-low difference, its absolute value, and rank.

The median outcome is the median of enumerated design points, not an expected value. Design-point counts do not imply likelihood.


## Time-varying reserve release output

When `reserve_release_schedule` is supplied to `run_simulation`, its periods are measured in days since the first modeled reserve delivery (drawdown day 1), not calendar simulation day or decision day. Each period contains `start_day`, `end_day` (inclusive; `None` for the final open-ended period), and `rate_multiplier` (0–1) applied to the nominal `reserve_release_limit`.

Daily simulation outputs add:

| Field | Description |
| --- | --- |
| reserve_drawdown_day | Day number since first modeled reserve delivery; blank before mobilisation |
| reserve_release_rate_multiplier | Schedule multiplier active on that day; zero before mobilisation |
| reserve_release_limit_today | Effective model-unit daily cap after applying the schedule; zero before mobilisation |


## Importer-country route-flow dataset

File: `data/processed/hormuz_importer_flows_2025.csv`

| Field | Description |
| --- | --- |
| country | Destination market |
| reference_year | Calendar year represented by the route-flow observation |
| commodity | Crude oil and condensates; does not include LNG or a separate oil-products series |
| baseline_hormuz_flow_mbd | Estimated seaborne destination flow via Hormuz, million barrels/day |
| source_organization | Publisher of the visualization |
| data_provider | Provider of the underlying estimate |
| source_url | Source page for the destination-flow graphic |
| data_status | Source classification and provenance note |
| limitations | Known rounding and scope limitations |

The destination-flow values are estimates, rounded to 0.1 million barrels/day. They are not country total imports or national import-dependency percentages.

## Importer resilience inputs and outputs

Function: `run_importer_resilience_scenario()` in `src/importer_resilience.py`.

| Input | Description |
| --- | --- |
| disruption_fraction | Share of the baseline Hormuz flow assumed unavailable (0–1) |
| disruption_duration_days | Number of days for which the disruption applies |
| alternative_supply_mbd | Analyst-defined replacement supply capacity, capped by the daily lost flow |
| alternative_supply_start_day | First day replacement supply is available |
| buffer_cover_days | Analyst-defined buffer volume expressed as days of disrupted Hormuz flow |
| simulation_days | Total scenario horizon; defaults to disruption duration plus 30 recovery/observation days |

Daily output fields:

| Field | Description |
| --- | --- |
| gross_lost_imports_mbd | Gross lost destination flow on the day |
| alternative_supply_mbd | Replacement volume assumed available on the day |
| buffer_release_mbd | Buffer volume released to cover the residual gap |
| uncovered_import_gap_mbd | Residual daily lost flow after replacement and buffer release |
| buffer_remaining_million_barrels | Remaining modeled buffer inventory |
| cumulative_uncovered_gap_million_barrels | Sum of uncovered daily gaps over the simulation horizon |

The buffer is a scenario assumption, not a measured national strategic stock. Summing a million-barrel/day rate over one-day time steps yields million barrels.


## LNG importer route-flow dataset

File: `data/processed/hormuz_importer_lng_flows_2025.csv`

| Field | Description |
| --- | --- |
| country | LNG destination market |
| reference_year | Calendar year represented by the annual flow |
| annual_hormuz_lng_flow_bcm | Estimated annual LNG volume transiting Hormuz, billion cubic metres |
| source_organization | Organization publishing the destination-flow chart |
| data_provider | Underlying commercial data provider cited by the publisher |
| source_url | Direct report URL |
| data_status | Source description and evidence classification |
| limitations | Scope and interpretation restrictions |

The ACER report reproduces the ICIS destination estimates. They are annual route-specific destination volumes, not total country LNG imports.

## LNG importer resilience inputs and outputs

Function: `run_lng_importer_resilience_scenario()` in `src/importer_lng_resilience.py`.

All rate and volume fields are gas volumes: million cubic metres/day (mcm/day) and million cubic metres (mcm).

| Input | Description |
| --- | --- |
| disruption_fraction | Share of annual-average Hormuz destination flow assumed interrupted (0–1) |
| disruption_duration_days | Disruption duration |
| alternative_supply_mcm_per_day | Analyst-defined replacement LNG delivery rate |
| alternative_supply_start_day | First day alternative LNG is available |
| buffer_cover_days | Assumed buffer stock expressed as days of the gross disrupted flow |
| demand_reduction_fraction | Demand response as a share of gross lost flow, capped by the residual daily gap |
| simulation_days | Model horizon; defaults to disruption duration plus 30 days |
| days_in_year | 365 or 366 for annual-flow averaging |

Daily outputs:

| Field | Description |
| --- | --- |
| gross_lost_lng_mcm_per_day | Gross daily lost Hormuz LNG flow |
| alternative_lng_mcm_per_day | Replacement LNG supply applied that day |
| buffer_release_mcm_per_day | Assumed buffer released against the remaining gap |
| demand_response_mcm_per_day | Modelled reduction in demand against the remaining gap |
| uncovered_lng_gap_mcm_per_day | Residual daily LNG supply gap |
| buffer_remaining_mcm | Remaining assumed buffer volume |
| cumulative_uncovered_lng_gap_mcm | Cumulative residual gap over the simulation horizon |

The LNG model uses natural-gas volume units and must not be merged with crude-oil million-barrel units.
