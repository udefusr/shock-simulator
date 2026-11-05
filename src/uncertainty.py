"""Deterministic bounded scenario-envelope analysis.

This module enumerates user-defined low/base/high assumptions. It assigns no
probabilities and must not be interpreted as Monte Carlo forecasting.
"""
from itertools import product
from math import isfinite

import pandas as pd

from src.empirical_scenarios import build_simulation_inputs
from src.scenarios import summarize_results
from src.simulation import run_simulation


DEFAULT_LEVELS = {
    "shock_loss_multipliers": (0.8, 1.0, 1.2),
    "shock_duration_multipliers": (0.8, 1.0, 1.2),
    "reserve_inventory_fractions": (0.5, 0.75, 1.0),
    "release_limit_fractions": (0.5, 0.75, 1.0),
    "recovery_rate_multipliers": (0.5, 1.0, 1.5),
    "additional_mobilization_delays": (0, 7, 14),
}

MAX_ENVELOPE_RUNS = 5000


def _validate_levels(name, values, *, integer=False, minimum=None, maximum=None):
    if not isinstance(values, (tuple, list)) or len(values) != 3:
        raise ValueError(f"{name} must contain exactly three low/base/high values.")

    parsed = []
    for value in values:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"{name} values must be numeric.")
        if not isfinite(value):
            raise ValueError(f"{name} values must be finite.")
        if integer and not float(value).is_integer():
            raise ValueError(f"{name} values must be whole numbers.")
        number = int(value) if integer else float(value)
        if minimum is not None and number < minimum:
            raise ValueError(f"{name} values must be at least {minimum}.")
        if maximum is not None and number > maximum:
            raise ValueError(f"{name} values cannot exceed {maximum}.")
        parsed.append(number)

    if parsed != sorted(parsed) or len(set(parsed)) != 3:
        raise ValueError(f"{name} values must be strictly increasing.")
    return tuple(parsed)


