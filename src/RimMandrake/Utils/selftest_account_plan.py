#!/usr/bin/env python3
"""selftest: the account plan (RIMMANDRAKE_DESIGN_ACCOUNT_PLAN_ONE_FILE_COMMANDED_IN_ONE_LINE; page
design/specs/2026-11-24-account-plan-one-file/boundary.md). One check per promise, by its name. Planted readings, a
fake switcher, a fake clock and scratch dirs only: it never reads the live meter, the live runs, the live plan file or
the real switcher. The planted faults: account_plan_mutants.py.

    python3 src/RimMandrake/Utils/selftest_account_plan.py
"""
import contextlib
import copy
import io
import itertools
import json
import os
import stat
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
TMP = Path(tempfile.mkdtemp(prefix="selftest_account_plan_"))
os.environ["RM_ACCOUNT_PLAN_DIR"] = str(TMP / "plan")
os.environ["RM_ACCOUNT_PLAN_FRAME"] = str(TMP / "frame.json")
os.environ["RM_ACCOUNT_PLAN_SERIES"] = str(TMP / "series.jsonl")
os.environ["RM_SWITCH_PLAN_DIR"] = str(TMP / "out")
os.environ["RM_ACCOUNTS_DIR"] = str(TMP / "accounts")
os.environ["RM_CONTROL_DB"] = str(TMP / "control.db")
os.environ["RM_DISPATCHER_STATE"] = str(TMP / "state")
os.environ.setdefault("RM_UNDER_SELFTEST", "1")
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "rimflow"))
import account_plan as AP  # noqa: E402
import account_plan_replay as RP  # noqa: E402
import switching_plan as SP  # noqa: E402

FAILS = []
NOW = AP.stamp("2026-11-24T14:00:00-08:00")
os.environ["RM_ACCOUNT_PLAN_NOW"] = repr(NOW)      # the clock of every command here
LEGACY = json.loads((HERE / "switching_plan.json").read_text())
LEGACY["exceptions"] = []
SEED = json.loads((HERE / "account_plan.seed.json").read_text())
BASE = AP.convert_legacy(LEGACY, SEED)      # steven (52, 48 h window), system, lukas, codex 25
SRC = (HERE / "account_plan.py").read_text()
RUN = ["rm-detached-bench-some-builder-1"]
(TMP / "series.jsonl").write_text("")


def check(name, ok, detail=""):
    print(("ok    " if ok else "FAIL  ") + name + ("" if ok or not detail else ": " + str(detail)[:500]))
    if not ok:
        FAILS.append(name)


def R(left, h, src="MEASURED", age=1.0, stale=False, now=NOW):
    return {"source": src, "week_pct_left": left, "week_pct_used": None if left is None else 100 - left,
            "hours_to_week_reset": h, "week_resets_at": AP.iso(now + h * 3600), "stale": stale, "age_min": age}


def F(live, rows, runs=(), burn_h=4.0, now=NOW, **kw):
    f = {"now": now, "live": live, "runs": None if runs is None else list(runs), "rows": rows, "burn_h": burn_h,
         "burn_live": {"rate": (burn_h or 0) / 60, "stale": burn_h is None, "age_s": 0}, "switches": [], "hand": False,
         "markers": {}, "state": {}, "codex": {**AP.reading(None, now), "burn_h": None}, "genai": ["absent", None],
         "load": 2.0, "ncpu": 14}
    f.update(kw)
    return f


def plan(order=None, **steps):
    """BASE with the Claude steps in `order`, and fields of steps changed: plan(steven={"leave": 5, "when": None})."""
    p = copy.deepcopy(BASE)
    if order:
        p["steps"].sort(key=lambda s: order.index(s["use"]) if s["use"] in order else 99)
    for name, ch in steps.items():
        s = p["steps"][AP.find_step(p, name)]
        for k, v in ch.items():
            if v is None:
                s.pop(k, None)
            else:
                s[k] = v
    return p


FAR = {"steven": R(90, 100), "system": R(80, 110), "lukas": R(18, 120)}      # steven outside his 48 h window
OPEN = plan(steven={"leave": 5, "when": None})                              # steven usable down to 5%, any time


def rescue_frame(runs=(), **kw):
    """lukas live with a week to its reset; steven has 90% that his reset erases in 20 h: a rescue worth 60 points."""
    return F("lukas", {"steven": R(90, 20), "system": R(3, 100), "lukas": R(60, 150)}, runs=runs, **kw)


def acct(*argv, frame=None, cwd=None):
    """One ./acct command in this process (or, with cwd, in a new one). -> (exit, text)."""
    if frame is not None:
        (TMP / "frame.json").write_text(json.dumps(frame))
    if cwd is not None:
        r = subprocess.run([sys.executable, str(HERE / "account_plan.py"), *argv], capture_output=True, text=True, cwd=cwd)
        return r.returncode, r.stdout + r.stderr
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = AP.main(list(argv))
    return rc, buf.getvalue()


def fresh(p=None, frame=None):
    """A new plan file holding p (default BASE), and the frame that the commands read."""
    d = TMP / "plan"
    if d.exists():
        os.chmod(d, 0o700)
        for x in d.iterdir():
            x.unlink()
    AP.commit(lambda _old: copy.deepcopy(p or BASE), {"why": "selftest", "create": True}, base=None)
    (TMP / "frame.json").write_text(json.dumps(frame or F("lukas", FAR)))


def on_disk():
    return json.loads((TMP / "plan" / "plan.json").read_text())


def rule(p, a, f):
    rd = AP.readings_of(f)
    rd["codex"] = f["codex"]
    env = AP.Env(f["now"], lambda x: (rd.get(x) or {}).get("left"), lambda x: (rd.get(x) or {}).get("reset"),
                 entry=lambda x: (f.get("entry") or {}).get(x))
    return AP.rule_of(p, a, env)


# ------------------------------------------------------------------ the decision
def t_live_account_stays_until_its_own_line():
    n = "live_account_stays_until_its_own_line"
    for order in itertools.permutations(["steven", "system", "lukas"]):
        for burn in (None, 1.0, 4.0):
            for runs in ((), RUN):
                d = AP.decide(plan(list(order), steven={"when": None}), F("lukas", FAR, runs=runs, burn_h=burn))
                check("%s: order %s, burn %s, %d runs" % (n, "/".join(order), burn, len(runs)),
                      d["do"] == "normal" and d["to"] is None and not d.get("pending"), d)
    d = AP.decide(BASE, F("lukas", {**FAR, "lukas": R(4, 120)}, runs=RUN))
    check(n + ": one point above the warning zone it still stays", d["do"] == "normal", d)


def t_order_only_answers_which_account_is_next():
    n = "order_only_answers_which_account_is_next"
    rows = {"steven": R(90, 150), "system": R(80, 110), "lukas": R(2, 120)}
    for first in ("steven", "system"):
        p = plan([first, "system" if first == "steven" else "steven", "lukas"], steven={"when": None})
        d = AP.decide(p, F("lukas", rows, burn_h=None))
        check("%s: lukas finished, %s first -> %s" % (n, first, first), d["do"] == "switch" and d["to"] == first, d)
    a = AP.decide(plan(["steven", "system", "lukas"], steven={"when": None}), F("lukas", FAR, burn_h=None))
    b = AP.decide(plan(["lukas", "system", "steven"], steven={"when": None}), F("lukas", FAR, burn_h=None))
    check(n + ": with lukas unfinished a change of order changes no act", (a["do"], a["to"]) == (b["do"], b["to"]) ==
          ("normal", None), (a, b))


def t_no_start_is_refused_for_a_preference():
    n = "no_start_is_refused_for_a_preference"
    small = F("lukas", {"steven": R(12, 20), "system": R(3, 100), "lukas": R(60, 150)}, runs=RUN)   # 7 points at risk
    d = AP.decide(OPEN, small)
    check(n + ": a rescue too small for a drain reads normal", d["do"] == "normal" and not d.get("drain"), d)
    fresh(OPEN, rescue_frame(RUN))
    acct("switch", "steven", "--why", "t")
    d = AP.decide(on_disk(), rescue_frame(RUN, burn_h=None, now=NOW + 60))
    check(n + ": a request that waits for no live run reads normal", d["do"] == "normal" and d.get("pending"), d)
    d = AP.decide(BASE, F("lukas", {"steven": R(90, 100), "system": R(100, 0.1), "lukas": R(40, 120)}, runs=RUN))
    check(n + ": a reset that is near reads normal", d["do"] == "normal", d)
    d = AP.decide(BASE, F("lukas", {**FAR, "lukas": R(4, 120)}, runs=RUN))
    check(n + ": the zone above the warning line reads normal", d["do"] == "normal", d)
    d = AP.decide(BASE, F("lukas", {**FAR, "lukas": R(2, 120)}, runs=RUN))
    check(n + ": at the warning line it reads soft, with the account-end flag", d["do"] == "soft" and d.get("account_end"), d)


def t_a_rescue_switch_needs_points_worth_a_switch():
    n = "a_rescue_switch_needs_points_worth_a_switch"
    d = AP.decide(OPEN, rescue_frame())
    check(n + ": 60 points at risk, no run live -> the switch", d["do"] == "switch" and d["to"] == "steven"
          and not d.get("under"), d)
    d = AP.decide(OPEN, F("lukas", {"steven": R(9, 20), "system": R(3, 100), "lukas": R(60, 150)}))
    check(n + ": 1 point at risk -> it stays", d["do"] == "normal" and not d.get("pending"), d)
    p = copy.deepcopy(OPEN)
    p["numbers"]["switch_cost_pts"] = 500
    d = AP.decide(p, rescue_frame())
    check(n + ": the cost of a switch is the plan's number", d["do"] == "normal", d)
    two = F("lukas", {"steven": R(90, 20), "system": R(3, 100), "lukas": R(60, 22)})
    st, sw = AP.week_ahead(OPEN, two), AP.week_ahead(OPEN, two, first="steven")
    d = AP.decide(OPEN, two)
    check(n + ": both reset in a day: leaving saves nothing, so it stays", d["do"] == "normal"
          and st["cost"] - sw["cost"] < OPEN["numbers"]["switch_cost_pts"], (st["cost"], sw["cost"], d))


