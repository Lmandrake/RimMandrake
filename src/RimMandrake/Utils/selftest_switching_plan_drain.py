#!/usr/bin/env python3
"""selftest: an account drains at its soft line; only its hard line stops live runs
(RIMMANDRAKE_LAUNCH_SIX_CONTEXT_KEEPING_CHANGES_FROM_THE_SCAN, report change 3; page
design/specs/2026-11-20-account-drain/boundary.md). Planted meter readings, a fake switcher and scratch dirs only: it
never reads the live meter, the live runs or the real switcher.

    python3 src/RimMandrake/Utils/selftest_switching_plan_drain.py
"""
import json
import os
import stat
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TMP = Path(tempfile.mkdtemp(prefix="selftest_switching_plan_drain_"))
os.environ["RM_SWITCH_PLAN_DIR"] = str(TMP / "out")
os.environ["RM_ACCOUNTS_DIR"] = str(TMP / "accounts")
os.environ.setdefault("RM_UNDER_SELFTEST", "1")
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "rimflow"))
import switching_plan as SP  # noqa: E402

FAILS = []
NOW = 1_800_000_000.0
SHIPPED = json.loads((HERE / "switching_plan.json").read_text())
PLAN = json.loads(json.dumps(SHIPPED))
PLAN["exceptions"] = []          # the standing rules only; the dated exceptions have their own selftest


def check(name, ok, detail=""):
    print(("ok    " if ok else "FAIL  ") + name + ("" if ok or not detail else ": " + str(detail)[:300]))
    if not ok:
        FAILS.append(name)


def R(left, h, src="MEASURED", age=1.0):
    return {"source": src, "week_pct_left": left, "week_pct_used": None if left is None else 100 - left,
            "hours_to_week_reset": h, "week_resets_at": SP.iso(NOW + h * 3600), "stale": False, "age_min": age}


OFF = {"steven": R(90, 100)}     # steven outside his 48 h window: the plan never goes to him


def D(meter, live, runs=(), plan=PLAN, state=None):
    return SP.decide(meter, live, NOW, plan, dict(state or {}), markers={}, polled=True, live_runs=runs)


RUN = ["rm-detached-bench-rimmandrake-some-builder-1795180000"]


def t_a_spent_account_drains_while_runs_live():
    # system, standing: line 1 (switch-away), soft 3, hard 1. lukas has budget. steven: line 52, hard 50.
    d = D({"steven": R(51, 150), "system": R(40, 100), "lukas": R(98, 120)}, "steven", RUN)
    check("steven at 51% (under 52, over its 50 hard line) with a live run: no switch",
          d["do"] == "soft" and d.get("drain") is True, d)
    check("the drain names the run and the hard line", RUN[0] in d["why"] and "50" in d["why"], d.get("why"))
    check("the drain still names where the switch goes", d.get("to") == "system", d)
    # the last account (no target): a stop is due at its line, and it drains too
    plan = dict(PLAN, floors=dict(PLAN["floors"], wait_pct_left=4))
    d = D({**OFF, "system": R(0.5, 100), "lukas": R(3, 120)}, "lukas", RUN, plan=plan)
    check("the last account under its 4% wait line, over its hard line, with a live run: no stop",
          d["do"] == "soft" and d.get("drain") is True, d)


def t_the_hard_line_stops_every_live_run():
    d = D({"steven": R(50, 150), "system": R(40, 100), "lukas": R(98, 120)}, "steven", RUN)
    check("steven at its 50% hard line with a live run: switch", d["do"] == "switch" and d["to"] == "system", d)
    d = D({**OFF, "system": R(1, 100), "lukas": R(98, 120)}, "system", RUN)
    check("system at its 1% hard line with a live run: switch to lukas", d["do"] == "switch" and d["to"] == "lukas", d)
    d = D({**OFF, "system": R(0.5, 100), "lukas": R(1, 120)}, "lukas", RUN)
    check("the last account at its hard line with a live run: stop", d["do"] == "stop", d)
    d = D({**OFF, "system": R(0.8, 100, src="ESTIMATE", age=30), "lukas": R(98, 120)}, "system", RUN)
    check("a blind 0% live account with a live run: switch, no drain", d["do"] == "switch", d)


def t_no_live_run_means_no_wait():
    d = D({"steven": R(51, 150), "system": R(40, 100), "lukas": R(98, 120)}, "steven", [])
    check("steven at 51% and no live run: switch at once", d["do"] == "switch" and d["to"] == "system", d)
    plan = dict(PLAN, floors=dict(PLAN["floors"], wait_pct_left=4))
    d = D({**OFF, "system": R(0.5, 100), "lukas": R(3, 120)}, "lukas", [], plan=plan)
    check("the last account under its line and no live run: stop at once", d["do"] == "stop", d)
    d = D({"steven": R(53, 150), "system": R(40, 100), "lukas": R(98, 120)}, "steven", RUN)
    check("steven at 53% (soft zone, over the line): soft, no new starts, nothing stopped", d["do"] == "soft", d)


