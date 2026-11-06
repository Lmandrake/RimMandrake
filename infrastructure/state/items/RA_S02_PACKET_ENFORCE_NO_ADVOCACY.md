# RA_S02_PACKET_ENFORCE_NO_ADVOCACY

Relentless Agent build, step 2. Design: `design/RimMandrake/relentless_agent_design_2026-11-01.md` section 13, ruling section 14. Contract: `MandrakeWorkflows/relentless/agent/RELENTLESS_AGENT.md`.

## step

Packet schema and lint, report-only

## verify

Planted contaminated packets rejected; 48 real ones scored by hand for false rejects

Order is measure, wall, change: a step does not start before the step it is blocked on lands. New rules run report-only first. State the narrow thing the proof shows.

## state, 2026-11-01

Schema and word lint: `src/RimMandrake/rimflow/relentless_packet.py`, report-only, journal `packet_report` on each receipt. 14 planted packets refused by `selftest_relentless_packet.py`. Real set: 121 finish receipts, not 48, `relentless_packet.py scan`, rows at `D:\ClaudeWork\rimmandrake\relentless_agent\packet_scan.json`. 15 hit after dropping `attempts`, which false-rejected "Steve attempts". Those 15 were read by hand: all are history or reasons; 2 ("DIRTY before this change") are plain facts in history words, so a floor of 2 false rejects of 121. The other 106 were not read, so misses are unmeasured. Still owed: Build authoring the packet at finish, the Marker reading it instead of evidence prose, `packet_reject_limit`, and the rejects going live.

## measured, 2026-11-06
The 48 hand-scored rows are committed: `src/RimMandrake/rimflow/testdata/relentless_packet_handscored.json` (counting rule inside), re-linted by `selftest_relentless_packet.py`. Store then: 1653 unique receipts, 165 hits. Seeded sample of 24 hits and 24 non-hits: **6 of 24 hits are false rejects** (review-state "before this change/edit" ×2, "not retried" as the behaviour under test, "prior" naming a file version, the `--because` CLI flag, "because" explaining tool behaviour) and **6 of 24 non-hits are misses** (mostly "checker's", which "the checker" never matches; "Gen-1" escapes `gen \d+`). Report-only lint, word list unchanged. Before rejects go live, the word list needs these fixes, and then a re-score.
