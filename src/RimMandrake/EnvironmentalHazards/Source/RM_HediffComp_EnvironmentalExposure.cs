using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // MIASMA_MECHANICS_1 M4 spike (miasma_kit_spec.md). "Unroofed pawns
    // during miasma weather accumulate RUT_MiasmaExposure, severity rate x
    // M1's salinity-band multiplier."
    //
    //   <HediffDef>
    //     <defName>RUT_MiasmaExposure</defName>
    //     ...
    //     <comps>
    //       <li Class="RimMandrake.EnvironmentalHazards.HediffCompProperties_EnvironmentalExposure">
    //         <onlyDuringWeather>RUT_MiasmaWeather</onlyDuringWeather>
    //         <severityPerDayExposed>0.05</severityPerDayExposed>
    //         <severityPerDayUnexposed>-0.2</severityPerDayUnexposed>
    //       </li>
    //     </comps>
    //   </HediffDef>
    public class HediffCompProperties_EnvironmentalExposure : HediffCompProperties
    {
        // Null = would accrue in every weather, not just the biome's own —
        // flagged by ConfigErrors, never silently shipped that way.
        public WeatherDef onlyDuringWeather;

        public float severityPerDayExposed = 0.05f;
        public float severityPerDayUnexposed = -0.2f; // heals off once clear/roofed

        // M1's per-band multiplier (spec M1's own INVENTED starting values).
        public float freshMultiplier = 0.8f;
        public float midMultiplier = 1f;
        public float brineMultiplier = 0.6f;

        public PawnTargetKind affects = PawnTargetKind.Flesh;
        public List<ThingDef> immuneThingDefs;
        public List<PawnKindDef> immunePawnKinds;

        public HediffCompProperties_EnvironmentalExposure()
        {
            compClass = typeof(RM_HediffComp_EnvironmentalExposure);
        }

        public override IEnumerable<string> ConfigErrors(HediffDef parentDef)
        {
            foreach (string err in base.ConfigErrors(parentDef))
            {
                yield return err;
            }

            if (onlyDuringWeather == null)
            {
                yield return "HediffCompProperties_EnvironmentalExposure has no onlyDuringWeather; it would accrue in every weather, not just the biome's own.";
            }
        }
    }

    // Base class HediffComp_SeverityModifierBase confirmed against the live
    // 1.6 decompile (Verse/HediffComp_SeverityModifierBase.cs): it already
    // does the per-200-ticks hashed interval and the /day-to-/tick division
    // (0.0033333334f = 200/60000), the exact shape HediffComp_Immunizable
    // uses. Cribbing the real base class rather than hand-rolling severity
    // math is the "read correctly" half of this spike.
    //
    // SPIKE SCOPE: this comp only tunes ITS OWN parent hediff's severity
    // once the pawn already carries RUT_MiasmaExposure. Giving that hediff
    // to every pawn who enters a Miasma map is separate, owed wiring — the
    // same per-pawn-scan shape GameCondition_EnvironmentalWeather.
    // DoPawnEffects already has in this mod, not a new engine question.
    public class RM_HediffComp_EnvironmentalExposure : HediffComp_SeverityModifierBase
    {
        public HediffCompProperties_EnvironmentalExposure Props => (HediffCompProperties_EnvironmentalExposure)props;

        public override float SeverityChangePerDay()
        {
            Pawn pawn = base.Pawn;
            HediffCompProperties_EnvironmentalExposure props = Props;
            if (props == null || pawn == null || !pawn.Spawned || pawn.Map == null)
            {
                return 0f;
            }

            if (!HazardTargeting.Affects(pawn, props.affects, props.immuneThingDefs, props.immunePawnKinds))
            {
                return 0f;
            }

            bool exposedNow = props.onlyDuringWeather != null
                && pawn.Map.weatherManager.curWeather == props.onlyDuringWeather
                && !pawn.Position.Roofed(pawn.Map);

            if (!exposedNow)
            {
                return props.severityPerDayUnexposed;
            }

            float mult = props.midMultiplier;
            RM_MapComponent_GradientAxis axis = pawn.Map.GetComponent<RM_MapComponent_GradientAxis>();
            if (axis != null)
            {
                float salinity = axis.SalinityAt(pawn.Position);
                mult = salinity > 0.66f
                    ? props.brineMultiplier
                    : (salinity < 0.34f ? props.freshMultiplier : props.midMultiplier);
            }

            return props.severityPerDayExposed * mult;
        }
    }
}
