import pytest

from src.empirical_scenarios import (
    AUGUST_SHOCK_PCT,
    MARCH_JULY_SHOCK_PCT,
    SEPTEMBER_SHOCK_PCT,
    SIMULATION_HORIZON_DAYS,
    build_simulation_inputs,
    get_empirical_scenario,
    list_empirical_scenarios,
    run_empirical_scenario,
    run_empirical_scenarios,
)


def test_all_six_scenarios_are_available():
    scenarios = list_empirical_scenarios()

    assert len(scenarios) == 6


def test_empirical_shock_percentages_are_calculated_correctly():
    assert MARCH_JULY_SHOCK_PCT == pytest.approx(8.512 / 25.2)
    assert AUGUST_SHOCK_PCT == pytest.approx(5.760 / 25.2)
    assert SEPTEMBER_SHOCK_PCT == pytest.approx(4.770 / 25.2)


def test_all_scenarios_use_the_same_simulation_horizon():
    for scenario in list_empirical_scenarios():
        inputs = build_simulation_inputs(scenario["scenario_id"])

        assert inputs["days"] == SIMULATION_HORIZON_DAYS


def test_baseline_has_no_supply_shock():
    inputs = build_simulation_inputs("baseline")

    assert inputs["shock_loss_pct"] == 0
    assert inputs["shock_duration"] == 0


def test_observed_benchmark_uses_153_day_shock():
    inputs = build_simulation_inputs("observed_benchmark")

    assert inputs["shock_loss_pct"] == pytest.approx(8.512 / 25.2)
    assert inputs["shock_duration"] == 153


def test_august_and_september_use_separate_durations():
    august = build_simulation_inputs("august_conditions")
    september = build_simulation_inputs("september_conditions")

    assert august["shock_duration"] == 31
    assert september["shock_duration"] == 30


def test_no_intervention_strategy_disables_reserves():
    inputs = build_simulation_inputs(
        "observed_benchmark",
        strategy="No intervention",
    )

    assert inputs["use_reserves"] is False
    assert inputs["demand_reduction_pct"] == 0


def test_reserve_strategy_enables_reserves():
    inputs = build_simulation_inputs(
        "observed_benchmark",
        strategy="Reserve release",
    )

    assert inputs["use_reserves"] is True
    assert inputs["demand_reduction_pct"] == 0


def test_combined_strategy_applies_demand_reduction():
    inputs = build_simulation_inputs(
        "observed_benchmark",
        strategy="Combined response",
    )

    assert inputs["use_reserves"] is True
    assert inputs["demand_reduction_pct"] == pytest.approx(0.10)


def test_unknown_scenario_is_rejected():
    with pytest.raises(ValueError):
        get_empirical_scenario("does_not_exist")


def test_unknown_strategy_is_rejected():
    with pytest.raises(ValueError):
        build_simulation_inputs(
            "baseline",
            strategy="Invalid strategy",
        )


def test_scenario_runner_returns_daily_results_and_summary():
    result = run_empirical_scenario(
        "observed_benchmark",
        strategy="No intervention",
    )

    assert len(result["daily_results"]) == SIMULATION_HORIZON_DAYS
    assert result["scenario"]["scenario_id"] == "observed_benchmark"
    assert result["strategy"] == "No intervention"
    assert "total_unmet_demand" in result["summary"]


def test_all_scenarios_can_be_run_together():
    results = run_empirical_scenarios()

    assert len(results) == 6
    assert "baseline" in results
    assert "observed_benchmark" in results
    assert "extreme_stress" in results
