# Review note — session `bfb20351`

**Task:** T41 — correct an unsupported operator-location claim in the public Questions register.

## Finding and correction

The published Q-01 entry said, “The operator location in the brief is Osaka, Japan.” Q-07 repeated that assertion. The user brief contains no operator location; neither claim had a source. Both statements were removed from the canonical dataset (`ledger/questions.json`), and the generated public page was rebuilt (`pages/questions.html`). The register still says the brief is in English and preserves the independently sourced statement that the Associates country selector lists Japan. No location was substituted or inferred. Q-01 remains open pending the owner’s marketplace/account information.

The retained marketplace facts link to the official Associates Operating Agreement and the three Amazon destination listings in the Q-01 row:

- [Amazon Associates Operating Agreement](https://affiliate-program.amazon.com/help/operating/agreement) — source S01 for the observed country selector.
- [Amazon destination for supplied link 1](https://www.amazon.com/dp/B0CDY277D3) — source S19.
- [Amazon destination for supplied link 2](https://www.amazon.com/dp/B09B7SB46R) — source S20.
- [Amazon destination for supplied link 3](https://www.amazon.com/dp/B08DKYBTPH) — source S21.

## Verification

After rebuilding, the public register and canonical data contain no Osaka/operator-location claim. The Q-01 retained source links are unchanged. All local gates passed:

- `tools/validate_data.py`: 0 errors, 0 warnings; 1,154 internal links checked; 340 ledger rows, 42 sources, 38 flags.
- `tests/test_pipeline.py`: 15/15.
- `tools/audit_site.py`: 116 published pages; fragments, sourced rows, prose counts, namespaces and disclosure all pass.
- `tools/build_site.py --check`: 39 built, 0 drift.
- `tools/build_root_views.py --check`, `tools/build_summary.py --check`, `tools/build_decisions.py --check`, `tools/validate_decisions.py`: all pass; 16 questions remain open and 10 suggestions remain awaiting owner choice.
- `tools/build_marketing.py --check`, marketing verifier, revalidation builder/verifier, research-hub builder/verifier, affiliate-lab verifier, and JavaScript syntax checks: all pass.

**Status:** correction implemented and locally verified. Live deployment confirmation is recorded after the integration PR/deploy.
