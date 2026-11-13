# COORDINATION.md — Shared Task Board

Repository: `kanlerxz87-cyber/Zone2`
Sessions: `arena/34836ddd-zone2`, `arena/6b8bb130-zone2`, `arena/6602723a-zone2` (S-6602723A)
**Last updated:** 2026-11-13 (UTC)

This is the shared task board for all agent sessions working on this repository. Read it before
starting work. Claim a task by writing your session ID and file scope here, then commit and push
the claim immediately. Never start a task another session has claimed.

---

## Session registry

| Session ID | Branch | Role | Status |
|---|---|---|---|
| `arena/6b8bb130-zone2` | merged to `main` via PR #1 | Dashboard prototype (Northstar) | merged |
| `arena/6602723a-zone2` (S-6602723A) | merged to `main` via PR #4 | Verified dataset, generated hub, first integration | merged |
| `arena/34836ddd-zone2` | PR #5 | AI-powered platform build (multi-page dashboard) + final integration | merged |

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
| T10 | Final integration: merge, re-verify, PR, deploy | done | `arena/34836ddd-zone2` | `COORDINATION.md`, `README.md`, `.github/workflows/**`, `start.html`, `index.html` |
| T11 | AI-powered platform build (multi-page dashboard) | done | `arena/34836ddd-zone2` | `zone2/**` |

## File ownership (non-overlapping scopes)

| Scope | Owner | Notes |
|---|---|---|
| `index.html`, `app.js`, `data.js`, `styles.css` | `arena/6b8bb130-zone2` | Northstar dashboard, preserved at repo root. |
| `overview.html`, `products.html`, `compare.html`, `compliance.html`, `requirements.html`, `methodology.html`, `flagged.html`, `summary.html`, `product-*.html`, `404.html`, `start.html`, `assets/**` | S-6602723A | generated; listed in `site-manifest.json`. |
| `data/**`, `docs/**`, `scripts/**` | S-6602723A | verified dataset and tooling. |
| `zone2/**` | `arena/34836ddd-zone2` | multi-page platform dashboard, preserved in a subfolder. |
| `COORDINATION.md`, `README.md`, `.github/workflows/**` | final integration session | task board, combined docs, merged CI. |

`site-manifest.json` records exactly which files `scripts/build.py` owns. The generator cleans up
only files on that list, so it can never delete the dashboard's hand-written files, `zone2/**`, or
anything in `data/`, `docs/` or `scripts/`.

## Change log

### `arena/6b8bb130-zone2` (merged via PR #1)
Built Northstar, a static source-first dashboard. Product fields left blank/Unverified because
the three short links could not be resolved to product pages. Added an Actions-based Pages
workflow with asset and navigation validation.

### S-6602723A (`arena/6602723a-zone2`, merged via PR #4)
Resolved all three short links to canonical ASINs by following Amazon's redirects
(B0CDY277D3, B09B7SB46R, B08DKYBTPH) and verified specifications against Amazon product pages and
the manufacturers' own pages. Built the verified hub, the verifier guard, and integrated the
Northstar dashboard (kept at `index.html`, hub at `overview.html`, `start.html` as landing).
Encountered and resolved a merge conflict with PR #1 without discarding either site; fixed the
dashboard workflow to stage only publishable files into `_site/`.

### `arena/34836ddd-zone2` (PR #5)
Built an independent AI-powered platform dashboard (multi-page: dashboard, products, analysis,
content, compliance, executive summary, flagged review, sources). Discovered the three supplied
codes are each **9 characters** and do not meet Amazon's official 10-character ASIN format; left
all product-specific fields blank and flagged. Merged into `main` as the final integration,
preserving all three sessions' work.

## Merge conflict and resolution (final integration, `arena/34836ddd-zone2`)

**What happened.** While PR #5 was open, sessions merged PR #1 and PR #4 into `main`, each adding
a full site at the repo root. Merging `origin/main` into `arena/34836ddd-zone2` produced conflicts
in `index.html`, `products.html`, `compliance.html`, `flagged.html`, `README.md`,
`COORDINATION.md` and `.github/workflows/pages.yml` (same paths written by different sessions).

**Resolution — nothing either session built was discarded:**

