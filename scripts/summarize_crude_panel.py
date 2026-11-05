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

# Monthly average flow rates.
RATE_INDICATORS = {
    "INDPROD": "Production",
    "TOTIMPSB": "Imports",
    "TOTEXPSB": "Exports",
    "REFINOBS": "Refinery intake",
    "DIRECUSE": "Direct use",
}


def assessment_summary(series):
    counts = series.value_counts().sort_index()

    return "; ".join(f"{code}: {count}" for code, count in counts.items())


def summarize_rate(df, country, flow, indicator):
    results = {
        "2025_value": None,
        "2026_value": None,
        "2025_months": 0,
        "2026_months": 0,
        "percentage_change": None,
        "2025_assessments": "",
        "2026_assessments": "",
    }

    for year in [2025, 2026]:
        selected = df[
            (df["REF_AREA"] == country)
            & (df["FLOW_BREAKDOWN"] == flow)
            & (df["UNIT_MEASURE"] == "KBD")
            & (df["OBSERVATION_DATE"].dt.year == year)
            & (df["OBSERVATION_DATE"].dt.month <= 8)
        ].copy()

        numeric = selected.dropna(subset=["OBS_VALUE_NUMERIC"])

        results[f"{year}_months"] = len(numeric)

        results[f"{year}_assessments"] = assessment_summary(numeric["ASSESSMENT_CODE"])

        if not numeric.empty:
            weights = numeric["OBSERVATION_DATE"].dt.days_in_month

            results[f"{year}_value"] = (
                (numeric["OBS_VALUE_NUMERIC"] * weights).sum()
                / weights.sum()
            )

    # Only compare complete eight-month windows.
    if (
        results["2025_months"] == 8
        and results["2026_months"] == 8
        and results["2025_value"] is not None
        and results["2025_value"] != 0
    ):
        results["percentage_change"] = (
            (results["2026_value"] - results["2025_value"]) / results["2025_value"]
        ) * 100

    return results


def summarize_closing_stocks(df, country):
    results = {
        "2025_value": None,
        "2026_value": None,
        "2025_months": 0,
        "2026_months": 0,
        "percentage_change": None,
    }

    for year in [2025, 2026]:
        selected = df[
            (df["REF_AREA"] == country)
            & (df["FLOW_BREAKDOWN"] == "CLOSTLV")
            & (df["UNIT_MEASURE"] == "KBBL")
            & (df["OBSERVATION_DATE"].dt.year == year)
            & (df["OBSERVATION_DATE"].dt.month == 8)
        ]

        numeric = selected.dropna(subset=["OBS_VALUE_NUMERIC"])

        results[f"{year}_months"] = len(numeric)

        if not numeric.empty:
            results[f"{year}_value"] = numeric["OBS_VALUE_NUMERIC"].iloc[-1]

    old = results["2025_value"]
    new = results["2026_value"]

    if old is not None and new is not None and old != 0:
        results["percentage_change"] = ((new - old) / old) * 100

    return results


def summarize_stock_change(df, country):
    results = {
        "2025_value": None,
        "2026_value": None,
        "2025_months": 0,
        "2026_months": 0,
    }

    for year in [2025, 2026]:
        selected = df[
            (df["REF_AREA"] == country)
            & (df["FLOW_BREAKDOWN"] == "STOCKCH")
            & (df["UNIT_MEASURE"] == "KBBL")
            & (df["OBSERVATION_DATE"].dt.year == year)
            & (df["OBSERVATION_DATE"].dt.month <= 8)
        ]

        numeric = selected.dropna(subset=["OBS_VALUE_NUMERIC"])

        results[f"{year}_months"] = len(numeric)

        # Do not sum an incomplete eight-month period.
        if len(numeric) == 8:
            results[f"{year}_value"] = numeric["OBS_VALUE_NUMERIC"].sum()

    return results


def main():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Historical panel not found: {DATA_FILE}")

    df = pd.read_csv(
        DATA_FILE,
        parse_dates=["OBSERVATION_DATE"],
        dtype={"ASSESSMENT_CODE": str},
    )

    reports = []

    for country, country_name in COUNTRIES.items():
        country_data = df[df["REF_AREA"] == country].copy()

        for flow, indicator in RATE_INDICATORS.items():
            summary = summarize_rate(
                country_data,
                country,
                flow,
                indicator,
            )

            reports.append(
                {
                    "Country": country_name,
                    "Indicator": indicator,
                    "Unit": "KBD",
                    **summary,
                }
            )

        stock_summary = summarize_closing_stocks(
            country_data,
            country,
        )

        reports.append(
            {
                "Country": country_name,
                "Indicator": "August closing stocks",
                "Unit": "KBBL",
                **stock_summary,
                "2025_assessments": "",
                "2026_assessments": "",
            }
        )

        change_summary = summarize_stock_change(
            country_data,
            country,
        )

        reports.append(
            {
                "Country": country_name,
                "Indicator": "Cumulative Jan-Aug stock change",
                "Unit": "KBBL",
                **change_summary,
                "percentage_change": None,
                "2025_assessments": "",
                "2026_assessments": "",
            }
        )

    comparison = pd.DataFrame(reports)

    output_file = OUTPUT_DIR / "crude_oil_2025_2026_comparison.csv"

    comparison.to_csv(output_file, index=False)

    print("\n" + "=" * 90)
    print("CRUDE OIL: JAN-AUG COMPARISON")
    print("=" * 90)

    display_columns = [
        "Country",
        "Indicator",
        "2025_value",
        "2026_value",
        "2025_months",
        "2026_months",
        "percentage_change",
    ]

    print(comparison[display_columns].round(2).to_string(index=False))

    print("\nComparison saved to:")
    print(output_file)


if __name__ == "__main__":
    main()
