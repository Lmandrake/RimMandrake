// Approach B for the Flame Statues: seeded fuzz over the Verse-free kernel the mod calls (../Kernel/RM_FlameKernel.cs):
//   quality  the quality-to-size table (monotone, positive, off switches give 1, unknown quality gives 1)
//   gate     burning / shown / lit predicates exhaustively against a truth table, plus the implication chain lit => shown => burning
//   fleck    the fleck cadence: every point fires exactly once per interval, interval floor, quality shortens it, 0 means none
//   frame    the per-point frame and jitter picks stay inside their arrays for ANY tick / id / point, including adversarial
//            inputs solved so the XOR lands on int.MinValue (Mathf.Abs of that is negative, the original indexing crashed on it)
//   fuel     the fuel-use multiplier clamp and scaling, and the "statues never run out" refill over a burn lifecycle
// A failing case is printed as `family seed N: message | detail`; --fuzz-seed N replays it.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace RimMandrake.FlameStatues.SelfTest
{
    internal static class FlameStatuesFuzz
    {
        public static long Cases, Steps;
        public static long Refilled, Dark, Lit, AdversarialFrames, FleckFires, PipeRefunds;
        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }

        private static List<string> Loop(string name, int n, int seed, Action<int> one)
        {
            var fails = new List<string>();
            for (int i = 0; i < n; i++)
            {
                Cases++;
                try { one(seed + i); } catch (Exception e) { fails.Add($"{name} seed {seed + i}: {e.Message}"); if (fails.Count >= 3) break; }
            }
            return fails;
        }

        // ════════════════════════ quality ════════════════════════
        private static List<string> Quality(int n, int seed)
        {
            return Loop("quality", 1, 1, _ =>
            {
                float prev = 0f;
                for (int q = 0; q < 7; q++)
                {
                    Steps++;
                    float s = RM_FlameKernel.QualityScale(true, true, q);
                    Check(s > 0f, "scale for quality " + q + " is not positive");
                    Check(s >= prev, "scale not monotone at quality " + q);
                    prev = s;
                    Check(RM_FlameKernel.QualityScale(false, true, q) == 1f, "comp scaling off still scaled quality " + q);
                    Check(RM_FlameKernel.QualityScale(true, false, q) == 1f, "setting off still scaled quality " + q);
                }
                Check(RM_FlameKernel.QualityScale(true, true, 2) == 1f, "Normal quality is not size 1");
                Check(RM_FlameKernel.QualityScale(true, true, 0) == 0.5f, "Awful is not half size");
                Check(RM_FlameKernel.QualityScale(true, true, 6) == 2f, "Legendary is not double size");
                Check(RM_FlameKernel.QualityScale(true, true, -1) == 1f, "no CompQuality is not size 1");
                Check(RM_FlameKernel.QualityScale(true, true, 7) == 1f, "an unknown quality ordinal is not size 1");
                Check(RM_FlameKernel.QualityScale(true, true, int.MaxValue) == 1f, "a huge quality ordinal is not size 1");
                Check(RM_FlameKernel.QualityScales.Length == 7, "the quality table does not cover all seven categories");
            });
        }

        // ════════════════════════ gate ════════════════════════
        private static List<string> Gate(int n, int seed)
        {
            return Loop("gate", 1, 1, _ =>
            {
                for (int m = 0; m < 32; m++)
                {
                    Steps++;
                    bool hasRef = (m & 1) != 0, hasFuel = (m & 2) != 0, consume = (m & 4) != 0, points = (m & 8) != 0, glow = (m & 16) != 0;
                    bool burning = RM_FlameKernel.Burning(hasRef, hasFuel, consume);
                    // spec: dark only when it consumes fuel, has a tank and the tank is empty
                    bool wantBurning = !(consume && hasRef && !hasFuel);
                    Check(burning == wantBurning, $"burning({hasRef},{hasFuel},{consume}) = {burning}, want {wantBurning}");
                    bool shown = RM_FlameKernel.FlamesShown(burning, points);
                    Check(shown == (wantBurning && points), "flames shown mismatch");
                    bool lit = RM_FlameKernel.LitNow(burning, points, glow);
                    Check(lit == (wantBurning && points && glow), "lit mismatch");
                    if (lit) { Check(shown, "lit without flames shown"); Lit++; }
                    if (shown) Check(burning, "flames shown while not burning");
                    if (!burning) Dark++;
                }
            });
        }

        // ════════════════════════ fleck ════════════════════════
        private static List<string> Fleck(int n, int seed)
        {
            return Loop("fleck", n, seed, s =>
            {
                var r = new Random(s);
                int[] bases = { 0, 1, 5, 30, 60, 90, 90, 90, 180, 600 };
                int baseInterval = bases[r.Next(bases.Length)];
                int qi = r.Next(8);
                float q = RM_FlameKernel.QualityScale(true, true, qi == 7 ? -1 : qi);
                int interval = RM_FlameKernel.FleckInterval(baseInterval, q);
                if (baseInterval <= 0) { Check(interval == 0, "a zero base interval did not mean no flecks"); for (int t = 0; t < 50; t++) Check(!RM_FlameKernel.FleckDue(t, 7, 0, interval), "fleck with interval 0"); return; }
                Check(interval >= RM_FlameKernel.MinFleckInterval, $"interval {interval} under the floor");
                float better = RM_FlameKernel.FleckInterval(baseInterval, q * 1.25f);
                Check(better <= interval, "a better statue throws flecks LESS often");
                Check(Math.Abs(interval - Math.Max(RM_FlameKernel.MinFleckInterval, baseInterval / q)) <= 0.5001 || interval == RM_FlameKernel.MinFleckInterval, $"interval {interval} is not the rounded base/q");
                int id = r.Next(0, 100000), t0 = r.Next(0, 5000000), points = r.Next(1, 7);
                for (int p = 0; p < points; p++)
                {
                    int fires = 0, last = -1;
                    for (int t = t0; t < t0 + interval * 3; t++)
                    {
                        Steps++;
                        if (RM_FlameKernel.FleckDue(t, id, p, interval))
                        {
                            fires++; FleckFires++;
                            if (last >= 0) Check(t - last == interval, $"point {p} fired {t - last} ticks after its last (want {interval})");
                            last = t;
                        }
                    }
                    Check(fires == 3, $"point {p} fired {fires} times in three intervals (interval {interval})");
                }
                // points are out of phase: unless the interval divides the phase step, point 0 and point 1 never puff on the same tick
                if (points >= 2 && RM_FlameKernel.PointPhase % interval != 0)
                    for (int t = t0; t < t0 + interval; t++)
                        Check(!(RM_FlameKernel.FleckDue(t, id, 0, interval) && RM_FlameKernel.FleckDue(t, id, 1, interval)), $"points 0 and 1 puff together at tick {t} (interval {interval})");
                Check(!RM_FlameKernel.FleckDue(t0, id, 0, 0), "FleckDue with interval 0");
            });
        }

        // ════════════════════════ frame ════════════════════════
        private static List<string> Frame(int n, int seed)
        {
            return Loop("frame", n, seed, s =>
            {
                var r = new Random(s);
                for (int k = 0; k < 40; k++)
                {
                    Steps++;
                    int frames = r.Next(1, 17), pattern = r.Next(1, 20000), p = r.Next(0, 8);
                    int id = k % 5 == 0 ? r.Next(int.MinValue, int.MaxValue) : r.Next(0, 1000000);
                    int ticks = RM_FlameKernel.AnimTicks(k % 7 == 0 ? r.Next(0, int.MaxValue / 2) : r.Next(0, 5000000), id);
                    int fi = RM_FlameKernel.FrameIndex(ticks, id, p, frames);
                    Check(fi >= 0 && fi < frames, $"frame {fi} outside 0..{frames - 1} (ticks {ticks} id {id} point {p})");
                    int ji = RM_FlameKernel.JitterIndex(ticks, p, pattern);
                    Check(ji >= 0 && ji < pattern, $"jitter {ji} outside 0..{pattern - 1} (ticks {ticks} point {p})");
                    Check(fi == RM_FlameKernel.FrameIndex(ticks, id, p, frames), "frame pick is not deterministic");
                    // adversarial: choose the tick so step ^ (id*391 + p*131) == int.MinValue exactly
                    int target = id * 391 + p * 131;
                    int step = int.MinValue ^ target;
                    int adv = (step - p * 7) * 15;                       // animTicks/15 + p*7 == step (when the product does not overflow)
                    if ((long)(step - p * 7) * 15 == adv)
                    {
                        AdversarialFrames++;
                        int af = RM_FlameKernel.FrameIndex(adv, id, p, frames);
                        Check(af >= 0 && af < frames, $"adversarial frame {af} outside 0..{frames - 1} (animTicks {adv} id {id} point {p})");
                    }
                    // adversarial jitter: step + p*3 == int.MinValue
                    int jstep = int.MinValue - p * 3;
                    int jt = (jstep - p * 7) * 15;
                    if ((long)(jstep - p * 7) * 15 == jt)
                    {
                        int aj = RM_FlameKernel.JitterIndex(jt, p, pattern);
                        Check(aj >= 0 && aj < pattern, $"adversarial jitter {aj} outside 0..{pattern - 1} (animTicks {jt} point {p})");
                    }
                }
                // the points of one statue do not flicker in step
                int same = 0, total = 0;
                for (int t = 0; t < 6000; t += 15) { total++; if (RM_FlameKernel.FrameIndex(RM_FlameKernel.AnimTicks(t, r.Next(0, 100000)), 77, 0, 8) == RM_FlameKernel.FrameIndex(RM_FlameKernel.AnimTicks(t, 77), 77, 1, 8)) same++; }
                int sameFixed = 0;
                int idf = r.Next(0, 100000);
                for (int t = 0; t < 6000; t += 15) { int a = RM_FlameKernel.AnimTicks(t, idf); if (RM_FlameKernel.FrameIndex(a, idf, 0, 8) == RM_FlameKernel.FrameIndex(a, idf, 1, 8)) sameFixed++; }
                Check(sameFixed * 3 < total, $"points 0 and 1 draw the same fire frame on {sameFixed} of {total} ticks (flicker in step)");
                // every frame is reachable by some tick (the flame does animate)
                int id2 = r.Next(0, 100000);
                var seen = new HashSet<int>();
                for (int t = 0; t < 4000; t += 15) seen.Add(RM_FlameKernel.FrameIndex(RM_FlameKernel.AnimTicks(t, id2), id2, 0, 8));
                Check(seen.Count >= 4, "the flame uses only " + seen.Count + " of 8 frames over 4000 ticks");
                Check(RM_FlameKernel.AnimTicks(1000, int.MinValue) >= 1000, "AnimTicks went backwards for a negative id");
            });
        }

        // ════════════════════════ fuel ════════════════════════
        private static List<string> Fuel(int n, int seed)
        {
            return Loop("fuel", n, seed, s =>
            {
                var r = new Random(s);
                float[] ms = { -1f, 0f, 0.1f, 0.25f, 0.5f, 1f, 1f, 2f, 4f, 9f, float.MaxValue };
                float m = r.Next(2) == 0 ? ms[r.Next(ms.Length)] : (float)(r.NextDouble() * 6 - 1);
                float c = RM_FlameKernel.ClampFuelMultiplier(m);
                Check(c >= 0.25f && c <= 4f, $"clamp({m}) = {c}");
                Check(RM_FlameKernel.ClampFuelMultiplier(c) == c, "clamp not idempotent");
                float rate = (float)(r.NextDouble() * 0.6 + 0.01);
                float scaled = RM_FlameKernel.ScaledFuelRate(rate, m);
                Check(scaled > 0f, "scaled rate not positive");
                if (Math.Abs(c - 1f) < 1e-6f) Check(scaled == rate, "multiplier 1 changed the rate");
                else Check(Math.Abs(scaled - rate * c) < 1e-6f, "scaled rate is not rate * clamped multiplier");
                Check(RM_FlameKernel.ScaledFuelRate(rate, 1f) == rate, "multiplier exactly 1 changed the rate");
                // lifecycle: a statue burning for a while with the setting flipped at random
                float capacity = new[] { 5f, 10f, 20f }[r.Next(3)];
                float fuel = r.Next(2) == 0 ? 0f : capacity * (float)r.NextDouble();
                float perTick = rate / 60000f * 5000f;                  // a coarse tick: 5000 ticks per step keeps the fuel moving
                bool consume = r.Next(2) == 0;
                for (int step = 0; step < 80; step++)
                {
                    Steps++;
                    if (r.Next(10) == 0) consume = !consume;
                    bool poll = r.Next(2) == 0;
                    if (consume) fuel = Math.Max(0f, fuel - perTick);          // the vanilla comp burns; ours never adds
                    float add = RM_FlameKernel.RefillAmount(consume, true, poll, fuel, capacity);
                    Check(add >= 0f, "negative refill");
                    if (consume) Check(add == 0f, "refilled while the statue is meant to consume fuel");
                    if (!poll) Check(add == 0f, "refilled off the poll tick");
                    fuel += add;
                    Check(fuel <= capacity + 1e-4f, $"fuel {fuel} above capacity {capacity}");
                    if (add > 0f) { Refilled++; Check(Math.Abs(fuel - capacity) < 1e-4f, "refill did not top the tank to capacity"); }
                    Check(RM_FlameKernel.Burning(true, fuel > 0f, consume) == (!consume || fuel > 0f), "burning disagrees with the tank");
                }
                Check(RM_FlameKernel.RefillAmount(false, false, true, 0f, 10f) == 0f, "refilled a statue with no refuelable comp");
            });
        }

        // ════════════════════════ pipe (Helixien link) ════════════════════════
        private static List<string> Pipe(int n, int seed)
        {
            return Loop("pipe", n, seed, s =>
            {
                var r = new Random(s);
                float capacity = new[] { 5f, 10f, 20f }[r.Next(3)];
                float fuel = capacity * (float)(0.2 + 0.8 * r.NextDouble());
                float perStep = capacity * (float)(r.NextDouble() * 0.05 + 0.001);
                bool link = r.Next(4) != 0, piped = r.Next(2) == 0;
                float last = -1f, startFuel = fuel;
                for (int step = 0; step < 120; step++)
                {
                    Steps++;
                    if (r.Next(15) == 0) { piped = !piped; }
                    fuel = Math.Max(0f, fuel - perStep);                      // the vanilla comp burns every tick
                    if (r.Next(40) == 0) fuel = capacity;                     // a hauler refills
                    bool poll = r.Next(3) != 0;
                    float back = RM_FlameKernel.PipeRefund(link, piped, true, poll, fuel, last);
                    Check(back >= 0f, "negative pipe refund");
                    if (!link || !piped || !poll || last < 0f) Check(back == 0f, "refunded while unlinked / unpiped / off-poll / unread");
                    if (back > 0f) { PipeRefunds++; Check(fuel + back <= capacity + 1e-4f, "refund overfilled the tank"); }
                    fuel += back;
                    if (poll) last = fuel;
                    Check(RM_FlameKernel.PipeRefund(link, piped, false, true, 0f, capacity) == 0f, "refunded with fuel use switched off");
                }
                Check(RM_FlameKernel.PipeRefund(true, true, true, true, 3f, 5f) == 2f, "refund is not the burn since the last poll");
                Check(RM_FlameKernel.PipeRefund(true, true, true, true, 5f, 3f) == 0f, "refunded a rise (a hauler's refill)");
                Check(RM_FlameKernel.PipeRefund(true, true, true, true, 3f, -1f) == 0f, "refunded with no previous reading");
                // continuously piped, every tick a poll: the tank never falls more than one step below its start
                float f2 = startFuel, l2 = -1f;
                for (int step = 0; step < 200; step++)
                {
                    f2 = Math.Max(0f, f2 - perStep);
                    f2 += RM_FlameKernel.PipeRefund(true, true, true, true, f2, l2);
                    l2 = f2;
                    Check(f2 >= startFuel - perStep - 1e-4f, $"piped tank drained to {f2} from {startFuel}");
                }
            });
        }

        public static bool Run(double scale, int? oneSeed, string only)
        {
            var sw = Stopwatch.StartNew();
            bool ok = true;
            int N(int n) { return oneSeed.HasValue ? 1 : (int)(n * scale); }
            int S(int baseSeed) { return oneSeed ?? baseSeed; }
            var fam = new (string name, Func<List<string>> run)[]
            {
                ("quality", () => Quality(1, 1)),
                ("gate", () => Gate(1, 1)),
                ("fleck", () => Fleck(N(2000), S(1))),
                ("frame", () => Frame(N(4000), S(1))),
                ("fuel", () => Fuel(N(3000), S(1))),
                ("pipe", () => Pipe(N(2000), S(1))),
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
            if (only == null && !oneSeed.HasValue && scale >= 1)
            {
                Console.WriteLine($"reached: lit {Lit}, dark {Dark}, refills {Refilled}, flecks {FleckFires}, adversarial frames {AdversarialFrames}, pipe refunds {PipeRefunds}");
                if (Lit == 0 || Dark == 0 || Refilled == 0 || FleckFires == 0 || AdversarialFrames == 0 || PipeRefunds == 0) { Console.WriteLine("FAIL fuzz never reached lit / dark / refill / fleck / adversarial frame / pipe refund (blind)"); ok = false; }
            }
            Console.WriteLine($"flamestatues fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
