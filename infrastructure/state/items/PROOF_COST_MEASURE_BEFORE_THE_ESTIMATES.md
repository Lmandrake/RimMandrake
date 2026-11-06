# PROOF_COST_MEASURE_BEFORE_THE_ESTIMATES — proof cost ledger + live-throughput benchmark

Fast-testing #8 (`design/RimMandrake/fast_testing_2026-11-05/scored.md` §ranked, rank 8). Owner 2026-11-06: "yes and expedite".
Every speed claim in that doc is INFERRED; this is the instrument that settles them. Build it before trusting #2-#7.

## spec
- One append-only record per live proof run (Relentless game_prove round, broker clause, testq job): item/clause, sha,
  mod tier, wall time split into queue wait, bridge-held staging, bridge-held proving, idle-while-held; LLM tokens
  spent; verdict (PASS/FAIL/UNMEASURED). Written by the code that runs the proof, not reconstructed later.
- A `throughput` report: measured rows/hour (PASS+FAIL), bridge-driven share of held time (reuse
  `src/RimMandrake/Utils/northstar_driver/bridge_utilization.py`), staging minutes p50/p95, tokens per measured row,
  over a chosen window; exposed in `relentless.py reading`.
- A controlled ticks/s benchmark: minimal list vs full list, empty vs busy map (60-280 ticks/s is the only figure on file).

## verify
- A selftest feeds synthetic runs and checks the report's arithmetic, including a 0-run window reading UNMEASURED, not 0.
- After one real day, the report reproduces today's baseline (Relentless ~2.7 measured rows/hour; bridge driven 5-10%
  of held time) within reason, or explains the gap.
