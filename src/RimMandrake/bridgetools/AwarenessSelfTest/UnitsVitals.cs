// Units for the test-state monitor's pure core (JawaBenchVitalsCore.cs, the PRODUCTION file).
// Item: TELEMETRY_COLONY_VITALS_BUILD_SPEC_SAID_SO. Each check is one acceptance rule of GPT §5 that can be proved
// without a game: diff rules, tombstone-independent departure, latch ordering, clock discontinuities (declared and not),
// the advance refusal, the stop rule, modal ages, rollup separation of role and relationship.
using System;
using System.Collections.Generic;
using V = JawaBench.BridgeTools.JawaBenchVitalsCore;

namespace JawaBench.BridgeTools
{
    internal static class VitalsUnits
    {
        static V.PawnObs P(int id, string cls = "humanlike", string rel = "player", bool colonist = true, float health = 1f,
                           bool downed = false, bool hostile = false, string food = "Fed", string mental = null, bool critical = false)
            => new V.PawnObs { Id = id, Map = 0, Label = "p" + id, Def = "Human", Kind = "Colonist", Cls = cls, Rel = rel, Colonist = colonist,
                               Health = health, Downed = downed, Hostile = hostile, Food = food, Mental = mental, Critical = critical };

        static Dictionary<int, V.PawnObs> D(params V.PawnObs[] ps) { var d = new Dictionary<int, V.PawnObs>(); foreach (var p in ps) d[p.Id] = p; return d; }
        static List<V.PawnObs> L(params V.PawnObs[] ps) => new List<V.PawnObs>(ps);
        static bool Has(List<V.Trigger> ts, string kind, string sev) => ts.Exists(t => t.Kind == kind && t.Severity == sev);

