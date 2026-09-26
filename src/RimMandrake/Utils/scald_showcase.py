"""Stage the Scald showcase on the CURRENT map in one invocation.

The Scald BiomeDef is impassable deep water, so it has no map of its own: this
paints a shore-to-deep strip of Scald terrain on whatever map is loaded (a
scratch save, never the campaign) and lays the kit out along it for a walk-
through review:

    margin  (RUT_ScaldMargin)     catch items in a labelled row + crowncarpet
    shallows(RUT_ScaldWaterShallow) vents, a steam-catch on one vent, three wrecks,
                                  the floor cast (noohm, shulla) spawned wild
    deep    (RUT_ScaldWaterDeep / OceanDeep)  visual only

Then unfog, midday, clear UI, frame, shoot clear + RUT_ScaldSteam, and save.

    python.exe scald_showcase.py --at 40,40 --shot scald_showcase --save SCALD_REVIEW
    python.exe scald_showcase.py --find            # print the best open rect and stop

--at      lower-left cell of the 44x28 strip (omit with --find to auto-pick)
--find    scan the map for the most open, unroofed strip away from colonists
--shot    screenshot base name (writes <shot>_clear and <shot>_steam)
--save    keeper save name; the file is stat-ed afterwards, never trusted

The floor cast only appears here because it is spawned by hand: in play it has
no reachable home until dive maps exist (SEA_DIVE_MAPS_BUILD_1).
"""
import argparse
import sys
import time

from stage_review import connect, pause, kill_hostiles, face, shoot, save_game

W, H = 44, 28
CATCH = ["RM_Saal", "RM_ShullaCatch", "RM_BladderboilCatch", "RM_Eesh", "RM_Muddal",
         "RM_Karrash", "RM_Doss", "RM_Thuum", "RM_Ekkel", "RM_Deepfire"]
CAST = [("RM_Noohm", 3), ("RM_Shulla", 3)]


def rect_score(rb, x, z):
    bad = 0
    for dz in range(0, H, 14):
        cells = rb.call("rimworld/get_cells_info",
                        {"x": x, "z": z + dz, "width": W, "height": min(14, H - dz)}).get("cells", [])
        for c in cells:
            if c.get("roofDefName") or c.get("solidThingDefs") or not c.get("walkable"):
                bad += 1
    return bad


def find_rect(rb):
    info = rb.call("jawa/map_info", {})
    sx, sz = info["sizeX"], info["sizeZ"]
    colon = [(p.get("x"), p.get("z")) for p in rb.call("jawa/list_pawns", {"limit": 300}).get("pawns", [])
             if p.get("faction") in ("PlayerColony", "Player") or p.get("isColonist")]
    best = None
    for x in range(10, sx - W - 10, 30):
        for z in range(10, sz - H - 10, 30):
            if any(cx is not None and x - 15 <= cx <= x + W + 15 and z - 15 <= cz <= z + H + 15
                   for cx, cz in colon):
                continue
            s = rect_score(rb, x, z)
            if best is None or s < best[0]:
                best = (s, x, z)
            if s == 0:
                return best
    return best


def paint(rb, x0, z0):
    ops = ";".join([
        "RUT_ScaldMargin:%d,%d,%d,%d" % (x0, z0, W, 8),
        "RUT_ScaldWaterShallow:%d,%d,%d,%d" % (x0, z0 + 8, W, 11),
        "RUT_ScaldWaterDeep:%d,%d,%d,%d" % (x0, z0 + 19, W, 5),
        "RUT_ScaldWaterOceanDeep:%d,%d,%d,%d" % (x0, z0 + 24, W, 4),
    ])
    return rb.call("jawa/set_terrain_batch", {"ops": ops, "refresh": True})


