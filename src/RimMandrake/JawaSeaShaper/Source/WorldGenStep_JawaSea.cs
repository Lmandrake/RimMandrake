using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;
using Verse.Noise;

namespace JawaSeaShaper
{
    // A quarter ocean, in three torn bodies in the habitable ring.
    //
    // NOT near the poles - this planet's isotherms are circles around the
    // subsolar point, not latitude bands. See PickHabitableRingSeeds.
    //
    // Spec: design/Jawa/worldbuilding/worldgen_sea_spec.md (VISION, c2b0026).
    // Owner's ruling it implements: "A quarter ocean, split into three different
    // bodies that are oddly shaped rather than round or reasonable. Only a few
    // rivers flow from nearby mountains into these bodies."
    //
    // ORDER 20, AND THAT IS THE WHOLE TRICK. We do not build rivers. We finish
    // before vanilla builds them, so vanilla's own river step flows into the seas
    // we just made. Verified against the shipped defs: Terrain 0, Tiles 5, then
    // NOTHING until Lakes 150 and Rivers 200 — a 145-wide gap, so this cannot
    // collide with a vanilla neighbour.
    //
    // IT IS MOSTLY A REMOVAL JOB. Vanilla generates 43-55% ocean unaided and the
    // target is 25%, so this raises most of the planet and lowers three patches.
    //
    // THE SEA-LEVEL RULE, read from IL rather than assumed —
    // SurfaceTile::get_WaterCovered is 17 bytes and it is exactly this:
    //     ldfld Tile::elevation / ldc.r4 0.0 / cgt.un / ldc.i4.0 / ceq
    // i.e. WaterCovered == (elevation <= 0). There is no sea-level setting
    // anywhere in vanilla, so elevation IS the sea.
    //
    // 🔴 WRITE ELEVATION AND BIOME TOGETHER, BOTH DIRECTIONS. Things that go
    // underwater read elevation, not the label. A tile labelled Ocean carrying
    // land elevation looks like sea and behaves like ground, and the reverse is
    // just as broken.
    public class WorldGenStep_JawaSea : WorldGenStep
    {
        public override int SeedPart => 1927341055;

        // ---- the targets, straight off the spec's acceptance table ----
        private const float TargetWaterFraction = 0.25f;   // accept 22-28%
        private const int Bodies = 3;                      // exactly three
        private const float MinCompactness = 25f;          // a circle is 4*pi = 12.57

        // 🔴 THE SPEC'S ONE SHAPE REQUIREMENT THAT CARRIED NO NUMBER.
        // worldgen_sea_spec.md test 4 item 4 says "long and torn, not round and
        // torn" and stops there, while raggedness has a hard gate (25, above).
        // An unmeasured requirement is the one that gets quietly failed, so this
        // is a number I chose rather than one I was given: a body must be at
        // least twice as long as it is wide. 2.0 is deliberately modest — it
        // rejects a disc without demanding a ribbon, and item 3 of the same test
        // forbids a ring, so pushing this higher would walk into that.
        // ⚠️ If VISION sets a real number, this constant is the only edit.
        private const float MinAspect = 2.0f;

        // Depth we write for claimed sea, and the floor we guarantee for raised
        // land. Both only have to sit the right side of zero — see the IL above.
        private const float SeaElevation = -350f;
        private const float MinLandElevation = 12f;

        // Patch scale for the shape field. Deliberately HIGH frequency: this
        // noise is what tears the coastline, and a low frequency would grow
        // smooth blobs — the exact failure the spec calls out.
        private const double ShapeFrequency = 0.85;

        // A body must reach this share of its quota to count as a body at all.
        // Below it we log a shortfall rather than loop — a hung worldgen is worse
        // than a 21% sea, and the spec forbids unbounded loops.
        private const float MinBodyFill = 0.5f;

