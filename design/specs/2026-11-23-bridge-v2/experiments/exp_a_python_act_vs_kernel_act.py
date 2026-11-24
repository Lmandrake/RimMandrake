#!/usr/bin/env python3
"""Experiment A of 08_where_tests_live.md: one scene, two homes for its act, and a pause-only control.

The scene: a colonist of a quicktest map is cut once, ACT ticks after the start; the run ends END ticks after the start.

  arm K (act inside the game)   one call. jawa/scene_slice does the cut itself in its end-of-tick step (actAt=ACT).
  arm P (act from Python)       jawa/scene_slice with no act runs until tick start+ACT and pauses; Python calls jawa/damage
                                while the game is paused; jawa/scene_slice runs again until tick start+END.
  arm KP (pause only)           the cut is done inside the game as in arm K, the run pauses one tick later, the game stands
                                paused for --dwell seconds with no call from Python, then it runs on. K against KP shows what
                                a pause alone changes; KP against P shows what the Python act adds (GPT's control arm).

It measures, per trial: the tick on which the cut landed, the tick on which the trace first shows the new injury, the tick
of the end, the wall time, the bridge calls, and (arm P) the wall time that the game stood paused for the act.
The question it decides: does an act from Python on a paused game land on the same TICK as an act inside the game's tick?
It does NOT decide whether the game's state is then the same: three tick offsets of one injury cannot see a cache, a power
net or a mod's frame work that differs. Scene 3 of 08 (a FlowWorks read on the tick after the act) is owed for that.

    python.exe exp_a_python_act_vs_kernel_act.py --trials 10 --out DIR     live: a TEST-profile game, a small mod list, a
                                                                           scratch quicktest map (it hurts one colonist)
    python3 exp_a_python_act_vs_kernel_act.py --selfcheck                  the comparison on hand-made traces; no game

Exit 0 = the three arms agree on every tick offset in every trial, 1 = they differ, 2 = could not measure.
The live part is UNRUN (2026-11-23): every game was held. It needs no code that is not landed (slice 5cebf3567fe1)."""
import argparse
import json
import os
import statistics
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "bridgetools"))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils"))

ACT, END = 60, 200
INJ = "inj"


# ------------------------------------------------------------------------------------------------ the comparison (pure)
def whole(trace):
    """True when the trace has its close, no dropped row and no gap; None-safe."""
    cl = [r for r in trace if r.get("rec") == "close"]
    if not cl:
        return False
    c = cl[-1]
    ns = [r["n"] for r in trace if "n" in r]
    return bool(c.get("drained")) and not c.get("dropped") and ns == list(range(1, len(ns) + 1))


def offsets(start, act_tick, traces):
    """-> dict of tick offsets from the start, or None when a trace cannot be read (could not look, never a number).

    act: the tick on which the cut was done. seen: the first tick whose end-of-tick sample shows more injuries than the
    first sample. end: the tick of the end record of the last segment."""
    if not traces or not all(whole(t) for t in traces) or act_tick is None:
        return None
    first = None
    seen = None
    for t in traces:
        for r in t:
            if r.get("rec") == "track" and r.get("name") == INJ and r.get("st") == "ok":
                if first is None:
                    first = r["v"]
                elif seen is None and r["v"] > first:
                    seen = r["tick"]
    ends = [r for r in traces[-1] if r.get("rec") == "end"]
    if first is None or not ends:
        return None
    return {"act": act_tick - start, "seen": None if seen is None else seen - start, "end": ends[-1].get("hitTick", -1) - start,
            "endState": ends[-1].get("state")}


def compare(k, p):
    """-> (True same | False differ | None could not compare, text). k and p are offsets() results."""
    if k is None or p is None:
        return None, "could not look: K=%s P=%s" % (k, p)
    diff = [f for f in ("act", "seen", "end", "endState") if k[f] != p[f]]
    if k["seen"] is None and p["seen"] is None:
        return None, "neither arm shows the injury: the scene did not expose the act"
    return (not diff), ("same offsets %s" % k if not diff else "differ in %s: K=%s P=%s" % (diff, k, p))


