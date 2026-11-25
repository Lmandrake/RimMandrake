#!/usr/bin/env python3
"""Live proof of the life cycle of a run (BRIDGE v2.0): a killed driver, the run lock, the two step loops. Page:
design/specs/2026-11-23-bridge-v2-life-cycle/boundary.md. Item RIMMANDRAKE_HARDEN_RUN_LIFE_CYCLE_KILL_CANCEL_THROWN_TICK.

    python.exe prove_run_life_cycle.py [--out DIR]   on a TEST-profile game, a scratch map (it makes its own quicktest map, and spawns
                                                     and leaves one animal there; no save is read or written). Row 3 needs the
                                                     PROOF build of Explosive Knockback for jawa/run_scenes, on the
                                                     explosiveknockback_visit tier: its scenes stage LWM Deep Storage lockers
    python3 prove_run_life_cycle.py --selfcheck      the judges on hand-made readings, good and planted; no game

Three rows:
  1 a driver killed in the middle of its run leaves a closing record and a paused game, and its session is taken and ended
  2 jawa/spawn_pawn from a second caller during a run is refused by the run's id, spawns nothing and is a breach on the receipt; a read
    is let through; the same tool as an act of the run works
  3 jawa/safe_advance and jawa/run_scenes stop on the exact tick of their condition
The item's fourth row (a thing spawned and destroyed inside one tick) needs the taps of
RIMMANDRAKE_BUILD_WORLD_EVENT_TAPS_SECOND_FAMILY, and belongs to that item.
Exit 0 = every row PASS, 1 = a FAIL, 2 = UNMEASURED."""
import argparse
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "Utils"))
sys.path.insert(0, HERE)
import prove_run_until as R  # noqa: E402  the session, run, tick and trace helpers
import prove_scene_tick_wiring as W  # noqa: E402  the connection, call() and row()

SUITE = "RimMandrake.ExplosiveKnockback.RM_KnockbackScenes"
LEASE_S = 4


# ------------------------------------------------------------------------------------------------ the judges (pure)
def closed_trace(rows, state):
    """None when the records of one run hold one end of this state and a drained close with the game paused, else what is wrong."""
    e, c = R.recs(rows, "end"), R.recs(rows, "close")
    if len(e) != 1 or len(c) != 1:
        return "%d end, %d close records" % (len(e), len(c))
    if e[0].get("state") != state:
        return "the end says %s" % e[0].get("state")
    if c[0].get("paused") is not True or c[0].get("drained") is not True or c[0].get("dropped"):
        return "close: paused %s drained %s dropped %s" % (c[0].get("paused"), c[0].get("drained"), c[0].get("dropped"))
    return None


def judge_killed(before, after, t1, t2, rows, taken, ended):
    """before: the session state while the child lived. after: past the lease. t1, t2: two reads of the tick, a second apart."""
    if before.get("stage") != "open" or before.get("paused") is not False:
        return None, "the child's run was not playing: stage %s, paused %s" % (before.get("stage"), before.get("paused"))
    why = closed_trace(rows, "cancelled")
    ok = (after.get("leaseEnded") is True and after.get("paused") is True and t1 is not None and t1 == t2 and why is None
          and taken.get("success") is True and taken.get("taken") is True and ended.get("stage") == "aborted")
    return ok, "lease ended %s, paused %s, tick %s then %s; trace %s; taken %s; session %s" % (
        after.get("leaseEnded"), after.get("paused"), t1, t2, why or "closed", taken.get("taken"), ended.get("stage"))


