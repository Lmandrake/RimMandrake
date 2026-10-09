#!/usr/bin/env python3
"""flyer_plate_from_master.py — derive a flyer's wingless body PLATE from the accepted flying master.

Sketto option A (Transient/sketto_repose_fix_2026-10-09.md). A separately drawn plate is ~1 px off the
frames everywhere, so the lock's silhouette gate fails on outline jitter. Here the plate is built FROM the
master the frames were edited from, so plate and frames align by construction:
  1. align the leg-donor plate to the master (flyer_lock.align, translation only);
  2. TRUNK = donor silhouette opened by --open px (drops legs/ear and tusk tips); LEGS = donor pixels farther
     than 1 px from the trunk;
  3. REGION = trunk dilated --grow px; body = master pixels with alpha > 128 inside REGION (wings outside it
     are masked out deterministically);
  4. donor legs not already covered are pasted over (donor RGBA, aligned).
Pure numpy, no randomness. Usage:
  flyer_plate_from_master.py --master M.png --donor D.png --out PLATE.png [--open 2] [--grow 2] [--report R.json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import flyer_lock as FL  # noqa: E402

OPEN, GROW = 2, 2


def erode(m):
    o = m.copy()
    o[1:] &= m[:-1]; o[:-1] &= m[1:]; o[:, 1:] &= m[:, :-1]; o[:, :-1] &= m[:, 1:]
    o[0] = o[-1] = False; o[:, 0] = o[:, -1] = False
    return o


def dilate(m):
    o = m.copy()
    o[1:] |= m[:-1]; o[:-1] |= m[1:]; o[:, 1:] |= m[:, :-1]; o[:, :-1] |= m[:, 1:]
    return o


def opening(m, k):
    o = m.copy()
    for _ in range(k):
        o = erode(o)
    for _ in range(k):
        o = dilate(o)
    return o & m


def derive(master, donor, open_r=OPEN, grow=GROW, search=8):
    """Return (plate RGBA int16, info)."""
    dx, dy = FL.align(donor, master, search)
    d = FL.shift(donor, -dx, -dy)
    ds = d[..., 3] > FL.OPAQUE
    trunk = opening(ds, open_r)
    legs = ds & ~dilate(trunk)
    reg = trunk
    for _ in range(grow):
        reg = dilate(reg)
    body = reg & (master[..., 3] > FL.OPAQUE)
    plate = np.where(body[..., None], master, 0)
    paste = legs & ~body
    plate = np.where(paste[..., None], d, plate).astype(np.int16)
    n = int((plate[..., 3] > FL.OPAQUE).sum())
    return plate, {"shift": [dx, dy], "trunk_px": int(trunk.sum()), "legs_pasted_px": int(paste.sum()),
                   "plate_px": n, "open": open_r, "grow": grow}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--master", required=True, type=Path)
    ap.add_argument("--donor", required=True, type=Path, help="redrawn plate whose thin legs are kept")
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--open", type=int, default=OPEN)
    ap.add_argument("--grow", type=int, default=GROW)
    ap.add_argument("--search", type=int, default=8)
    ap.add_argument("--report", type=Path)
    a = ap.parse_args(argv)
    m, d = FL.load(a.master), FL.load(a.donor)
    if m.shape != d.shape:
        print("size mismatch", file=sys.stderr)
        return 2
    plate, info = derive(m, d, a.open, a.grow, a.search)
    FL.save(plate, a.out)
    if a.report:
        a.report.write_text(json.dumps(info, indent=1))
    print(json.dumps(info))
    return 0


if __name__ == "__main__":
    sys.exit(main())
