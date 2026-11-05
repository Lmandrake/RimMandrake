#!/usr/bin/env python3
"""selftest_weir_installed.py -- the weir looks as INSTALLED (WEIR_LOOKS_REDRAW_ONE_PER_PIPE_STYLE). Owner 2026-10-24 on the
weir_by_photo sheet: Scrapper / Industrial / Modern = the staged after art; Futuristic = "the futuristic_after_ew is
preferred as a geometric design. We should improve that design at better resolution and quality, not make it a single
flat wall. But it can be made of the same white metal and pale blue "lights" as the higher quality one."

Needs no git history (selftest_weir_looks.py covers the before/after story against the timber set):
  installed   Textures/RimMandrake/FlowWorks/Weir/<Look>/ == art_source/Weir/out_photo/<Look>/ pixel for pixel, all N_FILES
              (5 bodies/post + 4 facings x 12 crest-sheet frames per look, WEIR_SPILL_REDRAW_ANIMATED_NOT_PAINTED)
  parity      weir_by_photo.py regenerated into a temp dir == out_photo (the source is deterministic)
  checks      every fw_scenes_weir check of every look passes on the installed set (zigzag_crest: not a flat wall)
  futuristic  bodies and post at 2x (512x256, 256x512, 256x256); the wall is white metal (median opaque luminance of the
              body's wall, the dark bay floor aside, >= 180, low saturation), carries pale-blue light pixels (>= 2 % of the body), and a near-black keyline
  can-fail    each must FAIL: one installed file swapped for another look's; Futuristic recoloured mid-grey; Futuristic
              without its lights; Futuristic at 1x; Futuristic east flattened into one straight wall
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fw_scenes_weir as W  # noqa: E402

FW = HERE.parent
INSTALLED = FW / "Textures/RimMandrake/FlowWorks/Weir"
OUT_PHOTO = FW / "art_source/Weir/out_photo"
GEN = FW / "art_source/Weir/weir_by_photo.py"
N_FILES = len(W.LOOKS) * (len(W.SIZES) + len(W.FACINGS) * W.SPILL_FRAMES)
BODIES = ("RM_BankWeir_east", "RM_BankWeir_west", "RM_BankWeir_north", "RM_BankWeir_south")
fails = []


def check(name, ok, detail=""):
    print("%-4s %s %s" % ("PASS" if ok else "FAIL", name, detail))
    if not ok:
        fails.append(name)


def px(p):
    return np.asarray(Image.open(p).convert("RGBA"))


def same_set(a, b):
    """(n files in a, [names differing or missing in b, or present only in b])."""
    files = sorted(Path(a).glob("*/*.png"))
    extra = sorted(str(p.relative_to(b)) for look in W.LOOKS for p in (Path(b) / look).glob("*.png")   # the four looks
                   if not (Path(a) / p.relative_to(b)).is_file())                                   # (not WhiteWater/)
    diff = extra + [str(p.relative_to(a)) for p in files
            if not (Path(b) / p.relative_to(a)).is_file() or px(p).shape != px(Path(b) / p.relative_to(a)).shape
            or (px(p) != px(Path(b) / p.relative_to(a))).any()]
    return len(files), diff


def futuristic(d):
    """(ok, detail): 2x canvases, white metal, pale-blue lights, dark keyline."""
    d = Path(d) / "Futuristic"
    want = {n: (s[0] * 2, s[1] * 2) for n, s in W.SIZES.items() if not n.startswith("RM_BankWeirSpill")}
    bad = [n for n, s in want.items() if Image.open(d / (n + ".png")).size != s]
    lum, sat, blue, key = [], [], [], []
    for n in BODIES:
        a = px(d / (n + ".png")).astype(np.float32)
        m = a[..., 3] >= 128
        rgb = a[..., :3][m]
        # the wall, not the bays between its teeth: since WEIR_SPILL_REDRAW_ANIMATED_NOT_PAINTED the bays are a dark wet
        # floor (cool, lum < 120; the water over them is the animated crest sheet), not painted white water. The bar was
        # 200 over the whole body; that median leaned on the bright painted bay water (55 % of the opaque px): the wall
        # alone measured 186 on the art it was set on, so it is 180 on the wall (mid-grey 128 still fails)
        bay = (W._lum(rgb) < 120) & (rgb[:, 0] < 0.92 * rgb[:, 2]) & (W._lum(rgb) >= 50)
        lum.append(np.median(W._lum(rgb[~bay])))
        mx, mn = rgb.max(1), rgb.min(1)
        lb = (rgb[:, 2] > 170) & (rgb[:, 1] > 150) & (rgb[:, 0] < 140)          # pale blue / cyan light
        sat.append(float(np.median((mx - mn)[~lb] / np.maximum(mx[~lb], 1))))
        blue.append(float(lb.mean()))
        key.append(float((W._lum(rgb) < 70).mean()))
    ok = not bad and min(lum) >= 180 and max(sat) <= 0.12 and min(blue) >= 0.02 and min(key) >= 0.01
    return ok, ("wrong size %s; " % bad if bad else "2x canvases; ") + (
        "wall median lum %s (>= 180), grey sat %s (<= 0.12), light px %s (>= 0.02), keyline px %s (>= 0.01)"
        % ([round(x) for x in lum], [round(x, 3) for x in sat], [round(x, 3) for x in blue], [round(x, 3) for x in key]))


def all_checks(d):
    res = W.check_all(d)
    failed = ["%s %s" % (look, n) for look, rows in res.items() for n, ok, _ in rows if not ok]
    return not failed, failed


def mutate(d, rel, fn):
    p = Path(d) / rel
    a = px(p).copy()
    Image.fromarray(fn(a).astype(np.uint8), "RGBA").save(p)


def main():
    n, diff = same_set(OUT_PHOTO, INSTALLED)
    check("installed == out_photo", n == N_FILES and not diff, "%d files, differ: %s" % (n, diff))
    ok, failed = all_checks(INSTALLED)
    check("every fw_scenes_weir check passes on the installed set", ok, "failed: %s" % failed if failed else "")
    ok, det = futuristic(INSTALLED)
    check("Futuristic 2x white metal + pale-blue lights", ok, det)

    with tempfile.TemporaryDirectory() as tmp:
        gen = Path(tmp) / "regen"
        subprocess.run([sys.executable, str(GEN), "--out", str(gen)], check=True, capture_output=True)
        n, diff = same_set(OUT_PHOTO, gen)
        check("parity out_photo == weir_by_photo.py", n == N_FILES and not diff, "%d files, differ: %s" % (n, diff))

        def copy(tag):
            d = Path(tmp) / tag
            shutil.copytree(INSTALLED, d)
            return d

        d = copy("swap")
        shutil.copy(d / "Modern/RM_BankWeir_east.png", d / "Industrial/RM_BankWeir_east.png")
        check("can-fail installed == out_photo (Industrial east swapped for Modern)", bool(same_set(OUT_PHOTO, d)[1]))

        def grey(a):
            m = (a[..., 3] > 0)[..., None]
            return np.where(m, np.concatenate([np.full(a.shape[:2] + (3,), 128), a[..., 3:]], -1), a)

        def unlit(a):
            lb = (a[..., 2] > 170) & (a[..., 1] > 150) & (a[..., 0] < 140)
            a[lb, :3] = 225
            return a

        for tag, fn in (("grey", grey), ("unlit", unlit)):
            d = copy(tag)
            for b in BODIES:
                mutate(d, "Futuristic/%s.png" % b, fn)
            ok, det = futuristic(d)
            check("can-fail Futuristic palette (%s)" % tag, not ok, det)

        d = copy("onex")
        for p in (d / "Futuristic").glob("*.png"):
            im = Image.open(p)
            if im.size[0] > 128 or im.size[1] > 128:
                im.resize((im.size[0] // 2, im.size[1] // 2), Image.Resampling.BOX).save(p)
        ok, det = futuristic(d)
        check("can-fail Futuristic at 1x", not ok, det)

        def flat(a):
            t = W.top_edge(Image.fromarray(a))
            row = int(np.median(t[t >= 0]))
            return np.repeat(a[:, :1], a.shape[1], 1) * 0 + a[:, [int(np.argmin(np.abs(t - row)))]]

        d = copy("flat")
        mutate(d, "Futuristic/RM_BankWeir_east.png", flat)
        ok, det = W.zigzag_crest(d)
        check("can-fail zigzag_crest (Futuristic east as one straight wall)", not ok, det)

    print("%d FAIL" % len(fails) if fails else "ALL OK")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