        public override void GenerateFresh(string seed, PlanetLayer layer)
        {
            if (layer == null || layer != Find.WorldGrid.Surface)
            {
                return;
            }

            BiomeDef ocean = BiomeDefOf.Ocean;
            if (ocean == null)
            {
                Log.Error("[JawaSea] BiomeDefOf.Ocean is null; leaving the world alone.");
                return;
            }

            int count = layer.TilesCount;
            if (count <= 0)
            {
                return;
            }

            // PlanetTile.tileId is GLOBAL across planet layers, while this step
            // works in layer-local indices 0..TilesCount. Build the map once
            // rather than assuming they coincide — on a multi-layer planet they
            // do not, and every array below is indexed locally.
            PlanetTile[] tileOf = new PlanetTile[count];
            Tile[] infoOf = new Tile[count];
            Dictionary<int, int> localOf = new Dictionary<int, int>(count);
            for (int i = 0; i < count; i++)
            {
                PlanetTile t = layer.PlanetTileForID(i);
                tileOf[i] = t;
                infoOf[i] = layer[t];
                localOf[t.tileId] = i;
            }

            int[][] neighboursOf = BuildNeighbourTable(layer, tileOf, localOf, count);

            // ---------------------------------------------------------------
            // PHASE 1 — raise the whole planet, carrying biome and elevation in
            // from the nearest original land.
            //
            // Vanilla has already assigned biomes at order 5 and nothing re-runs
            // that, so every tile we lift out of the sea needs a land biome from
            // us or it stays labelled Ocean on dry ground.
            //
            // ⭐ NEAREST-LAND-NEIGHBOUR IS A CONTINUITY RULE, NOT A MIX DECISION.
            // Raised beside badlands becomes badlands. It deliberately commits to
            // nothing about the planet's biome mix, which is a separate ruling the
            // owner is still reviewing — VISION's instruction, and the reason this
            // is a BFS from existing land rather than any kind of choice.
            // ---------------------------------------------------------------
            BiomeDef[] biomeSource = new BiomeDef[count];
            float[] elevationSource = new float[count];
            int originalWater = FloodLandOutward(count, neighboursOf, infoOf,
                                                 biomeSource, elevationSource);

            for (int i = 0; i < count; i++)
            {
                Tile info = infoOf[i];
                if (info == null || !info.WaterCovered)
                {
                    continue;
                }
                if (biomeSource[i] == null)
                {
                    // An all-water planet, or an isolated basin with no land in
                    // reach. Nothing sane to copy; leave the tile as it is rather
                    // than invent a biome.
                    continue;
                }
                info.PrimaryBiome = biomeSource[i];
                info.elevation = Mathf.Max(MinLandElevation, elevationSource[i]);
            }

            // ---------------------------------------------------------------
            // PHASE 2 — three seeds in the HABITABLE RING (31.5-58.5 deg of arc from
            // the subsolar point), deterministic from the world seed. NOT poles-ward:
            // see PickHabitableRingSeeds for why latitude is the wrong axis here.
            // ---------------------------------------------------------------
            int worldSeed = Gen.HashCombineInt(Find.World.info.Seed, SeedPart);
            Perlin shape = new Perlin(ShapeFrequency, 2.0, 0.5, 4,
                                      Gen.HashCombineInt(worldSeed, 0x5EA), QualityMode.Medium);

            int quota = Mathf.RoundToInt(count * TargetWaterFraction);
            int perBody = Mathf.Max(1, quota / Bodies);

            List<int> seeds = PickHabitableRingSeeds(layer, tileOf, count, worldSeed);

            // ---------------------------------------------------------------
            // PHASE 3 — grow each body by INVASION PERCOLATION.
            //
            // Each step claims the frontier tile standing highest in the noise
            // field, never the nearest one. That is the difference between a
            // coastline and a disc: growth follows the noise's ridges, so it
            // sends out peninsulas and leaves bays behind, and the compactness
            // score comes out fractal instead of round.
            //
            // Ranking rather than thresholding also fixes the quota exactly — a
            // Perlin field is bell-shaped, so any fixed cut gives a share that
            // moves with the seed. (Same reasoning as GravTide's order-20 step,
            // which is the in-stack precedent for working at this order.)
            // ---------------------------------------------------------------
            int[] bodyOf = new int[count];
            for (int i = 0; i < count; i++)
            {
                bodyOf[i] = -1;
            }

            int claimed = 0;
            for (int b = 0; b < seeds.Count; b++)
            {
                claimed += GrowBody(seeds[b], b + 1, perBody, layer, tileOf,
                                    neighboursOf, bodyOf, shape);
            }

            // ---------------------------------------------------------------
            // PHASE 4 — one body per seed, exactly. Ragged growth throws off
            // detached tiles, and the spec fails a stray single tile.
            //
            // ⚠️ ORPHAN REMOVAL IS NOT SMOOTHING. Smoothing shortens a coastline
            // and lowers the compactness score; deleting a detached tile does
            // neither. VISION's ruling, and the reason cleanup is allowed here at
            // all — test 3 stays binding, so if this drops the score below 25 the
            // cleanup went too far and the run should be reported as failing.
            // ---------------------------------------------------------------
            int orphans = KeepLargestComponentPerBody(count, neighboursOf, bodyOf, seeds.Count);
            claimed -= orphans;

            // ---------------------------------------------------------------
            // PHASE 5 — write the sea. Elevation AND biome, together.
            // ---------------------------------------------------------------
            for (int i = 0; i < count; i++)
            {
                if (bodyOf[i] <= 0)
                {
                    continue;
                }
                Tile info = infoOf[i];
                if (info == null)
                {
                    continue;
                }
                info.elevation = SeaElevation;
                info.PrimaryBiome = ocean;
            }

            Report(count, originalWater, claimed, quota, bodyOf, neighboursOf,
                   layer, tileOf, seeds.Count, orphans);
        }

