// Unit group for JawaBenchAwarenessCore.cs (the PRODUCTION file). Prints "U name ok|FAIL why" per check and
// "U-count n"; exit 1 when any check fails. Driven by src/RimMandrake/Utils/selftest_map_awareness_core.py.
using System;
using System.Collections.Generic;
using System.Threading;
using A = JawaBench.BridgeTools.JawaBenchAwarenessCore;

namespace JawaBench.BridgeTools
{
    internal static class Program
    {
        static int _n, _bad;

        static void Check(bool ok, string name, string why = "")
        {
            _n++;
            if (!ok) _bad++;
            Console.WriteLine("U " + name.Replace(' ', '_') + " " + (ok ? "ok" : "FAIL " + why));
        }

        static int Main()
        {
            var rec = new A.Recorder();
            var game1 = new object();
            int ep = rec.EpochFor(game1);

            // --- 1. the chain keeps our involvement: bridge > incident, root = bridge
            A.Scope.ResetThreadForTest();
            var tb = A.Scope.Push("bridge", "jawa/fire_incident", ep);
            var ti = A.Scope.Push("incident", "RaidEnemy", ep);
            var cur = A.Scope.Current(ep);
            Check(cur != null && cur.Chain.StartsWith("bridge:jawa/fire_incident#") && cur.Chain.Contains(" > incident:RaidEnemy#"),
                  "chain_outermost_first", cur?.Chain);
            Check(cur.Root.Kind == "bridge" && A.Involvement(cur.Root.Kind) == "confirmedIndirectAction",
                  "bridge_rooted_chain_is_our_indirect_action", cur.Root.Kind);
            Check(cur.HasKind("incident") && cur.HasKind("bridge"), "chain_has_both_kinds");
            A.Scope.Pop(ti);
            Check(ReferenceEquals(A.Scope.Current(ep), tb.Mine), "pop_restores_parent");
            A.Scope.Pop(ti);   // idempotent
            Check(ReferenceEquals(A.Scope.Current(ep), tb.Mine), "pop_is_idempotent");
            A.Scope.Pop(tb);
            Check(A.Scope.Current(ep) == null, "pop_to_empty");

            // --- 2. skipped prefix (invalid token) and an inner scope left open
            A.Scope.Pop(new A.Token());
            Check(A.Scope.Current(ep) == null, "invalid_token_pop_changes_nothing");
            var outer = A.Scope.Push("mapgen", "Settlement", ep);
            A.Scope.Push("wild-spawner", "SpawnRandomWildAnimalAt", ep);       // never popped (an exception path)
            long unb = A.Scope.Unbalanced;
            A.Scope.Pop(outer);
            Check(A.Scope.Current(ep) == null && A.Scope.Unbalanced == unb + 1, "outer_pop_closes_unbalanced_inner");

            // --- 3. threads: a thread-static context does NOT cross; an explicit token does
            var capt = A.Scope.Push("bridge", "jawa/incident_schedule", ep);
            var captured = A.Scope.Current(ep);
            A.Ctx seenOnWorker = null, adoptedOnWorker = null, afterPop = new A.Ctx("x", "x", -1, null, ep);
            var th = new Thread(() =>
            {
                seenOnWorker = A.Scope.Current(ep);
                var t = A.Scope.Adopt(captured, ep);
                var inner = A.Scope.Push("incident", "RaidEnemy", ep);
                adoptedOnWorker = A.Scope.Current(ep);
                A.Scope.Pop(inner);
                A.Scope.Pop(t);
                afterPop = A.Scope.Current(ep);
            });
            th.Start(); th.Join();
            A.Scope.Pop(capt);
            Check(seenOnWorker == null, "threadstatic_context_does_not_cross_threads");
            Check(adoptedOnWorker != null && adoptedOnWorker.Root.Label == "jawa/incident_schedule" && adoptedOnWorker.Kind == "incident",
                  "explicit_token_carries_the_chain_across_threads", adoptedOnWorker?.Chain);
            Check(afterPop == null, "worker_restored_after_adopt");
            var stale = A.Scope.Adopt(new A.Ctx("bridge", "old", 1, null, ep - 1), ep);
            Check(!stale.Valid && A.Scope.Current(ep) == null, "token_from_another_epoch_is_refused");

            // --- 4. depth bound
            var toks = new List<A.Token>();
            long tr0 = A.Scope.Truncated;
            for (int i = 0; i < A.MaxDepth + 3; i++) toks.Add(A.Scope.Push("bridge", "deep" + i, ep));
            Check(A.Scope.Current(ep).Depth == A.MaxDepth && A.Scope.Truncated == tr0 + 3, "depth_is_bounded_and_counted",
                  A.Scope.Current(ep).Depth + " / " + (A.Scope.Truncated - tr0));
            for (int i = toks.Count - 1; i >= 0; i--) A.Scope.Pop(toks[i]);
            Check(A.Scope.Current(ep) == null, "bounded_pushes_unwind_cleanly");

            // --- 5. epochs: a new game forgets; late rows from the old game are dropped and counted
            rec.AddGeneration(new A.GenObs { Epoch = ep, PawnId = 11, Kind = "Megaspider", Chain = "mapgen:x#1", RootKind = "mapgen", Reuse = "new" });
            int ep2 = rec.EpochFor(new object());
            Check(ep2 == ep + 1 && rec.Tags.Count == 0, "new_game_opens_a_new_epoch_and_forgets");
            bool late = rec.AddGeneration(new A.GenObs { Epoch = ep, PawnId = 12 });
            Check(!late && rec.LateRowsDropped == 1, "late_row_from_old_game_dropped_and_counted");
            Check(rec.AddSpawn(ep, 1, 0, 12, "k", "d", null, 0, 0, null, true) == null && rec.LateRowsDropped == 2,
                  "late_spawn_from_old_game_dropped");
            ep = ep2;

            // --- 6. reuse never overwrites the creation record
            rec.AddGeneration(new A.GenObs { Epoch = ep, PawnId = 21, Kind = "Colonist", Chain = "bridge:jawa/spawn_pawn#9", RootKind = "bridge", Reuse = "new" });
            rec.AddGeneration(new A.GenObs { Epoch = ep, PawnId = 21, Kind = "Colonist", Chain = "incident:WandererJoin#10", RootKind = "incident", Reuse = "reused" });
            rec.Tags.TryGet(21, out var g21);
            Check(g21 != null && g21.RootKind == "bridge" && g21.Reobserved == 1, "reuse_is_a_reobservation_not_an_overwrite",
                  g21 == null ? "null" : g21.RootKind + "/" + g21.Reobserved);

            // --- 7. classification + statements
            var s1 = rec.AddSpawn(ep, 100, 0, 21, "Colonist", "Human", "PlayerColony", 5, 5, "bridge:jawa/spawn_pawn#9", true);
            Check(s1.Classification == "firstObservedSpawn" && s1.Gen == g21, "first_spawn_links_its_generation");
            var s2 = rec.AddSpawn(ep, 200, 0, 21, "Colonist", "Human", "PlayerColony", 6, 6, null, true);
            Check(s2.Classification == "observedRespawn", "same_map_again_is_a_respawn", s2.Classification);
            var s3 = rec.AddSpawn(ep, 300, 7, 21, "Colonist", "Human", "PlayerColony", 6, 6, null, true);
            Check(s3.Classification == "mapTransfer", "other_map_is_a_transfer", s3.Classification);
            rec.NoteLoadRespawn(ep, 31, 0);
            var s4 = rec.AddSpawn(ep, 400, 0, 31, "Muffalo", "Muffalo", null, 1, 1, null, true);
            Check(s4.Classification == "observedRespawn" && s4.Gen == null, "after_load_respawn_a_spawn_is_not_first");
            var s5 = rec.AddSpawn(ep, 500, 0, 41, "Warg", "Warg", null, 1, 1, null, true);
            string st5 = A.Statement(s5);
            Check(st5.StartsWith("origin unknown") && !A.IsForbidden(st5), "untagged_spawn_reads_origin_unknown", st5);
            string st1 = A.Statement(s1);
            Check(st1.Contains("during bridge:jawa/spawn_pawn") && !A.IsForbidden(st1), "tagged_spawn_names_the_chain_without_upgrading", st1);
            Check(!A.IsForbidden(A.Statement(null)) && A.Statement(null).Contains("origin unknown"), "baseline_pawn_statement");
            foreach (var bad in new[] { "Caused by RaidEnemy", "a mapgen pawn", "no arrivals occurred", "incident fired" })
                Check(A.IsForbidden(bad), "lint_catches:" + bad);

            // --- 8. bounded seen-set: after an eviction "first" is no longer provable
            var seen = new A.BoundedMap<int>(2);
            A.Classify(seen, 1, 0); A.Classify(seen, 2, 0);
            string c3 = A.Classify(seen, 3, 0);
            Check(seen.Evicted == 1 && c3 == "unknown", "eviction_makes_first_unprovable", c3 + " ev " + seen.Evicted);
            var ring = new A.Ring<string>(3);
            for (int i = 0; i < 5; i++) ring.Add("r" + i);
            Check(ring.Overwritten == 2 && ring.Snapshot().Count == 3 && ring.Snapshot()[0] == "r2", "ring_counts_overwrites");

            // --- 9. incident statements: "called", never "fired"; worker unknown unless established
            var ir = new A.IncidentRec { Def = "RaidEnemy", OuterBodyRan = "true", Returned = "true" };
            string its = A.IncidentStatement(ir);
            Check(its.Contains("was called") && its.Contains("worker entered: unknown") && !A.IsForbidden(its), "incident_statement_honest", its);
            ir.Exception = "NullReferenceException: x"; ir.Returned = "exception";
            Check(A.IncidentStatement(ir).Contains("exception observed"), "incident_exception_observed");

            // --- 10. switches
            var sw = A.Switches.Parse("{\"aware.disk-rows\": false, \"aware.bogus\": true, \"aware.origin-spawn\": 3}");
            Check(!sw.On(A.MDisk) && sw.On(A.MSpawn) && sw.On(A.MIncident) && sw.Note.Contains("aware.bogus: unknown metric id")
                  && sw.Note.Contains("aware.origin-spawn: not a bool"), "switches_parse_and_note", sw.Note);
            var sw2 = A.Switches.Parse("{\"aware.disk-rows\": fal");
            Check(sw2.On(A.MDisk) && sw2.Note.StartsWith("invalid settings"), "invalid_settings_keep_defaults", sw2.Note);
            Check(A.Switches.Parse(null).On(A.MGeneration), "no_file_all_on");
            Check(!sw.Set("aware.nope", true), "unknown_switch_refused");

            // --- 11. disk arming TTL
            var arm = new A.Arm();
            var t0 = new DateTime(2026, 10, 10, 12, 0, 0, DateTimeKind.Utc);
            Check(!arm.Armed(t0), "disarmed_by_default");
            arm.Set(t0, 0, "test");
            Check(arm.Armed(t0.AddMinutes(29)) && !arm.Armed(t0.AddMinutes(31)), "default_ttl_30min");
            arm.Set(t0, 10000, "test");
            Check(arm.Armed(t0.AddMinutes(239)) && !arm.Armed(t0.AddMinutes(241)), "ttl_capped_240min");

            // --- 12. thing_explain rules
            Check(A.SelectorProblem(null, null, null, false) != null, "no_selector_refused");
            Check(A.SelectorProblem("Thing_1", "3,4", null, false) != null, "two_selectors_refused");
            Check(A.SelectorProblem("Thing_1", null, null, false) == null && A.SelectorProblem(null, null, null, true) == null, "one_selector_ok");
            var pv = A.ProviderVerdict(new[] { "ludeon.rimworld", "mod.a", "mod.b" }, null);
            Check(pv[0] == "mod.b" && pv[1] == "CANDIDATE", "candidate_is_last_in_load_order", string.Join("|", pv));
            var po = A.ProviderVerdict(new[] { "mod.a", "mod.b" }, "mod.a");
            Check(po[0] == "mod.a" && po[1] == "OBSERVED" && po[2].Contains("differs"), "observed_beats_candidate_and_says_so", string.Join("|", po));
            Check(A.ProviderVerdict(new string[0], null)[1] == "UNKNOWN", "no_pack_is_unknown");

            // --- 13. meter
            var m = new A.Meter();
            m.Add(100); m.Add(300);
            Check(m.Calls == 2 && Math.Abs(m.MeanUs(1e6) - 200) < 1e-9 && Math.Abs(m.MaxUs(1e6) - 300) < 1e-9, "meter_mean_and_max");

            // --- 14. companion safety core (profile, census, epochs, quiet block, handshake, install option)
            SafetyUnits.Run((ok, name, why) => Check(ok, name, why ?? ""));

            // --- 15. test-state monitor core (TELEMETRY_COLONY_VITALS_BUILD_SPEC_SAID_SO)
            VitalsUnits.Run((ok, name, why) => Check(ok, name, why ?? ""));

            Console.WriteLine("U-count " + _n);
            return _bad == 0 ? 0 : 1;
        }
    }
}
