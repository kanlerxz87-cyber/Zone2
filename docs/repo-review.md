# Repository Review — Zone2

- **Repo:** https://github.com/kanlerxz87-cyber/Zone2
- **Review date:** 2026-11-13 (UTC)
- **Session:** `181863ad` (branch `arena/181863ad-zone2`)
- **Method:** line-by-line inspection of the baseline commit `f5771676f12c092c316d7b4d3051018e61db4611` plus live checks against official sources. No values inferred; anything not confirmable from an official source is left blank and flagged.

## 1. Baseline inventory (commit `f577167`)

| # | Path | Lines | Content | Status |
|---|------|-------|---------|--------|
| 1 | `README.md` | 1 | `# Zone2` | Present but empty of project information — flagged (see AF-13) |
| 2 | `.git/` | — | Git metadata, single commit `f577167 Initial commit` | OK |

**Total tracked files at baseline: 1.** No source code, no data files, no license, no CI configuration, no GitHub Pages configuration existed before this session.

## 2. Remote / GitHub configuration (verified via official GitHub API)

| Item | Value | Source | Status |
|------|-------|--------|--------|
| Default branch | `main` | `GET https://api.github.com/repos/kanlerxz87-cyber/Zone2` | OK |
| Repository visibility | public | same | OK |
| GitHub Pages enabled | yes (`status: built`) | `GET https://api.github.com/repos/kanlerxz87-cyber/Zone2/pages` | OK |
| Pages source | branch `main`, path `/` (site root) | same | OK |
| Pages URL | https://kanlerxz87-cyber.github.io/Zone2/ | same | OK |
| Build type | `legacy` (no Actions workflow; branch-based publishing) | same | OK |

## 3. Supplied product links — line-by-line verification

The brief supplied three links. Each was decomposed into its code segment and checked against official Amazon properties on **2026-11-13**.

| # | Supplied link | Code extracted | Code length | Official ASIN length | Format check |
|---|---------------|----------------|-------------|----------------------|--------------|
| 1 | `https://link.amazon/B04G1MEwY` | `B04G1MEwY` | 9 chars | 10 chars | **FAIL** |
| 2 | `https://link.amazon/B02NbDxp3` | `B02NbDxp3` | 9 chars | 10 chars | **FAIL** |
| 3 | `https://link.amazon/B00hJ57DV` | `B00hJ57DV` | 9 chars | 10 chars | **FAIL** |

Official definition of ASIN length (both state 10 characters):

- Amazon Associates help — "ASIN is the 10-digit code that Amazon uses to denote specific products": https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC
- Amazon Selling blog — "a unique 10-character alphanumeric code assigned to every product listed in the Amazon store": https://sell.amazon.com/blog/fba-new-selection-program

### 3.1 Product detail page checks (all 18 URLs returned 404 "Page Not Found")

| Code | amazon.com | amazon.co.uk | amazon.de | amazon.in | amazon.ca | amazon.co.jp |
|------|-----------|--------------|-----------|-----------|-----------|--------------|
| `B04G1MEwY` | 404 | 404 | 404 | 404 | 404 | 404 |
| `B02NbDxp3` | 404 | 404 | 404 | 404 | 404 | 404 |
| `B00hJ57DV` | 404 | 404 | 404 | 404 | 404 | 404 |

Example check URLs (each pattern was fetched for every marketplace):
`https://www.amazon.com/dp/B04G1MEwY`, `https://www.amazon.co.uk/dp/B02NbDxp3`, `https://www.amazon.co.jp/dp/B00hJ57DV`, …

### 3.2 Site search checks (official Amazon search)

| Check URL | Result |
|-----------|--------|
| `https://www.amazon.com/s?k=B04G1MEwY` | "No results for your search query." |
| `https://www.amazon.com/s?k=B02NbDxp3` | "No results for your search query." |
| `https://www.amazon.com/s?k=B00hJ57DV` | "No results for your search query." |

### 3.3 Supplied short-link behaviour (as provided in the brief)

| Supplied URL | Observed behaviour on 2026-11-13 |
|--------------|-----------------------------------|
| `https://link.amazon/B04G1MEwY` | Opened `https://www.amazon.com/dp/B0CDY277D3?…&plpRedirect=mhFallback` — a real, live product page. |
| `https://link.amazon/B02NbDxp3` | Opened `https://www.amazon.com/dp/B09B7SB46R?…&plpRedirect=mhFallback` — a real, live product page. |
| `https://link.amazon/B00hJ57DV` | Opened `https://www.amazon.com/dp/B08DKYBTPH?…&plpRedirect=mhFallback` — a real, live product page. |
| `https://link.amazon/` (root) | HTTP 403 Forbidden. |
| `https://link.amazon/robots.txt` | HTTP 403 Forbidden. |

