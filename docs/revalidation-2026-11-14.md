# Line-by-line re-verification — 2026-11-14

Session `c6e94e8d` · branch `arena/c6e94e8d-zone2` · task T20 in `COORDINATION.md`.

Purpose: re-check the three supplied `link.amazon` links and the product attributes previously published,
against official sources, and run the control test that the earlier "fallback" conclusion was missing.

**Method note.** Fetches were made with the agent's page-fetch tool. `curl` from the build sandbox cannot
reach these hosts — `affiliate-program.amazon.com`, `www.amazon.com`, `chefman.com` and
`developers.google.com` all returned HTTP `000`, exit code 35. These are therefore dated observations with
quoted output, not a re-runnable CI step. CI re-checks internal consistency only.

Published at `revalidation/`. Every table row on that site ends in an official source link or is blank with
an explicit reason.

---

## 1. Link resolution and the control test

| ID | Question | Method | Result | Verdict |
|---|---|---|---|---|
| C-1 | Does `plpRedirect=mhFallback` prove a fallback? | Bare, untagged `GET https://www.amazon.com/dp/B08DKYBTPH` — a **valid** 10-char ASIN. | 200; full product page (buy box, About this Item, User Guide, Prop 65). Amazon rewrote its own links to `?lv=shuf&channelId=500&plpRedirect=mhFallback&th=1`. | **Marker is normal, not evidence.** Verified. |
| C-1b | Same control on a second valid ASIN | Bare `GET https://www.amazon.com/dp/B0CDY277D3` | 200; correct CHEFMAN 6 Qt page; same `plpRedirect=mhFallback` appended. | Confirms C-1. |
| C-2 | Is the destination unstable between requests? | `GET https://link.amazon/B04G1MEwY` twice. | Both → `/dp/B0CDY277D3`, **identical** `btn_ref=srctok-1e229870efde5acf`, identical body. | **Not a shuffle.** The published "different `btn_ref` on re-fetch" is not reproducible. |
| C-3 | Do the three links map one-to-one? | Fetch all three. | `B04G1MEwY`→`B0CDY277D3` `srctok-1e229870efde5acf`; `B02NbDxp3`→`B09B7SB46R` `srctok-534f5e7952f396b2`; `B00hJ57DV`→`B08DKYBTPH` `srctok-76c3adaeb8708b44`. All `channelId=704`, `btn_type=ss`. | Three distinct **stable per-link tokens** — per-link tracking. |
| C-4 | Are the codes ASINs? | Bare `GET /dp/<code>` for each. | All three → Amazon "Page Not Found" (title observed). Codes are 9 chars; Associates help states the ASIN is the 10-digit code. | **Not ASINs.** Confirmed. |
| C-5 | Do the resolved links carry an Associates tag? | Inspect each resolved URL for `tag=`. | Absent on all three. | **No tag → not a valid Special Link as supplied.** Verified, flagged RV-02. |

Sources: <https://www.amazon.com/dp/B08DKYBTPH>, <https://www.amazon.com/dp/B0CDY277D3>,
<https://www.amazon.com/dp/B09B7SB46R>, <https://www.amazon.com/dp/B04G1MEwY>,
<https://www.amazon.com/dp/B02NbDxp3>, <https://www.amazon.com/dp/B00hJ57DV>,
<https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC>.

### Corrected conclusion

The codes are **not** ASINs (C-4 stands). But the `link.amazon` URLs are **stable, individually tracked
links that resolve deterministically to one product each** (C-1, C-2, C-3). The published statement that
the destinations are arbitrary fallback pages that "cannot identify a product" is **not supported**.
What remains unresolved is narrower: no public Amazon document binds a short code to a destination ASIN,
and no resolved URL carries a tag.

---

## 2. Product attributes, re-read line by line

Legend: ✔ verified on the linked official source · ⚠ conflict between official sources · – blank, flagged.

### B0CDY277D3 — CHEFMAN 6 Qt Dual Basket Air Fryer Oven (via `link.amazon/B04G1MEwY`)

