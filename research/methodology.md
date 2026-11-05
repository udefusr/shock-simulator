# Research Methodology

## 1. Research objective

Investigate how the 2026 Strait of Hormuz disruption affected global oil supply, production, exports, inventories, and importing economies.

The project combines national oil statistics with independent maritime-flow and production-disruption estimates.

The research is descriptive and exploratory. It does not yet establish causal relationships.

## 2. Research period

- Historical reference year: 2025
- Disruption year: 2026
- JODI coverage: January 2025 to August 2026
- Primary event window: March to July 2026
- EIA maritime-flow coverage: Q1 2025 to Q2 2026

The event began on February 28, 2026. February is therefore treated as an approximate pre-disruption production reference, following the EIA's methodology.

## 3. Country selection

The initial comparison panel contains:

- Saudi Arabia
- Kuwait
- China
- India
- Japan
- South Korea
- Germany

Selection reflects data availability and different roles in the oil supply system.

Countries with incomplete observations are retained where useful, but their missing values are not estimated or interpolated.

## 4. JODI data selection

Primary product: CRUDEOIL.

Selected flows:

| Flow | Meaning | Unit |
| --- | --- | --- |
| INDPROD | Production | KBD |
| TOTIMPSB | Imports | KBD |
| TOTEXPSB | Exports | KBD |
| REFINOBS | Refinery intake | KBD |
| DIRECUSE | Direct use | KBD |
| CLOSTLV | Closing stocks | KBBL |
| STOCKCH | Stock change | KBBL |

CONVBBL is excluded because it is a conversion factor, not a physical volume or flow.

TOTCRUDE is kept separate from CRUDEOIL to avoid double-counting overlapping product aggregates.

## 5. Data processing

Original JODI files are preserved in data/raw/jodi/.

The data loader:

- Preserves original observation text.
- Converts numeric observations separately.
- Classifies missing-value markers.
- Retains assessment codes.
- Records the original source filename.
- Standardizes observation dates.

No missing observations are replaced with zero.

## 6. Averaging method

Monthly daily flow rates are averaged using calendar-day weights.

For a period containing monthly rates:

Weighted average = Sum(monthly rate × days in month) / Sum(days in month)

A complete-period comparison requires all expected monthly observations.

Inventory levels and inventory changes are treated separately from daily flow rates.

## 7. Cross-source comparison

JODI production observations are compared against EIA estimates of production shut-ins.

EIA-implied production is calculated as:

February production baseline − average estimated production shut-ins

This is a derived benchmark, not an independently observed production value.

Differences are retained and investigated rather than automatically treated as errors.

## 8. Simulation and response-policy assumptions

The deterministic simulation uses normalized supply, demand, and reserve units. These units are not presented as actual million barrels or barrels per day.

In the empirical scenario experiments, the demand-reduction policy begins on the first day of the disruption and remains active only for the duration of that disruption. Baseline demand is restored once the disruption window ends and the simulation enters the recovery period.

Reserve deployment follows a different timing rule. When reserve use is enabled, releases may continue during the recovery period whenever a supply deficit remains, subject to the daily release limit and the quantity of reserves still available. Releases stop when there is no deficit to cover or when the reserve stock is exhausted.

The demand-reduction percentage, reserve capacity, daily release limit, and supply recovery rate are model assumptions used for scenario analysis. They are not treated as measured historical policy responses.

## 9. Data quality

The project preserves:

- Missing observations.
- JODI assessment codes.
- Source publication dates.
- Measurement units.
- Observation periods.
- Estimated versus observed status.

AIS-based maritime estimates are subject to uncertainty, especially during the 2026 conflict.

## 10. Limitations

- National production changes cannot be attributed exclusively to Hormuz.
- JODI national trade data does not identify the maritime route of each shipment.
- The seven-country panel is not a complete global oil balance.
- EIA shut-in estimates and JODI production observations use different methodologies.
- The current research does not establish causal effects.


## 11. Evidence-aware reserve calibration

The separate reserve-calibration experiment translates compatible inventory and daily-release observations into normalized model units. It requires an analyst-supplied physical daily-flow denominator with a matching unit and a written definition. The project calculates inventory cover, normalized reserve inventory, and normalized daily release capability from that denominator; it does not infer missing rates or convert incompatible physical units.

The stated reserve-release lead time is represented explicitly. Under the current convention, simulation day 1 is the decision day and a lead time of N complete days enables delivery from day N+1. For the DOE 13-day statement, first modeled delivery is therefore day 14.

This parameter translation currently applies to the U.S. SPR profiles only. Japan's official announced volumes and equivalent days are retained as policy-event observations, with their division used only to derive an implied daily-supply denominator. That result is not a release rate. South Korea and Germany remain descriptive because the current source records lack compatible release-rate and lead-time inputs.

The new Reserve calibration dashboard tab is separate from the existing 18 normalized scenario experiments. The original results remain unchanged. See research/reserve_calibration_method.md for equations and limitations.


## 12. Deterministic uncertainty envelope

