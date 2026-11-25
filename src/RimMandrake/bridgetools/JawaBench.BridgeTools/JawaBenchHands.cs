// JawaBenchHands.cs - the generic hands of BRIDGE v2.0: the Verse half of jawa/session, jawa/run_until, jawa/read_paths and
// jawa/act_batch. Item RIMMANDRAKE_WIDEN_SLICE_INTO_RUN_UNTIL_AND_ACT_BATCH. Page: design/specs/2026-11-23-bridge-v2-hands/boundary.md
// (the wire, the grammar, the promises). The rules are JawaBenchHandsCore.cs and JawaBenchPathCore.cs.
// Each hand is a plain public static method (main thread only) with a thin tool wrapper, so that a mod can call it in process.
// No Harmony patch is made here: the run is stepped by the ONE end-of-tick hook (JawaBenchVitals.TickPost), the session by its frame.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;
using C = JawaBench.BridgeTools.JawaBenchCondCore;
using H = JawaBench.BridgeTools.JawaBenchHandsCore;
using P = JawaBench.BridgeTools.JawaBenchPathCore;
using T = JawaBench.BridgeTools.JawaBenchSceneTickCore;
using W = JawaBench.BridgeTools.JawaBenchTpsWriter;

namespace JawaBench.BridgeTools
{
    public static class JawaBenchHands
    {
        private static readonly VerseHost Host = new VerseHost();
        private static readonly H.Hands Core = new H.Hands(Host);

        internal static bool Busy { get { return Core.Busy; } }
        internal static void Frame()
        {
            bool expired = Core.Cur != null && Core.Cur.LeaseEnded;
            Core.Frame();
            if (!expired && Core.Cur != null && Core.Cur.LeaseEnded)
                PutBackSettings();
        }

        private static string PutBackSettings() => JawaBenchDeviations.Record.Holder == Core.Cur.Driver
            ? JawaBenchDeviations.Revert(Core.Cur.Driver) : null;

        internal static bool SettingsSessionOpen => Core.IsOpen;

        internal static string SettingsDriver(string driver)
        {
            if (!SettingsSessionOpen) return null;
            var no = Core.Admit(driver);
            return no == null ? null : no["refused"] + ": " + no["message"];
        }
        internal static PathValue ReadValue(string of, string path) { return P.Read(Host, of, path); }
        /// <summary>The open session's id, or null (the force record names it: JawaBenchForce.cs).</summary>
        internal static string SessionId { get { return Core.Cur != null && Core.Cur.Stage == "open" ? Core.Cur.Id : null; } }
        /// <summary>A record of the open session's trace; -2 when no session is open.</summary>
        internal static long SessionRecord(string rec, string fields) { return Core.Record("force", rec, fields); }
        /// <summary>The thing bound to `alias` or `alias[n]` in this session, or null.</summary>
        internal static Thing BoundThing(string of) { return Host.BoundThing(of); }
        /// <summary>The context that runs a tool body inline, in this hop (as an act of a batch is run).</summary>
        internal static IRimBridgeContext InlineCtx { get { return OneHopTools.InlineContext.One; } }

        // ============================================================================================ the hands (main thread)
        /// <summary>open | state | bind | take | close | abort.</summary>
        public static Dictionary<string, object> Session(string action, string driver = null, double leaseS = H.DefaultLeaseS, string bindings = null, string from = null, string overlay = null)
        {
            switch ((action ?? "").Trim().ToLowerInvariant())
            {
                case "state":
                    var st = More(Core.State());
                    st["force"] = JawaBenchTerrainTools.ForceSummary(Core.Cur != null ? Core.Cur.Id : null);
                    return st;
                case "open":
                    if (!JawaBenchVitals.GameReady()) return H.Refusal("NO_GAME", "no game is playing", "load a map first");
                    if (!W.Running) return H.Refusal("CANNOT_RUN", "the disk writer is not running: no trace could be kept", "read jawa/tps_report");
                    string hook = JawaBenchVitals.EnsureTickHook();
                    if (hook != null) return H.Refusal("CANNOT_RUN", "the end-of-tick hook is not on: " + hook, "read jawa/vitals");
                    if (JawaBenchSceneTick.Cur != null && JawaBenchSceneTick.Cur.Stage != "closed") return H.Refusal("RUN_ACTIVE", "run " + JawaBenchSceneTick.Cur.Id + " is live", "jawa/scene_slice action=cancel");
                    if (JawaBenchDeviations.Record.Spoiled) return H.Refusal("SPOILED", "the deviation record could not put values back", "restart the game");
                    if (!Core.Busy) Host.Enter();
                    var opened = Core.Open(driver, leaseS);
                    if (Equals(opened["success"], true))
                    {
                        string error = JawaBenchDeviations.ApplyPlan(driver, overlay);
                        if (error != null)
                        {
                            Core.Finish(driver, true);
                            return H.Refusal("OVERLAY_REFUSED", error, "read the deviation record and correct the overlay");
                        }
                    }
                    return More(opened);
                case "bind": return More(Core.Bind(driver, bindings));
                case "take": return More(Core.Take(driver, from));
                case "close":
                case "abort":
                    var ended = Core.Finish(driver, action.Trim().Equals("abort", StringComparison.OrdinalIgnoreCase));
                    if (Equals(ended["success"], true))
                    {
                        string error = PutBackSettings();
                        if (error != null) ended["deviationError"] = error;
                    }
                    return More(ended);
            }
            return H.Refusal("BAD_ARGS", "action is open, state, bind, take, close or abort, not '" + action + "'", "correct it");
        }

