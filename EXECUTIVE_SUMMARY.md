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
  (`pages/flags.html`) with source links — **33 flags (F-01 … F-33)**, including the deprecated-API trap and the
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

### One substantive defect found and fixed (F-29)

The “Bounty events” panel published **9** rows under a notice reading *“Transcribed row-by-row from Amazon's
published Associates Program Standard Commission Income Statement.”* S04 actually publishes **46** rows under
“(a) Bounty Events” and **2** more under “(b) Bonus Events”. The nine rows on the page were the first nine and
were individually correct and correctly sourced — the defect was **omission**, not error, but a partial list
wearing a completeness claim reads as the whole set, and it hid the two largest published bounty rates on the
program (Audible $20.00, Amazon Business $15.00). The full 46 + 2 are now transcribed, rendered, and counted on
`pages/commissions.html` (F-29, closed).

Two smaller irregularities were closed alongside it: the zero-rate caption said “Nine category groups publish a
0.00 % rate”, a count that matches no grouping in Table 1 (F-30, reworded); and `tools/validate_data.py` skipped
any ledger row whose only source field is `source_id`, so every commission row — including the 48 new ones —
would have escaped the source check (F-31, fixed; the gate's row count rose 173 → 243 and was negative-tested).

**One inherited flag closed.** F-16 — four compliance rows citing controls that did not exist — was re-verified
line by line in this pass: `check_marks` (tools/validate_data.py:190), `lint()` (tools/generate_articles.py:164)
and the `expires_utc` enforcement with its test all exist and are named correctly, and R-09 now states the
solicited-email/SMS permission accurately. F-16 is closed; its full text stays on the register page.

### Unchanged

Nothing about the product rows changed. 0 of 3 supplied codes are identified as ASINs; every unsourceable field
stays blank; no price, rating, review count, BSR, availability or earnings figure is published.

