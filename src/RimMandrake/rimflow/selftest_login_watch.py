#!/usr/bin/env python3
"""selftest_login_watch.py: the lost-login answer (login_watch.py) and the role slot given back on an auth death."""
import calendar
import datetime
import json
import os
import sys
import tempfile
import zoneinfo

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
        check("the same kind each tick: the Dispatcher rate-limits it, an undelivered one retries, still held",
              bool(h) and [x["kind"] for x in a] == ["login:expired:%d" % st["login"]["dead_since"]])
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
        st2 = {}
        run(sch, st2, obs(BAD), NOW)
        run(sch, st2, obs(BAD), NOW + 120)
        LW.switch_failed(st2)
        h, a = run(sch, st2, obs(BAD), NOW + 240)
        check("a refused switch is not tried again and alarms at once",
              [x["kind"].split(":")[1] for x in a] == ["switch_failed"] and "switch_at" in st2["login"])
        h, a = run(sch, st, obs(BAD), NOW + 1300)
        check("that alarm stays up until the login is back (the Dispatcher rate-limits it)", a and "switch_failed" in a[0]["kind"])
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
        w = {"seat": "S", "sess": {"pid": 1, "sessionId": "x"}, "start": 77, "path": "p", "size": 9, "at": NOW - 900, "conductor": False}
        h, a = run(sch, st, obs(GOOD, windows=[w]), NOW)
        check("stranded seat gets a restart request", [x["do"] for x in a] == ["login_rescue"] and a[0]["request"]["session_id"] == "x"
              and a[0]["request"]["start"] == 77)
        check("one request per error", not run(sch, st, obs(GOOD, windows=[w]), NOW + 120)[1])
        h, a = run(sch, st, obs(GOOD, windows=[w]), NOW + 7300)
        check("an error the request did not clear alarms", [x["do"] for x in a] == ["alarm"] and "did not clear" in a[0]["why"])
        check("still one request after UTC midnight", [x["do"] for x in run(sch, st, obs(GOOD, windows=[w]), NOW + 86400)[1]] == ["alarm"])
        w2 = dict(w, at=NOW - 10)
        run(sch, st, obs(GOOD, windows=[w2]), NOW + 240)
        w3 = dict(w, at=NOW - 5)
        h, a = run(sch, st, obs(GOOD, windows=[w3]), NOW + 360)
        check("past the daily cap: alarm", a[0]["do"] == "alarm" and a[0]["kind"] == "login:stranded:S")
        c = dict(w, conductor=True, seat="C")
        h, a = run(sch, {}, obs(GOOD, windows=[c]), NOW)
        check("a Conductor window is never restarted: it is poked", [x["do"] for x in a] == ["login_poke"])
        h, a = run(sch, {}, obs(GOOD, windows=[dict(w, start=None)]), NOW)
        check("no birth record: an alarm, no request the kill would refuse", [x["do"] for x in a] == ["alarm"])
        h, a = run(sch, {}, obs(GOOD, windows=[w], paused="x"), NOW)
        check("PAUSE: no rescue", not a)
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
            limited = dict(rec, error="rate_limit", message={"stop_reason": "stop_sequence", "content": [{"type": "text", "text": "limit"}]})
            at = NOW - 900
            when = datetime.datetime.fromtimestamp(at + 2 * 3600, datetime.timezone.utc)
            for text, wait in (("limit", 5 * 3600), ("limit \u00b7 resets %s (UTC)" % when.strftime("%I:%M%p").lower(), 2 * 3600)):
                limited["message"]["content"][0]["text"] = text
                with open(path, "w") as f:
                    f.write(json.dumps(limited) + "\n")
                check("a rate limit waits out %d s: not before" % wait, not LW.stranded({}, cfg, [sess], at + wait - 60))
                late = LW.stranded({}, cfg, [sess], at + wait + 60)
                check("a rate limit waits out %d s: then due" % wait, [w["error"] for w in late] == ["rate_limit"] * 2)
            with open(path, "w") as f:
                f.write(json.dumps(rec) + "\n")
            sess["status"] = "busy"
            check("a busy window is not stranded", not LW.stranded({}, cfg, [sess], NOW))
            sess["status"] = "idle"
            with open(path, "a") as f:
                f.write(json.dumps({"type": "user", "timestamp": SR._iso(NOW - 800), "message": {}}) + "\n")
            check("a later record clears it", not LW.stranded({}, cfg, [sess], NOW))
        finally:
            SR.config, SR.transcript_for, LW.SM.names_of, SR._find = keep


