using RimWorld;
using Verse;

namespace RimMandrake.TerminalBiomes
{
    // TWILIGHT_CHANNEL_CURRENT_1 §3. RM_Hediff_Sunk's severity ramp: "a
    // HediffComp_SeverityPerDay shape plus a small comp that stops the ramp
    // when rescued/indoors" (river pass spec, verbatim). The spec leaves the
    // exact rescue test unspecified ("design-to-spec inside the carry
    // component" per §7 Q1's own note on failure fairness) — this comp reads
    // "indoors" as Roofed, the same test RM_WanderingVortex.CellImmuneToDamage
    // already uses in this repo (`c.Roofed(Map)`), rather than guessing a bed
    // API. Death itself needs no C#: RM_Hediff_Sunk.xml sets
    // <lethalSeverity>1.0</lethalSeverity>, vanilla's own mechanism for
    // "reaches max severity, the pawn dies" (Malaria/Plague's own shape).
    public class RM_HediffCompProperties_Sunk : HediffCompProperties
    {
        // INVENTED tuning, not a ruling — "death in a day or two if
        // unrecovered" and "ramps down over a day" (spec §3) are the only
        // numbers owed; these hit both within the stated range.
        public float severityPerDayUnrescued = 0.7f;
        public float severityPerDayRescued = -1.1f;

        public RM_HediffCompProperties_Sunk()
        {
            compClass = typeof(RM_HediffComp_Sunk);
        }
    }

    public class RM_HediffComp_Sunk : HediffComp
    {
        private const int EvalIntervalTicks = 200;

        // "recoverable-but-injured" ladder rung (§3): a permanent scar
        // hediff is added at rescue instead of at arrival. Set by
        // RM_MapComponent_ChannelCurrent.ArriveAtSink right after
        // HediffMaker.MakeHediff — before AddHediff — so this comp instance
        // already exists (comps are constructed inside the Hediff itself,
        // ahead of the pawn ever carrying it) and the flag is Scribed so a
        // save mid-ramp does not forget the ladder setting that applied at
        // arrival.
        public bool ScarOnRescue;
        private bool scarApplied;

        private RM_HediffCompProperties_Sunk Props => (RM_HediffCompProperties_Sunk)props;

        public override void CompPostTick(ref float severityAdjustment)
        {
            base.CompPostTick(ref severityAdjustment);
            if (parent?.pawn == null || !parent.pawn.IsHashIntervalTick(EvalIntervalTicks))
            {
                return;
            }

            bool rescued = IsIndoors();
            float perDay = rescued ? Props.severityPerDayRescued : Props.severityPerDayUnrescued;
            severityAdjustment += perDay / GenDate.TicksPerDay * EvalIntervalTicks;

            if (rescued && ScarOnRescue && !scarApplied && parent.Severity <= 0.05f)
            {
                ApplyScar();
                scarApplied = true;
            }
        }

        private bool IsIndoors()
        {
            Pawn p = parent.pawn;
            return p.Spawned && p.Map != null && p.Position.Roofed(p.Map);
        }

        private void ApplyScar()
        {
            HediffDef scarDef = DefDatabase<HediffDef>.GetNamedSilentFail("RM_Hediff_SunkScar");
            if (scarDef == null)
            {
                return; // permanent scar row is a future-content nicety, not owed by this item's engine work
            }
            Hediff scar = HediffMaker.MakeHediff(scarDef, parent.pawn);
            parent.pawn.health.AddHediff(scar);
        }

        public override void CompExposeData()
        {
            base.CompExposeData();
            Scribe_Values.Look(ref ScarOnRescue, "scarOnRescue", false);
            Scribe_Values.Look(ref scarApplied, "scarApplied", false);
        }
    }
}