        /// <summary>start | status | cancel.</summary>
        public static Dictionary<string, object> RunUntil(string action, string driver = null, string request = null, string until = null, int limit = 0,
                                                          string speed = "Normal", string record = null, string acts = null, double tickBudgetMs = 0,
                                                          string randState = null)
        {
            string a = (action ?? "").Trim().ToLowerInvariant();
            if (a == "status") return More(Core.RunStatus(driver, request));
            if (a == "cancel") return More(Core.Cancel(driver, request));
            if (a != "start") return H.Refusal("BAD_ARGS", "action is start, status or cancel, not '" + action + "'", "correct it");
            if (JawaBenchDeviations.Record.Spoiled) return H.Refusal("SPOILED", "the deviation record could not put values back", "restart the game");
            try
            {
                // STEP (RIMMANDRAKE_MEASURE_PLAY_AGAINST_PAUSED_STEP_NEVER_COMPARED): the game stays paused and the scene frame steps
                // DoSingleTick in slices, one slice per frame (JawaBenchSceneTick.StepFrame). The same run, trace and end-of-tick hook.
                bool step = string.Equals((speed ?? "").Trim(), "Step", StringComparison.OrdinalIgnoreCase);
                TimeSpeed sp = TimeSpeed.Paused;
                if (!step && (!Enum.TryParse(speed, true, out sp) || !Enum.IsDefined(typeof(TimeSpeed), sp) || sp == TimeSpeed.Paused))
                    return H.Refusal("BAD_ARGS", "speed is Normal, Fast, Superfast, Ultrafast or Step, not '" + speed + "'", "correct it");
                ulong rand = 0;
                bool writeRand = !string.IsNullOrWhiteSpace(randState);
                if (writeRand && !ulong.TryParse(randState.Trim(), NumberStyles.None, CultureInfo.InvariantCulture, out rand))
                    return H.Refusal("BAD_ARGS", "randState is the decimal Rand.StateCompressed, not '" + randState + "'", "send the `rand` of a run's open record");
                var list = H.ParseActs(acts, true);
                if (!(tickBudgetMs >= 0)) return H.Refusal("BAD_ARGS", "tickBudgetMs is less than 0", "0 is no budget");
                string spName = step ? "Step" : sp.ToString();
                var what = new List<object> { until, (double)limit, spName, record, acts };
                if (tickBudgetMs > 0) what.Add(tickBudgetMs);
                if (writeRand) what.Add(randState.Trim());
                string canon = C.Canon(what);
                string randWhy = null;
                bool randTried = false;
                var reply = Core.StartRun(driver, request, canon, list, limit, (id, ticks, trace) =>
                {
                    var plan = H.MakePlan(until, record, limit, Host.MapId, Core.GroupSize);
                    var src = JawaBenchTerrainTools.NewProbeSource();
                    var made = new T.SceneRun(id, plan.Compile(src), src, ticks, Host, step ? "STEP" : "PLAY", spName, trace, tickBudgetMs);
                    JawaBenchCast.Join(made, Host.CastPawns(Core.GroupSize));       // the standard cast tracks of every bound pawn
                    JawaBenchWorld.Join(made, Host.MapId);                          // the world tracks of the run's map, and the world-event taps
                    return made;
                }, JawaBenchSceneTick.EpochBox(), run =>
                {
                    // the write-back is in the arming hop, just before the open record reads the state: no frame draws between them
                    if (writeRand) { randTried = true; randWhy = JawaBenchSceneTick.WriteRand(rand); }
                    Armed(run);
                }, () =>
                {
                    if (step) JawaBenchSceneTick.StepRun = JawaBenchSceneTick.Cur;
                    else Find.TickManager.CurTimeSpeed = sp;
                });
                if (randTried) { reply["randWritten"] = randWhy == null; if (randWhy != null) reply["randWhy"] = randWhy; }
                return More(reply);
            }
            catch (H.Refused e) { return H.Refusal(e); }
            catch (CondRefused e) { return H.Refusal(e); }
        }

        private static void Armed(T.SceneRun run)
        {
            JawaBenchSceneTick.Take(run, Host.TheMap());
        }

        /// <summary>Many value paths on one tick. Changes nothing.</summary>
        public static Dictionary<string, object> ReadPaths(string reads = null, string rect = null, string path = null, string of = "map")
        {
            if (Current.Game == null || Find.Maps == null) return H.Refusal("NO_GAME", "no game is loaded", "load a map first");
            var want = new List<KeyValuePair<string, string>>();
            if (!string.IsNullOrWhiteSpace(reads))
            {
                List<object> l;
                try { l = C.ParseJson(reads) as List<object>; } catch (Exception) { l = null; }
                if (l == null) return H.Refusal("BAD_ARGS", "reads is not a JSON list", "send [{\"of\": target, \"path\": path}, ...]");
                foreach (var o in l)
                {
                    var d = o as Dictionary<string, object>;
                    object t = null, p = null;
                    if (d != null) { d.TryGetValue("of", out t); d.TryGetValue("path", out p); }
                    if (d == null || d.Count != 2 || !(t is string) || !(p is string)) return H.Refusal("BAD_ARGS", "a read is not {of, path}: " + C.Canon(o), "correct it");
                    want.Add(new KeyValuePair<string, string>((string)t, (string)p));
                }
            }
            if (!string.IsNullOrWhiteSpace(rect))
            {
                string why = RectReads(rect, path, of, want);
                if (why != null) return H.Refusal("BAD_ARGS", why, "rect is x,z,w,h on the map, with path");
            }
            else if (!string.IsNullOrWhiteSpace(path)) want.Add(new KeyValuePair<string, string>(of, path));
            if (want.Count == 0 && string.IsNullOrWhiteSpace(rect)) return H.Refusal("BAD_ARGS", "nothing to read", "give reads, or path, or rect and path");
            var values = new List<object>();
            foreach (var kv in want)
            {
                var r = P.Read(Host, kv.Key, kv.Value);
                if (r.Refused != null) return H.Refusal(r.Refused, "'" + kv.Key + "' '" + kv.Value + "': " + r.Detail, "a step is a field, a reviewed property, comp<Class> or [n]");
                var v = new Dictionary<string, object> { { "of", kv.Key }, { "path", kv.Value }, { "state", r.State }, { "v", r.V } };
                if (r.State != "ok") v["detail"] = r.Detail;
                values.Add(v);
            }
            return new Dictionary<string, object> { { "success", true }, { "tick", Find.TickManager.TicksGame }, { "paused", Find.TickManager.Paused }, { "values", values } };
        }