def t_unreadable_runs_count_as_live():
    d = D({"steven": R(51, 150), "system": R(40, 100), "lukas": R(98, 120)}, "steven", None)
    check("runs unreadable at 51%: drain, never read as no runs", d["do"] == "soft" and d.get("drain") is True, d)
    check("and the why says UNMEASURED", "UNMEASURED" in d.get("why", ""), d.get("why"))
    d = D({"steven": R(50, 150), "system": R(40, 100), "lukas": R(98, 120)}, "steven", None)
    check("runs unreadable at the hard line: switch", d["do"] == "switch", d)


def t_the_hard_line_keeps_his_lines():
    line = {"steven": 52, "system": 1, "lukas": 2}
    check("steven's hard line is 50", SP.hard_line(PLAN, line, "steven") == 50, SP.hard_line(PLAN, line, "steven"))
    check("system's hard line is 1", SP.hard_line(PLAN, line, "system") == 1)
    check("a 2% wait line's hard line is 1, never 0", SP.hard_line(PLAN, line, "lukas") == 1)
    check("a 0% line is lifted to 1", SP.hard_line(PLAN, {"x": 0}, "x") == 1)


def t_the_floors_never_reach_zero():
    fl = SHIPPED["floors"]
    check("switch-away floor is 1", fl.get("switch_away_pct_left") == 1, fl)
    check("hard floor is 1", fl.get("hard_pct_left") == 1, fl)
    check("drain is 2", fl.get("drain_pct") == 2, fl)
    check("every floor is at least 1", all(fl[k] >= 1 for k in ("switch_away_pct_left", "wait_pct_left",
                                                                  "hard_pct_left")), fl)
    check("steven's leave line is still 52", SHIPPED["accounts"]["steven"]["leave_pct_left"] == 52)
    check("the order is still steven, system, lukas", SHIPPED["order"] == ["steven", "system", "lukas"])
    check("no exception sets a line under 1", all((a.get("leave_pct_left") or 1) >= 1 for e in SHIPPED["exceptions"]
                                                   for a in (e.get("accounts") or {}).values()), SHIPPED["exceptions"])
    check("checkpoint_grace_s is gone; pull_drain_max_s replaces it",
          "checkpoint_grace_s" not in SHIPPED and SHIPPED.get("pull_drain_max_s") == 7200)
    import conductor_acts as CA     # every changed rule carries lost: and undo:, as the plan file requires

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k not in ("from", "until"):      # an exception's times are dates, not rule texts
                    yield from walk(v)
        elif isinstance(o, list):
            for v in o:
                yield from walk(v)
        elif isinstance(o, str) and "2026-11-20" in o:
            yield o

    def unmindful(plan):
        return [t for t in walk(plan) if CA.why_problem(t, mindful=True) is not None]
    texts = list(walk(SHIPPED))
    check("each 2026-11-20 rule text names lost: and undo:", texts and not unmindful(SHIPPED), unmindful(SHIPPED))
    # 2026-11-20 ~4:30 PM: a dated exception from that day (from "2026-11-20T16:45:00-08:00") read as an unmindful rule
    dated = dict(SHIPPED, exceptions=[{"id": "X", "from": "2026-11-20T16:45:00-08:00", "until": "2026-11-27T16:00:00-08:00",
                                       "order": ["system", "steven", "lukas"],
                                       "_why": "[CA] 2026-11-20 the owner said use system up first, then steven; "
                                               "lost: steven's week is spent to its floor; undo: delete this exception"}])
    bare = dict(SHIPPED, _order="[CA] 2026-11-20 system first, the owner said so today")
    check("an exception's from/until dates are no rule text; a 2026-11-20 rule without lost:/undo: is still caught",
          not unmindful(dated) and unmindful(bare) == [bare["_order"]], (unmindful(dated), unmindful(bare)))


def fake_switcher():
    calls = TMP / "calls.txt"
    sw = TMP / "claude-account"
    sw.write_text("#!/bin/sh\necho \"$@\" >> %s\nif [ \"$1\" = \"--json\" ]; then echo '{\"live\": \"'$(cat %s)'\", "
                  "\"machine\": \"testbox\", \"armed\": true}'; fi\nexit 0\n" % (calls, TMP / "live.txt"))
    sw.chmod(sw.stat().st_mode | stat.S_IEXEC)
    SP.CA = str(sw)
    return calls