def test_limit_reset():
    LA = "You've hit your session limit \u00b7 resets 1:10pm (America/Los_Angeles)"
    at = calendar.timegm((2026, 10, 30, 12, 0, 0))             # 05:00 PDT
    want = calendar.timegm((2026, 10, 30, 20, 10, 0))          # 13:10 PDT
    check("a named reset is the next such moment", LW.limit_reset(LA, at) == want)
    check("one already past is tomorrow's", LW.limit_reset(LA, want + 1) == want + 86400)
    tz = zoneinfo.ZoneInfo("America/Los_Angeles")
    fall = datetime.datetime(2026, 11, 1, 1, 30, tzinfo=tz).timestamp()
    check("the repeated DST hour is 40 minutes off, not a day",
          LW.limit_reset("resets 1:10am (America/Los_Angeles)", fall) == fall + 2400)
    check("no minutes, 12am", LW.limit_reset("resets 12am (UTC)", at) == calendar.timegm((2026, 10, 31, 0, 0, 0)))
    weekly = "You've hit your weekly limit \u00b7 resets Oct 31, 5pm (America/Los_Angeles)"
    check("a weekly reset names its day", LW.limit_reset(weekly, at) == calendar.timegm((2026, 11, 1, 0, 0, 0)))
    check("a weekly date behind us is next year's", LW.limit_reset(weekly, calendar.timegm((2026, 11, 2, 0, 0, 0)))
          == calendar.timegm((2027, 11, 1, 0, 0, 0)))
    leap = calendar.timegm((2028, 2, 29, 17, 0, 0))
    check("Feb 29 is found across a year roll and next to a leap year's end",
          LW.limit_reset("resets Feb 29, 5pm (UTC)", calendar.timegm((2027, 12, 31, 12, 0, 0))) == leap
          and LW.limit_reset("resets Feb 29, 5pm (UTC)", calendar.timegm((2028, 2, 28, 12, 0, 0))) == leap)
    check("unnamed, or an unknown zone, is no reset", LW.limit_reset("rate limited", at) is None
          and LW.limit_reset("resets 1pm (Mars/Base)", at) is None and LW.limit_reset(None, at) is None)
    check("the text survives a record", "resets" in LW._record_text({"message": {"content": [{"type": "text", "text": LA}]}}))


def test_quiet_and_gate():
    check("an API error mid-retry, not a stopped turn, ends nothing",
          SR.api_ended({"type": "assistant", "isApiErrorMessage": True, "error": "server_error", "message": {}}) is None)
    rec = {"type": "assistant", "isApiErrorMessage": True, "error": "authentication_failed",
           "message": {"stop_reason": "stop_sequence"}}
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "t.jsonl")
        for er, want in (("authentication_failed", True), ("rate_limit", True), ("server_error", True), ("overloaded", False)):
            with open(path, "w") as f:
                f.write(json.dumps(dict(rec, error=er, timestamp=SR._iso(NOW))) + "\n")
            tx = SR.tx_summary(path, peers=())
            check("%s: the kill fence reads %s" % (er, want), SR.killable_turn(tx) is want)
            check("%s is no ended turn: a fresh window dying on it is not verified" % er,
                  tx["last_kind"] == "assistant_other")
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