        private static string RectReads(string rect, string path, string of, List<KeyValuePair<string, string>> want)
        {
            var map = Host.TheMap();
            if (map == null) return "no map";
            if (string.IsNullOrWhiteSpace(path)) return "rect with no path";
            var p = rect.Split(',');
            var n = new int[4];
            if (p.Length != 4) return "rect '" + rect + "' is not x,z,w,h";
            for (int i = 0; i < 4; i++) if (!int.TryParse(p[i].Trim(), NumberStyles.Integer, CultureInfo.InvariantCulture, out n[i])) return "rect '" + rect + "' is not x,z,w,h";
            if (n[0] < 0 || n[1] < 0 || n[2] < 1 || n[3] < 1 || n[0] + n[2] > map.Size.x || n[1] + n[3] > map.Size.z) return "rect '" + rect + "' is not on the map of " + map.Size.x + "x" + map.Size.z;
            bool cells = path.IndexOf("[cell]", StringComparison.Ordinal) >= 0;
            for (int z = n[1]; z < n[1] + n[3]; z++)
                for (int x = n[0]; x < n[0] + n[2]; x++)
                {
                    if (cells) { want.Add(new KeyValuePair<string, string>(of, path.Replace("[cell]", "[" + x + "," + z + "]"))); continue; }
                    var l = map.thingGrid.ThingsListAtFast(new IntVec3(x, 0, z));
                    for (int i = 0; i < l.Count; i++)
                        if (l[i].Position.x == x && l[i].Position.z == z) want.Add(new KeyValuePair<string, string>("thing:" + l[i].ThingID, path));
                }
            return null;
        }

        /// <summary>Several acts, now, with no frame between them.</summary>
        public static Dictionary<string, object> ActBatch(string driver, string acts)
        {
            try { return More(Core.Batch(driver, H.ParseActs(acts, false))); }
            catch (H.Refused e) { return H.Refusal(e); }
        }

        private static Dictionary<string, object> More(Dictionary<string, object> d)
        {
            d["ticksGame"] = Current.Game != null && Find.TickManager != null ? Find.TickManager.TicksGame : -1;
            if (!d.ContainsKey("paused")) d["paused"] = Host.Paused();
            d["recordDir"] = W.Dir; d["writerSession"] = W.Session; d["lastFault"] = JawaBenchSceneTick.LastFault;
            d["maxFrameTicks"] = JawaBenchSceneTick.MaxFrameTicks;
            d["deviation"] = JawaBenchDeviations.Record.Receipt();
            return d;
        }

        /// <summary>How many of this companion's tools a batch can take, by name. Changes nothing.</summary>
        internal static Dictionary<string, object> BatchCensus()
        {
            var wait = new List<string>();
            var cond = new List<string>();
            int n = 0;
            foreach (var kv in Host.Tools())
            {
                n++;
                string w = OneHopTools.WhyWaits(kv.Value);
                if (w == null) continue;
                if (OneHopTools.WaitArg.ContainsKey(kv.Key)) cond.Add(kv.Key); else wait.Add(kv.Key);
            }
            return new Dictionary<string, object> { { "success", true }, { "tools", n }, { "notOneHop", wait }, { "oneHopWithNoWait", cond } };
        }

        // ============================================================================================ the game
        private sealed class VerseHost : IHandsHost, IPathHost
        {
            private readonly JawaBenchSceneTick.Host _scene = new JawaBenchSceneTick.Host();
            private readonly Dictionary<string, Thing[]> _bound = new Dictionary<string, Thing[]>(StringComparer.Ordinal);
            private readonly Dictionary<string, Thing> _byId = new Dictionary<string, Thing>(StringComparer.Ordinal);
            private Game _game;                     // the game the bound things are of
            internal int MapId = -1;

            internal void Enter()
            {
                _game = Current.Game;
                JawaBenchSceneTick.RunGame = _game;
                _bound.Clear();
                _byId.Clear();
                MapId = Find.CurrentMap != null ? Find.CurrentMap.uniqueID : -1;
            }

            internal Map TheMap()
            {
                if (Core.Busy) return VerseProbeSource.MapById(MapId);
                return Current.Game != null ? Find.CurrentMap : null;
            }

            // ---- ISceneHost
            public long Enqueue(string fields) { return _scene.Enqueue(fields); }
            public bool Drained() { return _scene.Drained(); }
            public bool Pause() { return _scene.Pause(); }
            public long Tick() { return _scene.Tick(); }
            public ulong RandState() { return _scene.RandState(); }
            public double NowMs() { return _scene.NowMs(); }
            public long? AllocBytes() { return _scene.AllocBytes(); }

            // ---- IHandsHost
            public int Frame() { return Time.frameCount; }
            public bool Paused() { return Current.Game != null && Find.TickManager != null && Find.TickManager.Paused; }
            public string RefuseRun()
            {
                if (!JawaBenchSceneTick.SameGame()) return "CANNOT_RUN: the game was replaced since the session was opened";
                string hook = JawaBenchVitals.EnsureTickHook();
                string why = hook != null ? "the end-of-tick hook is not on: " + hook : JawaBenchSceneTick.Refuse();
                return why == null ? null : "CANNOT_RUN: " + why;
            }

            public bool Bind(string alias, int member, string id)
            {
                var t = JawaBenchTerrainTools.HandsFindThing(id);
                if (t == null) return false;
                if (alias == null) return true;
                Thing[] a;
                _bound.TryGetValue(alias, out a);
                int n = Math.Max(member, 0);
                if (a == null || a.Length <= n) { Array.Resize(ref a, n + 1); _bound[alias] = a; }
                a[n] = t;
                return true;
            }

            public void Unbind(string alias) { _bound.Remove(alias); }