def run_scenario_envelope(
    scenario_id,
    strategy="Reserve release",
    shock_loss_multipliers=DEFAULT_LEVELS["shock_loss_multipliers"],
    shock_duration_multipliers=DEFAULT_LEVELS["shock_duration_multipliers"],
    reserve_inventory_fractions=DEFAULT_LEVELS["reserve_inventory_fractions"],
    release_limit_fractions=DEFAULT_LEVELS["release_limit_fractions"],
    recovery_rate_multipliers=DEFAULT_LEVELS["recovery_rate_multipliers"],
    additional_mobilization_delays=DEFAULT_LEVELS["additional_mobilization_delays"],
    max_runs=MAX_ENVELOPE_RUNS,
):
    """Run the full factorial grid and return runs, baseline, and metric ranges.

    Reserve-only dimensions are used intentionally: a no-intervention strategy
    would make reserve inventory, release capability, and mobilisation delay
    irrelevant while inflating the grid with duplicate outcomes.
    """
    if strategy not in ("Reserve release", "Combined response"):
        raise ValueError("Uncertainty envelopes require a reserve-enabled response strategy.")

    if isinstance(max_runs, bool) or not isinstance(max_runs, int) or max_runs < 1:
        raise ValueError("max_runs must be a positive integer.")

    levels = {
        "shock_loss_multiplier": _validate_levels(
            "shock_loss_multipliers", shock_loss_multipliers, minimum=0
        ),
        "shock_duration_multiplier": _validate_levels(
            "shock_duration_multipliers", shock_duration_multipliers, minimum=0
        ),
        "reserve_inventory_fraction": _validate_levels(
            "reserve_inventory_fractions", reserve_inventory_fractions, minimum=0, maximum=1
        ),
        "release_limit_fraction": _validate_levels(
            "release_limit_fractions", release_limit_fractions, minimum=0, maximum=1
        ),
        "recovery_rate_multiplier": _validate_levels(
            "recovery_rate_multipliers", recovery_rate_multipliers, minimum=0
        ),
        "additional_mobilization_delay_days": _validate_levels(
            "additional_mobilization_delays", additional_mobilization_delays,
            integer=True, minimum=0
        ),
    }

    combinations = list(product(*levels.values()))
    if len(combinations) > max_runs:
        raise ValueError(
            f"Scenario grid contains {len(combinations)} runs, exceeding max_runs={max_runs}."
        )

    base = build_simulation_inputs(scenario_id, strategy)
    base_release_start = base.get("reserve_release_start_day", 1)
    rows = []
    reference_summary = None
    reference_inputs = None

    for values in combinations:
        (
            shock_mult,
            duration_mult,
            inventory_fraction,
            release_fraction,
            recovery_mult,
            extra_delay,
        ) = values

        inputs = base.copy()
        inputs["shock_loss_pct"] = base["shock_loss_pct"] * shock_mult
        inputs["shock_duration"] = int(round(base["shock_duration"] * duration_mult))
        inputs["initial_reserves"] = base["initial_reserves"] * inventory_fraction
        inputs["reserve_release_limit"] = base["reserve_release_limit"] * release_fraction
        inputs["recovery_rate"] = base["recovery_rate"] * recovery_mult
        if inputs["shock_loss_pct"] > 1:
            raise ValueError("Shock-loss multiplier produces a supply loss above 100%.")
        if inputs["recovery_rate"] > 1:
            raise ValueError("Recovery-rate multiplier produces a recovery rate above 100%.")
        inputs["reserve_release_start_day"] = base_release_start + extra_delay

        daily = run_simulation(**inputs)
        summary = summarize_results(daily)
        row = {
            "shock_loss_multiplier": shock_mult,
            "shock_loss_pct": inputs["shock_loss_pct"] * 100,
            "shock_duration_multiplier": duration_mult,
            "shock_duration_days": inputs["shock_duration"],
            "reserve_inventory_fraction": inventory_fraction,
            "initial_reserves_model_units": inputs["initial_reserves"],
            "release_limit_fraction": release_fraction,
            "release_limit_model_units_per_day": inputs["reserve_release_limit"],
            "recovery_rate_multiplier": recovery_mult,
            "recovery_rate": inputs["recovery_rate"],
            "additional_mobilization_delay_days": extra_delay,
            "reserve_release_start_day": inputs["reserve_release_start_day"],
            "total_unmet_demand": summary["total_unmet_demand"],
            "shortage_days": summary["shortage_days"],
            "critical_days": summary["critical_days"],
            "severe_days": summary["severe_days"],
            "maximum_shortage_percentage": summary["maximum_shortage_percentage"],
            "remaining_reserves": summary["remaining_reserves"],
            "total_reserve_released": (
                inputs["initial_reserves"] - summary["remaining_reserves"]
            ),
        }
        rows.append(row)

        is_reference = (
            shock_mult == 1.0
            and duration_mult == 1.0
            and inventory_fraction == 1.0
            and release_fraction == 1.0
            and recovery_mult == 1.0
            and extra_delay == 0
        )
        if is_reference:
            reference_summary = summary
            reference_inputs = inputs

    runs = pd.DataFrame(rows)
    if reference_summary is None:
        raise ValueError(
            "The uncertainty grid must include neutral levels: 1.0 multipliers, "
            "1.0 inventory/release fractions, and zero additional delay."
        )

    metric_columns = [
        "total_unmet_demand",
        "shortage_days",
        "critical_days",
        "severe_days",
        "maximum_shortage_percentage",
        "remaining_reserves",
        "total_reserve_released",
    ]
    envelope = pd.DataFrame(
        [
            {
                "metric": column,
                "minimum": runs[column].min(),
                "median_of_design_points": runs[column].median(),
                "maximum": runs[column].max(),
                "reference_case": reference_summary[
                    {
                        "total_unmet_demand": "total_unmet_demand",
                        "shortage_days": "shortage_days",
                        "critical_days": "critical_days",
                        "severe_days": "severe_days",
                        "maximum_shortage_percentage": "maximum_shortage_percentage",
                        "remaining_reserves": "remaining_reserves",
                        "total_reserve_released": None,
                    }.get(column, column)
                ] if column != "total_reserve_released" else (
                    reference_inputs["initial_reserves"] - reference_summary["remaining_reserves"]
                ),
            }
            for column in metric_columns
        ]
    )

    return {
        "scenario_id": scenario_id,
        "strategy": strategy,
        "runs": runs,
        "envelope": envelope,
        "reference_inputs": reference_inputs,
        "reference_summary": reference_summary,
        "run_count": len(runs),
        "interpretation": (
            "Deterministic full-factorial bounded scenario envelope. The median is "
            "the median of enumerated design points, not a probability-weighted estimate."
        ),
    }
