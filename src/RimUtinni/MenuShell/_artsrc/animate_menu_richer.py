#!/usr/bin/env python3
"""
RimUtinni Shell — RICHER Ishko-gate menu-background loop (PROVENANCE).

Owner, 2026-09-05: "make that movie richer, more interesting, and longer now
that we know how." Builds on `animate_menu.py` (the shipped 5s loop) using
the shared primitives in `scene_anim.py`, reusing the SAME approved base
still (`Textures/UI/Backgrounds/utinni_menu_1.png` — not regenerated).

What's added over the shipped version:
  - Duration 5s -> 9s (still loops cleanly: every periodic effect below uses
    an integer cycle count per loop).
  - A second, higher/finer dust layer around the hull-dome schematic band,
    for parallax depth (the original single dune-level layer is kept too).
  - A `Shimmer` sweep across the ship-hull's vector-line schematic band —
    one slow pale scanner-pulse per loop, low alpha, so it reads as a
    targeting-scanner/power-pulse glint on the circuitry rather than a
    light show.
  - Eyes re-measured on the CURRENT PNG via the same numpy amber-threshold
    scan as `animate_menu.py` (not copied from that file) — two clusters at
    (1244,1221) and (1320,1222) on the 2560x1440 source, matching the
    original measurement almost exactly (same unedited base image).

Output is a CANDIDATE first (`...BGPlanet.webm.candidate`), reviewed as a
frame extract, then promoted over the shipped `UI_BackgroundMain.BGPlanet.webm`
only if clearly better — never overwritten blind.

Run: python3 animate_menu_richer.py
"""
import math
import os
import numpy as np
from PIL import Image, ImageDraw

import scene_anim as sa


class MaskedShimmer:
    """Like scene_anim.Shimmer, but the band's alpha is multiplied by the
    base image's own luminance, sampled fresh each frame at the band's
    current position. Without this, a plain rectangular Shimmer band reads
    as a hard grey BOX over the black sky/black doorway void above and
    inside the hull dome (measured: it does, badly, on the first render of
    this scene) — the mask keeps the glint confined to lit metal/schematic
    pixels, where a scanner-glint actually belongs."""

    def __init__(self, base_rgb, region, color, w, h, band_frac=0.12, alpha=90):
        x0f, x1f, y0f, y1f = region
        self.rect = (int(x0f * w), int(y0f * h), int(x1f * w), int(y1f * h))
        self.color, self.band_frac, self.alpha = color, band_frac, alpha
        self.w, self.h = w, h
        gray = base_rgb.convert("L").resize((w, h), Image.LANCZOS)
        arr = np.asarray(gray).astype(np.float32) / 255.0
        # suppress near-black (sky, doorway interior) so the glint only
        # rides on already-lit metal/schematic lines
        arr = np.clip((arr - 0.14) / 0.45, 0, 1) ** 0.8
        self.mask = arr

    def draw(self, frame, t):
        x0, y0, x1, y1 = self.rect
        rw = x1 - x0
        band_w = max(1, int(rw * self.band_frac))
        bh = y1 - y0
        cx = x0 + int((t % 1.0) * (rw + band_w)) - band_w

        grad = Image.new("RGBA", (band_w, bh), (0, 0, 0, 0))
        gd = ImageDraw.Draw(grad)
        for i in range(band_w):
            a = int(self.alpha * math.sin(math.pi * i / max(1, band_w - 1)))
            gd.line([(i, 0), (i, bh)], fill=self.color + (max(0, a),))

        gx0, gy0, gx1, gy1 = cx, y0, cx + band_w, y1
        fx0, fy0 = max(0, gx0), max(0, gy0)
        fx1, fy1 = min(self.w, gx1), min(self.h, gy1)
        if fx1 <= fx0 or fy1 <= fy0:
            return
        sub = grad.crop((fx0 - gx0, fy0 - gy0, fx1 - gx0, fy1 - gy0))
        mask_crop = self.mask[fy0:fy1, fx0:fx1]
        a_arr = np.asarray(sub.split()[3]).astype(np.float32) * mask_crop
        sub.putalpha(Image.fromarray(a_arr.astype(np.uint8)))
        frame.alpha_composite(sub, (fx0, fy0))

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
SRC_PNG = os.path.join(MOD, "Textures", "UI", "Backgrounds", "utinni_menu_1.png")
CANDIDATE_WEBM = os.path.join(
    MOD, "RimThemes", "Utinni Shell", "Textures",
    "UI_BackgroundMain.BGPlanet.webm.candidate",
)

