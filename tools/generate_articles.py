"""Content engine: render SEO articles/comparisons/buying guides *only* from verified facts.

The generator is deliberately conservative.  It renders a draft when, and only when, the entry carries a
resolved product identity (from the catalog API), and every interpolated value traces to a stored source.
Otherwise it emits a refusal record explaining what is missing - which is the state all three
brief-supplied items are in (Flagged for Review F-06).

Linters enforce the compliance rules recorded in ledger/compliance.json.  A draft that fails any lint is not
written to the publish directory, so "auto-publish" can never publish a policy violation.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

from link_builder import REQUIRED_SITE_DISCLOSURE, audit_html  # noqa: E402

TEMPLATE_DIR = REPO / "content" / "templates"
OUT_DIR = REPO / "content" / "published"

PLACEHOLDER_RE = re.compile(r"\{\{\s*([a-z0-9_]+)\s*\}\}", re.I)
SUPERLATIVE_RE = re.compile(
    r"\b(best|worst|guaranteed|#1|number one|perfect|foolproof|cure|risk-free)\b", re.I
)
ABSOLUTE_CLAIM_RE = re.compile(r"\b(last[sd]? ?chance|only (place|site)|end[sd]? today|expires tonight)\b", re.I)
EXPERIENCE_CLAIM_RE = re.compile(
    r"\b(i (tested|used|tried|owned)|after \d+ (days|weeks|months) of use|in my experience)\b", re.I
)

# Terms that would assert an endorsement or affiliation Amazon forbids (Operating Agreement Sec. 5).
FORBIDDEN_IMPLICATIONS = ("officially endorsed by amazon", "partnered with amazon", "amazon recommends")


@dataclass
class LintError:
    code: str
    message: str


@dataclass
class Draft:
    slug: str
    kind: str
    body: str
    missing: list[str]
    blocked: bool
    # R-06: a limited-time promotion must disappear from the Site the moment it ends.
    # The front matter may declare `expires_utc`; when it is in the past the promo copy is
    # dropped and the linter refuses any draft that still mentions the promotion.
    expires_utc: datetime | None = None
    promo_dropped: bool = False


def _load_ledger() -> dict:
    return json.loads((REPO / "ledger" / "products.json").read_text(encoding="utf-8"))


def resolve_entry(entry_id: str) -> dict:
    """Fetch the verified record for an entry.

    Only ledger/catalog_verified.json (written by the collector from an API response) can supply facts.  If it
    is absent, the entry has no verified facts - full stop.
    """
    verified_path = REPO / "ledger" / "catalog_verified.json"
    verified = {}
    if verified_path.exists():
        doc = json.loads(verified_path.read_text(encoding="utf-8"))
        verified = doc.get("items", {}).get(entry_id, {})
    ledger = _load_ledger()
    base = next((e for e in ledger["entries"] if e["id"] == entry_id), None)
    if base is None:
        raise KeyError(entry_id)
    merged = dict(base)
    merged.update({k: v for k, v in verified.items() if v not in (None, "")})
    merged["_verified"] = bool(verified.get("resolved"))
    return merged


# Front-matter fields the templates declare. `expires_utc` is the only one with a policy
# meaning (Participation Requirements 2(b): a limited-time promotion mention must be removed
# from the Site as soon as the promotion ends on the Amazon Site).
FRONT_MATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.S)
EXPIRES_FIELD_RE = re.compile(r"^expires_utc:\s*(?P<value>[^#\n]*?)\s*(?:#.*)?$", re.M)
PROMO_BLOCK_RE = re.compile(
    r"<!--\s*promo:start\s*-->.*?<!--\s*promo:end\s*-->\n?", re.S
)
PROMO_SECTION_RE = re.compile(r"^##\s+(?:Promotion|Limited[- ]time offer)\b.*?(?=^##\s|\Z)", re.S | re.M)


def _parse_front_matter(text: str) -> dict:
    """Return the declared front-matter fields of a rendered draft."""
    m = FRONT_MATTER_RE.match(text)
    if not m:
        return {}
    fields = {}
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        fields[key.strip()] = value.split("#")[0].strip()
    return fields


def _parse_expiry(value: str | None) -> datetime | None:
    """Parse an `expires_utc` front-matter value. `null`/empty means no promotion."""
    if not value:
        return None
    value = value.strip().strip('"').strip("'")
    if value.lower() in ("null", "none", "~"):
        return None
    text = value.replace("Z", "+00:00")
    for fmt in (None, "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            parsed = (
                datetime.fromisoformat(text)
                if fmt is None
                else datetime.strptime(text, fmt)
            )
        except ValueError:
            continue
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    return None


def render(kind: str, ctx: dict) -> Draft:
    tmpl = (TEMPLATE_DIR / f"{kind}.md.tmpl").read_text(encoding="utf-8")
    missing = sorted({m for m in PLACEHOLDER_RE.findall(tmpl) if not str(ctx.get(m, "")).strip()})
    body = PLACEHOLDER_RE.sub(lambda m: str(ctx.get(m.group(1), "")), tmpl)
    body = body.strip() + "\n"

    # R-06 - drop expired promotion copy before the draft can reach the publish directory.
    expires_utc = None
    promo_dropped = False
    m = EXPIRES_FIELD_RE.search(body)
    if m:
        expires_utc = _parse_expiry(m.group("value"))
        if expires_utc and expires_utc <= datetime.now(timezone.utc):
            body, n = PROMO_BLOCK_RE.subn("", body)
            body, n2 = PROMO_SECTION_RE.subn("", body)
            promo_dropped = bool(n or n2)

    slug = re.sub(r"[^a-z0-9-]", "-", str(ctx.get("slug") or ctx.get("entry_id", "draft")).lower()).strip("-")
    return Draft(
        slug=slug,
        kind=kind,
        body=body,
        missing=missing,
        blocked=bool(missing),
        expires_utc=expires_utc,
        promo_dropped=promo_dropped,
    )


def lint(draft: Draft, *, html: str = "") -> list[LintError]:
    problems: list[LintError] = []
    text = draft.body

    # R-01/R-02 - disclosure must exist and sit adjacent to the recommendation.
    if REQUIRED_SITE_DISCLOSURE not in text:
        problems.append(LintError("DISCLOSURE_MISSING", "required Site disclosure sentence absent (R-01)"))
    first_link = re.search(r"https://www\.amazon\.[a-z.]+/(dp|gp/)", text)
    first_disc = text.find(REQUIRED_SITE_DISCLOSURE)
    if first_link and first_disc != -1 and first_link.start() < first_disc:
        problems.append(
            LintError("DISCLOSURE_POSITION", "first affiliate link appears before the disclosure block (R-02)")
        )

    # R-06 - no unverifiable superlatives / absolute claims without evidence markup.
    for rx, code in (
        (SUPERLATIVE_RE, "SUPERLATIVE"),
        (ABSOLUTE_CLAIM_RE, "URGENCY"),
        (re.compile("|".join(map(re.escape, FORBIDDEN_IMPLICATIONS)), re.I), "IMPLICATION"),
    ):
        for m in rx.finditer(text):
            line = text[: m.start()].count("\n") + 1
            if f"<!--evidence:" not in text.split("\n")[line - 1]:
                problems.append(LintError(code, f"claim without inline evidence reference on line {line}: {m.group(0)!r}"))

    # R-10/claims - no invented first-hand experience for an unverified product.
    if EXPERIENCE_CLAIM_RE.search(text):
        problems.append(
            LintError("FABRICATED_EXPERIENCE", "text claims hands-on use; only a real test may say so (R-06)")
        )

    # Never leak an unresolved placeholder into published copy.
    if "UNVERIFIED" in text and "FLAGGED" not in text:
        problems.append(LintError("LEAKY_PLACEHOLDER", "UNVERIFIED marker without the flag reference"))

    # R-06 - a limited-time promotion must not survive its expiry.
    if draft.expires_utc and draft.expires_utc <= datetime.now(timezone.utc):
        if draft.promo_dropped:
            problems.append(
                LintError(
                    "PROMO_EXPIRED",
                    f"promotion expired at {draft.expires_utc.isoformat()} and its copy was dropped (R-06); "
                    "this draft must not be published with the promotion",
                )
            )
        elif PROMO_SECTION_RE.search(text) or PROMO_BLOCK_RE.search(text):
            problems.append(
                LintError(
                    "PROMO_EXPIRED",
                    f"promotion expired at {draft.expires_utc.isoformat()} but promo copy is still present (R-06)",
                )
            )

    if html:
        problems.extend(LintError("HTML_AUDIT", p) for p in audit_html(html))
    return problems


def generate(entry_id: str, kinds=("product_article", "comparison", "buying_guide")) -> list[dict]:
    entry = resolve_entry(entry_id)
    results: list[dict] = []
    for kind in kinds:
        if not entry.get("_verified"):
            results.append(
                {
                    "entry": entry_id,
                    "kind": kind,
                    "status": "REFUSED_UNVERIFIED_IDENTITY",
                    "missing_fields": ["title", "brand", "category", "specifications", "offer"],
                    "reason": (
                        "product identity is not established by an official catalog record, so no article, "
                        "comparison, or buying guide may be written (see Flagged for Review F-01/F-06)"
                    ),
                    "would_enable": "store a Creators API GetItems response in ledger/catalog_verified.json",
                }
            )
            continue
        ctx = {
            "entry_id": entry_id,
            "slug": f"{entry_id.lower()}-{kind}",
            "title": entry.get("title", ""),
            "brand": entry.get("brand", ""),
            "category": entry.get("category", ""),
            "asin": entry.get("asin", ""),
            "as_of": entry.get("as_of", ""),
            "price_note": "shown from the dated API offer record only",
            "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "analysis": entry.get("analysis", ""),
        }
        draft = render(kind, ctx)
        problems = lint(draft)
        if draft.blocked or problems:
            results.append(
                {
                    "entry": entry_id,
                    "kind": kind,
                    "status": "BLOCKED_BY_LINT",
                    "missing_fields": draft.missing,
                    "lint": [f"{p.code}: {p.message}" for p in problems],
                }
            )
            continue
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        out = OUT_DIR / f"{draft.slug}.md"
        out.write_text(draft.body, encoding="utf-8")
        results.append({"entry": entry_id, "kind": kind, "status": "PUBLISHED_CANDIDATE", "path": str(out.relative_to(REPO))})
    return results


if __name__ == "__main__":  # pragma: no cover
    ids = sys.argv[1:] or [e["id"] for e in _load_ledger()["entries"]]
    out = {i: generate(i) for i in ids}
    print(json.dumps(out, indent=2))
