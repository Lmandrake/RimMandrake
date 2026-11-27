#!/usr/bin/env python3
"""selftest: a switch or a stop that falls due waits for live runs (page design/specs/2026-11-20-account-drain/boundary.md;
how an account ends: selftest_account_end.py). One check per promise, by its name. The decision is the account plan's
(account_plan.decide on the first plan, account_plan.first_plan); the act is account_actuator.check. Planted meter
readings, a fake switcher and scratch dirs only: it never reads the live meter, the live runs or the real switcher.

    python3 src/RimMandrake/Utils/selftest_account_actuator_drain.py
"""
import json
import os
import stat
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TMP = Path(tempfile.mkdtemp(prefix="selftest_account_actuator_drain_"))
os.environ["RM_SWITCH_PLAN_DIR"] = str(TMP / "out")
os.environ["RM_ACCOUNTS_DIR"] = str(TMP / "accounts")
os.environ["RM_ACCOUNT_PLAN_DIR"] = str(TMP / "plan")
os.environ["RM_ACCOUNT_PLAN_SERIES"] = str(TMP / "no-series.jsonl")
os.environ.setdefault("RM_UNDER_SELFTEST", "1")
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "rimflow"))
import account_actuator as ACT  # noqa: E402
import account_plan as AP  # noqa: E402

FAILS = []
NOW = 1_800_000_000.0
PLAN = AP.first_plan()      # steven 52 in the first 48 h after his reset, system 1, lukas 1
RUN = ["rm-detached-bench-rimmandrake-some-builder-1795180000"]
ORD = {"rate": 0.067, "stale": False, "age_s": 0, "span_min": 45, "why": ""}     # an ordinary burn


def check(name, ok, detail=""):
    print(("ok    " if ok else "FAIL  ") + name + ("" if ok or not detail else ": " + str(detail)[:300]))
    if not ok:
        FAILS.append(name)


def R(left, h, src="MEASURED", age=1.0):
    return {"source": src, "week_pct_left": left, "week_pct_used": None if left is None else 100 - left,
            "hours_to_week_reset": h, "week_resets_at": ACT.iso(NOW + h * 3600), "stale": False, "age_min": age}


OFF = {"steven": R(90, 100)}     # steven outside his 48 h window: the plan never goes to him


def D(meter, live, runs=(), burn=ORD):
    f = AP.frame_for_pass(ACT, meter, live, NOW, {}, {}, None, None if runs is None else list(runs), burn, PLAN)
    return AP.decide(PLAN, f, polled=True)


def fake_switcher():
    calls = TMP / "calls.txt"
    calls.write_text("")
    sw = TMP / "claude-account"
    sw.write_text("#!/bin/sh\necho \"$@\" >> %s\n[ \"$1\" = use ] && echo \"$2\" > %s\nif [ \"$1\" = \"--json\" ]; then "
                  "echo '{\"live\": \"'$(cat %s)'\", \"machine\": \"testbox\", \"armed\": true}'; fi\nexit 0\n"
                  % (calls, TMP / "live.txt", TMP / "live.txt"))
    sw.chmod(sw.stat().st_mode | stat.S_IEXEC)
    ACT.CA = str(sw)
    return calls


def t_a_spent_account_drains_while_runs_live():
    n = "a-spent-account-drains-while-runs-live"
    d = D({"steven": R(52, 150), "system": R(40, 100), "lukas": R(98, 120)}, "steven", RUN)
    check(n + ": steven at his 52% line with a live run: no switch, a drain at the line", d["do"] == "soft"
          and d.get("drain") is True and d.get("account_end") is True and RUN[0] in d["why"], d)
    d = D({**OFF, "system": R(2, 100), "lukas": R(98, 120)}, "system", RUN)
    check(n + ": in the warning zone (2%) the runs are warned and keep working: no drain", d["do"] == "normal"
          and d.get("warning") is True and not d.get("drain"), d)


def t_no_live_run_means_no_wait():
    n = "no-live-run-means-no-wait"
    d = D({**OFF, "system": R(1, 100), "lukas": R(98, 120)}, "system", [])
    check(n + ": at its line with no live run the switch goes at once", d["do"] == "switch" and d["to"] == "lukas", d)
    d = D({**OFF, "system": R(1, 100), "lukas": R(1, 120)}, "system", [])
    check(n + ": at its line with no account to take over and no live run the stop goes at once", d["do"] == "stop", d)


def t_unreadable_runs_count_as_live():
    n = "unreadable-runs-count-as-live"
    d = D({"steven": R(52, 150), "system": R(40, 100), "lukas": R(98, 120)}, "steven", None)
    check(n + ": the live runs unread: a drain, and the why says UNMEASURED", d["do"] == "soft" and d.get("drain")
          and "UNMEASURED" in d["why"], d)


def t_the_floors_never_reach_zero():
    n = "the-floors-never-reach-zero"
    N = PLAN["numbers"]
    check(n + ": the first plan's floor is 1", N["floor_pct"] == 1 and N["last_account_floor_pct"] >= 1, N)
    check(n + ": the emergency line is 1", N["account_end"]["emergency_pct"] == 1, N["account_end"])
    claude = [s for s in PLAN["steps"] if PLAN["accounts"][s["use"]]["kind"] == "claude"]
    check(n + ": no Claude step leaves under 1", all(isinstance(s["leave"], (int, float)) and s["leave"] >= 1
                                                    for s in claude), claude)
    check(n + ": steven's leave line is 52, and the order is steven, system, lukas",
          [s["use"] for s in claude] == ["steven", "system", "lukas"] and claude[0]["leave"] == 52, claude)
    check(n + ": a write under the floor is refused", any("floor" in x for x in AP.problems(
        dict(PLAN, steps=[dict(s, leave=0) if s["use"] == "lukas" else s for s in PLAN["steps"]]))))


