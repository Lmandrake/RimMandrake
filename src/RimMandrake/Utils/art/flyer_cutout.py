#!/usr/bin/env python3
"""flyer_cutout.py - rebuild a flier flip-book so the BODY is pixel-identical in every frame and only the wings move.

FLIER_FRAMES_AUDIT_BODY_NOT_WING_EXTREMES; owner 2026-10-20, by card "Fliers: rebuild all 18 now". Owner, verbatim:
"Their bodies should be kept static while the wings flap. So looking for extreme of the graphic image is not useful
and couples wing motion to body motion incorrectly."

The `flyer_lock` plate recipe, for sets whose frames are separate repaints (body redrawn in a new pose each frame):
ONE master frame per facing is cut into a body PLATE plus wing layers, and every frame is composed from that plate
plus the wing layers turned about their shoulder hinge (cut-out animation). Nothing is generated or repainted; every
pixel comes from the master frame, so identity, palette and canvas are the master's. No alpha bbox is used anywhere.

Config (JSON, one per flip-book set):
  {"set": "Uvak", "folder": "src/.../Textures/swanimals/Uvak", "prefix": "Uvak_Flying_",
   "facings": {"south": {"master": 3, "order": "under",
                          "protect": [[[x, y], ...], ...],      # polygons kept in the plate even inside a wing polygon
                          "wings": [{"poly": [[x, y], ...], "hinge": [x, y], "sign": 1,
                                     "poses": [[deg, scale, sy], ...]}]},   # one pose per frame; sy optional
               "east": {"translate": true}}}                  # frames are one drawing: shift each onto frame 1's body
  A wing layer = master pixels inside its polygon and outside every protect polygon. The plate = master minus the
  wing layers. Pose deg > 0 turns the wing counter-clockwise on screen when sign = 1 (clockwise when sign = -1);
  scale shrinks/grows it about the hinge. order "under" draws the plate over the wings, "over" the wings over it;
  a wing may carry its own "order" (side views: far wing under, near wing over).
  `poses` may instead be `"cycle": {"amp": A, "bias": B, "scale_amp": S}`: deg_k = B + A*cos(2*pi*k/N + phase), with
  phase 0 for even N (ping-pong: frame N copies frame 2) and pi/(2N) for odd N (every frame distinct).

Verbs:
  build   CONFIG --out DIR [--facing F]    write <prefix><N>_<facing>.png for the configured facings, then check them
  preview CONFIG --out PNG --facing F      master with a 16 px grid, plate (green), wings (red/blue), hinges (yellow)
  check   DIR --prefix P --facing F [--plate PLATE]   body drift (flier_frame_registration) + flyer_lock locked share

Exit 0 = pass, 1 = a gate failed, 2 = bad input. Never touches src/ Textures: install is `art.py install`.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import flier_frame_registration as FR  # noqa: E402
import flyer_lock as FL  # noqa: E402

REPO = HERE.parents[3]
MARGIN = 6
FALLOFF = 0.10        # wing motion fades in over this fraction of the canvas width from the body
SEAM = 2              # px of master kept in the plate across every wing cut
DRIFT_PX = 1.0          # target: body drift <= 1 px per facing


def poly_mask(shape, polys) -> np.ndarray:
    h, w = shape
    im = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(im)
    for p in polys or []:
        d.polygon([tuple(map(float, q)) for q in p], fill=255)
    return np.asarray(im) > 0


def cycle_poses(n: int, amp: float, bias: float = 0.0, scale_amp: float = 0.0) -> list[list[float]]:
    phase = 0.0 if n % 2 == 0 else math.pi / (2 * n)
    out = []
    for k in range(n):
        c = math.cos(2 * math.pi * k / n + phase)
        out.append([round(bias + amp * c, 3), round(1.0 - scale_amp * (1 - abs(c)) if scale_amp else 1.0, 4)])
    return out


def _premul(a: np.ndarray) -> np.ndarray:
    f = a.astype(np.float32)
    f[..., :3] *= f[..., 3:4] / 255.0
    return f


def _unpremul(f: np.ndarray) -> np.ndarray:
    al = f[..., 3:4]
    rgb = np.where(al > 0.5, f[..., :3] * 255.0 / np.maximum(al, 1e-3), 0)
    return np.clip(np.concatenate([rgb, al], -1) + 0.5, 0, 255).astype(np.uint8)


def turn(layer: np.ndarray, hinge, deg: float, scale: float, sy: float = 1.0) -> np.ndarray:
    """Rotate LAYER (RGBA uint8) by DEG counter-clockwise on screen about HINGE, scale it by SCALE, then squash it
    vertically by SY about the hinge's row (side views: a wing beating about the body's long axis projects as a
    vertical squash; SY < 0 swings it below the shoulder). Resampled premultiplied, so edges keep no dark fringe."""
    if abs(deg) < 1e-6 and abs(scale - 1) < 1e-6 and abs(sy - 1) < 1e-6:
        return layer.copy()
    if abs(sy) < 0.08:
        sy = 0.08 if sy >= 0 else -0.08
    h, w = layer.shape[:2]
    hx, hy = hinge
    t = math.radians(deg)
    c, s = math.cos(t), math.sin(t)
    # forward, y-down screen coords: p' = H + diag(1, sy) * scale * R * (p - H), R = [[c, s], [-s, c]] (CCW on screen)
    fwd = np.array([[1.0, 0.0], [0.0, sy]]) @ (scale * np.array([[c, s], [-s, c]]))
    inv = np.linalg.inv(fwd)
    ia, ib, id_, ie = inv[0, 0], inv[0, 1], inv[1, 0], inv[1, 1]
    coeffs = (ia, ib, hx - ia * hx - ib * hy, id_, ie, hy - id_ * hx - ie * hy)
    pm = _premul(layer)
    ch = [np.asarray(Image.fromarray(pm[..., i], "F").transform((w, h), Image.AFFINE, coeffs, Image.BICUBIC))
          for i in range(4)]
    f = np.clip(np.stack(ch, -1), 0, 255)
    f[..., :3] = np.minimum(f[..., :3], f[..., 3:4])
    return _unpremul(f)


def _dilate8(m: np.ndarray) -> np.ndarray:
    o = FL._dilate(m)
    o[1:, 1:] |= m[:-1, :-1]; o[:-1, :-1] |= m[1:, 1:]; o[1:, :-1] |= m[:-1, 1:]; o[:-1, 1:] |= m[1:, :-1]
    return o


def distance_from(mask: np.ndarray, maxd: int) -> np.ndarray:
    """Chessboard distance (px) of every pixel from MASK, capped at MAXD."""
    d = np.full(mask.shape, float(maxd), np.float32)
    cur = mask.copy()
    for i in range(maxd):
        d[cur & (d == maxd)] = i
        cur = _dilate8(cur)
    return d


def _bilinear(img: np.ndarray, x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Sample IMG (H x W [x C] float) at float coords; outside the canvas reads 0."""
    h, w = img.shape[:2]
    x0, y0 = np.floor(x).astype(int), np.floor(y).astype(int)
    fx, fy = x - x0, y - y0
    out = 0
    for dy, wy in ((0, 1 - fy), (1, fy)):
        for dx, wx in ((0, 1 - fx), (1, fx)):
            xi, yi = x0 + dx, y0 + dy
            ok = (xi >= 0) & (xi < w) & (yi >= 0) & (yi < h)
            v = img[np.clip(yi, 0, h - 1), np.clip(xi, 0, w - 1)]
            wgt = (wx * wy * ok)
            out = out + (v * wgt[..., None] if v.ndim == 3 else v * wgt)
    return out


