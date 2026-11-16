# Verification record — T50 — session `arena/9251f262-zone2` — 2026-11-16 (UTC)

Method: every source below was **fetched live on 2026-11-16** and compared, string by string, against
the value this repository stores for it. Nothing here is carried over from another session's record.

**Channel note.** Shell `curl` in this workspace fails outbound TLS on every non-GitHub host
(`OpenSSL SSL_connect: SSL_ERROR_SYSCALL`) — re-confirmed at the start of this session against
`affiliate-program.amazon.com`, `developers.google.com`, `www.ftc.gov`, `link.amazon` and
`www.amazon.com`. Every live read below therefore used the `fetch_page` tool, and every GitHub/Pages
statement used `gh` / the GitHub API. No value in this document was assumed because a fetch failed.

---

## 1. The three supplied short links

| Supplied link | Stored destination (`ledger/products.json`) | Destination observed 2026-11-16 | Match |
|---|---|---|---|
| `https://link.amazon/B04G1MEwY` | `https://www.amazon.com/dp/B0CDY277D3` | `https://www.amazon.com/dp/B0CDY277D3?lv=shuf&btn_type=ss&gaOptInStatus=true&btn_ref=srctok-68884e8aa630b24a&channelId=704&plpRedirect=mhFallback` | **yes** |
| `https://link.amazon/B02NbDxp3` | `https://www.amazon.com/dp/B09B7SB46R` | `https://www.amazon.com/dp/B09B7SB46R?lv=shuf&btn_type=ss&gaOptInStatus=true&btn_ref=srctok-662480f5bd825c83&channelId=704&plpRedirect=mhFallback` | **yes** |
| `https://link.amazon/B00hJ57DV` | `https://www.amazon.com/dp/B08DKYBTPH` | `https://www.amazon.com/dp/B08DKYBTPH?lv=shuf&btn_type=ss&gaOptInStatus=true&btn_ref=srctok-38bef00eb1e962ef&channelId=704&plpRedirect=mhFallback&th=1` | **yes** |

`btn_ref` values are new again today, and the destinations are unchanged — the fourth consecutive
date this has held. `channelId=704` and `plpRedirect=mhFallback` are present on all three, as before.
No resolved URL carries a `tag=` parameter, which is flag **F-24** and is still open.

Browse path observed on all three: `Home & Kitchen › Kitchen & Dining › Small Appliances › Fryers ›
Air Fryers` — identical to the stored `category_path`.

### Listing titles as served today, against the stored titles

| Product | Stored title | Title served 2026-11-16 | Result |
|---|---|---|---|
| P-01 `B0CDY277D3` | `CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows, Sync Finish, Hi-Fry, Auto Shutoff, 2 Independent 3Qt Nonstick Dishwasher Safe Frying Baskets, Digital Double Air Fryer - Black` | identical | **match** |
| P-02 `B09B7SB46R` | `Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven \| 26QT air fryer oven with French doors, 24 cooking functions, dual-speed fan and rotisserie for easy family meals.` | `Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven \| Countertop Convection Cooker, 24 One-Touch Preset Options, Extra Large Interior, Six Cooking Accessories Included` | **DRIFT** |
| P-03 `B08DKYBTPH` | `Chefman Air Fryer 8 Qt \| TurboFry® 4-in-1 with 450°F Hi-Fry Option for Crispier Results \| Bake, Dehydrate, Frozen \| XL Nonstick Dishwasher-Safe Basket \| Stainless Steel` | identical | **match** |

**Irregularity V-1 (published, not silently corrected).** The second half of P-02's Amazon title has
changed since it was recorded. The stored wording (`24 cooking functions, dual-speed fan and
rotisserie for easy family meals`) is no longer what the page serves. Two consequences, and only two:

* the stored *title* is stale;
* no **specification row** on this site is affected — the capacity, dimensions, voltage, temperature
  range, cooking modes, door and fan facts are all read from the manufacturer page and were
  re-confirmed below.

