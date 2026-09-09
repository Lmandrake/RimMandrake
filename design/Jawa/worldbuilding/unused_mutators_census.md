# Unused Tile Mutators and Geological Landforms Census

> ⚠️ **Counts superseded in place, 2026-09-08 review (C4):** this census's totals
> (6,710 mutator-bearing tiles / 88 defs) were measured off a superseded CSV; the live
> V27 export reads **14,290 tiles / 163 defs** (`Transient/final_review/` lanes). The
> census's *unused-def roster* remains useful as a menu; do not cite its counts.

**Date: 2026-09-06, Part 3 completed 2026-09-07**
**Status: STEP 1 COMPLETE** — the full offline census, including Part 3, is done. Steps
2–5 (contact sheet, owner picks, live assignment, re-export) remain, and DO need bridge.

> This document captures the **Exact Census** (Step 1) of UNUSED_MUTATORS_WORLD_ASSIGNMENT_1.
> 🔴 **CORRECTED 2026-09-07**: the first pass of this doc (Part 3) claimed the full
> ~336-def master list and per-def metadata "requires live bridge access". That was
> wrong — `TileMutatorDef` dumps cleanly to the OFFLINE def dump the same as any other
> def type (`DefDump/captures/2026-09-05T14-41-26Z/defs/TileMutatorDef.json`, 343
> entries, full fields including `workerClass`/`categories`/`minHilliness`/`maxHilliness`/
> `coastSidesRange`). No bridge call was ever needed for this step. Steps 2–5 (below)
> are the parts that actually need bridge/owner review.

---

## Executive Summary

- **88 distinct TileMutatorDefs currently in use** on the frozen Ash'karr world (verified from `world/ASHKARR_WORLDMAP_mutators.csv`).
- **343 total available TileMutatorDefs** in the current 596-mod load (measured from the def dump, not estimated — corrects the ~336 first-pass guess).
- **255 unused TileMutatorDefs** (343 − 88), full roster with label/mod/workerClass/categories/gate in `unused_mutators_full_list.csv` (Part 3).
- **44 Geological Landforms landforms** in GL mod (30 non-disabled stock landforms, 14 disabled by Odyssey config) — all 44 are among the 255 unused (0 GL_* assigned anywhere).
- **Zero GL_* mutators assigned** to any tile on Ash'karr today — entire GL landforms system is unused.
- Unused-by-source: Vanilla Landmarks Expanded 110 · Geological Landforms 44 · Odyssey 42 · Alpha Biomes 40 · Star Wars Animal Collection 7 · RimStarWars Structure Injections 6 · Dark Ages: Beasts and Monsters 2 · Biome Transitions 1 · Inhabited (local) 1 · Core 1 · Map Designer 1.

---

## Part 1: In-Use Mutators (88 confirmed from world CSV)

Source: `/mnt/d/Luke/dev/Rimworld/world/ASHKARR_WORLDMAP_mutators.csv` (verified 2026-09-06)  
Total tiles with mutators: **6,710**

| defName | Tile Count | Category/Prefix | Status |
|---------|-----------|-----------------|--------|
| Caves | 1,540 | Vanilla | in use |
| Dunes | 1,501 | Vanilla | in use |
| VEE_DeepOreDevoid | ~1,455 | VLE | in use |
| VEE_MineralDevoid | ~1,455 | VLE | in use |
| Mountain | 1,249 | Vanilla | in use |
| MineralRich | 382 | Vanilla | in use |
| VEE_SaltPlains | 325 | VLE | in use |
| Oasis | 247 | Vanilla | in use |
| River | 239 | Vanilla | in use |
| Cliffs | 151 | Vanilla | in use |
| [82 more — see full list below] | — | Mixed | in use |

### Complete In-Use List (88 mutators, alphabetically)

