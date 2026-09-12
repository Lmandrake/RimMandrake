using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.StarWars.Armoury;
using Verse;

namespace CrystalFormations;

internal class GenStep_ScatterLightsaberCrystals : GenStep_ScatterGroup
{
    private List<IntVec3> caveCells = new List<IntVec3>();

    private List<IntVec3> rockCells = new List<IntVec3>();

    private List<IntVec3> possibleSpawnCells = new List<IntVec3>();

    public override void Generate(Map map, GenStepParams parms)
    {
        // MOD_OPTIONS_RETROFIT_1: whole-step gate, taken before the two
        // full-map sweeps below so an off setting costs nothing at all.
        // Worldgen — a map that already exists is never revisited.
        if (!RSW_ArmourySettings.crystalFormationsEnabled)
        {
            return;
        }
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
        int spawnCount = GenMath.RoundRandom((float)caveCellCount / 1000f * RSW_ArmourySettings.crystalAbundance);
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