        // -------------------------------------------------------------------
        // Neighbour table, built once. GetTileNeighbors allocates into a list on
        // every call, and this step asks for neighbours several times per tile
        // across five phases.
        // -------------------------------------------------------------------
        private static int[][] BuildNeighbourTable(PlanetLayer layer, PlanetTile[] tileOf,
                                                   Dictionary<int, int> localOf, int count)
        {
            int[][] table = new int[count][];
            List<PlanetTile> scratch = new List<PlanetTile>(8);
            List<int> local = new List<int>(8);
            for (int i = 0; i < count; i++)
            {
                scratch.Clear();
                local.Clear();
                layer.GetTileNeighbors(tileOf[i], scratch);
                for (int n = 0; n < scratch.Count; n++)
                {
                    int li;
                    // A neighbour off this layer, or off the rim of a partial
                    // world, simply is not a candidate.
                    if (scratch[n].Valid && localOf.TryGetValue(scratch[n].tileId, out li))
                    {
                        local.Add(li);
                    }
                }
                table[i] = local.ToArray();
            }
            return table;
        }

        // -------------------------------------------------------------------
        // Multi-source BFS outward from every ORIGINAL land tile, carrying that
        // land's biome and elevation into the water. Breadth-first from all
        // sources at once means each water tile is reached by its nearest land,
        // which is the continuity rule, and it is O(tiles) rather than a nearest
        // search per tile.
        // -------------------------------------------------------------------
        private static int FloodLandOutward(int count, int[][] neighboursOf, Tile[] infoOf,
                                            BiomeDef[] biomeSource, float[] elevationSource)
        {
            Queue<int> queue = new Queue<int>();
            bool[] seen = new bool[count];
            int water = 0;

            for (int i = 0; i < count; i++)
            {
                Tile info = infoOf[i];
                if (info == null)
                {
                    seen[i] = true;
                    continue;
                }
                if (info.WaterCovered)
                {
                    water++;
                    continue;
                }
                seen[i] = true;
                biomeSource[i] = info.PrimaryBiome;
                elevationSource[i] = info.elevation;
                queue.Enqueue(i);
            }

            while (queue.Count > 0)
            {
                int at = queue.Dequeue();
                int[] near = neighboursOf[at];
                for (int n = 0; n < near.Length; n++)
                {
                    int to = near[n];
                    if (seen[to])
                    {
                        continue;
                    }
                    seen[to] = true;
                    biomeSource[to] = biomeSource[at];
                    elevationSource[to] = elevationSource[at];
                    queue.Enqueue(to);
                }
            }
            return water;
        }

