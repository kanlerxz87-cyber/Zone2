# T41 — Discoverability repair, line-by-line verification record

**Session:** `arena/156aae86-zone2` (session `156aae86`)
**Date:** 2026-11-15 (UTC)
**Base commit:** `83f52a9` (`origin/main`, after PR #89 font repair and PR #91 T40 review)
**Scope:** root `sitemap.xml`, two new tools, one CI step, a mechanical favicon `<link>` on the root pages,
the merge-corruption repair described in §3, and this record. No product fact, identity mapping, price,
rating or commission rate was added, changed or inferred.

Every claim below is a measurement with the command that reproduces it, or a quotation from an official
source with its link. Where something could not be confirmed, it is blank and listed in §7.

---

## 1. Repo state on arrival (before any edit)

All commands run from the repository root. Gates were run first so that anything failing afterwards is
attributable to this session.

| # | Gate | Command | Result |
|---|---|---|---|
| 1 | Generated subpages current | `python3 tools/build_site.py --check` | `{"built": 39, "drifted_or_uncommitted": []}` |
| 2 | Root evidence views current | `python3 tools/build_root_views.py --check` | `"drifted": []` |
| 3 | Executive summary current | `python3 tools/build_summary.py --check` | `{"drifted": [], "summary_stale": false}` |
| 4 | Marketing set current | `python3 tools/build_marketing.py --check` | `21 outputs … current` |
| 5 | Decision namespace current | `python3 tools/build_decisions.py --check` | `"drifted": []` |
| 6 | Subpage gate | `python3 tools/validate_data.py` | `0 errors / 0 warnings` |
| 7 | Decision gate | `python3 tools/validate_decisions.py` | `0 errors / 0 warnings` |
| 8 | Structural audit | `python3 tools/audit_site.py` | `116 published pages … 5/5 PASS` |
| 9 | Marketing gate | `python3 marketing/scripts/verify_marketing.py` | `OK 18 pages · 48 spec rows · 0 failures` |
| 10 | Platform tests | `python3 tests/test_pipeline.py` | `15/15 checks passed` |
| 11 | JS syntax | `node --check assets/js/{app,data}.js` | exit 0 |

Internal link check over every HTML file in the tree: **116 pages, 0 broken local references.**
`gh pr list --state open` at claim time: **#90** (verification-only) and **#70** (`CONFLICTING`,
generated `marketing/**`). `gh issue list --state open`: none. Neither open PR touches T41's scope.

---

## 2. Finding T41-D1 — the root sitemap listed 16 of 115 published pages

This is the load-bearing finding of the task. It was measured, not inferred.

```
$ python3 - <<'PY'
import re, glob
sitemap = len(re.findall(r'<url>', open('sitemap.xml').read()))   # 16
pages   = [f for f in glob.glob('**/*.html', recursive=True)]     # minus 404.html
PY
```

| Measurement | Value | How it was taken |
|---|---|---|
| `<loc>` entries in committed `sitemap.xml` | **16** | `grep -c '<url>' sitemap.xml` |
| Published HTML pages in the tree | **115** | every `*.html` excluding `404.html`; GitHub Pages serves the tree verbatim |
| Absent from the sitemap | **99 (86%)** | set difference |
| Complaint-free CI | yes | no CI step referenced `sitemap.xml` — `grep -rn "sitemap.xml" tools/*.py .github/workflows/pages.yml` matched only `tools/build_marketing.py`, which serves `marketing/sitemap.xml` |

**Pages a crawler needs first, and their status before this session:**

| Page | In sitemap before? | Why it matters |
|---|---|---|
| `marketing/index.html` | **No** | the reader-facing publication (18 pages, the organic-traffic surface) |
| `playbook.html` | **No** | the design/content playbook (46 KB, published page) |
| `pages/index.html` | Yes | the findings hub |
| all 38 other `pages/*.html` | **No** | the findings and evidence tables |
| all 18 `marketing/**` | **No** | the publication and its topic guides |
| `journal/index.html` | Yes | the three journal articles were listed; the hub was, by luck |
| `research-hub/`, `zone2/`, `affiliate-lab/`, `revalidation/`, `decisions/`, `northstar/` (42 pages) | **No** | companion namespaces, all reachable from the landing page |

