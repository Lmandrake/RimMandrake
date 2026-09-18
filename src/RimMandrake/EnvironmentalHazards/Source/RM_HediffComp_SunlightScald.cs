using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // ════════════════════════════════════════════════════════════════════
    // ROT_LIVE_PREPARATIONS_1, the cost half of the Sheenblood symbiont
    // ("sun intolerance: severity/burn while in direct sunlight").
    //
    // WHY NOT RM_Hediff_SunScald. The ticket's first choice was to reuse
    // mandrake.rm.creaturebehaviors' RM_Hediff_SunScald "if its shape fits".
    // It does not, for a structural reason rather than a behavioural one:
    // that is a HEDIFF CLASS, so a RotSporeKit HediffDef reusing it would
    // have to name it in <hediffClass>, which is a plain def FIELD — a
    // MayRequire there is not a thing, and if creaturebehaviors is absent
    // the whole HediffDef is discarded (the class cannot resolve), taking
    // the symbiont's benefit side down with it. Worse, that hediffClass is
    // the symbiont's ONLY class slot, so it could not also be a
    // HediffWithComps carrying the bargain's other half.
    //
    // This is the same mechanism as a COMP, in the assembly RotSporeKit
    // already depends on and already MayRequire-gates per <li>. It keys off
    // the identical primitive RM_Hediff_SunScald uses and documents:
    // IntVec3.InSunlight(map) — unroofed AND map.skyManager.CurSkyGlow >
    // 0.1, the same one vanilla's UV-sensitivity gene uses. A wall lamp is
    // never the sun.
    //
    // The comp only DRIVES SEVERITY. What rising severity does — pain,
    // capacity loss, a burn — is the consuming HediffDef's stages, exactly
    // as RM_Hediff_SunScald's own header requires of its consumers.
    // ════════════════════════════════════════════════════════════════════
    public class RM_HediffCompProperties_SunlightScald : HediffCompProperties
    {
        public float severityPerDayInSunlight = 1.0f;
        public float severityPerDayShaded = -2.0f;

        // Severity never climbs past this, so a symbiont left standing in
        // the open all season saturates rather than running away. -1 = no
        // ceiling beyond the HediffDef's own maxSeverity.
        public float maxSeverity = -1f;

        // A hediff that switches the scald off entirely (shade gear, a cure,
        // a second symbiont). Optional.
        public HediffDef immunityHediff;

        public RM_HediffCompProperties_SunlightScald()
        {
            compClass = typeof(RM_HediffComp_SunlightScald);
        }
    }

    public class RM_HediffComp_SunlightScald : HediffComp
    {
        private const int CheckIntervalTicks = 60;

        public RM_HediffCompProperties_SunlightScald Props =>
            (RM_HediffCompProperties_SunlightScald)props;

        public override bool CompShouldRemove => false;

        public override void CompPostTickInterval(ref float severityAdjustment, int delta)
        {
            base.CompPostTickInterval(ref severityAdjustment, delta);

            if (!RM_EnvironmentalHazardsSettings.sunlightScaldEnabled)
            {
                return; // mod option off: severity frozen exactly where it is, never reset
            }

            Pawn pawn = base.Pawn;
            if (pawn == null || pawn.Dead || !pawn.SpawnedOrAnyParentSpawned)
            {
                return;
            }

            if (!pawn.IsHashIntervalTick(CheckIntervalTicks, delta))
            {
                return;
            }

            if (Props.immunityHediff != null && pawn.health?.hediffSet != null
                && pawn.health.hediffSet.HasHediff(Props.immunityHediff))
            {
                return;
            }

            Map map = pawn.MapHeld;
            if (map == null)
            {
                return; // in a caravan or a container — no sky to be under
            }

            bool inSunlight = pawn.PositionHeld.InSunlight(map);
            float perDay = inSunlight ? Props.severityPerDayInSunlight : Props.severityPerDayShaded;

            // perDay is per in-game DAY; this runs once per CheckIntervalTicks.
            float change = perDay * (CheckIntervalTicks / 60000f);
            if (Mathf.Approximately(change, 0f))
            {
                return;
            }

            float next = parent.Severity + change;
            if (Props.maxSeverity > 0f)
            {
                next = Mathf.Min(next, Props.maxSeverity);
            }

            parent.Severity = Mathf.Max(0f, next);
        }
    }
}
