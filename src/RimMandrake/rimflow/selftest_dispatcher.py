#!/usr/bin/env python3
"""selftest_dispatcher.py — RimFlow v3.0 Dispatcher (dispatcher.py) and its wake channel (doorbell.py).

Covers the §6 acceptance list with SIMULATED windows (no real Claude window is started here):
  wake an idle window      decide() rings; a real doorbell.wait() in a thread (the simulated window) is woken, takes a
                           lease in its fake clone's shard, and the next tick VERIFIES the hand-off and notes it
  recover a dead one       a seat missing from `claude agents` is resumed (fake runner sees `--resume <session>` and
                           AGENT_SEAT), and the next tick sees it back
  never read his presence  a bridge/game-up/deploy ticket is rung exactly as with him away (owner 2026-10-30), no
                           ring carries an owner line, and an `owner` observer that raises is never called; the
                           dispatcher has no game call at all
plus retry/give-up, caps, PAUSE, blind instrument, dry-run writes nothing, doorbell supersede/orphan, and the
DISPATCHER seat's ledger rule (note only). Nothing outside a temp dir is touched.
"""
import copy
import json
import os
import shutil
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


def _no_presence():
    raise AssertionError("the dispatcher read the owner's presence (owner 2026-10-30: never)")


def obs(sessions=None, ticket=None, armed=True, events=(), consumed=None, agents_ok=True,
        paused=None):
    return {"paused": paused,
            "agents": {"state": "MEASURED", "sessions": sessions if sessions is not None
                       else [sess(), sess("AGENT BENCH", "busy", "b")]}
            if agents_ok else {"state": "UNMEASURED", "why": "x"},
            "owner": _no_presence,          # the retired presence observer: calling it fails the test
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

    for need in D.GAME_NEEDS:
        st = {"seats": {}, "wakes": [], "recovers": [], "alarms": {}}
        r = [a for a in stall(sch, st, obs(ticket={"id": "GAME_THING_DO_IT", "needs": need})) if a["do"] == "ring"]
        check(len(r) == 1 and st["seats"]["FOUNDRY"]["ring"]["ticket"] == "GAME_THING_DO_IT"
              and "owner" not in r[0]["message"].lower(),
              "ticket needs %s: rung like any other, no owner line, presence never read" % need)
    st = {"seats": {}, "wakes": [], "recovers": [], "alarms": {}}
    check(kinds(stall(sch, st, obs(ticket={}))) == [], "empty queue: an idle window is left alone")
    st = {"seats": {}, "wakes": [], "recovers": [], "alarms": {}}
    a = stall(sch, st, obs(armed=False))
    check(kinds(a) == ["alarm"] and a[0]["kind"] == "unwakeable:FOUNDRY", "no doorbell armed: UNWAKEABLE alarm")
    check(a[0].get("note") and a[0].get("conductor_log"), "UNWAKEABLE reaches the ledger and the Conductor, not only the journal")
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


def test_answered_ring_is_not_no_handoff():
    """FOUNDRY_RINGS_FIX_ANSWERED_READS_NO_HANDOFF: a seat that answers in its ledger is woke_answered and escalates as
    seat_declined (the queue), a silent one stays woke_no_handoff and idle_full_queue (the window)."""
    sch = sched(caps=D.load_schedule()["caps"], no_handoff={"rering_s": [300, 900, 1800], "escalate_after": 3})
    for ev, want_do, want_alarm in (
            ({"event": "note", "id": "PEEKED", "text": "post-trial work\n held"}, "woke_answered", "seat_declined:FOUNDRY"),
            ({"event": "implemented", "id": "HELD"}, "woke_answered", "seat_declined:FOUNDRY"),
            ({"event": "lease", "action": "renew", "id": "HELD"}, "woke_no_handoff", "idle_full_queue:FOUNDRY"),
            (None, "woke_no_handoff", "idle_full_queue:FOUNDRY")):
        st = {"seats": {}, "wakes": [], "recovers": [], "alarms": {}}
        o = obs(consumed={"consumed_at": 1.0}, events=[dict(ev, ts="2999-01-01T00:00:00Z")] if ev else [])
        now, seen = 1000.0, []
        while now < 1000.0 + 3 * 3600:
            seen += D.decide(sch, st, o, now, True)
            now += sch["tick_s"]
        ended = [a for a in seen if a["do"] in ("woke_answered", "woke_no_handoff")]
        alarms = [a for a in seen if a["do"] == "alarm"]
        check(len(ended) >= 3 and {a["do"] for a in ended} == {want_do} and all(a["note"] for a in ended),
              "%r ends each ring as %s (%r)" % (ev, want_do, sorted({a["do"] for a in ended})))
        check(alarms and {a["kind"] for a in alarms} == {want_alarm} and alarms[0]["conductor_log"]
              and alarms[0]["note"], "%r escalates as %s" % (ev, want_alarm))
        check(st["seats"]["FOUNDRY"]["nh_streak"] == len(ended), "both kinds share the backoff streak")
        if want_do == "woke_answered":
            check(" ".join((ev.get("text") or "").split()) in alarms[0]["why"] and "the queue" in alarms[0]["why"]
                  and ev["id"] in alarms[0]["why"], "the alarm carries the seat's own answer, folded to one line: %r"
                  % alarms[0]["why"])
    # a hand-off after answered rings ends the streak, and an answer alongside a claim is simply verified
    st = {"seats": {}, "wakes": [], "recovers": [], "alarms": {}}
    t0 = 1000.0
    D.decide(sch, st, obs(), t0, True)
    for t in range(1, 8):
        D.decide(sch, st, obs(), t0 + t * sch["tick_s"], True)
    ring = st["seats"]["FOUNDRY"]["ring"]
    both = [{"event": "note", "id": "A", "ts": D.iso(ring["rung_at"] + 1)},
            {"event": "lease", "action": "take", "id": "B", "ts": D.iso(ring["rung_at"] + 2)}]
    a = D.decide(sch, st, obs(consumed={"consumed_at": ring["rung_at"] + 1}, events=both),
                 ring["rung_at"] + sch["handoff_s"], True)
    check(kinds(a) == ["verified"], "a note plus a lease take is a hand-off, not an answer: %r" % kinds(a))


def test_new_ticket_skips_the_backoff():
    """A seat that declined ticket A is rung at the next tick for a different takeable top item, and only for that."""
    sch = sched(no_handoff={"rering_s": [1800], "escalate_after": 9})
    st = {"seats": {}, "wakes": [], "recovers": [], "alarms": {}}
    top = {"id": "A_ITEM", "needs": "offline"}
    o = obs(consumed={"consumed_at": 1.0}, ticket=top)
    now, seen = 1000.0, []
    def run(until):
        nonlocal now
        while now < until:
            seen.extend((now, a["ticket"]) for a in D.decide(sch, st, o, now, True) if a["do"] == "ring")
            now += sch["tick_s"]
    run(1000.0 + 1500)
    check([t for _, t in seen] == ["A_ITEM"], "one ring, then the backoff holds the same ticket: %r" % seen)
    ss = st["seats"]["FOUNDRY"]
    check(ss["cooldown_until"] > now and ss["nh_tickets"] == ["A_ITEM"], "backoff running, declined ticket recorded")
    top["id"] = "B_ITEM"
    run(now + sch["tick_s"])
    check([t for _, t in seen] == ["A_ITEM", "B_ITEM"], "a new top item rings inside the backoff: %r" % seen)
    run(now + 700)      # B declined as well: A coming back is no new work
    top["id"] = "A_ITEM"
    n = len(seen)
    run(now + 300)
    check(len(seen) == n, "a ticket already declined in this streak waits out the backoff: %r" % seen)
    st2 = {"seats": {"FOUNDRY": {"cooldown_until": 9e9}}, "wakes": [], "recovers": [], "alarms": {}}
    check(not [a for a in D.decide(sch, st2, o, 1000.0, True) if a["do"] == "ring"],
          "a plain cooldown (a give-up, no declined tickets) is never skipped")
    st3 = {"seats": {"FOUNDRY": {"cooldown_until": 9e9, "nh_tickets": ["GONE"], "nh_until": 5.0, "idle_since": 0.0}}, "wakes": [],
           "recovers": [], "alarms": {}}
    check(not [a for a in D.decide(sch, st3, o, 1000.0, True) if a["do"] == "ring"],
          "a give-up cooldown after a declined ticket is not the backoff: not skipped")
    st4 = {"seats": {"FOUNDRY": {"cooldown_until": 9e9, "nh_tickets": ["GONE"], "nh_until": 9e9, "idle_since": 0.0}}, "wakes": [],
           "recovers": [], "alarms": {}}
    held = dict(sch, caps=dict(sch["caps"], wakes_per_seat_hour=0))
    check([a["kind"] for a in D.decide(held, st4, o, 1000.0, True) if a["do"] == "alarm"] == ["cap:FOUNDRY"], "the cap held it")
    check(st4["seats"]["FOUNDRY"].get("cooldown_until") == 9e9, "no ring went out: the backoff still stands")
    peeks = [top["id"]]
    o2 = dict(o, peek=lambda seat: {"id": peeks.pop(), "needs": "offline"} if peeks else {"id": "A_ITEM", "needs": "offline"})
    rung = [a for a in D.decide(sch, {"seats": {"FOUNDRY": {"cooldown_until": 9e9, "nh_tickets": ["GONE"], "nh_until": 9e9, "idle_since": 0.0}},
                                      "wakes": [], "recovers": [], "alarms": {}}, o2, 1000.0, True) if a["do"] == "ring"]
    check(len(peeks) == 0 and [a["ticket"] for a in rung] == [top["id"]], "the ring carries the ticket it peeked: %r" % rung)


def test_alarm_delivery_and_lock():
    """An alarm nobody received keeps no rate-limit stamp; a broken ingest.lock stops no ring; an unreadable shard raises."""
    sch = sched(ledger_notes=True, alarm_item="X_Y")
    root = os.path.join(TMP, "deliv")
    os.makedirs(root, exist_ok=True)
    def boom(*x):
        raise OSError("disk")
    def alarm():
        return [{"do": "alarm", "kind": "k", "seat": "FOUNDRY", "why": "w", "note": True, "conductor_log": True}]
    st = {"seats": {}, "wakes": [], "recovers": [], "alarms": {}}
    base = {"lock": lambda: None, "publish": lambda n: "p", "note": lambda i, t: (True, "")}
    D.execute(alarm(), sch, st, root, True, 1.0, dict(base, conductor_log=boom))
    check("k" not in st["alarms"], "neither destination took it: no stamp, retried next tick")
    D.execute(alarm(), sch, st, root, True, 2.0, dict(base, conductor_log=lambda *x: "conductor log appended: p"))
    check(st["alarms"].get("k") == 2.0, "the log took it, the ledger did not: stamped")
    st["alarms"]["k"] = 2.0
    a = alarm()
    D.execute(a, sch, st, root, True, 3.0, dict(base, conductor_log=boom))
    check(st["alarms"]["k"] == 2.0 and "rate-limited" in a[0]["result"], "a rate-limited repeat keeps its stamp")
    fx = dict(base, lock=boom, conductor_log=lambda *x: "conductor log appended: p")
    acts = alarm()
    D.execute(acts, sch, st, root, True, 4.0e5, fx)
    check([x["kind"] for x in acts if x["do"] == "alarm"] == ["k", "tick:ingest_lock"], "lock failure alarms: %r" % acts)
    p = os.path.join(root, "infrastructure", "state", "ledger", "events")
    os.makedirs(os.path.join(p, "FOUNDRY.jsonl"), exist_ok=True)
    check(D.seat_events_since(os.path.join(root, "nope"), "FOUNDRY", "2026") == [], "no shard: no events")
    try:
        D.seat_events_since(root, "FOUNDRY", "2026")
        check(False, "an unreadable shard must raise")
    except OSError:
        pass


def test_no_handoff_rering_and_escalation():
    """FOUNDRY_IDLE_REWIRE_PARKS_ON_LANE_WAITS: a seat that consumes every ring and never claims, with work waiting,
    is rung again on the bounded no_handoff backoff (not after cooldown_s), and escalated after escalate_after."""
    real = D.load_schedule()
    nh = D.no_handoff_rule(real)
    check(nh["rering_s"] == [300, 900, 1800] and nh["escalate_after"] == 3 and max(nh["rering_s"]) < real["cooldown_s"],
          "real schedule: no_handoff.rering_s [300, 900, 1800] (bounded, all under cooldown_s), escalate_after 3")
    sch = sched(caps=real["caps"], no_handoff={"rering_s": [300, 900, 1800], "escalate_after": 3,
                                               "_doc": "ignored"})
    st = {"seats": {}, "wakes": [], "recovers": [], "alarms": {}}
    o = obs(consumed={"consumed_at": 1.0})          # the doorbell takes every ring at once; no hand-off ever
    now, rings, nhs, esc = 1000.0, [], [], []
    while now < 1000.0 + 4 * 3600:
        for a in D.decide(sch, st, o, now, True):
            if a["do"] == "ring":
                rings.append(now)
            elif a["do"] == "woke_no_handoff":
                nhs.append(now)
            elif a["do"] == "alarm" and a.get("kind") == "idle_full_queue:FOUNDRY":
                esc.append(a)
            elif a["do"] == "alarm":
                check(False, "no other alarm while re-ringing (caps hold): %r" % a)
        now += sch["tick_s"]
    gaps = [b - a for a, b in zip(rings, rings[1:])]
    # gap k = handoff_s (600, seen at the next tick) + rering_s[k-1] (seen at the next tick)
    want = [600 + 300, 600 + 900] + [600 + 1800] * (len(gaps) - 2)
    check(len(gaps) >= 4 and all(w <= g <= w + 2 * sch["tick_s"] for g, w in zip(gaps, want)),
          "re-ring gaps follow handoff_s + rering_s, bounded at the last step: %r (want ~%r)" % (gaps, want))
    check(max(gaps) < 600 + real["cooldown_s"], "no gap is the old handoff_s + cooldown_s (~70 min): %r" % gaps)
    check(len(nhs) >= 3 and len(esc) == len(nhs) - 2 and esc[0]["note"] and esc[0]["conductor_log"]
          and esc[0]["ticket"] == "DISPATCHER_ALARMS_X" and "3 consecutive" in esc[0]["why"],
          "escalation: an idle_full_queue alarm from the 3rd consecutive woke_no_handoff on (%d nh, %d esc: %r)"
          % (len(nhs), len(esc), esc[:1]))
    check(st["seats"]["FOUNDRY"]["nh_streak"] == len(nhs), "the streak counts every consecutive no-hand-off")
    # the alarm is rate-limited by alarm_every_s, and its first raise writes the Conductor's log line
    logged, noted = [], []
    fx = {"conductor_log": lambda sc, a, t: logged.append(a["why"]) or "logged",
          "note": lambda i, t: noted.append(i) or (True, ""), "publish": lambda n: "p"}
    st2 = {"seats": {}, "wakes": [], "recovers": [], "alarms": {}}
    for i, a in enumerate(esc[:2]):
        D.execute([dict(a)], sch, st2, os.path.join(TMP, "nh"), True, 5000.0 + i * 600, fx)
    check(len(logged) == 1 and noted == ["DISPATCHER_ALARMS_X"],
          "escalation: one conductor-log line and one ledger note per alarm_every_s (%r %r)" % (logged, noted))
    path = os.path.join(TMP, "conductor_log.md")
    out = D.conductor_log(sched(no_handoff={"conductor_log": path}), dict(esc[0]), 5000.0)
    with open(path, encoding="utf-8") as f:
        txt = f.read()
    check("DISPATCHER ESCALATION" in txt and "RAISE FIRST: FOUNDRY" in txt and path in out,
          "conductor_log appends a RAISE FIRST line to the configured path")
    check(D.conductor_log(sched(no_handoff={"conductor_log": None}), dict(esc[0]), 5000.0) == "conductor log off",
          "conductor_log null = off")
    # a hand-off ends the streak; an empty queue ends it too
    p = st["seats"]["FOUNDRY"].get("ring")
    if not p:
        now = st["seats"]["FOUNDRY"]["cooldown_until"] + 1
        D.decide(sch, st, o, now, True)
        p = st["seats"]["FOUNDRY"]["ring"]
    lease = {"event": "lease", "action": "take", "id": "SOME_ITEM_DO_IT", "ts": D.iso(p["rung_at"] + 30)}
    a = D.decide(sch, st, obs(consumed={"consumed_at": 1.0}, events=[lease]), p["rung_at"] + 120, True)
    check(kinds(a) == ["verified"] and "nh_streak" not in st["seats"]["FOUNDRY"], "a verified hand-off ends the streak")
    st3 = {"seats": {"FOUNDRY": {"nh_streak": 5, "idle_since": 0.0}}, "wakes": [], "recovers": [], "alarms": {}}
    D.decide(sch, st3, obs(ticket={}), 9000.0, True)
    check("nh_streak" not in st3["seats"]["FOUNDRY"], "an empty queue ends the streak (no work waiting)")
    # the first step after a hand-off is the short one again; a malformed block is a decide alarm, not a guess
    check(D.rering_after(nh, 1) == 300 and D.rering_after(nh, 2) == 900 and D.rering_after(nh, 9) == 1800,
          "rering_after: step k, capped at the last")
    bad = sched(no_handoff={"rering_s": []})
    st4 = {"seats": {"FOUNDRY": {"ring": {"ring_id": "FOUNDRY-1-1", "rung_at": 0.0, "rung_iso": D.iso(0.0),
                                          "ticket": "PT", "attempt": 1}}}, "wakes": [], "recovers": [], "alarms": {}}
    a = D.decide(bad, st4, obs(consumed={"consumed_at": 1.0}), 1000.0, True)
    check([x.get("kind") for x in a if x["do"] == "alarm"] == ["decide:FOUNDRY"] and "ring" in st4["seats"]["FOUNDRY"],
          "malformed no_handoff.rering_s: a decide alarm, the ring kept for the next tick (%r)" % a)
    # the ring text says waiting on a lane is not idle (the FOUNDRY 2026-10-29 answer)
    m = D.message("FOUNDRY", {}, {"id": "X_Y_Z"}, "FOUNDRY-1-1")
    check("NOT idle" in m and "lane job" in m and "rimflow note` on X_Y_Z" in m,
          "ring message: waiting on a lane/test is not idle; a no-claim answer says why in a note")


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
    a = D.decide(sch, st, obs(sessions=gone), 1100.0 + sch["dead_after_s"], True)
    check(kinds(a) == ["recover"] and "owner" not in a[0]["message"].lower(),
          "recover: the resumed session gets no owner-presence line")
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
    # LEDGER_TS_HARDEN_NONISO_AFTER_CUTOFF: a non-ISO ts string sorted after every cutoff and counted as new
    with open(sh, "a") as f:
        f.write(json.dumps({"seat": "FOUNDRY", "event": "claim", "id": "BAD_TS", "ts": "yesterday"}) + "\n")
        f.write(json.dumps({"seat": "FOUNDRY", "event": "claim", "id": "GOOD_TS", "ts": "2999-01-01T00:00:00Z"}) + "\n")
    skipped = []
    got = D.seat_events_since(sc, "FOUNDRY", p["rung_iso"], on_skip=skipped.append)
    check([e["id"] for e in got] == ["GOOD_TS"], "a non-ISO ts is never counted as new: %r" % [e["id"] for e in got])
    check([x["id"] for x in skipped] == ["BAD_TS"], "the skipped non-ISO ts is reported to the journal hook: %r" % skipped)
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
    # (review dispatcher-full #9: the lock is ACQUIRED and ledger notes are on, so the note really is called and raises)
    sch3 = sched(caps={"wakes_per_seat_hour": 1}, ledger_notes=True)
    sch3["max_retries"] = 0
    note_calls = []

    def raising_note(i, t):
        note_calls.append(i)
        raise subprocess.TimeoutExpired("rimflow", 120)
    boom = {"note": raising_note, "ring": lambda *x: None, "withdraw": lambda *x: "withdrawn",
            "publish": lambda n: "pushed", "lock": lambda: open(os.devnull)}
    os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "state_boom")
    try:
        t0 = 10000.0
        acts = D.tick(sch3, True, obs=obs(), now=t0, fx=boom)
        acts += D.tick(sch3, True, obs=obs(), now=t0 + 240, fx=boom)
        rings = []
        for i in range(2, 12):
            more = D.tick(sch3, True, obs=obs(), now=t0 + 240 * i, fx=boom)
            acts += more
            rings += [x for x in more if x["do"] == "ring"]
        failed = [x for x in acts if str(x.get("ledger", "")).startswith("note failed: TimeoutExpired")]
        check(note_calls and failed and len(failed) == len(note_calls),
              "M9 the note callback ran and raised, and each failure is recorded (%d call(s), %r)"
              % (len(note_calls), [(x["do"], x.get("kind"), x.get("ledger")) for x in acts if x.get("note")]))
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
    check(D.withdraw(root, "FOUNDRY", "R2")["outcome"] == "withdrawn"
          and not os.path.exists(doorbell.inbox_path("FOUNDRY", root)),
          "withdraw moves an unconsumed ring away")
    D.ring(root, "FOUNDRY", "R3", "x")
    check(D.withdraw(root, "FOUNDRY", "R2")["outcome"] == "withdrawn" and D.withdraw(root, "FOUNDRY", "R9")[
        "outcome"] == "absent" and os.path.exists(doorbell.inbox_path("FOUNDRY", root)),
        "withdraw never takes another ring (R2 already withdrawn, R9 never written)")


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
    check("scope_unconfirmed" not in src, "role_launch has no clock retirement of an unconfirmed run any more "
          "(dispatcher-full #1: busy until termination is established)")
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


