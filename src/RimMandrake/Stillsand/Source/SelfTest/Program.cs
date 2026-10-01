using System;
using System.Collections.Generic;

namespace RimMandrake.Stillsand.SelfTest
{
    // STILLSAND_PRECIOUS_CAVES_1 offline selftest. Drives the production
    // RM_PreciousCaveGeometry with synthetic rock grids. The item's own first
    // criterion ("at least eight of ten maps with rock carry a cave whose mouth
    // faces away from the sun") is reproduced here on ten synthetic yardangs at
    // ten different sun bearings; the real-map version is the live quicktest.
    internal static class Program
    {
        private static int failures;
        private static int checks;

        private static void Check(bool ok, string what)
        {
            checks++;
            if (!ok)
            {
                failures++;
                Console.WriteLine("FAIL " + what);
            }
        }

        private static int Main()
        {
            Compass();
            Yardang();
            DepthAndChamber();
            ShadeMouthTenRocks();
            ShadeMouthFansOut();
            Weighted();
            Console.WriteLine(failures == 0
                ? "PASS precious caves selftest: " + checks + "/" + checks + " checks"
                : "FAILED precious caves selftest: " + failures + " of " + checks + " checks failed");
            return failures == 0 ? 0 : 1;
        }

        private static void Compass()
        {
            Check(RM_PreciousCaveGeometry.CompassWord(0, 10) == "north", "compass north");
            Check(RM_PreciousCaveGeometry.CompassWord(7, 7) == "north-east", "compass north-east");
            Check(RM_PreciousCaveGeometry.CompassWord(5, 0) == "east", "compass east");
            Check(RM_PreciousCaveGeometry.CompassWord(0, -3) == "south", "compass south");
            Check(RM_PreciousCaveGeometry.CompassWord(-4, -4) == "south-west", "compass south-west");
            Check(RM_PreciousCaveGeometry.CompassWord(-9, 0.5) == "west", "compass west");
            Check(RM_PreciousCaveGeometry.CompassWord(0, 0) == "centre", "compass centre");
        }

        private static void Yardang()
        {
            RM_PreciousCaveGeometry.YardangAxes(300, 2.6, out double a, out double b);
            Check(Math.Abs(Math.PI * a * b - 300) < 1, "yardang axes preserve area (" + (Math.PI * a * b).ToString("0.0") + ")");
            Check(Math.Abs(a / b - 2.6) < 1e-6, "yardang aspect");
            Check(RM_PreciousCaveGeometry.InYardang(0, 0, a, b, 0.45), "yardang contains its centre");
            Check(!RM_PreciousCaveGeometry.InYardang(a + 0.5, 0, a, b, 0.45), "yardang ends at its tail");
            // The upwind head is wider than the downwind tail at equal distance.
            double u = a * 0.6;
            double v = b * 0.7;
            Check(RM_PreciousCaveGeometry.InYardang(-u, v, a, b, 0.45), "yardang head is blunt");
            Check(!RM_PreciousCaveGeometry.InYardang(u, v, a, b, 0.45), "yardang tail tapers");
            Check(RM_PreciousCaveGeometry.InYardang(u, v, a, b, 0.0), "taper 0 is a plain ellipse");
        }

        private static bool[] Rock(int w, int h, double cx, double cz, double ux, double uz, int area, double aspect)
        {
            RM_PreciousCaveGeometry.YardangAxes(area, aspect, out double a, out double b);
            bool[] g = new bool[w * h];
            for (int z = 0; z < h; z++)
            {
                for (int x = 0; x < w; x++)
                {
                    double dx = x - cx;
                    double dz = z - cz;
                    g[z * w + x] = RM_PreciousCaveGeometry.InYardang(dx * ux + dz * uz, -dx * uz + dz * ux, a, b, 0.45);
                }
            }
            return g;
        }

        private static List<int> Cells(bool[] g)
        {
            List<int> l = new List<int>();
            for (int i = 0; i < g.Length; i++)
            {
                if (g[i]) l.Add(i);
            }
            return l;
        }

        private static void DepthAndChamber()
        {
            const int w = 60, h = 60;
            bool[] g = Rock(w, h, 30, 30, 1, 0, 400, 2.6);
            int[] d = RM_PreciousCaveGeometry.DepthMap(g, w, h);
            Check(d[0] == 0, "open ground depth 0");
            int deepest = RM_PreciousCaveGeometry.DeepestCell(Cells(g), d, w);
            Check(deepest >= 0 && g[deepest], "deepest cell is rock");
            Check(d[deepest] >= 4, "a 400-cell yardang is at least 4 deep (" + d[deepest] + ")");
            int r = RM_PreciousCaveGeometry.ChamberRadius(400, d[deepest], 1, 6);
            Check(r >= 2 && r <= d[deepest] - 2, "chamber sized to rock and keeps a rim (r=" + r + ")");

            // A one-cell-thick wall has no room for a chamber.
            Check(RM_PreciousCaveGeometry.ChamberRadius(60, 1, 1, 6) == 0, "thin rock holds no chamber");
            // A huge rock is clamped to the max radius.
            Check(RM_PreciousCaveGeometry.ChamberRadius(5000, 40, 1, 6) == 6, "huge rock clamps to max radius");

            // Map-edge rock counts as exposed (depth 1), never infinitely deep.
            bool[] full = new bool[10 * 10];
            for (int i = 0; i < full.Length; i++) full[i] = true;
            int[] fd = RM_PreciousCaveGeometry.DepthMap(full, 10, 10);
            Check(fd[0] == 1 && fd[5 * 10 + 5] <= 6, "all-rock grid is finite depth");
        }

