import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.scenarios import summarize_results
from src.sensitivity import analyze_demand_reduction
from src.simulation import run_simulation
from src.empirical_scenarios import (
    RESPONSE_STRATEGIES,
    build_simulation_inputs,
    list_empirical_scenarios,
    run_empirical_scenarios,
)
from src.reserve_calibration import (
    calibrate_reserve_profile,
    list_calibratable_profiles,
    summarize_announced_release_denominators,
)
from src.uncertainty import run_scenario_envelope

# --------------------------------------------------
# Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Shock Simulator",
    page_icon="⚡",
    layout="wide",
)

st.title("Shock Simulator")
st.caption("Supply disruption, reserve deployment and recovery modelling")


# --------------------------------------------------
# Chart builders
# --------------------------------------------------


def create_supply_chart(results):
    days = [row["day"] for row in results]
    baseline = [row["supply"] for row in results]
    reserves = [row["reserve_release"] for row in results]
    demand = [row["demand"] for row in results]

    total_supply = [supply + reserve for supply, reserve in zip(baseline, reserves)]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=days,
            y=baseline,
            mode="lines",
            name="Baseline supply",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=days,
            y=reserves,
            mode="lines",
            name="Reserve contribution",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=days,
            y=total_supply,
            mode="lines",
            name="Total available supply",
            line={"width": 3},
        )
    )

    fig.add_trace(
        go.Scatter(
            x=days,
            y=demand,
            mode="lines",
            name="Demand",
            line={"dash": "dash"},
        )
    )

    fig.update_layout(
        xaxis_title="Simulation day",
        yaxis_title="Resource units",
        hovermode="x unified",
        template="plotly_dark",
    )

    return fig


def create_shortage_chart(results):
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=[row["day"] for row in results],
            y=[row["unmet_demand"] for row in results],
            name="Unmet demand",
        )
    )

    fig.update_layout(
        xaxis_title="Simulation day",
        yaxis_title="Unmet resource units",
        template="plotly_dark",
    )

    return fig


def create_severity_chart(results):
    severity_values = {
        "Normal": 0,
        "Warning": 1,
        "Critical": 2,
        "Severe": 3,
    }

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=[row["day"] for row in results],
            y=[severity_values[row["severity"]] for row in results],
            mode="lines+markers",
            name="Severity",
            line={"shape": "hv", "width": 3},
        )
    )

    fig.update_layout(
        xaxis_title="Simulation day",
        yaxis={
            "title": "Severity",
            "tickmode": "array",
            "tickvals": [0, 1, 2, 3],
            "ticktext": ["Normal", "Warning", "Critical", "Severe"],
            "range": [-0.2, 3.2],
        },
        template="plotly_dark",
    )

    return fig


# --------------------------------------------------
# Scenario analysis
# --------------------------------------------------


def run_strategy_comparison(inputs):
    strategies = {
        "No intervention": {
            "use_reserves": False,
            "demand_reduction_pct": 0.0,
        },
        "Reserve strategy": {
            "use_reserves": True,
            "demand_reduction_pct": 0.0,
        },
        "Combined strategy": {
            "use_reserves": True,
            "demand_reduction_pct": 0.10,
        },
    }

    comparison = []

    for name, settings in strategies.items():
        simulation = run_simulation(
            **inputs,
            **settings,
        )

        summary = summarize_results(simulation)

        comparison.append(
            {
                "Strategy": name,
                "Total unmet demand": round(summary["total_unmet_demand"], 2),
                "Shortage days": summary["shortage_days"],
                "Critical days": summary["critical_days"],
                "Severe days": summary["severe_days"],
                "Remaining reserves": round(summary["remaining_reserves"], 2),
            }
        )

    return comparison


# --------------------------------------------------
# Sidebar: simulation inputs
# --------------------------------------------------

st.sidebar.header("Simulation Parameters")

baseline_supply = st.sidebar.number_input(
    "Baseline supply",
    min_value=1.0,
    value=100.0,
)

daily_demand = st.sidebar.number_input(
    "Daily demand",
    min_value=0.0,
    value=95.0,
)

shock_loss_pct = (
    st.sidebar.slider(
        "Supply loss (%)",
        min_value=0,
        max_value=100,
        value=25,
    )
    / 100
)

shock_start_day = st.sidebar.number_input(
    "Shock start day",
    min_value=1,
    value=1,
)