def t_a_rescue_switch_waits_for_no_live_run():
    n = "a_rescue_switch_waits_for_no_live_run"
    p = copy.deepcopy(OPEN)
    p["numbers"]["rescue"]["drain_h"] = None
    for runs, label in ((RUN, "a run live"), (None, "runs unreadable")):
        d = AP.decide(p, rescue_frame(runs))
        check("%s: %s, no drain allowed -> normal, with the points and the command" % (n, label),
              d["do"] == "normal" and (d.get("pending") or {}).get("to") == "steven" and "./acct switch steven --now" in d["why"], d)
    d = AP.decide(p, rescue_frame(()))
    check(n + ": no run live -> the switch", d["do"] == "switch" and d["to"] == "steven", d)
    d = AP.decide(OPEN, rescue_frame(RUN))
    check(n + ": with the drain number, a rescue worth more than the work delayed goes as a drain that the reason names",
          d["do"] == "switch" and not d.get("under") and "at most 2 h" in d["why"], d)
    v = AP.legacy_view(OPEN, rescue_frame(RUN))
    check(n + ": the drain is bounded by the plan's number", v["pull_drain_max_s"] == 7200, v["pull_drain_max_s"])
    f = F("lukas", {"steven": R(14, 20), "system": R(3, 100), "lukas": R(95, 150)}, runs=RUN)
    q = copy.deepcopy(OPEN)
    q["numbers"]["rescue"]["drain_h"] = 5
    d, gain = AP.decide(q, f), AP.week_ahead(q, f)["cost"] - AP.week_ahead(q, f, first="steven")["cost"]
    check(n + ": a rescue worth %s points, under 3 + 5 h of burn (23): no start is refused" % AP.g(gain),
          3 <= gain < 23 and d["do"] == "normal" and (d.get("pending") or {}).get("to") == "steven", d)


def t_an_unknown_burn_never_causes_a_switch():
    n = "an_unknown_burn_never_causes_a_switch"
    d = AP.decide(OPEN, rescue_frame((), burn_h=None))
    check(n, d["do"] == "normal" and "No burn rate" in d["why"], d)


def t_a_hand_switch_is_respected():
    n = "a_hand_switch_is_respected"
    d = AP.decide(OPEN, rescue_frame((), hand=True))
    check(n + ": the last switch was by hand -> no rescue", d["do"] == "normal" and "by hand" in d["why"], d)
    p = copy.deepcopy(OPEN)
    p["pins"] = [{"account": "lukas", "at": AP.iso(NOW - 60), "ends": AP.iso(NOW + 3600), "why": "t"}]
    d = AP.decide(p, rescue_frame(()))
    check(n + ": a pin -> no rescue", d["do"] == "normal" and "pinned" in d["why"], d)
    d = AP.decide(p, rescue_frame((), now=NOW + 7200))
    check(n + ": after the pin's end the rescue goes", d["do"] == "switch", d)
    d = AP.decide(p, F("lukas", {"steven": R(90, 20), "system": R(3, 100), "lukas": R(2, 150)}))
    check(n + ": a pinned account still ends at its line", d["do"] == "switch" and d.get("under"), d)


def t_the_reason_is_one_checkable_line():
    n = "the_reason_is_one_checkable_line"
    for label, d in (("stay", AP.decide(OPEN, F("lukas", {"steven": R(90, 60), "system": R(80, 110), "lukas": R(18, 120)},
                                                 runs=RUN))),
                     ("rescue", AP.decide(OPEN, rescue_frame()))):
        w = d["why"]
        check("%s: %s" % (n, label), "\n" not in w and "lukas" in w and "erased" in w and "switch" in w
              and ("Next:" in w or "rescue" in w), w)
    w = AP.decide(OPEN, F("lukas", {"steven": R(90, 60), "system": R(80, 110), "lukas": R(18, 120)}, runs=RUN))["why"]
    check(n + ": the level, the line, the next account and both choices are in it",
          "18%" in w and "line 1%" in w and "Next: s" in w and "Best other choice" in w and "a switch counts 3" in w, w)


def t_the_forecast_is_the_pick():
    n = "the_forecast_is_the_pick"
    rows = {"steven": R(90, 30), "system": R(80, 160), "lukas": R(2, 120)}
    for mk in ({}, {"use_lukas_to_steven_x": {"phase": "done", "under": True, "from": "steven", "at": AP.iso(NOW - 9e4)}}):
        f = F("lukas", rows, markers=mk)
        d, w = AP.decide(OPEN, f), AP.week_ahead(OPEN, f)
        first = next(e["to"] for e in w["events"] if e["kind"] == "switch")
        check("%s: finished, two can take over%s" % (n, ", a marker present" if mk else ""),
              d["do"] == "switch" and d["to"] == first, (d["to"], first))
        f = rescue_frame(markers=mk)
        d, st, sw = AP.decide(OPEN, f), AP.week_ahead(OPEN, f), AP.week_ahead(OPEN, f, first="steven")
        check("%s: the rescue is the cheaper week ahead%s" % (n, ", a marker present" if mk else ""),
              d["to"] == "steven" and sw["cost"] < st["cost"] and d["week"]["cost"] == sw["cost"], (st["cost"], sw["cost"]))
    f = F("lukas", FAR)
    check(n + ": staying, the week ahead starts on the live account", AP.week_ahead(OPEN, f)["first"] == "lukas"
          and AP.decide(OPEN, f)["do"] == "normal")
    text, rc = AP.forecast_text(OPEN, F("lukas", rows))
    check(n + ": the forecast command prints that same first switch", rc == 0 and "lukas -> %s" % first in text, text)


def t_no_marker_decides():
    n = "no_marker_decides"
    old = {"use_steven_to_system_20261125": {"phase": "done", "under": True, "from": "steven", "to": "system",
                                             "at": AP.iso(NOW - 3 * 86400), "line": 5}}
    for label, f in (("finished", F("lukas", {"steven": R(97, 24), "system": R(3, 22), "lukas": R(2, 25)})),
                     ("unfinished", F("lukas", FAR)), ("rescue", rescue_frame())):
        a, b = AP.decide(OPEN, f), AP.decide(OPEN, {**f, "markers": old})
        check("%s: %s, the same with and without a done marker" % (n, label), (a["do"], a["to"]) == (b["do"], b["to"]), (a, b))
    f = F("lukas", {"steven": R(97, 24), "system": R(3, 22), "lukas": R(2, 25)})
    key = AP.decide(OPEN, f)["key"]
    d = AP.decide(OPEN, {**f, "markers": {key: {"phase": "pending", "at": AP.iso(NOW - 60), "from": "lukas", "to": "steven"}}})
    check(n + ": a switcher call in flight is not repeated", d["do"] in ("stop", "hold", "soft") and d["do"] != "switch", d)
    d = AP.decide(OPEN, {**f, "markers": {key: {"phase": "pending", "at": AP.iso(NOW - 3 * 3600), "from": "lukas", "to": "steven"}}})
    check(n + ": a pending marker over 40 min old changes nothing", d["do"] == "switch", d)
    d = AP.decide(OPEN, {**f, "markers": {key: {"phase": "failed", "at": AP.iso(NOW - 60), "from": "lukas", "to": "steven"}}})
    check(n + ": a failed switch off a finished account is the old stop", d["do"] == "stop", d)


def t_an_account_left_at_its_line_is_no_target():
    n = "an_account_left_at_its_line_is_no_target"
    for lv in (5, 6, 8):         # line 5: warning 6, entry line 8
        d = AP.decide(OPEN, F("lukas", {"steven": R(lv, 60), "system": R(80, 110), "lukas": R(2, 120)}, burn_h=None))
        check("%s: steven at %s%% (line 5) is passed over" % (n, lv), d["do"] == "switch" and d["to"] == "system", d)
    d = AP.decide(OPEN, F("lukas", {"steven": R(9, 60), "system": R(80, 110), "lukas": R(2, 120)}, burn_h=None))
    check(n + ": above its entry line it is the target", d["to"] == "steven", d)


def t_a_refilled_account_is_a_target_at_once():
    n = "a_refilled_account_is_a_target_at_once"
    rows = {"steven": R(5, 60), "system": R(3, 22), "lukas": R(2, 120)}
    d = AP.decide(OPEN, F("lukas", rows))
    check(n + ": before the refill nobody can take over", d["do"] in ("soft", "stop") and d["to"] is None, d)
    d = AP.decide(OPEN, F("lukas", {**rows, "steven": R(97, 60)}))
    check(n + ": after it, with no command", d["do"] == "switch" and d["to"] == "steven", d)


def t_unknown_never_gives_permission():
    n = "unknown_never_gives_permission"
    env = AP.Env(NOW, lambda a: None, lambda a: None)
    tr = AP.parse("left > 5")
    check(n + ": an unknown level is unknown, and so is its negation",
          AP.truth(tr, env, "x") is None and AP.truth(AP.parse("not left > 5"), env, "x") is None)
    check(n + ": false and unknown is false; true or unknown is true",
          AP.truth(AP.parse("clock > 23:59 and left > 5"), env, "x") is False
          and AP.truth(AP.parse("clock >= 00:00 or left > 5"), env, "x") is True)
    rows = {"steven": {**R(90, 100), "week_resets_at": None}, "system": R(80, 110), "lukas": R(2, 120)}
    d = AP.decide(BASE, F("lukas", rows, burn_h=None))
    check(n + ": a window on an unknown reset is not alive", d["to"] == "system", d)
    for src, stale in (("ESTIMATE", False), ("MEASURED", True)):
        d = AP.decide(OPEN, F("lukas", {"steven": R(90, 60, src=src, stale=stale), "system": R(80, 110), "lukas": R(2, 120)},
                              burn_h=None))
        check("%s: a %s%s level makes no target" % (n, src, " stale" if stale else ""), d["to"] == "system", d)
    p = plan(lukas={"until": "left:steven > 95"})
    d = AP.decide(p, F("lukas", {"steven": R(None, 60, src="UNMEASURED"), "system": R(80, 110), "lukas": R(40, 120)}))
    check(n + ": an `until` that is unknown does not end a step", d["do"] == "normal", d)
    q = plan(steven={"leave": 5, "when": None, "from": AP.iso(NOW - 3600), "ends_at_reset_of": "steven"})
    check(n + ": a step that ends at an unknown reset is not alive",
          rule(q, "steven", F("lukas", {"steven": {**R(90, 60), "week_resets_at": None}})) is None)


