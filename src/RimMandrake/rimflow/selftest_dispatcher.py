#!/usr/bin/env python3
"""selftest_dispatcher.py — RimFlow v3.0 Dispatcher (dispatcher.py) and its wake channel (doorbell.py).

Covers the §6 acceptance list with SIMULATED windows (no real Claude window is started here):
  wake an idle window      decide() rings; a real doorbell.wait() in a thread (the simulated window) is woken, takes a
                           lease in its fake clone's shard, and the next tick VERIFIES the hand-off and notes it
  recover a dead one       a seat missing from `claude agents` is resumed (fake runner sees `--resume <session>` and
                           AGENT_SEAT), and the next tick sees it back
  never take the game      a bridge/game-up/deploy ticket is HELD while the owner is present or UNMEASURED; every
                           other ring carries the "owner present" line; the dispatcher has no game call at all
plus retry/give-up, caps, PAUSE, blind instrument, dry-run writes nothing, doorbell supersede/orphan, and the
DISPATCHER seat's ledger rule (note only). Nothing outside a temp dir is touched.
"""
import json
import os
import subprocess
import sys
import tempfile
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TMP = tempfile.mkdtemp(prefix="selftest_dispatcher_")
os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "state")
os.environ["TESTQ_QUEUE"] = os.path.join(TMP, "testq")      # git_lock's ingest.lock: never the real queue
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import dispatcher as D  # noqa: E402
import doorbell  # noqa: E402
from rimflow import model  # noqa: E402

FAILS = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def sched(**kw):
    clone = os.path.join(TMP, "clone")
    s = {"seats": {"FOUNDRY": {"enabled": True, "wake": True, "recover_dead": True, "session_name": "AGENT FOUNDRY",
                               "clone": clone, "model": "sonnet"},
                   "BENCH": {"enabled": True, "wake": False, "session_name": "AGENT BENCH", "clone": clone}},
         "roles": [{"name": "Arbiter", "enabled": False}], "alarm_item": "DISPATCHER_ALARMS_X"}
    s.update(kw)
    path = os.path.join(TMP, "sched.json")
    with open(path, "w") as f:
        json.dump(s, f)
    return D.load_schedule(path)


def sess(name="AGENT FOUNDRY", status="idle", sid="sid-1"):
    return {"name": name, "status": status, "sessionId": sid, "kind": "interactive", "pid": 1}


IDLE_OWNER = {"state": "MEASURED", "idle_seconds": 3600, "foreground": "x", "rimworld_foreground": False}
PRESENT = {"state": "MEASURED", "idle_seconds": 30, "foreground": "RimWorldWin64", "rimworld_foreground": True}
BLIND = {"state": "UNMEASURED", "idle_seconds": None, "why": "test"}


def obs(sessions=None, owner=IDLE_OWNER, ticket=None, armed=True, events=(), consumed=None, agents_ok=True,
        paused=None):
    return {"paused": paused,
            "agents": {"state": "MEASURED", "sessions": sessions if sessions is not None
                       else [sess(), sess("AGENT BENCH", "busy", "b")]}
            if agents_ok else {"state": "UNMEASURED", "why": "x"},
            "owner": lambda: owner,
            "peek": lambda seat: {"id": "SOME_ITEM_DO_IT", "needs": "offline"} if ticket is None else ticket,
            "events": lambda seat, since: [e for e in events if e.get("ts", "") >= since],
            "consumed": lambda seat, rid: consumed,
            "armed": lambda seat: {"pid": 4242} if armed else None,
            "alive": lambda pid: True}


def kinds(acts):
    return [a["do"] for a in acts]


def stall(sch, st, o, t0=1000.0):
    """Two observations a stall window apart -> the actions of the second."""
    D.decide(sch, st, o, t0, True)
    return D.decide(sch, st, o, t0 + sch["stall_after_s"], True)


def test_parse_peek():
    out = ("(game UP, bridge free)  [peek: recorded game state, not measured]\n"
           "RECONCILE MINERALS_WHERE_THEY_BELONG_1: commits b5b48cf8e\n"
           "MINERALS_WHERE_THEY_BELONG_1   doing  row -  needs owner  target v1\nDesign (later): x\n")
    check(D.parse_peek(out) == {"id": "MINERALS_WHERE_THEY_BELONG_1", "needs": "owner"}, "peek: first item line parsed")
    check(D.parse_peek("ROAST_STICK_FIX_IT   ready  BLOCKED  row 3  needs bridge  target v1") ==
          {"id": "ROAST_STICK_FIX_IT", "needs": "bridge"}, "peek: needs read past BLOCKED/row")
    check(D.parse_peek("(game UP)\nnothing ready for FOUNDRY\n") == {}, "peek: empty queue -> {}")
    check(D.OPEN_STATES == model.OPEN_STATES, "peek: OPEN_STATES pinned to model.OPEN_STATES")


def test_wake_and_owner():
    sch = sched()
    st = D.load_state(os.path.join(TMP, "s1"))
    check(kinds(D.decide(sch, st, obs(), 1000.0, True)) == [], "idle under the stall window: nothing")
    st = {"seats": {}, "wakes": [], "recovers": [], "alarms": {}}
    acts = stall(sch, st, obs())
    r = [a for a in acts if a["do"] == "ring"]
    check(len(r) == 1 and r[0]["seat"] == "FOUNDRY" and "owner present" not in r[0]["message"]
          and "cli.py next --seat FOUNDRY" in r[0]["message"], "stalled + work + owner idle: ring FOUNDRY, no owner line")
    check(not any(a.get("seat") == "BENCH" for a in acts), "BENCH (wake false) is never rung")
    check(st["seats"]["FOUNDRY"]["ring"]["ticket"] == "SOME_ITEM_DO_IT", "ring is pending verification")

    st = {"seats": {}, "wakes": [], "recovers": [], "alarms": {}}
    r = [a for a in stall(sch, st, obs(owner=PRESENT)) if a["do"] == "ring"]
    check(len(r) == 1 and "owner present: do not take the bridge" in r[0]["message"],
          "owner present + offline ticket: ring carries the owner-present line")
    for need in D.GAME_NEEDS:
        for who, rd in (("present", PRESENT), ("UNMEASURED", BLIND)):
            st = {"seats": {}, "wakes": [], "recovers": [], "alarms": {}}
            acts = stall(sch, st, obs(owner=rd, ticket={"id": "GAME_THING_DO_IT", "needs": need}))
            check(kinds(acts) == ["hold"], "ticket needs %s, owner %s: HELD, not rung" % (need, who))
    st = {"seats": {}, "wakes": [], "recovers": [], "alarms": {}}
    check("ring" in kinds(stall(sch, st, obs(ticket={"id": "GAME_THING_DO_IT", "needs": "bridge"}))),
          "ticket needs bridge, owner MEASURED idle 60 min: rung")
    st = {"seats": {}, "wakes": [], "recovers": [], "alarms": {}}
    check(kinds(stall(sch, st, obs(ticket={}))) == [], "empty queue: an idle window is left alone")
    st = {"seats": {}, "wakes": [], "recovers": [], "alarms": {}}
    a = stall(sch, st, obs(armed=False))
    check(kinds(a) == ["alarm"] and a[0]["kind"] == "unwakeable:FOUNDRY", "no doorbell armed: UNWAKEABLE alarm")
    st = {"seats": {}, "wakes": [], "recovers": [], "alarms": {}}
    check(kinds(stall(sch, st, obs(sessions=[sess(status="busy")]))) == [], "busy window: nothing")
    code = open(os.path.join(HERE, "dispatcher.py")).read().split('"""', 2)[2]     # the code, not the docstring
    check(not any(x in code for x in ('"bridge", "take"', 'cli, "bridge"', '"restart"', "./game", "game.py", "deploy_custom_mods", "refresh.py")),
          "the dispatcher has no bridge/game/deploy call of its own")


