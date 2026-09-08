#!/usr/bin/env python3
"""Procedural war-debris ring strip for RW Planet Atmosphere (TransparentObject_Ring).
Shader samples tex2Dlod(ringMap, (u, 0.5)) -> horizontal axis = radial (left inner, right outer).
Outputs a 2048x128 RGBA strip + a polar-warp preview."""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 2048, 128
rng = np.random.default_rng(20260908)
u = np.linspace(0, 1, W, endpoint=False)


def value_noise(n, freq, seed):
    r = np.random.default_rng(seed)
    k = int(freq) + 2
    pts = r.random(k)
    x = np.linspace(0, freq, n, endpoint=False)
    i = np.floor(x).astype(int)
    f = x - i
    f = f * f * (3 - 2 * f)
    return pts[i] * (1 - f) + pts[i + 1] * f


def fbm(n, base, seed, octaves=5):
    out = np.zeros(n); amp = 1; tot = 0
    for o in range(octaves):
        out += amp * value_noise(n, base * 2 ** o, seed + o * 101)
        tot += amp; amp *= 0.5
    return out / tot

# --- explicit chunky bands ------------------------------------------------
rust = np.array([0.55, 0.28, 0.12]); drust = np.array([0.36, 0.17, 0.09])
ash = np.array([0.46, 0.44, 0.41]); char = np.array([0.17, 0.15, 0.14])
steel = np.array([0.62, 0.60, 0.56]); scorch = np.array([0.30, 0.20, 0.13])
pal = [rust, ash, char, steel, scorch, drust, rust, ash]
alpha = np.zeros(W); rgb = np.zeros((W, 3))
# background haze: thin, patchy, mostly ash/charcoal, with hard-zero lanes
haze = fbm(W, 7, 41, 3)
haze_a = np.clip((haze - 0.35) * 0.9, 0, 0.28) * (fbm(W, 30, 42, 2) > 0.3)
alpha[:] = haze_a
rgb[:] = char * 0.5 + ash * 0.5
# bands: (centre, width, peak alpha, palette idx)
bands = []
x = 0.03
br = np.random.default_rng(77)
while x < 0.96:
    w = br.uniform(0.012, 0.075)
    if x + w > 0.97: break
    bands.append((x + w / 2, w, br.uniform(0.55, 1.0), br.integers(0, len(pal))))
    x += w + br.uniform(0.008, 0.06)          # gap after the band (hard, sometimes wide)
for c, w, pk, pi in bands:
    inb = (u > c - w / 2) & (u < c + w / 2)
    inner = fbm(W, 140, int(c * 10000), 3)             # in-band chunkiness
    a = pk * (0.55 + 0.45 * inner)
    a *= (inner > 0.22)                                # holes inside the band
    col = pal[pi] * (0.7 + 0.6 * inner)[:, None]
    col = col * (1 - 0.3 * fbm(W, 30, int(c * 7777), 2))[:, None] + steel * (0.3 * fbm(W, 30, int(c * 7777), 2))[:, None]
    alpha[inb] = np.maximum(alpha[inb], a[inb])
    rgb[inb] = col[inb]
# deliberate wide hard gaps (cleared lanes), overriding everything
for c, w in [(0.22, 0.03), (0.47, 0.045), (0.71, 0.02), (0.86, 0.035)]:
    alpha[(u > c - w / 2) & (u < c + w / 2)] = 0
# ragged inner/outer edges, hard cut
alpha *= (u > 0.012 + 0.02 * value_noise(W, 40, 11)) & (u < 0.985 - 0.02 * value_noise(W, 40, 12))
alpha = np.clip(alpha, 0, 1)
shell = alpha
# --- glints: sparse bright fragments (thin bright arcs in the ring) -------
glint_cols = rng.choice(np.where(alpha > 0.3)[0], size=30, replace=False)
for c in glint_cols:
    wid = rng.integers(1, 3)
    tone = np.array([0.95, 0.90, 0.80]) if rng.random() < 0.7 else np.array([0.85, 0.95, 1.0])
    rgb[c:c + wid] = tone
    alpha[c:c + wid] = np.maximum(alpha[c:c + wid], 0.85)

strip = np.zeros((H, W, 4), dtype=np.float32)
strip[..., :3] = np.clip(rgb, 0, 1)[None]
strip[..., 3] = alpha[None]
out = Image.fromarray((strip * 255 + 0.5).astype(np.uint8), "RGBA")
out.save("/mnt/d/Luke/dev/Rimworld/Transient/ring_debris_candidate.png")

