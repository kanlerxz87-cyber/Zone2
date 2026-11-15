# Verification record — session `5d6d2254` (T42), 2026-11-15 (UTC)

Scope of this pass: every claim this session **published or relied on**, plus a line-by-line re-read of the
rows behind the three promoted products and the program facts the front door cites. Live fetches were made
on 2026-11-15 through the workspace's page fetcher; the fetch path is not a normal browser and Amazon
serves it a mix of product pages and an anti-bot interstitial, so where a fetch did not return the page,
the row says so rather than borrowing an earlier session's result.

Verdicts: **VERIFIED** = read from the official page this session, matches what the site publishes.
**REPRODUCED** = the behaviour, not a value, was re-observed and matches. **NOT RE-READ** = carried from an
earlier dated record; this session made no claim about it. **DEFECT** = what the site publishes does not
match what the official page says today.

## 1. The three supplied short links

| # | Claim on the site | Observed 2026-11-15 | Verdict | Official source |
|---|---|---|---|---|
| V-1 | `https://link.amazon/B04G1MEwY` resolves to `amazon.com/dp/B0CDY277D3` | Redirect landed on `https://www.amazon.com/dp/B0CDY277D3?lv=shuf&btn_type=ss&gaOptInStatus=true&btn_ref=srctok-6c31d96765b8adfb&channelId=704&plpRedirect=mhFallback`; page `<title>` = "Amazon.com: CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows, Sync Finish, Hi-Fry, Auto Shutoff, 2 Independent 3Qt Nonstick Dishwasher Safe Frying Baskets, Digital Double Air Fryer - Black : Home & Kitchen" | **REPRODUCED + VERIFIED** (destination, title, browse path) | https://link.amazon/B04G1MEwY |
| V-2 | `https://link.amazon/B02NbDxp3` resolves to `amazon.com/dp/B09B7SB46R` | Redirect landed on `https://www.amazon.com/dp/B09B7SB46R?lv=shuf&btn_type=ss&gaOptInStatus=true&btn_ref=srctok-3cf92e5d221f52b6&channelId=704&plpRedirect=mhFallback`; page `<title>` = "Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven \| Countertop Convection Cooker, 24 One-Touch Preset Options, Extra Large Interior, Six Cooking Accessories Included : Home & Kitchen" | **REPRODUCED** (destination) — but the **title is a defect**, see D-1 | https://link.amazon/B02NbDxp3 |
| V-3 | `https://link.amazon/B00hJ57DV` resolves to `amazon.com/dp/B08DKYBTPH` | Redirect landed on `https://www.amazon.com/dp/B08DKYBTPH?lv=shuf&btn_type=ss&gaOptInStatus=true&btn_ref=srctok-1ec41d2839354bef&channelId=704&plpRedirect=mhFallback`; page `<title>` matches the published P3 title verbatim | **REPRODUCED + VERIFIED** | https://link.amazon/B00hJ57DV |
| V-4 | None of the three carries an Associates `tag` parameter | All three resolved URLs above carry `lv`, `btn_type`, `gaOptInStatus`, `btn_ref`, `channelId`, `plpRedirect` and (for P3) `th`; none carries `tag=` | **VERIFIED** — supports F-24 as published | the three resolved URLs |
| V-5 | `btn_ref=srctok-…` rotates per fetch while the destination does not | Three different token values observed across today's fetches (`6c31d96765b8adfb`, `3cf92e5d221f52b6`, `1ec41d2839354bef`), each with a stable destination | **REPRODUCED** — supports F-21 as published | the three resolved URLs |

## 2. The controls

