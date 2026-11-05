# Reserve Calibration Method

**Version:** Initial evidence-aware model adapter  
**Research cutoff:** November 6, 2026  
**Status:** Exploratory parameter translation; not an operational reserve model.

## 1. Purpose

This method translates a reserve profile into the normalized units used by Shock Simulator only when the source record contains a compatible inventory quantity, nominal daily release rate, release lead time, and native units. It deliberately requires the analyst to provide the physical daily-flow denominator.

The adapter currently supports the U.S. Department of Energy Strategic Petroleum Reserve (SPR) records because those records include inventory, a nominal drawdown rate, and a lead-time statement. It does not manufacture release rates for Japan, South Korea, or Germany.

## 2. Required inputs

For a selected country and dated reserve profile:

- Reported inventory quantity Q, in a native volume unit.
- Nominal daily release capability R, in the matching volume-per-day unit.
- Release lead time L, in days.
- Analyst-supplied physical daily-flow denominator Dp, in the matching volume-per-day unit.
- Desired model daily demand Dm, in normalized simulation units per day.

The analyst must also record what Dp represents (for example, crude-oil net imports or domestic consumption). Dp must represent the same physical flow that model daily demand represents; it cannot be an unrelated denominator. The denominator must match the reserve scope and research question, and is never silently inferred.

## 3. Conversion equations

The implied stock-cover duration is:

\[
T_{cover} = Q / D_p
\]

The model-scale starting inventory is:

\[
Q_m = T_{cover} \times D_m
\]

The nominal release capability as a share of the physical daily-flow denominator is:

\[
r = R / D_p
\]

The model-scale daily release limit is:

\[
R_m = r \times D_m
\]

The calculations are valid only when volume and flow units match. For example, million barrels must be paired with million barrels per day. No conversion between barrels, kilolitres, and tonnes is performed by this adapter.

## 4. Mobilization timing

The model day-1 convention treats day 1 as the day a reserve-release decision is made. If a source states a lead time of L complete days, the first modeled market delivery is allowed on day L+1.

For the DOE's 13-day lead-time statement, the adapter therefore sets reserve_release_start_day = 14. This is a conservative explicit timing convention for the simulation; it is not a claim about a specific historical SPR release date.

The simulation records reserve_release_active separately from the quantity released. A deployment window can be active while actual release is zero because no deficit exists.

## 5. Current U.S. SPR calibration boundary

The data file contains two dated DOE inventory records: 411 million barrels at end-2025 and 282.2 million barrels on October 16, 2026. Both records include a 4.4-million-barrel/day nominal capability and a 13-day lead-time statement.

The end-2025 DOE stock-cover statement of approximately 125 days uses U.S. crude-oil net imports. The 2026 inventory record does not include a corresponding days-cover value in the structured data. The adapter recalculates stock cover from the analyst's selected denominator and labels it as derived.

DOE's August 2016 Long-Term Strategic Review publishes a stepped design drawdown curve: 4.4 million barrels/day on days 1–90, 3.8 on days 91–120, 3.4 on days 121–150, and 1.9 on days 151–180 ([DOE report, Figure 15](https://www.energy.gov/ceser/articles/long-term-strategic-review-ltsr-us-strategic-petroleum-reserve-spr-report-congress)). The simulator offers this as an optional historical design-reference schedule. It is indexed from the first modeled delivery day, not from the reserve decision day, so the 13-day lead time does not consume the first 13 drawdown days.

The DOE figure ends at day 180. For a simulation continuing beyond day 180, the implementation holds the final 1.9/4.4 multiplier constant. This is an explicit extrapolation for continuity, not a DOE-published rate beyond day 180. The alternative constant-cap setting is retained only as a comparison and does not reproduce DOE's post-90-day decline.

This historical curve must not be read as current effective SPR capability. GAO's May 2026 report states that DOE estimated aggregate effective drawdown capability at 2.700 million barrels/day against a 4.415 million-barrel/day design rate as of December 2025 (61%), citing site outages, infrastructure issues, and inventory constraints ([GAO-26-106918](https://www.gao.gov/products/gao-26-106918)). The 2016 curve and December 2025 effective rate are different measures and dates; the model does not combine them into a synthetic current curve.

The model still omits site-level constraints, crude-grade matching, pipeline/terminal bottlenecks, and the difference between SPR releases and barrels available to a particular importing country.

## 6. Japan announcement cross-check

Japan's two official national stock-release announcements give approximate volume and equivalent-days statements:

- 8.5 million kilolitres / 30 equivalent days = approximately 0.283 million kilolitres per day.
- 5.8 million kilolitres / 20 equivalent days = 0.290 million kilolitres per day.

These derived values are implied daily-supply denominators embedded in the announcements. They are not release rates, release schedules, or observed withdrawal rates. Their similarity is a useful arithmetic consistency check, subject to rounding in the source figures.

The separate 15-day reduction in the private stockholding obligation remains a policy change, not a physical reserve withdrawal. It is excluded from the denominator calculation.

## 7. Countries not calibrated by this adapter

- **Japan:** official announced release quantities and equivalent supply-days are available, but the current profile does not provide a comparable nominal daily release rate and lead time.
- **South Korea:** the profile contains a KNOC inventory and capacity figure, but no comparable daily release rate and lead time.
- **Germany:** the source provides an approximate stock volume and procedure, but no dated inventory observation or comparable daily release rate.

Their observations remain available for descriptive analysis. They are not assigned fabricated model rates.

## 8. Dashboard experiment

The dashboard's Reserve calibration tab:
1. Lets the analyst choose a dated U.S. SPR inventory record.
2. Requires a physical daily-flow denominator and a written definition for that denominator.
3. Converts reserve inventory and nominal release capability into the requested model scale.
4. Applies the lead-time delay.
5. Runs one selected disruption scenario and response strategy using those translated reserve parameters.
6. Exports the derived calibration record and daily model output.

This is a country-specific reserve sensitivity experiment embedded in a wider normalized producer-disruption model. It combines a U.S. reserve profile with regional Gulf producer disruption benchmarks or hypothetical stress tests, so it is an abstract cross-system sensitivity experiment rather than a matched country-level balance. It is not a full model of the U.S. petroleum market, global oil trade, or Hormuz-importing economies.

## 9. Interpretation and limitations

- Model-scale outputs depend directly on the analyst-supplied denominator.
- A nominal release capability is not a guarantee of actual market delivery.
- The model's single reserve pool abstracts from crude grades, refined-product compatibility, geography, transport, and commercial availability.
- The optional DOE taper is a 2016 historical design-reference curve, not current effective capability. Its final 1.9 rate is held beyond the source's 180-day horizon as an explicit extrapolation. GAO's December 2025 effective-rate estimate is reported separately and is not combined with the historical curve.
- The simulation does not assume that U.S. SPR barrels can be delivered directly to any specific importer.
- The Japan event cross-check uses rounded announced quantities and equivalent days.
- The existing 18 empirical experiments retain their original normalized illustrative reserve parameters. This calibration tab does not retroactively change their published results.

## 10. Reproducibility

Run the tests with pytest, validate reserve data with the reserve validation script, and launch the application with Streamlit.

The new adapter is implemented in src/reserve_calibration.py; automated coverage is in tests/test_reserve_calibration.py and the delayed mobilisation tests in tests/test_simulation.py.
