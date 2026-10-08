// Approach B for Colony Visibility: seeded fuzz over the Verse-free kernel the mod calls (../../Kernel/RM_VisibilityKernel.cs), each family
// checked against an independent restatement of the ruled rules (Annex A curve, halving per season, 5..15 launch reset) and cross-function properties:
//   band    the five-band ladder: edges at 20/40/60/80, monotone, every dial value has exactly one band
//   curve   the threat curve and the strength slider: exact at the ruled nodes, monotone, bounded, 1.0x at dial 50 for every strength
//   dial    random sequences of adjust / launch-reset / tile-memory arrival against a double-precision ledger: the dial never leaves 0..100
//   memory  tile-memory decay: halved per season away, never grows, an arrival only ever raises the dial and never above the remembered value
//   points  raid-point scaling: factor 1 is "no effect" for every input (including points outside the clamps), direction follows the factor
// A failing case prints `family seed N: message`; --fuzz-seed N replays it. PROVISIONAL: the curve values and 0.15x launch multiplier are
// owner-ruled design numbers; the global point floor used here (35) is vanilla's current value, the properties hold for any floor.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using RimMandrake.Visibility;

namespace RimMandrake.Visibility.SelfTest
{
    internal static class VisibilityFuzz
    {
        public static long Cases, Steps, Restores, Launches, Clamped, Scaled;
        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }
        private static float F(Random r, float lo, float hi) { return lo + (float)r.NextDouble() * (hi - lo); }
        private const float Season = 900000f;

        // independent restatement of the ruled curve, in double
        private static double SpecCurve(double v)
        {
            double[] x = { 0, 25, 50, 75, 100 }, y = { 0.55, 0.80, 1.00, 1.25, 1.60 };
            if (v <= 0) return 0.55;
            if (v >= 100) return 1.60;
            for (int i = 1; i < 5; i++)
                if (v <= x[i]) return y[i - 1] + (y[i] - y[i - 1]) * (v - x[i - 1]) / (x[i] - x[i - 1]);
            return 1.60;
        }

        private static List<string> Band(int cases, int seed0)
        {
            var fails = new List<string>();
            for (int c = 0; c < cases; c++)
            {
                int seed = seed0 + c; var r = new Random(seed); Cases++;
                try
                {
                    int prev = 0; float prevV = -1000f;
                    var vs = new List<float> { -50f, -0.001f, 0f, 19.999f, 20f, 39.999f, 40f, 59.999f, 60f, 79.999f, 80f, 100f, 150f };
                    for (int i = 0; i < 40; i++) vs.Add(F(r, -20f, 120f));
                    vs.Sort();
                    foreach (float v in vs)
                    {
                        Steps++;
                        int b = RM_VisibilityKernel.BandFor(v);
                        int want = v < 0 ? 0 : (int)Math.Min(4, Math.Floor(v / 20.0));
                        // the float edge 19.999f etc. is exact; guard double rounding at the edges by comparing against the float thresholds
                        if (v >= 20f && v < 40f) want = 1; else if (v >= 40f && v < 60f) want = 2; else if (v >= 60f && v < 80f) want = 3; else if (v >= 80f) want = 4; else want = 0;
                        Check(b == want, $"BandFor({v}) = {b}, want {want}");
                        Check(b >= prev, $"band fell from {prev} to {b} as the dial rose ({prevV} -> {v})");
                        prev = b; prevV = v;
                    }
                    Check(RM_VisibilityKernel.BandWidth * 5 == RM_VisibilityKernel.Max, "five bands of width BandWidth must tile 0..100");
                }
                catch (Exception e) { fails.Add($"band seed {seed}: {e.Message}"); }
            }
            return fails;
        }

