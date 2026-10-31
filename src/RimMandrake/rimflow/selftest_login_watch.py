#!/usr/bin/env python3
"""selftest_login_watch.py: the lost-login answer (login_watch.py) and the role slot given back on an auth death."""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import dispatcher as D  # noqa: E402
import login_watch as LW  # noqa: E402
import role_launch as RL  # noqa: E402
import seat_restart as SR  # noqa: E402

FAILS = []
NOW = 1_800_000_000.0


def check(name, ok):
    print(("ok   " if ok else "FAIL ") + name)
    if not ok:
        FAILS.append(name)


def box(d, hold=True, armed=True, others=True):
    usage = os.path.join(d, "latest.json")
    at = SR._iso(NOW - 60)
    recs = {"livey": {"source": "ESTIMATE"}}
    if others:
        recs.update(a={"source": "MEASURED", "measured_at": at, "week_pct_used": 50.0},
                    b={"source": "MEASURED", "measured_at": at, "week_pct_used": 5.0},
                    lent={"source": "MEASURED", "measured_at": at, "week_pct_used": 0.0},
                    stale={"source": "MEASURED", "measured_at": SR._iso(NOW - 9000), "week_pct_used": 0.0})
    with open(usage, "w") as f:
        json.dump({"accounts": recs}, f)
    mach = os.path.join(d, "machine.json")
    with open(mach, "w") as f:
        json.dump({"machine": "boxy"}, f)
    h, a = os.path.join(d, "HOLD"), os.path.join(d, "ARMED")
    for p, on in ((h, hold), (a, armed)):
        if on:
            open(p, "w").close()
        elif os.path.exists(p):
            os.remove(p)
    return {"alarm_every_s": 21600, "login_watch": {
        "enabled": True, "auto_switch": True, "hold_file": h, "usage_latest": usage, "armed_file": a,
        "machine_file": mach}}


def obs(reading, paused=None, windows=(), lent=("lent",), live="livey"):
    return {"paused": paused, "agents": {"state": "MEASURED", "sessions": []},
            "login": {"probe": lambda: reading, "account": lambda: (live, lent), "stranded": lambda s: list(windows)}}


def run(sch, st, o, now):
    acts = []
    hold = LW.step(sch, st, o, now, lambda **k: acts.append(k), D.iso)
    return hold, acts


BAD = (False, "auth status exited 1")
GOOD = (True, "")


def test_dead_held():
    with tempfile.TemporaryDirectory() as d:
        sch, st = box(d), {}
        h, a = run(sch, st, obs(BAD), NOW)
        check("one failure is not an outage", h is None and not a)
        h, a = run(sch, st, obs(BAD), NOW + 120)
        al = [x for x in a if x["do"] == "alarm"]
        check("second failure alarms into log and ledger", len(al) == 1 and al[0]["note"] and al[0]["conductor_log"])
        check("the alarm names the way back and the emptiest allowed login", "use b --confirm boxy" in al[0]["raise_first"])
        check("the alarm says the HOLD is why", "HOLD" in al[0]["why"])
        check("held", bool(h) and st["login"]["dead_since"] == NOW)
        check("HOLD: no switch", not [x for x in a if x["do"] == "login_switch"])
        h, a = run(sch, st, obs(BAD), NOW + 240)
        check("no repeat inside the window, still held", not a and bool(h))
        h, a = run(sch, st, obs((None, "timeout")), NOW + 360)
        check("a blind probe keeps the hold", bool(h) and not a)
        h, a = run(sch, st, obs(BAD), NOW + 21800)
        check("repeats after alarm_every_s", len(a) == 1 and a[0]["kind"] == "login:expired:%d" % NOW)
        h, a = run(sch, st, obs(GOOD), NOW + 21900)
        check("back: opens, alarms once", h is None and a[0]["kind"] == "login:back:%d" % NOW and "dead_since" not in st["login"])


def test_blip():
    with tempfile.TemporaryDirectory() as d:
        sch, st = box(d), {}
        run(sch, st, obs(BAD), NOW)
        h, a = run(sch, st, obs(GOOD), NOW + 120)
        h2, a2 = run(sch, st, obs(BAD), NOW + 240)
        check("a blip clears the count", h is None and h2 is None and not a and not a2)
        check("no reading at all never holds", run(box(d), {}, obs((None, "x")), NOW)[0] is None)


