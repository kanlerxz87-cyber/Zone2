# Verification record — T58 (session `0f5673ee`, 2026-11-17 UTC)

**Task:** close **CR-1**, the two items `dc72a69e` (T57) explicitly left for the next session:

1. **CR-1 part 1 — derive the two drift-prone counts on the release-readiness board.** RR-01 typed
   "116 published HTML pages"; RR-05 typed "72 pages link to amazon.com/dp/". Both were typed into
   prose, so the tree could grow under them without a gate noticing. They had drifted to **161** and
   **92** respectively (drift of 45 and 20 pages).
2. **CR-1 part 2 — resolve the duplicated suggestion.** `SG-11` and `SG-12` were the same proposal
   twice on the canonical suggestion board.

## What changed (and what did not)

**No verified value changed.** No product attribute, no source quote, no policy claim, no flag, no
commission figure. This is a **code + derived-artifact** fix: the same evidence, rendered so the
counts cannot drift.

| File | Change |
|---|---|
| `tools/build_readiness.py` | Added two measures — `published_html_pages` (counts published HTML pages, excluding the board's own output) and `pages_linking_dp` (counts pages linking to `amazon.com/dp/`). Extended the row model so a row may declare **more than one** measure (a string or a list), so RR-05 can carry both its tagged-link and dp-link counts under one gate. `validate()`, `check_claims()` and `render_rows()` updated accordingly; the existing single-measure rule is unchanged. |
| `tools/test_readiness.py` | Added negative case **R13**: a multi-measure row whose `site_state` names a measure outside its declared list must fire. The existing 13 cases are untouched. |
| `ledger/readiness.json` | RR-01 `site_state` now uses `{published_html_pages}`; added `measure: "published_html_pages"`. RR-05 `site_state` now uses `{pages_with_tagged_link}` and `{pages_linking_dp}`; `measure` is now the list `["pages_with_tagged_link", "pages_linking_dp"]`. |
| `ledger/suggestions.json` | **Deleted the `SG-11` row** (duplicate of `SG-12`). Added a resolution note. The board now carries 11 distinct suggestions (SG-01..SG-10, SG-12). |
| `ledger/products.json`, `ledger/sources.json` | Two **descriptive** mentions of "SG-11" updated to "SG-12" so no canonical register points at a deleted id. No measurement or conclusion changed. |
| Derived artifacts (regenerated through their existing builders, never hand-edited) | `release/index.html`, `pages/suggestions.html`, `pages/products.html`, `pages/sources.html`, `sources.html`, `decisions/*`, `DECISIONS.md`, `console/*` |

## The duplicate resolution, and why SG-12 was kept

`SG-11` and `SG-12` shared an area, a title and near-identical body text. **`SG-12` was kept and
`SG-11` deleted** because `SG-12` is the id the three functional references already use:

- `ledger/questions.json` — `Q-17` `blocks: ["SG-12"]`
- `ledger/readiness.json` — `RR-03` `owner_action` and `RR-09` `owner_action` both name `SG-12`

Deleting `SG-11` therefore leaves every functional reference valid and leaves the documented
"SG-01…SG-12" id range accurate (SG-12 still exists). Renumbering `SG-12 → SG-11` instead would have
churned three functional references and every "SG-01…SG-12" range for no gain. The numbering gap at
`SG-11` is **intentional** and recorded; no row was renumbered.

## Measurements taken from the tree (the fix itself)

These are the values the board now substitutes at render time. They are read from the working tree,
not typed, so a page added by any later session moves them automatically.

| Measure | Value on 2026-11-17 | Was (typed) | Drift |
|---|---|---|---|
| `published_html_pages` (RR-01) | **161** | 116 | +45 |
| `pages_linking_dp` (RR-05) | **92** | 72 | +20 |
| `pages_with_tagged_link` (RR-05) | **0** | 0 | 0 |

The `pages_with_tagged_link` count remains **0**: no page on the site carries an Associates tag in
Amazon's `NAME-NN` format (RR-05 stays **BLOCKED** on `Q-02` — no Associates ID exists). This is the
pre-existing owner blocker, unchanged by this task.

## Sources

No new live source was fetched, because **no verified value changed**. The two counts are measured
from this repository's own tree by `tools/build_readiness.py`. The requirements the rows quote were
already pinned to their official pages and are unchanged:

- **S23** — Amazon Associates Application Review Process
  (`https://affiliate-program.amazon.com/help/node/topic/G8TW5AE9XL2VX9VM`) — the requirement text
  for RR-01 (public availability) and RR-05 (Special Links / tags).
- **S22** — GitHub Pages serving (RR-01).
- **S02 / S24** — Associates Program Policies / ASIN definition (RR-05).

These are the same sources already recorded in `ledger/sources.json`; they were not re-fetched for
this fix because the fix does not touch any claim they support.

## Gates (all green, on the final tree)

- `python3 tools/ci_replay.py` — **43 / 43 steps PASSED** (replays every workflow step in order).
- `python3 tools/build_readiness.py --check` — `release/index.html` current, 12 rows, every one sourced.
- `python3 tools/test_readiness.py` — **14 / 14** negative tests fired (13 existing + new R13);
  control register clean.
- `python3 tools/build_site.py --check` — `pages/` current.
- `python3 tools/build_root_views.py --check` — `sources.html` / `verification.html` current.
- `python3 tools/build_decisions.py` / `--check` — `decisions/` + `DECISIONS.md` current.
- `python3 tools/build_console.py` / `--check` — `console/` current.
- `python3 tools/audit_site.py` — namespaces / disclosure / debris / board all **PASS**.
- `python3 tools/seo_audit.py` — all discoverability checks **PASS**.
- `python3 tools/build_head_meta.py --audit` — 94 pages under the contract, **0 problems**.
- `python3 tools/build_sitemap.py --check` — `sitemap.xml` current (160 URLs).

## Irregularities / follow-ups (non-blocking, recorded not actioned)

1. **The drift that was fixed.** RR-01 and RR-05 had drifted by 45 and 20 pages respectively because
   their counts were typed into prose. This is the defect CR-1 names; it is now closed by derivation.
   The lesson is recorded on the builder: a count that changes whenever a page is added must be a
   `{measure}` token, not a typed number.
2. **FB-03 (brief namespace) is now resolved in fact.** The brief's `brief/data/flags.json` still
   records FB-03 as an open flag describing the SG-11/SG-12 duplicate. The condition no longer exists
   (the duplicate is deleted). `brief/**` is another session's namespace and was **not** edited here;
   the flag record is left as history. Recommendation: the brief namespace's owner marks FB-03 closed
   (non-blocking).
3. **Descriptive "SG-01…SG-12" range prose** in `README.md`, `EXECUTIVE_SUMMARY.md`, `docs/*` and
   `brief/*` still describes the board by its old id range. The canonical register is correct
   (SG-01..SG-10, SG-12). These are descriptive, historical and outside this task's scope; logged for
   the final integration / owner to re-point if desired. Non-blocking.
4. **RR-05 remains BLOCKED** on `Q-02` (no Associates ID / Special Links). Unchanged; the owner action
   stands: supply the Associates ID and marketplace to clear it.
5. **No performance, traffic, click or revenue figure exists or is published** anywhere on the site
   (5 events defined, 0 live). Unchanged by this task.
