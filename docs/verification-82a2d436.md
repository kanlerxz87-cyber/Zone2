# T22 — Independent re-test of the three supplied `link.amazon` links

**Session:** `82a2d436` (`arena/82a2d436-zone2`) · **Date of observation:** 2026-11-14 (UTC) · **Method:** live page fetches with the agent's page-fetch tool. Direct `curl` from the build sandbox to `amazon.com` and `link.amazon` fails with TLS error (`SSL_ERROR_SYSCALL`, exit 35), so every observation below came from the fetch tool and is reproducible by opening the URL in a browser.

**Scope:** this file only. No product copy, price, rating, review count, commission or availability is recorded here, per the no-inference and no-price rules. Nothing in other sessions' files was edited.

---

## 1. Question tested

Earlier records disagree about what the supplied short links do:

| Reading | Where stated | Claim |
|---|---|---|
| A — "fallback" | `ledger/flags.json` F-03, F-12; `affiliate-lab/` AF-06; PR #22 body; T20 correction in `COORDINATION.md` | The token is ignored; the link lands on an unrelated "fallback" page (`plpRedirect=mhFallback`) that identifies no product. |
| B — "stable, tracked" | `docs/`/`revalidation/` (session `c6e94e8d`, C-1…C-3) | The link is a stable, per-link tracked destination; `mhFallback` is not evidence of fallback. |

This session ran the controls that decide between them.

---

## 2. Results

### 2.1 Supplied codes as ASINs

