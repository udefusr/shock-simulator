from pathlib import Path

import pandas as pd


# --------------------------------------------------
# Configuration
# --------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]

JODI_FILE = ROOT / "data" / "processed" / "crude_oil_historical_panel.csv"

EIA_FILE = ROOT / "data" / "raw" / "other" / "eia_production_shutins.csv"

OUTPUT_DIR = ROOT / "data" / "processed"

COUNTRIES = {
    "Saudi Arabia": "SA",
    "Kuwait": "KW",
}


# --------------------------------------------------
# Data-processing functions
# --------------------------------------------------


def weighted_average(data):
    """
    Calculate a calendar-day-weighted average
    of monthly daily flow rates.

    The input values are in KBD.
    """

    if data.empty:
        return None

    weights = data["OBSERVATION_DATE"].dt.days_in_month

    return (data["OBS_VALUE_NUMERIC"] * weights).sum() / weights.sum()


def get_jodi_production(
    df,
    country_code,
    start_date,
    end_date,
):
    """
    Extract crude oil production observations
    for one country and date range.
    """

    selected = df[
        (df["REF_AREA"] == country_code)
        & (df["ENERGY_PRODUCT"] == "CRUDEOIL")
        & (df["FLOW_BREAKDOWN"] == "INDPROD")
        & (df["UNIT_MEASURE"] == "KBD")
        & (df["OBSERVATION_DATE"] >= pd.Timestamp(start_date))
        & (df["OBSERVATION_DATE"] <= pd.Timestamp(end_date))
    ].copy()

    return selected.dropna(subset=["OBS_VALUE_NUMERIC"])


def get_single_month_value(data, month):
    """
    Retrieve a single monthly production value.

    Returns None if the observation is unavailable.
    """

    selected = data[data["OBSERVATION_DATE"].dt.month == month]

    if selected.empty:
        return None

    return float(selected["OBS_VALUE_NUMERIC"].iloc[0])


# --------------------------------------------------
# Cross-source comparison
# --------------------------------------------------


def compare_country(
    jodi,
    eia,
    country,
    country_code,
):
    """
    Compare JODI observed production with
    EIA estimated production shut-ins.

    Periods:
        Baseline: January-February 2026
        Event: March-July 2026
        Seasonal reference: March-July 2025

    All production quantities are in KBD.
    """

    eia_row = eia[eia["Country"] == country]

    if len(eia_row) != 1:
        raise ValueError(f"Expected exactly one EIA record for {country}.")

    eia_row = eia_row.iloc[0]

    # ----------------------------------------------
    # Extract JODI observations
    # ----------------------------------------------

    baseline = get_jodi_production(
        jodi,
        country_code,
        "2026-01-01",
        "2026-02-28",
    )

    event = get_jodi_production(
        jodi,
        country_code,
        "2026-03-01",
        "2026-07-31",
    )

    year_ago = get_jodi_production(
        jodi,
        country_code,
        "2025-03-01",
        "2025-07-31",
    )

    # ----------------------------------------------
    # Calculate weighted averages
    # ----------------------------------------------

    baseline_average = weighted_average(baseline)
    event_average = weighted_average(event)
    year_ago_average = weighted_average(year_ago)

    # February 2026 production observation.
    feb_value = get_single_month_value(
        baseline,
        2,
    )

    # ----------------------------------------------
    # Extract EIA estimates
    # ----------------------------------------------

    eia_feb = float(eia_row["Feb_2026_production_kbd"])

    eia_shutins = float(eia_row["Mar_Jul_average_shutins_kbd"])

    # EIA-implied production after estimated shut-ins.
    eia_implied_production = eia_feb - eia_shutins

    # ----------------------------------------------
    # Calculate production differences
    # ----------------------------------------------

    # Difference between the February baselines.
    feb_baseline_difference = feb_value - eia_feb if feb_value is not None else None

    # Decline relative to the January-February average.
    observed_decline = (
        baseline_average - event_average
        if (baseline_average is not None and event_average is not None)
        else None
    )

    # Decline relative to February specifically.
    february_to_event_decline = (
        feb_value - event_average
        if (feb_value is not None and event_average is not None)
        else None
    )

    # Seasonal year-on-year production difference.
    yoy_decline = (
        year_ago_average - event_average
        if (year_ago_average is not None and event_average is not None)
        else None
    )

    # ----------------------------------------------
    # Cross-source reconciliation
    # ----------------------------------------------

    jodi_eia_reconciliation_gap = (
        event_average - eia_implied_production if event_average is not None else None
    )

    observed_decline_minus_eia_shutins = (
        observed_decline - eia_shutins if observed_decline is not None else None
    )

    february_aligned_difference = (
        february_to_event_decline - eia_shutins
        if february_to_event_decline is not None
        else None
    )

    # ----------------------------------------------
    # Return comparison results
    # ----------------------------------------------

    return {
        "Country": country,
        # JODI data coverage.
        "JODI_baseline_months": baseline["OBSERVATION_DATE"].nunique(),
        "JODI_event_months": event["OBSERVATION_DATE"].nunique(),
        "JODI_2025_event_months": year_ago["OBSERVATION_DATE"].nunique(),
        # February baseline comparison.
        "JODI_Feb_2026_production_KBD": feb_value,
        "EIA_Feb_2026_baseline_KBD": eia_feb,
        "Feb_baseline_difference_KBD": (feb_baseline_difference),
        # JODI observed production.
        "JODI_Jan_Feb_average_KBD": baseline_average,
        "JODI_Mar_Jul_average_KBD": event_average,
        "JODI_2025_Mar_Jul_average_KBD": (year_ago_average),
        # Production decline calculations.
        "JODI_apparent_decline_KBD": observed_decline,
        "JODI_Feb_to_Mar_Jul_decline_KBD": (february_to_event_decline),
        "JODI_year_on_year_decline_KBD": yoy_decline,
        # EIA estimates.
        "EIA_Mar_Jul_average_shutins_KBD": (eia_shutins),
        "EIA_implied_Mar_Jul_production_KBD": (eia_implied_production),
        # Cross-source comparisons.
        "JODI_minus_EIA_implied_production_KBD": (jodi_eia_reconciliation_gap),
        "JODI_decline_minus_EIA_shutins_KBD": (observed_decline_minus_eia_shutins),
        "JODI_Feb_aligned_decline_minus_EIA_shutins_KBD": (february_aligned_difference),
    }