def t_the_last_account_waits_at_its_wait_floor():
    n = "the_last_account_waits_at_its_wait_floor"
    alone = {"steven": R(90, 100), "system": R(1, 110), "lukas": R(10, 120)}
    d = AP.decide(BASE, F("lukas", alone))
    check(n + ": nobody can take over -> the line is the wait floor", d["line"] == 2, d)
    d = AP.decide(BASE, F("lukas", {**alone, "system": R(60, 110)}))
    check(n + ": somebody can -> the line is the floor", d["line"] == 1, d)
    d = AP.decide(BASE, F("lukas", {**alone, "lukas": R(2, 120)}))
    check(n + ": at the wait floor with no run live the old stop is due", d["do"] == "stop" and d.get("key"), d)
    d = AP.decide(BASE, F("lukas", {**alone, "lukas": R(3, 120)}, runs=RUN, burn_h=None))
    check(n + ": warned above it with nowhere to go: no new start, no stop yet", d["do"] == "soft" and d.get("account_end"), d)


# ------------------------------------------------------------------ the plan file and the commands
def t_one_file_binds_at_the_next_read():
    n = "one_file_binds_at_the_next_read"
    rows = {"steven": R(90, 150), "system": R(80, 110), "lukas": R(2, 120)}
    fresh(plan(steven={"when": None}), F("lukas", rows, burn_h=None))
    rc, a = acct("next", cwd="/tmp")
    acct("order", "system", "steven", "lukas", "--why", "t")
    rc2, b = acct("next", cwd="/tmp")
    check(n + ": a write changes the next decision of another process", "Next: steven" in a and "Next: system" in b
          and rc == rc2 == 0, (a, b))
    os.environ["RM_SWITCH_PLAN"] = str(TMP / "no-such-plan.json")
    try:
        rc3, c = acct("next", cwd="/tmp")
    finally:
        del os.environ["RM_SWITCH_PLAN"]
    check(n + ": the decision needs no switching_plan.json", rc3 == 0 and "Next: system" in c, c)
    f = rescue_frame()
    p = copy.deepcopy(OPEN)
    fresh(p, f)
    before = acct("next")[1]
    acct("set", "numbers.switch_cost_pts=500")
    after = acct("next")[1]
    check(n + ": a number of the plan file decides", "SWITCH" in before and "NORMAL" in after, (before, after))
    (TMP / "seed-moved").write_text("")
    real = AP.SEED
    AP.SEED = TMP / "no-seed.json"
    try:
        rc4, _ = acct("next")
    finally:
        AP.SEED = real
    check(n + ": with a plan file the seed is never read", rc4 == 0)


def t_a_bad_write_keeps_the_old_plan():
    n = "a_bad_write_keeps_the_old_plan"
    fresh()
    path = TMP / "plan" / "plan.json"
    before, hist = path.read_bytes(), (TMP / "plan" / "history.jsonl").read_bytes()
    for argv in (["line", "lukas", "-5"], ["line", "lukas", "0"], ["line", "nobody", "5"], ["order", "lukas", "codex"],
                 ["step", "add", "x", "--use", "lukas", "--leave", "5", "--when", "left >> 3"],
                 ["step", "add", "x", "--use", "lukas", "--leave", "5", "--until", "moon > 3"],
                 ["step", "add", "system", "--use", "lukas", "--leave", "5"], ["hold", "--why", "no end"],
                 ["set", "numbers.switch_cost_pts=-1"], ["set", "numbers.nonesuch=1"], ["step", "rm", "nonesuch"],
                 ["step", "add", "y", "--use", "lukas", "--leave", "5", "--ends-at-reset", "nobody"],
                 ["line", "lukas", "9", "--until", "tomorrow"], ["step", "set", "lukas", "colour=red"]):
        rc, text = acct(*argv)
        check("%s: %s" % (n, " ".join(argv)), rc == AP.REFUSED and text.startswith("REFUSED") and path.read_bytes() == before
              and (TMP / "plan" / "history.jsonl").read_bytes() == hist, (rc, text))
    rc, text = acct("hold", "--why", "no end")
    check(n + ": the refusal names its repair", "repair: ./acct hold --for 2h" in text, text)
    for argv in (["step", "rm", "steven"], ["step", "rm", "system"], ["step", "rm", "lukas"]):
        rc, text = acct(*argv)
    check(n + ": the last Claude step cannot be removed", rc == AP.REFUSED and any(
        s["use"] == "lukas" for s in on_disk()["steps"]), (rc, text))
    path.write_text("{broken")
    rc, text = acct("next")
    check(n + ": a plan broken by hand is refused at the read, with the repair", rc == AP.REFUSED and "./acct undo" in text, text)
    rc, text = acct("undo")
    check(n + ": and undo restores the last good plan", rc == 0 and acct("next")[0] == 0, text)


def t_two_writers_lose_no_change():
    n = "two_writers_lose_no_change"
    fresh()
    rev = on_disk()["rev"]
    ps = [subprocess.Popen([sys.executable, str(HERE / "account_plan.py"), "step", "add", "w%d" % i, "--use", "lukas",
                            "--leave", str(10 + i), "--for", "1h", "--why", "writer %d" % i],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT) for i in range(8)]
    outs = [p.communicate()[0].decode() for p in ps]
    p = on_disk()
    names = {s["name"] for s in p["steps"]}
    hist = [json.loads(x) for x in (TMP / "plan" / "history.jsonl").read_text().splitlines()]
    check(n + ": 8 writers at once, 8 steps", all("w%d" % i in names for i in range(8)), (sorted(names), outs))
    check(n + ": 8 revisions and 8 history lines", p["rev"] == rev + 8 and len(hist) == 1 + 8
          and sorted(h["rev"] for h in hist) == list(range(rev, rev + 9)), (p["rev"], len(hist)))


WRITES = (["order", "lukas", "system", "steven"], ["order", "system", "lukas", "steven", "--for", "2h", "--line", "steven=9"],
          ["line", "steven", "40"], ["line", "steven", "5", "--until-reset"], ["line", "codex", "10", "--for", "3h"],
          ["step", "add", "night", "--use", "steven", "--leave", "25", "--when", "clock >= 22:00 or clock < 06:00"],
          ["step", "set", "steven", "warn=4", "until=hours_to_reset < 2"], ["step", "move", "lukas", "--first"],
          ["step", "rm", "codex"], ["set", "numbers.switch_cost_pts=7", "numbers.burn_mode.window_h=12"],
          ["switch", "system"], ["pin", "lukas", "--for", "2h"], ["hold", "--for", "30m"])


def t_every_write_has_an_undo():
    n = "every_write_has_an_undo"
    for argv in WRITES:
        fresh()
        before = on_disk()
        rc, text = acct(*argv, "--why", "t")
        lines = text.strip().splitlines()
        rev = on_disk()["rev"]
        ok = rc == 0 and len(lines) <= 3 and lines[-1] == "undo: ./acct undo %d" % rev and on_disk() != before
        rc2, text2 = acct("undo", str(rev))
        after = on_disk()
        after.pop("rev")
        before.pop("rev")
        check("%s: %s" % (n, " ".join(argv)), ok and rc2 == 0 and after == before, (rc, text, rc2, text2))
    fresh()
    acct("hold", "--for", "1h")
    rc, _ = acct("release")
    rc2, text = acct("undo")
    check(n + ": release, and its undo brings the hold back", rc == 0 and rc2 == 0 and on_disk()["holds"], text)


def t_a_write_is_never_refused_for_a_missing_flag():
    n = "a_write_is_never_refused_for_a_missing_flag"
    fresh()
    rc, text = acct("line", "steven", "40")
    h = AP.history()[-1]
    check(n + ": no flag at all: done, and the history says so", rc == 0 and h["why"] == "no reason given", (rc, text, h))
    said = "why not 40? do it"
    rc, _ = acct("line", "steven", "41", "--owner-said", said)
    h = AP.history()[-1]
    check(n + ": his words are kept as typed, a question included, and owed to the ledger",
          rc == 0 and h["owner_said"] == said and h.get("ledger") == "owed", h)
    rc, _ = acct("line", "steven", "42", "--per-ruling", "SOME_RULING")
    check(n + ": a ruling alone is enough", rc == 0 and AP.history()[-1]["per_ruling"] == "SOME_RULING")


def t_a_hold_needs_an_end_and_ends_by_itself():
    n = "a_hold_needs_an_end_and_ends_by_itself"
    fresh(OPEN, rescue_frame())
    rc, text = acct("hold", "--why", "stop the switching")
    check(n + ": no end -> refused, with the repair", rc == AP.REFUSED and "--for 2h" in text, text)
    rc, text = acct("hold", "--for", "1h", "--why", "stop the switching")
    p = on_disk()
    at = AP.stamp(p["holds"][0]["at"])
    d = AP.decide(p, rescue_frame(now=at + 60))
    check(n + ": while it stands the decision is passive, with its why", rc == 0 and d["do"] == "passive"
          and "stop the switching" in d["why"], d)
    d = AP.decide(p, rescue_frame(now=at + 3700))
    check(n + ": after its end the plan acts again with no command", d["do"] == "switch", d)


