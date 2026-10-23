#!/usr/bin/env python3
"""flier_layer_bake.py - bake a flier flip-book from ONE body plate plus wing surfaces, with a facing-specific
projection of each wing (FLIER_AFTERNOON_EXPERIMENT_PROVE_STILL_TORSO; design/RimMandrake/
flier_authoring_architecture_2026-10-21.md, GPT section E).

Offline authoring only: it writes PNGs and review pages to --out and never touches src/ Textures (install is
`art.py install`, and nothing here is installable without the owner's look).

Model (south). Each wing is a plane joined to the body along a pinned SEAM (two points on the flank). The seam is
the rotation axis and lies in the picture plane. For a wing pixel at signed distance d outward from the seam and
position a along it, a stroke angle theta gives
    in-plane span  d -> d*cos(theta)                (foreshortening: the wing turns toward/away from the camera)
    depth          z  = d*sin(theta)                (projected as a screen RISE of lift_k*z: high camera)
so a raised wing narrows AND lifts, a lowered one narrows and drops, and seam pixels (d = 0) never move. Before the
turn the FOLD compresses the membrane below the leading edge (shoulder -> wrist) toward it along the seam axis (the
fingers closing on the recovery). The distal wing lags the proximal one (distal_lag of a cycle, distal_gain), so the
tip trails. Shading: shade_rise*sin(theta) lighter when raised, shade_turn*(1-cos(theta)) darker as it turns. All of
it is an inverse map per output pixel (Gauss-Newton on the forward map), premultiplied bilinear: no fold-over
fragments, no alpha bbox anywhere, the plate is drawn byte-for-byte from the master.

Verbs:
  split  CONFIG --master PNG --out DIR             body plate, wing layers, masks (+ hole report)
  bake   CONFIG --master PNG --out DIR [--tag T]   <prefix><k>_south.png for every key, plus _bake_<tag>.json
  sheet  CONFIG --master PNG --frames DIR --out PNG   contact sheet: annotation, masks, seams, extremes, onion
  html   --frames DIR --prefix P --facing F --tpf N --out HTML [--alt DIR:label]   offline canvas preview
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import flyer_cutout as FC  # noqa: E402
import flyer_lock as FL  # noqa: E402


def load(cfg_path: str, facing: str = "south") -> tuple[dict, dict]:
    cfg = json.loads(Path(cfg_path).read_text())
    return cfg, cfg["facings"][facing]


def split_layers(master: np.ndarray, fc: dict):
    """Plate (master minus wings, plus a seam band of master pixels into each cut) and one layer per wing."""
    shape = master.shape[:2]
    protect = FC.poly_mask(shape, fc["protect"])
    used = np.zeros(shape, bool)
    wings, masks = [], []
    for wg in fc["wings"]:
        m = FC.poly_mask(shape, [wg["poly"]]) & ~protect & ~used & (master[..., 3] > 0)
        used |= m
        masks.append(m)
        wings.append(np.where(m[..., None], master, 0).astype(np.uint8))
    keep = ~used & (master[..., 3] > 0)
    for _ in range(int(fc.get("seam_px", FC.SEAM))):
        keep = FL._dilate(keep)
    keep &= master[..., 3] > 0
    plate = np.where(keep[..., None], master, 0).astype(np.uint8)
    # a soft (alpha < 255) seam-band pixel lives in the plate only: drawn twice it would double its coverage
    soft = keep & (master[..., 3] < 255)
    for L in wings:
        L[soft] = 0
    return plate, wings, masks, protect


def _smooth(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3 - 2 * x)


def periodic_sample(vals: list[float], t: float) -> float:
    """Catmull-Rom through VALS at t = k/n (periodic), sampled at T (cycles)."""
    n = len(vals)
    u = (t % 1.0) * n
    i = int(math.floor(u))
    f = u - i
    p0, p1, p2, p3 = (vals[(i + j) % n] for j in (-1, 0, 1, 2))
    return 0.5 * ((2 * p1) + (-p0 + p2) * f + (2 * p0 - 5 * p1 + 4 * p2 - p3) * f * f + (-p0 + 3 * p1 - 3 * p2 + p3) * f ** 3)


def wing_frame(layer: np.ndarray, wg: dict, lb: dict, th_p: float, th_d: float, fold: float, scale: float = 1.0):
    """Inverse-map one wing layer to stroke angles TH_P (proximal) / TH_D (distal), fold FOLD. Returns RGBA uint8."""
    h, w = layer.shape[:2]
    (sx0, sy0), (sx1, sy1) = wg["seam"]
    A = np.array([sx1 - sx0, sy1 - sy0], float)
    A /= np.linalg.norm(A)
    Nout = np.array([-A[1], A[0]])
    if wg["sign"] < 0:                               # outward = away from the body
        Nout = -Nout if Nout[0] > 0 else Nout
    else:
        Nout = -Nout if Nout[0] < 0 else Nout
    R = np.array([sx0, sy0], float)
    lift = np.array([0.0, -float(lb.get("lift_k", 0.8))])     # screen rise per px of depth toward the camera
    L = float(lb.get("span_px", 100))
    fold_ramp = float(lb.get("fold_ramp_px", 0.6 * L))   # how far off the seam the fold reaches full strength
    span_pow = float(lb.get("span_pow", 1.0))       # <1 narrows the raised wing less than true foreshortening
    (lx0, ly0), (lx1, ly1) = wg["leading_edge"]
    le0 = (np.array([lx0, ly0]) - R)
    le1 = (np.array([lx1, ly1]) - R)
    la0, ld0 = le0 @ A, le0 @ Nout
    la1, ld1 = le1 @ A, le1 @ Nout
    slope = (la1 - la0) / max(ld1 - ld0, 1e-6)

    def a_le(d):
        return la0 + (d - ld0) * slope

    def params(d):
        s = _smooth(d / L)
        th = np.radians(th_p + (th_d - th_p) * s) * (d > 0)
        f = 1.0 - (1.0 - fold) * _smooth(d / fold_ramp)
        return th, np.where(d > 0, f, 1.0)

    hinge_model = lb.get("model") == "hinge"
    H = np.array(wg["hinge"], float)
    ramp = float(lb.get("root_ramp_px", 24))
    sgn = 1.0 if wg["sign"] > 0 else -1.0
    ramp_from_hinge = lb.get("ramp_from") == "hinge"

    def forward_hinge(a, d):
        # 'hinge' model (south, 2026-10-23 redo after the owner read the seam-axis bake as PADDLING): the wing
        # swings UP/DOWN about its shoulder in the picture plane (the flap axis is the body's long axis, which
        # points at a south camera), shortening by `scale` (foreshortening + wrist fold) as it rises. The swing
        # and the shortening ease in over root_ramp_px off the seam, so the membrane root stays on the flank.
        th, f = params(d)
        ale = a_le(d)
        a1 = np.where(a > ale, ale + (a - ale) * f, a)
        px = R[0] + a1 * A[0] + d * Nout[0] - H[0]
        py = R[1] + a1 * A[1] + d * Nout[1] - H[1]
        if ramp_from_hinge:   # attached at the shoulder only: everything beyond ramp px of the hinge swings whole
            w = _smooth(np.hypot(px, py) / ramp)
        else:                 # attached along the whole flank seam: the membrane fans out from it
            w = _smooth(np.maximum(d, 0) / ramp)
        ph = th * w * sgn
        sc = 1.0 - (1.0 - scale) * w
        X = H[0] + sc * (px * np.cos(ph) + py * np.sin(ph))
        Y = H[1] + sc * (-px * np.sin(ph) + py * np.cos(ph))
        return X, Y

    def forward(a, d):
        if hinge_model:
            return forward_hinge(a, d)
        th, f = params(d)
        ale = a_le(d)
        a1 = np.where(a > ale, ale + (a - ale) * f, a)
        dp = np.maximum(d, 0)
        span = np.where(d > 0, d * np.abs(np.cos(th)) ** span_pow, d)
        z = dp * np.sin(th)
        X = R[0] + a1 * A[0] + span * Nout[0] + z * lift[0]
        Y = R[1] + a1 * A[1] + span * Nout[1] + z * lift[1]
        return X, Y

    yy, xx = np.mgrid[0:h, 0:w].astype(np.float64)
    rel = np.stack([xx - R[0], yy - R[1]], -1)
    a = rel @ A
    d = rel @ Nout
    qa, qd = a.copy(), d.copy()
    for _ in range(25):                              # Gauss-Newton with a numeric Jacobian
        X, Y = forward(a, d)
        rx, ry = xx - X, yy - Y
        e = 1e-3
        Xa, Ya = forward(a + e, d)
        Xd, Yd = forward(a, d + e)
        j11, j21 = (Xa - X) / e, (Ya - Y) / e
        j12, j22 = (Xd - X) / e, (Yd - Y) / e
        det = j11 * j22 - j12 * j21
        det = np.where(np.abs(det) < 1e-6, 1e-6, det)
        a = a + (j22 * rx - j12 * ry) / det
        d = d + (-j21 * rx + j11 * ry) / det
    X, Y = forward(a, d)
    resid = np.hypot(xx - X, yy - Y)
    srcx = R[0] + a * A[0] + d * Nout[0]
    srcy = R[1] + a * A[1] + d * Nout[1]
    pm = FC._premul(layer)
    f = np.clip(FC._bilinear(pm, srcx.astype(np.float32), srcy.astype(np.float32)), 0, 255)
    f[resid > 0.25] = 0                              # no source solves this pixel: leave it empty, never smear
    th, _ = params(d)
    th = th * _smooth(d / 12.0)                      # shading eases in off the seam: no tone step at the pinned root
    shade = 1.0 + float(lb.get("shade_rise", 0)) * np.sin(th) - float(lb.get("shade_turn", 0)) * (1 - np.cos(th))
    f[..., :3] *= shade[..., None]
    f[..., :3] = np.minimum(f[..., :3], f[..., 3:4])
    return FC._unpremul(f), float(resid[f[..., 3] > 0].max()) if (f[..., 3] > 0).any() else 0.0


def key_angles(lb: dict, n: int):
    keys = lb["keys"]
    if len(keys) != n:
        raise SystemExit(f"{len(keys)} keys for {n} frames")
    prox = [k[0] for k in keys]
    out = []
    for k in range(n):
        t = k / n
        th_d = periodic_sample(prox, t - float(lb.get("distal_lag", 0))) * float(lb.get("distal_gain", 1))
        out.append((prox[k], th_d, keys[k][1], keys[k][2] if len(keys[k]) > 2 else 1.0))
    return out


def bake(master: np.ndarray, fc: dict):
    lb = fc["layer_bake"]
    plate, wings, masks, _ = split_layers(master, fc)
    n = len(lb["keys"])
    frames, info = [], []
    for k, (tp, td, fold, scale) in enumerate(key_angles(lb, n)):
        acc = np.zeros_like(master)
        resid = 0.0
        moved = []
        for wg, layer in zip(fc["wings"], wings):
            L, r = wing_frame(layer, wg, lb, tp, td, fold, scale)
            resid = max(resid, r)
            moved.append(L)
        for wg, L in zip(fc["wings"], moved):
            if wg.get("occlusion", fc.get("order", "under")) == "under":
                acc = FC.over(acc, L)
        acc = FC.over(acc, plate)
        for wg, L in zip(fc["wings"], moved):
            if wg.get("occlusion", fc.get("order", "under")) == "over":
                acc = FC.over(acc, L)
        frames.append(acc)
        info.append({"frame": k + 1, "theta_prox": tp, "theta_distal": round(td, 2), "fold": fold, "scale": scale,
                     "inverse_resid_px": round(resid, 4)})
    return frames, plate, wings, masks, info


def seam_gap(frames, fc, master):
    """See-through test at each seam: along the seam segment, the column of pixels just outside the flank must stay
    opaque wherever it is opaque in the master (a wing pulled off the flank shows background there)."""
    out = []
    for wg in fc["wings"]:
        (x0, y0), (x1, y1) = wg["seam"]
        side = -1 if wg["sign"] < 0 else 1
        pts = []
        for t in np.linspace(0, 1, 40):
            x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            for off in (1, 2, 3):
                xi, yi = int(round(x + side * off)), int(round(y))
                if master[yi, xi, 3] == 255:
                    pts.append((xi, yi))
        bad = [(k + 1, p) for k, fr in enumerate(frames) for p in pts if fr[p[1], p[0], 3] < 200]
        out.append({"wing": wg.get("id"), "probe_px": len(pts), "open_px": len(bad), "examples": bad[:6]})
    return out


def holes_report(master, plate, wings, frames, protect=None):
    """Pixels inside the body outline (protect) that are opaque in the master, transparent in the plate, and
    transparent in some frame: body area a moving wing exposes with nothing behind it (needs completion)."""
    m = master[..., 3] > 128
    if protect is not None:
        m &= protect
    pl = plate[..., 3] > 128
    amin = np.min([f[..., 3] for f in frames], 0) > 128
    exposed = m & ~pl & ~amin
    return int(exposed.sum()), exposed


def cmd_split(a) -> int:
    cfg, fc = load(a.config)
    master = np.asarray(Image.open(a.master).convert("RGBA"))
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    plate, wings, masks, protect = split_layers(master, fc)
    Image.fromarray(plate, "RGBA").save(out / "south_body_plate.png")
    for wg, L, m in zip(fc["wings"], wings, masks):
        Image.fromarray(L, "RGBA").save(out / f"south_{wg['id']}.png")
        Image.fromarray((m * 255).astype(np.uint8), "L").save(out / f"south_{wg['id']}_mask.png")
    Image.fromarray(((protect & (master[..., 3] > 0)) * 255).astype(np.uint8), "L").save(out / "south_protected_mask.png")
    # recomposition check: plate over wings at pose 0 must equal the master byte for byte
    acc = np.zeros_like(master)
    for L in wings:
        acc = FC.over(acc, L)
    acc = FC.over(acc, plate)
    diff = int((acc != master).any(-1).sum())
    print(f"split: plate {int((plate[..., 3] > 0).sum())} px, wings {[int(m.sum()) for m in masks]} px, "
          f"recomposed vs master: {diff} px differ")
    return 0 if diff == 0 else 1


def cmd_bake(a) -> int:
    cfg, fc = load(a.config)
    master = np.asarray(Image.open(a.master).convert("RGBA"))
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    frames, plate, wings, masks, info = bake(master, fc)
    for i, fr in enumerate(frames, 1):
        Image.fromarray(fr, "RGBA").save(out / f"{cfg['prefix']}{i}_south.png")
    Image.fromarray(plate, "RGBA").save(out / "_plate_south.png")
    h, w = master.shape[:2]
    marg = min(min(ys.min(), xs.min(), h - 1 - ys.max(), w - 1 - xs.max())
               for ys, xs in (np.nonzero(f[..., 3] > 128) for f in frames))
    mm = np.nonzero(master[..., 3] > 128)
    mmarg = min(mm[0].min(), mm[1].min(), h - 1 - mm[0].max(), w - 1 - mm[1].max())
    nexp, _ = holes_report(master, plate, wings, frames, FC.poly_mask(master.shape[:2], fc["protect"]))
    rep = {"set": cfg["set"], "tag": a.tag, "master": str(a.master),
           "master_sha256": hashlib.sha256(Path(a.master).read_bytes()).hexdigest(),
           "frame1_equals_master": bool(np.array_equal(frames[0], master)),
           "margin_px": int(marg), "master_margin_px": int(mmarg), "exposed_body_px": nexp,
           "seams": seam_gap(frames, fc, master), "frames": info,
           "consecutive_identical": [i + 1 for i in range(len(frames)) if np.array_equal(frames[i], frames[(i + 1) % len(frames)])]}
    (out / f"_bake_{a.tag}.json").write_text(json.dumps(rep, indent=1, default=int))
    print(f"bake {a.tag}: {len(frames)} frames, frame1==master {rep['frame1_equals_master']}, margin {marg} "
          f"(master {mmarg}), exposed body px {nexp}, seam open px {[s['open_px'] for s in rep['seams']]}, "
          f"max inverse resid {max(i['inverse_resid_px'] for i in info)}")
    return 0


def _rgba_on(bg, arr, k):
    im = Image.new("RGBA", (arr.shape[1], arr.shape[0]), bg)
    im.alpha_composite(Image.fromarray(arr, "RGBA"))
    return im.resize((arr.shape[1] * k, arr.shape[0] * k), Image.NEAREST)


def cmd_sheet(a) -> int:
    cfg, fc = load(a.config)
    master = np.asarray(Image.open(a.master).convert("RGBA"))
    paths = FL.frame_paths(Path(a.frames), cfg["prefix"], "south")
    frames = [np.asarray(Image.open(p).convert("RGBA")) for p in paths]
    plate, wings, masks, protect = split_layers(master, fc)
    h, w = master.shape[:2]
    BG = (118, 112, 100, 255)
    k = 3
    # panel 1: enlarged annotated master
    ann = _rgba_on(BG, master, k)
    tint = np.zeros((h, w, 4), np.uint8)
    tint[protect & (master[..., 3] > 0)] = (0, 230, 255, 110)
    for i, m in enumerate(masks):
        tint[m] = ((255, 60, 60, 110), (70, 110, 255, 110))[i % 2]
    seamband = (plate[..., 3] > 0) & np.logical_or.reduce(masks)
    tint[seamband] = (255, 255, 0, 160)
    ann.alpha_composite(Image.fromarray(tint, "RGBA").resize((w * k, h * k), Image.NEAREST))
    d = ImageDraw.Draw(ann)
    env = np.max([f[..., 3] for f in frames], 0) > 128          # allowed envelope used by the cycle
    ey, ex = np.nonzero(env & ~FL._dilate(env) | (env & ~np.roll(env, 1, 0)) | (env & ~np.roll(env, -1, 0))
                        | (env & ~np.roll(env, 1, 1)) | (env & ~np.roll(env, -1, 1)))
    for x, y in zip(ex, ey):
        d.point((x * k + 1, y * k + 1), fill=(255, 255, 255, 255))
    for wg in fc["wings"]:
        (x0, y0), (x1, y1) = wg["seam"]
        d.line([(x0 * k, y0 * k), (x1 * k, y1 * k)], fill=(255, 255, 0, 255), width=3)
        (lx0, ly0), (lx1, ly1) = wg["leading_edge"]
        d.line([(lx0 * k, ly0 * k), (lx1 * k, ly1 * k)], fill=(255, 140, 0, 255), width=2)
        hx, hy = wg["hinge"]
        d.ellipse([hx * k - 6, hy * k - 6, hx * k + 6, hy * k + 6], outline=(255, 255, 0, 255), width=2)
    for lm in fc.get("landmarks", []):
        x, y = lm["xy"]
        col = (0, 255, 120, 255) if lm["role"] == "head" else (255, 0, 255, 255)
        d.line([(x * k - 7, y * k), (x * k + 7, y * k)], fill=col, width=2)
        d.line([(x * k, y * k - 7), (x * k, y * k + 7)], fill=col, width=2)
    # extremes: top (max theta) and bottom (min theta)
    lb = fc["layer_bake"]
    th = [kk[0] for kk in lb["keys"]]
    top, bot = int(np.argmax(th)), int(np.argmin(th))
    ext = [(_rgba_on(BG, frames[bot], k), f"frame {bot + 1}: bottom ({th[bot]} deg)"),
           (_rgba_on(BG, frames[top], k), f"frame {top + 1}: top ({th[top]} deg, fold {lb['keys'][top][1]})")]
    # masks row
    small = 1
    mrow = [(_rgba_on(BG, plate, small), "body plate"), (_rgba_on(BG, wings[0], small), "left wing layer"),
            (_rgba_on(BG, wings[1], small), "right wing layer")]
    pm = np.zeros((h, w, 4), np.uint8)
    pm[protect & (master[..., 3] > 0)] = (0, 230, 255, 255)
    mrow.append((Image.fromarray(pm, "RGBA"), "protected mask"))
    _, exposed = holes_report(master, plate, wings, frames, protect)
    ex_im = np.zeros((h, w, 4), np.uint8)
    ex_im[master[..., 3] > 128] = (60, 60, 60, 255)
    ex_im[exposed] = (255, 0, 0, 255)
    mrow.append((Image.fromarray(ex_im, "RGBA"), f"exposed in some frame ({int(exposed.sum())} px, red)"))
    # onion: all frames' silhouettes, plus every frame small
    onion = np.zeros((h, w, 4), np.uint8)
    for i, f in enumerate(frames):
        c = np.array(Image.new("RGB", (1, 1), f"hsl({int(360 * i / len(frames))},90%,55%)").getpixel((0, 0)))
        edge = (f[..., 3] > 128) & ~FL._dilate(~(f[..., 3] > 128))
        sil = (f[..., 3] > 128)
        ring = sil & ~(np.roll(sil, 1, 0) & np.roll(sil, -1, 0) & np.roll(sil, 1, 1) & np.roll(sil, -1, 1))
        onion[ring | edge] = (*c, 255)
    mrow.append((_rgba_on(BG, onion, small), "wing silhouettes, all frames"))
    frow = [(_rgba_on(BG, f, small), f"{i + 1}: {th[i]} deg") for i, f in enumerate(frames)]
    pad, lab = 12, 18
    W = max(ann.width + pad + ext[0][0].width + pad + ext[1][0].width,
            len(mrow) * (w + pad), len(frow) * (w + pad)) + pad
    H = lab + ann.height + pad + lab + h + pad + lab + h + pad + 40
    sheet = Image.new("RGB", (W, H), (44, 38, 32))
    sd = ImageDraw.Draw(sheet)
    x = pad
    for im, t in [(ann, "annotation: cyan protected body, red/blue wing layers, yellow seam band + seam axes, "
                        "orange leading edge, white envelope of the cycle")] + ext:
        sd.text((x, 4), t, fill=(240, 230, 210))
        sheet.paste(im, (x, lab), im)
        x += im.width + pad
    y = lab + ann.height + pad
    for row in (mrow, frow):
        x = pad
        for im, t in row:
            sd.text((x, y), t, fill=(240, 230, 210))
            sheet.paste(im, (x, y + lab), im)
            x += w + pad
        y += lab + h + pad
    sd.text((pad, y), f"{cfg['set']} south. Source master sha256 {hashlib.sha256(Path(a.master).read_bytes()).hexdigest()[:16]}; "
                      f"frames from {a.frames}", fill=(200, 190, 170))
    sheet.save(a.out)
    print(a.out)
    return 0


HTML = """<!doctype html><html><head><meta charset="utf-8"><title>Uvak South Flap</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
:root{--bg:#2c2620;--panel:#3a322a;--ink:#efe4d0;--mute:#b8a88c;--acc:#d9a441}
body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.45 system-ui,sans-serif;padding:16px}
h1{font-size:18px;margin:0 0 6px} .row{display:flex;flex-wrap:wrap;gap:16px;align-items:flex-start}
.card{background:var(--panel);border-radius:8px;padding:10px} canvas{image-rendering:pixelated;display:block}
label{margin-right:12px;white-space:nowrap} .mute{color:var(--mute)} button{background:var(--acc);border:0;border-radius:4px;padding:4px 10px;margin-right:6px}
select{background:#eee} #strip{max-width:100%;height:auto}
</style></head><body>
<h1>__TITLE__</h1>
<div class="mute">The exact PNG files, drawn whole at a fixed canvas position (never cropped or recentred). Crosshair = canvas centre (128,128). Timing = flyingAnimationTicksPerFrame at 60 ticks/s x game speed.</div>
<div class="card" style="margin:10px 0">
 <label>set <select id="set">__SETS__</select></label>
 <label>ticks/frame <select id="tpf"><option>5</option><option selected>__TPF__</option><option>15</option><option>20</option></select></label>
 <label>game speed <select id="spd"><option value="1" selected>1x</option><option value="2">2x</option><option value="3">3x</option><option value="0.25">0.25x (study)</option></select></label>
 <button id="pp">pause</button><button id="st">step</button>
 <label><input type="checkbox" id="gx" checked> crosshair</label>
 <label><input type="checkbox" id="ge" checked> eye line</label>
 <label><input type="checkbox" id="gs" checked> shoulder/root line</label>
 <label><input type="checkbox" id="gb"> body outline</label>
 <label>zoom <select id="zm"><option>2</option><option selected>3</option><option>4</option></select></label>
 <span id="fr" class="mute"></span>
</div>
<div class="row">
 <div class="card"><div class="mute">in-game size (~64 px, one cell)</div><canvas id="c64" width="64" height="64"></canvas></div>
 <div class="card"><div class="mute">native 256 px</div><canvas id="c1" width="256" height="256"></canvas></div>
 <div class="card"><div class="mute">enlarged, nearest neighbour</div><canvas id="cz"></canvas></div>
</div>
<div class="card" style="margin-top:12px"><div class="mute">all frames (native, same canvas)</div><canvas id="strip"></canvas></div>
<script>
const SETS=__DATA__;
const GUIDES=__GUIDE__;
let cur=Object.keys(SETS)[0], imgs=[], k=0, playing=true, last=0, acc=0;
const $=id=>document.getElementById(id);
function loadSet(name){cur=name;imgs=SETS[name].map(src=>{const i=new Image();i.src=src;return i});k=0;}
function guides(ctx,s){const GUIDE=GUIDES[cur]||{};ctx.save();ctx.lineWidth=Math.max(1,s/2);
 if($('gx').checked){ctx.strokeStyle='rgba(255,255,255,.9)';ctx.beginPath();ctx.moveTo(128*s,0);ctx.lineTo(128*s,256*s);ctx.moveTo(0,128*s);ctx.lineTo(256*s,128*s);ctx.stroke();}
 if($('ge').checked&&GUIDE.eye){ctx.strokeStyle='#3f8';ctx.beginPath();const[a,b]=GUIDE.eye;ctx.moveTo(a[0]*s,a[1]*s);ctx.lineTo(b[0]*s,b[1]*s);ctx.stroke();}
 if($('gs').checked&&GUIDE.shoulder){ctx.strokeStyle='#ff0';ctx.beginPath();const[a,b]=GUIDE.shoulder;ctx.moveTo(a[0]*s,a[1]*s);ctx.lineTo(b[0]*s,b[1]*s);ctx.stroke();
  ctx.strokeStyle='rgba(255,255,0,.6)';for(const sm of (GUIDE.seams||[])){ctx.beginPath();ctx.moveTo(sm[0][0]*s,sm[0][1]*s);ctx.lineTo(sm[1][0]*s,sm[1][1]*s);ctx.stroke();}}
 if($('gb').checked&&GUIDE.body){ctx.strokeStyle='rgba(0,230,255,.9)';ctx.beginPath();GUIDE.body.forEach((p,i)=>i?ctx.lineTo(p[0]*s,p[1]*s):ctx.moveTo(p[0]*s,p[1]*s));ctx.closePath();ctx.stroke();}
 ctx.restore();}
function draw(){const im=imgs[k]; if(!im||!im.complete) return;
 const z=+$('zm').value, cz=$('cz'); if(cz.width!=256*z){cz.width=256*z;cz.height=256*z;}
 for(const [c,s] of [[$('c64'),0.25],[$('c1'),1],[cz,z]]){const x=c.getContext('2d');x.imageSmoothingEnabled=(s<1);
  x.fillStyle='#6d6455';x.fillRect(0,0,c.width,c.height);x.drawImage(im,0,0,256*s,256*s);if(s>=1)guides(x,s);}
 $('fr').textContent=`${cur}  frame ${k+1}/${imgs.length}`;}
function strip(){const c=$('strip'),n=imgs.length;c.width=Math.min(256*n,256*8);c.height=256*Math.ceil(n/8);const x=c.getContext('2d');x.fillStyle='#6d6455';x.fillRect(0,0,c.width,c.height);
 imgs.forEach((im,i)=>{const go=()=>{x.drawImage(im,(i%8)*256,Math.floor(i/8)*256);x.save();x.translate((i%8)*256,Math.floor(i/8)*256);guides(x,1);x.restore();x.fillStyle='#fff';x.fillText(i+1,(i%8)*256+4,Math.floor(i/8)*256+12)};im.complete?go():im.onload=go;});}
function tick(t){const ms=1000*(+$('tpf').value)/(60*(+$('spd').value));if(playing){acc+=t-last;while(acc>=ms){acc-=ms;k=(k+1)%imgs.length;}}last=t;draw();requestAnimationFrame(tick);}
$('set').onchange=e=>{loadSet(e.target.value);strip();};
$('pp').onclick=()=>{playing=!playing;$('pp').textContent=playing?'pause':'play';};
$('st').onclick=()=>{playing=false;$('pp').textContent='play';k=(k+1)%imgs.length;draw();};
for(const id of ['gx','ge','gs','gb','zm']) $(id).onchange=()=>{draw();strip();};
loadSet(cur);strip();requestAnimationFrame(t=>{last=t;tick(t)});
</script></body></html>
"""


def cmd_html(a) -> int:
    """Each --frames spec is DIR[:label][@facing]; a set with its own @facing (e.g. an east sanity set beside the south
    bakes) reads <prefix><k>_<facing>.png and gets guides only when --config describes that facing."""
    sets, guides = {}, {}
    for spec in a.frames:
        facing = a.facing
        if "@" in spec:
            spec, facing = spec.rsplit("@", 1)
        d, label = (spec.rsplit(":", 1) if ":" in spec[2:] else (spec, ""))
        label = label or Path(d).name
        paths = FL.frame_paths(Path(d), a.prefix, facing)
        sets[label] = ["data:image/png;base64," + base64.b64encode(p.read_bytes()).decode() for p in paths]
        guide = {}
        if a.config and facing in json.loads(Path(a.config).read_text())["facings"]:
            cfg, fc = load(a.config, facing)
            if fc.get("eyes"):
                guide["eye"] = fc["eyes"][:2]
            hinges = [w["hinge"] for w in fc.get("wings", [])][:2]
            if len(hinges) == 2:
                guide["shoulder"] = hinges
            guide["seams"] = [w["seam"] for w in fc.get("wings", []) if w.get("seam")]
            guide["body"] = fc["protect"][0] if fc.get("protect") else None
        guides[label] = guide
    opts = "".join(f"<option>{k}</option>" for k in sets)
    html = (HTML.replace("__TITLE__", a.title).replace("__SETS__", opts).replace("__TPF__", str(a.tpf))
            .replace("__DATA__", json.dumps(sets)).replace("__GUIDE__", json.dumps(guides)))
    Path(a.out).write_text(html)
    print(a.out)
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="verb", required=True)
    for name in ("split", "bake", "sheet"):
        p = sub.add_parser(name)
        p.add_argument("config")
        p.add_argument("--master", required=True)
        p.add_argument("--out", required=True)
        if name == "bake":
            p.add_argument("--tag", default="raw")
        if name == "sheet":
            p.add_argument("--frames", required=True)
    h = sub.add_parser("html")
    h.add_argument("--frames", nargs="+", required=True, help="DIR[:label][@facing], one per selectable set")
    h.add_argument("--prefix", required=True)
    h.add_argument("--facing", default="south")
    h.add_argument("--tpf", type=int, default=10)
    h.add_argument("--config")
    h.add_argument("--title", default="Uvak south flap")
    h.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    return {"split": cmd_split, "bake": cmd_bake, "sheet": cmd_sheet, "html": cmd_html}[a.verb](a)


if __name__ == "__main__":
    sys.exit(main())
