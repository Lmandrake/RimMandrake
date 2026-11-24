#!/usr/bin/env python3
"""selftest for the switching plan's dated, self-expiring exceptions (switching_plan.json `exceptions`, read by
switching_plan.at() and slot_allocator.lent_allowance). Pure: scratch plans, a synthetic meter, no switcher.

Regimes read: the guard (each broken shape refused, a good one accepted), before `from`, inside the exception,
after `until`, after the reset of `ends_at_reset_of` (that reset read from the meter, rolled by whole weeks, so a
simulated week-later record still ends it), the decision, the pool, the week ahead, and the lent allowance.

    python3 src/RimMandrake/Utils/selftest_switching_plan_exceptions.py
"""
import copy
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TMP = Path(tempfile.mkdtemp(prefix="selftest_switching_plan_exc_"))
os.environ["RM_SWITCH_PLAN_DIR"] = str(TMP / "out")
os.environ["RM_ACCOUNTS_DIR"] = str(TMP / "accounts")
sys.path.insert(0, str(HERE))
import switching_plan as SP  # noqa: E402
import slot_allocator as SA  # noqa: E402

FAILS, CASES = [], [0]
NOW = 1_800_000_000.0
H = 3600.0


def check(ok, msg):
    CASES[0] += 1
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def R(left, h):
    return {"source": "MEASURED", "week_pct_left": left, "week_pct_used": 100 - left, "hours_to_week_reset": h,
            "week_resets_at": SP.iso(NOW + h * H), "stale": False, "age_min": 1.0}


# the standing plan's shape (the real file's numbers), so the case reads like the day it was built for
BASE = SP.load_plan()
BASE = {**copy.deepcopy(BASE), "exceptions": []}
A, B, C = BASE["order"]  # the windowed lent account first, then the two owned ones, as the real file has them
EXC = {"id": "T_EXC", "from": SP.iso(NOW - 1 * H), "until": SP.iso(NOW + 27.5 * H), "ends_at_reset_of": A,
       "order": [B, A, C], "accounts": {A: {"leave_pct_left": 35, "window_h_after_reset": None}},
       "_why": "test"}


def plan_with(*exc):
    return {**copy.deepcopy(BASE), "exceptions": [copy.deepcopy(e) for e in exc]}


