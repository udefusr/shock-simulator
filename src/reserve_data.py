"""Load and validate national oil reserve profiles and response events."""
from pathlib import Path
import pandas as pd

PROFILE_REQUIRED_COLUMNS = {
    "country","source_organization","stock_category","reference_date",
    "inventory_quantity","inventory_unit","capacity_quantity","capacity_unit",
    "stock_cover_days","stock_cover_basis","nominal_release_rate","release_rate_unit",
    "release_lead_time_days","release_procedure","source_url","data_quality_notes",
}
PROFILE_NUMERIC_COLUMNS = [
    "inventory_quantity","capacity_quantity","stock_cover_days",
    "nominal_release_rate","release_lead_time_days",
]
EVENT_REQUIRED_COLUMNS = {
    "event_id","country","decision_date","event_type","stock_category",
    "announced_quantity","quantity_unit","equivalent_days","obligation_reduction_days",
    "announcement_status","implementation_start","implementation_end",
    "source_organization","source_url","data_quality_notes",
}
EVENT_NUMERIC_COLUMNS = ["announced_quantity","equivalent_days","obligation_reduction_days"]


def _validate_required_columns(data, required, label):
    missing = required - set(data.columns)
    if missing:
        raise ValueError(f"{label} is missing required columns: " + ", ".join(sorted(missing)))


def _validate_numeric_columns(data, columns, label):
    cleaned = data.copy()
    for column in columns:
        original = cleaned[column]
        parsed = pd.to_numeric(original, errors="coerce")
        invalid = original.notna() & original.astype(str).str.strip().ne("") & parsed.isna()
        if invalid.any():
            raise ValueError(f"{label} {column} contains a non-numeric value.")
        if parsed.dropna().lt(0).any():
            raise ValueError(f"{label} {column} cannot be negative.")
        cleaned[column] = parsed
    return cleaned


def _validate_http_urls(data, label):
    urls = data["source_url"].astype("string")
    if urls.isna().any() or urls.str.strip().eq("").any():
        raise ValueError(f"{label} source_url must be populated for every record.")
    if not urls.str.startswith(("https://", "http://"), na=False).all():
        raise ValueError(f"Every {label} source_url must be an HTTP(S) URL.")


def validate_reserve_profiles(data):
    """Validate reserve profiles. Blank numeric values mean unknown, not zero."""
    _validate_required_columns(data, PROFILE_REQUIRED_COLUMNS, "Reserve profile")
    cleaned = _validate_numeric_columns(data, PROFILE_NUMERIC_COLUMNS, "Reserve profile")
    for column in ("country","source_organization","stock_category","inventory_unit"):
        if cleaned[column].isna().any() or cleaned[column].astype(str).str.strip().eq("").any():
            raise ValueError(f"Reserve profile {column} must be populated for every record.")
    _validate_http_urls(cleaned, "Reserve profile")
    duplicated = cleaned.duplicated(
        subset=["country","stock_category","reference_date"], keep=False
    )
    if duplicated.any():
        raise ValueError("Duplicate reserve profile keys found for country, category, and reference date.")
    comparable = cleaned["capacity_quantity"].notna() & cleaned["inventory_quantity"].notna()
    if (cleaned.loc[comparable,"inventory_quantity"] > cleaned.loc[comparable,"capacity_quantity"]).any():
        raise ValueError("Inventory quantity cannot exceed reported capacity.")
    return cleaned


def validate_reserve_response_events(data):
    """Validate announced reserve releases and stockholding-policy events."""
    _validate_required_columns(data, EVENT_REQUIRED_COLUMNS, "Reserve response event")
    cleaned = _validate_numeric_columns(data, EVENT_NUMERIC_COLUMNS, "Reserve response event")
    for column in (
        "event_id","country","decision_date","event_type","stock_category",
        "announcement_status","source_organization",
    ):
        if cleaned[column].isna().any() or cleaned[column].astype(str).str.strip().eq("").any():
            raise ValueError(f"Reserve response event {column} must be populated.")
    if cleaned["event_id"].duplicated().any():
        raise ValueError("Duplicate reserve response event_id values found.")
    _validate_http_urls(cleaned, "Reserve response event")
    for column in ("decision_date","implementation_start","implementation_end"):
        original = cleaned[column]
        parsed = pd.to_datetime(original, errors="coerce", format="%Y-%m-%d")
        invalid = original.notna() & original.astype(str).str.strip().ne("") & parsed.isna()
        if invalid.any():
            raise ValueError(f"Reserve response event {column} contains an invalid date.")
        cleaned[column] = parsed
    dated = cleaned["implementation_start"].notna() & cleaned["implementation_end"].notna()
    if (cleaned.loc[dated,"implementation_end"] < cleaned.loc[dated,"implementation_start"]).any():
        raise ValueError("Implementation end date cannot precede start date.")
    return cleaned


def load_reserve_profiles(path=None):
    """Load and validate the initial reserve profile CSV."""
    if path is None:
        path = Path(__file__).resolve().parents[1] / "data" / "processed" / "reserve_profiles_initial.csv"
    return validate_reserve_profiles(pd.read_csv(path, dtype={"reference_date":"string"}))


def load_reserve_response_events(path=None):
    """Load and validate the reserve response event CSV."""
    if path is None:
        path = Path(__file__).resolve().parents[1] / "data" / "raw" / "other" / "reserve_response_events.csv"
    return validate_reserve_response_events(pd.read_csv(path))
