using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.Scarlands
{
    // ════════════════════════════════════════════════════════════════════
    // WARSCAR_SETTLING_WEATHER_1 spec 6, the insecticide half: war dust cures blight.
    // A grower carries one war dust to a blighted plant and dusts it; the Blight thing is destroyed and the
    // plant lives. Scans vanilla ThingDefOf.Blight (one Thing per blighted plant). Gated by
    // RM_WarscarSettings.warDustBlightCureEnabled. The pigment-filler half is pure XML
    // (RM_StretchDyeWithWarDust in RM_WarDustRecipes.xml).
    // ════════════════════════════════════════════════════════════════════
    [DefOf]
    public static class RM_WarDustDefOf
    {
        public static JobDef RM_DustBlight;
        static RM_WarDustDefOf() { DefOfHelper.EnsureInitializedInCtor(typeof(RM_WarDustDefOf)); }
    }

    public class WorkGiver_DustBlight : WorkGiver_Scanner
    {
        public override ThingRequest PotentialWorkThingRequest { get { return ThingRequest.ForDef(ThingDefOf.Blight); } }
        public override PathEndMode PathEndMode { get { return PathEndMode.Touch; } }

        public override bool ShouldSkip(Pawn pawn, bool forced = false)
        {
            return !RM_WarscarSettings.warDustBlightCureEnabled
                || pawn.Map.listerThings.ThingsOfDef(RM_SettlingDefOf.RM_WarDust).Count == 0;
        }

        public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false) { return JobOnThing(pawn, t, forced) != null; }

        public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            if (!RM_WarscarSettings.warDustBlightCureEnabled || !(t is Blight) || !t.Spawned) return null;
            if (t.IsForbidden(pawn) || !pawn.CanReserve(t, 1, -1, null, forced)) return null;
            Thing dust = GenClosest.ClosestThingReachable(pawn.Position, pawn.Map,
                ThingRequest.ForDef(RM_SettlingDefOf.RM_WarDust), PathEndMode.ClosestTouch,
                TraverseParms.For(pawn), 9999f,
                d => !d.IsForbidden(pawn) && pawn.CanReserve(d, 1, 1, null, forced));
            if (dust == null) return null;
            Job job = JobMaker.MakeJob(RM_WarDustDefOf.RM_DustBlight, t, dust);
            job.count = 1;
            return job;
        }
    }

    public class JobDriver_DustBlight : JobDriver
    {
        private const int DustTicks = 120;

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(job.GetTarget(TargetIndex.A), job, 1, -1, null, errorOnFailed)
                && pawn.Reserve(job.GetTarget(TargetIndex.B), job, 1, 1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDestroyedOrNull(TargetIndex.A);
            yield return Toils_Goto.GotoThing(TargetIndex.B, PathEndMode.ClosestTouch)
                .FailOnDespawnedNullOrForbidden(TargetIndex.B);
            yield return Toils_Haul.StartCarryThing(TargetIndex.B);
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);
            yield return Toils_General.Wait(DustTicks).FailOnDestroyedNullOrForbidden(TargetIndex.A)
                .WithProgressBarToilDelay(TargetIndex.A);
            Toil fin = new Toil();
            fin.initAction = delegate
            {
                Thing carried = pawn.carryTracker.CarriedThing;
                if (carried == null || carried.def != RM_SettlingDefOf.RM_WarDust) return;
                Blight blight = job.GetTarget(TargetIndex.A).Thing as Blight;
                if (blight == null || blight.Destroyed) return;
                if (carried.stackCount > 1) carried.SplitOff(1).Destroy();
                else carried.Destroy();
                blight.Destroy();
                HealthUtility.AdjustSeverity(pawn, HediffDefOf.ToxicBuildup, 0.01f);
            };
            fin.defaultCompleteMode = ToilCompleteMode.Instant;
            yield return fin;
        }
    }
}
