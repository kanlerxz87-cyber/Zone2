# Verification record — T64, the thermometer desk

Session `arena/32788da6-zone2` · 2026-11-19 (UTC) · base `main` @ `4398071`, rebased onto `66b7213` (PR #165, T65)

## What shipped

A reader-facing section, `marketing/thermometers/`, that closes RQ-04. Before T64, the two newest products
(ledger P-04 ThermoMaven, P-05 CHEF iQ Sense) had no question-shaped page anywhere on the site.

| Page | What it answers |
|---|---|
| `marketing/thermometers/index.html` | The desk: both thermometers side by side, with tagged Special Links |
| `marketing/thermometers/thermomaven-instant-read.html` | ThermoMaven HT07 (B0DHZTCNR5), every spec row with its source |
| `marketing/thermometers/chef-iq-sense-wireless.html` | CHEF iQ Sense, 3 probes (B0DZFD6R9Z), every spec row with its source |
| `marketing/thermometers/instant-read-or-leave-in.html` | *Instant-read or leave-in: which meat thermometer do you actually need?* |
| `marketing/thermometers/thermometer-for-air-fryer.html` | *Do you need a meat thermometer for an air fryer?* (bridges to the air-fryer desk) |
| `marketing/thermometers/where-to-put-the-thermometer-in-a-turkey.html` | *Where does the thermometer go in a turkey? Three spots, one number* (in season: Thanksgiving is 2026-11-26) |
| `marketing/thermometers/is-my-meat-thermometer-accurate.html` | *Is your meat thermometer accurate? USDA's ice-water check* |

The guide titles are editorial hypotheses about how readers phrase the question. They are not claims about
search volume or popularity. No keyword tool was consulted, and Search Console is still not connected (RQ-28).

The section is reachable in five ways:
- the Counter Notes nav entry "Thermometers" on every marketing page;
- the guides index (`topics/index.html#thermometers`);
- `marketing/feed.xml`, with four new items;
- `marketing/sitemap.xml`;
- the root `sitemap.xml`.

## Sources: every one read live on 2026-11-19

| ID | Page | Used for |
|---|---|---|
| T1 (ledger S61) | https://www.amazon.com/dp/B0DHZTCNR5 | ThermoMaven rows: About this item, Product information, Item details, overview table |
| T2 (ledger S62) | https://www.amazon.com/dp/B0DZFD6R9Z | CHEF iQ rows: About this item, Product information, Item details, size selector |
| T3 | https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/food-thermometers | Placement, thermometer types table, calibration, colour |
| T4 | https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/safe-temperature-chart | Safe minimum internal temperatures, °F and °C (last updated Apr 14, 2025) |
| T5 | https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/air-fryers-and-food-safety | Air-fryer guidance (last updated Jun 24, 2024) |

Both supplied short links were re-opened the same day:
- `https://link.amazon/B0c8moW59` resolved to `amazon.com/dp/B0DHZTCNR5`;
- `https://link.amazon/B0f3GKalj` resolved to `amazon.com/dp/B0DZFD6R9Z`.

Neither resolved URL carried a tag. This is consistent with the ledger and claims nothing about the short links'
validity. The pages say plainly that this shows where each link goes, not which product the brief intended (F-03).

### How the values were checked

Every value and every quoted fragment in `marketing/data/thermometers.json` was compared to the live page text
**twice**: once while drafting, and again after drafting, against fresh fetches of T1–T5.

The second pass removed or corrected four things:
- The category path was carried from the 2026-11-17 ledger read and not re-read, so it was removed.
- The air-fryer hook paraphrased USDA too loosely ("whatever the appliance"), so it now uses USDA's wording.
- A calibration sentence put the "you may need to replace it" line in the wrong place. It now sits in the
  calibration section, as on the USDA page.
- A turkey sentence merged two separate USDA statements, so it is now split into two.

Values recorded on 2026-11-17 that could not be re-read as text on 2026-11-19 are **not reprinted**. Both now
sit in image-only Product Description sections:
- CHEF iQ "within 1 °F" accuracy. The row is blank, with that reason.
- CHEF iQ 70-hour battery figure. The row is PARTIAL and prints the 50-hour statement only.

Prices, star ratings, review counts and Best Sellers ranks are shown on both listings. None is stored or printed.

## Gates

| Gate | Result |
|---|---|
| `python3 tools/build_thermometers.py --check` | OK: 7 pages · 30 spec rows · 5 sources · gates passed · current |
| `python3 tools/build_marketing.py --check` | 30 outputs (20 pages + 7 desk pages + 3 machine-readable), current |
| `python3 marketing/scripts/verify_marketing.py` | OK: 20 pages · 0 failures. G13/G14 also run over the 7 desk pages (orphans, sitemap, feed targets, canonical) |
| `python3 tools/ci_replay.py` | **CI REPLAY PASSED, 49 steps**, before and after rebasing onto T65 |
| `python3 tools/audit_site.py` | 187 pages; fragments, spec_sources, prose_counts, namespaces, disclosure, debris and board all PASS |
| `python3 tools/build_sitemap.py --check` | current, 185 URLs |
| `python3 tools/seo_audit.py` | all discoverability checks PASS (D5: `marketing/sitemap.xml` covers `marketing/**`) |
| `python3 tools/build_head_meta.py --audit` | 102 pages under the contract, 0 problems |
| `python3 tests/test_pipeline.py` | 15/15 |

### Negative tests of the desk gate

Each of these was injected in memory and **refused**:
1. a valued row without a source;
2. a blank row without a reason;
3. a blank row carrying a value;
4. a prose sentence with no source id;
5. a dollar amount in the copy;
6. "out of 5 stars" in the copy;
7. a banned phrase ("game-changer");
8. a first-hand claim ("we tested");
9. a source on a non-allow-listed host;
10. a citation of an unregistered source id.

Ten of ten fired.

## Design decisions

1. **The desk renders inside `build_marketing.build()` but stays outside `PAGES`.** verify_marketing's G10
   allow-list (`marketing/scripts/verify_marketing.py`, not in T64's scope) has no `www.fsis.usda.gov`. Every
   food-safety sentence must cite USDA, so adding the pages to `PAGES` would fail G10, and the alternative would
   be to drop the sources.
   - Merging the pages into `build()`'s output means G13/G14, the feed, the sitemap and the guide index still
     cover them.
   - `build_thermometers.py` enforces G1–G12 equivalents itself, through its own `ALLOWED_HOSTS`.
   - CR-8 asks the verifier's owner to close the gap properly.
2. **No new rows in `ledger/flags.json`.** Appending F-44/F-45 would make the "43 flags" prose wrong in
   `README.md` and on the root pages. `audit_site check_counts` and `validate_data check_published_counts` would
   then fail, and those files are not T64's.
   - The irregularities are recorded as **Q-21** and **Q-22** in `ledger/questions.json`, with **SG-15** in
     `ledger/suggestions.json`.
   - CR-9 asks an integration pass to promote them to flags and update every count surface together.
3. **Additive hooks in the shared shell.** `shell()`/`json_ld()` gained optional `read_on` and `rail_note`. With
   the defaults, every existing page renders byte-identical (proved by `--check` before the nav entry was added).
   Desk pages state their own read date, sources and JSON-LD dates instead of inheriting the air-fryer desk's.

## Scope expansions, each logged in COORDINATION.md

- `tests/test_pipeline.py`: one assertion. `len(rendered)` now also counts `build_thermometers.page_rels()`.
  The caveat assertions run on the desk pages too. No other session claims `tests/**`.
- `brief/data/summary.json`: the four typed page counts were re-derived by hand (7→10 tagged, 168→175 pages).
  This is the drift that CR-3 has tracked since T60.
- `tools/build_marketing.py`: a refused build now exits 1. Before, it printed `BUILD REFUSED` and exited 0.
- Derived views regenerated by their own builders after the ledger appends:
  - `pages/questions.html`, `pages/suggestions.html`;
  - `decisions/*`, `DECISIONS.md`;
  - `release/index.html`;
  - `brief/index.html`;
  - `board/*`;
  - `console/*`.

## Irregularities found

| Where | What | Recorded as |
|---|---|---|
| T1 ThermoMaven listing | Amazon banner "There is a newer model of this item", pointing to B0GL7Z4KP4 (the same title in orange) | Q-21 |
| T2 CHEF iQ listing | Warranty given as "two-year assurance" (About this item) and "3 Year" (Item details) | Q-22; printed as CONFLICT |
| T2 CHEF iQ listing | Multi-size listing (1/2/3/4 probes). The link opens the 3-probe ASIN the short link resolved to | Q-22 |
| T2 CHEF iQ listing | The battery and accuracy figures from 2026-11-17 now render only as images and cannot be re-read | Rows PARTIAL / blank |
| T2 CHEF iQ listing | "Specification Met" lists 20 standards (including ISO 13485), with no certificates linked | Quoted as a count only; not presented as verified certification |
| `tools/build_marketing.py` | A refused build exited 0 | Fixed here |
| `brief/data/summary.json` | The note on "Published pages carrying an Associates tag" still says no click can become a qualifying purchase. That has been untrue since T58 added the tag | Not edited (prose outside the counts); CR-10 |
| USDA FSIS | The turkey guide URL `…/lets-talk-turkey-consumer-guide-safely-roasting` returns 404 | Not cited; T3/T4 used instead |

## Cross-scope requests

- **CR-7 → T63:** link `marketing/thermometers/` from the front page when `tools/build_front.py` is rebuilt.
- **CR-8 → owner of `marketing/scripts/verify_marketing.py`:** add `www.fsis.usda.gov` to `OFFICIAL_HOSTS`, then
  run G1–G10 over every rendered page (SG-15 option A).
- **CR-9 → integration session:** promote Q-21/Q-22 to F-44/F-45 in one pass that updates `README.md`,
  `EXECUTIVE_SUMMARY.md`, `assets/js/data.js` and the root pages together (SG-15 option C).
- **CR-10 → brief namespace:** correct the stale "no click can become a qualifying purchase" note, and derive the
  four state-table counts (completes CR-3).
