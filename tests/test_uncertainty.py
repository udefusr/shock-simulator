import pytest

from src.empirical_scenarios import run_empirical_scenario
from src.uncertainty import run_scenario_envelope


def test_default_scenario_envelope_runs_full_factorial_design():
    result = run_scenario_envelope(
        scenario_id="observed_benchmark",
        strategy="Reserve release",
    )
    assert result["run_count"] == 729
    assert len(result["runs"]) == 729
    assert len(result["envelope"]) == 7
    assert set(result["envelope"]["metric"]) == {
        "total_unmet_demand",
        "shortage_days",
        "critical_days",
        "severe_days",
        "maximum_shortage_percentage",
        "remaining_reserves",
        "total_reserve_released",
    }


def test_reference_case_matches_existing_empirical_scenario():
    baseline = run_empirical_scenario(
        scenario_id="observed_benchmark",
        strategy="Reserve release",
    )
    envelope = run_scenario_envelope(
        scenario_id="observed_benchmark",
        strategy="Reserve release",
    )
    assert envelope["reference_summary"] == baseline["summary"]
    assert envelope["reference_inputs"] == baseline["inputs"]


def test_uncertainty_envelope_is_deterministic():
    first = run_scenario_envelope("september_conditions")
    second = run_scenario_envelope("september_conditions")
    assert first["runs"].equals(second["runs"])
    assert first["envelope"].equals(second["envelope"])


def test_no_intervention_is_rejected_for_reserve_uncertainty_grid():
    with pytest.raises(ValueError, match="reserve-enabled"):
        run_scenario_envelope("observed_benchmark", strategy="No intervention")


def test_grid_size_limit_is_enforced():
    with pytest.raises(ValueError, match="exceeding max_runs"):
        run_scenario_envelope("observed_benchmark", max_runs=500)


def test_scenario_envelope_requires_three_strictly_increasing_levels():
    with pytest.raises(ValueError, match="strictly increasing"):
        run_scenario_envelope(
            "observed_benchmark",
            shock_loss_multipliers=(0.8, 0.8, 1.2),
        )


def test_scenario_envelope_requires_a_neutral_reference_point():
    with pytest.raises(ValueError, match="neutral levels"):
        run_scenario_envelope(
            "observed_benchmark",
            shock_loss_multipliers=(0.7, 0.8, 0.9),
        )


def test_scenario_envelope_rejects_shock_above_100_percent():
    with pytest.raises(ValueError, match="above 100%"):
        run_scenario_envelope(
            "extreme_stress",
            shock_loss_multipliers=(1.0, 1.1, 1.2),
        )