def test_alarm_run_retried_after_login_heals():
    """OPS_ALARM_RETRY_AFTER_AUTH_DEATH, end to end through the real supervise and decide: the 10-30 Operations alarm
    run dies on the real text, is held while the login is dead, and runs once it works, without running twice."""
    import selftest_dispatcher as SD
    os.environ["TZ"] = "UTC"
    op = SD.operations(runs_local=["07:30"], economy_pass_local=None, alarm_run_gap_s=1000)
    now = SD.at_local("12:00")
    ALARMS = {"a1": {"state": "OPEN", "item": "ITEM_ONE"}}
    ob = SD.robs(SD.ops_status(now, alarms=ALARMS))
    death = {"is_error": True, "subtype": "success", "result": "Failed to authenticate: OAuth session expired and could "
             "not be refreshed", "usage": SD.usage()}
    result = [death]
    ob.update(unit_state=lambda u: "inactive", result=lambda run: result[0])
    sch = {"roles": [op]}
    st = {"roles": {}}

    def decide(at, gate=None):
        acts = []
        ob.update({k: v for k, v in SD.robs(SD.ops_status(at, alarms=ALARMS)).items() if k == "ops"})
        RL.decide_roles(sch, st, ob, at, lambda **k: acts.append(k), set(), gate)
        launch = [a for a in acts if a.get("do") == "role_launch"]
        for a in launch:                                # what dispatcher.execute does on a good systemd-run
            rs = st["roles"]["Operations"]
            rs.setdefault("runs", []).append({"unit": a["unit"], "at": at, "state": "running", "mode": "alarm",
                                              "budget": 1000, "item": "ROLES_ITEM_X", "seat": "BENCH", "scope": "sc",
                                              "consumed": rs.pop("pending_launch")})
        return launch, acts

    def supervise(at):
        acts = []
        RL.supervise_roles(sch, st, ob, at, lambda **k: acts.append(k))
        return [a for a in acts if str(a.get("kind")).endswith(":failed")]

    first, _ = decide(now)
    check("the alarm launches a run", len(first) == 1 and "alarm" in str(first[0].get("mode", "alarm")))
    failed = supervise(now + 120)
    check("its auth death is told as a rerun", len(failed) == 1 and "reruns once the login works" in failed[0]["raise_first"])
    dead = lambda kind: (False, {"why": "login dead"})
    held, acts = decide(now + 240, dead)
    check("a dead login holds the rerun, and says so", not held and any(a.get("do") == "role_hold" for a in acts))
    check("still held hours later", not decide(now + 8 * 3600, dead)[0])
    again, _ = decide(now + 14 * 3600)
    check("the login back: it runs again", len(again) == 1)
    result[0] = {"subtype": "success", "result": "fine", "usage": SD.usage(input_tokens=10)}
    check("a good rerun raises nothing", not supervise(now + 14 * 3600 + 120))
    check("and is not repeated", not decide(now + 15 * 3600)[0])

    # a second outage the same day still gets its run: the login's return gave the count back
    rs = st["roles"]["Operations"]
    rs["auth_backs"] = {"day": RL.day_of(now), "n": RL.AUTH_BACKS_PER_DAY}
    with tempfile.TemporaryDirectory() as d:
        lst = {"login": {"dead_since": NOW - 60, "hold": "h", "fails": 2, "first_fail": NOW - 60}, "roles": {"Operations": rs, "x": 1}}
        run(box(d), lst, obs(GOOD), NOW)
    check("the login's return restores the per-day count", "auth_backs" not in rs)


def test_probe():
    with tempfile.TemporaryDirectory() as d:
        exe = os.path.join(d, "fake")
        for body, want in (('echo \'{"loggedIn": true}\'', True), ('echo \'{"loggedIn": false}\'; exit 1', False),
                           ("echo Please run /login >&2; exit 1", False),
                           ("echo 'Please run /login · API Error: 403 Attention Required! | Cloudflare' >&2; exit 1", None), ("echo segfault >&2; exit 139", None),
                           ("echo junk", None), ("sleep 5", None), ('echo \'{"error": "server"}\'', None),
                           ('echo \'{"loggedIn": "yes"}\'', None), ("echo '[1]'", None),
                           ('echo \'{"error": "x"}\'; echo Please run /login >&2; exit 1', False)):
            with open(exe, "w") as f:
                f.write("#!/bin/sh\n%s\n" % body)
            os.chmod(exe, 0o755)
            check("probe %s -> %s" % (body[:24], want), LW.probe(exe, 1)[0] is want)
    with tempfile.TemporaryDirectory() as d:
        sch, st = box(d), {}
        o = obs(GOOD)
        o["login"]["probe"] = lambda: (None, "crash")
        seen = [run(sch, st, o, NOW + i)[1] for i in range(5)]
        check("blind ticks alarm only after blind_alarm_n", not any(seen[:4]) and seen[4][0]["kind"] == "login:blind")
        check("blind holds nothing", run(sch, st, o, NOW + 9)[0] is None)


def test_bad_usage_file():
    with tempfile.TemporaryDirectory() as d:
        sch, st = box(d), {}
        with open(sch["login_watch"]["usage_latest"], "w") as f:
            json.dump({"accounts": ["a"]}, f)
        run(sch, st, obs(BAD), NOW)
        check("accounts as a list holds the fleet, no raise", bool(run(sch, st, obs(BAD), NOW + 120)[0]))


