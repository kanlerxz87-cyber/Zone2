# Verification record — T59 (session `1539a895`, 2026-11-17; renumbered from T58)

**Task.** Onboard the two newly supplied affiliate links — `B0c8moW59` and `B0f3GKalj` — that the brief
names but no prior session had processed. Resolve them, verify the destination specifications from official
Amazon listing pages, add them to the source-governed ledger with a product-intent confirmation record, and
regenerate every derived surface.

**Rule applied throughout.** A value appears only when the official page states it. Anything that cannot be
confirmed stays blank and is flagged. Nothing is inferred, filled in, or chosen between conflicting figures.

All live checks were performed with `fetch_page` on **2026-11-17 (UTC)**. The sandbox shell cannot reach
the network directly, so every official page was read through `fetch_page`; the repository's own gates were
run with `python3` from a clean checkout of the branch.

---

## 1. The five supplied links, and what was missing

| # | Link as supplied | Prior state in the repo |
|---|---|---|
| 1 | `https://link.amazon/B04G1MEwY` | processed (`P-01` → `B0CDY277D3`, Chefman 6 Qt dual-basket air fryer) |
| 2 | `https://link.amazon/B02NbDxp3` | processed (`P-02` → `B09B7SB46R`, Emeril 26 Qt French-door oven) |
| 3 | `https://link.amazon/B00hJ57DV` | processed (`P-03` → `B08DKYBTPH`, Chefman 8 Qt TurboFry) |
| 4 | `https://link.amazon/B0c8moW59` | **no references anywhere** — unprocessed |
| 5 | `https://link.amazon/B0f3GKalj` | **no references anywhere** — unprocessed |

A repository-wide search for `B0c8moW59` and `B0f3GKalj` returned **zero** hits before this session. This is
the gap T59 closes.

## 2. Resolution of the two new links (observed behaviour)

| Link | Final URL observed | Page title observed | Verdict |
|---|---|---|---|
| `https://link.amazon/B0c8moW59` | `https://www.amazon.com/dp/B0DHZTCNR5?...plpRedirect=mhFallback` | "ThermoMaven 1 Sec Professional Digital Meat Thermometer, ±0.5℉ Accuracy \| NIST&NSF Certified … Black" | **OBSERVED** — one stable listing |
| `https://link.amazon/B0f3GKalj` | `https://www.amazon.com/dp/B0DZFD6R9Z?...plpRedirect=mhFallback` | "CHEF iQ Sense \| Smart Wireless Meat Thermometer \| 3 Ultra-Thin Probes \| WiFi Unlimited Range \| 1000°F Heat Safe \| 5 Sensors \| … \| Gen3" | **OBSERVED** — one stable listing |

Each resolves reproducibly to a single live Amazon listing. As with the first three, the 9-character code is
**not** a valid ASIN and carries no documented binding to the destination, so the destination is an
observation, not an established identity (flags `F-03`, `F-20`, `F-24`).

## 3. The `/dp/<token>` control (reproduced)

| URL | Result |
|---|---|
| `https://www.amazon.com/dp/B0c8moW59` | Amazon "Page Not Found" error page |
| `https://www.amazon.com/dp/B0f3GKalj` | Amazon "Page Not Found" error page |

Both 9-character codes fail the canonical `/dp/` lookup exactly as the first three did, confirming the
codes are not ASINs and cannot address a catalog record as written (flag `F-01`, control `F-28`).

## 4. Destination specifications, read line by line from the official listings

Every row below was read from the Amazon listing's own *Product information* / *About this Item* /
*Product Description* blocks. The listing URL is the source for each row.

