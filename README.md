# Shock Simulator

Shock Simulator is an evolving Python research prototype for studying oil-supply resilience under production and maritime disruptions. It combines national energy statistics, documented disruption estimates, deterministic simulation, and an interactive Streamlit dashboard.

> **Research status:** The project is an exploratory, data-informed what-if framework. The current simulations use normalized units and simplified assumptions. They are not a global oil-market forecast or an operational policy tool.

## Research question

How do disruptions to critical maritime energy routes and regional oil production affect supply availability, and how do inventory releases and temporary demand responses change the resulting shortages?

The current empirical focus is the 2026 Strait of Hormuz disruption. The project distinguishes production shut-ins, maritime transit disruption, national trade observations, inventory records, and simulated outcomes rather than treating them as interchangeable measures.

## Current capabilities

- Deterministic day-by-day supply and demand simulation.
- Configurable supply disruption magnitude, timing, and duration.
- Reserve release constrained by starting inventory and a daily release limit.
- Gradual post-shock supply recovery.
- Demand reduction with configurable start day and duration.
- Daily unmet-demand and shortage-severity calculations.
- Six empirical/hypothetical scenario definitions and three response strategies (18 experiments).
- Sensitivity analysis for recovery, shock magnitude, reserve capacity, release limits, and demand reduction.
- JODI-Oil data loading and processing.
- EIA-based maritime-flow and production-shut-in reference datasets.
- Initial source-backed reserve profiles for the United States, Japan, South Korea, and Germany.
- Separate records for Japan's 2026 announced reserve releases and stockholding-obligation change.
- Reserve dataset schema validation and automated tests.
- Unit-checked U.S. SPR calibration adapter requiring an analyst-supplied physical daily-flow denominator and applying the DOE mobilisation lead time.
- Separate Japan announcement denominator cross-check that does not mislabel equivalent-day calculations as release rates.
- Streamlit dashboard with Plotly visualizations and CSV exports.

## Research evidence and interpretation

The project uses several different evidence types:

| Evidence | What it represents | What it does not establish |
|---|---|---|
| JODI country statistics | Reported national production, imports, exports, refinery intake and stocks | The maritime route used by a specific shipment |
| EIA chokepoint estimates | Estimated total oil flows through selected maritime routes | An equivalent loss of global oil supply |
| EIA production shut-ins | Estimated production unavailable in specified producer countries | A directly observed production series |
| Reserve profile sources | Inventory snapshots, capacities, stock categories and release procedures | That all recorded inventory is immediately deliverable |
| Reserve response events | Officially announced release plans or stockholding-policy changes | Verified physical withdrawals unless separately measured |
| Simulation output | Consequences under explicit model rules and assumptions | Causal proof or real-world predictive accuracy |

The EIA-derived March–July 2026 benchmark is calculated from estimated regional production shut-ins divided by the February baseline for covered Gulf producers. It is not a global supply-loss percentage. The model currently applies this benchmark to a normalized system for comparative experiments.

## Dashboard

Launch the application:

```powershell
streamlit run app.py
```

The dashboard currently contains:

1. **Simulation** — configurable supply, demand, reserve and recovery parameters.
2. **Scenario comparison** — compare no intervention, reserve release and a combined response.
3. **Sensitivity analysis** — inspect how demand-reduction assumptions affect outcomes.
4. **Empirical scenarios** — compare six scenarios under three response strategies, inspect individual runs, and export the 18-experiment results.
5. **Reserve calibration** — translate a compatible dated U.S. SPR record into normalized inventory and release parameters after the user supplies a matching physical daily-flow denominator; apply the mobilisation delay and export calibration and simulation outputs.

The empirical scenario experiments restrict the 10% demand-reduction response to the disruption window. Demand returns to baseline during recovery. Reserve releases may continue during recovery while a deficit remains and reserve stock is available.

## Current model assumptions

The simulation is deterministic. It advances one day at a time:

1. Apply the specified supply loss during the disruption window.
2. Calculate demand, including any active demand-reduction policy.
3. Release reserves if enabled, limited by both the daily cap and remaining stock.
4. Calculate unmet demand and shortage severity.
5. After the supply shock ends, recover supply gradually toward baseline.

Important assumptions and limitations:
- Supply, demand and reserve quantities must use consistent units.
- The current empirical experiments use normalized units, not million barrels or barrels per day.
- Reserve capacity and daily release limits in the original 18 empirical experiments remain illustrative assumptions. The separate Reserve calibration tab translates only compatible U.S. SPR records using an explicitly user-supplied physical daily-flow denominator.
- Crude oil and refined-product inventories are not interchangeable without considering refining, quality, transport and distribution.
- The model does not yet explicitly represent oil prices, refinery constraints, alternative shipping routes, country-level trade networks or market substitution.
- The U.S. SPR calibration uses a country-specific reserve profile inside a normalized wider supply-disruption model; it is not a full U.S. oil-market, global trade, or Hormuz-importer model.
- The calibrated release limit is constant in the simulation. DOE describes a nominal rate of up to 4.4 million barrels/day for up to 90 days before drawdown capability declines; the declining-rate curve is not yet implemented.
- The model does not establish that observed national changes were caused solely by the Hormuz disruption.
- Severity thresholds are configurable assumptions, not empirically validated thresholds.

