"""Cracked dry-lakebed terrain textures, one per depth band (LAKEBED_ART_BUILD_CRACKS_WITH_CHARACTER).

Procedural, seamless by construction: every noise field is made in the frequency domain (periodic)
and the crack network is a Worley diagram on a wrapped grid, so the tile repeats with no seam.
No pixels are copied from any game or donor texture; only the target brightness/saturation are
taken from vanilla terrain measurements (Mud lum 0.232, PackedDirt 0.349, Sand 0.428, Gravel std 0.040).

    python3 src/RimMandrake/Utils/art/lakebed_textures.py <out_dir>      writes RM_Lakebed_Shallow.png, RM_Lakebed_Deep.png
"""
import sys, colorsys
from pathlib import Path
import numpy as np
from PIL import Image

S = 1024

def tnoise(scale, seed):
    """Periodic gaussian-filtered noise, ~`scale` px features, normalised to std 1."""
    r = np.random.default_rng(seed)
    f = np.fft.fft2(r.standard_normal((S, S)))
    k = np.fft.fftfreq(S)
    kk = np.sqrt(k[:, None] ** 2 + k[None, :] ** 2)
    n = np.real(np.fft.ifft2(f * np.exp(-(kk * scale) ** 2)))
    return ((n - n.mean()) / n.std()).astype(np.float32)

def fbm(scales, seed):
    return sum(tnoise(s, seed + i) * (s / scales[0]) ** .5 for i, s in enumerate(scales))

def worley(G, seed, wx, wy):
    """Wrapped jittered-grid Voronoi. Returns (cell id, distance to the nearest cell edge in px, id across that edge)."""
    r = np.random.default_rng(seed)
    c = S / G
    jit = r.uniform(.12, .88, (G, G, 2)).astype(np.float32)
    gx, gy = np.floor(wx / c).astype(int), np.floor(wy / c).astype(int)
    cand = []
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            ix, iy = gx + dx, gy + dy
            jx, jy = ix % G, iy % G
            sx = (ix + jit[jy, jx, 0]) * c
            sy = (iy + jit[jy, jx, 1]) * c
            cand.append((sx, sy, jy * G + jx))
    sx = np.stack([a[0] for a in cand]); sy = np.stack([a[1] for a in cand]); ids = np.stack([a[2] for a in cand])
    d2 = (sx - wx) ** 2 + (sy - wy) ** 2
    a = np.argmin(d2, 0)
    take = lambda arr: np.take_along_axis(arr, a[None], 0)[0]
    ax, ay, aid, ad2 = take(sx), take(sy), take(ids), take(d2)
    sep = np.sqrt((sx - ax) ** 2 + (sy - ay) ** 2)
    edge = np.where(sep > 1e-3, (d2 - ad2) / (2 * np.maximum(sep, 1e-3)), np.inf)
    b = np.argmin(edge, 0)
    return aid, np.take_along_axis(edge, b[None], 0)[0], np.take_along_axis(ids, b[None], 0)[0]

def pairhash(a, b, salt):
    lo, hi = np.minimum(a, b).astype(np.int64), np.maximum(a, b).astype(np.int64)
    h = (lo * 73856093) ^ (hi * 19349663) ^ (salt * 83492791)
    return ((h % 10007) / 10007.0).astype(np.float32)

def cellhash(a, salt):
    return (((a.astype(np.int64) * 2654435761 + salt * 97) % 10007) / 10007.0).astype(np.float32)

def roll_grad(h):
    gx = (np.roll(h, -1, 1) - np.roll(h, 1, 1)) * .5
    gy = (np.roll(h, -1, 0) - np.roll(h, 1, 0)) * .5
    return gx, gy

def lum(rgb):
    return float(rgb.mean())

