"""Empirically informed scenarios for the 2026 oil disruption study.

Important:
- EIA production shut-in estimates calibrate the shock percentages.
- The simulation itself uses normalized units, not million barrels per day.
- The percentages describe the covered Gulf producer baseline, not global
  oil supply.
"""

from dataclasses import asdict, dataclass

from src.scenarios import summarize_results
from src.simulation import run_simulation


# --------------------------------------------------
# Empirical reference values
# --------------------------------------------------

GULF_PRODUCER_BASELINE_MBD = 25.2

MARCH_JULY_SHUTINS_MBD = 8.512
AUGUST_SHUTINS_MBD = 5.760
SEPTEMBER_SHUTINS_MBD = 4.770

MARCH_JULY_SHOCK_PCT = MARCH_JULY_SHUTINS_MBD / GULF_PRODUCER_BASELINE_MBD

AUGUST_SHOCK_PCT = AUGUST_SHUTINS_MBD / GULF_PRODUCER_BASELINE_MBD

SEPTEMBER_SHOCK_PCT = SEPTEMBER_SHUTINS_MBD / GULF_PRODUCER_BASELINE_MBD


# The longest shock lasts 153 days. An additional 60 days allows
# us to examine post-shock recovery in the simulation.
RECOVERY_WINDOW_DAYS = 60
SIMULATION_HORIZON_DAYS = 153 + RECOVERY_WINDOW_DAYS


# --------------------------------------------------
# Scenario definitions
# --------------------------------------------------


@dataclass(frozen=True)
class ScenarioDefinition:
    scenario_id: str
    name: str
    shock_loss_pct: float
    shock_duration_days: int
    classification: str
    evidence_basis: str
    interpretation: str


SCENARIOS = (
    ScenarioDefinition(
        scenario_id="baseline",
        name="Baseline — no disruption",
        shock_loss_pct=0.0,
        shock_duration_days=0,
        classification="Counterfactual",
        evidence_basis="No supply disruption applied.",
        interpretation=("Reference case used to compare disruption outcomes."),
    ),
    ScenarioDefinition(
        scenario_id="observed_benchmark",
        name="March–July observed-period benchmark",
        shock_loss_pct=MARCH_JULY_SHOCK_PCT,
        shock_duration_days=153,
        classification="EIA-derived benchmark",
        evidence_basis=(
            "8.512 mb/d estimated average shut-ins divided by "
            "25.2 mb/d February baseline production."
        ),
        interpretation=(
            "Regional production-disruption benchmark for the "
            "covered Gulf producers. Not a global supply-loss estimate."
        ),
    ),
    ScenarioDefinition(
        scenario_id="august_conditions",
        name="August 2026 conditions",
        shock_loss_pct=AUGUST_SHOCK_PCT,
        shock_duration_days=31,
        classification="EIA-derived benchmark",
        evidence_basis=(
            "5.760 mb/d estimated shut-ins divided by "
            "25.2 mb/d February baseline production."
        ),
        interpretation=(
            "A separate 31-day stress scenario based on the August estimate."
        ),
    ),
    ScenarioDefinition(
        scenario_id="september_conditions",
        name="September 2026 conditions",
        shock_loss_pct=SEPTEMBER_SHOCK_PCT,
        shock_duration_days=30,
        classification="EIA-derived benchmark",
        evidence_basis=(
            "4.770 mb/d estimated shut-ins divided by "
            "25.2 mb/d February baseline production."
        ),
        interpretation=(
            "A separate 30-day stress scenario based on the September estimate."
        ),
    ),
    ScenarioDefinition(
        scenario_id="severe_stress",
        name="Severe stress test",
        shock_loss_pct=0.50,
        shock_duration_days=153,
        classification="Hypothetical stress test",
        evidence_basis="Analyst-defined 50% supply shock.",
        interpretation=(
            "Tests system resilience under a disruption more severe "
            "than the observed-period benchmark."
        ),
    ),
    ScenarioDefinition(
        scenario_id="extreme_stress",
        name="Extreme stress test",
        shock_loss_pct=0.75,
        shock_duration_days=153,
        classification="Hypothetical stress test",
        evidence_basis="Analyst-defined 75% supply shock.",
        interpretation=(
            "Explores an extreme disruption. This is not a historical "
            "observation or an EIA forecast."
        ),
    ),
)


