using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.Utinni.Antiquities
{
    public class WorkGiver_ExamineAntiquity : WorkGiver_Scanner
    {
        public override ThingRequest PotentialWorkThingRequest => ThingRequest.ForGroup(ThingRequestGroup.HaulableEver);

        public override PathEndMode PathEndMode => PathEndMode.ClosestTouch;

        public override bool ShouldSkip(Pawn pawn, bool forced = false)
        {
            // Mod Settings master toggle -- off means the job is never offered.
            if (!AntiquitiesSettings.readingEnabled)
            {
                return true;
            }
            // Once VOICE is finished an urn has nothing left to teach; JobOnThing
            // refuses those per thing, so a piece with a catalogue listener (the
            // pilgrim's journal, WARSCAR_PILGRIM_JOURNAL_ANTIQUITY_1) can still be read.
            return false;
        }

        public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            // An antiquity is any thing carrying CompAntiquity -- the comp is the
            // family, so a new item (journal, testament) needs no list edit here.
            CompAntiquity comp = t.TryGetComp<CompAntiquity>();
            if (comp == null || comp.catalogued)
            {
                return null;
            }
            if (t.IsForbidden(pawn) || !pawn.CanReserveAndReach(t, PathEndMode.ClosestTouch, Danger.None))
            {
                return null;
            }
            if (AntiquityUtility.CurrentStage() == null && !AntiquityUtility.HasCatalogueListener(t))
            {
                return null;
            }

            Thing station = GenClosest.ClosestThingReachable(
                pawn.Position,
                pawn.Map,
                ThingRequest.ForDef(ThingDefOf_Antiquities.RUT_AntiquityReadingStation),
                PathEndMode.InteractionCell,
                TraverseParms.For(pawn),
                validator: s => !s.IsForbidden(pawn) && pawn.CanReserve(s));
            if (station == null)
            {
                return null;
            }

            Job job = JobMaker.MakeJob(JobDefOf_Antiquities.RUT_ExamineAntiquity, t, station);
            job.count = 1;
            return job;
        }
    }
}