        // -------------------------------------------------------------------
        // 🔴 THIS PLANET'S CLIMATE IS NOT BANDED BY LATITUDE. Corrected
        // 2026-08-14 against the shipping source of Alien Worlds - Tidally
        // Locked, workshop 3631364335, Source/PlanetTypeDef.cs:83-90:
        //
        //     effectiveLat = Acos(Cos(lon*Deg2Rad) * Cos(lat*Deg2Rad)) * Rad2Deg
        //     temp         = AvgTempByLatitudeCurve.Evaluate(effectiveLat / 90)
        //
        // A transpiler on WorldGenStep_Terrain.GenerateTileFor DELETES the .y
        // load and calls that instead, so vanilla's latitude-only path never
        // runs on this planet. `effectiveLat` is the great-circle ARC DISTANCE
        // FROM THE SUBSOLAR POINT (lon 0, lat 0) — the isotherms are CIRCLES
        // centred on (0,0), not latitude bands. That is also why the curve runs
        // past x = 1.0 at all: |lat| alone tops out at 90 deg, and only
        // longitude can carry the argument to 2.0.
        //
        // ⚠️ Why latitude cannot be patched into working: lat 45 / lon 0 is 45
        // deg of arc out and warm, while lat 45 / lon 120 is 110.7 deg out and
        // about -62 C. Same latitude, opposite worlds. The old predicate here
        // (|lat| > 45) could not tell them apart, and it aimed at the NIGHTSIDE.
        //
        // The band below is the spec's own 0.35-0.65 read on the correct axis:
        // the curve's x is effectiveLat/90, so x 0.35-0.65 is 31.5-58.5 deg of
        // arc. Independently interpolated off the shipped curve points
        // (0.0,70 · 0.1,65 · 0.5,14 · 1.0,-37 · 1.3,-70 · 2.0,-80), liquid water
        // sits at 0 C at 57.3 deg and +30 C at 33.7 deg — inside this band. The
        // spec's NUMBERS were right; only its axis label ("latitude", and x=0.5
        // called "the terminator") was wrong. The true terminator is x = 1.0.
        // -------------------------------------------------------------------
        private const float RingInnerDeg = 31.5f;   // curve x 0.35, about +32 C
        private const float RingOuterDeg = 58.5f;   // curve x 0.65, about -3 C
        // Past the true terminator (90 deg, curve x 1.0, -37 C). This is where the
        // deliberately off-pattern third body goes — see PickHabitableRingSeeds.
        private const float NightsideMinDeg = 100f; // curve x 1.11, about -45 C

        /// <summary>
        /// Great-circle arc distance in degrees from the subsolar point
        /// (lon 0, lat 0). Mirrors the mod's own BaseTemperatureAtLongLat, so
        /// this bands on exactly what the game scores the tile with.
        /// </summary>
        private static float ArcFromSubsolar(PlanetLayer layer, PlanetTile tile)
        {
            Vector2 ll = layer.LongLatOf(tile);
            float c = Mathf.Cos(ll.x * Mathf.Deg2Rad) * Mathf.Cos(ll.y * Mathf.Deg2Rad);
            return Mathf.Acos(Mathf.Clamp(c, -1f, 1f)) * Mathf.Rad2Deg;
        }

