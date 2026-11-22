#!/usr/bin/env python3
"""Generator-free look options for RIMMANDRAKE_REDRAW_FLOWWORKS_TANKS_THREE_STYLES_ONLY_SCRAPPER_READS_RIGHT.

Owner 2026-11-22 (FlowWorks walk): Industrial tank "is a bit... rusty. Could we clean up some of the rust a bit? Otherwise
it reads well."; Modern tank "reads very cartoonish, needs to be more realistic with some smudges and normal wear";
Modern pipes and sprinkler "need to have a little bit of "realism" added in terms of some patches of differently colored
paint or other non-cartoonishness added ... They look plastic."

Every option here is a REPAINT of the shipped texture: only colour moves, the alpha channel is copied byte for byte, so
the canvas, footprint and every fitted geometry (pipe atlas seams, port stubs, seat math) stay exactly as shipped.
Deterministic (fixed seeds). Look briefs: design/specs/2026-11-22-flowworks-look-briefs/looks.md.

Pipe atlas seam rule: the paint fields are periodic with period C (the displayed cell, 132 px) and are sampled at each
tile's own cell coordinates ((x - P) mod C, (y - P) mod C). A tile's inner edge line and its neighbour's padding
continuation therefore get the same paint, so check_pipe_atlas.py stays at 0 failures (it is run on every output).

    repaint_options.py OUT_DIR       writes OUT_DIR/<option>.png for every option below
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
TEX = HERE.parents[1] / "Textures/RimMandrake/FlowWorks"

# ---------------------------------------------------------------- helpers

def load(p):
    return np.asarray(Image.open(p).convert("RGBA")).astype(np.float32) / 255.0


def save(a, p):
    Image.fromarray(np.clip(a * 255 + 0.5, 0, 255).astype(np.uint8), "RGBA").save(p)


def blur(f, sigma):
    """Gaussian blur by FFT; wraps at the edges, so a blurred noise field is periodic with the array's own size."""
    h, w = f.shape
    fy = np.fft.fftfreq(h)[:, None]; fx = np.fft.fftfreq(w)[None, :]
    g = np.exp(-2 * (np.pi * sigma) ** 2 * (fx * fx + fy * fy))
    return np.real(np.fft.ifft2(np.fft.fft2(f) * g)).astype(np.float32)


def norm(f):
    lo, hi = np.percentile(f, 1), np.percentile(f, 99)
    return np.clip((f - lo) / max(hi - lo, 1e-6), 0, 1)


def field(shape, sigma, seed, periodic=False):
    """Smooth noise in [0,1]; the FFT blur makes it periodic with period = shape (needed for the pipe atlas)."""
    rng = np.random.default_rng(seed)
    return norm(blur(rng.random(shape).astype(np.float32), sigma))


def aniso_field(shape, sx, sy, seed):
    """Smooth periodic noise in [0,1], stretched: sx and sy are the blur sigmas along x and y."""
    rng = np.random.default_rng(seed)
    f = rng.random(shape).astype(np.float32)
    h, w = shape
    fy = np.fft.fftfreq(h)[:, None]; fx = np.fft.fftfreq(w)[None, :]
    g = np.exp(-2 * np.pi ** 2 * ((sx * fx) ** 2 + (sy * fy) ** 2))
    return norm(np.real(np.fft.ifft2(np.fft.fft2(f) * g)).astype(np.float32))


def streak_field(shape, seed, xs=3.0, ys=40.0):
    """Vertical grime streaks: noise blurred hard along y."""
    rng = np.random.default_rng(seed)
    f = rng.random(shape).astype(np.float32)
    h, w = shape
    fy = np.fft.fftfreq(h)[:, None]; fx = np.fft.fftfreq(w)[None, :]
    g = np.exp(-2 * np.pi ** 2 * ((xs * fx) ** 2 + (ys * fy) ** 2))
    return norm(np.real(np.fft.ifft2(np.fft.fft2(f) * g)).astype(np.float32))


def hsv(rgb):
    mx = rgb.max(-1); mn = rgb.min(-1); d = mx - mn
    s = np.where(mx > 1e-6, d / np.maximum(mx, 1e-6), 0)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    dd = np.maximum(d, 1e-6)
    h = np.where(mx == r, ((g - b) / dd) % 6, np.where(mx == g, (b - r) / dd + 2, (r - g) / dd + 4)) / 6.0
    h = np.where(d < 1e-6, 0, h)
    return h, s, mx


def luma(rgb):
    return rgb[..., 0] * 0.299 + rgb[..., 1] * 0.587 + rgb[..., 2] * 0.114


def ramp(x, lo, hi):
    return np.clip((x - lo) / (hi - lo), 0, 1)


