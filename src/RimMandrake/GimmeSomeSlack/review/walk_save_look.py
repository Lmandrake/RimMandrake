"""walk_save_look.py -- load a walk save, read it and capture named rects of it; with --save, write a keeper save under a new name and leave the game
paused. python.exe, the bridge of the game held.

    python.exe src\\RimMandrake\\GimmeSomeSlack\\review\\walk_save_look.py <save|-> <out dir> [--save NEW_NAME] x,z,w,h:name ...
"-" reads the map that is up. Prints hostiles, the probe holes: over the map, the wall lamps that point into a wall, tick and paused. Exit 0 clean, 1 a read is
wrong, 2 could not load or read."""
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
GSS = os.path.dirname(HERE)
sys.path[:0] = [GSS, os.path.join(GSS, "northstar"), os.path.join(os.path.dirname(GSS), "Utils")]
import validation as V  # noqa: E402
import validation_aerial as VA  # noqa: E402
import scene_rows as S  # noqa: E402
from modcheck import reviewmap as RM  # noqa: E402


def main(a):
    save, out = a[0], a[1]
    new = a[a.index("--save") + 1] if "--save" in a else None
    rects = [x for x in a[2:] if ":" in x and "," in x]
    os.makedirs(out, exist_ok=True)
    B = VA.A()
    if save != "-":
        print("load", str(B.call("rimworld/load_game", saveName=save))[:200])
        for _ in range(60):
            time.sleep(2)
            try:
                r = B.probe("holes")
                if r.get("success") and r.get("ends"):
                    break
            except Exception as ex:  # noqa: BLE001 - the map is still loading
                print("waiting", type(ex).__name__)
    B.probe("rebuild")
    st, why = V.holes_verdict(B.probe("holes"))
    _, _, lamps = S._styles(B, (0, 0, 250, 250))
    bad = S.wall_lamp_points_verdict(lamps)
    info = B.call("jawa/map_info")
    print(json.dumps({"holes": [st, why], "wallLamps": sum(1 for l in lamps.values() if l.get("def") == "WallLamp"), "pointWrong": bad,
                      "map": {k: info.get(k) for k in ("ticksGame", "paused", "hostiles", "hostileCount", "sizeX")}}, default=str)[:2500])
    for r in rects:
        rc, n = r.rsplit(":", 1)
        rc = tuple(int(v) for v in rc.split(","))
        B.call("rimworld/jump_camera_to_cell", x=rc[0] + rc[2] // 2, z=rc[1] + rc[3] // 2)
        B.call("rimworld/set_camera_zoom", rootSize=max(4, rc[3] * 0.8))
        log = []
        d = V.shot(B, n, rc, log, pad=0, root=max(4, rc[3] * 0.8))
        if d and os.path.exists(str(d)):
            shutil.copy(str(d), os.path.join(out, n + ".png"))
            print("shot", n)
        else:
            print("no capture", n, log[-1:])
    if new:
        print(json.dumps(RM.save_keeper(B, new, saves=V.SAVES), default=str)[:500])
    return 2 if st == "UNMEASURED" or bad is None else 1 if st != "PASS" or bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
