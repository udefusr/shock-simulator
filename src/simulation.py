from math import isfinite


def _validate_reserve_release_schedule(schedule):
    """Validate a contiguous schedule indexed by days since first delivery."""
    if schedule is None:
        return
    if not isinstance(schedule, (list, tuple)) or not schedule:
        raise ValueError("reserve_release_schedule must be a non-empty list or tuple.")
    expected_start_day = 1
    for index, period in enumerate(schedule):
        if not isinstance(period, dict):
            raise TypeError("Each schedule period must be a dictionary.")
        if not {"start_day", "end_day", "rate_multiplier"}.issubset(period):
            raise ValueError("Each schedule period requires start_day, end_day, and rate_multiplier.")
        start_day, end_day = period["start_day"], period["end_day"]
        multiplier = period["rate_multiplier"]
        if isinstance(start_day, bool) or not isinstance(start_day, int):
            raise TypeError("Schedule start_day values must be integers.")
        if start_day != expected_start_day:
            raise ValueError("Schedule periods must be contiguous and start at drawdown day 1.")
        if end_day is not None:
            if isinstance(end_day, bool) or not isinstance(end_day, int):
                raise TypeError("Schedule end_day values must be integers or None.")
            if end_day < start_day:
                raise ValueError("Schedule end_day cannot precede start_day.")
            expected_start_day = end_day + 1
        else:
            if index != len(schedule) - 1:
                raise ValueError("Only the final schedule period may have end_day=None.")
        if isinstance(multiplier, bool) or not isinstance(multiplier, (int, float)):
            raise TypeError("Schedule rate_multiplier values must be numeric.")
        if not isfinite(multiplier) or not 0 <= multiplier <= 1:
            raise ValueError("Schedule rate_multiplier values must be between 0 and 1.")
    if schedule[-1]["end_day"] is not None:
        raise ValueError("The final schedule period must be open-ended.")


def _reserve_release_rate_multiplier(day, reserve_release_start_day, schedule):
    """Return the schedule multiplier using days since first delivery."""
    if day < reserve_release_start_day:
        return 0.0
    if schedule is None:
        return 1.0
    drawdown_day = day - reserve_release_start_day + 1
    for period in schedule:
        if drawdown_day >= period["start_day"] and (
            period["end_day"] is None or drawdown_day <= period["end_day"]
        ):
            return float(period["rate_multiplier"])
    raise RuntimeError("Validated schedule does not cover this drawdown day.")

def validate_inputs(
    baseline_supply,
    daily_demand,
    initial_reserves,
    shock_loss_pct,
    shock_start_day,
    shock_duration,
    reserve_release_limit,
    demand_reduction_pct,
    use_reserves,
    recovery_rate,
    days,
    warning_threshold,
    critical_threshold,
    demand_reduction_start_day=1,
    demand_reduction_duration=None,
    reserve_release_start_day=1,
    reserve_release_schedule=None,
):
    """Validate simulation parameters before running."""

    numeric_values = {
        "baseline_supply": baseline_supply,
        "daily_demand": daily_demand,
        "initial_reserves": initial_reserves,
        "shock_loss_pct": shock_loss_pct,
        "reserve_release_limit": reserve_release_limit,
        "demand_reduction_pct": demand_reduction_pct,
        "recovery_rate": recovery_rate,
        "warning_threshold": warning_threshold,
        "critical_threshold": critical_threshold,
    }

    for name, value in numeric_values.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"{name} must be a number.")

        if not isfinite(value):
            raise ValueError(f"{name} must be finite.")

    for name in (
        "baseline_supply",
        "daily_demand",
        "initial_reserves",
        "reserve_release_limit",
    ):
        if numeric_values[name] < 0:
            raise ValueError(f"{name} cannot be negative.")

    if not 0 <= shock_loss_pct <= 1:
        raise ValueError("shock_loss_pct must be between 0 and 1.")

    if not 0 <= demand_reduction_pct <= 1:
        raise ValueError("demand_reduction_pct must be between 0 and 1.")

    if isinstance(shock_start_day, bool) or not isinstance(shock_start_day, int):
        raise TypeError("shock_start_day must be an integer.")

    if isinstance(shock_duration, bool) or not isinstance(shock_duration, int):
        raise TypeError("shock_duration must be an integer.")

    if isinstance(days, bool) or not isinstance(days, int):
        raise TypeError("days must be an integer.")

    if isinstance(demand_reduction_start_day, bool) or not isinstance(
        demand_reduction_start_day, int
    ):
        raise TypeError("demand_reduction_start_day must be an integer.")

    if shock_start_day < 1:
        raise ValueError("shock_start_day must be at least 1.")

    if shock_duration < 0:
        raise ValueError("shock_duration cannot be negative.")

    if demand_reduction_start_day < 1:
        raise ValueError("demand_reduction_start_day must be at least 1.")

    if demand_reduction_duration is not None:
        if isinstance(demand_reduction_duration, bool) or not isinstance(
            demand_reduction_duration, int
        ):
            raise TypeError("demand_reduction_duration must be an integer or None.")

        if demand_reduction_duration < 0:
            raise ValueError("demand_reduction_duration cannot be negative.")

    if days < 1:
        raise ValueError("days must be at least 1.")

    if isinstance(reserve_release_start_day, bool) or not isinstance(reserve_release_start_day, int):
        raise TypeError("reserve_release_start_day must be an integer.")

    if reserve_release_start_day < 1:
        raise ValueError("reserve_release_start_day must be at least 1.")

    _validate_reserve_release_schedule(reserve_release_schedule)

    if not isinstance(use_reserves, bool):
        raise TypeError("use_reserves must be a boolean.")

    if not 0 < recovery_rate <= 1:
        raise ValueError("recovery_rate must be greater than 0 and at most 1.")

    if not 0 <= warning_threshold < critical_threshold <= 100:
        raise ValueError(
            "Thresholds must satisfy: "
            "0 <= warning_threshold < critical_threshold <= 100."
        )


