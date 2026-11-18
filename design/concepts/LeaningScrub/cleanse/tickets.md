# Proposed work tickets

These are proposed contracts, not filed ledger actions or implementation. Built extras retain source and defs. Each OFF/ON test uses a fresh disposable map and current composed build; no test requires DLC removal. A closed historical ledger item does not prove today’s runtime, and an open item does not prove code is missing. All defaults and tests below are this Designer’s decisions under the cleansing mandate.

## T1: Switch off stall_freeze

Retain code and defs. Add or use a per-feature setting labelled "Next version: stall_freeze", shipped OFF; reset defaults, static initializers, defs, settings writes and campaign patches must agree. This ticket gates the feature, not the species roster.

Production call-site search: src/RimMandrake/LeaningScrub/Source/RM_WindCalendar.cs:138: prefix: nameof(Wander_Prefix)); | src/RimMandrake/LeaningScrub/Source/RM_LeaningScrubMod.cs:47: public static bool stallFreezeEnabled = true;

Decouple: Gate every producer and effect at the listed callers. If this is a moved vine form, suppress its wildPlant row, island-room entry, forced placements, sowing/recipe exposure and regrowth; no unarmed lookalike remains at default. Kept code may reuse pure utilities but must not invoke the moved player behavior.

Acceptance test: Fresh full map, default settings and all kept mechanics on: this extra's generated things, custom jobs, letters, incidents and side effects are absent by state reads and the log is clean. For a behavior on a retained animal/material, the species/material remains but its extra job/effect is absent. Repeat with its labelled setting ON and actual preconditions (including optional dependency/faction when relevant): the things or behavior are present. Test reload and ON-to-OFF interruption without ghost queues, lost objects or a global engine disable. This is characterization, not a passing bar for next version.

## T2: Switch off gale_exposure

Retain code and defs. Add or use a per-feature setting labelled "Next version: gale_exposure", shipped OFF; reset defaults, static initializers, defs, settings writes and campaign patches must agree. This ticket gates the feature, not the species roster.

Production call-site search: src/RimMandrake/LeaningScrub/Source/RM_WindCalendar.cs:67: if (RM_WindCalendar.On(RM_LeaningScrubSettings.galeDeafenEnabled)) | src/RimMandrake/LeaningScrub/Source/RM_LeaningScrubMod.cs:49: public static bool galeDeafenEnabled = true;

Decouple: Gate every producer and effect at the listed callers. If this is a moved vine form, suppress its wildPlant row, island-room entry, forced placements, sowing/recipe exposure and regrowth; no unarmed lookalike remains at default. Kept code may reuse pure utilities but must not invoke the moved player behavior.

Acceptance test: Fresh full map, default settings and all kept mechanics on: this extra's generated things, custom jobs, letters, incidents and side effects are absent by state reads and the log is clean. For a behavior on a retained animal/material, the species/material remains but its extra job/effect is absent. Repeat with its labelled setting ON and actual preconditions (including optional dependency/faction when relevant): the things or behavior are present. Test reload and ON-to-OFF interruption without ghost queues, lost objects or a global engine disable. This is characterization, not a passing bar for next version.

## T3: Switch off gale_turbines

Retain code and defs. Add or use a per-feature setting labelled "Next version: gale_turbines", shipped OFF; reset defaults, static initializers, defs, settings writes and campaign patches must agree. This ticket gates the feature, not the species roster.

Production call-site search: src/RimMandrake/LeaningScrub/Source/RM_WindCalendar.cs:72: if (tick % TurbineInterval == 0 && RM_WindCalendar.On(RM_LeaningScrubSettings.galeTurbineSurgeEnabled)) | src/RimMandrake/LeaningScrub/Source/RM_LeaningScrubMod.cs:50: public static bool galeTurbineSurgeEnabled = true;

Decouple: Gate surge postfix AND breakdown scheduler; vanilla turbine output remains connected to actual wind.

Acceptance test: Fresh full map, default settings and all kept mechanics on: this extra's generated things, custom jobs, letters, incidents and side effects are absent by state reads and the log is clean. For a behavior on a retained animal/material, the species/material remains but its extra job/effect is absent. Repeat with its labelled setting ON and actual preconditions (including optional dependency/faction when relevant): the things or behavior are present. Test reload and ON-to-OFF interruption without ghost queues, lost objects or a global engine disable. This is characterization, not a passing bar for next version.

## T4: Switch off gale_raid_weight

Retain code and defs. Add or use a per-feature setting labelled "Next version: gale_raid_weight", shipped OFF; reset defaults, static initializers, defs, settings writes and campaign patches must agree. This ticket gates the feature, not the species roster.

Production call-site search: src/RimMandrake/LeaningScrub/Source/RM_WindCalendar.cs:206: if (RM_WindCalendar.On(RM_LeaningScrubSettings.galeRaidWeightingEnabled) && RM_WindCalendar.IsGale(map)) | src/RimMandrake/LeaningScrub/Source/RM_LeaningScrubMod.cs:53: public static bool galeRaidWeightingEnabled = true;

Decouple: Gate every producer and effect at the listed callers. If this is a moved vine form, suppress its wildPlant row, island-room entry, forced placements, sowing/recipe exposure and regrowth; no unarmed lookalike remains at default. Kept code may reuse pure utilities but must not invoke the moved player behavior.

Acceptance test: Fresh full map, default settings and all kept mechanics on: this extra's generated things, custom jobs, letters, incidents and side effects are absent by state reads and the log is clean. For a behavior on a retained animal/material, the species/material remains but its extra job/effect is absent. Repeat with its labelled setting ON and actual preconditions (including optional dependency/faction when relevant): the things or behavior are present. Test reload and ON-to-OFF interruption without ghost queues, lost objects or a global engine disable. This is characterization, not a passing bar for next version.

## T5: Switch off upwind_scent

Retain code and defs. Add or use a per-feature setting labelled "Next version: upwind_scent", shipped OFF; reset defaults, static initializers, defs, settings writes and campaign patches must agree. This ticket gates the feature, not the species roster.

Production call-site search: src/RimMandrake/LeaningScrub/Source/RM_TheLean.cs:211: || !RM_LeaningScrubSettings.leanScentEnabled) | src/RimMandrake/LeaningScrub/Source/RM_LeaningScrubMod.cs:68: public static bool leanScentEnabled = true; | src/RimMandrake/LeaningScrub/Source/RM_TheLeanProof.cs:170: savedScent = RM_LeaningScrubSettings.leanScentEnabled;

Decouple: Gate every producer and effect at the listed callers. If this is a moved vine form, suppress its wildPlant row, island-room entry, forced placements, sowing/recipe exposure and regrowth; no unarmed lookalike remains at default. Kept code may reuse pure utilities but must not invoke the moved player behavior.

Acceptance test: Fresh full map, default settings and all kept mechanics on: this extra's generated things, custom jobs, letters, incidents and side effects are absent by state reads and the log is clean. For a behavior on a retained animal/material, the species/material remains but its extra job/effect is absent. Repeat with its labelled setting ON and actual preconditions (including optional dependency/faction when relevant): the things or behavior are present. Test reload and ON-to-OFF interruption without ghost queues, lost objects or a global engine disable. This is characterization, not a passing bar for next version.

## T6: Switch off downwind_fire

Retain code and defs. Add or use a per-feature setting labelled "Next version: downwind_fire", shipped OFF; reset defaults, static initializers, defs, settings writes and campaign patches must agree. This ticket gates the feature, not the species roster.

Production call-site search: src/RimMandrake/LeaningScrub/Source/RM_TheLean.cs:256: if (!RM_LeaningScrubSettings.leanFireEnabled) | src/RimMandrake/LeaningScrub/Source/RM_LeaningScrubMod.cs:70: public static bool leanFireEnabled = true; | src/RimMandrake/LeaningScrub/Source/RM_TheLeanProof.cs:251: RM_LeaningScrubSettings.leanFireEnabled = leanOn;

Decouple: Gate every producer and effect at the listed callers. If this is a moved vine form, suppress its wildPlant row, island-room entry, forced placements, sowing/recipe exposure and regrowth; no unarmed lookalike remains at default. Kept code may reuse pure utilities but must not invoke the moved player behavior.

Acceptance test: Fresh full map, default settings and all kept mechanics on: this extra's generated things, custom jobs, letters, incidents and side effects are absent by state reads and the log is clean. For a behavior on a retained animal/material, the species/material remains but its extra job/effect is absent. Repeat with its labelled setting ON and actual preconditions (including optional dependency/faction when relevant): the things or behavior are present. Test reload and ON-to-OFF interruption without ghost queues, lost objects or a global engine disable. This is characterization, not a passing bar for next version.

## T7: Switch off ripple

Retain code and defs. Add or use a per-feature setting labelled "Next version: ripple", shipped OFF; reset defaults, static initializers, defs, settings writes and campaign patches must agree. This ticket gates the feature, not the species roster.

