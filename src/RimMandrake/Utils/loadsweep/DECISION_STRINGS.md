# LOAD-HEALTH SWEEP decision strings — written BEFORE any launch, 2026-09-02

Base (9, proven clean 2026-09-01): brrainz.harmony, core+5 expansions,
imranfish.xmlextensions, brrainz.rimbridgeserver.

## FAIL strings (any batch)
- Player.log: `Recovered from incompatible or corrupted mods` OR disk activeMods
  collapses to 6 (Core-only recovery reset) OR bridge context modSet != intended count
- Player.log: `^Config error in` count > 0
- `Could not resolve cross-reference` naming RM_ / RSW_ / RUT_ / Jawa_
- `Patch operation` + `failed` naming a mandrake mod file
- `TypeLoadException` / `ReflectionTypeLoadException` naming a mandrake assembly
  (per-assembly signature = the assembly name in the exception text; that is what
  makes 8 C#-only mods batchable: their failures are name-attributed)

## PASS positive (batch 1 — not silence)
- `[JawaBench] ready:` present; context line `modSet 33/`
- jawa/get_defs returns non-null for ALL 13 sentinels:
  DamageDef:RSW_RN2_SteelBall (Armoury) · TerrainDef:RSW_FE_Ash_Trace (FireEcology-RSW)
  ThingDef:RM_FluidSpring_Test (FluidCanals) · ThingDef:RM_Graffiti_Vandal (Graffiti)
  LandmarkDef:RUT_LightlessSink (IshkoDarkLandmarks) · ThingDef:RSW_Cindermare (Livestock)
  TraitDef:RUT_Jawa_WaterDiscipline (PawnFlavor) · ThingDef:RM_PitCell_Single (Pits)
  ThingDef:RUT_Skewer (StickCuisine) · QuestScriptDef:RM_Stranded (StrandedQuest)
  SoundDef:RSW_Ingest_Glitterstim (SWBestiary) · GameConditionDef:RSW_WS_TerminatorFront
  (WeatherSuite) · ScenPartDef:RUT_RuthlessPursuingMechanoids (EmpirePursuit)
- C#-only mods (JawaRules, Ninefold, Oracle, PlanetPresetPrime, Property, RimDefDump,
  RiverSteam, Visibility): PASS = zero type-load exceptions naming them + clean menu.
- Patches-only (AshkarrLandmarkArt, FactionSlate): PASS = no `Patch operation failed`;
  their targets are absent on minimal so no-op silence is EXPECTED, not a pass on content.
- PlantGrowth: custom-typed settings def; get_defs may not resolve the type —
  that reads UNMEASURED, not FAIL; its check is no config error naming RUT_JawaPlantGrowth.

## Batch 2 (WreckedMachines)
base + vanillaexpanded.vfecore + vanillaexpanded.vfefactory + mandrake.rm.wreckedmachines
- PASS positive: get_defs ThingDef:RM_WM_AutomatedSmelter_Wrecked non-null; no VFEF
  cross-ref errors naming RM_WM_.

## Excluded, on purpose
- HelixTellurox — KNOWN crasher (HELIX_TELLUROX_SHELL_LOAD_CRASH_1), stays OUT.
- mandrake.jawa.patches, mandrake.rsw.seaswaterline — biome injectors, mapgen NRE.
- Dep-carrying mods (BeastNorm, Droidworks, IonWeapons, StarWarsRaces, …) — out of
  scope for this sweep per handoff.

## On any recovery reset
Disk config is wiped to Core-only: REWRITE the intended list before relaunch, bisect
the batch (config errors self-attribute; only hard resets need bisection).

## FULL 592 relaunch (post-sweep, written 01:24 before launch)
- PASS (fix proof): NO `Config error in TargetedInsultingSpree` (batch-1 baseline: 1 hit; label {0} removed + deployed)
- EXPECTED PRESENT (campaign-real, unfixed): `Config error in RSW_Gun_Sonic_HiveEmitter` x2, `burnedDef is flammable` x6
- EXPECTED ABSENT on full: guy762_*/SWPotF_*/EBSG_* crossrefs (donor mods present on 592)
- `[RimDefDump]` fires at menu (armed `all`); delete marker after
