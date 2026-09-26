using RimWorld;
using Verse;

namespace RimMandrake.Contagion
{
    // CONTAGION_GENOME_LIMB_AND_MATCH_BONUS_1. The install-match bonus: a
    // measurable, verifiable-in-the-mood-tab difference when a matched
    // organ or limb goes back into its own source colonist. Called only
    // from Recipe_InstallGrownBodyPart.ApplyOnPawn, only on a confirmed
    // same-colonist match, after the surgery has already succeeded.
    public static class GenomeMatchBonusUtility
    {
        public static void ApplyMatchBonus(Pawn recipient, BodyPartRecord part)
        {
            if (recipient?.needs?.mood?.thoughts?.memories == null)
            {
                return;
            }

            recipient.needs.mood.thoughts.memories.TryGainMemory(RM_ContagionDefOf.RM_GenomeMatchedInstall);

            string partLabel = part != null ? part.Label : "part";
            Messages.Message(
                recipient.LabelShort + "'s body accepts the grown " + partLabel
                + " as its own -- it was grown from " + recipient.LabelShort + "'s own genome.",
                recipient,
                MessageTypeDefOf.PositiveEvent,
                historical: false);
        }
    }
}
