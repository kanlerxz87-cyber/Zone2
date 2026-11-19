# Verification record — T66 (session `arena/6ce606cb-zone2`, 2026-11-19 UTC)

**Renumbered from T63 at integration.** `cf98ff65` claimed and merged T63 (PR #166, #168) while this branch
was in flight; `da47d78d` merged T65 (PR #165); `32788da6` merged T64 (PR #167, thermometer desk) and `f669bf2c` holds T64 in open PR #163. This branch merged
`main` twice and kept all of their work (see "Conflicts and how they were resolved").

## What this session shipped

| Area | What changed | Where |
|---|---|---|
| Front page | Leads with all five supplied listings: three air fryers (rows from `marketing/data/facts.json`) and two meat thermometers (rows read from `ledger/products.json` `resolved.specs`, sources S61/S62). A "Quick pick" list, a seasonal strip, two product shelves, derived counts. The duplicated "5 / 5" receipt and the missing space in "document." are gone; the board teaser count is derived. | `tools/build_front.py` → `index.html` |
| Navigation | cf98ff65's reader menu and single "Project & tools" group kept; two category links (Air fryers, Meat thermometers) added to the reader menu, and the decision desk added to the tools group. Every dashboard stays in the footer. | `masthead()`, `tools/verify_front.py` G9 |
| Thermometer guides | `guides/thermometers.html` (category, both listings row by row, safe-temperature chart) and three question-shaped guides: *Is the turkey done?*, *Instant-read or leave-in?*, *Can you use a meat thermometer in an air fryer?* Every Fahrenheit figure in an article block carries a citation in the same block (enforced by gate D5). | `guides/thermometers*.html` |
| Decision desk | 25 suggestions (12 from the T50 board + 13 new) under four goals (shop / findable / machinery / publication), each with options, evidence, unknowns and how to find out; nothing is marked decided. A ranked "answer these first" page for 19 questions. | `tools/build_desk.py`, `tools/validate_desk.py`, `desk/` |
| Overlay data | Editorial voice, food-safety rows, guide metadata, goal map, brief signals, one evidenced question update (Q-T50-02 answered: the tag was supplied), new suggestions and questions. Read-only input. | `docs/front-6ce606cb.json` |
| CI | Removed the conflict markers that had made `pages.yml` unloadable since PR #158; added `preflight()` to `tools/ci_replay.py`; two additive workflow steps (desk `--check` and gate) and `check("desk")`/`check("guides")` in the link heredoc. | `.github/workflows/pages.yml`, `tools/ci_replay.py` |
| Flags | F-44 … F-50 appended (register now 50 flags). | `ledger/flags.json` |

## Sources read on 2026-11-19 and what each supports

| Source | URL | Supports |
|---|---|---|
| Five supplied short links (live re-resolution) | `https://link.amazon/B04G1MEwY`, `…/B02NbDxp3`, `…/B00hJ57DV`, `…/B0c8moW59`, `…/B0f3GKalj` | Each still opens the same listing: B0CDY277D3, B09B7SB46R, B08DKYBTPH, B0DHZTCNR5, B0DZFD6R9Z. No resolved URL carried an Associates tag; the per-link `btn_ref` token changed again. The short links are **not** claimed invalid. |
| Amazon listing B0DHZTCNR5 (ThermoMaven 1 Sec) | https://www.amazon.com/dp/B0DHZTCNR5 | Title matches the ledger's recorded title; listing shows "There is a newer model of this item" → B0GL7Z4KP4 (F-45). |
| Amazon listing B0DZFD6R9Z (CHEF iQ Sense Gen3) | https://www.amazon.com/dp/B0DZFD6R9Z | Title matches the ledger; the battery-life conflict (50 h vs 70+ h) is still on the page and still published as a conflict. |
| FoodSafety.gov — Safe Minimum Internal Temperature Chart (page says last reviewed November 21, 2024) | https://www.foodsafety.gov/food-safety-charts/safe-minimum-internal-temperatures | Poultry and stuffing 165 °F; beef/pork/veal/lamb steaks, roasts, chops 145 °F + 3 min rest; ground meat 160 °F; fish 145 °F (or opaque and flakes); egg dishes 160 °F; leftovers and casseroles 165 °F. |
| USDA FSIS — Food Thermometers | https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/food-thermometers | A thermometer is the only reliable way; placement (thickest part, away from bone/fat/gristle; whole poultry at thigh, wing and breast; thin food from the side); calibration (ice water 32 °F, boiling 212 °F at sea level); thermometer types and reading times; 40–140 °F for more than 2 hours is a risk; do not leave a thermometer in food unless made to stay there. |
| Chefman TurboFry Touch (official) | https://chefman.com/products/turbofry-touch-air-fryer-1 | Auto shut-off halts cooking when the timer ends or the basket is opened (already in `facts.json` as P3 row M5). |
| Google — Creating helpful, reliable, people-first content | https://developers.google.com/search/docs/fundamentals/creating-helpful-content | Who/How/Why and original-value questions (SG-T66-02, SG-T66-09). |
| Google — Block Search indexing with noindex | https://developers.google.com/search/docs/crawling-indexing/block-indexing | Page-level noindex works on static hosting; robots.txt noindex is not supported (SG-T66-05). |
| Search Console Help — Verify your site ownership | https://support.google.com/webmasters/answer/9008080 | HTML-file and HTML-tag verification are available (SG-T66-03, Q-T66-03). |
| GitHub Docs — About custom domains and GitHub Pages | https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/about-custom-domains-and-github-pages | www/apex/subdomain support; verify the domain first (SG-T66-04). |
| GitHub Docs — Events that trigger workflows | https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows | Workflows can run at a scheduled time (SG-T66-07). |
| RSS Advisory Board — RSS 2.0 Specification (2.0.11) | https://www.rssboard.org/rss-specification | "All date-times in RSS conform to the Date and Time Specification of RFC 822" (F-47). |

Prices and star ratings were visible on the product pages and are **not** published anywhere (rows say
"withheld" with the reason). No commission, traffic or conversion figure was added.

## Irregularities found (flags F-44 … F-50)

* **F-44 (closed)** — the 0-job "failure" runs after PR #158 were workflow **parse failures**, not cancellations as CR-6 said. Fixed independently by T65, cf98ff65's T63 and this session.
* **F-45 (open)** — ThermoMaven listing shows a "newer model" notice (B0GL7Z4KP4); the site keeps linking the supplied destination until the owner says otherwise.
* **F-46 (open)** — `facts.json` shows the 8-quart Chefman's power as verified 1700 W; `ledger/products.json` records the same attribute as a CONFLICT (an Amazon bullet says 1000 W).
* **F-47 (open)** — `marketing/feed.xml` uses ISO-8601 `pubDate`; RSS 2.0 requires RFC 822. The feed also lists only marketing topic pages, so the root guides are in no feed. `tools/build_marketing.py` is outside this session's scope.
* **F-48 (open)** — release-readiness RR-08 still describes the site as three air-fryer appliances.
* **F-49 (open)** — the ledger records the CHEF iQ warranty as a verified two-year term. Re-read on 2026-11-19, the listing's About this item says "two-year assurance provided by CHEF iQ" and its Item details say "Warranty Description | 3 Year" (T64's Q-22 found the same). The T66 pages now print both as a conflict through an overlay `row_overrides` entry. The ledger row is unchanged (another session's file).
* **F-50 (open)** — T64 (PR #167, `marketing/thermometers/`) and T66 (`guides/thermometers*.html`) published thermometer guides on the same day. Three questions overlap. Every Fahrenheit figure agrees (145/160/165 °F food-safety values and the listings' 572/1000 °F probe limits), and each pair cites the same government pages. Each T66 guide now links its T64 counterpart, and the T66 category page links T64's desk. The consolidation choice is decision-desk item SG-T66-13 (recommendation B: keep T64's section).
* Not flagged, noted for the record: cf98ff65's completion record disputes T65's statement that the tag is "verified and active". This session agrees the account status is unconfirmed; nothing here says otherwise.

## Gates run on the final merged tree

* `python3 tools/ci_replay.py` → preflight OK, **CI REPLAY PASSED — 51 steps**.
* `python3 tools/audit_site.py` → 186 pages, 7/7 checks PASS.
* `python3 tools/verify_front.py` → 13 pages, G1–G10 pass.
* `python3 tools/validate_desk.py` → 25 suggestions in 4 goals, 19 questions, 3 guides; D1–D5 pass.
  Negative-tested: an uncited temperature, a desk count edited by hand, and a row rendered as "Decided" each fail the gate.
* `sitemap.xml` rebuilt from the tree: 184 URLs.

## Conflicts and how they were resolved

* **`pages.yml` vs T65** — a blank-line difference; main's side kept. Both preflights (T65's `check_workflow_health`, this session's `preflight`) are kept; they overlap but do not conflict.
* **`tools/build_front.py` vs cf98ff65's T63** — five hunks. Kept their tools group, aria-current, tag-status disclosure wording, "editorial hypotheses" line, derived proposal count, `summary.html` target and `ASIN_HELP_URL`; added the two category links and the desk. `tools/verify_front.py` G9's expected reader menu updated to include the two category links (cf98ff65's six links keep their order). Two duplicate footer entries (Design brief, Submitted links) removed in favour of cf98ff65's.
* **`COORDINATION.md`** — both registry rows kept; this session's claim renumbered to T66.
* **Generated files** (index, guides, suggestions, questions, summary, release, board) — regenerated from their generators on the merged tree; never hand-merged.

## Cross-scope edits (logged, minimal)

* `brief/data/summary.json` — five typed measurements updated to the values its own gate measures (pages carrying the tag, disclosure, price; prose page count; published-surface count). No other field touched.
* `release/index.html`, `brief/*.html`, `board/**`, `assets/js/data.js`, `pages/**`, `console/**`, `summary.html` — regenerated by their own generators because counts derived from the tree and the flag register changed. No generator logic changed.
* `README.md`, `EXECUTIVE_SUMMARY.md` — flag counts updated 43 → 50 (open/resolved 22 · 26) where `tools/audit_site.py` compares prose to the register.

## Still needs the owner (see the decision desk)

The questions blocking the most suggestions are listed first at `desk/questions.html`. The main ones: which
products were intended (Q-T50-01), the Associates account and commission band (Q-T50-04/05), a Search Console
property (Q-T66-03), a host for first-party analytics (Q-T50-10), a named author (Q-T66-04), whether the
ThermoMaven link should follow the newer model (Q-T66-07).
