from math import isfinite


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

    if reserve_release_active:
        release = min(deficit, reserve_release_limit, reserves)

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
        )

        previous_supply = daily_result["supply"]
        reserves = daily_result["reserves_remaining"]
        results.append(daily_result)

    return results
