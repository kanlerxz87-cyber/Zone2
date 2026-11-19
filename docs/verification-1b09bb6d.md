# Verification record — T72, session `arena/1b09bb6d-zone2` (final integration)

**Date:** 2026-11-19 (UTC) · **Branch:** `arena/1b09bb6d-zone2` · **Baseline:** `main` @ `fc243e0`
(merge of PR #189, the T71 close-out) · **Live site:** <https://kanlerxz87-cyber.github.io/Zone2/>

This record covers the final integration session: the two stale open pull requests were taken over
and integrated, the combined tree was re-verified line by line against official sources read **today**,
every repository gate was re-run, and the release was published.

---

## 1. What this session did, in order

1. **Claimed T72 on the shared board** before any edit, with the file scope and the takeover basis.
   Committed and pushed as the first commit (`25f1abd`).
2. **Took over the two stale pull requests** under the board's 60-minute rule (§2).
3. **Integrated them** — PR #182 first (`da07775`), then PR #184 (`8c15136`) — resolving every
   conflict explicitly, never by discarding upstream work (§3).
4. **Re-verified the combined tree line by line** against the official sources, read live on
   2026-11-19 (§4, §5).
5. **Ran every repository gate** on the combined tree (§6).
6. **Wrote this record**, an executive-summary addendum, and the board close-out; then PR → merge →
   confirm the Pages deploy (§7).

**No product fact, price, star rating, review count, ASIN, commission, traffic figure, conversion or
revenue number was added, changed or inferred by this session.** Every blank stayed blank.

---

## 2. Takeover basis for the two stale pull requests

`gh pr list --state open` returned exactly two pull requests at claim time. Both were stale and
neither session had left a live claim anywhere on the board (`grep -n "60b0ea6b\|698addcd"
COORDINATION.md` → no match on the merged board):

| PR | Branch | Last commit | Age at claim (2026-11-19 19:40Z) | Session id on the board |
|---|---|---|---|---|
| #182 | `arena/60b0ea6b-zone2` | `0951e6f` @ 2026-11-19 11:25:01Z | **8 h 15 m** | none |
| #184 | `arena/698addcd-zone2` | `5759d18` @ 2026-11-19 11:18:48Z | **8 h 21 m** | none |

Both exceed the board's "more than 60 minutes old with no commits" takeover threshold by a factor of
eight. Their branches were **read and merged, never rewritten**; no upstream commit was discarded.

### What each carried

* **PR #182 (T69, session `60b0ea6b`)** — separated the *current release* registers from the
  *preserved historical board* on `suggestions.html` and `questions.html`; added
  `tests/test_front_surfaces.py`; extended `tools/verify_front.py`.
* **PR #184 (T70, session `698addcd`)** — the **Decision Room** (`decision-room.html`, 13 decisions,
  10 owner questions, 17 sources) and the **design brief it feeds** (`decision-prompt.html`); the
  scoped CSS repair for table labels clipped mid-sentence; six measured findings (CN-11…CN-16);
  `tools/build_decision_room.py`, `tools/verify_decision_room.py`, `tests/test_decision_room.py`.

---

## 3. Conflict resolution — every file, and why

No conflict was resolved by taking "ours" or "theirs" wholesale except for **generated output**, which
was discarded and rebuilt from source by the existing builders.

