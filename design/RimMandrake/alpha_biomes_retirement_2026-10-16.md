# Alpha Biomes retirement plan, 2026-10-16 (FOUNDRY helper)

Owner, by card: *"Should Alpha Biomes retire as a donor too -> Yes, retire it"*. Umbrella item `ALPHA_BIOMES_RETIRE_THE_LAST_PLANT_DONOR`. Package `sarg.alphabiomes`, workshop 1841354677 (readable on this machine at `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\1841354677`). Nothing in this file is ported yet; the XML port is not started.

## Headline findings (measured by XML parse and grep of `src/`, 2026-10-16)

1. **The kickoff's "16 names" is the shipping `RM_` roster slice only.** Measured: 14 plant defs and 3 disease incidents in the three biomes' own roster rows (TheRot 12 plants, TheForge 2 plants, Miasma 3 diseases) = 17 names, not 16; the Forge's third row in the kickoff count is `LavaSnail`, which is an animal from a different mod, not Alpha Biomes. The whole live footprint is **146 distinct `AB_` names** in XML and C# under `src/` (comments stripped): terrains, weather, thoughts, biomes, tile mutators, incidents, game conditions and plants. The other 129 are listed in `ALPHA_BIOMES_CENSUS_THE_REST_OF_IT`, which needs his decision on scope (most sit in frozen `RUT_` twins, which the gate exempts, and in the `ExplosiveGrowth` roster and `PlantTolerances_Ashkarr` patch, which are not exempt).
2. **All 14 plants are donor DEFS wearing our patches.** `TheRot/Patches/RotSpecies_NamesAndSizes.xml` relabels, redescribes, resizes and retextures them in place (e.g. `AB_ArbuscularMycorrhiza` becomes "madruka", `visualSizeRange` 5.14~9, `texPath` `RotSpecies/ArbuscularMycorrhiza`). With the donor gone the def itself vanishes, so each needs a real `RM_` ThingDef (copy the donor def, fold the patch values in, parent `TreeBase`/`PlantBase`/`AB_CavePlantBase` replaced by our own abstract).
3. **Art is already ours for all 14, so no art jobs were queued for Alpha Biomes.** The ledger shows `artpipe` provenance for every `RotSpecies/*` file TheRot uses (12 plants); the three vanilla-texture plants (`Bryolux`, `Glowstool`, `GlowingAgarilux`) point at vanilla `Things/Plant/*` paths in the donor def and `RotSpecies/*` after our patch. Repo copies under `UtinniPatches/Textures/Things/Plants/AB_*` differ in sha from the donor files (ours). `AB_TinkleGrass` has no texture of ours installed (served by the donor today) but render `gapbs_AB_TinkleGrass_v1` is done; `gapbs_AB_FirevineTree_v1` is also done. Variants that exist only as finished renders (`rotvar_ab_*_{a,b}_v1`, 8 plants) wait on his picks. Item `ALPHA_BIOMES_INSTALL_UNINSTALLED_RENDERS`.

## The 17 names: what each is and what references it

| name | what it is (donor def) | donor art | ours today | referenced by (non-comment, file counts by tier) |
|---|---|---|---|---|
| `AB_Bryolux` | ThingDef "bryolux", Graphic_Random, visual size 0.82~0.95 | `Things/Plant/Bryolux` | `RotSpecies/Bryolux` via patch | RUT 2, RM 3 |
| `AB_Glowstool` | ThingDef "glowstool", Graphic_Random, visual size 0.4~0.7 | `Things/Plant/Glowstool` | `RotSpecies/Glowstool` via patch | RUT 2, RM 3 |
| `AB_GiantAgarilux` | ThingDef "giant agarilux", Graphic_Random, visual size 3.5~6 | `Things/Plants/AB_GiantAgarilux` | `RotSpecies/GiantAgarilux` via patch | RUT 2, RM 5 |
| `AB_GlowingAgarilux` | ThingDef "glowing agarilux", Graphic_Random, visual size 1.3~2 | `Things/Plant/Agarilux` | `RotSpecies/GlowingAgarilux` via patch | RUT 2, RM 4 |
| `AB_LilacBeacon` | ThingDef "lilac beacon", Graphic_Random, visual size 1~2 | `Things/Plants/AB_LilacBeacon` | `RotSpecies/LilacBeacon` via patch | RUT 2, RM 4 |
| `AB_WitchesOyster` | ThingDef "witches' oyster", Graphic_Single, visual size 1~2 | `Things/Plants/AB_WitchesOyster` | `RotSpecies/WitchesOyster` via patch | RUT 2, RM 5 |
| `AB_RecurvedStropharia` | ThingDef "recurved stropharia", Graphic_Single, visual size 3.5~5 | `Things/Plants/AB_RecurvedStropharia` | `RotSpecies/RecurvedStropharia` via patch | RUT 2, RM 4 |
| `AB_ArbuscularMycorrhiza` | ThingDef "arbuscular mycorrhiza", Graphic_Random, visual size 2~3.5 | `Things/Plants/AB_ArbuscularMycorrhiza` | `RotSpecies/ArbuscularMycorrhiza` via patch | RUT 2, RM 5 |
| `AB_SlimyPholiota` | ThingDef "slimy pholiota", Graphic_Random, visual size 3.5~5 | `Things/Plants/AB_SlimyPholiota` | `RotSpecies/SlimyPholiota` via patch | RUT 2, RM 4 |
| `AB_AgaricusDomeCap` | ThingDef "agaricus domecap", Graphic_Single, visual size 1.5~2 | `Things/Plants/AB_AgaricusDomeCap` | `RotSpecies/AgaricusDomeCap` via patch | RUT 2, RM 5 |
| `AB_DribblingCap` | ThingDef "dribbling cap", Graphic_Random, visual size 3.5~5 | `Things/Plants/AB_DribblingCap` | `RotSpecies/DribblingCap` via patch | RUT 2, RM 5 |
| `AB_AgariluxPrime` | ThingDef "Agarilux Prime", Graphic_Single, visual size 7.95~8 | `Things/Plants/AB_AgariluxPrime` | `RotSpecies/AgariluxPrime` via patch | RUT 2, RM 5 |
| `AB_TinkleGrass` | ThingDef "tinkle grass", Graphic_Single, visual size 0.6~0.9 | `Things/Plants/AB_TinkleGrass` | TinkleGrass: render done, not installed | RUT 1, RM 3 |
| `AB_FirevineTree` | ThingDef "firevine tree", Graphic_Random, visual size 2.8~3.8 | `Things/Plants/AB_FirevineTree` | FirevineTree: `UtinniPatches/.../AB_FirevineTreeA.png` (ours) + render gapbs | RUT 1, RM 1 |
| `AB_Disease_BacterialGangrene` | IncidentDef (disease) | none | n/a | RUT 1, RM 1 |
| `AB_Disease_ViralAbasia` | IncidentDef (disease) | none | n/a | RUT 1, RM 1 |
| `AB_Disease_RavagingIntestinalParasites` | IncidentDef (disease) | none | n/a | RUT 1, RM 1 |

