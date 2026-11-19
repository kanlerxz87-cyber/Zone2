# Counter Notes · Zone2

**Current release — 19 November 2026:** a product-led kitchen publication for the five supplied Amazon
links. Start at [the publication](https://kanlerxz87-cyber.github.io/Zone2/) or the
[current executive summary](https://kanlerxz87-cyber.github.io/Zone2/executive-summary.html).
**Shipped:** [PR #174](https://github.com/kanlerxz87-cyber/Zone2/pull/174), merged as
`4fcb61a` on 2026-11-19. [Main build and Pages deployment](https://github.com/kanlerxz87-cyber/Zone2/actions/runs/44475122952)
succeeded and live content was fetched. Exact evidence and remaining gates are in
[the verification record](docs/verification-37333afd.md) and [coordination board](COORDINATION.md).

## What this release actually provides

- Five source-linked product notes in two clusters: air fryers/countertop ovens and temperature tools.
  Five practical question-led guides, a format comparison, honest AI-assisted organizational authorship,
  original labelled artwork, root RSS and one reader sitemap. No invented hands-on review or “best” score.
- One Workspace navigation group and footer for all dashboards and preserved evidence archives.
  The **deployed `_site` artifact** applies noindex to operator/archive pages, self-canonicals, masthead
  disclosure repeated in the footer, and sponsored product anchors—including dynamically rendered links.
  Historical source files and decisions remain traceable; old implementation statements are dated snapshots.
- An implemented **first-party SQLite collector**, not just browser-storage queues: daily aggregates for
  `page_view`, `product_link_click`, `disclosure_view`; separately gated local importers for
  `conversion_import` and `search_query_import`. No reader IDs, cookies, analytics localStorage, raw
  referrers or IP/UA database fields. DNT/GPC and 90-day retention. See [measurement/README.md](measurement/README.md).
- Pages config intentionally **OFF**: GitHub Pages is [static hosting](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages).
  A tested temporary preview is not a permanent collector deployment. No authorized performance report
  has been imported; unavailable activity is not represented as zero orders.
- Direct reader product links use the supplied tracking ID `shopnow047c-20`. Neither enrollment nor
  attribution is authenticated. Intended ASIN/listing/date/source stay blank and separate from the dated
  observed destinations. The supplied short links are **not declared invalid**.
- Reviewable suggestions and known/unknown/discovery registers; local preference/export controls do not
  implement proposals. A review-only editorial planner includes a shared-meal seasonal reading cluster.
  No unattended LLM service, scraper, price/review feed or autonomous conversion optimizer is connected.

## Run and verify

```sh
python3 tools/build_front.py
python3 tools/build_artwork.py --check
python3 tools/build_sitemap.py
python3 tools/package_site.py
python3 tools/verify_publication.py
python3 -m measurement.collector serve --preview --port 8000
# open /Zone2/ on the same origin; use the proxied Arena preview host, never a browser-side localhost API
```

The Pages workflow uploads **only `_site`**, never the checkout, `.git`, local tooling or SQLite data.
Preserve all prior namespace gates. For the complete configured CI replay:

```sh
python3 tools/ci_replay.py
# Browser dependencies are development-only (npm ci); no production npm runtime is needed.
# The browser suite starts/stops a local fixture collector, blocks external navigation,
# tests desktop/mobile/keyboard/accessibility and verifies real local SQLite persistence.
```

Current code/data: `content/publication.json`, `content/guides.json`, `tools/publication.py`,
`tools/package_site.py`, `tools/verify_publication.py`, `measurement/`.
[Official sources and exact verification scope](docs/verification-37333afd.md) distinguish facts,
listing claims, unverified conflicts, tests and external deployment/account gates.

## Earlier dated project records

The material below is preserved for traceability. Earlier counts, missing-tag statements and client-only
measurement descriptions are historical—not the state of the current publication. The current summary
and verification record above take precedence. No historical date is silently refreshed.

---

# Zone2

AI-powered Amazon affiliate marketing platform — product research, trend and conversion analysis,
pricing/review/competition/commission analysis, SEO article · comparison · buying-guide generation,
niche discovery, link and campaign management, click/conversion tracking and continuous optimization,
built under Amazon Associates policy and disclosure requirements.

**Everything here is source-governed: a value appears only when an official source states it, and
anything unconfirmed is left blank and published on a Flagged for Review page rather than inferred.**

## Live site

<https://kanlerxz87-cyber.github.io/Zone2/> — GitHub Pages, served from the `main` branch root (`/`).

Dated repository review (2026-11-15), with live re-checks and irregularities R86-01 to R86-08: <https://kanlerxz87-cyber.github.io/Zone2/review-2026-11-15.html>.

## Site structure

### Primary platform

| Page | Purpose |
|---|---|
| `index.html` | Landing — hero, verified KPIs, product cards, executive summary, evidence (marketing redesign, 2026-11-15) |
| `products.html` | Product catalog + manufacturer spec tables, per-row source links |
| `analysis.html` | Niche, pricing, competition and commission-potential analysis |
| `content.html` | SEO content plan (articles, comparisons, buying guides) + editorial topic ideas for review |
| `compliance.html` | Associates policy and disclosure requirements |
| `tracking.html` | Special Link and campaign tracking setup |
| `verification.html` | Verification log — one row per claim, with the method used and the official page (generated) |
| `sources.html` | Complete source register, with each source's class made explicit (generated) |
| `flagged.html` | Flagged irregularities and unverified items, with source links |
| `design-notes.html` | Design rationale, compliance-linked design decisions, and queued suggestions for review |
| `journal/index.html` | **Journal (T38)** — hand-written editorial around the observed listings: a dual-basket trend explainer, a basket-vs-oven buyer's framework, and the site methodology |
| `journal/dual-basket-air-fryers.html` | What dual-basket cooking actually changes; argued from verified specs, conflicts included |
| `journal/basket-vs-oven.html` | Choosing between basket fryers and air-fryer ovens by geometry, not brand |
| `journal/why-every-number-has-a-source.html` | The blank-until-verified methodology and the compliance rules that shaped the build |
| `audit/index.html` | **Independent audit (2026-11-15, session `f8e18ca8`)** — 16 findings from a fresh line-by-line read of the deployed tree, each with the measurement behind it and an official source or an explicit unverified flag |
| `audit/suggestions.html` | The review-and-choose board: 14 recommendations with options, recommendation, cost, risk, reversibility and blockers. **Nothing is implemented from it** |
| `audit/gaps.html` | Missing-information register: 15 questions, what is verified, what is missing, how to close each, and who can |
| `audit/traffic.html` | Organic-traffic readiness restricted to documented Google/Amazon rules, quoted, plus the five metrics that no official source can verify — left blank |
| `audit/decision-cost.html` | Cost, reversibility, sequence and the consequence of deciding nothing, per open decision |
| `audit/method.html` | Every command run, what it cannot see, and which sources were re-fetched today versus carried |

The root pages were redesigned on 2026-11-15 (session `2b257b2e`) into a marketing presentation of the
same verified data — same ledger, same gates, no value changed; the reasoning lives on
[`design-notes.html`](https://kanlerxz87-cyber.github.io/Zone2/design-notes.html). `robots.txt` and
`sitemap.xml` were added for crawl hygiene.

#### Front of house — `index.html`, `suggestions.html`, `questions.html`, `guides/` (T50, 2026-11-16)

The brief for 2026-11-16 was that the site read as generated. The root pages were rebuilt as a
publication: a lead story about the three appliances, the machines as a hairline grid carrying their
real specifications, the guides as a story grid, and the verification state demoted to a single
receipts strip. All 11 hand-written root pages now share one masthead, disclosure strip and footer
(`assets/css/publish.css`, loaded alongside `style.css`), so a reader no longer crosses a design break
moving between the shop front and the operator pages.

| Page | Purpose |
|---|---|
| `index.html` | Publication front page: lead story, the three machines, the guides, the receipts strip |
| `suggestions.html` | **The decision board.** 12 suggestions, each with options A/B/C, cost, trade-off, a recommendation, the question it waits on, and status *Proposed — awaiting owner decision*. Nothing is implemented from it |
| `questions.html` | **The questions register.** 12 questions — what is known, what is missing, the action that would close each, and which suggestions it blocks |
| `guides/index.html` | The eleven published pieces grouped by reader category |
| `guides/basket-air-fryers.html` | Drawer-style machines, with the full sourced specification tables for both Chefman listings |
| `guides/air-fryer-ovens.html` | The Emeril 26-quart oven, with its full sourced specification table |
| `guides/buying-guides.html` | Decision-first pages |
| `guides/method.html` | How a figure earns a place on the site, and why a dash is sometimes the answer |

These eight pages are **generated**, not hand-written: `tools/build_front.py` renders them from
`marketing/data/facts.json` and `docs/board-9251f262.json`, so no figure is re-typed and every row
carries the official page that states it. `tools/build_front.py --check` fails CI if a committed page
has drifted from the dataset; `tools/verify_front.py` re-reads the pages on disk and enforces the rules above
(per-row sourcing, blanks carry a written reason, no prices, disclosure above the data, sponsored
product links, links resolve, canonical matches the path, no invented performance figures).

**No verified value changed.** No ledger row, no `assets/js/data.js` entry, no product attribute. The
rebuild is presentation and information architecture applied to the same evidence.

`verification.html` and `sources.html` are generated from `ledger/verification.json` and `ledger/sources.json`
by `tools/build_root_views.py` — CI fails if the committed output drifts from the ledger, so a row can never be
published without its official source link.

### Owner's Console — `console/` (T42, session `arena/d26f42db-zone2`)

**The section to open first if you are deciding what to build next.** Everything on it is a proposal; none of it
is implemented, and nothing is built until a choice is recorded on the decision sheet.

| Page | Purpose |
|---|---|
| `console/index.html` | Executive summary and the decisions in the order that unblocks the most |
| `console/suggestions.html` | 14 new proposals (`P-01…P-14`) — what changes, the options with trade-offs, a recommended path, effort, risk, evidence, and the questions each one waits on |
| `console/questions.html` | The information register: 15 questions an official source answers, 12 nothing here can answer, and the evidence inventory — each open row with the action that closes it |
| `console/design.html` | The redesign pack: why the site reads as machine output, before/after rewrites of the actual published copy, page templates, six articles, and a paste-ready brief |
| `console/review.html` | Line-by-line repository review: 11 namespaces, 9 measurements, 26 source checks |
| `console/decisions.html` | The decision sheet and an index of every register on this project |
| `console/flagged.html` | 9 irregularities (`IR-01…IR-09`), non-blocking, each with its source and the action that closes it |
| `console/sources.html` | The `C-01…C-31` register — every page a claim was read from, fetched 2026-11-15, with the verbatim sentence each one supports |

Generated by `tools/build_console.py` from `console/data/*.json`; gated by `tools/validate_console.py`
(referential integrity, official-host policy, blank-or-sourced, no invented metrics, no prices, disclosure on
every page, links resolve, board integrity, derived counts). Both run in CI.

**It does not duplicate the canonical registers.** `pages/suggestions.html` (`SG-01…SG-10`) and
`pages/questions.html` (`Q-01…Q-16`) keep their rows and their IDs; the console indexes them and adds only
namespaced rows (`P-`, `IN-`, `IR-`, `C-`) so nothing can collide.

### Review board — repository root (T53, session `arena/7c1511ee-zone2`)

**The section to open if the question is "which change do we make, and what is it waiting on".** Twelve
proposals on one scale — each with three options, the commitment/cost/risk of each, a recommendation, the
open question it waits on, and the official page its argument rests on — plus the information register, a
requirements trace of the 2026-11-16 request, and five article concepts. None of it is implemented: every
row reads *awaiting your decision* and the gate refuses a page that reads otherwise.

| Page | Purpose |
|---|---|
| `review-decide.html` | **The answer sheet.** The four proposals worth deciding first with every option, the 9 questions with the action that closes each, and how to reply. Start here if you only read one page |
| `review.html` | 12 proposals (`PS-01…PS-12`) scored on one scale, sorted by area, with this session's own irregularities and how each was resolved |
| `review-questions.html` | 9 questions (`PQ-01…PQ-09`): what is verified, what is missing, and the exact action that obtains it. No row carries an answer |
| `review-trace.html` | The request traced sentence by sentence (`RP-01…RP-16`), 12 measurements (`PM-01…PM-12`), 9 design findings (`PD-01…PD-09`) and 11 official sources quoted verbatim |
| `review-ideas.html` | 5 article concepts (`PS-13…PS-17`), each with its basis, the page it would become, and why it might convert |
| — | The irregularities `PI-01…PI-05` on `review.html#irregularities`: what was found, how it was resolved, what is left for the owner |

Generated by `tools/build_review_board.py` from `docs/review-board.json`; gated by
`tools/validate_review_board.py` (13 rules: source integrity, official hosts only, real quotes, three options
per proposal with a trade-off each, nothing reads as decided, open questions unanswered, derived counts,
disclosure, links and fragments, requirements traced, no product price) and negative-tested by
`tools/test_review_board.py` (19 injected defects, each must fire). All three run in CI.

**Why the register lives in `docs/`, not `decisions/`.** `tools/build_decisions.py --check` hashes every file
under `decisions/`, so any register stored there becomes permanent drift against the generated output. The
repository's established convention for a register is `docs/*.json` (`docs/discovery-t40.json`), and this one
follows it.

### Design brief — `brief/` (T57, renumbered from T50 — session `arena/dc72a69e-zone2`, 2026-11-16)

**The section to open if the question is "why does this site read like a machine wrote it, and what would
fix it?"** Every number on it was measured in the tree on 2026-11-16 and **re-measured after T55 rebuilt the
front pages mid-review**; every proposal on it is unimplemented.

| Page | Purpose |
|---|---|
| `brief/index.html` | Executive summary: the state table, the one blocking fact, and the three decisions that unblock the most |
| `brief/design-prompt.html` | The measured diagnosis, three before/after rewrites of actual published copy, the design system, and a paste-ready prompt for the rebuild |
| `brief/topics.html` | 12 article proposals for organic traffic, each with the verified fact it rests on — and a stated reason none can be ranked by expected volume |
| `brief/suggestions.html` | The review-and-choose board: 12 proposals (`DB-01…DB-12`) with options, trade-offs, effort, risk, reversibility and blockers. **Nothing is implemented from it** |
| `brief/questions.html` | 13 questions an official page answers, 10 nothing here can, and the inventory of what the project holds |
| `brief/review.html` | Line-by-line repository review: 16 measurements with the command behind each, plus links for manual review. Re-measured after T55 landed mid-review |
| `brief/verification.html` | One row per check this session ran, with the method and the page it was checked against |
| `brief/sources.html` | The `BR-01…BR-22` register — every page a value was read from, with the verbatim quote and the fetch date |
| `brief/flagged.html` | 8 irregularities (`FB-01…FB-08`), non-blocking, each with what would close it and who can |

Task-id note: claimed as **T50**, renumbered **T57** (T50…T56 were all shipped by other sessions the
same day). Renumbered rather than contended.

Generated by `tools/build_brief.py` from `brief/data/*.json`; gated by `tools/validate_brief.py`
(referential integrity, measurement rows must state a method, official rows must carry a source, carried
rows must say what they carry, open questions stay empty, **the executive summary's counts are re-derived
from the tree at gate time**, board integrity, disclosure, no price, canonical, links resolve, anchors
resolve). Negative-tested by `tools/test_brief.py` (12 injected defects, each must fire). All three run
in CI.

**It does not duplicate the canonical registers.** `pages/suggestions.html` (`SG-01…SG-12`),
`pages/questions.html` (`Q-01…Q-18`), `console/suggestions.html` (`P-01…P-14`),
`marketing/improvements.html` (`DS-01…DS-14`) and the root `suggestions.html` / `questions.html` (T55)
keep their rows and their IDs; the brief indexes them and adds only namespaced rows (`BR-`, `DB-`, `TQ-`,
`BQ-`, `IN-`, `RV-`, `FB-`, `VF-`), so nothing can collide.

Two of the eight flags it raises are the same defect twice, on the release-readiness board: `RR-01` prints
"116 published HTML pages" and `RR-05` prints "72 pages link to amazon.com/dp/", while the tree measures
150 and 87 (re-measured on 2026-11-16 after T55 added the `guides/` namespace and rebuilt the root
pages). Both are typed rather than derived, so both drifted silently. They are logged as change request
CR-1 in COORDINATION.md because the files that own them are outside this session's scope.


### Submitted-link intake — `intake/` (T60, session `arena/613900e6-zone2`, 2026-11-17; renumbered from T58)

The 2026-11-17 brief names **five** `link.amazon` links. This repository was built around **three**, and
`B0c8moW59`, `B0f3GKalj` and the tracking id `shopnow047c-20` appeared nowhere in the tree. This namespace
closes that gap — it adds rows under its own prefixes (`IN-`, `SUB-`, `OBS-`, `IF-`, `IQ-`, `IP-`, `EV-`) and
edits no register another session owns.

Eight pages: [executive summary](https://kanlerxz87-cyber.github.io/Zone2/intake/index.html) ·
[product-intent record](https://kanlerxz87-cyber.github.io/Zone2/intake/submissions.html) ·
[observations](https://kanlerxz87-cyber.github.io/Zone2/intake/observations.html) ·
[measurement](https://kanlerxz87-cyber.github.io/Zone2/intake/tracking.html) ·
[choose a path](https://kanlerxz87-cyber.github.io/Zone2/intake/proposals.html) ·
[what we know](https://kanlerxz87-cyber.github.io/Zone2/intake/questions.html) ·
[flagged](https://kanlerxz87-cyber.github.io/Zone2/intake/flags.html) ·
[sources](https://kanlerxz87-cyber.github.io/Zone2/intake/sources.html)

**The product-intent confirmation record** keeps two things apart, because they are not the same fact:
the *intended* ASIN, official listing URL, confirmation date and source — all blank, because a 9-character
token is not an ASIN and nothing public binds the code to a product — and the *observed* redirect target,
which is measured and populated. The two field groups are never merged, and a gate fails the build if
they are.

| Submitted | Resolves to | Category |
|---|---|---|
| `B04G1MEwY` | `B0CDY277D3` | Air Fryers |
| `B02NbDxp3` | `B09B7SB46R` | Air Fryers |
| `B00hJ57DV` | `B08DKYBTPH` | Air Fryers |
| `B0c8moW59` | `B0DHZTCNR5` | **Meat Thermometers** |
| `B0f3GKalj` | `B0DZFD6R9Z` | **Meat Thermometers** |

Three findings change what should be built: two of the five are not air fryers (**IF-01**); no resolved URL
carries an Associates `tag=`, so none is established as a Special Link (**IF-02**); and the self-hosted
analytics endpoint the brief asks for cannot run here, because GitHub Pages is static-only (**IF-08**).

Gate: `tools/build_intake.py` (drift check) · `tools/validate_intake.py` (contract) ·
`tools/test_intake.py` (15 injected defects, each must fire) — all three run in CI.

### Findings & verified subpages — `pages/`

37 generated pages, one table per question, **every row ending in an official-source link or an explicit
blank + flag**: [findings hub](https://kanlerxz87-cyber.github.io/Zone2/pages/index.html) ·
[executive summary](https://kanlerxz87-cyber.github.io/Zone2/pages/executive-summary.html) ·
[requested products](https://kanlerxz87-cyber.github.io/Zone2/pages/products.html) ·
[commission bands, 11 category subpages](https://kanlerxz87-cyber.github.io/Zone2/pages/categories/index.html) ·
[niche discovery](https://kanlerxz87-cyber.github.io/Zone2/pages/niches.html) ·
[platform modules, 12 subpages](https://kanlerxz87-cyber.github.io/Zone2/pages/modules/index.html) ·
[compliance control ledger](https://kanlerxz87-cyber.github.io/Zone2/pages/compliance.html) ·
[verification log (108 checks, V-01…V-108)](https://kanlerxz87-cyber.github.io/Zone2/pages/verification.html) ·
[source register (50 sources, S01…S67)](https://kanlerxz87-cyber.github.io/Zone2/pages/sources.html) ·
[tracking](https://kanlerxz87-cyber.github.io/Zone2/pages/tracking.html) ·
[content engine](https://kanlerxz87-cyber.github.io/Zone2/pages/content-engine.html) ·
[architecture](https://kanlerxz87-cyber.github.io/Zone2/pages/architecture.html) ·
[flagged for review (55 flags, F-01…F-55)](https://kanlerxz87-cyber.github.io/Zone2/pages/flags.html)

All three counts are derived from `ledger/*.json` and held to the register by
`tools/validate_data.py::check_published_counts`, so they cannot be typed wrong again.

Generated by `tools/build_site.py` from `ledger/*.json` — edit the data, never the HTML.

### Companion sites (parallel sessions, preserved in full)

- **`marketing/`** — the public, reader-facing site (desk name: *Counter Notes*). A buying guide, a
  head-to-head comparison, one article per product, six question-shaped guides under `marketing/topics/`,
  and `marketing/improvements.html` — the improvement board, where every open suggestion carries its
  options, its cost, its evidence and the question it waits on. Generated by `tools/build_marketing.py`
  from two data files (`marketing/data/facts.json` for values, `marketing/data/editorial.json` for every
  word a reader reads plus the board), so no page is hand-edited; gated by
  `marketing/scripts/verify_marketing.py` (G1–G14: disclosure on every page, link-level disclosure,
  preview-labelled links while no Associates ID exists, no prices, links resolve, every valued row
  sourced, every guide claim sourced, no filler phrasing or first-hand claims, no orphan pages,
  sitemap/feed/canonical coverage). Session `arena/e8b071cd-zone2` (T39). Record:
  `docs/marketing-2026-11-15.md`.
- **`research-hub/`** — Affiliate Research Hub: per-product attribute rows traced to official Amazon or
  manufacturer pages, comparison, requirements disposition, methodology, executive summary, plus its
  build/verify toolchain (`scripts/`, `data/*.json`). Session `arena/6602723a-zone2` (PRs #4/#6),
  relocated unchanged during final integration.
- **`zone2/`** — a second platform build (multi-page dashboard, sources, verification data) by session
  `arena/34836ddd-zone2` (PRs #5/#8/#9), preserved under its original directory name.
- **`northstar/`** — the original Northstar prototype dashboard (hash navigation, no build step) by
  session `arena/6b8bb130-zone2` (PR #1), preserved as-is.
- **`affiliate-lab/`** — Amazon Affiliate Intelligence Dashboard by session `arena/181863ad-zone2`
  (PR #14): line-by-line product verification (all three supplied codes unverified), official rate-card
  and attribution tables, compliance matrix, SEO content plan, executive summary, 13 session-local flags
  (`AF-01`…`AF-13`, namespaced so they don't collide with `ledger/flags.json`), and its own row-sourcing
  verifier (`affiliate-lab/scripts/verify_site.py`).
- **`revalidation/`** — controlled re-check of the three supplied links by session `arena/c6e94e8d-zone2`
  (2026-11-14): runs the control test the earlier "fallback" conclusion was missing, and corrects it.
  Generated by `revalidation/scripts/build.py` from `revalidation/data/*.json`; gated by
  `revalidation/scripts/verify.py` (per-row sourcing, disclosure, no product prices). Ten session-local
  flags `RV-01`…`RV-10`. Written log: `docs/revalidation-2026-11-14.md`. `EXECUTIVE_SUMMARY.md` and this file now carry the corrected conclusion.

## The five supplied links — read this before using any product data

`https://link.amazon/B04G1MEwY` · `https://link.amazon/B02NbDxp3` · `https://link.amazon/B00hJ57DV` ·
`https://link.amazon/B0c8moW59` · `https://link.amazon/B0f3GKalj`

The first three were processed by earlier sessions; the 4th and 5th were resolved and onboarded on
**2026-11-17 (T58, session `1539a895`)** — see the addendum in [`EXECUTIVE_SUMMARY.md`](EXECUTIVE_SUMMARY.md)
and [`docs/verification-1539a895.md`](docs/verification-1539a895.md). Every session agrees on the
measurements: each embedded token is **9 characters** (Amazon defines an ASIN as a unique **10-character**
identifier), and `https://www.amazon.com/dp/<token>` returns *Sorry! We couldn't find that page* for all
five. The 4th and 5th resolve to kitchen thermometers (`B0DHZTCNR5` ThermoMaven, `B0DZFD6R9Z` CHEF iQ) —
a second product category.

Earlier sessions concluded from the redirect alone that the destinations were *arbitrary fallback pages*.
**On 2026-11-14 that reasoning was tested and corrected** (see `revalidation/`). The measurements now read:

| Observation | Result |
|---|---|
| Redirect target | five **different** ASINs — links 1–3: `B0CDY277D3`, `B09B7SB46R`, `B08DKYBTPH` (air fryers); links 4–5: `B0DHZTCNR5` (ThermoMaven thermometer), `B0DZFD6R9Z` (CHEF iQ thermometer) — each a live product page |
| Redirect markers | every target carries `plpRedirect=mhFallback` and `lv=shuf` |
| Same-day re-fetch | **Corrected 2026-11-14:** re-fetched twice, the link returned the same `/dp/` path and the same page body — the "shuffle" is not reproducible. **Cross-day re-fetch (2026-11-14, session a133aa61):** same ASIN and body again, but the `btn_ref` token **differs** for all three links, so the token is per-day, not per-link-stable (flag **F-21**). See `revalidation/`. |
| Control (added 2026-11-14) | A **bare, untagged** request to a *valid* ASIN (`/dp/B08DKYBTPH`) is also answered with `plpRedirect=mhFallback&lv=shuf` appended. The marker is therefore not evidence of a fallback. |
| Associates tag | absent from all five resolved URLs — under OA §1 a Special Link must use Amazon's tagged format, so as supplied these links cannot be relied on to attribute commission. |

**What this does and does not settle.** The supplied codes are not ASINs, so the codes alone identify
nothing. But each `link.amazon` URL is a stable, individually tracked link resolving to one consistent
product — five distinct per-link tokens, identical on re-fetch. The earlier claim that the destinations
*change content and token between requests* is **not reproducible**, so the destinations are **not** shown to
be arbitrary fallbacks. The product pages elsewhere in this repository are therefore accurate **about those
five ASINs** (each row cites the manufacturer's or Amazon's own page), and they are the products these links
resolve to. Links 4 and 5 were added on 2026-11-17 (T58); their destination specifications are sourced to the
two Amazon listings and their identity remains observed, not confirmed.

Two things remain genuinely open, and are still flagged: **no public Amazon document binds a short code to a
destination ASIN** (so the mapping is observed behaviour, not documented intent), and **no resolved URL carries
an Associates `tag`** (so as supplied the links cannot be relied on to attribute commission). Recorded as
**F-12 / I-20** in [`COORDINATION.md`](COORDINATION.md), [`pages/flags.html`](https://kanlerxz87-cyber.github.io/Zone2/pages/flags.html)
and **RV-01…RV-03** in [`revalidation/flagged.html`](revalidation/flagged.html).
**Owner action:** confirm the mapping in Associates Central and regenerate the links with your Associates tag.

## Data & verification

| Namespace | Contents | Gate | In CI? |
|---|---|---|---|
| `assets/js/data.js` | primary site's dataset | workflow link/asset + data-parse steps | yes |
| `ledger/` | `pages/` dataset: products, commission table, compliance rules, modules, flags, verification log, sources, niches, campaigns | `tools/validate_data.py` + `tests/test_pipeline.py` | yes |
| `research-hub/data/` | hub dataset: products, compliance, requirements, sources, raw log | `research-hub/scripts/verify.py` | **no** — see below |
| `audit/data/` | audit namespace: findings, recommendations, gaps, decision-cost, traffic readiness, sources | `tools/validate_audit.py` + `tools/test_audit.py` (11 negative tests) | yes |

`tools/validate_data.py` fails the build when a row carries a value without a source, or a blank without a
flag; when a source host is outside the allowlist (`affiliate-program.amazon.com`, `amazon.com`,
`webservices.amazon.com`, `ftc.gov`, `developers.google.com`, `support.google.com`, `docs.github.com`);
when any performance metric is invented rather than reported; when an Amazon mark appears in an identifier
this project controls; when a page with a sponsored link lacks the disclosure sentence; when a page prints a
**product** price; when the landing loses its route into `pages/`; or when an internal link breaks (976
links checked).

**Resolved 2026-11-14 (T26, session `808a6840`).** The hub's own guard
(`research-hub/scripts/verify.py`, logged as I-27) was stale after the namespace move: it resolved the
repository root to `research-hub/` and then looked for the root site's files *inside* the hub, so it
reported seven false failures and was excluded from CI. It now resolves the hub and the repository root
separately, checks **13 pages** and **38 sourced attribute rows**, and **runs in CI**. It was verified to
fail on purpose (a removed disclosure and an injected `$49.99` each produce an error) before being trusted.

## Platform code (`tools/`)

| File | Role |
|---|---|
| `asin_guard.py` | identifier validation; refuses to repair a short token |
| `amazon_creators_api.py` | Creators API client (PA-API 5.0 is deprecated → `403 AccessDenied`); hashed raw responses, freshness classes, `BLOCKED` instead of scraping |
| `scoring.py` | opportunity + expected-value maths; returns `INSUFFICIENT_DATA` rather than a default; rates loaded only from `ledger/commission_table.json` |
| `generate_articles.py` | article / comparison / buying-guide renderer, six-family lint suite, refuses unverified entries |
| `link_builder.py` | compliant Special Link + disclosure emitter (tag required, `rel="sponsored nofollow"`, per-visitor sub-tags and competing attribution params rejected) |
| `redirect_server.py`, `tracking_schema.sql` | privacy-minimal first-party click counting (no cookies, IPs, or visitor ids) |
| `optimize.py` | evidence-gated optimizer: no action without ≥30 clicks **and** a dated report |
| `cache.py` | keyed cache with per-class freshness + request pacing |
| `build_site.py`, `validate_data.py` | deterministic site generation and the deploy gate |

```bash
python3 tools/build_site.py            # regenerate pages/ (deterministic, network-free)
python3 tools/build_site.py --check     # fail if committed pages/ drift (content-hashed)
python3 tools/validate_data.py          # deploy gate -> JSON report, non-zero exit on any error
python3 tests/test_pipeline.py          # 15 executable guard checks
python3 tools/audit_site.py             # structural audit: fragments, orphaned sets, prose counts
python3 tools/scoring.py                # published bands + scoring behaviour
PYTHONPATH=tools python3 tools/amazon_creators_api.py   # prints the BLOCKED reason (no credentials here)
```

## Affiliate disclosure & policy position

> As an Amazon Associate I earn from qualifying purchases.

Required by the Operating Agreement (§5) and rendered in the footer of every generated page. Outbound links
carry `rel="sponsored"` per Google's guidance; this project's own name contains no Amazon mark, as the
Participation Requirements demand. Prices and availability are never displayed as static text, sub-tags are
never tied to a specific end user, and content is never distributed by email, SMS or print — the controls and
their rule-by-rule citations live in [`pages/compliance.html`](https://kanlerxz87-cyber.github.io/Zone2/pages/compliance.html).
Both governing pages carry their own update dates (Agreement: 15 Oct 2025; Program Policies: 14 Apr 2026) and
change without notice, so re-verify each cycle.

## Building

Static site — no build step for the primary site or the companion views; open `index.html`. `pages/` is
regenerated by `python3 tools/build_site.py`. `.github/workflows/pages.yml` validates links, assets, data,
disclosure and pricing rules for every view — plus the `pages/` gates above — on each push and PR.

## The Associates tag is live (2026-11-17, session `7264f3c2`)

The owner supplied the tracking ID **`shopnow047c-20`**. It lives in one place —
`ASSOCIATES_TAG` in [`tools/link_builder.py`](tools/link_builder.py) — and flows from there:

* every reader-facing product link is a **tagged Special Link** emitted by
  `build_product_link()`, which refuses a malformed tag, an unvalidated ASIN, competing
  attribution parameters and per-visitor sub-tags;
* the deploy gates enforce it: `tools/verify_front.py` fails a product CTA without the tag,
  `marketing/scripts/verify_marketing.py` fails any product link without it, forbids any *other*
  tag, and forbids tags on citation links (`class="src"` / `class="pb-src"`), which stay
  unmonetized evidence;
* the per-link confirmation record — intended ASIN (blank with a reason; every supplied code is
  9 characters), official listing URL, confirmation date, and the observed redirect target kept in
  a **separate field, never merged** — is [`docs/product-intent.json`](docs/product-intent.json),
  published at [intent.html](https://kanlerxz87-cyber.github.io/Zone2/intent.html).

Click measurement is also live: `assets/js/events.js` records the three client-side events of
`docs/measurement-t40.json` (page views, product-link clicks, disclosure views) with no cookie, no
identifier and nothing per person, under the owner decision recorded on DS-11. Counts are held in
the visitor's own browser until the owner deploys the endpoint (`tools/tracking_schema.sql` is the
contract); nothing is transmitted and no count is published until then. Conversions still come only
from Associates reporting (EV-04, blocked).

### Submitted-link intake — `intake/` (T60, session `arena/613900e6-zone2`, 2026-11-17; renumbered from T62)

**2026-11-17 (T62, session `1539a895`)** — see the addendum in [`EXECUTIVE_SUMMARY.md`](EXECUTIVE_SUMMARY.md)

resolve to. Links 4 and 5 were added on 2026-11-17 (T62); their destination specifications are sourced to the


## The decision board (`board/`) — the five-product brief, 2026-11-17

Added by session `arena/1bfbc559-zone2` (T62). The 2026-11-17 brief named **five** products;
the register held **three**. The two new ones — `link.amazon/B0c8moW59` and
`link.amazon/B0f3GKalj` — appear in no file in this repository before that date, and both
resolve to **meat thermometers**, not air fryers. The brief also supplied a tracking ID
(`shopnow047c-20`) for the first time in the project's history.

Nine generated pages, built by `tools/build_board.py` from `board/data/*.json`, gated by
`tools/validate_board.py`, negative-tested by `tools/test_board.py` (19 injected defects,
each must fire):

| Page | What it holds |
|---|---|
| `board/index.html` | Executive summary and the three decisions that gate everything else |
| `board/products.html` | The product-intent confirmation record — five rows, intent and observation held in separate field groups that never merge |
| `board/suggestions.html` | Twelve suggestions, two or three costed options each, **nothing applied** |
| `board/questions.html` | 17 questions: 3 answered and sourced, 14 left empty on purpose, each with the action that would close it |
| `board/requirements.html` | Every row in the brief, checked against the tree rather than against the brief's own status word |
| `board/topics.html` | Ten question-shaped article proposals, deliberately unordered |
| `board/sources.html` | The source register — live reads and carried quotes labelled apart |
| `board/verification.html` | The line-by-line verification record — each claim with its method, result and source |
| `board/flagged.html` | 13 irregularities |

Three rules are specific to this namespace and enforced by the gate: **nothing is chosen**
(every suggestion's `chosen` field is empty), **an open question carries no answer**, and
**an intent field may never borrow a value from the observation group**.

Every count printed on these pages is measured from the tree in the same run that writes
them and re-measured by the gate. `board/` is excluded from its own measurement — a register
that measures itself measures the wrong thing.

```bash
python3 tools/build_board.py            # write the nine pages (also replays the CI gates)
python3 tools/build_board.py --check    # fail if committed board/ is stale
python3 tools/validate_board.py         # the gate
python3 tools/test_board.py             # prove every check fires
```

**Nothing on the board is implemented.** See `board/flagged.html` for the 13 irregularities,
four of them high severity — including FL-13: the rule that is supposed to stop a page
printing a product price never fires, in all four copies of it in this repository.

---

## T63 — reader-first front page (session 10727edd, 2026-11-19)

The live site's front door now reads like a kitchen-gear publication. The audit machinery has moved
behind a single **Behind the site** link.

- **Front page** ([index.html](https://kanlerxz87-cyber.github.io/Zone2/)): leads with all five supplied products. Three air fryers and two meat thermometers each have a sourced spec card and a tagged "(paid link)" button. The disclosure strip sits under the masthead and in the footer.
- **Four new question-shaped guides** in `guides/`: *Instant-read or wireless thermometer?*, *Do you need a thermometer for an air fryer?*, *Multi-function appliance questions*, *Cleanup and counter space*. Together with `guides/meat-thermometers.html` they give the two thermometers reader-facing pages for the first time (F-48).
- **Board** (`suggestions.html`, `questions.html`): owner directions from the brief are quoted verbatim, with their date and source. A suggestion counts as implemented only when such a direction exists (verify_front G5).
- **CI was not running on main from PR #158 to PR #161.** `pages.yml` had conflict markers and could not be parsed (F-45). This is fixed, and `tools/ci_replay.py` now refuses to run on conflict markers or invalid YAML.
- Registers after T72: flags F-01…F-55, 50 sources (S01…S67).

Verification record: [`docs/verification-10727edd.md`](docs/verification-10727edd.md).

## The shop (`shop/`) — 2026-11-19, session `75efdf57` (T66)

`python3 tools/build_shop.py` writes the shop from `shop/data/catalog.json`, `guides.json` and
`briefing.json`; `python3 tools/validate_shop.py` gates it (every row and comparison cell sourced or
blank-with-reason, disclosure strip above `<main>` and in the footer, tagged + sponsored + counted
product buttons, untagged citations, no prices, no invented metrics, canonical, image alt text, feed,
briefing integrity). Guides are written with tokens (`{{v:P-01:Capacity}}`, `{{s:SH-01}}`,
`{{buy:P-04}}`) so a figure in prose is always the sourced value from the catalog, never retyped.
The shared masthead and footer live in `tools/shop_layout.py` and are used by `tools/build_front.py`
too, so the menu is defined once for the whole site. Owner decisions for this round: [`shop/briefing.html`](https://kanlerxz87-cyber.github.io/Zone2/shop/briefing.html).

---

## T72 — final integration: the Decision Room and the design brief (session `arena/1b09bb6d-zone2`, 2026-11-19)

Two owner-facing surfaces the brief asks for by name are now published, and the two pull requests that
carried them — open and untouched for more than eight hours — have been taken over under the board's
60-minute rule, integrated, re-verified and released.

- **[`decision-room.html`](https://kanlerxz87-cyber.github.io/Zone2/decision-room.html)** — 13 decisions
  (9 open · 2 blocked · 1 fixed · 1 advisory), grouped by the question a reader would ask. Every row
  carries the measurement behind it, **what each option costs**, **what each option gives up**, and the
  **single owner answer that unblocks it**. 10 owner questions, 17 cited sources. Nothing applies itself.
  Built by `tools/build_decision_room.py`, gated by `tools/verify_decision_room.py` (D1–D9) and
  `tests/test_decision_room.py` (15 mutation tests — the gate must be able to fail).
- **[`decision-prompt.html`](https://kanlerxz87-cyber.github.io/Zone2/decision-prompt.html)** — the design
  brief the suggestions feed, written to be pasted verbatim: ten constraints, seven principles, and the
  table of unanswered decisions each change depends on.
- **`suggestions.html` / `questions.html`** now separate the *current release* from the *preserved
  history*: the current count and date lead, and the earlier eighteen-row decision board is kept below
  behind its own heading, unchanged.
- **Repaired:** 22 reader-facing row labels were being clipped mid-sentence by a legacy dashboard
  stylesheet rule that loaded on every page (10 on `flagged.html`, 7 on `questions.html`, 5 on
  `publishing.html`), and every `tbody th` rendered uppercase. A scoped reset in
  `assets/css/publication.css` restores wrapping and normal case; re-measured at 0 clipped / 0 uppercase
  across the 15 affected pages.
- **One defect the merge exposed:** both integrated branches had independently allocated the flag id
  `CN-11`. `main` had already published it; the incoming row was renumbered **`CN-17`** so no duplicate
  anchor ships and no existing cross-reference breaks.

**Gates on the combined tree:** `tools/ci_replay.py` **66/66 PASSED** (strict YAML parse enabled) ·
`verify_publication` `ok: true` — 230 HTML pages, 18 indexable, 1 453 sponsored product anchors, 172
current factual rows each with an official source · `audit_site` 7/7 over 230 pages ·
`verify_decision_room` PASS · note-overlap worst pair 0.163 against a 0.25 budget ·
`validate_data` clean (55 flags, 50 sources, 108 rows).

**Verification record:** [`docs/verification-1b09bb6d.md`](docs/verification-1b09bb6d.md) — ten official
sources re-read live on 2026-11-19 with the quoted text beside each published claim.
