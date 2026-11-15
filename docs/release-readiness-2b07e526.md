# Release readiness, and the defects found on the way — session `2b07e526` (T43)

Date: 2026-11-15 (UTC) · Branch: `arena/2b07e526-zone2`, based on `main` `bfc240d` · Type: build + review.

This session was asked to review the repository, publish a live site, verify every row against an
official source, and leave anything unverifiable blank and flagged. Most of that already existed. What
did not exist was the one board a person needs before spending an evening on an Amazon Associates
application, and two landing-page defects were live on the public URL while the repository's own
gates reported green. Both are addressed here.

---

## 1. What was built

| Artefact | What it is |
|---|---|
| `ledger/readiness.json` | 12 rows, one per named requirement on Amazon's Application Review Process page (S23), plus the blockers that page creates for this repository |
| `tools/build_readiness.py` | Generator and gate. Renders the board, recomputes every measurable count from the tree, and fails on 14 classes of defect (below) |
| `release/index.html` | The published board, generated from the register |
| `ledger/questions.json` **+Q-17** | "Do you own the website you will declare, and which exact URL will you declare?" — the question RR-02 and RR-12 both hang on |
| `ledger/suggestions.json` **+SG-11** | Close Amazon's "at least 10 posts" content bar *before* applying, not after |
| `tools/audit_site.py` **new check** | `debris`: stray unstyled prose lines, and duplicate links inside a single list |
| `.github/workflows/pages.yml` | One added step: `build_readiness.py --check` |

The board is deliberately not a second suggestions register. It answers a different question: not
"what should we change?" but "against Amazon's published review criteria, where does this actually
stand today, and what is missing?" Its rows cite the same canonical registers rather than restating
them — RR-05 and RR-06 block on **Q-02**, RR-11 on **Q-06 / DS-12**, RR-03 and RR-09 on **SG-11**.

### The 14 defects the gate was proven to catch

Before the gate was trusted, each of these was injected and the gate was required to fail **cleanly**
(exit non-zero, a named row, no traceback). All 14 did:

| # | Injected defect | What the gate reports |
|---|---|---|
| 1 | A row with no source id | `no official source id` |
| 2 | A source id that does not resolve | `source id 'S99' does not resolve` |
| 3 | A non-official source cited | `source S32 is not an official source` |
| 4 | A quote not on S23 as captured | `quote is not present in the S23 text` |
| 5 | `BLOCKED` with no `blocked_by` | `a blocker must name who can clear it` |
| 6 | `BLOCKED` with no owner action | `BLOCKED with no owner_action` |
| 7 | `GAP` with no owner action | `a gap with no next step is not a finding` |
| 8 | A `measure` key that cannot be computed | `unknown measure 'vibes'` |
| 9 | A state outside the closed vocabulary | `'PROBABLY_FINE' is not in the closed vocabulary` |
| 10 | A stated count that disagrees with the tree | `the tree and the register disagree` |
| 11 | Register edited, page not rebuilt | `release/index.html is stale` |
| 12 | A missing disclosure sentence | `missing the disclosure sentence` |
| 13 | A printed product price | `money value … in a buying context` |
| 14 | A broken local link | `internal link does not resolve` |

Two of those (8 and 9) initially crashed the generator instead of reporting a verdict. A traceback
reads like a bug in the tool rather than a finding about the data, so validation was moved ahead of
rendering and both now fail cleanly.

---

## 2. What the board says

4 of 12 rows are met. The eight that are not:

| ID | Requirement (S23) | State | Why |
|---|---|---|---|
| RR-02 | "You must own your website" | UNVERIFIED | S23 states the requirement; it does not define whether a `github.io` address satisfies it. Not answered by assumption — Q-17. |
| RR-03 | "robust original content … a good rule of thumb is at least 10 posts" | GAP | 14 editorial pages counted, but all 14 are specification or comparison surfaces, not articles a reader arrives at from a search. SG-11. |
| RR-05 | Associates tags must be embedded in the product links | BLOCKED | 0 pages carry a tag in Amazon's `NAME-NN` format. 72 pages link to `amazon.com/dp/`, every one an untagged source citation. Q-02 / F-07 / F-24. |
| RR-06 | "at least three [qualifying sales] within the first 180 days" | BLOCKED | An outcome of traffic through a tagged link; cannot exist before RR-05. Q-02. |
| RR-07 | Catalog access needs enrolment + 10 qualifying sales in 30 days | BLOCKED | `tools/amazon_creators_api.py` is written and has never run against the live API. Q-02 / F-05. |
| RR-09 | Applications are rejected for unoriginal or insufficient content | GAP | Same remedy as RR-03. SG-11. |
| RR-11 | The Site list must be current | GAP | 11 published surfaces; which one is the declared Site is recorded nowhere. Q-06 / DS-12. |
| RR-12 | The application must list exact URLs | OPEN | Applying S23's social-network rule to a website is this register's reading, not S23's words — flagged as such. Q-17. |

**The single finding worth acting on:** RR-03 and RR-09 are the only gaps that do not trace back to
the missing Associates account. Everything else on the list is either an owner decision or a
consequence of Q-02. So the content bar is the one piece of work that can be done *now*, without an
account, and `SG-11` is the proposal for it.

---

## 3. Live defects found and repaired

The `EAD` merge debris in `index.html` and `EXECUTIVE_SUMMARY.md` was removed by session `b6defa90`
(T40) while this session was running — independently, from the same observation. Their fix stopped
four lines short of the rest of the damage. What was still live on
`https://kanlerxz87-cyber.github.io/Zone2/` at the start of this session's second pass:

