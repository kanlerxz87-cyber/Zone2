# COORDINATION.md — Shared Task Board

Project: **Zone2 — AI-powered Amazon Affiliate Marketing Platform**
Repo: `kanlerxz87-cyber/Zone2`
Current session: **78c94859** (branch `arena/78c94859-zone2`, branched from `f5771676f12c092c316d7b4d3051018e61db4611` of `main`)

> Coordination note: This repository is managed by a single agent session in this run.
> Per Arena session policy, all work is performed on the fixed session branch
> `arena/78c94859-zone2` (no separate `session-<id>/<task>` worktrees are created).
> This session therefore performs research, site build, and final integration itself,
> and records everything in this log. No other sessions are currently active.

## Task Board

| # | Task | Status | Session | Branch | Files touched |
|---|------|--------|---------|--------|---------------|
| 1 | Repo review + verify the three product links against official Amazon sources | done | 78c94859 | arena/78c94859-zone2 | COORDINATION.md, docs/verification-log.md |
| 2 | Research official Amazon Associates program rules (commission, session, disclosure, agent/AI terms) | done | 78c94859 | arena/78c94859-zone2 | COORDINATION.md, docs/verification-log.md |
| 3 | Build GitHub Pages site: landing page + category subpages (dashboard UI, tables) | done | 78c94859 | arena/78c94859-zone2 | index.html, products.html, analysis.html, content.html, compliance.html, tracking.html, flagged.html, assets/ |
| 4 | Collect/verify all table data; every row carries an official source link; unverifiable values left blank + flagged | done | 78c94859 | arena/78c94859-zone2 | assets/js/data.js, docs/verification-log.md |
| 5 | Final integration: re-verify combined data line by line, confirm site builds with no broken internal links | done | 78c94859 | arena/78c94859-zone2 | see "Integration & verification" below |
| 6 | Publish to GitHub Pages, create PR to main, merge, record PR link and result | done | 78c94859 | arena/78c94859-zone2 | see "Integration & verification" below |

## Sources used (all official / verified)

| Source | URL | Used for |
|---|---|---|
| Amazon Associates Central (program home) | https://affiliate-program.amazon.com/ | Program description; "earn up to 10% in associate commissions from qualifying purchases and programs" |
| Amazon Associates Program Policies (updated April 14, 2026) | https://affiliate-program.amazon.com/help/operating/policies | Commission Income Statement (session, qualifying purchases, payment terms), Participation Requirements, Agent Terms, IP License |
| Amazon Associates Operating Agreement (updated October 15, 2025) | https://affiliate-program.amazon.com/help/operating/agreement | Mandatory disclosure language ("As an Amazon Associate I earn from qualifying purchases.") |
| Amazon product page — B0CDY277D3 | https://www.amazon.com/dp/B0CDY277D3 | Product 1 title/brand/category |
| Amazon product page — B09B7SB46R | https://www.amazon.com/dp/B09B7SB46R | Product 2 title/brand/category |
| Amazon product page — B08DKYBTPH | https://www.amazon.com/dp/B08DKYBTPH | Product 3 title/brand/category |

## Irregularities flagged for review

1. **Link-code / ASIN mismatch (all three products).** The provided short links
   `https://link.amazon/B04G1MEwY`, `https://link.amazon/B02NbDxp3`, `https://link.amazon/B00hJ57DV`
   each redirect to a live Amazon product page, but the destination ASIN differs from the code in the
   link: B04G1MEwY → B0CDY277D3, B02NbDxp3 → B09B7SB46R, B00hJ57DV → B08DKYBTPH. Direct fetches of
   `amazon.com/dp/B04G1MEwY` etc. return "Page Not Found" on Amazon. The codes look like ASINs but are
   not valid `/dp/` ASINs; they behave as opaque short-link tokens. Flagged — see
   [Flagged for Review](https://kanlerxz87-cyber.github.io/Zone2/flagged.html) page.
2. **All three products are in the same category (Home & Kitchen air fryers / air fryer ovens).**
   Confirmed from the three Amazon titles. Not an error; noted for niche-analysis (single-category
   portfolio).
3. **Commission rate card requires sign-in.** The official per-category rate schedule
   (https://affiliate-program.amazon.com/help/operating/schedule) redirects to Amazon sign-in, so the
   category-specific rate for Home & Kitchen could not be publicly verified. Only the official public
   statement "up to 10%" is recorded; the category rate is left blank and flagged as unverified.
4. **Price / rating / review-count not verifiable programmatically.** Amazon does not expose price,
   star ratings or review counts to automated fetches (bot protection). Per the no-hallucination rule,
   these cells are left blank and flagged as unverified. Amazon's policies also restrict displaying
   prices/ratings unless served via the link or via Creators API / PA API.

## Integration & verification

- Combined data re-verified line by line against the official sources listed above (2026-11-13).
- Site is a static site (HTML/CSS/JS) served from the repository root; no build step required.
- Internal link check: all internal navigation links point to existing files (verified locally).
- PR: **#1** — `https://github.com/kanlerxz87-cyber/Zone2/pull/1`
- Merge: merged into `main` (squash merge), commit recorded in git history.
- GitHub Pages: source branch `main`, path `/`; site live at
  https://kanlerxz87-cyber.github.io/Zone2/ (deploy status: built).
