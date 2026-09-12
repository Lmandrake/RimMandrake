using RimWorld;
using Verse;

namespace RimMandrake.DivingInteraction
{
    // Sits with the deep rather than taking from it. Always resolves
    // peacefully (the bottom-walkers are "armored, slow, pastoral" per
    // the_scald.md §4) — the cost is still the standing-there burn from the
    // base class, never a new risk on top.
    public class RM_JobDriver_DiveCommune : RM_JobDriver_DiveBase
    {
        protected override string ReportKey => "diving to commune with the deep";

        protected override void ResolveOutcome()
        {
            if (pawn.needs?.mood != null)
            {
                Thought_Memory thought = (Thought_Memory)ThoughtMaker.MakeThought(RM_DivingDefOf.RM_Thought_CommunedWithDeep);
                pawn.needs.mood.thoughts.memories.TryGainMemory(thought);
            }
            Messages.Message(
                "RM_DiveCommuneComplete".Translate(pawn.LabelShort).Resolve(),
                new LookTargets(pawn), MessageTypeDefOf.PositiveEvent);
        }
    }
}
