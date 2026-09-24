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
        private const int ShadeSearchRadius = 2;
        private const float ShadeCastingFillPercentThreshold = 0.8f;
        private const float ShadeCastingPlantVisualSize = 1.5f;
        private const float ShadeThreshold = 0.5f;

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
                return shade >= RM_OasisMakerSettings.shadeScoreFloor
                    && rock >= RM_OasisMakerSettings.rockScoreFloor;
            }

            /// 0..1, clamped, from how far shade/rock sit above their floors
            /// toward the "excellent" ceilings — average of both axes so a
            /// spot cannot buy full quality on one axis alone.
            public float Quality01()
            {
                float shadeQ = Mathf.InverseLerp(RM_OasisMakerSettings.shadeScoreFloor,
                    RM_OasisMakerSettings.shadeScoreExcellent, shade);
                float rockQ = Mathf.InverseLerp(RM_OasisMakerSettings.rockScoreFloor,
                    RM_OasisMakerSettings.rockScoreExcellent, rock);
                return Mathf.Clamp01((shadeQ + rockQ) / 2f);
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
            int radius = RM_OasisMakerSettings.scoringRadius;
            int shade = 0;
            int rock = 0;
            for (int dz = -radius; dz <= radius; dz++)
            {
                for (int dx = -radius; dx <= radius; dx++)
                {
                    IntVec3 cell = new IntVec3(center.x + dx, center.y, center.z + dz);
                    if (!cell.InBounds(map))
                    {
                        continue;
                    }
                    if (ShadeAt(map, cell) >= ShadeThreshold)
                    {
                        shade++;
                    }
                    if (IsRockCell(map, cell))
                    {
                        rock++;
                    }
                }
            }
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
            if (!cell.InBounds(map))
            {
                return 0f;
            }
            if (map.roofGrid.Roofed(cell))
            {
                return 1f;
            }
            float best = 0f;
            for (int dz = -ShadeSearchRadius; dz <= ShadeSearchRadius; dz++)
            {
                for (int dx = -ShadeSearchRadius; dx <= ShadeSearchRadius; dx++)
                {
                    if (dx == 0 && dz == 0)
                    {
                        continue;
                    }
                    IntVec3 neighbor = new IntVec3(cell.x + dx, cell.y, cell.z + dz);
                    if (!neighbor.InBounds(map) || !CastsShade(neighbor, map))
                    {
                        continue;
                    }
                    float dist = Mathf.Sqrt(dx * dx + dz * dz);
                    float score = Mathf.Clamp01(1f - dist / (ShadeSearchRadius + 1));
                    if (score > best)
                    {
                        best = score;
                    }
                }
            }
            return best;
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
