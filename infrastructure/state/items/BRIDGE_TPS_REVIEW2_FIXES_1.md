# BRIDGE_TPS_REVIEW2_FIXES_1 — repair build 2 of the TPS record per the second GPT review

## spec
Source of truth: Transient/foundry_tps_review_gpt2_20261010.md (35 numbered findings A, scenarios B, section F ranked table:
MUST 1-17, SHOULD 1-7). Read it whole; each finding names file+symbol and its failure scenario. Verdict: build 2 is not ready
to trust. MUST 1 (duplicate `kind` key on incidents) was already fixed in a119858e4 — verify, don't redo.
Fix every MUST as code plus a selftest that fails before the fix (trace-based for the accumulator/profiler boundaries,
fault-injection for the writer, multi-session fixtures for the reader). SHOULD items 1,3,5,6,7 where cheap; SKIP items stay skipped.
Do not trust the previous progress log's "Done" marks; GPT found runtime defects behind them.

## criteria
- C1 (L0) each MUST 1-16 has a selftest that failed on build 2 and passes now.
- C2 (L0) acceptance criteria text in BRIDGE_TPS_CAPTURE_FIXES_1 and tps_record.md updated so C3/C4 cannot pass with these defects (GPT section E).
- C3 (L2) the controlled interruption matrix (GPT section E items 1-3) passes on the minimal list; results in a Transient report.
- C4 (L3) full ~600-mod-list overhead + autostart + overnight reconstruction measured: MUST 17, needs a cold load covering the group.

## verify
`tps_record.py --at` for a deliberately induced 90 s stall returns it as an incident with correct local time, game id and duration.
