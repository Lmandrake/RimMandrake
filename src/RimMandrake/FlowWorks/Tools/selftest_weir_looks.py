#!/usr/bin/env python3
"""selftest_weir_looks.py -- the weir looks redraw (WEIR_LOOKS_REDRAW_ONE_PER_PIPE_STYLE; owner 2026-10-24: "Weirs by look:
scavver/crude, industrial, modern, futuristic.") as permanent offline checks on fw_scenes_weir.py.

  BEFORE  the timber set the owner was looking at, read from git at TIMBER_SHA (the installed Weir/<Look>/ textures there):
          every look's identity check (rubble_not_timber, three_steps, smooth_no_red, zigzag_crest) must FAIL on it,
          and so must spill_no_white_bar (its flat white crest lip, the judge's "thin bright white line" over the water)
  AFTER   art_source/Weir/out_photo (weir_by_photo.py's committed output): every check of every look must PASS
  parity  weir_by_photo.py regenerated into a temp dir == out_photo pixel for pixel (the source is deterministic)
  can-fail (each must FAIL, so no check passes vacuously):
          north_ends_drawn    the v5 wrap band re-created: Industrial north art's last 16 rows darkened 25 %
          zigzag_crest        Futuristic north art resampled to 3.5 teeth a cell (v5's N-S period, 73 rows)
          seamless            Modern east art with its right-hand column made transparent
          south_mirrors_north Scrapper south art == north art, not mirrored
          spill_fitted        Industrial east crest sheet lifted 24 rows above the body band
          spill_no_white_bar  Modern east crest sheet with one near-opaque white row painted across it
          identity checks     a blank (transparent) set for each look
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

TIMBER_SHA = "024e3d8002"      # last commit with the timber weir set installed
FW = HERE.parent
OUT_PHOTO = FW / "art_source/Weir/out_photo"
GEN = FW / "art_source/Weir/weir_by_photo.py"
fails = []


def check(name, ok, detail=""):
    print("%-4s %s %s" % ("PASS" if ok else "FAIL", name, detail))
    if not ok:
        fails.append(name)


def timber_dir(tmp):
    root = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, text=True,
                          check=True).stdout.strip()
    rel = (FW / "Textures/RimMandrake/FlowWorks/Weir").relative_to(root).as_posix()
    d = Path(tmp) / "timber"
    for look in W.LOOKS:
        (d / look).mkdir(parents=True)
        for n in W.SIZES:
            blob = subprocess.run(["git", "show", "%s:%s/%s/%s.png" % (TIMBER_SHA, rel, look, n)], cwd=root,
                                  capture_output=True, check=True).stdout
            (d / look / (n + ".png")).write_bytes(blob)
    return d


def copy_set(src, tmp, tag):
    d = Path(tmp) / tag
    shutil.copytree(src, d)
    return d


def rows_of(d, look, name):
    return dict((n, (ok, det)) for n, ok, det in W.check_all(d)[look])[name]


def mutate(d, look, name, fn):
    p = Path(d) / look / (name + ".png")
    a = np.asarray(Image.open(p).convert("RGBA")).copy()
    Image.fromarray(fn(a).astype(np.uint8), "RGBA").save(p)


def main():
    with tempfile.TemporaryDirectory() as tmp:
        before = timber_dir(tmp)
        res = W.check_all(before)
        for look in W.LOOKS:
            idn = W.IDENTITY[look].__name__
            ok, det = dict((n, (o, t)) for n, o, t in res[look])[idn]
            check("before %s %s FAILS" % (look, idn), not ok, det)
            ok, det = dict((n, (o, t)) for n, o, t in res[look])["spill_no_white_bar"]
            check("before %s spill_no_white_bar FAILS" % look, not ok, det)

        res = W.check_all(OUT_PHOTO)
        for look in W.LOOKS:
            for n, ok, det in res[look]:
                check("after %s %s" % (look, n), ok, det)

        gen = Path(tmp) / "regen"
        subprocess.run([sys.executable, str(GEN), "--out", str(gen)], check=True, capture_output=True)
        diff = [str(p.relative_to(OUT_PHOTO)) for p in sorted(OUT_PHOTO.glob("*/*.png"))
                if not (np.asarray(Image.open(p)) == np.asarray(Image.open(gen / p.relative_to(OUT_PHOTO)))).all()]
        n = len(list(OUT_PHOTO.glob("*/*.png")))
        check("parity out_photo == weir_by_photo.py", n == 36 and not diff, "%d files, differ: %s" % (n, diff))

        def darken_end(a):
            a[-16:, :, :3] = a[-16:, :, :3] * 0.75
            return a

        def teeth_3_5(a):
            return a[(np.arange(a.shape[0]) * 64 // 73) % a.shape[0]]

        def cut_right(a):
            a[:, -1, 3] = 0
            return a

        def lift(a):
            return np.roll(a, -24, axis=0)

        def white_row(a):
            a[60, :] = (245, 245, 245, 160)
            return a

        cases = [("spill_no_white_bar", "Modern", "RM_BankWeirSpill_east", white_row),
                 ("north_ends_drawn", "Industrial", "RM_BankWeir_north", darken_end),
                 ("zigzag_crest", "Futuristic", "RM_BankWeir_north", teeth_3_5),
                 ("seamless", "Modern", "RM_BankWeir_east", cut_right),
                 ("spill_fitted", "Industrial", "RM_BankWeirSpill_east", lift)]
        for i, (chk, look, name, fn) in enumerate(cases):
            d = copy_set(OUT_PHOTO, tmp, "cf%d" % i)
            mutate(d, look, name, fn)
            ok, det = rows_of(d, look, chk)
            check("can-fail %s (%s %s mutated)" % (chk, look, name), not ok, det)

        d = copy_set(OUT_PHOTO, tmp, "cf_mirror")
        shutil.copy(d / "Scrapper/RM_BankWeir_north.png", d / "Scrapper/RM_BankWeir_south.png")
        ok, det = rows_of(d, "Scrapper", "south_mirrors_north")
        check("can-fail south_mirrors_north (south == north)", not ok, det)

        d = copy_set(OUT_PHOTO, tmp, "cf_blank")
        for p in d.glob("*/*.png"):
            Image.new("RGBA", Image.open(p).size, (0, 0, 0, 0)).save(p)
        for look in W.LOOKS:
            try:
                ok, det = W.IDENTITY[look](d)
            except Exception as e:      # a check that crashes on blank art has not passed it
                ok, det = False, "raised %s" % type(e).__name__
            check("can-fail %s on a blank set" % W.IDENTITY[look].__name__, not ok, det)

    print("%d FAIL" % len(fails) if fails else "ALL OK")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
