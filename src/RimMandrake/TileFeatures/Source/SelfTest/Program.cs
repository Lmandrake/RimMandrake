// Selftest of the landform geometry (VEE_LANDFORMS_BUILD_CRATERS_AND_COMPANY), compiled straight from production
// RM_LandformGeometry.cs. Covers every pure decision the landform workers make: wobbly crater radius, crater zones and rim
// breaches, meandering lines and the distance/arc maths, the band-with-a-gap a ridge or canyon is drawn from, disc
// placement for cenotes/sinkholes/spires, and the tide. Two raster checks prove what a player would feel: a ridge with a
// gap leaves the map walkable end to end and one without does not; a crater with breaches can be walked into and one
// without cannot. Each of those carries a planted negative, so the instrument is shown able to see a failure.
// NOT covered: anything needing a Map (the workers turning these answers into elevation and terrain) - that is L3, live.

using System;
using System.Collections.Generic;

namespace RimMandrake.TileFeatures.SelfTest
{
    internal static class Program
    {
        private static int pass, fail;

        private static void Check(string name, bool ok)
        {
            Console.WriteLine((ok ? "PASS  " : "FAIL  ") + name);
            if (ok) pass++; else fail++;
        }

        private static bool Near(float a, float b, float eps = 1e-3f) { return Math.Abs(a - b) <= eps; }

        // 4-connected flood fill over cells where open[x,z]; true if (bx,bz) is reached from (ax,az)
        private static bool Connected(bool[,] open, int ax, int az, int bx, int bz)
        {
            int w = open.GetLength(0), h = open.GetLength(1);
            if (!open[ax, az] || !open[bx, bz]) return false;
            bool[,] seen = new bool[w, h];
            Queue<int> q = new Queue<int>();
            q.Enqueue(ax * h + az); seen[ax, az] = true;
            int[] dx = { 1, -1, 0, 0 }, dz = { 0, 0, 1, -1 };
            while (q.Count > 0)
            {
                int v = q.Dequeue(), x = v / h, z = v % h;
                if (x == bx && z == bz) return true;
                for (int k = 0; k < 4; k++)
                {
                    int nx = x + dx[k], nz = z + dz[k];
                    if (nx < 0 || nz < 0 || nx >= w || nz >= h || seen[nx, nz] || !open[nx, nz]) continue;
                    seen[nx, nz] = true; q.Enqueue(nx * h + nz);
                }
            }
            return false;
        }

