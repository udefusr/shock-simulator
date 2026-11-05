# Initial Reserve Data Assessment

**Research cutoff:** November 5, 2026.

**Status:** Initial source-backed assessment. This is not yet a harmonized country comparison and must not be used directly as simulation inputs.

## 1. Purpose

The next model-development milestone is to replace arbitrary reserve assumptions with documented evidence about national oil stockholding systems, inventory categories, and emergency release procedures.

The initial comparison covers the United States, Japan, South Korea, and Germany. These cases were selected because official or institutional sources provide useful information about reserve systems and emergency response.

## 2. Initial source findings

### United States

The U.S. Department of Energy describes the Strategic Petroleum Reserve (SPR) as a government-owned crude-oil reserve stored at four Gulf Coast sites.

DOE reports:
- Authorized storage capacity: 714 million barrels.
- Inventory at December 31, 2025: 411 million barrels.
- DOE-stated import protection for that dated inventory: approximately 125 days of U.S. crude-oil net imports.
- Maximum nominal drawdown capability: 4.4 million barrels per day.
- Approximate time from a Presidential decision for oil to enter the U.S. market: 13 days.

The 411-million-barrel inventory and 125-day figure are a December 31, 2025 snapshot, not a November 2026 inventory observation. The nominal drawdown figure is a system capability, not a guarantee that every barrel can be delivered at that rate under all operational conditions.

A newer indexed extract of the same DOE page showed a later inventory figure, while the page content retrieved during this assessment displayed a different dated site inventory. The newer figure is therefore excluded from the structured dataset until the dated primary record can be independently reconciled.

Source: https://www.energy.gov/hgeo/opr/spr-quick-facts

### Japan

METI describes three distinct categories:
1. National government stockpiles.
2. Private-sector stockpiles.
3. Joint stockpiles held in Japan by oil-producing countries.

A METI explainer reports 72.89 million kilolitres of stockpiles (70.06 million kilolitres on a product-equivalent basis) and 248 days of stocks as of the end of January 2026. The published day count follows Japan's domestic stockpiling basis and must not be compared directly with IEA days of net imports without reconciling the denominator and stock definitions.

Japan's 2026 emergency measures provide concrete response-policy evidence:
- In March 2026, METI decided to release national crude-oil stocks equivalent to approximately one month of supply.
- On April 24, METI announced a second national crude-oil release equivalent to approximately 20 days of supply, with an expected volume of about 5.8 million kilolitres.
- METI also reduced the private-sector stockholding obligation by 15 days during the response period.

These are official release decisions/announcements. They should not be treated as proof that the entire announced volume had already been physically delivered on the announcement date.

Sources:
- https://www.enecho.meti.go.jp/about/special/johoteikyo/government_stockpiled_oil.html
- https://www.meti.go.jp/english/press/2026/0316_003.html
- https://www.meti.go.jp/english/press/2026/0424_004.html
- https://www.meti.go.jp/english/press/2026/0415_002.html

### South Korea

KNOC reports that it operates nine stockpiling bases with a combined capacity of 146 million barrels and holds 100 million barrels of reserves, excluding international joint stockpiling reserves.

The indexed KNOC page extract identifies August 2026 for that 100-million-barrel figure. The page text retrieved in the same review displayed February 2026, so the reference date requires confirmation against a dated source record before it is used for time-series calibration.

This is KNOC-operated stockpiling information, not a complete measure of all Korean public and private emergency stocks. No comparable daily release-rate specification was established in this initial source review.

Source: https://www.knoc.co.kr/ENG/sub03/sub03_3_3.jsp

### Germany

Germany's Erdölbevorratungsverband (EBV) states that it currently holds approximately 20 million tonnes of crude oil and finished petroleum products.

The EBV's statutory mission is to maintain stocks based on average crude-oil and petroleum-product imports over a 90-day period. The reserve includes crude oil and products such as gasoline, diesel, light heating oil, and jet fuel.

EBV also states:
- Minimum stocks equivalent to 15 days of supply must be maintained in each of five designated supply areas.
- EBV must own 90% of its stocks itself; up to 10% may be held through delegation arrangements.
- A federal ministerial release decree specifies the products, volumes, and period.
- Allocations are generally apportioned equally over four calendar weeks.

The approximately 20-million-tonne quantity has no specific observation date on the page. The 90-day measure describes the statutory stockholding basis, not a separately measured current days-cover observation. A verified daily maximum release rate was not found.

Sources:
- https://www.ebv-oil.org/cmse/cms2.asp?sid=60
- https://www.ebv-oil.org/cmse/cms2.asp?sid=64

## 3. Why these figures are not directly comparable

The sources describe different stock categories and units:
- U.S. DOE reports a government crude-oil reserve.
- Japan reports a multi-category system including national, private, and joint stocks.
- KNOC reports its own operated reserves and explicitly excludes international joint stocks.
- Germany's EBV reports agency-held crude oil and finished products.

The figures also use different reference dates, product scopes, accounting conventions, and days-cover denominators.

A single column called `strategic_reserves` would therefore be misleading. The data model must preserve the stock category, product scope, reporting date, unit, and source definition.

The IEA 90-day obligation also should not be used as a proxy for current inventory. It is a stockholding commitment based on previous-year average daily net imports, and eligible stocks can include government, agency, and obligated industry stocks. IEA methodology makes adjustments for product conversion, unavailable stocks, and bilateral arrangements.

IEA methodology:
https://www.iea.org/data-and-statistics/data-tools/oil-stocks-of-iea-countries

## 4. Initial data-model decision

The first structured file is:

`data/processed/reserve_profiles_initial.csv`

It preserves:
- Country and responsible institution.
- Stock category.
- Reference date.
- Inventory quantity and native unit.
- Storage capacity and native unit.
- Days cover and its definition, where available.
- Nominal release rate and unit, where available.
- Release lead time and procedure.
- Source URL and quality notes.

Blank fields mean that a comparable value was not established in the reviewed source. They do not mean zero.

## 5. Data gaps to close before calibration

1. Retrieve and archive dated monthly reserve statistics for Japan, including separate national, private, and joint categories.
2. Verify KNOC's August 2026 inventory reference date and find a dated series if available.
3. Obtain a dated EBV annual report or official stock statement to timestamp the approximate 20-million-tonne figure.
4. Retrieve the U.S. DOE/EIA weekly SPR inventory series and reconcile the conflicting page extracts.
5. Find documented release-rate constraints for Japan, South Korea, and Germany, or explicitly leave those parameters uncalibrated.
6. Distinguish physical stocks, legal stockholding obligations, capacity, and deliverability.

## 6. Modelling rule

Do not convert these reserve observations directly into the current normalized model's 200 reserve units or five units/day release limit.

Before country-level calibration, define a consistent model scale and demand denominator. Where the evidence only supports days of net-import cover, model in days of demand or net imports rather than inventing an absolute stock volume.

Strategic crude oil and refined product stocks should not be treated as immediately interchangeable. Refining, product quality, transport, terminal access, and distribution can delay or limit delivery to consumers.

## 7. Interpretation boundary

This initial dataset is a source inventory and research aid. It is not evidence that every recorded barrel or tonne can be released at the nominal rate, nor that inventories are all physically accessible to the same market.

The next phase is source reconciliation and unit harmonization, followed by a documented reserve-response model.
