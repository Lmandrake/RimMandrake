#!/usr/bin/env python3
"""Experiment A, the part that exp_a_python_act_vs_kernel_act.py cannot decide: is the STATE after the act the same?

--scene replay   vanilla state. One save, loaded before every run, the random seed set to one number, then 200 ticks with the
                 cut at +60 in one of four arms: K (act inside the tick), KP (K, then a bare pause), P (act from Python on the
                 paused game), P1 (PLANTED: P one tick late). Tracks of every colonist (cell, job, injuries, hunger, rest) are
                 compared tick by tick with the first K run. The K-against-K runs are the noise floor: a difference counts only
                 when it is larger than what K shows against itself.
--scene pocket   FlowWorks state. A person of no faction stands stunned on flat ground; its own cell is dug, 20 ticks after an
                 earlier dig 4 cells away. Arms: R (the dig call lands on the RUNNING game, between two frames, as a game-side write does:
                 no paused frame sees it), RP (R, then a bare pause of --dwell s one or more ticks later), P (the dig call on
                 the paused game), G (act and go: the dig is an act at 0 of jawa/run_until, done in the hop that starts the clock), T (the
                 dig is an act on a tick inside one jawa/run_until); G and T: --arms R,P,RP,G,T. Read 10 and 100 ticks after the dig:
                 is the person held (RM_NorthstarProofs.ProofTrap), and on which tick the pocket grid was rebuilt (ProofEdge).
                 --quiet makes the earlier dig 200 ticks older, so that the 60-tick throttle has run out: the predicted SAME
                 case, and the control that the reads are not simply blind.
--scene blast    FlowWorks, an act really inside the tick: the slice's own cut kills a boomalope beside a damaged pit ramp, and its
                 blast destroys the ramp on the next tick; against the same kill from Python on the paused game.
--selfcheck      the comparison on hand-made series; no game.

The slice (jawa/scene_slice) can only do a cut inside the tick. Arms G and T do a DIG inside the hop and inside the tick, by
jawa/run_until; R was the stand-in for them. The blast scene shows that a write made inside a tick is throttled as R's is.
Run as exp_a_python_act_vs_kernel_act.py. Exit 0 all agree, 1 differ, 2 could not measure."""
import argparse
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exp_a_python_act_vs_kernel_act as A  # noqa: E402

ACT, END = A.ACT, A.END
SAVE, SEED = "exp_a_fixture", 20261123


# ------------------------------------------------------------------------------------------------ pure
def series(start, traces, upto=END):
    """-> {track: [value at the END of tick start+1 .. start+upto]} or None when a trace is not whole."""
    if not traces or not all(A.whole(t) for t in traces):
        return None
    out = {}
    for t in traces:
        lo = t[0]["tick"]
        for r in t:
            if r.get("rec") == "track" and r.get("phase") != "last":
                first = lo + 1 if r.get("phase") == "first" else r["tick"]
                s = out.setdefault(r["name"], [None] * upto)
                for k in range(max(first - start - 1, 0), upto):
                    s[k] = (r.get("st"), r.get("v"))
    return out


def first_split(a, b):
    """-> (tick offset of the first difference or None, the tracks that differ anywhere), or ("unread", []) ."""
    if a is None or b is None or set(a) != set(b):
        return "unread", []
    at = [(next(i for i, (x, y) in enumerate(zip(a[n], b[n])) if x != y) + 1, n) for n in a if a[n] != b[n]]
    return (min(at)[0] if at else None), sorted(n for _i, n in at)


def pair_summary(rows):
    """Every pair of runs, K against each arm: how many pairs split before the act, on the first tick after it, later, never."""
    by = {}
    for r in rows:
        by.setdefault("K" if r["arm"] in ("K", "K0") else r["arm"], []).append(r["series"])
    out = {}
    for arm, ss in by.items():
        n = {"pairs": 0, "before_act": 0, "at_act": 0, "later": 0, "never": 0, "unread": 0}
        for i, k in enumerate(by.get("K", [])):
            for j, s in enumerate(ss):
                if arm == "K" and j <= i:
                    continue
                at, _names = first_split(k, s)
                n["pairs"] += 1
                n["unread" if at == "unread" else "never" if at is None else "before_act" if at <= ACT else "at_act" if at <= ACT + 2 else "later"] += 1
        out["K:" + arm] = n
    return out


