using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.Utinni.Antiquities
{
    public class WorkGiver_ExamineAntiquity : WorkGiver_Scanner
    {
        // Every RUT_Antiquity_* item family, by defName -- RUT_Antiquity_Testament
        // is slice 6's item and does not exist in slice 1's defs, but the check
        // is future-proofed against it rather than hardcoded to today's three.
        private static readonly HashSet<string> AntiquityDefNames = new HashSet<string>
        {
            "RUT_Antiquity_Urn",
            "RUT_Antiquity_Stele",
            "RUT_Antiquity_Gravegood",
            "RUT_Antiquity_Testament",
        };

        public override ThingRequest PotentialWorkThingRequest => ThingRequest.ForGroup(ThingRequestGroup.HaulableEver);

        public override PathEndMode PathEndMode => PathEndMode.ClosestTouch;

        public override bool ShouldSkip(Pawn pawn, bool forced = false)
        {
            // Nothing left to advance once VOICE is finished -- stop offering
            // the job rather than let pawns carry urns to a station for free.
            return AntiquityUtility.CurrentStage() == null;
        }

        public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            if (!AntiquityDefNames.Contains(t.def.defName))
            {
                return null;
            }
            CompAntiquity comp = t.TryGetComp<CompAntiquity>();
            if (comp == null || comp.catalogued)
            {
                return null;
            }
            if (t.IsForbidden(pawn) || !pawn.CanReserveAndReach(t, PathEndMode.ClosestTouch, Danger.None))
            {
                return null;
            }
            if (AntiquityUtility.CurrentStage() == null)
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
