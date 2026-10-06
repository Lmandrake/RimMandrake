"""Selftest on synthetic boards: every tier-(a) check must FIRE on its planted defect and stay QUIET on a
clean board (a check that cannot stay quiet is as useless as one that cannot fire).

    cd src/RimMandrake/Utils && python3 -m artboard.selftest
"""
import json
import os
import sys
import tempfile

import numpy as np
from PIL import Image, ImageDraw

if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from artboard import geometry, run as runmod  # noqa: E402
else:
    from . import geometry, run as runmod

PPC, WC, HC = 32, 14, 10
GROUND = (110, 80, 55)
COL = {"A": (200, 40, 30), "B": (40, 70, 200), "C": (50, 160, 60), "D": (220, 200, 40),
       "E1": (60, 60, 60), "E2": (90, 200, 210), "F": (230, 130, 30), "G": (130, 50, 170),
       "H": (30, 25, 20), "I": (235, 235, 235)}
FAM = {"A": "red", "B": "blue", "C": "green", "D": "yellow", "E1": "grey", "E2": "cyan", "F": "orange",
       "G": "purple", "H": "black", "I": "white"}
CELLS = {"A": (1, 7), "B": (4, 7), "C": (7, 7), "D": (10, 7), "E1": (1, 4), "E2": (4, 4), "F": (7, 4),
         "G": (10, 4), "H": (1, 1), "I": (4, 1)}


def px_box(x, z, inset=4):
    return [x * PPC + inset, (HC - z - 1) * PPC + inset, (x + 1) * PPC - inset, (HC - z) * PPC - inset]


def ground(seed=7):
    rng = np.random.default_rng(seed)
    a = np.array(GROUND, np.int16) + rng.integers(-10, 11, (HC * PPC, WC * PPC, 3))
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def render(defects):
    im = ground()
    d = ImageDraw.Draw(im)
    for sid, (x, z) in CELLS.items():
        colour = COL[sid]
        if sid in defects.get("swap", {}):
            colour = COL[defects["swap"][sid]]
        if sid in defects.get("magenta", ()):
            colour = (255, 0, 255)
        if sid in defects.get("empty", ()):
            continue
        if sid == "E2" and "identical" in defects:
            colour = COL["E1"]
        box = px_box(x, z)
        if sid in defects.get("overflow", ()):
            box = [box[0] - 22, box[1], box[2] + 22, box[3]]
        if sid == "H":                                  # a pit: square, organic=False
            d.rectangle(box, fill=colour)
            continue
        d.ellipse(box, fill=colour)
        if sid in defects.get("truncate", ()):          # cut the right half off at a straight edge
            mid = (box[0] + box[2]) // 2
            bg = ground().crop((mid + 1, box[1], box[2] + 1, box[3] + 1))
            im.paste(bg, (mid + 1, box[1]))
        if sid in defects.get("hole", ()):
            cx, cy = (box[0] + box[2]) // 2, (box[1] + box[3]) // 2
            hole = ground().crop((cx - 7, cy - 7, cx + 7, cy + 7))
            mask = Image.new("L", (14, 14), 0)
            ImageDraw.Draw(mask).ellipse([0, 0, 13, 13], fill=255)
            im.paste(hole, (cx - 7, cy - 7), mask)
    return im


def board(tmp, image, refs=False, plate=None):
    subs = []
    for sid, (x, z) in CELLS.items():
        s = {"id": sid, "cell": [x, z], "expect": {"colour": FAM[sid]}}
        if sid == "H":
            s["expect"]["organic"] = False
        if sid == "E2":
            s["differs_from"] = ["E1"]
        subs.append(s)
    b = {"image": image, "camera": {"ppc": PPC, "origin_px": [0, HC * PPC]}, "pad": 0.5, "subjects": subs}
    if plate:
        b["plate"] = plate
    p = os.path.join(tmp, image + ".json")
    json.dump(b, open(p, "w"))
    return p


def flags(rep):
    return {r["id"]: sorted({f["check"] for f in r["findings"]}) for r in rep["rows"] if r["findings"]}