DNS for `link.amazon` resolves (observed: CloudFront addresses `18.172.170.59/20/77/98`). The supplied codes
do not resolve to matching product pages, but each supplied URL does open one live listing.

> **Corrected 2026-11-14 (sessions `c6e94e8d`, `bbe4ca47`, `a133aa61`).** The three destinations were
> originally labelled "unrelated product / homepage fallback" on the strength of the `plpRedirect=mhFallback`
> marker. A control test refutes that reading: a **bare, untagged** request to a valid ASIN
> (`/dp/B08DKYBTPH`) also comes back with `lv=shuf&channelId=500&plpRedirect=mhFallback&th=1` appended, and
> re-fetches of the supplied links return the same ASIN and the same page body every time. The marker is
> therefore **not** evidence of a fallback, and the destinations are stable. What remains open is narrower
> and still flagged: no public Amazon document binds a short code to a destination ASIN, the per-link
> `btn_ref` token is **not** stable across days (F-21), and no resolved URL carries an Associates `tag`. See
> [`revalidation/`](../revalidation/index.html).

### 3.4 Exact-match public web searches

Exact-phrase searches for `"B04G1MEwY"`, `"B02NbDxp3"`, and `"B00hJ57DV"` returned **no matching product listings** — only unrelated results.

### 3.5 Conclusion for the three products

**0 of 3 products could be identified from any official source.** Product name, price, rating, review count, category, best-seller rank, availability, and product-specific commission rate are therefore **left blank and flagged as unverified** on every page of the site. See `flagged-for-review.html` items AF-01 … AF-08.

## 4. Irregularities flagged for review

| ID | Irregularity | Evidence | Blocking? |
|----|--------------|----------|-----------|
| AF-01 | Code `B04G1MEwY` is 9 characters; not a valid 10-character ASIN | §3; official ASIN definition links in §3 | No — flagged |
| AF-02 | Code `B02NbDxp3` is 9 characters; not a valid 10-character ASIN | §3 | No — flagged |
| AF-03 | Code `B00hJ57DV` is 9 characters; not a valid 10-character ASIN | §3 | No — flagged |
| AF-04 | All 18 official `/dp/<code>` URLs return HTTP 404 | §3.1 | No — flagged |
| AF-05 | Official Amazon search returns "No results" for all three codes | §3.2 | No — flagged |
| AF-06 | Supplied `link.amazon/<code>` URLs open a stable listing each, but no public Amazon document ties a code to its destination and the `btn_ref` token changes between days | §3.3, [`revalidation/`](../revalidation/index.html) | No — flagged |
| AF-07 | No product attributes (name/price/rating/reviews/category) confirmable → all product data cells blank | §3.4–§3.5 | No — flagged |
| AF-08 | Per-product commission rate unknown (product category unknown) | Rate card is category-based only: https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ | No — flagged |
| AF-09 | Associates Commission Income Schedule requires an Associates sign-in (observed redirect to sign-in) | https://affiliate-program.amazon.com/help/operating/schedule | No — flagged |
| AF-10 | Product-research automation (Creators API) requires an accepted Associates account + ≥10 qualifying sales in prior 30 days | https://affiliate-program.amazon.com/creatorsapi/docs/en-us/introduction | No — flagged |
| AF-11 | Legacy PA-API 5 is deprecated (HTTP 403 `AccessDeniedException` if called) | https://affiliate-program.amazon.com/creatorsapi/docs/en-us/paapiv5-deprecation | No — flagged |
| AF-12 | No Amazon Associates Tracking ID (`tag`) was supplied → no commissioned affiliate links can be generated yet | Official link format requires `tag=YOURASSOCIATEID`: https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC | No — flagged |
| AF-13 | Baseline repo contained only a one-line README; no pre-existing product list, data, or code referenced by the brief | §1 | No — flagged |

None of the flagged items block publication. All are listed with source links on the site's **Flagged for Review** page.

## 5. Sources used for this review (all official)

