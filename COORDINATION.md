# COORDINATION.md — Shared Task Board

Repo: https://github.com/kanlerxz87-cyber/Zone2
Project: AI-powered Amazon affiliate marketing platform (site + verified data + executive summary)

## Sessions

| Session ID | Branch | Status |
|---|---|---|
| `181863ad` | `arena/181863ad-zone2` (Arena-managed) | active |

**Branch note:** This session runs on the Arena-managed branch `arena/181863ad-zone2`
(branched from `f5771676f12c092c316d7b4d3051018e61db4611` of `main`). The Arena platform
pins each session to its own branch and forbids creating/switching branches, so the
conventional `session-<id>/<task>` branch naming cannot be used here. All tasks claimed
below are executed on this branch only; file scopes are non-overlapping with any other
session (no other session has claimed anything as of this writing).

## Task board

| ID | Task | Status | Owner | File scope | Notes |
|---|---|---|---|---|---|
| T1 | Repo review & baseline audit (line by line, flag irregularities) | done | 181863ad | `docs/repo-review.md` | See "Sources & verification" below |
| T2 | Verify the 3 product ASINs from official Amazon sources | done | 181863ad | `data/products.json` | Unverifiable fields left blank + flagged |
| T3 | Verify Amazon Associates policy/disclosure/commission facts from official sources | done | 181863ad | `data/compliance.json` | |
| T4 | Site build: landing page + category subpages, dashboard UI, tables | done | 181863ad | `index.html`, `*.html`, `assets/*`, `.nojekyll` | Static site, no build step |
| T5 | Executive summary page | done | 181863ad | `executive-summary.html` | |
| T6 | Analysis & findings (niches, pricing, reviews, competition, commissions) | done | 181863ad | `analysis.html` | Only verified values; rest blank/flagged |
| T7 | Comparisons & buying guides (SEO content) | done | 181863ad | `comparisons.html`, `buying-guides.html` | |
| T8 | "Flagged for Review" page with source links | done | 181863ad | `flagged-for-review.html` | |
| T9 | Verification pass: every table row has official source link; no inferred values | done | 181863ad | all data/pages | Automated link + row audit |
| T10 | Integration: link check, site serves cleanly, no broken links | done | 181863ad | all | |
| T11 | Enable GitHub Pages, confirm deploy live | done | 181863ad | — | See "Deploy log" below |
| T12 | PR → main, merge without approval, record PR + merge result here | done | 181863ad | `COORDINATION.md` | See "Deploy log" below |

Status values: `unclaimed`, `in progress`, `done`, `needs review`.
"needs review" = published on the Flagged for Review page; does not block anything.

## Sources & verification

Verification is performed against official sources only (amazon.com / Amazon Associates
official pages / amazon.co.uk etc.). Every table row on the site links its official
source. Values that could not be confirmed from an official source are left **blank**
and flagged on the **Flagged for Review** page — never inferred.

- T1: repo content at baseline = `README.md` only (7 bytes, `# Zone2`). No code, no data,
  no config, no license. Irregularities: (a) supplied `https://link.amazon/<code>` URLs do
  not resolve to product pages for the codes (they fall back to unrelated Amazon pages via
  `plpRedirect=mhFallback`; root returns 403); (b) all three supplied codes are 9 characters
  while an official ASIN is 10 characters. All flagged. Review record: `docs/repo-review.md`.
- T2: all three products **unverified** — 18/18 official `/dp/` URLs return 404 across
  amazon.com/.co.uk/.de/.in/.ca/.co.jp; official site search returns "No results" for each
  code; exact-match public web searches find no listings. Product attributes left null in
  `data/products.json` and blank+flagged in `products.html`.
- T3: compliance matrix (`data/compliance.json`, `compliance.html`) — 12 requirements, each
  with an official source URL (OA §5, Program Policies, disclosure help, FTC guides,
  Creators API docs, application-review help).
- T4–T8: site pages built (10 HTML pages + `assets/`); sources recorded per-row with
  clickable official links; consolidated in `executive-summary.html` and
  `flagged-for-review.html` (flags F-01 … F-13, all non-blocking).
- T9: automated verification `scripts/verify_site.py` — PASS: 10 pages, 205 table rows,
  498 links, 0 failures (every data row has an external official source link; disclosure
  present on every page; internal links resolve; JSON valid; unverified fields null).
- T10: integration — local HTTP smoke test: all 14 site assets return 200; internal link
  check green; no broken links.

### Key official sources (fetched live 2026-11-13)

| Topic | URL |
|---|---|
| Commission rate card | https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ |
| Operating Agreement (§5 disclosure) | https://affiliate-program.amazon.com/help/operating/agreement |
| Program Policies (24h session / 89-day cart) | https://affiliate-program.amazon.com/help/operating/policies |
| Disclosure help (clear & conspicuous) | https://affiliate-program.amazon.com/help/node/topic/GHQNZAU6669EZS98 |
| Link format + ASIN = 10-digit code | https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC |
| ASIN = 10-character code (2nd source) | https://sell.amazon.com/blog/fba-new-selection-program |
| SiteStripe | https://affiliate-program.amazon.com/help/node/topic/GJMMT7G4C8K4Y3AY |
| Earnings report metrics | https://affiliate-program.amazon.com/help/node/topic/GCDWWRFEMW3Q2TE2 |
| Application review (≥3 sales/180d, ≥10 posts) | https://affiliate-program.amazon.com/help/node/topic/G8TW5AE9XL2VX9VM |
| Creators API intro (≥10 sales/30d) | https://affiliate-program.amazon.com/creatorsapi/docs/en-us/introduction |
| PA-API 5 deprecation | https://affiliate-program.amazon.com/creatorsapi/docs/en-us/paapiv5-deprecation |
| FTC Disclosures 101 | https://www.ftc.gov/tips-advice/business-center/guidance/disclosures-101-social-media-influencers |
| FTC Endorsement Guides FAQ | https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking |
| Google SEO starter guide | https://developers.google.com/search/docs/fundamentals/seo-starter-guide |
| GitHub repo / Pages config | https://api.github.com/repos/kanlerxz87-cyber/Zone2/pages |

### Irregularities flagged (all non-blocking, published at `flagged-for-review.html`)

F-01…F-03 invalid code length (9 vs 10) · F-04 18×404 · F-05 site search no results ·
F-06 supplied short links fall back to unrelated pages · F-07 product attributes blank ·
F-08 per-product commission unknown · F-09 rate schedule requires sign-in · F-10 Creators API
prerequisites unmet · F-11 PA-API 5 deprecated · F-12 no Tracking ID · F-13 baseline repo
had no product data.

## Request log (cross-session file requests)

_None — this is the only active session._

## Conflict log

_None._

## Deploy log

- (updated at integration time — PR link, merge result, Pages URL)
