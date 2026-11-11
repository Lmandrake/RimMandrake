using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.HugeThings
{
    /// <summary>Cut an enclosed huge root from its actual trunk, retaining vanilla plant policy, reservation, work,
    /// yield, designation and destruction toils. Only the approach and work-contact target change.
    /// Engine contract: installed 1.6 JobDriver_PlantWork iterator uses A for plant work; B/C are unused.
    /// Bounded reflection-only IL is retained under whittle/ht-trunk-doors/evidence/raw/engine-cut-contract.*.</summary>
    public class WorkGiver_CutHugePlantFromTrunk : WorkGiver_PlantsCut
    {
        public static JobDef CutDef => DefDatabase<JobDef>.GetNamed("RM_CutHugePlantFromTrunk");
        public override PathEndMode PathEndMode => PathEndMode.Touch;
        public override ThingRequest PotentialWorkThingRequest => ThingRequest.ForDef(HugeThingsDefOf.RM_HugeTrunkBlocker);

        public override bool ShouldSkip(Pawn pawn, bool forced = false)
            => !Patch_PlantWork_TrunkContact.Ready || !RM_HugeThingsSettings.PlantTrunkActive || base.ShouldSkip(pawn, forced);

        public override IEnumerable<Thing> PotentialWorkThingsGlobal(Pawn pawn)
        {
            if (ShouldSkip(pawn)) yield break;
            var component = pawn.Map.GetComponent<MapComponent_HugeFootprints>();
            if (component == null) yield break;
            var seen = new HashSet<int>();
            foreach (Designation designation in pawn.Map.designationManager.SpawnedDesignationsOfDef(DesignationDefOf.CutPlant))
                if (designation.target.Thing is Plant plant)
                    foreach (Building_TrunkBlocker blocker in component.CutBlockers(plant))
                        if (seen.Add(blocker.thingIDNumber)) yield return blocker;
        }

        public override Job JobOnThing(Pawn pawn, Thing thing, bool forced = false)
        {
            if (ShouldSkip(pawn, forced) || !(thing is Building_TrunkBlocker blocker) || !blocker.Spawned || blocker.Map != pawn.Map || thing.IsForbidden(pawn)) return null;
            var component = pawn.Map.GetComponent<MapComponent_HugeFootprints>();
            if (component == null) return null;
            foreach (Plant plant in component.CutOwners(blocker))
            {
                if (!ValidContact(pawn, plant, blocker) || plant.IsForbidden(pawn) ||
                    pawn.Map.designationManager.DesignationOn(plant, DesignationDefOf.CutPlant) == null ||
                    pawn.CanReach(plant, PathEndMode.Touch, Danger.Deadly)) continue;
                // The registered vanilla giver supplies its own gates, including all other mods' patches.
                var vanilla = DefDatabase<WorkGiverDef>.GetNamed("PlantsCut").Worker as WorkGiver_PlantsCut;
                Job original = vanilla?.JobOnThing(pawn, plant, forced);
                if (original == null) continue;
                bool accepted = original.def == JobDefOf.CutPlantDesignated && original.targetA.Thing == plant &&
                    (original.targetQueueA == null || original.targetQueueA.Count == 0);
                if (!accepted) { JobMaker.ReturnToPool(original); continue; }
                // Keep the vanilla-created job, including playerForced and any policy metadata; no queued batch.
                original.def = CutDef;
                original.targetC = blocker;
                return original;
            }
            return null;
        }

        public override string PostProcessedGerund(Job job)
        {
            var vanilla = DefDatabase<WorkGiverDef>.GetNamed("PlantsCut").Worker as WorkGiver_PlantsCut;
            Job description = JobMaker.MakeJob(JobDefOf.CutPlantDesignated, job.targetA);
            try { return vanilla.PostProcessedGerund(description); }
            finally { JobMaker.ReturnToPool(description); }
        }

        public static bool ValidContact(Pawn pawn, Plant plant, Building_TrunkBlocker blocker)
        {
            if (!Patch_PlantWork_TrunkContact.Ready || !RM_HugeThingsSettings.PlantTrunkActive ||
                pawn == null || !pawn.Spawned || plant == null || !plant.Spawned || plant.Destroyed || !plant.def.destroyable ||
                blocker == null || !blocker.Spawned || blocker.Destroyed || plant.Map != pawn.Map || blocker.Map != pawn.Map)
                return false;
            return pawn.Map.GetComponent<MapComponent_HugeFootprints>()?.HasCutClaim(plant, blocker) == true;
        }
    }

    [HarmonyPatch]
    public static class Patch_PlantWork_TrunkContact
    {
        public static bool Ready { get; private set; }

        public static MethodBase TargetMethod()
            => AccessTools.EnumeratorMoveNext(AccessTools.Method(typeof(JobDriver_PlantWork), "MakeNewToils"));

        public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instructions, MethodBase __originalMethod)
        {
            var code = instructions.ToList();
            var driverFields = __originalMethod.DeclaringType.GetFields(BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic)
                .Where(f => f.FieldType == typeof(JobDriver_PlantWork)).ToArray();
            MethodInfo go = AccessTools.Method(typeof(Toils_Goto), "GotoThing", new[] { typeof(TargetIndex), typeof(PathEndMode), typeof(bool) });
            MethodInfo[] touchMethods = typeof(ToilFailConditions).GetMethods(BindingFlags.Static | BindingFlags.Public)
                .Where(m => m.Name == "FailOnCannotTouch" && m.IsGenericMethodDefinition && m.GetParameters().Length == 3).ToArray();
            MethodInfo touch = touchMethods.Length == 1 ? touchMethods[0].MakeGenericMethod(typeof(Toil)) : null;
            var result = PlantCutToilRewrite.Rewrite(code, driverFields.Length == 1 ? driverFields[0] : null, go, touch,
                AccessTools.Method(typeof(Patch_PlantWork_TrunkContact), nameof(GotoContact)),
                AccessTools.Method(typeof(Patch_PlantWork_TrunkContact), nameof(FailOnContact)),
                (int)TargetIndex.A, (int)PathEndMode.Touch, out bool accepted);
            Ready = accepted;
            if (!Ready)
                Log.ErrorOnce("[RimMandrake.HugeThings] plant-work IL contact contract changed; trunk cutting disabled; vanilla toils retained.", 0x48544355);
            return result;
        }

        private static bool TrunkJob(JobDriver_PlantWork driver)
            => driver is JobDriver_PlantCut_Designated && driver.job.def == WorkGiver_CutHugePlantFromTrunk.CutDef;

        private static bool Valid(JobDriver_PlantWork driver)
            => WorkGiver_CutHugePlantFromTrunk.ValidContact(driver.pawn, driver.job.targetA.Thing as Plant,
                driver.job.targetC.Thing as Building_TrunkBlocker);

        public static Toil GotoContact(TargetIndex target, PathEndMode mode, bool parent, JobDriver_PlantWork driver)
        {
            if (!TrunkJob(driver)) return Toils_Goto.GotoThing(target, mode, parent);
            // Even an invalid saved C keeps the same toil count/index; fail at runtime, never fall back to the root.
            Toil toil = Toils_Goto.GotoThing(TargetIndex.C, mode, parent);
            return toil.FailOn(() => !Valid(driver));
        }

        public static Toil FailOnContact(Toil toil, TargetIndex target, PathEndMode mode, JobDriver_PlantWork driver)
        {
            if (!TrunkJob(driver)) return toil.FailOnCannotTouch(target, mode);
            // Local to approach/work only: after PlantCollected removes blockers, vanilla completion still runs.
            toil.FailOn(() => !Valid(driver));
            return toil.FailOnCannotTouch(TargetIndex.C, mode);
        }
    }
}
