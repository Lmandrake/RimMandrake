using System.Collections.Generic;
using Verse;
using Verse.AI;

namespace RimMandrake.DivingInteraction
{
    // SCALD_DIVING_MOD_1. Shared shape for both dive jobs: walk onto the
    // tagged cell, hold position for the tunable duration, resolve an
    // outcome. The ENTIRE cost mechanism is standing there — vanilla's own
    // HediffGiver_Terrain (Core/HediffGiverSetDefs/HediffGiverSets.xml) fires
    // on any pawn on burnDamage-carrying terrain every tick this job holds
    // them there. No damage code lives in this class or its subclasses.
    public abstract class RM_JobDriver_DiveBase : JobDriver
    {
        protected abstract string ReportKey { get; }

        protected abstract void ResolveOutcome();

        public override string GetReport()
        {
            return ReportKey;
        }

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(job.targetA.Cell, job, 1, -1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOn(() => !RM_DiveUtility.CellIsDiveSite(TargetLocA, Map));

            yield return Toils_Goto.GotoCell(TargetIndex.A, PathEndMode.OnCell);

            Toil dive = Toils_General.Wait(RM_DivingSettings.diveDurationTicks)
                .WithProgressBarToilDelay(TargetIndex.A);
            yield return dive;

            yield return Toils_General.Do(delegate
            {
                IntVec3 cell = TargetLocA;
                ResolveOutcome();
                Map?.GetComponent<RM_MapComponent_DiveSites>()?.RecordDive(cell);
            });
        }
    }
}
