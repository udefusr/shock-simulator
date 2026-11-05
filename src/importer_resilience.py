"""Importer-country oil resilience scenario model.

The baseline observations are estimated crude-oil and condensate flows via
Hormuz, not total national imports. Alternative sourcing and stock-buffer
inputs are analyst assumptions; this module does not infer cargo origins,
pipeline eligibility, or national stock availability.
"""
from math import isfinite
from pathlib import Path

import pandas as pd


DATA_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "processed"
    / "hormuz_importer_flows_2025.csv"
)

REQUIRED_COLUMNS = {
    "country",
    "reference_year",
    "commodity",
    "baseline_hormuz_flow_mbd",
    "source_url",
    "data_status",
}


def load_importer_flow_profiles(path=DATA_PATH):
    """Load source-backed importer flow observations."""
    data = pd.read_csv(path)
    missing = REQUIRED_COLUMNS - set(data.columns)
    if missing:
        raise ValueError(f"Importer flow data is missing columns: {sorted(missing)}")
    if data["country"].duplicated().any():
        raise ValueError("Importer flow data contains duplicate country records.")
    data["baseline_hormuz_flow_mbd"] = pd.to_numeric(
        data["baseline_hormuz_flow_mbd"], errors="coerce"
    )
    if data["baseline_hormuz_flow_mbd"].isna().any():
        raise ValueError("Importer flow baseline values must be numeric and present.")
    if not data["baseline_hormuz_flow_mbd"].map(isfinite).all():
        raise ValueError("Importer flow baseline values must be finite.")
    if (data["baseline_hormuz_flow_mbd"] <= 0).any():
        raise ValueError("Importer flow baseline values must be positive.")
    for column in (
        "country",
        "commodity",
        "source_url",
        "data_status",
        "source_organization",
        "data_provider",
        "limitations",
    ):
        if data[column].isna().any() or data[column].astype(str).str.strip().eq("").any():
            raise ValueError(f"Importer flow {column} values cannot be blank.")
    if not data["source_url"].astype(str).str.startswith(("https://", "http://")).all():
        raise ValueError("Importer flow source_url values must be HTTP(S) URLs.")
    data["reference_year"] = pd.to_numeric(data["reference_year"], errors="raise").astype(int)
    return data


def _finite_number(value, name, minimum=0.0, maximum=None):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a number.")
    if not isfinite(value):
        raise ValueError(f"{name} must be finite.")
    if value < minimum or (maximum is not None and value > maximum):
        bound = f"between {minimum} and {maximum}" if maximum is not None else f"at least {minimum}"
        raise ValueError(f"{name} must be {bound}.")


def run_importer_resilience_scenario(
    country,
    disruption_fraction=1.0,
    disruption_duration_days=30,
    alternative_supply_mbd=0.0,
    alternative_supply_start_day=1,
    buffer_cover_days=0.0,
    simulation_days=None,
    profiles=None,
):
    """Simulate a country-specific interruption to its observed Hormuz flow.

    buffer_cover_days is an analyst-defined stock buffer expressed as days
    of the disrupted Hormuz flow. It is not an observed national stock metric.
    Alternative supply is user-specified, capped at the daily lost flow, and
    is not an allocation of the shared Saudi/UAE pipeline bypass capacity.
    """
    data = load_importer_flow_profiles() if profiles is None else profiles.copy()
    if "country" not in data.columns or "baseline_hormuz_flow_mbd" not in data.columns:
        raise ValueError("profiles must include country and baseline_hormuz_flow_mbd.")
    selected = data[data["country"].eq(country)]
    if len(selected) != 1:
        raise ValueError("Country must match exactly one source-backed importer profile.")
    baseline_flow = float(selected.iloc[0]["baseline_hormuz_flow_mbd"])
    _finite_number(baseline_flow, "baseline_hormuz_flow_mbd", minimum=0.000001)
    _finite_number(disruption_fraction, "disruption_fraction", maximum=1.0)
    _finite_number(alternative_supply_mbd, "alternative_supply_mbd")
    _finite_number(buffer_cover_days, "buffer_cover_days")

    if (
        isinstance(disruption_duration_days, bool)
        or not isinstance(disruption_duration_days, int)
        or disruption_duration_days < 0
    ):
        raise ValueError("disruption_duration_days must be a non-negative integer.")
    if (
        isinstance(alternative_supply_start_day, bool)
        or not isinstance(alternative_supply_start_day, int)
        or alternative_supply_start_day < 1
    ):
        raise ValueError("alternative_supply_start_day must be a positive integer.")

    if simulation_days is None:
        simulation_days = max(1, disruption_duration_days + 30)
    if (
        isinstance(simulation_days, bool)
        or not isinstance(simulation_days, int)
        or simulation_days < 1
    ):
        raise ValueError("simulation_days must be a positive integer.")
    if simulation_days < disruption_duration_days:
        raise ValueError("simulation_days cannot be shorter than disruption_duration_days.")

    gross_loss_mbd = baseline_flow * disruption_fraction
    starting_buffer_million_barrels = gross_loss_mbd * buffer_cover_days
    buffer_remaining = starting_buffer_million_barrels
    cumulative_uncovered = 0.0
    rows = []

    for day in range(1, simulation_days + 1):
        disruption_active = day <= disruption_duration_days
        gross_lost = gross_loss_mbd if disruption_active else 0.0
        alternative = (
            min(gross_lost, alternative_supply_mbd)
            if disruption_active and day >= alternative_supply_start_day
            else 0.0
        )
        residual_before_buffer = max(0.0, gross_lost - alternative)
        buffer_release = min(residual_before_buffer, buffer_remaining)
        buffer_remaining -= buffer_release
        uncovered = max(0.0, residual_before_buffer - buffer_release)
        cumulative_uncovered += uncovered

        rows.append(
            {
                "day": day,
                "disruption_active": disruption_active,
                "gross_lost_imports_mbd": gross_lost,
                "alternative_supply_mbd": alternative,
                "buffer_release_mbd": buffer_release,
                "uncovered_import_gap_mbd": uncovered,
                "buffer_remaining_million_barrels": buffer_remaining,
                "cumulative_uncovered_gap_million_barrels": cumulative_uncovered,
            }
        )

    daily = pd.DataFrame(rows)
    summary = {
        "country": country,
        "reference_year": int(selected.iloc[0].get("reference_year", 2025)),
        "baseline_hormuz_flow_mbd": baseline_flow,
        "disruption_fraction": disruption_fraction,
        "disruption_duration_days": disruption_duration_days,
        "gross_lost_import_volume_million_barrels": gross_loss_mbd
        * disruption_duration_days,
        "alternative_supply_capacity_mbd": alternative_supply_mbd,
        "alternative_supply_start_day": alternative_supply_start_day,
        "total_alternative_supply_million_barrels": daily[
            "alternative_supply_mbd"
        ].sum(),
        "assumed_buffer_cover_days": buffer_cover_days,
        "starting_buffer_million_barrels": starting_buffer_million_barrels,
        "total_buffer_release_million_barrels": daily["buffer_release_mbd"].sum(),
        "total_uncovered_gap_million_barrels": cumulative_uncovered,
        "maximum_daily_uncovered_gap_mbd": daily[
            "uncovered_import_gap_mbd"
        ].max(),
        "ending_buffer_million_barrels": buffer_remaining,
    }
    return {"summary": summary, "daily": daily}
