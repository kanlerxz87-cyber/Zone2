
---

## 6. Corrections made after first publication

Recorded because a method section that only lists successes is not a method section.

| Issue | How it was found | Fix |
|---|---|---|
| A price value (`69.97`) was rendered in the audit-trail snapshot table on the product pages. | Reading the deployed page, not by CI. | Price rows removed from all rendered snapshots; the verifier now also rejects any bare number matching a `price_usd` / `list_price_usd` value in the dataset, with a test proving it fires. |
| The dashboard's `index.html` shipped with no affiliate disclosure in its static HTML — it existed only in JS-rendered content. | CI's disclosure check. | Disclosure added to the HTML itself. |
