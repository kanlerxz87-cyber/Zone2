# Verification record — T76 polished-marketing decision pack (session `arena/ed2307a8-zone2`)

**Date:** 2026-11-19 (UTC) · **Branch:** `arena/ed2307a8-zone2` · **Task:** T76 (proposals only; nothing implemented from the pack)

This record states what was re-read live on 2026-11-19, what was checked line by line, and what remains open. No verified value was altered. Blanks stay blank. No price, rating, popularity, conversion or revenue figure is asserted anywhere in this change.

## 1. Official sources re-read live on 2026-11-19

| ID | Official page | What was read (verbatim or tight paraphrase) | Used for |
|---|---|---|---|
| S40 | https://developers.google.com/search/docs/fundamentals/creating-helpful-content | Ranking systems "are designed to prioritize helpful, reliable information that's created to benefit people". Self-assess asks whether content provides "original information, reporting, research, or analysis", a "substantial, complete, or comprehensive description", "insightful analysis or interesting information that is beyond the obvious", avoids "simply copying or rewriting those sources", has a descriptive title, and answers "Who, How, and Why". | SG-T76-01/02/04, Q-T76-01 |
| S01 | https://affiliate-program.amazon.com/help/operating/agreement (Updated: October 15, 2025) | Section 1: links "must properly use the special 'tagged' link formats we provide" ("Special Links"); Program Content includes data, images, text and linking tools. | SG-T76-06, Q-T76-06 |
| S02 | https://affiliate-program.amazon.com/help/operating/policies (Updated: April 14, 2026) | Qualifying Purchases occur when a customer clicks through a Special Link and purchases within the session rules; Commission Income Statement and Participation Requirements incorporated by reference. | Context for SG-T76-06; no rate asserted |
| S24 | https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC | Qualifying text-link format is `http://www.amazon.com/dp/ASIN/ref=nosim?tag=YOURASSOCIATEID`. "ASIN is the 10-digit code that Amazon uses to denote specific products." | SG-T76-04 context, Q-T76-04 |
| FTC-D101 | https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers | Disclosure must be "hard to miss", placed "with the endorsement message itself", in simple clear language. "You can't talk about your experience with a product you haven't tried." | SG-T76-05, Q-T76-05 |
| S41 | https://developers.google.com/search/docs/essentials/spam-policies | Policy list includes "Thin affiliation", "Scaled content abuse", "Scraping", "Doorway abuse". Thin-affiliation guidance: good affiliate pages offer meaningful content such as original reviews, rigorous testing, navigation and comparisons. | SG-T76-02/04 context (no ranking claim) |
| GSC-VERIFY | https://support.google.com/webmasters/answer/9008080 | Verification methods include HTML file upload and HTML tag; verification lasts while the token is present and valid; data accrues after a property is added, taking a few days to start. | SG-T76-03, Q-T76-02/03 |
| GOOGLE-CANONICAL | https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls | Canonical annotations and sitemap inclusion are signals, not guaranteed indexing. | SG-T76-03 |
| M1 | https://chefman.com/products/turbofry-touch-dual-window-air-fryer | Model `RJ38-SQPF-3TDB-2W`; "TurboFry® Touch 6 Qt. Dual-Window Air Fryer"; "Sync Finish feature to ensure both baskets finish cooking simultaneously"; "Max temp: 450ºF/ 235ºC with Hi-Fry function". Page also shows prices and review counts; none are republished here (no-price policy). | Product spot-check (P1); no value changed |
| Live site | https://kanlerxz87-cyber.github.io/Zone2/ | Product-led front page: hero, five product cards (Chefman 6 Qt dual, Emeril 26 Qt oven, Chefman 8 Qt single, ThermoMaven instant-read, CHEF iQ Sense wireless), guide shelf, chooser, RSS follow. Product buttons point to `amazon.com/dp/<ASIN>?tag=shopnow047c-20` and read "paid link". | Baseline for SG-T76-01/04; no redesign implemented |

Sources not re-fetched this session (carried from prior dated verification, labelled as such): S04 rate card, S06 PA-API deprecation, S23 application review, S39 gen-AI content, S12 sponsored links, S11/FTC-ENDORSE, FSIS-TEMP, S61. No new claim in this change depends on them.

## 2. Line-by-line checks on the change

### 2.1 `docs/board-9251f262.json` (appended SG-T76-01..06, Q-T76-01..06, `t76_note`)

- Each suggestion has id, area, title, summary, three options (label/text/cost/tradeoff), recommendation naming one option label, waits_on, source, status, implemented, owner_direction. Verified by `tools/verify_front.py` G5 (recommendation valid, waits_on resolves, Proposed status, implemented false).
- Each question has id, question, status, what_we_know, what_is_missing, how_to_discover, blocks, source. All three text fields non-empty; blocks resolve (G5).
- Waits_on/blocks are bidirectional: SG-T76-01↔Q-T76-01, SG-T76-02↔Q-T76-02, SG-T76-03↔Q-T76-03, SG-T76-04↔Q-T76-04, SG-T76-05↔Q-T76-05, SG-T76-06↔Q-T76-06.
- Every source key exists in the file's `sources` map (S40, GOOGLE-CANONICAL, FTC-D101, S01, S24, GSC-VERIFY). No new URL introduced; no citation link carries an Associates tag (G4).
- No price-like string, no metric figure (G2/G8): the pack discusses measurement, demand and hosting in words only; no number is bound to a metric word.
- Counts are derived, never typed: suggestions 18→24, questions 17→23 (21 open, 2 answered). `tools/build_front.py` renders headline counts via `num_word`; `tools/verify_front.py` G9 re-derives them.

