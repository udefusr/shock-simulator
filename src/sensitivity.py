from src.scenarios import summarize_results
from src.simulation import run_simulation


def calculate_sensitivity_metrics(simulation, initial_reserves):
    summary = summarize_results(simulation)

    final_reserves = summary["remaining_reserves"]

    if initial_reserves > 0:
        reserve_utilization = (
            (initial_reserves - final_reserves) / initial_reserves
        ) * 100
    else:
        reserve_utilization = 0.0

    summary["reserve_utilization_percentage"] = reserve_utilization

    return summary


def calculate_improvement(baseline_value, current_value):
    if baseline_value == 0:
        return None

    improvement = ((baseline_value - current_value) / baseline_value) * 100

    return improvement


def add_baseline_comparisons(results, baseline_parameter):
    baseline = results[baseline_parameter]

    for parameter, summary in results.items():
        summary["unmet_demand_improvement_percentage"] = calculate_improvement(
            baseline["total_unmet_demand"], summary["total_unmet_demand"]
        )

        summary["shortage_days_improvement_percentage"] = calculate_improvement(
            baseline["shortage_days"], summary["shortage_days"]
        )

    return results


def analyze_recovery_rates():
    # Compare simulation outcomes across different recovery rates

    recovery_rates = [0.05, 0.10, 0.25, 0.50]

    common_inputs = {
        "baseline_supply": 100,
        "daily_demand": 95,
        "initial_reserves": 200,
        "shock_loss_pct": 0.25,
        "shock_start_day": 1,
        "shock_duration": 20,
        "reserve_release_limit": 5,
        "demand_reduction_pct": 0,
        "use_reserves": True,
        "days": 60,
        "warning_threshold": 5,
        "critical_threshold": 15,
    }

    results = {}

    for rate in recovery_rates:
        simulation = run_simulation(**common_inputs, recovery_rate=rate)

        summary = calculate_sensitivity_metrics(
            simulation, common_inputs["initial_reserves"]
        )
        results[rate] = summary

    add_baseline_comparisons(results, 0.05)

    return results


def analyze_shock_magnitude():

    shock_losses = [0.10, 0.20, 0.30, 0.40, 0.50]

    common_inputs = {
        "baseline_supply": 100,
        "daily_demand": 95,
        "initial_reserves": 200,
        "shock_start_day": 1,
        "shock_duration": 20,
        "reserve_release_limit": 5,
        "demand_reduction_pct": 0,
        "use_reserves": True,
        "days": 60,
        "warning_threshold": 5,
        "critical_threshold": 15,
        "recovery_rate": 0.1,
    }

    results = {}

    for loss in shock_losses:
        simulation = run_simulation(**common_inputs, shock_loss_pct=loss)

        summary = calculate_sensitivity_metrics(
            simulation, common_inputs["initial_reserves"]
        )
        results[loss] = summary

    add_baseline_comparisons(results, 0.10)
    return results


def analyze_reserve_capacities():

    reserve_capacities = [0, 50, 100, 200, 400, 800]

    common_inputs = {
        "baseline_supply": 100,
        "daily_demand": 95,
        "shock_start_day": 1,
        "shock_duration": 20,
        "reserve_release_limit": 5,
        "demand_reduction_pct": 0,
        "use_reserves": True,
        "days": 60,
        "warning_threshold": 5,
        "critical_threshold": 15,
        "recovery_rate": 0.1,
        "shock_loss_pct": 0.25,
    }

    results = {}

    for reserve in reserve_capacities:
        simulation = run_simulation(**common_inputs, initial_reserves=reserve)

        summary = calculate_sensitivity_metrics(simulation, reserve)
        results[reserve] = summary

    add_baseline_comparisons(results, 0)
    return results


def analyze_reserve_release_limits():
    reserve_release_limits = [2, 5, 10, 15, 20, 30]

    common_inputs = {
        "baseline_supply": 100,
        "daily_demand": 95,
        "shock_start_day": 1,
        "shock_duration": 20,
        "demand_reduction_pct": 0,
        "use_reserves": True,
        "days": 60,
        "warning_threshold": 5,
        "critical_threshold": 15,
        "recovery_rate": 0.1,
        "shock_loss_pct": 0.25,
        "initial_reserves": 200,
    }

    results = {}

    for limit in reserve_release_limits:
        simulation = run_simulation(**common_inputs, reserve_release_limit=limit)

        summary = calculate_sensitivity_metrics(
            simulation, common_inputs["initial_reserves"]
        )
        results[limit] = summary

    add_baseline_comparisons(results, 2)
    return results


def print_analysis(title, results, parameter_label, parameter_formatter=None):
    print(f"\n{title}")
    print("=" * 65)

    for parameter, summary in results.items():
        if parameter_formatter:
            parameter_text = parameter_formatter(parameter)
        else:
            parameter_text = f"{parameter:.0f}"

        print(f"\n{parameter_label}: {parameter_text}")

        for metric, value in summary.items():
            if value is None:
                print(f"  {metric}: N/A")
            else:
                print(f"  {metric}: {value:.2f}")


if __name__ == "__main__":
    analyses = [
        (
            "RECOVERY RATE SENSITIVITY ANALYSIS",
            analyze_recovery_rates(),
            "Recovery rate",
            lambda x: f"{x * 100:.0f}%",
        ),
        (
            "SUPPLY MAGNITUDE SENSITIVITY ANALYSIS",
            analyze_shock_magnitude(),
            "Supply loss rate",
            lambda x: f"{x * 100:.0f}%",
        ),
        (
            "RESERVE CAPACITY SENSITIVITY ANALYSIS",
            analyze_reserve_capacities(),
            "Initial reserve capacity",
            lambda x: f"{x:.0f}",
        ),
        (
            "RESERVE RELEASE CAPACITY SENSITIVITY ANALYSIS",
            analyze_reserve_release_limits(),
            "Reserve release capacity",
            lambda x: f"{x:.0f}",
        ),
    ]

    for title, results, label, formatter in analyses:
        print_analysis(title, results, label, formatter)
