"""wall_lamps_holes_look.py -- every wall lamp look on every wall face, and a cord into a wall plate and a rock hole on every face, zoomed
(RIMMANDRAKE_FIX_SLACK_WALL_LAMPS_FACE_INTO_WALL_CORDS_STOP_AT_HOLE; the owner's walk of 2026-11-24, stations 33 and 12). python.exe, the bridge
of the game held, tier gimmesomeslack or gimmesomeslack_walk.

    python.exe src\\RimMandrake\\GimmeSomeSlack\\review\\wall_lamps_holes_look.py [--new] <out dir>

--new loads the clean saved site `calm` first. A walled square and a rock square; outside each face one cord per look, with its wall lamp on the face (the
wall square) and a heater inside the far side, so the cord dives in through a plate or a hole. Reads the probes holes: and cstyles on the site, then one
close capture per look and face. Exit 0: every read clean and every capture taken; 1: a read is wrong; 2: could not stage or capture."""
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GSS = os.path.dirname(HERE)
sys.path[:0] = [GSS, os.path.join(GSS, "northstar"), os.path.join(os.path.dirname(GSS), "Utils"), os.path.join(os.path.dirname(GSS), "Utils", "modcheck")]
import validation as V  # noqa: E402
import validation_aerial as VA  # noqa: E402
import scene_rows as S  # noqa: E402

H = 11                          # half-side of each square
SQUARES = [("wall", 50, 60), ("rock", 90, 60)]
# the face a cord meets (named for the side it looks to), the way into the wall, a wall lamp's rotation there (the side its wall is on)
FACES = [("south_face", (0, 1), 0), ("west_face", (1, 0), 1), ("north_face", (0, -1), 2), ("east_face", (-1, 0), 3)]
ALONG = (-8, -3, 2, 7)          # one look each
SITE = (50 - H - 6, 60 - H - 6, (90 - 50) + 2 * H + 13, 2 * H + 13)


def at(sq, into, along, deep):
    """deep 0 = the wall of that face, -1 = the open cell outside it, +1 = inside."""
    _, cx, cz = sq
    dx, dz = into
    return cx - dx * (H - deep) + dz * along, cz - dz * (H - deep) + dx * along


def stage(B):
    S.SITE = SITE
    S._site(B, V)
    out, lamps = {}, {}
    for sq in SQUARES:
        wall = sorted({at(sq, into, k, 0) for _, into, _ in FACES for k in range(-H, H + 1)})
        if sq[0] == "wall":
            B.call("jawa/build_batch", ops=V.ops("Wall", wall), stuff="Steel", faction="player", wipeExisting=False)
        else:
            B.call("jawa/build_batch", ops=V.ops("Granite", wall), wipeExisting=False)
        B.call("jawa/map_commit")
        for name, into, rot in FACES:
            for a, look in zip(ALONG, S.LOOK_NAMES):
                c = [at(sq, into, a + k, -3) for k in (0, 1)]
                out["%s %s %s" % (sq[0], name, look)] = B.ap("cline:PowerConduit:%s:%d,%d:%d,%d:god" % (({"Modern": "Modern_Orange"}.get(look, look),) + c[0] + c[1])).get("success")
                b, heat, lamp = at(sq, into, a - (2 if into == (1, 0) else 1), -3), at(sq, into, a + 2, 1), at(sq, into, a, -1)
                B.call("jawa/build_batch", ops="Battery:%d,%d,0;Heater:%d,%d,0" % (b + heat), faction="player", wipeExisting=False)
                if sq[0] == "wall":
                    B.call("jawa/build_batch", ops="WallLamp:%d,%d,%d" % (lamp + (rot,)), faction="player", wipeExisting=False)
                    lamps[lamp] = look
    B.call("jawa/map_commit")
    B.ticks(3)
    for c, look in lamps.items():
        out["lamp %s" % (c,)] = B.ap("clamp:%d,%d:%s" % (c + (look,))).get("success")
    S._fill(B, SITE)
    B.ap("cprocess")
    B.probe("rebuild")
    B.ticks(250)                # the lamps and heaters take their power in: the no-power bolt would cover each lamp (first live run)
    S._fill(B, SITE)
    return out, lamps


def main(argv):
    out_dir = argv[-1]
    os.makedirs(out_dir, exist_ok=True)
    B = VA.A()
    if "--new" in argv:
        import test_site_saves  # Utils/modcheck
        print("site:", str(test_site_saves.load_site(B.call, "calm"))[:200])
    staged, want = stage(B)
    failed = sorted(k for k, v in staged.items() if not v)
    h = B.probe("holes:%d,%d,%d,%d" % SITE)
    _, _, lamps = S._styles(B, SITE)
    mine = {c: lamps.get(c) or {} for c in want}
    bad_look = S.wall_lamp_verdict(mine, want)
    bad_out = S.wall_lamp_points_verdict(lamps)
    st_h, why = V.holes_verdict(h)
    print(json.dumps({"stagedFailed": failed, "holes": [st_h, why], "lampLooksWrong": bad_look, "lampsPointWrong": bad_out, "lamps": len(want)}, default=str))
    B.call("jawa/clear_ui")
    got = 0
    for sq in SQUARES:
        for name, into, _ in FACES:
            for a, look in zip(ALONG, S.LOOK_NAMES):
                x, z = at(sq, into, a + 1, -1)
                n = "%s_%s_%s" % (sq[0], name, look)
                B.call("rimworld/jump_camera_to_cell", x=x, z=z)
                B.call("rimworld/set_camera_zoom", rootSize=4)
                log = []
                d = V.shot(B, n, (x - 2, z - 2, 5, 5), log, pad=0, root=4)
                if d and os.path.exists(str(d)):
                    shutil.copy(str(d), os.path.join(out_dir, n + ".png"))
                    got += 1
                else:
                    print("no capture", n, log[-1:])
    n = len(SQUARES) * len(FACES) * len(ALONG)
    print("captures", got, "of", n, "in", out_dir)
    if failed or got < n or st_h == "UNMEASURED" or bad_out is None:
        return 2
    return 1 if st_h != "PASS" or bad_look or bad_out else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
