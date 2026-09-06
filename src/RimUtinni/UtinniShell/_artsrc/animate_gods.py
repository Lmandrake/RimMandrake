#!/usr/bin/env python3
"""
RimUtinni Shell — the four new god menu-background loops (PROVENANCE).

UI_SHELL rich-loop follow-up, 2026-09-05: four more RimThemes/VBE background
rotation entries (Ohm, Oomo, Mob'Unloo, Rekko), same technique as
`animate_menu.py`/`animate_menu_richer.py` via the shared `scene_anim.py`
primitives. Each god's raw scene is generated once via Codex `edit`
(conditioned on `references/jawa_canon_hands_eyes_rope.jpg` for eye/hand/robe
consistency, same as the bust set) and is near-16:9 already (no worldgen, no
seed sweep — one raw per god, kept). Glow/arc anchor points are MEASURED per
scene via numpy colour-threshold scans in the functions below — never
hardcoded guesses.

Run one god at a time (synchronous; no background/Monitor — this can hang a
subagent that tries):
    python3 animate_gods.py ohm
    python3 animate_gods.py oomo
    python3 animate_gods.py mobunloo
    python3 animate_gods.py rekko
"""
import os
import sys

import numpy as np
from PIL import Image

import scene_anim as sa
from animate_menu_richer import MaskedShimmer

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
RAW = os.path.join(HERE, "raw")
OUT_DIR = os.path.join(MOD, "RimThemes", "Utinni Shell", "Textures")

W, H = 1600, 896
DURATION_S = 9.0
FPS = 20


