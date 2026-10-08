using RimWorld;
using Verse;

namespace RimMandrake.Greentide
{
    // GREENTIDE_FEVER_SPECIALISTS_1. U1's answer, MEASURED via RimSage against
    // the decompiled 1.6 engine 2026-09-29: HediffComp.CompPostPostRemoved()
    // fires whenever this comp's parent hediff is removed from a pawn -
    // vanilla precedent Verse/HediffComp_RecoveryThought.cs. That is the
    // durable, mod-readable "recovered vs died" hook the item needs: a pawn
    // still alive when the hediff comes off survived it.
    //
    // Gated on Props.collapseStageIndex so a pawn cured out of onset/
    // escalation by something outside the disease itself (Biosculpter pod,
    // dev-mode heal, any effect that clears hediffs outright) never rode the
    // real risk and does not earn the badge - the item's own "must stay
    // invisible for the first several trips... do not soften by making the
    // mark easy to earn" (Watch out section). collapseStageIndex must match
    // RM_Frenzy's own 3rd <li> (0-based index 2) in RM_Greentide_Hediffs.xml.
    public class HediffCompProperties_MarksFeverSurvivor : HediffCompProperties
    {
        /// <summary>The permanent badge hediff to apply on survival.</summary>
        public HediffDef markHediff;

        /// <summary>Stage index (0-based) the parent hediff must have reached at least once before removal counts as "survived the real risk", not "cured out of it early".</summary>
        public int collapseStageIndex = 2;

        public HediffCompProperties_MarksFeverSurvivor()
        {
            compClass = typeof(HediffComp_MarksFeverSurvivor);
        }
    }

    public class HediffComp_MarksFeverSurvivor : HediffComp
    {
        private bool reachedGateStage;

        public HediffCompProperties_MarksFeverSurvivor Props => (HediffCompProperties_MarksFeverSurvivor)props;

        public override void CompPostTick(ref float severityAdjustment)
        {
            base.CompPostTick(ref severityAdjustment);
            reachedGateStage = RM_RulesKernel.GateReached(reachedGateStage, parent.CurStageIndex, Props.collapseStageIndex);
        }

        public override void CompExposeData()
        {
            base.CompExposeData();
            Scribe_Values.Look(ref reachedGateStage, "reachedGateStage", defaultValue: false);
        }

        public override void CompPostPostRemoved()
        {
            base.CompPostPostRemoved();
            Pawn pawn = base.Pawn;
            if (!RM_RulesKernel.EarnsMark(RM_GreentideSettings.feverMarkEnabled, Props.markHediff != null, reachedGateStage,
                    pawn == null || pawn.Dead || pawn.health?.hediffSet == null,
                    pawn != null && Props.markHediff != null && pawn.health?.hediffSet != null && pawn.health.hediffSet.HasHediff(Props.markHediff)))
            {
                return; // already marked from a previous bout - never stacks, never re-applies
            }
            pawn.health.AddHediff(Props.markHediff);
            if (PawnUtility.ShouldSendNotificationAbout(pawn))
            {
                Messages.Message("RM_Greentide_FeverMarkEarned".Translate(pawn.Named("PAWN")), pawn, MessageTypeDefOf.PositiveEvent);
            }
        }
    }
}
