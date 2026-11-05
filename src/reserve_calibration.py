"""Evidence-aware conversion of compatible reserve records into model units.

This adapter never guesses a demand denominator. The caller must supply a
physical daily-flow denominator whose unit matches the inventory and release
rate record. This denominator must represent the same physical flow as the
simulation's model_daily_demand. It produces normalized model inputs, not a
forecast of actual deliveries.
"""
from math import isclose, isfinite
import pandas as pd

from src.reserve_data import load_reserve_profiles, load_reserve_response_events


INVENTORY_TO_FLOW_UNIT = {
    "million barrels": "million barrels per day",
    "million kilolitres": "million kilolitres per day",
    "million tonnes": "million tonnes per day",
}


DOE_SPR_DESIGN_REFERENCE_URL = (
    "https://www.energy.gov/ceser/articles/"
    "long-term-strategic-review-ltsr-us-strategic-petroleum-reserve-spr-report-congress"
)
DOE_SPR_DESIGN_REFERENCE_RATE = 4.4
DOE_SPR_DESIGN_REFERENCE_PERIODS = (
    (1, 90, 4.4),
    (91, 120, 3.8),
    (121, 150, 3.4),
    (151, None, 1.9),
)


def build_doe_spr_design_reference_schedule(nominal_release_rate):
    """Return DOE's historical 2016 drawdown curve as cap multipliers."""
    _positive_finite(nominal_release_rate, "nominal_release_rate")
    if not isclose(
        float(nominal_release_rate),
        DOE_SPR_DESIGN_REFERENCE_RATE,
        rel_tol=0.0,
        abs_tol=0.05,
    ):
        raise ValueError(
            "The DOE design-reference schedule requires a 4.4 million-barrel/day nominal rate."
        )

    return [
        {
            "start_day": start_day,
            "end_day": end_day,
            "rate_multiplier": rate / DOE_SPR_DESIGN_REFERENCE_RATE,
        }
        for start_day, end_day, rate in DOE_SPR_DESIGN_REFERENCE_PERIODS
    ]


