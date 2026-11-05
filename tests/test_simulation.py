"""Tests for the first Shock Simulator model.

Run from the project root:
    python -m pytest -v

Expected layout:
    src/simulation.py
    tests/test_simulation.py
"""

import pytest

from src.simulation import classify_severity, run_simulation


def test_normal_operation_has_no_shortage_or_reserve_release():
    results = run_simulation(
        baseline_supply=100,
        daily_demand=95,
        initial_reserves=200,
        shock_loss_pct=0,
        days=5,
    )
    assert len(results) == 5
    for row in results:
        assert row["supply"] == pytest.approx(100)
        assert row["demand"] == pytest.approx(95)
        assert row["reserve_release"] == pytest.approx(0)
        assert row["unmet_demand"] == pytest.approx(0)
        assert row["reserves_remaining"] == pytest.approx(200)


def test_shock_reduces_supply_and_creates_shortage():
    results = run_simulation(
        baseline_supply=100,
        daily_demand=95,
        initial_reserves=200,
        shock_loss_pct=0.25,
        shock_start_day=1,
        shock_duration=2,
        use_reserves=False,
        days=4,
    )
    assert [r["supply"] for r in results] == pytest.approx([75, 75, 77.5, 79.75])
    assert results[0]["unmet_demand"] == pytest.approx(20)
    assert results[2]["unmet_demand"] == pytest.approx(17.5)
    assert results[3]["unmet_demand"] == pytest.approx(15.25)


def test_reserves_reduce_but_do_not_remove_shortage_entirely():
    results = run_simulation(
        baseline_supply=100,
        daily_demand=95,
        initial_reserves=200,
        shock_loss_pct=0.25,
        shock_duration=1,
        reserve_release_limit=5,
        use_reserves=True,
        days=1,
    )
    assert results[0]["reserve_release"] == pytest.approx(5)
    assert results[0]["reserves_remaining"] == pytest.approx(195)
    assert results[0]["unmet_demand"] == pytest.approx(15)


def test_reserve_release_never_exceeds_available_reserves():
    results = run_simulation(
        baseline_supply=100,
        daily_demand=95,
        initial_reserves=3,
        shock_loss_pct=0.25,
        shock_duration=2,
        reserve_release_limit=5,
        use_reserves=True,
        days=2,
    )
    assert results[0]["reserve_release"] == pytest.approx(3)
    assert results[0]["reserves_remaining"] == pytest.approx(0)
    assert results[0]["unmet_demand"] == pytest.approx(17)
    assert results[1]["reserve_release"] == pytest.approx(0)
    assert results[1]["unmet_demand"] == pytest.approx(20)


def test_disabling_reserves_means_no_reserve_release():
    results = run_simulation(
        baseline_supply=100,
        daily_demand=95,
        initial_reserves=200,
        shock_loss_pct=0.25,
        shock_duration=2,
        use_reserves=False,
        days=2,
    )
    for row in results:
        assert row["reserve_release"] == pytest.approx(0)
        assert row["reserves_remaining"] == pytest.approx(200)
        assert row["unmet_demand"] == pytest.approx(20)


def test_demand_reduction_lowers_unmet_demand():
    without_reduction = run_simulation(
        baseline_supply=100,
        daily_demand=95,
        initial_reserves=0,
        shock_loss_pct=0.25,
        demand_reduction_pct=0,
        use_reserves=False,
        days=1,
    )
    with_reduction = run_simulation(
        baseline_supply=100,
        daily_demand=95,
        initial_reserves=0,
        shock_loss_pct=0.25,
        demand_reduction_pct=0.10,
        use_reserves=False,
        days=1,
    )
    assert without_reduction[0]["unmet_demand"] == pytest.approx(20)
    assert with_reduction[0]["unmet_demand"] == pytest.approx(10.5)


def test_shock_can_start_later():
    results = run_simulation(
        baseline_supply=100,
        daily_demand=95,
        initial_reserves=100,
        shock_loss_pct=0.25,
        shock_start_day=3,
        shock_duration=2,
        use_reserves=False,
        days=5,
    )
    assert [r["supply"] for r in results] == pytest.approx([100, 100, 75, 75, 77.5])


@pytest.mark.parametrize(
    "parameters",
    [
        {"baseline_supply": -10},
        {"daily_demand": -5},
        {"initial_reserves": -100},
        {"shock_loss_pct": 1.5},
        {"shock_loss_pct": -0.1},
        {"demand_reduction_pct": 1.2},
        {"reserve_release_limit": -2},
        {"days": 0},
        {"shock_start_day": 0},
        {"shock_duration": -1},
    ],
)
def test_invalid_inputs_are_rejected(parameters):
    with pytest.raises((ValueError, TypeError)):
        run_simulation(**parameters)


def test_reserves_never_become_negative():
    results = run_simulation(
        initial_reserves=2,
        shock_loss_pct=0.5,
        shock_duration=5,
        reserve_release_limit=5,
        days=5,
    )

    for row in results:
        assert row["reserves_remaining"] >= 0


