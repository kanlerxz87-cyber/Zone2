# COORDINATION.md — Shared Task Board

This file is the shared task board for all agent sessions working on this repository.
Read it before starting work. Claim a task by writing your session ID and file scope here,
then commit and push the claim immediately. Never start a task another session has claimed.

**Last updated:** 2026-11-13 (UTC)

---

## Session registry

| Session ID | Branch | Role | Started (UTC) |
|---|---|---|---|
| `S-6602723A` | `arena/6602723a-zone2` | Full build + final integration | 2026-11-13 |

---

## Task board

Legend for **Status**: `unclaimed` · `in progress` · `done` · `needs review`
A status of `needs review` means the item is published on the *Flagged for Review* page and does not block anything.

| ID | Task | Status | Owner | File scope |
|---|---|---|---|---|
| T1 | Task board + session registry | done | S-6602723A | `COORDINATION.md` |
| T2 | Resolve the three affiliate short links to canonical ASINs | done | S-6602723A | `data/raw-verification-log.md` |
| T3 | Verify product facts against official sources | done | S-6602723A | `data/products.json`, `data/sources.json` |
| T4 | Amazon Associates compliance requirements | done | S-6602723A | `data/compliance.json` |
| T5 | Executive summary | done | S-6602723A | `docs/executive-summary.md` |
| T6 | Automated platform requirements matrix | done | S-6602723A | `data/requirements.json` |
| T7 | GitHub Pages site (landing + category subpages) | done | S-6602723A | `site/**` |
| T8 | Link + data integrity check in CI | done | S-6602723A | `scripts/verify.py`, `.github/workflows/**` |
| T9 | Final integration, PR to `main`, merge, Pages deploy | in progress | S-6602723A | `.github/workflows/**`, `README.md` |

---

## File ownership (non-overlapping scopes)

| Scope | Owner | Notes |
|---|---|---|
| `COORDINATION.md` | S-6602723A | task board |
| `data/**` | S-6602723A | machine-readable verified data + source registry |
| `docs/**` | S-6602723A | executive summary, compliance, methodology |
| `site/**` | S-6602723A | GitHub Pages output (static HTML/CSS/JS, no build step) |
| `scripts/**` | S-6602723A | verification tooling |
| `.github/workflows/**` | S-6602723A | CI + Pages deploy |
| `README.md` | S-6602723A | repo front page |

Shared outputs (table data, site index and navigation) are owned by the final integration
session. This session is the only session currently registered, so it also owns
integration. Any future session must log a request here rather than editing these paths.

---

## Change log

### 2026-11-13 — S-6602723A

- **Claimed:** T2–T9, scope `data/**`, `docs/**`, `site/**`, `scripts/**`, `.github/workflows/**`, `README.md`.
- Repo state at claim: `main` = `f577167` "Initial commit"; repository contained only a 7-byte `README.md`. No CI, no site, no data. Nothing to conflict with.
- GitHub Pages was already enabled on `main` `/` (legacy build type); the live URL is
  <https://kanlerxz87-cyber.github.io/Zone2/>. Because Pages serves from `main`, the site
  is published when this branch's pull request is merged, not before.

### Irregularities log

| # | Irregularity | Where | Disposition |
|---|---|---|---|
| I-1 | `README.md` in the initial commit contains only `# Zone2` (7 bytes) — no project description, licence, or usage documentation. | `README.md` @ `f577167` | Resolved this session: README rewritten. |
| I-2 | No `LICENSE`, no `.gitignore`, no CI, no tests in the initial commit. | repo root @ `f577167` | `.gitignore` and CI added; licence left undecided (owner decision) — flagged on the site. |
| I-3 | The three supplied `link.amazon/*` short links are opaque redirects. Their target ASINs cannot be read from the link text itself and must be resolved by following the redirect. | affiliate inputs | Resolved: all three resolve to `www.amazon.com/dp/<ASIN>`. Recorded in `data/raw-verification-log.md`. |
| I-4 | No Amazon Associates tracking tag (Store ID) is present in the supplied links, so no commission attribution can be verified. | affiliate inputs | **Flagged for review** — owner must re-generate links with their Store ID. |
| I-5 | Product prices, star ratings, review counts and stock status are volatile and are **not** published as facts on the site. Only the capture timestamp and the source page are recorded. | product data | **Flagged for review** by design. |
| I-6 | Amazon.com product pages are bot-gated and render inconsistently to automated fetches. Where the US page body did not render, values were confirmed against the same ASIN's Amazon page on a regional Amazon storefront (`.ca`, `.co.uk`) and cross-checked against the manufacturer. Differing regional values are flagged. | product data | Disclosed in `docs/methodology.md`. |
| I-7 | Star-rating and review counts differ between Amazon storefronts for the same ASIN (for example `B09B7SB46R` shows 4.5/16,128 on `.co.uk` and 4.6/8,361 on `.sa`), which means reviews are storefront-specific and must not be quoted as a single global figure. | product data | **Flagged for review**; reviews omitted from the fact table. |

---

## Verification protocol used this session

1. Every table row carries a `source` link to an official page (Amazon product page, the
   Amazon Associates Operating Agreement, or the manufacturer's own site).
2. A value that could not be confirmed from an official source is left **blank** and marked
   `unverified` in `data/products.json`, and it appears on the *Flagged for Review* page.
3. No value is inferred, interpolated, or carried over from a similar product.
4. `scripts/verify.py` re-checks every row at build time: it fails the build if a fact row
   has no source URL, if any URL is not `https`, or if any internal link in `site/` does not
   resolve to a file that exists.
5. Capture timestamps are recorded in UTC in `data/products.json`.

---

## PR and merge record

| Item | Value |
|---|---|
| Branch | `arena/6602723a-zone2` (branched from `main` @ `f577167`) |
| Pull request | _pending — recorded after creation_ |
| Merge result | _pending_ |
| Pages deploy | _pending_ |
