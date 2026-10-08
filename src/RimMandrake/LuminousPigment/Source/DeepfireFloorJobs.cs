using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.LuminousPigment
{
    // DEEPFIRE_FLOOR_PAINT_1, spec §3.3 floor branch: the designator marks a
    // floor CELL (RM_ApplyDeepfireFloorDesignation, targetType Cell); this
    // WorkGiver/JobDriver pair fetches CostFloorCell Deepfire, walks to the
    // cell, works 600 ticks x WorkSpeedGlobal, then adds one coat to the
    // map component's floor grid. Cell-scanner shape (ShouldSkip /
    // PotentialWorkCellsGlobal / HasJobOnCell / JobOnCell, Floor reservation
    // layer) copied from vanilla WorkGiver_PaintFloor (read via RimSage).
    // One cell per job -- vanilla's queued multi-cell PaintFloor job is an
    // efficiency nicety no proof row needs.
    public class WorkGiver_ApplyDeepfireFloor : WorkGiver_Scanner
    {
        public override PathEndMode PathEndMode => PathEndMode.Touch;

        public override bool ShouldSkip(Pawn pawn, bool forced = false)
        {
            if (!LuminousPigmentSettings.paintingEnabled) return true;
            return !pawn.Map.designationManager.AnySpawnedDesignationOfDef(DeepfireDefOf.RM_ApplyDeepfireFloorDesignation);
        }

        public override IEnumerable<IntVec3> PotentialWorkCellsGlobal(Pawn pawn)
        {
            foreach (Designation d in pawn.Map.designationManager.SpawnedDesignationsOfDef(DeepfireDefOf.RM_ApplyDeepfireFloorDesignation))
            {
                yield return d.target.Cell;
            }
        }

        public override bool HasJobOnCell(Pawn pawn, IntVec3 c, bool forced = false)
        {
            if (!LuminousPigmentSettings.floorsPaintable) return false;
            Map map = pawn.Map;
            if (map.designationManager.DesignationAt(c, DeepfireDefOf.RM_ApplyDeepfireFloorDesignation) == null) return false;
            MapComponent_DeepfireLights mc = MapComponent_DeepfireLights.Get(map);
            if (mc == null || !mc.CanAddFloorCoat(c)) return false;
            if (map.designationManager.DesignationAt(c, DesignationDefOf.RemoveFloor) != null) return false;
            if (!pawn.CanReserveAndReach(c, PathEndMode, Danger.Some, 1, -1, ReservationLayerDefOf.Floor)) return false;

            if (DeepfireCostUtility.FindNearbyDeepfire(pawn, System.Math.Max(1, LuminousPigmentSettings.costFloorCell), forced) == null)
            {
                JobFailReason.Is("No deepfire available.");
                return false;
            }
            return true;
        }

        public override Job JobOnCell(Pawn pawn, IntVec3 cell, bool forced = false)
        {
            Thing stack = DeepfireCostUtility.FindNearbyDeepfire(pawn, System.Math.Max(1, LuminousPigmentSettings.costFloorCell), forced);
            if (stack == null) return null;
            Job job = JobMaker.MakeJob(DeepfireDefOf.RM_ApplyDeepfireFloor, cell, stack);
            job.count = System.Math.Max(1, LuminousPigmentSettings.costFloorCell);
            return job;
        }
    }

    // Same toil shape as JobDriver_ApplyDeepfire, and for the same MEASURED
    // reason it carries no FailOn* conditions (see that class's header):
    // abandonment is checked by hand inside the work toil instead.
    public class JobDriver_ApplyDeepfireFloor : JobDriver
    {
        private const int WorkTicks = 600;
        private const float ArtisticXP = 100f;

        private float workDone;

        private IntVec3 Cell => job.GetTarget(TargetIndex.A).Cell;
        private Thing DeepfireStack => job.GetTarget(TargetIndex.B).Thing;

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            if (!pawn.Reserve(Cell, job, 1, -1, ReservationLayerDefOf.Floor, errorOnFailed)) return false;
            return pawn.Reserve(DeepfireStack, job, job.count, -1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            yield return Toils_Goto.GotoThing(TargetIndex.B, PathEndMode.ClosestTouch);
            yield return Toils_Haul.StartCarryThing(TargetIndex.B, putRemainderInQueue: false, subtractNumTakenFromJobCount: true);
            yield return Toils_Goto.GotoCell(TargetIndex.A, PathEndMode.Touch);

            Toil apply = ToilMaker.MakeToil("ApplyDeepfireFloor");
            apply.initAction = delegate { workDone = 0f; };
            apply.tickIntervalAction = delegate(int delta)
            {
                Map map = pawn.Map;
                MapComponent_DeepfireLights mc = MapComponent_DeepfireLights.Get(map);
                if (mc == null || !mc.CanAddFloorCoat(Cell)
                    || map.designationManager.DesignationAt(Cell, DeepfireDefOf.RM_ApplyDeepfireFloorDesignation) == null)
                {
                    EndJobWith(JobCondition.Incompletable);
                    return;
                }
                pawn.rotationTracker.FaceCell(Cell);
                workDone += pawn.GetStatValue(StatDefOf.WorkSpeedGlobal) * delta;
                if (workDone >= WorkTicks)
                {
                    pawn.skills?.Learn(SkillDefOf.Artistic, ArtisticXP);
                    pawn.carryTracker.CarriedThing?.Destroy();
                    mc.AddFloorCoat(Cell);
                    map.designationManager.TryRemoveDesignation(Cell, DeepfireDefOf.RM_ApplyDeepfireFloorDesignation);
                    ReadyForNextToil();
                }
            };
            apply.defaultCompleteMode = ToilCompleteMode.Never;
            apply.WithEffect(EffecterDefOf.Paint, TargetIndex.A);
            apply.WithProgressBar(TargetIndex.A, () => workDone / WorkTicks, interpolateBetweenActorAndTarget: true);
            apply.activeSkill = () => SkillDefOf.Artistic;
            apply.handlingFacing = true;
            yield return apply;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref workDone, "workDone", 0f);
        }
    }
}
