// Units for JawaBenchModHooksCore.cs, the run's watch in JawaBenchSceneTickCore.cs and the shared RMTestHooks.cs (the PRODUCTION files,
// or planted copies). One unit per promise of design/specs/2026-11-23-bridge-v2-mod-hooks/boundary.md. Prints "U <name> ok|FAIL why"
// and "U-count n". argv[0]: the folder of the fixture mods (TestHooksSelfTest/Fixtures), each built as net472 like a real mod and
// loaded by path, as the game loads a mod.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Reflection.Metadata;
using System.Reflection.PortableExecutable;
using System.Text.Json;
using C = JawaBench.BridgeTools.JawaBenchCondCore;
using MH = JawaBench.BridgeTools.JawaBenchModHooksCore;
using T = JawaBench.BridgeTools.JawaBenchSceneTickCore;

namespace JawaBench.BridgeTools
{
    internal sealed class World : ISceneHost, IProbeSource
    {
        public long TickNow = 1000, Seq;
        public readonly List<JsonElement> Out = new List<JsonElement>();
        static readonly object[] Boxes = Enumerable.Range(0, 3000).Select(i => (object)(double)i).ToArray();

        public long Enqueue(string fields) { Seq++; Out.Add(JsonDocument.Parse("{" + fields + "}").RootElement); return Seq; }
        public bool Drained() { return true; }
        public bool Pause() { return true; }
        public long Tick() { return TickNow; }
        public ulong RandState() { return 7; }
        public double NowMs() { return 0; }
        public long? AllocBytes() { return null; }
        public int CurrentMap() { return 0; }
        public bool MapSize(int m, out int x, out int z) { x = z = 250; return m == 0; }
        public string Refuse(string key, C.Probe p) { return null; }
        public CondRead Read(string key, C.Probe p, int x, int z) { return new CondRead(Boxes[TickNow % 3000], "ok", ""); }
        public List<JsonElement> Rec(string rec) { return Out.Where(o => o.GetProperty("rec").GetString() == rec).ToList(); }
    }

    internal static class Program
    {
        static int _n, _bad;
        static string _dir;
        static readonly Dictionary<string, Assembly> Loaded = new Dictionary<string, Assembly>();

        static void Check(string name, Action f)
        {
            _n++;
            string w = null;
            try { f(); } catch (Exception e) { w = e.GetType().Name + ": " + e.Message; }
            if (w != null) _bad++;
            Console.WriteLine("U " + name + " " + (w == null ? "ok" : "FAIL " + w.Replace('\n', ' ')));
        }

        static void Eq(object a, object b, string what) { if (!Equals(a, b)) throw new Exception(what + ": got " + a + ", want " + b); }
        static void True(bool c, string what) { if (!c) throw new Exception(what); }

        static string Dll(string kind) { return Path.Combine(_dir, kind, "bin", "Release", "net472", "RimMandrake.HookFixture" + kind + ".dll"); }

        static Assembly Fix(string kind)
        {
            Assembly a;
            if (!Loaded.TryGetValue(kind, out a)) Loaded[kind] = a = Assembly.LoadFrom(Dll(kind));
            return a;
        }

        static MH.Registry Reg(params string[] kinds) { var asms = kinds.Select(Fix).ToList(); return new MH.Registry(() => asms); }
        static MH.Mod ModOf(MH.Registry r, string kind) { var m = r.Find("RimMandrake.HookFixture" + kind); if (m == null) throw new Exception("not listed: " + kind); return m; }

        static Type StateOf(string kind) { return Fix(kind).GetType("RimMandrake.HookFixture.State", true); }
        static void Call(string kind, string method) { StateOf(kind).GetMethod(method).Invoke(null, null); }
        static void Clear(string kind) { var s = StateOf(kind); ((System.Collections.IList)s.GetField("Pending").GetValue(null)).Clear(); s.GetField("Counter").SetValue(null, 0); }
        static object SinkOf(string kind) { return Fix(kind).GetType(MH.TraceType, true).GetField("Sink", BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic).GetValue(null); }

        static T.SceneRun Run(World w)
        {
            var spec = C.ParseJson("{\"until\":{\"cmp\":[{\"p\":\"game.tick\"},\">=\",2900]},\"max_ticks\":1500}");
            var c = new C.Compiler(w, "run").CompileSpec(spec);
            return new T.SceneRun("r1", c, w, new List<T.Act>(), w, "PLAY", "Ultrafast");
        }

