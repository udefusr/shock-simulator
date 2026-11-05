import pandas as pd
import pytest

from src.importer_lng_resilience import (
    load_lng_importer_profiles,
    run_lng_importer_resilience_scenario,
)


def test_load_source_backed_lng_destination_profiles():
    profiles = load_lng_importer_profiles()
    assert set(profiles["country"]) == {
        "Bangladesh", "Pakistan", "India", "China", "South Korea", "Japan"
    }
    bangladesh = profiles[profiles["country"] == "Bangladesh"].iloc[0]
    assert bangladesh["annual_hormuz_lng_flow_bcm"] == pytest.approx(6.2)


def test_lng_scenario_converts_annual_flow_and_uses_three_response_levers():
    result = run_lng_importer_resilience_scenario(
        country="Bangladesh",
        disruption_fraction=0.5,
        disruption_duration_days=3,
        alternative_supply_mcm_per_day=5.0,
        alternative_supply_start_day=2,
        buffer_cover_days=1,
        demand_reduction_fraction=0.25,
        simulation_days=4,
    )
    daily = result["daily"]
    summary = result["summary"]

    baseline = 6200 / 365
    lost = baseline * 0.5
    assert summary["baseline_hormuz_lng_flow_mcm_per_day"] == pytest.approx(baseline)
    assert daily["gross_lost_lng_mcm_per_day"].tolist() == pytest.approx(
        [lost, lost, lost, 0]
    )
    assert daily["alternative_lng_mcm_per_day"].tolist() == pytest.approx(
        [0, 5, 5, 0]
    )
    assert summary["starting_buffer_mcm"] == pytest.approx(lost)
    assert summary["total_buffer_release_mcm"] == pytest.approx(lost)
    assert summary["total_demand_response_mcm"] == pytest.approx(
        (lost * 0.25) * 2
    )
    assert summary["total_uncovered_lng_gap_mcm"] == pytest.approx(
        (lost - 5.0 - (lost * 0.25)) * 2
    )


def test_lng_scenario_residual_gap_when_no_response_capacity_exists():
    result = run_lng_importer_resilience_scenario(
        country="Bangladesh",
        disruption_fraction=1.0,
        disruption_duration_days=2,
        simulation_days=2,
    )
    baseline = 6200 / 365
    assert result["summary"]["total_uncovered_lng_gap_mcm"] == pytest.approx(
        baseline * 2
    )


@pytest.mark.parametrize(
    "kwargs",
    [
        {"disruption_fraction": -0.1},
        {"disruption_fraction": 1.1},
        {"alternative_supply_mcm_per_day": -1},
        {"buffer_cover_days": -1},
        {"demand_reduction_fraction": -0.1},
        {"demand_reduction_fraction": 1.1},
        {"disruption_duration_days": -1},
        {"alternative_supply_start_day": 0},
        {"simulation_days": 0},
        {"days_in_year": 364},
        {"simulation_days": 2, "disruption_duration_days": 3},
    ],
)
def test_invalid_lng_resilience_inputs_are_rejected(kwargs):
    with pytest.raises((TypeError, ValueError)):
        run_lng_importer_resilience_scenario(country="Bangladesh", **kwargs)


def test_alternative_supply_is_capped_at_the_daily_lost_lng_flow():
    result = run_lng_importer_resilience_scenario(
        country="Bangladesh",
        disruption_fraction=0.5,
        disruption_duration_days=1,
        alternative_supply_mcm_per_day=1000,
        simulation_days=1,
    )
    assert result["daily"].iloc[0]["alternative_lng_mcm_per_day"] == pytest.approx(
        (6200 / 365) * 0.5
    )


def test_duplicate_country_profiles_are_rejected():
    profiles = pd.DataFrame(
        [
            {"country": "Test", "annual_hormuz_lng_flow_bcm": 1.0, "reference_year": 2025},
            {"country": "Test", "annual_hormuz_lng_flow_bcm": 2.0, "reference_year": 2025},
        ]
    )
    with pytest.raises(ValueError, match="exactly one"):
        run_lng_importer_resilience_scenario(country="Test", profiles=profiles)
