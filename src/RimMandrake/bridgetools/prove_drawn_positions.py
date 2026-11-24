#!/usr/bin/env python3
"""Live proof that a pawn which walked while the bridge stepped ticks under pause is drawn on its own square.
Item RIMMANDRAKE_FIX_BRIDGE_STEPPED_PAWNS_DRAWN_ON_OLD_SQUARE. Hook: JawaBenchDrawSettle (JawaBenchShotSettleTools.cs).

    python.exe prove_drawn_positions.py                     live, a scratch quicktest map; no save is read or written
    python3 prove_drawn_positions.py --selfcheck            the judge on hand-made readings, good and planted; no game
    python3 prove_drawn_positions.py --judge-evidence F     judge a recorded reading (the item's outcome check)

One colonist is ordered 6 squares away, 300 ticks are stepped with jawa/safe_advance, and jawa/drawn_positions reads the
drawn position of the last frame. Two arms: `off` (the hook off: the red control, the pawn must be drawn over 1 square from
its own) and `on` (within 1 square). The hook is put back on after the `off` arm. The live run prints one `READING {json}` line.
Exit 0 = PASS, 1 = FAIL, 2 = UNMEASURED (no bridge, no walk, the pawn was not drawn, the `off` arm did not go red)."""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "Utils"))
sys.path.insert(0, HERE)

BAR = 1.0           # squares between the drawn position and the centre of the pawn's own square
WALK = 3            # an arm whose pawn walked less decides nothing
FRESH = 3           # frames since the pawn's last draw; more = the camera does not draw it
CS = os.path.join(HERE, "JawaBench.BridgeTools", "JawaBenchShotSettleTools.cs")
SAMPLER = os.path.join(HERE, "JawaBench.BridgeTools", "JawaBenchTpsSampler.cs")


# ------------------------------------------------------------------------------------------------ the judge (pure)
def judge_arm(arm, hook_on):
    """-> (True PASS / False FAIL / None UNMEASURED, why) for one arm's reading."""
    if not isinstance(arm, dict):
        return None, "no reading"
    for k in ("walked", "ticks", "offsetCells", "framesSinceDraw", "paused", "hookOn"):
        if arm.get(k) is None:
            return None, "%s was not read" % k
    if arm["hookOn"] is not hook_on:
        return None, "the hook reads %s, this arm needs %s" % (arm["hookOn"], hook_on)
    if arm["paused"] is not True:
        return None, "the game was not paused at the read"
    if arm["ticks"] < 1 or arm["walked"] < WALK:
        return None, "%s ticks, the pawn walked %s squares (needs %d)" % (arm["ticks"], arm["walked"], WALK)
    if not 0 <= arm["framesSinceDraw"] <= FRESH:
        return None, "the pawn was last drawn %s frames before the read" % arm["framesSinceDraw"]
    return arm["offsetCells"] <= BAR, "walked %s squares in %s ticks, drawn %s squares off its own" % (arm["walked"], arm["ticks"], arm["offsetCells"])


def judge(reading):
    """Both arms. The `off` arm must be seen red, or the `on` arm's green says nothing."""
    r = reading if isinstance(reading, dict) else {}
    off, why_off = judge_arm(r.get("off"), False)
    on, why_on = judge_arm(r.get("on"), True)
    detail = "hook off: %s | hook on: %s" % (why_off, why_on)
    if on is False:
        return False, detail
    if on is None or off is None:
        return None, detail
    if off is True:
        return None, "the red control did not go red. " + detail
    if not r.get("companionSrc"):
        return None, "the reading names no companion source hash. " + detail
    return True, detail


def hook_in_source():
    """None when the hook is in the companion source, on by default and installed at registration; else what is missing."""
    with open(CS, encoding="utf-8") as f:
        cs = "\n".join(ln for ln in f.read().splitlines() if not ln.strip().startswith("//"))
    with open(SAMPLER, encoding="utf-8") as f:
        sm = "\n".join(ln for ln in f.read().splitlines() if not ln.strip().startswith("//"))
    for text, src in (("nameof(PawnTweener.PreDrawPosCalculation)", cs), ("internal static bool On = true;", cs),
                      ("__instance.ResetTweenedPosToRoot();", cs), ('"jawa/drawn_positions"', cs), ("JawaBenchDrawSettle.Install();", sm)):
        if text not in src:
            return "the companion source lacks `%s`" % text
    return None


