# T68 verification record — session `arena/9ffe2d83-zone2` (2026-11-19 UTC)

**Scope.** Final integration for this wave: close change requests **CR-7, CR-8, CR-9, CR-10**,
take over the three stale conflicting pull requests (#162, #163, #172), re-verify every official
source this session's changes rest on, run every repository gate on the combined tree, then
PR → merge → confirm the GitHub Pages deploy. Branch base: `605e49f` (= `main` at claim time, the
PR #178 merge). Nothing in this record was copied from another session's prose; every
"re-read" below was fetched by this session on the date shown.

---

## 1. Official sources fetched live this session (2026-11-19)

| # | Source URL | What was confirmed | Used for |
|---|---|---|---|
| V-201 | https://www.amazon.com/dp/B0DZFD6R9Z (fetched in-page chunks 0–4, 8) | **"About this item":** "Built for long-lasting durability with a two-year assurance provided by CHEF iQ." **Item details table:** "Warranty Description: 3 Year". Same page: "Included Components: 3 Probes, Hub"; size selector offers 1/2/3/4 Probes (B0DZFD6R9Z is the 3-probe size); "running for up to 50 hours on a full charge" bullet re-confirmed (F-53); the ~20-entry "Specification Met" list re-confirmed (F-52); "ASIN: B0DZFD6R9Z" printed in Item details (10 characters). | **F-54** (new flag: warranty stated two ways), corroboration of F-52/F-53 and Q-22's size half |
| V-202 | https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/food-thermometers | Official USDA FSIS "Food Thermometers" factsheet resolves and carries the guidance the desk cites, including "inserted through the side until it reaches the center" for thin foods (matches the desk's `instant-read-or-leave-in.html` thin-food sentence) and the thermometer-type table (instant-read vs leave-in). | **CR-8** (FSIS is a primary .gov source; allow-list changed, not the source) |
| V-203 | https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/safe-temperature-chart | Resolves; "**Last Updated: Apr 14, 2025**" — matches the desk source list's own label exactly; contains the minimum-internal-temperature table. | CR-8 (source label line-by-line check) |
| V-204 | https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/air-fryers-and-food-safety | Resolves; "**Last Updated: Jun 24, 2024**" — matches the desk source list's label; air-fryer food-safety guidance (batching, not overcrowding, thermometer use). | CR-8 (source label line-by-line check) |
| V-205 | Google Search Central — https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links | Carried as source BD-15 by the salvaged RQ-05 row; the row's claim (paid links qualify with `rel="sponsored"`) is the same guidance the marketing gate G5 enforces. Not re-fetched this session; cited unchanged from the register. | #163 salvage (unchanged citation) |

Prices observed while fetching the listing were **not** transcribed anywhere (the site's no-price
rule); the Amazon fetch also surfaced star-rating/review blocks, which were likewise **not**
recorded (Program Policies restrict unlicensed rating display). No value in this session's diff
comes from those blocks.

## 2. Repository measurements (commands re-run this session)

| Command | Result |
|---|---|
| `python3 tools/ci_replay.py` | **61 / 61 workflow steps PASS**, including the Chromium browser verification (252 viewport checks, 24 accessibility pages, 0 WCAG A/AA findings) and the packaged-site contract |
| `python3 tools/validate_data.py` | PASS — `canonical_flags: 54`, `unique_flags_ids: 54`, `typed_flag_counts_checked: 54`, `sources: 49`, `rows: 108`, 0 errors |
| `python3 tools/audit_site.py` | PASS — 228 published pages; fragments, spec_sources, **prose_counts**, namespaces, disclosure, debris, board all PASS |
| `python3 marketing/scripts/verify_marketing.py` | PASS — **27 pages** (20 registry + 7 thermometer-desk, first time under G1–G10), 48 spec rows, 0 failures |
| `python3 tools/validate_board.py` | PASS — 9 pages, derived-count tokens re-measured |
| `python3 tools/validate_brief.py` | PASS — CR-10's four derived state rows agree with the tree and with the published `brief/index.html` |
| `python3 tools/build_front.py --check` / `build_site.py` / `build_root_views.py` / `build_summary.py` / `build_marketing.py --check` / `build_sitemap.py --check` / `build_brief.py --check` / `build_board.py --check` / `build_console.py` (replay steps) | committed output matches fresh builds everywhere |

**CR-8 negative tests (this session):**
1. Removing `www.fsis.usda.gov` from `OFFICIAL_HOSTS` → verifier exits 1 with **34 G10 failures**,
   each naming a `thermometers/*` page — proof the desk is now inside G1–G10, not merely that the
   allow-list grew.
2. Mutating one committed desk page (`<h1>` in `thermometers/index.html`) → verifier exits 1 with
   `G9 thermometers/index.html: committed file differs from a fresh build`.
Both mutations were restored; the verifier passes clean afterwards.

**CR-7 evidence:** `grep -o '<a[^>]*href="marketing/thermometers/index.html"' index.html` → 2 anchors
on the published front page. No edit needed; the request is already satisfied.

**CR-10 evidence:** `grep "no click on this site can become a qualifying purchase" brief/data/summary.json`
→ no match; the `the_blocking_fact` block now reads "The supplied tracking ID is not the remaining
missing string…" and states what is actually still missing. The four state-table counts
(with_tag / with_disclosure / price_pages / ai_powered_pages) are `{{tokens}}` filled by
`tools/build_brief.py` and re-measured against the published page by
`validate_brief.py::check_summary` (passing). No edit needed; recorded instead.

## 3. What this session changed (line-by-line)

| Change | File(s) | Verification |
|---|---|---|
| CR-8: G1–G10 over every rendered page incl. the desk; FSIS added to `OFFICIAL_HOSTS` | `marketing/scripts/verify_marketing.py` | 27 pages pass; both negative tests above |
| CR-9: new flag **F-54** (CHEF iQ warranty two ways), append-only; note addendum recorded | `ledger/flags.json` | row built from V-201; `validate_data` 54/54; no existing row edited; next-free id used (F-44…F-53 taken) |
| CR-9: `CANONICAL_FLAG_COUNT` 53 → 54 | `assets/js/data.js` | `check_flag_count` passes |
| CR-9: typed count prose → 54 (5 spots) and one internally inconsistent open/resolved pair corrected to (25 open · 29 resolved) per `tools/flag_state.py` | `EXECUTIVE_SUMMARY.md`, `README.md` | `validate_data.check_published_counts` passes; `audit_site` prose_counts PASS |
| CR-9: derived rebuilds (badge counts, F-54 row) | `pages/**` (via `tools/build_site.py`), root `flagged.html` (via `tools/build_front.py` invoked, not edited), `console/*` (via `tools/build_console.py`) | all `--check` gates pass |
| #163 salvage: TP-03's unsourced buyer-regret popularity claim removed; rests_on reworded to what the register can source | `board/data/topics.json` → regenerated `board/topics.html` | `validate_board` PASS; phrase absent from page and data |
| #163 salvage: RQ-05 self-contradictory og:image sentence → four derived tokens (`{{jsonld}} {{og_full}} {{og_image}} {{sc_pages}}`); new `og_full` metric (all five og identity tags) added to the measurement set | `board/data/requirements.json`, `tools/build_board.py` → regenerated `board/{requirements,topics,suggestions,verification}.html` + `board/data/measured.json` | `validate_board.check_derived_counts` re-measures the tree and passes; measured.json records the new token |
| Documentation | `EXECUTIVE_SUMMARY.md` (T68 addendum), this file | counts inside the addendum agree with `validate_data` |

Nothing else was edited. Product values, intent fields, sources, verification rows, campaign
ledger, workflows, and other sessions' namespaces are untouched.

## 4. Stale pull requests — disposition (handoff basis: >4 h without a commit, all CONFLICTING)

| PR | Branch (last commit) | Disposition |
|---|---|---|
| #163 | `arena/f669bf2c-zone2` (06:15Z) | **Salvaged, then closed.** Its only content was the two board-data corrections; both re-applied on the current tree above (plus a derived og:type count it had left typed). PR stays linked for its own record. |
| #172 | `arena/5d423a61-zone2` (06:20Z) | **Superseded, closed.** Two-dot diff vs `main` = 257 files / −19,907 lines: merging it would delete the shipped publication, shop, desk, and packaging tooling (`tools/publication.py`, `shop_layout.py`, `verify_publication.py`, `build_thermometers.py`, …). Its unique files are one unreferenced image and its own verification doc (retained on the branch/PR). Its buyer-first-front intent already shipped via #166/#174/#175/#177. |
| #162 (draft) | `arena/6ce606cb-zone2` (06:15Z) | **Superseded, closed.** Its `desk/` namespace, `build_desk.py`/`validate_desk.py` and parallel thermometer guides were overtaken by T64's `marketing/thermometers/` + T66's `shop/guides/` (merged #167/#170). Merging would likewise revert current main. |

No branch was deleted or force-pushed; no other session's work was discarded.

## 5. Irregularities found and retained (non-blocking)

1. **OBS-1 — stale comment in `tools/build_thermometers.py` (lines 27–29).** The docstring still
   says CR-8 "asks the owner of verify_marketing.py to extend G10 instead"; CR-8 is now closed.
   Comment-only fix, file outside this session's claim — recorded here for its owner rather than
   edited across scopes.
2. **OBS-2 — historical prose left as written.** `EXECUTIVE_SUMMARY.md`'s 2026-11-15-era addendum
   still says "22 CI steps green" and `README.md` still says "Registers after T63: flags
   F-01…F-48"; both are dated statements about that moment, not current-state claims, and neither
   matches the gates' count patterns. Rewriting history to look current would be the defect class
   this project keeps correcting.
3. **OBS-3 — `OBS-` the two typed brief rows** ("3 of 3", "0 of 3") describe the earlier
   three-link brief inside `brief/`, the namespace that deliberately preserves it; current state
   (five links, intent fields blank) lives on the intent register and current-release boards.
   Not silently rewritten.
4. **Open external gates unchanged (no session can close them):** CN-08 Pages source mode,
   permanent collector hosting, enrolled-workflow link/report confirmation, intended-ASIN
   confirmations, Search Console ownership, human/contact/privacy review.
5. **PRs #162/#163/#172 closing comments** carry each branch's disposition; the branches remain
   on the remote for audit.

## 6. Line-by-line re-check of this session's diff

Every changed line was reviewed against either (a) a source fetched today (rows V-201…V-204),
(b) a repository measurement re-run today (section 2), or (c) a removal of text that no source
supports (TP-03 claim, RQ-05 contradiction). No value was inferred, no blank was filled, no
price/rating/review count was recorded, and no claim of traffic, conversions or ranking appears
anywhere in the diff.
