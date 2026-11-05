# Initial Reserve Data Assessment

**Research cutoff:** November 5, 2026.

**Status:** Initial source-backed assessment. These profiles are not yet a harmonized country comparison and must not be used directly as simulation inputs.

## 1. Purpose

This phase documents national oil stockholding systems, dated inventory observations, storage capacity, legal stockholding frameworks, and emergency-release procedures.

The initial comparison covers the United States, Japan, South Korea, and Germany. It is intentionally a source inventory rather than a complete cross-country ranking.

## 2. Initial source findings

### United States

The U.S. Department of Energy (DOE) reports that the Strategic Petroleum Reserve (SPR) is a government-owned crude-oil reserve held at four Gulf Coast sites.

The DOE quick-facts page provides two dated inventory snapshots relevant to this project:

- December 31, 2025: 411 million barrels, equivalent to approximately 125 days of U.S. crude-oil net imports.
- October 16, 2026: 282.2 million barrels across the four sites.

The page also reports authorized storage capacity of 714 million barrels and a maximum nominal drawdown capability of 4.4 million barrels per day. DOE's FAQ qualifies the rate: up to 4.4 million barrels per day for up to 90 days, after which the drawdown rate begins to decline as caverns empty. DOE says deliveries can begin within 13 days of a Presidential decision.

The 125-day metric belongs to the December 2025 inventory snapshot and uses U.S. crude-oil net imports. It is not the IEA's all-oil 90-day net-import stockholding obligation. The drawdown rate is a nominal system capability and should not be interpreted as a guarantee that all inventory is deliverable at that rate for an arbitrary period.

Sources:
- https://www.energy.gov/hgeo/opr/spr-quick-facts
- https://www.energy.gov/hgeo/opr/spr-faqs

### Japan

Japan's stockholding system includes distinct national, private-sector, and producer-country joint stockpiles.

The Agency for Natural Resources and Energy (ANRE/METI) reports that, as of the end of January 2026, Japan held 72.89 million kilolitres of petroleum stocks, equivalent to 70.06 million kilolitres on the stated product-equivalent basis, or approximately 248 days under Japan's domestic stockpiling-day calculation. This aggregate should not be treated as a public-only inventory, nor compared directly with IEA days of net imports without reconciling the product conversion and denominator.

Japan's 2026 emergency policy actions provide useful evidence on actual policy design:

- On March 24, METI announced a release of approximately 8.5 million kilolitres of national crude-oil stocks, about one month of supply, with release to proceed sequentially from March 26.
- On April 24, METI announced a second national crude-oil release of approximately 5.8 million kilolitres, equivalent to about 20 days of supply, with release to proceed from May 1.
- METI also extended a 15-day reduction in private-sector stockholding obligations through May 15. The April 15 notice states that the obligation level was reduced from 70 to 55 days.

These are official announcements and policy decisions. The announced release volumes are planned quantities; the notices alone do not establish the exact quantity physically delivered by any particular date.

Sources:
- https://www.enecho.meti.go.jp/about/special/johoteikyo/government_stockpiled_oil.html
- https://www.meti.go.jp/press/2025/03/20260324004/20260324004.html
- https://www.meti.go.jp/english/press/2026/0424_004.html
- https://www.meti.go.jp/english/press/2026/0415_002.html
- https://www.iea.org/articles/japan-oil-security-policy

### South Korea

KNOC reports that it operates nine stockpiling bases with combined capacity of 146 million barrels and held 100 million barrels of reserves, excluding international joint stockpiling reserves, as of August 2026. The page's department-contact section was updated August 31, 2026.

This is KNOC-operated stockpiling information. It is not a complete measure of all Korean government, obligated-industry, and commercial stocks. A comparable maximum daily release-rate figure was not established in this source review.

Source:
- https://www.knoc.co.kr/ENG/sub03/sub03_3_3.jsp

### Germany

Germany's Erdölbevorratungsverband (EBV) states that it holds approximately 20 million tonnes of crude oil and finished petroleum products. Its statutory mission is to maintain a reserve level based on average crude-oil and petroleum-product imports over a 90-day period.

EBV's published description states:
- Stocks include crude oil, gasoline products, diesel fuel, light heating oil, and jet fuel.
- Minimum stocks equivalent to 15 days of supply must be distributed in each of five designated supply areas.
- EBV must own 90% of its stocks itself; up to 10% may be held through delegation agreements.
- Reserve release requires a decree by the Federal Minister of Economics and Energy specifying the release period and product volumes.
- Allocations are generally apportioned equally over four calendar weeks.

The approximately 20-million-tonne figure has no observation date on the page. The statutory 90-day basis is not a measured current inventory-days-cover value. Four calendar weeks is the described allocation period after a release decree, not evidence of a fixed daily maximum release rate.

Sources:
- https://www.ebv-oil.org/cmse/cms2.asp?sid=60
- https://www.ebv-oil.org/cmse/cms2.asp?sid=64
- https://www.iea.org/articles/germanys-legislation-on-oil-security

## 3. IEA stockholding definitions

IEA member countries are required to ensure oil stocks equivalent to at least 90 days of net imports. The obligation can be met through different combinations of government stocks, agency stocks, and obligated industry stocks. Stocks may be crude oil or refined products, and eligible stocks may be held abroad under qualifying bilateral agreements.

