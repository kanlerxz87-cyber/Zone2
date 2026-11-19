# Mobile type and target-size sign-off (T76)

**Recorded:** 2026-11-19  
**Scope owner:** session `5a3dd862`  
**Requirement:** S-20 / RQ-16  
**Result:** reader-facing mobile surfaces pass the measured 11 px type floor and 24 × 24 CSS-pixel standalone-target floor at the tested viewport. The 44 px rule remains a component-specific usability floor, not a claim of WCAG 2.5.5 conformance.

## What was measured

- Chromium **153.0.8010.0**, Playwright, mobile emulation, **390 × 844 CSS px**, full page load and `document.fonts.ready`.
- All **219** pages returned by `tools/build_board.py`'s published-page set were swept. The detailed sign-off set was **85 pages**: the 64 reader pages counted by the board builder (marketing, guides, journal and the listed root reader pages), plus all 17 `shop/` pages and root `compare.html`, `shop.html`, `about.html` and `privacy.html`.
- Text measurement walks non-whitespace text nodes and counts each distinct parent element once where its computed font size is below 11 px. The same definition is enforced by the mobile browser test.
- Target measurement uses visible, non-zero bounding boxes for links, buttons, summaries, non-hidden inputs, selects and `[role=button]`. Inputs with a non-empty wrapping/associated label are measured at the label box; targets with `pointer-events:none` or zero opacity are excluded. Inline links with neighboring sentence text are classified separately under the SC 2.5.8 Inline exception. The measured floors use unrounded `getBoundingClientRect()` dimensions.
- Horizontal overflow was checked at the same viewport. No reader-scope page overflowed.

## Before and after

After PR #194, the chooser PR #205 and the PR #207 integration merged while this task was in progress, the comparison was re-run on that combined page tree. The before pass served the current HTML and non-CSS assets while routing the four reader stylesheets and two generated dashboard CSS copies to their `origin/main` versions at `46601cf` (PR #207); the after pass used this branch's working-tree stylesheets. This isolates this branch's CSS changes while keeping the updated page set and browser/method constant.

| Reader-facing measure, 85 pages | Before | After | Change |
|---|---:|---:|---:|
| Text-bearing elements below 11 px | 455 | 0 | −455 |
| Standalone targets with either dimension below 24 CSS px | 1,900 | 0 | −1,900 |
| Standalone targets with either dimension below 44 CSS px | 3,329 | 2,030 | −1,299 |
| Pages with horizontal overflow | 0 | 0 | no change |

These are measurements of this page tree and viewport, not a claim about every device or browser. The scope intentionally excludes operator/admin namespaces; those remain outside the T76 claim.

## The 2,030 remaining targets below 44 px

All 2,030 have **both dimensions at least 24 CSS px** in the measurement, so they meet the size branch of WCAG 2.2 SC 2.5.8. The remainder is classified as follows (mutually exclusive buckets, by measured selector):

| Bucket | Count | Treatment |
|---|---:|---|
| Source/reference chips and links (`a.src`, `.pb-src`, `.sh-more-link`) | 1,318 | Kept at their compact 24 px-or-greater target height in dense source lists and tables. |
| Other table-cell links | 222 | Kept compact to preserve evidence-table readability and fit. |
| Header, navigation and footer links | 220 | Header/top-nav/footer components use a 44 px **minimum height** rule; some narrow labels are less than 44 px wide, so this is not asserted as a 44 × 44 square. |
| Other section, card, disclosure and content links/controls | 270 | At least 24 × 24 CSS px; includes varied content links and compact section controls. |
| **Total** | **2,030** | No reader-scope standalone target below 24 × 24 CSS px. |

The 44 × 44 square is WCAG 2.2 SC 2.5.5 Target Size (Enhanced), a **Level AAA** criterion; it is not the AA threshold. This pass uses 44 px minimum height for prominent header/footer/navigation controls as a usability convention, and deliberately does not enlarge dense evidence-table references to 44 px. It does **not** claim that every measured target meets SC 2.5.5.

The input exception was checked against the rendered label: for example, the comparison suggestion radios sit within their clickable `.cn-choice` cards, so the label card—not the 16 px native radio—is the effective measured target.

## Changes and permanent check

- Added phone-only (max-width 780 px) 11 px text-floor rules to `marketing/assets/marketing.css`, `assets/css/style.css`, `assets/css/publish.css` and `assets/css/shop.css`; desktop rules are unchanged.
- Added 24 px standalone-link floors and 44 px minimum-height rules for prominent navigation/footer controls. `style.css` restates the `publication.css`-owned small-text rules with `!important` because `publication.css` loads last; it also floors the chooser's result and no-script fallback text added in merged PR #205. Neither `publication.css` nor chooser markup/JS was edited in this task.
- `tests/browser.cjs` checks the 11 px floor at 390 px across the full 85-page sign-off set. Pages in the current indexable sweep and pages in the archive sweep are both covered; operator/admin pages outside this scope are not included.
- S-20 remains recorded with the 44 px caveat above; the phone-only sticky comparison bar was already present on `compare.html` from the earlier T72 pass.

## Official criterion references

- W3C, WCAG 2.2 Understanding SC 2.5.8 Target Size (Minimum), Level AA: <https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html>. Its size branch is 24 × 24 CSS px and it describes the Inline exception for links in sentences.
- W3C, WCAG 2.2 Understanding SC 2.5.5 Target Size (Enhanced), Level AAA: <https://www.w3.org/WAI/WCAG22/Understanding/target-size-enhanced.html>. Its size branch is 44 × 44 CSS px and it has its own Inline exception.

## Gate results

- `python3 tools/ci_replay.py`: **66/66 passed**, including browser verification and the 390 px type-floor assertion across the full sign-off set.
- `python3 tools/validate_board.py` and `python3 tools/build_board.py --check`: passed.
- `python3 tests/test_pipeline.py`: 15/15; link-policy, page-identity, price-guard and publication tests passed; event client: 12 behavior/privacy cases passed.
- Remaining standalone validators are recorded in the T76 close-out in `COORDINATION.md`.

No product facts, affiliate destinations, observed redirect targets or verification-register values were changed by this pass.
