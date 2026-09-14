using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // MIASMA_MECHANICS_1 M2 build (miasma_kit_spec.md M2: "the breath-tide
    // surge"). Generic on purpose, same reasoning as M1's own
    // RM_GradientAxisExtension header ("the Webwork/Scald never need it, but
    // any future two-water biome does") — attached to the SAME BiomeDef,
    // alongside that extension. Parameterizes both the MTB-driven firing
    // (RM_MapComponent_GradientAxis.TickSurgeRoll) and the shove/recede
    // magnitudes (RM_GameCondition_GradientSurge), so both classes read one
    // shared config instead of duplicating tuning across two def types.
    //
    //   <li Class="RimMandrake.EnvironmentalHazards.RM_GradientSurgeExtension">
    //     <incidentDef>RUT_Surge</incidentDef>
    //     <baseMtbDays>5</baseMtbDays>
    //     <stormMtbMultiplier>0.25</stormMtbMultiplier>
    //     <stormWindSpeedThreshold>1.2</stormWindSpeedThreshold>
    //     <frontCellsRange>15~35</frontCellsRange>
    //     <recedeDaysRange>2~4</recedeDaysRange>
    //     <residualFraction>0.15</residualFraction>
    //   </li>
    public class RM_GradientSurgeExtension : DefModExtension
    {
        // Which IncidentDef this map's own MTB clock fires when due. Never
        // reached through the Storyteller's own category queue (see
        // RUT_Surge.xml's own header for why its category is Misc) — this
        // mechanism owns its entire schedule in code; ban #4 ("no clockwork
        // tide") is about a fixed PERIOD, not about having no timer at all.
        public IncidentDef incidentDef;

        // Mean days between surge attempts absent any storm gust (INVENTED,
        // miasma_kit_spec.md M2: "base MTB 5 days").
        public float baseMtbDays = 5f;

        // Multiplies baseMtbDays (smaller = more frequent) while
        // Map.windManager.WindSpeed >= stormWindSpeedThreshold (INVENTED,
        // spec's own "x0.25... the terminator storms piling the Grey Sea
        // against the Salt Gate, priced as weighting, not schedule").
        public float stormMtbMultiplier = 0.25f;

        // "Storm weather active", resolved concretely rather than invented:
        // M4's RUT_MiasmaWeatherLock forces ONE permanent WeatherDef via
        // GameCondition.ForcedWeather(), so the vanilla WeatherManager's own
        // current-weather state can never distinguish "storming" from
        // "calm" here — there is no second, reachable weather left to check
        // (the M4 build pass's own words: "ban #5 is now mechanically
        // true"). The nearest EXISTING, non-invented engine signal that
        // still varies under one locked weather is real map wind gust
        // strength (Verse/WindManager.cs's own public WindSpeed, range
        // [0.04, 2.0], driven by Perlin noise independent of the current
        // WeatherDef) — thresholded here rather than inventing a new "storm"
        // flag/mechanism. The threshold itself is INVENTED (upper ~35% of
        // that real range).
        public float stormWindSpeedThreshold = 1.2f;

        // Front movement in cells during ramp-in (INVENTED, spec: 15-35).
        public IntRange frontCellsRange = new IntRange(15, 35);

        // Recede duration in days (INVENTED, spec: 2-4).
        public FloatRange recedeDaysRange = new FloatRange(2f, 4f);

        // Fraction of the forward shove's magnitude the recede leaves
        // behind as permanent residual drift (INVENTED — spec's own words,
        // "never quite to the old line... so no two maps age alike"; picked
        // and recorded here per this build pass's own instruction to do so).
        public float residualFraction = 0.15f;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string err in base.ConfigErrors())
            {
                yield return err;
            }

            if (incidentDef == null)
            {
                yield return "RM_GradientSurgeExtension has no incidentDef — the surge would never fire.";
            }

            if (baseMtbDays <= 0f)
            {
                yield return "RM_GradientSurgeExtension.baseMtbDays must be > 0.";
            }

            if (stormMtbMultiplier <= 0f)
            {
                yield return "RM_GradientSurgeExtension.stormMtbMultiplier must be > 0.";
            }

            if (frontCellsRange.min <= 0 || frontCellsRange.max < frontCellsRange.min)
            {
                yield return "RM_GradientSurgeExtension.frontCellsRange is invalid.";
            }

            if (recedeDaysRange.min <= 0f || recedeDaysRange.max < recedeDaysRange.min)
            {
                yield return "RM_GradientSurgeExtension.recedeDaysRange is invalid.";
            }

            if (residualFraction < 0f || residualFraction >= 1f)
            {
                yield return "RM_GradientSurgeExtension.residualFraction must be in [0,1).";
            }
        }
    }
}