def selfcheck():
    def mk(start, inj_at, segs=1, x=5):
        t = [{"n": 1, "tick": start, "rec": "open"}, {"n": 2, "tick": start, "rec": "track", "phase": "first", "name": "i", "st": "ok", "v": 0},
             {"n": 3, "tick": start, "rec": "track", "phase": "first", "name": "x", "st": "ok", "v": x}]
        if segs == 1:
            return [t + [{"n": 4, "tick": inj_at, "rec": "track", "phase": "end_of_tick", "name": "i", "st": "ok", "v": 1},
                         {"n": 5, "tick": start + END, "rec": "close", "drained": True}]]
        cut = inj_at - 1
        u = [{"n": 1, "tick": cut, "rec": "open"}, {"n": 2, "tick": cut, "rec": "track", "phase": "first", "name": "i", "st": "ok", "v": 1},
             {"n": 3, "tick": cut, "rec": "track", "phase": "first", "name": "x", "st": "ok", "v": x}, {"n": 4, "tick": start + END, "rec": "close", "drained": True}]
        return [t + [{"n": 4, "tick": cut, "rec": "track", "phase": "last", "name": "i", "st": "ok", "v": 0}, {"n": 5, "tick": cut, "rec": "close", "drained": True}], u]
    def arm(n, first, late):
        return {"runs": n, "void": 0, "heldAtFirstRead": first, "heldAt100": late}
    k = series(100, mk(100, 161))
    cases = [("same over a split run", first_split(k, series(900, mk(900, 961, 2))), (None, [])),
             ("one tick late", first_split(k, series(900, mk(900, 962, 2))), (61, ["i"])),
             ("another track", first_split(k, series(900, mk(900, 961, 2, x=6))), (1, ["x"])),
             ("a hand that reads as running play", pocket_verdict({"P": arm(3, 3, 3), "G": arm(3, 0, 3), "T": arm(3, 0, 3)}), 0),
             ("a hand that a paused frame saw", pocket_verdict({"P": arm(3, 3, 3), "G": arm(3, 1, 3)}), 1),
             ("a blind reading", pocket_verdict({"P": arm(3, 0, 0), "G": arm(3, 0, 0)}), 2),
             ("no hand's arm", pocket_verdict({"P": arm(3, 3, 3)}), 0),
             ("not whole is unread", first_split(k, series(900, [mk(900, 961)[0][:-1]])), ("unread", []))]
    bad = [c for c in cases if c[1] != c[2]]
    for c in cases:
        print("%s %s -> %s" % ("FAIL" if c in bad else "ok  ", c[0], c[1]))
    print("state after act: %d of %d" % (len(cases) - len(bad), len(cases)))
    return 1 if bad else 0


# ------------------------------------------------------------------------------------------------ the game
def ready(W):
    """Playing with the same readable tick on 3 reads: right after load_game_ready the old map still answers for a moment."""
    time.sleep(1)
    same, last, end = 0, None, time.time() + 240
    while time.time() < end:
        t = tick(W) if W.call("rimworld/get_ui_state").get("programState") == "Playing" else None
        same = same + 1 if (t is not None and t == last) else 0
        last = t
        if same >= 3:
            return True
        time.sleep(0.4)
    return False


def tick(W):
    return W.call("jawa/map_info").get("ticksGame")


def seg(W, pid, until, limit, speed, tracks=None, act_at=0):
    return W.run(pawn=pid, speed=speed, maxTicks=limit, actAt=act_at, damage=4.0, tracks=json.dumps(tracks or {}),
                 until=json.dumps({"cmp": [{"p": "game.tick"}, ">=", until]}))


def colonists(W):
    return [p["thingId"] for p in W.call("jawa/pawn_get", limit=200).get("pawns") or [] if p.get("faction") == "PlayerColony" and p.get("kindDef") == "Colonist"]


