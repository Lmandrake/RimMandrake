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
// SHADE_GEAR_FAMILY_1: the parasol and shade tent, with their numbers READ
// from the shipped EnvironmentalHazards RM_ShadeGear.xml and mirrak hide's
// bonus from LongShade's RM_LongShade_Mirrak.xml — each piece cuts Direct Sun
// at every sun elevation, and mirrak hide casts deepest. The sun shield is
// gone (DIRECT_SUN_UNIFY_GEOMETRY_ALONE_DECIDES spec 5).
//
// SOLAR_HEAT_EXPOSURE_1 tranche 2 (§5/§6), REAL from RM_ShadePatchGraph.cs:
// patch labelling (flecks dropped), rims, the distance-to-shade field, edges
// between patches (cost, cap, walls cut them), the dash-range math driven
// by vanilla's Heatstroke curve (bigger = further, already hot = nowhere,
// the strictness dial), and the §6 go-and-return ring.
//
// DIRECT_SUN_SELFTEST_BUILD_EVERY_BIOME_EQUAL: Direct Sun is a pure function
// of geometry. The model takes no biome input; at E in {0, 5, 14, 21, 31, 45,
// 56, 79, 90} the offset and the exposure of an open, a roofed, a parasol and
// a lee cell come out of the shipped functions alone; intensity is
// 55 x sin E (0 at E <= 0); a caster of height h throws h / tan E cells
// (capped), none beside a wall at E = 85, about 4 h at E = 14; roofs,
// tents and parasols cover at every E; weather and the strength dial
// multiply Direct Sun only. The defs half (no BiomeDef carries a sun field,
// air heat is a vanilla condition) is selftest_direct_sun.py.
//
// NOT covered, and why: anything that needs a live Map — the room test
// (UsesOutdoorTemperature), roof/thing scans, the Harmony postfixes and the
// NativeArray customizer. Those are the quicktest criteria on the item.
//
// Run:
//   "%USERPROFILE%\.dotnet\dotnet.exe" run --project D:\Luke\dev\RimMandrake\src\RimMandrake\CreatureBehaviors\Source\SelfTest\RimMandrakeCreatureBehaviors.SunHeat.SelfTest.csproj -c Release

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

        private static float Felt(bool outdoors, float roof, float cast, float bodySize = 1f)
        {
            float ex = RM_SunHeatMath.Exposure(outdoors, roof, cast);
            float f = RM_SunHeatMath.BodySizeFactor(bodySize, 0.5f, 0.25f, 2.5f);
            return OutdoorC + RM_SunHeatMath.HeatOffset(ex, 30f, 1f, f, 70f);
        }

        // STILLSAND_NATIVE_CRASH_1: a model of vanilla 1.6's path job lifecycle against a
        // customizer retirement policy. Tick T: MapPreTick completes the jobs scheduled at T-1,
        // then schedules jobs for every request pushed during T-1 (each reading its request's
        // customizer on a worker thread until T+1's MapPreTick); then pawns push requests
        // carrying the CURRENT customizer; then MapPostTick runs `rebuildsAt(T)` rebuilds.
        // Returns how many times a running job's customizer was disposed under it.
        private sealed class FakeCustomizer : IDisposable
        {
            public bool Disposed;
            public void Dispose() { Disposed = true; }
        }

        private static int UseAfterFreeCount(Func<int, int> rebuildsAt, bool oldPolicy, int ticks)
        {
            var current = new FakeCustomizer();
            var deferred = new RM_DeferredDisposal<FakeCustomizer>();
            var oldRetired = new List<FakeCustomizer>();
            var pushed = new List<FakeCustomizer>();
            var running = new List<FakeCustomizer>();
            int hits = 0;
            for (int t = 1; t <= ticks; t++)
            {
                running.Clear();                 // PathFinderTick: ForceCompleteScheduledJobs
                running.AddRange(pushed);        // ...then schedule last tick's requests
                pushed.Clear();
                pushed.Add(current);             // pawns tick: requests carry the current grid
                if (!oldPolicy) deferred.DisposeDue(t); // MapComponentTick head
                for (int r = 0; r < rebuildsAt(t); r++)  // MapPostTick: RebuildHeatLayers
                {
                    if (oldPolicy)
                    {
                        foreach (var c in oldRetired) c.Dispose();
                        oldRetired.Clear();
                        oldRetired.Add(current);
                    }
                    else
                    {
                        deferred.Retire(current, t);
                    }
                    current = new FakeCustomizer();
                    foreach (var j in running) if (j.Disposed) hits++;
                }
                foreach (var j in running) if (j.Disposed) hits++;
            }
            return hits;
        }

        private static int Main()
        {
            Case("path customizer retirement: no Burst grid job ever reads a disposed sun-cost array (STILLSAND_NATIVE_CRASH_1)", () =>
            {
                // Map open on Stillsand: our own requested rebuild plus a direct Recompute from
                // Solar Mirrors/LongShade in the same tick, then again the next tick.
                Func<int, int> burst = t => t <= 3 ? 2 : (t % 7 == 0 ? 1 : 0);
                Func<int, int> everyTick = t => 1;
                // Sanity probe: the model must SEE the bug under the old "one rebuild later" policy.
                Assert(UseAfterFreeCount(burst, true, 200) > 0,
                    "the model cannot see the old policy's use-after-free, so its zero below would prove nothing");
                Assert(UseAfterFreeCount(everyTick, true, 200) > 0,
                    "old policy with one rebuild per tick read no freed array: the model is blind");
                Assert(UseAfterFreeCount(burst, false, 500) == 0, "tick-based retirement freed an array a job was reading (burst)");
                Assert(UseAfterFreeCount(everyTick, false, 500) == 0, "tick-based retirement freed an array a job was reading (every tick)");
                Assert(UseAfterFreeCount(t => 5, false, 500) == 0, "tick-based retirement freed an array a job was reading (5 per tick)");
                var d = new RM_DeferredDisposal<FakeCustomizer>(1);
                Assert(d.RetireAfterTicks >= 2, "RetireAfterTicks below the 2-tick floor was accepted");
                var a = new FakeCustomizer();
                var q = new RM_DeferredDisposal<FakeCustomizer>();
                q.Retire(a, 100);
                q.DisposeDue(100 + q.RetireAfterTicks - 1);
                Assert(!a.Disposed, "disposed before RetireAfterTicks elapsed");
                q.DisposeDue(50);
                Assert(!a.Disposed && q.Count == 1, "a clock that went backwards disposed early");
                q.DisposeDue(100 + q.RetireAfterTicks);
                Assert(a.Disposed && q.Count == 0, "not disposed once RetireAfterTicks elapsed (leak)");
            });

            Case("wild leave: a Chill native (comfy -150..-30) on a 15 C map is TooWarm (CHILL_CREATURES_VANISH_1)", () =>
            {
                Assert(RM_WildLeaveMath.Classify(15f, -150f, -30f, 15f, -160f, -20f, false) == RM_WildLeaveReason.TooWarm,
                    "the Chill native's leave on a temperate map was not classed TooWarm");
                Assert(RM_WildLeaveMath.Classify(-60f, -150f, -30f, -60f, -160f, -20f, false) == RM_WildLeaveReason.None,
                    "a Chill native at home (-60 C) was given a temperature reason to leave");
                Assert(RM_WildLeaveMath.Classify(-40f, -10f, 55f, -40f, -20f, 65f, false) == RM_WildLeaveReason.TooCold,
                    "a Grey Sea native (-10..55) on a -40 C map was not classed TooCold");
                Assert(RM_WildLeaveMath.Classify(20f, -10f, 55f, 20f, -20f, 65f, true) == RM_WildLeaveReason.Starving,
                    "a starving animal in its season was not classed Starving");
                Assert(RM_WildLeaveMath.Classify(20f, -10f, 55f, 70f, -20f, 65f, false) == RM_WildLeaveReason.TooWarm,
                    "an in-season animal standing in dangerous heat was not classed TooWarm");
                Assert(RM_WildLeaveMath.ShouldNotify(100, -1, 2500) && !RM_WildLeaveMath.ShouldNotify(2000, 100, 2500)
                    && RM_WildLeaveMath.ShouldNotify(2600, 100, 2500), "the one-per-hour throttle is wrong");
                Assert(RM_WildLeaveMath.ShouldNotify(50, 2000, 2500),
                    "a throttle stamped in a later save silenced the notice after loading an earlier one");
            });

            Case("direct sun: sun heats, a cast shadow and a roof both protect", () =>
            {
                float sun = HeatstrokeStep(Felt(true, 0f, 0f), HumanSafeMax);
                float shade = HeatstrokeStep(Felt(true, 0f, 1f), HumanSafeMax);
                float roofed = HeatstrokeStep(Felt(true, 1f, 0f), HumanSafeMax);
                Assert(sun > 0f, "a pawn in full sun gained no Heatstroke (" + sun + ")");
                Assert(shade == 0f, "a pawn in cast shade still gained Heatstroke (" + shade + ")");
                Assert(roofed == 0f, "a pawn under a roof still gained Heatstroke (" + roofed + ")");
            });

            Case("sun-scald exposure: shade grid decides when usable, InSunlight when not (WEBWORK_HEAT_SHADE_BUILD_1)", () =>
            {
                Assert(RM_SunHeatMath.ScaldExposed(true, true, 0.0f, 0.5f, true), "open clearing (ShadeAt 0) was not exposed");
                Assert(!RM_SunHeatMath.ScaldExposed(true, true, 0.9f, 0.5f, true), "under the canopy (ShadeAt 0.9) was exposed");
                Assert(RM_SunHeatMath.ScaldExposed(true, false, 0.9f, 0.5f, true), "grid off did not fall back to InSunlight (exposed)");
                Assert(!RM_SunHeatMath.ScaldExposed(true, false, 0.0f, 0.5f, false), "grid off, not in sunlight, still exposed");
                Assert(RM_SunHeatMath.ScaldExposed(false, true, 0.9f, 0.5f, true), "setting off: the canopy case did not scald again");
                Assert(!RM_SunHeatMath.ScaldExposed(true, true, 0.0f, 0.5f, false), "a roofed cell (InSunlight false) was exposed");
            });

            Case("an enclosed room is never exposed", () =>
            {
                Assert(RM_SunHeatMath.Exposure(false, 0f, 0f) == 0f, "exposed indoors");
                Assert(RM_SunHeatMath.Exposure(false, 0f, 0f, 0f) == 0f, "exposed indoors with gear");
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
                float stepSmall = HeatstrokeStep(Felt(true, 0f, 0f, 0.3f), HumanSafeMax);
                float stepBig = HeatstrokeStep(Felt(true, 0f, 0f, 4f), HumanSafeMax);
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
                    float ex = RM_SunHeatMath.Exposure(true, 0f, shade[i]);
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
                Assert(gear.ContainsKey("RM_Parasol") && gear.ContainsKey("RM_ShadeTent"),
                    "missing a piece; found " + string.Join(",", gear.Keys));
                Assert(!gear.ContainsKey("RM_SunShield"), "the sun shield is still shade gear (DIRECT_SUN_UNIFY_GEOMETRY_ALONE_DECIDES spec 5)");
                Assert(gear["RM_Parasol"].mode == "wearer" && gear["RM_ShadeTent"].mode == "footprint", "a piece has the wrong mode");
                Assert(mirrakBonus > 0f, "mirrak hide carries no shade-cloth bonus (" + mirrakBonus + ")");
            });

            if (gear != null)
            {
                foreach (string piece in new[] { "RM_Parasol", "RM_ShadeTent" })
                {
                    GearSpec g = gear[piece];
                    Case(piece + ": cuts Direct Sun the same at every sun elevation", () =>
                    {
                        float first = float.NaN;
                        foreach (float e in Elevations)
                        {
                            float cut = FeltWithGear(g, 0f, e) - FeltWithGear(g, 0f, e, true);
                            float rel = RM_SunHeatMath.WithCover(1f, RM_SunHeatMath.GearDepth(g.depth, 0f));
                            if (e > 0f)
                            {
                                Assert(cut > 0f, "no relief at E = " + e);
                            }
                            Assert(Math.Abs(ExposureUnderGear(g, 0f) - rel) < 1e-6f, "the cover changed with E = " + e);
                            if (float.IsNaN(first) && e > 0f)
                            {
                                first = ExposureUnderGear(g, 0f);
                            }
                        }
                        Console.WriteLine("  " + piece + ": exposure under it " + first.ToString("0.00") + " at every E; felt -"
                            + (FeltWithGear(g, 0f, 90f) - FeltWithGear(g, 0f, 90f, true)).ToString("0.0") + "C at E 90, -"
                            + (FeltWithGear(g, 0f, 14f) - FeltWithGear(g, 0f, 14f, true)).ToString("0.0") + "C at E 14");
                    });

                    Case(piece + ": mirrak hide casts deeper shade than plain cloth", () =>
                    {
                        float plain = RM_SunHeatMath.GearDepth(g.depth, 0f);
                        float hide = RM_SunHeatMath.GearDepth(g.depth, mirrakBonus);
                        Assert(hide > plain, "mirrak " + hide + " not deeper than plain " + plain);
                        Assert(FeltWithGear(g, mirrakBonus, 45f, true) < FeltWithGear(g, 0f, 45f, true),
                            "mirrak did not cool more than plain cloth");
                    });
                }

                Case("parasol: the wearer stops gaining Heatstroke faster, under a high and a low sun", () =>
                {
                    GearSpec g = gear["RM_Parasol"];
                    foreach (float e in new[] { 14f, 79f })
                    {
                        float open = HeatstrokeStep(FeltWithGear(g, 0f, e), HumanSafeMax);
                        float under = HeatstrokeStep(FeltWithGear(g, 0f, e, true), HumanSafeMax);
                        Assert(under < open, "parasol did not slow Heatstroke at E " + e + " (" + under + " vs " + open + ")");
                    }
                });

                Case("shade tent footprint: its cells and only its cells", () =>
                {
                    const int w = 10, h = 10;
                    float[] grid = new float[w * h];
                    RM_SunHeatMath.FillRect(grid, w, h, 3, 3, 5, 5, 0.85f);
                    Assert(grid[4 * w + 4] == 0.85f && grid[3 * w + 3] == 0.85f && grid[5 * w + 5] == 0.85f, "footprint cell unshaded");
                    Assert(grid[2 * w + 4] == 0f && grid[4 * w + 6] == 0f, "tent shaded outside its footprint");
                });

                Case("standing lee: away from the sun, depth-scaled; parasol neighbour along the shadow", () =>
                {
                    const int w = 20, h = 20;
                    float[] grid = new float[w * h];
                    RM_SunHeatMath.CastInto(grid, w, h, 10, 10, 0f, 1f, 3f, 0.6f, 0.5f);
                    Assert(grid[11 * w + 10] == 0.5f, "lee cell not at the caster's depth (" + grid[11 * w + 10] + ")");
                    Assert(grid[9 * w + 10] == 0f, "shade on the sun side of the caster");
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

            Case("patch graph: a herd dashing for one rim lands on distinct cells of that patch", () =>
            {
                // RIMMANDRAKE_SPREAD_SHADE_DASH_SEVEN_ANIMALS_ON_ONE_CELL: 12 x 3 strip,
                // shade patch A at x=0..2, patch B at x=8..11. Seven animals all
                // aim at B's rim cell (8,1), one after another, each seeing the
                // landings already claimed.
                const int w = 12, h = 3;
                bool[] sh = new bool[w * h], wk = new bool[w * h];
                for (int i = 0; i < w * h; i++) { wk[i] = true; int x = i % w; sh[i] = x <= 2 || x >= 8; }
                var g = RM_ShadePatchGraph.Build(w, h, sh, wk, 400, 2);
                int target = 1 * w + 8;
                var taken = new HashSet<int>();
                Assert(g.SpreadLanding(target, i => taken.Contains(i) ? 1 : 0, null, 24) == target, "a free target was not kept");
                for (int k = 0; k < 7; k++)
                {
                    int c = g.SpreadLanding(target, i => taken.Contains(i) ? 1 : 0, null, 24);
                    Assert(taken.Add(c), "animal " + k + " landed on taken cell " + c);
                    Assert(g.patchOf[c] == g.patchOf[target], "animal " + k + " landed outside the target's patch (x=" + c % w + ")");
                }
                // Nearest first: the first six landings lie within one step of
                // the rim cell's column pair x=8..9.
                foreach (int c in taken) Assert(c % w <= 10, "landing at x=" + c % w + " skipped nearer free cells");
                // Planted fault guard: a full patch, an unshaded target and a null predicate return the target.
                Assert(g.SpreadLanding(target, i => 1, null, 24) == target, "with every cell equally loaded it did not keep the target");
                Assert(g.SpreadLanding(1 * w + 5, i => 1, null, 24) == 1 * w + 5, "an open-sun target moved");
                Assert(g.SpreadLanding(target, null, null, 24) == target, "a null predicate moved the target");
            });

            Case("patch graph: a herd too big for a sliver patch spills into the next shade, never piles up", () =>
            {
                // Live 2026-11-25 (Pyrelands, Steve1): seven animals on a two-cell
                // patch. Here: two-cell slivers at x=2 and x=4 (z=1..2), sun between,
                // and a 3x3 patch at x=20..22 beyond a 10-cell radius.
                const int w = 30, h = 5;
                bool[] sh = new bool[w * h], wk = new bool[w * h];
                for (int i = 0; i < w * h; i++) wk[i] = true;
                foreach (int x in new[] { 2, 4 }) { sh[1 * w + x] = true; sh[2 * w + x] = true; }
                for (int z = 1; z <= 3; z++) for (int x = 20; x <= 22; x++) sh[z * w + x] = true;
                var g = RM_ShadePatchGraph.Build(w, h, sh, wk, 400, 2);
                Assert(g.PatchCount == 3, "patches " + g.PatchCount);
                int target = 1 * w + 2;
                var taken = new HashSet<int>();
                for (int k = 0; k < 4; k++)
                {
                    int c = g.SpreadLanding(target, i => taken.Contains(i) ? 1 : 0, null, 10);
                    Assert(g.patchOf[c] != RM_ShadePatchGraph.NoPatch, "animal " + k + " landed in the sun (x=" + c % w + ")");
                    Assert(taken.Add(c), "animal " + k + " landed on taken cell x=" + c % w + " z=" + c / w);
                }
                // Both slivers full: the far patch lies beyond radius 10, so the fifth shares the target.
                Assert(g.SpreadLanding(target, i => taken.Contains(i) ? 1 : 0, null, 10) == target, "the search went past its radius");
                int far = g.SpreadLanding(target, i => taken.Contains(i) ? 1 : 0, null, 24);
                Assert(far % w >= 20, "with radius 24 the fifth did not reach the far patch (x=" + far % w + ")");
            });

            Case("patch graph: on scarce shade a herd spreads evenly, never three to a cell, and skips blocked cells", () =>
            {
                // Live 2026-11-25 (Pyrelands, Steve1): eight shade cells within the dash cap, ten animals.
                // Here: one 3-cell sliver (x=5, z=1..3) and a blocked shade cell (5,4); six animals aim at (5,1).
                const int w = 12, h = 6;
                bool[] sh = new bool[w * h], wk = new bool[w * h];
                for (int i = 0; i < w * h; i++) wk[i] = true;
                for (int z = 1; z <= 4; z++) sh[z * w + 5] = true;
                var g = RM_ShadePatchGraph.Build(w, h, sh, wk, 400, 2);
                int target = 1 * w + 5, blockedCell = 4 * w + 5;
                var load = new Dictionary<int, int>();
                for (int k = 0; k < 6; k++)
                {
                    int c = g.SpreadLanding(target, i => load.TryGetValue(i, out int n) ? n : 0, i => i == blockedCell, 24);
                    Assert(c != blockedCell, "animal " + k + " landed on a blocked cell");
                    Assert(g.patchOf[c] != RM_ShadePatchGraph.NoPatch, "animal " + k + " landed in the sun");
                    load[c] = load.TryGetValue(c, out int m) ? m + 1 : 1;
                    Assert(load[c] <= 2, "animal " + k + " made a heap of " + load[c] + " at z=" + c / w);
                }
                Assert(load.Count == 3, "six animals used " + load.Count + " of the three free shade cells");
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

            // ── DIRECT_SUN_SELFTEST_BUILD_EVERY_BIOME_EQUAL ─────────────
            Case("direct sun: the model takes no biome input (same E, same offset and shade in every biome)", () =>
            {
                // The equality is structural: every public decision of the model is a static of RM_SunHeatMath or
                // RM_DirectSun whose parameters are geometry (E, cover, size) and planet numbers. Nothing a BiomeDef
                // carries can reach it; selftest_direct_sun.py every_biome shows no BiomeDef carries a sun field.
                foreach (Type t in new[] { typeof(RM_SunHeatMath), typeof(RM_DirectSun) })
                {
                    foreach (System.Reflection.MethodInfo m in t.GetMethods(System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Static))
                    {
                        foreach (System.Reflection.ParameterInfo p in m.GetParameters())
                        {
                            string n = p.Name.ToLowerInvariant();
                            Assert(!n.Contains("biome") && !n.Contains("kind") && !n.Contains("floor") || n == "glarefloor",
                                t.Name + "." + m.Name + " takes a non-geometry input '" + p.Name + "'");
                            Assert(p.ParameterType.IsPrimitive || p.ParameterType.IsArray || p.ParameterType.IsByRef,
                                t.Name + "." + m.Name + " takes a " + p.ParameterType.Name + " (only numbers and grids are geometry)");
                        }
                    }
                    foreach (System.Reflection.FieldInfo fi in t.GetFields(System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Static))
                    {
                        Assert(fi.IsLiteral, t.Name + "." + fi.Name + " is not a constant (a per-world value could hide there)");
                    }
                }
                // The table every biome gets at each E: open, roofed, parasol (shipped parasol depth 0.9 as a stand-in
                // cover), and the lee cell one step behind a height-1 wall.
                foreach (float e in Elevations)
                {
                    float full = RM_SunHeatMath.DirectSunOffsetC(RM_DirectSun.ZenithDefaultC, e);
                    float open = RM_SunHeatMath.Exposure(true, 0f, 0f);
                    float roofed = RM_SunHeatMath.Exposure(true, 1f, 0f);
                    float parasol = RM_SunHeatMath.WithCover(open, 0.9f);
                    float lee = RM_SunHeatMath.Exposure(true, 0f, LeeShadeBehindWall(e, 1));
                    Assert(open == 1f && roofed == 0f && Math.Abs(parasol - 0.1f) < 1e-6f, "cover differs at E " + e);
                    Console.WriteLine("  E " + e.ToString("0") + ": +" + full.ToString("0.0") + "C open, +"
                        + (full * roofed).ToString("0.0") + " roofed, +" + (full * parasol).ToString("0.0") + " parasol, +"
                        + (full * lee).ToString("0.0") + " one cell behind a wall");
                }
            });

            Case("direct sun: intensity is 55 x sin E at defaults, 0 at or below the horizon", () =>
            {
                Assert(RM_DirectSun.ZenithDefaultC == 55f, "the zenith default is " + RM_DirectSun.ZenithDefaultC);
                foreach (float e in Elevations)
                {
                    float want = e <= 0f ? 0f : 55f * (float)Math.Sin(e * Math.PI / 180.0);
                    float got = RM_SunHeatMath.DirectSunOffsetC(55f, e);
                    Assert(Math.Abs(got - want) < 0.01f, "E " + e + " gave " + got + ", want " + want);
                }
                Assert(RM_SunHeatMath.DirectSunOffsetC(55f, -10f) == 0f, "a sun below the horizon heats");
                Assert(RM_SunHeatMath.DirectSunOffsetC(55f, float.NaN) == 0f, "an unknown sun heats");
                Assert(Math.Abs(RM_SunHeatMath.DirectSunOffsetC(40f, 30f) - 20f) < 0.01f, "the zenith setting is not the scale");
                Assert(RM_SunHeatMath.DirectSunOffsetC(55f, 14f) < RM_SunHeatMath.DirectSunOffsetC(55f, 79f), "a low sun is not weaker");
                Assert(RM_SunHeatMath.ClampElevation(120f) == 90f && RM_SunHeatMath.ClampElevation(-5f) == 0f, "the one clamp is not [0, 90]");
            });

            Case("direct sun: a shadow is h / tan E long; none beside a wall at E 85, about 4 h at E 14", () =>
            {
                foreach (float e in new[] { 14f, 21f, 31f, 45f, 56f, 79f })
                {
                    float want = (float)(1.0 / Math.Tan(e * Math.PI / 180.0));
                    Assert(Math.Abs(RM_SunHeatMath.ShadowLengthPerHeight(e) - want) < 1e-3f, "cot E wrong at " + e);
                    Assert(Math.Abs(RM_SunHeatMath.ShadowLength(2f, RM_SunHeatMath.ShadowLengthPerHeight(e), 16f) - Math.Min(16f, 2f * want)) < 1e-3f,
                        "length of a height-2 caster wrong at E " + e);
                }
                Assert(RM_SunHeatMath.ShadowLength(1f, RM_SunHeatMath.ShadowLengthPerHeight(2f), 16f) == 16f, "the cap does not hold at a grazing sun");
                Assert(LeeShadeBehindWall(85f, 1) == 0f, "an open cell beside a wall is shaded at E 85 (" + LeeShadeBehindWall(85f, 1) + ")");
                int cells = 0;
                for (int k = 1; k <= 8; k++)
                {
                    if (LeeShadeBehindWall(14f, k) >= 0.6f) cells = k;
                }
                Assert(cells >= 3 && cells <= 5, "the lee at E 14 is " + cells + " cells for a height-1 wall, want about 4");
                Assert(LeeShadeBehindWall(45f, 2) == 0f || LeeShadeBehindWall(14f, 2) > LeeShadeBehindWall(45f, 2), "shade does not grow as the sun drops");
                Console.WriteLine("  lee of a height-1 wall: " + cells + " cells at E 14, " + (LeeShadeBehindWall(85f, 1) > 0f ? "some" : "none") + " at E 85");
            });

            Case("direct sun: a roof, a tent and a parasol cover at every E", () =>
            {
                foreach (float e in Elevations)
                {
                    float full = RM_SunHeatMath.DirectSunOffsetC(55f, e);
                    Assert(full * RM_SunHeatMath.Exposure(true, 1f, 0f) == 0f, "a roof let sun through at E " + e);
                    float[] t = new float[9];
                    RM_SunHeatMath.FillRect(t, 3, 3, 0, 0, 2, 2, RM_SunHeatMath.GearDepth(0.85f, 0f));
                    Assert(RM_SunHeatMath.Exposure(true, 0f, 0f, t[4]) <= 0.15f + 1e-6f, "a tent did not cover at E " + e);
                    Assert(RM_SunHeatMath.WithCover(RM_SunHeatMath.Exposure(true, 0f, 0f), RM_SunHeatMath.GearDepth(0.9f, 0f)) <= 0.1f + 1e-6f,
                        "a parasol did not cover at E " + e);
                }
            });

            Case("direct sun: weather and the strength dial scale Direct Sun only", () =>
            {
                // E 21: 55 x sin 21 = 19.7 C, so twice it stays under the 70 C cap.
                float full = RM_SunHeatMath.DirectSunOffsetC(55f, 21f);
                float bare = RM_DirectSun.FeltOffsetC(1f, full, 1f, 1f);
                Assert(Math.Abs(RM_DirectSun.FeltOffsetC(0.5f, full, 1f, 1f) - bare * 0.5f) < 0.01f, "a weather factor of 0.5 did not halve it");
                Assert(Math.Abs(RM_DirectSun.FeltOffsetC(1f, full, 2f, 1f) - bare * 2f) < 0.01f, "strength 2 did not double it");
                Assert(RM_DirectSun.FeltOffsetC(0f, full, 1f, 1f) == 0f && RM_DirectSun.FeltOffsetC(1f, full, 0f, 1f) == 0f, "zero still heats");
                Assert(RM_DirectSun.FeltOffsetC(1f, full, 3f, 0.05f) == RM_DirectSun.MaxOffsetC, "the cap does not hold");
                // Only Direct Sun: the air temperature is an input the model adds to, never scales.
                float air = 40f;
                Assert(Math.Abs((air + RM_DirectSun.FeltOffsetC(0f, full, 1f, 1f)) - air) < 1e-6f, "the dial reached the air temperature");
            });

            Case("air heat: a native plant's upper growth bounds rise by the offset, never below its loaded band", () =>
            {
                RM_AirHeatNatives.Fit(42f, 58f, 12f, out float mo, out float mx);
                Assert(mo == 54f && mx == 70f, "a 12 C offset fitted 42/58 to " + mo + "/" + mx);
                RM_AirHeatNatives.Fit(42f, 58f, 0f, out mo, out mx);
                Assert(mo == 42f && mx == 58f, "no offset moved the band to " + mo + "/" + mx);
                RM_AirHeatNatives.Fit(42f, 58f, -5f, out mo, out mx);
                Assert(mo == 42f && mx == 58f, "a negative offset narrowed the band to " + mo + "/" + mx);
            });

            Case("direct sun: sand glare floors exposure in shade; paved shade is fully cool", () =>
            {
                float floor = RM_DirectSun.SandGlareExposureFloor;
                float shadeOnSand = RM_SunHeatMath.WithGlareFloor(RM_SunHeatMath.Exposure(true, 0f, 1f), floor);
                float shadeOnPaving = RM_SunHeatMath.WithGlareFloor(RM_SunHeatMath.Exposure(true, 0f, 1f), 0f);
                Assert(Math.Abs(shadeOnSand - floor) < 1e-5f, "sand shade exposure " + shadeOnSand);
                Assert(shadeOnPaving == 0f, "paved shade exposure " + shadeOnPaving);
                Assert(RM_SunHeatMath.WithGlareFloor(1f, floor) == 1f, "glare lowered full sun");
                float parasol = RM_SunHeatMath.WithGlareFloor(RM_SunHeatMath.WithCover(1f, 0.9f), floor);
                Assert(Math.Abs(parasol - floor) < 1e-5f, "parasol beat the glare floor: " + parasol);
                float felt = OutdoorC + RM_SunHeatMath.HeatOffset(shadeOnSand, 35f, 1f, 1f, 70f);
                float paved = OutdoorC + RM_SunHeatMath.HeatOffset(shadeOnPaving, 35f, 1f, 1f, 70f);
                Assert(HeatstrokeStep(felt, HumanSafeMax) > HeatstrokeStep(paved, HumanSafeMax), "sand shade no hotter than a shade yard");
            });

            // ── OLLOPOM_OUTDOOR_BEAUTY ──────────────────────────────────
            Case("perceived beauty: a pretty creature adds beauty outdoors only, alive only, scaled, and nothing when off (shipped ollopom)", () =>
            {
                string root = FindModsRoot();
                var doc = new System.Xml.XmlDocument();
                doc.Load(System.IO.Path.Combine(root, "..", "RimStarWars", "SWBestiary", "Defs", "ThingDefs_Races", "RSW_Ollopom.xml"));
                System.Xml.XmlNode ext = doc.SelectSingleNode("//ThingDef[defName='RSW_Ollopom']/modExtensions/li[contains(@Class,'RM_PerceivedBeautyExtension')]");
                Assert(ext != null, "RSW_Ollopom carries no RM_PerceivedBeautyExtension");
                Assert(ext.Attributes["MayRequire"]?.Value == "mandrake.rm.biomes",
                    "the extension is not MayRequire-guarded on mandrake.rm.biomes (CreatureBehaviors ships folded into it, so its own id never loads; an unguarded missing Class discards the def)");
                Assert(doc.SelectSingleNode("//ThingDef[defName='RSW_Ollopom']/statBases/PawnBeauty") == null,
                    "PawnBeauty is back on the ollopom: it is inert for animals (humanlike-only thoughts) and only inflates market value");
                float b = float.Parse(ext.SelectSingleNode("beautyOutdoors").InnerText, System.Globalization.CultureInfo.InvariantCulture);
                Assert(b > 0f && b < 14f, "ollopom beautyOutdoors " + b + " is not a SMALL bonus (0 < b < a rose's 14)");
                // Sanity probe: the rule must be able to say yes before its zeros mean anything.
                Assert(RM_PerceivedBeautyMath.Contribution(true, 1f, b, false, true) == b, "outdoors, alive, on: not the full value");
                Assert(RM_PerceivedBeautyMath.Contribution(true, 2f, b, false, true) == 2f * b, "multiplier not applied");
                Assert(RM_PerceivedBeautyMath.Contribution(true, 1f, b, false, false) == 0f, "indoors added beauty (owner asked for OUTDOOR beauty)");
                Assert(RM_PerceivedBeautyMath.Contribution(true, 1f, b, true, true) == 0f, "a dead creature added beauty");
                Assert(RM_PerceivedBeautyMath.Contribution(false, 1f, b, false, true) == 0f, "the setting off still added beauty");
                Assert(RM_PerceivedBeautyMath.Contribution(true, 0f, b, false, true) == 0f, "multiplier 0 still added beauty");
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

            // SOLAR_MIRRORS_MOD_DESIGN_1 §2.3, REAL from RM_SunHeatMath.cs (the light hook's two folds).
            Case("light hook: light un-shades up to full sun, never past it; zero light changes nothing", () =>
            {
                Assert(RM_SunHeatMath.WithLight(0.3f, 0f) == 0.3f, "zero light moved exposure");
                Assert(RM_SunHeatMath.ShadeWithLight(0.7f, 0f) == 0.7f, "zero light moved shade");
                Assert(RM_SunHeatMath.WithLight(0.3f, 0.6f) == 0.6f, "base 0.3 + light 0.6 should read 0.6");
                Assert(RM_SunHeatMath.WithLight(0.8f, 0.6f) == 0.8f, "light lowered exposure");
                Assert(RM_SunHeatMath.WithLight(0.2f, 2.5f) == 1f, "concentration pushed exposure past 1");
                Assert(System.Math.Abs(RM_SunHeatMath.ShadeWithLight(1f, 0.6f) - 0.4f) < 1e-6f, "full shade + 0.6 light should be 0.4");
                Assert(RM_SunHeatMath.ShadeWithLight(0.2f, 0.6f) == 0.2f, "light raised shade");
                // ShadeAt and exposure agree (the design's one-source-of-truth fix): shade = 1 - lit exposure.
                float ex = RM_SunHeatMath.WithLight(0.3f, 0.6f);
                float sh = RM_SunHeatMath.ShadeWithLight(0.7f, 0.6f);
                Assert(System.Math.Abs(ex + sh - 1f) < 1e-6f, "shade " + sh + " and exposure " + ex + " disagree");
                // A parasol in a beam still shades you: cover applies after the light.
                Assert(System.Math.Abs(RM_SunHeatMath.WithCover(RM_SunHeatMath.WithLight(0f, 1f), 0.5f) - 0.5f) < 1e-6f, "parasol lost in a beam");
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

            // ── STILLSAND_WIND_SUN_BEARING_1 ────────────────────────────
            Case("wind lock: the dune engine's bearing IS the pinned sun's (shipped DLL)", () =>
            {
                // Reflection into the BUILT CreatureBehaviors assembly: the dunes engine
                // cannot reference it, so this is what keeps the two formulas one.
                string dll = System.IO.Path.Combine(FindModsRoot(), "CreatureBehaviors", "Assemblies", "RimMandrake.CreatureBehaviors.dll");
                var asm = System.Reflection.Assembly.UnsafeLoadFrom(dll);   // not LoadFrom: from an ext4 clone the path is \\wsl.localhost, a "remote source" LoadFrom refuses
                var geo = asm.GetType("RimMandrake.CreatureBehaviors.RM_MapComponent_PinnedSun").GetMethod("SunGeometry");
                float[][] tiles = { new[] { 20f, -30f }, new[] { -40f, 10f }, new[] { 5f, 80f }, new[] { -60f, -120f }, new[] { 0f, 45f } };
                foreach (float[] t in tiles)
                {
                    object[] args = { t[0], t[1], 0f, 0f, 0f, 0f };
                    geo.Invoke(null, args);
                    float pinned = (float)args[4];
                    float dune = RimMandrake.MovingDunes.DuneWindBearing.SunBearingDegrees(t[0], t[1], 0f, 0f);
                    float diff = Math.Abs(((pinned - dune) % 360f + 540f) % 360f - 180f);
                    Assert(diff < 0.01f, "tile " + t[0] + "," + t[1] + ": pinned " + pinned + " vs dune " + dune);
                }
            });

            Case("wind lock: the wind blows along the shadows; lees fall shadow-side", () =>
            {
                // A tile due west of the substellar point sees the sun due east (90).
                float b = RimMandrake.MovingDunes.DuneWindBearing.SunBearingDegrees(0f, -40f, 0f, 0f);
                Assert(Math.Abs(b - 90f) < 0.01f, "sun bearing " + b + ", expected 90");
                Assert(RimMandrake.MovingDunes.DuneWindBearing.WindDirFromSunBearing(b, false) == 6, "wind not toward W (6)");
                Assert(RimMandrake.MovingDunes.DuneWindBearing.WindDirFromSunBearing(b, true) == 2, "toward-sun wind not E (2)");
                // Wind index 6 = (-1,0): the same way RM_MapComponent_ShadeGrid casts shadows, -(sin b, cos b).
                float sx = -(float)Math.Sin(b * Math.PI / 180), sz = -(float)Math.Cos(b * Math.PI / 180);
                Assert(sx < -0.99f && Math.Abs(sz) < 0.01f, "shadow not west");
                Assert(RimMandrake.MovingDunes.DuneWindBearing.WindDirFromSunBearing(-135f, false) == 1, "sun SW -> wind not NE");
                Assert(RimMandrake.MovingDunes.DuneWindBearing.SunBearingDegrees(0f, 0f, 0f, 0f) == 0f, "substellar tile not 0");
            });

            Case("wind lock: Stillsand's dune binding locks the bearing at the pinned sun's point", () =>
            {
                var doc = new System.Xml.XmlDocument();
                doc.Load(System.IO.Path.Combine(FindModsRoot(), "MovingDunes", "Patches", "BiomeBindings.xml"));
                System.Xml.XmlNode li = doc.SelectSingleNode("//match[xpath='Defs/BiomeDef[defName=\"RM_Stillsand\"]']/value/li");
                Assert(li != null, "no Stillsand dune binding");
                Assert(li.SelectSingleNode("lockBearingToSubstellar")?.InnerText == "true", "Stillsand wind not locked");
                Assert(F(li, "substellarLatitude", 0f) == 0f && F(li, "substellarLongitude", 0f) == 0f, "substellar point not 0,0");
            });

            // ── STILLSAND_STILL_COOLING_DRAUGHT_1 ───────────────────────
            Case("cooling draught: +8 C comfortable max for ~6 h slows vanilla Heatstroke", () =>
            {
                var doc = new System.Xml.XmlDocument();
                doc.Load(System.IO.Path.Combine(FindModsRoot(), "Stillsand", "Defs", "HediffDefs", "RM_CoolingDraught.xml"));
                System.Xml.XmlNode hd = doc.SelectSingleNode("//HediffDef[defName='RM_CoolingDraught']");
                Assert(hd != null, "RM_CoolingDraught missing");
                float off = F(hd, "stages/li/statOffsets/ComfyTemperatureMax", 0f);
                float ticks = F(hd, "comps/li[@Class='HediffCompProperties_Disappears']/disappearsAfterTicks", 0f);
                Assert(off == 8f, "ComfyTemperatureMax offset " + off);
                Assert(Math.Abs(ticks / 2500f - 6f) < 0.01f, "lasts " + ticks / 2500f + " h, not 6");
                // A felt 40 C: over the plain safe max, under it with the draught.
                Assert(HeatstrokeStep(40f, HumanSafeMax) > HeatstrokeStep(40f, HumanSafeMax + off), "draught does not slow Heatstroke");
            });

            // LONGSHADE_GPT_ENRICHMENT_1 §2, REAL from RM_MovingShadeMath.cs.
            Case("moving shade: body footprint shaded, shadow runs along the sun, nothing upsun", () =>
            {
                int w = 40, h = 40;
                float[] g = new float[w * h];
                RM_MovingShadeMath.CastBody(g, w, h, 20, 20, 1, true, 1f, 0f, 6f, 0.6f, 1f);
                for (int dz = -1; dz <= 1; dz++)
                    for (int dx = -1; dx <= 1; dx++)
                        Assert(g[(20 + dz) * w + 20 + dx] == 1f, "body cell " + dx + "," + dz + " not shaded");
                Assert(g[20 * w + 25] > 0.5f, "no shadow 4 cells down-sun of the body edge");
                Assert(g[20 * w + 17] == 0f, "shade appeared up-sun of the body");
                Assert(g[23 * w + 20] == 0f, "shade appeared beside the body, off the sun line");
            });

            Case("moving shade: every written cell lies inside ShadowBounds", () =>
            {
                int w = 50, h = 50;
                foreach (var dir in new[] { (1f, 0f), (-0.6f, 0.8f), (0.3f, -0.95f), (0f, 0f) })
                {
                    bool directional = dir.Item1 != 0f || dir.Item2 != 0f;
                    float[] g = new float[w * h];
                    RM_MovingShadeMath.CastBody(g, w, h, 25, 25, 2, directional, dir.Item1, dir.Item2, 9f, 0.6f, 0.8f);
                    Assert(RM_MovingShadeMath.ShadowBounds(w, h, 25, 25, 2, directional, dir.Item1, dir.Item2, 9f,
                        out int x0, out int z0, out int x1, out int z1), "bounds empty");
                    for (int z = 0; z < h; z++)
                        for (int x = 0; x < w; x++)
                            if (g[z * w + x] > 0f)
                                Assert(x >= x0 && x <= x1 && z >= z0 && z <= z1,
                                    "cell " + x + "," + z + " written outside bounds for dir " + dir);
                }
            });

            Case("world stars: still within a day, 6 degrees a day, one turn a year, frozen when drift is off (WORLD_STARS_REPAIR_STILL_SPINNING_FOR_NOBODY)", () =>
            {
                const int day = 60000;
                long t0 = 3L * RM_WorldStarsMath.TicksPerYear + 17 * day;
                float a = RM_WorldStarsMath.DriftDegrees(t0, true), b = RM_WorldStarsMath.DriftDegrees(t0 + day, true);
                Assert(Math.Abs((b - a) - 6f) < 1e-3f, "one day turns the stars " + (b - a) + " degrees, not 6");
                Assert(Math.Abs(RM_WorldStarsMath.DriftDegrees(t0 + day / 2, true) - a) < 3.01f,
                    "half a day turned the stars more than 3 degrees: they still wheel daily");
                Assert(Math.Abs(RM_WorldStarsMath.DriftDegrees(t0 + RM_WorldStarsMath.TicksPerYear, true) - a) < 1e-3f,
                    "a year later the stars are not back where they were");
                Assert(RM_WorldStarsMath.DriftDegrees(t0, false) == 0f && RM_WorldStarsMath.DriftDegrees(t0 + 12345, false) == 0f,
                    "drift off: the stars still move");
                for (long t = -5L * day; t < 70L * day; t += 7919)
                {
                    float d = RM_WorldStarsMath.DriftDegrees(t, true);
                    Assert(d >= 0f && d < 360f, "drift out of [0,360) at tick " + t + ": " + d);
                }
            });
            Case("world sun: pinned toward the substellar point, identical at any two ticks, vanilla at the main menu (WORLD_STARS_REPAIR_STILL_SPINNING_FOR_NOBODY)", () =>
            {
                // Vanilla's daily sun (GenCelestial.SunPositionUnmodified at latitude 0, equinox): (0,0,-1) turned about +Y
                // by (dayPercent - 0.5) * 360. The postfix replaces it, while playing, with the substellar direction.
                Func<long, float[]> vanilla = t =>
                {
                    double a = ((t % 60000) / 60000.0 - 0.5) * 2.0 * Math.PI;
                    return new[] { (float)(-Math.Sin(a)), 0f, (float)(-Math.Cos(a)) };
                };
                Func<long, bool, bool, float[]> sun = (t, on, playing) =>
                {
                    if (!RM_WorldStarsMath.PinsWorldSun(on, playing)) return vanilla(t);
                    RM_WorldStarsMath.SubstellarDirection(0.0, 0.0, out float x, out float y, out float z);
                    return new[] { x, y, z };
                };
                const long t1 = 7L * 60000 + 3000, t2 = t1 + 60000 + 17777;   // a day and a bit apart, different hour
                float[] a1 = sun(t1, true, true), a2 = sun(t2, true, true);
                Assert(a1[0] == a2[0] && a1[1] == a2[1] && a1[2] == a2[2], "pinned sun differs between two ticks");
                float[] v1 = vanilla(t1), v2 = vanilla(t2);
                Assert(Math.Abs(v1[0] - v2[0]) + Math.Abs(v1[2] - v2[2]) > 0.1f, "probe: vanilla's sun did not move between the ticks");
                Assert(Math.Abs(a1[0]) < 1e-6f && Math.Abs(a1[1]) < 1e-6f && Math.Abs(a1[2] + 1f) < 1e-6f,
                    "substellar (0,0) is not (0,0,-1), the vector Alien Worlds freezes the sun at");
                float[] e = sun(t1, true, false), o = sun(t2, false, true);
                Assert(e[0] == v1[0] && e[2] == v1[2], "main menu (Entry) does not keep vanilla's sun");
                Assert(o[0] == v2[0] && o[2] == v2[2], "setting off does not keep vanilla's sun");
                // Round trip through PlanetLayer.LongLatOf's formula: the direction points AT the substellar tile.
                for (double lat = -80; lat <= 80; lat += 20)
                    for (double lon = -170; lon <= 170; lon += 34)
                    {
                        RM_WorldStarsMath.SubstellarDirection(lat, lon, out float x, out float y, out float z);
                        double lon2 = Math.Atan2(x, -z) * 180.0 / Math.PI, lat2 = Math.Asin(y) * 180.0 / Math.PI;
                        Assert(Math.Abs(lat2 - lat) < 1e-3 && Math.Abs(lon2 - lon) < 1e-3,
                            "direction for (" + lat + "," + lon + ") reads back as (" + lat2 + "," + lon2 + ")");
                        Assert(Math.Abs(x * x + y * y + z * z - 1f) < 1e-5f, "substellar direction not unit length");
                    }
            });
            Case("tidal sun glow: day side reads day, night side night, west = east, home tile full (SUN_GLOW_DECIDE_WEST_TERMINATOR_SUNBATHING)", () =>
            {
                const float band = RM_TidalSunGlowMath.DefaultTwilightBandDegrees;
                float prev = -1f;
                for (double e = -90.0; e <= 90.0; e += 0.05)
                {
                    float g = RM_TidalSunGlowMath.GlowFromElevation(e, band);
                    Assert(g >= prev - 1e-6f, "glow not monotone in elevation at " + e);
                    Assert(g >= 0f && g <= 1f, "glow out of [0,1] at " + e + ": " + g);
                    if (e > 1e-6) Assert(g > RM_TidalSunGlowMath.DayNightThreshold, "sun up " + e + " deg reads night: " + g);
                    else Assert(g <= RM_TidalSunGlowMath.DayNightThreshold, "sun down " + e + " deg reads day: " + g);
                    if (e <= -band) Assert(g == 0f, "below the dusk band (" + e + ") glow " + g + " is not 0");
                    prev = g;
                }
                for (double lat = -85; lat <= 85; lat += 5)
                    for (double lon = 0; lon <= 180; lon += 5)
                        Assert(RM_TidalSunGlowMath.GlowAt(lat, lon, band) == RM_TidalSunGlowMath.GlowAt(lat, -lon, band)
                            && RM_TidalSunGlowMath.GlowAt(lat, lon, band) == RM_TidalSunGlowMath.GlowAt(-lat, lon, band),
                            "glow not symmetric at lat " + lat + " lon " + lon);
                Assert(RM_TidalSunGlowMath.GlowFromElevation(35.4, band) > 0.99f, "home tile 17011 (sun 35.4 deg) not full day");
                Assert(RM_TidalSunGlowMath.GlowAt(0, 90, band) <= 0.6f && RM_TidalSunGlowMath.GlowAt(0, -90, band) <= 0.6f,
                    "a terminator reads day");
                Assert(RM_TidalSunGlowMath.GlowAt(0, 80, band) > 0.6f && RM_TidalSunGlowMath.GlowAt(0, -80, band) > 0.6f,
                    "arc 80 (sun 10 deg up) reads night");
                Assert(RM_TidalSunGlowMath.GlowFromElevation(-3.0, 0f) == 0f, "dusk band 0: below the horizon is not dark");
                // TWILIGHT_BAND_DECIDE_HOW_FAR_DUSK_REACHES: owner, by card 2026-10-20 -> "12 degrees" (nautical).
                Assert(band == 12f, "default dusk band is " + band + ", the owner's card says 12");
                // Continuous across the band at every slider width: no step at the horizon or at -band.
                foreach (float w in new[] { 1f, 6f, 12f, 18f })
                {
                    float last = RM_TidalSunGlowMath.GlowFromElevation(-90.0, w);
                    for (double e = -90.0 + 0.01; e <= 90.0; e += 0.01)
                    {
                        float g = RM_TidalSunGlowMath.GlowFromElevation(e, w);
                        // smoothstep's steepest slope is 1.5 * 0.6 / band per degree; the day side's is ~0.014
                        Assert(Math.Abs(g - last) < 0.01f * 0.9f / w + 0.0005f, "glow jumps " + (g - last) + " at " + e + " deg, band " + w);
                        last = g;
                    }
                }
                Assert(Math.Abs(RM_TidalSunGlowMath.GlowFromElevation(-6.0, 12f) - 0.3f) < 1e-4f, "mid-band (-6 of 12) is not half of 0.6");
            });
            Case("tidal lock preset guard: restores only a locked save with no preset on Worldbuilder (TIDAL_LOCK_FIX_PRESET_NAME_WAS_MISSING)", () =>
            {
                string[] presets = { null, "", "TidallyLocked", "Default", "SomeOtherPreset" };
                string[] saved = { null, "", "TidallyLocked", "Default", "Unknown", "tidallylocked" };
                int restored = 0;
                foreach (bool on in new[] { false, true })
                    foreach (bool wb in new[] { false, true })
                        foreach (string p in presets)
                            foreach (string s in saved)
                            {
                                string r = RM_TidalLockPresetKernel.PresetToRestore(on, wb, p, s);
                                bool want = on && wb && string.IsNullOrEmpty(p) && s == "TidallyLocked";
                                Assert(want ? r == "TidallyLocked" : r == null,
                                    "on=" + on + " wb=" + wb + " preset=" + (p ?? "null") + " saved=" + (s ?? "null") + " -> " + (r ?? "null"));
                                if (r != null) restored++;
                            }
                Assert(restored == 2, "expected exactly 2 restoring inputs (preset null and empty), got " + restored);
            });
            Case("moving shade: clearing the old rectangle and casting the new leaves no trail", () =>
            {
                int w = 40, h = 40;
                float[] g = new float[w * h];
                RM_MovingShadeMath.CastBody(g, w, h, 10, 10, 1, true, 0f, 1f, 5f, 0.6f, 1f);
                RM_MovingShadeMath.ShadowBounds(w, h, 10, 10, 1, true, 0f, 1f, 5f, out int a0, out int b0, out int a1, out int b1);
                RM_MovingShadeMath.ClearRect(g, w, h, a0, b0, a1, b1);
                RM_MovingShadeMath.CastBody(g, w, h, 30, 10, 1, true, 0f, 1f, 5f, 0.6f, 1f);
                for (int z = 0; z < h; z++)
                    for (int x = 0; x < 20; x++)
                        Assert(g[z * w + x] == 0f, "stale shade left at " + x + "," + z);
                Assert(g[10 * w + 30] == 1f, "new body cell not shaded");
            });

            Case("moving shade: the gloomcast is a moving caster, the shadow cools like a rock's", () =>
            {
                var doc = new System.Xml.XmlDocument();
                doc.Load(System.IO.Path.Combine(FindModsRoot(), "LongShade", "Defs", "ThingDefs_Races", "RM_LongShade_Gloomcast.xml"));
                System.Xml.XmlNode td = doc.SelectSingleNode("//ThingDef[defName='RM_Gloomcast']");
                Assert(td != null, "RM_Gloomcast missing");
                float hgt = F(td, "comps/li[@Class='RimMandrake.CreatureBehaviors.RM_CompProperties_ShadowCaster']/castShadeHeight", 0f);
                float depth = F(td, "comps/li[@Class='RimMandrake.CreatureBehaviors.RM_CompProperties_ShadowCaster']/castShadeDepth", 1f);
                Assert(hgt > 0f, "RM_Gloomcast casts no moving shade");
                float ex = RM_SunHeatMath.WithCover(RM_SunHeatMath.Exposure(true, 0f, 0f), depth);
                Assert(HeatstrokeStep(OutdoorC + RM_SunHeatMath.HeatOffset(ex, 30f, 1f, 1f, 70f), HumanSafeMax) == 0f,
                    "a pawn in the gloomcast's shadow still gains Heatstroke");
            });

            // ── TREE_SHADE_SELFTEST_PROVE_FOREST_IS_SHADE (design tree_shade_model_2026-10-19.md §6) ──
            // The raster below (ForestRaster) is the loop of RM_MapComponent_ShadeGrid.Recompute for trees, through the
            // same shipped calls: trunk strip = CastInto(ShadowLength(hc, cot E, 16)), crown = CastCrown, merged by max.
            Case("tree crowns: the same tree at the same E casts the same footprint in every biome", () =>
            {
                foreach (Type t in new[] { typeof(RM_TreeCrown) })
                {
                    foreach (System.Reflection.MethodInfo m in t.GetMethods(System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Static))
                    {
                        foreach (System.Reflection.ParameterInfo p in m.GetParameters())
                        {
                            Assert(p.ParameterType.IsPrimitive && !p.Name.ToLowerInvariant().Contains("biome"),
                                t.Name + "." + m.Name + " takes a non-geometry input '" + p.Name + "'");
                        }
                    }
                }
                float[] first = null;
                foreach (string biome in new[] { "RM_Greentide", "RM_Miasma", "RM_FeverWood", "RM_Webwork", "RM_Contagion", "RM_Stillsand" })
                {
                    float[] g = ForestRaster(41, 41, new List<Tree> { new Tree(20, 30, 1.5f, 3.8f, 1f) }, 39f, 0f, -1f, true, 1f);
                    if (first == null) first = g;
                    Assert(SameGrid(first, g), "the footprint differs for " + biome);
                }
            });

            Case("tree crowns: at E 90 the disc lies under the crown; at E 14 it moves hc x cot 14, capped at 16", () =>
            {
                float hc = RM_TreeCrown.Height(4f, RM_TreeCrown.HeightFactorDefault);
                RM_SunHeatMath.CrownFootprint(10, 10, hc, 0f, -1f, RM_SunHeatMath.ShadowLengthPerHeight(90f), 16f, out float ox, out float oz);
                Assert(Math.Abs(ox - 10f) < 1e-4f && Math.Abs(oz - 10f) < 1e-3f, "at E 90 the disc is at " + ox + "," + oz);
                float cot14 = RM_SunHeatMath.ShadowLengthPerHeight(14f);
                RM_SunHeatMath.CrownFootprint(10, 40, hc, 0f, -1f, cot14, 16f, out ox, out oz);
                Assert(Math.Abs((40f - oz) - hc * cot14) < 1e-3f && Math.Abs(ox - 10f) < 1e-4f, "at E 14 the offset is " + (40f - oz) + ", want " + hc * cot14);
                float hcGiant = RM_TreeCrown.Height(16f, 0.79f);
                RM_SunHeatMath.CrownFootprint(10, 40, hcGiant, 0f, -1f, cot14, 16f, out ox, out oz);
                Assert(Math.Abs((40f - oz) - 16f) < 1e-3f, "a giant's crown at E 14 lands " + (40f - oz) + " cells away, not the cap 16");
                // The disc under the crown at E 90: every cell within r of the root, and none beyond. r is the design's
                // r = k x s / 2 (design §4.2), written here and not read from RM_TreeCrown.Radius, so a wrong kernel
                // radius moves the cast disc away from it.
                float r = RM_TreeCrown.RadiusFactorDefault * 4f / 2f;
                Assert(Math.Abs(RM_TreeCrown.Radius(4f, RM_TreeCrown.RadiusFactorDefault) - r) < 1e-4f, "the crown radius of a 4-cell tree is " + RM_TreeCrown.Radius(4f, RM_TreeCrown.RadiusFactorDefault) + ", want k x s / 2 = " + r);
                float[] g = ForestRaster(21, 21, new List<Tree> { new Tree(10, 10, 4f, 4f, 1f) }, 90f, 0f, -1f, true, 1f);
                for (int z = 0; z < 21; z++)
                    for (int x = 0; x < 21; x++)
                    {
                        bool inside = (x - 10) * (x - 10) + (z - 10) * (z - 10) <= r * r;
                        Assert(inside == (g[z * 21 + x] >= 0.999f), "cell " + x + "," + z + " at E 90: shade " + g[z * 21 + x] + ", inside the disc " + inside);
                    }
                // The trunk strip is about 4 x hc at E 14.
                float strip = RM_SunHeatMath.ShadowLength(hc, cot14, 16f);
                Assert(Math.Abs(strip - 4.01f * hc) < 0.1f * hc, "the trunk strip at E 14 is " + strip + " for hc " + hc);
                Console.WriteLine("  E 14: crown offset " + (hc * cot14).ToString("0.0") + " cells for a 4-cell tree, the giant's capped at 16");
            });

            Case("drawn crown shadow: the greatbole's soft disc sits on the cells its crown shades, down-sun, and only with a sun vector", () =>
            {
                // RIMMANDRAKE_TRY_RENDERED_CROWN_SHADOW_ON_ONE_GIANT_TREE. A grown greatbole (drawn 12 to 16, factors 0.97 /
                // 0.79 from Patches/RM_TreeCrowns_Giants.xml) at E 14 and E 40 with the sun from four bearings.
                foreach (float drawn in new[] { 12f, 16f })
                    foreach (float elev in new[] { 14f, 40f, 89f })
                        foreach (var dir in new[] { (0f, -1f), (1f, 0f), (-0.6f, 0.8f), (0.7071f, 0.7071f) })
                        {
                            const int W = 81;
                            float r = RM_TreeCrown.Radius(drawn, 0.97f);
                            float hc = RM_TreeCrown.Height(drawn, 0.79f);
                            float cot = RM_SunHeatMath.ShadowLengthPerHeight(elev);
                            float[] g = new float[W * W];
                            RM_SunHeatMath.CastCrown(g, W, W, 40, 40, r, hc, dir.Item1, dir.Item2, cot, 16f, 1f, null, 0);
                            RM_SunHeatMath.CrownShadowQuad(40, 40, r, hc, dir.Item1, dir.Item2, cot, 16f, out float sx, out float sz, out float half);
                            int raised = 0;
                            for (int z = 0; z < W; z++)
                                for (int x = 0; x < W; x++)
                                {
                                    if (g[z * W + x] < 0.999f) continue;
                                    raised++;
                                    float dx = x + 0.5f - sx, dz = z + 0.5f - sz;
                                    float d = (float)Math.Sqrt(dx * dx + dz * dz) / half;
                                    Assert(RM_SunHeatMath.CrownShadowAlpha(d, RM_SunHeatMath.CrownShadowCore) >= 0.999f,
                                        "drawn " + drawn + " E " + elev + ": shaded cell " + x + "," + z + " is outside the drawn shadow's dark core (d " + d + ")");
                                }
                            Assert(raised > 0, "no cell shaded");
                            // The drawn disc fades within one cell outside the shaded cells: its edge is no more than the
                            // penumbra beyond the crown radius.
                            Assert(Math.Abs(half - r - RM_SunHeatMath.CrownShadowPenumbra) < 1e-4f, "half side " + half + " for r " + r);
                            // Down-sun: the drawn centre moved along the shadow vector, by the same offset the grid casts.
                            RM_SunHeatMath.CrownFootprint(40, 40, hc, dir.Item1, dir.Item2, cot, 16f, out float ox, out float oz);
                            Assert(Math.Abs(sx - (ox + 0.5f)) < 1e-4f && Math.Abs(sz - (oz + 0.5f)) < 1e-4f, "drawn centre " + sx + "," + sz + " vs footprint " + ox + "," + oz);
                            float along = (sx - 40.5f) * dir.Item1 + (sz - 40.5f) * dir.Item2;
                            Assert(elev > 80f || along > 1f, "E " + elev + ": the drawn shadow is not down-sun (" + along + ")");
                        }
                // The soft edge: full inside the core, falling, 0 at the edge and beyond.
                Assert(RM_SunHeatMath.CrownShadowAlpha(0f, 0.85f) == 1f && RM_SunHeatMath.CrownShadowAlpha(0.85f, 0.85f) == 1f, "core not full");
                Assert(RM_SunHeatMath.CrownShadowAlpha(1f, 0.85f) == 0f && RM_SunHeatMath.CrownShadowAlpha(1.3f, 0.85f) == 0f, "edge not clear");
                float prev = 1f;
                for (float d = 0.85f; d <= 1f; d += 0.01f)
                {
                    float a = RM_SunHeatMath.CrownShadowAlpha(d, 0.85f);
                    Assert(a <= prev + 1e-6f, "the edge is not falling at " + d);
                    prev = a;
                }
                // The gate: tree crowns on, a sun vector, the flagged species, a crown that casts. Each missing one: no draw.
                Assert(RM_SunHeatMath.DrawsCrownShadow(true, true, true, 1f), "the greatbole under a fixed sun draws no shadow");
                Assert(!RM_SunHeatMath.DrawsCrownShadow(false, true, true, 1f), "crowns off still draw");
                Assert(!RM_SunHeatMath.DrawsCrownShadow(true, false, true, 1f), "no sun vector still draws");
                Assert(!RM_SunHeatMath.DrawsCrownShadow(true, true, false, 1f), "an unflagged species draws");
                Assert(!RM_SunHeatMath.DrawsCrownShadow(true, true, true, 0f), "a crown that casts nothing draws");
            });

            Case("tree crowns: a seedling casts by its drawn size, leafless thins it, the dial scales it, off casts only the trunk", () =>
            {
                float sSeed = RM_SunHeatMath.DrawnSize(1f, 3f, 12f, 0.1f);
                float sFull = RM_SunHeatMath.DrawnSize(1f, 3f, 12f, 1f);
                Assert(Math.Abs(sSeed - 3.9f) < 1e-4f && Math.Abs(sFull - 12f) < 1e-4f, "drawn size " + sSeed + " / " + sFull);
                Assert(Math.Abs(RM_SunHeatMath.DrawnSize(2f, 3f, 12f, 1f) - 24f) < 1e-4f, "drawSize.x does not scale the drawn size");
                int seed = Covered(ForestRaster(61, 61, new List<Tree> { new Tree(30, 50, 3f, 12f, 0.1f) }, 45f, 0f, -1f, true, 1f));
                int full = Covered(ForestRaster(61, 61, new List<Tree> { new Tree(30, 50, 3f, 12f, 1f) }, 45f, 0f, -1f, true, 1f));
                Assert(seed > 0 && full > 4 * seed, "a seedling covers " + seed + " cells and the grown tree " + full);
                Assert(Math.Abs(RM_SunHeatMath.CrownOpacity(1f, true, RM_TreeCrown.LeaflessFactor, 1f) - 0.3f) < 1e-6f, "leafless is not x 0.3");
                Assert(Math.Abs(RM_SunHeatMath.CrownOpacity(1f, false, RM_TreeCrown.LeaflessFactor, 0.5f) - 0.5f) < 1e-6f, "the dial does not scale");
                Assert(RM_SunHeatMath.CrownOpacity(1f, false, RM_TreeCrown.LeaflessFactor, 0f) == 0f, "dial 0 still shades");
                float[] off = ForestRaster(61, 61, new List<Tree> { new Tree(30, 50, 3f, 12f, 1f) }, 45f, 0f, -1f, false, 1f);
                int offCells = 0;
                for (int i = 0; i < off.Length; i++) if (off[i] > 0f) offCells++;
                float hcFull = RM_TreeCrown.Height(12f, RM_TreeCrown.HeightFactorDefault);
                Assert(offCells > 0 && offCells <= (int)Math.Ceiling(hcFull) + 1, "canopy off still casts " + offCells + " cells (want the trunk strip)");
                Console.WriteLine("  seedling " + seed + " cells, grown " + full + " cells, canopy off " + offCells + " (the trunk)");
            });

            Case("tree crowns: a synthetic dense Greentide forest is mostly shade, at least 60%", () =>
            {
                // Design §6 T2 (ruling option (a) of RIMMANDRAKE_RULE_TREE_SHADE_T2_MIASMA_MUD_GROWS_NO_FOREST): a dense
                // forest map is mostly shade. The stand-in is the design §2.2 estimate's ordinary-tree forest, 3.8-cell
                // trees at 0.70, growth uniform 0.3-1, at the Greentide's E 45. The live census
                // (design/specs/2026-11-26-tree-crowns/canopy_census_2026-11-26.md) measured a real Greentide map at
                // 0.974. No Miasma clause and no estimate clause: the estimate puts trees on every cell, and the
                // Miasma's mud grows few (0.274 measured).
                var greentide = SyntheticForest(200, 200, 0.70, new[] { new Spec(1f, 1.5f, 3.8f) }, 1);
                double g = Covered(ForestRaster(200, 200, greentide, 45f, 0f, -1f, true, 1f)) / 40000.0;
                Console.WriteLine("  covered: Greentide stand-in " + g.ToString("0.00"));
                Assert(g >= 0.60, "a dense forest is not mostly shade: " + g);
            });

            Case("tree crowns: a 7x7 clearing is sunlit at its centre once hc x cot E + r falls short of its edge", () =>
            {
                // Full-grown 3.8-cell trees on every cell outside a 7x7 clearing. The edge tree up-sun stands 4 cells from
                // the centre; its crown disc (r 1.52) lands hc x cot E (hc 1.9) closer. Geometry gives sun at the centre
                // iff 4 - 1.9 cot E > 1.52, that is E > 37.5 degrees (design §6 T2 guessed 30).
                const int n = 41, c = 20;
                var trees = new List<Tree>();
                for (int z = 0; z < n; z++)
                    for (int x = 0; x < n; x++)
                        if (Math.Abs(x - c) > 3 || Math.Abs(z - c) > 3) trees.Add(new Tree(x, z, 3.8f, 3.8f, 1f));
                foreach (float e in new[] { 38f, 45f, 60f, 75f, 90f })
                {
                    float centre = ForestRaster(n, n, trees, e, 0f, -1f, true, 1f)[c * n + c];
                    Assert(centre == 0f, "the clearing's centre is shaded " + centre + " at E " + e);
                }
                float at30 = ForestRaster(n, n, trees, 30f, 0f, -1f, true, 1f)[c * n + c];
                Assert(at30 > 0.99f, "at E 30 the up-sun edge tree's crown should cover the centre (geometry), shade " + at30);
                Console.WriteLine("  clearing centre: full sun at E >= 38, shaded at E 30 by the up-sun edge crown");
            });

            Case("tree crowns: removing a tree and recomputing clears its footprint; growing it widens it", () =>
            {
                var trees = new List<Tree> { new Tree(10, 40, 1.5f, 3.8f, 1f), new Tree(40, 40, 3f, 12f, 0.3f) };
                float[] both = ForestRaster(61, 61, trees, 45f, 0f, -1f, true, 1f);
                float[] one = ForestRaster(61, 61, trees.GetRange(0, 1), 45f, 0f, -1f, true, 1f);
                float[] alone = ForestRaster(61, 61, trees.GetRange(1, 1), 45f, 0f, -1f, true, 1f);
                for (int i = 0; i < both.Length; i++)
                {
                    Assert(!(alone[i] > 0f && one[i] == 0f && both[i] == 0f), "the felled tree's cell was never shaded");
                    Assert(one[i] == 0f || both[i] > 0f, "a cell lost its shade from the tree that stayed");
                    if (alone[i] > 0f && i % 61 > 25) Assert(one[i] == 0f, "the felled tree's shade remains at cell " + i);
                }
                trees[1] = new Tree(40, 40, 3f, 12f, 1f);
                int grown = Covered(ForestRaster(61, 61, trees.GetRange(1, 1), 45f, 0f, -1f, true, 1f));
                Assert(grown > Covered(alone), "growth did not widen the shade: " + Covered(alone) + " -> " + grown);
            });

            Case("tree crowns: a 275x275 raster at Greentide density takes at most 15 ms", () =>
            {
                // RM_Greentide stand-in: 0.79 caster cells, 3% greatbole 12-16 (factors 0.97 / 0.79), 10% veluthar and
                // kaddrath 8-11.5, the rest 1.5-3.8. Best of 3; the raster only (the live Recompute adds its thing scan).
                var forest = SyntheticForest(275, 275, 0.79, new[] { new Spec(0.03f, 12f, 16f, 0.97f, 0.79f), new Spec(0.10f, 8f, 11.5f), new Spec(0.87f, 1.5f, 3.8f) }, 3);
                ForestRaster(275, 275, forest, 45f, 0f, -1f, true, 1f);   // JIT warm-up
                double best = double.MaxValue;
                for (int k = 0; k < 3; k++)
                {
                    var sw = System.Diagnostics.Stopwatch.StartNew();
                    ForestRaster(275, 275, forest, 45f, 0f, -1f, true, 1f);
                    sw.Stop();
                    best = Math.Min(best, sw.Elapsed.TotalMilliseconds);
                }
                Console.WriteLine("  T5 MEASURED: " + forest.Count + " trees on 275x275, raster " + best.ToString("0.00") + " ms (bar 15 ms)");
                Assert(best <= 15.0, "the raster took " + best.ToString("0.00") + " ms");
            });

            Case("tree crowns: a rebuilt grid from the same trees is bit-identical, in any order", () =>
            {
                var forest = SyntheticForest(120, 120, 0.6, new[] { new Spec(0.1f, 7f, 12f), new Spec(0.9f, 1.5f, 3.8f) }, 4);
                // Every third tree leafless (crown 0.3): overlapping crowns of two depths, so only a max is order-free.
                for (int i = 0; i < forest.Count; i += 3) { Tree t = forest[i]; t.leafless = true; forest[i] = t; }
                float[] a = ForestRaster(120, 120, forest, 41f, 0.6f, -0.8f, true, 1f);
                float[] b = ForestRaster(120, 120, forest, 41f, 0.6f, -0.8f, true, 1f);
                var shuffled = new List<Tree>(forest);
                var rng = new Random(9);
                for (int i = shuffled.Count - 1; i > 0; i--) { int j = rng.Next(i + 1); Tree t = shuffled[i]; shuffled[i] = shuffled[j]; shuffled[j] = t; }
                float[] c = ForestRaster(120, 120, shuffled, 41f, 0.6f, -0.8f, true, 1f);
                Assert(SameGrid(a, b), "two rebuilds differ");
                Assert(SameGrid(a, c), "a rebuild in another order differs (a loaded save iterates its things in its own order)");
            });

            foreach (string p in Pass) Console.WriteLine("PASS " + p);
            foreach (string f in Fail) Console.WriteLine("FAIL " + f);
            Console.WriteLine(Pass.Count + "/" + (Pass.Count + Fail.Count) + " passed");
            return Fail.Count == 0 ? 0 : 1;
        }

        // ── TREE_SHADE_SELFTEST_PROVE_FOREST_IS_SHADE helpers ──

        private struct Tree
        {
            public int x, z;
            public float vmin, vmax, growth, rf, hf, opacity;
            public bool leafless;

            public Tree(int x, int z, float vmin, float vmax, float growth, float rf = RM_TreeCrown.RadiusFactorDefault,
                float hf = RM_TreeCrown.HeightFactorDefault)
            {
                this.x = x; this.z = z; this.vmin = vmin; this.vmax = vmax; this.growth = growth;
                this.rf = rf; this.hf = hf; opacity = RM_TreeCrown.OpacityDefault; leafless = false;
            }
        }

        private struct Spec
        {
            public float share, vmin, vmax, rf, hf;

            public Spec(float share, float vmin, float vmax, float rf = RM_TreeCrown.RadiusFactorDefault, float hf = RM_TreeCrown.HeightFactorDefault)
            {
                this.share = share; this.vmin = vmin; this.vmax = vmax; this.rf = rf; this.hf = hf;
            }
        }

        /// <summary>The tree part of RM_MapComponent_ShadeGrid.Recompute on a bare grid at sun elevation E along
        /// (dirX, dirZ): each tree's trunk strip (CastInto, height hc, cap 16, tip 0.6) into the cast layer and its crown
        /// (CastCrown) into the canopy layer, merged by max. canopyOn false = the setting off.</summary>
        private static float[] ForestRaster(int w, int h, List<Tree> trees, float e, float dirX, float dirZ, bool canopyOn, float strength)
        {
            float[] cast = new float[w * h];
            float[] canopy = new float[w * h];
            int[] owner = new int[w * h];
            float cot = RM_SunHeatMath.ShadowLengthPerHeight(e);
            for (int k = 0; k < trees.Count; k++)
            {
                Tree t = trees[k];
                float s = RM_SunHeatMath.DrawnSize(1f, t.vmin, t.vmax, t.growth);
                float hc = RM_TreeCrown.Height(s, t.hf);
                RM_SunHeatMath.CastInto(cast, w, h, t.x, t.z, dirX, dirZ, RM_SunHeatMath.ShadowLength(hc, cot, 16f), 0.6f);
                if (canopyOn)
                {
                    float o = RM_SunHeatMath.CrownOpacity(t.opacity, t.leafless, RM_TreeCrown.LeaflessFactor, strength);
                    RM_SunHeatMath.CastCrown(canopy, w, h, t.x, t.z, RM_TreeCrown.Radius(s, t.rf), hc, dirX, dirZ, cot, 16f, o, owner, k);
                }
            }
            for (int i = 0; i < cast.Length; i++)
            {
                if (canopy[i] > cast[i]) cast[i] = canopy[i];
            }
            return cast;
        }

        private static List<Tree> SyntheticForest(int w, int h, double density, Spec[] specs, int seed)
        {
            var rng = new Random(seed);
            var trees = new List<Tree>();
            float total = 0f;
            foreach (Spec sp in specs) total += sp.share;
            for (int z = 0; z < h; z++)
                for (int x = 0; x < w; x++)
                {
                    if (rng.NextDouble() > density) continue;
                    double r = rng.NextDouble() * total, acc = 0;
                    Spec pick = specs[specs.Length - 1];
                    foreach (Spec sp in specs) { acc += sp.share; if (r <= acc) { pick = sp; break; } }
                    float g = 0.3f + 0.7f * (float)rng.NextDouble();
                    trees.Add(new Tree(x, z, pick.vmin, pick.vmax, g, pick.rf, pick.hf));
                }
            return trees;
        }

        /// <summary>Cells at full shade (the estimate's "covered").</summary>
        private static int Covered(float[] g)
        {
            int n = 0;
            for (int i = 0; i < g.Length; i++) if (g[i] >= 0.99f) n++;
            return n;
        }

        private static bool SameGrid(float[] a, float[] b)
        {
            if (a.Length != b.Length) return false;
            for (int i = 0; i < a.Length; i++) if (BitConverter.ToInt32(BitConverter.GetBytes(a[i]), 0) != BitConverter.ToInt32(BitConverter.GetBytes(b[i]), 0)) return false;
            return true;
        }

        private sealed class GearSpec
        {
            public string mode;
            public float depth;
        }

        /// <summary>The sun elevations the item names (DIRECT_SUN_SELFTEST_BUILD_EVERY_BIOME_EQUAL).</summary>
        private static readonly float[] Elevations = { 0f, 5f, 14f, 21f, 31f, 45f, 56f, 79f, 90f };

        /// <summary>Cast shade at the k-th cell down-sun of a height-1 wall at elevation E, through the shipped
        /// ShadowLengthPerHeight, ShadowLength (cap 16, RM_MapComponent_ShadeGrid.MaxCastCells) and CastInto (tip 0.6).</summary>
        private static float LeeShadeBehindWall(float e, int k)
        {
            const int w = 40, h = 3;
            float[] grid = new float[w * h];
            float len = RM_SunHeatMath.ShadowLength(1f, RM_SunHeatMath.ShadowLengthPerHeight(e), 16f);
            RM_SunHeatMath.CastInto(grid, w, h, 2, 1, 1f, 0f, len, 0.6f);
            return grid[1 * w + 2 + k];
        }

        /// <summary>Exposure in the cell the piece shades: worn (parasol) or stood under (tent).</summary>
        private static float ExposureUnderGear(GearSpec g, float stuffBonus)
        {
            float d = RM_SunHeatMath.GearDepth(g.depth, stuffBonus);
            if (g.mode == "wearer")
            {
                return RM_SunHeatMath.WithCover(RM_SunHeatMath.Exposure(true, 0f, 0f), d);
            }
            float[] t = new float[9];
            RM_SunHeatMath.FillRect(t, 3, 3, 0, 0, 2, 2, d);
            return RM_SunHeatMath.Exposure(true, 0f, 0f, t[4]);
        }

        /// <summary>Felt temperature on an open, unroofed cell under a sun at E (55 x sin E), optionally with the
        /// piece in use: worn (parasol) or stood under (tent), through the same RM_SunHeatMath calls
        /// RM_MapComponent_ShadeGrid makes.</summary>
        private static float FeltWithGear(GearSpec g, float stuffBonus, float e, bool withGear = false)
        {
            float ex = withGear ? ExposureUnderGear(g, stuffBonus) : RM_SunHeatMath.Exposure(true, 0f, 0f);
            return OutdoorC + RM_DirectSun.FeltOffsetC(ex, RM_SunHeatMath.DirectSunOffsetC(55f, e), 1f, 1f);
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

        /// <summary>The pieces' RM_CompProperties_ShadeGear, and mirrak
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
