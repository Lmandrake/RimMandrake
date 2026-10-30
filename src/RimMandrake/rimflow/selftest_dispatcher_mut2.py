#!/usr/bin/env python3
"""selftest_dispatcher_mut2.py - second batch of tests written FROM the mutation survivors of dispatcher.py (item
DISPATCHER_HARDEN_MUTATION_SURVIVORS, run 20261028T013440 @113efcd97d: 380 alive). Pins the small observers whose
exact argv, state strings, boundaries and return shapes nothing asserted: observe_agents, window_live, caps_ok,
ledger_note, publish_bounded, default_obs. Loaded by selftest_dispatcher_mut.main() through TESTS."""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import selftest_dispatcher as T  # noqa: E402
from selftest_dispatcher import D, check, fresh, sched  # noqa: E402
import doorbell  # noqa: E402

NOW = 1_800_000_000.0


class FakeProc:
    def __init__(self, rc=0, out="", err=""):
        self.returncode, self.stdout, self.stderr = rc, out, err


def with_run(fn, body):
    real = subprocess.run
    subprocess.run = fn
    try:
        return body()
    finally:
        subprocess.run = real


def test_observe_agents():
    seen = {}

    def ok(argv, **kw):
        seen["argv"], seen["kw"] = argv, kw
        return FakeProc(0, '[{"name": "a"}]')
    r = with_run(ok, lambda: D.observe_agents())
    check(r == {"state": "MEASURED", "sessions": [{"name": "a"}]}, "measured shape: %r" % r)
    check(seen["argv"][1:] == ["agents", "--json"], "argv %r" % seen["argv"])
    kw = seen["kw"]
    check(kw.get("timeout") == 60 and kw.get("capture_output") is True and kw.get("text") is True
          and kw.get("stdin") == subprocess.DEVNULL, "run kwargs %r" % kw)
    with_run(ok, lambda: D.observe_agents(timeout=7))
    check(seen["kw"]["timeout"] == 7, "timeout passed through")
    r = with_run(lambda a, **k: FakeProc(3, "", "x" * 300 + "boom"), lambda: D.observe_agents())
    check(r["state"] == "UNMEASURED" and r["why"] == "claude agents exit 3: " + ("x" * 156) + "boom",
          "exit text keeps the last 160 chars: %r" % r)
    r = with_run(lambda a, **k: FakeProc(0, "{}"), lambda: D.observe_agents())
    check(r == {"state": "UNMEASURED", "why": "claude agents --json is not a list of session objects"}, "not a list: %r" % r)
    r = with_run(lambda a, **k: FakeProc(0, "[1]"), lambda: D.observe_agents())
    check(r["state"] == "UNMEASURED", "list of non-objects is unmeasured: %r" % r)
    r = with_run(lambda a, **k: FakeProc(0, "not json"), lambda: D.observe_agents())
    check(r["state"] == "UNMEASURED" and r["why"].startswith("JSONDecodeError: "), "bad json: %r" % r)

    def boom(argv, **kw):
        raise OSError("e" * 300)
    r = with_run(boom, lambda: D.observe_agents())
    check(r == {"state": "UNMEASURED", "why": "OSError: " + "e" * 160}, "exception text cut at 160: %r" % r)


def test_window_live():
    real = D.observe_agents
    try:
        D.observe_agents = lambda: {"state": "UNMEASURED", "why": "nope"}
        check(D.window_live("w") == (None, "nope"), "unreadable passes its why")
        D.observe_agents = lambda: {"state": "UNMEASURED"}
        check(D.window_live("w") == (None, "claude agents unreadable"), "default why")
        D.observe_agents = lambda: {"state": "MEASURED", "sessions": [{"session_name": "w", "name": "w", "sessionId": "S1", "status": "busy"},
                                                                       {"name": "z", "sessionId": "S2"}]}
        check(D.window_live("w") == (True, "session S1 is busy"), "found: %r" % (D.window_live("w"),))
        check(D.window_live("q") == (False, ""), "absent")
        D.observe_agents = lambda: {"state": "MEASURED", "sessions": [{"name": "w"}]}
        check(D.window_live("w") == (True, "session ? is ?"), "defaults: %r" % (D.window_live("w"),))
    finally:
        D.observe_agents = real


