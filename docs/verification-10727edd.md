# Verification record — session 10727edd (T63)

Branch `arena/10727edd-zone2`, base `4398071` (main after PR #161). Everything was checked on 2026-11-19 (UTC).
This file lists what was checked, where the evidence lives, and what is still unknown. It adds to the
earlier verification records and does not replace them.

## 1. The defect that mattered most: CI had not run since PR #158

| What | Evidence | Status |
|---|---|---|
| `.github/workflows/pages.yml` contained unresolved conflict markers (`<<<<<<< HEAD` at l.87 and l.386) | `git show 4398071:.github/workflows/pages.yml`; the [workflow runs](https://github.com/kanlerxz87-cyber/Zone2/actions/workflows/pages.yml) on 515cb7a, 00914b59, df17393 and 4398071 finished as *failure* with zero jobs, and each run is named after the file path, which is what GitHub shows when it cannot parse a workflow | **Fixed** in 7c29929. Both sides of each hunk were kept, because they were two sessions' separate gate steps |
| CR-6 blamed the red runs on `cancel-in-progress` | Same run list: a cancelled run reports `cancelled`, not `failure`, and still has jobs | **Corrected** (F-45; COORDINATION T63 row) |
| `tools/ci_replay.py` stayed green the whole time | It replayed `run:` lines and skipped the marker lines it did not recognise | **Guarded**: `preflight()` now refuses to run if a tracked non-Markdown file has a conflict marker or if pages.yml fails a strict YAML parse. A negative test with an injected marker failed as expected |

Local replay at hand-off: **CI REPLAY PASSED — 49 steps**.

## 2. Product facts used in the new reader pages

Every specification cell is rendered from `ledger/products.json` or `marketing/data/facts.json` along with
that row's own source link, so no value was retyped. Before publishing, I checked each figure the new
prose repeats against its ledger row:

| Figure in prose | Ledger row | Official source |
|---|---|---|
| ThermoMaven 1-second reading, ±0.5 °F, one AAA battery, 572 °F upper range | P-04 `resolved.specs` | [amazon.com/dp/B0DHZTCNR5](https://www.amazon.com/dp/B0DHZTCNR5) |
| CHEF iQ 1000 °F heat safe; battery "up to 50 hours" vs "70+ hours" | P-05 `resolved.specs` (conflict row, left unresolved) | [amazon.com/dp/B0DZFD6R9Z](https://www.amazon.com/dp/B0DZFD6R9Z) |
| Emeril 26 Qt: 10-in-1 modes, 16.9″ × 15.8″ × 14.8″, 120 V, 1-year warranty | facts.json P2; products.json warranty row | [Emeril Everyday official store](https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360) · [amazon.com/dp/B09B7SB46R](https://www.amazon.com/dp/B09B7SB46R) |
| Emeril 1700 W | facts.json P2 | [amazon.com/dp/B09B7SB46R](https://www.amazon.com/dp/B09B7SB46R) |
| Chefman 8 Qt: four presets, 1700 W / 120 V, 200–400 °F | facts.json P3 | [chefman.com TurboFry Touch](https://chefman.com/products/turbofry-touch-air-fryer-1) |
| 145 / 160 / 165 °F minimums, 3-minute rest, "as measured with a food thermometer" | `tools/front_t63.py` FSIS rows → S63 | [USDA FSIS chart](https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/safe-temperature-chart) (page date 2025-04-14) |

The rendered pages contain no dash or placeholder cells. No price or star rating appears on any page, as
policy requires (verify_front G2). Advice I could not source (kettle circuits, "15 cm" clearances,
"away from bone") was removed rather than softened.

## 3. Compliance sources re-read

| Requirement | Source | Where it is enforced |
|---|---|---|
| "As an Amazon Associate I earn from qualifying purchases." stated clearly and prominently | [Operating Agreement](https://affiliate-program.amazon.com/help/operating/agreement) §5 | Strip under the masthead and in the footer of all 14 front pages (verify_front G3) |
| Prices only through Amazon-served links or the API; no misleading claims; Special Links carry the Associates ID | [Program Policies](https://affiliate-program.amazon.com/help/operating/policies), page dated 2026-04-14 | G2 (no prices); every product link carries `tag=shopnow047c-20` |
| Disclosure placed with the endorsement; do not describe experience with a product you have not used | [FTC Disclosures 101](https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers) (S64) | "(paid link)" on every product button; the guides say plainly that nothing was bench-tested |
| Endorsement guides index (16 CFR 255) | [FTC Endorsements hub](https://www.ftc.gov/business-guidance/advertising-marketing/endorsements-influencers-reviews) (S65) | Method page |
| Paid links marked as such for search engines | `rel="sponsored nofollow"` | G4. This includes Amazon URLs cited as *evidence* on the board |

## 4. Flags added (register now F-01 … F-48)

- **F-44 (open, owner).** The ThermoMaven listing shows a "newer model" notice pointing to B0GL7Z4KP4. Nothing about that ASIN is inferred.
- **F-45 (closed).** The unparseable workflow; see §1.
- **F-46 (closed).** Counts typed into the front page and board had drifted; they are now rendered from the registers.
- **F-47 (open, owner).** The brief's S07/S24 IDs and its FLG-003 link come from a different register (Zone3). The FTC pages are registered here as S64 and S65.
- **F-48 (closed).** The thermometers had no reader-facing page; they now have three guides.

## 5. Still unknown, and how to find out

| Unknown | Why it cannot be settled from here | How to settle it |
|---|---|---|
| Whether `shopnow047c-20` is the account's active tracking ID (Q-T50-02) | It needs the owner's Associates Central login | Associates Central → Account settings → Manage tracking IDs |
| Whether short `link.amazon` Special Links attribute to the tag (FLG-003) | The test needs a signed-in session | Associates Central link checker, or Reports → Link-type after a test click. The site does **not** claim the links are invalid |
| The intended ThermoMaven ASIN (F-44 / Q-T63-03) | Only the owner knows which product was meant | The owner records it in the product-intent record |
| Search Console ownership (Q-T63-05) | It needs the owner's Google account | HTML-file or meta-tag method, both workable on GitHub Pages ([Google help](https://support.google.com/webmasters/answer/9008080)) |
| The CHEF iQ battery life (50 h vs 70+ h) | The listing contradicts itself | CHEF iQ's support pages or the manual; until then it is shown as a conflict |
| Any click, order or earnings figure | No first-party data exists yet | The campaign ledger stays empty until Associates reports exist. No forecasts |

## 6. Gates run before hand-off

`build_front.py --check`, `verify_front.py` (14 pages), `validate_data.py`, `validate_brief.py`,
`verify_marketing.py` (G14 now accepts feed items under `guides/` only if the page file exists),
`build_sitemap.py`, and the full `tools/ci_replay.py`: **49/49 passed**.

Known carry-over: the four "of N pages" values in `brief/data/summary.json` are still typed figures (CR-3).
They were re-measured to 174 and remain open as CR-3 until someone converts them into build-time tokens.
