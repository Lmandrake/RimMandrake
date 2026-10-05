using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.GimmeSomeSlack.Hose.Jobs
{
    /// <summary>
    /// Design section 4: go to the reel, start winding (Laid/Dropped -> Retracting), wind windCellsPerSecond x the winder's
    /// Manipulation (clamped 0.3-1.5) until the hose is Stored. Interrupted: the hose stays out, shortened by what was wound
    /// (StopWind -> Dropped), and the Retract order is kept for a resume.
    /// </summary>
    public class JobDriver_RetractHose : JobDriver
    {
        private const TargetIndex ReelInd = TargetIndex.A;
        private const int WindEvery = 10;   // the wound length check pulls the trail taut: every 10 ticks, not every tick

        /// <summary>Runtime: the hose length when winding started (progress bar only).</summary>
        private float total = 1f;

        private CompHoseReel Reel => HoseJobs.ReelOf(job);
        private bool WindingIt => Reel != null && Reel.carry == HoseCarryState.Retracting && Reel.carrier == pawn;

        public override bool TryMakePreToilReservations(bool errorOnFailed) =>
            pawn.Reserve(job.GetTarget(ReelInd), job, 1, -1, null, errorOnFailed);

        private float CellsPerTick()
        {
            float m = Mathf.Clamp(pawn.health.capacities.GetLevel(PawnCapacityDefOf.Manipulation), 0.3f, 1.5f);
            return HoseJobTuning.windCellsPerSecond * m / 60f;
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedOrNull(ReelInd);
            this.FailOn(() => !job.playerForced && Reel != null && Reel.parent.IsForbidden(pawn));
            this.FailOn(() => Reel == null || !HoseSettings.enabled);
            // cancelled, or someone else is carrying / winding it (a finished wind reads Stored: not a failure)
            this.FailOn(() => Reel.carry != HoseCarryState.Stored && Reel.pending != HosePendingOrder.Retract && !WindingIt);
            this.FailOn(() => Reel.carry == HoseCarryState.Carrying || (Reel.carry == HoseCarryState.Retracting && Reel.carrier != pawn));
            AddFinishAction(cond =>
            {
                CompHoseReel r = Reel;
                if (r != null && r.carry == HoseCarryState.Retracting && r.carrier == pawn) r.StopWind(pawn);
            });

            Toil wind = ToilMaker.MakeToil("RM_WindHose");
            yield return Toils_Jump.JumpIf(wind, () => WindingIt);   // resumed after a load
            yield return Toils_Goto.GotoThing(ReelInd, PathEndMode.Touch);
            yield return Toils_General.Do(() =>
            {
                if (!Reel.BeginWind(pawn)) EndJobWith(JobCondition.Incompletable);
            });

            wind.initAction = () => total = Mathf.Max(1f, Reel.TrailLength());
            wind.tickAction = () =>
            {
                if (!WindingIt) { if (Reel.carry == HoseCarryState.Stored) ReadyForNextToil(); return; }
                if (!pawn.IsHashIntervalTick(WindEvery)) return;
                if (Reel.WindBy(pawn, CellsPerTick() * WindEvery)) ReadyForNextToil();
            };
            wind.defaultCompleteMode = ToilCompleteMode.Never;
            wind.handlingFacing = true;
            wind.FailOn(() => !WindingIt && Reel.carry != HoseCarryState.Stored);
            wind.WithProgressBar(ReelInd, () => Reel == null ? 1f : Mathf.Clamp01(Reel.wound / total));
            wind.AddPreTickAction(() => pawn.rotationTracker.FaceTarget(job.GetTarget(ReelInd)));
            yield return wind;
        }
    }
}
