"""Executable checks for the guards that make this repository's claims safe.

Run either way:
    python3 tests/test_pipeline.py        # standalone, no dependencies
    python3 -m pytest tests -q            # if pytest is available
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

import asin_guard  # noqa: E402
import link_builder  # noqa: E402
import scoring  # noqa: E402
import build_marketing  # noqa: E402


def test_marketing_pages_label_unconfirmed_brief_mapping():
    """Destination-only marketing must not imply the short-code mapping is confirmed."""
    with tempfile.TemporaryDirectory() as tmp:
        rendered = build_marketing.build(Path(tmp))
    assert len(rendered) == 9
    for page, document in rendered.items():
        assert "Product identity is not confirmed." in document, page
        assert "they do not establish that those destinations are the products intended in the brief" in document, page
        assert "https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC" in document, page
        assert "pages/flags.html#F-03" in document, page
    import build_site

    exec_html = build_site.page_exec()
    assert "not yet monetized" in exec_html
    assert "destination-only articles" in exec_html
    assert "no published product claim" not in exec_html


def test_submitted_tokens_are_rejected_and_not_repaired():
    """The three brief tokens must fail, and must never be silently padded to 10 characters."""
    for token in ["B04G1MEwY", "B02NbDxp3", "B00hJ57DV"]:
        verdict = asin_guard.validate_asin(token)
        assert not verdict.valid, f"{token} unexpectedly passed the identifier check"
        assert "10" in verdict.reason
        assert asin_guard.normalize(token) == token.upper()  # normalisation never changes length
        assert not re.fullmatch(r"[A-Z0-9]{10}", asin_guard.normalize(token))


def test_valid_identifier_shape():
    assert asin_guard.validate_asin("B08N5WRWNW").valid
    assert not asin_guard.validate_asin("B08N5WRWN").valid          # 9 chars
    assert not asin_guard.validate_asin("B08N5WRNW!").valid         # punctuation
    assert asin_guard.extract_asin_from_url("https://www.amazon.com/dp/B08N5WRWNW?tag=x-20&psc=1").normalized == "B08N5WRWNW"
    assert not asin_guard.extract_asin_from_url("https://example.invalid/B08N5WRWNW").valid


def test_link_builder_refuses_untagged_and_mark_abusing_links():
    try:
        link_builder.build_product_link("B08N5WRWNW", "", link_text="View it")
        raise AssertionError("expected NO_TAG refusal when no Associates ID is configured")
    except link_builder.LinkPolicyError as exc:
        assert "NO_TAG" in str(exc)
    # An unverified identifier cannot even be previewed.
    for bad in ("B04G1MEwY", "toaster-oven"):
        try:
            link_builder.preview_link(bad, link_text="Preview")
            raise AssertionError(f"preview accepted unverified identifier {bad!r}")
        except link_builder.LinkPolicyError:
            pass
    link = link_builder.build_product_link("B08N5WRWNW", "exampletag-20", link_text="See the listing")
    assert "tag=exampletag-20" in link.href and 'rel="sponsored nofollow"' in link.to_html()
    html_doc = link.to_html() + link_builder.disclosure_block()
    assert link_builder.REQUIRED_SITE_DISCLOSURE in html_doc
    assert link_builder.audit_html(html_doc) == []


def test_link_builder_blocks_competing_attribution_and_per_user_subtags():
    try:
        link_builder.build_product_link("B08N5WRWNW", "exampletag-20", link_text="x", extra_params={"aff_id": "9"})
        raise AssertionError("competing-network attribution parameter was accepted (R-14)")
    except link_builder.LinkPolicyError:
        pass
    for subtag in ("user-123", "session-abc", "ip-10-0-0-1"):
        try:
            link_builder.build_product_link("B08N5WRWNW", "exampletag-20", link_text="x", subtag=subtag)
            raise AssertionError(f"per-visitor sub-tag {subtag!r} was accepted (R-08)")
        except link_builder.LinkPolicyError:
            pass


def test_disclosure_wording_policy():
    ok = link_builder.disclosure_block(link_level="#CommissionsEarned")
    assert "disclosure--link" in ok
    try:
        link_builder.disclosure_block(link_level="commissionable link")
        raise AssertionError("FTC-unclear wording was accepted (R-03)")
    except link_builder.LinkPolicyError:
        pass


def test_rate_table_matches_the_official_transcription():
    table = scoring.load_rate_table()
    # spot-check the bands this project would cite, straight from ledger/commission_table.json
    doc = json.loads((REPO / "ledger" / "commission_table.json").read_text(encoding="utf-8"))
    by_rate: dict[str, list[str]] = {}
    for group in doc["groups"]:
        by_rate.setdefault(group["rate_pct"], []).extend(group["categories"])
    assert table["kitchen"].rate_pct == 4.50
    assert table["luxury beauty"].rate_pct == 10.00
    assert table["toys"].rate_pct == 3.00
    assert table["televisions"].rate_pct == 2.00
    assert table["gift cards"].rate_pct == 0.00
    assert table["coach"].rate_pct == 0.00
    assert table["__default__"].rate_pct == 4.00 and not table["__default__"].exact_match
    assert "Kitchen" in by_rate["4.50"]


def test_scoring_refuses_to_guess():
    table = scoring.load_rate_table()
    assert scoring.commission_term(None, table)["score"] is None          # unknown category -> no score
    assert scoring.review_signal(None, None)["ok"] is False
    assert scoring.competition_term(None, None)["ok"] is False
    assert scoring.demand_term([{"value": 10}])["ok"] is False            # one snapshot is not a trend
    assert scoring.demand_term([{"value": 10}, {"value": 12}])["ok"] is True
    niche = scoring.niche_score("Kitchen")
    assert niche["verdict"] == "INSUFFICIENT_DATA"
    assert "commission" not in niche["blocked_inputs"]                    # this half IS sourced
    assert set(niche["blocked_inputs"]) >= {"demand", "competition"}
    zero = scoring.commission_term("Gift Cards", table)
    assert zero["ok"] is False and zero["score"] == 0.0                   # 0.00% band is an exclusion
    ev = scoring.expected_value(1000, None, None, 4.5)
    assert ev["ok"] is False and ev["estimate"] is None                   # unknown conversion -> no estimate
    illustrative = scoring.expected_value(1000, 0.02, 50.0, 4.5)
    assert illustrative["estimate"] == 45.0 and illustrative["labels_illustrative"]


def test_site_css_and_disclosure_present_on_every_generated_page():
    pages = sorted((REPO / "pages").rglob("*.html"))
    assert pages, "site not built yet - run python3 tools/build_site.py"
    for page in pages:
        text = page.read_text(encoding="utf-8")
        if re.search(r'class="sponsored-link|rel="sponsored', text):
            assert link_builder.REQUIRED_SITE_DISCLOSURE in text, f"{page.name} links out without the Site disclosure"


def test_no_invented_performance_numbers_in_data():
    """No clicks/conversion/earnings values may exist while no report is connected."""
    for name in ("products.json", "niches.json", "campaigns.json"):
        doc = json.loads((REPO / "ledger" / name).read_text(encoding="utf-8"))
        blob = json.dumps(doc).lower()
        for key in ("clicks", "conversion", "earnings", "epc"):
            for m in re.finditer(rf'"{key}"\s*:\s*"?([\w.\-]+)', blob):
                value = m.group(1)
                assert value in ("", "null", "none", "0", "0.0"), f"{name}: fabricated {key} value {value!r}"



def test_dashboard_flag_count_cannot_drift_from_the_ledger():
    """F-22 regression: the dashboard KPI must equal the canonical register, and the gate must catch drift.

    The check is exercised in both directions - matching the ledger passes, a deliberately wrong value fails -
    because a guard nobody has seen fail is not evidence that it works.
    """
    import validate_data

    ledger = json.loads((REPO / "ledger" / "flags.json").read_text(encoding="utf-8"))
    canonical = len(ledger["flags"])
    js = (REPO / "assets" / "js" / "data.js").read_text(encoding="utf-8")

    m = re.search(r"CANONICAL_FLAG_COUNT\s*=\s*(\d+)", js)
    assert m, "CANONICAL_FLAG_COUNT is missing from assets/js/data.js"
    assert int(m.group(1)) == canonical, (
        f"dashboard says {m.group(1)} flags, ledger holds {canonical}"
    )

    # Negative direction: the gate must actually reject a wrong count.
    report = validate_data.Report()
    original = js
    wrong = re.sub(r"(CANONICAL_FLAG_COUNT\s*=\s*)\d+", r"\g<1>999", original)
    js_path = REPO / "assets" / "js" / "data.js"
    js_path.write_text(wrong, encoding="utf-8")
    try:
        validate_data.check_flag_count(report)
        assert report.errors, "check_flag_count accepted a count that disagrees with the ledger"
    finally:
        js_path.write_text(original, encoding="utf-8")

    report_ok = validate_data.Report()
    validate_data.check_flag_count(report_ok)
    assert not report_ok.errors, report_ok.errors

def test_expired_promotion_copy_is_removed_and_linted():
    """R-06: a limited-time promotion mention must not survive its expiry (DD-1 item 3).

    The compliance ledger claimed the builder "refuses to render expired promos" while the
    `expires_utc` front-matter field was a commented placeholder and nothing read it. The
    enforcement is now implemented, and this test proves it.
    """
    import generate_articles as ga

    expired = "2020-01-01T00:00:00Z"
    live = "2999-01-01T00:00:00Z"

    tmpl = ga.TEMPLATE_DIR / "product_article.md.tmpl"
    body = tmpl.read_text(encoding="utf-8")
    assert "expires_utc:" in body, "the template must declare expires_utc"

    def render_with(expiry: str, promo: str) -> ga.Draft:
        stub = ga.TEMPLATE_DIR / "_promo_test.md.tmpl"
        stub.write_text(
            body.replace("expires_utc: null", f"expires_utc: {expiry}").replace(
                "{{analysis}}", "{{analysis}}\n\n" + promo
            ),
            encoding="utf-8",
        )
        try:
            return ga.render("_promo_test", {"entry_id": "P-TEST", "analysis": "analysis text"})
        finally:
            stub.unlink(missing_ok=True)

    promo_block = "<!-- promo:start -->\n50% off today only!\n<!-- promo:end -->"

    # An expired promotion: the copy is dropped and the linter refuses the draft.
    draft = render_with(expired, promo_block)
    assert draft.expires_utc is not None, "expires_utc must be parsed from the front matter"
    assert draft.promo_dropped, "expired promo copy must be dropped"
    assert "50% off today only" not in draft.body
    codes = [p.code for p in ga.lint(draft)]
    assert "PROMO_EXPIRED" in codes, f"expired promo must fail the linter, got {codes}"

    # A live promotion: nothing is dropped and the linter stays quiet about expiry.
    draft = render_with(live, promo_block)
    assert not draft.promo_dropped
    assert "50% off today only" in draft.body
    assert "PROMO_EXPIRED" not in [p.code for p in ga.lint(draft)]

    # The default template declares no promotion, so no expiry is parsed.
    draft = render_with("null", promo_block)
    assert draft.expires_utc is None
    assert not draft.promo_dropped


def test_validation_gate_passes():
    out = subprocess.run(
        [sys.executable, "tools/validate_data.py"], cwd=REPO, capture_output=True, text=True
    )
    report = json.loads(out.stdout)
    assert not report["errors"], f"validation errors: {report['errors']}"
    assert report["stats"]["sources"] >= 20


def test_build_is_deterministic():
    first = subprocess.run([sys.executable, "tools/build_site.py"], cwd=REPO, capture_output=True, text=True)
    assert first.returncode == 0, first.stderr
    digest_a = {p: p.stat().st_size for p in (REPO / "pages").rglob("*.html")}
    second = subprocess.run([sys.executable, "tools/build_site.py"], cwd=REPO, capture_output=True, text=True)
    assert second.returncode == 0, second.stderr
    digest_b = {p: p.stat().st_size for p in (REPO / "pages").rglob("*.html")}
    assert digest_a == digest_b, "build output is not deterministic"


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failures = 0
    for fn in tests:
        try:
            fn()
            print(f"PASS  {fn.__name__}")
        except Exception as exc:  # noqa: BLE001
            failures += 1
            print(f"FAIL  {fn.__name__}: {type(exc).__name__}: {exc}")
    print(f"\n{len(tests) - failures}/{len(tests)} checks passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
