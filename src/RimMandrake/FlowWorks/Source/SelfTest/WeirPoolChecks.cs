// WEIR_POOL_DIAGNOSE_DAMMED_AT_THE_EDGE: the weir's slack pool walked upstream by a rule that wanted a neighbour whose
// QUANTISED 8-way flow direction stepped exactly onto the cell (else the cell straight behind it). The weir's wet end
// is a bank-edge cell by construction, and vanilla's flow there runs ALONG the river (TileMutatorWorker_River averages
// the centreline tangents), so on a river not aligned to the 8 compass directions the exact step lands beside the
// cell and the cell behind is bank: pool = 0 (live, tile 825, 2026-10-12: "POOL cells=0 ... at=(108, 0, 12)").
// These cases drive the PRODUCTION walk (RM_RiverMath.UpstreamWalk, which RM_Building_BankWeir.AddPoolCells calls)
// on synthetic rasterised rivers, with the pre-fix rule beside it as the can-fail.
// NOT proven here: that tile 825's own grid has this shape (ProofWeirPool now prints the neighbourhood for that).
using System;
using System.Collections.Generic;
using RimMandrake.FlowWorks.Rivers;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class WeirPoolChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private const int N = 48;

        /// <summary>A straight river band at `deg` degrees through the grid, half-width `hw` cells; every water cell
        /// carries the along-river flow, quantised (optionally jittered +-`jitter` degrees by a fixed hash, the way
        /// vanilla's averaged tangents wander), -1 for bank and out of bounds.</summary>
        private static Func<int, int, int> River(double deg, double hw, double jitter)
        {
            double r = deg * Math.PI / 180.0;
            double ux = Math.Cos(r), uz = Math.Sin(r);
            int[,] g = new int[N, N];
            for (int x = 0; x < N; x++)
                for (int z = 0; z < N; z++)
                {
                    double px = x - N / 2.0, pz = z - N / 2.0;
                    double perp = -px * uz + pz * ux;
                    if (Math.Abs(perp) > hw) { g[x, z] = -1; continue; }
                    double j = jitter * (((x * 73856093 ^ z * 19349663) & 1023) / 511.5 - 1.0);
                    double a = r + j * Math.PI / 180.0;
                    g[x, z] = RM_RiverMath.Quantise((float)Math.Cos(a), (float)Math.Sin(a));
                }
            return (x, z) => x < 0 || z < 0 || x >= N || z >= N ? -1 : g[x, z];
        }

        /// <summary>The pre-fix RM_Building_BankWeir.Upstream + AddPoolCells spine, kept verbatim in shape.</summary>
        private static int OldWalk(int x0, int z0, int length, Func<int, int, int> dirAt)
        {
            int x = x0, z = z0, k = 0;
            for (; k < length; k++)
            {
                int curDir = dirAt(x, z);
                int bx = int.MinValue, bz = 0;
                bool found = false;
                for (int i = 0; i < 8 && !found; i++)
                {
                    int nx = x + RM_RiverMath.StepX[i], nz = z + RM_RiverMath.StepZ[i];
                    int d = dirAt(nx, nz);
                    if (d < 0 || nx + RM_RiverMath.StepX[d] != x || nz + RM_RiverMath.StepZ[d] != z) continue;
                    if (d == curDir) { bx = nx; bz = nz; found = true; }
                    else if (bx == int.MinValue) { bx = nx; bz = nz; }
                }
                if (bx == int.MinValue && curDir >= 0)
                {
                    int ax = x - RM_RiverMath.StepX[curDir], az = z - RM_RiverMath.StepZ[curDir];
                    if (dirAt(ax, az) >= 0) { bx = ax; bz = az; }
                }
                if (bx == int.MinValue) break;
                x = bx; z = bz;
            }
            return k;
        }

        /// <summary>Wet bank-edge cells (water with a 4-neighbour of bank) far enough from the grid edge that a
        /// full pool fits upstream - what FindWeirSite's margin guarantees in game.</summary>
        private static List<int[]> EdgeCells(Func<int, int, int> dirAt, int margin)
        {
            List<int[]> list = new List<int[]>();
            for (int x = margin; x < N - margin; x++)
                for (int z = margin; z < N - margin; z++)
                {
                    if (dirAt(x, z) < 0) continue;
                    if (dirAt(x + 1, z) < 0 || dirAt(x - 1, z) < 0 || dirAt(x, z + 1) < 0 || dirAt(x, z - 1) < 0)
                        list.Add(new[] { x, z });
                }
            return list;
        }

        private static int NewWalk(int x0, int z0, int length, Func<int, int, int> dirAt, List<int[]> spine = null)
        {
            return RM_RiverMath.UpstreamWalk(x0, z0, length, dirAt, (x, z) => spine?.Add(new[] { x, z }));
        }

        public static void Run(Action<string, Action> Case)
        {
            const int L = 8;   // RM_RiversSettings.weirPoolLength default
            const int M = L + 4;

            Case("WeirPool_edge_lane_minimal_scene_old_zero_new_pools", () =>
            {
                // the 3x3 shape of the inferred tile-825 site: wet cell flows NE, bank to its S/SW/SE, the water to
                // its W/NW also NE, N/NE flow E. No neighbour's quantised step lands on it; the cell behind is bank.
                Dictionary<(int, int), int> m = new Dictionary<(int, int), int>
                {
                    [(0, 0)] = 1, [(-1, 0)] = 1, [(-1, 1)] = 1, [(0, 1)] = 0, [(1, 1)] = 0, [(1, 0)] = 1,
                    [(-2, 0)] = 1, [(-2, 1)] = 1, [(-3, 0)] = 0, [(-3, 1)] = 0, [(-2, 2)] = 1, [(-1, 2)] = 1,
                };
                Func<int, int, int> d = (x, z) => m.TryGetValue((x, z), out int v) ? v : -1;
                int oldK = OldWalk(0, 0, L, d);
                int newK = NewWalk(0, 0, L, d);
                Console.WriteLine("      old spine=" + oldK + " new spine=" + newK);
                Assert(oldK == 0, "can-fail: the pre-fix rule must reproduce pool=0 on this scene, got " + oldK);
                Assert(newK >= 1, "the new rule must find the W neighbour upstream, got " + newK);
                Assert(RM_RiverMath.UpstreamStep(0, 0, d) == 4, "first step must be W (index 4), got " + RM_RiverMath.UpstreamStep(0, 0, d));
            });

            Case("WeirPool_off_axis_rivers_every_bank_edge_pools", () =>
            {
                // rivers at angles the 8-way quantisation does not hit exactly, with and without wander
                int oldZero = 0, newShort = 0, sites = 0;
                foreach (double deg in new[] { 0.0, 15, 22, 30, 37, 60, 105, 200, 290 })
                    foreach (double jit in new[] { 0.0, 12 })
                    {
                        Func<int, int, int> d = River(deg, 2.6, jit);
                        foreach (int[] c in EdgeCells(d, M))
                        {
                            sites++;
                            if (OldWalk(c[0], c[1], L, d) == 0) oldZero++;
                            if (NewWalk(c[0], c[1], L, d) < L) newShort++;
                        }
                    }
                Console.WriteLine("      sites=" + sites + " oldPool0=" + oldZero + " newShortOfFull=" + newShort);
                Assert(sites > 200, "sanity: the scenes must hold bank-edge sites, got " + sites);
                Assert(oldZero > 0, "can-fail: the pre-fix rule must pool 0 at some off-axis bank edge, got 0");
                Assert(newShort == 0, "every bank-edge site must get a full " + L + "-cell spine, " + newShort + " fell short");
            });

            Case("WeirPool_straight_river_unchanged_from_old_rule", () =>
            {
                // an axis-aligned river: the old exact step and the new best-aligned step are the same cell
                Func<int, int, int> d = River(0, 3.2, 0);
                foreach (int[] c in EdgeCells(d, M))
                {
                    List<int[]> sp = new List<int[]>();
                    Assert(NewWalk(c[0], c[1], L, d, sp) == L && OldWalk(c[0], c[1], L, d) == L, "full pool both ways");
                    for (int k = 0; k < sp.Count; k++)
                        Assert(sp[k][0] == c[0] - (k + 1) && sp[k][1] == c[1], "straight back along the flow at step " + k);
                }
            });

            Case("WeirPool_walk_never_goes_downstream_or_across", () =>
            {
                foreach (double deg in new[] { 0.0, 30, 60, 135, 250 })
                {
                    Func<int, int, int> d = River(deg, 2.6, 12);
                    double r = deg * Math.PI / 180.0, ux = Math.Cos(r), uz = Math.Sin(r);
                    foreach (int[] c in EdgeCells(d, M))
                    {
                        List<int[]> sp = new List<int[]>();
                        NewWalk(c[0], c[1], L, d, sp);
                        double prev = 0;
                        for (int k = 0; k < sp.Count; k++)
                        {
                            double along = (sp[k][0] - c[0]) * ux + (sp[k][1] - c[1]) * uz;
                            Assert(along < prev, "step " + k + " at deg " + deg + " did not move upstream (along " + along + ")");
                            prev = along;
                            Assert(d(sp[k][0], sp[k][1]) >= 0, "spine left the water");
                        }
                    }
                }
                // a lone cell whose only wet neighbours are lateral (flow E, wet N and S only) has no upstream
                Func<int, int, int> lat = (x, z) => x == 0 && z >= -1 && z <= 1 ? 0 : -1;
                Assert(RM_RiverMath.UpstreamStep(0, 0, lat) == -1, "a lateral neighbour is not upstream");
                // a neighbour flowing straight at the cell against its own flow gives no local flow to follow
                Func<int, int, int> opp = (x, z) => z != 0 ? -1 : (x == 0 ? 0 : (x == -1 ? 4 : -1));
                Assert(RM_RiverMath.UpstreamStep(0, 0, opp) == -1, "opposed flows: no upstream");
            });

            Case("WeirPool_length_honoured_and_no_revisit", () =>
            {
                Func<int, int, int> d = River(30, 4, 12);
                int[] c = EdgeCells(d, M)[0];
                foreach (int len in new[] { 0, 1, 3, 8 })
                {
                    List<int[]> sp = new List<int[]>();
                    int k = NewWalk(c[0], c[1], len, d, sp);
                    Assert(k == sp.Count && k <= len, "steps " + k + " for length " + len);
                    HashSet<(int, int)> seen = new HashSet<(int, int)> { (c[0], c[1]) };
                    foreach (int[] s in sp) Assert(seen.Add((s[0], s[1])), "revisited a cell");
                }
            });
        }
    }
}
