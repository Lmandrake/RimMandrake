#!/usr/bin/env python3
"""selftest_dispatcher_incident_bells.py -- the four Codex round-4 claims on dispatcher.py's incident path
(DISPATCHER_FIX_INCIDENT_BELLS_OVERWRITE), each driven red on its base before its fix:

  1. denied_runs: a Conductor-log failure after the refusal mark advanced lost the refusal for good; the mark is given
     back, so the next pass hands the same refusal on;
  2. incident_execute: two incident doorbells for one seat in one pass wrote one inbox file twice (the second
     destroyed the first); they go out as ONE ring carrying both texts;
  3. incident_execute: an incident doorbell carried no session, so a `claude -p` child that re-armed the seat's
     doorbell took it; it carries the seat window's session, as the ordinary ring does;
  4. execute: a ring's rung_at was the tick's start, before the ingest.lock wait, so a lease taken in that wait read
     as the ring's hand-off; rung_at/rung_iso are moved to the moment the ring was written.

Offline: the told ledger, inbox and Conductor log are doubles; nothing rings a real seat."""
import json
import os
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TMP = tempfile.mkdtemp(prefix="selftest_dispatcher_bells_")
os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "state")
os.environ["TESTQ_QUEUE"] = os.path.join(TMP, "testq")      # git_lock's ingest.lock: never the real queue
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import dispatcher as D  # noqa: E402
import schedule_fixture as SF  # noqa: E402

FAILS = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def stub_ledger():
    saved = {k: getattr(D.IN, k) for k in ("read_rows", "write_snapshot", "append")}
    D.IN.write_snapshot = lambda snap: None
    D.IN.append = lambda rows: None
    D.IN.read_rows = lambda: []
    return saved


def pass_of(rings):
    return {"rows": [], "rings": rings, "cursor": 0, "snapshot": {}, "ring_hold": None}


def test_refusal_survives_a_log_failure():
    st = {"roles": {"Operations": {"run_now_last": {"by": "DISPATCHER", "ids": ["x-1"], "decided": 77.0,
                                                    "outcome": "refused: daily cap"}}}, "seats": {}}

    def boom(*a):
        raise OSError("conductor log dir unavailable")
    try:
        D.incident_execute(pass_of([]), {}, st, TMP, 100.0, lambda *a: None, boom)
        raised = None
    except OSError as e:
        raised = e
    check(raised is not None, "claim 1: the log failure still surfaces to execute (it records incident_failed)")
    told = []
    D.incident_execute(pass_of([]), {}, st, TMP, 101.0, lambda *a: None, lambda sc, x, n: told.append(x))
    check(len(told) == 1 and "refused" in told[0].get("why", ""),
          "claim 1: once the log is back, the next pass hands the same refusal on: %r" % told)
    st["roles"]["Operations"]["run_now_last"]["decided"] = 78.0       # a second refusal, cut by the beat's end

    def cut(*a):
        raise D.StepCut("execute")
    try:
        D.incident_execute(pass_of([]), {}, st, TMP, 102.0, lambda *a: None, cut)
    except D.StepCut:
        pass
    told.clear()
    D.incident_execute(pass_of([]), {}, st, TMP, 103.0, lambda *a: None, lambda sc, x, n: told.append(x))
    check(len(told) == 1, "claim 1: a beat cut mid hand-off (StepCut) gives the mark back too: %r" % told)
    st["roles"]["Operations"]["run_now_last"]["decided"] = 79.0
    rr = D.IN.read_rows

    def cut_read():
        raise D.StepCut("execute")
    D.IN.read_rows = cut_read
    try:
        D.incident_execute(pass_of([]), {}, st, TMP, 104.0, lambda *a: None, lambda *a: None)
    except D.StepCut:
        pass
    D.IN.read_rows = rr
    told.clear()
    D.incident_execute(pass_of([]), {}, st, TMP, 105.0, lambda *a: None, lambda sc, x, n: told.append(x))
    check(len(told) == 1, "claim 1: a beat cut during the told.jsonl read gives the mark back too: %r" % told)


