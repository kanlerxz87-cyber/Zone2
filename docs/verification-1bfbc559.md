# Verification record — session `arena/1bfbc559-zone2`, T62 (2026-11-17)

The five-product brief. Everything below was read live on 2026-11-17 unless the row says
`carried`. Repository facts were measured from the working tree at `e58dac0`.

Method note: the sandbox shell has no general outbound network access (`curl` fails with
`SSL_ERROR_SYSCALL`), so every live fetch used the session's page-fetch tool and every
repository fact was measured from the tree or read with `gh`.

## 1. The five supplied links

| Id | Supplied | Token | Len | Resolved to | Tag? | Source |
|---|---|---|---|---|---|---|
| PI-01 | `link.amazon/B04G1MEwY` | B04G1MEwY | 9 | `amazon.com/dp/B0CDY277D3` — CHEFMAN 6 Qt dual basket air fryer | no | BD-06, BD-09 |
| PI-02 | `link.amazon/B02NbDxp3` | B02NbDxp3 | 9 | `amazon.com/dp/B09B7SB46R` — Emeril Lagasse 26QT French door air fryer oven | no | BD-07, BD-10 |
| PI-03 | `link.amazon/B00hJ57DV` | B00hJ57DV | 9 | `amazon.com/dp/B08DKYBTPH` — Chefman 8 Qt TurboFry air fryer | no | BD-08, BD-11 |
| PI-04 | `link.amazon/B0c8moW59` | B0c8moW59 | 9 | `amazon.com/dp/B0DHZTCNR5` — ThermoMaven 1 Sec instant-read meat thermometer | no | BD-01, BD-03 |
| PI-05 | `link.amazon/B0f3GKalj` | B0f3GKalj | 9 | `amazon.com/dp/B0DZFD6R9Z` — CHEF iQ Sense wireless meat thermometer | no | BD-02, BD-04 |

PI-01…PI-03 reproduce the destinations recorded on 2026-11-13, 14, 15 and 16 — a fifth
independent date, with the per-link `btn_ref` token new again (F-21). PI-04 and PI-05 were
never recorded anywhere in this repository before today.

Both new destinations were also fetched **directly**, at `/dp/<ASIN>` without the short
link, and both served the same title — so neither destination is an artefact of the redirect.

## 2. The control

`https://link.amazon/B0DHZTCNR5` — a valid, live 10-character ASIN, the very one PI-04
resolves to — was placed in the short-link token slot. It resolved to `amzlinks.in/B0DHZTCNR5`
and returned **404: File Not Found — "You've clicked on an invalid URL."**

This reproduces, for the new pair, the control that decides how to read the supplied tokens:
the service does not accept ASINs in that slot, so a 9-character supplied token is a
service-issued identifier rather than a truncated ASIN. Source BD-05.

## 3. Official sources read live

