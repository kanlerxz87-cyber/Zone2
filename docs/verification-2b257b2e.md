# Verification log — session `2b257b2e` (`arena/2b257b2e-zone2`) — 2026-11-15 (UTC)

Independent re-verification pass for the T30–T33 redesign wave. Every row below was fetched **live on
2026-11-15 by this session**, from the official page itself, not carried forward from a previous
session's notes. Where the page could not be reached, the row says exactly that — nothing is inferred.

| # | Claim checked | What the official page says (read 2026-11-15) | Verdict | Source |
|---|---|---|---|---|
| D2-01 | Operating Agreement currency + §5 disclosure sentence | Header: "**Updated:** October 15, 2025". §5 *Identifying Yourself as an Associate*: "You must clearly and prominently state the following … 'As an Amazon Associate I earn from qualifying purchases.'" | **Verified verbatim** | https://affiliate-program.amazon.com/help/operating/agreement |
| D2-02 | OA §4 expectation setting | "We do not make any representation, warranty, or covenant regarding the amount of traffic or commission income you can expect at any time in connection with the Associates Program" | **Verified verbatim** (confirms ledger rule R-19) | https://affiliate-program.amazon.com/help/operating/agreement |
| D2-03 | OA §1 Special Links definition | Links "must properly use the special '**tagged**' link formats we provide" — the basis for flag F-24 (the supplied links carry no Associates `tag`) | **Verified** | https://affiliate-program.amazon.com/help/operating/agreement |
| D2-04 | OA §6 termination | Either party may terminate on written notice, effective **7 calendar days** from notice; Amazon may terminate/suspend **immediately** on material breach, and "any violation of Section 5 … will be deemed a material breach" | **Verified verbatim** | https://affiliate-program.amazon.com/help/operating/agreement |
| D2-05 | Table 1 fixed rates | Eleven bands read row by row: Luxury Beauty 10.00% · Music/Handmade 5.00% · **Physical Books, Kitchen, Automotive 4.50%** · Devices/Apparel 4.00% · **Toys, Furniture, Home … 3.00%** · PC 2.50% · TV 2.00% · Grocery/Health 1.00% · zero-rate group 0.00% · Coach 0.00% · **All Other Categories 4.00%** | **Verified verbatim** | https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ |
| D2-06 | Supplied link 1 destination | `https://link.amazon/B04G1MEwY` → `https://www.amazon.com/dp/B0CDY277D3`, title "CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows, Sync Finish, Hi-Fry, Auto Shutoff, 2 Independent 3Qt Nonstick Dishwasher Safe Frying Baskets, Digital Double Air Fryer - Black"; markers `lv=shuf`, `plpRedirect=mhFallback`, `channelId=704`, `btn_ref=srctok-…` (a **new token vs. 2026-11-14**, consistent with F-21 per-day tokens); no Associates `tag` | **Independently reproduced** | https://link.amazon/B04G1MEwY |
| D2-07 | Supplied link 2 destination | `https://link.amazon/B02NbDxp3` → `https://www.amazon.com/dp/B09B7SB46R`, title "Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven … 24 One-Touch Preset Options …" (Amazon title states 24 — the manufacturer-page 25-pre-set conflict of F-19 stands) | **Independently reproduced** | https://link.amazon/B02NbDxp3 |
| D2-08 | Supplied link 3 destination | `https://link.amazon/B00hJ57DV` → `https://www.amazon.com/dp/B08DKYBTPH`, title "Chefman Air Fryer 8 Qt \| TurboFry® 4-in-1 with 450°F Hi-Fry Option for Crispier Results \| Bake, Dehydrate, Frozen \| XL Nonstick Dishwasher-Safe Basket \| Stainless Steel" | **Independently reproduced** | https://link.amazon/B00hJ57DV |
| D2-09 | Category path of all three destinations | Each fetched page's breadcrumb: Home & Kitchen › Kitchen & Dining › Small Appliances › Fryers › **Air Fryers** | **Verified** (supports "one shared category, Air Fryers") | The three `/dp/` URLs above |
| D2-10 | Google guidance on affiliate outbound links | "Mark links that are advertisements or paid placements (commonly called *paid links*) with the `sponsored` value"; multiple `rel` values may be combined. Page last updated 2025-12-10 UTC | **Verified** | https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links |
| D2-11 | FTC material-connection disclosure | Endorsement Guides FAQ: "if there's a connection between an endorser and the marketer that a significant minority of consumers wouldn't expect … that connection should be disclosed clearly and conspicuously" | **Verified** | https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking |
| D2-12 | Program Policies page (Participation Requirements §2(b), §4, §6(t)/(y)/(w)) | **Not re-fetched this session** (page is large; the requirements were transcribed into `ledger/compliance.json` and re-verified on 2026-11-14 by sessions `0a697d4a` (C-10…C-13) and `dd87f326`). This session quotes no new sentence from that page; the redesigned pages link the ledger rows instead. | **Carried forward, cited — not re-quoted** | https://affiliate-program.amazon.com/help/operating/policies |

## Observations recorded for the redesign (T30/T31)

1. All three destinations share the **Air Fryers** category path (D2-09) — the editorial topic set on
   `content.html` is anchored to that niche, with each topic's factual anchor linked to the listing it
   was read from.
2. The `btn_ref` tokens on all three links differ from the 2026-11-14 values while the ASINs are
   identical — consistent with flag **F-21** (per-day token), no change of position.
3. Per product price, rating, review count, availability and per-ASIN commission band: **still not
   published** — no official page was read for them this session, and the no-inference rule stands.
   The redesign leaves every such cell blank exactly as before.

## Irregularities

None new. The pre-existing flags (F-01…F-38 register) are unchanged and remain published on
[`flagged.html`](../flagged.html) / [`pages/flags.html`](../pages/flags.html).
