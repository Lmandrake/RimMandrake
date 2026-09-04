# Expected-failure signatures — code-review deploy batch, written 2026-09-04 BEFORE launch (FOUNDRY)

Supersedes the prior (2026-09-02, BENCH) entry — that load already happened and
completed; this is a fresh, much smaller batch riding the next restart.

Deploy batch: 4 assemblies, each a small isolated fix from this session's standing
code-review sweep (`DIRTY_CODE_REVIEW_LOOP_RESTART_6`), each in a different mod DLL
so they cannot blame each other. All four already build clean at 0 warnings/errors
offline; this load only proves the live deploy + runtime behavior.

| assembly | fix | expected signature |
|---|---|---|
| RimMandrakeGraffiti.dll | `ModExtension_Graffiti` startup validator gained a third mis-wire check (`viewerReactionThought`/`workerClass`) — commit `1e4fe0eb` | ABSENT: no new `Log.Error` naming `ModExtension_Graffiti` or `viewerReactionThought` (no shipped mark is actually mis-wired, so the new check should log nothing) |
| RimMandrakeVisibility.dll | `GameComponent_ColonyVisibility.tileMemory` rekeyed `Dictionary<int,...>` → `Dictionary<PlanetTile,...>` — commit `8a24dcd7` | RESIDUAL RISK: this changes the Scribe shape for a field written by prior saves under the OLD (int) key. Watch for any exception naming `tileMemory`, `GameComponent_ColonyVisibility`, or a Scribe parse error near "ColonyVisibility" on load. Best case: old entries silently fail to parse per-entry and the dict starts empty (acceptable — it's ephemeral decay memory, not save-critical state, matches the file's own doc). Worst case (should NOT happen, flag loudly if seen): a hard exception that aborts the whole save load. |
| RimMandrakeStructureInjections.dll | dead `RimplacePlan.DefNames()` + unused `System.Linq` deleted — commit `5d44b598` | ABSENT: zero behavior change, nothing should differ in the log at all |
| JawaArmoury.dll | `Patch_JobGiver_AIFightEnemy`'s ranged-branch transpiler injection point fixed (was emitting invalid IL mid-expression) — commit `12ad4c44` | ABSENT (this is the important one): `InvalidProgramException` naming `JobGiver_AIFightEnemy` or `TryGiveJob`. Pre-fix, this would have thrown the first time ANY hostile pawn's ranged-combat AI reached this JobGiver — a prior grep of the live log this session found zero hits, meaning either the path was never exercised yet or (less likely) the exception manifests differently; either way, absence post-fix plus normal-looking raids is the pass condition. |

General sweep: run `harvest_log.py` as usual after this load — dead mods, discarded
defs, unresolved cross-refs, stale Scribe references, patch no-ops — same as any
other restart, not specific to this batch.