def t_a_request_is_done_by_the_switchers_log():
    n = "a_request_is_done_by_the_switchers_log"
    rows = {"steven": R(90, 150), "system": R(80, 160), "lukas": R(60, 150)}
    fresh(OPEN, F("lukas", rows))
    acct("switch", "system", "--why", "t")
    p = on_disk()
    at = AP.stamp(p["requests"][0]["at"])
    d = AP.decide(p, F("lukas", rows, runs=RUN, now=at + 60))
    check(n + ": a run is live -> it waits, and no start is refused", d["do"] == "normal" and d["pending"]["to"] == "system", d)
    d = AP.decide(p, F("lukas", rows, runs=None, now=at + 60))
    check(n + ": unreadable runs count as live", d["do"] == "normal", d)
    d = AP.decide(p, F("lukas", rows, now=at + 60))
    check(n + ": no run live -> the switch", d["do"] == "switch" and d["to"] == "system" and not d.get("under"), d)
    log = [{"op": "use", "changed": True, "from": "lukas", "to": "system", "ts": AP.iso(at + 120)},
           {"op": "use", "changed": True, "from": "system", "to": "lukas", "ts": AP.iso(at + 900)}]
    d = AP.decide(p, F("lukas", rows, now=at + 1000, switches=log, hand=True))
    check(n + ": after the log shows that switch, the request causes no second one", d["do"] == "normal"
          and not d.get("pending"), d)
    d = AP.decide(p, F("lukas", rows, now=at + 25 * 3600))
    check(n + ": an ended request causes none", d["do"] == "normal" and not d.get("pending"), d)
    fresh(OPEN, F("lukas", rows, runs=RUN))
    acct("switch", "system", "--now", "--why", "t")
    p = on_disk()
    at = AP.stamp(p["requests"][0]["at"])
    d = AP.decide(p, F("lukas", rows, runs=RUN, now=at + 60))
    v = AP.legacy_view(p, F("lukas", rows, runs=RUN, now=at + 60))
    check(n + ": --now goes with a run live, and with no drain", d["do"] == "switch" and v["pull_drain_max_s"] == 0, (d, v))
    rc, text = acct("switch", "codex")
    check(n + ": a meter account is no switch target", rc == AP.REFUSED, text)


def t_whatif_writes_nothing():
    n = "whatif_writes_nothing"
    fresh(OPEN, rescue_frame(RUN))
    d = TMP / "plan"
    snap = {x.name: x.read_bytes() for x in d.iterdir()}
    rc, text = acct("whatif", "--", "set", "numbers.rescue.drain_h=null")
    check(n + ": the answer has now and then", rc == 0 and "nothing is written" in text and "now:" in text
          and "then:" in text and "SWITCH" in text.split("then:")[0] and "NORMAL" in text.split("then:")[1], text)
    check(n + ": no file changed and none appeared", {x.name: x.read_bytes() for x in d.iterdir()} == snap)
    rc, text = acct("whatif", "--", "line", "lukas", "-3")
    check(n + ": a bad change is refused there too", rc == AP.REFUSED, text)
    rc, text = acct("whatif", "--", "status")
    check(n + ": it takes a write only", rc == AP.REFUSED, text)


def t_the_four_answers_stay_apart():
    n = "the_four_answers_stay_apart"
    rows = {"steven": {"source": "UNMEASURED", "why": "token needs a refresh"}, "system": R(80, 110), "lukas": R(18, 120)}
    codex0 = {**AP.reading(None, NOW), "left": 0.0, "ok": True, "state": "MEASURED", "reset": NOW + 90 * 3600,
              "age_min": 3.0, "last_left": 0.0, "burn_h": 0.2}
    fresh(BASE, F("lukas", rows, codex=codex0))
    rc, text = acct("readings")
    st = next(x for x in text.splitlines() if x.strip().startswith("steven"))
    cx = next(x for x in text.splitlines() if x.strip().startswith("codex"))
    check(n + ": a level that was not read says UNMEASURED and its cause, never a number",
          "UNMEASURED" in st and "token needs a refresh" in st and "%" not in st.split("[")[0], st)
    check(n + ": a measured zero prints 0 and exits 0", rc == 0 and "0% left" in cx, cx)
    rc, text = acct("can-use", "codex")
    check(n + ": can-use on a measured zero answers NO, exit 1", rc == AP.NO and text.startswith("NO"), (rc, text))
    rc, text = acct("can-use", "codex", frame=F("lukas", rows))
    check(n + ": can-use on an unread meter is COULD NOT LOOK, exit 2", rc == AP.COULD_NOT_LOOK and "COULD NOT LOOK" in text, text)
    rc, text = acct("status", frame=F("lukas", {**rows, "lukas": R(18, 120, src="ESTIMATE")}))
    check(n + ": status with the live level unread exits 2", rc == AP.COULD_NOT_LOOK, (rc, text[:200]))
    rc, text = acct("status", frame=F(None, rows, live_why="the switcher did not answer"))
    check(n + ": status with the live account unknown exits 2 and says why", rc == AP.COULD_NOT_LOOK
          and "the switcher did not answer" in text, text[:300])
    rc, text = acct("release")
    check(n + ": nothing to release is NONE, exit 5", rc == AP.NONE and text.startswith("NONE"), (rc, text))
    rc, text = acct("measures", frame={**F("lukas", rows), "series": [], "switches": []})
    check(n + ": measures with no reset and no switch is NONE, exit 5", rc == AP.NONE, (rc, text))
    os.chmod(TMP / "plan", 0o500)
    try:
        rc, text = acct("line", "steven", "40", frame=F("lukas", rows))
    finally:
        os.chmod(TMP / "plan", 0o700)
    check(n + ": a write that broke is FAILED, exit 4", rc == AP.FAILED and text.startswith("FAILED"), (rc, text))
    for x in (TMP / "plan").iterdir():
        x.unlink()
    rc, text = acct("next")
    check(n + ": no plan file is NONE with the repair", rc == AP.NONE and "import-legacy" in text, (rc, text))


def t_every_account_is_listed_as_left():
    n = "every_account_is_listed_as_left"
    codex = {**AP.reading(None, NOW), "left": 99.0, "ok": True, "state": "MEASURED", "reset": NOW + 160 * 3600,
             "age_min": 4.0, "last_left": 99.0, "burn_h": 0.2}
    fresh(BASE, F("lukas", FAR, codex=codex))
    for cmd in ("status", "readings"):
        rc, text = acct(cmd)
        body = text.split("ACCOUNTS (what is LEFT)")[1]
        lines = {a: next((x for x in body.splitlines() if x.strip().startswith(a)), "") for a in
                 ("system", "lukas", "steven", "codex", "jpl-genai")}
        check("%s: %s has a line for each of the five" % (n, cmd), all(lines.values()), lines)
        check("%s: %s says left, a Pacific reset and an age, never used" % (n, cmd), all(
            "% left" in lines[a] and ("PST" in lines[a] or "PDT" in lines[a]) and "min old" in lines[a]
            for a in ("system", "lukas", "steven", "codex")) and "used" not in body, body)
        check("%s: %s says that jpl-genai is not on this machine" % (n, cmd), "not on this machine" in lines["jpl-genai"])
    rc, text = acct("readings", frame=F("lukas", FAR, codex=codex, genai=["failed", "exit 3: no session"]))
    check(n + ": a genai read that failed is UNMEASURED with its cause", "UNMEASURED: exit 3: no session" in text, text)


def t_status_reads_no_slow_source():
    n = "status_reads_no_slow_source"
    import account_live
    import account_usage
    called = []
    saved = (account_usage.read_codex_points, account_usage.read_genai_status, account_usage.read_now, account_usage.poll,
             account_live.read, SP.live_detached_runs, SP.switches, SP.read_markers, SP.load_state)
    account_usage.read_codex_points = lambda: called.append("codex") or {}
    account_usage.read_genai_status = lambda: called.append("genai") or ("absent", None)
    account_usage.poll = lambda *a, **k: called.append("poll")
    account_usage.read_now = lambda now=None: {"accounts": FAR}

    class Ans:
        kind, value = "value", {"live": "lukas"}
    account_live.read = lambda **k: Ans()
    SP.live_detached_runs = lambda: []
    SP.switches, SP.read_markers, SP.load_state = (lambda path=None: []), (lambda: {}), (lambda: {})
    fresh()
    del os.environ["RM_ACCOUNT_PLAN_FRAME"]
    try:
        for cmd in (["status"], ["next"], ["plan"], ["readings"], ["forecast", "--rate", "4"],
                    ["whatif", "--", "line", "steven", "40"], ["hold", "--for", "1m"]):
            rc, text = acct(*cmd)
        check(n + ": seven commands, no Codex reader, no GenAI reader, no poll", called == [], called)
        AP.gather(slow=True)
        check(n + ": only the timed pass reads the slow sources, and keeps them for status", called == ["codex", "genai"]
              and (TMP / "plan" / "frame.json").exists(), called)
    finally:
        os.environ["RM_ACCOUNT_PLAN_FRAME"] = str(TMP / "frame.json")
        (account_usage.read_codex_points, account_usage.read_genai_status, account_usage.read_now, account_usage.poll,
         account_live.read, SP.live_detached_runs, SP.switches, SP.read_markers, SP.load_state) = saved
    big = copy.deepcopy(OPEN)
    for i in range(12):
        big["steps"].insert(0, {"name": "t%d" % i, "use": ("steven", "system", "lukas")[i % 3], "leave": 3 + i,
                                "when": "clock >= %02d:00 and clock < %02d:30 or hours_to_reset < %d" % (i, i + 1, i)})
    f = F("lukas", {"steven": R(90, 30), "system": R(80, 100), "lukas": R(40, 160)}, runs=RUN)
    t0 = time.time()
    AP.decide(big, f)
    AP.forecast_text(big, f)
    dt = time.time() - t0
    check(n + ": a decision and a forecast on 16 steps with conditions take under a second (%.3f s)" % dt, dt < 1.0)
    check(n + ": the code calls no model and runs no subprocess", "import subprocess" not in SRC and "claude -p" not in SRC
          and "anthropic" not in SRC.lower())


def t_the_tool_never_touches_a_credential():
    n = "the_tool_never_touches_a_credential"
    low = SRC.lower()
    for word in ("credential", "token", "oauth", ".claude.json", "password", "secret"):
        body = "\n".join(ln for ln in low.splitlines() if "never" not in ln and "t_the_tool" not in ln)
        check("%s: the code has no `%s`" % (n, word), word not in body)
    check(n + ": it calls no switcher verb itself", "fleet-stop" not in SRC and "armed_call" not in SRC
          and "--confirm" not in SRC and "SP.run(" not in SRC)


