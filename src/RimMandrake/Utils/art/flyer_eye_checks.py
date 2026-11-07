#!/usr/bin/env python3
"""flyer_eye_checks.py - READ-ONLY: the flip-book faults the owner's eye named on the FireHawk page, read from PNGs.

RIMMASTER_FIX_FIREHAWK_EAST_SHOWS_TWO_WINGS_AT_ONCE. Eight birds, his verdicts, and what each row reads on them:
skills/rimworld-sprite-facings/references/flyer_truth_set.md. None of these rows has been scored on a fresh sealed
batch, so a green here is a lead and his look stays the decision. flyer_cutout and flier_body_stabilize measure whether
the plate moved; these rows measure what they cannot, starting with what the plate contains.

Verbs:
  audit DIR --prefix P --n N [--head FACING=x0,y0,x1,y1 ...] [--ref K] [--axis X] [--config JSON] [--plate-out PNG]
        FRAMES   every frame of every facing exists
        HEAD     the head box on frame K (a person places it on the skull mass, never ears, horns or crests), found by
                 translation in every frame; RED over 1 px. No box is UNMEASURED, never a pass
        SIDES    north and south: pixels that move left of the body axis against right of it; RED under 0.5
                 (one wing frozen or missing)
        SQUASH   a cut-out config's side-view pose under |sy| 0.5: the resample skips source rows and the wing breaks up
        STATIC   the share of ink pixel-identical in every frame. --plate-out writes those pixels: look at it, it must
                 be a wingless body. It is a look, so it has no verdict
        HOLD     the engine holds the last frame double: which pose that is, and whether it is a stroke extreme. Advice
  parts CONFIG --src DIR --out PNG   the plate alone and each wing layer alone, per facing, on a colour neither uses. A
        wing in the plate (two wings at once) or body in a wing layer (flesh ripping away) shows here before any build

Exit: 0 no row RED, 1 a row RED, 2 bad input. UNMEASURED and advice rows do not change the exit.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import flyer_cutout as FC  # noqa: E402

FACINGS = ("north", "east", "south")
HEAD_PX = 1
SIDES_MIN = 0.5
SQUASH_MIN = 0.5
EXTREME_SHARE = 0.15      # a pose this close to the largest or smallest silhouette of the cycle counts as an extreme
CHANGED = 24              # a pixel moved if a channel differs by more than this between frames
SEARCH_PX = 64


def load_facing(folder: Path, prefix: str, n: int, facing: str):
    """The facing's frames as int16 RGBA arrays, or None for each file that does not exist."""
    out = []
    for i in range(1, n + 1):
        p = folder / f"{prefix}{i}_{facing}.png"
        out.append(np.asarray(Image.open(p).convert("RGBA")).astype(np.int16) if p.exists() else None)
    return out


def flat(a: np.ndarray) -> np.ndarray:
    """RGB over mid grey, so transparent reads as background rather than black."""
    al = a[..., 3:4] / 255.0
    return a[..., :3] * al + 120 * (1 - al)


def head_shift(frame: np.ndarray, ref: np.ndarray, box) -> tuple[int, int]:
    """Best (dx, dy) of the reference head box in FRAME, by summed difference over the box's opaque reference pixels."""
    x0, y0, x1, y1 = box
    t = flat(ref)[y0:y1, x0:x1]
    m = ref[y0:y1, x0:x1, 3] > 128
    im = flat(frame)
    h, w = im.shape[:2]
    best = None
    for dy in range(max(-SEARCH_PX, -y0), min(SEARCH_PX, h - y1) + 1):
        for dx in range(max(-SEARCH_PX, -x0), min(SEARCH_PX, w - x1) + 1):
            e = np.abs(im[y0 + dy:y1 + dy, x0 + dx:x1 + dx] - t)[m].sum()
            if best is None or e < best[0]:
                best = (e, dx, dy)
    return best[1], best[2]


def static_mask(frames: list[np.ndarray]) -> np.ndarray:
    st = frames[0][..., 3] > 128
    for a in frames[1:]:
        st = st & (np.abs(a - frames[0]).max(2) == 0)
    return st


def side_ratio(frames: list[np.ndarray], axis: int) -> tuple[int, int, float]:
    moved = np.zeros(frames[0].shape[:2], bool)
    for a in frames[1:]:
        moved |= np.abs(a - frames[0]).max(2) > CHANGED
    left, right = int(moved[:, :axis].sum()), int(moved[:, axis:].sum())
    return left, right, min(left, right) / max(left, right, 1)


def hold_row(frames: list[np.ndarray]) -> tuple[int, bool, list[int]]:
    ink = [int((a[..., 3] > 128).sum()) for a in frames]
    span = max(max(ink) - min(ink), 1)
    share = (ink[-1] - min(ink)) / span
    return len(frames), share <= EXTREME_SHARE or share >= 1 - EXTREME_SHARE, ink


def squash_rows(config: dict) -> list[str]:
    rows = []
    for facing, fc in config.get("facings", {}).items():
        for i, w in enumerate(fc.get("wings", [])):
            low = [(k + 1, p[2]) for k, p in enumerate(w.get("poses") or []) if len(p) > 2 and abs(p[2]) < SQUASH_MIN]
            if low:
                rows.append(f"{facing} wing {i}: " + ", ".join(f"frame {k} sy {s}" for k, s in low))
    return rows


