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
            if (!RM_GreentideSettings.frenzyEnabled)
            {
                return;
            }
            float configuredSeverity = severity;
            if (severity > 0f)
            {
                severity *= RM_GreentideSettings.frenzySeverityMultiplier;
            }
            base.DoIngestionOutcomeSpecial(pawn, ingested, ingestedCount);
            severity = configuredSeverity;
        }
    }
}