def test_blind_pause_roles_caps():
    sch = sched()
    st = {"seats": {}, "wakes": [], "recovers": [], "alarms": {}}
    check(kinds(D.decide(sch, st, obs(agents_ok=False), 1000.0, True)) == ["skip"] and not st["seats"],
          "claude agents UNMEASURED: skip, nothing decided")
    check(kinds(D.decide(sch, st, obs(paused="owner said stop"), 1000.0, True)) == ["skip"], "PAUSE file: skip")
    sch2 = sched(roles=[{"name": "Auditor", "enabled": True}])
    st = {"seats": {}, "wakes": [], "recovers": [], "alarms": {}}
    check("alarm" in kinds(D.decide(sch2, st, obs(), 1000.0, True)), "an enabled role in v3.0: alarm, not run")
    st = {"seats": {}, "wakes": [{"seat": "FOUNDRY", "at": 900.0 + i} for i in range(3)], "recovers": [],
          "alarms": {}}
    a = stall(sch, st, obs())
    check(kinds(a) == ["alarm"] and "wakes/hour" in a[0]["why"], "3 wakes this hour: capped")
    st = {"seats": {}, "wakes": [{"seat": "X", "at": 900.0}] * 80, "recovers": [], "alarms": {}}
    check(kinds(stall(sch, st, obs())) == ["alarm"], "80 wakes today overall: capped")


def test_verify_retry():
    sch = sched()
    st = {"seats": {}, "wakes": [], "recovers": [], "alarms": {}}
    stall(sch, st, obs())
    p = st["seats"]["FOUNDRY"]["ring"]
    t = p["rung_at"]
    check(kinds(D.decide(sch, st, obs(), t + 60, True)) == [], "ring in flight, not consumed yet: wait")
    lease = {"seat": "FOUNDRY", "event": "lease", "action": "take", "id": "SOME_ITEM_DO_IT", "ts": D.iso(t + 70)}
    a = D.decide(sch, st, obs(consumed={"consumed_at": t + 5}, events=[lease]), t + 120, True)
    check(kinds(a) == ["verified"] and a[0]["note"] and a[0]["ticket"] == "SOME_ITEM_DO_IT",
          "consumed + lease take after the ring: VERIFIED, noted on the item")
    old = dict(lease, ts=D.iso(t - 500))
    st = {"seats": {}, "wakes": [], "recovers": [], "alarms": {}}
    stall(sch, st, obs())
    t = st["seats"]["FOUNDRY"]["ring"]["rung_at"]
    check(kinds(D.decide(sch, st, obs(consumed={"consumed_at": t + 5}, events=[old]), t + 120, True)) == [],
          "a lease from BEFORE the ring is not a hand-off")
    a = D.decide(sch, st, obs(consumed={"consumed_at": t + 5}, events=[old]), t + sch["handoff_s"], True)
    check(kinds(a) == ["woke_no_handoff"], "consumed, no hand-off in handoff_s: WOKE_NO_HANDOFF (partial)")

    st = {"seats": {}, "wakes": [], "recovers": [], "alarms": {}}
    now = 1000.0
    D.decide(sch, st, obs(), now, True)
    seen = []
    for _ in range(40):
        now += 60
        seen += kinds(D.decide(sch, st, obs(), now, True))
    check(seen.count("ring") == sch["max_retries"] + 1 and seen.count("withdraw") == sch["max_retries"] + 1
          and seen.count("alarm") == 1, "never consumed: withdrawn + retried %d times, then one alarm (%s)"
          % (sch["max_retries"], seen))
    check(st["seats"]["FOUNDRY"].get("cooldown_until", 0) > now - 3600, "give-up starts a cooldown")


def test_dead_recover():
    sch = sched()
    st = {"seats": {}, "wakes": [], "recovers": [], "alarms": {}}
    D.decide(sch, st, obs(), 1000.0, True)
    check(st["seats"]["FOUNDRY"]["session_id"] == "sid-1", "session id remembered")
    gone = [sess("AGENT BENCH", "busy", "b")]
    check(kinds(D.decide(sch, st, obs(sessions=gone), 1100.0, True)) == [], "just vanished: wait dead_after_s")
    a = D.decide(sch, st, obs(sessions=gone), 1100.0 + sch["dead_after_s"], True)
    check(kinds(a) == ["recover"] and a[0]["session_id"] == "sid-1", "dead for dead_after_s: recover its session")
    a = D.decide(sch, st, obs(sessions=[sess(status="busy", sid="sid-1")]), 1800.0, True)
    check(kinds(a) == ["recovered"], "session back: RECOVERED")
    st2 = json.loads(json.dumps(st))
    D.decide(sch, st2, obs(sessions=gone), 2000.0, True)
    D.decide(sch, st2, obs(sessions=gone), 2000.0 + sch["dead_after_s"], True)
    a = D.decide(sch, st2, obs(sessions=gone), 2000.0 + sch["dead_after_s"] + sch["recover_verify_s"], True)
    check(kinds(a) == ["alarm"] and a[0]["kind"] == "recover:FOUNDRY", "recover that brings nothing back: alarm")
    sch_off = sched()
    sch_off["seats"]["FOUNDRY"]["recover_dead"] = False
    st = {"seats": {}, "wakes": [], "recovers": [], "alarms": {}}
    D.decide(sch_off, st, obs(), 1000.0, True)
    D.decide(sch_off, st, obs(sessions=gone), 1100.0, True)
    a = D.decide(sch_off, st, obs(sessions=gone), 1100.0 + sch["dead_after_s"], True)
    check(kinds(a) == ["alarm"], "recovery off: alarm only")

    calls = []

    class R:
        returncode, stdout, stderr = 0, "started", ""

    def runner(argv, **kw):
        calls.append((argv, kw))
        return R()
    ok, _ = D.recover(dict(sch["seats"]["FOUNDRY"], seat="FOUNDRY"), "sid-1", "hello", runner=runner)
    argv, kw = calls[0]
    check(ok and "--bg" in argv and argv[argv.index("--resume") + 1] == "sid-1" and argv[-1] == "hello"
          and kw["cwd"] == sch["seats"]["FOUNDRY"]["clone"] and kw["env"]["AGENT_SEAT"] == "FOUNDRY",
          "recover argv: claude --bg --resume <session> in the seat's clone as AGENT_SEAT")
    # The seat windows' real launch line (install_wt_seat_profiles.LAUNCH), minus the shell quoting, must be inside
    # the recover argv, run through the seat clone's claude_bounded.sh (memory scope, out of the oneshot cgroup).
    sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
    import install_wt_seat_profiles as W
    clone = sch["seats"]["FOUNDRY"]["clone"]
    launch = W.LAUNCH.format(script=W.BOUNDED.format(home=clone), label="AGENT FOUNDRY",
                             model="sonnet").replace("'AGENT FOUNDRY'", "AGENT_FOUNDRY").split()
    launch = [x.replace("AGENT_FOUNDRY", "AGENT FOUNDRY") for x in launch]
    rest = [x for x in argv if x not in ("--bg", "--resume", "sid-1", "hello")]
    check(rest == launch, "recover argv is the seat launcher's own line + --bg --resume (%s vs %s)" % (rest, launch))


