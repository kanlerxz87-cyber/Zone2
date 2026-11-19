# Counter Notes · Zone2

An independent kitchen buying-guide publication: five observed product destinations, useful
questions, clear trade-offs and an open Workroom. **AI-assisted source research, not hands-on testing.**
No invented reviewer, product experience, popularity, price, rating, conversion or revenue claim.

**As an Amazon Associate I earn from qualifying purchases.**

Publication: <https://kanlerxz87-cyber.github.io/Zone2/>
Workroom / current executive summary: <https://kanlerxz87-cyber.github.io/Zone2/workroom.html>
Exact merge/deployment evidence: **T63 in [COORDINATION.md](COORDINATION.md)** and
[the dated verification record](docs/verification-2026-11-19.md). A local preview is not production.

## What readers get

- A product-first front page with original format drawings and a labelled conceptual food image.
- Air-fryer, countertop-oven and thermometer categories; five source-linked product profiles.
- Four question-led guides: basket vs oven, capacity, cleanup/counter space and multifunction appliances.
- An honest organization byline, research method, image provenance and privacy/measurement notice.
- RSS at `feed.xml`, with the earlier `marketing/feed.xml` subscription address preserved.
- A single **Workroom** navigation group and footer directory for all retained dashboards.
- Suggestions with options/knowns/missing evidence, optional local draft save/export/clear, and a
  separate unanswered-questions register. Saving a draft never applies a change.

The new edit is in `docs/publication.json`; `tools/build_front.py` renders it reproducibly. Official
statements carry dated source links. Unknown intent and conflicting specification values remain blank
and flagged. Topic angles are editorial hypotheses, **not measured search-demand claims**.

## Attribution and measurement are different things

The owner-supplied tracking ID is **`shopnow047c-20`**. Current product buttons are direct tagged Amazon
links, visibly identified as paid links and marked `sponsored nofollow`. The exact §5 disclosure sits
under the masthead and in the footer of every deployed HTML page. The toolkit refuses synthesized
sub-tags and attribution overrides.

A syntactically tagged URL is **not** proof of enrollment, eligible sales or attribution. Intended ASIN,
intent listing URL, confirmation date and confirmation source remain blank for all five submissions.
Initial and repeat observations for the last two short links disagree; both are retained separately in
the manifest. No cause, invalidity or stable-routing guarantee is inferred. The original compliance
question remains at [Zone3 · FLG-003](https://kanlerxz87-cyber.github.io/Zone3/flagged.html#FLG-003).

**Production collection is not connected.** GitHub Pages is a static host. A real, self-hostable Python
service is implemented, with a deliberately disabled static production config:

- Public EV-01–03: page load, direct product-link click, half-visible disclosure strip.
- Local EV-04–05: explicitly authorized Associates / personal-data-reviewed Search Console CSV imports.
- Daily SQLite aggregates, no cookies/visitor IDs/analytics browser storage, GPC/DNT support, retention
  and private import provenance. Browser clicks can never assert orders.
- Original reports, populated ledgers and databases stay private and out of Git. The public
  `ledger/campaign-reports.json` is **empty by design**, not evidence of zero traffic or orders.

See **[docs/MEASUREMENT.md](docs/MEASUREMENT.md)** for actual endpoints, normalized CSV contracts,
retention, tests and the controlled-HTTPS production activation gate. No hosting account, production
collector, real traffic dataset or authorized reporting export has been provisioned or invented.

## Build and verify

Python 3.11+, Node 22.17+ for optional real-browser checks. The publication/service use Python's
standard library; QA browser dependencies are pinned separately under `tools/browser/`.

```sh
python3 tools/build_front.py
python3 tools/build_sitemap.py
python3 tools/verify_front.py
python3 tools/test_analytics.py
python3 tools/test_publication.py
python3 tools/test_price_policy.py

# Full existing source-tree workflow replay. Does not execute `uses:` or deploy.
python3 tools/ci_replay.py

# Actual Pages artifact, with shared chrome/indexing/link policy applied everywhere.
python3 tools/build_publication.py
python3 tools/validate_publication.py

# QA only; no external product requests, temporary collector DB, generated screenshots ignored.
npm ci --prefix tools/browser --ignore-scripts --no-audit --no-fund
python3 tools/run_browser_tests.py
```

`tests/test_pipeline.py` retains **15 executable guard checks** for the original platform. Other
namespaces retain their builders and negative tests. Generated output must match its builder; don't
hand-edit HTML to silence a gate. Dynamic inventory counts exclude `_site/`, `.local/` and dependencies.

For a local self-hosted preview of the final artifact:

```sh
python3 tools/analytics_server.py --db .local/preview.sqlite3 serve \
  --preview --site-root _site --port 8080
```

It binds to `0.0.0.0`; preview collection excludes ordinary browser automation. The running service
provides a same-origin enabled config only for that service. A production HTTPS reverse proxy,
logging/privacy review and retention schedule are still required. Do not describe a preview URL as a
production deployment or test attribution by fabricating shoppers or self-purchases.

## Deployment and one-site SEO

`.github/workflows/pages.yml` validates the sources, builds and checks `_site/`, then uploads **only
that artifact**. Deployment to Pages runs on `main`; pull requests build/test without deploying.
The workflow preserves the predecessor intake and decision-board checks and contains no conflict
markers. Concurrency does not cancel in-flight verification runs.

`tools/publication_policy.py` selects the 17 indexable publication pages. Operator/archive pages receive
`noindex,follow` while staying crawlable and reachable; their dated records and local anchors are
preserved. The root sitemap lists only the publication. Legacy sitemap locations point at it. This
implements indexing instructions, **not a promise of immediate deindexing, indexing or search ranking**.

Search Console verification/query exports are not available. Future topics and AI-assisted optimization
remain publication-gated proposals until authorized evidence and editorial review support them.

## Official policy references

- [Amazon Operating Agreement §5](https://affiliate-program.amazon.com/help/operating/agreement)
- [Amazon Program Policies](https://affiliate-program.amazon.com/help/operating/policies)
- [FTC disclosure guidance](https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers)
- [Google people-first content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content)
- [Google sponsored links](https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links)
- [Google noindex](https://developers.google.com/search/docs/crawling-indexing/block-indexing)
- [GitHub Pages hosting boundaries](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages)

Current scope and limits: [EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md). Earlier README/executive
narratives remain in [the pre-integration Git history](https://github.com/kanlerxz87-cyber/Zone2/tree/4398071d49fdda73c084aa6f3dedf4f72b268076),
not presented here as fresh account/API/analytics verification. Historical site namespaces remain linked
from the Workroom rather than deleted or promoted as competing homepages.
