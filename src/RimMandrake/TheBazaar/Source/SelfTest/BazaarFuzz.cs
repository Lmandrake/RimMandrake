// Approach B for the Bazaar price engine: seeded random ACTION SEQUENCES over RM_BazaarKernel, the Verse-free
// arithmetic RM_BazaarEconomy/RM_BazaarBucket call. Every number comes from the production kernel; the model
// (which bucket an action touches, the reference history queue) is this file's own. A failing sequence is shrunk by
// delta debugging and printed as `family seed N: message | actions`, so it replays exactly.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace RimMandrake.Bazaar.SelfTest
{
    internal static class BazaarFuzz
    {
        public static long Cases, Steps;

        internal struct Act
        {
            public int kind, bucket, arg;
            public override string ToString()
            {
                string[] names = { "Drift", "Nudge", "Record", "Reload", "ReloadLong", "Reseed" };
                return names[kind] + "(b" + bucket + "," + arg + ")";
            }
        }

        private sealed class Bucket
        {
            public float mult, target, nudge;
            public List<float> ring = new List<float>();
            public int head;
            public List<float> reference = new List<float>();   // last HistorySize pushes, oldest first
        }

        private sealed class World { public Bucket[] b; public int day; }

        // arg -> float helpers, pure functions of the action so a shrunk list replays identically
        private static float Unit(int arg) { return ((arg * 2654435761u) >> 8) / 16777216f; }
        private static float NoiseU(int arg)
        {
            switch (arg % 7) { case 0: return 0f; case 1: return 1f; case 2: return 0.5f; default: return Unit(arg); }
        }
        private static float Fraction(int arg)
        {
            switch (arg % 6)
            {
                case 0: return -5f; case 1: return 5f; case 2: return 0f;
                default: return (Unit(arg) * 2f - 1f) * 1.5f;
            }
        }
        private static float Level(int arg)
        {
            switch (arg % 6) { case 0: return -3f; case 1: return 0f; case 2: return 100f; case 3: return 0.25f; case 4: return 4f; default: return 0.05f + Unit(arg) * 6f; }
        }

        private static World Make(int seed)
        {
            var r = new Random(seed);
            var w = new World { b = new Bucket[r.Next(1, 6)] };
            for (int i = 0; i < w.b.Length; i++)
            {
                float t = RM_BazaarKernel.SeedLevel(Level(r.Next(1000)));
                w.b[i] = new Bucket { mult = t, target = t };
                Push(w.b[i], t);
            }
            return w;
        }

        private static void Push(Bucket b, float v)
        {
            RM_BazaarKernel.RingPush(b.ring, ref b.head, v);
            b.reference.Add(v);
            if (b.reference.Count > RM_BazaarKernel.HistorySize) b.reference.RemoveAt(0);
        }

        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }

        private static string Digest(World w)
        {
            var sb = new System.Text.StringBuilder();
            foreach (var b in w.b)
                sb.Append(b.mult.ToString("R")).Append('/').Append(b.nudge.ToString("R")).Append('/').Append(b.head).Append(':')
                  .Append(string.Join(",", RM_BazaarKernel.RingOldestFirst(b.ring, b.head).Select(x => x.ToString("R")))).Append(';');
            return sb.ToString();
        }

        private static void Step(World w, Act a)
        {
            Bucket b = w.b[a.bucket % w.b.Length];
            switch (a.kind)
            {
                case 0: // one day of drift over every bucket (a day pass walks them all)
                    w.day++;
                    foreach (var x in w.b)
                    {
                        float oldM = x.mult, oldN = x.nudge;
                        float u = NoiseU(a.arg + (int)(x.target * 1000));
                        x.mult = RM_BazaarKernel.DriftStep(x.mult, x.target, ref x.nudge, u);
                        Push(x, x.mult);
                        Check(Math.Abs(x.mult - oldM) <= oldM * RM_BazaarKernel.MaxDailyStep * 1.0001f + 1e-6f,
                            $"daily move {oldM}->{x.mult} exceeds {RM_BazaarKernel.MaxDailyStep * 100}% of the old value");
                        Check(Math.Abs(x.nudge) <= Math.Abs(oldN) * RM_BazaarKernel.NudgeDecay + 1e-7f, $"nudge grew in a drift: {oldN}->{x.nudge}");
                        Check(x.nudge == 0f || Math.Abs(x.nudge) >= 0.001f, $"nudge dust left behind: {x.nudge}");
                        Check(x.nudge == 0f || Math.Sign(x.nudge) == Math.Sign(oldN), $"nudge changed sign in a drift: {oldN}->{x.nudge}");
                    }
                    break;
                case 1: // event nudge
                    b.nudge = RM_BazaarKernel.NudgeBy(b.nudge, Fraction(a.arg));
                    Check(b.nudge >= RM_BazaarKernel.NudgeMin && b.nudge <= RM_BazaarKernel.NudgeMax, $"nudge {b.nudge} outside [{RM_BazaarKernel.NudgeMin},{RM_BazaarKernel.NudgeMax}]");
                    break;
                case 2: // session-open observation: one more history entry for this bucket
                    Push(b, b.mult);
                    break;
                case 3: // save + load of a well-formed ring: order and contents survive
                {
                    var before = RM_BazaarKernel.RingOldestFirst(b.ring, b.head).ToList();
                    var copy = new List<float>(b.ring);
                    int head = RM_BazaarKernel.RingRepair(copy, b.head);
                    var after = RM_BazaarKernel.RingOldestFirst(copy, head).ToList();
                    Check(before.SequenceEqual(after), "a save/load of a well-formed ring reordered or lost history");
                    b.ring = copy; b.head = head;
                    break;
                }
                case 4: // load of an over-long / garbage-head ring (a save from a bigger HistorySize)
                {
                    var copy = new List<float>(b.ring);
                    for (int i = 0; i < a.arg % 40; i++) copy.Add(b.mult);
                    int head = RM_BazaarKernel.RingRepair(copy, a.arg % 97 - 20);
                    Check(copy.Count <= RM_BazaarKernel.HistorySize, $"RingRepair left {copy.Count} entries");
                    Check(copy.Count == 0 ? head == 0 : head >= 0 && head < copy.Count, $"RingRepair head {head} outside [0,{copy.Count})");
                    // the repaired ring keeps working; the reference restarts from what the load left
                    b.ring = copy; b.head = head;
                    b.reference = RM_BazaarKernel.RingOldestFirst(copy, head).ToList();
                    break;
                }
                case 5: // a fresh authored target is seeded into the band, bucket restarts there
                {
                    float t = RM_BazaarKernel.SeedLevel(Level(a.arg));
                    Check(t >= RM_BazaarKernel.BandMin && t <= RM_BazaarKernel.BandMax, $"SeedLevel {t} outside the band");
                    b.mult = t; b.target = t; b.nudge = 0;
                    Push(b, t);
                    break;
                }
            }
            foreach (var x in w.b)
            {
                Check(x.mult >= RM_BazaarKernel.BandMin && x.mult <= RM_BazaarKernel.BandMax, $"multiplier {x.mult} left the band [{RM_BazaarKernel.BandMin},{RM_BazaarKernel.BandMax}]");
                Check(x.ring.Count <= RM_BazaarKernel.HistorySize, $"history ring holds {x.ring.Count} > {RM_BazaarKernel.HistorySize}");
                Check(x.ring.Count < RM_BazaarKernel.HistorySize ? x.head >= 0 && x.head <= x.ring.Count : x.head >= 0 && x.head < RM_BazaarKernel.HistorySize,
                    $"head {x.head} out of range for {x.ring.Count} entries");
                var got = RM_BazaarKernel.RingOldestFirst(x.ring, x.head).ToList();
                Check(got.SequenceEqual(x.reference), $"ring oldest-first [{string.Join(",", got)}] != last pushes [{string.Join(",", x.reference)}]");
                if (a.kind != 4) Check(got.Count == 0 || got[got.Count - 1] == x.reference[x.reference.Count - 1], "newest entry is not the latest push");
            }
        }

        private static string RunSeq(int seed, List<Act> acts)
        {
            try
            {
                var w = Make(seed);
                foreach (var a in acts) { Step(w, a); Steps++; }
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

        private static List<Act> Gen(Random r, int len)
        {
            var l = new List<Act>(len);
            for (int i = 0; i < len; i++)
            {
                // weight drift highest: a game is mostly days passing
                int k = r.Next(10);
                int kind = k < 4 ? 0 : k < 6 ? 1 : k < 8 ? 2 : k == 8 ? (r.Next(2) == 0 ? 3 : 4) : 5;
                l.Add(new Act { kind = kind, bucket = r.Next(6), arg = r.Next(100000) });
            }
            return l;
        }

        public static List<string> Sequences(int n, int baseSeed)
        {
            var fails = new List<string>();
            for (int k = 0; k < n; k++)
            {
                int seed = baseSeed + k;
                var r = new Random(seed * 7919 + 1);
                var acts = Gen(r, r.Next(5, 160));
                Cases++;
                string err = RunSeq(seed, acts);
                if (err == null)
                {
                    // determinism: the same seed and actions replay to the same digest
                    var w1 = Make(seed); foreach (var a in acts) Step(w1, a);
                    var w2 = Make(seed); foreach (var a in acts) Step(w2, a);
                    if (Digest(w1) != Digest(w2)) fails.Add($"drift seed {seed}: two replays of one sequence diverged");
                    continue;
                }
                var min = Shrink(acts, t => RunSeq(seed, t) != null);
                fails.Add($"drift seed {seed}: {RunSeq(seed, min)} | {string.Join(" ", min)}");
                if (fails.Count >= 5) break;
            }
            return fails;
        }

        // Settling: no nudge, a flat walk (u = 0.5 gives zero noise) -> the multiplier walks to its target, never
        // overshooting it and never moving away; with the walk ON it stays in the band for 3 years of days.
        public static List<string> Settle(int n, int baseSeed)
        {
            var fails = new List<string>();
            for (int k = 0; k < n && fails.Count < 5; k++)
            {
                int seed = baseSeed + k;
                var r = new Random(seed);
                Cases++;
                float target = RM_BazaarKernel.SeedLevel(Level(r.Next(100000)));
                float m = RM_BazaarKernel.SeedLevel(Level(r.Next(100000)));
                float nudge = 0f;
                float prev = Math.Abs(m - target);
                float side = Math.Sign(m - target);
                for (int d = 0; d < 400; d++)
                {
                    Steps++;
                    m = RM_BazaarKernel.DriftStep(m, target, ref nudge, 0.5f);
                    float dist = Math.Abs(m - target);
                    if (dist > prev + 1e-6f) { fails.Add($"settle seed {seed}: day {d} moved away from target {target}: {prev} -> {dist}"); break; }
                    if (side != 0 && Math.Sign(m - target) == -side && dist > 1e-6f) { fails.Add($"settle seed {seed}: day {d} overshot target {target} (now {m})"); break; }
                    prev = dist;
                }
                if (fails.Count == 0 || !fails.Last().StartsWith($"settle seed {seed}"))
                    if (prev > 1e-3f) fails.Add($"settle seed {seed}: still {prev} from target {target} after 400 days");
                // noisy walk stays in band for 1,095 days
                m = target; nudge = 0f;
                for (int d = 0; d < 1095; d++)
                {
                    Steps++;
                    if (r.Next(30) == 0) nudge = RM_BazaarKernel.NudgeBy(nudge, Fraction(r.Next(1000)));
                    m = RM_BazaarKernel.DriftStep(m, target, ref nudge, (float)r.NextDouble());
                    if (!(m >= RM_BazaarKernel.BandMin && m <= RM_BazaarKernel.BandMax)) { fails.Add($"settle seed {seed}: noisy walk left the band on day {d}: {m}"); break; }
                }
            }
            return fails;
        }

        // Hash -> unit float: always in [0,1] and monotone in the unsigned hash. Float rounding makes the top 64 uint
        // values exactly 1.0 (the source comment says [0,1)); every consumer tolerates 1.0, so it is tallied, not failed.
        public static long UnitOne;

        public static List<string> Unit01(int n, int baseSeed)
        {
            var fails = new List<string>();
            var r = new Random(baseSeed);
            int[] edge = { 0, 1, -1, -2, -64, -65, int.MinValue, int.MaxValue, int.MinValue + 1, 1 << 24, -(1 << 24) };
            float prev = -1f; uint prevH = 0;
            for (int k = 0; k < n + edge.Length && fails.Count < 5; k++)
            {
                Cases++; Steps++;
                int h = k < edge.Length ? edge[k] : r.Next(int.MinValue, int.MaxValue);
                float u = RM_BazaarKernel.ToUnit(h);
                if (!(u >= 0f && u <= 1f)) fails.Add($"unit hash {h} -> {u} outside [0,1]");
                if (u == 1f) UnitOne++;
                // the noise built from it stays inside +-DailyNoise
                float noise = (u * 2f - 1f) * RM_BazaarKernel.DailyNoise;
                if (Math.Abs(noise) > RM_BazaarKernel.DailyNoise + 1e-7f) fails.Add($"unit hash {h}: noise {noise} beyond +-{RM_BazaarKernel.DailyNoise}");
            }
            // monotone over sorted unsigned hashes
            var hs = Enumerable.Range(0, 2000).Select(_ => (uint)r.Next(int.MinValue, int.MaxValue) ^ (uint)(r.Next(2) << 31)).OrderBy(x => x).ToArray();
            for (int i = 0; i < hs.Length; i++)
            {
                float u = RM_BazaarKernel.ToUnit((int)hs[i]);
                if (u < prev) { fails.Add($"unit not monotone: {prevH} -> {prev}, {hs[i]} -> {u}"); break; }
                prev = u; prevH = hs[i];
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
                ("drift", () => Sequences(N(3000), S(1))),
                ("settle", () => Settle(N(1500), S(1))),
                ("unit", () => Unit01(N(100000), S(1))),
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
            Console.WriteLine($"unit hashes rounding to exactly 1.0 (known float edge, tolerated): {UnitOne}");
            Console.WriteLine($"bazaar fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