def t_a_pull_switch_waits_for_live_runs():
    """The act: a switch above the line (a rescue: `under` false) waits while a run is live, at most
    pull_drain_max_s (legacy_view: numbers.rescue.drain_h) after its first drain notice."""
    n = "a-pull-switch-waits-for-live-runs"
    calls = fake_switcher()
    meter = {**OFF, "system": R(40, 100), "lukas": R(98, 120)}
    numbers = AP.legacy_view(PLAN, {"now": NOW, "rows": meter})
    bound = numbers["pull_drain_max_s"]

    def decide(_m, live, _now, _p, _s, _mk, **_kw):
        return {"do": "switch", "to": "lukas", "under": False, "account": live, "pct_left": 40, "line": 1,
                "key": ACT.switch_key(live, "lukas", meter["lukas"]), "why": "a rescue of lukas's points"}

    def go(now, runs):
        (TMP / "live.txt").write_text("system")
        calls.write_text("")
        ACT.check(decide, lambda: numbers, now=now, meter_fn=lambda: meter, poll_fn=lambda: None, runs_fn=lambda: runs)
        return [ln.split()[0] for ln in calls.read_text().splitlines() if ln.split() and ln.split()[0] != "--json"]

    def last():
        return json.loads((TMP / "out" / "log.jsonl").read_text().splitlines()[-1])
    check(n + ": the bound is the plan's rescue drain (2 h)", bound == PLAN["numbers"]["rescue"]["drain_h"] * 3600 == 7200,
          bound)
    acts = go(NOW, RUN)
    nt = json.loads((TMP / "out" / "notice.json").read_text())
    check(n + ": a pull switch with a live run waits", "use" not in acts and last().get("do") == "drain", (acts, last()))
    check(n + ": its notice reads soft with drain true", nt.get("state") == "soft" and nt.get("drain") is True, nt)
    acts = go(NOW + 3600, RUN)
    check(n + ": still waiting an hour later, the run still live", "use" not in acts, acts)
    acts = go(NOW + bound + 100, RUN)
    check(n + ": past the bound the switch goes", "use" in acts, acts)
    for k in list(ACT.read_markers()):
        (TMP / "out" / "markers" / f"{k}.json").unlink()
    (TMP / "out" / "notice.json").unlink()
    acts = go(NOW + bound + 800, [])
    check(n + ": with no live run the pull switch goes at once", "use" in acts, acts)


def t_a_new_launch_waits_while_the_account_drains():
    import detached_helper as DH
    n = "a-new-launch-waits-while-the-account-drains"
    p = TMP / "out" / "notice.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"state": "soft", "drain": True, "since": ACT.iso(NOW - 60), "at": ACT.iso(NOW - 30),
                             "account": "steven", "why": "draining"}))
    why = DH.drain_refusal(NOW, {}, None, path=str(p))
    check(n + ": a new launch is refused while the account drains", bool(why) and "drain" in why, why)
    check(n + ": a continuation of a live run is let through", DH.drain_refusal(NOW, {"continued_from": "rm-x"}, None,
                                                                               path=str(p)) is None)
    check(n + ": a resume of a run's session is let through", DH.drain_refusal(NOW, {}, "sess-1", path=str(p)) is None)
    check(n + ": a notice 30 min old refuses nothing (the plan's timer stopped)",
          DH.drain_refusal(NOW + 1800, {}, None, path=str(p)) is None)
    p.write_text(json.dumps({"state": "soft", "since": ACT.iso(NOW - 60), "at": ACT.iso(NOW - 30)}))
    check(n + ": a soft notice that is no drain refuses nothing", DH.drain_refusal(NOW, {}, None, path=str(p)) is None)
    p.write_text("{not json")
    check(n + ": an unreadable notice refuses nothing", DH.drain_refusal(NOW, {}, None, path=str(p)) is None)


def t_a_new_launch_goes_at_the_soft_line():
    """The plan has no soft line: above the line, in the warning zone too, a new run starts."""
    import detached_helper as DH
    n = "a-new-launch-goes-at-the-soft-line"
    p = TMP / "out" / "notice.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    for left in (3, 2):
        for runs in ([], RUN):
            d = D({**OFF, "system": R(left, 100), "lukas": R(98, 120)}, "system", runs)
            ACT.write_notice(d, NOW)
            check("%s: system at %s%%, %d live run(s): a new run starts" % (n, left, len(runs)), d["do"] == "normal"
                  and DH.drain_refusal(NOW, {}, None, path=str(p)) is None, d)
    ACT.write_notice({**d, "do": "soft", "drain": True}, NOW)
    check(n + ": the same notice as a drain refuses (the probe can see a refusal)",
          bool(DH.drain_refusal(NOW, {}, None, path=str(p))))


def main():
    for t in (t_a_spent_account_drains_while_runs_live, t_no_live_run_means_no_wait, t_unreadable_runs_count_as_live,
              t_the_floors_never_reach_zero, t_a_pull_switch_waits_for_live_runs,
              t_a_new_launch_waits_while_the_account_drains, t_a_new_launch_goes_at_the_soft_line):
        try:
            t()
        except Exception as e:  # noqa: BLE001  a check that broke is a FAIL of its promise, by name
            import traceback
            traceback.print_exc()
            check(t.__name__[2:] + " raised", False, "%s: %s" % (type(e).__name__, e))
    print("selftest_account_actuator_drain: %s (%d failed)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
