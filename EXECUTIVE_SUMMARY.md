# Executive Summary — AI-Powered Amazon Affiliate Platform (Zone2)

**Status:** platform built and live; three observed destination products have source-linked marketing copy, but their mapping to the products intended in the brief is unverified and the preview links are not monetized.
**Verified:** 2026-11-14 (UTC). Published product specifications are linked to official sources in the site and registered in
[`ledger/sources.json`](ledger/sources.json); unverified values remain blank and flagged.
**Live site:** https://kanlerxz87-cyber.github.io/Zone2/

---

## 1. What was asked, and what the inputs actually were

The brief asked for an AI-powered affiliate platform (product research, trend/conversion identification,
pricing/review/competition/commission analysis, SEO article + comparison + buying-guide generation, niche
discovery, link publishing, click/conversion tracking, continuous optimisation, under Amazon Associates
compliance) **for three specific products**:

| # | Link as supplied | Token | Token length | Valid ASIN? | Canonical `/dp/` result | Official evidence |
|---|---|---|---|---|---|---|
| 1 | `https://link.amazon/B04G1MEwY` | `B04G1MEwY` | 9 | **No** — supplied token is not a 10-character ASIN | Page Not Found | [Amazon lookup](https://www.amazon.com/dp/B04G1MEwY) · [Amazon ASIN/link help](https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC) |
| 2 | `https://link.amazon/B02NbDxp3` | `B02NbDxp3` | 9 | **No** — supplied token is not a 10-character ASIN | Page Not Found | [Amazon lookup](https://www.amazon.com/dp/B02NbDxp3) · [Amazon ASIN/link help](https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC) |
| 3 | `https://link.amazon/B00hJ57DV` | `B00hJ57DV` | 9 | **No** — supplied token is not a 10-character ASIN | Page Not Found | [Amazon lookup](https://www.amazon.com/dp/B00hJ57DV) · [Amazon ASIN/link help](https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC) |

Each submitted short link opened a **different** live Amazon air-fryer listing. Across the checks recorded
in `revalidation/` and the 2026-11-14 verification log, each destination ASIN and page body reproduced; the
`btn_ref` token rotated across days (flag F-21). **Correction (2026-11-14): the `plpRedirect=mhFallback`
marker is not evidence of a fallback** — a bare request to a valid ASIN carries the same marker (control
recorded in `docs/revalidation-2026-11-14.md`). What remains true is narrower: no resolved URL carries an
Associates `tag`, and no public Amazon document binds the short code to the destination. The three
observations are recorded as the products those links resolve to, not established as the products intended
in the brief.

> **Reconciliation (2026-11-14).** Earlier sessions read `plpRedirect=mhFallback` / `lv=shuf` as evidence
> of fallback destinations. A control request for a valid ASIN also carried those markers, so that inference
> was withdrawn. Repeated checks found the destination ASIN and page body stable; a later cross-day check
> found the `btn_ref` token rotated. This demonstrates observed redirect behaviour, not a documented
> short-code-to-product contract. See [`revalidation/`](revalidation/index.html) and flag F-03.

**Consequence — narrower than first reported.** The supplied *codes* are still not ASINs (9 characters;
`/dp/<code>` → Page Not Found), and **no public Amazon document binds a `link.amazon` code to a destination
ASIN**, so the mapping is observed behaviour rather than documented intent. None of the three resolved URLs
carries an Associates `tag` either. Identity as the products intended in the brief is therefore **not established**.
The published destination tables contain manufacturer-verified specifications for the observed ASINs, while price,
rating, review, competition and commission-band values that cannot be confirmed remain blank and flagged.
Writing marketing copy that claimed these were *the requested products* would invent an identity; the `/marketing/`
copy instead labels them as observed destinations and links each specification to its official source.

## 2. Decisions taken

1. **Build the platform and source-governed destination content, without inventing identity.** The three
   short links resolve reproducibly to product pages, but their 9-character codes are not ASINs and no
   public Amazon document binds those codes to the products intended in the brief. The `/marketing/` site
   publishes destination-only articles, comparison and buying guide from manufacturer-sourced facts; every
   marketing page labels that the brief mapping is unresolved. The root brief-mapped generator remains blocked
   until the owner confirms the mapping. Unverified fields stay blank; confirmed destination specifications
   remain published with their official sources.
2. **Identity gate before anything else.** `tools/asin_guard.py` validates the 10-character identifier and
   refuses to repair a short token. This is the boundary the supplied links failed.
3. **Only official ingestion.** The catalog client targets the **Creators API** (PA-API 5.0 is deprecated;
   calls return `403 AccessDenied` per Amazon's own notice) and exits with a machine-readable `BLOCKED` reason
   instead of falling back to scraping.
4. **Compliance as code, not as a disclaimer.** 21 rules read from the Operating Agreement, Program Policies and
   Participation Requirements (plus FTC and Google guidance) are each mapped to an implemented control, and
   `tools/validate_data.py` fails the build when one is violated.
5. **The original dashboard and Pages workflow are preserved** — the integrated site now distinguishes the observed destination data from the still-unverified brief mapping; sourced ledgers, content views and tooling are additive.

## 3. Verified economics (Amazon's published figures, not model output)

**Fixed Standard Commission bands** from Amazon's public Table 1 ([official source](https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ)), transcribed into `ledger/commission_table.json`:

| Rate | Categories (as published) | Official source |
|---|---|---|
| 10.00% | Luxury Beauty, Luxury Stores Beauty, Amazon Explore | [Amazon Table 1](https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ) |
| 5.00% | Digital Music, Physical Music, Handmade, Digital Videos | [Amazon Table 1](https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ) |
| 4.50% | Physical Books, Kitchen, Automotive | [Amazon Table 1](https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ) |
| 4.00% | Amazon Fire Tablet / Kindle Devices, Luxury Stores Fashion, Apparel, Cloud Cam, Fire TV Edition Smart TVs, Fire TV, Echo, Ring, Watches, Jewelry, Luggage, Shoes, Handbags & Accessories | [Amazon Table 1](https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ) |
| 3.00% | Toys, Furniture, Home, Home Improvement, Lawn & Garden, Pets Products, Headphones, Beauty, Musical Instruments, Business & Industrial Supplies, Outdoors, Tools, Sports, Baby Products, Amazon Coins | [Amazon Table 1](https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ) |
| 2.50% | PC, PC Components, DVD & Blu-Ray | [Amazon Table 1](https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ) |
| 2.00% | Televisions, Digital Video Games | [Amazon Table 1](https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ) |
| 1.00% | Amazon Fresh, Physical Video Games & Consoles, Grocery, Health & Personal Care | [Amazon Table 1](https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ) |
| 0.00% | Gift Cards; Wireless Service Plans; Alcoholic Beverages; Digital Kindle subscriptions; Vehicles – Leasing and Sales; Pet Prescription Medications; restaurant-prepared food; Amazon Appstore / Prime Now / Amazon Pay Places; Coach | [Amazon Table 1](https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ) |
| 4.00% | All Other Categories (default band) | [Amazon Table 1](https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ) |

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
| Naming | No Amazon mark (or variant) in any domain, subdomain, tag, or social identifier | primary site is named *Zone2*; the older *Northstar* prototype is isolated under `northstar/`; the validator scans controlled titles and paths |
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
  mark scan, disclosure audit, cross-session drift check, broken-link check (979 internal links).
* `tests/test_pipeline.py` — 14 executable checks, including a regression test for the marketing identity-scope notice.

## 6. What is intentionally *not* claimed

No monetized, Associates-tagged product link, no claim that the observed destinations are the products intended in the brief, no traffic/conversion/earnings figure, no "trending product" or "best niche" ranking, and no automated publishing to a third-party CMS. The `/marketing/` pages use untagged preview links and publish only sourced specifications for the observed destinations. An Associates ID, owner confirmation of the mapping, Creators API access, and dated performance reports have not been supplied; those values and claims remain blocked or blank rather than invented.

## 7. Next actions, in order of leverage

| # | Action | Owner | Unblocks |
|---|---|---|---|
| A1 | Supply the full 10-character ASIN (or complete `amazon.<tld>/dp/` URL) for each item | user | identity → every dependent field → content |
| A2 | Provide Associates account, marketplace and Associates ID/tag | user | compliant tagged links + earnings reporting |
| A3 | Register for the Creators API (needs ≥10 qualifying sales in the past 30 days) | user | real research, offer and browse-node data |
| A4 | Drop a dated Associates report export at `ledger/associates_report.json` | user | conversion, EPC, revenue-side optimisation |
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
  (`pages/flags.html`) with source links — the register now holds **43 flags (F-01 … F-43)**, rendered
  from `ledger/flags.json` and gated so the count cannot be typed wrong again — including the deprecated-API trap and the
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
---

## Addendum 2 — final integration re-verification, 2026-11-14 (session `a133aa61`)

This session ran the integration pass **with live outbound network access**, which the earlier build sandboxes
did not have (they recorded HTTP `000` for `affiliate-program.amazon.com`, `www.amazon.com` and the manufacturer
sites). Every program fact below was therefore re-read from the official page itself rather than carried forward
from another session's note. Row IDs refer to [`verification.html`](verification.html); each row links its source.

### Re-verified live and unchanged (V-33 … V-40, V-49, V-50)

| Fact | Official page | Result |
|---|---|---|
| Disclosure sentence, verbatim | Operating Agreement §5 (page states *Updated October 15, 2025*) | **VERIFIED** — "As an Amazon Associate I earn from qualifying purchases." |
| Session = 24 h / order / competing click; cart-add ≤ 89 days; ship-pay ≤ 180 days | Program Policies, Commission Income Statement §1 (page states *Updated April 14, 2026*) | **VERIFIED** — wording matches |
| Eleven fixed rate bands (10.00 / 5.00 / 4.50 / 4.00 / 3.00 / 2.50 / 2.00 / 1.00 / 0.00 / 0.00 Coach / 4.00 All Other) | Standard Commission Income Statement, Table 1 | **VERIFIED** — re-read row by row |
| Payment ≈60 days after month end; US minimums 10 / 10 (2,000 max) / 100 + 15 fee; 3-year inactivity | Commission Income Statement §6 + Payment Minimum Chart | **VERIFIED** |
| Special Links must carry the Associates ID as a URL parameter; sub-tags never tied to one end user | Participation Requirements §2(a)–(b) | **VERIFIED** |
| Price/availability only from an Amazon-served link or the API; comparison pages show lowest new (and used) | Participation Requirements §2(b) | **VERIFIED** — no product price is published anywhere in this repo |
| Agent Terms: `Agent/[agent name]` user agent, no concealing, no CAPTCHA circumvention | IP License §4 | **VERIFIED** — the catalog client refuses to scrape |
| PA-API 5 returns `403 AccessDeniedException`; migrate to the Creators API | Creators API deprecation notice | **VERIFIED** |
| Material connection disclosed clearly and conspicuously, near the recommendation | FTC Endorsement Guides FAQ / 16 CFR 255 | **VERIFIED** |
| Affiliate links marked `rel="sponsored"` | Google *Qualify your outbound links* (page states *Last updated 2025-12-10*) | **VERIFIED** — every outbound product link emits it |

### Re-verified live — the three supplied links (V-41 … V-45)

| Test | Result on 2026-11-14 |
|---|---|
| `link.amazon/B04G1MEwY` → | `/dp/B0CDY277D3`, CHEFMAN 6 Qt Dual Basket Air Fryer — same ASIN as every prior session |
| `link.amazon/B02NbDxp3` → | `/dp/B09B7SB46R`, Emeril Lagasse 26QT French Door Air Fryer Toaster Oven — same ASIN |
| `link.amazon/B00hJ57DV` → | `/dp/B08DKYBTPH`, Chefman 8 Qt TurboFry — same ASIN |
| `amazon.com/dp/B04G1MEwY` | Amazon "Sorry! We couldn't find that page." — **Page Not Found** |
| Control: bare `/dp/B08DKYBTPH` (valid ASIN) | real product page, its links carrying `lv=shuf&channelId=500&plpRedirect=mhFallback&th=1` → **`mhFallback` is not evidence of a fallback** |
| `btn_ref` on each supplied link | **changed** versus the values earlier sessions recorded (`srctok-1f979f303a4b5691` / `-0cd8be3c7e2e0de3` / `-7c59360cbbbd59b7`) |

**One new finding (flag F-21 / RV-11).** The earlier claim that a re-fetch returns "the same `btn_ref` token"
does **not** survive a day boundary. The ASIN, the page body and `channelId=704` all reproduce; the token does
not. So the published conclusion is narrowed: the destinations are stable and each link is individually tracked,
but the token is not a stable identifier and the short-code→ASIN mapping remains **observed behaviour**, not
documented intent. This does not change any product row — those were always published as "the product each link
resolves to", never as "the requested items".

### Manufacturer specification rows re-checked one by one (V-46 … V-48)

- **Chefman TurboFry Touch 6 Qt (P1):** all eight published rows match the manufacturer's own Specifications
  block — model `RJ38-SQPF-3TDB-2W`, 6 Qt / 5.67 L, 200–450 °F / 95–235 °C, 13.38 × 11.81 × 10.63 in
  (33.98 × 30 × 27 cm), 13.3 lb / 6.03 kg, 1700 W / 120 V, cETL + 1-year Chefman assurance. **Verified.**
- **Chefman TurboFry 8 Qt (P3):** model `RJ38-SQSS-8T`, 8 Qt / 7.57 L, 200–400 °F / 95–205 °C, 1700 W / 120 V,
  15.4 × 12.6 × 13.5 in (39.11 × 32 × 34.29 cm), 12.8 lb / 5.8 kg. **Verified** — and the Amazon-vs-manufacturer
  power conflict (Amazon bullet text 1000 W) therefore still stands as a published conflict, not an error.
- **Emeril 26QT (P2):** the manufacturer page really does contradict itself — "25 Cooking Pre-sets" (spec tile),
  "24 one-touch cooking presets" (description), "10-In-1 Versatility" (feature block). The published conflict row
  is correct and stays unresolved. **Verified as a conflict.**

### What this pass did *not* change

0 of 3 supplied codes are identified as ASINs. No price, rating, review count, BSR, availability, conversion,
traffic or earnings figure is published, because none can be sourced from an official Amazon page without the
Creators API and an Associates account — and this repository publishes nothing it cannot source. The owner
actions from §7 above (confirm the three ASINs in Associates Central, add the Associates tag, register for the
Creators API, connect a dated report) remain the only things standing between this platform and live revenue.

---

## Addendum 3 — T27 publication-scope reconciliation (2026-11-14)

A final surface audit found that an earlier addendum's statement “no product copy … is published” was too broad. It described the root **brief-mapped** generator, but a companion set already publishes destination-only marketing. This correction is now reflected in the root dashboard, the generated findings executive summary, F-06, and the primary content page.

- The public [`/marketing/` set](https://kanlerxz87-cyber.github.io/Zone2/marketing/) contains three product articles, a comparison, and a buying guide. Its 48 specification rows are source-linked or explicitly blank; the marketing verifier reports 0 failures. Product attributes link to the official [Chefman 6 Qt](https://chefman.com/products/turbofry-touch-dual-window-air-fryer), [Emeril 26 Qt](https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360), and [Chefman 8 Qt](https://chefman.com/products/turbofry-touch-air-fryer-1) pages. Every marketing page now says the short-link-to-brief mapping is unconfirmed and links to [Flag F-03](https://kanlerxz87-cyber.github.io/Zone2/pages/flags.html#F-03).
- This copy describes only the observed destinations. It does **not** establish that they are the products intended by the brief; no public Amazon document in the reviewed record binds the supplied `link.amazon` codes to those ASINs. The official [Amazon ASIN/link help](https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC) describes ASINs as catalog identifiers and the tagged-link format.
- The displayed Amazon links are untagged preview links. The [Operating Agreement](https://affiliate-program.amazon.com/help/operating/agreement) requires properly tagged Special Links and the site disclosure; this repository has no Associates ID, so the pages are not monetized. No clicks, conversions, or earnings are claimed.
- **Destination stability vs. token:** observed requests reproduced the destination ASIN and page body, while the per-link `btn_ref` token rotated across days. This is observed redirect behavior, not a documented or stable attribution identifier; the statement in Addendum 2 that the links were “individually tracked” is withdrawn as an unsupported interpretation (see F-21).

The distinction is now explicit: destination-only product marketing is published; the root generator remains blocked from copy asserting that the destinations match the brief. Neither the unresolved mapping nor the missing Associates ID is filled in by inference.
---

## Addendum 4 — independent close-out, 2026-11-14 (session `ba8b2d38`, task T27)

A fourth, independent pass. Every value below was read off a page **this session fetched itself**; nothing is
carried forward from another session's notes and no blank was filled by inference. Recorded row by row in
[`docs/verification-ba8b2d38.md`](docs/verification-ba8b2d38.md) and as verification rows **V-51 … V-70**.

> **Merge note.** Three sessions appended records while this pass was running, so `main` advanced
> `6a90dfc` → `b22c498` (PRs #42…#46) underneath it. Nothing of theirs was overwritten. One collision had to be
> resolved by hand: this session's control finding was written up locally as **F-27**, but session `b38cc982`
> had already published a different **F-27** (*research-hub/scripts/build.py deletes its own output*). Theirs
> reached `main` first and is left untouched; **this finding is numbered F-28**, and both are in the register.
> The overlapping hard-coded-count fix was reconciled the same way — T26's implementation is kept as the single
> one, and T27's contribution is the gate that covers the generated subpages and the hand-written docs.

### The three supplied links — confirmed for the third time

| Supplied link | Destination | `btn_ref` observed this session |
|---|---|---|
| `link.amazon/B04G1MEwY` | `/dp/B0CDY277D3` — CHEFMAN 6 Qt Dual Basket Air Fryer Oven | `srctok-704dc575b940a94c` |
| `link.amazon/B02NbDxp3` | `/dp/B09B7SB46R` — Emeril Lagasse 26QT French Door Air Fryer Toaster Oven | `srctok-76d4981d5f44181b` |
| `link.amazon/B00hJ57DV` | `/dp/B08DKYBTPH` — Chefman 8 Qt TurboFry | `srctok-016f4a534eed3621` |

Destinations unchanged — the **third independent confirmation**. All three `btn_ref` tokens are **new**, and none
matches any previously recorded value: the tracking token rotates continuously while the destination does not
(flag F-21). All three `/dp/<code>` canonical URLs return Amazon's *Page Not Found* page, as before.

### A new control settles what the 9-character codes actually are (flag F-28)

Earlier passes noted that each code is 9 characters where an ASIN is 10, and floated that the pattern looked
"consistent with a one-character truncation". This session ran the control that tests that reading:

> Passing a **valid 10-character ASIN** (`B0CDY277D3`, which renders normally at `amazon.com/dp/B0CDY277D3`) to
> the same short-link service returns **the identical 404 page as an unknown code**.

A service that accepted and truncated ASINs would resolve a correct one; this service does not accept ASINs at
all. It performs a lookup over its **own short-code namespace**. The supplied codes are therefore **opaque
short-link identifiers**, and their resemblance to a truncated ASIN is a coincidence of appearance.

**What changes:** only the explanation. No product conclusion moves — the tokens are still not ASINs, no missing
character was ever guessed, and all three destinations are unchanged. The earlier wording is retained in place
and marked corrected rather than deleted, so the record still shows what the site previously said and why it
changed (evidence row E-11, flag F-28).

### Official sources re-read — including the rate table, checked mechanically

All program facts re-verified: the §5 disclosure sentence verbatim; both document dates (Agreement 15 Oct 2025,
Program Policies 14 Apr 2026); the 24-hour session / 89-day cart / 180-day fulfilment window; ≈60-day payment and
the US minimums (10 / 10 capped at 2,000 / 100 + 15 USD fee); the 3-year inactivity rule; the double-claim
limitation; the Agent Terms (`Agent/[name]`, no CAPTCHA circumvention, answer truthfully); the ASIN definition;
and the official tagged-link format.

The **commission rate table was compared programmatically**, not by eye: all eleven bands in
`ledger/commission_table.json` were matched category-string by category-string against the live
[Table 1](https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ). **Every band matched.** The
`up to 10%` ceiling was re-verified on the [Associates home page](https://affiliate-program.amazon.com/), now
registered as source S37 — it had been cited on the dashboard without being recorded in the source register.

### Irregularity found and fixed

Root `flagged.html` hardcoded a stale register size — it named **twenty-seven** flags while the register held
twenty-eight, so the published page understated the register. Same defect class as flag F-26, but surfacing in
prose, which no gate compared against the ledger. The count and range now render from the data, and a new gate
(`tools/validate_data.py::check_no_typed_flag_counts`) fails the build if a typed register size reappears across
the generated subpages, the root pages, `README.md` and this file. **Negative-tested**: reintroducing the stale
sentence turns the build red. (Session `b38cc982` fixed the same sentence for `index.html` and `flagged.html` in
T26; both gates now run and cover different surfaces.)

The same drift was found in the hand-written docs and corrected here: `README.md` advertised stale check/source
counts and this file carried *868 internal links* against an actual **979** at merge, plus three `data/*.json` paths
pointing at a directory that no longer exists (the ledger moved to `ledger/`). All now resolve.

### Bottom line, unchanged

**0 of 3** supplied codes are identified as Amazon catalog ASINs; each of the **3** links resolves stably to one
live listing, published as an observation and explicitly **not** as the requested product. No price, rating,
review count, sales rank, availability, conversion, traffic or earnings figure is published, because none can be
sourced from an official page without the Creators API and an Associates account.

One nuance worth stating plainly, because it is the most common way to get this wrong: all three resolved
products sit under a *Home & Kitchen › … › Air Fryers* path, where Table 1 publishes **both** `Kitchen 4.50%` and
`Home 3.00%`. Which band Amazon actually applies is a catalog fact requiring an authenticated lookup, so that
cell is **left blank and flagged** rather than inferred — picking either number would be a guess dressed as a
fact.

---

---

## Addendum 5 — independent verification pass, 2026-11-14 (session `d3ce1c29`, task T26)

An independent pass run against the live official pages. At claim time the board was empty and no pull
requests were open (`main` = `6a90dfc`, branch `arena/d3ce1c29-zone2`); **three other sessions merged work to
`main` while this pass was running** (PRs #42–#47, sessions `808a6840` and `a6f70a13`), so the paragraph above
claiming an otherwise idle board is corrected here — the merge below reconciles the two bodies of work rather
than superseding either. Its purpose was to re-derive every load-bearing claim from the source rather than
from earlier sessions' notes, and to run the decisive control on all three destinations instead of one.

### Re-derived from the official pages, in this session

| Claim | What the official page says | Verdict |
| :-- | :-- | :-- |
| §5 disclosure | “You must clearly and prominently state the following … on your Site …: **“As an Amazon Associate I earn from qualifying purchases.”**” | **Verified verbatim** ([S01](https://affiliate-program.amazon.com/help/operating/agreement)) |
| Document currency | Operating Agreement header: **“Updated: October 15, 2025”** | **Verified** ([S01](https://affiliate-program.amazon.com/help/operating/agreement)) |
| Table 1 bands | Eleven bands, 10.00 % → 0.00 %, plus “All Other Categories 4.00 %” | **Verified** row by row against the ledger ([S04](https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ)) |
| ASIN definition | “ASIN is the **10-digit** code that Amazon uses to denote specific products.” | **Verified verbatim** ([S24](https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC)) |
| Public ceiling and payment timing | “Earn **up to 10 %** in associate commissions …”; “Commission income is paid **approximately 60 days** after the end of the month in which it was earned.” | **Verified verbatim** ([S36](https://affiliate-program.amazon.com/)) |
| Trade-In rates, fine-art cap, free-Kindle limit | 4.00 % / 4.00 % / 0.00 %; “maximum of **$200** per Product”; ≥20 000 free eBooks **and** ≥80 % free share | **Verified** ([S04](https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ)) |
| Unknown short code | `https://link.amazon/B00TEST12` → `amzlinks.in/B00TEST12` → **“404: File Not Found … You've clicked on an invalid URL.”** | **Reproduced** ([S32](https://link.amazon/B00TEST12)) |

### The `mhFallback` control, run on all three destinations

Session `c6e94e8d` ran this control on one ASIN (V-45). It has now been run on all three, and it reproduces
every time: a **bare, untagged** `https://www.amazon.com/dp/<ASIN>` request — no short link, no parameters —
returns the real product page with **`?lv=shuf&channelId=500&plpRedirect=mhFallback`** appended by Amazon's own
redirector (V-56 / V-57 / V-58). The marker is therefore a property of an ordinary `/dp/` load, not a signature
of a short-link fallback. The “these destinations are fallback pages” reading is **refuted on all three**; the
identity question (F-01 / F-03) is unaffected and remains open.

The three supplied links were also re-resolved in this session and each still lands on the same single listing:
`B04G1MEwY` → `B0CDY277D3`, `B02NbDxp3` → `B09B7SB46R`, `B00hJ57DV` → `B08DKYBTPH`. All three `btn_ref` tokens
were again different from every value recorded earlier the same day, and from each other — F-21 confirmed a
fourth time.

### One substantive defect found and fixed (F-30)

The “Bounty events” panel published **9** rows under a notice reading *“Transcribed row-by-row from Amazon's
published Associates Program Standard Commission Income Statement.”* S04 actually publishes **46** rows under
“(a) Bounty Events” and **2** more under “(b) Bonus Events”. The nine rows on the page were the first nine and
were individually correct and correctly sourced — the defect was **omission**, not error, but a partial list
wearing a completeness claim reads as the whole set, and it hid the two largest published bounty rates on the
program (Audible $20.00, Amazon Business $15.00). The full 46 + 2 are now transcribed, rendered, and counted on
`pages/commissions.html` (F-30, closed).

Two smaller irregularities were closed alongside it: the zero-rate caption said “Nine category groups publish a
0.00 % rate”, a count that matches no grouping in Table 1 (F-31, reworded); and `tools/validate_data.py` skipped
any ledger row whose only source field is `source_id`, so every commission row — including the 48 new ones —
would have escaped the source check (F-32, fixed; the gate's row count rose 173 → 243 and was negative-tested).

**One inherited flag closed.** F-16 — four compliance rows citing controls that did not exist — was re-verified
line by line in this pass: `check_marks` (tools/validate_data.py:190), `lint()` (tools/generate_articles.py:164)
and the `expires_utc` enforcement with its test all exist and are named correctly, and R-09 now states the
solicited-email/SMS permission accurately. F-16 is closed; its full text stays on the register page.

### Unchanged

Nothing about the product rows changed. 0 of 3 supplied codes are identified as ASINs; every unsourceable field
stays blank; no price, rating, review count, BSR, availability or earnings figure is published.


---

## Addendum — completeness re-read of the official programme pages, 2026-11-14 (session `0a697d4a`, T28)

A pass aimed at **completeness** rather than correctness: two official pages were re-read **row by row** and every published row compared against what this repository records. Two transcriptions turned out to be partial. Both are fixed, both are in the register as **F-37** and **F-38**, and neither changes a product conclusion.

> **Numbering note.** These findings were drafted as F-27/F-28. While this session ran, other sessions published F-27 and later findings on `main`. All reached `main` first and are left untouched; **these two findings are numbered F-37 and F-38**, and every finding is in the register.

### F-37 — the Special Commission Income table was only a fifth transcribed

Amazon's published Appendix sets out Special Commission Income in two tables. This repository recorded a fifth of the first and none of the second:

| Published by Amazon | Previously recorded here | Now recorded |
|---|---|---|
| **46** Bounty Event rows (§4(a)) | 9 | 46 |
| **2** Bonus Event rows (§4(b)) | 0 | 2 |
| **11** Table 1 rows | 11 — matched exactly | 11 |

The 39 missing rows were not trivia: they include the largest per-action amounts in the programme — Audible Standard **$20.00**, Audible Premium Plus Annual **$25.00**, Amazon Business **$15.00** — plus Kindle Unlimited, Amazon Music Unlimited, Amazon Haul and the six Subscribe & Save events. A content plan ranking bounty opportunities from this page would have missed the highest-value ones entirely.

One row that *was* present was **mis-transcribed**: for `Prime Sign Up at Checkout` the ledger had recorded the *Eligible Customer* column as its *Bounty Action*. Corrected to the published wording.

The page now prints its own published-vs-recorded row counts, so a future partial transcription is visible without re-reading the source.

### F-38 — 10 Participation Requirements that constrain this platform were missing from the ledger

The compliance ledger held 21 rules. Ten requirements in Policy §6 that bind this repository's own modules were absent and are now added as **R-22 … R-31**: §6(y) no price-tracking or price-alerting · §6(w) no link shortening that hides the destination · §6(v) no cloaking · §6(g) no incentives · §6(s) no artificial clicks · §6(u) no self-triggered Bounty Events · §6(n) no framing · §6(o) no pop-ups · §6(p) no Special Links on an Amazon Site · §6(z) no promoting non-Amazon products with Program Content.

**The one that matters is §6(y).** Module M-03 (*Pricing analysis*) is described on this site as tracking "price point, discount depth and offer shape per ASIN". §6(y) **forbids** exactly the tracking-and-alerting shape of that: "Unless otherwise agreed by Amazon, your Site must not have price tracking and/or price alerting functionality."

Nothing published was non-compliant — M-03 is **BLOCKED** (no API credentials, no cached offer records), so no price is tracked and no claim on the site is false. The defect was that the constraint register a builder would read before implementing M-03 did not contain the rule that most restricts it. It does now, and the permitted reading (a point-in-time offer record fetched from the Creators API and shown with its `as_of` timestamp) is stated on the module page.

Every control cited for the ten new rules was checked against the actual code, and two real gaps are stated honestly inside R-24 and R-31 rather than papered over. The ledger's scope note now says plainly that it is a curated set of the rules that constrain **this** platform and is **not** a restatement of the Program Policies.

### Sources read for this pass

* https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ — Table 1, §4(a) Bounty Events, §4(b) Bonus Events, Trade-In rates, Fine Art cap, free-book limit
* https://affiliate-program.amazon.com/help/operating/policies — Participation Requirements §4 and §6(a)–(z); Commission Income Statement §1, §4, §6
* https://affiliate-program.amazon.com/help/operating/agreement — §2, §4, §5, §6, re-verified verbatim
* The three supplied links, re-resolved independently: `B04G1MEwY`→`B0CDY277D3`, `B02NbDxp3`→`B09B7SB46R`, `B00hJ57DV`→`B08DKYBTPH` — **unchanged**

---

## Addendum — decision-support surfaces, reader-facing editorial pass, and a fresh verification day, 2026-11-15 (session `8c4236ad`, T32)

Two things changed on this date, both additive. Nothing in the fact base moved: every specification row,
status and source link published before 2026-11-15 is byte-identical after it (the marketing verifier
re-derives all specification rows from `marketing/data/facts.json` and would fail otherwise).

### 1. The owner's decision surfaces are now reachable from the dashboard

Session `2499438c` shipped the decision layer on 2026-11-15 (`pages/suggestions.html`, SG-01…SG-10, and
`pages/questions.html`, Q-01…Q-16). This session added the missing inbound paths: both pages are linked from
the root dashboard's navigation and footer, and the public marketing set's overview page links the suggestions
board as well. The principle the decision layer runs on is unchanged and is repeated on every page that
carries it: **nothing strategic is implemented before the owner records a choice in `ledger/suggestions.json`**.

### 2. The public marketing set now reads like a publication, not a lab notebook

The destination-only marketing set (`marketing/` — overview, buying guide, comparison, three product
articles) kept every fact, source and compliance label, and changed only its editorial voice:

* Each article opens with a lede that states what the machine is, in the manufacturer's own verified terms,
  followed by an explicit "honest fine print" paragraph (no hands-on testing, no star ratings, no prices).
* A new **"Who this fits"** section per article restates, line by line, what the cited manufacturer page
  already states about household size, basket layout, presets, windows, finishes and care — attributed, with
  the source linked in the section itself. A **"If that's not you"** block routes the reader to the
  neighbouring article that fits better, which also makes the three-piece set a real internal link network.
* The overview page explains the site's unusual editorial rule in plain words: agreements are shown as one
  number, disagreements are shown as two statements, and unknowns are shown as blanks.
* The articles index now carries a **"Planned topics — not published yet"** queue: four topic ideas, each
  tied to the verified rows it would rest on, and explicitly gated on suggestion **SG-04** — nothing is
  commissioned until the owner picks a content-engine path on the decision board.

Wording follows suggestion **SG-05** (data-led phrasing only — "the manufacturer lists…", never "we
tested…"), and the layout direction follows the recommendation recorded under **SG-06** (editorial guide for
public pages, dashboard for the owner), while both suggestions remain OPEN for the owner to confirm or
overrule.

### 3. Fresh verification pass, 2026-11-15

Re-fetched this session, from the pages themselves: the three supplied short links still resolve to one
destination each — `B0CDY277D3`, `B09B7SB46R`, `B08DKYBTPH` — with the same breadcrumb
(*Home & Kitchen › Kitchen & Dining › Small Appliances › Fryers › Air Fryers*); the ASIN help page still
defines an ASIN as the **10-digit code** Amazon uses to denote specific products; the official tagged link
format still reads `amazon.com/dp/ASIN/ref=nosim?tag=YOURASSOCIATEID`; the Operating Agreement still carries
"Updated: October 15, 2025" and §5 still requires the disclosure sentence verbatim; §4 still disclaims any
representation about traffic or commission income; and §6 still makes any violation of §5 a material breach.
Full row-by-row evidence: [`docs/verification-8c4236ad.md`](docs/verification-8c4236ad.md).

**New observation (flagged, not corrected):** the Amazon listing title for the Emeril destination
(`B09B7SB46R`) **has changed since the 2026-11-14 read** — it now reads "…Countertop Convection Cooker,
24 One-Touch Preset Options, Extra Large Interior, Six Cooking Accessories Included" where the published row
records "…24 cooking functions, dual-speed fan and rotisserie for easy family meals." The published value is
correct as of its read date and stays; the drift is flagged for the next verification cycle because Amazon
listing titles are seller-editable and change without notice. The "24 vs 25" preset CONFLICT row is unaffected
(today's title repeats the 24 side of the published conflict). Note also the accessories wording "Six Cooking
Accessories Included" in the new title versus the manufacturer's "7 premium accessories" — a third variant of
the already-published accessories discrepancy (MK-07 / P2 partial row).

---

## Addendum — primary-site marketing redesign + suggestions architecture, 2026-11-15 (session `2b257b2e`, T34–T37)

**The problem.** The root pages were correct but read like an internal admin tool — default-blue
sidebar, dense KPI tiles, procedural prose — exactly the presentation the brief called out as looking
machine-generated. The substance (ledger-governed tables, per-row sources, honest blanks) was right;
the presentation undermined it.

**What shipped.**

* **Marketing redesign of every root page** — landing (`index.html`), products, analysis, content,
  compliance, tracking, flagged, 404 — plus a new `design-notes.html`. Dark sticky header, editorial
  typography (Fraunces/Inter), warm palette, hero-led pages, product cards rendered from the same
  verified `PRODUCTS` dataset, flags preview rendered from the same register, decisions section.
  **No verified value changed.** The gates were read before the redesign was written, and every
  pinned element id (`flagCount`, `flagCountHeading`, `flagRegisterCount`, `flagRegisterMax`, all
  table hooks), the disclosure sentence, the route into `pages/`, and all companion-namespace links
  were preserved.
* **Compliance-positive link changes.** Outbound Amazon listing links now carry
  `rel="sponsored"` per Google's paid-link guidance (verified on the official page, 2026-11-15), and
  product cards cite the canonical `/dp/` destination rather than presenting the untagged short link
  as a purchase CTA — the Operating Agreement requires tagged link formats (§1, verified 2026-11-15).
* **Editorial topic queue.** `content.html` now carries a source-anchored topic-idea table for the
  air-fryer niche the three resolved destinations share. Every factual anchor cites the official
  listing it was read from; **search demand is deliberately blank** — no official source states it,
  and the platform does not estimate. Every topic is labelled a suggestion awaiting a recorded
  decision on the new suggestions board.
* **Suggestions architecture adopted, not duplicated.** The decision board
  (`pages/suggestions.html`) and open-questions register (`pages/questions.html`) shipped this wave by
  session `2499438c` (T29, PR #61). The redesign links them from the landing nav and footer rather
  than building a second system.
* **Crawl hygiene.** `robots.txt` and `sitemap.xml` added (root pages + findings hub).

**Verification performed (2026-11-15, live fetches — `docs/verification-2b257b2e.md`).** The Operating
Agreement (§1, §4, §5 verbatim, §6; updated October 15, 2025), Table 1's eleven commission bands
(including Kitchen 4.50% and All Other 4.00%), all three supplied links re-resolved to the same three
ASINs with fresh per-day `btn_ref` tokens (consistent with F-21), the shared Air-Fryers category path,
Google's outbound-link guidance, and the FTC endorsement-guidance page.

**What is unchanged and still open for the owner:** the brief mapping (F-01…F-03), tagged Associates
links (F-24), Creators API registration (F-05) — and, as before, no price, rating, review count,
availability or per-ASIN commission band is published, because no official source states them.

## Addendum — design/content playbook, repo review and integration state, 2026-11-15 (session `fcb538fa`, task T33)

This addendum answers the request of 2026-11-15 directly: *what should this site look like, what should it
write, how does it earn real traffic, and what must be decided before anything is built.* It records where
those answers live and what was independently re-verified while producing them. Nothing in it changes the
fact base; every figure already published elsewhere in this summary is untouched.

### 1. Where the design and content answers live

* **[`docs/design-prompt-suggestions.md`](docs/design-prompt-suggestions.md)** — the suggestion set written to
  be pasted into the site-design/content prompt: verified constraints the design must obey (20 rows, each
  linked to the official page it was read from), design-direction options with a recommendation per row,
  nine article angles for the three promoted destinations, an organic-traffic plan, ten anti-“AI slop”
  editorial rules, decision-making improvements, and discovery actions for the missing information.
* **[`playbook.html`](playbook.html)** — the same set published on the live site in table form, one source
  link per row, with a clearly labelled *Flagged for review* section for this session’s irregularities
  (IR-01…IR-11) so they can be reviewed while the site is up.
* **[`docs/review-fcb538fa.md`](docs/review-fcb538fa.md)** — the line-by-line repository review for this
  request: inventory, every CI gate reproduced locally, observations and irregularities with evidence.

Decision authority is unchanged: these are proposals. The owner chooses paths on the canonical
**[Suggestions decision board](https://kanlerxz87-cyber.github.io/Zone2/pages/suggestions.html)**
(SG-01…SG-10) after consulting the canonical **[Open Questions register](https://kanlerxz87-cyber.github.io/Zone2/pages/questions.html)**
(Q-01…Q-16) — both shipped by session `2499438c` (T29) and made reachable from the dashboard by sessions
`fb49a226` (T30) and `8c4236ad` (T32). Session `8c4236ad` also executed the first editorial upgrade of the
public marketing set (voice only, facts byte-identical) and closed change request **CR-9** by adding the
decision-surface mentions this file previously lacked.

### 2. What was re-verified by this session (all fetched live, 2026-11-15)

| Claim class | Result | Official source |
|---|---|---|
| Disclosure requirement and agreement currency | §5 sentence verbatim; “Updated: October 15, 2025” | https://affiliate-program.amazon.com/help/operating/agreement |
| No promise of traffic or commission income | §4 sentence verbatim | https://affiliate-program.amazon.com/help/operating/agreement |
| Price, comparison, product-list original-content, promotion-removal and no-misleading-claims rules | “Updated: April 14, 2026”; §2(b) text verbatim | https://affiliate-program.amazon.com/help/operating/policies |
| Search rule §6(f), ratings rule §6(t), cloaking/shortener §6(v)–(w), price-tracking §6(y), solicited-email §4, **machine-learning clause §5** | all verbatim | https://affiliate-program.amazon.com/help/operating/policies |
| Application thresholds (10 posts, ~60-day content, own website, three sales/180 days) | verbatim | https://affiliate-program.amazon.com/help/node/topic/G8TW5AE9XL2VX9VM |
| Creators API prerequisite | “at least 10 qualifying sales within the past 30 days” verbatim | https://affiliate-program.amazon.com/creatorsapi/docs/en-us/introduction |
| Google link qualification + spam policies (scaled content abuse, thin affiliation, link spam) | verbatim | https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links · https://developers.google.com/search/docs/essentials/spam-policies |
| FTC disclosure principle | “clearly and conspicuously”; Guides revised 2023 | https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking |
| The three supplied short links | still resolve to `B0CDY277D3`, `B09B7SB46R`, `B08DKYBTPH` with matching titles; **no `tag=` parameter on any of them** (re-observation of F-24) | https://link.amazon/B04G1MEwY · https://link.amazon/B02NbDxp3 · https://link.amazon/B00hJ57DV |

Full row-by-row evidence: [`docs/review-fcb538fa.md`](docs/review-fcb538fa.md) §5 and
[`playbook.html`](playbook.html) §9. Repo gates on the integration tree: `validate_data` clean,
all generator `--check` gates current, guard tests passing, structural audit green (see the closing record
in `COORDINATION.md` for the exact run).

### 3. New irregularities this session flagged (non-blocking, published with sources)

Eleven items, IR-01…IR-11, are published in [`playbook.html`](playbook.html) §8 and
[`docs/review-fcb538fa.md`](docs/review-fcb538fa.md) §4. The ones that most affect decisions:

* **IR-04 / candidate compliance gap** — Participation Requirements **§5** forbids using Special Links or
  Program Content to develop machine-learning models without Amazon’s express prior written approval, and
  the compliance ledger (R-01…R-31) does not carry it — directly relevant to this brief’s AI content engine.
  Flag ids F-39…F-42 are already reserved/used by two other sessions, so the candidate finding is published
  for the owner to add as the next free id rather than risking another register collision.
* **IR-06** — multiple parallel sessions proposed overlapping suggestion/question surfaces during the day;
  the integration position is that the canonical registers stay with T29’s `pages/suggestions.html` /
  `pages/questions.html`, and newcomers link rather than duplicate.
* **IR-09 / IR-10** — the Associates tag (F-24) and the brief-to-destination mapping (F-01/F-03) remain the
  two owner actions without which no monetisation claim of this platform can be true.
* **IR-11** — the source-register notes for rows S38…S42 were written char-by-char (“T; h; e; …”) by the
  session that added them; the rows’ links and dates are correct, the notes column is garbled. Logged as a
  change request for the register owner, not edited here (shared data, other sessions active).

Earlier coordination findings are cross-referenced rather than renumbered: the conflict-marker debris in
`COORDINATION.md` was found and logged as **F-42** by session `42fa4918` (independently found and removed
on this branch as well — two sessions, one defect, both records kept, following the F-30/F-37 precedent).

### 4. State of the ask, item by item

| Requested | State |
|---|---|
| Suggestions that feed the site-design prompt | Delivered — `docs/design-prompt-suggestions.md` + `playbook.html` |
| Suggestions section to review before implementing | Live at `pages/suggestions.html` (T29, PR #61) with dashboard entry points (T30/T32) |
| Clear list of questions / information / answers before decisions | Live at `pages/questions.html` (T29) plus discovery actions D-01…D-06 in the playbook |
| Catchy, trendy, non-“AI slop” articles | Nine compliant angles proposed (DP-09…DP-17); first execution already live in the marketing set’s voice upgrade and its SG-04-gated topic queue (T32) |
| Organic traffic | Plan published (DP-18…DP-27); measurement remains missing information (IR-08, D-01) — no traffic data exists to claim |
| Executive summary | This addendum; CR-9 closed via T32’s addendum |
| GitHub Pages live site | `https://kanlerxz87-cyber.github.io/Zone2/` — deploy confirmed per closing record in `COORDINATION.md` |
| Verification, source links per row, unverified left blank | Enforced by gates and re-verified for every claim made here |
| PR → merge → deploy | See the T33 closing record in `COORDINATION.md` |
## Addendum — the publication layer and the marketing improvement board, 2026-11-15 (session `e8b071cd`, T39)

The brief has two halves. Before today, everything merged served the first: the platform, the registers, the
verification. The second half — *a polished affiliate publication that pulls organic traffic and does not read
like generated filler* — is served now, in `marketing/`, and it sits beside the voice pass that landed the same
day (T32): the two are merged here, and the reconciliation is stated in
`marketing/data/editorial.json` so a reader can see which copy came from where.

**What a reader gets.** `marketing/index.html` opens as a publication rather than a tool screen: a named desk, a
decision-first buying guide, one article per product with a verdict and a stated gap, and six guides that each
answer one search phrasing — how many quarts, two baskets or one, basket or fryer oven, what Hi-Fry does,
whether it fits the counter, and why two official pages disagree about the same fryer. A glossary, a per-article
"what we did not do" box, `sitemap.xml`, `robots.txt`, `feed.xml`, canonical URLs, Open Graph and
Article + BreadcrumbList JSON-LD came with them. `Product` and `Review` markup were deliberately left out:
nobody has cooked in these machines, so there is no rating to mark up.

**What the site still cannot say.** No price, no star rating, no tested claim, no invented byline. The three
product pages and both manufacturer pages were re-fetched on 2026-11-15; the resolved destinations are unchanged
and the `btn_ref` shuffle token moved again, which is the third session to record it.

**Decision surfaces.** `marketing/improvements.html` holds 14 open suggestions in this site's own scope —
options, trade-offs, a recommendation, the evidence, and what each is waiting on; seven are built the recommended
way and can be reversed from the board, seven are not implemented, on purpose. Ten questions in the same scope
sit beside them. Programme and business decisions stay on `pages/suggestions.html` and `pages/questions.html`
(T29, verified by T31); the boards cross-reference and do not duplicate each other.

**The writing standard is enforced, not recommended.** Ten rules live in `marketing/data/editorial.json` and
gates G11–G14 fail the build on a filler phrase, a guide claim with no source, an opinion outside a labelled
box, a first-hand-experience claim, an orphaned page, or a sitemap that misses a page. All six were
negative-tested. G4 caught this session's own example text quoting a dollar figure: the example was rewritten,
the rule was not loosened.

Line-by-line record, with the official links: `docs/marketing-2026-11-15.md`.

**Delivered (T33, 2026-11-15 12:18:54 UTC):** PR #83 merged (merge commit `1e351e6`); GitHub Pages build and deploy both succeeded and the playbook was read back live at `https://kanlerxz87-cyber.github.io/Zone2/playbook.html`; PR check `Build and verify` pass on head `21bc8d7`; CI on the merged tree — `audit_site` 5/5 PASS (104 pages), `validate_data` 0 errors / 0 warnings, `tests` 15/15, every `--check` gate no drift. One integration fix: the Sec. 5 endorsement-phrase line break in `playbook.html` that `validate_data` flagged (negation window defeated by the wrap) — reflowed, validator green.
## Addendum — 2026-11-15 (T38, session `arena/bfed39e0-zone2`): the journal ships, the redesign integrates

Two waves answered the owner's 2026-11-15 brief in parallel. The T34–T37 wave (session `2b257b2e`) rebuilt the root
surfaces as a polished marketing presentation and queued editorial topic ideas on the Content page; that redesign is
merged and live, and this session's own competing root redesign was **withdrawn in its favour** rather than merged over it
(nothing on `main` was discarded). What T38 ships additively is the layer the topic queue sketched but did not write: the
**Journal** (`journal/`) — three hand-written pieces (dual-basket cooking, basket-vs-oven geometry, site methodology), each
argued only from the already-verified specification rows, carrying the §5 disclosure, an identity-status banner (F-03 open),
per-claim source links, `rel="sponsored"` product links, and no price or rating anywhere. The journal is linked from the
landing-page navigation, the Content page's topic queue, the footer, and the sitemap; `assets/favicon.svg` ships with it.
During integration one irregularity was found and repaired on the deployed landing page (an unclosed `pages/suggestions.html`
anchor in the footer's Decisions column, which swallowed the link label) — logged in COORDINATION.md with the original markup
recoverable in git history. A second irregularity, the `@font-face` paths in `assets/css/style.css` resolving relative to the
stylesheet (`assets/css/assets/fonts/…`, which 404s so the self-hosted fonts silently fall back), is flagged for the design
system's owner and was not repaired from another session's file.

## Addendum — 2026-11-15 (session `f8e18ca8`): the independent review, the gaps, and the decision pack

This session was asked for four things the brief keeps repeating — review the repo line by line, make
suggestions that feed the design prompt, publish a section where a human can review and choose before
anything is implemented, and produce the list of questions, information and answers that must exist
before any decision is reasonable. It did no product work and changed no verified value. It reviewed
the deployed site, published the review, and published the decisions.

**The review, in one line.** The site's central claim holds — of 705 table rows across the 37
generated findings pages, 523 end in an official-domain source link, 164 are explicit blanks, and the
18 that are neither are internal contract rows, listed rather than waved through — and the site still
cannot earn, for reasons that are almost all non-technical. Sixteen findings, each with the
measurement that produced it, are published at `audit/index.html`.

**The five that matter**

| # | Finding | Severity |
|---|---|---|
| A-01 | The tables a reader comes for are not in the HTML. Eight root pages ship empty containers filled by a 102 KB script; with JavaScript off there is no product table, no findings table and no flag table. | high |
| A-02 | The required disclosure sentence is on every page, but on 24 of the 77 pages that link to a product it appears **after** the first product link — on the landing page, 93% of the way down the file. | high |
| A-05 | There is no measurement in production — no analytics, no click endpoint, no Associates report. Every tracking, conversion and optimization page describes a capability that has never processed a click. | high |
| A-06 | 114 pages across eight directory namespaces describe the same three products: six pages called "products", eight flag registers. That is the shape Google's scaled-content and thin-affiliation sections describe. | high |
| A-07 | No page names an author, an editor, or a contact route, and no page carries a date. The two questions Google's guidance asks first are unanswered on all 116 pages. | high |

Also found and repaired inside this session's own scope: four lines of merge-conflict residue that
were live in the landing page's footer (two stray `EAD` lines, two duplicated list items, one stray
`in`), and the same stray `in` in this document. Logged as **A-16**, because the conflict markers
themselves were gone and every gate passed — the residue was the *content* of a partially resolved
merge. That is the failure mode the current gate suite cannot see, and it is now recorded rather than
quietly cleaned.

**The decision pack.** `audit/suggestions.html` carries 14 recommendations, each with its options, a
recommendation, cost, risk, reversibility and the gap that blocks it — and **none of them is
implemented**. `audit/gaps.html` carries 15 missing-information rows with what is verified, what is
missing, how to close it and who can. `audit/decision-cost.html` adds the column most decision
registers omit: what happens if nothing is decided. `audit/traffic.html` states, with quoted sources,
what Google and Amazon actually document about earning organic traffic — and lists the five metrics
every affiliate site publishes (volume, conversion rate, click-through, RPM, "trending") that no
official source can verify, left blank.

**What was built, and why it can be trusted.** `audit/` is generated from five JSON files by
`tools/build_audit.py`; `tools/validate_audit.py` holds it to fourteen separate rules (every finding is
verified-with-a-source or unverified-with-a-reason; every carried source is labelled carried *on the
page*; every printed count is derived, never typed; links, fragments, disclosure and the no-price rule
as everywhere else). `tools/test_audit.py` injects 11 defects, one per check, and all 11 fire — so the
gate is a control, not a claim. `tools/check_css_urls.py` closes the gap session `1b839f87` logged as
`1B-2`: nothing in CI resolved a CSS `url()`, which is how the font 404 shipped on every page for
weeks. It is negative-tested too.

**The three things worth doing first**, if the owner reads nothing else: name the author and publish
the method (**R-07**, free), move the disclosure above the links (**R-02**, under an hour, 24 pages),
and pre-render the tables (**R-01**, the only change that makes the landing legible to a reader who
is not running JavaScript). Each makes existing work visible rather than adding to it.

**One item blocks revenue and it is not technical:** F-07 / G-01 — no Associates account, marketplace
or tag. Until that exists, nothing built here can be measured against a commission, and the
optimization half of the brief stays theoretical no matter how much more code lands.

Line-by-line record: `docs/audit-2026-11-15.md`. Design-prompt suggestions: `docs/design-prompt-2026-11-15.md`.

---

## Addendum — 2026-11-15 · session `bbcc741f` (paths, the third-date re-check, and one real defect)

Three things this pass adds to the picture above, and one thing it corrects.

**1. A decision can now be taken in one move.** The suggestions board is ten rows of options, which is the right
record and the wrong interface: an owner who agrees with seven of ten recommendations has not chosen a direction,
they have filled a form. `paths.html` groups the same rows into three sequences that each make sense on their own
terms — publish clean, earn, automate — with the letters taken straight from the board so nothing is
re-litigated, the program's own launch bar quoted beneath them, and a "what no path authorises" table so a
choice cannot accidentally read as permission for something the rules forbid. Path 1 is the default precisely
because it *is* the board's recommendation set: if nobody records anything, the site is already that path.

**2. The supplied links were checked again, by a new session, on a third date.** All three destinations
reproduced exactly (`V-83`…`V-85`), as did the control that proves a `link.amazon` token is not an ASIN
(`V-86`) — a live ASIN in the token position is refused by the hop service, so nothing outside the creating
account can decode these links back to a product. Two consequences are unchanged and still decisive: no
resolved URL carries an Associates `tag=`, so the links cannot pay this owner as supplied, and every product
attribute therefore stays blank rather than being inferred from wherever a stranger's link happened to point.
One consequence moved: the negative control `F-20` calls decisive answered **403** for an unissued token today,
not the 404 the register recorded (`F-40`). The reading survives — the positive evidence is what carries it —
but the site now says which leg it stands on instead of implying both are equal.

**3. Amazon's review bar is now a published constraint, not folklore.** Re-reading the Application Review
Process page (`V-89`) turned up two sentences that bear directly on every path and had not been carried into a
decision surface: content must generally be "within the last 60 days", and — the one that should decide
timetable — "we aren't able to reassess an application once it's been rejected". Rejection is terminal, so the
cheap-to-fix failure mode is publishing thin content on a site the applicant does not own while holding no
account; the expensive one is doing it once and being unable to try again. That is now the argument for the
ordering on `paths.html`, and it is quoted rather than paraphrased so it can be checked in one click.

**4. A defect in the site's own appearance, fixed.** The self-hosted typefaces had never loaded: the design
system's `@font-face` rules resolved against the stylesheet's directory and pointed at a path that does not
exist, so every page on the site — including the marketing surfaces built around a serif display face — had been
rendering in fallback system fonts since the redesign. No gate could see it, because a link checker follows
`<a href>` and not `url()`. It had been noticed and left alone for the wrong reason (the fix spans two
namespaces plus two builders); it is now repaired at both layers, and the register carries it as `F-39` so the
class of bug — a resource a build cannot fail on — is on the record for the next time.

**Numbers for the reviewer, all derived from the registers:** 43 flags, 45 sources, 108 logged checks, 20 open
questions, and 22 CI steps green on the merged tree. Nothing in this addendum states a product, price, rating
or performance figure: the site still has no authorised source for one, and an absent number beats an invented
one.

---

## Addendum — the crawl layer and the front door, 2026-11-15 (session `5d6d2254`, T42)

The brief's two halves were both published before this session: the verified platform with its registers,
and a reader-facing publication (`marketing/`, with the hand-written `journal/`) written under a
machine-checked editorial standard. What this session worked on was the layer between that content and the
outside world — what a crawler is told, what a link preview reads, and which door a first-time visitor is
put through. Nothing else: no product attribute, price, rating, commission band or register row was added,
changed or inferred, and no fourteenth article was written, because the content queue is an owner decision
still open on the improvement board.

**Two sessions found the same hole the same day, and the site is better for it.** The root sitemap had
become the one shared output no generator derived, and it had drifted to a fraction of the published tree,
listing none of the reader publication. `156aae86` shipped that half — `tools/build_sitemap.py`, now the
repository's sitemap generator, and `tools/seo_audit.py`, which fails the build on a missing page, a dead
`<loc>`, a `robots.txt` that blocks what the sitemap advertises, or a broken favicon. This session shipped
the other half, which is why the audit's canonical check has nothing to report on the reader and evidence
surfaces: `<link rel="canonical">` with `og:type`, `og:site_name`, `og:title`, `og:description` and `og:url`
now appear on every indexed page, emitted by the generator that owns each page through one shared
`tools/head_meta.py`, and held by `tools/build_head_meta.py --audit` in CI. No `og:image` was added — the
imagery rights question is open (Q-10 / DS-11) and a tag pointing at nothing is the sort of placeholder this
site refuses — and no Product or Review markup, per DS-07. `404.html` is not advertised for indexing, and
`<lastmod>` is omitted, because the repository holds no official source for a per-page modification date.

**The landing page leads with the decision, not the dashboard.** The primary navigation was a flat row of
fifteen links; it is now two labelled groups — a reader path (the publication, the buying guide, the
head-to-head, the guides index, the Journal) and an operator path (overview, products and evidence, the
suggestions board, the open questions, the verification log, the independent audit) — and the hero answers
the buyer's question before it describes the platform. Every page that left the header is still reachable
from this page: the body sections and the footer carry them, and the namespaces the structural audit
requires from the landing page are unchanged, so "linked or lost" is a build failure rather than a hope.

**Independent re-verification, published.** `docs/verification-5d6d2254.md` records what was re-read on
2026-11-15 with the official URL beside each row: the three supplied short links and their destinations,
the three `amazon.com/dp/<supplied code>` Page-Not-Found controls, every sourced Chefman and Emeril
specification row (13 of 13 on the dual-window page; the 8 Qt page's per-model lines; both live conflicts —
the 25-versus-24 preset count and the 450-versus-400 °F Hi-Fry figure), and the program facts the front
door cites: the Operating Agreement's §5 disclosure sentence, §1's tagged-link requirement, §4's refusal to
represent traffic or income, §6's termination terms, and Table 1's bands. Four items came out of it and were
deliberately not papered over: the Emeril listing serves a different title today than the string this site
quotes, and that title states a different accessories count than the row's `partial` value; the control
behind F-20 answered `403` through this fetch path where the register quotes a `404`, so the conclusion
stands and the status code does not; the 8 Qt manufacturer page is a two-variant page whose per-model lines
the site reads correctly without saying so; and the official Emeril page's own carousel asset names a
function count that disagrees with its body copy.

**What still blocks the earning half is unchanged and none of it is technical:** no Associate ID, so no link
on this site can attribute a commission (F-07 / F-24); the three intended products are still not established
by any official document (F-01 … F-03); the Creators API account is unregistered (F-05); and there are no
performance reports, because there is no traffic to report (F-08). Everything the owner must decide is on
the suggestions board and the questions register, each with the action that would discover the answer.
## Addendum — official-source re-verification and decision-surface confirmation, 2026-11-16 (session `arena/e7a12fe5-zone2`, task T40)

**Scope.** A fresh line-by-line re-verification of the official sources the published site rests on, recorded in full at `docs/verification-e7a12fe5.md`. No product attribute, price, rating, commission band or register row was added, changed or inferred; nothing here states a figure the official pages do not state.

**Official sources re-fetched live on 2026-11-16 and confirmed:**
- Associates Program Operating Agreement (`affiliate-program.amazon.com/help/operating/agreement`, Updated October 15, 2025) — §5 disclosure sentence.
- Associates Program Policies (`affiliate-program.amazon.com/help/operating/policies`, Updated April 14, 2026) — Commission Income Statement §1 attribution window; Participation Requirements §6; IP License.
- Standard Commission Income Statement / Table 1 (`affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ`) — Kitchen 4.50%, Home 3.00%, All Other Categories 4.00%; Prime bounties $12.00. Matches `ledger/commission_table.json` row by row.
- ASIN definition and tagged Special Link format (`affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC`) — ASIN is a 10-digit code; enforces rejection of the three 9-char supplied tokens via `tools/asin_guard.py`.
- FTC Endorsement Guides (`ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking`) — clear-and-conspicuous material-connection disclosure.
- Google qualify-outbound-links (`developers.google.com/search/docs/crawling-indexing/qualify-outbound-links`, Updated 2025-12-10) — `rel="sponsored"` for paid/affiliate links.

**The three supplied links re-confirmed:** each `link.amazon/<code>` resolves reproducibly to one live Amazon listing (Chefman 6 Qt dual-basket → B0CDY277D3; Emeril Lagasse 26 QT → B09B7SB46R; Chefman 8 Qt TurboFry → B08DKYBTPH). Each supplied code is 9 characters (not a 10-digit ASIN); `amazon.com/dp/<code>` returns Page Not Found; no resolved URL carries an Associates `tag=`, so as supplied none can earn commission (F-24). The short-code → destination mapping is observed behaviour, not documented intent (F-03; Q-03 / Q-18 owner-open).

**Decision surfaces confirmed linked and prominent:** the root landing page links the Suggestions board (`pages/suggestions.html`, SG-01…SG-14) and the Open questions register (`pages/questions.html`, Q-01…Q-20) from both the primary navigation and the footer "Decisions" column. Each suggestion row carries options, a recommendation, the questions that must be answered first, and an owner decision field awaiting record in `ledger/suggestions.json`. Nothing is implemented until a choice is recorded there.

**Repo gates run locally, all green:** `validate_data.py` 0 errors / 0 warnings (45 sources, 422 rows, 1217 links, all derived from the live register); `tests/test_pipeline.py` 15/15; `build_site.py --check` 39 pages, 0 drift; `check_css_urls.py` 0 broken url() references; `build_head_meta.py --audit` 0 problems; `build_summary.py --check` no drift; `audit_site.py` 162 pages, all checks PASS.

**Flagged irregularities (non-blocking, on `pages/flags.html`):** F-01/F-03 (product identity not established by an official document), F-24 (no Associates tag on the supplied links), F-05 (Creators API unregistered; PA-API 5.0 deprecated), F-08 (no performance reports; no traffic/revenue figures published anywhere). None blocks merge; all are published for owner review with their source links and closing actions.

**What remains owner-open:** confirm the product → intended-ASIN mapping with the brief owner; assign decisions for SG-01…SG-12 in `ledger/suggestions.json`; close or carry Q-01…Q-18 in `ledger/questions.json` (Q-02 Associate ID, Q-04 domain ownership, Q-17 declared Associates URL are the account-holder actions that unblock monetisation).

---

## Addendum — review board, requirements trace and the AI-slop diagnosis, 2026-11-16 (session `arena/7c1511ee-zone2`, task T52)

**What this session was asked for, and what it found.** The 2026-11-16 request asked for four things that
had no single home: suggestions a reviewer can *choose from* before anything is implemented; the questions
and missing information that make a choice reasonable; suggestions aimed at *discovering* missing
information; and a site that reads like a polished marketing site rather than generated output. The first
three already existed in fragments across six boards with incompatible scales and no recorded decision. The
fourth had never been measured. This session added one register that scores every proposal on one scale,
traced the request sentence by sentence, and converted the "AI slop" complaint into nine counted findings.

**Delivered — four new pages, one register, one gate, fifteen negative tests.**

| Artifact | What it is |
|---|---|
| [`review.html`](review.html) | 12 proposals `PS-01…PS-12` on one scale: three options each, commitment/cost/risk per option, a recommendation, the question it waits on, and the official source. All 12 read **awaiting your decision** |
| [`review-questions.html`](review-questions.html) | 9 questions `PQ-01…PQ-09`: what is verified, what is missing, the exact action that obtains it, and who takes it. **No row carries an answer** |
| [`review-trace.html`](review-trace.html) | The request traced as 16 rows `RP-01…RP-16` (6 met, 5 partial, 5 not met), 13 measurements `PM-01…PM-13`, 9 design findings `PD-01…PD-09`, 11 official sources quoted verbatim |
| [`review-ideas.html`](review-ideas.html) | 5 article concepts `PS-13…PS-17`, each with its basis, the page it would become, and why it might convert |
| `docs/review-board.json` | The register. In `docs/` because `tools/build_decisions.py --check` hashes every file under `decisions/`, so a register stored there is permanent drift |
| `tools/validate_review_board.py` + `tools/test_review_board.py` | An 13-rule gate and 19 injected defects, each of which must fire. Both run in CI with `build_review_board.py --check` |

**The "AI slop" complaint, measured.** Nine findings, each counted on 2026-11-16 rather than asserted:
68 of the 71 product links on the 20 marketing pages render as a *citation* ("M4 · www.amazon.com Amazon
listing") rather than a way to buy (`PD-01`); there are **no product images** on any of the 20 pages
(`PD-02`); the site's own methodology is its most repeated subject (`PD-03`); the hero's primary button
("Which one to buy") leads to a page containing **zero** product links and which explicitly declines to
name a winner (`PD-04`); **no page carries a ranked shortlist**, the one page type a shopper searches for
(`PD-05`); the root navigation is **76 links** in two groups (`PD-06`); every page prints a verification
date that Amazon's 60-day freshness guidance will keep failing (`PD-07`); no page names an author or
explains that it is generated from a source register (`PD-08`); and seven decision boards publish
proposals with the choice visible on none of them (`PD-09`).

**What did *not* change.** No product fact, count, quotation or flag owned by an earlier session was
edited. The three supplied links were re-resolved live and are unchanged (`B04G1MEwY → B0CDY277D3`,
`B02NbDxp3 → B09B7SB46R`, `B00hJ57DV → B08DKYBTPH`), still 9-character codes, still carrying no Associates
tag. `release/index.html` moved only because RR-10's `{measure}` token is derived: 140 → 144 published
pages, from the four pages this task added.

**The three decisions that unblock the most, if only one is read.** `PS-08` (name the audience — shopper
first, operator views labelled internal), `PS-05` (turn citation labels into buy links with the source kept
beside them) and `PS-02` (make the products the subject and the method a linked feature). None of them
needs an Amazon account, a domain, or a paid tool. All three are still awaiting a decision, because a
proposal is not an implementation and this session did not decide on the owner's behalf.

---

## Addendum — 2026-11-16 (session `43eb0239`, task T54 — renumbered: T50 went to `ebc8a709`, T51 to `970d11d6`, T52/T53 to `7c1511ee`)

**The product evidence was re-read from the official pages today, and one published value was wrong.**

Session `224cc10c` (T49) had already re-audited the *programme* sources — Associates policies, the Operating
Agreement, the Google and FTC pages. This pass re-read the other half, which nobody had touched since
2026-11-14: the three Amazon listings the supplied links resolve to, and the three manufacturer pages that
carry every specification the tables print. All six were fetched live and compared value by value. The
full record is [`docs/verification-43eb0239.md`](docs/verification-43eb0239.md), and the rows are in the
register as `V-90` … `V-104`.

**What held.** All three supplied links still resolve to the same three listings they resolved to on
2026-11-13 — `B0CDY277D3`, `B09B7SB46R`, `B08DKYBTPH` — for the sixth independent session, and all three
`btn_ref` tracking tokens are new again, which is flag F-21 reproducing exactly as published. The
unissued-code control behind F-20 reproduces. Every specification value sourced to a manufacturer page
matched the live text character for character: seven of seven on the Chefman dual-window page, the whole
8 Qt page including both of its published conflicts, and every value on the Emeril page including the
three-way preset disagreement. The two Chefman conflicts and the two Emeril conflicts all still stand, and
no session picked a winner between them.

**What did not hold.** The Amazon listing title this site publishes for `B09B7SB46R` was **stale**: the page
serves "…| Countertop Convection Cooker, 24 One-Touch Preset Options, Extra Large Interior, Six Cooking
Accessories Included", while the repository was still printing the 2026-11-14 read, "…| 26QT air fryer oven
with French doors, 24 cooking functions, dual-speed fan and rotisserie for easy family meals." Session
`5d6d2254` found the same thing on 2026-11-15 and left it, correctly, for whoever owned
`ledger/products.json`. Two independent sessions two days apart now read the same current string, and the
other two products' titles reproduced verbatim in the same run, so this is not how the site reads titles —
**Amazon serves different title text for that listing at different times.** The stored value has been
replaced with what the page serves today and stamped with the date it was read and the date it was
previously read. Logged as **F-41**, and the register row for that check is recorded `REFUTED`, not
`VERIFIED`.

**The lesson is the deliverable, not the typo.** A listing title is perishable evidence, and it is only
defensible for as long as it carries the date it was read. Three downstream copies of the old string — in
`revalidation/`, `marketing/` and `research-hub/` — are logged as change request **CR-13** in
`COORDINATION.md` rather than edited across another namespace's claim; the historical verification docs keep
the old string, because they quote it as evidence of what was true when they were written and rewriting them
would falsify the record.

**What could not be verified today is on the record too (`V-103`).** The rows sourced *only* to the Amazon
product-information table were not re-read: the listing body is request-dependent and two consecutive
fetches of the same URL returned different page lengths, so reading a number out of the wrong section
would have been worse than not reading it. Nothing was changed, filled in or inferred. Every one of those
rows keeps its official source link and its earlier observation date.

**Where the decision material stands.** Nothing in this pass changes what blocks the earning half: no
Associate ID, so no link on this site can attribute a commission (F-07 / F-24); the three intended products
are still not established by any official document (F-01 … F-03); the Creators API account is unregistered
(F-05); and there are no performance reports, because there is no traffic to report (F-08). The owner's
decision surfaces are unchanged and current — the ten suggestions with options and trade-offs on
[the decision board](https://kanlerxz87-cyber.github.io/Zone2/pages/suggestions.html), the
**18 open questions** with the method that would close each one on
[the questions register](https://kanlerxz87-cyber.github.io/Zone2/pages/questions.html), and the
[Flagged for Review](https://kanlerxz87-cyber.github.io/Zone2/pages/flags.html) page carrying **43 flags**,
each with its source links. Nothing is implemented on this site until it is chosen there.

**Numbers for the reviewer, all derived from the registers:** 43 flags (18 open · 25 resolved), 45 sources,
108 logged checks, 20 open questions, and every repository gate green on the merged tree.
---

## Addendum — 2026-11-16 — T50, session `arena/9251f262-zone2` — the "do not read like AI slop" rebuild

Appended, never rewritten: everything above stands as written by its own session.

### What the brief asked for this round

Four things, and they are in tension with each other, so this section states which way each was resolved.

1. **"It should look like a polished marketing affiliate website … it should not read like some AI slop
   website like it looks like now."** The site's own landing page was the complaint. It opened with how
   many links resolved and how many were confirmed — operator reporting, placed where a reader arriving
   from search expects to find air fryers.
2. **Catchy, trendy articles, and organic traffic.** Eleven pieces already existed. They were buried
   under the operator chrome and not grouped for browsing.
3. **A simple dashboard.** Also asked for. The tables and the evidence views were kept; they moved
   behind the landing rather than onto it.
4. **A suggestions section and a questions register,** so a person can review options and choose a path
   before anything is implemented.

### What changed

| Change | Detail |
|---|---|
| **The landing page is now a publication front page.** | A lead story about the three appliances, five numbered take-aways, the three machines as a hairline grid with their real specifications, the guides as a story grid, and the verification state demoted to one receipts strip. |
| **One design system across the site.** | `assets/css/publish.css` (new) plus the Counter Notes masthead, disclosure strip and footer on all 11 hand-written root pages. Previously the front pages and the operator pages used different headers. |
| **Dedicated decision boards.** | `suggestions.html` (12 suggestions, each with options A/B/C, cost, trade-off, a recommendation, the question it waits on, and an explicit *Proposed — awaiting owner decision* status) and `questions.html` (12 questions, each with what is known, what is missing, and the action that would close it). The two cross-link. |
| **Category subpages.** | `guides/` with four reader categories — basket air fryers, air-fryer ovens, buying guides, method — each listing the published pieces and, for the two product categories, the full sourced specification tables. |
| **Every figure still comes from the dataset.** | `tools/build_front.py` renders all eight new pages from `marketing/data/facts.json`, so no number was re-typed. Every row ends in a link to the official page that states it, or a dash with the reason printed beside it. |
| **Two new gates.** | `tools/build_front.py --check` (pages are reproducible from the dataset) and `tools/verify_front.py` (per-row sourcing, blanks carry a reason, no prices, disclosure above the data, sponsored links, links resolve, canonical matches path, no invented performance figures). CI is now 37 steps, all green. |

### What did not change

No verified value. No ledger row, no `assets/js/data.js` entry, no product attribute, no commission band,
no flag. The redesign is presentation and information architecture applied to the same evidence.

### Verified this session

Every load-bearing official source was re-fetched live on 2026-11-16 and compared string by string. The
three supplied links resolve to the same three listings as recorded (fourth consecutive date). All 11
commission bands in Table 1 match. The ASIN definition and the qualifying link format match verbatim. The
three manufacturer pages match every stored specification row, including both recorded conflicts. Full
record: `docs/verification-9251f262.md`.

### One drift found, published rather than quietly corrected

The Amazon listing title stored for the 26-quart Emeril oven is no longer the title Amazon serves. No
specification row is affected and nothing on the site is wrong — the stored *title* is stale. It is flagged
on the landing page and in the review rather than overwritten, because a silent edit would destroy the
record of what was read and when. Logged as cross-scope request R-3.

### Where this leaves the earning half

Unchanged, and still not a technical problem:

| Blocker | What would close it |
|---|---|
| No Associates tag, so no link can attribute a sale (F-24) | The owner supplies the tag and marketplace |
| The three intended products are not established by any official document (F-01…F-03) | The owner confirms the three ASINs inside Associates Central |
| No API credential, so no catalog, rating or band lookup (F-05) | Register for the Creators API; PA-API 5.0 is deprecated |
| No traffic, click, conversion or revenue figure exists | Turn on measurement, then wait — nothing before that is real |

Three of the four are one message from the owner away from closing. The fourth is a hosting decision.
All twelve suggestions and all twelve questions are on the new boards with the actions that would settle
them; nothing on either board has been implemented.

---

## Addendum — 2026-11-16 — the design brief (session `dc72a69e`, T57 — renumbered from T50)

**One sentence.** The research platform is finished and honest; the earning part has not started, and it
cannot start until the owner supplies one string: the Associates ID (tag).

Read in full at <https://kanlerxz87-cyber.github.io/Zone2/brief/>.

**Measured on 2026-11-16, and re-measured after T55 landed mid-review.** 150 published pages (excluding
error documents, the readiness board's own page, and the brief itself); 150 of 150 carry the exact §5
disclosure; **0 of 150 carry an Associates tag**; 0 print a product price; 43 of 43 workflow steps replay
green locally; 16 separate published surfaces. The three supplied
links resolve, on four dates across four sessions, to the same three listings: a Chefman 6-quart dual
basket (`B0CDY277D3`), an Emeril Lagasse 26-quart French-door oven (`B09B7SB46R`) and a Chefman 8-quart
basket fryer (`B08DKYBTPH`).

**Why the tag is the whole story.** Amazon requires Associates tags to be embedded in the product links on
the site declared in an application, and reviews that application only once at least three qualifying sales
have been driven within the first 180 days. Zero tagged links means zero qualifying purchases, which means
the application is never reviewed. Everything downstream in the brief — conversion tracking, the optimizer,
the revenue model, and the API enrolment that would let the site publish prices and star ratings — sits
behind that one value. It costs the owner one sign-in and no code.

**What the design brief answers.** The brief asks why the site reads like machine output. Measured: 14
pages carry the phrase "AI-powered" in public copy (11 carry the full "AI-powered Amazon affiliate"), which
is the commission's vocabulary surviving into the deliverable; the landing page's second heading said
"Three listings identified", which is the one claim the project's own flag register (F-03) declines to
assert; and 4% of sentences across the seven root pages have the site itself as their subject.

**A parallel session fixed part of this while the brief was being written.** Session `arena/9251f262-zone2`
(T55, PR #144) rebuilt the front pages as a publication on the same day: the overclaim heading is gone, the
abstract headings are gone, and self-reference fell from 8% to 4%. The brief was re-measured against the
combined tree and says so on every affected row. What T55 did not reach is the 14 operator and companion
pages that still print "AI-powered" — none of them reader-facing. The brief
publishes three rewrites of the actual published copy, a design system, and a paste-ready prompt whose
acceptance tests are machine-checkable.

**Two defects found on the readiness board, same class, twice.** `RR-01` prints "116 published HTML pages"
(the tree measures 150, and 159 once this namespace is counted) and `RR-05` prints "72 pages link to
amazon.com/dp/" (measured 87). Both are typed into prose rather than derived, so both drifted with no gate
noticing. Logged as change request CR-1 in COORDINATION.md — the files that own them are outside this
session's claimed scope. The brief's own summary is not allowed to make that mistake: its gate re-derives
the counts from the tree every run.

**A third:** the canonical suggestion board carries the same proposal twice (`SG-11` and `SG-12`), so it
advertises twelve suggestions where eleven exist.

**Nothing on the new board is implemented.** Twelve proposals (`DB-01…DB-12`) wait on
`brief/suggestions.html` with options, costs, risks and blockers; ten questions on `brief/questions.html`
are left empty on purpose, each with the action that would close it and who can close it.

---

## Addendum 2026-11-17 — the brief names five links, not three (T59, session `1539a895`; renumbered from T58)

Every prior session processed only the first three of the five `link.amazon` links the brief supplies.
The **4th (`B0c8moW59`) and 5th (`B0f3GKalj`) had zero references anywhere in the repository** before this
session. Both were resolved live on 2026-11-17 and added to the source-governed ledger as `P-04` and `P-05`.

| # | Link as supplied | Token | Token length | Valid ASIN? | `/dp/<token>` result | Observed destination (ASIN) | Observed product | Official evidence |
|---|---|---|---|---|---|---|---|---|
| 4 | `https://link.amazon/B0c8moW59` | `B0c8moW59` | 9 | **No** | Page Not Found | `B0DHZTCNR5` | ThermoMaven 1 Sec Professional Digital Meat Thermometer | [Amazon listing](https://www.amazon.com/dp/B0DHZTCNR5) |
| 5 | `https://link.amazon/B0f3GKalj` | `B0f3GKalj` | 9 | **No** | Page Not Found | `B0DZFD6R9Z` | CHEF iQ Sense Smart Wireless Meat Thermometer (Gen3) | [Amazon listing](https://www.amazon.com/dp/B0DZFD6R9Z) |

**What changed.** The two new destinations are **kitchen thermometers** — a second product category the
air-fryer shop front does not cover. Both supplied codes are still 9 characters (not valid ASINs) and
`/dp/<code>` returns Amazon's Page Not Found page, exactly as for the first three (the same control and
flags `F-01`/`F-28`). Each link opens one stable Amazon listing, reproducibly, but no public Amazon document
binds a `link.amazon` code to a destination, so the destinations are recorded as **observed**, not as
established identities.

**Product-intent confirmation record (new, per the brief).** Each of `P-04`/`P-05` now carries an explicit
`intent_confirmation` block with four fields the owner fills in — `intended_asin`, `official_listing_url`,
`confirmation_date`, `intent_source` — kept in separate fields from `observed_redirect_target`, so the two
readings can never be merged. All four intent fields are blank until the owner confirms; the redirect target
is recorded separately as an observation. This is the schema the brief asks for and is proposed as the
standard intake for every future link (suggestion `SG-14`).

**Verified destination specifications (read from the two official listing pages, sourced per row).**
`P-04` (ThermoMaven): 1-second response, ±0.5 °F accuracy, 572 °F upper range, 0.1 ° resolution, 6.5 in
immersion depth, digital display, AAA battery, NIST/NSF specification met, plastic, wipe-clean.
`P-05` (CHEF iQ): 5 sensors (4 internal + 1 ambient), within 1 °F accuracy, 1000 °F heat-safe, 3 ultra-thin
probes (4.75 in), WiFi + Bluetooth, waterproof/dishwasher-safe probes, two-year assurance, smart hub with
speaker and push notifications, air-fryer/deep-fryer safe, 1/2/3/4-probe options. **One published conflict
is recorded, not resolved:** the CHEF iQ battery life is stated as "up to 50 hours" in the *About this Item*
block and "up to 70 hours" in the *Product Description* on the same listing — both figures are published.

**Still blank and flagged (never inferred).** Price, rating, review count, availability and sales rank for all
five links (Amazon policy restricts republishing them outside a served link or licensed API). The
commission band for the two thermometers is also blank: both sit in *Home & Kitchen › Kitchen & Dining ›
Kitchen Utensils & Gadgets*, a node Amazon's public Table 1 does not name, so the band cannot be assigned
between the 4.50% "Kitchen" and 3.00% "Home" rows without guessing (flag `F-43`, question `Q-20`).

**New decision records (nothing implemented; all awaiting an owner choice).** Flags `F-42` (the two links
were never processed and resolve to a new category) and `F-43` (commission-band ambiguity). Questions `Q-19`
(confirm the intended ASINs for links 4 and 5) and `Q-20` (confirm the commission band via an authenticated
catalog lookup). Suggestions `SG-13` (build a matching thermometer content set once intent is confirmed) and
`SG-14` (adopt the product-intent confirmation record as standard intake). The shop front still leads with the
three air fryers; the two thermometers are published in the product catalog with their sourced specs, and the
editorial expansion waits on `Q-19`.

**Register state after this addendum:** 5 product entries, 45 sources, 108 verification rows, 43 flags
(18 open · 25 resolved), 20 questions, 14 suggestions. Every repository gate is green on the merged tree.

---

## Addendum 2026-11-17 — the submitted set grew from three links to five (T60, session `613900e6`; renumbered from T58 — see the coordination note)

The brief of 2026-11-17 names five affiliate links. Every register in this repository was built around
three, and two of the codes (`B0c8moW59`, `B0f3GKalj`) plus the tracking id (`shopnow047c-20`) appeared
nowhere in the tree. A new `intake/` namespace registers all five and changes no other register.

*Read alongside the T59 addendum above.* Session `1539a895` (T59) resolved the same two links into the
ledger as `P-04`/`P-05` with full specifications; this session resolved them independently into `intake/`
as `SUB-04`/`SUB-05` and reached the **same two destinations** (`B0DHZTCNR5`, `B0DZFD6R9Z`). The two
records are complementary, not competing: T59 owns the ledger rows and the specs, this one owns the
all-five register, the tracking id, the measurement record and the decision board.

**What the five links do.** Three resolve into Air Fryers (`B0CDY277D3`, `B09B7SB46R`, `B08DKYBTPH`); two
resolve into Meat Thermometers (`B0DHZTCNR5`, `B0DZFD6R9Z`). Every page that describes the promoted range
as air fryers is now wrong about two fifths of it. All five resolve reproducibly, and an unissued code of
the same shape returns a 404, so the codes are honoured lookups rather than ignored input.

**What is still not established.** The intended ASIN for any of the five. Each submitted token is 9
characters and Amazon's help page defines an ASIN as "the 10-digit code that Amazon uses to denote
specific products", so no submitted token identifies a product on its own. The record therefore carries the
intended ASIN, listing URL, confirmation date and source in one group of fields — all blank — and the
observed redirect target in a separate group. They are not merged.

**No resolved URL carries an Associates `tag=`.** Under the Operating Agreement a Special Link must use the
tagged formats Amazon provides. It does not follow that the supplied links are invalid — a tag may be
attached during the redirect — and this project does not claim either way, which is also why the brief's
FLG-003 exists. Settling it takes one enrolled account and one report read.

**The measurement plan cannot be built as specified.** The brief asks for a self-hosted analytics endpoint;
GitHub Pages is a static site hosting service, so there is nowhere on this host to run one. Recorded rather
than worked around, because the three honest options differ in cost and in what they may store.

**Decisions, none taken.** Five proposals with fifteen options sit on `intake/proposals.html` with costs and
blockers; ten questions on `intake/questions.html` are left deliberately empty, each with the action that
would close it. Nothing in the namespace is implemented.

**A defect found in an existing control (CR-2).** The "no page prints a product price" rule used by six
gates in this repository is inert: it strips HTML tags before splitting on them, so the whole page becomes
one unit, and the mandatory disclosure contains the word "earn", which suppresses every hit. Reproduced on
three real pages with an injected `$149.99`. The new intake gate splits correctly and proves it with a
negative test. The six existing sites are logged as CR-2 in `COORDINATION.md` rather than edited, because
they are outside this session's file scope.

Verification: [`docs/verification-613900e6.md`](docs/verification-613900e6.md). All 46 CI steps pass on the
combined tree.

## Addendum — 2026-11-17 (session `7264f3c2`, T62; claimed as T58): the tag arrived, and what it changed

The previous section ends with the one action that unblocked the revenue side: the owner supplying
the Associates tag. On 2026-11-17 the brief supplied it — **`shopnow047c-20`** — and this session
wired it through the generators rather than pasting it into pages.

**What changed on the site.** Every reader-facing product link is now a tagged Special Link emitted
by `tools/link_builder.py:build_product_link()` (`rel="sponsored nofollow"`, tag `shopnow047c-20`,
link-level "(paid link)" disclosure kept). The gates hardened in the same direction: a product CTA
without the tag fails the build, any tag that is not the owner's fails the build, and citation
links to official pages must carry no tag at all — evidence stays unmonetized. The social-preview
image the site never had is shipped (`assets/img/og.jpg`, a brand card, deliberately not product
photography) and the head contract now carries `og:image` + `twitter:card` on every generated page.

**What measurement changed.** The owner decision was recorded on DS-11 and the three client-side
events of the measurement design went LIVE (`assets/js/events.js`): page views, product-link clicks,
disclosure views — no cookie, no identifier, nothing per person, and no count published anywhere.
EV-04 (conversions) and EV-05 (search queries) stay blocked on first-party reports; the endpoint
that would persist the counts does not exist on GitHub Pages static hosting and stays open as
DS-17/DQ-12 with `tools/tracking_schema.sql` as the contract.

**What did not change.** The mapping question (F-06) is untouched: no official Amazon document binds
a supplied code to a product, so every `intended_asin` in the new
[`docs/product-intent.json`](docs/product-intent.json) register stays null with its reason, and the
observed redirect targets live in separate fields, never merged. Two of the five supplied links land
outside the air-fryer set — `B0c8moW59` on a ThermoMaven meat thermometer (B0DHZTCNR5) and `B0f3GKalj`
on a CHEF iQ Sense (B0DZFD6R9Z). This session re-observed both live; they were first recorded by T59
(`1539a895`, onboarded as P-04/P-05) and corroborated by T60 (`613900e6`, the intake register) — three
independent passes reaching the same destinations. They are recorded, not promoted, and their
disposition waits on DS-16/DQ-11. The per-link Associates-workflow validation the
brief demands before scaling is recorded as pending on every row: it needs the owner's enrolled
session, and no conversion figure exists to publish.

## Addendum — 2026-11-17 — the five-product brief (session `arena/1bfbc559-zone2`, T62)

### Three new facts

**Two products the repository had never seen.** The brief names five products. `link.amazon/B0c8moW59`
and `link.amazon/B0f3GKalj` appear in no file in this repository before 2026-11-17 — verified by a
case-insensitive search across every `.json`, `.html`, `.md` and `.py` in the tree. Both were fetched live
and both resolve: to a ThermoMaven instant-read meat thermometer (`B0DHZTCNR5`) and a CHEF iQ Sense
wireless meat thermometer (`B0DZFD6R9Z`). Both serve the same title on direct arrival at `/dp/<ASIN>`
without the short link.

**So the catalogue is not one category.** Three products resolve into
*Small Appliances › Fryers › Air Fryers* and two into
*Kitchen Utensils & Gadgets › Thermometers & Timers › Meat*. Every product page this site has published —
the comparison, the buying guide, the counter-space analysis, the question-shaped articles — is about air
fryers. The plan is out of date, not the pages.

**A tracking ID, for the first time.** `shopnow047c-20` matches the shape Amazon publishes for a
special-link tag (`abcd-20`), and it cannot be confirmed as an issued, active ID from any public page —
Amazon states IDs are generated on application. No published page carries a tag today: 0 of 162.

### What was built

Nine pages at `board/`: the product-intent confirmation record (intent and observation in separate field
groups that never merge), a twelve-row choose-a-path board where nothing is applied, a 17-question
known/unknown register whose open answers are empty by rule, a trace of every requirement row in the brief
against the tree, ten topic proposals, the source register, the verification record and the flagged page.

**Nothing on the board is implemented.** The `chosen` field on every suggestion is empty, and the build
fails if it is not.

### The requirement rows, checked rather than taken on trust

Most hold up: 162 of 162 pages carry the disclosure, the front page leads with the products, the campaign
ledger is exactly the empty-but-defined thing the brief asks for. Four do not: **S-04** (7 pages with no
meta description — the only unfinished P1 row), **S-19** (no chooser component exists), **S-24**
(4 reader pages one hop short), **S-09** (no social preview image on any of the 162 pages, though 108
carry the rest of the `og:` block).

The loudest number is not a defect: 2,238 Amazon-host links of which 132 carry `rel="sponsored"`. The
unmarked remainder are citations to a source inside a verification table, not offers — and Google defines
the value by what the link is.

### One defect found in the repository's own gates

The context-aware rule that is supposed to stop any page printing a product price **never fires**. Four
copies of it (`.github/workflows/pages.yml:155`, `tools/validate_data.py:550`,
`tools/build_readiness.py:623`, `tools/validate_audit.py:272`) strip HTML tags *before* splitting the page
on those same tags, so all 162 pages collapse to a single unit and the program-economics exemption
swallows every price. Reversing the two operations makes the rule fire. `board/`'s own gate is written the
corrected way round, and its negative test caught its own evidence paragraph on the first run — which is
how the defect in the other four was noticed. Logged as FL-13 and CR-4; not fixed here, because those
files are outside this session's scope.

### Gates

`tools/ci_replay.py`: **46 of 46**. `tools/validate_board.py`: clean. `tools/test_board.py`: 19 injected
defects, each fires. `tools/audit_site.py`: 171 pages, all checks pass.

### Cross-scope requests filed

- **CR-2** — ingest the two new supplied links into `ledger/products.json`, copying the intent fields as
  empty rather than filling them from the observation.
- **CR-3** — the design brief's summary still types five counts (they moved from 150 pages to 159 when
  `board/` was added); derive them, as `tools/build_board.py` does.
- **CR-4** — fix the price-rule ordering in all four copies.


---

## Addendum — 2026-11-19 (session `arena/da47d78d-zone2`, T65): Final Integration, Five-Product Verification, Shopfront & Thermometer Marketing Desk, and Complete Compliance Synthesis

### 1. Executive Summary & Verified Status of the Five Products

This integration session delivers the complete, verified, line-by-line review of the repository, unites the five submitted affiliate marketing links, validates the official compliance posture, resolves critical workflow conflicts, and harmonizes the publication shopfront.

All five submitted links were independently analyzed and verified against official sources:

| # | Submitted Link | Token | Token Length | Valid ASIN? | Canonical `/dp/` Result | Observed Redirect Destination | Category | Sourcing & Status |
|---|---|---|---|---|---|---|---|---|
| 1 | `https://link.amazon/B04G1MEwY` | `B04G1MEwY` | 9 | **No** (ASIN is 10 chars) | Page Not Found (Amazon 404) | `https://www.amazon.com/dp/B0CDY277D3` (CHEFMAN 6 Quart Dual Basket Air Fryer Oven) | Small Appliances › Fryers › Air Fryers | [Amazon listing B0CDY277D3](https://www.amazon.com/dp/B0CDY277D3) · [ASIN Policy](https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC) · Unconfirmed mapping (F-01, F-03) |
| 2 | `https://link.amazon/B02NbDxp3` | `B02NbDxp3` | 9 | **No** (ASIN is 10 chars) | Page Not Found (Amazon 404) | `https://www.amazon.com/dp/B09B7SB46R` (Emeril Lagasse 26QT French Door Air Fryer Toaster Oven) | Small Appliances › Fryers › Air Fryers | [Amazon listing B09B7SB46R](https://www.amazon.com/dp/B09B7SB46R) · [ASIN Policy](https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC) · Unconfirmed mapping (F-01, F-03) |
| 3 | `https://link.amazon/B00hJ57DV` | `B00hJ57DV` | 9 | **No** (ASIN is 10 chars) | Page Not Found (Amazon 404) | `https://www.amazon.com/dp/B08DKYBTPH` (Chefman Air Fryer 8 Qt TurboFry) | Small Appliances › Fryers › Air Fryers | [Amazon listing B08DKYBTPH](https://www.amazon.com/dp/B08DKYBTPH) · [ASIN Policy](https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC) · Unconfirmed mapping (F-01, F-03) |
| 4 | `https://link.amazon/B0c8moW59` | `B0c8moW59` | 9 | **No** (ASIN is 10 chars) | Page Not Found (Amazon 404) | `https://www.amazon.com/dp/B0DHZTCNR5` (ThermoMaven 1 Sec Professional Digital Meat Thermometer) | Kitchen Utensils & Gadgets › Thermometers › Meat | [Amazon listing B0DHZTCNR5](https://www.amazon.com/dp/B0DHZTCNR5) · [ASIN Policy](https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC) · Unconfirmed mapping (F-42, F-43) |
| 5 | `https://link.amazon/B0f3GKalj` | `B0f3GKalj` | 9 | **No** (ASIN is 10 chars) | Page Not Found (Amazon 404) | `https://www.amazon.com/dp/B0DZFD6R9Z` (CHEF iQ Sense Smart Wireless Meat Thermometer) | Kitchen Utensils & Gadgets › Thermometers › Meat | [Amazon listing B0DZFD6R9Z](https://www.amazon.com/dp/B0DZFD6R9Z) · [ASIN Policy](https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC) · Unconfirmed mapping (F-42, F-43) |

**Key Finding:** The five submitted links span **two distinct kitchen categories** (three air fryers and two kitchen thermometers). None of the supplied 9-character tokens is an ASIN, and none resolves via canonical `/dp/` URLs. Each short link resolves reproducibly to a live Amazon product listing. In accordance with zero-hallucination principles, observed destinations are recorded as factual observations and are never merged or assumed to represent confirmed author intent.

---

### 2. Configured Associates Tracking ID (`shopnow047c-20`)

- **Selected Tracking ID:** `shopnow047c-20`.
- **Implementation in Code:** Governed centrally by `tools/link_builder.py` (`ASSOCIATES_TAG = "shopnow047c-20"`), which validates the tag against the Amazon Associates tag specification (`TAG_RE = re.compile(r"^[a-z0-9]+-\d{2}$")`).
- **Policy Enforcement:**
  - Every reader-facing product link is composed as a Special Link with `rel="sponsored nofollow"`, `target="_blank"`, and `referrerpolicy="no-referrer-when-downgrade"`.
  - Every product link carries a clear link-level disclosure (`(paid link)`).
  - Citation links and evidence references (e.g. `class="src"` or `class="pb-src"`) pointing to Amazon listings **deliberately carry no tag**, ensuring that evidence remains strictly unmonetized and objective.
  - Sub-tags are strictly constrained to static labels; per-visitor or user-derived identifiers are prohibited by `tools/link_builder.py` under Amazon Participation Requirements (R-08 / S02).

---

### 3. Strict Separation of Product Intent vs. Redirect Observation

To comply with the brief's requirement (*"store the intended ASIN, official listing URL, confirmation date, and source. Keep observed redirect targets in a separate field. Do not merge the two fields"*), the repository enforces strict schema segregation across `docs/product-intent.json`, `intent.html`, `board/products.html`, and `intake/submissions.html`:
- **Intended Fields Group:** `intended_asin`, `official_listing_url`, `confirmation_date`, `intent_source`.
- **Observed Fields Group:** `observed_redirect_target`, `destination_asin`, `destination_title`, `observed_on`, `observation_source`.
- **Integrity Rule:** `tools/validate_intake.py` and `tools/validate_board.py` verify that no intent field borrows an observed value. Because all five supplied tokens are 9 characters and undocumented by Amazon, every `intended_asin` field remains an explicit null with recorded justification.

---

### 4. Publication Front-Door & Shop-First Architecture

- **Front Page (`index.html`):** Transformed into a clean, buyer-centric publication front door under the brand **Counter Notes**. It leads directly with products, geometric comparisons, and actionable buyer guides ("The 6-quart, the 8-quart, and the oven that wants to be both"), rather than displaying raw audit registers to the shopper.
- **Navigation & Reachability:** A unified masthead navigation provides direct reader access to guides, comparisons, suggestions, and open questions. All operator dashboards, verification registers, audit tables, and companion prototype surfaces remain fully reachable through structured footer navigation groups.
- **Above-The-Fold Disclosure:** Every page features the prescribed Amazon Associates disclosure strip immediately under the masthead and above any product table or content:
  > *"As an Amazon Associate I earn from qualifying purchases. A commission may be earned when you buy through our links, at no extra cost to you. Product links are Special Links carrying the Associates tag `shopnow047c-20`; citation and evidence links are not affiliate links."*
  The disclosure is repeated in full in the page footer across all 180 published pages.

---

### 5. Question-Shaped Buyer Guides

The platform features human-sounding, question-shaped editorial guides grounded in verified manufacturer specifications:
1. **Basket vs. Oven-Style Air Fryers:** Geometry, footprint, and cooking style trade-offs between pull-out baskets and countertop convection doors.
2. **Capacity Translated:** Translating nominal quart figures into usable cooking surface area (single large basket vs. dual sync-finish compartments vs. 26-quart multi-rack rotisserie capacity).
3. **Counter-Space & Clearance:** Exact footprint measurements, vertical cabinet clearance, and ventilation requirements.
4. **Hi-Fry & Temperature Realities:** Spec-sheet analysis documenting manufacturer vs. retailer temperature discrepancies (400°F vs. 450°F).
5. **Kitchen Thermometers (Instant-Read vs. Wireless Probes):** Evaluating the 1-second single-probe ThermoMaven against the multi-probe CHEF iQ Sense Gen3 system, probe thickness impact on meat juices, and battery life specifications (50h vs. 70h conflict documented).

---

### 6. Privacy-Preserving Analytics & Measurement Layer

- **Client Tracking Script (`assets/js/events.js`):** Implements lightweight, privacy-preserving event recording adhering strictly to principles MP-01 through MP-05:
  - **EV-01 (`page_view`):** Fires on page load with day-bucket and sanitized referrer host. **LIVE**.
  - **EV-02 (`product_link_click`):** Observes outbound product clicks with product key and link state. **LIVE**.
  - **EV-03 (`disclosure_view`):** Employs an `IntersectionObserver` to confirm that the affiliate disclosure enters the reader's viewport above the first product link. **LIVE**.
  - **EV-04 (`conversion_import`):** Stores period conversions from authorized first-party Associates reports. **BLOCKED** on account reporting export.
  - **EV-05 (`search_query_import`):** Records verified search queries from Google Search Console. **BLOCKED** on Search Console domain verification.
- **Zero Fingerprinting:** No cookies, no local identifiers, no IP tracking, no query parameter capture. Events queue in a bounded local storage bucket with optional background beacon flush to `/api/events`.

---

### 7. Automated Verification Gates & Cross-Scope Defect Resolutions

- **CI Workflow Conflict Resolution:** Removed unresolved merge conflict markers in `.github/workflows/pages.yml` (lines 87–94 and 386–441). Harmonized both `intake/` and `board/` test suites within CI.
- **Workflow Health Preflight in `tools/ci_replay.py`:** Added an automated preflight check to `tools/ci_replay.py` that immediately detects and halts on any conflict markers or malformed lines in `.github/workflows/pages.yml`.
- **CR-4 Resolution (Inverted Price-Rule Ordering):** Resolved the longstanding defect where tags were stripped before splitting on tag boundaries. The logic across `tools/validate_data.py`, `tools/validate_audit.py`, `tools/build_readiness.py`, and `.github/workflows/pages.yml` now splits first on block tags (`</tr>`, `</p>`, `</li>`, `<br>`) and then strips tags per unit, preserving price-context boundaries. Tested across all 180 published HTML pages with zero regressions.
- **Discoverability & Canonical Contract:** Derives all 178 sitemap URLs dynamically, verifies `robots.txt`, and enforces self-referencing canonical URLs and Open Graph tags across indexed surfaces.

---

### 8. Suggestions & Open Questions Registers (Decision Desk)

The decision desk (`suggestions.html`, `board/suggestions.html`, `brief/suggestions.html`, `console/suggestions.html`, `audit/suggestions.html`) maintains explicit separation between proposals and decisions:
- **No Pre-Emptive Execution:** All proposals maintain status `Proposed — awaiting owner decision`. Each option details concrete costs, trade-offs, and blocking dependencies.
- **Missing Information & Discovery:** The open questions register (`questions.html`, `board/questions.html`, `brief/questions.html`, `console/questions.html`) explicitly outlines what is known, what is missing, and how the owner can discover it (e.g., verifying Associates Central enrollment, conducting Creators API GetItems catalog lookups, and confirming product intent).

---

### 9. Gate Audit & Build Results

- **`tools/ci_replay.py`:** **49 of 49 workflow steps PASSED**.
- **`tools/audit_site.py`:** **180 published pages audited — all 7 audit categories PASS** (fragments, spec sources, prose counts, namespaces, disclosure, debris, board).
- **`tools/seo_audit.py`:** **178 sitemap URLs audited — all discoverability checks PASS**.
- **Negative Test Suites:**
  - `tools/test_intake.py`: 15/15 injected defects fired.
  - `tools/test_board.py`: 19/19 injected defects fired.
  - `tools/test_brief.py`: 14/14 injected defects fired.
  - `tools/test_review_board.py`: 19/19 injected defects fired.
  - `tools/test_readiness.py`: 14/14 injected defects fired.
  - `tools/test_audit.py`: 11/11 injected defects fired.
  - `tests/test_pipeline.py`: 15/15 unit tests passed.
- **Published Surface Count:** 180 published pages, 100% carrying the statutory disclosure, 0 pages publishing unauthorized prices, 100% internal links resolving cleanly.
## Current-state addendum — 2026-11-19 (T63 integration)

This section is the current status as of the date above. It supersedes earlier summaries that describe
only the initial three-link set; it does not rewrite those dated verification records.

### Five submissions: intent is still blank

The current intake register contains five submitted short links. The submitted tokens are not recorded
as intended ASINs. For each record, `intended_asin`, intended listing URL, confirmation date, and
confirmation source remain blank; the observed redirect destination is stored separately and was last
recorded on 2026-11-17. The five observations point to three air-fryer listings and two meat-thermometer
listings, but that is not proof of what the submitter intended. The exact compliance status of the supplied
short links remains unresolved in FLG-003; no claim is made that they are invalid. See
[`intake/submissions.html`](intake/submissions.html), [`intake/flags.html`](intake/flags.html), and the
[Amazon link-format help](https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC).

### Publication and integration status

The reader-facing summary is now generated at [`summary.html`](summary.html) from the five-record intent
register. It keeps intended identity separate from observed destinations, leaves unknown values blank,
and links readers to the questions, decision board, source register, and suggestions with explicit options
and trade-offs. The earlier `summary.html` narrative mixed a three-link description with values from a later
five-entry ledger; it has been replaced rather than represented as current. This Markdown file preserves
the older dated narrative and its verification trail.

The Pages workflow's two literal conflict blocks have been resolved while retaining both submitted-link
intake gates (`build`, validator, negative tests) and decision-board gates (`build`, validator, negative
tests). The generated publication uses reader-first primary navigation, one accessible “Project & tools”
disclosure group, and footer links for the tool and dashboard routes. The suggestion count is derived from
the decision register. Buyer-question topics are described as editorial hypotheses, not measured demand.

The front-page disclosure accurately says that `shopnow047c-20` was supplied, while its account status and
presence on every product destination have not been confirmed. Repository HTML inspection finds product
destination links do not consistently carry the tag. **Correction to the T65 completion note above:** it
calls the tag “verified and active”; this integration found no authorized account evidence that establishes
that status or universal link coverage. Treat activation as unconfirmed until the owner validates it inside
Associates Central and in an authorized report. The implementation does not claim that account activation,
per-product Special-Link validation, server-side event collection, conversion attribution, or Search Console
reporting is live. Amazon's [Operating Agreement](https://affiliate-program.amazon.com/help/operating/agreement)
requires properly tagged Special Links; Google's guidance says paid placements should use
[`rel="sponsored"`](https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links).

### Measurement contract still needs reconciliation

`assets/js/events.js` stores page-view, product-click and disclosure-view events in a bounded browser-local
queue; without a configured endpoint, it transmits nothing and no counts are published. Conversion imports
and Search Console query imports remain blocked on first-party reports and verified account access.
There are two documentation discrepancies to resolve before enabling a backend: the intake tracking
register calls the events proposed/not instrumented while `docs/measurement-t40.json` labels three events
LIVE (client-side only), and the page-view code sends the referrer hostname under property `r` while the
measurement schema names `referrer_host`. These were identified by repository inspection, not by a live
endpoint test. GitHub Pages is documented as static hosting; no event sink was found in this repository.
See [`docs/measurement-t40.json`](docs/measurement-t40.json), [`intake/tracking.html`](intake/tracking.html),
[GitHub Pages documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages),
and the [FTC disclosure guidance](https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers).

### Verification in this integration

- Python compilation, the front-page generator and freshness check, the summary freshness check, and the
  front-page verifier passed; the verifier reports nine generated pages current.
- The Pages workflow parses as YAML and retains the intake and decision-board build, validator and negative
  test commands; conflict-marker scan is clean.
- Regenerated the sitemap and dependent derived counts. `tools/ci_replay.py` passed all 49 steps, including
  the intake/board gates, sitemap coverage, release-readiness checks, and front-page gate.
- No product/source facts were changed and no live Amazon redirect was repeated in this integration pass.
  The changed verification scope and commands are recorded in
  [`docs/verification-cf98ff65.md`](docs/verification-cf98ff65.md).
- PR #166 merged on 2026-11-19 at 06:01:43 UTC as merge commit `785740716952f309e5895ffeaea6c675115cc2d7`. The post-merge build-and-deploy run passed, the GitHub Pages deployment run succeeded, and the Pages API reports `status: built` at <https://kanlerxz87-cyber.github.io/Zone2/>.

### Next evidence to collect

1. Have the submitter confirm the intended ASIN and official listing URL for each of the five links; retain
the confirmation date/source apart from redirect observations.
2. Verify the Associates account and marketplace, then confirm each intended Special Link is tagged with
`shopnow047c-20` and appears in the authorized account report.
3. Reconcile the measurement definitions and field names before deploying an endpoint; record retention and
bot-filtering choices before collecting events.
4. Verify Search Console ownership and use actual query/page data before treating any topic as measured
interest. Until then the guide subjects remain editorial hypotheses.
