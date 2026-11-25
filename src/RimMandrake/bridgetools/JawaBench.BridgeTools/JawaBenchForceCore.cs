// JawaBenchForceCore.cs - the order through the giver, the motive and the force record of BRIDGE v2.0: the PURE half (no Verse,
// no Unity, no Harmony). Item RIMMANDRAKE_BUILD_CAST_ASSERTS_AND_ORDER_THROUGH_GIVER. Page: design/specs/2026-11-23-bridge-v2/
// boundary.md §THE ORDER THROUGH THE GIVER, THE MOTIVE, THE FORCE RECORD. The Verse half is JawaBenchForce.cs.
//
// The rule that this file holds: the level on the record is the level of the path that RAN, never the level that was asked.
// A giver's refusal is a fact about the mod: the order was delivered, nothing was started, and the record says nothing was forced.
//
// Compiled into bridgetools/ForceSelfTest as well: a `using Verse;` here breaks that build, which is the guard rail.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text;

namespace JawaBench.BridgeTools
{
    internal sealed class OrderReq
    {
        public string Actor, Level, Giver, JobDef, Target, Fallback;
    }

    internal sealed class MotiveReq
    {
        public string Actor, LordJob, Args;
    }

    /// <summary>The giver's own answer. Asking it starts nothing.</summary>
    internal sealed class GiverAnswer
    {
        public bool Found = true;        // false: no giver of that name exists (an argument fault, not the mod's)
        public string Bad;               // an argument fault named by the host (no target given, ...), or null
        public bool Given;
        public string Reason, Via, Node;
        public object Job;               // the host's handle on what the giver made
    }

    internal sealed class StartAnswer
    {
        public bool Started, Queued;
        public string Reason, Job;
        public string Bad;               // an argument fault (no such JobDef, no such target): nothing was started
    }

    internal sealed class MotiveAnswer
    {
        public bool Done;
        public string Reason, Before, After, Duty;
    }

    internal interface IForceHost
    {
        /// <summary>Null when the actor is a spawned pawn of the current map, else why not.</summary>
        string WhyNoActor(string actor);
        GiverAnswer AskGiver(OrderReq r);
        StartAnswer StartGiven(OrderReq r, GiverAnswer a);
        StartAnswer StartRaw(OrderReq r);
        /// <summary>The actor's lord ("lord 12 LordJob_AssaultColony"), or null when it has none.</summary>
        string LordOf(string actor);
        MotiveAnswer SetMotive(MotiveReq m);
        long Tick();
        /// <summary>A record of the session trace; -2 when no session is open.</summary>
        long Record(string rec, string fields);
    }

    internal static class JawaBenchForceCore
    {
        public const int Motive = 2, Giver = 3, Raw = 4;
        public const string NotReachable = "not shown reachable in play";

        internal sealed class Entry
        {
            public string Session, Actor, Act, Via, Reason;
            public int Asked;
            public int? Used;
            public bool Given, Started;
            public long Tick, Seq;

            public Dictionary<string, object> Dict()
            {
                return new Dictionary<string, object>
                {
                    { "actor", Actor }, { "act", Act }, { "asked", (double)Asked }, { "used", Used.HasValue ? (object)(double)Used.Value : null },
                    { "via", Via }, { "given", Given }, { "started", Started }, { "reason", Reason }, { "tick", (double)Tick },
                    { "class", "NOT UNDONE" }, { "reach", "save" },
                };
            }
        }

        /// <summary>Every force entry of this game process, with the session it was made in.</summary>
        internal sealed class ForceLog
        {
            public readonly List<Entry> Entries = new List<Entry>();

            /// <summary>Per actor of this session: each entry and the highest level used (null when nothing was forced).</summary>
            public Dictionary<string, object> Summary(string session)
            {
                var d = new Dictionary<string, object>(StringComparer.Ordinal);
                foreach (var e in Entries)
                {
                    if (!string.Equals(e.Session, session, StringComparison.Ordinal)) continue;
                    object o;
                    if (!d.TryGetValue(e.Actor, out o)) d[e.Actor] = o = new Dictionary<string, object> { { "max", null }, { "entries", new List<object>() } };
                    var a = (Dictionary<string, object>)o;
                    ((List<object>)a["entries"]).Add(e.Dict());
                    if (e.Used.HasValue && (a["max"] == null || (double)a["max"] < e.Used.Value)) a["max"] = (double)e.Used.Value;
                }
                return d;
            }
        }