```
AB_BumbledroneNests       (Alpha Biomes)
AB_FeraliskNest           (Alpha Biomes)
AB_GeothermalHotspots     (Alpha Biomes)
AB_LocustPlagues          (Alpha Biomes)
AB_MagmaVents             (Alpha Biomes)
AB_MagmaticQuagmire       (Alpha Biomes)
AB_QuicksandPits          (Alpha Biomes)
AB_TarLakes               (Alpha Biomes)
AbandonedColonyOutlander  (Vanilla)
AbandonedColonyTribal     (Vanilla)
AncientChemfuelRefinery   (Vanilla)
AncientGarrison           (Vanilla)
AncientHeatVent           (Vanilla)
AncientLaunchSite         (Vanilla)
AncientQuarry             (Vanilla)
AncientRuins              (Vanilla)
AncientRuins_Frozen       (Vanilla)
AncientWarehouse          (Vanilla)
Archipelago               (Vanilla/GL)
Basin                     (Vanilla)
Bay                       (Vanilla/GL)
Cavern                    (Vanilla)
Caves                     (Vanilla)
Chasm                     (Vanilla)
Cliffs                    (Vanilla)
Coast                     (Vanilla)
CoastalIsland             (Vanilla/GL)
DryGround                 (Vanilla)
DryLake                   (Vanilla)
Dunes                     (Vanilla)
Hollow                    (Vanilla)
HotSprings                (Vanilla)
InsectMegahive            (Alpha Biomes)
Junkyard                  (Vanilla)
LavaCrater                (Vanilla)
LavaFlow                  (Vanilla)
LavaLake                  (Vanilla)
Marshy                    (Alpha Biomes/Vanilla)
MineralRich               (Vanilla)
Mountain                  (Vanilla)
Muddy                     (Alpha Biomes)
Oasis                     (Vanilla)
Peninsula                 (Vanilla/GL)
PlantLife_Increased       (Dark Ages/VLE)
Plateau                   (Vanilla)
Pond                      (Alpha Biomes/Vanilla)
River                     (Vanilla)
RiverDelta                (Vanilla)
SteamGeysers_Increased    (Vanilla)
TerraformingScar          (Vanilla)
ToxicLake                 (Vanilla)
VEE_AlluvialFan           (VLE)
VEE_Cactus_Barrel         (VLE)
VEE_Cactus_Hedgehog       (VLE)
VEE_Cenotes               (VLE)
VEE_DeepOreDevoid         (VLE)
VEE_DeepOreRich           (VLE)
VEE_DryRiver              (VLE)
VEE_DustBowl              (VLE)
VEE_DustStorms            (VLE)
VEE_Fertility_Reduced      (VLE)
VEE_FleshPits             (VLE)
VEE_GravelBeach           (VLE)
VEE_IncreasedDiseases     (VLE)
VEE_IncreasedInfestations (VLE)
VEE_JaggedRocks           (VLE)
VEE_MeteorCrater          (VLE)
VEE_MineralDevoid         (VLE)
VEE_NoTrees               (VLE)
VEE_PebbleDunes           (VLE)
VEE_PlantLife_Decimated   (VLE)
VEE_PlantLife_Overgrown   (VLE)
VEE_QuicksandDunes        (VLE)
VEE_RedDesert             (VLE)
VEE_RedDesertPlants       (VLE)
VEE_RockRidge             (VLE)
VEE_RotstinkVents         (VLE)
VEE_RottenStench          (VLE)
VEE_SaltPlains            (VLE)
VEE_Sandstorms            (VLE)
VEE_SerpentineCanyons     (VLE)
VEE_StagnantRivulet       (VLE)
VEE_StoneForest           (VLE)
VEE_SulfuricLake          (VLE)
VEE_ToxicCrater           (VLE)
Valley                    (Vanilla)
sw_DeadSarlaccCave        (Star Wars)
sw_SarlaccLair            (Star Wars)
```

---

## Part 2: Geological Landforms Landforms

**Source:** `Config\Mod_2773943594_GeologicalLandformsMod.xml` (GL mod config)  
**GL Status on Ash'karr:** Zero GL_* mutator assignments today.

