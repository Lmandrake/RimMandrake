using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.Contagion
{
    // CONTAGION_GPT_ENRICHMENT_1, part 1: Draftprints. Right-click a living
    // Unfinished to walk up and scan it. Same auto-registered provider shape
    // as FloatMenuOptionProvider_InjectGenomeSample (FloatMenuMakerMap
    // reflects every non-abstract subclass; no Harmony).
    public class FloatMenuOptionProvider_SampleDraftprint : FloatMenuOptionProvider
    {
        protected override bool Drafted => true;

        protected override bool Undrafted => true;

        protected override bool Multiselect => false;

        protected override bool RequiresManipulation => true;

        protected override FloatMenuOption GetSingleOptionFor(Thing clickedThing, FloatMenuContext context)
        {
            if (!RM_ContagionSettings.draftprintsEnabled)
            {
                return null;
            }
            if (!(clickedThing is Pawn target) || !DraftprintUtility.CanBeSampled(target))
            {
                return null;
            }
            Pawn actor = context.FirstSelectedPawn;
            if (actor == null || actor == target)
            {
                return null;
            }
            if (!actor.CanReach(target, PathEndMode.Touch, Danger.Deadly))
            {
                return new FloatMenuOption(
                    "Cannot take draftprint: " + "NoPath".Translate().CapitalizeFirst(), null);
            }
            string risk = target.Downed ? "" : " (it may turn on you)";
            return FloatMenuUtility.DecoratePrioritizedTask(new FloatMenuOption(
                "Take a draftprint of " + target.LabelShort + risk,
                delegate
                {
                    Job job = JobMaker.MakeJob(RM_ContagionDefOf.RM_SampleDraftprint, target);
                    actor.jobs.TryTakeOrderedJob(job, JobTag.Misc);
                }), actor, target);
        }
    }
}
