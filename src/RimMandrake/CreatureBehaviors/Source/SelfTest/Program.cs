// Selftest for SOLAR_HEAT_EXPOSURE_1 (sun heat, mandrake.rm.creaturebehaviors).
//
// REAL, compiled straight from production source: RM_SunHeatMath — the
// exposure rule for each heat kind, the body-size factor, the felt-heat
// offset, the per-cell path cost and the directional shadow cast. Every live
// caller (RM_MapComponent_ShadeGrid, RM_SunHeatPatches) goes through it.
//
// REAL, read from Assembly-CSharp: vanilla HediffGiver_Heat's
// TemperatureOverageAdjustmentCurve. The per-interval severity step below is
// a transcription of HediffGiver_Heat.OnIntervalPassed (decompiled 1.6, via
// RimSage): over the safe max, max(curve(over) × 6.45e-5, 0.000375). That is
// the vanilla Heatstroke path sun heat feeds, so "sun vs shade vs roofed"
// is asserted as the Heatstroke gain each actually produces.
//
// NOT covered, and why: anything that needs a live Map — the room test
// (UsesOutdoorTemperature), roof/thing scans, the Harmony postfixes and the
// NativeArray customizer. Those are the quicktest criteria on the item.
//
// Run:
//   "%USERPROFILE%\.dotnet\dotnet.exe" run --project D:\Luke\dev\Rimworld\src\RimMandrake\CreatureBehaviors\Source\SelfTest\RimMandrakeCreatureBehaviors.SunHeat.SelfTest.csproj -c Release

using System;
using System.Collections.Generic;
using Verse;

namespace RimMandrake.CreatureBehaviors.SelfTest
{
    internal static class Program
    {
        private static readonly List<string> Pass = new List<string>();
        private static readonly List<string> Fail = new List<string>();

        // A human's vanilla comfortable max is 26 °C; SafeTemperatureRange
        // widens the comfortable range by 10 each side.
        private const float HumanSafeMax = 36f;
        private const float OutdoorC = 30f;

        private static void Case(string name, Action fn)
        {
            try
            {
                fn();
                Pass.Add(name);
            }
            catch (Exception ex)
            {
                Fail.Add(name + ": " + ex.Message);
            }
        }

        private static void Assert(bool cond, string msg)
        {
            if (!cond)
            {
                throw new Exception(msg);
            }
        }

        /// <summary>Heatstroke severity added per HediffGiver interval at felt
        /// temperature t (transcribed from HediffGiver_Heat.OnIntervalPassed).</summary>
        private static float HeatstrokeStep(float feltC, float safeMax)
        {
            if (feltC <= safeMax)
            {
                return 0f;
            }
            float x = HediffGiver_Heat.TemperatureOverageAdjustmentCurve.Evaluate(feltC - safeMax);
            return Math.Max(x * 6.45E-05f, 0.000375f);
        }

        private static float Felt(RM_HeatKind kind, bool outdoors, float roof, bool thick, float cast, float bodySize = 1f)
        {
            float ex = RM_SunHeatMath.Exposure(kind, outdoors, roof, thick, cast);
            float f = RM_SunHeatMath.BodySizeFactor(bodySize, 0.5f, 0.25f, 2.5f);
            return OutdoorC + RM_SunHeatMath.HeatOffset(ex, 30f, 1f, f, 70f);
        }

