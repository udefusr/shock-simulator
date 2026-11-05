from pathlib import Path

import pandas as pd


JODI_COLUMNS = [
    "REF_AREA",
    "TIME_PERIOD",
    "ENERGY_PRODUCT",
    "FLOW_BREAKDOWN",
    "UNIT_MEASURE",
    "OBS_VALUE",
    "ASSESSMENT_CODE",
]

MISSING_VALUE_CODES = {
    "-": "not_reported",
    "..": "conversion_factor_unavailable",
    "x": "unit_not_applicable",
    "N/A": "not_applicable",
}


def load_jodi_files(data_directory):
    """
    Load and standardize JODI extended CSV files.

    Original observation values are preserved in OBS_VALUE.
    Numeric values and missing-value classifications are
    added in separate columns.
    """

    data_directory = Path(data_directory)

    if not data_directory.exists():
        raise FileNotFoundError(f"Directory not found: {data_directory}")

    csv_files = sorted(data_directory.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError("No JODI CSV files found.")

    frames = []

    for path in csv_files:
        df = pd.read_csv(
            path,
            encoding="utf-8-sig",
            dtype=str,
            keep_default_na=False,
        )

        missing_columns = set(JODI_COLUMNS) - set(df.columns)

        if missing_columns:
            raise ValueError(
                f"{path.name} is missing columns: {sorted(missing_columns)}"
            )

        df = df[JODI_COLUMNS].copy()

        # Preserve the original observation text.
        df["OBS_VALUE"] = df["OBS_VALUE"].str.strip()

        # Convert only genuinely numeric observations.
        df["OBS_VALUE_NUMERIC"] = pd.to_numeric(
            df["OBS_VALUE"],
            errors="coerce",
        )

        # Classify missing-value markers.
        df["OBS_VALUE_STATUS"] = (
            df["OBS_VALUE"].map(MISSING_VALUE_CODES).fillna("reported")
        )

        # Parse the monthly observation date.
        df["OBSERVATION_DATE"] = pd.to_datetime(
            df["TIME_PERIOD"] + "-01",
            format="%Y-%m-%d",
            errors="raise",
        )

        # Retain the original source filename.
        df["SOURCE_FILE"] = path.name

        frames.append(df)

    combined = pd.concat(
        frames,
        ignore_index=True,
    )

    return combined