def place(rb, x0, z0):
    out = []
    def spawn(d, x, z, n=1):
        try:
            r = rb.call("rimworld/spawn_thing", {"defName": d, "x": x, "z": z, "stackCount": n})
            out.append((d, x, z, r.get("success", True)))
        except Exception as e:
            out.append((d, x, z, "ERR " + str(e)[:80]))
    for i, d in enumerate(CATCH):
        spawn(d, x0 + 3 + i * 4, z0 + 3, 10 if d == "RM_Deepfire" else 5)
    for i in range(6):
        spawn("RM_Crowncarpet", x0 + 4 + i * 6, z0 + 6)
    spawn("RUT_ScaldVent", x0 + 6, z0 + 12)
    spawn("RUT_ScaldVent", x0 + 14, z0 + 12)
    spawn("RUT_SteamCatch", x0 + 14, z0 + 12)
    for i, w in enumerate(("RUT_ScaldWreckHull", "RUT_ScaldWreckTank", "RUT_ScaldWreckFrame")):
        spawn(w, x0 + 22 + i * 7, z0 + 12)
    for i, (k, n) in enumerate(CAST):
        for j in range(n):
            try:
                rb.call("jawa/spawn_pawn", {"kindDef": k, "x": x0 + 8 + i * 10 + j * 3, "z": z0 + 16,
                                             "faction": "none"})
                out.append((k, x0 + 8 + i * 10 + j * 3, z0 + 16, True))
            except Exception as e:
                out.append((k, None, None, "ERR " + str(e)[:80]))
    return out


def census(rb, x0, z0):
    got = {}
    cells = []
    for dz in range(0, 20, 14):
        cells += rb.call("rimworld/get_cells_info",
                         {"x": x0, "z": z0 + dz, "width": W, "height": 14}).get("cells", [])
    for c in cells:
        for t in c.get("things", []):
            d = t.get("defName") or t.get("def")
            if d:
                got[d] = got.get(d, 0) + 1
    return got


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--at")
    ap.add_argument("--find", action="store_true")
    ap.add_argument("--shot", default="scald_showcase")
    ap.add_argument("--save")
    a = ap.parse_args()
    rb = connect()
    try:
        print("paused:", pause(rb))
        if a.find or not a.at:
            best = find_rect(rb)
            print("best rect (blocked cells, x, z):", best)
            if a.find:
                return 0
            x0, z0 = best[1], best[2]
        else:
            x0, z0 = [int(v) for v in a.at.split(",")]
        print("hostiles:", kill_hostiles(rb))
        print("clear:", rb.call("jawa/destroy_batch",
                                {"rects": "%d,%d,%d,%d" % (x0, z0, W, H), "category": "All"}).get("destroyed"))
        print("paint:", paint(rb, x0, z0).get("success"))
        for row in place(rb, x0, z0):
            print("  place", row)
        print("face:", face(rb, "south"))
        got = census(rb, x0, z0)
        want = set(CATCH) | {"RM_Crowncarpet", "RUT_ScaldVent", "RUT_SteamCatch", "RUT_ScaldWreckHull",
                             "RUT_ScaldWreckTank", "RUT_ScaldWreckFrame", "RM_Noohm", "RM_Shulla"}
        print("census:", {d: got.get(d, 0) for d in sorted(want)})
        tk = rb.call("rimworld/get_game_info", {}).get("ticksGame")
        rb.call("jawa/time_set_ticks", {"ticks": (tk // 60000) * 60000 + 60000 + 12 * 2500})
        rb.call("jawa/weather_set", {"weather": "Clear", "lockWeather": True})
        frame = "%d,%d,%d,%d" % (x0, z0, W, H)
        print("shot clear:", shoot(rb, frame, a.shot + "_clear"))
        rb.call("jawa/weather_set", {"weather": "RUT_ScaldSteam", "lockWeather": True})
        time.sleep(2.0)
        print("shot steam:", shoot(rb, frame, a.shot + "_steam"))
        if a.save:
            print("save:", save_game(rb, a.save))
        print("rect:", frame)
    finally:
        rb.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