def mix(a, b, w):
    return a * (1 - w[..., None]) + b * w[..., None]


def grain(shape, seed, amp):
    rng = np.random.default_rng(seed)
    return (rng.random(shape).astype(np.float32) - 0.5) * 2 * amp


def matte(rgb, knee=0.86, k=0.45):
    """Compress glossy highlights: plastic reads from hard white specular blobs."""
    v = rgb.max(-1, keepdims=True)
    over = np.clip(v - knee, 0, None)
    return rgb - over * k


# ---------------------------------------------------------------- Industrial: rust cleaned, else as shipped

def industrial_derust():
    a = load(TEX / "Tank/Industrial/RM_LiquidTank.png")
    rgb, al = a[..., :3], a[..., 3]
    h, s, v = hsv(rgb)
    hue = h * 360
    # rust: warm orange-brown, real saturation. Hazard yellow (hue ~40-60, bright) is left alone.
    rust = ramp(s, 0.16, 0.34) * (ramp(hue, 2, 10) * (1 - ramp(hue, 34, 42)))
    hazard = ramp(hue, 36, 44) * (1 - ramp(hue, 62, 70)) * ramp(s, 0.35, 0.55) * ramp(v, 0.45, 0.6)
    rust *= 1 - hazard
    # keep honest wear: a sparse set of rust weeps survives (low-frequency mask, ~12% of the rust)
    keep = ramp(field(al.shape, 6, 101), 0.80, 0.90)
    w = rust * (1 - keep)
    L = luma(rgb)
    # gunmetal paint: the shipped luminance texture, a cool slate tint, lifted slightly (paint, not bare rusted metal)
    paint = np.stack([L * 0.92 + 0.035, L * 0.96 + 0.04, L * 1.02 + 0.05], -1)
    out = mix(rgb, paint, w * 0.92)
    # the surviving weeps darken a touch toward oxide brown (stain, not scale)
    out = mix(out, out * np.array([0.85, 0.72, 0.6]), keep * rust * 0.35)
    return np.concatenate([np.clip(out, 0, 1), al[..., None]], -1)


def industrial_sand():
    """Industrial B: the rust-cleaned drawing in the setting's sand-grey equipment paint (the Star Wars standard side of
    the Industrial look: painted, maintained, desert-dusty). Hazard bands stay; rust weeps stay as stains."""
    a = industrial_derust()
    rgb, al = a[..., :3], a[..., 3]
    h, s, v = hsv(rgb)
    hue = h * 360
    hazard = ramp(hue, 36, 44) * (1 - ramp(hue, 62, 70)) * ramp(s, 0.35, 0.55) * ramp(v, 0.45, 0.6)
    grey = (1 - ramp(s, 0.14, 0.26)) * (1 - hazard) * ramp(luma(rgb), 0.16, 0.26)   # gunmetal paint; the black hazard bands stay black
    L = luma(rgb)
    sand = np.clip(L[..., None] * 1.05 + 0.20, 0, 1) * np.array([1.0, 0.93, 0.78])
    out = mix(rgb, sand, grey * 0.9)
    H, W = al.shape
    ys = np.nonzero(al > 0.5)[0]
    rel = np.clip((np.arange(H, dtype=np.float32)[:, None] - ys.min()) / max(ys.max() - ys.min(), 1), 0, 1) * np.ones((1, W))
    dust = ramp(rel, 0.55, 1.0) * (0.5 + 0.5 * field((H, W), 5, 111)) * 0.35
    out = mix(out, np.array([0.66, 0.58, 0.46]), dust * ramp(al, 0.5, 1))
    out = out + grain((H, W, 1), 112, 0.015) * ramp(al, 0.5, 1)[..., None]
    return np.concatenate([np.clip(out, 0, 1), al[..., None]], -1)


# ---------------------------------------------------------------- Modern tank: realistic weathering of the white leg tank

