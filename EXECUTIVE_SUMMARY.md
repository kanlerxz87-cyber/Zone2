# Counter Notes — executive summary

**Status recorded:** 2026-11-19 (UTC)

**Publication:** buyer-first product guides, comparisons and articles, with a grouped Project desk for evidence, decisions and suggestions.

**Important:** this release pass rechecked repository data and generated outputs; it did **not** fetch Amazon or manufacturer product pages live.

## The current position

Counter Notes presents source-linked air-fryer listing information and buyer-oriented guides. Three air-fryer destinations are included in the reader-facing product comparison. Two additional supplied-link observations resolve in the repository record to meat-thermometer listings; their intended products are unknown, so they remain separate observations rather than recommendations. Product specifications, disagreements and blank values are kept in the dated source records.

The intent register has **0 of 5 owner-confirmed intended-product mappings**. For the first three records, site-generated Special Links carry the supplied Associates ID, **`shopnow047c-20`**, but their Associates-workflow validation fields remain null. The other two observations have no published purchase link because product intent is unresolved. Neither the tagged site links nor the recorded redirects prove that an order will be attributed or earn a commission. The exact compliance status of the supplied short links remains unresolved in [F-03 / FLG-003](pages/flags.html#F-03); this summary does not call them invalid.

No order, conversion or earnings results are presented. The site does not claim live product discovery, demand/trend scoring, price/review monitoring, or campaign optimisation without the authorized data inputs and reports. The selected tracking ID is preserved; no revenue or performance is inferred from it.

## Supplied links: observed destination is not intended identity

The table reflects the dated observation and product records in [`docs/product-intent.json`](docs/product-intent.json) and [`ledger/products.json`](ledger/products.json). Each supplied short link is cited as the observation source, and each Amazon listing is a retailer reference for its recorded destination—not independent proof that the submitted code was intended to identify that product. The manufacturer links support specifications for the first three product records; they do not establish the brief mapping. All five intended-ASIN fields remain blank. Observation dates below come from the repository record; this pass did not repeat the redirects. The short-link citations are evidence references, not purchase calls to action.

| Supplied code / observation source | Destination recorded on 2026-11-17 | Intended product | Published site link record | Official references |
|---|---|---|---|---|
| [`B04G1MEwY` · supplied link](https://link.amazon/B04G1MEwY) | CHEFMAN dual-basket air fryer, ASIN `B0CDY277D3` | **Unconfirmed — blank** | `shopnow047c-20`; Associates-workflow validation pending | [Amazon destination listing](https://www.amazon.com/dp/B0CDY277D3) · [Chefman manufacturer page](https://chefman.com/products/turbofry-touch-dual-window-air-fryer) · [Amazon Special Link help](https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC) |
| [`B02NbDxp3` · supplied link](https://link.amazon/B02NbDxp3) | Emeril Lagasse French-door air-fryer oven, ASIN `B09B7SB46R` | **Unconfirmed — blank** | `shopnow047c-20`; Associates-workflow validation pending | [Amazon destination listing](https://www.amazon.com/dp/B09B7SB46R) · [Emeril manufacturer page](https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360) · [Amazon Special Link help](https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC) |
| [`B00hJ57DV` · supplied link](https://link.amazon/B00hJ57DV) | Chefman 8-quart air fryer, ASIN `B08DKYBTPH` | **Unconfirmed — blank** | `shopnow047c-20`; Associates-workflow validation pending | [Amazon destination listing](https://www.amazon.com/dp/B08DKYBTPH) · [Chefman manufacturer page](https://chefman.com/products/turbofry-touch-air-fryer-1) · [Amazon Special Link help](https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC) |
| [`B0c8moW59` · supplied link](https://link.amazon/B0c8moW59) | ThermoMaven meat thermometer, ASIN `B0DHZTCNR5` | **Unconfirmed — blank** | No purchase link published; intent unresolved | [Amazon destination listing](https://www.amazon.com/dp/B0DHZTCNR5) · [Amazon Special Link help](https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC) |
| [`B0f3GKalj` · supplied link](https://link.amazon/B0f3GKalj) | CHEF iQ Sense wireless meat thermometer, ASIN `B0DZFD6R9Z` | **Unconfirmed — blank** | No purchase link published; intent unresolved | [Amazon destination listing](https://www.amazon.com/dp/B0DZFD6R9Z) · [Amazon Special Link help](https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC) |

The official Special Link format and account attribution requirements are described in [Amazon's help page](https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC) and [Associates Program policies](https://affiliate-program.amazon.com/help/operating/policies). A tagged URL in this repository is not a substitute for checking the destination and tracking in the enrolled Associates workflow.

## What is published—and what is deliberately withheld

- **Reader experience:** a buyer-first front page, category-organised guides, comparisons and articles; disclosure above the fold and in the footer; a grouped Project menu; and clear routes to questions, missing information and reviewable suggestions.
- **Product evidence:** each displayed factual value is associated with a source in the publication data. Conflicting official statements remain visibly conflicted. Unsupported values remain blank and flagged; the two thermometer destinations are not promoted as air-fryer recommendations.
- **Affiliate links:** the front publication generates its first three product Special Links from the records with the selected ID `shopnow047c-20`. The ID is present; per-link account-workflow validation remains pending. Amazon's current participation requirements should be checked directly before relying on any link ([Operating Agreement](https://affiliate-program.amazon.com/help/operating/agreement); [Program Policies](https://affiliate-program.amazon.com/help/operating/policies)).
- **Performance:** no first-party Associates report is recorded. Clicks, orders, conversions and earnings therefore remain unreported, not zero-valued estimates.
- **Unconnected research:** the repository does not contain authorized Creators API inputs. Amazon's [Creators API introduction](https://affiliate-program.amazon.com/creatorsapi/docs/en-us/introduction), [GetItems reference](https://affiliate-program.amazon.com/creatorsapi/docs/en-us/api-reference/operations/get-items), and [PA-API 5 deprecation notice](https://affiliate-program.amazon.com/creatorsapi/docs/en-us/paapiv5-deprecation) are the official references for the current integration path. No scraping or fabricated demand/trend metric is substituted.
- **Prices and market performance:** no current price, rating, review count, availability, demand, trend, conversion or revenue figure is asserted in this summary. The local Amazon commission schedule is recorded as read on 2026-11-13 and rechecked in the repository verification record on 2026-11-14; it was not fetched live in this pass. See the [official statement](https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ) and verify it again before using a rate. No rate is assigned to any supplied product.

## Review note — older decision-board wording

An older suggestion/requirements record still says no Associates ID was supplied and states that the supplied links cannot attribute sales. That wording predates the current owner-supplied ID and site-generated Special Link records; it is not a finding about the supplied short links' exact compliance status. The current intent register leaves Associates-workflow validation pending and keeps the short-link status unresolved. This integration did not edit that board's source data. Review the [requirements note](board/requirements.html#RQ-22), [suggestion](board/suggestions.html#BS-04), and [current intent register](intent.html); the cross-scope follow-up is recorded as CR-T63-1 in `COORDINATION.md`.

## What still needs to be discovered

1. **Intended products and marketplace.** The owner should confirm each intended ASIN and target marketplace from their own brief or Associates Central record, then enter the listing URL, date and confirmation source in the [intent register](intent.html). Do not fill this from the redirect alone.
2. **Special Link validation.** For each confirmed item, test the generated Special Link in the enrolled Associates workflow and record its destination and tracking result. Amazon documents the link format [here](https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC); the [policies](https://affiliate-program.amazon.com/help/operating/policies) govern attribution.
3. **Product research access.** If automated catalog work is needed, obtain eligible account access and configure the documented [Creators API](https://affiliate-program.amazon.com/creatorsapi/docs/en-us/introduction) inputs. Until then, product discovery and trend scores are not live features.
4. **Performance evidence.** Import a dated first-party Associates report before describing clicks, orders or earnings. The source of truth is the program's [policies and reporting terms](https://affiliate-program.amazon.com/help/operating/policies), not a forecast or a click counter alone.
5. **Open questions and suggestions.** Use the [questions register](questions.html) to find known unknowns and how to investigate them; use [suggestions](suggestions.html) to review proposals. No suggestion is automatically applied.

## Release record

The publication and summary are generated from repository data and checked by their generators. A generator's `--check` confirms output consistency, not factual freshness of remote sources. The release record should be updated with the actual pull-request, Pages build and deployment outcome after integration; no live deployment result is asserted in this document before that verification.