| Row | Code (as supplied) | Length | Official ASIN definition | `amazon.com/dp/<code>` (fetched 2026-11-14) | Verdict |
|---|---|---|---|---|---|
| R1 | `B04G1MEwY` | 9 | 10-digit code — [Associates help GP38PJ6EUR6PFBEC](https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC) | "Page Not Found" — [amazon.com/dp/B04G1MEwY](https://www.amazon.com/dp/B04G1MEwY) | **Not an ASIN.** Confirmed. |
| R2 | `B02NbDxp3` | 9 | same | "Page Not Found" — [amazon.com/dp/B02NbDxp3](https://www.amazon.com/dp/B02NbDxp3) | **Not an ASIN.** Confirmed. |
| R3 | `B00hJ57DV` | 9 | same | "Page Not Found" — [amazon.com/dp/B00hJ57DV](https://www.amazon.com/dp/B00hJ57DV) | **Not an ASIN.** Confirmed. |

### 2.2 Short-link destinations (two fetches per link, same session)

| Row | Supplied link | Final product page (`/dp/`) | Page title (product as shown) | `btn_ref` token, fetch 1 = fetch 2 | Verdict |
|---|---|---|---|---|---|
| R4 | [link.amazon/B04G1MEwY](https://link.amazon/B04G1MEwY) | `B0CDY277D3` — [amazon.com/dp/B0CDY277D3](https://www.amazon.com/dp/B0CDY277D3) | CHEFMAN 6 Quart Dual Basket Air Fryer Oven … : Home & Kitchen | `srctok-1f979f303a4b5691` = `srctok-1f979f303a4b5691` | Resolves to a stable product page. |
| R5 | [link.amazon/B02NbDxp3](https://link.amazon/B02NbDxp3) | `B09B7SB46R` — [amazon.com/dp/B09B7SB46R](https://www.amazon.com/dp/B09B7SB46R) | Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven … : Home & Kitchen | `srctok-0cd8be3c7e2e0de3` = `srctok-0cd8be3c7e2e0de3` | Resolves to a stable product page. |
| R6 | [link.amazon/B00hJ57DV](https://link.amazon/B00hJ57DV) | `B08DKYBTPH` — [amazon.com/dp/B08DKYBTPH](https://www.amazon.com/dp/B08DKYBTPH) | Chefman Air Fryer 8 Qt \| TurboFry® 4-in-1 … : Home & Kitchen | `srctok-7c59360cbbbd59b7` = `srctok-7c59360cbbbd59b7` | Resolves to a stable product page. |

In all six fetches the `/dp/` path, page title and the `lv=shuf&…&plpRedirect=mhFallback` query came back together. No `tag=` (Associates tracking ID) parameter appears in any redirect chain (see §3, F-07 link).

### 2.3 Controls (decide whether the code matters, and whether `mhFallback` means fallback)

| Row | Control | Result (2026-11-14) | What it shows |
|---|---|---|---|
| C-a | Bare, untagged `https://www.amazon.com/dp/B0CDY277D3` (valid ASIN, no parameters) | Loads the CHEFMAN page; Amazon appends `lv=shuf&channelId=500&plpRedirect=mhFallback` | `plpRedirect=mhFallback` is added on an ordinary, direct product-page load. **Not evidence of a fallback.** |
| C-b | Bare, untagged `…/dp/B09B7SB46R` | Loads the Emeril page; same appended query | Same as C-a. |
| C-c | Bare, untagged `…/dp/B08DKYBTPH` | Loads the Chefman 8 Qt page; appends `lv=shuf&channelId=500&plpRedirect=mhFallback&th=1` | Same as C-a. |
| C-d | Random 9-char code `link.amazon/Qx3Vt8Rp1` (cannot be a real code) | **403 Forbidden** (no product page) | A made-up code does **not** produce a product page. |
| C-e | Supplied code with the **last character changed**: `link.amazon/B04G1MEwW` | Leaves Amazon's domain: `amzlinks.in/B04G1MEwW` → "404: File Not Found — You've clicked on an invalid URL." | A one-character change breaks the link. **The code is a keyed lookup, not ignored.** `amzlinks.in` is a third-party host; it is recorded as an observation, not as an Amazon source. |

---

## 3. Comparison with earlier records

| Item | Earlier record | This session (2026-11-14) | Status |
|---|---|---|---|
| Codes are 9 chars, not ASINs | F-01, F-02, AF-01…03, `c6e94e8d` C-4 | Same (R1–R3) | **Confirmed** |
| Destinations `B0CDY277D3`, `B09B7SB46R`, `B08DKYBTPH` | All sessions, 2026-11-13 and 2026-11-14 | Same (R4–R6) | **Confirmed stable across ≥2 days** |
| `btn_ref` token per link | `c6e94e8d` C-3: `srctok-1e229870efde5acf`, `srctok-534f5e7952f396b2`, `srctok-76c3adaeb8708b44` | `srctok-1f979f303a4b5691`, `srctok-0cd8be3c7e2e0de3`, `srctok-7c59360cbbbd59b7` | **Differs from the earlier values.** Stable within a window (R4–R6), changes between windows. The "per-link permanent token" wording in `c6e94e8d` C-3 is therefore **too strong**; the token is not a fixed identifier. |
| "Different `btn_ref` on same-day re-fetch" | F-05, PR #22 | Not observed within this session (identical on fetch 1 and 2) | **Not reproduced** here; left as-is in its owner's files. |
| `mhFallback` = fallback page | F-03, F-12, AF-06, PR #22, T20 note | Also appended to bare valid `/dp/` loads (C-a…C-c) | **Not supported.** The marker does not distinguish fallback from a normal load. |
| Token ignored by `link.amazon` | F-03 ("ignores the token") | Changing one character breaks the link (C-e); a random code gives 403 (C-d) | **Not supported.** |

---

## 4. Verdict

1. **The three supplied codes are not Amazon ASINs** (10-digit per the official help page). Confirmed.
2. **Each supplied `link.amazon` code resolves to one specific product page, and the same page on every fetch made in two separate windows.** The code is a working lookup key (C-d, C-e).
3. **The "arbitrary fallback" conclusion is not supported.** The `plpRedirect=mhFallback` parameter is added to ordinary product pages (C-a…C-c). Flags F-03, F-12, AF-06 and the matching PR #22 wording describe a fallback that the controls do not show.
4. **Still unresolved (owner action):** no official Amazon document found in this session describes the `link.amazon` short-link format or how a code maps to a product. So whether `B0CDY277D3`, `B09B7SB46R`, `B08DKYBTPH` are the products the brief intends remains **unverified**. The owner should confirm this in Associates Central / the Share flow.
5. **Associates tracking:** no `tag=` appears in any resolved URL in this session. This matches F-07 and is unchanged.

**Recommended wording for the owner files (not edited here):** "Each supplied short link resolves to a single product page (`/dp/` IDs listed above) that is the same across fetches on 2026-11-13 and 2026-11-14. The codes are not 10-digit ASINs. Which product the owner intends, and whether the link carries their Associates tag, are unconfirmed."

---

## 5. Sources (official unless marked)

| Source | URL | Used for |
|---|---|---|
| Amazon Associates Central — Help: simple text link / ASIN definition | https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC | ASIN = 10-digit code; `/dp/ASIN?tag=` format |
| Amazon product pages (fetched 2026-11-14) | https://www.amazon.com/dp/B0CDY277D3 · https://www.amazon.com/dp/B09B7SB46R · https://www.amazon.com/dp/B08DKYBTPH | Destination identity (titles); controls C-a…C-c |
| Amazon `/dp/` for the 9-char codes (fetched 2026-11-14) | https://www.amazon.com/dp/B04G1MEwY · https://www.amazon.com/dp/B02NbDxp3 · https://www.amazon.com/dp/B00hJ57DV | R1–R3 (Page Not Found) |
| Supplied short links (fetched 2026-11-14) | https://link.amazon/B04G1MEwY · https://link.amazon/B02NbDxp3 · https://link.amazon/B00hJ57DV | R4–R6 |
| Controls (fetched 2026-11-14) | https://link.amazon/Qx3Vt8Rp1 (403) · https://link.amazon/B04G1MEwW (→ amzlinks.in 404) | C-d, C-e |
| Third-party host (observation only, **not** an official source) | https://amzlinks.in/B04G1MEwW | C-e destination |

**Not found in official sources (left unverified):** any Amazon document defining the `link.amazon` short-link format, the meaning of `btn_ref`/`lv`/`plpRedirect` parameters, or a code→product mapping. Third-party blog posts that describe `link.amazon` were returned by search and were **not** used.

---

## 6. Limits

- One observation environment (fetch tool). Other browsers, locales or logged-in sessions may show different parameters; this session did not test them.
- Two windows only (2026-11-13 per earlier records; 2026-11-14 here). Stability beyond that is not established.
- Product identity is recorded as the *destination page title*, not as a catalog-verified product record. No price, rating or availability is recorded.
