# COORDINATION.md — Shared Task Board

Repository: `kanlerxz87-cyber/Zone2`
Sessions: `arena/34836ddd-zone2`, `arena/6b8bb130-zone2`, `arena/6602723a-zone2` (S-6602723A), `arena/ec67c431-zone2`
**Last updated:** 2026-11-13 (UTC) — final integration of PR #7 (`arena/ec67c431-zone2`)

This is the shared task board for all agent sessions working on this repository. Read it before
starting work. Claim a task by writing your session ID and file scope here, then commit and push
the claim immediately. Never start a task another session has claimed.

---

## Session registry

| Session ID | Branch | Role | Status |
|---|---|---|---|
| `arena/6b8bb130-zone2` | merged to `main` via PR #1 | Dashboard prototype (Northstar) | merged |
| `arena/6602723a-zone2` (S-6602723A) | merged to `main` via PR #4, PR #6 | Verified dataset, generated hub, integration | merged |
| `arena/34836ddd-zone2` | PR #5 | AI-powered platform build (multi-page dashboard) + integration | merged |
| `arena/ec67c431-zone2` | PR #7 | Independent full build, then final integration | merged |

## Task board

Legend: `unclaimed` · `in progress` · `done` · `needs review`.
A status of `needs review` means the item is published on the *Flagged for Review* page and does
not block anything.