shock_duration = st.sidebar.number_input(
    "Shock duration (days)",
    min_value=0,
    value=20,
)

initial_reserves = st.sidebar.number_input(
    "Initial reserves",
    min_value=0.0,
    value=200.0,
)

reserve_release_limit = st.sidebar.number_input(
    "Daily reserve release limit",
    min_value=0.0,
    value=5.0,
)

recovery_rate = (
    st.sidebar.slider(
        "Recovery rate (%)",
        min_value=1,
        max_value=100,
        value=10,
    )
    / 100
)

days = st.sidebar.number_input(
    "Simulation duration (days)",
    min_value=1,
    value=60,
)


# --------------------------------------------------
# Execute primary simulation
# --------------------------------------------------

simulation_inputs = {
    "baseline_supply": baseline_supply,
    "daily_demand": daily_demand,
    "initial_reserves": initial_reserves,
    "shock_loss_pct": shock_loss_pct,
    "shock_start_day": shock_start_day,
    "shock_duration": shock_duration,
    "reserve_release_limit": reserve_release_limit,
    "recovery_rate": recovery_rate,
    "days": days,
}

results = run_simulation(**simulation_inputs)

total_unmet = sum(row["unmet_demand"] for row in results)
shortage_days = sum(row["unmet_demand"] > 0 for row in results)
final_reserves = results[-1]["reserves_remaining"]


# --------------------------------------------------
# Main dashboard tabs
# --------------------------------------------------

simulation_tab, comparison_tab, sensitivity_tab, empirical_tab, reserve_tab, uncertainty_tab = st.tabs(
    [
        "📊 Simulation",
        "⚖️ Scenario comparison",
        "📈 Sensitivity analysis",
        "🛢️ Empirical scenarios",
        "🧰 Reserve calibration",
        "🧪 Uncertainty analysis",
    ]
)


# ==================================================
# TAB 1: SIMULATION
# ==================================================

