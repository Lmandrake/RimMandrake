# MAPGEN_NRE_FULL_LIST_20260920_1 — the crash log is a TRIMMED-TIER log, not the full list

## 🔴 the premise was wrong: that process loaded 19 mods, not 618

`Transient/crash_mapgen_20260920T1900.log` line 1338 is RimWorld's own
`Game.InitNewGame()` record of the running mod set (`Verse/Game.cs:495`, read from the
decompiled engine). It names **19 mods**:

```
brrainz.harmony · Ludeon.RimWorld + all five DLC · brrainz.rimbridgeserver
Mlie.StarWarsAnimalCollection · OskarPotocki.VanillaFactionsExpanded.Core
OskarPotocki.VFE.Insectoid2 · sarg.alphaanimals
mandrake.rm.creaturebehaviors · mandrake.rm.environmentalhazards
mandrake.rm.proximityhatch · mandrake.rm.weathersuite · mandrake.rsw.swbestiary
mandrake.rut.ashkarrflora · mandrake.rut.patches
```

That is exactly `modset_builder.py`'s **`desertplants`** tier closure, and the log's three
`[TILEGEN_SILENT_REUSE_1]` tiles — **83745, 83750, 83752** — are the same three tiles
`BIOMEFLORA_PATCH_WIPES_WILDPLANTS_1` used for its live verification. **This log is that
item's own verification session**, preserved and then misattributed.

🔴 **Why the `ModsConfig.xml` reading said 618: the mtime is a restore artifact.**
`modlist_swap` restores by copying the backup back with metadata preserved, so the live
file and `deployed/config/ModsConfig.before-tier-desertplants.xml` are **byte-identical
(md5 `b364fd13…`) and share mtime 08:29** — the 08:29 stamp is the backup's, taken
*before* the swap, not evidence that no swap happened. An unchanged mtime on `ModsConfig`
is not evidence about what a already-running process loaded; only the process's own
`Initializing new game with mods:` / `Loading game from file … with mods:` line is.

## what the NREs actually were — all three, mechanism read from the engine

| fault | mechanism | why the tier caused it |
|---|---|---|
| `WildPlantSpawner.EnoughLowerOrderPlantsNearby` | `wildPlants[i].plant.plant.wildOrder` — the record survives with `plant == null` when its `ThingDef` cross-reference fails | 108 `BiomePlantRecord` cross-refs failed on that load (60 `AB_*`, 19 `RUT_*`, 7 `RG_*`, …) because the donor mods that declare them were not in the 19-mod tier |
| `BiomeDef.CommonalityOfAnimal` → `GenStep_Animals` / `WildAnimalSpawnerTick` | same shape on `wildAnimals`, plus null `PawnGenOption` kinds | same cause; this is the `StatRequest for null def` source that runs to the end of the log |
| `VEF…GenStep_Settlement_ScatterAt_Patch.SettlementGenerationSymbol` | `GenStep_Settlement.ScatterAt` takes `Find.FactionManager.RandomEnemyFaction()` when `map.ParentFaction` is null; that returns **null** in a world with no enemy faction, and VEF's transpiled symbol resolver dereferences the faction | a bridge-generated map on a trimmed-tier world has no parent faction and a near-empty faction roster |

⚠️ **Nothing "died".** `MapGenerator.GenerateContentsIntoMap` catches per-GenStep, and all
three maps generated (`map.uniqueID` 1, 2, 3 in the same log).

## the real production question, MEASURED and clean

**Would any biome entry resolve to null on the owner's ACTUAL list?** No.

1. **On disk** — `selftest_deployed_biome_refs.py`, run 2026-09-20: **480 deployed
   `wildAnimals`/`wildPlants` entries, 0 unresolved** against the 89,613-defName universe
   of Mods + Data + Workshop. PASS.
2. **Against the live ACTIVE list** — every one of those 480 entries checked against the
   defNames declared by the **618 mods active in the live `ModsConfig.xml`**: **0 dangle.**
   Three are correctly stripped by an inactive `MayRequire` and so create no null record:
   `RUT_Staggerseed` and `RUT_Fuzz` (`mandrake.rut.ashkarrflora`) and `RM_Titanoslime`
   (`mandrake.rm.gelatinousslime`). *(The scan under-matches folder→packageId for ~50
   active ids, which can only produce FALSE dangles, never hide one — a zero here is safe
   in the conservative direction.)*
3. **Live, on the running game** — the RimWorld process up at 2026-09-20 21:06 reports
   `Loading game from file CANONICAL_ASHKARR_START_2026-09-12 with mods:` followed by
   **618 mods**, and its `Player.log` carries **0 `BiomePlantRecord` cross-reference
   failures, 0 `StatRequest for null def`, 0 `Error in GenStep`** — 16 cross-reference
   failures in total, against 219 on the tier load.

## ⛔ it is NOT a regression of `FULL_LIST_CANNOT_LOAD_GAME_1`

That item was a deterministic NRE in `new Game()` → `ReadingPolicyDatabase..ctor` →
`GenerateStartingPolicies`, root-caused at `9a2316798` to **FlowWorks' stale DLL** (gizka
exonerated). Different throw site, different cause, and `new Game()` **succeeded** in this
log. Two faults, one superficial resemblance — no ticket merge is owed.

## it was not fixed by the biome-flora work either

`BIOMEFLORA_PATCH_WIPES_WILDPLANTS_1` fixed a real and separate defect (a generated
`PatchOperationReplace` overwriting authored `wildPlants`). It did not cause and did not
cure these NREs: the null entries here are donor plants whose **mods were absent from the
tier**, which no roster reconciliation can affect.

## 🔑 the lesson, which is the only thing owed

**A trimmed tier list produces `GenStep` NREs and unbounded `StatRequest for null def` as
its NORMAL behaviour**, because our BiomeDefs legitimately name ~480 species across mods a
tier does not load, and an unresolved `BiomePlantRecord`/`BiomeAnimalRecord` leaves a
**null-bearing record in the list rather than removing it**. Only `MayRequire` removes an
entry. So:

- ⛔ **Never diagnose a biome/spawner NRE from a tier-list log** without first reading the
  process's own `Initializing new game with mods:` / `Loading game from file … with mods:`
  line. It is the only instrument for what a running process loaded.
- ⛔ **Never infer a running process's mod set from `ModsConfig.xml`** — not its contents
  and *especially* not its mtime, which a restore preserves.
- ✅ When preserving a crash log, copy that mod-list line into the item with it.

## state

**CLOSED — not a defect.** No code or def change was made or is owed; the fault is
confined to a deliberately trimmed tier, and the owner's 618-mod list is measured clean by
three independent instruments including the live game.
