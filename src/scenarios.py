from src.simulation import run_simulation


def summarize_results(results):
    # Calculate useful summary statistics for a simulation

    total_unmet = sum(row["unmet_demand"] for row in results)

    shortage_days = sum(row["unmet_demand"] > 0 for row in results)

    critical_days = sum(row["is_critical"] for row in results)

    severe_days = sum(row["severity"] == "Severe" for row in results)

    maximum_shortage_percentage = max(
        (row["shortage_percentage"] for row in results),
        default=0.0,
    )

    maximum_shortage = max(
        (row["unmet_demand"] for row in results),
        default=0.0,
    )

    return {
        "total_unmet_demand": total_unmet,
        "shortage_days": shortage_days,
        "maximum_daily_shortage": maximum_shortage,
        "remaining_reserves": results[-1]["reserves_remaining"],
        "critical_days": critical_days,
        "severe_days": severe_days,
        "maximum_shortage_percentage": maximum_shortage_percentage,
    }


def compare_scenarios():
    # Compare three responses to the same supply disruption

    common_inputs = {
        "baseline_supply": 100,
        "daily_demand": 95,
        "initial_reserves": 200,
        "shock_loss_pct": 0.25,
        "shock_start_day": 1,
        "shock_duration": 20,
        "reserve_release_limit": 5,
        "recovery_rate": 0.10,
        "days": 60,
    }

    scenarios = {
        "No intervention": {
            "use_reserves": False,
            "demand_reduction_pct": 0,
        },
        "Reserve release": {
            "use_reserves": True,
            "demand_reduction_pct": 0,
        },
        "Combined response": {
            "use_reserves": True,
            "demand_reduction_pct": 0.10,
        },
    }

    comparison = {}

    for name, strategy in scenarios.items():
        results = run_simulation(
            **common_inputs,
            **strategy,
        )

        comparison[name] = {
            "daily_results": results,
            "summary": summarize_results(results),
        }

    return comparison


if __name__ == "__main__":
    comparison = compare_scenarios()

    for name, data in comparison.items():
        print(f"\n--- {name} ---")

        for metric, value in data["summary"].items():
            print(f"{metric}: {value:.2f}")