def replay(W, a):
    r = W.call("rimworld/save_game", saveName=SAVE)
    if not r.get("success"):
        print("UNMEASURED: no fixture save: %s" % r)
        return 2
    pids = sorted(colonists(W))
    pid = pids[0]
    tracks = {}
    for p in pids:
        for nm, path in (("x", "positionInt.x"), ("z", "positionInt.z"), ("inj", "health.hediffSet.hediffs._size"), ("food", "needs.food.curLevelInt"), ("rest", "needs.rest.curLevelInt")):
            tracks["%s_%s" % (p, nm)] = {"p": "thing.field", "thing": p, "path": path}
        tracks[p + "_job"] = {"p": "pawn.job", "pawn": p, "f": "def"}
    rows, ref = [], None
    order = ["K"] + [x for _ in range(a.trials) for x in ("K", "P", "KP")] + ["P1"] * min(3, a.trials)
    for i, arm in enumerate(order):
        if not W.call("rimworld/load_game_ready", saveName=SAVE, readiness="mapData", pauseIfNeeded=True, timeoutMs=280000).get("success") or not ready(W):
            print("UNMEASURED: the fixture did not load")
            return 2
        if not W.call("jawa/static_call", type="Verse.Rand", method="set_Seed", args=str(SEED)).get("success"):
            print("UNMEASURED: the seed was not set")
            return 2
        t0 = tick(W)
        w = time.time()
        if arm == "K":
            st, tr = seg(W, pid, t0 + END, END + 50, a.speed, tracks, ACT)
            trs = [tr]
        else:
            late = 1 if arm == "P1" else 0
            kp = arm == "KP"
            st, t1 = seg(W, pid, t0 + ACT + (1 if kp else late), ACT + 50, a.speed, tracks, ACT if kp else 0)
            if kp:
                time.sleep(a.dwell)
            else:
                d = W.call("jawa/damage", damageDef="Cut", amount=4.0, thingId=pid, armorPenetration=1.0, bodyPart="Torso", allowColonists=True)
                if not d.get("success"):
                    t1 = []
            st, t2 = seg(W, pid, t0 + END, END - ACT + 50, a.speed, tracks)
            trs = [t1, t2] if t1 and t2 else []
        s = series(t0, trs) if trs else None
        if ref is None:
            ref = s
            rows.append({"arm": "K0", "t0": t0, "series": s})
            print("reference K read: %s, %d tracks" % (s is not None, len(s or {})), flush=True)
            continue
        at, names = first_split(ref, s)
        inj = None if s is None else s[pid + "_inj"][-1]
        rows.append({"arm": arm, "first_split": at, "tracks": names, "end_inj": inj, "wall_s": round(time.time() - w, 2), "maxFrameTicks": st.get("maxFrameTicks"), "series": s})
        print("%2d %-2s against K0: first difference at +%s in %s; injuries at the end %s; wall %.2f s" % (i, arm, at, names, inj, rows[-1]["wall_s"]), flush=True)
    with open(os.path.join(a.out, "replay_rows.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f)
    for k, n in sorted(pair_summary(rows).items()):
        print("%-5s %s" % (k, n))
    return 0


NS = "RimMandrake.FlowWorks.RM_NorthstarProofs"
PG = "RimMandrake.FlowWorks.RM_PocketGrid"


def static(W, ty, m, args):
    r = W.call("jawa/static_call", type=ty, method=m, args=args)
    return r.get("result") if r.get("success") else "FAILED " + str(r.get("message") or r.get("_error"))


def edge(W, pid):
    e = str(static(W, PG, "ProofEdge", pid))
    t = str(static(W, NS, "ProofTrap", pid))
    plain = e.split("| plain")[-1]

    def g(pat, s):
        m = re.search(pat, s)
        return m.group(1) if m else None
    return {"builtTick": int(g(r"builtTick=(-?\d+)", plain) or -1), "gen": g(r"gen=(\d+)", e), "built": g(r"built=(\d+)", plain), "rebuilds": int(g(r"rebuilds=(\d+)", plain) or -1),
            "pocket": g(r"pocket=(\w+)", e), "ownReachesEdge": g(r"own=(\w+)", e), "held": g(r"held=(\w+)", t), "raw": e + " || " + t}


def hand_dig(arm, W, t0, wait, dig, speed):
    """The dig by the hands, then on to +10. G: run to the tick, then act and go. T: one run, the act on its tick. -> (tick of the dig, the tool's reply)."""
    import prove_run_until as R
    R.open_session()
    rid = R.req("dig")
    act = {"id": rid, "tool": "jawa/flowworks_excavation_drive", "args": dig, "at": 0}
    if arm == "G":
        r = R.run(R.at_tick(t0 + wait), wait + 50, speed=speed)
        if r.get("why") == "hit":
            r = R.run(R.at_tick(t0 + wait + 10), 60, speed=speed, acts=[act])
    else:
        r = R.run(R.at_tick(t0 + wait + 10), wait + 60, speed=speed, acts=[dict(act, at=wait)])
    done = [x for x in r.get("acts") or [] if x.get("id") == rid and x.get("state") == "done"]
    R.end_session()
    if r.get("why") != "hit" or not done:
        return None, R.brief(r) or r
    return int(done[0]["tick"]), done[0]["reply"]


def pocket(W, a):
    pids = colonists(W)
    info = W.call("jawa/map_info")
    rows = []
    for i in range(a.trials):
        for arm in a.arms.split(","):
            # one fresh 3x3 station per run, 12 cells apart
            n = len(rows)
            x, z = a.x0 + 10 * (n % 12), a.z0 + 10 * (n // 12)
            row = {"arm": arm, "cell": (x, z), "quiet": a.quiet}
            rows.append(row)
            sp = W.call("jawa/spawn_pawn", kindDef=a.kind, x=x, z=z, faction="none")
            pid = ((sp.get("pawns") or [{}])[0]).get("id")
            row["spawn"] = pid or sp
            if not pid:
                print("UNMEASURED: no person: %s" % sp)
                return 2
            W.call("jawa/damage", damageDef="Stun", amount=200, thingId=pid)        # it stands still; the same in every arm
            static(W, NS, "ProofShove", "%s;%d,%d" % (pid, x, z))
            row["before"] = edge(W, pid)
            W.call("jawa/flowworks_excavation_drive", x=x + 4, z=z, deepenLevels=a.levels)   # the earlier dig, 4 cells away
            time.sleep(0.5)                                                         # frames: the paused write is rebuilt at once
            t0 = tick(W)
            row["afterFirstDig"] = edge(W, pid)
            wait = 200 if a.quiet else 20
            speed = a.speed
            dig = dict(x=x, z=z, deepenLevels=a.levels)
            w = time.time()
            if arm == "P":
                seg(W, pids[0], t0 + wait, wait + 50, speed)
                g = time.time()
                d = W.call("jawa/flowworks_excavation_drive", **dig)
                row["gap_s"] = round(time.time() - g, 3)
                tact = tick(W)
                row["digTick"] = (d.get("ticksGame"), tact)
            elif arm in ("G", "T"):
                tact, d = hand_dig(arm, W, t0, wait, dig, speed)
                row["digTick"] = (tact, None)
                if tact is None:
                    print("UNMEASURED: %s" % d)
                    return 2
            else:
                # the dig lands on the running game: start a run that outlasts it, watch the clock, dig
                W.call("jawa/scene_slice", action="start", pawn=pids[0], speed=speed, maxTicks=2000, tracks=json.dumps({"depth": {"p": "fw.depth", "cell": [x, z]}}),
                       until=json.dumps({"cmp": [{"p": "game.tick"}, ">=", t0 + wait + 10 + a.slack]}) )
                while (tick(W) or 0) < t0 + wait - 2:
                    pass
                d = W.call("jawa/flowworks_excavation_drive", **dig)
                tact = d.get("ticksGame")
                row["digTick"] = (tact, None)
                if arm == "RP":
                    W.call("jawa/scene_slice", action="cancel")                       # a bare pause, then on
                    time.sleep(a.dwell)
                    seg(W, pids[0], tact + 10, 100, speed)
                else:
                    end = time.time() + 30
                    while W.call("jawa/scene_slice", action="status").get("stage") != "closed" and time.time() < end:
                        time.sleep(0.05)
            row["digOk"] = d.get("success")
            row["depth"] = d.get("depth")
            row["digOnPaused"] = (d.get("state") or {}).get("paused")
            row["void"] = arm not in ("P", "G", "T") and row["digOnPaused"] is not False       # the run had ended before the call landed: not arm R
            if arm == "P":
                seg(W, pids[0], tact + 10, 100, speed)
            row["t_first"] = tick(W) - tact
            row["at10"] = edge(W, pid)
            now = tick(W)
            seg(W, pids[0], tact + 100, 200, speed)
            row["t_second"] = tick(W) - tact
            row["at100"] = edge(W, pid)
            row["wall_s"] = round(time.time() - w, 2)
            row["digAfterFirstBuild"] = tact - row["afterFirstDig"]["builtTick"]
            row["rebuiltAfterDig"] = row["at100"]["builtTick"] - tact
            print(("VOID " if row["void"] else "") + "%-2s dig %s ticks after the last rebuild, depth %s | +%s: held=%s pocket=%s reachesEdge=%s | +%s: held=%s pocket=%s | grid rebuilt at dig%+d"
                  % (arm, row["digAfterFirstBuild"], row["depth"], row["t_first"], row["at10"]["held"], row["at10"]["pocket"], row["at10"]["ownReachesEdge"],
                     row["t_second"], row["at100"]["held"], row["at100"]["pocket"], row["rebuiltAfterDig"]), flush=True)
            with open(os.path.join(a.out, "pocket_rows_%s.json" % ("quiet" if a.quiet else "throttled")), "w", encoding="utf-8") as f:
                json.dump(rows, f, indent=1)
    out = pocket_summary(rows)
    print(json.dumps(out))
    return pocket_verdict(out)


def pocket_verdict(out):
    """0: each arm of the hands (G, T) reads as running play does (not held at the first read, held at +100), and P, the arm that must
    differ, is held at its first read, so the reading is not blind. 1: a hand's arm is held at its first read. 2: cannot say."""
    hands = [out[k] for k in ("G", "T") if k in out]
    if not hands:
        return 0
    if any(o["heldAtFirstRead"] for o in hands):
        return 1
    p = out.get("P") or {}
    good = p.get("runs") and p["heldAtFirstRead"] == p["runs"] and all(o["runs"] and o["heldAt100"] == o["runs"] for o in hands)
    return 0 if good else 2


def pocket_summary(rows):
    """arm -> [runs, held at the first read, first reads at which ticks, ticks from the dig to the rebuild]; void runs counted apart."""
    out = {}
    for r in rows:
        o = out.setdefault(r["arm"], {"runs": 0, "void": 0, "heldAtFirstRead": 0, "heldAt100": 0, "firstReadAt": [], "rebuiltAfter": []})
        if r["void"]:
            o["void"] += 1
            continue
        o["runs"] += 1
        o["heldAtFirstRead"] += r["at10"]["held"] == "True"
        o["heldAt100"] += r["at100"]["held"] == "True"
        o["firstReadAt"].append(r["t_first"])
        o["rebuiltAfter"].append(r["rebuiltAfterDig"])
    return out


def blast(W, a):
    """The in-tick act that the slice can do: a boomalope beside a damaged pit ramp is killed inside the tick (K) or by Python on
    the paused game (P). Its blast destroys the ramp in a later TICK in both arms, so the FlowWorks write is never made paused.
    Predicted: the two arms agree (rebuild at the 60-tick throttle, counted from the ramp's placing)."""
    pid = colonists(W)[0]
    rows = []
    for i in range(a.trials):
        for arm in ("K", "P"):
            n = len(rows)
            x, z = a.x0 + 30 * (n % 5), a.z0 + 30 * (n // 5)
            static(W, PG, "ProofEdge", pid)
            W.call("jawa/flowworks_excavation_drive", x=x, z=z, deepenLevels=2)
            r = static(W, NS, "ProofRamp", "%d,%d;0" % (x, z))
            rt = W.call("jawa/list_things_batch", rects="%d,%d,1,1" % (x, z)) if not str(r).startswith("RAMP") else None
            sp = W.call("jawa/spawn_pawn", kindDef="Boomalope", x=x + 1, z=z, faction="none")
            bid = ((sp.get("pawns") or [{}])[0]).get("id")
            hit = W.call("jawa/damage", damageDef="Blunt", amount=a.ramphit, x=x, z=z)
            row = {"arm": arm, "ramp": r, "rampHit": [(t.get("def"), t.get("hitPointsAfter"), t.get("destroyed")) for t in hit.get("targets") or []], "spawn": bid, "why": rt}
            rows.append(row)
            W.call("jawa/damage", damageDef="Stun", amount=200, thingId=bid)
            time.sleep(0.5)
            t0 = tick(W)
            row["start"] = edge(W, pid)
            tracks = {"fires": {"p": "map.count", "def": "Fire"}, "ramps": {"p": "map.count", "def": "RM_PitRamp"}}
            if arm == "K":
                st, tr = W.run(pawn=bid, speed=a.speed, maxTicks=200, actAt=20, damage=800.0, tracks=json.dumps(tracks), until=json.dumps({"cmp": [{"p": "game.tick"}, ">=", t0 + 50]}))
                trs = [tr]
            else:
                st, t1 = seg(W, bid, t0 + 20, 100, a.speed, tracks)
                d = W.call("jawa/damage", damageDef="Cut", amount=800.0, thingId=bid, armorPenetration=1.0, bodyPart="Body")
                row["dmg"] = [(t.get("dead"), t.get("bodyPartHit")) for t in d.get("targets") or []]
                st, t2 = seg(W, pid, t0 + 50, 100, a.speed, tracks)
                trs = [t1, t2]
            s = series(t0, trs, 50) if all(trs) else None
            rr = (s or {}).get("ramps") or []
            row["deadAt"] = next((k + 1 for k, v in enumerate((s or {}).get("dead") or []) if v and v[1]), None)
            row["fires"] = ((s or {}).get("fires") or [None])[-1]
            row["rampGoneAt"] = next((k + 1 for k, v in enumerate(rr) if v and v[1] < rr[0][1]), None)
            row["at50"] = edge(W, pid)
            seg(W, pid, t0 + 130, 200, a.speed)
            row["at130"] = edge(W, pid)
            row["builtAfterStart"] = row["at130"]["builtTick"] - t0
            row["state"] = st.get("state") or st.get("message")
            print("%s ramp %s hit %s | ramp gone at +%s | gen start %s +50 %s +130 %s | rebuilds %s %s %s | last rebuild at +%s | dead +%s fires %s" % (
                arm, r, row["rampHit"], row["rampGoneAt"], row["start"]["gen"], row["at50"]["gen"], row["at130"]["gen"],
                row["start"]["rebuilds"], row["at50"]["rebuilds"], row["at130"]["rebuilds"], row["builtAfterStart"], row["deadAt"], row["fires"]), flush=True)
            with open(os.path.join(a.out, "blast_rows.json"), "w", encoding="utf-8") as f:
                json.dump(rows, f, indent=1)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selfcheck", action="store_true")
    ap.add_argument("--scene", default="replay")
    ap.add_argument("--trials", type=int, default=5)
    ap.add_argument("--speed", default="Normal")
    ap.add_argument("--dwell", type=float, default=0.25)
    ap.add_argument("--arms", default="R,P,RP")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--kind", default="SpaceRefugee")
    ap.add_argument("--levels", type=int, default=4)
    ap.add_argument("--slack", type=int, default=0)
    ap.add_argument("--ramphit", type=float, default=20)
    ap.add_argument("--x0", type=int, default=60)
    ap.add_argument("--z0", type=int, default=60)
    ap.add_argument("--out", default=".")
    a = ap.parse_args()
    if a.selfcheck:
        return selfcheck()
    import prove_scene_tick_wiring as W
    W.connect()
    os.makedirs(a.out, exist_ok=True)
    if W.call("rimworld/get_ui_state").get("programState") != "Playing":
        W.call("rimworld/start_debug_game_ready", timeoutMs=280000, readiness="mapData", pauseIfNeeded=True)
    if not ready(W):
        print("UNMEASURED: no map")
        return 2
    import prove_run_until as R
    if W.call("jawa/session", action="state").get("stage") == "open":       # jawa/scene_slice is refused while a session is open
        R.open_session()
        R.end_session("abort")
    return R.closing(lambda: {"replay": replay, "pocket": pocket, "blast": blast}[a.scene](W, a))


if __name__ == "__main__":
    sys.exit(main())