def test_never_adopt_or_resume_a_stranger():
    sch = sched()
    st = {"seats": {}, "wakes": [], "recovers": [], "alarms": {}}
    owners = [{"name": "EMERGENCY", "status": "idle", "sessionId": "OWNER-SID", "kind": "interactive", "pid": 9,
               "cwd": sch["seats"]["FOUNDRY"]["clone"]}, sess("AGENT BENCH", "busy", "b")]
    for t in (1000.0, 1000.0 + sch["dead_after_s"] + 1, 1000.0 + 2 * sch["dead_after_s"]):
        a = D.decide(sch, st, obs(sessions=owners), t, True)
        check(not any(x["do"] in ("ring", "recover") for x in a), "an unnamed window in the seat's clone: never "
              "adopted, rung or resumed (%s)" % kinds(a))
    check(st["seats"]["FOUNDRY"].get("session_id") != "OWNER-SID", "its session id is never remembered")
    # recovered only when the RESUMED session is back, not any window with the name
    st = {"seats": {}, "wakes": [], "recovers": [], "alarms": {}}
    gone = [sess("AGENT BENCH", "busy", "b")]
    D.decide(sch, st, obs(), 1000.0, True)
    D.decide(sch, st, obs(sessions=gone), 1100.0, True)
    a = D.decide(sch, st, obs(sessions=gone, owner=PRESENT), 1100.0 + sch["dead_after_s"], True)
    check(kinds(a) == ["recover"] and "owner present: do not take the bridge" in a[0]["message"],
          "recover while the owner is present: the resumed session is told not to take the game")
    a = D.decide(sch, st, obs(sessions=[sess(sid="other")]), 1100.0 + sch["dead_after_s"] + 60, True)
    check("recovered" not in kinds(a), "another session under the seat's name is not the recovered one")


def test_review_fixes():
    sch = sched()
    # armed doorbell of another session: no ring
    st = {"seats": {}, "wakes": [], "recovers": [], "alarms": {}}
    o = obs()
    o["armed"] = lambda seat: {"pid": 4242, "session_id": "a-claude-p-child"}
    a = stall(sch, st, o)
    check(kinds(a) == ["alarm"] and "not ringing a stranger" in a[0]["why"],
          "doorbell armed by another session (claude -p child): alarm, no ring")
    o["armed"] = lambda seat: {"pid": 4242, "session_id": "sid-1"}
    a = stall(sch, {"seats": {}, "wakes": [], "recovers": [], "alarms": {}}, o)
    check([x for x in a if x["do"] == "ring"][0]["session_id"] == "sid-1", "the ring names the observed session")
    # PAUSE withdraws a ring still in an inbox
    st = {"seats": {}, "wakes": [], "recovers": [], "alarms": {}}
    stall(sch, st, obs())
    a = D.decide(sch, st, obs(paused="stop"), 2000.0, True)
    check(kinds(a) == ["skip", "withdraw"] and "ring" not in st["seats"]["FOUNDRY"], "PAUSE withdraws a queued ring")
    # a hand-off in the same second as the ring is not after it
    st = {"seats": {}, "wakes": [], "recovers": [], "alarms": {}}
    stall(sch, st, obs())
    p = st["seats"]["FOUNDRY"]["ring"]
    sc = os.path.join(TMP, "sameclone")
    sh = os.path.join(sc, "infrastructure", "state", "ledger", "events", "FOUNDRY.jsonl")
    os.makedirs(os.path.dirname(sh), exist_ok=True)
    with open(sh, "w") as f:
        f.write(json.dumps({"seat": "FOUNDRY", "event": "claim", "id": "X_Y", "ts": p["rung_iso"]}) + "\n")
    check(D.seat_events_since(sc, "FOUNDRY", p["rung_iso"]) == [],
          "an event stamped in the ring's own second is not a hand-off (it may predate the ring)")
    # busy during verification is not stall time; success resets the retry count
    st["seats"]["FOUNDRY"]["ring"]["attempt"] = 2
    st["seats"]["FOUNDRY"]["attempt"] = 1
    lease = {"seat": "FOUNDRY", "event": "lease", "action": "take", "id": "X_Y", "ts": D.iso(p["rung_at"] + 10)}
    busy = [sess(status="busy"), sess("AGENT BENCH", "busy", "b")]
    a = D.decide(sch, st, obs(sessions=busy, consumed={"consumed_at": 1}, events=[lease]), p["rung_at"] + 60, True)
    check(kinds(a) == ["verified"] and st["seats"]["FOUNDRY"]["attempt"] == 0
          and "idle_since" not in st["seats"]["FOUNDRY"], "verified: attempt reset, busy cleared idle_since")
    check(kinds(D.decide(sch, st, obs(), p["rung_at"] + 120, True)) == [],
          "idle again right after a busy verification: waits a full stall window, no immediate re-ring")
    # withdraw that lost the race to the doorbell keeps verifying, never rings twice
    st = {"seats": {}, "wakes": [], "recovers": [], "alarms": {}}
    root = os.path.join(TMP, "race")
    stall(sch, st, obs())
    p = dict(st["seats"]["FOUNDRY"]["ring"])
    a = D.decide(sch, st, obs(), p["rung_at"] + sch["verify_s"], True)
    D.execute(a, sch, st, root, True, p["rung_at"] + sch["verify_s"],
              {"withdraw": lambda *x: "gone (the doorbell took it)", "lock": lambda: None})
    check(st["seats"]["FOUNDRY"].get("ring", {}).get("ring_id") == p["ring_id"],
          "withdraw lost to the doorbell: the ring stays pending (delivered), no second ring")
    # a side effect that raises still saves the caps; the next ticks are capped
    sch3 = sched(caps={"wakes_per_seat_hour": 1})
    sch3["max_retries"] = 0
    boom = {"note": lambda i, t: (_ for _ in ()).throw(subprocess.TimeoutExpired("rimflow", 120)),
            "ring": lambda *x: None, "withdraw": lambda *x: "withdrawn", "publish": lambda n: "p", "lock": lambda: None}
    os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "state_boom")
    try:
        t0 = 10000.0
        D.tick(sch3, True, obs=obs(), now=t0, fx=boom)
        D.tick(sch3, True, obs=obs(), now=t0 + 240, fx=boom)
        rings = []
        for i in range(2, 12):
            rings += [x for x in D.tick(sch3, True, obs=obs(), now=t0 + 240 * i, fx=boom) if x["do"] == "ring"]
        st = D.load_state(D.state_root(True))
        check(len(st["wakes"]) == 1 and not rings, "caps survive a raising note: 1 wake/hour holds (%d extra rings)"
              % len(rings))
        with open(os.path.join(D.state_root(True), "state.json"), "w") as f:
            f.write("{torn")
        a = D.tick(sch3, True, obs=obs(), now=t0 + 9999, fx=boom)
        check(kinds(a) == ["skip"] and "UNREADABLE" in a[0]["why"], "unreadable state: skip (fail closed), not reset")
    finally:
        os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "state")
    # testq's ingest.lock busy: no ledger note (unstaged lines would break RUNNER's pull --rebase), journal says so
    noted = []
    acts = [{"do": "verified", "seat": "FOUNDRY", "ticket": "X_Y", "note": True, "ring_id": "r"}]
    D.execute(acts, sch, {"seats": {}, "wakes": [], "recovers": [], "alarms": {}}, os.path.join(TMP, "lk"), True,
              1.0, {"note": lambda i, t: noted.append(i) or (True, ""), "lock": lambda: None, "publish": lambda n: "p"})
    check(not noted and "ingest.lock busy" in acts[0]["ledger"], "ingest.lock busy: no note, journal records why")
    import testq
    testq.ensure_dirs()
    with open(testq.q("ingest.lock"), "w") as held:
        import fcntl
        fcntl.flock(held, fcntl.LOCK_EX)
        check(D.git_lock(wait_s=0) is None, "git_lock sees testq's ingest.lock held")
    lk = D.git_lock(wait_s=0)
    check(lk is not None, "git_lock takes a free ingest.lock")
    lk.close()