| # | Source | URL |
|---|--------|-----|
| 1 | Amazon Associates — simple text link format + ASIN definition | https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC |
| 2 | Amazon Selling — ASIN = unique 10-character code | https://sell.amazon.com/blog/fba-new-selection-program |
| 3 | Amazon Associates — Standard Commission Income rates (rate card) | https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ |
| 4 | Amazon Associates — Commission Income Schedule (sign-in required) | https://affiliate-program.amazon.com/help/operating/schedule |
| 5 | Amazon Creators API — introduction & prerequisites | https://affiliate-program.amazon.com/creatorsapi/docs/en-us/introduction |
| 6 | Amazon Creators API — PA-API 5 deprecation notice | https://affiliate-program.amazon.com/creatorsapi/docs/en-us/paapiv5-deprecation |
| 7 | GitHub REST API — repository + Pages configuration | https://api.github.com/repos/kanlerxz87-cyber/Zone2 |
| 8 | Official Amazon marketplace product/search pages (18 × 404, 3 × no-results) | `https://www.amazon.<tld>/dp/<code>`, `https://www.amazon.com/s?k=<code>` |

Verification performed: every URL above was fetched live on 2026-11-13; page titles/status codes recorded in §3 of this document and mirrored on `verification.html`.

---

# Second review — 2026-11-14 (session `bbe4ca47`)

An independent line-by-line pass over the *live* repository, run a day after the integration above. Every
fact was re-read from the official page rather than from the previous session's notes. Method: fetch each
cited official page, diff it against what the site publishes, and re-check every control the compliance
ledger claims exists by grepping the code.

## R1. What was re-verified and held

| Claim under test | Result 2026-11-14 | Official source |
|---|---|---|
| Table 1 commission rates (11 rows) | Match exactly, including `Coach 0.00%` and `All Other Categories 4.00%` | https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ |
| The 9 published bounty rates | All match (`$12/$12/$12/$12/$12/$12/$2/$5/$0.25`) | same |

> **Note added 2026-11-14 (session `d3ce1c29`, task T26).** The nine bounty rates checked here were
> correct, but they were only the first nine of the set. Re-reading S04 in full shows it publishes
> **46** rows under “(a) Bounty Events” and **2** more under “(b) Bonus Events”, so the page's
> “transcribed row-by-row” notice overstated what had been transcribed. All 46 + 2 are now published
> on `pages/commissions.html`; see flag **F-29** and `tools/apply_bounty_completion_2026_11_14.py`.
> This row is left as written because it is an accurate record of what this review checked.
| Trade-In rates, fine-art $200 cap, free-Kindle limit | Match verbatim | same |
| 24 h session · 89-day cart · 180-day fulfilment · ~60-day payment · US payment minimums · 3-year inactivity | Match Commission Income Statement §1 and §6 | https://affiliate-program.amazon.com/help/operating/policies |
| Disclosure sentence | Verbatim match with §5 | https://affiliate-program.amazon.com/help/operating/agreement |
| "Up to 10%" ceiling and ≈60-day payout | Match the program home page | https://affiliate-program.amazon.com/ |
| Agent Terms (`Agent/[agent name]`, no CAPTCHA circumvention, answer verification prompts truthfully) | Match IP License §4 | https://affiliate-program.amazon.com/help/operating/policies |
| Price/availability display rule and the "lowest new price" comparison rule | Match Participation Requirements §2(b) | same |
| Creators API prerequisites (enrolled; ≥10 qualifying sales in the past 30 days; register; credentials) | Match verbatim | https://affiliate-program.amazon.com/creatorsapi/docs/en-us/introduction |
| PA-API 5 deprecated, returns `403 AccessDeniedException` | Match verbatim, including the error shape | https://affiliate-program.amazon.com/creatorsapi/docs/en-us/paapiv5-deprecation |
| ASIN is a 10-character code | Match verbatim | https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC |
| `rel="sponsored"` for affiliate links | Match | https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links |
| FTC "you can't talk about your experience with a product you haven't tried" | Match | https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers |
| `/dp/B04G1MEwY`, `/dp/B02NbDxp3`, `/dp/B00hJ57DV` | All three still return Amazon's "Page Not Found" | the three `amazon.com/dp/` URLs |
| Where the three `link.amazon` links land | Unchanged from 2026-11-13 and stable per link: `B04G1MEwY`→`B0CDY277D3`, `B02NbDxp3`→`B09B7SB46R`, `B00hJ57DV`→`B08DKYBTPH`, each with its own `btn_ref` | those three product pages |
| Whether `plpRedirect=mhFallback` proves a fallback | **No.** A bare request to a valid ASIN (`/dp/B08DKYBTPH`) returns the real product page with the same marker appended. See correction note below | same |
| Chefman 6 Qt specs (8 rows) | All match the manufacturer page | https://chefman.com/products/turbofry-touch-dual-window-air-fryer |
| Chefman 8 Qt specs | Model `RJ38-SQSS-8T`, 8 Qt/7.57 L, 200–400 °F, 15.4×12.6×13.5 in, 12.8 lb, cETL, 1 year — all match; the 1700 W vs 1000 W conflict stands unresolved | https://chefman.com/products/turbofry-touch-air-fryer-1 |
| Emeril 26QT specs | Model `4-00675-02A-VN`, 26 qt/24.6 L, 16.9×15.8×14.8 in, 120 V, dual-speed fan, 1-year warranty match | https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360 |
| Internal links, all namespaces | 79 pages, 0 broken file references, 0 unresolvable anchors (checked by resolution, not by eye) | — |
| Secret scan (`AKIA`, `ghp_`, private keys, `sk-`, hard-coded tags) | 0 findings; no Associates tag is committed | — |

