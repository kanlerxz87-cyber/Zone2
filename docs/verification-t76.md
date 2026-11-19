# Verification record — T76 final integration remeasurement

**Date:** 2026-11-19 (UTC)
**Branch:** `arena/f8c77723-zone2`
**Scope:** remeasurement of PR #194's current reader-facing claims against a locally packaged Pages artifact after integrating main's latest merged tip. This is a repository/artifact check, **not** a live-site fetch, Search Console report, or product/account verification. No product fact, intended ASIN, observation, campaign metric, or owner-only blank was changed.

All counts below are reproducible from committed builders and the ignored `_site/` artifact. The current decision rows cite this record rather than treating older T69 measurements as current.

---

## M1 — publication table row-label CSS

<a id="m1"></a>

**Method.** Run `python3 tools/package_site.py`, then use Playwright/Chromium at 1440×900 and 390×844 on every packaged HTML page containing `.cn-table tbody th`. For each body row-header cell, compare `scrollWidth`/`clientWidth` and `scrollHeight`/`clientHeight`, and read computed `white-space` and `text-transform`.

**Result in the packaged artifact:** **14 pages, 173 row-header cells, 0 clipped, 0 uppercase, 0 `nowrap` at both 1440×900 and 390×844.** The 14 page counts are:

| Packaged page | `tbody th` cells |
|---|---:|
| `compare.html` | 23 |
| `decision-prompt.html` | 12 |
| `decision-room.html` | 10 |
| `executive-summary.html` | 7 |
| `flagged.html` | 72 |
| `guides/chef-iq-sense.html` | 4 |
| `guides/chefman-dual-basket.html` | 5 |
| `guides/chefman-single-basket.html` | 5 |
| `guides/emeril-french-door.html` | 5 |
| `guides/thermomaven-instant-read.html` | 4 |
| `intent.html` | 5 |
| `measurement.html` | 5 |
| `publishing.html` | 5 |
| `questions.html` | 11 |
| **Total** | **173** |

The scoped `.cn-table` reset in `assets/css/publication.css` remains in the packaged stylesheet. This is a remeasurement of the repair; the table data and labels were not changed.

---

## M2 — packaged robots, sitemap, and shop-front links

<a id="m2"></a>

**Method.** Run `python3 tools/package_site.py`; parse every `_site/**/*.html` `meta[name=robots]` and canonical; parse `_site/sitemap.xml`; URL-resolve relative and `/Zone2/` base-path links found inside `<main>`, excluding repeated masthead/footer chrome, and map directory routes to `index.html`. For the four indexability examples below, count whitespace-separated text tokens and table rows within `<main>`, plus `a.pb-src` links.

**Result:**

- `_site/` contains **230** HTML pages: **18 `index,follow`** and **212 `noindex,follow`**.
- The 18 canonical URLs for the indexable pages match the sitemap's 18 `<loc>` entries exactly. The site-root URL is the canonical for `index.html`; it is counted once, not added as a nineteenth URL.
- Excluding shared chrome, **17** packaged pages link from their main content to `shop/index.html`; **2** link from main content to `shop.html`. These are page counts (at least one main-content link), not counts of all repeated sitewide navigation links.
- `shop.html` is indexable and in the sitemap. `shop/index.html` is `noindex,follow` and absent from the sitemap. Their packaged H1s are “Find the format that fits your routine.” and “Five pieces of kitchen gear, explained before you buy.” They are distinct shop front doors; the choice of canonical URL remains an owner decision and this report applies neither option.

The 18 indexable pages include `decision-room.html` and `decision-prompt.html`. The older 16-page references in T69-era records are superseded for the current packaged artifact.

**Product-page comparison used by DR-02.** Table-row totals below include each table's header row; the source-link count is the number of `a.pb-src` anchors inside `<main>`.

| Packaged page | Robots | Main words | Tables | `<tr>` rows | Official-source links |
|---|---|---:|---:|---:|---:|
| `shop/chefman-6-qt-dual-basket-air-fryer.html` | noindex | 779 | 2 | 20 (18 body + 2 headers) | 16 |
| `guides/chefman-dual-basket.html` | index | 653 | 1 | 6 (5 body + 1 header) | 9 |
| `shop/thermomaven-1-second-instant-read-meat-thermometer.html` | noindex | 603 | 2 | 20 (18 body + 2 headers) | 15 |
| `guides/thermomaven-instant-read.html` | index | 663 | 1 | 5 (4 body + 1 header) | 8 |

These current counts do not support the older statement that both indexable guides are shorter. The ThermoMaven guide has more main-content words than its shop-local product page; the shop page's table and source-link counts are separate facts, not a quality or ranking conclusion.

---

## M3 — RSS source files versus deployed artifact

<a id="m3"></a>

**Method.** Parse each source XML and packaged XML with Python's `xml.etree.ElementTree`; compare the packaged feed bytes and each item's title/link. Separately, verify that each shop-local guide and its root counterpart exists in `_site/`, then count whitespace-separated text tokens inside each page's `<main>`.

