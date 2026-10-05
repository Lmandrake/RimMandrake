using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.MessyConduit.Hose.Jobs
{
    [DefOf]
    public static class HoseJobDefOf
    {
        public static JobDef RM_CarryHoseEnd;
        public static JobDef RM_RetractHose;

        static HoseJobDefOf() => DefOfHelper.EnsureInitializedInCtor(typeof(HoseJobDefOf));
    }

    /// <summary>Handling times and winding speed (design sections 4, 9, 12). Plain statics so S5 can put them on the
    /// hose settings page; the defaults are the shipped behaviour.</summary>
    public static class HoseJobTuning
    {
        public static int grabTicks = 45;
        public static int setDownTicks = 30;
        public static int coupleTicks = 90;
        public static float windCellsPerSecond = 3f;
        /// <summary>Design section 2: an interrupted order (end dropped, order kept) is picked up again by an idle colonist.</summary>
        public static bool autoResumeDroppedHose = true;
    }

    /// <summary>Job construction and the holder test the reel's 30-tick check uses (design section 5 b).</summary>
    [StaticConstructorOnStartup]
    public static class HoseJobs
    {
        static HoseJobs()
        {
            CompHoseReel.HoldsReel = Holds;
        }

        public static CompHoseReel ReelOf(Job job) => job?.targetA.Thing?.TryGetComp<CompHoseReel>();

        /// <summary>Is this pawn's CURRENT driver one of ours, on this reel?</summary>
        public static bool Holds(Pawn p, CompHoseReel r)
        {
            JobDriver d = p?.jobs?.curDriver;
            if (!(d is JobDriver_CarryHoseEnd) && !(d is JobDriver_RetractHose)) return false;
            return d.job != null && d.job.targetA.Thing == r.parent;
        }

        /// <summary>targetA = the reel, targetB = the order's destination (pendingAt). Jogging: fast is the point.</summary>
        public static Job MakeCarry(CompHoseReel r)
        {
            Job j = JobMaker.MakeJob(HoseJobDefOf.RM_CarryHoseEnd, r.parent, r.pendingAt);
            j.locomotionUrgency = LocomotionUrgency.Jog;
            return j;
        }

        public static Job MakeRetract(CompHoseReel r)
        {
            Job j = JobMaker.MakeJob(HoseJobDefOf.RM_RetractHose, r.parent);
            j.locomotionUrgency = LocomotionUrgency.Jog;
            return j;
        }

        /// <summary>A direct (right-click / probe) order: forced, so allowed areas are ignored and a drafted pawn may run it.</summary>
        public static bool GiveForced(Pawn p, Job j)
        {
            j.playerForced = true;
            return p.jobs.TryTakeOrderedJob(j, JobTag.Misc);
        }
    }

    /// <summary>
    /// Design section 4: walk to the hose end (the reel when Stored, the free end when Laid/Dropped), grab it, carry it to
    /// targetB while the reel records the cells walked (CompHoseReel.CarrierStep), set it down / couple it. Any end but
    /// success drops the end where the carrier stands (finish action), backed by the reel's own 30-tick holder check.
    /// The reel is authoritative: after a load this driver resumes at its toil and simply carries on stepping.
    /// </summary>
    public class JobDriver_CarryHoseEnd : JobDriver
    {
        private const TargetIndex ReelInd = TargetIndex.A;
        private const TargetIndex DestInd = TargetIndex.B;
        private const TargetIndex EndInd = TargetIndex.C;

        /// <summary>Runtime only: the last cell handed to CarrierStep.</summary>
        private IntVec3 lastStep = IntVec3.Invalid;
        /// <summary>Runtime only: the final toil ran (the order is cleared by FinishCarry, which must not read as a failure).</summary>
        private bool finished;

        private CompHoseReel Reel => HoseJobs.ReelOf(job);
        private IntVec3 Dest => job.GetTarget(DestInd).Cell;

        private bool CarryingIt => Reel != null && Reel.carry == HoseCarryState.Carrying && Reel.carrier == pawn;

        /// <summary>The reel still wants THIS carry: a Deploy/Move order to our destination.</summary>
        private bool OrderStillMine()
        {
            CompHoseReel r = Reel;
            if (r == null) return false;
            return (r.pending == HosePendingOrder.Deploy || r.pending == HosePendingOrder.Move) && r.pendingAt == Dest;
        }

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            // one hand on a hose at a time (design section 4.1)
            if (!pawn.Reserve(job.GetTarget(ReelInd), job, 1, -1, null, errorOnFailed)) return false;
            CompHoseReel r = Reel;
            if (r != null && Dest.IsValid && !r.IsBringBack(Dest) && Dest.Standable(pawn.Map))
                pawn.Map.pawnDestinationReservationManager.Reserve(pawn, job, Dest);   // the rope precedent
            return true;
        }

        private PathEndMode WalkEndMode()
        {
            CompHoseReel r = Reel;
            if (r == null || !Dest.IsValid) return PathEndMode.Touch;
            if (r.IsBringBack(Dest)) return PathEndMode.Touch;
            return Dest.Standable(pawn.Map) ? PathEndMode.OnCell : PathEndMode.Touch;   // water, a tank side, a relay intake
        }

        private int SetDownTicks()
        {
            CompHoseReel r = Reel;
            RM_MapComponent_Hoses comp = r != null && r.parent.Spawned ? r.parent.Map.GetComponent<RM_MapComponent_Hoses>() : null;
            bool couples = comp != null && Dest.IsValid && comp.RelayAt(r, new Core.Cell(Dest.x, Dest.z)) != null;
            return couples ? HoseJobTuning.coupleTicks : HoseJobTuning.setDownTicks;
        }

        /// <summary>Every tick while carrying: a new cell goes to the reel's trail rule. Cells of the reel itself are skipped
        /// (a carrier cutting across the drum must not read as "walked back to the reel"), except when bringing it back.</summary>
        private void Step()
        {
            CompHoseReel r = Reel;
            if (r == null || !CarryingIt) return;
            IntVec3 c = pawn.Position;
            if (c == lastStep) return;
            lastStep = c;
            if (r.parent.OccupiedRect().Contains(c) && !r.IsBringBack(Dest)) return;
            TrailStep s = r.CarrierStep(pawn, c);
            if (s == TrailStep.Stowed) { finished = true; EndJobWith(JobCondition.Succeeded); }
            else if (s == TrailStep.Stretched) EndJobWith(JobCondition.Incompletable);   // the reel dropped it and told the player
        }

        private void OnFinish(JobCondition cond)
        {
            CompHoseReel r = Reel;
            if (r == null || r.carry != HoseCarryState.Carrying || r.carrier != pawn) return;
            // a path failure (Incompletable/Errored) on a still-current order clears it: resuming would loop (section 5).
            // Everything else (draft, another order, downed, a new order for this reel) keeps the order for a resume.
            bool unreachable = (cond == JobCondition.Incompletable || cond == JobCondition.Errored) && OrderStillMine();
            r.DropCarry(pawn, !unreachable);
            if (unreachable && r.parent.Faction == Faction.OfPlayer)
                Messages.Message("Hose end dropped at " + r.far + ": could not reach " + Dest + ".", new LookTargets(r.parent), MessageTypeDefOf.RejectInput, false);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedOrNull(ReelInd);
            this.FailOn(() => !job.playerForced && Reel != null && Reel.parent.IsForbidden(pawn));
            this.FailOn(() => !finished && !OrderStillMine());
            this.FailOn(() => Reel == null || !HoseSettings.enabled);
            // someone else holds it, or it is being wound in
            this.FailOn(() => Reel.carry == HoseCarryState.Retracting || (Reel.carry == HoseCarryState.Carrying && Reel.carrier != pawn));
            AddFinishAction(OnFinish);

            Toil walk = Toils_Goto.Goto(DestInd, WalkEndMode());
            walk.AddPreTickAction(Step);
            walk.FailOn(() => !CarryingIt);

            // after a load mid-carry the driver resumes at its toil index; a fresh job held by us (cannot normally happen) skips ahead
            yield return Toils_Jump.JumpIf(walk, () => CarryingIt);

            // 1. go to the end: the reel's side when Stored, the free end where it lies otherwise (Touch: it may lie in water)
            Toil gotoEnd = ToilMaker.MakeToil("RM_GotoHoseEnd");
            gotoEnd.initAction = () =>
            {
                CompHoseReel r = Reel;
                if (r.carry == HoseCarryState.Stored)
                {
                    job.SetTarget(EndInd, r.parent);
                    pawn.pather.StartPath(r.parent, PathEndMode.Touch);
                }
                else
                {
                    job.SetTarget(EndInd, r.far);
                    pawn.pather.StartPath(r.far, PathEndMode.Touch);
                }
            };
            gotoEnd.defaultCompleteMode = ToilCompleteMode.PatherArrival;
            gotoEnd.FailOn(() => Reel.carry == HoseCarryState.Stored && Reel.pending != HosePendingOrder.Deploy);
            yield return gotoEnd;

            // 2. grab it
            Toil grabWait = Toils_General.Wait(HoseJobTuning.grabTicks, EndInd);
            grabWait.WithProgressBarToilDelay(EndInd);
            yield return grabWait;
            Toil grab = Toils_General.Do(() =>
            {
                lastStep = IntVec3.Invalid;
                if (!Reel.BeginCarry(pawn)) { EndJobWith(JobCondition.Incompletable); return; }
                Step();   // the cell he stands in is the trail's first walked cell
            });
            yield return grab;

            // 3. carry it (the reel records the walk; the hose is re-laid along the trail on each change: S3's draw)
            yield return walk;

            // 4. set it down / couple it, then 5. finish
            Toil setDown = Toils_General.Wait(SetDownTicks(), DestInd);
            setDown.AddPreTickAction(Step);
            setDown.FailOn(() => !CarryingIt);
            setDown.WithProgressBarToilDelay(DestInd);
            yield return setDown;
            yield return Toils_General.Do(() =>
            {
                CompHoseReel r = Reel;
                bool bringBack = r.IsBringBack(Dest);
                finished = true;
                if (!r.FinishCarry(pawn, bringBack ? IntVec3.Invalid : Dest)) return;
                if (bringBack) r.ReelIn();   // carried back to the reel: stowed
            });
        }
    }
}
