# RIMPULSE_PACKETS_BUILD_ANSWERED_NOT_APPLIED

Sources: design/RimMandrake/rimpulse_redesign_2026-10-23.gpt_review.md (lines 6-12, 64) and Transient/away_dashboard_gpt_review_2026-10-08.md (line 13, 75). GPT opinion, ingested under "delegated: GPT assessment ingestion". Owner rulings stand: RimPulse scope picked defects-only plus morning brief (see GPT_CONFLICTS_FOR_OWNER_DIGEST); this item is agent-side data model only, no widget redesign.

## spec
GPT quotes:
- "An idle worker, unfinished preread, and answered card awaiting implementation are agent obligations. Surface them when they threaten an owner commitment, with the agent's recovery plan."
- "Missing lifecycle: preparing -> ready -> opened -> answered -> applied -> verified. Opening is not approval; answering is not implementation. Cards must survive window closure and remain discoverable without arbitrary age cutoffs."
- "Missing evidence: artifact version, recommendation, alternatives, what the decision blocks, deployment versus verification versus loaded-game state, and whether an answer still applies after revision."
- "'Nothing needs you' requires trustworthy coverage. Missing collectors or an unwritten digest mean unknown, not reassurance."
- 10-08 review: "Represent outputs as typed references: repository, commit SHA, relative path, MIME type, availability ..." and "Missing historical signals are unknown, not zero."

Build: a per-card state field with the six states, derived from existing events where possible (answered with no later applied event = agent obligation, listed with age); artifact version + supersession on each card; typed artifact ref (commit-pinned path, MIME, availability). A missing collector or digest renders UNKNOWN, never "nothing needs you".

## verify
- Selftest: a card answered and not applied appears under agent obligations, not owner attention.
- Selftest: collector absent -> headline reads UNKNOWN.
- Selftest: revising an artifact marks earlier answers "may not apply".
- No age cutoff hides an open card.
