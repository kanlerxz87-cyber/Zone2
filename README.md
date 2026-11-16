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

### Findings & verified subpages — `pages/`

37 generated pages, one table per question, **every row ending in an official-source link or an explicit
blank + flag**: [findings hub](https://kanlerxz87-cyber.github.io/Zone2/pages/index.html) ·
[executive summary](https://kanlerxz87-cyber.github.io/Zone2/pages/executive-summary.html) ·
[requested products](https://kanlerxz87-cyber.github.io/Zone2/pages/products.html) ·
[commission bands, 11 category subpages](https://kanlerxz87-cyber.github.io/Zone2/pages/categories/index.html) ·
[niche discovery](https://kanlerxz87-cyber.github.io/Zone2/pages/niches.html) ·
[platform modules, 12 subpages](https://kanlerxz87-cyber.github.io/Zone2/pages/modules/index.html) ·
[compliance control ledger](https://kanlerxz87-cyber.github.io/Zone2/pages/compliance.html) ·
[verification log (104 checks, V-01…V-104)](https://kanlerxz87-cyber.github.io/Zone2/pages/verification.html) ·
[source register (43 sources, S01…S43)](https://kanlerxz87-cyber.github.io/Zone2/pages/sources.html) ·
[tracking](https://kanlerxz87-cyber.github.io/Zone2/pages/tracking.html) ·
[content engine](https://kanlerxz87-cyber.github.io/Zone2/pages/content-engine.html) ·
[architecture](https://kanlerxz87-cyber.github.io/Zone2/pages/architecture.html) ·
[flagged for review (41 flags, F-01…F-41)](https://kanlerxz87-cyber.github.io/Zone2/pages/flags.html)

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

## The three supplied links — read this before using any product data

`https://link.amazon/B04G1MEwY` · `https://link.amazon/B02NbDxp3` · `https://link.amazon/B00hJ57DV`

Every session agrees on the measurements: each embedded token is **9 characters** (Amazon defines an ASIN as
a unique **10-character** identifier), and `https://www.amazon.com/dp/<token>` returns *Sorry! We couldn't
find that page* for all three.

Earlier sessions concluded from the redirect alone that the destinations were *arbitrary fallback pages*.
**On 2026-11-14 that reasoning was tested and corrected** (see `revalidation/`). The measurements now read:

| Observation | Result |
|---|---|
| Redirect target | three **different** ASINs (`B0CDY277D3`, `B09B7SB46R`, `B08DKYBTPH`), each a live product page |
| Redirect markers | every target carries `plpRedirect=mhFallback` and `lv=shuf` |
| Same-day re-fetch | **Corrected 2026-11-14:** re-fetched twice, the link returned the same `/dp/` path and the same page body — the "shuffle" is not reproducible. **Cross-day re-fetch (2026-11-14, session a133aa61):** same ASIN and body again, but the `btn_ref` token **differs** for all three links, so the token is per-day, not per-link-stable (flag **F-21**). See `revalidation/`. |
| Control (added 2026-11-14) | A **bare, untagged** request to a *valid* ASIN (`/dp/B08DKYBTPH`) is also answered with `plpRedirect=mhFallback&lv=shuf` appended. The marker is therefore not evidence of a fallback. |
| Associates tag | absent from all three resolved URLs — under OA §1 a Special Link must use Amazon's tagged format, so as supplied these links cannot be relied on to attribute commission. |

**What this does and does not settle.** The supplied codes are not ASINs, so the codes alone identify
nothing. But each `link.amazon` URL is a stable, individually tracked link resolving to one consistent
product — three distinct per-link tokens, identical on re-fetch. The earlier claim that the destinations
*change content and token between requests* is **not reproducible**, so the destinations are **not** shown to
be arbitrary fallbacks. The product pages elsewhere in this repository are therefore accurate **about those
three ASINs** (each row cites the manufacturer's own page), and they are the products these links resolve to.

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