def selfcheck():
    def made(off=4.0, on=0.1, **kw):
        base = {"walked": 6, "ticks": 300, "framesSinceDraw": 1, "paused": True}
        r = {"companionSrc": "ab", "off": dict(base, offsetCells=off, hookOn=False), "on": dict(base, offsetCells=on, hookOn=True)}
        for k, v in kw.items():
            if k in ("offArm", "onArm"):
                r[k[:-3]].update(v)
            else:
                r[k] = v
        return r
    cases = [
        ("good", made(), True),
        ("the fault: still drawn on the old square with the hook on", made(on=4.0), False),
        ("just over the bar", made(on=1.01), False),
        ("at the bar", made(on=1.0), True),
        ("the red control stayed green", made(off=0.2), None),
        ("the pawn did not walk", made(onArm={"walked": 0}), None),
        ("no tick was stepped", made(onArm={"ticks": 0}), None),
        ("the camera did not draw it", made(onArm={"framesSinceDraw": 40}), None),
        ("never drawn", made(onArm={"framesSinceDraw": -1}), None),
        ("the offset was not read", made(onArm={"offsetCells": None}), None),
        ("the game was playing", made(onArm={"paused": False}), None),
        ("the on arm ran with the hook off", made(onArm={"hookOn": False}), None),
        ("the off arm ran with the hook on", made(offArm={"hookOn": True}), None),
        ("no companion hash", made(companionSrc=None), None),
        ("an arm is missing", {"on": made()["on"], "companionSrc": "ab"}, None),
        ("empty", {}, None),
        ("not a reading", [], None),
    ]
    bad = 0
    for n, r, want in cases:
        got = judge(r)[0]
        bad += got is not want
        print("%s %s -> %s" % ("ok  " if got is want else "FAIL", n, got))
    miss = hook_in_source()
    print("%s the hook is in the companion source%s" % ("FAIL" if miss else "ok  ", ": " + miss if miss else ""))
    print("prove_drawn_positions judge: %d of %d" % (len(cases) - bad, len(cases)))
    return 1 if bad or miss else 0


def judge_evidence(path):
    """Exit 0 the need is met, 1 it is not (no reading yet, a FAIL, or a reading that decides nothing)."""
    miss = hook_in_source()
    if miss:
        print("NOT MET: " + miss)
        return 1
    try:
        with open(path, encoding="utf-8") as f:
            reading = json.load(f)
    except (OSError, ValueError) as e:
        print("NOT MET: no readable live reading at %s (%s)" % (path, type(e).__name__))
        return 1
    v, d = judge(reading)
    print("%s: %s" % ("MET" if v is True else "NOT MET (FAIL)" if v is False else "NOT MET (UNMEASURED)", d))
    return 0 if v is True else 1


# ------------------------------------------------------------------------------------------------- the game
def where(W, pid, **kw):
    r = W.call("jawa/drawn_positions", pawnIds=pid, **kw)
    rows = r.get("pawns") or []
    return r, (rows[0] if rows else {})


