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
## What happens each day
The sequence is as follows:
1. Calculate how much supply remains after the shock
2. Apply any demand reduction measure.
3. Calculate the supply deficit.
4. If enabled, release reserves to cover part of the deficit
5. Calculate any demand that still cannot be met
6. Update remaining reserves and check critical thresholds
7. Move to the next day

## SHITTING MY PANTS

$$
S_t = S_0(1-L_t)
$$
$$
D_t = D_0(1-R_t)
$$

| $S_t$ | supply after disruption       |
| ----- | ----------------------------- |
| $D_t$ | demand after demand reduction |
| $L_t$ | supply loss fraction          |
| $R_t$ | demand-reduction fraction     |
$$Q_t = min(B_t, R_{max}, max(0, D_t - S_t))$$
$$B{t+1} = B_t - Q_t$$
The reserve release is limited by both the remaining stock and the daily release limit
$$ U_t=\max(0,D_t-S_t-Q_t)$$

| $Q_t$ | amount releassed that day |
| ----- | ------------------------- |
| $B_t$ | the reserve stock         |
## for the first run ( hypothetical)
- Normal supply: 100 mb/d
- Demand: 95 mb/d
- Initial reserves: 200 mb
- Supply loss: 25% for 20 days
- Maximum reserve release: 5 mb/d