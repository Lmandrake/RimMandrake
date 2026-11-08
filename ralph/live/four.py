"""four.py -- the four offline-closed fixes of 682e7b4e72, seen live on game A (run with python.exe from the repo root on Steve).

  python.exe ralph/live/four.py [--big 30] [--deck 20] [--save fw4_four] [--skip-maps]

On the current (quick-test) map, east of the colonists: a big dug hole (big x big at 2 m) with a deck of pit covers over a
deck x deck part of it; the pit-cover scan timed (COVER_SCAN_TAME_QUADRATIC_ID_MINIMA); a save and reload with the cliff mask's
full rebuild timed (CLIFF_MASK_TAME_PER_CELL_SCRATCH); then a second map with its own pit, and the per-map derive count read
on both (TRENCH_STRIDE_FIX_CROSS_MAP_INVALIDATION). Every result line starts with RESULT.
"""
import argparse
import json
import sys
import time

import fwb

CLIFF = "RimMandrake.FlowWorks.RM_CliffMask"
COVER = "RimMandrake.FlowWorks.Pits.RM_PitCoverUtility"


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def proof(B, typ, method, arg="read"):
    # static_call passes NO argument for an empty string: every probe here takes one
    r = B.call("jawa/static_call", type=typ, method=method, args=arg or "read") or {}
    return str(r.get("result") or r.get("message") or r.get("error") or r)


def centre(B):
    cen = B.call("jawa/pawn_census", faction="player") or {}
    cols = [p for p in cen.get("pawns") or [] if p.get("isColonist")]
    return sum(p["x"] for p in cols) // len(cols), sum(p["z"] for p in cols) // len(cols)


def dig_square(B, x0, z0, w, h, levels):
    B.call("jawa/clear_area", rect="%d,%d,%d,%d" % (x0, z0, w, h), dryRun=False)
    t = time.time()
    for x in range(x0, x0 + w):
        for z in range(z0, z0 + h):
            B.call("jawa/flowworks_excavation_drive", x=x, z=z, deepenLevels=levels, setFill=-1)
    log("dug %dx%d at %d,%d to %d notches in %.0f s" % (w, h, x0, z0, levels, time.time() - t))


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--big", type=int, default=30)
    ap.add_argument("--deck", type=int, default=20)
    ap.add_argument("--save", default="fw4_four")
    ap.add_argument("--skip-maps", action="store_true")
    ap.add_argument("--reuse", action="store_true", help="the hole and deck are already there: reload the save first")
    a = ap.parse_args()
    B = fwb.FW()
    B.call("rimworld/set_time_speed", speed="Paused")
    if a.reuse:
        r = B.call("rimworld/load_game_ready", saveName=a.save, readiness="playable", pauseIfNeeded=True, timeoutMs=240000) or {}
        log("reuse load", json.dumps(r, default=str)[:160])
        time.sleep(3)
    mx, mz = centre(B)
    mi = B.call("jawa/map_info") or {}
    size = mi.get("size") or mi.get("mapSize") or {}
    log("map", json.dumps({k: mi.get(k) for k in ("uniqueID", "mapId", "tile", "size", "biome") if k in mi}, default=str))
    x0, z0 = mx + 12, mz - a.big // 2
    log("RESULT cliff before dig:", proof(B, CLIFF, "ProofCliffTiming", "reset"))
    if not a.reuse:
        dig_square(B, x0, z0, a.big, a.big, 4)
    B.step(30)
    log("RESULT cliff after dig:", proof(B, CLIFF, "ProofCliffTiming", ""))
    # the deck: covers over the middle of the hole
    dx0, dz0 = x0 + (a.big - a.deck) // 2, z0 + (a.big - a.deck) // 2
    ops = ";".join("RM_PitCover_WovenScrap:%d,%d" % (x, z) for x in range(dx0, dx0 + a.deck) for z in range(dz0, dz0 + a.deck))
    r = {} if a.reuse else B.call("jawa/build_batch", ops=ops, stuff="WoodLog", faction="player", readBack=0) or {}
    log("deck", {k: r.get(k) for k in ("success", "placed", "survived", "message") if k in r})
    B.step(30)
    for i in range(3):
        log("RESULT coverscan %d:" % i, proof(B, COVER, "ProofCoverScan", ""))
    B.shot("fw4_bigdeck", x0 - 1, z0 - 1, a.big + 2, a.big + 2, root=40)
    # save and reload: the full cliff-mask rebuild of a big hole on load
    log("RESULT cliff reset before reload:", proof(B, CLIFF, "ProofCliffTiming", "reset"))
    r = B.call("rimworld/save_game", saveName=a.save) or {}
    log("save", json.dumps(r, default=str)[:200])
    time.sleep(3)
    t = time.time()
    r = B.call("rimworld/load_game_ready", saveName=a.save, readiness="playable", pauseIfNeeded=True, timeoutMs=240000) or {}
    log("load", "%.1f s" % (time.time() - t), json.dumps(r, default=str)[:300])
    time.sleep(3)
    B.call("rimworld/set_time_speed", speed="Paused")
    log("RESULT cliff after reload:", proof(B, CLIFF, "ProofCliffTiming", ""))
    B.step(60)
    log("RESULT cliff after reload+60:", proof(B, CLIFF, "ProofCliffTiming", ""))
    log("RESULT coverscan after reload:", proof(B, COVER, "ProofCoverScan", ""))
    if a.skip_maps:
        return
    # a second map with its own pit; per-map derive counts on both
    mi = B.call("jawa/map_info") or {}
    tileA = mi.get("tile")
    idA = mi.get("uniqueID") if mi.get("uniqueID") is not None else mi.get("mapId")
    log("map A", tileA, idA)
    a0 = proof(B, CLIFF, "ProofCliffTiming", "")
    log("RESULT A before:", a0)
    idB = None
    for dt in (1, -1, 2, -2, 3, -3, 5, -5, 8, 13, 21, 34):
        if tileA is None:
            break
        r = B.call("jawa/world_tile_map_generate", tile=int(tileA) + dt, sizeX=150, sizeZ=150) or {}
        log("gen tile", int(tileA) + dt, json.dumps(r, default=str)[:300])
        idB = r.get("mapId") if r.get("mapId") is not None else r.get("uniqueID")
        if r.get("success") and idB is not None:
            break
        idB = None
    if idB is None:
        log("RESULT maps: no second map")
        return
    B.call("jawa/set_current_map", mapId=idB)
    time.sleep(2)
    log("RESULT B fresh:", proof(B, CLIFF, "ProofCliffTiming", ""))
    dig_square(B, 70, 70, 4, 4, 8)
    B.step(30)
    log("RESULT B after its pit:", proof(B, CLIFF, "ProofCliffTiming", ""))
    dig_square(B, 80, 70, 3, 3, 8)
    B.step(30)
    log("RESULT B after a second pit:", proof(B, CLIFF, "ProofCliffTiming", ""))
    B.call("jawa/set_current_map", mapId=idA)
    time.sleep(2)
    log("RESULT A after B's digs:", proof(B, CLIFF, "ProofCliffTiming", ""))
    B.step(30)
    log("RESULT A after 30 ticks:", proof(B, CLIFF, "ProofCliffTiming", ""))


if __name__ == "__main__":
    main()