def test_switch():
    with tempfile.TemporaryDirectory() as d:
        sch, st = box(d, hold=False), {}
        run(sch, st, obs(BAD), NOW)
        h, a = run(sch, st, obs(BAD), NOW + 120)
        sw = [x for x in a if x["do"] == "login_switch"]
        check("no HOLD, armed, healthy: switches to the emptiest non-lent", len(sw) == 1 and sw[0]["account"] == "b")
        check("switch is told to the log", sw[0]["conductor_log"] and sw[0]["machine"] == "boxy")
        h, a = run(sch, st, obs(BAD), NOW + 240)
        check("only one try", not a and bool(h))
        h, a = run(sch, st, obs(BAD), NOW + 1100)
        check("not back in time: alarm, no second try", [x["kind"].split(":")[1] for x in a] == ["switch_failed"])
        h, a = run(sch, st, obs(BAD), NOW + 1300)
        check("that alarm fires once", not a)
        got = []
        LW.run_switch({"epoch": NOW, "command": "ca", "account": "b", "machine": "boxy"}, got.append)
        check("the command", got[0][-5:] == ["ca", "use", "b", "--confirm", "boxy"] and got[0][0] == "systemd-run")
    for kw, o, name in ((dict(armed=False), obs(BAD), "unarmed"), (dict(others=False), obs(BAD), "no healthy login"),
                        (dict(), obs(BAD, paused="p"), "PAUSE"), (dict(), obs(BAD, lent=None), "lent unreadable"),
                        (dict(), obs(BAD, live=None), "live unknown")):
        with tempfile.TemporaryDirectory() as d:
            sch, st = box(d, hold=False, **kw), {}
            run(sch, st, o, NOW)
            h, a = run(sch, st, o, NOW + 120)
            check("%s: alarm, no switch" % name, [x["do"] for x in a] == ["alarm"] and bool(h))


def test_stranded():
    with tempfile.TemporaryDirectory() as d:
        sch, st = box(d), {}
        w = {"seat": "S", "sess": {"pid": 1, "sessionId": "x"}, "path": "p", "size": 9, "at": NOW - 900, "conductor": False}
        h, a = run(sch, st, obs(GOOD, windows=[w]), NOW)
        check("stranded seat gets a restart request", [x["do"] for x in a] == ["login_rescue"] and a[0]["request"]["session_id"] == "x")
        check("one request per error", not run(sch, st, obs(GOOD, windows=[w]), NOW + 120)[1])
        w2 = dict(w, at=NOW - 10)
        run(sch, st, obs(GOOD, windows=[w2]), NOW + 240)
        w3 = dict(w, at=NOW - 5)
        h, a = run(sch, st, obs(GOOD, windows=[w3]), NOW + 360)
        check("past the daily cap: alarm", a[0]["do"] == "alarm" and a[0]["kind"] == "login:stranded:S")
        c = dict(w, conductor=True, seat="C")
        h, a = run(sch, {}, obs(GOOD, windows=[c]), NOW)
        check("a Conductor window is never restarted", a[0]["do"] == "alarm")
        h, a = run(sch, {}, dict(obs(BAD, windows=[w])), NOW)
        check("no rescue on a dead login", not a)


