using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;
using Verse.Noise;

namespace RimMandrake.DivingInteraction
{
    // SEA_DIVE_MAPS_BUILD_1. The vanilla `Terrain` GenStepDef paints from
    // the biome's own terrainsByFertility, which for every terminal sea is
    // liquid (deep water is Impassable) — correct for the SURFACE tile,
    // wrong for a floor pocket map the diving crew walks. This GenStep
    // replaces it outright (vanilla Terrain is omitted from every
    // RM_SeaDiveGenerator_*).
    //
    // 1. Base floor: RM_SeaFloorBandsExtension.baseTerrain on the map's own
    //    generatorDef, else the pre-extension default — RM_ChillIceBedrock on
    //    the Chill seabed (CHILL_RIME_TERRACES_1, via
    //    RM_ChillFireGate.IsChillSeabedMap: both map.Biome and
    //    map.IsPocketMap are set in MapGenerator.GenerateMap before any
    //    GenStep runs), RM_SeaFloorGround everywhere else.
    // 2. Habitat bands (SEA_DIVE_FLOOR_TERRAIN_1, 2026-09-30): the
    //    extension's nested bands, painted from one Perlin field ranked by
    //    exact share, so each sea's floor carries the terrain TAGS its
    //    wildPlants' wildTerrainTags need (PlantUtility.CanEverPlantAt
    //    refuses a wild plant on a cell whose terrain lacks every tag). Then
    //    a walkability pass — see RM_SeaFloorBandsExtension.minConnectedShare.
    //    Gated by RM_DivingSettings.seaFloorBandsEnabled; off = step 1 only.
    //
    // Other per-sea floor dressing runs later in its own GenSteps
    // (GenStep_GreySeaFloorDressing 880, GenStep_ChillRimeTerraces 920).
    public class GenStep_SeaFloorTerrain : GenStep
    {
        public override int SeedPart => 8362341;

        public override void Generate(Map map, GenStepParams parms)
        {
            RM_SeaFloorBandsExtension ext = map.generatorDef?.GetModExtension<RM_SeaFloorBandsExtension>();

            TerrainDef floor = null;
            if (ext != null && !ext.baseTerrain.NullOrEmpty())
            {
                floor = DefDatabase<TerrainDef>.GetNamedSilentFail(ext.baseTerrain);
                if (floor == null)
                {
                    Log.Warning("[RM_DivingInteraction] sea floor base terrain '" + ext.baseTerrain + "' not loaded; using default floor.");
                }
            }
            if (floor == null)
            {
                floor = RM_ChillFireGate.IsChillSeabedMap(map)
                    ? DefDatabase<TerrainDef>.GetNamed("RM_ChillIceBedrock")
                    : DefDatabase<TerrainDef>.GetNamed("RM_SeaFloorGround");
            }
            foreach (IntVec3 cell in map.AllCells)
            {
                map.terrainGrid.SetTerrain(cell, floor);
            }

            if (ext != null && RM_DivingSettings.seaFloorBandsEnabled)
            {
                PaintBands(map, ext, floor);
            }
        }

