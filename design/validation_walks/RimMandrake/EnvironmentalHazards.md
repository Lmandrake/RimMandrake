# RimMandrake: Environmental Hazards Kit — validation walk
subject: src/RimMandrake/EnvironmentalHazards  (packageId `mandrake.rm.environmentalhazards`)
deps: `mandrake.rm.creaturebehaviors`, `mandrake.rm.flowworks` (modDependencies); content mods opt into every mechanism by XML
list: shared C# assembly; the kit names no campaign, planet or creature
status-hint: ENVIRONMENTAL_HAZARDS_FIRST_SCRIPT_1 — first script drafted, never run live

Sources: `src/RimMandrake/EnvironmentalHazards/About/About.xml` description (the numbered mechanisms), `Defs/**`, `Source/RM_EnvironmentalHazardsMod.cs` (Mod Settings + Harmony rules), `Source/BiomeGlowPatches.cs`, `Source/RM_Patch_*.cs`.

## must be true
- Every def the mod ships (gas bases excepted: abstract) — damage/armor categories, stats, jobs, duties, think trees, work givers, the contact-venom hediff and damage, Venomvine, Leachmoss, flame statuary, shade gear — loads and resolves; a bogus name reads notFound. → defs_resolve.every_shipped_def_resolves
- Every Mod Settings field (`gasEmittersEnabled` … `hazardApparelAIAwarenessEnabled`, incl. `waterTruceRadius`, `waterTruceSuppressionEnabled`, `waterTruceRetributionEnabled`, `hazardDamageMultiplier`) round-trips get/set/get/restore. → settings_roundtrip.settings_probe_finds_fields, settings_roundtrip.<field>_round_trips for each field (the suite derives the list from the C#)
- The biome glow multiplier and the in-sunlight suppression are armed (Harmony postfixes on `GenCelestial.CurCelestialSunGlow` and `ConditionalStatAffecter_InSunlight.Applies`). → harmony_rules_armed.GenCelestial_CurCelestialSunGlow_postfix_armed, harmony_rules_armed.ConditionalStatAffecter_InSunlight_Applies_postfix_armed
- The body-size barrier routes and costs (prefix `PathFinder.CreateRequest`, postfix `Pawn_PathFollower.GetPawnCellBaseCostOverride`). → harmony_rules_armed.PathFinder_CreateRequest_prefix_armed, harmony_rules_armed.Pawn_PathFollower_GetPawnCellBaseCostOverride_postfix_armed
- The water-truce retribution and hunt suppression are armed (`Thing.PostApplyDamage`, `FoodUtility.IsAcceptablePreyFor`, `JobDriver_PredatorHunt.MakeNewToils`). → harmony_rules_armed.Thing_PostApplyDamage_postfix_armed, harmony_rules_armed.FoodUtility_IsAcceptablePreyFor_postfix_armed, harmony_rules_armed.JobDriver_PredatorHunt_MakeNewToils_postfix_armed
- The Leachmoss spawn gate (and pollination gate) is armed on `WildPlantSpawner.CalculatePlantsWhichCanGrowAt`. → harmony_rules_armed.WildPlantSpawner_CalculatePlantsWhichCanGrowAt_postfix_armed
- The biome-arrival letter rides `GenStep_GravshipMarker.Generate`; the creche-despoil factor rides `IncidentWorker.ChanceFactorNow`. → harmony_rules_armed.GenStep_GravshipMarker_Generate_postfix_armed, harmony_rules_armed.IncidentWorker_ChanceFactorNow_postfix_armed
- Live-prep viability, treasure-sale conscience, hazard-apparel AI scoring and the grazing hook are armed. → harmony_rules_armed.CompTemperatureRuinable_CompTick_prefix_armed, harmony_rules_armed.TradeDeal_TryExecute_prefix_armed, harmony_rules_armed.TradeDeal_TryExecute_postfix_armed, harmony_rules_armed.JobGiver_OptimizeApparel_ApparelScoreRaw_postfix_armed, harmony_rules_armed.Plant_IngestedCalculateAmounts_postfix_armed
- Contact venom is lethal at severity 1.0 (the threshold the lethal-off toggle holds under). → contact_venom_wiring.venom_hediff_is_lethal_at_one
- Gas emitters, gas effects, periodic area attacks, environmental weather, scaled explosions, water truce behaviour (incl. the radius override), boles/regrowth/tree-fall, stranding pools, tar/glasswalk, accelerated rot/warm ground, sheen/live-prep, venomvine scratch and barrier, and the world-generation scatterers act as their toggles say. → map_mechanics.* (UNMEASURED: each needs a content mod's def, a generated biome map, an incident or game days; the run may not drive them)
- Shade gear's heat and shade effect. → UNCOVERED: owned by CreatureBehaviors (shade grid) and the SOLAR_HEAT_EXPOSURE_1 / SHADE_GEAR_FAMILY_1 items; the defs resolve in defs_resolve
- No biome's tile count or painting. → UNCOVERED: the planet is painted once at the end (BIOME_PAINT_ONCE_AT_THE_END_1)

## the walk
1. [D] `jawa/get_defs` over every def derived from `Defs/**/*.xml` (batches of 40): `foundCount` equals the request, `notFound` empty; a bogus def reads notFound   # defs_resolve
2. [D] `jawa/mod_settings_field` get/set/get/restore on every scalar field of `RM_EnvironmentalHazardsSettings`   # settings_roundtrip
3. [D] `jawa/harmony_patches` per rule: postfix/prefix owner `mandrake.rm.environmentalhazards` with the named patch method; a nonexistent method reads no owner   # harmony_rules_armed
4. [D] `jawa/get_defs HediffDef/RM_VenomvineVenom fields lethalSeverity`   # contact_venom_wiring
5. [B] biome/map/incident/ticks mechanics   # map_mechanics (UNMEASURED until a drivable route exists)

## north star
state: DRAFT
validated-hash:

No owner north-star bars are drafted for this mod yet.

## anti-guessing notes
RULED OUT: "a rule that never armed would show in the defs" — a failed target logs `rule NOT armed` and the defs still load; harmony_rules_armed reads the live patch list instead.
RULED OUT: "an off toggle can be proven by reading its value back" — the round trip proves the field only; each toggle's effect needs its mechanism's map (map_mechanics, UNMEASURED).
RULED OUT: "the `public static` regex sees every setting" — `public const WaterTruceRadiusDefault` is deliberately excluded; waterTruceRadius (a static initialised from it) is asserted present by the probe.