        private static List<int> PickHabitableRingSeeds(PlanetLayer layer, PlanetTile[] tileOf,
                                                        int count, int worldSeed)
        {
            // 🔴 TWO POOLS, NOT ONE. Spec test 4 items 1 and 2: two bodies in the
            // habitable ring, and the THIRD deliberately off-pattern — owner's
            // words, "one near the pole to make it feel really alien", which on a
            // tidally locked planet means a frozen sea out on the NIGHTSIDE.
            // Seeding all three in the ring would also walk straight into item 3,
            // "NOT A RING" — three ring bodies grown along one band read as a
            // diagram, which is the thing the owner explicitly rejected.
            List<int> ring = new List<int>();
            List<int> night = new List<int>();
            for (int i = 0; i < count; i++)
            {
                float arc = ArcFromSubsolar(layer, tileOf[i]);
                if (arc >= RingInnerDeg && arc <= RingOuterDeg)
                {
                    ring.Add(i);
                }
                else if (arc >= NightsideMinDeg)
                {
                    night.Add(i);
                }
            }
            if (ring.Count == 0)
            {
                // No tile in the habitable ring at all. Fall back to anything
                // rather than returning nothing and silently making no sea.
                for (int i = 0; i < count; i++)
                {
                    ring.Add(i);
                }
            }
            if (night.Count == 0)
            {
                // Nowhere cold enough to be off-pattern. Better a third ring body
                // than no third body — test 2 counts bodies, and an empty one
                // fails it outright.
                night = ring;
            }

            List<int> seeds = new List<int>(Bodies);
            Rand.PushState(worldSeed);
            try
            {
                for (int b = 0; b < Bodies; b++)
                {
                    // The last body is the off-pattern one; the rest ride the ring.
                    List<int> pool = (b == Bodies - 1) ? night : ring;
                    if (pool.Count == 0)
                    {
                        continue;
                    }
                    int best = -1;
                    float bestScore = float.NegativeInfinity;
                    // Sample rather than sort: pick the candidate furthest from
                    // the seeds already chosen, out of a bounded random draw.
                    // Bounded on purpose — no unbounded search anywhere here.
                    int draws = Mathf.Min(pool.Count, 256);
                    for (int d = 0; d < draws; d++)
                    {
                        int cand = pool[Rand.Range(0, pool.Count)];
                        float score = float.MaxValue;
                        for (int s = 0; s < seeds.Count; s++)
                        {
                            float dist = (layer.GetTileCenter(tileOf[cand])
                                          - layer.GetTileCenter(tileOf[seeds[s]])).sqrMagnitude;
                            if (dist < score)
                            {
                                score = dist;
                            }
                        }
                        if (score > bestScore)
                        {
                            bestScore = score;
                            best = cand;
                        }
                    }
                    if (best >= 0)
                    {
                        seeds.Add(best);
                    }
                }
            }
            finally
            {
                Rand.PopState();
            }
            return seeds;
        }

        // -------------------------------------------------------------------
        // Invasion percolation from one seed. Returns how many tiles it claimed.
        //
        // The frontier is scanned linearly for its best-scoring tile. That is
        // O(frontier) per claim rather than a heap's O(log n), and it is the
        // right trade here: the frontier of a ragged body stays small, the tile
        // budget is a few thousand, and a linear scan cannot go wrong the way a
        // hand-rolled priority queue can.
        // -------------------------------------------------------------------
        private static int GrowBody(int seedTile, int bodyId, int budget, PlanetLayer layer,
                                    PlanetTile[] tileOf, int[][] neighboursOf, int[] bodyOf,
                                    Perlin shape)
        {
            if (bodyOf[seedTile] > 0)
            {
                return 0;
            }

            List<int> frontier = new List<int>();
            bodyOf[seedTile] = bodyId;
            int claimed = 1;
            AddFrontier(seedTile, neighboursOf, bodyOf, frontier);

            // Hard iteration cap. The spec forbids unbounded loops; if the
            // frontier dies before the budget is met we stop and report.
            while (claimed < budget && frontier.Count > 0)
            {
                int bestAt = -1;
                float bestScore = float.NegativeInfinity;
                for (int f = 0; f < frontier.Count; f++)
                {
                    int cand = frontier[f];
                    if (bodyOf[cand] > 0)
                    {
                        continue;
                    }
                    Vector3 c = layer.GetTileCenter(tileOf[cand]);
                    float score = (float)shape.GetValue(c.x, c.y, c.z);
                    if (score > bestScore)
                    {
                        bestScore = score;
                        bestAt = f;
                    }
                }
                if (bestAt < 0)
                {
                    break;
                }

                int take = frontier[bestAt];
                frontier.RemoveAt(bestAt);
                bodyOf[take] = bodyId;
                claimed++;
                AddFrontier(take, neighboursOf, bodyOf, frontier);
            }
            return claimed;
        }

