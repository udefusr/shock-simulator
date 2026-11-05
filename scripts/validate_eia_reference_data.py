from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "raw" / "other"

ROUTE_FILE = DATA_DIR / "eia_chokepoint_flows.csv"
SHUTIN_FILE = DATA_DIR / "eia_production_shutins.csv"


def validate_routes():
    df = pd.read_csv(ROUTE_FILE)

    assert len(df) == 48
    assert df["Route"].nunique() == 8
    assert df["Quarter"].nunique() == 6

    assert not df.duplicated(["Quarter", "Route"]).any()

    assert df["Flow_million_barrels_per_day"].notna().all()

    hormuz = df[df["Route"] == "Strait of Hormuz"]

    expected = {
        "2025-Q1": 20.9,
        "2025-Q2": 21.0,
        "2025-Q3": 21.3,
        "2025-Q4": 21.6,
        "2026-Q1": 14.9,
        "2026-Q2": 4.9,
    }

    actual = dict(
        zip(
            hormuz["Quarter"],
            hormuz["Flow_million_barrels_per_day"],
        )
    )

    assert actual == expected

    print("Chokepoint dataset: PASSED")
    print(f"  Observations: {len(df)}")
    print(f"  Routes: {df['Route'].nunique()}")


def validate_shutins():
    df = pd.read_csv(SHUTIN_FILE)

    total = df[df["Country"] == "Total listed producers"]

    countries = df[df["Country"] != "Total listed producers"]

    assert len(countries) == 7
    assert len(total) == 1

    checks = {
        "Feb_2026_production_kbd": 25200,
        "Mar_Jul_average_shutins_kbd": 8512,
        "Aug_2026_shutins_kbd": 5760,
        "Sep_2026_shutins_kbd": 4770,
    }

    for column, expected in checks.items():
        actual = countries[column].sum()

        assert actual == expected, f"{column}: expected {expected}, got {actual}"

        assert total.iloc[0][column] == expected

    assert total.iloc[0]["Q4_2026_forecast_shutins_kbd"] == 4470
    assert total.iloc[0]["Q1_2027_forecast_shutins_kbd"] == 2683

    # Country-level forecasts should remain unavailable.
    forecast_columns = [
        "Q4_2026_forecast_shutins_kbd",
        "Q1_2027_forecast_shutins_kbd",
    ]

    assert countries[forecast_columns].isna().all().all()

    print("Production shut-in dataset: PASSED")
    print(f"  Countries: {len(countries)}")
    print("  Country estimates reconcile with aggregate totals.")
    print("  Aggregate forecasts preserved separately.")


def main():
    validate_routes()
    validate_shutins()

    print("\nAll EIA reference-data checks passed.")


if __name__ == "__main__":
    main()
