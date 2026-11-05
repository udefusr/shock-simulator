"""Tests for the first Shock Simulator model.

Run from the project root:
    python -m pytest -v

Expected layout:
    src/simulation.py
    tests/test_simulation.py
"""

import pytest

from src.simulation import run_simulation


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