def bend(layer: np.ndarray, body: np.ndarray, hinge, deg: float, scale: float, sy: float, falloff: int) -> np.ndarray:
    """Like turn(), but the motion fades in with distance from the BODY: pixels touching the body stay put and the
    pose is reached FALLOFF px out, so membrane joined along a flank flexes instead of tearing away from it (rigid
    cut-outs leave a see-through gap there). Inverse-mapped per output pixel; bilinear, premultiplied."""
    if falloff <= 0:
        return turn(layer, hinge, deg, scale, sy)
    h, w = layer.shape[:2]
    hx, hy = hinge
    dmap = distance_from(body, falloff) / float(falloff)
    alpha_map = dmap * dmap * (3 - 2 * dmap)                       # smoothstep 0..1
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    px, py = xx - hx, yy - hy

    def inv_at(al):
        th = math.radians(deg) * al
        sc = 1 + (scale - 1) * al
        sv = 1 + (sy - 1) * al
        sv = np.where(np.abs(sv) < 0.08, np.where(sv >= 0, 0.08, -0.08), sv)
        # forward A = diag(1, sv) * sc * [[c, s], [-s, c]];  inverse = R^T / sc * diag(1, 1/sv)
        c, s_ = np.cos(th), np.sin(th)
        ux, uy = px, py / sv
        return (c * ux - s_ * uy) / sc, (s_ * ux + c * uy) / sc

    # the blend weight is read at the OUTPUT pixel: the body is static, so distance from it is the same in both
    # spaces, and every output pixel gets one well-defined source (no iteration, no fold-over fragments)
    qx, qy = inv_at(alpha_map)
    pm = _premul(layer)
    f = np.clip(_bilinear(pm, qx + hx, qy + hy), 0, 255)
    f[..., :3] = np.minimum(f[..., :3], f[..., 3:4])
    return _unpremul(f)