def refill_cases(mk):
    """RIMMANDRAKE_CLEAR_STEVEN_MARKER_HIS_REFILL_READS_AS_SPENT: the live case of 2026-11-24. Under
    SYSTEM_THEN_STEVEN_TO_FLOOR_2026_11_20 (system 3, steven 5, order system, steven, lukas) steven was left at 5% on
    11-21 17:45 (marker line 5); he then used a spare reset and read 97% MEASURED with his weekly reset unmoved; lukas
    live at 21%, system at its 3% line. The marker kept him out until 11-25 and the fleet would go DARK at lukas' 2%."""
    e5 = {"id": "T_EXC5", "from": SP.iso(NOW - 70 * H), "until": SP.iso(NOW + 26 * H), "ends_at_reset_of": A,
          "order": [B, A, C], "accounts": {A: {"leave_pct_left": 5, "window_h_after_reset": None},
                                           B: {"leave_pct_left": 3}}, "_why": "test"}
    P5 = plan_with(e5)

    def M(a_left, src="MEASURED", age=1.0, stale=False, c_left=21):
        return {A: {**R(a_left, 24.7), "source": src, "age_min": age, "stale": stale}, B: R(3, 22.7), C: R(c_left, 25.8)}
    left5 = mk(A, C, -67.5, line=5)  # use_steven_to_lukas_20261125: at 11-21 17:45, about 67.5 h before 11-24 13:15
    d = SP.decide(M(97), C, NOW, P5, {}, left5, polled=True)
    check(d["do"] == "switch" and d["to"] == A,
          f"refill: {A} left at 5% reads 97% MEASURED after the marker: the marker lifts, switch to {A} "
          f"({d['do']} {d.get('to')}: {d['why']})")
    d = SP.decide(M(97), C, NOW, P5, {}, {}, polled=True)
    check(d["do"] == "switch" and d["to"] == A, f"control, no marker: switch to {A} ({d['do']} {d.get('to')})")
    # the bar: the most the account can read when left is its fast warning line (5 -> 6), and a refill must clear its
    # soft margin (2) above that: 8 still keeps it out, 9 lifts it
    ceil = SP.AE.warning_line(5, None, P5["account_end"]) + P5["soft_margin_pct"]
    for p, out in ((6, True), (7, True), (ceil, True), (ceil + 1, False), (50, False)):
        d = SP.decide(M(p), C, NOW, P5, {}, left5, polled=True)
        kept = d.get("to") != A
        check(kept == out, f"refill bar {ceil}%: {A} reads {p}% after the marker: "
                           f"{'kept out' if out else 'lifted'} ({d['do']} {d.get('to')})")
    # a refill is read from a MEASURED level only, never an estimate, a stale figure or one taken before the marker
    for kw, what in (({"src": "ESTIMATE"}, "an ESTIMATE"), ({"stale": True}, "a stale MEASURED figure"),
                     ({"age": 67.5 * 60 + 5}, "a MEASURED figure taken before the marker"),
                     ({"age": None}, "a MEASURED figure with no age")):
        d = SP.decide(M(97, **kw), C, NOW, P5, {}, left5, polled=True)
        check(d.get("to") != A, f"{what} of 97% lifts no marker ({d['do']} {d.get('to')}: {d['why']})")
    # the same, on refilled() itself (an ESTIMATE or stale account is also not eligible, which hides it in decide)
    eff = SP.at(P5, NOW, M(97))
    for kw, want in (({}, True), ({"src": "ESTIMATE"}, False), ({"stale": True}, False)):
        got = SP.refilled(eff, A, left5["k"], 5, M(97, **kw), NOW)
        check(got is want, f"refilled() on 97% {kw or 'MEASURED'}: {got} (want {want})")
    # the standing plan is unchanged: outside the exception a refilled account stays kept out by its marker
    d = SP.decide(M(97), C, NOW, BASE, {}, left5, polled=True)
    check(d.get("to") != A, f"standing plan: the refill lifts nothing ({d['do']} {d.get('to')})")
    # after the lift: burnt again to 5% it is left again, and the new marker binds (no flap back at 5-8%)
    d = SP.decide(M(5), A, NOW + 20 * H, P5, {}, left5, polled=True)
    check(d["do"] == "switch" and d["to"] == C and d.get("under"),
          f"{A} live at 5% after the refill: switch away to {C} ({d['do']} {d.get('to')})")
    again = mk(A, C, 20, line=5)
    for p in (5, 7):
        d = SP.decide(M(p), C, NOW + 20.5 * H, P5, {}, again, polled=True)
        check(d.get("to") != A, f"left again at 5%, {A} re-reads {p}%: kept out ({d['do']} {d.get('to')})")