def test_caps_ok():
    sch = sched()
    c = sch["caps"]
    h, d, g = c["wakes_per_seat_hour"], c["wakes_per_seat_day"], c["wakes_per_day"]

    def st_with(ages, seat="A"):
        s = fresh()
        s["wakes"] = [{"seat": seat, "at": NOW - a} for a in ages]
        return s
    check(D.caps_ok(st_with([]), sch, "A", NOW) == (True, ""), "no wakes: ok with empty reason")
    # hour cap: h wakes inside the hour trips, one at exactly 3600 s does not count
    check(D.caps_ok(st_with([3599] * h), sch, "A", NOW) == (False, "cap: %d wakes/hour for A" % h), "hour cap")
    check(D.caps_ok(st_with([3599] * (h - 1) + [3600]), sch, "A", NOW)[1] != "cap: %d wakes/hour for A" % h, "3600 s is outside the hour")
    check(D.caps_ok(st_with([3600] * h), sch, "A", NOW)[1] != "cap: %d wakes/hour for A" % h, "all at 3600 s: not hourly capped")
    # other seats do not count toward a seat's hour/day caps
    check(D.caps_ok(st_with([10] * h, seat="B"), sch, "A", NOW)[1] != "cap: %d wakes/hour for A" % h, "other seat not counted")
    # seat day cap (pick ages outside the hour so only the day rule can trip)
    ok, why = D.caps_ok(st_with([4000] * d), sch, "A", NOW)
    check(not ok and why == "cap: %d wakes/day for A" % d, "seat day cap: %r" % (why,))
    check(D.caps_ok(st_with([4000] * (d - 1)), sch, "A", NOW)[0] is True or d - 1 >= g, "one under the seat day cap passes")
    ok, why = D.caps_ok(st_with([86399] * d), sch, "A", NOW)
    check(not ok and why == "cap: %d wakes/day for A" % d, "86399 s still in the day: %r" % (why,))
    ok, why = D.caps_ok(st_with([86400] * d), sch, "A", NOW)
    check(ok and why == "", "exactly 86400 s is outside the day: %r" % (why,))
    ok, why = D.caps_ok(st_with([86400] * (d - 1) + [4000]), sch, "A", NOW)
    check(ok, "d-1 inside the day does not trip (> vs >=): %r" % (why,))
    # overall day cap: g wakes spread over other seats (each seat under its own caps)
    s = fresh()
    s["wakes"] = [{"seat": "S%d" % i, "at": NOW - 4000} for i in range(g)]
    ok, why = D.caps_ok(s, sch, "A", NOW)
    check(not ok and why == "cap: %d wakes/day overall" % g, "overall cap: %r" % (why,))
    s["wakes"].pop()
    check(D.caps_ok(s, sch, "A", NOW) == (True, ""), "one under the overall cap")
    s["wakes"] = [{"seat": "S%d" % i, "at": NOW - 86399} for i in range(g)]
    check(D.caps_ok(s, sch, "A", NOW)[1] == "cap: %d wakes/day overall" % g, "86399 s counts overall")
    s["wakes"] = [{"seat": "S%d" % i, "at": NOW - 86400} for i in range(g)]
    check(D.caps_ok(s, sch, "A", NOW) == (True, ""), "86400 s does not count overall")


def test_ledger_note():
    calls = []

    def fake(argv, **kw):
        calls.append((argv, kw))
        return FakeProc(0, "out-", "err")
    r = D.ledger_note("ITEM_X", "hello", run=fake)
    argv, kw = calls[0]
    check(r == (True, "out-err"), "ok shape %r" % (r,))
    check(argv == [sys.executable, os.path.join(D.HERE, "cli.py"), "note", "ITEM_X", "--text", "hello", "--seat", "DISPATCHER"], "argv %r" % argv)
    check(kw["cwd"] == D.REPO and kw["env"]["RIMFLOW_SEAT"] == "DISPATCHER" and kw["env"]["CLAUDE_PROJECT_DIR"] == D.REPO,
          "env/cwd")
    check(kw["capture_output"] is True and kw["text"] is True and kw["timeout"] == 120 and kw["stdin"] == subprocess.DEVNULL,
          "kwargs %r" % kw)
    check(os.path.isfile(argv[1]), "cli.py exists at the path used")
    r = D.ledger_note("I", "t", run=lambda a, **k: FakeProc(1, "a", "b"))
    check(r == (False, "ab"), "rc 1 -> False: %r" % (r,))
    r = D.ledger_note("I", "t", run=lambda a, **k: FakeProc(2, "a", "b"))
    check(r[0] is False, "rc 2 -> False")
    r = D.ledger_note("I", "t", run=lambda a, **k: FakeProc(0, None, None))
    check(r == (True, ""), "None streams -> empty: %r" % (r,))
    r = D.ledger_note("I", "t", run=lambda a, **k: FakeProc(0, None, "e"))
    check(r == (True, "e"), "None stdout: %r" % (r,))
    r = D.ledger_note("I", "t", run=lambda a, **k: FakeProc(0, "o", None))
    check(r == (True, "o"), "None stderr: %r" % (r,))
    r = D.ledger_note("I", "t", run=lambda a, **k: FakeProc(0, "  " + "x" * 150, "y" * 150 + "\n"))
    check(r[1] == ("x" * 50) + ("y" * 150), "tail 200 of the stripped text: %d" % len(r[1]))