## R2. Irregularities found in this pass

| # | Finding | Where | Disposition |
|---|---|---|---|
| F-16 | Four compliance rows cited controls that do not exist: `site/compliance-inject.js` (R-01), `assert_no_amazon_marks` (R-11), `lint_disclosure_proximity` (R-02), `lint_claims` (R-06). R-09 also described email/SMS as absent from the schema, while the current policies *permit* solicited email/SMS/DM. | `ledger/compliance.json` | **Fixed** — rows now cite the real functions (`check_disclosure`, `check_marks`, `lint()`), and R-09 states the policy as published with the repo's stricter default labelled as self-imposed. |
| F-17 | Dashboard KPI said "3 Verified affiliate products" and "11 items flagged"; the ledger says all three submitted items are `UNVERIFIED` and holds 19 flags. Both readings were defensible in isolation and contradictory on the page. | `index.html`, `assets/js/data.js` | **Fixed** — KPI now reads `0 of 3 supplied products identified` and `3 links verified as resolving stably to one listing each`; flag count is derived from the data, never typed. (Wording revised again after the control test below: "fallback" is not supported.) |
| F-18 | CI link check never walked `pages/` (37 pages), and the disclosure/price gate covered 4 of 6 namespaces. The gate would also have failed my own permitted program-economics dollar figures, because it used a bare `\$\d+\.\d{2}` regex while the repo's policy is context-aware. | `.github/workflows/pages.yml` | **Fixed** — `pages/` and the root views added to the link check (with fragment handling), all six namespaces covered by the price/disclosure gate using the same context-aware rule as `tools/validate_data.py`. |
| F-19 | The published Emeril "conflict" row attributed the disagreement to Amazon-vs-manufacturer. The manufacturer page actually states **24** (description), **25** (spec tile) and **10-in-1** (feature block) — it contradicts itself. | `assets/js/data.js`, `ledger/flags.json` | **Fixed** — all four observations published verbatim, status stays `conflict`, per-value source named. |
| — | The dashboard claimed "Home & Kitchen category commission rate (UNVERIFIED)" and that the rate card "requires Associates sign-in". **The fixed-rate table is publicly readable**; only the per-ASIN band is unresolved. | `assets/js/data.js` | **Fixed** — the two published bands (Kitchen 4.50%, Home 3.00%) are now shown as verified, with a separate `unverified` row explaining exactly what is missing and why. |
| — | `TRACKING_ROWS` reported every campaign as `Configured`, `Monthly reconciliation` — while `ledger/campaigns.json` is `EMPTY_BY_DESIGN` and no tag exists. | `assets/js/data.js` | **Fixed** — statuses now read "Not live — blocked" / "Not live — no reports connected", with the rule for when a campaign may be called live written into the file. |
| — | The dashboard's Flagged page listed 11 reader-facing items but never linked to the 19-flag canonical register. | `flagged.html`, `assets/js/app.js` | **Fixed** — each row carries its ledger flag id and a link to the full text + sources. |
| — | A candidate finding (asserting a fabricated hands-on-testing line in `content/templates/product_article.md.tmpl`) did **not survive checking**: `grep` finds no such sentence in the template or anywhere in `content/`, `tools/` or the site. It was withdrawn before publication. | — | Recorded here for transparency; not published as a flag. |

## R3. Items deliberately left alone

