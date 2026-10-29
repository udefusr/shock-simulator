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
    reserves = initial_reserves
    results = []

    for day in range(1, days + 1):
        shock_active = shock_start_day <= day < shock_start_day + shock_duration

        loss = shock_loss_pct if shock_active else 0.0
        supply = baseline_supply * (1 - loss)
        demand = daily_demand * (1 - demand_reduction_pct)

        deficit = max(0.0, demand - supply)

        release = 0.0
        if use_reserves:
            release = min(
                deficit,
                reserve_release_limit,
                reserves,
            )

        reserves -= release
        unmet_demand = max(0.0, deficit - release)

        results.append(
            {
                "day": day,
                "supply": supply,
                "demand": demand,
                "reserve_release": release,
                "reserves_remaining": reserves,
                "unmet_demand": unmet_demand,
            }
        )

    return results


if __name__ == "__main__":
    results = run_simulation()

    for row in results:
        print(row)
