// Units for JawaBenchPathCore.cs and JawaBenchHandsCore.cs (the PRODUCTION files), with the run of JawaBenchSceneTickCore.cs.
// One unit per promise of design/specs/2026-11-23-bridge-v2-hands/boundary.md. Prints "U <name> ok|FAIL why" and "U-count n".
// The game is played by World.Play as TickManager.TickManagerUpdate does; each call of a hand is one main-thread hop, and a hop
// moves the frame count (World.Hop). Things are C# objects of this file, read by the production path evaluator.
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using System.Threading.Tasks;
using C = JawaBench.BridgeTools.JawaBenchCondCore;
using H = JawaBench.BridgeTools.JawaBenchHandsCore;
using P = JawaBench.BridgeTools.JawaBenchPathCore;
using T = JawaBench.BridgeTools.JawaBenchSceneTickCore;

namespace JawaBench.BridgeTools
{
    internal struct Cell3 { public int x, z; public Cell3(int a, int b) { x = a; z = b; } }
    internal sealed class HeldComp { private bool held; private int heldTicks; public void Set(bool h, int t) { held = h; heldTicks = t; } public string Sum() { return held + "/" + heldTicks; } }
    internal enum Mood { Calm, Angry }
    internal class Creature
    {
        private Cell3 positionInt;
        internal int hp = 100;
        private float curLevelInt = 0.5f;
        public Cell3 Position { get { return positionInt; } set { positionInt = value; } }
        public static int Touched;
        public string Label { get { Touched++; hp--; return "label"; } }           // a property with an effect: never read
        public string Auto { get; set; } = "auto";
        public virtual int Virt { get { return hp; } }
        public int Compute() { Touched++; return 1; }
        public Creature Rider;
        public List<int> Wounds = new List<int> { 3, 4 };
        public Mood mood = Mood.Angry;
        public string jobDef;
        public HeldComp Held = new HeldComp();
        public bool Gone;
        public string Digest() { return positionInt.x + "," + positionInt.z + "," + hp + "," + curLevelInt + "," + Held.Sum() + "," + string.Join(";", Wounds) + "," + Touched + "," + Gone; }
    }
    internal sealed class Beast : Creature { public override int Virt { get { Touched++; return hp * 2; } } }
    internal static class ModStatics { private static int secretCount = 7; public static void Bump() { secretCount++; } }

    internal sealed class World : IHandsHost, IProbeSource, IPathHost
    {
        public long TickNow = 1000, Seq;
        public bool PausedNow = true, RefusePause;
        public ulong Rand = 7;
        public double Clock;
        public long Queue;
        public int FrameNow = 50, Goes, FrameAtGo = -1;
        public readonly Dictionary<string, Creature> Things = new Dictionary<string, Creature>();
        public readonly Dictionary<string, Creature[]> Bound = new Dictionary<string, Creature[]>();
        public readonly List<(long seq, JsonElement r)> Out = new List<(long, JsonElement)>();
        public readonly List<string> Done = new List<string>();
        public string RefuseRunWhy;
        public H.Hands Hands;

        public World() { Hands = new H.Hands(this); }
        public Creature Add(string id, int x = 5, int z = 5) { var c = new Creature { Position = new Cell3(x, z) }; Things[id] = c; return c; }

        // ---- ISceneHost
        public long Enqueue(string fields)
        {
            Seq++; Queue++;
            Out.Add((Seq, JsonDocument.Parse("{" + fields + "}").RootElement));
            return Seq;
        }
        public bool Drained() { return Queue == 0; }
        public bool Pause() { if (RefusePause) return false; PausedNow = true; return true; }
        public long Tick() { return TickNow; }
        public ulong RandState() { return Rand; }
        public double NowMs() { return Clock; }
        public long? AllocBytes() { return null; }

        // ---- IHandsHost
        public int Frame() { return FrameNow; }
        public bool Paused() { return PausedNow; }
        public string RefuseAct(string tool, Dictionary<string, object> args) { return tool.StartsWith("jawa/") ? null : "UNKNOWN_TOOL: " + tool; }
        public string RefuseRun() { return RefuseRunWhy; }
        public bool Bind(string alias, int member, string id)
        {
            if (!Things.ContainsKey(id)) return false;
            if (alias == null) return true;
            Creature[] a;
            Bound.TryGetValue(alias, out a);
            int n = Math.Max(member, 0);
            if (a == null || a.Length <= n) { Array.Resize(ref a, n + 1); Bound[alias] = a; }
            a[n] = Things[id];
            return true;
        }
        public void Unbind(string alias) { Bound.Remove(alias); }
        public ActOutcome Act(string tool, Dictionary<string, object> args)
        {
            Done.Add(tool);
            if (tool == "jawa/throw") throw new InvalidOperationException("no target");
            if (tool == "jawa/no") return new ActOutcome { State = "refused", Error = "said no", Reply = new Dictionary<string, object> { { "success", false } } };
            if (tool == "jawa/hit") Things[(string)args["id"]].hp -= (int)C.Num(args["by"]);
            return new ActOutcome { State = "done", Reply = new Dictionary<string, object> { { "n", (double)Done.Count } } };
        }

