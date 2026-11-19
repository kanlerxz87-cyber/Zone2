# Verification record — T74 (claimed as T72), session `arena/aecb287a-zone2`, 2026-11-19 (UTC)

Scope: the measured gaps the requirements register still reported as open — S-04 (titles and
descriptions), S-24 (internal links from the journal), S-20 (mobile-first pass). Claim: `COORDINATION.md`
§ "T72 claim". Base: `main` at `fc243e0`.

## 1. Official sources read live on 2026-11-19

| Id | Source | What was checked | Used for |
|---|---|---|---|
| V1 | https://developers.google.com/search/docs/appearance/snippet | Best-practice section "Create unique descriptions for each page on your site"; snippet is truncated by device, so no fixed length is required | S-04: unique meta descriptions |
| V2 | https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html | SC 2.5.8 (AA): 24×24 CSS px minimum; **Inline** exception for targets inside a sentence | S-20: which links the tap rule must cover |
| V3 | Understanding SC 2.5.5 (AAA), 44×44 CSS px — **not fetched separately**; the 44 px figure and its link are stated in V2's text | SC 2.5.5 (AAA): 44×44 CSS px threshold | S-20: the 44 px floor used for header, footer and control targets |

Amazon Associates policy text relevant to this change (sponsored marking, tag on Special Links) was **not**
re-read this session. The existing links are unchanged in destination and attribute; no new Amazon claim is made.

## 2. S-04 — titles and meta descriptions (RQ-01): not re-done on this branch

Closed on `main` by session `672f9c4c` (PR #192, merged), with its own gate (D8, `tools/seo_audit.py`). This branch merged
`main` and **kept `main`'s S-04 implementation unchanged**, so the two sessions' edits do not diverge.

Re-measured on the merged tree on 2026-11-19: published pages with a missing description 0; duplicated descriptions 0;
duplicated titles 0. The six pages without a description are Playwright's own HTML under `node_modules/`
(installed by `tools/ci_replay.py`), which are not published pages.

## 3. S-24 — internal links (RQ-18)

Before: 4 journal articles had no link to `marketing/comparison.html`, `marketing/buying-guide.html` or
`guides/index.html` (`board/data/measured.json` `guides_unlinked` 4).
Change: each of `journal/basket-vs-oven.html`, `journal/dual-basket-air-fryers.html`, `journal/index.html`
and `journal/why-every-number-has-a-source.html` gained a "Where to go next" block with those three links.
After: `guides_unlinked` 0. The targets all exist (checked by the CI link step in `ci_replay`).

## 4. S-20 — mobile-first pass (RQ-16), measured in headless Chromium

Method: `@sparticuz/chromium` 131 with `puppeteer-core` 23, rendered at 390×844, mobile emulation, over the
64 reader pages (`board/data/measured.json` `reader_pages` 64). Measured:
- **text under 11 px** — elements whose own text node has a computed font size below 11 px;
- **small controls** — links, buttons, summaries and inputs under 44×44 px, excluding inline links inside
  running text (V2 Inline exception);
- **horizontal overflow** — `scrollWidth` minus viewport width.

| Stage | Text under 11 px | Small controls | Pages with overflow |
|---|---|---|---|
| Before the change | 3,098 | 5,271 | 0 |
| After the mobile type floor | 344 | 5,269 | 0 |
| After the 44 px control rule and the sticky bar | 344 | 1,574 | 0 |

Changes:
- `assets/css/publication.css` — a block at `max-width:780px` restates each selector whose font size is under
  11 px (58 selectors, from `style.css`, `publish.css` and `publication.css`) at 11 px, with `!important` kept
  where the original used it. Desktop rules are unchanged.
- `assets/css/publication.css` — at `max-width:780px`, header, footer, filter, button and chip controls get
  `min-height:44px` and `display:inline-flex`.
- `tools/publication.py` + `compare.html` — a phone-only sticky bar ("Compare · five listings", "Back to the list",
  "Shop the edit"). Measured on the rendered page: the bar sits at the bottom of the 844 px viewport.

Residuals, not claimed as finished (so S-20 stays open in the register, with a note):
- 344 text runs of 9–10.6 px remain on `marketing/*` pages and `flagged.html` table cells. They use a separate
  stylesheet and pill/code styles; the change belongs in that stylesheet's owner's scope.
- 1,574 small controls remain, mostly table-cell links, status chips and breadcrumb items, which sit in
  content tables. Several are narrow inline-flex items; a human sign-off pass is still needed.

## 5. Gates

- `tools/ci_replay.py` — 63/63 steps passed (run after all HTML/CSS/generator edits and again after the board
  regeneration; see the close-out in `COORDINATION.md`).
- `tools/validate_board.py`, `tools/build_board.py --check` — pass.
- `tools/build_front.py --check`, `tools/build_site.py --check`, `tools/build_decisions.py --check`,
  `revalidation/scripts/build.py --check` — no drift.
- `tools/build_head_meta.py --audit` — 0 problems across 111 contract pages.
- `tools/validate_data.py`, `tools/audit_site.py`, `tools/verify_publication.py` — pass.

## 6. Board rows changed

`board/data/requirements.json`: RQ-18 moved from `overstated` to `matches` (the tree now supports the
"Implemented" status word the brief gives it); RQ-16 keeps `no-status-given` and records the partial pass.
No other row changed. RQ-01 keeps `main`'s value from PR #192.

## 7. Not done in this task (owner or later action)

- Search Console verification (SG-29, RQ-28): needs the owner's Search Console property. Not attempted.
- Reader capture choice (SG-30, RQ-29) and the self-hosted analytics endpoint (RQ-25): an owner choice and a
  hosting decision (GitHub Pages cannot run the endpoint). Unchanged.
- Associates Special-Link test (RQ-22): needs the owner's signed-in Associates session. Unchanged.
- Product photography (S-18, RQ-14): a decision. Unchanged.
- Bare Amazon links on the evidence pages (`class="src"` / `pb-src`) remain untagged by design (1,071 untagged
  Amazon links across all published pages were counted earlier this session, most on evidence and process pages), as `tools/link_builder.py` documents. Shopping-style product links on reader pages carry
  `tag=shopnow047c-20` and `rel="sponsored"`.
