// Units for the order through the giver, the motive and the force record (JawaBenchForceCore.cs: the PRODUCTION file, or a planted
// copy). One unit per promise of design/specs/2026-11-23-bridge-v2/boundary.md §THE ORDER THROUGH THE GIVER, THE MOTIVE, THE FORCE
// RECORD. Prints "U <name> ok|FAIL why" and "U-count n". The host is a recorder: it counts every start and keeps every trace record.
using System;
using System.Collections.Generic;
using K = JawaBench.BridgeTools.JawaBenchForceCore;

namespace JawaBench.BridgeTools
{
    internal sealed class FakeHost : IForceHost
    {
        public bool GiverGives = true;
        public string GiverReason = "Cannot rescue: no fallen comrade in a pit";
        public string Lord = "lord 7 LordJob_AssaultColony";
        public int AskedGiver, StartedGiven, StartedRaw, MotivesSet;
        public readonly List<string> Records = new List<string>();
        public string Running;              // the job the pawn runs now

        public string WhyNoActor(string actor) { return actor == "ghost" ? "no pawn 'ghost' is bound or found" : null; }
        public GiverAnswer AskGiver(OrderReq r)
        {
            AskedGiver++;
            if (r.Giver == "NoSuchGiver") return new GiverAnswer { Found = false };
            return GiverGives ? new GiverAnswer { Given = true, Via = r.Giver, Node = "duty", Job = "RM_RaiderFetchFallen#41" }
                              : new GiverAnswer { Given = false, Via = r.Giver, Node = "duty", Reason = GiverReason };
        }
        public StartAnswer StartGiven(OrderReq r, GiverAnswer a) { StartedGiven++; Running = (string)a.Job; return new StartAnswer { Started = true, Job = Running }; }
        public StartAnswer StartRaw(OrderReq r) { StartedRaw++; Running = r.JobDef + "#99"; return new StartAnswer { Started = true, Job = Running }; }
        public string LordOf(string actor) { return Lord; }
        public MotiveAnswer SetMotive(MotiveReq m) { MotivesSet++; return new MotiveAnswer { Done = true, Before = Lord, After = "lord 7 " + m.LordJob, Duty = "AssaultColony" }; }
        public long Tick() { return 1000; }
        public long Record(string rec, string fields) { Records.Add(rec + " {" + fields + "}"); return Records.Count; }
    }

    internal static class Program
    {
        private static string First(params string[] fails) { foreach (var f in fails) if (f != null) return "FAIL " + f; return "ok"; }
        private static string Need(bool c, string why) { return c ? null : why; }
        private static object G(Dictionary<string, object> d, string k) { object v; return d != null && d.TryGetValue(k, out v) ? v : null; }
        private static bool Is(object v, bool want) { return v is bool && (bool)v == want; }
        private static bool Num(object v, int want) { return v is double && (double)v == want; }

        private static OrderReq Rescue(string level, string els = null)
        {
            return new OrderReq { Actor = "rescuer", Level = level, Giver = "JobGiver_RM_FetchFallen", JobDef = "RM_RaiderFetchFallen", Target = "fallen", Fallback = els };
        }

        // 1
        private static string ARefusedGiverOrderReturnsTheReasonAndStartsNothing()
        {
            var h = new FakeHost { GiverGives = false };
            var log = new K.ForceLog();
            var r = K.Order(Rescue("giver"), h, log, "s1");
            var e = log.Entries.Count == 1 ? log.Entries[0] : null;
            return First(Need(Is(G(r, "success"), true), "a giver's refusal is a fact, not a refused act: success must be true, got " + G(r, "success") + " " + G(r, "message")),
                         Need(Is(G(r, "given"), false), "given must be false"),
                         Need((G(r, "reason") as string) == h.GiverReason, "the reason must be the giver's own words, got '" + G(r, "reason") + "'"),
                         Need(h.AskedGiver == 1, "the giver must be asked once, was asked " + h.AskedGiver),
                         Need(h.StartedGiven == 0 && h.StartedRaw == 0 && h.Running == null, "no job may start: given " + h.StartedGiven + ", raw " + h.StartedRaw),
                         Need(Is(G(r, "started"), false), "started must be false"),
                         Need(G(r, "levelUsed") == null, "nothing was forced: levelUsed must be null, got " + G(r, "levelUsed")),
                         Need(e != null && !e.Used.HasValue && e.Asked == 3 && e.Reason == h.GiverReason, "the record must say asked 3, used none, with the reason"),
                         Need(h.Records.Count == 1 && h.Records[0].Contains("\"used\":null"), "one force record with used null: " + string.Join(" | ", h.Records)));
        }

