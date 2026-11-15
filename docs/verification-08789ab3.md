# Follow-up record — session `08789ab3` (`arena/08789ab3-zone2`, T41)

Date: 2026-11-15 (UTC). Base: `main` @ `83f52a9` (after PR #91). Type: **verification and disposition only.**
No product value, table row, ledger entry or generated page was changed.

## Relationship to T40

T40 was already merged by session `3db75825` (`docs/review-3db75825.md`, PR #91). This session
claimed a T40 row at the same time, so it is **re-scoped to T41** as a follow-up. It does not repeat
that review. It closes the items that review left open:

| T40 open item (`docs/review-3db75825.md` §5) | Status after this record |
|---|---|
| **I-A** — the 9-character supplied codes vs. the 10-character ASIN rule, "needs an Amazon help-page link" | **Closed** — §1 |
| **I-B** — open PR #70 is CONFLICTING and has no checks; "owner should rebase or close" | **Closed** — §2 |
| I-C — board rows reading "in progress" that have closing records | Not touched here (hygiene; see §4) |
| I-D — `COORDINATION.md` size and renumbering | Not touched here (see §4) |
| I-E — owner-only blockers (F-05, F-07, F-08, F-24) | Unchanged; owner action required (see §4) |

## 1. I-A closed — the ASIN rule, from Amazon's own help page

Re-read on 2026-11-15: https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC

> "ASIN: ASIN is the 10-digit code that Amazon uses to denote specific products."

The same page gives the simple text-link format `http://www.amazon.com/dp/ASIN/ref=nosim?tag=YOURASSOCIATEID`.
The three supplied codes (`B04G1MEwY`, `B02NbDxp3`, `B00hJ57DV`) are **9 characters** each. The
resolved destinations (`B0CDY277D3`, `B09B7SB46R`, `B08DKYBTPH`) are 10 characters each. So the site
may now state the 10-digit rule with an official link. It may not state that a 9-character code "is
an ASIN", because the page defines ASINs as 10 digits.

## 2. I-B closed — PR #70 disposition

PR #70 (`arena/cffe745a-zone2`, "trendy marketing articles for organic traffic") was **closed as
superseded** on 2026-11-15 with an explanatory comment. The branch is kept, so it can be reopened.

Evidence, checked this session:

- Its branch is based on an older `main`. Against current `origin/main`, its diff is 86 files,
  1,366 insertions and 13,760 deletions. The deletions include `tools/build_decisions.py`,
  `tools/build_marketing.py` and `playbook.html`, which are merged work. Merging it would have
  removed that work.
- `mergeable: CONFLICTING`, `mergeStateStatus: DIRTY`, no check runs (per `docs/review-3db75825.md`).
- Its suggestions and Q&A pages duplicate the canonical pages from T29/T30 (PR #61/#64), as its own
  board record states.
- Its trendy-article goal is already covered on `main`: `marketing/articles/p1–p3`,
  `marketing/topics/*` (six guides, T39 / PR #82) and `journal/*` (T33/T38).

Nothing unique to PR #70 was lost. The two extra articles in its diff can be re-proposed from a
fresh branch off current `main`, if the owner wants them.

## 3. Official Associates pages re-read this session

| Claim on the site | Official page | Result |
|---|---|---|
| Table 1: Books/Kitchen/Automotive 4.50%; Home/Toys/… 3.00%; All Other Categories 4.00% | https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ | Matches. Amazon does not state which band the air-fryer listings fall in. That stays an open question. |
| Operating Agreement "Updated: October 15, 2025" | https://affiliate-program.amazon.com/help/operating/agreement | Matches |
| Program Policies "Updated: April 14, 2026" | https://affiliate-program.amazon.com/help/operating/policies | Matches |
| PA-API 5 "has been deprecated and is being replaced by the Creators API"; calls get HTTP 403 | https://affiliate-program.amazon.com/creatorsapi/docs/en-us/paapiv5-deprecation | Matches. The official page states **no shutoff date**. The repository states none either. Third-party pages give conflicting dates; they are not cited. |

## 4. Still open (not closed by this record)

- **Owner-only blockers.** No Associates tracking ID or tag has been supplied (F-07, F-24). No Creators
  API credentials exist (F-05). The links cannot earn commission until the owner supplies these. The
  agent cannot complete them.
- **I-D, board size.** `COORDINATION.md` is about 401 KB. The owner should decide whether to archive
  closed session records. No change is made here.
- **I-C, hygiene.** Board rows still read "in progress" for tasks that have closing records. Editing
  other sessions' rows was out of scope for this record.
- **Branch naming.** The protocol's `session-<id>/<task>` form conflicts with the platform-required
  `arena/<id>-zone2`. Prior sessions recorded the same deviation.

## 5. Gate status on the rebased tree

The 22 CI steps from `.github/workflows/pages.yml` were replayed on `arena/08789ab3-zone2` after it was
rebased onto `main` @ `83f52a9`. Results and any failures are recorded in the closing record on the
board (`COORDINATION.md`, T41 closing record).

## 6. Manual review links

- Amazon ASIN definition: https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC
- Associates Table 1: https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ
- Operating Agreement: https://affiliate-program.amazon.com/help/operating/agreement
- Program Policies: https://affiliate-program.amazon.com/help/operating/policies
- PA-API 5 deprecation notice: https://affiliate-program.amazon.com/creatorsapi/docs/en-us/paapiv5-deprecation
- Supplied links: https://link.amazon/B04G1MEwY · https://link.amazon/B02NbDxp3 · https://link.amazon/B00hJ57DV
- Live site: https://kanlerxz87-cyber.github.io/Zone2/ · Flagged for Review: https://kanlerxz87-cyber.github.io/Zone2/flagged.html
- Closed PR #70: https://github.com/kanlerxz87-cyber/Zone2/pull/70
- Parent review (T40): `docs/review-3db75825.md`
