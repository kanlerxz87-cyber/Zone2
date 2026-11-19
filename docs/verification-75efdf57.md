# Verification record — T66 (session `arena/75efdf57-zone2`), 2026-11-19

Task T66 was claimed on this branch as "T63"; it was renumbered on merge because session `cf98ff65`
had used T63 on `main` first (see `COORDINATION.md`). Scope: a shop-first front page, a `shop/`
section, CI repair, flags, and an owner briefing.

## 1. What was re-read live, and from where (all on 2026-11-19)

| What | Official page | Result |
|---|---|---|
| Supplied link 1 `B04G1MEwY` | https://link.amazon/B04G1MEwY → https://www.amazon.com/dp/B0CDY277D3 | Same destination as earlier records (CHEFMAN 6 Qt dual basket). No `tag=` in the resolved URL. |
| Supplied link 2 `B02NbDxp3` | https://link.amazon/B02NbDxp3 → https://www.amazon.com/dp/B09B7SB46R | Same (Emeril 26QT French door). |
| Supplied link 3 `B00hJ57DV` | https://link.amazon/B00hJ57DV → https://www.amazon.com/dp/B08DKYBTPH | Same (Chefman 8 Qt TurboFry). |
| Supplied link 4 `B0c8moW59` | https://link.amazon/B0c8moW59 → https://www.amazon.com/dp/B0DHZTCNR5 | Same (ThermoMaven). Listing shows "There is a newer model" B0GL7Z4KP4 → **F-44**. |
| Supplied link 5 `B0f3GKalj` | https://link.amazon/B0f3GKalj → https://www.amazon.com/dp/B0DZFD6R9Z | Same (CHEF iQ Sense Gen3). |
| Chefman 6 Qt Dual Window | https://www.chefman.com/products/turbofry-touch-dual-window-air-fryer | Capacity, 200–450 °F, 1700 W/120 V, dimensions, 13.3 lb, cETL, 1-year. Match to P-01 is by description only → **F-51**. |
| Chefman 8 Qt TurboFry Touch | https://www.chefman.com/products/turbofry-touch-air-fryer-1 | 8 Qt, 200–400 °F, 4 presets, 1700 W, 15.4×12.6×13.5 in, 12.8 lb. 400 vs Amazon title 450 is already **F-22**. |
| Emeril French door 360 | https://emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360 | 26 QT/24.6 L, 16.9×15.8×14.8 in, 120 V, 1-year. Presets 24 vs 25 (already **F-19**); accessories 7 vs Amazon 6 and an "11-in-1" image label → **F-49**; template placeholder text → **F-50**. |
| ThermoMaven listing details | https://www.amazon.com/dp/B0DHZTCNR5 | 1 s, ±0.5 °F NIST, thermocouple, waterproof, motion wake, auto-rotate, 1 AAA, calibration certificate. |
| CHEF iQ listing details | https://www.amazon.com/dp/B0DZFD6R9Z | 3 probes, 4 + 1 sensors, 1000 °F, WiFi + Bluetooth, hub speaker/notifications, two-year assurance. "Specification Met" list implausible → **F-52**. Battery 50 h here vs 70 h recorded in `ledger/products.json` → **F-53**, published as a conflict. |
| Safe minimum internal temperatures | https://www.foodsafety.gov/food-safety-charts/safe-minimum-internal-temperatures | 145 °F + 3 min rest (whole cuts), 145 °F fish, 160 °F ground meat and egg dishes, 165 °F poultry, casseroles, leftovers. Used in the temperatures guide and the seasonal callout. |
| Associates Program Policies | https://affiliate-program.amazon.com/help/operating/policies | Page states "updated April 14, 2026". No prices printed; Special Links only. |
| Google — qualify outbound links | https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links | `rel="sponsored"` for paid links; multiple values allowed → buttons use `sponsored nofollow`. |
| FTC Disclosures 101 | https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers | Disclosure next to the endorsement, plain words, no claimed experience you have not had → strip under the masthead, "(paid link)" on every button, "we have not tested" on every guide. |
| FTC endorsement hub | https://www.ftc.gov/business-guidance/advertising-marketing/endorsements-influencers-reviews | 16 CFR 255 and 16 CFR 465 linked from the footer. |

Nothing was inferred. A value no official page states is a dash with its reason. Where two official
readings disagree, both are printed as a conflict. Prices, ratings and review counts are never printed.

## 2. What was built

* `shop/` contains 17 pages plus `shop/feed.xml`:
  * an index, two categories and a comparison page;
  * five product pages;
  * a guides index and six guides;
  * an owner briefing.

  Data lives in `shop/data/catalog.json`, `guides.json` and `briefing.json`.
* `tools/build_shop.py` builds every page. Guide tokens (`{{v:…}}`, `{{p:…}}`, `{{s:…}}`, `{{buy:…}}`) are
  resolved at build time. A guide that quotes a blank or conflicting row fails the build.