**Root cause.** The file was hand-typed and nothing regenerated it. The repository already had the
mirror-image control for *links* (`tools/audit_site.py::check_namespaces` proves every namespace is
reachable **by a link**), but nothing proved any page was reachable **by a crawler**. A hand-typed list
with no gate is a claim about the site that stops being true silently — the same failure mode every
other gate here exists to prevent.

**Why this is the right thing to fix for the owner's stated goal.** The brief asks for a site that can
"generate organic traffic to the website so real people can click the links and buy." A page absent
from a submitted sitemap is not invisible — crawlers discover links — but it is undiscoverable by the
one mechanism that tells a search engine the page exists and is wanted. Publishing a 115-page site while
advertising 16 is spending the content and discarding the distribution.

**Fix.** `tools/build_sitemap.py` derives the file from the tree; committed output is now **115 URLs**
and CI fails on drift.

---

## 3. Finding T41-D2 — merge-conflict residue rendered as visible text on the live landing page

Found while auditing `index.html` for the favicon change. **This was live on the deployed site**, not a
local artifact.

| Evidence | Detail |
|---|---|
| Source on `origin/main` | `git show origin/main:index.html` → line 258 `EAD`, line 270 `EAD`, line 300 `in` |
| Also in `EXECUTIVE_SUMMARY.md` | lines 649–651 `EAD` ×3, line 685 `in` |
| Introduced by | `ceaf9a7` — "Merge pull request #88" (`git log -S 'EAD' -- index.html` → single commit) |
| Third corruption at the same site | a duplicated `<li><a href="pages/suggestions.html">Suggestions board</a></li>` and a stray blank line inside the Companion-builds list |
| Effect | `EAD` and `in` are bare text nodes in the footer `<ul>`/`<div>`, so a browser renders them as literal words between the navigation entries |

**Repair.** The three stray lines were deleted; the duplicated navigation entry was reduced to one (no
link was lost — the same `href` remains once). No prose, value or structure was otherwise changed. The
executive-summary residue was removed the same way, leaving the two addendum headings that had lost
their surrounding blank lines.

A repo-wide scan for this class was then run over `.html`, `.css`, `.js`, `.json`, `.py`, `.md`, `.xml`
and `.txt`, matching conflict markers and the exact stray tokens:

```
$ grep -rn "^<<<<<<< \|^=======$\|^>>>>>>> " --include=*.* .   # 0 outside COORDINATION.md
$ # plus an exact-match scan for EAD / HEAD / in
remaining: 0
```

No other file in the tree carried it.

---

## 4. Finding T41-D3 — every root page requested a favicon that 404s

| Measurement | Value |
|---|---|
| Root pages with a `rel="icon"` link, before | **0 of 13** (`grep -c 'rel="icon"' *.html`) |
| Pages with one, tree-wide, before | 4 — `journal/*.html` only |
| Icon that exists | `assets/favicon.svg` (present, referenced by the journal) |
| Consequence | a browser requests `/favicon.ico` by default; Pages answers **404**. Journal pages resolved theirs; nothing else did. |

Fixed on all 12 remaining root pages. Three of them are generated, so the fix went into the generators,
not their output:

| Page | Generated by | Fix applied to |
|---|---|---|
| `verification.html`, `sources.html` | `tools/build_root_views.py` | the `page()` template |
| `summary.html` | `tools/build_summary.py` | the inline `<head>` |
| the other 9 | hand-written | the file itself |

`python3 tools/build_root_views.py` and `build_summary.py` were re-run; both `--check` gates report no drift.

---

## 5. The new controls, and proof that they fail

### `tools/build_sitemap.py`

Derives `sitemap.xml` from the published tree. Exclusions are deliberate and documented in the module
docstring: `404.html` (an error document — `custom_404: true` on the Pages site, verified via
`gh api repos/kanlerxz87-cyber/Zone2/pages`) and `tools/`, `tests/`, `content/` (no HTML lives there;
the exclusion keeps a future stray file from being advertised).