def test_doorbell():
    root = os.path.join(TMP, "bell")
    res = {}

    def window():
        res["r"] = doorbell.wait("FOUNDRY", "sid", root=root, max_wait=20, poll=0.05)
    th = threading.Thread(target=window)
    th.start()
    for _ in range(100):
        if os.path.exists(doorbell.armed_path("FOUNDRY", root)):
            break
        time.sleep(0.05)
    D.ring(root, "FOUNDRY", "R1", "wake up")
    th.join(10)
    check(res.get("r") == (2, "wake up") and not os.path.exists(doorbell.inbox_path("FOUNDRY", root)),
          "doorbell: a ring wakes the waiting hook (exit 2, message) and is consumed")
    check((D.consumed_ring(root, "FOUNDRY", "R1") or {}).get("consumed_at"), "consumed record is findable by ring id")
    D.ring(root, "FOUNDRY", "R9", "for another", session_id="other-session")
    code, _ = doorbell.wait("FOUNDRY", "sid", root=root, max_wait=0.3, poll=0.05)
    check(code == 0 and os.path.exists(doorbell.inbox_path("FOUNDRY", root)),
          "doorbell: a ring addressed to another session is left alone")
    os.remove(doorbell.inbox_path("FOUNDRY", root))
    import io
    saved = (doorbell.claude_ancestor, sys.stdin, os.environ.get("AGENT_SEAT"), os.environ["RM_DISPATCHER_STATE"])
    doorbell.claude_ancestor = lambda pid=None: None
    sys.stdin = io.StringIO('{"session_id": "s"}')
    os.environ["AGENT_SEAT"], os.environ["RM_DISPATCHER_STATE"] = "FOUNDRY", os.path.join(TMP, "noanc")
    try:
        code = doorbell.main()
    finally:
        doorbell.claude_ancestor, sys.stdin = saved[0], saved[1]
        if saved[2] is None:
            os.environ.pop("AGENT_SEAT", None)
        else:
            os.environ["AGENT_SEAT"] = saved[2]
        os.environ["RM_DISPATCHER_STATE"] = saved[3]
    check(code == 0 and not os.path.exists(doorbell.armed_path("FOUNDRY", os.path.join(TMP, "noanc"))),
          "doorbell with no Claude Code ancestor: exits 0 without arming (fail closed, no orphan)")
    check(not os.path.exists(doorbell.armed_path("FOUNDRY", root)), "doorbell disarms after a ring")

    def superseded():
        res["s"] = doorbell.wait("FOUNDRY", "sid", root=root, max_wait=20, poll=0.05)
    th = threading.Thread(target=superseded)
    th.start()
    time.sleep(0.3)
    doorbell._write_json_atomic(doorbell.armed_path("FOUNDRY", root), {"pid": -7})
    D.ring(root, "FOUNDRY", "R7", "for the newer doorbell")
    th.join(10)
    check(res.get("s", (None,))[0] == 0 and "superseded" in res["s"][1], "doorbell: a newer arm supersedes the old")
    check(os.path.exists(doorbell.inbox_path("FOUNDRY", root)),
          "doorbell: a superseded doorbell does not consume the newer one's ring")
    os.remove(doorbell.inbox_path("FOUNDRY", root))
    p = subprocess.Popen(["true"])
    p.wait()
    code, why = doorbell.wait("FOUNDRY", "sid", root=root, max_wait=20, poll=0.05, owner_pid=p.pid)
    check(code == 0 and "gone" in why, "doorbell: exits when its window process is gone (no orphan)")
    code, _ = doorbell.wait("FOUNDRY", "sid", root=root, max_wait=0, poll=0.05)
    check(code == 0, "doorbell: gives up at its deadline")
    D.ring(root, "FOUNDRY", "R2", "x")
    check(D.withdraw(root, "FOUNDRY", "R2") == "withdrawn" and not os.path.exists(doorbell.inbox_path("FOUNDRY", root)),
          "withdraw moves an unconsumed ring away")
    D.ring(root, "FOUNDRY", "R3", "x")
    check(D.withdraw(root, "FOUNDRY", "R2") == "not ours / gone", "withdraw never takes another ring")