def make(p):
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    # domain warp: smooth natural curves plus a little edge roughness, still periodic
    wx = (xx + p["warp"] * tnoise(110, p["seed"]) + 0.9 * tnoise(5, p["seed"] + 1)) % S
    wy = (yy + p["warp"] * tnoise(110, p["seed"] + 10) + 0.9 * tnoise(5, p["seed"] + 11)) % S
    cid, d1, nid = worley(p["G1"], p["seed"] + 20, wx, wy)
    # primary crack width varies per edge, a little along it
    w1 = p["w1"] * (.5 + 1.0 * pairhash(cid, nid, 1) ** 1.5) * (.85 + .15 * tnoise(30, p["seed"] + 30))
    # secondary, finer net: whole edges only, so a plate is split in two rather than scribbled on
    cid2, d2, nid2 = worley(p["G2"], p["seed"] + 50, wx, wy)
    keep2 = (pairhash(cid2, nid2, 2) > p["sub_keep"]).astype(np.float32)
    w2 = p["w2"] * keep2
    c1 = np.clip((w1 / 2 - d1) / 1.0 + .5, 0, 1)
    c2 = np.clip((w2 / 2 - d2) / .9 + .5, 0, 1) * keep2
    crack = np.maximum(c1, c2 * .85)
    # height: plates lift at their rims (curl), crack floors sit low, fine grain everywhere
    e1 = np.maximum(d1 - w1 / 2, 0); e2 = np.where(keep2 > 0, np.maximum(d2 - w2 / 2, 0), 99)
    curl = p["curl"] * (np.exp(-e1 / p["curl_len"]) + .5 * np.exp(-e2 / 3))
    grain = p["grain"] * fbm([2.5, 1.2], p["seed"] + 70)
    h = curl + grain - crack * p["crack_depth"] + p["swell"] * tnoise(120, p["seed"] + 80)
    gx, gy = roll_grad(h)
    shade = 1 + p["relief"] * (-(gx * .7 + gy * .7))
    lip = np.exp(-e1 / p["lip_len"]) * (1 - crack)
    # albedo: base colour, per-plate tone, mottling, crack floor
    base = np.array(p["base"], np.float32)
    plate_tone = 1 + p["plate_var"] * (cellhash(cid, 5) - .5) + p["mottle"] * fbm([160, 50], p["seed"] + 90) * .5
    alb = base[None, None] * plate_tone[..., None] * (1 + p["lip"] * lip)[..., None]
    if p.get("salt"):
        # a pale silt film that gathers on the curled rims (shallow bed dried first, from the edge)
        film = np.clip(curl / p["curl"], 0, 1) * np.clip(tnoise(60, p["seed"] + 95) * .4 + .6, 0, 1)
        alb = alb * (1 - p["salt"] * film[..., None]) + np.array(p["salt_col"], np.float32) * (p["salt"] * film[..., None])
    floor = np.array(p["floor"], np.float32)
    alb = alb * (1 - crack[..., None]) + floor * crack[..., None]
    rgb = alb * shade[..., None]
    # match the vanilla level: mean luminance and saturation
    for _ in range(3):
        rgb *= p["lum"] / lum(rgb)
        m = rgb.reshape(-1, 3).mean(0)
        s_now = colorsys.rgb_to_hsv(*m)[1]
        grey = rgb.mean(2, keepdims=True)
        rgb = grey + (rgb - grey) * (p["sat"] / max(s_now, 1e-3))
    return np.clip(rgb, 0, 1)

COMMON = dict(warp=11, sub_keep=.55, curl_len=5, swell=.15, lip=.10, lip_len=4)
SHALLOW = dict(COMMON, seed=101, G1=13, G2=29, sub_keep=.72, w1=4.6, w2=1.6, curl=.9, crack_depth=2.2, grain=.18, relief=.22,
               plate_var=.07, mottle=.05, base=(.62, .53, .43), floor=(.30, .23, .18), salt=.28, salt_col=(.80, .74, .64),
               lum=.375, sat=.27)
DEEP = dict(COMMON, seed=202, G1=7, G2=17, w1=9.0, w2=2.4, curl=1.3, curl_len=9, crack_depth=3.0, grain=.22, relief=.2,
            plate_var=.10, mottle=.07, base=(.40, .31, .245), floor=(.14, .10, .08), salt=0, sub_keep=.6,
            lum=.235, sat=.34)

if __name__ == "__main__":
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    for name, p in (("RM_Lakebed_Shallow", SHALLOW), ("RM_Lakebed_Deep", DEEP)):
        a = make(p)
        Image.fromarray((a * 255 + .5).astype(np.uint8), "RGB").save(out / f"{name}.png", optimize=True)
        m = a.reshape(-1, 3).mean(0)
        print(name, "lum", round(lum(a), 3), "sat", round(colorsys.rgb_to_hsv(*m)[1], 3), "std", round(float(a.mean(2).std()), 3))