| File | Resolution |
|---|---|
| `index.html` | Kept the Northstar dashboard (main's version, with its disclosure fix); added a link to the Zone2 dashboard. |
| `products.html`, `compliance.html`, `flagged.html` | Kept the verified hub's versions (main). The Zone2 equivalents moved to `zone2/`. |
| `zone2/**` | The whole Zone2 platform build moved intact into the `zone2/` subfolder; its relative links still resolve. |
| `start.html` | Landing page extended with a third choice card linking to the Zone2 dashboard. |
| `README.md` | Rewritten to document all three deliverables with per-session attribution. |
| `COORDINATION.md` | This file — all three sessions' records retained, plus this resolution log. |
| `.github/workflows/pages.yml` | Kept the merged workflow; added staging of `zone2/**` into `_site/zone2/` and extended the disclosure/no-price check and bundle assertion to cover `zone2/*.html`. |

## Verification protocol used

1. Every table row carries a `source` link to an official page (Amazon product page, the Amazon
   Associates Operating Agreement, or the manufacturer's own site).
2. A value that could not be confirmed from an official source is left **blank** and marked
   `unverified`; it appears on the *Flagged for Review* page.
3. No value is inferred, interpolated, or carried over from a similar product.
4. `scripts/verify.py` re-checks every row at build time and fails the build on an unsourced row,
   a non-`https` source, a published unverified value, a broken internal link, a missing
   disclosure, or a printed price.
5. Capture timestamps are recorded in UTC in `data/products.json`.

## Irregularities log

| # | Irregularity | Where | Disposition |
|---|---|---|---|
| I-1 | Initial `README.md` contains only `# Zone2` (7 bytes). | `README.md` @ `f577167` | Resolved. |
| I-2 | No `LICENSE`, `.gitignore`, CI or tests in the initial commit. | repo root @ `f577167` | `.gitignore` and CI added; licence is owner decision. |
| I-3 | The three `link.amazon/*` short links are opaque redirects; target ASINs not readable from the link text. | affiliate inputs | Resolved by following the redirect; recorded in `data/raw-verification-log.md`. |
| I-4 | No Amazon Associates tracking tag (`tag=`) on any of the three links, so commission attribution is impossible. | affiliate inputs | **Flagged for review — owner action.** |
| I-5 | Prices, ratings, review counts and stock status are volatile and Amazon restricts their display. | product data | Captured for the audit trail, withheld from publication. |
| I-6 | Amazon.com product pages are bot-gated and render inconsistently to automated fetches. | product data | Disclosed in methodology; corroborated against regional storefronts and the manufacturer. |
| I-7 | Star ratings differ by storefront for the same ASIN (`B09B7SB46R`). | product data | No rating published. |
| I-8 | Chefman 8 Qt: Amazon bullet text says 1000 W; Chefman says 1700 W for the same model `RJ38-SQSS-8T`. | `B08DKYBTPH` | Manufacturer figure published; discrepancy flagged. |
| I-9 | Chefman 8 Qt dimensions differ between the Amazon spec table and the manufacturer page. | `B08DKYBTPH` | Both published as separate sourced rows. |
| I-10 | Emeril model suffix `-02X-VN` (Amazon US) vs `-02A-VN` (manufacturer store). | `B09B7SB46R` | Both published with sources. |
| I-11 | Emeril wattage: 1700 W rated; a customer review reports a lower measured draw. | `B09B7SB46R` | Rated figure published; measured draw not published. |
| I-12 | Emeril preset count: 24 (title/description) vs 25 (manufacturer spec tile). | `B09B7SB46R` | Both shown side by side. |
| I-13 | Emeril 500 °F maximum is single-sourced to Amazon's product-information block. | `B09B7SB46R` | Published as single-source and labelled. |
| I-14 | The Chefman 6 Qt listing's rating block did not render; the visible figure belongs to a sibling ASIN (`B0B7C327LK`). | `B0CDY277D3` | Rating left blank; not attributed. |
| I-15 | Amazon's Agent Terms require automated clients to self-identify and forbid bypassing blocks. | brief vs policy | Documented on the compliance page; compliant automation built. |
| I-16 | Two sessions built overlapping front pages. | `index.html` | Resolved without discarding either: dashboard at `index.html`, hub at `overview.html`, `start.html` as landing. |
| I-17 | The dashboard's workflow published `path: .`, exposing `data/`, `docs/`, `scripts/`. | `.github/workflows/pages.yml` | Fixed: only `_site/` is uploaded, with a leak assertion. |
| I-18 | The dashboard's `index.html` had no affiliate disclosure in its static HTML (only JS-rendered). | `index.html` | Fixed: disclosure now in the HTML itself. Caught by CI. |
| I-19 | **Three sessions built overlapping full sites at the repo root.** Each session's `index.html`, `products.html`, `compliance.html`, `flagged.html` collided. | root HTML | Resolved without discarding any: Northstar dashboard kept at root, verified hub at root, Zone2 platform build preserved in `zone2/`, `start.html` landing links to all three. |
| I-20 | The three supplied codes are each **9 characters**; Amazon officially defines an ASIN as a unique **10-character** alphanumeric code. No official source (Amazon, Google, Bing, Wayback Machine, CamelCamelCamel) has any record of the 9-char codes. | affiliate inputs | Recorded here. The short links were resolved to canonical 10-char ASINs by following Amazon's redirects (I-3); the Zone2 build treats the raw 9-char codes as invalid and leaves product fields blank, while the verified hub publishes the redirect-resolved products with full sourcing. Both interpretations are documented for owner review. |

## PR and merge record

| Item | Value |
|---|---|
| PR #1 (Northstar dashboard) | <https://github.com/kanlerxz87-cyber/Zone2/pull/1> — merged |
| PR #4 (verified hub + integration) | <https://github.com/kanlerxz87-cyber/Zone2/pull/4> — merged |
| PR #5 (Zone2 platform build + final integration) | <https://github.com/kanlerxz87-cyber/Zone2/pull/5> — merged |
| Final integration session | `arena/34836ddd-zone2` |
| Pages deploy | `.github/workflows/pages.yml` deploys `_site/` (dashboard + verified hub + `zone2/`) from `main` via GitHub Actions. |