def test_end_to_end():
    """A SIMULATED window: a real doorbell.wait() thread; when rung it takes a lease in its clone's shard."""
    clone = os.path.join(TMP, "clone")
    shard = os.path.join(clone, "infrastructure", "state", "ledger", "events", "FOUNDRY.jsonl")
    os.makedirs(os.path.dirname(shard), exist_ok=True)
    root = doorbell.state_dir()
    sch = sched()

    def window():
        code, msg = doorbell.wait("FOUNDRY", "sid-1", root=root, max_wait=30, poll=0.05, owner_pid=os.getpid())
        if code == 2 and "next --seat FOUNDRY" in msg:
            with open(shard, "a") as f:
                f.write(json.dumps({"seat": "FOUNDRY", "event": "lease", "action": "take", "id": "SOME_ITEM_DO_IT",
                                    "ts": D.iso(time.time() + 1)}) + "\n")
    th = threading.Thread(target=window)
    th.start()
    for _ in range(100):
        if os.path.exists(doorbell.armed_path("FOUNDRY", root)):
            break
        time.sleep(0.05)
    o = obs()
    o.update(armed=lambda seat: doorbell._read_json(doorbell.armed_path(seat, root)),
             alive=D.pid_alive,
             events=lambda seat, since: D.seat_events_since(clone, seat, since),
             consumed=lambda seat, rid: D.consumed_ring(root, seat, rid))
    notes, boom = [], []
    fx = {"note": lambda item, text: (notes.append((item, text)) or (True, "ok")),
          "publish": lambda n: "published %d" % n, "recover": lambda *a: boom.append(a) or (False, "")}
    now = time.time() - 1000
    D.tick(sch, True, obs=o, now=now, fx=fx)
    acts = D.tick(sch, True, obs=o, now=now + sch["stall_after_s"], fx=fx)
    check("ring" in kinds(acts), "e2e: the tick rang the idle simulated window")
    th.join(10)
    acts = D.tick(sch, True, obs=o, now=time.time() + 5, fx=fx)
    check(kinds(acts) == ["verified"], "e2e: next tick VERIFIED the hand-off (%s)" % kinds(acts))
    check(notes and notes[-1][0] == "SOME_ITEM_DO_IT", "e2e: the verified hand-off was noted on the item")
    jr = [json.loads(x) for x in open(os.path.join(root, "journal.jsonl"))]
    check(any(j["do"] == "publish" for j in jr) and all(j.get("message") is None for j in jr),
          "e2e: journal has the publish and no message bodies")
    check(not boom, "e2e: no recover")


def test_dry_run():
    root = doorbell.state_dir()
    sch = sched()
    called = []
    fx = {k: (lambda *a, **kw: called.append(a)) for k in ("ring", "withdraw", "recover", "note", "publish")}
    now = 5000.0
    D.tick(sch, False, obs=obs(), now=now, fx=fx)
    acts = D.tick(sch, False, obs=obs(), now=now + sch["stall_after_s"], fx=fx)
    check("ring" in kinds(acts) and not called, "dry-run: decides a ring, calls no side effect")
    check(all(a["result"].startswith("DRY") for a in acts), "dry-run: every result marked DRY")
    check(os.path.exists(os.path.join(root, "dry", "journal.jsonl")) and
          not os.path.exists(doorbell.inbox_path("FOUNDRY", os.path.join(root, "dry"))),
          "dry-run: bookkeeping under state/dry only, no inbox")
    st = D.load_state(os.path.join(root, "dry"))
    check("ring" not in st["seats"]["FOUNDRY"], "dry-run: no pending ring to 'verify'")


def test_alarm_rate():
    sch = sched()
    st = {"seats": {}, "wakes": [], "recovers": [], "alarms": {}}
    root = os.path.join(TMP, "alarm")
    noted = []
    fx = {"note": lambda i, t: noted.append(i) or (True, ""), "publish": lambda n: "p"}
    for t in (0.0, 60.0):
        D.execute([{"do": "alarm", "kind": "k", "why": "w", "note": True}], sch, st, root, True, t, fx)
    check(noted == ["DISPATCHER_ALARMS_X"], "an alarm is noted once per alarm_every_s, not every tick")


def test_seat_rule():
    base = [{"seat": "BENCH", "event": "file", "id": "SOME_ITEM_DO_IT", "title": "t", "kind": "task", "for": "FOUNDRY",
             "ts": "2026-10-26T00:00:00Z"}]
    note = {"seat": "DISPATCHER", "event": "note", "id": "SOME_ITEM_DO_IT", "text": "rung", "ts": "2026-10-26T00:01:00Z"}
    try:
        model.replay(base + [note], strict=True)
        ok = True
    except model.LedgerError:
        ok = False
    check(ok, "ledger: DISPATCHER may note any seat's item")
    claim = {"seat": "DISPATCHER", "event": "claim", "id": "SOME_ITEM_DO_IT", "ts": "2026-10-26T00:01:00Z"}
    try:
        model.replay(base + [claim], strict=True)
        msg = None
    except model.LedgerError as e:
        msg = str(e)
    check(msg is not None and "DISPATCHER" in msg, "ledger: DISPATCHER may not claim (%s)" % (msg or "accepted")[:80])
    for verb, extra in (("close", {"sha": "abc"}), ("start", {}), ("drop", {"reason": "x"}),
                        ("lease", {"action": "take", "token": "DISPATCHER.t1234", "expires": "2026-10-26T01:00:00Z"}),
                        ("bridge", {"state": "taken", "id": None}), ("file", {"title": "t", "kind": "task", "for": "BENCH"})):
        ev = dict({"seat": "DISPATCHER", "event": verb, "id": "SOME_ITEM_DO_IT" if verb != "file" else "NEW_ITEM_X",
                   "ts": "2026-10-26T00:01:00Z"}, **extra)
        try:
            model.replay(base + [ev], strict=True)
            msg = None
        except model.LedgerError as e:
            msg = str(e)
        check(msg is not None and "DISPATCHER" in msg, "ledger: DISPATCHER may not %s (%s)" % (verb, (msg or "accepted")[:60]))


def test_ringed_next_rechecks_owner():
    """DISPATCHER_HARDEN_OWNER_RETURN_AFTER_RING: the wake message says --ringed, and a ringed `next` withholds
    game-needing items (ranked and claimable) once the owner is back, while offline items still flow."""
    import types
    from rimflow import cli, idle_probe
    sch = sched()
    st = {"seats": {}, "wakes": [], "recovers": [], "alarms": {}}
    r = [a for a in stall(sch, st, obs()) if a["do"] == "ring"]
    check(r and "next --seat FOUNDRY --ringed" in r[0]["message"], "wake message tells the window to run next --ringed")
    A = lambda needs: types.SimpleNamespace(item=types.SimpleNamespace(id="X_" + needs, needs=needs, raised=None),
                                            kind="build")
    C = lambda needs: types.SimpleNamespace(id="C_" + needs, needs=needs, raised=None)
    saved = (cli.priority.rank, cli.reconcile.guard, cli._claimable, cli.reconcile.assess)
    try:
        cli.priority.rank = lambda *a, **k: [A("bridge"), A("deploy"), A("offline")]
        cli.reconcile.guard = lambda offers, idx: (offers, [])
        cli._claimable = lambda *a, **k: [C("game-up"), C("offline")]
        cli.reconcile.assess = lambda it, idx: types.SimpleNamespace(kind="build", item=it)
        args = types.SimpleNamespace(target=None)
        free = cli._choose(None, "FOUNDRY", args, {}, None)
        check(free["item"].id == "X_bridge", "no hold: game item offered first (control)")
        held = cli._choose(None, "FOUNDRY", args, {"hold_game": "owner back"}, None)
        check(held["kind"] == "offer" and held["item"].id == "X_offline", "owner back: first offer skips bridge/deploy")
        cli.priority.rank = lambda *a, **k: [A("bridge")]
        held = cli._choose(None, "FOUNDRY", args, {"hold_game": "owner back"}, None)
        check(held["kind"] == "claimable" and [c.id for c in held["claimable"]] == ["C_offline"],
              "owner back: claimable list drops game-up")
        cli._claimable = lambda *a, **k: [C("bridge")]
        held = cli._choose(None, "FOUNDRY", args, {"hold_game": "owner back"}, None)
        check(held["kind"] == "nothing", "owner back and only game work: nothing offered")
    finally:
        cli.priority.rank, cli.reconcile.guard, cli._claimable, cli.reconcile.assess = saved
    check(not idle_probe.idle_verdict(idle_probe.unmeasured("x"))[0], "UNMEASURED owner is not idle (so withheld)")


