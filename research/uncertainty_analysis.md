# Deterministic Uncertainty Analysis

**Version:** Initial bounded full-factorial scenario envelope  
**Research cutoff:** November 6, 2026  
**Status:** Deterministic sensitivity analysis; not probabilistic forecasting.

## 1. Objective

The purpose of this analysis is to examine how uncertainty in key model assumptions changes simulated shortage outcomes. It supplements the six fixed scenario definitions and three response strategies without replacing their existing results.

The analysis uses a full-factorial grid of bounded low/reference/high design values. No probability distribution is assigned to any input. The resulting minimum, median, and maximum are summaries of the enumerated design points, not confidence intervals or probability-weighted forecasts.

## 2. Factors and levels

The default design varies six inputs:

| Factor | Level 1 | Level 2 | Level 3 |
| --- | ---: | ---: | ---: |
| Supply-shock multiplier | 0.8× | 1.0× | 1.2× |
| Shock-duration multiplier | 0.8× | 1.0× | 1.2× |
| Initial reserve inventory fraction | 50% | 75% | 100% |
| Daily release-cap fraction | 50% | 75% | 100% |
| Recovery-rate multiplier | 0.5× | 1.0× | 1.5× |
| Additional mobilisation delay | 0 days | 7 days | 14 days |

All levels are analyst-defined stress ranges. The neutral reference combination uses 1.0× for multipliers, 100% for reserve inventory and release-cap fractions, and zero additional mobilisation delay. Therefore, the 50% / 75% / 100% reserve and release-cap levels are all reductions up to the existing baseline, not a symmetric low/base/high range. Duration values are rounded to the nearest whole simulation day.

The full factorial design contains 3^6 = 729 design points for each selected disruption scenario and reserve-enabled strategy.

## 3. Scenario and strategy selection

The analysis accepts scenarios with a positive supply shock and positive disruption duration. The no-disruption baseline is excluded because reserve inventory, release capability, and mobilisation delay cannot affect outcomes when there is no shortage.

The supported strategies are:
- Reserve release
- Combined response

A no-intervention strategy is excluded because the reserve-related factors would be inactive and would create redundant combinations.

## 4. Outcome envelope

For each metric, the dashboard reports:
- Minimum across all design points.
- Median of the enumerated design points.
- Maximum across all design points.
- The neutral reference-case result.

The median gives equal weight to every design point, not to its empirical plausibility. It is a design-grid statistic, not an expected value.

Primary outputs include cumulative unmet demand, shortage days, critical days, severe days, maximum daily shortage percentage, remaining reserve inventory, and total reserve released.

## 5. Main-effect ranking

The analysis also calculates a simple average high-minus-low main effect for each input factor.

For a factor X:

E_X = mean(Y at X high) - mean(Y at X low)

where Y is cumulative unmet demand and each mean is calculated across all combinations of the other five factors.

The absolute value of this difference is used to rank factors by their average main effect. A positive signed value means the high level is associated with more unmet demand in the enumerated design; a negative value means it is associated with less.

This is a screening statistic. It averages over other factors, does not estimate causal effects, and does not fully explain interactions or nonlinear behaviour. The full design-point CSV should be retained for deeper analysis.

## 6. Model constraints

The implementation:
- Validates exactly three strictly increasing levels for each factor.
- Requires neutral reference levels to be present.
- Prevents supply loss above 100%.
- Prevents recovery rates above 100%.
- Applies reserve inventory and release-cap fractions to the normalized base inputs.
- Delays reserve release according to the base mobilisation day plus the additional delay.
- Applies the selected scenario's demand-response duration only for the disruption window, as before.
- Enforces a maximum grid size to prevent accidental combinatorial explosion.

## 7. Interpretation limitations

The ranges are analyst-defined, not statistical uncertainty intervals. The levels are not probability distributions. The design does not currently account for:
- Correlated input uncertainty.
- Empirically estimated distributions for shock size or duration.
- Statistical uncertainty in EIA estimates.
- Country-specific demand or trade network uncertainty.
- Changing release capability as reserves are depleted.
- Structural uncertainty about market substitution, rerouting, refining and logistics.

The dashboard's scatter and histogram are visual summaries of deterministic design points, not sampled forecasts.

## 8. Reproducibility

Run the complete test suite and launch the dashboard:

    python -m pytest -v
    streamlit run app.py

The implementation is in src/uncertainty.py. Tests are in tests/test_uncertainty.py. The dashboard exports:
- All 729 design points.
- The outcome envelope.
- The main-effect ranking table.

## 9. Next research steps

The next level of uncertainty analysis should estimate defensible parameter ranges from data or expert-elicitation protocols, examine input correlations, and separately quantify uncertainty in the source estimates. A probabilistic model should only be introduced when distributions and their evidential basis can be defended.
