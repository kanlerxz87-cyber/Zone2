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
| `https://link.amazon/B04G1MEwY` | Redirected into `https://www.amazon.com/dp/B0CDY277D3?…&plpRedirect=mhFallback` — the CHEFMAN 6 Qt product page. **Re-verified 2026-11-14:** the same destination ASIN on every fetch. |
| `https://link.amazon/B02NbDxp3` | Redirected into `https://www.amazon.com/dp/B09B7SB46R?…&plpRedirect=mhFallback` — the Emeril Lagasse 26QT product page. **Re-verified 2026-11-14:** the same destination ASIN on every fetch. |
| `https://link.amazon/B00hJ57DV` | Redirected into `https://www.amazon.com/dp/B08DKYBTPH?…&plpRedirect=mhFallback` — the Chefman 8 Qt product page. **Re-verified 2026-11-14:** the same destination ASIN on every fetch. |
| `https://link.amazon/` (root) | HTTP 403 Forbidden. |
| `https://link.amazon/robots.txt` | HTTP 403 Forbidden. |

DNS for `link.amazon` resolves (observed: CloudFront addresses `18.172.170.59/20/77/98`). The supplied codes do not resolve to matching product pages — each is 9 characters and `amazon.com/dp/<code>` is a 404 — but each short link does resolve to one product, deterministically.

> **Correction (2026-11-14).** This section originally described the three destinations as
> "an unrelated product / homepage fallback". That reading rested on the `plpRedirect=mhFallback`
> marker, and it does not survive a control test: a bare, untagged fetch of a **valid** ASIN
> (`https://www.amazon.com/dp/B0CDY277D3`) returns the real product page and carries the same
> `plpRedirect=mhFallback` and `lv=shuf` markers. Re-fetching each short link returns the same
> destination ASIN and the same page body; only the per-request `srctok` attribution token
> rotates between days. The destinations are therefore stable, individually tracked links — not
> arbitrary fallbacks. What is still open: no public Amazon document binds a `link.amazon` code to
> a destination ASIN, so the mapping is observed behaviour rather than documented intent.

### 3.4 Exact-match public web searches

Exact-phrase searches for `"B04G1MEwY"`, `"B02NbDxp3"`, and `"B00hJ57DV"` returned **no matching product listings** — only unrelated results.

### 3.5 Conclusion for the three products

**0 of 3 products could be identified from the supplied codes** — each code is 9 characters, is not an addressable ASIN, and returns a 404 at `amazon.com/dp/<code>`. Each *short link* does resolve to one product, deterministically and repeatably (re-verified 2026-11-14), and the product's name, brand and category path are published from its own Amazon product page. Price, rating, review count, best-seller rank, availability and the product-specific commission rate are **left blank and flagged as unverified** on every page of the site. See `flagged-for-review.html` items AF-01 … AF-08.

## 4. Irregularities flagged for review

| ID | Irregularity | Evidence | Blocking? |
|----|--------------|----------|-----------|
| AF-01 | Code `B04G1MEwY` is 9 characters; not a valid 10-character ASIN | §3; official ASIN definition links in §3 | No — flagged |
| AF-02 | Code `B02NbDxp3` is 9 characters; not a valid 10-character ASIN | §3 | No — flagged |
| AF-03 | Code `B00hJ57DV` is 9 characters; not a valid 10-character ASIN | §3 | No — flagged |
| AF-04 | All 18 official `/dp/<code>` URLs return HTTP 404 | §3.1 | No — flagged |
| AF-05 | Official Amazon search returns "No results" for all three codes | §3.2 | No — flagged |
| AF-06 | Supplied `link.amazon/<code>` URLs resolve to one product each, but no public Amazon document binds a code to a destination ASIN — the mapping is observed behaviour, not documented intent | §3.3 | No — flagged |
| AF-07 | No product attributes (name/price/rating/reviews/category) confirmable → all product data cells blank | §3.4–§3.5 | No — flagged |
| AF-08 | Per-ASIN commission rate unknown. The category band is published (Table 1: "Physical Books, Kitchen, Automotive" = 4.50%; the three products sit at Kitchen & Dining), but the rate Amazon applies to one ASIN lives in the account rate card | https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ · https://affiliate-program.amazon.com/help/operating/schedule | No — flagged |
| AF-09 | The **account** Commission Income Schedule requires an Associates sign-in (observed redirect to sign-in). The **public** Standard Commission Income Statement is readable without signing in and publishes the full Table 1 rate bands | https://affiliate-program.amazon.com/help/operating/schedule · https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ | No — flagged |
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