            internal Thing BoundThing(string of)
            {
                if (string.IsNullOrEmpty(of) || !Core.Busy) return null;
                int i = of.IndexOf('[');
                string alias = i < 0 ? of : of.Substring(0, i);
                int n = 0;
                if (i >= 0 && (!of.EndsWith("]", StringComparison.Ordinal) || !int.TryParse(of.Substring(i + 1, of.Length - i - 2), NumberStyles.None, CultureInfo.InvariantCulture, out n))) return null;
                Thing[] a;
                if (!_bound.TryGetValue(alias, out a) || n >= a.Length) return null;
                return a[n];
            }

            /// <summary>The cast of a run: every bound pawn, named by its alias, or `alias[i]` in a group.</summary>
            internal List<KeyValuePair<string, Thing>> CastPawns(Func<string, int> sizeOf)
            {
                var l = new List<KeyValuePair<string, Thing>>();
                foreach (var kv in _bound)
                {
                    int n = sizeOf(kv.Key);
                    for (int i = 0; i < kv.Value.Length; i++)
                        if (kv.Value[i] is Pawn)
                            l.Add(new KeyValuePair<string, Thing>(n > 0 ? kv.Key + "[" + i.ToString(CultureInfo.InvariantCulture) + "]" : kv.Key, kv.Value[i]));
                }
                l.Sort((a, b) => string.CompareOrdinal(a.Key, b.Key));
                return l;
            }

            private Dictionary<string, MethodInfo> _tools;
            internal Dictionary<string, MethodInfo> Tools()
            {
                if (_tools == null) _tools = OneHopTools.Scan();
                return _tools;
            }

            public string RefuseAct(string tool, Dictionary<string, object> args)
            {
                if (OneHopTools.Nested.Contains(tool)) return "NESTED_HAND: " + tool + " cannot be an act";
                MethodInfo m;
                if (!Tools().TryGetValue(tool, out m)) return "UNKNOWN_TOOL: " + tool + " is not a tool of this companion (a rimworld/ tool goes through the host's own queue)";
                string why = JawaBenchCompanionSafety.CheckReserved(args);
                if (why != null) return "BAD_ARGS: " + why;
                object[] bound;
                why = OneHopTools.BindArgs(m, args, out bound);
                if (why != null) return "BAD_ARGS: " + why;
                why = OneHopTools.WhyWaits(m);
                if (why == null) return null;
                string arg;
                if (!OneHopTools.WaitArg.TryGetValue(tool, out arg)) return "NOT_ONE_HOP: " + tool + " waits inside its body (" + why + ")";
                object v;
                if (args.TryGetValue(arg, out v) && C.IsNum(v) && C.Num(v) == 0) return null;
                return "NOT_ONE_HOP: " + tool + " waits inside its body unless " + arg + " is 0";
            }

            public ActOutcome Act(string tool, Dictionary<string, object> args)
            {
                var m = Tools()[tool];
                object[] bound;
                string why = OneHopTools.BindArgs(m, args, out bound);
                if (why != null) return new ActOutcome { State = "failed", Error = why };
                object r;
                JawaBenchSceneTick.InsideAct++;
                try { r = m.Invoke(null, bound); }
                catch (TargetInvocationException e) { var x = e.InnerException ?? e; return new ActOutcome { State = "failed", Error = x.GetType().Name + ": " + x.Message }; }
                finally { JawaBenchSceneTick.InsideAct--; }
                var task = r as Task;
                if (task != null)
                {
                    if (!task.IsCompleted)
                    {
                        task.ContinueWith(OneHopTools.Observe, TaskContinuationOptions.OnlyOnFaulted);
                        return new ActOutcome { State = "not_one_hop", Error = "the tool did not end inside the hop; what it did after is not known" };
                    }
                    if (task.IsFaulted || task.IsCanceled)
                    {
                        Exception x = task.Exception == null ? null : task.Exception.GetBaseException();
                        return new ActOutcome { State = "failed", Error = x == null ? "cancelled" : x.GetType().Name + ": " + x.Message };
                    }
                    var t = task as Task<object>;
                    r = t != null ? t.Result : null;
                }
                string err;
                return new ActOutcome { State = OneHopTools.SaidNo(r, out err) ? "refused" : "done", Reply = r, Error = err };
            }

            // ---- IPathHost
            public bool Root(string of, out object root, out Type staticOf, out PathValue bad)
            {
                root = null; staticOf = null; bad = default(PathValue);
                if (string.IsNullOrEmpty(of)) { bad = PathValue.No(P.BadPath, "the target is empty"); return false; }
                if (Current.Game == null) { bad = PathValue.Bad("gone", "no game is loaded"); return false; }
                if (of == "game") root = Current.Game;
                else if (of == "world") { root = Find.World; if (root == null) bad = PathValue.Bad("gone", "no world"); }
                else if (of == "map") { root = TheMap(); if (root == null) bad = PathValue.Bad("gone", "map " + MapId + " is gone"); }
                else if (of.StartsWith("static:", StringComparison.Ordinal))
                {
                    staticOf = TypeOf(of.Substring(7));
                    if (staticOf == null) bad = PathValue.Bad("error", "no type '" + of.Substring(7) + "' is loaded");
                    return staticOf != null;
                }
                else if (of.StartsWith("def:", StringComparison.Ordinal))
                {
                    int s = of.IndexOf('/');
                    var ty = s < 0 ? null : GenTypes.GetTypeInAnyAssembly(of.Substring(4, s - 4));
                    if (s < 0) bad = PathValue.No(P.BadPath, "'" + of + "': want def:<DefType>/<defName>");
                    else if (ty == null || !typeof(Def).IsAssignableFrom(ty)) bad = PathValue.Bad("error", "no DefType '" + of.Substring(4, s - 4) + "'");
                    else
                    {
                        root = GenDefDatabase.GetDefSilentFail(ty, of.Substring(s + 1), false);
                        if (root == null) bad = PathValue.Bad("error", "no " + ty.Name + " named '" + of.Substring(s + 1) + "'");
                    }
                }
                else if (of.StartsWith("thing:", StringComparison.Ordinal))
                {
                    string id = of.Substring(6);
                    if (!ReferenceEquals(_game, Current.Game) && !Core.Busy) { _game = Current.Game; _byId.Clear(); _bound.Clear(); }
                    Thing t;
                    if (!_byId.TryGetValue(id, out t))
                    {
                        t = JawaBenchTerrainTools.HandsFindThing(id);
                        if (t != null) _byId[id] = t;
                    }
                    if (t == null) bad = PathValue.Bad("unbound", "no thing '" + id + "' was found");
                    else Live(t, out root, out bad);
                }
                else if (of.IndexOf(':') >= 0) bad = PathValue.No(P.BadPath, "target '" + of + "' is of no known kind");
                else
                {
                    int i = of.IndexOf('[');
                    string alias = i < 0 ? of : of.Substring(0, i);
                    int n = 0;
                    Thing[] a;
                    if (i >= 0 && (!of.EndsWith("]", StringComparison.Ordinal) || !int.TryParse(of.Substring(i + 1, of.Length - i - 2), NumberStyles.None, CultureInfo.InvariantCulture, out n)))
                        bad = PathValue.No(P.BadPath, "target '" + of + "': want alias or alias[n]");
                    else if (!_bound.TryGetValue(alias, out a) || n >= a.Length || a[n] == null) bad = PathValue.Bad("unbound", "'" + of + "' is bound to nothing");
                    else if (i < 0 && Core.GroupSize(alias) >= 0) bad = PathValue.No(P.BadPath, "'" + alias + "' is a group: name a member, " + alias + "[0]");
                    else Live(a[n], out root, out bad);
                }
                return root != null;
            }