def test_shock_status_is_recorded_correctly():
    results = run_simulation(
        shock_start_day=3,
        shock_duration=2,
        days=6,
    )

    assert [r["shock_active"] for r in results] == [
        False,
        False,
        True,
        True,
        False,
        False,
    ]


def test_different_runs_with_same_inputs_are_identical():
    first = run_simulation()
    second = run_simulation()

    assert first == second


def test_shock_duration_zero_means_no_shock():
    results = run_simulation(
        shock_duration=0,
        use_reserves=False,
        days=5,
    )

    assert all(not row["shock_active"] for row in results)


def test_use_reserves_must_be_boolean():
    with pytest.raises(TypeError):
        run_simulation(use_reserves="false")


def test_zero_baseline_supply_is_handled():
    results = run_simulation(
        baseline_supply=0,
        daily_demand=95,
        initial_reserves=0,
        shock_loss_pct=0,
        use_reserves=False,
        days=1,
    )

    assert results[0]["unmet_demand"] == pytest.approx(95)


def test_supply_recovers_gradually_after_shock():
    results = run_simulation(
        baseline_supply=100,
        daily_demand=95,
        initial_reserves=0,
        shock_loss_pct=0.25,
        shock_start_day=1,
        shock_duration=2,
        recovery_rate=0.5,
        use_reserves=False,
        days=5,
    )

    supplies = [row["supply"] for row in results]

    assert supplies == pytest.approx([75, 75, 87.5, 93.75, 96.875])


def test_recovery_rate_one_restores_supply_immediately():
    results = run_simulation(
        baseline_supply=100,
        shock_loss_pct=0.25,
        shock_duration=2,
        recovery_rate=1.0,
        use_reserves=False,
        days=4,
    )

    assert results[2]["supply"] == pytest.approx(100)


def test_invalid_recovery_rates_are_rejected():
    for rate in [-0.1, 0, 1.1]:
        with pytest.raises(ValueError):
            run_simulation(recovery_rate=rate)


def test_severity_classification():
    assert classify_severity(0) == "Normal"
    assert classify_severity(2) == "Warning"
    assert classify_severity(5) == "Warning"
    assert classify_severity(10) == "Critical"
    assert classify_severity(15) == "Critical"
    assert classify_severity(20) == "Severe"


def test_shortage_percentage_is_calculated_correctly():
    results = run_simulation(
        baseline_supply=100,
        daily_demand=100,
        initial_reserves=0,
        shock_loss_pct=0.20,
        use_reserves=False,
        days=1,
    )

    assert results[0]["shortage_percentage"] == pytest.approx(20)
    assert results[0]["severity"] == "Severe"
    assert results[0]["is_critical"] is True


def test_zero_demand_does_not_cause_division_error():
    results = run_simulation(
        baseline_supply=100,
        daily_demand=0,
        initial_reserves=0,
        use_reserves=False,
        days=1,
    )

    assert results[0]["shortage_percentage"] == 0
    assert results[0]["severity"] == "Normal"


def test_custom_severity_thresholds():
    assert classify_severity(7, warning_threshold=8, critical_threshold=20) == "Warning"

    assert (
        classify_severity(15, warning_threshold=8, critical_threshold=20) == "Critical"
    )

    assert classify_severity(25, warning_threshold=8, critical_threshold=20) == "Severe"


def test_invalid_thresholds_are_rejected():
    invalid_configurations = [
        {"warning_threshold": -1},
        {"warning_threshold": 15, "critical_threshold": 10},
        {"critical_threshold": 101},
        {"warning_threshold": 5, "critical_threshold": 5},
    ]

    for parameters in invalid_configurations:
        with pytest.raises(ValueError):
            run_simulation(**parameters)


def test_custom_thresholds_affect_daily_severity():
    results = run_simulation(
        baseline_supply=100,
        daily_demand=100,
        initial_reserves=0,
        shock_loss_pct=0.10,
        use_reserves=False,
        warning_threshold=5,
        critical_threshold=15,
        days=1,
    )

    assert results[0]["shortage_percentage"] == pytest.approx(10)
    assert results[0]["severity"] == "Critical"


def test_demand_reduction_ends_when_configured_duration_expires():
    results = run_simulation(
        baseline_supply=100,
        daily_demand=95,
        initial_reserves=0,
        shock_loss_pct=0.25,
        shock_duration=2,
        demand_reduction_pct=0.10,
        demand_reduction_start_day=1,
        demand_reduction_duration=2,
        use_reserves=False,
        days=4,
    )

    assert [row["demand"] for row in results] == pytest.approx([85.5, 85.5, 95, 95])

    assert [row["demand_reduction_active"] for row in results] == [
        True,
        True,
        False,
        False,
    ]


def test_demand_reduction_can_start_later():
    results = run_simulation(
        daily_demand=100,
        shock_loss_pct=0,
        demand_reduction_pct=0.10,
        demand_reduction_start_day=3,
        demand_reduction_duration=2,
        days=6,
    )

    assert [row["demand"] for row in results] == pytest.approx(
        [100, 100, 90, 90, 100, 100]
    )


