"""One definition of the generated <head> layer, shared by every generator that owns a page.

Why this module exists
----------------------
Four different generators write complete HTML pages into this repository, and each one
compares its output with the committed file to detect drift:

    tools/build_root_views.py   -> verification.html, sources.html
    tools/build_summary.py      -> summary.html
    tools/build_site.py         -> pages/**
    tools/build_marketing.py    -> marketing/**
    tools/build_decisions.py    -> decisions/**

A separate, additive contribution is the canonical URL, the Open Graph tags and the
schema.org graph emitted by `tools/build_meta.py`. Two of the pages built by the
generators above are *also* pages that need that layer (the dashboard's two evidence
views and the executive summary). Without a shared definition, one of two bad things
happens:

  * the generators do not know about the layer, so `build_meta.py` appends it and
    `build_root_views.py --check` immediately reports both pages as drifted — a gate
    failure that is nobody's fault and that a future contributor "fixes" by deleting
    the layer; or
  * each generator re-implements the layer, and two different canonical URLs or two
    different schema graphs end up on one site.

This module is the same pattern as `tools/flag_state.py`, which exists because three
surfaces published three different open-flag counts. One predicate, imported everywhere.

What it does
------------
`normalize(text)` removes the generated block, so a generator can compare what it
actually authored against what is on disk. `apply(text)` inserts the block back. A
generator then writes `apply(rendered)` and checks `normalize(committed) == normalize(rendered)`.

The block is delimited by `tools/build_meta.MARK_BEGIN` / `MARK_END`. If the markers are
ever removed from the module, normalization becomes a no-op and the gates revert to
whole-file comparison, which is the current behaviour — a safe failure mode.
"""

from __future__ import annotations

import re

from build_meta import BEGIN as MARK_BEGIN, END as MARK_END  # noqa: E402  (single source of truth)

_BLOCK = re.compile(re.escape(MARK_BEGIN) + r".*?" + re.escape(MARK_END) + r"\n?", re.S)


def has_block(text: str) -> bool:
    return MARK_BEGIN in text


def normalize(text: str) -> str:
    """The page as the generator authored it, with the generated head layer removed."""
    return _BLOCK.sub("", text)


def apply(text: str, rel: str) -> str:
    """Insert (or refresh) the generated head layer for page `rel`."""
    from build_meta import block_for  # local import: avoids a cycle at module load

    return block_for(text, rel)


def same_page(committed: str, rendered: str) -> bool:
    """True when the committed file differs from a fresh render only by the generated layer."""
    return normalize(committed) == normalize(rendered)
