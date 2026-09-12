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