        private static void AddFrontier(int at, int[][] neighboursOf, int[] bodyOf,
                                        List<int> frontier)
        {
            int[] near = neighboursOf[at];
            for (int n = 0; n < near.Length; n++)
            {
                int to = near[n];
                if (bodyOf[to] <= 0 && !frontier.Contains(to))
                {
                    frontier.Add(to);
                }
            }
        }

        // -------------------------------------------------------------------
        // Flood-fill each body and keep only its largest connected component.
        // Everything else is released back to land — and it must be released
        // properly, so the caller has already written land biome and elevation
        // into every tile before any sea is claimed. Releasing here is therefore
        // just clearing the claim.
        // -------------------------------------------------------------------
        private static int KeepLargestComponentPerBody(int count, int[][] neighboursOf,
                                                       int[] bodyOf, int bodyCount)
        {
            int released = 0;
            bool[] visited = new bool[count];

            for (int b = 1; b <= bodyCount; b++)
            {
                List<List<int>> components = new List<List<int>>();
                for (int i = 0; i < count; i++)
                {
                    if (bodyOf[i] != b || visited[i])
                    {
                        continue;
                    }
                    List<int> comp = new List<int>();
                    Queue<int> queue = new Queue<int>();
                    queue.Enqueue(i);
                    visited[i] = true;
                    while (queue.Count > 0)
                    {
                        int at = queue.Dequeue();
                        comp.Add(at);
                        int[] near = neighboursOf[at];
                        for (int n = 0; n < near.Length; n++)
                        {
                            int to = near[n];
                            if (bodyOf[to] == b && !visited[to])
                            {
                                visited[to] = true;
                                queue.Enqueue(to);
                            }
                        }
                    }
                    components.Add(comp);
                }

                int keep = -1, keepSize = -1;
                for (int c = 0; c < components.Count; c++)
                {
                    if (components[c].Count > keepSize)
                    {
                        keepSize = components[c].Count;
                        keep = c;
                    }
                }
                for (int c = 0; c < components.Count; c++)
                {
                    if (c == keep)
                    {
                        continue;
                    }
                    for (int k = 0; k < components[c].Count; k++)
                    {
                        bodyOf[components[c][k]] = -1;
                        released++;
                    }
                }
            }
            return released;
        }

        // -------------------------------------------------------------------
        // Measure what was actually produced and log it against every acceptance
        // test, PASS or FAIL.
        //
        // Reported rather than enforced, deliberately: the step must not loop to
        // hit a number, and a world that misses by two points is still a world.
        // The log line is the acceptance evidence — the whole spec is decided by
        // reading it across three seeds.
        // -------------------------------------------------------------------
        /// <summary>
        /// Long axis over width, for one body. Bounded and O(n), deliberately:
        /// the exact diameter is an O(n^2) pairwise scan and a sea body can run
        /// to thousands of tiles.
        ///
        /// DOUBLE SWEEP, the standard graph-diameter approximation: from any
        /// member find the furthest member A, from A find the furthest member B.
        /// A-B is the long axis. Width is then twice the greatest perpendicular
        /// distance from that axis, in one more linear pass.
        ///
        /// ⚠️ This APPROXIMATES the diameter — a double sweep can under-report on
        /// a pathological shape. It is a diagnostic gate, not a proof, and it
        /// errs toward reporting a body as rounder than it is, which is the safe
        /// direction for a floor.
        /// </summary>
        private static float AspectRatio(int b, int[] bodyOf, int count,
                                         PlanetLayer layer, PlanetTile[] tileOf)
        {
            int first = -1;
            for (int i = 0; i < count && first < 0; i++)
            {
                if (bodyOf[i] == b)
                {
                    first = i;
                }
            }
            if (first < 0)
            {
                return 0f;
            }

            int a = FurthestFrom(first, b, bodyOf, count, layer, tileOf);
            int c = FurthestFrom(a, b, bodyOf, count, layer, tileOf);

            Vector3 pa = layer.GetTileCenter(tileOf[a]);
            Vector3 pc = layer.GetTileCenter(tileOf[c]);
            Vector3 axis = pc - pa;
            float length = axis.magnitude;
            if (length <= 0.0001f)
            {
                // One tile, or all members coincident. Not elongated, and not a
                // divide-by-zero either.
                return 0f;
            }
            Vector3 unit = axis / length;

            float maxPerp = 0f;
            for (int i = 0; i < count; i++)
            {
                if (bodyOf[i] != b)
                {
                    continue;
                }
                Vector3 d = layer.GetTileCenter(tileOf[i]) - pa;
                float perp = (d - unit * Vector3.Dot(d, unit)).magnitude;
                if (perp > maxPerp)
                {
                    maxPerp = perp;
                }
            }

            // Width is the full span across the axis, not the half-span.
            float width = maxPerp * 2f;
            return width <= 0.0001f ? 999f : length / width;
        }