- **`research-hub/scripts/verify.py`** still reports 7 false failures (F-15). Re-confirmed, not fixed: `research-hub/**` is another session's scope, and the workflow does not call it.
- **`research-hub/compliance.html` `<title>` leading with an Amazon mark** (F-13) — still a build *warning*, not an error; the rule covers domains/subdomains/tags/usernames, not page titles.
- **`.github/workflows` publishes the whole repo** including `tools/`, `ledger/` and `tests/` (I-25). Unchanged by design; no secret or personal data is present (secret scan above).
- **Price, rating, review count, BSR and availability** for the three listings remain blank. They are observable on Amazon's pages, but republishing them requires either Amazon-served link content or Creators API data (Participation Requirements §2(b)), and this workspace has neither — so they stay blank and flagged rather than being copied in.

## R4. Sources added in this pass

| Source | URL | Used for |
|---|---|---|
| Associates — Application Review Process | https://affiliate-program.amazon.com/help/node/topic/G8TW5AE9XL2VX9VM | ≥3 qualifying sales in the first 180 days; ≥10 posts; content generally within 60 days |
| Associates — simple text link / ASIN definition | https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC | ASIN = 10 characters; canonical `/dp/ASIN?tag=` |
| Chefman — TurboFry Touch 6 Qt dual-window | https://chefman.com/products/turbofry-touch-dual-window-air-fryer | 8 specification rows, re-read |
| Chefman — 8 Qt TurboFry Touch | https://chefman.com/products/turbofry-touch-air-fryer-1 | specification rows, re-read |
| Emeril Everyday — French Door AirFryer 360, 26 QT | https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360 | specification rows; the self-contradicting preset count (F-19) |

Manufacturer hosts are now explicitly allow-listed in `tools/validate_data.py` **only** when a source record
declares `kind="manufacturer"`, so they can never be used to state an Amazon-side fact.

## R5. Verification performed on the result

- `python3 tools/validate_data.py` — **0 errors**; 102 rows, 27 sources, 956 internal links, 0 price findings.
- `python3 tools/build_site.py --check` — 37 pages, **no drift**.
- `python3 tools/build_root_views.py --check` — 2 pages, **no drift**.
- `python3 tests/test_pipeline.py` — **11/11 pass**.
- `python3 affiliate-lab/scripts/verify_site.py` — 10 pages / 205 rows / 498 links / **0 failures**.
- Workflow steps simulated locally: link check **0 problems**; disclosure + price across **79 pages** **0 problems**.

## R6. Correction issued during integration — the "fallback" inference is withdrawn

While rebasing onto `main` at the end of this pass, session `c6e94e8d`'s controlled re-test landed
(`docs/revalidation-2026-11-14.md`, `revalidation/`). It tests the inference that the earlier passes here
leaned on, and the inference fails:

- A **bare, untagged** request to a *valid* ASIN (`/dp/B08DKYBTPH`, `/dp/B0CDY277D3`) is answered with the real
  product page **and the same `lv=shuf&plpRedirect=mhFallback` markers** appended. `mhFallback` is Amazon's own
  link-rewrite plumbing, not evidence of a fallback.
- Re-fetching a short link returns the **same** ASIN, body and per-link `btn_ref`. The "different token on
  re-fetch" observation published on 2026-11-13 does **not** reproduce.

This session reproduced both results independently on 2026-11-14 before accepting them. Consequences applied:

| Item | Action |
|---|---|
| `ledger/flags.json` F-03 | **Downgraded** high → medium and retitled; detail now states what reproduced (9-char codes, `/dp/` 404s, stable per-link destinations, no `tag=`) and what did not (that the token was "not honoured"). |
| `ledger/flags.json` F-12 | **Withdrawn**, kept in the register rather than deleted so the record shows the site carried an unsupported claim for a day. |
| `ledger/products.json` | `why_blank` no longer cites `mhFallback`; each entry now records `resolves_to` (the listing the link lands on) as an observation, explicitly not as the requested product. |
| `assets/js/data.js` | The three "link-code / ASIN mismatch" rows now say the destination is stable per link *and* that no public document binds code to ASIN. |
| `verification.html` | Carries the control test as its own row. |
| KPI wording | "3 fallback landing pages verified" → "3 links verified as resolving stably to one listing each". |

Change requests CR-1 … CR-4 from that session are therefore **closed**: only one owner holds `ledger/**`, so
they could not be applied by the requesting session, and they are applied here.

**Net position, restated precisely.** The three supplied codes are not ASINs and do not resolve as ones. The
three short links resolve stably, one product each, but carry no Associates tag and no public document binds
the code to the destination. So the destinations remain *not established* as the requested products — on the
narrower, documented ground rather than on the retracted "fallback" reading.