def test_two_bells_one_seat_one_ring():
    inbox, rings = {}, []

    def dr(root, seat, rid, msg, session_id=None):
        inbox[seat] = msg                      # one inbox file per seat, as doorbell.inbox_path
        rings.append(seat)
    st = {"roles": {}, "seats": {}}
    b1 = {"how": "doorbell", "seat": "BENCH", "id": "i-1", "text": "FIRST incident text"}
    b2 = {"how": "doorbell", "seat": "BENCH", "id": "i-2", "text": "SECOND incident text"}
    b3 = {"how": "doorbell", "seat": "FOUNDRY", "id": "i-3", "text": "OTHER seat text"}
    res = D.incident_execute(pass_of([b1, b2, b3]), {}, st, TMP, 100.0, dr, lambda *a: None)
    check(rings.count("BENCH") == 1, "claim 2: two bells for BENCH in one pass write its inbox once: %r" % rings)
    check("FIRST" in inbox.get("BENCH", "") and "SECOND" in inbox.get("BENCH", ""),
          "claim 2: neither bell's text is lost: %r" % inbox.get("BENCH"))
    check(inbox.get("FOUNDRY") == "OTHER seat text" and rings.count("FOUNDRY") == 1,
          "claim 2: a lone bell for another seat rings as before: %r" % inbox.get("FOUNDRY"))
    check("i-1" in res and "i-2" in res, "claim 2: the pass still reports both bells: %r" % res)
    inbox.clear()
    rings.clear()
    st = {"roles": {}, "seats": {}}

    def boom(*a):
        raise OSError("conductor log dir unavailable")
    quick = {"how": "quick_run", "id": "q-1", "text": "q"}
    try:
        D.incident_execute(pass_of([b1, quick]), {}, st, TMP, 100.0, dr, boom)
    except OSError:
        pass
    check(b1 in st["incident"].get("held", []),
          "claim 2: a later ring that raised leaves the unrung bell held, not lost: %r" % st["incident"].get("held"))


def test_bell_carries_the_window_session():
    got = []

    def dr(root, seat, rid, msg, session_id=None):
        got.append((seat, session_id))
    st = {"roles": {}, "seats": {"BENCH": {"session_id": "sid-window", "session_t": 100.0}}}
    D.incident_execute(pass_of([{"how": "doorbell", "seat": "BENCH", "id": "i-1", "text": "t"}]), {}, st, TMP, 100.0,
                       dr, lambda *a: None)
    check(got == [("BENCH", "sid-window")], "claim 3: the incident bell is addressed to BENCH's window session: %r" % got)
    got.clear()
    D.incident_execute(pass_of([{"how": "doorbell", "seat": "FOUNDRY", "id": "i-2", "text": "t"}]), {},
                       {"roles": {}, "seats": {}}, TMP, 101.0, dr, lambda *a: None)
    check(got == [("FOUNDRY", None)], "claim 3: no known session: the bell goes unaddressed, as before: %r" % got)
    got.clear()
    st = {"roles": {}, "seats": {"BENCH": {"session_id": "sid-old", "session_t": 50.0}}}
    D.incident_execute(pass_of([{"how": "doorbell", "seat": "BENCH", "id": "i-3", "text": "t"}]), {}, st, TMP, 102.0,
                       dr, lambda *a: None)
    check(got == [("BENCH", None)], "claim 3: a session not seen this tick (PAUSE skipped the refresh) is not trusted: %r"
          % got)
    st = {"seats": {}, "wakes": [], "recovers": [], "alarms": {}}
    D.decide(sched(), st, {"paused": None, "owner": None, "alive": lambda pid: True, "armed": lambda seat: {"pid": 1},
                           "agents": {"state": "MEASURED", "sessions": [{"name": "AGENT BENCH", "status": "busy",
                                      "sessionId": "sid-b", "kind": "interactive", "pid": 1}]},
                           "peek": lambda seat: None, "events": lambda seat, since: [], "consumed": lambda seat, rid: None},
             200.0, True)
    check((st["seats"].get("BENCH") or {}).get("session_t") == 200.0,
          "claim 3: decide stamps when it learned a seat's session: %r" % st["seats"].get("BENCH"))
    st = {"seats": {"BENCH": {"session_id": "old", "session_t": 100.0}}, "wakes": [], "recovers": [], "alarms": {}}
    D.decide(sched(), st, {"paused": None, "owner": None, "alive": lambda pid: True, "armed": lambda seat: {"pid": 1},
                           "agents": {"state": "MEASURED", "sessions": [{"name": "AGENT BENCH", "status": "busy",
                                      "kind": "interactive", "pid": 1}]},
                           "peek": lambda seat: None, "events": lambda seat, since: [], "consumed": lambda seat, rid: None},
             300.0, True)
    check((st["seats"].get("BENCH") or {}).get("session_t") != 300.0,
          "claim 3: a session read with no id does not certify the stored one fresh: %r" % st["seats"].get("BENCH"))


def sched():
    path = os.path.join(TMP, "sched.json")
    clone = os.path.join(TMP, "clone")
    with open(path, "w") as f:
        json.dump(SF.fill({"seats": {"FOUNDRY": {"enabled": True, "wake": True, "session_name": "AGENT FOUNDRY",
                                                 "clone": clone},
                                     "BENCH": {"enabled": True, "wake": False, "session_name": "AGENT BENCH",
                                               "clone": clone}},
                           "roles": [], "alarm_item": "DISPATCHER_ALARMS_X", "publish": True,
                           "no_handoff": {"conductor_log": os.path.join(TMP, "conductor_log.md")}}), f)
    return D.load_schedule(path)


