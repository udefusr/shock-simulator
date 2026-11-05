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
    "CLOSTLV": ("Closing stocks", "KBBL"),
    "STOCKCH": ("Stock change", "KBBL"),
}


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = load_jodi_files(DATA_DIR)

    df = df[
        (df["ENERGY_PRODUCT"] == "CRUDEOIL")
        & (df["REF_AREA"].isin(COUNTRIES))
        & (df["FLOW_BREAKDOWN"].isin(INDICATORS))
    ].copy()

    df["EXPECTED_UNIT"] = df["FLOW_BREAKDOWN"].map(
        {flow: unit for flow, (name, unit) in INDICATORS.items()}
    )

    df = df[df["UNIT_MEASURE"] == df["EXPECTED_UNIT"]].copy()

    df["COUNTRY_NAME"] = df["REF_AREA"].map(COUNTRIES)

    df["INDICATOR"] = df["FLOW_BREAKDOWN"].map(
        {flow: name for flow, (name, unit) in INDICATORS.items()}
    )

    # Preserve monthly observations, missing values and
    # assessment codes. Do not interpolate or fill gaps.
    output_columns = [
        "REF_AREA",
        "COUNTRY_NAME",
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

    df = df[output_columns].sort_values(
        ["REF_AREA", "OBSERVATION_DATE", "FLOW_BREAKDOWN"]
    )

    output_file = OUTPUT_DIR / "crude_oil_monthly_profiles.csv"

    df.to_csv(output_file, index=False)

    # Print a focused set of monthly series.
    focus = [
        ("SA", "INDPROD"),
        ("SA", "TOTEXPSB"),
        ("KW", "INDPROD"),
        ("KW", "TOTEXPSB"),
        ("CN", "TOTIMPSB"),
        ("CN", "REFINOBS"),
        ("JP", "TOTIMPSB"),
        ("JP", "REFINOBS"),
        ("KR", "TOTIMPSB"),
        ("KR", "REFINOBS"),
        ("DE", "TOTIMPSB"),
        ("DE", "REFINOBS"),
    ]

    selected = df[
        [
            (country, flow) in focus
            for country, flow in zip(
                df["REF_AREA"],
                df["FLOW_BREAKDOWN"],
            )
        ]
    ].copy()

    pivot = selected.pivot(
        index="OBSERVATION_DATE",
        columns=["REF_AREA", "FLOW_BREAKDOWN"],
        values="OBS_VALUE_NUMERIC",
    )

    pivot.columns = [
        f"{COUNTRIES[country]} - {INDICATORS[flow][0]}"
        for country, flow in pivot.columns
    ]

    print("\n" + "=" * 100)
    print("MONTHLY CRUDE OIL PROFILES (KBD)")
    print("=" * 100)

    print(pivot.round(1).to_string(na_rep="--"))

    print("\nFull monthly dataset saved to:")
    print(output_file)

    print(f"\nTotal selected observations: {len(df):,}")
    print(
        "Missing numeric observations:",
        df["OBS_VALUE_NUMERIC"].isna().sum(),
    )


if __name__ == "__main__":
    main()