Production call-site search: src/RimMandrake/LeaningScrub/Source/RM_Ripple.cs:27: public class RM_RippleCoverExtension : DefModExtension | src/RimMandrake/LeaningScrub/Source/RM_LeaningScrubDefOf.cs:15: public static HediffDef RM_RippleHidden; | src/RimMandrake/LeaningScrub/Source/RM_StallHunt.cs:158: bool savedMod = RM_LeaningScrubSettings.modEnabled, savedHunt = RM_LeaningScrubSettings.stallHuntEnabled, savedRipple = RM_LeaningScrubSettings.rippleEnabled; | src/RimMandrake/LeaningScrub/Source/RM_LeaningScrubMod.cs:109: public static bool rippleEnabled = true; | src/RimMandrake/LeaningScrub/Patches/RM_Ripple_Cover.xml:3: RM_Ripple_Cover.xml   LEANINGSCRUB_MECHANICS_BUILD_1 part 6 - the ripple. | src/RimMandrake/LeaningScrub/Source/Kernel/RM_RippleKernel.cs:11: public static class RM_RippleKernel | src/RimMandrake/LeaningScrub/Defs/HediffDefs/RM_LeaningScrub_Ripple.xml:3: LEANINGSCRUB_MECHANICS_BUILD_1 part 6 - the ripple (Source/RM_Ripple.cs adds and removes it). | src/RimMandrake/LeaningScrub/Defs/ThingDefs_Races/RM_LeaningScrubFauna.xml:640: (RM_Ripple.cs: a wild creature within rippleMaxBodySize on fuzz cover is hidden in wind, moving or not; in the Stall a

Decouple: Gate invisibility application, targeting exclusion and rendering together; remove existing hidden condition with a readable reveal. Cover stats and real flight remain independent.

Acceptance test: Fresh full map, default settings and all kept mechanics on: this extra's generated things, custom jobs, letters, incidents and side effects are absent by state reads and the log is clean. For a behavior on a retained animal/material, the species/material remains but its extra job/effect is absent. Repeat with its labelled setting ON and actual preconditions (including optional dependency/faction when relevant): the things or behavior are present. Test reload and ON-to-OFF interruption without ghost queues, lost objects or a global engine disable. This is characterization, not a passing bar for next version.

## T8: Switch off windbreak_lee

Retain code and defs. Add or use a per-feature setting labelled "Next version: windbreak_lee", shipped OFF; reset defaults, static initializers, defs, settings writes and campaign patches must agree. This ticket gates the feature, not the species roster.

Production call-site search: src/RimMandrake/LeaningScrub/Source/RM_Ripple.cs:65: bool still = stall || (on && cover && InWindbreakLee(p.Position)); | src/RimMandrake/LeaningScrub/Source/RM_LeaningScrubMod.cs:73: public static bool leanWakesEnabled = true;

Decouple: Gate every producer and effect at the listed callers. If this is a moved vine form, suppress its wildPlant row, island-room entry, forced placements, sowing/recipe exposure and regrowth; no unarmed lookalike remains at default. Kept code may reuse pure utilities but must not invoke the moved player behavior.

Acceptance test: Fresh full map, default settings and all kept mechanics on: this extra's generated things, custom jobs, letters, incidents and side effects are absent by state reads and the log is clean. For a behavior on a retained animal/material, the species/material remains but its extra job/effect is absent. Repeat with its labelled setting ON and actual preconditions (including optional dependency/faction when relevant): the things or behavior are present. Test reload and ON-to-OFF interruption without ghost queues, lost objects or a global engine disable. This is characterization, not a passing bar for next version.

## T9: Switch off stall_hunter

Retain code and defs. Add or use a per-feature setting labelled "Next version: stall_hunter", shipped OFF; reset defaults, static initializers, defs, settings writes and campaign patches must agree. This ticket gates the feature, not the species roster.

Production call-site search: src/RimMandrake/LeaningScrub/Source/RM_StallHunt.cs:24: public class RM_StallHunterExtension : DefModExtension | src/RimMandrake/LeaningScrub/Source/RM_LeaningScrubMod.cs:112: public static bool stallHuntEnabled = true; | src/RimMandrake/LeaningScrub/Defs/ThingDefs_Races/RM_LeaningScrubFauna.xml:399: <li Class="RimMandrake.LeaningScrub.RM_StallHunterExtension" />

Decouple: Gate every producer and effect at the listed callers. If this is a moved vine form, suppress its wildPlant row, island-room entry, forced placements, sowing/recipe exposure and regrowth; no unarmed lookalike remains at default. Kept code may reuse pure utilities but must not invoke the moved player behavior.

Acceptance test: Fresh full map, default settings and all kept mechanics on: this extra's generated things, custom jobs, letters, incidents and side effects are absent by state reads and the log is clean. For a behavior on a retained animal/material, the species/material remains but its extra job/effect is absent. Repeat with its labelled setting ON and actual preconditions (including optional dependency/faction when relevant): the things or behavior are present. Test reload and ON-to-OFF interruption without ghost queues, lost objects or a global engine disable. This is characterization, not a passing bar for next version.

## T10: Switch off twitcher

Retain code and defs. Add or use a per-feature setting labelled "Next version: twitcher", shipped OFF; reset defaults, static initializers, defs, settings writes and campaign patches must agree. This ticket gates the feature, not the species roster.

Production call-site search: src/RimMandrake/LeaningScrub/Source/RM_TwitcherLash.cs:25: public class RM_CompProperties_Lash : CompProperties | src/RimMandrake/LeaningScrub/Source/RM_LeaningScrubMod.cs:57: public static bool twitcherLashEnabled = true; | src/RimMandrake/LeaningScrub/Defs/ThingDefs_Plants/RM_LeaningScrubVenomvineForms.xml:10: (RM_CompProperties_Lash), the dripping stand's regrowing harvest

Decouple: Gate every producer and effect at the listed callers. If this is a moved vine form, suppress its wildPlant row, island-room entry, forced placements, sowing/recipe exposure and regrowth; no unarmed lookalike remains at default. Kept code may reuse pure utilities but must not invoke the moved player behavior.

Acceptance test: Fresh full map, default settings and all kept mechanics on: this extra's generated things, custom jobs, letters, incidents and side effects are absent by state reads and the log is clean. For a behavior on a retained animal/material, the species/material remains but its extra job/effect is absent. Repeat with its labelled setting ON and actual preconditions (including optional dependency/faction when relevant): the things or behavior are present. Test reload and ON-to-OFF interruption without ghost queues, lost objects or a global engine disable. This is characterization, not a passing bar for next version.

## T11: Switch off crown_mob

Retain code and defs. Add or use a per-feature setting labelled "Next version: crown_mob", shipped OFF; reset defaults, static initializers, defs, settings writes and campaign patches must agree. This ticket gates the feature, not the species roster.

Production call-site search: src/RimMandrake/LeaningScrub/Source/RM_VenomvineRooms.cs:72: public class RM_StallMobExtension : DefModExtension | src/RimMandrake/LeaningScrub/Source/RM_LeaningScrubMod.cs:83: public static bool crownMobEnabled = true; | src/RimMandrake/LeaningScrub/Defs/ThingDefs_Plants/RM_LeaningScrubVenomvineForms.xml:11: (RM_RegrowingHarvestExtension) and the crown's Stall mob (RM_StallMobExtension).

Decouple: Filter Crown from random wild flora, island rooms and forced crown heart placement; gate gathering. No kept flyer relies on crown to start flight.

Acceptance test: Fresh full map, default settings and all kept mechanics on: this extra's generated things, custom jobs, letters, incidents and side effects are absent by state reads and the log is clean. For a behavior on a retained animal/material, the species/material remains but its extra job/effect is absent. Repeat with its labelled setting ON and actual preconditions (including optional dependency/faction when relevant): the things or behavior are present. Test reload and ON-to-OFF interruption without ghost queues, lost objects or a global engine disable. This is characterization, not a passing bar for next version.

## T12: Switch off rearing

Retain code and defs. Add or use a per-feature setting labelled "Next version: rearing", shipped OFF; reset defaults, static initializers, defs, settings writes and campaign patches must agree. This ticket gates the feature, not the species roster.

Production call-site search: src/RimMandrake/LeaningScrub/Source/RM_VenomvineForms.cs:112: public class RM_CompProperties_Rearing : CompProperties | src/RimMandrake/LeaningScrub/Source/RM_LeaningScrubMod.cs:126: public static bool rearingEnabled = true; | src/RimMandrake/LeaningScrub/Defs/ThingDefs_Plants/RM_VenomvineSixForms.xml:78: <li Class="RimMandrake.LeaningScrub.RM_CompProperties_Rearing">

Decouple: Gate every producer and effect at the listed callers. If this is a moved vine form, suppress its wildPlant row, island-room entry, forced placements, sowing/recipe exposure and regrowth; no unarmed lookalike remains at default. Kept code may reuse pure utilities but must not invoke the moved player behavior.

Acceptance test: Fresh full map, default settings and all kept mechanics on: this extra's generated things, custom jobs, letters, incidents and side effects are absent by state reads and the log is clean. For a behavior on a retained animal/material, the species/material remains but its extra job/effect is absent. Repeat with its labelled setting ON and actual preconditions (including optional dependency/faction when relevant): the things or behavior are present. Test reload and ON-to-OFF interruption without ghost queues, lost objects or a global engine disable. This is characterization, not a passing bar for next version.

## T13: Switch off walking

Retain code and defs. Add or use a per-feature setting labelled "Next version: walking", shipped OFF; reset defaults, static initializers, defs, settings writes and campaign patches must agree. This ticket gates the feature, not the species roster.

Production call-site search: src/RimMandrake/LeaningScrub/Source/RM_VenomvineForms.cs:156: public class RM_CompProperties_Walking : CompProperties | src/RimMandrake/LeaningScrub/Source/RM_LeaningScrubMod.cs:128: public static bool walkingEnabled = true; | src/RimMandrake/LeaningScrub/Defs/ThingDefs_Plants/RM_VenomvineSixForms.xml:147: <li Class="RimMandrake.LeaningScrub.RM_CompProperties_Walking">

Decouple: Filter Walking from wildPlants, island room selection and regeneration while off; keep the common creep counted-set explicit. No Walking output or tail cane may supplement kept claim income.

Acceptance test: Fresh full map, default settings and all kept mechanics on: this extra's generated things, custom jobs, letters, incidents and side effects are absent by state reads and the log is clean. For a behavior on a retained animal/material, the species/material remains but its extra job/effect is absent. Repeat with its labelled setting ON and actual preconditions (including optional dependency/faction when relevant): the things or behavior are present. Test reload and ON-to-OFF interruption without ghost queues, lost objects or a global engine disable. This is characterization, not a passing bar for next version.

## T14: Switch off hoard

Retain code and defs. Add or use a per-feature setting labelled "Next version: hoard", shipped OFF; reset defaults, static initializers, defs, settings writes and campaign patches must agree. This ticket gates the feature, not the species roster.

Production call-site search: src/RimMandrake/LeaningScrub/Source/RM_VenomvineForms.cs:249: public class RM_CompProperties_Hoard : CompProperties | src/RimMandrake/LeaningScrub/Source/RM_LeaningScrubMod.cs:130: public static bool hoardEnabled = true; | src/RimMandrake/LeaningScrub/Defs/ThingDefs_Plants/RM_VenomvineSixForms.xml:215: <li Class="RimMandrake.LeaningScrub.RM_CompProperties_Hoard">

Decouple: Remove Hoard plant spawns and all object-taking sweeps while off; kept fuel/venom rewards use no hoard store. On deactivation return held objects with a readable sign, never destroy carried gear.

Acceptance test: Fresh full map, default settings and all kept mechanics on: this extra's generated things, custom jobs, letters, incidents and side effects are absent by state reads and the log is clean. For a behavior on a retained animal/material, the species/material remains but its extra job/effect is absent. Repeat with its labelled setting ON and actual preconditions (including optional dependency/faction when relevant): the things or behavior are present. Test reload and ON-to-OFF interruption without ghost queues, lost objects or a global engine disable. This is characterization, not a passing bar for next version.

## T15: Switch off quench

Retain code and defs. Add or use a per-feature setting labelled "Next version: quench", shipped OFF; reset defaults, static initializers, defs, settings writes and campaign patches must agree. This ticket gates the feature, not the species roster.

Production call-site search: src/RimMandrake/LeaningScrub/Source/RM_VenomvineForms.cs:193: public class RM_CompProperties_Quench : CompProperties | src/RimMandrake/LeaningScrub/Source/RM_LeaningScrubMod.cs:133: public static bool quenchEnabled = true; | src/RimMandrake/LeaningScrub/Defs/ThingDefs_Plants/RM_VenomvineSixForms.xml:280: <li Class="RimMandrake.LeaningScrub.RM_CompProperties_Quench">

Decouple: Gate every producer and effect at the listed callers. If this is a moved vine form, suppress its wildPlant row, island-room entry, forced placements, sowing/recipe exposure and regrowth; no unarmed lookalike remains at default. Kept code may reuse pure utilities but must not invoke the moved player behavior.

Acceptance test: Fresh full map, default settings and all kept mechanics on: this extra's generated things, custom jobs, letters, incidents and side effects are absent by state reads and the log is clean. For a behavior on a retained animal/material, the species/material remains but its extra job/effect is absent. Repeat with its labelled setting ON and actual preconditions (including optional dependency/faction when relevant): the things or behavior are present. Test reload and ON-to-OFF interruption without ghost queues, lost objects or a global engine disable. This is characterization, not a passing bar for next version.

## T16: Switch off sworn

Retain code and defs. Add or use a per-feature setting labelled "Next version: sworn", shipped OFF; reset defaults, static initializers, defs, settings writes and campaign patches must agree. This ticket gates the feature, not the species roster.

Production call-site search: src/RimMandrake/LeaningScrub/Source/RM_VenomvineForms.cs:83: && RM_WindCalendar.On(RM_LeaningScrubSettings.swornSparesMarkedEnabled) | src/RimMandrake/LeaningScrub/Source/RM_LeaningScrubMod.cs:135: public static bool swornSparesMarkedEnabled = true; | src/RimMandrake/LeaningScrub/Defs/ThingDefs_Plants/RM_VenomvineSixForms.xml:297: spare any pawn carrying RM_SwornSapMarked, whoever they are (owner ruling 2026-10-03). | src/RimMandrake/LeaningScrub/Defs/ThingDefs_Items/RM_VenomvineFormSupport.xml:9: RM_SwornSapMark      a pot of anointing made from the dripping stand's RM_RawVenom.

Decouple: Filter wild/sown Sworn, research/recipes and sap-mark item menus; gate marked-thorn exemption without affecting the kept thicket barrier.

Acceptance test: Fresh full map, default settings and all kept mechanics on: this extra's generated things, custom jobs, letters, incidents and side effects are absent by state reads and the log is clean. For a behavior on a retained animal/material, the species/material remains but its extra job/effect is absent. Repeat with its labelled setting ON and actual preconditions (including optional dependency/faction when relevant): the things or behavior are present. Test reload and ON-to-OFF interruption without ghost queues, lost objects or a global engine disable. This is characterization, not a passing bar for next version.

## T17: Switch off shedding

Retain code and defs. Add or use a per-feature setting labelled "Next version: shedding", shipped OFF; reset defaults, static initializers, defs, settings writes and campaign patches must agree. This ticket gates the feature, not the species roster.

Production call-site search: src/RimMandrake/LeaningScrub/Source/RM_VenomvineForms.cs:175: public class RM_CompProperties_Shedding : CompProperties | src/RimMandrake/LeaningScrub/Source/RM_LeaningScrubMod.cs:136: public static bool sheddingEnabled = true; | src/RimMandrake/LeaningScrub/Defs/ThingDefs_Plants/RM_VenomvineSixForms.xml:418: <li Class="RimMandrake.LeaningScrub.RM_CompProperties_Shedding">

Decouple: Filter Shedding plant spawns and litter creation/damage; clear its pending fan queue on off, never count litter as kept vines.

Acceptance test: Fresh full map, default settings and all kept mechanics on: this extra's generated things, custom jobs, letters, incidents and side effects are absent by state reads and the log is clean. For a behavior on a retained animal/material, the species/material remains but its extra job/effect is absent. Repeat with its labelled setting ON and actual preconditions (including optional dependency/faction when relevant): the things or behavior are present. Test reload and ON-to-OFF interruption without ghost queues, lost objects or a global engine disable. This is characterization, not a passing bar for next version.

## T18: Switch off strangler

Retain code and defs. Add or use a per-feature setting labelled "Next version: strangler", shipped OFF; reset defaults, static initializers, defs, settings writes and campaign patches must agree. This ticket gates the feature, not the species roster.

Production call-site search: src/RimMandrake/LeaningScrub/Source/RM_VenomvineFourForms.cs:20: public class RM_CompProperties_Strangler : CompProperties | src/RimMandrake/LeaningScrub/Source/RM_LeaningScrubMod.cs:138: public static bool stranglerEnabled = true; | src/RimMandrake/LeaningScrub/Defs/ThingDefs_Plants/RM_VenomvineFourForms.xml:64: <li Class="RimMandrake.LeaningScrub.RM_CompProperties_Strangler">

Decouple: Gate every producer and effect at the listed callers. If this is a moved vine form, suppress its wildPlant row, island-room entry, forced placements, sowing/recipe exposure and regrowth; no unarmed lookalike remains at default. Kept code may reuse pure utilities but must not invoke the moved player behavior.

Acceptance test: Fresh full map, default settings and all kept mechanics on: this extra's generated things, custom jobs, letters, incidents and side effects are absent by state reads and the log is clean. For a behavior on a retained animal/material, the species/material remains but its extra job/effect is absent. Repeat with its labelled setting ON and actual preconditions (including optional dependency/faction when relevant): the things or behavior are present. Test reload and ON-to-OFF interruption without ghost queues, lost objects or a global engine disable. This is characterization, not a passing bar for next version.

## T19: Switch off weeper

Retain code and defs. Add or use a per-feature setting labelled "Next version: weeper", shipped OFF; reset defaults, static initializers, defs, settings writes and campaign patches must agree. This ticket gates the feature, not the species roster.

Production call-site search: src/RimMandrake/LeaningScrub/Source/RM_VenomvineFourForms.cs:117: public class RM_CompProperties_Weeper : CompProperties | src/RimMandrake/LeaningScrub/Source/RM_LeaningScrubMod.cs:141: public static bool weeperEnabled = true; | src/RimMandrake/LeaningScrub/Defs/ThingDefs_Plants/RM_VenomvineFourForms.xml:127: <li Class="RimMandrake.LeaningScrub.RM_CompProperties_Weeper">

Decouple: Filter Weeper plant spawns and pool/pollution emission; do not zero shared EnvironmentalHazards controls to hide it.

Acceptance test: Fresh full map, default settings and all kept mechanics on: this extra's generated things, custom jobs, letters, incidents and side effects are absent by state reads and the log is clean. For a behavior on a retained animal/material, the species/material remains but its extra job/effect is absent. Repeat with its labelled setting ON and actual preconditions (including optional dependency/faction when relevant): the things or behavior are present. Test reload and ON-to-OFF interruption without ghost queues, lost objects or a global engine disable. This is characterization, not a passing bar for next version.

## T20: Switch off sleeper

Retain code and defs. Add or use a per-feature setting labelled "Next version: sleeper", shipped OFF; reset defaults, static initializers, defs, settings writes and campaign patches must agree. This ticket gates the feature, not the species roster.

Production call-site search: src/RimMandrake/LeaningScrub/Source/RM_VenomvineFourForms.cs:172: public class RM_CompProperties_Sleeper : CompProperties | src/RimMandrake/LeaningScrub/Source/RM_LeaningScrubMod.cs:143: public static bool sleeperEnabled = true; | src/RimMandrake/LeaningScrub/Defs/ThingDefs_Plants/RM_VenomvineFourForms.xml:179: <li Class="RimMandrake.LeaningScrub.RM_CompProperties_Sleeper">

Decouple: Filter dormant and awake plants from fresh-map spawn paths and stop traffic activation; gate wake damage, not just replacement.

Acceptance test: Fresh full map, default settings and all kept mechanics on: this extra's generated things, custom jobs, letters, incidents and side effects are absent by state reads and the log is clean. For a behavior on a retained animal/material, the species/material remains but its extra job/effect is absent. Repeat with its labelled setting ON and actual preconditions (including optional dependency/faction when relevant): the things or behavior are present. Test reload and ON-to-OFF interruption without ghost queues, lost objects or a global engine disable. This is characterization, not a passing bar for next version.

## T21: Switch off lure

Retain code and defs. Add or use a per-feature setting labelled "Next version: lure", shipped OFF; reset defaults, static initializers, defs, settings writes and campaign patches must agree. This ticket gates the feature, not the species roster.

Production call-site search: src/RimMandrake/LeaningScrub/Source/RM_VenomvineFourForms.cs:274: public class RM_CompProperties_Lure : CompProperties | src/RimMandrake/LeaningScrub/Source/RM_LeaningScrubMod.cs:144: public static bool lureEnabled = true; | src/RimMandrake/LeaningScrub/Defs/ThingDefs_Plants/RM_VenomvineFourForms.xml:295: <li Class="RimMandrake.LeaningScrub.RM_CompProperties_Lure">

Decouple: Gate every producer and effect at the listed callers. If this is a moved vine form, suppress its wildPlant row, island-room entry, forced placements, sowing/recipe exposure and regrowth; no unarmed lookalike remains at default. Kept code may reuse pure utilities but must not invoke the moved player behavior.

Acceptance test: Fresh full map, default settings and all kept mechanics on: this extra's generated things, custom jobs, letters, incidents and side effects are absent by state reads and the log is clean. For a behavior on a retained animal/material, the species/material remains but its extra job/effect is absent. Repeat with its labelled setting ON and actual preconditions (including optional dependency/faction when relevant): the things or behavior are present. Test reload and ON-to-OFF interruption without ghost queues, lost objects or a global engine disable. This is characterization, not a passing bar for next version.

## T22: Switch off felt_comfort

Retain code and defs. Add or use a per-feature setting labelled "Next version: felt_comfort", shipped OFF; reset defaults, static initializers, defs, settings writes and campaign patches must agree. This ticket gates the feature, not the species roster.

Production call-site search: src/RimMandrake/LeaningScrub/Source/RM_SweetlineFelt.cs:21: public class RM_StuffComfortExtension : DefModExtension | src/RimMandrake/LeaningScrub/Source/RM_LeaningScrubMod.cs:96: public static bool sweetlineFeltApparelEnabled = true; | src/RimMandrake/LeaningScrub/Patches/RM_StuffComfort_StatPart.xml:5: RM_StuffComfortExtension.comfortOffset. Inert for every stuff without the extension. --> | src/RimMandrake/LeaningScrub/Defs/ThingDefs_Items/RM_SweetlineTree_Items.xml:40: <li Class="RimMandrake.LeaningScrub.RM_StuffComfortExtension"> | src/RimMandrake/LeaningScrub/Defs/ThoughtDefs/RM_SweetlineFelt_Thoughts.xml:3: stacked per piece" (spec §5). Fires for any stuff carrying RM_StuffComfortExtension. -->

Decouple: Gate both the comfort patch and apparel-thought patch; keep stuff/blanket use and ordinary material properties.

Acceptance test: Fresh full map, default settings and all kept mechanics on: this extra's generated things, custom jobs, letters, incidents and side effects are absent by state reads and the log is clean. For a behavior on a retained animal/material, the species/material remains but its extra job/effect is absent. Repeat with its labelled setting ON and actual preconditions (including optional dependency/faction when relevant): the things or behavior are present. Test reload and ON-to-OFF interruption without ghost queues, lost objects or a global engine disable. This is characterization, not a passing bar for next version.

## T23: Switch off sweetline_visits

Retain code and defs. Add or use a per-feature setting labelled "Next version: sweetline_visits", shipped OFF; reset defaults, static initializers, defs, settings writes and campaign patches must agree. This ticket gates the feature, not the species roster.

Production call-site search: src/RimMandrake/LeaningScrub/Source/RM_LeaningScrubMod.cs:86: public static bool sweetlineVisitorsEnabled = true; | src/RimMandrake/LeaningScrub/Source/RM_SweetlineStation.cs:89: private static bool VisitorsOn => Enabled && RM_LeaningScrubSettings.sweetlineVisitorsEnabled;

Decouple: Gate Visit and token/ash creation without switching off tree registration, naming, wool, scratching, bank payout or healing.

Acceptance test: Fresh full map, default settings and all kept mechanics on: this extra's generated things, custom jobs, letters, incidents and side effects are absent by state reads and the log is clean. For a behavior on a retained animal/material, the species/material remains but its extra job/effect is absent. Repeat with its labelled setting ON and actual preconditions (including optional dependency/faction when relevant): the things or behavior are present. Test reload and ON-to-OFF interruption without ghost queues, lost objects or a global engine disable. This is characterization, not a passing bar for next version.

## T24: Switch off runway_bloom

Retain code and defs. Add or use a per-feature setting labelled "Next version: runway_bloom", shipped OFF; reset defaults, static initializers, defs, settings writes and campaign patches must agree. This ticket gates the feature, not the species roster.

Production call-site search: src/RimMandrake/LeaningScrub/Source/RM_RunwayBloom.cs:50: public class RM_RunwayBloomExtension : DefModExtension | src/RimMandrake/LeaningScrub/Source/RM_LeaningScrubMod.cs:84: public static bool runwayBloomEnabled = true; | src/RimMandrake/LeaningScrub/Defs/ThingDefs_Races/RM_LeaningScrubFauna.xml:79: <li Class="RimMandrake.LeaningScrub.RM_RunwayBloomExtension"> | src/RimMandrake/LeaningScrub/Defs/ThingDefs_Misc/RM_SurrikExitHole.xml:5: (RM_RunwayBloomExtension response Surface, Source/RM_RunwayBloom.cs). PLACEHOLDER ART: vanilla rock

Decouple: Gate both traffic detection and queued answers; drop pending answers safely. Shirrel/dustflutter real flight must still start through their ordinary movement AI, without calling bloom.

Acceptance test: Fresh full map, default settings and all kept mechanics on: this extra's generated things, custom jobs, letters, incidents and side effects are absent by state reads and the log is clean. For a behavior on a retained animal/material, the species/material remains but its extra job/effect is absent. Repeat with its labelled setting ON and actual preconditions (including optional dependency/faction when relevant): the things or behavior are present. Test reload and ON-to-OFF interruption without ghost queues, lost objects or a global engine disable. This is characterization, not a passing bar for next version.

## T25: Switch off vissler_arm_food

Retain code and defs. Add or use a per-feature setting labelled "Next version: vissler_arm_food", shipped OFF; reset defaults, static initializers, defs, settings writes and campaign patches must agree. This ticket gates the feature, not the species roster.

Production call-site search: src/RimMandrake/LeaningScrub/Source/RM_LeaningScrubMod.cs:98: public static bool visslerArmFoodEnabled = true; | src/RimMandrake/LeaningScrub/Source/RM_VisslerArm.cs:13: public static class RM_VisslerArmPatches | src/RimMandrake/LeaningScrub/Defs/ThingDefs_Races/RM_LeaningScrubFauna.xml:773: <RM_VisslerArm>1</RM_VisslerArm> | src/RimMandrake/LeaningScrub/Defs/ThingDefs_Items/RM_LeaningScrubItems.xml:6: RM_VisslerArm  the shed arm of RM_Vissler (butcher product of the animal).

Decouple: Gate the food-search postfix and arm item creation together with the bloom setting; no arm product is a required diet or blanket ingredient.

Acceptance test: Fresh full map, default settings and all kept mechanics on: this extra's generated things, custom jobs, letters, incidents and side effects are absent by state reads and the log is clean. For a behavior on a retained animal/material, the species/material remains but its extra job/effect is absent. Repeat with its labelled setting ON and actual preconditions (including optional dependency/faction when relevant): the things or behavior are present. Test reload and ON-to-OFF interruption without ghost queues, lost objects or a global engine disable. This is characterization, not a passing bar for next version.

## T26: Switch off thornhold_den_stand

Retain code and defs. Add or use a per-feature setting labelled "Next version: thornhold_den_stand", shipped OFF; reset defaults, static initializers, defs, settings writes and campaign patches must agree. This ticket gates the feature, not the species roster.

Production call-site search: src/RimMandrake/LeaningScrub/Source/RM_ScrubDens.cs:53: public class RM_CompProperties_VineDen : CompProperties | src/RimMandrake/LeaningScrub/Source/RM_LeaningScrubMod.cs:101: public static bool thornholdStandEnabled = true; | src/RimMandrake/LeaningScrub/Defs/ThingDefs_Races/RM_LeaningScrubFauna.xml:124: safe. ContactVenomImmunity: its own den does not poison it. Mod Settings: thornholdDenEnabled, thornholdStandEnabled. -->

Decouple: Gate den choice, HomeTether binding and the damage-triggered stand response together; keep inherent melee/venom and normal predator logic.

Acceptance test: Fresh full map, default settings and all kept mechanics on: this extra's generated things, custom jobs, letters, incidents and side effects are absent by state reads and the log is clean. For a behavior on a retained animal/material, the species/material remains but its extra job/effect is absent. Repeat with its labelled setting ON and actual preconditions (including optional dependency/faction when relevant): the things or behavior are present. Test reload and ON-to-OFF interruption without ghost queues, lost objects or a global engine disable. This is characterization, not a passing bar for next version.

## T27: Switch off surrik_crustswim

Retain code and defs. Add or use a per-feature setting labelled "Next version: surrik_crustswim", shipped OFF; reset defaults, static initializers, defs, settings writes and campaign patches must agree. This ticket gates the feature, not the species roster.

Production call-site search: src/RimMandrake/LeaningScrub/Source/RM_Ripple.cs:44: && def.HasModExtension<RimMandrake.CreatureBehaviors.RM_SandSwimExtension>(); | src/RimMandrake/LeaningScrub/Defs/HediffDefs/RM_LeaningScrub_Surrik.xml:6: Movement is CreatureBehaviors' sand-swim kit (RM_SandSwimExtension on the race, worker comp injected at startup), | src/RimMandrake/LeaningScrub/Defs/ThingDefs_Races/RM_LeaningScrubFauna.xml:525: sand-swim kit (RM_SandSwimExtension below), retuned to the crust: it swims the Scrub's own natural ground (Sand, Soil, | src/RimMandrake/CreatureBehaviors/Source/RM_CompSandSwim.cs:41: private RM_SandSwimExtension extCached; | src/RimMandrake/CreatureBehaviors/Source/RM_SandSwimExtension.cs:15: public class RM_SandSwimExtension : DefModExtension | src/RimMandrake/CreatureBehaviors/Defs/HediffDefs/RM_SandSwim_Hediffs.xml:5: The two hediffs RM_CompSandSwim manages. Any RM_SandSwimExtension may point at these

Decouple: Add a LeaningScrub-local opt-in gate to this species extension; do not switch off CreatureBehaviors globally or remove the species. Deferred ripple/bloom must not force a hidden state when swimming is off.

Acceptance test: Fresh full map, default settings and all kept mechanics on: this extra's generated things, custom jobs, letters, incidents and side effects are absent by state reads and the log is clean. For a behavior on a retained animal/material, the species/material remains but its extra job/effect is absent. Repeat with its labelled setting ON and actual preconditions (including optional dependency/faction when relevant): the things or behavior are present. Test reload and ON-to-OFF interruption without ghost queues, lost objects or a global engine disable. This is characterization, not a passing bar for next version.

## T28: Switch off ribbonwhip_wind_concealment

Retain code and defs. Add or use a per-feature setting labelled "Next version: ribbonwhip_wind_concealment", shipped OFF; reset defaults, static initializers, defs, settings writes and campaign patches must agree. This ticket gates the feature, not the species roster.

Production call-site search: src/RimMandrake/LeaningScrub/Defs/BiomeDefs/RM_LeaningScrub_Biome.xml:179: <RM_Ribbonwhip>0.3</RM_Ribbonwhip> | src/RimMandrake/LeaningScrub/Defs/ThingDefs_Races/RM_LeaningScrubFauna.xml:644: <defName>RM_Ribbonwhip</defName>

Decouple: The same ripple gate also covers ribbonwhip-specific special cases; keep the animal and its ordinary AI.

Acceptance test: Fresh full map, default settings and all kept mechanics on: this extra's generated things, custom jobs, letters, incidents and side effects are absent by state reads and the log is clean. For a behavior on a retained animal/material, the species/material remains but its extra job/effect is absent. Repeat with its labelled setting ON and actual preconditions (including optional dependency/faction when relevant): the things or behavior are present. Test reload and ON-to-OFF interruption without ghost queues, lost objects or a global engine disable. This is characterization, not a passing bar for next version.

## T29: Switch off rollbug_carrion

Retain code and defs. Add or use a per-feature setting labelled "Next version: rollbug_carrion", shipped OFF; reset defaults, static initializers, defs, settings writes and campaign patches must agree. This ticket gates the feature, not the species roster.

Production call-site search: src/RimMandrake/LeaningScrub/Source/RM_ScrubDens.cs:349: public class RM_CompProperties_CarrionLarder : CompProperties | src/RimMandrake/LeaningScrub/Source/RM_LeaningScrubMod.cs:102: public static bool rollbugCarrionEnabled = true; | src/RimMandrake/LeaningScrub/Defs/ThingDefs_Races/RM_LeaningScrubFauna.xml:1143: Source/RM_ScrubDens.cs, Defs/JobDefs/RM_ScrubDens.xml. Mod Settings: rollbugCarrionEnabled (off: no rolling, no

Decouple: Gate larder selection/haul/bite/gear stripping and HomeTether binding. Ordinary carrion eating remains; interruption/off returns actual corpse and gear with a readable sign.

Acceptance test: Fresh full map, default settings and all kept mechanics on: this extra's generated things, custom jobs, letters, incidents and side effects are absent by state reads and the log is clean. For a behavior on a retained animal/material, the species/material remains but its extra job/effect is absent. Repeat with its labelled setting ON and actual preconditions (including optional dependency/faction when relevant): the things or behavior are present. Test reload and ON-to-OFF interruption without ghost queues, lost objects or a global engine disable. This is characterization, not a passing bar for next version.

## T30: Switch off ruin_injections

Retain code and defs. Add or use a per-feature setting labelled "Next version: ruin_injections", shipped OFF; reset defaults, static initializers, defs, settings writes and campaign patches must agree. This ticket gates the feature, not the species roster.

Production call-site search: src/RimMandrake/LeaningScrub/Source/RM_ScrubInjections.cs:62: if (RM_WindCalendar.On(RM_LeaningScrubSettings.scrubInjectionsEnabled)) | src/RimMandrake/LeaningScrub/Source/RM_LeaningScrubMod.cs:120: public static bool scrubInjectionsEnabled = true; | src/RimMandrake/LeaningScrub/Defs/BiomeDefs/RM_LeaningScrub_Biome.xml:237: <li>RM_ScrubInjections</li> | src/RimMandrake/LeaningScrub/Defs/FactionDefs/RM_CombHolds.xml:38: The Scrub's farmer camps now belong to OutlanderCivil (RM_ScrubInjections_GenStep.xml). | src/RimMandrake/LeaningScrub/Defs/MapGeneration/RM_ScrubInjections_GenStep.xml:9: UtinniPatches/Patches/RM_ScrubInjections_ScavengerClans.xml adds the Jawa clans. Settings: scrubInjectionsEnabled,

Decouple: Gate dead farmstead, hedge homestead and pre-started claim generation; ordinary tree and vine placement must remain independent.

Acceptance test: Fresh full map, default settings and all kept mechanics on: this extra's generated things, custom jobs, letters, incidents and side effects are absent by state reads and the log is clean. For a behavior on a retained animal/material, the species/material remains but its extra job/effect is absent. Repeat with its labelled setting ON and actual preconditions (including optional dependency/faction when relevant): the things or behavior are present. Test reload and ON-to-OFF interruption without ghost queues, lost objects or a global engine disable. This is characterization, not a passing bar for next version.

## T31: Switch off wind_vaporator

Retain code and defs. Add or use a per-feature setting labelled "Next version: wind_vaporator", shipped OFF; reset defaults, static initializers, defs, settings writes and campaign patches must agree. This ticket gates the feature, not the species roster.

Production call-site search: src/RimMandrake/LeaningScrub/Source/RM_ScrubInjections.cs:443: ThingDef vap = DefDatabase<ThingDef>.GetNamedSilentFail("RM_WindVaporator"); | src/RimMandrake/LeaningScrub/Defs/MapGeneration/RM_ScrubInjections_GenStep.xml:16: <ruinVaporatorDef>RM_WindVaporatorWreck</ruinVaporatorDef> | src/RimMandrake/LeaningScrub/Defs/ThingDefs_Buildings/RM_WindVaporator.xml:4: RM_WindVaporator.xml              LEANINGSCRUB_MECHANICS_BUILD_1 part 3

Decouple: Gate construction menu, research, techprint spawning, salvage recipes, powered spawner and wreck discovery independently of retained terrain and wind.

Acceptance test: Fresh full map, default settings and all kept mechanics on: this extra's generated things, custom jobs, letters, incidents and side effects are absent by state reads and the log is clean. For a behavior on a retained animal/material, the species/material remains but its extra job/effect is absent. Repeat with its labelled setting ON and actual preconditions (including optional dependency/faction when relevant): the things or behavior are present. Test reload and ON-to-OFF interruption without ghost queues, lost objects or a global engine disable. This is characterization, not a passing bar for next version.

## T32: Switch off scavenger_camps

Retain code and defs. Add or use a per-feature setting labelled "Next version: scavenger_camps", shipped OFF; reset defaults, static initializers, defs, settings writes and campaign patches must agree. This ticket gates the feature, not the species roster.

Production call-site search: src/RimMandrake/LeaningScrub/Source/RM_ScrubInjections.cs:77: if (RM_WindCalendar.On(RM_LeaningScrubSettings.scrubCampsEnabled)) | src/RimMandrake/LeaningScrub/Source/RM_LeaningScrubMod.cs:122: public static bool scrubCampsEnabled = true; | src/RimMandrake/LeaningScrub/Defs/MapGeneration/RM_ScrubInjections_GenStep.xml:9: UtinniPatches/Patches/RM_ScrubInjections_ScavengerClans.xml adds the Jawa clans. Settings: scrubInjectionsEnabled,

Decouple: Gate both campaign faction injection and map/LordJob behavior. No camp letters or pawns at default; retain ordinary wild animals.

Acceptance test: Fresh full map, default settings and all kept mechanics on: this extra's generated things, custom jobs, letters, incidents and side effects are absent by state reads and the log is clean. For a behavior on a retained animal/material, the species/material remains but its extra job/effect is absent. Repeat with its labelled setting ON and actual preconditions (including optional dependency/faction when relevant): the things or behavior are present. Test reload and ON-to-OFF interruption without ghost queues, lost objects or a global engine disable. This is characterization, not a passing bar for next version.

## T33: Switch off fire_stamping

Retain code and defs. Add or use a per-feature setting labelled "Next version: fire_stamping", shipped OFF; reset defaults, static initializers, defs, settings writes and campaign patches must agree. This ticket gates the feature, not the species roster.

Production call-site search: src/RimMandrake/LeaningScrub/Source/RM_FireStamp.cs:35: public class RM_FireStamperExtension : DefModExtension | src/RimMandrake/LeaningScrub/Source/RM_LeaningScrubMod.cs:106: public static bool fireStampEnabled = true;

Decouple: Gate map scans, job overrides, messages and Utinni stamper binding. Native giant migration/roster is not this feature and remains. No off stamp may be needed to stabilize the whole model.

Acceptance test: Fresh full map, default settings and all kept mechanics on: this extra's generated things, custom jobs, letters, incidents and side effects are absent by state reads and the log is clean. For a behavior on a retained animal/material, the species/material remains but its extra job/effect is absent. Repeat with its labelled setting ON and actual preconditions (including optional dependency/faction when relevant): the things or behavior are present. Test reload and ON-to-OFF interruption without ghost queues, lost objects or a global engine disable. This is characterization, not a passing bar for next version.

## T34: Switch off calling_pyre

Retain code and defs. Add or use a per-feature setting labelled "Next version: calling_pyre", shipped OFF; reset defaults, static initializers, defs, settings writes and campaign patches must agree. This ticket gates the feature, not the species roster.

Production call-site search: src/RimMandrake/LeaningScrub/Source/RM_CallingPyre.cs:33: public static class RM_CallingPyreDefOf | src/RimMandrake/LeaningScrub/Source/RM_LeaningScrubMod.cs:115: public static bool callingPyreEnabled = true; | src/RimMandrake/LeaningScrub/Defs/Ideology/RM_CallingPyre.xml:4: RM_CallingPyre.xml          LEANINGSCRUB_MECHANICS_BUILD_1 part 5, second half

Decouple: Gate precept/meme/ritual discoverability as well as execution, outcome workers, incident generation, herd arrival and aftermath. A disabled ritual cannot be selected or emitted indirectly.

Acceptance test: Fresh full map, default settings and all kept mechanics on: this extra's generated things, custom jobs, letters, incidents and side effects are absent by state reads and the log is clean. For a behavior on a retained animal/material, the species/material remains but its extra job/effect is absent. Repeat with its labelled setting ON and actual preconditions (including optional dependency/faction when relevant): the things or behavior are present. Test reload and ON-to-OFF interruption without ghost queues, lost objects or a global engine disable. This is characterization, not a passing bar for next version.

## T35: Keep excluded save_aliases inert

This is an exclusion/compliance ticket, not permission to delete code. Leave source/defs in the tree; prevent runtime alias registration or spawning of excluded content. No compatibility conversion, alias import or old-save preservation may be reintroduced. Sources: src/RimMandrake/LeaningScrub/Defs/Misc/RM_SWBRehome_Aliases.xml; src/RimMandrake/LeaningScrub/Defs/ThingDefs_Items/RM_Absorbed_Eggs.xml

Acceptance test: On a fresh current-schema map, excluded behavior is absent by state read and the log is clean. Current names resolve directly; no alias operation is registered. No on-arm: old-save preservation is already excluded by the owner.

## T36: Switch off acoustic_payload

Retain code and defs. Add or use a per-feature setting labelled "Next version: acoustic_payload", shipped OFF; reset defaults, static initializers, defs, settings writes and campaign patches must agree. This ticket gates the feature, not the species roster.

Production call-site search: src/RimMandrake/LeaningScrub/Patches/RM_AcousticPayload_LeaningScrub.xml:20: <li Class="RimMandrake.AcousticScanner.RM_AcousticPayloadExtension">

Decouple: Gate biome-specific payload registration without disabling the external scanner engine.

Acceptance test: Fresh full map, default settings and all kept mechanics on: this extra's generated things, custom jobs, letters, incidents and side effects are absent by state reads and the log is clean. For a behavior on a retained animal/material, the species/material remains but its extra job/effect is absent. Repeat with its labelled setting ON and actual preconditions (including optional dependency/faction when relevant): the things or behavior are present. Test reload and ON-to-OFF interruption without ghost queues, lost objects or a global engine disable. This is characterization, not a passing bar for next version.

## T37: Switch off proximity_hatch

Retain code and defs. Add or use a per-feature setting labelled "Next version: proximity_hatch", shipped OFF; reset defaults, static initializers, defs, settings writes and campaign patches must agree. This ticket gates the feature, not the species roster.

Production call-site search: src/RimMandrake/LeaningScrub/Patches/ProximityHatch/RM_ProtovermesEgg_ProximityHatch.xml:6: Moved here (batch 3) from src/RimStarWars/SWBestiary/Patches/ProximityHatch/RSW_ProtovermesEgg_ProximityHatch.xml. | src/RimMandrake/LeaningScrub/Defs/Misc/RM_SWBRehome_Aliases.xml:60: <li><from>RSW_ProtovermesEggFertilized</from><to>RM_ProtovermesEggFertilized</to><defType>ThingDef</defType></li> | src/RimMandrake/LeaningScrub/Defs/ThingDefs_Races/RM_Absorbed_Protovermes.xml:70: <eggFertilizedDef>RM_ProtovermesEggFertilized</eggFertilizedDef> | src/RimMandrake/LeaningScrub/Defs/ThingDefs_Items/RM_Absorbed_Eggs.xml:212: <defName>RM_ProtovermesEggFertilized</defName>

Decouple: Gate optional patch comp behavior without removing the fertilized egg or its vanilla timer hatcher.

Acceptance test: Fresh full map, default settings and all kept mechanics on: this extra's generated things, custom jobs, letters, incidents and side effects are absent by state reads and the log is clean. For a behavior on a retained animal/material, the species/material remains but its extra job/effect is absent. Repeat with its labelled setting ON and actual preconditions (including optional dependency/faction when relevant): the things or behavior are present. Test reload and ON-to-OFF interruption without ghost queues, lost objects or a global engine disable. This is characterization, not a passing bar for next version.

## T38: Specify later fire_maker_witness_trail

Deferred promised behavior, not a claim that code exists. Before any later activation, write its complete state/transition and interaction contract, keeping the present native roster. Search evidence: OWNER:1794334503877366549; src/RimMandrake/LeaningScrub/Source/RM_FireStamp.cs:49; src/RimMandrake/RimProperty/Source/PerceptionUtility.cs:35. Maker attribution and pursuit are a separate social knowledge system; the route/claim signature does not need them. Shared ownership-engine work is not redesigned here. Default remains OFF; no stub description may promise a current behavior.

Acceptance test: none, there is no credible current implementation to exercise; acceptance of the later specification requires explicit inputs, states, expiry/interruption rules and a game-calibrated instrument before a build is authorized.

## T39: Specify later shokka_ambush

Deferred promised behavior, not a claim that code exists. Before any later activation, write its complete state/transition and interaction contract, keeping the present native roster. Search evidence: src/RimMandrake/LeaningScrub/Defs/ThingDefs_Races/RM_LeaningScrubFauna.xml:243; ITEM:LEANINGSCRUBFAUNA_BUILD_STUBBED_BEHAVIOURS; CONDUCTOR:1794794271528276351. Habitat-triggered edge ambush adds custom AI beyond ordinary predation; retain the predator itself. Default remains OFF; no stub description may promise a current behavior.

Acceptance test: none, there is no credible current implementation to exercise; acceptance of the later specification requires explicit inputs, states, expiry/interruption rules and a game-calibrated instrument before a build is authorized.

## T40: Specify later fuzzviper_ambush

Deferred promised behavior, not a claim that code exists. Before any later activation, write its complete state/transition and interaction contract, keeping the present native roster. Search evidence: src/RimMandrake/LeaningScrub/Defs/ThingDefs_Races/RM_LeaningScrubFauna.xml:444; ITEM:LEANINGSCRUBFAUNA_BUILD_STUBBED_BEHAVIOURS; CONDUCTOR:1794794271528276351. Run-wall traffic interception adds custom AI beyond ordinary predation; retain the predator itself. Default remains OFF; no stub description may promise a current behavior.

Acceptance test: none, there is no credible current implementation to exercise; acceptance of the later specification requires explicit inputs, states, expiry/interruption rules and a game-calibrated instrument before a build is authorized.

## T41: Specify later ribbonwhip_canopy_route

Deferred promised behavior, not a claim that code exists. Before any later activation, write its complete state/transition and interaction contract, keeping the present native roster. Search evidence: src/RimMandrake/LeaningScrub/Defs/ThingDefs_Races/RM_LeaningScrubFauna.xml:642; ITEM:LEANINGSCRUBFAUNA_BUILD_STUBBED_BEHAVIOURS; CONDUCTOR:1794794271528276351. Canopy-only pathfinding is a separate habitat movement restriction; retain the animal without claiming it is implemented. Default remains OFF; no stub description may promise a current behavior.

Acceptance test: none, there is no credible current implementation to exercise; acceptance of the later specification requires explicit inputs, states, expiry/interruption rules and a game-calibrated instrument before a build is authorized.

## T42: Specify later pillowmoss_wet_spot

Deferred promised behavior, not a claim that code exists. Before any later activation, write its complete state/transition and interaction contract, keeping the present native roster. Search evidence: src/RimMandrake/LeaningScrub/Defs/ThingDefs_Plants/RM_LeaningScrubFuzzFlora.xml:11; CONDUCTOR:1794794271528276351. Fog condensation/terrain conversion is an independent moisture system; the moss remains ordinary ground cover. Default remains OFF; no stub description may promise a current behavior.

Acceptance test: none, there is no credible current implementation to exercise; acceptance of the later specification requires explicit inputs, states, expiry/interruption rules and a game-calibrated instrument before a build is authorized.

## T43: Specify later tanglefuzz_den_ecology

Deferred promised behavior, not a claim that code exists. Before any later activation, write its complete state/transition and interaction contract, keeping the present native roster. Search evidence: src/RimMandrake/LeaningScrub/Defs/ThingDefs_Plants/RM_LeaningScrubFuzzFlora.xml:11; CONDUCTOR:1794794271528276351. Spawning/anchoring dens is a separate population system; the plant remains ordinary cover. Default remains OFF; no stub description may promise a current behavior.

Acceptance test: none, there is no credible current implementation to exercise; acceptance of the later specification requires explicit inputs, states, expiry/interruption rules and a game-calibrated instrument before a build is authorized.

## T44: Specify later cruststar_grazing_ecology

Deferred promised behavior, not a claim that code exists. Before any later activation, write its complete state/transition and interaction contract, keeping the present native roster. Search evidence: src/RimMandrake/LeaningScrub/Defs/ThingDefs_Plants/RM_LeaningScrubFuzzFlora.xml:11; CONDUCTOR:1794794271528276351. A bespoke exclusive grazer pairing adds population tuning; ordinary edible Cruststar and vanilla grazing stay. Default remains OFF; no stub description may promise a current behavior.

Acceptance test: none, there is no credible current implementation to exercise; acceptance of the later specification requires explicit inputs, states, expiry/interruption rules and a game-calibrated instrument before a build is authorized.

## T45: Specify later vissler_finite_arm_regrowth

Deferred promised behavior, not a claim that code exists. Before any later activation, write its complete state/transition and interaction contract, keeping the present native roster. Search evidence: src/RimMandrake/LeaningScrub/Defs/ThingDefs_Races/RM_LeaningScrubFauna.xml:734; src/RimMandrake/LeaningScrub/Source/RM_RunwayBloom.cs:217; CONDUCTOR:1794794271528276351. Finite shedding/regrowth is required if limbs are dropped, but both dropping and regrowth move together. The native animal is not removed. Default remains OFF; no stub description may promise a current behavior.

Acceptance test: none, there is no credible current implementation to exercise; acceptance of the later specification requires explicit inputs, states, expiry/interruption rules and a game-calibrated instrument before a build is authorized.

## T46: Switch off shirrel_glide

Keep the source and defs. Relabel the existing setting “Next version: Shirrel Gale glide and sweetline tether” and default it OFF for both initialization and unsupplied settings. Gate the Gale Goto/launch, tree binding, tether return and glide inspect text. The shirrel's HomeTether can otherwise bind to its spawn cell in PostSpawnSetup, so suppress its local binding and return jobs from spawn and reload while off, without changing the shared behavior for other animals. Clear its stored home and safely resolve any in-progress special glide when switched off.

Decouple: RM_ShirrelGlide.cs CanFlyNow_Postfix currently gates every pawn with the glide comp even while the feature is off, and RM_LeaningScrubFauna.xml sets flightStartChanceOnJobStart to zero for the shirrel. Bypass that veto when off and enable ordinary job-start flight through TFLIGHT, keeping the existing directional frames. With the extra on, preserve the special launch gate and tether. Update the current settings inventory and distinguish the optional ProofGlide read from the ordinary-flight observer.

Acceptance test: On a fresh default map with shirrels and eligible trees, passive state reads across ordinary wind and Gale show ordinary flight but no scripted Gale launch, home binding/return job, glide inspect effect, or extra things, letters or incidents. The log is clean. With the setting on, a naturally eligible idle shirrel in Gale uses the scripted launch and sweetline binding/return. Switching it off clears the tether, resolves the special glide visibly and leaves ordinary flight available. Visual flight checks are owner-attended.

## THISTORY: Switch off sweetline history

Split naming and inspect timers from Record/history storage and CompGetGizmosExtra. Keep the old code/defs, add "Next version: tree history" OFF. Scratch notification can bank felt without writing a narrative entry. Callers: RM_SweetlineStation.cs Record, Notify_Scratched, Notify_DamageApplied, shedding tick and History action. Search found these inside the station; none is an argument to retain the diary.

Acceptance test: Default map: tree label, scratch, free shed and bank work, no History gizmo or new narrative visit/damage entries; log clean. ON: dated entries and History appear, without inventing visiting pawns.

## TTERRAIN: Reconcile ordinary land with standing bans

Source evidence: Defs/BiomeDefs/RM_LeaningScrub_Biome.xml terrainsByFertility selects Sand; Defs/WeatherDefs/RM_LeaningScrub_WindyTwins.xml RM_ScrubDryThunderstorm includes WeatherEvent_LightningStrike; windy twins also include jungle voice beds. Use existing suitable crust/soil terrain if found in effective composed defs; exact crust def identity is unknown pending resolution, so do not invent a name. No new art or planet generation. Preserve the later instruction for wind in the twins while removing automatic ignition, open-sand land and loud wild chorus. Audit outdoor edible crop behavior against the frozen covered-growing requirement; native forage is not a player crop. Keep global Direct Sun, no private biome heat.

Acceptance test: Effective composed terrain/weather state at supported fertility extremes shows crust/soil, no open sand on ordinary plain and no random rain/lightning ignition; wind twins remain eligible and windy. Outdoor player food crops fail or stay poor as the existing ruling requires while protected growlight growing works. Inspect actual game terrain/event state, then apply land_read for readability; log clean. Do not rewrite any world tile.

## TROUTE: Implement and observe explicit trip intent

Implement ordinary_intent/protected_ground using the existing shared passability seam, without redesigning EnvironmentalHazards. In RM_VenomvineIslands.cs NaturalFree, replace the blanket zone veto and separate sown-plant veto with protection for cells that have both a growing zone and a sown plant. Add a read-only observer that records job source/actor/target, every entered cell, hazard/growth/size decision and permission lifecycle, including actual serialization links. No ready intent gate was found in RM_BodySizeBarrierPatches.cs. Offer “Order risky trip” by right-click on the target with a colonist selected and confirm the named target and risk of injury from venomvine contact. Use the closed job list in ordinary_intent. Cancel or replan if growth arms the next cell.

Acceptance test: Calibrated ordinary work chooses the safe detour. Close it so the only traversable route crosses armed vines. A Harvest designation on ripe Dripping and a blanket-placement designation both remain queued with “No safe route: armed venomvine contact.” For each eligible job, right-click its target and confirm the target and contact risk: harvest ripe Dripping, place a smother blanket, pick up paid-out dry cane, cut an armed stand or rescue a downed pawn. The confirmed job can cross while physically traversable. Declining, an ineligible job or a body-size block prevents the crossing. A completed Dripping harvest regrows, and cancellation gives no venom. The situation generator also checks death, downing, retarget, cancellation, mental break and post-load stale tokens for permission leaks. Trace intermediate cells and reject corrupted IDs; the observer starts no jobs.

Acceptance test, route upkeep: In otherwise eligible dirt within creep reach and below the spread cap, a one-cell-wide bare stockpile stripe along a dirt route still receives runners. Repeat for a dumping stripe and an empty growing zone. Roofed, built, floored and sown growing-zone cells refuse insertion in matched branches. Assess dirt-route clearing and developed ground with all kept mechanics on.

## TCLAIM: Finish saved claim duration and safe transactions

RM_CompSmotherable currently saves smotherStartTick and recomputes ClaimTicks from the current setting. Implement claim_transaction with captured current-schema duration/due and growth/yield basis. Proposed120–600 day controls preserve the years-long promise. Add the labelled vanilla Cloth alternate ingredient for tree-free maps using actually resolved Cloth; keep the felt recipe path. No alias/import/migration. Do not destroy plants mid-Plant.TickLong; current MapComponent design is the correct seam.

Acceptance test: Real bill -> blanket -> completed placement -> saved long claim -> actual delivered cane works without direct reward calls. Interrupted placement consumes nothing; duplicate jobs/reload/off and output placement failure never duplicate or lose earned payout. Changing settings changes new claims only. On a tree-free map legitimate Cloth and FuzzFiber can complete the recipe with no spawned blanket. The actual overdue claim is still hazardous until removed and says so.

## TFUEL: Complete useful premium fuel adapters

RM_DeadVenomvine_Fuel.xml only broadens wood filters; no premium adapter was found. Resolve actual CompRefuelable consumers and implement the smallest conserved per-fuel adapter needed by earned_claims. Keep explicit supported-consumer list, mixed-fuel credit and current save serialization. Candidate2 equivalent units and1.25 heat are provisional checks, never owner numbers. No new fuel engine design for neighbors.

Acceptance test: Matched campfire/cooking or other supported consumers given accounted comparable input retain useful work/heat longer with cane than ordinary wood under the same conditions; mixed-fuel and reload retain credit, and a filter-only/no-adapter control fails that comparison. Unsupported consumers are truthfully labelled and cannot be used as premium evidence.

## TCARE: Implement and observe bounded animal care

RM_SweetlineScratching.cs WhyNot currently rejects coats below readiness, and Rub sheds coat without a located health application. Implement care_transaction with resolved disease mechanisms, a legal pen/rope/allowed-area touch-cell and a nonstacking personal health effect. Allow eligible sick animals to choose a care-only rub below readiness and to return when the effect expires while ill. Leave their regrowing coats intact. Vanilla animal disease incidents supply tame flu and plague. Stage gut worms and muscle parasites for adapter proof only. Add no native parasite source. Fix bank placement-before-debit and overflow delivery if current code cannot conserve it. Keep everMature and tree-free behavior. Log completed natural rubs and health ticks without setting coat fullness or injecting jobs.

Acceptance test: For tame animal flu and plague from ordinary incidents and for each staged parasite, the eligible coated animal chooses a legal rub and the named condition clears from the living animal sooner than in a matched untreated control with the same starting severity, immunity and medicine. Include a sick animal below coat readiness that seeks care without producing wool or felt, and a ready animal that sheds its coat. No care effect on canceled rub, mere proximity, excluded condition or no-path animal. No pen escape. The same cohort, coat, bank and condition survive actual current reload. Repeated harvest conserves coat-derived wool, free shedding stays separate, and overflow has a readable physical disposition.

## TACCOUNT: Production material and health receipts

Create non-mutating receipts for recipe/harvest/rub/claim/bank/fuel/product transactions with IDs, input/output custody, fractions, due ticks and actual health deltas. Reuse suitable existing observer plans from the concept but do not call mutating Proof methods evidence of normal actions. Include normal egg hatch, butcher, corpse and engine output references so ordinary lifecycle can be accounted.

Acceptance test: Independent before/after state and actual saved IDs agree with receipts for all transaction classes. Corrupt an intermediate output identity, timer or fraction: offline reader refuses. Observer-off comparison changes no game state/AI decisions; receipts alone never grant health, work or target knowledge.

## TPOWER: Read actual wind-powered work

Extend ordinary validation with WindManager, effective current weather, actual connected turbine output, stored energy, consumer work and gate receipts. Existing reported multiplier/patch state cannot prove ordinary connected work. Export engine curve samples for the whole model.

Acceptance test: Energy ledger explains real wind-only consumer work and end battery charge across ordinary/Stall/Gale transitions. Disconnected output and a tester-filled hidden battery are detected; no surge/breakdown, fixed weather or external generation is needed.

## TNATIVE: Resolve effective ordinary life and source claims

Resolve base/campaign patched animals, age-stage/diet/ordinary-product fields, all native water hooks and existing multihomes from composed defs, not source text counts. Positively identify a named existing native with a real ready shearable coat and actual wool product for tree care; an empty eligibility set cannot pass. If no such native is wired, specify the smallest coat adapter for an already-cast wool-bearing native under its recorded lore, with conservation and ordinary growth; never introduce a test sheep or a new species as a substitute. Source record claims ordinary lifecycles; no current natural census establishes them. Remove or label deferred behavior promises in active descriptions without removing a species. Keep authorized invented thunderstep rehome distinct from deferred fire stamping; resolve its existing library dependency under OWNER:1792856115688559019, never invent a replacement species or a canon claim from RSW prefix.

Acceptance test: Natural map/cycle state shows ordinary active life by class, including a real eligible coated native on tree-care fixtures; real eating/hatching/reproduction/butchery produces accounted results, thornhold melee venom has a distinct cause, native environmental water is usable for natives, and no animal silently vanishes. Effective roster preserves every existing animal entry; adult-band/multihome conflicts are annotated for existing human review without eviction. Base-tier authorized thunderstep is positively bound independent of campaign stamper patch.

## TFLIGHT: Separate ordinary flight from deferred launch events

Search current ordinary movement callers for every effective fiction flyer. Complete ordinary job-start flight opt-ins for shirrel, dustflutter and any other dependent flyer through the existing CreatureBehaviors/Core seam, with the shirrel decoupled by T46. Reuse whole-body directional animation. Extend a non-mutating tracker observer for ordinary movement. Visual observations are jointly with the owner.

Acceptance test: With Gale glide, tether, crown and bloom OFF, passive production tracker/job evidence records ordinary airborne movement and landing for each effective fiction flyer, including shirrel and dustflutter. Check a shirrel on a map without a sweetline in ordinary wind, and record interruption and reload outcomes. Attended observation establishes directional body motion. The observer never drives a flyer.

## TLAND: Rendered and audible context reader

Existing wind/sound scripts mainly check defs/paths and historical observations. Specify attended land_read from actual full-map geometry, naturally unlocked weather and current sound at ordinary play zoom. Use pure independent heading and active audio/weather state as supporting receipts. Existing art is accepted; no new art pipeline or variant quota.

Acceptance test: Cold observer correctly separates the land_read pictures using the actual landscape, wind/Stall/Gale transitions, overlapping foliage/tree signs and audible wind. A static fog sheet, inverted sprite lean or stuck sound bed is detected even when defs and overlay flags look right. Recovery is a discarded fixture or untouched start save.

## TWHOLE: Whole-colony continuation and non-mutating readout

Implement whole_season instrument after smaller models calibrate; include every kept default and all shared mechanics, weather unlocked, actual current save unload/reload, same IDs and reversed feasible main actions. Observer exports upkeep/completed work, every living/dead/exit identity, food/coats/care, power, growth/claims/outputs, errors and settings. Split flight into attended segments; do not schedule unattended flyer driving. Neither the fake bridge nor staging snapshots are a season run.

Acceptance test: All whole_season declared regimes have either calibrated model counterexamples resolved or an explicit still-unproved record, then actual full-map continuation passes its contrasting pictures through season and due extension. No clock-only jump, actor restage, silent relief, fixed clear weather or disabled kept mechanic is accepted. Current save interruption resumes finite jobs/claims without duplicate reward or error loop.

## TMODELS: Implement the prioritized offline instruments

Build the four models in models.md in that order, reusing existing pure kernels with independent oracles. No game code/art is written by this proposal. Unknowns are the first implementation work, not numbers guessed to let a scene pass. Export uncalibrated regimes explicitly; no simulation output is labelled measurement of the game.

Acceptance test: Each model publishes inputs/assumptions/output, range coverage, wrong-input controls and exact current-game agreement receipts to its declared tolerance. An uncalibrated path/health/AI/scheduler regime cannot certify its bar. Whole runtime still requires the actual game instrument.
