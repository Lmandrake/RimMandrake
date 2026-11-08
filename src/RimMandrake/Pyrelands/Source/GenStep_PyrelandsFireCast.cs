using RimWorld;
using Verse;

namespace RimMandrake.Pyrelands
{
    /// <summary>
    /// The roster is rolled by commonality, and small herds of the bestiary grazers can fill the whole budget: one fresh
    /// map in three had no fire-hawk or no ashwallow, so the player never met the cast the biome is about. After
    /// GenStep_Animals (order 1200) this tops the map up to a pair of hawks and eight ashwallows. The furnace-beast
    /// stays on its ruled commonality, so it stays a find.
    /// </summary>
    public class GenStep_PyrelandsFireCast : GenStep
    {
        private const int MinHawks = 2;
        // 8, not 4: pyre_animal_distribution_correct ("the small common grazers outnumber the big predators"). Vanilla spawns
        // only about 7 groups on a 250 map (pick weight = commonality / wildGroupSize.Average, groups until ecoSystemWeight
        // reaches area x density / 10000 = 13.1), so one Anooba pack (6~8) with no Ullai or Iriaz herd flips a map. Modelled
        // over 20,000 maps: 17% fail with no top-up, 10.4% at 4 ashwallows, 4.3% at 8, the owner's roster weights untouched.
        private const int MinAshwallows = 8;
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
