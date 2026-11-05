import pandas as pd
import pytest

from src.importer_resilience import (
    load_importer_flow_profiles,
    run_importer_resilience_scenario,
)


def test_load_source_backed_importer_profiles():
    profiles = load_importer_flow_profiles()
    assert set(profiles["country"]) == {"China", "India", "South Korea", "Japan"}
    assert profiles["baseline_hormuz_flow_mbd"].sum() == pytest.approx(11.0)


def test_importer_scenario_calculates_alternative_sourcing_and_buffer():
    result = run_importer_resilience_scenario(
        country="China",
        disruption_fraction=0.5,
        disruption_duration_days=3,
        alternative_supply_mbd=1.0,
        alternative_supply_start_day=3,
        buffer_cover_days=2,
        simulation_days=5,
    )
    daily = result["daily"]
    summary = result["summary"]

    assert daily["gross_lost_imports_mbd"].tolist() == pytest.approx(
        [2.7, 2.7, 2.7, 0, 0]
    )
    assert daily["alternative_supply_mbd"].tolist() == pytest.approx(
        [0, 0, 1.0, 0, 0]
    )
    assert daily["buffer_release_mbd"].tolist() == pytest.approx(
        [2.7, 2.7, 0, 0, 0]
    )
    assert summary["starting_buffer_million_barrels"] == pytest.approx(5.4)
    assert summary["total_uncovered_gap_million_barrels"] == pytest.approx(1.7)
    assert summary["ending_buffer_million_barrels"] == pytest.approx(0)


def test_importer_scenario_reports_residual_gap_after_buffer_exhaustion():
    result = run_importer_resilience_scenario(
        country="India",
        disruption_fraction=1.0,
        disruption_duration_days=2,
        buffer_cover_days=0.5,
        simulation_days=2,
    )
    assert result["summary"]["total_uncovered_gap_million_barrels"] == pytest.approx(1.05)
    assert result["summary"]["maximum_daily_uncovered_gap_mbd"] == pytest.approx(1.05)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"disruption_fraction": -0.1},
        {"disruption_fraction": 1.1},
        {"alternative_supply_mbd": -1},
        {"buffer_cover_days": -1},
        {"disruption_duration_days": -1},
        {"alternative_supply_start_day": 0},
        {"simulation_days": 0},
        {"simulation_days": 2, "disruption_duration_days": 3},
    ],
)
def test_invalid_importer_resilience_inputs_are_rejected(kwargs):
    with pytest.raises((TypeError, ValueError)):
        run_importer_resilience_scenario(country="China", **kwargs)


def test_alternative_supply_cannot_exceed_daily_lost_flow():
    result = run_importer_resilience_scenario(
        country="Japan",
        disruption_fraction=0.5,
        disruption_duration_days=1,
        alternative_supply_mbd=9.0,
        simulation_days=1,
    )
    assert result["daily"].iloc[0]["alternative_supply_mbd"] == pytest.approx(0.85)


def test_profiles_must_contain_one_matching_country():
    profiles = pd.DataFrame(
        [{"country": "Test", "baseline_hormuz_flow_mbd": 1.0},
         {"country": "Test", "baseline_hormuz_flow_mbd": 2.0}]
    )
    with pytest.raises(ValueError, match="exactly one"):
        run_importer_resilience_scenario(country="Test", profiles=profiles)
