# revalidation/ — controlled re-check of the three supplied Amazon links

Session `c6e94e8d` · branch `arena/c6e94e8d-zone2` · 2026-11-14 · task **T20** in `COORDINATION.md`.

This directory answers one question the repository had answered by inference: **are the three supplied
`link.amazon` short links arbitrary fallback pages, or do they identify products?** It adds the
control test that the earlier conclusion was missing.

## Result in one line

The short *codes* are not ASINs, but the short *links* are stable, individually tracked links that
resolve deterministically to one product each — so the "arbitrary fallback" reading does not hold.

| Evidence | What it showed |
|---|---|
| Bare `GET /dp/B08DKYBTPH` (valid ASIN, no tag, no short link) | Amazon answers with the real product page **and** appends `plpRedirect=mhFallback&lv=shuf`. The marker is normal, not a fallback signal. |
| `link.amazon/B04G1MEwY` fetched twice | Same ASIN, **same** `btn_ref=srctok-1e229870efde5acf`, same body. Not a shuffle. |
| All three links | Three distinct stable tokens (`…1e229870…`, `…534f5e79…`, `…76c3adae…`), all `channelId=704`. Per-link tracking. |
| `GET /dp/<code>` for each code | All three → Amazon "Page Not Found". The codes are **not** ASINs. |
| Resolved URLs | **No** Associates `tag` on any of the three. |

Still open and flagged: the mapping is observed behaviour, not a documented binding, and the links carry no
Associates tag. See `flagged.html` (RV-01…RV-10).

## Files

| Path | Purpose |
|---|---|
| `data/links.json` | Per-link evidence, the control test (C-1) and the repeat test (C-2). |
| `data/specs.json` | 38 product-attribute rows across the three ASINs, each with an official source or a blank+flag. |
| `data/program.json` | Programme facts re-read this session. |
| `data/flags.json` | RV-01…RV-10. |
| `scripts/build.py` | Generates the six pages from the JSON. Never hand-edit the HTML. |
| `scripts/verify.py` | Per-row sourcing, disclosure, link resolution, no-product-price, no-placeholder gate. |
| `assets.css` | Reuses the primary dashboard's design tokens. |

Generated pages: `index.html`, `links.html`, `products.html`, `method.html`, `flagged.html`, `sources.html`.

## Reproduce the gates

```bash
python3 revalidation/scripts/build.py          # regenerate pages from data
python3 revalidation/scripts/build.py --check  # committed HTML matches a fresh build
python3 revalidation/scripts/verify.py         # 6 pages · 73 rows · 165 refs · 0 failures
```

Both run in CI (`.github/workflows/pages.yml`) on every push and pull request.

## Important limit

The live checks in `data/*.json` cannot be re-run from the build sandbox: `curl` to `amazon.com`,
`affiliate-program.amazon.com`, `chefman.com` and `developers.google.com` returns HTTP `000` (exit 35).
They were made with the agent's page-fetch tool and are recorded as **dated observations with quoted
output**. CI enforces internal consistency and the sourcing rules — not the upstream facts.

Affiliate disclosure: **As an Amazon Associate I earn from qualifying purchases.**
