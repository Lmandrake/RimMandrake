#!/usr/bin/env python3
"""GSS_JUNCTION_REDRAW_BODY_WIDER_THAN_CORD: the Modern (ExtCord, five colours) and Futuristic (Cybertek) T/X junction
PNGs have compact housings and cable necks that match the cord where the cord meets them.

Drawn at CordBuilder.JunctionScale = 1.15 cells per 128 px canvas over a strand SectionLayer_RM_MessyCords.StrandWidth
= 0.08 cells wide. Checked per PNG:
  * port mask unchanged: an arm tip at every port the shipped art had (T: left, right, bottom; X: all four) at the
    recorded centre (+-3 px), and nothing at the T's top;
  * neck: the opaque width 2 px inside each port tip is within 20% of the 0.08-cell strand;
  * compact: along each arm axis, the span of the part thicker than 0.12 cell (1.5 strands: housing and sleeves,
    not the necks) is at most 0.75 cell (the shipped art: ~1.15, sleeves running to the canvas edge).
Pure offline PNG measurement. Exit 0 PASS, 1 FAIL.
"""
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
STYLES = os.path.join(HERE, "Textures", "RimMandrake", "GimmeSomeSlack", "Styles")
SCALE_CELLS, PX, STRAND = 1.15, 128, 0.08
CELL_PER_PX = SCALE_CELLS / PX
FOLDERS = ["ExtCord", "ExtCord/Blue", "ExtCord/Brown", "ExtCord/Green", "ExtCord/Yellow", "Cybertek"]
# meeting point (x, y image px) and arm tips (direction, tip coordinate along it) measured on the shipped art
# Round 3 (owner 2026-11-08 5:18 PM: "I think you still have wires printed into static graphic textures ... Just stop that approach entirely"):
# the necks stop at the tuck radius, 0.44 canvas from the meeting point (the code's cord ends under them at CordBuilder.ArmTuck 0.40);
# no cable runs on to the canvas edge any more (gss_sitting tools/r3_install.py cut them; ralph/live/lab_r3_checks.py baked_stub).
SLOTS = {"Junction_T": ((63.5, 44.5), {"left": 8, "right": 119, "bottom": 100}, ["top"]),
         "Junction_X": ((63.5, 63.5), {"left": 8, "right": 119, "top": 8, "bottom": 119}, [])}
ALPHA = 40


def opaque(im, x, y):
    return im.getpixel((x, y))[3] > ALPHA


def run_across(im, axis_h, at):
    """Opaque pixels on the line perpendicular to an arm: (first, last) or None. axis_h: arm runs horizontally."""
    n = im.height if axis_h else im.width
    hits = [i for i in range(n) if (opaque(im, at, i) if axis_h else opaque(im, i, at))]
    return (hits[0], hits[-1]) if hits else None


def check(path, slot):
    fails = []
    im = Image.open(path).convert("RGBA")
    (mx, my), tips, absent = SLOTS[slot]
    for side, tip in tips.items():
        h = side in ("left", "right")
        inward = 2 if side in ("left", "top") else -2
        # an arm reaches the shipped tip; the T's bottom arm does not run past it
        step = 1 if side in ("left", "top") else -1
        r_tip = next((run_across(im, h, tip + step * k) for k in range(3) if run_across(im, h, tip + step * k)), None)
        if r_tip is None:  # within 2 px of the shipped tip (the shipped Cybertek arms stop 1 px short of the edge)
            fails.append(f"{side}: no arm tip at {tip}")
            continue
        if tip == SLOTS["Junction_T"][1]["bottom"] and slot == "Junction_T" and any(run_across(im, False, y) is not None for y in range(tip + 3, PX)):
            fails.append(f"{side}: art runs past the shipped tip {tip}")
        r = run_across(im, h, tip + inward)
        if r is None:   # an opaque tip with nothing 2 px in is a failed neck, not a crash of the whole checker
            fails.append(f"{side}: no arm {abs(inward)} px inside the tip {tip}")
            continue
        centre = (r[0] + r[1]) / 2
        want = my if h else mx
        if abs(centre - want) > 3:
            fails.append(f"{side}: port centre {centre:.1f} px, shipped {want}")
        w = (r[1] - r[0] + 1) * CELL_PER_PX
        if abs(w - STRAND) > 0.2 * STRAND:
            fails.append(f"{side}: neck {w:.3f} cell vs strand {STRAND} (+-20%)")
    for side in absent:
        # the shipped T's housing top is row 17: an arm upward would reach rows 0-10
        if any(run_across(im, False, y) is not None for y in range(0, 11)):
            fails.append(f"{side}: a port the T never had")
    # compactness: along each arm axis, how far the thick (>1.5 strands) part reaches
    thick = 1.5 * STRAND / CELL_PER_PX
    for h in (True, False):
        thick_at = []
        for at in range(PX):
            r = run_across(im, h, at)
            if r and r[1] - r[0] + 1 > thick:
                thick_at.append(at)
        span = (thick_at[-1] - thick_at[0] + 1) * CELL_PER_PX if thick_at else 0
        if span > 0.75:
            fails.append(f"{'horizontal' if h else 'vertical'} body span {span:.2f} cell > 0.75")
    return fails


def main():
    bad = 0
    n = 0
    for folder in FOLDERS:
        for slot in SLOTS:
            p = os.path.join(STYLES, folder, slot + ".png")
            n += 1
            fails = check(p, slot)
            print(("FAIL " if fails else "PASS ") + folder + "/" + slot + (": " + "; ".join(fails) if fails else ""))
            bad += bool(fails)
    print(f"{n - bad}/{n} junction PNGs pass")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