def arm(W, pid, hook, shots):
    """Walk pid about 6 squares under stepped ticks. -> the arm's reading (what could not be read stays None)."""
    out = {"hookOn": None, "walked": None, "ticks": None, "offsetCells": None, "framesSinceDraw": None, "paused": None}
    W.call("rimworld/pause_game", pause=True)
    r, p0 = where(W, pid, autoSettle="on" if hook else "off")
    if not p0:
        out["why"] = "drawn_positions: %s" % {k: r.get(k) for k in ("message", "_error")}
        return out
    W.call("jawa/settle_tweens")
    W.call("rimworld/jump_camera_to_cell", x=p0["x"], z=p0["z"])
    time.sleep(1.5)
    tried = []
    for dx, dz in ((6, 0), (-6, 0), (0, 6), (0, -6), (5, 5), (-5, -5), (5, -5), (-5, 5)):
        o = W.call("jawa/order_pawn", pawnId=pid, x=p0["x"] + dx, z=p0["z"] + dz, waitTicks=0, unpause=False)
        row = (o.get("results") or o.get("pawns") or [{}])[0] if isinstance(o.get("results") or o.get("pawns"), list) else {}
        tried.append((dx, dz, row.get("canReach"), row.get("accepted")))
        adv = W.call("jawa/safe_advance", ticks=300, chunk=60)
        time.sleep(1.0)
        r, p1 = where(W, pid)
        if not p1:
            out["why"] = "the pawn is gone: %s" % r.get("message")
            return out
        out.update(hookOn=(r.get("autoSettle") or {}).get("on"), installed=(r.get("autoSettle") or {}).get("installed"), resets=(r.get("autoSettle") or {}).get("resets"),
                   faults=(r.get("autoSettle") or {}).get("faults"), walked=max(abs(p1["x"] - p0["x"]), abs(p1["z"] - p0["z"])), ticks=adv.get("executed"),
                   advanceState=adv.get("state"), start=[p0["x"], p0["z"]], at=[p1["x"], p1["z"]], drawn=[p1.get("drawnX"), p1.get("drawnZ")],
                   offsetCells=p1.get("offsetCells"), framesSinceDraw=p1.get("framesSinceDraw"), moving=p1.get("moving"), paused=r.get("paused"), tried=tried)
        if out["walked"] >= WALK:
            break
    s = W.call("rimworld/screenshot_cell_rect", x=p0["x"] - 9, z=p0["z"] - 9, width=19, height=19, fileName="drawn_positions_%s_%d" % ("on" if hook else "off", int(time.time())))
    shots.append(s.get("path") or {k: s.get(k) for k in ("message", "_error")})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selfcheck", action="store_true")
    ap.add_argument("--judge-evidence", metavar="FILE")
    a = ap.parse_args()
    if a.selfcheck:
        return selfcheck()
    if a.judge_evidence:
        return judge_evidence(a.judge_evidence)
    import companion_identity as CI
    import prove_scene_tick_wiring as W
    try:
        W.connect()
    except (Exception, SystemExit) as e:  # noqa: BLE001 - no bridge is UNMEASURED
        print("UNMEASURED: no bridge: %s" % str(e)[:200])
        return 2
    W.call("rimworld/start_debug_game_ready", timeoutMs=280000, readiness="mapData", pauseIfNeeded=True)
    from await_lifecycle import await_lifecycle
    if not await_lifecycle(W.call, "map_ready", deadline_s=240):
        print("UNMEASURED: no quicktest map reached Playing")
        return 2
    time.sleep(3)
    pl = [p for p in W.call("jawa/pawn_get", limit=200).get("pawns") or [] if p.get("faction") == "PlayerColony" and p.get("kindDef") == "Colonist"]
    if not pl:
        print("UNMEASURED: no colonist on the quicktest map")
        return 2
    pid, shots = pl[0]["thingId"], []
    reading = {"companionSrc": CI.srchash_worktree(os.path.abspath(os.path.join(HERE, "..", "..", ".."))), "pawn": pid,
               "host": os.environ.get("COMPUTERNAME") or os.uname().nodename, "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    try:
        reading["off"] = arm(W, pid, False, shots)
    finally:
        W.call("jawa/drawn_positions", pawnIds=pid, autoSettle="on")
    reading["on"] = arm(W, pid, True, shots)
    reading["shots"] = shots
    v, d = judge(reading)
    print("READING " + json.dumps(reading, sort_keys=True))
    print("%s A1: %s" % ("PASS" if v is True else "FAIL" if v is False else "UNMEASURED", d))
    return 0 if v is True else 1 if v is False else 2


if __name__ == "__main__":
    sys.exit(main())