def test_publish_bounded():
    py = sys.executable
    check(D.publish_bounded(1, 0).startswith("publish skipped"), "no budget skips")
    check(D.publish_bounded(1, -5).startswith("publish skipped"), "negative budget skips")
    r = D.publish_bounded(1, 30, argv=[py, "-c", "print('None')"])
    check(r is None, "child printing None -> None: %r" % (r,))
    r = D.publish_bounded(1, 30, argv=[py, "-c", "print('a'); print('b line')"])
    check(r == "b line", "last line returned: %r" % (r,))
    r = D.publish_bounded(1, 30, argv=[py, "-c", "pass"])
    check(r == "", "silent child -> empty string: %r" % (r,))
    r = D.publish_bounded(1, 30, argv=[py, "-c", "import sys; print('z'*300); sys.exit(4)"])
    check(r == "publish child exit 4: " + "z" * 200, "failed child: %r" % (r,))
    r = D.publish_bounded(1, 1, argv=[py, "-c", "import time; time.sleep(60)"])
    check(r == "publish KILLED after 1 s (tick budget; the commit stays local, the next tick retries)", "killed: %r" % (r,))
    # text mode: a str comes back (bytes mode would break .strip()/splitlines semantics)
    r = D.publish_bounded(1, 30, argv=[py, "-c", "print('é')"])
    check(isinstance(r, str), "text mode")
    # default argv: the module itself with `publish <n>` (a nonexistent command exits non-zero, shown)
    real = subprocess.Popen
    got = {}

    def fp(argv, **kw):
        got["argv"], got["kw"] = argv, kw
        return real([py, "-c", "print('None')"], **{k: v for k, v in kw.items() if k != "cwd"})
    subprocess.Popen = fp
    try:
        D.publish_bounded(7.9, 30)
    finally:
        subprocess.Popen = real
    check(got["argv"][1:] == [os.path.abspath(D.__file__), "publish", "7"], "default argv %r" % got["argv"])
    check(got["kw"]["cwd"] == D.REPO and got["kw"]["start_new_session"] is True, "popen kwargs")


def test_default_obs():
    saved = {k: getattr(D, k) for k in ("paused_now", "observe_agents", "peek_ticket", "seat_events_since", "consumed_ring", "role_obs", "_skip_journal")}
    real_rj, real_ap, real_sd = doorbell._read_json, doorbell.armed_path, doorbell.state_dir
    rec = []
    try:
        D.paused_now = lambda: "P"
        D.observe_agents = lambda: "AG"
        D.peek_ticket = lambda clone, seat: rec.append(("peek", clone, seat)) or "PK"
        D.seat_events_since = lambda clone, seat, since, on_skip=None: rec.append(("ev", clone, seat, since, on_skip)) or "EV"
        D.consumed_ring = lambda sd, seat, rid: rec.append(("cons", sd, seat, rid)) or "CO"
        D.role_obs = lambda s: "ROLES"
        D._skip_journal = lambda root, st: ("skip", root, st)
        doorbell.state_dir = lambda: "SD"
        doorbell.armed_path = lambda seat: "ARM-" + seat
        doorbell._read_json = lambda p: "J:" + p
        sch = {"seats": {"A": {"clone": "/c/a"}}}
        o = D.default_obs(sch, "ROOT", {"s": 1})
        check(o["paused"] == "P" and o["agents"] == "AG" and o["roles"] == "ROLES", "plain keys")
        check("owner" not in o and "peek_offline" not in o and not hasattr(D, "owner_reading")
              and o["alive"] is D.pid_alive, "no owner-presence observer (owner 2026-10-30); alive bound")
        check(o["peek"]("A") == "PK" and rec[-1] == ("peek", "/c/a", "A"), "peek: %r" % (rec[-1],))
        check(o["events"]("A", 5) == "EV" and rec[-1] == ("ev", "/c/a", "A", 5, ("skip", "ROOT", {"s": 1})), "events: %r" % (rec[-1],))
        check(o["consumed"]("A", "R1") == "CO" and rec[-1] == ("cons", "SD", "A", "R1"), "consumed: %r" % (rec[-1],))
        check(o["armed"]("A") == "J:ARM-A", "armed: %r" % (o["armed"]("A"),))
        check(o["seat_restart"] is None, "no seat_restart config -> None")
        o = D.default_obs({}, "ROOT")
        check(o["paused"] == "P", "no seats key is fine")
        o = D.default_obs({"seats": None}, "ROOT")
        check(o["armed"]("Q") == "J:ARM-Q", "seats None is fine")
    finally:
        for k, v in saved.items():
            setattr(D, k, v)
        doorbell._read_json, doorbell.armed_path, doorbell.state_dir = real_rj, real_ap, real_sd


TESTS = [test_observe_agents, test_window_live, test_caps_ok, test_ledger_note, test_publish_bounded, test_default_obs]

if __name__ == "__main__":
    for t in TESTS:
        t()
    print("%d failure(s)" % len(T.FAILS))
    sys.exit(1 if T.FAILS else 0)
