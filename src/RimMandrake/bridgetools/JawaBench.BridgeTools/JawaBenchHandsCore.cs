// JawaBenchHandsCore.cs - the session, the request ids, the run and the act batch of BRIDGE v2.0: the PURE half (no Verse, no
// Unity, no Harmony). Page: design/specs/2026-11-23-bridge-v2-hands/boundary.md (the wire, the refusals, the promises).
// Item RIMMANDRAKE_WIDEN_SLICE_INTO_RUN_UNTIL_AND_ACT_BATCH. It names no mod, no scene and no check, and it judges nothing.
//
// Compiled into bridgetools/RunUntilSelfTest as well: a `using Verse;` here breaks that build, which is the guard rail.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Threading.Tasks;
using C = JawaBench.BridgeTools.JawaBenchCondCore;
using T = JawaBench.BridgeTools.JawaBenchSceneTickCore;

namespace JawaBench.BridgeTools
{
    /// <summary>What the hands need of the game, beside what a run needs.</summary>
    internal interface IHandsHost : ISceneHost
    {
        int Frame();
        bool Paused();
        /// <summary>Null when a tool call may be part of a batch, else "NAME: why". Changes nothing.</summary>
        string RefuseAct(string tool, Dictionary<string, object> args);
        /// <summary>Do one tool call now. done | refused | failed | not_one_hop, with the tool's reply or the error.</summary>
        ActOutcome Act(string tool, Dictionary<string, object> args);
        /// <summary>Null when a run may start, else "NAME: why".</summary>
        string RefuseRun();
        /// <summary>The thing of this id exists. Binding it is the host's.</summary>
        bool Bind(string alias, int member, string id);
        void Unbind(string alias);
    }

    internal sealed class ActOutcome
    {
        public string State, Error;
        public object Reply;
    }

    internal sealed class HandAct
    {
        public string Id, Tool;
        public Dictionary<string, object> Args = new Dictionary<string, object>();
        public long At;
        public string Canon { get { return Tool + " " + C.Canon(Args) + " at " + At.ToString(CultureInfo.InvariantCulture); } }
    }

    internal static class JawaBenchHandsCore
    {
        internal const double DrainMs = 60000, DefaultLeaseS = 600;         // boundary page, LIMITS

        internal sealed class Refused : Exception
        {
            public readonly string Name, Repair;
            public Refused(string name, string message, string repair) : base(message) { Name = name; Repair = repair; }
        }

        internal static Dictionary<string, object> Refusal(string name, string message, string repair)
        {
            return new Dictionary<string, object> { { "success", false }, { "refused", name }, { "message", name + ": " + message }, { "repair", repair } };
        }

        internal static Dictionary<string, object> Refusal(Refused r) { return Refusal(r.Name, r.Message, r.Repair); }

        /// <summary>A refusal of the condition compiler, by the name that the caller acts on.</summary>
        internal static Dictionary<string, object> Refusal(CondRefused e)
        {
            string name = "BAD_CONDITION", det = e.Detail ?? "";
            if (e.Name == "field_method") name = JawaBenchPathCore.CallsMethod;
            foreach (var n in new[] { JawaBenchPathCore.BadPath, JawaBenchPathCore.CallsMethod, "UNKNOWN_GROUP", "EMPTY_GROUP", "OPTIONAL_COUNTS_UNKNOWN_FALSE" })
                if (e.Name == n || det.StartsWith(n + ": ", StringComparison.Ordinal)) name = n;
            var d = Refusal(name, e.Name + " at " + e.At + ": " + det, "correct the condition or the path; the grammar is on the boundary page");
            d["at"] = e.At; d["detail"] = det; d["cause"] = e.Name;
            return d;
        }

        static Dictionary<string, object> Split(string nameAndWhy, string repair)
        {
            int i = nameAndWhy.IndexOf(": ", StringComparison.Ordinal);
            return i < 0 ? Refusal("CANNOT_RUN", nameAndWhy, repair) : Refusal(nameAndWhy.Substring(0, i), nameAndWhy.Substring(i + 2), repair);
        }

        static string S(object o) { return C.Canon(o); }

