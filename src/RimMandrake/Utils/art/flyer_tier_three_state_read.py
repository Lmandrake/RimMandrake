#!/usr/bin/env python3
"""flyer_tier_three_state_read.py - FLYER_TIER_THREE_REBUILD_EASY_WINGS_ONLY clause A1: the six tier-3 flyers report
canEverFly and maxFlightTimeStat > 0 from Pawn_FlightTracker on a spawned pawn.

A state read, never a flight: action=report, maintainTicks=0, unpause=False, the game stays paused. It spawns one of each
kind on a quicktest map (the tracker exists only on a spawned pawn) and destroys them after. Runs under Windows Python
(the bridge binds Windows loopback). Live only in a joint session: the Relentless game gate holds every flyer for him.
Exit 0 = all six hold, 1 = one does not, 2 = UNMEASURED.
"""
import os
import sys

KINDS = ("RM_Dwommo", "RM_FeverSwarm", "RM_Skellick", "RM_Skinflap", "RM_Skiralim", "RSW_Porg")


def verdict(rows):
    """rows: {kind: tracker rows of the report}. -> (exit code, last line). Pure."""
    empty = [k for k in KINDS if not rows.get(k)]
    if empty:
        return 2, "UNMEASURED: no spawned pawn in the tracker report: " + ",".join(empty)
    bad = [k for k in KINDS if not all(p.get("canEverFly") and (p.get("maxFlightTimeStat") or 0) > 0 for p in rows[k])]
    return (1, "FAIL " + ",".join(bad)) if bad else (0, "PASS all six report canEverFly and maxFlightTimeStat > 0")


def main():
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    import rimbridge_client as rc
    try:
        host, port, token = rc.resolve_endpoint(None, None, None, None)
        if not token:
            raise RuntimeError("no bridge token")
        rows = {}
        with rc.RimBridge(host, port, token, timeout=60) as rb:
            info = rb.call("jawa/map_info", {})
            cx, cz = int(info["sizeX"]) // 2, int(info["sizeZ"]) // 2
            for j, k in enumerate(KINDS):
                rb.call("jawa/spawn_pawn", {"kindDef": k, "x": cx + 3 * j, "z": cz, "faction": "player", "count": 1})
                r = rb.call("jawa/pawn_flight", {"action": "report", "kind": k, "maxPawns": 5, "maintainTicks": 0, "unpause": False})
                rows[k] = [p for p in (r.get("pawns") or []) if isinstance(p, dict)]
                print(k, rows[k])
            rb.call("jawa/destroy_bulk", {"filter": "playerAnimals", "dryRun": False})
    except Exception as e:  # noqa: BLE001 -- a bridge fault measures nothing about the mods
        print("UNMEASURED: bridge call failed: %s" % type(e).__name__)
        return 2
    code, line = verdict(rows)
    print(line)
    return code


if __name__ == "__main__":
    sys.exit(main())