            private readonly Dictionary<string, Type> _types = new Dictionary<string, Type>(StringComparer.Ordinal);

            /// <summary>A type by name: the game's and the mods' first (GenTypes searches only those), then every loaded assembly, for
            /// an engine or a companion type. Null is not kept: an assembly may be loaded later.</summary>
            private Type TypeOf(string name)
            {
                Type t;
                if (_types.TryGetValue(name, out t)) return t;
                t = GenTypes.GetTypeInAnyAssembly(name);
                if (t == null)
                    foreach (var a in AppDomain.CurrentDomain.GetAssemblies())
                    {
                        try { t = a.GetType(name, false); } catch (Exception) { t = null; }
                        if (t != null) break;
                    }
                if (t != null) _types[name] = t;
                return t;
            }

            /// <summary>The thing, or gone with its cause: dead, destroyed, left the map, of another game.</summary>
            private void Live(Thing t, out object root, out PathValue bad)
            {
                root = null;
                bad = default(PathValue);
                var p = t as Pawn;
                if (!ReferenceEquals(_game, Current.Game)) bad = PathValue.Bad("gone", "the game was replaced");
                else if (t.Destroyed) bad = PathValue.Bad("gone", p != null && p.Dead ? "dead" : "destroyed");
                else if (p != null && p.Dead) bad = PathValue.Bad("gone", "dead");
                else if (!t.SpawnedOrAnyParentSpawned) bad = PathValue.Bad("gone", "left the map");
                else root = t;
            }

            public object Comp(object owner, string cls, out string why)
            {
                why = null;
                System.Collections.IList l = null;
                var tc = owner as ThingWithComps;
                if (tc != null) l = tc.AllComps;
                else if (owner is Map) l = ((Map)owner).components;
                else if (owner is Game) l = ((Game)owner).components;
                else if (owner is World) l = ((World)owner).components;
                else if (owner is HediffWithComps) l = ((HediffWithComps)owner).comps;
                if (l == null) { why = owner.GetType().FullName + " has no comps"; return null; }
                var names = new List<string>();
                foreach (var c in l)
                {
                    if (c == null) continue;
                    for (var ty = c.GetType(); ty != null && ty != typeof(object); ty = ty.BaseType)
                        if (ty.Name == cls || ty.FullName == cls) return c;
                    names.Add(c.GetType().Name);
                }
                why = "no comp of class '" + cls + "'; it has: " + string.Join(", ", names.ToArray());
                return null;
            }

            public object Leaf(object v, out bool known)
            {
                known = true;
                var d = v as Def; if (d != null) return d.defName;
                var t = v as Thing; if (t != null) return t.ThingID;
                if (v is IntVec3) { var c = (IntVec3)v; return c.x.ToString(CultureInfo.InvariantCulture) + "," + c.z.ToString(CultureInfo.InvariantCulture); }
                if (v is Rot4) return (double)((Rot4)v).AsInt;
                if (v is Vector3) { var f = (Vector3)v; return Num(f.x) + "," + Num(f.y) + "," + Num(f.z); }
                if (v is Vector2) { var f = (Vector2)v; return Num(f.x) + "," + Num(f.y); }
                if (v is Color) { var f = (Color)v; return Num(f.r) + "," + Num(f.g) + "," + Num(f.b) + "," + Num(f.a); }
                if (v is TaggedString) return ((TaggedString)v).RawText;
                var m = v as Map; if (m != null) return "Map_" + m.uniqueID.ToString(CultureInfo.InvariantCulture);
                var fa = v as Faction; if (fa != null) return "Faction_" + fa.loadID.ToString(CultureInfo.InvariantCulture);
                var ty = v as Type; if (ty != null) return ty.FullName;
                known = false;
                return null;
            }

            private static string Num(float f) { return ((double)f).ToString("R", CultureInfo.InvariantCulture); }

            public int CellIndex(int x, int z, int length, out string why)
            {
                why = null;
                var m = TheMap();
                if (m == null) { why = "no map"; return -1; }
                if (x < 0 || z < 0 || x >= m.Size.x || z >= m.Size.z) { why = x + "," + z + " is outside " + m.Size.x + "x" + m.Size.z; return -1; }
                if (length != m.Size.x * m.Size.z) { why = "the list holds " + length + ", the map " + m.Size.x * m.Size.z + " cells"; return -1; }
                return z * m.Size.x + x;
            }
        }
    }

    /// <summary>A tool body called inside one main-thread hop: its arguments, its context, and whether it can end there.</summary>
    internal static class OneHopTools
    {
        internal static readonly HashSet<string> Nested = new HashSet<string>(StringComparer.Ordinal)
        { "jawa/session", "jawa/run_until", "jawa/act_batch", "jawa/scene_slice", "jawa/run_scenes", "jawa/safe_advance" };