File lists per name: `design/RimMandrake/alpha_biomes_hits_2026-10-16.json` (generated, regenerate with the scratch census described below).

Every plant row is referenced by: `RM_TheRot_Biome.xml` / `RM_TheForge_Biome.xml` (roster, MayRequire-guarded), `RUT_TheRot.xml` / `RUT_TheForge.xml` (frozen twin), `PlantTolerances_Ashkarr.xml` (13 rows per TheRot plant, RUT), `RM_ExplosiveGrowthRoster.xml`, `RotSpecies_NamesAndSizes.xml` and `RotGiants_HugeFootprint.xml` (the retexture/resize patches), and for TheRot's nine mushroom names `RimMandrake/BiomesShell/Source/RM_PlantDrawOrder.cs`. Tinkle grass is also named in `Miasma/RM_DecayDrake.xml` and `TheForge/Patches/RM_TheForge_GroundCoverDrawLayer.xml`. The three diseases are in `Miasma/RM_Miasma.xml` and `RUT_Miasma.xml` `<diseases>`; `RUT_Contagion`/`RUT_TheRot` also carry `AB_Disease_SporesAllergy`/`AnimalSporesAllergy` (not in the 17).

C# strings naming the package or its defs: `EnvironmentalHazards/Source/RM_WarmGroundExtension.cs` (`AB_MycoticGrass`), `RM_PollinationGateExtension.cs` (`AB_MangroveTree`, `AB_MangrovePalm`, `AB_ParasiticMangrove`), `Pyrelands/Source/WildPlantAllowlist.cs` (`AB_GiantStikehr`, `AB_RockyCrags`, `AB_MechanoidIntrusion`, `AB_SessileMechanoid`), `Pyrelands/PyrelandsTuning.cs`, `BiomesShell/Source/RM_PlantDrawOrder.cs` (nine plant names above), plus `FlowWorks`, `RiverColors` and `EnvironmentalHazards` hits on terrain and biome names.

## Port plan (do not start before his go; XML only)

1. `ALPHA_BIOMES_MIGRATE_PLANTS_TO_RM_TWINS`: for each of the 14, write `RM_<Name>` ThingDefs under TheRot / TheForge defs (copy donor def from workshop `1.6/Defs/ThingDefs_Plants/`, fold in the label, description, size and texPath the patches set, our own parent, no `MayRequire`), repoint `RM_` biome rosters, `ExplosiveGrowth` roster, `RM_PlantDrawOrder.cs` names and the Forge ground-cover patch; delete the retexture patches they make redundant. `RUT_` twins are frozen: their guarded rows drop out quietly.
2. `ALPHA_BIOMES_MIGRATE_DISEASES_AND_CODE`: Miasma needs three disease incidents of our own (`RM_` IncidentDefs using vanilla disease hediffs, or drop the three rows by his say), and the C# strings above change.
3. `ALPHA_BIOMES_INSTALL_UNINSTALLED_RENDERS`: sheet and `art.py install` for Tinkle grass, Firevine tree and the waiting `rotvar_*` variants.
4. `ALPHA_BIOMES_CENSUS_THE_REST_OF_IT`: his scope call on the other names (terrain, weather, thoughts, biomes: porting a BiomeDef or WeatherDef is a different job from porting a plant).
5. Then the SWAC/AA gate (kickoff 0.5.5): rosters, references, art, save, live round, list.

Facings and sizes for any art still owed: plants take no facings (`facings` empty, one job per variant, 256 px, 512 for `visualSizeRange` max 5 and up). Donor variant counts: GiantAgarilux 6, Arbuscular 4, DribblingCap 4, SlimyPholiota 3, LilacBeacon 3, others 1, Firevine 4 (+ a leafless frame no XML uses).
