# MAPGEN_NRE_FULL_LIST_20260920_1 — map generation died on the full list

## what happened, and what is NOT claimed

2026-09-20 ~19:00 local, on the full **618**-mod list (MEASURED by parsing `ModsConfig.xml`;
mtime 08:29 that morning, so **no list swap was involved**). A RimWorld process reached the
bridge (`GABP server running standalone`, log line 1098), then **generated a map and died**.

Log preserved: `Transient/crash_mapgen_20260920T1900.log` (175,999 bytes).

⚠️ **BENCH did not drive this session and does not know what triggered it.** The cause is
**UNMEASURED**. What follows is evidence, not a diagnosis.

## the evidence, in order

```
[TILEGEN_SILENT_REUSE_1] call #1 thread=1 requesting tile=83745,0 BEFORE GetOrGenerateMap
Error in GenStep: System.NullReferenceException  [Ref 77860930]
  VEF.Factions.VanillaExpandedFramework_GenStep_Settlement_ScatterAt_Patch.SettlementGenerationSymbol
  RimWorld.GenStep_Settlement.ScatterAt
Error in GenStep: System.NullReferenceException  [Ref 9EFD084]
  RimWorld.WildPlantSpawner.EnoughLowerOrderPlantsNearby
  RimWorld.WildPlantSpawner.CalculatePlantsWhichCanGrowAt
  RimWorld.GenStep_Plants.Generate
StatRequest for null def.        <- then unbounded, to the end of the log
```

and later, once a map was ticking:

```
RimWorld.WildAnimalSpawner.get_DesiredAnimalDensity
  - POSTFIX com.alphaanimals: AlphaAnimals_MapTemperature_SeasonAcceptableFor_Patch:AllowAnimalSpawns
  - POSTFIX VFEInsectoidsMod: WildAnimalSpawner_DesiredAnimalDensity_Patch:Postfix
RimWorld.WildAnimalSpawner.WildAnimalSpawnerTick → Verse.Map.MapPostTick
```

🔑 **Two independent spawners — plants and animals — both fault on a NULL def.** That is the
signature of a biome roster holding an entry that resolves to nothing, not of one bad mod.

## 🔴 it is the same shape as an item that is CLOSED

`FULL_LIST_CANNOT_LOAD_GAME_1` — *"Full 635-mod list throws a deterministic NRE in
`new Game()` — no save loads, no map generates"* — was **closed at `9a2316798`**.
⇒ Either this is a regression of that, or a second defect wearing its face. **Check that
item before assuming it is new**, and if it has regressed, say so there rather than
carrying two tickets for one fault.

## one hypothesis, TESTED AND DISCONFIRMED — do not re-run it

`OUR_MODS_DEPLOYED_NEVER_ACTIVATED_1` found `mandrake.rut.ashkarrflora` deployed but
**inactive**, which would make any unguarded reference to its plants resolve to null — an
exact fit for the `GenStep_Plants` fault.

❌ **It is not the cause.** MEASURED against the DEPLOYED copy: `Mods/AshkarrFlora` ships
exactly **one** def (`RUT_SweetlineTree`), and there are **zero** references to it in any
deployed `UtinniPatches` biome def or patch. The repo holds more (`RUT_Staggerseed`,
`RUT_Fuzz`) but they are **not deployed**, so the running game never saw them.

## spec

Find which biome roster carries the null entry. The two spawners give the search its shape:
whatever it is, it is in a list both `WildPlantSpawner` and `WildAnimalSpawner` walk.
⚠️ Check the **deployed** defs under `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\`,
not the repo — writing a file is not deploying it, and this fault is about what the game
actually loaded.

## verify

A map generates on the full 618-mod list with no `GenStep` NRE and no `StatRequest for
null def`.