        private static List<string> Curve(int cases, int seed0)
        {
            var fails = new List<string>();
            for (int c = 0; c < cases; c++)
            {
                int seed = seed0 + c; var r = new Random(seed); Cases++;
                try
                {
                    float[] nodes = { 0f, 25f, 50f, 75f, 100f }; float[] vals = { 0.55f, 0.80f, 1.00f, 1.25f, 1.60f };
                    for (int i = 0; i < 5; i++) Check(Math.Abs(RM_VisibilityKernel.ThreatFactor(nodes[i]) - vals[i]) < 1e-6f, $"curve at node {nodes[i]} is not {vals[i]}");
                    Check(RM_VisibilityKernel.ThreatFactor(-40f) == 0.55f && RM_VisibilityKernel.ThreatFactor(400f) == 1.60f, "curve not flat beyond its ends");
                    float prev = 0f; float s = F(r, 0f, 2f);
                    for (int i = 0; i <= 100; i++)
                    {
                        Steps++;
                        float v = i + F(r, -0.4f, 0.4f);
                        v = Math.Max(0f, Math.Min(100f, v));
                        float f = RM_VisibilityKernel.ThreatFactor(v);
                        Check(Math.Abs(f - SpecCurve(v)) < 1e-4, $"ThreatFactor({v}) = {f}, spec {SpecCurve(v)}");
                        Check(f >= 0.55f - 1e-6f && f <= 1.60f + 1e-6f, "curve left its ruled bounds");
                        float sf = RM_VisibilityKernel.ScaledThreatFactor(f, s);
                        Check(sf > 0f, $"scaled factor {sf} not positive at strength {s}: a raid would be deleted or inverted");
                        Check(Math.Abs(sf - (1.0 + (f - 1.0) * s)) < 1e-5, "scaled factor is not the lerp from 1");
                        // direction: more visibility never lowers a raid, any strength in 0..2
                        if (i > 0 && v >= prev) Check(RM_VisibilityKernel.ScaledThreatFactor(RM_VisibilityKernel.ThreatFactor(prev), s) <= sf + 1e-6f, "scaled factor fell as visibility rose");
                        prev = v;
                    }
                    Check(RM_VisibilityKernel.ScaledThreatFactor(RM_VisibilityKernel.ThreatFactor(50f), s) == 1f, "dial 50 must be 1.0x at every strength");
                    Check(RM_VisibilityKernel.ScaledThreatFactor(0.55f, 0f) == 1f && RM_VisibilityKernel.ScaledThreatFactor(1.6f, 0f) == 1f, "strength 0 must be no effect");
                    Check(Math.Abs(RM_VisibilityKernel.ScaledThreatFactor(1.6f, 1f) - 1.6f) < 1e-6f, "strength 1 must be the ruled curve");
                }
                catch (Exception e) { fails.Add($"curve seed {seed}: {e.Message}"); }
            }
            return fails;
        }

        private enum Op { Adjust, Launch, Depart, Wait, Arrive }

