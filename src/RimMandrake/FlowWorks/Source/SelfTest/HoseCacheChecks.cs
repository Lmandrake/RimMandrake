// HOSELINKS_REFRESH_DIAGNOSE_MAP0_TICK_SPIKE: RM_HoseLinks.Refresh reads every reel's Port() and FreeEnd() each tick; both
// are 60-tick caches. Stamped on the same tick, they all expired on the same tick, so one Refresh paid every
// HosePorts.Find (a pump-coupled one walks every reel) and HoseEnds.Read at once. These checks hold HoseLive.PhasedFresh to
// spreading those expiries (at most one of 60 consecutive ids per tick), to never being fresher than CacheFresh, and
// HoseLive.RectsNear to being an exact superset of "a reel body or free end can couple to the pump" (the PumpSideTakes
// prefilter), brute-forced on random rects.
using System;
using RimMandrake.FlowWorks.Hose;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class HoseCacheChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static bool In(int x, int z, int x0, int z0, int w, int h) => x >= x0 && x < x0 + w && z >= z0 && z < z0 + h;

        /// <summary>Brute force: does pump rect A hold a cell of B or a cell edge-adjacent outside B (HoseReelRect.Perimeter)?</summary>
        private static bool Couples(int ax, int az, int aw, int ah, int bx, int bz, int bw, int bh)
        {
            for (int x = bx - 1; x <= bx + bw; x++)
                for (int z = bz - 1; z <= bz + bh; z++)
                {
                    bool inB = In(x, z, bx, bz, bw, bh);
                    bool edge = !inB && (In(x, z - 1, bx, bz, bw, bh) || In(x, z + 1, bx, bz, bw, bh) || In(x - 1, z, bx, bz, bw, bh) || In(x + 1, z, bx, bz, bw, bh));
                    if ((inB || edge) && In(x, z, ax, az, aw, ah)) return true;
                }
            return false;
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("HOSECACHE_PHASED_SPREADS_EXPIRY", () =>
            {
                for (int start = 4990; start < 5010; start++)
                {
                    int[] staleAt = new int[200];
                    for (int id = 1000; id < 1060; id++)
                    {
                        int t = start + 1;
                        while (HoseLive.PhasedFresh(t, start, 60, id)) t++;
                        Assert(t - start >= 1 && t - start <= 60, "id " + id + " went stale after " + (t - start) + " ticks");
                        staleAt[t - start]++;
                    }
                    int worst = 0;
                    foreach (int n in staleAt) worst = Math.Max(worst, n);
                    Assert(worst <= 1, "60 ids read on tick " + start + ": " + worst + " went stale on one tick (want <= 1)");
                }
            });
            Case("HOSECACHE_PHASED_NEVER_FRESHER", () =>
            {
                var rng = new Random(7);
                Assert(!HoseLive.PhasedFresh(0, int.MinValue, 60, 5), "never-read cache read fresh");
                Assert(!HoseLive.PhasedFresh(int.MaxValue, int.MinValue, 60, 5), "never-read cache read fresh at MaxValue");
                for (int i = 0; i < 200000; i++)
                {
                    int last = rng.Next(-1000, 2000000);
                    int now = last + rng.Next(-5, 130);
                    int phase = rng.Next(int.MinValue, int.MaxValue);
                    bool p = HoseLive.PhasedFresh(now, last, 60, phase);
                    Assert(!p || HoseLive.CacheFresh(now, last, 60), "phased fresh where plain is stale: now=" + now + " last=" + last + " phase=" + phase);
                    if (now == last) Assert(p, "a cache read this tick is stale this tick: " + now + " phase=" + phase);
                }
            });
            Case("HOSECACHE_RECTSNEAR_SUPERSET", () =>
            {
                var rng = new Random(11);
                int near = 0, far = 0;
                for (int i = 0; i < 100000; i++)
                {
                    int aw = rng.Next(1, 4), ah = rng.Next(1, 4), ax = rng.Next(0, 12), az = rng.Next(0, 12);
                    bool end = rng.Next(2) == 0;
                    int bw = end ? 1 : rng.Next(1, 3), bh = end ? 1 : rng.Next(1, 3), bx = rng.Next(0, 12), bz = rng.Next(0, 12);
                    bool c = Couples(ax, az, aw, ah, bx, bz, bw, bh);
                    bool n = HoseLive.RectsNear(ax, az, aw, ah, bx, bz, bw, bh, 1);
                    Assert(!c || n, "couples but not near: A=" + ax + "," + az + " " + aw + "x" + ah + " B=" + bx + "," + bz + " " + bw + "x" + bh);
                    if (n) near++; else far++;
                    // exactness of the gap: two cells apart (Chebyshev) is never near at gap 1
                    bool gap2 = ax >= bx + bw + 1 || bx >= ax + aw + 1 || az >= bz + bh + 1 || bz >= az + ah + 1;
                    Assert(!(gap2 && n), "near across a 1-cell gap: A=" + ax + "," + az + " B=" + bx + "," + bz);
                }
                Assert(near > 1000 && far > 1000, "degenerate sample near=" + near + " far=" + far);
            });
        }
    }
}