def classify_severity(
    shortage_percentage,
    warning_threshold=5.0,
    critical_threshold=15.0,
):
    """Classify severity using configurable shortage thresholds."""

    if not 0 <= warning_threshold < critical_threshold <= 100:
        raise ValueError(
            "Thresholds must satisfy: "
            "0 <= warning_threshold < critical_threshold <= 100."
        )

    if shortage_percentage < 0 or shortage_percentage > 100:
        raise ValueError("shortage_percentage must be between 0 and 100.")

    if shortage_percentage == 0:
        return "Normal"
    elif shortage_percentage <= warning_threshold:
        return "Warning"
    elif shortage_percentage <= critical_threshold:
        return "Critical"
    else:
        return "Severe"


def simulate_day(
    day,
    baseline_supply,
    daily_demand,
    previous_supply,
    reserves,
    shock_loss_pct,
    shock_start_day,
    shock_duration,
    reserve_release_limit,
    demand_reduction_pct,
    recovery_rate,
    use_reserves,
    warning_threshold=5.0,
    critical_threshold=15.0,
    demand_reduction_start_day=1,
    demand_reduction_duration=None,
    reserve_release_start_day=1,
    reserve_release_schedule=None,
):
    """Calculate the system state for one simulation day."""

    shock_active = shock_start_day <= day < shock_start_day + shock_duration

    if shock_active:
        supply = baseline_supply * (1 - shock_loss_pct)
    else:
        supply = previous_supply + recovery_rate * (baseline_supply - previous_supply)

    # Determine whether demand reduction is active today.
    demand_reduction_active = day >= demand_reduction_start_day and (
        demand_reduction_duration is None
        or day < demand_reduction_start_day + demand_reduction_duration
    )

    effective_demand_reduction = (
        demand_reduction_pct if demand_reduction_active else 0.0
    )

    demand = daily_demand * (1 - effective_demand_reduction)

    deficit = max(0.0, demand - supply)

    release = 0.0

    reserve_release_active = use_reserves and day >= reserve_release_start_day
    reserve_drawdown_day = day - reserve_release_start_day + 1 if reserve_release_active else None
    release_rate_multiplier = (
        _reserve_release_rate_multiplier(day, reserve_release_start_day, reserve_release_schedule)
        if reserve_release_active else 0.0
    )
    release_limit_today = reserve_release_limit * release_rate_multiplier
    if reserve_release_active:
        release = min(deficit, release_limit_today, reserves)

    remaining_reserves = reserves - release
    unmet_demand = max(0.0, deficit - release)
    shortage_percentage = (unmet_demand / demand) * 100 if demand > 0 else 0.0

    severity = classify_severity(
        shortage_percentage,
        warning_threshold,
        critical_threshold,
    )

    is_critical = severity in ("Critical", "Severe")

    return {
        "day": day,
        "shock_active": shock_active,
        "demand_reduction_active": demand_reduction_active,
        "reserve_release_active": reserve_release_active,
        "reserve_drawdown_day": reserve_drawdown_day,
        "reserve_release_rate_multiplier": release_rate_multiplier,
        "reserve_release_limit_today": release_limit_today,
        "supply": supply,
        "demand": demand,
        "reserve_release": release,
        "reserves_remaining": remaining_reserves,
        "unmet_demand": unmet_demand,
        "shortage_percentage": shortage_percentage,
        "severity": severity,
        "is_critical": is_critical,
    }


def run_simulation(
    baseline_supply=100.0,
    daily_demand=95.0,
    initial_reserves=200.0,
    shock_loss_pct=0.25,
    shock_start_day=1,
    shock_duration=20,
    reserve_release_limit=5.0,
    demand_reduction_pct=0.0,
    use_reserves=True,
    recovery_rate=0.10,
    days=60,
    warning_threshold=5.0,
    critical_threshold=15.0,
    demand_reduction_start_day=1,
    demand_reduction_duration=None,
    reserve_release_start_day=1,
    reserve_release_schedule=None,
):
    """Run a simulation and return daily results."""

    validate_inputs(
        baseline_supply,
        daily_demand,
        initial_reserves,
        shock_loss_pct,
        shock_start_day,
        shock_duration,
        reserve_release_limit,
        demand_reduction_pct,
        use_reserves,
        recovery_rate,
        days,
        warning_threshold,
        critical_threshold,
        demand_reduction_start_day,
        demand_reduction_duration,
        reserve_release_start_day,
        reserve_release_schedule,
    )

    reserves = float(initial_reserves)
    previous_supply = float(baseline_supply)
    results = []

    for day in range(1, days + 1):
        daily_result = simulate_day(
            day=day,
            baseline_supply=baseline_supply,
            previous_supply=previous_supply,
            daily_demand=daily_demand,
            reserves=reserves,
            shock_loss_pct=shock_loss_pct,
            shock_start_day=shock_start_day,
            shock_duration=shock_duration,
            reserve_release_limit=reserve_release_limit,
            demand_reduction_pct=demand_reduction_pct,
            use_reserves=use_reserves,
            recovery_rate=recovery_rate,
            warning_threshold=warning_threshold,
            critical_threshold=critical_threshold,
            demand_reduction_start_day=demand_reduction_start_day,
            demand_reduction_duration=demand_reduction_duration,
            reserve_release_start_day=reserve_release_start_day,
            reserve_release_schedule=reserve_release_schedule,
        )

        previous_supply = daily_result["supply"]
        reserves = daily_result["reserves_remaining"]
        results.append(daily_result)

    return results
