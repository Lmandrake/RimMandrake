using RimWorld;
using Verse;

namespace RimMandrake.Pyrelands
{
    /// <summary>
    /// The roster is rolled by commonality, and small herds of the bestiary grazers can fill the whole budget: one fresh
    /// map in three had no fire-hawk or no ashwallow, so the player never met the cast the biome is about. After
    /// GenStep_Animals (order 1200) this tops the map up to a pair of hawks and one ashwallow colony. The furnace-beast
    /// stays on its ruled commonality, so it stays a find.
    /// </summary>
    public class GenStep_PyrelandsFireCast : GenStep
    {
        private const int MinHawks = 2;
        private const int MinAshwallows = 4;
        private const int ColonySpread = 6;

        public override int SeedPart => 1993482203;

        public override void Generate(Map map, GenStepParams parms)
        {
            if (!PyrelandsMechanicsGate.On) return;
            TopUp(map, "RM_FireHawk", MinHawks);
            TopUp(map, "RM_Ashwallow", MinAshwallows);
        }

        private static void TopUp(Map map, string kindName, int wanted)
        {
            PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamedSilentFail(kindName);
            if (kind == null) return;
            int have = 0;
            foreach (Pawn p in map.mapPawns.AllPawnsSpawned)
            {
                if (p.kindDef == kind) have++;
            }
            if (have >= wanted) return;
            if (!CellFinderLoose.TryGetRandomCellWith(c => Fits(c, map, kind), map, 1000, out IntVec3 home)) return;
            for (int i = have; i < wanted; i++)
            {
                if (!CellFinder.TryFindRandomCellNear(home, map, ColonySpread, c => Fits(c, map, kind), out IntVec3 cell)) cell = home;
                Pawn pawn = PawnGenerator.GeneratePawn(new PawnGenerationRequest(kind, null, PawnGenerationContext.NonPlayer, map.Tile));
                GenSpawn.Spawn(pawn, cell, map);
            }
        }

        private static bool Fits(IntVec3 c, Map map, PawnKindDef kind)
        {
            return c.Standable(map) && !c.Roofed(map) && !c.Fogged(map) && map.reachability.CanReachMapEdge(c, TraverseParms.For(TraverseMode.PassDoors));
        }
    }
}
