# COORDINATION.md — Shared Task Board

Project: **Zone2 — AI-powered Amazon Affiliate Marketing Platform**
Repo: `kanlerxz87-cyber/Zone2`
**Last updated:** 2026-11-13 (UTC) — final integration completed by session 78c94859.

## Session registry

| Session ID | Branch | Role | Status |
|---|---|---|---|
| `arena/6b8bb130-zone2` | merged to `main` via PR #1 | Northstar research-dashboard prototype | merged; preserved at `northstar/` |
| `arena/6602723a-zone2` (S-6602723A) | merged to `main` via PRs #4 / #6 | Verified dataset, generated Affiliate Research Hub, compliance position | merged; preserved at `research-hub/` |
| `arena/34836ddd-zone2` | merged to `main` via PR #5 | AI-powered platform build (multi-page dashboard) | merged; preserved at `zone2/` |
| `arena/78c94859-zone2` (78c94859) | merged to `main` via PR #3 | Zone2 platform site, verification, **final integration** | merged; primary site at repo root |

> **Integration note (multi-session race):** four sessions worked in parallel and each merged work to
> `main` while others were still active, so every integration PR conflicted with the others. Per the
> project instruction, session 78c94859 acted as the final integration session: it merged `main` into
> its branch, relocated the companion sites into `northstar/`, `research-hub/` and `zone2/` (nothing
> discarded), re-verified the combined data line by line, and merged the integrated result to `main`
> via PR #3. All companion sites are reachable from the primary dashboard footer.

## Task board

| ID | Task | Status | Owner | File scope |
|---|---|---|---|---|
| T1 | Task board + session registry | done | all sessions | `COORDINATION.md` |
| T2 | Resolve the three affiliate short links to canonical ASINs | done | 6602723a / 78c94859 | `docs/verification-log.md`, `research-hub/data/raw-verification-log.md` |
| T3 | Verify product facts against official sources | done | 6602723a / 78c94859 | `research-hub/data/products.json`, `assets/js/data.js` |
| T4 | Amazon Associates compliance requirements | done | 6602723a / 78c94859 | `research-hub/data/compliance.json`, `compliance.html` |
| T5 | Executive summary | done | 6602723a / 34836ddd / 78c94859 | `docs/executive-summary.md`, `zone2/docs/EXECUTIVE_SUMMARY.md`, `index.html` |
| T6 | Automated platform requirements matrix | done | 6602723a | `research-hub/data/requirements.json`, `research-hub/requirements.html` |
| T7 | Verified hub site (landing + category subpages) | done | 6602723a | `research-hub/*.html`, `research-hub/assets/**` |
| T8 | Link + data integrity check in CI | done | 6602723a / 78c94859 | `.github/workflows/pages.yml` |
| T9 | Dashboard prototype (Northstar) | done | 6b8bb130 | `northstar/*` |
| T10 | AI-powered platform build (multi-page dashboard) | done | 34836ddd | `zone2/**` |
| T11 | Zone2 platform site (dashboard, categories, tables) | done | 78c94859 | `index.html`, `products.html`, `analysis.html`, `content.html`, `compliance.html`, `tracking.html`, `flagged.html`, `404.html`, `assets/` |
| T12 | Final integration: merge, re-verify, PR, deploy | done | 78c94859 | see "Integration & verification" |

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
2. **Cross-source conflicts.** (a) Emeril Lagasse cooking functions: Amazon title states 24 functions;
   the manufacturer spec tile states 25 cooking pre-sets — both shown, flagged as a conflict.
   (b) Chefman 8 Qt power: Amazon bullet text states 1000 W while Chefman's official page states
   1700 W for the same model — conflict flagged, manufacturer figure published. (c) Chefman 8 Qt
   dimensions differ between the Amazon spec table and Chefman's official page — both rows published as
   conflicts.
3. **All three products are in the same category (Home & Kitchen air fryers / air fryer ovens).**
   Single-category portfolio, confirmed from the three Amazon titles.
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
7. **Static affiliate disclosure.** Every page of the primary site and the companion sites carries the
   static disclosure "As an Amazon Associate I earn from qualifying purchases."

## Integration & verification

- Combined data re-verified line by line against the official sources listed above (2026-11-13).
  Manufacturer spec pages (Chefman ×2, Emeril Everyday ×1) re-fetched and confirmed during final
  integration.
- Site is static (HTML/CSS/JS) served from the repo root; no build step.
- Internal link check: every internal navigation link across the primary site, `research-hub/`,
  `northstar/` and `zone2/` resolves to an existing file. JS syntax check and render test pass for all
  primary-site tables (including the merged verified spec table).
- `research-hub/data/*.json` and `research-hub/site-manifest.json` parse cleanly.
- PR **#1** — https://github.com/kanlerxz87-cyber/Zone2/pull/1 — merged into `main` (by session
  6b8bb130).
- PR **#4** — https://github.com/kanlerxz87-cyber/Zone2/pull/4 — merged into `main` (by session
  6602723a); superseded by PR #6.
- PR **#5** — https://github.com/kanlerxz87-cyber/Zone2/pull/5 — merged into `main` (by session
  34836ddd).
- PR **#6** — https://github.com/kanlerxz87-cyber/Zone2/pull/6 — merged into `main` (by session
  6602723a).
- PR **#3** — https://github.com/kanlerxz87-cyber/Zone2/pull/3 — merged into `main` (squash) by
  session 78c94859 as the final integration; it carried the integrated result of all four sessions.
- GitHub Pages: source branch `main`, path `/`; site live at
  https://kanlerxz87-cyber.github.io/Zone2/ (deploy status: built).
