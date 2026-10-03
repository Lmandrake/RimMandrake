using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.Stillsand
{
    // ════════════════════════════════════════════════════════════════════
    // STILLSAND_SAND_SIEVE_CHORE_1 — the sand sieve as a pawn chore. No building:
    // a pawn who CARRIES an RM_SandSieve (in inventory) sifts glass sand lying in
    // the home area into fine sand, with small chances of grit finds.
    //   RM_WorkGiver_SiftGlassSand  offers the chore ONLY to a sieve carrier.
    //   RM_WorkGiver_TakeSieve      sends a sieve-less pawn to pick one up (vanilla
    //                               TakeInventory job), but only while there is
    //                               glass sand worth sifting, so the chore never
    //                               needs an order and never offers itself without a sieve.
    //   RM_JobDriver_SiftGlassSand  walk, work with a progress bar, yield.
    // Settings live on RM_GlassChainSettings ("Stillsand: glass and lenses").
    // ════════════════════════════════════════════════════════════════════
    public static class RM_SandSieveUtil
    {
        public const int BatchSize = 10;          // glass sand consumed per sift
        public const float FineFraction = 0.25f;  // fine sand per glass sand at yield x1

        public static ThingDef Sieve { get { return DefDatabase<ThingDef>.GetNamedSilentFail("RM_SandSieve"); } }
        public static ThingDef GlassSand { get { return DefDatabase<ThingDef>.GetNamedSilentFail("RM_GlassSand"); } }
        public static ThingDef FineSand { get { return DefDatabase<ThingDef>.GetNamedSilentFail("RM_FineSand"); } }

        public static bool CarriesSieve(Pawn p)
        {
            ThingDef d = Sieve;
            return d != null && p?.inventory?.innerContainer != null && p.inventory.innerContainer.Contains(d);
        }

        public static bool SiftableHere(Pawn pawn, Thing t)
        {
            if (!RM_GlassChainSettings.sieveEnabled || t == null || !t.Spawned || t.def != GlassSand) return false;
            if (t.stackCount < BatchSize) return false;
            if (t.IsForbidden(pawn)) return false;
            // "in the home area": the player scopes the chore with the home area.
            if (!t.Map.areaManager.Home[t.Position]) return false;
            return pawn.CanReserveAndReach(t, PathEndMode.ClosestTouch, pawn.NormalMaxDanger());
        }

        public static int FineYield()
        {
            return Mathf.Max(1, Mathf.RoundToInt(BatchSize * FineFraction * RM_GlassChainSettings.sieveYieldMultiplier));
        }
    }

    public class RM_WorkGiver_SiftGlassSand : WorkGiver_Scanner
    {
        public override PathEndMode PathEndMode { get { return PathEndMode.ClosestTouch; } }

        public override IEnumerable<Thing> PotentialWorkThingsGlobal(Pawn pawn)
        {
            ThingDef d = RM_SandSieveUtil.GlassSand;
            return d == null ? null : pawn.Map.listerThings.ThingsOfDef(d);
        }

        public override bool ShouldSkip(Pawn pawn, bool forced = false)
        {
            return !RM_GlassChainSettings.sieveEnabled || !RM_SandSieveUtil.CarriesSieve(pawn);
        }

        public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            return RM_SandSieveUtil.CarriesSieve(pawn) && RM_SandSieveUtil.SiftableHere(pawn, t);
        }

        public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            return JobMaker.MakeJob(DefDatabase<JobDef>.GetNamed("RM_SiftGlassSand"), t);
        }
    }

    public class RM_WorkGiver_TakeSieve : WorkGiver_Scanner
    {
        public override PathEndMode PathEndMode { get { return PathEndMode.ClosestTouch; } }

        public override IEnumerable<Thing> PotentialWorkThingsGlobal(Pawn pawn)
        {
            ThingDef d = RM_SandSieveUtil.Sieve;
            return d == null ? null : pawn.Map.listerThings.ThingsOfDef(d);
        }

        public override bool ShouldSkip(Pawn pawn, bool forced = false)
        {
            if (!RM_GlassChainSettings.sieveEnabled || RM_SandSieveUtil.CarriesSieve(pawn)) return true;
            ThingDef g = RM_SandSieveUtil.GlassSand;
            if (g == null) return true;
            // Only worth fetching while some glass sand is waiting in the home area.
            foreach (Thing s in pawn.Map.listerThings.ThingsOfDef(g))
            {
                if (s.stackCount >= RM_SandSieveUtil.BatchSize && pawn.Map.areaManager.Home[s.Position] && !s.IsForbidden(pawn))
                    return false;
            }
            return true;
        }

        public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            return t.Spawned && !t.IsForbidden(pawn) && !RM_SandSieveUtil.CarriesSieve(pawn)
                && pawn.CanReserveAndReach(t, PathEndMode.ClosestTouch, pawn.NormalMaxDanger());
        }

        public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            Job job = JobMaker.MakeJob(JobDefOf.TakeInventory, t);
            job.count = 1;
            return job;
        }
    }

    public class RM_JobDriver_SiftGlassSand : JobDriver
    {
        private const int SiftTicks = 300;

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(job.targetA, job, 1, -1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedNullOrForbidden(TargetIndex.A);
            this.FailOn(() => !RM_GlassChainSettings.sieveEnabled || !RM_SandSieveUtil.CarriesSieve(pawn));
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.ClosestTouch);
            yield return Toils_General.Wait(SiftTicks).WithProgressBarToilDelay(TargetIndex.A)
                .FailOnDespawnedNullOrForbidden(TargetIndex.A);
            Toil sift = ToilMaker.MakeToil("RM_SiftGlassSand");
            sift.initAction = delegate
            {
                Thing stack = job.targetA.Thing;
                if (stack == null || !stack.Spawned || stack.stackCount < RM_SandSieveUtil.BatchSize) return;
                Map map = stack.Map;
                IntVec3 at = stack.Position;
                stack.SplitOff(RM_SandSieveUtil.BatchSize).Destroy();
                Place(RM_SandSieveUtil.FineSand, RM_SandSieveUtil.FineYield(), at, map);
                RollGrit(at, map);
                pawn.skills?.Learn(SkillDefOf.Crafting, 4f);
            };
            sift.defaultCompleteMode = ToilCompleteMode.Instant;
            yield return sift;
        }

        private static void RollGrit(IntVec3 at, Map map)
        {
            if (Rand.Chance(0.25f)) Place(DefDatabase<ThingDef>.GetNamedSilentFail("RM_BiosilicaGrit"), Rand.RangeInclusive(1, 3), at, map);
            if (Rand.Chance(0.06f)) Place(DefDatabase<ThingDef>.GetNamedSilentFail("RM_Biosilica"), 1, at, map);
            if (Rand.Chance(0.01f)) Place(DefDatabase<ThingDef>.GetNamedSilentFail("RM_GlassPearl"), 1, at, map);
        }

        private static void Place(ThingDef def, int count, IntVec3 at, Map map)
        {
            if (def == null || count <= 0) return;
            Thing t = ThingMaker.MakeThing(def);
            t.stackCount = count;
            GenPlace.TryPlaceThing(t, at, map, ThingPlaceMode.Near);
        }
    }
}
