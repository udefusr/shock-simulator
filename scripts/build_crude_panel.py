from pathlib import Path

import pandas as pd

from src.data_loader import load_jodi_files


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "raw" / "jodi"
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
    "INDPROD": ("Production", "KBD"),
    "TOTIMPSB": ("Imports", "KBD"),
    "TOTEXPSB": ("Exports", "KBD"),
    "REFINOBS": ("Refinery intake", "KBD"),
    "DIRECUSE": ("Direct use", "KBD"),
    "CLOSTLV": ("Closing stocks", "KBBL"),
    "STOCKCH": ("Stock change", "KBBL"),
}


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading JODI datasets...")

    df = load_jodi_files(DATA_DIR)

    print(f"Loaded {len(df):,} source observations.")

    # Select crude oil and our initial country panel.
    panel = df[
        (df["ENERGY_PRODUCT"] == "CRUDEOIL") & (df["REF_AREA"].isin(COUNTRIES))
    ].copy()

    # Keep only the seven selected indicators and their
    # appropriate physical measurement units.
    indicator_names = {flow: name for flow, (name, unit) in INDICATORS.items()}

    expected_units = {flow: unit for flow, (name, unit) in INDICATORS.items()}

    panel = panel[panel["FLOW_BREAKDOWN"].isin(INDICATORS)].copy()

    panel["EXPECTED_UNIT"] = panel["FLOW_BREAKDOWN"].map(expected_units)

    panel = panel[panel["UNIT_MEASURE"] == panel["EXPECTED_UNIT"]].copy()

    panel["COUNTRY_NAME"] = panel["REF_AREA"].map(COUNTRIES)

    panel["INDICATOR"] = panel["FLOW_BREAKDOWN"].map(indicator_names)

    # Convert assessment codes to strings to preserve
    # their categorical meaning.
    panel["ASSESSMENT_CODE"] = panel["ASSESSMENT_CODE"].astype(str)

    panel = panel.sort_values(
        [
            "REF_AREA",
            "OBSERVATION_DATE",
            "FLOW_BREAKDOWN",
            "SOURCE_FILE",
        ]
    ).reset_index(drop=True)

    key_columns = [
        "REF_AREA",
        "TIME_PERIOD",
        "ENERGY_PRODUCT",
        "FLOW_BREAKDOWN",
        "UNIT_MEASURE",
    ]

    duplicates = panel.duplicated(
        subset=key_columns,
        keep=False,
    )

    if duplicates.any():
        raise ValueError(f"Found {duplicates.sum()} duplicate observation rows.")

    # Preserve both original and standardized fields.
    output_columns = [
        "REF_AREA",
        "COUNTRY_NAME",
        "TIME_PERIOD",
        "OBSERVATION_DATE",
        "ENERGY_PRODUCT",
        "FLOW_BREAKDOWN",
        "INDICATOR",
        "UNIT_MEASURE",
        "OBS_VALUE",
        "OBS_VALUE_NUMERIC",
        "OBS_VALUE_STATUS",
        "ASSESSMENT_CODE",
        "SOURCE_FILE",
    ]

    panel = panel[output_columns]

    output_file = OUTPUT_DIR / "crude_oil_historical_panel.csv"

    panel.to_csv(
        output_file,
        index=False,
    )

    # Build a separate coverage summary.
    coverage = (
        panel.groupby(
            [
                "SOURCE_FILE",
                "REF_AREA",
                "COUNTRY_NAME",
                "INDICATOR",
                "UNIT_MEASURE",
            ],
            dropna=False,
        )
        .agg(
            total_observations=("OBS_VALUE", "size"),
            numeric_observations=("OBS_VALUE_NUMERIC", "count"),
        )
        .reset_index()
    )

    coverage["missing_observations"] = (
        coverage["total_observations"] - coverage["numeric_observations"]
    )

    coverage_file = OUTPUT_DIR / "crude_oil_panel_coverage.csv"

    coverage.to_csv(
        coverage_file,
        index=False,
    )

    print("\n" + "=" * 70)
    print("CRUDE OIL HISTORICAL PANEL")
    print("=" * 70)

    print(f"Countries: {panel['REF_AREA'].nunique()}")
    print(f"Observations: {len(panel):,}")
    print(
        "Numeric observations:",
        f"{panel['OBS_VALUE_NUMERIC'].count():,}",
    )
    print(
        "Missing observations:",
        f"{panel['OBS_VALUE_NUMERIC'].isna().sum():,}",
    )

    print("\nOBSERVATION COUNTS BY COUNTRY AND YEAR:")

    summary = panel.pivot_table(
        index="COUNTRY_NAME",
        columns=panel["OBSERVATION_DATE"].dt.year,
        values="OBS_VALUE_NUMERIC",
        aggfunc="count",
        fill_value=0,
    )

    print(summary.to_string())

    print("\nFiles created:")
    print(output_file)
    print(coverage_file)


if __name__ == "__main__":
    main()