        private static void PaintBands(Map map, RM_SeaFloorBandsExtension ext, TerrainDef floor)
        {
            // Resolve bands, dropping any whose terrain is absent.
            List<TerrainDef> terrains = new List<TerrainDef>();
            List<float> shares = new List<float>();
            foreach (RM_SeaFloorBand band in ext.bands)
            {
                TerrainDef t = band?.terrain.NullOrEmpty() == false ? DefDatabase<TerrainDef>.GetNamedSilentFail(band.terrain) : null;
                if (t == null)
                {
                    Log.Warning("[RM_DivingInteraction] sea floor band terrain '" + band?.terrain + "' not loaded; band skipped.");
                    continue;
                }
                if (band.share <= 0f)
                {
                    continue;
                }
                terrains.Add(t);
                shares.Add(band.share);
            }
            if (terrains.Count == 0)
            {
                return;
            }

            Perlin noise = new Perlin(ext.noiseFrequency, 2.0, 0.5, 4, Rand.Range(0, int.MaxValue), QualityMode.Medium);
            List<IntVec3> ranked = map.AllCells
                .OrderByDescending(c => noise.GetValue(c.x, 0.0, c.z))
                .ToList();
            int total = ranked.Count;
            int idx = 0;
            // bandOf[cellIndex] = band index, -1 = base floor.
            int[] bandOf = new int[total];
            for (int i = 0; i < total; i++)
            {
                bandOf[i] = -1;
            }
            CellIndices indices = map.cellIndices;
            for (int b = 0; b < terrains.Count; b++)
            {
                int count = (int)(shares[b] * total);
                for (int k = 0; k < count && idx < total; k++, idx++)
                {
                    IntVec3 c = ranked[idx];
                    bandOf[indices.CellToIndex(c)] = b;
                    map.terrainGrid.SetTerrain(c, terrains[b]);
                }
            }

            EnsureWalkable(map, ext, floor, terrains, bandOf);
        }

        private static bool Walkable(TerrainDef t) => t.passability != Traversability.Impassable;

        private static void EnsureWalkable(Map map, RM_SeaFloorBandsExtension ext, TerrainDef floor, List<TerrainDef> terrains, int[] bandOf)
        {
            if (terrains.All(Walkable))
            {
                return;
            }
            CellIndices indices = map.cellIndices;
            int total = indices.NumGridCells;
            int[] region = new int[total];
            List<int> regionSizes = new List<int>();
            int walkableTotal = 0;
            Queue<IntVec3> open = new Queue<IntVec3>();
            foreach (IntVec3 start in map.AllCells)
            {
                int si = indices.CellToIndex(start);
                if (!Walkable(start.GetTerrain(map)))
                {
                    continue;
                }
                walkableTotal++;
                if (region[si] != 0)
                {
                    continue;
                }
                int id = regionSizes.Count + 1;
                int size = 0;
                region[si] = id;
                open.Enqueue(start);
                while (open.Count > 0)
                {
                    IntVec3 c = open.Dequeue();
                    size++;
                    for (int d = 0; d < 4; d++)
                    {
                        IntVec3 n = c + GenAdj.CardinalDirections[d];
                        if (!n.InBounds(map))
                        {
                            continue;
                        }
                        int ni = indices.CellToIndex(n);
                        if (region[ni] == 0 && Walkable(n.GetTerrain(map)))
                        {
                            region[ni] = id;
                            open.Enqueue(n);
                        }
                    }
                }
                regionSizes.Add(size);
            }
            if (regionSizes.Count <= 1)
            {
                return;
            }
            int mainId = regionSizes.IndexOf(regionSizes.Max()) + 1;
            int mainSize = regionSizes[mainId - 1];

            if (walkableTotal > 0 && mainSize >= ext.minConnectedShare * walkableTotal)
            {
                // Fill each stranded walkable pocket with the first impassable
                // band terrain — it becomes part of the pool that enclosed it.
                TerrainDef fill = terrains.First(t => !Walkable(t));
                foreach (IntVec3 c in map.AllCells)
                {
                    int ci = indices.CellToIndex(c);
                    if (region[ci] != 0 && region[ci] != mainId)
                    {
                        map.terrainGrid.SetTerrain(c, fill);
                    }
                }
                return;
            }

            // Too fragmented: revert every impassable band cell to the next
            // walkable band outward, or the base floor.
            TerrainDef[] revertTo = new TerrainDef[terrains.Count];
            for (int b = 0; b < terrains.Count; b++)
            {
                revertTo[b] = terrains.Skip(b + 1).FirstOrDefault(Walkable) ?? floor;
            }
            foreach (IntVec3 c in map.AllCells)
            {
                int b = bandOf[indices.CellToIndex(c)];
                if (b >= 0 && !Walkable(terrains[b]))
                {
                    map.terrainGrid.SetTerrain(c, revertTo[b]);
                }
            }
        }
    }
}