| Field | Value | Verdict | Source |
|---|---|---|---|
| Title | CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows, Sync Finish, Hi-Fry, Auto Shutoff, 2 Independent 3Qt Nonstick Dishwasher Safe Frying Baskets, Digital Double Air Fryer — Black | ✔ | <https://www.amazon.com/dp/B0CDY277D3> |
| Model number | RJ38-SQPF-3TDB-2W | ✔ | <https://chefman.com/products/turbofry-touch-dual-window-air-fryer> |
| Capacity | 6 Qt / 5.67 L | ✔ | same |
| Temperature range | 200–450 °F / 95–235 °C | ✔ | same |
| Power | 1700 W / 120 V | ✔ | same |
| Dimensions | 13.38 × 11.81 × 10.63 in / 33.98 × 30 × 27 cm | ✔ | same |
| Weight | 13.3 lb / 6.03 kg | ✔ | same |
| Certification / warranty | cETL approved; 1-year Chefman assurance | ✔ | same |
| Inner material | – | – **not re-observed** (RV-06) | — |
| UPC | – | – none printed (RV-07) | — |

Note: Chefman's page lists capacity in both **Qt (6)** and **litres (5.67)**, i.e. 1 Qt ≈ 0.945 L on their
own figures — not the US-liquid 0.946 L. Both are the manufacturer's own statements and both are reproduced
here without conversion.

### B09B7SB46R — Emeril Lagasse 26QT French Door Air Fryer Toaster Oven (via `link.amazon/B02NbDxp3`)

| Field | Value | Verdict | Source |
|---|---|---|---|
| Title | Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven \| 26QT air fryer oven with French doors, 24 cooking functions, dual-speed fan and rotisserie for easy family meals. | ✔ | <https://www.amazon.com/dp/B09B7SB46R> |
| Model number (as printed) | 4-00675-02A-VN | ✔ | <https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360> |
| Capacity | 26 qt / 24.6 L, sized for 4–6 people | ✔ | same |
| Dimensions | 16.9"D × 15.8"W × 14.8"H | ✔ | same |
| Voltage | 120 V | ✔ | same |
| Rotisserie / dual-speed fan | Both stated | ✔ | same |
| Warranty | 1 year | ✔ | same |
| Accessories | 7 premium accessories named only in part | ✔ | same |
| **Cooking functions** | **24** (Amazon title) · **24** (manufacturer description) · **25** (manufacturer spec tile) · **10** listed under "10-In-1" | ⚠ conflict | <https://www.amazon.com/dp/B09B7SB46R> + manufacturer page |
| Wattage | – | – manufacturer publishes voltage only (RV-06) | — |
| Maximum temperature | – | – manufacturer states "Temperature Control", no number (RV-06) | — |
| Item weight / UPC | – | – (RV-07) | — |

The manufacturer's own page states the function count as **both 24 and 25**, and separately advertises
"10-In-1". All four figures are published; none is presented as definitive.

### B08DKYBTPH — Chefman 8 Qt TurboFry 4-in-1 (via `link.amazon/B00hJ57DV`)

| Field | Value | Verdict | Source |
|---|---|---|---|
| Title | Chefman Air Fryer 8 Qt \| TurboFry 4-in-1 with 450°F Hi-Fry Option for Crispier Results \| Bake, Dehydrate, Frozen \| XL Nonstick Dishwasher-Safe Basket \| Stainless Steel | ✔ | <https://www.amazon.com/dp/B08DKYBTPH> |
| Model number | RJ38-SQSS-8T | ✔ | <https://chefman.com/products/turbofry-touch-air-fryer-1> |
| Capacity (8 Qt model) | 8 Qt / 7.57 L | ✔ | same |
| Temperature range | 200–400 °F / 95–205 °C | ✔ | same |
| **Power** | **1000 W / 120 V** (Amazon "About this Item" bullet) vs **1700 W / 120 V** (Amazon "Product Description", *same page*) vs **1700 W / 120 V** (manufacturer) | ⚠ conflict | <https://www.amazon.com/dp/B08DKYBTPH> + manufacturer page |
| Dimensions (8 Qt) | 15.4 × 12.6 × 13.5 in / 39.11 × 32 × 34.29 cm | ✔ | manufacturer |
| Weight (8 Qt) | 12.8 lb / 5.8 kg | ✔ | manufacturer |
| Presets | 4 — French fries, chicken, meat, fish | ✔ | Amazon + manufacturer |
| Certification / warranty | cETL approved; 1-year Chefman assurance | ✔ | manufacturer |