        // a tool whose only wait is a loop that this argument turns off
        internal static readonly Dictionary<string, string> WaitArg = new Dictionary<string, string>(StringComparer.Ordinal)
        { { "jawa/ordered_job", "waitTicks" }, { "jawa/order_pawn", "waitTicks" }, { "jawa/prioritized_work", "waitTicks" }, { "jawa/do_bill_now", "waitTicks" }, { "jawa/pawn_flight", "maintainTicks" } };

        internal static Dictionary<string, MethodInfo> Scan()
        {
            var d = new Dictionary<string, MethodInfo>(StringComparer.Ordinal);
            Type[] types;
            try { types = typeof(OneHopTools).Assembly.GetTypes(); }
            catch (ReflectionTypeLoadException e) { types = e.Types; }
            foreach (var t in types)
            {
                if (t == null) continue;
                MethodInfo[] ms;
                try { ms = t.GetMethods(BindingFlags.Public | BindingFlags.Static | BindingFlags.DeclaredOnly); } catch (Exception) { continue; }
                foreach (var m in ms)
                {
                    ToolAttribute a;
                    try { a = m.GetCustomAttribute<ToolAttribute>(false); } catch (Exception) { continue; }
                    if (a != null) d[a.Name] = m;
                }
            }
            return d;
        }

        private static readonly Dictionary<MethodBase, string> Waits = new Dictionary<MethodBase, string>();

        /// <summary>Null when the body ends in the hop it starts in, else the call that waits. Read from the IL of the body, of
        /// its state machine and of each async helper of this assembly that it calls.</summary>
        internal static string WhyWaits(MethodInfo m)
        {
            string w;
            if (Waits.TryGetValue(m, out w)) return w;
            w = Waiting(m, new HashSet<MethodBase>());
            Waits[m] = w;
            return w;
        }

        private static string Waiting(MethodBase m, HashSet<MethodBase> seen)
        {
            if (!seen.Add(m)) return null;
            var body = m;
            var sm = m.GetCustomAttribute<System.Runtime.CompilerServices.AsyncStateMachineAttribute>();
            if (sm != null) body = sm.StateMachineType.GetMethod("MoveNext", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public);
            byte[] il;
            try { var b = body.GetMethodBody(); il = b == null ? null : b.GetILAsByteArray(); } catch (Exception e) { return "its body could not be read (" + e.GetType().Name + ")"; }
            if (il == null) return "its body could not be read";
            Type[] ga = body.DeclaringType.IsGenericType ? body.DeclaringType.GetGenericArguments() : null;
            for (int i = 0; i + 5 <= il.Length; i++)
            {
                if (il[i] != 0x28 && il[i] != 0x6F && il[i] != 0x73) continue;          // call, callvirt, newobj
                MethodBase c;
                try { c = body.Module.ResolveMethod(BitConverter.ToInt32(il, i + 1), ga, null); } catch (Exception) { continue; }
                var t = c.DeclaringType;
                if (t == null) continue;
                if (t == typeof(Task) && (c.Name == "Delay" || c.Name == "Run" || c.Name == "WhenAny" || c.Name == "WhenAll" || c.Name == "Yield")) return "Task." + c.Name;
                if (t == typeof(IRimBridgeGameClock) || t == typeof(IRimBridgeToolClient)) return t.Name + "." + c.Name;
                if (t.IsGenericType && t.GetGenericTypeDefinition() == typeof(TaskCompletionSource<>)) return "TaskCompletionSource";
                var mi = c as MethodInfo;
                if (mi != null && t.Assembly == typeof(OneHopTools).Assembly && typeof(Task).IsAssignableFrom(mi.ReturnType))
                {
                    string deeper = Waiting(c, seen);
                    if (deeper != null) return mi.Name + " -> " + deeper;
                }
            }
            return null;
        }

        /// <summary>The arguments as the tool declares them, or why not. An undeclared key is refused, as the binder does it.</summary>
        internal static string BindArgs(MethodInfo m, Dictionary<string, object> args, out object[] bound)
        {
            var ps = m.GetParameters();
            bound = new object[ps.Length];
            var left = new HashSet<string>(args.Keys, StringComparer.OrdinalIgnoreCase);
            foreach (var r in JawaBenchSafetyCore.ReservedArgs) left.Remove(r);
            for (int i = 0; i < ps.Length; i++)
            {
                var p = ps[i];
                if (typeof(IRimBridgeContext).IsAssignableFrom(p.ParameterType)) { bound[i] = InlineContext.One; continue; }
                if (p.ParameterType == typeof(CancellationToken)) { bound[i] = CancellationToken.None; continue; }
                object v = null;
                bool has = false;
                foreach (var kv in args) if (string.Equals(kv.Key, p.Name, StringComparison.OrdinalIgnoreCase)) { v = kv.Value; has = true; }
                left.Remove(p.Name);
                if (!has)
                {
                    if (p.HasDefaultValue) { bound[i] = p.DefaultValue; continue; }
                    var pa = p.GetCustomAttribute<ToolParameterAttribute>(false);       // the host fills a default that only the attribute gives
                    if (pa == null || pa.DefaultValue == null) return "argument '" + p.Name + "' is missing";
                    string bad = Convert1(pa.DefaultValue is string || pa.DefaultValue is bool ? pa.DefaultValue : (object)System.Convert.ToDouble(pa.DefaultValue, CultureInfo.InvariantCulture), p.ParameterType, out bound[i]);
                    if (bad != null) return "argument '" + p.Name + "' is missing and its default is not usable: " + bad;
                    continue;
                }
                string why = Convert1(v, p.ParameterType, out bound[i]);
                if (why != null) return "argument '" + p.Name + "': " + why;
            }
            if (left.Count > 0) return m.Name + " does not declare " + string.Join(", ", new List<string>(left).ToArray());
            return null;
        }