def over(bottom: np.ndarray, top: np.ndarray) -> np.ndarray:
    return np.asarray(Image.alpha_composite(Image.fromarray(bottom, "RGBA"), Image.fromarray(top, "RGBA")))


def split(master: np.ndarray, fc: dict) -> tuple[np.ndarray, list[np.ndarray]]:
    shape = master.shape[:2]
    protect = poly_mask(shape, fc.get("protect"))
    used = np.zeros(shape, bool)
    wings = []
    for wg in fc["wings"]:
        m = poly_mask(shape, [wg["poly"]]) & ~protect & ~used & (master[..., 3] > 0)
        used |= m
        wings.append(np.where(m[..., None], master, 0).astype(np.uint8))
    # SEAM: the plate keeps the master's pixels for SEAM px into each wing cut, so a turned wing's resampled edge
    # never shows a see-through line along the cut (the overlap is master pixels, drawn under or over the wing)
    keep = ~used & (master[..., 3] > 0)
    for _ in range(fc.get("seam", SEAM)):
        keep = FL._dilate(keep)
    keep &= master[..., 3] > 0
    plate = np.where(keep[..., None], master, 0).astype(np.uint8)
    return plate, wings


def poses_of(wg: dict, n: int) -> list[list[float]]:
    if "poses" in wg:
        p = wg["poses"]
        if len(p) != n:
            raise SystemExit(f"wing has {len(p)} poses, set has {n} frames")
        return p
    c = wg["cycle"]
    return cycle_poses(n, c["amp"], c.get("bias", 0.0), c.get("scale_amp", 0.0))


def compose_facing(master: np.ndarray, fc: dict, n: int) -> tuple[list[np.ndarray], np.ndarray, list[np.ndarray]]:
    """Frames, the plate, and per frame the mask of pixels an OVER wing paints (where the plate may not show)."""
    plate, wings = split(master, fc)
    body = (plate[..., 3] > 0) & ~np.logical_or.reduce([w_[..., 3] > 0 for w_ in wings])   # plate minus the seam band
    frames, covers = [], []
    for k in range(n):
        acc = np.zeros_like(master, dtype=np.uint8)
        layers = []
        for wg, layer in zip(fc["wings"], wings):
            pose = list(poses_of(wg, n)[k]) + [1.0, 1.0][len(poses_of(wg, n)[k]) - 1:]
            deg, sc, sy = pose[0], pose[1], pose[2] if len(pose) > 2 else 1.0
            layers.append(bend(layer, body, wg["hinge"], deg * wg.get("sign", 1), sc, sy,
                               int(wg.get("falloff", fc.get("falloff", round(FALLOFF * master.shape[1]))))))
        default = fc.get("order", "under")
        for wg, L in zip(fc["wings"], layers):          # wings drawn under the plate first (far side)
            if wg.get("order", default) == "under":
                acc = over(acc, L)
        acc = over(acc, plate)
        cover = np.zeros(master.shape[:2], bool)
        for wg, L in zip(fc["wings"], layers):          # then wings over it (near side)
            if wg.get("order", default) == "over":
                acc = over(acc, L)
                cover |= L[..., 3] > 0
        covers.append(cover)
        frames.append(acc)
    return frames, plate, covers


def translate_facing(paths: list[Path]) -> tuple[list[np.ndarray], list]:
    """Frames that are one drawing, only shifted: move each so its rigid body lies on frame 1's (mask overlap)."""
    rg = [np.asarray(Image.open(p).convert("RGBA")) for p in paths]
    bm = [FR.body_of(a[..., 3]) for a in rg]
    out, shifts = [rg[0].copy()], [(0, 0)]
    for a, b in zip(rg[1:], bm[1:]):
        dx, dy = FR.mask_shift(bm[0], b)
        # mask_shift gives the shift that lays b on ref: ref[y+dy, x+dx] ~ b[y, x] -> move frame by (dx, dy)
        out.append(FL.shift(a.astype(np.int16), dx, dy).astype(np.uint8))
        shifts.append((dx, dy))
    return out, shifts