        private static void ShadeMouthTenRocks()
        {
            const int w = 120, h = 120;
            Random rng = new Random(1953);
            int facingAway = 0;
            for (int k = 0; k < 10; k++)
            {
                double bearing = k * 36.0 + rng.NextDouble() * 20.0; // sun bearing, clockwise from north
                double br = bearing * Math.PI / 180.0;
                double sdx = -Math.Sin(br), sdz = -Math.Cos(br);        // shadow (downwind) direction
                int area = 120 + rng.Next(500);
                bool[] g = Rock(w, h, 60, 60, sdx, sdz, area, 2.6);
                int[] d = RM_PreciousCaveGeometry.DepthMap(g, w, h);
                int c = RM_PreciousCaveGeometry.DeepestCell(Cells(g), d, w);
                int r = RM_PreciousCaveGeometry.ChamberRadius(area, d[c], 1, 6);
                bool rim = true;
                for (int z = c / w - r - 1; z <= c / w + r + 1; z++)
                {
                    for (int x = c % w - r - 1; x <= c % w + r + 1; x++)
                    {
                        double ex = x - c % w, ez = z - c / w;
                        if (Math.Sqrt(ex * ex + ez * ez) <= r + 0.5 && !g[z * w + x])
                        {
                            rim = false;
                        }
                    }
                }
                Check(r > 0 && rim, "rock " + k + " (" + area + " cells): chamber r=" + r + " stays inside the rock");
                List<int> tunnel = new List<int>();
                double ang = RM_PreciousCaveGeometry.ShadeMouth(g, w, h, c % w, c / w, sdx, sdz, tunnel, out int exit);
                if (double.IsNaN(ang) || exit < 0)
                {
                    Console.WriteLine("  rock " + k + ": no mouth");
                    continue;
                }
                double mx = exit % w - c % w, mz = exit / w - c / w;
                double dot = (mx * sdx + mz * sdz) / Math.Sqrt(mx * mx + mz * mz);
                bool exitOpen = !g[exit];
                bool tunnelRock = tunnel.TrueForAll(i => g[i]);
                if (dot > 0 && exitOpen && tunnelRock)
                {
                    facingAway++;
                }
                else
                {
                    Console.WriteLine("  rock " + k + ": dot " + dot.ToString("0.00") + " open " + exitOpen + " tunnelRock " + tunnelRock);
                }
            }
            Check(facingAway >= 8, "at least 8 of 10 rocks open their mouth away from the sun (" + facingAway + "/10)");
            Check(facingAway == 10, "all 10 synthetic rocks open away from the sun (" + facingAway + "/10)");
        }

        private static void ShadeMouthFansOut()
        {
            // Rock fills the whole lower (shadow-side) half of the map: a ray straight
            // along the shadow (south) hits the map edge in rock, so the mouth must fan
            // out — and still face away from the sun.
            const int w = 40, h = 40;
            bool[] g = new bool[w * h];
            for (int z = 0; z < h; z++)
            {
                for (int x = 0; x < w; x++)
                {
                    g[z * w + x] = z < 20 && x >= 8 && x < 32;
                }
            }
            List<int> tunnel = new List<int>();
            double ang = RM_PreciousCaveGeometry.ShadeMouth(g, w, h, 20, 10, 0, -1, tunnel, out int exit);
            Check(!double.IsNaN(ang) && Math.Abs(ang) > 0, "blocked shade ray fans out (angle " + ang + ")");
            if (exit >= 0)
            {
                double mz = exit / w - 10;
                Check(mz < 0.5, "fanned mouth still opens on the shadow side (dz " + mz + ")");
            }

            // No open ground reachable on the shadow side at all: no mouth.
            bool[] all = new bool[w * h];
            for (int i = 0; i < all.Length; i++) all[i] = true;
            double none = RM_PreciousCaveGeometry.ShadeMouth(all, w, h, 20, 20, 0, -1, tunnel, out int noExit);
            Check(double.IsNaN(none) && noExit == -1, "no way out means no mouth");
        }

        private static void Weighted()
        {
            double[] wts = { 5, 2, 1.5, 1.5, 0.5 };
            int[] hits = new int[wts.Length];
            Random rng = new Random(7);
            const int n = 200000;
            for (int i = 0; i < n; i++)
            {
                hits[RM_PreciousCaveGeometry.WeightedPick(wts, rng.NextDouble())]++;
            }
            double total = 10.5;
            for (int i = 0; i < wts.Length; i++)
            {
                double got = hits[i] / (double)n;
                double want = wts[i] / total;
                Check(Math.Abs(got - want) < 0.01, "weighted row " + i + " " + got.ToString("0.000") + " vs " + want.ToString("0.000"));
            }
            Check(RM_PreciousCaveGeometry.WeightedPick(new double[] { 0, 3, 0 }, 0.0) == 1, "zero weight never wins (low roll)");
            Check(RM_PreciousCaveGeometry.WeightedPick(new double[] { 0, 3, 0 }, 1.0) == 1, "zero weight never wins (high roll)");
            Check(RM_PreciousCaveGeometry.WeightedPick(new double[] { 0, 0 }, 0.5) == -1, "nothing weighted picks nothing");
            Check(RM_PreciousCaveGeometry.WeightedPick(new double[0], 0.5) == -1, "empty table picks nothing");
        }
    }
}