# --------------------------------------------------
# Main execution
# --------------------------------------------------


def main():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not JODI_FILE.exists():
        raise FileNotFoundError(f"JODI dataset not found: {JODI_FILE}")

    if not EIA_FILE.exists():
        raise FileNotFoundError(f"EIA dataset not found: {EIA_FILE}")

    print("Loading JODI dataset...")

    jodi = pd.read_csv(
        JODI_FILE,
        parse_dates=["OBSERVATION_DATE"],
    )

    print("Loading EIA dataset...")

    eia = pd.read_csv(EIA_FILE)

    required_eia_columns = [
        "Country",
        "Feb_2026_production_kbd",
        "Mar_Jul_average_shutins_kbd",
    ]

    missing_columns = set(required_eia_columns) - set(eia.columns)

    if missing_columns:
        raise ValueError(f"EIA dataset is missing columns: {sorted(missing_columns)}")

    # Run comparisons.
    results = []

    for country, country_code in COUNTRIES.items():
        result = compare_country(
            jodi,
            eia,
            country,
            country_code,
        )

        results.append(result)

    comparison = pd.DataFrame(results)

    # Save results.
    output_file = OUTPUT_DIR / "eia_jodi_production_comparison.csv"

    comparison.to_csv(
        output_file,
        index=False,
    )

    # ----------------------------------------------
    # Display results
    # ----------------------------------------------

    display_columns = [
        "Country",
        "JODI_baseline_months",
        "JODI_event_months",
        "JODI_2025_event_months",
        "JODI_Feb_2026_production_KBD",
        "EIA_Feb_2026_baseline_KBD",
        "Feb_baseline_difference_KBD",
        "JODI_Jan_Feb_average_KBD",
        "JODI_Mar_Jul_average_KBD",
        "JODI_apparent_decline_KBD",
        "JODI_Feb_to_Mar_Jul_decline_KBD",
        "JODI_2025_Mar_Jul_average_KBD",
        "JODI_year_on_year_decline_KBD",
        "EIA_Mar_Jul_average_shutins_KBD",
        "EIA_implied_Mar_Jul_production_KBD",
        "JODI_minus_EIA_implied_production_KBD",
        "JODI_decline_minus_EIA_shutins_KBD",
        "JODI_Feb_aligned_decline_minus_EIA_shutins_KBD",
    ]

    print("\n" + "=" * 100)
    print("EIA AND JODI PRODUCTION COMPARISON")
    print("=" * 100)

    print(comparison[display_columns].round(2).to_string(index=False))

    print("\nSaved to:")
    print(output_file)

    print(
        "\nInterpretation:\n"
        "JODI production changes and EIA estimated shut-ins "
        "are separate measurements. Their differences are "
        "not automatically estimation errors.\n"
        "All production quantities are in thousand barrels "
        "per day (KBD)."
    )


if __name__ == "__main__":
    main()
