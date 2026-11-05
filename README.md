# Shock Simulator

A Python-based simulation project exploring how supply disruptions affect demand, reserves, shortages, and system recovery.

Shock Simulator models a simplified resource-supply system. It lets you define a disruption, apply response strategies, and examine how different assumptions change the system's behaviour over time. An interactive dashboard supports scenario exploration and comparison.

> **Project status:** Early-stage prototype. The model uses simplified, configurable assumptions for experimentation and learning. It is not a real-world forecasting system or an operational policy tool.

## What it does

The current project includes:

- A deterministic, day-by-day supply-and-demand simulation.
- Temporary supply disruptions with configurable start day, duration, and magnitude.
- Reserve deployment constrained by available stock and a daily release limit.
- Gradual post-shock supply recovery.
- Optional demand reduction.
- Daily unmet-demand calculations and shortage-severity classification.
- Configurable warning and critical severity thresholds.
- Scenario comparison across no-intervention, reserve-release, and combined-response strategies.
- One-factor-at-a-time sensitivity experiments, including recovery rate, shock magnitude, reserve capacity, reserve release limit, and demand reduction.
- An interactive Streamlit dashboard with Plotly charts.
- CSV export for scenario comparisons and demand-response sensitivity results.
- Input validation and automated tests.

## How it works

The simulation advances one day at a time:

1. **Baseline:** Define normal supply and daily demand.
2. **Shock:** Apply a percentage reduction in supply for a specified duration.
3. **Response:** Optionally release reserves, limited by available stock and the daily release cap. Demand can also be reduced.
4. **Recovery:** After the shock ends, supply gradually approaches its baseline level.
5. **Assessment:** Calculate daily unmet demand, shortage percentage, reserve use, and severity.

### Severity classification

Severity is based on the percentage of daily demand that goes unmet.

| Unmet demand as a percentage of demand | Classification |
| --- | --- |
| 0% | Normal |
| Greater than 0% up to the warning threshold | Warning |
| Above the warning threshold up to the critical threshold | Critical |
| Above the critical threshold | Severe |

The default warning and critical thresholds are 5% and 15%, respectively. They are configurable simulation parameters and are prototype assumptions, not empirically validated thresholds.

## Interactive dashboard

The Streamlit dashboard provides controls for core simulation parameters and visualizes:

- Baseline supply, reserve contribution, total available supply, and demand.
- Daily unmet demand.
- System severity over the simulation period.
- A comparison of no intervention, reserve deployment, and a combined response.
- Demand-reduction sensitivity results.

The dashboard also provides CSV downloads for the scenario comparison and demand-response sensitivity experiment.

## Project structure

```text
shock-simulator/
├── src/
│   ├── __init__.py
│   ├── simulation.py
│   ├── scenarios.py
│   └── sensitivity.py
├── tests/
│   ├── test_simulation.py
│   └── test_sensitivity.py
├── app.py
├── main.py
├── requirements.txt
└── README.md
```

The repository may contain additional files as development continues. The virtual environment directory (usually `.venv/`) should remain local and should not be committed.

## Getting started

### Requirements

- Python 3.10 or later (recommended)
- `pip`
- Git (optional, for cloning and version control)

### 1. Clone the repository

```bash
git clone https://github.com/udefusr/shock-simulator.git
cd shock-simulator
```

### 2. Create and activate a virtual environment

**Windows PowerShell**

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use the environment's interpreter directly:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

Install the project dependencies:

```bash
python -m pip install -r requirements.txt
```

The simulation engine uses Python code, while the interactive dashboard uses Streamlit and Plotly. The dashboard's CSV export uses pandas. The test suite uses pytest.

### 4. Run the interactive dashboard

From the repository root:

```bash
streamlit run app.py
```

Streamlit will start a local server and provide a URL for opening the dashboard in your browser.

### 5. Run the built-in scenario comparison

```bash
python -m src.scenarios
```

This runs the built-in response scenarios and prints summary metrics.

### 6. Run the sensitivity experiments

```bash
python -m src.sensitivity
```

This runs the sensitivity analyses defined in the module.

### 7. Run the tests

```bash
python -m pytest -v
```

