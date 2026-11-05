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
