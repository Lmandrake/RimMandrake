using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.DivingInteraction
{
    // GREYSEA_FLOOR_WALKABLE_CHECK_1 (DI-6). The Grey Sea floor runs eight scatter steps (pillars, domes, chimneys,
    // statuary, four crystals), the dressing step (basin, jacket ring, Elder) and the wreck field, and the only
    // connectivity test on that floor (GenStep_SeaFloorTerrain.EnsureWalkable) reads TERRAIN alone. So a ring of
    // pillars can wall the Elder or a wreck off from where the ship lands.
    //
    // This is the last pass: flood from the landing zone (the map centre), and for every target (each Elder, each
    // grey-floor wreck) whose surrounding ring is not reached, find the cheapest path in which the only blockers
    // crossed are our own destroyable scatter pieces, and remove exactly those pieces. A target that cannot be reached
    // even so (impassable terrain, an unremovable blocker) is logged, not forced. Toggle: greyFloorWalkCheckEnabled.
    // Only the Grey Sea floor is touched. Every piece below is removable by name; nothing else is ever destroyed.
    public class GenStep_GreySeaWalkCheck : GenStep
    {
        public override int SeedPart => 5140951;

        private static readonly string[] RemovableDefs =
        {
            "RM_SaltPillar", "RM_SaltDome", "RM_SaltChimney", "RM_BrineJacket",
            "RM_GreatSaltCrystal_White", "RM_GreatSaltCrystal_Pink", "RM_GreatSaltCrystal_Amber", "RM_GreatSaltCrystal_Violet",
        };

        private static readonly string[] TargetDefs = { "RM_BrineElder", "RM_GreyFloorWreckHull", "RM_GreyFloorWreckSpine" };

        private const int Hard = -1;

        public override void Generate(Map map, GenStepParams parms)
        {
            if (!RM_DivingSettings.greyFloorWalkCheckEnabled || !RM_SeaFloorIdentity.IsFloorOf(map, "RM_GreySea"))
            {
                return;
            }
            HashSet<ThingDef> removable = new HashSet<ThingDef>();
            foreach (string n in RemovableDefs)
            {
                ThingDef d = DefDatabase<ThingDef>.GetNamedSilentFail(n);
                if (d != null)
                {
                    removable.Add(d);
                }
            }
            List<Thing> targets = new List<Thing>();
            foreach (string n in TargetDefs)
            {
                ThingDef d = DefDatabase<ThingDef>.GetNamedSilentFail(n);
                if (d != null)
                {
                    targets.AddRange(map.listerThings.ThingsOfDef(d));
                }
            }
            if (targets.Count == 0)
            {
                return;
            }

            IntVec3 start = FindStart(map, removable);
            if (!start.IsValid)
            {
                return;
            }
            bool[] reached = Flood(map, removable, start);
            int removedTotal = 0;
            foreach (Thing target in targets)
            {
                List<IntVec3> ring = Ring(map, target, removable);
                if (ring.Count == 0 || AnyReached(map, ring, reached))
                {
                    continue;
                }
                List<IntVec3> path = CheapestPath(map, removable, reached, ring);
                if (path == null)
                {
                    Log.Warning("[GreySeaWalkCheck] " + target.def.defName + " at " + target.Position
                        + " cannot be reached from the landing zone even with scatter pieces removed.");
                    continue;
                }
                foreach (IntVec3 c in path)
                {
                    foreach (Thing t in c.GetThingList(map).ToArray())
                    {
                        if (removable.Contains(t.def) && t.def.destroyable && !t.Destroyed)
                        {
                            t.Destroy();
                            removedTotal++;
                        }
                    }
                }
                reached = Flood(map, removable, start);
            }
            if (removedTotal > 0)
            {
                Log.Message("[GreySeaWalkCheck] removed " + removedTotal + " scatter piece(s) that walled the Elder or a wreck off from the landing zone.");
            }
        }

        // Hard = never crossable; 0 = open; 1 = blocked only by our own destroyable scatter pieces.
        private static int Cost(Map map, IntVec3 c, HashSet<ThingDef> removable)
        {
            if (!c.InBounds(map) || c.GetTerrain(map).passability == Traversability.Impassable)
            {
                return Hard;
            }
            int cost = 0;
            foreach (Thing t in c.GetThingList(map))
            {
                if (t.def.passability != Traversability.Impassable)
                {
                    continue;
                }
                if (!removable.Contains(t.def) || !t.def.destroyable)
                {
                    return Hard;
                }
                cost = 1;
            }
            return cost;
        }

        private static IntVec3 FindStart(Map map, HashSet<ThingDef> removable)
        {
            for (int r = 0; r < map.Size.x; r++)
            {
                foreach (IntVec3 c in GenRadial.RadialCellsAround(map.Center, r, true))
                {
                    if (c.InBounds(map) && Cost(map, c, removable) == 0)
                    {
                        return c;
                    }
                }
            }
            return IntVec3.Invalid;
        }

        private static bool[] Flood(Map map, HashSet<ThingDef> removable, IntVec3 start)
        {
            CellIndices idx = map.cellIndices;
            bool[] seen = new bool[idx.NumGridCells];
            Queue<IntVec3> q = new Queue<IntVec3>();
            seen[idx.CellToIndex(start)] = true;
            q.Enqueue(start);
            while (q.Count > 0)
            {
                IntVec3 c = q.Dequeue();
                for (int d = 0; d < 4; d++)
                {
                    IntVec3 n = c + GenAdj.CardinalDirections[d];
                    if (n.InBounds(map) && !seen[idx.CellToIndex(n)] && Cost(map, n, removable) == 0)
                    {
                        seen[idx.CellToIndex(n)] = true;
                        q.Enqueue(n);
                    }
                }
            }
            return seen;
        }

        // The cells just outside the target's footprint that something could stand on.
        private static List<IntVec3> Ring(Map map, Thing target, HashSet<ThingDef> removable)
        {
            List<IntVec3> ring = new List<IntVec3>();
            CellRect foot = target.OccupiedRect();
            foreach (IntVec3 c in foot.ExpandedBy(1).Cells)
            {
                if (!foot.Contains(c) && Cost(map, c, removable) != Hard)
                {
                    ring.Add(c);
                }
            }
            return ring;
        }

        private static bool AnyReached(Map map, List<IntVec3> ring, bool[] reached)
        {
            foreach (IntVec3 c in ring)
            {
                if (reached[map.cellIndices.CellToIndex(c)])
                {
                    return true;
                }
            }
            return false;
        }

        // 0-1 search outward from the reached region; entering a cell costs Cost(). Returns the cells of the cheapest
        // path to any ring cell (excluding the reached ones), or null when none exists.
        private static List<IntVec3> CheapestPath(Map map, HashSet<ThingDef> removable, bool[] reached, List<IntVec3> ring)
        {
            CellIndices idx = map.cellIndices;
            int n = idx.NumGridCells;
            int[] dist = new int[n];
            int[] parent = new int[n];
            for (int i = 0; i < n; i++)
            {
                dist[i] = int.MaxValue;
                parent[i] = -1;
            }
            LinkedList<int> dq = new LinkedList<int>();
            for (int i = 0; i < n; i++)
            {
                if (reached[i])
                {
                    dist[i] = 0;
                    dq.AddLast(i);
                }
            }
            HashSet<int> goal = new HashSet<int>();
            foreach (IntVec3 c in ring)
            {
                goal.Add(idx.CellToIndex(c));
            }
            while (dq.Count > 0)
            {
                int ci = dq.First.Value;
                dq.RemoveFirst();
                if (goal.Contains(ci))
                {
                    List<IntVec3> path = new List<IntVec3>();
                    for (int p = ci; p >= 0 && !reached[p]; p = parent[p])
                    {
                        path.Add(idx.IndexToCell(p));
                    }
                    return path;
                }
                IntVec3 c = idx.IndexToCell(ci);
                for (int d = 0; d < 4; d++)
                {
                    IntVec3 nb = c + GenAdj.CardinalDirections[d];
                    if (!nb.InBounds(map))
                    {
                        continue;
                    }
                    int cost = Cost(map, nb, removable);
                    int ni = idx.CellToIndex(nb);
                    if (cost == Hard || dist[ni] <= dist[ci] + cost)
                    {
                        continue;
                    }
                    dist[ni] = dist[ci] + cost;
                    parent[ni] = ci;
                    if (cost == 0)
                    {
                        dq.AddFirst(ni);
                    }
                    else
                    {
                        dq.AddLast(ni);
                    }
                }
            }
            return null;
        }
    }
}
