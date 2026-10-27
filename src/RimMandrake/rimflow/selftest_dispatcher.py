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


def test_review_s():
    """F1: the UNCONFIRMED retirement alarm is not rate-limited away by the per-tick scope alarm. F3: a stuck
    index.lock in the publish result raises one `publish:index_lock` alarm."""
    sch = sched()
    st = {"seats": {}, "wakes": [], "recovers": [], "alarms": {}}
    root = os.path.join(TMP, "reviews")
    noted = []
    fx = {"note": lambda i, t: noted.append(t) or (True, ""), "publish": lambda n: None}
    scope_kind = "role:Arbiter:scope"
    unc_kind = "role:Arbiter:scope_unconfirmed:u1"
    acts = [{"do": "alarm", "kind": scope_kind, "why": "never resolved", "note": True},
            {"do": "alarm", "kind": unc_kind, "why": "UNCONFIRMED", "note": True}]
    D.execute(acts, sch, st, root, True, 10.0, fx)
    check(len(noted) == 2, "both the scope alarm and the unconfirmed alarm reach the ledger: %r" % noted)
    src = open(os.path.join(HERE, "role_launch.py")).read()
    check('kind="role:%s:scope_unconfirmed:%s"' in src, "role_launch gives the retirement its own kind")
    noted.clear()
    class _Lk:
        def close(self):
            pass
    fx2 = dict(fx, lock=lambda: _Lk(), publish=lambda n: "add failed: Unable to create '.git/index.lock': File exists.")
    sch2 = sched(publish=True)
    for t in (20.0, 80.0):
        D.execute([], sch2, st, root, True, t, fx2)
    check(len(noted) == 1 and "index.lock" in noted[0], "a stuck index.lock raises one rate-limited alarm: %r" % noted)


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


def usage(**kw):
    u = {k: 0 for k in RL.USAGE_KEYS}
    u.update(kw)
    return u


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
                                                  result={"usage": usage(output_tokens=10)}), t20))
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
                                          "mode": "economy", "item": "ROLES_ITEM_X", "state": "running",
                                          "scope": "s.scope"}]
    alarms2 = dict(alarms, k2={"state": "OPEN", "item": "OPS_NEW_ONE"})
    a = role_acts(rdecide([operations()], st, robs(ops_status(t, alarms=alarms2), unit="active"), t))
    check(a == [], "a new alarm waits while a run is going (one run per role)")
    res = {"usage": usage(input_tokens=100, output_tokens=50), "modelUsage": {"m-x": {}}, "subtype": "success"}
    a = role_acts(rdecide([operations()], st, robs(ops_status(t, alarms=alarms2), unit="inactive", result=res), t))
    ds = [x["do"] for x in a]
    check(ds == ["role_done", "role_launch"], "run finished -> role_done (noted), then the new alarm runs: %s" % ds)
    check("150 tokens" in a[0]["why"] and "m-x" in a[0]["why"], "role_done records tokens and the model used")
    check(a[1]["ticket"] == "OPS_NEW_ONE" and a[1]["budget"] == 60000, "alarm run: noted on the alarm item, run cap")
    check(st["roles"]["Operations"]["runs"][0]["tokens"] == 150, "spend recorded on the run")
    st["roles"]["Operations"]["runs"] = [{"unit": "u2", "at": t, "day": RL.day_of(t), "budget": 1000,
                                          "mode": "run", "item": "ROLES_ITEM_X", "state": "running",
                                          "scope": "s.scope"}]
    a = role_acts(rdecide([operations()], st, robs(ops_status(t + 60), unit="inactive",
                                                   result={"usage": usage(output_tokens=5000)}), t + 60))
    check("role:Operations:overbudget" in [x.get("kind") for x in a], "a run over its budget: alarm")
    st["roles"]["Operations"]["runs"] = [{"unit": "u3", "at": t, "day": RL.day_of(t), "budget": 1000,
                                          "mode": "run", "item": "ROLES_ITEM_X", "state": "running",
                                          "scope": "s.scope"}]
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
    check(not st["roles"]["Conductor"]["runs"] and "LAUNCH FAILED" in a[0]["why"],
          "execute: a failed launch records no run, says so")
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