**Deliberately not emitted:** `<lastmod>`, `<changefreq>`, `<priority>`. Google documents that it
**ignores `<priority>` and `<changefreq>`**, and uses `<lastmod>` only "if it's consistently and
verifiably … accurate." This repository has no per-file change date it can trust — `actions/checkout`
fetches a single commit, so `git log` cannot see a file's history in CI. Emitting a typed date would be
exactly the class of unverified value every other gate here refuses to publish. Source:
<https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap> ("Google ignores
`<priority>` and `<changefreq>` values"; "Google uses the `<lastmod>` value if it's consistently and
verifiably (for example by comparing to the last modification of the page) accurate"). Absolute-URL
requirement: same page, "Use fully-qualified, absolute URLs in your sitemaps."

### `tools/seo_audit.py`

Seven checks. D1–D6 fail the build; D7 is a report, because the duplicate-content decision is an owner
decision already on the board (MQ-08 / DS-12) and the marketing set is internally consistent (0 pages
point a canonical elsewhere). D6 shares its published-page definition with `build_sitemap.py` by
importing `EXCLUDED_DIRS`/`EXCLUDED_FILES`, so the two cannot drift apart.

**Negative tests — nine defects injected into a throwaway copy, each must fail.** Run 2026-11-15:

| # | Injected defect | Check | Exit | Message |
|---|---|---|---|---|
| N0 | none (baseline) | — | **0** | — |
| N1 | one page dropped from `sitemap.xml` | D1 | **1** | `D1 sitemap coverage: 1 of 115 published pages absent — /marketing/index.html` |
| N2 | `<loc>` for a file that does not exist | D2 | **1** | `<loc> …/does-not-exist.html has no corresponding file` |
| N3 | duplicate `<loc>` | D2 | **1** | `duplicate <loc> '…/analysis.html'` |
| N4 | `robots.txt` with a blanket `Disallow: /` | D3 | **1** | `contains a blanket Disallow: /, which blocks the whole site` |
| N5 | `robots.txt` without the `Sitemap:` line | D3 | **1** | `does not advertise https://…/sitemap.xml` |
| N6 | `noindex` on a page listed in the sitemap | D4 | **1** | `page is listed in sitemap.xml but declares noindex — marketing/index.html` |
| N7 | `marketing/sitemap.xml` misses a page | D5 | **1** | `1 marketing page(s) absent — /marketing/index.html` |
| N8 | root page loses its icon link | D6 | **1** | `1 root page(s) without a resolvable icon — products.html` |
| N9 | malformed sitemap XML | D2 | **1** | `does not parse as XML (mismatched tag: line 1, column 24)` |

**Negative tests for the generator.** On a copy: unmodified → `--check` exit 0; a new page added →
`--check` exit 1 (`committed 115 URLs, a fresh derivation has 116`); regenerate → exit 0 and the new
page appears in the file.

N6 initially passed when it should have failed. The cause was the test, not the gate: the injected
`<meta charset="UTF-8">` did not match the file's lowercase `utf-8`, so nothing was injected. Re-run
against the real string, D4 fires. Recorded because a negative test that silently no-ops is worse than
no test.

### CI

Two steps added after `audit_site.py` in `.github/workflows/pages.yml`:

```
- name: Rebuild the sitemap and confirm committed output is current
  run: python3 tools/build_sitemap.py --check
- name: Discoverability audit (sitemap coverage, robots, noindex, favicon, canonical)
  run: python3 tools/seo_audit.py
```

The whole job was replayed locally — one script per step, extracted from the workflow — before each
push: **24 of 24 steps green**, twice (before and after the shared-policy refactor).

---

## 6. Official sources re-verified this session (live fetches, 2026-11-15)

The site's load-bearing compliance facts were spot-checked against the official pages; this session
changed none of them, but a claim that is not re-read is a claim being taken on trust.

| ID | Claim on the site | What the official page says | Verdict | Source |
|---|---|---|---|---|
| V-01 | Mandatory disclosure sentence (§5) | "You must clearly and prominently state the following … 'As an Amazon Associate I earn from qualifying purchases.'" — and "You will not misrepresent or embellish our relationship with you … or express or imply any affiliation" | **Verified verbatim** | <https://affiliate-program.amazon.com/help/operating/agreement> |
| V-02 | Operating Agreement currency | "**Updated:** October 15, 2025" | **Verified** | same |
| V-03 | §2 consequences | "permanently … cease payment of … any and all commission income … without notice" on violation | **Verified verbatim** | same |
| V-04 | §4 no income representation | "We do not make any representation, warranty, or covenant regarding the amount of traffic or commission income you can expect" | **Verified verbatim** | same |
| V-05 | §6 termination | 7 calendar days' notice; immediate termination on material breach; "any violation of Section 5 … will be deemed a material breach" | **Verified verbatim** | same |
| V-06 | Session / attribution window | Session ends at first of: 24 hours, order placed, or click on another Special Link; cart completion **no later than 89 days** after initial click; shipped/paid **within 180 days** of purchase | **Verified verbatim** | <https://affiliate-program.amazon.com/help/operating/policies> |
| V-07 | Program Policies currency | "**Updated:** April 14, 2026" | **Verified** | same |
| V-08 | Policy → material breach | "any violation of the Associates Program Participation Requirements, the … IP License or Section 1 of the … Influencer Program Policy will be deemed a material breach" | **Verified verbatim** | same |
| V-09 | Table 1, all eleven bands | 10.00% Luxury Beauty/Luxury Stores Beauty/Amazon Explore · 5.00% Digital+Physical Music, Handmade, Digital Videos · **4.50% Physical Books, Kitchen, Automotive** · 4.00% devices/fashion/watch band · 3.00% Toys…Amazon Coins · 2.50% PC, PC Components, DVD & Blu-Ray · 2.00% Televisions, Digital Video Games · 1.00% Grocery/Health · **0.00%** excluded band incl. Gift Cards, Vehicles · **0.00% Coach** · **4.00% All Other Categories** | **Verified — all 11 rows match `ledger/commission_table.json` exactly** | <https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ> |
| V-10 | Three supplied links → destinations | `link.amazon/B04G1MEwY` → `/dp/B0CDY277D3` ("CHEFMAN 6 Quart Dual Basket Air Fryer Oven…"); `/B02NbDxp3` → `/dp/B09B7SB46R` ("Emeril Lagasse 26QT French Door…"); `/B00hJ57DV` → `/dp/B08DKYBTPH` ("Chefman Air Fryer 8 Qt … TurboFry") | **Reproduced — matches the ledger**; each carried `plpRedirect=mhFallback`, `lv=shuf`, a per-fetch `btn_ref=srctok-…`, and **no `tag=` parameter** | the three `link.amazon` URLs |

**No product value was copied from these fetches.** The `$69.97` price shown on the Amazon page for
B0CDY277D3 was observed and is **deliberately not published anywhere**: the repository's no-price rule
exists because Amazon restricts price display, and a sitemap task is the wrong place to break a
compliance rule.

Note on tooling: this sandbox reaches only github.com, codeload, api.github.com, registry.npmjs.org,
pypi.org and files.pythonhosted.org. Direct `curl` to `link.amazon` and to `amazon.com` fails at TLS
(`curl: (35) SSL_ERROR_SYSCALL`). All live reads above were taken through the agent's fetch path, which
returns the final URL and page title; each is reproducible by hand in a browser.

---

## 7. What remains unverified, and why (blank, not guessed)

| Item | Status | Why it stays blank |
|---|---|---|
| Whether B0CDY277D3 / B09B7SB46R / B08DKYBTPH are the products the brief intended | **Unverified** (F-01…F-03) | No public Amazon document binds a `link.amazon` code to an ASIN; the codes are 9 characters and not ASINs. Only the owner can confirm in Associates Central. |
| Associates ID / `tag=` on the links | **Absent** (F-24) | None of the three resolved URLs carries a `tag=` parameter, so as supplied they cannot attribute a commission. Owner action. |
| Search-engine indexing status (are any pages actually indexed?) | **Unverified** | No Search Console access. This session fixed what is checkable from the repository; whether a crawler has since fetched a page is only observable in the owner's Search Console. |
| Real traffic, clicks, conversions, revenue | **Does not exist** | No analytics and no Associates report has ever been supplied (F-08). Nothing on this site states a performance figure, and nothing added here does. |
| `<lastmod>` accuracy | **Not emitted** | See §5 — no trustworthy per-file timestamp source in CI. |
| Category-specific commission rate for these three ASINs | **Blank** | The custom rate card at `affiliate-program.amazon.com/help/operating/schedule` redirects to Amazon sign-in (re-confirmed this session: the redirect target is `…/home/account/payment/customratecard`). The public Table 1 band is published; the per-account rate is not. Both statements are true and the site says both, in different places: `analysis.html` carries the sign-in caveat, and the Table 1 bands are published from `ledger/commission_table.json`. |

---

## 8. Irregularities flagged for review (non-blocking)

| ID | Finding | Where | Disposition |
|---|---|---|---|
| IR-01 | **Merge residue on the live landing page** — `EAD` ×2 and `in` rendered as visible text; a duplicated nav `<li>`; a stray blank line. Committed in `ceaf9a7`. | `index.html`, `EXECUTIVE_SUMMARY.md` | **Repaired** (§3). Worth a gate: the existing checks all look for *missing* things (missing link, missing disclosure, missing source); none looks for *foreign* text that a merge left behind. Not built here — it is a repo-wide concern beyond T41's scope. |
| IR-02 | **The sitemap had no owner and no gate.** 86% of the site was unadvertised and CI was green. | root `sitemap.xml` | **Fixed + gated** (§2, §5). |
| IR-03 | **`rel="icon"` was on 4 of 115 pages**, so every root page 404s on the default `/favicon.ico` request. Three of the missing pages were generated, so the defect would have survived a hand-edit of the HTML. | 12 root pages | **Fixed in the files and in the two generators** (§4). |
| IR-04 | **`README.md` says "37 generated pages"** under `pages/`; a fresh build emits **39** (`python3 tools/build_site.py --check` → `{"built": 39}`, and `find pages -name '*.html'` → 39: 14 at the top level, 12 in `categories/`, 13 in `modules/`). The stale figure is two low. | `README.md` | **Not changed** — `README.md` is outside T41's scope and its prose is not one of this session's files. This is a *real* drift, not a different set: `check_counts` was checked and does **not** cover page counts (it matches only `checks`, `sources`, `flags` and `items flagged`), so nothing would have caught it. Logged for the owner of `README.md`; the fix is "37" → "39" or, better, deriving it. |
| IR-05 | **`marketing/improvements.html` was suspected of `noindex`** during the audit (`grep -c noindex` → 1). It is a false positive: the match is the word "noindex" inside MQ-08's prose about a future decision. No `robots` meta exists on any marketing page. Recorded so the next session does not re-chase it. | `marketing/improvements.html` | No action. |
| IR-06 | **Checked and NOT a defect, recorded so the next session does not re-chase it.** `affiliate-lab/flagged-for-review.html` AF-09 ("Commission Income Schedule requires Associates sign-in") and `affiliate-lab/compliance.html` looked like stale copies of a claim `EXECUTIVE_SUMMARY.md` says was corrected. Re-read this session: AF-09 is about `help/operating/schedule`, which §7 re-confirmed **does** redirect to sign-in (`…/home/account/payment/customratecard`), and it explicitly says "the public category rate card was used instead" and links the public Table 1. It is accurate and it is not the claim that was corrected — the corrected one was the *absence* of a public fixed-rate table. | `affiliate-lab/**` | **No action.** Nothing false. |
| IR-07 | **`COORDINATION.md` is ~4,240 lines / 400 KB** with repeated task-ID renumbering (this session ships as T41). T40 flagged the same (I-D). It is auditable but slow, and renumbering has already corrupted another session's row once (T39's record). | `COORDINATION.md` | Recorded; no archival done here. |

---

## 9. Files touched

| File | Change |
|---|---|
| `sitemap.xml` | regenerated — 16 → **115** URLs, derived from the tree |
| `tools/build_sitemap.py` | **new** — generator + `--check` gate |
| `tools/seo_audit.py` | **new** — D1–D7 discoverability gate |
| `.github/workflows/pages.yml` | two steps added (sitemap rebuild check, discoverability audit) |
| `tools/build_root_views.py`, `tools/build_summary.py` | favicon `<link>` in the shared head templates |
| 9 hand-written root pages | favicon `<link>` only |
| `verification.html`, `sources.html`, `summary.html` | regenerated from the patched generators |
| `index.html` | merge-residue repair (§3) + favicon |
| `EXECUTIVE_SUMMARY.md` | merge-residue repair (§3) |
| `docs/verification-156aae86.md` | this record |
| `COORDINATION.md` | T41 claim + closing record (append-only) |

No file owned by another session's active scope was edited: `ledger/**`, `assets/js/**`,
`marketing/data/**`, `tools/build_marketing.py`, and every companion namespace are untouched.
