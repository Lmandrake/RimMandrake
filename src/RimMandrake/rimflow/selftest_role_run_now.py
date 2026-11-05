#!/usr/bin/env python3
"""Selftest of the one-shot role run (`role_launch.py run-now`; V3_ROLES_BUILD_EIGHT_CHAIRS_ONE_TABLE, the v3 trial
path). A run-now request sits in the dispatcher state (st["roles"][R]["run_now"]); the next tick launches it ONCE,
even for a role whose schedule entry is not enabled, through every gate a scheduled run passes (off switch, busy,
ops reading, band, daily cap, account), and consumes it on launch or refusal. The test role is
selftest_dispatcher.arbiter(), a plain two-slot clock role (its name is the fixture's, the Arbiter role is retired).
Pure but for a temp dir: fake obs, no systemd, no clock."""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import selftest_dispatcher as SD  # noqa: E402  (fixtures; its own tests do not run on import)

D, RL = SD.D, SD.RL
FAILS = []


def check(ok, msg):
    if not ok:
        FAILS.append(msg)
        print("FAIL:", msg)


T = SD.at_local("13:00")                  # no fixture slot (11:00, 17:00) is due: only a run-now can launch


def req(**kw):
    sch = SD.sched(roles=[SD.arbiter(enabled=False)])
    return RL.run_now_request(sch, dict({"role": "Arbiter", "by": "BENCH", "why": "v3 trial", "mode": None}, **kw),
                              T - 60)


def state(r=None, **rs):
    st = SD.fresh()
    st["roles"] = {"Arbiter": dict({"done": {}, "runs": []}, **rs)}
    if r is not None:
        st["roles"]["Arbiter"]["run_now"] = r
    return st


def ledger_boom():
    raise RuntimeError("ledger must not be read for a run-now")


def decide(st, role=None, status=None, now=T, **kw):
    ro = SD.lrobs(status if status is not None else SD.ops_status(now), ledger_boom, **kw)
    return SD.role_acts(SD.rdecide([role or SD.arbiter(enabled=False)], st, ro, now))


def launches(acts):
    return [a for a in acts if a["do"] == "role_launch"]


def test_request_validated():
    r = req()
    check(r["by"] == "BENCH" and r["why"] == "v3 trial" and r["mode"] == "run" and r["at"] == T - 60
          and set(r) == {"at", "by", "why", "mode"}, "request: the defaults (mode run for a run_token_cap role)")
    for kw, text in (({"role": "Nobody"}, "no role"), ({"by": ""}, "--by"), ({"why": " "}, "--why"),
                     ({"mode": "alarm"}, "mode"), ({"mode": "event"}, "mode"), ({"mode": "quick"}, "mode")):
        try:
            req(**kw)
            check(False, "request %r refused" % kw)
        except ValueError as e:
            check(text in str(e), "request %r refused naming %s: %s" % (kw, text, e))
    sch = SD.sched(roles=[SD.operations(enabled=False)])
    ok = RL.run_now_request(sch, {"role": "Operations", "by": "B", "why": "w", "mode": "economy"}, T)
    check(ok["mode"] == "economy", "a mode the role has a cap for is accepted (Operations economy)")


def test_launch_disabled_role_once():
    st = state(req())
    acts = decide(st)
    la = launches(acts)
    check(len(la) == 1, "run-now launches a role whose entry is not enabled: %r" % [a["do"] for a in acts])
    a = la[0]
    check(a["mode"] == "run" and " run-now " in a["slot"] and a["slot"].startswith(RL.day_of(T)),
          "the run's key: '<day> run-now <at>', mode run: %r" % a["slot"])
    check("run-now by BENCH: v3 trial" in a["why"] and a["budget"] == 100000 and a.get("run_now"),
          "why names who asked and why; budget = run_token_cap x GREEN 1.0; the action carries run_now")
    check("run-now by BENCH: v3 trial" in a["message"], "the run is told it is a run-now and why")
    rs = st["roles"]["Arbiter"]
    check("run_now" not in rs and rs["run_now_last"]["outcome"] == "launched" and rs["run_now_last"]["unit"] == a["unit"],
          "the request is consumed on launch, its outcome kept: %r" % rs.get("run_now_last"))
    check("event_cursor" not in rs, "a run-now sets no event baseline (enabling the role later baselines as before)")
    rs["runs"] = []
    rs.pop("pending_launch", None)
    check(not launches(decide(st, now=T + 120)), "one-shot: the next tick launches nothing")
    check(not decide(state(None)), "a disabled role with no request: nothing at all (unchanged)")


