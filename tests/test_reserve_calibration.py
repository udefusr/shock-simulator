import pandas as pd
import pytest

from src.reserve_calibration import (
    build_doe_spr_design_reference_schedule,
    calibrate_reserve_profile,
    list_calibratable_profiles,
    summarize_announced_release_denominators,
)


def test_only_profiles_with_compatible_release_evidence_are_calibratable():
    profiles = list_calibratable_profiles()
    assert len(profiles) == 2
    assert set(profiles["country"]) == {"United States"}


def test_us_spr_profile_converts_to_model_units_and_delays_release():
    result = calibrate_reserve_profile(
        country="United States",
        reference_date="2026-10-16",
        physical_daily_demand=20.0,
        physical_daily_demand_unit="million barrels per day",
        model_daily_demand=95.0,
        demand_denominator_basis="Illustrative daily crude-oil net imports",
    )
    assert result["derived_stock_cover_days"] == pytest.approx(282.2 / 20.0)
    assert result["initial_reserves_model_units"] == pytest.approx((282.2 / 20.0) * 95)
    assert result["reserve_release_limit_model_units"] == pytest.approx((4.4 / 20.0) * 95)
    assert result["reserve_release_start_day"] == 14
    schedule = result["doe_spr_design_reference_schedule"]
    assert [period["rate_multiplier"] for period in schedule] == pytest.approx(
        [1.0, 3.8 / 4.4, 3.4 / 4.4, 1.9 / 4.4]
    )
    assert schedule[-1]["start_day"] == 151
    assert schedule[-1]["end_day"] is None


def test_ambiguous_us_profile_requires_reference_date():
    with pytest.raises(ValueError, match="reference_date"):
        calibrate_reserve_profile(
            country="United States",
            physical_daily_demand=20.0,
            physical_daily_demand_unit="million barrels per day",
        )


def test_profile_without_release_capability_cannot_be_calibrated():
    with pytest.raises(ValueError, match="lacks"):
        calibrate_reserve_profile(
            country="Japan",
            reference_date="2026-01-31",
            physical_daily_demand=1.0,
            physical_daily_demand_unit="million kilolitres per day",
        )


def test_mismatched_physical_flow_unit_is_rejected():
    with pytest.raises(ValueError, match="Daily-demand unit"):
        calibrate_reserve_profile(
            country="United States",
            reference_date="2026-10-16",
            physical_daily_demand=20.0,
            physical_daily_demand_unit="million tonnes per day",
        )


@pytest.mark.parametrize("demand", [0, -1, float("inf"), float("nan")])
def test_invalid_physical_daily_demand_is_rejected(demand):
    with pytest.raises((ValueError, TypeError)):
        calibrate_reserve_profile(
            country="United States",
            reference_date="2026-10-16",
            physical_daily_demand=demand,
            physical_daily_demand_unit="million barrels per day",
        )


def test_japan_event_equivalents_are_not_mislabeled_as_release_rates():
    summary = summarize_announced_release_denominators()
    assert len(summary) == 2
    assert summary["implied_daily_supply_equivalent"].tolist() == pytest.approx(
        [8.5 / 30, 5.8 / 20]
    )
    assert summary["derived_metric_status"].str.contains("not a release rate").all()


def test_doe_design_reference_schedule_requires_the_documented_nominal_rate():
    schedule = build_doe_spr_design_reference_schedule(4.4)
    assert schedule[0] == {
        "start_day": 1,
        "end_day": 90,
        "rate_multiplier": 1.0,
    }
    with pytest.raises(ValueError, match="4.4"):
        build_doe_spr_design_reference_schedule(2.7)