        // ============================================================================================ the acts of a call, as data
        internal static List<HandAct> ParseActs(string json, bool withAt)
        {
            var outl = new List<HandAct>();
            if (string.IsNullOrWhiteSpace(json)) return outl;
            List<object> l;
            try { l = C.ParseJson(json) as List<object>; }
            catch (Exception e) { throw new Refused("BAD_ARGS", "acts is not JSON: " + e.Message, "send a JSON list"); }
            if (l == null) throw new Refused("BAD_ARGS", "acts is not a list", "send a JSON list of {id, tool, args}");
            foreach (var o in l)
            {
                var d = o as Dictionary<string, object>;
                if (d == null) throw new Refused("BAD_ARGS", "an act is not an object", "each act is {id, tool, args}");
                foreach (var k in d.Keys)
                    if (k != "id" && k != "tool" && k != "args" && !(withAt && k == "at")) throw new Refused("BAD_ARGS", "an act has no key '" + k + "'", "the keys are id, tool, args" + (withAt ? ", at" : ""));
                object v;
                var a = new HandAct { Id = d.TryGetValue("id", out v) ? v as string : null, Tool = d.TryGetValue("tool", out v) ? v as string : null };
                if (string.IsNullOrEmpty(a.Id)) throw new Refused("NO_REQUEST", "an act has no id", "make the id before you send the call");
                if (string.IsNullOrEmpty(a.Tool)) throw new Refused("BAD_ARGS", "act '" + a.Id + "' names no tool", "give the tool's full name");
                if (d.TryGetValue("args", out v) && v != null)
                {
                    a.Args = v as Dictionary<string, object>;
                    if (a.Args == null) throw new Refused("BAD_ARGS", "the args of act '" + a.Id + "' are not an object", "args is a JSON object");
                }
                if (d.TryGetValue("at", out v))
                {
                    if (!C.IsInt(v) || C.Num(v) < 0) throw new Refused("BAD_ARGS", "act '" + a.Id + "': at is a whole number of ticks, 0 or more", "0 is the start");
                    a.At = (long)C.Num(v);
                }
                outl.Add(a);
            }
            return outl;
        }

        // ============================================================================================ groups in a condition
        /// <summary>The tree with each any_of / all_of written out for the members of its group.</summary>
        internal static object Expand(object node, Func<string, int> sizeOf, string at)
        {
            var l = node as List<object>;
            if (l != null)
            {
                var o = new List<object>();
                for (int i = 0; i < l.Count; i++) o.Add(Expand(l[i], sizeOf, at + "[" + i + "]"));
                return o;
            }
            var d = node as Dictionary<string, object>;
            if (d == null) return node;
            object opt;
            if (d.TryGetValue("optional", out opt) && !(opt is bool && !(bool)opt))
                throw new CondRefused("OPTIONAL_COUNTS_UNKNOWN_FALSE", at, "an optional node counts an unreadable value as false; test value.state");
            foreach (var kind in new[] { "any_of", "all_of" })
            {
                if (!d.ContainsKey(kind)) continue;
                var q = d[kind] as Dictionary<string, object>;
                object g, body;
                if (d.Count != 1 || q == null || q.Count != 2 || !q.TryGetValue("group", out g) || !(g is string) || !q.TryGetValue("node", out body))
                    throw new CondRefused("type", at + "." + kind, "want {\"group\": name, \"node\": node} and no other key");
                int n = sizeOf((string)g);
                if (n < 0) throw new CondRefused("UNKNOWN_GROUP", at + "." + kind, "no group '" + g + "' is bound");
                if (n == 0) throw new CondRefused("EMPTY_GROUP", at + "." + kind, "group '" + g + "' has no member, so the condition says nothing");
                var members = new List<object>();
                for (int i = 0; i < n; i++)
                    members.Add(Expand(Member(body, (string)g + "[" + i.ToString(CultureInfo.InvariantCulture) + "]", "#" + i.ToString(CultureInfo.InvariantCulture)), sizeOf, at + "." + kind));
                return new Dictionary<string, object> { { kind == "any_of" ? "any" : "all", members } };
            }
            var outd = new Dictionary<string, object>();
            foreach (var kv in d) outd[kv.Key] = Expand(kv.Value, sizeOf, at + "." + kv.Key);
            return outd;
        }

        static object Member(object node, string of, string suffix)
        {
            var l = node as List<object>;
            if (l != null)
            {
                var o = new List<object>();
                foreach (var x in l) o.Add(Member(x, of, suffix));
                return o;
            }
            var d = node as Dictionary<string, object>;
            if (d == null) return node;
            var outd = new Dictionary<string, object>();
            foreach (var kv in d)
                outd[kv.Key] = kv.Key == "of" && "$".Equals(kv.Value) ? of : kv.Key == "id" && kv.Value is string ? (string)kv.Value + suffix : Member(kv.Value, of, suffix);
            return outd;
        }

        /// <summary>The probes a tree reads, each once, in order. game.tick is on every row already.</summary>
        internal static void ProbesOf(object node, List<Dictionary<string, object>> outl, HashSet<string> seen)
        {
            var l = node as List<object>;
            if (l != null) { foreach (var x in l) ProbesOf(x, outl, seen); return; }
            var d = node as Dictionary<string, object>;
            if (d == null) return;
            object p;
            if (d.TryGetValue("p", out p))
            {
                if (!"game.tick".Equals(p) && seen.Add(C.Canon(d))) outl.Add(d);
                return;
            }
            foreach (var k in C.SortedKeys(d)) ProbesOf(d[k], outl, seen);
        }