def test_pick_and_way():
    with tempfile.TemporaryDirectory() as d:
        cfg = LW.config(box(d))
        at = SR._iso(NOW)
        with open(cfg["usage_latest"], "w") as f:
            json.dump({"accounts": {n: {"source": "MEASURED", "measured_at": at, "week_pct_used": u} for n, u in
                                    (("full", 95), ("some", 60), ("empty", 5), ("unread", None))}}, f)
        check("over the week line, emptiest first; no reading is unfit",
              LW.healthy_logins(cfg, "x", (), NOW, {"target_min": {"week_left_pct_ge": 20}}) == ["empty", "some"])
    for w in (LW.way_back(["a"], None), LW.way_back([], "m"), LW.way_back(["a"], "m")):
        check("way back never sends him to a window, never prints None",
              "None" not in w and "/login in any" not in w and "plain terminal" in w)


def test_give_back():
    st = {"login": {"switch_at": NOW, "switched_to": "a", "rescues": {"S": {"day": 1, "n": 2, "for": NOW}}}}
    back = D.unreleased(st, [{"do": "login_switch"}, {"do": "login_rescue", "seat": "S"}], NOW)
    check("a raised tick gives both back", len(back) == 2 and "switch_at" not in st["login"]
          and st["login"]["rescues"]["S"] == {"day": 1, "n": 1})
    check("a released switch stays", not D.unreleased(st, [{"do": "login_switch", "released": True}], NOW))
    LW.give_back(st, {"do": "login_rescue", "seat": "S"}, spent=True)
    check("a failed write keeps its place in the day's limit", st["login"]["rescues"]["S"]["n"] == 1)
    LW.switch_failed(st)
    check("a refused switch alarms at once", st["login"]["switch_at"] == 0)


def test_release():
    with tempfile.TemporaryDirectory() as d:
        sch = box(d, hold=False)
        sw = {"do": "login_switch", "kind": "login:switch", "seat": None, "account": "b", "machine": "boxy", "command": "ca",
              "why": "w"}
        res = {"do": "login_rescue", "seat": "S", "kind": "x", "why": "w", "request": {}}
        fired, logged = [], []
        fx = {"login_switch": lambda argv: fired.append(argv) or "started: ok", "paused": lambda: None,
              "conductor_log": lambda *a: logged.append(a) or "logged", "lock": lambda: None}
        st = {"alarms": {}, "login": {"switch_at": NOW}}
        D.execute([dict(sw)], sch, st, d, True, NOW, fx, deadline=NOW + 1e9)
        check("the switch runs at release when nothing blocks it", len(fired) == 1 and st["login"]["switch_at"] == NOW)
        open(sch["login_watch"]["hold_file"], "w").close()
        D.execute([dict(sw)], sch, st, d, True, NOW, fx, deadline=NOW + 1e9)
        check("a HOLD landed during the lock wait stops it", len(fired) == 1 and "switch_at" not in st["login"])
        os.remove(sch["login_watch"]["hold_file"])
        st["login"]["switch_at"] = NOW
        D.execute([dict(sw)], sch, st, d, True, NOW, dict(fx, paused=lambda: "p"), deadline=NOW + 1e9)
        check("a PAUSE landed during the lock wait stops it", len(fired) == 1 and "switch_at" not in st["login"])
        st["login"]["switch_at"] = NOW
        D.execute([dict(sw)], sch, st, d, True, NOW, dict(fx, login_switch=lambda argv: "FAILED: no"), deadline=NOW + 1e9)
        check("a refused switch is due its alarm now", st["login"]["switch_at"] == 0)
        st["login"]["rescues"] = {"S": {"day": 1, "n": 1, "for": NOW}}
        D.execute([dict(res)], sch, st, d, True, NOW, dict(fx, paused=lambda: "p"), deadline=NOW + 1e9)
        check("PAUSE at release: the rescue goes back", st["login"]["rescues"]["S"] == {"day": 1, "n": 0})


CF_TEXT = "Please run /login · API Error: 403 Attention Required! | Cloudflare"
PAUSE_TEXT = "owner 2026-11-06 18:22 PST: Stop the pipeline immediately. No further runs except for test runs allowed."