        internal static void Run(Action<bool, string, string> c)
        {
            void check(bool ok, string name, string why = "") => c(ok, name, why);

            // --- diff: baseline hostiles reported once, as present at arm
            var b = V.Diff(null, L(P(1), P(2, "mech", "hostile", false, hostile: true)), false, 100);
            check(b.Count == 1 && b[0].Kind == V.KHostileArrival && b[0].Detail.StartsWith("present at arm"), "vitals_baseline_hostile_present", b.Count + "");

            // --- a raid arrives
            var t1 = V.Diff(D(P(1)), L(P(1), P(9, "humanlike", "hostile", false, hostile: true)), false, 200);
            check(Has(t1, V.KHostileArrival, V.SThreat), "vitals_arrival_is_threat");

            // --- downed worker: damage when it is the critical actor, damage for any colonist when no actor is declared
            var t2 = V.Diff(D(P(1, critical: true)), L(P(1, downed: true, health: 0.4f, critical: true)), true, 300);
            check(Has(t2, V.KDowned, V.SDamage) && Has(t2, V.KHurt, V.SDamage), "vitals_critical_downed_is_damage");
            var t2b = V.Diff(D(P(1), P(3, critical: true)), L(P(1, downed: true), P(3, critical: true)), true, 300);
            check(Has(t2b, V.KDowned, V.SThreat) && !Has(t2b, V.KDowned, V.SDamage), "vitals_noncritical_colonist_downed_is_threat_when_actors_declared");
            var t2c = V.Diff(D(P(1)), L(P(1, downed: true)), false, 300);
            check(Has(t2c, V.KDowned, V.SDamage), "vitals_any_colonist_downed_is_damage_without_actors");

            // --- small health wobble is not hurt; >= 0.05 is
            check(V.Diff(D(P(1, health: 1f)), L(P(1, health: 0.97f)), false, 1).Count == 0, "vitals_health_wobble_ignored");

            // --- colonist turns hostile (berserk)
            var t3 = V.Diff(D(P(1)), L(P(1, hostile: true, mental: "Berserk")), false, 400);
            check(Has(t3, V.KColonistHostile, V.SDamage) && Has(t3, V.KMental, V.SDamage), "vitals_colonist_hostile_latched");

            // --- starving
            var t4 = V.Diff(D(P(1, food: "UrgentlyHungry")), L(P(1, food: "Starving")), false, 500);
            check(Has(t4, V.KStarving, V.SDamage), "vitals_starving_colonist_is_damage");

            // --- absence is not death
            var t5 = V.Diff(D(P(1), P(4, critical: true)), L(P(1)), true, 600);
            check(t5.Count == 1 && t5[0].Kind == V.KDeparted && t5[0].Severity == V.SDamage && !Has(t5, V.KDeath, V.SDamage), "vitals_departure_is_not_death");

            // --- latch keeps the FIRST non-info trigger; info and declared ones never become first
            var latch = new V.Latch();
            latch.Add(new V.Trigger { Kind = V.KDeparted, Severity = V.SInfo });
            latch.Add(new V.Trigger { Kind = V.KClock, Severity = V.SClock, Declared = true });
            latch.Add(new V.Trigger { Kind = V.KDowned, Severity = V.SDamage, Tick = 77 });
            latch.Add(new V.Trigger { Kind = V.KDeath, Severity = V.SDamage, Tick = 99 });
            check(latch.First != null && latch.First.Kind == V.KDowned && latch.First.Tick == 77, "vitals_latch_first_disturbance");
            check(latch.Since(2).Count == 2 && latch.Since(0).Count == 4, "vitals_latch_since_seq");

            // --- clock: ordinary ticks are continuous; a reassignment between ticks or frames is a discontinuity
            var clk = new V.ClockLedger();
            check(clk.Frame(1000, 0) == null, "clock_first_read_is_base");
            check(clk.BeforeTick(1000, 0) == null && clk.AfterTick(1000, 1001, 0) == null && clk.BeforeTick(1001, 0) == null, "clock_ordinary_tick_continuous");
            clk.AfterTick(1001, 1002, 0);
            var dj = clk.Frame(601002, 0);
            check(dj != null && dj.Kind == V.KClock && !dj.Declared && clk.Discontinuities == 1, "clock_reassign_while_paused_detected", dj?.Detail);
            check(clk.Frame(601002, 0) == null, "clock_reassign_reported_once");
            clk.Declare(700000, "row declared a time exception");
            var dd = clk.BeforeTick(700000, 0);
            check(dd != null && dd.Declared && clk.Declared == 1, "clock_declared_reassign_marked", dd?.Detail);
            var fe = clk.AfterTick(700000, 702000, 0);
            check(fe != null && fe.Detail.Contains("fastEcology"), "clock_fast_ecology_step_recorded");
            var back = clk.Frame(500, 0);
            check(back != null && back.Detail.Contains("-701500"), "clock_backward_jump_detected", back?.Detail);

            // --- advance policy: the measured failure (10 days on a populated map) is refused before any tick
            check(V.AdvanceRefusal(600000, 0, true, false) != null, "advance_600k_populated_refused");
            check(V.AdvanceRefusal(600000, 0, true, true) == null, "advance_600k_with_time_exception_allowed");
            check(V.AdvanceRefusal(600000, 0, false, false) == null, "advance_600k_empty_map_allowed");
            check(V.AdvanceRefusal(2000000, 0, false, true) != null, "advance_hard_cap_always");
            check(V.AdvanceRefusal(20000, 0, true, false) == null && V.AdvanceRefusal(40000, 0, true, false) != null, "advance_default_budget_30000");
            check(V.AdvanceRefusal(40000, 50000, true, false) == null, "advance_row_budget_respected");
            check(V.AdvanceRefusal(0, 0, true, false) != null, "advance_zero_refused");

            // --- stop rule: info and declared never stop; a raid does; an unlisted kind does not
            var kinds = V.ParseKinds("default", out var bad0);
            var since = new List<V.Trigger>
            {
                new V.Trigger { Kind = V.KDowned, Severity = V.SInfo },
                new V.Trigger { Kind = V.KClock, Severity = V.SClock, Declared = true },
                new V.Trigger { Kind = V.KHostileArrival, Severity = V.SThreat, Tick = 5 },
            };
            var st = V.FirstStop(since, kinds);
            check(bad0 == null && st != null && st.Kind == V.KHostileArrival, "stop_first_real_disturbance");
            var only = V.ParseKinds("death,colony_loss", out var bad1);
            check(bad1 == null && V.FirstStop(since, only) == null, "stop_respects_kind_list");
            V.ParseKinds("death,warp_drive", out var bad2);
            check(bad2 == "warp_drive", "stop_unknown_kind_refused", bad2);

            // --- ids: "Human123" and "123" both resolve to thingIDNumber 123
            var ids = V.ParseIds("Human123, 456", out var badI);
            check(badI == null && ids.Count == 2 && ids[0] == 123 && ids[1] == 456, "ids_parse_label_and_number");
            V.ParseIds("abc", out var badJ);
            check(badJ == "abc", "ids_parse_refuses_no_digits");

            // --- modal ages: new, crossed once, forgotten when closed
            var ma = new V.ModalAges();
            var fresh = new List<int>(); var crossed = new List<int>();
            ma.Observe(new[] { 7 }, 0, 30, fresh, crossed);
            check(fresh.Count == 1 && crossed.Count == 0, "modal_new_window_seen");
            fresh.Clear(); ma.Observe(new[] { 7 }, 31, 30, fresh, crossed);
            check(crossed.Count == 1 && crossed[0] == 7, "modal_stuck_crossed");
            crossed.Clear(); ma.Observe(new[] { 7 }, 60, 30, fresh, crossed);
            check(crossed.Count == 0 && Math.Abs(ma.MaxAge(60) - 60) < 1e-9, "modal_stuck_latched_once");
            ma.Observe(new int[0], 61, 30, fresh, crossed);
            check(ma.MaxAge(61) == 0, "modal_closed_forgotten");

            // --- rollup: role and relationship stay separate; mood n/a is not zero
            var r = V.Rollup.Of(L(P(1, health: 0.8f), P(2, "animal", "hostile", false, hostile: true), P(3, "mech", "player", false)));
            check(r.Groups.ContainsKey("animal|hostile") && r.Groups.ContainsKey("mech|player") && r.ColonistsAlive == 1 && r.Hostiles == 1,
                  "rollup_role_and_relationship_separate", r.Key());
            check(r.Fields().Contains("\"minColonistMoodMargin\":null") && r.Fields().Contains("\"minColonistHealth\":0.8"), "rollup_na_is_null_not_zero", r.Fields());
            check(V.Rollup.Of(L()).Fields().Contains("\"colonistsAlive\":0"), "rollup_empty_map_counts_zero_alive");

            // --- delta rows: only real changes
            check(!P(1, health: 0.9f).Changed(P(1, health: 0.91f)) && P(1, health: 0.9f).Changed(P(1, health: 0.95f)), "pawn_delta_threshold");
        }
    }
}
