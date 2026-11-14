// POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD (design/RimMandrake/pond_depth_design_2026-10-16.md §10, D1-D4 RULED 2026-10-16).
// Owner, by card: "Should natural water get partial depth like dug cells? → Yes, ponds shallow out". D2, his words: "It should
// slosh around until it levels, pond or canal or otherwise." The arithmetic is the PRODUCTION RM_PondDepthMath and the
// PRODUCTION RM_FlowKernel (head rule + return half); the world is the fuzz ArrayWorld.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class PondDepthChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        /// <summary>A w×h pond: rim squares bed <paramref name="rim"/>, the rest bed <paramref name="mid"/>.</summary>
        private static (List<int> cells, List<int> beds) Pond(int w, int h, int rim, int mid)
        {
            var cells = new List<int>();
            var beds = new List<int>();
            for (int z = 0; z < h; z++)
                for (int x = 0; x < w; x++)
                {
                    cells.Add(z * w + x);
                    beds.Add(x == 0 || z == 0 || x == w - 1 || z == h - 1 ? rim : mid);
                }
            return (cells, beds);
        }

        /// <summary>w per square for <paramref name="levels"/> over the pond (s, r and the patch from production).</summary>
        private static int[] Layout(int w, int h, List<int> cells, List<int> beds, long levels, out int s, out int r,
            Func<int, bool> eligible = null)
        {
            int[] hist = RM_PondDepthMath.Histogram(beds);
            RM_PondDepthMath.Drawdown(levels, hist, out s, out r);
            HashSet<int> patch = RM_PondDepthMath.PickPatch(w, h, cells, beds, s, r, eligible);
            var water = new int[cells.Count];
            for (int i = 0; i < cells.Count; i++)
            {
                water[i] = RM_PondDepthMath.WaterAt(beds[i], s, patch.Contains(cells[i]));
            }
            return water;
        }

        private static bool Connected4(int w, IEnumerable<int> set)
        {
            var s = new HashSet<int>(set);
            if (s.Count <= 1) return true;
            var q = new Queue<int>();
            var seen = new HashSet<int> { s.First() };
            q.Enqueue(s.First());
            while (q.Count > 0)
            {
                int c = q.Dequeue();
                foreach (int nb in new[] { c + 1, c - 1, c + w, c - w })
                {
                    if ((nb == c + 1 && nb % w == 0) || (nb == c - 1 && c % w == 0)) continue;
                    if (s.Contains(nb) && seen.Add(nb)) q.Enqueue(nb);
                }
            }
            return seen.Count == s.Count;
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("PondDepth_S1_shallow_out_not_shrink", () =>
            {
                // 10×10 pond, rim bed 2, middle bed 4 (capacity 36×2 + 64×4 = 328 levels), drawn one surface level at a time.
                var (cells, beds) = Pond(10, 10, 2, 4);
                int cap = beds.Sum();
                Assert(cap == 328, "capacity " + cap);
                int[] one = Layout(10, 10, cells, beds, cap - 100, out int s1, out int r1);
                Assert(s1 == 1 && r1 == 0, "one level drawn: s=" + s1 + " r=" + r1);
                Assert(one.All(x => x > 0), "after one level no square is dry (the old model dried 50 rim squares)");
                for (int i = 0; i < cells.Count; i++)
                    Assert(beds[i] != 4 || one[i] == 3, "every bed-4 square reads 3 after one level");
                int[] two = Layout(10, 10, cells, beds, cap - 200, out int s2, out _);
                Assert(s2 == 2, "two levels drawn: s=" + s2);
                for (int i = 0; i < cells.Count; i++)
                    Assert(beds[i] == 4 ? two[i] == 2 : two[i] == 0, "after two: the rim is exposed (mud), the middle reads 2");
                // Σ terrain-implied levels == floor(V), at EVERY stock from empty to full (and over).
                for (int v = 0; v <= cap + 5; v++)
                {
                    int[] wa = Layout(10, 10, cells, beds, v, out int s, out int r);
                    Assert(wa.Sum() == Math.Min(v, cap), "Σw " + wa.Sum() + " != V " + v + " (s=" + s + " r=" + r + ")");
                }
                // Stage ladder (§4): full → original, then deep/chest/shallow/thin, then mud, then lakebed.
                Assert(RM_PondDepthMath.StageFor(4, 4, false) == RM_PondDepthMath.Stage.Original, "full = original");
                Assert(RM_PondDepthMath.StageFor(6, 8, false) == RM_PondDepthMath.Stage.Deep, "w 6 of 8 = deep");
                Assert(RM_PondDepthMath.StageFor(3, 4, false) == RM_PondDepthMath.Stage.ChestDeep, "w 3 = chest-deep still");
                Assert(RM_PondDepthMath.StageFor(2, 4, false) == RM_PondDepthMath.Stage.Shallow, "w 2 of 4 = shallow");
                Assert(RM_PondDepthMath.StageFor(2, 2, false) == RM_PondDepthMath.Stage.Original, "a full bed-2 square (marsh too) keeps its own look");
                Assert(RM_PondDepthMath.StageFor(1, 2, false) == RM_PondDepthMath.Stage.Thin, "w 1 = thin water");
                Assert(RM_PondDepthMath.StageFor(0, 2, false) == RM_PondDepthMath.Stage.Mud, "just exposed = mud");
                Assert(RM_PondDepthMath.StageFor(0, 2, true) == RM_PondDepthMath.Stage.Lakebed, "past the mud time = lakebed");
            });

            Case("PondDepth_S2_min_depth_is_one_patch", () =>
            {
                var (cells, beds) = Pond(10, 10, 2, 4);
                int cap = beds.Sum();
                int checkedPatches = 0;
                for (int v = 1; v < cap; v++)
                {
                    int[] hist = RM_PondDepthMath.Histogram(beds);
                    RM_PondDepthMath.Drawdown(v, hist, out int s, out int r);
                    if (r == 0) continue;
                    Assert(r < hist[s], "r " + r + " < H[s] " + hist[s]);
                    HashSet<int> patch = RM_PondDepthMath.PickPatch(10, 10, cells, beds, s, r);
                    Assert(patch.Count == r, "patch holds r squares");
                    Assert(Connected4(10, patch), "V=" + v + ": the band-" + s + " squares form one 4-connected patch, never 0,1,0,1");
                    Assert(patch.All(c => beds[cells.IndexOf(c)] >= s), "the patch is drawn from squares that own band s");
                    checkedPatches++;
                }
                Assert(checkedPatches > 100, "the sweep reached the part-level case " + checkedPatches + " times");
            });

            // PondDepth_S4_head_rule_ditch_above_surface_stops and PondDepth_S3_pond_canal_pond_level_to_one_surface were deleted
            // with the whole-notch engine (RIMMANDRAKE_DELETE_FILL_N_ONE_WATER_NUMBER_SEVEN_FIXES): they drove its pond head rule
            // (RM_FlowKernel.sourceDrawdown / returnLevel / ReturnToPonds), which the shipped game never ran (the exact-level
            // kernel solves a pond and its canals as one surface; LevelExact_* and ExcavationTick_* cover that).

            Case("PondDepth_S4_return_half_and_dead_band", () =>
            {
                // Pure head rule: a give leaves the dug side at the new surface or one above it; a return needs two above.
                for (int s = 0; s <= 6; s++)
                    for (int d = 1; d <= 4; d++)
                        for (int f = 0; f <= d; f++)
                        {
                            bool give = RM_PondDepthMath.SourceMayGive(s, d, f);
                            bool ret = RM_PondDepthMath.DugMayReturn(s, d, f);
                            Assert(!(give && ret), "never both give and return (s=" + s + " d=" + d + " f=" + f + ")");
                            Assert(give == (f - d <= -s - 1), "give iff the dug surface is below the pond's");
                            Assert(ret == (f > 0 && f - d >= -s + 2), "return iff two or more above");
                        }
                Assert(!RM_PondDepthMath.DugMayReturn(0, 4, 4), "a brim-full pond takes no return from a brim-full canal (today unchanged)");
                Assert(RM_PondDepthMath.SourceMayGive(0, 1, 0), "a brim-full pond feeds a D=1 ditch (today unchanged)");
            });

            Case("PondDepth_S5_relay_is_a_pure_function_of_stock", () =>
            {
                // Migration and the toggle re-lay from the stock alone: the same stock gives the same s, r and wet set every
                // time, in any order of re-lays (the stock never moves during one).
                var (cells, beds) = Pond(12, 9, 2, 4);
                for (int k = 0; k < cells.Count; k += 7) beds[k] = Math.Max(beds[k], 6);   // a few deeper squares
                int cap = beds.Sum();
                foreach (int v in new[] { 0, 1, 17, cap / 3, cap / 2, cap - 1, cap })
                {
                    int[] w1 = Layout(12, 9, cells, beds, v, out int s1, out int r1);
                    int[] w2 = Layout(12, 9, cells, beds, v, out int s2, out int r2);
                    Assert(s1 == s2 && r1 == r2 && w1.SequenceEqual(w2), "re-lay at V=" + v + " is identical");
                    Assert(w1.Sum() == v, "the picture holds exactly the stock");
                }
            });

            Case("PondDepth_S8_occupied_square_waits_share_goes_on", () =>
            {
                // Ruling 5: a dry square with a pawn waits; its band share goes to the next square in patch order and the
                // picture still holds exactly V (the stock is the truth; nothing is spent on the waiting square).
                var (cells, beds) = Pond(8, 8, 2, 2);
                int cap = beds.Sum();
                int blocked = 3 * 8 + 3;
                for (int v = 1; v < cap; v++)
                {
                    int[] hist = RM_PondDepthMath.Histogram(beds);
                    RM_PondDepthMath.Drawdown(v, hist, out int s, out int r);
                    if (r == 0) continue;
                    HashSet<int> patch = RM_PondDepthMath.PickPatch(8, 8, cells, beds, s, r, c => c != blocked);
                    Assert(!patch.Contains(blocked), "the occupied square is never picked");
                    Assert(patch.Count == r, "its share went to the next square (V=" + v + ")");
                }
            });

            Case("PondDepth_S7_cost_40000_square_lake", () =>
            {
                // §8: a 200×200 lake with a deep middle (beds 2 .. 20), drawn over 100 pulses: histogram once, then s/r and the
                // part-level patch per pulse. Bar: under 10 ms a pulse added (selftest harness; the terrain writes are capped
                // separately by pondStageWritesPerPulse).
                int w = 200, h = 200;
                var cells = new List<int>(w * h);
                var beds = new List<int>(w * h);
                for (int z = 0; z < h; z++)
                    for (int x = 0; x < w; x++)
                    {
                        int d = Math.Min(Math.Min(x, w - 1 - x), Math.Min(z, h - 1 - z));
                        cells.Add(z * w + x);
                        beds.Add(d == 0 ? 2 : Math.Min(20, 4 + Math.Max(0, (d - 3) / 4)));   // the retired §9.4 slope, kept as this bench's input
                    }
                long cap = beds.Sum();
                var sw = Stopwatch.StartNew();
                int[] hist = RM_PondDepthMath.Histogram(beds);
                double histMs = sw.Elapsed.TotalMilliseconds;
                long sumCheck = 0;
                // best of 3 timed runs of the 100 pulses (10.75 ms was measured once against the 10 ms bar on a loaded box): a
                // scheduler hiccup lands in one run, a real regression is slow in all three
                double perPulse = double.MaxValue;
                for (int run = 0; run < 3; run++)
                {
                    sw.Restart();
                    sumCheck = 0;
                    for (int p = 0; p < 100; p++)
                    {
                        long v = cap - (long)p * 3000;
                        RM_PondDepthMath.Drawdown(v, hist, out int s, out int r);
                        sumCheck += RM_PondDepthMath.PickPatch(w, h, cells, beds, s, r).Count;
                    }
                    perPulse = Math.Min(perPulse, sw.Elapsed.TotalMilliseconds / 100.0);
                }
                Console.WriteLine("    S7: 40,000-square lake, histogram " + histMs.ToString("F1") + " ms once, s/r/patch " + perPulse.ToString("F2") + " ms a pulse (bar 10)");
                Assert(sumCheck > 0, "the sweep reached part-levels");
                Assert(perPulse < 10.0, "pond depth adds " + perPulse.ToString("F2") + " ms a pulse on a 40,000-square lake (bar 10)");
            });
        }
    }
}