        internal static string TrackName(Dictionary<string, object> probe)
        {
            object p;
            probe.TryGetValue("p", out p);
            if ("value".Equals(p) && probe.ContainsKey("of") && probe.ContainsKey("path")) return probe["of"] + "." + probe["path"];
            if ("value.state".Equals(p) && probe.ContainsKey("of") && probe.ContainsKey("path")) return probe["of"] + "." + probe["path"] + "#state";
            return C.Canon(probe);
        }

        /// <summary>What a run is to play: the expanded condition and its tracks, as the condition compiler takes them.</summary>
        internal sealed class Plan
        {
            public Dictionary<string, object> Spec;
            public List<string> Names = new List<string>();

            public C.Compiled Compile(IProbeSource src)
            {
                var c = new C.Compiler(src, "run") { NodeCap = int.MaxValue }.CompileSpec(Spec);
                if (c.Sample != null)
                    for (int i = 0; i < c.Sample.Count; i++)
                        c.Sample[i] = new KeyValuePair<string, C.Probe>(Names[i], c.Sample[i].Value);
                return c;
            }
        }

        internal static Plan MakePlan(string until, string record, int limit, int mapId, Func<string, int> sizeOf)
        {
            if (limit < 1) throw new Refused("NO_LIMIT", "limit is " + limit, "give the most ticks the run may play");
            if (string.IsNullOrWhiteSpace(until)) throw new Refused("BAD_ARGS", "until is missing", "give a JSON condition tree");
            var tree = Expand(C.ParseSpec(until), sizeOf, "$.until");
            var probes = new List<Dictionary<string, object>>();
            var seen = new HashSet<string>();
            ProbesOf(tree, probes, seen);
            var plan = new Plan();
            var sample = new Dictionary<string, object>();
            var used = new HashSet<string>();
            Action<string, Dictionary<string, object>> add = (name, pr) =>
            {
                if (!used.Add(name)) return;
                sample["t" + plan.Names.Count.ToString("D6", CultureInfo.InvariantCulture)] = pr;
                plan.Names.Add(name);
            };
            foreach (var pr in probes) add(TrackName(pr), pr);
            if (!string.IsNullOrWhiteSpace(record))
            {
                var l = C.ParseSpec(record) as List<object>;
                if (l == null) throw new Refused("BAD_ARGS", "record is not a list", "record is a JSON list of {of, path} or {name, probe}");
                foreach (var o in l)
                {
                    var d = o as Dictionary<string, object>;
                    object of = null, path = null, nm = null, pr = null;
                    if (d != null) { d.TryGetValue("of", out of); d.TryGetValue("path", out path); d.TryGetValue("name", out nm); d.TryGetValue("probe", out pr); }
                    if (d != null && d.Count == 2 && nm is string && pr is Dictionary<string, object>) { add((string)nm, (Dictionary<string, object>)pr); continue; }
                    if (d == null || d.Count != 2 || !(of is string) || !(path is string)) throw new Refused("BAD_ARGS", "a record entry is neither {of, path} nor {name, probe}: " + C.Canon(o), "correct the entry");
                    int n = sizeOf((string)of);
                    if (n == 0) throw new Refused("EMPTY_GROUP", "group '" + of + "' has no member", "bind the group first");
                    for (int i = 0; i < Math.Max(n, 1); i++)           // n < 0: one thing, or a target that is no alias
                    {
                        var one = new Dictionary<string, object> { { "p", "value" }, { "of", n > 0 ? (string)of + "[" + i.ToString(CultureInfo.InvariantCulture) + "]" : of }, { "path", path } };
                        add(TrackName(one), one);
                    }
                }
            }
            plan.Spec = new Dictionary<string, object> { { "until", tree }, { "max_ticks", (double)limit } };
            if (mapId >= 0) plan.Spec["mapId"] = (double)mapId;
            if (plan.Names.Count > 0) plan.Spec["sample"] = new Dictionary<string, object> { { "every", 1.0 }, { "probes", sample } };
            return plan;
        }

        // ============================================================================================ the session
        internal sealed class ActRec { public string Canon; public Dictionary<string, object> Reply; }
        internal sealed class RunRec { public string Request, Canon; public T.SceneRun Run; public List<HandAct> Acts; public Dictionary<string, object> Groups; }

        internal sealed class Session
        {
            public string Id, Driver, Stage = "open";        // open -> closing -> closed | aborted
            public string End;
            public double LeaseMs, RenewedAt, ClosingFrom = -1;
            public bool LeaseEnded, Taken;                  // taken over from a dead driver: it may be read and ended, not played
            public T.Trace Trace;
            public readonly Dictionary<string, int> Bound = new Dictionary<string, int>(StringComparer.Ordinal);   // -1 one thing, else the group's size
            public readonly Dictionary<string, List<string>> Ids = new Dictionary<string, List<string>>(StringComparer.Ordinal);
            public readonly Dictionary<string, ActRec> Acts = new Dictionary<string, ActRec>(StringComparer.Ordinal);
            public readonly Dictionary<string, RunRec> Runs = new Dictionary<string, RunRec>(StringComparer.Ordinal);
            public RunRec Last;
            public string OpenAct;
        }

