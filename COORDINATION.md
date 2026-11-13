# COORDINATION.md — Shared Task Board

Project: **Zone2 — AI-powered Amazon Affiliate Marketing Platform**
Repo: `kanlerxz87-cyber/Zone2`

## Sessions

| Session | Branch | Role |
|---|---|---|
| arena/6b8bb130-zone2 | `arena/6b8bb130-zone2` | Built Northstar source-first research dashboard; PR #1 merged into main 2026-11-13 22:36:46 UTC |
| arena/6602723a-zone2 | `arena/6602723a-zone2` | Built Affiliate Research Hub (verified dataset, generated site, compliance position); PR #4 opened 2026-11-13 22:42:48 UTC |
| **78c94859 (this session)** | `arena/78c94859-zone2` | Platform site build, verification, and **final integration session** |

> Integration note: this session acts as the final integration session. All three contributions are
> merged into a single coherent site on branch `arena/78c94859-zone2`: the Zone2 platform is the
> primary site at the repo root; the Northstar dashboard and the Affiliate Research Hub are preserved
> in full under `northstar/` and `research-hub/` respectively. No session's work was discarded.

## Task Board

| # | Task | Status | Owner session | Files |
|---|------|--------|--------------|-------|
| 1 | Source-first Amazon affiliate research dashboard | done | arena/6b8bb130-zone2 | `northstar/*` (moved from root during integration) |
| 2 | Amazon affiliate research hub: verified dataset, generated site, compliance position | done (integrated into `research-hub/`) | arena/6602723a-zone2 | `research-hub/*`, `docs/executive-summary.md`, `.nojekyll`, `.gitignore` |
| 3 | Repo review + verify the three product links against official Amazon sources | done | 78c94859 | `COORDINATION.md`, `docs/verification-log.md` |
| 4 | Research official Amazon Associates program rules | done | 78c94859 | `COORDINATION.md`, `docs/verification-log.md`, `assets/js/data.js` |
| 5 | Build GitHub Pages site: landing page + category subpages (dashboard UI, tables) | done | 78c94859 | `index.html`, `products.html`, `analysis.html`, `content.html`, `compliance.html`, `tracking.html`, `flagged.html`, `404.html`, `assets/` |
| 6 | Collect/verify all table data; every row carries an official source link; unverifiable values left blank + flagged | done | 78c94859 (incl. merged spec verification) | `assets/js/data.js`, `docs/verification-log.md` |
| 7 | Final integration: merge branches, re-verify combined data line by line, confirm site builds with no broken links | done | 78c94859 | see "Integration & verification" |
| 8 | Publish to GitHub Pages, create PR to main, merge, record PR link and result | done | 78c94859 | see "Integration & verification" |

## Sources used (all official / verified)

| Source | URL | Used for |
|---|---|---|
| Amazon Associates Central | https://affiliate-program.amazon.com/ | Program description; "earn up to 10% in associate commissions from qualifying purchases and programs" |
| Amazon Associates Program Policies (updated 2026-04-14) | https://affiliate-program.amazon.com/help/operating/policies | Commission Income Statement, Participation Requirements, Agent Terms, IP License |
| Amazon Associates Operating Agreement (updated 2025-10-15) | https://affiliate-program.amazon.com/help/operating/agreement | Mandatory disclosure language |
| Amazon product page — B0CDY277D3 | https://www.amazon.com/dp/B0CDY277D3 | Product 1 title/brand/category |
| Amazon product page — B09B7SB46R | https://www.amazon.com/dp/B09B7SB46R | Product 2 title/brand/category |
| Amazon product page — B08DKYBTPH | https://www.amazon.com/dp/B08DKYBTPH | Product 3 title/brand/category |
| Chefman official product page — TurboFry Touch Dual-Window | https://chefman.com/products/turbofry-touch-dual-window-air-fryer | Product 1 model/specs/manufacturer price |
| Chefman official product page — TurboFry Touch 8 Qt | https://chefman.com/products/turbofry-touch-air-fryer-1 | Product 3 model/specs/manufacturer price |
| Emeril Everyday official store — French Door AirFryer 360 | https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360 | Product 2 model/specs/manufacturer price |

## Irregularities flagged for review

1. **Link-code / ASIN mismatch (all three products).** The provided short links resolve to live Amazon
   product pages, but the destination ASIN differs from the code in the link: B04G1MEwY → B0CDY277D3,
   B02NbDxp3 → B09B7SB46R, B00hJ57DV → B08DKYBTPH. Direct fetches of `amazon.com/dp/<code>` return
   "Page Not Found". The codes behave as opaque short-link tokens. Published on the Flagged for Review
   page.
2. **Cross-source conflicts (merged research).** (a) Emeril Lagasse cooking functions: Amazon title
   states 24 functions; the manufacturer spec tile states 25 cooking pre-sets — both shown, flagged as
   a conflict. (b) Chefman 8 Qt power: Amazon bullet text states 1000 W while Chefman's official page
   states 1700 W for the same model — conflict flagged, manufacturer figure published. (c) Chefman 8 Qt
   dimensions differ between Amazon spec table and Chefman's official page — both rows published as
   conflicts.
3. **All three products are in the same category (Home & Kitchen air fryers / air fryer ovens).**
   Confirmed from the three Amazon titles. Single-category portfolio.
4. **Commission rate card requires sign-in.** The official per-category rate schedule
   (https://affiliate-program.amazon.com/help/operating/schedule) redirects to Amazon sign-in; the
   Home & Kitchen rate is left blank and flagged as unverified. Only the public "up to 10%" ceiling is
   recorded.
5. **Price / rating / review-count / stock on Amazon (UNVERIFIED).** Amazon does not expose these to
   automated fetches. Left blank and flagged. Manufacturer-site prices (Chefman.com, Emeril Everyday)
   are published where verified, clearly labelled as manufacturer-site prices — not Amazon prices.
6. **Associates tag absent on resolved short links.** The resolved `link.amazon` URLs carry no
   Associates tag parameter; live tracking requires Special Links with the Associates tag (per
   Participation Requirements §2). Flagged for account configuration.

## Integration & verification

- Combined data re-verified line by line against the official sources listed above (2026-11-13).
  Manufacturer spec pages (Chefman ×2, Emeril Everyday ×1) re-fetched and confirmed during integration.
- Site is static (HTML/CSS/JS) served from the repo root; no build step.
- Internal link check: every internal navigation link across the primary site, `northstar/` and
  `research-hub/` resolves to an existing file.
- Render test: all primary-site tables populate from `assets/js/data.js`.
- PR **#3** — https://github.com/kanlerxz87-cyber/Zone2/pull/3 — merged into `main` (squash) after
  resolving conflicts against merged PR #1; PR #3's branch carried the integrated result of all three
  sessions.
- PR **#4** (arena/6602723a-zone2) closed as superseded: its content is preserved in full under
  `research-hub/` and its executive summary under `docs/executive-summary.md`.
- GitHub Pages: source branch `main`, path `/`; site live at
  https://kanlerxz87-cyber.github.io/Zone2/ (deploy status: built).
