# T69 verification — current versus preserved decision-register rollups

**Date:** 2026-11-19 (UTC)
**Session / branch:** `arena/60b0ea6b-zone2`
**Original baseline:** `605e49f` (PR #178 merge). During the work, `main` advanced through PRs #179 and #180; this branch was rebased onto `e081f42` and retains both upstream coordination histories and the merged freshness-label correction.

## Scope and observed defect

The reader-facing decision pages combine two distinct registers:

- **Current release:** 5 proposals and 7 questions in `tools/publication.py`, with current-data date `2026-11-19` from `publication.DATE`.
- **Earlier preserved board:** 18 suggestions (4 with recorded owner directions) and 17 questions (15 recorded open, 2 answered) in `docs/board-9251f262.json`. Its compilation date is `2026-11-16`; the latest recorded owner-direction date is `2026-11-19`.

Before this repair, `suggestions.html` showed the 5 current proposal cards and 18 earlier suggestion rows, while its headline/byline reported only the earlier-board figures. `questions.html` showed 7 current-release questions plus 17 earlier questions, while its lead summarized only the earlier set. The source data was present; the page summaries did not clearly distinguish which register each count and date described.

While this branch was in progress, PR [#180](https://github.com/kanlerxz87-cyber/Zone2/pull/180) separately corrected the page-update label and added the G11 freshness check. That completed upstream change is retained: the new summaries still state `Page last updated 2026-11-19` from `UPDATED_ON`, separately from the current data date and preserved-board dates. This branch's current/preserved rollup work is complementary to, not a replacement for, that freshness fix.

## Changes

- Label current-release and earlier-preserved registers separately on both pages.
- Derive counts from the respective proposal, question, and board arrays. Preserve all rows, status, owner directions, answers, options, and choices without modification.
- Distinguish the page-update date (`UPDATED_ON`), current release data date (`publication.DATE`), earlier board compilation date (`compiled_utc`), and suggestions' latest owner-direction date.
- Extend `tools/verify_front.py` to validate the visible labels, counts, dates, and rendered row IDs against both inputs; retain upstream G11's page-freshness contract.
- Add 12 regression tests in `tests/test_front_surfaces.py`, including stale current/preserved counts, stale page/current/board/owner-direction dates, and missing current rows.
- Run the tests in the existing Front-of-house workflow command (`verify_front.py && test_front_surfaces.py`), not in a new workflow step. This keeps the CI replay count at 61 and leaves unrelated generated `brief/**` files untouched.

No product specification, source claim, redirect observation, product-intent field, affiliate link, account state, or strategic choice was changed. `docs/board-9251f262.json` remains untouched. No external product or policy claim was added or re-verified in this derived-summary change.

## Verification performed after rebasing onto `e081f42`

- `python3 -m py_compile tools/publication.py tools/build_front.py tools/verify_front.py tests/test_front_surfaces.py` — pass.
- `python3 tests/test_front_surfaces.py` — **12/12 pass**, including negative mutations.
- `python3 tools/build_front.py --check` — current; 15 generated front pages.
- `python3 tools/verify_front.py` — pass; all 16 front-of-house pages.
- `.venv/bin/python tools/ci_replay.py 'Front-of-house gate'` — pass; confirmed the combined CI step executes all 12 regression tests.
- `python3 tools/build_brief.py --check` — 9 generated pages current; derived step count remains stable.
- `python3 tools/validate_brief.py` — pass; `python3 tools/test_brief.py` — 14/14 negative tests pass.
- `.venv/bin/python tools/ci_replay.py` — **61/61 steps pass** with strict PyYAML parsing enabled in the local ignored virtual environment. Artifact contract: 228 HTML pages (16 indexable), 1,451 product anchors and 138 current factual rows checked. Synthetic browser verification: 252 viewport checks and 24 accessibility pages; these fixtures are not campaign results.
- `git diff --check` — pass.

The workflow-derived count of 61 is preserved; `brief/**` was not modified. The full local replay includes packaging and browser checks, but is not a substitute for the GitHub Actions run or actual post-merge Pages verification. Those hosted checks remain pending until PR checks and main deployment complete.

## Unchanged external gates

Intended ASIN/listing/source confirmations, authenticated Associates attribution, permanent production analytics hosting, Search Console ownership and authorized reports, and real orders remain unverified and unchanged. Existing question and Flagged for Review surfaces continue to carry those gaps. Supplied short-link compliance remains unresolved; no invalidity conclusion is made.
