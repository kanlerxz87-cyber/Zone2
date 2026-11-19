# T63 verification record — 2026-11-19

Branch: `arena/cf98ff65-zone2`  
Base recorded by Arena: `4398071d49fdda73c084aa6f3dedf4f72b268076`  
Scope: resolve Pages workflow conflicts; reader-first publication navigation; retain tool routes; label topic choices as hypotheses; add a current executive summary and verification record.

## Changes verified

- Resolved both literal conflict-marker regions in `.github/workflows/pages.yml`. Preserved the submitted-link intake build, validator and negative tests, plus the decision-board build, validator and negative tests.
- Updated `tools/build_front.py` / `tools/verify_front.py` and generated pages: six reader-facing primary links; one accessible “Project & tools” disclosure menu; footer routes to the tools and dashboards; suggestion counts derived from the decision register; no unsupported implication that guide topics are based on measured search activity.
- Added the current five-submission summary at `summary.html`. It derives rows from the intake register, does not copy observed destinations into intended-product fields, leaves unconfirmed intended values blank, and identifies the legacy three-link summary text as superseded in `EXECUTIVE_SUMMARY.md` history. `tools/build_summary.py` delegates its freshness check to the canonical front-page builder.
- Adjusted the generated disclosure to distinguish the supplied Associates tag from unverified account activation and destination-link coverage. The current summary explicitly records that repository HTML does not consistently carry the supplied tag on product-destination links; it does not claim those links are valid or invalid.
- Regenerated dependent repository artifacts after adding the current summary: `sitemap.xml`, `release/index.html`, and the decision-board measurement/rendered outputs. No product or source facts were changed.
- Appended a current-state addendum to `EXECUTIVE_SUMMARY.md` covering the five-link register, measurement limits, current work and next evidence to collect.

## Checks run

All commands below completed successfully on the final working tree:

```text
python3 -m py_compile tools/build_front.py tools/verify_front.py tools/build_summary.py
python3 tools/build_front.py --check
  front pages current (9 pages)
python3 tools/build_summary.py --check
  summary.html: current executive summary
python3 tools/verify_front.py
  front gate OK — 9 pages, all checks pass
PYTHONPATH=/tmp/zone2-yaml python3 ... yaml.safe_load('.github/workflows/pages.yml')
  workflow YAML parsed; jobs: build, deploy; build steps: 53
grep -nE '^(<<<<<<<|=======|>>>>>>>)' .github/workflows/pages.yml
  no conflict markers
python3 tools/build_sitemap.py --check
  sitemap.xml is current (178 URLs)
python3 tools/build_readiness.py --check
  release/index.html is current - 12 rows, every one sourced
python3 tools/build_board.py --check
  board/: 9 pages current
python3 tools/ci_replay.py
  CI REPLAY PASSED — 49 steps
```

The full replay included all intake and decision-board contract gates and negative tests, sitemap coverage, readiness checks, link checks, structural audit, and the front-page gate. Rebuilding generated outputs initially exposed stale sitemap, readiness, and board-derived values after the summary change; those outputs were regenerated and the final complete replay passed.

## Source and data boundaries

Official guidance consulted for the summary and disclosure wording:

- Amazon Associates Operating Agreement: <https://affiliate-program.amazon.com/help/operating/agreement>
- Amazon help for ASIN / tagged link formats: <https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC>
- FTC disclosure guidance: <https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers>
- Google outbound-link qualification: <https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links>
- GitHub Pages static-hosting documentation: <https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages>
- Search Console ownership, sitemap and performance documentation:
  <https://support.google.com/webmasters/answer/9008080?hl=en>,
  <https://support.google.com/webmasters/answer/7451001?hl=en>,
  <https://support.google.com/webmasters/answer/7576553?hl=en>

The five intake entries still have blank intended ASINs and confirmation sources. Their redirect observations are dated 2026-11-17; no Amazon redirects were repeated for this integration. `shopnow047c-20` is the supplied tag, not proof of account activation or proof that every destination URL includes it. FLG-003 remains unresolved; the supplied short links are not described as invalid.

Repository inspection also found an unresolved measurement-contract mismatch: `assets/js/events.js` sends the page-view hostname field as `r`, while `docs/measurement-t40.json` specifies `referrer_host`. The measurement design labels EV-01–03 LIVE as client-side-only, while `intake/data/tracking.json` describes the five events as proposed/not instrumented. The browser queues events locally and sends nothing without a configured endpoint; conversion and search-query imports remain blocked. No endpoint, authorized Associates report, Search Console query report, or product-intent confirmation was established in this task.

## Publication / integration status

This record documents local verification only. PR #166 is open from `arena/cf98ff65-zone2` to `main`. No merge or GitHub Pages deployment is confirmed here. T65's earlier completion note calls the supplied tag “verified and active”; this task found no authorized account evidence that confirms activation or link coverage, so the current summary marks that status unverified.
