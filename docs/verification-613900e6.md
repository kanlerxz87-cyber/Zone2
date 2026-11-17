# Verification record — session `arena/613900e6-zone2` (T60, renumbered from T58), 2026-11-17

The five submitted affiliate links, verified line by line against official pages fetched live
on 2026-11-17. Every row below names the URL that was read and the value it supports. Where a
value could not be confirmed from an official source it is left blank and flagged, never
inferred.

## What prompted this

The 2026-11-17 brief names **five** `link.amazon` links and a tracking id (`shopnow047c-20`).
This repository's registers were built around **three**. Before this session:

```
$ grep -rn "B0c8moW59\|B0f3GKalj\|shopnow047c" .   # every tracked file
(no results)
```

Two of the five promoted products were absent from the site entirely, and so was the tracking
id. That is the gap this record documents closing.

## 1. The five links, resolved

Each URL was requested live and the resolved URL and page title read from the response.

| Id | Submitted | Token chars | Resolves to | Observed page title (as served) | Category path | Source |
|---|---|---|---|---|---|---|
| SUB-01 | `https://link.amazon/B04G1MEwY` | 9 | `B0CDY277D3` | CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows, Sync Finish, Hi-Fry, Auto Shutoff, 2 Independent 3Qt Nonstick Dishwasher Safe Frying Baskets, Digital Double Air Fryer - Black | …› Small Appliances › Fryers › **Air Fryers** | [IN-09](https://www.amazon.com/dp/B0CDY277D3) |
| SUB-02 | `https://link.amazon/B02NbDxp3` | 9 | `B09B7SB46R` | Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven \| Countertop Convection Cooker, 24 One-Touch Preset Options, Extra Large Interior, Six Cooking Accessories Included | …› Small Appliances › Fryers › **Air Fryers** | [IN-10](https://www.amazon.com/dp/B09B7SB46R) |
| SUB-03 | `https://link.amazon/B00hJ57DV` | 9 | `B08DKYBTPH` | Chefman Air Fryer 8 Qt \| TurboFry® 4-in-1 with 450°F Hi-Fry Option for Crispier Results \| Bake, Dehydrate, Frozen \| XL Nonstick Dishwasher-Safe Basket \| Stainless Steel | …› Small Appliances › Fryers › **Air Fryers** | [IN-11](https://www.amazon.com/dp/B08DKYBTPH) |
| SUB-04 | `https://link.amazon/B0c8moW59` | 9 | `B0DHZTCNR5` | ThermoMaven 1 Sec Professional Digital Meat Thermometer, ±0.5℉ Accuracy \| NIST&NSF Certified Food Thermometer, Auto-Rotate Bright LED Screen, Highly Waterproof for Grill BBQ Camping, Black | …› Kitchen Utensils & Gadgets › Thermometers & Timers › **Meat** | [IN-12](https://www.amazon.com/dp/B0DHZTCNR5) |
| SUB-05 | `https://link.amazon/B0f3GKalj` | 9 | `B0DZFD6R9Z` | CHEF iQ Sense \| Smart Wireless Meat Thermometer \| 3 Ultra-Thin Probes \| WiFi Unlimited Range \| 1000°F Heat Safe \| 5 Sensors \| BBQ, Grill, Oven, Smoker, Air Fryer \| Gen3 | …› Kitchen Utensils & Gadgets › Thermometers & Timers › **Meat** | [IN-13](https://www.amazon.com/dp/B0DZFD6R9Z) |

**Finding (IF-01).** Three links land in Air Fryers; two land in Meat Thermometers. Every page
on the site that describes the promoted range as air fryers is now wrong about two fifths of it.

## 2. The control: does the service honour the code at all?

An unissued 9-character code of the same shape as the submitted codes was requested.

| Request | Result |
|---|---|
| `https://link.amazon/B0c8moW5Z` | **404 File Not Found**, served at `https://amzlinks.in/B0c8moW5Z`, body: “Uh oh, it looks like something went wrong.” / “You've clicked on an invalid URL.” |

Source: [IN-14](https://link.amazon/B0c8moW5Z).

**Reads as:** the five supplied codes resolve because they are issued lookups, not because the
service ignores its input and falls back to something arbitrary. **Does not read as:** the
destination is the product the owner intended.

**Side effect (IF-05).** The error page is served from `amzlinks.in`, not an amazon.com domain.
Third-party write-ups describe that host as connected to Amazon's link tools, but a third-party
write-up is not an official source, so the question is left open rather than answered.

## 3. Does `plpRedirect=mhFallback` mean the link fell back?

No. A bare request to a known-good ASIN returns the same marker:

`https://www.amazon.com/dp/B0CDY277D3` → `…?lv=shuf&channelId=500&plpRedirect=mhFallback`

This reproduces the control already recorded in the repository's README. The marker is not
evidence of a fallback. Source: [IN-09](https://www.amazon.com/dp/B0CDY277D3).

## 4. Do the resolved URLs carry an Associates tag?

No. Every resolved URL carries some subset of `lv`, `btn_type`, `gaOptInStatus`, `btn_ref`,
`channelId`, `plpRedirect`, `th`, `sbo`, `sp_csd`, `content-id`, `_encoding`, `language`, `ie`.
**None carries `tag=`.**

Amazon's own help page publishes the required shape:

> `http://www.amazon.com/dp/ASIN/ref=nosim?tag=YOURASSOCIATEID`
> Source: [IN-03](https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC), read 2026-11-17

**Reads as:** the `tag` parameter is absent from all five observed destinations.
**Does not read as:** the links are invalid. A tag may be attached during the redirect in a way
this measurement cannot see. The brief's own FLG-003 records the compliance status of the
supplied short links as unresolved, and this project does not claim either way. Flagged as IF-02.

## 5. Official sources re-read live on 2026-11-17

| Id | Page | Page states updated | Quote relied on |
|---|---|---|---|
| IN-01 | [Operating Agreement](https://affiliate-program.amazon.com/help/operating/agreement) | 2025-10-15 | “The links must properly use the special “tagged” link formats we provide and comply with this Agreement (“Special Links”).” |
| IN-01 | as above | | “You must clearly and prominently state the following…: “As an Amazon Associate I earn from qualifying purchases.”” |
| IN-01 | as above | | “We do not make any representation, warranty, or covenant regarding the amount of traffic or commission income you can expect…” |
| IN-02 | [Program Policies](https://affiliate-program.amazon.com/help/operating/policies) | 2026-04-14 | “These Associates Program policies (“Program Policies”) are incorporated by reference in the Associates Program Operating Agreement” |
| IN-03 | [Simple text link / ASIN definition](https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC) | — | “ASIN: ASIN is the 10-digit code that Amazon uses to denote specific products. It is short for “Amazon.com Standard Item Number.” Every item in our catalog has a unique ASIN.” |
| IN-15 | [Qualify your outbound links](https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links) | 2025-12-10 | “Mark links that are advertisements or paid placements (commonly called paid links) with the sponsored value.” |
| IN-16 | [What is GitHub Pages?](https://docs.github.com/en/pages/getting-started-with-github-pages/about-github-pages) | — | “GitHub Pages is a static site hosting service that takes HTML, CSS, and JavaScript files straight from a repository on GitHub…” |

Seven further sources are **carried** from `ledger/sources.json` (FTC ×2, Google ×3, Creators API
×1, and the ASIN page's companion rows) and are labelled CARRIED wherever they are cited, with
their own last-verified dates. A carried source is never used to support a value this session
measured.

## 6. The ASIN rule, which is why the intent fields are blank

Every submitted token is **9 characters**. Amazon's help page defines an ASIN as “the 10-digit
code that Amazon uses to denote specific products.” No public Amazon document binds a short code
to a destination ASIN.

So for each submission the four intent fields — `intended_asin`, `intended_listing_url`,
`confirmation_date`, `intended_source` — are blank, and the observed destination is recorded in a
**separate** field. They are never merged, and a gate fails the build if they are
(`tools/validate_intake.py`, negative-tested by case 1 and case 14 in `tools/test_intake.py`).

## 7. What was not verified, and why

| Not verified | Reason |
|---|---|
| The intended ASIN for any of the five | Requires an Associates report or a Creators API call; neither is available without the owner's credentials. |
| Whether `shopnow047c-20` is a valid Associates tracking ID | No official page defines or confirms it. Recorded exactly as submitted, with no attribute attached (IF-07). |
| Whether the links carry a tag when clicked from an enrolled account | Needs a signed-in Associates session (IQ-04). |
| Who operates `amzlinks.in` | Not confirmable from any official Amazon page found (IF-05). |
| Price, rating, review count, sales rank | Not recorded anywhere. Program Policies restrict their display outside an Amazon link or licensed API, and nothing in this task needed them. |

## 8. Irregularity found in an existing control (CR-2, logged not fixed)

While writing the price rule for this namespace's gate, the pattern used by six other gates was
tested and found inert:

```python
units = re.split(r"</tr>|</p>|</li>|<br\s*/?>", re.sub(r"<[^>]+>", " ", t))
for unit in units:
    for m in MONEY.finditer(unit):
        if PRICE_CONTEXT.search(unit) and not PROGRAM_CONTEXT.search(unit):   # never true
```

`re.sub` strips the tags **before** `re.split` looks for them, so `units` collapses to
`[whole page]`. The mandatory disclosure contains the word “earn”, which `PROGRAM_CONTEXT`
matches, so `not PROGRAM_CONTEXT.search(unit)` is always false and the rule never fires.

Reproduced on three real pages: an injected `<p>Buy now at the current price of $149.99 today.</p>`
was **not** reported by that ordering. Splitting on block tags *before* stripping them fixes it,
which is what `tools/validate_intake.py` does (and its negative test case 12 confirms it fires).

Present in: `.github/workflows/pages.yml` (×2), `tools/validate_data.py:550`,
`tools/validate_audit.py:272`, `tools/validate_decisions.py:284`, `tools/build_readiness.py:623`.
All outside this session's file scope, so logged as CR-2 in `COORDINATION.md` rather than edited.

## 9. Gates

Every gate in the repository was run on the combined tree after this work: **46 of 46 CI steps
pass**, including the three added for this namespace (drift check, contract gate, and 16 negative
tests — baseline clean, all 16 injected defects fire).

## 10. A defect in this session's own first publish, and what it produced

Reading the deployed page (not the gate) caught a typed count that had drifted from the log:
`SUB-01` rendered "2 observation(s)" while only `OBS-02` referenced it. The count had been typed
into `intake/data/submissions.json` rather than measured — the same class as CR-1 and FB-01/FB-02
elsewhere in this repository.

Two changes came out of it, so the class cannot recur here:

1. `tools/build_intake.py` now renders the observation count **derived** from
   `observations.json` in the same run, rather than reading the typed field.
2. `tools/validate_intake.py::check_observation_counts` fails the build when the register's typed
   value disagrees with the derived one, and `tools/test_intake.py` case 16 proves the rule fires.

This is worth recording because the defect survived 15 negative tests, a passing contract gate and
a green CI run. It was found by reading the page a reader would see.
