#!/usr/bin/env python3
"""selftest_flyer_cutout.py - the cut-out rebuild must hold the body byte-identical and move only the wings.

Fixture (in memory): a 64x64 canvas, a 10x30 body block (protected) and a 24x6 wing to its right, hinged at the
body's edge. Four poses (+30, 0, -30, 0 degrees).
  BODY      every frame equals the plate on every solid body pixel (plate_identical 1.0)
  WINGS     the wing pixels differ between the up and down poses (the animation is not a no-op)
  DIRECTION sign +1, +30 deg moves the wing tip UP (smaller y) - counter-clockwise on screen
  SQUASH    sy -0.5 swings a wing above the hinge row to below it
  FALLOFF   with a falloff the wing pixel touching the body stays put while the tip still moves
  NEG       a frame with the body shifted 2 px is caught by plate_identical < 1 (the check can fail)
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import flyer_cutout as C  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print(("ok   " if cond else "FAIL ") + name + (f"  {detail}" if detail else ""))
    if not cond:
        FAILS.append(name)


def master():
    a = np.zeros((64, 64, 4), np.uint8)
    a[17:47, 22:32] = (120, 80, 40, 255)      # body
    a[29:35, 32:56] = (200, 200, 90, 255)     # wing, right of the body
    return a


FC = {"master": 1, "order": "under", "falloff": 0,
      "protect": [[[22, 17], [32, 17], [32, 47], [22, 47]]],
      "wings": [{"poly": [[32, 20], [64, 20], [64, 44], [32, 44]], "hinge": [32, 32], "sign": 1,
                 "poses": [[30, 1.0], [0, 1.0], [-30, 1.0], [0, 1.0]]}]}


def tip_y(fr):
    ys, xs = np.nonzero(fr[..., 3] > 128)
    right = xs >= 50
    return float(ys[right].mean()) if right.any() else float("nan")


def main() -> int:
    m = master()
    frames, plate, covers = C.compose_facing(m, FC, 4)
    check("BODY plate identical", C.plate_identical(frames, plate, covers) == 1.0)
    check("WINGS move", not np.array_equal(frames[0], frames[2]))
    check("DIRECTION +deg is up", tip_y(frames[0]) < tip_y(frames[1]) < tip_y(frames[2]),
          f"tip y {tip_y(frames[0]):.1f} / {tip_y(frames[1]):.1f} / {tip_y(frames[2]):.1f}")
    up = np.zeros((64, 64, 4), np.uint8)
    up[10:30, 30:34] = 255
    sq = C.turn(up, (32, 32), 0, 1.0, -0.5)
    ys, _ = np.nonzero(sq[..., 3] > 128)
    check("SQUASH below hinge", len(ys) and ys.min() > 32, f"rows {ys.min() if len(ys) else None}..")
    body = np.zeros((64, 64), bool)
    body[17:47, 22:32] = True
    wing = np.where((np.arange(64)[None, :, None] >= 32) & (m[..., 3:4] > 0), m, 0).astype(np.uint8)
    b = C.bend(wing, body, (32, 32), 30, 1.0, 1.0, 12)
    check("FALLOFF root stays", b[31, 32, 3] > 128 and b[31, 33, 3] > 128)
    check("FALLOFF tip moves", tip_y(b) < 31.0, f"tip y {tip_y(b):.1f}")
    bad = [f.copy() for f in frames]
    bad[2] = np.roll(bad[2], 2, axis=1)
    check("NEG shifted body caught", C.plate_identical(bad, plate, covers) < 1.0)
    print("FAIL" if FAILS else "PASS", "selftest_flyer_cutout", FAILS or "")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
