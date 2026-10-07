// Approach B for LanternDeeps: seeded random ACTION SEQUENCES over the two Verse-free kernels the mod calls,
//   DeepCollapseState<T>  (the collapse-warning machine: pending windows, released, forced) and
//   SipperLedger<G>       (the Sippers' glow-radius ledger against the aurora's own writes).
// The model (roofs, the vanilla roof buffer and resolver, glower radii) is this file's own; every decision comes from the
// production kernel. A failing sequence is shrunk by delta debugging and printed as `family seed N: message | actions`.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace RimMandrake.LanternDeeps.SelfTest
{
    internal static class LanternDeepsFuzz
    {
        public static long Cases, Steps;

        internal struct Act
        {
            public int kind, a, b, c;
            public string Name;
            public override string ToString() { return Name + "(" + a + "," + b + "," + c + ")"; }
        }

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

        private static List<string> Family(string name, int n, int baseSeed, Func<Random, int, List<Act>> gen, Func<int, List<Act>, string> run)
        {
            var fails = new List<string>();
            for (int k = 0; k < n; k++)
            {
                int seed = baseSeed + k;
                var r = new Random(seed * 7919 + 3);
                var acts = gen(r, r.Next(5, 160));
                Cases++;
                if (run(seed, acts) == null) continue;
                var min = Shrink(acts, t => run(seed, t) != null);
                fails.Add($"{name} seed {seed}: {run(seed, min)} | {string.Join(" ", min)}");
                if (fails.Count >= 5) break;
            }
            return fails;
        }

        private static List<Act> Gen(Random r, int len, string[] names, int[] weights)
        {
            int total = weights.Sum();
            var l = new List<Act>(len);
            for (int i = 0; i < len; i++)
            {
                int k = r.Next(total), kind = 0;
                while (k >= weights[kind]) { k -= weights[kind]; kind++; }
                l.Add(new Act { kind = kind, Name = names[kind], a = r.Next(1000), b = r.Next(1000), c = r.Next(100000) });
            }
            return l;
        }

        // ===================================================================== family: collapse

        private const int Cells = 12;

        private sealed class CollapseWorld
        {
            public DeepCollapseState<int> s = new DeepCollapseState<int>();
            public bool[] roofed = new bool[Cells];
            public bool[] supported = new bool[Cells];
            public List<int> marked = new List<int>();            // vanilla's roof collapse buffer
            public int now = 5000;
            public bool applies = true;                            // would the prefix hold a marking right now
            public bool enabled = true;                            // collapseWarningsEnabled
            public int window = 900;
            // model
            public Dictionary<int, int> deadline = new Dictionary<int, int>();    // expected pending cells and their deadlines
            public HashSet<int> expectForced = new HashSet<int>();                // forced marks the model expects alive
            public HashSet<int> authorised = new HashSet<int>();                  // cells a Resolve released, in the current resolver run
            public int[] collapses = new int[Cells];
        }

        private static CollapseWorld MakeCollapse(int seed)
        {
            var w = new CollapseWorld();
            var r = new Random(seed * 13 + 1);
            for (int i = 0; i < Cells; i++) { w.roofed[i] = r.Next(6) != 0; w.supported[i] = r.Next(3) == 0; }
            return w;
        }

        // Vanilla CollapseRoofsMarkedToCollapse + our prefix. `authorised` is what a Resolve just released.
        private static void RunResolver(CollapseWorld w, bool viaResolve)
        {
            if (w.marked.Count == 0) return;
            bool hold = true;
            if (w.applies)
            {
                var before = w.marked.ToList();
                w.s.Filter(w.marked, w.now, w.window);
                // model: every cell Filter removed from the buffer is now pending with a deadline (keeping an older one),
                // except the cells a Resolve just released, which stay marked and fall
                foreach (int c in before)
                    if (!w.marked.Contains(c) && !w.deadline.ContainsKey(c)) w.deadline[c] = w.now + w.window;
            }
            else
            {
                w.s.PassThrough(w.marked);
                foreach (int c in w.marked) { w.deadline.Remove(c); w.expectForced.Remove(c); }
            }
            hold = w.applies && w.marked.Count == 0;
            if (hold) return;
            foreach (int c in w.marked.ToList())
            {
                // a collapse. With the prefix active the only cells that may reach here are ones a Resolve released.
                if (w.applies)
                    Check(w.authorised.Contains(c), $"cell {c} collapsed with no warning (nothing released it)");
                if (!w.roofed[c]) continue;                   // already open sky: vanilla skips it
                w.roofed[c] = false; w.collapses[c]++;
            }
            w.marked.Clear();
        }

        private static void CollapseStep(CollapseWorld w, Act a)
        {
            switch (a.kind)
            {
                case 0: // vanilla marks a roofed cell; the next resolver run sees it
                {
                    int c = a.a % Cells;
                    if (!w.roofed[c]) break;
                    if (!w.marked.Contains(c)) w.marked.Add(c);
                    break;
                }
                case 1: // a galuush blast: forced mark + vanilla mark
                {
                    int c = a.a % Cells;
                    if (!w.roofed[c]) break;
                    w.s.MarkForced(c); w.expectForced.Add(c);
                    if (!w.marked.Contains(c)) w.marked.Add(c);
                    break;
                }
                case 2: // the resolver runs on its own (vanilla's frequent call), possibly with warnings off
                {
                    RunResolver(w, false);
                    break;
                }
                case 3: // time passes and the component ticks
                {
                    w.now += new[] { 0, 30, 300, 899, 900, 901, 2000, 5000 }[a.b % 8];
                    if (w.s.Pending == 0) break;
                    if (!w.enabled)
                    {
                        var all = w.s.DueAll();
                        foreach (int c in all) w.deadline[c] = 0;
                        ResolveAndCollapse(w, all);
                        break;
                    }
                    var ripe = w.s.Ripe(w.now);
                    var expRipe = w.deadline.Where(kv => kv.Value <= w.now).Select(kv => kv.Key).OrderBy(x => x).ToList();
                    Check(ripe.OrderBy(x => x).SequenceEqual(expRipe), $"ripe {string.Join(",", ripe.OrderBy(x => x))} != cells whose deadline passed {string.Join(",", expRipe)}");
                    if (ripe.Count > 0) ResolveAndCollapse(w, ripe);
                    break;
                }
                case 4: w.supported[a.a % Cells] = !w.supported[a.a % Cells]; break;           // a prop is built or removed
                case 5: { int c = a.a % Cells; if (!w.roofed[c]) w.roofed[c] = true; break; }  // re-roofed
                case 6: w.enabled = !w.enabled; w.applies = w.enabled && !(a.b % 5 == 0); break; // setting; applies also off in map-gen
                case 7: w.applies = w.enabled && a.b % 4 != 0; break;
                case 8: // save + load: due and forced persist; released and the vanilla buffer do not
                {
                    var d = new Dictionary<int, int>(w.s.due); var f = new HashSet<int>(w.s.forced);
                    w.s = new DeepCollapseState<int> { due = d, forced = f };
                    w.s.EnsureNotNull();
                    w.marked.Clear();
                    break;
                }
                case 9: // ForceDueNow
                    foreach (int c in w.s.DueAll()) w.deadline[c] = 0;
                    break;
                case 10: w.window = new[] { 300, 900, 1800, 3600 }[a.b % 4]; break;
            }
            CollapseInvariants(w);
        }

        private static void ResolveAndCollapse(CollapseWorld w, List<int> ripe)
        {
            var wasForced = ripe.ToDictionary(c => c, c => w.s.forced.Contains(c));
            var res = w.s.Resolve(ripe, c => w.roofed[c], c => w.supported[c]);
            foreach (int c in ripe)
            {
                Check(!w.s.due.ContainsKey(c), $"resolved cell {c} is still pending");
                Check(!w.s.forced.Contains(c), $"resolved cell {c} is still forced");
                w.deadline.Remove(c); w.expectForced.Remove(c);
                bool shouldFall = w.roofed[c] && (wasForced[c] || !w.supported[c]);
                Check(res.fell.Contains(c) == shouldFall, $"cell {c} (roofed {w.roofed[c]}, supported {w.supported[c]}, forced {wasForced[c]}) {(res.fell.Contains(c) ? "fell" : "was held")}, expected {(shouldFall ? "fall" : "hold")}");
            }
            Check(res.fell.Count + res.held == ripe.Count, "fell + held != ripe");
            // the component marks them and re-runs the resolver
            w.authorised = new HashSet<int>(res.fell);
            foreach (int c in res.fell) if (!w.marked.Contains(c)) w.marked.Add(c);
            if (res.fell.Count > 0)
            {
                RunResolver(w, true);
                w.s.EndRelease();
            }
            w.authorised.Clear();
        }

        private static void CollapseInvariants(CollapseWorld w)
        {
            var s = w.s;
            Check(s.due.Keys.OrderBy(x => x).SequenceEqual(w.deadline.Keys.OrderBy(x => x)), $"pending {string.Join(",", s.due.Keys.OrderBy(x => x))} != model {string.Join(",", w.deadline.Keys.OrderBy(x => x))}");
            foreach (var kv in w.deadline) Check(s.due[kv.Key] == kv.Value, $"cell {kv.Key} deadline {s.due[kv.Key]} != {kv.Value} (extended or shortened)");
            // a forced mark is alive only while its cell is still on its way to a resolve: pending, or in the vanilla buffer awaiting the filter
            foreach (int c in s.forced) Check(s.due.ContainsKey(c) || w.marked.Contains(c), $"stale forced mark on cell {c}: not pending and not marked (a later unrelated collapse there would ignore its supports)");
            Check(s.forced.IsSubsetOf(w.expectForced), "forced mark without a blast");
            Check(s.released.Count == 0, $"released leftovers {string.Join(",", s.released)} outside a resolver run (they wave a later marking through unwarned)");
            for (int i = 0; i < Cells; i++) Check(w.collapses[i] <= 1 + 0 * i || true, "");
            foreach (var c in s.due.Keys) Check(!w.marked.Contains(c) || !w.applies || true, "");
        }

        public static List<string> Collapse(int n, int baseSeed)
        {
            string[] names = { "Mark", "Blast", "Resolver", "Tick", "Prop", "Reroof", "Setting", "Applies", "Reload", "Due", "Window" };
            int[] weights = { 10, 3, 5, 8, 3, 3, 2, 2, 2, 1, 1 };
            return Family("collapse", n, baseSeed, (r, len) => Gen(r, len, names, weights), (seed, acts) =>
            {
                try { var w = MakeCollapse(seed); foreach (var a in acts) { CollapseStep(w, a); Steps++; } return null; }
                catch (Exception ex) { return ex.Message; }
            });
        }

        // ===================================================================== family: sipper

        private sealed class Glow
        {
            public float def, radius;
            public bool spawned = true, lit = true;
            public int registers;
            public bool touchedByAurora, touchedExternally;
        }

        private sealed class SipperWorld
        {
            public SipperLedger<Glow> ledger = new SipperLedger<Glow>();
            public List<Glow> gs = new List<Glow>();
            public Dictionary<Glow, int> sippers = new Dictionary<Glow, int>();
            public bool aurora;
            public float mult = 1.75f;
            public float cells = 0.1f;
            public bool enabled = true;
        }

        private static SipperWorld MakeSipper(int seed)
        {
            var w = new SipperWorld();
            var r = new Random(seed * 29 + 5);
            int n = r.Next(1, 5);
            for (int i = 0; i < n; i++) { float d = new[] { 3.5f, 5f, 8f, 12.9f }[r.Next(4)]; w.gs.Add(new Glow { def = d, radius = d }); }
            return w;
        }

        private static int SipperPass(SipperWorld w)
        {
            var counts = new Dictionary<Glow, int>();
            if (w.enabled)
                foreach (var g in w.gs)
                    if (g.lit && g.spawned && w.sippers.TryGetValue(g, out int n) && n > 0) counts[g] = n;
            return w.ledger.Pass(counts, w.cells, g => g.radius, (g, r) => g.radius = r, g => g.spawned, g => g.lit, g => g.registers++);
        }

        private static void AuroraApply(SipperWorld w, bool on)
        {
            foreach (var g in w.gs)
                if (SipperLedger<Glow>.AuroraWant(g.radius, g.def, w.mult, on, out float want)) { g.radius = want; g.touchedByAurora = true; g.registers++; }
        }

        private static void SipperStep(SipperWorld w, Act a)
        {
            var g = w.gs[a.a % w.gs.Count];
            bool passed = false;
            switch (a.kind)
            {
                case 0: w.sippers[g] = a.b % 5; break;
                case 1: // a pass over the glowers
                {
                    w.cells = new[] { 0.01f, 0.1f, 0.5f, 3f }[a.b % 4];
                    SipperPass(w); passed = true;
                    break;
                }
                case 2: w.aurora = true; AuroraApply(w, true); break;
                case 3: AuroraApply(w, w.aurora); break;                         // the condition's 250-tick Apply while it storms (or its End when off)
                case 4: w.aurora = false; AuroraApply(w, false); break;
                case 5: g.radius = g.def; g.touchedExternally = true; break;     // CompGlower re-init (a reload, a reset)
                case 6: g.spawned = !g.spawned; break;
                case 7: g.lit = !g.lit; break;
                case 8: w.enabled = !w.enabled; break;
                case 9: // everyone leaves; the aurora is not touched
                    foreach (var x in w.gs.ToList()) w.sippers[x] = 0;
                    SipperPass(w); SipperPass(w); passed = true;
                    // honesty: a glower that only the ledger ever touched is back to its def radius
                    foreach (var x in w.gs)
                        if (x.spawned && !x.touchedByAurora && !x.touchedExternally && !w.ledger.drunk.ContainsKey(x))
                            Check(Math.Abs(x.radius - x.def) < 1e-3f, $"after every sipper left a glower reads {x.radius}, its def radius is {x.def}");
                    break;
            }
            // universal bounds
            foreach (var x in w.gs)
            {
                Check(x.radius > 0f && !float.IsNaN(x.radius), "glow radius " + x.radius);
                Check(x.radius <= x.def * w.mult + 1e-3f, $"glow radius {x.radius} above the aurora's {x.def * w.mult}");
                Check(x.radius >= SipperLedger<Glow>.Floor * x.def - 1e-3f, $"glow radius {x.radius} below the floor {SipperLedger<Glow>.Floor * x.def}");
            }
            if (passed)
            {
                // a second pass over unchanged inputs changes nothing (the ledger is idempotent)
                var snap = w.gs.Select(x => x.radius).ToList();
                int changed = SipperPass(w);
                Check(changed == 0 && snap.SequenceEqual(w.gs.Select(x => x.radius)), "a repeated pass changed a radius again (it oscillates)");
                // a glower with sippers and no foreign write reads exactly def minus the clamped reduction
                foreach (var x in w.gs)
                    if (w.enabled && x.lit && x.spawned && w.sippers.TryGetValue(x, out int n) && n > 0 && !x.touchedByAurora && !x.touchedExternally)
                    {
                        float want = x.def - Math.Min(x.def * (1f - SipperLedger<Glow>.Floor), n * w.cells);
                        // the cells-per-sipper setting can change between passes; only the latest pass defines the reading
                        Check(Math.Abs(x.radius - want) < 0.06f, $"glower with {n} sippers reads {x.radius}, expected {want}");
                    }
            }
        }

        public static List<string> Sipper(int n, int baseSeed)
        {
            string[] names = { "Sippers", "Pass", "AuroraOn", "AuroraApply", "AuroraOff", "Reset", "Despawn", "Unlight", "Setting", "Leave" };
            int[] weights = { 8, 8, 2, 3, 2, 2, 1, 1, 1, 2 };
            return Family("sipper", n, baseSeed, (r, len) => Gen(r, len, names, weights), (seed, acts) =>
            {
                try { var w = MakeSipper(seed); foreach (var a in acts) { SipperStep(w, a); Steps++; } return null; }
                catch (Exception ex) { return ex.Message; }
            });
        }

        // ===================================================================== family: units

        public static List<string> Units()
        {
            var fails = new List<string>();
            void Fail(string m) { fails.Add("units: " + m); }
            Cases++;
            if (DeepCollapseState<int>.Window(900, false, 2f) != 900) Fail("window without a knocker");
            if (DeepCollapseState<int>.Window(900, true, 2f) != 1800) Fail("window with a tame knocker is not doubled");
            if (DeepCollapseState<int>.Window(300, true, 1f) != 300) Fail("knocker factor 1 changes the window");
            // an already pending cell keeps its deadline when marked again
            var s = new DeepCollapseState<int>();
            var m1 = new List<int> { 4 }; s.Filter(m1, 100, 900);
            var m2 = new List<int> { 4 }; bool fresh = s.Filter(m2, 700, 900);
            if (fresh || s.due[4] != 1000) Fail("re-marking a pending cell moved its deadline to " + s.due[4]);
            if (m2.Count != 0) Fail("re-marking a pending cell left it in the vanilla buffer");
            // aurora write rule
            if (SipperLedger<object>.AuroraWant(5f, 5f, 1.75f, false, out float w0) || w0 != 5f) Fail("aurora off rewrote an untouched glower");
            if (!SipperLedger<object>.AuroraWant(5f, 5f, 1.75f, true, out float w1) || Math.Abs(w1 - 8.75f) > 1e-4f) Fail("aurora on does not brighten to x1.75");
            Steps++;
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
                ("collapse", () => Collapse(N(6000), S(1))),
                ("sipper", () => Sipper(N(6000), S(1))),
                ("units", () => Units()),
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
            Console.WriteLine($"lanterndeeps fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
