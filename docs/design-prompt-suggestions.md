# Design & Content Prompt Suggestions — Zone2 (task T31, session `fcb538fa`)

**Purpose.** This is the suggestion set that *feeds the prompt used to design and write the site*: it says
what the site should look like, what to write, how to earn organic traffic, and which editorial rules keep
it from reading like AI-generated filler — with every hard constraint anchored to an official source so the
design prompt cannot accidentally produce a policy violation.

**How to use it.** Sections 1–7 are written so they can be pasted, verbatim or edited, into a site-design /
content-generation prompt. Section 8 lists the information that is still missing (nothing may be assumed
where a cell is marked missing). Nothing in this document is implemented: like every other suggestion on
this project, each item reaches the owner first as a proposal on the
[Suggestions decision board](https://kanlerxz87-cyber.github.io/Zone2/pages/suggestions.html), and is only
built after an owner choice is recorded there (precedent: T29 `ledger/suggestions.json`, field `decision`).

**Division of labour (so nothing is built twice).**

| Surface | Owner | What lives there |
|---|---|---|
| `pages/suggestions.html` + `pages/questions.html` (PR #61) | session `2499438c` (T29) | Canonical owner-decision board (SG-01…SG-10) and open-questions register (Q-01…Q-16) |
| Dashboard links to both (PR #64) | session `fb49a226` (T30) | Discoverability only |
| `docs/design-prompt-suggestions.md` + `playbook.html` (this task) | session `fcb538fa` (T31) | The *design/editorial/SEO suggestion set* and its published page — proposals only, not a second decision store |
| `decisions/` requirements layer (PR #69, merged) | session `d0135100` | Requirements/status review layer — its author dropped its duplicate registers and read the canonical ones |
| `marketing/` editorial voice upgrade (PR #75, merged, task T32) | session `8c4236ad` | First execution of DP-02/DP-09-style editorial rules (facts byte-identical, voice only) + [SG-04](../pages/suggestions.html#SG-04)-gated topic queue |
| `marketing/trending-topics.html` (PR #65) / trendy topic articles (PR #70, superseding #68) | sessions `bf8f07a7` / `cffe745a` | Overlapping proposals still owned by their sessions — flagged in §8 (IR-06) for consolidation |

**All statements in §1 were fetched live by this session on 2026-11-15** (UTC) from the official pages
linked in each row. Everything else in §§2–7 is explicitly labelled *suggestion* (a judgment) or
*missing* (an open question) — suggestions are never presented as program facts.

---

## 1. Verified constraints the design prompt MUST obey (official sources, fetched 2026-11-15)

| # | Verified constraint (what the official page says) | Official source | Fetched |
|---|---|---|---|
| C-01 | Every page must state, clearly and prominently, verbatim: “As an Amazon Associate I earn from qualifying purchases.” | [Associates Operating Agreement §5](https://affiliate-program.amazon.com/help/operating/agreement) | 2026-11-15 |
| C-02 | The site must not promise or imply expected traffic or commission income (“We do not make any representation … regarding the amount of traffic or commission income you can expect”). | [Operating Agreement §4](https://affiliate-program.amazon.com/help/operating/agreement) | 2026-11-15 |
| C-03 | Product prices/availability may be shown only if Amazon serves the link containing them, or the data comes from Creators API / PA API; comparison displays must show the lowest “new” (and, if provided, lowest “used”) Amazon price. | [Program Policies — Participation Requirements §2(b)](https://affiliate-program.amazon.com/help/operating/policies) | 2026-11-15 |
| C-04 | Claims about products must not be “inaccurate, overbroad, deceptive or otherwise misleading”. | [Program Policies — §2(b)](https://affiliate-program.amazon.com/help/operating/policies) | 2026-11-15 |
| C-05 | Links to Amazon product lists (search results, events, department pages) require additional original content on the site that is relevant to the link. | [Program Policies — §2(b)](https://affiliate-program.amazon.com/help/operating/policies) | 2026-11-15 |
| C-06 | Limited-time promotion mentions must be removed from the site as soon as the promotion ends. | [Program Policies — §2(b)](https://affiliate-program.amazon.com/help/operating/policies) | 2026-11-15 |
| C-07 | Customer reviews and star ratings may not be displayed unless obtained through Creators API or PA API. | [Program Policies — Participation Requirements §6(t)](https://affiliate-program.amazon.com/help/operating/policies) | 2026-11-15 |
| C-08 | The site must not have price-tracking or price-alerting functionality. | [Program Policies — §6(y)](https://affiliate-program.amazon.com/help/operating/policies) | 2026-11-15 |
| C-09 | Link shorteners/buttons must never make it unclear that the link goes to an Amazon Site; URLs and user agents must not be cloaked. | [Program Policies — §6(w), §6(v)](https://affiliate-program.amazon.com/help/operating/policies) | 2026-11-15 |
| C-10 | Search traffic must be driven to *your own site first*: organic/unpaid search results are allowed “so long as … those … results send users to your site and not directly, or indirectly via a Redirecting Link, to an Amazon Site”. | [Program Policies — §6(f)](https://affiliate-program.amazon.com/help/operating/policies) | 2026-11-15 |
| C-11 | Special Links must carry the assigned Associates tag (`XXXXX-##`); the supplied short links resolve **without** a `tag=` parameter, so as supplied they cannot earn (flag F-24, re-observed this session). | [Program Policies — §2(a)–(b)](https://affiliate-program.amazon.com/help/operating/policies) · observed on [link.amazon/B04G1MEwY](https://link.amazon/B04G1MEwY) | 2026-11-15 |
| C-12 | Application bar for websites: public site the applicant owns, “at least 10 posts” of robust original content, content “generally within the last 60 days”, at least three qualifying sales in the first 180 days (personal orders excluded). | [Application Review Process](https://affiliate-program.amazon.com/help/node/topic/G8TW5AE9XL2VX9VM) | 2026-11-15 |
| C-13 | What Amazon calls a good affiliate/review site: content that “adds value … by giving them insight on a subject or product they might not get easily” and “a unique experience or insight that is not available anywhere else”. | [Application Review Process](https://affiliate-program.amazon.com/help/node/topic/G8TW5AE9XL2VX9VM) | 2026-11-15 |
| C-14 | Email/SMS Special Links are allowed only when the communications are solicited (opted into). | [Program Policies — §4](https://affiliate-program.amazon.com/help/operating/policies) | 2026-11-15 |
| C-15 | Affiliate/paid links should be qualified with `rel="sponsored"`; qualified links are not treated as link spam. | [Google Search Central — Qualify your outbound links](https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links) · [Google spam policies (link spam)](https://developers.google.com/search/docs/essentials/spam-policies) | 2026-11-15 |
| C-16 | “Scaled content abuse” — many pages generated mainly to manipulate rankings, “typically … large amounts of unoriginal content that provides little to no value to users, no matter how it’s created”, explicitly including “using generative AI tools … to generate many pages without adding value” — is a spam policy violation. | [Google Search Central — Spam policies, “Scaled content abuse”](https://developers.google.com/search/docs/essentials/spam-policies#scaled-content) | 2026-11-15 |
| C-17 | “Thin affiliation” — affiliate pages whose product descriptions/reviews are copied from the merchant with no original content or added value — is demoted; Google names “meaningful content or features” (extra information, original reviews, rigorous testing and ratings, navigation, comparisons) as what makes affiliate sites good. | [Google Search Central — Spam policies, “Thin affiliation”](https://developers.google.com/search/docs/essentials/spam-policies#thin-affiliate-pages) | 2026-11-15 |
| C-18 | Endorsements must be honest and not misleading; a material connection (e.g. earning commission) must be disclosed “clearly and conspicuously”. | [FTC — The FTC’s Endorsement Guides: What People Are Asking](https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking) | 2026-11-15 |
| C-19 | Program Content or Special Links may not be used to develop machine-learning models or related technology without Amazon’s “express prior written approval”. | [Program Policies — Participation Requirements §5](https://affiliate-program.amazon.com/help/operating/policies) | 2026-11-15 — **gap in the compliance ledger, see IR-04** |
| C-20 | The three supplied short links currently resolve to `/dp/B0CDY277D3` (CHEFMAN 6 Qt Dual Basket Air Fryer Oven), `/dp/B09B7SB46R` (Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven) and `/dp/B08DKYBTPH` (Chefman Air Fryer 8 Qt TurboFry® 4-in-1), all in breadcrumb “Home & Kitchen › Kitchen & Dining › Small Appliances › Fryers › Air Fryers”. This is *destination evidence only* — it does not confirm the brief’s intended products (flag F-03). | [link.amazon/B04G1MEwY](https://link.amazon/B04G1MEwY) · [link.amazon/B02NbDxp3](https://link.amazon/B02NbDxp3) · [link.amazon/B00hJ57DV](https://link.amazon/B00hJ57DV) | 2026-11-15 |

---

## 2. Design-direction suggestions (how the site should look and feel)

*Every row is a suggestion (a judgment), not a program fact. The “Constraint” column names the official
rule it must respect, or “design judgment” where no official source applies.*

| ID | Suggestion | Options | Recommendation | Constraint / basis |
|---|---|---|---|---|
| DP-01 | Split the site into two layers: a **front-of-house** (reader-first marketing/editorial home: hero, featured guide, latest articles, product cards) and an **evidence layer** (the existing dashboards, ledgers, verification pages). | A) Both layers, dashboard stays at `index.html` and the marketing home lives as a clearly linked subpage; B) Marketing home at `index.html`, dashboard moves under a subpath; C) Keep one combined surface as today. | **A** — lowest breakage (CI requires the root dashboard files; the landing-page audit requires every companion namespace to stay linked from `index.html`), and it fixes the “internal tool” first impression immediately. | Design judgment; CI constraints in [`.github/workflows/pages.yml`](https://github.com/kanlerxz87-cyber/Zone2/blob/main/.github/workflows/pages.yml) and `tools/audit_site.py` |
| DP-02 | Editorial homepage design: one strong hero statement (“every claim on this site links to its source”), a featured buying guide, three product cards (one per destination), trust strip (disclosure, last-verified date, “how we verify”), and a single primary CTA per card. | A) Editorial hero + cards; B) Magazine grid; C) Keep KPI dashboard as the front page. | **A** — it reads as a publication, keeps the verification story as the differentiator, and displays the disclosure where C-18 demands prominence. | C-01, C-18; design judgment |
| DP-03 | Typography and colour: keep the evidence tables legible (the current system is fine) but give the marketing layer its own warmer, magazine-style layout: larger headings, real article typography, pull quotes for “what we verified”. | A) New stylesheet for the marketing layer only; B) Re-skin everything. | **A** — evidence pages stay byte-stable (drift gates), marketing layer gets personality. | Design judgment |
| DP-04 | Product imagery: until the image-licence question ([Q-10](../pages/questions.html#Q-10), open) is answered, design with no retailer product photos: use typographic cards, manufacturer press/media assets where their terms allow, and screenshots-free comparison diagrams. | A) No photos until [Q-10](../pages/questions.html#Q-10) answered; B) Use Amazon product images now; C) Use manufacturer images only. | **A** (with C as a per-manufacturer follow-up after each site’s terms are read). **B must not be chosen before the licence is read line by line.** | [Q-10](../pages/questions.html#Q-10) open on the canonical board; [Program Policies — IP License](https://affiliate-program.amazon.com/help/operating/policies) (not yet read line by line — flagged, IR-07) |
| DP-05 | Trust layer on every marketing page: exact disclosure sentence in the header area and again beside each set of links, a “last verified” date, and a visible link to the verification methodology. | A) Header + per-article box; B) Footer only. | **A** — “clearly and prominently” (C-01) and “clearly and conspicuously” (C-18) are placement rules, not footer rules. | C-01, C-18 |
| DP-06 | Comparison UX: side-by-side columns with a shared spec table where **every row cell carries its source link**, and cells that cannot be sourced render “— (unverified)” rather than a value. | A) Keep the proven renderer pattern; B) Hand-built tables. | **A** — this repo’s gates already enforce it; reuse the pattern. | Verification rule of the brief; `tools/validate_data.py` |
| DP-07 | Structured data (schema.org) only from the safe subset: `Article`, breadcrumbs, author — **no** `AggregateRating`, **no** `offers`/price unless served by Amazon/Creators API. | A) Safe subset only; B) Full `Product`+`Review` schema. | **A** — review/rating markup would display ratings the policy forbids without API data. | C-03, C-07 |
| DP-08 | Make decisions reviewable in the UI: every marketing card that depends on an undecided suggestion shows a small “proposed — awaiting owner decision” chip linking to the canonical board. | A) Chips; B) Silent publishing. | **A** — preserves the “review before implement” requirement. | T29 board; brief |

---

## 3. Article & topic suggestions (catchy, trendy, but compliant)

*Status: **proposals only.** They depend on owner decisions [SG-02](../pages/suggestions.html#SG-02) (products/niche width) and [SG-04](../pages/suggestions.html#SG-04) (article
formats) on the canonical board, and every product mention must keep the destination caveat (F-03) until
[Q-03](../pages/questions.html#Q-03) is answered. No price, no star rating, no “we tested it” claim may appear (C-03, C-07, and [SG-05](../pages/suggestions.html#SG-05)).*

| ID | Article angle (working title) | Hook / search intent | Format & placement | Guardrails | Basis |
|---|---|---|---|---|---|
| DP-09 | “Dual-Basket Air Fryers Explained: What 6 Qt Really Means When It’s Two 3 Qt Baskets” | Informational — people search capacity/format questions before buying | Explainer, hub of the “air fryer formats” cluster | Use only manufacturer-stated specs (two 3 qt baskets, Sync Finish, 200–450 °F, 1700 W); no prices, no ratings | Manufacturer pages behind `marketing/data/facts.json` (verified rows); C-13 |
| DP-10 | “Air Fryer vs. Toaster Oven vs. French-Door Oven: Which Countertop Format Fits Your Kitchen?” | Commercial comparison — the highest-intent query the three destinations naturally answer | 3-way comparison article linking the comparison page | Destination caveat (F-03) in the intro; spec-table rows each sourced | C-05 (original content required alongside product-list links), C-13, C-17 |
| DP-11 | “The 450 °F Question: What a ‘Hi-Fry’-Style Finishing Heat Actually Does” | Informational/feature education | Short feature deep-dive | Temperature claims quoted from the manufacturer page only | Verified spec rows (Hi-Fry max 450 °F); C-04 |
| DP-12 | “French-Door Air Fryer Ovens: Why a 26 QT Interior Changes Weeknight Cooking” | Informational, capacity-led | Listicle-style feature article around the Emeril destination | No performance claims beyond the listing/manufacturer text; no comparison to specific rival models with unverified figures | C-04, C-13 |
| DP-13 | “Feeding a Crowd: What 8 Qt Actually Lets You Cook in One Basket” | Informational, capacity-led | Article around the Chefman 8 Qt destination | Same rules; link the buying guide, not just the product | C-05, C-17 |
| DP-14 | “How to Read an Air Fryer Spec Sheet (Watts, Basket Splits, Temperature Ranges)” | Educational hub — evergreen, linkable, genuinely useful | Pillar article for the cluster; internal links out to all three product articles | Every number sourced to a manufacturer row | C-13, C-17 |
| DP-15 | Seasonal gift/cookout guides (holiday season, summer) | Seasonal spikes | Calendar-planned articles | **Promotion-mention discipline:** any limited-time mention must be removed when it ends (C-06); no price tables (C-03) | C-03, C-06 |
| DP-16 | “What Amazon’s Associate Application Actually Checks (10 Posts, 60 Days, Original Content)” — meta article about building this very site, from verified application rules | Unique/first-hand — nothing else says it better than our own verified transcription | Transparency article in the evidence layer | Quoted from the application page only | C-12, C-13 (verbatim source) |
| DP-17 | Avoid: “top 10 air fryers 2026”, “best air fryer under $X”, “is it worth it?” hype clones | — (would require prices/ratings/testing claims we do not have) | Not proposed | Would violate C-03 (prices), C-07 (ratings), C-04 (unverifiable superlatives), or duplicate thin affiliate content | C-04, C-07, C-17; [SG-05](../pages/suggestions.html#SG-05) open |

**Article-quality test (paste into the writing prompt):** every paragraph must contain at least one
concrete, sourced detail (a specification, a quoted rule, a dated observation) or first-hand context the
site actually has; delete any sentence that would still be true about any product (the “swap-the-model
test”); state up front what we could *not* verify; end with disclosure + sponsored link marking.

---

## 4. Organic-traffic suggestions (how real people find the site)

| ID | Suggestion | Why / official basis |
|---|---|---|
| DP-18 | Build one topic cluster: pillar = DP-14 spec-sheet explainer; spokes = the three product articles, the 3-way comparison, and the buying guide; every spoke links back to the pillar and to at least two siblings. | C-17 (good affiliate sites add navigation and comparisons); design judgment on topology |
| DP-19 | Hard rule for every SEO action: search users land on *our* pages first; never redirect or point search listings at Amazon. | C-10 — verbatim §6(f) |
| DP-20 | Editorial cadence aimed at the application bar: reach ≥10 substantial posts, keep the newest content within ~60 days, then maintain ≥1 fresh article/month. | C-12 — verbatim application-review thresholds (these are *Amazon’s* numbers, not a traffic promise) |
| DP-21 | Mark every affiliate link `rel="sponsored"` (plus `nofollow`), and never use a link shortener that hides the Amazon destination. | C-15, C-09 |
| DP-22 | Ship the technical basics with the marketing layer: XML sitemap, `robots.txt`, canonical tags, descriptive titles/descriptions, one `h1` per page, mobile-first layout. | Design judgment (standard SEO hygiene); Google outbound-link doc for link hygiene |
| DP-23 | Stand up Google Search Console + a sitemap submission as the first measurement loop; until it reports, treat all traffic forecasts as **missing information** (nothing in the repository measures search demand). | Missing-data discipline (brief); no official source claims otherwise — flagged IR-08 |
| DP-24 | Distribution channels chosen to match Amazon’s accepted-site list for applications (Facebook, Instagram, X, YouTube, TikTok, Twitch — public pages with a substantive organic following, “in most cases, at least 500”). | [Application Review Process](https://affiliate-program.amazon.com/help/node/topic/G8TW5AE9XL2VX9VM) — verbatim, 2026-11-15 |
| DP-25 | Earned links over bought links: the transparency article (DP-16), the spec-sheet pillar, and downloadable checklists are the linkable assets; never buy or trade links. | [Google spam policies — link spam](https://developers.google.com/search/docs/essentials/spam-policies#link-spam) — “exchanging goods or services for links” listed as violation |
| DP-26 | Add `hreflang`/market split **only after** [Q-01](../pages/questions.html#Q-01) (US vs Japan marketplace) is answered; language and marketplace must match the Associates account. | [Q-01](../pages/questions.html#Q-01) open; C-11 (tag must be the account’s) |
| DP-27 | No traffic, ranking or revenue numbers may be promised anywhere on the site (marketing copy included). | C-02 — verbatim OA §4 |

---

## 5. Anti-“AI slop” editorial rules (paste into the content prompt)

1. **Source gate (already enforced):** no sentence prints a value without a link to the official page it
   came from; unsourceable cells render “unverified” with the reason, never an inferred value.
2. **No invented experience:** never write “we tested”, “in our kitchen”, or first-person results unless
   the owner actually performed the test ([SG-05](../pages/suggestions.html#SG-05) undecided).
3. **No banned surfaces:** no prices (C-03), no star ratings/review counts (C-07), no price-drop/price-alert
   widgets (C-08).
4. **Specificity test / swap-the-model test:** if a paragraph survives swapping in a different model name,
   delete it — it is filler (C-13’s “insight … not available anywhere else”).
5. **Scale guard:** publish no page whose main purpose is covering a keyword; every page must help a user
   do something (C-16 verbatim).
6. **Thin-affiliation check before publish:** does the piece add at least one of Google’s named value-adds —
   extra information, original review, rigorous testing we actually did, navigation, comparison? If none,
   do not publish (C-17 verbatim).
7. **Named authorship & editorial responsibility** on marketing pages (Google’s site-reputation guidance
   treats stated authorship and editorial integration as review factors — observed on the policy page,
   2026-11-15).
8. **Disclosure placement:** disclosure sentence in the first screenful *and* next to link blocks (C-01,
   C-18).
9. **Freshness dates visible**; re-verify spec rows at least annually and after any destination change;
   remove expired promotion mentions the day they end (C-06).
10. **Human editorial pass:** generation may draft, but a pass that applies rules 1–9 is mandatory before
    publish — record who approved it (mirrors Google’s “editorial oversight” factor).

---

## 6. Decision-making improvement suggestions

| ID | Suggestion | Basis |
|---|---|---|
| DP-28 | Keep **one** decision store (canonical `ledger/suggestions.json` / `pages/suggestions.html`) and one questions register; every other page links to it instead of opening a parallel register. | T30 integration note; duplication observed in open PRs #65/#68/#69 — IR-06 |
| DP-29 | Definition of done for every suggestion: options → recommendation → owner records `decision` → implementation commit → verification row → deploy check. Nothing skips stages. | Existing T29 workflow, extended |
| DP-30 | One in-progress claim per session on the board; stale claims (>60 min, no commits) get re-claimed or closed by the next session (the rule exists; T27 shows why it must be applied — IR-03). | Project coordination rules |
| DP-31 | Quarterly (or per-merge) re-verification cadence for official sources, with the page dates showing the last *source check* date — the current generated “verified 2026-11-14” eyebrow can disagree with newer checks (IR-07). | T29’s recorded display issue |
| DP-32 | Keep the automated gates as the floor, not the ceiling: gates prove HTML matches the ledger, not that a sentence is true — always read the deployed page after merge (lesson recorded by three sessions). | `COORDINATION.md` process notes |
| DP-33 | Every launch-facing claim gets a “launch gate” row: account approved ([Q-02](../pages/questions.html#Q-02)), tag configured ([Q-05](../pages/questions.html#Q-05)/F-24), ASINs confirmed ([Q-03](../pages/questions.html#Q-03)), domain question settled ([Q-04](../pages/questions.html#Q-04)) — the site cannot honestly go into revenue mode until these are answered. | C-11, C-12; canonical Q register |

---

## 7. Missing information — discovery suggestions (what must be answered before decisions)

The canonical open-questions register is [pages/questions.html](https://kanlerxz87-cyber.github.io/Zone2/pages/questions.html)
(Q-01…Q-16: marketplace, account status, true ASINs, domain ownership, tracking plan, commission band,
image licence…). This session adds only the *discovery* actions nobody had written down:

| ID | Missing information | How to discover it | Blocks |
|---|---|---|---|
| D-01 | Search demand for the candidate topics (keyword volumes, SERP competitors) | Set up Google Search Console after first publish; export Google Keyword Planner data via the owner’s Google account (no keyword data exists in this repository — nothing may be invented) | DP-09…DP-18 prioritisation, [SG-04](../pages/suggestions.html#SG-04) |
| D-02 | Whether the owner will operate the US or JP marketplace (and whether these destinations sell on amazon.co.jp) | Owner checks Associates Central country ([Q-01](../pages/questions.html#Q-01)); agent checks amazon.co.jp listings once true ASINs are known ([Q-03](../pages/questions.html#Q-03)) | [SG-01](../pages/suggestions.html#SG-01), [SG-09](../pages/suggestions.html#SG-09), DP-26 |
| D-03 | Whether manufacturer press images may be used on the site | Read each manufacturer’s site terms/media-licence pages line by line ([Q-10](../pages/questions.html#Q-10) covers Amazon’s IP licence) | DP-04 |
| D-04 | Conversion/click baseline | Requires Associates tag live first (F-24/F-07) and then the tracking module (M-09) — nothing to measure until then | [SG-09](../pages/suggestions.html#SG-09), campaign optimisation |
| D-05 | Whether the Creators API is available to this account (rating/price display, product images) | Application + 10 qualifying sales/30 days prerequisite on the official page ([Creators API introduction](https://affiliate-program.amazon.com/creatorsapi/docs/en-us/introduction)) | DP-07 (rich schema), ratings display ([SG-07](../pages/suggestions.html#SG-07)) |
| D-06 | Whether training any model on Program Content is needed for the platform’s own tooling | If yes, seek Amazon’s express prior written approval (C-19) or design the pipeline to not do it | Platform M-07 content engine — IR-04 |

---

## 8. Flagged for review (irregularities found by this session — non-blocking)

| ID | Irregularity | Status | Source / evidence |
|---|---|---|---|
| IR-01 | `COORDINATION.md` on `main` contained two stray git conflict-marker lines (`=======`, `>>>>>>> origin/main`) left by an earlier merge | **Fixed content-preserving** in the T31 claim commit (both sides of the text kept; only the marker lines removed) | `COORDINATION.md` history around old lines 2897/2952 |
| IR-02 | The block after that marker duplicates the `d3ce1c29` T26 closing record that already appears earlier in the file (two copies of one record) | Kept (append-only rule: nothing deleted) — owner may dedupe | `COORDINATION.md` §“T26 — closing record” |
| IR-03 | Task T27 still marked `in progress` (owner `0f44536f`) with no commits since 2026-11-14 — stale beyond the 60-minute takeover rule | Open — board owner to close or re-claim | `COORDINATION.md` task board |
| IR-04 | Compliance ledger (31 rules) has **no rule for Participation Requirements §5** — “You will not, without our express prior written approval, use, or allow any third party to use, any Special Links or Program Content to develop machine learning models or related technology”, directly relevant to this brief’s AI content engine | Open — **candidate finding; not written into `ledger/flags.json` by this session** because F-39…F-41 are reserved by session `d0135100` and F-42 is used by session `42fa4918`; owner to add it as the next free id | [Program Policies §5](https://affiliate-program.amazon.com/help/operating/policies), fetched 2026-11-15; `ledger/compliance.json` holds R-01…R-31 without it |
| IR-05 | The generated pages’ eyebrow reads “verified 2026-11-14” although checks ran 2026-11-15 (date source is `ledger/products.json.verified_utc`) | Open — generator-owner decision (recorded by T29, carried here) | `tools/build_site.py` date source |
| IR-06 | Three open PRs at integration time propose overlapping suggestion/question surfaces: #65 (dropped its root pages, adds `marketing/trending-topics.html`), #68 (adds root `suggestions.html` + `questions.html`), #69 (adds `decisions/` layer that reads the canonical registers). Risk: two registers answering the same question | Open — integrate with consolidation: canonical board stays T29; newcomers must link, not duplicate | [PR #65](https://github.com/kanlerxz87-cyber/Zone2/pull/65), [PR #68](https://github.com/kanlerxz87-cyber/Zone2/pull/68), [PR #69](https://github.com/kanlerxz87-cyber/Zone2/pull/69) |
| IR-07 | Image licensing for the marketing layer is unverified ([Q-10](../pages/questions.html#Q-10) open; Amazon IP Licence not yet read line by line) | Open — DP-04 designs around it | [Program Policies — IP License](https://affiliate-program.amazon.com/help/operating/policies) |
| IR-08 | No search-demand/traffic measurement exists anywhere in the repository; “generate organic traffic” cannot yet be evidenced with data | Open — D-01 defines the discovery path | Repository inspection 2026-11-15 |
| IR-09 | Resolved links still carry **no Associates `tag=`** (F-24 re-observed today): the site cannot earn until a tagged link strategy exists | Open, owner action | [link.amazon/B04G1MEwY](https://link.amazon/B04G1MEwY) resolved 2026-11-15 |
| IR-10 | Brief-to-destination mapping still unconfirmed: supplied codes are 9 characters; Amazon documents ASINs as 10-**digit**; destinations are stable but may not be the intended products (F-01/F-03) | Open, owner action ([Q-03](../pages/questions.html#Q-03)) | [ASIN help](https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC); three link resolutions above |
| IR-11 | The source register’s notes column for rows S38…S42 was written character-by-character (“T; h; e; …”) by the session that appended them; URLs and dates are correct, the notes are garbled on the published Sources page | Open — change request logged for the register owner; not edited here (shared data, other sessions active) | `sources.html` rows S38–S42 · `ledger/sources.json` |

---

## 9. Verification appendix — what this session fetched itself (2026-11-15)

| # | Checked | Result | Official source |
|---|---|---|---|
| V-1 | Disclosure sentence + agreement currency | §5 sentence verbatim; “Updated: October 15, 2025” | https://affiliate-program.amazon.com/help/operating/agreement |
| V-2 | No-income-expectation clause | §4 sentence verbatim | https://affiliate-program.amazon.com/help/operating/agreement |
| V-3 | Policies currency + price rule + comparison rule + product-list original-content rule + promo-removal rule + no-misleading-claims rule | “Updated: April 14, 2026”; §2(b) text verbatim | https://affiliate-program.amazon.com/help/operating/policies |
| V-4 | §6(f) search rule, §6(t) ratings rule, §6(v)/(w) cloaking/shortener rules, §6(y) price-tracking rule, §6(z), §4 solicited-email rule, §5 ML-training clause | All verbatim | https://affiliate-program.amazon.com/help/operating/policies |
| V-5 | Application review thresholds | “at least 10 posts”, “generally within the last 60 days”, “You must own your website”, “at least three within the first 180 days”, “personal orders do not qualify”, social list + 500-followers rule of thumb | https://affiliate-program.amazon.com/help/node/topic/G8TW5AE9XL2VX9VM |
| V-6 | Google `rel="sponsored"` guidance | “Mark links that are advertisements or paid placements … with the sponsored value”; page “Last updated 2025-12-10” | https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links |
| V-7 | Google scaled-content-abuse + thin-affiliation definitions | Verbatim (quoted in C-16/C-17) | https://developers.google.com/search/docs/essentials/spam-policies |
| V-8 | FTC endorsement-disclosure principle | “should be disclosed clearly and conspicuously”; 2023 revision of the Guides | https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking |
| V-9 | Supplied link 1 resolves | `B04G1MEwY` → `/dp/B0CDY277D3` — “CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows…”; breadcrumb Air Fryers; **no `tag=`** | https://link.amazon/B04G1MEwY |
| V-10 | Supplied link 2 resolves | `B02NbDxp3` → `/dp/B09B7SB46R` — “Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven…”; no `tag=` | https://link.amazon/B02NbDxp3 |
| V-11 | Supplied link 3 resolves | `B00hJ57DV` → `/dp/B08DKYBTPH` — “Chefman Air Fryer 8 Qt \| TurboFry® 4-in-1…”; no `tag=` | https://link.amazon/B00hJ57DV |
| V-12 | Repo gates on the claim tree | `validate_data` 0 errors / 0 warnings (37 sources, 82 rows); `build_site --check` 39 built / 0 drifted; `build_root_views --check` clean; `build_summary --check` clean; `build_marketing --check` current; `tests/test_pipeline.py` 15/15; `audit_site.py` 97 pages, 5/5 PASS | local run, 2026-11-15 |

**Nothing on this page was inferred.** Any value this session could not confirm from an official source is
left out or marked missing — never filled in.