def test_rung_at_is_the_ring_moment():
    sch = sched()
    now = time.time()
    st = {"seats": {"FOUNDRY": {"ring": {"ring_id": "FOUNDRY-1-1", "rung_at": now, "rung_iso": D.iso(now),
                                         "ticket": "T", "attempt": 1}}}, "wakes": [], "recovers": [], "alarms": {}}
    rung = []

    def slow_lock():
        time.sleep(1.2)                        # the ingest.lock wait between decide and the ring
        return None
    act = {"do": "ring", "seat": "FOUNDRY", "ring_id": "FOUNDRY-1-1", "ticket": "T", "attempt": 1,
           "session_id": "sid-1", "message": "m", "at": D.iso(now)}
    D.execute([act], sch, st, os.path.join(TMP, "root"), True, now,
              {"lock": slow_lock, "publish": lambda n: "p", "paused": lambda: None,
               "ring": lambda root, seat, rid, msg, sid=None: rung.append(rid), "persist": lambda: None})
    pend = st["seats"]["FOUNDRY"].get("ring") or {}
    check(rung == ["FOUNDRY-1-1"], "claim 4: the ring went out: %r" % rung)
    check(pend.get("rung_at", now) >= now + 1 and pend.get("rung_iso") != D.iso(now),
          "claim 4: rung_at/rung_iso are the ring's moment, after the lock wait: %r (tick start %r)" % (pend, now))
    # the live tick passes its real clock: observation and decide time before execute count too (Codex review)
    t = 1000.0
    st = {"seats": {"FOUNDRY": {"ring": {"ring_id": "FOUNDRY-2-1", "rung_at": t, "rung_iso": D.iso(t),
                                         "ticket": "T", "attempt": 1}}}, "wakes": [], "recovers": [], "alarms": {}}
    D.execute([dict(act, ring_id="FOUNDRY-2-1", at=D.iso(t))], sch, st, os.path.join(TMP, "root"), True, t,
              {"lock": lambda: None, "publish": lambda n: "p", "paused": lambda: None,
               "ring": lambda root, seat, rid, msg, sid=None: rung.append(rid), "persist": lambda: None},
              ring_clock=lambda: t + 12)
    pend = st["seats"]["FOUNDRY"].get("ring") or {}
    check(pend.get("rung_at") == t + 12 and pend.get("rung_iso") == D.iso(t + 12),
          "claim 4: with the tick's clock, rung_at is the write's moment (12 s of observation, no lock wait): %r" % pend)
    st = {"seats": {"FOUNDRY": {"ring": {"ring_id": "FOUNDRY-4-1", "rung_at": 1000.9, "rung_iso": D.iso(1000.9),
                                         "ticket": "T", "attempt": 1}}}, "wakes": [], "recovers": [], "alarms": {}}
    D.execute([dict(act, ring_id="FOUNDRY-4-1", at=D.iso(1000.9))], sch, st, os.path.join(TMP, "root"), True, 1000.9,
              {"lock": lambda: None, "publish": lambda n: "p", "paused": lambda: None,
               "ring": lambda root, seat, rid, msg, sid=None: rung.append(rid), "persist": lambda: None},
              ring_clock=lambda: 1001.1)
    check((st["seats"]["FOUNDRY"].get("ring") or {}).get("rung_iso") == D.iso(1001.1),
          "claim 4: a sub-second wait across a second boundary moves rung_iso too: %r" % st["seats"]["FOUNDRY"].get("ring"))
    import inspect
    src = inspect.getsource(D.tick)
    check('{"ring_clock": ring_clock}' in src and "fx = dict(" not in src,
          "claim 4: the live clock reaches execute as its own argument, never in fx (an empty fx is the live owed-sources sync)")
    st = {"seats": {"FOUNDRY": {"ring": {"ring_id": "FOUNDRY-3-1", "rung_at": t, "rung_iso": D.iso(t),
                                         "ticket": "T", "attempt": 1}}}, "wakes": [], "recovers": [], "alarms": {}}
    D.execute([dict(act, ring_id="FOUNDRY-3-1", at=D.iso(t))], sch, st, os.path.join(TMP, "root"), True, t,
              {"lock": lambda: None, "publish": lambda n: "p", "paused": lambda: None,
               "ring": lambda root, seat, rid, msg, sid=None: rung.append(rid), "persist": lambda: None})
    check((st["seats"]["FOUNDRY"].get("ring") or {}).get("rung_at") == t,
          "claim 4: a simulated clock with no wait keeps decide's stamp: %r" % st["seats"]["FOUNDRY"].get("ring"))


def main():
    saved = stub_ledger()
    try:
        for t in (test_refusal_survives_a_log_failure, test_two_bells_one_seat_one_ring,
                  test_bell_carries_the_window_session, test_rung_at_is_the_ring_moment):
            try:
                t()
            except Exception as e:  # noqa: BLE001 -- a crash is a failing case, named
                check(False, "%s crashed: %s: %s" % (t.__name__, type(e).__name__, e))
    finally:
        for k, v in saved.items():
            setattr(D.IN, k, v)
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
