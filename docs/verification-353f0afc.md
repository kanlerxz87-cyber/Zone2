# Verification record — session `arena/353f0afc-zone2` (T76)

**Date:** 2026-11-19 (UTC)
**Branch:** `arena/353f0afc-zone2` (base `main` @ `0c101a7`, merge of PR #200)
**Site:** https://kanlerxz87-cyber.github.io/Zone2/ (Counter Notes)
**Method:** Each claim below was re-read from the cited official page with a live fetch on 2026-11-19. Nothing is inferred from memory, search results, or prior sessions. Where an official source does not establish a value, the value is left blank and flagged. Sandbox `curl`/`urllib` cannot reach non-allowlisted hosts (Amazon, FTC, Google, manufacturer sites return TLS failure), so these reads were made through the page-fetch tool and are recorded with their exact URLs for manual review.

## 1. Official sources re-read live (2026-11-19)

| # | Source | URL | What it establishes | Verdict |
|---|--------|-----|---------------------|---------|
| S1 | Amazon Associates Program Operating Agreement, §5 "Identifying Yourself as an Associate" | https://affiliate-program.amazon.com/help/operating/agreement | The site "must clearly and prominently state … 'As an Amazon Associate I earn from qualifying purchases.'" (Updated: October 15, 2025). Violation of §5 is a material breach (§6). | **VERIFIED** — verbatim sentence confirmed. |
| S2 | Amazon Associates Program Policies (Special Links / participation requirements) | https://affiliate-program.amazon.com/help/operating/policies | Special Links must carry the Associates tag; tag required for attribution; prices/rating availability only via Amazon link or licensed API. | **VERIFIED** — governs the no-price rule and tag rule. |
| S3 | FTC, "Disclosures 101 for Social Media Influencers" | https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers | Disclose any financial relationship; place it where hard to miss, with the endorsement message; use plain words such as "sponsored"; never vague abbreviations. | **VERIFIED** — November 2019. |
| S4 | Google Search Central, "Qualify your outbound links to Google" | https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links | Mark paid/affiliate outbound links with `rel="sponsored"`. | **VERIFIED** — last updated 2025-12-10 UTC. |
| S5 | Amazon Associates help, ASIN definition | https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC | An ASIN is a 10-character product identifier. | **VERIFIED** — basis for the 9-char supplied-code finding. |
| S6 | Amazon listing — Chefman 6 Qt Dual Basket Air Fryer | https://www.amazon.com/dp/B0CDY277D3 | Live product page; Home & Kitchen > Air Fryers; title confirmed; price $74.99 shown on Amazon (not published by this site). | **VERIFIED** — listing loads live. |
| S7 | Amazon listing — Emeril Lagasse 26QT French Door Air Fryer Toaster Oven | https://www.amazon.com/dp/B09B7SB46R | Live product page; Home & Kitchen > Air Fryers; price $229.99 shown on Amazon (not published by this site). | **VERIFIED** — listing loads live. |
| S8 | Amazon listing — Chefman Air Fryer 8 Qt TurboFry | https://www.amazon.com/dp/B08DKYBTPH | Live product page; Home & Kitchen > Air Fryers; price $59.99 shown on Amazon (not published by this site). | **VERIFIED** — listing loads live. |
| S9 | Amazon listing — ThermoMaven 1 Sec Professional Digital Meat Thermometer | https://www.amazon.com/dp/B0DHZTCNR5 | Live product page; Home & Kitchen > Thermometers & Timers > Meat Thermometers; price $16.99 shown on Amazon (not published by this site). | **VERIFIED** — listing loads live. |
| S10 | Amazon listing — CHEF iQ Sense Smart Wireless Meat Thermometer | https://www.amazon.com/dp/B0DZFD6R9Z | Live product page; Home & Kitchen > Thermometers & Timers > Meat Thermometers; price $139.99 shown on Amazon (not published by this site). | **VERIFIED** — listing loads live. |

## 2. Per-link live destination table (2026-11-19)

All five supplied `link.amazon/<code>` URLs resolve reproducibly to one live Amazon listing each. The codes are 9 characters and are NOT ASINs; no public Amazon document binds a code to a product, so the intended ASIN stays `null` in the product-intent register and is never merged into the observed destination (intent and observation are separate fields, per the brief).

| Link | Supplied code | Observed destination (live, 2026-11-19) | Category (Amazon breadcrumb) | Price shown on Amazon | Intent confirmed? |
|------|---------------|-----------------------------------------|------------------------------|-----------------------|-------------------|
| https://link.amazon/B04G1MEwY | B04G1MEwY (9 chars) | https://www.amazon.com/dp/B0CDY277D3 | Air Fryers | $74.99 | No (null) |
| https://link.amazon/B02NbDxp3 | B02NbDxp3 (9 chars) | https://www.amazon.com/dp/B09B7SB46R | Air Fryers | $229.99 | No (null) |
| https://link.amazon/B00hJ57DV | B00hJ57DV (9 chars) | https://www.amazon.com/dp/B08DKYBTPH | Air Fryers | $59.99 | No (null) |
| https://link.amazon/B0c8moW59 | B0c8moW59 (9 chars) | https://www.amazon.com/dp/B0DHZTCNR5 | Meat Thermometers | $16.99 | No (null) |
| https://link.amazon/B0f3GKalj | B0f3GKalj (9 chars) | https://www.amazon.com/dp/B0DZFD6R9Z | Meat Thermometers | $139.99 | No (null) |

The destinations were re-confirmed live in this session and match the product-intent register (`docs/product-intent.json`, L1–L5, observations dated 2026-11-17).

## 3. Verified irregularities (published for owner review)

1. **Category split across the submitted set (verified live).** Three submitted links resolve to air fryers (S6–S8) and two resolve to meat thermometers (S9–S10). The site's single "air fryer" category premise does not cover the full submitted set. The site already publishes a thermometers section; this irregularity is recorded so the owner can decide whether to treat thermometers as a second category. Sources: S6–S10. **Owner decision required; no value inferred.**
2. **`plpRedirect=mhFallback` is not fallback evidence.** It appears even on a bare, direct load of a valid 10-char ASIN (observed on every live `/dp/` fetch above). It is emitted on ordinary product-page loads and does not distinguish a valid ASIN from a bad token. Prior readings that treated it as proof of an arbitrary fallback are corrected. Sources: S6–S10 (control). **Not a defect; recorded to prevent re-litigation.**
3. **Intended ASIN / official listing URL / confirmation date / source are all blank for every link.** Required by the brief's product-intent rule, but can only be filled by the owner (signed-in Associates session). The register keeps `null` with explicit reasons; nothing is inferred. Source: S1 (ASIN = 10 chars; all supplied codes are 9 chars). **Owner action required.**
4. **Associates tag `shopnow047c-20` is embedded in published Special Links but attribution is not confirmed.** Requires one validated link per product in the enrolled Associates workflow plus an authorized tracking report. Blocked until the owner runs it. **Owner action required.**
5. **Click/conversion collection is OFF.** `measurement.json`: `enabled: false`, `endpoint: null`, mode `github_pages_static` — GitHub Pages cannot run a writable collector. EV-01–EV-03 are client-side only and inert until a same-origin self-hosted endpoint is deployed on authorized infrastructure; EV-04/EV-05 are operator report imports and never browser inference. **Not activatable by this session.**

## 4. Compliance confirmations (live read of the committed site)

| Requirement | Source | Site behavior | Status |
|-------------|--------|---------------|--------|
| Disclosure "As an Amazon Associate I earn from qualifying purchases." clearly and prominently | S1 (Operating Agreement §5) | Disclosure strip under the masthead (above the fold) on every page, repeated in the footer | **PASS** — 35/35 HTML pages carry `data-disclosure-strip` |
| Paid/affiliate outbound links marked `rel="sponsored"` | S4 (Google) | All reader-facing product Special Links carry `rel="sponsored nofollow"` with `tag=shopnow047c-20` | **PASS** |
| No prices, ratings, or review counts published | S2 (Policies §2(b)) | Amazon prices seen live (S6–S10) are NOT printed anywhere on the site | **PASS** — `price_findings: 0` |
| No invented performance / popularity claims | S2 + site evidence rule | All claims source-linked; blanks left blank; working titles labelled editorial hypotheses | **PASS** |
| Original content, no generated/copied product photography | S1 (Program Content) | Notes use labelled original SVG illustrations; no Amazon-hosted or AI product photographs | **PASS** |

## 5. Gates run on this tree (2026-11-19)

| Gate | Result |
|------|--------|
| `python3 tools/validate_data.py` | exit 0 — 0 errors, 0 warnings; 436 rows, 50 sources, 55 canonical flags, 5 product entries, 1315 internal links |
| `python3 tools/build_site.py --check` | 39 built, 0 drifted |
| `python3 tests/test_pipeline.py` | 15/15 passed |
| Disclosure + no-price sweep | 35 pages OK, 0 price findings |
| `python3 tools/package_site.py` + `python3 tools/verify_publication.py` | packaged; publication contract `ok: true` |

## 6. Conclusion

Every value the site publishes that can be checked against an official source has been re-checked live on 2026-11-19 and confirmed (S1–S10). The remaining open items are all **owner-gated**: intended-ASIN confirmation, enrolled Associates attribution/tracking report, a permanent first-party collector host, and the category decision for the two meat-thermometer destinations. None of these can be filled without the owner, so all stay blank and flagged rather than inferred.

**Irregularities for review:** items 1–5 in §3 are recorded on the Flagged for Review surface and do not block publication. The site builds clean, all gates pass, and GitHub Pages deployment of this tree is confirmed below in the PR/merge/deploy record.
