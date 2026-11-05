# Research Source Register

## 1. JODI-Oil

**Organization:** Joint Organisations Data Initiative

**Download page:** <https://www.jodidata.org/oil/database/data-downloads.aspx>

**Local files:**
- `primaryyear2025.csv`
- `primaryyear2026.csv`
- `secondaryyear2025.csv`
- `secondaryyear2026.csv`

**Coverage used:** January 2025–August 2026.

**Purpose:** National production, imports, exports, refinery intake, and inventory analysis.

**Limitations:**
- Missing country observations.
- Different reporting units.
- National trade data does not identify shipping routes.
- Assessment codes and original missing-value markers must be preserved.

## 2. EIA — August 2026 Short-Term Energy Outlook

**Organization:** U.S. Energy Information Administration

**Report:** August 2026 Short-Term Energy Outlook.

**Report URL:** <https://www.eia.gov/outlooks/steo/archives/Aug26.pdf>

**Local file:** `data/raw/other/eia_chokepoint_flows.csv`

**Coverage:** Q1 2025–Q2 2026.

**Purpose:** Quarterly oil flows through eight global chokepoints and the Cape of Good Hope.

**Limitations:**
- Figures are estimates based partly on tanker tracking.
- AIS data can be incomplete or manipulated.
- Quarterly averages conceal within-quarter changes.
- Figures may be revised.

## 3. EIA — October 2026 Short-Term Energy Outlook

**Organization:** U.S. Energy Information Administration

**Publication date:** October 6, 2026.

**Report URL:** <https://www.eia.gov/outlooks/steo/pdf/steo_text.pdf>

**Relevant table:** Table 1, estimated Strait of Hormuz closure-related disruptions in crude oil production.

**Local file:** `data/raw/other/eia_production_shutins.csv`

**Coverage:** February 2026 baseline, March–July average shut-ins, August and September estimates, and aggregate forecasts for Q4 2026 and Q1 2027.

**Limitations:** Shut-ins are estimates, not observed production. Country-level forecasts are not provided. Future-period values are forecasts, not historical observations.

## 4. IEA Middle East Maritime Chokepoints Monitor

**Organization:** International Energy Agency

**URL:** <https://www.iea.org/data-and-statistics/data-tools/middle-east-maritime-chokepoints-shipping-monitor>

**Purpose:** Additional context on maritime traffic and AIS uncertainty.

**Limitations:** AIS signals may be switched off, jammed, or spoofed. Actual transit volumes may be difficult to determine precisely.

## 5. U.S. Department of Energy — Strategic Petroleum Reserve

**Organization:** U.S. Department of Energy, Office of Petroleum Reserves.

**Quick facts:** <https://www.energy.gov/hgeo/opr/spr-quick-facts>

**Frequently asked questions:** <https://www.energy.gov/hgeo/opr/spr-faqs>

**Used for:** Dated SPR inventory and capacity snapshots, nominal maximum drawdown capability, drawdown duration qualification, and time for oil to enter the market.

**Data notes:** DOE reports 411 million barrels at December 31, 2025 and site-level inventory totaling 282.2 million barrels as of October 16, 2026. DOE reports 714 million barrels of authorized capacity and a 4.4 million barrels/day maximum nominal drawdown rate. The FAQ clarifies that 4.4 million barrels/day is available for up to 90 days before the rate declines, and deliveries can begin within 13 days of a Presidential decision.

## 6. Japan — Agency for Natural Resources and Energy / METI

**Stockpile overview:** <https://www.enecho.meti.go.jp/about/special/johoteikyo/government_stockpiled_oil.html>

**March 2026 national stock release:** <https://www.meti.go.jp/press/2025/03/20260324004/20260324004.html>

**April 24, 2026 second release:** <https://www.meti.go.jp/english/press/2026/0424_004.html>

**April 15, 2026 private stockholding obligation notice:** <https://www.meti.go.jp/english/press/2026/0415_002.html>

**Used for:** Aggregate stockpile reference (January 2026), national stock release announcements, and temporary reduction in private stockholding obligations.

**Data notes:** Japan's inventory categories include national, private, and producer-country joint stockpiles. The aggregate domestic stockpiling-days measure is not automatically equivalent to IEA days of net imports. Announced release quantities are not treated as verified completed withdrawals.

## 7. South Korea — Korea National Oil Corporation

**URL:** <https://www.knoc.co.kr/ENG/sub03/sub03_3_3.jsp>

**Used for:** KNOC-operated reserve quantity and capacity.

**Data notes:** KNOC reports 100 million barrels of reserves, excluding international joint stockpiling, and 146 million barrels of capacity as of August 2026. This does not represent every Korean public, obligated-industry, or commercial stock category.

## 8. Germany — Erdölbevorratungsverband (EBV)

**Logistics and stocks:** <https://www.ebv-oil.org/cmse/cms2.asp?sid=60>

**Release procedure:** <https://www.ebv-oil.org/cmse/cms2.asp?sid=64>

**Used for:** Approximate agency-held crude and product stock volume, statutory basis, geographic minimum distribution, ownership/delegation structure, and release procedure.

