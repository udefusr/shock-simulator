## Build in 6 stages:
- Build a tiny simulation in Python
- Make the calculations meaningful
- Add scenarios
- Add mitigation strategies
- Build the dashboard
- Validate and improve the model

## Roles maybe
- Problem research
- Simulation
- Interface
- Testing and documentation

## Things to do first
1. **A one-page model specification**: The problem, variables, assumptions and expected outputs.
2. **A tiny working python simulation**: no dashboard yet.
3. **A comparison of at least three scenarios**: baseline, disruption and intervention.

## Variables that can change:
*labelled hypothetical values*

| variable              | description                        |
| --------------------- | ---------------------------------- |
| baseline_supply       | normal daily supply                |
| daily_demand          | normal daily demand                |
| shock_loss_pct        | rate of normal supply loss         |
| shock_shart_day       | day of the disruption begins       |
| shock_duration        | num of days the disruption lasts   |
| initial_reserves      | available reserve stock            |
| reserve_release_limit | maximum reserve release per day    |
| demand_reduction_pct  | optional reduction in daily demand |