        /// <summary>All the hands' state. One for a game process.</summary>
        internal sealed class Hands
        {
            readonly IHandsHost _h;
            int _serial;
            public Session Cur;
            public Hands(IHandsHost h) { _h = h; }

            public bool IsOpen { get { return Cur != null && Cur.Stage == "open"; } }
            /// <summary>An open session or one that is still writing its end: nobody else may start a run.</summary>
            public bool Busy { get { return Cur != null && (Cur.Stage == "open" || Cur.Stage == "closing"); } }
            bool RunLive { get { return Cur != null && Cur.Last != null && Cur.Last.Run.Stage != "closed"; } }

            long Row(string phase, string rec, string fields) { return Cur.Trace.Emit(_h, null, _h.Tick(), phase, rec, fields); }

            /// <summary>A record of the open session's trace, outside any run (the force record); -2 when no session is open.</summary>
            public long Record(string phase, string rec, string fields) { return Cur == null || Cur.Stage != "open" ? -2 : Row(phase, rec, fields); }

            /// <summary>The caller may drive. Its call renews the lease.</summary>
            Dictionary<string, object> RefuseTaken()
            {
                return Cur.Taken ? Refusal("TAKEN_OVER", "session " + Cur.Id + " lost its first driver: it makes no more evidence", "read it, then close or abort it") : null;
            }

            internal Dictionary<string, object> Admit(string driver)
            {
                if (!IsOpen) return Refusal("NO_SESSION", Cur == null ? "no session is open" : "session " + Cur.Id + " is " + Cur.Stage, "open a session first");
                if (string.IsNullOrEmpty(driver) || driver != Cur.Driver)
                    return Refusal("NOT_THE_DRIVER", "session " + Cur.Id + " is driven by '" + Cur.Driver + "', not by '" + driver + "'", "wait, or use another game");
                Cur.RenewedAt = _h.NowMs();
                Cur.LeaseEnded = false;
                return null;
            }

            public Dictionary<string, object> Open(string driver, double leaseS)
            {
                if (Busy) return Refusal("SESSION_OPEN", "session " + Cur.Id + " of '" + Cur.Driver + "' is " + Cur.Stage, "its driver closes it, or it is aborted after its lease");
                if (string.IsNullOrEmpty(driver)) return Refusal("BAD_ARGS", "driver is empty", "give the caller's own name");
                if (!(leaseS > 0)) return Refusal("BAD_ARGS", "leaseS is " + leaseS.ToString(CultureInfo.InvariantCulture), "more than 0 seconds");
                if (!_h.Pause()) return Refusal("CANNOT_RUN", "the game did not pause", "another mod keeps the game running");
                _serial++;
                string id = "S" + _serial.ToString(CultureInfo.InvariantCulture) + "_" + DateTime.UtcNow.ToString("yyyyMMddTHHmmss", CultureInfo.InvariantCulture);
                Cur = new Session { Id = id, Driver = driver, LeaseMs = leaseS * 1000, RenewedAt = _h.NowMs(), Trace = new T.Trace { Session = id } };
                Row("session", "session_open", "\"driver\":" + S(driver) + ",\"leaseS\":" + S(leaseS) + ",\"frame\":" + _h.Frame());
                return State();
            }

            public Dictionary<string, object> State()
            {
                var d = new Dictionary<string, object> { { "success", true }, { "session", null }, { "stage", "none" }, { "paused", _h.Paused() }, { "tick", (double)_h.Tick() } };
                if (Cur == null) return d;
                var bound = new Dictionary<string, object>();
                foreach (var kv in Cur.Ids)
                {
                    var l = new List<object>();
                    foreach (var x in kv.Value) l.Add(x);
                    bound[kv.Key] = Cur.Bound[kv.Key] < 0 ? l[0] : l;
                }
                d["session"] = Cur.Id; d["stage"] = Cur.Stage; d["driver"] = Cur.Driver; d["taken"] = Cur.Taken; d["leaseEnded"] = Cur.LeaseEnded;
                d["leaseLeftS"] = Math.Round((Cur.LeaseMs - (_h.NowMs() - Cur.RenewedAt)) / 1000, 1);
                d["lastRun"] = Cur.Last == null ? null : RunReply(Cur.Last, false);
                d["openAct"] = Cur.OpenAct; d["bound"] = bound; d["rows"] = (double)Cur.Trace.Rows; d["dropped"] = (double)Cur.Trace.Dropped;
                return d;
            }