def _made(start, act, seen, end, lost=False, segs=1):
    out = []
    cut = [start + ACT] if segs == 2 else []
    lo = start
    for i, hi in enumerate(cut + [end]):
        t, n = [], [0]

        def add(tick, rec, **kw):
            n[0] += 1
            t.append(dict({"n": n[0], "tick": tick, "rec": rec}, **kw))
        add(lo, "open")
        add(lo, "track", name=INJ, st="ok", v=1 if (seen is None or lo < seen) else 2)
        if seen is not None and lo < seen <= hi:
            add(seen, "track", name=INJ, st="ok", v=2)
        add(hi, "end", state="hit", hitTick=hi)
        add(hi, "close", drained=True, dropped=1 if lost else 0)
        out.append(t)
        lo = hi
    return offsets(start, act, out)


def selfcheck():
    good = _made(1000, 1060, 1061, 1200)
    cases = [
        ("same, K one segment and P two", compare(good, _made(5000, 5060, 5061, 5200, segs=2))[0], True),
        ("P act one tick late", compare(good, _made(5000, 5061, 5062, 5200, segs=2))[0], False),
        ("P injury seen one tick later", compare(good, _made(5000, 5060, 5062, 5200, segs=2))[0], False),
        ("P end one tick late", compare(good, _made(5000, 5060, 5061, 5201, segs=2))[0], False),
        ("a dropped row is could not look", compare(good, _made(5000, 5060, 5061, 5200, lost=True, segs=2))[0], None),
        ("no trace is could not look", compare(good, offsets(5000, 5060, []))[0], None),
        ("no act tick is could not look", compare(good, offsets(5000, None, [[{"n": 1, "rec": "close", "drained": True}]]))[0], None),
        ("neither arm exposed the act", compare(_made(1000, 1060, None, 1200), _made(5000, 5060, None, 5200, segs=2))[0], None),
        ("K exposed, P did not", compare(good, _made(5000, 5060, None, 5200, segs=2))[0], False),
    ]
    bad = [c for c in cases if c[1] is not c[2]]
    for name, got, want in cases:
        print("%s %s -> %s" % ("ok  " if got is want else "FAIL", name, got))
    print("exp_a comparison: %d of %d" % (len(cases) - len(bad), len(cases)))
    return 1 if bad else 0