# ---------------------------------------------------------------- role launch (role_launch.py)
import role_launch as RL  # noqa: E402

DAY0 = time.mktime((2026, 10, 28, 0, 0, 0, 0, 0, -1))          # a local midnight


def at_local(hhmm, plus_s=60):
    return RL.slot_epoch(DAY0, hhmm) + plus_s


def ops_status(now, runway=2.0, week_left=40.0, m="MEASURED", age_s=300, alarms=None, acct="acct"):
    return {"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now - age_s)), "alarms": alarms or {},
            "points": {"accounts.%s.runway" % acct: {"m": m, "v": runway},
                       "accounts.%s.week_left_pct" % acct: {"m": m, "v": week_left}}}


def conductor(**kw):
    r = {"name": "Conductor", "enabled": True, "instructions": "src/RimMandrake/rimflow/roles/conductor.md",
         "seat": "BENCH", "clone": os.path.join(TMP, "clone"), "model": "sonnet", "ledger_item": "ROLES_ITEM_X",
         "off_file": os.path.join(TMP, "CONDUCTOR_OFF"), "quick_checks_local": ["08:00", "20:00"],
         "quick_token_cap": 30000, "daily_token_cap": 200000,
         "throttle_bands": {"GREEN": {"runway_ge": 1.5, "quick_cap_x": 1.0, "slots": "all"},
                            "AMBER": {"runway_ge": 1.0, "quick_cap_x": 0.6, "slots": "first"},
                            "RED": {"runway_ge": 0.0, "quick_cap_x": 0.4, "slots": "first"},
                            "FLOOR": {"week_left_pct_lt": 10, "quick_cap_x": 0.4, "slots": "none"}}}
    r.update(kw)
    return r


def operations(**kw):
    r = {"name": "Operations", "enabled": True, "instructions": "src/RimMandrake/rimflow/roles/operations.md",
         "seat": "BENCH", "clone": os.path.join(TMP, "clone"), "model": "sonnet", "ledger_item": "ROLES_ITEM_X",
         "off_file": os.path.join(TMP, "OPERATIONS_OFF"), "runs_local": ["07:30", "19:30"],
         "economy_pass_local": "07:30", "run_token_cap": 60000, "economy_token_cap": 150000,
         "daily_token_cap": 300000, "alarm_runs": True}
    r.update(kw)
    return r


def robs(status=None, account="acct", unit="active", result=None, off=None):
    return {"ops": lambda: status, "account": lambda: account, "unit_state": lambda u: unit,
            "result": lambda run: result, "off": lambda p: off}


def rdecide(roles, st, ro, now, **kw):
    o = obs(**kw)
    o["roles"] = ro
    return D.decide(sched(roles=roles), st, o, now, True)


def fresh():
    return {"seats": {}, "wakes": [], "recovers": [], "alarms": {}}


def role_acts(acts):
    return [a for a in acts if a["do"].startswith("role") or str(a.get("kind", "")).startswith("role")]


def test_role_reading_and_band():
    now = at_local("08:00")
    r = RL.ops_reading(ops_status(now), "acct", now)
    check(r["state"] == "MEASURED" and r["runway"] == 2.0, "ops reading: fresh MEASURED points are read")
    check(RL.ops_reading(ops_status(now, m="ESTIMATE"), "acct", now)["state"] == "MEASURED",
          "ops reading: an ESTIMATE counts as its value (conductor.md)")
    check("STALE" in RL.ops_reading(ops_status(now, age_s=2701), "acct", now)["why"], "ops reading: 45 min old is STALE")
    check(RL.ops_reading(ops_status(now, m="UNMEASURED"), "acct", now)["state"] == "UNMEASURED",
          "ops reading: an UNMEASURED point is UNMEASURED")
    check(RL.ops_reading(None, "acct", now)["state"] == "UNMEASURED", "ops reading: no status.json is UNMEASURED")
    check(RL.ops_reading(ops_status(now), None, now)["state"] == "UNMEASURED", "ops reading: no account is UNMEASURED")
    c = conductor()
    for rw, wl, want in ((2.0, 40, "GREEN"), (1.5, 40, "GREEN"), (1.2, 40, "AMBER"), (0.3, 40, "RED"),
                         (2.0, 9, "FLOOR"), (-0.5, 40, "RED")):
        check(RL.band(c, {"runway": rw, "week_left": wl})[0] == want, "band: runway %s week_left %s -> %s" % (rw, wl, want))
    check(RL.band(operations(), {"runway": 0.1, "week_left": 5})[0] == "NONE", "band: a role with no bands -> NONE x1")
    check(RL.run_tokens({"usage": {"input_tokens": 2, "cache_creation_input_tokens": 24009,
                                   "cache_read_input_tokens": 11227, "output_tokens": 4}}) == 35242,
          "run tokens: all four usage fields (the proof's trivial haiku run: 35242)")
    check(RL.wsl_path("D:\\ClaudeWork\\x\\OFF") == "/mnt/d/ClaudeWork/x/OFF", "off_file: Windows path -> /mnt/d")