def test_ringed_next_withholds_nothing():
    """Owner 2026-10-30 ("strip "when I come back to the machine" as an event for anything changing"): the wake
    message no longer says --ringed, `next --ringed` still parses, and `_choose` offers game work first as before."""
    import types
    from rimflow import cli
    sch = sched()
    st = {"seats": {}, "wakes": [], "recovers": [], "alarms": {}}
    r = [a for a in stall(sch, st, obs()) if a["do"] == "ring"]
    check(r and "next --seat FOUNDRY" in r[0]["message"] and "--ringed" not in r[0]["message"],
          "wake message runs plain next, no --ringed")
    check(cli.build_parser().parse_args(["next", "--ringed"]).ringed is True, "next --ringed still parses (no-op)")
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
        for ctx in ({}, {"hold_game": "owner back"}):
            got = cli._choose(None, "FOUNDRY", args, ctx, None)
            check(got["item"].id == "X_bridge", "ctx %s: the game item is still offered first" % sorted(ctx))
        cli.priority.rank = lambda *a, **k: []
        got = cli._choose(None, "FOUNDRY", args, {"hold_game": "owner back"}, None)
        check(got["kind"] == "claimable" and [c.id for c in got["claimable"]] == ["C_game-up", "C_offline"],
              "a stale hold_game key drops nothing from the claimable list")
    finally:
        cli.priority.rank, cli.reconcile.guard, cli._claimable, cli.reconcile.assess = saved


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
                                   "cache_read_input_tokens": 11227, "output_tokens": 4}}) == 49163,
          "run tokens: all four usage fields, price-weighted (the proof's trivial haiku run: 35242 raw, 49163 weighted: "
          "no TTL split -> the 1h write rate)")
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
    check("conductor.md" in a[0]["message"] and "bridge" in a[0]["message"],
          "launch prompt names the instructions and the no-bridge line")
    blind = a[0]["message"].lower()
    check(not any(w in blind for w in ("30000", "token", "budget", "cap ", "runway", "week left", "band", "green")),
          "F1: a token-blind role's launch message carries no budget, cap, band, runway or week (review T)")
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
    check(st["roles"]["Operations"]["alarms_seen"] == [], "W1: alarms open at first enable are no baseline: not seen")
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
    check("350 weighted tokens" in a[0]["why"] and "raw 150" in a[0]["why"] and "m-x" in a[0]["why"],
          "role_done records weighted and raw tokens and the model used")
    check(a[1]["ticket"] == "OPS_NEW_ONE" and a[1]["budget"] == 60000, "alarm run: noted on the alarm item, run cap")
    check(st["roles"]["Operations"]["alarms_seen"] == ["OPS_NEW_ONE", "OPS_OLD_ONE"]
          and "OPS_OLD_ONE" in a[1]["why"], "W1: one alarm run covers every unseen open alarm, the one open at enable too")
    check(st["roles"]["Operations"]["runs"][0]["tokens"] == 350 and st["roles"]["Operations"]["runs"][0]["raw_tokens"] == 150
          and st["roles"]["Operations"]["runs"][0]["token_unit"] == RL.TOKEN_UNIT,
          "spend recorded on the run (100 in + 50 out x5 = 350 weighted; raw 150)")
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


# Frozen copy of Operations' throttle_bands as of 2460d2cc0a~1 (before the owner neutralized them).
CON_BANDS_FROZEN = {"GREEN": {"runway_ge": 1.5, "session_helpers_max": 3, "quick_cap_x": 1.0, "slots": "all"},
                    "AMBER": {"runway_ge": 1.0, "session_helpers_max": 2, "quick_cap_x": 0.75, "slots": "last"},
                    "RED": {"runway_ge": 0.0, "session_helpers_max": 1, "quick_cap_x": 0.75, "slots": "last"},
                    "FLOOR": {"week_left_pct_lt": 10, "session_helpers_max": 0, "quick_cap_x": 0.75, "slots": "none"}}
OPS_BANDS_FROZEN = {"GREEN": {"runway_ge": 1.5, "quick_cap_x": 1.0, "slots": "all"},
                    "AMBER": {"runway_ge": 1.0, "quick_cap_x": 1.0, "slots": "quick"},
                    "RED": {"runway_ge": 0.0, "quick_cap_x": 0.75, "slots": "quick_one"},
                    "FLOOR": {"week_left_pct_lt": 10, "quick_cap_x": 0.75, "slots": "none"}}


