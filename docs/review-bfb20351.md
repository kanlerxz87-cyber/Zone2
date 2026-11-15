# Review note — session `bfb20351`

**Status:** in progress. This note tracks a narrow accuracy correction discovered during the requested repository and live-site review.

**Scope:** `ledger/questions.json` (canonical question data), generated `pages/questions.html`, `COORDINATION.md` (append-only claim and audit record), and this review note. No product facts, marketing copy, navigation, or another session's files are in scope.

## Finding

The published Q-01 entry says, “The operator location in the brief is Osaka, Japan.” The user brief does not state an operator location. That sentence is unsupported and conflicts with the session context available to this agent; no personal location is needed to answer the marketplace question. Remove the sentence rather than substitute another location. Keep the independently sourced fact that the Associates country selector lists Japan, cited to S01, and keep the marketplace/account question open.

**Review state:** pending canonical-data correction, regeneration, gates, PR, and deployment verification.
