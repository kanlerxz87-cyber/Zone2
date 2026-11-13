# COORDINATION — Shared Task Board

This is the shared task board for the Zone2 Amazon Affiliate platform build.
It lists every task, its status (`unclaimed`, `in progress`, `done`, `needs review`),
the owning session ID, and the files each task touches.

## Session registry

| Session ID | Branch / role | Notes |
| --- | --- | --- |
| `ec67c431-zone2` | `arena/ec67c431-zone2` | Sole active session for this run. Acts as research + build + integration session. No other sessions have claimed work in this repo. |

> Coordination note: the task instructions describe a branch-per-session model
> (`session-<id>/<task>`). This session is pinned to branch
> `arena/ec67c431-zone2` by the environment and must not switch branches, so all
> work is committed to this single branch. With only one active session there is
> no cross-session conflict to resolve. Any file that would be a shared output
> (table data, site index/nav) is produced here as the final integration pass.

## Tasks

| # | Task | Status | Session | Files (scope) | Notes |
| --- | --- | --- | --- | --- | --- |
| T1 | Research & verify the 3 Amazon affiliate products line by line from official sources | done | ec67c431-zone2 | `js/data.js` | Products resolved from `link.amazon` redirects; fields verified against amazon.com listings. See verification log below. |
| T2 | Executive summary | done | ec67c431-zone2 | `content/executive-summary.md`, `executive-summary.html` | Important details, sources, flagged items. |
| T3 | Build static GitHub Pages site (landing + category subpages, dashboard UI, tables) | done | ec67c431-zone2 | `*.html`, `css/**`, `js/**`, `scripts/**` | Clean dashboard, all entries/findings in tables with source links. |
| T4 | Verification pass — every table row has an official source link; unverifiable values blank + flagged | done | ec67c431-zone2 | `js/data.js`, `flagged.html` | See "Verification" section. |
| T5 | Integration — re-verify combined data, confirm build + no broken links | in progress | ec67c431-zone2 | `*.html`, `css/**`, `js/**` | Running link checker and final review before deploy. |
| T6 | Deploy to GitHub Pages + PR to main + merge + confirm deploy | in progress | ec67c431-zone2 | `.github/workflows/*`, `gh` | Final step. Pages configured to publish repo root from `main`. |

## Verification performed (T1 / T4)

Each product's identity was confirmed by following the `link.amazon` short link
to its Amazon destination (the redirect target is the authoritative listing):

- `https://link.amazon/B04G1MEwY` → `https://www.amazon.com/dp/B0CDY277D3`
  (CHEFMAN 6 Quart Dual Basket Air Fryer Oven)
- `https://link.amazon/B02NbDxp3` → `https://www.amazon.com/dp/B09B7SB46R`
  (Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven)
- `https://link.amazon/B00hJ57DV` → `https://www.amazon.com/dp/B08DKYBTPH`
  (Chefman Air Fryer 8 Qt TurboFry 4-in-1)

**Key irregularity flagged for review:** the ASIN embedded in each `link.amazon`
short link (e.g. `B04G1MEwY`) is NOT the ASIN of the product it redirects to
(e.g. `B0CDY277D3`). The redirect target ASIN is the real product identifier.
This is expected behavior for Amazon's link shortener but is worth flagging so
reviewers don't mistake the short-link token for the product ASIN.

**Other flagged items:**
- `B0CDY277D3` official Amazon US price and star rating could not be captured
  from the Amazon US listing during this session → left blank + flagged unverified
  (third-party price trackers/blogs are NOT used as the value source).
- `B0CDY277D3` Amazon structured "Capacity" field says "6 liters" while the
  title and product description state "6 quarts (two 3-quart baskets)".
  Reported as-is; minor listing inconsistency flagged.
- Commission rate is the published US standard "Kitchen" rate (4.5%) per the
  Amazon Associates Commission Income Statement; exact browse-node
  classification should be confirmed in Associates Central. Flagged.

## Sources used (official / trusted)

- Amazon product listings (official): `amazon.com/dp/B0CDY277D3`, `B09B7SB46R`, `B08DKYBTPH`
- Amazon Associates Operating Agreement: `https://affiliate-program.amazon.com/help/operating/agreement`
- Amazon Associates Program Policies: `https://affiliate-program.amazon.com/help/operating/policies`
- Amazon Associates Disclosure (official Amazon page): `https://www.amazon.com/b?ie=UTF8&node=51812349011`
- Amazon Associates Commission Income Statement (official; rate table)

Full per-field source links are recorded in `data/sources.json` and rendered on
the site's Sources & Verification page.

## Handoff / takeover log

None — single session, no takeovers.

## Results

(filled in after deploy)
