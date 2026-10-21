#!/usr/bin/env python3
"""Uvak wing recolour to canon (UVAK_WINGS_RESKIN_TO_CANON).

Canon (design/RimStarWars/canon_references/uvak/description.md): wing membrane a translucent DULL PINKISH-BROWN with
darker finger-bone ribs; never vivid red-orange. Target chroma is sampled from our own Uvak_Dessicated wing membrane,
which already reads as that pinkish-brown.

Only pixels that are (a) inside a wing layer of the flyer_cutout config (split(), the same cut the rebuild uses) and
(b) red-orange (hue <= ~40 deg or >= ~330 deg, saturation > SAT_MIN) change. Lightness L* is kept (texture, veins,
shading); a*, b* are moved to the target mean plus a damped copy of the pixel's own deviation. Ribs and outlines are
low-saturation and fall outside (b). The plate (body, mouth, eyes) is never touched.

usage: Uvak_recolour.py SRC_DIR OUT_DIR CONFIG  (SRC_DIR = the pre-rebuild frames at 842bca0^; then flyer_cutout.py build --src OUT_DIR)     copies every frame, rewrites the master frame of each cutout facing
"""
import json
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import flyer_cutout as FC  # noqa: E402

SAT_MIN = 0.22
DAMP = 0.55     # how much of each pixel's own chroma deviation survives
L_SCALE = 0.97  # a hair darker: membrane is translucent, not glowing
ROOT_PX = 20    # wing-root membrane kept in the plate: within this many px of a wing layer ...
ROOT_H0, ROOT_H1 = 36.0, 42.0   # ... and RED by Lab hue angle (membrane ~35 deg incl. its dark shadows; body brown/tan
ROOT_C0, ROOT_C1 = 6.0, 12.0    #     sits at 40-90 deg), with C* above ~6; both ramps blend instead of cutting
EXCLUDE = {"south": [[[128, 66], [160, 66], [160, 104], [128, 104]]],     # the open mouth (red, stays red)
           "east": [[[226, 128], [256, 128], [256, 156], [226, 156]]]}

_M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
_WP = np.array([0.95047, 1.0, 1.08883])


def rgb2lab(rgb):
    c = np.where(rgb > 0.04045, ((rgb + 0.055) / 1.055) ** 2.4, rgb / 12.92)
    xyz = c @ _M.T / _WP
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def lab2rgb(lab):
    fy = (lab[..., 0] + 16) / 116
    fx, fz = fy + lab[..., 1] / 500, fy - lab[..., 2] / 200
    f = np.stack([fx, fy, fz], -1)
    xyz = np.where(f ** 3 > 0.008856, f ** 3, (f - 16 / 116) / 7.787) * _WP
    c = xyz @ np.linalg.inv(_M).T
    rgb = np.where(c > 0.0031308, 1.055 * np.clip(c, 0, None) ** (1 / 2.4) - 0.055, 12.92 * c)
    return np.clip(rgb, 0, 1)


def hsv_hs(rgb):
    mx, mn = rgb.max(-1), rgb.min(-1)
    d = mx - mn
    s = np.where(mx > 0, d / np.maximum(mx, 1e-6), 0)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    h = np.where(mx == r, ((g - b) / np.maximum(d, 1e-6)) % 6, np.where(mx == g, (b - r) / np.maximum(d, 1e-6) + 2,
                                                                         (r - g) / np.maximum(d, 1e-6) + 4)) * 60
    return np.where(d > 0, h, 0), s


def target_from_dessicated(p):
    a = np.asarray(Image.open(p).convert("RGBA")).astype(float) / 255
    rgb = a[..., :3]
    lab, (h, s) = rgb2lab(rgb), hsv_hs(rgb)
    mem = (a[..., 3] > 0.9) & (s > 0.12) & ((h < 40) | (h > 330)) & (lab[..., 0] > 45)
    return lab[mem].mean(0), int(mem.sum())


def red_mask(rgba):
    rgb = rgba[..., :3].astype(float) / 255
    h, s = hsv_hs(rgb)
    return (rgba[..., 3] > 0) & (s > SAT_MIN) & ((h <= 40) | (h >= 330))


def recolour(rgba, sel, tgt, weight=None):
    """Rotate each selected pixel's hue angle to the target's and scale its chroma by target/mean chroma; keep L*."""
    rgb = rgba[..., :3].astype(float) / 255
    lab = rgb2lab(rgb)
    src = lab[sel]
    mu = src.mean(0)
    c_src = np.hypot(src[:, 1], src[:, 2])
    k = np.hypot(tgt[1], tgt[2]) / max(np.hypot(mu[1], mu[2]), 1e-6)
    ang = np.arctan2(tgt[2], tgt[1])
    new = src.copy()
    new[:, 0] = src[:, 0] * L_SCALE
    new[:, 1] = c_src * k * np.cos(ang)
    new[:, 2] = c_src * k * np.sin(ang)
    if weight is not None:
        wv = weight[sel][:, None]
        new = wv * new + (1 - wv) * src
    out = rgba.copy()
    out[..., :3][sel] = np.round(lab2rgb(new) * 255).astype(np.uint8)
    return out, mu


def main():
    src, out, cfgp = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    cfg = json.loads(cfgp.read_text())
    out.mkdir(parents=True, exist_ok=True)
    for p in src.glob(cfg["prefix"] + "*.png"):
        shutil.copy(p, out / p.name)
    tgt, n = target_from_dessicated(str(Path(__file__).resolve().parents[4] / "RimStarWars/SWBestiary/Textures/swanimals/Uvak") + "/"
                                    "Uvak_Dessicated.png")
    print(f"target Lab {tgt.round(1)} from {n} Dessicated membrane px")
    for facing, fc in cfg["facings"].items():
        if fc.get("translate"):
            continue
        mp = out / f"{cfg['prefix']}{fc['master']}_{facing}.png"
        m = np.asarray(Image.open(mp).convert("RGBA"))
        _, wings = FC.split(m, fc)
        inwing = np.logical_or.reduce([w[..., 3] > 0 for w in wings])
        red = red_mask(m)
        lab = rgb2lab(m[..., :3].astype(float) / 255)
        chroma = np.hypot(lab[..., 1], lab[..., 2])
        near = FC.distance_from(inwing, ROOT_PX) < ROOT_PX
        excl = np.zeros(m.shape[:2], bool)
        for poly in EXCLUDE.get(facing, []):
            excl |= FC.poly_mask(m.shape[:2], [poly])
        hue = np.degrees(np.arctan2(lab[..., 2], lab[..., 1]))
        ramp = lambda v, a, b: np.clip((v - a) / (b - a), 0, 1)  # noqa: E731
        wroot = np.maximum(ramp(-hue, -ROOT_H1, -ROOT_H0) * ramp(chroma, ROOT_C0, ROOT_C1),
                           ramp(-hue, -50, -44) * ramp(chroma, 24, 30))     # bright membrane highlights lean orange
        wroot *= (hue > -40) & (m[..., 3] > 0)
        root = ~inwing & near & (wroot > 0) & ~excl
        sel = (inwing & red) | root
        weight = np.ones(m.shape[:2])
        weight[root] = wroot[root]
        res, mu = recolour(m, sel, tgt, weight)
        Image.fromarray(res, "RGBA").save(mp)
        outside = red & ~sel
        print(f"{facing}: master {fc['master']} recoloured {int(sel.sum())} px (src Lab mean {mu.round(1)}); "
              f"red px left OUTSIDE wing layers (plate, untouched): {int(outside.sum())}")


if __name__ == "__main__":
    main()