| ID | Task | Status | Owner | File scope |
|---|---|---|---|---|
| T1 | Task board + session registry | done | S-6602723A | `COORDINATION.md` |
| T2 | Resolve the three affiliate short links to canonical ASINs | done | S-6602723A | `data/raw-verification-log.md` |
| T3 | Verify product facts against official sources | done | S-6602723A | `data/products.json`, `data/sources.json` |
| T4 | Amazon Associates compliance requirements | done | S-6602723A | `data/compliance.json` |
| T5 | Executive summary | done | S-6602723A | `docs/executive-summary.md` |
| T6 | Automated platform requirements matrix | done | S-6602723A | `data/requirements.json` |
| T7 | Verified hub site (landing + category subpages) | done | S-6602723A | generated `*.html`, `assets/**` |
| T8 | Link + data integrity check in CI | done | S-6602723A | `scripts/verify.py`, `.github/workflows/**` |
| T9 | Dashboard prototype (Northstar) | done | `arena/6b8bb130-zone2` | `index.html`, `app.js`, `data.js`, `styles.css` |
| T10 | Integration: merge, re-verify, PR, deploy (PR #5) | done | `arena/34836ddd-zone2` | `COORDINATION.md`, `README.md`, `.github/workflows/**`, `start.html`, `index.html` |
| T11 | AI-powered platform build (multi-page dashboard) | done | `arena/34836ddd-zone2` | `zone2/**` |
| T12 | Independent research + verification of the 3 products | done | ec67c431-zone2 | (research only — reconciled into T3) |
| T13 | Independent dashboard site build | superseded at integration | ec67c431-zone2 | redundant duplicates removed; canonical `main` site kept |
| T14 | Final integration of PR #7 (merge, re-verify, deploy) | done | ec67c431-zone2 | `COORDINATION.md`, `scripts/check_links.py` |

## File ownership (non-overlapping scopes)

| Scope | Owner | Notes |
|---|---|---|
| `index.html`, `app.js`, `data.js`, `styles.css` | `arena/6b8bb130-zone2` | Northstar dashboard, preserved at repo root. |
| `overview.html`, `products.html`, `compare.html`, `compliance.html`, `requirements.html`, `methodology.html`, `flagged.html`, `summary.html`, `product-*.html`, `404.html`, `start.html`, `assets/**` | S-6602723A | generated; listed in `site-manifest.json`. |
| `data/**`, `docs/**`, `scripts/**` | S-6602723A | verified dataset and tooling. |
| `zone2/**` | `arena/34836ddd-zone2` | multi-page platform dashboard, preserved in a subfolder. |
| `northstar/**` | `arena/34836ddd-zone2` | Northstar copy preserved in a subfolder. |
| `scripts/check_links.py` | ec67c431-zone2 | generic internal-link checker (additive; supplementary to `verify.py`). |
| `COORDINATION.md`, `README.md`, `.github/workflows/**` | final integration session | task board, combined docs, merged CI. |

`site-manifest.json` records exactly which files `scripts/build.py` owns. The generator cleans up
only files on that list, so it can never delete the dashboard's hand-written files, `zone2/**`,
`northstar/**`, or anything in `data/`, `docs/` or `scripts/`.

## Change log

### `arena/6b8bb130-zone2` (merged via PR #1)
Built Northstar, a static source-first dashboard. Product fields left blank/Unverified because
the three short links could not be resolved to product pages. Added an Actions-based Pages
workflow with asset and navigation validation.

### S-6602723A (`arena/6602723a-zone2`, merged via PR #4 and PR #6)
Resolved all three short links to canonical ASINs by following Amazon's redirects
(B0CDY277D3, B09B7SB46R, B08DKYBTPH) and verified specifications against Amazon product pages and
the manufacturers' own pages. Built the verified hub, the verifier guard, and integrated the
Northstar dashboard (kept at `index.html`, hub at `overview.html`, `start.html` as landing).
Encountered and resolved merge conflicts without discarding other sessions' work; fixed the
dashboard workflow to stage only publishable files into `_site/`; fixed a price that leaked to the
live site (PR #6).

### `arena/34836ddd-zone2` (PR #5)
Built an independent AI-powered platform dashboard (multi-page: dashboard, products, analysis,
content, compliance, executive summary, flagged review, sources). Discovered the three supplied
codes are each **9 characters** and do not meet Amazon's official 10-character ASIN format; left
all product-specific fields blank and flagged. Merged into `main` as the integration, preserving
all sessions' work.

### `arena/ec67c431-zone2` (PR #7, final integration)
- Claimed the full task independently on branch `arena/ec67c431-zone2` (branched from `main` @
  `f577167`), scope the whole build.
- Resolved the three `link.amazon` short links to their Amazon destinations by following the
  redirect (B04G1MEwY → B0CDY277D3, B02NbDxp3 → B09B7SB46R, B00hJ57DV → B08DKYBTPH) and verified
  product facts against official Amazon listings.
- Built an alternative dashboard site (own `*.html`, `css/`, `js/`, `data.js`, tables, analysis,
  compliance, flagged and executive-summary pages).
- **Cross-check against `main`'s verified dataset:** the ASINs, redirect targets, titles, brands,
  and the B0CDY277D3 "rating not attributable to this ASIN" finding all match. Two divergences
  noted and resolved in favour of `main`'s more rigorous treatment: (a) this session initially
  published a commission figure (US standard Kitchen 4.5%) from corroborating summaries, while the
  official Amazon Associates rate card is login-gated and unverified — `main` correctly does **not**
  publish a rate, and that treatment is adopted; (b) `main` captures prices as an audit-only
  `volatile_snapshot` and never publishes them (no-price rule), also adopted.
- **Merge conflict on PR #7:** `main` had already integrated and deployed the canonical site from
  the three prior sessions. This session merged `origin/main` into its branch, resolved the
  `COORDINATION.md` conflict by merging both boards' records, kept `main`'s canonical site intact,
  deleted its own redundant duplicate pages, and carried forward only its additive
  `scripts/check_links.py`. No prior session's work was discarded.
- Re-verified: `python3 scripts/build.py` regenerates the committed output cleanly and
  `python3 scripts/verify.py` reports 0 errors; `python3 scripts/check_links.py .` reports no
  broken internal links.

## Merge conflict and resolution (final integration, `arena/34836ddd-zone2`)

**What happened.** While PR #5 was open, other sessions merged PR #1, PR #4 and PR #6 into
`main`, each adding a full site at the repo root. Merging `origin/main` into
`arena/34836ddd-zone2` produced conflicts in `index.html`, `products.html`, `compliance.html`,
`flagged.html`, `README.md`, `COORDINATION.md` and `.github/workflows/pages.yml` (same paths
written by different sessions).

**Resolution — nothing any session built was discarded:**

| File | Resolution |
|---|---|
| `index.html` | Kept the Northstar dashboard (main's version, with its disclosure fix); added a link to the Zone2 dashboard. |
| `products.html`, `compliance.html`, `flagged.html` | Kept the verified hub's versions (main). The Zone2 equivalents moved to `zone2/`. |
| `zone2/**` | The whole Zone2 platform build moved intact into the `zone2/` subfolder; its relative links still resolve. |
| `start.html` | Landing page extended with a third choice card linking to the Zone2 dashboard. |
| `README.md` | Rewritten to document all three deliverables with per-session attribution. |
| `COORDINATION.md` | This file — all sessions' records retained, plus this resolution log. |
| `.github/workflows/pages.yml` | Kept the merged workflow; added staging of `zone2/**` into `_site/zone2/` and extended the disclosure/no-price check and bundle assertion to cover `zone2/*.html`. |

### PR #7 conflict resolution (`arena/ec67c431-zone2`)

**What happened.** This session independently built a complete overlapping site from the same base
(`f577167`). By the time PR #7 was opened, `main` already contained the integrated, deployed site
from the three prior sessions. PR #7 reported `mergeable: CONFLICTING`.

**Files conflicted:** `COORDINATION.md` (after re-merging the then-current `main`; earlier rounds
also touched `index.html`, `products.html`, `compliance.html`, `flagged.html`, `README.md`).

**Resolution — `main`'s work preserved:** this session merged `origin/main` into its branch,
resolved `COORDINATION.md` by merging both boards' records (this file), kept `main`'s canonical
site, build pipeline and dataset intact, deleted its own redundant duplicate pages, and carried
forward only the additive `scripts/check_links.py`. No prior session's work was discarded.

## Verification protocol used

1. Every table row carries a `source` link to an official page (Amazon product page, the Amazon
   Associates Operating Agreement, or the manufacturer's own site).
2. A value that could not be confirmed from an official source is left **blank** and marked
   `unverified`; it appears on the *Flagged for Review* page.
3. No value is inferred, interpolated, or carried over from a similar product.
4. `scripts/verify.py` re-checks every row at build time and fails the build on an unsourced row,
   a non-`https` source, a published unverified value, a broken internal link, a missing
   disclosure, or a printed price (including bare `price_usd` figures — see I-19).
5. Capture timestamps are recorded in UTC in `data/products.json`.
6. `scripts/check_links.py` (ec67c431-zone2) additionally scans every page for broken internal
   links and missing local assets; run with `python3 scripts/check_links.py .`.

## Irregularities log

| # | Irregularity | Where | Disposition |
|---|---|---|---|
| I-1 | Initial `README.md` contains only `# Zone2` (7 bytes). | `README.md` @ `f577167` | Resolved. |
| I-2 | No `LICENSE`, `.gitignore`, CI or tests in the initial commit. | repo root @ `f577167` | `.gitignore` and CI added; licence is owner decision. |
| I-3 | The three `link.amazon/*` short links are opaque redirects; target ASINs not readable from the link text. | affiliate inputs | Resolved by following the redirect; recorded in `data/raw-verification-log.md`. |
| I-4 | No Amazon Associates tracking tag (`tag=`) on any of the three links, so commission attribution is impossible. | affiliate inputs | **Flagged for review — owner action.** |
| I-5 | Prices, ratings, review counts and stock status are volatile and Amazon restricts their display. | product data | Captured for the audit trail, withheld from publication. |
| I-6 | Amazon.com product pages are bot-gated and render inconsistently to automated fetches. | product data | Disclosed in methodology; corroborated against regional storefronts and the manufacturer. |
| I-7 | Star ratings differ by storefront for the same ASIN (`B09B7SB46R`: 4.5/16,128 on `.co.uk` vs 4.6/8,361 on `.sa`). | product data | No rating published. |
| I-8 | Chefman 8 Qt: Amazon bullet text says 1000 W; Chefman says 1700 W for the same model `RJ38-SQSS-8T`. | `B08DKYBTPH` | Manufacturer figure published; discrepancy flagged. |
| I-9 | Chefman 8 Qt dimensions differ between the Amazon spec table and the manufacturer page. | `B08DKYBTPH` | Both published as separate sourced rows. |
| I-10 | Emeril model suffix `-02X-VN` (Amazon US) vs `-02A-VN` (manufacturer store). | `B09B7SB46R` | Both published with sources. |
| I-11 | Emeril wattage: 1700 W rated; a customer review reports a lower measured draw. | `B09B7SB46R` | Rated figure published; measured draw not published. |
| I-12 | Emeril preset count: 24 (title/description) vs 25 (manufacturer spec tile). | `B09B7SB46R` | Both shown side by side. |
| I-13 | Emeril 500 °F maximum is single-sourced to Amazon's product-information block. | `B09B7SB46R` | Published as single-source and labelled. |
| I-14 | The Chefman 6 Qt listing's rating block did not render; the visible figure belongs to a sibling ASIN (`B0B7C327LK`). | `B0CDY277D3` | Rating left blank; not attributed. |
| I-15 | Amazon's Agent Terms require automated clients to self-identify and forbid bypassing blocks, which makes "fully automated scraping" non-compliant. | brief vs policy | Documented on the compliance page; the automation that *is* compliant was built. |
| I-16 | Two sessions built overlapping front pages (PR #1 merged a dashboard at `index.html` while PR #4 was in progress). | `index.html` | Resolved without discarding either: dashboard kept at `index.html`, hub at `overview.html`, `start.html` as landing. |
| I-17 | The dashboard's workflow published `path: .`, exposing `data/`, `docs/`, `scripts/` as static files. | `.github/workflows/pages.yml` | Fixed in the merged workflow: only `_site/` is uploaded, with an assertion that nothing leaks. |
| I-18 | The dashboard's `index.html` had no affiliate disclosure in its static HTML (only JS-rendered), so the served page had none before JavaScript ran. | `index.html` | Fixed: disclosure now in the HTML itself. Caught by CI. |
| I-19 | **A price value reached the live site.** The audit-trail snapshot rendered `Price (USD) 69.97` on the product pages; the verifier's no-price rule only matched `$`-prefixed amounts, so a bare number passed and was published. | `product-*.html`, `products.html` | Fixed: price rows removed from rendered snapshots entirely, and the verifier now also rejects any bare figure matching a `price_usd` / `list_price_usd` value, with a regression test. Found by reading the deployed page, not by CI. |
| I-21 | **Three sessions built overlapping full sites at the repo root.** Each session's `index.html`, `products.html`, `compliance.html`, `flagged.html` collided. | root HTML | Resolved without discarding any: Northstar dashboard kept at root, verified hub at root, Zone2 platform build preserved in `zone2/`, `start.html` landing links to all three. |
| I-22 | The three supplied codes are each **9 characters**; Amazon officially defines an ASIN as a unique **10-character** alphanumeric code. No official source (Amazon, Google, Bing, Wayback Machine, CamelCamelCamel) has any record of the 9-char codes. | affiliate inputs | Recorded here. The short links were resolved to canonical 10-char ASINs by following Amazon's redirects (I-3); the Zone2 build treats the raw 9-char codes as invalid and leaves product fields blank, while the verified hub publishes the redirect-resolved products with full sourcing. Both interpretations are documented for owner review. **Confirmed by session ec67c431-zone2** (B04G1MEwY, B02NbDxp3, B00hJ57DV are each 9 chars; the redirect targets B0CDY277D3 / B09B7SB46R / B08DKYBTPH are the valid 10-char ASINs). |
| I-23 | Session ec67c431-zone2 initially published a commission rate (US standard Kitchen 4.5%) sourced from corroborating summaries, while the official Amazon Associates rate card is login-gated and could not be read directly. | commission data | `main`'s treatment adopted: the commission rate is marked **unverified** and is **not** published on the site. |
| I-24 | **A fourth session (ec67c431-zone2) built a second overlapping full site** after PR #5 had already integrated and deployed `main`. PR #7 conflicted on `COORDINATION.md` (and earlier on the root HTML files). | `COORDINATION.md`, root HTML | Resolved at final integration: `main`'s canonical site preserved; the fourth session's redundant duplicates removed; only its additive `scripts/check_links.py` and merged `COORDINATION.md` records carried forward. |

## PR and merge record

| Item | Value |
|---|---|
| PR #1 (Northstar dashboard) | <https://github.com/kanlerxz87-cyber/Zone2/pull/1> — merged |
| PR #4 (verified hub + integration) | <https://github.com/kanlerxz87-cyber/Zone2/pull/4> — merged |
| PR #6 (price-leak fix) | <https://github.com/kanlerxz87-cyber/Zone2/pull/6> — merged |
| PR #5 (Zone2 platform build + integration) | <https://github.com/kanlerxz87-cyber/Zone2/pull/5> — merged |
| PR #7 (ec67c431-zone2 integration) | <https://github.com/kanlerxz87-cyber/Zone2/pull/7> — merged via `gh pr merge 7 --merge` on 2026-11-13T23:02:50Z, merge commit `5741e01` |
| Final integration sessions | `arena/34836ddd-zone2` (PR #5), `arena/ec67c431-zone2` (PR #7) |
| Re-verification (PR #7) | `build.py` regenerates committed output cleanly; `verify.py` = 0 errors; `check_links.py` = no broken internal links |
| Pages deploy | `.github/workflows/pages.yml` ("Build, verify and deploy") ran on the PR #7 merge push to `main` and completed with **success**. Site confirmed live at <https://kanlerxz87-cyber.github.io/Zone2/> (root = Northstar workspace, `/products.html` = verified source-linked hub, `/zone2/` = platform dashboard). All pages carry the required disclosure; no prices are published. |