def main():
    fails = []

    def expect(name, cond, got):
        print("%s  %s%s" % ("ok  " if cond else "FAIL", name, "" if cond else "  got %r" % (got,)))
        if not cond:
            fails.append(name)

    # geometry: markers fitted back to the camera mapping; a marker off by one cell shows as residual
    cam = geometry.mapping_from_board({"camera": {"ppc": PPC, "origin_px": [0, HC * PPC]}})
    mk = [{"cell": [x, z], "px": list(cam.world_to_px(x + .5, z + .5))} for x, z in ((1, 1), (10, 7), (4, 4))]
    fit = geometry.fit_markers(mk)
    expect("markers reproduce the camera mapping", abs(fit.ax - PPC) < 1e-6 and fit.residual_px < 1e-6,
           fit.to_json())
    mk[2]["px"][0] += PPC
    expect("a marker off by one cell shows a residual >= ppc/3", geometry.fit_markers(mk).residual_px > PPC / 3,
           geometry.fit_markers(mk).residual_px)

    with tempfile.TemporaryDirectory() as tmp:
        render({}).save(os.path.join(tmp, "clean.png"))
        ground().save(os.path.join(tmp, "plate.png"))
        rep = runmod.run(board(tmp, "clean.png"), os.path.join(tmp, "o_clean"))
        expect("clean board: zero findings (ring mode)", not flags(rep), flags(rep))
        runmod.approve(os.path.join(tmp, "o_clean"), list(CELLS), os.path.join(tmp, "refs"))

        defects = {"magenta": ["A"], "empty": ["B"], "swap": {"C": "D", "D": "C"}, "truncate": ["F"],
                   "overflow": ["G"], "identical": True, "hole": ["I"]}
        render(defects).save(os.path.join(tmp, "bad.png"))
        for mode, plate in (("ring", None), ("plate", "plate.png")):
            rep = runmod.run(board(tmp, "bad.png", plate=plate), os.path.join(tmp, "o_bad_" + mode),
                             ref_dir=os.path.join(tmp, "refs"))
            fl = flags(rep)
            expect("[%s] magenta cell -> MISSING_TEXTURE" % mode, "MISSING_TEXTURE" in fl.get("A", []), fl)
            expect("[%s] empty cell -> EMPTY" % mode, "EMPTY" in fl.get("B", []), fl.get("B"))
            expect("[%s] swapped cells -> WRONG_COLOUR + REF_DRIFT on both" % mode,
                   all({"WRONG_COLOUR", "REF_DRIFT"} <= set(fl.get(k, [])) for k in "CD"), (fl.get("C"), fl.get("D")))
            expect("[%s] cut-off sprite -> TRUNCATED" % mode, "TRUNCATED" in fl.get("F", []), fl.get("F"))
            expect("[%s] oversize sprite -> OVERFLOW" % mode, "OVERFLOW" in fl.get("G", []), fl.get("G"))
            expect("[%s] identical state pair -> IDENTICAL" % mode, "IDENTICAL" in fl.get("E2", []), fl.get("E2"))
            expect("[%s] holed sprite -> HOLE" % mode, "HOLE" in fl.get("I", []), fl.get("I"))
            expect("[%s] untouched controls stay quiet (H, E1)" % mode, "H" not in fl and "E1" not in fl, fl)
            expect("[%s] square pit not called TRUNCATED" % mode, "H" not in fl, fl.get("H"))
            key = json.load(open(os.path.join(tmp, "o_bad_" + mode, "vision_key.json")))
            expect("[%s] vision mosaic holds only tier-a survivors" % mode,
                   {t["id"] for t in key["tiles"]} == set(CELLS) - set(fl), [t["id"] for t in key["tiles"]])
            expect("[%s] report + boards written" % mode, all(os.path.exists(os.path.join(tmp, "o_bad_" + mode, f))
                   for f in ("report.json", "report.html", "owner_board.png", "vision_mosaic.png")), "missing")

        # geometry fault: a board whose camera is off the frame reports OUT_OF_FRAME, never a crash
        b = json.load(open(board(tmp, "clean.png")))
        b["camera"]["origin_px"] = [-200, HC * PPC]
        json.dump(b, open(os.path.join(tmp, "off.json"), "w"))
        rep = runmod.run(os.path.join(tmp, "off.json"), os.path.join(tmp, "o_off"))
        expect("off-frame geometry -> OUT_OF_FRAME", "OUT_OF_FRAME" in rep["by_check"], rep["by_check"])

    n = 2 + 1 + 2 * 11 + 1
    print("%d/%d passed" % (n - len(fails), n))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
