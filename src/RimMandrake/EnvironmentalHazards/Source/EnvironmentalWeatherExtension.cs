using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // ALPHA_MECHANICS_KIT_1 item 4 (alpha_family_source_review.md §4.4).
    //
    // The data side of GameCondition_EnvironmentalWeather. A DefModExtension
    // on the GameConditionDef, because GameConditionDef has no props object
    // and its only per-def hook is conditionClass — which is exactly the
    // "one class, many hardcoded subclasses" problem this kit exists to
    // remove.
    //
    // One class replaces the donor's acid-rain condition and covers its
    // volcanic-heat-wave and temperature-fluctuation siblings as config
    // (flat tempOffset, or dayTempOffset/nightTempOffset).
    //
    //   <GameConditionDef>
    //     <defName>RM_ExampleAcidRain</defName>
    //     <conditionClass>RimMandrake.EnvironmentalHazards.GameCondition_EnvironmentalWeather</conditionClass>
    //     ...
    //     <modExtensions>
    //       <li Class="RimMandrake.EnvironmentalHazards.EnvironmentalWeatherExtension">
    //         <forcedWeather>RM_ExampleAcidRainWeather</forcedWeather>
    //         <damageDef>ToxicBuildup</damageDef>
    //         <damageIntervalTicks>10000</damageIntervalTicks>
    //         <damageAmount>4</damageAmount>
    //         <onlyUnroofed>true</onlyUnroofed>
    //         <affects>Flesh</affects>
    //         <itemRotProgressPerCellEffect>3000</itemRotProgressPerCellEffect>
    //         <plantKillChancePerCellEffect>0.0065</plantKillChancePerCellEffect>
    //         <animalDensityFactor>0</animalDensityFactor>
    //         <plantDensityFactor>0</plantDensityFactor>
    //         <allowEnjoyableOutside>false</allowEnjoyableOutside>
    //       </li>
    //     </modExtensions>
    //   </GameConditionDef>
    public class EnvironmentalWeatherExtension : DefModExtension
    {
        // --- weather lock -------------------------------------------------
        // Forced through GameCondition.ForcedWeather(), vanilla's own
        // override for exactly this. The donor fought vanilla's weather
        // rotation with a 300-tick re-set instead; the override is both
        // correct and free, so this kit uses it.
        public WeatherDef forcedWeather;

        // --- periodic pawn damage ----------------------------------------
        public DamageDef damageDef;
        public float damageAmount = 1f;
        public float armorPenetration;
        public int damageIntervalTicks = 10000;

        // Escalate a hediff instead of / as well as dealing damage.
        public HediffDef hediffToApply;
        public float hediffSeverityPerInterval;

        // Only pawns under open sky are hit when true — the whole point of
        // a weather hazard is that a roof is the answer to it.
        public bool onlyUnroofed = true;

        public PawnTargetKind affects = PawnTargetKind.Flesh;
        public List<ThingDef> immuneThingDefs;
        public List<PawnKindDef> immunePawnKinds;

        // --- steady per-cell effects --------------------------------------
        // Both ride GameCondition.DoCellSteadyEffects, which the engine
        // already calls at its own throttled rate over the map (vanilla's
        // toxic fallout uses the identical route) — so neither costs a
        // full-map sweep of our own.
        //
        // Rot progress added to each unroofed, rottable, not-yet-dessicated
        // item the steady sweep touches. 0 disables.
        public float itemRotProgressPerCellEffect;

        // Probability that each plant the steady sweep touches dies.
        // 0 disables. Only plants whose def opts into toxic-fallout death
        // are eligible when respectPlantToxicSensitivity is true.
        public float plantKillChancePerCellEffect;
        public bool respectPlantToxicSensitivity = true;

        // --- ambient modifiers --------------------------------------------
        // Spawn density while the condition runs. Below 1 suppresses (the
        // donor's only direction); above 1 is a deliberate broadening
        // (source review §5) so a biome can get MORE life in its signature
        // weather, not only less.
        public float animalDensityFactor = 1f;
        public float plantDensityFactor = 1f;

        public bool allowEnjoyableOutside = true;

        public bool electricityDisabled;

        // --- temperature ---------------------------------------------------
        // Flat offset, applied whenever dayTempOffset/nightTempOffset are
        // both unset.
        public float tempOffset;

        // Day/night swing. When either is non-zero the flat offset is
        // ignored and the condition lerps between them by daylight, which is
        // the temperature-fluctuation sibling folded in as configuration
        // rather than a second class.
        public float dayTempOffset;
        public float nightTempOffset;

        // Ticks over which the temperature offset fades in at the start and
        // out at the end, via GameConditionUtility.LerpInOutValue.
        public int temperatureTransitionTicks = 5000;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string err in base.ConfigErrors())
            {
                yield return err;
            }

            if (damageIntervalTicks < 1)
            {
                yield return "EnvironmentalWeatherExtension damageIntervalTicks must be >= 1.";
            }

            if (damageDef == null && hediffToApply == null && forcedWeather == null
                && itemRotProgressPerCellEffect <= 0f && plantKillChancePerCellEffect <= 0f
                && animalDensityFactor == 1f && plantDensityFactor == 1f
                && tempOffset == 0f && dayTempOffset == 0f && nightTempOffset == 0f
                && allowEnjoyableOutside && !electricityDisabled)
            {
                yield return "EnvironmentalWeatherExtension has no effect configured at all.";
            }

            if (animalDensityFactor < 0f || plantDensityFactor < 0f)
            {
                yield return "EnvironmentalWeatherExtension density factors must be >= 0.";
            }
        }
    }
}