def audit(a) -> int:
    folder = Path(a.dir)
    heads = {}
    for h in a.head or []:
        facing, _, box = h.partition("=")
        heads[facing] = tuple(int(v) for v in box.split(","))
    red = False
    plate_rows = []
    for facing in FACINGS:
        frames = load_facing(folder, a.prefix, a.n, facing)
        missing = [i + 1 for i, f in enumerate(frames) if f is None]
        if missing:
            print(f"FRAMES  {facing}: RED, missing frame {missing}")
            red = True
            continue
        print(f"FRAMES  {facing}: GREEN, {a.n} frames")
        if facing in heads:
            ref = frames[a.ref - 1]
            shifts = [head_shift(f, ref, heads[facing]) for f in frames]
            span = max(max(abs(dx - sx), abs(dy - sy)) for dx, dy in shifts for sx, sy in shifts)
            bad = span > HEAD_PX
            red |= bad
            print(f"HEAD    {facing}: {'RED' if bad else 'GREEN'}, span {span} px, shifts {shifts}")
        else:
            print(f"HEAD    {facing}: UNMEASURED, no --head box placed for this facing")
        if facing in ("north", "south"):
            axis = a.axis if a.axis is not None else frames[0].shape[1] // 2
            left, right, ratio = side_ratio(frames, axis)
            bad = ratio < SIDES_MIN
            red |= bad
            print(f"SIDES   {facing}: {'RED' if bad else 'GREEN'}, moved left {left} right {right} ratio {ratio:.2f}")
        st = static_mask(frames)
        print(f"STATIC  {facing}: {st.sum() / max(np.mean([(f[..., 3] > 128).sum() for f in frames]), 1):.2f} of ink")
        plate_rows.append((facing, frames[0], st))
        n, extreme, ink = hold_row(frames)
        print(f"HOLD    {facing}: frame {n} holds double, {'a stroke extreme' if extreme else 'mid-stroke: move an extreme to last'}, "
              f"ink per frame {ink}")
    if a.config:
        rows = squash_rows(json.loads(Path(a.config).read_text()))
        red |= bool(rows)
        print("SQUASH  " + ("RED, " + "; ".join(rows) if rows else "GREEN, no side-view pose under |sy| 0.5"))
    else:
        print("SQUASH  UNMEASURED, no --config")
    if a.plate_out and plate_rows:
        side = plate_rows[0][1].shape[1]
        sheet = Image.new("L", (side * len(plate_rows), side), 40)
        for k, (_, frame, st) in enumerate(plate_rows):
            sheet.paste(Image.fromarray((st * 255).astype(np.uint8)), (k * side, 0))
        sheet.save(a.plate_out)
        print(f"PLATE   wrote {a.plate_out}: it must show a wingless body")
    return 1 if red else 0


def parts(a) -> int:
    config = json.loads(Path(a.config).read_text())
    src = Path(a.src)
    rows = []
    for facing, fc in config["facings"].items():
        if "master" not in fc or not fc.get("wings"):
            continue
        master = np.asarray(Image.open(src / f"{config['prefix']}{fc['master']}_{facing}.png").convert("RGBA"))
        shape = master.shape[:2]
        protect = FC.poly_mask(shape, fc.get("protect"))
        layers = [FC.poly_mask(shape, [w["poly"]]) & ~protect for w in fc["wings"]]
        union = np.zeros(shape, bool)
        for m in layers:
            union |= m
        rows.append((facing, [("plate", ~union)] + [(f"wing {i}", m) for i, m in enumerate(layers)], master))
    if not rows:
        print("parts: no facing with a master and wings in this config", file=sys.stderr)
        return 2
    side = rows[0][2].shape[1]
    cols = max(len(r[1]) for r in rows)
    sheet = Image.new("RGB", (side * cols, side * len(rows)), (0, 110, 120))
    for y, (_, cuts, master) in enumerate(rows):
        for x, (_, mask) in enumerate(cuts):
            cut = master.copy()
            cut[~mask] = 0
            sheet.paste(Image.fromarray(cut), (x * side, y * side), Image.fromarray(cut[..., 3]))
    sheet.save(a.out)
    print(f"parts: wrote {a.out}: rows {[r[0] for r in rows]}, columns plate then each wing layer")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="verb", required=True)
    au = sub.add_parser("audit")
    au.add_argument("dir")
    au.add_argument("--prefix", required=True)
    au.add_argument("--n", type=int, required=True)
    au.add_argument("--head", action="append", help="FACING=x0,y0,x1,y1 on frame --ref")
    au.add_argument("--ref", type=int, default=1)
    au.add_argument("--axis", type=int)
    au.add_argument("--config")
    au.add_argument("--plate-out")
    pa = sub.add_parser("parts")
    pa.add_argument("config")
    pa.add_argument("--src", required=True)
    pa.add_argument("--out", required=True)
    a = ap.parse_args()
    return audit(a) if a.verb == "audit" else parts(a)


if __name__ == "__main__":
    sys.exit(main())