        // ---- IPathHost
        public bool Root(string of, out object root, out Type staticOf, out PathValue bad)
        {
            root = null; staticOf = null; bad = default(PathValue);
            if (of.StartsWith("static:")) { staticOf = Type.GetType("JawaBench.BridgeTools." + of.Substring(7)); if (staticOf != null) return true; bad = PathValue.Bad("error", "no type"); return false; }
            int i = of.IndexOf('[');
            string alias = i < 0 ? of : of.Substring(0, i);
            int n = i < 0 ? 0 : int.Parse(of.Substring(i + 1).TrimEnd(']'));
            Creature[] a;
            if (!Bound.TryGetValue(alias, out a) || n >= a.Length || a[n] == null) { bad = PathValue.Bad("unbound", of + " is bound to nothing"); return false; }
            if (a[n].Gone) { bad = PathValue.Bad("gone", "dead"); return false; }
            root = a[n];
            return true;
        }
        public object Comp(object owner, string cls, out string why)
        {
            why = null;
            var c = owner as Creature;
            if (c != null && cls == "HeldComp") return c.Held;
            why = "no comp " + cls;
            return null;
        }
        public object Leaf(object v, out bool known)
        {
            known = v is Cell3;
            return known ? ((Cell3)v).x + "," + ((Cell3)v).z : null;
        }
        public int CellIndex(int x, int z, int length, out string why) { why = null; return z * 10 + x; }

        // ---- IProbeSource (as VerseProbeSource does it)
        public int CurrentMap() { return 0; }
        public bool MapSize(int m, out int x, out int z) { x = z = 250; return m == 0; }
        public string Refuse(string key, C.Probe p)
        {
            if (p.Name != "value" && p.Name != "value.state") return null;
            var r = P.Read(this, (string)p.Args["of"], (string)p.Args["path"]);
            return r.Refused == null ? null : r.Detail;
        }
        public CondRead Read(string key, C.Probe p, int x, int z)
        {
            if (p.Name == "game.tick") return new CondRead((double)TickNow, "ok", "");
            var r = P.Read(this, (string)p.Args["of"], (string)p.Args["path"]);
            if (p.Name == "value.state") return new CondRead(P.StateOf(r), "ok", "");
            return r.Refused != null ? new CondRead(null, "error", r.Detail) : new CondRead(r.V, r.State, r.Detail);
        }

        // ---- a call from outside: one hop, and at least one frame between two hops
        public Task<object> Hop(Func<object> body) { FrameNow++; return Task.FromResult(body()); }

        public Dictionary<string, object> Run(string driver, string request, string until, int limit = 500, string record = null, string acts = null, string canon = null)
        {
            var l = H.ParseActs(acts, true);
            return (Dictionary<string, object>)Hop(() =>
            {
                try
                {
                    return Hands.StartRun(driver, request, canon ?? until + "|" + limit + "|" + record + "|" + acts, l, limit, (id, ticks, trace) =>
                    {
                        var plan = H.MakePlan(until, record, limit, -1, Hands.GroupSize);
                        return new T.SceneRun(id, plan.Compile(this), this, ticks, this, "PLAY", "Normal", trace);
                    }, Epoch, r => Cur = r, () => { Goes++; FrameAtGo = FrameNow; PausedNow = false; });
                }
                catch (H.Refused e) { return H.Refusal(e); }
                catch (CondRefused e) { return H.Refusal(e); }
            }).Result;
        }
        public Dictionary<string, object> Batch(string driver, string acts)
        {
            var l = H.ParseActs(acts, false);
            return (Dictionary<string, object>)H.OneHop(Hop, () => Hands.Batch(driver, l)).Result;
        }

        public T.SceneRun Cur;
        public void Play(int frames, int perFrame = 6, Action<long> during = null)
        {
            for (int f = 0; f < frames; f++)
            {
                FrameNow++;
                Clock += 16;
                if (Cur != null) Cur.Settle();
                Hands.Frame();
                for (int i = 0; i < perFrame && !PausedNow; i++)
                {
                    TickNow++;
                    Rand += 3;
                    if (during != null) during(TickNow);
                    if (Cur != null) Cur.OnTickEnd(TickNow, Epoch, true);
                }
                Queue = 0;
            }
        }
        public static readonly object Epoch = 1.0;
        public List<(long seq, JsonElement r)> Rec(string rec) { return Out.Where(o => o.r.GetProperty("rec").GetString() == rec).ToList(); }
        public List<(long seq, JsonElement r)> Track(string name) { return Rec("track").Where(o => o.r.GetProperty("name").GetString() == name).ToList(); }
    }

    internal static class Program
    {
        static int _n, _bad;

        static void Check(string name, Action f)
        {
            _n++;
            string w = null;
            try { f(); } catch (Exception e) { w = e.GetType().Name + ": " + e.Message; }
            if (w != null) _bad++;
            Console.WriteLine("U " + name + " " + (w == null ? "ok" : "FAIL " + w.Replace("\n", " ")));
        }

