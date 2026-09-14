using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // GREENTIDE_MECHANICS_2 M9 build (greentide_kit_spec.md M9, "Root
    // causeways — map-gen"). FEVER_WOOD_MECHANICS_1's own item file names
    // this exact class as one of the two it is blocked on (F6, "boughway
    // network"). Ordered after GenStep_Terrain (order 210, same verified
    // anchor RUT_Miasma_GradientAxisGenStep.xml's own header cites) — see
    // this class's own GenStepDef order value in the MapGeneration
    // registration XML, set higher than RM_GenStep_LivingBoles' so a
    // paired map's boles are already registered when this runs.
    //
    // Anchor selection is configurable, not hardcoded to the Greatbole:
    // RM_MapComponent_LivingRegrowth's own registered bole centers when
    // present (M9 paired with M12), otherwise a fallback scatter picked
    // straight from RM_RootCausewayBiomeExtension's own fields (M9 running
    // standalone) — "so M9 can run standalone or paired with M12" per the
    // build brief. A no-op on any biome without the extension at all.
    public class RM_GenStep_RootCauseways : GenStep
    {
        private static readonly IntVec3[] EightDirs =
        {
            new IntVec3(1, 0, 0), new IntVec3(1, 0, 1), new IntVec3(0, 0, 1), new IntVec3(-1, 0, 1),
            new IntVec3(-1, 0, 0), new IntVec3(-1, 0, -1), new IntVec3(0, 0, -1), new IntVec3(1, 0, -1),
        };

        public override int SeedPart => 1908244413;

        public override void Generate(Map map, GenStepParams parms)
        {
            if (!RM_EnvironmentalHazardsSettings.rootCausewaysEnabled)
            {
                return; // MOD_OPTIONS_RETROFIT_1: WORLDGEN-AFFECTING master toggle
            }

            RM_RootCausewayBiomeExtension ext = map.Biome?.GetModExtension<RM_RootCausewayBiomeExtension>();
            if (ext == null)
            {
                return;
            }

            if (ext.causewayTerrain == null)
            {
                Log.Error("[RM EnvironmentalHazards] RM_GenStep_RootCauseways: biome " + map.Biome.defName
                    + "'s RM_RootCausewayBiomeExtension has no causewayTerrain — skipping.");
                return;
            }

            RM_MapComponent_LivingRegrowth livingRegrowth = map.GetComponent<RM_MapComponent_LivingRegrowth>();
            List<IntVec3> anchors = livingRegrowth != null && livingRegrowth.BoleCenters.Count > 0
                ? new List<IntVec3>(livingRegrowth.BoleCenters)
                : PickFallbackAnchors(map, ext);

            if (anchors.Count == 0)
            {
                Log.Warning("[RM EnvironmentalHazards] RM_GenStep_RootCauseways: no anchor points found on "
                    + map.Biome.defName + " — nothing to connect.");
                return;
            }

            for (int i = 0; i < anchors.Count; i++)
            {
                int pathCount = ext.pathsPerAnchorRange.RandomInRange;
                for (int p = 0; p < pathCount; p++)
                {
                    TraceSpline(map, ext, anchors[i]);
                }
            }

            ConnectNearestNeighbors(map, ext, anchors);
        }

        private List<IntVec3> PickFallbackAnchors(Map map, RM_RootCausewayBiomeExtension ext)
        {
            List<IntVec3> anchors = new List<IntVec3>();
            int count = ext.fallbackAnchorCountRange.RandomInRange;

            for (int i = 0; i < count; i++)
            {
                for (int attempt = 0; attempt < 60; attempt++)
                {
                    IntVec3 candidate = CellFinder.RandomCell(map);
                    if (candidate.x < ext.fallbackEdgeMargin || candidate.z < ext.fallbackEdgeMargin
                        || candidate.x >= map.Size.x - ext.fallbackEdgeMargin
                        || candidate.z >= map.Size.z - ext.fallbackEdgeMargin)
                    {
                        continue;
                    }
                    if (!candidate.Standable(map))
                    {
                        continue;
                    }

                    bool tooClose = false;
                    for (int j = 0; j < anchors.Count; j++)
                    {
                        if ((anchors[j] - candidate).LengthHorizontal < ext.fallbackMinAnchorSpacing)
                        {
                            tooClose = true;
                            break;
                        }
                    }
                    if (tooClose)
                    {
                        continue;
                    }

                    anchors.Add(candidate);
                    break;
                }
            }

            return anchors;
        }

        private void TraceSpline(Map map, RM_RootCausewayBiomeExtension ext, IntVec3 anchor)
        {
            IntVec3 cursor = anchor;
            int dirIndex = Rand.Range(0, EightDirs.Length);
            int length = ext.pathLengthRange.RandomInRange;
            int width = ext.laneWidthRange.RandomInRange;

            for (int step = 0; step < length; step++)
            {
                PaintFootprint(map, ext, cursor, width);

                if (Rand.Chance(ext.turnChancePerStep))
                {
                    dirIndex = (dirIndex + (Rand.Bool ? 1 : -1) + EightDirs.Length) % EightDirs.Length;
                }

                cursor += EightDirs[dirIndex];
                if (!cursor.InBounds(map))
                {
                    break;
                }
            }
        }

        // Every anchor connects to its own single nearest neighbor — not a
        // full minimum spanning tree, but enough for "the network spans the
        // map" per the kit spec's own text, at map-gen-appropriate cost.
        private void ConnectNearestNeighbors(Map map, RM_RootCausewayBiomeExtension ext, List<IntVec3> anchors)
        {
            if (anchors.Count < 2)
            {
                return;
            }

            HashSet<long> connected = new HashSet<long>();
            for (int i = 0; i < anchors.Count; i++)
            {
                int nearest = -1;
                int bestDist = int.MaxValue;
                for (int j = 0; j < anchors.Count; j++)
                {
                    if (i == j)
                    {
                        continue;
                    }
                    int d = (anchors[i] - anchors[j]).LengthHorizontalSquared;
                    if (d < bestDist)
                    {
                        bestDist = d;
                        nearest = j;
                    }
                }

                if (nearest < 0)
                {
                    continue;
                }

                int lo = Mathf.Min(i, nearest);
                int hi = Mathf.Max(i, nearest);
                long key = ((long)lo << 32) | (uint)hi;
                if (connected.Add(key))
                {
                    ConnectAnchors(map, ext, anchors[i], anchors[nearest]);
                }
            }
        }

        private void ConnectAnchors(Map map, RM_RootCausewayBiomeExtension ext, IntVec3 a, IntVec3 b)
        {
            float dx = b.x - a.x;
            float dz = b.z - a.z;
            float dist = Mathf.Sqrt(dx * dx + dz * dz);
            if (dist < 1f)
            {
                return;
            }
            dx /= dist;
            dz /= dist;

            int width = Mathf.Max(1, ext.laneWidthRange.min);
            int steps = Mathf.CeilToInt(dist);
            for (int i = 0; i <= steps; i++)
            {
                IntVec3 cell = new IntVec3(Mathf.RoundToInt(a.x + dx * i), 0, Mathf.RoundToInt(a.z + dz * i));
                PaintFootprint(map, ext, cell, width);
            }
        }

        private void PaintFootprint(Map map, RM_RootCausewayBiomeExtension ext, IntVec3 center, int width)
        {
            foreach (IntVec3 c in GenRadial.RadialCellsAround(center, width, true))
            {
                if (!c.InBounds(map))
                {
                    continue;
                }

                if (!ext.basinTerrains.NullOrEmpty() && !ext.basinTerrains.Contains(map.terrainGrid.TerrainAt(c)))
                {
                    continue; // restricted to basin terrain — leave everything else untouched
                }

                map.terrainGrid.SetTerrain(c, ext.causewayTerrain);
            }
        }
    }
}
