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
  no config, no license. Irregularity: `https://link.amazon/<ASIN>` URLs supplied in the
  brief are NOT valid Amazon domains (official short link host is `amzn.to`; product pages
  are `amazon.com/dp/<ASIN>`). Flagged for review; ASINs extracted and verified individually.
- T2/T3/T4–T8: sources recorded per-row in `data/*.json` and rendered on the site with
  clickable official links; consolidated in `executive-summary.html` and
  `flagged-for-review.html`.

## Request log (cross-session file requests)

_None — this is the only active session._

## Conflict log

_None._

## Deploy log

- (updated at integration time — PR link, merge result, Pages URL)
