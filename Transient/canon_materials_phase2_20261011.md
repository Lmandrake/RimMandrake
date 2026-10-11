# CANON_MATERIALS_BUILD_1 — phase 2 offline pass (L5, L7, L8, L9), 2026-10-11

Script: `src/RimStarWars/Armoury/prove_canon_materials.py` (`--selftest` plants a defect for every new check). Output:
`Transient/canon_materials_prove_output_phase2_20261011.txt`. validate_patch (4 patches + 1 def, `--defs` Data+Mods+workshop,
`--live` capture 2026-10-11T05-02-19Z): 0 errors, 13 warnings, all by design (`Transient/canon_materials_validate_patch_phase2_20261011.txt`).
Nothing deployed and nothing loaded. L10 (one minimal-list load) covers all of it.

| criterion | before | now | basis |
|---|---|---|---|
| L1 | PASS | **PARTIAL** | the defect and the Mines 2.0 gap below |
| L5 | OWED | PASS (L0) | `RSW_Duranium` defined; `RSW_SalvageByComposition.xml` replayed on fixtures copied from the real defs |
| L7 | OWED | PARTIAL | recipe removed, smelting returns no beskar, mining routes zeroed; "lesser ores" and Mines 2.0 still owed |
| L8 | OWED | PASS (L0) | three descriptions; no DefInjected override replaces them |
| L9 | OWED | PARTIAL | census built (`canon_materials_census.py`); the criterion conflicts with a later card |

## Defect in the first pass (L1): a patch class that does not exist
`RSW_DurasteelProducersZeroed.xml` used `PatchOperationAddOrReplace`. That class is not in decompiled 1.6 Verse, and a scan of every
DLL under Mods and workshop found it in none of them. The same scan did find other mods' PatchOperation classes, so it can see them.
Patches with that class would not have loaded, and the old prove script's simulator still reported them as passing.
Fixed by using Conditional(Replace | Add). New check: `patch_classes_bad` rejects any non-vanilla PatchOperation class in the
material patches. Its planted defect is an AddOrReplace patch.

## Two engine routes produce a rock even when its commonality is 0 (L1, L7)
Read from decompiled 1.6:
- `ThingSetMaker_Meteorite` picks any mineable that does not set `mineablePreventMeteorite`.
- Odyssey `TileMutatorWorker_MineralRich` picks one resource rock per tile from every `isResourceRock` def that is not on
  `MineralRich.resourceBlacklist`. When that rock's commonality is 0, its small-map fallback still scatters it.

`RSW_ZeroedOreGates.xml` fixes this for six rocks. Each of LKDurasteel_Ore, LKBeskar_Ore and LKPureBeskar_Ore gets
`mineablePreventMeteorite` and a blacklist row. KOTOR_MineableDurasteel and KOTOR_MineableBeskar also get both, the meteorite flag
set in source. RSW_MineableDoonium gets a blacklist row: it is asteroid-only, but a mineral-rich planet tile could scatter it.
**Not fixed:** Mines 2.0 (`cain.mineshaft`, active) generates a mine-shaft recipe for every `isResourceRock` def regardless of
commonality (`CreateRecipeDefs.IsMinableSource`). The live capture holds
`MinesAutomated_RecipeDef_{LKDurasteel_Ore,KOTOR_MineableDurasteel,LKBeskar_Ore,LKPureBeskar_Ore,KOTOR_MineableBeskar}`, and
`..._MineablePlasteel` too (an L4-shaped gap). XML cannot remove generated recipes. Setting `isResourceRock=false` would make the
rocks natural stone (TerrainDefGenerator_Stone), so it is not done. This needs code, or a ruling to drop Mines 2.0.

## L5 salvage by composition
| salvage | added (PROVISIONAL amounts) | field |
|---|---|---|
| Core `ShipChunk` (children of ShipChunkBase inherit it) | +20 RSW_Durasteel, +10 Plasteel | costList |
| Core `ShuttleCrashed` (both Biotech exitable children inherit it) | +30 RSW_Durasteel, +10 RSW_Duranium, +5 RSW_Doonium (it already has 70 Plasteel) | costList |
| VFE Pirates `VFEP_ShipChunkReactor` | +10 RSW_Doonium | costList |
| VFE Pirates `VFEP_CrashedShip` parent (4 wrecks) | +30 durasteel, +15 plasteel, +10 duranium, +5 doonium | killedLeavings (it has no costList) |
| B1 battle/security/commander droids | +12 Plasteel | race butcherProducts |

