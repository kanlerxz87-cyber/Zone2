#!/usr/bin/env python3
"""Single source of truth for the Associates tag and the site's link state.

Every generator that emits a product link reads the tag from `ledger/site_config.json`
through this module — never from a constant in a builder — so the moment the owner
supplies a tag (or withdraws it) one file changes and every surface follows.

Policy enforced here (each rule is traced in ledger/compliance.json):

  * an empty/missing tag means preview links: `link_state()` returns "PREVIEW_NO_TAG"
    and callers must label the link non-earning (the historic state of this site);
  * a tag must match the tagged format Amazon assigns (``exampletag-20``) and must
    contain no Amazon mark (R-11) — a malformed or infringing tag raises, it never
    silently degrades into an invented link;
  * the href is composed by `tools/link_builder.build_product_link` (R-07/R-08/R-14),
    so the tag is applied only through the audited Special-Link path;
  * evidence URLs recorded in the ledgers (observed redirect targets, cited source
    links) are **never** routed through this module. What was observed is recorded
    as observed; the tag belongs only on links this site publishes for the reader.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))

from link_builder import TAG_RE, LinkPolicyError, build_product_link  # noqa: E402

CONFIG = REPO / "ledger" / "site_config.json"

_MARKS = ("amazon", "amzn", "prime", "kindle")


def load() -> dict:
    if not CONFIG.exists():
        return {}
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def associates_tag() -> str:
    """The configured Associates tag, or '' when none is configured.

    Raises on a tag that could not have been assigned by Amazon (wrong shape) or
    that contains an Amazon mark (R-11) — a bad tag is a build failure, never a
    silently untagged link.
    """
    tag = str(load().get("associates_tag") or "").strip()
    if not tag:
        return ""
    if not TAG_RE.match(tag):
        raise LinkPolicyError(
            f"site_config: associates_tag {tag!r} is not the tagged format Amazon assigns (e.g. exampletag-20)"
        )
    lowered = tag.lower()
    for mark in _MARKS:
        if mark in lowered:
            raise LinkPolicyError(
                f"site_config: associates_tag {tag!r} contains the Amazon mark {mark!r} (R-11)"
            )
    return tag


def link_state() -> str:
    """'TAGGED' when a valid tag is configured, 'PREVIEW_NO_TAG' otherwise."""
    return "TAGGED" if associates_tag() else "PREVIEW_NO_TAG"


def product_href(asin: str) -> str:
    """The outbound href for a product: a tagged Special Link, or the untagged preview.

    The ASIN is validated by link_builder (10-character identifier check) either way,
    so neither branch can publish a link to an unverified identifier.
    """
    tag = associates_tag()
    if tag:
        link = build_product_link(
            asin,
            tag,
            link_text="see this model on the listing",
            extra_params=None,
        )
        return link.href
    from link_builder import preview_link  # local import: preview path only

    return preview_link(asin, link_text="see this model on the listing").href


def tag_amazon_url(url: str) -> str:
    """Append the Associates tag to an Amazon product-listing URL (R-07).

    Used for source citations whose displayed text is the exact page a fact was read
    from: the citation stays a plain listing URL on the page, while the href becomes a
    Special Link so every outbound path to an Amazon listing is tagged uniformly. A URL
    that is not a product listing (category browse pages, 9-character not-found codes)
    is returned unchanged — only a validated ASIN earns a tag.
    """
    tag = associates_tag()
    if not tag:
        return url
    try:
        from asin_guard import extract_asin_from_url

        verdict = extract_asin_from_url(url)
    except Exception:
        return url
    if not getattr(verdict, "valid", False):
        return url
    return product_href(verdict.normalized)


def disclosure_variant() -> str:
    """The second sentence of the site disclosure strip, true for the current link state."""
    if link_state() == "TAGGED":
        return (
            "Links marked (paid link) are Special Links carrying our Associates ID "
            "(shopnow047c-20), so a purchase through one may earn this site a commission "
            "at no extra cost to you."
        )
    return (
        "Product links on this site carry no Associates tag yet, so they are preview links "
        "and earn nothing."
    )
