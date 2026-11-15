# Independent verification pass — T31 — session `42fa4918` (2026-11-15)

**Task:** T31 — verification-only re-test of the merged T29 deliverable (Suggestions decision board + Questions register), the combined tree, and the live GitHub Pages deployment. **No shared file was edited by this session** except this report and the session's append-only records in `COORDINATION.md` (plus one mechanical repair, logged as finding F-39 below).

**Method.** Every factual claim carried by `ledger/suggestions.json` (SG-01…SG-10) and `ledger/questions.json` (Q-01…Q-16) was re-checked against the official page it cites, fetched live on 2026-11-15 via `fetch_page`. Rendered pages were compared to the ledgers row by row. Every external link on both pages was matched against `ledger/sources.json`. All repository gates were re-run on the combined tree (`main` = `f30c7aa`, merged into this session's branch). Nothing was inferred; anything not re-verifiable today is stated as such.

---

## 1. Repository gates re-run on the combined tree (2026-11-15)

| Gate | Command | Result | Notes |
|---|---|---|---|
| Generated subpages current | `python3 tools/build_site.py --check` | PASS — `drifted_or_uncommitted: []` | |
| Root evidence views current | `python3 tools/build_root_views.py --check` | PASS — `drifted: []` | |
| Executive summary current | `python3 tools/build_summary.py --check` | PASS — `drifted: []` | |
| Marketing set current | `python3 tools/build_marketing.py --check` | PASS — 9 pages current | |
| Revalidation set current | `python3 revalidation/scripts/build.py --check` | PASS | |
| Data validator | `python3 tools/validate_data.py` | PASS — 0 errors, 0 warnings | 38 canonical flags, 38 unique ids, 37 unique sources, 340 rows, 1,126 internal links checked |
| Platform tests | `python3 tests/test_pipeline.py` | PASS — 15/15 | |
| Structural audit | `python3 tools/audit_site.py` | PASS — **97 published pages**; fragments, spec_sources, prose_counts, namespaces, disclosure all PASS | Count matches T29's record (97). T30's record says 96; discrepancy noted in §7, not a site defect. |
| Research hub rebuild + verify | `research-hub/scripts/build.py` + `git diff` + `verify.py` | PASS — no drift; 3 products, 38 sourced attribute rows, 0 errors | |
| Marketing gate | `marketing/scripts/verify_marketing.py` | PASS — 502 links, 0 failures | |
| Affiliate-lab gate | `affiliate-lab/scripts/verify_site.py` | PASS — disclosure, links, no prices | |

## 2. Claim-by-claim re-verification of the T29 rows (fetched live 2026-11-15)

| # | Claim (T29 row) | What the official page says today | Verdict | Source |
|---|---|---|---|---|
| V-83 | SG-01/Q-02: review requires qualifying sales — "at least three within the first 180 days"; "personal orders do not qualify" | Verbatim on the Application Review Process page | **Verified verbatim** | https://affiliate-program.amazon.com/help/node/topic/G8TW5AE9XL2VX9VM |
| V-84 | SG-01: Special Links must use the assigned Associates ID | Participation Requirements §2(a): "Special Links must use the Associates ID we have assigned to you." | **Verified verbatim** | https://affiliate-program.amazon.com/help/operating/policies |
| V-85 | Q-02/Q-04 (S23): "You must own your website"; content "generally within the last 60 days"; "at least 10 posts" | Websites section: "Content on your website must be recent (generally within the last 60 days). You must own your website." Sites: "a good rule of thumb is at least 10 posts." | **Verified verbatim** | https://affiliate-program.amazon.com/help/node/topic/G8TW5AE9XL2VX9VM |
| V-86 | Q-14: tax-interview help topic exists and is reachable from the review-process page | Sidebar of the page links "How do I complete the Tax Interview?" | **Verified** | https://affiliate-program.amazon.com/help/node/topic/G8TW5AE9XL2VX9VM |
| V-87 | Q-14/SG-08: commission paid ~60 days after month end | Commission Income Statement §6: "We will pay Standard Commission Income and Special Commission Income in the default currency for an Amazon Site approximately 60 days following the end of each calendar month in which they were earned" | **Verified verbatim** | https://affiliate-program.amazon.com/help/operating/policies |
| V-88 | SG-07/Q-12/Q-13: Creators API eligibility — "at least 10 qualifying sales within the past 30 days"; SearchItems/GetItems exist | Creators API introduction, Prerequisites §2 verbatim; API Operations table lists SearchItems and GetItems | **Verified verbatim** | https://affiliate-program.amazon.com/creatorsapi/docs/en-us/introduction |
| V-89 | Q-03 (S24): "An ASIN is a 10-character code" | Help topic: "ASIN is the 10-digit code that Amazon uses to denote specific products." (The page's own example `B000IB9QXI` contains letters, so the ledger's "10-character" is the accurate paraphrase of the page's loose "10-digit".) | **Verified** (faithful paraphrase; wording difference noted) | https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC |
| V-90 | Q-03/S32: unknown code control — a bogus code returns 404 | `https://link.amazon/B00TEST12` → "404: File Not Found — You've clicked on an invalid URL." (served via amzlinks.in) | **Reproduced today** | https://link.amazon/B00TEST12 |
| V-91 | SG-02/Q-05/Q-08: supplied link 1 → B0CDY277D3, "CHEFMAN 6 Quart Dual Basket Air Fryer Oven…", breadcrumb Home & Kitchen › Kitchen & Dining › Small Appliances › Fryers › Air Fryers, `plpRedirect=mhFallback`, rotating `btn_ref` | Reproduced live; page title and breadcrumb match S19 exactly | **Reproduced today** | https://link.amazon/B04G1MEwY → https://www.amazon.com/dp/B0CDY277D3 |
| V-92 | SG-02/Q-05/Q-08: supplied link 2 → B09B7SB46R, "Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven…" | Reproduced live; title and breadcrumb match S20 | **Reproduced today** | https://link.amazon/B02NbDxp3 → https://www.amazon.com/dp/B09B7SB46R |
| V-93 | SG-02/Q-05/Q-08: supplied link 3 → B08DKYBTPH, "Chefman Air Fryer 8 Qt \| TurboFry® 4-in-1…" | Reproduced live; title and breadcrumb match S21 | **Reproduced today** | https://link.amazon/B00hJ57DV → https://www.amazon.com/dp/B08DKYBTPH |
| V-94 | SG-03/Q-09: §6(y) — no price tracking/alerting unless Amazon agrees otherwise | "Unless otherwise agreed by Amazon, your Site must not have price tracking and/or price alerting functionality." | **Verified verbatim** (closes the gap T29's V-7 left open) | https://affiliate-program.amazon.com/help/operating/policies |
| V-95 | SG-07/Q-12: §6(t) — reviews/stars only via Creators API or PA API | "You will not display or otherwise use any of our customer reviews or star ratings … unless you have obtained a link to that customer review or star rating through Creators API or PA API…" | **Verified verbatim** (closes V-7 gap) | https://affiliate-program.amazon.com/help/operating/policies |
| V-96 | Q-10: §6(z) — Program Content never promotes non-Amazon retailers; Excluded Products data may not be used | Both sentences of §6(z) confirmed verbatim | **Verified verbatim** | https://affiliate-program.amazon.com/help/operating/policies |
| V-97 | R-04 basis (price/availability display conditions) | Participation Requirements §2(b): "your Site may only show prices and availability if: (a) we serve the link in which that price and availability data are displayed, or (b) you obtain Product pricing and availability data via Creators API or PA API…" | **Verified verbatim** | https://affiliate-program.amazon.com/help/operating/policies |
| V-98 | R-06/R-21 basis (no misleading claims; remove expired promotions) | §2(b): "You must not make inaccurate, overbroad, deceptive or otherwise misleading claims about any Product, an Amazon Site, or any of our policies, promotions, or prices." + the limited-time-promotion removal sentence | **Verified verbatim** | https://affiliate-program.amazon.com/help/operating/policies |
| V-99 | R-08 basis (sub-tags never tied to a user) | §2(b): "Under no circumstances may you associate any sub-tag, other ID or reporting … with a specific end user of your Site (e.g., you may not dynamically assign sub-tags to users as they arrive on your Site…)" | **Verified verbatim** | https://affiliate-program.amazon.com/help/operating/policies |
| V-100 | SG-08/Q-08 (S04): Table 1 — Kitchen 4.50%, Home 3.00%, All Other Categories 4.00% | Table 1 rows read verbatim: "Physical Books, Kitchen, Automotive — 4.50%"; "Toys, Furniture, Home, … — 3.00%"; "All Other Categories — 4.00%" (closes the gap T29's V-8 left open) | **Verified verbatim** | https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ |
| V-101 | Q-08 stance: the breadcrumb does not name a Table 1 band, so no rate is asserted | Correct: Table 1 has separate "Kitchen" and "Home" bands; the destination breadcrumb "Home & Kitchen › Kitchen & Dining › …" names neither band unambiguously | **Confirmed (correctly left unconfirmed)** | https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ |
| V-102 | Q-15/R-01: disclosure sentence + "substantially similar statement previously allowed" | Operating Agreement §5 verbatim: "You must clearly and prominently state the following, or any substantially similar statement previously allowed under this Agreement …: 'As an Amazon Associate I earn from qualifying purchases.'" | **Verified verbatim** | https://affiliate-program.amazon.com/help/operating/agreement |
| V-103 | SG-08/R-19: commission never guaranteed | Operating Agreement §4: "We do not make any representation, warranty, or covenant regarding the amount of traffic or commission income you can expect at any time…" | **Verified verbatim** | https://affiliate-program.amazon.com/help/operating/agreement |
| V-104 | Q-01: Associates country selector lists Japan | The country selector on the Associates pages lists Japan (observed on every page fetched in this session) | **Reproduced today** | https://affiliate-program.amazon.com/help/operating/agreement (selector present site-wide) |
| V-105 | Q-16/SG-06 (S10, FTC): material connections disclosed clearly | FTC Endorsement Guides: "…that connection should be disclosed clearly and conspicuously." | **Verified verbatim** | https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking |
| V-106 | SG-09 (S09): Associates reports/SiteStripe are official tools | Tools overview page shows SiteStripe ("View Earnings Summary"), Product Links, Banners, and a Reports section link | **Verified** | https://affiliate-program.amazon.com/welcome/topic/tools |
| V-107 | SG-10 (S22): the live site is served by GitHub Pages | Pages API: `build_type: legacy`, source `main` `/`, `status: built`, https://kanlerxz87-cyber.github.io/Zone2/ | **Verified** (live) | https://docs.github.com/en/rest/pages/pages + Pages API |
| V-108 | Q-01/Q-02: version dates of the two core documents | OA "Updated: October 15, 2025"; Program Policies "Updated: April 14, 2026" | **Verified verbatim** | https://affiliate-program.amazon.com/help/operating/agreement · https://affiliate-program.amazon.com/help/operating/policies |

**Result: every factual claim in the 26 T29 rows is verified against its cited official source. No claim required blanking; no new factual defect was found in the T29 ledgers.**

## 3. Rendered pages vs ledgers (row-by-row)

| Check | Result |
|---|---|
| All 10 suggestion rows (SG-01…SG-10) render on `pages/suggestions.html` with id, title, all options, recommendation, needs-answers links | PASS (SG-08's apostrophe is HTML-escaped `&#x27;` — correct rendering, not a mismatch) |
| All 16 question rows (Q-01…Q-16) render on `pages/questions.html` with verified-now / missing / how-to-close / blocks / sources | PASS |
| All 24 unique external hrefs across the two pages are registered in `ledger/sources.json` | PASS — no invented or unregistered links |
| Decision state | Every row renders "awaiting owner decision" with empty `decision` — nothing is implemented without a recorded choice, as designed |

## 4. Live deployment confirmation (2026-11-15)

| Check | Result |
|---|---|
| Pages API (after PR #66) | `status: built`, commit `f30c7aa`, source `main` `/` |
| Live `pages/suggestions.html` | Serves the decision board: 10 suggestions, options A/B/C, recommendations, per-row source links, flag count 38 |
| Live `pages/questions.html` | Serves the register: 16 questions with verified-now/missing/how-to-close, per-row source links |
| Root dashboard (post-T30) | `index.html` links the two canonical pages (nav + callout); verified in tree and served live |

## 5. Open-PR status audit (as of 2026-11-15 ~11:50 UTC)

| PR | Session | Scope | Status during this audit |
|---|---|---|---|
| #62 (T30 draft) | fb49a226 | root `index.html` + draft suggestions page | **Closed unmerged** at 11:45:15Z by its own session, superseded by #64 — consistent with its coordination record |
| #64 + #66 (T30 final) | fb49a226 | root `index.html` integration + closing record | **Merged** (`f9a86bd`, `f30c7aa`); Pages deploy confirmed |
| #65 | bf8f07a7 | `marketing/trending-topics.html` (new), `marketing/index.html` nav, `COORDINATION.md` | **Open** (created 11:46:48Z). Audited: the session dropped its earlier root-level `suggestions.html`/`decisions.html` duplicates and now ships a labelled editorial-ideas layer; its record cites the same official sources verified in §2 above; no factual claim in its diff contradicts the ledgers; file scope does not overlap T31. Left untouched — fresh claim by an active session. |

## 6. Findings and irregularities (flagged for review; nothing blocking)

1. **F-39 — pre-existing unresolved conflict debris in `COORDINATION.md` on `main`.** The file carried a stray `=======` line, a stray `>>>>>>> origin/main` line, and a duplicated fragment (a second "## T26 — closing record" heading mixed with later-session board rows and a process note) between them. Present at this session's branch base `e030c40` (PR #60 lineage) and carried through PRs #61/#64/#66 — i.e., not introduced by T29/T30. During this session's required conflict resolution the **two stray marker lines were removed** (mechanical repair; recorded as a scope amendment in `COORDINATION.md`). **The duplicated fragment was left byte-identical for owner review** — owner action: deduplicate the T26-area fragment or confirm which copy is canonical. Until then the board renders one heading-twice anomaly in that area.
2. **Page-count note.** T29's record counts 97 audited pages, T30's says 96, this session measures **97** on `main` = `f30c7aa` (and 97 on the combined tree). The 96 likely reflects a tree snapshot taken before/while PR #61 was merging. Record-keeping note only; all gates passed on each session's own tree.
3. **CR-3 (change request).** The executive summaries (`EXECUTIVE_SUMMARY.md`, `docs/executive-summary.md`, `summary.html`) are current through F-38 but predate the T29/T30 surfaces: they do not yet mention the Suggestions decision board or the Questions register. Owner/next session: add a short subsection pointing to `pages/suggestions.html` and `pages/questions.html`. Not edited here (shared output owned by earlier sessions).
4. **Carried forward, unchanged** (already on the Flagged for Review page): the generator eyebrow reads "verified 2026-11-14" while these pages were checked 2026-11-15 (recorded by T29); the stale `in progress` T27 board row (flagged by `2499438c`); F-01/F-03 (ASINs unconfirmed), F-07/F-24 (no Associates tag on the supplied links), F-05 (Creators API registration).

## 7. Evidence read for Q-10 (IP License) — recorded for the owner, not written into the register

Q-10 ("May the site use Amazon product images and descriptions?") says the agent should read S30 in full. This session read the IP License section of the official policies page and records the operative clauses (the register itself remains untouched; the owner decides):

- License §1 grants a "limited, revocable, non-transferable, non-sublicensable, non-exclusive, royalty-free license" to "(a) copy and display Program Content solely on your Site; (b) use only those of the Amazon Marks … solely on your Site and in accordance with the Trademark Guidelines; and (c) access and use Creators API, PA API, Data Feeds, and Product Advertising Content solely in accordance with the Specifications and this License."
- Use must "solely … send end users and sales to an Amazon Site"; each use must link "solely to the related Product detail page or other relevant page of an Amazon Site."
- §2(h): images may not be stored/cached (only a link to image content, up to 24 hours); other content may cache ≤ 24 h and must be refreshed.
- §2(i): pricing/availability displays require a date/time stamp and the mandatory "Product prices and availability are accurate as of the date/time indicated…" disclaimer.
- §2(k): applications displaying text PAC must show the "CERTAIN CONTENT THAT APPEARS … COMES FROM AMAZON…" disclaimer.
- Trademark Guidelines: Amazon Marks only to advertise availability with a Special Link, unaltered, standalone.
- §4 Agent Terms: any software acting autonomously must identify itself in the user-agent string ("Agent/[agent name]"), must not mimic human behaviour or circumvent CAPTCHAs — directly relevant to this project's automation layer.
- Practical consequence for this repo: without Creators API/PA API access (which requires the 10-qualifying-sales threshold, V-88), the site has no authorised programmatic way to fetch fresh product images or prices — consistent with the site's current no-price/no-image design and R-04.

Source: https://affiliate-program.amazon.com/help/operating/policies#Associates%20Program%20IP%20License (fetched 2026-11-15, chunks 6–9).

## 8. Verdict

The merged T29 deliverable is **verified line by line** against official sources; the combined tree passes **every repository gate**; the live site serves the decision board and questions register **with per-row source links**. Two bookkeeping items (F-39 debris, page-count note) and one completeness gap (CR-3) are flagged for review; none blocks the site.

---

## 9. Addendum — final combined tree at PR time (recorded 2026-11-15, after PR #69 merged)

While this session worked, `main` advanced once more: **PR #69** (`arena/d0135100-zone2`, session `d0135100`, merged 11:53:17Z) added `ledger/requirements.json` (24 requirements), a `decisions/` namespace with its own gate pair (`tools/build_decisions.py --check`, `tools/validate_decisions.py`), `DECISIONS.md`, and the RF-01…RF-03 findings. That session had also claimed T29, and its record on `main` documents the deduplication: the canonical suggestions/questions ledgers written by `2499438c` were **kept untouched** — `d0135100`'s own copies were deleted, and its tooling now *reads* the canonical registers.

Consequences verified on the final combined tree (`main` = `5caf097` + this session's commits merged in):

| Check | Result |
|---|---|
| Canonical T29 ledgers unchanged by PR #69 | Confirmed — the 26 rows verified in §2 above are still the live data (`validate_decisions` re-reads them: 10 suggestions, 16 open questions) |
| New decisions gates on the combined tree | PASS — `build_decisions --check` (8 built, no drift); `validate_decisions` (0 errors: 24 requirements, 10 suggestions awaiting, 16 questions open, 3 findings, 28 distinct sources cited) |
| Full audit on the combined tree | `tools/audit_site.py`: **101 published pages** (97 + the 4 `decisions/` pages), all classes PASS |
| Remaining drift gates re-run | `build_site --check`, `build_root_views --check`, `build_summary --check`, `test_pipeline.py` 15/15 — all PASS |
| Flag-id collision avoided | `d0135100` reserved **F-39…F-41** for its RF findings (CR-6); this session's debris finding is therefore numbered **F-42**, and `ledger/flags.json` still holds F-01…F-38 until a flag-register owner lands either set |

The finding numbering in §6 applies as amended: **F-42** = pre-existing `COORDINATION.md` conflict debris (markers removed this session; duplicated fragment left for owner review), **CR-9** = executive-summary completeness gap.