def modern_tank_weathered():
    a = load(TEX / "Tank/Modern/RM_LiquidTank.png")
    rgb, al = a[..., :3].copy(), a[..., 3]
    H, W = al.shape
    ys, xs = np.nonzero(al > 0.5)
    y0, y1 = ys.min(), ys.max()
    yy = np.arange(H, dtype=np.float32)[:, None] * np.ones((1, W), np.float32)
    rel = np.clip((yy - y0) / max(y1 - y0, 1), 0, 1)           # 0 top of tank, 1 at the feet
    h, s, v = hsv(rgb)
    poly = ramp(v, 0.55, 0.75) * (1 - ramp(s, 0.18, 0.3))      # white / water-blue poly body (not the black cap, not the tap)
    # 1. UV ageing: the poly goes faintly cream, more on the sun-facing top
    cream = np.array([1.0, 0.975, 0.91])
    rgb = mix(rgb, rgb * cream, poly * (0.55 + 0.45 * (1 - rel)))
    # 2. matte: kill the glossy plastic highlight
    rgb = matte(rgb, 0.84, 0.5)
    # 3. desert dust film rising from the feet, broken up by noise
    dust = np.array([0.62, 0.53, 0.42])
    dn = field((H, W), 5, 202)
    dw = ramp(rel, 0.45, 1.0) ** 1.4 * (0.45 + 0.55 * dn) * 0.55
    rgb = mix(rgb, mix(rgb, dust, np.full_like(dw, 0.85)), dw * ramp(al, 0.5, 1))
    # 4. grime streaks running down from the top (rain on dust), faint
    st = streak_field((H, W), 203, 2.0, 30.0)
    sw = ramp(st, 0.62, 0.95) * ramp(rel, 0.05, 0.25) * (1 - ramp(rel, 0.8, 1.0)) * 0.22 * poly
    rgb = mix(rgb, rgb * np.array([0.78, 0.74, 0.68]), sw)
    # 5. smudges: soft grey-brown hand marks near the cap and the tap, and a scuff on the shell
    sm = np.zeros((H, W), np.float32)
    for (cx, cy, r, k) in [(0.50, 0.30, 26, 0.35), (0.12, 0.80, 22, 0.45), (0.80, 0.55, 18, 0.25), (0.33, 0.62, 14, 0.25)]:
        X = xs.min() + cx * (xs.max() - xs.min()); Y = y0 + cy * (y1 - y0)
        d2 = (np.arange(W)[None, :] - X) ** 2 + (np.arange(H)[:, None] - Y) ** 2
        sm += k * np.exp(-d2 / (2 * r * r))
    sm *= 0.55 + 0.45 * field((H, W), 2.5, 204)
    rgb = mix(rgb, rgb * np.array([0.72, 0.68, 0.62]), np.clip(sm, 0, 0.5) * poly)
    # 6. fine grain so flat fills read as a real surface, not vector shading
    rgb = rgb + grain((H, W, 1), 205, 0.022) * ramp(al, 0.5, 1)[..., None]
    return np.concatenate([np.clip(rgb, 0, 1), al[..., None]], -1)


# ---------------------------------------------------------------- Modern pipe system: two paint treatments

def blue_paint_mask(rgb):
    h, s, v = hsv(rgb)
    hue = h * 360
    return ramp(s, 0.10, 0.22) * ramp(hue, 175, 190) * (1 - ramp(hue, 235, 250))


def repaint_blue(rgb, al, F, variant, G):
    """F(name) -> paint field in [0,1] of al.shape (periodic for the atlas). variant 'touchup' or 'fieldworn'."""
    m = blue_paint_mask(rgb) * ramp(al, 0.3, 0.8)
    L = luma(rgb)
    out = rgb.copy()
    out = matte(out, 0.80, 0.55)                                    # the plastic sheen goes first
    # every variant: the clean baby-blue is dulled toward real painted iron (less chroma, a touch darker)
    out = mix(out, np.stack([L, L, L], -1) * 0.92 + 0.02, 0.28 * m)
    if variant == "touchup":
        # A: a maintained municipal main. Patches of touch-up paint that never matched: an older darker blue, a
        #    greener blue from another batch, and grey primer where a section was replaced.
        p = F("patch")
        sel = F("which")
        patch = ramp(p, 0.52, 0.58)                                 # hard-edged brushed patches, about a third
        older = np.stack([L * 0.42, L * 0.60, L * 0.86], -1)
        teal = np.stack([L * 0.50, L * 0.86, L * 0.84], -1)
        primer = np.stack([L * 0.80 + 0.10, L * 0.80 + 0.10, L * 0.76 + 0.09], -1)
        col = np.where((sel < 0.40)[..., None], older, np.where((sel < 0.70)[..., None], teal, primer))
        out = mix(out, col, patch * m * 0.95)
        grime = F("grime")
        out = mix(out, out * np.array([0.78, 0.76, 0.72]), (0.10 + 0.25 * grime) * m)
    else:
        # B: a field-worn main. Sun-faded body, chipped to red-oxide primer and bare grey steel in places, a dust film.
        out = mix(out, np.stack([L, L, L], -1) * 1.02 + 0.04, 0.30 * m)          # sun-faded toward chalky blue-grey
        chip = F("chip")
        bare = ramp(chip, 0.84, 0.88)
        # judge 2026-11-22 (REDO, "candy stripe" in a laid run): fewer, duller, irregular primer scuffs. The primer
        # mask multiplies the along-the-pipe band by a 2D blotch field, so a scuff is a ragged spot, not a ring.
        oxide = ramp(F("patch") * (0.55 + 0.45 * F("chip2")), 0.74, 0.79) * (1 - bare)
        out = mix(out, np.stack([L * 0.80 + 0.06, L * 0.55 + 0.04, L * 0.46 + 0.04], -1), oxide * m * 0.75)
        out = mix(out, np.stack([L * 0.85 + 0.06, L * 0.85 + 0.06, L * 0.84 + 0.06], -1), bare * m * 0.9)
        dust = F("grime")
        out = mix(out, mix(out, np.array([0.58, 0.50, 0.40]), np.full(al.shape, 0.6)), (0.10 + 0.25 * dust) * m)
    out = out + G[..., None] * m[..., None]
    return np.clip(out, 0, 1)


