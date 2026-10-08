using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using Verse;

namespace RimMandrake.DivingInteraction
{
    // CHILL_RIME_TERRACES_1, 2026-09-28. Rime-terrace districts painted OVER
    // the freshly-laid RM_ChillIceBedrock base (GenStep_SeaFloorTerrain,
    // order 210) — "whole districts of the floor are stepped pale dunes of
    // shed rime" (item ruling). "The terrain is the fiction's residue, not
    // noise": districts are COHERENT REGIONS, grown by a capped flood-fill
    // blob from each seed cell, never an independent per-tile scatter.
    //
    // DENSITY CORRELATION WITH KRELLIK — the mechanism, not a coincidence:
    // this step is listed at order 920, immediately AFTER RM_SeaFloorFauna
    // (900), so by the time it runs every RM_Krellik this generation
    // actually spawned is already a real pawn standing on the map. Each
    // live Krellik's own cell is a blob seed. Krellik land independently at
    // random (GenStep_SeaFloorFauna.cs), so where several happen to land
    // near each other THIS generation, their blobs overlap and coalesce
    // into one larger district; where a Krellik is alone, its district
    // stays small. That IS "denser where Krellik density is higher" — read
    // off where Krellik actually concentrated this generation, not off a
    // scalar parameter that says nothing about spatial layout (the item's
    // own deliverable 3 offers this as the stronger of its two acceptable
    // routes: "wherever Krellik actually concentrate").
    //
    // FALLBACK: RM_Krellik has real commonality (0.5 in RM_TheChill's own
    // <wildAnimals> — the highest of the biome's residents) but is not
    // guaranteed a nonzero spawn count every single generation
    // (GenStep_SeaFloorFauna's own countForKind can round to a Rand.Chance
    // roll). A dive that rolls too few Krellik still gets a MinDistricts
    // floor of terrace seeds (placed on random standable ice, same as any
    // other seed) so the floor is never uniformly bare — sparse, not
    // broken.
    //
    // SCOPE: RM_ChillFireGate.IsChillSeabedMap(map) only, same identity
    // check every sibling Chill mechanism this session uses — defensive:
    // this step is also only ever listed on RM_SeaDiveGenerator_TheChill,
    // same pattern as GenStep_GreySeaFloorDressing's own scope guard.
    public class GenStep_ChillRimeTerraces : GenStep
    {
        // How far (in flood-fill rings) a district can spread from one
        // seed before growth chance has decayed to nothing. Keeps a single
        // seed's district a patch of a ~50x50 map, not a paintjob over the
        // whole floor.
        private const int MaxBlobRadius = 6;

        // Per-ring continuation chance, compounding outward (ring 1:
        // 0.72, ring 2: 0.72^2, ...) — gives each district a soft, organic
        // stepped edge instead of a hard-edged disc or per-tile noise.
        private const float RingContinueChance = 0.72f;

        // Floor on how many districts a dive gets even on a bad Krellik
        // roll — see header.
        private const int MinDistricts = 3;

        public override int SeedPart => 8362343;

        public override void Generate(Map map, GenStepParams parms)
        {
            if (!RM_ChillFireGate.IsChillSeabedMap(map))
            {
                return;
            }

            TerrainDef baseFloor = DefDatabase<TerrainDef>.GetNamed("RM_ChillIceBedrock");
            TerrainDef terrace = DefDatabase<TerrainDef>.GetNamed("RM_ChillRimeTerrace");

            List<IntVec3> seeds = map.mapPawns.AllPawnsSpawned
                .Where(p => p?.kindDef != null && p.kindDef.defName == "RM_Krellik")
                .Select(p => p.Position)
                .ToList();

            int fallbackNeeded = MinDistricts - seeds.Count;
            for (int i = 0; i < fallbackNeeded; i++)
            {
                if (CellFinder.TryFindRandomCell(map, c => c.Standable(map) && c.GetTerrain(map) == baseFloor && !seeds.Contains(c), out IntVec3 cell))
                {
                    seeds.Add(cell);
                }
            }

            foreach (IntVec3 seed in seeds)
            {
                GrowDistrict(map, seed, baseFloor, terrace);
            }
        }

        // Flood-fill blob growth from one seed cell. Cells already
        // converted by an earlier seed's blob read as non-baseFloor and
        // stop this blob's spread there — two nearby seeds' districts meet
        // and merge into one contiguous painted region rather than
        // double-processing, which is exactly the "coalesce where Krellik
        // concentrate" behaviour this step exists for.
        private void GrowDistrict(Map map, IntVec3 seed, TerrainDef baseFloor, TerrainDef terrace)
        {
            Queue<(IntVec3 cell, int ring)> frontier = new Queue<(IntVec3, int)>();
            HashSet<IntVec3> visited = new HashSet<IntVec3> { seed };
            frontier.Enqueue((seed, 0));

            while (frontier.Count > 0)
            {
                (IntVec3 cell, int ring) = frontier.Dequeue();
                if (!cell.InBounds(map))
                {
                    continue;
                }
                // Grow THROUGH an earlier district's terrace (no repaint) so overlapping
                // seeds enlarge the merged district instead of a later seed dying on contact.
                TerrainDef here = cell.GetTerrain(map);
                if (here == baseFloor)
                {
                    map.terrainGrid.SetTerrain(cell, terrace);
                }
                else if (here != terrace)
                {
                    continue;
                }

                if (ring >= MaxBlobRadius)
                {
                    continue;
                }

                foreach (IntVec3 offset in GenAdj.CardinalDirections)
                {
                    IntVec3 next = cell + offset;
                    if (!next.InBounds(map) || visited.Contains(next))
                    {
                        continue;
                    }
                    visited.Add(next);
                    if (Rand.Chance(Mathf.Pow(RingContinueChance, ring + 1)))
                    {
                        frontier.Enqueue((next, ring + 1));
                    }
                }
            }
        }
    }
}
