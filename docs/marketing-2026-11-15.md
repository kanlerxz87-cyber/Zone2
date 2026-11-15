# T38 — marketing site: verification record (2026-11-15)

Session `arena/e8b071cd-zone2` (`e8b071cd`). Scope: the consumer-facing publication in `marketing/`,
the six question-shaped guides it now publishes, and the improvement board at
[`marketing/improvements.html`](https://kanlerxz87-cyber.github.io/Zone2/marketing/improvements.html).

This file is the line-by-line record: what was fetched, what the official page says, what was published,
and what was deliberately not published. Nothing here is inferred; where a value could not be read off an
official page it is listed under *Not published*.

## 1. The three supplied links, re-tested today

Each was fetched on 2026-11-15 and the resolved destination recorded. Prior sessions reached the same
destinations on 2026-11-13 and 2026-11-14; the result reproduces them.

| # | Supplied | Resolved to (2026-11-15) | Page title as served | Flags on the resolved URL |
|---|---|---|---|---|
| 1 | `https://link.amazon/B04G1MEwY` | `https://www.amazon.com/dp/B0CDY277D3` | "Amazon.com: CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows, Sync Finish, Hi-Fry, Auto Shutoff, 2 Independent 3Qt Nonstick Dishwasher Safe Frying Baskets, Digital Double Air Fryer - Black : Home & Kitchen" | `plpRedirect=mhFallback`, `lv=shuf`, `channelId=704`, `btn_ref=srctok-7dce8b124ae972c6` |
| 2 | `https://link.amazon/B02NbDxp3` | `https://www.amazon.com/dp/B09B7SB46R` | "Amazon.com: Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven \| Countertop Convection Cooker, 24 One-Touch Preset Options, Extra Large Interior, Six Cooking Accessories Included : Home & Kitchen" | `plpRedirect=mhFallback`, `btn_ref=srctok-1b5b6494c3cb1f18` |
| 3 | `https://link.amazon/B00hJ57DV` | `https://www.amazon.com/dp/B08DKYBTPH` | "Amazon.com: Chefman Air Fryer 8 Qt \| TurboFry® 4-in-1 with 450°F Hi-Fry Option for Crispier Results \| Bake, Dehydrate, Frozen \| XL Nonstick Dishwasher-Safe Basket \| Stainless Steel : Home & Kitchen" | `plpRedirect=mhFallback`, `btn_ref=srctok-4fac96cb28cd27fc` |

- All three breadcrumbs read **Home & Kitchen › Kitchen & Dining › Small Appliances › Fryers › Air Fryers**
  ([1](https://www.amazon.com/dp/B0CDY277D3), [2](https://www.amazon.com/dp/B09B7SB46R),
  [3](https://www.amazon.com/dp/B08DKYBTPH)) — the single-category finding recorded by earlier sessions holds.
- **The `btn_ref` value differs from the one recorded on 2026-11-14 and all three differ from each other
  today.** That is the per-request shuffle already recorded in the flag register; it is re-stated here
  because it is the reason no destination can be treated as a stable per-link mapping.
- No `tag=` parameter appears on any resolved URL. The links as supplied cannot earn (register flag **F-07**).

## 2. Manufacturer pages, re-read today

| Source | URL | What the page states today | Used by |
|---|---|---|---|
| M1 — Chefman, 6 Qt Dual-Window | https://chefman.com/products/turbofry-touch-dual-window-air-fryer | Title "TurboFry® Touch 6 Qt. Dual-Window Air Fryer"; model line `RJ38-SQPF-3TDB-2W`; "Max temp: 450ºF/ 235ºC with Hi-Fry function"; "Sync Function so both baskets finish cook…"; two independent 3 qt baskets | `articles/p1.html`, `topics/how-many-quarts-do-you-need.html`, `topics/dual-basket-or-one-big-basket.html`, `topics/what-hi-fry-actually-does.html` |
| M3 — Emeril Everyday, French Door AirFryer 360 | https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360 | Spec tiles: "26-Quart Capacity / preparing food for 4–6 people", "24.6 Liters", "16.9"D x 15.8"W x 14.8"H", "120 volts", "25 Cooking Pre-sets", "Dual-Speed Fan for golden fried crisping"; description calls it a "10-in-1 air fry convection oven"; model line `4-00675-02A-VN` | `articles/p2.html`, `topics/basket-or-fryer-oven.html`, `topics/why-two-official-pages-disagree.html`, `topics/will-it-fit-your-counter.html` |
| M5 — Chefman, 8 Qt TurboFry Touch | https://chefman.com/products/turbofry-touch-air-fryer-1 | "presets for fries, chicken, fish, and meat"; "temperatures ranging from 200–400°F"; "98% less oil"; "LED shake reminder"; "automatic shutoff … halts cooking whenever the timer runs out or the basket is opened"; "Designed for 4-6 people"; model `RJ38-SQSS-8T`; one URL sells both **8 Quart and 5 Quart** via a size selector | `articles/p3.html`, `topics/dual-basket-or-one-big-basket.html`, `topics/what-hi-fry-actually-does.html` |

Amazon-side rows (M2 / M4 / M6) are the three listing pages in §1; the power and temperature figures for the
Emeril are taken from Amazon's product-information block because the manufacturer page prints no wattage.
That is stated in the table on the guide, not buried.

## 3. Sources used for the recommendations on the improvement board

Recommendations are judgements, so they cite the primary documentation rather than an SEO blog.

| Claim on the board | Official source | Verified |
|---|---|---|
| Affiliate/paid links should carry `rel="sponsored"`; `sponsored` is preferred over `nofollow` for paid placements | https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links | 2026-11-15 |
| Review markup: pages where the reviewed entity controls the reviews about itself are ineligible (the "self-serving" restriction); Google's own review-snippet page carries the anchor and the Product/Review nesting this site declines to use | https://developers.google.com/search/docs/appearance/structured-data/review-snippet (see `#self-serving`) | 2026-11-15 |
| Sitemaps are the recommended way to tell Google about changes | https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap (linked from the review-snippet page's step 5) | 2026-11-15 |
| People-first content: be clear who created content, how, and why | https://developers.google.com/search/docs/fundamentals/creating-helpful-content | 2026-11-15 |
| "Create the content yourself … Don't just recycle what others on the internet have already said, or could easily be produced by a generative AI model." | https://developers.google.com/search/docs/fundamentals/ai-optimization-guide | 2026-11-15 |
| Mandatory disclosure sentence; 7-day termination on notice; no traffic or income representation; Special Links and sub-tag rules | https://affiliate-program.amazon.com/help/operating/agreement and https://affiliate-program.amazon.com/help/operating/policies | transcribed 2026-11-14 by T28 (`ledger/compliance.json`, R-01…R-31) — **not re-read today**, see §5 |
| Category rate bands and the bounty/bonus appendix | https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ | transcribed 2026-11-14 by T28 — not re-read today |

## 4. Gates run on this branch

| Gate | Command | Result |
|---|---|---|
| Marketing output is generated, not hand-edited | `python3 tools/build_marketing.py --check` | pass — 20 outputs (17 pages + sitemap.xml, robots.txt, feed.xml) |
| Marketing set (G1–G14) | `python3 marketing/scripts/verify_marketing.py` | pass — 17 pages · 48 spec rows · 0 failures |
| Pages subpages | `python3 tools/build_site.py --check`, `python3 tools/validate_data.py` | pass — 39 pages, 0 errors, ids unique (38 flags / 82 checks / 37 sources) |
| Root views + executive summary | `tools/build_root_views.py --check`, `tools/build_summary.py --check` | pass, no drift |
| Platform pipeline | `python3 tests/test_pipeline.py` | pass — 15/15 |
| Structural audit (fragments, spec sources, prose counts, namespaces, disclosure) | `python3 tools/audit_site.py` | pass — 105 published pages audited |
| Companion sites | `revalidation/scripts/{build,verify}.py`, `affiliate-lab/scripts/verify_site.py`, `research-hub/scripts/verify.py` | pass — untouched by this session |

### Negative tests on the five new gates (T38)

A gate that cannot fail is decoration. Each new rule was broken on purpose and confirmed to catch it:

| Gate | Injected defect | Result |
|---|---|---|
| G11 sourced claims | emptied `data-src` on a guide claim | caught |
| G12 banned phrases | inserted "In today's fast-paced world," | caught |
| G12 labelled opinion | removed the take-box label | caught |
| G12 no first-hand claims | inserted "We tested this for three weeks." | caught |
| G13 no orphans | unlinked a guide from every page | caught |
| G14 sitemap coverage | removed a page from `sitemap.xml` | caught |

The no-price gate (G4) caught this session's own illustration: the negative example in the writing
standard quoted a dollar figure. The example was rewritten; the gate was not weakened.

## 5. Irregularities and limits (published, not blocking)

1. **The board file carried unresolved conflict markers on `main`.** `COORDINATION.md` lines added by the
   merge of PR #60 (`e030c40`) contained a stray `=======` and `>>>>>>> origin/main` between the `e9c8362c`
   and `d3ce1c29` records. The marker lines are artefacts, not content; both records are intact. This
   session deleted the two marker lines only, in a separate commit.
2. **Table 1 / Appendix and the compliance rules on the board are carried, not re-read.** Every
   programme figure quoted on `marketing/improvements.html` is a pointer to a ledger transcription dated
   2026-11-14 (T28). This session re-read only the Amazon/manufacturer product pages and the four Google
   documentation pages listed in §3. Nothing was presented as re-verified today that was not.
3. **Emeril model-suffix drift, newly observed.** The manufacturer store's own product-image file names
   contain `4-00675-02X` — the suffix Amazon's specification block publishes — while its model line reads
   `4-00675-02A-VN`. Recorded as `verified_today` T-08 and published as a conflict; **not** added to
   `ledger/flags.json` because that file is not in this session's claimed scope. Change request **CR-8**
   on `COORDINATION.md` asks the ledger owner to fold it in.
4. **Manufacturer pages publish prices and aggregate ratings; this site publishes neither.** Both are
   withheld by policy, and the decision to allow manufacturer-sourced ratings is open on the board
   (DS-06 / MQ-05). Ratings were deliberately not transcribed into this file either, so no page can pick
   the number up by accident.
5. **The T27 board row still reads `in progress`** although the closing record in the same file marks T27
   done. Already flagged by session `2499438c` on 2026-11-15; not edited here.
6. **`marketing/data/editorial.json` carries the copy.** Editorial judgement lives in data so the gate can
   check it and the owner can diff it. The `decision` fields on the board are empty by design until the
   owner records a choice.

## 6. Not published, and why

| Item | Status | Reason |
|---|---|---|
| Price of any of the three products | withheld | Amazon's content restrictions; the deploy gate fails on a money value in a buying context |
| Star rating / review count (Amazon or manufacturer) | withheld | Volatile, storefront-specific; no `Review`/`AggregateRating` markup either (DS-07) |
| Inner-basket material for P1 | blank | The Amazon product-information block did not render it; the manufacturer page does not state it in those words |
| UPC for all three | blank | Not stated on any official page read |
| Minimum ventilation clearance for all three | blank | Not stated on any product page read; only the manual would carry it, and no manual was read |
| Servings figure for P1 | blank | The manufacturer page publishes capacity and basket count, not a household size |
| Full accessory list for P2 | partial | The page names three of the seven it counts |
| "Tested", "reviewed in our kitchen", "our team" | never | Nobody has used these products; the gate fails the build on that claim class |

## 7. Second merge, and a page that was not generated (2026-11-15, later in the day)

While this PR was open, `main` took three more merges. One of them put a **hand-written HTML page inside this
namespace**: `marketing/trending-topics.html` (session `bf8f07a7`, PR #65) — a queue of six article shapes plus a
list of reasons they would earn traffic, written under the old sidebar shell.

It is kept, and it is now generated. Same URL, same proposals, rendered from `marketing/data/editorial.json` →
`trending`, so the page inherits the masthead, the disclosure, the scope note, the canonical URL and the sitemap —
and so a later rebuild cannot quietly undo it. Three changes were made to its content, all of them stated on the
page itself under "How this page got here":

| Change | Why |
|---|---|
| The traffic rationale is labelled an **editorial hypothesis** | it asserted how Google ranks pages and how shoppers behave; nothing here can verify that, and the site's own rule is that a claim either has a source or is labelled as judgement |
| "Capacity is the #1 spec shoppers filter on" → the row now says what the pages publish | same reason; a ranking we cannot cite is not a fact |
| The energy row's wattage | My first pass at this merge wrote "1500 W and 1800 W on the Emeril's two official blocks". **No official page states either number.** All three products publish **1700 W** (P1 · P2 · P3, `facts.json`), and 120 V. The row was corrected before commit, and the error is recorded on the page — an invention caught by re-reading the data file is exactly what the row-sourcing rule is for |

Two mechanical fixes came with it: `sitemap.xml` is now derived from the page registry instead of a typed list
(a hand-maintained list is how F-26-style drift starts), and the hub links the queue so the new page is not an
orphan under G13.

Task id: this session renumbered again — **T33 was taken** by session `fcb538fa` in prose while my row was being
merged, so the work ships as **T38**.