def test_role_gates():
    now = at_local("08:00")
    st = fresh()
    a = role_acts(rdecide([conductor(enabled=False)], st, robs(ops_status(now)), now))
    check(a == [], "role enabled false: nothing")
    st = fresh()
    a = role_acts(rdecide([{"name": "Auditor", "enabled": True}], st, robs(ops_status(now)), now))
    check([x["do"] for x in a] == ["alarm"] and "cannot be launched" in a[0]["why"],
          "enabled role without launch keys: alarm, not run")
    st = fresh()
    a = role_acts(rdecide([conductor()], st, robs(ops_status(now)), now))
    check([x["do"] for x in a] == ["role_launch"] and a[0]["budget"] == 30000 and a[0]["note"]
          and a[0]["ticket"] == "ROLES_ITEM_X", "GREEN 08:00: launch, full quick cap, noted on the role's item")
    check("conductor.md" in a[0]["message"] and "30000" in a[0]["message"] and "bridge" in a[0]["message"],
          "launch prompt names the instructions, the budget and the no-bridge line")
    a2 = role_acts(rdecide([conductor()], st, robs(ops_status(now)), now + 120))
    check(a2 == [], "a slot runs once a day (next tick: nothing)")
    st = fresh()
    a = role_acts(rdecide([conductor()], st, robs(ops_status(now), off="owner: quiet today"), now))
    check([x["do"] for x in a] == ["role_hold"] and "off switch" in a[0]["why"], "off file present: hold, no launch")
    for status, acct, label in ((ops_status(now, age_s=3600), "acct", "stale"),
                                (ops_status(now, m="UNMEASURED"), "acct", "UNMEASURED"),
                                (None, "acct", "missing status.json"), (ops_status(now), None, "no account")):
        st = fresh()
        a = role_acts(rdecide([conductor()], st, robs(status, account=acct), now))
        check([x["do"] for x in a] == ["alarm"] and "REFUSED" in a[0]["why"] and a[0]["note"],
              "ops reading %s: refused loudly (noted alarm), no launch" % label)
        check("%s 08:00" % RL.day_of(now) not in st["roles"]["Conductor"]["done"],
              "ops reading %s: the slot is not spent (retried next tick)" % label)
    st = fresh()
    a = role_acts(rdecide([conductor()], st, robs(ops_status(now, runway=1.2)), now))
    check(a and a[0]["do"] == "role_launch" and a[0]["budget"] == 18000, "AMBER 08:00: runs at x0.6")
    t20 = at_local("20:00")
    a = role_acts(rdecide([conductor()], st, robs(ops_status(t20, runway=1.2), unit="inactive",
                                                  result={"usage": {"output_tokens": 10}}), t20))
    check("role_launch" not in [x["do"] for x in a] and any("band AMBER" in x.get("why", "") for x in a),
          "AMBER 20:00: held (first slot only)")
    st = fresh()
    a = role_acts(rdecide([conductor()], st, robs(ops_status(now, week_left=5)), now))
    check([x["do"] for x in a] == ["role_hold"] and "FLOOR" in a[0]["why"], "FLOOR: no scheduled check")
    st = fresh()
    st["roles"] = {"Conductor": {"done": {}, "runs": [{"day": RL.day_of(now), "tokens": 190000, "state": "done",
                                                        "at": now - 3600, "unit": "u0", "budget": 30000}]}}
    a = role_acts(rdecide([conductor()], st, robs(ops_status(now)), now))
    check([x["do"] for x in a] == ["alarm"] and "daily_token_cap" in a[0]["why"], "daily cap would be passed: refused")
    late = at_local("08:00", 3601)
    st = fresh()
    a = role_acts(rdecide([conductor()], st, robs(ops_status(late)), late))
    check([x["do"] for x in a] == ["role_hold"] and "missed" in a[0]["why"], "a slot more than slot_late_s late: missed")
    st = fresh()
    a = role_acts(rdecide([conductor()], st, robs(ops_status(now)), now - 120))
    check(a == [], "before the slot: nothing")


def test_role_economy_and_alarms():
    now = at_local("07:30")
    st = fresh()
    alarms = {"k1": {"state": "OPEN", "item": "OPS_OLD_ONE"}}
    a = role_acts(rdecide([operations()], st, robs(ops_status(now, runway=0.1, week_left=3, alarms=alarms)), now))
    check([x["do"] for x in a] == ["role_launch"] and a[0]["mode"] == "economy" and a[0]["budget"] == 150000,
          "Operations 07:30: economy pass at economy_token_cap, no bands (x1.0 even when low)")
    check(st["roles"]["Operations"]["alarms_seen"] == ["OPS_OLD_ONE"], "alarms open at first enable: baseline")
    t = now + 600
    st["roles"]["Operations"]["runs"] = [{"unit": "u1", "at": now, "day": RL.day_of(now), "budget": 150000,
                                          "mode": "economy", "item": "ROLES_ITEM_X", "state": "running"}]
    alarms2 = dict(alarms, k2={"state": "OPEN", "item": "OPS_NEW_ONE"})
    a = role_acts(rdecide([operations()], st, robs(ops_status(t, alarms=alarms2), unit="active"), t))
    check(a == [], "a new alarm waits while a run is going (one run per role)")
    res = {"usage": {"input_tokens": 100, "output_tokens": 50}, "modelUsage": {"m-x": {}}, "subtype": "success"}
    a = role_acts(rdecide([operations()], st, robs(ops_status(t, alarms=alarms2), unit="inactive", result=res), t))
    ds = [x["do"] for x in a]
    check(ds == ["role_done", "role_launch"], "run finished -> role_done (noted), then the new alarm runs: %s" % ds)
    check("150 tokens" in a[0]["why"] and "m-x" in a[0]["why"], "role_done records tokens and the model used")
    check(a[1]["ticket"] == "OPS_NEW_ONE" and a[1]["budget"] == 60000, "alarm run: noted on the alarm item, run cap")
    check(st["roles"]["Operations"]["runs"][0]["tokens"] == 150, "spend recorded on the run")
    st["roles"]["Operations"]["runs"] = [{"unit": "u2", "at": t, "day": RL.day_of(t), "budget": 1000,
                                          "mode": "run", "item": "ROLES_ITEM_X", "state": "running"}]
    a = role_acts(rdecide([operations()], st, robs(ops_status(t + 60), unit="inactive",
                                                   result={"usage": {"output_tokens": 5000}}), t + 60))
    check("role:Operations:overbudget" in [x.get("kind") for x in a], "a run over its budget: alarm")
    st["roles"]["Operations"]["runs"] = [{"unit": "u3", "at": t, "day": RL.day_of(t), "budget": 1000,
                                          "mode": "run", "item": "ROLES_ITEM_X", "state": "running"}]
    a = role_acts(rdecide([operations()], st, robs(ops_status(t + 60), unit="failed", result=None), t + 60))
    check("role:Operations:failed" in [x.get("kind") for x in a], "a run with no result: alarm")
    st["roles"]["Operations"]["runs"] = [{"unit": "u4", "at": t, "day": RL.day_of(t), "budget": 1000, "scope": "s.scope",
                                          "mode": "run", "item": "ROLES_ITEM_X", "state": "running"}]
    a = role_acts(rdecide([operations()], st, robs(ops_status(t + 1900), unit="active"), t + 1900))
    check([x["do"] for x in a][:2] == ["role_stop", "alarm"] and a[0]["scope"] == "s.scope",
          "a run past run_max_s: its scope and unit are stopped, with an alarm")


