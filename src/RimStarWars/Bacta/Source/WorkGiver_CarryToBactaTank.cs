using Verse;

namespace RimMandrake.StarWars.Bacta
{
    /// <summary>
    /// Lets a hauler carry the designated pawn — downed, prisoner, or simply immobile — into the
    /// tank. All the logic is in vanilla's WorkGiver_CarryToBuilding; the only thing a subclass
    /// exists for is to narrow the scan to our building, which is what Biotech's
    /// WorkGiver_CarryToGrowthVat / _CarryToGeneExtractor do too.
    /// </summary>
    public class WorkGiver_CarryToBactaTank : RimWorld.WorkGiver_CarryToBuilding
    {
        public override ThingRequest PotentialWorkThingRequest =>
            ThingRequest.ForDef(BactaDefOf.RSW_BactaTank);
    }
}