# ------------------------------------------------------------------ Burn Mode and the measures
def CX(left, h, burn=0.5, ok=True):
    return {**AP.reading(None, NOW), "left": left if ok else None, "ok": ok, "state": "MEASURED" if ok else "ESTIMATE",
            "reset": NOW + h * 3600, "age_min": 5.0, "last_left": left, "burn_h": burn}


def t_burn_mode_enters_on_measured_allowance_at_risk():
    n = "burn_mode_enters_on_measured_allowance_at_risk"
    b = AP.burn_mode(BASE, F("lukas", FAR, codex=CX(60, 20)))["accounts"]["codex"]
    check(n + ": 60 usable points, 20 h, 0.5 an hour -> on, target 3 an hour, 50 at risk",
          b["state"] == "on" and b["target_burn_pct_h"] == 3.0 and b["at_risk_pts"] == 50.0, b)
    b = AP.burn_mode(BASE, F("lukas", FAR, codex=CX(60, 20, burn=None)))["accounts"]["codex"]
    check(n + ": an unknown burn is unmeasured, never on", b["state"] == "unmeasured", b)
    b = AP.burn_mode(BASE, F("lukas", FAR, codex=CX(60, 20, ok=False)))["accounts"]["codex"]
    check(n + ": an estimated level is unmeasured", b["state"] == "unmeasured", b)
    b = AP.burn_mode(BASE, F("lukas", FAR, codex=CX(60, 100)))["accounts"]["codex"]
    check(n + ": a reset 100 h away is off", b["state"] == "off", b)
    b = AP.burn_mode(BASE, F("lukas", FAR, codex=CX(60, 20, burn=2.9)))["accounts"]["codex"]
    check(n + ": 2 points at risk is under the minimum: off", b["state"] == "off", b)
    bm = AP.burn_mode(BASE, F("lukas", {**FAR, "lukas": R(60, 10)}, burn_h=1.0))
    check(n + ": the live Claude account has it too, on its floor line, and the others do not",
          bm["accounts"]["lukas"]["state"] == "on" and bm["accounts"]["lukas"]["usable_pts"] == 59.0
          and "steven" not in bm["accounts"] and bm["on"] == ["lukas"], bm)


def t_burn_mode_never_counts_under_a_leave_line():
    n = "burn_mode_never_counts_under_a_leave_line"
    p = copy.deepcopy(BASE)
    p["numbers"]["reset_day"]["accounts"] = ["system", "lukas"]
    b = AP.burn_mode(p, F("lukas", FAR, codex=CX(30, 20, burn=0.0)))["accounts"]["codex"]
    check(n + ": codex at 30 with a 25 line: 5 usable, target 0.25 an hour", b["usable_pts"] == 5.0
          and b["target_burn_pct_h"] == 0.25 and b["line"] == 25, b)
    b = AP.burn_mode(p, F("lukas", FAR, codex=CX(20, 20, burn=0.0)))["accounts"]["codex"]
    check(n + ": under its line there is nothing to burn: off", b["state"] == "off" and b["usable_pts"] == 0.0, b)
    q = plan(steven={"when": None})
    b = AP.burn_mode(q, F("steven", {**FAR, "steven": R(90, 10)}, burn_h=1.0))["accounts"]["steven"]
    check(n + ": Steve's account at 90 with a 52 line: 38 usable", b["usable_pts"] == 38.0, b)


def t_burn_mode_does_not_raise_on_a_loaded_machine():
    n = "burn_mode_does_not_raise_on_a_loaded_machine"
    for load, want in ((41.0, False), (5.0, True), (None, False)):
        bm = AP.burn_mode(BASE, F("lukas", FAR, codex=CX(60, 20), load=load))
        check("%s: load %s on 14 cores -> raise_ok %s" % (n, load, want), bm["raise_ok"] is want
              and ("41" in bm["load_why"] if load == 41.0 else True) and bm["accounts"]["codex"]["state"] == "on", bm)


def t_burn_mode_ends_at_the_reset():
    n = "burn_mode_ends_at_the_reset"
    cx = CX(60, 20)
    check(n + ": on before it", AP.burn_mode(BASE, F("lukas", FAR, codex=cx))["on"] == ["codex"])
    late = AP.burn_mode(BASE, F("lukas", FAR, codex={**cx, "left": 100.0, "last_left": 100.0, "reset": NOW + 167 * 3600}))
    check(n + ": the first reading of the new week is off, with no command", late["on"] == []
          and late["accounts"]["codex"]["state"] == "off", late)
    f = F("lukas", {**FAR, "lukas": R(60, 10)}, burn_h=1.0)
    check(n + ": the live account, on before its reset", AP.burn_mode(BASE, f)["on"] == ["lukas"])
    f2 = F("lukas", {**FAR, "lukas": R(60, 10)}, burn_h=1.0, now=NOW + 11 * 3600)
    check(n + ": with a reading from before a reset that has passed it is not on",
          AP.burn_mode(BASE, f2)["accounts"]["lukas"]["state"] != "on", AP.burn_mode(BASE, f2))


def t_the_reset_day_rule_is_plan_data():
    n = "the_reset_day_rule_is_plan_data"
    p = plan(system={"leave": 3})
    f = F("lukas", {"steven": R(90, 10), "system": R(80, 10), "lukas": R(18, 120)}, codex=CX(60, 10))
    check(n + ": codex inside the day: line 0", rule(p, "codex", f)["line"] == 0 and rule(p, "codex", f)["reset_day"])
    check(n + ": a Claude account inside the day: its floor, never 0", rule(p, "system", f)["line"] == 1)
    check(n + ": outside the day: its own line", rule(p, "system", F("lukas", FAR, codex=CX(60, 100)))["line"] == 3
          and rule(p, "codex", F("lukas", FAR, codex=CX(60, 100)))["line"] == 25)
    q = plan(steven={"when": None})
    check(n + ": Steve's account is not in the list and keeps 52", rule(q, "steven", f)["line"] == 52)
    fresh(p, f)
    rc, _ = acct("set", "numbers.reset_day.hours=0")
    check(n + ": the hours are a number of the plan: 0 turns the rule off", rc == 0 and rule(on_disk(), "codex", f)["line"] == 25)
    rc, text = acct("can-use", "codex", frame=F("lukas", FAR, codex=CX(20, 10)))
    fresh(p, f)
    rc2, text2 = acct("can-use", "codex", frame=F("lukas", FAR, codex=CX(20, 10)))
    check(n + ": can-use follows it: 20% left is NO without the rule and yes on the reset day", rc == AP.NO and rc2 == 0
          and "reset day" in text2, (text, text2))


def t_measures_count_erased_points_and_switches():
    n = "measures_count_erased_points_and_switches"
    r1, r2, r3 = NOW, NOW + AP.WEEK, NOW + 2 * AP.WEEK

    def row(a, t, used, rs):
        return {"account": a, "source": "MEASURED", "measured_at": AP.iso(t), "week_pct_used": used, "week_resets_at": AP.iso(rs)}
    rows = [row("lukas", r1 - 7200, 70, r1), row("lukas", r1 - 600, 80, r1 + 60), row("lukas", r1 + 600, 0, r2),
            row("system", r1 - 10 * 3600, 50, r1), row("system", r1 + 600, 1, r2),
            row("steven", r1 - 600, 30, r1), row("steven", r1 + 900, 2, r2),
            {**row("lukas", r1 - 300, 99, r1), "source": "ESTIMATE"}]
    sws = [{"ts": AP.iso(r1 - 5000), "from": "system", "to": "lukas"}, {"ts": AP.iso(r1 + 5000), "from": "lukas", "to": "steven"}]
    m = AP.measures(rows, sws, lambda a, t: {"lukas": 1, "system": 1, "steven": 52}[a])
    w = m[AP.week_of(r1)]
    check(n + ": 20% left at the reset, line 1 -> 19 points erased", w["erased"]["lukas"] == 19.0
          and w["left_at_reset"]["lukas"] == 20.0, w)
    check(n + ": 70% left on a 52 line -> 18 erased, not 70", w["erased"]["steven"] == 18.0, w)
    check(n + ": no reading inside 6 h before the reset is UNMEASURED, never 0",
          str(w["erased"]["system"]).startswith("UNMEASURED"), w)
    check(n + ": both switches of the week are counted", w["switches"] == 2, w)
    check(n + ": no reading at all is an empty answer, not zeros", AP.measures([], [], lambda a, t: 1) == {})


# ------------------------------------------------------------------ the old actuator, shadow and replay
class Fake:
    """The machine: a switcher that records its calls, live runs, the order channel, and a clock that only sleep moves."""

    def __init__(self, live="system", runs=RUN):
        self.live, self.runs, self.sent, self.t = live, list(runs), [], NOW
        for k in list(SP.read_markers()):
            (SP.OUT / "markers" / f"{k}.json").unlink()
        SP.OUT.mkdir(parents=True, exist_ok=True)
        for f in ("notice.json", "state.json", "log.jsonl", "HOLD"):
            (SP.OUT / f).unlink(missing_ok=True)
        self.calls = TMP / "calls.txt"
        self.calls.write_text("")
        sw = TMP / "claude-account"
        sw.write_text("#!/bin/sh\necho \"$@\" >> %s\n[ \"$1\" = use ] && echo \"$2\" > %s\nif [ \"$1\" = \"--json\" ]; then "
                      "echo '{\"live\": \"'$(cat %s)'\", \"machine\": \"testbox\", \"armed\": true}'; fi\nexit 0\n"
                      % (self.calls, TMP / "live.txt", TMP / "live.txt"))
        sw.chmod(sw.stat().st_mode | stat.S_IEXEC)
        (TMP / "live.txt").write_text(live)
        self.restore = SP.CA, SP.clock, SP.sleep
        SP.CA, SP.clock, SP.sleep = str(sw), (lambda: self.t), self.sleep

    def close(self):
        SP.CA, SP.clock, SP.sleep = self.restore

    def store_runs(self):
        return list(self.runs)

    def send(self, units, mode, text, deadline=None):
        self.sent.append({"units": units, "mode": mode, "text": text})
        return "ct_%d" % len(self.sent), None

    def withdraw(self, acts, why):
        return len(acts), None

    def saved(self, unit, since):
        return "ended by itself before the switch"

    def sleep(self, s):
        self.t += s

    def go(self, meter, shadow=False, **kw):
        seams = {"now": self.t, "meter_fn": meter if callable(meter) else (lambda: meter), "poll_fn": lambda: None,
                 "runs_fn": lambda: list(self.runs), "burn_fn": lambda *a: {"rate": 0.05, "stale": False, "age_s": 0},
                 "orders": self, "passes": 1, **kw}
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = AP.tick(shadow=shadow, seams=seams)
        return rc, buf.getvalue()

    def acts(self):
        return [ln.split()[0] for ln in self.calls.read_text().splitlines() if ln.split() and ln.split()[0] != "--json"]

    def notice(self):
        return json.loads((SP.OUT / "notice.json").read_text())


