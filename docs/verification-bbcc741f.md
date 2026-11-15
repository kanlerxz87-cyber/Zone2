# Line-by-line verification record — session `bbcc741f` (task T40)

**Date:** 2026-11-15 (UTC) · **Repo:** `kanlerxz87-cyber/Zone2` · **Branch:** `arena/bbcc741f-zone2`
**Method:** every row below was read from the live page in this session's HTTP client during this task.
No value was copied from a prior session's note, and nothing is asserted that the cited page does not say.
Links are given so a human can repeat each fetch by hand.

## 1. The three supplied affiliate links

The brief supplied three `link.amazon` short links. Each was re-fetched today, from this session, and the
final URL plus the document title were read straight off the response.

| # | As supplied | Where it went | Page title returned | Verdict | Repeat it |
|---|---|---|---|---|---|
| P-01 | `https://link.amazon/B04G1MEwY` | `https://www.amazon.com/dp/B0CDY277D3?lv=shuf&btn_type=ss&gaOptInStatus=true&btn_ref=srctok-6c31d96765b8adfb&channelId=704&plpRedirect=mhFallback` | "Amazon.com: CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows, Sync Finish, Hi-Fry, Auto Shutoff, 2 Independent 3Qt Nonstick Dishwasher Safe Frying Baskets, Digital Double Air Fryer - Black : Home & Kitchen" | **Reproduced** — the destination the ledger publishes, for a third date | [open](https://link.amazon/B04G1MEwY) |
| P-02 | `https://link.amazon/B02NbDxp3` | `https://www.amazon.com/dp/B09B7SB46R?…&btn_ref=srctok-4796bf563b804868&channelId=704&plpRedirect=mhFallback` | "Amazon.com: Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven \| Countertop Convection Cooker, 24 One-Touch Preset Options, Extra Large Interior, Six Cooking Accessories Included : Home & Kitchen" | **Reproduced** | [open](https://link.amazon/B02NbDxp3) |
| P-03 | `https://link.amazon/B00hJ57DV` | `https://www.amazon.com/dp/B08DKYBTPH?…&btn_ref=srctok-33a7001c2f183379&channelId=704&plpRedirect=mhFallback&th=1` | "Amazon.com: Chefman Air Fryer 8 Qt \| TurboFry® 4-in-1 with 450°F Hi-Fry Option for Crispier Results \| Bake, Dehydrate, Frozen \| XL Nonstick Dishwasher-Safe Basket \| Stainless Steel : Home & Kitchen" | **Reproduced** | [open](https://link.amazon/B00hJ57DV) |

All three returned the same breadcrumb: Home & Kitchen › Kitchen & Dining › Small Appliances › Fryers › Air
Fryers. Three observations that decide what the site may do with these links:

1. **No `tag=` parameter on any of them.** An Associates special link carries the owner's ID in the URL. None of
   the three does, so as supplied they cannot pay this site's owner — the register's `F-24`, reproduced today.
2. **The `btn_ref` value changed again** since 2026-11-14 while the destination did not, which is why the token
   cannot be used as a link identity (`F-21`).
3. **`th=1` appears on P-03 only.** Recorded because the three links are not one uniform artefact; they behave
   like three separately created links, not one batch export.

## 2. The controls

| Control | Expected from the register | Observed 2026-11-15 | Verdict |
|---|---|---|---|
| A real, live ASIN placed in the token position: `https://link.amazon/B0CDY277D3` (that is P-01's own destination) | 404 from the hop service, proving the token is not an ASIN (`S36`) | Left `link.amazon`, landed on `amzlinks.in/B0CDY277D3`, returned that service's own 404 page: "404: File Not Found — Uh oh, it looks like something went wrong. You've clicked on an invalid URL." | **Reproduced** — the token is a service-issued identifier and cannot be decoded to a product from outside the account that minted it |
| An unissued 10-character token: `https://link.amazon/ZZ9QQ7X4LK` | 404, the "decisive control" of `F-20` | **HTTP 403 Forbidden at `link.amazon` itself** — no hop, no lookup | **Not reproduced as published** → raised as `F-40` |
| A bogus code that is 9 characters, `https://link.amazon/B00TEST12` (the original `F-20` control) | 404 at the hop service | Not re-run in this session; the register's own record of it stands unchallenged | cited, not re-verified |

The 403 does not overturn `F-20` — a refusal at the edge is not a fallback to a random product, which is the
reading `F-20` disproved. What it does remove is the idea that the negative control alone carries the
argument. What carries it is the positive evidence: three tokens, three distinct live listings, the same three
on every date they have been fetched. That is now stated in `F-40` rather than assumed.

## 3. Governing pages re-read

| Page | What was checked | Result | Link |
|---|---|---|---|
| Associates Program Policies | Header date; Commission Income Statement §1 attribution rules | "Updated: April 14, 2026." A Session starts at the click on a Special Link and ends at the first of 24 hours / a non-digital order / a click through someone else's link; a cart order must complete "no later than 89 days after their initial click-through"; the product must be shipped and paid for "within 180 days of the purchase". | [open](https://affiliate-program.amazon.com/help/operating/policies) |
| Associates Central → Application Review Process | The launch bar the paths page quotes | Verbatim: "we require at least three within the first 180 days", "personal orders do not qualify", "a good rule of thumb is at least 10 posts", "Content on your website must be recent (generally within the last 60 days). You must own your website.", "we aren't able to reassess an application once it's been rejected." Social networks named individually, exact page URL required, "in most cases, at least 500" organic followers. | [open](https://affiliate-program.amazon.com/help/node/topic/G8TW5AE9XL2VX9VM) |

Nothing in §3 contradicted the register. The last row *added* two constraints the board had not carried
into a decision surface: the 60-day recency test and the fact that rejection is final. Both are now on
`paths.html` and in `V-89`.

## 4. Repository review, and the irregularities this session found

| Area | What was read | Finding |
|---|---|---|
| CI contract (`.github/workflows/pages.yml`) | All 22 steps, replayed locally before every push | Healthy. Each step was extracted and run; 22/22 green at baseline and 22/22 green on this session's merged tree. |
| Data pipeline (`ledger/**` → `tools/build_*.py` → published HTML) | `build_root_data`, `build_root_views`, `build_site`, `build_summary`, `build_decisions`, `build_marketing` | Healthy and genuinely enforced: after this session added two flags and seven verification rows, three gates failed on the *stale prose counts* in `README.md` and `EXECUTIVE_SUMMARY.md`, which is the gate working as intended (the `F-17`/`F-26` drift class). Fixed by updating the labels, not by loosening the check. |
| `assets/css/style.css` @font-face | The three `url()` targets resolved against the stylesheet's own directory | **Defect, repaired here** — the URLs resolved to a path that has never existed, so Fraunces and Inter 404'd on every page and the whole site rendered in fallback system fonts. No gate could see it: a link checker walks `<a href>`, not CSS `url()`. Recorded as `F-39`; the vendored copies under `pages/assets/` and `decisions/assets/` now normalise either authoring form. |
| `README.md` | The flagged-for-review link label | **Defect, repaired here** — `[flagged for review (38 flags, F-01…F-38](url)` was missing its closing parenthesis, so the label rendered with the URL glued to it. |
| Flag-id collision | `ledger/flags.json` vs main's incoming commits | This session had taken `F-39` for the control caveat while `1b839f87` was using that id in prose for the font repair. Resolved by renumbering **this** session's rows around main's: `F-39` is the font defect (now in the register, where a reader can find it, rather than only in a commit message), `F-40` is the control caveat. Nothing was dropped. |
| Task-label collisions on the board | `COORDINATION.md` | `T40` had been claimed by three other sessions today (`08789ab3`, `3db75825`, `b6defa90`). This session's work is identified by `bbcc741f`; the number is decoration, per the board's own lesson. |
| Sibling work in flight | PRs #101 (a release-readiness board from the same Amazon review-criteria page) and #102 (a sitemap generator) | Deliberately not duplicated, deliberately not edited. `paths.html` is the *decision* view of the same source; `release/index.html` is the *compliance-score* view. If both merge, they cross-link cleanly. |

## 5. What this session did not verify, and why it is blank rather than filled

- The three products' **identity** — that the listing each link opens is the product the brief meant. Only the
  account that minted the token can answer that (`Q-18`), so every product attribute stays blank in
  `ledger/products.json` and the rows stay `UNVERIFIED`.
- Which **commission band** applies (`Q-08`), whether the owner has an approved **account** (`Q-02`), whether a
  **domain** is owned (`Q-04`), and whether a **Creators API** tier is reachable (`Q-13` gate chain) — none of
  these are discoverable from public pages, so the site says so instead of guessing.
- **Whether the 403 in §2 was caused by the token or by this agent's client.** Not resolvable from inside the
  sandbox. `F-40` states both possibilities and hands the browser test to the owner.
- Any **traffic, demand, conversion or revenue figure**. There is no authorised source for one in this
  repository, so none appears anywhere, in any phrasing.

**Manual review shortcut:** the published versions of the same rows are
[verification log](https://kanlerxz87-cyber.github.io/Zone2/verification.html) ·
[source register](https://kanlerxz87-cyber.github.io/Zone2/sources.html) ·
[flagged for review](https://kanlerxz87-cyber.github.io/Zone2/flagged.html) ·
[choose a path](https://kanlerxz87-cyber.github.io/Zone2/paths.html).