W, H = 1600, 896
DURATION_S = 9.0
FPS = 20


def measure_eyes():
    """Amber-threshold scan of the ACTUAL current PNG, clustered by
    proximity — not hardcoded from animate_menu.py."""
    src = Image.open(SRC_PNG).convert("RGB")
    sw, sh = src.size
    arr = np.asarray(src).astype(np.float32)
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    mask = (r > 180) & (g > 90) & (g < 200) & (b < 120) & (r - b > 80)
    ys, xs = np.where(mask)
    pts = list(zip(xs.tolist(), ys.tolist()))
    # cluster: two eyes sit close together near the doorway; anything far
    # from the doorway's expected band (roughly the middle third, upper-mid
    # height) is a stray false positive (a distant lit window etc).
    doorway_pts = [(x, y) for x, y in pts if 0.44 * sw < x < 0.56 * sw and 0.7 * sh < y < 0.95 * sh]
    doorway_pts.sort(key=lambda p: p[0])
    mid = len(doorway_pts) // 2
    left, right = doorway_pts[:mid], doorway_pts[mid:]

    def centroid(cluster):
        xs_ = [p[0] for p in cluster]
        ys_ = [p[1] for p in cluster]
        return sum(xs_) / len(xs_), sum(ys_) / len(ys_)

    eye_l = centroid(left)
    eye_r = centroid(right)
    scale = W / sw
    print(f"measured eyes on {sw}x{sh}: L={eye_l} R={eye_r}")
    return [(eye_l[0] * scale, eye_l[1] * scale), (eye_r[0] * scale, eye_r[1] * scale)]


def main():
    eyes = measure_eyes()
    base_rgb = Image.open(SRC_PNG).convert("RGB")

    effects = [
        # foreground dune-level dust (as shipped): bigger, faster, lower band
        sa.Dust(55, region=(0.0, 1.0, 0.58, 0.97), color=(224, 214, 190),
                w=W, h=H, seed=11, size_range=(2.0, 4.5), drift_px=50),
        # NEW: finer, slower dust hugging the hull/schematic band for depth
        # (kept just below the dome apex so it never floats over black sky)
        sa.Dust(24, region=(0.20, 0.80, 0.62, 0.72), color=(200, 210, 214),
                w=W, h=H, seed=29, size_range=(1.2, 2.4), drift_px=16),
        # breathing fog along the dune line (as shipped)
        sa.Fog(y0=int(H * 0.62), height=int(H * 0.32), color=(150, 158, 165),
               w=W, amt=0.10, breathe_amt=0.05, seed=5),
        # NEW: one slow pale scanner-pulse sweeping across the hull's
        # vector-line schematic band per loop — luminance-masked so it only
        # rides the lit metal/schematic lines, never the black sky/doorway
        MaskedShimmer(base_rgb, region=(0.27, 0.68, 0.64, 0.90),
                      color=(210, 225, 235), w=W, h=H, band_frac=0.16, alpha=150),
        # pulsing eyes, re-measured on the current PNG
        sa.GlowPulse(eyes, color=(255, 150, 40), radius=int(26 * (W / 1600)),
                     pulses_per_loop=3, base=0.55, amp=0.45),
    ]

    sa.render_loop(SRC_PNG, CANDIDATE_WEBM, effects, duration_s=DURATION_S, fps=FPS, size=(W, H))


if __name__ == "__main__":
    main()