def pipe_atlas(variant):
    a = load(TEX / "Pipe/Modern/UniversalPipe_Atlas.png")
    rgb, al = a[..., :3], a[..., 3]
    T = a.shape[1] // 4; P = T // 8; C = T - 2 * P
    # paint runs ALONG a pipe: each field is stretched along x for the east-west arm and along y for the north-south arm,
    # blended by which arm a cell pixel is nearer (both blends are functions of cell coordinates, so still periodic)
    # paint runs ALONG a pipe: on the east-west arm a field varies with x only, on the north-south arm with y only, so a
    # patch is a band of paint round a section (how touch-ups are really applied), never a slash across the girth. A
    # little fine 2D noise roughens the band edges. Arms are blended by which one a cell pixel is nearer; every term is a
    # function of cell coordinates, so the atlas seams stay exact.
    sig = {"patch": 7.0, "which": 16.0, "grime": 10.0, "chip": 2.5}
    off = 0 if variant == "touchup" else 50
    k = np.arange(C, dtype=np.float32) - (C - 1) / 2
    ax, ay = np.abs(k)[None, :] * np.ones((C, 1)), np.abs(k)[:, None] * np.ones((1, C))
    wx = (ax + 1e-3) / (ax + ay + 2e-3)                               # 1 on the east-west arm, 0 on the north-south arm
    cell = {}
    for i, (name, sg) in enumerate(sig.items()):
        fx = field((1, C), sg, 301 + i + off)                         # varies along x
        fy = field((1, C), sg, 401 + i + off).reshape(C, 1)           # varies along y
        rough = field((C, C), 1.2, 501 + i + off)
        cell[name] = norm(wx * fx + (1 - wx) * fy + 0.12 * (rough - 0.5))
    cell["chip"] = field((C, C), 1.3, 599 + off)                        # chips are small flecks, not bands
    cell["chip2"] = field((C, C), 4.0, 598 + off)                       # ragged blotches that break a band into spots
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    cy = ((yy % T) - P) % C; cx = ((xx % T) - P) % C

    def F(name):
        return cell[name][cy, cx]
    # grain must also respect the seams: sample a periodic grain cell the same way
    g = np.random.default_rng(399).random((C, C)).astype(np.float32)
    out = repaint_blue(rgb, al, F, variant, (g[cy, cx] - 0.5) * 0.06)
    return np.concatenate([np.clip(out, 0, 1), al[..., None]], -1)


def sprinkler(variant):
    a = load(TEX / "Sprinkler/Modern/RM_SprinklerHead.png")
    rgb, al = a[..., :3], a[..., 3]
    sig = {"patch": 3.5, "which": 7, "grime": 5, "chip": 1.4, "chip2": 1.0}
    seeds = {"patch": 311, "which": 312, "grime": 313, "chip": 314, "chip2": 316}
    fl = {k: field(al.shape, sig[k], seeds[k] + (0 if variant == "touchup" else 50)) for k in sig}
    out = repaint_blue(rgb, al, lambda n: fl[n], variant, grain(al.shape, 315, 0.03))
    return np.concatenate([out, al[..., None]], -1)


OPTIONS = {
    "tank_industrial_A_rust_cleaned": industrial_derust,
    "tank_industrial_B_sand_grey_paint": industrial_sand,
    "tank_modern_A_weathered_leg_tank": modern_tank_weathered,
    "pipe_modern_A_touchup_patches": lambda: pipe_atlas("touchup"),
    "pipe_modern_B_field_worn": lambda: pipe_atlas("fieldworn"),
    "sprinkler_modern_A_touchup_patches": lambda: sprinkler("touchup"),
    "sprinkler_modern_B_field_worn": lambda: sprinkler("fieldworn"),
}


def main(argv):
    out = Path(argv[1]); out.mkdir(parents=True, exist_ok=True)
    for name, fn in OPTIONS.items():
        save(fn(), out / f"{name}.png")
        print("wrote", out / f"{name}.png")


if __name__ == "__main__":
    main(sys.argv)