It is logged rather than overwritten because this repository's record is supposed to show what was
read and when, and a silent edit would destroy that. Owner action: none required for accuracy; the
row should be refreshed on the next ledger pass. Cross-scope request **R-3** in `COORDINATION.md`
covers the `ledger/products.json` edit this session did not make.

---

## 2. Manufacturer pages (the source of every specification row)

| Source | URL | Read 2026-11-16 | Result |
|---|---|---|---|
| S25 Chefman 6 Qt dual-window | <https://chefman.com/products/turbofry-touch-dual-window-air-fryer> | yes | **match** |
| S26 Chefman 8 Qt TurboFry Touch | <https://chefman.com/products/turbofry-touch-air-fryer-1> | yes | **match** |
| S27 Emeril French Door AirFryer 360 | <https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360> | yes | **match** |

What each page stated today, against the stored rows:

* **S25** — model `RJ38-SQPF-3TDB-2W`; page title `Chefman® TurboFry® Touch Dual-Window Air Fryer`;
  **"Max temp: 450ºF/ 235ºC with Hi-Fry function"**; **"Sync Function so both baskets finish cook…"**.
  Matches the stored `Hi-Fry maximum = 450 °F / 235 °C` and `Sync Finish` rows.
* **S26** — model `RJ38-SQSS-8T`; page title `CHEFMAN® 8 Qt. TurboFry® Touch Air Fryer – Chefman`;
  **"precise temperatures ranging from 200–400°F"**, presets **fries, chicken, fish, and meat**,
  **"dishwasher-safe basket and rack"**, **"automatic shutoff"**, **"LED shake reminder"**. Matches
  the stored rows exactly, and matches the stored conflict note: the manufacturer says 200–400 °F
  while the Amazon title says *450°F Hi-Fry Option*.
* **S27** — model `4-00675-02A-VN`; page title `EMERIL LAGASSE FRENCH DOOR AIRFRYER 360™ TOASTER OVEN
  COMBO, 26 QT`; spec tiles read **26-Quart Capacity / preparing food for 4–6 people**,
  **Dual-Speed Fan**, **25 Cooking Pre-sets**, **16.9"D x 15.8"W x 14.8"H**, **24.6 Liters**,
  **120 volts**. Matches the stored rows, and reproduces the stored conflict exactly: the
  manufacturer's own spec tile says **25** pre-sets while the Amazon listing title says **24
  One-Touch Preset Options**. That conflict is published as a conflict on this site, not resolved by
  picking one — which today's read confirms is still the correct treatment.

**Prices.** All three manufacturer pages display prices. This site publishes none, per the program
policies restriction (R-04/R-05). Confirmed: no price token appears on any page generated by
`tools/build_front.py` (gate G2).

---

## 3. Amazon Associates official pages

| Source | URL | What was checked | Result |
|---|---|---|---|
| S24 — simple text link format | <https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC> | ASIN definition + qualifying link format | **verbatim match** |
| S04/S28 — Standard Commission Income Statement, Table 1 | <https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ> | all 11 fixed rate bands | **exact match** |

**S24, verbatim as served today:**

> ASIN: ASIN is the 10-digit code that Amazon uses to denote specific products.

> http://www.amazon.com/dp/ASIN/ref=nosim?tag=YOURASSOCIATEID

This is the sentence the 9-vs-10-character flag **F-01** rests on, and the format that flag **F-24**
(no `tag=` parameter on the supplied links) rests on. Both readings are confirmed.

**Table 1 as served today, against `ledger/commission_table.json`:**

