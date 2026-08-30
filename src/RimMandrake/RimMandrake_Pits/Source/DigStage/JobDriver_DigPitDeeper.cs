using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.Pits
{
    // Deepens a Building_PitDigSite by one stage. Modeled on
    // RimWorld/JobDriver_RemoveBuilding (the vanilla base JobDriver_FillIn
    // itself uses), but MiningSpeed-scaled rather than ConstructionSpeed -
    // deepening an already-placed pit reads as digging, and this is the hook
    // point where a future Jawa species dig-speed bonus (campaign layer,
    // spec section 9) attaches without touching this class.
    public class JobDriver_DigPitDeeper : JobDriver
    {
        private float workLeft;
        private float totalWork;

        private Thing DigSite => job.targetA.Thing;
        private CompPitDigStage Comp => DigSite?.TryGetComp<CompPitDigStage>();

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(DigSite, job, 1, -1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedNullOrForbidden(TargetIndex.A);
            this.FailOn(() => Comp == null || !Comp.NeedsMoreDigging);

            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);

            Toil dig = ToilMaker.MakeToil("MakeNewToils");
            dig.initAction = delegate
            {
                totalWork = Comp.workLeftThisStage;
                workLeft = totalWork;
            };
            dig.tickIntervalAction = delegate(int delta)
            {
                float amount = pawn.GetStatValue(StatDefOf.MiningSpeed) * (float)delta;
                workLeft -= amount;
                if (pawn.skills != null)
                {
                    pawn.skills.Learn(SkillDefOf.Mining, 0.08f * (float)delta);
                }
                if (workLeft <= 0f)
                {
                    Comp.AddDigWork(totalWork);
                    base.Map.designationManager.TryRemoveDesignationOn(DigSite, RMPits_DesignationDefOf.RM_DigPitDeeper);
                    ReadyForNextToil();
                }
            };
            dig.defaultCompleteMode = ToilCompleteMode.Never;
            dig.WithProgressBar(TargetIndex.A, () => 1f - workLeft / totalWork);
            dig.FailOnCannotTouch(TargetIndex.A, PathEndMode.Touch);
            dig.activeSkill = () => SkillDefOf.Mining;
            yield return dig;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref workLeft, "workLeft", 0f);
            Scribe_Values.Look(ref totalWork, "totalWork", 0f);
        }
    }
}
