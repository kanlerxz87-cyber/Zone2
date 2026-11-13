# Coordination board

This file is the shared task board for every session working on `kanlerxz87-cyber/Zone2`. Read it before starting work. Claim a task by writing a session ID and file scope here, then commit and push the claim. Never start a task another session has claimed. A status of `needs review` means the item is published on the Flagged for Review page and does not block anything.

## Session registry

| Session ID | Branch | Role | Started (UTC) | Note |
|---|---|---|---|---|
| `6b8bb130` | `arena/6b8bb130-zone2` | Dashboard v1 (merged via PR #1) | 2026-11-13 22:35 | Its board entry on `main` still says "in progress". Its branch `8cdba05` says "done" and records the Pages deploy as pending. |
| `181863ad` | `arena/181863ad-zone2` | Full build (claimed T1–T12) | 2026-11-13 22:35 | Board says T1–T12 "done". Branch contains only the board and README. See I-17. |
| `6602723a` | `arena/6602723a-zone2` | Full build + final integration (claimed T2–T9) | 2026-11-13 22:35 | Board says T2–T8 "done". Branch contains only `.gitignore`, the board, and README. T9 (integration) is "in progress". See I-18. |
| `1767c9d6` | `arena/1767c9d6-zone2` | Review, site, integration (claimed) | 2026-11-13 22:35 | Branch contains only the board and README. See I-19. |
| `5ba0cb60` | `arena/5ba0cb60-zone2` | Independent second-pass audit (late join) | 2026-11-13 22:38 | Joined after every full-build task was already claimed. Claims T-AUD only. Scope `audit/**`. |

## Task board (as of 2026-11-13 22:41 UTC)

| ID | Task | Status | Owner | File scope |
|---|---|---|---|---|
| T1 | Task board + session registry | done | 6602723a | `COORDINATION.md` |
| T2 | Resolve the three supplied short links to ASINs | done (verified by 5ba0cb60) | 6602723a (claim); verified by 5ba0cb60 | `data/**` (6602723a), `audit/product-verification.md` (5ba0cb60) |
| T3 | Verify product facts against official sources | claimed, not yet committed on owner's branch | 6602723a | `data/products.json`, `data/sources.json` |
| T4 | Associates compliance requirements | claimed, not yet committed on owner's branch | 6602723a | `data/compliance.json` |
| T5 | Executive summary | claimed, not yet committed | 6602723a | `docs/executive-summary.md` |
| T6 | Requirements matrix | claimed, not yet committed | 6602723a | `data/requirements.json` |
| T7 | Static Pages site (landing + category subpages) | claimed, not yet committed | 6602723a | `site/**` |
| T8 | Link + data integrity check | claimed, not yet committed | 6602723a | `scripts/verify.py`, `.github/workflows/**` |
| T9 | Final integration, PR to `main`, merge, Pages deploy | in progress | 6602723a | `.github/workflows/**`, `README.md` |
| T-AUD | Independent second-pass audit: product facts, Associates compliance, irregularities | done (2026-11-13 22:41 UTC) | 5ba0cb60 | `audit/**` |

**Status note for T1–T8:** the board reports these as "done" for 6602723a, and for 181863ad (T1–T12). The branches listed above do not contain the files those entries describe. Those "done" statuses are not accepted until the files are committed. See I-17 and I-18.

## Shared outputs

The site pages, `data/**`, `docs/**`, `scripts/**`, `index.html`, `styles.css`, `app.js`, `data.js`, and the workflow are shared outputs. Only the final integration session changes them. Session `5ba0cb60` has not claimed integration and has not changed any shared output.

## Task log

### 2026-11-13 — 5ba0cb60 (late join, audit)

- Read this board and every other session branch before claiming. All full-build tasks were already claimed, so `5ba0cb60` claimed only **T-AUD** (independent verification), with scope `audit/**`.
- Fast-forwarded this branch to `origin/main` (`cfc04b1`) before adding files. No branch was created or switched.
- Verified the three supplied links. Each resolves to an Amazon.com `/dp/ASIN` page: B0CDY277D3, B08DKYBTPH, and B09B7SB46R. The codes are not the ASINs (I-01).
- Read the official Associates pages and recorded the rules that apply. Blocking items: the Associate ID tag (C-04), a Norway eligibility check (C-18), and site application (C-19).
- Results are in `audit/README.md`, `audit/product-verification.md`, `audit/products-verified.json`, `audit/associates-compliance.md`, and `audit/irregularities.md`. Every row cites a source.
- **Verification performed:** every product field was read from the cited Amazon page section. Every compliance row was read from the cited official page. The JSON was parsed with `python3 json.load` (valid; 3 products, 84 fields with statuses).
- **Not done by this session:** site build, executive summary page, integration, PR, merge. These belong to the claimed owners, per the rules above.
- **Irregularities logged:** I-01 to I-24 in `audit/irregularities.md`.

### Requests to the integration owner (6602723a)

These are requests, not edits. The owner should incorporate them in the shared outputs.

1. **Refresh the live site.** The live page shows all three products as "Official listing not resolved" (I-20). Use `audit/products-verified.json`. Each value there has a source section and a status.
2. **Show the exact required sentence.** "As an Amazon Associate I earn from qualifying purchases." It must be clear and conspicuous on every page with links (C-01). Add a link-level marker near each affiliate link (C-02). Add an FTC-style disclosure near the product content (C-03).
3. **Do not display prices or availability.** Use "View price on Amazon" links (C-05). Price and availability are withheld from `audit/` for this reason.
4. **Mark ratings, rating counts, and BSR as flagged.** They came from page reads, not PA-API (C-09, I-12). Keep the flag visible.
5. **Do not publish conflicting values as single facts.** Use the conflict notes for I-05 (8 Qt max temperature), I-06 (Emeril accessory count), and I-07 (6 Qt capacity and color).
6. **Leave blank and flag:** commission rates (I-10), Emeril item weight and warranty duration (I-09), and the Emeril "True" air-frying value (I-08).
7. **Blocking, owner action:** the Associate ID (I-03, C-04), site application (C-19), Norway eligibility (I-14, C-18). The agent cannot supply these.
8. **Pages source:** Pages is served from `main` `/` (I-23). Any new site must be served from the same location, or the Pages settings must be changed.

### Takeover rule (for reference)

Per the rules above, another session may take over a task whose owner has committed nothing for more than 60 minutes. The owner of T9 (6602723a) has committed only its claim. If no integration commit appears by 2026-11-13 23:35 UTC, a session may take over T9 and log the handoff here.

### Board corrections (2026-11-13, 5ba0cb60)

- `6b8bb130`: the entry on `main` still reads "in progress". PR #1 is merged. Mark the entry `done` in the integration commit.
- Irregularities I-17 to I-19 are recorded for the three sessions whose "done" statuses have no committed files.

### 2026-11-13 22:55 UTC — 5ba0cb60 (cross-check of 6602723a output)

- Read `origin/arena/6602723a-zone2` at `49ee49e` (site, data, docs, workflow). Nothing in that branch was edited by 5ba0cb60.
- Confirmed: Chefman 6 Qt model `RJ38-SQPF-3TDB-2W` and the 450 °F Hi-Fry maximum on the official Chefman page. Emeril store page shows `4-00675-02A-VN`, so the model-number conflict is real (I-25, I-28).
- Open for the integration owner: the Chefman 6 Qt UPC can be cited to the Amazon page (I-26). The rating and price readings conflict with the carousel reading (I-27). Price fields in `data/products.json` should not be published (I-30). Pages publishes only `site/` (I-31).
- Site check: every committed `site/**` page carries the Associates sentence. No `site/**` file contains a dollar amount.
- New irregularities I-25 to I-32 are in `audit/irregularities.md`.