def main():
    # ---- the guard: every broken shape is refused, with its reason; a good one passes
    check(SP.exception_problems(plan_with(EXC)) == [], f"a well-formed exception passes the guard "
                                                       f"({SP.exception_problems(plan_with(EXC))})")
    broken = {
        "no until (no expiry)": {k: v for k, v in EXC.items() if k != "until"},
        "no from": {k: v for k, v in EXC.items() if k != "from"},
        "no id": {k: v for k, v in EXC.items() if k != "id"},
        "no provenance": {k: v for k, v in EXC.items() if k != "_why"},
        "until without a UTC offset": {**EXC, "until": "2027-01-16T12:00:00"},
        "until not a date": {**EXC, "until": "Wednesday"},
        "until before from": {**EXC, "until": SP.iso(NOW - 2 * H)},
        "longer than a week": {**EXC, "until": SP.iso(NOW + 8 * 24 * H)},
        "order not the standing accounts": {**EXC, "order": [B, A]},
        "order with a stranger": {**EXC, "order": [B, A, "zed"]},
        "an account outside the plan": {**EXC, "accounts": {"zed": {"leave_pct_left": 35}}},
        "an unknown rule key": {**EXC, "accounts": {A: {"leave_pct": 35}}},
        "a line over 100": {**EXC, "accounts": {A: {"leave_pct_left": 135}}},
        "a line under 0": {**EXC, "accounts": {A: {"leave_pct_left": -1}}},
        "a line that is not a number": {**EXC, "accounts": {A: {"leave_pct_left": "35"}}},
        "a window that is not a number or null": {**EXC, "accounts": {A: {"window_h_after_reset": "48"}}},
        "ends_at_reset_of a stranger": {**EXC, "ends_at_reset_of": "zed"},
        "an unknown top-level key": {**EXC, "floors": {"wait_pct_left": 0}},
        "changes nothing": {k: v for k, v in EXC.items() if k not in ("order", "accounts")},
    }
    for name, e in broken.items():
        pr = SP.exception_problems(plan_with(e))
        check(len(pr) == 1 and "T_EXC" in pr[0] or (name == "no id" and len(pr) == 1),
              f"guard refuses {name}: {pr}")
    two = SP.exception_problems(plan_with(EXC, {**EXC, "id": "T_EXC2"}))
    check(len(two) == 1 and "overlap" in two[0], f"guard refuses two exceptions active at once: {two}")
    check(SP.exception_problems({**BASE, "exceptions": {"id": "x"}}) != [], "guard refuses exceptions that is not a list")

    meter = {A: R(55, 27.3), B: R(13, 25.3), C: R(2, 28.3)}
    # ---- a broken exception is never applied: the standing plan stands
    bad = plan_with({k: v for k, v in EXC.items() if k != "until"})
    check(SP.at(bad, NOW, meter)["order"] == BASE["order"], "a refused exception (no expiry) changes nothing")
    _l, el = SP.lines(meter, bad, NOW)
    check(SP.pick(meter, bad, NOW, el) == B and _l[B] == 2, f"refused: standing lines {_l}, {B} idles at 2%")

    P = plan_with(EXC)
    # ---- active window
    check(SP.at(P, NOW - 2 * H, meter)["order"] == BASE["order"], "before `from`: standing plan")
    eff = SP.at(P, NOW, meter)
    check(eff["order"] == [B, A, C] and eff["accounts"][A]["leave_pct_left"] == 35
          and eff["accounts"][A].get("window_h_after_reset") is None and eff.get("_exception") == "T_EXC",
          f"inside: order {eff['order']}, {A} {eff['accounts'][A]}")
    check(P["order"] == BASE["order"] and P["accounts"][A] == BASE["accounts"][A], "at() never edits the plan it reads")
    reset_a = NOW + 27.3 * H
    check(SP.at(P, reset_a - 60, meter).get("_exception") == "T_EXC", "a minute before the reset: still on")
    check(SP.at(P, reset_a + 1, meter).get("_exception") is None, f"{A}'s reset (from the meter) ends it")
    rolled = {A: {**meter[A], "week_resets_at": SP.iso(reset_a + SP.WEEK)}}
    check(SP.at(P, reset_a + 1, rolled).get("_exception") is None,
          "a record rolled a week on (the simulation's) still ends it at the first reset after `from`")
    check(SP.at(P, NOW + 27.5 * H + 1, {}).get("_exception") is None, "no meter: `until` alone ends it")
    check(SP.at(P, NOW + 27.4 * H, {}).get("_exception") == "T_EXC", "no meter: on until `until`")

    # ---- the decision: system first, then the lent account to 35%, then a stop
    d = SP.decide(meter, B, NOW, P, {}, {}, polled=True)
    away = BASE["floors"]["switch_away_pct_left"]
    check(d["do"] == "normal" and d["line"] == away, f"{B} live at 13%: normal, line {away} (someone takes over): {d['do']} {d['line']}")
    m0 = {**meter, B: R(0, 25.3)}
    d = SP.decide(m0, B, NOW, P, {}, {}, polled=True)
    check(d["do"] == "switch" and d["to"] == A, f"{B} at 0%: switch to {A} ({d['do']} {d.get('to')}: {d['why']})")
    m35 = {**m0, A: R(35, 27.3)}
    d = SP.decide(m35, A, NOW, P, {}, {}, polled=True)
    check(d["do"] == "stop" and d["line"] == 35, f"{A} at 35%: hard stop ({d['do']} line {d['line']}: {d['why']})")
    d = SP.decide({**m0, A: R(37, 27.3)}, A, NOW, P, {}, {}, polled=True)
    check(d["do"] == "soft", f"{A} at 37% (line + soft margin): soft ({d['do']})")
    d = SP.decide(m0, B, NOW, BASE, {}, {}, polled=True)
    check(d["do"] != "switch", f"control, standing plan: {B} at 0% never switches to {A} outside his window ({d['do']})")
    # after `until`, on the lent account outside his window: spent by the standing rule again, a hard stop
    short = plan_with({**EXC, "until": SP.iso(NOW + 2 * H)})
    d = SP.decide({A: R(50, 27.3), B: R(0, 25.3), C: R(2, 28.3)}, A, NOW + 3 * H, short, {}, {}, polled=True)
    check(d["do"] == "stop" and d.get("exception") is None,
          f"after `until` {A} (outside his window) is spent again: {d['do']} ({d['why']})")
    d = SP.decide({A: R(50, 27.3), B: R(0, 25.3), C: R(2, 28.3)}, A, NOW + 1 * H, short, {}, {}, polled=True)
    check(d["do"] == "normal" and d.get("exception") == "T_EXC", f"before `until` the same reading runs: {d['do']}")
    d = SP.decide(meter, B, NOW, bad, {}, {}, polled=True)
    check(any("T_EXC" in x for x in d.get("exception_refused") or []), f"a refused exception is named in every "
                                                                        f"decision: {d.get('exception_refused')}")

    # ---- a done/under marker for A (left at its standing 52% line before the exception) does not hide the budget the
    # exception opened (RIMMANDRAKE_FIX_SWITCHING_PLAN_EXCEPTION_MARKERS: live 2026-11-17, the engine picked C at 2%)
    def mk(frm, to, at_h, **kw):
        return {"k": {"at": SP.iso(NOW + at_h * H), "from": frm, "to": to, "phase": "done", "under": True, **kw}}
    left_a = mk(A, B, -118)  # a legacy marker: no line recorded (the live one, 11-12 13:50, ~118 h before the case)
    d = SP.decide(m0, B, NOW, P, {}, left_a, polled=True)
    check(d["do"] == "switch" and d["to"] == A, f"marker (no line) + exception: {B} at 0% switches to {A}, never {C} "
                                                f"({d['do']} {d.get('to')}: {d['why']})")
    d = SP.decide(m0, B, NOW, P, {}, mk(A, B, -118, line=52), polled=True)
    check(d["do"] == "switch" and d["to"] == A, f"marker (line 52) + exception line 35: switch to {A} ({d['do']} {d.get('to')})")
    for p in (35, 34):
        d = SP.decide({**m0, A: R(p, 27.3)}, B, NOW, P, {}, left_a, polled=True)
        check(d["do"] == "stop" and d.get("to") is None, f"marker + exception, {A} at {p}% (<= 35): IDLE, {C} at 2% "
                                                         f"never picked ({d['do']} {d.get('to')}: {d['why']})")
    d = SP.decide({**m0, A: R(36, 27.3)}, A, NOW, P, {}, left_a, polled=True)
    check(d["do"] == "soft" and d.get("to") is None, f"{A} live at 36% with the marker: burns on, soft ({d['do']} {d.get('to')})")
    # A re-reads 38%: above the 35% line, and the most it can read when left there (fast warning line 36 + soft margin
    # 2). These two read 40% until 2026-11-24; 40% after a leave at 35% is a MEASURED refill (usage only grows inside a
    # week; no upward re-read under 26 points in 5,319 plan-log records), which lifts the marker (refill_cases)
    d = SP.decide({**m0, A: R(38, 27.3)}, B, NOW, P, {}, mk(A, B, -5, line=35), polled=True)
    check(d["do"] == "stop", f"a marker left at the exception's own 35% line still excludes {A} ({d['do']} {d.get('to')})")
    d = SP.decide({**m0, A: R(38, 27.3)}, B, NOW, P, {}, mk(A, B, -0.5), polled=True)
    check(d["do"] == "stop", f"a legacy marker written inside the exception reads its line (35): {A} excluded ({d['do']})")
    d = SP.decide({**m0, A: R(40, 27.3)}, B, NOW, P, {}, mk(A, B, -5, line=35), polled=True)
    check(d["do"] == "switch" and d["to"] == A, f"left at 35%, {A} reads 40% MEASURED: a refill, switch to {A} "
                                                f"({d['do']} {d.get('to')})")
    # the marker's meaning is unchanged outside the exception: A in its window, left at 52%, re-reads 60%
    inwin = {A: R(60, 150), B: R(40, 25.3), C: R(30, 28.3)}
    d = SP.decide(inwin, B, NOW, BASE, {}, mk(A, B, -10), polled=True)
    check(d["do"] == "normal" and d.get("to") is None, f"standing plan: the marker keeps {A} out ({d['do']} {d.get('to')})")
    d = SP.decide(inwin, B, NOW, BASE, {}, {}, polled=True)
    check(d["do"] == "switch" and d["to"] == A, f"control, no marker: {A} in its window is the target ({d['do']} {d.get('to')})")
    d = SP.decide(inwin, B, NOW + 3 * H, short, {}, mk(A, B, -10), polled=True)
    check(d["do"] == "normal" and d.get("exception") is None,
          f"after the exception expires the marker excludes {A} again ({d['do']} {d.get('to')})")
    # a marker for an account whose line the exception does not lower keeps its meaning inside the exception
    d = SP.decide({A: R(50, 27.3), B: R(1, 25.3), C: R(2, 28.3)}, A, NOW, P, {}, mk(B, A, -1), polled=True)
    check(d["do"] == "normal" and d.get("to") is None, f"{B} left at its floor re-reads 1%: no flap back ({d['do']} {d.get('to')})")

    refill_cases(mk)

    # ---- the pool counts the exception's budget only while it stands
    pl = SP.pool(meter, NOW, P)
    pa = [x for x in pl["parts"] if x["account"] == A and x["by_h"] < 30]
    check(pa and abs(pa[0]["spend_pct"] - 20) < 1e-6, f"pool: {A}'s 55->35 is due inside the exception ({pa})")
    pl0 = SP.pool(meter, NOW, BASE)
    check(not [x for x in pl0["parts"] if x["account"] == A and x["by_h"] < 27.3],
          f"control: standing pool has no present {A} budget ({pl0['parts'][:3]})")

    # a budget only the exception opens is due when the exception ends, not at the account's reset (review finding 2)
    pl = SP.pool(meter, NOW, short)
    early = sum(x["spend_pct"] for x in pl["parts"] if x["account"] == A and x["by_h"] <= 2.0 + 1e-6)
    late = [x for x in pl["parts"] if x["account"] == A and 2.0 + 1e-6 < x["by_h"] < 27.3 + 1e-6]
    check(abs(early - 20) < 1e-6 and not late, f"pool: an exception ending in 2 h makes {A}'s 20% due in 2 h "
                                                f"(due by 2 h: {early}; later present parts: {late})")
    # a refill a week past the exception follows the standing line, not the first refill's exception line (finding 3)
    span = plan_with({"id": "T_SPAN", "from": SP.iso(NOW - 1 * H), "until": SP.iso(NOW + 30 * H),
                      "accounts": {A: {"leave_pct_left": 35}}, "_why": "test"})
    pl = SP.pool({A: R(55, 5), B: R(40, 100), C: R(30, 120)}, NOW, span)
    wk = [x for x in pl["parts"] if x["account"] == A and x["by_h"] > 5 + 168]
    std = 100 - BASE["accounts"][A]["leave_pct_left"]
    check(wk and abs(sum(x["spend_pct"] for x in wk) - std) < 1e-6,
          f"pool: {A}'s refill after the exception ended is {std}% (standing line), not 65% ({wk})")
    first = [x for x in pl["parts"] if x["account"] == A and 5 < x["by_h"] <= 5 + 48 + 1e-6]
    check(abs(sum(x["spend_pct"] for x in first) - 65) < 1e-6
          and any(abs(x["by_h"] - 30) < 1e-6 and abs(x["spend_pct"] - 17) < 1e-6 for x in first),
          f"pool: {A}'s refill inside the exception is 65%, its extra 17% due at the exception's end ({first})")

    # ---- the week ahead: B, then A to 35%, then IDLE until B's reset; after A's reset the standing lines
    ev = SP.simulate(meter, NOW, P, B, 1.32, hours=60)
    seq = [(e["kind"], e.get("target") or e.get("account")) for e in ev]
    want = [("target", B), ("target", A), ("target", None), ("reset", B), ("target", B), ("reset", A), ("target", A)]
    check(seq[:7] == want, f"week ahead: {seq[:8]}")
    txt = SP.week_lines(ev, P)
    check("to 35% left" in txt[1] and "T_EXC" in txt[1], f"week line names the exception: {txt[1]!r}")
    check("to 52% left" in txt[6] or "to %s%% left" % BASE["accounts"][A]["leave_pct_left"] in txt[6],
          f"after the reset the standing line: {txt[6]!r}")
    stop_at = [e for e in ev if e["kind"] == "target" and e["target"] is None][0]
    check(abs(stop_at["pct"][A] - 35) < 0.05 and stop_at["pct"][B] == BASE["floors"]["switch_away_pct_left"],
          f"IDLE with {A} at {stop_at['pct'][A]}% (limit 35) and {B} at {stop_at['pct'][B]}%")

    # ---- the lent allowance reads the same exception (one source: the plan file)
    rules = {"lent_accounts": {A: {"max_used_by_us_pct": 48, "prefer_start_of_week_h": 48, "floor_pct_left": 10}}}
    sp = {"account": A, "pct_left": 55.0, "pct_used": 45.0, "hours_to_reset": 27.3}
    cap, why = SA.lent_allowance(sp, rules, NOW, plan=P)
    check(abs(cap - 20) < 1e-6 and "T_EXC" in why, f"lent allowance inside the exception: {cap} ({why})")
    cap, why = SA.lent_allowance(sp, rules, NOW, plan=BASE)
    check(cap == 0, f"control, standing: outside his window the allowance is 0 ({cap}: {why})")
    cap, why = SA.lent_allowance({**sp, "hours_to_reset": 0.1}, rules, NOW + 27.4 * H, plan=P)
    check(cap > 0, f"with the reset still ahead (0.1 h), the exception holds ({cap}: {why})")
    cap, _w = SA.lent_allowance({**sp, "pct_left": 30.0, "pct_used": 70.0}, rules, NOW, plan=P)
    check(cap == 0, f"under the exception's line the allowance is 0 ({cap})")
    low = plan_with({**EXC, "accounts": {A: {"leave_pct_left": 5, "window_h_after_reset": None}}})
    cap, _w = SA.lent_allowance(sp, rules, NOW, plan=low)
    check(abs(cap - 45) < 1e-6, f"the lent floor (10%) still binds under an exception line of 5% ({cap}, limit 45)")
    cap, _w = SA.lent_allowance({**sp, "account": B}, rules, NOW, plan=P)
    check(cap is None, "an account with no lent rule is untouched")

    print(f"{CASES[0]} cases read; " + (f"FAILED {len(FAILS)}" if FAILS else "all passed"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