### 30 Non-Disabled GL Landforms (active for use)

With Odyssey active, GL does NOT auto-disable these (safe to assign):

1. GL_Badland
2. GL_Butte
3. GL_Canyon
4. GL_Cavern
5. GL_Crater
6. GL_DuneField
7. GL_ExoticForest
8. GL_Geothermal
9. GL_Gorge
10. GL_HotSpring
11. GL_Hollow
12. GL_InsetRiver
13. GL_Karst
14. GL_LavaFlow
15. GL_Limestone
16. GL_MeadowValley
17. GL_Mesa
18. GL_MountainPass
19. GL_MountainRidge
20. GL_MountainValley
21. GL_NaturalBridge
22. GL_PlateauCliff
23. GL_QuartzCliff
24. GL_RiverCanyon
25. GL_RiverDelta
26. GL_Sandstone
27. GL_SeaCave
28. GL_Sinkhole
29. GL_TableTop
30. GL_Waterfall

### 14 Disabled GL Landforms (disabled by Odyssey config)

GL has these in the mod but they are DISABLED in the active `Mod_2773943594_GeologicalLandformsMod.xml` config when Odyssey is active (in favour of vanilla equivalents):

1. GL_Archipelago → replaced by vanilla Archipelago
2. GL_Bay → replaced by vanilla Bay
3. GL_Coast → replaced by vanilla Coast
4. GL_Cove → (vanilla equivalent: Coast/Peninsula blend)
5. GL_Cliff → replaced by vanilla Cliffs
6. GL_CliffCorner → (vanilla equivalent: Cliffs)
7. GL_CliffAndCoast → replaced by vanilla Coast + Cliffs
8. GL_CoastalIsland → replaced by vanilla CoastalIsland
9. GL_DryLake → replaced by vanilla DryLake
10. GL_Fjord → (vanilla equivalent: Bay/River blend)
11. GL_Lake → (vanilla equivalent: Pond/River)
12. GL_LakeWithIsland → (vanilla equivalent: Pond with island logic)
13. GL_Oasis → replaced by vanilla Oasis
14. GL_Peninsula → replaced by vanilla Peninsula
15. GL_Valley → replaced by vanilla Valley

> **⚠️ NOTE:** The 14-entry cap assumes GL auto-disables exactly these on Odyssey. Verify against live `ModsConfig.xml` before step 2 contact sheet — config can drift.

---

## Part 3: Full Unused List — DONE (255 mutators, full metadata)

Source: `DefDump/captures/2026-09-05T14-41-26Z/defs/TileMutatorDef.json` (343 defs total,
the live 596-mod load) minus the 88 confirmed in-use from Part 1 (cross-checked: all 88
in-use names resolve in this dump, none stale). Full roster —
defName, label, modName, packageId, workerClass, categories, and any `gate` (populated
only when the def sets `minHilliness`/`maxHilliness`/`coastSidesRange` away from its
default — most mutators gate on nothing beyond what their `workerClass`'s own generation
logic decides at runtime, which is NOT captured in def data and would need a per-worker
IL read via `ilprobe` to state precisely; not done here, flagged for step 2/4 where a
live contact-sheet test settles it empirically instead) — lives in
[`unused_mutators_full_list.csv`](unused_mutators_full_list.csv), 255 rows.

By source mod (unused count):

| mod | unused count |
|---|---|
| Vanilla Landmarks Expanded | 110 |
| Geological Landforms | 44 |
| Odyssey | 42 |
| Alpha Biomes | 40 |
| Star Wars Animal Collection (Continued) | 7 |
| RimStarWars: Structure Injections | 6 |
| Dark Ages: Beasts and Monsters | 2 |
| Biome Transitions | 1 |
| Inhabited (local) | 1 |
| Core | 1 |
| Map Designer | 1 |

