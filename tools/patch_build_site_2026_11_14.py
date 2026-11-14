#!/usr/bin/env python3
"""T23 final integration: extend tools/build_site.py so the generated `pages/` namespace publishes
the resolved destinations of the three supplied links, with a source link on every row.

Run once by the final integration session. Idempotent: re-running is a no-op once the patch is in.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BUILD = REPO / "tools" / "build_site.py"
src = BUILD.read_text(encoding="utf-8")

MARKER = "T23-INTEGRATION"
if MARKER in src:
    print("already patched")
    raise SystemExit(0)

# ------------------------------------------------------------------ 1. products page: resolved rows
old = '''    whys = "".join(
        "\\n".join(
            [
                "<div class=\\"why\\"><dt>"
                + esc(f"{e['id']} \\u00b7 {e['token_as_given']}")
                + "</dt><dd>"
                + esc(e["why_blank"])
                + "</dd><dd class=\\"flags-inline\\">Flags: "
                + " ".join(f"<a href=\\"flags.html#{esc(f)}\\">{esc(f)}</a>" for f in e["flag_ids"])
                + "</dd></div>"
            ]
        )
        for e in PRODUCTS["entries"]
    )'''

# The file uses a slightly different layout; locate the real block by anchors instead.
start = src.index('    whys = "".join(')
end = src.index('    body = (\n        notice("Verification method"', start)
whys_block = src[start:end]

new_whys = whys_block + '''
    # ---- T23-INTEGRATION: what each supplied link actually resolves to, and its sourced specs ----
    resolved_rows = []
    for e in PRODUCTS["entries"]:
        r = e.get("resolved")
        if not r:
            continue
        resolved_rows.append(
            [
                f'<td><a class="pagelink" href="{esc(e["submitted_url"])}" target="_blank" '
                f'rel="noopener noreferrer nofollow">{esc(e["token_as_given"])}</a></td>',
                text_cell(r["asin"], code=True),
                text_cell(r["title"]),
                text_cell(r["brand"]),
                text_cell(r["category_path"]),
                blank_cell("not republished outside an Amazon link (R-04)"),
                blank_cell("not republished outside an Amazon link (R-04)"),
                blank_cell("needs a licensed API response"),
                f"<td>{status_pill('OBSERVED')}</td>",
                source_cell(r["source_ids"] + r.get("manufacturer_source_ids", [])),
            ]
        )

    spec_tables = ""
    for e in PRODUCTS["entries"]:
        r = e.get("resolved")
        if not r:
            continue
        srows = []
        for sp in r["specs"]:
            if sp.get("status") == "unverified":
                srows.append(
                    [
                        text_cell(sp["attribute"]),
                        blank_cell(sp.get("why_blank") or "not confirmed on an official page"),
                        f"<td>{status_pill('UNVERIFIED')}</td>",
                        source_cell(sp.get("source_ids"), blank_hint="no official source states this value"),
                    ]
                )
            else:
                srows.append(
                    [
                        text_cell(sp["attribute"]),
                        text_cell(sp["value"]),
                        f"<td>{status_pill('CONFLICT' if sp.get('status') == 'conflict' else 'VERIFIED')}</td>",
                        source_cell(sp.get("source_ids")),
                    ]
                )
                if sp.get("source_label"):
                    srows[-1][1] += f'<div class="row-note">{esc(sp["source_label"])}</div>'
        spec_tables += panel(
            f"{r['brand']} {r['asin']} \\u2014 specifications",
            table(["Attribute", "Value", "Status", "Official source"], srows),
            meta=f'<span class="chip">resolved from {esc(e["token_as_given"])}</span>',
        )

'''

src = src[:start] + new_whys + src[end:]

# ------------------------------------------------------------------ 2. products page: new panels
old_panel = '''        + panel("Why each field is blank", f"<dl class=\\"whys\\">{whys}</dl>")
        + panel("Evidence observations (reproducible by hand)", table(["ID", "Observation", "Interpretation", "Status", "Evidence"], ev))'''
new_panel = '''        + panel("Why each field is blank", f"<dl class=\\"whys\\">{whys}</dl>")
        + panel(
            "What each supplied link resolves to (observed 2026-11-14)",
            table(
                [
                    "Supplied link",
                    "Resolved ASIN",
                    "Listing title as published on Amazon",
                    "Brand",
                    "Category path",
                    "Price",
                    "Rating",
                    "Commission band",
                    "Status",
                    "Evidence",
                ],
                resolved_rows,
            ),
            meta=f'<span class="chip">{len(resolved_rows)} links resolved</span>',
        )
        + notice(
            "How to read the two tables above",
            "The first table is about the TOKEN as supplied: it is 9 characters, an ASIN is 10, and "
            "amazon.com/dp/&lt;code&gt; is Amazon's Page Not Found page, so every field is left blank and "
            "flagged. The second table is about the LINK as supplied: each one resolves to exactly one "
            "Amazon product page, reproducibly, and an unknown code on the same service returns a 404 "
            "instead of a product (flag F-20), so the destination is a verified observation of the link's "
            "behaviour. They are kept apart because Amazon publishes no document that binds a "
            "link.amazon code to a product - see flags F-03, F-04 and F-24.",
        )
        + spec_tables
        + panel("Evidence observations (reproducible by hand)", table(["ID", "Observation", "Interpretation", "Status", "Evidence"], ev))'''
assert old_panel in src, "products panel anchor not found"
src = src.replace(old_panel, new_panel, 1)

# ------------------------------------------------------------------ 3. executive summary wording
old_key = '''        ("Requested products can be identified", False, "All three tokens are 9 characters (an ASIN is 10); the canonical /dp/ URLs return Amazon's Page Not Found page; and each submitted short link resolved to a different, unrelated ASIN through a fallback redirect.", ["S16", "S17", "S18", "S19"]),
        ("Marketing copy for those products", False, "The content engine refuses to draft copy for an entry whose identity is unresolved, so zero articles, comparisons and buying guides exist for these inputs.", ["S02"]),'''
new_key = '''        ("What each supplied link resolves to", True, "Each of the three supplied link.amazon URLs resolves to one specific Amazon product page, reproducibly, and an UNKNOWN code on the same service returns a 404 instead of a product - so the codes are honoured lookups, not ignored tokens.", ["S28", "S19", "S20", "S21"]),
        ("The brief's product identity, as a documented contract", False, "Each supplied code is 9 characters (an ASIN is 10), the canonical /dp/ URLs return Amazon's Page Not Found page, and no public Amazon document binds a link.amazon code to a product. The destination is therefore published as an observation, never as a confirmed brief mapping.", ["S16", "S17", "S18", "S24"]),
        ("Marketing copy for those products", False, "The content engine refuses to draft published copy for an entry whose brief mapping is undocumented, so zero articles, comparisons and buying guides are published for these inputs. The verified specification tables above are published; the copy is held pending owner confirmation.", ["S02", "S28"]),'''
assert old_key in src, "exec key anchor not found"
src = src.replace(old_key, new_key, 1)

old_bottom = '''            '<p class="lede">Everything this platform needs in order to earn is built and wired to official data. The three named '
            "products are the one thing that cannot be marketed, because none of the supplied links identifies a product. The site "
            "therefore publishes the mechanism, the sourced economics, and the gaps \\u2014 and nothing else.</p>",'''
new_bottom = '''            '<p class="lede">Everything this platform needs in order to earn is built and wired to official data. The three supplied '
            "links each resolve to one specific Amazon product page - reproducibly, and confirmed by an unknown-code control that "
            "returns a 404 rather than a product - so the site publishes those three products with their manufacturer-verified "
            "specifications and a source link on every row. What it does not publish is copy asserting a brief mapping Amazon does "
            "not document, or any price, rating or commission figure it could not confirm.</p>",'''
assert old_bottom in src, "exec bottom anchor not found"
src = src.replace(old_bottom, new_bottom, 1)

old_finding = '''        "The highest-value action is identifier hygiene, not copywriting: a link that does not resolve to a valid ASIN cannot be researched, written about, tagged, or attributed. The pipeline now fails loudly at that boundary instead of inventing downstream facts.",'''
new_finding = '''        "The highest-value action is identifier hygiene, not copywriting: a link whose code is not a valid ASIN cannot be researched, written about, tagged, or attributed, even when its destination is known. The three supplied codes are exactly that case - they resolve, but they are not ASINs, they carry no Associates tag, and no Amazon document says what they are for.",'''
assert old_finding in src
src = src.replace(old_finding, new_finding, 1)

old_action = '''        ("A1", "Replace the three tokens with valid 10-character ASINs, or full amazon.<tld>/dp/ URLs", "user", "unblocks identity for P-01..P-03, and with it every dependent field", ["S16", "S17", "S18"]),'''
new_action = '''        ("A1", "Confirm in Associates Central that the three resolved destinations are the items to market, and replace the three tokens with valid 10-character ASINs or full amazon.<tld>/dp/ URLs", "user", "unblocks the brief mapping for P-01..P-03, and with it every dependent field and all published copy", ["S16", "S17", "S18", "S28"]),
        ("A1b", "Supply links that carry the Associates tag (…?tag=YOURASSOCIATEID)", "user", "as supplied the three links carry no tag, so they cannot attribute a sale or earn a commission", ["S24", "S19", "S20", "S21"]),'''
assert old_action in src
src = src.replace(old_action, new_action, 1)

BUILD.write_text(src, encoding="utf-8")
print("patched", BUILD)
