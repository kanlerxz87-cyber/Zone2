# Verification record — session `08789ab3` (`arena/08789ab3-zone2`, T40)

Date: 2026-11-15 (UTC). Base: `main` @ `ceaf9a7`. Scope: an independent re-verification sweep of
the published Zone2 site and repository, the three supplied `link.amazon` links, the Associates
pages the site cites, and every CI gate. **No product value, table row, or ledger entry was
changed in this session.** Findings are recorded here and on the coordination board; nothing
was silently fixed.

## 1. Gates replayed (identical to `.github/workflows/pages.yml`)

Each of the 22 `run:` steps was extracted from the workflow file and executed in order from the
repository root on the unmodified tree. Exit code 0 means pass.

| # | Step (workflow name) | Result |
|---|---|---|
| 01 | Primary site files exist | pass |
| 02 | Internal links and asset references resolve (all sites) | pass — "All internal links and assets resolve" |
| 03 | Primary dataset is well-formed (`node --check`) | pass — JS syntax OK |
| 04 | Data files parse | pass |
| 05 | No page prints a price and every page discloses | pass — 90 pages |
| 06 | affiliate-lab discloses, links resolve, no product prices | pass — 10 pages |
| 07 | affiliate-lab per-row sourcing verifier | pass — 502 links checked, 0 failures |
| 08 | Rebuild revalidation pages; committed output current | pass — no drift |
| 09 | Research hub: committed output matches generator; verifier | pass — 3 products, 38 sourced attribute rows, 16 requirements, 13 pages, 0 errors |
| 10 | Revalidation gate | pass — 168 references, 0 failures |
| 11 | Rebuild marketing pages; committed output current | pass — 21 outputs current |
| 12 | Marketing gate | pass |
| 13 | Rebuild subpages; committed output current | pass — no drift |
| 14 | Rebuild root evidence views; committed output current | pass — no drift |
| 15 | Subpage gate | pass — no warnings |
| 16 | Platform guard tests | pass — 15/15 |
| 17 | Rebuild executive summary; committed output current | pass — no drift |
| 18 | Structural audit (fragments, spec sources, prose counts, orphans, disclosure) | pass — all checks PASS |
| 19 | Rebuild decision namespace; committed output current | pass — summary not stale |
| 20 | Decision gate | pass — no warnings |
| 21 | Research-hub per-row sourcing guard | pass — 3 products, 38 rows, 16 requirements, 13 pages |
| 22 | Subpages disclose and never print a product price | pass — 39 subpages |

After all 22 steps the working tree was clean: the generators reproduced every committed output
byte for byte.

## 2. Live site

- Landing page fetched from `https://kanlerxz87-cyber.github.io/Zone2/` on 2026-11-15 (first of
  four text chunks read). It renders the three supplied-link rows (code, resolved listing, category
  path, price/rating/availability shown as unverified), the executive-summary block, the
  verified-platform-facts table, and the links to the Suggestions board, Open Questions and Flagged
  for Review register. The three product rows and the Associates facts matched the ledger values.
