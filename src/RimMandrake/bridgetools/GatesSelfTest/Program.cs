// Units for JawaBenchGatesCore.cs (the PRODUCTION file, or a planted copy). One unit per C# part of a check of
// RIMMANDRAKE_BUILD_INCIDENT_QUEST_MENTAL_GATES_BEFORE_CERTIFICATE (design/specs/2026-11-23-bridge-v2/boundary.md §SCENE GATES).
// Prints "U <name> ok|FAIL why" and "U-count n". A gate is called as the Verse prefixes call it: Decide(onMain, __runOriginal,
// the game, CAMPAIGN, the name, the caller, the detail, the tick); the queue as JawaBenchGates.HoldQueue / GiveBackQueue call it.
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using K = JawaBench.BridgeTools.JawaBenchGatesCore;

namespace JawaBench.BridgeTools
{
    /// <summary>The live run's tap sink: rows, or outside (-2), or a full writer (-1), or a sink that throws.</summary>
    internal sealed class FakeSink : ICastSink
    {
        public bool Running = true, DropAll, Throw;
        public readonly List<JsonElement> Rows = new List<JsonElement>();
        long _seq;
        public long EmitTap(string rec, string fields)
        {
            if (Throw) throw new InvalidOperationException("the sink threw");
            if (!Running) return -2;
            if (DropAll) return -1;
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
        static string Str(JsonElement e, string k) { var v = e.GetProperty(k); return v.ValueKind == JsonValueKind.Null ? null : v.ToString(); }

        static (K.Gate g, FakeSink sink) Armed(string kind, string allow)
        {
            var g = new K.Gate(kind);
            var sink = new FakeSink();
            g.Sink = () => sink;
            var why = g.Arm(Game, false, allow);
            True(why == null, "arm refused: " + why);
            return (g, sink);
        }

        /// <summary>One attempt through the prefix half, on the main thread, with the original still to run.</summary>
        static bool Try(K.Gate g, string name, string caller = "RimWorld.Storyteller.TryFire", long tick = 5000, object game = null, bool campaign = false)
        {
            return g.Decide(true, true, game ?? Game, campaign, name, () => caller, () => "detail of " + name, tick);
        }

        static K.QEntry E(string def, long fire, long retryEnd, bool tried) { return new K.QEntry { Def = def, FireTick = fire, RetryEnd = retryEnd, Tried = tried, Ref = def }; }

        // ------------------------------------------------------------------------------------------------ 1
        static void AllowOnce()
        {
            var (g, sink) = Armed(K.Incident, "RaidEnemy");
            True(Try(g, "RaidEnemy"), "the named incident on the allow list was held");
            True(!Try(g, "RaidEnemy"), "the named incident went through a second time on one allow entry");
            True(!Try(g, "ManhunterPack"), "an incident not on the allow list went through");
            Eq(g.Allowed, 1L, "allowed");
            Eq(g.Held, 2L, "held");
            Eq(g.Attempts, 3L, "attempts");
            Eq(g.AllowLeft(), "", "allow entries left");
            Eq(sink.Rows.Count(r => Str(r, "outcome") == "allowed"), 1, "rows of the allowed attempt");
            // a name listed twice goes through twice, case aside
            var (g2, _) = Armed(K.Incident, "RaidEnemy, raidenemy");
            True(Try(g2, "RaidEnemy") && Try(g2, "RAIDENEMY") && !Try(g2, "RaidEnemy"), "a name listed twice did not go through exactly twice");
        }

        // ------------------------------------------------------------------------------------------------ 2
        static void HeldCountedWithCaller()
        {
            var (g, sink) = Armed(K.Mental, "");
            True(!Try(g, "Berserk", "RimWorld.MentalBreaker.TryDoMentalBreak", 7001), "an attempt with nothing allowed went through");
            True(!Try(g, "Wander_Sad", "RimWorld.Hediff_Psychic.Tick", 7002), "a second attempt went through");
            Eq(g.Held, 2L, "held count");
            Eq(g.Attempts, 2L, "attempt count");
            var rows = g.Rows();
            Eq(rows.Count, 2, "log rows");
            Eq(rows[0].Caller, "RimWorld.MentalBreaker.TryDoMentalBreak", "the first held attempt's caller");
            Eq(rows[1].Caller, "RimWorld.Hediff_Psychic.Tick", "the second held attempt's caller");
            Eq(rows[0].Tick, 7001L, "the held attempt's tick");
            Eq(rows[0].Outcome, "held", "outcome");
            Eq(sink.Rows.Count, 2, "trace rows");
            var r0 = sink.Rows[0];
            Eq(Str(r0, "rec"), "gate", "the trace record");
            Eq(Str(r0, "gate"), "mental", "the gate on the row");
            Eq(Str(r0, "name"), "Berserk", "the name on the row");
            Eq(Str(r0, "caller"), "RimWorld.MentalBreaker.TryDoMentalBreak", "the caller on the row");
            Eq(Str(r0, "outcome"), "held", "the outcome on the row");
            // a caller that cannot be read is named as unknown, and the attempt is still held and counted
            True(!g.Decide(true, true, Game, false, "Berserk", () => { throw new InvalidOperationException("no stack"); }, null, 7003), "a throwing caller let it through");
            True(g.Rows().Last().Caller.StartsWith("unknown"), "a caller that threw is not named unknown");
            Eq(g.Held, 3L, "held after a caller that threw");
        }

        // ------------------------------------------------------------------------------------------------ 3
        static void OffChangesNothing()
        {
            var g = new K.Gate(K.Quest);
            var sink = new FakeSink();
            g.Sink = () => sink;
            int calls = 0;
            string Caller() { calls++; return "x"; }
            for (int i = 0; i < 3; i++)
                True(g.Decide(true, true, Game, false, "OpportunitySite_ItemStash", Caller, () => { calls++; return "d"; }, 100 + i), "an off gate held an attempt");
            True(g.Decide(false, true, Game, false, "Q", Caller, null, 1), "an off gate held a foreign call");
            True(g.Decide(true, false, Game, false, "Q", Caller, null, 1), "an off gate held a skipped original");
            Eq(g.Attempts + g.Held + g.Allowed + g.ForeignPassed + g.AlreadySkipped + g.Faults + g.Outside, 0L, "an off gate counted something");
            Eq(g.Rows().Count, 0, "an off gate logged a row");
            Eq(sink.Rows.Count, 0, "an off gate wrote a trace row");
            Eq(calls, 0, "an off gate read the caller or the detail");
            // armed then released: off again, the same
            var (g2, s2) = Armed(K.Quest, "");
            g2.Release("the scene left");
            long before = g2.Attempts + g2.Held;
            True(Try(g2, "Q"), "a released gate held an attempt");
            Eq(g2.Attempts + g2.Held, before, "a released gate counted");
            Eq(s2.Rows.Count, 0, "a released gate wrote a row");
            Eq(g2.LastRelease, "the scene left", "the release reason");
        }

        // ------------------------------------------------------------------------------------------------ 4, 5
        static List<K.QEntry> HoldAndReturn(long heldFor, out K.QueueHold q)
        {
            q = new K.QueueHold();
            var entries = new List<K.QEntry>
            {
                E("RaidEnemy", 12000, 12000, false),                      // fires at 12000, no retry
                E("TraderCaravanArrival", 9000, 9000 + 30000, true),     // tried once at 9000, retries until 39000
                E("WandererJoin", 15000, 15000 + 60000, false),          // fires at 15000, may retry until 75000
            };
            var rep = new List<string>();
            True(q.Hold(Game, false, 10000, entries, rep) == null, "the hold was refused");
            Eq(rep.Count, 0, "the hold reported an entry that is inside its window");
            True(q.Holding && q.Count == 3, "three entries are not held aside");
            var back = q.GiveBack(Game, 10000 + heldFor, rep);
            Eq(rep.Count, 0, "the give-back reported a loss: " + string.Join("; ", rep));
            Eq(back.Count, 3, "entries given back");
            True(!q.Holding, "the queue reads held after the give-back");
            return back;
        }

        static void FireTickMoved()
        {
            K.QueueHold q;
            var back = HoldAndReturn(2500, out q);
            var by = back.ToDictionary(e => e.Def);
            Eq(by["RaidEnemy"].FireTick, 14500L, "RaidEnemy's fire tick (12000 + 2500 held)");
            Eq(by["TraderCaravanArrival"].FireTick, 11500L, "the tried entry's fire tick (9000 + 2500 held)");
            Eq(by["WandererJoin"].FireTick, 17500L, "WandererJoin's fire tick (15000 + 2500 held)");
            True(by["TraderCaravanArrival"].Tried, "the tried flag was lost");
            Eq(q.Returned, 3L, "returned count");
        }

        static void RetryWindowMoved()
        {
            K.QueueHold q;
            var back = HoldAndReturn(2500, out q);
            var by = back.ToDictionary(e => e.Def);
            Eq(by["TraderCaravanArrival"].RetryEnd, 41500L, "the tried entry's retry window end (39000 + 2500 held)");
            Eq(by["TraderCaravanArrival"].RetryDuration, 30000L, "the tried entry's retry duration (the engine's retryDurationTicks)");
            Eq(by["WandererJoin"].RetryEnd, 77500L, "WandererJoin's retry window end");
            Eq(by["WandererJoin"].RetryDuration, 60000L, "WandererJoin's retry duration");
            Eq(by["RaidEnemy"].RetryDuration, 0L, "a no-retry entry keeps no retry");
            // GPT's case, said plainly: a tried entry given back after a long hold must not be past its window at once
            var back2 = HoldAndReturn(40000, out q);
            var t = back2.Single(e => e.Def == "TraderCaravanArrival");
            True(!K.QueueHold.PastWindow(t, 50000), "the tried entry given back after 40000 ticks held is past its window at once (it would expire)");
        }

        // ------------------------------------------------------------------------------------------------ 6
        static void ExpiredReported()
        {
            var q = new K.QueueHold();
            var entries = new List<K.QEntry>
            {
                E("TraderCaravanArrival", 2000, 2000 + 3000, true),      // tried, its window ended at 5000: dropped on the next tick
                E("RaidEnemy", 12000, 12000, false),
            };
            var rep = new List<string>();
            True(q.Hold(Game, false, 10000, entries, rep) == null, "the hold was refused");
            Eq(rep.Count, 1, "lines reported at the hold");
            True(rep[0].Contains("TraderCaravanArrival") && rep[0].Contains("past its retry window"), "the hold did not name the expired entry: " + rep[0]);
            var rep2 = new List<string>();
            var back = q.GiveBack(Game, 11000, rep2);
            Eq(back.Count, 1, "entries given back");
            Eq(rep2.Count, 1, "lines reported at the give-back");
            True(rep2[0].Contains("TraderCaravanArrival"), "the give-back did not name the entry it did not return: " + rep2[0]);
            Eq(q.Expired, 1L, "the expired count");
            Eq((long)back.Count + q.Expired + q.Lost, 2L, "every entry held is returned or named");
            // a give-back into another game returns nothing and names each entry
            var q2 = new K.QueueHold();
            q2.Hold(Game, false, 100, new List<K.QEntry> { E("A", 200, 200, false), E("B", 300, 300, false) }, null);
            var rep3 = new List<string>();
            Eq(q2.GiveBack(OtherGame, 150, rep3).Count, 0, "entries given back into another game");
            Eq(rep3.Count, 2, "lines for the entries the game change kept");
            Eq(q2.Lost, 2L, "the lost count");
        }

        // ------------------------------------------------------------------------------------------------ 7, 8: the hook rules of a gate site
        static void HookRules(string kind)
        {
            var (g, sink) = Armed(kind, "");
            // thread: a foreign call runs, is counted, reads nothing and records nothing
            int calls = 0;
            True(g.Decide(false, true, Game, false, "N", () => { calls++; return "c"; }, () => { calls++; return "d"; }, 1), "a foreign call was held");
            Eq(g.ForeignPassed, 1L, "foreign calls counted");
            Eq(calls, 0, "a foreign call read the caller or the detail");
            Eq(g.Attempts, 0L, "a foreign call counted as an attempt");
            // skipped original: another prefix skipped it; not ours to hold, counted, no row
            True(g.Decide(true, false, Game, false, "N", () => "c", null, 2), "an original another prefix skipped was decided again");
            Eq(g.AlreadySkipped, 1L, "skips by another prefix counted");
            Eq(g.Held, 0L, "a skip by another prefix counted as held");
            // reentrancy: an attempt that starts inside another attempt's decision is decided on its own
            bool inner = true;
            bool outer = g.Decide(true, true, Game, false, "Outer", () => { inner = g.Decide(true, true, Game, false, "Inner", () => "inner-caller", null, 3); return "outer-caller"; }, null, 3);
            True(!outer && !inner, "a nested pair was not both held");
            Eq(g.Held, 2L, "a nested pair counted");
            var callers = g.Rows().Select(r => r.Name + "<-" + r.Caller).ToList();
            True(callers.Contains("Outer<-outer-caller") && callers.Contains("Inner<-inner-caller"), "a nested attempt took the other's caller: " + string.Join(",", callers));
            // contained: a sink that throws is a fault of ours, counted; the decision stands and nothing throws into the game
            sink.Throw = true;
            bool r1 = g.Decide(true, true, Game, false, "N", () => "c", null, 4);
            sink.Throw = false;
            True(!r1, "a sink fault let a held attempt through");
            Eq(g.Faults, 1L, "the sink fault counted");
            True(g.LastFault != null, "the fault is not named");
            // writer fault: a dropped row is counted; outside a run the row is counted outside
            sink.DropAll = true; Try(g, "N"); sink.DropAll = false;
            Eq(g.SinkDropped, 1L, "a row the writer dropped is counted");
            sink.Running = false; Try(g, "N"); sink.Running = true;
            Eq(g.Outside, 1L, "a row outside a run is counted outside");
            // a game change releases the gate and lets the attempt run
            True(Try(g, "N", game: OtherGame), "an attempt in another game was held");
            True(!g.On, "the gate stayed on in another game");
            True(g.LastRelease != null && g.LastRelease.Contains("game changed"), "the release reason: " + g.LastRelease);
        }

        // ------------------------------------------------------------------------------------------------ 9
        static void CampaignRefused()
        {
            var gs = new K.Gates();
            foreach (var g in gs.All)
            {
                var why = g.Arm(Game, true, "RaidEnemy");
                True(why != null && why.Contains("CAMPAIGN"), "the " + g.Kind + " gate armed under CAMPAIGN: " + why);
                True(!g.On, "the " + g.Kind + " gate reads on after a refusal");
                True(Try(g, "RaidEnemy", campaign: true), "a refused " + g.Kind + " gate held an attempt");
            }
            var qwhy = gs.Queue.Hold(Game, true, 100, new List<K.QEntry> { E("RaidEnemy", 200, 200, false) }, new List<string>());
            True(qwhy != null && qwhy.Contains("CAMPAIGN"), "the queue was held under CAMPAIGN: " + qwhy);
            True(!gs.Queue.Holding, "the queue reads held after a refusal");
            // a gate armed on a test save lets go when a canonical save is loaded under it
            foreach (var g in gs.All)
            {
                True(g.Arm(Game, false, "") == null, "the " + g.Kind + " gate did not arm on a test save");
                True(Try(g, "RaidEnemy", campaign: true), "an armed " + g.Kind + " gate held an attempt under CAMPAIGN");
                True(!g.On, "the " + g.Kind + " gate stayed on under CAMPAIGN");
                True(g.LastRelease.Contains("CAMPAIGN"), "the release reason: " + g.LastRelease);
                Eq(g.Held, 0L, "held under CAMPAIGN");
            }
        }

        static int Main()
        {
            Check("the_allow_list_lets_one_named_incident_through_once", AllowOnce);
            Check("a_held_attempt_is_counted_and_recorded_with_its_caller", HeldCountedWithCaller);
            Check("a_gate_that_is_off_changes_nothing_and_records_nothing", OffChangesNothing);
            Check("a_held_queue_entry_comes_back_with_its_fire_tick_moved", FireTickMoved);
            Check("a_held_queue_entry_comes_back_with_its_retry_window_moved", RetryWindowMoved);
            Check("an_entry_past_its_retry_window_when_held_is_reported_never_dropped_in_silence", ExpiredReported);
            Check("the_quest_gate_follows_the_hook_rules", () => HookRules(K.Quest));
            Check("the_mental_gate_follows_the_hook_rules", () => HookRules(K.Mental));
            Check("with_a_canonical_save_loaded_every_gate_is_refused", CampaignRefused);
            Console.WriteLine("U-count " + _n);
            return _bad == 0 ? 0 : 1;
        }
    }
}
