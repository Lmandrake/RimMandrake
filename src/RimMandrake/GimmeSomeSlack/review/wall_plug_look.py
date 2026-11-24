"""wall_plug_look.py -- wall plugs on every wall face, zoomed (RIMMANDRAKE_STRAIGHTEN_SLACK_CORD_WHERE_IT_LEAVES_WALL_PLUG_HE_SAW_IT_LIVE; the
owner's sighting of 2026-11-23). python.exe, the bridge of the game held, tier gimmesomeslack.

    python.exe src\\RimMandrake\\GimmeSomeSlack\\review\\wall_plug_look.py [--new] <out dir>

--new starts a debug map first. Four walls, one a side of a room; a Modern cord outside each, and beyond the wall a far-side wall lamp, a heater
against the wall and a heater two cells off it. Reads the probe joins: on the site, then one close capture a stand. Exit 0: joins clean and
every capture taken; 1: a join off; 2: could not stage or capture."""
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GSS = os.path.dirname(HERE)
sys.path[:0] = [GSS, os.path.join(GSS, "northstar"), os.path.join(os.path.dirname(GSS), "Utils")]
import validation as V  # noqa: E402
import validation_aerial as VA  # noqa: E402
import scene_rows as S  # noqa: E402

CX, CZ, H = 60, 60, 9          # the walled square's middle and half-side; the cord runs one cell outside each wall
SITE = (CX - H - 6, CZ - H - 6, 2 * H + 13, 2 * H + 13)
# name, the way from the cord into the wall (dx, dz), the rotation a wall lamp on the inner face looks (its wall is behind it)
FACES = [("cord_south_of_wall", (0, 1), 2), ("cord_west_of_wall", (1, 0), 3), ("cord_north_of_wall", (0, -1), 0), ("cord_east_of_wall", (-1, 0), 1)]


def at(into, along, deep):
    """deep 0 = the wall of that side, -1 = the cord outside it, +1 = inside."""
    dx, dz = into
    return CX - dx * (H - deep) + dz * along, CZ - dz * (H - deep) + dx * along


def stage(B):
    S.SITE = SITE
    S._site(B, V)
    out = {}
    for name, into, rot in FACES:
        wall = [at(into, k, 0) for k in range(-H, H + 1)]
        cord = [at(into, k, -2) for k in range(-H + 2, H - 1)]
        B.call("jawa/build_batch", ops=V.ops("Wall", wall), stuff="Steel", faction="player", wipeExisting=False)
        out[name] = B.ap("cline:PowerConduit:Modern:%d,%d:%d,%d:god" % (cord[0] + cord[-1])).get("success")
        B.call("jawa/build_batch", ops="Battery:%d,%d,0" % at(into, -H + 1, -2), faction="player", wipeExisting=False)
        lamp, near, far = at(into, -5, 1), at(into, 0, 1), at(into, 5, 2)
        B.call("jawa/build_batch", ops="WallLamp:%d,%d,%d;Heater:%d,%d,0;Heater:%d,%d,0" % (lamp + (rot,) + near + far), faction="player", wipeExisting=False)
    B.call("jawa/map_commit")
    B.ticks(3)
    S._fill(B, SITE)
    B.ap("cprocess")
    B.probe("rebuild")
    B.ticks(3)
    return out


def main(argv):
    out_dir = argv[-1]
    os.makedirs(out_dir, exist_ok=True)
    B = VA.A()
    if "--new" in argv:
        print(str(B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000))[:160])
    staged = stage(B)
    r = B.probe("joins:%d,%d,%d,%d" % SITE)
    print(json.dumps({"staged": staged, "joins": {k: r.get(k) for k in ("success", "taken", "offLine", "offSlope", "empty", "byKind", "bad", "error")}}, default=str))
    B.call("jawa/clear_ui")
    got = 0
    for name, into, _ in FACES:
        for along in (-5, 0, 5):
            x, z = at(into, along, 0)
            log = []
            B.call("rimworld/jump_camera_to_cell", x=x, z=z)
            B.call("rimworld/set_camera_zoom", rootSize=5)
            n = "plug_%s_%+d" % (name, along)
            d = V.shot(B, n, (x - 3, z - 3, 7, 7), log, pad=0, root=5)
            if d and os.path.exists(str(d)):
                shutil.copy(str(d), os.path.join(out_dir, n + ".png"))
                got += 1
            else:
                print("no capture", n, log[-1:])
    print("captures", got, "in", out_dir)
    if not r.get("success") or got < 12 or not r.get("taken"):
        return 2
    return 1 if r.get("offLine") or r.get("offSlope") or r.get("empty") else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
