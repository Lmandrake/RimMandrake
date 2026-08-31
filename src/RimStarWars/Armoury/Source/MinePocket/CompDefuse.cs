using System.Collections.Generic;
using Verse;
using Verse.AI;

namespace MinePocket;

public class CompDefuse : ThingComp
{
    public override IEnumerable<FloatMenuOption> CompFloatMenuOptions(Pawn selPawn)
    {
        if (selPawn.CanReach(parent, PathEndMode.Touch, Danger.Deadly))
        {
            yield return new FloatMenuOption("Defuse mine", delegate
            {
                Job job = JobMaker.MakeJob(MineDefOfs.MinePocket_Job, parent);
                selPawn.jobs.TryTakeOrderedJob(job, JobTag.Misc);
            });
        }
    }
}