def test_role_real_schedule_caps_and_ops_bands():
    sch = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "dispatcher_schedule.json")))
    roles = {r["name"]: r for r in sch["roles"]}
    c, o = roles["Conductor"], roles["Operations"]
    check(c["quick_token_cap"] == 450000 and c["daily_token_cap"] == 1350000 and c["session_week_pct_cap"] == 6,
          "schedule: Conductor caps 450,000 / 1,350,000 / 6%")
    check(o["run_token_cap"] == 450000
          and o["daily_token_cap"] >= o["economy_token_cap"] + o["run_token_cap"] * 2,
          "schedule: Operations daily cap fits economy + evening + one alarm run")
    for r, cap in ((c, c["quick_token_cap"]), (o, o["run_token_cap"])):
        for bn, b in r["throttle_bands"].items():
            check(b["slots"] == "none" or cap * b["quick_cap_x"] >= 285538,
                  "%s band %s: launches nothing or stays >= 285,538 (the measured Operations run, weighted)"
                  % (r["name"], bn))
    # The LIVE bands were neutralized (owner 2026-10-28: "Stop the whole account rated RED on runeway crap. Just do
    # the checkout."), so the rows below test the band MECHANISM on a frozen copy of the old Operations bands.
    o_old = dict(o, throttle_bands=OPS_BANDS_FROZEN)
    for r in sch["roles"]:
        check(all(b.get("slots", "all") == "all" and float(b.get("quick_cap_x", 1.0)) >= 1.0
                  for b in r["throttle_bands"].values()),
              '%s live bands never restrict (owner 2026-10-28: "Stop the whole account rated RED on runeway crap")'
              % r["name"])
    base = at_local("07:30")
    ev = at_local("19:30")

    def run(now, **kw):
        st = fresh()
        if now == ev:                      # the morning slot is long past (else it is reported missed first)
            st["roles"] = {"Operations": {"done": {"%s 07:30" % RL.day_of(ev): "x"}, "runs": []}}
        return st, role_acts(rdecide([dict(o_old, enabled=True, off_file=os.path.join(TMP, "OPERATIONS_OFF"),
                                          clone=os.path.join(TMP, "clone"))], st,
                                     robs(ops_status(now, **kw)), now))
    st, a = run(base, runway=2.0)
    check(a and a[0]["mode"] == "economy" and a[0]["budget"] == 550000, "Ops GREEN 07:30: economy pass")
    st, a = run(base, runway=1.2)
    check([x["do"] for x in a] == ["role_hold"] and "band AMBER" in a[0]["why"], "Ops AMBER 07:30: no economy pass")
    st, a = run(ev, runway=1.2)
    check(a and a[0]["do"] == "role_launch" and a[0]["budget"] == 450000, "Ops AMBER 19:30: quick run, 450,000")
    st, a = run(ev, runway=0.5)
    check(a and a[0]["do"] == "role_launch" and a[0]["budget"] == 337500, "Ops RED 19:30: the one quick run, 337,500")
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
        a = role_acts(rdecide([dict(o_old, enabled=True, off_file=os.path.join(TMP, "OPERATIONS_OFF"),
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
    check(rec["scope"] == "claude-seat-BENCH-rm-role-conductor-1.scope" and rec["marker"] == "rm-role-conductor-1"
          and len(calls) == 1, "launch: the scope is named by the launcher (claude-seat-<seat>-<unit>), no MainPID query")
    check("CLAUDE_SCOPE_UNIT=claude-seat-BENCH-rm-role-conductor-1" in argv and "RM_ROLE_UNIT=rm-role-conductor-1" in argv,
          "launch: the unit tells claude_bounded the scope name and marks every process of the run")
    # pre_launch (review AA brief AA7): the Arbiter's tiers.json is produced inside the unit before claude starts
    pre_role = dict(role, pre_launch=["python3", "src/x y/arbiter_tiers.py"])
    pa = RL.launch_argv(pre_role, "u-pre", "it's \"msg\" $HOME", "/o", "/e", "/opt/bin/claude")
    j = pa.index("--")
    check(pa[j + 1:j + 3] == ["/bin/sh", "-c"] and pa[j + 4] == "role-pre-launch"
          and pa[j + 5].endswith("claude_bounded.sh") and pa[j + 6:j + 8] == ["-p", "it's \"msg\" $HOME"],
          "pre_launch: sh -c wraps the step, claude's argv stays positional and unquoted")
    with tempfile.TemporaryDirectory() as pd:
        mark, errf = os.path.join(pd, "ran"), os.path.join(pd, "err")
        for pre, want_rc, want_out in ((["sh", "-c", "echo PRE; touch '%s'" % mark], 0, "ARGS:-p|it's \"msg\" $HOME"),
                                       (["false"], 1, "")):
            if os.path.exists(mark):
                os.remove(mark)
            sa = RL.launch_argv(dict(role, pre_launch=pre), "u", "it's \"msg\" $HOME", "/o", "/e", "/opt/bin/claude")
            k = sa.index("--")
            body = sa[k + 1:]
            body = body[:4] + ["sh", "-c", 'printf "ARGS:%s|%s" "$1" "$2"', "fake-claude"] + body[5:7]
            with open(errf, "w") as ef:
                p = subprocess.run(body, stdout=subprocess.PIPE, stderr=ef, text=True, timeout=30)
            check(p.returncode == want_rc and p.stdout == want_out and (want_rc != 0 or os.path.exists(mark))
                  and (want_rc != 0 or "PRE" in open(errf).read()),
                  "pre_launch %s: rc %s, stdout %r (claude's JSON alone), pre-step stdout to stderr"
                  % (pre[0], p.returncode, p.stdout))
    try:
        RL.launch_argv(dict(role, pre_launch="python3 x.py"), "u", "m", "/o", "/e", "/opt/bin/claude")
        check(False, "pre_launch as a string is refused")
    except ValueError:
        check(True, "pre_launch as a string is refused")
    # a list of argvs runs in order, each only after the one before exited 0 (the Arbiter: isolated_evidence.py,
    # then arbiter_tiers.py; ARBITER_BUILD_LAUNCH_ON_ANY_PENDING_WORK item 3)
    with tempfile.TemporaryDirectory() as pd:
        log, errf = os.path.join(pd, "log"), os.path.join(pd, "err")
        for steps, want_rc, want_log, want_out in (
                ([["sh", "-c", "echo one >> '%s'" % log], ["sh", "-c", "echo two >> '%s'" % log]], 0, "one\ntwo\n",
                 "ARGS:-p|m"),
                ([["sh", "-c", "echo one >> '%s'; exit 3" % log], ["sh", "-c", "echo two >> '%s'" % log]], 3,
                 "one\n", "")):
            if os.path.exists(log):
                os.remove(log)
            try:
                sa = RL.launch_argv(dict(role, pre_launch=steps), "u", "m", "/o", "/e", "/opt/bin/claude")
            except ValueError as e:
                check(False, "pre_launch as a list of argvs is accepted (%s)" % e)
                continue
            body = sa[sa.index("--") + 1:]
            body = body[:4] + ["sh", "-c", 'printf "ARGS:%s|%s" "$1" "$2"', "fake-claude"] + body[5:7]
            with open(errf, "w") as ef:
                p = subprocess.run(body, stdout=subprocess.PIPE, stderr=ef, text=True, timeout=30)
            got_log = open(log).read() if os.path.exists(log) else ""
            check((p.returncode, got_log, p.stdout) == (want_rc, want_log, want_out),
                  "pre_launch list: rc %s, steps ran %r, claude ran %s" % (p.returncode, got_log, bool(p.stdout)))
    for bad in ([["python3", "x.py"], []], [["python3"], "x.py"], [[]]):
        try:
            RL.launch_argv(dict(role, pre_launch=bad), "u", "m", "/o", "/e", "/opt/bin/claude")
            check(False, "pre_launch %r is refused" % (bad,))
        except ValueError:
            check(True, "pre_launch %r is refused" % (bad,))
    calls.clear()
    RL.stop("u", "s.scope", runner=fake_run)
    check(calls == [["systemctl", "--user", "stop", "--no-block", "s.scope"],
                    ["systemctl", "--user", "stop", "--no-block", "u"]],
          "stop: scope first, then the unit, each its own call")
    # execute: a launch records the run; a failed launch records nothing
    sch = sched(roles=[role])
    st = fresh()
    act = {"do": "role_launch", "role": "Conductor", "unit": "U1", "message": "m", "ticket": "ROLES_ITEM_X",
           "note": True, "mode": "quick", "budget": 30000, "slot": "k", "band": "GREEN", "why": "w",
           "blind": RL.blind("Conductor", "launched", "quick", "rm-role-conductor-1")}   # as decide builds it
    noted = []
    fx = {"note": lambda i, t: noted.append((i, t)) or (True, ""), "publish": lambda n: "p", "lock": lambda: open(os.devnull),
          "role_launch": lambda *a: (True, "unit U1 started", {"out": "o", "err": "e", "scope": "s"})}
    D.execute([dict(act)], sch, st, root, True, 100.0, fx)
    run = st["roles"]["Conductor"]["runs"][0]
    check(run["state"] == "running" and run["budget"] == 30000 and run["scope"] == "claude-seat-BENCH-U1.scope"
          and run["marker"] == "U1", "execute: the run is recorded with the scope and marker named at creation")
    check(noted and noted[0] == ("ROLES_ITEM_X", "dispatcher: Conductor quick run: launched"),
          "execute: the launch is noted on the ledger, the fixed outcome")
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
    # the shipped schedule: at most the wave-1 set enabled (runbook step 14 enables it), Conductor and Operations
    # launchable once enabled
    real = D.load_schedule()
    check(not wave1_problems(real), "shipped schedule within wave 1: %s" % (wave1_problems(real) or "ok"))
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
    check(ok and rec["scope"] == "claude-seat-BENCH-UQ2.scope" and len(calls) == 1,
          "Q4 launched: the scope is named, never looked up (no MainPID query to fail)")
    calls.clear()

    def pid_then_stop(argv, **kw):
        calls.append(argv)
        return subprocess.CompletedProcess(argv, 0, "777\n" if "MainPID" in argv else "", "")
    RL.stop("UQ2", None, runner=pid_then_stop, seat="BENCH")
    check(calls[-2:] == [["systemctl", "--user", "stop", "--no-block", "claude-seat-BENCH-777.scope"],
                         ["systemctl", "--user", "stop", "--no-block", "UQ2"]],
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
    cb = CON_BANDS_FROZEN
    check(real["Conductor"].get("after_role") == "Operations" and "after_role" in con_md
          and cb["AMBER"]["slots"] == cb["RED"]["slots"] == "last",
          "Q7 Conductor runs after Operations (schedule + conductor.md); AMBER/RED keep the 20:00 check (schedule bands; "
          "the role file carries no band text since review T, F6)")
    # band mechanism on the frozen pre-2460d2cc0a bands (the live ones were neutralized by owner order, 2026-10-28)
    rc = dict(real["Conductor"], throttle_bands=CON_BANDS_FROZEN, enabled=True, clone=os.path.join(TMP, "clone"),
              off_file=os.path.join(TMP, "CQ_OFF"))
    ro = dict(real["Operations"], throttle_bands=OPS_BANDS_FROZEN, enabled=True, clone=os.path.join(TMP, "clone"), off_file=os.path.join(TMP, "OQ_OFF"))
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
    check([(x["role"], x["budget"]) for x in a if x["do"] == "role_launch" and x["role"] == "Conductor"] == [("Conductor", 337500)],
          "Q7 Conductor AMBER 20:00, after the 19:30 Operations run: launches at 337,500 (450,000 x 0.75)")
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
    ro = dict(real["Operations"], throttle_bands=OPS_BANDS_FROZEN, enabled=True, clone=os.path.join(TMP, "clone"), off_file=os.path.join(TMP, "OR_OFF"))
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
    # C: a blind first reading reads no alarms (nothing pruned, nothing run); the first MEASURED one runs the open
    # alarm once (review W, W1: no baseline)
    st = fresh()
    noon = at_local("12:00")
    al = {"k": {"state": "OPEN", "item": "OPS_OPEN_BEFORE"}}
    a = role_acts(rdecide([operations()], st, robs(None), noon))
    check(not st["roles"]["Operations"].get("alarms_seen") and any("alarm runs held" in x.get("why", "") for x in a),
          "R-C status.json missing on the first tick: no alarm read, and it says so")
    a = role_acts(rdecide([operations()], st, robs(ops_status(noon + 120, alarms=al)), noon + 120))
    check([x["mode"] for x in a if x["do"] == "role_launch"] == ["alarm"] and st["roles"]["Operations"]["alarms_seen"]
          == ["OPS_OPEN_BEFORE"], "R-C/W1 first MEASURED tick: the alarm open before enable runs once")
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

LENT_RULES = {"lent_accounts": {"lent": {"max_used_by_us_pct": 50, "floor_pct_left": 10,
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
    check(pk(three, lent=None)["state"] == "UNMEASURED" and pk(three, lent=None)["hold"],
          "pick: lent rules unreadable, no lent set ever read -> no switch, HELD (fail closed, review U N1)")
    check(pk(three, allowance=None)["state"] == "UNMEASURED", "pick: allocator not importable -> no switch")
    # lent accounts: data rule (<= 50% of his week used, only right after his reset, never under the 10% floor)
    p = pk({"a": (0.3, 30, 50, "MEASURED"), "lent": (5.0, 80, 5, "MEASURED"), "b": (3.0, 60, 100, "MEASURED")})
    check(p["to"] == "b", "pick: an owned account goes before a lent one, even one resetting sooner")
    p = pk({"a": (0.3, 30, 50, "MEASURED"), "lent": (5.0, 80, 150, "MEASURED")})
    check(p["to"] == "lent" and "may draw 30%" in p["why"], "pick: only the lent one fit, 20% used -> may draw 30% "
          "(to 50%)")
    p = pk({"a": (0.3, 30, 50, "MEASURED"), "lent": (5.0, 45, 150, "MEASURED")})
    check(p["state"] == "KEEP" and "lent, allowance 0%" in p["why"], "pick: lent account 55% used early in his week "
          "-> refused (50% rule)")
    p = pk({"a": (0.3, 30, 50, "MEASURED"), "lent": (5.0, 40, 10, "MEASURED")})
    check(p["state"] == "KEEP" and "lent, allowance 0%" in p["why"], "pick: 10 h before his reset, 40% left -> "
          "refused (owner 2026-10-27: fresh reset only; the end-of-week drawdown is withdrawn)")
    p = pk({"a": (0.3, 30, 50, "MEASURED"), "lent": (5.0, 80, 150, "MEASURED")})
    check(p["to"] == "lent" and "may draw 30%" in p["why"], "pick: 18 h after his reset, 20% used -> may draw 30%")
    p = pk({"a": (0.3, 30, 50, "MEASURED"), "lent": (5.0, 80, 108, "MEASURED")})
    check(p["state"] == "KEEP", "pick: 60 h after his reset, 20% used -> refused (outside the fresh-reset window)")
    p = pk({"a": (0.3, 30, 50, "MEASURED"), "lent": (5.0, 15, 10, "MEASURED")})
    check(p["state"] == "KEEP", "pick: near his reset, 15% left -> refused")
    off = {"lent_accounts": {"lent": dict(LENT_RULES["lent_accounts"]["lent"],
                                          off_limits_through="2099-01-01T00:00:00-07:00")}}
    check(pk({"a": (0.3, 30, 50, "MEASURED"), "lent": (5.0, 90, 150, "MEASURED")}, lent=off)["state"] == "KEEP",
          "pick: lent account off-limits -> never a target")
    p = pk({"lent": (5.0, 45, 150, "MEASURED"), "b": (3.0, 60, 20, "MEASURED")}, cur="lent")
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
    # the owner's ceiling is "up to 50%"; the plan may sit under it (48 since his 2026-10-28 card), never over it
    check(fn2 is not None and any(isinstance(p.get("max_used_by_us_pct"), (int, float))
                                  and 0 < p["max_used_by_us_pct"] <= 50 and p.get("floor_pct_left") == 10 for p in pols),
          "schedule: lent_rules loads the allocator's lent_accounts (<= 50% early, 10% floor) and lent_allowance")
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


# ---------------------------------------------------------------- weekday slots and ledger event triggers
# (item DISPATCHER_BUILD_WEEKDAY_AND_EVENT_TRIGGERS)

class FakeItem(object):
    def __init__(self, open_=True, raised=None, row=None):
        self.open, self.raised, self.row = open_, raised, row


class FakeWorld(object):
    def __init__(self, items):
        self.items = items


def lts(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def lread(events, items=None):
    return lambda: {"events": list(events), "world": FakeWorld(items or {})}


BASE_EV = {"seat": "BENCH", "event": "file", "id": "OLD_ONE", "ts": "2026-01-01T00:00:00Z"}


def arbiter(**kw):
    r = {"name": "Arbiter", "enabled": True, "instructions": "src/RimMandrake/rimflow/roles/arbiter.md",
         "seat": "BENCH", "clone": os.path.join(TMP, "clone"), "model": "opus", "ledger_item": "ROLES_ITEM_X",
         "off_file": os.path.join(TMP, "ARBITER_OFF"), "runs_local": ["11:00", "17:00"], "slot_when": "done_claims",
         "run_token_cap": 100000, "daily_token_cap": 250000}
    r.update(kw)
    return r


def producer(**kw):
    r = {"name": "Producer", "enabled": True, "instructions": "src/RimMandrake/rimflow/roles/producer.md",
         "seat": "BENCH", "clone": os.path.join(TMP, "clone"), "model": "opus", "ledger_item": "ROLES_ITEM_X",
         "off_file": os.path.join(TMP, "PRODUCER_OFF"), "runs_local": ["09:00"], "weekly_plan_weekday": "Wed",
         "run_token_cap": 100000, "daily_token_cap": 250000, "event_runs": ["plan_step_failure", "replan_request"],
         "event_runs_per_day": 1, "plan_scope": ["raised", "row"], "replan_note_prefix": "REPLAN REQUEST",
         "throttle_bands": {"GREEN": {"runway_ge": 1.5, "quick_cap_x": 1.0, "slots": "all"},
                            "RED": {"runway_ge": 0.0, "quick_cap_x": 0.75, "slots": "weekly"},
                            "FLOOR": {"week_left_pct_lt": 10, "quick_cap_x": 0.75, "slots": "none"}}}
    r.update(kw)
    return r


def lrobs(status, ledger, **kw):
    o = robs(status, **kw)
    o["ledger"] = ledger
    return o


def day_with_weekday(wd):
    """A local midnight at or after DAY0 whose weekday is wd (0 = Mon)."""
    t = DAY0
    while time.localtime(t).tm_wday != wd:
        t += 86400
    return t


def test_role_weekday_slots():
    check(RL.parse_slot("09:00") == (None, "09:00"), "slot: HH:MM runs every day")
    check(RL.parse_slot("Wed 09:00") == (frozenset([2]), "09:00"), "slot: 'Wed 09:00' -> Wednesday only")
    check(RL.parse_slot("mon,Thu 10:30") == (frozenset([0, 3]), "10:30"), "slot: 'Mon,Thu 10:30' -> two weekdays")
    for bad in ("Wday 09:00", "25:00", "9", "Wed 09:00 x", "Wed 9:7x"):
        try:
            RL.parse_slot(bad)
            check(False, "slot %r should be refused" % bad)
        except ValueError:
            check(True, "slot %r refused (ValueError)" % bad)
    wed, thu = day_with_weekday(2), day_with_weekday(3)
    inn = producer(name="Innovator", runs_local=["Mon,Thu 10:00", "Wed 15:00"], weekly_plan_weekday=None,
                   event_runs=None)
    check([t for t, _, _ in RL.slots(inn, wed)] == ["Wed 15:00"], "weekday filter: Wednesday keeps only 'Wed 15:00'")
    check([t for t, _, _ in RL.slots(inn, thu)] == ["Mon,Thu 10:00"], "weekday filter: Thursday keeps 'Mon,Thu 10:00'")
    check([m for _, m, _ in RL.slots(producer(), wed)] == ["weekly"], "Producer on Wednesday: the 09:00 is the weekly run")
    check([m for _, m, _ in RL.slots(producer(), thu)] == ["run"], "Producer on Thursday: the 09:00 is a daily run")
    # a weekday slot launches on its day only
    o = operations(runs_local=["Wed 07:30"], economy_pass_local=None, alarm_runs=False)
    tw, tt = RL.slot_epoch(wed, "07:30") + 60, RL.slot_epoch(thu, "07:30") + 60
    a = role_acts(rdecide([o], fresh(), robs(ops_status(tw)), tw))
    check([x["do"] for x in a] == ["role_launch"] and a[0]["slot"].endswith("Wed 07:30"),
          "'Wed 07:30' launches on Wednesday")
    a = role_acts(rdecide([o], fresh(), robs(ops_status(tt)), tt))
    check(a == [], "'Wed 07:30' does nothing on Thursday")
    a = role_acts(rdecide([operations(runs_local=["Wdy 07:30"])], fresh(), robs(ops_status(tw)), tw))
    check([x.get("kind") for x in a] == ["role:Operations:schedule"] and "unreadable" in a[0]["why"],
          "an unreadable weekday slot: alarm, no launch")
    # Producer weekly mode and the RED band (weekly only)
    led = lread([BASE_EV])
    t9w, t9t = RL.slot_epoch(wed, "09:00") + 60, RL.slot_epoch(thu, "09:00") + 60
    p = producer(after_role=None)
    a = role_acts(rdecide([p], fresh(), lrobs(ops_status(t9w), led), t9w))
    la = [x for x in a if x["do"] == "role_launch"]
    check(la and la[0]["mode"] == "weekly" and "weekly plan" in la[0]["message"], "Wednesday 09:00: weekly-plan run")
    a = role_acts(rdecide([p], fresh(), lrobs(ops_status(t9w, runway=0.3), led), t9w))
    la = [x for x in a if x["do"] == "role_launch"]
    check(la and la[0]["budget"] == 75000, "RED Wednesday: the weekly run goes at x0.75")
    a = role_acts(rdecide([p], fresh(), lrobs(ops_status(t9t, runway=0.3), led), t9t))
    check(not [x for x in a if x["do"] == "role_launch"] and any("band RED" in x.get("why", "") for x in a),
          "RED Thursday: the daily run is held (weekly only)")


def test_role_done_claims_gate():
    t = at_local("11:00")
    st = fresh()
    old_claim = dict(BASE_EV, event="close", id="BEFORE_BASELINE", ts=lts(t - 9000))
    led0 = lread([BASE_EV, old_claim])       # on the ledger at the baseline: seen, never a batch (N4: by identity)
    a = role_acts(rdecide([arbiter()], st, lrobs(ops_status(t - 7200), led0), t - 7200))
    check(st["roles"]["Arbiter"]["event_cursor"] == t - 7200 and [x["do"] for x in a] == ["role_hold"]
          and "baseline" in a[0]["why"], "Arbiter first seen enabled: baseline cursor, nothing run")
    a = role_acts(rdecide([arbiter()], st, lrobs(ops_status(t), lread([BASE_EV, old_claim])), t))
    check(not [x for x in a if x["do"] == "role_launch"] and any("no done claim" in x.get("why", "") for x in a),
          "11:00 with only claims before the baseline: slot held, no batch")
    check(st["roles"]["Arbiter"]["done"].get("%s 11:00" % RL.day_of(t)) == "no done claims",
          "the empty slot is spent (not retried every tick)")
    t17 = at_local("17:00")
    claims = [dict(BASE_EV, event="implemented", id="BUILT_ONE", ts=lts(t + 600)),
              dict(BASE_EV, event="close", id="CLOSED_ONE", ts=lts(t + 900)),
              dict(BASE_EV, event="note", id="NOISE", ts=lts(t + 950), text="x")]
    a = role_acts(rdecide([arbiter()], st, lrobs(ops_status(t17), lread([BASE_EV] + claims)), t17))
    la = [x for x in a if x["do"] == "role_launch"]
    check(la and "2 done claim(s)" in la[0]["why"] and "implemented BUILT_ONE" in la[0]["why"],
          "17:00 with an implemented + a close since the cursor: the batch launches, naming the oldest")
    check(st["roles"]["Arbiter"]["event_cursor"] == t17, "the launch moves the cursor to its own time")
    check([c[1] for c in RL.done_claims(claims, t)] == ["BUILT_ONE", "CLOSED_ONE"],
          "done_claims: implemented and close only, oldest first")
    st2 = fresh()
    st2["roles"] = {"Arbiter": {"done": {}, "runs": [], "event_cursor": t - 60}}
    a = role_acts(rdecide([arbiter()], st2, lrobs(ops_status(t), lread([BASE_EV] + claims[:1]), off="owner: off"), t))
    check([x["do"] for x in a] == ["role_hold"] and "off switch" in a[0]["why"], "claims pending + off file: held")


class BacklogItem(object):
    def __init__(self, state, owed, built_at=None):
        self.state, self._owed, self.open, self.raised, self.row = state, owed, True, None, None
        self.built_at = built_at

    def owed_levels(self):
        return list(self._owed)


def pwobs(t, events, items=None, stores=None, **kw):
    o = lrobs(ops_status(t), lread([BASE_EV] + events, items), **kw)
    if callable(stores):
        o["pending_stores"] = stores
    elif stores is not False:
        st = dict({"verdicts": [], "tiers_history": [], "cutoff": t - 86400 * 9}, **(stores or {}))
        o["pending_stores"] = lambda: st
    return o


def test_role_pending_work_gate():
    """ARBITER_BUILD_LAUNCH_ON_ANY_PENDING_WORK: a slot launches on ANY pending work, read from state; a launch that
    did not judge it leaves it pending."""
    t, t17 = at_local("11:00"), at_local("17:00")
    arb = arbiter(slot_when="pending_work")
    sha = "abcdef1234567890"

    def run(st, tt, *a, **kw):
        acts = role_acts(rdecide([arb], st, pwobs(tt, *a, **kw), tt))
        return [x for x in acts if x["do"] == "role_launch"], acts

    def based():
        st = fresh()
        st["roles"] = {"Arbiter": {"done": {}, "runs": [], "event_cursor": t - 60, "events_seen": []}}
        return st

    la, acts = run(based(), t, [])
    check(not la and any("nothing pending" in x.get("why", "") for x in acts), "pending_work: nothing pending: held")
    # a carried UNRESOLVED alone (no new claim on the ledger) starts a batch
    unres = {"item": "CARRIED", "sha": sha[:7], "disposition": "UNRESOLVED", "ts": lts(t - 86400 * 30)}
    la, _ = run(based(), t, [], stores={"verdicts": [unres]})
    check(la and "1 unresolved (first CARRIED)" in la[0]["why"], "pending_work: a carried UNRESOLVED alone launches")
    # an escape alone: work filed against an item after the Arbiter passed it, no check spec filed yet
    passed = {"item": "GOOD", "sha": sha, "disposition": "PASS", "ts": lts(t - 86400 * 20)}
    esc = dict(BASE_EV, event="file", id="GOOD_BROKE_LATER", ts=lts(t - 86400 * 10), caused_by="GOOD")
    la, _ = run(based(), t, [esc], stores={"verdicts": [passed]})
    check(la and "1 escapes (first GOOD_BROKE_LATER)" in la[0]["why"], "pending_work: an escape alone launches")
    spec = dict(BASE_EV, event="spawn", ts=lts(t - 3600), **{"from": "GOOD_BROKE_LATER", "for": "BENCH",
                                                               "name": "GOOD_CHECK_SPEC"})
    la, _ = run(based(), t, [esc, spec], stores={"verdicts": [passed]})
    check(not la, "pending_work: an escape whose check spec is filed is no longer pending")
    before = dict(esc, ts=lts(t - 86400 * 25))
    la, _ = run(based(), t, [before], stores={"verdicts": [passed]})
    check(not la, "pending_work: work filed BEFORE the pass is not an escape")
    # the verify backlog alone (an L4-only item is his, not pending)
    items = {"BUILT_L1": BacklogItem("built", ["L1", "L4"], lts(t - 3600))}
    la, _ = run(based(), t, [], items=items)
    check(la and "verify backlog (first BUILT_L1)" in la[0]["why"], "pending_work: a verify-backlog item launches")
    la, _ = run(based(), t, [], items={"ONLY_L4": BacklogItem("validated", ["L4"], lts(t - 3600)),
                                       "CLOSED": BacklogItem("closed", ["L1"], lts(t - 3600))})
    check(not la, "pending_work: L4-only and closed items are not the Arbiter's backlog")
    # a done claim, and a launch that never wrote a verdict: still pending at the next slot (nothing consumed)
    close = dict(BASE_EV, event="close", id="CLAIMED", sha=sha, ts=lts(t - 3600))
    st = based()
    la, _ = run(st, t, [close])
    check(la and "1 done claims (first CLAIMED)" in la[0]["why"], "pending_work: a done claim launches")
    st["roles"]["Arbiter"].pop("pending_launch", None)
    la, _ = run(st, t17, [close])
    check(la and "CLAIMED" in la[0]["why"],
          "pending_work: a launch that wrote no verdict consumed nothing: the claim launches the next slot too")
    final = {"item": "CLAIMED", "sha": sha[:9], "disposition": "FAIL-check", "ts": lts(t + 60)}
    la, _ = run(based(), t, [close], stores={"verdicts": [final]})
    check(not la, "pending_work: a final verdict (short sha) acknowledges the claim")
    la, _ = run(based(), t, [close], stores={"verdicts": [dict(final, disposition="UNRESOLVED")]})
    check(la, "pending_work: an UNRESOLVED verdict does not acknowledge it")
    for dec, want in (("PASS", False), ("AI", True), ("BOUNCE", True), ("HOLD", True)):
        la, _ = run(based(), t, [close], stores={"tiers_history": [{"item": "CLAIMED", "sha": sha, "decision": dec}]})
        check(bool(la) == want, "pending_work: tiers_history decision %s %s the claim" % (
            dec, "leaves pending" if want else "acknowledges"))
    # ARBITER_FIX_CLAIMS_AGE_OUT_UNJUDGED: a claim after the cutoff never ages out; one before it is not his queue
    old = dict(close, ts=lts(t - 86400 * 8))
    la, _ = run(based(), t, [old])
    check(la and "CLAIMED" in la[0]["why"], "pending_work: an unjudged close 8 days old (after the cutoff) is pending")
    la, _ = run(based(), t + 86400 * 364, [old], stores={"cutoff": t - 86400 * 9})    # 52 weeks: same slot, same DST
    check(la and "CLAIMED" in la[0]["why"], "pending_work: an unjudged close after the cutoff is pending a year on")
    pre = dict(close, ts=lts(t - 86400 * 10))
    la, _ = run(based(), t, [pre])
    check(not la, "pending_work: a close before the cutoff is the pre-enable backlog, not the Arbiter's queue")
    # blind stores launch (work may be pending), with the reason in the trigger
    def torn():
        raise ValueError("verdicts.jsonl line 3 is not JSON")
    la, _ = run(based(), t, [], stores=torn)
    check(la and "UNMEASURED" in la[0]["why"] and "line 3" in la[0]["why"], "pending_work: torn store: launch, said")
    la, _ = run(based(), t, [], stores=False)
    check(la and "no pending_stores reader" in la[0]["why"], "pending_work: no store reader: launch, said")
    # kinds can be narrowed; a bad kind is a schedule alarm, never a launch
    a2 = role_acts(rdecide([arbiter(slot_when="pending_work", pending_work=["verify_backlog"])], based(),
                           pwobs(t, [], stores={"verdicts": [unres]}), t))
    check(not [x for x in a2 if x["do"] == "role_launch"], "pending_work: kinds narrowed to the backlog ignore UNRESOLVED")
    for bad in ({"pending_work": ["escape"]}, {"pending_work": []}, {"claim_window_days": 0},
                {"claim_window_days": 7}, {"pre_launch_max_s": 0}, {"pre_launch_max_s": "600"},
                {"slot_when": "claims"}):
        a2 = role_acts(rdecide([arbiter(**dict({"slot_when": "pending_work"}, **bad))], based(), pwobs(t, []), t))
        check([x.get("kind") for x in a2] == ["role:Arbiter:schedule"], "pending_work: schedule %r refused" % (bad,))
    # the store reader: absent files are empty (never ran), a misspelt disposition is torn
    with tempfile.TemporaryDirectory() as d:
        v, h = os.path.join(d, "verdicts.jsonl"), os.path.join(d, "tiers_history.jsonl")
        c = os.path.join(d, "cutoff.json")
        check(RL.PW.read_stores(v, h, c) == {"verdicts": [], "tiers_history": [], "cutoff": None},
              "read_stores: absent files are empty, an absent cutoff is None")
        with open(v, "w") as f:
            f.write(json.dumps(dict(unres, disposition="PASSED")) + "\n")
        try:
            RL.PW.read_stores(v, h, c)
            check(False, "read_stores: an unknown disposition is refused")
        except ValueError:
            check(True, "read_stores: an unknown disposition is refused")


def test_role_arbiter_cutoff():
    """ARBITER_DECIDE_BACKLOG_NEVER_DRAINS (BENCH delegated ruling 2026-10-27): the Arbiter's queue is the work after
    the cutoff stamped at enable, oldest first; no stamp holds the slot with an alarm (never a launch over the whole
    pre-enable backlog). ARBITER_MEASURE_PRELAUNCH_EVIDENCE_TIME: pre_launch_max_s is its own bound."""
    t = at_local("11:00")
    cut = t - 86400 * 2

    def based():
        st = fresh()
        st["roles"] = {"Arbiter": {"done": {}, "runs": [], "event_cursor": t - 60, "events_seen": []}}
        return st

    def acts(role, events, **kw):
        return role_acts(rdecide([role], based(), pwobs(t, events, **kw), t))
    arb = arbiter(slot_when="pending_work")
    c1 = dict(BASE_EV, event="close", id="NEWER", sha="abcdef1234567890", ts=lts(cut + 7200))
    c2 = dict(BASE_EV, event="close", id="OLDER", sha="1234567abcdef890", ts=lts(cut + 60))
    a = acts(arb, [c1, c2], stores={"cutoff": None})
    check(not [x for x in a if x["do"] == "role_launch"]
          and [x.get("kind") for x in a if x["do"] == "alarm"] == ["role:Arbiter:cutoff"]
          and any("cutoff" in x.get("why", "") and "stamp" in x.get("why", "") for x in a),
          "cutoff: no stamp holds the slot with an alarm naming `stamp`, never a launch over the backlog")
    unres = {"item": "CARRIED", "sha": "abcdef1", "disposition": "UNRESOLVED", "ts": lts(t - 600)}
    a = acts(arbiter(slot_when="pending_work", pending_work=["unresolved"]), [], stores={"cutoff": None,
                                                                                         "verdicts": [unres]})
    check([x for x in a if x["do"] == "role_launch"], "cutoff: kinds that need no cutoff launch without one")
    a = acts(arb, [c1, c2], stores={"cutoff": cut})
    la = [x for x in a if x["do"] == "role_launch"]
    check(la and "2 done claims (first OLDER)" in la[0]["why"], "cutoff: done claims are listed oldest first")
    items = {"PRE": BacklogItem("built", ["L1"], lts(cut - 60)), "NONE": BacklogItem("validated", ["L2"])}
    check(not [x for x in acts(arb, [], items=items, stores={"cutoff": cut}) if x["do"] == "role_launch"],
          "cutoff: a backlog item built before the cutoff (or with no build time) is not the Arbiter's")
    items["POST"] = BacklogItem("built", ["L1"], lts(cut + 60))
    la = [x for x in acts(arb, [], items=items, stores={"cutoff": cut}) if x["do"] == "role_launch"]
    check(la and "1 verify backlog (first POST)" in la[0]["why"], "cutoff: a backlog item built after it is")
    # the stamp: written once, never overwritten; torn -> ValueError; read back as epoch
    with tempfile.TemporaryDirectory() as d:
        c = os.path.join(d, "arbiter", "cutoff.json")
        check(RL.PW.read_cutoff(c) is None, "stamp: absent -> None")
        RL.PW.stamp(c, "2026-10-30T09:00:00Z", by="BENCH", why="advisory enable")
        check(RL.PW.read_cutoff(c) == RL.PW.epoch("2026-10-30T09:00:00Z"), "stamp: read back")
        try:
            RL.PW.stamp(c, "2026-11-30T09:00:00Z", by="BENCH", why="again")
            check(False, "stamp: a second stamp is refused")
        except FileExistsError:
            check(RL.PW.read_cutoff(c) == RL.PW.epoch("2026-10-30T09:00:00Z"), "stamp: a second stamp is refused")
        with open(c, "w") as f:
            f.write('{"cutoff": "2026-1')
        try:
            RL.PW.read_cutoff(c)
            check(False, "stamp: a torn file raises ValueError")
        except ValueError:
            check(True, "stamp: a torn file raises ValueError")
    # pre_launch_max_s: its own budget, added to the run's wall bound and recorded on the run
    arb2 = arbiter(slot_when="pending_work", run_max_s=2700, pre_launch_max_s=1200)
    la = [x for x in acts(arb2, [c1], stores={"cutoff": cut}) if x["do"] == "role_launch"]
    check(la and la[0]["run_max_s"] == 3900, "pre_launch_max_s: the launch records run_max_s 2700 + 1200")
    check(RL.max_s_of({}, arb2) == 3900 and RL.max_s_of({"run_max_s": 3900}, arb2) == 3900
          and RL.max_s_of({}, arbiter(run_max_s=2700)) == 2700, "pre_launch_max_s: max_s_of sums it, absent = 0")


def test_role_event_skip_keeps_quota():
    """Review night r2: an event run skipped by the off switch or a band is not a run: it must not use the day's
    event_runs_per_day, so the event launches once the switch is gone (or the band allows it), the hold journalled
    once, not every tick. And daily_token_cap 0 is a cap of zero, not no cap."""
    t = at_local("13:00")
    items = {"PLAN_A": FakeItem(raised="2026-10-28T01:00:00Z")}
    fail = dict(BASE_EV, event="verify", id="PLAN_A", result="fail", ts=lts(t - 200))
    st = fresh()
    st["roles"] = {"Producer": {"done": {"%s 09:00" % RL.day_of(t): "launch"}, "runs": [], "event_cursor": t - 3600}}
    p = producer(after_role=None)
    a = role_acts(rdecide([p], st, lrobs(ops_status(t), lread([BASE_EV, fail], items), off="quiet"), t))
    check([x["do"] for x in a] == ["role_hold"] and "off switch" in a[0]["why"], "event + off switch: held %r" % a)
    a = role_acts(rdecide([p], st, lrobs(ops_status(t + 60), lread([BASE_EV, fail], items), off="quiet"), t + 60))
    check(a == [], "event + off switch: the hold is journalled once, not every tick %r" % a)
    a = role_acts(rdecide([p], st, lrobs(ops_status(t + 120), lread([BASE_EV, fail], items)), t + 120))
    la = [x for x in a if x["do"] == "role_launch"]
    check(la and la[0]["mode"] == "event", "off switch removed the same day: the event runs (quota unused) %r" % a)
    # band FLOOR blocks event runs; when the band lifts the same day, the event runs
    st = fresh()
    st["roles"] = {"Producer": {"done": {"%s 09:00" % RL.day_of(t): "launch"}, "runs": [], "event_cursor": t - 3600}}
    a = role_acts(rdecide([p], st, lrobs(ops_status(t, week_left=5), lread([BASE_EV, fail], items)), t))
    check(not [x for x in a if x["do"] == "role_launch"] and any("FLOOR" in x.get("why", "") for x in a),
          "event in FLOOR: not run %r" % a)
    a = role_acts(rdecide([p], st, lrobs(ops_status(t + 60, week_left=5), lread([BASE_EV, fail], items)), t + 60))
    check(a == [], "event in FLOOR: the hold is journalled once %r" % a)
    a = role_acts(rdecide([p], st, lrobs(ops_status(t + 120), lread([BASE_EV, fail], items)), t + 120))
    check([x for x in a if x["do"] == "role_launch"], "band lifts the same day: the event runs %r" % a)
    now = at_local("08:00")
    st = fresh()
    a = role_acts(rdecide([conductor(daily_token_cap=0)], st, robs(ops_status(now)), now))
    check([x["do"] for x in a] == ["alarm"] and "daily_token_cap" in a[0]["why"],
          "daily_token_cap 0: refused, not uncapped %r" % a)


def test_role_event_cap_refusal_keeps_quota():
    """ROLE_LAUNCH_REVIEW_FINISH_ROUND_FIVE: an event run REFUSED on daily_token_cap is not a run: it must not use the
    day's event_runs_per_day, so it launches the same day once it fits (a raised cap, a band that shrinks its
    budget). The refusal alarms once, not every tick."""
    t = at_local("13:00")
    items = {"PLAN_A": FakeItem(raised="2026-10-28T01:00:00Z")}
    fail = dict(BASE_EV, event="verify", id="PLAN_A", result="fail", ts=lts(t - 200))
    st = fresh()
    st["roles"] = {"Producer": {"done": {"%s 09:00" % RL.day_of(t): "launch"}, "event_cursor": t - 3600,
                                "runs": [{"day": RL.day_of(t), "tokens": 200000, "state": "done",
                                          "at": t - 3600, "unit": "u0", "budget": 100000}]}}
    p = producer(after_role=None)
    a = role_acts(rdecide([p], st, lrobs(ops_status(t), lread([BASE_EV, fail], items)), t))
    check([x["do"] for x in a] == ["alarm"] and "daily_token_cap" in a[0]["why"], "event over the daily cap: refused %r"
          % a)
    check(not [k for k in st["roles"]["Producer"]["done"] if " event" in k],
          "a refused event run does not use the day's event quota %r" % st["roles"]["Producer"]["done"])
    a = role_acts(rdecide([p], st, lrobs(ops_status(t + 60), lread([BASE_EV, fail], items)), t + 60))
    check(a == [], "event refused on the cap: alarmed once, not every tick %r" % a)
    p2 = producer(after_role=None, daily_token_cap=300000)
    a = role_acts(rdecide([p2], st, lrobs(ops_status(t + 120), lread([BASE_EV, fail], items)), t + 120))
    la = [x for x in a if x["do"] == "role_launch"]
    check(la and la[0]["mode"] == "event", "the cap leaves room the same day: the event runs (quota unused) %r" % a)


def test_role_event_key_same_second_twins():
    """ROLE_EVENT_KEY_WIDEN_SAME_SECOND_TWINS: two replan notes on one item in the same second are two events (their
    tsn differ), so a run that read the first does not swallow the second; a seen list written before the widening
    (int-second keys) still covers the events it named, so a deploy re-fires nothing."""
    ts, base = "2026-10-28T01:00:00Z", 1793174400 * 10 ** 9
    a = {"event": "note", "id": "PROD_ITEM", "text": "REPLAN REQUEST one", "ts": ts, "tsn": base + 100000000}
    b = dict(a, text="REPLAN REQUEST two", tsn=base + 700000000)
    ea = RL.replan_requests([a], 0, "PROD_ITEM", "REPLAN REQUEST")
    eb = RL.replan_requests([a, b], 0, "PROD_ITEM", "REPLAN REQUEST")
    rs = {"events_seen": [RL.event_key(e) for e in ea]}
    check(len(eb) == 2 and len(RL.unseen(eb, rs)) == 1,
          "a same-second twin note is a second event, unseen after a run read the first: %s %s" % (eb, rs))
    legacy = {"events_seen": ["%d|PROD_ITEM|replan request" % RL.utc_epoch(ts)]}
    check(RL.unseen(eb, legacy) == [], "an int-second seen list from before the widening still covers its events")
    check(all(int(e[0]) == RL.utc_epoch(ts) for e in eb), "an event's whole second is still its ts")
    z = RL.replan_requests([dict(a, tsn=base)], 0, "PROD_ITEM", "REPLAN REQUEST")
    zs = {"events_seen": [RL.event_key(e) for e in z]}
    check(len(RL.unseen(eb, zs)) == 2, "a new list whose only event fell on .000000 is not read as a legacy list: %s"
          % zs)


def test_role_review_r5():
    """Review r5 (role_launch.py): a negative quick_cap_x (a negative budget passes every cap) and an unknown band
    `slots` policy (slot_blocked would block nothing) are schedule errors, refused by validate_role."""
    for bad, word in (({"runway_ge": 0.0, "quick_cap_x": -1}, "quick_cap_x"),
                      ({"runway_ge": 0.0, "quick_cap_x": 1.0, "slots": "weeky"}, "slots")):
        try:
            RL.validate_role(dict(RL.ROLE_DEFAULTS, **producer(throttle_bands={"GREEN": bad})))
            check(False, "r5: band %r is refused" % bad)
        except ValueError as e:
            check(word in str(e), "r5: band %r is refused (%s)" % (bad, e))
    RL.validate_role(dict(RL.ROLE_DEFAULTS, **producer()))
    check(True, "r5: the fixture bands (all, weekly, none) still validate")


def test_role_review_night_r3():
    """Review night r3 (role_launch.py): a zero quick/economy cap is a cap, not a fall-back; one status.json read per
    tick; after_role chains decided in order; the unit's wall bound adds pre_launch_max_s to the DEFAULT run_max_s."""
    day = RL.day_of(at_local("08:00"))
    sl = RL.slots(conductor(quick_token_cap=0, run_token_cap=10000), day)
    check(sl and all(c == 0 for _, _, c in sl), "quick_token_cap 0: the slots carry cap 0, not run_token_cap %r" % sl)
    sl = RL.slots(operations(economy_token_cap=0), day)
    check(sl and sl[0][1] == "economy" and sl[0][2] == 0, "economy_token_cap 0: still the economy slot, cap 0 %r" % sl)
    now = at_local("19:30")
    st = fresh()
    ro = robs(ops_status(now))
    calls = []
    first = ro["ops"]
    ro["ops"] = lambda: calls.append(1) or first()
    rdecide([operations()], st, ro, now)
    check(len(calls) == 1, "one status.json read per tick: the alarm keys come from the reading's snapshot (%d)"
          % len(calls))
    order = [r["name"] for r in RL.decide_order([{"name": "C", "after_role": "B"}, {"name": "B", "after_role": "A"},
                                                 {"name": "A"}])]
    check(order == ["A", "B", "C"], "after_role chain: decided A, B, C %r" % order)
    order = [r["name"] for r in RL.decide_order([{"name": "X", "after_role": "Y"}, {"name": "Y", "after_role": "X"},
                                                 {"name": "Z"}])]
    check(sorted(order) == ["X", "Y", "Z"], "after_role cycle: every role still decided %r" % order)
    check(RL.scope_bound_s({"pre_launch_max_s": 1200}) == 1800 + 1200 + RL.SCOPE_GRACE_S,
          "unit bound: default run_max_s + pre_launch_max_s, as decide counts it")


def test_role_plan_failure_events():
    t = at_local("13:00")
    items = {"PLAN_A": FakeItem(raised="2026-10-28T01:00:00Z"), "PLAN_ROW": FakeItem(row="R3"),
             "OFF_PLAN": FakeItem(), "PLAN_CLOSED": FakeItem(open_=False, raised="x")}
    evs = [BASE_EV,
           dict(BASE_EV, event="block", id="OFF_PLAN", ts=lts(t - 300)),
           dict(BASE_EV, event="verify", id="PLAN_CLOSED", result="fail", ts=lts(t - 290)),
           dict(BASE_EV, event="verify", id="PLAN_A", result="pass", ts=lts(t - 280))]
    st = fresh()
    st["roles"] = {"Producer": {"done": {"%s 09:00" % RL.day_of(t): "launch"}, "runs": [], "event_cursor": t - 3600}}
    p = producer(after_role=None)
    a = role_acts(rdecide([p], st, lrobs(ops_status(t), lread(evs, items)), t))
    check(a == [], "no event run for: a block off the plan, a fail on a closed item, a verify pass")
    fail = dict(BASE_EV, event="verify", id="PLAN_A", result="fail", ts=lts(t - 200))
    blk = dict(BASE_EV, event="block", id="PLAN_ROW", ts=lts(t - 100))
    a = role_acts(rdecide([p], st, lrobs(ops_status(t), lread(evs + [fail, blk], items)), t))
    la = [x for x in a if x["do"] == "role_launch"]
    check(la and la[0]["mode"] == "event" and "verify fail on PLAN_A" in la[0]["why"] and "+1 more" in la[0]["why"],
          "a verify fail on a raised item (and a block on a rowed one): one event run, naming the oldest")
    check(la and la[0]["budget"] == 100000 and la[0]["slot"] == "%s event#1" % RL.day_of(t),
          "event run: run cap, keyed once per day")
    st["roles"]["Producer"]["runs"][:0] = []
    t2 = t + 3600
    blk2 = dict(BASE_EV, event="block", id="PLAN_A", ts=lts(t2 - 60))
    st["roles"]["Producer"]["runs"] = [{"unit": "u", "at": t, "day": RL.day_of(t), "budget": 100000, "mode": "event",
                                        "state": "done", "tokens": 50000, "item": "ROLES_ITEM_X"}]
    a = role_acts(rdecide([p], st, lrobs(ops_status(t2), lread(evs + [fail, blk, blk2], items)), t2))
    check(not [x for x in a if x["do"] == "role_launch"] and any("event_runs_per_day" in x.get("why", "") for x in a),
          "a second failure the same day: no second event run (per-day count), journaled once")
    a = role_acts(rdecide([p], st, lrobs(ops_status(t2 + 120), lread(evs + [fail, blk, blk2], items)), t2 + 120))
    check(a == [], "... and not journaled again on the next tick")
    # replan request
    st3 = fresh()
    st3["roles"] = {"Producer": {"done": {"%s 09:00" % RL.day_of(t): "launch"}, "runs": [], "event_cursor": t - 3600}}
    notes = [dict(BASE_EV, event="note", id="OTHER_ITEM", text="REPLAN REQUEST elsewhere", ts=lts(t - 50)),
             dict(BASE_EV, event="note", id="ROLES_ITEM_X", text="economy pass: fine", ts=lts(t - 40))]
    a = role_acts(rdecide([p], st3, lrobs(ops_status(t), lread(evs + notes, items)), t))
    check(a == [], "a note without the prefix, or on another item: no replan run")
    req = dict(BASE_EV, event="note", id="ROLES_ITEM_X", text="Replan request: 30% of the plan misses", ts=lts(t - 30))
    a = role_acts(rdecide([p], st3, lrobs(ops_status(t), lread(evs + notes + [req], items)), t))
    la = [x for x in a if x["do"] == "role_launch"]
    check(la and "replan request on ROLES_ITEM_X" in la[0]["why"], "an Operations REPLAN REQUEST note: event run")
    # RED: event runs still go; FLOOR: nothing
    st4 = fresh()
    st4["roles"] = {"Producer": {"done": {}, "runs": [], "event_cursor": t - 3600}}
    a = role_acts(rdecide([p], st4, lrobs(ops_status(t, runway=0.3), lread(evs + [fail], items)), t))
    la = [x for x in a if x["do"] == "role_launch"]
    check(la and la[0]["mode"] == "event" and la[0]["budget"] == 75000, "RED: the event run goes at x0.75")
    st4 = fresh()
    st4["roles"] = {"Producer": {"done": {}, "runs": [], "event_cursor": t - 3600}}
    a = role_acts(rdecide([p], st4, lrobs(ops_status(t, week_left=5), lread(evs + [fail], items)), t))
    check(not [x for x in a if x["do"] == "role_launch"], "FLOOR: no event run")
    # a slot due in the same tick wins; its launch covers the events (cursor moves)
    t9 = at_local("09:00")
    st5 = fresh()
    st5["roles"] = {"Producer": {"done": {}, "runs": [], "event_cursor": t9 - 3600}}
    early = dict(fail, ts=lts(t9 - 100))
    a = role_acts(rdecide([p], st5, lrobs(ops_status(t9), lread(evs + [early], items)), t9))
    la = [x for x in a if x["do"] == "role_launch"]
    check(la and la[0]["mode"] in ("run", "weekly") and st5["roles"]["Producer"]["event_cursor"] == t9,
          "slot and event due together: the slot runs and covers the event")
    a = role_acts(rdecide([p], st5, lrobs(ops_status(t9 + 2000), lread(evs + [early], items), unit="inactive",
                                         result={"usage": usage(output_tokens=10)}), t9 + 2000))
    check(not [x for x in a if x["do"] == "role_launch"], "... and no event run follows for that covered failure")


def test_role_ledger_unmeasured():
    t = at_local("11:00")

    def boom():
        raise ValueError("torn line 812")

    for led, label in ((boom, "raises"), (lambda: None, "returns nothing"), (lread([]), "zero events")):
        st = fresh()
        st["roles"] = {"Arbiter": {"done": {}, "runs": [], "event_cursor": t - 3600},
                       "Producer": {"done": {}, "runs": [], "event_cursor": t - 3600}}
        roles = [arbiter(), producer(after_role=None, runs_local=["11:00"])]
        a = role_acts(rdecide(roles, st, lrobs(ops_status(t), led), t))
        check(not [x for x in a if x["do"] == "role_launch"], "ledger %s: nothing launches, clock slots included" % label)
        al = [x for x in a if x.get("kind") == "role:ledger"]
        check(len(al) == 1 and "UNMEASURED" in al[0]["why"] and al[0]["note"], "ledger %s: ONE alarm" % label)
        check("%s 11:00" % RL.day_of(t) not in st["roles"]["Arbiter"]["done"],
              "ledger %s: the slot is not spent (it waits, missed only after slot_late_s)" % label)
        a = role_acts(rdecide(roles, st, lrobs(ops_status(t + 120), led), t + 120))
        check(not [x for x in a if x.get("kind") == "role:ledger"] and not a,
              "ledger %s: next tick, no second alarm" % label)
    claim = dict(BASE_EV, event="close", id="C1", ts=lts(t - 60))
    a = role_acts(rdecide([arbiter()], st, lrobs(ops_status(t + 240), lread([BASE_EV, claim])), t + 240))
    check(any("readable again" in x.get("why", "") for x in a) and [x for x in a if x["do"] == "role_launch"]
          and "ledger_blind" not in st, "ledger readable again: journaled, the batch launches")
    st = fresh()
    a = role_acts(rdecide([arbiter()], st, lrobs(ops_status(t), boom), t))
    check("event_cursor" not in st["roles"]["Arbiter"], "a blind first tick sets no baseline")
    a = role_acts(rdecide([conductor()], fresh(), robs(ops_status(at_local("08:00"))), at_local("08:00")))
    check([x["do"] for x in a] == ["role_launch"], "a role with no event keys never reads the ledger")
    check(RL.ledger_reading(RL.read_ledger)["state"] == "MEASURED", "read_ledger: the real ledger reads MEASURED")


def test_role_real_schedule_triggers():
    sch = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "dispatcher_schedule.json")))
    roles = {r["name"]: r for r in sch["roles"]}
    a, p = roles["Arbiter"], roles["Producer"]
    check(a.get("slot_when") == "pending_work" and a["runs_local"] == ["11:00", "17:00"]
          and a.get("pending_work", list(RL.PW.KINDS)) == list(RL.PW.KINDS),
          "schedule: Arbiter batches at 11:00/17:00 gated on ANY pending work (escapes, unresolved, claims, backlog)")
    check(a.get("pre_launch") == [["python3", "src/RimMandrake/rimflow/isolated_evidence.py", "--run", "--seat",
                                   "DISPATCHER", "--since-cutoff", "--budget-s", "900"],
                                  ["python3", "src/RimMandrake/rimflow/arbiter_tiers.py", "--since-cutoff", "--cap",
                                   "6"]],
          "schedule: the Arbiter's pre_launch runs isolated_evidence.py (900 s budget), then arbiter_tiers.py (cap 6)"
          ", both from the cutoff")
    check(a.get("pre_launch_max_s") == 1200 and a.get("run_max_s") == 2700 and "claim_window_days" not in a,
          "schedule: the Arbiter's pre-step has its own 1200 s bound beside run_max_s 2700; no claim window")
    check(roles["Auditor"].get("pre_launch") == [["python3", "src/RimMandrake/rimflow/audits.py", "ensure"],
                                                 ["python3", "src/RimMandrake/rimflow/audit_prescreen.py"],
                                                 ["python3", "src/RimMandrake/rimflow/audit_hardflag_file.py"]],
          "schedule: the Auditor's pre_launch creates/validates audits.jsonl (audits.py ensure), then writes a fresh "
          "prescreen.json over the closes since the last finished run (audit_prescreen.py, no --days: "
          "AUDITOR_PRESCREEN_FIX_WINDOW_SINCE_LAST_RUN), then files its hard flags (audit_hardflag_file.py)")
    here = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    for r in sch["roles"]:
        if r.get("pre_launch"):
            # the role's registered clone is the live seat's path; the test reads its OWN checkout (hermetic: on a
            # mutation shard the registered path is absent or is the unmutated base)
            RL.launch_argv(dict(r, unit="u", clone=here), "u", "m", "/o", "/e", "/opt/bin/claude")   # raises if unusable
            steps = r["pre_launch"] if isinstance(r["pre_launch"][0], list) else [r["pre_launch"]]
            check(all(os.path.isfile(os.path.join(here, st[1])) for st in steps),
                  "schedule: %s pre_launch scripts exist in the clone" % r["name"])
    check(p.get("event_runs") == ["plan_step_failure", "replan_request"] and p["weekly_plan_weekday"] == "Wed"
          , "schedule: Producer weekly Wed, events")
    # Owner 2026-10-28 ("Less cautioun, more progress?"): the day may hold a re-plan after the weekly run.
    check(p["daily_token_cap"] >= int(p["run_token_cap"] * 1.25), "schedule: Producer daily cap >= one run + 25%")
    for r in sch["roles"]:
        for t in r.get("runs_local") or r.get("quick_checks_local") or []:
            RL.parse_slot(t)
    check(not wave1_problems(sch), "schedule: only the wave-1 roles may be enabled, recovery off, every slot parses: "
          "%s" % (wave1_problems(sch) or "ok"))


# ---------------------------------------------------------------- review T (launcher findings)

def test_review_t():
    # F1: only a token_aware role (Operations, and the Conductor since the owner ruling of 2026-10-31) is told band, runway, budget and caps
    t = at_local("07:30")
    o = operations(token_aware=True, alarm_runs=False)
    a = role_acts(rdecide([o], fresh(), robs(ops_status(t)), t))
    la = [x for x in a if x["do"] == "role_launch"]
    check(la and "Token budget" in la[0]["message"] and "runway" in la[0]["message"]
          and "does not stop you" in la[0]["message"], "F1: Operations (token_aware) is told its band and budget")
    a = role_acts(rdecide([operations(alarm_runs=False)], fresh(), robs(ops_status(t)), t))
    msg = [x for x in a if x["do"] == "role_launch"][0]["message"].lower()
    check(not any(w in msg for w in ("token", "budget", "runway", "week left", "band")),
          "F1: a role without token_aware: no token content in its launch message")
    for r in (producer(after_role=None), arbiter(slot_when=None)):
        msg = RL.prompt(r, "run", "x", "GREEN", {"runway": 2.0, "runway_m": "MEASURED", "week_left": 40,
                                                "week_left_m": "MEASURED", "at": "now"}, 1, 2, 1.0, 3, "u").lower()
        check(not any(w in msg for w in ("token", "budget", "runway", "week left", "band", "stop at")),
              "F1: %s's launch message is token-blind" % r["name"])
    sch = json.load(open(os.path.join(HERE, "dispatcher_schedule.json")))
    aware = [r["name"] for r in sch["roles"] if r.get("token_aware")]
    check(aware == ["Conductor", "Operations"], "F1: in the schedule only the Conductor (owner 2026-10-31) and Operations are token_aware")
    # F2: no code claims a mid-run token stop
    src = open(os.path.join(HERE, "role_launch.py"), encoding="utf-8").read()
    check("At the budget" not in src and "stops a run at its cap" not in src, "F2: role_launch claims no token stop")
    # F4: Operations' 07:30 skipped by its band -> the Producer's 09:00 follows the 19:30 run of the day before
    t9 = at_local("09:00")
    ops = operations(throttle_bands={"AMBER": {"runway_ge": 0.0, "quick_cap_x": 0.75, "slots": "quick"}})
    p = producer(after_role="Operations", event_runs=None, slot_when=None, weekly_plan_weekday=None)
    yday = RL.day_of(t9 - 86400)
    st = fresh()
    st["roles"] = {"Operations": {"done": {"%s 19:30" % yday: "launch", "%s 07:30" % RL.day_of(t9): "band AMBER"},
                                  "runs": [{"unit": "u", "at": t9 - 50000, "day": yday, "slot": "%s 19:30" % yday,
                                            "mode": "run", "state": "done", "tokens": 1, "budget": 1}]}}
    a = role_acts(rdecide([ops, p], st, robs(ops_status(t9)), t9))
    check([x for x in a if x["do"] == "role_launch" and x["role"] == "Producer"],
          "F4: AMBER, Operations 07:30 band-skipped: the Producer's 09:00 follows yesterday's 19:30 run")
    st["roles"]["Operations"]["runs"][0]["state"] = "failed"
    st["roles"].pop("Producer", None)
    a = role_acts(rdecide([ops, p], st, robs(ops_status(t9)), t9))
    check(not [x for x in a if x["do"] == "role_launch" and x["role"] == "Producer"],
          "F4: ... but not when that 19:30 run failed")
    st["roles"]["Operations"]["done"]["%s 07:30" % RL.day_of(t9)] = "off switch"
    st["roles"]["Operations"]["runs"][0]["state"] = "done"
    st["roles"].pop("Producer", None)
    a = role_acts(rdecide([ops, p], st, robs(ops_status(t9)), t9))
    check(not [x for x in a if x["do"] == "role_launch" and x["role"] == "Producer"],
          "F4: a 07:30 skipped for another reason (off switch) is not passed over")
    # F7: every role on opus (Agent_Policy.md, the one ladder)
    check(all(r.get("model") == "opus" for r in sch["roles"] if r["name"] in
              ("Conductor", "Operations", "Producer", "Arbiter", "Auditor", "Innovator")),
          "F7: Conductor, Operations, Producer, Arbiter, Auditor, Innovator are opus")


def test_account_hold_dispatch():
    """DISPATCHER_FIX_LENT_HOLD_ALARM: on a lent account under its limit with nothing else fit, the work is held and
    one alarm is raised per hold (again only every HOLD_ALARM_EVERY_S); F10: the schedule's ops_stale_s rules."""
    now = at_local("08:00")
    accts = {"lent": (2.0, 40, 50, "MEASURED"), "b": (0.2, 5, 20, "MEASURED")}
    sch = sched(roles=[conductor()], account_pick=PICK_RULE)

    def hobs(t):
        o = pobs(t, accts, cur="lent")
        o["roles"]["lent"] = lambda: (LENT_RULES, lambda view, rules, n: (0.0, "off-limits"))
        return o
    st = fresh()
    a = D.decide(sch, st, hobs(now), now, True)
    al = [x for x in a if x["do"] == "alarm" and x["kind"].startswith("account:")]
    check([x["do"] for x in a if x["do"].startswith("role")] == ["role_hold"], "HOLD: the role launch is held")
    check(len(al) == 1 and al[0]["kind"] == "account:hold:lent" and al[0]["note"], "HOLD: one alarm, noted")
    a = D.decide(sch, st, hobs(now + 120), now + 120, True)
    check(not [x for x in a if x["do"] == "alarm" and x["kind"].startswith("account:")]
          and not [x for x in a if x["do"] == "role_launch"], "HOLD tick 2: still held, no second alarm")
    t2 = now + D.HOLD_ALARM_EVERY_S + 60
    a = D.decide(sch, st, hobs(t2), t2, True)
    check(len([x for x in a if x["do"] == "alarm" and x["kind"] == "account:hold:lent"]) == 1,
          "HOLD lasting HOLD_ALARM_EVERY_S: alarmed again")
    # F10: the schedule's ops_stale_s overrides a stale line in the rule (both gates read the same one)
    st = fresh()
    a = D.decide(sched(roles=[conductor()], account_pick=dict(PICK_RULE, ops_stale_s=100), ops_stale_s=2700),
                 st, pobs(now, {"a": (2.0, 40, 50, "MEASURED")}), now, True)
    check([x for x in a if x["do"] == "account_pick" and x["state"] == "KEEP"]
          and [x for x in a if x["do"] == "role_launch"], "F10: the pick uses the schedule's ops_stale_s")


def test_review_u_notes():
    """review U N2: no token figure is noted on an item a token-blind role reads. A note with a token term bound for
    one goes to token_notes_item (Operations' own item); blind roles' launch and done notes carry a closed-set blind
    note with no term; with no token_notes_item the note is not written; Operations' own item is not blind."""
    rx = D.token_rx()
    check(rx.search("used 40000 tokens") and rx.search("daily_token_cap 1, 2 used + 3 budget".replace("_", " "))
          and not rx.search("Conductor quick 08:00 launched, unit rm-role-conductor-1"), "N2: the word list sees terms")
    check(D.token_rx(os.path.join(TMP, "no_such_rules.json")).search("anything"), "N2: no word list fails closed")
    sch = sched(roles=[conductor(), operations(ledger_item="OPS_OWN_X", token_aware=True)],
                token_notes_item="OPS_OWN_X", ledger_notes=True)
    check(D.blind_items(sch) == {"ROLES_ITEM_X"}, "N2: the blind items are every role's but the token_aware one's")
    noted = []
    fx = {"note": lambda i, t: noted.append((i, t)) or (True, ""), "publish": lambda n: "p",
          "lock": lambda: open(os.devnull)}
    root = os.path.join(TMP, "u_notes")
    acts = [{"do": "alarm", "kind": "role:Conductor:cap", "ticket": "ROLES_ITEM_X", "note": True,
             "why": "Conductor quick REFUSED: daily token cap 200000, 190000 used today + 30000 budget"},
            {"do": "alarm", "kind": "role:Conductor:failed", "ticket": "ROLES_ITEM_X", "note": True,
             "why": "Conductor run U ended without a good result (no result file)"},
            {"do": "alarm", "kind": "role:Operations:cap", "ticket": "OPS_OWN_X", "note": True,
             "why": "Operations run REFUSED: 9 tokens used"}]
    D.execute([dict(x) for x in acts], sch, fresh(), root, True, 100.0, fx)
    check(noted[0][0] == "OPS_OWN_X" and "190000" in noted[0][1] and "ROLES_ITEM_X" in noted[0][1],
          "N2: a token note bound for the shared item goes to Operations' item, naming where it was meant to go")
    check(noted[1][0] == "OPS_OWN_X" and "no result file" in noted[1][1],
          "r2 #1: a note with no term but no blind note_text is NOT on the shared item (allow-list, not word list)")
    check(noted[2][0] == "OPS_OWN_X" and "[meant for" not in noted[2][1], "N2: Operations' own item is not blind")
    check(not any(i == "ROLES_ITEM_X" and rx.search(t) for i, t in noted), "N2: nothing on the shared item has a term")
    # r2 #1: only a code-built note_text reaches a blind item; outside text the word list misses goes to Operations'
    noted.clear()
    D.execute([{"do": "alarm", "kind": "role:Conductor:failed", "role": "Conductor", "ticket": "ROLES_ITEM_X", "note": True,
                "why": "Conductor run U ended without a good result (Claude AI usage limit reached|1730000000)",
                "blind": RL.blind("Conductor", "failed", "quick", "rm-role-conductor-7")},
               {"do": "alarm", "kind": "role:Conductor:x", "ticket": "ROLES_ITEM_X", "note": True,
                "why": "Conductor run U: usage limit reached"},
               {"do": "role_done", "role": "Conductor", "ticket": "ROLES_ITEM_X", "note": True,
                "why": "x", "blind": RL.blind("Conductor", "completed", "quick", "30000 tokens")}],
              sch, fresh(), root, True, 100.0, fx)
    check(noted[0] == ("ROLES_ITEM_X", "dispatcher: Conductor quick run: ended without a good result"),
          "r2 #1: the fixed blind note, and only it, lands on the shared item")
    check(noted[1][0] == "OPS_OWN_X" and "usage limit" in noted[1][1] and "[meant for ROLES_ITEM_X" in noted[1][1],
          "r2 #1: free text the word list misses ('usage limit reached') goes to Operations' item")
    check(noted[2][0] == "OPS_OWN_X", "r2 #1: a blind note with a field outside its closed set is diverted")
    check(not any(i == "ROLES_ITEM_X" and ("limit" in t or "1730000000" in t) for i, t in noted),
          "r2 #1: no outside text on the shared item")
    noted.clear()
    sch2 = dict(sch)
    sch2.pop("token_notes_item")
    a = D.execute([dict(acts[0])], sch2, fresh(), root, True, 100.0, fx)
    check(not noted and a[0]["ledger"].startswith("not noted"), "N2: no token_notes_item -> not noted, journalled")
    real = D.load_schedule()
    check(real.get("token_notes_item") and real["token_notes_item"] not in D.blind_items(real)
          and "V3_ROLES_BUILD_EIGHT_CHAIRS_ONE_TABLE" in D.blind_items(real),
          "N2 real schedule: token notes go to Operations' own item, off the shared table")
    # decide: a blind role's launch note_text carries no term; the journal's why keeps the budget
    now = at_local("08:00")
    st = fresh()
    a = D.decide(sched(roles=[conductor()], account_pick=PICK_RULE), st, pobs(now, {"a": (2.0, 40, 50, "MEASURED")}),
                 now, True)
    la = [x for x in a if x["do"] == "role_launch"]
    check(la and "budget" in la[0]["why"] and RL.blind_note(la[0].get("blind"))
          and not rx.search(RL.blind_note(la[0]["blind"])),
          "N2: the Conductor launch note has no token term (the journal keeps the budget)")
    # supervise: a blind role's done note has no tokens; Operations' keeps them
    for role, blind in ((conductor(), True), (operations(token_aware=True), False)):
        st = {"roles": {role["name"]: {"runs": [{"state": "running", "unit": "U", "at": 0, "budget": 30000,
                                                  "item": role["ledger_item"], "mode": "quick", "scope": "s"}]}}}
        out = []
        RL.supervise_roles({"roles": [role]}, st, {"unit_state": lambda u: "inactive", "result": lambda r: {
            "usage": usage(input_tokens=1000, output_tokens=10), "modelUsage": {"opus": {}}, "subtype": "success"}},
            5000.0, lambda **k: out.append(k))
        d = [x for x in out if x["do"] == "role_done"]
        bn = RL.blind_note(dict(d[0]["blind"], unit="rm-role-%s-1" % role["name"].lower())) if d else None
        check(d and "tokens" in d[0]["why"] and bn and not rx.search(bn) and "success" not in bn,
              "N2: %s done: the blind note is fixed and token-free; the why keeps its tokens" % role["name"])


def test_review_u_lent_unmeasured():
    """review U N1/F3: UNMEASURED on a lent account HOLDS (ring, recover and role launches) and alarms; on an owned
    account it keeps; an unresolved account keeps (never guess); the lent set last read stands in while the rules are
    unreadable."""
    now = at_local("09:00")
    fn = lent_fn()
    blind = {"lent": (2.0, 40, 50, "UNMEASURED"), "a": (3.0, 60, 20, "MEASURED")}
    st_ = accounts_status(now, blind)
    p = AP.pick(PICK_RULE, st_, "lent", LENT_RULES, fn, now)
    check(p["state"] == "UNMEASURED" and p["hold"] and "HELD" in p["why"], "N1: lent account, reading UNMEASURED -> held")
    stale = accounts_status(now, {"lent": (2.0, 40, 50, "MEASURED")}, age_s=3000)
    check(AP.pick(PICK_RULE, stale, "lent", LENT_RULES, fn, now)["hold"], "N1: lent account, stale reading -> held")
    check(not AP.pick(PICK_RULE, stale, "a", LENT_RULES, fn, now)["hold"], "N1: owned account, stale reading -> kept")
    check(not AP.pick(PICK_RULE, st_, None, LENT_RULES, fn, now)["hold"], "N1: unresolved account -> kept, never guess")
    ok = accounts_status(now, {"lent": (2.0, 40, 50, "MEASURED"), "a": (3.0, 60, 20, "MEASURED")})
    check(AP.pick(PICK_RULE, ok, "lent", None, fn, now, ["lent"])["hold"],
          "N1: rules unreadable, on the last-read lent account -> held")
    check(not AP.pick(PICK_RULE, ok, "a", None, fn, now, ["lent"])["hold"],
          "N1: rules unreadable, on an account the last-read set calls owned -> kept")
    # through the dispatcher: the ring is held and the alarm says so; the lent set is cached for an outage
    sch = sched(roles=[conductor()], account_pick=PICK_RULE)
    st = fresh()
    a = stall(sch, st, pobs(now, blind, cur="lent"), now)
    check("ring" not in kinds(a) and [x for x in a if x.get("kind") == "account:unmeasured:held"],
          "N1 dispatch: on a lent account with no reading the ring is held and alarmed")
    check(st.get("account_lent_known") == ["lent"], "N1 dispatch: the lent set read is cached")
    o = pobs(now, {"lent": (2.0, 40, 50, "MEASURED"), "a": (3.0, 60, 20, "MEASURED")}, cur="lent")
    o["roles"]["lent"] = lambda: (None, fn)
    st2 = fresh()
    st2["account_lent_known"] = ["lent"]
    a = stall(sch, st2, o, now)
    check("ring" not in kinds(a) and [x for x in a if x.get("kind") == "account:unmeasured:held"],
          "N1 dispatch: rules unreadable, the cached set still holds the lent account")
    st3 = fresh()
    a = stall(sch, st3, pobs(now, blind, cur="a"), now)
    check("ring" in kinds(a), "N1 dispatch: on an owned account the ring goes")


def test_review_u_group4():
    t8 = at_local("08:00")
    quiet_ops = operations(runs_local=["08:00"], economy_pass_local=None, alarm_runs=False)
    # N5: a bad schedule value skips THAT role with an alarm; the others are still decided
    bad = conductor(throttle_bands={"X": {"quick_cap_x": 1.0, "slots": "all"}})
    a = role_acts(rdecide([bad, quiet_ops], fresh(), robs(ops_status(t8)), t8))
    al = [x for x in a if x.get("kind") == "role:Conductor:schedule"]
    check(al and "runway_ge" in al[0]["why"] and al[0]["note"], "N5: bands without runway_ge -> schedule alarm")
    check([x["role"] for x in a if x["do"] == "role_launch"] == ["Operations"], "N5: the other role still launches")
    for kw, word in (({"event_runs_per_day": "two"}, "event_runs_per_day"), ({"run_token_cap": "lots"}, "run_token_cap"),
                     ({"throttle_bands": {"G": {"runway_ge": "high"}}}, "runway_ge")):
        a = role_acts(rdecide([producer(after_role=None, **kw)], fresh(), lrobs(ops_status(t8), lread([BASE_EV])), t8))
        check([x.get("kind") for x in a] == ["role:Producer:schedule"] and word in a[0]["why"],
              "N5: %s refused per role" % word)
    try:
        RL.band({"throttle_bands": {"F": {"week_left_pct_lt": 10}}}, {"week_left": 50, "runway": 1})
        check(False, "N5: band() with no runway band raises")
    except ValueError as e:
        check("runway_ge" in str(e), "N5: band() with no runway band raises a clear ValueError")
    # an unforeseen raise (a malformed ops alarms map) is caught per role, and supervision still acts
    st = fresh()
    st["roles"] = {"Conductor": {"done": {}, "runs": [{"unit": "U0", "at": t8 - 4000, "day": RL.day_of(t8),
                                                        "budget": 30000, "mode": "quick", "state": "running",
                                                        "run_max_s": 1800, "scope": "s0", "item": "ROLES_ITEM_X"}]}}
    real_ak = RL.alarm_keys

    def ak_boom(alarms):
        raise TypeError("an unforeseen alarms shape")
    RL.alarm_keys = ak_boom   # alarm_keys itself now skips a malformed entry (review V): force the raise
    try:
        acts = rdecide([conductor(), operations(runs_local=["08:00"], economy_pass_local=None)], st,
                       robs(ops_status(t8, alarms={"A": "not a mapping"})), t8)
    finally:
        RL.alarm_keys = real_ak
    check(any(x.get("kind") == "role:Operations:schedule" and "raised" in x["why"] for x in acts),
          "N5: a raise while deciding one role -> that role's alarm, the tick goes on")
    check(any(x["do"] == "role_stop" for x in acts), "N5: the over-time run is still stopped")
    # N3: an event run may not eat the day's scheduled run
    wed = day_with_weekday(2)
    t8w = RL.slot_epoch(wed, "08:00") + 60
    items = {"PLAN_A": FakeItem(raised="2026-10-28T01:00:00Z")}
    fail = dict(BASE_EV, event="verify", id="PLAN_A", result="fail", ts=lts(t8w - 100))
    led = lread([BASE_EV, fail], items)
    p = producer(after_role=None, daily_token_cap=125000)
    st = fresh()
    st["roles"] = {"Producer": {"done": {}, "runs": [], "event_cursor": t8w - 3600}}
    a = role_acts(rdecide([p], st, lrobs(ops_status(t8w), led), t8w))
    check(not [x for x in a if x["do"] == "role_launch"] and any("waits" in x.get("why", "") for x in a)
          and not [k for k in st["roles"]["Producer"]["done"] if "event" in k],
          "N3: 08:00 Wednesday event with the weekly run still to come: waits, not spent, no alarm")
    check(not [x for x in a if x["do"] == "alarm"], "N3: the wait raises no alarm")
    a = role_acts(rdecide([p], st, lrobs(ops_status(t8w + 120), led), t8w + 120))
    check(a == [], "N3: the wait is journalled once")
    t9w = RL.slot_epoch(wed, "09:00") + 60
    a = role_acts(rdecide([p], st, lrobs(ops_status(t9w), led), t9w))
    la = [x for x in a if x["do"] == "role_launch"]
    check(la and la[0]["mode"] == "weekly" and la[0]["budget"] == 100000, "N3: the 09:00 weekly plan still runs")
    st = fresh()
    st["roles"] = {"Producer": {"done": {}, "runs": [], "event_cursor": t8w - 3600}}
    a = role_acts(rdecide([producer(after_role=None)], st, lrobs(ops_status(t8w), led), t8w))
    check([x["mode"] for x in a if x["do"] == "role_launch"] == ["event"], "N3: room for both -> the event runs")
    # N4: an event stamped before the cursor but ingested after it still triggers, once
    t11 = at_local("11:00")
    st = fresh()
    st["roles"] = {"Arbiter": {"done": {}, "runs": [], "event_cursor": t11 - 600, "events_seen": []}}
    late = dict(BASE_EV, event="close", id="WRITTEN_ON_FOUNDRY", ts=lts(t11 - 900))
    a = role_acts(rdecide([arbiter()], st, lrobs(ops_status(t11), lread([BASE_EV, late])), t11))
    la = [x for x in a if x["do"] == "role_launch"]
    check(la and "WRITTEN_ON_FOUNDRY" in la[0]["why"], "N4: a claim ts'd before the cursor, ingested late, triggers")
    check(any("WRITTEN_ON_FOUNDRY" in k for k in st["roles"]["Arbiter"]["events_seen"]), "N4: the launch records it seen")
    t17 = at_local("17:00")
    st["roles"]["Arbiter"]["runs"] = []
    a = role_acts(rdecide([arbiter()], st, lrobs(ops_status(t17), lread([BASE_EV, late])), t17))
    check(not [x for x in a if x["do"] == "role_launch"] and any("no done claim" in x.get("why", "") for x in a),
          "N4: the same claim does not trigger twice")
    st = fresh()
    st["roles"] = {"Arbiter": {"done": {}, "runs": [], "event_cursor": t11 - 600, "events_seen": []}}
    ancient = dict(late, ts=lts(t11 - 600 - RL.EVENT_LOOKBACK_S - 60))
    a = role_acts(rdecide([arbiter()], st, lrobs(ops_status(t11), lread([BASE_EV, ancient])), t11))
    check(not [x for x in a if x["do"] == "role_launch"], "N4: older than the look-back window: not an event")
    # N6: a failed launch alarms and gives the slot back; a PAUSE recheck gives it back; success clears the record
    root = os.path.join(TMP, "roles_exec_u")
    sch = sched(roles=[conductor()])
    key = "%s 08:00" % RL.day_of(t8)
    base_fx = {"note": lambda i, t: (True, ""), "publish": lambda n: "p", "lock": lambda: open(os.devnull),
               "off": lambda p: None, "paused": lambda: None}

    def launch_then(fx_extra, now=t8):
        st = fresh()
        acts = [x for x in rdecide([conductor()], st, robs(ops_status(now)), now) if x["do"] == "role_launch"]
        check(st["roles"]["Conductor"]["done"].get(key) == "launch" and st["roles"]["Conductor"].get("pending_launch"),
              "N6: decide marks the slot and records what it consumed")
        out = D.execute(acts, sch, st, root, True, now, dict(base_fx, **fx_extra))
        return st, out
    st, out = launch_then({"role_launch": lambda *a: (False, "systemd-run exit 1", {})})
    rs = st["roles"]["Conductor"]
    check(any(x.get("kind") == "role:Conductor:launch_failed" and x.get("note") and "systemd-run exit 1" in x["why"]
              for x in out), "N6: a failed launch raises role:<name>:launch_failed")
    check(key not in rs["done"] and "pending_launch" not in rs and not rs["runs"], "N6: the slot is given back")
    a = [x for x in rdecide([conductor()], st, robs(ops_status(t8 + 120)), t8 + 120) if x["do"] == "role_launch"]
    check(a, "N6: the next tick retries the launch")
    st, out = launch_then({"paused": lambda: "owner: away"})
    rs = st["roles"]["Conductor"]
    check(key not in rs["done"] and not [x for x in out if x.get("kind", "").endswith("launch_failed")],
          "N6: a launch held by the PAUSE recheck keeps its slot due, no alarm")
    st, out = launch_then({"role_launch": lambda *a: (True, "started", {"scope": "s"})})
    rs = st["roles"]["Conductor"]
    check(rs["done"].get(key) == "launch" and "pending_launch" not in rs and len(rs["runs"]) == 1,
          "N6: a good launch keeps the mark and clears the record")

    def boom(*a):
        raise TimeoutError("systemctl MainPID query")
    st, out = launch_then({"role_launch": boom})
    rs = st["roles"]["Conductor"]
    check(rs["done"].get(key) == "launch" and len(rs["runs"]) == 1
          and any(x.get("kind") == "role:Conductor:launch_failed" and "TimeoutError" in x["why"] for x in out),
          "N6: a launch that raised alarms, keeps the run tracked and the mark (never launched twice)")
    # the real schedule passes validation, every role
    for r in D.load_schedule()["roles"]:
        try:
            RL.validate_role(dict(RL.ROLE_DEFAULTS, **r))
            check(True, "real schedule: %s validates" % r.get("name"))
        except ValueError as e:
            check(False, "real schedule: %s validates (%s)" % (r.get("name"), e))



def test_review_v():
    """Review V: V2 (Operations-only alarms), V3 (run_max_s and supervision), V4 (true launch note), V5-V7."""
    t8 = at_local("08:00")
    t12 = at_local("12:00")
    # V3: run_max_s / slot_late_s must be numbers > 0; None, 0, a string or inf is refused
    for v in (None, 0, -5, "1800", float("inf")):
        for k in ("run_max_s", "slot_late_s"):
            try:
                RL.validate_role(dict(RL.ROLE_DEFAULTS, **conductor(**{k: v})))
                check(False, "V3: %s=%r is refused" % (k, v))
            except ValueError as e:
                check(k in str(e), "V3: %s=%r is refused" % (k, v))
    a = role_acts(rdecide([conductor(run_max_s=None), operations(runs_local=["08:00"], economy_pass_local=None,
                                                                 alarm_runs=False)], fresh(), robs(ops_status(t8)), t8))
    check(any(x.get("kind") == "role:Conductor:schedule" and "run_max_s" in x["why"] for x in a)
          and [x["role"] for x in a if x["do"] == "role_launch"] == ["Operations"],
          "V3: run_max_s null skips that role with an alarm; the other role launches")
    # a run recorded with run_max_s None (an older launch) falls back to the default bound and is still stopped
    over = {"unit": "U0", "at": t8 - 4000, "day": RL.day_of(t8), "budget": 30000, "mode": "quick", "state": "running",
            "run_max_s": None, "scope": "s0", "item": "ROLES_ITEM_X"}
    st = fresh()
    st["roles"] = {"Conductor": {"done": {}, "runs": [dict(over)]}, "Operations": {"done": {}, "runs": [dict(over, unit="U1")]}}
    acts = rdecide([conductor(), operations(runs_local=["07:30"], economy_pass_local=None, alarm_runs=False)], st,
                   robs(ops_status(t8)), t8)
    check(sorted(x["unit"] for x in acts if x["do"] == "role_stop") == ["U0", "U1"],
          "V3: a run with run_max_s None is bounded by the default and stopped, no TypeError")
    # one role's supervision raising: alarm for it, kept busy, the other role is still supervised
    real_one = RL._supervise_one

    def one_boom(name, *a):
        if name == "Conductor":
            raise TypeError("unorderable run_max_s")
        return real_one(name, *a)
    RL._supervise_one = one_boom
    try:
        st = fresh()
        st["roles"] = {"Conductor": {"done": {}, "runs": [dict(over)]},
                       "Operations": {"done": {}, "runs": [dict(over, unit="U1", run_max_s=1800)]}}
        acts = rdecide([conductor(), operations(runs_local=["07:30"], economy_pass_local=None, alarm_runs=False)],
                       st, robs(ops_status(t8)), t8)
    finally:
        RL._supervise_one = real_one
    check(any(x.get("kind") == "role:Conductor:supervise" for x in acts)
          and [x["unit"] for x in acts if x["do"] == "role_stop"] == ["U1"]
          and not [x for x in acts if x["do"] == "role_launch" and x["role"] == "Conductor"],
          "V3: one role's supervision raising alarms that role; the other's over-time run is still stopped")
    # supervise_roles raising as a whole: the dispatcher alarms and the tick goes on
    real_sup = RL.supervise_roles

    def sup_boom(*a):
        raise TypeError("whole supervision")
    RL.supervise_roles = sup_boom
    try:
        acts = rdecide([conductor()], fresh(), robs(ops_status(t8)), t8)
    finally:
        RL.supervise_roles = real_sup
    check(any(x.get("kind") == "role:supervise" for x in acts), "V3: decide() survives supervise_roles raising")
    # a roles entry that is not a mapping: alarmed and skipped, the others decided
    a = role_acts(rdecide(["not a role", conductor()], fresh(), robs(ops_status(t8)), t8))
    check(any(x.get("kind") == "role:schedule" for x in a)
          and [x["role"] for x in a if x["do"] == "role_launch"] == ["Conductor"],
          "V3: a non-mapping roles entry is alarmed and skipped; Conductor still launches")
    # V4: the ledger note records the true outcome of a held or failed launch; a repeated failure is noted once
    root = os.path.join(TMP, "roles_exec_v")
    sch = sched(roles=[conductor()], ledger_notes=True)
    notes = []
    base_fx = {"note": lambda i, t: (notes.append(t), (True, ""))[1], "publish": lambda n: "p",
               "lock": lambda: open(os.devnull), "off": lambda p: None, "paused": lambda: None}

    def launch(st, fx_extra, now=t8):
        acts = [x for x in rdecide([conductor()], st, robs(ops_status(now)), now) if x["do"] == "role_launch"]
        del notes[:]
        D.execute(acts, sch, st, root, True, now, dict(base_fx, **fx_extra))
        return [n for n in notes if n.startswith("dispatcher: Conductor ")]
    ln = launch(fresh(), {"paused": lambda: "owner: away"})
    check(ln and ln[0].endswith(": held by PAUSE, not launched") and "away" not in ln[0],
          "V4: a held launch is noted held by PAUSE, the reason kept off")
    st = fresh()
    ln = launch(st, {"role_launch": lambda *a: (False, "systemd-run exit 1", {})})
    check(ln and ln[0].endswith(": launch failed, retried") and "systemd" not in ln[0],
          "V4: a failed launch is noted launch failed, the error kept off")
    ln = launch(st, {"role_launch": lambda *a: (False, "systemd-run exit 1", {})}, t8 + 120)
    check(not ln, "V4: the retry that fails again is not noted a second time")
    ln = launch(st, {"role_launch": lambda *a: (True, "started", {"scope": "s"})}, t8 + 240)
    check(ln and ln[0].endswith(": launched") and "launch_failed_key" not in st["roles"]["Conductor"],
          "V4: the launch that then succeeds is noted launched and clears the failure record")

    def boom(*a):
        raise TimeoutError("MainPID")
    ln = launch(fresh(), {"role_launch": boom})
    check(ln and ln[0].endswith(": launch outcome unknown, the run stays tracked") and "MainPID" not in ln[0],
          "V4: a launch that raised is noted unknown, the exception kept off")
    # V2: an Operations-only alarm (no ledger item) triggers one Operations alarm run, keyed alarm:<aid>, once
    ops = operations(runs_local=["07:30"], economy_pass_local=None)
    oal = {"RUNWAY_LOW:codex.runway": {"state": "OPEN", "for": "Operations", "item": None, "title": "t"}}
    st = fresh()
    st["roles"] = {"Operations": {"done": {"%s 07:30" % RL.day_of(t12): "launch"}, "runs": [], "alarms_seen": []}}
    a = role_acts(rdecide([ops], st, robs(ops_status(t12, alarms=oal)), t12))
    la = [x for x in a if x["do"] == "role_launch"]
    check(la and la[0]["ticket"] == "ROLES_ITEM_X"
          and "alarm:RUNWAY_LOW:codex.runway" in st["roles"]["Operations"]["alarms_seen"],
          "V2: an Operations-only alarm runs Operations on its own item, seen as alarm:<aid>")
    st["roles"]["Operations"]["runs"] = []
    a = role_acts(rdecide([ops], st, robs(ops_status(t12 + 600, alarms=oal)), t12 + 600))
    check(not [x for x in a if x["do"] == "role_launch"], "V2: the same alarm does not run Operations twice")
    check(RL.alarm_keys({"A:x": {"state": "OPEN", "item": "IT"}, "B:y": {"state": "OPEN", "for": "Operations"},
                         "C:z": {"state": "OPEN"}, "D:w": "junk", "E:v": {"state": "PENDING", "for": "Operations"}})
          == {"IT", "alarm:B:y"} and RL.alarm_keys(["junk"]) == set(),
          "V2: alarm_keys: item, or alarm:<aid> for Operations; junk and non-OPEN skipped")
    # V5: a block that was off the plan when a run read it does not trigger later once the item is raised
    p = producer(after_role=None, runs_local=["11:00"])
    t11 = at_local("11:00")
    blk = dict(BASE_EV, event="block", id="X_ITEM", ts=lts(t11 - 1800))
    st = fresh()
    st["roles"] = {"Producer": {"done": {}, "runs": [], "event_cursor": t11 - 7200, "events_seen": []}}
    a = role_acts(rdecide([p], st, lrobs(ops_status(t11), lread([BASE_EV, blk], {"X_ITEM": FakeItem()})), t11))
    check([x["mode"] for x in a if x["do"] == "role_launch"] in (["run"], ["weekly"]), "V5: the 11:00 run launches")
    st["roles"]["Producer"]["runs"] = []
    raised = {"X_ITEM": FakeItem(raised="2026-10-28T01:00:00Z")}
    a = role_acts(rdecide([p], st, lrobs(ops_status(t12), lread([BASE_EV, blk], raised)), t12))
    check(not [x for x in a if x["do"] == "role_launch"],
          "V5: a block the 11:00 run already read (off the plan then) does not trigger once the item is raised")
    blk2 = dict(blk, ts=lts(t11 + 600))
    a = role_acts(rdecide([p], st, lrobs(ops_status(t12), lread([BASE_EV, blk, blk2], raised)), t12))
    check([x["mode"] for x in a if x["do"] == "role_launch"] == ["event"], "V5: a new block on it does trigger")
    # V6: a slot the band blocks reserves nothing: RED (weekly only), not Wednesday, a 01:00 event is not held
    thu = day_with_weekday(3)
    t1 = RL.slot_epoch(thu, "01:00") + 60
    fail = dict(BASE_EV, event="verify", id="PLAN_A", result="fail", ts=lts(t1 - 100))
    led = lread([BASE_EV, fail], {"PLAN_A": FakeItem(raised="x")})
    for runway, waits in ((0.5, False), (2.0, True)):
        st = fresh()
        st["roles"] = {"Producer": {"done": {}, "runs": [], "event_cursor": t1 - 3600}}
        a = role_acts(rdecide([producer(after_role=None, daily_token_cap=125000)], st,
                              lrobs(ops_status(t1, runway=runway), led), t1))
        got = any("waits" in x.get("why", "") for x in a)
        check(got == waits and bool([x for x in a if x["do"] == "role_launch"]) != waits,
              "V6: runway %s: the 09:00 slot %s, so the event %s" % (
                  runway, "will run" if waits else "is blocked", "waits" if waits else "runs"))
    # V7: a raise after the slot was consumed gives it back; a raise building the prompt consumes nothing
    real_re = RL.role_events

    def re_boom(*a, **k):
        raise RuntimeError("ledger shape")
    RL.role_events = re_boom
    try:
        st = fresh()
        st["roles"] = {"Producer": {"done": {}, "runs": [], "event_cursor": t11 - 600, "events_seen": []}}
        a = role_acts(rdecide([p], st, lrobs(ops_status(t11), lread([BASE_EV])), t11))
    finally:
        RL.role_events = real_re
    rs = st["roles"]["Producer"]
    check(any(x.get("kind") == "role:Producer:schedule" for x in a) and not rs["done"] and "pending_launch" not in rs
          and not [x for x in a if x["do"] == "role_launch"],
          "V7: a raise after mark() gives the slot back (it stays due), with an alarm")
    real_pr = RL.prompt

    def pr_boom(*a):
        raise KeyError("template")
    RL.prompt = pr_boom
    try:
        st = fresh()
        a = role_acts(rdecide([conductor()], st, robs(ops_status(t8)), t8))
    finally:
        RL.prompt = real_pr
    rs = st["roles"].get("Conductor") or {}
    check(any(x.get("kind") == "role:Conductor:schedule" for x in a) and not rs.get("done")
          and "pending_launch" not in rs, "V7: a raise building the prompt consumes nothing")


def test_review_w_alarm_rearm():
    """Review W, W1: an alarm that clears and re-crosses runs Operations again; alarms open at enable run once; alarm
    runs are rate-limited; a blind or unreadable reading prunes nothing."""
    ops = operations(runs_local=["07:30"], economy_pass_local=None)
    t = at_local("12:00")
    A = {"RUNWAY_LOW:accounts.x.runway": {"state": "OPEN", "for": "Operations", "item": None, "title": "t"}}
    key = "alarm:RUNWAY_LOW:accounts.x.runway"
    st = fresh()
    st["roles"] = {"Operations": {"done": {"%s 07:30" % RL.day_of(t): "launch"}, "runs": []}}
    rs = st["roles"]["Operations"]

    def tick(now, status):
        rs["runs"] = []
        return role_acts(rdecide([ops], st, robs(status), now))

    def launches(a):
        return [x for x in a if x["do"] == "role_launch"]
    a = tick(t, ops_status(t, alarms=A))
    check(len(launches(a)) == 1 and rs["alarms_seen"] == [key], "W1: an alarm open at first enable runs once")
    check(not launches(tick(t + 600, ops_status(t + 600, alarms=A))), "W1: still open: no second run")
    a = tick(t + 700, None)
    check(not launches(a) and rs["alarms_seen"] == [key] and any("alarm runs held" in x.get("why", "") for x in a),
          "W1: a blind tick prunes nothing and says so")
    tick(t + 800, ops_status(t + 800, alarms={"_alarm_state": {"state": "UNREADABLE"}}))
    check(rs["alarms_seen"] == [key], "W1: an UNREADABLE alarms dict prunes nothing")
    check(not launches(tick(t + 900, ops_status(t + 900, alarms=A))), "W1: readable again, same crossing: no run")
    tick(t + 1200, ops_status(t + 1200, alarms={}))
    check(rs["alarms_seen"] == [], "W1: the alarm cleared: it is re-armed (pruned from alarms_seen)")
    a = tick(t + 1800, ops_status(t + 1800, alarms=A))
    check(not launches(a) and any("alarm_run_gap_s" in x.get("why", "") for x in a),
          "W1: re-crossed inside alarm_run_gap_s of the last alarm run: it waits, journaled")
    a = tick(t + 1900, ops_status(t + 1900, alarms=A))
    check(a == [], "W1: the wait is journaled once")
    a = tick(t + 3700, ops_status(t + 3700, alarms=A))
    check(len(launches(a)) == 1 and launches(a)[0]["mode"] == "alarm",
          "W1: cross, clear, re-cross: the alarm runs Operations a second time")
    unit = launches(a)[0]["unit"]
    check(RL.unlaunch(rs, unit) and rs["alarm_last_run"] == t and rs["alarms_seen"] == [],
          "W1: a launch that did not happen gives back the alarm and the gap clock")
    # the real schedule's Operations, enabled with both live runway alarms open: one run covers both
    real = {r["name"]: r for r in json.load(open(os.path.join(HERE, "dispatcher_schedule.json")))["roles"]}
    ro = dict(real["Operations"], throttle_bands=OPS_BANDS_FROZEN, enabled=True, clone=os.path.join(TMP, "clone"), off_file=os.path.join(TMP, "OR_OFF"))
    two = {"RUNWAY_LOW:accounts.lukas.runway": {"state": "OPEN", "for": "Operations"},
           "RUNWAY_LOW:codex.runway": {"state": "OPEN", "for": "Operations"}}
    t13 = at_local("13:00")
    st = fresh()
    st["roles"] = {"Operations": {"done": {"%s 07:30" % RL.day_of(t13): "x"}, "runs": []}}
    a = role_acts(rdecide([ro], st, robs(ops_status(t13, runway=1.2, alarms=two)), t13))
    la = [x for x in a if x["do"] == "role_launch"]
    check(len(la) == 1 and la[0]["mode"] == "alarm" and "codex.runway" in la[0]["why"]
          and len(st["roles"]["Operations"]["alarms_seen"]) == 2,
          "W1: real schedule, first enable with two runway alarms open: one alarm run covers both: %s"
          % [x.get("why", "")[:80] for x in a])


def test_review_x_alarm_flap():
    """Review X, X1: a runway alarm flapping near its line (open 15 min, clear 60 min, every 75 min, all day) must not
    crowd out the 07:30 / 19:30 scheduled runs: alarm runs reserve the scheduled runs' budget, and the schedule's
    alarm_runs_per_alarm_per_day / alarm_runs_per_day limit them."""
    real = {r["name"]: r for r in json.load(open(os.path.join(HERE, "dispatcher_schedule.json")))["roles"]}
    base = dict(real["Operations"], enabled=True, clone=os.path.join(TMP, "clone"), off_file=os.path.join(TMP, "OR_OFF"))
    check(base.get("alarm_runs_per_alarm_per_day") == 1 and base.get("alarm_runs_per_day") == 2,
          "X1: the real schedule holds the alarm limits as data (1 per alarm, 2 per day)")

    def day(ro, keys):
        t0 = at_local("00:00")
        st = fresh()
        st["roles"] = {"Operations": {"done": {}, "runs": []}}
        rs = st["roles"]["Operations"]
        got, refused = [], []
        for i in range(96):
            now = t0 + i * 900
            op = {}
            if i % 5 == 0:
                op = {k: {"state": "OPEN", "for": "Operations"} for k in keys}
            for x in role_acts(rdecide([ro], st, robs(ops_status(now, runway=2.0, alarms=op)), now)):
                if x["do"] == "role_launch":
                    got.append((x["mode"], RL.local_hhmm(now) if hasattr(RL, "local_hhmm") else i))
                    rs["runs"].append({"day": RL.day_of(now), "budget": x["budget"], "at": now, "state": "done",
                                       "mode": x["mode"], "tokens": x["budget"]})
                    rs.pop("pending_launch", None)
                elif x["do"] == "alarm" and ":cap" in str(x.get("kind")):
                    refused.append(x["why"])
        return got, refused, rs
    keys = ["RUNWAY_LOW:accounts.lukas.runway"]
    got, refused, rs = day(base, keys)
    modes = [m for m, _ in got]
    check(modes.count("alarm") <= 1 and "economy" in modes and "run" in modes and not refused,
          "X1: real caps, flapping alarm: both scheduled runs launch, at most one alarm run, no cap REFUSED: %s %s"
          % (modes, refused[:1]))
    roomy = dict(base, daily_token_cap=base["daily_token_cap"] * 3)
    got, refused, rs = day(roomy, keys)
    modes = [m for m, _ in got]
    check(modes.count("alarm") == 1 and len(got) == 3 and rs["alarm_day"]["keys"][
          "alarm:" + keys[0]] == 1, "X1: room in the cap: one alarm run per alarm per day, not one per flap: %s" % modes)
    two = ["RUNWAY_LOW:accounts.lukas.runway", "RUNWAY_LOW:accounts.steven.runway", "RUNWAY_LOW:codex.runway"]
    got, refused, rs = day(dict(roomy, alarm_runs_per_alarm_per_day=9), two)
    check([m for m, _ in got].count("alarm") == 2, "X1: alarm_runs_per_day caps the day's alarm runs at 2: %s"
          % [m for m, _ in got])
    got, refused, rs = day(dict(roomy, alarm_runs_per_alarm_per_day=None, alarm_runs_per_day=None), keys)
    check([m for m, _ in got].count("alarm") > 2, "X1: instrument: without the limits the same flap runs more than twice")
    # unlaunch gives the day's count back
    st = fresh()
    st["roles"] = {"Operations": {"done": {}, "runs": []}}
    t = at_local("12:00")
    a = role_acts(rdecide([roomy], st, robs(ops_status(t, alarms={"RUNWAY_LOW:x": {"state": "OPEN", "for": "Operations"}})), t))
    unit = [x for x in a if x["do"] == "role_launch"][0]["unit"]
    check(st["roles"]["Operations"]["alarm_day"]["n"] == 1 and RL.unlaunch(st["roles"]["Operations"], unit)
          and "alarm_day" not in st["roles"]["Operations"], "X1: a launch that did not happen gives back the day's count")


# ---------------------------------------------------------------- go-live review (DISPATCHER_GOLIVE_FIX_THREE_BLOCKERS_FOUND)
# go-live wave 1 (design/RimMandrake/rimflow_v3_golive_wave1.md): the owner's switch may enable these and no others,
# unless the schedule's golive block names the set (trial night: the flip adds the role to golive.roles in the same file)
WAVE1_ROLES = ("Conductor", "Operations")


def shipped_schedule():
    with open(os.path.join(HERE, "dispatcher_schedule.json")) as f:
        return json.load(f)


def wave1_problems(sch):
    """-> the ways a schedule exceeds its go-live set: a role not in golive.roles (default WAVE1_ROLES) that is not
    `enabled: false`, or a seat not in golive.recover_dead (default none) whose recover_dead is not false.
    [] = within the set (a listed role may be enabled or not)."""
    g = sch.get("golive") or {}
    roles = list(g["roles"]) if isinstance(g.get("roles"), list) else list(WAVE1_ROLES)
    rec = list(g["recover_dead"]) if isinstance(g.get("recover_dead"), list) else []
    bad = ["role %s must stay disabled (go-live set: %s)" % (r.get("name"), "/".join(roles))
           for r in sch.get("roles") or [] if r.get("name") not in roles and r.get("enabled") is not False]
    bad += ["seat %s recover_dead must stay false (go-live recover_dead: %s)" % (k, "/".join(rec) or "none")
            for k, v in sorted((sch.get("seats") or {}).items()) if k not in rec and v.get("recover_dead") is not False]
    return bad


def wave1_base(sch):
    """The fixed wave-1 baseline the mutation probes start from, whatever the shipped schedule has since flipped:
    golive = Conductor/Operations and no recovery, every other role off, every seat's recover_dead false."""
    x = copy.deepcopy(sch)
    x["golive"] = {"roles": list(WAVE1_ROLES), "recover_dead": []}
    for r in x["roles"]:
        r["enabled"] = r.get("name") in WAVE1_ROLES
    for v in x["seats"].values():
        v["recover_dead"] = False
    return x


def test_golive_b3_wave1_config():
    """dispatcher-full #3: the config assertions accept the wave-1 enabled set (runbook step 14 then reaches GREEN)
    and still refuse any other role or recovery being enabled."""
    real = shipped_schedule()
    check(not wave1_problems(real), "B3 the shipped schedule is within its go-live set: %s" % (wave1_problems(real),))
    on = wave1_base(real)
    check(not wave1_problems(on), "B3 Conductor + Operations enabled is within wave 1")
    for name in ("Arbiter", "Auditor", "Producer", "Innovator"):
        x = copy.deepcopy(on)
        next(r for r in x["roles"] if r["name"] == name)["enabled"] = True
        check(wave1_problems(x) == ["role %s must stay disabled (go-live set: Conductor/Operations)" % name],
              "B3 %s enabled is refused" % name)
        del next(r for r in x["roles"] if r["name"] == name)["enabled"]
        check(wave1_problems(x), "B3 %s with no enabled key is refused (only an explicit false passes)" % name)
    check({r["name"] for r in real["roles"]} >= set(WAVE1_ROLES) | {"Arbiter", "Auditor", "Producer", "Innovator"},
          "B3 the probe roles exist in the schedule")
    for seat in sorted(real["seats"]):
        x = copy.deepcopy(on)
        x["seats"][seat]["recover_dead"] = True
        check(wave1_problems(x) == ["seat %s recover_dead must stay false (go-live recover_dead: none)" % seat],
              "B3 recover_dead on %s is refused" % seat)


def test_golive_trial_set_from_schedule():
    """trial night (design/RimMandrake/rimflow_v3_trial_night_2026-10-28.md): the set the owner's switch may enable is
    read from the schedule's golive block, not pinned in this test, so a flip is one file: the role's `enabled` and
    its name in golive.roles (recover_dead likewise: the seat in golive.recover_dead). Unlisted stays refused.
    The probes start from the fixed wave-1 baseline, so they hold after any valid flip of the shipped file."""
    g = shipped_schedule().get("golive") or {}
    check(isinstance(g.get("roles"), list) and set(WAVE1_ROLES) <= set(g["roles"])
          and isinstance(g.get("recover_dead"), list),
          "TN the shipped schedule names its go-live set (golive.roles >= wave 1, golive.recover_dead a list): %s" % (g,))
    base = wave1_base(shipped_schedule())
    x = copy.deepcopy(base)
    next(r for r in x["roles"] if r["name"] == "Arbiter")["enabled"] = True
    check(wave1_problems(x) == ["role Arbiter must stay disabled (go-live set: Conductor/Operations)"],
          "TN Arbiter enabled but not in golive.roles is refused: %s" % (wave1_problems(x),))
    x["golive"]["roles"].append("Arbiter")
    check(not wave1_problems(x), "TN Arbiter enabled AND listed in golive.roles passes (the trial flip): %s"
          % (wave1_problems(x),))
    next(r for r in x["roles"] if r["name"] == "Producer")["enabled"] = True
    check(wave1_problems(x) == ["role Producer must stay disabled (go-live set: Conductor/Operations/Arbiter)"],
          "TN listing Arbiter does not let Producer through: %s" % (wave1_problems(x),))
    y = copy.deepcopy(base)
    y["seats"]["FOUNDRY"]["recover_dead"] = True
    check(wave1_problems(y) == ["seat FOUNDRY recover_dead must stay false (go-live recover_dead: none)"],
          "TN recover_dead on FOUNDRY not in golive.recover_dead is refused: %s" % (wave1_problems(y),))
    y["golive"]["recover_dead"] = ["FOUNDRY"]
    check(not wave1_problems(y), "TN FOUNDRY recover_dead listed in golive.recover_dead passes: %s"
          % (wave1_problems(y),))
    z = copy.deepcopy(base)
    z.pop("golive")
    check(not wave1_problems(z), "TN no golive block -> wave 1 is the set (Conductor/Operations pass)")
    next(r for r in z["roles"] if r["name"] == "Arbiter")["enabled"] = True
    check(wave1_problems(z) == ["role Arbiter must stay disabled (go-live set: Conductor/Operations)"],
          "TN no golive block -> Arbiter refused: %s" % (wave1_problems(z),))


def test_golive_b1_busy_until_ended():
    """dispatcher-full #1: a run is busy until its termination is POSITIVELY established (unit, the scope named at
    creation, and no process with its marker); never retired by the clock; the stop hits that exact scope."""
    t = at_local("19:00")
    def one_run(**kw):
        r = {"unit": "rm-role-operations-1", "at": t, "day": RL.day_of(t), "budget": 1, "mode": "run", "item": "X",
             "state": "running", "seat": "BENCH", "run_max_s": 1800}
        r.update(kw)
        return {"Operations": {"done": {}, "runs": [r]}}
    # the review's case: the scope never resolved (old record), unit gone, long past run_max_s -> still busy
    st = fresh()
    st["roles"] = one_run(scope=None)
    ro = robs(ops_status(t + 7200), unit="inactive")
    a = role_acts(rdecide([operations(runs_local=["21:00"])], st, ro, t + 7200))
    run = st["roles"]["Operations"]["runs"][0]
    check(run["state"] == "running" and "role_done" not in kinds(a) and any(x.get("kind") == "role:Operations:scope"
          for x in a), "B1 scope never resolved, unit gone, 2 h past run_max_s: kept running (was retired UNCONFIRMED)")
    # a marked run: unit and scope inactive, but a marked process survives -> busy, stopped (TERM, then KILL)
    st = fresh()
    st["roles"] = one_run(scope=RL.role_scope("BENCH", "rm-role-operations-1"), marker="rm-role-operations-1")
    left = {"n": 1}
    ro = robs(ops_status(t + 600), unit="inactive")
    ro["procs"] = lambda m, **k: [4711] * left["n"] if m == "rm-role-operations-1" else []
    a = role_acts(rdecide([operations()], st, ro, t + 600))
    check(st["roles"]["Operations"]["runs"][0]["state"] == "running" and "role_done" not in kinds(a),
          "B1 unit+scope inactive but a marked process lives: still running")
    stops = []
    for k in range(3):
        a = role_acts(rdecide([operations()], st, robs_with(ro, ops_status(t + 1900 + k * 120)), t + 1900 + k * 120))
        stops += [x for x in a if x["do"] == "role_stop"]
    check(len(stops) == 3 and all(x["scope"] == "claude-seat-BENCH-rm-role-operations-1.scope" and x["unit_gone"]
                                  and x["marker"] == "rm-role-operations-1" for x in stops)
          and [x["force"] for x in stops] == [False, False, True],
          "B1 overtime: the exact scope + marker are stopped each tick, KILL from the third stop")
    ro["procs"] = lambda m, **k: None
    a = role_acts(rdecide([operations()], st, robs_with(ro, ops_status(t + 2400)), t + 2400))
    check(st["roles"]["Operations"]["runs"][0]["state"] == "running", "B1 marker scan UNMEASURED: still running")
    del ro["procs"]
    a = role_acts(rdecide([operations()], st, robs_with(ro, ops_status(t + 2500)), t + 2500))
    check(st["roles"]["Operations"]["runs"][0]["state"] == "running", "B1 no marker observer at all: still running")
    ro["procs"] = lambda m, **k: []
    a = role_acts(rdecide([operations()], st, robs_with(ro, ops_status(t + 2600)), t + 2600))
    check(st["roles"]["Operations"]["runs"][0]["state"] in ("done", "failed") and "role_done" in kinds(a),
          "B1 unit, scope and marker scan all clear: then the run is finished")
    # stop(): each name its own call; marked survivors get TERM, KILL when forced; scan blind is said
    calls, sigs = [], []
    run_ok = lambda argv, **kw: calls.append(argv) or subprocess.CompletedProcess(argv, 0, "", "")
    out = RL.stop("U", "S.scope", runner=run_ok, unit_gone=True, marker="U", procs=lambda m, **k: [11, 12],
                  kill=lambda pid, sig: sigs.append((pid, sig)))
    check(calls == [["systemctl", "--user", "stop", "--no-block", "S.scope"]] and sigs == [(11, 15), (12, 15)]
          and "TERM" in out,
          "B1 stop: the exact scope, then TERM to the marked survivors")
    sigs.clear()
    RL.stop("U", "S.scope", runner=run_ok, unit_gone=True, marker="U", procs=lambda m, **k: [11], force=True,
            kill=lambda pid, sig: sigs.append((pid, sig)))
    check(sigs == [(11, 9)], "B1 stop forced: KILL")
    check("UNMEASURED" in RL.stop("U", "S.scope", runner=run_ok, unit_gone=True, marker="U", procs=lambda m, **k: None),
          "B1 stop: a blind marker scan is said, not hidden")
    # procs_of: a fake /proc, and the real one with a live marked child
    fp = os.path.join(TMP, "fakeproc")
    for pid, env in (("101", b"A=1\0RM_ROLE_UNIT=uX\0"), ("102", b"RM_ROLE_UNIT=uXY\0"), ("self", b"")):
        os.makedirs(os.path.join(fp, pid), exist_ok=True)
        with open(os.path.join(fp, pid, "environ"), "wb") as f:
            f.write(env)
    os.makedirs(os.path.join(fp, "103"), exist_ok=True)       # no environ: skipped, not a failure
    check(RL.procs_of("uX", proc=fp) == [101], "B1 procs_of: exact marker match only (uXY is another run)")
    check(RL.procs_of("uX", proc=os.path.join(TMP, "no_such_proc")) is None, "B1 procs_of: /proc unreadable -> None")
    # a process mid-exec is unreadable for a moment (the live flake: young siblings under parallel load); a
    # non-dumpable one stays so. A fake /proc with a 000 environ made readable after 60 ms:
    import threading
    tp = os.path.join(TMP, "transientproc")
    for pid in ("201", "202"):
        os.makedirs(os.path.join(tp, pid), exist_ok=True)
    for pid, env in (("201", b"RM_ROLE_UNIT=uT\0"), ("202", b"RM_ROLE_UNIT=uOther\0")):
        with open(os.path.join(tp, pid, "environ"), "wb") as f:
            f.write(env)
    if os.getuid() != 0:
        e201 = os.path.join(tp, "201", "environ")
        os.chmod(e201, 0)
        thr = threading.Timer(0.06, os.chmod, (e201, 0o644))
        thr.start()
        check(RL.procs_of("uT", proc=tp) == [201], "B1 procs_of: a transiently unreadable environ is re-read, not blind")
        thr.join()
        os.chmod(e201, 0)
        check(RL.procs_of("uT", proc=tp) is None, "B1 procs_of: a persistently unreadable environ stays blind")
        os.chmod(e201, 0o644)
        _r = RL.SCAN_RETRIES
        RL.SCAN_RETRIES = 0                     # control: without the re-read the transient case is blind (the old code)
        try:
            os.chmod(e201, 0)
            thr = threading.Timer(0.06, os.chmod, (e201, 0o644))
            thr.start()
            check(RL.procs_of("uT", proc=tp) is None, "B1 procs_of control: no retries -> blind on a transient")
            thr.join()
        finally:
            RL.SCAN_RETRIES = _r
    mk = "selftest-marker-%d" % os.getpid()
    t_run = time.time()      # a run's `at`: this user's older unreadable processes (systemd, sd-pam) predate it
    # The real /proc is shared with every co-running selftest: their young same-uid children (python3, git,
    # reg.exe mid-exec) are unreadable for a moment, and a scan that meets one past SCAN_RETRIES is blind (None),
    # which the Dispatcher treats as UNMEASURED and rescans next tick. Measured under testq+contracts load
    # 2026-10-29: 11/489 single scans blind with no re-read (the old code; 1 in 14 runs FAILed "none once it is
    # gone"), 0/479 with it. These rows test what a live scan SEES, so a blind scan is rescanned (bounded) like
    # the next tick would, and its reason is printed (DISPATCHER_HUNT_SELFTEST_PARALLEL_FLAKE).
    def live(mk_, since_):
        for _ in range(10):
            pids, blind = RL.scan_marked(mk_, since=since_)
            if not blind:
                return pids, None
            time.sleep(0.2)
        return None, blind
    p = subprocess.Popen(["sleep", "30"], env=dict(os.environ, RM_ROLE_UNIT=mk))
    try:
        got, blind = live(mk, t_run)
        check(got == [p.pid], "B1 procs_of on the real /proc sees a live marked process (%s, blind: %s)"
              % (got, blind))
    finally:
        p.kill()
        p.wait()
    got, blind = live(mk, t_run)
    check(got == [], "B1 procs_of: none once it is gone (%s, blind: %s)" % (got, blind))
    # execute: the scope and marker are on disk BEFORE systemd-run, and a launcher's own scope cannot replace them
    sch = sched(roles=[conductor()])
    act = {"do": "role_launch", "role": "Conductor", "unit": "UB1", "message": "m", "ticket": "ROLES_ITEM_X",
           "note": False, "mode": "quick", "budget": 1, "slot": "k", "band": "GREEN", "why": "w", "seat": "BENCH",
           "run_max_s": 1800}
    seen = []
    st = fresh()
    def persist():
        r = (st.get("roles", {}).get("Conductor", {}).get("runs") or [{}])[0]
        seen.append((r.get("scope"), r.get("marker")))
    D.execute([act], sch, st, TMP, True, 100.0, {"note": lambda i, x: (True, ""), "publish": lambda n: None,
              "lock": lambda: open(os.devnull), "off": lambda p: None, "paused": lambda: None, "persist": persist,
              "role_launch": lambda *x: (True, "ok", {"scope": "other.scope", "marker": "zz"})})
    check(seen and seen[0] == ("claude-seat-BENCH-UB1.scope", "UB1")
          and st["roles"]["Conductor"]["runs"][0]["scope"] == "claude-seat-BENCH-UB1.scope",
          "B1 execute: scope+marker persisted before systemd-run and kept authoritative")
    # claude_bounded.sh: the launcher's name is used, a bad one refused, and it is not inherited by the child
    src = open(os.path.join(os.path.dirname(HERE), "Utils", "claude_bounded.sh")).read()
    blk = src[src.index('SCOPE_NAME="claude-seat-'):src.index("unset CLAUDE_SCOPE_UNIT")]
    for val, want in (("claude-seat-BENCH-rm-role-x-1", "claude-seat-BENCH-rm-role-x-1"), ("", "claude-seat-S-"),
                      ("bad name;rm", "claude-seat-S-")):
        sh = "red(){ :; }; SEAT=S; " + blk + "unset CLAUDE_SCOPE_UNIT; printf '%s|%s' \"$SCOPE_NAME\" \"${CLAUDE_SCOPE_UNIT-unset}\""
        o = subprocess.run(["bash", "-c", sh], env=dict(os.environ, CLAUDE_SCOPE_UNIT=val), capture_output=True,
                           text=True, timeout=30).stdout
        check(o.startswith(want) and o.endswith("|unset"), "B1 claude_bounded scope name for %r: %r" % (val, o))
    check('--unit="$SCOPE_NAME"' in src, "B1 claude_bounded: the scope is created under that name")


def test_ts_skip_journalled_once():
    """DISPATCHER_JOURNAL_TAME_REPEAT_TS_SKIPS: one bad-ts ledger line is journalled once, not every tick."""
    root = os.path.join(TMP, "tsskip_root")
    sc = os.path.join(TMP, "tsskip_clone")
    sh = os.path.join(sc, "infrastructure", "state", "ledger", "events", "FOUNDRY.jsonl")
    os.makedirs(os.path.dirname(sh), exist_ok=True)
    with open(sh, "w") as f:
        f.write(json.dumps({"seat": "FOUNDRY", "event": "claim", "id": "BAD_ONE", "ts": "yesterday"}) + "\n")
    st = {}
    for _ in range(3):      # three ticks: a fresh hook each time, the same state
        D.seat_events_since(sc, "FOUNDRY", "2000-01-01T00:00:00Z", on_skip=D._skip_journal(root, st))
    jp = os.path.join(root, "journal.jsonl")
    n = sum(1 for l in open(jp) if "ledger_ts_skipped" in l and "BAD_ONE" in l)
    check(n == 1, "the same bad line is journalled once across ticks, got %d" % n)
    with open(sh, "a") as f:
        f.write(json.dumps({"seat": "FOUNDRY", "event": "claim", "id": "BAD_TWO", "ts": "later"}) + "\n")
    D.seat_events_since(sc, "FOUNDRY", "2000-01-01T00:00:00Z", on_skip=D._skip_journal(root, st))
    n = sum(1 for l in open(jp) if "ledger_ts_skipped" in l)
    check(n == 2, "a new bad line is journalled: %d" % n)
    for i in range(D.TS_SKIPS_KEEP + 50):
        D._skip_journal(root, st)({"seat": "S", "id": "E%d" % i, "ts": "x"})
    check(len(st["ts_skips"]) <= D.TS_SKIPS_KEEP, "the seen set is bounded: %d" % len(st["ts_skips"]))
    # review night r6: a fixed backlog LARGER than the seen set must not be re-journalled on every scan (an evicting
    # set cycles through it); past the cap one overflow line per seat is journalled, then silence
    root2, st2 = os.path.join(TMP, "tsskip_root2"), {}
    for _ in range(3):
        hook = D._skip_journal(root2, st2)
        for i in range(D.TS_SKIPS_KEEP + 1):
            hook({"seat": "S", "id": "B%d" % i, "ts": "x"})
    lines = [l for l in open(os.path.join(root2, "journal.jsonl")) if "ledger_ts_skipped" in l]
    check(len(lines) == D.TS_SKIPS_KEEP + 1, "a backlog past the cap is journalled once (+1 overflow line), got %d"
          % len(lines))


def test_golive_b2_blind_fixed_outcomes():
    """dispatcher-full #2: a blind item gets fixed outcome texts only. Outside text with an account id or a figure in
    words no token list knows (PAUSE/off reasons, launch errors, exception text, result subtypes) never reaches it;
    it stays in the journal (`why`) or goes to Operations' item. A blind field outside its closed set diverts."""
    secret = ("acct-7781", "4.2M", "42%")
    sch = sched(roles=[conductor(), operations(ledger_item="OPS_OWN_X", token_aware=True)],
                token_notes_item="OPS_OWN_X", ledger_notes=True)
    rx = D.token_rx()
    check(not any(rx.search(x) for x in secret), "B2 probe: the outside figures carry no token keyword")
    root = os.path.join(TMP, "golive_b2")
    t8 = at_local("08:00")
    noted = []
    base = {"note": lambda i, t: noted.append((i, t)) or (True, ""), "publish": lambda n: "p",
            "lock": lambda: open(os.devnull), "off": lambda p: None, "paused": lambda: None}

    def run(fx_extra, st=None):
        st = st or fresh()
        acts = [x for x in rdecide([conductor()], st, robs(ops_status(t8)), t8) if x["do"] == "role_launch"]
        del noted[:]
        out = D.execute(acts, sch, st, root, True, t8, dict(base, **fx_extra))
        return out, [t for i, t in noted if i == "ROLES_ITEM_X"], [t for i, t in noted if i == "OPS_OWN_X"]

    def boom(*a):
        raise RuntimeError("acct-7781 has 4.2M left")
    cases = (("PAUSE reason", {"paused": lambda: "acct-7781 at 42%"}, "held by PAUSE, not launched"),
             ("off reason", {"off": lambda p: "acct-7781 down to 4.2M"}, "held by its off switch, not launched"),
             ("launch error", {"role_launch": lambda *a: (False, "systemd-run exit 1: acct-7781 4.2M left", {})},
              "launch failed, retried"),
             ("exception text", {"role_launch": boom}, "launch outcome unknown, the run stays tracked"))
    for label, fx, want in cases:
        out, blind_notes, ops_notes = run(fx)
        journal = repr(out)
        check(len(blind_notes) == 1 and blind_notes[0].endswith(": " + want)
              and not any(x in blind_notes[0] for x in secret),
              "B2 %s: the shared item gets the fixed outcome only: %r" % (label, blind_notes))
        check("acct-7781" in journal or any("acct-7781" in t for t in ops_notes),
              "B2 %s: the detail stays in the journal / Operations' item" % label)
    # a result subtype with an account id: the done note is the fixed outcome
    role = conductor()
    for sub, want in (("success", "completed"), ("error_acct_7781_4.2M", "ended without a good result")):
        st = {"roles": {"Conductor": {"runs": [{"state": "running", "unit": "rm-role-conductor-5", "at": 0,
                                                "budget": 30000, "item": role["ledger_item"], "mode": "quick",
                                                "scope": "s"}]}}}
        acts = []
        RL.supervise_roles({"roles": [role]}, st, {"unit_state": lambda u: "inactive", "result": lambda r: {
            "usage": usage(input_tokens=1000, output_tokens=10), "modelUsage": {"opus": {}}, "subtype": sub,
            "is_error": sub != "success"}}, 5000.0, lambda **k: acts.append(k))
        notes = [RL.blind_note(a.get("blind")) for a in acts if a.get("blind")]
        check(any(n and n.endswith(": " + want) for n in notes)
              and not any("7781" in (n or "") or "4.2M" in (n or "") or sub in (n or "") for n in notes),
              "B2 subtype %r: blind notes are fixed (%r)" % (sub, notes))
    # 10-30: an expired login reports subtype success, is_error true, 0 tokens: `why` must not read "failed ... success"
    st = {"roles": {"Conductor": {"runs": [{"state": "running", "unit": "rm-role-conductor-6", "at": 0, "budget": 30000,
                                            "item": role["ledger_item"], "mode": "quick", "scope": "s"}]}}}
    acts = []
    RL.supervise_roles({"roles": [role]}, st, {"unit_state": lambda u: "inactive", "result": lambda r: {
        "usage": usage(), "subtype": "success", "is_error": True, "terminal_reason": "api_error"}}, 5000.0,
        lambda **k: acts.append(k))
    check(any("is_error (api_error)" in (a.get("why") or "") for a in acts), "a failed run says why it failed: %s"
          % [a.get("why") for a in acts])
    # closed sets: any field outside them -> None, and execute diverts that note to Operations' item
    good = RL.blind("Conductor", "completed", "quick", "rm-role-conductor-9")
    check(RL.blind_note(good) == "dispatcher: Conductor quick run: completed", "B2 a good note")
    for bad in (dict(good, role="acct-7781"), dict(good, mode="acct-7781"), dict(good, outcome="acct-7781 at 42%"),
                dict(good, unit="rm-role-conductor-9 acct-7781"), dict(good, unit="rm-role-arbiter-9"),
                dict(good, outcome="subtype"), "Conductor completed", None):
        check(RL.blind_note(bad) is None, "B2 closed set refuses %r" % (bad,))
    del noted[:]
    D.execute([{"do": "role_done", "role": "Conductor", "ticket": "ROLES_ITEM_X", "note": True,
                "why": "Conductor run done, acct-7781 4.2M", "blind": dict(good, outcome="acct-7781")}],
              sch, fresh(), root, True, 100.0, base)
    check(noted and noted[0][0] == "OPS_OWN_X" and "acct-7781" in noted[0][1],
          "B2 a refused blind note goes to Operations' item, never the shared one")
    src = open(os.path.join(HERE, "role_launch.py")).read() + open(os.path.join(HERE, "dispatcher.py")).read()
    check("def note_text" not in src and "note_base" not in src and "note_text=" not in src,
          "B2 no free-text note_text/note_base path is left (the closed renderer is contracts.blind_core.note_text)")
    check(D.route_note(sch, "ROLES_ITEM_X", "x", blind_text="dispatcher: Conductor: acct-7781 4.2M")[0] != "ROLES_ITEM_X",
          "B2 route_note refuses a blind_text no closed record renders (blind_core.is_note_text)")
    check(D.route_note(sch, "ROLES_ITEM_X", "x", blind_text=RL.blind_note(good)) == ("ROLES_ITEM_X", RL.blind_note(good)),
          "B2 route_note takes a closed note")


def test_golive_m4_disabled_parent_holds():
    """dispatcher-full #4: Operations finished its 19:30 run, then was disabled: the Conductor's 20:00 slot waits; its
    persisted success does not stand in. Enabled, the same state launches (control)."""
    t20 = at_local("20:00")
    key = "%s 19:30" % RL.day_of(t20)
    for ops_on in (True, False):
        st = fresh()
        st["roles"] = {"Operations": {"done": {key: "launched"}, "runs": [
            {"state": "done", "slot": key, "mode": "run", "unit": "rm-role-operations-1", "at": t20 - 1800}]}}
        acts = role_acts(rdecide([conductor(after_role="Operations"), operations(enabled=ops_on, alarm_runs=False)],
                                 st, robs(ops_status(t20)), t20))
        la = [a for a in acts if a["do"] == "role_launch" and a["role"] == "Conductor"]
        if ops_on:
            check(la, "M4 control: Operations enabled and done at 19:30 -> the Conductor's 20:00 launches")
        else:
            holds = [a for a in acts if a["do"] == "role_hold" and a.get("role") == "Conductor"]
            check(not la and any("waits" in h["why"] and h["why"].endswith("Operations is not enabled") for h in holds)
                  and st["roles"]["Conductor"]["waiting"][1] == "Operations is not enabled",
                  "M4 Operations disabled after its 19:30 run: the Conductor's 20:00 waits (%r)" % (
                      [a.get("why") for a in holds],))


def test_golive_m5_malformed_obs():
    """dispatcher-full #5, through tick() with persisted state: a malformed `claude agents` reading is UNMEASURED and
    the overtime stop still executes; a seat whose processing raises is alarmed and the launch and the stop still
    execute; a tick that raises gives back the launch it decided and never executed, and journals it."""
    t8 = at_local("08:00")
    state = os.path.join(TMP, "state_m5")
    sch = sched(roles=[conductor(after_role=None), operations(alarm_runs=False, runs_local=["23:00"],
                                                                economy_pass_local=None)], ledger_notes=False)

    def start(seats=None):
        if os.path.isdir(state):
            shutil.rmtree(state)
        os.makedirs(state)
        st = fresh()
        st["seats"] = seats or {}
        st["roles"] = {"Operations": {"done": {}, "runs": [
            {"state": "running", "unit": "rm-role-operations-5", "at": t8 - 20000, "run_max_s": 600, "mode": "run",
             "scope": "claude-seat-BENCH-rm-role-operations-5.scope", "marker": "rm-role-operations-5",
             "item": "ROLES_ITEM_X", "seat": "BENCH"}]}}
        D.S.dump(st, os.path.join(state, "state.json"))
    launched, stopped = [], []
    fx = {"role_launch": lambda *a: launched.append(a[1]) or (True, "ok", {}),
          "role_stop": lambda *a, **k: stopped.append(a[0]) or "stopped", "note": lambda i, t: (True, ""),
          "publish": lambda n: "p", "lock": lambda: open(os.devnull), "off": lambda p: None, "paused": lambda: None,
          "ring": lambda *x: None, "withdraw": lambda *x: "withdrawn"}

    def o(sessions, consumed=None):
        x = obs(sessions=sessions)
        x["roles"] = robs(ops_status(t8))
        if consumed:
            x["consumed"] = consumed
        return x
    os.environ["RM_DISPATCHER_STATE"] = state
    real_exec = D.execute
    try:
        for bad in ([None], [sess(), "AGENT FOUNDRY"], [sess(), 7]):
            start()
            del launched[:], stopped[:]
            acts = D.tick(sch, True, obs=o(bad), now=t8, fx=fx)
            st = D.load_state(state)
            check(stopped == ["rm-role-operations-5"] and any(a["do"] == "skip" and "UNMEASURED" in a["why"]
                                                              for a in acts)
                  and not launched and not st["roles"].get("Conductor", {}).get("pending_launch"),
                  "M5 sessions %r: UNMEASURED, the overtime stop executes, nothing reserved" % (bad,))
        check(D.sessions_ok([sess()]) and D.sessions_ok([]) and not D.sessions_ok({"a": 1})
              and not D.sessions_ok([sess(), None]), "M5 sessions_ok: a list of objects only")

        def raises(seat, rid):
            raise KeyError("consumed_at")
        start({"FOUNDRY": {"ring": {"ring_id": "r1", "rung_at": t8 - 100, "rung_iso": "2026-01-01T00:00:00Z",
                                    "ticket": "T"}}})
        del launched[:], stopped[:]
        acts = D.tick(sch, True, obs=o(None, raises), now=t8, fx=fx)
        st = D.load_state(state)
        check(any(a.get("kind") == "decide:FOUNDRY" for a in acts) and stopped == ["rm-role-operations-5"]
              and len(launched) == 1 and launched[0].startswith("rm-role-conductor-")
              and st["roles"]["Conductor"]["runs"] and not st["roles"]["Conductor"].get("pending_launch"),
              "M5 a seat that raises is alarmed; the stop and the Conductor launch still execute")

        def boom(*a, **k):
            raise RuntimeError("execute died")
        start()
        D.execute = boom
        raised = False
        try:
            D.tick(sch, True, obs=o(None), now=t8, fx=fx)
        except RuntimeError:
            raised = True
        D.execute = real_exec
        st = D.load_state(state)
        cr = st["roles"].get("Conductor") or {}
        jr = open(os.path.join(state, "journal.jsonl")).read()
        check(raised and not cr.get("pending_launch") and not (cr.get("done") or {}) and "tick:raised" in jr
              and "rm-role-conductor-" in jr,
              "M5 a tick that raises gives back the launch it never executed and journals it (%r)" % (cr,))
        st2 = fresh()
        D.decide(sch, st2, o(None), t8, True)
        check(st2["roles"]["Conductor"].get("pending_launch") and st2["roles"]["Conductor"]["done"],
              "M5 probe: the same tick does reserve a Conductor launch (the give-back above is real)")
    finally:
        D.execute = real_exec
        os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "state")


def test_golive_m8_ring_withdraw_and_pause():
    """dispatcher-full #8: a seat disabled, or its wake switched off, withdraws its unconsumed ring (a consumed one
    stays and is verified); PAUSE appearing between decide and execute holds the ring: nothing is written, the
    pending ring and the wake are given back."""
    t0 = 1000.0
    for change, label in (({"enabled": False}, "disabled"), ({"wake": False}, "wake off")):
        sch = sched()
        st = fresh()
        a = stall(sch, st, obs(), t0)
        rid = [x for x in a if x["do"] == "ring"][0]["ring_id"]
        sch["seats"]["FOUNDRY"].update(change)
        a = D.decide(sch, st, obs(), t0 + sch["stall_after_s"] + 60, True)
        w = [x for x in a if x["do"] == "withdraw"]
        check(w and w[0]["ring_id"] == rid and w[0]["pending"]["ring_id"] == rid and not st["seats"]["FOUNDRY"].get("ring"),
              "M8 seat %s: its unconsumed ring is withdrawn" % label)
        st2 = fresh()
        stall(sched(), st2, obs(), t0)
        st2["seats"]["FOUNDRY"]["ring"]["consumed_at"] = t0 + 5
        a = D.decide(sch, st2, obs(), t0 + sch["stall_after_s"] + 60, True)
        check(not [x for x in a if x["do"] == "withdraw"] and st2["seats"]["FOUNDRY"].get("ring"),
              "M8 seat %s: a ring the doorbell already took is kept" % label)
    sch = sched()
    rung = []
    fx = {"ring": lambda *x: rung.append(x), "lock": lambda: None, "publish": lambda n: "p",
          "note": lambda i, t: (True, "")}
    for paused in ("owner: stop", None):
        st = fresh()
        D.decide(sch, st, obs(), t0, True)
        t1 = t0 + sch["stall_after_s"]
        before = st["seats"]["FOUNDRY"]["idle_since"]
        a = D.decide(sch, st, obs(), t1, True)
        check([x for x in a if x["do"] == "ring"] and st["seats"]["FOUNDRY"].get("ring") and len(st["wakes"]) == 1,
              "M8 probe: decide rang (paused=%r)" % paused)
        del rung[:]
        D.execute(a, sch, st, os.path.join(TMP, "m8"), True, t1, dict(fx, paused=lambda: paused))
        if paused:
            check(not rung and not st["seats"]["FOUNDRY"].get("ring") and not st["wakes"]
                  and st["seats"]["FOUNDRY"]["idle_since"] == before
                  and a[[x["do"] for x in a].index("ring")]["result"].startswith("held at release: PAUSE"),
                  "M8 PAUSE after decide: the ring is not released; ring, wake and stall clock given back")
        else:
            check(len(rung) == 1 and st["seats"]["FOUNDRY"].get("ring"), "M8 control: no PAUSE -> the ring is rung")


def test_review_night_n1():
    """night review 2026-10-27 (BENCH full-file): N1 the seat's session id is learned while it cools down or a
    recover is in flight (a later recover must resume the CURRENT session, not the one seen before the cooldown);
    N2 PAUSE is read again at a recover's release, like a ring's and a launch's; N3 a tick that raises after decide()
    gives back the rings it decided but never released (no phantom attempt, no phantom wake on the caps)."""
    t0 = 50000.0
    sch = sched()
    st = fresh()
    D.decide(sch, st, obs(), t0, True)
    st["seats"]["FOUNDRY"]["cooldown_until"] = t0 + 99999
    D.decide(sch, st, obs(sessions=[sess(sid="sid-NEW"), sess("AGENT BENCH", "busy", "b")]), t0 + 10, True)
    check(st["seats"]["FOUNDRY"].get("session_id") == "sid-NEW",
          "N1 a session seen during the cooldown is remembered (%r)" % st["seats"]["FOUNDRY"].get("session_id"))
    st = fresh()
    D.decide(sch, st, obs(), t0, True)
    st["seats"]["FOUNDRY"]["recover"] = {"at": t0, "session_id": "sid-1"}
    D.decide(sch, st, obs(sessions=[sess(sid="sid-OTHER"), sess("AGENT BENCH", "busy", "b")]), t0 + 10, True)
    check(st["seats"]["FOUNDRY"].get("session_id") == "sid-OTHER",
          "N1 a session seen while a recover is verified is remembered (%r)" % st["seats"]["FOUNDRY"].get("session_id"))
    # N2: recover decided, PAUSE created before its release
    gone = [sess("AGENT BENCH", "busy", "b")]
    for paused in ("owner: stop", None):
        st = fresh()
        D.decide(sch, st, obs(), t0, True)
        D.decide(sch, st, obs(sessions=gone), t0 + 100, True)
        t1 = t0 + 100 + sch["dead_after_s"]
        a = D.decide(sch, st, obs(sessions=gone), t1, True)
        calls = []
        fx = {"recover": lambda cfg, sid, msg: (calls.append(sid), (True, "started"))[1], "lock": lambda: None,
              "publish": lambda n: "p", "note": lambda i, t: (True, ""), "paused": lambda: paused}
        D.execute(a, sch, st, os.path.join(TMP, "n2"), True, t1, fx)
        r = [x for x in a if x["do"] == "recover"]
        if paused:
            check(r and not calls and not st["seats"]["FOUNDRY"].get("recover") and not st["recovers"]
                  and r[0]["result"].startswith("held at release: PAUSE"),
                  "N2 PAUSE after decide: the recover is not released; its record and cap entry are given back (%r)"
                  % (([x.get("result") for x in r], calls, st["recovers"]),))
        else:
            check(calls == ["sid-1"] and st["seats"]["FOUNDRY"].get("recover"), "N2 control: no PAUSE -> recovered")
    # N3: a tick killed (SIGTERM -> SystemExit) at the ingest.lock wait, after decide rang
    old = os.environ.get("RM_DISPATCHER_STATE")
    os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "n3state")
    try:
        def killed():
            raise SystemExit(143)
        fx = {"ring": lambda *x: None, "lock": killed, "publish": lambda n: "p", "note": lambda i, t: (True, "")}
        sch3 = sched()
        D.tick(sch3, True, obs=obs(), now=t0, fx=dict(fx, lock=lambda: None))
        try:
            D.tick(sch3, True, obs=obs(), now=t0 + sch3["stall_after_s"], fx=fx)
            check(False, "N3 probe: the killed tick raised")
        except SystemExit:
            pass
        st = D.load_state(D.state_root(True))
        ss = st["seats"].get("FOUNDRY") or {}
        check(not ss.get("ring") and not st["wakes"] and ss.get("idle_since") == t0,
              "N3 a tick killed before its ring was released keeps no pending ring, no wake, and the stall clock "
              "(ring=%r wakes=%r idle_since=%r)" % (ss.get("ring"), st["wakes"], ss.get("idle_since")))
        # ... and killed INSIDE decide, at a later seat's peek, after FOUNDRY's ring was decided
        shutil.rmtree(os.path.join(TMP, "n3state"), ignore_errors=True)
        sch4 = sched()
        sch4["seats"]["ZED"] = dict(sch4["seats"]["FOUNDRY"], session_name="AGENT ZED")
        o4 = obs(sessions=[sess(), sess("AGENT BENCH", "busy", "b"), sess("AGENT ZED", sid="z")])

        def peek(seat):
            if seat == "ZED":
                raise SystemExit(143)
            return {"id": "SOME_ITEM_DO_IT", "needs": "offline"}
        D.tick(sch4, True, obs=dict(o4, peek=lambda seat: {}), now=t0, fx=dict(fx, lock=lambda: None))
        try:
            D.tick(sch4, True, obs=dict(o4, peek=peek), now=t0 + sch4["stall_after_s"], fx=fx)
            check(False, "N3 probe: the tick killed in decide raised")
        except SystemExit:
            pass
        st = D.load_state(D.state_root(True))
        ss = st["seats"].get("FOUNDRY") or {}
        check(not ss.get("ring") and not st["wakes"] and ss.get("idle_since") == t0,
              "N3 a tick killed inside decide gives back the ring it had decided (ring=%r wakes=%r)"
              % (ss.get("ring"), st["wakes"]))
        # ... and killed before a decided WITHDRAW ran: the ring may still be in the inbox, so it stays pending
        shutil.rmtree(os.path.join(TMP, "n3state"), ignore_errors=True)
        D.tick(sch3, True, obs=obs(), now=t0, fx=dict(fx, lock=lambda: None))
        D.tick(sch3, True, obs=obs(), now=t0 + sch3["stall_after_s"], fx=dict(fx, lock=lambda: None))
        rid = (D.load_state(D.state_root(True))["seats"]["FOUNDRY"].get("ring") or {}).get("ring_id")
        try:
            D.tick(sch3, True, obs=obs(), now=t0 + sch3["stall_after_s"] + sch3["verify_s"], fx=fx)
            check(False, "N3 probe: the tick killed before its withdraw raised")
        except SystemExit:
            pass
        st = D.load_state(D.state_root(True))
        check(rid and (st["seats"]["FOUNDRY"].get("ring") or {}).get("ring_id") == rid,
              "N3 a tick killed before its withdraw ran keeps the ring pending (%r -> %r)"
              % (rid, st["seats"]["FOUNDRY"].get("ring")))
    finally:
        if old is None:
            os.environ.pop("RM_DISPATCHER_STATE", None)
        else:
            os.environ["RM_DISPATCHER_STATE"] = old
    # N5: a seat REMOVED from the schedule with an unconsumed ring in its inbox has that ring withdrawn
    sch6 = sched()
    st = fresh()
    stall(sch6, st, obs(), t0)
    rid = st["seats"]["FOUNDRY"]["ring"]["ring_id"]
    del sch6["seats"]["FOUNDRY"]
    a = D.decide(sch6, st, obs(), t0 + sch6["stall_after_s"] + 30, True)
    w = [x for x in a if x["do"] == "withdraw"]
    check(w and w[0]["ring_id"] == rid and not st["seats"]["FOUNDRY"].get("ring"),
          "N5 a seat gone from the schedule has its waiting ring withdrawn (%r)" % kinds(a))
    st = fresh()
    stall(sched(), st, obs(), t0)
    st["seats"]["FOUNDRY"]["ring"]["consumed_at"] = t0 + 5
    a = D.decide(sch6, st, obs(), t0 + sch6["stall_after_s"] + 30, True)
    check(not st["seats"]["FOUNDRY"].get("ring") and [x for x in a if x["do"] == "skip" and x.get("seat") == "FOUNDRY"],
          "N5 a removed seat's delivered ring is dropped and said, never pending forever (%r)" % kinds(a))
    st = fresh()
    stall(sched(), st, obs(), t0)
    a = D.decide(sch6, st, obs(), t0 + sch6["stall_after_s"] + 30, True)
    D.execute(a, sch6, st, os.path.join(TMP, "n5"), True, t0 + 300,
              {"withdraw": lambda root, seat, rid: {"outcome": "consumed", "ring_id": rid, "consumed_at": t0 + 9},
               "lock": lambda: None, "publish": lambda n: "p", "note": lambda i, t: (True, "")})
    check(not st["seats"]["FOUNDRY"].get("ring"), "N5 a removed seat's withdraw that finds it consumed does not re-pend it")
    # N6: the last attempt's withdraw finds the doorbell took it after all: no give-up alarm, no cooldown
    sch7 = sched()
    st = fresh()
    now = 1000.0
    D.decide(sch7, st, obs(), now, True)
    last = []
    for _ in range(40):
        now += 60
        last = D.decide(sch7, st, obs(), now, True)
        if [x for x in last if x["do"] == "alarm" and x.get("kind") == "undelivered:FOUNDRY"]:
            break
    check([x for x in last if x["do"] == "withdraw"], "N6 probe: the give-up tick withdraws and alarms")
    noted = []
    D.execute(last, sch7, st, os.path.join(TMP, "n6"), True, now,
              {"withdraw": lambda root, seat, rid: {"outcome": "consumed", "ring_id": rid, "consumed_at": now - 1},
               "lock": lambda: None, "publish": lambda n: "p", "note": lambda i, t: (noted.append(t), (True, ""))[1]})
    al = [x for x in last if x.get("kind") == "undelivered:FOUNDRY"][0]
    check(st["seats"]["FOUNDRY"].get("ring") and not st["seats"]["FOUNDRY"].get("cooldown_until")
          and "never consumed" not in (al.get("result") or "") and not al.get("note"),
          "N6 a give-up whose ring was consumed after all is not alarmed and starts no cooldown (%r, %r)"
          % (al.get("result"), st["seats"]["FOUNDRY"].get("cooldown_until")))
    # N4: the publish index.lock alarm goes through route_note like every other note (never raw onto a blind item)
    sch5 = sched(roles=[{"name": "Arbiter", "enabled": False, "ledger_item": "BLIND_ITEM_X"}],
                 alarm_item="BLIND_ITEM_X", token_notes_item="OPS_ITEM_X")
    noted = []
    D.execute([], sch5, fresh(), os.path.join(TMP, "n4"), True, t0,
              {"lock": lambda: object.__new__(type("L", (), {"close": lambda self: None})),
               "publish": lambda n: "fatal: index.lock exists", "note": lambda i, t: (noted.append(i), (True, ""))[1]})
    check(noted == ["OPS_ITEM_X"], "N4 the publish index.lock alarm is diverted off a blind alarm_item (%r)" % noted)


def test_golive_m6_weekday_slot_keys():
    """dispatcher-full #6: a weekday-qualified parent slot ("Wed 07:30") and its dependent ("Wed 08:00") agree on the
    key: the parent's done run, keyed by the due list (the writer), releases the dependent (after_slots, the reader)."""
    wd = RL.WEEKDAYS[RL.weekday(DAY0)]
    t730, t8 = at_local("07:30"), at_local("08:00")
    roles = [conductor(after_role="Operations", quick_checks_local=[wd + " 08:00"]),
             operations(runs_local=[wd + " 07:30"], economy_pass_local=None, alarm_runs=False)]
    st = fresh()
    acts = role_acts(rdecide(roles, st, robs(ops_status(t730)), t730))
    keys = list((st["roles"].get("Operations") or {}).get("done") or {})
    check([a for a in acts if a["do"] == "role_launch" and a["role"] == "Operations"] and len(keys) == 1,
          "M6 probe: Operations' %s 07:30 slot launches and is keyed (%r)" % (wd, keys))
    check(RL.after_slots(roles[1], {"slot": wd + " 08:00"}, t8) == keys,
          "M6 reader and writer agree on the weekday slot key (%r vs %r)" % (
              RL.after_slots(roles[1], {"slot": wd + " 08:00"}, t8), keys))
    st["roles"]["Operations"]["runs"] = [{"state": "done", "slot": keys[0] if keys else None, "mode": "run",
                                           "unit": "rm-role-operations-1", "at": t730}]
    acts = role_acts(rdecide(roles, st, robs(ops_status(t8)), t8))
    check([a for a in acts if a["do"] == "role_launch" and a["role"] == "Conductor"],
          "M6 the Conductor's %s 08:00 follows Operations' done %s 07:30 run (%r)" % (
              wd, wd, [a.get("why") for a in acts if a.get("role") == "Conductor"]))


def test_golive_m7_dst_yesterday():
    """dispatcher-full #7: "yesterday" is the previous CALENDAR day. 00:30 after a spring-forward Sunday (23 h) minus
    86400 s is Saturday; the dependent must still find Sunday's 23:30 parent slot. Real transitions, two zones."""
    old = os.environ.get("TZ")
    try:
        for tz, monday, sunday in (("Europe/Berlin", "2026-03-30", "2026-03-29"),
                                   ("America/New_York", "2026-03-09", "2026-03-08"),
                                   ("Europe/Berlin", "2026-10-26", "2026-10-25")):
            os.environ["TZ"] = tz
            time.tzset()
            now = time.mktime(time.strptime(monday + " 00:31", "%Y-%m-%d %H:%M"))
            got = RL.after_slots({"runs_local": ["23:30"]}, {"slot": "00:30"}, now)
            check(got == [sunday + " 23:30"], "M7 %s %s 00:30 follows %s 23:30 (%r)" % (tz, monday, sunday, got))
            check(RL.day_of(RL.prev_day(now)) == sunday, "M7 %s prev_day(%s) is %s" % (tz, monday, sunday))
    finally:
        if old is None:
            os.environ.pop("TZ", None)
        else:
            os.environ["TZ"] = old
        time.tzset()


def robs_with(ro, status):
    r = dict(ro)
    r["ops"] = lambda: status
    return r


def test_long_helper_alarm():
    """CONDUCTOR_HELPERS_TUNE_TWENTY_MINUTE_WINDOW (owner 2026-10-29): a Conductor helper running more than
    long_helper.alarm_after_s (1 h) raises a long_helper:<id> alarm with a RAISE FIRST line; one at 1 h or under does not."""
    sch = sched(long_helper={"enabled": True, "alarm_after_s": 3600, "item": None})
    st = D.load_state(os.path.join(TMP, "lh1"))
    o = obs()
    o["long_helpers"] = lambda: [{"id": "aaaaaaaaaaaaaaaa", "age_s": 3601.0}, {"id": "bbbbbbbbbbbbbbbb", "age_s": 3600.0},
                                 {"id": "cccccccccccccccc", "age_s": 600.0}]
    a = [x for x in D.decide(sch, st, o, 5000.0, True) if x["do"] == "alarm"]
    check([x["kind"] for x in a] == ["long_helper:aaaaaaaaaaaa"], "long helper: only the one past 1 h alarms (%r)" % a)
    check(a and a[0].get("conductor_log") and a[0].get("note") and a[0]["ticket"] == "DISPATCHER_ALARMS_X",
          "long helper: ledger note on the alarm item and a conductor-log line")
    path = os.path.join(TMP, "lh_log.md")
    D.conductor_log(sched(no_handoff={"conductor_log": path}), dict(a[0]), 5000.0)
    with open(path, encoding="utf-8") as f:
        txt = f.read()
    check("RAISE FIRST: Conductor-window helper aaaaaaaaaaaa has run 60 min" in txt, "long helper: RAISE FIRST line says which (%r)" % txt)
    o["long_helpers"] = lambda: [{"id": "aaaaaaaaaaaaaaaa", "age_s": 3601.0}]
    off = D.decide(sched(long_helper={"enabled": False}), D.load_state(os.path.join(TMP, "lh2")), o, 5000.0, True)
    check(not [x for x in off if str(x.get("kind")).startswith("long_helper")], "long helper: disabled = silent")


def main():
    for t in (test_parse_peek, test_wake_and_owner, test_blind_pause_roles_caps, test_verify_retry,
              test_no_handoff_rering_and_escalation, test_new_ticket_skips_the_backoff, test_alarm_delivery_and_lock, test_answered_ring_is_not_no_handoff, test_dead_recover,
              test_never_adopt_or_resume_a_stranger, test_review_fixes, test_ts_skip_journalled_once, test_doorbell, test_end_to_end, test_dry_run, test_alarm_rate, test_review_s, test_seat_rule, test_ringed_next_withholds_nothing,
              test_role_reading_and_band, test_role_gates, test_role_economy_and_alarms,
              test_role_real_schedule_caps_and_ops_bands, test_role_execute_and_dry, test_review_q,
              test_review_r, test_account_pick_rule, test_account_pick_dispatch,
              test_role_weekday_slots, test_role_done_claims_gate, test_role_pending_work_gate,
              test_role_arbiter_cutoff, test_role_plan_failure_events, test_role_event_skip_keeps_quota, test_role_event_cap_refusal_keeps_quota, test_role_review_r5,
              test_role_event_key_same_second_twins,
              test_role_review_night_r3,
              test_role_ledger_unmeasured, test_role_real_schedule_triggers, test_review_t,
              test_account_hold_dispatch, test_review_u_notes,
              test_review_u_lent_unmeasured, test_review_u_group4, test_review_v, test_review_w_alarm_rearm, test_review_x_alarm_flap,
              test_golive_b1_busy_until_ended, test_golive_b2_blind_fixed_outcomes,
              test_golive_b3_wave1_config, test_golive_trial_set_from_schedule, test_golive_m4_disabled_parent_holds,
              test_golive_m5_malformed_obs, test_golive_m8_ring_withdraw_and_pause,
              test_golive_m6_weekday_slot_keys, test_long_helper_alarm, test_golive_m7_dst_yesterday, test_review_night_n1):
        try:
            t()
        except Exception as e:  # noqa: BLE001
            import traceback
            traceback.print_exc()
            check(False, "%s crashed: %s" % (t.__name__, e))
    # Re-list the failures last: run_selftests keeps only the last 40 lines of a FAIL, and the
    # failing check is otherwise scrolled out of that tail (DISPATCHER_HUNT_SELFTEST_PARALLEL_FLAKE).
    for msg in FAILS:
        print("FAILED: " + msg)
    print("%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
