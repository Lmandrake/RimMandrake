# LONGSHADE_MIDDENS_DESIGN_1 build — 2026-10-06 (uncommitted, offline)

## Item + design read
Ruled 2026-10-03: heap that regrows over weeks, re-searchable; vanilla items only; the clean-patch
tell is purely visible on the ground; the vrekka builds the heaps, and killing it stops regrowth.
Design: `design/Jawa/worldbuilding/biomes/long_shade_bedazzle_2026-09-27.md` §4.4.

## Precedent sweep
- Shape copied from SWBestiary scrap nest (`RSW_ScrapNest.xml`, `CompScrapHoarder.cs`,
  `JobGiver_HoardScrap.cs`): BuildingNaturalBase heap, a giver inserted at Animal_PreMain, built by direct spawn.
- Search copied from Scarlands `WorkGiver_DefuseOrdnance` and the Command_Toggle in `RM_ReactionPools.cs`.
- LongShade ALREADY had a settings screen (scrolls, maxOneColumn); the new toggles were added to it.

## Built
- `src/RimMandrake/LongShade/Source/RM_LongShadeMiddens.cs`: heap comp (layers, tend, search loot,
  inspect string, "Search midden" toggle), vrekka JobGiver (builds a heap in shade ≥0.5, unroofed,
  outside the home area; tends one on a half-day cooldown), tend/search JobDrivers, WorkGiver (Mining).
- `src/RimMandrake/LongShade/Defs/ThingDefs_Buildings/RM_LongShade_Middens.xml`: RM_LongShadeMidden,
  2 JobDefs, WorkGiverDef RM_SearchMidden, ThinkTreeDef RM_VrekkaMiddenInsert. All numbers are PROVISIONAL.
- Settings: middenVrekkaBuildEnabled, middenRegrowthEnabled (in `RM_LongShadeMod.cs`); csproj Compile line added.
- validation.py: midden_problems() static chain (mutant probe caught a broken Tend()).

## Validation
- winbuild LongShade: 0 warnings, 0 errors (srchash stamped +dirty, so rebuild after commit).
- validate_patch: 0 errors, 1 warning (vanilla texPath ChunkSlag, which RimSage confirms on ChunkSlagSteel).
- validation.py STATIC: FAIL on 5 roster findings that were already there before this change
  (RM_Vosska, RM_Ommok, RM_Ulgga, RM_TruffleMole, RM_UltrissPad, from the Fillers publish); midden chain finds 0.

## Art owed
- Midden heap sprite: none in artpipe (only the Wasteland middenshell family). Placeholder is
  vanilla slag chunks, tinted. Ideally per-layer art (empty → full).

## Deferred / open questions
- Mapgen seeding of old heaps on the lee of big rocks (§4.4). Not ruled. Right now a heap exists only after a vrekka builds it.
- Clean-patch visible tell (mirrak/sarlacc patch kept unnaturally clean). Not built.
- "Drive them off": vrekka leaving the map stops regrowth; nothing forces flight.
- Live proof is owed: a quicktest on a Long Shade map with vrekka.