def fake(live, runs=RUN):
    return Fake(live, runs)


def t_tick_drives_the_old_actuator():
    n = "tick_drives_the_old_actuator"
    rows = {"steven": R(90, 100), "system": R(2, 110), "lukas": R(60, 120)}
    fresh()
    m = fake("system", runs=[])
    try:
        m.go(rows)
        check(n + ": finished, no run live -> arm-free `use lukas` through the old pass", m.acts() == ["use"]
              and (TMP / "live.txt").read_text().strip() == "lukas", m.acts())
        mk = SP.read_markers()
        check(n + ": the old pass wrote its act record", any(v.get("phase") == "done" and v.get("to") == "lukas"
                                                             for v in mk.values()), mk)
    finally:
        m.close()
    m = fake("system", runs=RUN)
    try:
        m.go(rows)
        nt = m.notice()
        check(n + ": at the warning line with a run live: the old save order, the old notice, no switch yet",
              m.acts() == [] and nt["state"] == "soft" and nt["account_end"] and m.sent and m.sent[0]["mode"] == "at_easy_spot", (m.acts(), nt))
        m.runs = []
        m.t += 60
        m.go(rows)
        check(n + ": the run ended -> the switch goes", m.acts() == ["use"], m.acts())
    finally:
        m.close()
    m = fake("lukas", runs=RUN)
    try:
        m.go({"steven": R(90, 100), "system": R(80, 110), "lukas": R(40, 120)})
        check(n + ": unfinished -> no act, and a notice that refuses nothing", m.acts() == [] and m.notice()["state"] == "none",
              (m.acts(), m.notice()))
        log = [json.loads(x) for x in (TMP / "plan" / "log.jsonl").read_text().splitlines()]
        check(n + ": the pass is in the tool's log with its reason and the count of live runs",
              log and log[-1]["do"] == "normal" and log[-1]["runs"] == 1 and "it stays" in log[-1]["why"], log[-1:])
        check(n + ": the published decision is rewritten", json.loads((TMP / "plan" / "decision.json").read_text())["do"] == "normal")
    finally:
        m.close()


def t_shadow_acts_on_nothing():
    n = "shadow_acts_on_nothing"
    fresh()
    m = fake("system", runs=[])
    try:
        rows = {"steven": R(90, 100), "system": R(2, 110), "lukas": R(60, 120)}
        f = F("system", rows, runs=[])
        rc, text = m.go(rows, shadow=True, frame=f)
        rec = json.loads(text.strip().splitlines()[-1])
        check(n + ": a switch is due, and shadow calls no switcher verb", m.acts() == [] and rec["new"]["do"] == "switch", (m.acts(), rec))
        check(n + ": no notice and no marker", not (SP.OUT / "notice.json").exists() and not SP.read_markers())
        check(n + ": both picks are logged with whether they agree", "old" in rec and "agree" in rec
              and rec["old"]["to"] == rec["new"]["to"] == "lukas" and rec["agree"] is True and rc == 0, rec)
        bm = json.loads((TMP / "plan" / "burn_mode.json").read_text())
        dj = json.loads((TMP / "plan" / "decision.json").read_text())
        check(n + ": it publishes Burn Mode and its decision, marked shadow", "accounts" in bm and dj["shadow"] is True)
        f2 = F("lukas", {"steven": R(90, 20), "system": R(80, 110), "lukas": R(40, 120)}, runs=RUN)
        (TMP / "live.txt").write_text("lukas")
        rc, text = m.go(f2["rows"], shadow=True, frame=f2)
        rec = json.loads(text.strip().splitlines()[-1])
        check(n + ": where the old engine would leave lukas for the order, shadow says disagree, exit 1",
              rec["agree"] is False and rc == AP.NO and rec["old"]["to"] == "system" and rec["new"]["do"] == "normal", rec)
    finally:
        m.close()


def t_a_hold_makes_the_pass_passive():
    n = "a_hold_makes_the_pass_passive"
    rows = {"steven": R(90, 100), "system": R(2, 110), "lukas": R(60, 120)}
    fresh()
    acct("hold", "--for", "1h", "--why", "t")
    m = fake("system", runs=[])
    try:
        rc, text = m.go(rows)
        check(n + ": a plan hold: no switcher call at all", m.calls.read_text() == "" and "PASSIVE" in text, (m.calls.read_text(), text))
        acct("release")
        (SP.OUT / "HOLD").write_text("by hand")
        m.go(rows)
        check(n + ": a hand-made HOLD file is still obeyed", m.acts() == [], m.acts())
        (SP.OUT / "HOLD").unlink()
        m.go(rows)
        check(n + ": with neither, the pass acts", m.acts() == ["use"], m.acts())
    finally:
        m.close()


def t_shadow_drain_is_not_the_plan_tools():
    n = "shadow_drain_is_not_the_plan_tools"
    for word in ("def drained", "def warn_step", "def emergency_step", "def send_orders", "def armed_call", "systemctl",
                 "os.kill", "SIGTERM", "def pause_s", "def write_notice"):
        check("%s: account_plan.py has no `%s`" % (n, word), word not in SRC)
    check(n + ": it calls the old drain", "SP.drained(" in SRC and "SP.check(" in SRC)


def t_replay_names_each_difference():
    n = "replay_names_each_difference"
    same = [({"do": "normal"}, {"do": "normal"}), ({"do": "switch", "to": "lukas"}, {"do": "switch", "to": "lukas"}),
            ({"do": "stop"}, {"do": "stop"}), ({"do": "soft"}, {"do": "soft"})]
    check(n + ": the same decision has no cause", all(RP.classify(o, x) == "" for o, x in same))
    cases = [({"do": "drain", "to": "steven", "pct_left": 18, "line": 1}, {"do": "normal", "line": 1}, "STAY"),
             ({"do": "soft", "why": "lukas at 4% is within 2 of its 2% line"}, {"do": "normal"}, "NO_REFUSAL_ABOVE_THE_WARNING"),
             ({"do": "normal"}, {"do": "switch", "to": "steven", "under": False}, "RESCUE"),
             ({"do": "switch", "to": "system"}, {"do": "switch", "to": "steven", "under": True}, "NEXT_BY_WEEK_AHEAD"),
             ({"do": "normal", "line": 30}, {"do": "normal", "line": 52}, "PLAN_DATA"),
             ({"do": "hold", "why": "transition x already done: never repeated"}, {"do": "switch", "to": "steven", "under": True}, "MARKER"),
             ({"do": "normal"}, {"do": "soft", "pct_left": 2.0, "why": "at its warning line"}, "WARNING_LINE")]
    for o, x, want in cases:
        got = RP.classify(o, x)
        check("%s: %s" % (n, want), got == want and got in RP.CAUSES, got)
    got = RP.classify({"do": "switch", "to": "system", "pct_left": 1, "line": 1}, {"do": "weird"})
    check(n + ": a difference that fits no cause is UNEXPLAINED, by that word", got == "UNEXPLAINED", got)
    ser = RP.Series([{"account": "lukas", "ts": AP.iso(NOW - 600), "measured_at": AP.iso(NOW - 600), "source": "MEASURED",
                      "week_pct_used": 80.0, "week_resets_at": AP.iso(NOW + 9 * 86400 / 9 * 5)},
                     {"account": "steven", "ts": AP.iso(NOW - 600), "measured_at": AP.iso(NOW - 600), "source": "MEASURED",
                      "week_pct_used": 3.0, "week_resets_at": AP.iso(NOW + 86400)}])
    legacy = {**LEGACY, "order": ["steven", "lukas"], "accounts": {"steven": {"leave_pct_left": 5}, "lukas": {}}}
    old_log = [{"at": AP.iso(NOW), "do": "drain", "live": "lukas", "to": "steven", "pct_left": 20.0, "line": 1},
               {"at": AP.iso(NOW + 300), "do": "normal", "live": "lukas", "pct_left": 20.0, "line": 1},
               {"at": AP.iso(NOW + 400), "do": "passive", "why": "HOLD"}]
    cnt, counts, _shown, bad, eps = RP.passes(ser, old_log, [], [(0, legacy)], legacy, SEED, NOW - 60, NOW + 900)
    check(n + ": two passes compared (a passive one is skipped), one STAY, none unexplained",
          cnt == 2 and counts == {"STAY": 1} and bad == [] and len(eps) == 1, (cnt, counts, bad))


# ------------------------------------------------------------------ the census: each row is one command
def one(argv, p=None, frame=None):
    fresh(p, frame)
    rc, text = acct(*argv)
    return rc, text, on_disk()


def t_census_lent_account_window_and_leave_line():
    n = "census_lent_account_window_and_leave_line"
    rc, text, p = one(["step", "set", "steven", "leave=50", "when=hours_since_reset <= 24", "--owner-said",
                       "Dispatcher can use Steve up to 50% after a fresh reset only"])
    inside = F("lukas", {"steven": R(90, 150), "system": R(80, 110), "lukas": R(2, 120)}, burn_h=None)
    outside = F("lukas", {"steven": R(90, 100), "system": R(80, 110), "lukas": R(2, 120)}, burn_h=None)
    check(n, rc == 0 and rule(p, "steven", inside)["line"] == 50 and rule(p, "steven", outside) is None
          and AP.decide(p, inside)["to"] == "steven" and AP.decide(p, outside)["to"] == "system", text)


