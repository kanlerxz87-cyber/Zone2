# Verification record — session `dc72a69e` (T57, renumbered from T50 — design brief)

**Date:** 2026-11-16 (UTC) · **Branch:** `arena/dc72a69e-zone2` · **Base commit:** `004a040`
(merge of PR #130), **rebased onto `main` at `18e8de8`** before the pull request · **Scope:** the
`brief/` namespace, `tools/build_brief.py`, `tools/validate_brief.py`, `tools/test_brief.py`, additive
links and additive CI steps.

> **Re-measured after a parallel session landed.** While this session was in flight, session
> `arena/9251f262-zone2` (**T55**, PR #144) rebuilt the front pages as a publication and added the
> `guides/` namespace. Every count in this record was taken again on the combined tree. Three things
> changed: the landing-page overclaim this session had flagged (**FB-05**) was removed by that rebuild and
> is recorded as **closed** rather than deleted; the page-count drift this session flagged (**FB-01**)
> widened from 22 pages to 34; and self-referential copy fell from 8% of sentences to 4%. Nothing in this
> record describes the tree as it was before that rebase without saying so.

Everything below was measured in this working tree or read from a page fetched on
2026-11-16. Nothing is carried from another session's prose except where a row says so
explicitly.

## Channel

The sandbox shell cannot reach the network: `curl` fails with `SSL_ERROR_SYSCALL`. Every
live check used `fetch_page`; repository and deployment facts used the GitHub API (`gh`).
No row in this record rests on the shell's outbound network.

## 1. Live re-verification of the three supplied links

| Supplied link | Resolved destination (2026-11-16) | Matches the ledger |
|---|---|---|
| `https://link.amazon/B04G1MEwY` | `www.amazon.com/dp/B0CDY277D3` — "CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows…" | yes |
| `https://link.amazon/B02NbDxp3` | `www.amazon.com/dp/B09B7SB46R` — "Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven…" | yes |
| `https://link.amazon/B00hJ57DV` | `www.amazon.com/dp/B08DKYBTPH` — "Chefman Air Fryer 8 Qt \| TurboFry® 4-in-1 with 450°F Hi-Fry Option…" | yes |

All three breadcrumb to Home & Kitchen › Kitchen & Dining › Small Appliances › Fryers ›
Air Fryers, and none carries an Associates `tag` parameter. The third listing's title
prints 450°F for the Hi-Fry option, which is the conflict already carried as F-22; this
session observed the title text and restates no specification from it.

## 2. Official sources fetched and quoted

22 source rows (BR-01…BR-22) are published at `brief/sources.html`. 21 were fetched live
on 2026-11-16; one (BR-22, the manufacturer pages) is marked `carried` because this
session did not re-fetch it.

| Source | Datestamp read from the page | Quote verified verbatim |
|---|---|---|
| Associates Program Policies | Updated: April 14, 2026 | §6(t), §6(y), §6(g), §6(v)/(w) |
| Operating Agreement | Updated: October 15, 2025 | §5, §4 |
| Application Review Process | (none printed) | three-sales threshold; content bar; recency and ownership; Special Link tag format |
| Google spam policies | Last updated 2026-08-28 UTC | scaled content abuse; thin affiliation |
| Google generative-AI guidance | Last updated 2026-10-01 UTC | scaled-content-abuse sentence |
| Google helpful content | (not captured) | trending-topic warning; spread-across-sites warning; first-hand expertise |
| FTC Disclosures 101 | November 2019 | placement; claims requiring proof |

## 3. Measurements taken on the tree

| Measure | Value |
|---|---|
| HTML files in the tree | 162 (2 are error documents) |
| Published pages, excluding error documents | 160 |
| Published pages excluding `release/index.html` and `brief/**` (the measured set) | 150 |
| Of those, carrying the exact §5 disclosure sentence | 150 |
| Of those, carrying an Associates tag in `NAME-NN` format | 0 |
| Of those, printing a product price | 0 |
| Of those, carrying the phrase "AI-powered" | 14 (25 occurrences; 11 carry the full phrase; **none reader-facing** after T55) |
| Pages carrying the phrase "AI-powered" that a visitor from search could land on | 0 |
| Sentences across the seven root pages with the site as their subject | 12 of 299, 4% (was 8% before T55) |
| Pages linking to `amazon.com/dp/` | 87 (the readiness board says 72) |
| Separate published surfaces | 16 (15 excluding this namespace) |
| Pages without a self-referencing canonical | 43, all in companion namespaces |
| Workflow steps replayed locally on the combined tree | 43 of 43, plus 15 of 15 pipeline tests |

## 4. Irregularities this session raised (FB-01…FB-08)

Published at `brief/flagged.html`. Two of them are the same defect class twice:

- **FB-01** — readiness row RR-01 prints "116 published HTML pages"; the tree measures 150 (159
  counting this namespace). RR-01 has no `{measure}` token. The drift has grown with every namespace
  another session adds, which is the argument for deriving it.
- **FB-02** — readiness row RR-05 prints "72 pages link to amazon.com/dp/"; measured 87. RR-05 has a
  token for its headline count but a typed supporting sentence.

Both are logged as change request CR-1 rather than fixed, because `ledger/readiness.json`
and `tools/build_readiness.py` are outside this session's claimed scope.

The other six: FB-03 (SG-11 and SG-12 are the same proposal twice on the canonical board),
FB-04 ("AI-powered" on 14 operator and companion pages — T55 cleared every reader-facing page, so
this is now a cleanup rather than a public-facing defect), **FB-05 — closed by T55** (the landing
page's "Three listings identified" contradicted F-03; that session's rebuild removed the heading and
this session verified the string is absent after the rebase), FB-06 (zero tagged links — high
severity, owner action), FB-07 (43 companion pages without a canonical — an open owner decision,
carried as MQ-08 / DS-12), FB-08 (manufacturer pages not re-fetched by this session).

## 5. The gate, and its negative tests

`tools/validate_brief.py` enforces: referential integrity of every source id; a row is a
measurement (with a method), an official or observed claim (with a source), or a carried
row (saying what it carries); open questions stay empty; the executive summary's measured
counts are re-derived from the tree at gate time; board integrity; the disclosure; a
canonical; no money figure; and no broken local link or dangling same-page anchor.

`tools/test_brief.py` injects twelve defects — unknown source id, filled-in open answer,
row without a method, carried row that quotes, stale typed count, choice outside the
options, recommendation naming no option, blocker that is not a proposal, result with
nothing observed, page without the disclosure, money figure, and the clean register — and
asserts each fires. **Result: 12 of 12 fire, and the clean register is clean.**

Why the derived-counts rule is in the gate at all: FB-01 and FB-02 are two rows whose
typed numbers the tree outgrew with no gate noticing. The executive summary in this
namespace cannot do that, because the gate recomputes the four counts it prints.

## 6. Defects the repository's existing gates caught in this session's work

Recorded because they are the checks that earned their place:

1. `tools/build_sitemap.py --check` — sitemap drifted (139 committed URLs vs 148 derived).
   Fixed by regenerating; `sitemap.xml` is never hand-edited.
2. `tools/audit_site.py` — two cross-page fragments addressing nothing
   (`suggestions.html#FB-06`, `suggestions.html#BQ-15`), produced because two open
   questions listed a flag id and a question id in their `blocks` field instead of a
   proposal id. Fixed in the data, and a rule was added to `tools/validate_brief.py` so
   it cannot recur.
3. `tools/seo_audit.py` — nine `brief/` pages absent from the sitemap. Fixed by
   regenerating.
4. `tools/build_readiness.py --check` — `release/index.html` went stale when this
   namespace added pages, because two of its measures count every published page.
   Regenerated. **No ledger data was changed.** Recorded as a scope extension in
   COORDINATION.md: the file is a derived artifact, and leaving it stale would have failed
   the deploy gate.

5. **`tools/build_front.py --check` (T55's gate) — `index.html` went stale.** This session had
   added its links to `index.html` by hand, and T55's generator owns that file: it rebuilds the page
   from a hardcoded navigation list. Two constraints collided — `tools/audit_site.py` fails a
   published namespace that nothing links to, and the only page that could carry the link is
   generated by another session's tool. Resolved with the smallest possible change: one entry added
   to the navigation list in `tools/build_front.py`, nothing else in that generator touched, and the
   page regenerated by its own builder. Logged as a scope extension in COORDINATION.md.

## 7. Steps run green before the pull request

`tools/ci_replay.py` replays all 38 workflow steps locally in order: **38 of 38 pass**.
Additionally run green: `build_brief`, `validate_brief`, `test_brief`,
`build_site`, `build_root_views`, `build_summary`, `build_sitemap`, `build_decisions`,
`build_audit`, `build_console`, `build_marketing`, `build_readiness`,
`build_head_meta --audit` (87 pages, 0 problems), `validate_data`, `validate_decisions`,
`validate_audit`, `validate_console`, `validate_discovery`, `audit_site` (150 pages),
`seo_audit` (148 URLs), `check_css_urls`, `test_readiness`, `test_audit`,
`tests/test_pipeline.py` (15 of 15).

## 8. Deployment

Recorded after the merge — see section 9 of the session record in COORDINATION.md and
the `VF-36` row on `brief/verification.html`.
