using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;
using Verse.AI;
using Verse.AI.Group;

namespace RimMandrake.Utinni.StructureInjectionsRUT
{
    // One patrol: who walks it, and the loop they walk. Waypoints are layout cells, (column,row), row 0 the
    // layout's first <li>.
    public class CathedralDescentPatrolGroup
    {
        public List<PawnKindDef> kinds = new List<PawnKindDef>();
        public List<IntVec2> waypoints = new List<IntVec2>();
    }

    // Runs right after KCSG has placed RUT_CathedralDescent_Halls (RUT_CathedralDescent_GenStepFinish, order 401).
    // Every field is written by Source/CathedralDescent/gen_descent_layout.py; nothing here restates the layout.
    //   1. Find the terminus (exactly one) and from it the layout's rect, trying both row orders: KCSG's row order
    //      is not read from its source here, so the one that puts the arrival cells on open floor wins.
    //   2. Map bigger than the layout: carry the open cells and the line on the rect's border out to the map edge.
    //   3. Everything else outside the rect becomes the kit's rock. 4. Thick rock roof over the whole map.
    //   5. Mechanoid sentinels on slow patrol loops (LordJob_CathedralDescentPatrol); no assault, no raid.
    public class GenStep_CathedralDescent : GenStep
    {
        public int layoutSize = 250;
        public ThingDef terminusDef;
        public IntVec2 terminusCell;
        public int arrivalRow;
        public IntVec2 arrivalCols;
        public string rockDef;
        public List<string> openTerrains = new List<string>();
        public List<ThingDef> lineDefs = new List<ThingDef>();
        public DutyDef dutyDef;
        public List<CathedralDescentPatrolGroup> patrols = new List<CathedralDescentPatrolGroup>();

        private int originX, originZ;
        private bool rowZeroSouth;

        public override int SeedPart => 611250147;

        public override void Generate(Map map, GenStepParams parms)
        {
            if (terminusDef == null)
            {
                Log.Error("[DESCENT] GenStep has no terminusDef");
                return;
            }
            List<Thing> found = map.listerThings.ThingsOfDef(terminusDef);
            if (found.Count != 1)
            {
                Log.Error("[DESCENT] expected exactly one " + terminusDef.defName + " on the map, found " + found.Count);
                if (found.Count == 0)
                {
                    return;
                }
            }
            HashSet<TerrainDef> open = new HashSet<TerrainDef>();
            foreach (string name in openTerrains)
            {
                TerrainDef t = DefDatabase<TerrainDef>.GetNamedSilentFail(name);
                if (t == null)
                {
                    Log.Warning("[DESCENT] open terrain " + name + " is not loaded");
                }
                else
                {
                    open.Add(t);
                }
            }
            if (!ChooseOrientation(map, found[0].Position, open))
            {
                Log.Error("[DESCENT] neither row order puts the arrival cells on open floor; using row 0 = north");
            }
            CellRect rect = new CellRect(originX, originZ, layoutSize, layoutSize);
            HashSet<ThingDef> line = new HashSet<ThingDef>(lineDefs.Where(d => d != null));
            ExtendToEdges(map, rect, open, line);
            FillRock(map, rect, open);
            foreach (IntVec3 c in map.AllCells)
            {
                map.roofGrid.SetRoof(c, RoofDefOf.RoofRockThick);
            }
            SpawnPatrols(map);
        }

        // Layout (column,row) to a map cell under the chosen row order.
        public IntVec3 ToMap(int col, int row)
        {
            return new IntVec3(originX + col, 0, rowZeroSouth ? originZ + row : originZ + (layoutSize - 1 - row));
        }

