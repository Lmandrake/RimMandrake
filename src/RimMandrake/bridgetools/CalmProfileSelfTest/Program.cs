// Units for JawaBenchCalmProfileCore.cs (the PRODUCTION file, or a planted copy). One unit per C# part of a check of
// RIMMANDRAKE_BUILD_CALM_PROFILE_BREACH_LOG_AND_LEASE (design/specs/2026-11-23-bridge-v2/boundary.md §CALM PROFILE).
// Prints "U <name> ok|FAIL why" and "U-count n". The session is driven as JawaBenchCalmProfile.cs drives it: Parse the tool's keys,
// Arm with an applier per control, Call before each write, Tick each frame, Leave. The gates are the real JawaBenchGatesCore.Gate.
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using P = JawaBench.BridgeTools.JawaBenchCalmProfileCore;
using K = JawaBench.BridgeTools.JawaBenchGatesCore;

namespace JawaBench.BridgeTools
{
    internal sealed class FakeSink : ICastSink
    {
        public readonly List<JsonElement> Rows = new List<JsonElement>();
        long _seq;
        public long EmitTap(string rec, string fields)
        {
            Rows.Add(JsonDocument.Parse("{\"rec\":\"" + rec + "\"," + fields + "}").RootElement);
            return ++_seq;
        }
    }

    internal static class Program
    {
        static int _n, _bad;
        static readonly object Game = new object(), OtherGame = new object();

        static void Check(string name, Action f)
        {
            _n++;
            string w = null;
            try { f(); } catch (Exception e) { w = e.GetType().Name + ": " + e.Message; }
            if (w != null) _bad++;
            Console.WriteLine("U " + name + " " + (w == null ? "ok" : "FAIL " + w));
        }

        static void Eq(object a, object b, string what) { if (!Equals(a, b)) throw new Exception(what + ": got " + a + ", want " + b); }
        static void True(bool b, string what) { if (!b) throw new Exception(what); }

        static P.Profile Prof(params string[] kv)
        {
            var d = new Dictionary<string, string> { ["driver"] = "A" };
            for (int i = 0; i + 1 < kv.Length; i += 2) d[kv[i]] = kv[i + 1];
            string why;
            var p = P.Parse(d, out why);
            True(p != null, "parse refused: " + why);
            return p;
        }

        /// <summary>An applier that reads every mechanism back in place, with no entries; `calls` counts the controls offered.</summary>
        static Func<P.ControlDef, P.Record, P.Applied> AllOk(List<string> calls, Func<string, Func<long>> stopped = null)
        {
            return (c, r) => { calls?.Add(c.Name); return P.Applied.Ok(null, stopped?.Invoke(c.Name)); };
        }

