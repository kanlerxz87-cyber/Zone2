# Verification record — T73 (claimed as T72), session `arena/aecb287a-zone2`, 2026-11-19 (UTC)

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

## 2. S-04 — titles and meta descriptions (RQ-01)

Before (measured, `board/data/measured.json` at 2026-11-19T11:44Z): 219 pages in the board's contract,
`no_desc` 7, `dup_desc` 2, `dup_titles` 4.
Measured by a separate scan of all 228 published HTML files before the edit: 7 pages without a description,
duplicated descriptions shared by 39 `pages/` pages and 4 `decisions/` pages, and 4 duplicated titles.

Changes (each through its generator; no hand edit except `404.html`):

- `tools/head_meta.py::meta_description()` — a new helper: the page's own lead paragraph, whitespace collapsed,
  cut at a word boundary at 158 characters. Used by `tools/build_site.py` (`pages/`), `tools/build_decisions.py`
  (`decisions/`) and `revalidation/scripts/build.py` (`revalidation/`).
- `tools/build_site.py` — category band titles now include the band id (`Category band 4.00% · C-04` vs `… · C-OTH`);
  module titles now include the module id (`M-11 · Niche discovery`), so the module page no longer duplicates the niches page.
- `tools/build_thermometers.py` — the marketing desk title is "Meat thermometers, compared row by row",
  so it no longer duplicates the guide's title.
- `404.html` — a description was added (one hand-written sentence; it makes no product claim).

After (scan of the same 228 files): missing descriptions 0, duplicated descriptions 0, duplicated titles 0.
Board measure after the rebuild: `no_desc` 0, `dup_desc` 0, `dup_titles` 0.

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

- `tools/ci_replay.py` — 62/62 steps passed (run after all HTML/CSS/generator edits and again after the board
  regeneration; see the close-out in `COORDINATION.md`).
- `tools/validate_board.py`, `tools/build_board.py --check` — pass.
- `tools/build_front.py --check`, `tools/build_site.py --check`, `tools/build_decisions.py --check`,
  `revalidation/scripts/build.py --check` — no drift.
- `tools/build_head_meta.py --audit` — 0 problems across 111 contract pages.
- `tools/validate_data.py`, `tools/audit_site.py`, `tools/verify_publication.py` — pass.

## 6. Board rows changed

`board/data/requirements.json`: RQ-01 and RQ-18 moved from `overstated` to `matches` (the tree now supports the
"Implemented" status word the brief gives them); RQ-16 keeps `no-status-given` and records the partial pass.
No other row changed (checked by diff against `HEAD`: only these three rows differ).

## 7. Not done in this task (owner or later action)

- Search Console verification (SG-29, RQ-28): needs the owner's Search Console property. Not attempted.
- Reader capture choice (SG-30, RQ-29) and the self-hosted analytics endpoint (RQ-25): an owner choice and a
  hosting decision (GitHub Pages cannot run the endpoint). Unchanged.
- Associates Special-Link test (RQ-22): needs the owner's signed-in Associates session. Unchanged.
- Product photography (S-18, RQ-14): a decision. Unchanged.
- Bare Amazon links on the evidence pages (`class="src"` / `pb-src`) remain untagged by design (1,071 untagged
  Amazon links across all published pages were counted earlier this session, most on evidence and process pages), as `tools/link_builder.py` documents. Shopping-style product links on reader pages carry
  `tag=shopnow047c-20` and `rel="sponsored"`.