The IEA days-of-net-import-cover calculation is not simply inventory divided by current consumption. Its methodology uses the previous calendar year's average daily net imports, makes product-equivalence adjustments, and deducts 10% of stocks to account for unavailable quantities such as tank bottoms. The IEA also adjusts eligible stocks and imports for specified product categories and stock changes.

Accordingly:
- IEA's 90-day minimum is a stockholding obligation, not a claim that every country currently holds exactly 90 days.
- Nationally reported domestic stockpile days can use different denominators.
- Government, agency, industry, and commercial inventories must not be merged without documenting eligibility and availability.
- A stockholding obligation does not itself demonstrate immediate deliverability.

Sources:
- https://www.iea.org/data-and-statistics/data-tools/oil-stocks-of-iea-countries
- https://www.iea.org/about/oil-security-and-emergency-response

## 4. Structured files

### Reserve profiles

File: `data/processed/reserve_profiles_initial.csv`

This file preserves:
- Country and responsible institution.
- Stock category.
- Reference date.
- Inventory quantity and native unit.
- Storage capacity and native unit.
- Stock-cover days and the stated denominator, where available.
- Nominal release rate and unit, where available.
- Release lead time and procedure.
- Source URL and data-quality notes.

Two U.S. inventory snapshots are stored separately to preserve the dated change from 411 million barrels at end-2025 to 282.2 million barrels on October 16, 2026.

### Reserve response events

File: `data/raw/other/reserve_response_events.csv`

This file records Japanese 2026 announced national stock releases and the temporary reduction in private stockholding obligations. Planned volumes, implementation dates, and obligation changes are stored as policy events; they are not represented as verified daily physical withdrawals.

### Validation code

- `src/reserve_data.py` loads and validates the reserve-profile schema.
- `scripts/validate_reserve_data.py` provides a command-line validation report.
- `tests/test_reserve_data.py` tests schema, units, missing values, duplicate keys and basic quantity constraints.

Blank numeric fields mean unknown/not reported, not zero.

## 5. Why these figures are not directly comparable

The source records describe different categories and units:
- U.S. DOE reports government-held crude oil.
- Japan reports an aggregate stockholding system involving national, private, and joint stockpiles.
- KNOC reports its own operated reserve stocks excluding international joint stockpiling.
- Germany's EBV reports agency-held crude oil and refined products.

The figures also use different reference dates, product scopes, accounting conventions, and days-cover denominators. A single column called `strategic_reserves` would therefore be misleading.

## 6. Data gaps to close before calibration

1. Retrieve dated monthly Japanese statistics that separately identify national, private, and joint stockpiles.
2. Find a dated Korean series and clarify how KNOC stocks relate to industry obligations and national IEA-accounted stocks.
3. Obtain a dated EBV stock series or annual report to timestamp the approximately 20-million-tonne figure.
4. Archive the U.S. weekly SPR inventory series to extend the dated snapshots into a time series.
5. Find documented release constraints for Japan, South Korea, and Germany, or explicitly leave those parameters uncalibrated.
6. Distinguish physical stocks, legal obligations, capacity, and deliverability.
7. Determine whether stocks are crude or product and whether product compatibility/refining capacity constrains their use.

## 7. Modelling rule

Do not convert these reserve observations directly into the current normalized model's 200 reserve units or five units/day release limit.

Before country-level calibration, define a consistent model scale and demand denominator. Where evidence only supports days of net-import cover, model in days of the same import measure rather than inventing absolute stock volumes.

Strategic crude oil and refined product stocks should not be treated as immediately interchangeable. Refining, product quality, transport, terminal access, and distribution can delay or limit delivery to consumers.

## 8. Interpretation boundary

This initial dataset is a source inventory and research aid. It is not evidence that every recorded barrel or tonne can be released at the nominal rate, nor that inventories are all physically accessible to the same market.

The next phase is to obtain reproducible time series, harmonize stock definitions, and design a reserve-response model with explicit deliverability assumptions.


## 9. Reserve calibration implementation (November 6, 2026)

The next-stage adapter is implemented in src/reserve_calibration.py. It converts one compatible reserve profile into normalized simulation inputs only when inventory, nominal daily release capability, lead time, and measurement units are all available.

The adapter requires a user-supplied physical daily-flow denominator and a written definition of that denominator. It calculates:

- Derived stock cover = reported inventory / user-supplied physical daily flow.
- Model inventory = derived stock-cover days × model daily demand.
- Model release limit = (reported nominal release rate / physical daily flow) × model daily demand.
- First modeled delivery day = stated complete lead time + 1, using day 1 as the decision day.

The two U.S. DOE records are eligible because both contain inventory, nominal rate, and lead-time information. Japan, South Korea, and Germany remain descriptive-only in this calibration adapter because the current records do not contain all required comparable parameters.

The Japanese event analysis separately derives the daily-supply denominator implied by announced volume divided by equivalent supply-days. For the two national announcements, the derived values are approximately 0.283 and 0.290 million kilolitres/day. These are **not release rates** and are not treated as observed withdrawals.

The Reserve calibration dashboard tab runs a selected scenario with the translated U.S. SPR inventory, daily release cap, and mobilisation delay. It is kept separate from the existing 18 normalized experiments, whose original assumptions and findings remain unchanged.

See research/reserve_calibration_method.md for equations, day-number convention, caveats, and reproducibility steps.
