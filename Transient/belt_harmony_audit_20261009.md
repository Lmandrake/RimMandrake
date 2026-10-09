# Harmony PatchApplier conversion audit 2026-10-09

Source: origin/main 16586f34c (RimMandrake, RimStarWars, RimUtinni; 38 Apply sites in 37 assemblies + the ExplosiveKnockback forced-miss probe). Live: Player.log (00:10, 57 KB) census lines. Read-only; no code changed.

## Verdict

**No dropped patches.** Apply with `ns=null` (every call but ExplosiveKnockback's) patches every `[HarmonyPatch]`-attributed class in the assembly, exactly as PatchAll did, one at a time. For all 32 assemblies in the live log, class count == `patched N`, `missing 0`. No Apply call passes a feature tag or exclusion (Apply takes none; `[PatchFeature]` only labels a class for the failure path).

## Instrument notes

Class counter: a `[HarmonyPatch]` (or `HarmonyLib.HarmonyPatch`) attribute followed by a class declaration, with balanced-bracket attribute skipping, comments stripped, classes deduped (stacked `[HarmonyPatch]` lines on one class count once), and csproj `Compile Include` honoured where `EnableDefaultCompileItems` is false. Sanity probe: the first regexes undercounted FlowWorks (28 vs live 31), GimmeSomeSlack (22 vs 26: `HarmonyLib.`-qualified attributes and `new[] {}` inside the attribute) and overcounted LuminousPigment (15 vs 14: two stacked attributes on one class). After fixing, every live number matches exactly.

## Table

| Assembly | Apply site | ns filter | [HarmonyPatch] classes | Apply covers | live census | hand `.Patch(` outside Apply | Apply timing |
|---|---|---|---|---|---|---|---|
| Abyss | RM_AbyssMod.cs:217 | none (all) | 1 | 1 | 1 | - | |
| Aftermath | AftermathMod.cs:18 | none (all) | 6 | 6 | 6 | - | |
| Cauldron | RM_VexxithAcidImmunity.cs:38 | none (all) | 1 | 1 | 1 | none now | |
| DivingInteraction | RM_DivingSettings.cs:467 | none (all) | 10 | 10 | 10 | - | |
| ExplosiveGrowth | RM_ExplosiveGrowthPatches.cs:25 | none (all) | 5 | 5 | not in log (mod not active that session) | - | |
| ExplosiveKnockback | RM_KnockbackMod.cs:125 | RimMandrake.ExplosiveKnockback | 5 | 4 | 4 | - | |
| ExplosiveKnockback | RM_PatchApplierProbe.cs:29 | RimMandrake.ExplosiveKnockback.ForcedMissProbe | 5 | 1 | 4 | - | |
| FeverWood | RM_FeverWoodMod.cs:457 | none (all) | 5 | 5 | 5 | - | |
| FloodedCanyon | RM_FloodedCanyonMod.cs:285 | none (all) | 2 | 2 | 2 | - | |
| FlowWorks | RM_Patch_SuperdeepShooting.cs:31 | none (all) | 31 | 31 | 31 | RM_FerryAndLevee.cs (private/optional targets, pre-existing) | |
| GimmeSomeSlack | GimmeSomeSlackMod.cs:157 | none (all) | 26 | 26 | 26 | - | |
| GravshipLanding | GravshipLandingMod.cs:38 | none (all) | 1 | 1 | 1 | - | |
| Inhabited | InhabitedMod.cs:31 | none (all) | 3 | 3 | 3 | - | |
| KeelHoist | KeelHoistMod.cs:130 | none (all) | 2 | 2 | 2 | - | |
| KineticArms | RM_KineticArmsMod.cs:90 | none (all) | 2 | 2 | 2 | - | |
| LanternDeeps | Patch_PocketMapGrowthRate.cs:35 | none (all) | 4 | 4 | 4 | - | |
| LuminousPigment | HarmonyPatches.cs:20 | none (all) | 14 | 14 | 14 | DeepfireLightsOutCompat.cs (LightsOut compat, try/catch) | |
| Ninefold | NinefoldMod.cs:28 | none (all) | 31 | 31 | 31 | - | |
| PlanetPresetPrime | PlanetPresetPrime.cs:27 | none (all) | 1 | 1 | 1 | - | |
| RaidRedesigner | RaidRedesignerMod.cs:25 | none (all) | 5 | 5 | 5 | Patch_CaravanRobbed.cs (TryPatch, optional mod) | |
| RustCathedral/Source/Hum | HarmonyPatch_WatchedBolts.cs:25 | none (all) | 12 | 12 | 12 | - | |
| RustCathedral/Source/Walls | HarmonyPatch_GateLivePatternMetal.cs:22 | none (all) | 1 | 1 | 1 | - | |
| Scarlands | RM_Chotrix.cs:125 | none (all) | 12 | 12 | 12 | RM_AerosolScreen.cs wasteland bridge (try/catch) | |
| SeaShores | RM_SeaShoresHarmony.cs:19 | none (all) | 3 | 3 | 3 | RM_SeaShoresHarmony.cs private TryAddMutator (null-guarded, NOT in try/catch) | |
| SolarMirrors | RM_SolarMirrorsMod.cs:243 | none (all) | 3 | 3 | 3 | - | |
| TerminalBiomes | RM_TerminalBiomesMod.cs:546 | none (all) | 11 | 11 | 11 | - | |
| TheForge | RM_ForgeSpunstone.cs:121 | none (all) | 3 | 3 | 3 | - | |
| Wreckage | RM_WreckageMod.cs:110 | none (all) | 1 | 1 | 1 | - | |
| GizkaStowaway | RSW_GizkaHarmonyPatches.cs:20 | none (all) | 5 | 5 | not in log (mod not active that session) | - | |
| SWBestiary/Source/BeastMechanics | RSW_BeastMechanicsSettings.cs:87 | none (all) | 1 | 1 | 1 | - | |
| CathedralPass | CathedralPassMod.cs:37 | none (all) | 1 | 1 | 1 | - | |
| EmpirePursuit | HarmonyPatches.cs:19 | none (all) | 3 | 3 | 3 | - | |
| FallLineArrivals | FeralRaces.cs:54 | none (all) | 1 | 1 | 1 | - | |
| FungalSoilTrade | MapComponent_RotFungalDistress.cs:62 | none (all) | 1 | 1 | not in log (mod not active that session) | - | |
| PlantGrowth | Patch_Plant_GrowthRate.cs:22 | none (all) | 1 | 1 | not in log (mod not active that session) | - | |
| PropaneLakeMechanics | PropaneLakeMechanicsMod.cs:14 | none (all) | 1 | 1 | not in log (mod not active that session) | - | |
| RiverColors | HarmonyPatch_RiverColors.cs:65 | none (all) | 1 | 1 | not in log (mod not active that session) | - | |
| ShipShields | HarmonyPatches.cs:16 | none (all) | 2 | 2 | 2 | - | |
| UnfinishedLine | UnfinishedLineTithe.cs:228 | none (all) | 3 | 3 | 3 | - | |

ExplosiveKnockback: 5 classes in the assembly, 4 in `RimMandrake.ExplosiveKnockback`, 1 (`RM_ForcedMissPatch`) in `...ForcedMissProbe` deliberately excluded by the namespace filter; `RM_PatchApplierProbe.Probe` applies it once on demand (a test probe, runs nothing at startup). Live 4/0 is correct. The second table row for ExplosiveKnockback is that probe, not a conversion.

Not in the 00:10 log (mod inactive that session, so live N is UNMEASURED; source count shown above): ExplosiveGrowth, GizkaStowaway, FungalSoilTrade, PlantGrowth, PropaneLakeMechanics, RiverColors.

## Other checks

- Namespace outliers: none (only ExplosiveKnockback uses a filter). RaidRedesigner has one class in `RimMandrake.Spikes`, covered because it passes no filter.
- Remaining `PatchAll(` calls in RimMandrake: none (only comments). Still PatchAll in RimStarWars/Armoury (4 files), not converted, out of scope. Pyrelands comment says it has no PatchAll anywhere (unconverted/unrelated).
- Hand-written `harmony.Patch(` outside Apply (6 sites listed in table): all pre-date the conversion and target private or optional-mod methods that attributes cannot reach; none were ever covered by PatchAll, so nothing was dropped. Only SeaShores' call is not in a try/catch (null-guarded; a throw would abort its static constructor). Low risk, not changed.
- Settings timing: every non-Mod caller sits in a `[StaticConstructorOnStartup]` class (runs after all Mod constructors, so settings are loaded); every Mod-subclass caller has `GetSettings<>` earlier in the same file. `Apply` itself never reads a setting; `[PatchFeature]` is read only on the failure path (`Fail` snapshots the field and forces it false). Only Ninefold, FlowWorks, Cauldron and the EK probe call `BeforeExpose/AfterExpose`, so in the other adopters a failure-forced-off setting would be overwritten by a later settings load; harmless because the patch itself is simply absent, but the toggle would still read ON. Not a dropped patch.
- Static check that the `typeof(X).Assembly` anchor lives in the same csproj as the counted sources: passes for all.

## Fixes

None required; nothing landed.
