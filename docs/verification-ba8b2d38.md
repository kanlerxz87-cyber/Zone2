# Independent verification pass — session `ba8b2d38` (T27), 2026-11-14

This is a **standalone record**. Every value below was read off a page this session fetched
itself; nothing is copied from another session's notes, and no blank was filled by inference.

Scope: re-fetch all three supplied affiliate links, all three canonical `/dp/<token>` URLs,
every official Amazon Associates page cited by this repository, and run one control no earlier
session had run.

---

## 1. The three supplied links

| Supplied link | Resolves to | Verified page title (as observed) | `btn_ref` observed this session |
|---|---|---|---|
| `https://link.amazon/B04G1MEwY` | `https://www.amazon.com/dp/B0CDY277D3` | CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows, Sync Finish, Hi-Fry, Auto Shutoff, 2 Independent 3Qt Nonstick Dishwasher Safe Frying Baskets, Digital Double Air Fryer - Black | `srctok-704dc575b940a94c` |
| `https://link.amazon/B02NbDxp3` | `https://www.amazon.com/dp/B09B7SB46R` | Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven \| 26QT air fryer oven with French doors, 24 cooking functions, dual-speed fan and rotisserie for easy family meals. | `srctok-76d4981d5f44181b` |
| `https://link.amazon/B00hJ57DV` | `https://www.amazon.com/dp/B08DKYBTPH` | Chefman Air Fryer 8 Qt \| TurboFry® 4-in-1 with 450°F Hi-Fry Option for Crispier Results \| Bake, Dehydrate, Frozen \| XL Nonstick Dishwasher-Safe Basket \| Stainless Steel | `srctok-016f4a534eed3621` |

All three destinations match the destinations already on record (evidence rows E-01…E-03).
This is the **third independent confirmation** of all three.

All three `btn_ref` values are **new**, and none matches any previously recorded value. The
source token rotates continuously; the destination does not. Recorded as evidence row **E-12**
and consistent with flag **F-21**.

All three resolved URLs carried `channelId=704` and `plpRedirect=mhFallback`, as before.
Per E-07 that parameter is also emitted on ordinary direct product-page loads, so it is not
evidence of a fallback.

## 2. The tokens as supplied are not catalog identifiers

