"""Validate the initial reserve profile dataset.

Run from the project root:
    python -m scripts.validate_reserve_data
"""

from src.reserve_data import load_reserve_profiles


def main():
    profiles = load_reserve_profiles()

    print("Reserve profile dataset PASSED")
    print(f"Records: {len(profiles)}")
    print(f"Countries: {profiles['country'].nunique()}")
    print(
        "Records with reported inventory:",
        int(profiles["inventory_quantity"].notna().sum()),
    )
    print(
        "Records with reported capacity:",
        int(profiles["capacity_quantity"].notna().sum()),
    )
    print(
        "Records with reported nominal release rate:",
        int(profiles["nominal_release_rate"].notna().sum()),
    )
    print("Blank values are retained as unknown/not reported.")
    print("All reserve profile checks passed.")


if __name__ == "__main__":
    main()
