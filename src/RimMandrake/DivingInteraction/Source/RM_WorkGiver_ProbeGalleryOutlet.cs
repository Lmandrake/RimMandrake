using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.DivingInteraction
{
    // SCALD_RETURN_GALLERY_1 — any colonist hooks a gauge to an unprobed outlet port (600 ticks).
    public class RM_WorkGiver_ProbeGalleryOutlet : WorkGiver_Scanner
    {
        public override PathEndMode PathEndMode => PathEndMode.Touch;

        public override bool ShouldSkip(Pawn pawn, bool forced = false)
        {
            return !RM_DivingSettings.masterEnabled || !RM_DivingSettings.scaldReturnGalleryEnabled;
        }

        public override IEnumerable<Thing> PotentialWorkThingsGlobal(Pawn pawn)
        {
            ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail("RM_GalleryOutlet");
            return def == null ? new List<Thing>() : pawn.Map.listerThings.ThingsOfDef(def);
        }

        public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            RM_CompGalleryOutlet c = t.TryGetComp<RM_CompGalleryOutlet>();
            return c != null && !c.probed && !t.IsForbidden(pawn) && pawn.CanReserve(t, 1, -1, null, forced);
        }

        public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            return JobMaker.MakeJob(DefDatabase<JobDef>.GetNamed("RM_ProbeGalleryOutlet"), t);
        }
    }

    public class RM_JobDriver_ProbeGalleryOutlet : JobDriver
    {
        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(job.targetA, job, 1, -1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedNullOrForbidden(TargetIndex.A);
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);
            yield return Toils_General.Wait(600).WithProgressBarToilDelay(TargetIndex.A).FailOnDespawnedOrNull(TargetIndex.A);
            yield return Toils_General.Do(delegate
            {
                job.targetA.Thing?.TryGetComp<RM_CompGalleryOutlet>()?.Probe(pawn);
            });
        }
    }
}
