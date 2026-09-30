using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FloodedCanyon
{
    // ════════════════════════════════════════════════════════════════════
    // CRACKEDLANDS_MECHANICS_BUILD_1 §3 — FOSSILS IN THE WALLS.
    //
    // Two entry points over one placement rule:
    //
    //   SeedMap   — map generation (RM_GenStep_FossilStrata). Fossil-bearing
    //               strata go into canyon wall FACES, biased low (the wall
    //               foot, by the generator's own elevation grid), with the
    //               deep-stratum tier only well inside the rock.
    //   RecutAlong — the recede (RM_MapComponent_CanyonFlood.RecedeFlood).
    //               A few natural-rock cells touching the wetted line turn
    //               into FRESH seams: "the flood re-cuts the ledger". The
    //               deep tier is allowed here too — the bible's "found only
    //               deep in the walls or where a flood has just cut a fresh
    //               face".
    //
    // A seam only ever REPLACES an existing natural, non-resource rock cell
    // (ThingDef.building.isNaturalRock && !isResourceRock). It never creates
    // rock, never touches a vein, a player building or a smoothed/built wall,
    // so it cannot change the map's shape — only what a wall cell yields
    // when mined. The seam defs themselves are the ruled content
    // (RM_FossilSeams.xml, RockBase mineables).
    // ════════════════════════════════════════════════════════════════════
    public static class RM_FossilStrata
    {
        // Base rates per 10,000 map cells at density 1. The bible's shape:
        // impressions common ("the walls hold thousands of them" — relative
        // to the other tiers, not literally), articulated rare, deep uniques
        // quest-grade. A 250x250 map (62,500 cells) at density 1 gets
        // ~6 impression runs, ~2 articulated seams, ~1 deep-stratum seam
        // on average — tunable through fossilSeamDensity.
        private const float ImpressionRunsPer10k = 1.0f;
        private const float SkeletonSeamsPer10k = 0.3f;
        private const float UniqueSeamsPer10k = 0.12f;

        // Deep stratum lives at least this many cells inside the rock face.
        private const int DeepMinDepth = 3;

        public static bool IsNaturalWallRock(IntVec3 c, Map map)
        {
            if (!c.InBounds(map))
            {
                return false;
            }
            Building ed = c.GetEdifice(map);
            if (ed == null || ed.def.building == null)
            {
                return false;
            }
            return ed.def.building.isNaturalRock && !ed.def.building.isResourceRock;
        }

        // A face: natural rock with at least one cardinal neighbour that is
        // open (no edifice at all, i.e. floor a pawn could stand on).
        private static bool IsFace(IntVec3 c, Map map)
        {
            if (!IsNaturalWallRock(c, map))
            {
                return false;
            }
            for (int i = 0; i < 4; i++)
            {
                IntVec3 n = c + GenAdj.CardinalDirections[i];
                if (n.InBounds(map) && n.GetEdifice(map) == null)
                {
                    return true;
                }
            }
            return false;
        }

        public static void SeedMap(Map map, float density, MapGenFloatGrid elevation)
        {
            if (density <= 0f)
            {
                return;
            }
            float per10k = map.Area / 10000f * density;

            // Depth-into-rock by BFS from every face, capped at DeepMinDepth+2
            // (nothing deeper matters to the rule).
            Dictionary<IntVec3, int> depth = new Dictionary<IntVec3, int>();
            Queue<IntVec3> frontier = new Queue<IntVec3>();
            List<IntVec3> faces = new List<IntVec3>();
            foreach (IntVec3 c in map.AllCells)
            {
                if (IsFace(c, map))
                {
                    faces.Add(c);
                    depth[c] = 1;
                    frontier.Enqueue(c);
                }
            }
            if (faces.Count == 0)
            {
                return;
            }
            List<IntVec3> deep = new List<IntVec3>();
            while (frontier.Count > 0)
            {
                IntVec3 c = frontier.Dequeue();
                int d = depth[c];
                if (d >= DeepMinDepth + 2)
                {
                    continue;
                }
                for (int i = 0; i < 4; i++)
                {
                    IntVec3 n = c + GenAdj.CardinalDirections[i];
                    if (depth.ContainsKey(n) || !IsNaturalWallRock(n, map))
                    {
                        continue;
                    }
                    depth[n] = d + 1;
                    if (d + 1 >= DeepMinDepth)
                    {
                        deep.Add(n);
                    }
                    frontier.Enqueue(n);
                }
            }

            // "Biased low": weight a face by how low it sits. Rock only
            // exists above ~0.7 elevation, so the wall foot reads ~0.7 and a
            // mountain crown ~1.0+. No elevation grid (a map made outside
            // normal generation) -> flat weights.
            System.Func<IntVec3, float> lowWeight = c =>
            {
                if (elevation == null)
                {
                    return 1f;
                }
                float e = elevation[c];
                return 0.15f + (1f - Mathf.InverseLerp(0.7f, 1.05f, e));
            };

            int impressionRuns = GenMath.RoundRandom(per10k * ImpressionRunsPer10k);
            for (int i = 0; i < impressionRuns; i++)
            {
                if (faces.TryRandomElementByWeight(lowWeight, out IntVec3 start))
                {
                    PlaceRun(map, start, RM_FloodedCanyonDefOf.RM_FossilSeam_Impression, Rand.RangeInclusive(2, 4));
                }
            }

            int skeletons = GenMath.RoundRandom(per10k * SkeletonSeamsPer10k);
            for (int i = 0; i < skeletons; i++)
            {
                if (faces.TryRandomElementByWeight(lowWeight, out IntVec3 c) && IsNaturalWallRock(c, map))
                {
                    Replace(map, c, RM_FloodedCanyonDefOf.RM_FossilSeam_Skeleton);
                }
            }

            int uniques = GenMath.RoundRandom(per10k * UniqueSeamsPer10k);
            for (int i = 0; i < uniques && deep.Count > 0; i++)
            {
                IntVec3 c = deep.RandomElement();
                if (IsNaturalWallRock(c, map))
                {
                    Replace(map, c, RM_FloodedCanyonDefOf.RM_FossilSeam_Unique);
                }
            }
        }

        // A short run along the face: walks to neighbouring face cells so an
        // impression seam reads as a band in the wall, not a lone pixel.
        private static void PlaceRun(Map map, IntVec3 start, ThingDef seam, int length)
        {
            IntVec3 cur = start;
            for (int n = 0; n < length; n++)
            {
                if (!IsFace(cur, map))
                {
                    return;
                }
                Replace(map, cur, seam);
                IntVec3 next = IntVec3.Invalid;
                for (int i = 0; i < 8; i++)
                {
                    IntVec3 cand = cur + GenAdj.AdjacentCells[(i + Rand.Range(0, 8)) % 8];
                    if (IsFace(cand, map))
                    {
                        next = cand;
                        break;
                    }
                }
                if (!next.IsValid)
                {
                    return;
                }
                cur = next;
            }
        }

        // Fresh seams along the wetted line. Returns how many were cut.
        public static int RecutAlong(Map map, IEnumerable<IntVec3> wetted, int count)
        {
            if (count <= 0)
            {
                return 0;
            }
            HashSet<IntVec3> candidates = new HashSet<IntVec3>();
            foreach (IntVec3 w in wetted)
            {
                for (int i = 0; i < 8; i++)
                {
                    IntVec3 n = w + GenAdj.AdjacentCells[i];
                    if (IsNaturalWallRock(n, map))
                    {
                        candidates.Add(n);
                    }
                }
            }
            if (candidates.Count == 0)
            {
                return 0;
            }
            List<IntVec3> list = new List<IntVec3>(candidates);
            list.Shuffle();
            int cut = 0;
            for (int i = 0; i < list.Count && cut < count; i++)
            {
                // A fresh face: mostly impressions, sometimes articulated, and
                // the one place outside the deep rock a deep-stratum seam shows.
                float r = Rand.Value;
                ThingDef seam = r < 0.06f ? RM_FloodedCanyonDefOf.RM_FossilSeam_Unique
                    : r < 0.26f ? RM_FloodedCanyonDefOf.RM_FossilSeam_Skeleton
                    : RM_FloodedCanyonDefOf.RM_FossilSeam_Impression;
                if (Replace(map, list[i], seam))
                {
                    cut++;
                }
            }
            return cut;
        }

        private static bool Replace(Map map, IntVec3 c, ThingDef seam)
        {
            if (seam == null)
            {
                return false;
            }
            Building ed = c.GetEdifice(map);
            if (ed == null || ed.def.building == null || !ed.def.building.isNaturalRock || ed.def.building.isResourceRock)
            {
                return false;
            }
            ed.Destroy(DestroyMode.Vanish);
            GenSpawn.Spawn(ThingMaker.MakeThing(seam), c, map);
            return true;
        }
    }

    // Registered on MapCommonBase (Patches/RM_FloodedCanyon_FossilStrata_Register.xml)
    // so every map generator that builds natural terrain carries it — a
    // player map, an encounter map and a faction base alike. Gated on the
    // BIOME (plus the settings) inside Generate, so it is a no-op elsewhere.
    public class RM_GenStep_FossilStrata : GenStep
    {
        public override int SeedPart => 1628093411;

        public override void Generate(Map map, GenStepParams parms)
        {
            if (!RM_FloodedCanyonSettings.fossilSeamsEnabled)
            {
                return;
            }
            if (map.Biome != RM_FloodedCanyonDefOf.RM_FloodedCanyon && !RM_FloodedCanyonSettings.fossilSeamsInOtherBiomes)
            {
                return;
            }
            RM_FossilStrata.SeedMap(map, RM_FloodedCanyonSettings.fossilSeamDensity, MapGenerator.Elevation);
        }
    }
}
