using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.Scarlands
{
    // WARSCAR_AEROSOL_SCREEN_1 part 7: evaluate / salvage / repair of the projector rings.
    // Driven by designations toggled from the ring's gizmos (RM_CompWarscarRing.CompGetGizmosExtra).
    // The WreckedMachines ladder is a def-level DefModExtension, not a comp, so it is NOT reused: repair is
    // the job below (a Failing salvaged ring -> Working, costs 2 industrial components).

    [DefOf]
    public static class RM_RingDesignations
    {
        public static DesignationDef RM_EvaluateRing;
        public static DesignationDef RM_SalvageRing;
        public static DesignationDef RM_RepairRing;
        public static DesignationDef Evaluate => RM_EvaluateRing;
        public static DesignationDef Salvage => RM_SalvageRing;
        public static DesignationDef Repair => RM_RepairRing;
        static RM_RingDesignations() { DefOfHelper.EnsureInitializedInCtor(typeof(RM_RingDesignations)); }
    }

    public abstract class RM_WorkGiver_RingBase : WorkGiver_Scanner
    {
        protected abstract DesignationDef Desig { get; }
        protected abstract JobDef JobDefToUse { get; }
        protected abstract int MinCrafting { get; }
        protected virtual bool Gated { get { return false; } }

        public override PathEndMode PathEndMode { get { return PathEndMode.Touch; } }

        public override bool ShouldSkip(Pawn pawn, bool forced = false)
        {
            if (Gated && !RM_WarscarSettings.ringSalvageEnabled) return true;
            return !pawn.Map.designationManager.AnySpawnedDesignationOfDef(Desig);
        }

        public override IEnumerable<Thing> PotentialWorkThingsGlobal(Pawn pawn)
        {
            foreach (Designation d in pawn.Map.designationManager.SpawnedDesignationsOfDef(Desig))
                if (d.target.HasThing) yield return d.target.Thing;
        }

        protected virtual bool ThingOk(RM_CompWarscarRing c) { return true; }

        public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            if (pawn.Map.designationManager.DesignationOn(t, Desig) == null) return null;
            RM_CompWarscarRing c = t.TryGetComp<RM_CompWarscarRing>();
            if (c == null || !ThingOk(c)) return null;
            if (!pawn.CanReserve(t, 1, -1, null, forced)) return null;
            if (pawn.skills == null || pawn.skills.GetSkill(SkillDefOf.Crafting).Level < MinCrafting)
            {
                JobFailReason.Is("needs Crafting " + MinCrafting);
                return null;
            }
            return Make(pawn, t, c);
        }

        protected virtual Job Make(Pawn pawn, Thing t, RM_CompWarscarRing c) { return JobMaker.MakeJob(JobDefToUse, t); }
    }

    public class RM_WorkGiver_EvaluateRing : RM_WorkGiver_RingBase
    {
        protected override DesignationDef Desig { get { return RM_RingDesignations.Evaluate; } }
        protected override JobDef JobDefToUse { get { return DefDatabase<JobDef>.GetNamed("RM_EvaluateRing"); } }
        protected override int MinCrafting { get { return 6; } }
        protected override bool ThingOk(RM_CompWarscarRing c) { return !c.Evaluated; }
    }

    public class RM_WorkGiver_SalvageRing : RM_WorkGiver_RingBase
    {
        protected override DesignationDef Desig { get { return RM_RingDesignations.Salvage; } }
        protected override JobDef JobDefToUse { get { return DefDatabase<JobDef>.GetNamed("RM_SalvageRing"); } }
        protected override int MinCrafting { get { return 6; } }
        protected override bool Gated { get { return true; } }
        protected override bool ThingOk(RM_CompWarscarRing c) { return c.Evaluated && c.RingProps.wild; }
    }

    public class RM_WorkGiver_RepairRing : RM_WorkGiver_RingBase
    {
        protected override DesignationDef Desig { get { return RM_RingDesignations.Repair; } }
        protected override JobDef JobDefToUse { get { return DefDatabase<JobDef>.GetNamed("RM_RepairRing"); } }
        protected override int MinCrafting { get { return 8; } }
        protected override bool Gated { get { return true; } }
        protected override bool ThingOk(RM_CompWarscarRing c) { return !c.RingProps.wild && c.Condition == RingCondition.Failing; }

        protected override Job Make(Pawn pawn, Thing t, RM_CompWarscarRing c)
        {
            Thing parts = GenClosest.ClosestThingReachable(t.Position, t.Map, ThingRequest.ForDef(ThingDefOf.ComponentIndustrial),
                PathEndMode.ClosestTouch, TraverseParms.For(pawn), 9999f,
                x => !x.IsForbidden(pawn) && x.stackCount >= 2 && pawn.CanReserve(x));
            if (parts == null) { JobFailReason.Is("needs 2 industrial components in one stack"); return null; }
            Job job = JobMaker.MakeJob(DefDatabase<JobDef>.GetNamed("RM_RepairRing"), t, parts);
            job.count = 2;
            return job;
        }
    }

    // Evaluate: ~1 game hour of work; reveals the true condition.
    public class RM_JobDriver_EvaluateRing : JobDriver
    {
        public const int WorkTicks = 2500; // INVENTED
        public override bool TryMakePreToilReservations(bool errorOnFailed) { return pawn.Reserve(job.targetA, job, 1, -1, null, errorOnFailed); }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedNullOrForbidden(TargetIndex.A);
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);
            Toil work = Toils_General.Wait(WorkTicks, TargetIndex.A);
            work.WithProgressBarToilDelay(TargetIndex.A);
            work.FailOnCannotTouch(TargetIndex.A, PathEndMode.Touch);
            work.activeSkill = () => SkillDefOf.Crafting;
            yield return work;
            yield return Toils_General.Do(delegate
            {
                RM_CompWarscarRing c = job.targetA.Thing.TryGetComp<RM_CompWarscarRing>();
                if (c == null) return;
                c.Evaluate();
                Designation d = pawn.Map.designationManager.DesignationOn(job.targetA.Thing, RM_RingDesignations.Evaluate);
                if (d != null) pawn.Map.designationManager.RemoveDesignation(d);
                Messages.Message("The ring is " + RM_CompWarscarRing.ConditionLabel(c.Condition) + ".", job.targetA.Thing, MessageTypeDefOf.NeutralEvent, false);
            });
        }
    }

    // Salvage: uninstall (working/failing) or strip (dead). All in RM_CompWarscarRing.DoSalvage.
    public class RM_JobDriver_SalvageRing : JobDriver
    {
        public const int WorkTicks = 3000; // INVENTED
        public override bool TryMakePreToilReservations(bool errorOnFailed) { return pawn.Reserve(job.targetA, job, 1, -1, null, errorOnFailed); }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedNullOrForbidden(TargetIndex.A);
            this.FailOn(() => !RM_WarscarSettings.ringSalvageEnabled);
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);
            Toil work = Toils_General.Wait(WorkTicks, TargetIndex.A);
            work.WithProgressBarToilDelay(TargetIndex.A);
            work.FailOnCannotTouch(TargetIndex.A, PathEndMode.Touch);
            work.activeSkill = () => SkillDefOf.Crafting;
            yield return work;
            yield return Toils_General.Do(delegate
            {
                Thing ring = job.targetA.Thing;
                RM_CompWarscarRing c = ring.TryGetComp<RM_CompWarscarRing>();
                if (c != null) c.DoSalvage(pawn);
            });
        }
    }

    // Repair: carry 2 industrial components to the ring, work, ring becomes Working.
    public class RM_JobDriver_RepairRing : JobDriver
    {
        public const int WorkTicks = 4000; // INVENTED
        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(job.targetA, job, 1, -1, null, errorOnFailed) && pawn.Reserve(job.targetB, job, 1, -1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedNullOrForbidden(TargetIndex.A);
            this.FailOn(() => !RM_WarscarSettings.ringSalvageEnabled);
            yield return Toils_Goto.GotoThing(TargetIndex.B, PathEndMode.ClosestTouch).FailOnDespawnedNullOrForbidden(TargetIndex.B);
            yield return Toils_Haul.StartCarryThing(TargetIndex.B, false, true, true);
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);
            Toil work = Toils_General.Wait(WorkTicks, TargetIndex.A);
            work.WithProgressBarToilDelay(TargetIndex.A);
            work.FailOnCannotTouch(TargetIndex.A, PathEndMode.Touch);
            work.activeSkill = () => SkillDefOf.Crafting;
            yield return work;
            yield return Toils_General.Do(delegate
            {
                RM_CompWarscarRing c = job.targetA.Thing.TryGetComp<RM_CompWarscarRing>();
                if (c == null) return;
                pawn.carryTracker.DestroyCarriedThing();
                c.SetCondition(RingCondition.Working, true);
                Designation d = pawn.Map.designationManager.DesignationOn(job.targetA.Thing, RM_RingDesignations.Repair);
                if (d != null) pawn.Map.designationManager.RemoveDesignation(d);
                Messages.Message("The ring is repaired and humming.", job.targetA.Thing, MessageTypeDefOf.PositiveEvent, false);
            });
        }
    }
}
