# Executive summary

**Project:** Amazon affiliate marketing platform and product research site
**Repository:** `kanlerxz87-cyber/Zone2`
**Branch:** `arena/6602723a-zone2` (from `main` @ `f577167`)
**Data captured:** 2026-11-13 (UTC)
**Live site:** https://kanlerxz87-cyber.github.io/Zone2/

---

## 1. What was asked for

The brief asked for an AI-powered Amazon affiliate platform that would automate product
research, find trending and high-converting products, analyse price, reviews, competition and
commission potential, write SEO content, publish and manage affiliate links, track clicks and
conversions, and continuously optimise campaigns — with automation, scalability, data-driven
decisions and Amazon Associates compliance as the priorities. It supplied three affiliate links
and required that every table row link to an official source, that unconfirmable values be left
blank and flagged, and that everything be verified without hallucination.

## 2. What this project actually is

A **verified, source-linked research site** for the three supplied products, plus an honest map of
which parts of the brief Amazon's own policies permit.

This is a deliberate narrowing. Several requested capabilities cannot be built lawfully as
specified, and building a convincing-looking version of them would have meant inventing data.
The value delivered is the opposite: a small dataset where every single published number can be
clicked back to the page it came from, and every gap is visible.

## 3. The three products

> **Correction (2026-11-14 re-verification):** the original text of this section stated that the three
> supplied short links "resolved successfully to canonical Amazon ASINs" and framed the destinations
> as "a coherent niche." The destinations below are the products each supplied link **resolves to**
> (verified on the official Amazon product page), but each supplied code is **9 characters — not a
> valid ASIN** (an ASIN is 10) — and `amazon.com/dp/<code>` returns Page Not Found. The
> code→product mapping is therefore **flagged for confirmation** (F-01/F-02/F-03/F-12); it is not a
> valid-ASIN match. The "countertop air frying" niche reading is an inference from the resolved
> destinations and is not asserted as a verified finding. The canonical, current executive summary is
> [`EXECUTIVE_SUMMARY.md`](../EXECUTIVE_SUMMARY.md) at the repo root. The original wording is preserved
> below for the record.

The three supplied `link.amazon/*` short links each resolved (following the redirect) to an Amazon
product page. Full short-link text was resolved by following the redirect, because the ASIN is not
readable from the short link itself. The destinations observed are listed below as **resolved
destinations (flagged for confirmation)**; each code is not itself a valid ASIN.

| # | Supplied link | Resolved ASIN (flagged) | Resolved product | Brand |
|---|---|---|---|---|
| 1 | `link.amazon/B04G1MEwY` | B0CDY277D3 | 6 Quart Dual Basket Air Fryer, dual viewing windows, Sync Finish | Chefman |
| 2 | `link.amazon/B02NbDxp3` | B09B7SB46R | 26QT French Door Multi-Function Air Fryer Toaster Oven | Emeril Lagasse |
| 3 | `link.amazon/B00hJ57DV` | B08DKYBTPH | 8 Qt TurboFry Touch air fryer, stainless steel | Chefman |

The resolved destinations all sit in the air-fryer space, but a "coherent niche: countertop air
frying" reading is an **inference drawn from the resolved destinations**, not a verified finding about
the supplied codes, and is therefore not asserted (see flag F-12).

## 4. Verified facts, and the limits of them

> **Scope note (2026-11-14):** the attributes below are verified for the **resolved destination
> ASINs** (the products each supplied link resolves to). They are accurate about those ASINs, but the
> supplied codes are not valid ASINs, so these specs describe the resolved destinations, not a
> confirmed valid-ASIN match for the supplied codes (F-01/F-02/F-12).

Every published attribute has a named official source: the Amazon product page for that exact
ASIN, or the manufacturer's own product page for the model number printed on it.

Published and verified, per product:

- **Chefman 6 Qt dual basket (B0CDY277D3)** — model RJ38-SQPF-3TDB-2W; 6 qt across two
  independent 3-qt baskets; 1700 W / 120 V; 200–450 °F; cETL; 1-year assurance. Source: Chefman.
- **Emeril Lagasse 26QT (B09B7SB46R)** — 26 qt / 24.6 L; 1700 W / 120 V; 75–500 °F; French doors;
  7 accessories; 1-year warranty. Sources: Amazon product information and Emeril Everyday.
