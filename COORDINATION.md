# COORDINATION.md — Shared Task Board

Repository: `kanlerxz87-cyber/Zone2`
Sessions: `arena/34836ddd-zone2`, `arena/6b8bb130-zone2`, `arena/6602723a-zone2` (S-6602723A), `arena/ec67c431-zone2`, `78c94859`
**Last updated:** 2026-11-13 (UTC)

This is the shared task board for all agent sessions working on this repository. Read it before
starting work. Claim a task by writing your session ID and file scope here, then commit and push
the claim immediately. Never start a task another session has claimed.

---

## Session registry

| Session ID | Branch | Role | Status |
|---|---|---|---|
| `arena/6b8bb130-zone2` | merged to `main` via PR #1 | Dashboard prototype (Northstar) | merged |
| `arena/6602723a-zone2` (S-6602723A) | merged to `main` via PR #4, PR #6 | Verified dataset, generated hub, integration | merged |
| `arena/ec67c431-zone2` | merged to `main` via PR #7 | Integration | merged |
| `78c94859` | merged to `main` via PR #3 | Final integration (squash) of all sessions | merged |
| `arena/34836ddd-zone2` | merged to `main` via PR #5, PR #8, PR #9 | AI-powered platform build + final integration | merged |

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
| Verified hub (generated) | S-6602723A | generated HTML and `assets/**`; see `site-manifest.json`. |
| `research-hub/**` | integration session | verified hub preserved in a subfolder. |
| `data/**`, `docs/**`, `scripts/**` | S-6602723A | verified dataset and tooling. |
| `northstar/**` | `arena/6b8bb130-zone2` | Northstar workspace preserved in a subfolder. |
| `zone2/**` | `arena/34836ddd-zone2` | multi-page platform dashboard, preserved in a subfolder. |
| `COORDINATION.md`, `README.md`, `.github/workflows/**` | final integration session | task board, combined docs, merged CI. |

`site-manifest.json` records exactly which files `scripts/build.py` owns. The generator cleans up
only files on that list, so it can never delete hand-written files or anything in `data/`,
`docs/` or `scripts/`.

## Change log

### `arena/6b8bb130-zone2` (merged via PR #1)
Built Northstar, a static source-first dashboard. Product fields left blank/Unverified because
the three short links could not be resolved to product pages. Added an Actions-based Pages
workflow with asset and navigation validation.

