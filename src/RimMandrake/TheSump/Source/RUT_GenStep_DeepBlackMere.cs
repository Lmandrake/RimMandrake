using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.TheSump
{
    /// <summary>
    /// SUMP_TAR_HYDROLOGY_1 ruling 7 — the Deep Black: "a landmark-scale
    /// unbroken deep-tar mere -- beast country, undiggable from shore, the
    /// biome's 'ocean' at MAP scale." Explicitly NOT a world-map body (the
    /// ruling's own "no new world-map body; the frozen world stays
    /// untouched" clause) — this is pure map generation: one large,
    /// organically-grown blob of RM_TarDeep terrain (with a thin RM_TarShallow
    /// rim), carved once per Sump map, well clear of the edge.
    ///
    /// "Canal-connected, effectively infinite on-map source" (ruling 6) needs
    /// no new engine code at all: RM_MapComponent_Excavation.IsSourceCell
    /// (mandrake.rm.flowworks, FLOWWORKS_BUILD_PROGRAM_1 ruling 24) already
    /// reads ANY cell of natural TerrainDef.IsWater terrain as a source with
    /// zero excavation writes, and RM_TarDeep/RM_TarShallow (Defs/LiquidTypes/
    /// TerrainDefs/RM_Tar.xml) both carry the "Water" tag and are parented to
    /// WaterDeepBase/WaterShallowBase (read directly before writing this) —
    /// so IsWater already reads true for them. Placing the terrain is the
    /// whole job; the "infinite source" property comes free.
    ///
    /// Grown with a randomized flood-fill from a single seed cell (same
    /// reservoir-sampling shape RimMandrake.FlowWorks.Flood_FlowWorks.
    /// SpreadOneTile already uses, read directly before writing this, kept
    /// independent rather than shared since the two run on different
    /// engines — one ticks against a draining volume, this runs once against
    /// a fixed target size) rather than a fixed shape, so the mere reads
    /// organic on every map and never repeats a silhouette. Runs once at map
    /// generation; no MapComponent, no per-tick cost, nothing to save.
    ///
    /// Registered globally onto Base_Player (Patches/
    /// RUT_GenStep_DeepBlackMere_Register.xml) and self-gated on the map's
    /// own biome — same "register once, gate in code" posture
    /// RUT_GenStep_TarBeastPlacement/RM_GenStep_LiquidShores already use in
    /// this codebase — so registering it costs nothing on every other biome.
    /// </summary>
    public class RUT_GenStep_DeepBlackMere : GenStep
    {
        public override int SeedPart => 1861039201;

        // Both current Sump BiomeDefs by defName, matching the same
        // string-not-hard-reference posture RM_LiquidBodyDef.biomes already
        // uses for this exact RM/RUT twin pair — a bare string can never
        // dangle if either def is absent from the active mod set.
        private static readonly string[] SumpBiomeDefNames = { "RM_TheSump", "RUT_Sump" };

        // INVENTED-BUILD tuning: no owner number was given for the mere's own
        // size. Deliberately generous — smaller than this and "landmark-
        // scale... the biome's ocean at MAP scale" (ruling 7's own words) is
        // not true yet.
        private const int MinMereCells = 180;

        private const int MaxMereCells = 420;

        private const int MinEdgeDistance = 12;

        private const int SeedSampleTries = 300;

        private const int MaxGrowAttempts = 4000;

        public override void Generate(Map map, GenStepParams parms)
        {
            if (!RM_TheSumpSettings.deepBlackMereEnabled)
            {
                return;
            }

            BiomeDef biome = map.Biome;
            if (biome == null || !IsSumpBiome(biome))
            {
                return;
            }

            TerrainDef deep = DefDatabase<TerrainDef>.GetNamedSilentFail("RM_TarDeep");
            if (deep == null)
            {
                // mandrake.rm.flowworks absent or renamed -- the biome's own
                // scattered tar pockets never generated either in that case,
                // so there is nothing for a mere to be made of. No-op, same
                // posture RUT_GenStep_TarBeastPlacement's own validator
                // already takes on the same absence.
                return;
            }
            TerrainDef shallow = DefDatabase<TerrainDef>.GetNamedSilentFail("RM_TarShallow");

            IntVec3 seed = CellFinderLoose.RandomCellWith(c => IsSeedCandidate(c, map), map, SeedSampleTries);
            if (!seed.IsValid)
            {
                return; // map too small, or too obstructed, to seat a real mere -- skip gracefully
            }

            HashSet<IntVec3> blob = GrowBlob(map, seed);
            if (blob.Count < MinMereCells)
            {
                // Could not carve a real mere here -- leave the map
                // untouched rather than ship an undersized puddle wearing
                // the landmark's name.
                return;
            }

            HashSet<IntVec3> rim = new HashSet<IntVec3>();
            foreach (IntVec3 c in blob)
            {
                map.terrainGrid.SetTerrain(c, deep);
                if (shallow == null)
                {
                    continue;
                }
                for (int i = 0; i < 4; i++)
                {
                    IntVec3 n = c + GenAdj.CardinalDirections[i];
                    if (n.InBounds(map) && !blob.Contains(n))
                    {
                        rim.Add(n);
                    }
                }
            }
            if (shallow != null)
            {
                foreach (IntVec3 c in rim)
                {
                    if (CanCarry(c, map))
                    {
                        map.terrainGrid.SetTerrain(c, shallow);
                    }
                }
            }

            Log.Message("[RimMandrake.TheSump] the Deep Black mere generated: " + blob.Count
                + " deep-tar cell(s), " + rim.Count + "-cell shallow rim, seed " + seed
                + ", biome " + biome.defName + ", tile " + map.Tile.tileId + ".");
        }

        private static bool IsSumpBiome(BiomeDef biome)
        {
            for (int i = 0; i < SumpBiomeDefNames.Length; i++)
            {
                if (biome.defName == SumpBiomeDefNames[i])
                {
                    return true;
                }
            }
            return false;
        }

        private static bool IsSeedCandidate(IntVec3 c, Map map)
        {
            return EdgeDistance(c, map) >= MinEdgeDistance && CanCarry(c, map);
        }

        private static int EdgeDistance(IntVec3 c, Map map)
        {
            int distX = Mathf.Min(c.x, map.Size.x - 1 - c.x);
            int distZ = Mathf.Min(c.z, map.Size.z - 1 - c.z);
            return Mathf.Min(distX, distZ);
        }

        // What may become part of the mere or its rim: ordinary open ground,
        // nothing already built on and nothing already water (a river should
        // stay a river, not get swallowed into the mere).
        private static bool CanCarry(IntVec3 c, Map map)
        {
            if (!c.InBounds(map) || c.OnEdge(map))
            {
                return false;
            }
            TerrainDef t = map.terrainGrid.TerrainAt(c);
            if (t == null || t.IsWater)
            {
                return false;
            }
            if (c.GetEdifice(map) != null)
            {
                return false;
            }
            return true;
        }

        /// <summary>Randomized flood-fill: repeatedly pop a random frontier
        /// cell and try to grow into one open cardinal neighbour, picked
        /// uniformly among the eligible ones via reservoir sampling -- the
        /// same shape Flood_FlowWorks.SpreadOneTile already uses, kept as an
        /// independent copy here (see the class header for why).</summary>
        private static HashSet<IntVec3> GrowBlob(Map map, IntVec3 seed)
        {
            HashSet<IntVec3> placed = new HashSet<IntVec3> { seed };
            List<IntVec3> frontier = new List<IntVec3> { seed };
            int targetSize = Rand.RangeInclusive(MinMereCells, MaxMereCells);
            int attempts = MaxGrowAttempts;

            while (placed.Count < targetSize && frontier.Count > 0 && attempts-- > 0)
            {
                int pick = Rand.Range(0, frontier.Count);
                IntVec3 from = frontier[pick];
                IntVec3 target = IntVec3.Invalid;
                int seen = 0;
                for (int i = 0; i < 4; i++)
                {
                    IntVec3 n = from + GenAdj.CardinalDirections[i];
                    if (placed.Contains(n) || !CanCarry(n, map))
                    {
                        continue;
                    }
                    seen++;
                    if (Rand.Range(0, seen) == 0)
                    {
                        target = n;
                    }
                }
                if (!target.IsValid)
                {
                    frontier.RemoveAt(pick);
                    continue;
                }
                placed.Add(target);
                frontier.Add(target);
            }

            return placed;
        }
    }
}