def t_a_pull_switch_waits_for_live_runs():
    calls = fake_switcher()
    plan = dict(PLAN, accounts=dict(PLAN["accounts"], steven=dict(PLAN["accounts"]["steven"], window_h_after_reset=168)))
    (TMP / "plan.json").write_text(json.dumps(plan))
    SP.PLAN_PATH = TMP / "plan.json"
    meter = {"steven": R(100, 167), "system": R(40, 100), "lukas": R(98, 120)}   # steven's reset pulls the machine
    out = TMP / "out"

    def go(now, runs):
        (TMP / "live.txt").write_text("system")
        calls.write_text("")
        SP.check(dry=False, now=now, meter_fn=lambda: meter, poll_fn=lambda: None, runs_fn=lambda: runs)
        return [ln.split()[0] for ln in calls.read_text().splitlines() if ln.split() and ln.split()[0] != "--json"]

    def last():
        return json.loads((out / "log.jsonl").read_text().splitlines()[-1])
    acts = go(NOW, RUN)
    nt = json.loads((out / "notice.json").read_text())
    check("a pull switch with a live run waits", "use" not in acts and last().get("do") == "drain", (acts, last()))
    check("its notice reads soft with drain true", nt.get("state") == "soft" and nt.get("drain") is True, nt)
    acts = go(NOW + 3600, RUN)
    check("still waiting an hour later, the run still live", "use" not in acts, acts)
    acts = go(NOW + 7300, RUN)
    check("past pull_drain_max_s the switch goes", "use" in acts, acts)
    for k in list(SP.read_markers()):
        (out / "markers" / f"{k}.json").unlink()
    (out / "notice.json").unlink()
    acts = go(NOW + 8000, [])
    check("with no live run the pull switch goes at once", "use" in acts, acts)


def t_a_new_launch_waits_while_the_account_drains():
    import detached_helper as DH
    p = TMP / "out" / "notice.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"state": "soft", "drain": True, "since": SP.iso(NOW - 60), "at": SP.iso(NOW - 30),
                             "account": "steven", "why": "draining"}))
    why = DH.drain_refusal(NOW, {}, None, path=str(p))
    check("a new launch is refused while the account drains", bool(why) and "drain" in why, why)
    check("a continuation of a live run is let through", DH.drain_refusal(NOW, {"continued_from": "rm-x"}, None,
                                                                          path=str(p)) is None)
    check("a resume of a run's session is let through", DH.drain_refusal(NOW, {}, "sess-1", path=str(p)) is None)
    check("a notice 30 min old refuses nothing (the plan's timer stopped)",
          DH.drain_refusal(NOW + 1800, {}, None, path=str(p)) is None)
    p.write_text(json.dumps({"state": "soft", "since": SP.iso(NOW - 60), "at": SP.iso(NOW - 30)}))
    check("a soft notice that is no drain refuses nothing", DH.drain_refusal(NOW, {}, None, path=str(p)) is None)
    p.write_text("{not json")
    check("an unreadable notice refuses nothing", DH.drain_refusal(NOW, {}, None, path=str(p)) is None)


def t_a_new_launch_goes_at_the_soft_line():
    import detached_helper as DH
    p = TMP / "out" / "notice.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    name = "a-new-launch-goes-at-the-soft-line"
    for left in (3, 2):     # system: line 1, soft 3
        for runs in ([], RUN):
            d = D({**OFF, "system": R(left, 100), "lukas": R(98, 120)}, "system", runs)
            check("%s: system at %s%%, %d live run(s), lukas full: soft, no drain, and no switch that a refusal could wait "
                  "for" % (name, left, len(runs)), d["do"] == "soft" and not d.get("drain"), d)
            SP.write_notice(d, NOW)
            check("%s: a new run starts at %s%% with %d live run(s)" % (name, left, len(runs)),
                  DH.drain_refusal(NOW, {}, None, path=str(p)) is None, d)
    d = D({**OFF, "system": R(40, 100), "lukas": R(98, 120)}, "system", RUN)
    SP.write_notice({**d, "do": "soft", "drain": True}, NOW)
    check("%s: the same notice as a drain refuses (the probe can see a refusal)" % name,
          bool(DH.drain_refusal(NOW, {}, None, path=str(p))))


def main():
    for t in (t_a_spent_account_drains_while_runs_live, t_the_hard_line_stops_every_live_run,
              t_no_live_run_means_no_wait, t_unreadable_runs_count_as_live, t_the_hard_line_keeps_his_lines,
              t_the_floors_never_reach_zero, t_a_pull_switch_waits_for_live_runs,
              t_a_new_launch_waits_while_the_account_drains, t_a_new_launch_goes_at_the_soft_line):
        try:
            t()
        except Exception as e:  # noqa: BLE001
            import traceback
            traceback.print_exc()
            check(t.__name__ + " raised", False, "%s: %s" % (type(e).__name__, e))
    print("selftest_switching_plan_drain: %s (%d failed)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
