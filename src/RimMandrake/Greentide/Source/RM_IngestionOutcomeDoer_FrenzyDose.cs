using RimWorld;
using Verse;

namespace RimMandrake.Greentide
{
    // GREENTIDE_FRENZY_DISEASE_1. RM_FrenzyDose's own outcomeDoer
    // (RM_Frenzy_Items.xml) uses this instead of the vanilla
    // IngestionOutcomeDoer_GiveHediff directly, so Mod Settings can gate the
    // deliberate-dose route: fully off skips giving the hediff at all
    // (frenzyEnabled), and frenzySeverityMultiplier tunes how strong the
    // initial kick from a single dose is. Everything else — the natural
    // per-day climb, the coma, tending — lives entirely on RM_Frenzy's own
    // HediffDef and is unaffected by this class.
    public class RM_IngestionOutcomeDoer_FrenzyDose : IngestionOutcomeDoer_GiveHediff
    {
        protected override void DoIngestionOutcomeSpecial(Pawn pawn, Thing ingested, int ingestedCount)
        {
            int dose = RM_RulesKernel.FrenzyDose(RM_GreentideSettings.frenzyEnabled, RM_GreentideSettings.feverMarkGrantsImmunity,
                pawn.health?.hediffSet != null && pawn.health.hediffSet.HasHediff(RM_DefOf.RM_FeverMark), severity,
                RM_GreentideSettings.frenzySeverityMultiplier, out float applied);
            if (dose == 0)
            {
                return;
            }
            if (dose == 1)
            {
                Messages.Message("RM_Greentide_FrenzyDoseWasted".Translate(pawn.Named("PAWN")), pawn, MessageTypeDefOf.NeutralEvent);
                return;
            }
            float configuredSeverity = severity;
            severity = applied;
            base.DoIngestionOutcomeSpecial(pawn, ingested, ingestedCount);
            severity = configuredSeverity;
        }
    }
}
