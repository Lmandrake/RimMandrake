#!/usr/bin/env python3
"""sc_rewire_cost: a 2000-cell conduit base with masts, then place, cut, dig beside, kill a mast, each alone and then ten at once. Prints the longest slice and whether the drawing caught up.

    python.exe ralph/live/rewire_cost.py [--fresh-map]

The bar is the scene's: max slice under 20 ms, and the touched edges current after. Bridge-side timing, so the time runs at speed 1 while each action settles.
"""
import argparse, json, os, sys, time
REPO = os.getcwd()
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "GimmeSomeSlack", "northstar_matrix"))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
import run_live as RL  # noqa: E402

X0, Z0, W, H = 90, 90, 62, 62


def conduit_cells():
    cells = set()
    for z in range(0, H, 2):
        for x in range(W):
            cells.add((x, z))
    for z in range(H):
        cells.add((0, z))
        cells.add((W - 1, z))
    return sorted(cells)


def settle(B, label, t0, rows, want_change=None):
    """Let the frame-sliced rebuild finish, then read the worst slice of the window this action opened."""
    B.call("rimworld/set_time_speed", speed=1)
    end, m, c = time.time() + 25, {}, {}
    while time.time() < end:
        time.sleep(0.7)
        m, c = B.probe("motion"), B.probe("census")
        if m.get("pending") == 0 and time.time() - t0 > 2.5:
            break
    B.call("rimworld/set_time_speed", speed=0)
    row = {"action": label, "maxSliceMs": m.get("winMaxSliceMs"), "pending": m.get("pending"), "cordEdges": c.get("cordEdges"), "builds": m.get("builds"), "wall_s": round(time.time() - t0, 1)}
    rows.append(row)
    print(json.dumps(row), flush=True)
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fresh-map", action="store_true")
    a = ap.parse_args()
    B = RL.LiveBridge()
    if a.fresh_map:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
        from await_lifecycle import await_lifecycle
        lc = await_lifecycle(B.call, "map_ready", 240, poll_s=0.5)
        if not lc.ok:
            raise SystemExit("no fresh map: %s" % lc.reason)
    B.call("rimworld/set_god_mode", enabled=True)
    B.call("jawa/research_bulk", mode="finish_all")
    B.call("jawa/storyteller_swap", difficultyDef="Peaceful")
    B.call("jawa/incident_queue_clear")
    B.call("jawa/set_fog", action="unfog", rect="0,0,250,250")
    rect = "%d,%d,%d,%d" % (X0 - 1, Z0 - 1, W + 2, H + 2)
    B.call("jawa/destroy_batch", rects=rect, categories="Plant,Item,Filth,Building")
    B.call("jawa/set_terrain_batch", ops="Concrete:%s" % rect)
    cells = conduit_cells()
    print("conduit cells", len(cells), flush=True)
    for i in range(0, len(cells), 300):
        r = B.call("jawa/build_batch", ops=";".join("PowerConduit:%d,%d" % (x + X0, z + Z0) for x, z in cells[i:i + 300]), wipeExisting=False)
        if r.get("survived") != len(cells[i:i + 300]):
            print("build", json.dumps(r)[:200])
    B.call("jawa/build_batch", ops="Battery:%d,%d,0" % (X0 + 5, Z0 - 2), wipeExisting=False)
    masts = []
    B.ap("set:autoLink=False")
    for k, (x, z) in enumerate(((W + 3, 5), (W + 3, 25), (W + 3, 45))):
        B.ap("place:RM_AerialMast:Modern:%d,%d:god" % (x + X0, z + Z0))
    B.ap("cprocess")
    B.ticks(2)
    B.ap("set:autoLink=True")
    ids = [q["id"] for q in B.ap("census").get("anchors") or []]
    for u, v in zip(ids, ids[1:]):
        B.ap("link:%d,%d" % (u, v))
    t0 = time.time()
    B.probe("rebuild")
    print("full rebuild took", round(time.time() - t0, 1), "s", json.dumps({k: v for k, v in B.probe("census").items() if k in ("conduitCells", "cordEdges", "strands")}), flush=True)
    rows = []

    def act(label, fn):
        B.probe("slicereset")
        t = time.time()
        fn()
        return settle(B, label, t, rows)

    def place(n, base):
        B.call("jawa/build_batch", ops=";".join("PowerConduit:%d,%d" % (X0 + base + 3 * i, Z0 + 1) for i in range(n)), wipeExisting=False)

    def cut(n, base):
        B.call("jawa/destroy_batch", rects=";".join("%d,%d,1,1" % (X0 + base + 3 * i, Z0 + 20) for i in range(n)), categories="Building")

    def dig(n, base):
        B.call("jawa/build_batch", ops=";".join("Wall:%d,%d" % (X0 + base + 3 * i, Z0 + 31) for i in range(n)), stuff="BlocksGranite", wipeExisting=False)

    act("idle window", lambda: None)
    act("place one", lambda: place(1, 10))
    act("place ten", lambda: place(10, 20))
    act("cut one", lambda: cut(1, 10))
    act("cut ten", lambda: cut(10, 20))
    act("wall beside one", lambda: dig(1, 10))
    act("wall beside ten", lambda: dig(10, 20))
    if ids:
        act("kill a mast", lambda: B.call("jawa/destroy_batch", rects="%d,%d,1,1" % (X0 + W + 3, Z0 + 25), categories="Building"))
    worst = max((r["maxSliceMs"] or 0) for r in rows)
    late = [r["action"] for r in rows if r["pending"] != 0]
    print("WORST slice %.1f ms (bar 20); not caught up: %s" % (worst, late), flush=True)


if __name__ == "__main__":
    main()