_SCENARIOS_BY_ID = {scenario.scenario_id: scenario for scenario in SCENARIOS}


# --------------------------------------------------
# Response strategies
# --------------------------------------------------

RESPONSE_STRATEGIES = {
    "No intervention": {
        "use_reserves": False,
        "demand_reduction_pct": 0.0,
    },
    "Reserve release": {
        "use_reserves": True,
        "demand_reduction_pct": 0.0,
    },
    "Combined response": {
        "use_reserves": True,
        "demand_reduction_pct": 0.10,
    },
}


# --------------------------------------------------
# Default normalized model assumptions
# --------------------------------------------------

BASE_MODEL_INPUTS = {
    "baseline_supply": 100.0,
    "daily_demand": 95.0,
    "initial_reserves": 200.0,
    "reserve_release_limit": 5.0,
    "recovery_rate": 0.10,
    "shock_start_day": 1,
    "days": SIMULATION_HORIZON_DAYS,
    "warning_threshold": 5.0,
    "critical_threshold": 15.0,
}


# --------------------------------------------------
# Scenario access
# --------------------------------------------------


def list_empirical_scenarios():
    """Return all scenario definitions as dictionaries."""

    return [asdict(scenario) for scenario in SCENARIOS]


def get_empirical_scenario(scenario_id):
    """Return one scenario definition by its ID."""

    try:
        return _SCENARIOS_BY_ID[scenario_id]
    except KeyError as exc:
        valid_ids = ", ".join(_SCENARIOS_BY_ID)

        raise ValueError(
            f"Unknown scenario '{scenario_id}'. Valid scenario IDs: {valid_ids}"
        ) from exc


# --------------------------------------------------
# Build simulation inputs
# --------------------------------------------------


def build_simulation_inputs(
    scenario_id,
    strategy="No intervention",
):
    """Convert a scenario and response strategy into engine inputs."""

    scenario = get_empirical_scenario(scenario_id)

    if strategy not in RESPONSE_STRATEGIES:
        valid_strategies = ", ".join(RESPONSE_STRATEGIES)

        raise ValueError(
            f"Unknown strategy '{strategy}'. Valid strategies: {valid_strategies}"
        )

    inputs = BASE_MODEL_INPUTS.copy()

    inputs.update(
        {
            "shock_loss_pct": scenario.shock_loss_pct,
            "shock_duration": scenario.shock_duration_days,
        }
    )

    inputs.update(RESPONSE_STRATEGIES[strategy])

    return inputs


# --------------------------------------------------
# Run one scenario
# --------------------------------------------------


def run_empirical_scenario(
    scenario_id,
    strategy="No intervention",
):
    """Run one empirical scenario and return results and metadata."""

    scenario = get_empirical_scenario(scenario_id)

    inputs = build_simulation_inputs(
        scenario_id=scenario_id,
        strategy=strategy,
    )

    daily_results = run_simulation(**inputs)

    summary = summarize_results(daily_results)

    return {
        "scenario": asdict(scenario),
        "strategy": strategy,
        "inputs": inputs,
        "daily_results": daily_results,
        "summary": summary,
    }


# --------------------------------------------------
# Run all scenarios with one response strategy
# --------------------------------------------------


def run_empirical_scenarios(
    strategy="No intervention",
):
    """Run every scenario using the same response strategy."""

    return {
        scenario.scenario_id: run_empirical_scenario(
            scenario_id=scenario.scenario_id,
            strategy=strategy,
        )
        for scenario in SCENARIOS
    }