| File | Conflict | Resolution | Why |
|---|---|---|---|
| `content/publication.json` | 1 | **Union.** Main's five per-product `reader` blocks + PR #184's two new sources (`GOOGLE-SITEMAP`, `W3C-258`). | The two branches touched **disjoint keys** (proved by a key-by-key structural diff of base→ours and base→theirs: ours added only `/products[*]/reader` + 3 sources; theirs added only 2 sources). Re-serialising produced a byte-identical file except the two added sources — **zero formatting churn**. |
| `assets/css/publication.css` | 1 | **Union.** Main's reader-block CSS + PR #184's scoped `.cn-table` reset and Decision Room styles. | The branches appended at the same offset but added different rules; a diff-based merge keeps both with no rule duplication. |
| `tools/publication.py` | 0 (auto-merged) | Verified union by hand. | Checked that all of main's additions survive (`p['reader']`, Q68 rows, S68 proposals, CN-11) **and** all of PR #184's (`import re`, the two Decision Room nav entries, CN-12…CN-16, the register captions). |
| `board/data/measured.json` | 5 | **Discarded and regenerated** by `tools/build_board.py`. | It is a measured snapshot of the tree; a hand-merged value would be a measurement that was never taken. |
| `board/*.html`, `brief/*.html`, `guides/*.html`, `flagged.html` | 15 | **Discarded and regenerated** through the existing builders only. | Generated output. A hand-merged generated file would diverge from its generator and fail the `--check` gate. |
| `COORDINATION.md` | 1 | **Both chronologies kept**, separated by a marked HTML comment. | The board is append-only; the conflict was at the shared tail. Nothing upstream was dropped. |

### 3.1 One real defect the merge exposed — and the fix