        static void Eq(object a, object b, string what) { if (!Equals(a, b)) throw new Exception(what + ": got " + (a ?? "null") + ", want " + (b ?? "null")); }
        static void True(bool b, string what) { if (!b) throw new Exception(what); }
        static string Until(long t) { return "{\"cmp\":[{\"p\":\"game.tick\"},\">=\"," + t + "]}"; }
        static string Val(string of, string path, string op, string lit) { return "{\"cmp\":[{\"p\":\"value\",\"of\":\"" + of + "\",\"path\":\"" + path + "\"},\"" + op + "\"," + lit + "]}"; }
        static string Rec(string of, string path) { return "{\"of\":\"" + of + "\",\"path\":\"" + path + "\"}"; }
        static object G(Dictionary<string, object> d, string k) { object v; if (!d.TryGetValue(k, out v)) throw new Exception("no key " + k + " in " + C.Canon(d)); return v; }
        static Dictionary<string, object> D(object o) { return (Dictionary<string, object>)o; }
        static List<object> L(object o) { return (List<object>)o; }

        static World New(params string[] ids)
        {
            var w = new World();
            foreach (var id in ids) w.Add(id);
            Eq(G(w.Hands.Open("drv", 600), "success"), true, "open");
            return w;
        }

        static void Bind(World w, string json) { var r = w.Hands.Bind("drv", json); Eq(G(r, "success"), true, "bind " + C.Canon(r)); }

