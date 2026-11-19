# Verification record — T76 (session `arena/47786492-zone2`, 2026-11-19 (UTC))

Scope: close RQ-15 / S-19 — build the three-question "which one is for you" chooser **immediately above the
comparison table** on the comparison page. Answer BQ2-06 and resolve FL-05. Claim: `COORDINATION.md` §
"T76 claim". Base: `main` at `0c101a7` (PR #200 merge).

## 1. What was asked, and what the tree actually had

RQ-15 (`board/data/requirements.json`, brief ref S-19, P2) recorded `measured_status: not present`,
`verdict: overstated`, with the note that the brief's own status word said "Implemented". BQ2-06
(`board/data/questions.json`) asked whether a chooser was ever built or whether the requirement was
satisfied by a question-led article section. FL-05 (`board/data/flags.json`, `medium`) carried the same
opening.

Line-by-line review of the tree confirmed **no chooser component existed**. The board's own derived
measurement `chooser_pages` reported `1`, but that was a **false positive**: `tools/build_board.py`'s
measurement regex (`chooser|which-one|which one is for you|three-question`) matched only one published
page, `intake/tracking.html`, which mentions the phrase in passing and is not a chooser. The comparison
page (`compare.html`) had no chooser at all. The only related reader surface was the separate, hardcoded
`#kitchen-finder` form in `assets/js/publication.js` (a kitchen-priority → guide mapper), which is a
different component and was deliberately left untouched.

**Decision:** the chooser is built, not restated. The recommendation maps to the five formats the page
already publishes and is framed as a starting point. No price, rating, popularity, conversion, performance
or intended-ASIN claim is introduced.

## 2. Official sources

The chooser introduces **no new factual claim**, so no new product or policy source needed to be read live
this session. It reuses only facts already published on the comparison page and the registered guide
routes. The Amazon Associates disclosure and tagging obligations that govern the page are unchanged
(existing product links already carry `tag=shopnow047c-20` and `rel="sponsored"`); the chooser's own links
are **internal** and carry no tag, so no Associates source re-read was required for this change.

The sources the component draws on are the five product listings already registered in `ledger/sources.json`
(S1..S67) and `content/publication.json` (the `sources` map). These were registered and reviewed by the
prior sessions that built the comparison page; this session did not re-open them.

| Id | Source | What was checked | Used for |
|---|---|---|---|
| V1 | `content/publication.json` (products P1..P5, `reader.fit_for` / `tradeoff`) | The five formats, their types and the buyer checks already published on the comparison page | The chooser's answer→product map and its "check the listing" reminders |
| V2 | `content/guides.json` (`guides/instant-read-or-wireless.html`) | The temperature-tool guide exists and is a valid route | The chooser's temperature branch and the no-JavaScript fallback link |

No value in the chooser was inferred or filled in: every option label rests on the format/job wording the
comparison page already prints, and every recommendation is a format pointer plus a check reminder.

## 3. What was built

**`tools/publication.py`** — a `CHOOSER` data block and a `chooser()` renderer, placed in `compare()`
**immediately above** `<section id="compare-list">`. The section carries the phrase "Which one is for you"
(the requirement's own wording) and a `data-chooser` attribute so `build_board.py`'s own measurement
counts it. The answer map and the five guide targets are rendered into one `data-chooser-map` attribute
from a single `_chooser_payload()` helper, so the server-rendered markup and the client script read the
**same** map — no second, drifting copy of the product slugs in the script.

**`assets/js/publication.js`** — progressive-enhancement chooser logic (client-side only, no network, no
storage). It reads the map from the form's `data-chooser-map`, reads the three radio answers, maps the
combined answer to a format + guide, and renders the result as a format pointer plus a link to the
comparison and the guide. A `<noscript>` fallback links directly to the comparison and the temperature-tool
guide, so the page still works without JavaScript.

**`assets/css/publication.css`** — chooser styles matching the publication design system (`.cn-chooser*`),
mobile-first, with 44 px tap targets on the options and the submit control at ≤780 px.

## 4. Register updates (same tree)

| Row | File | Change |
|---|---|---|
| RQ-15 | `board/data/requirements.json` | `measured_status` → `implemented 2026-11-19 (T76)`, `verdict` → `matches`, evidence rewritten with the derived `{{chooser_pages}}` |
| BQ2-06 | `board/data/questions.json` | `state` → `answered`, `answer` filled, `how_to_close` / `who_can_close` updated (open questions carry empty answers — none open remain on this row) |
| FL-05 | `board/data/flags.json` | `status` → `resolved 2026-11-19 (T76)`, evidence updated to the built component; `severity` retained at `medium` (the record keeps the fact it was flagged) |

`board/data/measured.json` and `board/**` were regenerated with `tools/build_board.py`.

## 5. Measurements (from the regenerated tree)

- `chooser_pages`: **1 → 3** on the combined tree. The original `1` was a false positive (`intake/tracking.html`,
  a passing phrase). The new component adds `compare.html` (`data-chooser`). The third is `suggestions.html`,
  which mentions "chooser" in the SG-T76-04 proposal merged to `main` this session (decision aids: a chooser and
  trade-off tables) — a legitimate mention, not the component itself. The component is `compare.html`; the count
  is no longer a pure false positive.
- The chooser sits **above** `#compare-list` (section start 7,136 < anchor 10,899 in the built page).
- `compare.html` still has exactly **one** `<h1>` (the validator's one-H1 rule).

## 6. Gates (run on the rebuilt tree)

| Gate | Result |
|---|---|
| `tools/build_front.py --check` | PASS — 15 front pages current |
| `tools/validate_data.py` | PASS — 108 unique row ids, 50 unique source ids, 0 warnings |
| `tools/seo_audit.py` (D1–D8) | PASS — all discoverability checks |
| `tools/audit_site.py` | PASS — fragments, spec_sources, prose_counts, namespaces, disclosure, debris, board |
| `tools/verify_front.py` (G1–G11) | PASS — 16 pages, all checks |
| `tools/package_site.py` + `tools/verify_publication.py` | PASS — 228 HTML pages, 16 indexable, 1,463 product anchors checked, 145 current factual rows |
| `tools/build_board.py --check` | PASS — 9 board pages current |
| `tools/validate_board.py` | PASS — sourcing, blanks, nothing decided, open questions empty, derived counts |
| `tools/ci_replay.py` (standalone, 63 steps) | **PASS** — 63/63 steps |

**Note on the `gates` field in `board/data/measured.json`.** The `gates` string written there reports a
"Decision-board gate" failure. This is a **pre-existing build-ordering race in `build_board.py`'s
`run_gates()`**, not a real gate failure: it runs `ci_replay.py` (which re-runs `validate_board.py`)
against `measured.json` **before** the end-of-run rewrite, so it reads the previous run's stale counts. The
same failing string is present on `main` and on the base commit `0c101a7`. The standalone replay of the
actual gates passes 63/63 on this tree. This is shared tooling out of scope for T76; it is recorded here so
the next session does not chase it.

## 7. Flagged irregularities

- **`gates` field staleness** — pre-existing `run_gates()` ordering race, present on `main`; see §6. Flagged,
  not changed (shared tooling; would affect every session's measured.json).
- **`chooser_pages` false positive** — resolved: the count now includes the real component. The
  `intake/tracking.html` phrase match remains, which is why the count is 2 rather than 1; the component
  itself is the `compare.html` one.
- No product fact, price, rating, conversion figure, intended ASIN or account state was invented or merged.
  The chooser's recommendation is a format pointer + a check reminder, explicitly labelled a starting point.
