# Irregularities register (session 5ba0cb60, snapshot 2026-11-13 UTC)

Each item states the evidence and a disposition. Items marked **Owner decision** need a human choice. Nothing here is hidden or auto-resolved.

## 1. Supplied inputs

| ID | Irregularity | Evidence | Disposition |
|---|---|---|---|
| I-01 | The codes in the supplied links are **not** ASINs. Each `link.amazon/<code>` redirects to a different ASIN. | Supplied `https://link.amazon/B04G1MEwY` → [amazon.com/dp/B0CDY277D3](https://www.amazon.com/dp/B0CDY277D3). `https://link.amazon/B02NbDxp3` → [amazon.com/dp/B09B7SB46R](https://www.amazon.com/dp/B09B7SB46R). `https://link.amazon/B00hJ57DV` → [amazon.com/dp/B08DKYBTPH](https://www.amazon.com/dp/B08DKYBTPH). | Resolved. Use the ASIN in the canonical `/dp/` link. Flag to owner: confirm these are the intended products. |
| I-02 | Whether `link.amazon` is an approved short-link domain could **not** be verified. Session 181863ad's board states that `link.amazon` is "NOT valid Amazon domains" and that `amzn.to` is the official host. | Observed: `link.amazon` redirects to amazon.com. No official Amazon page checked in this audit states which short domains are sanctioned. | **Unverified claim, not adopted.** The redirect was observed, and the claim about validity is left open for review. |
| I-03 | The resolved URLs carry no Associates tag. They carry share tokens instead (`btn_ref=srctok-…`, `channelId=704`, `plpRedirect=mhFallback`). Associates requires the Associate ID as a URL parameter. | Final URLs of the three redirects; [Program Policies §2(b)](https://affiliate-program.amazon.com/help/operating/policies). | **BLOCKING for commission.** Owner must supply the Associate ID. The agent will not invent one. See compliance row C-04. |
| I-04 | Commission attribution cannot be verified for any supplied link. | No tag (I-03); no Associates account connected; no reports supplied. | **Owner decision.** Account and reporting access needed. |

## 2. Product data conflicts (both values recorded, row flagged)

| ID | Product | Conflict | Evidence | Disposition |
|---|---|---|---|---|
| I-05 | Chefman 8 Qt (`B08DKYBTPH`) | Title says "450°F Hi-Fry Option". Spec table says Max Temperature **400 °F**. | [amazon.com/dp/B08DKYBTPH › Product information](https://www.amazon.com/dp/B08DKYBTPH) | Flag. Do not publish 450°F unless the owner confirms it. |
| I-06 | Emeril (`B09B7SB46R`) | Item details list **six** included components. The description says "Included are 7 premium accessories", and Configuration says "7 Accessories". | [amazon.com/dp/B09B7SB46R › Product information](https://www.amazon.com/dp/B09B7SB46R) and Product Description | Flag. Do not publish a single accessory count. |
| I-07 | Chefman 6 Qt (`B0CDY277D3`) | Capacity: "6 liters" (spec) vs "6 Quart" (Measurements). 6 liters is about 6.3 US quarts. Color: "Black" (title) vs "Black, Gray" (spec). | [amazon.com/dp/B0CDY277D3 › Product information](https://www.amazon.com/dp/B0CDY277D3) | Flag. Both values recorded. |
| I-08 | Chefman 8 Qt, Emeril | Non-descriptive fields. Chefman 8 Qt: "Model Number: Large Air Fryer" (descriptive text; the part number is RJ38-SQSS-8T). Emeril: "Air Frying Technology: True". | Same pages, Item details and Features & Specs | Recorded as-is with a note. Do not treat as model codes or technology names. |
| I-09 | Emeril | Item weight is not listed. Warranty duration is not stated (only a PDF link). | Same page | Left **blank** and flagged. |

## 3. Values left blank (unverified)

| ID | Field | Why blank | Disposition |
|---|---|---|---|
| I-10 | Commission rate (all products) | The official rate schedule (`/help/operating/schedule`) redirects to sign-in. Secondary sites (for example [affserp.com](https://affserp.com/blog/how-much-does-amazon-associates-pay), [ecomchief.com](https://ecomchief.com/blogs/news-1/amazon-affiliate-commission-rates-2026), [stackinfluence.com](https://stackinfluence.com/blog/how-does-amazon-affiliate-work-a-sellers-guide), [brandid.app](https://brandid.app/blog/amazon-affiliate-program/)) report Kitchen 4.5% and Home 3%. Those are secondary and are **not** adopted, per the verification rule. | **Blank and flagged.** Owner can confirm against the Associates Central rate card after sign-in. |

## 4. Policy conflicts with the brief

| ID | Conflict | Evidence | Disposition |
|---|---|---|---|
| I-11 | The brief asks for pricing analysis. Associates policy restricts displaying prices and availability to Amazon-served links or PA-API / Creators API data. | [Participation Requirements §2(b)](https://affiliate-program.amazon.com/help/operating/policies), compliance row C-05. | **Owner decision.** Prices and availability are withheld from all artifacts. Observed values are reported in the chat, not written to the repo. Options: (a) keep withheld, (b) set up PA-API access, then publish via that route. |
| I-12 | Ratings, review counts, and BSR came from product page reads, not from PA-API. The IP License excludes "data mining, robots, or similar data gathering and extraction tools" from the license. | [IP License §1](https://affiliate-program.amazon.com/help/operating/policies), compliance row C-09. | **Owner decision.** Flagged for review. Recommend PA-API for any recurring automation. |
| I-13 | The brief describes an "AI-powered" automation platform. Associates prohibits using Special Links or Program Content to develop machine-learning models without prior written approval. | [Participation Requirements §5](https://affiliate-program.amazon.com/help/operating/policies), compliance row C-22. | **Owner decision.** No ML is built on Amazon data in this audit. |
| I-14 | Norway. The Associates country selector does not list Norway. The owner is in Oslo, NO. Whether a Norway-resident account is eligible is not stated. Ship-to-Norway for these Amazon.com listings is also unverified. | Compliance rows C-18; country selector on [Associates Central](https://affiliate-program.amazon.com/help/operating/compensation). | **Blocking until confirmed** in Associates Central. |

## 5. Snapshot and regional variance

| ID | Irregularity | Evidence | Disposition |
|---|---|---|---|
| I-15 | Amazon product pages render delivery-location-specific content. The snapshots were taken with delivery locations shown as "Fairfax 22030" and "Herndon 20170". | Page text of each product (for example, "Delivering to Fairfax 22030"). | Recorded. Ratings and BSR were taken from amazon.com only. Regional storefronts are not used. |
| I-16 | Another session reports that ratings and review counts differ across Amazon storefronts for the same ASIN (for example `B09B7SB46R`: 4.5 / 16,128 on amazon.co.uk and 4.6 / 8,361 on amazon.sa, as reported by session 6602723a, I-7). This audit did not check those storefronts. | Board reports only. | Not used. Rows are amazon.com only. |

## 6. Repository and coordination

| ID | Irregularity | Evidence | Disposition |
|---|---|---|---|
| I-17 | **Session 181863ad** marks T1 to T12 "done" on the board. Its branch contains only `COORDINATION.md` and `README.md`. The `docs/`, `data/`, `index.html`, and other claimed files do not exist on that branch. | `git ls-tree -r origin/arena/181863ad-zone2` and `git log origin/main..origin/arena/181863ad-zone2` (one commit: the board itself). | Recorded on the shared board. Its "done" statuses are unsupported. |
| I-18 | **Session 6602723a** marks T2 to T8 "done". Its branch contains `.gitignore`, `COORDINATION.md`, and `README.md`. The `data/`, `site/`, and `scripts/` files it describes do not exist on that branch. | `git ls-tree -r origin/arena/6602723a-zone2`. | Recorded on the shared board. Its "done" statuses are unsupported until those files are committed. |
| I-19 | **Session 1767c9d6** claims the full repo review, site, and integration. Its branch contains only the board and `README.md`. | `git ls-tree -r origin/arena/1767c9d6-zone2`. | Recorded. |
| I-20 | Live site (PR #1 merged to `main`) shows all three products as "Official listing not resolved", with "—" in every product field. That is now out of date: all three destinations were resolved and read in this audit. | Fetched <https://kanlerxz87-cyber.github.io/Zone2/> on 2026-11-13. | Recorded. Integration session must refresh the data. |
| I-21 | Branch divergence. `main` moved from `f577167` to `cfc04b1` (PR #1 merge) after the session branches were cut. Sessions starting from `f577167` have stale `README.md`, `app.js`, `data.js`, `index.html`, and `styles.css`. | `git diff --stat origin/main origin/arena/*-zone2`. | Recorded. This session fast-forwarded its branch to `origin/main` before adding `audit/**`. |
| I-22 | No `LICENSE` file on `main`. The repo is public. | `git ls-tree origin/main`. | **Owner decision** (the license choice is the owner's). |
| I-23 | Pages is served from `main` `/` (legacy build). The Pages workflow `pages.yml` is also present. Both deploy `main`. | `gh api repos/kanlerxz87-cyber/Zone2/pages` (status `built`, source `main` `/`); workflow runs `43520718533` (success) on PR #1 merge. | Recorded. No conflict in outcome. |
| I-24 | The brief's coordination rule asks for `session-<id>/<task>` branch names. This session is pinned to `arena/5ba0cb60-zone2` by the platform and cannot rename it. | Branch note in the session. | Recorded. The platform branch is used. |