with simulation_tab:
    col1, col2, col3 = st.columns(3)

    col1.metric("Total unmet demand", f"{total_unmet:.2f}")
    col2.metric("Shortage days", shortage_days)
    col3.metric("Remaining reserves", f"{final_reserves:.2f}")

    st.divider()

    st.subheader("Supply vs. demand")

    st.plotly_chart(
        create_supply_chart(results),
        width="stretch",
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Daily unmet demand")

        st.plotly_chart(
            create_shortage_chart(results),
            width="stretch",
        )

    with col2:
        st.subheader("System severity")

        st.plotly_chart(
            create_severity_chart(results),
            width="stretch",
        )


# ==================================================
# TAB 2: SCENARIO COMPARISON
# ==================================================

with comparison_tab:
    st.header("Scenario comparison")

    st.caption("Compare response strategies under identical simulation conditions.")

    comparison_data = run_strategy_comparison(simulation_inputs)

    comparison_df = pd.DataFrame(comparison_data)

    st.dataframe(
        comparison_df,
        width="stretch",
        hide_index=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Total unmet demand")

        fig = go.Figure(
            go.Bar(
                x=comparison_df["Strategy"],
                y=comparison_df["Total unmet demand"],
                name="Total unmet demand",
            )
        )

        fig.update_layout(
            yaxis_title="Unmet resource units",
            template="plotly_dark",
        )

        st.plotly_chart(fig, width="stretch")

    with col2:
        st.subheader("Shortage days")

        fig = go.Figure(
            go.Bar(
                x=comparison_df["Strategy"],
                y=comparison_df["Shortage days"],
                name="Shortage days",
            )
        )

        fig.update_layout(
            yaxis_title="Number of days",
            template="plotly_dark",
        )

        st.plotly_chart(fig, width="stretch")

    st.download_button(
        label="Download comparison as CSV",
        data=comparison_df.to_csv(index=False).encode("utf-8"),
        file_name="shock_simulator_comparison.csv",
        mime="text/csv",
    )


# ==================================================
# TAB 3: SENSITIVITY ANALYSIS
# ==================================================

with sensitivity_tab:
    st.header("Demand-response sensitivity")

    st.caption(
        "Investigate how demand reduction affects system "
        "resilience under fixed disruption conditions."
    )

    demand_results = analyze_demand_reduction()

    demand_comparison = []

    for reduction, summary in demand_results.items():
        demand_comparison.append(
            {
                "Demand reduction": f"{reduction * 100:.0f}%",
                "Total unmet demand": round(summary["total_unmet_demand"], 2),
                "Shortage days": summary["shortage_days"],
                "Critical days": summary["critical_days"],
                "Severe days": summary["severe_days"],
                "Remaining reserves": round(summary["remaining_reserves"], 2),
            }
        )

    demand_df = pd.DataFrame(demand_comparison)

    st.dataframe(
        demand_df,
        width="stretch",
        hide_index=True,
    )

    st.subheader("Impact of demand reduction")

    fig = go.Figure(
        go.Scatter(
            x=demand_df["Demand reduction"],
            y=demand_df["Total unmet demand"],
            mode="lines+markers",
            name="Total unmet demand",
        )
    )

    fig.update_layout(
        xaxis_title="Demand reduction",
        yaxis_title="Total unmet resource units",
        template="plotly_dark",
    )

    st.plotly_chart(fig, width="stretch")

    st.download_button(
        label="Download sensitivity analysis as CSV",
        data=demand_df.to_csv(index=False).encode("utf-8"),
        file_name="demand_response_sensitivity.csv",
        mime="text/csv",
    )

# ==================================================
# TAB 4: EMPIRICAL OIL DISRUPTION SCENARIOS
# ==================================================

with empirical_tab:
    st.header("Empirical oil disruption scenarios")

    st.caption(
        "Compare EIA-informed disruption benchmarks and hypothetical "
        "stress tests under different response strategies."
    )

    st.info(
        "These experiments use normalized model units. The EIA-derived "
        "shock percentages represent estimated production disruptions "
        "among covered Gulf producers, not global oil supply losses. "
        "Reserve, demand and recovery parameters remain model assumptions."
    )

    # --------------------------------------------------
    # Run all 18 experiments
    # --------------------------------------------------

    scenario_definitions = {
        scenario["scenario_id"]: scenario for scenario in list_empirical_scenarios()
    }

    empirical_runs = {}
    empirical_rows = []

    for strategy in RESPONSE_STRATEGIES:
        strategy_results = run_empirical_scenarios(strategy=strategy)

        for scenario_id, result in strategy_results.items():
            empirical_runs[(scenario_id, strategy)] = result

            scenario = result["scenario"]
            summary = result["summary"]

            empirical_rows.append(
                {
                    "Scenario": scenario["name"],
                    "Classification": scenario["classification"],
                    "Response strategy": strategy,
                    "Supply shock (%)": round(scenario["shock_loss_pct"] * 100, 2),
                    "Shock duration (days)": (scenario["shock_duration_days"]),
                    "Total unmet demand (units)": round(
                        summary["total_unmet_demand"], 2
                    ),
                    "Shortage days": summary["shortage_days"],
                    "Critical days": summary["critical_days"],
                    "Severe days": summary["severe_days"],
                    "Remaining reserves (units)": round(
                        summary["remaining_reserves"], 2
                    ),
                }
            )

    empirical_df = pd.DataFrame(empirical_rows)

    # --------------------------------------------------
    # Full experiment results
    # --------------------------------------------------

    st.subheader("Experiment results")

    st.caption("Six disruption scenarios tested against three response strategies.")

    st.dataframe(
        empirical_df,
        width="stretch",
        hide_index=True,
    )

    # --------------------------------------------------
    # Metric comparison chart
    # --------------------------------------------------

    st.subheader("Compare response strategies")

    metric_options = [
        "Total unmet demand (units)",
        "Shortage days",
        "Critical days",
        "Severe days",
        "Remaining reserves (units)",
    ]

    selected_metric = st.selectbox(
        "Comparison metric",
        options=metric_options,
    )

    fig = go.Figure()

    for strategy in RESPONSE_STRATEGIES:
        strategy_df = empirical_df[empirical_df["Response strategy"] == strategy]

        fig.add_trace(
            go.Bar(
                x=strategy_df["Scenario"],
                y=strategy_df[selected_metric],
                name=strategy,
            )
        )

    fig.update_layout(
        barmode="group",
        xaxis_title="Disruption scenario",
        yaxis_title=selected_metric,
        template="plotly_dark",
        hovermode="x unified",
    )

    st.plotly_chart(
        fig,
        width="stretch",
    )

    # --------------------------------------------------
    # Inspect one experiment in detail
    # --------------------------------------------------

    st.divider()
    st.subheader("Inspect an individual experiment")

    scenario_ids = list(scenario_definitions)

    selected_scenario_id = st.selectbox(
        "Disruption scenario",
        options=scenario_ids,
        format_func=lambda value: scenario_definitions[value]["name"],
    )

    selected_strategy = st.selectbox(
        "Response strategy",
        options=list(RESPONSE_STRATEGIES),
    )

    selected_result = empirical_runs[(selected_scenario_id, selected_strategy)]

    selected_summary = selected_result["summary"]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total unmet demand",
        f"{selected_summary['total_unmet_demand']:.2f}",
    )

    col2.metric(
        "Shortage days",
        selected_summary["shortage_days"],
    )

    col3.metric(
        "Critical days",
        selected_summary["critical_days"],
    )

    col4.metric(
        "Remaining reserves",
        f"{selected_summary['remaining_reserves']:.2f}",
    )

    st.caption(selected_result["scenario"]["interpretation"])

    detail_col1, detail_col2 = st.columns(2)

    with detail_col1:
        st.subheader("Supply and demand")

        st.plotly_chart(
            create_supply_chart(selected_result["daily_results"]),
            width="stretch",
        )

    with detail_col2:
        st.subheader("Daily unmet demand")

        st.plotly_chart(
            create_shortage_chart(selected_result["daily_results"]),
            width="stretch",
        )

    # --------------------------------------------------
    # Export
    # --------------------------------------------------

    st.download_button(
        label="Download all 18 experiments as CSV",
        data=empirical_df.to_csv(index=False).encode("utf-8"),
        file_name="empirical_oil_scenario_comparison.csv",
        mime="text/csv",
    )

# ==================================================
# TAB 5: EVIDENCE-AWARE RESERVE CALIBRATION
# ==================================================

with reserve_tab:
    st.header("Evidence-aware reserve calibration")

    st.warning(
        "This is a separate, user-parameterized calibration experiment. "
        "It does not alter the 18 normalized experiments above. The selected "
        "physical daily-demand denominator must match the reserve record's scope."
    )

    calibratable_profiles = list_calibratable_profiles()
    profile_options = {
        f"{row['country']} — {row['reference_date']}": row
        for _, row in calibratable_profiles.iterrows()
    }
    selected_profile_label = st.selectbox(
        "Reserve profile",
        options=list(profile_options),
    )
    selected_profile = profile_options[selected_profile_label]

    st.caption(
        f"Source: {selected_profile['source_organization']}. "
        f"Stock category: {selected_profile['stock_category']}."
    )

    input_col1, input_col2 = st.columns(2)
    with input_col1:
        physical_daily_demand = st.number_input(
            "Physical daily flow represented by model demand "
            "(million barrels per day)",
            min_value=0.0,
            value=0.0,
            step=0.1,
            help=(
                "Enter the same physical flow represented by the simulation daily-demand "
                "series. If the stock-cover basis is crude-oil net imports, "
                "model daily demand must represent that net-import flow, not "
                "total oil consumption. This value is user supplied."
            ),
        )
        demand_denominator_basis = st.text_input(
            "Denominator definition",
            value="User-specified crude-oil daily flow denominator",
        )
    with input_col2:
        model_daily_demand = st.number_input(
            "Daily demand in simulation units",
            min_value=0.1,
            value=95.0,
            step=1.0,
        )

    if physical_daily_demand <= 0:
        st.info(
            "Enter a positive physical daily-flow denominator to calculate "
            "model-scale reserve inputs. No default denominator is assumed."
        )
    else:
        calibration = calibrate_reserve_profile(
            country=selected_profile["country"],
            reference_date=selected_profile["reference_date"],
            physical_daily_demand=physical_daily_demand,
            physical_daily_demand_unit="million barrels per day",
            model_daily_demand=model_daily_demand,
            demand_denominator_basis=demand_denominator_basis,
        )

        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        metric_col1.metric(
            "Derived stock cover",
            f"{calibration['derived_stock_cover_days']:.1f} days",
        )
        metric_col2.metric(
            "Model reserve inventory",
            f"{calibration['initial_reserves_model_units']:.1f} units",
        )
        metric_col3.metric(
            "Model daily release cap",
            f"{calibration['reserve_release_limit_model_units']:.2f} units/day",
        )
        metric_col4.metric(
            "First delivery day",
            calibration["reserve_release_start_day"],
        )

        st.caption(
            "The stock-cover result is calculated from the user-entered "
            "denominator; it is not a separately reported official metric. "
            "The release cap is DOE's nominal capability scaled to the chosen "
            "denominator, not a guarantee of market delivery."
        )

        drawdown_profile = st.selectbox(
            "Reserve drawdown profile",
            options=[
                "DOE 2016 design-reference taper",
                "Constant nominal cap (comparison only)",
            ],
            key="reserve_calibration_drawdown_profile",
            help=(
                "The DOE taper uses historical 2016 design rates. It is not a "
                "measurement of current effective SPR capability."
            ),
        )

        if drawdown_profile == "DOE 2016 design-reference taper":
            st.dataframe(
                pd.DataFrame(
                    [
                        ["Days 1–90", 4.4],
                        ["Days 91–120", 3.8],
                        ["Days 121–150", 3.4],
                        ["Days 151–180", 1.9],
                    ],
                    columns=[
                        "Days since first delivery",
                        "DOE design rate (million barrels/day)",
                    ],
                ),
                width="stretch",
                hide_index=True,
            )
            st.caption(
                "The DOE 2016 curve is expressed as a fraction of the calibrated "
                "4.4-million-barrel/day nominal cap. For model days beyond day 180, "
                "the final 1.9 rate is held constant; that extension is an explicit "
                "extrapolation because the cited curve ends at day 180. "
                f"Source: {calibration['doe_spr_design_reference_url']}"
            )
            st.warning(
                "This is a historical design-reference curve, not a current "
                "capability forecast. GAO reported effective aggregate drawdown "
                "capability of 2.700 million barrels/day versus a 4.415 design rate "
                "as of December 2025 (61%). The dated effective rate reflects "
                "site outages, infrastructure and inventory limits. The model "
                "does not combine that aggregate figure with the 2016 taper because "
                "a current time-varying site-level curve is not available in this "
                "calibration record. Source: https://www.gao.gov/products/gao-26-106918"
            )
        else:
            st.warning(
                "This comparison holds the nominal cap constant and therefore "
                "does not reproduce DOE's published post-90-day decline."
            )

        st.info(
            "The selected disruption percentage is an EIA-derived regional Gulf "
            "producer benchmark or a hypothetical stress test, while the reserve "
            "profile is the U.S. SPR. This combined experiment is an abstract "
            "sensitivity analysis, not a reconstruction of a documented U.S. "
            "SPR deployment or a country-specific market balance."
        )

        st.subheader("Run a reserve-calibrated scenario")
        scenario_lookup = {
            item["scenario_id"]: item
            for item in list_empirical_scenarios()
        }
        selected_reserve_scenario = st.selectbox(
            "Disruption scenario",
            options=list(scenario_lookup),
            format_func=lambda value: scenario_lookup[value]["name"],
            key="reserve_calibration_scenario",
        )
        selected_reserve_strategy = st.selectbox(
            "Response strategy",
            options=["Reserve release", "Combined response"],
            key="reserve_calibration_strategy",
        )

        calibrated_inputs = build_simulation_inputs(
            selected_reserve_scenario,
            selected_reserve_strategy,
        )
        calibrated_inputs.update(
            {
                "daily_demand": model_daily_demand,
                "initial_reserves": calibration["initial_reserves_model_units"],
                "reserve_release_limit": calibration["reserve_release_limit_model_units"],
                "reserve_release_start_day": calibration["reserve_release_start_day"],
                "reserve_release_schedule": (
                    calibration["doe_spr_design_reference_schedule"]
                    if drawdown_profile == "DOE 2016 design-reference taper"
                    else None
                ),
            }
        )
        calibrated_results = run_simulation(**calibrated_inputs)
        calibrated_summary = summarize_results(calibrated_results)

        result_col1, result_col2, result_col3, result_col4 = st.columns(4)
        result_col1.metric(
            "Total unmet demand",
            f"{calibrated_summary['total_unmet_demand']:.1f}",
        )
        result_col2.metric("Shortage days", calibrated_summary["shortage_days"])
        result_col3.metric(
            "Remaining reserves",
            f"{calibrated_summary['remaining_reserves']:.1f}",
        )
        result_col4.metric(
            "Total reserve released",
            f"{sum(row['reserve_release'] for row in calibrated_results):.1f}",
        )

        st.plotly_chart(
            create_supply_chart(calibrated_results),
            width="stretch",
        )
        calibrated_daily_df = pd.DataFrame(calibrated_results)
        st.download_button(
            "Download calibrated daily simulation",
            data=calibrated_daily_df.to_csv(index=False).encode("utf-8"),
            file_name="reserve_calibrated_simulation.csv",
            mime="text/csv",
        )
        calibration_export = pd.DataFrame([{
            **calibration,
            "selected_drawdown_profile": drawdown_profile,
        }])
        st.download_button(
            "Download calibration parameters",
            data=calibration_export.to_csv(index=False).encode("utf-8"),
            file_name="reserve_calibration_parameters.csv",
            mime="text/csv",
        )

    st.divider()
    st.subheader("Japan: announced stock-release equivalents")
    japan_event_summary = summarize_announced_release_denominators()
    st.dataframe(
        japan_event_summary[
            [
                "decision_date",
                "announced_quantity",
                "quantity_unit",
                "equivalent_days",
                "implied_daily_supply_equivalent",
                "implied_daily_supply_unit",
            ]
        ],
        width="stretch",
        hide_index=True,
    )
    st.caption(
        "The implied daily-supply-equivalent column is announced volume divided "
        "by the official equivalent-days statement. It is a derived denominator "
        "check, not a physical release rate, withdrawal time series, or evidence "
        "that the announced volumes were fully delivered."
    )

# ==================================================
# TAB 6: DETERMINISTIC UNCERTAINTY ENVELOPE
# ==================================================

with uncertainty_tab:
    st.header("Deterministic uncertainty envelope")
    st.caption(
        "Explore how combinations of uncertain assumptions change cumulative "
        "unmet demand and reserve performance."
    )

    st.warning(
        "This is a deterministic full-factorial scenario grid, not a probabilistic "
        "forecast. The median is the median of the enumerated design points; it is "
        "not an expected value, confidence interval, or likelihood estimate."
    )

    uncertainty_col1, uncertainty_col2 = st.columns(2)
    scenario_options = {
        item["scenario_id"]: item
        for item in list_empirical_scenarios()
        if item["shock_loss_pct"] > 0 and item["shock_duration_days"] > 0
    }
    with uncertainty_col1:
        uncertainty_scenario_id = st.selectbox(
            "Disruption scenario",
            options=list(scenario_options),
            index=list(scenario_options).index("observed_benchmark"),
            format_func=lambda value: scenario_options[value]["name"],
            key="uncertainty_scenario",
        )
    with uncertainty_col2:
        uncertainty_strategy = st.selectbox(
            "Response strategy",
            options=["Reserve release", "Combined response"],
            key="uncertainty_strategy",
        )

    st.markdown("**Assumption ranges**")
    assumption_ranges = pd.DataFrame(
        [
            ["Supply shock multiplier", "0.8× / 1.0× / 1.2×"],
            ["Shock duration multiplier", "0.8× / 1.0× / 1.2×"],
            ["Starting reserve inventory", "50% / 75% / 100% of baseline"],
            ["Daily release cap", "50% / 75% / 100% of baseline"],
            ["Supply recovery multiplier", "0.5× / 1.0× / 1.5×"],
            ["Additional mobilisation delay", "0 / 7 / 14 days"],
        ],
        columns=["Parameter", "Tested levels"],
    )
    st.dataframe(assumption_ranges, width="stretch", hide_index=True)
    st.caption(
        "The six three-level dimensions create 3⁶ = 729 design points. "
        "The 100% reserve and release-cap levels preserve the baseline values; "
        "zero additional delay and 1.0× multipliers form the neutral reference case."
    )

    uncertainty_result = run_scenario_envelope(
        scenario_id=uncertainty_scenario_id,
        strategy=uncertainty_strategy,
    )
    uncertainty_runs = uncertainty_result["runs"]
    uncertainty_envelope = uncertainty_result["envelope"]

    st.subheader("Outcome envelope")
    metric_row = uncertainty_envelope[
        uncertainty_envelope["metric"] == "total_unmet_demand"
    ].iloc[0]
    reference_unmet = metric_row["reference_case"]
    min_unmet = metric_row["minimum"]
    max_unmet = metric_row["maximum"]

    envelope_col1, envelope_col2, envelope_col3, envelope_col4 = st.columns(4)
    envelope_col1.metric("Design points", uncertainty_result["run_count"])
    envelope_col2.metric("Reference unmet demand", f"{reference_unmet:,.1f}")
    envelope_col3.metric("Lowest unmet demand", f"{min_unmet:,.1f}")
    envelope_col4.metric("Highest unmet demand", f"{max_unmet:,.1f}")

    st.dataframe(
        uncertainty_envelope.rename(
            columns={
                "metric": "Outcome metric",
                "minimum": "Minimum across design points",
                "median_of_design_points": "Median design point",
                "maximum": "Maximum across design points",
                "reference_case": "Neutral reference case",
            }
        ).round(2),
        width="stretch",
        hide_index=True,
    )

    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.subheader("Cumulative unmet-demand distribution")
        histogram = go.Figure(
            go.Histogram(
                x=uncertainty_runs["total_unmet_demand"],
                nbinsx=30,
                name="Design points",
            )
        )
        histogram.update_layout(
            xaxis_title="Total unmet demand (model units)",
            yaxis_title="Number of design points",
            template="plotly_dark",
        )
        st.plotly_chart(histogram, width="stretch")

    with chart_col2:
        st.subheader("Reserve and recovery trade-offs")
        scatter = go.Figure(
            go.Scatter(
                x=uncertainty_runs["reserve_release_start_day"],
                y=uncertainty_runs["total_unmet_demand"],
                mode="markers",
                marker={
                    "size": 7,
                    "color": uncertainty_runs["recovery_rate"],
                    "showscale": True,
                    "colorbar": {"title": "Recovery rate"},
                },
                text=[
                    (
                        f"Shock: {row.shock_loss_pct:.1f}%<br>"
                        f"Duration: {row.shock_duration_days} days<br>"
                        f"Inventory: {row.initial_reserves_model_units:.1f}<br>"
                        f"Release cap: {row.release_limit_model_units_per_day:.2f}/day"
                    )
                    for row in uncertainty_runs.itertuples()
                ],
                hovertemplate=(
                    "First delivery day: %{x}<br>"
                    "Total unmet demand: %{y:.1f}<br>"
                    "%{text}<extra></extra>"
                ),
                name="Scenario design point",
            )
        )
        scatter.update_layout(
            xaxis_title="First reserve delivery day",
            yaxis_title="Total unmet demand (model units)",
            template="plotly_dark",
        )
        st.plotly_chart(scatter, width="stretch")

    best_run = uncertainty_runs.loc[
        uncertainty_runs["total_unmet_demand"].idxmin()
    ]
    worst_run = uncertainty_runs.loc[
        uncertainty_runs["total_unmet_demand"].idxmax()
    ]
    st.subheader("Boundary cases")
    boundary_col1, boundary_col2 = st.columns(2)
    with boundary_col1:
        st.markdown("**Lowest unmet demand design point**")
        st.dataframe(
            best_run.to_frame("Value"),
            width="stretch",
        )
    with boundary_col2:
        st.markdown("**Highest unmet demand design point**")
        st.dataframe(
            worst_run.to_frame("Value"),
            width="stretch",
        )

    st.subheader("Which assumptions move the result most?")
    st.caption(
        "Main effect = mean unmet demand at the high level minus mean unmet "
        "demand at the low level, averaged over all combinations of the other "
        "five factors. This ranks average one-factor effects; it does not remove "
        "or fully explain interactions."
    )
    factor_effects = uncertainty_result["factor_effects"]
    st.dataframe(
        factor_effects.round(2),
        width="stretch",
        hide_index=True,
    )
    effects_chart = go.Figure(
        go.Bar(
            x=factor_effects["absolute_main_effect"],
            y=factor_effects["factor"],
            orientation="h",
            name="Absolute high-low main effect",
        )
    )
    effects_chart.update_layout(
        xaxis_title="Absolute change in mean total unmet demand",
        yaxis_title="Assumption",
        yaxis={"categoryorder": "total ascending"},
        template="plotly_dark",
    )
    st.plotly_chart(effects_chart, width="stretch")

    st.download_button(
        "Download all 729 design points",
        data=uncertainty_runs.to_csv(index=False).encode("utf-8"),
        file_name="shock_simulator_uncertainty_design_points.csv",
        mime="text/csv",
    )
    st.download_button(
        "Download outcome envelope",
        data=uncertainty_envelope.to_csv(index=False).encode("utf-8"),
        file_name="shock_simulator_uncertainty_envelope.csv",
        mime="text/csv",
    )
    st.download_button(
        "Download assumption sensitivity ranking",
        data=factor_effects.to_csv(index=False).encode("utf-8"),
        file_name="shock_simulator_uncertainty_factor_effects.csv",
        mime="text/csv",
    )