| Defect | Where | Effect on a reader |
|---|---|---|
| A duplicated `Suggestions board` link in one `<ul>` | `index.html` footer | The same link printed twice in a four-item list |
| A second `marketing/index.html` entry labelled **"Field Notes — verified articles"** | `index.html` footer | The same page listed twice under two different names; "Field Notes" is not a brand that exists — the site is called **Counter Notes** |
| The same stale "Field Notes" label | 9 root pages' footers (analysis, compliance, content, design-notes, flagged, playbook, products, tracking) | A name for the marketing site that appears nowhere on it |

Fixed: the duplicate entry removed, and the label refreshed to the published brand across all nine
pages. Reported rather than silently changed, because a rename is a content decision — but "Field
Notes" named nothing, and "Counter Notes" is the masthead of the site it points at.

Worth stating plainly: **the repository's existing gates passed with all of this on `main`.** No
fragment was dead, no count was wrong, the disclosure was present, and every link resolved. A
duplicate `<li>` and a stale label are invisible to a link checker, and so were the three `EAD` lines
that preceded them. That is the gap `check_debris` now closes.

---

## 4. Verification performed in this session (live, 2026-11-15)

Read over the network in this session, not copied from the repository's own registers:

| # | Claim | Result | Source |
|---|---|---|---|
| V-01 | Supplied link 1 destination | `link.amazon/B04G1MEwY` → `amazon.com/dp/B0CDY277D3`, "CHEFMAN 6 Quart Dual Basket Air Fryer Oven…" | https://link.amazon/B04G1MEwY |
| V-02 | Supplied link 2 destination | `link.amazon/B02NbDxp3` → `amazon.com/dp/B09B7SB46R`, "Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven…" | https://link.amazon/B02NbDxp3 |
| V-03 | Supplied link 3 destination | `link.amazon/B00hJ57DV` → `amazon.com/dp/B08DKYBTPH`, "Chefman Air Fryer 8 Qt \| TurboFry® 4-in-1…" | https://link.amazon/B00hJ57DV |
| V-04 | Token rotation / no tag | Each resolved URL carried a fresh `btn_ref=srctok-…` and `plpRedirect=mhFallback`; **no `tag=` parameter on any of the three** | the three links above |
| V-05 | ASIN is a 10-digit code | Verbatim: "**ASIN**: ASIN is the 10-digit code that Amazon uses to denote specific products." Supplied tokens are 9 characters. | https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC |
| V-06 | Disclosure sentence | Verbatim, §5: "You must clearly and prominently state the following … 'As an Amazon Associate I earn from qualifying purchases.'" Page dated October 15, 2025. | https://affiliate-program.amazon.com/help/operating/agreement |
| V-07 | Price display rule | Verbatim: "your Site may only show prices and availability if: (a) we serve the link in which that price and availability data are displayed, or (b) you obtain Product pricing and availability data via Creators API or PA API…" — confirms the repository's blank-price policy is correct, and that a price is *permitted* through those two routes rather than unavailable. | https://affiliate-program.amazon.com/help/operating/policies |
| V-08 | Content bar, ownership, exact URLs, 3-sales rule | Verbatim from the Application Review Process page, quoted in `ledger/readiness.json` → `primary_source_quotes` and rendered on the board. | https://affiliate-program.amazon.com/help/node/topic/G8TW5AE9XL2VX9VM |

V-07 is worth a line on its own. The repository tells readers that price, rating and availability
"could not be confirmed" and are published blank. That is true of the *repository's* state, but the
governing sentence is narrower than the earlier summaries implied: a price is permitted when Amazon
serves it in the link or when it comes from the API under the licence. The distinction does not change
any published cell — all three remain blank — but it changes what the blank *means*, and the board now
says it in Amazon's words.

---

## 5. Gates re-run on this branch (all exit 0)

`validate_data` · `audit_site` (6 checks: fragments, spec sources, prose counts, namespaces,
disclosure, **debris**) · `validate_decisions` · `build_readiness --check` · `build_site --check` ·
`build_root_views --check` · `build_summary --check` · `build_marketing --check` ·
`build_decisions --check` · `tests/test_pipeline.py` 15/15 · `verify_marketing` · `revalidation/verify`
· `affiliate-lab/verify_site` · `research-hub/verify` · `node --check` ×2 ·
`revalidation/build --check` · `research-hub/build` no drift.

Recursive link + disclosure sweep across all **117** published HTML files: **0 problems**.
(`tools/audit_site.py` and CI's root glob both miss subdirectories such as `journal/` and `release/`,
so this was run separately.)

---

## 6. Irregularities and things left for review (non-blocking)

1. **Two sessions fixed the same debris independently** (`b6defa90` / T40 and this one), and a third
   session `bfb20351` took T42 before this session could claim it. My task id went T41 → T42 → **T43**.
   No work was discarded: each collision was resolved by aborting my own history and re-applying only
   my files onto current `main`.
2. **`COORDINATION.md` survives only because every session resolves its conflicts by hand.** It is
   append-only in intent and a conflict magnet in practice; three separate merge attempts in this
   session conflicted on it. A per-session log file would end the class of problem.
3. **RR-02 and RR-12 are unreachable by an agent.** Whether a `github.io` subdomain counts as
   "owning your website" is not answered on any page I could read, and I did not infer it.
4. **The 14 counted editorial posts are not 14 posts by Amazon's bar.** The count is honest and is on
   the board; the judgement of whether they satisfy "robust original content" belongs to a reviewer,
   not to this repository. That is why RR-03 is GAP rather than MET despite the count clearing 10.
5. **No product value was added or changed by this session.** Price, rating, review count,
   availability and commission band remain blank, because no official source states them and the
   Creators API is not reachable without the account (F-05 / Q-02).