def measure(frames: list[np.ndarray]) -> dict:
    r = FR.measure_frames([a[..., 3] for a in frames], frames)
    h, w = frames[0].shape[:2]
    marg = 10 ** 9
    for a in frames:
        ys, xs = np.nonzero(a[..., 3] > FL.OPAQUE)   # the animal shader is a cutout: what draws is alpha > 128
        if len(ys):
            marg = min(marg, ys.min(), xs.min(), h - 1 - ys.max(), w - 1 - xs.max())
    share = FL.locked_share([a.astype(np.int16) for a in frames])
    return {"body_px": round(r["match_span"], 2), "body_frac": round(r["match_span"] / r["body_size"], 4) if r["body_size"] else 0,
            "colour_px": round(r["colour_span"], 2), "open_px": round(r["body_span"], 2), "bbox_px": round(r["bbox_span"], 2),
            "colour_share": round(r["colour_share"], 3), "locked_share": round(share, 4), "margin": int(marg)}


def drift_ok(m: dict, plate_ident: float | None = None) -> bool:
    """Body drift target. The mask-overlap span (body_px) is the audit's primary figure, but the opened mask keeps
    broad wing roots, so a pixel-identical body can still read tens of px. The colour registration (colour_px) is
    exact when the body pixels really are shared (colour_share high), so either at <= DRIFT_PX passes."""
    shared = m["colour_share"] >= 0.5 or (plate_ident or 0) >= 0.99   # a byte-identical plate is the shared body
    return m["body_px"] <= DRIFT_PX or (m["colour_px"] <= DRIFT_PX and shared)


def plate_identical(frames: list[np.ndarray], plate: np.ndarray, covers: list[np.ndarray] | None = None) -> float:
    """Share of opaque plate pixels that are byte-identical to the plate in EVERY frame (wings excused where they
    actually cover them: a pixel counts as covered when it differs from the plate in that frame)."""
    pm = plate[..., 3] == 255      # soft plate edges blend with the wing drawn under them, so only solid pixels count
    if covers is None:
        covers = [np.zeros(pm.shape, bool)] * len(frames)
    free = pm & ~np.logical_or.reduce(covers)
    same = np.logical_and.reduce([(a == plate).all(-1) for a in frames]) & free
    return float(same.sum()) / max(int(free.sum()), 1)


def cmd_build(a) -> int:
    cfg = json.loads(Path(a.config).read_text())
    folder = REPO / cfg["folder"] if not Path(cfg["folder"]).is_absolute() else Path(cfg["folder"])
    src_root = Path(a.src) if a.src else folder
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    rep, ok = {"set": cfg["set"], "facings": {}}, True
    for facing, fc in cfg["facings"].items():
        if a.facing and facing != a.facing:
            continue
        paths = FL.frame_paths(src_root, cfg["prefix"], facing)
        if len(paths) < 2:
            print(f"ERROR {facing}: {len(paths)} frames in {src_root}", file=sys.stderr)
            return 2
        orig = [np.asarray(Image.open(p).convert("RGBA")) for p in paths]
        sizes = sorted({o.shape[1] for o in orig})
        before = measure(orig) if len(sizes) == 1 else {"body_px": None, "colour_px": None, "locked_share": None,
                                                         "error": f"mixed canvas sizes {sizes}"}
        if fc.get("translate"):
            frames, shifts = translate_facing(paths)
            info = {"mode": "translate", "shifts": shifts}
            plate, covers = None, None
        else:
            master = np.asarray(Image.open(paths[fc["master"] - 1]).convert("RGBA"))
            frames, plate, covers = compose_facing(master, fc, len(paths))
            info = {"mode": "cutout", "master": fc["master"]}
        for i, fr in enumerate(frames, 1):
            Image.fromarray(fr, "RGBA").save(out / f"{cfg['prefix']}{i}_{facing}.png")
        if plate is not None:
            Image.fromarray(plate, "RGBA").save(out / f"_plate_{cfg['prefix']}{facing}.png")
        after = measure(frames)
        info.update(before=before, after=after)
        if plate is not None:
            info["plate_identical"] = round(plate_identical(frames, plate, covers), 4)
            info["plate_never_covered"] = round(float((plate[..., 3] == 255).sum() and ((plate[..., 3] == 255) & ~np.logical_or.reduce(covers)).sum() / (plate[..., 3] == 255).sum()), 4)
        fails = []
        if not drift_ok(after, info.get("plate_identical")):
            fails.append(f"body drift {after['body_px']} px (colour {after['colour_px']} px at share {after['colour_share']}) > {DRIFT_PX}")
        floor = MARGIN if plate is None else min(MARGIN, measure([master, master])["margin"])
        if after["margin"] < floor:   # a master drawn closer to the edge than 6 px keeps its own margin, no less
            fails.append(f"margin {after['margin']} < {floor}")
        for i in range(len(frames)):
            if np.array_equal(frames[i], frames[(i + 1) % len(frames)]):
                fails.append(f"frames {i + 1} and {(i + 1) % len(frames) + 1} identical")
        info["fails"] = fails
        ok &= not fails
        rep["facings"][facing] = info
        print(f"{'PASS' if not fails else 'FAIL'} {cfg['set']} {facing} {info['mode']}: drift {before['body_px']} -> "
              f"{after['body_px']} px (colour {before['colour_px']} -> {after['colour_px']} @ {after['colour_share']}), locked {before['locked_share']} -> {after['locked_share']}, margin {after['margin']}"
              + (f", plate_identical {info['plate_identical']}" if plate is not None else "") + (f"  {fails}" if fails else ""))
    (out / f"_report_{cfg['set']}.json").write_text(json.dumps(rep, indent=1, default=int))
    return 0 if ok else 1