| Check | Result | Source |
|---|---|---|
| `https://www.amazon.com/dp/B04G1MEwY` | Page Not Found ("Sorry! We couldn't find that page.") | [S16](https://www.amazon.com/dp/B04G1MEwY) |
| `https://www.amazon.com/dp/B02NbDxp3` | Page Not Found | [S17](https://www.amazon.com/dp/B02NbDxp3) |
| `https://www.amazon.com/dp/B00hJ57DV` | Page Not Found | [S18](https://www.amazon.com/dp/B00hJ57DV) |
| Amazon's definition of an ASIN | "ASIN is the **10-digit** code that Amazon uses to denote specific products." | [S24](https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC) |

Each supplied code is 9 characters, so none is a valid ASIN (**F-01**).

## 3. Controls

### 3.1 Unknown-code control (reproduces F-20)

`https://link.amazon/B00TEST12` → `https://amzlinks.in/B00TEST12` → **404: File Not Found —
"You've clicked on an invalid URL."** Independently reproduced. A service that answered unknown
codes with a random product would be a fallback; one that answers with a 404 is doing a lookup.
[Source S32](https://link.amazon/B00TEST12)

### 3.2 Valid-ASIN control — **new, run for the first time by this session**

`https://link.amazon/B0CDY277D3` — a **valid 10-character ASIN**, which renders normally at
`https://www.amazon.com/dp/B0CDY277D3` — resolved to `https://amzlinks.in/B0CDY277D3` and
returned **the identical 404 page** as the unknown-code control.
[Source S36](https://link.amazon/B0CDY277D3)

**What this decides.** The `link.amazon` service does not accept, interpret or truncate ASINs.
It performs a lookup over its own short-code namespace. The earlier suggestion that the supplied
codes look like a "one-character truncation" of an ASIN (evidence row E-05) is therefore **not
supported**: a service that truncated to fit would resolve a correct ASIN, and this one does not
accept ASINs at all. The 9-character codes are opaque short-link identifiers, and their
resemblance to a truncated ASIN is a coincidence of appearance.

Recorded as evidence row **E-11** and flag **F-28**. The original E-05 wording is retained in
place and marked corrected rather than deleted, so the record still shows what the site
previously said and why it changed. **No product conclusion changes** — the tokens are still not
ASINs, no character was ever guessed, and the three destinations are unchanged.

## 4. Official Amazon Associates sources re-read this session

| # | Claim | Verdict | Source |
|---|---|---|---|
| V-51 | OA §5 requires "As an Amazon Associate I earn from qualifying purchases." clearly and prominently | **Verified** | [S01](https://affiliate-program.amazon.com/help/operating/agreement) |
| V-52 | Operating Agreement states "Updated: October 15, 2025" | **Verified** | [S01](https://affiliate-program.amazon.com/help/operating/agreement) |
| V-53 | Program Policies state "Updated: April 14, 2026" | **Verified** | [S02](https://affiliate-program.amazon.com/help/operating/policies) |
| V-54 | Session ends at 24 h / an order / another associate's click; cart order ≤ 89 days; shipped and paid within 180 days | **Verified** | [S02](https://affiliate-program.amazon.com/help/operating/policies) |
| V-55 | Paid ≈60 days after month end; US minimums 10 / 10 (2,000 max) / 100 + 15 USD fee | **Verified** | [S02](https://affiliate-program.amazon.com/help/operating/policies) |
| V-56 | "Earn up to 10% in associate commissions from qualifying purchases and programs." | **Verified** | [S37](https://affiliate-program.amazon.com/) |
| V-57 | Agent Terms: `Agent/[name]` user-agent; must not circumvent CAPTCHAs; must answer truthfully | **Verified** | [S30](https://affiliate-program.amazon.com/help/operating/policies#Associates%20Program%20IP%20License) |
| V-58 | All eleven Table 1 rate bands match the ledger transcription, band for band | **Verified** | [S28](https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ) |
| V-59 | ASIN is defined as a 10-digit code | **Verified** | [S24](https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC) |
| V-60 | Official simple text link format is `.../dp/ASIN/ref=nosim?tag=YOURASSOCIATEID` | **Verified** | [S24](https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC) |
| V-69 | 3-year inactivity → withholding up to the gift-card minimum, with 7 days' notice | **Verified** | [S02](https://affiliate-program.amazon.com/help/operating/policies) |
| V-70 | Associates tags may only be used for Associates commissions; double-claiming may trigger withholding or termination | **Verified** | [S02](https://affiliate-program.amazon.com/help/operating/policies) |

V-58 was checked **programmatically**, not by eye: all eleven bands (10.00 / 5.00 / 4.50 / 4.00 /
3.00 / 2.50 / 2.00 / 1.00 / 0.00 / Coach 0.00 / All Other Categories 4.00) were compared
category-string by category-string against `ledger/commission_table.json`. Every one matched.
The only difference was cosmetic: the ledger files "All Other Categories" inside the 4.00 % band,
which is where the live page places it.

## 5. Irregularity found and fixed by this session

Root `flagged.html` carried the hardcoded sentence **"26 flags (F-01 … F-26)"**. The register had
already grown to 28 while the page still named 27, so the published page told readers the register
held 26. This is the same defect class as **F-26** (a count that drifts from the ledger), but
surfacing in prose rather than in a KPI — and the existing gate only compared the
`CANONICAL_FLAG_COUNT` constant, so nothing caught it.

Fixed by rendering the count and the range from the data (`#flagRegisterCount`,
`#flagRegisterRange`), and closed with a new build gate,

> **Note added 2026-11-14 (session `d3ce1c29`).** The sentence quoted above is the defect, not a
> claim, so it is left verbatim. The register has grown again since this log was written — it now
> holds **33 flags (F-01 … F-33)** after this session added F-29 … F-33 and `main` contributed
> F-27/F-28 — and the count is rendered from the data, so the page can no longer drift.
`tools/validate_data.py::check_no_typed_flag_counts`, which fails the build if a typed register
size reappears. The gate is **negative-tested**: reintroducing "26 flags" turns it red.

The gate is deliberately narrow. An "F-01 … F-NN" range check was tried first and rejected,
because pages legitimately cite a *subset* of flags that way (`index.html` cites
`<code>F-01…F-03</code>` in a table cell), which produced a false positive. Only a count phrase
("N flags", "N items flagged") is unambiguous enough to fail a build on. The check also skips
`pages/flags.html` (which quotes historical counts 11 and 15 while narrating how F-17 and F-26
were found) and the companion namespaces (`affiliate-lab/` publishes its own, separate register).

## 6. What remains genuinely unverified

Unchanged, and **not** inferable:

1. **Identity.** No public Amazon document binds a `link.amazon` code to a product. The three
   products are published as "the product this link resolves to", never "the product the brief
   named" (F-03, F-06).
2. **Economics.** None of the three supplied links carries an Associates `tag`, so as supplied
   they cannot attribute a sale or earn a commission (F-24).
3. **Data.** Price, rating, review count, availability, sales rank and the per-category
   commission band could not be confirmed from an official source within the rules and are left
   blank. The resolved products sit under a Home & Kitchen › … › Air Fryers path, where Table 1
   offers both "Kitchen 4.50 %" and "Home 3.00 %"; which band Amazon actually applies is an
   account/catalog lookup, so it is **not** inferred here.
