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
        SQUASH   a cut-out config's side-view pose under |sy| 0.5 in a facing without `"area": true`: point sampling
                 skips source rows and the wing breaks up. With area on, the pose is area-sampled and reads GREEN
        STATIC   the share of ink pixel-identical in every frame. --plate-out writes those pixels: look at it, it must
                 be a wingless body. It is a look, so it has no verdict
        HOLD     the engine holds the last frame double: which pose that is, and whether it is a stroke extreme. Advice
  alias CONFIG [--src DIR] [--facing F]   each wing pose under |sy| 0.5 as the bake draws it against a reference that reads every
        source row (REF_ROWS sub-rows per output row, its own sampler): the mean premultiplied RGB error on the wing's
        ink. RED over ALIAS_MAX. The owner's FireHawk east ("static-like noise", 2026-11-07) read 34 here; frames he
        called good read under 4. BAKED: a facing with `"area": true` and a recorded `"source"` ({"path", "rev", "pad"})
        must hold exactly the area bake of that source, or it is RED. A facing whose master frame is not in DIR is UNMEASURED (exit 2 unless a row is RED)
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
REF_ROWS = 16             # the alias reference averages this many sub-rows per output row
ALIAS_MAX = 8.0           # basis: FireHawk east 34 (his "static-like noise"); his good frames 1.4..3.7 (truth set)


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
            if low and not fc.get("area"):
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


def ref_bend(layer, body, hinge, deg, scale, sy, falloff):
    """The reference wing: the pose of flyer_cutout.bend() sampled at REF_ROWS sub-rows per output row and averaged.
    Its own loop, so a fault in the bake's sampler does not hide in the reference."""
    h, w = layer.shape[:2]
    hx, hy = hinge
    if falloff > 0:
        d = FC.distance_from(body, falloff) / float(falloff)
        am = d * d * (3 - 2 * d)
    else:
        am = np.ones((h, w), np.float32)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    th, sc = np.radians(deg) * am, 1 + (scale - 1) * am
    sv = 1 + (sy - 1) * am
    sv = np.where(np.abs(sv) < 0.08, np.where(sv >= 0, 0.08, -0.08), sv)
    c, s_ = np.cos(th), np.sin(th)
    pm = layer.astype(np.float32)
    pm[..., :3] *= pm[..., 3:4] / 255.0
    acc = 0
    for j in range(REF_ROWS):
        uy = (yy + (j + 0.5) / REF_ROWS - 0.5 - hy) / sv
        ux = xx - hx
        acc = acc + FC._bilinear(pm, (c * ux - s_ * uy) / sc + hx, (s_ * ux + c * uy) / sc + hy)
    return np.clip(acc / REF_ROWS, 0, 255)


def alias_rows(config: dict, src: Path, only: str | None = None) -> tuple[list[tuple[str, int, float, float]], list[str]]:
    """(facing, frame, sy, error) for every wing pose under |sy| SQUASH_MIN of every cut-out facing, and the facings
    that could not be read (their master frame is not in SRC)."""
    out, blind = [], []
    for facing, fc in config["facings"].items():
        if only and facing != only:
            continue
        if fc.get("translate") or fc.get("layer_bake") or "master" not in fc or not fc.get("wings"):
            continue                                   # a translate or layer_bake facing is not bent by bend()
        paths = FC.FL.frame_paths(src, config["prefix"], facing)
        if len(paths) < fc["master"]:
            blind.append(f"{facing} ({len(paths)} frames in {src}, master is frame {fc['master']})")
            continue
        master = np.asarray(Image.open(paths[fc["master"] - 1]).convert("RGBA"))
        plate, wings = FC.split(master, fc)
        body = (plate[..., 3] > 0) & ~np.logical_or.reduce([w_[..., 3] > 0 for w_ in wings])
        n = len(paths)
        for wg, layer in zip(fc["wings"], wings):
            fo = int(wg.get("falloff", fc.get("falloff", round(FC.FALLOFF * master.shape[1]))))
            for k, pose in enumerate(FC.poses_of(wg, n)):
                pose = list(pose) + [1.0, 1.0][len(pose) - 1:]
                deg, sc, sy = pose[0] * wg.get("sign", 1), pose[1], (pose[2] if len(pose) > 2 else 1.0)
                if abs(sy) >= SQUASH_MIN:
                    continue
                got = FC.bend(layer, body, wg["hinge"], deg, sc, sy, fo, bool(fc.get("area"))).astype(np.float32)
                got[..., :3] *= got[..., 3:4] / 255.0
                ref = ref_bend(layer, body, wg["hinge"], deg, sc, sy, fo)
                ink = (got[..., 3] > 0) | (ref[..., 3] > 0)
                if ink.sum():
                    out.append((facing, k + 1, sy, float(np.abs(got[..., :3] - ref[..., :3]).mean(-1)[ink].mean())))
    return out, blind


def installed_rows(config: dict, src: Path, only: str | None = None) -> list[tuple[str, bool, str]]:
    """(facing, the frames in SRC equal the bake of the recorded source, detail) for each area facing with a source."""
    out = []
    for facing, fc in config["facings"].items():
        if (only and facing != only) or not fc.get("area") or not fc.get("source"):
            continue
        paths = FC.FL.frame_paths(src, config["prefix"], facing)
        if not paths:
            out.append((facing, False, f"no frames in {src}"))
            continue
        frames = [np.asarray(Image.open(p).convert("RGBA")) for p in paths]
        baked, _, _ = FC.compose_facing(FC.source_master(fc["source"], frames[0].shape[0]), fc, len(frames))
        bad = [i + 1 for i, (x, y) in enumerate(zip(frames, baked)) if not np.array_equal(x, y)]
        out.append((facing, not bad, f"frames {bad} differ from the area bake of {fc['source']['path']}" if bad
                    else f"{len(frames)} frames are the area bake of {fc['source']['path']}"))
    return out


def alias(a) -> int:
    config = json.loads(Path(a.config).read_text())
    src = Path(a.src) if a.src else FC.REPO / config["folder"]
    rows, blind = alias_rows(config, src, a.facing)
    for b in blind:
        print(f"ALIAS   {config['set']} {b}: UNMEASURED")
    shipped = installed_rows(config, src, a.facing)
    for facing, ok, detail in shipped:
        print(f"BAKED   {config['set']} {facing}: {'GREEN' if ok else 'RED'}, {detail}")
    red = [r for r in rows if r[3] > ALIAS_MAX]
    if rows:
        worst = max(rows, key=lambda r: r[3])
        print(f"ALIAS   {config['set']}: {'RED' if red else 'GREEN'}, worst {worst[3]:.2f} at {worst[0]} frame {worst[1]} "
              f"sy {worst[2]} (max {ALIAS_MAX}); {len(red)} of {len(rows)} squashed poses over")
    elif not blind:
        print(f"ALIAS   {config['set']}: GREEN, no wing pose under |sy| {SQUASH_MIN}")
    return 1 if red or any(not r[1] for r in shipped) else (2 if blind else 0)


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
    al = sub.add_parser("alias")
    al.add_argument("config")
    al.add_argument("--src")
    al.add_argument("--facing")
    pa = sub.add_parser("parts")
    pa.add_argument("config")
    pa.add_argument("--src", required=True)
    pa.add_argument("--out", required=True)
    a = ap.parse_args()
    return {"audit": audit, "alias": alias, "parts": parts}[a.verb](a)


if __name__ == "__main__":
    sys.exit(main())