def _overnight_transcript(path, at):
    """The CONDUCTOR window's tail at 2026-11-13T09:48:59Z, shape for shape (14f81ed2...jsonl): a tool result, the
    api-request record, the synthetic 403 record that ended the turn, then the system turn-duration record."""
    sid = "14f81ed2-1357-4f6c-ae1f-5ffb7a88ad6b"
    recs = [{"type": "user", "isSidechain": False, "timestamp": SR._iso(at - 0.09), "sessionId": sid,
             "message": {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "t", "content": "- 01:32 stage 2"}]}},
            {"type": "api-request", "timestamp": SR._iso(at - 0.04), "sessionId": sid},
            {"type": "assistant", "error": "authentication_failed", "isApiErrorMessage": True, "isSidechain": False,
             "apiErrorStatus": 403, "timestamp": SR._iso(at), "sessionId": sid,
             "message": {"model": "<synthetic>", "role": "assistant", "stop_reason": "stop_sequence", "stop_sequence": "",
                         "type": "message", "content": [{"type": "text", "text": CF_TEXT}]}},
            {"type": "system", "subtype": "turn_duration", "isSidechain": False, "timestamp": SR._iso(at + 0.01), "sessionId": sid}]
    with open(path, "w") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")
    return sid


def test_overnight_conductor_cloudflare():
    """RIMMANDRAKE_RESCUE_STRANDED_CONDUCTOR_CLOUDFLARE_SAID_LOGIN: the Conductor window sat on a Cloudflare 403 from
    01:48 PST under PAUSE with the login healthy, and nothing was raised (PAUSE skipped the stranded check) and nothing
    could have recovered it (a Conductor was only alarmed). Now it is poked, PAUSE or not, and his phone is told."""
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "t.jsonl")
        at = NOW - 400
        sid = _overnight_transcript(path, at)
        sess = {"name": "CONDUCTOR", "status": "idle", "pid": 3152005, "sessionId": sid, "cwd": "/home/mandrake/rm/bench"}
        keep = SR.config, SR.transcript_for, SR.session_file
        try:
            SR.config = lambda sch: {"BENCH": {"kind": "conductor", "session_name": "CONDUCTOR", "session_aliases": ["AGENT BENCH"]}}
            SR.transcript_for = lambda s, c: path
            SR.session_file = lambda pid: {"procStart": "16824875"}
            sch, st = box(d), {}
            cfg = LW.config(sch)
            got = LW.stranded(sch, cfg, [sess], NOW)
            check("the 403 record reads stranded, the real lookup finds CONDUCTOR", [(w["seat"], w["conductor"]) for w in got] == [("BENCH", True)])
            check("a Cloudflare challenge is marked transient", bool(got) and got[0].get("cloudflare") is True)

            def o(now):
                x = obs(GOOD, paused=PAUSE_TEXT)
                x["agents"]["sessions"] = [sess]
                x["login"]["stranded"] = lambda s: LW.stranded(sch, cfg, s, now)
                return x
            h, a = run(sch, st, o(NOW), NOW)
            pokes = [x for x in a if x["do"] == "login_poke"]
            check("under PAUSE the stranded Conductor is poked", len(pokes) == 1 and pokes[0]["seat"] == "BENCH"
                  and pokes[0]["pid"] == 3152005 and pokes[0]["session_id"] == sid)
            check("the poke tells his phone", bool(pokes) and (pokes[0].get("phone") or {}).get("key"))
            check("the poke is a program's text, never his", bool(pokes) and pokes[0]["text"].startswith("[RimFlow login rescue]"))
            check("one poke per error", not run(sch, st, o(NOW + 120), NOW + 120)[1])
            late = NOW + cfg["poke_wait_s"] + 60
            h, a = run(sch, st, o(late), late)
            check("a poke that did not clear it alarms, to the phone too", [x["do"] for x in a] == ["alarm"]
                  and a[0]["kind"] == "login:stranded:BENCH" and (a[0].get("phone") or {}).get("key"))
            sch2, st2 = box(d), {}
            for i in range(cfg["rescues_per_day"] + 1):
                t = NOW + i * 600
                _overnight_transcript(path, t - 400)
                h, a = run(sch2, st2, o(t), t)
            check("past rescues_per_day: alarm, no poke", [x["do"] for x in a] == ["alarm"])
        finally:
            SR.config, SR.transcript_for, SR.session_file = keep