        static int Main()
        {
            Check("one_session_one_trace_no_gap", () =>
            {
                var w = New("P");
                Bind(w, "{\"p\":\"P\"}");
                w.Run("drv", "a", Until(1050), record: "[" + Rec("p", "hp") + "]");
                w.Play(30, 6, t => { if (t == 1020) w.Things["P"].hp = 90; });
                Eq(G(w.Hands.RunStatus("drv", "a"), "stage"), "closed", "first run");
                w.Run("drv", "b", Until(1090), record: "[" + Rec("p", "hp") + "]");
                w.Play(30);
                Eq(G(w.Hands.RunStatus("drv", "b"), "why"), "hit", "second run");
                w.Hands.Finish("drv", false);
                w.Play(5);
                var ns = w.Out.Select(o => o.r.GetProperty("n").GetInt32()).ToList();
                True(ns.SequenceEqual(Enumerable.Range(1, w.Out.Count)), "n has a gap or starts again: " + string.Join(",", ns));
                Eq(w.Out.Select(o => o.r.GetProperty("sess").GetString()).Distinct().Count(), 1, "sessions in the trace");
                Eq(w.Rec("open").Count, 2, "runs in the trace");
                Eq(w.Out.Last().r.GetProperty("rec").GetString(), "session_close", "last record");
                Eq(w.Out.Last().r.GetProperty("rows").GetInt32(), w.Out.Count - 1, "rows the close counts");
                Eq(w.Out.Last().r.GetProperty("drained").GetBoolean(), true, "drained");
            });
            Check("true_at_start_plays_no_tick", () =>
            {
                var w = New();
                var r = w.Run("drv", "a", Until(1000));
                Eq(w.Goes, 0, "the clock was started");
                w.Play(10);
                r = w.Hands.RunStatus("drv", "a");
                Eq(G(r, "why"), "hit", "why");
                Eq(w.TickNow, 1000L, "tick");
                Eq(G(r, "tick"), 1000.0, "reply tick");
                Eq(G(w.Run("drv", "b", Until(2000), limit: 0), "refused"), "NO_LIMIT", "a run with no limit");
            });
            Check("hit_wins_over_limit", () =>
            {
                var w = New();
                w.Run("drv", "a", Until(1040), limit: 40);
                w.Play(20);
                var r = w.Hands.RunStatus("drv", "a");
                Eq(G(r, "why"), "hit", "why");
                Eq(G(r, "tick"), 1040.0, "tick");
                w.Run("drv", "b", Until(5000), limit: 40);
                w.Play(20);
                Eq(G(w.Hands.RunStatus("drv", "b"), "why"), "limit", "why of a run that only reached its limit");
            });
            Check("an_unreadable_value_ends_as_unknown_and_is_named", () =>
            {
                var w = New("P");
                Bind(w, "{\"p\":\"P\"}");
                w.Run("drv", "a", Val("p", "hp", "<", "10"));
                w.Play(30, 6, t => { if (t == 1033) w.Things["P"].Gone = true; });
                var r = w.Hands.RunStatus("drv", "a");
                Eq(G(r, "why"), "unknown", "why");
                Eq(G(r, "tick"), 1033.0, "tick");
                Eq(w.TickNow, 1033L, "the game's tick");
                var u = D(G(r, "unknownValue"));
                Eq(G(u, "status"), "gone", "state of the unknown value");
                True(((string)G(u, "value")).Contains("of=p") && ((string)G(u, "value")).Contains("path=hp"), "the value is not named: " + G(u, "value"));
                var v = D(D(G(r, "values"))["p.hp"]);
                Eq(G(v, "state"), "gone", "value state");
                Eq(G(v, "v"), null, "value of a gone thing");
                Eq(D(L(G(r, "couldNotLook"))[0])["value"], "p.hp", "could not look");
                // the expected death is readable, and an optional node is refused: it would count an unreadable value as false
                var x = New("P");
                Bind(x, "{\"p\":\"P\"}");
                string ok = "{\"any\":[{\"cmp\":[{\"p\":\"value.state\",\"of\":\"p\",\"path\":\"hp\"},\"==\",\"gone\"]}," + Val("p", "hp", "<", "10") + "]}";
                x.Run("drv", "a", ok);
                x.Play(30, 6, t => { if (t == 1033) x.Things["P"].Gone = true; });
                Eq(G(x.Hands.RunStatus("drv", "a"), "why"), "hit", "why of an expected death");
                Eq(G(x.Run("drv", "b", "{\"cmp\":[{\"p\":\"value\",\"of\":\"p\",\"path\":\"hp\"},\"<\",10],\"optional\":true}"), "refused"), "OPTIONAL_COUNTS_UNKNOWN_FALSE", "optional");
                // a value that cannot be read at the start stops there
                var y = New("P");
                y.Run("drv", "a", Val("nobody", "hp", "<", "10"));
                Eq(y.Goes, 0, "the clock was started on an unbound value");
                Eq(G(D(G(y.Hands.RunStatus("drv", "a"), "unknownValue")), "status"), "unbound", "unbound");
            });
            Check("a_group_is_frozen", () =>
            {
                var w = New("A", "B", "Z");
                Bind(w, "{\"raiders\":[\"A\",\"B\"]}");
                w.Run("drv", "a", Until(1060), record: "[" + Rec("raiders", "hp") + "]");
                w.Play(30, 6, t => { if (t == 1020) w.Things["A"].Gone = true; if (t == 1030) w.Add("NEW"); });
                var r = w.Hands.RunStatus("drv", "a");
                var vals = D(G(r, "values"));
                Eq(string.Join(",", vals.Keys.OrderBy(k => k)), "raiders[0].hp,raiders[1].hp", "the group's values");
                Eq(D(vals["raiders[0].hp"])["state"], "gone", "the dead member");
                Eq(D(vals["raiders[0].hp"])["v"], null, "the dead member's value");
                Eq(D(vals["raiders[1].hp"])["state"], "ok", "the other member");
                var rows = w.Track("raiders[0].hp").Select(o => o.r.GetProperty("st").GetString() + o.r.GetProperty("tick").GetInt64()).ToList();
                Eq(string.Join(" ", rows), "ok1000 gone1020 gone1060", "rows of the dead member");
                // a condition over the group reads each member, the dead one included
                var x = New("A", "B");
                Bind(x, "{\"raiders\":[\"A\",\"B\"]}");
                string any = "{\"any_of\":{\"group\":\"raiders\",\"node\":" + Val("$", "Position.x", ">", "50") + "}}";
                x.Run("drv", "a", any);
                x.Play(30, 6, t => { if (t == 1040) x.Things["B"].Position = new Cell3(60, 5); });
                Eq(G(x.Hands.RunStatus("drv", "a"), "tick"), 1040.0, "any_of over the group");
                Eq(D(G(x.Hands.RunStatus("drv", "a"), "values")).Count, 2, "values the condition read");
                Eq(G(x.Run("drv", "b", any.Replace("raiders", "ghosts")), "refused"), "UNKNOWN_GROUP", "an unbound group");
                Bind(x, "{\"none\":[]}");
                Eq(G(x.Run("drv", "c", any.Replace("raiders", "none")), "refused"), "EMPTY_GROUP", "an empty group");
            });
            Check("private_fields_and_statics_are_read", () =>
            {
                var w = New("P");
                Bind(w, "{\"p\":\"P\"}");
                w.Things["P"].Held.Set(true, 12);
                w.Run("drv", "a", Until(1040), record: "[" + Rec("p", "comp<HeldComp>.held") + "," + Rec("p", "comp<HeldComp>.heldTicks") + "," + Rec("static:ModStatics", "secretCount") + "," +
                                                       Rec("p", "Position") + "," + Rec("p", "jobDef") + "," + Rec("p", "mood") + "," + Rec("p", "Wounds[1]") + "," + Rec("p", "Wounds.Count") + "," + Rec("p", "Auto") + "]");
                w.Play(30, 6, t => { if (t == 1010) ModStatics.Bump(); if (t == 1020) w.Things["P"].Held.Set(false, 13); });
                var v = D(G(w.Hands.RunStatus("drv", "a"), "values"));
                Eq(D(v["p.comp<HeldComp>.held"])["v"], false, "private bool: false is a value");
                Eq(D(v["p.comp<HeldComp>.heldTicks"])["v"], 13.0, "private int");
                Eq(D(v["static:ModStatics.secretCount"])["v"], 8.0, "private static");
                Eq(D(v["p.Position"])["v"], "5,5", "a cell, through a property that returns a field");
                Eq(D(v["p.jobDef"])["state"], "ok", "null is a reading");
                Eq(D(v["p.jobDef"])["v"], null, "null");
                Eq(D(v["p.mood"])["v"], "Angry", "enum");
                Eq(D(v["p.Wounds[1]"])["v"], 4.0, "list index");
                Eq(D(v["p.Wounds.Count"])["v"], 2.0, "reviewed property");
                Eq(D(v["p.Auto"])["v"], "auto", "auto property");
                Eq(D(v["static:ModStatics.secretCount"])["reads"], 42.0, "reads of a track: 40 ticks, the first and the last");
                Eq(w.Track("static:ModStatics.secretCount").Count, 3, "rows of the static: first, change, last");
                var all = P.Read(w, "p", "Wounds");
                Eq(string.Join(",", L(all.V)), "3,4", "a list of values");
            });
            Check("a_wrong_field_is_an_error_with_the_fields", () =>
            {
                var w = New("P");
                Bind(w, "{\"p\":\"P\"}");
                var r = P.Read(w, "p", "hitPoints");
                Eq(r.State, "error", "state");
                Eq(r.V, null, "value");
                True(r.Refused == null, "a wrong field name is not a refusal");
                foreach (var f in new[] { "hitPoints", "hp", "positionInt", "Wounds", "Position" }) True(r.Detail.Contains(f), "detail does not name " + f + ": " + r.Detail);
                r = P.Read(w, "p", "Rider.hp");
                Eq(r.State, "error", "a null link");
                True(r.Detail.Contains("null at 'Rider'"), r.Detail);
                r = P.Read(w, "p", "Held");
                True(r.State == "error" && r.Detail.Contains("heldTicks"), "an object is not a value: " + r.Detail);
                r = P.Read(w, "p", "Wounds[9]");
                True(r.State == "error" && r.Detail.Contains("9 of 2"), r.Detail);
                w.Run("drv", "a", Until(1010), record: "[" + Rec("p", "hitPoints") + "]");
                w.Play(10);
                var run = w.Hands.RunStatus("drv", "a");
                Eq(G(run, "why"), "hit", "a wrong name in a track does not stop the run");
                Eq(D(D(G(run, "values"))["p.hitPoints"])["state"], "error", "the track's state");
                Eq(G(D(L(G(run, "couldNotLook"))[0]), "firstTick"), 1000.0, "could not look from");
            });
            Check("an_unreviewed_method_is_refused_by_name", () =>
            {
                var w = New("P");
                w.Things["B"] = new Beast();
                Bind(w, "{\"p\":\"P\",\"b\":\"B\"}");
                Creature.Touched = 0;
                foreach (var path in new[] { "Compute", "Compute()", "Label", "Digest" })
                {
                    Eq(P.Read(w, "p", path).Refused, "PATH_CALLS_METHOD", path);
                    Eq(G(w.Run("drv", "r" + path, Val("p", path, ">", "1")), "refused"), "PATH_CALLS_METHOD", "a condition on " + path);
                    Eq(G(w.Run("drv", "t" + path, Until(1010), record: "[" + Rec("p", path) + "]"), "refused"), "PATH_CALLS_METHOD", "a track on " + path);
                }
                Eq(P.Read(w, "p", "Virt").V, 100.0, "a getter that only returns a field");
                Eq(P.Read(w, "b", "Virt").Refused, "PATH_CALLS_METHOD", "the override is what would run");
                Eq(Creature.Touched, 0, "a method ran");
                Eq(w.Goes, 0, "the clock was started");
                foreach (var path in new[] { "", "a..b", ".a", "a.", "a[", "a[x]", "1a", "comp<>", "a b", "a[-1]" })
                    Eq(P.Read(w, "p", path).Refused, "BAD_PATH", "path '" + path + "'");
            });
            Check("a_thousand_reads_change_nothing", () =>
            {
                var w = New("P");
                Bind(w, "{\"p\":\"P\"}");
                string before = w.Things["P"].Digest() + "|" + w.TickNow + "|" + w.Rand + "|" + w.Out.Count + "|" + w.PausedNow;
                var paths = new[] { "hp", "Position", "Position.x", "comp<HeldComp>.held", "Wounds", "Wounds.Count", "Label", "Compute", "nothing", "mood" };
                for (int i = 0; i < 1000; i++) P.Read(w, "p", paths[i % paths.Length]);
                Eq(w.Things["P"].Digest() + "|" + w.TickNow + "|" + w.Rand + "|" + w.Out.Count + "|" + w.PausedNow, before, "state digest");
            });
            Check("only_the_driver_drives_an_open_session", () =>
            {
                var w = New("P");
                foreach (var who in new[] { "other", "", null })
                {
                    Eq(G(w.Run(who, "a", Until(1010)), "refused"), "NOT_THE_DRIVER", "run by '" + who + "'");
                    Eq(G(w.Batch(who, "[{\"id\":\"x\",\"tool\":\"jawa/ping\"}]"), "refused"), "NOT_THE_DRIVER", "batch by '" + who + "'");
                    Eq(G(w.Hands.Bind(who, "{\"p\":\"P\"}"), "refused"), "NOT_THE_DRIVER", "bind by '" + who + "'");
                    Eq(G(w.Hands.Finish(who, true), "refused"), "NOT_THE_DRIVER", "abort by '" + who + "'");
                }
                Eq(G(w.Hands.Open("other", 60), "refused"), "SESSION_OPEN", "a second session");
                Eq(w.Done.Count, 0, "acts done");
                Eq(G(w.Run("drv", "a", Until(1010)), "success"), true, "the driver's own run");
                Eq(G(w.Run("drv", "b", Until(1020)), "refused"), "RUN_ACTIVE", "a second run while one is live");
                Eq(G(w.Hands.Cancel("other", "a"), "refused"), "NOT_THE_DRIVER", "cancel by another caller");
                w.Play(10);
                Eq(w.TickNow, 1010L, "the original stop tick after a refused cancel");
                Eq(G(w.Run("drv", "cancel", Until(1020)), "success"), true, "the driver's next run");
                Eq(G(w.Hands.Cancel("drv", "cancel"), "why"), "cancelled", "cancel by the driver");
                w.Play(10);
                Eq(w.TickNow, 1010L, "the driver cancelled before another tick");
                Eq(G(w.Batch("drv", "[{\"id\":\"x\",\"tool\":\"jawa/ping\"}]"), "success"), true, "the driver's own batch");
                w.PausedNow = false;
                Eq(G(w.Run("drv", "c", Until(5000)), "refused"), "GAME_RUNNING", "a run on a running game");
                Eq(G(w.Batch("drv", "[{\"id\":\"y\",\"tool\":\"jawa/ping\"}]"), "refused"), "GAME_RUNNING", "a batch on a running game");
                w.PausedNow = true;
                w.RefuseRunWhy = "CANNOT_RUN: no control";
                Eq(G(w.Run("drv", "d", Until(5000)), "refused"), "CANNOT_RUN", "the game's own refusal");
                Eq(G(w.Hands.Bind("drv", "{\"p\":\"Nobody\"}"), "refused"), "UNKNOWN_THING", "binding a thing that is not there");
                Eq(G(w.Hands.RunStatus("other", "a"), "why"), "hit", "anyone may read");
            });
            Check("a_taken_session_is_read_and_ended_never_played", () =>
            {
                var w = new World();
                w.Add("P1");
                Eq(G(w.Hands.Take("new", "drv"), "refused"), "NO_SESSION", "no session");
                w.Hands.Open("drv", 600);
                w.Run("drv", "a", Until(900000), limit: 800000);
                w.Play(5);
                Eq(G(w.Hands.Take("new", null), "refused"), "DRIVER_ALIVE", "a live lease with no name of the dead driver");
                Eq(G(w.Hands.Take("new", "somebody"), "refused"), "DRIVER_ALIVE", "another driver's name");
                Eq(G(w.Hands.Take("drv", "drv"), "refused"), "BAD_ARGS", "its own driver");
                True(!w.PausedNow, "a refused take changed the game");
                var s = w.Hands.Take("new", "drv");
                Eq(G(s, "success"), true, "take");
                Eq(G(s, "driver"), "new", "driver");
                Eq(G(s, "taken"), true, "taken");
                Eq(w.PausedNow, true, "paused");
                w.Play(5);
                Eq(G(D(G(w.Hands.State(), "lastRun")), "why"), "cancelled", "the live run");
                Eq(w.Rec("close").Count, 1, "closing records of the run");
                Eq(w.Rec("session_taken").Single().r.GetProperty("from").GetString(), "drv", "the record");
                Eq(G(w.Run("new", "b", Until(900000)), "refused"), "TAKEN_OVER", "a run");
                Eq(G(w.Batch("new", "[{\"id\":\"x\",\"tool\":\"jawa/hit\"}]"), "refused"), "TAKEN_OVER", "a batch");
                Eq(G(w.Hands.Bind("new", "{\"p\":\"P1\"}"), "refused"), "TAKEN_OVER", "a bind");
                Eq(w.Done.Count, 0, "acts");
                Eq(G(w.Hands.RunStatus("new", "a"), "stage"), "closed", "the run can be read");
                Eq(G(w.Hands.Finish("drv", false), "refused"), "NOT_THE_DRIVER", "the dead driver's text");
                Eq(G(w.Hands.Finish("new", false), "success"), true, "close");
                w.Play(5);
                Eq(G(w.Hands.State(), "stage"), "closed", "stage");
                Eq(G(w.Hands.Open("next", 600), "success"), true, "the next session");
                Eq(G(w.Hands.State(), "taken"), false, "the next session is not a taken one");
                // past its lease no name is needed
                var x = new World();
                x.Hands.Open("drv", 10);
                x.Clock += 20000;
                x.Play(2);
                Eq(G(x.Hands.Take("new", null), "success"), true, "after the lease");
            });
            Check("a_session_past_its_lease_stays_open_and_paused", () =>
            {
                var w = new World();
                w.Hands.Open("drv", 10);
                w.Run("drv", "a", Until(900000), limit: 800000);
                w.Play(30);
                True(!w.PausedNow, "the run plays inside the lease");
                w.Clock += 20000;
                w.Play(5);
                Eq(w.PausedNow, true, "paused after the lease");
                var s = w.Hands.State();
                Eq(G(s, "stage"), "open", "stage");
                Eq(G(s, "leaseEnded"), true, "leaseEnded");
                Eq(G(D(G(s, "lastRun")), "why"), "cancelled", "the run");
                Eq(w.Rec("lease_ended").Count, 1, "lease_ended records");
                Eq(w.Rec("session_close").Count, 0, "the session closed itself");
                Eq(G(w.Hands.RunStatus(null, "a"), "stage"), "closed", "the run can be read");
                Eq(G(w.Hands.Open("other", 60), "refused"), "SESSION_OPEN", "it is still open");
                Eq(G(w.Hands.Finish("other", true), "success"), true, "anyone may abort it now");
                w.Play(5);
                Eq(G(w.Hands.State(), "stage"), "aborted", "stage");
                Eq(w.Rec("session_close").Single().r.GetProperty("end").GetString(), "aborted", "the closing record");
                // a driver that polls keeps its lease
                var x = new World();
                x.Hands.Open("drv", 10);
                x.Run("drv", "a", Until(900000), limit: 800000);
                for (int i = 0; i < 5; i++) { x.Clock += 8000; x.Hands.RunStatus("drv", "a"); x.Play(2); }
                Eq(x.PausedNow, false, "a polling driver's run was stopped");
                // a poll of somebody else does not
                for (int i = 0; i < 5; i++) { x.Clock += 8000; x.Hands.RunStatus("other", "a"); x.Play(2); }
                Eq(x.PausedNow, true, "a stranger's poll kept the lease");
            });
            Check("no_session_no_run", () =>
            {
                var w = new World();
                Eq(G(w.Run("drv", "a", Until(1010)), "refused"), "NO_SESSION", "a run");
                Eq(G(w.Batch("drv", "[{\"id\":\"x\",\"tool\":\"jawa/ping\"}]"), "refused"), "NO_SESSION", "a batch");
                Eq(G(w.Hands.State(), "stage"), "none", "state");
                Eq(w.Goes + w.Done.Count + w.Out.Count, 0, "something was done");
                w.Hands.Open("drv", 60);
                w.Hands.Finish("drv", false);
                w.Play(5);
                Eq(G(w.Run("drv", "a", Until(1010)), "refused"), "NO_SESSION", "a run after the close");
                Eq(G(w.Hands.State(), "stage"), "closed", "state after the close");
            });
            Check("no_frame_inside_a_batch", () =>
            {
                var w = New("P");
                var r = w.Batch("drv", "[{\"id\":\"a\",\"tool\":\"jawa/hit\",\"args\":{\"id\":\"P\",\"by\":3}},{\"id\":\"b\",\"tool\":\"jawa/ping\"}]");
                Eq(G(r, "allDone"), true, "all done");
                Eq(G(r, "frameFrom"), G(r, "frameTo"), "frames of the reply");
                var f = w.Out.Where(o => o.r.GetProperty("rec").GetString().StartsWith("act_")).Select(o => o.r.GetProperty("frame").GetInt32()).ToList();
                Eq(f.Count, 4, "act records");
                Eq(f.Distinct().Count(), 1, "frames in the act records: " + string.Join(",", f));
                var rec = string.Join(" ", w.Out.Where(o => o.r.GetProperty("rec").GetString().StartsWith("act_")).Select(o => o.r.GetProperty("rec").GetString() + ":" + o.r.GetProperty("id").GetString()));
                Eq(rec, "act_start:a act_end:a act_start:b act_end:b", "order");
            });
            Check("a_repeated_id_returns_the_first_reply", () =>
            {
                var w = New("P");
                string acts = "[{\"id\":\"a\",\"tool\":\"jawa/hit\",\"args\":{\"id\":\"P\",\"by\":30}}]";
                var r1 = D(L(G(w.Batch("drv", acts), "acts"))[0]);
                w.Play(3);
                var r2 = D(L(G(w.Batch("drv", acts), "acts"))[0]);
                Eq(w.Things["P"].hp, 70, "the victim's health");
                Eq(G(r1, "replayed"), false, "first");
                Eq(G(r2, "replayed"), true, "second");
                Eq(C.Canon(G(r2, "reply")), C.Canon(G(r1, "reply")), "reply");
                Eq(G(r2, "frame"), G(r1, "frame"), "frame of the first");
                Eq(w.Rec("act_start").Count, 1, "records");
                // a failed act is not tried again either, and a run's request is answered by its id
                w.Batch("drv", "[{\"id\":\"t\",\"tool\":\"jawa/throw\"}]");
                Eq(G(D(L(G(w.Batch("drv", "[{\"id\":\"t\",\"tool\":\"jawa/throw\"}]"), "acts"))[0]), "state"), "failed", "a repeat of a failed act");
                Eq(w.Done.Count(x => x == "jawa/throw"), 1, "tries of the failed act");
                w.Run("drv", "run", Until(1050));
                w.Play(20);
                var again = w.Run("drv", "run", Until(1050));
                Eq(G(again, "replayed"), true, "the run's repeat");
                Eq(G(again, "why"), "hit", "the run's repeat answers the run");
                Eq(w.TickNow, 1050L, "the run was played twice");
                Eq(w.Goes, 1, "starts of the clock");
            });
            Check("a_changed_repeat_is_refused", () =>
            {
                var w = New("P");
                w.Batch("drv", "[{\"id\":\"a\",\"tool\":\"jawa/hit\",\"args\":{\"id\":\"P\",\"by\":30}}]");
                Eq(G(w.Batch("drv", "[{\"id\":\"b\",\"tool\":\"jawa/ping\"},{\"id\":\"a\",\"tool\":\"jawa/hit\",\"args\":{\"id\":\"P\",\"by\":31}}]"), "refused"), "REQUEST_CONFLICT", "other arguments");
                Eq(G(w.Batch("drv", "[{\"id\":\"a\",\"tool\":\"jawa/ping\"}]"), "refused"), "REQUEST_CONFLICT", "another tool");
                Eq(w.Things["P"].hp, 70, "health");
                Eq(w.Done.Count, 1, "acts done: the whole batch is refused");
                Eq(G(w.Batch("drv", "[{\"id\":\"c\",\"tool\":\"other/ping\"},{\"id\":\"d\",\"tool\":\"jawa/ping\"}]"), "refused"), "UNKNOWN_TOOL", "a tool that cannot be in a batch");
                Eq(w.Done.Count, 1, "acts done after a refused tool");
                w.Run("drv", "run", Until(1050));
                w.Play(20);
                Eq(G(w.Run("drv", "run", Until(1060)), "refused"), "REQUEST_CONFLICT", "a run request with another condition");
                Eq(G(w.Run("drv", "a", Until(1060)), "refused"), "REQUEST_CONFLICT", "a run with an act's id");
                Eq(G(w.Run("drv", "", Until(1060)), "refused"), "NO_REQUEST", "a run with no id");
                try { w.Batch("drv", "[{\"tool\":\"jawa/ping\"}]"); throw new Exception("an act with no id was taken"); } catch (H.Refused e) { Eq(e.Name, "NO_REQUEST", "an act with no id"); }
            });
            Check("a_thrown_act_keeps_the_acts_before_it", () =>
            {
                var w = New("P");
                var r = w.Batch("drv", "[{\"id\":\"a\",\"tool\":\"jawa/hit\",\"args\":{\"id\":\"P\",\"by\":3}},{\"id\":\"b\",\"tool\":\"jawa/throw\"},{\"id\":\"c\",\"tool\":\"jawa/ping\"}]");
                var states = string.Join(",", L(G(r, "acts")).Select(a => D(a)["state"]));
                Eq(states, "done,failed,not_tried", "states");
                Eq(G(r, "allDone"), false, "allDone");
                Eq(G(r, "firstNotDone"), "b", "firstNotDone");
                True(((string)D(L(G(r, "acts"))[1])["error"]).Contains("no target"), "the error is not named");
                Eq(w.Things["P"].hp, 97, "the first act's effect");
                Eq(string.Join(",", w.Rec("act_end").Select(o => o.r.GetProperty("state").GetString())), "done,failed", "end records");
                Eq(w.Hands.State()["openAct"], null, "open act");
                Eq(D(L(G(w.Batch("drv", "[{\"id\":\"n\",\"tool\":\"jawa/no\"}]"), "acts"))[0])["state"], "refused", "a tool that says no is not done");
            });
            Check("an_act_at_zero_shares_the_hop_that_starts_the_clock", () =>
            {
                var w = New("P");
                Bind(w, "{\"p\":\"P\"}");
                var r = w.Run("drv", "a", Until(1020), record: "[" + Rec("p", "hp") + "]", acts: "[{\"id\":\"h\",\"tool\":\"jawa/hit\",\"args\":{\"id\":\"P\",\"by\":40},\"at\":0}]");
                Eq(w.Goes, 1, "starts");
                var s = w.Rec("act_start").Single();
                Eq(s.r.GetProperty("frame").GetInt32(), w.FrameAtGo, "the frame of the act and of the start");
                Eq(s.r.GetProperty("tick").GetInt64(), 1000L, "tick of the act");
                True(w.Track("p.hp")[0].seq < s.seq && w.Track("p.hp")[0].r.GetProperty("v").GetDouble() == 100, "the first sample is before the act");
                w.Play(10);
                Eq(w.Track("p.hp")[1].r.GetProperty("tick").GetInt64(), 1001L, "the act's effect is sampled on the first tick");
                r = w.Hands.RunStatus("drv", "a");
                Eq(D(L(G(r, "acts"))[0])["state"], "done", "the act in the run's reply");
                // an act that is not done: the clock is not started
                var x = New("P");
                x.Run("drv", "a", Until(1020), acts: "[{\"id\":\"h\",\"tool\":\"jawa/throw\",\"at\":0}]");
                Eq(x.Goes, 0, "the clock was started after a failed act");
                x.Play(5);
                Eq(G(x.Hands.RunStatus("drv", "a"), "why"), "fault", "why");
                Eq(x.TickNow, 1000L, "tick");
            });
            Check("an_act_on_a_tick_is_any_tool_call", () =>
            {
                var w = New("P");
                Bind(w, "{\"p\":\"P\"}");
                w.Run("drv", "a", Val("p", "hp", "<", "80"), record: "[]", acts: "[{\"id\":\"h\",\"tool\":\"jawa/hit\",\"args\":{\"id\":\"P\",\"by\":40},\"at\":25},{\"id\":\"late\",\"tool\":\"jawa/ping\",\"at\":60}]");
                w.Play(20);
                var r = w.Hands.RunStatus("drv", "a");
                Eq(G(r, "why"), "hit", "why");
                Eq(G(r, "tick"), 1026.0, "the effect is seen on the next tick");
                Eq(w.Rec("act_start").Single().r.GetProperty("tick").GetInt64(), 1025L, "tick of the act");
                var acts = L(G(r, "acts"));
                Eq(D(acts[0])["state"] + "," + D(acts[1])["state"], "done,not_tried", "acts");
                Eq(G(w.Batch("drv", "[{\"id\":\"h\",\"tool\":\"jawa/ping\"}]"), "refused"), "REQUEST_CONFLICT", "the act's id is taken");
                Eq(G(w.Run("drv", "b", Until(2000), limit: 30, acts: "[{\"id\":\"z\",\"tool\":\"jawa/ping\",\"at\":30}]"), "refused"), "BAD_ARGS", "an act on the limit");
            });
            Console.WriteLine("U-count " + _n);
            return _bad == 0 ? 0 : 1;
        }
    }
}