        static int Main()
        {
            Check("a_control_reads_held_only_with_its_certificate_line", () =>
            {
                var gate = P.Catalog["standard"][1].First(c => c.Name == P.IncidentGate);
                var sw = P.Catalog["standard"][1].First(c => c.Name == P.Storyteller);
                string why;
                Eq(P.StatusOf(gate, true, new[] { "incident.held" }, out why), P.Held, "read back, with its line");
                Eq(P.StatusOf(gate, true, new[] { "gate.quest.held" }, out why), P.Unproven, "read back, another control's line only");
                Eq(P.StatusOf(gate, true, null, out why), P.Unproven, "read back, no certificate");
                Eq(P.StatusOf(gate, false, new[] { "incident.held" }, out why), P.CouldNotArm, "with its line, but not read back");
                Eq(P.StatusOf(sw, true, new[] { "incident.held", "gate.quest.held", "gate.mental.held", "storyteller" }, out why), P.Unproven, "a control with no line");
                var s = new P.Session();
                True(s.Arm(Prof("certified", "incident.held,storyteller"), Game, false, 0, AllOk(null)) == null, "arm refused");
                Eq(s.State[P.IncidentGate].Status, P.Held, "the session: incident gate with its line");
                Eq(s.State[P.QuestGate].Status, P.Unproven, "the session: quest gate without its line");
                Eq(s.State[P.Storyteller].Status, P.Unproven, "the session: a switch, whatever the caller certified");
            });

            Check("a_scene_exception_opens_one_gate_for_one_named_event", () =>
            {
                var g = new K.Gate(K.Incident);
                True(g.Arm(Game, false, "") == null, "gate arm refused");
                var s = new P.Session();
                True(s.Arm(Prof(), Game, false, 0, AllOk(null)) == null, "arm refused");
                True(s.Except(g, "RaidEnemy") == null, "exception refused");
                True(s.Except(g, "ManhunterPack") == null, "second exception refused");
                bool Try(string n) => g.Decide(true, true, Game, false, n, () => "caller", () => "detail", 10);
                True(Try("RaidEnemy"), "the excepted event did not go through");
                True(!Try("RaidEnemy"), "the excepted event went through twice");
                True(!Try("Eclipse"), "another event went through");
                var lines = s.Leave("scene left");
                True(lines.Any(l => l.Contains("exception incident:RaidEnemy closed, used")), "the used exception is not named closed: " + string.Join(" | ", lines));
                True(lines.Any(l => l.Contains("exception incident:ManhunterPack closed UNUSED")), "the unused exception is not named: " + string.Join(" | ", lines));
                True(!Try("ManhunterPack"), "a closed exception still lets its event through");
                Eq(g.AllowLeft(), "", "allow entries left after leave");
                True(s.Except(g, "RaidEnemy") != null, "an exception after leave was taken");

                // across a re-arm after a load: the unused exception stays open on the new game, the used one is closed and named
                var g2 = new K.Gate(K.Incident);
                object cur = Game;
                Func<P.ControlDef, P.Record, P.Applied> armG = (c, r) =>
                {
                    if (c.Name == P.IncidentGate) { True(g2.Arm(cur, false, "") == null, "gate re-arm refused"); r.Add(c.Name, P.PutBack, "off", () => { g2.Release("put back"); return null; }, () => g2.On ? "on" : "off"); }
                    return P.Applied.Ok();
                };
                var s2 = new P.Session();
                True(s2.Arm(Prof(), Game, false, 0, armG) == null, "arm refused");
                True(s2.Except(g2, "RaidEnemy") == null && s2.Except(g2, "Eclipse") == null, "exceptions refused");
                True(g2.Decide(true, true, Game, false, "Eclipse", () => "c", () => "d", 1), "the excepted Eclipse did not go through");
                cur = OtherGame;
                var rl = new List<string>();
                True(s2.Rearm(OtherGame, false, 5, armG, rl) == null, "re-arm refused");
                True(rl.Any(l => l.Contains("exception incident:Eclipse closed, used")), "the used exception is not named at the re-arm: " + string.Join(" | ", rl));
                True(rl.Any(l => l.Contains("exception incident:RaidEnemy carried")), "the unused exception is not carried: " + string.Join(" | ", rl));
                True(s2.OpenExceptions().SequenceEqual(new[] { "incident:RaidEnemy" }), "open after the re-arm: " + string.Join(",", s2.OpenExceptions()));
                True(g2.Decide(true, true, OtherGame, false, "RaidEnemy", () => "c", () => "d", 9), "the carried exception did not let its event through on the new game");
                True(!g2.Decide(true, true, OtherGame, false, "RaidEnemy", () => "c", () => "d", 10), "the carried exception let its event through twice");
                var l2 = s2.Leave("scene left");
                True(l2.Any(l => l.Contains("exception incident:RaidEnemy closed, used")), "the carried exception is not closed at leave: " + string.Join(" | ", l2));
            });

            Check("a_hold_on_needs_is_two_entries", () =>
            {
                var r = new P.Record();
                r.AddNeedsHold("pawn 12", () => null, () => "not held");
                var l = r.Live;
                Eq(l.Count, 2, "entries of one needs hold");
                True(l.Count(e => e.Control == P.NeedsHold && e.Class == P.PutBack) == 1, "no PUT BACK entry for the hold");
                True(l.Count(e => e.Control == P.NeedsHold && e.Class == P.NotUndone && e.Reach == "save") == 1, "no NOT UNDONE entry of reach save for what did not happen");
                var npb = new List<string>();
                r.PutBackAll("leave", npb);
                Eq(npb.Count, 0, "not put back: " + string.Join(" | ", npb));
                True(r.NotUndoneLines().Any(x => x.StartsWith("needs_hold (NOT UNDONE, reach save)")), "what did not happen is not listed after leave");
            });

            Check("the_put_back_runs_in_reverse_order_with_read_back", () =>
            {
                var r = new P.Record();
                var seen = new List<string>();
                var vals = new Dictionary<string, string> { ["a"] = "x", ["b"] = "x", ["c"] = "x" };
                foreach (var n in new[] { "a", "b", "c" })
                {
                    var name = n;
                    r.Add(name, n == "b" ? P.GivenBack : P.PutBack, "old " + name, () => { seen.Add("put " + name); vals[name] = "old " + name; return null; },
                          () => { seen.Add("read " + name); return vals[name]; });
                }
                var npb = new List<string>();
                r.PutBackAll("leave", npb);
                Eq(string.Join(",", seen), "put c,read c,put b,read b,put a,read a", "order");
                Eq(npb.Count, 0, "not put back");
                Eq(r.Live.Count, 0, "entries left live");
            });

            Check("a_lease_that_ran_out_puts_back", () =>
            {
                var s = new P.Session();
                int put = 0;
                True(s.Arm(Prof("minutes", "1"), Game, false, 100, (c, r) =>
                {
                    if (c.Name == P.Storyteller) r.Add(c.Name, P.PutBack, "True", () => { put++; return null; }, () => put > 0 ? "True" : "False");
                    return P.Applied.Ok();
                }) == null, "arm refused");
                bool rearm;
                Eq(s.Tick(130, Game, out rearm), null, "a leave before the lease ended");
                Eq(put, 0, "put back before the lease ended");
                True(s.Armed, "off before the lease ended");
                var l = s.Tick(160, Game, out rearm);
                True(l != null && l.Any(x => x.Contains("lease ended")), "no leave at the end of the lease");
                Eq(put, 1, "put-backs at the end of the lease");
                True(!s.Armed && !s.L.On, "the profile is still on after its lease");
                Eq(s.L.LastEnd, "lease ended", "the lease's end");
                Eq(s.Tick(200, Game, out rearm), null, "a second leave");
                Eq(put, 1, "put back twice");

                // a re-arm after a load keeps the deadline: a load never renews the lease
                var s3 = new P.Session();
                True(s3.Arm(Prof("minutes", "1"), Game, false, 100, AllOk(null)) == null, "arm refused");
                Eq(s3.Tick(130, OtherGame, out rearm), null, "a leave at the load");
                True(rearm, "a game change did not ask for a re-arm");
                True(s3.Rearm(OtherGame, false, 130, AllOk(null), new List<string>()) == null, "re-arm refused");
                Eq(s3.Tick(159, OtherGame, out rearm), null, "a leave before the first deadline");
                True(!rearm, "a re-arm asked again on the same game");
                var l3 = s3.Tick(160, OtherGame, out rearm);
                True(l3 != null && !s3.Armed, "the lease did not end at its first deadline after a re-arm");
            });

            Check("a_value_that_could_not_be_put_back_is_named", () =>
            {
                var r = new P.Record();
                bool aPut = false;
                r.Add("a", P.PutBack, "1", () => { aPut = true; return null; }, () => "1");
                r.Add("b", P.PutBack, "1", () => { throw new InvalidOperationException("gone"); }, () => "1");
                r.Add("c", P.PutBack, "1", () => null, () => "2");
                var npb = new List<string>();
                r.PutBackAll("leave", npb);
                True(aPut, "an entry after a failed one was not put back");
                True(npb.Any(x => x.StartsWith("b (PUT BACK)") && x.Contains("gone")), "a put-back that threw is not named: " + string.Join(" | ", npb));
                True(npb.Any(x => x.StartsWith("c (PUT BACK)") && x.Contains("reads '2'")), "a value that reads otherwise is not named: " + string.Join(" | ", npb));
                Eq(npb.Count, 2, "named");
            });

            Check("a_destructive_control_is_refused_under_campaign_only", () =>
            {
                var calls = new List<string>();
                var s = new P.Session();
                True(s.Arm(Prof("clear", "true"), Game, true, 0, AllOk(calls)) == null, "arm refused");
                Eq(calls.Count, 0, "controls applied under CAMPAIGN");
                True(s.State.Values.All(x => x.Status == P.Refused), "a control not refused under CAMPAIGN");
                True(s.State[P.ClearSite].Why.Contains("DESTRUCTIVE"), "the destructive control is not named as destructive: " + s.State[P.ClearSite].Why);
                s.Leave("done");
                var s2 = new P.Session();
                True(s2.Arm(Prof("clear", "true"), Game, false, 0, AllOk(calls)) == null, "arm refused on a test save");
                True(calls.Contains(P.ClearSite), "the destructive control was not applied on a test save");
                True(s2.State[P.ClearSite].Status != P.Refused, "the destructive control refused on a test save");
            });

            Check("attempts_stopped_and_scheduling_switched_off_are_two_numbers", () =>
            {
                var s = new P.Session();
                True(s.Arm(Prof(), Game, false, 0, AllOk(null, n => n == P.IncidentGate ? (Func<long>)(() => 2) : n == P.Wild ? (Func<long>)(() => 5) : null)) == null, "arm refused");
                Eq(s.AttemptsStopped(), 7L, "attempts stopped (2 incidents held, 5 spawner ticks skipped)");
                Eq(s.SchedulingSwitchedOff(), 4, "schedulers switched off (storyteller, mental, diseases, queue)");
                var s2 = new P.Session();
                True(s2.Arm(Prof("except", "storyteller,incident_queue"), Game, false, 0, AllOk(null)) == null, "arm refused");
                Eq(s2.AttemptsStopped(), 0L, "attempts stopped with nothing held");
                Eq(s2.SchedulingSwitchedOff(), 2, "schedulers switched off with two excepted");
            });

            Check("a_second_driver_is_an_apparatus_breach", () =>
            {
                var s = new P.Session();
                var sink = new FakeSink();
                s.B.Sink = () => sink;
                True(s.Arm(Prof(), Game, false, 0, AllOk(null)) == null, "arm refused");
                Eq(s.Call("A", "renew", 5), null, "the owner's own call");
                Eq(s.B.OfClass(P.Apparatus), 0L, "a breach for the owner's call");
                var why = s.Call("B", "leave", 7);
                True(why != null && why.StartsWith("REFUSED"), "a second driver's write was not refused");
                Eq(s.B.OfClass(P.Apparatus), 1L, "APPARATUS breaches");
                var b = s.B.Since(0).Single();
                True(b.What.Contains("'B'") && b.What.Contains("'A'"), "the breach does not name both drivers: " + b.What);
                Eq(b.Tick, 7L, "the breach's tick");
                True(s.Armed, "a refused write changed the profile");
                var d = new Dictionary<string, string> { ["driver"] = "B" };
                string r;
                True(s.Arm(P.Parse(d, out r), Game, false, 0, AllOk(null)) != null, "a second driver armed over the first");
                Eq(s.P.Driver, "A", "the owner after a refused arm");
                Eq(s.B.OfClass(P.Apparatus), 2L, "APPARATUS breaches after a refused arm");
                Eq(sink.Rows.Count(x => x.GetProperty("rec").GetString() == "breach" && x.GetProperty("class").GetString() == P.Apparatus), 2, "breach rows in the trace");
            });

            Check("unknown_profile_keys_are_refused", () =>
            {
                string why;
                Func<Dictionary<string, string>, string> refused = d => { var p = P.Parse(d, out why); return p == null ? why : null; };
                var w = refused(new Dictionary<string, string> { ["driver"] = "A", ["excpet"] = "weather" });
                True(w != null && w.Contains("'excpet'"), "a misspelt key was taken: " + w);
                w = refused(new Dictionary<string, string> { ["driver"] = "A", ["profile"] = "fancy" });
                True(w != null && w.Contains("'fancy'"), "an unknown profile was taken: " + w);
                w = refused(new Dictionary<string, string> { ["driver"] = "A", ["version"] = "9" });
                True(w != null && w.Contains("'9'"), "an unknown version was taken: " + w);
                w = refused(new Dictionary<string, string> { ["driver"] = "A", ["except"] = "weather,nosuch" });
                True(w != null && w.Contains("'nosuch'"), "an exception that names no control was taken: " + w);
                w = refused(new Dictionary<string, string> { ["driver"] = "A", ["minutes"] = "soon" });
                True(w != null && w.Contains("'soon'"), "a bad lease was taken: " + w);
                w = refused(new Dictionary<string, string> { ["profile"] = "standard" });
                True(w != null && w.Contains("driver"), "a profile with no driver was taken: " + w);
                var ok = P.Parse(new Dictionary<string, string> { ["driver"] = "A", ["except"] = "weather", ["version"] = "1" }, out why);
                True(ok != null && ok.Id == "standard/1" && ok.Except.Contains("weather"), "a good profile was refused: " + why);
            });

            Check("a_not_undone_control_is_listed_as_such", () =>
            {
                var s = new P.Session();
                bool undone = false;
                True(s.Arm(Prof("clear", "true"), Game, false, 0, (c, r) =>
                {
                    if (c.Name == P.ClearSite) r.Add(c.Name, P.NotUndone, null, () => { undone = true; return null; }, null, "save", "3 hostiles vanished");
                    return P.Applied.Ok();
                }) == null, "arm refused");
                var lines = s.Leave("leave");
                True(!undone, "a NOT UNDONE entry was put back");
                Eq(s.LastNotPutBack.Count, 0, "a NOT UNDONE entry counted as not put back");
                True(!lines.Any(l => l.StartsWith("clear_site:")), "a NOT UNDONE entry is in the put-back lines");
                True(s.R.NotUndoneLines().Any(x => x == "clear_site (NOT UNDONE, reach save): 3 hostiles vanished"), "not listed: " + string.Join(" | ", s.R.NotUndoneLines()));
            });

            Console.WriteLine("U-count " + _n);
            return _bad == 0 ? 0 : 1;
        }
    }
}