        // ------------------------------------------------------------------------------------------------ helpers
        internal static string Q(string s)
        {
            if (s == null) return "null";
            var b = new StringBuilder("\"");
            foreach (char c in s)
            {
                if (c == '"' || c == '\\') b.Append('\\').Append(c);
                else if (c < ' ') b.Append("\\u").Append(((int)c).ToString("x4", CultureInfo.InvariantCulture));
                else b.Append(c);
            }
            return b.Append('"').ToString();
        }

        internal static Dictionary<string, object> Refusal(string name, string message, string repair)
        {
            return new Dictionary<string, object> { { "success", false }, { "refused", name }, { "message", name + ": " + message }, { "repair", repair } };
        }

        static int? LevelOf(string s)
        {
            switch ((s ?? "").Trim().ToLowerInvariant())
            {
                case "giver": case "3": return Giver;
                case "raw": case "4": return Raw;
            }
            return null;
        }

        static Entry Write(IForceHost h, ForceLog log, string session, string actor, string act, int asked, int? used, string via, bool given, bool started, string reason)
        {
            var e = new Entry { Session = session, Actor = actor, Act = act, Asked = asked, Used = used, Via = via, Given = given, Started = started, Reason = reason, Tick = h.Tick() };
            e.Seq = h.Record("force", "\"actor\":" + Q(actor) + ",\"act\":" + Q(act) + ",\"asked\":" + asked +
                                      ",\"used\":" + (used.HasValue ? used.Value.ToString(CultureInfo.InvariantCulture) : "null") +
                                      ",\"via\":" + Q(via) + ",\"given\":" + (given ? "true" : "false") + ",\"started\":" + (started ? "true" : "false") +
                                      ",\"reason\":" + Q(reason) + ",\"class\":\"NOT UNDONE\",\"reach\":\"save\"");
            log.Entries.Add(e);
            return e;
        }

        static Dictionary<string, object> Reply(Entry e, StartAnswer st, GiverAnswer g, string giverSaid)
        {
            var d = new Dictionary<string, object>
            {
                { "success", true }, { "given", e.Given }, { "reason", giverSaid }, { "started", e.Started }, { "queued", st != null && st.Queued },
                { "levelAsked", (double)e.Asked }, { "levelUsed", e.Used.HasValue ? (object)(double)e.Used.Value : null }, { "via", e.Via },
                { "job", st != null ? st.Job : null }, { "startReason", st != null ? st.Reason : null }, { "node", g != null ? g.Node : null },
                { "record", (double)e.Seq }, { "force", e.Dict() },
            };
            if (e.Used == Raw) d["note"] = NotReachable;
            return d;
        }