| Id | Page | What it establishes |
|---|---|---|
| BD-12 | [How do I build a simple text link to a specific item on Amazon?](https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC) | "ASIN is the 10-digit code that Amazon uses to denote specific products"; the qualifying link form `http://www.amazon.com/dp/ASIN/ref=nosim?tag=YOURASSOCIATEID`; "YOURASSOCIATEID is the unique ID that is used to identify your Associates account, automatically generated when you apply" |
| BD-13 | [Application Review Process](https://affiliate-program.amazon.com/help/node/topic/G8TW5AE9XL2VX9VM) | "we require at least three within the first 180 days"; "personal orders do not qualify"; "a good rule of thumb is at least 10 posts"; "generally within the last 60 days"; "Associates special links are the identifiers (e.g. abcd-20) embedded in Amazon product links. These tags must be embedded in your Amazon product links on the site(s) declared in your application" |
| BD-14 | [Why do I have to identify myself as an Associate?](https://affiliate-program.amazon.com/help/node/topic/GHQNZAU6669EZS98) | the two obligations; the exact required sentence "As an Amazon Associate I earn from qualifying purchases."; clear and conspicuous, placed near the link |
| BD-15 | [Qualify your outbound links to Google](https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links) | "Mark links that are advertisements or paid placements (commonly called paid links) with the sponsored value." Page states last update 2025-12-10 |
| BD-16 | [Spam policies for Google web search](https://developers.google.com/search/docs/essentials/spam-policies) | human-review factors including "Its stated or implied authorship"; the worked example "Likely to take action: unauthored affiliate article not integrated in publication" |

Carried, **not** re-fetched by this session, and labelled as carried on the sources page:
BD-17 Operating Agreement, BD-18 Program Policies, BD-19 FTC Disclosures 101, BD-20 Google
helpful-content guidance.

## 4. Measured from the tree (excluding `board/`, which measures nothing about itself)

```
pages                162      disclosed       162      tagged         0
og_image             0        jsonld          36       canonical_missing  46
unique_titles        157      dup_titles      5        no_desc        7      dup_desc 2
amazon_links         2238     sponsored_links 132
reader_pages         42       sponsored_reader 122     unsponsored_reader 306
guide_pages          29       guides_unlinked 4
sc_pages             0        endpoint_pages  0        capture_pages  0
chooser_pages        0        counter_pages   11       viewport_pages 162
```

Every one of these is printed on `board/` by substitution from a measurement taken in the
same run, and `tools/validate_board.py` re-measures and fails on any disagreement.

## 5. Gate runs

- `tools/ci_replay.py` — replays all **46** workflow steps in order: **46 of 46 pass**.
- `tools/build_board.py --check` — 9 pages current.
- `tools/validate_board.py` — all checks pass.
- `tools/test_board.py` — **19** injected defects, each fires; unmutated board clean.
- `tools/audit_site.py` — 171 pages: fragments, spec sources, prose counts, namespaces,
  disclosure, debris, board — all PASS.

## 6. What could not be verified

1. Whether `shopnow047c-20` is an issued, active Associates ID. It matches the published
   shape (`abcd-20`, BD-13) but no public page can confirm it: Amazon states IDs are
   generated on application. Logged as BQ2-01.
2. Whether the supplied short links are valid Special Links. The brief records this as
   unresolved in FLG-003 and instructs that no claim be made either way. Reproduced as
   BQ2-04 rather than as a finding.
3. The fifteen decision records the brief cites on another site. The page is live and hosts
   anchors in the `D-nn` form; individual ids were not checked, and the Zone3 item the brief
   cites was not fetched. Logged as FL-11.
4. The four carried sources (BD-17…BD-20). Not re-fetched; labelled.

## 7. Irregularities found

Thirteen, published at `board/flagged.html`. Four are high severity:

- **FL-01** — two of the five supplied products appear in no file in this repository.
- **FL-02** — no Associates tag anywhere; none of the five supplied links carries one.
- **FL-03** — the five products span two category nodes; the published site covers one.
- **FL-13** — the rule that is supposed to stop a page printing a product price never fires.
  Four copies (`.github/workflows/pages.yml:155`, `tools/validate_data.py:550`,
  `tools/build_readiness.py:623`, `tools/validate_audit.py:272`) strip tags before splitting
  on those tags, so all 162 pages collapse to a single unit and the program-economics
  exemption swallows every price. The corrected order is a one-line change in each.

## 8. Scope actually touched

New: `board/**`, `tools/build_board.py`, `tools/validate_board.py`, `tools/test_board.py`,
this file. Additive: `.github/workflows/pages.yml` (four steps, one of them a link-check
line — no existing step altered), `README.md`, `EXECUTIVE_SUMMARY.md`, one nav entry and one
footer entry in `tools/build_front.py`.

Forced, and recorded as such:

- `brief/data/summary.json` — five typed counts. `tools/validate_brief.py` derives the
  expected values from the tree, and adding `board/` moved them from 150 to 159 pages and
  from 16 to 17 surfaces, so the design-brief gate failed until they were updated. Data only;
  no change to `tools/build_brief.py`. Filed as CR-3 asking the owner to derive them.
- `sitemap.xml`, `release/index.html` — regenerated by their own builders (derived only).

Not touched: `ledger/**`, any other session's namespace.
