"""Load and validate the project's initial national oil reserve profiles."""

from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {
    "country",
    "source_organization",
    "stock_category",
    "reference_date",
    "inventory_quantity",
    "inventory_unit",
    "capacity_quantity",
    "capacity_unit",
    "stock_cover_days",
    "stock_cover_basis",
    "nominal_release_rate",
    "release_rate_unit",
    "release_lead_time_days",
    "release_procedure",
    "source_url",
    "data_quality_notes",
}

NUMERIC_COLUMNS = [
    "inventory_quantity",
    "capacity_quantity",
    "stock_cover_days",
    "nominal_release_rate",
    "release_lead_time_days",
]


def validate_reserve_profiles(data: pd.DataFrame) -> pd.DataFrame:
    """Validate reserve profile structure and numeric fields.

    Blank numeric values are allowed and mean unknown/not reported, not zero.
    Returns a copy with numeric columns parsed as floats.
    """

    missing_columns = REQUIRED_COLUMNS - set(data.columns)
    if missing_columns:
        raise ValueError(
            "Reserve profile is missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    cleaned = data.copy()

    for column in NUMERIC_COLUMNS:
        original = cleaned[column]
        parsed = pd.to_numeric(original, errors="coerce")

        invalid_text = (
            original.notna()
            & original.astype(str).str.strip().ne("")
            & parsed.isna()
        )
        if invalid_text.any():
            raise ValueError(f"{column} contains a non-numeric value.")

        if parsed.dropna().lt(0).any():
            raise ValueError(f"{column} cannot contain negative values.")

        cleaned[column] = parsed

    for column in (
        "country",
        "source_organization",
        "stock_category",
        "inventory_unit",
        "source_url",
    ):
        if (
            cleaned[column].isna().any()
            or cleaned[column].astype(str).str.strip().eq("").any()
        ):
            raise ValueError(
                f"{column} must be populated for every record."
            )

    if not cleaned["source_url"].astype(str).str.startswith(
        ("https://", "http://")
    ).all():
        raise ValueError("Every source_url must be an HTTP(S) URL.")

    duplicate_keys = cleaned.duplicated(
        subset=["country", "stock_category", "reference_date"],
        keep=False,
    )
    if duplicate_keys.any():
        raise ValueError(
            "Duplicate reserve profile keys found for country, category, "
            "and reference date."
        )

    comparable = (
        cleaned["capacity_quantity"].notna()
        & cleaned["inventory_quantity"].notna()
    )
    exceeds_capacity = (
        cleaned.loc[comparable, "inventory_quantity"]
        > cleaned.loc[comparable, "capacity_quantity"]
    )
    if exceeds_capacity.any():
        raise ValueError(
            "Inventory quantity cannot exceed reported capacity."
        )

    return cleaned


def load_reserve_profiles(path=None) -> pd.DataFrame:
    """Load the initial reserve profile CSV from the repository."""

    if path is None:
        path = (
            Path(__file__).resolve().parents[1]
            / "data"
            / "processed"
            / "reserve_profiles_initial.csv"
        )

    data = pd.read_csv(path, dtype={"reference_date": "string"})
    return validate_reserve_profiles(data)
