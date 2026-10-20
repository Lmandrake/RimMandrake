#!/usr/bin/env python3
"""selftest_fit_head_canvas.py — the head envelope check and fit (fit_head_canvas.py + head_envelope.json).

Part 1, synthetic heads: an in-envelope head passes; a wide side profile, a blank facing (UNMEASURED, never a
pass) and a trunk hanging below the chin are caught; fit clamps an over-wide head into the envelope with one
scale; the legacy argv form still runs. Part 2, a SANITY PROBE on shipped art: the Mimbanese side profile the
owner called "far too wide" (2026-10-20) is flagged, so the instrument can see the defect it was built for.
"""
import os
import sys
import tempfile

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fit_head_canvas as F  # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
FAILS = []


def check(cond, msg, detail=""):
    print(("PASS " if cond else "FAIL ") + msg + ("" if cond else f"  [{str(detail)[:400]}]"))
    if not cond:
        FAILS.append(msg)


def head(path, w_frac, h_frac, cx=0.5, bottom=0.70, canvas=512):
    im = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    if w_frac:
        w, h = w_frac * canvas, h_frac * canvas
        x0, y1 = cx * canvas - w / 2, bottom * canvas
        ImageDraw.Draw(im).ellipse((x0, y1 - h, x0 + w - 1, y1 - 1), fill=(200, 150, 120, 255))
    im.save(path)


def rules(viol):
    return {(f, r) for f, r, _, _ in viol}


env = F.load_envelope()
van = env["vanilla"]
check(all(f in van and 0.3 < van[f]["w"] < 0.45 and 0.35 < van[f]["h"] < 0.45 for f in F.FACINGS),
      "envelope carries measured vanilla extents for all three facings", van)

with tempfile.TemporaryDirectory() as td:
    good = os.path.join(td, "Good")
    os.makedirs(good)
    for f in F.FACINGS:
        head(os.path.join(good, f"Good_Head_{f}.png"), van[f]["w"] * 1.05, van[f]["h"] * 1.05, bottom=van[f]["b"])
    _, ext = F.measure_dir(good)
    viol, _ = F.judge(ext, env, "Good")
    check(not viol, "a head 5% over vanilla on every facing passes", viol)

    wide = os.path.join(td, "Wide")
    os.makedirs(wide)
    for f in F.FACINGS:
        k = 1.5 if f == "east" else 1.0
        head(os.path.join(wide, f"Wide_Head_{f}.png"), van["south"]["w"] * k, van[f]["h"], bottom=van[f]["b"])
    # the mask a CutoutComplex head ships must not be taken for a facing
    Image.new("RGBA", (512, 512), (0, 0, 0, 255)).save(os.path.join(wide, "Wide_Head_eastm.png"))
    _, ext = F.measure_dir(wide)
    r = rules(F.judge(ext, env, "Wide")[0])
    check(("east", "side profile wider than front") in r and ("east", "too wide") in r,
          "a 1.5x-wide side profile is flagged (and the _eastm mask is skipped)", r)

    blank = os.path.join(td, "Blank")
    os.makedirs(blank)
    head(os.path.join(blank, "Blank_Head_south.png"), van["south"]["w"], van["south"]["h"], bottom=van["south"]["b"])
    head(os.path.join(blank, "Blank_Head_east.png"), 0, 0)
    _, ext = F.measure_dir(blank)
    r = rules(F.judge(ext, env, "Blank")[0])
    check(("east", "UNMEASURED") in r and ("north", "UNMEASURED") in r,
          "blank and missing facings are UNMEASURED, never passed", r)

    trunk = os.path.join(td, "Trunk")
    os.makedirs(trunk)
    for f in F.FACINGS:
        b = van[f]["b"] + (0.08 if f == "east" else 0)
        head(os.path.join(trunk, f"Trunk_Head_{f}.png"), van[f]["w"], van[f]["h"], bottom=b)
    _, ext = F.measure_dir(trunk)
    check(("east", "hangs below vanilla chin") in rules(F.judge(ext, env, "Trunk")[0]),
          "a facing hanging below the vanilla chin is flagged")

    src = os.path.join(td, "Src")
    os.makedirs(src)
    paths = []
    for f in F.FACINGS:
        p = os.path.join(src, f"big_{f}.png")
        head(p, 0.80, 0.60, bottom=0.95)       # a full-canvas render, much too wide
        paths.append(p)
    out = os.path.join(td, "out")
    rc = F.main(["fit", "--stem", "Big_Head", "--out", out] + paths)
    _, ext = F.measure_dir(out)
    viol, rows = F.judge(ext, env, "Big")
    check(rc == 0 and not viol, "fit clamps an over-wide render inside the envelope", (rc, viol))
    check(all(rows[f]["w_ratio"] <= env["limits"]["width_ratio_max"] + 0.01 for f in F.FACINGS),
          "fit honours width_ratio_max", rows)

    out2 = os.path.join(td, "legacy")
    rc = F.main(["--target-h", "240", "--stem", "L", "--out", out2] + paths)
    check(rc == 0 and len(os.listdir(out2)) == 3, "legacy argv (no subcommand) still fits", os.listdir(out2))

mimb = os.path.join(REPO, "src/RimStarWars/StarWarsRaces/Textures/RimMandrakeSW/Heads/Mimbanese")
if os.path.isdir(mimb):
    _, ext = F.measure_dir(mimb)
    check(("east", "side profile wider than front") in rules(F.judge(ext, env, "Mimbanese")[0]),
          "SANITY: the shipped Mimbanese side profile is flagged too wide")
else:
    print("UNMEASURED sanity probe: Mimbanese head dir absent")

print(f"{'FAIL' if FAILS else 'OK'}: {len(FAILS)} failure(s)")
sys.exit(1 if FAILS else 0)
