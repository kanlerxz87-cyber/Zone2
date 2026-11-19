# T69 verification — current versus preserved decision-register rollups

**Date:** 2026-11-19 (UTC)
**Session / branch:** `arena/60b0ea6b-zone2`
**Original baseline:** `605e49f` (PR #178 merge). During the work, `main` advanced through PRs #179–#186; this branch was rebased onto `34bab9d`, retaining the upstream coordination records and completed changes.

## Scope and observed defect

The reader-facing decision pages combine two distinct registers:

- **Current release:** At the original T69 baseline, 5 proposals and 7 questions. After merged PR [#183](https://github.com/kanlerxz87-cyber/Zone2/pull/183) added four current S68 proposals and four current Q68 questions, the source arrays contain **9 proposals and 11 questions**. Their current-data date is `2026-11-19` (`publication.DATE`).
- **Earlier preserved board:** 18 suggestions (4 with recorded owner directions) and 17 questions (15 recorded open, 2 answered) in `docs/board-9251f262.json`. Its compilation date is `2026-11-16`; the latest recorded owner-direction date is `2026-11-19`.

At the original baseline, `suggestions.html` showed 5 current proposal cards and 18 earlier suggestion rows, while its headline/byline reported only earlier-board figures. `questions.html` showed 7 current-release questions plus 17 earlier questions, while its lead summarized only the earlier set. The source data was present; the problem was that page summaries did not clearly distinguish which register each count and date described. The final regenerated pages now reflect the expanded 9/11 current arrays without changing the 18/17 preserved board.

While this branch was in progress, PR [#180](https://github.com/kanlerxz87-cyber/Zone2/pull/180) separately corrected the page-update label and added G11. That work is retained: both summaries state `Page last updated 2026-11-19` from `UPDATED_ON`, separately from current data and preserved-board dates. PR #183's S68/Q68 source additions and their live-source review are recorded in [its verification report](verification-5f7f77a4.md); this branch did not edit that source data.

## Changes

- Label current-release and earlier-preserved registers separately on both pages.
- Derive counts from the current proposal/question arrays and preserved-board arrays. Keep all source rows, statuses, owner directions, answers, options, and choices unchanged.
- Distinguish page-update date (`UPDATED_ON`), current release data date (`publication.DATE`), earlier board compilation date (`compiled_utc`), and suggestions' latest owner-direction date.
- Extend `tools/verify_front.py` to validate visible labels, counts, dates, and rendered row IDs against both inputs; retain upstream G11's page-freshness check.
- Add 12 regression tests in `tests/test_front_surfaces.py`, including stale current/preserved counts, stale page/current/board/owner-direction dates, and missing current rows (including Q68 IDs).
- Run the tests in the existing Front-of-house workflow command (`verify_front.py && test_front_surfaces.py`); this branch adds no workflow step. The combined workflow now has 62 steps because upstream PR #183 added its separate product-note overlap gate and regenerated its derived brief count. This branch leaves `brief/**` untouched.

No `content/publication.json` or preserved board data was changed in this branch. No product specification, redirect observation, product-intent field, affiliate link, account state, or strategic choice was changed. Supplied short-link compliance remains unresolved; this work makes no invalidity claim.

## Verification performed on the combined tree rebased onto `34bab9d`

- `python3 -m py_compile tools/publication.py tools/build_front.py tools/verify_front.py tests/test_front_surfaces.py` — pass.
- `python3 tests/test_front_surfaces.py` — **12/12 pass**, including negative mutations.
- `python3 tools/build_front.py --check` — current; 15 generated front pages.
- `python3 tools/verify_front.py` — pass; all 16 front-of-house pages.
- `.venv/bin/python tools/ci_replay.py 'Front-of-house gate'` — pass; confirmed the combined CI step executes all 12 regression tests.
- `python3 tools/build_brief.py --check` — 9 generated pages current, with the combined 62-step workflow count.
- `python3 tools/validate_brief.py` — pass; `python3 tools/test_brief.py` — 14/14 negative tests pass.
- `.venv/bin/python tools/ci_replay.py` — **62/62 steps pass** with strict PyYAML parsing enabled in the local ignored virtual environment. Artifact contract: 228 HTML pages (16 indexable), 1,451 product anchors and 143 current factual rows checked. Synthetic browser verification: 252 viewport checks and 24 accessibility pages; these fixtures are not campaign results.
- `git diff --check` — pass.

The full local replay includes packaging and browser checks, but is not a substitute for the GitHub Actions run or actual post-merge Pages verification. Those hosted checks remain pending until this PR's checks and main deployment complete.

## Unchanged external gates

Intended ASIN/listing/source confirmations, authenticated Associates attribution, permanent production analytics hosting, Search Console ownership and authorized reports, and real orders remain unverified and unchanged. Existing questions and Flagged for Review surfaces continue to carry those gaps.
