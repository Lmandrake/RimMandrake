using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.OasisMaker
{
    /// <summary>
    /// OASIS_MAKER_BUILD_1 §3. On-demand shade/rock scoring, standalone per
    /// the spec's own recommendation (§3 "Dependency decision owed... (b)
    /// copy the ~100-line sampler into this mod and stay standalone" —
    /// chosen over soft-depending on CreatureBehaviors' shade grid).
    ///
    /// ShadeAt's algorithm is copied from
    /// src/RimMandrake/CreatureBehaviors/Source/RM_MapComponent_ShadeGrid.cs
    /// (read 2026-09-24): roofed cells are full shade; otherwise a falloff
    /// score against the nearest adjacent shade-casting building (fillPercent
    /// >= 0.8) or plant (visualSizeRange.max >= 1.5) within a 2-cell search.
    /// Unlike that MapComponent, this is a STATIC, NO-CACHE query: the oasis
    /// maker only needs a score at ONE cell (the placement/machine cell)
    /// during placement preview and infrequent (RareTick) revalidation, never
    /// a whole-map grid, so a persistent per-map grid is not worth the extra
    /// moving part — see PERF NOTE below.
    ///
    /// RockScore's "natural rock edifice or rough-stone terrain" (§3) is two
    /// real, verified engine checks (decompiled 2026-09-24, not guessed):
    ///   - edifice: BuildingProperties.isNaturalRock (RimWorld/BuildingProperties.cs;
    ///     used the same way by GenStep_ScatterLumpsMineable, GenStep_AncientAltar, …)
    ///   - rough-stone floor: TerrainAffordanceDefOf.SmoothableStone, the exact
    ///     affordance Designator_SmoothFloors/Designator_SmoothSurface gate on
    ///     to decide whether a floor IS rough natural stone — defName-independent,
    ///     so it does not break on a modded stone type that doesn't end in "_Rough".
    /// </summary>
    public static class RM_OasisPlacementScorer
    {
        private const float ShadeCastingFillPercentThreshold = 0.8f;
        private const float ShadeCastingPlantVisualSize = 1.5f;
        private const float ShadeThreshold = RM_OasisKernel.ShadeThreshold;

        /// <summary>The map as the kernel's scoring reads it. One shared instance (main thread only): ContributingCells asks per cell.</summary>
        private sealed class MapGrid : IOasisGrid
        {
            public Map map;

            public bool InBounds(int x, int z) => new IntVec3(x, 0, z).InBounds(map);

            public bool Roofed(int x, int z) => map.roofGrid.Roofed(new IntVec3(x, 0, z));

            public bool CastsShade(int x, int z) => RM_OasisPlacementScorer.CastsShade(new IntVec3(x, 0, z), map);

            public bool IsRock(int x, int z) => IsRockCell(map, new IntVec3(x, 0, z));
        }

        private static readonly MapGrid SharedGrid = new MapGrid();

        private static MapGrid GridFor(Map map)
        {
            SharedGrid.map = map;
            return SharedGrid;
        }

        public readonly struct Score
        {
            public readonly int shade;
            public readonly int rock;

            public Score(int shade, int rock)
            {
                this.shade = shade;
                this.rock = rock;
            }

            public bool MeetsFloor()
            {
                return RM_OasisKernel.MeetsFloor(shade, rock, RM_OasisMakerSettings.shadeScoreFloor, RM_OasisMakerSettings.rockScoreFloor);
            }

            /// 0..1, clamped, from how far shade/rock sit above their floors
            /// toward the "excellent" ceilings — average of both axes so a
            /// spot cannot buy full quality on one axis alone.
            public float Quality01()
            {
                return RM_OasisKernel.Quality01(shade, rock, RM_OasisMakerSettings.shadeScoreFloor, RM_OasisMakerSettings.shadeScoreExcellent,
                    RM_OasisMakerSettings.rockScoreFloor, RM_OasisMakerSettings.rockScoreExcellent);
            }
        }

        // PERF NOTE (spec §3): "score is recomputed per ghost move; R=8 is
        // ~200 cells of array reads, fine at mouse rate, but cache the rock
        // scan per-map like ShadeGrid caches shade." A full ShadeAt call is
        // itself a small (2r+1)^2 scan, so this is O(radius^4)-ish per query
        // — acceptable for a UI-rate-only call (placement ghost held, one
        // building's RareTick revalidation) but NOT something to call every
        // frame for many machines at once. If a future pass adds many
        // simultaneous placement previews or a whole-map query, revisit with
        // a cached per-map grid exactly like RM_MapComponent_ShadeGrid.
        public static Score ScoreAt(Map map, IntVec3 center)
        {
            RM_OasisKernel.ScoreAt(GridFor(map), center.x, center.z, RM_OasisMakerSettings.scoringRadius, out int shade, out int rock);
            return new Score(shade, rock);
        }

        public static bool IsRockCell(Map map, IntVec3 cell)
        {
            if (!cell.InBounds(map))
            {
                return false;
            }
            Building edifice = cell.GetEdifice(map);
            if (edifice != null && edifice.def.building != null && edifice.def.building.isNaturalRock)
            {
                return true;
            }
            return cell.GetAffordances(map).Contains(TerrainAffordanceDefOf.SmoothableStone);
        }

        public static float ShadeAt(Map map, IntVec3 cell)
        {
            return RM_OasisKernel.ShadeAt(GridFor(map), cell.x, cell.z);
        }

        private static bool CastsShade(IntVec3 cell, Map map)
        {
            List<Thing> thingList = cell.GetThingList(map);
            for (int i = 0; i < thingList.Count; i++)
            {
                Thing thing = thingList[i];
                if (thing is Building && thing.def.fillPercent >= ShadeCastingFillPercentThreshold)
                {
                    return true;
                }
                if (thing is Plant plant && plant.def.plant != null
                    && plant.def.plant.visualSizeRange.max >= ShadeCastingPlantVisualSize)
                {
                    return true;
                }
            }
            return false;
        }

        /// Every cell within scoring radius whose shade (if shade=true) or
        /// rock (if shade=false) contribution is what earns the floor — used
        /// by the PlaceWorker to cyan/edge-tint "why this spot is good" (§3).
        public static IEnumerable<IntVec3> ContributingCells(Map map, IntVec3 center, bool shade)
        {
            int radius = RM_OasisMakerSettings.scoringRadius;
            for (int dz = -radius; dz <= radius; dz++)
            {
                for (int dx = -radius; dx <= radius; dx++)
                {
                    IntVec3 cell = new IntVec3(center.x + dx, center.y, center.z + dz);
                    if (!cell.InBounds(map))
                    {
                        continue;
                    }
                    bool contributes = shade ? ShadeAt(map, cell) >= ShadeThreshold : IsRockCell(map, cell);
                    if (contributes)
                    {
                        yield return cell;
                    }
                }
            }
        }
    }
}
