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
    check(not os.path.exists(doorbell.armed_path("FOUNDRY", root)), "doorbell disarms after a ring")

    def superseded():
        res["s"] = doorbell.wait("FOUNDRY", "sid", root=root, max_wait=20, poll=0.05)
    th = threading.Thread(target=superseded)
    th.start()
    time.sleep(0.3)
    doorbell._write_json_atomic(doorbell.armed_path("FOUNDRY", root), {"pid": -7})
    th.join(10)
    check(res.get("s", (None,))[0] == 0 and "superseded" in res["s"][1], "doorbell: a newer arm supersedes the old")
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


def main():
    for t in (test_parse_peek, test_wake_and_owner, test_blind_pause_roles_caps, test_verify_retry, test_dead_recover,
              test_doorbell, test_end_to_end, test_dry_run, test_alarm_rate, test_seat_rule):
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
