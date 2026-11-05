"""LNG importer resilience model using source-backed Hormuz destination flows.

All scenario rates use million cubic metres/day (mcm/day), and inventories/
cumulative volumes use million cubic metres (mcm). Annual destination flows
are converted to calendar-day averages. Alternative cargo, buffer inventory,
and demand response are analyst assumptions, not measured capabilities.
"""
from math import isfinite
from pathlib import Path

import pandas as pd


DATA_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "processed"
    / "hormuz_importer_lng_flows_2025.csv"
)

REQUIRED_COLUMNS = {
    "country",
    "reference_year",
    "annual_hormuz_lng_flow_bcm",
    "source_organization",
    "data_provider",
    "source_url",
    "data_status",
    "limitations",
}


def load_lng_importer_profiles(path=DATA_PATH):
    """Load and validate annual destination LNG-flow estimates."""
    data = pd.read_csv(path)
    missing = REQUIRED_COLUMNS - set(data.columns)
    if missing:
        raise ValueError(f"LNG importer data is missing columns: {sorted(missing)}")
    if data["country"].duplicated().any():
        raise ValueError("LNG importer data contains duplicate country records.")

    data["annual_hormuz_lng_flow_bcm"] = pd.to_numeric(
        data["annual_hormuz_lng_flow_bcm"], errors="coerce"
    )
    if data["annual_hormuz_lng_flow_bcm"].isna().any():
        raise ValueError("Annual LNG flow values must be numeric and present.")
    if not data["annual_hormuz_lng_flow_bcm"].map(isfinite).all():
        raise ValueError("Annual LNG flow values must be finite.")
    if (data["annual_hormuz_lng_flow_bcm"] <= 0).any():
        raise ValueError("Annual LNG flow values must be positive.")

    for column in (
        "country",
        "source_organization",
        "data_provider",
        "source_url",
        "data_status",
        "limitations",
    ):
        if data[column].isna().any() or data[column].astype(str).str.strip().eq("").any():
            raise ValueError(f"LNG importer {column} values cannot be blank.")
    if not data["source_url"].astype(str).str.startswith(("https://", "http://")).all():
        raise ValueError("LNG importer source_url values must be HTTP(S) URLs.")

    data["reference_year"] = pd.to_numeric(
        data["reference_year"], errors="raise"
    ).astype(int)
    return data


def _finite_number(value, name, minimum=0.0, maximum=None):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a number.")
    if not isfinite(value):
        raise ValueError(f"{name} must be finite.")
    if value < minimum or (maximum is not None and value > maximum):
        bounds = (
            f"between {minimum} and {maximum}"
            if maximum is not None
            else f"at least {minimum}"
        )
        raise ValueError(f"{name} must be {bounds}.")