def judge_lock(live, no, n_before, n_after, read, rep, rows, n_end):
    """live: the run was running at the call. no: the refusal. n_*: the animals of that kind before, after the refusal, at the end."""
    if not live or rep.get("why") != "hit" or None in (n_before, n_after, n_end):
        return None, "run live %s, ended %s; counts %s %s %s" % (live, rep.get("why"), n_before, n_after, n_end)
    txt = json.dumps(no)
    c = (R.recs(rows, "close") or [{}])[0]
    ok = (no.get("success") is False and "RUN_ACTIVE" in txt and str(rep.get("run")) in txt and n_after == n_before and read is True
          and (rep.get("breaches") or {}).get("jawa/spawn_pawn") == 1 and (c.get("breaches") or {}).get("jawa/spawn_pawn") == 1
          and (c.get("lockReads") or 0) >= 1 and n_end == n_before + 1)
    return ok, "refusal: %s | animals %s, after it %s, after the run's own act %s; read let through %s; close breaches %s reads %s" % (
        txt[:160], n_before, n_after, n_end, read, c.get("breaches"), c.get("lockReads"))


def judge_advance(t0, n, r, t1, t2):
    sc = r.get("scene") or {}
    if not r or r.get("_error") or "state" not in r:
        return None, "jawa/safe_advance: %s" % str(r)[:200]
    ok = r.get("state") == "hit" and r.get("executed") == n and r.get("tickTo") == t0 + n and t1 == t0 + n and t2 == t1 and sc.get("stage") == "closed"
    return ok, "asked +%d: %s, executed %s, tickTo +%s, read +%s then +%s, run %s" % (
        n, r.get("state"), r.get("executed"), (r.get("tickTo") or 0) - t0, (t1 or 0) - t0, (t2 or 0) - t0, sc.get("stage"))


def judge_scenes(t0, n, r, t1):
    sc = (r.get("scenes") or [{}])[0]
    if r.get("success") is not True or "untilRun" not in sc:
        return None, "jawa/run_scenes: %s" % str(r.get("message") or r.get("rows") or r)[:200]
    ok = sc.get("untilState") == "hit" and sc.get("ticksStepped") == n and t1 == t0 + n
    return ok, "asked +%d: %s, stepped %s, hit +%s, read +%s" % (n, sc.get("untilState"), sc.get("ticksStepped"), (sc.get("untilHitTick") or 0) - t0, (t1 or 0) - t0)


def selfcheck():
    end, close = {"rec": "end", "state": "cancelled"}, {"rec": "close", "paused": True, "drained": True, "dropped": 0}
    B, A = {"stage": "open", "paused": False}, {"leaseEnded": True, "paused": True}
    T, E = {"success": True, "taken": True}, {"stage": "aborted"}
    no = {"success": False, "message": "REFUSED: RUN_ACTIVE. Run S1_r1 is live"}
    rep = {"why": "hit", "run": "S1_r1", "breaches": {"jawa/spawn_pawn": 1}}
    lc = [dict(close, breaches={"jawa/spawn_pawn": 1}, lockReads=1)]
    adv = {"state": "hit", "executed": 137, "tickTo": 237, "scene": {"stage": "closed"}}
    scn = {"success": True, "scenes": [{"untilRun": "s1", "untilState": "hit", "ticksStepped": 90, "untilHitTick": 190}]}
    cases = [
        ("killed good", judge_killed(B, A, 5, 5, [end, close], T, E)[0], True),
        ("killed, no close", judge_killed(B, A, 5, 5, [end], T, E)[0], False),
        ("killed, the game goes on", judge_killed(B, A, 5, 9, [end, close], T, E)[0], False),
        ("killed, not paused", judge_killed(B, dict(A, paused=False), 5, 5, [end, close], T, E)[0], False),
        ("killed, the run ended as a hit", judge_killed(B, A, 5, 5, [dict(end, state="hit"), close], T, E)[0], False),
        ("killed, not taken", judge_killed(B, A, 5, 5, [end, close], {"success": False}, E)[0], False),
        ("killed, it never played", judge_killed(dict(B, paused=True), A, 5, 5, [end, close], T, E)[0], None),
        ("lock good", judge_lock(True, no, 2, 2, True, rep, lc, 3)[0], True),
        ("lock, the call spawned", judge_lock(True, no, 2, 3, True, rep, lc, 4)[0], False),
        ("lock, let through", judge_lock(True, {"success": True}, 2, 2, True, rep, lc, 3)[0], False),
        ("lock, no run id", judge_lock(True, dict(no, message="RUN_ACTIVE"), 2, 2, True, rep, lc, 3)[0], False),
        ("lock, no breach on the close", judge_lock(True, no, 2, 2, True, rep, [dict(close, breaches={}, lockReads=1)], 3)[0], False),
        ("lock, a read refused", judge_lock(True, no, 2, 2, False, rep, lc, 3)[0], False),
        ("lock, its own act refused", judge_lock(True, no, 2, 2, True, rep, lc, 2)[0], False),
        ("lock, the run was over", judge_lock(False, no, 2, 2, True, rep, lc, 3)[0], None),
        ("advance good", judge_advance(100, 137, adv, 237, 237)[0], True),
        ("advance one late", judge_advance(100, 137, dict(adv, executed=138, tickTo=238), 238, 238)[0], False),
        ("advance to the end of its chunk", judge_advance(100, 137, adv, 280, 280)[0], False),
        ("advance not answered", judge_advance(100, 137, {"_error": "x"}, 237, 237)[0], None),
        ("scenes good", judge_scenes(100, 90, scn, 190)[0], True),
        ("scenes ran on", judge_scenes(100, 90, scn, 191)[0], False),
        ("scenes, no suite", judge_scenes(100, 90, {"success": False, "message": "Type not found"}, 190)[0], None),
    ]
    bad = [n for n, got, want in cases if got is not want]
    for n, got, want in cases:
        print("%s %s -> %s" % ("ok  " if got is want else "FAIL", n, got))
    print("prove_run_life_cycle judges: %d of %d" % (len(cases) - len(bad), len(cases)))
    return 1 if bad else 0


