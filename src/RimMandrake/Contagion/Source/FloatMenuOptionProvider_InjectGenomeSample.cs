using System.Linq;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.Contagion
{
    // CONTAGION_GENOME_ORGAN_GROWING_1. Same FloatMenuOptionProvider shape as
    // RimProperty's providers (e.g.
    // src/RimMandrake/RimProperty/Source/Pickpocket/FloatMenuOptionProvider_Pickpocket.cs):
    // FloatMenuMakerMap.Init() auto-registers every non-abstract subclass via
    // reflection, so no Harmony hook or manual registration is needed. This
    // is the "how the creature is made a vessel" answer from the item's
    // question 4: a right-click interaction on a live AA_RedGoo while
    // carrying a genome sample, not a building.
    public class FloatMenuOptionProvider_InjectGenomeSample : FloatMenuOptionProvider
    {
        protected override bool Drafted => true;

        protected override bool Undrafted => true;

        protected override bool Multiselect => false;

        protected override bool RequiresManipulation => true;

        protected override FloatMenuOption GetSingleOptionFor(Thing clickedThing, FloatMenuContext context)
        {
            if (!RM_ContagionSettings.genomeOrganGrowingEnabled)
            {
                return null;
            }

            if (!(clickedThing is Pawn host))
            {
                return null;
            }
            if (!AmoebaHostUtility.IsEligibleHost(host))
            {
                return null;
            }

            Pawn actor = context.FirstSelectedPawn;
            if (actor?.inventory == null)
            {
                return null;
            }
            Thing sample = actor.inventory.innerContainer.FirstOrDefault(t => t.def == RM_ContagionDefOf.RM_GenomeSample);
            if (sample == null)
            {
                return null;
            }

            if (!actor.CanReach(host, PathEndMode.Touch, Danger.Deadly))
            {
                return new FloatMenuOption(
                    "Cannot inject genome sample: " + "NoPath".Translate().CapitalizeFirst(), null);
            }

            CompGenomeSample comp = sample.TryGetComp<CompGenomeSample>();
            string sourceName = (comp != null && !comp.sourcePawnName.NullOrEmpty()) ? comp.sourcePawnName : "unknown";

            return FloatMenuUtility.DecoratePrioritizedTask(new FloatMenuOption(
                "Inject genome sample (" + sourceName + ") into " + host.LabelShort,
                delegate
                {
                    Job job = JobMaker.MakeJob(RM_ContagionDefOf.RM_InjectGenomeSample, host);
                    actor.jobs.TryTakeOrderedJob(job, JobTag.Misc);
                }), actor, host);
        }
    }
}
