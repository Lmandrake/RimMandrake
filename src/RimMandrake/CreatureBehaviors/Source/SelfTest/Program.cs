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
// SHADE_GEAR_FAMILY_1: the parasol, shade tent and sun shield, with their
// numbers READ from the shipped EnvironmentalHazards RM_ShadeGear.xml and
// mirrak hide's bonus from LongShade's RM_LongShade_Mirrak.xml — each piece
// cuts sun heat on the kinds it is for, the shield wins under a low sun,
// nothing helps under ambient heat, and mirrak hide casts deepest.
//
// SOLAR_HEAT_EXPOSURE_1 tranche 2 (§5/§6), REAL from RM_ShadePatchGraph.cs:
// patch labelling (flecks dropped), rims, the distance-to-shade field, edges
// between patches (cost, cap, walls cut them), the dash-range math driven
// by vanilla's Heatstroke curve (bigger = further, already hot = nowhere,
// the strictness dial), and the §6 go-and-return ring.
//
// STILLSAND_SUN_FROM_LATITUDE_1: the heat kind resolved from sun elevation,
// irradiance by sin(elevation) with its far-ring floor, and the sand glare
// floor (shade on sand stays warm, a paved shade yard does not).
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

            // ── SHADE_GEAR_FAMILY_1 — numbers read from the shipped XML ──
            Dictionary<string, GearSpec> gear = null;
            float mirrakBonus = -1f;
            Case("shade gear: shipped defs found and read", () =>
            {
                gear = ReadGear(out mirrakBonus);
                Assert(gear.ContainsKey("RM_Parasol") && gear.ContainsKey("RM_ShadeTent") && gear.ContainsKey("RM_SunShield"),
                    "missing a piece; found " + string.Join(",", gear.Keys));
                Assert(gear["RM_Parasol"].mode == "wearer" && gear["RM_ShadeTent"].mode == "footprint"
                    && gear["RM_SunShield"].mode == "lee", "a piece has the wrong mode");
                Assert(mirrakBonus > 0f, "mirrak hide carries no shade-cloth bonus (" + mirrakBonus + ")");
            });

            if (gear != null)
            {
                foreach (string piece in new[] { "RM_Parasol", "RM_ShadeTent", "RM_SunShield" })
                {
                    GearSpec g = gear[piece];
                    Case(piece + ": cuts sun heat on the right kinds, nothing on ambient", () =>
                    {
                        float openO = FeltWithGear(RM_HeatKind.overhead, g, 0f);
                        float cutO = openO - FeltWithGear(RM_HeatKind.overhead, g, 0f, true);
                        float cutL = FeltWithGear(RM_HeatKind.lowSun, g, 0f) - FeltWithGear(RM_HeatKind.lowSun, g, 0f, true);
                        float cutA = FeltWithGear(RM_HeatKind.ambient, g, 0f) - FeltWithGear(RM_HeatKind.ambient, g, 0f, true);
                        Assert(cutO > 0f, "no relief under overhead sun");
                        Assert(cutL > 0f, "no relief under low sun");
                        Assert(cutA == 0f, "relief under ambient heat (" + cutA + " C)");
                        if (g.mode == "lee")
                        {
                            Assert(cutL > cutO, "the shield is not better under a low sun (low " + cutL + ", overhead " + cutO + ")");
                        }
                        else
                        {
                            Assert(cutO > cutL, piece + " is not better under an overhead sun (overhead " + cutO + ", low " + cutL + ")");
                        }
                        Console.WriteLine("  " + piece + ": felt -" + cutO.ToString("0.0") + "C overhead, -"
                            + cutL.ToString("0.0") + "C low sun, -" + cutA.ToString("0.0") + "C ambient");
                    });

                    Case(piece + ": mirrak hide casts deeper shade than plain cloth", () =>
                    {
                        foreach (RM_HeatKind k in new[] { RM_HeatKind.overhead, RM_HeatKind.lowSun })
                        {
                            float plain = RM_SunHeatMath.GearDepth(k, g.depth, 0f, g.overhead, g.lowSun);
                            float hide = RM_SunHeatMath.GearDepth(k, g.depth, mirrakBonus, g.overhead, g.lowSun);
                            Assert(hide > plain, k + ": mirrak " + hide + " not deeper than plain " + plain);
                            Assert(FeltWithGear(k, g, mirrakBonus, true) < FeltWithGear(k, g, 0f, true),
                                k + ": mirrak did not cool more than plain cloth");
                        }
                        Assert(RM_SunHeatMath.GearDepth(RM_HeatKind.ambient, g.depth, mirrakBonus, g.overhead, g.lowSun) == 0f,
                            "mirrak hide gave shade under ambient heat");
                    });
                }

                Case("parasol under overhead sun: the wearer stops gaining Heatstroke faster", () =>
                {
                    GearSpec g = gear["RM_Parasol"];
                    float open = HeatstrokeStep(FeltWithGear(RM_HeatKind.overhead, g, 0f), HumanSafeMax);
                    float under = HeatstrokeStep(FeltWithGear(RM_HeatKind.overhead, g, 0f, true), HumanSafeMax);
                    Assert(under < open, "parasol did not slow Heatstroke (" + under + " vs " + open + ")");
                });

                Case("shade tent footprint: its cells and only its cells", () =>
                {
                    const int w = 10, h = 10;
                    float[] grid = new float[w * h];
                    RM_SunHeatMath.FillRect(grid, w, h, 3, 3, 5, 5, 0.85f);
                    Assert(grid[4 * w + 4] == 0.85f && grid[3 * w + 3] == 0.85f && grid[5 * w + 5] == 0.85f, "footprint cell unshaded");
                    Assert(grid[2 * w + 4] == 0f && grid[4 * w + 6] == 0f, "tent shaded outside its footprint");
                });

                Case("sun shield lee: away from the sun, depth-scaled; parasol neighbour along the shadow", () =>
                {
                    const int w = 20, h = 20;
                    float[] grid = new float[w * h];
                    RM_SunHeatMath.CastInto(grid, w, h, 10, 10, 0f, 1f, 3f, 0.6f, 0.5f);
                    Assert(grid[11 * w + 10] == 0.5f, "lee cell not at the panel's depth (" + grid[11 * w + 10] + ")");
                    Assert(grid[9 * w + 10] == 0f, "shade on the sun side of the panel");
                    Assert(RM_SunHeatMath.AdjacentShadowCell(5, 5, 0.9f, 0.1f, out int ax, out int az) && ax == 6 && az == 5,
                        "parasol neighbour not one step along the shadow");
                    Assert(!RM_SunHeatMath.AdjacentShadowCell(5, 5, 0f, 0f, out _, out _), "neighbour chosen with no direction");
                });
            }

            // ── tranche 2: shade-patch graph, dash range, ring ──────────
            Case("patch graph: two patches across 5 sun cells, one edge at the rim-to-rim cost", () =>
            {
                // 12 x 3 strip: shade at x=0..2 and x=8..11, sun between.
                const int w = 12, h = 3;
                bool[] sh = new bool[w * h], wk = new bool[w * h];
                for (int i = 0; i < w * h; i++) { wk[i] = true; int x = i % w; sh[i] = x <= 2 || x >= 8; }
                var g = RM_ShadePatchGraph.Build(w, h, sh, wk, 400, 2);
                Assert(g.PatchCount == 2, "patches " + g.PatchCount);
                Assert(g.EdgeCount == 1, "edges " + g.EdgeCount);
                var e = g.patches[g.patchOf[0]].edges[0];
                Assert(e.cost == 60, "hop cost " + e.cost + ", expected 6 cardinal steps = 60");
                Assert(e.fromCell % w == 2 && e.toCell % w == 8, "hop does not run rim to rim (" + e.fromCell % w + " -> " + e.toCell % w + ")");
                Assert(g.distToShade[1 * w + 5] == 30 && g.distToShade[1 * w + 1] == 0, "distance field wrong");
                Assert(g.patches[0].rim.Count == 3 && g.patches[1].rim.Count == 3, "rim is not the sun-facing column");
            });

            Case("patch graph: the cap cuts a long hop; a wall cuts any hop", () =>
            {
                const int w = 30, h = 3;
                bool[] sh = new bool[w * h], wk = new bool[w * h];
                for (int i = 0; i < w * h; i++) { wk[i] = true; int x = i % w; sh[i] = x == 0 || x == 29; }
                Assert(RM_ShadePatchGraph.Build(w, h, sh, wk, 200, 1).EdgeCount == 0, "a 28-cell hop passed a 20-cell cap");
                Assert(RM_ShadePatchGraph.Build(w, h, sh, wk, 400, 1).EdgeCount == 1, "a 28-cell hop failed a 40-cell cap");
                for (int z = 0; z < h; z++) wk[z * w + 15] = false;
                var walled = RM_ShadePatchGraph.Build(w, h, sh, wk, 400, 1);
                Assert(walled.EdgeCount == 0, "a hop went through a wall");
                Assert(walled.distToShade[1 * w + 20] == 90, "distance leaked through the wall (" + walled.distToShade[1 * w + 20] + ")");
            });

            Case("patch graph: flecks under minPatchCells are open sun", () =>
            {
                const int w = 10, h = 10;
                bool[] sh = new bool[w * h], wk = new bool[w * h];
                for (int i = 0; i < w * h; i++) wk[i] = true;
                sh[5 * w + 5] = true;                          // a one-cell fleck
                for (int x = 0; x < 3; x++) sh[0 * w + x] = true; // a 3-cell patch
                var g = RM_ShadePatchGraph.Build(w, h, sh, wk, 400, 2);
                Assert(g.PatchCount == 1, "fleck counted as a patch");
                Assert(g.patchOf[5 * w + 5] == RM_ShadePatchGraph.NoPatch && g.distToShade[5 * w + 5] > 0, "fleck cell is shade");
            });

            Case("patch graph: diagonal steps cost 14, and every edge is symmetric", () =>
            {
                const int w = 9, h = 9;
                bool[] sh = new bool[w * h], wk = new bool[w * h];
                for (int i = 0; i < w * h; i++) wk[i] = true;
                sh[0] = sh[1] = sh[w] = sh[w + 1] = true;                       // 2x2 at a corner
                sh[8 * w + 8] = sh[8 * w + 7] = sh[7 * w + 8] = sh[7 * w + 7] = true; // 2x2 at the far corner
                var g = RM_ShadePatchGraph.Build(w, h, sh, wk, 400, 2);
                Assert(g.EdgeCount == 1, "edges " + g.EdgeCount);
                var a0 = g.patches[0].edges[0]; var b0 = g.patches[1].edges[0];
                Assert(a0.cost == 6 * 14 && b0.cost == a0.cost, "diagonal hop cost " + a0.cost + " / " + b0.cost);
                Assert(a0.fromCell == b0.toCell && a0.toCell == b0.fromCell, "edge ends are not mirrored");
            });

            Case("dash range: bigger animals dash further, a hot one goes nowhere, cool = the cap", () =>
            {
                // Outdoor 30 C, safe max 40 C (an animal whose comfortable max is 30).
                Func<float, float, int> range = (bodySize, alreadyHot) =>
                {
                    float f = RM_SunHeatMath.BodySizeFactor(bodySize, 0.5f, 0.25f, 2.5f);
                    float felt = 30f + RM_SunHeatMath.HeatOffset(1f, 30f, 1f, f, 70f);
                    float curved = HediffGiver_Heat.TemperatureOverageAdjustmentCurve.Evaluate(Math.Max(0f, felt - 40f));
                    int ticks = RM_DashMath.ToleratedTicks(felt, 40f, curved, 0.012f - alreadyHot);
                    // Ticks per cell rise as size falls: 10 at size 1, like a smallish animal.
                    float tpc = RM_DashMath.TicksPerCell(10f / (float)Math.Sqrt(Math.Max(0.2f, bodySize)), 0.75f);
                    return RM_DashMath.DashRangeCost(ticks, tpc, 1f, 3f, 40f);
                };
                int small = range(0.3f, 0f), mid = range(1f, 0f), big = range(3f, 0f);
                Console.WriteLine("  dash range, cells: size 0.3 = " + small / 10f + ", size 1 = " + mid / 10f + ", size 3 = " + big / 10f);
                Assert(small < mid && mid <= big, "range not rising with size: " + small + " " + mid + " " + big);
                Assert(small >= 30 && big <= 400, "range escaped its [3, 40] cell clamp");
                Assert(range(1f, 0.02f) == 0, "an animal past its heatstroke budget still dashes");
                Assert(RM_DashMath.ToleratedTicks(35f, 40f, 0f, 0.012f) == int.MaxValue, "a cool sun limited the dash");
                Assert(RM_DashMath.DashRangeCost(int.MaxValue, 7.5f, 1f, 3f, 40f) == 400, "cool sun did not give the cap");
            });

            Case("dash range: the strictness dial scales it, and the step matches vanilla's heat giver", () =>
            {
                int full = RM_DashMath.DashRangeCost(1200, 10f, 1f, 3f, 40f);
                int half = RM_DashMath.DashRangeCost(1200, 10f, 0.5f, 3f, 40f);
                Assert(full == 400, "1200 ticks at 10/cell is 120 cells, clamped to 40 (" + full + ")");
                Assert(RM_DashMath.DashRangeCost(200, 10f, 1f, 3f, 40f) == 200 && RM_DashMath.DashRangeCost(200, 10f, 0.5f, 3f, 40f) == 100,
                    "dial did not halve a 20-cell dash");
                Assert(half <= full, "a stricter dial dashed further");
                Assert(RM_DashMath.DashRangeCost(10, 10f, 1f, 3f, 40f) == 30, "min clamp not applied");
                Assert(Math.Abs(RM_DashMath.SeverityPerInterval(0f) - 0.000375f) < 1e-9f, "floor step is not vanilla's 0.000375");
                Assert(Math.Abs(RM_DashMath.SeverityPerInterval(25f) - 25f * 6.45E-05f) < 1e-9f, "step is not curve x 6.45e-5");
                Assert(RM_DashMath.ToleratedTicks(60f, 40f, 20f, 0f) == 0, "no budget still tolerated sun");
            });

            Case("ring: from shade, reach a sun cell only if there and back fits the range", () =>
            {
                // 41 x 1 corridor: shade at x=0, sun beyond. From x=0 with a
                // 100 range (10 cells), the reachable sun cells are x <= 5.
                const int w = 41, h = 1;
                bool[] sh = new bool[w * h], wk = new bool[w * h];
                for (int i = 0; i < w; i++) wk[i] = true;
                sh[0] = true;
                var g = RM_ShadePatchGraph.Build(w, h, sh, wk, 600, 1);
                var cells = new List<int>();
                g.ReachableWithReturn(0, 100, cells);
                int far = 0; foreach (int c in cells) far = Math.Max(far, c);
                Assert(cells.Contains(5) && !cells.Contains(6) && far == 5, "ring edge at x=" + far + ", expected 5");
                // A pawn standing out at x=4 has used its outbound leg already.
                g.ReachableWithReturn(4, 100, cells);
                Assert(cells.Contains(0) && cells.Contains(5) && !cells.Contains(8), "ring from x=4 wrong");
                g.ReachableWithReturn(0, 0, cells);
                Assert(cells.Count == 0, "no budget still drew a ring");
            });

            // ── STILLSAND_SUN_FROM_LATITUDE_1 ───────────────────────────
            Case("stillsand: cover follows the sun angle (overhead at/above threshold, lowSun below)", () =>
            {
                Assert(RM_SunHeatMath.KindFromElevation(RM_HeatKind.lowSun, 70f, 55f) == RM_HeatKind.overhead, "70 deg not overhead");
                Assert(RM_SunHeatMath.KindFromElevation(RM_HeatKind.lowSun, 55f, 55f) == RM_HeatKind.overhead, "55 deg not overhead");
                Assert(RM_SunHeatMath.KindFromElevation(RM_HeatKind.lowSun, 40f, 55f) == RM_HeatKind.lowSun, "40 deg not lowSun");
                Assert(RM_SunHeatMath.KindFromElevation(RM_HeatKind.overhead, 40f, 55f) == RM_HeatKind.lowSun, "base overhead at 40 not lowSun");
                Assert(RM_SunHeatMath.KindFromElevation(RM_HeatKind.ambient, 80f, 55f) == RM_HeatKind.ambient, "ambient changed by angle");
                Assert(RM_SunHeatMath.KindFromElevation(RM_HeatKind.lowSun, 80f, -1f) == RM_HeatKind.lowSun, "threshold off still switched");
                Assert(RM_SunHeatMath.KindFromElevation(RM_HeatKind.lowSun, float.NaN, 55f) == RM_HeatKind.lowSun, "unknown elevation switched");
            });

            Case("stillsand: above the threshold a roof protects, below it only a lee does", () =>
            {
                RM_HeatKind high = RM_SunHeatMath.KindFromElevation(RM_HeatKind.lowSun, 75f, 55f);
                RM_HeatKind low = RM_SunHeatMath.KindFromElevation(RM_HeatKind.lowSun, 35f, 55f);
                Assert(RM_SunHeatMath.Exposure(high, true, 1f, false, 0f) == 0f, "roof gave no cover under a high sun");
                Assert(RM_SunHeatMath.Exposure(low, true, 1f, false, 0f) == 1f, "roof still covered under a low sun");
                Assert(RM_SunHeatMath.Exposure(low, true, 0f, false, 1f) == 0f, "lee gave no cover under a low sun");
            });

            Case("stillsand: irradiance scales with sin(elevation), floored at the far ring", () =>
            {
                Assert(Math.Abs(RM_SunHeatMath.ElevationHeatOffset(55f, 90f, 35f) - 55f) < 0.01f, "zenith not 55");
                float at40 = RM_SunHeatMath.ElevationHeatOffset(55f, 40f, 0f);
                Assert(Math.Abs(at40 - 35.35f) < 0.1f, "40 deg gave " + at40 + ", expected ~35.4");
                Assert(RM_SunHeatMath.ElevationHeatOffset(55f, 10f, 35f) == 35f, "floor not applied low");
                Assert(RM_SunHeatMath.ElevationHeatOffset(55f, 60f, 35f) > RM_SunHeatMath.ElevationHeatOffset(55f, 45f, 35f), "not monotone");
                Assert(RM_SunHeatMath.ElevationHeatOffset(55f, float.NaN, 35f) == 55f, "NaN elevation not passthrough");
            });

            Case("stillsand: sand glare floors exposure in shade; paved shade is fully cool", () =>
            {
                float shadeOnSand = RM_SunHeatMath.WithGlareFloor(RM_SunHeatMath.Exposure(RM_HeatKind.lowSun, true, 0f, false, 1f), 0.35f);
                float shadeOnPaving = RM_SunHeatMath.WithGlareFloor(RM_SunHeatMath.Exposure(RM_HeatKind.lowSun, true, 0f, false, 1f), 0f);
                float sunOnSand = RM_SunHeatMath.WithGlareFloor(1f, 0.35f);
                Assert(Math.Abs(shadeOnSand - 0.35f) < 1e-5f, "sand shade exposure " + shadeOnSand);
                Assert(shadeOnPaving == 0f, "paved shade exposure " + shadeOnPaving);
                Assert(sunOnSand == 1f, "glare lowered full sun");
                // A parasol cannot beat glare either (cover, then the floor).
                float parasol = RM_SunHeatMath.WithGlareFloor(RM_SunHeatMath.WithCover(1f, 0.9f), 0.35f);
                Assert(Math.Abs(parasol - 0.35f) < 1e-5f, "parasol beat the glare floor: " + parasol);
                float felt = OutdoorC + RM_SunHeatMath.HeatOffset(shadeOnSand, 35f, 1f, 1f, 70f);
                float paved = OutdoorC + RM_SunHeatMath.HeatOffset(shadeOnPaving, 35f, 1f, 1f, 70f);
                Assert(HeatstrokeStep(felt, HumanSafeMax) > HeatstrokeStep(paved, HumanSafeMax), "sand shade no hotter than a shade yard");
            });

            Case("stillsand: shadow length differs by latitude (cot of elevation)", () =>
            {
                float lph70 = (float)(1.0 / Math.Tan(70 * Math.PI / 180));
                float lph40 = (float)(1.0 / Math.Tan(40 * Math.PI / 180));
                float l70 = RM_SunHeatMath.ShadowLength(1f, lph70, 16f);
                float l40 = RM_SunHeatMath.ShadowLength(1f, lph40, 16f);
                Assert(l40 > l70 * 2f, "40 deg shadow " + l40 + " not much longer than 70 deg " + l70);
            });

            // ── STILLSAND_GLARE_BLIND_GOGGLES_1 ─────────────────────────
            Case("glare-blind: full sun blinds, sand shade and protected eyes do not (shipped numbers)", () =>
            {
                string root = FindModsRoot();
                var biome = new System.Xml.XmlDocument();
                biome.Load(System.IO.Path.Combine(root, "Stillsand", "Defs", "BiomeDefs", "RM_Stillsand_Biome.xml"));
                System.Xml.XmlNode ext = biome.SelectSingleNode("//li[contains(@Class,'RM_SunHeatExtension')]");
                Assert(ext != null, "Stillsand has no RM_SunHeatExtension");
                Assert(ext.SelectSingleNode("glareBlindHediff")?.InnerText == "RM_GlareBlind", "Stillsand does not name RM_GlareBlind");
                float min = F(ext, "glareBlindExposureMin", 0.6f);
                float perDay = F(ext, "glareBlindSeverityPerDay", 4f);
                float floor = F(ext, "sandGlareExposureFloor", 0f);
                var hd = new System.Xml.XmlDocument();
                hd.Load(System.IO.Path.Combine(root, "CreatureBehaviors", "Defs", "HediffDefs", "RM_GlareBlind_Hediffs.xml"));
                float decay = F(hd.SelectSingleNode("//HediffDef[defName='RM_GlareBlind']/comps/li[@Class='HediffCompProperties_SeverityPerDay']"), "severityPerDay", 0f);
                Assert(decay < 0f, "RM_GlareBlind has no recovery");
                int iv = 250;
                float sun = RM_SunHeatMath.GlareBlindGain(1f, min, perDay, 1f, iv, false);
                float netPerDay = sun * 60000f / iv + decay;
                Assert(netPerDay > 0f, "full glare nets " + netPerDay + "/day, never blinds");
                Assert(RM_SunHeatMath.GlareBlindGain(RM_SunHeatMath.WithGlareFloor(0f, floor), min, perDay, 1f, iv, false) == 0f, "shade on sand blinds");
                Assert(RM_SunHeatMath.GlareBlindGain(1f, min, perDay, 1f, iv, true) == 0f, "protected eyes blinded");
                Assert(RM_SunHeatMath.GlareBlindGain(1f, min, perDay, 0f, iv, false) == 0f, "rate dial 0 still blinds");
                Console.WriteLine("  glare-blind: full glare nets +" + netPerDay.ToString("0.00") + "/day; reaches 0.35 in "
                    + (0.35f / netPerDay * 24f).ToString("0.0") + " h; clears at " + (-decay).ToString("0.0") + "/day");
            });

            Case("glare-blind: immunity is a gene on the Jawa, goggles carry the tag", () =>
            {
                string root = FindModsRoot();
                var gene = new System.Xml.XmlDocument();
                gene.Load(System.IO.Path.Combine(root, "CreatureBehaviors", "Defs", "GeneDefs", "RM_GlareAdapted.xml"));
                Assert(gene.SelectSingleNode("//GeneDef[defName='RM_GlareAdapted']/modExtensions/li[contains(@Class,'RM_GlareProtectionExtension')]") != null, "gene lacks the protection extension");
                var jawa = new System.Xml.XmlDocument();
                jawa.Load(System.IO.Path.Combine(root, "..", "RimStarWars", "StarWarsRaces", "Patches", "RSW_Jawa_GlareAdapted.xml"));
                System.Xml.XmlNode op = jawa.SelectSingleNode("//match[contains(xpath,'RSW_RimMandrakeJawa')]");
                Assert(op != null && op.SelectSingleNode("value/li")?.InnerText == "RM_GlareAdapted", "Jawa patch does not add RM_GlareAdapted");
                var gog = new System.Xml.XmlDocument();
                gog.Load(System.IO.Path.Combine(root, "Stillsand", "Defs", "ThingDefs_Apparel", "RM_SunGoggles.xml"));
                Assert(gog.SelectSingleNode("//ThingDef[defName='RM_SunGoggles']/apparel/tags/li[.='" + "RM_GlareProtection" + "']") != null, "goggles lack the tag");
                Assert(gog.SelectSingleNode("//ThingDef[defName='RM_SunGoggles']/apparel/layers/li[.='EyeCover']") != null, "goggles not eyes-layer");
            });

            // ── STILLSAND_MIRAGE_CONDITION_1 ────────────────────────────
            Case("mirage: held only at/above the sun threshold", () =>
            {
                Assert(RM_SunHeatMath.MirageActive(60f, 45f), "60 deg no mirage");
                Assert(RM_SunHeatMath.MirageActive(45f, 45f), "45 deg no mirage");
                Assert(!RM_SunHeatMath.MirageActive(30f, 45f), "30 deg mirage");
                Assert(!RM_SunHeatMath.MirageActive(float.NaN, 45f), "unknown sun mirage");
                Assert(!RM_SunHeatMath.MirageActive(80f, -1f), "threshold off still mirage");
            });

            Case("mirage: the band lies on the sun-ward edge, opposite the shadows", () =>
            {
                // Shadow vector = -(sin b, cos b) for sun bearing b from north.
                Assert(RM_SunHeatMath.MirageEdge(0f, -1f) == 0, "sun north -> not north edge");
                Assert(RM_SunHeatMath.MirageEdge(-1f, 0f) == 1, "sun east -> not east edge");
                Assert(RM_SunHeatMath.MirageEdge(0f, 1f) == 2, "sun south -> not south edge");
                Assert(RM_SunHeatMath.MirageEdge(1f, 0f) == 3, "sun west -> not west edge");
                Assert(RM_SunHeatMath.MirageEdge(-0.9f, -0.4f) == 1, "sun ENE -> not east edge");
                Assert(RM_SunHeatMath.MirageEdge(0f, 0f) == 0, "no direction -> not north");
            });

            Case("mirage: heat shimmer cuts accuracy only in full sun (shipped factors)", () =>
            {
                string root = FindModsRoot();
                var patch = new System.Xml.XmlDocument();
                patch.Load(System.IO.Path.Combine(root, "CreatureBehaviors", "Patches", "RM_Mirage_ThinkTree.xml"));
                System.Xml.XmlNode lng = patch.SelectSingleNode("//Operation[contains(xpath,'ShootingAccuracyFactor_Long')]/nomatch/value/parts/li");
                System.Xml.XmlNode med = patch.SelectSingleNode("//Operation[contains(xpath,'ShootingAccuracyFactor_Medium')]/nomatch/value/parts/li");
                Assert(lng != null && med != null, "shimmer stat parts not patched on Medium and Long");
                float fl = F(lng, "factor", 1f), fm = F(med, "factor", 1f);
                Assert(fl < fm && fm < 1f, "long " + fl + " not harsher than medium " + fm);
                Assert(RM_SunHeatMath.MirageShimmerFactor(1f, 0.6f, fl) == fl, "full sun not cut");
                Assert(RM_SunHeatMath.MirageShimmerFactor(0.35f, 0.6f, fl) == 1f, "sand shade cut");
                var biome = new System.Xml.XmlDocument();
                biome.Load(System.IO.Path.Combine(root, "Stillsand", "Defs", "BiomeDefs", "RM_Stillsand_Biome.xml"));
                System.Xml.XmlNode ext = biome.SelectSingleNode("//li[contains(@Class,'RM_SunHeatExtension')]");
                Assert(ext.SelectSingleNode("mirageCondition")?.InnerText == "RM_Mirage", "Stillsand does not name RM_Mirage");
                Assert(ext.SelectSingleNode("mirageMentalState")?.InnerText == "RM_ChasingWater", "Stillsand does not name RM_ChasingWater");
                var think = patch.SelectSingleNode("//Operation[contains(xpath,'MentalStateNonCritical')]");
                Assert(think != null && think.SelectSingleNode("order")?.InnerText == "Prepend"
                       && think.SelectSingleNode("value/li/state")?.InnerText == "RM_ChasingWater", "think-tree node missing");
            });

            foreach (string p in Pass) Console.WriteLine("PASS " + p);
            foreach (string f in Fail) Console.WriteLine("FAIL " + f);
            Console.WriteLine(Pass.Count + "/" + (Pass.Count + Fail.Count) + " passed");
            return Fail.Count == 0 ? 0 : 1;
        }

        private sealed class GearSpec
        {
            public string mode;
            public float depth, overhead, lowSun;
        }

        /// <summary>Felt temperature on an open, unroofed cell, optionally
        /// with the piece in use: worn (parasol), stood under (tent), or stood
        /// in the lee cell one step behind the panel (shield) — each through
        /// the same RM_SunHeatMath calls RM_MapComponent_ShadeGrid makes.</summary>
        private static float FeltWithGear(RM_HeatKind kind, GearSpec g, float stuffBonus, bool withGear = false)
        {
            float ex = RM_SunHeatMath.Exposure(kind, true, 0f, false, 0f);
            if (withGear)
            {
                float d = RM_SunHeatMath.GearDepth(kind, g.depth, stuffBonus, g.overhead, g.lowSun);
                if (g.mode == "wearer")
                {
                    ex = RM_SunHeatMath.WithCover(ex, d);
                }
                else if (g.mode == "footprint")
                {
                    float[] t = new float[9];
                    RM_SunHeatMath.FillRect(t, 3, 3, 0, 0, 2, 2, d);
                    ex = RM_SunHeatMath.Exposure(kind, true, 0f, false, 0f, t[4]);
                }
                else
                {
                    float[] t = new float[5 * 5];
                    RM_SunHeatMath.CastInto(t, 5, 5, 2, 1, 0f, 1f, 3f, 0.6f, d);
                    ex = RM_SunHeatMath.Exposure(kind, true, 0f, false, 0f, t[2 * 5 + 2]);
                }
            }
            return OutdoorC + RM_SunHeatMath.HeatOffset(ex, 30f, 1f, 1f, 70f);
        }

        private static string FindModsRoot()
        {
            string dir = AppDomain.CurrentDomain.BaseDirectory;
            while (!string.IsNullOrEmpty(dir))
            {
                string cand = System.IO.Path.Combine(dir, "src", "RimMandrake");
                if (System.IO.Directory.Exists(System.IO.Path.Combine(cand, "EnvironmentalHazards")))
                {
                    return cand;
                }
                dir = System.IO.Path.GetDirectoryName(dir.TrimEnd('\\', '/'));
            }
            throw new Exception("src/RimMandrake not found above " + AppDomain.CurrentDomain.BaseDirectory);
        }

        private static float F(System.Xml.XmlNode n, string name, float dflt)
        {
            System.Xml.XmlNode c = n.SelectSingleNode(name);
            return c == null ? dflt : float.Parse(c.InnerText, System.Globalization.CultureInfo.InvariantCulture);
        }

        /// <summary>The three pieces' RM_CompProperties_ShadeGear, and mirrak
        /// hide's shadeBonus, read from the shipped def files.</summary>
        private static Dictionary<string, GearSpec> ReadGear(out float mirrakBonus)
        {
            string root = FindModsRoot();
            var doc = new System.Xml.XmlDocument();
            doc.Load(System.IO.Path.Combine(root, "EnvironmentalHazards", "Defs", "ThingDefs_Buildings", "RM_ShadeGear.xml"));
            var result = new Dictionary<string, GearSpec>();
            foreach (System.Xml.XmlNode def in doc.SelectNodes("/Defs/ThingDef"))
            {
                System.Xml.XmlNode comp = def.SelectSingleNode("comps/li[contains(@Class,'RM_CompProperties_ShadeGear')]");
                if (comp == null)
                {
                    continue;
                }
                // Defaults mirror RM_CompProperties_ShadeGear's field initialisers.
                result[def.SelectSingleNode("defName").InnerText] = new GearSpec
                {
                    mode = comp.SelectSingleNode("mode")?.InnerText ?? "footprint",
                    depth = F(comp, "shadeDepth", 0.8f),
                    overhead = F(comp, "overheadFactor", 1f),
                    lowSun = F(comp, "lowSunFactor", 0.3f),
                };
            }
            var hide = new System.Xml.XmlDocument();
            hide.Load(System.IO.Path.Combine(root, "LongShade", "Defs", "ThingDefs_Races", "RM_LongShade_Mirrak.xml"));
            System.Xml.XmlNode ext = hide.SelectSingleNode(
                "/Defs/ThingDef[defName='RM_Leather_Mirrak']/modExtensions/li[contains(@Class,'RM_ShadeClothExtension')]");
            mirrakBonus = ext == null ? -1f : F(ext, "shadeBonus", 0.25f);
            return result;
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
