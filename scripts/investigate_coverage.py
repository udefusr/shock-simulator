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
    "Production": ("INDPROD", "KBD"),
    "Imports": ("TOTIMPSB", "KBD"),
    "Exports": ("TOTEXPSB", "KBD"),
    "Refinery intake": ("REFINOBS", "KBD"),
    "Direct use": ("DIRECUSE", "KBD"),
    "Closing stocks": ("CLOSTLV", "KBBL"),
    "Stock change": ("STOCKCH", "KBBL"),
}


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = load_jodi_files(DATA_DIR)

    df = df[
        (df["ENERGY_PRODUCT"] == "CRUDEOIL") & (df["REF_AREA"].isin(COUNTRIES))
    ].copy()

    reports = []

    for source_file in sorted(df["SOURCE_FILE"].unique()):
        file_data = df[df["SOURCE_FILE"] == source_file]

        print("\n" + "=" * 85)
        print(source_file)
        print("=" * 85)

        for country in COUNTRIES:
            country_data = file_data[file_data["REF_AREA"] == country]

            results = []

            for indicator, (flow, unit) in INDICATORS.items():
                selected = country_data[
                    (country_data["FLOW_BREAKDOWN"] == flow)
                    & (country_data["UNIT_MEASURE"] == unit)
                ]

                total = len(selected)
                numeric = int(selected["OBS_VALUE_NUMERIC"].count())

                results.append(f"{indicator}: {numeric}/{total}")

                reports.append(
                    {
                        "Source file": source_file,
                        "Country": country,
                        "Indicator": indicator,
                        "Unit": unit,
                        "Available observations": numeric,
                        "Total observations": total,
                    }
                )

            print(f"{country:>3} | " + " | ".join(results))

    report_df = pd.DataFrame(reports)

    output_file = OUTPUT_DIR / "jodi_crude_coverage_clean.csv"
    report_df.to_csv(output_file, index=False)

    print("\nCoverage report saved to:")
    print(output_file)


if __name__ == "__main__":
    main()