        // ------------------------------------------------------------------------------------------------ the order
        /// <summary>One order at level 3 (through the giver) or 4 (raw). Main thread; the game paused or not.</summary>
        public static Dictionary<string, object> Order(OrderReq r, IForceHost h, ForceLog log, string session)
        {
            if (r == null || string.IsNullOrWhiteSpace(r.Actor)) return Refusal("BAD_ARGS", "actor is required", "give an alias, alias[n] or a pawn id");
            int? lv = LevelOf(r.Level);
            if (lv == null) return Refusal("BAD_ARGS", "level is giver or raw, not '" + r.Level + "'", "give level=giver (3) or level=raw (4)");
            bool elseRaw = false;
            if (!string.IsNullOrWhiteSpace(r.Fallback))
            {
                if (!string.Equals(r.Fallback.Trim(), "raw", StringComparison.OrdinalIgnoreCase)) return Refusal("BAD_ARGS", "fallback is raw or empty, not '" + r.Fallback + "'", "give fallback=raw or nothing");
                if (lv != Giver) return Refusal("BAD_ARGS", "fallback=raw is for a level=giver order", "drop fallback");
                elseRaw = true;
            }
            if (lv == Giver && string.IsNullOrWhiteSpace(r.Giver)) return Refusal("BAD_ARGS", "a level=giver order names its giver", "give giver=<WorkGiverDef or ThinkNode_JobGiver type>");
            if ((lv == Raw || elseRaw) && string.IsNullOrWhiteSpace(r.JobDef)) return Refusal("BAD_ARGS", "a raw order names its jobDef", "give jobDef=<JobDef>");
            string no = h.WhyNoActor(r.Actor);
            if (no != null) return Refusal("NO_ACTOR", no, "bind the pawn, or give its id");

            if (lv == Giver)
            {
                var g = h.AskGiver(r);
                if (!g.Found) return Refusal("NO_SUCH_GIVER", "no WorkGiverDef and no ThinkNode_JobGiver type is named '" + r.Giver + "'", "name a WorkGiverDef defName or a JobGiver type");
                if (g.Bad != null) return Refusal("BAD_ARGS", g.Bad, "correct the order");
                if (g.Given)
                {
                    var st = h.StartGiven(r, g);
                    var e = Write(h, log, session, r.Actor, "order", Giver, Giver, g.Via, true, st.Started, st.Started ? null : st.Reason);
                    return Reply(e, st, g, null);
                }
                if (!elseRaw)
                {
                    var e = Write(h, log, session, r.Actor, "order", Giver, null, g.Via, false, false, g.Reason);
                    return Reply(e, null, g, g.Reason);
                }
                var raw = h.StartRaw(r);
                if (raw.Bad != null) return Refusal("BAD_ARGS", raw.Bad + " (the giver had refused: " + g.Reason + ")", "correct the raw half of the order");
                var er = Write(h, log, session, r.Actor, "order", Giver, Raw, "raw", false, raw.Started, "the giver refused (" + g.Reason + "); fallback=raw" + (raw.Started ? "" : ": " + raw.Reason));
                return Reply(er, raw, g, g.Reason);
            }

            var s = h.StartRaw(r);
            if (s.Bad != null) return Refusal("BAD_ARGS", s.Bad, "correct the order");
            var ex = Write(h, log, session, r.Actor, "order", Raw, Raw, "raw", false, s.Started, s.Started ? null : s.Reason);
            return Reply(ex, s, null, null);
        }

        // ------------------------------------------------------------------------------------------------ the motive
        /// <summary>Level 2: the actor's lord takes a new LordJob. A pawn with no lord is refused: a motive makes no group.</summary>
        public static Dictionary<string, object> SetMotive(MotiveReq m, IForceHost h, ForceLog log, string session)
        {
            if (m == null || string.IsNullOrWhiteSpace(m.Actor)) return Refusal("BAD_ARGS", "actor is required", "give an alias, alias[n] or a pawn id");
            if (string.IsNullOrWhiteSpace(m.LordJob)) return Refusal("BAD_ARGS", "lordJob is required", "give a LordJob type, e.g. LordJob_AssaultColony");
            string no = h.WhyNoActor(m.Actor);
            if (no != null) return Refusal("NO_ACTOR", no, "bind the pawn, or give its id");
            string lord = h.LordOf(m.Actor);
            if (lord == null)
                return Refusal("NO_LORD", "'" + m.Actor + "' has no lord: a motive gives a lord a new job, it does not make a group",
                               "stage the pawn in a group (a raid through its incident, or a lord the stage makes), then give the motive");
            var a = h.SetMotive(m);
            if (!a.Done) return Refusal("MOTIVE_NOT_SET", a.Reason ?? "the lord did not take the job", "read the reason; the lord is as the reply says");
            var e = Write(h, log, session, m.Actor, "motive", Motive, Motive, m.LordJob, true, true, null);
            return new Dictionary<string, object>
            {
                { "success", true }, { "lordBefore", a.Before ?? lord }, { "lordAfter", a.After }, { "duty", a.Duty },
                { "levelAsked", (double)Motive }, { "levelUsed", (double)Motive }, { "record", (double)e.Seq }, { "force", e.Dict() },
            };
        }
    }
}
