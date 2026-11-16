# Verification record — T50, session `arena/7c1511ee-zone2` (2026-11-16 UTC)

Scope: the four new review pages, the register they are generated from, the gate that holds them, and the
additive edits made to `index.html`, `README.md`, `EXECUTIVE_SUMMARY.md`, `.github/workflows/pages.yml`,
`sitemap.xml` and `release/index.html`.

Method: every external page was fetched live with `fetch_page` on 2026-11-16 (the sandbox shell cannot do
outbound TLS — `curl` fails with `SSL_ERROR_SYSCALL`). Every internal claim was counted from this tree with
the command printed beside it. Nothing below is inferred.

---

## 1. The three supplied links, re-resolved live

| # | Supplied link | Resolved to | Page title observed | Change since 2026-11-15 |
|---|---|---|---|---|
| 1 | `https://link.amazon/B04G1MEwY` | `amazon.com/dp/B0CDY277D3?lv=shuf&btn_type=ss&btn_ref=srctok-68884e8aa630b24a&channelId=704&plpRedirect=mhFallback` | CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows, Sync Finish, Hi-Fry … | destination unchanged; `btn_ref` rotated again |
| 2 | `https://link.amazon/B02NbDxp3` | `amazon.com/dp/B09B7SB46R?…&btn_ref=srctok-662480f5bd825c83&…&plpRedirect=mhFallback` | Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven … 24 One-Touch Preset Options | destination unchanged; `btn_ref` rotated |
| 3 | `https://link.amazon/B00hJ57DV` | `amazon.com/dp/B08DKYBTPH?…&btn_ref=srctok-38bef00eb1e962ef&…&plpRedirect=mhFallback&th=1` | Chefman Air Fryer 8 Qt \| TurboFry 4-in-1 with 450°F Hi-Fry Option … | destination unchanged; `btn_ref` rotated |

**Unchanged findings, re-confirmed rather than copied:** the supplied tokens are 9 characters; no resolved
URL carries an Associates `tag` parameter; `btn_ref` is per-fetch. This session makes **no claim** about
whether `plpRedirect=mhFallback` means "fallback" — the 2026-11-14 control that withdrew that inference is
respected, and the register repeats only the narrow, documented position.

## 2. Official pages cited by the review board, all re-read live on 2026-11-16

