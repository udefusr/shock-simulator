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
    days,
):
    # Validate simulation parameters before running

    numeric_values = {
        "baseline_supply": baseline_supply,
        "daily_demand": daily_demand,
        "initial_reserves": initial_reserves,
        "shock_loss_pct": shock_loss_pct,
        "reserve_release_limit": reserve_release_limit,
        "demand_reduction_pct": demand_reduction_pct,
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

    if shock_start_day < 1:
        raise ValueError("shock_start_day must be at least 1.")

    if shock_duration < 0:
        raise ValueError("shock_duration cannot be negative.")

    if days < 1:
        raise ValueError("days must be at least 1.")

    if not isinstance(use_reserves, bool):
        raise TypeError("use_reserves must be a boolean.")


def simulate_day(
    day,
    baseline_supply,
    daily_demand,
    reserves,
    shock_loss_pct,
    shock_start_day,
    shock_duration,
    reserve_release_limit,
    demand_reduction_pct,
    use_reserves,
):
    # Calculate the system state for one simulation day

    shock_active = shock_start_day <= day < shock_start_day + shock_duration

    supply_loss = shock_loss_pct if shock_active else 0.0

    supply = baseline_supply * (1 - supply_loss)
    demand = daily_demand * (1 - demand_reduction_pct)

    deficit = max(0.0, demand - supply)

    release = 0.0

    if use_reserves:
        release = min(deficit, reserve_release_limit, reserves)

    remaining_reserves = reserves - release
    unmet_demand = max(0.0, deficit - release)

    return {
        "day": day,
        "shock_active": shock_active,
        "supply": supply,
        "demand": demand,
        "reserve_release": release,
        "reserves_remaining": remaining_reserves,
        "unmet_demand": unmet_demand,
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
    days=60,
):
    # Run a simulation and return daily results

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
        days,
    )

    reserves = float(initial_reserves)
    results = []

    for day in range(1, days + 1):
        daily_result = simulate_day(
            day=day,
            baseline_supply=baseline_supply,
            daily_demand=daily_demand,
            reserves=reserves,
            shock_loss_pct=shock_loss_pct,
            shock_start_day=shock_start_day,
            shock_duration=shock_duration,
            reserve_release_limit=reserve_release_limit,
            demand_reduction_pct=demand_reduction_pct,
            use_reserves=use_reserves,
        )

        reserves = daily_result["reserves_remaining"]
        results.append(daily_result)

    return results