**Data notes:** EBV reports approximately 20 million tonnes of crude oil and finished products; the page does not give an observation date. Release requires a Federal Ministerial decree specifying products, volumes and period. Allocations are generally apportioned over four calendar weeks; this is not a published fixed daily release rate.

## 9. IEA — Oil Stocks of IEA Countries

**URL:** <https://www.iea.org/data-and-statistics/data-tools/oil-stocks-of-iea-countries>

**Last updated when consulted:** August 12, 2026.

**Used for:** IEA 90-day net-import stockholding obligation, days-of-net-import-cover methodology, crude-equivalent adjustments, unavailable-stock deduction, and treatment of stocks held abroad.

**Important definition:** The IEA obligation can be met through government, agency, and obligated-industry stocks. It is not synonymous with national strategic petroleum reserve inventory.

## 10. IEA — Country oil security frameworks

**Japan:** <https://www.iea.org/articles/japan-oil-security-policy>

**Germany:** <https://www.iea.org/articles/germanys-legislation-on-oil-security>

**IEA emergency response framework:** <https://www.iea.org/about/oil-security-and-emergency-response>

**Used for:** Interpretation of country-level stockholding structures, legal obligations and release procedures.

## Source management principles

- Preserve original downloads.
- Record retrieval dates when downloading new versions.
- Never silently overwrite historical datasets.
- Document manual transcription separately from original downloadable data.
- Distinguish observation, estimate, forecast, announced policy and completed release.
- Retain source definitions and native units before calculating comparable measures.


## 11. U.S. Department of Energy — 2016 Long-Term Strategic Review of the SPR

**Organization:** U.S. Department of Energy.

**Report:** *Long-Term Strategic Review of the U.S. Strategic Petroleum Reserve: Report to Congress* (2016).

**URL:** <https://www.energy.gov/ceser/articles/long-term-strategic-review-ltsr-us-strategic-petroleum-reserve-spr-report-congress>

**Relevant figure:** Figure 15, SPR Maximum Drawdown Rate vs. Duration.

**Used for:** Historical design-reference drawdown schedule: 4.4 million barrels/day during days 1–90; 3.8 during days 91–120; 3.4 during days 121–150; and 1.9 during days 151–180.

**Limitations:** This is a historical design curve, not a dated observation of current effective site-level capability. The simulator's continuation of the final rate beyond day 180 is an explicit extrapolation, not a value published in the figure.

## 12. U.S. Government Accountability Office — GAO-26-106918

**Organization:** U.S. Government Accountability Office.

**Report:** *Energy Security: Congress and DOE Need a Unified Plan to Align Priorities and Investments for the Strategic Petroleum Reserve*.

**Publication date:** May 29, 2026; publicly released June 26, 2026.

**URL:** <https://www.gao.gov/products/gao-26-106918>

**Used for:** Dated assessment of effective SPR drawdown capability, inventory, and operational constraints.

**Data notes:** GAO reports DOE's estimates as of December 2025: effective aggregate drawdown capability of 2.700 million barrels/day against a 4.415 million-barrel/day design rate (61%). This aggregate snapshot is not a time-varying drawdown curve and is not combined with the 2016 DOE design-reference curve in this model.


## 13. Vortexa — Hormuz crude oil and condensate destination estimates (2025)

**Data provider:** Vortexa.

**Published visualization:** The Guardian interactive graphic, *The majority of oil and LNG transiting through the strait of Hormuz is destined for Asian markets*.

**URL:** <https://interactive.guim.co.uk/uploader/embed/2026/03/hormuz_oil_lng_hs/giv-32554JERMFmBib7Ja/>

**Local file:** `data/processed/hormuz_importer_flows_2025.csv`.

**Values transcribed for destination crude oil and condensates, 2025:** China 5.4 mb/d; India 2.1 mb/d; South Korea 1.8 mb/d; Japan 1.7 mb/d.

**Used for:** Destination-specific baseline seaborne crude-oil and condensate flows transiting the Strait of Hormuz in the first importer-country scenario panel.

**Limitations:** The values are shown to one decimal place in a secondary visualization sourced to Vortexa. They do not represent each country's total imports, national import-dependency percentages, total oil products, or LNG. Values are estimates, not official national statistics. The panel preserves this provenance and rounding limitation.

## 14. IEA — Strait of Hormuz factsheet

**Organization:** International Energy Agency.

**URL:** <https://www.iea.org/about/oil-safety-and-emergency-response/strait-of-hormuz>

**Last updated:** February 2026.

**Used for:** Cross-checking the overall 2025 route-flow scale and interpreting alternative export routes. The IEA reports nearly 15 mb/d of crude oil, 5 mb/d of oil products, and 19.87 mb/d total oil exports via Hormuz in 2025. It estimates 3.5–5.5 mb/d of potential alternative crude export capacity through Saudi Arabia's East-West pipeline and the UAE's ADCOP route.

**Limitations:** Shared regional bypass capacity is not equivalent to available replacement imports for any one destination. Operational conditions and export-terminal constraints affect deliverability, and rerouted flows have not been robustly tested at scale. The importer model therefore does not allocate this capacity to individual countries.