def t_census_fixed_priority_order():
    n = "census_fixed_priority_order"
    rows = {"steven": R(90, 150), "system": R(80, 110), "lukas": R(2, 120)}
    rc, text, p = one(["order", "system", "steven", "lukas", "--why", "t"], plan(steven={"when": None}), F("lukas", rows, burn_h=None))
    check(n, rc == 0 and [s["use"] for s in p["steps"]][:3] == ["system", "steven", "lukas"]
          and AP.decide(p, F("lukas", rows, burn_h=None))["to"] == "system", text)


def t_census_set_floor_and_leave_line():
    n = "census_set_floor_and_leave_line"
    rc, text, p = one(["set", "numbers.last_account_floor_pct=3", "steps.steven.leave=45", "--by-card", "Floor -> 3; Steven -> 45"])
    check(n, rc == 0 and p["numbers"]["last_account_floor_pct"] == 3 and p["steps"][AP.find_step(p, "steven")]["leave"] == 45
          and AP.history()[-1]["by_card"], text)


def t_census_hold_with_why_and_end():
    n = "census_hold_with_why_and_end"
    rc, text, p = one(["hold", "--for", "2h", "--owner-said", "STOP KILLING THESE WINDOWS NOW"])
    h = p["holds"][0]
    check(n, rc == 0 and h["why"] == "STOP KILLING THESE WINDOWS NOW" and AP.stamp(h["ends"]) - AP.stamp(h["at"]) == 7200
          and AP.history()[-1]["by"], (text, h))


def t_census_one_week_allowance_ends_at_reset():
    n = "census_one_week_allowance_ends_at_reset"
    f = F("lukas", {"steven": R(60, 30), "system": R(80, 110), "lukas": R(2, 120)}, burn_h=None)
    rc, text, p = one(["line", "steven", "20", "--until-reset", "--owner-said", "He has authorized using another 20%"], frame=f)
    at = AP.stamp(p["steps"][0]["from"])
    live = F("lukas", {"steven": R(60, 30, now=at), "system": R(80, 110), "lukas": R(2, 120)}, burn_h=None, now=at + 60)
    after = F("lukas", {"steven": R(100, 30 + 168 - 1, now=at), "system": R(80, 110), "lukas": R(2, 120)}, burn_h=None,
              now=at + 31 * 3600)
    check(n + ": this week the line is 20", rc == 0 and rule(p, "steven", live)["line"] == 20, (text, rule(p, "steven", live)))
    check(n + ": after his reset the 52 line and the window stand again, with no command",
          rule(p, "steven", after)["line"] == 52, rule(p, "steven", after))


def t_census_leave_line_relative_to_entry_level():
    n = "census_leave_line_relative_to_entry_level"
    f = F("steven", {"steven": R(70, 30), "system": R(80, 110), "lukas": R(2, 120)}, entry={"steven": 88.0})
    rc, text, p = one(["line", "steven", "entry-50", "--until-reset", "--owner-said", "use up to 50% lower than where it is now"], frame=f)
    at = AP.stamp(p["steps"][0]["from"])
    f = {**f, "now": at + 60, "rows": {**f["rows"], "steven": R(70, 30, now=at)}}
    check(n + ": 50 points under the level at switch-in (88) is 38", rc == 0 and rule(p, "steven", f)["line"] == 38, rule(p, "steven", f))
    check(n + ": an unknown level at switch-in gives no permission: the standing line", rule(p, "steven", {**f, "entry": {}}) is None
          or rule(p, "steven", {**f, "entry": {}})["line"] == 52)


def t_census_pin_account_now_plan_does_not_fight():
    n = "census_pin_account_now_plan_does_not_fight"
    rc, text, p = one(["pin", "--owner-said", "you know you're on Lukas account now, right? And that's how it should be."],
                      OPEN, rescue_frame())
    at = AP.stamp(p["pins"][0]["at"])
    d = AP.decide(p, rescue_frame(now=at + 60))
    check(n, rc == 0 and p["pins"][0]["account"] == "lukas" and d["do"] == "normal" and "pinned" in d["why"], (text, d))


def t_census_temporary_order_and_line_until_reset():
    n = "census_temporary_order_and_line_until_reset"
    f = F("system", {"steven": R(52, 30), "system": R(2, 110), "lukas": R(60, 120)}, burn_h=None)
    rc, text, p = one(["order", "system", "steven", "lukas", "--until-reset", "steven", "--line", "steven=35",
                       "--owner-said", "Use this account, then switch to Steve"], frame=f)
    at = AP.stamp(p["steps"][0]["from"])
    f = F("system", {"steven": R(52, 30, now=at), "system": R(2, 110, now=at), "lukas": R(60, 120, now=at)}, burn_h=None, now=at + 60)
    d = AP.decide(p, f)
    check(n + ": Steve is next, down to 35, outside his window", rc == 0 and d["to"] == "steven" and rule(p, "steven", f)["line"] == 35, (text, d))
    later = F("system", {"steven": R(100, 30 + 167, now=at), "system": R(2, 110, now=at), "lukas": R(60, 120, now=at)},
              burn_h=None, now=at + 31 * 3600)
    check(n + ": after his reset the standing order and line are back", rule(p, "steven", later)["line"] == 52
          and AP.order_now(p, {a: rule(p, a, later) for a in ("steven", "system", "lukas")})[0] == "steven", rule(p, "steven", later))


def t_census_line_by_time_of_day():
    n = "census_line_by_time_of_day"
    rc, text, p = one(["step", "add", "steven-overnight", "--use", "steven", "--leave", "25", "--when",
                       "clock >= 22:00 or clock < 06:00", "--until-reset", "--owner-said", "Steven keeps 25% overnight"],
                      plan(steven={"when": None, "leave": 5}))
    night, day = AP.stamp("2026-11-24T23:30:00-08:00"), AP.stamp("2026-11-25T10:00:00-08:00")

    def at_(t):
        return rule(p, "steven", F("lukas", {"steven": R(60, 60), "system": R(80, 110), "lukas": R(40, 120)}, now=t))
    check(n + ": at 11:30 PM Pacific the line is 25", rc == 0 and at_(night)["line"] == 25, (text, at_(night)))
    check(n + ": at 10 AM Pacific it is 5", at_(day)["line"] == 5, at_(day))


def t_census_switch_now_when_no_run_is_live():
    n = "census_switch_now_when_no_run_is_live"
    rows = {"steven": R(55, 150), "system": R(80, 110), "lukas": R(40, 120)}
    rc, text, p = one(["switch", "system", "--owner-said", "please switch to the.mandrake.system. Don't lose work. When you can"],
                      plan(steven={"when": None}), F("steven", rows, runs=RUN))
    at = AP.stamp(p["requests"][0]["at"])
    busy, idle = AP.decide(p, F("steven", rows, runs=RUN, now=at + 60)), AP.decide(p, F("steven", rows, now=at + 60))
    check(n + ": with runs live it waits and refuses nothing; with none it goes", rc == 0 and busy["do"] == "normal"
          and idle["do"] == "switch" and idle["to"] == "system", (text, busy, idle))
    check(n + ": no leave line was moved to force it", p["steps"] == plan(steven={"when": None})["steps"])


def t_census_use_until_pct_then_next():
    n = "census_use_until_pct_then_next"
    rc, text, p = one(["line", "system", "4", "--owner-said", "Switch to Lukas when you get to 4% on the.mandrake.system account."])
    rows = {"steven": R(90, 100), "system": R(6, 110), "lukas": R(60, 120)}
    a = AP.decide(p, F("system", rows, burn_h=None))
    b = AP.decide(p, F("system", {**rows, "system": R(4, 110)}, burn_h=None))
    check(n, rc == 0 and a["do"] == "normal" and b["do"] == "switch" and b["to"] == "lukas", (text, a, b))


def t_census_reorder_and_lower_line_until_reset():
    n = "census_reorder_and_lower_line_until_reset"
    rc, text, p = one(["order", "system", "steven", "lukas", "--until-reset", "steven", "--line", "steven=3", "--line", "system=3",
                       "--owner-said", "we do NOT switch to lukas.mandrake next, we switch back to Steven"])
    names = [s["name"] for s in p["steps"]][:3]
    at = AP.stamp(p["steps"][0]["from"])
    f = F("system", {"steven": R(97, 100, now=at), "system": R(3, 110, now=at), "lukas": R(60, 120, now=at)}, burn_h=None, now=at + 60)
    d = AP.decide(p, f)
    check(n + ": one command makes the order and both lines, together", rc == 0 and len(names) == 3
          and rule(p, "steven", f)["line"] == 3 and rule(p, "system", f)["line"] == 3 and d["to"] == "steven", (text, d))
    check(n + ": one history line, one undo", len(AP.history()) == 2 and "undo: ./acct undo" in text)


def t_census_no_rule_lives_in_prose():
    n = "census_no_rule_lives_in_prose"
    fresh()
    rc, text = acct("plan")
    check(n + ": the plan prints the evening share as a number (0: run to the line)", rc == 0 and '"evening_share_pct": 0' in text, text[-600:])
    rc, _t, p = one(["set", "numbers.evening_share_pct=10", "--by-card", "Keep a share for his evenings? -> 10"])
    check(n + ": and one command changes what the decision does with it",
          rule(p, "lukas", F("lukas", FAR))["line"] == 11 and rule(p, "codex", F("lukas", FAR))["line"] == 25)


def t_census_set_warn_and_emergency_numbers():
    n = "census_set_warn_and_emergency_numbers"
    rc, text, p = one(["set", "numbers.account_end.warn_pct=4", "numbers.account_end.warn_fast_pct=5", "numbers.account_end.pause_max_s=120",
                       "--owner-said", "At 4% no new work is started"])
    d = AP.decide(p, F("lukas", {**FAR, "lukas": R(4, 120)}, runs=RUN))
    check(n, rc == 0 and d["warn_line"] == 4 and d["do"] == "soft" and AP.legacy_view(p, F("lukas", FAR))["account_end"]["pause_max_s"] == 120, (text, d))