def test_refusals_consume():
    for name, kw, want in (
            ("off switch", {"off": "owner: off"}, "off switch"),
            ("ops UNMEASURED", {"status": SD.ops_status(T, m="UNMEASURED")}, "REFUSED"),
            ("band FLOOR", {"status": SD.ops_status(T, week_left=5.0)}, "band FLOOR"),
            ("daily cap", {"spent": 200000}, "daily_token_cap")):
        st = state(req())
        role = SD.arbiter(enabled=False, throttle_bands={
            "GREEN": {"runway_ge": 1.5, "quick_cap_x": 1.0, "slots": "all"},
            "FLOOR": {"week_left_pct_lt": 10, "quick_cap_x": 0.4, "slots": "none"}})
        if kw.get("spent"):
            st["roles"]["Arbiter"]["runs"] = [{"day": RL.day_of(T), "tokens": kw["spent"], "state": "done",
                                               "unit": "rm-role-arbiter-1", "at": T - 600}]
        acts = decide(st, role=role, status=kw.get("status"), off=kw.get("off"))
        rs = st["roles"]["Arbiter"]
        check(not launches(acts) and any(want in x.get("why", "") for x in acts),
              "%s: no launch, said (%s): %r" % (name, want, [x.get("why", "")[:90] for x in acts]))
        check("run_now" not in rs and rs.get("run_now_last", {}).get("outcome", "").startswith("refused"),
              "%s: the request is consumed (one-shot), its refusal kept: %r" % (name, rs.get("run_now_last")))


def test_waits_keep_request():
    st = state(req(), runs=[{"state": "running", "unit": "rm-role-arbiter-9", "at": T - 30, "scope": "S.scope",
                             "marker": "M", "item": "I", "budget": 1, "mode": "run", "day": RL.day_of(T)}])
    check(not launches(decide(st)) and st["roles"]["Arbiter"].get("run_now"),
          "busy (a run of the role is running): waits, the request kept")
    st2 = state(dict(req(), at=T - RL.RUN_NOW_TTL_S - 1))
    acts = decide(st2)
    check(not launches(acts) and "run_now" not in st2["roles"]["Arbiter"]
          and any("expired" in x.get("why", "") for x in acts), "a request older than RUN_NOW_TTL_S expires, said")


def test_enabled_role_slot_untouched():
    t = SD.at_local("11:00")
    st = state(dict(req(), at=t - 60), event_cursor=t - 60, events_seen=[])
    # daily cap room for the run-now beside the two scheduled slots it keeps a reserve for (2 x 100000)
    role = SD.arbiter(daily_token_cap=400000)
    ro = SD.robs(SD.ops_status(t))
    la = launches(SD.role_acts(SD.rdecide([role], st, ro, t)))
    rs = st["roles"]["Arbiter"]
    check(len(la) == 1 and " run-now " in la[0]["slot"], "an enabled role: the run-now goes first")
    check(RL.slot_key(t, "11:00") not in rs["done"], "its 11:00 slot is not consumed by the run-now")
    check(rs["event_cursor"] == t - 60, "a run-now does not move the event cursor")
    rs["runs"] = []
    rs.pop("pending_launch", None)
    la = launches(SD.role_acts(SD.rdecide([role], st, ro, t + 120)))
    check(len(la) == 1 and la[0]["slot"] == RL.slot_key(t, "11:00"), "the next tick runs the 11:00 slot as before")
    # review r1: a slot already past its late window keeps no reserve (13:00: 11:00 is gone, 17:00 is kept)
    t = SD.at_local("13:00")
    ro = SD.robs(SD.ops_status(t))
    st = state(dict(req(), at=t - 60), event_cursor=t - 60, events_seen=[])
    role = SD.arbiter(daily_token_cap=200000)
    la = launches(SD.role_acts(SD.rdecide([role], st, ro, t)))
    check(len(la) == 1 and " run-now " in la[0]["slot"], "13:00: only 17:00 is reserved, the run-now fits 200000")
    st = state(dict(req(), at=t - 60), event_cursor=t - 60, events_seen=[])
    role = SD.arbiter(daily_token_cap=199999)
    acts = SD.role_acts(SD.rdecide([role], st, ro, t))
    check(not launches(acts) and st["roles"]["Arbiter"]["run_now_last"]["outcome"] == "refused: daily cap",
          "one token short of run-now + the 17:00 reserve: refused, consumed")


