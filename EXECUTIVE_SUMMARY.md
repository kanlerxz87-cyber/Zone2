# Executive Summary — AI-Powered Amazon Affiliate Platform (Zone2)

**Status:** platform built, site live, three requested products **unmarketable as supplied** (details below).
**Verified:** 2026-11-13 (UTC). Every figure in this file is transcribed from a source listed in
[`data/sources.json`](data/sources.json); nothing is estimated, averaged, or inferred.
**Live site:** https://kanlerxz87-cyber.github.io/Zone2/

---

## 1. What was asked, and what the inputs actually were

The brief asked for an AI-powered affiliate platform (product research, trend/conversion identification,
pricing/review/competition/commission analysis, SEO article + comparison + buying-guide generation, niche
discovery, link publishing, click/conversion tracking, continuous optimisation, under Amazon Associates
compliance) **for three specific products**:

| # | Link as supplied | Token | Token length | Valid ASIN? | Canonical `/dp/` result |
|---|---|---|---|---|---|
| 1 | `https://link.amazon/B04G1MEwY` | `B04G1MEwY` | 9 | **No** (ASIN is 10 chars) | Page Not Found |
| 2 | `https://link.amazon/B02NbDxp3` | `B02NbDxp3` | 9 | **No** | Page Not Found |
| 3 | `https://link.amazon/B00hJ57DV` | `B00hJ57DV` | 9 | **No** | Page Not Found |

Each submitted short link opened a **different** live Amazon air-fryer listing, and each destination is
*stable*: the same ASIN and page body on every re-fetch. **Correction (2026-11-14): the
`plpRedirect=mhFallback` marker is not evidence of a fallback** — a bare request to a valid ASIN carries the
same marker (control test in `docs/revalidation-2026-11-14.md`, reproduced live this session). What remains
true is narrower: no resolved URL carries an Associates `tag`, no public Amazon document binds the code to
the destination, and the per-link `btn_ref` token changes between days (flag F-20). The three destinations
are therefore recorded as the product each link resolves to, and are **not** established as the requested
products.

> **Corrected 2026-11-14 (session `c6e94e8d`).** This section previously called those three destinations
> "unrelated fallback pages", reasoning from the `plpRedirect=mhFallback` and `lv=shuf` markers and from a
> reported change of page body / `btn_ref` on re-fetch. **That reasoning was tested and does not hold:** a
> bare, untagged request to a *valid* ASIN (`/dp/B08DKYBTPH`) is answered with the real product page and the
> same markers appended; and re-fetching a short link returns the same ASIN, body and `btn_ref` token. The
> destinations are stable and individually tracked — not arbitrary. Evidence and sources:
> [`revalidation/`](revalidation/index.html).

**Consequence — narrower than first reported.** The supplied *codes* are still not ASINs (9 characters;
`/dp/<code>` → Page Not Found), and **no public Amazon document binds a `link.amazon` code to a destination
ASIN**, so the mapping is observed behaviour rather than documented intent. None of the three resolved URLs
carries an Associates `tag` either. Product identity is therefore **not established**, so price, category,
rating, review, competition and commission-band values for these items are **left blank and flagged**,
exactly as the verification rule requires. Writing marketing copy about them *as the requested products*
would have meant inventing an identity — but the three ASINs themselves are real, verified products, and
the attribute tables record them as *the product each link resolves to*.

## 2. Decisions taken

1. **Build the platform, not the prose.** The brief's contradiction (build an automated, verified content
   machine; supply links that resolve to nothing) is resolved in favour of the rule that governs the project:
   *never infer a value*. Every module was built and is runnable; the three product records stay blank.
2. **Identity gate before anything else.** `tools/asin_guard.py` validates the 10-character identifier and
   refuses to repair a short token. This is the boundary the supplied links failed.
