# T63 final-integration verification

**Session:** `5d423a61` · **Branch:** `arena/5d423a61-zone2` · **Date:** 2026-11-19 UTC
**Scope:** buyer-first root publication, grouped Project navigation, front-page disclosure and link attributes, current five-link executive summaries, generated root dataset, and the integration gates listed below.

## Outcome

- The root landing page is generated as the Counter Notes buyer publication; the grouped Project desk and footer retain reader, decision, evidence and operator routes.
- `summary.html`, `EXECUTIVE_SUMMARY.md`, and the linked `pages/executive-summary.html` now describe all five supplied-link records. The generated summaries join `ledger/products.json` to `docs/product-intent.json`, keep observed destinations separate from intended products, and cite the supplied retailer links plus the relevant Amazon and manufacturer pages. Intended-product fields remain blank; site-generated Special Links for the first three use `shopnow047c-20` and remain unvalidated in the Associates workflow. No categorical conclusion is made about the supplied short links.
- Citation links are emitted as unmonetized evidence links; purchase CTAs retain `rel="sponsored nofollow"`, the selected Associates ID, and link-level disclosures. The front gate distinguishes those two link classes.
- The root JavaScript dataset was regenerated from `ledger/products.json` and the current flags register. Generated decision-board measurements were refreshed from the tree; no board input data was edited.
- **Full replay:** `python tools/ci_replay.py` → **49/49 steps passed**. `python tools/build_board.py` also completed and its embedded replay passed; `python tools/build_board.py --check` → 9 pages current.

## Evidence reviewed and source status

No external Amazon or manufacturer pages were fetched in this session. The URLs below are the official sources already registered in `ledger/sources.json`; their recorded dates and prior verification methods remain the provenance for published values. This integration did not renew those source dates or represent them as freshly checked.

| Register/source | Use in this integration | This session's verification |
|---|---|---|
| [`docs/product-intent.json`](product-intent.json), [`ledger/products.json`](../ledger/products.json) | Five supplied codes; observed destinations and dates; intended ASINs; published Special Link/tag and validation fields | Read local data, kept observation and intent separate; no source values changed |
| Supplied retailer short links [1](https://link.amazon/B04G1MEwY), [2](https://link.amazon/B02NbDxp3), [3](https://link.amazon/B00hJ57DV), [4](https://link.amazon/B0c8moW59), [5](https://link.amazon/B0f3GKalj) | Evidence links for the five recorded redirect observations; the summary labels them as citations, not shopping calls to action | Observation dates remain 2026-11-17 from the intent register; none of these links was fetched in this session |
| [Amazon listing S19](https://www.amazon.com/dp/B0CDY277D3), [S20](https://www.amazon.com/dp/B09B7SB46R), [S21](https://www.amazon.com/dp/B08DKYBTPH), [S61](https://www.amazon.com/dp/B0DHZTCNR5), [S62](https://www.amazon.com/dp/B0DZFD6R9Z) | Official listing references for the five recorded destinations | URLs/IDs matched the local source and intent records; pages not fetched live |
| [Amazon Special Link help S24](https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC), [Operating Agreement S01](https://affiliate-program.amazon.com/help/operating/agreement), [Program Policies S02](https://affiliate-program.amazon.com/help/operating/policies) | Summary guidance for Special Links, account workflow and reporting | Existing citations retained; pages not fetched live |
| [Amazon commission statement S04](https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ) | Date-bounded rate-schedule note in the executive summary | Local record says read 2026-11-13 and rechecked in verification record V-73 on 2026-11-14; not fetched live |
| [Manufacturer S25](https://chefman.com/products/turbofry-touch-dual-window-air-fryer), [S26](https://chefman.com/products/turbofry-touch-air-fryer-1), and [S27](https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360) | Official manufacturer sources cited for the first three product fact sets | Source IDs and URLs included in the generated summary rows and Markdown summary; pages not fetched live |

The dated redirect observations in `docs/product-intent.json` are recorded as 2026-11-17. The summary presents those as repository observations, not as a redirect test repeated on 2026-11-19.

## Checks run

| Check | Result |
|---|---|
| `python tools/build_front.py --check` | 8 generated pages current |
| `python tools/verify_front.py` | Front gate passed; citations untagged/un-sponsored, product links sponsored/tagged |
| Custom Amazon-link audit of the 8 front pages | 6 tagged purchase CTAs and 15 untagged citations checked; 0 citation/product-link attribute violations |
| Summary citation audit (`summary.html`, `pages/executive-summary.html`) | All Amazon and supplied-short-link evidence links are untagged and unsponsored; both summaries cite all 5 supplied URLs and the relevant manufacturer sources |
| `python tools/build_summary.py --check` | Summary HTML current against generator inputs |
| `python tools/build_root_data.py --check`; `node --check assets/js/data.js`; `node --check assets/js/app.js` | Dataset current; JavaScript syntax valid |
| `python tools/build_root_views.py --check`; `python tools/build_site.py --check`; `python tools/build_sitemap.py --check` | Root views current; 39 site pages current; sitemap current at 178 URLs |
| `python tools/build_marketing.py --check`; `python marketing/scripts/verify_marketing.py` | 23 outputs current; 20 pages and 48 spec rows pass, 0 failures |
| `python tools/build_board.py --check`; `python tools/validate_board.py`; `python tools/test_board.py` | 9 pages current; board gate clean; 19 injected defects fired as expected |
| `python tools/ci_replay.py` | **49/49 steps passed**, including link resolution, disclosure/price checks, summary drift, structural/SEO/head audits, decision/intake/board gates, and front gate |
| Pages workflow YAML parse (PyYAML 6.0.3) | 2 jobs / 54 steps parsed; both T60 intake and T58 decision-board gates are present; no conflict markers |
| `git diff --check` | Clean at final local check |

## Irregularities and unresolved items

1. **Source freshness:** no official product, manufacturer or program page was fetched live for this editorial/integration pass. Do not read local generator checks as factual re-verification.
2. **Intent and Associates validation:** 0 of 5 intended-product mappings are confirmed. The three site-generated tagged Special Link records have null Associates-workflow validation. The two thermometer observations have no purchase link.
3. **Supplied short-link status:** exact compliance remains unresolved under F-03 / FLG-003. No claim that the supplied short links are invalid is made.
4. **Cross-scope copy request CR-T63-1:** `docs/board-9251f262.json` and `board/data/requirements.json` retain categorical wording that the three supplied links cannot earn/attribute because they carry no tag, and that no tag was supplied. The source data belongs to the earlier suggestion/requirements surface and was not edited. The request is logged in `COORDINATION.md`; the executive summary uses the corrected, evidence-bounded status.
5. **Board measurement date:** `tools/build_board.py` refreshed counts and generated outputs, but `board/data/measured.json` still writes the hard-coded `measured_utc` value `2026-11-17`. Counts are current to the tree used for this build; that timestamp is not a fresh date for this run and is logged for the board owner.
6. **Head metadata companion report:** `tools/build_head_meta.py --audit` reported 0 contract problems; it separately lists 44 companion pages without a self-referencing canonical as report-only under the existing MQ-08 / DS-12 decision.

**Not verified here:** live GitHub Pages deployment, Amazon Associates account enrollment, per-link tracking attribution, product intent, current prices/availability, API access, and first-party orders/earnings. Record PR and deployment results after integration; do not infer them from the local gates.