`ShipChunk_durasteel` already yields 40 durasteel and 20 plasteel, so it is untouched. B1 remains have exactly one plasteel route, and
the script counts the routes:
- meatDef is Steel and leatherDef is Leather_Human;
- 11 live recipes admit a B1 corpse, and they are butchery, which makes no plasteel;
- no Droidworks C# names Plasteel.

Planted defect: a B1 race that already has a plasteel butcher product reads as 2 routes on each of the three races.
Side finding, not touched: B1 droids butcher into 75 `Leather_Human` (`LeatherAmount` 75).

## L7 beskar never reforged
- `kotor_IngotBeskar_recipe` and `kotor_IngotBeskar_10xrecipe` are deleted from the Armoury's absorbed `Metals2.xml`, the same way the
  durasteel recipes were. `RSW_BeskarNeverReforged.xml` also removes the donor's copy behind a FindMod on
  "Star Wars KotOR Resources and Materials". That donor is inactive in the live ModsConfig, so this removal is insurance.
- Smelting: `Thing.SmeltProducts` returns a cost-list stuff only if that stuff is `smeltable`. Outer Rim's two beskars inherit
  smeltable=true from OuterRimMetal, so they are set false (FindMod "Outer Rim - Core"). `KOTOR_IngotBeskar` was already false.
  **Owed:** steel and slag as "lesser ores" in place of the beskar. That needs a SmeltProducts postfix in C#.
- Mining (FindMod "LK Mineable Resources Outer Rim"):
  - LK's beskar rocks get scatter 0 and come out of PreciousLump and both Odyssey asteroid counts;
  - the deep deposits LK adds to both Outer Rim beskars go to 0;
  - the Ideology `WorkSite_Mining` beskar loot rows are removed, because beskar is salvage only;
  - `KOTOR_MineableBeskar` gets scatter 0 in source.
- The absorbed Metals2 file says it is generated by `gen_kotorcore_absorption.py`. A regeneration would undo these source edits and
  the earlier durasteel ones. The generator has no transforms for them.

## L8 role prose
- `RM_CloakLacquer`: adds "The film hides a person and nothing larger: no amount of it will cloak a ship or a machine."
- `RUT_Mindstone`: adds "What kyber is to the Force, mindstone is to machines: cut true and set in a droid's head, it can hold a mind."
  **Kept** "Droids do not like to be near it". That is not a contradiction. `mindstone_arc_legends.md` Entry I is owner-ruled lore
  ("droids will not go near it ... the machines seem to fear it might be them"), and their fear is of exactly this role. The knowledge
  gates still hold: the text names no Kindled and no Cathedral.
- `RSW_Leather_KraytDragon`: adds "the best of the hides, though still an ordinary leather". It has no heirloom, quest or beskar rule.
- Checks: the old texts fail, and so does an "heirloom" krayt text. The check also looks for DefInjected overrides and finds none.

## L9 key-job census
`python3 src/RimStarWars/Armoury/canon_materials_census.py --csv <out>` writes `Transient/canon_materials_l9_census_20261011.csv`
(2,549 consumer rows) and `..._jobs.csv` (every def in each key job and what it costs). Probes 5/5: BionicArm fixes Plasteel and is
a prosthetic; Door takes Plasteel as stuff and is not a blast door; Make_BionicArm's ingredient admits only Plasteel. Results:
- hull plating: 8 defs; durasteel is FIXED in 1 (`guy762_PoweredWall_SandcrawlerHull`, 8 durasteel).
- blast and vault doors: 6 (PH blast doors), steel cost plus stuff, so preference only.
- droid shells: 2 (`RSW_DW_Part_Frame` steel 40, `_Primitive`); plasteel is not used at all.
- prosthetics and implants: 65 defs and 80 fixed Plasteel consumers (Core and mod bionics).
- large frames: 30 by a keyword rule (VFE Factory machines, GravEngine, droid frame; the rule catches some noise such as bedrolls);
  no duranium consumer.
- reactor cores: 35; no doonium consumer.

**Ruling conflict, so no verdict:** the item's L9 and design §4 say "preferences only, none enforced". The BENCH note of 2026-10-09
23:06Z records a later card, 15:01 local, after the 15:57Z "held as preferences" note. It makes durasteel hard in none of its jobs,
plasteel HARD for droid shells and prosthetics, duranium HARD for large frames, and doonium HARD for cores. The two cannot both stand.
The census measures either way.