# ------------------------------------------------------------------------------------------------- the game
def live(a):
    import prove_scene_tick_wiring as W
    calls = [0]

    def call(tool, **p):
        calls[0] += 1
        return W.call(tool, **p)
    W.connect()
    call("rimworld/start_debug_game_ready", timeoutMs=280000, readiness="mapData", pauseIfNeeded=True)
    for _ in range(240):
        if call("rimworld/get_ui_state").get("programState") == "Playing":
            break
        time.sleep(1)
    else:
        print("UNMEASURED: no quicktest map reached Playing")
        return 2
    time.sleep(3)
    pl = [p for p in call("jawa/pawn_get", limit=200).get("pawns") or [] if p.get("faction") == "PlayerColony" and p.get("kindDef") == "Colonist"]
    if not pl:
        print("UNMEASURED: no colonist on the quicktest map")
        return 2
    pid = pl[0]["thingId"]
    tracks = json.dumps({INJ: {"p": "thing.field", "thing": pid, "path": "health.hediffSet.hediffs._size"}})
    tick = {"p": "game.tick"}

    def seg(until_tick, limit, act_at=0):
        st, tr = W.run(pawn=pid, speed=a.speed, maxTicks=limit, actAt=act_at, damage=4.0, tracks=tracks,
                       until=json.dumps({"cmp": [tick, ">=", until_tick]}))
        calls[0] += 2          # the start and at least one status read; W.run polls every 0.3 s
        return st, tr

    rows, verdicts = [], []
    os.makedirs(a.out, exist_ok=True)
    for i in range(a.trials):
        # arm K
        calls[0] = 0
        t0 = call("jawa/map_info").get("ticksGame")
        w = time.time()
        st, tr = seg(t0 + END, END + 50, act_at=ACT)
        k_wall, k_calls = time.time() - w, calls[0]
        acts = [r for r in tr if r.get("rec") == "act"]
        k = offsets(t0, acts[0]["tick"] if acts else None, [tr])
        # arm P
        calls[0] = 0
        t1 = call("jawa/map_info").get("ticksGame")
        w = time.time()
        st1, tr1 = seg(t1 + ACT, ACT + 50)
        g = time.time()
        at = call("jawa/map_info").get("ticksGame")
        d = call("jawa/damage", damageDef="Cut", amount=4.0, thingId=pid, armorPenetration=1.0, bodyPart="Torso", allowColonists=True)
        after = call("jawa/map_info").get("ticksGame")
        gap = time.time() - g
        st2, tr2 = seg(t1 + END, END - ACT + 50)
        p_wall, p_calls = time.time() - w, calls[0]
        p = offsets(t1, at if (d.get("success") and at == after) else None, [tr1, tr2] if tr1 and tr2 else [])
        # arm KP: the cut inside the game, then a pause with no call, then on
        t2 = call("jawa/map_info").get("ticksGame")
        st3, tr3 = seg(t2 + ACT + 1, ACT + 50, act_at=ACT)
        time.sleep(a.dwell)
        moved = call("jawa/map_info").get("ticksGame") != t2 + ACT + 1
        st4, tr4 = seg(t2 + END, END - ACT + 50)
        acts = [r for r in tr3 if r.get("rec") == "act"]
        kp = offsets(t2, acts[0]["tick"] if (acts and not moved) else None, [tr3, tr4] if tr3 and tr4 else [])
        v, text = compare(k, p)
        v2, text2 = compare(k, kp)
        v = None if (v is None or v2 is None) else (v and v2)
        verdicts.append(v)
        rows.append({"trial": i, "K": k, "P": p, "KP": kp, "same": v, "text": text, "pause_only_text": text2,
                     "K_wall_s": round(k_wall, 3), "P_wall_s": round(p_wall, 3),
                     "K_calls": k_calls, "P_calls": p_calls, "P_paused_for_act_s": round(gap, 3), "clock_moved_in_gap": at != after,
                     "clock_moved_in_dwell": moved})
        print("trial %d  %s  K %.2f s %d calls  P %.2f s %d calls  paused for the act %.0f ms  K:P %s | K:KP %s"
              % (i, {True: "SAME", False: "DIFFER", None: "COULD NOT LOOK"}[v], k_wall, k_calls, p_wall, p_calls, gap * 1000, text, text2), flush=True)
    with open(os.path.join(a.out, "exp_a_rows.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=1)
    ok = [r for r in rows if r["same"] is not None]
    if ok:
        print("wall time median: K %.2f s, P %.2f s; the act cost Python %.0f ms of paused game (median)"
              % (statistics.median(r["K_wall_s"] for r in ok), statistics.median(r["P_wall_s"] for r in ok),
                 1000 * statistics.median(r["P_paused_for_act_s"] for r in ok)))
    n = dict((x, sum(1 for v in verdicts if v is x)) for x in (True, False, None))
    print("exp_a live: %d SAME, %d DIFFER, %d COULD NOT LOOK of %d trials" % (n[True], n[False], n[None], len(verdicts)))
    return 1 if n[False] else (2 if n[None] or not verdicts else 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selfcheck", action="store_true")
    ap.add_argument("--trials", type=int, default=10)
    ap.add_argument("--speed", default="Normal")
    ap.add_argument("--dwell", type=float, default=0.25, help="arm KP: seconds the game stands paused")
    ap.add_argument("--out", default=".")
    a = ap.parse_args()
    return selfcheck() if a.selfcheck else live(a)


if __name__ == "__main__":
    sys.exit(main())
