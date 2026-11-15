# Design & content brief — the delta (T40, session `arena/3e0b3b4e-zone2`, 2026-11-15)

**Read this with `docs/design-prompt-suggestions.md`, not instead of it.** That document (T31, session
`fcb538fa`) is the standing brief: DP-01…DP-31 and its editorial rules are still the house style, and most
of them stand up when read against the tree today. This file does four things it does not:

1. **Corrects one item that is no longer true, and one that is now done.** (DP-04 and DP-22.)
2. **Completes the evidence behind the image question**, which was flagged open (IR-07 in that file) rather
   than answered. It is now answered from the licence text, and the answer changes the design.
3. **Adds the parts of a site-design prompt that were missing entirely**: the conversion layout, the
   measurement layer, the authorship/provenance story, and the "one page, one question" article spec.
4. **Restates every constraint with a source a reader can open**, in a form that can be pasted into a design
   prompt without carrying its own paraphrase of Amazon's rules.

Nothing here is implemented. Every proposal is registered on the review board at
[`discovery/suggestions.html`](https://kanlerxz87-cyber.github.io/Zone2/discovery/suggestions.html) and waits
for a recorded owner decision. Where this brief and that board disagree, the board is canonical.

---

## 1. What the prompt must be told first: the four hard constraints

These are not stylistic preferences. A design prompt that violates one of them will produce a page this site
cannot publish, however good it looks.

| # | Constraint | The sentence it comes from | Source |
|---|---|---|---|
| H-01 | Any product photograph must be Program Content, may not be stored or cached, and a **link** to one may be kept at most 24 hours. | "You will not store or cache Product Advertising Content consisting of an image, but you may store a link to Product Advertising Content consisting of an image for up to 24 hours." | [IP License §2(h)](https://affiliate-program.amazon.com/help/operating/policies) · `S44` |
| H-02 | Displaying Amazon-sourced **text** requires a specific disclaimer in plain view. | "CERTAIN CONTENT THAT APPEARS [IN THIS APPLICATION or ON THIS SITE, as applicable] COMES FROM AMAZON. THIS CONTENT IS PROVIDED 'AS IS' AND IS SUBJECT TO CHANGE OR REMOVAL AT ANY TIME." | [IP License §2(k)](https://affiliate-program.amazon.com/help/operating/policies) · `S44` |
| H-03 | A price may be shown only when Amazon serves it on the link, or it comes from Creators API / PA API. No price tracking, no alerts. | "your Site may only show prices and availability if: (a) we serve the link in which that price and availability data are displayed, or (b) you obtain … via Creators API or PA API"; "(y) … your Site must not have price tracking and/or price alerting functionality." | [Participation Requirements §2(b), §6(y)](https://affiliate-program.amazon.com/help/operating/policies) · `S53`, `S52` |
| H-04 | No star ratings or customer reviews may be displayed unless obtained through the API. | "You will not display or otherwise use any of our customer reviews or star ratings … unless you have obtained a link to that customer review or star rating through Creators API or PA API." | [Participation Requirements §6(t)](https://affiliate-program.amazon.com/help/operating/policies) · `S43` |

Two consequences that a design prompt usually gets wrong:

- **"Add product photos to look legitimate" is not available.** The most common fix for a site that looks
  untrustworthy is the one this licence forbids until an account exists. The prompt must ask for a design
  that is convincing *without* product photography — see §3.
- **Star ratings in search results are not available either**, and that is why this site will look plainer
  than a competitor's in a results page. That is a compliance outcome, not a design failure, and the design
  should not try to fake its way to it. Google's own rule forbids aggregating ratings from other sites
  ([review-snippet guidelines](https://developers.google.com/search/docs/appearance/structured-data/review-snippet) · `S49`).

---

## 2. Corrections to the standing brief

| Standing item | Status | What changed, and the evidence |
|---|---|---|
| **DP-04** — "Product imagery: until the image-licence question (Q-10, open) is answered, design with no retailer product photos … with C (manufacturer images) as a per-manufacturer follow-up" | **Corrected** | Option C is not safe as written. A manufacturer's product photograph of an *Amazon-sold* product is still not Program Content, and using it to promote an Amazon listing raises the licence question rather than avoiding it. Option A (no photographs) is the only option that is compliant today; a self-drawn specification diagram is a third path that the standing brief did not consider and is now `DS-01` option A on the board. The licence text is quoted at `S44` and the finding is `DG-01`. |
| **DP-22** — "Ship the technical basics … XML sitemap, robots.txt, canonical tags … one h1 per page" | **Partly done, partly still open** | Canonical tags and Open Graph now exist on all 17 root/discovery pages and are generated and gated (`tools/build_meta.py`). The sitemap is now generated from the file tree (`tools/build_sitemap.py`) and covers 52 submitted URLs instead of 16 hand-listed ones. `robots.txt` already existed. One `h1` per page passes across the tree. What is **still open** is that none of this fixes the underlying problem: a sitemap is a discovery mechanism, not a reason to rank. |
| **DP-23** — "Stand up Google Search Console … as the first measurement loop" | **Confirmed, and made concrete** | Now specified as event `EV-05` in the measurement design, with its fields, its blocker (`DQ-04`, the owner's Google account) and the decision it enables. See `discovery/measurement.html`. |
| **DP-07** — "Structured data only from the safe subset: Article, breadcrumbs, author — no AggregateRating, no offers" | **Confirmed and extended** | Implemented for `WebSite` + `Organization` + `BreadcrumbList` + `WebPage`/`CollectionPage` on the root pages, which had none. Still no `Product`, `Review`, `AggregateRating` or `Offer` anywhere, and the discovery gate refuses it without a measured rating behind it (`DS-06`). |
| **IR-07** — "IP License not yet read line by line — flagged" | **Closed** | Read in full on 2026-11-15. It produced H-01, H-02 and the `DG-01` / `DG-14` findings. Two obligations it imposes remain unmet and are published: the §2(k) text disclaimer (`DG-14`, `DS-14`) and any arrangement to display an image (`DG-01`, `DQ-03`). |

---

## 3. The design direction, stated as prompt-ready instructions

Paste §3.1–§3.6 into a site-design prompt. Each instruction names the constraint it must not break.

### 3.1 What the site is, in one sentence the design has to make obvious

> A research desk that publishes a specification only when an official page states it, shows both numbers
> when two official pages disagree, and leaves a blank where no page says anything.

The design must make three things visible within one screen on any product page: **the measurement**, **the
source**, and **the disagreement**. If a reader has to scroll to find out that a number is sourced, the design
has failed regardless of how it looks.

### 3.2 The conversion layout (this is the part that was missing)

- **Above the fold on a product page:** the product's official title (verbatim, attributed), three measured
  facts that decide the purchase (capacity, temperature range, footprint), and **one** primary action.
- **The action is a sentence, not a button.** "See this model on Amazon — paid link" beats a green
  "Buy Now", because the destination must never be unclear (Participation Requirements §6(w), `S45`) and
  because a site that is honest about being paid converts the readers who distrust affiliate sites.
- **Exactly one primary action per screen region.** No sticky buy bar, no exit-intent popup: pop-ups and
  layer ads are restricted (§6(o)), and a site whose whole argument is "we do not manipulate you" cannot
  open with an interstitial.
- **The comparison table is the product.** It should be the densest, most legible object on the site, with
  one source link per row rather than one per table.
- **Show the loser.** A comparison that only praises is a brochure. State which of the three is wrong for
  which household, from the measured numbers — that is the "useful comparison" Google's thin-affiliation
  guidance asks for (`S47`).

### 3.3 What to do instead of photographs

- **Measured diagrams, drawn by this project**: a to-scale footprint outline per model, a capacity
  cross-section (two 3 Qt baskets vs one 8 Qt chamber), a door-geometry diagram. Generated as inline SVG from
  the numbers already in `marketing/data/facts.json`, captioned with the row they were drawn from.
- **Never**: a stock photo of an air fryer, a competitor's product shot, an AI image of a plausible appliance,
  or a screenshot of an Amazon page. The first two misrepresent the product; the third invents one; the fourth
  reproduces Program Content outside its licence.
- The visual language should therefore be **technical-drawing**, not lifestyle photography: thin rules, precise
  annotations, a caption under every drawing that names its source row.

### 3.4 Typography and tone (the answer to "AI slop")

AI-slop prose has four readable fingerprints. The prompt should ban each by name:

| Fingerprint | The rule that removes it |
|---|---|
| A scene-setting first paragraph that contains no fact | **Every opening sentence states a number or a decision.** If the first sentence would still be true of a different product, delete it. |
| Balanced both-sides paragraphs that end in "it depends" | **Take a position and show the measurement behind it.** "Buy the 6 Qt if you cook two things at once; the baskets are the reason" is a position. "Both have their pros and cons" is not. |
| Adjective stacking where a number belongs ("powerful", "generous capacity") | **Replace the adjective with the published figure or delete the sentence.** "1700 W" is not an adjective. |
| Symmetry tics — three-item lists everywhere, "not just X, but Y", a summary box that restates the page | **No summary that repeats.** End with the decision, the caveats and the source, in that order. |

Positive instruction: write like a person who has read the two spec sheets and is annoyed that they
disagree. The voice this site earns is *irritatingly precise*, and it is the only voice a reader will believe
coming from a source that publishes blanks.

### 3.5 Authorship and provenance (missing entirely before this brief)

Google's people-first guidance asks who made the content and how, and warns that fabricated author profiles
are deception ([creating helpful content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content) · `S55`). This site has an unusually good answer and has never told it. The prompt should
produce:

- A **provenance page** that states, in plain language: what the pipeline does, what the gates reject (a
  value with no source, a page with no disclosure, a price, an invented rating), what a human decides, and what
  the desk has never done (a hands-on test, a rating).
- An **honest date** on every product page: the date the source pages were last read, not the date the file was
  generated.
- **No invented person, no generated headshot.** A desk name is honest; a fake human is the one thing that
  turns a good site into a deceptive one.

This is proposal `DS-10`, blocked on `DQ-08` (does the owner want to be the named human, or is the desk the
author?).

### 3.6 The dashboard is a different product from the publication

The root dashboard is an evidence console and should stay one — but its first screen should answer three
questions in plain words before any table appears: **what this is**, **what it has found**, **what it is
waiting on**. The publication (`marketing/`) is where a reader lands from a search; it should not contain a
single KPI chip.

---

## 4. The article spec (what every new page must satisfy)

The standing brief's "swap-the-model test" is good; this makes it mechanical enough to gate.

1. **One question in the title, answered in the first two sentences.** If the answer needs the whole article,
   the question is wrong.
2. **At least one number per section, each with a source link in the same paragraph.** A section with no
   number is a section that can be cut.
3. **One disagreement or tension, if the evidence has one.** This site's differentiator is that it shows the
   seams: 24 vs 25 presets, 1000 W vs 1700 W, two dimension tables that do not match. A page that hides the
   seams is interchangeable with every affiliate page that never looked.
4. **A stated limit.** One sentence naming what this page cannot tell the reader — no price, no rating, no
   hands-on test. It builds more trust than any badge.
5. **No claim that requires a test the desk has not run.** "Crispier", "faster", "easier to clean" are
   testable and untested. Delete them or attribute them.
6. **A single primary action**, above the fold and once more at the end. Never mid-paragraph.
7. **The disclosure**: the exact sentence in the page furniture, plus `(paid link)` beside the link itself.
   FTC guidance says a disclosure placed where a reader must click to find it is likely to be missed
   ([Disclosures 101](https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers) · `S54`).
8. **A length floor that comes from the argument, not a word count.** The prompt should say "as long as the
   measurements require" and never "1500 words minimum", because the second instruction produces padding.

---

## 5. How to earn traffic, restated under the actual rules

The attractive tactics and what stops each one.

| Tactic | Verdict | The rule that decides it |
|---|---|---|
| Publish 100 AI-written pages targeting long-tail keywords | **Not available** | "Scaled content abuse … using generative AI tools or other similar tools to generate many pages without adding value" (`S46`). |
| Rewrite competitor reviews and add a comparison table | **Not available** | "Thin affiliation … product descriptions and reviews are copied directly from the original merchant without any original content or added value" (`S47`). |
| Buy search ads that deep-link straight to Amazon | **Not available** | Search results must send users to your site, "not directly, or indirectly via a Redirecting Link, to an Amazon Site" (`S50`, `S51`). |
| Six pages, each answering one buying question from data already measured | **The recommended path** | It is the "original content or added value" that `S47` and `S55` name, and it needs no new fact-gathering. `DS-03`. |
| Turn each measured cross-source disagreement into one article | **Recommended, and the differentiator** | Nobody else has done the comparison, so it cannot be copied, which is exactly what `S47` rewards. |
| Measure which page sends people where, then write the next page from that | **Recommended, and blocked on the owner** | Needs a cookie-free counter and Search Console; `DS-11` and `DQ-04`. |

The honest summary: this site's traffic plan is *fewer, better pages built from measurements a competitor has
not made*, and its ceiling right now is not content volume but the absence of any measurement to say which
page worked.

---

## 6. What the design prompt must not be told

Four instructions that would produce a non-compliant site, listed because they are the four a generic prompt
writes by default:

1. **"Add a product carousel that updates prices"** → `S52` forbids tracking/alerting; `S53` forbids a price
   that Amazon did not serve.
2. **"Show star ratings and review counts to build trust"** → `S43` forbids displaying them without API
   access; `S49` forbids aggregating them from elsewhere.
3. **"Write a punchy author bio with a photo"** → `S55` names fabricated creator profiles and AI headshots as
   deception.
4. **"Optimise for 'best air fryer 2026' and write 2000 words"** → the superaltive requires a test the desk has
   not run (FTC: you cannot talk about your experience with a product you have not tried, `S54`), the word
   floor produces padding, and the aggregate of those two is the thin-affiliation pattern `S47` demotes.

---

## 7. What is still missing before this brief can be finished

Not an omission in this document — missing information that no amount of writing can supply.

| ID | Missing | Why it blocks the brief | Where it is tracked |
|---|---|---|---|
| `DQ-01` | An Associates account and marketplace | Decides whether any of §3.2 can be monetised at all, and whether product photography ever becomes possible | [questions](https://kanlerxz87-cyber.github.io/Zone2/discovery/questions.html#DQ-01) |
| `DQ-02` | The intended ASINs or product URLs | The site currently writes about the listings the supplied links resolve to, which may not be the products the brief meant | [questions](https://kanlerxz87-cyber.github.io/Zone2/discovery/questions.html#DQ-02) |
| `DQ-03` | Whether a static page may hot-link an Amazon image | Decides whether §3.3's diagrams are a permanent substitute or a stopgap | [questions](https://kanlerxz87-cyber.github.io/Zone2/discovery/questions.html#DQ-03) |
| `DQ-05` | Which surface the "AI slop" complaint was about | Decides whether §3.6 or §3.4 is the first job | [questions](https://kanlerxz87-cyber.github.io/Zone2/discovery/questions.html#DQ-05) |
| `DQ-08` | Who the author is | §3.5 cannot be written without a name or a decision to use none | [questions](https://kanlerxz87-cyber.github.io/Zone2/discovery/questions.html#DQ-08) |

The design can proceed on `DS-01` option A, `DS-03` option A and `DS-06` option A without any of these being
answered. Nothing that depends on them has been built.
