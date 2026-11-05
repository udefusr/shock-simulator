import pandas as pd
import pytest

from src.reserve_data import load_reserve_profiles, validate_reserve_profiles


def test_initial_reserve_profiles_load():
    profiles = load_reserve_profiles()

    assert len(profiles) == 5
    assert set(profiles["country"]) == {
        "United States",
        "Japan",
        "South Korea",
        "Germany",
    }


def test_us_dated_inventory_snapshots_are_preserved():
    profiles = load_reserve_profiles()
    us = profiles[profiles["country"] == "United States"]

    assert set(us["reference_date"]) == {"2025-12-31", "2026-10-16"}
    latest = us[us["reference_date"] == "2026-10-16"].iloc[0]

    assert latest["inventory_quantity"] == pytest.approx(282.2)
    assert latest["capacity_quantity"] == pytest.approx(714.0)


def test_korea_stock_category_excludes_joint_stockpiling():
    profiles = load_reserve_profiles()
    korea = profiles[profiles["country"] == "South Korea"].iloc[0]

    assert "excluding international joint" in korea["stock_category"]


def test_unknown_values_are_not_converted_to_zero():
    profiles = load_reserve_profiles()
    germany = profiles[profiles["country"] == "Germany"].iloc[0]

    assert pd.isna(germany["capacity_quantity"])
    assert pd.isna(germany["nominal_release_rate"])
    assert pd.isna(germany["stock_cover_days"])


def test_negative_inventory_is_rejected():
    profiles = load_reserve_profiles()
    profiles.loc[0, "inventory_quantity"] = -1

    with pytest.raises(ValueError, match="cannot contain negative"):
        validate_reserve_profiles(profiles)


def test_inventory_above_capacity_is_rejected():
    profiles = load_reserve_profiles()
    profiles.loc[0, "inventory_quantity"] = 800

    with pytest.raises(ValueError, match="cannot exceed"):
        validate_reserve_profiles(profiles)


def test_duplicate_profile_key_is_rejected():
    profiles = load_reserve_profiles()
    profiles = pd.concat([profiles, profiles.iloc[[0]]], ignore_index=True)

    with pytest.raises(ValueError, match="Duplicate"):
        validate_reserve_profiles(profiles)


def test_required_column_is_enforced():
    profiles = load_reserve_profiles().drop(columns=["source_url"])

    with pytest.raises(ValueError, match="source_url"):
        validate_reserve_profiles(profiles)