        private static List<string> Dial(int cases, int seed0)
        {
            var fails = new List<string>();
            for (int c = 0; c < cases; c++)
            {
                int seed = seed0 + c; var r = new Random(seed); Cases++;
                try
                {
                    float dial = F(r, 0f, 100f); double ledger = dial;
                    float mult = F(r, 0.05f, 0.5f);
                    bool hasMem = false; float memV = 0f; int memAt = 0; int now = 0;
                    int n = 10 + r.Next(60);
                    for (int i = 0; i < n; i++)
                    {
                        Steps++;
                        Op op = (Op)r.Next(5);
                        switch (op)
                        {
                            case Op.Adjust:
                                {
                                    float d = r.Next(4) == 0 ? F(r, -300f, 300f) : new[] { 3f, 8f, 20f, -3f, -8f, -20f }[r.Next(6)];
                                    float after = RM_VisibilityKernel.Adjust(dial, d);
                                    ledger = Math.Max(0.0, Math.Min(100.0, ledger + d));
                                    if (dial + d < 0f || dial + d > 100f) Clamped++;
                                    dial = after;
                                    break;
                                }
                            case Op.Launch:
                                {
                                    float after = RM_VisibilityKernel.ResetOnLaunch(dial, mult);
                                    Check(after >= 5f && after <= 15f, $"launch reset left the dial at {after}, outside 5..15");
                                    double spec = Math.Max(5.0, Math.Min(15.0, (double)dial * mult));
                                    Check(Math.Abs(after - spec) < 1e-3, $"launch reset {dial} x {mult} = {after}, spec {spec}");
                                    dial = after; ledger = after; Launches++;
                                    break;
                                }
                            case Op.Depart: hasMem = true; memV = dial; memAt = now; break;
                            case Op.Wait: now += (int)F(r, 0f, 3.5f * Season); break;
                            case Op.Arrive:
                                if (hasMem)
                                {
                                    float decayed = RM_VisibilityKernel.DecayedTileVisibility(memV, now - memAt);
                                    float delta = RM_VisibilityKernel.RestoreDelta(dial, decayed);
                                    Check(delta >= 0f, "restore delta negative: arrival lowered the dial");
                                    float after = RM_VisibilityKernel.Adjust(dial, delta);
                                    Check(after >= dial - 1e-4f, $"arrival lowered the dial {dial} -> {after}");
                                    Check(after <= Math.Max(dial, memV) + 1e-3f, $"arrival raised the dial to {after}, above both the present {dial} and the remembered {memV}");
                                    Check(Math.Abs(after - Math.Max(dial, decayed)) < 1e-3f, "arrival did not land on max(dial, decayed memory)");
                                    dial = after; ledger = after; Restores++;
                                }
                                break;
                        }
                        Check(!float.IsNaN(dial) && dial >= 0f && dial <= 100f, $"dial {dial} left 0..100 after {op}");
                        Check(Math.Abs(dial - ledger) < 1e-2, $"dial {dial} drifted from the double-precision ledger {ledger} after {op}");
                    }
                }
                catch (Exception e) { fails.Add($"dial seed {seed}: {e.Message}"); }
            }
            return fails;
        }

        private static List<string> Memory(int cases, int seed0)
        {
            var fails = new List<string>();
            for (int c = 0; c < cases; c++)
            {
                int seed = seed0 + c; var r = new Random(seed); Cases++;
                try
                {
                    float v0 = F(r, 0f, 100f);
                    Check(RM_VisibilityKernel.DecayedTileVisibility(v0, 0) == v0, "no time away must not decay");
                    Check(RM_VisibilityKernel.DecayedTileVisibility(v0, -12345) == v0, "negative time away must not grow or decay the memory");
                    Check(RM_VisibilityKernel.SeasonsAway(-1) == 0f && RM_VisibilityKernel.SeasonsAway(0) == 0f, "seasons away negative");
                    Check(Math.Abs(RM_VisibilityKernel.SeasonsAway((int)Season) - 1f) < 1e-6f, "a season is 900000 ticks");
                    float prev = v0 + 1f;
                    for (int k = 0; k <= 8; k++)
                    {
                        Steps++;
                        int ticks = (int)(k * Season);
                        float d = RM_VisibilityKernel.DecayedTileVisibility(v0, ticks);
                        Check(Math.Abs(d - v0 / Math.Pow(2.0, k)) < 1e-3 + v0 * 1e-5, $"after {k} seasons the memory is {d}, halving gives {v0 / Math.Pow(2.0, k)}");
                        Check(d <= prev, "memory grew with time away");
                        Check(d >= 0f, "memory negative");
                        prev = d;
                    }
                    // monotone within a season at random ticks
                    int t0 = r.Next(0, (int)(4 * Season)); int t1 = t0 + r.Next(0, 100000);
                    Check(RM_VisibilityKernel.DecayedTileVisibility(v0, t1) <= RM_VisibilityKernel.DecayedTileVisibility(v0, t0) + 1e-5f, "decay not monotone");
                    // RestoreDelta algebra
                    float dial = F(r, 0f, 100f), dec = F(r, 0f, 100f);
                    float rd = RM_VisibilityKernel.RestoreDelta(dial, dec);
                    Check(rd >= 0f && Math.Abs((dial + rd) - Math.Max(dial, dec)) < 1e-3f, "RestoreDelta does not land on max(dial, decayed)");
                }
                catch (Exception e) { fails.Add($"memory seed {seed}: {e.Message}"); }
            }
            return fails;
        }

