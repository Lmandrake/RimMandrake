# FindMod audit 2026-10-03

Engine (decompiled `PatchOperationFindMod` -> `ModLister.HasActiveModWithName`): matches ACTIVE mods by exact, case-sensitive About `<name>` ONLY. packageIds never match. DLCs/Core match by their About names `Core`, `Royalty`, `Ideology`, `Biotech`, `Anomaly`, `Odyssey`.
Sweep: 115 FindMod names across src/**/*.xml; 1 name needing XML-unescape (`Big and Small - Genes &amp; More`) is OK. Sanity probe: Baroque Biomes resolves (13 files).
`MayRequire` on `<Operation>` (inert): 33 files list below (unverified, not changed).

## Result
Distinct names: 115 -> OK 105 (incl. 6 DLC/Core and 3 ship-only), INERT 10 before fixes, 1 left INERT unresolved + 0 fixed-by-us remaining ... see below.

## Fixed (our own mods, stale form) - 10 name-forms, 10 files
| was | now | files |
|---|---|---|
| `Ludeon.RimWorld` (packageId; Core's name is `Core`) | `Core` | FeverWood StakeLure + Suppression OrdersPatch, FlowWorks_OrdersPatch, Graffiti_OrdersPatch, LuminousPigment DeepfireOrdersPatch (5). These designator patches were INERT: designators never added to Orders. No C# duplicate registration exists. |
| `mandrake.rm.acousticscanner` | `RimMandrake: Acoustic Scanner` | FloodedCanyon RM_AcousticPayload, Stillsand RM_AcousticPayload, UtinniPatches AcousticPayload_CrackedLands (3) |
| `mandrake.rut.longhunger` | `RimUtinni: The Long Hunger` | Stillsand RM_Thumper_Groundcaller (1) |
| `RimMandrake - SW Sea Beasts` (defs live in SWBestiary) | `RimMandrake: SW — Bestiary` | Doctrine/Patches/MegafaunaYield.xml (1) |

## Remaining INERT, not changed
- `RimUtinni: Rot Spore Kit` -> no mod by that name; Rot Spore Kit content lives in TheRot (`RimMandrake: The Rot`) and others. Needs a decision which mod. File: src/RimUtinni/UtinniPatches/Patches/RotDecayHarvest_LivingProduce.xml
- `Medieval Overhaul` -> not installed in either root (probably intentional optional donor guard). File: src/RimMandrake/Pyrinth/Patches/Absorbed_EpochsPyrinth/Absorbed_EpochsPyrinth_MO_Cost_Patch.xml

## OK-but-note
Ship-only (not installed in Mods roots, fine if deployed): Moving Dunes, RimMandrake: Creature Behaviors, RimMandrake: Stillsand. All other 100+ donor/ours names resolve to an installed About name.

## MayRequire on <Operation> files (inert, unverified)
src/RimMandrake/FloodedCanyon/Defs/ThingDefs_Races/RM_MuttavaqUttaqar.xml
src/RimMandrake/LeaningScrub/Patches/BetterTrees_SweetlineTree_Immunity.xml
src/RimMandrake/MandrakePatches/Patches/ThirdPartySignConfigErrors_Fix.xml
src/RimMandrake/RimProperty/Patches/TheftHauler/DroidLoaders_TheftHauler.xml
src/RimMandrake/RimProperty/Patches/TheftHauler/MuckrakerChassis_TheftHauler.xml
src/RimStarWars/DesertVehicleReskin/Patches/BeastVehicleProp_Identity.xml
src/RimStarWars/DesertVehicleReskin/Patches/BeastVehicle_Identity.xml
src/RimStarWars/DesertVehicleReskin/Patches/EopieSled_Identity.xml
src/RimStarWars/SWBestiary/Patches/RSW_SekkulaathTank_DianogaSwap.xml
src/RimUtinni/AshkarrFlora/Patches/BetterTrees_SweetlineTree_Immunity.xml
src/RimUtinni/UtinniPatches/Patches/Absorbed_Cephaloids/Absorbed_Cephaloids_Patches.xml
src/RimUtinni/UtinniPatches/Patches/AncientDangerGenSteps_AmbientDoctrine.xml
src/RimUtinni/UtinniPatches/Patches/FishTypesStrip_NoFishBiomes.xml
src/RimUtinni/UtinniPatches/Patches/HolyFlame_RitualistWiring.xml
src/RimUtinni/UtinniPatches/Patches/TibannaEmbargo_CutMineableRoute.xml
src/RimUtinni/UtinniPatches/Patches/WildAnimals_BlueDesert.xml
src/RimUtinni/UtinniPatches/Patches/WildAnimals_Cauldron.xml
src/RimUtinni/UtinniPatches/Patches/WildAnimals_CrackedLands.xml
src/RimUtinni/UtinniPatches/Patches/WildAnimals_Greentide.xml
src/RimUtinni/UtinniPatches/Patches/WildAnimals_LanternDeeps.xml
src/RimUtinni/UtinniPatches/Patches/WildAnimals_LeaningScrub.xml
src/RimUtinni/UtinniPatches/Patches/WildAnimals_LongShade.xml
src/RimUtinni/UtinniPatches/Patches/WildAnimals_NightsideIce.xml
src/RimUtinni/UtinniPatches/Patches/WildAnimals_Pyrelands.xml
src/RimUtinni/UtinniPatches/Patches/WildAnimals_Stillsand.xml
src/RimUtinni/UtinniPatches/Patches/WildAnimals_Sump.xml
src/RimUtinni/UtinniPatches/Patches/WildAnimals_TheRot.xml
src/RimUtinni/UtinniPatches/Patches/WildAnimals_TheScald.xml
src/RimUtinni/UtinniPatches/Patches/WildAnimals_TwilightSea.xml
src/RimUtinni/UtinniPatches/Patches/WildAnimals_Warscar.xml
src/RimUtinni/UtinniPatches/Patches/WildAnimals_Wasteland.xml
src/RimUtinni/UtinniPatches/Patches/WildAnimals_WeepingStones.xml
src/RimUtinni/UtinniPatches/Patches/WildPlants_Webwork.xml