        private static string Convert1(object v, Type want, out object got)
        {
            got = null;
            var t = Nullable.GetUnderlyingType(want) ?? want;
            if (v == null) { if (want.IsValueType && t == want) return "null for " + want.Name; return null; }
            if (t.IsInstanceOfType(v)) { got = v; return null; }
            try
            {
                if (t == typeof(string)) { got = v is bool ? ((bool)v ? "true" : "false") : C.Canon(v); return null; }
                if (t.IsEnum && v is string) { got = Enum.Parse(t, (string)v, true); return null; }
                if (C.IsNum(v) && t != typeof(bool))
                {
                    double d = C.Num(v);
                    if ((t == typeof(int) || t == typeof(long) || t == typeof(short) || t == typeof(byte)) && d != Math.Floor(d)) return "want a whole number, got " + d.ToString(CultureInfo.InvariantCulture);
                    got = Convert.ChangeType(d, t, CultureInfo.InvariantCulture);
                    return null;
                }
                if (v is string && t.IsPrimitive) { got = Convert.ChangeType(v, t, CultureInfo.InvariantCulture); return null; }
                var l = v as List<object>;
                if (l != null && (t.IsArray || (t.IsGenericType && t.GetGenericArguments().Length == 1)))
                {
                    var et = t.IsArray ? t.GetElementType() : t.GetGenericArguments()[0];
                    var arr = Array.CreateInstance(et, l.Count);
                    for (int i = 0; i < l.Count; i++)
                    {
                        object one;
                        string why = Convert1(l[i], et, out one);
                        if (why != null) return "[" + i + "] " + why;
                        arr.SetValue(one, i);
                    }
                    if (t.IsArray || t.IsInstanceOfType(arr)) { got = arr; return null; }
                    got = Activator.CreateInstance(t, arr);
                    return null;
                }
            }
            catch (Exception e) { return e.GetType().Name + ": " + e.Message; }
            return "want " + t.Name + ", got " + v.GetType().Name;
        }

        /// <summary>The tool's own reply says that it did not do it.</summary>
        internal static bool SaidNo(object r, out string error)
        {
            error = null;
            if (r == null) return false;
            object s = Get(r, "success");
            if (!(s is bool) || (bool)s) return false;
            error = (Get(r, "message") ?? Get(r, "error") ?? "the tool answered success false").ToString();
            return true;
        }

        private static object Get(object r, string name)
        {
            var d = r as IDictionary<string, object>;
            object v;
            if (d != null) return d.TryGetValue(name, out v) ? v : null;
            var p = r.GetType().GetProperty(name);
            return p == null ? null : p.GetValue(r, null);
        }

        internal static void Observe(Task t) { var _ = t.Exception; }

        /// <summary>The context of a tool body inside a hop. There is no other queue to go to, so the body ends where it starts.</summary>
        internal sealed class InlineContext : IRimBridgeContext
        {
            internal static readonly InlineContext One = new InlineContext();
            private readonly InlineMainThread _main = new InlineMainThread();
            public string OperationId { get { return "act_batch"; } }
            public string CapabilityId { get { return "act_batch"; } }
            public IRimBridgeToolClient Tools { get { throw new NotSupportedException("an act inside a hop cannot call through the bridge host"); } }
            public IRimBridgeGameClock Game { get { throw new NotSupportedException("an act inside a hop cannot wait for a frame"); } }
            public IRimBridgeMainThread MainThread { get { return _main; } }
        }

        private sealed class InlineMainThread : IRimBridgeMainThread
        {
            public bool IsMainThread { get { return true; } }
            public Task<TR> InvokeAsync<TR>(Func<TR> func, CancellationToken cancellationToken = default(CancellationToken))
            {
                try { return Task.FromResult(func()); } catch (Exception e) { return Task.FromException<TR>(e); }
            }
            public Task InvokeAsync(Action action, CancellationToken cancellationToken = default(CancellationToken))
            {
                try { action(); return Task.CompletedTask; } catch (Exception e) { return Task.FromException(e); }
            }
        }
    }

    public sealed partial class JawaBenchTerrainTools
    {
        internal static Thing HandsFindThing(string id)
        {
            string e;
            return (Thing)FindPawn(id, out e) ?? SystemToolsFindThing(id, out e) ?? FindThingIncludingContainers(id, out e);
        }

