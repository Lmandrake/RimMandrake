#!/usr/bin/env python3
"""Selftest for modern_bridge.py (MODERN_BRIDGE_REDRAW_BRIDGE_NOT_PLUMBING): Modern bridges carry no pipe colour.

Pins:
  - the check can see: plumbing_colour() fails a red-trim fixture and a waterworks-blue fixture, passes a grey one; the installed
    Modern pipe icon (the real blue) fails too;
  - repaint() takes the red fixture and every installed Modern bridge piece to a pass, never touches alpha, and is
    idempotent (a second pass moves under 1% of opaque pixels), so geometry fitted to the art cannot move;
  - wood, concrete and silver are left alone (a grey and a wood fixture come back unchanged);
  - the installed set is REPORTED, not failed: the red art is owner-kept until he rules on the repaint sheet
    (Transient/biome_ffar/modern_bridge_sheet_<date>.html). Once installed, the installed set must pass: set
    MODERN_BRIDGE_INSTALLED=1 in the environment to make the report a hard check."""
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import modern_bridge as MB  # noqa: E402


def fixture(trim_rgb, body_rgb=(185, 185, 182), n=64):
    a = np.zeros((n, n, 4), np.uint8)
    a[8:56, 8:56, :3] = body_rgb
    a[8:56, 8:16, :3] = trim_rgb
    a[8:56, 48:56, :3] = [int(c * 0.7) for c in trim_rgb]   # shaded side of the trim
    a[8:56, 8:56, 3] = 255
    return Image.fromarray(a, "RGBA")


def main():
    fails = []
    red, blue, grey, wood = (fixture((200, 32, 28)), fixture((150, 190, 214)), fixture((120, 124, 128)),
                             fixture((150, 102, 60), body_rgb=(170, 120, 72)))
    if MB.is_bridge_coloured(red):
        fails.append(f"check blind: red fixture passes {MB.plumbing_colour(red)}")
    if MB.is_bridge_coloured(blue):
        fails.append(f"check blind: blue fixture passes {MB.plumbing_colour(blue)}")
    if not MB.is_bridge_coloured(grey):
        fails.append(f"check too strict: grey fixture fails {MB.plumbing_colour(grey)}")
    pipe = MB.TEX / "RimMandrake/FlowWorks/Pipe/Modern/UniversalPipe_MenuIcon.png"   # the real waterworks blue
    if pipe.is_file() and MB.is_bridge_coloured(Image.open(pipe)):
        fails.append(f"check blind: the installed Modern pipe icon passes {MB.plumbing_colour(Image.open(pipe))}")
    out, _ = MB.repaint(red, "red")
    if not MB.is_bridge_coloured(out):
        fails.append(f"repaint leaves the red fixture pipe-coloured {MB.plumbing_colour(out)}")
    for name, im in (("grey", grey), ("wood", wood)):
        out, _ = MB.repaint(im, name)
        d = np.abs(np.asarray(out, int) - np.asarray(im, int)).max()
        if d > 2:
            fails.append(f"repaint moved the {name} fixture (max diff {d})")

    rels = MB.pieces()
    if len(rels) < 30:
        fails.append(f"only {len(rels)} Modern bridge pieces found (expected the 41-piece set): path drift?")
    still_red = []
    for rel in rels:
        im = Image.open(MB.TEX / rel).convert("RGBA")
        out, _ = MB.repaint(im, rel)
        if not MB.is_bridge_coloured(out):
            fails.append(f"{rel}: repaint still pipe-coloured {MB.plumbing_colour(out)}")
        if not np.array_equal(np.asarray(out)[..., 3], np.asarray(im)[..., 3]):
            fails.append(f"{rel}: repaint changed alpha")
        again, _ = MB.repaint(out, rel)
        op = np.asarray(im)[..., 3] > 128
        moved = (np.abs(np.asarray(again, int) - np.asarray(out, int))[..., :3].max(-1) > 2) & op
        if moved.sum() > 0.01 * op.sum():   # half-weighted edge pixels may move (<1%); a wood field may not (was 25% at 16..34 deg)
            fails.append(f"{rel}: repaint not idempotent ({int(moved.sum())}/{int(op.sum())} opaque px move on a 2nd pass)")
        if not MB.is_bridge_coloured(im):
            still_red.append(rel)
    if still_red:
        msg = f"installed Modern bridge pieces still pipe-coloured: {len(still_red)}/{len(rels)} (owner-kept, sheet pending)"
        if os.environ.get("MODERN_BRIDGE_INSTALLED") == "1":
            fails.append(msg)
        else:
            print("REPORT", msg)
    for f in fails:
        print("FAIL", f)
    print("ALL OK" if not fails else f"{len(fails)} FAIL")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