# ------------------------------------------------------------------------------------------------- the game
def child(request):
    """The driver that will be killed: a session, a long run, then no more calls."""
    W.connect()
    R.DRIVER = "prove-child:%d" % os.getpid()
    W.call("jawa/session", action="open", driver=R.DRIVER, leaseS=LEASE_S)
    r = W.call("jawa/run_until", action="start", driver=R.DRIVER, request=request, until=json.dumps(R.at_tick(10 ** 9)), limit=500000, speed="Normal")
    print(json.dumps({"driver": R.DRIVER, "run": r.get("run"), "stage": r.get("stage"), "no": r.get("message")}), flush=True)
    time.sleep(600)


def animals(kind):
    r = W.call("jawa/list_pawns")
    l = r.get("pawns")
    return None if not isinstance(l, list) else sum(1 for p in l if kind.lower() in json.dumps(p).lower())


def second_caller(tool, **p):
    """The same call from another connection."""
    mine = W.S[0]
    try:
        W.connect()
        return W.call(tool, **p)
    finally:
        W.S[0] = mine


def run_rows(st, run, limit_s=15):
    """The records of one run, in seq order, once its close is on disk."""
    return W.read_trace({"recordDir": st.get("recordDir"), "session": st.get("writerSession") or st.get("session"), "run": run}, limit_s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=".")
    ap.add_argument("--selfcheck", action="store_true")
    ap.add_argument("--child")
    a = ap.parse_args()
    if a.selfcheck:
        return selfcheck()
    if a.child:
        return child(a.child)
    os.makedirs(a.out, exist_ok=True)
    W.connect()
    if not R.start_map():
        return 2
    R.open_session()                                    # a session that an earlier run left is out of the way first
    R.end_session("abort")
    keep = {}

    # 1. the driver is killed
    p = subprocess.Popen([sys.executable, os.path.abspath(__file__), "--child", "kill_me"], stdout=subprocess.PIPE, text=True)
    said = json.loads(p.stdout.readline() or "{}")
    time.sleep(1.5)
    before = W.call("jawa/session", action="state")
    p.kill()
    p.wait()
    time.sleep(LEASE_S + 3)
    after = W.call("jawa/session", action="state")
    t1 = after.get("ticksGame")
    time.sleep(1)
    t2 = R.tick()
    rows = run_rows(after, said.get("run")) if said.get("run") else []
    taken = W.call("jawa/session", **{"action": "take", "driver": R.DRIVER, "from": said.get("driver")})
    ended = R.end_session("abort")
    keep["killed"] = {"said": said, "before": before, "after": after, "rows": rows, "taken": taken, "ended": ended}
    W.row("1 a killed driver", *judge_killed(before, after, t1, t2, rows, taken, ended))

    # 2. the run lock
    kind = "Muffalo"
    W.call("jawa/session", action="open", driver=R.DRIVER, leaseS=60)
    pl = [x for x in W.call("jawa/pawn_get", limit=200).get("pawns") or [] if x.get("faction") == "PlayerColony"]
    pos = (pl[0].get("position") if pl else None) or {}
    x, z = (pl[0].get("x", pos.get("x")), pl[0].get("z", pos.get("z"))) if pl else (None, None)
    n0, rid = animals(kind), R.req("lock")
    spawn = {"kindDef": kind, "x": x, "z": z, "faction": "none"}
    r = W.call("jawa/run_until", action="start", driver=R.DRIVER, request=rid, until=json.dumps(R.at_tick((R.tick() or 0) + 400)), limit=900, speed="Normal",
               acts=json.dumps([{"id": R.req("own"), "tool": "jawa/spawn_pawn", "args": spawn, "at": 300}]))
    time.sleep(0.5)
    live = W.call("jawa/run_until", action="status", driver=R.DRIVER, request=rid).get("stage") == "running"
    no = second_caller("jawa/spawn_pawn", **spawn)
    n1 = animals(kind)
    read = W.call("jawa/map_info").get("success") is not False and n1 is not None
    end = time.time() + 120
    while r.get("success") and r.get("stage") != "closed" and time.time() < end:
        time.sleep(0.2)
        r = W.call("jawa/run_until", action="status", driver=R.DRIVER, request=rid)
    n2 = animals(kind)
    st = W.call("jawa/session", action="state")
    rows = run_rows(st, r.get("run")) if r.get("run") else []
    keep["lock"] = {"refusal": no, "reply": r, "rows": rows, "counts": [n0, n1, n2]}
    W.row("2 the run lock", *judge_lock(live, no, n0, n1, read, r, rows, n2))
    R.end_session("close")

    # 3. the step loops
    t0 = R.tick()
    adv = W.call("jawa/safe_advance", ticks=600, stopOn="colony_loss", until=json.dumps(R.at_tick(t0 + 137)))
    if adv.get("success") is False and "state" not in adv:
        adv = W.call("jawa/safe_advance", ticks=600, until=json.dumps(R.at_tick(t0 + 137)))
    t1 = R.tick()
    time.sleep(1)
    v1, d1 = judge_advance(t0, 137, adv, t1, R.tick())
    t0 = R.tick()
    scn = W.call("jawa/run_scenes", type=SUITE, scenes="storeroom_bomb_pit", until=json.dumps(R.at_tick(t0 + 90)))
    v2, d2 = judge_scenes(t0, 90, scn, R.tick())
    keep["step"] = {"advance": adv, "scenes": scn}
    W.row("3 the step loops stop on the tick", None if v1 is None or (v1 and v2 is None) else v1 and v2, "safe_advance %s: %s | run_scenes %s: %s" % (v1, d1, v2, d2))
    keep["hooks"] = W.call("jawa/harmony_patches", typeName="Verse.TickManager")
    with open(os.path.join(a.out, "run_life_cycle.json"), "w", encoding="utf-8") as f:
        json.dump(keep, f, indent=1, default=str)
    words = [w for _n, w in W.ROWS]
    print("prove_run_life_cycle: %d of %d rows PASS" % (words.count("PASS"), len(words)), flush=True)
    return 1 if "FAIL" in words else (2 if "UNMEASURED" in words or len(words) != 3 else 0)


if __name__ == "__main__":
    sys.exit(main())