        [Tool(
            "jawa/session",
            Description =
                "The one session of this game process (BRIDGE v2.0, design/specs/2026-11-23-bridge-v2-hands/boundary.md): one driver, one " +
                "trace over several runs and batches, request ids. action=open pauses the game. action=state reads, for anyone. " +
                "action=bind binds aliases to thing ids ({\"pawn_1\": \"Human12\", \"raiders\": [\"Human3\", \"Human4\"]}); a list is a frozen group. " +
                "action=close | abort writes the closing record after the trace has drained (poll state until stage is closed or aborted). " +
                "When the driver's lease ends with no call from it, the game is paused and the session stays open; then abort takes any caller. " +
                "action=take gives the session of a dead driver to a new one (the live run is cancelled, the game paused): it may then be read and " +
                "ended, not played.",
            ResultDescription =
                "success, session, stage (none | open | closing | closed | aborted), driver, leaseEnded, leaseLeftS, paused, tick, lastRun, openAct, " +
                "bound, rows, dropped, recordDir, writerSession. A refusal: success false, refused (name), message, repair; nothing was changed.")]
        public static async Task<object> HandsSession(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "open, state, bind, take, close or abort.")] string action = "state",
            [ToolParameter(Description = "The caller's own name; the same text on each call.")] string driver = null,
            [ToolParameter(Description = "open: seconds without a call from the driver after which the game is paused.")] double leaseS = 600,
            [ToolParameter(Description = "bind: a JSON object alias -> thing id, or a list of ids (a frozen group), or null (not bound).")] string bindings = null,
            [ToolParameter(Description = "take: the text of the dead driver, as action=state says it. Not needed after its lease has ended.")] string from = null,
            [ToolParameter(Description = "open: none to require a clean game, or a JSON object with name and ordered settings entries.")] string overlay = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                return JawaBenchHands.Session(action, driver, leaseS, bindings, from, overlay);
            }, cancellationToken);
        }

        [Tool(
            "jawa/run_until",
            Description =
                "Let the game play in its OWN loop until a condition is true at the end of a tick, or `limit` ticks; it stops and is paused ON that " +
                "tick. Records each named value path on every tick, on change, in the session's trace (schema scene_trace_v1, kind `scene`). JUDGES " +
                "NOTHING. Needs an open jawa/session and a paused game. action=start returns at once; action=status (by request id) reads, and " +
                "renews the lease when the driver asks; action=cancel ends it. A repeat of a request id with the same arguments answers the first run. until: a jawa/cond_eval tree, plus probes " +
                "value / value.state {of, path} and nodes any_of / all_of {group, node}. An unreadable value of the condition ends the run as " +
                "`unknown`, never false. acts: any one-hop jawa tool call, at 0 (in the hop that starts the clock, so no paused frame sees it) or on " +
                "tick N after the start. Grammar and refusals: design/specs/2026-11-23-bridge-v2-hands/boundary.md. TEST profile only.",
            ResultDescription =
                "success, request, run, stage (running | settling | closed), why (hit | limit | unknown | cancelled | fault; null while it runs), state, " +
                "tickFrom, tick, hitTick, values (name -> state, v, detail), couldNotLook, unknownValue, faults, acts, rows, dropped, drained, replayed, cost. " +
                "A refusal: success false, refused (name), message, repair; nothing was changed.")]
        public static async Task<object> HandsRunUntil(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "start, status or cancel.")] string action = "status",
            [ToolParameter(Description = "The session's driver.")] string driver = null,
            [ToolParameter(Description = "The request id, made by the caller before it sends the call.")] string request = null,
            [ToolParameter(Description = "start: the stop condition, a JSON condition node.")] string until = null,
            [ToolParameter(Description = "start: the most ticks to play, at least 1.")] int limit = 0,
            [ToolParameter(Description = "start: Normal, Fast, Superfast or Ultrafast (the game's own loop), or Step (paused; the companion steps the tick in slices, once a frame).")] string speed = "Normal",
            [ToolParameter(Description = "start: a JSON list of {of, path} or {name, probe}: more values to record.")] string record = null,
            [ToolParameter(Description = "start: a JSON list of {id, tool, args, at}: acts in the starting hop (at 0) or on a tick (at N).")] string acts = null,
            [ToolParameter(Description = "start: the most ms that reading one tick (tracks and condition) may take; over it the run ends in state budget and names the costliest value. 0 = no bound.")] double tickBudgetMs = 0,
            [ToolParameter(Description = "start: a decimal Rand.StateCompressed to write back at arm, in the arming hop (the `rand` of an earlier run's open record); the reply says randWritten. Empty = none.")] string randState = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                return JawaBenchHands.RunUntil(action, driver, request, until, limit, speed, record, acts, tickBudgetMs, randState);
            }, cancellationToken);
        }

        [Tool(
            "jawa/read_paths",
            Description =
                "READ-ONLY. Many value paths in one call, on one tick: public and PRIVATE fields, statics of a mod (static:Full.Type), def values " +
                "(def:ThingDef/Wall), comps by class (comp<Class>), list indexes [n], map-sized arrays [x,z]; of map, game, world, thing:<id> or a " +
                "session alias. Calls no method; a property is read only when it returns a field or is on the reviewed list (else refused " +
                "PATH_CALLS_METHOD). rect=x,z,w,h with path reads each thing in the rectangle, or each cell when the path holds [cell]. " +
                "State is never hidden: ok | gone | unbound | error (a wrong name lists the fields the type has); 0, false, \"\", [] and null are real values of state ok.",
            ResultDescription = "success, tick, paused, values[] of of, path, state, v, detail. A refusal: success false, refused (name), message, repair.")]
        public static async Task<object> HandsReadPaths(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "A JSON list of {of, path}.")] string reads = null,
            [ToolParameter(Description = "x,z,w,h: read `path` for each thing (or each cell, with [cell] in the path) in it.")] string rect = null,
            [ToolParameter(Description = "One path, with `of` or `rect`.")] string path = null,
            [ToolParameter(Description = "The target of `path`.")] string of = "map")
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                return JawaBenchHands.ReadPaths(reads, rect, path, of);
            }, cancellationToken);
        }

        [Tool(
            "jawa/act_batch",
            Description =
                "Several jawa tool calls, done in order in ONE main-thread hop on the paused game: no frame runs between two of them. Each act has a " +
                "request id; a repeat of an id with the same arguments returns the first reply and does nothing, with other arguments the whole " +
                "batch is refused. The batch stops at the first act that is not done. Needs the open jawa/session. A tool that waits inside its body is " +
                "refused (NOT_ONE_HOP), as is a rimworld/ tool. action=census counts the tools that can be in a batch and names those that cannot. " +
                "The next frame after a batch is a PAUSED frame; for an act that no paused frame may see, use the acts of jawa/run_until. TEST profile only.",
            ResultDescription =
                "success (the batch was tried), allDone, firstNotDone, acts[] of id, tool, state (done | refused | failed | not_one_hop | not_tried), reply, " +
                "error, tick, frame, replayed; frameFrom, frameTo, tick. A refusal: success false, refused (name), message, repair; nothing was changed.")]
        public static async Task<object> HandsActBatch(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "do or census.")] string action = "do",
            [ToolParameter(Description = "The session's driver.")] string driver = null,
            [ToolParameter(Description = "A JSON list of {id, tool, args}.")] string acts = null)
        {
            return await JawaBenchHandsCore.OneHop(f => ctx.MainThread.InvokeAsync(f, cancellationToken), () =>
            {
                if (action == "census") return JawaBenchHands.BatchCensus();
                if (action != "do") return JawaBenchHandsCore.Refusal("BAD_ARGS", "action is do or census, not '" + action + "'", "correct it");
                return JawaBenchHands.ActBatch(driver, acts);
            });
        }
    }
}