def test_zero_demand_reduction_duration_means_no_reduction():
    results = run_simulation(
        daily_demand=100,
        shock_loss_pct=0,
        demand_reduction_pct=0.10,
        demand_reduction_duration=0,
        days=3,
    )

    assert all(row["demand"] == pytest.approx(100) for row in results)
    assert all(not row["demand_reduction_active"] for row in results)


def test_unspecified_demand_reduction_duration_preserves_old_behavior():
    results = run_simulation(
        daily_demand=100,
        shock_loss_pct=0,
        shock_duration=1,
        demand_reduction_pct=0.10,
        use_reserves=False,
        days=4,
    )

    assert all(row["demand"] == pytest.approx(90) for row in results)
    assert all(row["demand_reduction_active"] for row in results)


def test_invalid_demand_reduction_periods_are_rejected():
    invalid_configurations = [
        {"demand_reduction_start_day": 0},
        {"demand_reduction_duration": -1},
        {"demand_reduction_duration": 1.5},
        {"demand_reduction_duration": True},
        {"demand_reduction_start_day": True},
    ]

    for parameters in invalid_configurations:
        with pytest.raises((ValueError, TypeError)):
            run_simulation(**parameters)


def test_delayed_reserve_mobilization_waits_until_start_day():
    results = run_simulation(
        baseline_supply=100,
        daily_demand=95,
        initial_reserves=100,
        shock_loss_pct=0.25,
        shock_duration=4,
        reserve_release_limit=5,
        reserve_release_start_day=3,
        use_reserves=True,
        days=4,
    )

    assert [row["reserve_release"] for row in results] == pytest.approx([0, 0, 5, 5])
    assert [row["reserve_release_active"] for row in results] == [False, False, True, True]
    assert [row["reserves_remaining"] for row in results] == pytest.approx([100, 100, 95, 90])


def test_reserve_release_start_day_must_be_positive_integer():
    for value in (0, -1, 1.5, True):
        with pytest.raises((ValueError, TypeError)):
            run_simulation(reserve_release_start_day=value)


def test_delayed_reserve_mobilization_does_not_release_when_reserves_disabled():
    results = run_simulation(
        initial_reserves=100,
        shock_loss_pct=0.25,
        shock_duration=3,
        reserve_release_start_day=3,
        use_reserves=False,
        days=3,
    )
    assert all(row["reserve_release"] == 0 for row in results)
    assert all(not row["reserve_release_active"] for row in results)


def test_reserve_release_schedule_uses_days_since_first_delivery():
    schedule = [
        {"start_day": 1, "end_day": 2, "rate_multiplier": 1.0},
        {"start_day": 3, "end_day": None, "rate_multiplier": 0.5},
    ]
    results = run_simulation(
        baseline_supply=100,
        daily_demand=95,
        initial_reserves=100,
        shock_loss_pct=0.25,
        shock_duration=5,
        reserve_release_limit=10,
        reserve_release_start_day=3,
        reserve_release_schedule=schedule,
        days=5,
    )

    assert [row["reserve_drawdown_day"] for row in results] == [None, None, 1, 2, 3]
    assert [row["reserve_release_rate_multiplier"] for row in results] == pytest.approx(
        [0, 0, 1, 1, 0.5]
    )
    assert [row["reserve_release_limit_today"] for row in results] == pytest.approx(
        [0, 0, 10, 10, 5]
    )
    assert [row["reserve_release"] for row in results] == pytest.approx([0, 0, 10, 10, 5])


@pytest.mark.parametrize(
    "schedule",
    [
        [],
        [{"start_day": 2, "end_day": None, "rate_multiplier": 1.0}],
        [
            {"start_day": 1, "end_day": 2, "rate_multiplier": 1.0},
            {"start_day": 4, "end_day": None, "rate_multiplier": 0.5},
        ],
        [{"start_day": 1, "end_day": 2, "rate_multiplier": 1.0}],
        [{"start_day": 1, "end_day": None, "rate_multiplier": 1.1}],
        [{"start_day": 1, "end_day": None, "rate_multiplier": -0.1}],
        [{"start_day": 1, "end_day": None, "rate_multiplier": float("inf")}],
    ],
)
def test_invalid_reserve_release_schedules_are_rejected(schedule):
    with pytest.raises((ValueError, TypeError)):
        run_simulation(reserve_release_schedule=schedule)


def test_reserve_release_schedule_is_ignored_when_reserves_are_disabled():
    results = run_simulation(
        shock_loss_pct=0.25,
        shock_duration=2,
        reserve_release_limit=10,
        use_reserves=False,
        reserve_release_schedule=[
            {"start_day": 1, "end_day": None, "rate_multiplier": 0.5}
        ],
        days=2,
    )
    assert all(row["reserve_release"] == 0 for row in results)
    assert all(row["reserve_release_limit_today"] == 0 for row in results)