* `tools/validate_shop.py` runs gates S1–S12 against the files on disk. Negative tests: a price, a foreign
  tag, a missing disclosure, an unsourced row, an unsourced comparison cell, an asserted visitor figure and
  an unresolved token were each caught. The files were restored afterwards.
* `tools/shop_layout.py` holds the one masthead, disclosure strip and footer.
  * It is used by the shop and, after the final merge, by `tools/build_front.py`.
  * The menu content is the one sessions cf98ff65 and 10727edd merged on `main`, plus one reader link
    ("Shop") and two tools entries (owner briefing, intent register).
  * The footer is a superset of every link previously in either footer.
* **The front page is session 10727edd's.**
  * This branch had its own shop-first front page. 10727edd's reader-first front page (PR #164) reached
    `main` first and does the same job, so this branch adopted it rather than replacing it.
  * The only change to it here is a shop link under the hero buttons.
* Imagery is in `assets/img/shop/*.jpg`: four generated, illustrative food and kitchen photographs, each
  labelled as illustrative. No product photos and no logos.

## 3. Gates run (final state, after merging `main` @ 881dbb7 — PRs #164 to #169)

* `python3 tools/ci_replay.py` → **CI REPLAY PASSED — 51 steps**: 49 existing steps plus the two new shop
  steps.
* `python3 tools/audit_site.py` → 210 published pages; all 7 checks PASS. `shop/index.html` was added to
  `REQUIRED_NAMESPACES`.
* `python3 tools/seo_audit.py` → all discoverability checks PASS. The sitemap is regenerated from the tree
  (208 URLs).
* `python3 tools/verify_front.py` → 15 pages, G1–G10 PASS. `python3 tools/validate_shop.py` → 17 pages +
  feed, S1–S12 PASS.

## 4. Edits outside the claimed file scope (integration), each logged in COORDINATION.md

| File | Edit | Why |
|---|---|---|
| `tools/build_front.py` (main's version, sessions cf98ff65 + 10727edd) | `masthead()` / `footer()` now delegate to `tools/shop_layout.py`; one shop link added under the hero buttons | One menu for the whole site. The links are unchanged apart from the additions. |
| `tools/verify_front.py` G9 | Expected reader menu gains `shop/index.html` (eight links); the footer must also expose `shop/index.html` and `shop/briefing.html` | Keeps the five product pages one click from every page. The rest of G9 is unchanged. |
| `tools/audit_site.py` | `shop/index.html` added to `REQUIRED_NAMESPACES` | Losing the route into the shop now fails the build. |
| `brief/data/summary.json` | Measured rows and the surface count re-derived with `validate_brief.measure()` | The brief gate refuses typed counts that disagree with the tree. Computed, not typed. |
| `EXECUTIVE_SUMMARY.md`, `README.md` | Typed flag counts re-derived (53; split 24 open / 29 resolved). Two dated "after T63" snapshots rewritten as ID ranges ("flags F-01…F-48") | `tools/validate_data.py` refuses a typed count that disagrees with the ledger. The snapshots keep their historical meaning. |
| Generated outputs (`pages/`, `board/`, `console/`, `release/`, `summary.html`, `assets/js/data.js`, `sitemap.xml`, front pages) | Regenerated by their own builders | They derive from the ledgers and the tree. |

`tools/ci_replay.py`: this branch's `conflict_markers()` guard was dropped in favour of the `preflight()`
on `main`, which covers every tracked file and adds a strict YAML parse. That is a superset.

## 5. Irregularities found (published on the Flagged for Review page)

New flags:
* **F-49** Emeril accessory and function counts disagree (7 vs 6; 10-in-1 vs 11-in-1).
* **F-50** The Emeril store page carries Shopify placeholder text.
* **F-51** P-01 is matched to Chefman's Dual Window page by description, not by a printed model number.
* **F-52** The CHEF iQ "Specification Met" list is implausible.
* **F-53** The CHEF iQ battery life is given two ways (50 h vs 70 h).

They were drafted as F-48…F-52 and published under the next free ids, because session 10727edd's F-44…F-48
reached `main` first.

Four further drafts were **not** added because flags on `main` already record them:
* the ThermoMaven newer model (10727edd's **F-44**);
* the unparseable workflow, the false-green replay and the wrong "cancelled runs" diagnosis
  (10727edd's **F-45**).

Two more were not added because **F-19** (Emeril presets) and **F-22** (Chefman 8 Qt 400 vs 450 °F) already
existed.

One data error in this session's own work was caught and fixed before publication. The catalog first showed
the CHEF iQ battery as a settled "up to 50 hours". The ledger records 70 hours from the same listing, so the
row is now a conflict citing F-53, and the guide no longer quotes a single figure.

## 6. Open overlap (owner decision)

Three guide sets answer some of the same buyer questions:
* `guides/` (10727edd);
* `marketing/thermometers/` (32788da6, T64);
* `shop/guides/` (this session).

Nothing was deleted or re-pointed. The options are on the owner briefing as **SG-S11**.