Run these commands from the repository root so Python can resolve the `src` package correctly.

## Current model parameters

The simulation exposes parameters including:

| Parameter | Description |
| --- | --- |
| `baseline_supply` | Normal daily supply |
| `daily_demand` | Daily demand |
| `initial_reserves` | Starting reserve stock |
| `shock_loss_pct` | Fraction of baseline supply lost during the shock (0–1) |
| `shock_start_day` | First day of the disruption |
| `shock_duration` | Number of days the disruption lasts |
| `reserve_release_limit` | Maximum reserve release per day |
| `use_reserves` | Whether reserve releases are enabled |
| `demand_reduction_pct` | Fraction of demand reduced (0–1) |
| `recovery_rate` | Fraction of the remaining supply gap recovered each day |
| `days` | Number of simulation days |
| `warning_threshold` | Upper boundary of the Warning classification |
| `critical_threshold` | Upper boundary of the Critical classification |

Supply, demand, and reserve quantities must use consistent units. The model does not enforce a particular real-world unit.

## Scenario comparison

The dashboard compares three response strategies under the same baseline and shock conditions:

- **No intervention:** No reserve release and no demand reduction.
- **Reserve strategy:** Reserve stock can be released to reduce shortages.
- **Combined strategy:** Reserve release and a 10% demand reduction are applied.

The combined strategy's demand reduction is a fixed illustrative assumption in the current comparison. It is applied throughout the simulation, not only during the shock. These settings are not recommended intervention levels.

The comparison reports total unmet demand, shortage days, critical days, severe days, and remaining reserves. It is important to consider multiple metrics: a strategy can reduce cumulative unmet demand without eliminating all shortage days or periods of elevated severity.

## Sensitivity analysis

The sensitivity module varies one parameter at a time while holding the other inputs constant. The current experiments examine:

- Recovery rate.
- Shock magnitude.
- Initial reserve capacity.
- Daily reserve release limit.
- Demand-reduction percentage.

The demand-response experiment compares 0%, 5%, 10%, 15%, and 20% demand reduction under a fixed set of illustrative assumptions. Results are descriptive outputs of this simplified model, not empirical estimates of real-world intervention effects.

## Model assumptions and limitations

The current implementation is intentionally simplified:

- Supply is reduced to a fixed level while the shock is active.
- Recovery begins immediately after the shock ends and follows a gradual, exponential-style recovery rule.
- Reserve releases directly offset the daily supply deficit.
- Reserve releases are limited by available stock and a daily release limit.
- Demand is constant unless a demand-reduction parameter is applied.
- The model does not yet represent prices, market behaviour, imports, production constraints, transport networks, storage infrastructure, or distribution bottlenecks.
- The model does not currently represent surplus supply being stored for later use.
- Severity thresholds are configurable assumptions and have not been calibrated against empirical evidence.
- The model is deterministic: identical inputs produce identical outputs.

These limitations matter. The simulator is currently a **what-if model**, not a predictive model of actual energy markets or geopolitical events. Passing software tests demonstrates that the implementation behaves as expected for tested cases; it does not establish real-world predictive accuracy.

## Development roadmap

- [x] Basic daily supply-and-demand simulation
- [x] Reserve-release response
- [x] Gradual post-shock supply recovery
- [x] Shortage severity classification
- [x] Configurable severity thresholds
- [x] One-factor-at-a-time sensitivity analysis
- [ ] Improved model validation and empirical calibration
- [ ] Additional disruption types and response strategies
- [x] Visualisation and interactive exploration
- [x] Scenario comparison and CSV export

The roadmap may change as the model is tested and refined.

## Contributing

This is an evolving project. Suggestions, bug reports, and constructive feedback are welcome.

For substantial changes, consider opening an issue first to discuss the proposed model behaviour or implementation.

## Disclaimer

Shock Simulator is an educational and experimental software project. Its outputs depend on simplified assumptions and user-provided parameters. They should not be used as forecasts, investment guidance, emergency-planning instructions, or operational policy recommendations.

## License

No license has been selected yet. Unless a license is added to this repository, the project remains under its default copyright and reuse is not automatically granted.
