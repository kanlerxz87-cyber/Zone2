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
| Supplied link 4 `B0c8moW59` | https://link.amazon/B0c8moW59 → https://www.amazon.com/dp/B0DHZTCNR5 | Same (ThermoMaven). Listing shows "There is a newer model" B0GL7Z4KP4 → **F-45**. |
| Supplied link 5 `B0f3GKalj` | https://link.amazon/B0f3GKalj → https://www.amazon.com/dp/B0DZFD6R9Z | Same (CHEF iQ Sense Gen3). |
| Chefman 6 Qt Dual Window | https://www.chefman.com/products/turbofry-touch-dual-window-air-fryer | Capacity, 200–450 °F, 1700 W/120 V, dimensions, 13.3 lb, cETL, 1-year. Match to P-01 is by description only → **F-50**. |
| Chefman 8 Qt TurboFry Touch | https://www.chefman.com/products/turbofry-touch-air-fryer-1 | 8 Qt, 200–400 °F, 4 presets, 1700 W, 15.4×12.6×13.5 in, 12.8 lb. 400 vs Amazon title 450 is already **F-22**. |
| Emeril French door 360 | https://emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360 | 26 QT/24.6 L, 16.9×15.8×14.8 in, 120 V, 1-year. Presets 24 vs 25 (already **F-19**); accessories 7 vs Amazon 6 and an "11-in-1" image label → **F-48**; template placeholder text → **F-49**. |
| ThermoMaven listing details | https://www.amazon.com/dp/B0DHZTCNR5 | 1 s, ±0.5 °F NIST, thermocouple, waterproof, motion wake, auto-rotate, 1 AAA, calibration certificate. |
| CHEF iQ listing details | https://www.amazon.com/dp/B0DZFD6R9Z | 3 probes, 4 + 1 sensors, 1000 °F, WiFi + Bluetooth, hub speaker/notifications, two-year assurance. "Specification Met" list implausible → **F-51**. Battery 50 h here vs 70 h recorded in `ledger/products.json` → **F-52**, published as a conflict. |
| Safe minimum internal temperatures | https://www.foodsafety.gov/food-safety-charts/safe-minimum-internal-temperatures | 145 °F + 3 min rest (whole cuts), 145 °F fish, 160 °F ground meat and egg dishes, 165 °F poultry, casseroles, leftovers. Used in the temperatures guide and the seasonal callout. |
| Associates Program Policies | https://affiliate-program.amazon.com/help/operating/policies | Page states "updated April 14, 2026". No prices printed; Special Links only. |
| Google — qualify outbound links | https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links | `rel="sponsored"` for paid links; multiple values allowed → buttons use `sponsored nofollow`. |
| FTC Disclosures 101 | https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers | Disclosure next to the endorsement, plain words, no claimed experience you have not had → strip under the masthead, "(paid link)" on every button, "we have not tested" on every guide. |
| FTC endorsement hub | https://www.ftc.gov/business-guidance/advertising-marketing/endorsements-influencers-reviews | 16 CFR 255 and 16 CFR 465 linked from the footer. |

Nothing was inferred. A value no official page states is a dash with its reason. Where two official
readings disagree, both are printed as a conflict. Prices, ratings and review counts are never printed.

## 2. What was built

* `shop/` contains 17 pages plus `shop/feed.xml`: an index, two categories, a comparison page, five
  products, a guides index, six guides and an owner briefing. Data lives in `shop/data/catalog.json`,
  `guides.json` and `briefing.json`.
* `tools/build_shop.py` builds every page. Guide tokens (`{{v:…}}`, `{{p:…}}`, `{{s:…}}`, `{{buy:…}}`)
  are resolved at build time. A guide that quotes a blank or conflicting row fails the build.
* `tools/validate_shop.py` runs gates S1–S12 against the files on disk. Negative tests: a price, a
  foreign tag, a missing disclosure, an unsourced row, an unsourced comparison cell, an asserted
  visitor figure and an unresolved token were each caught. The files were restored afterwards.
* `tools/shop_layout.py` holds the one masthead, disclosure strip and footer for the front and the shop.
* `index.html` is rebuilt by `tools/build_front.py` as a shop-first front page. Order: products,
  seasonal callout, categories, guides, how we pick, project & tools.
* Imagery is in `assets/img/shop/*.jpg`: four generated, illustrative food and kitchen photographs,
  each labelled as illustrative. No product photos and no logos.

## 3. Gates run (final state, after merging `main` @ 695031c)

* `python3 tools/ci_replay.py` → **CI REPLAY PASSED — 51 steps**. That is 49 existing steps plus the
  two new shop steps.
* `python3 tools/audit_site.py` → 197 published pages; all 7 checks PASS. `shop/index.html` was added
  to `REQUIRED_NAMESPACES`.
* `python3 tools/seo_audit.py` → all discoverability checks PASS. The sitemap is regenerated from the tree.
* `python3 tools/verify_front.py` → 9 pages, G1–G10 PASS. `python3 tools/validate_shop.py` → S1–S12 PASS.

## 4. Edits outside the claimed file scope (integration), each logged in COORDINATION.md

| File | Edit | Why |
|---|---|---|
| `tools/verify_front.py` | G9's expected reader menu changed to the shop-first list; the footer must also expose `journal/`, `marketing/`, `shop/index.html` and `shop/briefing.html` | The owner's brief asks the front to lead with products. The rest of cf98ff65's G9 contract is unchanged (one "Project & tools" group, every dashboard in it and in the footer). |
| `tools/audit_site.py` | `shop/index.html` added to `REQUIRED_NAMESPACES` | Losing the route into the shop now fails the build. |
| `brief/data/summary.json` | Three measured rows and two prose counts re-derived with `validate_brief.measure()` (21 of 185 tagged, 185 of 185 disclosed, 0 of 185 priced, 19 surfaces) | The brief gate refuses typed counts that disagree with the tree. The values were computed, not typed. |
| `EXECUTIVE_SUMMARY.md`, `README.md` | Typed "43 flags" updated to 52, and the open/resolved split to 23/29 | `tools/validate_data.py` refuses a typed flag count that disagrees with the ledger. |
| Generated outputs (`pages/`, `board/`, `console/`, `release/`, `summary.html`, `assets/js/data.js`, `sitemap.xml`) | Regenerated by their own builders | They derive from `ledger/flags.json` and from the tree. |

## 5. Irregularities found (published on the Flagged for Review page)

**F-44** CI markers broke the gate on `main` · **F-45** ThermoMaven newer model · **F-46**
`ci_replay` false pass · **F-47** correction to the "cancelled runs" record · **F-48** Emeril accessory
and function counts · **F-49** Emeril placeholder text · **F-50** P-01 model identity by description
only · **F-51** CHEF iQ "Specification Met" list · **F-52** CHEF iQ battery 50 h vs 70 h.

Two candidate flags were **not** added, because F-19 and F-22 already record them.

One data error was found and fixed in this session's own work before publication. The catalog first
showed the CHEF iQ battery as a settled "up to 50 hours". The ledger records a second figure, 70 hours,
on the same listing, so the row is now a conflict. The guide no longer quotes a single figure.
