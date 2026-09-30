# DEEPFIRE_LIVE_FAILURES_1 — report

Offline fixes for the failures seen in the 2026-09-30 live proofs
(`Transient/deepfire_live_2026-09-30/`).

## 1. Double-destroy of RM_DeepfireLightProxy

**Where:** `Player.log` lines 21968-9 and 22290-1. Both pairs sit right after a proof's
`cleanup` line and before the next proof's first action, which is when the status proof's
`jawa/make_empty_room` and similar calls clear the area where earlier proofs left a
coated wall or sculpture.

**Root cause:** our own destroys are all guarded by `!Destroyed`. The second destroy comes from
the caller. `jawa/clear_area`/`make_empty_room` call vanilla `GenDebug.ClearArea`, which takes
**`GetThingList(map).ToList()` per cell** and then calls `Destroy()` on each thing in it.
A coated 1x1 building shares its cell with its cluster proxy, because a one-member
cluster anchors on the building's own cell. So the building's `Destroy` runs
`CompDeepfire.PostDeSpawn`, then `DeregisterClusteredThing`, `RebuildBlock` and `RemoveLight`,
and that destroys the proxy. `ClearArea` then reaches the proxy in its stale snapshot and destroys
it a second time. Vanilla `Thing.Destroy` logs the error on an already-destroyed thing
(RimSage `Verse/Thing.cs`). Any code that destroys from a cell snapshot hits the same thing.

**Fix (the proxy itself):** both proxy defs now use `thingClass`
`RimMandrake.LuminousPigment.DeepfireLightProxy`. Its `Destroy` returns immediately when the
proxy is already `Destroyed`. The component owns the proxy's lifetime, so a second destroy from
someone else's stale list has nothing left to do. The entry-table guards stay as they were.

## 2. Worn glow: walk + AimOnTargetChance pairs

Neither failure was in the mod code. **Both were in the proof's expectation or its fixture.**

- **Pairs (18/20).** The x1.25 target-size factor was applied in every row: at equal body size,
  coated/plain = 0.509/0.4072 = 1.25 exactly. The other rows differ only by the twin's body size:
  0.3258 = 0.4072 x 0.8. Vanilla `factorFromTargetSize = Clamp(BodySize, 0.5, 2)` (RimSage
  `Verse/ShotReport.cs`). The twins were random `Colonist` pawns, and on this mod list some have
  body size 0.8 (the log shows "bodysizes genes are active"). So a small coated twin next to a normal
  plain twin loses, and that happened in 2 of 20 pairs.
  **Fix (fixture):** the proof pawns are generated as baseliner adults. The tally compares aim per
  unit of each twin's own clamped body size. Each row now reports `coatedSize`, `plainSize` and
  `coatedSizeFactor` (the patched struct field, read directly), and a failure prints the
  offending rows.
- **Walk (7 samples, 30 cells).** The walker did the whole walk, and every sample was good
  (`0 bad`). The `>= 10 samples` bar assumed about 13 ticks per cell (26 polls for 30 cells). Live, it
  finished in 7 polls (about 100 ticks). **I have not explained that speed.** `moveSpeed` and the
  (tick, x) of each sample are now in the report, so the rerun will show it.
  **Fix (proof):** the bar is now `>= 25 cells travelled AND proxy seen at >= 5 distinct cells`,
  which is the property the check was meant to test. The contaminated first run
  (80 samples, 0 cells) would still fail it.

## 3. Status thoughts: opinion offset + visitor impress NRE

- **Opinion -15 read `{}` (code in the report, not the thought).** `RM_WearsAboveStation` was
  active by its own worker (`aboveStationActive` PASS). The report reads the live social list through
  `SituationalThoughtHandler.AppendSocialThoughts`, which caches per other-pawn and only
  recalculates 100 ticks after the last recalculation (RimSage
  `RimWorld/SituationalThoughtHandler.cs`). The proof calls the report several times in one tick,
  so the read after the commoner was dressed got the empty cache the earlier read had built.
  In play the game recalculates on that 100-tick cadence, which is correct.
  **Fix:** `BuildPairReport` calls `Notify_SituationalThoughtsDirty()` on both pawns before reading.
- **Visitor NRE (debug action bug).** The Empire `FactionDef` has **no `basicMemberKind`**
  (RimSage def dump, pawnGroupMakers only). `PickVisitorFaction` returned the Empire without
  checking that, so `PawnGenerator.GeneratePawn(null, empire)` threw. The fallback loop already
  checked it; the Empire branch did not.
  **Fix:** every candidate faction must come with a humanlike kind: `basicMemberKind`, or else
  `Faction.RandomPawnKind()` (its humanlike pawnGroupMaker options). A faction with neither is
  skipped. The visitor is generated as an adult.
- Also: the re-spawn paths (`SpawnPair`, `SpawnWalker`, `StylingSetup`, `VisitorImpress`) no longer
  call `Destroy()` on a pawn that is already destroyed, for example after a map regen between runs.

## 4. Proof error checks

**Root cause:** `jawa/drain_log` does **not** drain. It returns the newest entries of the game's
1000-entry `Log.Messages` buffer, and `errorsOnly` still includes Warnings (JawaBench
`JawaBenchTerrainTools.cs`). The opening "discard" call discarded nothing. The closing check
substring-matched the whole JSON for "Deepfire". So any Deepfire-named Warning, or any earlier
proof's error still in the buffer, failed every proof.
**Fix:** a new shared helper, `src/RimMandrake/bridgetools/deepfire_log_check.py`. It takes a
baseline of Error-type counts at the start. At the end it keeps only **Error**-type lines whose text
matches `Deepfire|LuminousPigment|Luminous|WornGlow|FirstCoat|Sumptuary` (god deltas adds
`Ninefold`) and that are new or have repeated since the baseline. Our `[Deepfire*]` info lines are
Message-type and never count. All six `prove_deepfire_*.py` use it.

## Verification

- The `dotnet build` of `RM_LuminousPigment.csproj` is clean (0 warnings, 0 errors). The DLL and
  `.srchash` are committed together.
- All six proofs pass `py_compile`.
- `run_selftests.py`: 77 of 79 passed, 2 skipped, 1 unmeasured, and 1 failed:
  `selftest_deployed_biome_refs.py`. It reports 19 RUT_ biome references that dangle in the
  **deployed game Mods folder**. That is game-folder state and has nothing to do with this change,
  which touches no biome and deploys nothing.
- Nothing is proven live yet. The game was not touched.

## Proofs to rerun

Deploy LuminousPigment, then rerun on fresh maps (`regen_current_map.py` between them):
`prove_deepfire_worn_glow.py`, `prove_deepfire_status_thoughts.py`, then `prove_deepfire_floor.py`,
`prove_deepfire_firstcoat.py`, `prove_deepfire_proxy_storage.py` and `prove_deepfire_god_deltas.py`.
The last four only for the new log check and the proxy thingClass. Run them back to back on one
map at least once. That sequence is what produced the double destroy, and after this fix it
should leave no `already-destroyed` line in `Player.log`.
