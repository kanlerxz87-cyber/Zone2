# Verification record — T72, session `arena/672f9c4c-zone2`

**Date:** 2026-11-19 (UTC)
**Task:** close S-04 / RQ-01, the only P1 requirement row the decision board measured as unfinished —
"give every page its own title and meta description" — and put a gate in front of it.
**Base:** `fc243e0` (`main`, merge of PR #189). **Branch:** `arena/672f9c4c-zone2`.

Every number below was produced by a command run in this working tree on 2026-11-19, or read off the
official page named beside it. No product fact, verified value, price, rating, commission figure,
intent field or campaign row was changed by this session. Blank values stay blank; nothing was inferred.

---

## 1. What was measured before any edit

The measurement uses the same page set and the same two regexes as `tools/build_board.py::measure`,
so the before/after numbers are comparable to the numbers the board publishes.

| Property | Before (2026-11-19, pre-edit) | After | Where it was fixed |
|---|---|---|---|
| Published pages counted | 219 | 219 | — |
| Pages with **no** `<meta name="description">` | **7** | **0** | `404.html`, `revalidation/scripts/build.py` |
| Distinct titles | 215 of 219 | **219 of 219** | `tools/build_site.py`, `tools/build_thermometers.py` |
| Titles shared by 2 pages | **4** | **0** | same |
| Description strings shared by >1 page | **3** (one string × 39 pages, one × 4, and the 7 blanks) | **0** | `tools/build_site.py`, `tools/build_decisions.py` |

The seven blank pages were `404.html` and all six `revalidation/` pages (`index`, `links`, `products`,
`method`, `flagged`, `sources`). The 39-page share was `pages/**`, and the 4-page share was
`decisions/**`; in both cases a single module-level `HUB_DESCRIPTION` string was printed by every call
to the namespace's `render()`.

The four duplicated titles:

| Title as published | Pages |
|---|---|
| `Category band 4.00% · Zone2` | `pages/categories/all-other-categories.html` (C-OTH), `pages/categories/devices-fashion-accessories.html` (C-04) |
| `Category band 0.00% · Zone2` | `pages/categories/coach-exclusion.html` (C-00b), `pages/categories/zero-rate-exclusions.html` (C-00) |
| `Niche discovery · Zone2` | `pages/niches.html`, `pages/modules/m-11-niche-discovery.html` |
| `Meat thermometers · Counter Notes` | `guides/meat-thermometers.html`, `marketing/thermometers/index.html` |

All four are structural, not editorial: two published commission rates are each carried by two bands;
M-11's own name is "Niche discovery"; and the front page's category heading and the marketing desk's
derived title are the same string.

## 2. What changed, and why nothing new is claimed

Not one sentence of new product or editorial copy was introduced. Every replacement description is
composed from two strings the page **already publishes**: its `<h1>` text and its standfirst (`lead`).
The composers are `page_description()` in `tools/build_site.py` and `tools/build_decisions.py`, and an
inline equivalent in `revalidation/scripts/build.py`; each truncates at 160 characters on a word
boundary and appends an ellipsis.

The four title fixes each add a fact already printed on the page:

* `Category band 4.00% (C-OTH)` — the band id is published in that page's own "Band id" row.
* `Niche discovery: method and empty ranking` — the page's own standfirst says the ranking is empty.
* `Meat thermometers, read off the listing` — the desk's own `<h1>` says exactly that.
* `404.html` gained a description stating only what the page is and where to go instead.

## 3. The gate (this is the part that keeps the row closed)

`tools/seo_audit.py` already ran in CI and checked D1–D7 (sitemap coverage and integrity, robots.txt,
robots meta, the marketing sitemap, favicon, canonical). It did not look at titles or descriptions,
which is why the tree could fail all three properties while every build stayed green.

**D8 per-page identity** is added to that gate and fails the build when any published page carries no
description, when two pages share a title, or when two pages share a description. It measures every
published page, including `noindex` archives, because S-04 says "every page".

**Negative controls:** `tests/test_page_identity.py` (8 tests, wired into `.github/workflows/pages.yml`
as a new step). Each of the three pre-T72 defects is injected into a temporary miniature tree and must
fire; the repaired shape must pass; and a blank description must *not* be reported as a duplicate or
vice versa, so a green build cannot come from a check that fired for the wrong reason. The derivation
helpers are also exercised against the lead strings the generators actually pass.

## 4. Sources re-read for this session's changes

| ID | Official page | Read | Used for |
|---|---|---|---|
| S67 | [Google Search Central — title links](https://developers.google.com/search/docs/appearance/title-link) | 2026-11-19 | The standard D8 and flag F-55 are measured against: a result's title link and snippet are generated from the page's own `<title>` and description, so identical boilerplate leaves a page with nothing distinguishing to show. |

**Scope limitation, stated rather than papered over.** This sandbox's outbound network reaches
`github.com`, `codeload.github.com`, `api.github.com`, `registry.npmjs.org`, `pypi.org` and
`files.pythonhosted.org` only. Direct `curl` to `developers.google.com`, `amazon.com` and
`fsis.usda.gov` returns `SSL_ERROR_SYSCALL` (exit 000), and page fetches through the tool layer return a
proxy-network error. S67 is therefore recorded from its stable, long-published URL and scope, and is
**flagged for a live re-read by the next session that has outbound access** rather than presented as a
fresh fetch. No existing source observation was re-dated, and no earlier session's verified value was
altered on the strength of this session's own reading.

## 5. Gates run on this tree

| Gate | Result |
|---|---|
| `python3 tools/ci_replay.py` (the full configured workflow) | **PASSED — 63 steps** (was 62; the D8 negative-control step is the 63rd) |
| `python3 tools/seo_audit.py` | PASS — D1–D8, **226 published pages audited**, 16 sitemap URLs, `D8 … (226/226 described, 226 distinct titles, 226 distinct descriptions)` |
| `python3 tests/test_page_identity.py` | 8/8 pass |
| `python3 tools/validate_data.py` | ok — 0 errors, 55/55 flags, 50 sources, 436 rows, 1315 internal links |
| `python3 tools/audit_site.py` | 7/7 PASS over 228 pages (fragments, spec sources, prose counts, namespaces, disclosure, debris, board) |
| `python3 tools/build_site.py --check` | 39 pages, 0 drift |
| `python3 tools/build_decisions.py --check` | 8 pages, 0 drift, summary fresh |
| `python3 tools/validate_board.py` | all checks pass, 9 pages |
| `python3 tools/build_brief.py --check` / `validate_brief.py` | fresh / pass (the workflow step count derives in the brief and moved 62 → 63) |
| `python3 revalidation/scripts/verify.py` | 6 pages, 73 rows, 168 references, 0 failures |
| `python3 tools/package_site.py` | 228 pages packaged, 16 reader URLs indexable |
| `python3 tools/verify_publication.py` | ok — 228 HTML pages, 16 indexable, 1453 sponsored product anchors, 145 current factual rows |
| Deployed-artifact sweep (this record, §1 re-measured on `_site`) | 16/16 indexable pages carry a description; 0 duplicated titles; 0 duplicated descriptions |

## 6. Irregularities raised

**F-55** (new, published on `flagged.html` / `pages/flags.html` with source S67) records the finding
itself: the brief carried S-04 as "Implemented 2026-11-16" for two days while the tree measured the
opposite, and no build step was checking. It is published rather than silently repaired because the
gap between a status word and a measurement is the reusable lesson — the same failure mode as F-45 (a
local replay printing PASSED while the real runner refused to parse the workflow) and FB-01/FB-02
(prose counts that had drifted from the register they described).

Register counts moved with the row, in one pass, on every surface that publishes them: 54 → **55** flags
(26 open · 29 resolved via `tools/flag_state.py`'s predicate), 49 → **50** sources, and
`CANONICAL_FLAG_COUNT` in `assets/js/data.js`. `validate_data` and `audit_site` both police these and
were run until green.

**Not changed by this session, and still open for the owner:** every item already on the Flagged for
Review page, including F-53 / F-54 (the CHEF iQ battery and warranty conflicts), CR-14 (the
`ledger/products.json` P-05 warranty row), the unclaimed S-20 / RQ-16 mobile-first pass, and the
owner-only gates (authenticated Associates enrollment, the product-intent confirmation fields for all
five supplied links, Search Console, and a permanent first-party collector).

## 7. What this session deliberately did not do

* It did not touch `ledger/products.json`, `shop/**`, `content/publication.json`, or any reader product
  page: no product fact was in scope.
* It did not re-date any earlier session's source observation, and it did not mark S67 as
  re-fetched-live (see §4).
* It did not edit any other session's branch, and it did not resolve CR-14 by choosing between the two
  warranty figures on the listing — that remains an owner decision.
* It did not change the deployment model: `_site` is still the only artifact uploaded, and
  `measurement.json` still ships with collection **off**.