def run_lng_importer_resilience_scenario(
    country,
    disruption_fraction=1.0,
    disruption_duration_days=30,
    alternative_supply_mcm_per_day=0.0,
    alternative_supply_start_day=1,
    buffer_cover_days=0.0,
    demand_reduction_fraction=0.0,
    simulation_days=None,
    days_in_year=365,
    profiles=None,
):
    """Simulate LNG import interruption and three explicit response levers.

    Response order each day:
      1. Alternative LNG cargoes replace lost flow.
      2. A finite analyst-defined buffer covers the remaining gap.
      3. Demand response reduces the residual gap, capped by a fraction of
         the day's gross lost Hormuz flow.

    The buffer is expressed as days of gross disrupted Hormuz flow. It is not
    actual national storage capacity or official stock cover. Demand response
    is not a claim that gas demand can be curtailed without economic impacts.
    """
    data = load_lng_importer_profiles() if profiles is None else profiles.copy()
    required = {"country", "annual_hormuz_lng_flow_bcm"}
    if not required.issubset(data.columns):
        raise ValueError("profiles must include country and annual_hormuz_lng_flow_bcm.")
    selected = data[data["country"].eq(country)]
    if len(selected) != 1:
        raise ValueError("Country must match exactly one LNG destination profile.")

    annual_flow_bcm = float(selected.iloc[0]["annual_hormuz_lng_flow_bcm"])
    _finite_number(annual_flow_bcm, "annual_hormuz_lng_flow_bcm", minimum=0.000001)
    _finite_number(disruption_fraction, "disruption_fraction", maximum=1.0)
    _finite_number(alternative_supply_mcm_per_day, "alternative_supply_mcm_per_day")
    _finite_number(buffer_cover_days, "buffer_cover_days")
    _finite_number(demand_reduction_fraction, "demand_reduction_fraction", maximum=1.0)

    if isinstance(days_in_year, bool) or not isinstance(days_in_year, int) or days_in_year not in (365, 366):
        raise ValueError("days_in_year must be 365 or 366.")
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

    baseline_flow_mcm_per_day = annual_flow_bcm * 1000.0 / days_in_year
    gross_loss_mcm_per_day = baseline_flow_mcm_per_day * disruption_fraction
    starting_buffer_mcm = gross_loss_mcm_per_day * buffer_cover_days
    buffer_remaining_mcm = starting_buffer_mcm
    cumulative_uncovered_mcm = 0.0
    rows = []

    for day in range(1, simulation_days + 1):
        disruption_active = day <= disruption_duration_days
        gross_lost = gross_loss_mcm_per_day if disruption_active else 0.0
        alternative = (
            min(gross_lost, alternative_supply_mcm_per_day)
            if disruption_active and day >= alternative_supply_start_day
            else 0.0
        )
        residual_after_alternative = max(0.0, gross_lost - alternative)
        buffer_release = min(residual_after_alternative, buffer_remaining_mcm)
        buffer_remaining_mcm -= buffer_release
        residual_after_buffer = max(0.0, residual_after_alternative - buffer_release)
        demand_response = min(
            residual_after_buffer,
            gross_lost * demand_reduction_fraction,
        )
        uncovered = max(0.0, residual_after_buffer - demand_response)
        cumulative_uncovered_mcm += uncovered

        rows.append(
            {
                "day": day,
                "disruption_active": disruption_active,
                "gross_lost_lng_mcm_per_day": gross_lost,
                "alternative_lng_mcm_per_day": alternative,
                "buffer_release_mcm_per_day": buffer_release,
                "demand_response_mcm_per_day": demand_response,
                "uncovered_lng_gap_mcm_per_day": uncovered,
                "buffer_remaining_mcm": buffer_remaining_mcm,
                "cumulative_uncovered_lng_gap_mcm": cumulative_uncovered_mcm,
            }
        )

    daily = pd.DataFrame(rows)
    total = lambda column: float(daily[column].sum())
    summary = {
        "country": country,
        "reference_year": int(selected.iloc[0].get("reference_year", 2025)),
        "annual_hormuz_lng_flow_bcm": annual_flow_bcm,
        "days_in_year_for_average": days_in_year,
        "baseline_hormuz_lng_flow_mcm_per_day": baseline_flow_mcm_per_day,
        "disruption_fraction": disruption_fraction,
        "disruption_duration_days": disruption_duration_days,
        "gross_lost_lng_volume_mcm": gross_loss_mcm_per_day * disruption_duration_days,
        "alternative_supply_capacity_mcm_per_day": alternative_supply_mcm_per_day,
        "alternative_supply_start_day": alternative_supply_start_day,
        "total_alternative_lng_mcm": total("alternative_lng_mcm_per_day"),
        "assumed_buffer_cover_days": buffer_cover_days,
        "starting_buffer_mcm": starting_buffer_mcm,
        "total_buffer_release_mcm": total("buffer_release_mcm_per_day"),
        "demand_reduction_fraction_of_gross_loss": demand_reduction_fraction,
        "total_demand_response_mcm": total("demand_response_mcm_per_day"),
        "total_uncovered_lng_gap_mcm": cumulative_uncovered_mcm,
        "maximum_daily_uncovered_lng_gap_mcm_per_day": float(
            daily["uncovered_lng_gap_mcm_per_day"].max()
        ),
        "ending_buffer_mcm": buffer_remaining_mcm,
    }
    return {"summary": summary, "daily": daily}
