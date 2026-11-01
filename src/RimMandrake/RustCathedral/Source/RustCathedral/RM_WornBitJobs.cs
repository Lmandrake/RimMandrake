using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.RustCathedral
{
    /// <summary>Stage 1. Two colonists at once or nothing moves; a lone worker gives up after a while, so an order is never a
    /// trap. The hulk is not held still: it wanders off, the job ends, progress waits on the comp.</summary>
    public class RM_JobDriver_UnbitBorehulk : JobDriver
    {
        private const int LoneWaitTicks = 3000;

        private Pawn Hulk => (Pawn)job.targetA.Thing;

        private int stalled;

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return true;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref stalled, "stalled", 0);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedOrNull(TargetIndex.A);
            RM_CompBorehulkDrill comp = Hulk?.TryGetComp<RM_CompBorehulkDrill>();
            this.FailOn(() => comp == null || comp.State != RM_BorehulkDrillState.Worn);
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);
            Toil work = ToilMaker.MakeToil("RM_UnbitWork");
            work.defaultCompleteMode = ToilCompleteMode.Never;
            work.handlingFacing = true;
            work.tickAction = delegate
            {
                pawn.rotationTracker.FaceTarget(Hulk);
                if (!pawn.Position.InHorDistOf(Hulk.Position, 2.9f))
                {
                    EndJobWith(JobCondition.Incompletable);
                    return;
                }
                int workers = RM_WornBit.WorkersAt(Hulk, job.def);
                float speed = pawn.GetStatValue(StatDefOf.ConstructionSpeed);
                float added = RM_WornBit.UnbitTick(comp, workers, speed);
                pawn.skills?.Learn(SkillDefOf.Construction, 0.08f);
                stalled = added > 0f ? 0 : stalled + 1;
                if (stalled > LoneWaitTicks)
                {
                    Messages.Message(pawn.LabelShort + " stops: the boom needs a second pair of hands and a calm hum.", Hulk, MessageTypeDefOf.NeutralEvent, historical: false);
                    EndJobWith(JobCondition.Incompletable);
                }
            };
            work.WithEffect(EffecterDefOf.ConstructMetal, TargetIndex.A);
            yield return work;
        }
    }

    /// <summary>Shared by restoration and service: fetch what the machine still wants, one stack a trip, then work.</summary>
    public abstract class RM_JobDriver_BorehulkFetchAndWork : JobDriver
    {
        protected Pawn Hulk => (Pawn)job.targetA.Thing;

        protected RM_CompBorehulkDrill Comp => Hulk?.TryGetComp<RM_CompBorehulkDrill>();

        protected abstract ThingDef NextWanted(out int count);

        protected abstract void Delivered(ThingDef def, int count);

        protected abstract Toil WorkToil();

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return true;
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedOrNull(TargetIndex.A);
            this.FailOn(() => Comp == null || !StillWanted());
            Toil work = WorkToil();
            Toil pick = ToilMaker.MakeToil("RM_PickWanted");
            pick.defaultCompleteMode = ToilCompleteMode.Instant;
            pick.initAction = delegate
            {
                ThingDef def = NextWanted(out int count);
                if (def == null)
                {
                    JumpToToil(work);
                    return;
                }
                Thing thing = RM_WornBit.Available(pawn.Map, def)
                    .Where(t => !t.IsForbidden(pawn) && pawn.CanReserveAndReach(t, PathEndMode.ClosestTouch, Danger.Deadly))
                    .OrderBy(t => t.Position.DistanceToSquared(pawn.Position)).FirstOrDefault();
                if (thing == null)
                {
                    Messages.Message(pawn.LabelShort + " cannot reach any " + def.label + ".", Hulk, MessageTypeDefOf.RejectInput, historical: false);
                    EndJobWith(JobCondition.Incompletable);
                    return;
                }
                job.SetTarget(TargetIndex.B, thing);
                job.count = Mathf.Min(count, thing.stackCount);
                pawn.Reserve(thing, job);
            };
            yield return pick;
            yield return Toils_Goto.GotoThing(TargetIndex.B, PathEndMode.ClosestTouch).FailOnDespawnedNullOrForbidden(TargetIndex.B);
            yield return Toils_Haul.StartCarryThing(TargetIndex.B);
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);
            Toil fit = ToilMaker.MakeToil("RM_FitCarried");
            fit.defaultCompleteMode = ToilCompleteMode.Instant;
            fit.initAction = delegate
            {
                Thing carried = pawn.carryTracker.CarriedThing;
                if (carried != null)
                {
                    Delivered(carried.def, carried.stackCount);
                    pawn.carryTracker.DestroyCarriedThing();
                }
                job.SetTarget(TargetIndex.B, LocalTargetInfo.Invalid);
            };
            yield return fit;
            yield return Toils_Jump.Jump(pick);
            yield return work;
        }

        protected abstract bool StillWanted();
    }

    public class RM_JobDriver_RestoreBorehulk : RM_JobDriver_BorehulkFetchAndWork
    {
        private float sessionDone;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref sessionDone, "sessionDone", 0f);
        }

        protected override bool StillWanted()
        {
            return Comp.State == RM_BorehulkDrillState.Unbitted;
        }

        protected override ThingDef NextWanted(out int count)
        {
            foreach (ThingDefCountClass row in RM_WornBitDefOf.RM_BorehulkRestoration.ingredients)
            {
                int left = row.count - Comp.Delivered(row.thingDef);
                if (left > 0)
                {
                    count = left;
                    return row.thingDef;
                }
            }
            count = 0;
            return null;
        }

        protected override void Delivered(ThingDef def, int count)
        {
            Comp.Deliver(def, count);
        }

        protected override Toil WorkToil()
        {
            Toil work = ToilMaker.MakeToil("RM_RestoreWork");
            work.defaultCompleteMode = ToilCompleteMode.Never;
            work.handlingFacing = true;
            work.tickAction = delegate
            {
                RM_CompBorehulkDrill comp = Comp;
                pawn.rotationTracker.FaceTarget(Hulk);
                if (comp.choice == RM_WornBitChoice.None
                    && RM_WornBitKernel.ChoiceDue(comp.restoreProgress, RM_RustCathedralSettings.wornBitRestoreWork, comp.choice))
                {
                    RM_WornBit.OpenChoiceDialog(comp);
                    EndJobWith(JobCondition.Succeeded);
                    return;
                }
                float add = pawn.GetStatValue(StatDefOf.GeneralLaborSpeed);
                comp.restoreProgress += add;
                sessionDone += add;
                pawn.skills?.Learn(SkillDefOf.Crafting, 0.08f);
                if (comp.choice != RM_WornBitChoice.None && comp.restoreProgress >= RM_RustCathedralSettings.wornBitRestoreWork)
                {
                    RM_WornBit.FinishRestoration(comp);
                    EndJobWith(JobCondition.Succeeded);
                }
                else if (sessionDone >= RM_RustCathedralSettings.wornBitSessionWork)
                {
                    // The work is two sessions at least: the worker has to stop and come back.
                    Messages.Message(pawn.LabelShort + " stops for the day. The restoration waits for the next session.", Hulk, MessageTypeDefOf.NeutralEvent, historical: false);
                    EndJobWith(JobCondition.Succeeded);
                }
            };
            work.WithEffect(EffecterDefOf.ConstructMetal, TargetIndex.A);
            return work;
        }
    }

    public class RM_JobDriver_ServiceBorehulk : RM_JobDriver_BorehulkFetchAndWork
    {
        private const int WorkTicks = 600;

        private int comps;
        private int fuel;
        private int done;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref comps, "comps", 0);
            Scribe_Values.Look(ref fuel, "fuel", 0);
            Scribe_Values.Look(ref done, "done", 0);
        }

        protected override bool StillWanted()
        {
            return Comp.Kept;
        }

        protected override ThingDef NextWanted(out int count)
        {
            count = RM_RustCathedralSettings.wornBitServiceComponents - comps;
            if (count > 0)
            {
                return ThingDefOf.ComponentIndustrial;
            }
            count = RM_RustCathedralSettings.wornBitServiceChemfuel - fuel;
            return count > 0 ? ThingDefOf.Chemfuel : null;
        }

        protected override void Delivered(ThingDef def, int count)
        {
            if (def == ThingDefOf.ComponentIndustrial)
            {
                comps += count;
            }
            else
            {
                fuel += count;
            }
        }

        protected override Toil WorkToil()
        {
            Toil work = ToilMaker.MakeToil("RM_ServiceWork");
            work.defaultCompleteMode = ToilCompleteMode.Never;
            work.tickAction = delegate
            {
                if (++done >= WorkTicks)
                {
                    Comp.lastServiceTick = Find.TickManager.TicksGame;
                    EndJobWith(JobCondition.Succeeded);
                }
            };
            work.WithEffect(EffecterDefOf.ConstructMetal, TargetIndex.A);
            return work;
        }
    }
}
