from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

DATA_FILE = ROOT / "data" / "processed" / "crude_oil_historical_panel.csv"

OUTPUT_DIR = ROOT / "data" / "processed"

COUNTRIES = {
    "SA": "Saudi Arabia",
    "KW": "Kuwait",
    "CN": "China",
    "IN": "India",
    "JP": "Japan",
    "KR": "South Korea",
    "DE": "Germany",
}

INDICATORS = {
    "INDPROD": "Production",
    "TOTIMPSB": "Imports",
    "TOTEXPSB": "Exports",
    "REFINOBS": "Refinery intake",
    "DIRECUSE": "Direct use",
}


def summarize_period(data, flow, year, start_month, end_month):

    selected = data[
        (data["FLOW_BREAKDOWN"] == flow)
        & (data["OBSERVATION_DATE"].dt.year == year)
        & (data["OBSERVATION_DATE"].dt.month.between(start_month, end_month))
        & (data["UNIT_MEASURE"] == "KBD")
    ].copy()

    selected = selected.dropna(subset=["OBS_VALUE_NUMERIC"])

    expected_months = end_month - start_month + 1
    available_months = selected["OBSERVATION_DATE"].nunique()

    result = {
        "months_available": available_months,
        "months_expected": expected_months,
        "weighted_average": None,
    }

    # Do not silently calculate a complete-period average
    # from an incomplete period.
    if available_months != expected_months:
        return result

    weights = selected["OBSERVATION_DATE"].dt.days_in_month

    result["weighted_average"] = (
        selected["OBS_VALUE_NUMERIC"] * weights
    ).sum() / weights.sum()

    return result


def main():

    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Historical panel not found: {DATA_FILE}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(
        DATA_FILE,
        parse_dates=["OBSERVATION_DATE"],
        dtype={"ASSESSMENT_CODE": str},
    )

    reports = []

    for country, country_name in COUNTRIES.items():
        country_data = df[df["REF_AREA"] == country]

        for flow, indicator in INDICATORS.items():
            baseline = summarize_period(country_data, flow, 2025, 3, 8)

            pre_shock = summarize_period(country_data, flow, 2026, 1, 2)

            event = summarize_period(country_data, flow, 2026, 3, 8)

            baseline_value = baseline["weighted_average"]
            pre_value = pre_shock["weighted_average"]
            event_value = event["weighted_average"]

            event_yoy_change = None
            event_vs_pre_change = None

            if baseline_value is not None and baseline_value != 0:
                if event_value is not None:
                    event_yoy_change = (
                        (event_value - baseline_value) / baseline_value
                    ) * 100

            if pre_value is not None and pre_value != 0:
                if event_value is not None:
                    event_vs_pre_change = ((event_value - pre_value) / pre_value) * 100

            reports.append(
                {
                    "Country": country_name,
                    "Indicator": indicator,
                    "Unit": "KBD",
                    "2025_Mar_Aug": baseline_value,
                    "2025_months": baseline["months_available"],
                    "2026_Jan_Feb": pre_value,
                    "2026_pre_months": pre_shock["months_available"],
                    "2026_Mar_Aug": event_value,
                    "2026_event_months": event["months_available"],
                    "Event_vs_2025_pct": event_yoy_change,
                    "Event_vs_pre_shock_pct": event_vs_pre_change,
                }
            )

    comparison = pd.DataFrame(reports)

    output_file = OUTPUT_DIR / "crude_oil_event_window_comparison.csv"

    comparison.to_csv(output_file, index=False)

    print("\n" + "=" * 100)
    print("CRUDE OIL EVENT-WINDOW ANALYSIS")
    print("=" * 100)

    display_columns = [
        "Country",
        "Indicator",
        "2025_Mar_Aug",
        "2026_Jan_Feb",
        "2026_Mar_Aug",
        "Event_vs_2025_pct",
        "Event_vs_pre_shock_pct",
    ]

    print(comparison[display_columns].round(2).to_string(index=False))

    print("\nCoverage summary:")

    print(
        comparison[
            [
                "Country",
                "Indicator",
                "2025_months",
                "2026_pre_months",
                "2026_event_months",
            ]
        ].to_string(index=False)
    )

    print("\nSaved to:")
    print(output_file)


if __name__ == "__main__":
    main()
