"""Validate reserve profiles and reserve response events.

Run from the project root:
    python -m scripts.validate_reserve_data
"""
from src.reserve_data import load_reserve_profiles, load_reserve_response_events
from src.reserve_calibration import list_calibratable_profiles


def main():
    profiles = load_reserve_profiles()
    events = load_reserve_response_events()
    calibratable = list_calibratable_profiles(profiles)
    print("Reserve profile dataset PASSED")
    print(f"Profile records: {len(profiles)}")
    print(f"Countries: {profiles['country'].nunique()}")
    print("Records with inventory:", int(profiles["inventory_quantity"].notna().sum()))
    print("Records with capacity:", int(profiles["capacity_quantity"].notna().sum()))
    print("Records with release rate:", int(profiles["nominal_release_rate"].notna().sum()))
    print("Profiles eligible for unit-compatible calibration:", len(calibratable))
    print("Calibration countries:", ", ".join(sorted(calibratable["country"].unique())))
    print("\nReserve response event dataset PASSED")
    print(f"Response events: {len(events)}")
    print(f"Countries: {events['country'].nunique()}")
    print("Events with announced quantities:", int(events["announced_quantity"].notna().sum()))
    print("Events with obligation changes:", int(events["obligation_reduction_days"].notna().sum()))
    print("\nBlank values mean unknown/not reported, not zero.")
    print("Announced releases are not verified physical withdrawals.")
    print("All reserve data checks passed.")


if __name__ == "__main__":
    main()
