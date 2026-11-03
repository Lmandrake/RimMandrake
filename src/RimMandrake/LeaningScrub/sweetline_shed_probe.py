#!/usr/bin/env python3
"""LEANINGSCRUB_SWEETLINE_SHED_LIVE_1 live clause A1: a mature sweetline tree sheds its felt once its timer has passed.

The item's repro, standalone (no suite, no site): on a Playing map it lays Soil over a 13x13 pad off the map centre,
clears its plants/items/filth, plants ONE RM_SweetlineTree at growth 1, reads the tree's inspect timer line, jumps the
clock +5.5 days (past the 5-day timer and its <=5-day first-shed stagger; jawa/time_set_ticks, timeException=true),
steps 2100 real ticks (one Long tick: Plant.TickLong -> CompTickLong), then reads the felt (RM_SweetlineWool, stacks
summed) round the tree, the tree's inspect line again and the log for 'Exception ticking'. The tree and the felt are
destroyed after (the soil stays: a disposable quicktest map).
  exit 0  the tree stands, >= woolCount (5) more felt within the pad, the timer line reset to "falls in" (it ran), no
          'Exception ticking' line in the log
  exit 1  any of that fails; the line printed says which half broke (the timer line still 'ready to fall' = the
          comp never ran its shed; reset but no felt = the felt went somewhere the count does not see; tree gone = it
          died across the jump)
  exit 2  no map / bridge down / the tree did not stand or showed no station line before the jump: UNMEASURED
History: LIVE 2026-10-07 two runs shed 0 (tree then carried the bark-warden harvest seam, cut 2026-10-23); the suite row
sweetline.station_sheds_wool PASSED 2026-10-23 (FOUNDRY scrub_ns2.json at 18669c79a5c8). This re-proves it on the build
of today.
Usage: python3 src/RimMandrake/LeaningScrub/sweetline_shed_probe.py
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MODCHECK = os.path.join(HERE, "..", "Utils", "modcheck")
sys.path.insert(0, MODCHECK)
sys.path.insert(0, os.path.join(MODCHECK, ".."))

TREE, FELT, SOIL = "RM_SweetlineTree", "RM_SweetlineWool", "Soil"
WOOL_COUNT = 5                  # RM_SweetlineTree.xml woolCount
JUMP = int(5.5 * 60000)         # past woolIntervalDays 5 and the first-shed stagger Rand.Range(0, 5 days)
STEP = 2100                     # one Long tick (2000) and a margin
HALF = 6                        # 13x13 pad; GenPlace Near lands within a few cells of the trunk
TIMER = re.compile(r"Loose .*(falls in|ready to fall)")


def judge(before, after, moved, standing, lines_after, errors):
    """-> (ok, reasons). The verdict alone, so the selftest can prove it rejects each broken half."""
    bad = []
    text = " ".join(lines_after or [])
    if not standing:
        bad.append("tree gone after the wait (died across the jump)")
    if moved is None or moved < STEP - 100:
        bad.append("clock moved %s < %d after the jump: no Long tick guaranteed" % (moved, STEP - 100))
    shed = (after or 0) - (before or 0)
    if shed < WOOL_COUNT:
        bad.append("shed %d felt (want >= %d)" % (shed, WOOL_COUNT))
    if standing:
        if "ready to fall" in text:
            bad.append("timer still 'ready to fall': CompTickLong never ran its shed")
        elif "falls in" not in text:
            bad.append("no timer line after the wait: %r" % (lines_after,))
    if errors:
        bad.append("'Exception ticking' in the log: %s" % (errors[0][:300],))
    return not bad, bad


def _felt(c, rect):
    r = c.call("jawa/list_things", {"defName": FELT, "rect": rect, "limit": 500})
    if not isinstance(r, dict) or r.get("success") is False:
        return None
    return sum(int(w.get("stackCount") or 1) for w in (r.get("things") or []))


def _tree(c, x, z):
    r = c.call("jawa/list_things", {"defName": TREE, "rect": "%d,%d,1,1" % (x, z), "limit": 5})
    rows = (r or {}).get("things") or [] if isinstance(r, dict) else []
    return rows[0]["id"] if rows else None


def _inspect(c, tid):
    r = c.call("jawa/inspect_string", {"thingIds": tid})
    rows = (r or {}).get("things") or [] if isinstance(r, dict) else []
    return list(rows[0].get("inspect") or []) if rows and not rows[0].get("error") else []


def _tick_errors(c):
    """(total repeats, newest text) of 'Exception ticking' error lines in the log buffer (it is never drained, and an
    already-capped Verse.Log is blind to new lines: instrument_traps)."""
    lg = c.call("jawa/drain_log", {"limit": 500, "errorsOnly": True, "contains": "Exception ticking"})
    rows = (lg or {}).get("messages") or [] if isinstance(lg, dict) else []
    return sum(int(m.get("repeats") or 1) for m in rows), (str(rows[-1].get("text")) if rows else None)


def _ticks(c):
    try:
        return (c.call("rimworld/get_game_info", {}) or {}).get("ticksGame")
    except Exception:                                           # noqa: BLE001
        return None


class _Session(object):
    def __init__(self, client):
        self.c = client

    def call(self, tool, **p):
        return self.c.call(tool, p)


def main():
    import clockgate  # noqa: E402
    import helpers as H  # noqa: E402
    import rimbridge_client as rb  # noqa: E402
    h, p, tok = rb.resolve_endpoint()
    c = rb.RimBridge(host=h, port=p, token=tok, timeout=120.0)
    try:
        c.connect()
    except Exception as e:                                      # noqa: BLE001
        print("UNMEASURED bridge unreachable: %s" % e)
        return 2
    probe = c.call("jawa/get_terrain_batch", {"rects": "0,0,1,1"})
    size = (probe or {}).get("mapSize") if isinstance(probe, dict) else None
    if not size:
        print("UNMEASURED no map loaded: %r" % (probe,))
        return 2
    x, z = int(size["x"]) // 2 + 30, int(size["z"]) // 2 + 30   # off the colony's centre
    pad = "%d,%d,%d,%d" % (x - HALF, z - HALF, 2 * HALF + 1, 2 * HALF + 1)
    c.call("jawa/destroy_batch", {"rects": pad, "categories": "Plant,Item,Filth"})
    c.call("jawa/set_terrain_batch", {"ops": "%s:%s" % (SOIL, pad), "layer": "top"})
    c.call("jawa/set_plants", {"ops": "%s:%d,%d,1,1" % (TREE, x, z), "growth": 1.0})
    tid = _tree(c, x, z)
    if not tid:
        print("UNMEASURED the sweetline tree did not stand at %d,%d after set_plants" % (x, z))
        return 2
    try:
        lines0 = _inspect(c, tid)
        if not TIMER.search(" ".join(lines0)):
            print("UNMEASURED no station timer line before the jump (stations off? not mature?): %r" % (lines0,))
            return 2
        before = _felt(c, pad)
        cur = _ticks(c)
        if before is None or cur is None:
            print("UNMEASURED felt count or clock unreadable before the jump")
            return 2
        err0, _ = _tick_errors(c)                               # jawa/drain_log never drains: count, then compare
        r = c.call("jawa/time_set_ticks", {"ticks": int(cur + JUMP), "timeException": True,
                                           "why": "LEANINGSCRUB_SWEETLINE_SHED_LIVE_1 probe: past the 5-day shed timer"})
        if not (isinstance(r, dict) and r.get("success")):
            print("UNMEASURED time_set_ticks refused: %r" % (r,))
            return 2
        start = now = _ticks(c)
        if start is None:
            print("UNMEASURED clock unreadable after the jump")
            return 2
        s = _Session(c)
        for _ in range(8):                                      # bounded: a stalled clock is the harness, not the tree
            if now is None or now - start >= STEP:
                break
            try:
                clockgate.advance_chunk(s, min(STEP - (now - start), 2000), time_exception=True)
            except Exception as e:                              # noqa: BLE001 - a vitals stop is not the tree's verdict
                print("UNMEASURED the clock was stopped after the jump: %s: %s" % (type(e).__name__, str(e)[:300]))
                return 2
            now = _ticks(c)
        moved = None if now is None else now - start
        if moved is None or moved < STEP - 100:
            print("UNMEASURED the clock moved %s of %d ticks after the jump (stalled or unreadable)" % (moved, STEP))
            return 2
        after = _felt(c, pad)
        standing = _tree(c, x, z) == tid
        lines1 = _inspect(c, tid) if standing else ["<tree gone>"]
        err1, last = _tick_errors(c)
        errors = [last or "?"] if (err1 or 0) > (err0 or 0) else []
        print("tree %s at %d,%d; felt before=%s after=%s; clock +%s after the +%d jump; inspect before %r after %r; "
              "Exception ticking lines=%d" % (tid, x, z, before, after, moved, JUMP, lines0, lines1, len(errors)))
        ok, bad = judge(before, after, moved, standing, lines1, errors)
        for b in bad:
            print("FAIL  " + b)
        return 0 if ok else 1
    finally:
        c.call("jawa/destroy_batch", {"rects": pad, "categories": "Plant,Item"})


if __name__ == "__main__":
    sys.exit(main())