The uncertainty module evaluates a full-factorial grid of 729 combinations across six analyst-defined low/reference/high dimensions: shock magnitude, shock duration, initial reserve inventory, daily release capability, recovery rate, and additional mobilisation delay.

The engine uses reserve-enabled strategies only. The neutral combination reproduces the original empirical-scenario inputs. It reports the minimum, median of enumerated design points, maximum, and neutral reference result for each outcome metric. These are deterministic grid summaries, not probability-weighted values or statistical confidence intervals.

A main-effect screening statistic is also calculated for each input: mean total unmet demand at the high level minus mean total unmet demand at the low level, averaged over all settings of the other five inputs. The absolute difference ranks average high-low effects. This is a screening measure and does not isolate interactions or establish causal effects.

The default levels are analyst-defined and have not been statistically estimated from empirical distributions. No probabilities are assigned. The no-disruption baseline is excluded because reserve parameters would be inactive and create redundant outcomes. See research/uncertainty_analysis.md for the complete design and limitations.


## 11. Importer-country resilience scenario

The importer module uses 2025 estimates of crude-oil and condensate seaborne flows through the Strait of Hormuz for China, India, South Korea, and Japan. These destination-flow observations are not total national imports, national dependency percentages, or product/LNG flows. The country values are rounded to 0.1 million barrels per day and sourced from the Vortexa-based destination graphic listed in the source register.

For a selected country, the model calculates:

`gross daily loss = baseline Hormuz destination flow × disruption fraction`

`starting buffer = gross daily loss × assumed buffer-cover days`

For each disrupted day, alternative sourcing becomes available only from the user-selected start day and is capped at the gross daily loss. The buffer releases against the residual daily gap, bounded by remaining buffer stock. The remaining daily gap is recorded as uncovered imports. Daily rates in million barrels/day are summed over calendar days to obtain million barrels.

The alternative supply rate, buffer-cover duration, disruption fraction and delay are analyst-defined scenario assumptions. They are not inferred from JODI national imports, national inventory statistics, spare pipeline capacity, or observed replacement cargoes. The buffer is a deliberately simplified volume equal to a chosen number of days of the disrupted flow; it must not be labelled official national stock cover.

The model does not allocate the shared Saudi/UAE pipeline bypass capacity to importers. It does not identify cargo origins, model bilateral contracts, oil products, LNG, refinery compatibility, prices, or competition among importers for the same replacement barrels. It also does not infer a national import-dependency percentage because a consistent same-year total-import denominator is not included in the route-flow dataset.

The present comparison includes four destination markets with published flow labels. Bangladesh is not represented in this crude-oil panel. The IEA separately reports substantial Bangladesh exposure to LNG transiting Hormuz; that is a different commodity and should be added through a separate LNG module with consistent gas-volume units rather than mixed into crude-oil barrels/day.


## 12. LNG importer-country resilience

The LNG extension is separate from the crude-oil importer model. Its baseline dataset records 2025 annual destination volumes of LNG transiting Hormuz, in billion cubic metres (bcm), reproduced from the European Union Agency for the Cooperation of Energy Regulators (ACER) 2026 gas-market report. The reported destination estimates are Bangladesh 6.2 bcm, Pakistan 9.6 bcm, India 20.0 bcm, China 28.3 bcm, South Korea 9.9 bcm, and Japan 5.6 bcm. These are not total national LNG imports and cannot by themselves be used to calculate each country's import-dependency percentage.

The annual destination flow is converted to a calendar-day average:

`baseline mcm/day = annual destination flow bcm × 1,000 / days in year`

The user selects a disruption fraction and duration. For each disruption day the simulation applies this response order:

1. Alternative LNG deliveries become available from the user-selected day, bounded by the gross daily lost flow.
2. A finite, assumed buffer volume covers the remaining gap. Its starting volume is gross disrupted flow multiplied by the assumed buffer-cover days.
3. Demand response reduces a user-defined share of the gross lost flow, capped by the remaining gap.
4. Any remaining daily gap is recorded as uncovered LNG volume.

Daily rates in million cubic metres/day summed over daily time steps yield million cubic metres (mcm). The model does not convert LNG volumes into crude-oil barrels or normalized oil model units.

Alternative LNG deliveries, assumed buffer days, disruption fraction/duration, and demand-response fraction are scenario parameters, not source observations. The buffer is not a claim about actual national storage or linepack. Demand response is not a claim that gas demand can be curtailed without industrial, power-sector or economic consequences.

The IEA states that Bangladesh, India and Pakistan imported almost two-thirds of their total LNG supplies via Hormuz in 2025. It also reports that gas-fired generation supplied 50% of Bangladesh's electricity mix in 2024. These IEA indicators provide national exposure context; they are not used as inputs to the destination-flow simulation because the model has no matched national LNG-import denominator or gas-sector demand series.

Important limitations: no country-specific total LNG demand series, non-Hormuz import origin mix, regasification-terminal capacity, cargo scheduling, spot-market competition, pipeline constraints, storage/linepack inventory, domestic gas production, power dispatch, industrial allocation, prices, or contract flexibility are modelled. The module is a transparent first-stage volume-gap stress test, not a national gas-system forecast.
