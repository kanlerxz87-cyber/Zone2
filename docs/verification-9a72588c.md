# Verification record — T72, session `arena/9a72588c-zone2` (9a72588c) — 2026-11-19 (UTC)

Task: **wave 2 of the review board** — the 2026-11-19 brief's suggestion wave on
`docs/review-board.json`, its renderer, its gate, and the five generated review pages.
Scope, files touched, and exclusions are recorded in `COORDINATION.md` (T72 row).

## Live official-source reads (all on 2026-11-19, UTC)

Every source this wave adds or leans on was fetched live today. "Quote present" means the
text the register records was found verbatim in the fetched page content.

| # | Source row | URL | What the live read confirmed |
|---|---|---|---|
| V1 | S91 | fsis.usda.gov — Safe Minimum Internal Temperature Chart | Page live; title matches; page states "Last Updated: Apr 14, 2025"; the recorded quote ("Cook all food to these minimum internal temperatures, as measured with a food thermometer…") is present verbatim, as is the 165 °F poultry row PS-19's concept relies on. |
| V2 | S92 | developers.google.com — SEO Starter Guide | Page live; title matches; both quotes present verbatim: "Think about the words that a user might search for…" (§ Expect your readers' search terms) and "Every change you make will take some time to be reflected on Google's end…" plus "The content is up-to-date: Check in on previously published content and update it as needed" (§ Make your site interesting and useful). |
| V3 | S93 | developers.google.com — Understanding page experience | Page live; title matches; the recorded quote ("Google's core ranking systems look to reward content that provides a good page experience…") is present verbatim, as is the mobile self-assessment question "Does your content display well on mobile devices?". |
| V4 | S94 | ftc.gov — CAN-SPAM Act: A Compliance Guide for Business | Page live; title matches; the recorded quote ("Despite its name, the CAN-SPAM Act doesn't apply just to bulk email…") is present verbatim, as are the identify-the-ad, physical-postal-address and opt-out requirements PW-05/PQ-11 rest on. |
| V5 | S95 | developers.google.com — Spam policies, scaled content abuse section | Section live on the page (same URL as S84); the recorded quote ("Scaled content abuse is when many pages are generated for the primary purpose of manipulating search rankings and not helping users…") is present verbatim, including the generative-AI example bullet. |
| V6 | S96 | amazon.com/dp/B0DZFD6R9Z | Page fetched live through its redirect; the listing title as served today is recorded as the quote: "CHEF iQ Sense | Smart Wireless Meat Thermometer | 3 Ultra-Thin Probes | WiFi Unlimited Range | 1000°F Heat Safe | 5 Sensors | BBQ, Grill, Oven, Smoker, Air Fryer | Gen3". No price was recorded anywhere in this wave (the fetched page shows prices; the register prints none). |
| V7 | S97 | amazon.com/dp/B0DHZTCNR5 | Page fetched live through its redirect; the listing title as served today is recorded as the quote: "ThermoMaven 1 Sec Professional Digital Meat Thermometer, ±0.5℉ Accuracy | NIST&NSF Certified, Auto-Rotate Bright LED Screen, IP67 Waterproof for Grill BBQ, Stocking Stuffers Gifts for Men, Black". This also confirms the ledger's open Q-21 (newer-model situation) still holds today. |
| V8 | S84 | developers.google.com — Spam policies | Page live; the thin-affiliation quote recorded in wave 1 remains on the page (§ Thin affiliation); the scaled-content section is separately quoted as S95. |
| V9 | S85 | developers.google.com — Write high quality reviews | Page live; page states "Last updated 2025-12-10 UTC" (matches the register); the wave-1 recorded quote is present verbatim, and the wave-2 arguments additionally rest on "Demonstrate that you are knowledgeable about what you are reviewing—show you are an expert" and "Describe key choices in how a product has been designed and their effect on the users beyond what the manufacturer says", both present verbatim today. |
| V10 | S83 | developers.google.com — Creating helpful, reliable, people-first content | Page live; title matches; the wave-1 recorded quote sits in § How (the content was created); today's read also confirmed the self-assessment questions PW-01/PW-04 lean on ("Does the main heading or page title avoid exaggerating or being shocking in nature?", "Are you using extensive automation to produce content on many topics?"). |
| V11 | S80 | affiliate-program.amazon.com — Associates Program Policies | Page live; header states "Updated: April 14, 2026"; the recorded quote's section sits deeper in the 11-chunk page (verified by T53 when recorded). PQ-13's argument rests on this page being the program's documentation surface, not on re-quoting that section; noted here rather than over-claimed. |

## Local measurements taken on the committed tree (2026-11-19)

These are the wave-2 measurement rows PM-14…PM-18 in the register; each was run exactly as
its `how_measured` states:

- **PM-14** — `grep -rl 'google-site-verification' --include='*.html' . | wc -l` → **0**; page
  count via `tools/build_sitemap.published_pages()` → **226**.
- **PM-15** — `publication.indexable_paths()` contains **no** review page (16 indexable reader
  URLs; the five review pages deploy noindex under `tools/package_site.py`).
- **PM-16** — register JSON counts before wave 2: **12/12** proposals awaiting a decision,
  **0/9** questions answered.
- **PM-17** — `ls guides/*.html | wc -l` → **20** (the wave-1 prose printed 13).
- **PM-18** — no verifier rule in `tools/` scans generated prose for filler phrases
  (`grep -rniE 'look no further|fast-paced|game-changer|in today' tools/*.py` → no
  enforcement rule; `verify_publication` checks anchors and row counts, not prose fillers).

## Counts the renderer no longer types (PI-07)

The rebuild derives, at build time, from the registers and the tree: the guide-page count
(`guides/*.html`), the ledger question-register size (`ledger/questions.json` → 22), the
marketing question-set size (`marketing/data/editorial.json` → 10), the season-claiming idea
ids, and every wave count (`wave` field; rows without one read as the 2026-11-16 wave).

## Gates run on the final tree (2026-11-19)

- `tools/build_review_board.py --check` → 5 pages, drift **0**.
- `tools/validate_review_board.py` → PASS, 0 warnings (18 sources, 19 proposals, 13 questions,
  9 ideas, 18 measurements, 12 findings, 8 irregularities, 16 requirements).
- `tools/test_review_board.py` → **21 injected defects, each fired · 1 control passed** (two
  new mutations cover the wave-2 `recommended_option` rule).
- Full `tools/ci_replay.py` → **62/62 PASSED** (including audit_site, verify_publication,
  seo_audit, sitemap freshness, package checks, intake/board/brief/decision gates, note
  overlap, browser viewport and accessibility scans).

Two freshness gates forced regeneration through their own builders when this wave landed
(`release/index.html` — one derived token, `pages_linking_dp` 144 → 145, because the new S96/S97
citations make review-ideas.html a page that cites amazon.com/dp URLs, untagged by design;
and one transient regeneration of `brief/index.html` that was returned to its committed state
after PW-01's problem text was reworded so it no longer contains the literal token the brief's
"AI-powered page counter" matches). Both are derived surfaces rebuilt through their existing
builders only; no other session's data was edited.

## Irregularities found and recorded (PI-06…PI-08 in the register)

1. **PI-06** — wave-1 idea ids sit inside the proposal id space (PS-13…PS-17); wave 2 gives
   proposals the PW- prefix and preserves existing ids verbatim.
2. **PI-07** — three printed counts had drifted from the tree (guide count; the two sister
   question-register sizes); the rebuild derives all three.
3. **PI-08** — two unregistered open PRs (#182 `60b0ea6b`, #184 `698addcd`) re-use task ids
   held by merged sessions and appear nowhere on the coordination board; not touched, file
   scope kept disjoint, recorded for the next integration session.

## What this session did not do

- No verified value anywhere else was changed; no price was recorded; blanks stay blank.
- The two open PRs' files were not touched, merged, closed or edited.
- No register row on the board was marked decided — every wave-2 row ships as
  `AWAITING_DECISION`, and the answer sheet's pipeline section states that nothing is
  implemented while a row reads that way.