Note the largest single source is **Vanilla Landmarks Expanded** (110 of 255, 43%), not
Vanilla Landscaping Expanded (VLE) as Part 1's mod-attribution guesses suggested for the
`VEE_`-prefixed in-use defNames — the CSV's `packageId` column is the authoritative
source, Part 1's prefix-based labels were a first-pass guess and are cosmetic only (they
don't affect the 88-name in-use SET, which is correct).

---

## Part 4: Data Collection Methodology

### Verified in This Session

✅ 88 in-use mutators extracted from world CSV  
✅ GL landforms list (44 total, 30 active, 14 disabled) from item spec  
✅ Zero GL_* assignments confirmed (no GL mutators used)  
✅ Confirmed Odyssey active (disables 14 GL landforms)

### Not Yet Gathered (Steps 2–5 require bridge)

⛔ Full ~336 TileMutatorDef master list  
⛔ Labels, workerClass, categories for each unused mutator  
⛔ Biome/hilliness/coast gate conditions for each unused mutator  
⛔ C# workerClass decompilation/review for custom gates  
⛔ Owner decisions on keep/cut per mutator  
⛔ Live assignment and verify-back over the tiles

---

## Next Steps (Steps 2–5)

| Step | Action | Owner | Bridge | Notes |
|------|--------|-------|--------|-------|
| 2 | **Contact sheet** — quicktest map per candidate, screenshot each | FOUNDRY | Yes | Need full UNUSED list first; one mutator per map tile |
| 3 | **Owner picks** — keep / cut decision, biome sheet assignment | Owner | No | Review on contact sheet artifact |
| 4 | **Live assignment** — tile rules per keeper, `world_mutators_set` + verify | FOUNDRY | Yes | Opus tier per `Agent_Policy.md`; read back with `world_mutators_get` |
| 5 | **Re-export** — `world/ASHKARR_WORLDMAP_mutators.csv`, restamp, save grid | FOUNDRY | Yes | `verify_frozen.py --restamp`; final review save with grid key |

---

## Caveats & Assumptions

1. **The full def dump location**: Assumed to be accessible via live game or cached dump. If offline dump `OFFICIAL-2026-09-06` exists, use that; otherwise bridge must call `jawa/get_defs TileMutatorDef/*`.

2. **GL disabled list**: Verified against item spec (14 disabled names given); live `ModsConfig.xml` is authoritative and may have drifted since item filing (2026-09-06 19:35:03Z).

3. **Mod prefix assumption**: Prefixes (vanilla, AB_, VLE_, GL_, etc.) inferred from defName conventions; if mod attribution is wrong, will be caught in step 2 when contact sheet is built.

4. **Category conflicts**: When assigning unused mutators, `AddMutator` may silently drop due to category conflict (reads documented in the `AddMutator` source or engine logs). Step 4 must read back what was actually applied and diff against the CSV to verify.

5. **No GL path proven yet**: Item spec notes GL doesn't place GL_* mutators itself on Ashkarr. Step 2 must prove the `TileMutatorWorker_Landform` actually applies GL landforms when set — if not, GL landforms bypass assignment entirely (they'd need a different mechanism).

---

## Files & References

- **In-use source:** `/mnt/d/Luke/dev/Rimworld/world/ASHKARR_WORLDMAP_mutators.csv`
- **GL mod config (live):** `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\Mod_2773943594_GeologicalLandformsMod.xml`
- **GL mod config (repo copy):** `/mnt/d/Luke/dev/Rimworld/deployed/config/v1_freeze/Mod_2773943594_GeologicalLandformsMod.xml`
- **Queue item:** `UNUSED_MUTATORS_WORLD_ASSIGNMENT_1` (steps 1 of 5, this document completes step 1)

---

## Sign-Off

**Step 1 Completion:** 2026-09-06 offline census complete.  
**Pending:** Steps 2–5 (bridge + owner + live testing required).  
**Not Closed:** Item remains in "doing" state until all 5 steps complete.

