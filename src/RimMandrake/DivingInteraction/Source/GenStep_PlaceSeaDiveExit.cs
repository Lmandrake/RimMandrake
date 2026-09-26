using System.Linq;
using Verse;

namespace RimMandrake.DivingInteraction
{
    // SEA_DIVE_MAPS_BUILD_1. Mirrors vanilla's own GenStep_PlaceCaveExit
    // (RimWorld/GenStep_PlaceCaveExit.cs, read this session), which
    // hardcodes ThingDefOf.CaveExit rather than reading the portal's own
    // MapPortalProperties.exitDef — there is no generic "read exitDef off
    // the entrance" path in the engine. This sea-specific twin spawns
    // RM_SeaDiveExit instead; PocketMapExit.SpawnSetup links the new
    // building back to whichever RM_SeaDiveHatch generated the map
    // automatically (PocketMapUtility.currentlyGeneratingPortal) — nothing
    // else here needs to be sea-specific.
    public class GenStep_PlaceSeaDiveExit : GenStep
    {
        public const float ClearRadius = 4.5f;

        public override int SeedPart => 8362343;

        public override void Generate(Map map, GenStepParams parms)
        {
            if (!CellFinder.TryFindRandomCell(map, c => c.Standable(map) && c.DistanceToEdge(map) > 5.5f, out IntVec3 result))
            {
                CellFinder.TryFindRandomCell(map, c => c.Standable(map), out result);
            }

            foreach (IntVec3 cell in GenRadial.RadialCellsAround(result, ClearRadius, useCenter: true))
            {
                foreach (Thing thing in cell.GetThingList(map).Where(t => t.def.destroyable).ToList())
                {
                    thing.Destroy();
                }
            }

            ThingDef exitDef = DefDatabase<ThingDef>.GetNamed("RM_SeaDiveExit");
            GenSpawn.Spawn(ThingMaker.MakeThing(exitDef), result, map);
            MapGenerator.PlayerStartSpot = result;
        }
    }
}