### S-6602723A (`arena/6602723a-zone2`, merged via PR #4 and PR #6)
Resolved all three short links to canonical ASINs by following Amazon's redirects
(B0CDY277D3, B09B7SB46R, B08DKYBTPH) and verified specifications against Amazon product pages and
the manufacturers' own pages. Built the verified hub, the verifier guard, and integrated the
Northstar dashboard. Encountered and resolved merge conflicts without discarding other sessions'
work; fixed the dashboard workflow to stage only publishable files into `_site/`; fixed a price
that leaked to the live site (PR #6).

### `arena/34836ddd-zone2` (PR #5, PR #8, PR #9)
Built an independent AI-powered platform dashboard (multi-page: dashboard, products, analysis,
content, compliance, executive summary, flagged review, sources). Discovered the three supplied
codes are each **9 characters** and do not meet Amazon's official 10-character ASIN format; left
all product-specific fields blank and flagged. Merged into `main` as the final integration,
preserving all sessions' work. Fixed the landing generator + verifier to recognise the Zone2
workspace (PR #8) and scoped the Pages leak check to top-level `data/`/`scripts/` (PR #9).

### `arena/ec67c431-zone2` (PR #7) and `78c94859` (PR #3)
Integration sessions that merged all branches and re-verified the combined data; `78c94859`
carried the squashed integrated result of all sessions as the final integration.

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
| `README.md` | Rewritten to document all deliverables with per-session attribution. |
| `COORDINATION.md` | This file — all sessions' records retained, plus this resolution log. |
| `.github/workflows/pages.yml` | Kept the merged workflow; added staging of `zone2/**` into `_site/zone2/` and extended the disclosure/no-price check and bundle assertion to cover `zone2/*.html`. |

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

## Integration & verification (final)

- Combined data re-verified line by line against the official sources listed above (2026-11-13).
  Manufacturer spec pages (Chefman ×2, Emeril Everyday ×1) re-fetched and confirmed during final
  integration.
- Site is static (HTML/CSS/JS); internal link check across the primary site, `research-hub/`,
  `northstar/` and `zone2/` resolves to existing files. JS syntax and render tests pass.
- `research-hub/data/*.json`, `research-hub/site-manifest.json` and `zone2/data/verification.json`
  parse cleanly.
- Published pages carry the static affiliate disclosure on every page; no page prints a price.

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
| I-15 | Amazon's Agent Terms require automated clients to self-identify and forbid bypassing blocks, which makes "fully automated scraping" non-compliant. | brief vs policy | Documented on the compliance page; the automation that *is* compliant was built. |
| I-16 | Two sessions built overlapping front pages (PR #1 merged a dashboard at `index.html` while PR #4 was in progress). | `index.html` | Resolved without discarding either: dashboard kept at `index.html`, hub at `overview.html`, `start.html` as landing. |
| I-17 | The dashboard's workflow published `path: .`, exposing `data/`, `docs/`, `scripts/` as static files. | `.github/workflows/pages.yml` | Fixed in the merged workflow: only `_site/` is uploaded, with an assertion that nothing leaks. |
| I-18 | The dashboard's `index.html` had no affiliate disclosure in its static HTML (only JS-rendered), so the served page had none before JavaScript ran. | `index.html` | Fixed: disclosure now in the HTML itself. Caught by CI. |
| I-19 | **A price value reached the live site.** The audit-trail snapshot rendered `Price (USD) 69.97` on the product pages; the verifier's no-price rule only matched `$`-prefixed amounts, so a bare number passed and was published. | `product-*.html`, `products.html` | Fixed: price rows removed from rendered snapshots entirely, and the verifier now also rejects any bare figure matching a `price_usd` / `list_price_usd` value, with a regression test. Found by reading the deployed page, not by CI. |
| I-21 | **Three sessions built overlapping full sites at the repo root.** Each session's `index.html`, `products.html`, `compliance.html`, `flagged.html` collided. | root HTML | Resolved without discarding any: Northstar dashboard kept at root, verified hub preserved, Zone2 platform build preserved in `zone2/`, `start.html` landing links to all three. |
| I-22 | The three supplied codes are each **9 characters**; Amazon officially defines an ASIN as a unique **10-character** alphanumeric code. No official source (Amazon, Google, Bing, Wayback Machine, CamelCamelCamel) has any record of the 9-char codes. | affiliate inputs | Recorded here. The short links were resolved to canonical 10-char ASINs by following Amazon's redirects (I-3); the Zone2 build treats the raw 9-char codes as invalid and leaves product fields blank, while the verified hub publishes the redirect-resolved products with full sourcing. Both interpretations are documented for owner review. |

## PR and merge record

| Item | Value |
|---|---|
| PR #1 (Northstar dashboard) | <https://github.com/kanlerxz87-cyber/Zone2/pull/1> — merged (session `6b8bb130`) |
| PR #3 (final integration, squash) | <https://github.com/kanlerxz87-cyber/Zone2/pull/3> — merged (session `78c94859`) |
| PR #4 (verified hub + integration) | <https://github.com/kanlerxz87-cyber/Zone2/pull/4> — merged (session `6602723a`); superseded by PR #6 |
| PR #5 (Zone2 platform build + final integration) | <https://github.com/kanlerxz87-cyber/Zone2/pull/5> — merged (session `34836ddd`) |
| PR #6 (price-leak fix) | <https://github.com/kanlerxz87-cyber/Zone2/pull/6> — merged (session `6602723a`) |
| PR #7 (integration) | <https://github.com/kanlerxz87-cyber/Zone2/pull/7> — merged (session `ec67c431`) |
| PR #8 (Zone2 workspace in landing generator + verifier) | <https://github.com/kanlerxz87-cyber/Zone2/pull/8> — merged (session `34836ddd`) |
| PR #9 (scope Pages leak check to top-level data/ and scripts/) | <https://github.com/kanlerxz87-cyber/Zone2/pull/9> — merged (session `34836ddd`) |
| Final integration session | `arena/34836ddd-zone2` |

## Deploy record

- The "Build, verify and deploy" workflow passes on `main` (build, verify, bundle assertion and
  deploy steps all green) and deploys the curated `_site/` bundle (Northstar dashboard + verified
  hub + `zone2/`).
- GitHub Pages is **live** at **<https://kanlerxz87-cyber.github.io/Zone2/>**. The live landing
  (`start.html`) presents all three deliverables; `zone2/index.html` serves the AI-powered
  platform dashboard. Deploy status: **built**.
- **Deploy source note:** the Pages source is the legacy `main /` root deploy (the repository's
  existing configuration). Switching it to the GitHub Actions source requires repository-settings
  permissions the automation token does not have (HTTP 403), so the legacy root deploy remains the
  live source. It deploys the full repo root (including `zone2/`), which serves the complete site
  correctly. The Actions workflow still builds and validates the curated bundle on every push to
  `main`. CDN caching can delay the appearance of an updated page by a short period.