def test_review_q():
    """GPT review round Q (2026-10-27): run supervision, execute-time off switch, non-finite / missing data."""
    t0 = at_local("19:00")
    late = t0 + 1900

    def running(**kw):
        r = {"unit": "uq", "at": t0, "day": RL.day_of(t0), "budget": 1000, "mode": "run", "item": "ROLES_ITEM_X",
             "state": "running", "scope": "s.scope", "seat": "BENCH"}
        r.update(kw)
        return {"Operations": {"done": {}, "runs": [r]}}
    # 1: PAUSE / blind agents / disabled role still supervise (and time-limit) a launched run
    for label, kw, role in (("PAUSE", {"paused": "owner stop"}, operations()),
                            ("agents UNMEASURED", {"agents_ok": False}, operations()),
                            ("role disabled", {}, operations(enabled=False)),
                            ("role gone from the schedule", {}, conductor())):
        st = fresh()
        st["roles"] = running()
        a = role_acts(rdecide([role], st, robs(ops_status(late), unit="active"), late, **kw))
        check([x["do"] for x in a][:2] == ["role_stop", "alarm"],
              "Q1 %s: an overtime run is still stopped: %s" % (label, [x["do"] for x in a]))
    # 2: the stop is not trusted until systemd says inactive; re-issued with stop_failed
    st = fresh()
    st["roles"] = running()
    rdecide([operations()], st, robs(ops_status(late), unit="active"), late)
    run = st["roles"]["Operations"]["runs"][0]
    check(run["state"] == "running" and run["stop_tries"] == 1, "Q2 stop issued: the run stays running until confirmed")
    a = role_acts(rdecide([operations()], st, robs(ops_status(late + 120), unit="active"), late + 120))
    check([x["do"] for x in a][:2] == ["role_stop", "alarm"] and a[1]["kind"] == "role:Operations:stop_failed"
          and not a[0]["note"], "Q2 still active after a stop: stop again + stop_failed alarm (one ledger note)")
    a = role_acts(rdecide([operations()], st, robs(ops_status(late + 240), unit="inactive"), late + 240))
    check(a and a[0]["do"] == "role_done" and "after 2 stop(s)" in a[0]["why"], "Q2 inactive: then it is finished")
    # 3: an unknown unit state is busy and alarmed, never a finish
    st = fresh()
    st["roles"] = running(at=at_local("19:30") - 60)
    t = at_local("19:30")
    a = role_acts(rdecide([operations()], st, robs(ops_status(t), unit="unknown"), t))
    ds = [x["do"] for x in a]
    check("role_done" not in ds and "role_launch" not in ds and any(x.get("kind") == "role:Operations:unit" for x in a)
          and st["roles"]["Operations"]["runs"][0]["state"] == "running",
          "Q3 unit state unknown: kept running, UNMEASURED alarm, no new launch: %s" % ds)
    check(RL.unit_state("u", runner=lambda argv, **kw: subprocess.CompletedProcess(argv, 1, "inactive", "")) == "unknown",
          "Q3 systemctl exit != 0: unknown, not its stdout")

    def raising(argv, **kw):
        raise subprocess.TimeoutExpired(argv, 30)
    st = fresh()
    st["roles"] = running(at=t - 1900)
    a = role_acts(rdecide([operations()], st, robs(ops_status(t), unit="unknown"), t))
    check(any(x["do"] == "role_stop" for x in a), "Q3 unknown and overtime: stopped anyway")
    # 4: a launch that raised after systemd-run stays tracked; MainPID failure keeps the run; stop resolves the scope
    sch = sched(roles=[conductor()])
    act = {"do": "role_launch", "role": "Conductor", "unit": "UQ", "message": "m", "ticket": "ROLES_ITEM_X",
           "note": False, "mode": "quick", "budget": 30000, "slot": "k", "band": "GREEN", "why": "w", "seat": "BENCH",
           "run_max_s": 1800}
    base_fx = {"note": lambda i, x: (True, ""), "publish": lambda n: None, "lock": lambda: open(os.devnull),
               "off": lambda p: None, "paused": lambda: None}

    def boom(*a):
        raise subprocess.TimeoutExpired("systemd-run", 60)
    st = fresh()
    D.execute([dict(act)], sch, st, TMP, True, 100.0, dict(base_fx, role_launch=boom))
    r = st["roles"]["Conductor"]["runs"]
    check(len(r) == 1 and r[0]["state"] == "running" and r[0]["unit"] == "UQ" and r[0]["run_max_s"] == 1800,
          "Q4 launch raised: the run is still recorded (unit may be up) and supervised")
    calls = []

    def sd_ok_pid_raises(argv, **kw):
        calls.append(argv)
        if argv[0] == "systemd-run":
            return subprocess.CompletedProcess(argv, 0, "", "")
        raise subprocess.TimeoutExpired(argv, 30)
    ok, out, rec = RL.launch(conductor(), "UQ2", "m", os.path.join(TMP, "q4"), "/opt/bin/claude", runner=sd_ok_pid_raises)
    check(ok and rec["scope"] is None, "Q4 MainPID query raised: still launched, scope resolved later")
    calls.clear()

    def pid_then_stop(argv, **kw):
        calls.append(argv)
        return subprocess.CompletedProcess(argv, 0, "777\n" if "MainPID" in argv else "", "")
    RL.stop("UQ2", None, runner=pid_then_stop, seat="BENCH")
    check(calls[-1] == ["systemctl", "--user", "stop", "claude-seat-BENCH-777.scope", "UQ2"],
          "Q4 stop with no recorded scope: resolves it from MainPID, stops scope + unit")
    # 5: the off switch and PAUSE are rechecked at execution
    for label, fx in (("off file", dict(base_fx, off=lambda p: "owner: now")),
                      ("PAUSE", dict(base_fx, paused=lambda: "owner stop"))):
        launched = []
        st = fresh()
        a = D.execute([dict(act)], sch, st, TMP, True, 100.0,
                      dict(fx, role_launch=lambda *x: launched.append(x) or (True, "", {})))
        check(not launched and not (st.get("roles") or {}).get("Conductor", {}).get("runs")
              and "NOT LAUNCHED" in a[0]["why"], "Q5 %s appearing after decide: not launched" % label)
    # 6 + 7: the shipped schedule and role docs agree (cheaper readings)
    here = os.path.dirname(os.path.abspath(__file__))
    real = {r["name"]: r for r in json.load(open(os.path.join(here, "dispatcher_schedule.json")))["roles"]}
    ops_md = open(os.path.join(here, "roles", "operations.md"), encoding="utf-8").read()
    con_md = open(os.path.join(here, "roles", "conductor.md"), encoding="utf-8").read()
    check("skips this whole run" in ops_md and "07:30 and 19:30 local" not in ops_md,
          "Q6 operations.md: a band without the economy pass skips the whole 07:30 run (as the code does)")
    check(real["Conductor"].get("after_role") == "Operations" and "after_role" in con_md
          and "the 20:00 check only" in con_md and "the 08:00 check only" not in con_md,
          "Q7 Conductor runs after Operations (schedule + conductor.md); AMBER/RED keep the 20:00 check")
    rc = dict(real["Conductor"], enabled=True, clone=os.path.join(TMP, "clone"), off_file=os.path.join(TMP, "CQ_OFF"))
    ro = dict(real["Operations"], enabled=True, clone=os.path.join(TMP, "clone"), off_file=os.path.join(TMP, "OQ_OFF"))
    c8 = at_local("08:00")
    st = fresh()
    st["roles"] = {"Operations": {"done": {"%s 07:30" % RL.day_of(c8): "x"}, "runs": []}}
    a = role_acts(rdecide([rc, ro], st, robs(ops_status(c8)), c8))
    check([x["do"] for x in a if x.get("role") == "Conductor"] == ["role_hold"] and "waits" in a[0]["why"],
          "Q7 Conductor 08:00 with no finished Operations run: waits")
    a = role_acts(rdecide([rc, ro], st, robs(ops_status(c8 + 120)), c8 + 120))
    check(not [x for x in a if x.get("role") == "Conductor"], "Q7 the wait is journaled once, not every tick")
    st["roles"]["Operations"]["runs"] = [{"unit": "o1", "at": at_local("07:30"), "day": RL.day_of(c8), "state": "running",
                                          "budget": 1, "mode": "economy", "item": "X", "scope": "s.scope",
                                          "slot": "%s 07:30" % RL.day_of(c8)}]
    a = role_acts(rdecide([rc, ro], st, robs(ops_status(c8 + 240), unit="active"), c8 + 240))
    check(not [x for x in a if x.get("do") == "role_launch"], "Q7 Operations still running: Conductor waits")
    a = role_acts(rdecide([rc, ro], st, robs(ops_status(c8 + 360), unit="inactive",
                                             result={"usage": usage(output_tokens=9), "subtype": "success"}), c8 + 360))
    check([x["role"] for x in a if x["do"] == "role_launch"] == ["Conductor"],
          "Q7 Operations run finished done: the Conductor check launches")
    st = fresh()
    a = role_acts(rdecide([rc], st, robs(ops_status(c8)), c8))
    check(any(x.get("kind") == "role:Conductor:after" for x in a), "Q7 Operations not enabled: alarm")
    st = fresh()
    a = role_acts(rdecide([rc, ro], st, robs(ops_status(c8, runway=1.2)), c8))
    check(not [x for x in a if x["do"] == "role_launch"], "Q7 Conductor AMBER 08:00: not its slot")
    c20 = at_local("20:00")
    st = fresh()
    st["roles"] = {"Operations": {"done": {"%s 19:30" % RL.day_of(c20): "launch"}, "runs": [{"unit": "o2", "at": at_local("19:30"), "day": RL.day_of(c20),
                                                        "state": "done", "budget": 1, "mode": "run", "item": "X",
                                                        "slot": "%s 19:30" % RL.day_of(c20)}]},
                   "Conductor": {"done": {"%s 08:00" % RL.day_of(c20): "x"}, "runs": []}}
    a = role_acts(rdecide([rc, ro], st, robs(ops_status(c20, runway=1.2)), c20))
    check([(x["role"], x["budget"]) for x in a if x["do"] == "role_launch" and x["role"] == "Conductor"] == [("Conductor", 60000)],
          "Q7 Conductor AMBER 20:00, after the 19:30 Operations run: launches at 60,000")
    # 8: missing / malformed usage is UNMEASURED, failed, counted at its budget
    for bad in ({}, {"input_tokens": "abc"}, dict(usage(), output_tokens=True), dict(usage(), output_tokens=-1),
                dict(usage(), output_tokens=float("nan"))):
        check(RL.run_tokens({"usage": bad}) is None, "Q8 usage %r -> UNMEASURED" % (bad,))
    st = fresh()
    st["roles"] = running(at=t - 60, budget=50000)
    a = role_acts(rdecide([operations()], st, robs(ops_status(t), unit="inactive", result={"usage": {}}), t))
    check(any(x.get("kind") == "role:Operations:failed" and "usage UNMEASURED" in x["why"] for x in a)
          and RL.spent_today(st["roles"]["Operations"], t) == 50000,
          "Q8 a result with usage {}: failed alarm, spend counted at its full budget")
    # 9 + 10: a future reading and non-finite / bool points are UNMEASURED
    now = at_local("08:00")
    check("FUTURE" in RL.ops_reading(ops_status(now, age_s=-3600), "acct", now)["why"], "Q9 'at' an hour ahead: UNMEASURED")
    check(RL.ops_reading(ops_status(now, age_s=-120), "acct", now)["state"] == "MEASURED", "Q9 2 min skew: tolerated")
    for kw in ({"week_left": float("nan")}, {"runway": float("inf")}, {"runway": True}):
        check(RL.ops_reading(ops_status(now, **kw), "acct", now)["state"] == "UNMEASURED", "Q10 %r: UNMEASURED" % (kw,))
    # 11: last_ok_tick only for a tick that worked
    rooted = D.state_root(False)
    sp = os.path.join(rooted, "state.json")
    if os.path.exists(sp):
        os.remove(sp)
    try:
        D.tick(sched(), False, obs={"paused": None, "roles": None}, now=5000.0, fx={})
    except Exception:  # noqa: BLE001
        pass
    sv = json.load(open(sp))
    check(sv["last_tick"] and sv["last_ok_tick"] is None, "Q11 a tick that raised: last_tick (attempt) only")
    D.tick(sched(), False, obs=obs(agents_ok=False), now=5200.0, fx={})
    check(json.load(open(sp))["last_ok_tick"] is None, "Q11 a blind tick: not a working tick")
    D.tick(sched(), False, obs=obs(), now=5400.0, fx={})
    check(json.load(open(sp))["last_ok_tick"] == D.iso(5400.0), "Q11 a working tick stamps last_ok_tick")


