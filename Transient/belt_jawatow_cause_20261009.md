# Jawa return tow: why it never fired (2026-10-09, offline trace; fix landed 3f5ad1125)

## Root cause: two defects, one in the test and one in the code
1. TEST: `IncidentWorker.CanFireNow` caches its result per worker per game tick (`lastCheckCanRunTick == TicksGame` returns
   `lastCanRunResult` before `CanFireNowSub`, forced calls included). Sitting 3 (`Transient/belt_acc3_tow3/4/5_20261009.py`)
   evaluated once after entry with 7 ChunkSlagSteel still in the rect (legitimately false), destroyed them, then re-asked
   WITHOUT advancing a tick, so every later dry run (plain, forced, toggle off) replayed that false. Likely also why the
   Stampede answers looked like they ignored the gates.
2. CODE: `IncidentWorker_RM_HullTow.TryExecuteWorker` (RM_ShadeExtras.cs) generated `PawnGroupKindDefOf.Peaceful`, but 7 of 8
   `RUT_Jawa_*` FactionDefs (all but IndigenousTribes) declare no Peaceful pawnGroupMaker, so GeneratePawns gave nobody and the
   worker returned false (the "forced fire = fired False"). Fix: `RM_LongShadeKernel.ClanGroupChoice` (Peaceful, else Combat,
   else none) and `FindClan` skips factions with neither.

## False theories ruled out by reading
- OnLongShade: `world_tile_map_generate biome=` sets the tile PrimaryBiome first, so map.Biome is RM_LongShade.
- Map_PlayerHome, earliestDay, allowedBiomes, minRefireDays: all skipped when `parms.forced`.
- Kernel HullLooted/InHullRect and the hull-rect arithmetic match the fuzz definitions.
- Faction hostility/hidden: all permanentEnemy/naturalEnemy false, none hidden.
- Not measured: the entry cell (RCellFinder) and corpses counting as loose items (Corpse is an EverHaulable Item).

## Also found, not changed
`src/RimMandrake/LongShade/validation.py` STATIC fails: it demands `MayRequire mandrake.rm.longshade` on RUT_JawaReturnTow but
the def says `mandrake.rm.biomes`. Needs a ruling on which package carries the worker; the def loaded in sitting 3 so biomes is active.
`run_selftests.py`: 344/348 pass, the one FAIL is selftest_utinnipatches_dump.py (untouched by this change).

Scene for the next sitting: see `## verify` of LONGSHADE_JAWATOW_LIVECHECK_1 (S.run(5) before every dry run).
