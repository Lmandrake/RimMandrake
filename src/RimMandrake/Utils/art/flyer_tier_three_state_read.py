#!/usr/bin/env python3
"""flyer_tier_three_state_read.py - FLYER_TIER_THREE_REBUILD_EASY_WINGS_ONLY clause A1: the six tier-3 flyers report
canEverFly and maxFlightTimeStat > 0 from Pawn_FlightTracker on a spawned pawn.

A state read, never a flight: action=report, maintainTicks=0, unpause=False, the game stays paused. It spawns one of each
kind on a quicktest map (the tracker exists only on a spawned pawn) and destroys them after. Runs under Windows Python
(the bridge binds Windows loopback). An agent may run it without the owner (owner by card 2026-11-12 ~8:25 PM PST:
paused reads allowed, no ticks, no pictures; anything moving still waits for him). paused_read_guard refuses unless the
game is paused before and after the read and ticksGame did not move during it.
Exit 0 = all six hold, 1 = one does not, 2 = UNMEASURED or refused by the guard.
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


def paused_read_guard(status0, ticks0, status1, ticks1):
    """Bridge status and ticksGame before and after the read. -> None when the read was paused and still, else the
    refusal reason. An unreadable pause flag or clock refuses: a guard that cannot see is not a pass. Pure."""
    for when, st in (("before", status0), ("after", status1)):
        paused = ((st or {}).get("state") or {}).get("paused") if isinstance(st, dict) else None
        if paused is not True:
            return "game not paused %s the read (paused=%r): a flyer read is a state read, never a flight" % (when, paused)
    if not isinstance(ticks0, int) or not isinstance(ticks1, int):
        return "ticksGame unreadable (before=%r, after=%r): cannot prove no tick passed" % (ticks0, ticks1)
    if ticks1 != ticks0:
        return "ticksGame moved %d -> %d during the read: readings void" % (ticks0, ticks1)
    return None


def _still(rb):
    return rb.call("rimbridge/get_bridge_status", {}), (rb.call("rimworld/get_game_info", {}) or {}).get("ticksGame")


def main():
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    import rimbridge_client as rc
    try:
        host, port, token = rc.resolve_endpoint(None, None, None, None)
        if not token:
            raise RuntimeError("no bridge token")
        rows = {}
        with rc.RimBridge(host, port, token, timeout=60) as rb:
            s0, t0 = _still(rb)
            why = paused_read_guard(s0, t0, s0, t0)
            if why:
                print("REFUSED: " + why)
                return 2
            info = rb.call("jawa/map_info", {})
            cx, cz = int(info["sizeX"]) // 2, int(info["sizeZ"]) // 2
            for j, k in enumerate(KINDS):
                rb.call("jawa/spawn_pawn", {"kindDef": k, "x": cx + 3 * j, "z": cz, "faction": "player", "count": 1})
                r = rb.call("jawa/pawn_flight", {"action": "report", "kind": k, "maxPawns": 5, "maintainTicks": 0, "unpause": False})
                rows[k] = [p for p in (r.get("pawns") or []) if isinstance(p, dict)]
                print(k, rows[k])
            s1, t1 = _still(rb)
            rb.call("jawa/destroy_bulk", {"filter": "playerAnimals", "dryRun": False})
            why = paused_read_guard(s0, t0, s1, t1)
            if why:
                print("REFUSED: " + why)
                return 2
    except Exception as e:  # noqa: BLE001 -- a bridge fault measures nothing about the mods
        print("UNMEASURED: bridge call failed: %s" % type(e).__name__)
        return 2
    code, line = verdict(rows)
    print(line)
    return code


if __name__ == "__main__":
    sys.exit(main())
