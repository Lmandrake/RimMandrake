using UnityEngine;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for the Environmental Hazards
    // kit (ALPHA_MECHANICS_KIT_1).
    //
    // Precedent: src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs and
    // src/RimMandrake/Greentide/Source/RM_GreentideMod.cs.
    //
    // This whole assembly is a MECHANICS KIT: every mechanism here is inert
    // until some ThingDef/HediffDef/GameConditionDef/AbilityDef somewhere
    // opts in via a CompProperties or DefModExtension — this assembly names
    // no content of its own. There is therefore nothing to expose per-def
    // (that is authoring, not a player option); what belongs here is a
    // master switch per mechanism so a player who finds one hazard mod's
    // use of this kit too much (or too little) can turn just that piece
    // down, plus one global intensity dial that scales every damage number
    // the kit deals together, since a modder normally tunes them as one set.
    //
    //   1. gasEmittersEnabled — CompActiveGasEmitter. Off: emitters never
    //      burst, so no new gas clouds spawn from this comp (gas already
    //      spawned by something else is unaffected by this toggle).
    //   2. gasEffectsEnabled — Gas_Damaging / Gas_Transmuting. Off: a gas
    //      cloud (however it got there) sits and expires without damaging,
    //      afflicting or transmuting anything.
    //   3. areaAttacksEnabled — HediffComp_PeriodicAreaAttack. Off: a
    //      carrier with the hediff stops pulsing damage; the hediff itself
    //      is untouched.
    //   4. latentHazardArmingEnabled — GameCondition_ArmLatentHazard. Off:
    //      the condition runs (weather/temperature/etc. it also drives, if
    //      any, still apply) but never arms a fresh hediff onto anyone.
    //   5. environmentalDamageEnabled — the pawn-damaging half of
    //      GameCondition_EnvironmentalWeather (GameConditionTick's sweep and
    //      DoCellSteadyEffects' item-rot/plant-kill). The condition's
    //      weather/temperature/density overrides are structural to whatever
    //      scripted the condition and are left alone — the safe coarse gate
    //      is the damage, not the whole condition.
    //   6. scaledExplosionsEnabled — DeathActionWorker_ScaledExplosion. Off:
    //      a creature with this death action just dies, no explosion.
    //   7. targetedHediffAbilityEnabled — CompAbilityEffect_
    //      TargetedHediffAffliction. Off: casting the ability does nothing.
    //   8. biomeGlowMultiplierEnabled — BiomeGlowPatches. Off: a biome that
    //      opts into darkening keeps vanilla's ordinary sun glow.
    //   9. hazardDamageMultiplier — global scalar on every damage/severity
    //      amount the mechanisms above deal (never on cadence, radius or
    //      chance — those stay whatever the def author tuned).
    //  10. weatherPulseEnabled — RM_GameCondition_WeatherPulse /
    //      RUT_Plant_FlashFlora (FORGE_MECHANICS_1 F1). Off: the condition
    //      stops rolling for a new burst and stays on its calm base
    //      weather permanently (a burst already in progress finishes
    //      rather than snapping off under a pawn's feet); flash-growth
    //      plants stop reading the burst window and grow at their normal
    //      (unmultiplied) rate instead of being stuck at the "outside
    //      window" penalty forever.
    //  11. localGrowthAuraEnabled — RM_HediffComp_LocalGrowthAura
    //      (MIASMA_MECHANICS_1 M5, "Loam-lunged"). Off: a carrier stops
    //      nudging nearby plant growth; the hediff itself is untouched.
    //  12. periodicInspirationEnabled — RM_HediffComp_PeriodicInspiration
    //      (MIASMA_MECHANICS_1 M5, "Mother-dreamed"). Off: a carrier stops
    //      rolling for a random vanilla Inspiration.
    //  13. wardenCrecheScattererEnabled — RM_ScattererValidator_
    //      BrineShallowWater (MIASMA_MECHANICS_1 M6). WORLDGEN-AFFECTING:
    //      off means RUT_GenStep_CrecheScatterer finds no valid site on any
    //      map generated while it is off, so no crèche marker or anchored
    //      pawn is ever placed on that map — already-generated maps and
    //      their existing markers/pawns are unaffected either way.
    //  14. crecheDespoilMemoryEnabled — RM_CompCrecheMarker /
    //      RM_MapComponent_CrecheMemory (MIASMA_MECHANICS_1 M6, §8). Off:
    //      a despoiled marker still flips its own despoiled flag (flavor,
    //      inspect string), but the map-wide manhunter-chance factor is
    //      never registered or applied.
    //  15. bubbleSailorScattererEnabled — RM_ScattererValidator_NearThingDef
    //      (SCALD_MECHANICS_1 S5). WORLDGEN-AFFECTING: off means
    //      RUT_GenStep_ScaldSailScatterer finds no valid site on any map
    //      generated while it is off, so no sail-cluster pawn is ever
    //      placed near a vent on that map — already-generated maps and
    //      their existing placements are unaffected either way.
    //  16. strandingPoolsEnabled — RM_MapComponent_StrandingPools /
    //      RM_JobGiver_ReturnToWater (MIASMA_MECHANICS_1 M3). Off: no new
    //      pool is ever detected after a recede, no stranded creature is
    //      ever spawned, and every already-tracked pool freezes in place
    //      (no further decay, no despawn fallback, no return-to-water jobs)
    //      until this is turned back on — never a silent despawn just from
    //      toggling the option off.
    //  17. livingBolesEnabled — RM_GenStep_LivingBoles (GREENTIDE_MECHANICS_2
    //      M12). WORLDGEN-AFFECTING: off means no Greatbole is placed on any
    //      map generated while it is off. Maps already generated keep
    //      whatever bole they already have.
    //  18. livingRegrowthEnabled — RM_MapComponent_LivingRegrowth
    //      (GREENTIDE_MECHANICS_2 M12). Off: every already-registered bole
    //      freezes exactly where it is — no new regrow timer is scheduled,
    //      no creak warning fires, no crush/eject pulse lands — until this
    //      is back on. Mining, sealing and the bole's own presence are
    //      unaffected either way.
    //  19. rootCausewaysEnabled — RM_GenStep_RootCauseways
    //      (GREENTIDE_MECHANICS_2 M9). WORLDGEN-AFFECTING: off means no
    //      causeway network is painted on any map generated while it is
    //      off. Maps already generated keep whatever network they already
    //      have.
    //  20. wetBulbOverwhelmEnabled — RM_GameCondition_WetBulb
    //      (GREENTIDE_MECHANICS_2 M1). Off: a biome carrying the wet-bulb
    //      condition stops ramping the overwhelm hediff on anyone at all.
    //  21. dryAirBlowerEnabled — RM_CompDryFieldEmitter
    //      (GREENTIDE_MECHANICS_2 M2). Off: a built dry-air blower stops
    //      drying its room (M1's clock keeps running there) and stops
    //      repelling wild animals from its doorway arc; it still draws
    //      power/fuel and pushes heat like any running machine.
    //  22. treeFallEnabled — RM_TreeFallUtility.FellTree (GREENTIDE_MECHANICS_2
    //      M6). Single choke point for all three fellers: off means a
    //      cracking giant tree stops rolling/warning, the Shatterer's own
    //      area aura stops felling trees it damages, and a Gnawer stops
    //      seeking a trunk to chew — an already-falling/mid-chew tree at the
    //      moment this is toggled off simply never completes; nothing is
    //      forced upright again.
    //  23. breaklightEnabled — RUT_IncidentWorker_Breaklight
    //      (GREENTIDE_MECHANICS_2 M5). Off: the Breaklight clearing event
    //      never fires (CanFireNowSub refuses outright); an occurrence
    //      already in progress runs to its own scheduled end rather than
    //      snapping off under a pawn's feet, same posture every other timed
    //      condition in this kit takes.
    //  24. steamDevilEnabled — RM_WanderingVortex / RUT_IncidentWorker_
    //      SteamDevil (GREENTIDE_MECHANICS_2 M3 remainder). Off: the
    //      incident never fires (CanFireNowSub refuses outright) and any
    //      steam devil already wandering the map goes inert in place —
    //      stops moving, damaging and felling trees — rather than vanishing
    //      out from under a pawn; it simply never dissipates or resumes
    //      until this is back on.
    //  25. sporeCloudEnabled — RUT_IncidentWorker_SporeCloud
    //      (ROT_SPORECLOUD_PORT_1, RimUtinni RotSporeKit). Off: the incident
    //      never fires (CanFireNowSub refuses outright); a spore cloud
    //      already settled over a map runs to its own scheduled end rather
    //      than snapping off under a pawn's feet, same posture as
    //      breaklightEnabled.
    //  26. acceleratedRotEnabled — RM_MapComponent_AcceleratedRot
    //      (ROT_DECAY_HARVEST_1). Off: a biome carrying
    //      RM_AcceleratedRotExtension stops accelerating rot and thinning
    //      outdoor filth entirely; everything rots at vanilla's own rate.
    //  27. acceleratedRotItemMultiplier / acceleratedRotCorpseMultiplier —
    //      the SAME mechanism's rate dials, separated because a corpse and a
    //      dropped item read very differently at the same multiplier. Both
    //      only ever ADD to vanilla's own rot tick, never replace it.
    //  28. livingProduceHeatEnabled — RM_MapComponent_LivingProduce
    //      (ROT_DECAY_HARVEST_1). Off: a def carrying
    //      RM_LivingProduceExtension stops pushing any heat into its room;
    //      it still rots, ferments, or does whatever else it already did.
    //  29. warmGroundEnabled — RM_MapComponent_WarmGround
    //      (ROT_WARM_MAT_1). Off: a biome carrying RM_WarmGroundExtension
    //      stops heating its mat-floored rooms entirely; those rooms need
    //      heaters like anywhere else. Nothing else about the mat terrain
    //      (growing, beauty, walking on it) changes either way.
    //  30. warmGroundOffsetCelsius — the SAME mechanism's warmth dial, in °C
    //      above the outdoor temperature. It scales both the temperature the
    //      mat aims a room at AND how much heat the mat can actually deliver
    //      per sweep, so the dial moves the whole mechanism coherently
    //      instead of moving a ceiling a cold room never reaches. The
    //      absolute cap (21 °C) is authoring, not a player option — the mat
    //      is never a comfortable room on its own in real cold.
    //  31. sheenExposureEnabled — RM_HediffComp_SheenExposure
    //      (ROT_SHEEN_WEATHER_1, RimUtinni RotSporeKit "the Sheen"). Off: the
    //      RUT_SheenCoating hediff (and the RUT_SporeFlesh it can seed) stops
    //      accruing from Sheen-fall weather entirely, everywhere. The three
    //      reskinned Sheen weathers themselves (the ban-3 fix) are pure
    //      cosmetic WeatherDefs and keep occurring either way.
    //  32. livePrepStrictViability — the Rot's live preparations
    //      (ROT_LIVE_PREPARATIONS_1, "viability: strict/lenient"). The
    //      kit's own settings law says ban 4 is never fully off, so this is
    //      a two-position dial, not an off switch. Strict (shipped): a
    //      live-prep item carrying RM_LivePrepExtension is ruined by cold
    //      exactly as its vanilla CompTemperatureRuinable says — a fridge
    //      kills it. Lenient: temperature stops ruining those items at all,
    //      and they still expire on their CompLifespan clock. Nothing else
    //      that uses CompTemperatureRuinable (eggs, fermenting) is touched
    //      in either position.
    //  33. treasureConscienceEnabled — RM_TreasureConscienceDef /
    //      RM_Patch_TreasureSaleConscience (ROT_LIVE_PREPARATIONS_1, owner
    //      card 6). Off: selling items marked as some conscience's treasure
    //      no longer gives its memory thought to carriers of that
    //      conscience's hediffs. Thoughts already held run out on their own
    //      normal duration rather than being stripped.
    //  34. sunlightScaldEnabled — RM_HediffComp_SunlightScald
    //      (ROT_LIVE_PREPARATIONS_1, the Sheenblood symbiont's cost). Off: a
    //      carrier's scald severity freezes exactly where it is — never
    //      reset to zero, so turning this back on resumes rather than
    //      forgiving. The hediff's own stages are untouched.
    //  35. mirrorPoolsEnabled — RM_GenStep_ScatterPools (FEVER_WOOD_MECHANICS_1
    //      F1). WORLDGEN-AFFECTING: off means no mirror pools are painted on
    //      any map generated while it is off. Maps already generated keep
    //      whatever pools they already have.
    //  36. leachmossEnabled — RM_LeachmossWildSpawnGatePatch
    //      (DESERT_LEACHMOSS_BUILD_1). Off: RM_Leachmoss stops being offered
    //      by the wild-plant spawner on any map, for both initial seeding
    //      and later regrowth — checked live, so it takes effect the moment
    //      this is toggled, not only on the next map generated. Any moss
    //      already growing is left standing; it simply never re-takes an
    //      emptied cell and never appears on fresh ground until this is
    //      back on.
    //  37. contactVenomEnabled — CompContactVenom /
    //      MapComponent_ContactVenom (VENOMVINE_CONTACT_VENOM_BUILD_1). Off:
    //      a plant built to scratch whoever stands in it stays exactly where
    //      it is and goes inert — it still grows, still costs path, still
    //      blocks, still gets cut, it simply never scratches. Every per-pawn
    //      contact clock already running FREEZES rather than clearing, so
    //      turning this back on resumes instead of forgiving; venom a pawn
    //      already carries decays on its own hediff clock either way.
    //  38. contactVenomScratchMultiplier — the SAME mechanism's damage dial,
    //      applied on top of hazardDamageMultiplier (the two multiply).
    //      Separate from the kit-global because the venom dose is
    //      proportional to damage actually dealt, so this one dial moves both
    //      the injury and how fast the poison builds, and a player who wants
    //      only THIS hazard softened should not have to soften every hazard
    //      in the kit. At 0 the scratch is skipped outright, so no venom is
    //      delivered at all.
    //  39. contactVenomLethal — whether contact venom can finish a pawn.
    //      lethalSeverity is a HediffDef field the engine reads directly, so
    //      this cannot be an XML toggle: on (shipped), the venom reaches its
    //      own lethal threshold and kills, which is what lying down in a
    //      stand for a day costs. Off: severity is held just below that
    //      threshold after every scratch, so the venom still hurts, still
    //      disables and still has to be waited out — it just never finishes
    //      anyone. Turning it off never heals a carrier already past the
    //      threshold; it only stops pushing.
    //  40. bodySizeBarrierEnabled — RM_CompBodySizeBarrier /
    //      RM_MapComponent_BodySizeBarrier / RM_BodySizeBarrierPatches
    //      (VENOMVINE_FORTRESS_PASSABILITY_1). Off: a plant built as a
    //      size-gated barrier stops gating — it still grows, still scratches
    //      if it also carries contact venom, still costs its own pathCost,
    //      but every pawn routes and moves through it on the same terms.
    //      Both hooks read this flag on their first line, so turning it off
    //      also removes the cost of consulting them. Takes effect at once,
    //      on every map: nothing is baked at map generation.
    //  41. bodySizeBarrierThreadCostMultiplier — how heavily a
    //      middle-band pawn (big enough to be slowed, small enough to get
    //      through) is charged per cell inside a barrier. The BLOCK is not
    //      on this dial and cannot be tuned away here, because "larger ones
    //      simply cannot" is the mechanic rather than its difficulty; this
    //      only moves what threading one costs the creatures that can. At 0
    //      a barrier is free to walk through for anything not outright
    //      blocked.
    //  42. glasswalkSlipEnabled — RM_MapComponent_GlasswalkSlip
    //      (SUMP_WALKWAYS_1). Off: a floor tagged RM_SlipperyWalkway (the
    //      Sump's RUT_Glasswalk) never stuns a hurrying/hauling pawn; the
    //      terrain's own permanent speed cap (its pathCost) is untouched
    //      either way — that half needs no toggle since it is a plain
    //      TerrainDef field, not a mechanism this kit runs.
    //  43. glasswalkSlipChancePerSweep — the SAME mechanism's chance dial,
    //      rolled once per eligible pawn every 60-tick sweep. At 0, behaves
    //      identically to the toggle above being off.
    //  44. tarCoatingEnabled — RM_Comp_TarCoatingSource (SUMP_TAR_NASTINESS_1
    //      §1). Off: a Thing built to splash a tar filth coating around
    //      itself (belch events, a surfacing beast) stops splashing; tar
    //      already tracked onto the ground by ordinary foot traffic
    //      (SUMP_WALKWAYS_1's own generatedFilth wiring) is a separate
    //      vanilla mechanism and keeps working either way.
    //  45. tarredHediffEnabled — RM_MapComponent_CarriedFilthHediffLink /
    //      RM_HediffComp_CarriedFilthExposure (SUMP_TAR_NASTINESS_1 §2).
    //      Off: nobody newly carrying tar filth is given the tarred hediff,
    //      and a carrier already afflicted stops accruing OR healing
    //      severity — frozen exactly where it is, not cleared, until this
    //      is back on.
    //  46. warblingGlowEnabled — RM_Comp_WarblingGlow (SUMP_GASLIGHT_1 §2).
    //      Off: a lamp or statue built with this comp stops animating and
    //      simply glows at its sibling CompGlower's own static base color
    //      and radius — same as any plain glower — rather than the warbling
    //      pulse. Scrubbing tar and crafting Sumpgas (the reaction itself)
    //      are untouched either way.
    //  47. warblingGlowSpeedMultiplier — the SAME mechanism's tempo dial.
    //      Never changes hue range, radius range or brightness range — only
    //      how fast the two sine waves cycle. At a very small value the
    //      light reads as nearly static without being a hard off.
    //  48. waterTruceRetributionEnabled — RM_MapComponent_WaterTruce
    //      (WATER_TRUCE_RETRIBUTION_1). Off: a guilty hit landing in a
    //      water-truce biome's radius never rouses wildlife against the
    //      aggressor faction; RM_WaterTruceExtension's own radius field is
    //      still built (cheap, terrain-only) but every retaliation check
    //      bails on this flag first. A retribution already under way on an
    //      affected animal is untouched — this only gates NEW triggers.
    // ════════════════════════════════════════════════════════════════════
    public class RM_EnvironmentalHazardsSettings : ModSettings
    {
        public static bool gasEmittersEnabled = true;
        public static bool gasEffectsEnabled = true;
        public static bool areaAttacksEnabled = true;
        public static bool latentHazardArmingEnabled = true;
        public static bool environmentalDamageEnabled = true;
        public static bool scaledExplosionsEnabled = true;
        public static bool targetedHediffAbilityEnabled = true;
        public static bool biomeGlowMultiplierEnabled = true;
        public static float hazardDamageMultiplier = 1f;
        public static bool weatherPulseEnabled = true;
        public static bool localGrowthAuraEnabled = true;
        public static bool periodicInspirationEnabled = true;
        public static bool wardenCrecheScattererEnabled = true;
        public static bool crecheDespoilMemoryEnabled = true;
        public static bool bubbleSailorScattererEnabled = true;
        public static bool strandingPoolsEnabled = true;
        public static bool livingBolesEnabled = true;
        public static bool livingRegrowthEnabled = true;
        public static bool rootCausewaysEnabled = true;
        public static bool wetBulbOverwhelmEnabled = true;
        public static bool dryAirBlowerEnabled = true;
        public static bool treeFallEnabled = true;
        public static bool breaklightEnabled = true;
        public static bool steamDevilEnabled = true;
        public static bool sporeCloudEnabled = true;
        public static bool acceleratedRotEnabled = true;
        public static float acceleratedRotItemMultiplier = 12f;
        public static float acceleratedRotCorpseMultiplier = 20f;
        public static bool livingProduceHeatEnabled = true;
        public static bool warmGroundEnabled = true;
        public static float warmGroundOffsetCelsius = 18f;
        public static bool sheenExposureEnabled = true;
        public static bool livePrepStrictViability = true;
        public static bool treasureConscienceEnabled = true;
        public static bool sunlightScaldEnabled = true;
        public static bool mirrorPoolsEnabled = true;
        public static bool leachmossEnabled = true;
        public static bool contactVenomEnabled = true;
        public static float contactVenomScratchMultiplier = 1f;
        public static bool contactVenomLethal = true;
        public static bool bodySizeBarrierEnabled = true;
        public static float bodySizeBarrierThreadCostMultiplier = 1f;
        public static bool glasswalkSlipEnabled = true;
        public static float glasswalkSlipChancePerSweep = 0.02f;
        public static bool tarCoatingEnabled = true;
        public static bool tarredHediffEnabled = true;
        public static bool warblingGlowEnabled = true;
        public static float warblingGlowSpeedMultiplier = 1f;
        public static bool waterTruceRetributionEnabled = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref gasEmittersEnabled, "gasEmittersEnabled", true);
            Scribe_Values.Look(ref gasEffectsEnabled, "gasEffectsEnabled", true);
            Scribe_Values.Look(ref areaAttacksEnabled, "areaAttacksEnabled", true);
            Scribe_Values.Look(ref latentHazardArmingEnabled, "latentHazardArmingEnabled", true);
            Scribe_Values.Look(ref environmentalDamageEnabled, "environmentalDamageEnabled", true);
            Scribe_Values.Look(ref scaledExplosionsEnabled, "scaledExplosionsEnabled", true);
            Scribe_Values.Look(ref targetedHediffAbilityEnabled, "targetedHediffAbilityEnabled", true);
            Scribe_Values.Look(ref biomeGlowMultiplierEnabled, "biomeGlowMultiplierEnabled", true);
            Scribe_Values.Look(ref hazardDamageMultiplier, "hazardDamageMultiplier", 1f);
            Scribe_Values.Look(ref weatherPulseEnabled, "weatherPulseEnabled", true);
            Scribe_Values.Look(ref localGrowthAuraEnabled, "localGrowthAuraEnabled", true);
            Scribe_Values.Look(ref periodicInspirationEnabled, "periodicInspirationEnabled", true);
            Scribe_Values.Look(ref wardenCrecheScattererEnabled, "wardenCrecheScattererEnabled", true);
            Scribe_Values.Look(ref crecheDespoilMemoryEnabled, "crecheDespoilMemoryEnabled", true);
            Scribe_Values.Look(ref bubbleSailorScattererEnabled, "bubbleSailorScattererEnabled", true);
            Scribe_Values.Look(ref strandingPoolsEnabled, "strandingPoolsEnabled", true);
            Scribe_Values.Look(ref livingBolesEnabled, "livingBolesEnabled", true);
            Scribe_Values.Look(ref livingRegrowthEnabled, "livingRegrowthEnabled", true);
            Scribe_Values.Look(ref rootCausewaysEnabled, "rootCausewaysEnabled", true);
            Scribe_Values.Look(ref wetBulbOverwhelmEnabled, "wetBulbOverwhelmEnabled", true);
            Scribe_Values.Look(ref dryAirBlowerEnabled, "dryAirBlowerEnabled", true);
            Scribe_Values.Look(ref treeFallEnabled, "treeFallEnabled", true);
            Scribe_Values.Look(ref breaklightEnabled, "breaklightEnabled", true);
            Scribe_Values.Look(ref steamDevilEnabled, "steamDevilEnabled", true);
            Scribe_Values.Look(ref sporeCloudEnabled, "sporeCloudEnabled", true);
            Scribe_Values.Look(ref acceleratedRotEnabled, "acceleratedRotEnabled", true);
            Scribe_Values.Look(ref acceleratedRotItemMultiplier, "acceleratedRotItemMultiplier", 12f);
            Scribe_Values.Look(ref acceleratedRotCorpseMultiplier, "acceleratedRotCorpseMultiplier", 20f);
            Scribe_Values.Look(ref livingProduceHeatEnabled, "livingProduceHeatEnabled", true);
            Scribe_Values.Look(ref warmGroundEnabled, "warmGroundEnabled", true);
            Scribe_Values.Look(ref warmGroundOffsetCelsius, "warmGroundOffsetCelsius", 18f);
            Scribe_Values.Look(ref sheenExposureEnabled, "sheenExposureEnabled", true);
            Scribe_Values.Look(ref livePrepStrictViability, "livePrepStrictViability", true);
            Scribe_Values.Look(ref treasureConscienceEnabled, "treasureConscienceEnabled", true);
            Scribe_Values.Look(ref sunlightScaldEnabled, "sunlightScaldEnabled", true);
            Scribe_Values.Look(ref mirrorPoolsEnabled, "mirrorPoolsEnabled", true);
            Scribe_Values.Look(ref leachmossEnabled, "leachmossEnabled", true);
            Scribe_Values.Look(ref contactVenomEnabled, "contactVenomEnabled", true);
            Scribe_Values.Look(ref contactVenomScratchMultiplier, "contactVenomScratchMultiplier", 1f);
            Scribe_Values.Look(ref contactVenomLethal, "contactVenomLethal", true);
            Scribe_Values.Look(ref bodySizeBarrierEnabled, "bodySizeBarrierEnabled", true);
            Scribe_Values.Look(ref bodySizeBarrierThreadCostMultiplier, "bodySizeBarrierThreadCostMultiplier", 1f);
            Scribe_Values.Look(ref glasswalkSlipEnabled, "glasswalkSlipEnabled", true);
            Scribe_Values.Look(ref glasswalkSlipChancePerSweep, "glasswalkSlipChancePerSweep", 0.02f);
            Scribe_Values.Look(ref tarCoatingEnabled, "tarCoatingEnabled", true);
            Scribe_Values.Look(ref tarredHediffEnabled, "tarredHediffEnabled", true);
            Scribe_Values.Look(ref warblingGlowEnabled, "warblingGlowEnabled", true);
            Scribe_Values.Look(ref warblingGlowSpeedMultiplier, "warblingGlowSpeedMultiplier", 1f);
            Scribe_Values.Look(ref waterTruceRetributionEnabled, "waterTruceRetributionEnabled", true);
        }

        private static Vector2 scrollPosition = Vector2.zero;

        public void DoWindowContents(Rect inRect)
        {
            // 38 checkboxes (most with a two-line tooltip) plus six labeled
            // sliders — this is a FIXED view height, so content taller than it
            // is clipped rather than scrolled to. Same pattern as
            // RimMandrakeFlowWorksMod.DoWindowContents: raise this number in
            // the same edit as whoever adds the next toggle, or their block is
            // invisible.
            Rect view = new Rect(0f, 0f, inRect.width - 24f, 4400f);
            Widgets.BeginScrollView(inRect, ref scrollPosition, view);
            Listing_Standard list = new Listing_Standard { ColumnWidth = view.width };
            list.Begin(view);

            list.Label("This is a toolkit other content uses to build hazards — turning a "
                     + "piece off only matters if some installed content actually uses it.");
            list.GapLine();

            list.CheckboxLabeled("Gas emitters", ref gasEmittersEnabled,
                "Vents/plants/creatures built to periodically release gas stop releasing it.");
            list.CheckboxLabeled("Gas damage and transmuting", ref gasEffectsEnabled,
                "A gas cloud no longer hurts, afflicts, or transforms plants it drifts over.");
            list.CheckboxLabeled("Periodic area attacks", ref areaAttacksEnabled,
                "A hediff built to pulse area damage around its carrier stops pulsing.");
            list.CheckboxLabeled("Latent hazard arming", ref latentHazardArmingEnabled,
                "A map condition built to plant a latent hediff on the population stops planting it.");
            list.CheckboxLabeled("Environmental weather damage", ref environmentalDamageEnabled,
                "A hazardous weather condition stops directly damaging pawns, rotting items or "
              + "killing plants. Its temperature and weather-forcing are unaffected.");
            list.CheckboxLabeled("Scaled death explosions", ref scaledExplosionsEnabled,
                "A creature built to explode on death just dies instead.");
            list.CheckboxLabeled("Targeted affliction ability effect", ref targetedHediffAbilityEnabled,
                "An ability built on this effect does nothing when cast.");
            list.CheckboxLabeled("Biome darkness multiplier", ref biomeGlowMultiplierEnabled,
                "A biome built to run darker than usual (WORLDGEN-AFFECTING for anything that reads "
              + "sunlight over time, but applies to existing maps too since it reads live sun glow) "
              + "reads normal daylight instead.");
            list.CheckboxLabeled("Weather-pulse bursts and flash growth", ref weatherPulseEnabled,
                "A biome built to pulse between calm weather and a violent scalding burst stops "
              + "bursting and stays calm; flash-growth plants stop surging in the burst window and "
              + "grow at their normal rate instead.");
            list.CheckboxLabeled("Local growth aura", ref localGrowthAuraEnabled,
                "A hediff built to slightly speed up plant growth around its carrier stops doing so.");
            list.CheckboxLabeled("Periodic inspiration dreams", ref periodicInspirationEnabled,
                "A hediff built to rarely grant its carrier a random Inspiration stops rolling for one.");
            list.CheckboxLabeled("Warden/crèche placement (WORLDGEN-AFFECTING)", ref wardenCrecheScattererEnabled,
                "A biome built to place guarded crèche sites stops placing new ones on any map generated "
              + "while this is off. Maps already generated keep whatever they already have.");
            list.CheckboxLabeled("Crèche despoil memory", ref crecheDespoilMemoryEnabled,
                "Killing a placed crèche's warden stops raising manhunter-pack odds on that map afterward. "
              + "The marker itself still remembers it was despoiled either way.");
            list.CheckboxLabeled("Bubble-sailor placement (WORLDGEN-AFFECTING)", ref bubbleSailorScattererEnabled,
                "A biome built to place sail clusters near its vents stops placing new ones on any map "
              + "generated while this is off. Maps already generated keep whatever they already have.");
            list.CheckboxLabeled("Stranding pools and the stranded", ref strandingPoolsEnabled,
                "A biome built to leave cut-off water pools behind a receding surge stops detecting new "
              + "ones, stops spawning anything stranded in them, and freezes every pool already tracked "
              + "(no further shrinking, no return-to-water jobs, no despawn) until this is back on.");
            list.CheckboxLabeled("Living-tower bole placement (WORLDGEN-AFFECTING)", ref livingBolesEnabled,
                "A biome built to place a mineable living-tower bole stops placing new ones on any map "
              + "generated while this is off. Maps already generated keep whatever bole they already have.");
            list.CheckboxLabeled("Living-tower regrowth", ref livingRegrowthEnabled,
                "A placed bole stops scheduling new regrowth, stops warning, and stops crushing/ejecting "
              + "whatever is in the way — every chamber freezes exactly as it is until this is back on. "
              + "Mining and sealing chambers is unaffected either way.");
            list.CheckboxLabeled("Root causeway network (WORLDGEN-AFFECTING)", ref rootCausewaysEnabled,
                "A biome built to paint a causeway network stops painting one on any map generated while "
              + "this is off. Maps already generated keep whatever network they already have.");
            list.CheckboxLabeled("Wet-bulb overwhelm", ref wetBulbOverwhelmEnabled,
                "A biome built to overwhelm pawns with saturated heat stops ramping that hediff on "
              + "anyone at all.");
            list.CheckboxLabeled("Dry-air blower drying and animal repel", ref dryAirBlowerEnabled,
                "A built dry-air blower stops drying its room and stops repelling wild animals from its "
              + "doorway arc; it still draws power/fuel and pushes heat like any running machine.");
            list.CheckboxLabeled("Tree fall (crack, shatter, gnaw)", ref treeFallEnabled,
                "A cracking giant tree stops rolling and warning, a hazard aura built to shatter trees "
              + "stops felling them, and a creature built to gnaw one down stops seeking a trunk to chew.");
            list.CheckboxLabeled("Breaklight clearing event", ref breaklightEnabled,
                "A biome built with a rare weather-clearing event stops rolling for one. An occurrence "
              + "already in progress finishes on its own instead of snapping off immediately.");
            list.CheckboxLabeled("Steam devils", ref steamDevilEnabled,
                "The wandering scald-damage vortex event stops occurring; one already wandering the "
              + "map freezes in place (stops moving, damaging and felling trees) instead of vanishing.");
            list.CheckboxLabeled("Spore cloud event", ref sporeCloudEnabled,
                "The fungal spore cloud event stops occurring. One already settled over a map runs "
              + "to its own scheduled end instead of snapping off immediately.");
            list.CheckboxLabeled("Accelerated rot and outdoor filth thinning", ref acceleratedRotEnabled,
                "A biome built to rot exposed things faster and slowly thin outdoor filth stops doing "
              + "either; everything rots at vanilla's own rate again.");
            list.CheckboxLabeled("Living produce room heat", ref livingProduceHeatEnabled,
                "A stockpiled crop or food built to radiate warmth stops pushing any heat into its "
              + "room; it still rots, ferments, or does whatever else it already did.");
            list.CheckboxLabeled("Warm ground (living mat heating)", ref warmGroundEnabled,
                "A biome built with warm living ground stops heating rooms floored on it; those "
              + "rooms need heaters like anywhere else.");
            list.CheckboxLabeled("Sheen exposure (the Rot)", ref sheenExposureEnabled,
                "Unroofed pawns stop accumulating Sheen coating during Sheen-fall weather, and it "
              + "can no longer seed spore flesh. The Sheen-fall/storm/mist weathers themselves "
              + "keep occurring either way.");
            list.CheckboxLabeled("Live preparations: strict viability", ref livePrepStrictViability,
                "Strict: a living brew or symbiont is ruined by cold, so a fridge destroys it and it "
              + "must be drunk where it was made. Lenient: cold no longer ruins it — but it still "
              + "dies of old age within a couple of days either way.");
            list.CheckboxLabeled("Treasure-sale conscience", ref treasureConscienceEnabled,
                "A colonist carrying a symbiont stops feeling anything when the colony sells the "
              + "treasures that symbiont came from.");
            list.CheckboxLabeled("Sunlight scald", ref sunlightScaldEnabled,
                "A hediff built to burn its carrier in direct sunlight stops building up; whatever "
              + "severity a carrier already has is frozen, not cleared.");
            list.CheckboxLabeled("Mirror pool placement (WORLDGEN-AFFECTING)", ref mirrorPoolsEnabled,
                "A biome built to scatter small still-water pools stops placing new ones on any map "
              + "generated while this is off. Maps already generated keep whatever pools they already have.");
            list.CheckboxLabeled("Leachmoss wild spawning", ref leachmossEnabled,
                "A fast-spreading moss built to race everything else for fertile open ground stops being "
              + "offered by the wild-plant spawner, on every map immediately. Moss already growing is left "
              + "standing; it just never re-takes an emptied cell or appears on fresh ground until this is "
              + "back on.");
            list.CheckboxLabeled("Contact venom (thorn plants)", ref contactVenomEnabled,
                "A plant built to scratch whoever stands in it goes inert — it still grows, still "
              + "slows movement and can still be cut, it just never scratches. Clocks already "
              + "running freeze rather than reset, so turning this back on resumes.");
            list.CheckboxLabeled("Contact venom can kill", ref contactVenomLethal,
                "On: staying in a thorn stand long enough is fatal. Off: the venom still hurts and "
              + "disables, but is always held just short of killing. Turning this off does not heal "
              + "anyone already past that point.");
            list.CheckboxLabeled("Thickets block large creatures", ref bodySizeBarrierEnabled,
                "On: a plant built as a fortress thicket is impassable to anything big — herds, "
              + "pack animals and the largest wildlife route around a stand instead of through it, "
              + "while small creatures cross freely and people force a slow way through. Off: "
              + "everything moves through it on the same terms.");
            list.CheckboxLabeled("Glasswalk slip-and-fall", ref glasswalkSlipEnabled,
                "A floor built slick (the Sump's glasswalk) stops rarely staggering a pawn who is "
              + "hurrying or hauling across it. No damage either way — the floor's own permanent "
              + "speed cap is untouched by this toggle.");
            list.CheckboxLabeled("Tar-coating sources", ref tarCoatingEnabled,
                "A Thing built to splash a tar filth coating around itself (a belch event, a "
              + "surfacing beast) stops splashing. Tar tracked onto the ground by ordinary foot "
              + "traffic is a separate mechanism and keeps working either way.");
            list.CheckboxLabeled("Tarred-pawn hediff", ref tarredHediffEnabled,
                "Nobody newly tracking tar is given the tarred hediff, and a carrier already "
              + "afflicted stops accruing or healing severity — frozen exactly where it is until "
              + "this is back on.");
            list.CheckboxLabeled("Warbling gaslight animation", ref warblingGlowEnabled,
                "A lamp or statue built with the warbling glow comp stops dancing/pulsing and just "
              + "glows steadily at its base color and radius, like any plain light. Scrubbing tar "
              + "and crafting Sumpgas are unaffected either way.");
            list.CheckboxLabeled("Water-truce retribution", ref waterTruceRetributionEnabled,
                "A biome built with a sacred water truce stops turning wildlife against whoever "
              + "lands the first guilty hit near the water. Defending yourself never counts as "
              + "guilty either way — this only gates the retaliation, never who started it.");
            list.GapLine();

            list.Label("Contact venom scratch: " + contactVenomScratchMultiplier.ToString("0.00") + "x");
            list.Label("How hard a thorn plant scratches, on top of the overall hazard damage dial. "
                     + "The venom dose follows the damage, so this moves the poison too. At 0 the "
                     + "plant scratches nobody.");
            contactVenomScratchMultiplier = list.Slider(contactVenomScratchMultiplier, 0f, 3f);

            list.Label("Forcing a thicket: " + bodySizeBarrierThreadCostMultiplier.ToString("0.00") + "x");
            list.Label("How slowly someone big enough to be slowed — but not big enough to be "
                     + "stopped — crosses a fortress thicket. Does not change WHO is stopped; at 0 "
                     + "a thicket costs nothing extra to anyone who can enter it at all.");
            bodySizeBarrierThreadCostMultiplier = list.Slider(bodySizeBarrierThreadCostMultiplier, 0f, 1.5f);

            list.Label("Hazard damage: " + hazardDamageMultiplier.ToString("0.00") + "x");
            list.Label("Scales every damage/severity number the mechanisms above deal. Never "
                     + "changes how often, how far, or how likely a hazard fires.");
            hazardDamageMultiplier = list.Slider(hazardDamageMultiplier, 0.25f, 3f);

            list.Label("Accelerated rot, dropped items: " + acceleratedRotItemMultiplier.ToString("0.0") + "x vanilla's rate");
            acceleratedRotItemMultiplier = list.Slider(acceleratedRotItemMultiplier, 1f, 40f);
            list.Label("Accelerated rot, corpses: " + acceleratedRotCorpseMultiplier.ToString("0.0") + "x vanilla's rate");
            acceleratedRotCorpseMultiplier = list.Slider(acceleratedRotCorpseMultiplier, 1f, 40f);

            list.Label("Warm ground: up to " + warmGroundOffsetCelsius.ToString("0") + " C above the outdoor temperature");
            list.Label("How much warmth living ground gives a room floored on it, and how fast it "
                     + "delivers it. Never past 21 C, so it helps a lot in the cold without ever "
                     + "replacing a heater.");
            warmGroundOffsetCelsius = list.Slider(warmGroundOffsetCelsius, 0f, 30f);

            list.Label("Glasswalk slip chance: " + (glasswalkSlipChancePerSweep * 100f).ToString("0.0") + "% per second while hurrying/hauling on it");
            list.Label("How often a fast-moving or hauling pawn briefly staggers on a slick floor. "
                     + "At 0, nobody ever slips.");
            glasswalkSlipChancePerSweep = list.Slider(glasswalkSlipChancePerSweep, 0f, 0.2f);

            list.Label("Warbling gaslight tempo: " + warblingGlowSpeedMultiplier.ToString("0.00") + "x");
            list.Label("How fast a warbling lamp or statue's color and radius dance. Never changes "
                     + "how far they wander, only how quickly.");
            warblingGlowSpeedMultiplier = list.Slider(warblingGlowSpeedMultiplier, 0.1f, 3f);

            list.End();
            Widgets.EndScrollView();
        }
    }

    public class RM_EnvironmentalHazardsMod : Mod
    {
        public static RM_EnvironmentalHazardsSettings settings;

        public RM_EnvironmentalHazardsMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_EnvironmentalHazardsSettings>();
        }

        public override string SettingsCategory()
        {
            return "Environmental Hazards Kit";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