            public Dictionary<string, object> Bind(string driver, string bindings)
            {
                var no = Admit(driver);
                if (no != null) return no;
                no = RefuseTaken();
                if (no != null) return no;
                if (RunLive) return Refusal("RUN_ACTIVE", "run " + Cur.Last.Run.Id + " is " + Cur.Last.Run.Stage, "read its status, then cancel it");
                Dictionary<string, object> d;
                try { d = C.ParseJson(bindings ?? "") as Dictionary<string, object>; }
                catch (Exception) { d = null; }
                if (d == null || d.Count == 0) return Refusal("BAD_ARGS", "bindings is not a JSON object of alias to id", "send {\"alias\": \"id\"} or {\"alias\": [\"id\", ...]}");
                var want = new List<KeyValuePair<string, List<string>>>();
                foreach (var k in C.SortedKeys(d))
                {
                    bool good = k.Length > 0;
                    foreach (char c in k) if (c != '_' && !char.IsLetterOrDigit(c)) good = false;
                    if (!good) return Refusal("BAD_ARGS", "alias '" + k + "' is not letters, digits and _", "rename it");
                    var ids = new List<string>();
                    var l = d[k] as List<object>;
                    if (l != null) foreach (var x in l) ids.Add(x as string);
                    else if (d[k] == null || d[k] is string) ids.Add(d[k] as string);
                    else return Refusal("BAD_ARGS", "alias '" + k + "' is bound to neither a text nor a list", "use ids");
                    if (l != null && (ids.Contains(null) || ids.Contains(""))) return Refusal("BAD_ARGS", "group '" + k + "' holds something that is not an id", "a group is a list of ids");
                    want.Add(new KeyValuePair<string, List<string>>(k, ids));
                }
                foreach (var kv in want)
                    foreach (var id in kv.Value)
                        if (id != null && !_h.Bind(null, 0, id)) return Refusal("UNKNOWN_THING", "no thing '" + id + "' for alias '" + kv.Key + "'", "read the id again");
                foreach (var kv in want)
                {
                    bool group = d[kv.Key] is List<object>;
                    _h.Unbind(kv.Key);
                    for (int i = 0; i < kv.Value.Count; i++) if (kv.Value[i] != null) _h.Bind(kv.Key, group ? i : -1, kv.Value[i]);
                    Cur.Bound[kv.Key] = group ? kv.Value.Count : -1;
                    Cur.Ids[kv.Key] = kv.Value;
                    Row("session", "bind", "\"alias\":" + S(kv.Key) + ",\"ids\":" + S(d[kv.Key]));
                }
                return State();
            }

            /// <summary>The members of a group, or -1 when the name is not a group.</summary>
            public int GroupSize(string alias)
            {
                int n;
                return Cur != null && alias != null && Cur.Bound.TryGetValue(alias, out n) ? n : -1;
            }

            /// <summary>A new driver takes the session of a dead one, to read it and to end it. A live lease is taken only with the
            /// dead driver's own text: the caller looked and that process is gone. The live run is cancelled and the game paused.</summary>
            public Dictionary<string, object> Take(string driver, string from)
            {
                bool open = IsOpen;
                if (!open) return Refusal("NO_SESSION", Cur == null ? "no session is open" : "session " + Cur.Id + " is " + Cur.Stage, "open a session");
                if (string.IsNullOrEmpty(driver)) return Refusal("BAD_ARGS", "driver is empty", "give the caller's own name");
                string old = Cur.Driver;
                if (driver == old) return Refusal("BAD_ARGS", "'" + driver + "' is the driver already", "close or abort the session");
                if (!string.IsNullOrEmpty(from) ? from != old : !Cur.LeaseEnded)
                    return Refusal("DRIVER_ALIVE", "session " + Cur.Id + " is driven by '" + old + "'" + (string.IsNullOrEmpty(from) ? " and its lease has not ended" : ", not by '" + from + "'"),
                                   "look whether that process is alive; when it is dead, give its text as `from`");
                if (RunLive) Cur.Last.Run.Force("cancelled", "the session was taken over from '" + old + "'", _h.Tick());
                bool p = _h.Pause();
                Cur.Driver = driver;
                Cur.Taken = true;
                Cur.RenewedAt = _h.NowMs();
                Cur.LeaseEnded = false;
                Row("session", "session_taken", "\"from\":" + S(old) + ",\"to\":" + S(driver) + ",\"paused\":" + (p ? "true" : "false"));
                return State();
            }

            public Dictionary<string, object> Finish(string driver, bool abort)
            {
                if (abort && IsOpen && Cur.LeaseEnded) { }                      // its driver may be gone: anyone may end it
                else { var no = Admit(driver); if (no != null) return no; }
                if (RunLive) Cur.Last.Run.Force("cancelled", abort ? "the session was aborted" : "the session was closed", _h.Tick());
                _h.Pause();
                Cur.End = abort ? "aborted" : "closed";
                Cur.Stage = "closing";
                return State();
            }