| # | Claim on the site | Observed 2026-11-15 | Verdict | Official source |
|---|---|---|---|---|
| V-6 | `amazon.com/dp/<supplied code>` is "Page Not Found" for all three (F-01, F-02) | `…/dp/B04G1MEwY` → "Page Not Found" (Amazon's error page, "Sorry! We couldn't find that page"); `…/dp/B02NbDxp3` → same; `…/dp/B00hJ57DV` → same | **REPRODUCED 3 of 3** | https://www.amazon.com/dp/B04G1MEwY · https://www.amazon.com/dp/B02NbDxp3 · https://www.amazon.com/dp/B00hJ57DV |
| V-7 | An unknown code on the short-link service returns **a 404** — the decisive control F-20 rests on | `https://link.amazon/NOTACODE9` returned **`403 Forbidden`**, not the 404 page F-20 quotes ("404: File Not Found … You've clicked on an invalid URL", hosted at `amzlinks.in`) | **PARTIALLY REPRODUCED — the conclusion survives, the status code does not.** See D-2 | https://link.amazon/NOTACODE9 |
| V-8 | A valid 10-character ASIN passed to `link.amazon/` also 404s, so the service does not accept ASINs (F-28, E-11, S36) | Not re-run this session | **NOT RE-READ** (carried from session `ba8b2d38`, 2026-11-14) | https://github.com/kanlerxz87-cyber/Zone2/blob/main/revalidation/ |

## 3. Product rows, read off the manufacturer pages today

Every row below is `marketing/data/facts.json`, which is what the reader articles, the comparison table and
the buying guide render. Chefman values come from the manufacturer's own product page; the P2 conflicts come
from the pair of official pages named in the row.

| # | Product | Row published by the site | Official page, read 2026-11-15 | Verdict |
|---|---|---|---|---|
| V-9 | P1 Chefman 6 Qt dual-window | Capacity `6 Qt / 5.67 L` | "• Capacity: 6 Qt / 5.67 L" | **VERIFIED** |
| V-10 | P1 | Power `1700 W / 120 V` | "• Power: 1700W/120V" | **VERIFIED** |
| V-11 | P1 | Temperature range `200–450 °F / 95–235 °C` | "• 200–450°F / 95º-235ºC temperature range" | **VERIFIED** |
| V-12 | P1 | Dimensions `13.38 × 11.81 × 10.63 in / 33.98 × 30 × 27 cm` | "• Dimensions: 13.38 in x 11.81 in x 10.63 in / 33.98 cm x 30 cm x 27 cm" | **VERIFIED** |
| V-13 | P1 | Weight `13.3 lb / 6.03 kg` | "• Weight: 13.3 lbs / 6.03 kg" | **VERIFIED** |
| V-14 | P1 | Model `RJ38-SQPF-3TDB-2W` | "• Model Number: RJ38-SQPF-3TDB-2W" (and the page's own image file names) | **VERIFIED** |
| V-15 | P1 | `cETL approved with a 1-year Chefman assurance` | identical bullet, plus the warranty PDF link | **VERIFIED** |
| V-16 | P1 | `Dual viewing windows with interior light`; `Matte black`; `Nonstick, dishwasher-safe baskets` | "• Dual viewing windows", "• Interior light", "• Matte-black finish", "• Nonstick, dishwasher-safe baskets" | **VERIFIED** |
| V-17 | P1 | Hi-Fry max `450 °F / 235 °C`; Sync Finish `Both baskets finish cooking at the same time` | "• Max temp: 450ºF/ 235ºC with Hi-Fry function"; "• Sync Function so both baskets finish cooking at the same time" | **VERIFIED** |
| V-18 | P3 Chefman 8 Qt | Capacity `8 Qt / 7.57 L`; Dimensions `15.4 × 12.6 × 13.5 in / 39.11 × 32 × 34.29 cm`; Weight `12.8 lb / 5.8 kg`; Model `RJ38-SQSS-8T` | the page sells **two sizes on one product page** ("Capacity: 5 Qt or 8 Qt / 4.73 L or 7.57 L") and gives per-model dimensions, weights and model numbers; each value the site publishes is the *8 Qt model* line, verbatim | **VERIFIED — with a caveat worth publishing (D-3)** |
| V-19 | P3 | `1700 W / 120 V`; `200–400 °F / 95–205 °C`; `4 (fries, chicken, fish, meat)`; `cETL … 1-year`; `Stainless steel`; `LED shake reminder`; auto shut-off `when the timer runs out or the basket is opened` | "• Power: 1700W/120V"; "• 200–400°F / 95º-205ºC temperature range"; "• 4 cooking presets" + description "presets for fries, chicken, fish, and meat"; "• cETL approved with a 1-year Chefman® assurance"; "• Stainless-steel finish"; "an LED shake reminder"; "automatic shutoff … halting cooking whenever the timer runs out or the basket is opened" | **VERIFIED** |
| V-20 | P3 | `Dishwasher-safe basket and rack (manufacturer: top-rack)` | the Features list says "• Top-rack dishwasher-safe **basket**"; the description says "dishwasher-safe **basket and rack**". The site's row states both, labelled by source | **VERIFIED — the row's phrasing is doing exactly the right thing** |
| V-21 | P3 | Hi-Fry max temp row published as **conflict** | Features bullet on the manufacturer page: "Max temp: 400ºF/ 205ºC"; Amazon's title for the same ASIN: "450°F Hi-Fry Option". Both statements are live today | **CONFLICT REPRODUCED** |
| V-22 | P2 Emeril 26 Qt | Capacity `26 Qt / 24.6 L`, "for 4–6 people", `16.9"D × 15.8"W × 14.8"H`, `120 V`, dual-speed fan, French doors, `1 year` | spec tiles read "26-Quart Capacity / preparing food for 4–6 people", "24.6 Liters", "16.9"D x 15.8"W x 14.8"H", "120 volts", "Dual-Speed Fan" | **VERIFIED** |
| V-23 | P2 | Cooking presets published as **conflict**: tile "25 Cooking Pre-sets" vs "24 one-touch" | the manufacturer page's spec tile reads **"25 Cooking Pre-sets"** today; the Amazon title reads **"24 One-Touch Preset Options"** today. The conflict is live on both official pages | **CONFLICT REPRODUCED** |
| V-24 | P2 | Model `4-00675-02A-VN` published as **conflict** | the manufacturer page's price/model line shows `4-00675-02A-VN` today, while its own product-image file names carry `4-00675-02X` | **REPRODUCED** |
| V-25 | P2 | `10-in-1: Air Fry, Bake, Broil, Defrost, Dehydrate, Grill, Proof, Reheat, …` | "This endlessly versatile **10-in-1** air fry convection oven…" — note the page's own carousel asset is named `11-in-1_convection_oven_in_action.png`, which is an internal inconsistency **on the official page**. This session publishes neither count as a spec value; the copy cites the body text only | **VERIFIED (10-in-1), with an observation (D-4)** |
| V-26 | P2 | Included accessories `7 premium accessories`, status `partial`, sourced to the manufacturer page | today's fetch of the manufacturer page returned the spec tiles and the description, **not** the accessories list, so this session could neither confirm nor refute "7"; the Amazon `<title>` for the same model says "**Six** Cooking Accessories Included" | **NOT CONFIRMED THIS SESSION — see D-1** |

## 4. Program facts the front door and the summary rely on

| # | Claim | What the official page says today | Verdict | Source |
|---|---|---|---|---|
| V-27 | The Operating Agreement was updated 2025-10-15 | "**Updated:** October 15, 2025" | **VERIFIED verbatim** | https://affiliate-program.amazon.com/help/operating/agreement |
| V-28 | The disclosure sentence the site carries is the required one | §5: "You must clearly and prominently state the following … on your Site …: **'As an Amazon Associate I earn from qualifying purchases.'**" | **VERIFIED verbatim** | https://affiliate-program.amazon.com/help/operating/agreement |
| V-29 | Links must use Amazon's tagged formats | §1: "The links must properly use the special **'tagged'** link formats we provide and comply with this Agreement ('**Special Links**')." | **VERIFIED verbatim** — the rule F-24 applies to these links | https://affiliate-program.amazon.com/help/operating/agreement |
| V-30 | No income or traffic expectation may be represented | §4: "We do not make any representation, warranty, or covenant regarding the amount of traffic or commission income you can expect at any time…" | **VERIFIED verbatim** — the site publishes no traffic or income figure | https://affiliate-program.amazon.com/help/operating/agreement |
| V-31 | A §5 breach is a material breach; termination is 7 days / immediate for material breach | §6 as published: 7 calendar days' notice; immediate suspension or termination for listed causes; "any violation of Section 5 … will be deemed a material breach" | **VERIFIED verbatim** | https://affiliate-program.amazon.com/help/operating/agreement |
| V-32 | Commission band "Physical Books, Kitchen, Automotive — 4.50%" | Table 1, read today, says exactly that | **VERIFIED** | https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ |
| V-33 | "All Other Categories — 4.00%" | Table 1, read today, says exactly that | **VERIFIED** | same |
| V-34 | Top band 10.00% (Luxury Beauty, Luxury Stores Beauty, Amazon Explore); Coach 0.00%; "Toys, Furniture, Home, … 3.00%" | all three bands read as published today | **VERIFIED** | same |
| V-35 | The three resolved listings sit under "Home & Kitchen › Kitchen & Dining › Small Appliances › Fryers › Air Fryers" | the browse path above each product page read today is exactly that, for P1 and P3 (P2's path was not re-read — the fetch for `…/dp/B09B7SB46R` directly returned the "continue shopping" interstitial) | **VERIFIED for P1 and P3; P2 NOT RE-READ at the listing level** | https://www.amazon.com/dp/B0CDY277D3 · https://www.amazon.com/dp/B08DKYBTPH |
| V-36 | An ASIN is 10 characters | the Associates help page defining the ASIN as "the 10-digit code that Amazon uses to denote specific products" was **not re-read this session**; it is the same source `08789ab3` closed I-A against | **NOT RE-READ** (carried) | https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC |
| V-37 | The deployment address every canonical, og:url and sitemap entry on this site now points at | `https://kanlerxz87-cyber.github.io/Zone2/…` returned HTTP 200 for the landing page and rendered the published hero, product cards and footer | **VERIFIED against the live deployment** | https://kanlerxz87-cyber.github.io/Zone2/ |

## 5. Defects this pass found (published, not silently fixed)

**D-1 — the P2 listing title the site quotes is not the title the listing serves today, and the
accessories count now has two official answers.** `marketing/data/facts.json`, `assets/js/data.js` and the
landing page all publish P2's `title_official` as "… \| 26QT air fryer oven with French doors, 24 cooking
functions, dual-speed fan and rotisserie for easy family meals." The `<title>` at the same URL today is
"Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven \| Countertop Convection Cooker,
24 One-Touch Preset Options, Extra Large Interior, **Six Cooking Accessories Included**". P1's and P3's
published titles reproduce verbatim, so this is not a formatting difference in how this site reads titles:
Amazon serves different title text for that listing at different times. Two consequences, both for the owner
to accept or reject: (a) **a listing title is perishable evidence**, and the "read on 2026-11-14" stamp the
articles already carry is what makes that sentence defensible — re-read before any republication; (b) the
accessories row is published as `7 premium accessories` (status `partial`, sourced to the manufacturer page),
while the Amazon title states six, and this session's fetch of the manufacturer page did not return the
accessories text at all. The row should be re-read end to end and labelled `conflict` with both figures, the
way the preset-count row already is. **Not changed here**: `marketing/**` copy and `ledger/products.json` are
other sessions' scopes, and rewriting a sourced row is exactly what a single session must not do alone.

**D-2 — the control behind F-20 does not reproduce as a 404 through this fetch path.** F-20 is published as
"DECISIVE CONTROL — an unknown link.amazon code returns a 404", quoting the service's "404: File Not Found …
You've clicked on an invalid URL" page at `amzlinks.in`. Today `https://link.amazon/NOTACODE9` returned
`403 Forbidden`. The **conclusion F-20 supports is untouched** — an unknown code does not fall through to a
product page, so the three supplied codes are honoured lookups rather than ignored tokens — but the specific
status code is now known to vary with the client that asks. Suggested wording for the register: "returns an
error (404 for the recorded fetches; 403 through the workspace fetcher on 2026-11-15), never a product
page". Owner-actionable in one line, and it is a wording change to a flag, not to a product fact, so it is
recorded here for whoever owns `ledger/flags.json`.

**D-3 — P3's manufacturer page is a two-variant page.** The 8 Qt values the site publishes are real, but
they sit on a page titled "TurboFry® Touch Stainless-Steel Air Fryer" that sells 5 Qt **and** 8 Qt and prints
per-model bullets ("Dimensions: (5 Qt Model) …", "• Capacity: 5 Qt or 8 Qt …"). The site picks the right line
every time, yet nothing on the page says so. One sentence — "the manufacturer sells this model in two sizes
on one page; every figure here is the 8 Qt line" — removes a way a reader could doubt the row.

**D-4 — the official Emeril page disagrees with itself about the function count.** The body copy reads
"10-in-1"; the page's own carousel asset is named `11-in-1_convection_oven_in_action.png`. The site
publishes the body text and is right to. Recorded because the register already tracks a 24-vs-25 preset
disagreement for this product, and a reader who inspects the page source could find a third number: the
difference is in image naming, so it is an observation, not a spec row.

**D-5 — the crawl layer had drifted, and it is now derived.** Measured on `main` @ `23895e2` before any
edit this session: `sitemap.xml` listed 16 URLs while 39 published pages outside `marketing/` existed plus 18
inside it — the entire reader publication, all four `decisions/` pages and `playbook.html` were unlisted;
`<link rel="canonical">` existed on 18 of 78 pages. `tools/build_sitemap.py` now generates the sitemap from
the tree and `tools/audit_site.py` gained a stray-marker check that caught **two `EAD` lines rendering as
visible text inside the landing page footer**, plus three in `EXECUTIVE_SUMMARY.md` — a heredoc tail left by
an earlier shell patch. The footer also carried a duplicated "Suggestions board" entry and two labels
("Counter Notes", "Field Notes") pointing at the same URL; all repaired this session.

## 6. What this pass did not check

- Nothing about **price, rating, review count, availability or Best Sellers Rank** was looked up or copied,
  because the site publishes none of them (Program Policies; `sources.html` "Which claims these sources
  cannot support"). Manufacturer pages do display their own store prices and aggregate review counts; that is
  precisely the decision DS-06 / Q-12 keeps open, and no figure of either kind was transcribed here.
- `ledger/**`, `tools/build_marketing.py` copy, `journal/**` prose, and the four companion namespaces were
  not audited beyond the head metadata this session added; the 2026-11-14 per-row registers
  (`docs/verification-8c4236ad.md`, `docs/verification-42fa4918.md`, `review-2026-11-15.html`) remain the
  detailed record for those surfaces.
- No claim is made about ranking, indexing, traffic or conversion. Amazon's own agreement (§4, V-30) makes no
  representation about traffic, and neither can this page: the sitemap and canonical work changes what a
  crawler is *told*, which is checkable in the files; what a crawler *does* with it is not measured here and
  no number is attached to it.
