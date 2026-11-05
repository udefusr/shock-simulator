from src.sensitivity import (
    add_baseline_comparisons,
    calculate_improvement,
    calculate_sensitivity_metrics,
)


def test_calculate_improvement():
    assert calculate_improvement(100, 75) == 25.0


def test_calculate_negative_improvement():
    assert calculate_improvement(100, 125) == -25.0


def test_zero_baseline_returns_none():
    assert calculate_improvement(0, 50) is None


def test_identical_values_return_zero():
    assert calculate_improvement(100, 100) == 0.0


def test_baseline_comparison():
    results = {
        5: {
            "total_unmet_demand": 100,
            "shortage_days": 20,
        },
        10: {
            "total_unmet_demand": 75,
            "shortage_days": 10,
        },
    }

    add_baseline_comparisons(results, 5)

    assert results[10]["unmet_demand_improvement_percentage"] == 25.0
    assert results[10]["shortage_days_improvement_percentage"] == 50.0


def test_sensitivity_metrics_include_reserve_utilization():
    simulation = [
        {
            "day": 1,
            "unmet_demand": 5,
            "is_critical": False,
            "severity": "Warning",
            "shortage_percentage": 5.0,
            "reserves_remaining": 75,
        }
    ]

    summary = calculate_sensitivity_metrics(simulation, 100)

    assert summary["reserve_utilization_percentage"] == 25.0