### 2.2 Regenerated pages (through builders only, no hand edits)

- `suggestions.html`, `questions.html`, `behind-the-site.html` via `tools/build_front.py`. `index.html`, `summary.html`, `guides/*` rewritten byte-identical (no drift).
- `board/data/measured.json`, `board/suggestions.html`, `board/questions.html`, `board/requirements.html`, `board/verification.html`, `board/flagged.html` via `tools/build_board.py`. Drift cause measured: tree-wide Amazon-link counts moved because three new source citations point at Amazon hosts (S01, S24): outbound 3036→3039, sponsored 663→666, reader-page sponsored 446→449. No board prose number was typed; all counts are measured in the same run.
- `behind-the-site.html` drift: byline now reads 24 suggestions, 21 open questions (derived from the register).

### 2.3 Products, links, disclosure

- Five supplied links and observed destinations unchanged: B04G1MEwY→B0CDY277D3 (Chefman 6 Qt dual), B02NbDxp3→B09B7SB46R (Emeril 26 Qt oven), B00hJ57DV→B08DKYBTPH (Chefman 8 Qt single), B0c8moW59→B0DHZTCNR5 (ThermoMaven instant-read), B0f3GKalj→B0DZFD6R9Z (CHEF iQ Sense wireless). Intended-ASIN fields remain blank; intent and observation stay in separate fields (G10).
- Reader product links carry `tag=shopnow047c-20`, `rel="sponsored nofollow"`, and "(paid link)" labelling; citation links stay untagged (G4). Disclosure sentence present above product content on every front page (G3).
- No verified product value was altered in this change. The Chefman spot-check above reproduces the stored model, capacity framing, Sync Finish and Hi-Fry maximum; nothing was re-typed into the ledger.

### 2.4 `EXECUTIVE_SUMMARY.md` (append-only addendum)

- Dated T76 addendum appended at end; earlier chronology preserved verbatim. No count prose changed: `tools/audit_site.py` prose_counts PASS (the "108 checks" prose still matches the 108-row verification register, which this change does not touch).

## 3. Gates (this session, all green)

- `tools/build_front.py --check` — front pages current (15 pages)
- `tools/verify_front.py` — front gate OK (16 pages)
- `tools/build_board.py --check` — board 9 pages current; `tools/validate_board.py` — all checks pass (9 pages)
- `tools/audit_site.py` — 228 pages; fragments, spec_sources, prose_counts, namespaces, disclosure, debris, board all PASS
- `tools/ci_replay.py` — 63/63 steps PASSED (includes every builder --check, intake/board/console gates, negative tests)
- `tools/validate_data.py` — 108 rows, 0 errors, 0 warnings
- `tools/validate_shop.py` — PASS (17 pages + feed, S1-S12)
- `tools/package_site.py` + `tools/verify_publication.py` — 228 pages, 16 indexable, 1463 product anchors, 145 factual rows, ok true
- `tests/test_pipeline.py` — 15/15

## 4. Irregularities and open items (non-blocking; published for owner review)

No new flag ID was created (`ledger/flags.json` is outside this task's scope). The following remain open and are carried on the Flagged for Review page and questions register:

1. **Intended-product confirmation blank for all five links** (Q-T76-04 / Q-T50-01). Observed destinations are not asserted as intent.
2. **Short-link compliance unresolved.** A missing tag in a fetched redirect proves neither invalidity nor attribution; the site does not call the supplied short links invalid.
3. **Search Console not verified** (Q-T76-02/03). Topic choice stays hypothesis-led until query data exists; no topic is called trending.
4. **Permanent measurement host absent.** Three browser events and two report importers are implemented; production Pages collection stays off.
5. **No named editor or corrections contact** (Q-T76-05). Authorship stays AI-assisted organizational; no hands-on testing is claimed.
6. **ThermoMaven newer-model notice** (F-44, carried): the observed listing advertises a newer model; nothing is inferred about it.
7. **CHEF iQ listing conflicts** (F-54 battery and warranty, carried): both statements published as conflicts; no term chosen.
8. **Overlap with open PRs #194 (T73), #184 (T70), #182 (T69):** `suggestions.html`, `questions.html`, `behind-the-site.html`, `board/**`, `EXECUTIVE_SUMMARY.md` are regenerated/appended outputs. Whichever side merges later must re-merge `origin/main` and regenerate through the builders.

## 5. What this change does not do

- Does not implement any suggestion. All six new rows read Proposed — awaiting owner decision, Implemented No.
- Does not redesign the site, add photography, add prices/ratings, rank products, or claim traffic, conversion or revenue.
- Does not touch `tools/**`, `.github/**`, `ledger/**`, `content/**`, `README.md`, `marketing/**`, `shop/**`, or `guides/**` beyond builder output.