def test_stranded_reader():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "t.jsonl")
        rec = {"type": "assistant", "isApiErrorMessage": True, "error": "authentication_failed", "timestamp": SR._iso(NOW - 900),
               "message": {"stop_reason": "stop_sequence", "content": [{"type": "text", "text": "Login expired"}]}}
        with open(path, "w") as f:
            f.write(json.dumps({"type": "user", "timestamp": SR._iso(NOW - 901), "message": {}}) + "\n")
            f.write(json.dumps(rec) + "\n")
        keep = SR.config, SR.transcript_for, LW.SM.names_of, SR._find
        sess = {"status": "idle", "sessionId": "x", "pid": 1}
        try:
            SR.config = lambda sch: {"S": {"kind": "doorbell"}, "C": {"kind": "conductor"}}
            SR.transcript_for = lambda s, c: path
            LW.SM.names_of = lambda c: c
            SR._find = lambda sessions, names: [sess]
            cfg = LW.config({})
            got = LW.stranded({}, cfg, [sess], NOW)
            check("a window on an auth error reads stranded", [(w["seat"], w["conductor"]) for w in got] == [("S", False), ("C", True)])
            check("too fresh is not stranded yet", not LW.stranded({}, cfg, [sess], NOW - 700))
            sess["status"] = "busy"
            check("a busy window is not stranded", not LW.stranded({}, cfg, [sess], NOW))
            sess["status"] = "idle"
            with open(path, "a") as f:
                f.write(json.dumps({"type": "user", "timestamp": SR._iso(NOW - 800), "message": {}}) + "\n")
            check("a later record clears it", not LW.stranded({}, cfg, [sess], NOW))
        finally:
            SR.config, SR.transcript_for, LW.SM.names_of, SR._find = keep


def test_quiet_and_gate():
    rec = {"type": "assistant", "isApiErrorMessage": True, "error": "authentication_failed",
           "message": {"stop_reason": "stop_sequence"}}
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "t.jsonl")
        for er, want in (("authentication_failed", "assistant_end"), ("rate_limit", "assistant_other")):
            with open(path, "w") as f:
                f.write(json.dumps(dict(rec, error=er, timestamp=SR._iso(NOW))) + "\n")
            check("%s reads %s" % (er, want), SR.tx_summary(path, peers=())["last_kind"] == want)
    with tempfile.TemporaryDirectory() as d:
        sch, st, a = box(d), {"login": {"fails": 1, "first_fail": NOW}}, []
        g = D.login_gate(sch, st, obs(BAD), NOW + 120, lambda **k: a.append(k), lambda kind: (True, {}))
        check("dead login shuts the gate", g("ring")[0] is False and "login dead" in g("role_launch")[1]["why"])
        g = D.login_gate({}, {}, {}, NOW, lambda **k: a.append(k), lambda kind: (True, {"x": 1}))
        check("off: the gate is unchanged", g("ring") == (True, {"x": 1}))
        a2 = []
        o = obs(BAD)
        o["login"]["probe"] = lambda: 1 / 0
        g = D.login_gate(sch, {}, o, NOW, lambda **k: a2.append(k), lambda kind: (True, {}))
        check("a broken watch alarms and holds nothing", g("ring")[0] and a2[0]["kind"] == "login:watch")


def test_slot_back():
    p = {"unit": "u", "mode": "alarm", "key": "k", "done": None, "had_done": False, "alarms_seen": ["old"],
         "event_cursor": None, "alarm_day": {"day": 1, "n": 0, "keys": {}}, "events_seen": None, "alarm_last_run": None}
    def rs_run():
        run_ = {"unit": "u", "at": NOW, "consumed": dict(p)}
        return {"alarms_seen": ["old", "new"], "alarm_day": {"day": 1, "n": 1, "keys": {"new": 1}}, "alarm_last_run": NOW,
                "runs": [run_]}, run_
    rs, r = rs_run()
    check("auth death gives the alarm slot back", RL.auth_failed_back(rs, r, "Failed to authenticate: OAuth session expired", NOW))
    check("marks restored", rs["alarms_seen"] == ["old"] and rs["alarm_day"]["n"] == 0 and "alarm_last_run" not in rs)
    rs, r = rs_run()
    check("another failure keeps it", not RL.auth_failed_back(rs, r, "disk full", NOW) and rs["alarm_day"]["n"] == 1)
    rs, r = rs_run()
    rs["auth_backs"] = {"day": RL.day_of(NOW), "n": RL.AUTH_BACKS_PER_DAY}
    check("the daily cap stops a loop", not RL.auth_failed_back(rs, r, "Login expired", NOW))
    rs, r = rs_run()
    rs["runs"].append({"at": NOW + 5})
    check("a later run keeps the marks", not RL.auth_failed_back(rs, r, "Login expired", NOW))


def main():
    for t in (test_dead_held, test_blip, test_switch, test_stranded, test_stranded_reader, test_quiet_and_gate, test_slot_back):
        t()
    print("selftest_login_watch: %s" % ("FAILED %d" % len(FAILS) if FAILS else "OK"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
