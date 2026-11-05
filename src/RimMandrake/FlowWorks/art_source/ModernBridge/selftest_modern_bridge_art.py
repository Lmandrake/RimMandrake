#!/usr/bin/env python3
"""Selftest for modern_bridge.py (MODERN_BRIDGE_REDRAW_BRIDGE_NOT_PLUMBING): Modern bridges carry no pipe colour.

Pins:
  - the check can see: plumbing_colour() fails a red-trim fixture and a waterworks-blue fixture, passes a grey one; the installed
    Modern pipe icon (the real blue) fails too;
  - repaint() takes the red fixture and every installed Modern bridge piece to a pass, never touches alpha, and is
    idempotent (a second pass moves under 1% of opaque pixels), so geometry fitted to the art cannot move;
  - wood, concrete and silver are left alone (a grey and a wood fixture come back unchanged);
  - the installed set (installed 2026-11-05 on the owner's item words) is REPORTED by default and HARD-CHECKED with
    MODERN_BRIDGE_INSTALLED=1: every piece AND deck atlas out of pipe red/blue, no pink red-highlight residue over 1%,
    the three FLAG polish rows of modern_bridge_sheet_2026-10-24 fixed by measurement (gate and tower carry the darker
    blue-grey accent; the leaf's long edge has accent rails that contrast with its core; the wreck has rust), and every
    installed picture judged ACCEPT by the art-eval pipeline (run ART_RUN's decisions.jsonl names its sha)."""
import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import modern_bridge as MB  # noqa: E402

REPO = HERE.parents[4]
ART_RUN = REPO / "infrastructure/state/art_eval/runs/modern_bridge_r4_20261105/decisions.jsonl"
ROWS = 7   # one art-eval subject per sheet row


def shares(im):
    """(accent share, rust share, pink residue share, core-minus-accent brightness) over opaque pixels."""
    a = np.asarray(im.convert("RGBA")).astype(float) / 255.0
    rgb, op = a[..., :3], a[..., 3] > 0.5
    mx, mn = rgb.max(-1), rgb.min(-1)
    s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0.0)
    deg = MB.WB._hue(rgb, mx, mn) * 360
    acc = op & (s >= 0.08) & (deg >= 190) & (deg <= 225) & (mx > 0.15)
    rust = op & (s >= 0.35) & (deg >= 20) & (deg <= 40) & (mx > 0.15)
    pink = op & (s > 0.12) & (np.minimum(deg, 360 - deg) < 14) & (mx > 0.2)
    rest = op & ~acc & (mx > 0.25)
    n = max(float(op.sum()), 1.0)
    con = float(mx[rest].mean() - mx[acc].mean()) if acc.any() and rest.any() else 0.0
    return acc.sum() / n, rust.sum() / n, pink.sum() / n, con


def installed_checks():
    """Hard checks on the installed set; returns a list of failures."""
    fails = []
    rels = MB.pieces() + [a for _, a in MB.atlas_jobs()]
    for rel in rels:
        im = Image.open(MB.TEX / rel)
        if not MB.is_bridge_coloured(im):
            fails.append(f"installed {rel} pipe-coloured {MB.plumbing_colour(im)}")
        if shares(im)[2] > MB.MAX_SHARE:
            fails.append(f"installed {rel} keeps pink red-highlight residue {shares(im)[2]:.3f}")
    named = {Path(r).name: r for r in rels}
    for stem in ("RM_SuspensionTower.png", "RM_DrawbridgeGate_Closed_Modern_south.png", "RM_DrawbridgeGate_Open_Modern_south.png"):
        a = shares(Image.open(MB.TEX / named[stem]))[0]
        if a < 0.20:
            fails.append(f"FLAG monotone: {stem} accent share {a:.3f} < 0.20")
    a, _, _, con = shares(Image.open(MB.TEX / named["RM_DrawbridgeLeafUp_Edge_Modern.png"]))
    if a < 0.20 or con < 0.15:
        fails.append(f"FLAG faint leaf edge: accent {a:.3f} (>= 0.20), contrast {con:.3f} (>= 0.15)")
    r = shares(Image.open(MB.TEX / named["RM_SuspensionWreck.png"]))[1]
    if r < 0.03:
        fails.append(f"FLAG flat wreck: rust share {r:.3f} < 0.03")
    if not ART_RUN.is_file():
        return fails + [f"no art-eval record {ART_RUN}"]
    recs = [json.loads(l) for l in ART_RUN.read_text().splitlines() if l.strip()]
    acc = {x["subject"] for x in recs if x.get("decision") == "ACCEPT"}
    if len(acc) < ROWS:
        fails.append(f"art-eval: {len(acc)}/{ROWS} rows ACCEPT in {ART_RUN.name}")
    judged = {v for x in recs if x.get("decision") == "ACCEPT" for v in (x.get("source_sha256") or {}).values()}
    facings = [rel for rel in MB.pieces() if hashlib.sha256((MB.TEX / rel).read_bytes()).hexdigest() in judged]
    if len(facings) < 15:   # the facing panels the run judged as files (south/east/north per row; variants are strips)
        fails.append(f"art-eval: only {len(facings)} installed pieces carry a judged sha: the run judged other bytes")
    return fails


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
    if os.environ.get("MODERN_BRIDGE_INSTALLED") == "1":
        fails += installed_checks()
    elif still_red:
        print("REPORT", f"installed Modern bridge pieces still pipe-coloured: {len(still_red)}/{len(rels)}")
    for f in fails:
        print("FAIL", f)
    print("ALL OK" if not fails else f"{len(fails)} FAIL")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
