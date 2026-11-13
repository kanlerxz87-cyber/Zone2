"""ASIN identity guard.

The single most important gate in this repository: nothing may be written about a product until its
identifier has been *validated* and *resolved*.  Both checks must pass.

Why this exists (see COORDINATION.md V-01..V-05 / ledger/flags.json F-01): the three identifiers supplied in the
project brief (B04G1MEwY, B02NbDxp3, B00hJ57DV) are 9 characters long.  An Amazon Standard Identification
Number is 10 characters, so none of them can address a catalog record, and every downstream field
(title, brand, category, price, rating, commission band, ...) is therefore unavailable rather than merely
unset.  This module encodes that so a future automation run cannot paper over it.

No Amazon trademark is used in this project's own naming (Participation Requirements, R-11).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# ASIN: 10 alphanumeric characters.  Books are the documented exception where the ASIN is the ISBN-10,
# which may contain an 'X' check digit.  Everything else observed in Amazon catalog URLs is uppercase
# alphanumeric beginning with an alnum character.
ASIN_RE = re.compile(r"^[A-Z0-9]{10}$")
ISBN10_RE = re.compile(r"^[0-9]{9}[0-9X]$")

MARKETPLACE_HOSTS = {
    "amazon.com": ".com",
    "amazon.co.uk": ".co.uk",
    "amazon.de": ".de",
    "amazon.fr": ".fr",
    "amazon.it": ".it",
    "amazon.es": ".es",
    "amazon.ca": ".ca",
    "amazon.co.jp": ".co.jp",
    "amazon.com.au": ".com.au",
    "amazon.in": ".in",
    "amazon.com.mx": ".com.mx",
    "amazon.com.br": ".com.br",
    "amazon.nl": ".nl",
    "amazon.se": ".se",
    "amazon.pl": ".pl",
    "amazon.sg": ".sg",
    "amazon.com.tr": ".com.tr",
    "amazon.ae": ".ae",
    "amazon.sa": ".sa",
    "amazon.eg": ".eg",
}


@dataclass(frozen=True)
class Verdict:
    asin: str
    valid: bool
    reason: str
    normalized: str = ""

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"{'PASS' if self.valid else 'FAIL'} {self.asin!r}: {self.reason}"


def normalize(token: str) -> str:
    """Uppercase + strip surrounding noise.  Deliberately does NOT repair length or characters:
    inserting a guessed character would manufacture an identifier for a product we cannot confirm
    exists, which is exactly the failure this guard prevents."""
    return (token or "").strip().upper().lstrip("/")


def validate_asin(token: str) -> Verdict:
    cand = normalize(token)
    if not cand:
        return Verdict(token, False, "empty identifier")
    if len(cand) != 10:
        return Verdict(
            token,
            False,
            f"length {len(cand)} != 10; an ASIN is a 10-character identifier, so this token cannot "
            "address a catalog record (do not pad or guess the missing character)",
        )
    if not ASIN_RE.match(cand):
        bad = sorted({c for c in cand if not c.isalnum() or (c.isalpha() and not c.isupper())})
        return Verdict(token, False, f"contains non-ASIN characters {bad}")
    if ISBN10_RE.match(cand) and "X" in cand:
        digits = [int(c) for c in cand[:9]]
        total = sum((10 - i) * d for i, d in enumerate(digits))
        check = (11 - total % 11) % 11
        if check != 10:  # 10 is rendered as 'X'
            return Verdict(cand, False, "looks like an ISBN-10 but the check digit does not validate")
        return Verdict(cand, True, "valid ISBN-10 form (books use the ISBN-10 as their ASIN)", cand)
    return Verdict(cand, True, "valid 10-character identifier format", cand)


def extract_asin_from_url(url: str) -> Verdict:
    """Pull the identifier out of a canonical product URL: /dp/<ASIN>, /gp/product/<ASIN>, /product/<ASIN>.

    The ASIN is the path segment immediately after /dp/ or /gp/product/ - any trailing query string is
    link decoration (tag, sub-tag, ref, mrkID...) and must not be treated as part of the identifier.
    """
    if not url:
        return Verdict(url or "", False, "no URL supplied")
    m = re.search(r"(?:/dp/|/gp/product/|/product/)([A-Za-z0-9]{6,20})", url)
    if not m:
        return Verdict(
            url,
            False,
            "no /dp/ or /gp/product/ identifier found in the URL; a short link whose token is not a valid "
            "ASIN cannot be used to establish product identity - resolve it to a canonical product URL first",
        )
    return validate_asin(m.group(1))


def canonical_product_url(asin: str, marketplace: str = "amazon.com") -> str:
    host = MARKETPLACE_HOSTS.get(marketplace)
    if host is None:
        raise ValueError(f"unsupported marketplace host {marketplace!r}")
    return f"https://{marketplace}/dp/{normalize(asin)}"


if __name__ == "__main__":  # pragma: no cover - manual check
    for t in ["B04G1MEwY", "B02NbDxp3", "B00hJ57DV"]:
        print(validate_asin(t))
    for u in [
        "https://link.amazon/B04G1MEwY",
        "https://www.amazon.com/dp/B08N5WRWNW?tag=example-20&psc=1",
    ]:
        print(extract_asin_from_url(u))
