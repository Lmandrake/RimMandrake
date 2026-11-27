// The two jobs of the repair on the machine (DESIGN.md "The repair on the machine") and the Construction work giver that gives
// them: in the Ordered phase carry a missing material into the machine, in the Working phase work on it where it stands.
// The toils follow the base game's JobDriver_ConstructFinishFrame (work rate, skill gain, completion mode) read from the 1.6 decomp.
using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.WreckedMachines
{
    public static class RM_RepairDefs
    {
        private static JobDef deliver, repair;

        public static JobDef Deliver => deliver ?? (deliver = DefDatabase<JobDef>.GetNamedSilentFail("RM_WM_DeliverToRepair"));
        public static JobDef Repair => repair ?? (repair = DefDatabase<JobDef>.GetNamedSilentFail("RM_WM_RepairMachine"));
    }

    public class WorkGiver_RepairMachine : WorkGiver_Scanner
    {
        public override PathEndMode PathEndMode => PathEndMode.Touch;

        public override Danger MaxPathDanger(Pawn pawn) => Danger.Deadly;

        public override IEnumerable<Thing> PotentialWorkThingsGlobal(Pawn pawn)
        {
            foreach (Thing t in pawn.Map.listerThings.ThingsInGroup(ThingRequestGroup.BuildingArtificial))
            {
                CompWreckedMachine c = t.TryGetComp<CompWreckedMachine>();
                if (c != null && c.Active) yield return t;
            }
        }

        public override bool ShouldSkip(Pawn pawn, bool forced = false)
        {
            if (RM_RepairDefs.Deliver == null || RM_RepairDefs.Repair == null) return true;
            foreach (Thing t in pawn.Map.listerThings.ThingsInGroup(ThingRequestGroup.BuildingArtificial))
            {
                CompWreckedMachine c = t.TryGetComp<CompWreckedMachine>();
                if (c != null && c.Active) return false;
            }
            return true;
        }

        /// <summary>The machine may be worked on by this pawn now (shared by both phases).</summary>
        private static CompWreckedMachine Workable(Pawn pawn, Thing t, bool forced)
        {
            CompWreckedMachine c = t.TryGetComp<CompWreckedMachine>();
            if (c == null || !c.Active || !t.Spawned) return null;
            if (t.Faction != null && t.Faction != pawn.Faction) return null;
            if (t.IsForbidden(pawn) || t.IsBurning()) return null;
            if (t.Map.designationManager.DesignationOn(t, DesignationDefOf.Uninstall) != null
                || t.Map.designationManager.DesignationOn(t, DesignationDefOf.Deconstruct) != null) return null;
            if (!c.SiteOk())
            {
                JobFailReason.Is("The repair waits: the line is off or the ground is wrong.");
                return null;
            }
            if (!pawn.CanReserve(t, 1, -1, null, forced)) return null;
            return c;
        }

        /// <summary>The closest material the repair still misses that this pawn can reach and reserve.</summary>
        public static Thing FindMaterial(Pawn pawn, CompWreckedMachine c, bool forced, out int count)
        {
            count = 0;
            RM_RepairRecord rec = c.rec;
            for (int i = 0; i < rec.defs.Length; i++)
            {
                int missing = RM_WreckedMachinesRepair.Missing(rec, rec.defs[i]);
                if (missing <= 0) continue;
                ThingDef d = DefDatabase<ThingDef>.GetNamedSilentFail(rec.defs[i]);
                if (d == null) continue;
                Thing found = GenClosest.ClosestThingReachable(pawn.Position, pawn.Map, ThingRequest.ForDef(d), PathEndMode.ClosestTouch,
                    TraverseParms.For(pawn), 9999f, x => !x.IsForbidden(pawn) && pawn.CanReserve(x, 1, -1, null, forced));
                if (found == null) continue;
                count = System.Math.Min(missing, found.stackCount);
                int space = pawn.carryTracker.MaxStackSpaceEver(d);
                if (space > 0) count = System.Math.Min(count, space);
                if (count > 0) return found;
            }
            return null;
        }

        public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            CompWreckedMachine c = Workable(pawn, t, forced);
            if (c == null) return false;
            if (c.rec.phase == RM_WreckedMachinesRepair.Ordered)
            {
                if (FindMaterial(pawn, c, forced, out _) != null) return true;
                JobFailReason.Is("No reachable material for the repair.");
                return false;
            }
            return c.rec.phase == RM_WreckedMachinesRepair.Working;
        }

        public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            CompWreckedMachine c = Workable(pawn, t, forced);
            if (c == null) return null;
            if (c.rec.phase == RM_WreckedMachinesRepair.Ordered)
            {
                Thing m = FindMaterial(pawn, c, forced, out int count);
                if (m == null) return null;
                Job j = JobMaker.MakeJob(RM_RepairDefs.Deliver, m, t);
                j.count = count;
                j.haulMode = HaulMode.ToContainer;
                return j;
            }
            if (c.rec.phase == RM_WreckedMachinesRepair.Working) return JobMaker.MakeJob(RM_RepairDefs.Repair, t);
            return null;
        }
    }

    /// <summary>Ordered phase: carry one material (TargetA) to the machine (TargetB) and put it in. The record takes what it misses;
    /// exactly that many leave the world and the rest stays in the pawn's hands.</summary>
    public class JobDriver_DeliverToRepair : JobDriver
    {
        private Thing Machine => job.GetTarget(TargetIndex.B).Thing;
        private CompWreckedMachine Comp => Machine?.TryGetComp<CompWreckedMachine>();

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(job.targetA, job, 1, job.count, null, errorOnFailed)
                && pawn.Reserve(job.targetB, job, 1, -1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDestroyedOrNull(TargetIndex.B);
            this.FailOn(() => Comp == null || Comp.rec.phase != RM_WreckedMachinesRepair.Ordered || !Comp.SiteOk());
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.ClosestTouch)
                .FailOnDespawnedNullOrForbidden(TargetIndex.A).FailOnSomeonePhysicallyInteracting(TargetIndex.A);
            yield return Toils_Haul.StartCarryThing(TargetIndex.A, false, true);
            yield return Toils_Goto.GotoThing(TargetIndex.B, PathEndMode.Touch);
            Toil put = ToilMaker.MakeToil("DeliverToRepair");
            put.initAction = delegate
            {
                Thing carried = pawn.carryTracker.CarriedThing;
                CompWreckedMachine c = Comp;
                if (carried == null || c == null) return;
                int taken = c.Deliver(carried.def, carried.stackCount);
                if (taken > 0)
                {
                    Thing part = carried.SplitOff(taken);
                    if (!part.Destroyed) part.Destroy(DestroyMode.Vanish);
                }
            };
            put.defaultCompleteMode = ToilCompleteMode.Instant;
            yield return put;
        }
    }

    /// <summary>Working phase: work on the machine where it stands (ClosestTouch), at the base game's construction rate.</summary>
    public class JobDriver_RepairMachine : JobDriver
    {
        private Thing Machine => job.GetTarget(TargetIndex.A).Thing;
        private CompWreckedMachine Comp => Machine?.TryGetComp<CompWreckedMachine>();

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(job.targetA, job, 1, -1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.ClosestTouch).FailOnDespawnedNullOrForbidden(TargetIndex.A);
            Toil work = ToilMaker.MakeToil("RepairMachine");
            work.tickIntervalAction = delegate(int delta)
            {
                Pawn actor = work.actor;
                CompWreckedMachine c = Comp;
                if (c == null || c.rec.phase != RM_WreckedMachinesRepair.Working || !c.SiteOk())
                {
                    EndJobWith(JobCondition.Incompletable);
                    return;
                }
                actor.skills?.Learn(SkillDefOf.Construction, 0.25f * delta);
                actor.rotationTracker.FaceTarget(Machine);
                float amount = actor.GetStatValue(StatDefOf.ConstructionSpeed) * 1.7f * delta;
                if (c.DoWork(amount) != null) ReadyForNextToil();
            };
            work.WithProgressBar(TargetIndex.A, () =>
            {
                CompWreckedMachine c = Comp;
                return c == null || c.rec.workTotal <= 0f ? 0f : c.rec.workDone / c.rec.workTotal;
            });
            work.FailOnDespawnedNullOrForbidden(TargetIndex.A);
            work.defaultCompleteMode = ToilCompleteMode.Delay;
            work.defaultDuration = 5000;
            work.activeSkill = () => SkillDefOf.Construction;
            work.handlingFacing = true;
            yield return work;
        }
    }
}