def test_launch_role_override():
    role = SD.arbiter(enabled=False, pre_launch=[["x"]])
    check(RL.launch_role(role, {"do": "role_launch"}) is role, "a scheduled launch: the schedule entry as is")
    r2 = RL.launch_role(role, {"run_now": {"by": "B"}, "pre_launch": [["y"]]})
    check(r2["enabled"] is True and r2["pre_launch"] == [["y"]] and role["enabled"] is False,
          "a run-now: enabled for this launch only, its pre-steps; the schedule entry untouched")
    r3 = RL.launch_role(role, {"run_now": {"by": "B"}, "pre_launch": None})
    check(r3["pre_launch"] == [["x"]], "a run-now with no pre-steps of its own keeps the schedule's")


def test_execute_launches_disabled_role():
    role = SD.arbiter(enabled=False)
    sch = SD.sched(roles=[role])
    st = state(req())
    acts = decide(st, role=role)
    got = []

    def fake_launch(r, unit, msg, root, claude):
        got.append(r)
        return True, "ok", {}
    root = tempfile.mkdtemp(prefix="run_now_exec_")
    fx = {"role_launch": fake_launch, "off": lambda p: None, "paused": lambda: None, "note": lambda i, t: (True, ""),
          "publish": lambda n: None}
    D.execute(acts, sch, st, root, True, T, fx)
    check(len(got) == 1 and got[0]["enabled"] is True,
          "execute launches the disabled role for the run-now: %r"
          % [a.get("result") for a in acts])
    st = state(req())
    acts = decide(st, role=role)
    got.clear()
    D.execute(acts, sch, st, root, True, T, dict(fx, paused=lambda: "owner pause"))
    rs = st["roles"]["Arbiter"]
    check(not got and rs.get("run_now"), "PAUSE at launch: not launched, the request given back")


def test_cli_writes_request():
    root = tempfile.mkdtemp(prefix="run_now_cli_")
    sch_path = os.path.join(root, "sched.json")
    with open(sch_path, "w") as f:
        json.dump({"seats": {}, "roles": [SD.arbiter(enabled=False)], "alarm_item": "X"}, f)
    base = ["run-now", "--schedule", sch_path, "--root", root, "--role", "Arbiter", "--by", "BENCH", "--why", "trial"]
    rc = RL.main(base)
    check(rc == 0 and not os.path.exists(os.path.join(root, "state.json")), "run-now without --apply writes nothing")
    rc = RL.main(base + ["--apply"])
    st = json.load(open(os.path.join(root, "state.json")))
    r = st["roles"]["Arbiter"]["run_now"]
    check(rc == 0 and r["by"] == "BENCH" and r["why"] == "trial",
          "run-now --apply writes the request into the state")
    check(RL.main(base + ["--apply"]) == 1, "a second request while one is pending is refused (cancel it first)")
    check(RL.main(["run-now", "--schedule", sch_path, "--root", root, "--role", "Arbiter", "--cancel", "--apply"]) == 0
          and "run_now" not in json.load(open(os.path.join(root, "state.json")))["roles"]["Arbiter"],
          "--cancel withdraws it")
    check(RL.main(base + ["--mode", "alarm", "--apply"]) == 2, "a bad request exits 2")
    check(RL.main(["run-status", "--root", root, "--role", "Arbiter"]) == 0, "run-status reads it")


TESTS = (test_request_validated, test_launch_disabled_role_once, test_refusals_consume, test_waits_keep_request,
         test_enabled_role_slot_untouched, test_launch_role_override, test_execute_launches_disabled_role,
         test_cli_writes_request)


def main():
    SD.strict_roles()       # strict gates under test; the advisory default: selftest_role_caps_advisory A7
    for t in TESTS:
        try:
            t()
        except Exception as e:  # noqa: BLE001
            import traceback
            traceback.print_exc()
            check(False, "%s raised %s: %s" % (t.__name__, type(e).__name__, e))
    print("selftest_role_run_now: %d checks failed" % len(FAILS) if FAILS else "selftest_role_run_now: ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