| Band | Rate | Categories | Stored | Match |
|---|---|---|---|---|
| C-10 | 10.00% | Luxury Beauty, Luxury Stores Beauty, Amazon Explore | yes | ✔ |
| C-05 | 5.00% | Digital Music, Physical Music, Handmade, Digital Videos | yes | ✔ |
| C-045 | 4.50% | Physical Books, **Kitchen**, Automotive | yes | ✔ |
| C-04 | 4.00% | Amazon devices, Fashion, Apparel, Watches, Jewelry, Luggage, Shoes, Handbags & Accessories | yes | ✔ |
| C-03 | 3.00% | Toys, Furniture, Home, Home Improvement, Lawn & Garden, Pets Products, Headphones, Beauty, Musical Instruments, Business & Industrial Supplies, Outdoors, Tools, Sports, Baby Products, Amazon Coins | yes | ✔ |
| C-025 | 2.50% | PC, PC Components, DVD & Blu-Ray | yes | ✔ |
| C-02 | 2.00% | Televisions, Digital Video Games | yes | ✔ |
| C-01 | 1.00% | Amazon Fresh, Physical Video Games & Video Game Consoles, Grocery, Health & Personal Care | yes | ✔ |
| C-00 | 0.00% | Gift Cards; Wireless; Alcohol; Kindle subscription; Vehicles; Pet Prescriptions; restaurant delivery; Appstore, Prime Now, Amazon Pay Places | yes | ✔ |
| C-00b | 0.00% | Coach | yes | ✔ |
| C-OTH | 4.00% | All Other Categories | yes | ✔ |

11 of 11 bands, rates and category lists all identical. The bounty table's first ten rows were also
read and match (Prime Free Trial $12.00, Prime Video First Stream $5.00, Prime Video Stream $0.25,
and so on).

**Not re-fetched today, and why:** the Associates Program Policies (S02, page states *Updated: April
14, 2026*) and the Operating Agreement (S01, page states *Updated: October 15, 2025*) were re-read
live earlier on 2026-11-16 by session `arena/224cc10c-zone2`, whose record lists 16 of 17 stored
quotes matching verbatim and the one drift (S60) corrected. Re-reading them again hours later would
add nothing; this record depends on that one only for the two page-stated dates quoted above, which
are reproduced from that session's table.

---

## 4. Gates run on the tree before and after this session's changes

| Gate | Before T50 | After T50 |
|---|---|---|
| `tools/ci_replay.py` (full workflow, local) | 35/35 pass | **37/37 pass** (2 new steps: front rebuild-check, front gate) |
| `tools/validate_data.py` | pass | pass |
| `tools/validate_decisions.py` | pass | pass |
| `tools/validate_discovery.py` | 0 failures | 0 failures |
| `tools/build_head_meta.py --audit` | 87 pages, 0 problems | 87 pages, 0 problems |
| `tools/seo_audit.py` | all pass | all pass |
| `tools/build_readiness.py --check` | current | current after regeneration (derived counts only) |
| `tools/test_readiness.py` | 13/13 | 13/13 |
| `tools/audit_site.py` | 141 pages, all pass | **148 pages**, all pass |
| `tools/verify_front.py` (new) | — | **8 pages, 8/8 checks pass** |

Two gates failed during the build and were fixed at source, not suppressed:

1. **Subpage gate** — the rewritten `index.html` no longer carried the `id="flagCount"` and
   `id="flagCountHeading"` markers, so the flag count would have had to be typed into prose and could
   drift from the register (the F-17/F-26 class of defect). Fixed by restoring both markers in the
   new layout and loading `assets/js/data.js` + `assets/js/app.js` so they render from
   `CANONICAL_FLAG_COUNT`.
2. **Structural audit, orphan check** — the new footer initially dropped the links to eight companion
   namespaces (`release/`, `research-hub/`, `northstar/`, `zone2/`, `affiliate-lab/`,
   `revalidation/`, `marketing/`, `discovery/`). Fixed by restoring all of them in the footer's
   operator-surfaces line.

---

## 5. What this record does not cover

* **The three token-to-product mappings.** Not verified, and not verifiable: no public Amazon
  document binds a `link.amazon` short code to a product. That gap is flag **F-03** and question
  **Q-T50-01**, and it is published, not closed.
* **The Associates tag, marketplace and account status.** Unknown; cannot be looked up. **Q-T50-02**,
  **Q-T50-03**, **Q-T50-04**.
* **Traffic, clicks, conversions, revenue.** None exist. No figure appears anywhere on this site.
* **Search-volume or trend data for the article topics.** Deliberately absent. Third-party estimates
  are not official sources, and publishing them as fact is what Google's helpful-content guidance
  warns against.