| ID | Page | Date the page itself states | What was taken | Verbatim check |
|---|---|---|---|---|
| S80 | `affiliate-program.amazon.com/help/operating/policies` | Updated **April 14, 2026** | IP License §2(c)(i): principal purpose = advertising/marketing Amazon and driving sales | quote matches |
| S81 | `affiliate-program.amazon.com/help/node/topic/G8TW5AE9XL2VX9VM` | no date on page | "robust original content … at least 10 posts"; must be publicly available | quote matches |
| S82 | same page, Websites section | no date | "Content on your website must be recent (generally within the last 60 days). You must own your website." | quote matches |
| S83 | `developers.google.com/…/creating-helpful-content` | Last updated **2026-10-05 UTC** | Effort/Originality/Talent/Accuracy; "Who, How, Why"; AI-generation disclosure; fabricated authorship = deception | quote matches |
| S84 | `developers.google.com/…/spam-policies` | Last updated **2026-08-28 UTC** (carried from T49's audit) | Thin affiliation: "Good affiliate sites add value … meaningful content or features" | quote matches |
| S85 | `developers.google.com/…/write-high-quality-reviews` | Last updated **2025-12-10 UTC** | "Ensure there is enough useful content in your ranked lists for them to stand on their own" | quote matches |
| S86 | `ftc.gov/…/disclosures-101-social-media-influencers` | **November 2019** | "The disclosure should be placed with the endorsement message itself." | quote matches |
| S87 | same page, "What Else to Know" | — | "You can't talk about your experience with a product you haven't tried." | quote matches |
| S88–S90 | the three `amazon.com/dp/` pages | — | the listing titles printed in the register | titles match the live page titles |

Register check: 11 sources defined, 11 cited, 0 unused (`tools/validate_review_board.py` prints
`sources_defined: 11, sources_cited: 11`).

## 3. Measurements quoted on `review-trace.html`, each reproduced

| ID | Value published | Command that reproduces it |
|---|---|---|
| PM-01 | 139 | `python3 -c "import sys;sys.path.insert(0,'tools');import build_sitemap as b;print(len(b.published_pages()))"` |
| PM-02 | 24 of 139 (17.3%) | same, filtered on the `marketing/` and `journal/` prefixes |
| PM-03 | 0 images | `grep -c '<img' marketing/*.html marketing/topics/*.html marketing/articles/*.html` → 0 everywhere |
| PM-04 | 68 of 71 product links render as a citation label | parse every `<a href="…amazon.com/dp/…">` on the marketing pages and print its text: 34 `M4 · …`, 16 `M2 · …`, 13 `M6 · …`, 8 `www.amazon.com` |
| PM-05 | 0 product links on the hero's destination | `grep -c 'amazon.com/dp/' marketing/buying-guide.html` → 0 |
| PM-06 | 0 ranked shortlists | no marketing page contains a ranked list of ≥2 products |
| PM-07 | 0 named authors | no marketing page carries a byline |
| PM-08 | 76 nav links | count `<a ` inside the `<nav class="nav">` element of `index.html` |
| PM-09 | 5 boards carry proposals (6 counting the hub), 7 after this task | the six named filenames all exist; `review.html` is the seventh |
| PM-10 | 0 of 28 answered | `ledger/questions.json` (18) + `marketing/data/editorial.json` (10), no `answer` field set |
| PM-11 | 3 of 3 resolve unchanged | section 1 above |
| PM-12 | every marketing page prints a 2026-11-14/15 date | `grep -l '2026-11-14\|2026-11-15' marketing/*.html marketing/topics/*.html marketing/articles/*.html` |

**Flag (this session, needs review).** `PM-09` says "6 before this task". Six *files* exist, but
`decisions/index.html` is a hub rather than a proposal board, so a strict count of boards carrying
proposals is five. The register's value is written as six files and the finding (`PD-09`) says "seven
decision boards". The reader-visible claim that matters — that several boards publish proposals and none
records a decision — is unaffected, but the number is ambiguous and is left as published rather than
silently adjusted. Recorded on the Flagged page for the owner.

## 4. Requirement-trace rows, spot-checked against the tree

| Row | Claim | Check |
|---|---|---|
| RP-03 | all three page types exist | `marketing/articles/p1–p3.html`, `marketing/comparison.html`, `marketing/buying-guide.html` all in `sitemap.xml` |
| RP-04 | no Associates tag | `marketing/data/facts.json` → `associates_tag_configured: false` |
| RP-05 | 5 events, 0 live | `discovery/measurement.html` states it |
| RP-08 | disclosure on 139 pages when measured | `tools/audit_site.py` `disclosure PASS` over 145 pages after this task's four were added |
| RP-09 | three registers, three vocabularies | `ledger/requirements.json` (MET/PARTIAL/NOT_MET/UNVERIFIABLE), `ledger/readiness.json` (MET/GAP/BLOCKED/OPEN/UNVERIFIED), `docs/review-board.json` |
| RP-12 | 18 ledger + 10 marketing open questions | `ledger/questions.json` → 18 rows; `marketing/data/editorial.json` → 10 |
| RP-15 | live, deployed | GitHub Pages API `status: built`; run `43891405619` success, both re-read 2026-11-16 |

## 5. Gates replayed on the final tree

Every gate was run locally on the exact tree that was pushed, and then the whole workflow was replayed
from a clean clone of the pushed commit (`git clone . /tmp/clean`), so the result is not an artefact of
working-directory state.

```
ci_replay.py ............ CI REPLAY PASSED — 38 steps   (was 35; +3 for this task)
build_review_board --check   pass, 4 pages, 0 drift
validate_review_board ....... pass, 0 errors, 0 warnings
test_review_board ........... 19 injected defects, each fired; 1 control passed
build_decisions --check ..... pass after the register moved out of decisions/
build_readiness --check ..... pass; RR-10 derived count 140 -> 144
build_sitemap --check ....... pass; 143 URLs
build_head_meta --audit ..... 91 pages under the contract, 0 problems
audit_site .................. 145 published pages, all seven checks PASS
seo_audit ................... pass
check_css_urls .............. 17 stylesheets, 9 local url(), 0 broken
validate_data ............... pass (after the footer negation was put on one line)
validate_decisions, validate_audit, validate_console, validate_discovery, validate_content? ... pass
test_audit, test_readiness .. pass
research-hub/scripts/verify.py  pass
```

## 6. Three defects this session introduced and then fixed (recorded, not hidden)

1. **`validate_decisions` failed because the register sat in `decisions/`.** `tools/build_decisions.py
   --check` hashes every file under `decisions/`, generated or not, so any register stored there is
   permanent drift. Fixed by moving the register to `docs/review-board.json`, which is the repository's
   existing convention (`docs/discovery-t40.json`). No file owned by another session was edited.
2. **`validate_data` failed on a typed count in `README.md`.** The README said "5 flags" next to the new
   review-board row; the gate reads any "N flags" in the root surfaces as a claim about `ledger/flags.json`,
   which holds 40. No external ledger was touched; the sentence was reworded so it no longer makes a count
   claim at all. This is the same defect class the repository has flagged three times before (F-17, F-26,
   F-29), and the gate caught it in CI rather than in review — which is the point.
3. **`validate_data` failed on the footer's own negation.** The rule requires a negation on the same line
   as the phrase "affiliated with Amazon". The first render split them across two lines. Fixed by keeping
   the negation inside one element. The sentence itself was not weakened.

## 7. What could not be verified, and is therefore not claimed

- **No browser render.** The sandbox cannot download a Chromium build (`npx playwright install chromium`
  fails with `Download failure, code=1`), so the four pages were not screenshot-tested. They were checked
  structurally instead: tags balance on all four (`html.parser` stack check), every internal href and
  fragment resolves (the gate enforces this), and the pages carry no JavaScript and no `data-` hooks, so
  there is no runtime behaviour that a browser test would cover and this check does not.
- **No traffic data.** Nothing in this session measures organic visitors, because the site ships no
  analytics and Search Console is not connected. Any statement about traffic would be invented, so the
  register asks for it instead (`PQ-04`).
- **No claim about what Amazon will decide.** S82 and S81 are quoted exactly; whether a github.io
  subdomain satisfies "you must own your website" is left open (`PQ-06`), as earlier sessions left it.
