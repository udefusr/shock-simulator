import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.scenarios import summarize_results
from src.sensitivity import analyze_demand_reduction
from src.simulation import run_simulation
from src.empirical_scenarios import (
    RESPONSE_STRATEGIES,
    list_empirical_scenarios,
    run_empirical_scenarios,
)

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

simulation_tab, comparison_tab, sensitivity_tab, empirical_tab = st.tabs(
    [
        "📊 Simulation",
        "⚖️ Scenario comparison",
        "📈 Sensitivity analysis",
        "🛢️ Empirical scenarios",
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
        use_container_width=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Daily unmet demand")

        st.plotly_chart(
            create_shortage_chart(results),
            use_container_width=True,
        )

    with col2:
        st.subheader("System severity")

        st.plotly_chart(
            create_severity_chart(results),
            use_container_width=True,
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
        use_container_width=True,
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

        st.plotly_chart(fig, use_container_width=True)

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

        st.plotly_chart(fig, use_container_width=True)

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
        use_container_width=True,
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

    st.plotly_chart(fig, use_container_width=True)

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
        use_container_width=True,
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
        use_container_width=True,
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
            use_container_width=True,
        )

    with detail_col2:
        st.subheader("Daily unmet demand")

        st.plotly_chart(
            create_shortage_chart(selected_result["daily_results"]),
            use_container_width=True,
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