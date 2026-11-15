# The design prompt these suggestions feed

**Date:** 2026-11-15 · **Session:** `f8e18ca8` · **Status:** proposals only — nothing here is implemented
without a recorded owner decision. The machine-readable board is `audit/data/suggestions.json`; the
published pages are `audit/suggestions.html`, `audit/gaps.html` and `audit/decision-cost.html`.

Two things this document is *not*. It is not another list of the same ten suggestions already
published on `pages/suggestions.html` (SG-01…SG-10) or `marketing/improvements.html` (DS-01…DS-14) —
it starts from a fresh measurement of the deployed site and reaches different conclusions, and where
it overlaps with an earlier board it says so. And it is not a promise about traffic: the brief asks
for organic traffic, and the honest answer is that no official source can tell anyone how much
traffic a page will earn. What *can* be done is remove the documented reasons a page does not earn
any. That is the shape of everything below.

---

## 1. The finding that changes the brief

The brief asks for a polished marketing affiliate site that does not read like "AI slop". The site
that exists is the opposite failure. It is a verification instrument: 116 pages, 42 registered
sources, 705 table rows each ending in an official-source link, a 38-item flag register, and a set
of gates that will fail a build if a row loses its citation. It is, by measurement, more honest than
almost anything in its category.

What it does not have is a reason for a person to arrive. Concretely, from the review
(`audit/index.html`):

| What a reader needs | What the site has |
|---|---|
| A page that shows the products before a script runs | Eight root pages whose tables are empty in the HTML (A-01) |
| A disclosure they can see next to the link | A correct sentence at the bottom of the page, after the links, on 24 of 77 pages (A-02) |
| A person to trust | No author, no About page, no contact route on any page (A-07) |
| Something to look at | Zero photographs in 116 pages (A-08) |
| One page about a product | Six pages called "products", eight flag registers (A-06) |

So the design problem is not "make it prettier". It is **make the evidence visible to a reader who
did not come for the evidence.** The phrase to design to, and the one this document recommends
putting at the top of the design prompt, is:

> The site should read like a consumer-magazine test desk that shows its working — not like a
> compliance ledger that happens to have a homepage.

That single sentence resolves most of the disagreements in this repository. A test desk has an
editor's name on it, photographs, a verdict at the top and the method at the bottom. A compliance
ledger has 705 rows and no reason for anyone to read row one.

---

## 2. The prompt, in the order it should be applied

Each line names the finding it fixes and the board row that implements it. Nothing here contradicts
an official source; where a rule is quoted, the quote is on `audit/method.html` with its link.

### 2.1 Structure — one public site, one page per intent (A-06 → R-06)