## Data and research files

- `data/raw/jodi/` — original JODI-Oil downloads.
- `data/raw/other/eia_chokepoint_flows.csv` — manually transcribed EIA route-flow estimates.
- `data/raw/other/eia_production_shutins.csv` — manually transcribed EIA production shut-in estimates.
- `data/raw/other/reserve_response_events.csv` — manually structured official Japanese reserve-response announcements.
- `data/processed/reserve_profiles_initial.csv` — source-backed reserve profile snapshots, preserving native units and stock definitions.
- `research/methodology.md` — research and simulation methodology.
- `research/data_dictionary.md` — data fields and measurement units.
- `research/source_register.md` — source register.
- `research/findings.md` — descriptive results and scenario experiments.
- `research/scenario_design.md` — empirical and hypothetical scenario definitions.
- `research/reserve_data_assessment.md` — reserve-source assessment, comparability cautions and data gaps.
- `research/reserve_calibration_method.md` — unit-compatible conversion, lead-time treatment, and calibration limitations.

The reserve data is an initial source inventory, not a calibrated cross-country reserve dataset. Missing values mean not reported or not established; they are not zero.

## Repository structure

```text
shock-simulator/
├── src/
│   ├── simulation.py
│   ├── scenarios.py
│   ├── empirical_scenarios.py
│   ├── sensitivity.py
│   ├── data_loader.py
│   ├── reserve_data.py
│   └── reserve_calibration.py
├── scripts/
│   └── validate_reserve_data.py
├── tests/
│   ├── test_simulation.py
│   ├── test_sensitivity.py
│   ├── test_empirical_scenarios.py
│   ├── test_reserve_data.py
│   └── test_reserve_calibration.py
├── data/
│   ├── raw/
│   │   ├── jodi/
│   │   └── other/
│   └── processed/
├── research/
├── app.py
├── main.py
├── requirements.txt
└── README.md
```

The virtual environment directory (usually `.venv/`) should remain local and should not be committed.

## Setup

Python 3.10 or later is recommended.

### Windows PowerShell

```powershell
git clone https://github.com/udefusr/shock-simulator.git
cd shock-simulator
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### macOS / Linux

```bash
git clone https://github.com/udefusr/shock-simulator.git
cd shock-simulator
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Validation commands

Run all automated tests from the repository root:

```powershell
python -m pytest -v
```

Validate the source-backed reserve profile and response-event files:

```powershell
python -m scripts.validate_reserve_data
```

Run the built-in scenario comparison:

```powershell
python -m src.scenarios
```

Run the sensitivity experiments:

```powershell
python -m src.sensitivity
```

## Development roadmap

- [x] Basic daily supply-and-demand simulation.
- [x] Reserve-release response and finite stock constraint.
- [x] Gradual post-shock supply recovery.
- [x] Severity classification and configurable thresholds.
- [x] One-factor-at-a-time sensitivity analysis.
- [x] JODI and EIA source data processing.
- [x] Empirical scenario definitions and dashboard comparison.
- [x] Time-bounded demand-response policy in empirical experiments.
- [x] Initial national reserve profiles and response-event records.
- [x] Reserve schema validation and automated tests.
- [ ] Reconcile and extend dated reserve inventory time series.
- [ ] Harmonize reserve categories and country-level demand denominators.
- [x] Add an evidence-aware U.S. SPR calibration adapter with explicit demand denominator and mobilisation lead time.
- [ ] Extend reserve calibration with dated compatible inventory and release-rate series for Japan, South Korea, and Germany.
- [ ] Implement DOE's declining SPR drawdown-rate curve after the nominal 90-day period.
- [ ] Calibrate deliverable reserve release constraints by country.
- [ ] Model production disruption separately from maritime transit disruption and rerouting.
- [ ] Develop country-level importer and producer resilience models.
- [ ] Add uncertainty analysis and stronger empirical validation.
- [ ] Complete research report, figures and portfolio demonstration.

## Disclaimer

Shock Simulator is an educational and experimental research project. Its outputs depend on simplified assumptions and source limitations. They should not be used as forecasts, investment guidance, emergency-planning instructions or operational policy recommendations.

## License

No license has been selected yet. Unless a license is added to this repository, the project remains under its default copyright and reuse is not automatically granted.
