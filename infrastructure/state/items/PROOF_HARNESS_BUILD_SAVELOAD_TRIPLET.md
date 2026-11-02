# PROOF_HARNESS_BUILD_SAVELOAD_TRIPLET

Proposed by the daily agent-improvement Curator on 2026-11-01 (`D:\ClaudeWork\rimmandrake\agent_improve\2026-11-01\live-debugging-proof-harness.curator.json`)
from two FOUNDRY lessons:
- `infrastructure/state/lessons/20261101T091226Z-FOUNDRY-sheet-saveload-live-vs-loaded.md`
- `infrastructure/state/lessons/20261101T111824Z-FOUNDRY-save-quantises-tile-temperature-load-ticks.md`

Both lessons record the same failure: a save/load-identical proof compared the live arm with a loaded arm and misread the result. Two vanilla causes:
- Game.LoadGame with Prefs.PauseOnLoad runs one extra DoSingleTick, so the loaded arm is a tick ahead.
- Saving quantises tile temperature.

One save plus one load cannot tell "the save drops state" from "the load is nondeterministic".

Build `saveload_triplet(B, read_state, ticks, tolerance=None)` in `src/RimMandrake/Utils/validation_core.py`:
- one save, three arms: live A, first load B, second load C;
- tick counts aligned by reading Find.TickManager.TicksGame after each load;
- a per-field tolerance map;
- verdict IDENTICAL / SAVE_DROPS_STATE (B==C!=A) / LOAD_NONDETERMINISTIC (B!=C), plus the differing fields.

Then point step 3 of the live-debugging-proof-harness skill at the helper in one line.
## criteria
An offline selftest with a fake bridge covers all three verdicts. One live run on a FOUNDRY save/load proof.
