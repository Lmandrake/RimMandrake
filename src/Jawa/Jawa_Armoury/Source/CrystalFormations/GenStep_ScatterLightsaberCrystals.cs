using System;
using System.Collections.Generic;
using System.Linq;
using Verse;

namespace CrystalFormations;

internal class GenStep_ScatterLightsaberCrystals : GenStep_ScatterGroup
{
    private List<IntVec3> caveCells = new List<IntVec3>();

    private List<IntVec3> rockCells = new List<IntVec3>();

    private List<IntVec3> possibleSpawnCells = new List<IntVec3>();

    public override void Generate(Map map, GenStepParams parms)
    {
        MapGenFloatGrid caves = MapGenerator.Caves;
        MapGenFloatGrid elevation = MapGenerator.Elevation;
        float rockElevationThreshold = 0.7f;
        int caveCellCount = 0;
        rockCells.Clear();
        foreach (IntVec3 cell in map.AllCells)
        {
            if (elevation[cell] > rockElevationThreshold)
            {
                rockCells.Add(cell);
            }
            if (caves[cell] > 0f)
            {
                caveCellCount++;
            }
        }
        List<IntVec3> factionCells = map.AllCells.Where((IntVec3 c) => map.thingGrid.ThingsAt(c).Any((Thing thing) => thing.Faction != null)).ToList();
        GenMorphology.Dilate(factionCells, 50, map, null);
        HashSet<IntVec3> excluded = new HashSet<IntVec3>(factionCells);
        int spawnCount = GenMath.RoundRandom((float)caveCellCount / 1000f);
        GenMorphology.Erode(rockCells, 10, map, null);
        possibleSpawnCells.Clear();
        foreach (IntVec3 rockCell in rockCells)
        {
            if (caves[rockCell] > 0f && !excluded.Contains(rockCell))
            {
                possibleSpawnCells.Add(rockCell);
            }
        }
        for (int i = 0; i < spawnCount; i++)
        {
            if (possibleSpawnCells.Count == 0)
            {
                break;
            }
            IntVec3 spot = possibleSpawnCells.RandomElement();
            possibleSpawnCells.Remove(spot);
            ScatterAt(spot, map, parms, 1);
        }
    }
}