3. **Only official ingestion.** The catalog client targets the **Creators API** (PA-API 5.0 is deprecated;
   calls return `403 AccessDenied` per Amazon's own notice) and exits with a machine-readable `BLOCKED` reason
   instead of falling back to scraping.
4. **Compliance as code, not as a disclaimer.** 20 rules read from the Operating Agreement, Program Policies and
   Participation Requirements (plus FTC and Google guidance) are each mapped to an implemented control, and
   `tools/validate_data.py` fails the build when one is violated.
5. **The landing page from the first merged commit is preserved** — its dashboard, honest blank product rows and
   Pages workflow all remain; the subpages, sourced data and tooling are additive.

## 3. Verified economics (Amazon's published figures, not model output)

**Fixed Standard Commission bands** ([source S04](https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ)), transcribed into `data/commission_table.json`:

| Rate | Categories (as published) |
|---|---|
| 10.00% | Luxury Beauty, Luxury Stores Beauty, Amazon Explore |
| 5.00% | Digital Music, Physical Music, Handmade, Digital Videos |
| 4.50% | Physical Books, Kitchen, Automotive |
| 4.00% | Amazon Fire Tablet / Kindle Devices, Luxury Stores Fashion, Apparel, Cloud Cam, Fire TV Edition Smart TVs, Fire TV, Echo, Ring, Watches, Jewelry, Luggage, Shoes, Handbags & Accessories |
| 3.00% | Toys, Furniture, Home, Home Improvement, Lawn & Garden, Pets Products, Headphones, Beauty, Musical Instruments, Business & Industrial Supplies, Outdoors, Tools, Sports, Baby Products, Amazon Coins |
| 2.50% | PC, PC Components, DVD & Blu-Ray |
| 2.00% | Televisions, Digital Video Games |
| 1.00% | Amazon Fresh, Physical Video Games & Consoles, Grocery, Health & Personal Care |
| 0.00% | Gift Cards; Wireless Service Plans; Alcoholic Beverages; Digital Kindle subscriptions; Vehicles – Leasing and Sales; Pet Prescription Medications; restaurant-prepared food; Amazon Appstore / Prime Now / Amazon Pay Places; Coach |
| 4.00% | All Other Categories (default band) |

**Attribution mechanics** ([source S02](https://affiliate-program.amazon.com/help/operating/policies)) that bound every revenue claim:

* A Session starts at the Special Link click and ends at the first of: **24 hours** elapsing, an order placed,
  or the customer clicking another associate's link.
* A cart-add must be completed **no later than 89 days** after the click-through.
* The purchase must be shipped/streamed/downloaded **and paid for within 180 days**.
* Income is paid **~60 days** after the end of the earning month; US minimums: 10 USD deposit, 10 USD gift card
  (2,000 USD cap), 100 USD check (+15 USD fee).
* Bounties: Prime trial/membership **$12.00**, Prime Video trial $2.00, first stream $5.00, stream $0.25.

Nine category groups pay **0.00%**, so the niche filter excludes them *before* ranking — the single most
actionable economics finding in the brief.

## 4. Compliance posture (all four surfaces)

| Surface | Requirement | Control in this repo |
|---|---|---|
| Site | Must state: *"As an Amazon Associate I earn from qualifying purchases."* | rendered in the footer of every generated page; lint `DISCLOSURE_MISSING` |
| Link-level | Disclosure must be clear (`(paid link)`, `#ad`, `#CommissionsEarned`) and conspicuous, in the same medium as the recommendation | `DISCLOSURE_POSITION` + `DISCLOSURE_BANNED` ("commissionable link" is explicitly unclear per FTC) |
| Pricing | Prices/availability only from an Amazon-served link or API data under the License | **no price cell is populated anywhere on the site**; comparison template keeps lowest-new / lowest-used slots sourced-only |
| Content | Content may not be altered, resold or redistributed; no misleading claims; expired promos must be removed | immutable raw API block + response hash; claim-evidence lint; promo expiry gate |
| Linking | Tag required; no offline/email/SMS distribution; sub-tags must never be tied to a specific end user; no double-claiming with another network | static campaign registry only; email/SMS channels absent from the schema; competing attribution params rejected |
| Naming | No Amazon mark (or variant) in any domain, subdomain, tag, or social identifier | site is named *Northstar*; `assert_no_amazon_marks` scans titles, copy and paths |
| SEO | Affiliate links qualified with `rel="sponsored"`; Product/Review structured data rules | builder always emits `rel="sponsored nofollow"`; template JSON-LD constrained |

## 5. What is built (and provably so)

* `tools/asin_guard.py` — identifier validation and URL extraction (refuses to pad a 9-character token).
* `tools/amazon_creators_api.py` — Creators API client: cache, freshness classes, `BLOCKED`/`QuotaExceeded`
  states, hashed raw responses, verbatim-only field normalisation.
* `tools/scoring.py` — opportunity scoring (commission 0.30 / demand 0.25 / competition 0.25 / review 0.20)
  and expected-value maths, returning `INSUFFICIENT_DATA` rather than a default whenever an input is missing.
* `tools/generate_articles.py` — article / comparison / buying-guide renderer with a six-family lint suite;
  refuses unverified entries; a failing draft never reaches `content/published/`.
* `tools/link_builder.py` — compliant Special Link + disclosure emitter with policy refusals.
* `tools/redirect_server.py` + `tools/tracking_schema.sql` — privacy-minimal first-party click counting.
* `tools/optimize.py` — evidence-gated optimiser (needs ≥30 clicks **and** a dated report before any action).
* `tools/build_site.py` — deterministic, network-free generation of 37 pages from the data ledger.
* `tools/validate_data.py` — the deploy gate: per-row sourcing, blank-or-flagged, no-invented-metrics,
  mark scan, disclosure audit, cross-session drift check, broken-link check (868 internal links).
* `tests/test_pipeline.py` — 11 executable checks; **all pass**.

## 6. What is intentionally *not* claimed

No live affiliate link, no published product claim, no traffic/conversion/earnings figure, no "trending
product" or "best niche" ranking, and no automated publishing to a third-party CMS. Each needs an account, a
credential, or a verified product record. The machinery for all of them is present; the inputs are not, and
that distinction is recorded on the site rather than papered over.

## 7. Next actions, in order of leverage

| # | Action | Owner | Unblocks |
|---|---|---|---|
| A1 | Supply the full 10-character ASIN (or complete `amazon.<tld>/dp/` URL) for each item | user | identity → every dependent field → content |
| A2 | Provide Associates account, marketplace and Associates ID/tag | user | compliant tagged links + earnings reporting |
| A3 | Register for the Creators API (needs ≥10 qualifying sales in the past 30 days) | user | real research, offer and browse-node data |
| A4 | Drop a dated Associates report export at `data/associates_report.json` | user | conversion, EPC, revenue-side optimisation |
| A5 | Re-read policy/rate pages each cycle (both carry update dates) | operator | keeps the compliance ledger honest |

## 8. Review notes on the repository

* Branch base was `f577167` (README only). `main` had advanced to `cfc04b1` (PR #1, another session's
  source-first dashboard). A `COORDINATION.md` add/add conflict from `git pull --rebase` was resolved by
  preserving the other session's rows and log verbatim — nothing was discarded.
* Their four cited sources were re-fetched and **confirmed live and on-topic**; their product rows correctly
  assert nothing. Flagged as a gap only: they cited the PA-API overview without the deprecation notice, carried
  no rate table, no attribution window, no per-row sourcing and no category subpages. All four gaps are closed
  here; nothing of theirs was removed.
* Irregularities found are published on the site's **Flagged for Review** page
  (`pages/flags.html`) with source links — 11 items, including the deprecated-API trap and the
  network-allowlist limitation on live verification.

---

## Addendum — second verification pass, 2026-11-14 (session `bbe4ca47`)

The whole repository was re-checked against the live official pages one day after the integration above.
The substantive position is unchanged; three published claims were corrected and two new gaps were closed.

**Held up under re-check (no change needed).** The 11-row commission table, all 9 published bounty rates, the
Trade-In rates, the fine-art and free-Kindle limits, the 24-hour session / 89-day cart / 180-day fulfilment
window, ≈60-day payment, the US payment minimums, the 3-year inactivity rule, the verbatim §5 disclosure
sentence, the Agent Terms, the price/availability display rule, the Creators API prerequisites, the PA-API 5
deprecation and the ASIN-is-10-characters definition all match their official pages exactly. The three supplied
codes still return "Page Not Found" and each link still resolves stably to the same single listing. The
earlier "arbitrary fallback" reading is **withdrawn**: `plpRedirect=mhFallback` is appended to valid ASINs too,
and the destinations do not shuffle between requests.

**Corrected.**

1. **The rate card is public.** The site had said the fixed-rate table "requires Associates sign-in" and left the
   category rate blank. Table 1 is readable without signing in, and publishes both `Kitchen 4.50%` and
   `Home 3.00%` as separate bands. Both are now shown as verified; what remains genuinely unknown is *which*
   band applies to a specific ASIN, which is a catalog fact requiring Creators API — that cell is still blank
   and flagged.
2. **Four compliance controls named files or functions that do not exist** (flag F-16). Corrected to the real
   enforcement points. One rule (email/SMS) also mis-stated a permission as a prohibition and was rewritten to
   the policy as published.
3. **The dashboard's KPI contradicted the ledger** (flag F-17): "3 verified products" against a ledger that
   records 0 of 3 submitted items identified. The KPI now states both numbers explicitly — `0 / 3` identified,
   `3` links verified as resolving stably to one listing each — and the flag count is computed from the data
   instead of typed.

**Newly recorded.** The Emeril manufacturer page contradicts itself on the cooking-preset count (24 in the
description, 25 on the specification tile, "10-in-1" in the feature block), so that value stays unresolved and
is published as a conflict (flag F-19). The CI gate also never walked the 37 generated `pages/` for broken
links and covered only 4 of 6 namespaces for the disclosure/price rule; both gaps are closed (flag F-18).

**Bottom line, unchanged and now stated in one place.** 0 of 3 supplied codes are identified as Amazon
catalog ASINs; each of the 3 links resolves stably to one live listing that is published as an observation,
explicitly not as the requested product.
No product copy, link, campaign or revenue claim is published for the requested items. Every table row on the
live site links an official source or is blank and flagged — now including two new generated
[Verification](https://kanlerxz87-cyber.github.io/Zone2/verification.html) and
[Sources](https://kanlerxz87-cyber.github.io/Zone2/sources.html) pages, which CI rebuilds and diffs against the
ledger so they cannot drift.
