// Units for the life cycle of a run (JawaBenchSceneTickCore.cs, JawaBenchHandsCore.cs, JawaBenchRunLockCore.cs: the PRODUCTION
// files). One unit per promise of design/specs/2026-11-23-bridge-v2-life-cycle/boundary.md. Prints "U <name> ok|FAIL why" and
// "U-count n". World plays the game as TickManagerUpdate does: a tick that throws runs no postfix, and the finalizer speaks instead.
// args[0]: a file of "tool<TAB>description", every [Tool] of the companion.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using C = JawaBench.BridgeTools.JawaBenchCondCore;
using H = JawaBench.BridgeTools.JawaBenchHandsCore;
using L = JawaBench.BridgeTools.JawaBenchRunLockCore;
using T = JawaBench.BridgeTools.JawaBenchSceneTickCore;

namespace JawaBench.BridgeTools
{
    internal sealed class World : IHandsHost, IProbeSource
    {
        public long TickNow = 1000, Seq, Queue;
        public bool PausedNow = true, ThrowPause, ThrowRead, Alive = true, Control = true;
        public int FrameNow = 50, Goes, Pauses;
        public ulong Rand = 7;
        public double Clock, SlowMs;
        public object Epoch = 1.0;
        public readonly Dictionary<string, object> Values = new Dictionary<string, object> { { "fast", 1.0 }, { "slow", 1.0 } };
        public readonly List<JsonElement> Out = new List<JsonElement>();
        public readonly List<string> Acted = new List<string>();
        public H.Hands Hands;
        public T.SceneRun Cur;
        public World() { Hands = new H.Hands(this); }

        public long Enqueue(string fields) { Seq++; Queue++; Out.Add(JsonDocument.Parse("{" + fields + "}").RootElement); return Seq; }
        public bool Drained() { return Queue == 0; }
        public bool Pause()
        {
            if (ThrowPause) throw new InvalidOperationException("the speed setter threw");
            if (!Alive) return false;                  // another game is there: it is not this run's to pause
            Pauses++;
            PausedNow = true;
            return true;
        }
        public long Tick() { return TickNow; }
        public ulong RandState() { return Rand; }
        public double NowMs() { return Clock; }
        public long? AllocBytes() { return null; }
        public int Frame() { return FrameNow; }
        public bool Paused() { return PausedNow; }
        public string RefuseAct(string tool, Dictionary<string, object> args) { return null; }
        public ActOutcome Act(string tool, Dictionary<string, object> args) { Acted.Add(tool); return new ActOutcome { State = "done" }; }
        public string RefuseRun() { return Control ? null : "CANNOT_RUN: the player has no control: the game would drop the pause"; }
        public bool Bind(string alias, int member, string id) { return true; }
        public void Unbind(string alias) { }

        public int CurrentMap() { return 0; }
        public bool MapSize(int m, out int x, out int z) { x = z = 250; return m == 0; }
        public string Refuse(string key, C.Probe p) { return null; }
        public CondRead Read(string key, C.Probe p, int x, int z)
        {
            if (p.Name == "game.tick") return new CondRead((double)TickNow, "ok", "");
            if (ThrowRead) throw new InvalidOperationException("the getter threw");
            string path = (string)p.Args["path"];
            Clock += path == "slow" ? SlowMs : 0.01;
            return new CondRead(Values[path], "ok", "");
        }

        public T.SceneRun Make(string until, int max = 500, double budget = 0, string mode = "PLAY", params T.Act[] acts)
        {
            var spec = C.ParseJson("{\"until\":" + until + ",\"max_ticks\":" + max + ",\"sample\":{\"every\":1,\"probes\":{\"fast\":" + Program.V("fast") + "}}}");
            Cur = new T.SceneRun("r1", new C.Compiler(this, "run").CompileSpec(spec), this, acts, this, mode, "Normal", null, budget);
            return Cur;
        }
        public void Start(T.SceneRun r) { r.Arm(TickNow, Epoch); if (r.Running) PausedNow = false; }

