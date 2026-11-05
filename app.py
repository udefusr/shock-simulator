import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.scenarios import summarize_results
from src.sensitivity import analyze_demand_reduction
from src.simulation import run_simulation

st.set_page_config(
    page_title="Shock Simulator",
    page_icon="⚡",
    layout="wide",
)

st.title("⚡ Shock Simulator")
st.caption("Supply disruption, reserve deployment and recovery modelling")

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

results = run_simulation(
    baseline_supply=baseline_supply,
    daily_demand=daily_demand,
    initial_reserves=initial_reserves,
    shock_loss_pct=shock_loss_pct,
    shock_start_day=shock_start_day,
    shock_duration=shock_duration,
    reserve_release_limit=reserve_release_limit,
    recovery_rate=recovery_rate,
    days=days,
)

total_unmet = sum(row["unmet_demand"] for row in results)
shortage_days = sum(row["unmet_demand"] > 0 for row in results)
final_reserves = results[-1]["reserves_remaining"]

col1, col2, col3 = st.columns(3)

col1.metric("Total unmet demand", f"{total_unmet:.2f}")
col2.metric("Shortage days", shortage_days)
col3.metric("Remaining reserves", f"{final_reserves:.2f}")

st.divider()

st.subheader("Supply vs. demand")

days_axis = [row["day"] for row in results]
baseline_supply_series = [row["supply"] for row in results]
reserve_contribution = [row["reserve_release"] for row in results]
total_available_supply = [row["supply"] + row["reserve_release"] for row in results]
demand = [row["demand"] for row in results]

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=days_axis,
        y=baseline_supply_series,
        mode="lines",
        name="Baseline supply",
    )
)

fig.add_trace(
    go.Scatter(
        x=days_axis, y=reserve_contribution, mode="lines", name="Reserve contribution"
    )
)

fig.add_trace(
    go.Scatter(
        x=days_axis,
        y=total_available_supply,
        mode="lines",
        name="Total available supply",
        line=dict(width=3),
    )
)

fig.add_trace(
    go.Scatter(
        x=days_axis, y=demand, mode="lines", name="Demand", line=dict(dash="dash")
    )
)

fig.update_layout(
    xaxis_title="Simulation day",
    yaxis_title="Resource units",
    hovermode="x unified",
    template="plotly_dark",
)

st.plotly_chart(fig, use_container_width=True)
st.divider()
st.subheader("Daily unmet demand")

unmet_demand = [row["unmet_demand"] for row in results]

shortage_fig = go.Figure()

shortage_fig.add_trace(go.Bar(x=days_axis, y=unmet_demand, name="Unmet demand"))

shortage_fig.update_layout(
    xaxis_title="Simulation day",
    yaxis_title="Unmet resource units",
    hovermode="x unified",
    template="plotly_dark",
)

st.plotly_chart(shortage_fig, use_container_width=True)

st.divider()
st.subheader("System severity timeline")

severity_values = {
    "Normal": 0,
    "Warning": 1,
    "Critical": 2,
    "Severe": 3,
}

severity_days = [row["day"] for row in results]
severity_levels = [severity_values[row["severity"]] for row in results]

severity_fig = go.Figure()

severity_fig.add_trace(
    go.Scatter(
        x=severity_days,
        y=severity_levels,
        mode="lines+markers",
        name="Severity",
        line={"shape": "hv", "width": 3},
    )
)

severity_fig.update_layout(
    xaxis_title="Simulation day",
    yaxis={
        "title": "Severity level",
        "tickmode": "array",
        "tickvals": [0, 1, 2, 3],
        "ticktext": ["Normal", "Warning", "Critical", "Severe"],
        "range": [-0.2, 3.2],
    },
    hovermode="x unified",
    template="plotly_dark",
)

st.plotly_chart(severity_fig, use_container_width=True)

st.divider()
st.header("Scenario comparison")
st.caption("Compare different response strategies under identical conditions.")

common_inputs = {
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

comparison_results = {}

for strategy_name, strategy_settings in strategies.items():
    simulation = run_simulation(
        **common_inputs,
        **strategy_settings,
    )

    comparison_results[strategy_name] = summarize_results(simulation)

comparison_data = []

for strategy_name, summary in comparison_results.items():
    comparison_data.append(
        {
            "Strategy": strategy_name,
            "Total unmet demand": round(summary["total_unmet_demand"], 2),
            "Shortage days": summary["shortage_days"],
            "Critical days": summary["critical_days"],
            "Severe days": summary["severe_days"],
            "Remaining reserves": round(summary["remaining_reserves"], 2),
        }
    )

st.dataframe(
    comparison_data,
    use_container_width=True,
    hide_index=True,
)

st.subheader("Strategy performance")

comparison_fig = go.Figure()

comparison_fig.add_trace(
    go.Bar(
        x=[row["Strategy"] for row in comparison_data],
        y=[row["Total unmet demand"] for row in comparison_data],
        name="Total unmet demand",
    )
)

comparison_fig.update_layout(
    title="Total unmet demand by strategy",
    xaxis_title="Response strategy",
    yaxis_title="Unmet resource units",
    template="plotly_dark",
)

st.plotly_chart(comparison_fig, use_container_width=True)


shortage_fig_comparison = go.Figure()

shortage_fig_comparison.add_trace(
    go.Bar(
        x=[row["Strategy"] for row in comparison_data],
        y=[row["Shortage days"] for row in comparison_data],
        name="Shortage days",
    )
)

shortage_fig_comparison.update_layout(
    title="Shortage days by strategy",
    xaxis_title="Response strategy",
    yaxis_title="Number of days",
    template="plotly_dark",
)

st.plotly_chart(shortage_fig_comparison, use_container_width=True)

st.divider()
st.subheader("Export comparison")

comparison_df = pd.DataFrame(comparison_data)

csv_data = comparison_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download comparison as CSV",
    data=csv_data,
    file_name="shock_simulator_comparison.csv",
    mime="text/csv",
)

st.divider()
st.header("Demand-response sensitivity")
st.caption(
    "Investigate how demand reduction affects system resilience "
    "under identical supply disruption conditions."
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

st.dataframe(
    demand_comparison,
    use_container_width=True,
    hide_index=True,
)

demand_fig = go.Figure()

demand_fig.add_trace(
    go.Scatter(
        x=[row["Demand reduction"] for row in demand_comparison],
        y=[row["Total unmet demand"] for row in demand_comparison],
        mode="lines+markers",
        name="Total unmet demand",
    )
)

demand_fig.update_layout(
    title="Impact of demand reduction on unmet demand",
    xaxis_title="Demand reduction",
    yaxis_title="Total unmet resource units",
    template="plotly_dark",
)

st.plotly_chart(demand_fig, use_container_width=True)

demand_csv = pd.DataFrame(demand_comparison).to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download demand-response analysis as CSV",
    data=demand_csv,
    file_name="demand_response_sensitivity.csv",
    mime="text/csv",
)