        private static int FurthestFrom(int from, int b, int[] bodyOf, int count,
                                        PlanetLayer layer, PlanetTile[] tileOf)
        {
            Vector3 origin = layer.GetTileCenter(tileOf[from]);
            int best = from;
            float bestSq = -1f;
            for (int i = 0; i < count; i++)
            {
                if (bodyOf[i] != b)
                {
                    continue;
                }
                float sq = (layer.GetTileCenter(tileOf[i]) - origin).sqrMagnitude;
                if (sq > bestSq)
                {
                    bestSq = sq;
                    best = i;
                }
            }
            return best;
        }

        private static void Report(int count, int originalWater, int claimed, int quota,
                                   int[] bodyOf, int[][] neighboursOf, PlanetLayer layer,
                                   PlanetTile[] tileOf, int bodyCount, int orphans)
        {
            float fraction = count > 0 ? (float)claimed / count : 0f;
            string verdict = fraction >= 0.22f && fraction <= 0.28f ? "PASS" : "FAIL";

            System.Text.StringBuilder sb = new System.Text.StringBuilder();
            sb.AppendFormat(
                "[JawaSea] water {0:P1} of {1} tiles ({2} claimed, quota {3}) — test 1 {4}. "
                + "Vanilla had made {5:P1}. {6} orphan tile(s) released.",
                fraction, count, claimed, quota, verdict,
                count > 0 ? (float)originalWater / count : 0f, orphans);

            int live = 0;
            for (int b = 1; b <= bodyCount; b++)
            {
                int area = 0, perimeter = 0;
                float arcSum = 0f;
                for (int i = 0; i < count; i++)
                {
                    if (bodyOf[i] != b)
                    {
                        continue;
                    }
                    area++;
                    arcSum += ArcFromSubsolar(layer, tileOf[i]);
                    int[] near = neighboursOf[i];
                    for (int n = 0; n < near.Length; n++)
                    {
                        if (bodyOf[near[n]] != b)
                        {
                            perimeter++;
                            break;
                        }
                    }
                }
                if (area <= 0)
                {
                    sb.AppendFormat(" | body {0}: EMPTY — shortfall, not grown", b);
                    continue;
                }
                live++;
                // Perimeter squared over area. A circle is 4*pi = 12.57; the spec
                // wants at least 25, i.e. twice as ragged as a circle.
                float compactness = (float)perimeter * perimeter / area;
                float aspect = AspectRatio(b, bodyOf, count, layer, tileOf);
                sb.AppendFormat(" | body {0}: {1} tiles, perimeter {2}, compactness {3:F1} ({4}), "
                              + "aspect {5:F1} ({6}), mean arc {7:F0} deg",
                    b, area, perimeter, compactness,
                    compactness >= MinCompactness ? "PASS" : "FAIL — too round",
                    aspect,
                    aspect >= MinAspect ? "PASS" : "FAIL — too round, not elongated",
                    arcSum / area);
            }

            sb.AppendFormat(" | bodies {0}/{1} — test 2 {2}",
                live, Bodies, live == Bodies ? "PASS" : "FAIL");

            Log.Message(sb.ToString());
        }
    }
}