# --- preview: polar warp, top-down + oblique with planet ------------------
INNER, OUTER, PLANET = 140.0, 200.0, 100.0   # ring units (planet radius 100)
row = strip[0]


def ring_layer(size, scale_px, tilt=1.0):
    cx = cy = size / 2
    yy, xx = np.mgrid[0:size, 0:size]
    dx = (xx - cx) / scale_px
    dy = (yy - cy) / scale_px / tilt
    r = np.sqrt(dx * dx + dy * dy)
    uu = (r - INNER) / (OUTER - INNER)
    inside = (uu >= 0) & (uu < 1)
    idx = np.clip((uu * W).astype(int), 0, W - 1)
    img = row[idx].copy()
    img[~inside] = 0
    # cheap "sun from upper-left" shading on the far/near halves
    return img


def planet_layer(size, scale_px):
    cx = cy = size / 2
    yy, xx = np.mgrid[0:size, 0:size]
    dx = (xx - cx) / scale_px; dy = (yy - cy) / scale_px
    r = np.sqrt(dx * dx + dy * dy)
    inside = r <= PLANET
    nz = np.sqrt(np.clip(1 - (r / PLANET) ** 2, 0, 1))
    light = np.clip(0.25 + 0.75 * (-dx / PLANET * 0.5 - dy / PLANET * 0.4 + nz * 0.8), 0, 1)
    base = np.array([0.80, 0.66, 0.42])
    img = np.zeros((size, size, 4), np.float32)
    img[..., :3] = base * light[..., None]
    img[..., 3] = inside
    img[~inside] = 0
    return img


def over(dst, src):
    a = src[..., 3:4]
    dst[..., :3] = src[..., :3] * a + dst[..., :3] * (1 - a)
    dst[..., 3] = np.maximum(dst[..., 3], src[..., 3])
    return dst


def starfield(size, seed):
    r = np.random.default_rng(seed)
    bg = np.zeros((size, size, 4), np.float32); bg[..., 3] = 1
    bg[..., :3] = np.array([0.02, 0.02, 0.04])
    n = size * size // 900
    ys = r.integers(0, size, n); xs = r.integers(0, size, n)
    bg[ys, xs, :3] = r.random((n, 1)) * 0.6 + 0.3
    return bg


S = 900
scale_px = (S / 2 - 10) / OUTER
# top-down
top = starfield(S, 1)
over(top, ring_layer(S, scale_px))
over(top, planet_layer(S, scale_px))
# oblique: ring plane tilted; far half behind planet, near half in front
tilt = 0.38
ob = starfield(S, 2)
ring = ring_layer(S, scale_px, tilt)
far = ring.copy(); far[S // 2:] = 0
near = ring.copy(); near[:S // 2] = 0
over(ob, far)
over(ob, planet_layer(S, scale_px))
over(ob, near)

top_im = Image.fromarray((np.clip(top, 0, 1) * 255).astype(np.uint8), "RGBA")
ob_im = Image.fromarray((np.clip(ob, 0, 1) * 255).astype(np.uint8), "RGBA")
strip_prev = out.resize((S * 2 + 20, 100), Image.NEAREST)
canvas = Image.new("RGBA", (S * 2 + 20, S + 140), (10, 10, 14, 255))
canvas.paste(top_im, (0, 0)); canvas.paste(ob_im, (S + 20, 0))
# show strip over checker so alpha gaps read
chk = Image.new("RGBA", strip_prev.size, (60, 60, 60, 255))
d = ImageDraw.Draw(chk)
for x in range(0, chk.width, 16):
    d.rectangle([x, 0, x + 7, chk.height], fill=(90, 90, 90, 255))
chk.alpha_composite(strip_prev)
canvas.paste(chk, (0, S + 20))
d = ImageDraw.Draw(canvas)
d.text((8, S + 4), "strip (left=inner edge 140, right=outer edge 200; shader reads one row)", fill=(220, 220, 220))
d.text((8, 4), "top-down: planet R=100, ring 140-200", fill=(220, 220, 220))
d.text((S + 28, 4), "oblique (world camera view)", fill=(220, 220, 220))
canvas.save("/mnt/d/Luke/dev/Rimworld/Transient/ring_debris_preview.png")
print("alpha mean %.2f, gap fraction %.2f" % (alpha.mean(), (alpha < 0.02).mean()))