        public void Play(int frames, int perFrame = 6, Action<long> during = null, Func<long, string> stop = null)
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
                    try { if (during != null) during(TickNow); }
                    catch (Exception e) { if (Cur != null) Cur.Force("threw", "the game's tick threw " + e.GetType().Name, TickNow); break; }
                    if (Cur != null) Cur.OnTickEnd(TickNow, Epoch, true, stop == null ? null : stop(TickNow));
                }
                Queue = 0;
            }
        }
        public List<JsonElement> Rec(string rec) { return Out.Where(o => o.GetProperty("rec").GetString() == rec).ToList(); }
        public JsonElement One(string rec) { var l = Rec(rec); if (l.Count != 1) throw new Exception(l.Count + " records " + rec + ", want 1"); return l[0]; }

        public Dictionary<string, object> Session(string driver, string request, string until, int limit = 500)
        {
            return Hands.StartRun(driver, request, until, new List<HandAct>(), limit, (id, ticks, trace) =>
            {
                var plan = H.MakePlan(until, null, limit, -1, Hands.GroupSize);
                return new T.SceneRun(id, plan.Compile(this), this, ticks, this, "PLAY", "Normal", trace);
            }, Epoch, r => Cur = r, () => { Goes++; PausedNow = false; });
        }
    }

    internal static class Program
    {
        static int _n, _bad;
        internal static string V(string path) { return "{\"p\":\"thing.field\",\"thing\":\"P\",\"path\":\"" + path + "\"}"; }
        static string At(long t) { return "{\"cmp\":[{\"p\":\"game.tick\"},\">=\"," + t + "]}"; }
        static string Is(string path, double v) { return "{\"cmp\":[" + V(path) + ",\"==\"," + v + "]}"; }

        static void Check(string name, Action f)
        {
            _n++;
            string w = null;
            try { f(); } catch (Exception e) { w = e.GetType().Name + ": " + e.Message; }
            if (w != null) _bad++;
            Console.WriteLine("U " + name + " " + (w == null ? "ok" : "FAIL " + w));
        }
        static void Eq(object a, object b, string what) { if (!Equals(a, b)) throw new Exception(what + ": got " + a + ", want " + b); }
        static string Str(JsonElement e, string k) { return e.GetProperty(k).GetString(); }

        /// <summary>After an end: nothing of the run is stepped again, and it closes.</summary>
        static void Quiet(World w, T.SceneRun r)
        {
            int n = w.Out.Count;
            string stage = r.Stage;
            w.Values["fast"] = 99.0;
            r.OnTickEnd(w.TickNow + 1, w.Epoch, true);
            Eq(w.Out.Count, n, "records that an ended run wrote on a later tick");
            Eq(r.Running, false, "running after the end (" + stage + ")");
        }

        static int Main(string[] args)
        {
            var tools = File.ReadAllLines(args[0]).Select(x => x.Split('\t')).ToDictionary(x => x[0], x => x.Length > 1 ? x[1] : "");
            Check("a_safety_stop_and_a_hit_on_one_tick_report_both", () =>
            {
                var w = new World();
                var r = w.Make(Is("slow", 2), 500, 0, "STEP");
                w.Start(r);
                w.Play(40, 6, t => { if (t == 1040) w.Values["slow"] = 2.0; }, t => t == 1040 ? "death" : null);
                var e = w.One("end");
                var trig = e.GetProperty("triggers").EnumerateArray().Select(x => x.GetString()).ToList();
                Eq(string.Join("+", trig), "cond+death", "triggers");
                Eq(Str(e, "state"), "stopped", "state");
                Eq(e.GetProperty("hitTick").GetDouble(), 1040.0, "hitTick");
                Eq(w.TickNow, 1040L, "tick");
                // a stop with no hit, and a hit with no stop
                var a = new World();
                a.Start(a.Make(Is("slow", 2)));
                a.Play(40, 6, null, t => t == 1020 ? "death" : null);
                Eq(a.One("end").GetProperty("hitTick").ValueKind, JsonValueKind.Null, "hitTick of a stop alone");
                Eq(a.TickNow, 1020L, "tick of a stop alone");
            });
            Check("the_budget_stop_names_the_costliest_node", () =>
            {
                var w = new World();
                var r = w.Make("{\"all\":[" + Is("fast", 5) + "," + Is("slow", 5) + "]}", 500, 50);
                w.Start(r);
                w.Play(60, 6, t => { w.SlowMs = t >= 1030 ? 80 : 1; });
                var e = w.One("end");
                Eq(Str(e, "state"), "budget", "state");
                Eq(w.TickNow, 1030L, "tick");
                string why = Str(e, "why");
                if (!why.Contains("path=slow") || why.Contains("path=fast")) throw new Exception("the costliest is not named: " + why);
                Eq(Str(e.GetProperty("costliest"), "node"), "n2", "costliest node");
                Quiet(w, r);
                // no budget given: no stop
                var b = new World { SlowMs = 5000 };
                b.Start(b.Make("{\"any\":[" + Is("slow", 5) + "," + At(1010) + "]}"));
                b.Play(20);
                Eq(Str(b.One("end"), "state"), "hit", "a slow run with no budget");
                // a hit on a tick over the budget is a hit
                var c = new World { SlowMs = 80 };
                c.Start(c.Make("{\"any\":[" + Is("slow", 5) + "," + At(1001) + "]}", 500, 50));
                c.Play(20);
                Eq(Str(c.One("end"), "state"), "hit", "a hit on a slow tick");
            });
            Check("an_epoch_change_ends_the_run", () =>
            {
                var w = new World();
                var r = w.Make(At(1400));
                w.Start(r);
                w.Play(40, 6, t => { if (t == 1050) { w.Epoch = 2.0; w.Alive = false; } });
                Eq(Str(w.One("end"), "state"), "epoch", "state");
                Eq(w.One("end").GetProperty("executed").GetInt64(), 50L, "executed");
                Eq(w.PausedNow, false, "the other game was paused by the run");
                Eq(w.One("close").GetProperty("paused").GetBoolean(), false, "paused on the close");
                if (!w.Rec("fault").Any(f => Str(f, "what") == "game_replaced")) throw new Exception("no fault names the replaced game");
                Quiet(w, r);
                // seen between two ticks: the game is gone before the tick hook saw it
                var m = new World();
                var q = m.Make(At(1400));
                m.Start(q);
                m.Play(2);
                q.Force("epoch", "map 3 left the game under the run", m.TickNow);
                m.Play(3);
                Eq(Str(m.One("end"), "why"), "map 3 left the game under the run", "why");
                Eq(m.PausedNow, true, "a map that left leaves the game paused");
                m.One("close");
            });
            Check("two_runs_cannot_be_armed_at_once", () =>
            {
                foreach (var stage in new[] { "running", "settling" })
                    if (!(L.RefuseArm("r1", stage, false, null, null) ?? "").Contains("r1")) throw new Exception("a second run is armed beside one that is " + stage);
                Eq(L.RefuseArm("r1", "closed", false, null, null), null, "after the close");
                Eq(L.RefuseArm(null, null, true, null, null) != null, true, "beside jawa/safe_advance");
                Eq(L.RefuseArm(null, null, false, "jawa/run_scenes", null) != null, true, "beside jawa/run_scenes");
                Eq(L.RefuseArm(null, null, false, "jawa/run_scenes", "jawa/run_scenes"), null, "the step loop's own run");
                var w = new World();
                w.Hands.Open("d", 600);
                Eq(w.Session("d", "q1", At(1300))["success"], true, "first");
                w.Play(2);
                Eq(w.Session("d", "q2", At(1300)).TryGetValue("refused", out var no) ? no : null, "RUN_ACTIVE", "second");
                Eq(w.Goes, 1, "clock starts");
                Eq(w.Rec("open").Count, 1, "open records");
                Eq(w.Hands.Open("other", 600)["refused"], "SESSION_OPEN", "a second driver");
            });
            Check("a_thrown_tick_still_writes_its_closing_record", () =>
            {
                var w = new World();
                var r = w.Make(At(1400));
                w.Start(r);
                w.Play(40, 6, t => { if (t == 1033) throw new InvalidOperationException("a mod threw"); });
                Eq(Str(w.One("end"), "state"), "threw", "state");
                Eq(w.TickNow, 1033L, "no tick after the one that threw");
                Eq(w.One("close").GetProperty("paused").GetBoolean(), true, "paused");
                Quiet(w, r);
                // the evaluator throws, the pause throws, and the last sample throws: the run still closes
                foreach (var plant in new Action<World>[] { x => x.ThrowRead = true, x => x.ThrowPause = true })
                {
                    var v = new World();
                    var q = v.Make(At(1060));
                    v.Start(q);
                    v.Play(4);
                    plant(v);
                    try { v.Play(1, 1); } catch (InvalidOperationException e) { q.Force("aborted", "the tick step threw " + e.Message, v.TickNow); }
                    if (q.Running) q.Force("cancelled", "x", v.TickNow);
                    v.Play(6, 0);
                    v.One("end");
                    v.One("close");
                    if (!v.Rec("fault").Any(f => Str(f, "what") == "threw")) throw new Exception("no fault names the throw");
                    Eq(q.Stage, "closed", "stage");
                    Quiet(v, q);
                }
                // the first sample throws: the run never starts the clock, and closes
                var a = new World { ThrowRead = true };
                var p = a.Make(At(1060));
                a.Start(p);
                Eq(a.PausedNow, true, "paused");
                a.Play(6);
                Eq(Str(a.One("end"), "state"), "aborted", "state of a run whose arm threw");
                a.One("close");
            });
            Check("a_changing_tool_during_a_run_is_refused_with_the_run_id", () =>
            {
                var log = new L.LockLog();
                string[] changing = { "jawa/spawn_pawn", "jawa/damage", "jawa/set_terrain", "jawa/weather_set", "jawa/fire_incident", "jawa/world_tile_set", "jawa/ideo_create",
                                      "jawa/static_call", "jawa/debug_actions", "jawa/ordered_job", "jawa/run_scenes", "jawa/set_game_speed", "jawa/comp_set", "jawa/mod_settings_field" };
                foreach (var t in changing)
                {
                    if (!tools.ContainsKey(t)) throw new Exception(t + " is no tool of the companion");
                    string no = L.Refuse(t, L.DeclaredRead(tools[t]), null, "s1_7", false, log);
                    if (no == null || !no.Contains("s1_7") || !no.Contains(t)) throw new Exception(t + " is let through, or the run is not named: " + no);
                }
                foreach (var t in tools.Keys)            // every family: a tool is refused unless somebody reviewed it as a read
                {
                    bool pass = L.Passes(t, L.DeclaredRead(tools[t]), "start");
                    if (pass && System.Text.RegularExpressions.Regex.IsMatch(t, "jawa/(set_|spawn_|destroy_|fire_|world_\\w+_set|pawn_force|\\w+_(set|add|remove|create|place|start|spawn)$)")) throw new Exception(t + " passes");
                }
                foreach (var a in new[] { "start", "", null }) Eq(L.Refuse("jawa/safe_advance", false, a, "r", false, log) != null, true, "jawa/safe_advance " + a);
                Eq(L.Refuse("jawa/spawn_pawn", false, null, null, false, log), null, "no run is live");
                Eq(L.Refuse("jawa/spawn_pawn", false, null, "r", true, log), null, "an act of the run itself");
                Eq(L.Refuse("jawa/a_tool_of_tomorrow", false, null, "r", false, log) != null, true, "a tool that nobody reviewed");
                Eq(L.DeclaredRead("READ ONLY. x") && L.DeclaredRead("Read-only: x") && !L.DeclaredRead("READ ONLYX") && !L.DeclaredRead("Sets. READ ONLY."), true, "DeclaredRead");
                Eq(L.Refuse("jawa/static_call", true, "Some.Type.Method", "r", false, log) != null, true, "jawa/static_call declared as a read");
                Eq(L.Refuse("jawa/static_call", false, "System.Environment.SetEnvironmentVariable", "r", false, log) != null, true, "a write of the process text");
                Eq(L.Refuse("jawa/static_call", false, "System.Environment.GetEnvironmentVariable", "r", false, log), null, "a read of the process text");
                Eq(log.Breaches()["jawa/spawn_pawn"], 1.0, "the log of refused calls");
                // on the run's own record
                var w = new World();
                var r = w.Make(At(1030));
                w.Start(r);
                w.Play(2);
                L.Refuse("jawa/spawn_pawn", false, null, r.Id, false, r.Lock);
                L.Refuse("jawa/spawn_pawn", false, null, r.Id, false, r.Lock);
                w.Play(10);
                Eq(w.One("close").GetProperty("breaches").GetProperty("jawa/spawn_pawn").GetDouble(), 2.0, "breaches on the close");
            });
            Check("a_read_tool_during_a_run_is_allowed_and_counted", () =>
            {
                foreach (var t in L.Reads.Concat(L.OwnCheck).Concat(L.ReadActions.Keys))
                    if (!tools.ContainsKey(t)) throw new Exception(t + " is on a list of the lock and is no tool of the companion");
                var w = new World();
                var r = w.Make(At(1030));
                w.Start(r);
                w.Play(2);
                foreach (var t in L.Reads) Eq(L.Refuse(t, false, null, r.Id, false, r.Lock), null, t);
                Eq(L.Refuse("jawa/map_info", L.DeclaredRead(tools["jawa/map_info"]), null, r.Id, false, r.Lock), null, "a tool declared READ ONLY");
                Eq(L.Refuse("jawa/safe_advance", false, "Status", r.Id, false, r.Lock), null, "a status");
                Eq(L.Refuse("jawa/scene_slice", false, "cancel", r.Id, false, r.Lock), null, "a cancel");
                Eq(L.Refuse("jawa/run_until", false, "status", r.Id, false, r.Lock), null, "the driver's poll");
                w.Play(10);
                Eq(w.One("close").GetProperty("lockReads").GetInt64(), (long)L.Reads.Count + 3, "reads on the close (a poll of the run is not a read)");
                Eq(w.One("close").GetProperty("breaches").EnumerateObject().Count(), 0, "breaches");
            });
            Check("a_cancelled_run_leaves_the_game_paused", () =>
            {
                var w = new World();
                var r = w.Make(At(1400), 500, 0, "PLAY", new T.Act("late", 100, () => "x"));
                w.Start(r);
                w.Play(5);
                long at = w.TickNow;
                r.Force("cancelled", "cancelled by a call", w.TickNow);
                Quiet(w, r);
                w.Play(10);
                Eq(w.TickNow, at, "tick after the cancel");
                Eq(w.PausedNow, true, "paused");
                Eq(Str(w.One("end"), "state"), "cancelled", "state");
                Eq(w.One("close").GetProperty("paused").GetBoolean(), true, "paused on the close");
                Eq(w.Rec("act").Count, 0, "acts after the cancel");
                r.Force("aborted", "again", w.TickNow);
                w.One("end");
                // the driver that died: its lease ends, the run is cancelled, the game paused, the closing record written
                var d = new World();
                d.Hands.Open("d", 5);
                d.Session("d", "q1", At(9000), 20000);
                d.Play(3);
                d.Clock += 6000;
                d.Play(4);
                Eq(d.PausedNow, true, "paused after the lease");
                Eq(Str(d.One("end"), "state"), "cancelled", "state after the lease");
                d.One("close");
                Eq(d.Hands.IsOpen, true, "the session is open");
            });
            Check("a_run_refused_for_no_player_control_changes_nothing", () =>
            {
                var w = new World { Control = false };
                w.Hands.Open("d", 600);
                int rows = w.Out.Count, pauses = w.Pauses;
                var r = w.Session("d", "q1", At(1300));
                Eq(r["refused"], "CANNOT_RUN", "refused");
                if (!((string)r["message"]).Contains("no control")) throw new Exception("the cause is not named: " + r["message"]);
                Eq(w.Out.Count, rows, "records");
                Eq(w.Pauses, pauses, "pauses");
                Eq(w.Goes, 0, "clock starts");
                Eq(w.Cur, null, "a run was armed");
                Eq(w.Hands.RunStatus("d", "q1")["refused"], "UNKNOWN_REQUEST", "the request id is not used up");
                w.Control = true;
                Eq(w.Session("d", "q1", At(1300))["success"], true, "the same request starts when control is back");
            });
            Console.WriteLine("U-count " + _n);
            return _bad == 0 ? 0 : 1;
        }
    }
}
