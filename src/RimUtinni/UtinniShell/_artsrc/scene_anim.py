#!/usr/bin/env python3
"""
RimUtinni Shell — shared scene-animation primitives (PROVENANCE).

Generalizes the technique proven in `animate_menu.py` (the Ishko-gate loop:
drifting dust, breathing fog, pulsing eye-glow) into reusable building
blocks so every god's animated background/scene uses the same quality bar
and the same measured fixes, instead of each being reinvented:

  - VP8 (`libvpx`), never VP9 — Unity's VideoPlayer hard-errors on VP9
    (measured live, UI_SHELL_SLICE_BUILD_1, 2026-09-05).
  - Frame dims divisible by 16 (no macro-block padding warning/stretch).
  - Dust/glow sprites are drawn oversampled then downscaled — a raw few-px
    PIL ellipse renders as a hard plus/star, not a soft round mote.
  - A drifting fog/haze band must fade to zero at both its own top AND
    bottom edge (smoothstep), or it reads as a visible hard-edged rectangle
    laid over the scene.

Effects available, composable per scene:
  - dust(n, region, color)      — soft drifting motes, looping via modulo
  - fog(y0, height, color, amt) — a breathing, horizontally-drifting haze band
  - glow_pulse(points, color, radius, pulses_per_loop) — soft point-glow(s)
    breathing in brightness (e.g. eyes, embers, an instrument light)
  - arcs(points, color, n_per_burst) — jagged lightning-bolt flicker bursts
    between/around given points (electric-arc gods)
  - shimmer(region, color, band_h) — a soft light band sweeping across a
    region once per loop (water glint, metal sheen)

Usage: import and call `render_loop(base_png, out_webm, effects, duration_s, fps)`.
"""
import math
import os
import random

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFilter


def make_soft_sprite(radius, color, peak_alpha=160, supersample=4):
    """A soft round sprite via oversample-then-downscale (never a raw small
    PIL ellipse, which renders as a hard plus/star at a few px radius)."""
    ss = supersample
    d = (radius * 2 + 4) * ss
    im = Image.new("RGBA", (d, d), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    cx = cy = d / 2
    r_ss = radius * ss
    dr.ellipse([cx - r_ss, cy - r_ss, cx + r_ss, cy + r_ss], fill=color + (peak_alpha,))
    im = im.filter(ImageFilter.GaussianBlur(radius=r_ss * 0.6))
    final = max(4, radius * 2 + 4)
    return im.resize((final, final), Image.LANCZOS)


def make_glow_sprite(radius, color, peak_alpha=200, falloff=1.6):
    d = radius * 2
    im = Image.new("RGBA", (d, d), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    for r in range(radius, 0, -1):
        a = int(peak_alpha * (1 - r / radius) ** falloff)
        dr.ellipse([radius - r, radius - r, radius + r, radius + r], fill=color + (a,))
    return im


def make_fade_band(width, height, seed=0, edge_fade_top=0.35, edge_fade_bottom=0.25):
    """A horizontally-tileable soft noise band, pre-faded to zero at both
    edges (no hard seam when composited over a still image)."""
    rng = np.random.RandomState(seed)
    noise = rng.rand(height, width).astype(np.float32)
    im = Image.fromarray((noise * 255).astype(np.uint8), "L")
    im = im.filter(ImageFilter.GaussianBlur(radius=max(width, height) * 0.03))
    arr = np.asarray(im).astype(np.float32)
    arr = (arr - arr.min()) / (arr.max() - arr.min() + 1e-6)
    y = np.linspace(0, 1, height)
    fi = np.clip(y / edge_fade_top, 0, 1); fi = fi * fi * (3 - 2 * fi)
    fo = np.clip((1 - y) / edge_fade_bottom, 0, 1); fo = fo * fo * (3 - 2 * fo)
    arr *= np.minimum(fi, fo)[:, None]
    return arr


class Dust:
    def __init__(self, n, region, color, w, h, seed=11, size_range=(2.0, 4.5), drift_px=50):
        rng = random.Random(seed)
        (x0f, x1f, y0f, y1f) = region  # fractions of w,h
        self.items = []
        for _ in range(n):
            x0 = rng.uniform(x0f * w, x1f * w)
            y0 = rng.uniform(y0f * h, y1f * h)
            depth = rng.uniform(0.4, 1.0)
            r = max(2, int(round(rng.uniform(*size_range) * depth)))
            sprite = make_soft_sprite(r, color, peak_alpha=int(70 + 50 * depth))
            self.items.append((x0, y0, sprite, drift_px * depth))
        self.w = w

    def draw(self, frame, t):
        for x0, y0, sprite, drift in self.items:
            x = (x0 + t * drift) % self.w
            sw, sh = sprite.size
            frame.alpha_composite(sprite, (int(x - sw / 2), int(y0 - sh / 2)))


class Fog:
    def __init__(self, y0, height, color, w, amt=0.13, breathe_amt=0.05, seed=5):
        self.y0, self.h, self.color, self.w = y0, height, color, w
        self.amt, self.breathe_amt = amt, breathe_amt
        self.noise = make_fade_band(w, height, seed=seed)

    def draw(self, frame, t):
        shift = int(t * self.w) % self.w
        rolled = np.roll(self.noise, shift, axis=1)
        breathe = 0.5 + 0.5 * math.sin(2 * math.pi * t)
        alpha = (rolled * (self.amt + self.breathe_amt * breathe) * 255).astype(np.uint8)
        rgba = np.zeros((self.h, self.w, 4), dtype=np.uint8)
        rgba[..., 0:3] = self.color
        rgba[..., 3] = alpha
        frame.alpha_composite(Image.fromarray(rgba, "RGBA"), (0, self.y0))


class GlowPulse:
    def __init__(self, points, color, radius, pulses_per_loop=2, base=0.55, amp=0.45):
        self.points, self.pulses = points, pulses_per_loop
        self.base, self.amp = base, amp
        self.sprite = make_glow_sprite(radius, color)

    def draw(self, frame, t):
        pulse = self.base + self.amp * math.sin(2 * math.pi * t * self.pulses)
        gw, gh = self.sprite.size
        tinted = self.sprite.copy()
        a = tinted.split()[3].point(lambda v: int(v * pulse))
        tinted.putalpha(a)
        for ex, ey in self.points:
            frame.alpha_composite(tinted, (int(ex - gw / 2), int(ey - gh / 2)))


class Arcs:
    """Jagged lightning-bolt flicker bursts near given points — electric,
    chaotic gods (Ohm, Zizzik). Bolts flash on/off in short random bursts."""
    def __init__(self, points, color, seed=3, length=40, burst_hz=3.0):
        self.points, self.color, self.length, self.burst_hz = points, color, length, burst_hz
        self.rng = random.Random(seed)

    def _bolt(self, draw, ox, oy, alpha):
        x, y = ox, oy
        pts = [(x, y)]
        for _ in range(5):
            x += self.rng.uniform(-self.length / 5, self.length / 5)
            y += self.rng.uniform(-self.length / 4, 0)
            pts.append((x, y))
        draw.line(pts, fill=self.color + (alpha,), width=2)

    def draw(self, frame, t):
        phase = (t * self.burst_hz) % 1.0
        if phase > 0.25:  # off most of the time -> reads as flicker, not constant
            return
        alpha = int(255 * (1 - phase / 0.25))
        d = ImageDraw.Draw(frame, "RGBA")
        for px, py in self.points:
            if self.rng.random() < 0.7:
                self._bolt(d, px, py, alpha)


class Shimmer:
    """A soft light band sweeping across a region once per loop (water
    glint, metal sheen) — Oomo, Rekko."""
    def __init__(self, region, color, w, h, band_frac=0.12, alpha=90):
        (x0f, x1f, y0f, y1f) = region
        self.rect = (int(x0f * w), int(y0f * h), int(x1f * w), int(y1f * h))
        self.color, self.band_frac, self.alpha = color, band_frac, alpha

    def draw(self, frame, t):
        x0, y0, x1, y1 = self.rect
        rw = x1 - x0
        band_w = int(rw * self.band_frac)
        cx = x0 + int((t % 1.0) * (rw + band_w)) - band_w
        grad = Image.new("RGBA", (max(1, band_w), y1 - y0), (0, 0, 0, 0))
        gd = ImageDraw.Draw(grad)
        for i in range(band_w):
            a = int(self.alpha * math.sin(math.pi * i / max(1, band_w - 1)))
            gd.line([(i, 0), (i, y1 - y0)], fill=self.color + (max(0, a),))
        frame.alpha_composite(grad, (cx, y0))


def render_loop(base_png, out_webm, effects, duration_s=8.0, fps=20, size=None):
    """effects: list of objects with .draw(frame, t) for t in [0,1). Frame
    dims are taken from base_png (resized to `size` if given, forced to a
    multiple of 16 either way)."""
    base = Image.open(base_png).convert("RGB")
    w, h = size if size else base.size
    w -= w % 16
    h -= h % 16
    base = base.resize((w, h), Image.LANCZOS)

    n_frames = int(fps * duration_s)
    os.makedirs(os.path.dirname(out_webm), exist_ok=True)
    writer = imageio_ffmpeg.write_frames(
        out_webm, (w, h), fps=fps, codec="libvpx",
        output_params=["-b:v", "2200k", "-crf", "10", "-deadline", "good"],
    )
    writer.send(None)
    for i in range(n_frames):
        t = i / n_frames
        frame = base.copy().convert("RGBA")
        for eff in effects:
            eff.draw(frame, t)
        writer.send(np.asarray(frame.convert("RGB")))
        if i % max(1, n_frames // 5) == 0:
            print(f"  frame {i}/{n_frames}")
    writer.close()
    print("wrote", out_webm)