            /// <summary>Once a frame: the lease, and the closing record after the drain.</summary>
            public void Frame()
            {
                if (Cur == null) return;
                if (RunLive && !Cur.Last.Run.Running && Cur.Last.Run.Stage == "settling") return;         // the run closes first
                if (Cur.Stage == "open")
                {
                    if (Cur.LeaseEnded || _h.NowMs() - Cur.RenewedAt <= Cur.LeaseMs) return;
                    Cur.LeaseEnded = true;
                    if (RunLive) Cur.Last.Run.Force("cancelled", "the driver's lease ended", _h.Tick());
                    bool p = _h.Pause();
                    Row("session", "lease_ended", "\"paused\":" + (p ? "true" : "false"));
                    return;
                }
                if (Cur.Stage != "closing") return;
                double now = _h.NowMs();
                if (Cur.ClosingFrom < 0) { Cur.ClosingFrom = now; return; }
                bool drained = _h.Drained();
                if (!drained && now - Cur.ClosingFrom < DrainMs) return;
                Row("session", "session_close", "\"end\":" + S(Cur.End) + ",\"rows\":" + Cur.Trace.Rows + ",\"dropped\":" + Cur.Trace.Dropped + ",\"drained\":" + (drained ? "true" : "false"));
                Cur.Stage = Cur.End;
                foreach (var a in new List<string>(Cur.Bound.Keys)) _h.Unbind(a);
            }

            // ---------------------------------------------------------------------------------------- acts
            /// <summary>Null when every act may be tried, else the refusal of the whole list. Changes nothing.</summary>
            Dictionary<string, object> RefuseActs(IList<HandAct> acts)
            {
                var inCall = new Dictionary<string, string>(StringComparer.Ordinal);
                foreach (var a in acts)
                {
                    string canon;
                    ActRec known;
                    if (inCall.TryGetValue(a.Id, out canon) ? canon != a.Canon : Cur.Acts.TryGetValue(a.Id, out known) && known.Canon != a.Canon)
                        return Refusal("REQUEST_CONFLICT", "id '" + a.Id + "' has other arguments than the first time", "never reuse an id");
                    if (Cur.Runs.ContainsKey(a.Id)) return Refusal("REQUEST_CONFLICT", "id '" + a.Id + "' is the id of a run", "never reuse an id");
                    inCall[a.Id] = a.Canon;
                    if (Cur.Acts.ContainsKey(a.Id)) continue;
                    string why = _h.RefuseAct(a.Tool, a.Args);
                    if (why != null) return Split(why, "correct the act '" + a.Id + "'");
                }
                return null;
            }

            Dictionary<string, object> DoOne(HandAct a, string phase)
            {
                ActRec known;
                if (Cur.Acts.TryGetValue(a.Id, out known))
                    return new Dictionary<string, object>(known.Reply) { ["replayed"] = true };
                Cur.OpenAct = a.Id;
                Row(phase, "act_start", "\"id\":" + S(a.Id) + ",\"tool\":" + S(a.Tool) + ",\"args\":" + S(a.Args) + ",\"frame\":" + _h.Frame());
                ActOutcome o;
                try { o = _h.Act(a.Tool, a.Args); }
                catch (Exception e) { o = new ActOutcome { State = "failed", Error = e.GetType().Name + ": " + e.Message }; }
                var r = new Dictionary<string, object>
                {
                    { "id", a.Id }, { "tool", a.Tool }, { "state", o.State }, { "reply", o.Reply }, { "error", o.Error },
                    { "tick", (double)_h.Tick() }, { "frame", (double)_h.Frame() }, { "replayed", false },
                };
                Row(phase, "act_end", "\"id\":" + S(a.Id) + ",\"state\":" + S(o.State) + ",\"error\":" + S(o.Error) + ",\"frame\":" + _h.Frame());
                Cur.Acts[a.Id] = new ActRec { Canon = a.Canon, Reply = r };
                Cur.OpenAct = null;
                return r;
            }

            List<object> DoAll(IList<HandAct> acts, string phase, out string firstBad)
            {
                var outl = new List<object>();
                firstBad = null;
                foreach (var a in acts)
                {
                    if (firstBad != null)
                    {
                        outl.Add(new Dictionary<string, object> { { "id", a.Id }, { "tool", a.Tool }, { "state", "not_tried" }, { "reply", null }, { "error", "act '" + firstBad + "' was not done" },
                                                                  { "tick", (double)_h.Tick() }, { "frame", (double)_h.Frame() }, { "replayed", false } });
                        continue;
                    }
                    var r = DoOne(a, phase);
                    outl.Add(r);
                    if (!"done".Equals(r["state"])) firstBad = a.Id;
                }
                return outl;
            }

