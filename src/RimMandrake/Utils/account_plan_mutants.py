#!/usr/bin/env python3
"""Planted faults for selftest_account_plan.py (page design/specs/2026-11-24-account-plan-one-file/boundary.md): each
is one realistic fault in a COPY of the code, and the selftest must print a FAIL line that names the promise it breaks.
A control (no fault) must pass. A plant whose anchor is gone is an error by name, never a catch. Exit 0: every fault
caught. One fault may be listed under several promises: each of them must name it.

    python3 src/RimMandrake/Utils/account_plan_mutants.py [promise ...]
"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent
sys.path.insert(0, str(HERE))
import time_budget  # noqa: E402

P, RP = "Utils/account_plan.py", "Utils/account_plan_replay.py"
MARKER = ('        if not r["ok"]:\n            return False, False, "its level reads %s" % r["state"]',
          '        if any(m.get("from") == a and m.get("under") for m in markers.values()):\n'
          '            return False, False, "a marker says that it was left at its line"\n'
          '        if not r["ok"]:\n            return False, False, "its level reads %s" % r["state"]')
PULL = ('    until = ended(rl, env, live)',
        '    until = bool(can) and bool(order) and order[0] != live      # the old rule: the first in the order pulls')
UNDO = ('commit(lambda _old: copy.deepcopy(h["before"]),', 'commit(lambda _old: copy.deepcopy(h["after"]),')
# (promise its FAIL line must name, file, old, new)
PLANTS = [
    ("live_account_stays_until_its_own_line", P, *PULL),
    # the fault of 2026-11-24 4:56 PM PST (RIMMANDRAKE_BURN_TO_LINE_WARNING_SWITCHED_AT_THREE): finished at the warning line
    ("the_account_burns_to_its_line", P, '    under = rl is None or (pl is not None and pl <= line)',
     '    under = rl is None or (pl is not None and warn is not None and pl <= warn)'),
    ("order_only_answers_which_account_is_next", P, 'nxt = best_of(ch, order) if ch else (can[0] if can else None)',
     'nxt = best_of(ch, order) if ch else (sorted(can)[0] if can else None)'),
    ("no_start_is_refused_for_a_preference", P, '    eta = None if not rate else (pl - warn) / rate\n',
     '    if pl <= warn + 2:\n        return {**base, "do": "soft", "why": "inside the soft zone: publish and finish"}\n'
     '    eta = None if not rate else (pl - warn) / rate\n'),
    ("a_rescue_switch_needs_points_worth_a_switch", P, '    if gain < N["switch_cost_pts"]:     # leaving', '    if gain <= 1e-9:     # leaving'),
    ("a_rescue_switch_waits_for_no_live_run", P, '    idle = runs is not None and not runs\n    delayed', '    idle = not runs\n    delayed'),
    ("an_unknown_burn_never_causes_a_switch", P, '    if rate is None or not live:\n        return None',
     '    if not live:\n        return None\n    rate = 4.0 if rate is None else rate'),
    ("a_hand_switch_is_respected", P, '    if pin or f.get("hand") or commanded(plan, f):', '    if pin or commanded(plan, f):'),
    ("a_hand_switch_is_respected", P, '    if pin or f.get("hand") or commanded(plan, f):', '    if pin or f.get("hand"):'),
    ("the_reason_is_one_checkable_line", P, '    if alt is not None and stay:\n        gain = stay["cost"] - others[alt]["cost"]',
     '    if False:\n        gain = stay["cost"] - others[alt]["cost"]'),
    ("the_forecast_is_the_pick", P, 'nxt = best_of(ch, order) if ch else (can[0] if can else None)', 'nxt = can[0] if can else None'),
    ("no_marker_decides", P, *MARKER),
    ("an_account_left_at_its_line_is_no_target", P,
     '    return max(AE.warning_line(rl["line"], None, N["account_end"]), rl["line"] + (rl["warn"] or 0)) + N["entry_margin_pct"]', '    return rl["line"]'),
    ("an_account_left_at_its_line_is_no_target", P, 'rl["line"] + (rl["warn"] or 0)) + N[', 'rl["line"]) + N['),
    ("an_account_left_at_its_line_is_no_target", P, 'if not ended(rules[a], env, a)] or (can if under else [])', ']'),
    ("a_refilled_account_is_a_target_at_once", P, *MARKER),
    ("unknown_never_gives_permission", P, '        return None if v is None else not v', '        return not v'),
    ("the_last_account_waits_at_its_wait_floor", P,
     '        line = rl["line"] if can else max(rl["line"], N["last_account_floor_pct"])\n        warn = max(',
     '        line = rl["line"]\n        warn = max('),
    ("a_level_not_confirmed_near_the_line_refuses_starts", P,
     '    if near_old and lr["age_min"] is not None and lr["age_min"] > fr["max_age_min"]:', '    if False:'),
    ("a_rescue_drain_in_flight_goes_on", P, 'f["draining"] or bool(last.get("draining"))', 'f["draining"]'),
    ("a_request_is_done_by_the_switchers_log", P, 'for q in open_requests(plan, f))\n', 'for q in active(plan["requests"], f["now"]))\n'),
    ("tick_drives_the_old_actuator", P, '        if near_end and not polled:', '        if False:'),
    ("tick_drives_the_old_actuator", P, '            can = [a for a in can if take(a)[1]] or can\n', '            pass\n'),
    ("tick_drives_the_old_actuator", P, 'if is_under and not (rl is None and pl is not None and pl > line):', 'if is_under:'),
    ("a_rescue_drain_in_flight_goes_on", P, '(0.0 if f.get("draining") else delayed):', 'delayed:'),
    ("an_account_outside_the_plan_is_left_alone", P, '    if live not in accts:       # somebody', '    if False:       # somebody'),
    ("a_step_that_is_not_alive_says_so", P, '" (NOT ALIVE NOW: %s)" % dead if dead else ""', '""'),
    ("one_file_binds_at_the_next_read", P,
     '    return max(AE.warning_line(rl["line"], None, N["account_end"]), rl["line"] + (rl["warn"] or 0)) + N["entry_margin_pct"]',
     '    return AE.warning_line(rl["line"], None, N["account_end"]) + 2'),
    ("a_bad_write_keeps_the_old_plan", P, '        bad = problems(new)\n        if bad:\n            raise Refused("; ".join(bad))\n        new["rev"]',
     '        write_atomic(d / "plan.json", new)\n        bad = problems(new)\n        if bad:\n            raise Refused("; ".join(bad))\n        new["rev"]'),
    ("two_writers_lose_no_change", P, '        fcntl.flock(lk, fcntl.LOCK_EX)      # a write', '        pass      # a write'),
    ("every_write_has_an_undo", P, *UNDO),
    ("a_write_is_never_refused_for_a_missing_flag", P,
     '        if not any(meta.get(k) for k in ("why", "owner_said", "by_card", "per_ruling")):\n            rec["why"] = "no reason given"',
     '        if not any(meta.get(k) for k in ("why", "per_ruling")):\n            raise Refused("a write needs --why")'),
    ("a_hold_needs_an_end_and_ends_by_itself", P, '<= now < stamp_or(h.get("ends"), 0)]', '<= now]'),
    ("a_request_is_done_by_the_switchers_log", P, 'stamp_or(s.get("ts"), 0) >= at for s in log)', 'False for s in log)'),
    ("whatif_writes_nothing", P, '        f = gather(now)\n        wa, wb = week_ahead(plan, f), week_ahead(new, f)',
     '        write_atomic(plan_dir() / "plan.json", new)\n        f = gather(now)\n        wa, wb = week_ahead(plan, f), week_ahead(new, f)'),
    ("the_four_answers_stay_apart", P, '            lvl, mark = "UNMEASURED: %s" % (r.get("why") or r["state"]), age',
     '            lvl, mark = "0% left", age'),
    ("every_account_is_listed_as_left", P, '                out.append("  %-10s not on this machine" % a)', '                pass'),
    ("status_reads_no_slow_source", P, '    if slow:\n        try:\n            codex = meter_reading(', '    if True:\n        try:\n            codex = meter_reading('),
    ("the_tool_never_touches_a_credential", P, 'OK, NO, COULD_NOT_LOOK, REFUSED, FAILED, NONE = 0, 1, 2, 3, 4, 5',
     'OK, NO, COULD_NOT_LOOK, REFUSED, FAILED, NONE = 0, 1, 2, 3, 4, 5\nCRED = Path.home() / ".claude" / ".credentials.json"'),
    ("burn_mode_enters_on_measured_allowance_at_risk", P, '                on = risk >= bm["min_at_risk_pts"]', '                on = True'),
    ("burn_mode_never_counts_under_a_leave_line", P, '            usable = max(0.0, r["left"] - rl["line"])', '            usable = r["left"]'),
    ("burn_mode_does_not_raise_on_a_loaded_machine", P, '    raise_ok = load is not None and load <= cap', '    raise_ok = True'),
    ("burn_mode_ends_at_the_reset", P, '        elif h > bm["window_h"]:', '        elif False:'),
    ("the_reset_day_rule_is_plan_data", P, 'h is not None and 0 < h <= rd["hours"]', 'h is not None and 0 < h <= 24'),
    ("measures_count_erased_points_and_switches", P, '            if ra - ta > 6 * 3600:', '            if False:'),
    ("tick_drives_the_old_actuator", P,
     '        rc = SP.check(dry=dry, **({"passes": 5} if not seams else {k: v for k, v in seams.items() if k != "frame"}))',
     '        rc = 0'),
    ("the_timer_runs_the_driver_that_the_plan_names", P, '    if plan is not None and plan.get("driver", "old") == "new":',
     '    if plan is not None:'),
    ("shadow_acts_on_nothing", P, '    if shadow:\n        f = seams["frame"] if "frame" in seams else gather(slow=True)',
     '    if False:\n        f = seams["frame"] if "frame" in seams else gather(slow=True)'),
    ("a_hold_makes_the_pass_passive", P, '    if active(plan["holds"], clock()):\n        h = active(plan["holds"], clock())[0]',
     '    if False:\n        h = active(plan["holds"], clock())[0]'),
    ("shadow_drain_is_not_the_plan_tools", P, 'def log(rec: dict) -> None:',
     'def drained(d, plan, live_runs):\n    return d\n\n\ndef log(rec: dict) -> None:'),
    ("replay_names_each_difference", RP, 'return "ENTRY_LINE" if nd in ("soft", "normal") else "UNEXPLAINED"',
     'return "ENTRY_LINE" if nd in ("soft", "normal") else "STAY"'),
    ("census_lent_account_window_and_leave_line", P, '                        s[k] = value(v) if k in ("leave", "warn") else v',
     '                        s[k] = value(v) if k in ("leave", "warn") else s.get(k, v)'),
    ("census_fixed_priority_order", P, '                rank = {x: i for i, x in enumerate(a.accounts)}', '                rank = {x: 0 for x in a.accounts}'),
    ("census_set_floor_and_leave_line", P, '                    p["steps"][find_step(p, parts[1])][parts[2]] = value(v)', '                    find_step(p, parts[1])'),
    ("census_hold_with_why_and_end", P, '"ends": lf["ends"], "why": words(a)})', '"ends": lf["ends"], "why": ""})'),
    ("census_one_week_allowance_ends_at_reset", P, '        if rs is not None:\n            end = rs if end is None else min(end, rs)',
     '        if rs is not None and end is not None:\n            end = min(end, rs)'),
    ("census_leave_line_relative_to_entry_level", P, '            lv = max(N["floor_pct"], e - float(lv.split("-", 1)[1]))',
     '            lv = max(N["floor_pct"], (e if env.left(a) is None else env.left(a)) - float(lv.split("-", 1)[1]))'),
    ("census_pin_account_now_plan_does_not_fight", P, '    pin = [p for p in active(plan["pins"], now) if p["account"] == live]', '    pin = []'),
    ("census_temporary_order_and_line_until_reset", P, '                    if acc in lines:\n                        s["leave"] = value(lines[acc])',
     '                    if acc in lines:\n                        pass'),
    ("census_line_by_time_of_day", P, '        d = datetime.fromtimestamp(self.now, TZ)\n        return d.hour * 60',
     '        d = datetime.fromtimestamp(self.now, timezone.utc)\n        return d.hour * 60'),
    ("census_switch_now_when_no_run_is_live", P, '        if q.get("now") or (runs is not None and not runs):', '        if True:'),
    ("census_use_until_pct_then_next", P, '                    p["steps"][idx[-1]]["leave"] = lv', '                    pass'),
    ("census_reorder_and_lower_line_until_reset", P, '                p["steps"] = new + p["steps"]', '                p["steps"] = p["steps"] + new'),
    ("census_no_rule_lives_in_prose", P, '        line = lv + (N["evening_share_pct"] if kind == "claude" else 0)', '        line = lv'),
    ("census_set_warn_and_emergency_numbers", P, '    cfg, fr = N["account_end"], N["fresh"]\n    hold = active(',
     '    cfg, fr = {**N["account_end"], "warn_pct": 2, "warn_fast_pct": 3}, N["fresh"]\n    hold = active('),
    ("census_refill_is_seen_from_the_meter_no_marker", P, *MARKER),
    ("census_codex_leave_line_in_the_same_plan", P, '    if r["left"] > rl["line"]:\n        return OK, "yes', '    if r["left"] > 25:\n        return OK, "yes'),
    ("status_shows_pool_pace_not_sets_it", P, '        out.append("BURN MODE %s: %s. %s" % (a, v["state"].upper(), v["why"]))', '        pass'),
    ("fault_stale_marker_kept_a_refilled_account_out", P, *MARKER),
    ("fault_forecast_disagreed_with_the_pick", P, *MARKER),
    ("fault_preference_switch_drained_at_eighteen_percent", P, *PULL),
    ("fault_plan_change_needed_edit_publish_pull", P, 'Path.home() / ".local/state/rimmandrake/account_plan")', 'HERE / "account_plan_state")'),
    ("fault_hand_hold_six_seconds_before_a_pass", P, '        p, w = load_plan()\n        if p is None:\n            return {"do": "passive", "why": w}',
     '        p, w = plan, None\n        if p is None:\n            return {"do": "passive", "why": w}'),
    ("fault_stop_and_undo_crossed", P, *UNDO),
]


def run(plant=None):
    """-> (rc, output) of the selftest in a copy of src/RimMandrake's two folders, with the plant in."""
    tmp = Path(tempfile.mkdtemp(prefix="account_plan_mutant_"))
    try:
        root = tmp / "src" / "RimMandrake"
        for d in ("Utils", "rimflow"):
            shutil.copytree(SRC / d, root / d, ignore=shutil.ignore_patterns("__pycache__", "*.png", "*.dll"))
        if plant:
            p = root / plant[1]
            s = p.read_text(encoding="utf-8")
            if s.count(plant[2]) != 1:
                return None, "anchor found %d times" % s.count(plant[2])
            p.write_text(s.replace(plant[2], plant[3]), encoding="utf-8")
        r = subprocess.run([sys.executable, str(root / "Utils" / "selftest_account_plan.py")], capture_output=True, text=True,
                           timeout=time_budget.CALL_S, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONPATH=""))
        return r.returncode, r.stdout + r.stderr
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main(argv=None):
    from concurrent.futures import ThreadPoolExecutor
    only = set(sys.argv[1:] if argv is None else argv)
    plants = [p for p in PLANTS if not only or p[0] in only]
    rc, out = run()
    if rc != 0 or "selftest_account_plan: 0 FAIL" not in out:
        print("CONTROL RED: the harness proves nothing:\n" + out[-800:])
        return 3
    bad = 0
    with ThreadPoolExecutor(3) as ex:     # each run has its own copy and its own scratch dirs
        for p, (rc, out) in zip(plants, ex.map(run, plants)):
            fails = [x for x in out.splitlines() if x.startswith("FAIL  ")]
            named = [x for x in fails if x[6:].startswith(p[0])]
            ok = rc == 1 and bool(named)
            bad += not ok
            print("%s %s: %s -> %s" % ("caught " if ok else "MISSED ", p[0], p[2].strip().splitlines()[0][:70],
                                       named[0][6:150] if named else (out[-160:] if rc is None else "%d other FAIL(s): %s" % (
                                           len(fails), fails[:1]))))
    print("account_plan_mutants: %s (%d of %d caught, control green)" % ("FAIL" if bad else "PASS", len(plants) - bad, len(plants)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