| Feed path | Source-tree item count | Packaged item count | Packaged result |
|---|---:|---:|---|
| `feed.xml` | 5 | 5 | Root guide feed |
| `shop/feed.xml` | 6 | 5 | Byte-identical to packaged `feed.xml` |
| `marketing/feed.xml` | 16 | 5 | Byte-identical to packaged `feed.xml` |

`tools/package_site.py` replaces nested `feed.xml` files with the root `pub.feed()` output. Thus, the packaged artifact has three feed URLs serving the same five-item document; it does **not** serve the six- and sixteen-item source feeds, and those packaged feeds do not point to separate shop-local article URLs. The duplicate shop-local guide pages themselves remain a separate URL/content decision and are not removed by this packaging behavior.

**Separate page-URL issue.** Five overlapping question topics still have a root guide and a shop-local guide at different paths. Their main-content word counts are measurements, not a quality or ranking score:

| Topic | Root guide (`<main>` words) | Shop-local guide (`<main>` words) |
|---|---|---|
| Basket or oven-style air fryer | `guides/basket-or-oven.html` — 936 | `shop/guides/basket-or-oven-air-fryer.html` — 837 |
| Air-fryer capacity | `guides/air-fryer-capacity.html` — 803 | `shop/guides/air-fryer-capacity-checklist.html` — 640 |
| Cleanup and counter space | `guides/cleanup-and-counter-space.html` — 788 | `shop/guides/cleanup-and-counter-space.html` — 628 |
| Multi-function appliance checklist | `guides/multi-function-appliance-checklist.html` — 758 | `shop/guides/multi-function-appliance-questions.html` — 542 |
| Instant-read or wireless thermometer | `guides/instant-read-or-wireless.html` — 739 | `shop/guides/instant-read-vs-wireless-meat-thermometer.html` — 698 |

Two pairs share the same H1 text; the other three titles differ. Page length alone does not establish which URL is more useful. The owner decision about which URL to retain or canonicalize remains open.

---

## M4 — Workspace links in the reader chrome

<a id="m4"></a>

**Method.** Count `<a href>` elements and unique destinations under `.cn-menu-links` and `.cn-footer-tool-grid` in packaged pages. The homepage's total anchor count is read from Chromium's parsed DOM at 390×844.

**Result:**

- Each of the **37** current `body.cn-publication` pages has **70 unique Workspace links** in the masthead's collapsible Workspace group and the same **70 unique links** in the footer's Workspace section.
- Chromium reports **200** `a[href]` elements in the packaged homepage DOM at 390×844. This is a DOM count, not a count of raw `<a>` text in source files.
- All 230 packaged pages have the 70-link Workspace menu, while the 193 archived pages use a compact archive footer rather than the 70-link footer grid. The repeated 70/70 count therefore describes the 37 current publication pages, not every archived page.

The four intended reader links are Shop, Buying guides, Compare, and Our approach. At 390px, the first three appear in the primary nav and Our approach is hidden by the mobile CSS; that separate navigation choice remains open in DR-12.

---

## M5 — mobile paid-link targets

<a id="m5"></a>

**Method.** At 390×844, load every packaged page containing `.cn-retailer-link` in Playwright/Chromium. Read `getBoundingClientRect()`, computed `min-height`, visibility, and `rel` for every link.

**Result:** **29 controls across 8 packaged pages**; every visible control measures **141.546875 × 44 CSS px**, has computed `min-height: 44px`, and carries `rel="sponsored"`. No undersized or unsponsored control was found in this set. The earlier 142×18 measurement in T69-era material does not describe the current packaged artifact; this integration remeasured the existing rule and did not add or change it.

The measured dimensions exceed the 24×24 CSS-pixel target in [W3C WCAG 2.2 SC 2.5.8](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html). This is a control-size result only, not a claim that the whole site conforms to WCAG.

---

## M6 — owner-only fields and scope limits

<a id="m6"></a>

No source in this measurement establishes which product the owner intended for a submitted short link, whether the Associates account is enrolled for the tested workflow, or what a first-party report contains. Those fields remain blank or flagged for owner review. Measured redirect targets remain separate from intended ASINs. No link is labeled invalid from these artifact checks.

---

## V — local validation (not a deployment confirmation)

- `.venv/bin/python tools/ci_replay.py` — **66/66 workflow steps passed**, with PyYAML available for the strict workflow parse. This includes the source/data gates, builders, mutation tests, reader-surface gates, packaging, and browser checks.
- The packaged contract reports **230 HTML pages, 18 indexable URLs, 1,463 product anchors checked, and 172 current factual rows**; `ok: true`, with no errors. This is distinct from the 173 `.cn-table tbody th` cells measured in M1.
- Structural audit: **7/7 checks passed** across 230 published pages. The front-page and shop gates also passed.
- Browser run: **256 viewport checks, 26 mobile accessibility pages, and 11 behavior/privacy checks passed**. The regression now explicitly checks the 70/70 Workspace link sets, 200 homepage DOM anchors, 44px retailer controls, and publication-table row-label overflow/case at the mobile viewport.

These are local build-artifact results. They do **not** establish that the replacement PR is merged or that GitHub Pages has deployed it; those require a separate post-merge check.
