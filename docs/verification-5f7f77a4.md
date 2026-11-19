# Verification record — T68, session `arena/5f7f77a4-zone2`

**Date:** 2026-11-19 (UTC) · **Baseline:** `605e49f` (`main`, PR #178 merged)
**Scope:** the five reader-facing product notes in `guides/`, the suggestion and question registers,
and the measurement that motivated the change. Nothing outside that scope was altered.

---

## 1. What this session measured before changing anything

A local replay of the retained workflow (`python3 tools/ci_replay.py`) passed **61/61** steps on the
baseline commit before any edit. `tools/audit_site.py`, `tools/seo_audit.py` and
`tools/build_sitemap.py --check` were also green on the baseline.

**Duplicate content between the five product notes.** Text of each page with `<script>`, `<style>`,
`<nav>`, `<header>`, `<footer>` and `<details>` stripped, split into words, cut into overlapping
8-word shingles, compared pairwise with the Jaccard index (`|A∩B| / |A∪B|`):

| Pair | Baseline | After this session |
|---|---|---|
| `chef-iq-sense` × `thermomaven-instant-read` | **0.389** | 0.163 |
| `chefman-dual-basket` × `chefman-single-basket` | **0.363** | 0.163 |
| `chefman-dual-basket` × `emeril-french-door` | **0.342** | 0.147 |
| `chefman-single-basket` × `emeril-french-door` | 0.333 | 0.147 |
| worst pair overall | **0.389** | **0.163** |

The cause was structural, not stylistic: each note carried the same byline, the same "start with the
job" block, the same link-provenance aside and the same closing read, and differed only in its name,
one intro sentence, one trade-off sentence and five table rows.

**Discoverability of the deployed artifact** (built with `tools/package_site.py`, not counted from the
working tree — the two differ):

| Measure | Count |
|---|---|
| HTML pages in the artifact | 226 |
| Reader URLs in the root sitemap | 16 |
| Pages carrying `noindex,follow` | 187 |
| **Crawlable pages in neither the sitemap nor a robots directive** | **23** |
| — of which `brief/` | 9 |
| — of which `console/` | 8 |
| — of which `discovery/` | 6 |

The 23 are operator dashboards that the packaging step does not mark. Each is reachable, linked and
serves an operator purpose; none is advertised to a crawler. This session did not change that state —
it is recorded as Q68-01 / S68-01 so the choice is made deliberately rather than inherited.

**Titles and descriptions.** All 16 indexable pages carry distinct `<title>`, `<meta name="description">`,
`og:title`, `og:description` and a self-canonical. Sampled and confirmed distinct: `brief/questions.html`
("What we know · Zone2 design brief"), `discovery/measurement.html` ("Measurement contract · Zone2
discovery review"), `console/design.html` ("Redesign pack · Zone2 Owner's Console"), `guides/index.html`,
`shop/index.html`, `marketing/index.html`.

---

## 2. Official sources read on 2026-11-19, and what each was used for

Each was fetched live in this session; none is quoted from memory or from another session's record.

| ID | Source | URL | Used for |
|---|---|---|---|
| `GOOGLE-SPAM` | Google Search Central — Spam policies for Google web search | https://developers.google.com/search/docs/essentials/spam-policies | Doorway abuse ("Creating substantially similar pages that are closer to search results than a clearly defined, browseable hierarchy"); scaled content abuse ("Using generative AI tools … to generate many pages without adding value for users"). Constrains *why* duplication is worth measuring. |
| `GOOGLE-HELPFUL` | Google Search Central — Creating helpful, reliable, people-first content | https://developers.google.com/search/docs/fundamentals/creating-helpful-content | "Does the content draw on other sources … instead of simply copying or rewriting those sources"; the "Who / How / Why" authorship questions. |
| `GOOGLE-SEO` | Google Search Central — SEO starter guide | https://developers.google.com/search/docs/fundamentals/seo-starter-guide | "There are no secrets here that'll automatically rank your site first in Google"; descriptive titles and URLs. |
| `GOOGLE-SNIPPET` | Google Search Central — Control your snippets in search results | https://developers.google.com/search/docs/appearance/snippet | "Create unique descriptions for each page on your site"; the meta description is used only when it describes the page better than the page content itself. |
| `AMZ-POLICIES` | Amazon Associates Central — Associates Program Policies | https://affiliate-program.amazon.com/help/operating/policies | Participation Requirements **6(t)**: no customer reviews or star ratings on your site unless obtained through Creators API or PA API. **6(v)/6(w)**: no obscuring the destination of a link, no link that makes it unclear you are linking to Amazon. Read live: the page states "**Updated: April 14, 2026**". |
| `USDA` | USDA FSIS — Food Thermometers | https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/food-thermometers | Probe placement: 2–3 in of the sensing area through the side of thin food for an instant-read; wireless/smart thermometers are designed to stay in the food at least 1 in deep; poultry is checked in three places (thigh, wing, breast); ice-water calibration at 32 °F after at least 30 seconds; "Do not leave your food thermometer in food while cooking unless the manufacturer's instructions specifically say it can withstand heat". |
| `M1` | Chefman — TurboFry Touch Dual-Window product page | https://chefman.com/products/turbofry-touch-dual-window-air-fryer | The specification rows for P1 (6 Qt / 5.67 L, 200–450 °F, 13.38 × 11.81 × 10.63 in, 13.3 lb, 1700 W/120 V, model RJ38-SQPF-3TDB-2W, dual viewing windows, interior light, nonstick dishwasher-safe baskets, cETL, 1-year assurance). Re-read live: every row matched what the site prints. Note: the page's review widget shows a star average and review counts — **not** copied, per `AMZ-POLICIES` 6(t). |
| `M3` | Emeril Everyday — French Door AirFryer 360 | https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360 | P2 capacity and dimensions. The mode/preset/accessory conflicts (10-in-1 vs 11-in-1, 24 vs 25 presets, 7 vs 6 accessories) remain **blank** on the site, as before. |

### What could not be verified in this session

- **Amazon product-page fetches.** `https://www.amazon.com/dp/<ASIN>` returned HTTP 503 to the sandbox's
  fetcher for all five ASINs on this date (B0CDY277D3 was readable through the page-fetch tool on the
  first attempt, then 503 on repeat). The product rows that cite an Amazon listing are therefore **not
  re-verified here**; they retain the observation dates already printed on them (2026-11-19, earlier in
  the day) and the record of the session that read them. No Amazon value was re-typed from a search
  result or from memory.
- **The live GitHub Pages site.** `https://kanlerxz87-cyber.github.io/` did not complete a TLS handshake
  from this sandbox on 2026-11-19 (connection established to 185.199.111.153, then
  `SSL_ERROR_SYSCALL`). `api.github.com` answered 200, so this is a host-level reachability limit, not a
  site failure. The deployment is instead confirmed through the GitHub API (Pages `status: built`) and
  the workflow run list, and the artifact is verified locally with `tools/verify_publication.py`.
- **Intended ASINs, enrollment, Associates reports, Search Console, real traffic.** Unchanged and still
  blank. Nothing in this session supplies any of them.

---

## 3. What this session changed

1. **`content/publication.json`** — a `reader` block per product: `dek`, `lede`, `fit_for`, `not_for`,
   `tradeoff`, four `checks` (heading + body), `verdict`, `card_line`, `reviewed`. Every product claim in
   that copy traces to a row already in the same product's `specs` or to `USDA`; no new product fact was
   introduced, and no blank became a value.
2. **`tools/publication.py`** — `product_page()` renders the new sections; `card()` uses the per-product
   `card_line` instead of the shared intro; three sources registered (`GOOGLE-SPAM`, `GOOGLE-SEO`,
   `GOOGLE-SNIPPET`); `QUESTIONS` gains Q68-01…Q68-04; `PROPOSALS` gains S68-01…S68-04 (all still
   "Proposed — not implemented"); `CURRENT_FLAGS` gains **CN-11**.
3. **`tools/note_overlap.py`** — new gate. Measures the same shingle/Jaccard property on the built pages
   and exits non-zero at 0.25. Wired into `.github/workflows/pages.yml` immediately after
   `tools/verify_front.py`; the replay count moves 61 → 62.
4. **`assets/css/publication.css`** — styles for the new fit lists, checks and verdict block, including a
   mobile breakpoint. `tools/check_css_urls.py` reports 0 broken `url()` references.
5. **Generated pages** — `index.html`, `shop.html`, `compare.html`, `about.html`, `privacy.html`,
   `guides/*.html`, `suggestions.html`, `questions.html`, `flagged.html`, `workspace.html`,
   `publishing.html`, `executive-summary.html`, `measurement.html`, `intent.html` and `feed.xml`, rebuilt
   through their generators (`tools/build_front.py`, `tools/build_board.py`, `tools/build_brief.py`) —
   not edited by hand.
6. **`EXECUTIVE_SUMMARY.md`** — an append-only dated addendum at the end. Earlier dated sections are
   untouched.

---

## 4. Gates run after the change

| Gate | Result |
|---|---|
| `tools/ci_replay.py` (full workflow replay) | **62/62 steps pass**, including the new duplication gate |
| `tools/verify_front.py` (G1–G10) | pass — 16 pages |
| `tools/verify_publication.py` (artifact contract) | pass — 228 HTML pages, 16 indexable, 1,451 product anchors, 138 current factual rows |
| `tools/audit_site.py` | pass — 228 pages; fragments, spec sources, prose counts, namespaces, disclosure, debris, board |
| `tools/seo_audit.py` | pass — D1–D6; 0 canonical mismatches |
| `tools/build_sitemap.py --check` | current — 16 URLs |
| `tools/build_readiness.py --check` | current — 12 rows, all sourced |
| `tools/note_overlap.py` | worst pair **0.163**, below the 0.25 gate |
| `tools/check_css_urls.py` | 42 stylesheets, 18 local `url()` references, 0 broken |
| Browser verification (inside the replay) | 252 viewport checks, 24 accessibility scans, 0 automated WCAG A/AA findings |

Visual review at 1280 px and 390 px confirmed the new sections render in the publication style and do
not break the mobile layout.

---

## 5. Irregularities raised, not silently fixed

- **CN-11** — the measured duplication above, now repaired and gated. The 0.25 threshold is this
  project's own budget. No search engine publishes an overlap figure, and the page that reports the
  measurement says so.
- **Q68-01** — 23 deployed pages are crawlable but in neither the sitemap nor a robots directive. Three
  options are on the board; none is applied by this session.
- **Amazon 503s and the unreachable Pages host** from this sandbox, recorded above as limits of this
  session's evidence rather than as site failures.
- **The `AMZ-POLICIES` page now states "Updated: April 14, 2026"**, later than the date recorded against
  some earlier flag entries in this repository. The two rules this session relied on (6(t) and 6(v)/6(w))
  were read live on 2026-11-19 and are quoted above; no earlier quotation was re-used.