- Deploy of `main` at `ceaf9a7` (PR #88 merge): workflow run `Build, verify and deploy` = success;
  `pages build and deployment` = success (per `gh run list`).

## 3. The three supplied `link.amazon` links, re-observed live

| Supplied link | Code length | Resolves to (official Amazon listing) | Listing title as shown | Tag present? | Note |
|---|---|---|---|---|---|
| `https://link.amazon/B04G1MEwY` | 9 chars | `https://www.amazon.com/dp/B0CDY277D3` (ASIN 10 chars) | "CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows…" | No Associates tag; URL carries `plpRedirect=mhFallback` | matches site |
| `https://link.amazon/B02NbDxp3` | 9 chars | `https://www.amazon.com/dp/B09B7SB46R` | "Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven…" | No; `plpRedirect=mhFallback` | matches site |
| `https://link.amazon/B00hJ57DV` | 9 chars | `https://www.amazon.com/dp/B08DKYBTPH` | "Chefman Air Fryer 8 Qt \| TurboFry® 4-in-1…" | No; `plpRedirect=mhFallback` | matches site |

Observations, not inferences: the three destinations are the same three ASINs the site already
publishes. The codes are 9 characters. Amazon's Associates help page defines an ASIN as "the 10-digit
code" (re-read 2026-11-15: https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC). The `plpRedirect=mhFallback` marker and the absence
of an Associates `tag` are visible in the URLs. Whether the owner intended these three listings is
a question for the owner (F-01…F-03, owner step, unchanged). Prices and ratings shown on the
listing pages are **not** transcribed anywhere in this repository, by design.

## 4. Official Associates pages re-read this session

| Claim published on the site | Official page re-read | Result |
|---|---|---|
| Table 1: "Physical Books, Kitchen, Automotive — 4.50%"; "Toys, Furniture, Home, Home Improvement… — 3.00%"; "All Other Categories — 4.00%" | https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ | Matches. The air-fryer listings' band is **not** confirmed by Amazon's page and is left as an open question (no inference). |
| Operating Agreement "Updated: October 15, 2025" | https://affiliate-program.amazon.com/help/operating/agreement | Matches |
| Program Policies "Updated: April 14, 2026" | https://affiliate-program.amazon.com/help/operating/policies | Matches |
| Simple text link format `…/dp/ASIN/ref=nosim?tag=…` and ASIN = 10-digit code | https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC | Matches |
| PA-API 5 "deprecated" and "being replaced by the Creators API"; calls receive HTTP 403 | https://affiliate-program.amazon.com/creatorsapi/docs/en-us/paapiv5-deprecation | Matches. The official page gives **no shutoff date**. The repository states no date (grep: none). Third-party pages quote conflicting dates; they are not cited and not used. |

## 5. Irregularities found this session

1. **Open PR #70 (`arena/cffe745a-zone2`) was stale and conflicting.** Opened 11:54:12 UTC; last
   commit `a160442` at 11:55:29 UTC; no later commit before this review. GitHub reported
   `mergeable: CONFLICTING`, `mergeStateStatus: DIRTY`. Against `origin/main` its diff is 86 files,
   1,366 insertions and 13,760 deletions, including `tools/build_decisions.py`,
   `tools/build_marketing.py` and `playbook.html`, which are merged work. Its suggestions and Q&A
   pages duplicate the canonical T29/T30 pages, as its own board record says. Its trendy-article
   goal is already covered on `main` by `marketing/articles/p1–p3`, six `marketing/topics/` guides
   (T39) and the journal (T33/T38). **Resolution:** closed as superseded, not merged, with a comment
   pointing here. The branch is kept, so it can be reopened from a fresh branch off current `main`
   if the owner wants the two extra articles.
2. **Coordination board size and ID reuse.** `COORDINATION.md` is about 401 KB and carries task IDs
   that were reused across sessions (for example T31, T32 and T38 appear more than once in history).
   This session claimed a fresh row (T40) rather than renumbering anyone else's row. **Recommendation
   for the owner:** archive closed session records to `docs/coordination-archive/` in a later
   integration pass. No change made here.
3. **Branch naming.** The coordination protocol names branches `session-<id>/<task>`. This session's
   platform branch is `arena/08789ab3-zone2`, which the platform requires. Prior sessions recorded the
   same deviation; this session keeps it.
4. **Owner-only blocker, unchanged.** No Associates tracking ID or tag has been supplied (F-07). Links
   cannot earn commission until the owner supplies one. This cannot be completed by the agent.

## 6. Not verified in this session (stated, not implied)

- Product prices, ratings, availability and review counts: not published anywhere, by design.
- The manufacturer pages named in the ledger: not re-read in this session.
- The Table 1 band for the air-fryer listings: unconfirmed by Amazon (see §4).
- Every item marked `user` on the Flagged for Review register: unchanged; they depend on the owner.

## 7. Manual review links

- Associates Table 1: https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ
- Operating Agreement: https://affiliate-program.amazon.com/help/operating/agreement
- Program Policies: https://affiliate-program.amazon.com/help/operating/policies
- PA-API 5 deprecation notice: https://affiliate-program.amazon.com/creatorsapi/docs/en-us/paapiv5-deprecation
- Supplied links: https://link.amazon/B04G1MEwY · https://link.amazon/B02NbDxp3 · https://link.amazon/B00hJ57DV
- Live site: https://kanlerxz87-cyber.github.io/Zone2/ · Flagged for Review: https://kanlerxz87-cyber.github.io/Zone2/flagged.html
- Closed PR #70: https://github.com/kanlerxz87-cyber/Zone2/pull/70