**New detail on the wattage conflict.** It was previously reported as Amazon-versus-manufacturer. It is
really **Amazon-versus-Amazon**: the same page states 1000 W in the bullet list and 1700 W at the end of the
Product Description paragraph, for the same model number. The manufacturer agrees with 1700 W.

**Why 200–400 °F and 450 °F coexist without conflict.** The listing's 450 °F refers to the Hi-Fry button,
described in the Product Description as lifting the heat "up to 450°F for the last two minutes of cooking";
the general range remains 200–400 °F. Both are on the same official page, so this is reconciled, not a
conflict — recorded as such rather than as an open flag.

---

## 3. Programme facts re-read

| ID | Fact | Verdict | Source |
|---|---|---|---|
| PG-01 | "ASIN is the 10-digit code that Amazon uses to denote specific products"; documented link form `amazon.com/dp/ASIN?tag=YOURASSOCIATEID` | ✔ verbatim | <https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC> |
| PG-02 | Required disclosure: "As an Amazon Associate I earn from qualifying purchases." | ✔ verbatim | <https://affiliate-program.amazon.com/help/operating/agreement> §5 (page states *Updated: October 15, 2025*) |
| PG-03 | Violating §5 is a material breach | ✔ verbatim | same, §6 |
| PG-04 | Special Links must use the special "tagged" link formats | ✔ verbatim | same, §1 |
| PG-05 | Price / availability display rules | **not re-read this session** — relied on, conservative choice retained | <https://affiliate-program.amazon.com/help/operating/policies> |
| PG-06 | Rating / review display rules | **not re-read this session** | same |
| PG-07 | Home & Kitchen commission rate | – requires Associates sign-in | <https://affiliate-program.amazon.com/help/operating/schedule> |

PG-05/PG-06 are marked *not re-checked* rather than *verified*. They are carried forward from the earlier
record and the no-price rule is retained because it is the conservative choice.

---

## 4. Instructions followed by the site's own gates

`revalidation/scripts/verify.py` — result: **6 pages · 73 table rows · 165 references · 0 failures.**

It enforces:
1. the required disclosure sentence on every page;
2. every internal reference resolves to a real file;
3. every data row cites an official external source **or** is an explicitly blank-flagged row;
4. no product price in a buying context (programme economics allowed);
5. no placeholder text.

`revalidation/scripts/build.py --check` — result: **6 built · 0 drifted.** The committed HTML matches a
fresh build from `revalidation/data/*.json`, so the pages cannot silently diverge from their data.

---

## 5. Items logged for other sessions, not edited here

| ID | File (owner) | Request |
|---|---|---|
| CR-1 | `ledger/flags.json` F-03 | Downgrade the "token not honoured / unrelated destination" reading. |
| CR-2 | `ledger/flags.json` F-05, `README.md` | Remove the "different `btn_ref` on re-fetch" claim — not reproducible. |
| CR-3 | `README.md` divergence table | Add the control result for `plpRedirect=mhFallback`. |
| CR-4 | `ledger/products.json` | Remove "via mhFallback" as a `why_blank` reason. |
| CR-5 | `research-hub/data/products.json` | Six attribute rows not re-observable (RV-06). |
| CR-6 | `research-hub/scripts/verify.py` | Still exits non-zero (7 false failures) because `ROOT` points at `research-hub/`; not wired into CI, so nothing is blocked. |

Open flags from this session: **RV-01 … RV-10**, published on `revalidation/flagged.html`.
