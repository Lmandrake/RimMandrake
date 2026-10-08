// Approach B for TerminalBiomes: seeded fuzz over the Verse-free kernels the mod calls (../Kernel/*.cs):
//   wells    RM_WellKernel: the drifting light-well book (lifecycle, delayed re-opening, gardener, lid-dark)
//   sphere   RM_SunSphereKernel: the culture clock and its starvation grace
//   channel  RM_ChannelKernel: flow / lane / band grids, cadence, the drift step, the surge grab, the occupant book
//   crust    RM_CrustKernel: the hull-crust clock, doors, rime and crust, chip rewind
//   lamp     RM_LampWatchKernel: the grey lamp watch's burn clock and per-lamp latches
//   misc     RM_TerminalMiscKernel: Sunk rate and scar, the wax procession timer, the veil-fall scheduler
// A failing action sequence is shrunk (delta debugging) and printed as `family seed N: message | actions`.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace RimMandrake.TerminalBiomes.SelfTest
{
    internal static class TerminalBiomesFuzz
    {
        public static long Cases, Steps;
        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }
        private static bool Near(float a, float b, float eps) { return Math.Abs(a - b) <= eps; }

        internal struct Act
        {
            public int kind, a, b;
            public string[] names;
            public override string ToString() { return (names != null && kind < names.Length ? names[kind] : "k" + kind) + "(" + a + "," + b + ")"; }
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

        private static string Drive(int seed, Func<Random, List<Act>> gen, Func<int, List<Act>, string> run)
        {
            var acts = gen(new Random(seed));
            string err = run(seed, acts);
            if (err == null) return null;
            var small = Shrink(acts, t => run(seed, t) != null);
            return run(seed, small) + " | " + string.Join(" ", small);
        }

        private static List<string> Family(string name, int n, int baseSeed, Func<int, string> one)
        {
            var fails = new List<string>();
            for (int k = 0; k < n && fails.Count < 5; k++)
            {
                Cases++;
                try { string e = one(baseSeed + k); if (e != null) fails.Add($"{name} seed {baseSeed + k}: {e}"); }
                catch (Exception e) { fails.Add($"{name} seed {baseSeed + k}: {e.Message} {(e is IndexOutOfRangeException || e is ArgumentOutOfRangeException ? e.StackTrace : "")}"); }
            }
            return fails;
        }



        // ════════════════════════ wells ════════════════════════
        private static readonly string[] WellNames = { "Tick", "Gardener", "LidDark", "Sites", "Cadence" };
        public static long WellsClosed, WellWarnings, GardenerCloses, GardenerAdvances, PendingWaited, WaningVisuals;

        private sealed class W : WellRec { }

        private static List<Act> GenWells(Random r)
        {
            int n = 8 + r.Next(50);
            var l = new List<Act>();
            for (int i = 0; i < n; i++)
            {
                int w = r.Next(100);
                int kind = w < 60 ? 0 : w < 70 ? 1 : w < 78 ? 2 : w < 92 ? 3 : 4;
                l.Add(new Act { kind = kind, a = r.Next(1000), b = r.Next(1000), names = WellNames });
            }
            return l;
        }

        private static string RunWells(int seed, List<Act> acts)
        {
            var r = new Random(seed ^ 0x99);
            int mapX = new[] { 100, 250, 400, 900 }[r.Next(4)];
            int cadence = 1; bool sitesOk = true; int now = 5000;
            var skylights = new HashSet<int>(); int opened = 0;
            var near = new Dictionary<int, bool>();
            var lastFactor = new Dictionary<int, float>();
            var warned = new Dictionary<int, int>();
            var ageSpec = new Dictionary<int, long>();
            int nextSite = 0;
            WellBook<W> book = null;
            book = new WellBook<W>(
                (out int x, out int z) => { x = nextSite % 97; z = nextSite / 97; if (sitesOk) { nextSite++; return true; } return false; },
                w => { skylights.Add(w.id); opened++; near[w.id] = r.Next(2) == 0; ageSpec[w.id] = 0; },
                w =>
                {
                    float f = RM_WellKernel.GlowFactor(w.stage, w.ageTicks, w.lifespanTicks);
                    Check(f >= 0f && f <= 1f, "glow factor out of [0,1]");
                    float t = RM_WellKernel.ColourT(w.stage, w.ageTicks, w.lifespanTicks);
                    Check(t >= 0f && t <= 1f, "colour step out of [0,1]");
                    Check(RM_WellKernel.Radius(f) >= 0.5f, "radius under 0.5");
                    if (w.stage == WellStage.Waning) { WaningVisuals++; Check(f >= 0.2f && f <= 1f, "waning factor out of [0.2,1]"); if (lastFactor.TryGetValue(w.id, out float lf) && lf >= 0f) { } }
                    if (w.stage == WellStage.Standing) Check(f == 1f && t == 0f, "standing well not at full gold");
                    lastFactor[w.id] = f;
                },
                w => { if (near[w.id]) { warned[w.id] = (warned.TryGetValue(w.id, out int c) ? c : 0) + 1; WellWarnings++; return true; } return false; },
                w => { Check(skylights.Remove(w.id), "closed a well that had no skylight"); WellsClosed++; },
                n => n <= 0 ? 0 : r.Next(n), () => cadence);
            string where = "";
            int target = 0;
            try
            {
                book.Initialize(mapX);
                target = book.Wells.Count + book.Pending.Count;
                Check(book.Wells.Count == RM_WellKernel.TargetWellCount(mapX), "initial well count != the target for this map");
                foreach (var w in book.Wells) Check(w.stage == WellStage.Opening || w.stage == WellStage.Standing, "a well started waning or closed");
                foreach (var w in book.Wells) { Check(w.lifespanTicks >= 5 * 60000 && w.lifespanTicks <= 9 * 60000, "lifespan outside 5..9 days"); Check(w.ageTicks < w.lifespanTicks - RM_WellKernel.WaningTicks, "initial age reaches the waning window"); }
                int step = 0;
                foreach (var a in acts)
                {
                    step++; Steps++; where = " at step " + step + " " + a;
                    switch (a.kind)
                    {
                        case 0:
                            for (int i = 0, n = 1 + (a.b % 4 == 0 ? a.a % 600 : a.a % 20); i < n; i++)
                            {
                                now += 250;
                                var before = book.Wells.ToDictionary(w => w.id, w => new[] { w.ageTicks, w.lifespanTicks, (int)w.stage });
                                int pendBefore = book.Pending.Count, wellsBefore = book.Wells.Count;
                                if (cadence == 0) book.ProcessPending(now); else book.Tick(now);
                                foreach (var w in book.Wells)
                                {
                                    if (before.TryGetValue(w.id, out int[] b))
                                    {
                                        if (cadence != 0) { Check(w.ageTicks == b[0] + 250, "a well did not age 250"); Check(w.ageTicks < w.lifespanTicks, "a well past its lifespan stayed open"); }
                                        else Check(w.ageTicks == b[0], "a frozen well aged");
                                        Check((int)w.stage >= b[2], "a well's stage went backwards");
                                    }
                                }
                                if (cadence != 0)
                                    foreach (var kv in before)
                                        if (!book.Wells.Any(w => w.id == kv.Key)) Check(kv.Value[0] + 250 >= kv.Value[1], $"well {kv.Key} closed early (age {kv.Value[0] + 250} of {kv.Value[1]})");
                            }
                            break;
                        case 1:
                            {
                                var waning = book.Wells.Where(w => w.stage == WellStage.Waning).OrderBy(w => w.TicksRemaining).ToList();
                                int wc = book.Wells.Count, pc = book.Pending.Count; int opened0 = opened;
                                int dueAfter = book.Pending.Count == 0 ? 0 : 1 + book.Pending.Skip(1).Count(t => t <= now);   // pending[0] is pulled to now; any other already-due entry opens with it
                                book.GardenerAdvance(now);
                                if (wc == 0) { Check(book.Wells.Count == 0, "gardener changed an empty ledger"); break; }
                                if (waning.Count > 0)
                                {
                                    Check(book.Wells.Count == wc - 1 && !book.Wells.Any(w => w.id == waning[0].id), "the gardener did not close the well nearest its end");
                                    Check(book.Pending.Count == pc + 1, "a gardener close did not schedule a re-opening"); GardenerCloses++;
                                }
                                else if (pc > 0)
                                {
                                    if (sitesOk) { Check(book.Wells.Count == wc + dueAfter && book.Pending.Count == pc - dueAfter, $"the gardener opened {book.Wells.Count - wc}, expected {dueAfter} due"); GardenerAdvances++; }
                                    else { Check(book.Wells.Count == wc && book.Pending.Count == pc, "the gardener changed things with no site"); PendingWaited++; }
                                }
                                else Check(book.Wells.Count == wc && book.Pending.Count == pc, "the gardener changed things with nothing to do");
                                break;
                            }
                        case 2:
                            {
                                var before = book.Wells.ToDictionary(w => w.id, w => w.ageTicks);
                                book.LidDarkEnded(now);
                                foreach (var w in book.Wells) if (before.TryGetValue(w.id, out int b0)) Check(w.ageTicks >= b0 && w.ageTicks < b0 + 15000, "lid-dark aged a well by an amount outside [0, 15000)");
                                break;
                            }
                        case 3: sitesOk = a.a % 3 != 0; break;
                        case 4: cadence = a.a % 3; break;
                    }
                    // the ledger's own invariants
                    Check(book.Wells.Count + book.Pending.Count == target, $"wells {book.Wells.Count} + pending {book.Pending.Count} != {target}: a closed well's replacement was lost");
                    Check(skylights.Count == book.Wells.Count, $"{skylights.Count} skylights for {book.Wells.Count} wells");
                    foreach (var w in book.Wells)
                    {
                        Check(w.stage != WellStage.Closed, "a closed well is still listed");
                        Check(w.stage == RM_WellKernel.StageOf(w.ageTicks, w.lifespanTicks), $"well stage {w.stage} but age {w.ageTicks}/{w.lifespanTicks} says {RM_WellKernel.StageOf(w.ageTicks, w.lifespanTicks)}");
                        Check(skylights.Contains(w.id), "a listed well has no skylight");
                    }
                    Check(warned.Values.All(c => c <= 1), "a well warned twice");
                    Check(book.Wells.Select(w => w.id).Distinct().Count() == book.Wells.Count, "duplicate well id");
                }
            }
            catch (Exception e) when (!(e is OutOfMemoryException)) { return e.Message + where + (e is IndexOutOfRangeException || e is ArgumentOutOfRangeException ? " " + e.StackTrace : ""); }
            return null;
        }

        private static List<string> Wells(int n, int baseSeed) { return Family("wells", n, baseSeed, seed => Drive(seed, GenWells, RunWells)); }

        private static string RunWellProps(int seed)
        {
            var r = new Random(seed);
            Check(RM_WellKernel.TargetWellCount(0) == 3 && RM_WellKernel.TargetWellCount(125) == 4 && RM_WellKernel.TargetWellCount(250) == 5 && RM_WellKernel.TargetWellCount(375) == 6 && RM_WellKernel.TargetWellCount(5000) == 6, "TargetWellCount values");
            for (int roll = 0; roll < 5; roll++) { Check(RM_WellKernel.Lifespan(roll, 1) == (5 + roll) * 60000 && RM_WellKernel.Lifespan(roll, 2) == (5 + roll) * 120000 && RM_WellKernel.Lifespan(roll, 0) == (5 + roll) * 60000, "Lifespan"); }
            int life = (5 + r.Next(5)) * 60000;
            WellStage prev = WellStage.Opening; float pf = -1f;
            for (int age = 0; age <= life + 5000; age += 250)
            {
                WellStage s = RM_WellKernel.StageOf(age, life);
                Check((int)s >= (int)prev, "StageOf went backwards over age"); prev = s;
                int remaining = life - age;
                WellStage want = age < 30000 ? WellStage.Opening : remaining <= 0 ? WellStage.Closed : remaining <= 90000 ? WellStage.Waning : WellStage.Standing;
                Check(s == want, $"StageOf({age}, {life}) = {s}, want {want}");
                float f = RM_WellKernel.GlowFactor(s, age, life);
                if (s == WellStage.Opening) { Check(f >= pf - 1e-6f, "opening factor fell"); pf = f; }
                if (s == WellStage.Waning) { Check(f <= 1f && f >= 0.2f, "waning factor range"); }
            }
            Check(RM_WellKernel.GlowFactor(WellStage.Opening, 30000, life) == 1f && RM_WellKernel.GlowFactor(WellStage.Opening, 0, life) == 0f, "opening ramp ends");
            // waning steps once per half day, 1.0 -> 0.8 -> 0.6 -> 0.4
            int ws = life - 90000;
            Check(Near(RM_WellKernel.GlowFactor(WellStage.Waning, ws, life), 1f, 1e-5f) && Near(RM_WellKernel.GlowFactor(WellStage.Waning, ws + 30000, life), 0.8f, 1e-5f)
                && Near(RM_WellKernel.GlowFactor(WellStage.Waning, ws + 60000, life), 0.6f, 1e-5f) && Near(RM_WellKernel.GlowFactor(WellStage.Waning, life - 1, life), 0.6f, 1e-5f), "waning steps are 20% per half-day, three steps");
            // the fourth step (0.4 / full cool colour) would be reached only at age == lifespan, when the well is already closed
            Check(Near(RM_WellKernel.ColourT(WellStage.Waning, life - 1, life), 2f / 3f, 1e-5f) && RM_WellKernel.WaningStep(life, life) == 3, "the colour reaches two thirds of the way to cool-dead before the well closes");
            Check(RM_WellKernel.Radius(1f) == 6f && RM_WellKernel.Radius(0f) == 0.5f, "Radius");
            return null;
        }

        private static List<string> WellProps(int n, int baseSeed) { return Family("wells-props", n, baseSeed, RunWellProps); }

        // ════════════════════════ sphere ════════════════════════
        public static long SphereMature, SphereHusked, SphereSeeded, SphereConsumed;

        private static string RunSphere(int seed)
        {
            var r = new Random(seed);
            var stage = RM_SunSphereStage.Husk; int culture = 0, starved = 0;
            int grace = new[] { 0, 60000, 120000, 300000 }[r.Next(4)];
            bool seed1 = r.Next(2) == 0;
            // independent model
            int mCulture = 0, mStarved = 0, mStage = 0; // 0 husk 1 seeded 2 culturing 3 mature
            float prevFactor = 0f; RM_SunSphereStage prevStage = stage;
            bool phaseFed = true; int phaseLeft = 0;
            for (int step = 0; step < 14000; step++)
            {
                Steps++;
                bool seedNow = r.Next(8) == 0 ? !seed1 : seed1; seed1 = seedNow;
                if (phaseLeft <= 0) { phaseFed = r.Next(10) < 6; phaseLeft = 1 + r.Next(r.Next(3) == 0 ? 7000 : 1500); }
                phaseLeft--;
                bool fed = phaseFed || step < 20;
                bool consumed = RM_SunSphereKernel.Step(ref stage, ref culture, ref starved, seed1 && r.Next(1) == 0 || seed1, fed, grace, 60);
                // model
                bool mConsumed = false;
                if (mStage == 0) { if (seed1) { mStage = 1; mCulture = 0; mStarved = 0; mConsumed = true; } }
                else if (fed)
                {
                    mStarved = 0; mCulture += 60;
                    if (mStage == 1 && mCulture > 0) mStage = 2;
                    if (mCulture >= 360000) { mCulture = 360000; mStage = 3; }
                }
                else
                {
                    mStarved += 60;
                    if (grace > 0 && mStarved >= grace) { mStage = 0; mCulture = 0; mStarved = 0; }
                }
                Check(consumed == mConsumed, $"seed consumed={consumed} want {mConsumed} at step {step}");
                if (consumed) SphereConsumed++;
                Check((int)stage == mStage && culture == mCulture && starved == mStarved, $"sphere state {stage}/{culture}/{starved} want {mStage}/{mCulture}/{mStarved} at step {step}");
                Check(culture >= 0 && culture <= RM_SunSphereKernel.CultureTicksToMature, "culture out of range");
                if (stage == RM_SunSphereStage.Mature) { Check(culture == RM_SunSphereKernel.CultureTicksToMature, "mature before the culture finished"); SphereMature++; }
                if (stage == RM_SunSphereStage.Husk) { Check(culture == 0 && starved == 0, "a husk keeps culture or hunger"); if (prevStage != RM_SunSphereStage.Husk) SphereHusked++; }
                if (stage == RM_SunSphereStage.Seeded) SphereSeeded++;
                float f = RM_SunSphereKernel.Factor(stage, culture);
                Check(RM_SunSphereKernel.Radius(f) >= 0.05f && f >= 0f && f <= 1f, "factor range");
                switch (stage)
                {
                    case RM_SunSphereStage.Husk: Check(f == 0f, "husk glows"); break;
                    case RM_SunSphereStage.Seeded: Check(f == 0.1f, "seeded factor"); break;
                    case RM_SunSphereStage.Culturing: Check(f >= 0.15f - 1e-5f && f <= 0.7f + 1e-5f, "culturing factor range"); break;
                    default: Check(f == 1f, "mature factor"); break;
                }
                if (stage == prevStage && stage == RM_SunSphereStage.Culturing) Check(f >= prevFactor - 1e-5f, "culturing glow fell while culturing");
                prevFactor = f; prevStage = stage;
            }
            // a fed seeded sphere matures in exactly 6000 steps
            var st = RM_SunSphereStage.Seeded; int c2 = 0, s2 = 0; int n = 0;
            while (st != RM_SunSphereStage.Mature && n < 10000) { RM_SunSphereKernel.Step(ref st, ref c2, ref s2, false, true, 60000, 60); n++; }
            Check(n == 6000, $"a fed sphere matured in {n} steps, expected 6000");
            return null;
        }

        private static List<string> Sphere(int n, int baseSeed) { return Family("sphere", n, baseSeed, RunSphere); }

        // ════════════════════════ channel ════════════════════════
        private static readonly string[] ChannelNames = { "Time", "Surge", "Item", "Pawn", "Grab" };
        public static long ChanSteps, ChanSinks, ChanStops, ChanGrabs, ChanSurgeSteps, ChanHarness;

        private sealed class Occ { public int x, z; public bool pawn, harness; public int id; }

        private static List<Act> GenChannel(Random r)
        {
            int n = 6 + r.Next(40);
            var l = new List<Act>();
            for (int i = 0; i < n; i++)
            {
                int w = r.Next(100);
                int kind = w < 55 ? 0 : w < 65 ? 1 : w < 80 ? 2 : w < 92 ? 3 : 4;
                l.Add(new Act { kind = kind, a = r.Next(1000), b = r.Next(1000), names = ChannelNames });
            }
            return l;
        }

        private static readonly int[] Dx = { 0, 0, 1, 1, 1, 0, -1, -1, -1 }, Dz = { 0, 1, 1, 0, -1, -1, -1, 0, 1 };

        private static string RunChannel(int seed, List<Act> acts)
        {
            var r = new Random(seed ^ 0x2468);
            int W = 8 + r.Next(14), H = 8 + r.Next(10);
            var f = new ChannelField(W, H);
            var blocked = new bool[W * H]; var sink = new HashSet<int>();
            // a channel: random walk of flow cells with lanes, and a bank of band cells pointing in
            int x = r.Next(W), z = r.Next(H);
            int dir = 1 + r.Next(8);
            for (int i = 0; i < 40; i++)
            {
                if (r.Next(4) == 0) dir = 1 + r.Next(8);
                f.SetFlow(x, z, dir, r.Next(2) == 0 ? 2 : 1);
                x = Math.Max(0, Math.Min(W - 1, x + Dx[dir])); z = Math.Max(0, Math.Min(H - 1, z + Dz[dir]));
            }
            for (int i = 0; i < 25; i++) f.SetBankBand(r.Next(W), r.Next(H), 1 + r.Next(8), r.Next(-1, 5));
            for (int i = 0; i < W * H / 12; i++) blocked[r.Next(W * H)] = true;
            for (int i = 0; i < 3; i++) sink.Add(r.Next(W * H));
            foreach (int s in sink) blocked[s] = false;
            Func<int, int, bool> standable = (a, b) => f.InBounds(a, b) && !blocked[b * W + a];
            Func<int, int, bool> isSink = (a, b) => sink.Contains(b * W + a);
            float strength = new[] { 0.25f, 1f, 2f, 0.01f }[r.Next(4)];
            var book = new ChannelBook<Occ>(); var occs = new List<Occ>(); int now = 100; int nextId = 1;
            string where = "";
            Action<Occ> reg = o => book.Register(o, now, RM_ChannelKernel.CadenceFor(f.LaneAt(o.x, o.z), f.Surge, o.harness, o.pawn, strength));
            try
            {
                // band clamp and field basics
                for (int zz = 0; zz < H; zz++) for (int xx = 0; xx < W; xx++) Check(f.BankBandAt(xx, zz) >= 0 && f.BankBandAt(xx, zz) <= 2, "band out of 0..2");
                Check(!f.HasCurrent(-1, 0) && !f.HasCurrent(W, 0) && f.LaneAt(-1, -1) == 0 && f.FlowAt(W + 3, 0) == 0, "out-of-bounds queries");
                int step = 0;
                foreach (var a in acts)
                {
                    step++; Steps++; where = " at step " + step + " " + a;
                    switch (a.kind)
                    {
                        case 0:
                            for (int t = 0; t < 1 + a.a % 40; t++)
                            {
                                now += 15;
                                foreach (var o in book.Keys())
                                {
                                    if (!book.TryGetDue(o, out int due) || now < due) continue;
                                    ChanSteps++; if (f.Surge) ChanSurgeSteps++;
                                    // independent spec from the raw grids
                                    int idx = o.z * W + o.x;
                                    bool cur = f.Lane[idx] != 0 || (f.Surge && f.Band[idx] > 0 && f.Flow[idx] != 0);
                                    int fd = f.Flow[idx];
                                    int nx = o.x + (fd >= 1 && fd <= 8 ? Dx[fd] : 0), nz = o.z + (fd >= 1 && fd <= 8 ? Dz[fd] : 0);
                                    ChannelStep want = !cur || fd < 1 || fd > 8 || nx < 0 || nz < 0 || nx >= W || nz >= H || blocked[nz * W + nx] ? ChannelStep.Stop : sink.Contains(nz * W + nx) ? ChannelStep.Sink : ChannelStep.Moved;
                                    ChannelStep got = RM_ChannelKernel.Step(f, o.x, o.z, standable, isSink, out int gx, out int gz);
                                    Check(got == want, $"Step {got} want {want} from {o.x},{o.z} flow {fd}");
                                    if (got == ChannelStep.Moved || got == ChannelStep.Sink) Check(gx == nx && gz == nz, "Step went to the wrong cell");
                                    if (got == ChannelStep.Moved)
                                    {
                                        Check(Math.Abs(gx - o.x) <= 1 && Math.Abs(gz - o.z) <= 1 && (gx != o.x || gz != o.z), "a step moved more than one cell");
                                        o.x = gx; o.z = gz; reg(o);
                                    }
                                    else { book.Remove(o); if (got == ChannelStep.Sink) { ChanSinks++; occs.Remove(o); } else ChanStops++; }
                                }
                            }
                            break;
                        case 1:
                            f.Surge = !f.Surge;
                            if (f.Surge)
                            {
                                foreach (var o in occs.ToList())
                                {
                                    bool ok = RM_ChannelKernel.GrabTarget(f, o.x, o.z, standable, out int tx, out int tz);
                                    // spec
                                    bool wantOk = false; int wx = 0, wz = 0;
                                    if (f.Band[o.z * W + o.x] > 0 && f.Flow[o.z * W + o.x] >= 1 && f.Flow[o.z * W + o.x] <= 8)
                                    {
                                        int d = f.Flow[o.z * W + o.x];
                                        int x2 = o.x + 2 * Dx[d], z2 = o.z + 2 * Dz[d], x1 = o.x + Dx[d], z1 = o.z + Dz[d];
                                        if (standable(x2, z2)) { wantOk = true; wx = x2; wz = z2; }
                                        else if (standable(x1, z1)) { wantOk = true; wx = x1; wz = z1; }
                                    }
                                    Check(ok == wantOk && (!ok || (tx == wx && tz == wz)), $"GrabTarget {ok} ({tx},{tz}) want {wantOk} ({wx},{wz})");
                                    if (ok) { o.x = tx; o.z = tz; ChanGrabs++; if (f.HasCurrent(o.x, o.z)) reg(o); }
                                }
                            }
                            break;
                        case 2:
                        case 3:
                            {
                                var o = new Occ { id = nextId++, x = a.a % W, z = a.b % H, pawn = a.kind == 3, harness = a.kind == 3 && a.a % 4 == 0 };
                                if (blocked[o.z * W + o.x]) break;
                                occs.Add(o); if (o.harness) ChanHarness++;
                                // the scan: a thing on a current cell is registered once
                                if (f.HasCurrent(o.x, o.z)) { Check(!book.Contains(o), "registered twice"); reg(o); }
                                break;
                            }
                        case 4:
                            {
                                // scan pass: everyone currently on current is present; the rest are pruned
                                var present = new HashSet<Occ>();
                                foreach (var o in occs) if (f.HasCurrent(o.x, o.z)) { present.Add(o); if (!book.Contains(o)) reg(o); }
                                book.Prune(present);
                                foreach (var o in book.Keys()) Check(present.Contains(o), "a pruned occupant survived");
                                break;
                            }
                    }
                    foreach (var o in occs) Check(o.x >= 0 && o.z >= 0 && o.x < W && o.z < H && !blocked[o.z * W + o.x], "an occupant left the map or sits in a blocked cell");
                    foreach (var o in book.Keys()) Check(occs.Contains(o), "the book holds a thing that is gone");
                }
            }
            catch (Exception e) when (!(e is OutOfMemoryException)) { return e.Message + where + (e is IndexOutOfRangeException || e is ArgumentOutOfRangeException ? " " + e.StackTrace : ""); }
            return null;
        }

        private static List<string> Channel(int n, int baseSeed) { return Family("channel", n, baseSeed, seed => Drive(seed, GenChannel, RunChannel)); }

        private static string RunChannelProps(int seed)
        {
            var r = new Random(seed);
            // offsets: 8 distinct directions, none for 0 and out of range
            var seen = new HashSet<(int, int)>();
            for (int d = 1; d <= 8; d++) { Check(RM_ChannelKernel.Offset(d, out int dx, out int dz) && dx == Dx[d] && dz == Dz[d], "Offset " + d); seen.Add((dx, dz)); }
            Check(seen.Count == 8 && !RM_ChannelKernel.Offset(0, out int _, out int _) && !RM_ChannelKernel.Offset(9, out int _, out int _) && !RM_ChannelKernel.Offset(255, out int _, out int _), "Offset set");
            // cadence table
            Check(RM_ChannelKernel.CadenceFor(2, false, false, true, 1f) == 45 && RM_ChannelKernel.CadenceFor(1, false, false, true, 1f) == 90 && RM_ChannelKernel.CadenceFor(0, false, false, true, 1f) == 90, "base cadence");
            Check(RM_ChannelKernel.CadenceFor(2, true, false, true, 1f) == 22 && RM_ChannelKernel.CadenceFor(1, true, false, true, 1f) == 22 && RM_ChannelKernel.CadenceFor(1, true, true, true, 1f) == 90 && RM_ChannelKernel.CadenceFor(2, false, true, true, 1f) == 90, "surge doubles centre, promotes margin, harness caps");
            Check(RM_ChannelKernel.CadenceFor(2, false, false, false, 1f) == 90 && RM_ChannelKernel.CadenceFor(1, false, false, false, 1f) == 180, "items drift at half the pawn rate");
            for (int k = 0; k < 20; k++)
            {
                int lane = r.Next(3); bool surge = r.Next(2) == 0, har = r.Next(2) == 0, pawn = r.Next(2) == 0; float s1 = 0.05f + (float)r.NextDouble() * 3f, s2 = s1 + 0.5f;
                int c1 = RM_ChannelKernel.CadenceFor(lane, surge, har, pawn, s1), c2 = RM_ChannelKernel.CadenceFor(lane, surge, har, pawn, s2);
                Check(c1 >= 1 && c2 >= 1 && c2 <= c1, "a stronger current was slower or the cadence hit 0");
                Check(RM_ChannelKernel.CadenceFor(lane, surge, har, false, s1) >= RM_ChannelKernel.CadenceFor(lane, surge, har, true, s1), "an item drifted faster than a pawn");
            }
            Check(RM_ChannelKernel.CadenceFor(2, false, false, true, 0f) == 900 && RM_ChannelKernel.CadenceFor(2, false, false, true, -3f) == 900, "strength is floored at 0.05");
            // adopt a wrong-size grid
            var f = new ChannelField(5, 4);
            f.Adopt(new byte[3], new byte[20], null);
            Check(f.Flow.Length == 20 && f.Lane.Length == 20 && f.Band.Length == 20, "Adopt did not replace a wrong-size grid with an empty one");
            f.SetBankBand(1, 1, 3, 9); Check(f.BankBandAt(1, 1) == 2 && f.FlowAt(1, 1) == 3, "SetBankBand clamp / direction");
            f.SetFlow(2, 2, 5, 2); f.SetBankBand(2, 2, 7, 1); Check(f.FlowAt(2, 2) == 5, "SetBankBand overwrote a channel cell's flow");
            f.SetBankBand(0, 0, 2, 1); Check(!f.HasCurrent(0, 0), "a calm bank has current"); f.Surge = true; Check(f.HasCurrent(0, 0) && f.LaneAt(0, 0) == 1, "a surge did not widen the bank into margin");
            f.SetBankBand(3, 0, 0, 1); Check(!f.HasCurrent(3, 0), "a bank cell with no direction has current in a surge");
            return null;
        }

        private static List<string> ChannelProps(int n, int baseSeed) { return Family("channel-props", n, baseSeed, RunChannelProps); }

        // ════════════════════════ crust ════════════════════════
        private static readonly string[] CrustNames = { "Step", "Rewind", "Big" };
        public static long CrustDoors, CrustRimes, CrustPatches, CrustRewinds, CrustFloors;

        private static List<Act> GenCrust(Random r)
        {
            int n = 5 + r.Next(60);
            var l = new List<Act>();
            for (int i = 0; i < n; i++)
            {
                int w = r.Next(100);
                l.Add(new Act { kind = w < 70 ? 0 : w < 90 ? 1 : 2, a = r.Next(1000), b = r.Next(1000), names = CrustNames });
            }
            return l;
        }

        private static string RunCrust(int seed, List<Act> acts)
        {
            var r = new Random(seed ^ 0x777);
            float days = 0f, nextDoor = RM_CrustKernel.FirstDoorDays;
            bool rimeDef = r.Next(5) != 0, crustDef = r.Next(5) != 0;
            string where = "";
            try
            {
                int step = 0;
                foreach (var a in acts)
                {
                    step++; Steps++; where = " at step " + step + " " + a;
                    if (a.kind == 1)
                    {
                        float d0 = days, n0 = nextDoor;
                        RM_CrustKernel.Rewind(ref days, ref nextDoor);
                        Check(days == Math.Max(0f, d0 - 0.25f) && nextDoor == Math.Max(2.5f, n0 - 0.25f), "rewind arithmetic");
                        CrustRewinds++; if (days == 0f) CrustFloors++;
                    }
                    else
                    {
                        float mult = RM_CrustKernel.Multiplier(new[] { 0.5f, 1f, 3f }[a.a % 3], a.b % 2 == 0, 2f, a.b % 3 == 0, 1.5f);
                        float add = RM_CrustKernel.AddDays(2500, mult * (a.kind == 2 ? 200f : 1f));
                        Check(add >= 0f, "negative days");
                        float d0 = days, n0 = nextDoor; int rolls = 0; var asked = new List<float>();
                        RM_CrustKernel.Step(ref days, ref nextDoor, add, rimeDef, crustDef, p => { rolls++; asked.Add(p); return (a.a + rolls) % 2 == 0; }, out bool rime, out int doors, out bool crust);
                        Check(Near(days, d0 + add, 1e-4f), "clock did not advance by the days added");
                        // doors: one per interval crossed
                        int wantDoors = 0; float nn = n0; while (d0 + add >= nn) { nn += 1f; wantDoors++; }
                        Check(doors == wantDoors && Near(nextDoor, nn, 1e-4f), $"doors {doors} want {wantDoors}");
                        Check(days < nextDoor, "the next door is already due after a step");
                        if (days < 1f) Check(!rime, "rime before day 1");
                        if (!rimeDef) Check(!rime, "rime without a rime def");
                        if (days < 5f || !crustDef) Check(!crust, "crust too early or without a def");
                        if (days >= 5f && crustDef) { Check(asked.Count >= 1 && asked.All(p => p >= 0.1f - 1e-5f && p <= 1f + 1e-5f), "crust chance out of [0.1, 1]"); }
                        CrustDoors += doors; if (rime) CrustRimes++; if (crust) CrustPatches++;
                    }
                    Check(days >= 0f && nextDoor >= 2.5f, "clock or door threshold under their floors");
                }
                Check(RM_CrustKernel.CrustChance(5f) == 0.1f && Near(RM_CrustKernel.CrustChance(15f), 1f, 1e-6f) && Near(RM_CrustKernel.CrustChance(10f), 0.55f, 1e-5f) && RM_CrustKernel.CrustChance(0f) == 0.1f && Near(RM_CrustKernel.CrustChance(99f), 1f, 1e-6f), "CrustChance ramp");
                Check(RM_CrustKernel.CrustCap(0) == 1 && RM_CrustKernel.CrustCap(2) == 1 && RM_CrustKernel.CrustCap(3) == 1 && RM_CrustKernel.CrustCap(9) == 3 && RM_CrustKernel.CrustCap(100) == 33, "CrustCap");
                Check(RM_CrustKernel.Multiplier(2f, false, 9f, false, 9f) == 2f && RM_CrustKernel.Multiplier(2f, true, 3f, true, 5f) == 30f, "Multiplier");
            }
            catch (Exception e) when (!(e is OutOfMemoryException)) { return e.Message + where; }
            return null;
        }

        private static List<string> Crust(int n, int baseSeed) { return Family("crust", n, baseSeed, seed => Drive(seed, GenCrust, RunCrust)); }

        // ════════════════════════ lamp ════════════════════════
        private static readonly string[] LampNames = { "Burn", "Dark", "Toggle", "Answer" };
        public static long LampWatches, LampScrapes, LampAnswers, LampResets;

        private static List<Act> GenLamp(Random r)
        {
            int n = 8 + r.Next(60);
            var l = new List<Act>();
            for (int i = 0; i < n; i++)
            {
                int w = r.Next(100);
                l.Add(new Act { kind = w < 62 ? 0 : w < 78 ? 1 : w < 90 ? 2 : 3, a = r.Next(1000), b = r.Next(1000), names = LampNames });
            }
            return l;
        }

        private static string RunLamp(int seed, List<Act> acts)
        {
            var r = new Random(seed ^ 0x31);
            const int L = 4; int threshold = LampWatchBook.ThresholdTicks(new[] { 1f, 2f, 6f }[r.Next(3)]);
            var book = new LampWatchBook();
            var dark = new bool[L]; var lit = new int[L]; var scraped = new bool[L]; var answered = new bool[L]; var answerOk = new bool[L];
            for (int i = 0; i < L; i++) answerOk[i] = r.Next(3) != 0;
            bool watcher = true, giant = true;
            var watchCalls = new int[L]; var scrapeCalls = new int[L]; var answerCalls = new int[L];
            string where = "";
            try
            {
                Check(LampWatchBook.ThresholdTicks(2f) == 5000 && LampWatchBook.ThresholdTicks(0.5f) == 1250, "ThresholdTicks");
                int step = 0;
                foreach (var a in acts)
                {
                    step++; Steps++; where = " at step " + step + " " + a;
                    switch (a.kind)
                    {
                        case 0:
                            {
                                int ticks = 250 * (1 + a.a % 8);
                                var litNow = new List<int>();
                                for (int i = 0; i < L; i++) if (!dark[i] && (a.b >> i & 1) == 0) litNow.Add(i); else if (!dark[i]) { }
                                // lamps left out of litNow are "dark this pass" (reset)
                                var notLit = Enumerable.Range(0, L).Where(i => !litNow.Contains(i)).ToList();
                                foreach (int i in notLit) { if (lit[i] > 0 || scraped[i] || answered[i]) LampResets++; lit[i] = 0; scraped[i] = false; answered[i] = false; }
                                var wBefore = (int[])watchCalls.Clone(); var sBefore = (int[])scrapeCalls.Clone(); var aBefore = (int[])answerCalls.Clone();
                                book.Advance(litNow, ticks, threshold, watcher, giant, id => { watchCalls[id]++; LampWatches++; }, id => { scrapeCalls[id]++; LampScrapes++; },
                                    id => { answerCalls[id]++; if (answerOk[id]) LampAnswers++; return answerOk[id]; });
                                foreach (int i in litNow)
                                {
                                    lit[i] += ticks;
                                    float fr = lit[i] / (float)Math.Max(1, threshold);
                                    Check(book.LitTicksOf(i) == lit[i], $"lamp {i} lit {book.LitTicksOf(i)} want {lit[i]}");
                                    Check((watchCalls[i] - wBefore[i] == 1) == (watcher && fr >= 0.5f), $"lamp {i} watch at {fr:F2} watcher={watcher}");
                                    bool wantScrape = watcher && fr >= 0.75f && !scraped[i];
                                    Check(scrapeCalls[i] - sBefore[i] == (wantScrape ? 1 : 0), $"lamp {i} scrape {scrapeCalls[i] - sBefore[i]} want {(wantScrape ? 1 : 0)} at {fr:F2}");
                                    if (wantScrape) scraped[i] = true;
                                    bool wantAnswer = giant && fr >= 1f && !answered[i];
                                    Check(answerCalls[i] - aBefore[i] == (wantAnswer ? 1 : 0), $"lamp {i} answer calls {answerCalls[i] - aBefore[i]} want {(wantAnswer ? 1 : 0)} at {fr:F2}");
                                    if (wantAnswer && answerOk[i]) answered[i] = true;
                                }
                                foreach (int i in notLit) Check(book.LitTicksOf(i) == 0 && !book.Watched.Contains(i) && !book.Scraped.Contains(i) && !book.Answered.Contains(i), "a dark lamp kept its clock or latches");
                                break;
                            }
                        case 1: dark[a.a % L] = !dark[a.a % L]; break;
                        case 2: if (a.b % 2 == 0) watcher = !watcher; else giant = !giant; break;
                        case 3: answerOk[a.a % L] = !answerOk[a.a % L]; break;
                    }
                }
            }
            catch (Exception e) when (!(e is OutOfMemoryException)) { return e.Message + where; }
            return null;
        }

        private static List<string> Lamp(int n, int baseSeed) { return Family("lamp", n, baseSeed, seed => Drive(seed, GenLamp, RunLamp)); }

        // ════════════════════════ misc ════════════════════════
        public static long WaxFires, WaxWaits, VeilSheds, VeilDecks, ScarsDue;

        private static string RunMisc(int seed)
        {
            var r = new Random(seed);
            // sunk: sign and magnitude; scar latch
            float up = 0.1f + (float)r.NextDouble(), down = -(0.1f + (float)r.NextDouble());
            Check(RM_TerminalMiscKernel.SunkStep(false, up, down, 60000, 200) > 0f && RM_TerminalMiscKernel.SunkStep(true, up, down, 60000, 200) < 0f, "sunk rises unrescued and falls rescued");
            Check(Near(RM_TerminalMiscKernel.SunkStep(false, 0.7f, -1.1f, 60000, 200) * 300f, 0.7f, 1e-4f), "300 evaluations of 200 ticks are one day");
            for (int m = 0; m < 32; m++)
            {
                bool rescued = (m & 1) != 0, scar = (m & 2) != 0, applied = (m & 4) != 0; float sev = (m & 8) != 0 ? 0.05f : 0.0501f; if ((m & 16) != 0) sev = 0f;
                bool got = RM_TerminalMiscKernel.ScarDue(rescued, scar, applied, sev);
                Check(got == (rescued && scar && !applied && sev <= 0.05f), "ScarDue truth table"); if (got) ScarsDue++;
            }
            // wax: every period when still, waits while walking
            int period = 90000, ticks = -1, fires = 0, rare = 250; bool moving = false; int sinceFire = 0; int waiting = 0;
            for (int t = 0; t < 2000; t++)
            {
                Steps++;
                moving = r.Next(3) == 0;
                bool fired = RM_TerminalMiscKernel.WaxStep(ref ticks, period, rare, moving);
                sinceFire += rare;
                if (fired) { fires++; Check(!moving, "a sheet dropped while walking"); Check(ticks == period, "the timer did not re-arm"); Check(sinceFire >= period, $"a sheet dropped after {sinceFire} ticks, period {period}"); sinceFire = 0; WaxFires++; }
                else if (ticks <= 0) { Check(moving, "the timer sat at zero while the carrier was still"); waiting++; WaxWaits++; }
                Check(ticks > -rare * 10 || moving, "the timer ran away");
            }
            Check(fires >= 1, "no sheet in 2000 rare ticks");
            // veil: arm, fire, re-arm
            int ns = -1, nd = -1, now = 10000, iv = 2500; int sheds = 0, decks = 0;
            RM_TerminalMiscKernel.VeilStep(ref ns, ref nd, now, iv, n => r.Next(n), out bool s0, out bool d0);
            Check(!s0 && !d0 && ns >= now + iv && ns < now + 2 * iv && nd >= now + iv && nd < now + 2 * iv, "the veil-fall timers were not armed in [interval, 2*interval)");
            for (int t = 0; t < 400; t++)
            {
                Steps++;
                now += 2500 * (1 + r.Next(2));
                int ns0 = ns, nd0 = nd;
                RM_TerminalMiscKernel.VeilStep(ref ns, ref nd, now, iv, n => r.Next(n), out bool shed, out bool deck);
                Check(shed == (now >= ns0) && deck == (now >= nd0), "veil fired off schedule");
                Check(shed ? ns == now + iv : ns == ns0, "shed timer not re-armed one interval on"); Check(deck ? nd == now + iv : nd == nd0, "deck timer not re-armed one interval on");
                if (shed) { sheds++; VeilSheds++; } if (deck) { decks++; VeilDecks++; }
            }
            Check(sheds > 100 && decks > 100, "the veil timers rarely fired");
            return null;
        }

        private static List<string> Misc(int n, int baseSeed) { return Family("misc", n, baseSeed, RunMisc); }

        public static bool Run(double scale, int? oneSeed, string only)
        {
            var sw = Stopwatch.StartNew();
            bool ok = true;
            int N(int n) { return oneSeed.HasValue ? 1 : (int)(n * scale); }
            int S(int baseSeed) { return oneSeed ?? baseSeed; }
            var fam = new (string name, Func<List<string>> run)[]
            {
                ("wells", () => { var f = Wells(N(3000), S(1)); f.AddRange(WellProps(N(300), S(1))); return f; }),
                ("sphere", () => Sphere(N(150), S(1))),
                ("channel", () => { var f = Channel(N(3000), S(1)); f.AddRange(ChannelProps(N(500), S(1))); return f; }),
                ("crust", () => Crust(N(3000), S(1))),
                ("lamp", () => Lamp(N(3000), S(1))),
                ("misc", () => Misc(N(1000), S(1))),
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
            Console.WriteLine($"reached: wells closed {WellsClosed}, warnings {WellWarnings}, gardener closes {GardenerCloses} / advances {GardenerAdvances}, pending waited for a site {PendingWaited}, waning visuals {WaningVisuals}; sphere mature {SphereMature}, husked {SphereHusked}, seeded {SphereSeeded}, seeds consumed {SphereConsumed}");
            Console.WriteLine($"reached: channel steps {ChanSteps} ({ChanSurgeSteps} in surge), sinks {ChanSinks}, stops {ChanStops}, grabs {ChanGrabs}, harness pawns {ChanHarness}; crust doors {CrustDoors}, rimes {CrustRimes}, patches {CrustPatches}, rewinds {CrustRewinds} ({CrustFloors} at the floor)");
            Console.WriteLine($"reached: lamp watches {LampWatches}, scrapes {LampScrapes}, answers {LampAnswers}, resets {LampResets}; misc wax fires {WaxFires} / waits {WaxWaits}, veil sheds {VeilSheds} / decks {VeilDecks}, scars due {ScarsDue}");
            if (!oneSeed.HasValue && scale >= 1 && only == null)
            {
                if (WellsClosed == 0 || WellWarnings == 0 || GardenerCloses == 0 || GardenerAdvances == 0 || PendingWaited == 0 || WaningVisuals == 0 || SphereMature == 0 || SphereHusked == 0 || SphereSeeded == 0 || SphereConsumed == 0
                    || ChanSteps == 0 || ChanSurgeSteps == 0 || ChanSinks == 0 || ChanStops == 0 || ChanGrabs == 0 || ChanHarness == 0 || CrustDoors == 0 || CrustRimes == 0 || CrustPatches == 0 || CrustRewinds == 0 || CrustFloors == 0
                    || LampWatches == 0 || LampScrapes == 0 || LampAnswers == 0 || LampResets == 0 || WaxFires == 0 || WaxWaits == 0 || VeilSheds == 0 || VeilDecks == 0 || ScarsDue == 0)
                { Console.WriteLine("FAIL a fuzz family never reached one of its key transitions (blind)"); ok = false; }
            }
            Console.WriteLine($"terminalbiomes fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
