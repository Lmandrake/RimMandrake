using System.Collections.Generic;
using RimWorld;
using UnityEngine;
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

        // ROT_SHEEN_WEATHER_1 addition: a biome with more than one qualifying
        // weather (the Sheen ships three reskinned rows) lists them here
        // instead. When non-empty this takes priority over the single
        // onlyDuringWeather above; either satisfies ConfigErrors. Kept as a
        // separate field rather than widening onlyDuringWeather itself so
        // RUT_MiasmaExposure's existing single-weather XML needs no edit.
        public List<WeatherDef> onlyDuringWeathers;

        public float severityPerDayExposed = 0.05f;
        public float severityPerDayUnexposed = -0.2f; // heals off once clear/roofed

        // M1's per-band multiplier (spec M1's own INVENTED starting values).
        // Unused (stays at defaults, all multiply to midMultiplier=1) unless
        // RM_MapComponent_GradientAxis is present on the map — Miasma-only.
        public float freshMultiplier = 0.8f;
        public float midMultiplier = 1f;
        public float brineMultiplier = 0.6f;

        // ROT_SHEEN_WEATHER_1 addition: gear-slows-the-clock (owner card 5).
        // Summed across worn apparel via HazardTargeting.SumApparelStat (an
        // "Apparel"-category StatDef, same reasoning RM_WetBulbProtection's
        // header gives — no vanilla per-pawn aggregation exists). The applied
        // gain is severityPerDayExposed * max(minDriveFactor, 1 - protection):
        // protection alone can slow the clock but, by the floor, never zero
        // it — card 5 is explicit that gear is never full immunity.
        public StatDef protectionStat;
        public float minDriveFactor;

        // ROT_SHEEN_WEATHER_1 addition: a hediff that zeroes accrual outright
        // (the Rot's symbiont, RUT_SheenSymbiosis — card 5: "the symbiont
        // remains the only true immunity"). Checked before the protection
        // floor above, so this is the one route that actually reaches zero.
        public HediffDef immunityHediff;

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

            if (onlyDuringWeather == null && (onlyDuringWeathers == null || onlyDuringWeathers.Count == 0))
            {
                // Read the actual gate in RM_HediffComp_EnvironmentalExposure.SeverityChangePerDay:
                // exposedNow short-circuits false when neither field is set, so this hediff
                // would NEVER accrue (not "in every weather") — it would only ever apply
                // severityPerDayUnexposed and heal itself off, silently inert.
                yield return "HediffCompProperties_EnvironmentalExposure has no onlyDuringWeather/onlyDuringWeathers; exposedNow can never be true, so this hediff will only ever heal (severityPerDayUnexposed) and never accrue, in any weather.";
            }

            if (immunityHediff != null && immunityHediff == parentDef)
            {
                yield return "HediffCompProperties_EnvironmentalExposure.immunityHediff is the same def this comp is attached to — a hediff cannot immunize its own carrier against itself.";
            }

            if (minDriveFactor < 0f || minDriveFactor > 1f)
            {
                yield return "HediffCompProperties_EnvironmentalExposure minDriveFactor must be within 0..1.";
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

            // ROT_SHEEN_WEATHER_1: the symbiont hediff is the one route that
            // actually reaches zero (card 5). Checked ahead of the weather
            // gate so a symbiont also stops the carrier decaying pointlessly
            // while indoors — full immunity, not just a slowed clock.
            if (props.immunityHediff != null && pawn.health.hediffSet.HasHediff(props.immunityHediff))
            {
                return 0f;
            }

            bool weatherOk = props.onlyDuringWeathers != null && props.onlyDuringWeathers.Count > 0
                ? props.onlyDuringWeathers.Contains(pawn.Map.weatherManager.curWeather)
                : props.onlyDuringWeather != null && pawn.Map.weatherManager.curWeather == props.onlyDuringWeather;

            bool exposedNow = weatherOk && !pawn.Position.Roofed(pawn.Map);

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

            // ROT_SHEEN_WEATHER_1: gear-slows-the-clock (card 5). Miasma sets
            // no protectionStat, so protection stays 0 and driveFactor stays
            // 1 — unchanged behaviour for the existing consumer.
            float driveFactor = 1f;
            if (props.protectionStat != null)
            {
                float protection = HazardTargeting.SumApparelStat(pawn, props.protectionStat);
                driveFactor = Mathf.Max(props.minDriveFactor, 1f - Mathf.Clamp01(protection));
            }

            return props.severityPerDayExposed * mult * driveFactor;
        }
    }
}
