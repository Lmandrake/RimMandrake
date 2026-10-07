// Approach B for the Cathedral hum-mood: seeded random ACTION SEQUENCES over RM_AttitudeKernel, the Verse-free
// arithmetic RM_MapComponent_BiomeAttitude calls, with a random def per seed. The model of the component (which
// action does what, in the order MapComponentTick does it) is this file's own; every number comes from the kernel.
// Failures are shrunk by delta debugging and printed as `family seed N: message | actions`.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace RimMandrake.RustCathedral.Hum.SelfTest
{
    internal static class AttitudeFuzz
    {
        public static long Cases, Steps, DrainsApplied, DrainsClamped, WorstBandChecks, Falls;
        const int TicksPerDay = 60000;
        const int TicksPerHour = 2500;

        internal struct Act
        {
            public int kind, arg;
            public override string ToString()
            {
                string[] names = { "AddIrr", "Standing", "Check", "SetStage", "LineCycle", "Afk", "SetIrr" };
                return names[kind] + "(" + arg + ")";
            }
        }

        private sealed class Def
        {
            public List<float> thr; public float margin, weight, halfLife, rateSetting;
            public int interval, drainIntervalTicks, drainAmount, drainCap, layers, standingStart;
            public int[] ceiling = new int[3]; public float[] decayMult = new float[3];
            public int Worst => thr.Count;
        }

        private sealed class State
        {
            public Def d;
            public float irr; public int standing, currentBand = -1, displayBand = -1, stage;
            public bool lineCycleDrop, drainEnabled;
            public int lastDrain = -999999, anchor, drained, tick;
            // independent bookkeeping for the drain invariants
            public int refWindowSum, lastDrainTickSeen = int.MinValue;
        }

        private static Def MakeDef(Random r)
        {
            var d = new Def();
            int n = r.Next(1, 7);
            d.thr = new List<float>();
            float v = 0;
            for (int i = 0; i < n; i++) { v += 3f + (float)r.NextDouble() * 22f; d.thr.Add(Math.Min(v, 99f + i * 0f)); }
            d.thr.Sort();
            d.margin = r.Next(4) == 0 ? 0f : (float)r.NextDouble() * 20f;
            d.weight = r.Next(5) == 0 ? 0f : (float)r.NextDouble() * 2f;
            d.halfLife = 0.05f + (float)r.NextDouble() * 5f;
            d.rateSetting = 0.2f + (float)r.NextDouble() * 2.8f;
            d.interval = r.Next(60, 2501);
            d.drainIntervalTicks = (int)Math.Round((0.5f + r.NextDouble() * 8) * TicksPerHour);
            d.drainAmount = r.Next(8) == 0 ? r.Next(0, 5) : -r.Next(1, 11);
            d.drainCap = r.Next(8) == 0 ? 0 : -r.Next(1, 31);
            d.layers = r.Next(0, 7);
            d.standingStart = r.Next(-300, 301);
            for (int i = 0; i < 3; i++) { d.ceiling[i] = r.Next(3) == 0 ? int.MaxValue : r.Next(0, n + 1); d.decayMult[i] = 0.5f + (float)r.NextDouble() * 2.5f; }
            return d;
        }

        private static State Make(int seed)
        {
            var r = new Random(seed);
            var d = MakeDef(r);
            var s = new State { d = d, drainEnabled = r.Next(5) != 0, tick = r.Next(0, 5) * TicksPerDay };
            s.standing = RM_AttitudeKernel.StandingStartValue(d.standingStart);
            s.anchor = 0;
            Check(s.standing >= -100 && s.standing <= 100, $"StandingStartValue({d.standingStart}) = {s.standing} outside [-100,100]");
            return s;
        }

        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }

        private static void DoCheck(State s)
        {
            var d = s.d;
            s.tick += d.interval;
            float before = s.irr;
            s.irr = RM_AttitudeKernel.DecayedIrritation(s.irr, d.halfLife, d.rateSetting, s.stage < 3 ? d.decayMult[s.stage] : 1f, d.interval, TicksPerDay);
            Check(s.irr <= before, $"decay raised irritation {before} -> {s.irr}");
            Check(s.irr >= 0f, $"decay made irritation negative: {s.irr}");
            Check(s.irr == 0f || s.irr >= 0.05f, $"decay left dust {s.irr}");
            float comp = RM_AttitudeKernel.Composite(s.irr, s.standing, d.weight);
            Check(comp >= 0f && comp <= 100f, $"composite {comp} outside [0,100]");
            int prev = s.currentBand;
            int band = RM_AttitudeKernel.BandFor(comp, prev, d.thr, d.margin);
            Check(band >= 0 && band <= d.Worst, $"band {band} outside [0,{d.Worst}]");
            int raw = RM_AttitudeKernel.BandFor(comp, -1, d.thr, d.margin);
            int p = prev < 0 ? 0 : prev;
            Check(band >= raw && band <= Math.Max(raw, p), $"band {band} not between raw {raw} and max(raw, previous {p})");
            Check(raw < p || band == raw, $"escalation not immediate: raw {raw} >= previous {p} but band {band}");
            if (band < p) Check(p - 1 >= d.thr.Count || comp < d.thr[p - 1] - d.margin, $"fell {p}->{band} at composite {comp} before {d.margin} below threshold {d.thr[Math.Min(p - 1, d.thr.Count - 1)]}");
            Check(RM_AttitudeKernel.BandFor(comp, band, d.thr, d.margin) == band, $"band {band} is not a fixed point at constant composite {comp}");
            s.currentBand = band;
            ShowBand(s);
            if (band < p) Falls++;
            if (band >= d.Worst) WorstBandChecks++;
            if (band >= d.Worst && s.drainEnabled) Drain(s);
        }

        private static void ShowBand(State s)
        {
            var d = s.d;
            int ceil = s.stage < 3 ? d.ceiling[s.stage] : d.Worst;
            s.displayBand = RM_AttitudeKernel.ClampToCeiling(s.currentBand < 0 ? 0 : s.currentBand, ceil);
            Check(s.displayBand >= 0 && s.displayBand <= Math.Max(ceil, 0) && s.displayBand <= Math.Max(s.currentBand, 0), $"displayBand {s.displayBand} outside [0,min(ceiling {ceil}, band {s.currentBand})]");
            int shown = s.lineCycleDrop ? RM_AttitudeKernel.DroppedBand(s.displayBand, d.Worst) : s.displayBand;
            Check(shown <= s.displayBand && shown >= s.displayBand - 1 && shown >= 0, $"line-cycle drop moved band {s.displayBand} -> {shown}");
            Check(!(s.displayBand >= d.Worst) || shown == s.displayBand, "the worst band is silent and must not drop further");
            int layers = RM_AttitudeKernel.DesiredLayers(s.displayBand, d.Worst, d.layers, s.lineCycleDrop);
            Check(layers >= 0 && layers <= d.layers, $"layers {layers} outside [0,{d.layers}]");
            Check(s.displayBand < d.Worst || layers == 0, $"worst band must be silent, got {layers} layers");
            if (s.displayBand + 1 < d.Worst)
            {
                int up = RM_AttitudeKernel.DesiredLayers(s.displayBand + 1, d.Worst, d.layers, s.lineCycleDrop);
                Check(up >= layers, $"layers fell as the band rose {s.displayBand}->{s.displayBand + 1}: {layers}->{up}");
            }
        }

        private static void Drain(State s)
        {
            var d = s.d;
            int oldAnchor = s.anchor, oldStanding = s.standing;
            int delta = RM_AttitudeKernel.DrainDelta(s.tick, ref s.anchor, ref s.drained, ref s.lastDrain, d.drainIntervalTicks, d.drainAmount, d.drainCap, TicksPerDay);
            Check(delta <= 0, $"a drain RAISED standing by {delta}");
            if (s.anchor != oldAnchor) s.refWindowSum = 0;
            if (delta < 0)
            {
                DrainsApplied++; if (delta > d.drainAmount) DrainsClamped++;
                s.standing = RM_AttitudeKernel.StandingAfter(s.standing, delta);
                s.refWindowSum += delta;
                Check(d.drainAmount < 0 && d.drainCap < 0, $"drained {delta} with amount {d.drainAmount} cap {d.drainCap}");
                Check(delta >= d.drainCap, $"one drain of {delta} is beyond the whole day's cap {d.drainCap}");
                Check(delta >= d.drainAmount, $"drain {delta} larger than the tick amount {d.drainAmount}");
                Check(s.lastDrainTickSeen == int.MinValue || s.tick - s.lastDrainTickSeen >= d.drainIntervalTicks, $"two drains {s.tick - s.lastDrainTickSeen} ticks apart, interval is {d.drainIntervalTicks}");
                s.lastDrainTickSeen = s.tick;
            }
            Check(s.refWindowSum >= d.drainCap, $"day window drained {s.refWindowSum}, cap {d.drainCap}");
            Check(s.drained == s.refWindowSum, $"drainedToday {s.drained} != sum of this window's drains {s.refWindowSum}");
        }

        private static void Step(State s, Act a)
        {
            switch (a.kind)
            {
                case 0: // irritation event; a negative amount is a mercy
                {
                    float amt = (a.arg % 131) - 50f;
                    float old = s.irr;
                    s.irr = RM_AttitudeKernel.IrritationAfter(s.irr, amt);
                    Check(s.irr >= 0f, $"irritation went negative: {s.irr}");
                    Check(Math.Abs(s.irr - Math.Max(0f, old + amt)) < 1e-4f, "irritation not old+amount floored at 0");
                    break;
                }
                case 1: // standing event (offence / mercy), large ones included
                {
                    int delta = (a.arg % 801) - 400;
                    int expect = Math.Max(-100, Math.Min(100, s.standing + delta));
                    s.standing = RM_AttitudeKernel.StandingAfter(s.standing, delta);
                    Check(s.standing == expect, $"standing {s.standing} != clamp(old+{delta}) = {expect}");
                    break;
                }
                case 2: DoCheck(s); break;
                case 3:
                    s.stage = a.arg % 4;           // stage 3 has no entry: unrestricted, normal decay
                    ShowBand(s);
                    break;
                case 4:
                    s.lineCycleDrop = !s.lineCycleDrop;
                    ShowBand(s);
                    break;
                case 5: // AFK: many checks
                    for (int i = 0; i < 1 + a.arg % 300; i++) { DoCheck(s); Steps++; }
                    break;
                case 6: // set irritation outright (proof hook): band through the real ComputeBand
                    s.irr = (a.arg % 200) / 2f;
                    s.currentBand = RM_AttitudeKernel.BandFor(RM_AttitudeKernel.Composite(s.irr, s.standing, s.d.weight), s.currentBand, s.d.thr, s.d.margin);
                    ShowBand(s);
                    break;
            }
            Check(s.standing >= -100 && s.standing <= 100, $"standing {s.standing} left [-100,100]");
            Check(s.irr >= 0f && !float.IsNaN(s.irr) && !float.IsInfinity(s.irr), $"irritation {s.irr}");
            Check(s.currentBand >= -1 && s.currentBand <= s.d.Worst, $"band {s.currentBand}");
        }

        private static string RunSeq(int seed, List<Act> acts)
        {
            try
            {
                var s = Make(seed);
                foreach (var a in acts) { Step(s, a); Steps++; }
                return null;
            }
            catch (Exception ex) { return ex.Message; }
        }

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

        public static List<string> Sequences(int n, int baseSeed)
        {
            var fails = new List<string>();
            for (int k = 0; k < n; k++)
            {
                int seed = baseSeed + k;
                var r = new Random(seed * 7919 + 1);
                int len = r.Next(5, 120);
                var acts = new List<Act>();
                for (int i = 0; i < len; i++)
                {
                    int q = r.Next(20);
                    int kind = q < 5 ? 2 : q < 8 ? 0 : q < 11 ? 1 : q < 13 ? 3 : q < 15 ? 4 : q < 17 ? 5 : 6;
                    acts.Add(new Act { kind = kind, arg = r.Next(100000) });
                }
                Cases++;
                string err = RunSeq(seed, acts);
                if (err == null) continue;
                var min = Shrink(acts, t => RunSeq(seed, t) != null);
                fails.Add($"seq seed {seed}: {RunSeq(seed, min)} | {string.Join(" ", min)}");
                if (fails.Count >= 5) break;
            }
            return fails;
        }

        // Band function properties over random thresholds: monotone in composite for a fixed previous band; hysteresis
        // is a fixed point; and standing is monotone (lower standing never lowers the band for the same irritation).
        public static long MultiBandDrops;   // observation: a fall from band p lands below p-1 in one step (tallied)

        public static List<string> Bands(int n, int baseSeed)
        {
            var fails = new List<string>();
            for (int k = 0; k < n && fails.Count < 5; k++)
            {
                var r = new Random(baseSeed + k);
                Cases++;
                var d = MakeDef(r);
                int prev = r.Next(-1, d.Worst + 1);
                int last = -1;
                for (float c = 0; c <= 100f; c += 0.5f)
                {
                    Steps++;
                    int b = RM_AttitudeKernel.BandFor(c, prev, d.thr, d.margin);
                    if (b < last) { fails.Add($"band seed {baseSeed + k}: band fell {last}->{b} as composite rose to {c} (prev {prev}, margin {d.margin})"); break; }
                    last = b;
                    int p = prev < 0 ? 0 : prev;
                    if (b < p - 1) MultiBandDrops++;
                }
                // standing monotone: more standing (friendlier) never raises the band, same irritation and previous band
                float irr = (float)r.NextDouble() * 100f;
                int lastB = int.MaxValue;
                for (int st = -100; st <= 100; st += 5)
                {
                    Steps++;
                    int b = RM_AttitudeKernel.BandFor(RM_AttitudeKernel.Composite(irr, st, d.weight), prev, d.thr, d.margin);
                    if (b > lastB) { fails.Add($"band seed {baseSeed + k}: band ROSE {lastB}->{b} as standing rose to {st} (irritation {irr})"); break; }
                    lastB = b;
                }
            }
            return fails;
        }

        // Decay is an exponential law: two steps equal one step of double length (away from the dust floor), and never
        // raises irritation; a larger stage multiplier never decays slower.
        public static List<string> Decay(int n, int baseSeed)
        {
            var fails = new List<string>();
            for (int k = 0; k < n && fails.Count < 5; k++)
            {
                var r = new Random(baseSeed + k);
                Cases++; Steps++;
                float x = 60f + (float)r.NextDouble() * 40f, hl = 0.05f + (float)r.NextDouble() * 5f, rate = 0.2f + (float)r.NextDouble() * 3f, st = 0.5f + (float)r.NextDouble() * 2.5f;
                int i1 = r.Next(60, 2501);
                float a = RM_AttitudeKernel.DecayedIrritation(RM_AttitudeKernel.DecayedIrritation(x, hl, rate, st, i1, TicksPerDay), hl, rate, st, i1, TicksPerDay);
                float b = RM_AttitudeKernel.DecayedIrritation(x, hl, rate, st, 2 * i1, TicksPerDay);
                if (Math.Abs(a - b) > x * 1e-4f) fails.Add($"decay seed {baseSeed + k}: two steps {a} vs one double step {b} (x {x})");
                float slow = RM_AttitudeKernel.DecayedIrritation(x, hl, rate, st, i1, TicksPerDay);
                float fast = RM_AttitudeKernel.DecayedIrritation(x, hl, rate, st * 1.5f, i1, TicksPerDay);
                if (fast > slow + 1e-4f) fails.Add($"decay seed {baseSeed + k}: a bigger decay multiplier decayed slower ({fast} > {slow})");
                float half = RM_AttitudeKernel.DecayedIrritation(x, hl, 1f, 1f, hl * TicksPerDay, TicksPerDay);
                if (hl >= 0.01f && Math.Abs(half - x / 2) > x * 1e-3f) fails.Add($"decay seed {baseSeed + k}: one half-life of ticks left {half}, expected {x / 2}");
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
                ("seq", () => Sequences(N(10000), S(1))),
                ("band", () => Bands(N(20000), S(1))),
                ("decay", () => Decay(N(50000), S(1))),
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
            Console.WriteLine($"coverage: {WorstBandChecks} checks at the worst band, {DrainsApplied} drains applied ({DrainsClamped} cut short by the day cap), {Falls} band falls");
            Console.WriteLine($"observation: de-escalations that skip a band (fall below p-1 in one step, by design): {MultiBandDrops}");
            Console.WriteLine($"edge: StandingAfter(100, int.MaxValue) = {RM_AttitudeKernel.StandingAfter(100, int.MaxValue)} (int overflow wraps; callers pass small deltas)");
            Console.WriteLine($"attitude fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
