from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "data" / "raw" / "other"

EIA_URL = "https://www.eia.gov/outlooks/steo/report/energysecurity/article.php"

OCTOBER_REPORT_URL = "https://www.eia.gov/outlooks/steo/pdf/steo_text.pdf"

QUARTERS = [
    "2025-Q1",
    "2025-Q2",
    "2025-Q3",
    "2025-Q4",
    "2026-Q1",
    "2026-Q2",
]

ROUTE_DATA = {
    "Strait of Hormuz": [20.9, 21.0, 21.3, 21.6, 14.9, 4.9],
    "Strait of Malacca": [22.3, 23.8, 23.4, 24.9, 21.3, 16.6],
    "Suez Canal and SUMED Pipeline": [4.6, 5.1, 5.6, 5.9, 5.7, 5.8],
    "Bab el-Mandeb": [3.9, 4.5, 4.6, 5.4, 5.6, 8.1],
    "Danish Straits": [5.0, 4.8, 4.9, 5.0, 4.9, 4.7],
    "Turkish Straits": [3.8, 3.7, 3.7, 3.7, 3.3, 4.1],
    "Panama Canal": [2.8, 2.5, 2.8, 2.8, 2.9, 3.2],
    "Cape of Good Hope": [9.0, 9.3, 9.0, 9.9, 8.2, 9.4],
}

SHUTIN_DATA = [
    {
        "Country": "Kuwait",
        "Feb_2026_production_kbd": 2560,
        "Mar_Jul_average_shutins_kbd": 1466,
        "Aug_2026_shutins_kbd": 630,
        "Sep_2026_shutins_kbd": 930,
    },
    {
        "Country": "UAE",
        "Feb_2026_production_kbd": 3600,
        "Mar_Jul_average_shutins_kbd": 740,
        "Aug_2026_shutins_kbd": 0,
        "Sep_2026_shutins_kbd": 0,
    },
    {
        "Country": "Iran",
        "Feb_2026_production_kbd": 3390,
        "Mar_Jul_average_shutins_kbd": 424,
        "Aug_2026_shutins_kbd": 900,
        "Sep_2026_shutins_kbd": 1200,
    },
    {
        "Country": "Iraq",
        "Feb_2026_production_kbd": 4400,
        "Mar_Jul_average_shutins_kbd": 2646,
        "Aug_2026_shutins_kbd": 780,
        "Sep_2026_shutins_kbd": 760,
    },
    {
        "Country": "Qatar",
        "Feb_2026_production_kbd": 557,
        "Mar_Jul_average_shutins_kbd": 350,
        "Aug_2026_shutins_kbd": 100,
        "Sep_2026_shutins_kbd": 100,
    },
    {
        "Country": "Bahrain",
        "Feb_2026_production_kbd": 193,
        "Mar_Jul_average_shutins_kbd": 136,
        "Aug_2026_shutins_kbd": 80,
        "Sep_2026_shutins_kbd": 80,
    },
    {
        "Country": "Saudi Arabia",
        "Feb_2026_production_kbd": 10500,
        "Mar_Jul_average_shutins_kbd": 2750,
        "Aug_2026_shutins_kbd": 3270,
        "Sep_2026_shutins_kbd": 1700,
    },
]


def build_route_dataset():
    rows = []

    for route, values in ROUTE_DATA.items():
        for quarter, value in zip(QUARTERS, values):
            rows.append(
                {
                    "Quarter": quarter,
                    "Route": route,
                    "Flow_million_barrels_per_day": value,
                    "Data_status": "EIA estimate",
                    "Source_report": "EIA Global Energy Security Data, August 2026",
                    "Publication_date": "2026-08-12",
                    "Source_URL": EIA_URL,
                }
            )

    return pd.DataFrame(rows)


def build_shutin_dataset():
    rows = []

    for record in SHUTIN_DATA:
        rows.append(
            {
                **record,
                "Q4_2026_forecast_shutins_kbd": None,
                "Q1_2027_forecast_shutins_kbd": None,
                "Data_status": "EIA estimate",
                "Source_report": "EIA Short-Term Energy Outlook, October 2026",
                "Publication_date": "2026-10-06",
                "Source_URL": OCTOBER_REPORT_URL,
            }
        )

    # EIA publishes forecasts only for the aggregate total.
    rows.append(
        {
            "Country": "Total listed producers",
            "Feb_2026_production_kbd": 25200,
            "Mar_Jul_average_shutins_kbd": 8512,
            "Aug_2026_shutins_kbd": 5760,
            "Sep_2026_shutins_kbd": 4770,
            "Q4_2026_forecast_shutins_kbd": 4470,
            "Q1_2027_forecast_shutins_kbd": 2683,
            "Data_status": "EIA estimate and forecast",
            "Source_report": "EIA Short-Term Energy Outlook, October 2026",
            "Publication_date": "2026-10-06",
            "Source_URL": OCTOBER_REPORT_URL,
        }
    )

    return pd.DataFrame(rows)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    routes = build_route_dataset()
    shutins = build_shutin_dataset()

    route_file = OUTPUT_DIR / "eia_chokepoint_flows.csv"
    shutin_file = OUTPUT_DIR / "eia_production_shutins.csv"

    routes.to_csv(route_file, index=False)
    shutins.to_csv(shutin_file, index=False)

    print("EIA reference datasets created.")
    print(f"\nChokepoint observations: {len(routes)}")
    print(f"Production shut-in records: {len(shutins)}")

    print(f"\n{route_file}")
    print(shutin_file)

    print(
        "\nNote: These are manually transcribed report tables, "
        "not original EIA bulk downloads."
    )


if __name__ == "__main__":
    main()
