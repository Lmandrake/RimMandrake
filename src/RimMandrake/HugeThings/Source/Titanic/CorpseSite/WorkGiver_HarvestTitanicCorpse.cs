using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.TitanicCreatures
{
    /// <summary>
    /// Finds a Building_TitanicCorpseSite with yield left and assigns the
    /// harvest job to it - the "over days" half of card #4. Modeled on the
    /// WorkGiver_Scanner precedent already in this codebase
    /// (RimMandrake.Pits.WorkGiver_DigPitDeeper).
    /// </summary>
    public class WorkGiver_HarvestTitanicCorpse : WorkGiver_Scanner
    {
        public override ThingRequest PotentialWorkThingRequest =>
            ThingRequest.ForDef(RM_TitanicCreaturesDefOf.RM_TitanicCorpseSite);

        public override PathEndMode PathEndMode => PathEndMode.Touch;

        public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            if (!(t is Building_TitanicCorpseSite site) || !site.HasYield)
            {
                return false;
            }
            return pawn.CanReserve(t, 1, -1, null, forced);
        }

        public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            return JobMaker.MakeJob(RM_TitanicCreaturesDefOf.RM_HarvestTitanicCorpse, t);
        }
    }
}
