from pathlib import Path
import pandas as pd

from src.data_loader import load_jodi_files


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "raw" / "jodi"
OUTPUT_DIR = ROOT / "data" / "processed"

COUNTRIES = [
    "SA",
    "AE",
    "IQ",
    "KW",
    "QA",
    "OM",
    "IR",
    "CN",
    "IN",
    "JP",
    "KR",
    "DE",
    "BD",
]

INDICATORS = {
    "Production (KBD)": ("INDPROD", "KBD"),
    "Imports (KBD)": ("TOTIMPSB", "KBD"),
    "Exports (KBD)": ("TOTEXPSB", "KBD"),
    "Closing stocks (KBBL)": ("CLOSTLV", "KBBL"),
    "Stock change (KBBL)": ("STOCKCH", "KBBL"),
}


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading JODI datasets...")

    df = load_jodi_files(DATA_DIR)

    print(f"Total loaded observations: {len(df):,}")

    # Focus on crude oil only.
    df = df[df["ENERGY_PRODUCT"] == "CRUDEOIL"].copy()

    df = df[df["REF_AREA"].isin(COUNTRIES)].copy()

    reports = []

    for source_file in sorted(df["SOURCE_FILE"].unique()):
        file_data = df[df["SOURCE_FILE"] == source_file]

        print("\n" + "=" * 70)
        print(source_file)
        print("=" * 70)

        rows = []

        for country in COUNTRIES:
            country_data = file_data[file_data["REF_AREA"] == country]

            row = {"Country code": country}

            for indicator, (flow, unit) in INDICATORS.items():
                selected = country_data[
                    (country_data["FLOW_BREAKDOWN"] == flow)
                    & (country_data["UNIT_MEASURE"] == unit)
                ]

                numeric_count = selected["OBS_VALUE_NUMERIC"].count()

                row[indicator] = int(numeric_count)

                reports.append(
                    {
                        "Source file": source_file,
                        "Country": country,
                        "Indicator": indicator,
                        "Total observations": len(selected),
                        "Numeric observations": int(numeric_count),
                        "Missing observations": (len(selected) - int(numeric_count)),
                    }
                )

            rows.append(row)

        coverage = pd.DataFrame(rows)

        print(coverage.to_string(index=False))

        print("\nAssessment codes in selected observations:")

        selected_file = file_data[
            file_data["FLOW_BREAKDOWN"].isin(
                [flow for flow, unit in INDICATORS.values()]
            )
        ]

        print(selected_file["ASSESSMENT_CODE"].value_counts().sort_index().to_string())

    report_df = pd.DataFrame(reports)

    output_file = OUTPUT_DIR / "jodi_crude_coverage.csv"

    report_df.to_csv(output_file, index=False)

    print("\n" + "=" * 70)
    print("PROFILE COMPLETE")
    print(f"Coverage report saved to: {output_file}")
    print("=" * 70)


if __name__ == "__main__":
    main()