def test_review_r():
    """Review round R (2026-10-27): A state durable at launch + bounded publish, B after_role strict, C no blind alarm
    baseline, D a run retires only when its scope is empty."""
    # A: the run (and decide's slot mark) is on disk BEFORE systemd-run; a tick killed after it never relaunches
    role = conductor()
    sp = os.path.join(D.state_root(True), "state.json")
    if os.path.exists(sp):
        os.remove(sp)
    snap = {}

    def launch_reads_disk(*a):
        snap["st"] = json.load(open(sp))
        return True, "unit started", {"scope": "s.scope"}
    fx = {"note": lambda i, t: (True, ""), "publish": lambda n: None, "lock": lambda: open(os.devnull),
          "off": lambda p: None, "paused": lambda: None, "role_launch": launch_reads_disk}
    now = at_local("08:00")
    o = obs()
    o["roles"] = robs(ops_status(now))
    D.tick(sched(roles=[role]), True, obs=o, now=now, fx=fx)
    rs = (snap.get("st") or {}).get("roles", {}).get("Conductor", {})
    check([r["state"] for r in rs.get("runs", [])] == ["running"] and rs.get("done", {}).get(
        "%s 08:00" % RL.day_of(now)) == "launch", "R-A the run and its slot mark are on disk before systemd-run")
    with open(sp, "w") as f:                 # the tick was SIGTERMed before its final save: only the early save
        json.dump(snap["st"], f)
    relaunch = []
    fx["role_launch"] = lambda *a: relaunch.append(a) or (True, "", {})
    o["roles"] = robs(ops_status(now + 120), unit="active")
    D.tick(sched(roles=[role]), True, obs=o, now=now + 120, fx=fx)
    check(not relaunch, "R-A a tick killed after launch: the next tick does not launch the role again")
    t = time.time()
    out = D.publish_bounded(0, 1, argv=["sleep", "30"])
    check("KILLED" in out and time.time() - t < 15, "R-A a hung publish is killed at the tick budget: %s" % out)
    check(D.publish_bounded(0, 0, argv=["sleep", "30"]).startswith("publish skipped"), "R-A no budget left: no publish")
    # B: an Operations alarm run (or yesterday's late run) does not let the Conductor skip today's 07:30 run
    real = {r["name"]: r for r in json.load(open(os.path.join(HERE, "dispatcher_schedule.json")))["roles"]}
    rc = dict(real["Conductor"], enabled=True, clone=os.path.join(TMP, "clone"), off_file=os.path.join(TMP, "CR_OFF"))
    ro = dict(real["Operations"], enabled=True, clone=os.path.join(TMP, "clone"), off_file=os.path.join(TMP, "OR_OFF"))
    t801 = at_local("08:00", 60)
    for label, run in (("an alarm run at 02:00", {"at": at_local("02:00"), "mode": "alarm", "slot": "alarm OPS_A"}),
                       ("yesterday's 19:30 run launched late", {"at": at_local("20:10") - 86400, "mode": "run",
                                                               "slot": "%s 19:30" % RL.day_of(t801 - 86400)})):
        st = fresh()
        st["roles"] = {"Operations": {"done": {}, "alarms_seen": [],
                                      "runs": [dict(run, unit="o", day=RL.day_of(run["at"]), state="done", budget=1,
                                                    tokens=1, item="X", scope="s.scope")]}}
        a = role_acts(rdecide([rc, ro], st, robs(ops_status(t801), unit="inactive"), t801))
        got = [(x["role"], x["slot"]) for x in a if x["do"] == "role_launch"]
        check(got == [("Operations", "%s 07:30" % RL.day_of(t801))],
              "R-B %s: Operations 07:30 launches, the Conductor waits for it: %s" % (label, got))
    # C: a blind first reading sets no alarm baseline; the first MEASURED one does, and runs nothing
    st = fresh()
    noon = at_local("12:00")
    al = {"k": {"state": "OPEN", "item": "OPS_OPEN_BEFORE"}}
    a = role_acts(rdecide([operations()], st, robs(None), noon))
    check("alarms_seen" not in st["roles"]["Operations"] and any("no baseline" in x.get("why", "") for x in a),
          "R-C status.json missing on the first tick: no baseline, and it says so")
    a = role_acts(rdecide([operations()], st, robs(ops_status(noon + 120, alarms=al)), noon + 120))
    check(not [x for x in a if x["do"] == "role_launch"] and st["roles"]["Operations"]["alarms_seen"]
          == ["OPS_OPEN_BEFORE"], "R-C first MEASURED tick: the open alarm is the baseline, no paid run")
    # D: unit gone but claude still in its scope -> kept running; scope resolved while the unit runs
    st = fresh()
    t = at_local("19:00")
    st["roles"] = {"Operations": {"done": {}, "runs": [{"unit": "ud", "at": t, "day": RL.day_of(t), "budget": 1,
                                                         "mode": "run", "item": "X", "state": "running",
                                                         "scope": "claude-seat-BENCH-9.scope", "seat": "BENCH"}]}}
    ro2 = robs(ops_status(t + 300))
    ro2["unit_state"] = lambda u: "active" if u.endswith(".scope") else "inactive"
    a = role_acts(rdecide([operations()], st, ro2, t + 300))
    check(st["roles"]["Operations"]["runs"][0]["state"] == "running" and "role_done" not in [x["do"] for x in a]
          and any(x.get("kind") == "role:Operations:scope" for x in a),
          "R-D unit inactive, scope still active: not retired, alarmed")
    a = role_acts(rdecide([operations()], st, ro2, t + 1900))
    stops = [x for x in a if x["do"] == "role_stop"]
    check(stops and stops[0]["unit_gone"] and stops[0]["scope"] == "claude-seat-BENCH-9.scope",
          "R-D overtime with the unit gone: the scope alone is stopped")
    ro2["unit_state"] = lambda u: "inactive"
    a = role_acts(rdecide([operations()], st, ro2, t + 2000))
    check("role_done" in [x["do"] for x in a], "R-D scope empty too: then the run is finished")
    st = fresh()
    st["roles"] = {"Operations": {"done": {}, "runs": [{"unit": "ue", "at": t, "day": RL.day_of(t), "budget": 1,
                                                         "mode": "run", "item": "X", "state": "running",
                                                         "scope": None, "seat": "BENCH"}]}}
    ro3 = robs(ops_status(t + 60), unit="active")
    ro3["scope"] = lambda u, seat: "claude-seat-%s-77.scope" % seat
    rdecide([operations()], st, ro3, t + 60)
    check(st["roles"]["Operations"]["runs"][0]["scope"] == "claude-seat-BENCH-77.scope",
          "R-D scope unknown at launch: resolved while the unit runs")


