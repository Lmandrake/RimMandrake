#!/usr/bin/env python3
"""prove_shotsettle_live.py - SHOTSETTLE_BUILD_PAUSED_BARRIER clause A1, on the running game.

Runs rimbench/shotsettle.settled_shot once on the current map: pause, read ticksGame, settle every
spawned pawn's tweener (jawa/settle_tweens), capture, read ticksGame again.
Exit 0: the capture exists, ticksGame before == after, and at least one pawn was settled.
Exit 1: the barrier refused (ticks moved, settle refused) or no pawn was settled.
Exit 2: UNMEASURED (no bridge, no game, no map, tool missing from the deployed companion).
Writes nothing but the screenshot and pauses the game; advances no ticks.
"""
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "Utils")))


def _local(path):
    """A Windows path (C:\\x or C:/x) as this interpreter can open it (python.exe or WSL)."""
    if not path:
        return None
    m = re.match(r"^([A-Za-z]):[\\/](.*)$", path)
    if m and os.name != "nt":
        return "/mnt/%s/%s" % (m.group(1).lower(), m.group(2).replace("\\", "/"))
    return path


def main():
    try:
        import rimbridge_client as rb
        from rimbench.shotsettle import settled_shot, ShotSettleError
        h, port, t = rb.resolve_endpoint()
        c = rb.RimBridge(host=h, port=port, token=t, timeout=120)
        c.connect()
    except Exception as e:
        print("UNMEASURED: bridge not reachable: %s: %s" % (type(e).__name__, str(e)[:200]))
        return 2

    def call(tool, **p):
        return c.call(tool, p) or {}

    try:
        gi = call("rimworld/get_game_info")
    except Exception as e:
        print("UNMEASURED: get_game_info: %s: %s" % (type(e).__name__, str(e)[:200]))
        return 2
    if not isinstance(gi.get("ticksGame"), int) or gi.get("ticksGame", -1) < 0:
        print("UNMEASURED: no running game (get_game_info ticksGame=%r)" % gi.get("ticksGame"))
        return 2
    try:
        r = settled_shot(call, "shotsettle_A1_%d" % int(time.time()))
    except ShotSettleError as e:
        m = str(e)
        if "UNMEASURED" in m or "No current map" in m or "no tool" in m.lower() or "unknown tool" in m.lower() \
                or "No game is running" in m:
            print("UNMEASURED: %s" % m[:300])
            return 2
        print("FAIL A1: %s" % m[:300])
        return 1
    except Exception as e:  # bridge dropped, or the deployed companion predates jawa/settle_tweens
        print("UNMEASURED: %s: %s" % (type(e).__name__, str(e)[:300]))
        return 2
    if not (r.get("settled") or 0) and not (r.get("noTweener") or 0):
        print("UNMEASURED: no spawned pawn on the current map to settle")
        return 2
    shot = _local(r.get("path"))
    exists = bool(shot) and os.path.isfile(shot) and os.path.getsize(shot) > 0
    if not exists:
        print("FAIL A1: no screenshot file at %r" % r.get("path"))
        return 1
    ok = r["ticksBefore"] == r["ticksAfter"] and (r.get("settled") or 0) >= 1
    print("%s A1: ticksGame %d -> %d, settled %s pawns, max shift %s cells, shot %s"
          % ("PASS" if ok else "FAIL", r["ticksBefore"], r["ticksAfter"], r.get("settled"),
             r.get("maxShiftCells"), r.get("path")))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