        private bool ChooseOrientation(Map map, IntVec3 terminus, HashSet<TerrainDef> open)
        {
            foreach (bool south in new[] { false, true })
            {
                rowZeroSouth = south;
                originX = terminus.x - terminusCell.x;
                originZ = south ? terminus.z - terminusCell.z : terminus.z - (layoutSize - 1 - terminusCell.z);
                bool all = true;
                for (int col = arrivalCols.x; col <= arrivalCols.z && all; col++)
                {
                    IntVec3 c = ToMap(col, arrivalRow);
                    all = c.InBounds(map) && open.Contains(c.GetTerrain(map)) && c.GetEdifice(map) == null;
                }
                if (all)
                {
                    return true;
                }
            }
            rowZeroSouth = false;
            originX = terminus.x - terminusCell.x;
            originZ = terminus.z - (layoutSize - 1 - terminusCell.z);
            return false;
        }

        private static void Clear(Map map, IntVec3 c)
        {
            foreach (Thing t in c.GetThingList(map).ToList())
            {
                if (t.def.destroyable && !(t is Pawn p && p.Faction == Faction.OfPlayer))
                {
                    t.Destroy();
                }
            }
        }

        private static void ExtendToEdges(Map map, CellRect rect, HashSet<TerrainDef> open, HashSet<ThingDef> line)
        {
            foreach (IntVec3 b in rect.EdgeCells)
            {
                if (!b.InBounds(map))
                {
                    continue;
                }
                Building ed = b.GetEdifice(map);
                TerrainDef terrain = b.GetTerrain(map);
                bool isLine = ed != null && line.Contains(ed.def);
                if (!isLine && !(ed == null && open.Contains(terrain)))
                {
                    continue;
                }
                foreach (IntVec3 dir in new[] { IntVec3.West, IntVec3.East, IntVec3.South, IntVec3.North })
                {
                    if (rect.Contains(b + dir))
                    {
                        continue;   // dir must point out of the rect from this border cell
                    }
                    for (IntVec3 c = b + dir; c.InBounds(map); c += dir)
                    {
                        Clear(map, c);
                        map.terrainGrid.SetTerrain(c, terrain);
                        if (isLine)
                        {
                            GenSpawn.Spawn(ThingMaker.MakeThing(ed.def), c, map);
                        }
                    }
                }
            }
        }

        private void FillRock(Map map, CellRect rect, HashSet<TerrainDef> open)
        {
            ThingDef rock = DefDatabase<ThingDef>.GetNamedSilentFail(rockDef ?? "");
            if (rock == null)
            {
                Log.Error("[DESCENT] rock " + rockDef + " is not loaded; the map outside the layout stays open");
                return;
            }
            foreach (IntVec3 c in map.AllCells)
            {
                if (rect.Contains(c) || c.GetEdifice(map) != null || open.Contains(c.GetTerrain(map)))
                {
                    continue;
                }
                Clear(map, c);
                GenSpawn.Spawn(ThingMaker.MakeThing(rock), c, map);
            }
        }

        private void SpawnPatrols(Map map)
        {
            Faction mechs = Faction.OfMechanoids;
            if (mechs == null || dutyDef == null)
            {
                Log.Warning("[DESCENT] no mechanoid faction or no patrol duty: the halls stay empty");
                return;
            }
            foreach (CathedralDescentPatrolGroup group in patrols)
            {
                List<IntVec3> loop = group.waypoints.Select(w => ToMap(w.x, w.z)).ToList();
                if (loop.Count == 0 || loop.Any(c => !c.InBounds(map) || !c.Standable(map)))
                {
                    Log.Error("[DESCENT] a patrol loop leaves the open floor; group skipped");
                    continue;
                }
                List<Pawn> pawns = new List<Pawn>();
                foreach (PawnKindDef kind in group.kinds.Where(k => k != null))
                {
                    if (!CellFinder.TryFindRandomCellNear(loop[0], map, 4, c => c.Standable(map) && c.GetFirstPawn(map) == null, out IntVec3 at))
                    {
                        at = loop[0];
                    }
                    Pawn pawn = PawnGenerator.GeneratePawn(kind, mechs);
                    GenSpawn.Spawn(pawn, at, map);
                    pawns.Add(pawn);
                }
                if (pawns.Count > 0)
                {
                    LordMaker.MakeNewLord(mechs, new LordJob_CathedralDescentPatrol(loop, dutyDef), map, pawns);
                }
            }
        }
    }
}
