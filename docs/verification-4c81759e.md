# Verification record — session 4c81759e (2026-11-19)

Task T75 / CR-14: re-read the CHEF iQ Sense warranty terms on the official listing and
fix the repository's contradiction (the Warranty field published one value while the
same listing states the warranty two ways).

## What was re-read (external, official)

- URL: `https://www.amazon.com/dp/B0DZFD6R9Z` (the official CHEF iQ Sense listing; served
  URL carried `?lv=shuf&channelId=500&plpRedirect=mhFallback&th=1`), fetched 2026-11-19.
- "About this item" bullet, verbatim: **"RESOURCES: Built for long-lasting durability with
  a two-year assurance provided by CHEF iQ."**
- "Item details" table, verbatim: **"Warranty Description | 3 Year"** (Model CQ60-3C-Z1-E,
  UPC 810170921148, ASIN B0DZFD6R9Z).
- Both statements appear on the same official listing. Neither was chosen, neither was
  inferred, no third value was invented. The Asurion protection-plan blocks on the page
  are unrelated to the manufacturer warranty.
- Same-session context read on the listing: price $119.99 (list $219.99), rating 4.2★
  (2,178 ratings), BSR #375 Kitchen & Dining / #4 Meat Thermometers — consistent with the
  already-published V-108 spec row (P-05 spec sourcing); no contradiction found there.
- The canonical external re-read for CR-14 also lives in flag **F-54** (live re-read
  2026-11-19 by session `9ffe2d83`; verbatim: "Re-read live on 2026-11-19 by session
  9ffe2d83 during CR-14 close-out: the listing states both 'Built for long-lasting
  durability with a two-year assurance provided by CHEF iQ' and 'Warranty Description:
  3 Year' on one official page.") and question **Q-22** (both statements quoted).

## Changes made (all tracked in the T75 claim)

1. `ledger/products.json` — P-05 attribute "Warranty": `verified` single-value row replaced
   with a `conflict` row. `value`: "two-year assurance (About this Item) / 3 Year (Item
   details)"; `source_ids: ["S62"]`; `source_label` quotes both statements and states that
   neither is chosen; `why_blank` explains the repository publishes both rather than
   selecting one.
2. `shop/data/catalog.json` — P-05 Warranty row: `status: "conflict"`, `same_page: true`,
   `src: ["S62"]`, value in the board's conflict format ("CONFLICT - same listing, two
   statements … re-read 2026-11-19" for each, 4 apostrophes), `note` pointing at F-54.
3. `ledger/verification.json` — **unchanged (still 108 rows)**. A V-109 append recording the
   2026-11-19 re-read was drafted, then dropped before commit: `audit_site.py`
   (`check_counts`) pins the "108 checks" prose in `README.md` and `EXECUTIVE_SUMMARY.md`
   to the register length, and both files are inside the active claim scope of PR #194
   (session `1b09bb6d`, who explicitly declined CR-14). Editing their count lines would be
   a cross-scope edit of another session's files, which the protocol forbids (log instead
   of edit). The evidence is fully preserved without the register row: F-54 (re-read),
   Q-22 (owner question), V-108 (spec sourcing), and this record. Reverted with
   `git checkout -- ledger/verification.json`; all gates re-run green afterwards.
4. Regenerated outputs (no hand-edits anywhere): `tools/build_root_data.py` →
   `assets/js/data.js`; `tools/build_site.py` → `pages/products.html` (+ all `pages/`,
   including `pages/verification.html` back at "108 checks"); `tools/build_shop.py` →
   `shop/chef-iq-sense-smart-wireless-meat-thermometer.html`, `shop/compare.html`,
   `shop/meat-thermometers.html`; `tools/build_front.py` → `guides/meat-thermometers.html`,
   `guides/instant-read-or-wireless-thermometer.html` (run only — `guides/**` and
   `build_front.py` belong to PR #194's claim); `tools/build_root_views.py` → root
   `verification.html`, `sources.html` (back to HEAD after the V-109 revert).

## Verification (gates run in this session, all exit 0)

| Gate | Result |
|---|---|
| `tools/validate_data.py` | PASS — 108 rows, 0 errors, 0 warnings |
| `tools/audit_site.py` | PASS — prose_counts (README/EXEC ↔ register), disclosure, orphans, fragments all PASS |
| `tools/validate_shop.py` | PASS — 17 pages + feed, S1–S12 clean |
| `tools/validate_board.py` | PASS — 9 pages |
| `tools/build_root_data.py --check` | PASS (no drift) |
| `tools/build_site.py --check` | PASS (`drifted_or_uncommitted: []`) |
| `tools/build_shop.py --check` | PASS |
| `tools/build_front.py --check` | PASS |
| `tools/build_root_views.py --check` | PASS |
| `tools/package_site.py` + `tools/verify_publication.py` | PASS — 228 pages packaged, 16 indexable reader URLs, 1,463 product anchors checked, 145 current factual rows |
| `python3 tests/test_pipeline.py` | PASS — 15/15 |
| `tools/ci_replay.py` | **CI REPLAY PASSED — 63 steps** (full `.github/workflows/pages.yml` replay incl. audit, summary check, Playwright browser checks) |

Content checks (grep of generated output):

- All five catalog conflict rows now render: P-03 Maximum temperature, P-02 Presets,
  P-02 Included accessories, P-05 Battery, **P-05 Warranty** (new). "Sources disagree"
  occurrences: `shop/compare.html` 2→3, `shop/meat-thermometers.html` 1→2, product page
  1→2. Guides show the conflict pill: `two-year assurance (About this Item) / 3 Year
  (Item details)` + `pb-pill--flag conflict`.
- No generated surface publishes a single verified "Two-year assurance …" value anymore;
  every remaining mention of either statement sits inside conflict/flag/question context
  (`ledger/flags.json`, `ledger/questions.json`, `pages/flags.html`, `pages/questions.html`,
  marketing conflict rows).
- P-04 still shows its pre-existing `NOT_TRANSCRIBED` blank for Warranty (flagged, not
  inferred) — unchanged behavior.

## Flagged for review (do not block merge)

- **F-54 (open)**: warranty stated two ways on one official listing — published as a
  conflict on every surface after this change; owner decision needed.
- **Q-22 (open)**: which warranty statement governs (2-year vs 3-year)? Owner input
  required before any single value can be published.
- V-109 deviation (register append dropped for the cross-scope reason above) — logged in
  the T75 claim amendment in `COORDINATION.md`.