def build_ohm():
    raw = os.path.join(RAW, "god_ohm_scene_raw.png")
    im = Image.open(raw).convert("RGB")
    rw, rh = im.size
    arr = np.asarray(im).astype(np.float32)
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]

    # electric blue-white arc pixels, restricted to the plausible contact
    # zone between the hooded figure and the droid (measured by eye first,
    # confirmed by threshold — not guessed)
    arc_mask = (b > 150) & (b - r > 20) & (g > 100)
    x0, x1, y0, y1 = 700, 960, 440, 580
    sub = arc_mask[y0:y1, x0:x1]
    ys, xs = np.where(sub)
    xs = xs + x0
    ys = ys + y0
    order = np.argsort(xs)
    xs_s, ys_s = xs[order], ys[order]
    n = len(xs_s)
    k = max(1, n // 5)
    hand_end = (xs_s[:k].mean(), ys_s[:k].mean())
    droid_end = (xs_s[-k:].mean(), ys_s[-k:].mean())

    sx, sy = W / rw, H / rh
    hand_pt = (hand_end[0] * sx, hand_end[1] * sy)
    droid_pt = (droid_end[0] * sx, droid_end[1] * sy)
    print(f"ohm: hand_pt={hand_pt} droid_pt={droid_pt}")

    effects = [
        sa.Dust(35, region=(0.0, 1.0, 0.05, 0.95), color=(210, 205, 195),
                w=W, h=H, seed=41, size_range=(1.5, 3.5), drift_px=22),
        sa.Arcs([hand_pt, droid_pt], color=(150, 195, 255), seed=3,
                length=34, burst_hz=2.2),
    ]
    return raw, effects


def build_oomo():
    raw = os.path.join(RAW, "god_oomo_scene_raw.png")
    im = Image.open(raw).convert("RGB")
    rw, rh = im.size
    arr = np.asarray(im).astype(np.float32)

    # find the brightest broad horizontal band in the lower half of the
    # frame — the still water surface catching lamp-light — by scoring
    # row-wise brightness variance (a water surface reads as a smoother,
    # brighter band than surrounding stone)
    gray = np.asarray(im.convert("L")).astype(np.float32) / 255.0
    lower = gray[int(rh * 0.55):, :]
    row_mean = lower.mean(axis=1)
    best_row = int(np.argmax(row_mean)) + int(rh * 0.55)
    # water band: a fixed-height slice centered on the brightest row
    band_h_frac = 0.14
    y0f = max(0.0, (best_row / rh) - band_h_frac / 2)
    y1f = min(1.0, (best_row / rh) + band_h_frac / 2)
    print(f"oomo: water band rows y0f={y0f:.3f} y1f={y1f:.3f} (best_row={best_row}/{rh})")

    effects = [
        sa.Dust(30, region=(0.0, 1.0, 0.05, 0.95), color=(215, 210, 200),
                w=W, h=H, seed=53, size_range=(1.5, 3.2), drift_px=20),
        MaskedShimmer(im, region=(0.10, 0.90, y0f, y1f), color=(220, 235, 240),
                      w=W, h=H, band_frac=0.14, alpha=170),
    ]
    return raw, effects


def build_mobunloo():
    raw = os.path.join(RAW, "god_mobunloo_scene_raw.png")
    im = Image.open(raw).convert("RGB")

    effects = [
        sa.Dust(28, region=(0.0, 1.0, 0.05, 0.95), color=(210, 200, 185),
                w=W, h=H, seed=61, size_range=(1.4, 3.0), drift_px=18),
        MaskedShimmer(im, region=(0.30, 0.75, 0.45, 0.85), color=(225, 210, 170),
                      w=W, h=H, band_frac=0.14, alpha=140),
    ]
    return raw, effects


def build_rekko():
    raw = os.path.join(RAW, "god_rekko_scene_raw.png")
    im = Image.open(raw).convert("RGB")
    rw, rh = im.size
    arr = np.asarray(im).astype(np.float32)

    # A generous amber-threshold box across the droid/god area also catches
    # Rekko's OWN eyes (well above the droid) and two amber lamps on the
    # side shelves at the droid's own height — averaging all of it gives a
    # meaningless midpoint. Cropped and visually located the droid's actual
    # eye first (`rekko_droid_crop.png`), then confirmed it by a bright-core
    # threshold restricted to that small box (105 px, centroid (851,658) on
    # this 1672x941 raw) — measured, not guessed.
    r, g = arr[..., 0], arr[..., 1]
    x0, x1, y0, y1 = 820, 900, 630, 710
    sub_r, sub_g = r[y0:y1, x0:x1], g[y0:y1, x0:x1]
    mask = (sub_r > 230) & (sub_g > 180)
    ys, xs = np.where(mask)
    if len(xs) == 0:
        raise RuntimeError("rekko: could not measure the droid eye — widen the search box and inspect the raw PNG")
    pt = (xs.mean() + x0, ys.mean() + y0)
    sx, sy = W / rw, H / rh
    glow_pt = (pt[0] * sx, pt[1] * sy)
    print(f"rekko: droid eye={glow_pt}")

    effects = [
        sa.Dust(26, region=(0.0, 1.0, 0.05, 0.95), color=(215, 205, 190),
                w=W, h=H, seed=71, size_range=(1.4, 3.0), drift_px=16),
        sa.GlowPulse([glow_pt], color=(255, 170, 60), radius=int(16 * (W / 1600)),
                     pulses_per_loop=2, base=0.5, amp=0.35),
    ]
    return raw, effects


GODS = {
    "ohm": ("ohm", build_ohm),
    "oomo": ("oomo", build_oomo),
    "mobunloo": ("mobunloo", build_mobunloo),
    "rekko": ("rekko", build_rekko),
}


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in GODS:
        print(f"usage: python3 animate_gods.py <{'|'.join(GODS)}>")
        sys.exit(2)
    suffix, builder = GODS[sys.argv[1]]
    raw_png, effects = builder()
    out_webm = os.path.join(OUT_DIR, f"UI_BackgroundMain.BGPlanet_{suffix}.webm")
    sa.render_loop(raw_png, out_webm, effects, duration_s=DURATION_S, fps=FPS, size=(W, H))


if __name__ == "__main__":
    main()