def _positive_finite(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a number.")
    if not isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be finite and greater than zero.")


def list_calibratable_profiles(profiles=None):
    """Return profiles with inventory, daily release rate, and lead time."""
    data = load_reserve_profiles() if profiles is None else profiles.copy()
    required_values = [
        "inventory_quantity",
        "nominal_release_rate",
        "release_lead_time_days",
    ]
    eligible = data[required_values].notna().all(axis=1)
    eligible &= data["inventory_quantity"].gt(0)
    eligible &= data["nominal_release_rate"].gt(0)
    eligible &= data["inventory_unit"].isin(INVENTORY_TO_FLOW_UNIT)
    eligible &= data.apply(
        lambda row: row["release_rate_unit"]
        == INVENTORY_TO_FLOW_UNIT.get(row["inventory_unit"]),
        axis=1,
    )
    return data.loc[eligible].reset_index(drop=True)


def calibrate_reserve_profile(
    country,
    physical_daily_demand,
    physical_daily_demand_unit,
    model_daily_demand=95.0,
    reference_date=None,
    demand_denominator_basis="User-specified physical daily flow",
    profiles=None,
):
    """Convert one compatible reserve profile into normalized model inputs.

    The day-1 convention is that a reserve-release decision is made on
    simulation day 1. A stated lead time of N complete days therefore makes
    market delivery available from day N+1.
    """
    _positive_finite(physical_daily_demand, "physical_daily_demand")
    _positive_finite(model_daily_demand, "model_daily_demand")
    if not isinstance(country, str) or not country.strip():
        raise ValueError("country must be a non-empty string.")
    if not isinstance(physical_daily_demand_unit, str):
        raise TypeError("physical_daily_demand_unit must be a string.")
    if not isinstance(demand_denominator_basis, str) or not demand_denominator_basis.strip():
        raise ValueError("demand_denominator_basis must be a non-empty string.")

    data = load_reserve_profiles() if profiles is None else profiles.copy()
    selected = data[data["country"].eq(country)]
    if reference_date is not None:
        selected = selected[selected["reference_date"].astype(str).eq(str(reference_date))]
    if selected.empty:
        raise ValueError("No reserve profile matches the selected country and reference date.")
    if len(selected) != 1:
        raise ValueError("Select a reference_date because multiple reserve snapshots exist.")

    row = selected.iloc[0]
    required = ("inventory_quantity", "nominal_release_rate", "release_lead_time_days")
    if any(pd.isna(row[column]) for column in required):
        raise ValueError("Selected profile lacks inventory, release-rate, or lead-time evidence.")

    expected_flow_unit = INVENTORY_TO_FLOW_UNIT.get(row["inventory_unit"])
    if expected_flow_unit is None:
        raise ValueError(f"Unsupported inventory unit: {row['inventory_unit']}.")
    if physical_daily_demand_unit != expected_flow_unit:
        raise ValueError(
            f"Daily-demand unit must be '{expected_flow_unit}' for this inventory unit."
        )
    if row["release_rate_unit"] != expected_flow_unit:
        raise ValueError("Inventory and release-rate units are not compatible.")

    lead_time = float(row["release_lead_time_days"])
    if not isfinite(lead_time) or lead_time < 0 or not lead_time.is_integer():
        raise ValueError("release_lead_time_days must be a non-negative whole number.")

    stock_cover_days = float(row["inventory_quantity"]) / float(physical_daily_demand)
    release_share_of_demand = (
        float(row["nominal_release_rate"]) / float(physical_daily_demand)
    )
    model_initial_reserves = stock_cover_days * float(model_daily_demand)
    model_release_limit = release_share_of_demand * float(model_daily_demand)

    return {
        "country": country,
        "source_organization": row["source_organization"],
        "stock_category": row["stock_category"],
        "reference_date": str(row["reference_date"]),
        "inventory_quantity": float(row["inventory_quantity"]),
        "inventory_unit": row["inventory_unit"],
        "nominal_release_rate": float(row["nominal_release_rate"]),
        "release_rate_unit": row["release_rate_unit"],
        "release_lead_time_days": int(lead_time),
        "physical_daily_demand": float(physical_daily_demand),
        "physical_daily_demand_unit": physical_daily_demand_unit,
        "demand_denominator_basis": demand_denominator_basis,
        "derived_stock_cover_days": stock_cover_days,
        "nominal_release_as_share_of_daily_demand": release_share_of_demand,
        "model_daily_demand": float(model_daily_demand),
        "initial_reserves_model_units": model_initial_reserves,
        "reserve_release_limit_model_units": model_release_limit,
        "reserve_release_start_day": int(lead_time) + 1,
        "doe_spr_design_reference_schedule": (
            build_doe_spr_design_reference_schedule(float(row["nominal_release_rate"]))
            if country == "United States"
            else None
        ),
        "doe_spr_design_reference_url": DOE_SPR_DESIGN_REFERENCE_URL,
        "calibration_status": "Derived from reported inventory/rate plus user-supplied demand denominator",
        "source_url": row["source_url"],
        "interpretation_note": (
            "Nominal capability is not a guarantee of actual market delivery. "
            "The chosen demand denominator is user supplied. Day 1 is the decision day; "
            "delivery starts after the stated complete lead time. The optional DOE "
            "design-reference taper is historical engineering design data, not a "
            "measurement of current effective site capability."
        ),
    }


def summarize_announced_release_denominators(events=None):
    """Derive the implied daily-supply denominator from stated equivalent days.

    This is NOT a physical release rate. It is quantity divided by the
    official 'equivalent days of supply' statement.
    """
    data = load_reserve_response_events() if events is None else events.copy()
    releases = data[
        data["event_type"].eq("government_stock_release")
        & data["announced_quantity"].notna()
        & data["equivalent_days"].notna()
        & data["equivalent_days"].gt(0)
    ].copy()
    releases["implied_daily_supply_equivalent"] = (
        releases["announced_quantity"] / releases["equivalent_days"]
    )
    releases["implied_daily_supply_unit"] = (
        releases["quantity_unit"].astype(str) + " per day"
    )
    releases["derived_metric_status"] = (
        "Implied supply denominator from stated equivalent days; not a release rate"
    )
    return releases[
        [
            "event_id",
            "country",
            "decision_date",
            "announced_quantity",
            "quantity_unit",
            "equivalent_days",
            "implied_daily_supply_equivalent",
            "implied_daily_supply_unit",
            "derived_metric_status",
            "source_url",
        ]
    ].reset_index(drop=True)
