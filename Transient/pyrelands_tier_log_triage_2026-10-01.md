# Pyrelands tier log triage 2026-10-01

Log: Player.log copy of the 20-mod pyrelands tier load (09:41, build 89dd1414). harvest_log run with --stale-ok
(its def dump predates this run; counts below are from the log itself, which shows a COMPLETE load: bridge up at line 1115).
Deployed state matters: the game reads `Mods\RimMandrake.Biomes` (composed 2026-10-01 02:59) and `Mods\UtinniPatches`, not the repo.

## Source -> class -> action (filling)

| source | class | action |
|---|---|---|
| RM_LiquidProperties "does nothing beyond documenting viscosity" (~111 of 158 ConfigErrors) | a (real: advisory emitted as error) | remove the yield in `FlowWorks/Source/LiquidTypes/RM_LiquidProperties.cs`, rebuild DLL+srchash |
| RM_TheSump / RM_Warscar `ConfigErrors()` NRE | b (cascade) | BiomeDef.ConfigErrors does `wa.animal.defName` on duplicate unresolved wildAnimals rows; vanishes when the unresolved rows resolve or are MayRequire-guarded |
| RM_TheSump unresolved RM_Sump* fauna/flora (13 xrefs) | deploy lag | repo already holds RM_SumpFauna/Flora + RM_TheSump_Biome (DEPLOY_HOLD, LOAD_ERRORS_DEF_FIELDS_1) but the OLD deployed biome copy is still in `Mods\RimMandrake.Biomes\Biomes\TheSump` ("game copy left as-is"). Deployer must remove it |
| texture failures (33 distinct paths) | c (art not rendered yet) | none: art jobs pending in artpipe, no png in repo or deployed. Exceptions to check: `Animal/RockTroll/RockTroll`, `swanimals/DesertPort/Zakkro/Zakkro`, `Things/Item/Apparel/Duster/Duster` (non-RM paths) |
| 15 SoundDef xrefs (Pawn_Insect_Ambient x18, Pawn_Melee_SmallBite_* x12, Warg_Eat, Muffalo_Eat/Call, Pawn_Squirrel_Call, Pawn_Dog_Wounded, Ingest_Vegetable) | a (names never existed in 1.6 Core) | FIXED 8db5a4419: repointed to real vanilla vox (Megascarab wounded/death, HumanBite/SmallScratch, PredatorLarge_Eat, Herbivore_Eat, Pawn_Rodent_*, Pawn_Dog_Injured, RawVegetable_Eat). Judgement: audio choice is mine |
| RM_Dunes_Sand "depositFilthChance set but depositFilthDef null" | a | FIXED: default chance 0 (Wasteland patch sets both explicitly); MovingDunes DLL rebuilt |
| RM_Storm_CinderwireWhine "PrioritizeNewest not supported with sustainers" | a | FIXED: priorityMode PrioritizeNearest |
| RM_Quest_RiteOfTipping "non-root quest has defaultChallengeRating" | a | FIXED: field removed |
| RM_ConstellationCageSphere/Cube, RM_NoothelmLampClipped, RM_HoolimbreLampClipped minifiable w/o category + no Mass | a | FIXED: thingCategories BuildingsMisc, Mass 10/3 |
| RUT_BrineDeposit_Tekk/Drazz/BrinePlate "claimable item is compressible" | a | FIXED: claimable false |
| RM_FE_Ash_Trace/Light + 4 ground bases "burnedDef is flammable" | c (deliberate, documented in AshLadder.xml header) | none; gate baseline must accept, ~12 lines |
| RM_TarShallow "makes terrain filth and also accepts it" | c (deliberate, SUMP_MECHANICS_1 patches) | none |
| LandmarkDef RUT_ComplexStructures / RUT_Slough_GelatinousBreach "no mutators chance >= 1" | c (deliberate, comment in def) | none |
| Eclipse/SolarFlare/Aurora "world-targeting incident has a biome restriction list" | judgement | from LanternDeeps suppression patch (owner ruling 2026-09-18). The vanilla check says the restriction list is meaningless on a world-targeting incident, so the suppression may not work at all; needs a design call |
| CannibalPirate / PirateYttakin "required meme not allowed" | c (vanilla/DLC faction defs, our patch only sets startingCount) | none |
| RUT_Jawa_* "cheapest weapon costs X but weaponMoney min Y" (4) | b/judgement | depends on donor weapons absent in this tier; Jawa campaign roster, not Pyrelands |
| RM_Warscar ConfigErrors NRE (4 unresolved patch-added wildAnimals: SW_Electrictick/gryllotalpa/Juggernautbeetles, RUT_ScarRoach) | b | FIXED d8766b4a1: MayRequire on the 4 rows in `WildAnimals_Warscar.xml` (Isopoda geneline / rustcathedralroaches). Note RM_Warscar (franchise-free tier) still gets a RUT_ creature from the campaign patch layer, which is a layering call, not a load defect |
| RM_TheSump ConfigErrors NRE + 13 xrefs (RM_Sump* fauna x5, flora x8) | deploy lag | NOT fixable in src: repo already holds the cast in held `RM_SumpFauna/Flora.xml` and `DEPLOY_HOLD` keeps `RM_TheSump_Biome.xml` "game copy left as-is" -- the OLD biome copy in `Mods\RimMandrake.Biomes\Biomes\TheSump` still names them. Deployer: delete that deployed biome file or lift the holds together |
| RUT_FoundrySalvageCache / RUT_FoundryTowerEntrance markerDef xrefs | deploy lag | same: scatter files held in repo (LOAD_ERRORS_DEF_FIELDS_1), stale copies deployed |
| donor plant/terrain/pawn rows in 14 biome defs (RG_Plant_* x6, IronScruff_* x3, AG_*, PoisonSoil/Rich, PoisonShrub, PoisonPlantTallGrass, GRimMoss, CypreJungle*, LightGrass, VolcanoSoil, WastelandAsphalt, TreePalma, VEE_Plant_DatePalm, VRE_PoluxBush, ZBiome_DesertOasis) | b | FIXED d8766b4a1: MayRequire on 98 rows/li (packageId read from each donor's About.xml; RM_ Abyss/LeaningScrub/TheForge/Wasteland and the RUT_ twins, two RUT patches). MayRequire on shorthand biome records is the existing convention (Overcast/GrayPall rows) |
| UtinniPatches Jawa roster/kinds/faction/scenario rows naming OuterRim_*, guy762_*, VFEP_*, RSW_MandrakeJawa, RSW_Jawa_Gamorrean_*, RSW_Jawa_Spawn_Hutt | b | FIXED: MayRequire (OuterRim.Core/GalacticEmpire, rsw.armoury, VFE.Pirates, rsw.starwarsraces, rsw.patches) |
| TabulaRasa.DefModExt_PawnKindExtended (3 pawnkinds in JawaFactionRoster.xml discarded) | b | FIXED: `MayRequire="neronix17.toolbox"` on the 3 modExtension li (same id the xenotypes tier uses); the kinds now load without the training hediff when the toolbox is absent |
| RSW_SW_RedFog weather row in RM_TheForge (xref) | b | row is in RM_TheForge_Biome; MayRequire on it is NOT applied (weatherDef row inside WeatherCommonalityRecord li with a patch-added def); report only |
| Stat BoneAmount (RSW_Maguana) | b | FIXED: MayRequire sihv.rombonesPort |
| Stat HungerRateMultiplier (RUT_YearningFruit hediff) | a | FIXED: HediffStage.hungerRateFactor (confirmed in decompiled HediffStage.cs) |
| RawVegetables (RM_Boilbulb harvest), Turtle (Stillsand useMeatFrom) | a | FIXED: RawPotatoes, SeaTurtle. Judgement: substitutes are mine |
| BodyPartGroup Jaw/Tail (Contagion, Sump) , HindlegsFrontClaws (Webwork), FrontLeft/RightFoot (Ashwallow, SlimeGrazer) | a | FIXED: Jaw/Tail/HindlegsFrontClaws are not groups anywhere (Jaw/Tail are BodyPartDefs): link dropped; FrontLeft/RightFoot -> FrontLeft/RightLeg |
| ThoughtDef AteUltracactus (RM_ and RSW_ Ultracactus) | a | FIXED: dangling field removed (and its stale "pre-existing dangling" comment) |
| "Failed to find any textures" Duster (RM_GreatboleHarvest apparel), RockTroll (RM_MuttavaqUttaqar), TerrorWorm (RSW_DesertPortMisc), Zakkro | b | donor-art paths (loud-donor placeholder by design / absent Space Worms); no repo art; not changed |
| Could not find type BiomeWorker_* (BiomesPlus, VanillaBiomes, ReGrowthCore, CypreJungle, DesertOasis) | b/c | donor biome workers for donor BiomeDefs absent in this tier; not ours |
| 155 patch ops failed (patchfail), Plant "Collection cannot init" texture lines | b/c | out of the four counts asked about; not triaged |

## State
- Not deployed (instructed). Everything above lands in the repo only; the bridge holder must deploy `RimMandrake.Biomes` (compose), `UtinniPatches`, `FlowWorks`, `MovingDunes` DLLs and resolve the TheSump/Foundry held-copy lag before the next load.
- Expected after deploy: the ~111 liquid lines, the 2 NRE lines, ~60 donor xrefs and the sound/body-part xrefs gone. Residual ConfigErrors that cannot go without a design call: FE ash burnedDef (12 lines), Tar filth, 2 landmarks, 3 incidents, 2 vanilla faction memes, 4 Jawa weaponMoney.