# ---------------------------------------------------------------- account first (DISPATCHER_BUILD_PICK_ACCOUNT_FIRST)
import account_pick as AP  # noqa: E402

LENT_RULES = {"lent_accounts": {"lent": {"max_used_by_us_pct": 50, "floor_pct_left": 10, "end_window_h": 24,
                                         "prefer_start_of_week_h": 48}}}
PICK_RULE = {"enabled": True, "act": "recommend", "hold": ["role_launch", "ring", "recover"],
             "switch_when": {"runway_lt": 0.8, "week_left_pct_lt": 10},
             "target_min": {"runway_ge": 1.2, "week_left_pct_ge": 20, "m": ["MEASURED"]},
             "rank": "soonest_reset", "lent_min_draw_pct": 10}


def accounts_status(now, accts, age_s=300):
    """accts: {label: (runway, week_left, hours_to_reset, m)}."""
    pts = {}
    for a, (rw, wl, h, m) in accts.items():
        pts["accounts.%s.runway" % a] = {"m": m, "v": rw}
        pts["accounts.%s.week_left_pct" % a] = {"m": m, "v": wl}
        pts["accounts.%s.hours_to_reset" % a] = {"m": "MEASURED", "v": h}
    return {"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now - age_s)), "alarms": {}, "points": pts}


def lent_fn():
    sys.path.append(os.path.join(os.path.dirname(HERE), "Utils"))
    import slot_allocator
    return slot_allocator.lent_allowance


def test_account_pick_rule():
    now = at_local("08:00")
    fn = lent_fn()

    def pk(accts, cur="a", rule=None, lent=LENT_RULES, allowance=fn):
        return AP.pick(dict(PICK_RULE, **(rule or {})), accounts_status(now, accts), cur, lent, allowance, now)
    p = pk({"a": (2.0, 40, 50, "MEASURED"), "b": (3.0, 60, 20, "MEASURED")})
    check(p["state"] == "KEEP" and not p["hold"] and p["account"] == "a", "pick: current over the line -> KEEP")
    three = {"a": (0.3, 30, 50, "MEASURED"), "b": (3.0, 50, 40, "MEASURED"), "c": (2.0, 60, 10, "MEASURED")}
    p = pk(three)
    check(p["state"] == "SWITCH" and p["to"] == "c" and p["hold"], "pick: runway under the line -> SWITCH, soonest "
          "reset first (c)")
    check(pk(three, rule={"rank": "most_runway"})["to"] == "b", "pick: rank most_runway -> b")
    check(pk({"a": (2.0, 5, 50, "MEASURED"), "b": (3.0, 60, 20, "MEASURED")})["to"] == "b",
          "pick: week left under the line -> SWITCH")
    p = pk({"a": (0.3, 30, 50, "MEASURED"), "b": (3.0, 60, 20, "ESTIMATE")})
    check(p["state"] == "KEEP" and "not MEASURED" in p["why"], "pick: an ESTIMATE candidate is never a target")
    p = pk({"a": (0.3, 30, 50, "MEASURED"), "b": (1.0, 60, 20, "MEASURED")})
    check(p["state"] == "KEEP" and "no other account is fit" in p["why"], "pick: no fit candidate -> KEEP (bands "
          "pace it)")
    p = pk({"a": (0.3, 30, 50, "MEASURED"), "b": (3.0, 60, 20, "UNMEASURED")})
    check(p["state"] == "KEEP" and "b unmeasured" in p["why"], "pick: an UNMEASURED candidate is not a candidate")
    # unmeasured current: keep, never guess
    p = pk({"a": (0.3, 30, 50, "UNMEASURED"), "b": (3.0, 60, 20, "MEASURED")})
    check(p["state"] == "UNMEASURED" and not p["hold"] and p["to"] is None, "pick: current UNMEASURED -> keep + "
          "UNMEASURED, no switch guessed")
    check(pk({"b": (3.0, 60, 20, "MEASURED")}, cur=None)["state"] == "UNMEASURED", "pick: current account unresolved "
          "-> UNMEASURED")
    st = accounts_status(now, three, age_s=3000)
    check(AP.pick(PICK_RULE, st, "a", LENT_RULES, fn, now)["state"] == "UNMEASURED", "pick: stale reading -> "
          "UNMEASURED")
    check(pk(three, lent=None)["state"] == "UNMEASURED" and not pk(three, lent=None)["hold"],
          "pick: lent rules unreadable -> no switch (fail closed)")
    check(pk(three, allowance=None)["state"] == "UNMEASURED", "pick: allocator not importable -> no switch")
    # lent accounts: data rule (<= 50% of his week used early, never under the 10% floor near reset)
    p = pk({"a": (0.3, 30, 50, "MEASURED"), "lent": (5.0, 80, 5, "MEASURED"), "b": (3.0, 60, 100, "MEASURED")})
    check(p["to"] == "b", "pick: an owned account goes before a lent one, even one resetting sooner")
    p = pk({"a": (0.3, 30, 50, "MEASURED"), "lent": (5.0, 80, 100, "MEASURED")})
    check(p["to"] == "lent" and "may draw 30%" in p["why"], "pick: only the lent one fit, 20% used -> may draw 30% "
          "(to 50%)")
    p = pk({"a": (0.3, 30, 50, "MEASURED"), "lent": (5.0, 45, 100, "MEASURED")})
    check(p["state"] == "KEEP" and "lent, allowance 0%" in p["why"], "pick: lent account 55% used early in his week "
          "-> refused (50% rule)")
    p = pk({"a": (0.3, 30, 50, "MEASURED"), "lent": (5.0, 40, 10, "MEASURED")})
    check(p["to"] == "lent", "pick: near his reset, 40% left -> may draw toward the 10% floor")
    p = pk({"a": (0.3, 30, 50, "MEASURED"), "lent": (5.0, 15, 10, "MEASURED")})
    check(p["state"] == "KEEP", "pick: near his reset, 15% left -> 5% to the floor < 10% minimum: refused")
    off = {"lent_accounts": {"lent": dict(LENT_RULES["lent_accounts"]["lent"],
                                          off_limits_through="2099-01-01T00:00:00-07:00")}}
    check(pk({"a": (0.3, 30, 50, "MEASURED"), "lent": (5.0, 90, 100, "MEASURED")}, lent=off)["state"] == "KEEP",
          "pick: lent account off-limits -> never a target")
    p = pk({"lent": (5.0, 45, 100, "MEASURED"), "b": (3.0, 60, 20, "MEASURED")}, cur="lent")
    check(p["to"] == "b" and "lent account allowance" in p["why"], "pick: ON a lent account past its allowance -> "
          "switch to an owned one")
    check(AP.validate(PICK_RULE) == [], "rule: the test rule validates")
    check(len(AP.validate(dict(PICK_RULE, act="switch", hold=["x"], rank="r"))) == 3, "rule: act switch / bad hold / "
          "bad rank are refused")
    # the real schedule: the rule is data, enabled, valid, and its lent rules are the allocator's file with the
    # owner's lent line (50% / 10% floor); no account is named in the schedule block
    sch = json.load(open(os.path.join(HERE, "dispatcher_schedule.json")))
    rule = sch.get("account_pick") or {}
    check(rule.get("enabled") and AP.validate(rule) == [], "schedule: account_pick enabled and valid")
    rules, fn2 = AP.load_lent(rule)
    pols = list(((rules or {}).get("lent_accounts") or {}).values())
    check(fn2 is not None and any(p.get("max_used_by_us_pct") == 50 and p.get("floor_pct_left") == 10 for p in pols),
          "schedule: lent_rules loads the allocator's lent_accounts (50% early, 10% floor) and lent_allowance")
    names = set(rules.get("lent_accounts") or {}) if rules else set()
    blob = json.dumps(rule)
    check(not any(n in blob for n in names), "schedule: the account_pick block names no account")
    code = open(os.path.join(HERE, "account_pick.py")).read()
    check(not any(n in code for n in names) and "@" not in code, "account_pick.py names no account or email")


def pobs(now, accts, cur="a", **kw):
    o = obs(**kw)
    o["roles"] = robs(accounts_status(now, accts), account=cur)
    o["roles"]["lent"] = lambda: (LENT_RULES, lent_fn())
    return o


def test_account_pick_dispatch():
    now = at_local("08:00")
    keep = {"a": (2.0, 40, 50, "MEASURED"), "b": (3.0, 60, 20, "MEASURED")}
    low = {"a": (0.3, 30, 50, "MEASURED"), "b": (3.0, 60, 20, "MEASURED")}
    # role launch, SWITCH: held once per slot, alarm names the target, the pick is noted on change only
    st = fresh()
    sch = sched(roles=[conductor()], account_pick=PICK_RULE)
    a = D.decide(sch, st, pobs(now, low), now, True)
    check([x["do"] for x in a if x["do"].startswith("role")] == ["role_hold"] and "account switch" in
          [x for x in a if x["do"] == "role_hold"][0]["why"], "SWITCH: the role launch is held")
    ap = [x for x in a if x["do"] == "account_pick"]
    al = [x for x in a if x["do"] == "alarm" and x["kind"].startswith("account:")]
    check(len(ap) == 1 and ap[0]["note"] and ap[0]["to"] == "b" and ap[0]["ticket"] == "DISPATCHER_ALARMS_X",
          "SWITCH: one account_pick record, noted on the ledger (alarm item)")
    check(len(al) == 1 and al[0]["kind"] == "account:switch:b" and "claude-account use b" in al[0]["why"],
          "SWITCH: alarm names the account to switch to")
    check(not st["roles"]["Conductor"]["done"], "SWITCH: the slot stays due (not marked)")
    a = D.decide(sch, st, pobs(now + 120, low), now + 120, True)
    check(not [x for x in a if x["do"].startswith("role")], "SWITCH tick 2: the hold is journaled once per slot")
    check([x["note"] for x in a if x["do"] == "account_pick"] == [False], "SWITCH tick 2: unchanged pick not re-noted")
    a = D.decide(sch, st, pobs(now + 240, keep), now + 240, True)
    rl = [x for x in a if x["do"] == "role_launch"]
    check(rl and rl[0]["account"] == "a" and "account a (KEEP)" in rl[0]["why"], "KEEP after the switch line clears: "
          "launched, the note names the account")
    check([x["note"] for x in a if x["do"] == "account_pick"] == [True], "KEEP: the changed pick is noted")
    # ring / recover
    t0 = at_local("09:00")
    st = fresh()
    a = stall(sch, st, pobs(t0, low), t0)
    check("ring" not in kinds(a) and [x for x in a if x["do"] == "hold" and "ring held" in x["why"]],
          "SWITCH: the ring is held")
    check(not st["wakes"], "SWITCH: a held ring spends no wake cap")
    st = fresh()
    a = stall(sch, st, pobs(t0, keep), t0)
    r = [x for x in a if x["do"] == "ring"]
    check(r and r[0]["account"] == "a", "KEEP: rung, the ring records the account")
    st = fresh()
    a = stall(sch, st, pobs(t0, keep, cur=None), t0)
    check("ring" in kinds(a) and [x for x in a if x.get("kind") == "account:unmeasured"],
          "UNMEASURED: kept (rung) and alarmed")
    st = fresh()
    a = stall(sched(roles=[], account_pick=dict(PICK_RULE, hold=["role_launch"])), st, pobs(t0, low), t0)
    check("ring" in kinds(a), "SWITCH with ring not under hold: rung")
    st = fresh()
    a = stall(sched(roles=[], account_pick=dict(PICK_RULE, act="switch")), st, pobs(t0, low), t0)
    check("ring" in kinds(a) and [x for x in a if x.get("kind") == "account:unmeasured" and "unusable" in x["why"]],
          "an unusable rule holds nothing and is alarmed")
    st = fresh()
    st["seats"] = {"FOUNDRY": {"session_id": "sid-9", "dead_since": t0 - 10000}}
    a = D.decide(sch, st, pobs(t0, low, sessions=[sess("AGENT BENCH", "busy", "b")]), t0, True)
    check("recover" not in kinds(a) and [x for x in a if x["do"] == "hold" and "recover held" in x["why"]]
          and not st["recovers"], "SWITCH: the recover is held")
    st = fresh()
    st["seats"] = {"FOUNDRY": {"session_id": "sid-9", "dead_since": t0 - 10000}}
    a = D.decide(sch, st, pobs(t0, keep, sessions=[sess("AGENT BENCH", "busy", "b")]), t0, True)
    check([x for x in a if x["do"] == "recover" and x["account"] == "a"], "KEEP: recovered, with the account")
    st = fresh()
    a = stall(sched(roles=[]), st, pobs(t0, low), t0)
    check("ring" in kinds(a) and "account_pick" not in kinds(a), "no account_pick block: no pick, no hold")
    st = fresh()
    a = stall(sch, st, pobs(t0, low, ticket={}), t0)
    check("account_pick" not in kinds(a), "nothing to release: the pick is not made")


def main():
    for t in (test_parse_peek, test_wake_and_owner, test_blind_pause_roles_caps, test_verify_retry, test_dead_recover,
              test_never_adopt_or_resume_a_stranger, test_review_fixes, test_doorbell, test_end_to_end, test_dry_run, test_alarm_rate, test_review_s, test_seat_rule, test_ringed_next_rechecks_owner,
              test_role_reading_and_band, test_role_gates, test_role_economy_and_alarms,
              test_role_real_schedule_caps_and_ops_bands, test_role_execute_and_dry, test_review_q,
              test_review_r, test_account_pick_rule, test_account_pick_dispatch):
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
