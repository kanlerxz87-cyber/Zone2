# Zone2 — Amazon affiliate research hub

A source-linked research site for three Amazon affiliate products, plus a documented
position on which parts of an "automated affiliate platform" Amazon's own policies
actually permit.

**Live site:** <https://kanlerxz87-cyber.github.io/Zone2/>

> As an Amazon Associate I earn from qualifying purchases.

---

## What this repository is

It is a **verifiable dataset plus a static site generated from it** — not a scraper and not
an AI content farm.

Every published product fact is traceable to an official page: the Amazon listing for that
exact ASIN, or the manufacturer's own product page for the model number printed on it.
Values that could not be confirmed are left blank and listed on the *Flagged for Review* page.

```
data/          the verified dataset (the source of truth)
  products.json            per-product specs; every row carries a status + source URL
  compliance.json          Amazon's rules, quoted with section references
  requirements.json        every requirement in the brief, and its honest disposition
  sources.json             source registry with a 3-tier trust model
  raw-verification-log.md  raw capture log: what each page actually said
docs/
  executive-summary.md     the short version
scripts/
  build.py                 generates site/ from data/
  verify.py                the guard: fails on unsourced rows, broken links, printed prices
site/          generated output, served by GitHub Pages
COORDINATION.md  shared task board, irregularities log, PR record
```

## The three products

| Supplied link | ASIN | Product | Brand |
|---|---|---|---|
| `link.amazon/B04G1MEwY` | B0CDY277D3 | 6 Qt Dual Basket Air Fryer, dual windows, Sync Finish | Chefman |
| `link.amazon/B02NbDxp3` | B09B7SB46R | 26QT French Door Multi-Function Air Fryer Toaster Oven | Emeril Lagasse |
| `link.amazon/B00hJ57DV` | B08DKYBTPH | 8 Qt TurboFry Touch air fryer, stainless steel | Chefman |

## Build and check locally

Requires Python 3.9+. No third-party dependencies.

```bash
python3 scripts/build.py     # writes site/
python3 scripts/verify.py    # exits non-zero on any broken rule
python3 -m http.server 8080 --directory site   # preview at http://localhost:8080
```

CI (`.github/workflows/pages.yml`) runs the same two commands on every push and pull
request, and deploys to GitHub Pages only from `main` after verification passes.

## What the verification enforces

`scripts/verify.py` fails the build when:

- a fact row claimed as `verified` or `conflict` has no source URL;
- a source URL is not `https` or is not an official host;
- a row marked `unverified` still carries a published value;
- an internal link in the generated site points at a file that does not exist;
- a page is missing the affiliate disclosure or the trademark attribution;
- a page prints a currency amount — this project does not publish prices.

## What is deliberately *not* published

| Data | Why |
|---|---|
| Price | Amazon permits price display only where Amazon serves it or it comes from the official API, and requires a timestamp plus a disclaimer. |
| Star rating / review count | Storefront-specific for the same ASIN; a single figure would mislead. |
| Stock status | Changes by the minute. |
| Commission rate | The official rate card requires an Associates login. |
| Conversion rate, sales volume, "trending" score | Not published by Amazon; no official source exists. |

## Known issues

The one thing blocking commercial value: **the three supplied links carry no Amazon
Associates tracking tag**, so clicks cannot be attributed. See *Flagged for Review* on the
site, or `COORDINATION.md` item O-1.

## Licence

Not yet chosen — see `COORDINATION.md` item O-3.
