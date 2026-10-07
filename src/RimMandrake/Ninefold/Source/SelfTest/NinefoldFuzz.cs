// Approach B for the Ninefold satiation engine: seeded random ACTION SEQUENCES over RM_NinefoldKernel, the Verse-free
// arithmetic and first-contact/front decisions GameComponent_Ninefold calls. The model of the component (hours, ticks,
// launches, landings, triggers, in the order the component does them) is this file's own; every number and every
// fire/queue/flip decision comes from the kernel. Failures are shrunk by delta debugging and printed as
// `family seed N: message | actions`.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace RimMandrake.Ninefold.SelfTest
{
    internal static class NinefoldFuzz
    {
        public static long Cases, Steps, Fires, Queued, Flips, Pops;
        const int N = 9, OneDay = 60000, Hour = 2500, TaBaa = 5, Shkaar = 7, RootedTicks = OneDay * 4, ShkaarDeaths = 3;
        const float Large = 15f;
        static readonly float[] Amp = { 0.15f, 0.65f, 0.45f, 0.20f, 0.35f, 0.40f, 0.80f, 0.55f, 0.70f };

        internal struct Act
        {
            public int kind, arg;
            public override string ToString()
            {
                string[] names = { "Event", "Hours", "Launch", "Landing", "Death", "Trigger", "Days" };
                return names[kind] + "(" + arg + ")";
            }
        }

        private sealed class S
        {
            public float[] sat = new float[N], mood = new float[N];
            public bool[] unveiled = new bool[N];
            public List<int> pending = new List<int>();
            public int next, violent, lastLaunch, tick, front;
            public bool reckoned;
            public float eventMult = 1f, walkMult = 1f;
            public Random rng;
            public List<(int god, int tick)> fired = new List<(int, int)>();
            public HashSet<int> triggered = new HashSet<int>();
            public List<int> queueModel = new List<int>();
        }

        private static S Make(int seed)
        {
            var r = new Random(seed);
            var s = new S { rng = new Random(seed ^ 0x5bd1e995), tick = r.Next(0, 4) * OneDay };
            s.eventMult = (new[] { 0.1f, 0.5f, 1f, 1f, 2f, 3f })[r.Next(6)];
            s.walkMult = (new[] { 0f, 0.5f, 1f, 2f })[r.Next(4)];
            for (int i = 0; i < N; i++) { s.sat[i] = r.Next(4) == 0 ? (float)(r.NextDouble() * 200 - 100) : 0f; s.mood[i] = 0f; }
            s.lastLaunch = s.tick;
            return s;
        }

        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }

        private static void Fire(S s, int god)
        {
            Check(!s.unveiled[god], $"god {god} fired a second time");
            s.next = RM_NinefoldKernel.MarkFired(s.unveiled, god, s.tick, OneDay);
            Check(s.unveiled[god], "MarkFired did not unveil");
            if (s.fired.Count > 0) Check(s.tick - s.fired[s.fired.Count - 1].tick >= OneDay, $"god {god} fired {s.tick - s.fired[s.fired.Count - 1].tick} ticks after the previous introduction (gap must be >= a day)");
            s.fired.Add((god, s.tick));
            Fires++;
        }

        private static void Trigger(S s, int god)
        {
            s.triggered.Add(god);
            bool wasUnveiled = s.unveiled[god], wasPending = s.pending.Contains(god);
            int pendingBefore = s.pending.Count;
            var c = RM_NinefoldKernel.TryFirstContact(s.unveiled, s.pending, s.tick, s.next, god);
            if (wasUnveiled || wasPending) Check(c == RM_NinefoldKernel.Contact.None && s.pending.Count == pendingBefore, "a repeat trigger was not a no-op");
            else if (c == RM_NinefoldKernel.Contact.Fire)
            {
                Check(pendingBefore == 0 && s.tick >= s.next, "fired while something was queued or the day gate was shut");
                Fire(s, god);
            }
            else
            {
                Check(c == RM_NinefoldKernel.Contact.Queued && s.pending.Count == pendingBefore + 1 && s.pending[s.pending.Count - 1] == god, "queue did not take the god at its tail");
                s.queueModel.Add(god); Queued++;
            }
        }

        private static void StepPending(S s)
        {
            int before = s.pending.Count;
            int g = RM_NinefoldKernel.PopDue(s.pending, s.tick, s.next);
            if (g < 0) { Check(s.pending.Count == before, "PopDue removed without returning"); Check(before == 0 || s.tick < s.next, $"PopDue held {before} queued god(s) although the gate is open (tick {s.tick} >= {s.next})"); return; }
            Check(before > 0 && s.tick >= s.next, "PopDue popped with nothing due");
            Check(s.queueModel.Count > 0 && s.queueModel[0] == g, $"queue not FIFO: popped {g}, expected {(s.queueModel.Count > 0 ? s.queueModel[0] : -1)}");
            s.queueModel.RemoveAt(0);
            Pops++;
            Fire(s, g);
        }

        private static void Event(S s, int god, float raw)
        {
            float[] before = (float[])s.sat.Clone();
            float amount = raw * s.eventMult;
            s.sat[god] = RM_NinefoldKernel.AddSatiation(s.sat[god], amount);
            for (int i = 0; i < N; i++) if (i != god) Check(s.sat[i] == before[i], $"an event for god {god} moved god {i}");
            if (amount >= 0) Check(s.sat[god] >= before[god], $"+{amount} lowered satiation {before[god]} -> {s.sat[god]}");
            else Check(s.sat[god] <= before[god], $"{amount} raised satiation {before[god]} -> {s.sat[god]}");
            int loudest = RM_NinefoldKernel.LoudnessRank(s.sat)[0];
            int newFront = RM_NinefoldKernel.FrontAfterSwing(s.reckoned, s.front, raw, Large, loudest);
            if (newFront != s.front)
            {
                Check(s.reckoned && Math.Abs(raw) >= Large && newFront == loudest, $"front flipped {s.front}->{newFront} on raw {raw} (reckoned {s.reckoned}, loudest {loudest})");
                Flips++;
            }
            else if (s.reckoned && Math.Abs(raw) >= Large) Check(s.front == loudest, "a violent swing left the front off the loudest god");
            s.front = newFront;
        }

        private static void Hours(S s, int count)
        {
            for (int h = 0; h < count; h++)
            {
                for (int sub = 0; sub < 10; sub++) { s.tick += Hour / 10; StepPending(s); }
                float[] beforeSat = (float[])s.sat.Clone();
                for (int i = 0; i < N; i++)
                {
                    float roll = s.rng.Next(6) == 0 ? (s.rng.Next(2) == 0 ? 0f : 0.999999f) : (float)s.rng.NextDouble();
                    float m = RM_NinefoldKernel.MoodStep(s.mood[i], Amp[i], roll, s.walkMult);
                    Check(m >= -100f && m <= 100f && !float.IsNaN(m), $"mood {m} left [-100,100]");
                    s.mood[i] = m;
                }
                s.sat[TaBaa] = RM_NinefoldKernel.ErodeSatiation(s.sat[TaBaa], 0.4f * s.eventMult);
                for (int i = 0; i < N; i++) if (i != TaBaa) Check(s.sat[i] == beforeSat[i], $"the hourly walk moved god {i}'s satiation");
                Check(s.sat[TaBaa] <= beforeSat[TaBaa], "rooted erosion raised Ta'Baa");
                if (!s.unveiled[TaBaa] && s.tick - s.lastLaunch >= RootedTicks)
                {
                    Check(s.tick - s.lastLaunch >= RootedTicks, "rooted contact before the fourth night");
                    Trigger(s, TaBaa);
                }
            }
        }

        private static void Step(S s, Act a)
        {
            switch (a.kind)
            {
                case 0:
                {
                    float[] raws = { 3f, 8f, 15f, -3f, -8f, -15f, 0.5f, -0.5f, 60f };
                    Event(s, a.arg % N, raws[(a.arg / N) % raws.Length]);
                    break;
                }
                case 1: Hours(s, 1 + a.arg % 12); break;
                case 2: // launch: reset the rooted clock AND spike Ta'Baa
                    s.lastLaunch = s.tick;
                    Event(s, TaBaa, Large);
                    break;
                case 3: // landing: reckon the front
                    s.front = RM_NinefoldKernel.LoudnessRank(s.sat)[0];
                    s.reckoned = true;
                    break;
                case 4: // a violent death
                    if (!s.unveiled[Shkaar])
                        if (RM_NinefoldKernel.CountViolentDeath(ref s.violent, ShkaarDeaths)) { Check(s.violent >= ShkaarDeaths, "death count fired early"); Trigger(s, Shkaar); }
                        else Check(s.violent < ShkaarDeaths, "death count did not fire at the threshold");
                    break;
                case 5: // a trigger from a patch; one in three lands after the clock moved but before the component's next step
                    if (a.arg % 3 == 0) s.tick += 1 + (a.arg / 3) % 3000;
                    Trigger(s, a.arg % N);
                    break;
                case 6: Hours(s, 24 * (1 + a.arg % 9)); break;
            }
            // ── invariants ──
            for (int i = 0; i < N; i++)
            {
                Check(s.sat[i] >= -100f && s.sat[i] <= 100f && !float.IsNaN(s.sat[i]), $"satiation[{i}] = {s.sat[i]} left [-100,100]");
                Check(s.mood[i] >= -100f && s.mood[i] <= 100f, $"mood[{i}] = {s.mood[i]}");
            }
            Check(s.pending.Distinct().Count() == s.pending.Count, "duplicate god in the pending queue");
            Check(s.pending.All(g => !s.unveiled[g]), "an unveiled god is still queued");
            Check(s.pending.SequenceEqual(s.queueModel), "queue contents diverged from the FIFO model");
            Check(s.fired.Select(f => f.god).Distinct().Count() == s.fired.Count, "a god was introduced twice");
            foreach (var f in s.fired)
                Check(s.triggered.Contains(f.god), $"god {f.god} was introduced without ever being triggered");
            if (s.unveiled[Shkaar] && !s.triggered.Contains(Shkaar)) Check(false, "Sh'kaar unveiled untriggered");
            var rank = RM_NinefoldKernel.LoudnessRank(s.sat);
            Check(rank.OrderBy(x => x).SequenceEqual(Enumerable.Range(0, N)), "rank is not a permutation of the nine gods");
            for (int i = 1; i < rank.Count; i++)
            {
                float la = Math.Abs(s.sat[rank[i - 1]]), lb = Math.Abs(s.sat[rank[i]]);
                Check(la > lb || (la == lb && rank[i - 1] < rank[i]), $"rank not loudest-first / ordinal tie-break at {i}");
            }
            Check(rank.SequenceEqual(RM_NinefoldKernel.LoudnessRank(s.sat)), "rank not deterministic");
            Check(!s.reckoned || (s.front >= 0 && s.front < N), $"front {s.front} is not a god");
        }

        private static string Digest(S s)
        {
            return string.Join(",", s.sat.Select(x => x.ToString("R"))) + "|" + string.Join(",", s.mood.Select(x => x.ToString("R"))) + "|" + string.Join(",", s.fired.Select(f => f.god + "@" + f.tick)) + "|" + s.front + "|" + string.Join(",", s.pending);
        }

        private static string RunSeq(int seed, List<Act> acts, bool liveness)
        {
            try
            {
                var s = Make(seed);
                foreach (var a in acts) { Step(s, a); Steps++; }
                if (liveness)
                {
                    // nothing new triggered: the queue must drain, one introduction per day
                    int guard = s.pending.Count + 2;
                    Hours(s, 24 * guard);
                    Check(s.pending.Count == 0, $"{s.pending.Count} gods still queued after {guard} quiet days");
                    Check(s.queueModel.Count == 0, "queue model not empty");
                }
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
                int len = r.Next(5, 100);
                var acts = new List<Act>();
                for (int i = 0; i < len; i++)
                {
                    int q = r.Next(20);
                    int kind = q < 7 ? 0 : q < 10 ? 1 : q < 11 ? 2 : q < 12 ? 3 : q < 14 ? 4 : q < 18 ? 5 : 6;
                    acts.Add(new Act { kind = kind, arg = r.Next(100000) });
                }
                Cases++;
                string err = RunSeq(seed, acts, true);
                if (err == null)
                {
                    var s1 = Make(seed); foreach (var a in acts) Step(s1, a);
                    var s2 = Make(seed); foreach (var a in acts) Step(s2, a);
                    if (Digest(s1) != Digest(s2)) fails.Add($"seq seed {seed}: two replays diverged");
                    continue;
                }
                var min = Shrink(acts, t => RunSeq(seed, t, true) != null);
                fails.Add($"seq seed {seed}: {RunSeq(seed, min, true)} | {string.Join(" ", min)}");
                if (fails.Count >= 5) break;
            }
            return fails;
        }

        // The five bands: exact boundaries (each boundary belongs to its NAMED endpoint) and monotone in satiation.
        public static List<string> Bands(int n, int baseSeed)
        {
            var fails = new List<string>();
            (float v, SatiationBand b)[] table =
            {
                (100f, SatiationBand.Exalted), (60f, SatiationBand.Exalted), (59.999f, SatiationBand.Content), (20f, SatiationBand.Content),
                (19.999f, SatiationBand.Neutral), (0f, SatiationBand.Neutral), (-19.999f, SatiationBand.Neutral), (-20f, SatiationBand.Slighted),
                (-59.999f, SatiationBand.Slighted), (-60f, SatiationBand.Wrathful), (-100f, SatiationBand.Wrathful),
            };
            foreach (var t in table) if (SatiationBandUtility.BandFor(t.v) != t.b) fails.Add($"band boundary: BandFor({t.v}) = {SatiationBandUtility.BandFor(t.v)}, expected {t.b}");
            var r = new Random(baseSeed);
            // Rekko's -15 per deconstruct lands on -60 exactly after four: sequences of exact steps hit boundaries
            float x = 0; for (int i = 0; i < 4; i++) x = RM_NinefoldKernel.AddSatiation(x, -15f);
            if (SatiationBandUtility.BandFor(x) != SatiationBand.Wrathful) fails.Add($"four -15 deconstructs reach {x} = {SatiationBandUtility.BandFor(x)}, expected Wrathful");
            for (int k = 0; k < n && fails.Count < 5; k++)
            {
                Cases++; Steps++;
                float a = (float)(r.NextDouble() * 200 - 100), b = (float)(r.NextDouble() * 200 - 100);
                if (a > b) { float tmp = a; a = b; b = tmp; }
                if (SatiationBandUtility.BandFor(a) > SatiationBandUtility.BandFor(b)) fails.Add($"band not monotone: {a} -> {SatiationBandUtility.BandFor(a)}, {b} -> {SatiationBandUtility.BandFor(b)}");
            }
            return fails;
        }

        // Loudness rank over random satiation vectors, with many exact ties (a fresh colony is nine zeros).
        public static List<string> Ranks(int n, int baseSeed)
        {
            var fails = new List<string>();
            for (int k = 0; k < n && fails.Count < 5; k++)
            {
                var r = new Random(baseSeed + k);
                Cases++; Steps++;
                var sat = new float[N];
                for (int i = 0; i < N; i++) sat[i] = r.Next(3) == 0 ? 0f : (new[] { 15f, -15f, 60f, -60f, 100f })[r.Next(5)] * (r.Next(2) == 0 ? 1f : -1f) * (r.Next(3) == 0 ? 0.5f : 1f);
                var rank = RM_NinefoldKernel.LoudnessRank(sat);
                for (int i = 1; i < N; i++)
                {
                    float la = Math.Abs(sat[rank[i - 1]]), lb = Math.Abs(sat[rank[i]]);
                    if (!(la > lb || (la == lb && rank[i - 1] < rank[i]))) { fails.Add($"rank seed {baseSeed + k}: bad order at {i}: {string.Join(",", rank)} for {string.Join(",", sat)}"); break; }
                }
                var shuffled = (float[])sat.Clone();
                var again = RM_NinefoldKernel.LoudnessRank(shuffled);
                if (!rank.SequenceEqual(again)) fails.Add($"rank seed {baseSeed + k}: not deterministic");
            }
            return fails;
        }

        // Mood walk: a self-driven bounded walk pulled back toward 0. A zero roll-offset step is pure 2% decay
        // (sign kept, never grows), the walk is monotone in the roll and bounded by its amplitude, and with the walk
        // switched off any mood decays to nothing -- a god cannot be stuck on a rail with no event.
        public static List<string> Moods(int n, int baseSeed)
        {
            var fails = new List<string>();
            for (int k = 0; k < n && fails.Count < 5; k++)
            {
                var r = new Random(baseSeed + k);
                Cases++; Steps++;
                float m = (float)(r.NextDouble() * 200 - 100);
                float amp = Amp[r.Next(N)], mult = (new[] { 0f, 0.5f, 1f, 2f })[r.Next(4)];
                float still = RM_NinefoldKernel.MoodStep(m, amp, 0.5f, mult);
                if (Math.Abs(still - m * 0.98f) > 1e-4f) fails.Add($"mood seed {baseSeed + k}: a zero step from {m} gave {still}, expected {m * 0.98f}");
                if (Math.Abs(still) > Math.Abs(m) || (m != 0 && Math.Sign(still) != Math.Sign(m) && still != 0)) fails.Add($"mood seed {baseSeed + k}: the pullback grew or flipped {m} -> {still}");
                float lo = RM_NinefoldKernel.MoodStep(m, amp, 0f, mult), hi = RM_NinefoldKernel.MoodStep(m, amp, 1f, mult);
                if (lo > still || still > hi) fails.Add($"mood seed {baseSeed + k}: not monotone in the roll ({lo}, {still}, {hi})");
                float bound = 5f * amp * mult + 1e-4f;
                if (hi - m * 0.98f > bound && hi < 100f || m * 0.98f - lo > bound && lo > -100f) fails.Add($"mood seed {baseSeed + k}: step beyond +-{bound}");
                float z = m;
                for (int h = 0; h < 600; h++) { z = RM_NinefoldKernel.MoodStep(z, amp, (float)r.NextDouble(), 0f); Steps++; }
                if (Math.Abs(z) > 0.01f) fails.Add($"mood seed {baseSeed + k}: with the walk off, mood {m} is still {z} after 600 hours");
            }
            return fails;
        }

        public static bool Run(double scale, int? oneSeed, string only)
        {
            var sw = Stopwatch.StartNew();
            bool ok = true;
            int Nn(int n) { return oneSeed.HasValue ? 1 : (int)(n * scale); }
            int Sd(int baseSeed) { return oneSeed ?? baseSeed; }
            var fam = new (string name, Func<List<string>> run)[]
            {
                ("seq", () => Sequences(Nn(2000), Sd(1))),
                ("band", () => Bands(Nn(100000), Sd(1))),
                ("rank", () => Ranks(Nn(100000), Sd(1))),
                ("mood", () => Moods(Nn(20000), Sd(1))),
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
            Console.WriteLine($"coverage: {Fires} introductions ({Pops} from the queue, {Queued} queued), {Flips} front flips");
            Console.WriteLine($"ninefold fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