- **Chefman 8 Qt (B08DKYBTPH)** — model RJ38-SQSS-8T; 8 qt / 7.57 L; 1700 W / 120 V; 200–400 °F;
  four presets; cETL; 1-year assurance. Source: Chefman.

Deliberately **not** published, with the reason:

| Data | Published? | Reason |
|---|---|---|
| Price | No | Amazon allows price display only where Amazon serves it or it comes from the official API, and requires a timestamp plus a disclaimer. |
| Star rating | No | Ratings are storefront-specific. B09B7SB46R shows 4.5 / 16,128 on Amazon.co.uk against 4.6 / 8,361 on Amazon.sa. Any single figure would mislead. |
| Review count | No | Same reason; also drifts continuously. |
| Stock status | No | Changes by the minute. |
| Commission rate | No | The official rate card requires an Associates login and could not be read. |
| Conversion rate, sales volume, "trendiness" | No | Not published by Amazon for third-party listings. No official source exists, so no figure is stated. |

## 5. Irregularities found — the headline items

These are the findings that most affect the owner.

**O-1 — The supplied links carry no Associates tracking tag.** All three resolved to plain
`amazon.com/dp/<ASIN>` URLs. Without a `tag=` parameter, clicks cannot be attributed and no
commission can be earned. This is the single most commercially important finding in the project.
Fix: re-generate the links in Associates Central with the Store ID and update
`data/products.json`.

**O-2 — The commission rate card is login-gated.** The official schedule at
`affiliate-program.amazon.com/help/operating/schedule` redirects to sign-in. Amazon's public page
states only "Earn up to 10% in associate commissions". Every blog confidently quoting "3% for
Home" is quoting something this project could not verify, so no rate is published here.

**O-3 — No repository licence.** The repo has no `LICENSE` file. Owner decision.

**O-4 — Affiliate account not evidenced.** The disclosure statement is published because the
brief frames this as an Amazon affiliate project. Only the account holder can confirm an approved
Associates account exists. The 3-sale / 180-day review applies.

**O-5 — Content refresh deadline of roughly 2027-01-12.** Amazon expects site content to be
recent, generally within the last 60 days. The capture is dated 2026-11-13.

### Conflicts between official sources

| ID | Product | Conflict |
|---|---|---|
| I-8 | Chefman 8 Qt | Amazon's bullet text says 1000 W; Chefman says 1700 W for the same model number RJ38-SQSS-8T. Manufacturer figure published, discrepancy flagged. |
| I-9 | Chefman 8 Qt | Dimensions: 12.75 × 13.5 × 10 in on Amazon against 15.4 × 12.6 × 13.5 in from Chefman. Both published as separate sourced rows. |
| I-10 | Emeril 26QT | Model number suffix: `-02X-VN` on Amazon US against `-02A-VN` on the manufacturer store. Both published. |
| I-12 | Emeril 26QT | Preset count: 24 in the title and description, 25 in the manufacturer's own spec tile. Both shown. |
| I-13 | Emeril 26QT | 500 °F maximum is sourced to Amazon's product information only; the manufacturer states temperature control without a numeric maximum. |

### Values left blank because nothing official confirms them

- Chefman 6 Qt UPC (`810087845025`) — appeared only in reseller listings.
- Emeril 26QT UPC (`752356835682`) — same.
- Emeril 26QT item weight — regional listings give 10.21 kg, 12.02 kg and 26.5 lb in different
  places; not confirmed on the US page or the manufacturer page.
- Chefman 6 Qt star rating — the Amazon page did not render its own rating block, and the figure
  visible on the page belongs to a sibling listing. Not attributed.

## 6. The compliance position, which shapes everything

Amazon's Associates terms are unusually specific, and four points dominate.

1. **Disclosure is mandatory and the wording is prescribed.** "As an Amazon Associate I earn from
   qualifying purchases." It appears in a bar at the top of every page of this site, unmodified.
2. **Prices cannot be republished freely.** A site may show price and availability only where
   Amazon serves the link displaying them or the data comes from the official API, and any
   displayed price needs a timestamp and a disclaimer. This site therefore links out and says the
   price on Amazon is the price that applies.
3. **Tracking tags are mandatory.** Every Special Link must carry the associate's own ID. The site
   does not invent one.
