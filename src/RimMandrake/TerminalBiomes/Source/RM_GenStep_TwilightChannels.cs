using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.TerminalBiomes
{
    // TWILIGHT_CHANNEL_CURRENT_1 §1.2. Braids 1-3 channels from a map-edge
    // source to a sink basin at the low end, authoring
    // RM_MapComponent_ChannelCurrent's flow grid as it goes, paints
    // RM_ChannelBed/RM_BankSilt where those terrain defs exist (content
    // drop §8.2's own job — GetNamedSilentFail throughout, same posture as
    // GenStep_GreySeaFloorDressing in mandrake.rm.divinginteraction), and
    // places the stake-line (this item's own RM_BankStake) plus one
    // pre-existing Compact weir at the first eddy.
    //
    // ALGORITHM, and what is a build-time simplification rather than a
    // ruling (the spec specifies the SHAPE — braided channels, a sink at
    // the low end, 2-4 eddies, a stake-line every ~8 cells — never an
    // exact path-finding algorithm):
    //   1. Find the sink basin: lowest-elevation cell away from the map
    //      edge (GenStep_GreySeaFloorDressing's own FindBasinCell shape).
    //   2. Pick 1-3 source cells scattered around the map border.
    //   3. For each source, walk a straight line to the basin
    //      (GenSight.PointsOnLineOfSight — the same simplification
    //      GenStep_GreySeaFloorDressing's own CarveChannel already uses in
    //      this exact mod for "follow the channel downhill" rather than a
    //      true gradient walk) and lay CENTRE/MARGIN/band width around it.
    //   4. Stake every ~8 cells along the outer band edge.
    //   5. 2-4 eddies: evenly spaced points along the combined path,
    //      widened to MARGIN in a small radius; the Compact's own weir
    //      stands at the very first one.
    //   6. Register the sink cells with the component and paint the basin
    //      if RM_ChannelBed exists.
    // Keeps clear of any already-placed RM_SeaDiveHatch footprint (content
    // drop's own rule: "the ship never lands astride a channel").
    public class RM_GenStep_TwilightChannels : GenStep
    {
        private const int CentreHalfWidth = 0; // 1 cell wide centre lane
        private const int MarginHalfWidth = 2; // +2 cells either side of centre = margin
        private const int BandHalfWidth = 2; // +2 more cells either side = undersurge band
        private const float SinkRadius = 4f;
        private const int StakeSpacing = 8;
        private const float EddyRadius = 2.5f;
        private const float HatchExclusionRadius = 6f;

        public override int SeedPart => 5140938;

        public override void Generate(Map map, GenStepParams parms)
        {
            if (map?.Biome == null || map.Biome.defName != "RM_TwilightSea")
            {
                return;
            }

            RM_MapComponent_ChannelCurrent current = map.GetComponent<RM_MapComponent_ChannelCurrent>();
            if (current == null)
            {
                return;
            }

            IntVec3 sink = FindBasinCell(map);
            if (!sink.IsValid)
            {
                return;
            }

            List<IntVec3> hatchFootprints = FindHatchFootprints(map);

            int channelCount = Rand.RangeInclusive(1, 3);
            List<IntVec3> combinedPath = new List<IntVec3>();
            for (int i = 0; i < channelCount; i++)
            {
                IntVec3 source = RandomEdgeCell(map);
                List<IntVec3> path = new List<IntVec3>(GenSight.PointsOnLineOfSight(source, sink));
                AuthorChannel(map, current, path, hatchFootprints);
                combinedPath.AddRange(path);
            }

            PlaceEddies(map, current, combinedPath);
            RegisterSink(map, current, sink);
        }

        private static T Named<T>(string defName) where T : Def
        {
            return DefDatabase<T>.GetNamedSilentFail(defName);
        }

        // Same shape as GenStep_GreySeaFloorDressing.FindBasinCell — lowest
        // elevation, kept off the map edge.
        private static IntVec3 FindBasinCell(Map map)
        {
            MapGenFloatGrid elevation = MapGenerator.Elevation;
            IntVec3 best = IntVec3.Invalid;
            float bestVal = float.MaxValue;
            int margin = 12;
            foreach (IntVec3 c in map.AllCells)
            {
                if (c.x < margin || c.z < margin || c.x >= map.Size.x - margin || c.z >= map.Size.z - margin)
                {
                    continue;
                }
                float v = elevation[c];
                if (v < bestVal)
                {
                    bestVal = v;
                    best = c;
                }
            }
            return best;
        }

        private static IntVec3 RandomEdgeCell(Map map)
        {
            int side = Rand.RangeInclusive(0, 3);
            int x, z;
            switch (side)
            {
                case 0: x = Rand.Range(0, map.Size.x); z = 1; break;
                case 1: x = Rand.Range(0, map.Size.x); z = map.Size.z - 2; break;
                case 2: x = 1; z = Rand.Range(0, map.Size.z); break;
                default: x = map.Size.x - 2; z = Rand.Range(0, map.Size.z); break;
            }
            return new IntVec3(x, 0, z);
        }

        private static List<IntVec3> FindHatchFootprints(Map map)
        {
            List<IntVec3> result = new List<IntVec3>();
            ThingDef hatchDef = Named<ThingDef>("RM_SeaDiveHatch");
            if (hatchDef == null)
            {
                return result;
            }
            foreach (Thing t in map.listerThings.ThingsOfDef(hatchDef))
            {
                result.Add(t.Position);
            }
            return result;
        }

        private static bool NearHatch(IntVec3 c, List<IntVec3> hatches)
        {
            for (int i = 0; i < hatches.Count; i++)
            {
                if (c.DistanceTo(hatches[i]) <= HatchExclusionRadius)
                {
                    return true;
                }
            }
            return false;
        }

        private void AuthorChannel(Map map, RM_MapComponent_ChannelCurrent current, List<IntVec3> path, List<IntVec3> hatches)
        {
            TerrainDef bed = Named<TerrainDef>("RM_ChannelBed");
            TerrainDef bankSilt = Named<TerrainDef>("RM_BankSilt");
            ThingDef stake = Named<ThingDef>("RM_BankStake");

            int cellsSinceStake = 0;
            for (int i = 0; i < path.Count; i++)
            {
                IntVec3 centre = path[i];
                if (!centre.InBounds(map) || NearHatch(centre, hatches))
                {
                    continue;
                }

                RM_FlowDir dir = DirectionBetween(centre, i + 1 < path.Count ? path[i + 1] : centre);
                IntVec3 perp = PerpendicularOffset(dir);

                for (int w = -(MarginHalfWidth + BandHalfWidth); w <= MarginHalfWidth + BandHalfWidth; w++)
                {
                    IntVec3 c = centre + perp * w;
                    if (!c.InBounds(map) || NearHatch(c, hatches))
                    {
                        continue;
                    }

                    if (System.Math.Abs(w) <= CentreHalfWidth)
                    {
                        current.SetFlow(c, dir, RM_ChannelLane.Centre);
                        PaintIfPresent(map, c, bed);
                    }
                    else if (System.Math.Abs(w) <= MarginHalfWidth)
                    {
                        current.SetFlow(c, dir, RM_ChannelLane.Margin);
                        PaintIfPresent(map, c, bed);
                    }
                    else
                    {
                        int band = System.Math.Abs(w) - MarginHalfWidth;
                        current.SetBankBand(c, dir, band);
                        PaintIfPresent(map, c, bankSilt);
                    }
                }

                // Stake-line: every ~8 cells, on the outer band edge both
                // sides — "where the surge reaches, not where the calm
                // ends" (§4), i.e. at the very outside of the widened band.
                if (stake != null && ++cellsSinceStake >= StakeSpacing)
                {
                    cellsSinceStake = 0;
                    PlaceStakePair(map, centre, perp, stake);
                }
            }
        }

        private static void PlaceStakePair(Map map, IntVec3 centre, IntVec3 perp, ThingDef stake)
        {
            int outerOffset = MarginHalfWidth + BandHalfWidth + 1;
            foreach (int sign in new[] { -1, 1 })
            {
                IntVec3 c = centre + perp * (outerOffset * sign);
                if (c.InBounds(map) && c.Standable(map) && c.GetEdifice(map) == null)
                {
                    GenSpawn.Spawn(stake, c, map);
                }
            }
        }

        private void PlaceEddies(Map map, RM_MapComponent_ChannelCurrent current, List<IntVec3> combinedPath)
        {
            if (combinedPath.Count == 0)
            {
                return;
            }
            int eddyCount = Rand.RangeInclusive(2, 4);
            ThingDef weirDef = Named<ThingDef>("RM_BankWeir");

            for (int i = 0; i < eddyCount; i++)
            {
                IntVec3 centre = combinedPath[Rand.Range(0, combinedPath.Count)];
                foreach (IntVec3 c in GenRadial.RadialCellsAround(centre, EddyRadius, useCenter: true))
                {
                    if (c.InBounds(map) && current.HasCurrent(c))
                    {
                        current.SetFlow(c, current.FlowAt(c), RM_ChannelLane.Margin); // "where the carry releases"
                    }
                }

                // The Compact's own pre-existing weir stands at the first
                // eddy only (§4 tier note) — Inhabited dressing, never
                // breaches.
                if (i == 0 && weirDef != null)
                {
                    IntVec3 weirCell = FindStandableNear(map, centre);
                    if (weirCell.IsValid)
                    {
                        Thing weir = GenSpawn.Spawn(weirDef, weirCell, map);
                        if (weir is RM_Building_BankWeir bw)
                        {
                            bw.neverBreaches = true;
                        }
                    }
                }
            }
        }

        private static IntVec3 FindStandableNear(Map map, IntVec3 centre)
        {
            foreach (IntVec3 c in GenRadial.RadialCellsAround(centre, 3f, useCenter: true))
            {
                if (c.InBounds(map) && c.Standable(map) && c.GetEdifice(map) == null)
                {
                    return c;
                }
            }
            return IntVec3.Invalid;
        }

        private void RegisterSink(Map map, RM_MapComponent_ChannelCurrent current, IntVec3 sink)
        {
            TerrainDef pool = Named<TerrainDef>("RM_ChannelBed");
            List<IntVec3> cells = new List<IntVec3>();
            foreach (IntVec3 c in GenRadial.RadialCellsAround(sink, SinkRadius, useCenter: true))
            {
                if (!c.InBounds(map))
                {
                    continue;
                }
                cells.Add(c);
                PaintIfPresent(map, c, pool);
            }
            current.SetSinkCells(cells);
        }

        private static void PaintIfPresent(Map map, IntVec3 c, TerrainDef terrain)
        {
            if (terrain == null || !c.InBounds(map))
            {
                return;
            }
            map.terrainGrid.SetTerrain(c, terrain);
        }

        private static RM_FlowDir DirectionBetween(IntVec3 from, IntVec3 to)
        {
            if (from == to)
            {
                return RM_FlowDir.South;
            }
            float angle = (to - from).AngleFlat; // 0 = north, clockwise, vanilla convention
            int octant = Mathf.RoundToInt(angle / 45f) % 8;
            switch (octant)
            {
                case 0: return RM_FlowDir.North;
                case 1: return RM_FlowDir.NorthEast;
                case 2: return RM_FlowDir.East;
                case 3: return RM_FlowDir.SouthEast;
                case 4: return RM_FlowDir.South;
                case 5: return RM_FlowDir.SouthWest;
                case 6: return RM_FlowDir.West;
                default: return RM_FlowDir.NorthWest;
            }
        }

        // A perpendicular unit step for laying width either side of the
        // centreline — good enough for the four cardinal/diagonal families
        // this genstep ever produces (a straight source-to-sink line).
        private static IntVec3 PerpendicularOffset(RM_FlowDir dir)
        {
            IntVec3 f = RM_MapComponent_ChannelCurrent.Offset(dir);
            return new IntVec3(-f.z, 0, f.x);
        }
    }
}