def cmd_preview(a) -> int:
    cfg = json.loads(Path(a.config).read_text())
    folder = REPO / cfg["folder"]
    src_root = Path(a.src) if a.src else folder
    fc = cfg["facings"][a.facing]
    paths = FL.frame_paths(src_root, cfg["prefix"], a.facing)
    master = np.asarray(Image.open(paths[fc.get("master", 1) - 1]).convert("RGBA"))
    h, w = master.shape[:2]
    k = max(1, 768 // w)
    bg = Image.new("RGBA", (w, h), (118, 118, 118, 255))
    img = Image.alpha_composite(bg, Image.fromarray(master, "RGBA"))
    if "wings" in fc:
        plate, wings = split(master, fc)
        tint = np.zeros((h, w, 4), np.uint8)
        tint[plate[..., 3] > 0] = (0, 255, 0, 35)
        for i, wl in enumerate(wings):
            tint[wl[..., 3] > 0] = ((255, 0, 0, 90), (0, 80, 255, 90), (255, 0, 255, 90), (0, 255, 255, 90))[i % 4]
        img = Image.alpha_composite(img, Image.fromarray(tint, "RGBA"))
    img = img.resize((w * k, h * k), Image.NEAREST)
    d = ImageDraw.Draw(img)
    step = 16 if w <= 256 else 32
    for g in range(0, w, step):
        col = (255, 255, 255, 110) if g % (step * 4) else (255, 255, 0, 160)
        d.line([(g * k, 0), (g * k, h * k)], fill=col)
        d.line([(0, g * k), (w * k, g * k)], fill=col)
        d.text((g * k + 1, 1), str(g), fill=(255, 255, 255, 255))
        d.text((1, g * k + 1), str(g), fill=(255, 255, 255, 255))
    for wg in fc.get("wings", []):
        x, y = wg["hinge"]
        d.ellipse([x * k - 5, y * k - 5, x * k + 5, y * k + 5], outline=(255, 255, 0, 255), width=2)
    img.convert("RGB").save(a.out)
    print(a.out)
    return 0


def cmd_check(a) -> int:
    paths = FL.frame_paths(Path(a.dir), a.prefix, a.facing)
    frames = [np.asarray(Image.open(p).convert("RGBA")) for p in paths]
    if len(frames) < 2:
        print("ERROR fewer than 2 frames", file=sys.stderr)
        return 2
    m = measure(frames)
    if a.plate:
        m["plate_identical"] = round(plate_identical(frames, np.asarray(Image.open(a.plate).convert("RGBA"))), 4)
    ok = drift_ok(m, m.get("plate_identical")) and m["margin"] >= MARGIN
    print(f"{'PASS' if ok else 'FAIL'} {a.prefix}{a.facing}: {json.dumps(m)}")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="verb", required=True)
    b = sub.add_parser("build")
    b.add_argument("config")
    b.add_argument("--out", required=True)
    b.add_argument("--facing")
    b.add_argument("--src", help="read the frames from here instead of the config folder (e.g. a before/ copy)")
    p = sub.add_parser("preview")
    p.add_argument("config")
    p.add_argument("--out", required=True)
    p.add_argument("--facing", required=True)
    p.add_argument("--src")
    c = sub.add_parser("check")
    c.add_argument("dir")
    c.add_argument("--prefix", required=True)
    c.add_argument("--facing", required=True)
    c.add_argument("--plate")
    a = ap.parse_args(argv)
    return {"build": cmd_build, "preview": cmd_preview, "check": cmd_check}[a.verb](a)


if __name__ == "__main__":
    sys.exit(main())
