// Approach B for ProximityHatch: seeded fuzz over the Verse-free kernel the comp calls (../Kernel/RM_ProximityHatchKernel.cs):
//   cadence    random tick / settings / spawn sequences through the production countdown, against an independent elapsed-counter model
//   radius     interval and radius maths: bounds, rounding, monotonicity
//   nearest    the nearest-pawn pick against a sort oracle (ties keep the first, empty is -1)
//   gates      every decision table exhaustively against a restated truth table, plus the cross-table safety properties
//   lifecycle  a whole egg on a small grid: pawns walk in and out, the egg hatches at most once, never when off, within one interval
// A failing sequence is shrunk (delta debugging) and printed as `family seed N: message | actions`; --fuzz-seed N replays it.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace RimMandrake.ProximityHatch.SelfTest
{
    internal static class ProximityHatchFuzz
    {
        public static long Cases, Steps, Scans, Hatches, SkippedDisabled, Latencies;
        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }

        internal static List<T> Shrink<T>(List<T> acts, Func<List<T>, bool> fails)
        {
            var cur = new List<T>(acts);
            for (int chunk = Math.Max(1, cur.Count / 2); chunk >= 1; chunk /= 2)
            {
                bool progress = true;
                while (progress)
                {
                    progress = false;
                    for (int i = 0; i + chunk <= cur.Count; i++)
                    {
                        var trial = new List<T>(cur);
                        trial.RemoveRange(i, chunk);
                        if (fails(trial)) { cur = trial; progress = true; break; }
                    }
                }
            }
            return cur;
        }

        // ════════════════════════ cadence ════════════════════════
        private enum A { Tick, Mult, Base, Fire, Unspawn, Respawn, Reload }
        private struct Act
        {
            public A kind; public int a;
            public override string ToString() { return kind + "(" + a + ")"; }
        }

        private static readonly float[] Mults = { 0.25f, 0.5f, 1f, 1.5f, 2f, 3f, 4f };
        private static readonly int[] Bases = { 1, 2, 7, 30, 60, 61, 120, 600 };

        private static Act[] GenActs(Random r, int len)
        {
            var a = new Act[len];
            for (int i = 0; i < len; i++)
            {
                int k = r.Next(100);
                A kind = k < 70 ? A.Tick : k < 78 ? A.Mult : k < 86 ? A.Base : k < 88 ? A.Fire : k < 93 ? A.Unspawn : k < 97 ? A.Respawn : A.Reload;
                a[i] = new Act { kind = kind, a = r.Next(1 << 12) };
            }
            return a;
        }

        // the comp, as CompTick drives the kernel
        private sealed class Egg
        {
            public int ticksUntilScan; public bool fired, spawned = true; public int baseTicks = 60; public float mult = 1f;
            public int scans;
            public void Tick()
            {
                if (!RM_ProximityHatchKernel.TicksNow(fired, spawned)) return;
                if (!RM_ProximityHatchKernel.CountdownStep(ref ticksUntilScan, RM_ProximityHatchKernel.ScanInterval(baseTicks, mult))) return;
                scans++;
            }
        }

        private static string RunCadence(IList<Act> acts, bool count)
        {
            var e = new Egg();
            // independent model: elapsed ticks since the last scan against the interval armed at that scan (the first tick always scans)
            int elapsed = 0, armed = 1, modelScans = 0;
            int stepNo = 0;
            try
            {
                foreach (var a in acts)
                {
                    stepNo++;
                    if (count) Steps++;
                    switch (a.kind)
                    {
                        case A.Tick:
                            int before = e.scans;
                            e.Tick();
                            bool running = !e.fired && e.spawned;
                            bool modelScan = false;
                            if (running)
                            {
                                elapsed++;
                                if (elapsed >= armed)
                                {
                                    modelScan = true;
                                    modelScans++;
                                    elapsed = 0;
                                    armed = Math.Max(1, (int)Math.Round(e.baseTicks * e.mult));
                                }
                            }
                            Check((e.scans - before == 1) == modelScan, "scan " + (e.scans - before == 1) + " but model says " + modelScan + " (elapsed " + elapsed + ", armed " + armed + ")");
                            Check(!(e.fired && e.scans != before), "a fired egg scanned");
                            Check(e.ticksUntilScan >= 0 && e.ticksUntilScan <= Math.Max(armed, 1), "countdown " + e.ticksUntilScan + " outside 0.." + armed);
                            if (count && modelScan) Scans++;
                            break;
                        case A.Mult: e.mult = Mults[a.a % Mults.Length]; break;
                        case A.Base: e.baseTicks = Bases[a.a % Bases.Length]; break;
                        case A.Fire: e.fired = true; break;
                        case A.Unspawn: e.spawned = false; break;
                        case A.Respawn: e.spawned = true; break;
                        case A.Reload:
                            // save/load round-trips the countdown only; the interval is re-read from def and settings
                            int saved = e.ticksUntilScan;
                            e = new Egg { ticksUntilScan = saved, fired = e.fired, spawned = e.spawned, baseTicks = e.baseTicks, mult = e.mult, scans = e.scans };
                            break;
                    }
                }
            }
            catch (Exception ex) { return "step " + stepNo + ": " + ex.Message; }
            return null;
        }

        private static List<string> Cadence(int n, int seed0)
        {
            var fails = new List<string>();
            for (int s = seed0; s < seed0 + n; s++)
            {
                Cases++;
                var r = new Random(s * 7919 + 11);
                var acts = GenActs(r, 20 + r.Next(380)).ToList();
                string msg = RunCadence(acts, true);
                if (msg != null)
                {
                    var small = Shrink(acts, t => RunCadence(t, false) != null);
                    fails.Add("cadence seed " + s + ": " + RunCadence(small, false) + " | " + string.Join(" ", small));
                    if (fails.Count >= 3) break;
                }
            }
            return fails;
        }

        // ════════════════════════ radius ════════════════════════
        private static List<string> Radius(int n, int seed0)
        {
            var fails = new List<string>();
            for (int s = seed0; s < seed0 + n && fails.Count < 3; s++)
            {
                Cases++; Steps++;
                var r = new Random(s * 31 + 5);
                try
                {
                    int b = r.Next(1, 100000); float m = 0.25f + (float)r.NextDouble() * 3.75f;
                    int iv = RM_ProximityHatchKernel.ScanInterval(b, m);
                    Check(iv >= 1, "interval " + iv + " < 1 for base " + b + " mult " + m);
                    double exact = (double)(b * m);
                    Check(Math.Abs(iv - exact) <= 0.5 + 1e-6 || iv == 1, "interval " + iv + " is not the rounded product " + exact);
                    Check(RM_ProximityHatchKernel.ScanInterval(b, 1f) == b, "multiplier 1 changed the interval " + b);
                    float m2 = m + (float)r.NextDouble();
                    Check(RM_ProximityHatchKernel.ScanInterval(b, m2) >= iv, "interval fell as the multiplier rose " + m + "->" + m2 + " base " + b);
                    Check(RM_ProximityHatchKernel.ScanInterval(b + 5, m) >= iv, "interval fell as the base rose");
                    Check(RM_ProximityHatchKernel.ScanInterval(0, m) == 1 && RM_ProximityHatchKernel.ScanInterval(-3, m) == 1, "a zero/negative base interval must clamp to 1");
                    Check(RM_ProximityHatchKernel.ScanInterval(1, 0.25f) == 1 && RM_ProximityHatchKernel.ScanInterval(2, 0.25f) == 1 && RM_ProximityHatchKernel.ScanInterval(6, 0.25f) == 2, "half-to-even rounding at the .5 boundary");

                    float rb = (float)(r.NextDouble() * (r.Next(2) == 0 ? 0.6 : 40)); float rm = 0.25f + (float)r.NextDouble() * 2.75f;
                    float rad = RM_ProximityHatchKernel.Radius(rb, rm);
                    Check(RM_ProximityHatchKernel.MinRadius == 0.1f, "the documented radius floor is 0.1 cells");
                    Check(rad >= RM_ProximityHatchKernel.MinRadius, "radius " + rad + " below the floor");
                    Check(rb * rm < RM_ProximityHatchKernel.MinRadius || rad == rb * rm, "radius " + rad + " is not base*mult " + rb * rm);
                    Check(RM_ProximityHatchKernel.Radius(rb, rm + 0.5f) >= rad, "radius fell as the multiplier rose");
                    Check(RM_ProximityHatchKernel.Radius(rb + 1f, rm) >= rad, "radius fell as the base rose");
                    Check(RM_ProximityHatchKernel.Radius(0f, rm) == RM_ProximityHatchKernel.MinRadius && RM_ProximityHatchKernel.Radius(-4f, rm) == RM_ProximityHatchKernel.MinRadius && RM_ProximityHatchKernel.Radius(rb, 0f) == RM_ProximityHatchKernel.MinRadius, "a zero/negative radius must clamp to the floor");
                }
                catch (Exception e) { fails.Add("radius seed " + s + ": " + e.Message); }
            }
            return fails;
        }

        // ════════════════════════ nearest ════════════════════════
        private static List<string> Nearest(int n, int seed0)
        {
            var fails = new List<string>();
            Cases++;
            try
            {
                Check(RM_ProximityHatchKernel.PickNearest(new List<int>()) == -1, "empty list must pick -1");
                Check(RM_ProximityHatchKernel.PickNearest(new[] { 0 }) == 0, "a pawn on the egg's own cell (distance 0) must be picked");
                Check(RM_ProximityHatchKernel.PickNearest(new[] { 5, 5, 5 }) == 0, "ties keep the first");
            }
            catch (Exception e) { fails.Add("nearest fixed: " + e.Message); }
            for (int s = seed0; s < seed0 + n && fails.Count < 3; s++)
            {
                Cases++; Steps++;
                var r = new Random(s * 131 + 3);
                try
                {
                    int len = 1 + r.Next(40);
                    int span = 1 + r.Next(200);
                    var d = new List<int>();
                    for (int i = 0; i < len; i++) d.Add(r.Next(span));
                    int pick = RM_ProximityHatchKernel.PickNearest(d);
                    int min = d.Min();
                    Check(pick >= 0 && pick < d.Count, "pick " + pick + " out of range");
                    Check(d[pick] == min, "picked distance " + d[pick] + " but the minimum is " + min);
                    Check(d.IndexOf(min) == pick, "tie not resolved to the first minimum");
                    // permuting the candidates never changes the distance picked
                    var shuf = d.OrderBy(x => r.Next()).ToList();
                    Check(shuf[RM_ProximityHatchKernel.PickNearest(shuf)] == min, "shuffled list picked a farther pawn");
                    // removing a non-picked, non-minimal candidate never changes the distance picked
                    var rest = new List<int>(d); rest.RemoveAt(pick);
                    if (rest.Count > 0) Check(rest[RM_ProximityHatchKernel.PickNearest(rest)] >= min, "after removing the nearest, a nearer one appeared");
                }
                catch (Exception e) { fails.Add("nearest seed " + s + ": " + e.Message); }
            }
            return fails;
        }

        // ════════════════════════ gates ════════════════════════
        private static List<string> Gates()
        {
            var fails = new List<string>();
            Cases++;
            try
            {
                for (int m = 0; m < 32; m++)
                {
                    bool fired = (m & 1) != 0, spawned = (m & 2) != 0, enabled = (m & 4) != 0, hatcher = (m & 8) != 0, map = (m & 16) != 0;
                    Steps++;
                    bool want = !fired && spawned && enabled && hatcher && map;
                    bool got = RM_ProximityHatchKernel.MayScan(fired, spawned, enabled, hatcher, map);
                    Check(got == want, "MayScan(" + fired + "," + spawned + "," + enabled + "," + hatcher + "," + map + ") = " + got);
                    if (fired) Check(!got, "a fired egg may scan");
                    if (!enabled) Check(!got, "scan allowed with the master switch off");
                    if (got) Check(RM_ProximityHatchKernel.TicksNow(fired, spawned), "scan allowed on a tick the comp ignores");
                }
                for (int m = 0; m < 4; m++)
                {
                    Steps++;
                    bool fired = (m & 1) != 0, spawned = (m & 2) != 0;
                    Check(RM_ProximityHatchKernel.TicksNow(fired, spawned) == (!fired && spawned), "TicksNow(" + fired + "," + spawned + ")");
                }
                for (int m = 0; m < 8; m++)
                {
                    Steps++;
                    bool pawn = (m & 1) != 0, kind = (m & 2) != 0, there = (m & 4) != 0;
                    bool got = RM_ProximityHatchKernel.IsFreshHatchling(pawn, kind, there);
                    Check(got == (pawn && kind && !there), "IsFreshHatchling(" + pawn + "," + kind + "," + there + ") = " + got);
                    if (there) Check(!got, "a pawn already on the cell was taken for the hatchling");
                }
            }
            catch (Exception e) { fails.Add("gates: " + e.Message); }
            return fails;
        }

        // ════════════════════════ lifecycle ════════════════════════
        private sealed class Walker { public int x, y, vx, vy; public bool flesh = true, dead; }

        private static List<string> Lifecycle(int n, int seed0)
        {
            var fails = new List<string>();
            for (int s = seed0; s < seed0 + n && fails.Count < 3; s++)
            {
                Cases++;
                var r = new Random(s * 17 + 101);
                try
                {
                    var egg = new Egg { baseTicks = Bases[r.Next(Bases.Length)], mult = Mults[r.Next(Mults.Length)] };
                    bool enabled = r.Next(5) != 0;
                    float triggerRadius = 1 + (float)r.NextDouble() * 9; float radMult = 0.25f + (float)r.NextDouble() * 2.75f;
                    float radius = RM_ProximityHatchKernel.Radius(triggerRadius, radMult);
                    var walkers = new List<Walker>();
                    int count = r.Next(0, 6);
                    for (int i = 0; i < count; i++)
                        walkers.Add(new Walker { x = r.Next(-40, 40), y = r.Next(-40, 40), vx = r.Next(-2, 3), vy = r.Next(-2, 3), flesh = r.Next(4) != 0, dead = r.Next(8) == 0 });
                    int hatchedAt = -1, firstInRange = -1;
                    int ticks = 2000;
                    for (int t = 0; t < ticks; t++)
                    {
                        Steps++;
                        foreach (var w in walkers) { w.x += w.vx; w.y += w.vy; if (Math.Abs(w.x) > 60) w.vx = -w.vx; if (Math.Abs(w.y) > 60) w.vy = -w.vy; }
                        bool anyInRange = walkers.Any(w => w.flesh && !w.dead && (double)(w.x * w.x + w.y * w.y) <= (double)radius * radius);
                        if (anyInRange && firstInRange < 0 && !egg.fired) firstInRange = t;
                        int scansBefore = egg.scans;
                        egg.Tick();
                        if (egg.scans != scansBefore)
                        {
                            Scans++;
                            if (!RM_ProximityHatchKernel.MayScan(egg.fired, egg.spawned, enabled, true, true)) { SkippedDisabled++; continue; }
                            var cand = new List<Walker>(); var dist = new List<int>();
                            foreach (var w in walkers)
                                if (w.flesh && !w.dead && (double)(w.x * w.x + w.y * w.y) <= (double)radius * radius) { cand.Add(w); dist.Add(w.x * w.x + w.y * w.y); }
                            int pick = RM_ProximityHatchKernel.PickNearest(dist);
                            if (pick >= 0)
                            {
                                Check(hatchedAt < 0, "the egg hatched twice (second at tick " + t + ")");
                                Check(enabled, "hatched with the master switch off");
                                Check(dist[pick] == dist.Min(), "the egg woke the wrong pawn");
                                Check(!egg.fired, "scanning after fired");
                                egg.fired = true; hatchedAt = t; Hatches++;
                            }
                        }
                    }
                    if (hatchedAt >= 0) { Latencies++; Check(firstInRange >= 0 && hatchedAt >= firstInRange, "hatched at " + hatchedAt + " before any pawn was in range (first " + firstInRange + ")"); }
                    if (!enabled) Check(hatchedAt < 0, "an egg with the setting off hatched");
                }
                catch (Exception e) { fails.Add("lifecycle seed " + s + ": " + e.Message); }
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
                ("cadence", () => Cadence(N(4000), S(1))),
                ("radius", () => Radius(N(6000), S(1))),
                ("nearest", () => Nearest(N(6000), S(1))),
                ("gates", () => Gates()),
                ("lifecycle", () => Lifecycle(N(1500), S(1))),
            };
            foreach (var f in fam)
            {
                if (only != null && f.name != only) continue;
                long c0 = Cases, s0 = Steps; var t = Stopwatch.StartNew();
                var fails = f.run();
                Console.WriteLine($"fuzz {f.name}: {Cases - c0} cases, {Steps - s0} steps, {t.Elapsed.TotalSeconds:F2}s, {(fails.Count == 0 ? "0 failures" : fails.Count + " FAILURES")}");
                foreach (var m in fails) Console.WriteLine("FAIL " + m);
                if (fails.Count > 0) ok = false;
            }
            if (only != null && !fam.Any(f => f.name == only)) { Console.WriteLine("FAIL unknown --fuzz-only family: " + only); return false; }
            if (Cases == 0) { Console.WriteLine("FAIL no cases ran (--fuzz-scale too small?); a fuzz that checked nothing is not a pass"); return false; }
            if (only == null || only == "lifecycle")
            {
                Console.WriteLine($"reached: scans {Scans}, hatches {Hatches}, scans skipped by the gate {SkippedDisabled}");
                if (!oneSeed.HasValue && scale >= 1 && (Scans == 0 || Hatches == 0 || SkippedDisabled == 0)) { Console.WriteLine("FAIL lifecycle fuzz never reached a scan, a hatch and a gated scan (blind)"); ok = false; }
            }
            Console.WriteLine($"proximityhatch fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