### P-04 — ThermoMaven 1 Sec Professional Digital Meat Thermometer (`B0DHZTCNR5`)
Source: [https://www.amazon.com/dp/B0DHZTCNR5](https://www.amazon.com/dp/B0DHZTCNR5) (S61)

| Attribute | Value read from the listing | Status |
|---|---|---|
| Response time | 1 second | verified |
| Accuracy | ±0.5 °F | verified |
| Upper temperature range | 572 °F | verified |
| Resolution | 0.1 ° | verified |
| Immersion depth | 6.5 in | verified |
| Display type | Digital | verified |
| Power source | Battery powered (1 AAA battery, included) | verified |
| Additional features | Auto off, fast reading system, high accuracy, ultra clear screen, waterproof | verified |
| Reusability | Reusable | verified |
| Indoor / outdoor use | Indoor, Outdoor | verified |
| Specification met | NIST, NSF | verified |
| Material | Plastic | verified |
| Care instructions | Wipe clean | verified |

### P-05 — CHEF iQ Sense Smart Wireless Meat Thermometer, Gen3 (`B0DZFD6R9Z`)
Source: [https://www.amazon.com/dp/B0DZFD6R9Z](https://www.amazon.com/dp/B0DZFD6R9Z) (S62)

| Attribute | Value read from the listing | Status |
|---|---|---|
| Sensors | 5 (4 internal temperature sensors + 1 ambient sensor) | verified |
| Accuracy | within 1 °F | verified |
| Heat safety | 1000 °F | verified |
| Probes included | 3 ultra-thin probes | verified |
| Probe length | 4.75 in | verified |
| Connectivity | WiFi (unlimited range) and Bluetooth | verified |
| Battery life | up to 50 hours (*About this Item*) **vs** up to 70 hours (*Product Description*) | **conflict — both published** |
| Probe care | Waterproof and dishwasher-safe probes | verified |
| Warranty | Two-year assurance provided by CHEF iQ | verified |
| Smart hub | Speaker + push notifications; charges all probes simultaneously | verified |
| Air-fryer / deep-fryer safe | Yes | verified |
| Size options | 1, 2, 3 or 4 probes | verified |

The battery-life row is recorded as a **conflict**: two figures appear on the same official listing and
disagree. Both are published; neither is selected. This mirrors the repository's treatment of the two
published disagreements on the air-fryer set.

## 5. Fields left blank, and why

| Field | Reason it is blank |
|---|---|
| `title`, `brand`, `category` (token identity) | The 9-character code is not a valid ASIN and `/dp/<code>` returns Page Not Found; no official record identifies the token itself. |
| `price`, `rating`, `review_count`, `availability`, `bsr` | Point-in-time values the Associates Program Policies do not allow to be republished outside a served link or licensed API (S02). |
| `commission_rate` | Needs an authenticated catalog lookup; the public Table 1 (S04) does not name the "Kitchen Utensils & Gadgets" node, so the band cannot be assigned between "Kitchen" 4.50% and "Home" 3.00% without guessing (flag `F-43`). |
| `intended_asin`, `official_listing_url`, `confirmation_date`, `intent_source` | The product-intent confirmation record is blank until the owner confirms intent; the observed redirect target is kept in a separate field (`observed_redirect_target`) and never merged with them. |

## 6. New register rows

- **Sources:** `S61` (ThermoMaven listing), `S62` (CHEF iQ listing) — added to `ledger/sources.json`.
- **Flags:** `F-42` (the two links were unprocessed and resolve to a new category), `F-43` (commission-band
  ambiguity) — added to `ledger/flags.json`.
- **Verification rows:** `V-105`…`V-108` — added to `ledger/verification.json`.
- **Questions:** `Q-19` (confirm intended ASINs for links 4 and 5), `Q-20` (confirm the commission band) —
  added to `ledger/questions.json`.
- **Suggestions:** `SG-13` (build a matching thermometer content set once intent is confirmed), `SG-14`
  (adopt the product-intent confirmation record as standard intake) — added to `ledger/suggestions.json`.

## 7. Irregularities found and resolved during this session

1. **Source-ID collision with the discovery namespace (resolved).** The discovery register
   (`docs/discovery-t40-sources.json`) owns source IDs `S44`…`S60`. The first draft of this task used `S44`/`S45`
   for the two new product listings, which `validate_discovery.py` correctly flagged as "source ids redefined
   in both registers". The two ledger sources were renumbered to **`S61`/`S62`**, outside the discovery range.
   No other session's source IDs were altered.
2. **Typed derived counts drifted (resolved).** Adding two flags and two sources pushed the registers from
   41→43 flags, 43→45 sources, 104→108 verification rows, and added two questions and two suggestions.
   `validate_data.py` and `audit_site.py` caught typed copies of these counts in the generated `pages/*.html`
   (regenerated) and in the hand-authored `README.md` / `EXECUTIVE_SUMMARY.md` (updated to the live counts).
   No verified product value was changed by any of this.
3. **Hardcoded "three" copy in `build_site.py` (resolved).** The product-catalog page and its decision text
   still said "three items / three supplied / three resolved destinations" after the count became five.
   These were corrected to "five" and the two new listing sources added to the affected evidence lists. This
   is a correctness fix to a published surface, logged here per the coordination protocol.

## 8. Gates run on the final tree

`validate_data.py` 0 errors · `validate_console.py` pass · `validate_decisions.py` pass ·
`validate_audit.py` pass · `validate_brief.py` pass · `validate_discovery.py` pass ·
`validate_review_board.py` pass · `audit_site.py` 162 pages all PASS · `seo_audit.py` pass ·
`build_head_meta.py --audit` 0 problems · `check_css_urls.py` 0 broken · `verify_front.py` pass ·
`tests/test_pipeline.py` 15/15 · `test_readiness.py` pass · `test_brief.py` pass ·
`test_review_board.py` pass · `test_audit.py` pass · `ci_replay.py` (all 43 CI steps) pass.

**No verified value from the first three entries was altered.** No price, rating, review count, availability,
sales rank or commission value was inferred for any of the five links.
