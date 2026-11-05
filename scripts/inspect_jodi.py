from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "raw" / "jodi"

DIMENSIONS = [
    "REF_AREA",
    "ENERGY_PRODUCT",
    "FLOW_BREAKDOWN",
    "UNIT_MEASURE",
]

KEY_COLUMNS = [
    "REF_AREA",
    "TIME_PERIOD",
    "ENERGY_PRODUCT",
    "FLOW_BREAKDOWN",
    "UNIT_MEASURE",
]


def inspect_file(path):
    print("\n" + "=" * 75)
    print(f"FILE: {path.name}")
    print("=" * 75)

    df = pd.read_csv(
        path,
        encoding="utf-8-sig",
        dtype=str,
        keep_default_na=False,
    )

    print(f"Total observations: {len(df):,}")
    print(f"Date range: {df['TIME_PERIOD'].min()} to {df['TIME_PERIOD'].max()}")

    for column in DIMENSIONS:
        values = sorted(df[column].unique())

        print(f"\n{column}: {len(values)} unique values")

        for value in values:
            print(f"  {value}")

    print("\nASSESSMENT CODE COUNTS:")
    print(df["ASSESSMENT_CODE"].value_counts(dropna=False).to_string())

    numeric_values = pd.to_numeric(
        df["OBS_VALUE"],
        errors="coerce",
    )

    non_numeric = df.loc[
        numeric_values.isna(),
        "OBS_VALUE",
    ].value_counts()

    print("\nNON-NUMERIC OBS_VALUE ENTRIES:")

    if non_numeric.empty:
        print("  None")
    else:
        print(non_numeric.to_string())

    print("\nDUPLICATE OBSERVATION KEYS:")

    duplicates = df.duplicated(
        subset=KEY_COLUMNS,
        keep=False,
    )

    print(f"  {duplicates.sum():,} rows involved in duplicates")

    if duplicates.any():
        print(df.loc[duplicates, KEY_COLUMNS].head(10).to_string(index=False))

    print("\nTOP 15 REPORTING ECONOMIES:")

    print(df["REF_AREA"].value_counts().head(15).to_string())


def main():
    if not DATA_DIR.exists():
        raise FileNotFoundError(f"Dataset directory not found: {DATA_DIR}")

    csv_files = sorted(DATA_DIR.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError("No CSV files found in data/raw/jodi/")

    for path in csv_files:
        inspect_file(path)

    print("\n" + "=" * 75)
    print("DATASET INSPECTION COMPLETE")
    print("=" * 75)


if __name__ == "__main__":
    main()
