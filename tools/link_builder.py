"""Affiliate link + disclosure emitter with policy guards baked in.

Every rule enforced here is traced in data/compliance.json:
  R-01 disclosure sentence (Operating Agreement Sec. 5, source S01)
  R-02 link-level disclosure wording Amazon accepts (S05)
  R-03 FTC accepted/rejected wording (S10)
  R-07 tagged Special Link format, direct access, no bookmarking (S02)
  R-08 sub-tags must never be tied to a specific end user (S02)
  R-11 no Amazon mark in our own naming/tag (S02)
  R-14 no competing-network attribution parameter on the same link (S02)
  R-17 rel="sponsored" for affiliate links (S12/S13)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from urllib.parse import parse_qs, urlencode, urlparse

from asin_guard import MARKETPLACE_HOSTS, normalize, validate_asin

# Operating Agreement Sec. 5 wording. Verbatim, because it is prescribed.
REQUIRED_SITE_DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."

# Amazon's own help page (S05) lists these as examples of a *clear* link-level disclosure.
DISCLOSURE_OK = (
    "(paid link)",
    "#ad",
    "#CommissionsEarned",
    "I earn commissions from qualifying purchases",
    "As an Amazon Associate I earn from qualifying purchases.",
)
# FTC guidance (S10) calls this one out as probably not a clear disclosure.
DISCLOSURE_BANNED = ("commissionable link", "affiliate stuff", "some links maybe pay")

TAG_RE = re.compile(r"^[a-z0-9]+-\d{2}$")
# R-08: a sub-tag must be a static campaign label, never something derived from the visitor.
SUBTAG_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,47}$")
COMPETING_ATTRIBUTION_PARAMS = {
    "aff_id",
    "aigid",
    "cjclickid",
    "clickid",
    "irclickid",
    "u",
    "cv",
    "awc",
    "anid",
}


class LinkPolicyError(ValueError):
    """Raised instead of emitting a non-compliant link. Never auto-silenced."""


@dataclass
class SponsoredLink:
    href: str
    text: str
    rel: str = "sponsored nofollow"
    disclosure: str = ""
    warnings: list[str] = field(default_factory=list)

    def to_html(self) -> str:
        return (
            f'<a class="sponsored-link" href="{self.href}" rel="{self.rel}" target="_blank" '
            f'referrerpolicy="no-referrer-when-downgrade">{self.text}</a>'
        )


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise LinkPolicyError(message)


def build_product_link(
    asin: str,
    associates_tag: str,
    *,
    subtag: str | None = None,
    marketplace: str = "amazon.com",
    link_text: str,
    disclosure: str = REQUIRED_SITE_DISCLOSURE,
    extra_params: dict[str, str] | None = None,
) -> SponsoredLink:
    """Compose a compliant tagged product link.

    ``associates_tag`` is the ID Amazon assigns to the account; when it is absent the caller must use
    :func:`preview_link` instead - an untagged link earns nothing and an invented tag is worse.
    """
    verdict = validate_asin(asin)
    _require(verdict.valid, f"refusing to link an unverified identifier: {verdict.reason}")
    _require(
        marketplace in MARKETPLACE_HOSTS,
        f"marketplace {marketplace!r} is not a recognized Amazon Site host; Special Links must point at an Amazon Site",
    )
    _require(bool(link_text and link_text.strip()), "link text is required (no bare 'click here' links)")
    _require(
        "amazon" not in normalize(link_text).lower() and "associates" not in link_text.lower(),
        "link text must not present itself as an Amazon-branded element (R-11)",
    )
    if associates_tag:
        _require(
            bool(TAG_RE.match(associates_tag)),
            "Associates ID must use the tagged format assigned by Amazon (e.g. exampletag-20); do not invent one",
        )
    else:
        raise LinkPolicyError(
            "NO_TAG: an Associates ID was not supplied. Use preview_link() for a non-publishing placeholder."
        )
    if subtag:
        _require(
            bool(SUBTAG_RE.match(subtag)),
            "sub-tag must be a static lowercase campaign label (R-08); never a user/session/IP-derived value",
        )
        _require(
            not any(tok in subtag for tok in ("user", "uid", "session", "ip", "visitor")),
            "sub-tag looks user-derived, which the Participation Requirements forbid (R-08)",
        )

    params: dict[str, str] = {"tag": associates_tag}
    if subtag:
        params["linkCode"] = "sl1"
        params["tag"] = f"{associates_tag}-{subtag}" if not associates_tag.endswith("-" + subtag) else associates_tag
    for key, val in (extra_params or {}).items():
        _require(
            key.lower() not in COMPETING_ATTRIBUTION_PARAMS,
            f"parameter {key!r} is a competing-network attribution field; combining attribution is prohibited (R-14)",
        )
        params[key] = val

    href = f"https://{marketplace}/dp/{verdict.normalized}?{urlencode(params)}"
    _require("tag=" in href, "a Special Link must carry the Associates tag as a URL parameter (R-07)")
    return SponsoredLink(href=href, text=link_text, disclosure=disclosure)


def preview_link(asin: str, *, link_text: str, marketplace: str = "amazon.com") -> SponsoredLink:
    """Inert, clearly-labelled placeholder used when no Associates ID exists yet (F-07).

    It is *not* a monetized link and is never written into publishable markup without the tag.
    """
    verdict = validate_asin(asin)
    _require(verdict.valid, f"cannot even preview an unverified identifier: {verdict.reason}")
    return SponsoredLink(
        href=f"https://{marketplace}/dp/{verdict.normalized}",
        text=link_text,
        rel="sponsored nofollow",
        disclosure="",
        warnings=["NO_TAG - NOT FOR PUBLICATION: no Associates ID is configured (see Flagged for Review F-07)"],
    )


def disclosure_block(site_level: bool = True, link_level: str = "(paid link)") -> str:
    """Return the disclosure HTML. Both halves are mandatory: the Site statement (S01 Sec. 5) and a
    clear/conspicuous statement near the link itself (S05, S10)."""
    parts = []
    if site_level:
        parts.append(f'<p class="disclosure" data-rule="R-01">{REQUIRED_SITE_DISCLOSURE}</p>')
    _require(
        any(ok in link_level for ok in DISCLOSURE_OK) or link_level.strip().lower() not in DISCLOSURE_BANNED,
        f"link-level disclosure {link_level!r} is not acceptable wording (R-03)",
    )
    _require(
        not any(b in link_level.lower() for b in DISCLOSURE_BANNED),
        f"link-level disclosure {link_level!r} uses wording the FTC calls unclear (R-03)",
    )
    parts.append(f'<p class="disclosure disclosure--link" data-rule="R-02">{link_level}</p>')
    return "\n".join(parts)


def audit_html(html: str) -> list[str]:
    """Used by the deploy gate: catch non-compliant affiliate markup in built output."""
    problems: list[str] = []
    for m in re.finditer(r"<a\b[^>]*>", html, flags=re.I):
        tag = m.group(0)
        href = re.search(r'href="([^"]+)"', tag)
        if not href:
            continue
        host = urlparse(href.group(1)).netloc.lower()
        if host.split(":")[0] in MARKETPLACE_HOSTS:
            rel = re.search(r'rel="([^"]*)"', tag)
            if not rel or "sponsored" not in rel.group(1).lower():
                problems.append(f"Amazon link without rel=\"sponsored\": {href.group(1)[:80]}")
            if "tag=" not in href.group(1) and "NOT FOR PUBLICATION" not in html:
                problems.append(f"Amazon link without an Associates tag parameter: {href.group(1)[:80]}")
    if "sponsored-link" in html and REQUIRED_SITE_DISCLOSURE not in html:
        problems.append("page contains a sponsored link but not the required Site disclosure sentence (R-01)")
    if "sponsored-link" in html and "disclosure--link" not in html:
        problems.append("page contains a sponsored link but no link-level disclosure (R-02)")
    for banned in DISCLOSURE_BANNED:
        if banned in html.lower():
            problems.append(f"banned disclosure wording present: {banned!r} (R-03)")
    # R-08: a per-visitor sub-tag would show up as request interpolation in the emitted href.
    if re.search(r"[?&](tag|subtag|linkCode)=[^\"']*\{", html):
        problems.append("template placeholder left inside a link parameter - would produce per-user tagging (R-08)")
    return problems


def parse_tag_from_href(href: str) -> dict[str, str]:
    q = parse_qs(urlparse(href).query)
    return {k: v[0] for k, v in q.items()}


if __name__ == "__main__":  # pragma: no cover
    print(build_product_link("B08N5WRWNW", "exampletag-20", link_text="See the listing on Amazon").to_html())
    print(preview_link("B08N5WRWNW", link_text="Preview only").warnings)
    for bad in [("B04G1MEwY", "invalid identifier"), ("B08N5WRWNW", "invented mark")]:
        try:
            build_product_link(bad[0], "exampletag-20", link_text=bad[1])
        except LinkPolicyError as exc:
            print("blocked:", exc)