            /// <summary>The whole batch, now, on the main thread.</summary>
            public Dictionary<string, object> Batch(string driver, IList<HandAct> acts)
            {
                var no = Admit(driver);
                if (no != null) return no;
                no = RefuseTaken();
                if (no != null) return no;
                if (acts.Count == 0) return Refusal("BAD_ARGS", "the batch holds no act", "give at least one act");
                no = RefuseActs(acts);
                if (no != null) return no;
                bool all = true;                     // a whole repeat is answered whatever the game does now: nothing will be done
                foreach (var a in acts) if (!Cur.Acts.ContainsKey(a.Id)) all = false;
                if (!all && RunLive) return Refusal("RUN_ACTIVE", "run " + Cur.Last.Run.Id + " is " + Cur.Last.Run.Stage, "read its status, then cancel it");
                if (!all && !_h.Paused()) return Refusal("GAME_RUNNING", "the game is not paused", "run to the tick first");
                long f0 = _h.Frame();
                string bad;
                var l = DoAll(acts, "batch", out bad);
                return new Dictionary<string, object> { { "success", true }, { "acts", l }, { "allDone", bad == null }, { "firstNotDone", bad },
                                                        { "frameFrom", (double)f0 }, { "frameTo", (double)_h.Frame() }, { "tick", (double)_h.Tick() } };
            }

            // ---------------------------------------------------------------------------------------- the run
            /// <summary>Start a run, or answer a repeat of its request. `make` compiles it; `go` starts the clock.</summary>
            public Dictionary<string, object> StartRun(string driver, string request, string canon, IList<HandAct> acts, int limit,
                                                       Func<string, IList<T.Act>, T.Trace, T.SceneRun> make, object epoch, Action<T.SceneRun> armed, Action go)
            {
                var no = Admit(driver);
                if (no != null) return no;
                no = RefuseTaken();
                if (no != null) return no;
                if (string.IsNullOrEmpty(request)) return Refusal("NO_REQUEST", "the run has no request id", "make the id before you send the call");
                RunRec known;
                if (Cur.Runs.TryGetValue(request, out known))
                {
                    if (known.Canon != canon) return Refusal("REQUEST_CONFLICT", "request '" + request + "' started another run", "never reuse an id");
                    var again = RunReply(known, true);
                    again["replayed"] = true;
                    return again;
                }
                if (Cur.Acts.ContainsKey(request)) return Refusal("REQUEST_CONFLICT", "request '" + request + "' is the id of an act", "never reuse an id");
                if (RunLive) return Refusal("RUN_ACTIVE", "run " + Cur.Last.Run.Id + " is " + Cur.Last.Run.Stage, "read its status, then cancel it");
                if (!_h.Paused()) return Refusal("GAME_RUNNING", "the game is not paused", "something else started the clock: read the session's state");
                string why = _h.RefuseRun();
                if (why != null) return Split(why, "read the session's state");
                no = RefuseActs(acts);
                if (no != null) return no;
                var starts = new List<HandAct>();
                var ticks = new List<T.Act>();
                var ids = new HashSet<string>();
                foreach (var a in acts)
                {
                    if (!ids.Add(a.Id) || a.Id == request) return Refusal("REQUEST_CONFLICT", "id '" + a.Id + "' is used twice in this run", "each act has its own id");
                    if (Cur.Acts.ContainsKey(a.Id)) return Refusal("REQUEST_CONFLICT", "act '" + a.Id + "' was done already, in another call", "a run's acts have new ids");
                    if (a.At == 0) { starts.Add(a); continue; }
                    var act = a;
                    ticks.Add(new T.Act(act.Id, act.At, () =>
                    {
                        var r = DoOne(act, "end_of_tick");
                        if (!"done".Equals(r["state"])) throw new InvalidOperationException(r["state"] + ": " + r["error"]);
                        return act.Tool;
                    }));
                }
                why = T.RefuseActs(ticks, limit);
                if (why != null) return Refusal("BAD_ARGS", why, "move the act inside the limit");
                string runId = Cur.Id + "_r" + (Cur.Runs.Count + 1).ToString(CultureInfo.InvariantCulture);
                var run = make(runId, ticks, Cur.Trace);
                var groups = new Dictionary<string, object>();
                foreach (var kv in Cur.Ids) { var l = new List<object>(); foreach (var x in kv.Value) l.Add(x); groups[kv.Key] = l; }
                var rec = new RunRec { Request = request, Canon = canon, Run = run, Acts = new List<HandAct>(acts), Groups = groups };
                Cur.Runs[request] = rec;
                Cur.Last = rec;
                if (armed != null) armed(run);
                Row("first", "run_open", "\"of\":" + S(runId) + ",\"request\":" + S(request) + ",\"bound\":" + S(groups) + ",\"frame\":" + _h.Frame());
                run.Arm(_h.Tick(), epoch);
                if (run.Running && starts.Count > 0)
                {
                    string bad;
                    DoAll(starts, "start", out bad);
                    if (bad != null) run.Force("aborted", "act '" + bad + "' was not done, so the clock was not started", _h.Tick());
                }
                if (run.Running) go();
                return RunReply(rec, true);
            }