        private static List<string> Points(int cases, int seed0)
        {
            var fails = new List<string>();
            for (int c = 0; c < cases; c++)
            {
                int seed = seed0 + c; var r = new Random(seed); Cases++;
                try
                {
                    float min = 35f;
                    for (int i = 0; i < 40; i++)
                    {
                        Steps++;
                        float p = i < 8 ? new[] { 0.5f, 10f, 34.9f, 35f, 36f, 9999f, 10000f, 25000f }[i] : F(r, 1f, 14000f);
                        float f = i % 5 == 0 ? 1f : F(r, 0.1f, 3.2f);
                        float got = RM_VisibilityKernel.ScalePoints(p, f, min);
                        Scaled++;
                        Check(!float.IsNaN(got) && got > 0f, $"ScalePoints({p},{f}) = {got}");
                        if (f == 1f) Check(got == p, $"factor 1 changed {p} to {got}: strength 0 / the middle of the curve must be no effect");
                        if (f >= 1f) Check(got >= p, $"factor {f} lowered {p} to {got}");
                        if (f <= 1f) Check(got <= p, $"factor {f} raised {p} to {got}");
                        Check(got >= Math.Min(p, min) - 1e-3f && got <= Math.Max(p, 10000f) + 1e-3f, $"{p} x {f} = {got} left [min(p,floor), max(p,cap)]");
                        if (p >= min && p <= 10000f) Check(got >= min - 1e-3f && got <= 10000f + 1e-3f, "an in-range raid left the clamp range");
                        float want = p * f;
                        if (want >= Math.Min(p, min) && want <= Math.Max(p, 10000f)) Check(Math.Abs(got - want) < 1e-4f * Math.Max(1f, want) + 1e-3f, $"unclamped {p} x {f} should be {want}, got {got}");
                    }
                }
                catch (Exception e) { fails.Add($"points seed {seed}: {e.Message}"); }
            }
            return fails;
        }

        public static bool Run(double scale, int? oneSeed, string only)
        {
            var sw = Stopwatch.StartNew();
            bool ok = true;
            int N(int n) { return oneSeed.HasValue ? 1 : (int)(n * scale); }
            int S(int baseSeed) { return oneSeed ?? baseSeed; }
            var fam = new (string name, Func<List<string>> run)[]
            {
                ("band", () => Band(N(1500), S(1))),
                ("curve", () => Curve(N(2000), S(1))),
                ("dial", () => Dial(N(4000), S(1))),
                ("memory", () => Memory(N(3000), S(1))),
                ("points", () => Points(N(3000), S(1))),
            };
            foreach (var f in fam)
            {
                if (only != null && f.name != only) continue;
                long c0 = Cases, s0 = Steps; var t = Stopwatch.StartNew();
                var fails = f.run();
                Console.WriteLine($"fuzz {f.name}: {Cases - c0} cases, {Steps - s0} steps, {t.Elapsed.TotalSeconds:F2}s, {(fails.Count == 0 ? "0 failures" : fails.Count + " FAILURES")}");
                foreach (var m in fails.Take(8)) Console.WriteLine("FAIL " + m);
                if (fails.Count > 0) ok = false;
            }
            if (only != null && !fam.Any(f => f.name == only)) { Console.WriteLine("FAIL unknown --fuzz-only family: " + only); return false; }
            if (Cases == 0) { Console.WriteLine("FAIL no cases ran (--fuzz-scale too small?); a fuzz that checked nothing is not a pass"); return false; }
            if (only == null && !oneSeed.HasValue && scale >= 1)
            {
                Console.WriteLine($"reached: restores {Restores}, launches {Launches}, clamped adjusts {Clamped}, scaled raids {Scaled}");
                if (Restores == 0 || Launches == 0 || Clamped == 0 || Scaled == 0) { Console.WriteLine("FAIL visibility fuzz never reached a path (blind)"); ok = false; }
            }
            Console.WriteLine($"visibility fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