        private static int Main()
        {
            Case("overhead: sun heats, cast shade and a roof both protect", () =>
            {
                float sun = HeatstrokeStep(Felt(RM_HeatKind.overhead, true, 0f, false, 0f), HumanSafeMax);
                float shade = HeatstrokeStep(Felt(RM_HeatKind.overhead, true, 0f, false, 1f), HumanSafeMax);
                float roofed = HeatstrokeStep(Felt(RM_HeatKind.overhead, true, 1f, false, 0f), HumanSafeMax);
                Assert(sun > 0f, "a pawn in full sun gained no Heatstroke (" + sun + ")");
                Assert(shade == 0f, "a pawn in cast shade still gained Heatstroke (" + shade + ")");
                Assert(roofed == 0f, "a pawn under a roof still gained Heatstroke (" + roofed + ")");
            });

            Case("lowSun: only the lee shadow (or inside rock) protects, a built roof does not", () =>
            {
                float thinRoof = HeatstrokeStep(Felt(RM_HeatKind.lowSun, true, 1f, false, 0f), HumanSafeMax);
                float lee = HeatstrokeStep(Felt(RM_HeatKind.lowSun, true, 0f, false, 1f), HumanSafeMax);
                float rock = HeatstrokeStep(Felt(RM_HeatKind.lowSun, true, 1f, true, 0f), HumanSafeMax);
                Assert(thinRoof > 0f, "a built roof protected on a low-sun map");
                Assert(lee == 0f, "the lee shadow did not protect on a low-sun map");
                Assert(rock == 0f, "inside overhead rock did not protect on a low-sun map");
            });

            Case("ambient: shade and roof give no relief, an enclosed room does", () =>
            {
                float open = HeatstrokeStep(Felt(RM_HeatKind.ambient, true, 0f, false, 0f), HumanSafeMax);
                float shaded = HeatstrokeStep(Felt(RM_HeatKind.ambient, true, 1f, false, 1f), HumanSafeMax);
                float indoors = HeatstrokeStep(Felt(RM_HeatKind.ambient, false, 0f, false, 0f), HumanSafeMax);
                Assert(open > 0f && shaded == open, "shade changed ambient heat (open " + open + ", shaded " + shaded + ")");
                Assert(indoors == 0f, "an enclosed room still gained Heatstroke on an ambient map");
            });

            Case("an enclosed room is never exposed, whatever the kind", () =>
            {
                foreach (RM_HeatKind k in Enum.GetValues(typeof(RM_HeatKind)))
                {
                    Assert(RM_SunHeatMath.Exposure(k, false, 0f, false, 0f) == 0f, k + " exposed indoors");
                }
            });

            Case("body size: small heats faster, large slower, clamped", () =>
            {
                float small = RM_SunHeatMath.BodySizeFactor(0.3f, 0.5f, 0.25f, 2.5f);
                float one = RM_SunHeatMath.BodySizeFactor(1f, 0.5f, 0.25f, 2.5f);
                float big = RM_SunHeatMath.BodySizeFactor(16f, 0.5f, 0.25f, 2.5f);
                float tiny = RM_SunHeatMath.BodySizeFactor(0.01f, 0.5f, 0.25f, 2.5f);
                Assert(small > one && one > big, "factor not monotone in size: " + small + " " + one + " " + big);
                Assert(Math.Abs(one - 1f) < 1e-5f, "size 1 is not 1x");
                Assert(tiny <= 2.5f && big >= 0.25f, "factor escaped its clamp");
                float stepSmall = HeatstrokeStep(Felt(RM_HeatKind.overhead, true, 0f, false, 0f, 0.3f), HumanSafeMax);
                float stepBig = HeatstrokeStep(Felt(RM_HeatKind.overhead, true, 0f, false, 0f, 4f), HumanSafeMax);
                Assert(stepSmall > stepBig, "a small pawn does not reach heatstroke sooner than a big one");
            });

            Case("heat offset: zero exposure or strength adds nothing; the cap holds", () =>
            {
                Assert(RM_SunHeatMath.HeatOffset(0f, 30f, 1f, 1f, 70f) == 0f, "shade added heat");
                Assert(RM_SunHeatMath.HeatOffset(1f, 30f, 0f, 1f, 70f) == 0f, "strength 0 added heat");
                Assert(RM_SunHeatMath.HeatOffset(1f, 30f, 3f, 2.5f, 70f) == 70f, "cap not applied");
            });

            Case("path cost: sun cells cost, shade is free, never impassable", () =>
            {
                Assert(RM_SunHeatMath.PathCost(0f, 20f, 1f) == 0, "shade cell has a cost");
                Assert(RM_SunHeatMath.PathCost(1f, 20f, 1f) == 20, "full-sun cell cost is not 20");
                Assert(RM_SunHeatMath.PathCost(1f, 1e9f, 3f) < RM_SunHeatMath.ImpassableCustomCost, "sun cost reached impassable");
                Assert(RM_SunHeatMath.PathCost(1f, 20f, 0f) == 0, "path dial 0 still costs");
            });

            Case("path cost: a route goes shade-to-shade when the detour is short", () =>
            {
                // 21 × 5 grid. Row z=2 is open sun; row z=0 is a shaded lee strip.
                // Start (0,2) -> goal (20,2). Straight = 20 sun cells; the detour
                // drops two rows into the shade and back.
                const int w = 21, h = 5;
                float[] shade = new float[w * h];
                for (int x = 0; x < w; x++) { shade[0 * w + x] = 1f; shade[1 * w + x] = 1f; }
                ushort[] cost = new ushort[w * h];
                for (int i = 0; i < cost.Length; i++)
                {
                    float ex = RM_SunHeatMath.Exposure(RM_HeatKind.overhead, true, 0f, false, shade[i]);
                    cost[i] = RM_SunHeatMath.PathCost(ex, 20f, 1f);
                }
                List<int> path = Dijkstra(w, h, cost, 0 + 2 * w, 20 + 2 * w);
                int sunCells = 0;
                foreach (int i in path) { if (shade[i] < 0.5f) sunCells++; }
                Assert(sunCells <= 4, "path crossed " + sunCells + " sun cells; expected it to hug the shade");
                List<int> flat = Dijkstra(w, h, new ushort[w * h], 0 + 2 * w, 20 + 2 * w);
                int flatSun = 0;
                foreach (int i in flat) { if (shade[i] < 0.5f) flatSun++; }
                Assert(flatSun > sunCells, "without sun cost the path was not the straight sunny one");
            });

            Case("directional cast: a strip along the sun vector, nothing behind or beside", () =>
            {
                const int w = 30, h = 30;
                float[] g = new float[w * h];
                float len = RM_SunHeatMath.ShadowLength(1f, 4f, 16f);
                Assert(Math.Abs(len - 4f) < 1e-5f, "a height-1 caster at cot 4 did not throw 4 cells");
                RM_SunHeatMath.CastInto(g, w, h, 10, 10, 1f, 0f, len, 0.6f);
                for (int x = 11; x <= 14; x++)
                {
                    Assert(g[10 * w + x] >= 0.6f, "cell (" + x + ",10) in the shadow is lit");
                }
                Assert(g[10 * w + 13] == 1f, "body of the shadow is not full shade");
                Assert(g[10 * w + 10] == 0f, "the caster's own cell was shaded");
                Assert(g[10 * w + 9] == 0f, "shade fell on the sun side");
                Assert(g[11 * w + 11] == 0f && g[9 * w + 11] == 0f, "shade spread sideways like the old ring");
                Assert(g[10 * w + 16] == 0f, "shadow ran past its length");
                RM_SunHeatMath.ShadowLength(1f, 100f, 16f);
                Assert(RM_SunHeatMath.ShadowLength(1f, 100f, 16f) == 16f, "shadow length cap not applied");
            });

            Case("directional cast: a diagonal shadow has no gaps", () =>
            {
                const int w = 30, h = 30;
                float[] g = new float[w * h];
                float d = (float)(1.0 / Math.Sqrt(2.0));
                RM_SunHeatMath.CastInto(g, w, h, 5, 5, d, d, 6f, 0.6f);
                for (int k = 1; k <= 4; k++)
                {
                    Assert(g[(5 + k) * w + (5 + k)] > 0f, "diagonal gap at step " + k);
                }
            });

            Case("directional cast: overlapping shadows never lighten each other", () =>
            {
                const int w = 20, h = 5;
                float[] g = new float[w * h];
                RM_SunHeatMath.CastInto(g, w, h, 2, 2, 1f, 0f, 8f, 0.6f);
                float before = g[2 * w + 9];
                Assert(before > 0.6f, "long shadow did not reach x=9");
                RM_SunHeatMath.CastInto(g, w, h, 8, 2, 1f, 0f, 1f, 0.1f);
                Assert(g[2 * w + 9] == before, "a short shadow's faint tip lightened a long shadow ("
                    + before + " -> " + g[2 * w + 9] + ")");
            });

            foreach (string p in Pass) Console.WriteLine("PASS " + p);
            foreach (string f in Fail) Console.WriteLine("FAIL " + f);
            Console.WriteLine(Pass.Count + "/" + (Pass.Count + Fail.Count) + " passed");
            return Fail.Count == 0 ? 0 : 1;
        }