            public Dictionary<string, object> RunStatus(string driver, string request)
            {
                if (Cur == null) return Refusal("NO_SESSION", "no session is open", "open a session first");
                if (IsOpen && driver != null && driver == Cur.Driver) Admit(driver);      // a poll renews the lease; a reader does not
                RunRec r = Cur.Last;
                if (!string.IsNullOrEmpty(request) && !Cur.Runs.TryGetValue(request, out r))
                    return Refusal("UNKNOWN_REQUEST", "no run of request '" + request + "' in session " + Cur.Id, "the call did not arrive: it may be sent again");
                if (r == null) return Refusal("UNKNOWN_REQUEST", "session " + Cur.Id + " has no run", "start one");
                return RunReply(r, true);
            }

            public Dictionary<string, object> Cancel(string driver, string request)
            {
                var no = Admit(driver);
                if (no != null) return no;
                RunRec r;
                if (string.IsNullOrEmpty(request)) r = Cur.Last;
                else if (!Cur.Runs.TryGetValue(request, out r)) r = null;
                if (r == null) return Refusal("UNKNOWN_REQUEST", "no such run", "read the session's state");
                if (r.Run.Running) r.Run.Force("cancelled", "cancelled by a call", _h.Tick());
                return RunReply(r, true);
            }

            internal static string WhyOf(string state)
            {
                return state == "running" ? null : state == "hit" ? "hit" : state == "done" ? "limit" : state == "unknown" ? "unknown" : state == "cancelled" ? "cancelled" : "fault";
            }

            Dictionary<string, object> RunReply(RunRec rec, bool values)
            {
                var run = rec.Run;
                var d = new Dictionary<string, object>
                {
                    { "success", true }, { "session", Cur.Id }, { "request", rec.Request }, { "run", run.Id }, { "stage", run.Stage }, { "state", run.State },
                    { "why", run.Running ? null : WhyOf(run.State) }, { "detail", run.Why }, { "tickFrom", (double)run.FromTick }, { "tick", (double)run.EndTick },
                    { "hitTick", run.HitTick.HasValue ? (object)(double)run.HitTick.Value : null }, { "rows", (double)run.Rows }, { "dropped", (double)run.Dropped },
                    { "drained", run.Drained }, { "replayed", false }, { "unknownValue", run.UnknownValue() },
                };
                var faults = new List<object>();
                foreach (var f in run.Faults) faults.Add(f);
                d["faults"] = faults;
                d["lockReads"] = (double)run.Lock.Reads; d["breaches"] = run.Lock.Breaches();
                if (!values) return d;
                var acts = new List<object>();
                foreach (var a in rec.Acts)
                {
                    ActRec ar;
                    acts.Add(Cur.Acts.TryGetValue(a.Id, out ar) ? new Dictionary<string, object>(ar.Reply) { ["at"] = (double)a.At }
                             : new Dictionary<string, object> { { "id", a.Id }, { "tool", a.Tool }, { "at", (double)a.At }, { "state", run.Running ? "owed" : "not_tried" } });
                }
                d["acts"] = acts;
                var vals = new Dictionary<string, object>();
                var blind = new List<object>();
                foreach (var t in run.Tracks)
                {
                    if (!t.Has) { blind.Add(new Dictionary<string, object> { { "value", t.Name }, { "state", "unread" } }); continue; }
                    var v = new Dictionary<string, object> { { "state", t.Last.Status }, { "v", t.Last.V }, { "reads", (double)t.Reads } };
                    if (t.Last.Status != "ok") v["detail"] = t.Last.Detail;
                    vals[t.Name] = v;
                    if (t.BadTicks > 0)
                        blind.Add(new Dictionary<string, object> { { "value", t.Name }, { "state", t.BadState }, { "detail", t.BadDetail }, { "firstTick", (double)t.BadFrom }, { "ticks", (double)t.BadTicks } });
                }
                if (run.Dropped > 0) blind.Add(new Dictionary<string, object> { { "value", "trace rows" }, { "state", "dropped" }, { "ticks", (double)run.Dropped } });
                d["values"] = vals;
                d["couldNotLook"] = blind;
                d["cost"] = run.Result()["cost"]; d["costliest"] = run.Costliest();
                return d;
            }
        }

        // ============================================================================================ one hop
        /// <summary>The whole body in ONE main-thread hop: no frame runs between two acts of a batch.</summary>
        internal static Task<object> OneHop(Func<Func<object>, Task<object>> hop, Func<object> body)
        {
            return hop(body);
        }
    }
}