def t_census_refill_is_seen_from_the_meter_no_marker():
    n = "census_refill_is_seen_from_the_meter_no_marker"
    marker = {"use_steven_to_system_20261125": {"phase": "done", "under": True, "from": "steven", "to": "system",
                                                "at": "2026-11-21T17:45:00-08:00", "line": 5}}
    d = AP.decide(OPEN, F("lukas", {"steven": R(97, 24), "system": R(3, 22), "lukas": R(2, 25)}, markers=marker))
    check(n + ": 97% left and the 11-21 marker present: Steve's account is the target, with no command",
          d["do"] == "switch" and d["to"] == "steven", d)


def t_census_codex_leave_line_in_the_same_plan():
    n = "census_codex_leave_line_in_the_same_plan"
    f = F("lukas", FAR, codex=CX(28, 100))
    rc, text, p = one(["line", "codex", "30", "--owner-said", "preserve 30% for personal use"], frame=f)
    rc1, t1 = acct("can-use", "codex")
    acct("line", "codex", "25")
    rc2, t2 = acct("can-use", "codex")
    check(n + ": the line is a step of the same file, and can-use answers from it", rc == 0 and rc1 == AP.NO and rc2 == 0, (t1, t2))
    rc3, t3 = acct("status")
    check(n + ": codex is in the same status", "codex" in t3 and "28% left" in t3 and "line 25%" in t3, t3)


def t_status_shows_pool_pace_not_sets_it():
    n = "status_shows_pool_pace_not_sets_it"
    fresh(BASE, F("lukas", {**FAR, "lukas": R(60, 10)}, burn_h=1.0))
    rc, text = acct("status")
    check(n + ": status shows the measured burn and the target", "points an hour" in text and "BURN MODE lukas: ON" in text, text)
    check(n + ": the code names no allocator write", "slot_allocator" not in SRC)


# ------------------------------------------------------------------ the faults of 2026-11-24
def t_fault_stale_marker_kept_a_refilled_account_out():
    t_census_refill_is_seen_from_the_meter_no_marker()
    d = AP.decide(OPEN, F("lukas", {"steven": R(97, 24), "system": R(3, 22), "lukas": R(2, 25)}))
    check("fault_stale_marker_kept_a_refilled_account_out", d["to"] == "steven", d)


def t_fault_forecast_disagreed_with_the_pick():
    n = "fault_forecast_disagreed_with_the_pick"
    marker = {"use_steven_to_system_20261125": {"phase": "done", "under": True, "from": "steven", "to": "system",
                                                "at": "2026-11-21T17:45:00-08:00", "line": 5}}
    f = F("lukas", {"steven": R(97, 24), "system": R(3, 22), "lukas": R(2, 25)}, markers=marker)
    d, w = AP.decide(OPEN, f), AP.week_ahead(OPEN, f)
    first = next(e["to"] for e in w["events"] if e["kind"] == "switch")
    check(n, d["to"] == first == "steven", (d["to"], first))


def t_fault_preference_switch_drained_at_eighteen_percent():
    n = "fault_preference_switch_drained_at_eighteen_percent"
    rows = {"steven": R(97, 24), "system": R(3, 22), "lukas": R(18, 25)}
    p = plan(["steven", "system", "lukas"], steven={"leave": 5, "when": None})
    d = AP.decide(p, F("lukas", rows, runs=RUN * 5))
    check(n + ": lukas at 18%, steven first in the order at 97%, runs live: it stays", d["do"] == "normal" and d["to"] is None, d)
    fresh(p)
    m = fake("lukas", runs=RUN * 5)
    try:
        m.go(rows)
        log = [json.loads(x) for x in (SP.OUT / "log.jsonl").read_text().splitlines()]
        check(n + ": the pass writes a notice that refuses no start, drains nothing and calls no switcher verb",
              m.acts() == [] and m.notice()["state"] == "none" and not any(r.get("do") == "drain" for r in log), (m.acts(), m.notice()))
    finally:
        m.close()


def t_fault_plan_change_needed_edit_publish_pull():
    n = "fault_plan_change_needed_edit_publish_pull"
    rows = {"steven": R(90, 150), "system": R(80, 110), "lukas": R(2, 120)}
    fresh(plan(steven={"when": None}), F("lukas", rows, burn_h=None))
    t0 = time.time()
    rc, text = acct("order", "system", "lukas", "steven", "--owner-said", "use up Lukas first", cwd=str(TMP))
    dt = time.time() - t0
    rc2, nxt = acct("next", cwd="/")
    check(n + ": one command from one folder, and a process in another follows it (%.2f s)" % dt,
          rc == 0 and rc2 == 0 and "Next: system" in nxt and dt < 3, (text, nxt))
    check(n + ": the plan file is outside the repository", str(AP.plan_dir()).startswith(str(TMP))
          and ".local/state/rimmandrake/account_plan" in SRC)


def t_fault_hand_hold_six_seconds_before_a_pass():
    n = "fault_hand_hold_six_seconds_before_a_pass"
    rows = {"steven": R(90, 100), "system": R(2, 110), "lukas": R(60, 120)}
    fresh(BASE, F("system", rows))
    t0 = time.time()
    rc, text = acct("whatif", "--", "hold", "--for", "1h", cwd="/tmp")
    dt = time.time() - t0
    check(n + ": the what-if of a hold answers in under a second (%.2f s) and shows the pass going passive" % dt,
          rc == 0 and dt < 1.5 and "PASSIVE" in text.split("then:")[1], text)
    m = fake("system", runs=[])
    calls = {"n": 0}

    def meter():
        calls["n"] += 1
        if calls["n"] == 3:      # the pass has decided the switch; the hold lands before the switcher is called
            AP.commit(lambda p: {**p, "holds": [{"id": "H", "at": AP.iso(NOW - 5), "ends": AP.iso(NOW + 3600), "why": "t"}]},
                      {"why": "t"})
        return rows
    try:
        m.go(meter)
        check(n + ": a hold written while the pass runs is seen before the pass acts", "use" not in m.acts() and calls["n"] >= 3,
              (m.acts(), calls))
    finally:
        m.close()


def t_fault_stop_and_undo_crossed():
    n = "fault_stop_and_undo_crossed"
    rows = {"steven": R(90, 150), "system": R(80, 160), "lukas": R(60, 150)}
    fresh(OPEN, F("lukas", rows))
    rc, text = acct("switch", "system", "--why", "t")
    rev = on_disk()["rev"]
    rc2, text2 = acct("undo", str(rev))
    p = on_disk()
    d = AP.decide(p, F("lukas", rows, now=NOW + 60))
    hist = AP.history()
    check(n + ": the request and its undo leave one plan with no request, and one history line each",
          rc == 0 and rc2 == 0 and p["requests"] == [] and len(hist) == 3 and hist[-1]["undoes"] == rev, (text, text2))
    check(n + ": no act follows the withdrawn request", d["do"] == "normal" and not d.get("pending"), d)


def main():
    for t in (t_live_account_stays_until_its_own_line, t_order_only_answers_which_account_is_next,
              t_no_start_is_refused_for_a_preference, t_a_rescue_switch_needs_points_worth_a_switch,
              t_a_rescue_switch_waits_for_no_live_run, t_an_unknown_burn_never_causes_a_switch,
              t_a_hand_switch_is_respected, t_the_reason_is_one_checkable_line, t_the_forecast_is_the_pick,
              t_no_marker_decides, t_an_account_left_at_its_line_is_no_target, t_a_refilled_account_is_a_target_at_once,
              t_unknown_never_gives_permission, t_the_last_account_waits_at_its_wait_floor,
              t_one_file_binds_at_the_next_read, t_a_bad_write_keeps_the_old_plan, t_two_writers_lose_no_change,
              t_every_write_has_an_undo, t_a_write_is_never_refused_for_a_missing_flag,
              t_a_hold_needs_an_end_and_ends_by_itself, t_a_request_is_done_by_the_switchers_log, t_whatif_writes_nothing,
              t_the_four_answers_stay_apart, t_every_account_is_listed_as_left, t_status_reads_no_slow_source,
              t_the_tool_never_touches_a_credential, t_burn_mode_enters_on_measured_allowance_at_risk,
              t_burn_mode_never_counts_under_a_leave_line, t_burn_mode_does_not_raise_on_a_loaded_machine,
              t_burn_mode_ends_at_the_reset, t_the_reset_day_rule_is_plan_data, t_measures_count_erased_points_and_switches,
              t_tick_drives_the_old_actuator, t_shadow_acts_on_nothing, t_a_hold_makes_the_pass_passive,
              t_shadow_drain_is_not_the_plan_tools, t_replay_names_each_difference,
              t_census_lent_account_window_and_leave_line, t_census_fixed_priority_order, t_census_set_floor_and_leave_line,
              t_census_hold_with_why_and_end, t_census_one_week_allowance_ends_at_reset,
              t_census_leave_line_relative_to_entry_level, t_census_pin_account_now_plan_does_not_fight,
              t_census_temporary_order_and_line_until_reset, t_census_line_by_time_of_day,
              t_census_switch_now_when_no_run_is_live, t_census_use_until_pct_then_next,
              t_census_reorder_and_lower_line_until_reset, t_census_no_rule_lives_in_prose,
              t_census_set_warn_and_emergency_numbers, t_census_refill_is_seen_from_the_meter_no_marker,
              t_census_codex_leave_line_in_the_same_plan, t_status_shows_pool_pace_not_sets_it,
              t_fault_stale_marker_kept_a_refilled_account_out, t_fault_forecast_disagreed_with_the_pick,
              t_fault_preference_switch_drained_at_eighteen_percent, t_fault_plan_change_needed_edit_publish_pull,
              t_fault_hand_hold_six_seconds_before_a_pass, t_fault_stop_and_undo_crossed):
        try:
            t()
        except Exception as e:  # noqa: BLE001  a check that broke is a FAIL of its promise, by name
            import traceback
            check(t.__name__[2:] + ": the check itself broke", False, "%s: %s | %s" % (
                type(e).__name__, e, traceback.format_exc().strip().splitlines()[-3:]))
    print("\n%s: %d FAIL" % ("selftest_account_plan", len(FAILS)))
    for f in FAILS:
        print("  FAIL " + f)
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
