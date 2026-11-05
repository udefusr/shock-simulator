
# Empirical Scenario Design

## 1. Objective

This document defines the empirical scenarios used to investigate how disruptions to Gulf oil production and critical maritime energy routes affect oil supply resilience.

The scenarios distinguish historical estimates, counterfactual conditions, and hypothetical stress tests.

## 2. Empirical calibration

The primary production-disruption benchmark is based on the EIA October 2026 Short-Term Energy Outlook.

The covered Gulf producers have an estimated February 2026 baseline production of 25.2 million barrels per day.

The EIA estimated average production shut-ins of 8.512 million barrels per day during March–July 2026.

The resulting disruption rate is:

Disruption rate = 8.512 / 25.2 = 0.3378

The model therefore uses a 33.8% supply shock as its principal observed-period calibration benchmark.

This is a regional production benchmark, not an estimate of the percentage of global oil supply lost.

## 3. Scenario definitions

| Scenario | Supply shock | Duration | Classification |
| --- | ---: | ---: | --- |
| Baseline | 0% | 153 days | Counterfactual |
| Observed-period benchmark | 33.8% | 153 days | EIA-based estimate |
| August conditions | 22.9% | 31 days | EIA-based estimate |
| September conditions | 18.9% | 30 days | EIA-based estimate |
| Severe stress test | 50% | 153 days | Hypothetical |
| Extreme stress test | 75% | 153 days | Hypothetical |

The March–July benchmark represents the average estimated production disruption over that five-month period.

The August and September scenarios represent separate monthly disruption estimates. They are not a reconstruction of daily production.

The 50% and 75% scenarios are hypothetical stress tests. They are not historical observations or EIA forecasts.

## 4. Maritime route indicator

EIA estimated Hormuz oil transit flows at:

- 21.6 million barrels per day in Q4 2025.
- 4.9 million barrels per day in Q2 2026.

This represents an estimated reduction of approximately 77.3%.

This indicator measures reduced oil flows through a maritime chokepoint. It must not be treated as an equivalent reduction in global oil supply.

Alternative routes, rerouting, inventories, production changes, and demand responses affect the relationship between transit flows and actual market availability.

## 5. Model parameters and evidence status

| Parameter | Evidence status |
| --- | --- |
| Production shock magnitude | Empirically benchmarked using EIA estimates |
| Shock duration | Based on the March–July observation period |
| Reserve capacity | Model assumption until independently sourced |
| Daily reserve release limit | Model assumption until independently sourced |
| Demand reduction | Policy experiment, not an observed estimate |
| Recovery rate | Model assumption requiring sensitivity analysis |
| Baseline demand | Model assumption requiring further data |

The normalized simulation units should not be presented as actual million barrels per day unless the model is explicitly calibrated to matching physical supply and demand series.

## 6. Validation strategy

JODI monthly crude-oil production data will be used as an independent comparison source where numeric observations are available.

Saudi Arabia and Kuwait are the initial country-level comparison cases.

The comparison will examine:

- February 2026 production as a pre-disruption reference.
- March–July 2026 average production.
- The corresponding March–July 2025 average.
- Differences between JODI production changes and EIA estimated production shut-ins.

JODI production observations and EIA estimated production shut-ins are different measures. Differences between them should be treated as reconciliation diagnostics, not automatically as errors.

## 7. Interpretation limitations

The analysis is descriptive and scenario-based.

National JODI import and export observations do not identify the maritime route used by each shipment.

The collected data therefore cannot establish that a particular country's observed import change was caused exclusively by the Strait of Hormuz disruption.

EIA estimates are subject to methodological uncertainty and revision.

Hypothetical stress tests must always be identified separately from historical observations and official forecasts.

## 8. Research principle

The simulator is intended to investigate possible system responses under clearly defined assumptions.

It is not intended to reproduce the entire 2026 oil crisis or to claim precise causal attribution from incomplete observational data.


## 9. Bounded uncertainty analysis

The empirical scenario dashboard is supplemented by a separate deterministic full-factorial uncertainty envelope. Six assumptions are varied across low/reference/high levels: shock magnitude, shock duration, reserve inventory fraction, daily release-cap fraction, recovery-rate multiplier, and additional mobilisation delay.

This produces 729 design points for each selected disruption scenario and reserve-enabled response strategy. The no-disruption baseline and no-intervention strategy are excluded because reserve-related parameters would not affect those runs.

The analysis reports outcome ranges and ranks average high-versus-low main effects. The ranges are analyst-defined stress bounds, not estimated probability distributions. Median values describe the enumerated design points, not a statistical expectation.

See research/uncertainty_analysis.md for the levels, calculation method, constraints and interpretation boundary.
