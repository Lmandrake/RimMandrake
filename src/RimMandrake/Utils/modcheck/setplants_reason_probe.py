#!/usr/bin/env python3
"""MODCHECK_ULTRAFAST_CLOCK_STALL_1 live clause A2: jawa/set_plants names the engine's reason for a rejected cell.

The bloom fuzz strip came back "REJECTED 75" of 150 RM_Fuzz with no cause. On a Playing map this paints ONE cell
PackedDirt (Core fertility 0.0), asks set_plants for Plant_Grass there (Core fertilityMin 0.05) additively
(clearFirst=false, destroys nothing), then paints the cell's captured terrain back in a finally. A candidate cell
with a thing on it (blocker) is restored and the next one tried, so the rejection is fertility's alone.
  exit 0  rejected 1, planted 0; the reason is not the generic text and holds the engine's own words
          (Core English MessageWarningNotEnoughFertility "Need more fertile terrain."); rejectedCells[0] reports
          fertility < fertilityMin, fertilityMin 0.05, terrain PackedDirt, no blocker
  exit 1  any of that fails (the pre-fix tool returned "terrain or conditions cannot support Plant_Grass" and no
          rejectedCells at all), or the terrain could not be put back
  exit 2  no map / bridge down / every candidate cell carried a blocker: UNMEASURED
Usage: python3 src/RimMandrake/Utils/modcheck/setplants_reason_probe.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
import rimbridge_client as rb  # noqa: E402

PLANT, DIRT = "Plant_Grass", "PackedDirt"
GENERIC = "terrain or conditions cannot support " + PLANT


def judge(res):
    """(verdict, why) for one set_plants result on a PackedDirt cell: 'ok', 'blocker' (try another cell) or 'fail'."""
    if not isinstance(res, dict):
        return "fail", "no result object: %r" % (res,)
    rows = res.get("rejectedCells")
    if res.get("planted") != 0 or res.get("rejected") != 1:
        return "fail", "planted=%s rejected=%s (want 0 / 1)" % (res.get("planted"), res.get("rejected"))
    if not isinstance(rows, list) or len(rows) != 1:
        return "fail", "rejectedCells missing or not one row: %r" % (rows,)
    row = rows[0]
    if row.get("blocker"):
        return "blocker", "cell carries %s" % row["blocker"]
    reasons = list((res.get("rejectionReasons") or {}).keys())
    reason = str(row.get("reason") or "")
    if len(reasons) != 1 or not reasons[0].startswith(GENERIC + ": "):
        return "fail", "rejectionReasons %r: want one '%s: <engine reason>'" % (reasons, GENERIC)
    tail = reasons[0][len(GENERIC) + 2:].strip()
    if not tail or tail == "no reason given" or tail != reason:
        return "fail", "engine reason empty/absent or disagrees with rejectedCells: %r vs %r" % (tail, reason)
    if "fertil" not in reason.lower():
        return "fail", "reason %r does not name fertility" % reason
    fert, fmin = row.get("fertility"), row.get("fertilityMin")
    if row.get("terrain") != DIRT or fert is None or fmin is None or not (float(fert) < float(fmin)) \
            or abs(float(fmin) - 0.05) > 1e-4:
        return "fail", "rejectedCells row wrong: terrain=%s fertility=%s fertilityMin=%s" % (
            row.get("terrain"), fert, fmin)
    return "ok", "reason=%r fertility=%s fertilityMin=%s polluted=%s" % (reason, fert, fmin, row.get("polluted"))


def main():
    h, p, tok = rb.resolve_endpoint()
    c = rb.RimBridge(host=h, port=p, token=tok, timeout=60.0)
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
    cx, cz = int(size["x"]) // 2, int(size["z"]) // 2
    for k in range(1, 9):                                       # off the colony's centre, along a diagonal
        x, z = cx + 7 * k, cz - 5 * k
        before = c.call("jawa/get_terrain_batch", {"rects": "%d,%d,1,1" % (x, z)})
        ops = (before or {}).get("ops") if isinstance(before, dict) else None
        if not ops:
            continue
        verdict, why, restored = "fail", "never ran", False
        try:
            c.call("jawa/set_terrain_batch", {"ops": "%s:%d,%d,1,1" % (DIRT, x, z)})
            res = c.call("jawa/set_plants", {"ops": "%s:%d,%d,1,1" % (PLANT, x, z), "clearFirst": False})
            verdict, why = judge(res)
        finally:
            c.call("jawa/set_terrain_batch", {"ops": ops})
            after = c.call("jawa/get_terrain_batch", {"rects": "%d,%d,1,1" % (x, z)})
            restored = isinstance(after, dict) and after.get("ops") == ops
        print("cell %d,%d (%s): %s %s; terrain restored=%s" % (x, z, ops, verdict, why, restored))
        if not restored:
            return 1
        if verdict == "blocker":
            continue
        return 0 if verdict == "ok" else 1
    print("UNMEASURED every candidate cell carried a blocker or had no terrain")
    return 2


if __name__ == "__main__":
    sys.exit(main())
