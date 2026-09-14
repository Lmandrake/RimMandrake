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
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

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
            list.GapLine();

            list.Label("Hazard damage: " + hazardDamageMultiplier.ToString("0.00") + "x");
            list.Label("Scales every damage/severity number the mechanisms above deal. Never "
                     + "changes how often, how far, or how likely a hazard fires.");
            hazardDamageMultiplier = list.Slider(hazardDamageMultiplier, 0.25f, 3f);

            list.End();
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
