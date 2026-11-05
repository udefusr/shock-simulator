# Shock Simulator

A Python-based simulation project exploring how supply disruptions
affect demand, reserves, shortages, and system recovery.

Shock Simulator models a simplified resource-supply system. It lets you
define a disruption, apply response strategies, and examine how
different assumptions change the system's behaviour over time.

> **Project status:** Early-stage prototype. The model currently uses
> simplified, configurable assumptions and is intended for
> experimentation and learning not real-world forecasting or
> operational policy decisions.

## What it does

The current simulation can:

- Model a temporary reduction in supply.
- Track daily supply, demand, reserve releases, and unmet demand.
- Simulate gradual supply recovery after a disruption ends.
- Apply reserve-release and demand-reduction strategies.
- Calculate shortage percentages and classify disruption severity.
- Compare multiple response scenarios using summary metrics.
- Validate simulation inputs and run automated tests.

## How it works

The simulation advances one day at a time.

1. **Baseline:** Define normal supply and daily demand.
2. **Shock:** Apply a percentage reduction in supply for a specified
    duration.
3. **Response:** Optionally release reserves, up to a daily release
    limit and the available reserve stock.
4. **Recovery:** Once the shock ends, supply gradually approaches its
    baseline level.
5. **Assessment:** Calculate unmet demand, shortage percentage, and
    severity for each day.

### Severity classification

Severity is based on the percentage of daily demand that goes unmet.

                      Unmet demand as a percentage of demand Classification
  ---------------------------------------------------------- ----------------
                                                          0% Normal
                 Greater than 0% up to the warning threshold Warning
    Above the warning threshold up to the critical threshold Critical
                                Above the critical threshold Severe

The default warning and critical thresholds are 5% and 15%,
respectively. They can be changed through the simulation parameters.
These are prototype assumptions, not validated real-world thresholds.

## Project structure

``` text
shock-simulator/
├── src/
│   ├── __init__.py
│   ├── simulation.py
│   └── scenarios.py
├── tests/
│   └── test_simulation.py
├── main.py
├── requirements.txt
└── README.md
```

The exact contents of the repository may evolve as the project develops.

## Getting started

### Requirements

- Python
- `pip`
- Git (optional, for cloning and version control)

### 1. Clone the repository

``` bash
git clone https://github.com/YOUR-USERNAME/shock-simulator.git
cd shock-simulator
```

Replace `YOUR-USERNAME` with your GitHub username.

### 2. Create a virtual environment

**Windows PowerShell**

``` powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can use the environment's
interpreter directly:

``` powershell
.venv\Scripts\python.exe -m pip install pytest
```

**macOS / Linux**

``` bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install the test dependency

The simulation currently uses Python's standard library. Install
`pytest` to run the test suite:

``` bash
python -m pip install pytest
```

If the repository's `requirements.txt` lists the project dependencies,
you can instead install them with:

``` bash
python -m pip install -r requirements.txt
```

### 4. Run the scenario comparison

From the repository root:

``` bash
python -m src.scenarios
```

This runs the built-in response scenarios and prints summary metrics.

### 5. Run the tests

``` bash
python -m pytest -v
```

Run these commands from the repository root so Python can resolve the
`src` package correctly.

## Current model parameters

The simulation exposes parameters including:

| Parameter | Description |
| --- | --- |
| `baseline_supply` | Normal daily supply |
| `daily_demand` | Daily demand |
| `initial_reserves` | Starting reserve stock |
| `shock_loss_pct` | Fraction of baseline supply lost during the shock (0--1) |
| `shock_start_day` | First day of the disruption |
| `shock_duration` | Number of days the disruption lasts |
| `reserve_release_limit` | Maximum reserve release per day |
| `use_reserves` | Whether reserve releases are enabled |
| `demand_reduction_pct` | Fraction of demand reduced (0--1) |
| `recovery_rate` | Fraction of the remaining supply gap recovered each day |
| `warning_threshold` | Upper boundary of the Warning classification |
| `critical_threshold` | Upper boundary of the Critical classification |

Supply, demand, and reserve quantities must use consistent units. The
model does not enforce a particular real-world unit.

## Built-in scenarios

The scenario comparison currently evaluates three strategies under
shared baseline conditions:

- **No intervention:** No reserve release and no demand reduction.
- **Reserve release:** Reserve stock can be released to reduce
    shortages.
- **Combined response:** Reserve release and a demand reduction are
    both applied.

The scenario values are illustrative. They should not be interpreted as
recommended intervention levels.

## Model assumptions and limitations

The current implementation is intentionally simplified.

- Supply is reduced to a fixed level while the shock is active.
- Recovery begins immediately after the shock ends and follows a
    gradual, exponential-style recovery rule.
- Reserve releases directly offset the daily supply deficit.
- Reserve releases are limited by available stock and a daily release
    limit.
- Demand is constant unless a demand-reduction parameter is applied.
- The model does not yet represent prices, market behaviour, imports,
    production constraints, transport networks, storage infrastructure,
    or distribution bottlenecks.
- The severity thresholds are configurable assumptions and have not
    yet been calibrated against empirical evidence.
- The model is deterministic: identical inputs produce identical
    outputs.

These limitations matter. The simulator is currently a **what-if
model**, not a predictive model of actual energy markets or geopolitical
events.

## Development roadmap

Planned areas of development include:

- [x] Basic daily supply-and-demand simulation
- [x] Reserve-release response
- [x] Gradual post-shock supply recovery
- [x] Shortage severity classification
- [x] Configurable severity thresholds
- [x] One-factor-at-a-time sensitivity analysis
- [ ] Improved model validation and empirical calibration
- [ ] Additional disruption types and response strategies
- [x] Visualisation and interactive exploration

The roadmap may change as the model is tested and refined.

## Contributing

This is an evolving project. Suggestions, bug reports, and constructive
feedback are welcome.

For substantial changes, consider opening an issue first to discuss the
proposed model behaviour or implementation.

## Disclaimer

Shock Simulator is an educational and experimental software project. Its
outputs depend on simplified assumptions and user-provided parameters.
They should not be used as forecasts, investment guidance,
emergency-planning instructions, or operational policy recommendations.

## License

No license has been selected yet. Unless a license is added to this
repository, the project remains under its default copyright and reuse is
not automatically granted.
