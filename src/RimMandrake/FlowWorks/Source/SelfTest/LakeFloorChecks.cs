// LAKE_FLOORS_BUILD_MOUNTAINS_RUN_DEEP (plan P11; owner R10 + R11, 2026-10-17). The arithmetic is the PRODUCTION
// RM_LakeFloorMath / RM_LevelSolve / RM_PondDepthMath / RM_PocketGridMath; the Verse-bound wiring (RM_LiquidStock,
// RM_MapComponent_Excavation, settings) is read from production source.
// R11, verbatim: "Vary it. Some lakes will be shallow and silted up. Others will be deep and chasm-like. Depends on the biome.
// The more mountainous, the deeper in general. The more plains-like, the smoother/shallower. They should also have some
// variation down there, not just a radial crater."
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class LakeFloorChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        /// <summary>A lake of irregular outline (radius wobbling with the angle), with a two-square shallow fringe the way the
        /// map generator leaves one: deep water from three squares in. Deterministic in (seed).</summary>
        internal static (List<int> fp, HashSet<int> deep) Synthetic(int w, int h, int cx, int cz, double r0, int seed, double wobble = 0.28)
        {
            var fp = new List<int>();
            uint k = (uint)seed * 2654435761u;
            for (int z = 0; z < h; z++)
                for (int x = 0; x < w; x++)
                {
                    double dx = x - cx, dz = z - cz, a = Math.Atan2(dz, dx);
                    double rr = r0 * (1 + wobble * RM_LakeFloorMath.Fbm(k, 1.6 * Math.Cos(a) + 3, 1.6 * Math.Sin(a) + 3));
                    if (dx * dx + dz * dz <= rr * rr) fp.Add(z * w + x);
                }
            var set = new HashSet<int>(fp);
            var dist = new Dictionary<int, int>();
            var q = new Queue<int>();
            foreach (int i in fp)
            {
                int x = i % w, z = i / w;
                if (x == 0 || z == 0 || x == w - 1 || z == h - 1 || !set.Contains(i - 1) || !set.Contains(i + 1) || !set.Contains(i - w) || !set.Contains(i + w))
                { dist[i] = 1; q.Enqueue(i); }
            }
            while (q.Count > 0)
            {
                int c = q.Dequeue();
                foreach (int n in new[] { c - 1, c + 1, c - w, c + w })
                    if (set.Contains(n) && !dist.ContainsKey(n)) { dist[n] = dist[c] + 1; q.Enqueue(n); }
            }
            var deep = new HashSet<int>(fp.Where(i => dist[i] >= 3));
            return (fp, deep);
        }

        internal static int[] Floor(int w, int h, List<int> fp, HashSet<int> deep, RM_LakeFloorMath.Params p, out RM_LakeFloorMath.Traits tr)
        {
            int[] f = new int[fp.Count];
            tr = RM_LakeFloorMath.Floor(w, h, fp, i => deep.Contains(i), p, f);
            return f;
        }

        // hilliness byte -> its band's name, for messages
        private static readonly int[] Hills = { 1, 2, 3, 4, 5 };
        private static readonly string[] HillNames = { "Flat", "SmallHills", "LargeHills", "Mountainous", "Impassable" };

        /// <summary>Can a creature that climbs <paramref name="k"/> notches reach the water's edge from land, the lake drawn
        /// down to <paramref name="surface"/> (dL per square, ≤ 0)? Dry squares are walked at their floor; land is 0.</summary>
        private static bool EdgeReachable(int w, int h, List<int> fp, int[] f, double surface, int k)
        {
            var slot = new Dictionary<int, int>();
            for (int i = 0; i < fp.Count; i++) slot[fp[i]] = i;
            bool Wet(int s) => RM_LevelSolve.PondSquareWater(f[s], surface) >= 0.5;
            if (!Enumerable.Range(0, fp.Count).Any(Wet)) return true;   // nothing left to reach
            var seen = new HashSet<int>();
            var q = new Queue<int>();
            int[] dx = { 1, -1, 0, 0 }, dz = { 0, 0, 1, -1 };
            for (int s = 0; s < fp.Count; s++)
            {
                int x = fp[s] % w, z = fp[s] / w;
                for (int d = 0; d < 4; d++)
                {
                    int X = x + dx[d], Z = z + dz[d];
                    if (X < 0 || Z < 0 || X >= w || Z >= h || slot.ContainsKey(Z * w + X)) continue;
                    if (Wet(s)) return true;                                  // the water touches the land
                    if (f[s] <= k && seen.Add(s)) q.Enqueue(s);
                }
            }
            while (q.Count > 0)
            {
                int s = q.Dequeue();
                int x = fp[s] % w, z = fp[s] / w;
                for (int d = 0; d < 4; d++)
                {
                    int X = x + dx[d], Z = z + dz[d];
                    if (X < 0 || Z < 0 || X >= w || Z >= h || !slot.TryGetValue(Z * w + X, out int m)) continue;
                    if (Wet(m)) return true;                                  // a dry floor square beside the water
                    if (!seen.Contains(m) && Math.Abs(f[m] - f[s]) <= k) { seen.Add(m); q.Enqueue(m); }
                }
            }
            return false;
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("Lake_floor_same_seed_same_floor_any_order", () =>
            {
                int w = 140, h = 140;
                var (fp, deep) = Synthetic(w, h, 70, 70, 50, 4);
                var p = RM_LakeFloorMath.Params.Defaults(123456, 0.8f);
                int[] a = Floor(w, h, fp, deep, p, out var ta);
                int[] b = Floor(w, h, fp, deep, p, out _);
                Assert(a.SequenceEqual(b), "same seed, same lake: the same floor (a reload never re-rolls)");
                // the footprint in another order (another seed square, another walk): every square keeps its floor
                var shuffled = fp.OrderBy(i => (i * 7919) % 104729).ToList();
                int[] c = Floor(w, h, shuffled, deep, p, out _);
                var byCell = new Dictionary<int, int>();
                for (int k = 0; k < fp.Count; k++) byCell[fp[k]] = a[k];
                for (int k = 0; k < shuffled.Count; k++) Assert(byCell[shuffled[k]] == c[k], "walk order never changes a floor: square " + shuffled[k]);
                p.seed = 654321;
                int[] d = Floor(w, h, fp, deep, p, out _);
                Assert(!a.SequenceEqual(d), "another map's seed: another floor");
                Assert(RM_LakeFloorMath.LakeKey(fp) == fp.Min() && RM_LakeFloorMath.LakeKey(shuffled) == fp.Min(), "the key is the lowest square");
                Assert(ta.deepestNotches > RM_LakeFloorMath.DeepNotches, "a 100-wide mountain lake is deeper than 2 m");
            });

            Case("Lake_floors_deepen_with_roughness_50m_only_in_mountains", () =>
            {
                // N seeded lakes per hilliness class (Flat .. Impassable), sizes from a pond to a 140-wide lake. Mean and max
                // deepest floor rise from flat to mountainous; no floor passes the ceiling; 50 m only in mountains / chasm.
                int w = 170, h = 170;
                var rows = new List<string>();
                double prevMean = -1, prevMax = -1;
                for (int hc = 0; hc < Hills.Length; hc++)
                {
                    float r = RM_LakeFloorMath.Roughness(Hills[hc], null);
                    var deepest = new List<int>();
                    int silted = 0;
                    for (int t = 0; t < 40; t++)
                    {
                        double r0 = 8 + (t % 8) * 9;   // 8 .. 71 squares radius
                        var (fp, deep) = Synthetic(w, h, 85, 85, r0, 100 + t);
                        int[] f = Floor(w, h, fp, deep, RM_LakeFloorMath.Params.Defaults(9000 + t * 31, r), out var tr);
                        Assert(f.Max() <= RM_LakeFloorMath.DefaultCeilingNotches, "never past the ceiling");
                        deepest.Add(f.Max());
                        if (tr.silted) silted++;
                    }
                    double mean = deepest.Average(); int max = deepest.Max();
                    rows.Add(HillNames[hc] + " r " + r.ToString("F2") + ": mean deepest " + (mean / 2).ToString("F1") + " m, max " + (max / 2.0).ToString("F1") + " m, silted " + silted + "/40");
                    Assert(mean > prevMean, HillNames[hc] + ": mean deepest rises with roughness (" + mean + " after " + prevMean + ")");
                    Assert(max >= prevMax, HillNames[hc] + ": max deepest does not fall with roughness (" + max + " after " + prevMax + ")");
                    if (Hills[hc] <= 3) Assert(max < 100, HillNames[hc] + ": 50 m is for mountains only, got " + max / 2.0 + " m");
                    prevMean = mean; prevMax = max;
                }
                Console.WriteLine("  LakeFloor table: " + string.Join(" | ", rows));
                // a very large lake in chasm country reaches the 50 m bound (with the way out on)
                int W = 250;
                var (bfp, bdeep) = Synthetic(W, W, 125, 125, 115, 77, 0.08);
                int best = 0;
                for (int s = 0; s < 30; s++) best = Math.Max(best, Floor(W, W, bfp, bdeep, RM_LakeFloorMath.Params.Defaults(31 * s + 5, 0.95f), out _).Max());
                Console.WriteLine("  LakeFloor: a 230-wide chasm-country lake, deepest of 30 draws " + best / 2.0 + " m");
                Assert(best >= 90, "a 230-wide chasm-country lake can run to about 50 m: best of 30 " + best / 2.0 + " m");
                // the ceiling setting caps, and the depth scale lifts the band (still under the ceiling)
                var pc = RM_LakeFloorMath.Params.Defaults(5, 0.95f); pc.ceilingNotches = 30;
                Assert(Floor(W, W, bfp, bdeep, pc, out _).Max() <= 30, "the ceiling setting caps every floor");
                var pd = RM_LakeFloorMath.Params.Defaults(5, 0.95f); pd.depthScale = 2.5f; pd.ceilingNotches = 250;
                Assert(Floor(W, W, bfp, bdeep, pd, out _).Max() > 100, "depth x2.5 and a 125 m ceiling go past 50 m");
            });

            Case("Lake_floors_vary_lake_to_lake_silted_and_deep", () =>
            {
                int w = 120, h = 120;
                var (fp, deep) = Synthetic(w, h, 60, 60, 40, 9);
                var plains = new List<RM_LakeFloorMath.Traits>();
                var mountain = new List<int>();
                for (int s = 0; s < 60; s++)
                {
                    Floor(w, h, fp, deep, RM_LakeFloorMath.Params.Defaults(s * 101 + 1, RM_LakeFloorMath.Roughness(1, null)), out var tr);
                    plains.Add(tr);
                    mountain.Add(Floor(w, h, fp, deep, RM_LakeFloorMath.Params.Defaults(s * 101 + 1, RM_LakeFloorMath.Roughness(4, null)), out _).Max());
                }
                int silted = plains.Count(t => t.silted);
                Assert(silted >= 15 && silted <= 40, "plains: about 45% of lakes silted up, got " + silted + "/60");
                Assert(plains.Where(t => t.silted).All(t => t.deepestNotches <= 5), "a silted lake is at most 2.5 m");
                Assert(plains.Max(t => t.deepestNotches) >= 8, "and some plains lakes are still 4 m or more");
                Assert(mountain.Max() - mountain.Min() >= 20, "one mountain lake shape differs lake to lake by 10 m or more: " + mountain.Min() / 2.0 + " .. " + mountain.Max() / 2.0);
                // the biome moves it: a swamp is shallower than its hilliness alone, a canyon deeper
                Assert(RM_LakeFloorMath.Roughness(3, "TemperateSwamp") < RM_LakeFloorMath.Roughness(3, null)
                    && RM_LakeFloorMath.Roughness(3, "RM_FloodedCanyon") > RM_LakeFloorMath.Roughness(3, null)
                    && RM_LakeFloorMath.Roughness(4, "RUT_TheScald") <= 1f, "biome bias, clamped");
            });

            Case("Lake_floors_are_irregular_not_a_radial_crater", () =>
            {
                // the verify row: a floor is not a function of distance to shore alone. Measured: the fraction of deep squares
                // at least 1 m off the mean floor of their distance ring. The stated floors: >= 0.20 averaged over lakes 6 m or
                // deeper, and > 0 for every one of them; the control (the retired radial slope) is exactly 0.
                int w = 150, h = 150;
                var offs = new List<double>();
                for (int s = 0; s < 30; s++)
                {
                    var (fp, deep) = Synthetic(w, h, 75, 75, 25 + (s % 5) * 10, 200 + s);
                    float r = 0.3f + 0.65f * (s % 3) / 2f;
                    int[] f = Floor(w, h, fp, deep, RM_LakeFloorMath.Params.Defaults(s * 977 + 3, r), out var tr);
                    double off = RM_LakeFloorMath.OffRadial(w, h, fp, i => deep.Contains(i), f, 2);
                    if (tr.deepestNotches >= 12) Assert(off > 0, "seed " + s + ": a " + tr.deepestNotches / 2.0 + " m floor is not radial");
                    if (tr.deepestNotches >= 12) offs.Add(off);
                }
                Assert(offs.Count >= 8, "enough deep lakes in the sample: " + offs.Count);
                double mean = offs.Average();
                Console.WriteLine("  LakeFloor irregularity: " + offs.Count + " lakes >= 6 m, mean fraction >= 1 m off-radial " + mean.ToString("F2"));
                Assert(mean >= 0.20, "irregular down there: mean off-radial fraction " + mean.ToString("F2"));
                // control: the radial slope (a function of shore distance) scores 0
                var (cfp, cdeep) = Synthetic(w, h, 75, 75, 45, 1);
                int[] radial = new int[cfp.Count];
                var dist = ShoreDist(w, h, cfp);
                for (int k = 0; k < cfp.Count; k++) radial[k] = Math.Min(40, 4 + dist[k] / 2);
                Assert(RM_LakeFloorMath.OffRadial(w, h, cfp, i => cdeep.Contains(i), radial, 2) == 0.0, "control: a radial crater scores 0");
            });

            Case("Lake_floor_full_lake_is_unchanged_on_screen_and_holds_its_floor", () =>
            {
                // R10: a full lake: one surface at the brim, every square's water = its floor, every square's picture Original.
                // Volume: the body holds Σ floor notches (a notch = 1,000 L in a square); the engine's surface reads it back.
                int w = 120, h = 120;
                var (fp, deep) = Synthetic(w, h, 60, 60, 45, 12);
                int[] f = Floor(w, h, fp, deep, RM_LakeFloorMath.Params.Defaults(42, 0.8f), out var tr);
                int[] hist = RM_PondDepthMath.Histogram(f.ToList());
                long full = f.Sum(x => (long)x) * RM_LevelSolve.U;
                Assert(tr.sumNotches * RM_LevelSolve.U == full, "the traits' sum is the floor's");
                double surf = RM_LevelSolve.PondSurfaceHeight(hist, full);
                Assert(Math.Abs(surf) < 1e-9, "full: the surface is the brim, got " + surf);
                for (int k = 0; k < f.Length; k++)
                {
                    double wd = RM_LevelSolve.PondSquareWater(f[k], surf);
                    Assert(Math.Abs(wd - f[k] * (double)RM_LevelSolve.U) < 1e-6, "full: water = floor");
                    Assert(RM_PondDepthMath.StageForExact(wd, f[k]) == RM_PondDepthMath.Stage.Original, "full: the square keeps its own terrain (R10)");
                }
                // one basin: from the deepest square every square is reached without the floor getting deeper on the way, so a
                // drawn-down lake never splits into pools behind an inner sill (the solver's one pond node is exact)
                Assert(OneBasin(w, h, fp, f), "one basin");
                foreach (float rr in new[] { 0.05f, 0.55f, 0.95f })
                    for (int s2 = 0; s2 < 6; s2++)
                    {
                        var (bfp, bd) = Synthetic(w, h, 60, 60, 25 + s2 * 6, 40 + s2);
                        foreach (int wo in new[] { 0, 1, 2 })
                        {
                            var pp = RM_LakeFloorMath.Params.Defaults(s2 * 37 + 1, rr); pp.wayOutNotches = wo;
                            Assert(OneBasin(w, h, bfp, Floor(w, h, bfp, bd, pp, out _)), "one basin, r " + rr + " lake " + s2 + " way out " + wo);
                        }
                    }
                // drained to 40%: one surface; the water summed over squares is the stock; dry squares are exactly the shallow ones
                long stock = (long)(full * 0.4);
                surf = RM_LevelSolve.PondSurfaceHeight(hist, stock);
                double sum = 0; int dryDeepest = 0, wetShallowest = int.MaxValue;
                for (int k = 0; k < f.Length; k++)
                {
                    double wd = RM_LevelSolve.PondSquareWater(f[k], surf);
                    sum += wd;
                    if (wd <= 0) dryDeepest = Math.Max(dryDeepest, f[k]); else wetShallowest = Math.Min(wetShallowest, f[k]);
                }
                Assert(Math.Abs(sum - stock) < 1.0 + f.Length * 1e-6, "40%: the water standing on the floor is the stock (" + sum + " vs " + stock + ")");
                Assert(dryDeepest < wetShallowest, "40%: dry squares are the shallow floors, wet ones the deep (one surface)");
            });

            Case("Lake_floor_drained_lake_keeps_the_water_in_reach", () =>
            {
                // the play review's stranding: drawn down step by step, the water's edge stays reachable from land for a person
                // (defaults: no shelf since 2026-10-18, way out 1 m), and for small animals with the way out at 0.5 m. Without the shelf and the
                // way out a chasm lake strands both (the control).
                int w = 130, h = 130;
                foreach (float r in new[] { 0.05f, 0.55f, 0.95f })
                    for (int s = 0; s < 4; s++)
                    {
                        var (fp, deep) = Synthetic(w, h, 65, 65, 30 + s * 8, 300 + s);
                        var pd = RM_LakeFloorMath.Params.Defaults(s * 13 + 7, r);
                        var ps = pd; ps.wayOutNotches = 1;
                        int[] fd = Floor(w, h, fp, deep, pd, out _), fs = Floor(w, h, fp, deep, ps, out _);
                        foreach (var (f, k, who) in new[] { (fd, 2, "person, defaults"), (fs, 1, "small animal, way out 0.5 m") })
                        {
                            int[] hist = RM_PondDepthMath.Histogram(f.ToList());
                            long full = f.Sum(x => (long)x) * RM_LevelSolve.U;
                            for (int step = 1; step < 20; step++)
                            {
                                double surf = RM_LevelSolve.PondSurfaceHeight(hist, full * (20 - step) / 20);
                                Assert(EdgeReachable(w, h, fp, f, surf, k), who + ", r " + r + " lake " + s + ", " + (step * 5) + "% drawn: the water is out of reach");
                            }
                        }
                    }
                var (cfp, cdeep) = Synthetic(w, h, 65, 65, 40, 5);
                var p0 = RM_LakeFloorMath.Params.Defaults(9, 0.95f); p0.wayOutNotches = 0; p0.shelfNotches = 0;
                int[] f0 = Floor(w, h, cfp, cdeep, p0, out _);
                int[] h0 = RM_PondDepthMath.Histogram(f0.ToList());
                long full0 = f0.Sum(x => (long)x) * RM_LevelSolve.U;
                bool stranded = false;
                for (int step = 1; step < 20 && !stranded; step++)
                    stranded = !EdgeReachable(w, h, cfp, f0, RM_LevelSolve.PondSurfaceHeight(h0, full0 * (20 - step) / 20), 1);
                Assert(stranded, "control: a chasm lake with no shelf and no way out strands small animals once drawn down");
                // the shelf: OFF by default (owner 2026-10-18, BEACH_RING_RETIRE_DRAINED_MEANS_DRY: drained means dry); switched on
                // at 0.5 m the outer ring is 0.5 m; off, the shore keeps 1 m (shallow) / 2 m (deep)
                Assert(RM_LakeFloorMath.DefaultShelfNotches == 0 && RM_LakeFloorMath.Params.Defaults(9, 0.95f).shelfNotches == 0, "no beach ring by default");
                Floor(w, h, cfp, cdeep, RM_LakeFloorMath.Params.Defaults(9, 0.95f), out var tnone);
                Assert(tnone.shelfSquares == 0, "defaults: the shelf moves no square");
                var dist = ShoreDist(w, h, cfp);
                var pon = RM_LakeFloorMath.Params.Defaults(9, 0.95f); pon.shelfNotches = 1;
                int[] fdef = Floor(w, h, cfp, cdeep, pon, out var tdef);
                for (int k = 0; k < cfp.Count; k++)
                    if (dist[k] == 1) Assert(fdef[k] == 1, "shelf on: the outer ring is 0.5 m");
                Assert(tdef.shelfSquares > 0, "the shelf moved the ring");
                for (int k = 0; k < cfp.Count; k++)
                    if (dist[k] == 1) Assert(f0[k] == (cdeep.Contains(cfp[k]) ? 4 : 2) || f0[k] >= 4, "shelf off: the shore is the terrain's 1 m or the floor below 2 m");
            });

            Case("Lake_floor_wiring_formation_settings_and_save", () =>
            {
                string st = RiverSwitchFlipChecks.Src("RM_LiquidStock.cs");
                RiverSwitchFlipChecks.Has(st, @"RM_LakeFloorMath\.Traits tr = RM_LakeFloorMath\.Floor\(map\.Size\.x, map\.Size\.z, footprint,", "formation runs the generator");
                RiverSwitchFlipChecks.Has(st, @"owner\.RecordBedDepth\(footprint\[k\], floor\[k\]\);", "every footprint square's floor is recorded");
                string rec = Between(st, "private static void RecordLakeFloor(", "private static bool AnyMovingWater(");
                string all = Between(st, "public int FormAllBodies(", "/// <summary>Σ bed levels");
                Assert(!rec.Contains("SetTerrain") && !all.Contains("SetTerrain") && !rec.Contains("StageNaturalCell"), "R10: forming lakes writes no terrain");
                RiverSwitchFlipChecks.Has(st, @"if \(owner\.IsSourceCell\(c\)\) \{ BodyAt\(map, c, owner\); \}", "every natural square is formed through BodyAt (an indexed square keeps its body and floor)");
                string ex = RiverSwitchFlipChecks.Src("RM_MapComponent_Excavation.cs");
                RiverSwitchFlipChecks.Has(ex, @"Scribe_Values\.Look\(ref lakeFloorsFormed, ""RM_lakeFloorsFormed"", false\);", "the formed flag is saved (an old save loads false: formed once)");
                RiverSwitchFlipChecks.Has(ex, @"if \(!lakeFloorsFormed\) \{ int formed = stock\.FormAllBodies\(map, this\); lakeFloorsFormed = true;", "FinalizeInit forms every lake once");
                Assert(ex.IndexOf("stock.FormAllBodies(map, this)") > ex.IndexOf("stock.RebuildIndex(map);"), "after the saved bodies are indexed (a formed lake is never re-formed)");
                RiverSwitchFlipChecks.Has(ex, @"int seed = Gen\.HashCombineInt\(Find\.World\?\.info\?\.persistentRandomValue \?\? 0, map\.ConstantRandSeed\);", "the seed is saved state (world + map), not the clock");
                RiverSwitchFlipChecks.Has(ex, @"hill = \(int\)map\.TileInfo\.HillinessForElevationGen;", "roughness reads the hilliness the map was generated with");
                string set = RiverSwitchFlipChecks.Src("RimMandrakeFlowWorksMod.cs");
                RiverSwitchFlipChecks.Has(set, @"public static int LakeShoreShelfNotches => Mathf\.Clamp\(Mathf\.RoundToInt\(lakeShoreShelfMetres \* 2f\), 0, 4\);", "shelf in metres");
                RiverSwitchFlipChecks.Has(set, @"public static int LakeWayOutNotches => Mathf\.Clamp\(Mathf\.RoundToInt\(lakeWayOutMetres \* 2f\), 0, 8\);", "way out in metres");
                Assert(!set.Contains("deepBedCellsPerLevel") && !RiverSwitchFlipChecks.Src("RM_BedMath.cs").Contains("DeepBedLevels"), "the radial slope is gone (R11)");
                Assert(RM_LakeFloorMath.DefaultCeilingNotches == 100 && RM_BedMath.DefaultMaxBedDepth == 100 && RM_BedMath.MaxBedCeiling == 250, "default ceiling 50 m, settable to 125 m");
            });

            Case("Lake_floor_bench_offline", () =>
            {
                int w = 250, h = 250;
                var (fp, deep) = Synthetic(w, h, 125, 125, 110, 3, 0.08);
                var sw = Stopwatch.StartNew();
                int[] f = Floor(w, h, fp, deep, RM_LakeFloorMath.Params.Defaults(1, 0.95f), out var tr);
                double ms = sw.Elapsed.TotalMilliseconds;
                Console.WriteLine("  LakeFloor bench: " + fp.Count + " squares, deepest " + tr.deepestNotches / 2.0 + " m, way out moved " + tr.wayOutRaised + ", " + ms.ToString("F0") + " ms (once per lake, at map creation)");
                Assert(ms < 4000, "generous ceiling so a loaded host does not flake");
            });
        }

        /// <summary>Every square reachable from the deepest by N/S/E/W steps that never go deeper than the step before.</summary>
        internal static bool OneBasin(int w, int h, List<int> fp, int[] f)
        {
            var slot = new Dictionary<int, int>();
            int start = 0;
            for (int i = 0; i < fp.Count; i++) { slot[fp[i]] = i; if (f[i] > f[start]) start = i; }
            var seen = new bool[fp.Count];
            var q = new Queue<int>();
            seen[start] = true; q.Enqueue(start);
            int[] dx = { 1, -1, 0, 0 }, dz = { 0, 0, 1, -1 };
            int count = 1;
            while (q.Count > 0)
            {
                int s = q.Dequeue(), x = fp[s] % w, z = fp[s] / w;
                for (int d = 0; d < 4; d++)
                {
                    int X = x + dx[d], Z = z + dz[d];
                    if (X < 0 || Z < 0 || X >= w || Z >= h || !slot.TryGetValue(Z * w + X, out int m) || seen[m] || f[m] > f[s]) continue;
                    seen[m] = true; count++; q.Enqueue(m);
                }
            }
            return count == fp.Count;
        }

        private static string Between(string s, string a, string b)
        {
            int i = s.IndexOf(a, StringComparison.Ordinal);
            int j = i < 0 ? -1 : s.IndexOf(b, i, StringComparison.Ordinal);
            if (i < 0 || j < 0) throw new Exception("source anchor missing: " + a);
            return s.Substring(i, j - i);
        }

        internal static int[] ShoreDist(int w, int h, List<int> fp)
        {
            var slot = new Dictionary<int, int>();
            for (int i = 0; i < fp.Count; i++) slot[fp[i]] = i;
            int[] dist = new int[fp.Count];
            var q = new Queue<int>();
            int[] dx = { 1, -1, 0, 0 }, dz = { 0, 0, 1, -1 };
            for (int s = 0; s < fp.Count; s++)
            {
                int x = fp[s] % w, z = fp[s] / w;
                for (int d = 0; d < 4; d++)
                {
                    int X = x + dx[d], Z = z + dz[d];
                    if (X < 0 || Z < 0 || X >= w || Z >= h || !slot.ContainsKey(Z * w + X)) { dist[s] = 1; q.Enqueue(s); break; }
                }
            }
            while (q.Count > 0)
            {
                int s = q.Dequeue();
                int x = fp[s] % w, z = fp[s] / w;
                for (int d = 0; d < 4; d++)
                {
                    int X = x + dx[d], Z = z + dz[d];
                    if (X < 0 || Z < 0 || X >= w || Z >= h || !slot.TryGetValue(Z * w + X, out int m) || dist[m] != 0) continue;
                    dist[m] = dist[s] + 1; q.Enqueue(m);
                }
            }
            return dist;
        }

        /// <summary>The preview tool's data (Transient/fw_scenes/lake_floors/, rendered by lake_floor_preview.py): eight lakes
        /// on synthetic maps across plains, hills and mountains, floors from the PRODUCTION generator at shipped defaults.</summary>
        public static int Preview(string outPath)
        {
            // want: "silted" / "open" / "any". Each lake starts at its own fixed seed and takes the FIRST draw of the wanted kind
            // (the draws skipped are counted and shown), so every kind appears once; the table gives the real odds.
            var specs = new (string title, int hill, string biome, double r0, int shapeSeed, int seed, double wobble, string want)[]
            {
                ("Plains pond (Flat, grassland)", 1, "Grasslands", 14, 11, 101, 0.30, "any"),
                ("Plains lake, silted up (Flat)", 1, null, 30, 12, 102, 0.25, "silted"),
                ("Plains lake, open (Flat, swamp)", 1, "TemperateSwamp", 34, 13, 103, 0.30, "open"),
                ("Low hills lake (SmallHills)", 2, null, 32, 14, 104, 0.30, "open"),
                ("Hills lake (LargeHills)", 3, null, 36, 15, 105, 0.28, "open"),
                ("Hills lake (LargeHills, canyon country)", 3, "RM_FloodedCanyon", 38, 16, 106, 0.32, "open"),
                ("Mountain lake (Mountainous)", 4, null, 40, 17, 107, 0.25, "open"),
                ("Chasm lake (Impassable)", 5, null, 46, 18, 108, 0.22, "open"),
            };
            var sb = new StringBuilder();
            sb.Append("{\"lakes\":[");
            var ci = CultureInfo.InvariantCulture;
            for (int n = 0; n < specs.Length; n++)
            {
                var sp = specs[n];
                int w = 110, h = 110;
                var (fp, deep) = Synthetic(w, h, 55, 55, sp.r0, sp.shapeSeed, sp.wobble);
                float r = RM_LakeFloorMath.Roughness(sp.hill, sp.biome);
                // the seed sweep picks a typical draw, not a hand-picked one: the first seed of a fixed list (no cherry-picking)
                var p = RM_LakeFloorMath.Params.Defaults(sp.seed * 7717, r);
                int[] f = Floor(w, h, fp, deep, p, out var tr);
                int skipped = 0;
                while (sp.want != "any" && tr.silted != (sp.want == "silted") && skipped < 200)
                {
                    skipped++;
                    p.seed = (sp.seed + skipped * 1000) * 7717;
                    f = Floor(w, h, fp, deep, p, out tr);
                }
                var p0 = p; p0.wayOutNotches = 0;
                int[] raw = Floor(w, h, fp, deep, p0, out _);
                double off = RM_LakeFloorMath.OffRadial(w, h, fp, i => deep.Contains(i), f, 2);
                if (n > 0) sb.Append(',');
                sb.Append("{\"title\":\"").Append(sp.title).Append("\",\"hilliness\":").Append(sp.hill)
                  .Append(",\"biome\":").Append(sp.biome == null ? "null" : "\"" + sp.biome + "\"")
                  .Append(",\"roughness\":").Append(r.ToString("F3", ci))
                  .Append(",\"band\":\"").Append(tr.band).Append("\",\"silted\":").Append(tr.silted ? "true" : "false")
                  .Append(",\"siltCap\":").Append(tr.siltCap.ToString("F2", ci)).Append(",\"terraces\":").Append(tr.terraces)
                  .Append(",\"target\":").Append(tr.targetDeepestM.ToString("F2", ci)).Append(",\"inradius\":").Append(tr.inradius)
                  .Append(",\"wayOutMoved\":").Append(tr.wayOutRaised).Append(",\"basinFilled\":").Append(tr.basinFilled).Append(",\"skipped\":").Append(skipped).Append(",\"want\":\"").Append(sp.want).Append("\"").Append(",\"offRadial\":").Append(off.ToString("F3", ci))
                  .Append(",\"w\":").Append(w).Append(",\"h\":").Append(h)
                  .Append(",\"cells\":[").Append(string.Join(",", fp)).Append("]")
                  .Append(",\"deep\":[").Append(string.Join(",", fp.Select(i => deep.Contains(i) ? 1 : 0))).Append("]")
                  .Append(",\"floor\":[").Append(string.Join(",", f)).Append("]")
                  .Append(",\"floorNoWayOut\":[").Append(string.Join(",", raw)).Append("]}");
            }
            sb.Append("],\"bands\":[");
            for (int b = 0; b < RM_LakeFloorMath.Bands.Length; b++)
            {
                var bd = RM_LakeFloorMath.Bands[b];
                if (b > 0) sb.Append(',');
                sb.Append("{\"name\":\"").Append(bd.name).Append("\",\"r\":").Append(bd.r.ToString("F2", ci))
                  .Append(",\"low\":").Append(bd.lowM.ToString("F1", ci)).Append(",\"high\":").Append(bd.highM.ToString("F1", ci))
                  .Append(",\"cap\":").Append(bd.capM.ToString("F1", ci)).Append(",\"silt\":").Append(bd.siltChance.ToString("F2", ci))
                  .Append(",\"siltFlat\":").Append(bd.siltFlatChance.ToString("F2", ci)).Append(",\"wall\":").Append(bd.wallWidth.ToString("F2", ci))
                  .Append(",\"terrace\":").Append(bd.terraceChance.ToString("F2", ci)).Append('}');
            }
            sb.Append("]}");
            File.WriteAllText(outPath, sb.ToString());
            Console.WriteLine("wrote " + outPath);
            return 0;
        }
    }
}