        /// <summary>8-connected Dijkstra with vanilla step costs (13 cardinal,
        /// 18 diagonal) plus the custom offset of the cell entered — the same
        /// addition PathGridJob makes.</summary>
        private static List<int> Dijkstra(int w, int h, ushort[] custom, int start, int goal)
        {
            int n = w * h;
            int[] dist = new int[n];
            int[] prev = new int[n];
            bool[] done = new bool[n];
            for (int i = 0; i < n; i++) { dist[i] = int.MaxValue; prev[i] = -1; }
            dist[start] = 0;
            for (int iter = 0; iter < n; iter++)
            {
                int u = -1;
                for (int i = 0; i < n; i++)
                {
                    if (!done[i] && dist[i] != int.MaxValue && (u < 0 || dist[i] < dist[u])) u = i;
                }
                if (u < 0 || u == goal) break;
                done[u] = true;
                int ux = u % w, uz = u / w;
                for (int dz = -1; dz <= 1; dz++)
                {
                    for (int dx = -1; dx <= 1; dx++)
                    {
                        if (dx == 0 && dz == 0) continue;
                        int vx = ux + dx, vz = uz + dz;
                        if (vx < 0 || vz < 0 || vx >= w || vz >= h) continue;
                        int v = vz * w + vx;
                        int step = (dx != 0 && dz != 0 ? 18 : 13) + custom[v];
                        if (dist[u] + step < dist[v]) { dist[v] = dist[u] + step; prev[v] = u; }
                    }
                }
            }
            List<int> path = new List<int>();
            for (int c = goal; c >= 0; c = prev[c]) path.Add(c);
            path.Reverse();
            return path;
        }
    }
}