        private static int Main()
        {
            // --- wobbled radius
            float[] amps = { 0.05f, 0.04f, 0.03f }, ph = { 0.3f, 1.1f, 2.0f };
            bool inBounds = true;
            for (int i = 0; i < 3600; i++)
            {
                float r = RM_LandformGeometry.WobbledRadius(40f, i * RM_LandformGeometry.TwoPi / 3600f, amps, ph);
                if (r < 40f * (1f - 0.12f) - 1e-3f || r > 40f * (1f + 0.12f) + 1e-3f) inBounds = false;
            }
            Check("wobbled radius stays within baseR*(1 +/- sum|amp|) over a full turn", inBounds);
            Check("wobbled radius with no harmonics is the base radius", Near(RM_LandformGeometry.WobbledRadius(40f, 1.3f, null, null), 40f));

            // --- angle gap
            Check("angle gap wraps: 0 vs 2pi-0.1 is 0.1", Near(RM_LandformGeometry.AngleGap(0f, RM_LandformGeometry.TwoPi - 0.1f), 0.1f));
            Check("angle gap: pi vs -pi is 0", Near(RM_LandformGeometry.AngleGap((float)Math.PI, -(float)Math.PI), 0f));

            // --- crater zones
            Check("crater: beyond radius is Outside", RM_LandformGeometry.CraterZone(41f, 40f, 0.2f, 0f, 0f) == RM_CraterZone.Outside);
            Check("crater: zero radius is Outside", RM_LandformGeometry.CraterZone(0f, 0f, 0.2f, 0f, 0f) == RM_CraterZone.Outside);
            Check("crater: outer band is Rim", RM_LandformGeometry.CraterZone(38f, 40f, 0.2f, 0f, 0f) == RM_CraterZone.Rim);
            Check("crater: rim inside a breach is Basin",
                RM_LandformGeometry.CraterZone(38f, 40f, 0.2f, 0f, 0f, 1.0f, new[] { 1.05f }, 0.1f) == RM_CraterZone.Basin);
            Check("crater: rim outside the breach stays Rim",
                RM_LandformGeometry.CraterZone(38f, 40f, 0.2f, 0f, 0f, 2.0f, new[] { 1.05f }, 0.1f) == RM_CraterZone.Rim);
            Check("crater: centre with a dome is Dome", RM_LandformGeometry.CraterZone(4f, 40f, 0.2f, 0f, 0.25f) == RM_CraterZone.Dome);
            Check("crater: centre with a pool is Pool", RM_LandformGeometry.CraterZone(12f, 40f, 0.2f, 0.55f, 0f) == RM_CraterZone.Pool);
            Check("crater: between pool and rim is Basin", RM_LandformGeometry.CraterZone(28f, 40f, 0.2f, 0.55f, 0f) == RM_CraterZone.Basin);
            bool order = true; RM_CraterZone prev = RM_CraterZone.Dome;
            int Rank(RM_CraterZone z) { return z == RM_CraterZone.Dome ? 0 : z == RM_CraterZone.Pool ? 1 : z == RM_CraterZone.Basin ? 2 : z == RM_CraterZone.Rim ? 3 : 4; }
            for (float d = 0f; d <= 45f; d += 0.25f)
            {
                RM_CraterZone z = RM_LandformGeometry.CraterZone(d, 40f, 0.2f, 0.5f, 0.2f);
                if (Rank(z) < Rank(prev)) order = false;
                prev = z;
            }
            Check("crater: along a ray the zones run dome, pool, basin, rim, outside and never go back", order);

            // --- crater enclosure raster (with planted negative)
            bool CraterWalkable(int breaches)
            {
                int n = 121, c = 60;
                bool[,] open = new bool[n, n];
                float[] br = new float[breaches];
                for (int i = 0; i < breaches; i++) br[i] = i * RM_LandformGeometry.TwoPi / Math.Max(1, breaches) + 0.4f;
                for (int x = 0; x < n; x++)
                    for (int z = 0; z < n; z++)
                    {
                        float dx = x - c, dz = z - c;
                        float ang = (float)Math.Atan2(dz, dx);
                        float r = RM_LandformGeometry.WobbledRadius(40f, ang, amps, ph);
                        RM_CraterZone zone = RM_LandformGeometry.CraterZone((float)Math.Sqrt(dx * dx + dz * dz), r, 0.2f, 0f, 0f, ang, br, 0.12f);
                        open[x, z] = zone != RM_CraterZone.Rim;
                    }
                return Connected(open, 0, 0, c, c);
            }
            Check("crater raster: two breaches let a walker from the map edge reach the basin", CraterWalkable(2));
            Check("crater raster (planted negative): no breach seals the basin off", !CraterWalkable(0));

            // --- meander
            RM_LandformGeometry.Meander(50f, 50f, 0f, 40f, 20, 0f, 2f, 0f, out float[] xs, out float[] zs);
            bool straight = true;
            for (int i = 0; i < zs.Length; i++) if (!Near(zs[i], 50f)) straight = false;
            Check("meander with zero amplitude is a straight line of segments+1 points", xs.Length == 21 && straight);
            Check("meander with zero amplitude is 2*halfLength long", Near(RM_LandformGeometry.PolylineLength(xs, zs), 80f, 0.01f));
            Check("meander midpoint sits on the centre", Near(xs[10], 50f) && Near(zs[10], 50f));
            RM_LandformGeometry.Meander(50f, 50f, 0.7f, 40f, 64, 9f, 1.7f, 0.4f, out xs, out zs);
            bool within = true;
            float nx = -(float)Math.Sin(0.7f), nz = (float)Math.Cos(0.7f);
            for (int i = 0; i < xs.Length; i++)
                if (Math.Abs((xs[i] - 50f) * nx + (zs[i] - 50f) * nz) > 9f + 1e-3f) within = false;
            Check("meander never strays more than its amplitude from its axis", within);

            // --- distances
            float dseg = RM_LandformGeometry.DistToSegment(0f, 1f, -1f, 0f, 1f, 0f, out float tseg);
            Check("distance to segment: (0,1) to (-1,0)-(1,0) is 1 at t=0.5", Near(dseg, 1f) && Near(tseg, 0.5f));
            float dend = RM_LandformGeometry.DistToSegment(3f, 0f, -1f, 0f, 1f, 0f, out float tend);
            Check("distance to segment clamps to the end point", Near(dend, 2f) && Near(tend, 1f));
            float dpl = RM_LandformGeometry.DistToPolyline(10f, 3f, new[] { 0f, 10f, 10f }, new[] { 0f, 0f, 10f }, out float arc);
            Check("distance to polyline picks the nearest leg and the arc length to it", Near(dpl, 0f) && Near(arc, 13f));

            // --- ridge band with a gap, raster (with planted negative)
            bool RidgeWalkable(float gapLen)
            {
                int n = 120;
                RM_LandformGeometry.Meander(60f, 60f, 0f, 90f, 60, 6f, 1.2f, 0.3f, out float[] rx, out float[] rz);
                float len = RM_LandformGeometry.PolylineLength(rx, rz);
                float gs = gapLen > 0f ? len / 2f - gapLen / 2f : -1f;
                bool[,] open = new bool[n, n];
                for (int x = 0; x < n; x++)
                    for (int z = 0; z < n; z++)
                        open[x, z] = !RM_LandformGeometry.OnBand(x, z, rx, rz, 3.5f, gs, gs + gapLen);
                return Connected(open, 60, 0, 60, n - 1);
            }
            Check("ridge raster: an 8-cell gap leaves the two halves of the map connected", RidgeWalkable(8f));
            Check("ridge raster (planted negative): with no gap the ridge cuts the map in two", !RidgeWalkable(0f));

            // --- disc placement
            bool noOverlap = true, inside = true, vetoKept = true, capped = true;
            for (int seed = 0; seed < 200; seed++)
            {
                List<RM_Disc> ds = RM_LandformGeometry.PlaceDiscs(150, 120, 12, 1, 4, 6, 3, new Random(seed), (x, z, r) => x > 20);
                if (ds.Count > 12) capped = false;
                for (int i = 0; i < ds.Count; i++)
                {
                    RM_Disc a = ds[i];
                    if (a.x - a.r < 6 || a.z - a.r < 6 || a.x + a.r > 150 - 1 - 6 || a.z + a.r > 120 - 1 - 6) inside = false;
                    if (a.x <= 20) vetoKept = false;
                    for (int j = i + 1; j < ds.Count; j++)
                    {
                        RM_Disc b = ds[j];
                        int need = a.r + b.r + 3;
                        if ((a.x - b.x) * (a.x - b.x) + (a.z - b.z) * (a.z - b.z) < need * need) noOverlap = false;
                    }
                }
            }
            Check("discs never overlap (spacing kept) over 200 seeds", noOverlap);
            Check("discs stay inside the margin over 200 seeds", inside);
            Check("discs honour the veto (no centre at x <= 20)", vetoKept);
            Check("discs never exceed the requested count", capped);
            List<RM_Disc> d1 = RM_LandformGeometry.PlaceDiscs(150, 120, 12, 1, 4, 6, 3, new Random(7));
            List<RM_Disc> d2 = RM_LandformGeometry.PlaceDiscs(150, 120, 12, 1, 4, 6, 3, new Random(7));
            bool same = d1.Count == d2.Count;
            for (int i = 0; same && i < d1.Count; i++) same = d1[i].x == d2[i].x && d1[i].z == d2[i].z && d1[i].r == d2[i].r;
            Check("disc placement is deterministic for one seed", same && d1.Count > 0);
            Check("a map too small for any disc returns none", RM_LandformGeometry.PlaceDiscs(10, 10, 5, 4, 4, 6, 3, new Random(1)).Count == 0);

            // --- tide
            Check("tide: low at tick 0", Near(RM_LandformGeometry.TideLevel(0, 60000), 0f));
            Check("tide: high at half a period", Near(RM_LandformGeometry.TideLevel(30000, 60000), 1f));
            Check("tide: low again after a full period", Near(RM_LandformGeometry.TideLevel(60000, 60000), 0f));
            Check("tide: the sea itself is never 'flooded'", !RM_LandformGeometry.TideFloods(0, 12, 1f));
            Check("tide: at high tide the reach-th cell floods and the next does not",
                RM_LandformGeometry.TideFloods(12, 12, 1f) && !RM_LandformGeometry.TideFloods(13, 12, 1f));
            Check("tide: at low tide nothing floods", !RM_LandformGeometry.TideFloods(1, 12, 0f));
            bool mono = true;
            for (int d = 1; d <= 12; d++)
                for (float lv = 0f; lv < 1f; lv += 0.05f)
                    if (RM_LandformGeometry.TideFloods(d, 12, lv) && !RM_LandformGeometry.TideFloods(d, 12, lv + 0.05f)) mono = false;
            Check("tide: a rising level never un-floods a cell", mono);
            Check("tide: reach 0 (switched off) floods nothing", !RM_LandformGeometry.TideFloods(1, 0, 1f));

            Console.WriteLine();
            Console.WriteLine("landform geometry: " + pass + " passed, " + fail + " failed");
            return fail == 0 ? 0 : 1;
        }
    }
}