        static int Main(string[] args)
        {
            _dir = args[0];

            Check("a_mod_with_no_hook_is_listed_as_such", () =>
            {
                var r = new MH.Registry(() => new[] { Fix("None"), Fix("A"), typeof(Enumerable).Assembly, typeof(Program).Assembly });
                Eq(string.Join(",", r.Mods.Select(m => m.Name)), "RimMandrake.HookFixtureA,RimMandrake.HookFixtureNone", "listed (System.Linq and the harness are not ours)");
                var row = ModOf(r, "None").Row();
                Eq(row["build"], "none", "build");
                Eq(row["trace"], "no trace point", "trace");
                Eq(row["reset"], "no reset hook", "reset");
                Eq(row["digest"], "no digest hook", "digest");
                Eq(((List<object>)row["problems"]).Count, 0, "problems of a mod with no hook");
                Eq(ModOf(r, "A").Row()["reset"], "RimMandrake.HookFixture.Hooks.Reset", "A's reset is found beside it");
            });

            Check("a_hook_of_the_wrong_shape_is_a_named_problem", () =>
            {
                var m = ModOf(Reg("Wrong"), "Wrong");
                Eq(m.Reset, null, "a wrong reset hook is not used");
                Eq(m.Digest, null, "a wrong digest hook is not used");
                string all = string.Join(" | ", m.Problems);
                True(m.Problems.Count == 3, "three problems, got " + m.Problems.Count + ": " + all);
                True(all.Contains("RMReset on RimMandrake.HookFixture.Hooks.Reset") && all.Contains("is not static"), "the instance reset is named: " + all);
                True(all.Contains("RMDigest on RimMandrake.HookFixture.Hooks.Digest") && all.Contains("takes (Int32)"), "the int digest is named: " + all);
                True(all.Contains("RMReset on RimMandrake.HookFixture.MoreHooks.ResetVoid") && all.Contains("returns Void"), "the void reset is named: " + all);
                Eq(ModOf(Reg("A"), "A").Problems.Count, 0, "a hook of the right shape is no problem");
            });

            Check("emit_with_a_null_sink_allocates_nothing", () =>
            {
                var tr = Fix("A").GetType(MH.TraceType, true);
                var sink = tr.GetField("Sink", BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic);
                sink.SetValue(null, null);
                MethodInfo M(params Type[] ps) { return tr.GetMethod("Emit", BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic, null, ps, null); }
                var e0 = (Action<string>)Delegate.CreateDelegate(typeof(Action<string>), M(typeof(string)));
                var es = (Action<string, string, string>)Delegate.CreateDelegate(typeof(Action<string, string, string>), M(typeof(string), typeof(string), typeof(string)));
                var el = (Action<string, string, long>)Delegate.CreateDelegate(typeof(Action<string, string, long>), M(typeof(string), typeof(string), typeof(long)));
                var ed = (Action<string, string, double>)Delegate.CreateDelegate(typeof(Action<string, string, double>), M(typeof(string), typeof(string), typeof(double)));
                var eb = (Action<string, string, bool>)Delegate.CreateDelegate(typeof(Action<string, string, bool>), M(typeof(string), typeof(string), typeof(bool)));
                long Measure()
                {
                    long b0 = GC.GetAllocatedBytesForCurrentThread();
                    for (int i = 0; i < 20000; i++) { e0("n"); es("n", "k", "v"); el("n", "k", i); ed("n", "k", i * 0.5); eb("n", "k", true); }
                    return GC.GetAllocatedBytesForCurrentThread() - b0;
                }
                Measure();                                                   // JIT first
                Eq(Measure(), 0L, "bytes allocated by 100000 Emit calls with a null sink");
                sink.SetValue(null, (Action<string, string, string>)((n, k, v) => { }));
                long armed = Measure();
                sink.SetValue(null, null);
                True(armed > 0, "the instrument sees: with a sink set, the same calls allocate (" + armed + " bytes)");
            });

            Check("the_sink_is_cleared_at_the_end_also_after_a_thrown_tick", () =>
            {
                try
                {
                    foreach (var end in new[] { "threw", "cancelled", "aborted" })
                    {
                        var reg = Reg("A", "B");
                        T.Watch = reg;
                        var w = new World();
                        var run = Run(w);
                        run.Arm(w.TickNow, 1.0);
                        True(SinkOf("A") != null && SinkOf("B") != null, end + ": both sinks are set at the arm");
                        var held = (Action<string, string, string>)SinkOf("A");
                        w.TickNow++;
                        Call("A", "Work");
                        Eq(w.Rec("mod").Count, 5, end + ": the mod records of one Work");
                        var first = w.Rec("mod")[1];
                        Eq(first.GetProperty("mod").GetString() + " " + first.GetProperty("name").GetString() + " " + first.GetProperty("key").GetString() + "=" +
                           first.GetProperty("v").GetString() + " " + first.GetProperty("phase").GetString() + " " + first.GetProperty("tick").GetInt64(),
                           "RimMandrake.HookFixtureA worked counter=0 in_tick 1001", end + ": a mod record");
                        run.Force(end, "the planted end", w.TickNow);
                        Eq(SinkOf("A"), null, end + ": A's sink after the end");
                        Eq(SinkOf("B"), null, end + ": B's sink after the end");
                        Eq(reg.Armed, 0, end + ": sinks the registry holds after the end");
                        Call("A", "Work");
                        held("late", null, null);                            // a mod that kept the delegate it was given
                        Eq(w.Rec("mod").Count, 5, end + ": no mod record after the end");
                        Eq(reg.Late, 1L, end + ": the kept delegate's call is counted late, not written");
                    }
                }
                finally { T.Watch = null; }
            });

            Check("two_mods_hooks_do_not_collide", () =>
            {
                Clear("A"); Clear("B");
                var reg = Reg("A", "B");
                Eq(reg.Mods.Count, 2, "two mods with the same type names are two entries");
                var said = new List<string>();
                reg.Arm((mod, n, k, v) => { if (k == null) said.Add(mod); });
                Call("A", "Work"); Call("B", "Work"); Call("B", "Work");
                reg.Leave();
                Eq(string.Join(",", said), "RimMandrake.HookFixtureA,RimMandrake.HookFixtureB,RimMandrake.HookFixtureB", "each record carries its own mod");
                Call("B", "Poke");
                reg.Prove("RimMandrake.HookFixtureA", "clean", "");
                Call("A", "Poke");
                Eq(reg.Prove("RimMandrake.HookFixtureA", "dirty", "")["digestProven"], true, "A's proof");
                Eq(ModOf(reg, "B").Proven, false, "B is not proven by A's proof");
                reg.Reset("RimMandrake.HookFixtureA", "");
                Eq(StateOf("B").GetField("Counter").GetValue(null), 1, "A's reset leaves B's state");
                Eq(StateOf("A").GetField("Counter").GetValue(null), 0, "A's reset clears A's state");
                Clear("B");
            });

            Check("a_proof_build_hook_is_refused_for_an_acceptance_run", () =>
            {
                var reg = Reg("A", "Proof", "None");
                Eq(ModOf(reg, "Proof").Build, "PROOF", "the PROOF build says so");
                Eq(ModOf(reg, "A").Build, "RELEASE", "the RELEASE build says so");
                var no = reg.Admit("acceptance");
                Eq(no.Count, 1, "refusals for acceptance: " + string.Join(" | ", no));
                True(no[0].StartsWith("PROOF_BUILD: RimMandrake.HookFixtureProof "), "the refusal names the PROOF build: " + no[0]);
                Eq(reg.Admit("explore").Count, 0, "an exploring run is admitted");
            });

            Check("a_release_dll_with_hooks_names_no_companion_type", () =>
            {
                var companion = new[] { "JawaBench", "RimBridgeServer", typeof(Program).Assembly.GetName().Name };
                List<string> Names(string kind)
                {
                    var hits = new List<string>();
                    using (var pe = new PEReader(File.OpenRead(Dll(kind))))
                    {
                        var md = pe.GetMetadataReader();
                        foreach (var h in md.AssemblyReferences)
                        {
                            string n = md.GetString(md.GetAssemblyReference(h).Name);
                            if (companion.Any(c => n.StartsWith(c, StringComparison.Ordinal))) hits.Add("assembly " + n);
                        }
                        foreach (var h in md.TypeReferences)
                        {
                            string ns = md.GetString(md.GetTypeReference(h).Namespace);
                            if (companion.Any(c => ns.StartsWith(c, StringComparison.Ordinal))) hits.Add("type " + ns + "." + md.GetString(md.GetTypeReference(h).Name));
                        }
                    }
                    return hits;
                }
                Eq(ModOf(Reg("A"), "A").Build, "RELEASE", "A is a release DLL");
                True(ModOf(Reg("A"), "A").HasHooks, "A has hooks");
                var a = Names("A");
                Eq(a.Count, 0, "names of the companion in A: " + string.Join(", ", a));
                var leak = Names("Leak");
                True(leak.Any(x => x == "type JawaBench.BridgeTools.FakeCompanionType"), "the instrument sees: the Leak build names the companion's type (" + string.Join(", ", leak) + ")");
            });

            Check("a_digest_is_accepted_only_after_it_was_seen_to_differ", () =>
            {
                Clear("A"); Clear("Const");
                var reg = Reg("A", "Const");
                string A = "RimMandrake.HookFixtureA", K = "RimMandrake.HookFixtureConst";
                Eq(reg.Prove(A, "dirty", "")["refused"], "NO_CLEAN_READ", "dirty before clean");
                Call("A", "Poke");
                True(((string)reg.Reset(A, "")["reset"]).StartsWith("unproven"), "a reset before the proof is unproven");
                reg.Prove(A, "clean", "");
                Call("A", "Poke"); Call("A", "Poke");
                var p = reg.Prove(A, "dirty", "");
                Eq(p["digestProven"], true, "A's digest differs between clean and dirtied: " + p["digestProof"]);
                Eq(reg.Reset(A, "")["reset"], "verified", "A's reset brings the clean digest back");
                Call("A", "Poke");
                Eq(reg.Prove(A, "clean", "")["digestProven"], false, "a new clean read drops the old proof");
                reg.Prove(K, "clean", "");
                Call("Const", "Poke");
                var q = reg.Prove(K, "dirty", "");
                Eq(q["digestProven"], false, "the constant digest is refused");
                True(((string)q["digestProof"]).Contains("did not change when the state was dirtied"), "and says why: " + q["digestProof"]);
                True(((string)reg.Reset(K, "")["reset"]).StartsWith("unproven"), "the constant digest never verifies a reset");
                Clear("A"); Clear("Const");
            });

            Console.WriteLine("U-count " + _n);
            return _bad == 0 ? 0 : 1;
        }
    }
}