**Both branches independently allocated the flag id `CN-11`.** Main (PR #183, session `5f7f77a4`)
already **published** `CN-11` for the product-note duplication finding; PR #184 allocated `CN-11`
for the CSS-clipping finding. A merged file with two `CN-11` rows would have shipped duplicate
anchor ids on the *Flagged for Review* page.

**Fix:** PR #184's row was renumbered **`CN-17`** — the next free id — and main's published `CN-11`
was left **unchanged**, so the already-merged cross-references in `COORDINATION.md` and
`docs/verification-5f7f77a4.md` continue to resolve. Verified afterwards: `CN-01`…`CN-17`, one row
each, zero duplicates. PR #184's new files cite no `CN-` id for that finding, so the renumber touched
exactly one line (`tools/publication.py`).

**Recorded, not hidden.** This is logged in `COORDINATION.md` and is visible on the site's
*Flagged for Review* page as `CN-17` with the same measurement and source as published by PR #184.

---

## 4. Official sources re-read live on 2026-11-19

Every source below was fetched live today through the session's page-fetch tool and the quoted text
is the text on the page. **Each row states what the site publishes and what the official page says.**

### V1 — Amazon Associates Operating Agreement (§1, §4, §5)
<https://affiliate-program.amazon.com/help/operating/agreement> — *Updated: October 15, 2025.*

* §1, verbatim: *"The links must properly use the special '**tagged**' link formats we provide and
  comply with this Agreement ('**Special Links**')."* → the site calls its outbound buttons
  **Special Links** and points every product button at a direct tagged URL.
* §1 also defines **Program Content** as *"data, images, text, link formats, widgets, links, marketing
  content, and other linking tools"* → this is the cited basis for the standing rule that no Amazon
  product imagery is copied (see S-18 / the imagery question).
* §4, verbatim: *"We do not make any representation, warranty, or covenant regarding the amount of
  traffic or commission income you can expect at any time"* → the site publishes **no** traffic,
  conversion or revenue forecast anywhere.
* §5, verbatim: *"You must clearly and prominently state the following … : 'As an Amazon Associate I
  earn from qualifying purchases.'"* → the site prints **exactly this sentence**, in a disclosure
  strip directly under the masthead on every page, and again in the footer. A mechanical check of the
  whole tree confirms it.

### V2 — Amazon Associates Program Policies (Commission Income Statement §2)
<https://affiliate-program.amazon.com/help/operating/policies> — *Updated: April 14, 2026.*

* §2(g), verbatim: *"any Product purchase that is not correctly tracked or reported because the links
  from your site to the relevant Amazon Site are not properly formatted"* is disqualified → this is the
  stated reason the reader-facing buttons are **direct tagged URLs**, not the supplied short links.
* §2(e) defines a **"Redirecting Link"** — one that sends users indirectly to an Amazon Site via an
  intermediate site without an affirmative action — as a disqualified purchase → this is the exact
  policy hook behind the still-open question about the five supplied `link.amazon` short links.
  The site does **not** call them invalid; the question stays open and published.
* §1 defines the **Session** as beginning at the click-through and ending at the first of 24 hours /
  the order / the next Special Link click → the measurement contract on `measurement.html` is written
  against this definition, not an invented one.

### V3 — FTC, *Disclosures 101 for Social Media Influencers*
<https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers> — November 2019.

* Verbatim: *"Make sure people will **see and understand** the disclosure. Place it so it's **hard to
  miss**. … Disclosures are likely to be missed if they appear only on an ABOUT ME or profile page, at
  the end of posts or videos, or anywhere that requires a person to click MORE."*
* Verbatim: *"terms like 'advertisement,' 'ad,' and 'sponsored'"* are given as clear disclosure words.
* → This is the cited authority for the decision to keep the disclosure **above the fold on every
  page** and to label every outbound product control **"paid link"** in its own text, in addition to
  `rel="sponsored nofollow noopener"`.

### V4 — Google Search Central, *Spam policies for Google web search* → **Thin affiliation**
<https://developers.google.com/search/docs/essentials/spam-policies>

* Verbatim: *"Not every site that participates in an affiliate program is a thin affiliate. Good
  affiliate sites add value by offering meaningful content or features. Examples of good affiliate
  pages include offering additional information about price, original product reviews, rigorous
  testing and ratings, navigation of products or categories, and product comparisons."*
* → This is the editorial standard the whole publication is written to, and the cited authority for
  S-06 (the decision **not** to adopt, and instead build comparison + navigation + original
  decision copy).

### V5 — Google Search Central, *Creating helpful, reliable, people-first content*
<https://developers.google.com/search/docs/fundamentals/creating-helpful-content>

* Verbatim questions include: *"Does the content provide original information, reporting, research,
  or analysis?"* and *"Does the content provide insightful analysis or interesting information that is
  beyond the obvious?"*
* → Cited by the Decision Room's editorial rows and by the note-overlap gate, whose threshold the
  site states is **its own repair budget, not an engine's published rule**.

### V6 — Google Search Central, *Control your snippets in search results*
<https://developers.google.com/search/docs/appearance/snippet>

* Verbatim heading: *"Create unique descriptions for each page on your site"*, with the body:
  *"Identical or similar descriptions on every page …"* described as unhelpful.
* → Cited by S-04 and enforced by the head-metadata gate: every indexable page carries its own
  title and meta description.

### V7 — Google Search Central, *How to specify a canonical URL with rel="canonical" and other methods*
<https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls>

* Verbatim: *"**Redirects**: A strong signal that the target of the redirect should become
  canonical."* · *"**`rel="canonical"` link annotations**: A strong signal that the specified URL
  should become canonical."* · *"**Sitemap inclusion**: A weak signal that helps the URLs that are
  included in a sitemap become canonical."*
* → This is the official basis for **DR-01**, the open question about the site's two shop front doors
  (`shop.html` vs `shop/index.html`). It is published as an **open decision with three costed
  options**, not applied.

### V8 — Google Search Central, *Build and submit a sitemap*
<https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap>

* Verbatim: *"Keep in mind that submitting a sitemap is merely a hint: it doesn't guarantee that
  Google will download the sitemap or use the sitemap for crawling URLs on the site."*
* → The site's source scope reads *"A sitemap lists URLs an owner wants crawled and indexed;
  submitting one does not guarantee indexing."* — an accurate paraphrase; **no indexing or traffic
  outcome is claimed anywhere.**

### V9 — W3C WAI, *Understanding SC 2.5.8: Target Size (Minimum), Level AA*
<https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html>

* Verbatim: *"The size of the target for pointer inputs is at least **24 by 24 CSS pixels**, except
  when: **Spacing** — Undersized targets … are positioned so that if a 24 CSS pixel diameter circle is
  centered on the bounding box of each, the circles do not intersect another target…"*
* Verbatim note: *"While not normatively required, authors are encouraged to at least meet the
  minimum size requirement of the success criterion, regardless of spacing."*
* → The published finding `CN-16` says the 142×18 px paid-link control **passes** 2.5.8 on the
  spacing exception and records it as **craft, not compliance**. The measurement is reproduced by
  the browser test suite; the criterion's wording above is what makes the distinction.

### V10 — USDA FSIS, *Food Thermometers*
<https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/food-thermometers>

* Section heading, verbatim: *"**Color is Not a Reliable Indicator that Food is Safe**"* — *"Color and
  grill marks are not indicators that food is safe to eat…"*; and *"Using a food thermometer is the
  only reliable way to ensure that foods have been cooked to a safe minimum internal temperature."*
* Section heading, verbatim: *"**Check Manufacturer's Instructions**"* — *"Before using a food
  thermometer, read the manufacturer's instructions."*
* → These are the two headings the site's source scope paraphrases
  (*"Check manufacturer insertion and care instructions. Food color alone does not establish a safe
  internal temperature."*), and the authority for the thermometer guides.

---

## 5. Line-by-line check of the combined data

### 5.1 Every product specification row

Measured from `content/publication.json` on the combined tree:

* **23** specification rows across the five products.
* **23** carry a source id; **0** carry a source id that does not resolve in the source register.
* **7** rows are blank. Every blank carries a written reason and a source, and none is filled in:

| Product | Row | Why it is blank | Source |
|---|---|---|---|
| P2 (Emeril French Door) | Cooking modes | *description says 10-in-1; image text says 11-in-1* | M3 |
| P2 | Preset count | *manufacturer description says 24; specification tile says 25* | M3 |
| P2 | Included accessories | *manufacturer description says 7; Amazon title says 6* | M3, M4 |
| P3 (Chefman single-basket) | Temperature range | conflicting manufacturer/listing readings | M5, M6 |
| P4 (ThermoMaven) | Verified accuracy | no manufacturer accuracy specification published | M7 |
| P4 | Care instructions | no published care/insertion instruction | M7 |
| P5 (ThermoMaven wireless) | Verified operating limits | no published operating range | M8 |

This is the brief's rule working as intended: **a value that cannot be confirmed from an official
source stays blank and is flagged**, rather than being inferred.

### 5.2 Product intent vs observed destination — never merged

All five submitted links carry the confirmation record in **four separate empty fields**, with the
observed redirect target in a **different** field:

| Product | Submitted link | `intended_asin` | `official_listing_url` | `confirmation_date` | `source` | `observed_redirect_target` (separate) |
|---|---|---|---|---|---|---|
| P1 | `link.amazon/B04G1MEwY` | *(blank)* | *(blank)* | *(blank)* | *(blank)* | `amazon.com/dp/B0CDY277D3` |
| P2 | `link.amazon/B02NbDxp3` | *(blank)* | *(blank)* | *(blank)* | *(blank)* | `amazon.com/dp/B09B7SB46R` |
| P3 | `link.amazon/B00hJ57DV` | *(blank)* | *(blank)* | *(blank)* | *(blank)* | `amazon.com/dp/B08DKYBTPH` |
| P4 | `link.amazon/B0c8moW59` | *(blank)* | *(blank)* | *(blank)* | *(blank)* | `amazon.com/dp/B0DHZTCNR5` |
| P5 | `link.amazon/B0f3GKalj` | *(blank)* | *(blank)* | *(blank)* | *(blank)* | `amazon.com/dp/B0DZFD6R9Z` |

The blanks are correct: the owner has not confirmed an intended product identity, and this repository
must not infer one. The tracking id `shopnow047c-20` is applied to the reader-facing Special Links,
and the site states in plain words that **a correctly shaped link is not proof of enrollment or
attribution**, because no authenticated Associates report is available here.

---

## 6. Gates on the combined tree

| Gate | Result |
|---|---|
| `tools/ci_replay.py` (every `run:` step of `pages.yml`, in order, **strict YAML parse enabled**) | **66/66 PASSED** |
| `tools/verify_publication.py` | `ok: true` — **230** HTML pages, **18** indexable, **1 453** product anchors all `rel="sponsored"`, **172** current factual rows each carrying an official source link, **0** errors |
| `tools/verify_front.py` | front gate OK — 16 pages, all checks pass |
| `tools/verify_decision_room.py` | PASS — 2 pages, 13 decisions, 10 owner questions, 17 sources |
| `tests/test_decision_room.py` | 15 mutation tests — the gate can actually fail |
| `tests/test_front_surfaces.py` | 12 regression tests pass |
| `tools/note_overlap.py` | worst pair **0.163** (gate fails above 0.25) |
| `tools/audit_site.py` | 230 published pages audited — fragments, spec_sources, prose_counts, namespaces, disclosure, debris, board: **7/7 PASS** |
| `tools/validate_data.py` | clean — 55 flags (unique ids), 50 sources, 108 rows |
| `tools/package_site.py` | 230 HTML pages packaged; 18 reader URLs indexable |
| `tools/validate_board.py` / `validate_brief.py` / `validate_intake.py` / `validate_decisions.py` / `validate_console.py` / `validate_shop.py` / `validate_audit.py` / `validate_discovery.py` / `validate_review_board.py` | all pass, including every negative-test suite (14–19 injected defects each, all firing) |

**The prose counts moved once more during the release.** While this pull request was open, a
parallel session merged PR #192 into `main`, adding flag `F-55` and source `S67` — the register
went from 54 flags and 49 sources to **55 flags and 50 sources**. The prose on `README.md` and
`EXECUTIVE_SUMMARY.md` states those counts in prose and the structural audit compares them against
the registers, so the two surfaces were reconciled to **55 flags / 50 sources** in the same commit
as the merge. The first CI run of this pull request failed on that comparison, not on any
product, source or link check; no gate was loosened and no value was invented.

**One intermediate failure, recorded honestly.** The first full replay stopped at *"Rebuild the
decision board"* → *"Decision-board gate"*. Cause: `tools/build_board.py` writes
`board/data/measured.json` **after** it runs the gates, so during its own inner replay the measured
snapshot was still the previous one and the board's derived counts did not match. Re-running the
builder once the tree was stable fixed it, and the snapshot now records
`tools/ci_replay.py exit 0 — CI REPLAY PASSED — 66 steps (all steps passed)`. No gate was loosened;
the builder's ordering was already correct and the tree simply had to settle before the measurement
was taken.

---

## 7. Irregularities raised by this session

All are published on the site's **Flagged for Review** page with their source links, and none of them
blocks the release.

| # | Irregularity | Where | Disposition |
|---|---|---|---|
| **T72-01** | **Duplicate flag id `CN-11` across the two integrated branches.** | `tools/publication.py` | **Fixed** — PR #184's row renumbered `CN-17`; main's published `CN-11` untouched so existing cross-references still resolve. Logged in `COORDINATION.md`. |
| **T72-02** | **Two shop front doors.** `shop.html` and `shop/index.html` are separate designs; only `shop.html` is in the sitemap and `index,follow`, while `shop/index.html` is the one 52 pages link to. | `decision-room.html` DR-01, flagged `CN-12` | **Open — owner decision**, published with the official canonicalisation source (V7) and three costed options. Not applied. |
| **T72-03** | **18 indexable pages vs 212 noindex**, and the noindex set contains the product pages that carry the 20 sourced specification rows. | `decision-room.html` DR-02, flagged `CN-13` | **Open — owner decision** (A: noindex the operator pages, B: index them deliberately, C: leave unlisted). Not applied. |
| **T72-04** | **Three feeds.** The same five question guides are published at ten URLs across `feed.xml` and `shop/feed.xml`. | `decision-room.html` DR-03, flagged `CN-14` | **Open — owner decision.** Not applied. |
| **T72-05** | **68 dashboard links repeated in the menu and the footer** on every page, of 197 anchors. | `decision-room.html` DR-04, flagged `CN-15` | **Advisory.** Not applied. |
| **T72-06** | **The paid-link control is 142×18 px on a phone.** | `decision-room.html` DR-05, flagged `CN-16` | **Advisory.** Passes SC 2.5.8 on the spacing exception (V9). One padding declaration would fix it; that is a design decision, not a compliance one. |
| **T72-07** | **The supplied `link.amazon` short links' exact compliance status is unresolved.** Program Policies §2(e) disqualifies "Redirecting Link" purchases, but the supplied links are not declared invalid and the enrolled-Associates workflow has not been run. | `intent.html`, `intake/` | **Open.** Published as a question with the official policy text; the reader-facing buttons use direct tagged URLs meanwhile. |
| **T72-08** | **No authenticated first-party report exists** — no Associates report, no Search Console property, no production collector host. | `measurement.html`, `flagged.html` | **Open, non-blocking.** No traffic, conversion or revenue figure is published anywhere, and none may be. |

**Carried over unchanged from earlier sessions** (not re-litigated here, still published and still
open): intended-ASIN confirmation for all five links; the P-05 two-year vs three-year warranty
divergence (`F-54`); Search Console ownership; the production collector host; and the administrator-
only Pages source-mode setting (`CN-08`).

---

## 8. What this session did **not** do

* It did not create, fill in, or infer any product specification value.
* It did not merge `intended_asin` / `official_listing_url` / `confirmation_date` / `source` with
  `observed_redirect_target`.
* It did not apply any option from the Decision Room, the suggestions board, or any preserved
  historical proposal. Nothing on those pages applies itself.
* It did not print, and did not authorise the printing of, any price, star rating, review count,
  search-volume figure, popularity claim, conversion rate or revenue forecast.
* It did not close, reopen or re-review any other session's completed work, and it did not merge or
  close any pull request other than by integrating the two stale branches above.

---

## 9. Sources, with links for manual review

| # | Source | Link | Read |
|---|---|---|---|
| V1 | Amazon Associates Program Operating Agreement | <https://affiliate-program.amazon.com/help/operating/agreement> | 2026-11-19 |
| V2 | Amazon Associates Program Policies | <https://affiliate-program.amazon.com/help/operating/policies> | 2026-11-19 |
| V3 | FTC — Disclosures 101 for Social Media Influencers | <https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers> | 2026-11-19 |
| V4 | Google — Spam policies for Google web search (Thin affiliation) | <https://developers.google.com/search/docs/essentials/spam-policies> | 2026-11-19 |
| V5 | Google — Creating helpful, reliable, people-first content | <https://developers.google.com/search/docs/fundamentals/creating-helpful-content> | 2026-11-19 |
| V6 | Google — Control your snippets in search results | <https://developers.google.com/search/docs/appearance/snippet> | 2026-11-19 |
| V7 | Google — How to specify a canonical URL | <https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls> | 2026-11-19 |
| V8 | Google — Build and submit a sitemap | <https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap> | 2026-11-19 |
| V9 | W3C WAI — Understanding SC 2.5.8 Target Size (Minimum) | <https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html> | 2026-11-19 |
| V10 | USDA FSIS — Food Thermometers | <https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/food-thermometers> | 2026-11-19 |

The full source register as published: <https://kanlerxz87-cyber.github.io/Zone2/sources.html> ·
Verification log: <https://kanlerxz87-cyber.github.io/Zone2/verification.html> ·
Flagged for Review: <https://kanlerxz87-cyber.github.io/Zone2/flagged.html> ·
Decision Room: <https://kanlerxz87-cyber.github.io/Zone2/decision-room.html>
