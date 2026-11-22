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

        // A wall-second timeline of back-to-back safe_advance calls (runS each, gapS between), driven by the SHIPPED lease
        // decisions in the order JawaBenchVitals wires them: the advance start (V.AdvanceArmAction; "arm" and "renew" set the
        // TTL end to V.AutoArmUntil), the frame (V.TtlExpired, then the stepper ends a running advance on the disarm), the
        // advance end (an auto-armed monitor renews). explicitTtlMin > 0: a governor row armed it at t=0 with that TTL.
        static (int midRunDisarms, int firstAt, int idleExpiries, int advances) SimLease(int runS, int gapS, int horizonS, double explicitTtlMin)
        {
            bool armed = false, auto = false; double until = 0;
            if (explicitTtlMin > 0) { armed = true; auto = false; until = explicitTtlMin * 60.0; }
            int mid = 0, first = -1, idleExp = 0, advances = 0, t = 0;
            while (t < horizonS)
            {
                string act = V.AdvanceArmAction(armed, auto);
                if (act == "arm") { armed = true; auto = true; until = V.AutoArmUntil(t); }
                else if (act == "renew") until = V.AutoArmUntil(t);
                advances++;
                int end = t + runS; bool aborted = false;
                for (; t < end; t++)
                    if (armed && V.TtlExpired(t, until, auto, true)) { armed = false; auto = false; mid++; if (first < 0) first = t; aborted = true; break; }
                if (!aborted && V.AdvanceEndRenews(armed, auto)) until = V.AutoArmUntil(t);
                int gapEnd = t + gapS;
                for (; t < gapEnd; t++)
                    if (armed && V.TtlExpired(t, until, auto, false)) { armed = false; auto = false; idleExp++; }
            }
            return (mid, first, idleExp, advances);
        }

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

            // --- RIMMANDRAKE_SHIELD_PYRE_WALK_FROM_FULL_LIST_EVENTS: in vanilla 1.6 only Hediff_Injury and Hediff_MissingPart lower
            // SummaryHealthPercent (Verse/SummaryHealthHandler.cs); a drop with no new wound is another mod's hediff class (his
            // 315-mod list, 2026-11-21: 1 -> 0.87 -> 0.73 with SEX_Penis/SEX_Reproduction age 0) and is info, never a stop.
            var nw0 = P(1, health: 1f); nw0.Wounds = 0f; nw0.Newest = "SEX_Penis/SEX_Reproduction age 0";
            var nw1 = P(1, health: 0.87f); nw1.Wounds = 0f; nw1.Newest = "SEX_Penis/SEX_Reproduction age 0";
            var tw = V.Diff(D(nw0), L(nw1), false, 700);
            check(Has(tw, V.KHurt, V.SInfo) && !Has(tw, V.KHurt, V.SDamage) && tw.Exists(x => x.Detail.Contains("no new wound")),
                  "vitals_health_drop_without_new_wound_is_info", tw.Count > 0 ? tw[0].Severity + " " + tw[0].Detail : "none");
            var wd0 = P(1, health: 1f); wd0.Wounds = 0f; wd0.Newest = "SEX_Penis/SEX_Reproduction age 0";
            var wd1 = P(1, health: 0.87f); wd1.Wounds = 4f; wd1.Newest = "SEX_Penis/SEX_Reproduction age 0"; wd1.NewestWound = "Burn/Torso age 30";
            var tb = V.Diff(D(wd0), L(wd1), false, 700);
            check(Has(tb, V.KHurt, V.SDamage) && tb.Exists(x => x.Detail.Contains("newest hediff Burn/Torso")),
                  "vitals_health_drop_with_new_wound_is_damage_naming_the_wound", tb.Count > 0 ? tb[0].Detail : "none");
            var mp0 = P(1, health: 1f); mp0.Wounds = 0f;
            var mp1 = P(1, health: 0.9f); mp1.Wounds = V.WoundScore(0f, 1);
            check(Has(V.Diff(D(mp0), L(mp1), false, 700), V.KHurt, V.SDamage), "vitals_new_missing_part_is_damage");
            var un0 = P(1, health: 1f); var un1 = P(1, health: 0.87f);      // Wounds unread (NaN): could not look, the stop stands
            check(Has(V.Diff(D(un0), L(un1), false, 700), V.KHurt, V.SDamage), "vitals_unread_wounds_keep_the_stop");
            var hl0 = P(1, health: 0.6f); hl0.Wounds = 9f;                   // a wound healing while health falls elsewhere
            var hl1 = P(1, health: 0.5f); hl1.Wounds = 8.5f;
            check(Has(V.Diff(D(hl0), L(hl1), false, 700), V.KHurt, V.SInfo), "vitals_healing_wound_with_other_drop_is_info");
            // --- a downing names what downed the pawn (cause 1 of the same run was unread: "downed (health 1)")
            var dn0 = P(1); var dn1 = P(1, downed: true); dn1.Ailments = "Heatstroke 0.82, Malnutrition 0.1";
            var td = V.Diff(D(dn0), L(dn1), false, 800);
            check(td.Exists(x => x.Kind == V.KDowned && x.Detail.StartsWith("downed (health 1") && x.Detail.Contains("Heatstroke 0.82")),
                  "vitals_downed_names_its_ailments", td.Count > 0 ? td[0].Detail : "none");
            var al = V.AilmentList(new List<V.Ail> { new V.Ail { Def = "A", Sev = 0.1f }, new V.Ail { Def = "B", Part = "Leg", Sev = 0.9f },
                                                     new V.Ail { Def = "C", Sev = 0.5f } }, 2);
            check(al == "B/Leg 0.9, C 0.5 (+1 more)", "vitals_ailment_list_worst_first_bounded", al);
            check(V.AilmentList(new List<V.Ail>(), 6) == null, "vitals_ailment_list_empty_is_null");

            // --- colonist turns hostile (berserk)
            var t3 = V.Diff(D(P(1)), L(P(1, hostile: true, mental: "Berserk")), false, 400);
            check(Has(t3, V.KColonistHostile, V.SDamage) && Has(t3, V.KMental, V.SDamage), "vitals_colonist_hostile_latched");

            // --- starving
            var t4 = V.Diff(D(P(1, food: "UrgentlyHungry")), L(P(1, food: "Starving")), false, 500);
            check(Has(t4, V.KStarving, V.SDamage), "vitals_starving_colonist_is_damage");

            // --- absence is not death
            var t5 = V.Diff(D(P(1), P(4, critical: true)), L(P(1)), true, 600);
            check(t5.Count == 1 && t5[0].Kind == V.KDeparted && t5[0].Severity == V.SDamage && !Has(t5, V.KDeath, V.SDamage), "vitals_departure_is_not_death");

            // --- a death's severity by where the pawn was (RIMMANDRAKE_IGNORE_OFFMAP_COLONIST_DEATH_HEART_ATTACK_TWICE: Randall, a
            // world-pawn colonist of the abandoned quicktest colony, map -1, died of a heart attack and stopped two Pyrelands rows).
            // The range: {colonist, not} x {spawned, caravan/transporter (Map -1, not off-map), world pawn (off-map)} x
            // {actors declared, none} x {critical, not}. Left out: Verse placement itself (KillPlacementOffMap reads Verse; live).
            V.PawnObs Dead(int id, bool colonist = true, bool offMap = false, bool critical = false, int map = 0)
            { var d = P(id, colonist: colonist, critical: critical); d.OffMap = offMap; d.Map = map; d.Health = float.NaN; return d; }
            var worldPawn = Dead(760, offMap: true, map: -1);
            check(V.DeathSeverity(worldPawn, false) == V.SInfo, "vitals_offmap_colonist_death_is_info", V.DeathSeverity(worldPawn, false));
            check(V.DeathSeverity(worldPawn, true) == V.SInfo, "vitals_offmap_colonist_death_is_info_with_actors", V.DeathSeverity(worldPawn, true));
            check(V.DeathSeverity(Dead(1), false) == V.SDamage, "vitals_spawned_colonist_death_is_damage", V.DeathSeverity(Dead(1), false));
            check(V.DeathSeverity(Dead(1), true) == V.SThreat, "vitals_spawned_noncritical_colonist_death_is_threat_with_actors");
            check(V.DeathSeverity(Dead(2, map: -1), false) == V.SDamage, "vitals_caravan_colonist_death_is_damage");
            check(V.DeathSeverity(Dead(3, offMap: true, map: -1, critical: true), true) == V.SDamage, "vitals_offmap_critical_actor_death_is_damage");
            check(V.DeathSeverity(Dead(4, colonist: false), false) == V.SInfo && V.DeathSeverity(Dead(5, colonist: false, offMap: true), false) == V.SInfo,
                  "vitals_noncolonist_death_is_info");
            var stopKindsDefault = V.ParseKinds("default", out var _bd);
            var worldDeath = V.T(V.KDeath, V.DeathSeverity(worldPawn, false), 900, worldPawn, "died: HeartAttack");
            var siteDeath = V.T(V.KDeath, V.DeathSeverity(Dead(1), false), 901, Dead(1), "died: Burn");
            check(V.FirstStop(new List<V.Trigger> { worldDeath }, stopKindsDefault) == null, "vitals_offmap_colonist_death_stops_no_advance");
            check(V.FirstStop(new List<V.Trigger> { worldDeath, siteDeath }, stopKindsDefault) == siteDeath, "vitals_site_colonist_death_still_stops");
            check(!V.Matters(worldPawn, false) && V.Matters(Dead(1), false), "vitals_offmap_colonist_does_not_matter");

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

            // --- stepper frame gate (night review 2026-10-13): a cancel, a wall timeout or a lost monitor ENDS a run even when
            // no game is ready; before the fix a disarm/TTL mid-advance left the run "running" forever and every later
            // safe_advance (cancel included) was refused.
            check(V.AdvanceFrameStop(false, 1, 60, false) != null && V.AdvanceFrameStop(false, 1, 60, false).StartsWith("aborted"), "advance_frame_disarmed_aborts");
            check(V.AdvanceFrameStop(true, 1, 60, false) == "cancelled", "advance_frame_cancel_wins");
            check(V.AdvanceFrameStop(false, 61, 60, true) != null && V.AdvanceFrameStop(false, 61, 60, true).Contains("wall"), "advance_frame_wall_timeout_aborts");
            check(V.AdvanceFrameStop(false, 1, 60, true) == null, "advance_frame_armed_in_time_goes_on");

            // --- the auto-arm lease (RIMMANDRAKE_RENEW_SAFE_ADVANCE_AUTO_ARM_HOURLY): safe_advance's own arm lasts while
            // safe_advance uses it. Before the fix the 60 min auto-arm was never renewed, so 60 wall minutes after the first
            // advance the TTL disarmed the monitor mid-advance (Pyrelands visit 2, 2026-11-21: embergrass_regrow stopped at
            // 660/2000 ticks). An explicit arm keeps its own TTL. Each timeline below runs the SHIPPED decisions
            // (V.AdvanceArmAction at start, V.TtlExpired every wall second, V.AdvanceEndRenews at end) and prints its worst TTL margin.
            check(V.AdvanceArmAction(false, false) == "arm" && V.AdvanceArmAction(false, true) == "arm", "autoarm_unarmed_arms");
            check(V.AdvanceArmAction(true, true) == "renew", "autoarm_armed_by_safe_advance_renews");
            check(V.AdvanceArmAction(true, false) == "keep", "autoarm_explicit_arm_keeps_its_ttl");
            check(V.AdvanceEndRenews(true, true) && !V.AdvanceEndRenews(true, false) && !V.AdvanceEndRenews(false, true), "autoarm_end_renews_only_its_own_arm");
            check(V.TtlExpired(10, 5, false, false) && V.TtlExpired(10, 5, false, true) && V.TtlExpired(10, 5, true, false), "ttl_expires_unless_auto_and_running");
            check(!V.TtlExpired(10, 5, true, true) && !V.TtlExpired(4, 5, false, false), "ttl_auto_armed_running_advance_never_expires");
            // Range: chains of advances (wall 1 s .. 100 min each, gaps 0 .. 59 min) over 4 h, auto-armed or explicitly armed
            // (TTL 30 / 240 min). Left out: a cancel or abort mid-run (Finish runs the same end path) and game reloads.
            int cases = 0, midRunDisarms = 0, advances = 0; string autoFail = null;
            foreach (int runS in new[] { 1, 60, 600, 1500, 3599, 3600, 3601, 6000 })
                foreach (int gapS in new[] { 0, 30, 600, 3540, 3599 })
                {
                    cases++;
                    var sim = SimLease(runS, gapS, 4 * 3600, 0);
                    midRunDisarms += sim.midRunDisarms; advances += sim.advances;
                    if (sim.midRunDisarms > 0 && autoFail == null) autoFail = "run " + runS + " s gap " + gapS + " s: first disarm mid-advance at t=" + sim.firstAt + " s";
                }
            check(autoFail == null, "autoarm_chain_never_disarms_mid_advance",
                  (autoFail ?? "ok") + "; worst " + midRunDisarms + " mid-advance disarms (limit 0) over " + cases + " timelines, " + advances + " advances");
            var idle = SimLease(60, 3601 + 60, 3 * 3600, 0);
            check(idle.midRunDisarms == 0 && idle.idleExpiries > 0, "autoarm_lease_still_ends_after_an_idle_hour", "idle expiries " + idle.idleExpiries);
            var exp30 = SimLease(700, 0, 3 * 3600, 30);
            check(exp30.midRunDisarms > 0 && exp30.firstAt == 1800, "explicit_arm_ttl_still_binds_mid_advance", "first disarm t=" + exp30.firstAt + " s (want 1800)");
            var exp240 = SimLease(600, 30, 3 * 3600, 240);
            check(exp240.midRunDisarms == 0, "explicit_long_arm_holds_a_three_hour_chain", exp240.midRunDisarms + " mid-advance disarms");

            // --- per-frame tick cap (TICKBURST_PROVE_MANY_TICKS_ONE_FRAME): 0 = unlimited, a cap cuts the chunk, never overshoots
            check(V.NextChunk(60, 1000, 0, 0) == 60 && V.NextChunk(60, 1000, 0, 600) == 60, "nextchunk_cap0_unlimited");
            check(V.NextChunk(60, 25, 0, 0) == 25, "nextchunk_remaining_cuts");
            check(V.NextChunk(60, 1000, 1, 0) == 1 && V.NextChunk(60, 1000, 1, 1) == 0, "nextchunk_cap1_one_per_frame");
            check(V.NextChunk(60, 1000, 61, 60) == 1 && V.NextChunk(60, 1000, 61, 61) == 0, "nextchunk_cap61_cuts_second_chunk");
            check(V.NextChunk(60, 1000, 30, 0) == 30, "nextchunk_cap_below_chunk");
            check(V.NextChunk(0, 1000, 0, 0) == 0 && V.NextChunk(60, 0, 0, 0) == 0, "nextchunk_degenerate_zero");
            {   // sweep: for every (chunk, cap, remaining) a simulated frame loop steps exactly min(remaining, cap or inf) per frame
                bool okSweep = true; string bad = "";
                foreach (int ch in new[] { 1, 7, 30, 60 })
                    foreach (int cap in new[] { 0, 1, 30, 59, 60, 61, 125 })
                        foreach (long rem0 in new long[] { 1, 59, 60, 61, 600, 1001 })
                        {
                            long rem = rem0; int frames = 0;
                            while (rem > 0 && frames < 100000)
                            {
                                int done = 0, n, chunks = 0;
                                while ((n = V.NextChunk(ch, rem, cap, done)) > 0 && chunks < 3) { done += n; rem -= n; chunks++; }
                                frames++;
                                if (cap > 0 && done > cap) { okSweep = false; bad = ch + "/" + cap + "/" + rem0; }
                                if (done == 0) { okSweep = false; bad = "stall " + ch + "/" + cap + "/" + rem0; break; }
                            }
                            if (rem != 0) { okSweep = false; bad = "left " + ch + "/" + cap + "/" + rem0; }
                        }
                check(okSweep, "nextchunk_sweep_exact_total_never_over_cap", bad);
            }
            check(V.Percentile(new List<double> { 5, 1, 3, 2, 4 }, 50) == 3 && V.Percentile(new List<double> { 5, 1, 3, 2, 4 }, 100) == 5,
                  "percentile_nearest_rank");
            check(double.IsNaN(V.Percentile(new List<double>(), 99)), "percentile_empty_nan");
            {
                var h = V.FrameTickHistogram(new List<int> { 60, 61, 60, 1 });
                check(h.Count == 3 && h[60] == 2 && h[61] == 1 && h[1] == 1, "frame_tick_histogram_exact");
            }

            // --- game-identity gate (SAFE_ADVANCE_MENU_DIAGNOSE_LUCKY_NULLREF): menu / load / new game / lost map end the run
            // with a NAMED reason before anything can NRE; the same game on its start map goes on.
            check(V.AdvanceGameGate(true, false, false, false, 0)?.StartsWith("game_changed") == true, "advance_gate_menu_is_game_changed");
            check(V.AdvanceGameGate(false, true, false, false, 0)?.StartsWith("game_changed") == true, "advance_gate_other_game_is_game_changed");
            check(V.AdvanceGameGate(false, false, true, true, 0)?.StartsWith("game_changed") == true, "advance_gate_not_playing_is_game_changed");
            check(V.AdvanceGameGate(false, true, true, false, 7)?.StartsWith("map_gone") == true, "advance_gate_lost_map_is_map_gone");
            check(V.AdvanceGameGate(false, true, true, true, 7) == null, "advance_gate_same_game_and_map_goes_on");

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