        // 2
        private static string TheForceLevelRecordedIsTheLevelUsed()
        {
            var h = new FakeHost { GiverGives = false };
            var log = new K.ForceLog();
            var r = K.Order(Rescue("giver", "raw"), h, log, "s1");
            var e = log.Entries.Count == 1 ? log.Entries[0] : null;
            var h2 = new FakeHost { GiverGives = true };
            var log2 = new K.ForceLog();
            var r2 = K.Order(Rescue("giver"), h2, log2, "s1");
            var e2 = log2.Entries.Count == 1 ? log2.Entries[0] : null;
            var sum = log.Summary("s1");
            var one = G(sum, "rescuer") as Dictionary<string, object>;
            return First(Need(Num(G(r, "levelAsked"), 3) && Num(G(r, "levelUsed"), 4), "a refused giver order with fallback=raw: asked 3 used 4, got " + G(r, "levelAsked") + " " + G(r, "levelUsed")),
                         Need(h.StartedGiven == 0 && h.StartedRaw == 1, "fallback=raw starts the raw job only"),
                         Need(e != null && e.Asked == 3 && e.Used == 4 && e.Via == "raw", "the record must say asked 3, used 4, via raw"),
                         Need(h.Records.Count == 1 && h.Records[0].Contains("\"asked\":3") && h.Records[0].Contains("\"used\":4"), "the trace record must say asked 3 used 4: " + string.Join(" | ", h.Records)),
                         Need(one != null && Num(one["max"], 4), "the summary's highest level used must be 4"),
                         Need(Num(G(r2, "levelUsed"), 3) && e2 != null && e2.Used == 3 && e2.Via == "JobGiver_RM_FetchFallen", "a giver that gives: used 3, via the giver"),
                         Need(h2.StartedGiven == 1 && h2.StartedRaw == 0, "a given order starts the giver's job, never a raw one"),
                         Need(log2.Summary("other").Count == 0, "the summary is of one session"));
        }

        // 3
        private static string AMotiveForAPawnWithNoLordIsRefusedByName()
        {
            var h = new FakeHost { Lord = null };
            var log = new K.ForceLog();
            var r = K.SetMotive(new MotiveReq { Actor = "raider1", LordJob = "LordJob_AssaultColony" }, h, log, "s1");
            var h2 = new FakeHost();
            var log2 = new K.ForceLog();
            var r2 = K.SetMotive(new MotiveReq { Actor = "raider1", LordJob = "LordJob_AssaultColony" }, h2, log2, "s1");
            return First(Need(Is(G(r, "success"), false) && (G(r, "refused") as string) == "NO_LORD", "want refused NO_LORD, got " + G(r, "refused") + " " + G(r, "message")),
                         Need(((G(r, "message") as string) ?? "").Contains("raider1"), "the refusal names the pawn"),
                         Need(h.MotivesSet == 0 && log.Entries.Count == 0 && h.Records.Count == 0, "a refused motive changes nothing and records nothing"),
                         Need(Is(G(r2, "success"), true) && h2.MotivesSet == 1 && log2.Entries.Count == 1 && log2.Entries[0].Used == 2, "a pawn with a lord takes the motive at level 2"));
        }

        // 4
        private static string ARawJobIsRecordedAsRaw()
        {
            var h = new FakeHost();
            var log = new K.ForceLog();
            var r = K.Order(Rescue("raw"), h, log, "s1");
            var e = log.Entries.Count == 1 ? log.Entries[0] : null;
            return First(Need(Is(G(r, "success"), true) && Is(G(r, "started"), true), "the raw order must start: " + G(r, "message")),
                         Need(h.AskedGiver == 0 && h.StartedGiven == 0 && h.StartedRaw == 1, "a raw order asks no giver"),
                         Need(Num(G(r, "levelAsked"), 4) && Num(G(r, "levelUsed"), 4), "asked 4 used 4"),
                         Need((G(r, "via") as string) == "raw" && e != null && e.Via == "raw" && e.Used == 4, "via raw on the reply and the record"),
                         Need((G(r, "note") as string) == K.NotReachable, "the reply says '" + K.NotReachable + "'"),
                         Need(h.Records.Count == 1 && h.Records[0].Contains("\"via\":\"raw\""), "the trace record says via raw"));
        }

        private static int Main()
        {
            var units = new List<KeyValuePair<string, Func<string>>>
            {
                new KeyValuePair<string, Func<string>>("a_refused_giver_order_returns_the_reason_and_starts_nothing", ARefusedGiverOrderReturnsTheReasonAndStartsNothing),
                new KeyValuePair<string, Func<string>>("the_force_level_recorded_is_the_level_used", TheForceLevelRecordedIsTheLevelUsed),
                new KeyValuePair<string, Func<string>>("a_motive_for_a_pawn_with_no_lord_is_refused_by_name", AMotiveForAPawnWithNoLordIsRefusedByName),
                new KeyValuePair<string, Func<string>>("a_raw_job_is_recorded_as_raw", ARawJobIsRecordedAsRaw),
            };
            foreach (var u in units)
            {
                string v;
                try { v = u.Value(); } catch (Exception e) { v = "FAIL threw " + e.GetType().Name + ": " + e.Message; }
                Console.WriteLine("U " + u.Key + " " + v);
            }
            Console.WriteLine("U-count " + units.Count);
            return 0;
        }
    }
}