- The public reader-facing site is **marketing/** (it already has a masthead, a desk name, canonical
  URLs, OG tags and JSON-LD). It becomes the site.
- The seven evidence namespaces move under a single labelled archive route and are `noindex`ed.
  Nothing is deleted: the brief requires the findings to persist, and the findings are the asset.
- Every public page answers **one** reader question. "Which air fryer should I buy" is one page, not
  six.
- The archive is linked from one place — "how this page was verified" — so a sceptical reader can
  reach the 705 rows in one click, and a casual reader never sees them.

### 2.2 The first screen (A-01, A-09 → R-01, R-09)

- Tables are **pre-rendered HTML**. The 102 KB data script leaves the critical path. A crawler and a
  reader with a blocked script see the same rows.
- The first screen is a **verdict**, not a hero: one product named as the pick for the most common
  need, one sentence of why, and a link to the full comparison. No carousel, no "welcome to".
- Budget: under 200 KB to first render. Two font families is one too many for a table site; subset
  or drop the display face (A-09).

### 2.3 Trust surfaces (A-07 → R-07)

- A named author or editor, a photograph, one line of real background, and a link to an About page
  that states the method in plain language.
- A visible **"Last checked"** date per article, because on this site the date is meaningful: it is
  when the spec table was re-read against the manufacturer's page.
- A contact route. A site that argues for transparency and offers no way to correct it is asking to
  be trusted on its own word.
- **Never** an invented persona. The site's own editorial rule already forbids it, and Google's
  site-reputation example treats an unattributed affiliate article as likely to draw action.

### 2.4 Disclosure placement (A-02 → R-02)

- The exact sentence, above the first affiliate link, in the visual weight of a standfirst.
- Keep the footer copy. Two placements is what the FTC brochure's "hard to miss" test actually asks
  for; one placement at the bottom is what the 24 pages currently do.

### 2.5 Evidence a reader can see (A-08 → R-08)

- Photographs. Own units where they exist (which then also unlocks first-hand claims); manufacturer
  imagery otherwise, under the Associates IP licence, positioned next to the tagged link the licence
  requires.
- One comparison table per category with the decision factors as columns: capacity, footprint,
  baskets, window, temperature ceiling, dishwasher-safe parts. Every cell sourced, every unsourced
  cell blank. The blanks are the design feature, not a gap to fill.
- A one-screen "what we could not confirm" box on each product page. It is the single most
  differentiating element available, and this repository is the only place that can build it
  credibly.

### 2.6 Voice — the anti-slop rules, stated as lint (→ R-14)

Publish the editorial standard as a page and lint every article against it. The measurable ones:

| Rule | Why | How it is enforced |
|---|---|---|
| No first-hand claim without a dated record | FTC: "You can't talk about your experience with a product you haven't tried" | the existing linter family already raises `FABRICATED_EXPERIENCE` |
| No superlative without the spec that supports it | vague praise is what "AI slop" reads like | `SUPERLATIVE` lint on any unfootnoted "best/longest/quietest" |
| No number without a source | the one rule that makes this site worth reading | every valued table row carries a source id or a blank, gated |
| No em-dash-per-sentence cadence | the strongest tell of machine prose in this repository | measured: the 12 editorial root pages run 1.5–3.3 em/en dashes per 100 words, while the median across all 122 prose pages is 0.61 — the two registers are separable by a number, so a budget belongs in the lint |
| No sentence that would survive on any other product | the definition of filler | the existing filler list, extended to the marketing namespace |
| No "we" without a person behind it | ties back to 2.3 | author field required before publish |

The em-dash measurement is worth pausing on, because it is the one number in this review that maps
directly onto the phrase "reads like AI slop" and the one that is completely mechanical. Note what it
does and does not say. It does not say a dash is bad, and the page with the highest rate
(`compliance.html`, 3.29) is not the worst page — it is the most list-like. What it does say is that
the editorial voice and the record-keeping voice sit in measurably different registers (1.5–3.3 per
100 words against a 0.61 median across 122 prose pages), and a drafting pass can be held to the lower
one without touching a single fact.

### 2.7 What to write (A-06 → R-06, and the traffic page)

Six article shapes that a test desk can publish **today**, with the evidence the repository already
holds, and that are not the "10 best air fryers 2026" listicle:

1. **The measuring-piece explainer** — what a quart of basket capacity actually holds, argued from
   the three verified capacities, with a photograph of food in a basket.
2. **The window question** — why two of these three have viewing windows and one does not, and what
   that changes in use.
3. **Basket versus oven** — geometry decides this, not brand; it is already written (`journal/`) and
   it is the model the rest should follow.
4. **The two pages that disagree** — the manufacturer's page and the listing state different figures
   for one specification. Publishing the discrepancy, with both sources, is the most trust-building
   page this site can have and no competitor will copy it.
5. **What "Hi-Fry" actually does** — a specification read, not a review.
6. **The counter-footprint test** — does it fit under a cabinet; a tape measure and a photograph.

Every one of these is answerable from the repository's verified data, requires no product claim, and
none of them can be generated in bulk without a person forming a view. That is the point.

---

## 3. What would make this go wrong

Stated plainly, because the brief is asking for volume and the official documents are asking for the
opposite:

- **Volume before evidence** produces the exact page shape Google's scaled-content section
  describes. The repository already has 116 pages for three products; the next 116 would not be a
  growth strategy.
- **Automation dressed as testing** is prohibited by the FTC guidance and by the site's own rule.
- **A generated author** is worse than no author.
- **A price** — even an accurate one — is a compliance breach on this site unless Amazon serves it
  or the API supplies it.
- **A performance metric** published from this repository would be invented, and inventing one
  would destroy the only asset the project has.

---

## 4. If only three things are done

1. **R-07 — name the author, publish the method.** Free, reversible, and it answers the first two
   questions Google's guidance asks.
2. **R-02 — move the disclosure above the links.** Under an hour, and it removes a live compliance
   argument from 24 pages.
3. **R-01 — pre-render the tables.** The only change that makes the site legible to a reader who is
   not running JavaScript, and it removes the 102 KB payload at the same time.

Everything else on the board is worth doing. These three are worth doing before anything else,
because each of them makes the existing work visible rather than adding to it.

---

## 5. Questions that must be answered before this prompt can be executed

Full detail and how to close each: `audit/gaps.html`.

| ID | Question | Blocks |
|---|---|---|
| G-01 | Approved Associates account, marketplace and tag? | every revenue item |
| G-02 | Which three products, confirmed by the owner? | every product claim |
| G-05 | Who is the named author? | R-07, the whole trust layer |
| G-08 | Which pages are public? | R-06, R-10 and the sitemap |
| G-11 | Which language and market? | content plan, disclosure wording |
| G-12 | Has anyone handled the products? | any review, rating or "best for" claim |
| G-15 | Where do decisions get recorded? | whether any of this is ever chosen |

---

## 6. Sources

Every rule quoted in this document, with the exact text and the fetch date, is registered in
`audit/data/sources.json` and rendered with its link on `audit/method.html`. The load-bearing ones:

- **SA-01** Operating Agreement §5 — the disclosure sentence, verbatim — <https://affiliate-program.amazon.com/help/operating/agreement>
- **SA-03** Program Policies, Participation Requirements §2(b) — Special Links must use the Associates ID — <https://affiliate-program.amazon.com/help/operating/policies>
- **SA-04** Program Policies §2(b) — the only two permitted routes to display a price — same URL
- **SA-05** Program Policies §3(t) — reviews and star ratings only via the API — same URL
- **SA-10** Google, spam policies — scaled content abuse and thin affiliation — <https://developers.google.com/search/docs/essentials/spam-policies>
- **SA-12** Google, creating helpful, reliable, people-first content — <https://developers.google.com/search/docs/fundamentals/creating-helpful-content>
- **SA-13** Google, JavaScript SEO basics — pre-rendering is still a great idea — <https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics>
- **SA-14** Google, how to write high quality reviews — first-hand evidence — <https://developers.google.com/search/docs/specialty/ecommerce/write-high-quality-reviews>
- **SA-16** FTC, Disclosures 101 — disclosure placed with the message, not at the end — <https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers>
- **SA-17** Google, site reputation policy — the unauthored affiliate article example — within the spam-policies URL above

Two sources in the register (**SA-18**, **SA-19**) are marked *carried*: this session did not
re-fetch them, and the method page says so rather than implying a fresh check.
