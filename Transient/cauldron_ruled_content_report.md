# Cauldron ruled content report (CAULDRON_RULED_CONTENT_1)

## Status
- Landed in one commit on main (sha in the agent's final message). Mod folder is still
  `src/RimMandrake/PoisonForest/`, so PoisonForest names are in use; `CAULDRON_FULL_RENAME_1` has not run.
- No C#, no ledger writes, no game/bridge/deploy.

## Spec read
- Frozen sheet `design/Jawa/worldbuilding/biomes/poison_forest.md` and roster JSON
  `design/Jawa/worldbuilding/biomes/rosters/poison_forest.json` (imports at fauna rows 17-23).
- Twin architecture: RM_PoisonForest inline rows plus `UtinniPatches/Patches/WildAnimals_PoisonForest.xml`.

## Landed
1. Seven imports wired. Alpha Animals rows (Plasmorph, LuciferBug, Radyak, RipperHound) inline with
   MayRequire; Lylek and Skalder as RSW_ ports and Silooth as a donor row in the Utinni patch.
   Sheet ban lines and the RipperHound eviction row amended ("wire and keep"). Merged roster parsed by
   node name: all seven visible (29 rows merged).
2. Natives: RM_Vexxiss, RM_Zisska, RM_Eskith (ThingDef + PawnKindDef each, with art), RM_Xithess (plant,
   with art), RM_Vexxith (shear stuff, shear-only via CompProperties_Shearable on the vexxiss, no explosion
   anywhere), RM_ZisskaMeat (toxic prized meat via vanilla ToxicBuildup).
3. Seven AB_ flora diverged to RM_CrystalFlower, RM_BloodBouquet, RM_RavenNettle, RM_RedBugloss,
   RM_GiantAgariTox, RM_KeeningCordax, RM_GiantToxicFlower at unchanged weights; AB_ rows retired from the
   biome def. RM_TwistingThornwood description no longer claims ore.
4. Steep harvestWork: thornwood 210 to 1200, martyr 210 to 1000.
5. Existing toxic prized meat defs untouched.
- Patch guards on the Utinni file fixed from inert `Operation MayRequire` to PatchOperationFindMod.

## Deferred
- Growth-scaled metal second yield on both trees: needs a C# comp (plants tick via TickLong only).
  Follow-on CAULDRON_TREE_METAL_YIELD_1. Stub comment sits in both tree defs.
- Vexxiss behaviours (wild-shear job, fire warden, vent inhale, water poison), zisska rasping, eskith
  silence tell, vexxith acid immunity (no vanilla stat): CAULDRON_MECHANICS_BUILD_1 (C#).
  Vanilla shearing works on a tamed animal only.
- Mod Settings coverage for the new features: C#.
- Vexxith uses the Metallic stuff category as a stand-in; a dedicated non-metal StuffCategoryDef is owed.
- Xithess yields vanilla Chemfuel as a stand-in for a real vent-chemistry item.
- Rename sweep: CAULDRON_FULL_RENAME_1.

## Art
- Present and wired: RM_Vexxiss, RM_Zisska, RM_Eskith (north/east/south), RM_Xithess, RM_Vexxith.
- BLOCKED: the seven diverged flora. Their validated PNGs lived in gitignored
  `infrastructure/artpipe/_artsrc/` and are absent from this checkout; only manifests remain in `done/`.
  texPaths are wired; drop PNGs at
  `D:\Luke\dev\Rimworld\src\RimMandrake\PoisonForest\Textures\Things\Plant\RM_<Name>\RM_<Name>_a.png`.
  No donor art copied, no art queued.
- RM_ZisskaMeat uses vanilla Meat_Small retinted (no PNG).

## Validation
- XML parse (ElementTree) of every touched file OK; roster JSON parses.
- validate_patch.py: 0 errors; 7 texPath warnings are exactly the blocked flora art.
- defName sweep with korrum probe (7 hits): no collisions (only ThingDef/PawnKindDef pairs share a name).
- run_selftests: 75/78. Two failures are outside this change: selftest_retired_mods (Mo'Events FindMod in
  Doctrine and UtinniPatches patches) and selftest_deployed_biome_refs (RUT_TheRot / WeepingStones refs).