def test_role_real_schedule_caps_and_ops_bands():
    sch = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "dispatcher_schedule.json")))
    roles = {r["name"]: r for r in sch["roles"]}
    c, o = roles["Conductor"], roles["Operations"]
    check(c["quick_token_cap"] == 80000 and c["daily_token_cap"] == 300000 and c["session_week_pct_cap"] == 6,
          "schedule: Conductor caps 80,000 / 300,000 / 6%")
    check(o["run_token_cap"] == 80000 and o["daily_token_cap"] == round(80000 * 2 * 1.25),
          "schedule: Operations run cap 80,000, daily 80,000 x 2 + 25%")
    for r, cap in ((c, c["quick_token_cap"]), (o, o["run_token_cap"])):
        for bn, b in r["throttle_bands"].items():
            check(b["slots"] == "none" or cap * b["quick_cap_x"] >= 60000,
                  "%s band %s: launches nothing or stays >= 60,000" % (r["name"], bn))
    base = at_local("07:30")
    ev = at_local("19:30")

    def run(now, **kw):
        st = fresh()
        if now == ev:                      # the morning slot is long past (else it is reported missed first)
            st["roles"] = {"Operations": {"done": {"%s 07:30" % RL.day_of(ev): "x"}, "runs": []}}
        return st, role_acts(rdecide([dict(o, enabled=True, off_file=os.path.join(TMP, "OPERATIONS_OFF"),
                                          clone=os.path.join(TMP, "clone"))], st,
                                     robs(ops_status(now, **kw)), now))
    st, a = run(base, runway=2.0)
    check(a and a[0]["mode"] == "economy" and a[0]["budget"] == 100000, "Ops GREEN 07:30: economy pass")
    st, a = run(base, runway=1.2)
    check([x["do"] for x in a] == ["role_hold"] and "band AMBER" in a[0]["why"], "Ops AMBER 07:30: no economy pass")
    st, a = run(ev, runway=1.2)
    check(a and a[0]["do"] == "role_launch" and a[0]["budget"] == 80000, "Ops AMBER 19:30: quick run, 80,000")
    st, a = run(ev, runway=0.5)
    check(a and a[0]["do"] == "role_launch" and a[0]["budget"] == 60000, "Ops RED 19:30: the one quick run, 60,000")
    st, a = run(base, runway=0.5)
    check([x["do"] for x in a] == ["role_hold"], "Ops RED 07:30: economy pass held")
    st, a = run(ev, week_left=5)
    check([x["do"] for x in a] == ["role_hold"] and "FLOOR" in a[0]["why"], "Ops FLOOR: nothing")
    # alarm runs: RED and FLOOR block, AMBER allows
    for rw, wl, want in ((1.2, 50, True), (0.5, 50, False), (2.0, 5, False)):
        st = fresh()
        st["roles"] = {"Operations": {"done": {"%s 07:30" % RL.day_of(ev): "x", "%s 19:30" % RL.day_of(ev): "x"},
                                      "runs": [], "alarms_seen": []}}
        al = {"k": {"state": "OPEN", "item": "OPS_NEW"}}
        a = role_acts(rdecide([dict(o, enabled=True, off_file=os.path.join(TMP, "OPERATIONS_OFF"),
                                    clone=os.path.join(TMP, "clone"))], st,
                              robs(ops_status(ev, runway=rw, week_left=wl, alarms=al)), ev))
        check(bool([x for x in a if x["do"] == "role_launch"]) == want,
              "Ops alarm run at runway %s week_left %s: %s" % (rw, wl, "runs" if want else "blocked"))


def test_role_execute_and_dry():
    calls = []

    def fake_run(argv, **kw):
        calls.append(argv)
        out = "4242\n" if argv[:2] == ["systemctl", "--user"] else ""
        return subprocess.CompletedProcess(argv, 0, out, "")
    role = conductor()
    root = os.path.join(TMP, "roles_exec")
    ok, out, rec = RL.launch(role, "rm-role-conductor-1", "hello", root, "/opt/bin/claude", runner=fake_run)
    argv = calls[0]
    check(ok and argv[:5] == ["systemd-run", "--user", "--quiet", "--collect", "--unit"],
          "launch: its own transient user unit (outlives the oneshot tick)")
    check("--setenv" in argv and "AGENT_SEAT=BENCH" in argv and any(a.startswith("PATH=/opt/bin:") for a in argv),
          "launch: seat env and claude's dir on PATH")
    i = argv.index("--")
    check(argv[i + 1].endswith("claude_bounded.sh") and argv[i + 2:i + 4] == ["-p", "hello"]
          and argv[argv.index("--model") + 1] == "sonnet" and "json" in argv, "launch: claude_bounded -p, alias, json")
    check(rec["scope"] == "claude-seat-BENCH-4242.scope", "launch: the scope to stop is claude-seat-<seat>-<MainPID>")
    calls.clear()
    RL.stop("u", "s.scope", runner=fake_run)
    check(calls[0] == ["systemctl", "--user", "stop", "s.scope", "u"], "stop: scope first, then the unit")
    # execute: a launch records the run; a failed launch records nothing
    sch = sched(roles=[role])
    st = fresh()
    act = {"do": "role_launch", "role": "Conductor", "unit": "U1", "message": "m", "ticket": "ROLES_ITEM_X",
           "note": True, "mode": "quick", "budget": 30000, "slot": "k", "band": "GREEN", "why": "w"}
    noted = []
    fx = {"note": lambda i, t: noted.append((i, t)) or (True, ""), "publish": lambda n: "p", "lock": lambda: open(os.devnull),
          "role_launch": lambda *a: (True, "unit U1 started", {"out": "o", "err": "e", "scope": "s"})}
    D.execute([dict(act)], sch, st, root, True, 100.0, fx)
    run = st["roles"]["Conductor"]["runs"][0]
    check(run["state"] == "running" and run["budget"] == 30000 and run["scope"] == "s", "execute: the run is recorded")
    check(noted and noted[0][0] == "ROLES_ITEM_X" and "Conductor" in noted[0][1], "execute: the launch is noted on the ledger")
    st = fresh()
    fx["role_launch"] = lambda *a: (False, "systemd-run exit 1", {})
    a = D.execute([dict(act)], sch, st, root, True, 100.0, fx)
    check(not st.get("roles") and "LAUNCH FAILED" in a[0]["why"], "execute: a failed launch records no run, says so")
    # dry-run tick: decides the launch, launches nothing
    launched = []
    fx = {k: (lambda *a, **kw: launched.append(a)) for k in ("ring", "withdraw", "recover", "note", "publish",
                                                              "role_launch", "role_stop")}
    now = at_local("08:00")
    o = obs()
    o["roles"] = robs(ops_status(now))
    acts = D.tick(sched(roles=[role]), False, obs=o, now=now, fx=fx)
    check("role_launch" in kinds(acts) and not launched and all(x["result"].startswith("DRY") for x in acts),
          "dry-run: decides the launch, launches nothing")
    # recover() env: claude's dir on PATH (the timer's PATH has no ~/.local/bin)
    seen = {}
    D.recover({"seat": "FOUNDRY", "clone": TMP}, "sid", "m",
              runner=lambda argv, **kw: seen.update(kw) or subprocess.CompletedProcess(argv, 0, "", ""))
    check(os.path.dirname(D.claude_exe()) in seen["env"]["PATH"].split(":"), "recover: claude's dir on PATH")
    # the shipped schedule: every role disabled, Conductor and Operations launchable once enabled
    real = D.load_schedule()
    check(all(not r.get("enabled") for r in real["roles"]), "shipped schedule: every role enabled false")
    for name in ("Conductor", "Operations"):
        r = next(x for x in real["roles"] if x["name"] == name)
        check(all(r.get(k) for k in RL.LAUNCH_KEYS) and r.get("off_file"), "shipped schedule: %s has launch keys" % name)


def main():
    for t in (test_parse_peek, test_wake_and_owner, test_blind_pause_roles_caps, test_verify_retry, test_dead_recover,
              test_never_adopt_or_resume_a_stranger, test_review_fixes, test_doorbell, test_end_to_end, test_dry_run, test_alarm_rate, test_seat_rule, test_ringed_next_rechecks_owner,
              test_role_reading_and_band, test_role_gates, test_role_economy_and_alarms,
              test_role_real_schedule_caps_and_ops_bands, test_role_execute_and_dry):
        try:
            t()
        except Exception as e:  # noqa: BLE001
            import traceback
            traceback.print_exc()
            check(False, "%s crashed: %s" % (t.__name__, e))
    print("%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
