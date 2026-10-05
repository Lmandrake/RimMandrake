"""pole_shots.py -- screenshot the aerial pole stations (7-10) in every look through the bridge, for eyeballing pole art.

    python.exe src/RimMandrake/GimmeSomeSlack/pole_shots.py [OUTDIR]     # default D:\\Luke\\dev\\_rmscratch\\mc_poles
Per look x station: one station frame (rect_of(s,2)) and one close-up on the first mast (16x6 cells, zoomed to root size 11).
Needs the review map built (human_review.py --build). Leaves the style on the LAST look in LOOKS_ORDER.
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import human_review as HR  # noqa: E402
import run_live as RL  # noqa: E402

LOOKS_ORDER = ["StarWars", "StarWarsJawa", "ExtensionCord", "Cybertek"]


def main(argv):
    out = argv[0] if argv else "D:\\Luke\\dev\\_rmscratch\\mc_poles"
    os.makedirs(out, exist_ok=True)
    S = HR.station_list()
    R = HR.Review(RL.LiveBridge(), None)
    for style in LOOKS_ORDER:
        R.B.probe("set:style=%s" % style)
        time.sleep(1.5)
        for n in (7, 8, 9, 10):
            s = next(s for s in S if s["n"] == n)
            mx, mz = HR.g(s, s["masts"][0][1])
            rects = {"st": HR.rect_of(s, 2), "m0": (mx - 2, mz - 1, 16, 6)}
            for k, r in rects.items():
                R.B.call("jawa/clear_ui", all=True)
                R.B.call("rimworld/frame_cell_rect", x=r[0], z=r[1], width=r[2], height=r[3], paddingCells=1)
                time.sleep(3.0)
                name = "pole_%s_s%d_%s" % (style, n, k)
                res = R.B.call("rimworld/screenshot_cell_rect", x=r[0], z=r[1], width=r[2], height=r[3], paddingCells=1, fileName=name, rootSize=11 if k == "m0" else 24)
                res["filePath"] = res.get("filePath") or res.get("path") or res.get("savedPath")
                src = res.get("filePath")
                for _ in range(10):
                    if src and os.path.exists(src):
                        break
                    time.sleep(0.5)
                shutil.copyfile(src, os.path.join(out, name + ".png"))
                print(name)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