def test_poke_release():
    with tempfile.TemporaryDirectory() as d:
        sch = box(d)
        pk = {"do": "login_poke", "seat": "BENCH", "pid": 7, "session_id": "s", "text": "[RimFlow login rescue] x",
              "why": "w", "note": True, "conductor_log": True, "kind": "login:poke:BENCH",
              "phone": {"key": "k1", "title": "t", "detail": "d"}}
        pokes, phones = [], []
        fx = {"paused": lambda: PAUSE_TEXT, "conductor_log": lambda *a: "logged", "lock": lambda: None,
              "login_poke": lambda a: pokes.append(a) or "poked", "phone": lambda row: phones.append(row) or True}
        st = {"alarms": {}, "login": {}}
        D.execute([dict(pk)], sch, st, d, True, NOW, fx, deadline=NOW + 1e9)
        check("a poke is released under PAUSE: the Conductor is not the pipeline", len(pokes) == 1)
        check("the poke's phone push goes", [r["key"] for r in phones] == ["k1"])
        al = {"do": "alarm", "kind": "login:stranded:BENCH", "seat": "BENCH", "why": "w", "note": True,
              "phone": {"key": "k2", "title": "t", "detail": "d"}}
        D.execute([dict(al)], sch, st, d, True, NOW, fx, deadline=NOW + 1e9)
        D.execute([dict(al)], sch, st, d, True, NOW + 60, fx, deadline=NOW + 1e9)
        check("a phoned alarm pushes once, not on its rate-limited repeat", [r["key"] for r in phones] == ["k1", "k2"])


def test_poke_wire():
    """LW.poke finds the window by pid and session, and refuses a pid that now runs another session."""
    sent = []
    recs = [{"pid": 7, "sessionId": "s", "messagingSocketPath": "/x", "peerToken": "t"}]
    bc = type("BC", (), {"sessions": staticmethod(lambda: recs),
                         "send": staticmethod(lambda rec, text, sender="OWNER": sent.append((rec["pid"], sender)) or None)})
    check("poke delivers to the window's own socket", LW.poke({"pid": 7, "session_id": "s", "text": "x"}, bc) == "poked"
          and sent == [(7, LW.POKE_SENDER)])
    check("a reused pid is refused", LW.poke({"pid": 7, "session_id": "other", "text": "x"}, bc).startswith("FAILED"))
    check("no live record is refused", LW.poke({"pid": 8, "session_id": "s", "text": "x"}, bc).startswith("FAILED"))
    rec = {"type": "user", "origin": {"kind": "peer", "name": LW.POKE_SENDER}, "timestamp": SR._iso(NOW),
           "message": {"role": "user", "content": '<cross-session-message from-name="%s" from-mode="bypass">\n[RimFlow login rescue] x\n</cross-session-message>' % LW.POKE_SENDER}}
    check("the poke is not his input (no chat clock, no cancel)", SR._is_human_input(rec, ["CONDUCTOR"]) is False)
    rec2 = dict(rec, origin={"kind": "peer", "name": "OWNER"})
    check("an OWNER peer message is still his input", SR._is_human_input(rec2, ["CONDUCTOR"]) is True)


def test_cloudflare_role_runs():
    run_ = {"consumed": {"unit": "u"}, "at": NOW - 60, "unit": "u"}
    res = {"is_error": True, "terminal_reason": "api_error", "result": CF_TEXT, "session_id": "sx"}
    check("a Cloudflare death is the account's transient, not a dead login", RL.account_death(res) == "cloudflare")
    rec, why = RL.resume_record(dict(run_, tokens=5000), res, "cloudflare", NOW, {})
    check("a Cloudflare death after work resumes after a short wait", rec is not None and 0 < rec["due"] - NOW <= 300)
    rec2, why2 = RL.resume_record(dict(run_, tokens=5000, resume_of="u0", resume_n=1, resume_error="cloudflare"), res,
                                  "cloudflare", NOW, {})
    check("only once: a second Cloudflare death is not resumed", rec2 is None and "once" in why2)
    rs = {"runs": [run_]}
    keep = RL.unlaunch
    try:
        RL.unlaunch = lambda rs, unit: True
        check("a no-work Cloudflare death gives its slot back", RL.auth_failed_back(rs, run_, "API Error: 403 Attention Required! | Cloudflare", NOW))
    finally:
        RL.unlaunch = keep


def main():
    for t in (test_dead_held, test_blip, test_switch, test_stranded, test_stranded_reader, test_limit_reset, test_quiet_and_gate, test_slot_back, test_alarm_run_retried_after_login_heals,
              test_probe, test_bad_usage_file, test_pick_and_way, test_give_back, test_release,
              test_overnight_conductor_cloudflare, test_poke_release, test_poke_wire, test_cloudflare_role_runs):
        t()
    print("selftest_login_watch: %s" % ("FAILED %d" % len(FAILS) if FAILS else "OK"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
