using RimWorld;
using Verse;

namespace RimMandrake.Pyrelands
{
    /// <summary>
    /// The roster is rolled by commonality, and small herds of the bestiary grazers can fill the whole budget: one fresh
    /// map in three had no fire-hawk or no ashwallow, so the player never met the cast the biome is about. After
    /// GenStep_Animals (order 1200) this tops the map up to a pair of hawks and eight ashwallows. The furnace-beast
    /// stays on its ruled commonality, so it stays a find. Last it checks the mix itself (PyrelandsAnimalMix) and adds
    /// ashwallow groups while the big predators still equal or outnumber the small common grazers.
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
        // The mix check after the top-up: at most this many extra groups (each the kind's own largest wild group), so a map
        // that rolled a freak number of predators still ends. A ceiling, not a target.
        private const int MaxBalanceGroups = 10;

        public override int SeedPart => 1993482203;

        public override void Generate(Map map, GenStepParams parms)
        {
            if (!PyrelandsMechanicsGate.On) return;
            TopUp(map, "RM_FireHawk", MinHawks);
            TopUp(map, "RM_Ashwallow", MinAshwallows);
            BalanceGrazers(map);
        }

        /// <summary>The top-up leaves about 4% of maps with grazers at or below the big predators (one Anooba pack and no
        /// Ullai or Iriaz herd). Count by the one rule and add an ashwallow group, the way the top-up spawns, until the
        /// grazers lead. Silent when the map already passes.</summary>
        private static void BalanceGrazers(Map map)
        {
            PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamedSilentFail("RM_Ashwallow");
            if (kind == null) return;
            int groupSize = System.Math.Max(1, kind.wildGroupSize.max);
            int grazers = 0;
            int bigPredators = 0;
            for (int g = 0; g < MaxBalanceGroups; g++)
            {
                PyrelandsAnimalMix.Census(map, out grazers, out bigPredators);
                if (grazers > bigPredators) return;
                if (SpawnGroup(map, kind, groupSize) == 0) break;
            }
            PyrelandsAnimalMix.Census(map, out grazers, out bigPredators);
            if (grazers <= bigPredators)
            {
                Log.Warning("[Pyrelands] fire-cast step could not make the small grazers (" + grazers + ") outnumber the big predators (" + bigPredators + ") on this map.");
            }
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
            SpawnGroup(map, kind, wanted - have);
        }

        /// <summary>One wild group of count, spread within ColonySpread of a random open home cell. Returns how many it
        /// spawned (0 when the map has no open, edge-reachable cell).</summary>
        private static int SpawnGroup(Map map, PawnKindDef kind, int count)
        {
            if (!CellFinderLoose.TryGetRandomCellWith(c => Fits(c, map, kind), map, 1000, out IntVec3 home)) return 0;
            for (int i = 0; i < count; i++)
            {
                if (!CellFinder.TryFindRandomCellNear(home, map, ColonySpread, c => Fits(c, map, kind), out IntVec3 cell)) cell = home;
                Pawn pawn = PawnGenerator.GeneratePawn(new PawnGenerationRequest(kind, null, PawnGenerationContext.NonPlayer, map.Tile));
                GenSpawn.Spawn(pawn, cell, map);
            }
            return count;
        }

        private static bool Fits(IntVec3 c, Map map, PawnKindDef kind)
        {
            return c.Standable(map) && !c.Roofed(map) && !c.Fogged(map) && map.reachability.CanReachMapEdge(c, TraverseParms.For(TraverseMode.PassDoors));
        }
    }

    /// <summary>The one rule behind "the small common grazers outnumber the big predators" (north-star bar
    /// pyre_animal_distribution_correct; ralph/QUESTIONS.md item 5, ruled 2026-11-07). Big predator: the race is a predator
    /// and its baseBodySize is at least 0.9. Small common grazer: a non-predator that eats plants (Eats(Plant), not
    /// ResolvedDietCategory, which would call the omnivore-flagged Gizka no grazer) with baseBodySize under 2. The suite
    /// checks the same bar by kind name (validation.py COMMON_GRAZERS / BIG_PREDATORS, comp animal_distribution_correct);
    /// read against the race defs on 2026-11-07 this rule yields exactly those five grazers and seven predators, and the
    /// fire-hawk (0.65), fire-wasp (0.79) and furnace-beast (6.0) count as neither. Change a threshold here and in that
    /// pair of lists together.</summary>
    public static class PyrelandsAnimalMix
    {
        public const float BigPredatorMinBodySize = 0.9f;
        public const float SmallGrazerMaxBodySize = 2f;

        public static bool IsBigPredator(PawnKindDef kind)
        {
            RaceProperties race = kind?.race?.race;
            return race != null && race.Animal && race.predator && race.baseBodySize >= BigPredatorMinBodySize;
        }

        public static bool IsSmallCommonGrazer(PawnKindDef kind)
        {
            RaceProperties race = kind?.race?.race;
            return race != null && race.Animal && !race.predator && race.Eats(FoodTypeFlags.Plant) && race.baseBodySize < SmallGrazerMaxBodySize;
        }

        /// <summary>Wild (factionless), living, spawned animals on the map, counted by the two rules above.</summary>
        public static void Census(Map map, out int grazers, out int bigPredators)
        {
            grazers = 0;
            bigPredators = 0;
            foreach (Pawn p in map.mapPawns.AllPawnsSpawned)
            {
                if (p.Faction != null || p.Dead || !p.RaceProps.Animal) continue;
                if (IsBigPredator(p.kindDef)) bigPredators++;
                else if (IsSmallCommonGrazer(p.kindDef)) grazers++;
            }
        }
    }
}
