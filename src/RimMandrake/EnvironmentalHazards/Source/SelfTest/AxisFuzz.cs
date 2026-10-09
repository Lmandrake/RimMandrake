// Approach B for the fresh->brine salinity axis: seeded random ACTION SEQUENCES over RM_AxisKernel, the Verse-free
// arithmetic RM_MapComponent_GradientAxis and RM_GameCondition_GradientSurge call. The model (a small grid, the
// shift-in-progress fields, the order TickShift/ShiftAxis/ExposeData do things) is this file's own; every number comes
// from the production kernel. Failures are shrunk by delta debugging and printed as `family seed N: message | actions`.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace RimMandrake.EnvironmentalHazards.SelfTest
{
    internal static class AxisFuzz
    {
        public static long Cases, Steps, ShiftsDone, RecedesDone, Overwrites, OverwrittenRecedes, ClampLossCells, CleanCycles, SaveLoads;
        public static double LostDeltaAbs;
        const int Interval = 250;

        internal struct Act
        {
            public int kind, a, b, c;
            public float f;
            public override string ToString()
            {
                switch (kind)
                {
                    case 0: return $"Surge(front={a},map={b},dur={c},resid={f:F2})";
                    case 1: return $"Update({a})";
                    case 2: return $"EndSurge(recedeTicks={a})";
                    case 3: return $"Force(delta={f:F3},dur={a},recede={b})";
                    case 4: return "SaveLoad";
                    default: return $"Set(cell={a},{f:F2})";
                }
            }
        }

        private sealed class Shift { public float D; public int T, Steps, Expected; public bool Recede, Clean = true; public double Applied; }

        private sealed class M
        {
            public float[] sal; public bool[] hit;
            public bool inProgress, isRecede; public float deltaRem; public int ticksRem, lastRecede = -1, now;
            public Shift cur;
            public float totalDelta, resid; public bool surgeOpen;
            public List<float> cycleStart; public Shift surgeFwd, surgeRec; public bool cycleOk; public float net;
        }

        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }

        private static void Begin(M m, float delta, int dur, bool recede)
        {
            if (m.inProgress)
            {
                Overwrites++; LostDeltaAbs += Math.Abs(m.deltaRem);
                if (m.isRecede) OverwrittenRecedes++;
                m.cur.Clean = false;
            }
            m.inProgress = true; m.deltaRem = delta; m.ticksRem = RM_AxisKernel.ClampDuration(dur); m.isRecede = recede;
            m.cur = new Shift { D = delta, T = m.ticksRem, Recede = recede, Expected = (m.ticksRem + Interval - 1) / Interval };
        }

        private static void Update(M m)
        {
            m.now += Interval;
            if (!m.inProgress) return;
            Steps++;
            int before = m.ticksRem; float remBefore = m.deltaRem;
            int step = RM_AxisKernel.StepTicks(Interval, m.ticksRem);
            float d = RM_AxisKernel.StepDelta(m.deltaRem, step, m.ticksRem);
            Check(step >= 1 && step <= Interval && step <= before, $"step {step} outside [1,min({Interval},{before})]");
            Check(!float.IsNaN(d) && !float.IsInfinity(d), "step delta not finite");
            Check(d * m.cur.D >= 0f, $"step delta {d} has the opposite sign of the shift {m.cur.D}");
            Check(Math.Abs(d) <= Math.Abs(remBefore) * (1 + 1e-6f) + 1e-9f, $"step delta {d} exceeds what remained {remBefore}");
            // The remaining-slice rule is a constant rate only against the REMAINING budget, which telescopes: each
            // slice equals the original D * step / T up to accumulated float error.
            if (m.cur.Clean)
                Check(Math.Abs(d - m.cur.D * step / m.cur.T) <= 3e-5 * Math.Abs(m.cur.D) + 1e-8, $"slice {d} is not the constant-rate share {m.cur.D * step / (double)m.cur.T} of {m.cur.D} over {m.cur.T}");
            for (int i = 0; i < m.sal.Length; i++)
            {
                float old = m.sal[i];
                float ns = RM_AxisKernel.Apply(old, d);
                Check(ns >= 0f && ns <= 1f, $"cell {i} salinity {ns} left [0,1]");
                if (d >= 0f) Check(ns >= old, $"cell {i} fell {old}->{ns} under a rising slice {d}");
                else Check(ns <= old, $"cell {i} rose {old}->{ns} under a falling slice {d}");
                if (ns != old + d) m.hit[i] = true;
                m.sal[i] = ns;
            }
            m.deltaRem -= d; m.ticksRem -= step;
            m.cur.Applied += d; m.cur.Steps++;
            Check(m.ticksRem == before - step && m.ticksRem >= 0, "ticks remaining did not drop by exactly the step");
            if (RM_AxisKernel.ShiftFinished(m.ticksRem))
            {
                m.inProgress = false; m.deltaRem = 0f;
                if (m.isRecede) { m.lastRecede = m.now; RecedesDone++; }
                ShiftsDone++;
                if (m.cur.Clean)
                {
                    Check(m.cur.Steps == m.cur.Expected, $"shift of {m.cur.T} ticks took {m.cur.Steps} updates, expected {m.cur.Expected}");
                    Check(Math.Abs(m.cur.Applied - m.cur.D) <= 1e-4 * Math.Abs(m.cur.D) + 1e-6, $"shift applied {m.cur.Applied} of {m.cur.D}");
                }
            }
        }

        private static void Apply(M m, Act a)
        {
            switch (a.kind)
            {
                case 0:
                {
                    // a surge starts: forward shove sized from the map; a still-open surge is replaced.
                    m.totalDelta = RM_AxisKernel.TotalDelta(a.a, a.b, a.b);
                    Check(m.totalDelta >= 0f && !float.IsNaN(m.totalDelta), $"total delta {m.totalDelta}");
                    Check(m.totalDelta <= (a.b > 0 ? a.a / (double)a.b + 1e-6 : 0.0), $"total delta {m.totalDelta} exceeds front/mapsize");
                    m.resid = a.f; m.surgeOpen = true;
                    m.cycleStart = new List<float>(m.sal);
                    for (int i = 0; i < m.hit.Length; i++) m.hit[i] = false;
                    m.cycleOk = true; m.surgeRec = null;
                    Begin(m, m.totalDelta, a.c, false);
                    m.surgeFwd = m.cur;
                    break;
                }
                case 1: for (int i = 0; i < a.a; i++) Update(m); break;
                case 2:
                {
                    if (!m.surgeOpen || m.totalDelta == 0f) break;
                    float rec = RM_AxisKernel.RecedeDelta(m.totalDelta, m.resid);
                    Check(rec <= 0f && rec >= -m.totalDelta - 1e-6f, $"recede {rec} outside [-{m.totalDelta},0] for residual {m.resid}");
                    Check(Math.Abs((m.totalDelta + rec) - m.totalDelta * m.resid) <= 1e-5, $"net drift {m.totalDelta + rec} != total*residual {m.totalDelta * m.resid}");
                    bool fwdClean = m.cycleOk && m.surgeFwd == m.cur && !m.inProgress && m.cur.Clean && m.cur.Steps == m.cur.Expected;
                    m.surgeOpen = false;
                    Begin(m, rec, a.a, true);
                    m.surgeRec = fwdClean ? m.cur : null;
                    m.net = m.totalDelta * m.resid;
                    break;
                }
                case 3: Begin(m, a.f, a.a, a.b != 0); m.cycleOk = false; m.surgeRec = null; break;
                case 4:
                    SaveLoads++;
                    for (int i = 0; i < m.sal.Length; i++)
                    {
                        float v = m.sal[i];
                        float back = RM_AxisKernel.Clamp01(RM_AxisKernel.Dequantize(RM_AxisKernel.Quantize(v)));
                        Check(back >= 0f && back <= 1f, $"reload of {v} gave {back}");
                        Check(Math.Abs(back - v) <= 0.5f / RM_AxisKernel.ShortScale + 1e-6f, $"reload of {v} gave {back}, error beyond half a quantum");
                        m.sal[i] = back;
                    }
                    break;
                default:
                    if (a.a < m.sal.Length) { m.sal[a.a] = RM_AxisKernel.Clamp01(a.f); m.cycleOk = false; m.surgeRec = null; }
                    break;
            }
        }

        private static string RunSeq(int seed, List<Act> acts, bool tally)
        {
            var r = new Random(seed);
            var m = new M();
            int g = 1 + r.Next(12);
            m.sal = new float[g]; m.hit = new bool[g];
            for (int i = 0; i < g; i++) { m.sal[i] = r.Next(5) == 0 ? (r.Next(2) == 0 ? 0f : 1f) : (float)r.NextDouble(); }
            try
            {
                foreach (var a in acts)
                {
                    Apply(m, a);
                    // lastRecede only ever moves forward and only when a recede finished
                    Check(m.lastRecede <= m.now, "lastRecedeCompletedTick in the future");
                    // a finished clean surge cycle: unclamped cells land exactly on start + total*residual
                    if (m.surgeRec != null && m.cur == m.surgeRec && !m.inProgress && m.cur.Clean && m.cur.Steps == m.cur.Expected && m.cycleOk)
                    {
                        for (int i = 0; i < m.sal.Length; i++)
                        {
                            if (!m.hit[i]) Check(Math.Abs(m.sal[i] - (m.cycleStart[i] + m.net)) <= 1e-3, $"cell {i} {m.cycleStart[i]} -> {m.sal[i]} after a clean surge cycle, expected {m.cycleStart[i] + m.net}");
                            else ClampLossCells++;
                        }
                        CleanCycles++;
                        m.surgeRec = null;
                    }
                }
            }
            catch (Exception e) { return e.Message; }
            return null;
        }

        private static List<Act> Gen(Random r, int len)
        {
            int[] maps = { 50, 100, 150, 200, 250, 300, 400 };
            int[] durs = { 1, 2, 249, 250, 251, 500, 2500, 15000, 60000, 120000, 300000, 480000 };
            var l = new List<Act>();
            for (int i = 0; i < len; i++)
            {
                int k = r.Next(100);
                if (k < 14) l.Add(new Act { kind = 0, a = r.Next(0, 121), b = maps[r.Next(maps.Length)], c = durs[r.Next(durs.Length)], f = (float)r.NextDouble() });
                else if (k < 60) l.Add(new Act { kind = 1, a = 1 + r.Next(r.Next(3) == 0 ? 400 : 40) });
                else if (k < 78) l.Add(new Act { kind = 2, a = durs[r.Next(durs.Length)] });
                else if (k < 86) l.Add(new Act { kind = 3, f = (float)(r.NextDouble() * 1.2 - 0.6) * (r.Next(6) == 0 ? 0f : 1f), a = durs[r.Next(durs.Length)], b = r.Next(2) });
                else if (k < 94) l.Add(new Act { kind = 4 });
                else l.Add(new Act { kind = 5, a = r.Next(12), f = (float)r.NextDouble() });
            }
            return l;
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
            for (int k = 0; k < n && fails.Count < 5; k++)
            {
                int seed = baseSeed + k;
                var r = new Random(seed);
                var acts = Gen(r, 6 + r.Next(60));
                Cases++;
                if (RunSeq(seed, acts, true) == null) continue;
                var min = Shrink(acts, t => RunSeq(seed, t, false) != null);
                fails.Add($"axis seed {seed}: {RunSeq(seed, min, false)} | {string.Join(" ", min)}");
            }
            return fails;
        }

        // Every stored ushort survives a load -> save round trip unchanged, and every unit float quantizes in range.
        public static List<string> Quant(int n, int baseSeed)
        {
            var fails = new List<string>();
            // AXIS_SURGE_CLAMP_DRIFT_1: a saturated cell recedes only what it really gained
            {
                Cases++;
                float start = 0.95f, total = 0.10f, resid = 0.2f;
                float afterFwd = RM_AxisKernel.Apply(start, total);
                float applied = afterFwd - start;
                float rec = RM_AxisKernel.RecedeDelta(total, resid) * RM_AxisKernel.AppliedFraction(applied, total);
                float end = RM_AxisKernel.Apply(afterFwd, rec);
                float want = start + applied * resid;
                if (Math.Abs(end - want) > 1e-5f) fails.Add($"clamp drift: saturated cell {start} -> {afterFwd} -> {end}, expected {want}");
                if (end < start - 1e-6f) fails.Add($"clamp drift: saturated cell receded below its start ({end} < {start})");
            }
            for (int q = 0; q <= ushort.MaxValue; q++)
            {
                Cases++;
                float s = RM_AxisKernel.Clamp01(RM_AxisKernel.Dequantize((ushort)q));
                if (s < 0f || s > 1f) { fails.Add($"quant: stored {q} loads as {s}"); break; }
                if (RM_AxisKernel.Quantize(s) != q) { fails.Add($"quant: stored {q} -> {s} saved as {RM_AxisKernel.Quantize(s)} (not idempotent)"); if (fails.Count >= 5) break; }
            }
            for (int k = 0; k < n && fails.Count < 5; k++)
            {
                Cases++;
                var r = new Random(baseSeed + k);
                float v = (float)r.NextDouble();
                if (r.Next(10) == 0) v = r.Next(2);
                ushort u = RM_AxisKernel.Quantize(v);
                if (Math.Abs(RM_AxisKernel.Dequantize(u) - v) > 0.5f / RM_AxisKernel.ShortScale + 1e-6f) fails.Add($"quant: {v} -> {u} -> {RM_AxisKernel.Dequantize(u)} beyond half a quantum");
                // monotone: quantization never reorders two salinities
                float w = Math.Min(1f, v + (float)r.NextDouble() * 0.01f);
                if (RM_AxisKernel.Quantize(w) < RM_AxisKernel.Quantize(v)) fails.Add($"quant: {v}<={w} but {RM_AxisKernel.Quantize(v)}>{RM_AxisKernel.Quantize(w)}");
                // band predicates: the two spellings of "near the salt line" agree except within float rounding of the edge
                float band = 0.01f + (float)r.NextDouble() * 0.09f;
                if (RM_AxisKernel.InSaltLine(w, band) != RM_AxisKernel.InFleckBand(w, band) && Math.Abs(Math.Abs(w - 0.5f) - band) > 1e-5f)
                    fails.Add($"band: {w} band {band}: SaltLine {RM_AxisKernel.InSaltLine(w, band)} vs Fleck {RM_AxisKernel.InFleckBand(w, band)}");
            }
            return fails;
        }

        public static void Report(Func<int, int> N, Func<int, int> S, string only, ref bool ok)
        {
            var fam = new (string name, Func<List<string>> run)[]
            {
                ("axis", () => Sequences(N(4000), S(1))),
                ("quant", () => Quant(N(200000), S(1))),
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
            Console.WriteLine($"axis coverage: shifts done {ShiftsDone}, recedes done {RecedesDone}, clean surge cycles checked {CleanCycles}, save/loads {SaveLoads}, cells that clamped mid-cycle {ClampLossCells}");
            Console.WriteLine($"axis observation (design, not failure): a shift started while another ran dropped its remainder {Overwrites}x (recedes cut short {OverwrittenRecedes}x, total |delta| lost {LostDeltaAbs:F2})");
        }

        public static bool Run(double scale, int? oneSeed, string only)
        {
            bool ok = true;
            Report(n => oneSeed.HasValue ? 1 : (int)(n * scale), s => oneSeed ?? s, only, ref ok);
            return ok;
        }
    }
}