4. **Automated access is governed by the "Agent Terms".** An Agent — any software taking
   autonomous or semi-autonomous action — must identify itself in the user agent as
   `Agent/[agent name]`, must not conceal that access is automated, and must not solve or
   circumvent CAPTCHAs or blocking measures. **This is why "fully automate everything" was not
   implemented as literally requested.** A platform that silently scrapes the storefront at scale
   would breach the terms that make the commission possible in the first place.

## 7. Requirement dispositions

Sixteen requirements were extracted from the brief and each given an honest disposition.

| Disposition | Count | Meaning |
|---|---|---|
| Delivered | 7 | Built and verifiable in the repo |
| Constrained by Amazon policy | 7 | Requested; built the compliant alternative |
| Owner decision needed | 1 | Click and conversion tracking — requires the account holder |
| Not deliverable | 1 | Trending / high-converting identification — no official public source exists |

No requirement is marked delivered unless the artefact exists in this repository. The full
line-by-line table is at `requirements.html`.

## 8. What was built

| Artefact | Purpose |
|---|---|
| `data/products.json` | The verified dataset. Every value carries its own status and source URL. |
| `data/compliance.json` | Amazon's rules, quoted, sectioned and linked. |
| `data/requirements.json` | Disposition of every clause of the brief. |
| `data/sources.json` | Source registry with a three-tier trust model and a list of rejected sources. |
| `data/raw-verification-log.md` | Raw capture log: what each page actually said. |
| `scripts/build.py` | Generates the static site from the JSON. No page can state a fact absent from the data. |
| `scripts/verify.py` | CI guard. Fails the build on an unsourced row, a non-https source, a broken internal link, a missing disclosure, or a printed price. |
| `site/` | The GitHub Pages site: overview, products, comparison, compliance, requirements, method, flagged, executive summary. |
| `COORDINATION.md` | Shared task board and irregularity log, as the brief required. |

## 9. Commercial reality, stated plainly

The plausible revenue here is small in absolute terms and the brief's framing of "maximise
affiliate revenue" through automation overstates what is available.

- The category is **home and kitchen appliances**, one of the lower-paying Amazon categories. The
  exact rate is behind the login gate, but no source this project could verify suggests a
  high-value category rate.
- A single-digit-percent category rate applied to the low-to-mid hundreds in order value these
  appliances typically carry produces a commission per sale measured in single-digit currency
  units, not tens of them. That arithmetic is illustrative and is **not** a projection — no rate
  is verified, and no currency figure is published on the site, by design.
- The **24-hour session** with an **89-day cart window** is the real leverage: a click that adds
  something to a cart can pay for weeks. Content that converts on "which air fryer should I buy"
  is therefore worth more than content optimised per-product.
- **Three products is not a business.** Amazon's own review bar is a rule of thumb of at least ten
  posts, and content must be recent — generally within 60 days. This is a seed dataset and a
  working pipeline, not a finished channel.

## 10. Recommended next steps, in order

1. **Fix the links first (O-1).** Nothing else matters commercially until a tracking tag exists.
2. **Read the rate card from inside the account (O-2)** and record the Home-category rate with its
   date. Only then can any revenue model be honest.
3. **Re-capture before 2027-01-12 (O-5)** and diff against this dataset; the CI guard will show
   exactly which rows changed.
4. **Pick a licence (O-3).**
5. **Scale content only after the three above.** Adding a fourth product is one JSON object; the
   navigation and tables rebuild themselves.
6. **If automation is scaled, use the official Creators API / PA API,** not scraping. The Agent
   Terms make that the only durable path.

## 11. Honest limitations

- No product was tested. Nothing here is a performance claim.
- Capture is a single point in time.
- Amazon product pages render inconsistently to automated fetches; where the US body did not
  render, the same ASIN's page on another Amazon storefront was used for the product-information
  block and the manufacturer for specifications. This is disclosed per product.
- Non-official sources were used only to locate official ones, and every rejected source is listed
  with its reason in `data/sources.json`.
- The site loads no analytics and sets no cookies, so no traffic or conversion data exists for
  this project yet.

## 12. Bottom line

The brief asked for automation. The honest deliverable is **verifiability**: three products
resolved, documented and cross-checked against official pages; every conflict surfaced instead of
smoothed over; every gap left blank and listed; and a compliance position that will survive an
Amazon review. The one thing that must happen next is not technical — the affiliate links need a
tracking tag before any of this can earn anything.
