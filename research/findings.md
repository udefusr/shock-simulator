
# Preliminary Research Findings

**Research cutoff:** November 5, 2026.

These findings are descriptive and provisional. They do not establish that the Hormuz disruption caused every observed national production or trade change.

## 1. Dataset coverage

The initial JODI panel contains:

- Seven economies.
- 980 selected observations.
- 857 numeric observations.
- 123 missing numeric observations.

The panel covers January 2025–August 2026.

## 2. Saudi Arabia

JODI weighted-average production:

- March–July 2025: 9,217.93 KBD.
- March–July 2026: 7,024.18 KBD.
- February 2026 observation: 10,882 KBD.

The JODI February-to-March–July decline is 3,857.82 KBD.

The EIA estimated average March–July production shut-ins at 2,750 KBD.

EIA-implied production is 7,750 KBD.

JODI observed production is 725.82 KBD below that derived benchmark.

## 3. Kuwait

JODI weighted-average production:

- March–July 2025: 2,422.27 KBD.
- March–July 2026: 1,193.33 KBD.
- February 2026 observation: 2,580 KBD.

The JODI February-to-March–July decline is 1,386.67 KBD.

The EIA estimated average March–July production shut-ins at 1,466 KBD.

EIA-implied production is 1,094 KBD.

JODI observed production is 99.33 KBD above that derived benchmark.

## 4. Importing economies

March–August year-on-year comparisons show:

- China crude imports: approximately −23.22%.
- Japan crude imports: approximately −15.87%.
- South Korea crude imports: approximately −8.08%.
- Germany crude imports: approximately −2.59%.

These figures are descriptive comparisons, not causal estimates.

India's 2026 observations are incomplete for the event window.

## 5. Maritime flows

EIA estimates for total oil flows through the Strait of Hormuz:

| Quarter | Million barrels per day |
| --- | ---: |
| Q1 2025 | 20.9 |
| Q2 2025 | 21.0 |
| Q3 2025 | 21.3 |
| Q4 2025 | 21.6 |
| Q1 2026 | 14.9 |
| Q2 2026 | 4.9 |

These figures represent total oil flows, including crude oil and petroleum products, not crude oil alone.

They are estimates based partly on tanker tracking and may be revised.

## 6. Interpretation

The JODI observations show substantial changes in producer output, exports, and importer activity during 2026.

The EIA estimates provide independent context for the maritime disruption and regional production shut-ins.

However, differences between JODI and EIA are not automatically errors. The sources measure different concepts using different methodologies.

## 7. Remaining research questions

- How much of the national production decline is attributable to Hormuz-related constraints?
- How effectively did alternative export routes compensate?
- How did commercial and strategic inventories respond?
- How did importing economies adjust refinery intake and imports?
- How did the September disruption to Saudi Arabia's East-West pipeline affect recovery?
- How should uncertainty and missing observations be represented in the simulation?

## 2026 Empirical Scenario Experiments — Revised Demand-Response Model

### Experimental design

Six disruption scenarios were tested against three response strategies:

1. No intervention.
2. Reserve release.
3. Combined response: reserve release and a 10% demand reduction.

The simulation horizon is 213 days. Demand reduction is now restricted to the disruption period. Demand returns to its baseline level during recovery.

Reserve deployment remains available during recovery, subject to the daily release limit and remaining reserve stock.

All supply, demand and reserve quantities are normalized model units.

### Results

| Scenario | Strategy | Total unmet demand | Shortage days | Critical days | Severe days | Remaining reserves |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| March–July | No intervention | 4571.37 | 171 | 164 | 158 | 200.00 |
| March–July | Reserve release | 4371.37 | 171 | 164 | 158 | 0.00 |
| March–July | Combined response | 2917.87 | 171 | 164 | 158 | 0.00 |
| August | No intervention | 642.22 | 45 | 39 | 32 | 200.00 |
| August | Reserve release | 442.22 | 43 | 35 | 0 | 0.00 |
| August | Combined response | 147.72 | 43 | 4 | 0 | 0.00 |
| September | No intervention | 480.10 | 42 | 36 | 0 | 200.00 |
| September | Reserve release | 287.68 | 36 | 32 | 0 | 7.58 |
| September | Combined response | 19.82 | 6 | 2 | 0 | 24.72 |
| Severe | No intervention | 7180.76 | 174 | 168 | 162 | 200.00 |
| Severe | Reserve release | 6980.76 | 174 | 168 | 162 | 0.00 |
| Severe | Combined response | 5527.26 | 174 | 168 | 162 | 0.00 |
| Extreme | No intervention | 11211.54 | 178 | 172 | 165 | 200.00 |
| Extreme | Reserve release | 11011.54 | 178 | 172 | 165 | 0.00 |
| Extreme | Combined response | 9558.04 | 178 | 172 | 165 | 0.00 |

### Strategy effectiveness

Percentage reduction in cumulative unmet demand relative to no intervention:

| Scenario | Reserve release | Combined response |
| --- | ---: | ---: |
| March–July | 4.4% | 36.2% |
| August | 31.1% | 77.0% |
| September | 40.1% | 95.9% |
| Severe stress | 2.8% | 23.0% |
| Extreme stress | 1.8% | 14.7% |

### Findings

1. Reserve release provides limited protection under prolonged disruptions because the finite reserve stock becomes depleted.
2. Combined response produces substantial reductions in unmet demand under the shorter August and September scenarios.
3. In the longer benchmark and hypothetical stress tests, intervention reduces cumulative unmet demand but does not eliminate shortage days.
4. Severe and extreme shocks overwhelm the modeled reserve capacity and retain substantial shortages even with combined intervention.
5. The effectiveness of demand reduction depends on intervention duration. The revised model therefore restricts the 10% demand reduction to the disruption period rather than maintaining it throughout recovery.

### Model interpretation

The revised demand-response experiment replaces the original always-active demand-reduction assumption.

The original experiment kept demand reduction active for all 213 days. The revised experiment restores baseline demand after the disruption ends.

This increases combined-response unmet demand in every non-baseline scenario compared with the original experiment.

The results demonstrate sensitivity to intervention timing, not real-world policy effectiveness.

### Limitations

- Normalized units are not actual million barrels or barrels per day.
- Reserve capacity and release limits are assumptions.
- The 10% demand reduction is an experimental policy assumption.
- Recovery follows a simplified deterministic function.
- The model does not explicitly represent oil prices, rerouting, country-level trade networks or substitution between fuels.
- These experiments do not establish causal effects of real-world policy interventions.
