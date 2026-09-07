#!/usr/bin/env python3
"""Ash'karr planetary portrait — two hemispheres (dayside / nightside faces) on a
starfield plate. Naturalistic palette, sun lighting with soft terminator, night
emissives. No iconography. Reads world/ASHKARR_WORLDMAP_tiles.csv."""
import csv, math, sys, random
import numpy as np
from PIL import Image, ImageFilter

CSV = "/mnt/d/Luke/dev/Rimworld/world/ASHKARR_WORLDMAP_tiles.csv"
OUT = sys.argv[1] if len(sys.argv) > 1 else "/mnt/d/Luke/dev/Rimworld/Transient/ashkarr_portrait.png"

# --- naturalistic from-space palette (keyed to ratified artistic themes) ---
PAL = {
    "Ocean": (22, 50, 79), "Lake": (43, 95, 138), "SeaIce": (184, 204, 216),
    "IceSheet": (168, 191, 208), "RUT_NightsideIce": (160, 184, 203),
    "ExtremeDesert": (232, 217, 174), "Desert": (212, 182, 120),
    "AridShrubland": (184, 159, 94), "ZBiome_Badlands": (168, 106, 66),
    "Wasteland": (154, 148, 138), "ZBiome_Grasslands": (163, 168, 98),
    "Savanna": (176, 164, 87), "AB_GallatrossGraveyard": (203, 185, 140),
    "ZBiome_DesertOasis": (126, 168, 109), "BiomeCypreJungle": (62, 122, 58),
    "AB_FeraliskInfestedJungle": (47, 107, 53), "AB_MiasmicMangrove": (74, 122, 104),
    "COMIGO_GreaterSwamp_Tropical": (85, 128, 94),
    "AB_PyroclasticConflagration": (107, 68, 54), "LavaField": (87, 52, 44),
    "Volcano": (74, 44, 34), "Scarlands": (138, 90, 78),
    "PoisonForest": (109, 122, 68), "AB_GelatinousSuperorganism": (156, 134, 168),
    "AB_MycoticJungle": (110, 96, 134), "BMT_FungalForest": (87, 80, 112),
    "AB_OcularForest": (122, 74, 82), "HorrorWastes": (92, 74, 82),
    "AB_RockyCrags": (86, 88, 106), "AB_TarPits": (38, 34, 42),
    "AB_PropaneLakes": (29, 44, 51), "BMT_CrystalCaverns": (123, 150, 173),
    "Glowforest": (46, 107, 99), "AB_MechanoidIntrusion": (146, 108, 88),
    "BiomeGRimond": (74, 95, 122), "IronScruff_PrimordialGeysers": (106, 143, 153),
    "BMT_EarthenDepths": (74, 58, 42),
}
DEFAULT = (136, 128, 112)
# night emissives: biome -> (r,g,b,strength)
EMIT = {
    "LavaField": (255, 96, 20, 0.85), "Volcano": (255, 80, 16, 0.8),
    "AB_PyroclasticConflagration": (255, 120, 30, 0.65),
    "Glowforest": (40, 230, 190, 0.5), "BMT_CrystalCaverns": (140, 200, 255, 0.3),
    "AB_PropaneLakes": (40, 160, 110, 0.22), "AB_GelatinousSuperorganism": (240, 120, 200, 0.24),
    "AB_OcularForest": (230, 60, 60, 0.22), "IronScruff_PrimordialGeysers": (90, 210, 230, 0.28),
}

# --- load tiles ---
lats, lons, arcs, elevs, bids, waters = [], [], [], [], [], []
names = []
name_ix = {}
unknown = set()
with open(CSV) as f:
    for row in csv.DictReader(f):
        b = row["biome"]
        if b not in name_ix:
            name_ix[b] = len(names); names.append(b)
            if b not in PAL: unknown.add(b)
        lats.append(float(row["lat"])); lons.append(float(row["lon"]))
        arcs.append(float(row["arc"])); elevs.append(float(row["elev_m"]))
        bids.append(name_ix[b]); waters.append(1.0 if row["water"] not in ("", "0", "False", "false") else 0.0)
if unknown: print("PALETTE FALLBACK for:", sorted(unknown))
lat = np.radians(np.array(lats)); lon = np.radians(np.array(lons))
arc = np.array(arcs); elev = np.array(elevs); bid = np.array(bids); wat = np.array(waters)
N = len(lat); print(f"{N} tiles, {len(names)} biomes")

pal = np.array([PAL.get(n, DEFAULT) for n in names], dtype=np.float32) / 255.0
emit = np.zeros((len(names), 4), dtype=np.float32)
for i, n in enumerate(names):
    if n in EMIT:
        r, g, b, s = EMIT[n]; emit[i] = (r / 255.0, g / 255.0, b / 255.0, s)
water_col = np.array([n in ("Ocean", "Lake") for n in names]) | False

# tile unit vectors
tx = np.cos(lat) * np.cos(lon); ty = np.cos(lat) * np.sin(lon); tz = np.sin(lat)
tvec = np.stack([tx, ty, tz], 1).astype(np.float32)

# substellar / antistellar from arc column
sub_i = int(np.argmin(arc)); anti_i = int(np.argmax(arc))
sub = tvec[sub_i] / np.linalg.norm(tvec[sub_i])
print(f"substellar tile arc={arc[sub_i]:.1f} lat={lats[sub_i]:.1f} lon={lons[sub_i]:.1f}; "
      f"antistellar arc={arc[anti_i]:.1f}")

# --- equirect nearest-tile raster via bucket grid ---
W, H = 2880, 1440
BL_lon, BL_lat = 288, 144  # 1.25 deg buckets
buckets = [[] for _ in range(BL_lon * BL_lat)]
blon = ((np.degrees(lon) + 180.0) / 360.0 * BL_lon).astype(int) % BL_lon
blat = np.clip(((90.0 - np.degrees(lat)) / 180.0 * BL_lat).astype(int), 0, BL_lat - 1)
for i in range(N):
    buckets[blat[i] * BL_lon + blon[i]].append(i)

px_lon = (np.arange(W) + 0.8) / W * 2 * np.pi - np.pi
px_lat = np.pi / 2 - (np.arange(H) + 0.8) / H * np.pi
plon_g, plat_g = np.meshgrid(px_lon, px_lat)
pvx = np.cos(plat_g) * np.cos(plon_g); pvy = np.cos(plat_g) * np.sin(plon_g); pvz = np.sin(plat_g)

nearest = np.zeros((H, W), dtype=np.int32)
pb_lon = ((np.degrees(plon_g) + 180.0) / 360.0 * BL_lon).astype(int) % BL_lon
pb_lat = np.clip(((90.0 - np.degrees(plat_g)) / 180.0 * BL_lat).astype(int), 0, BL_lat - 1)
cache = {}
def candidates(bx, by, ring=1):
    key = (bx, by, ring)
    c = cache.get(key)
    if c is None:
        ids = []
        for dy in range(-ring, ring + 1):
            yy = by + dy
            if yy < 0 or yy >= BL_lat: continue
            for dx in range(-ring, ring + 1):
                ids.extend(buckets[yy * BL_lon + (bx + dx) % BL_lon])
        c = np.array(ids, dtype=np.int32) if ids else None
        cache[key] = c
    return c

for by in range(BL_lat):
    ys = np.where(pb_lat[:, 0] == by)[0]
    if len(ys) == 0: continue
    for bx in range(BL_lon):
        ring = 1; cand = candidates(bx, by, ring)
        while cand is None or len(cand) == 0:
            ring += 1; cand = candidates(bx, by, ring)
        xs = np.where(pb_lon[0] == bx)[0]
        vv = np.stack([pvx[np.ix_(ys, xs)].ravel(), pvy[np.ix_(ys, xs)].ravel(),
                       pvz[np.ix_(ys, xs)].ravel()], 1)   # (P,3)
        d = vv @ tvec[cand].T                             # (P,C) cos distance
        pick = cand[np.argmax(d, 1)]
        nearest[np.ix_(ys, xs)] = pick.reshape(len(ys), len(xs))

r_bid = bid[nearest]; r_elev = elev[nearest]; r_arc = arc[nearest]
base = pal[r_bid]                                        # H,W,3

# subtle elevation modulation + hillshade
ee = np.clip(r_elev, -200, 3200)
base *= (0.92 + 0.10 * (ee / 3200.0))[..., None]
gy, gx = np.gradient(ee)
shade = np.clip(1.0 + (gx * math.cos(2.4) + gy * math.sin(2.4)) / 900.0, 0.72, 1.22)
base = np.clip(base * shade[..., None], 0, 1)

# --- orthographic disc renderer ---
def render_disc(center_vec, radius_px, sunlit):
    Rz = radius_px
    size = int(radius_px * 2.3)
    cx = cy = size / 2
    yy, xx = np.mgrid[0:size, 0:size]
    ux = (xx - cx) / Rz; uy = (cy - yy) / Rz
    rr2 = ux * ux + uy * uy
    inside = rr2 <= 1.0
    uz = np.sqrt(np.clip(1.0 - rr2, 0, 1))
    # basis: center_vec = forward; up = +z projected
    f = center_vec / np.linalg.norm(center_vec)
    upw = np.array([0, 0, 1.0])
    right = np.cross(upw, f)
    if np.linalg.norm(right) < 1e-6: right = np.array([1.0, 0, 0])
    right /= np.linalg.norm(right); upv = np.cross(f, right)
    P = (ux[..., None] * right + uy[..., None] * upv + uz[..., None] * f)
    plat = np.arcsin(np.clip(P[..., 2], -1, 1)); plon = np.arctan2(P[..., 1], P[..., 0])
    sx = np.clip(((plon + np.pi) / (2 * np.pi) * W).astype(int), 0, W - 1)
    sy = np.clip(((np.pi / 2 - plat) / np.pi * H).astype(int), 0, H - 1)
    col = base[sy, sx].copy()
    b_here = r_bid[sy, sx]; a_here = r_arc[sy, sx]
    # sun lighting from arc (angular distance to substellar): soft terminator 82..102 deg
    cosl = np.cos(np.radians(a_here))
    t = np.clip((102.0 - a_here) / 20.0, 0, 1); t = t * t * (3 - 2 * t)
    daylight = np.clip(cosl, 0, 1) * 0.9 + 0.1
    lightmap = t * daylight
    nightbase = np.array([0.10, 0.125, 0.19])  # starlit blue ambient
    lit = col * lightmap[..., None] + col * nightbase * (1 - t)[..., None]
    # night emissives
    em = emit[b_here]
    glow = em[..., :3] * (em[..., 3:] * (1 - t)[..., None])
    lit = lit + glow
    # reconnection aurora over the deep-night cap (arc > 150): waving green-violet ribbons
    deep = np.clip((a_here - 148.0) / 32.0, 0, 1)
    if deep.max() > 0:
        wave = (np.sin(ux * 9.5 + uy * 3.0) * 0.5 + 0.5) * (np.sin(uy * 13.0 - ux * 2.0) * 0.5 + 0.5)
        band = deep * (0.35 + 0.65 * wave) * (1 - t)
        lit += band[..., None] * np.array([0.05, 0.30, 0.16]) * 0.55
        lit += (band ** 2)[..., None] * np.array([0.16, 0.08, 0.28]) * 0.3
    # warm tint near substellar (the furnace)
    warm = np.clip((30.0 - a_here) / 30.0, 0, 1)[..., None]
    lit = lit * (1 + warm * np.array([0.10, 0.03, -0.06]))
    # specular glint on water, dayside
    isw = water_col[b_here] & (a_here < 75)
    spec = np.clip((75.0 - a_here) / 75.0, 0, 1) ** 3 * 0.35
    lit[isw] += (spec[..., None] * np.array([1.0, 0.95, 0.8]))[isw]
    # limb darkening
    limb = 0.45 + 0.55 * uz ** 0.7
    lit *= limb[..., None]
    lit = np.clip(lit, 0, 1)
    rgba = np.zeros((size, size, 4), dtype=np.float32)
    rgba[..., :3] = lit; rgba[..., 3] = inside.astype(np.float32)
    # anti-aliased edge
    edge = np.clip((1.0 - np.sqrt(rr2)) * Rz, 0, 1)
    rgba[..., 3] = np.minimum(rgba[..., 3], edge)
    return rgba, size

def atmosphere(size, radius_px, color, strength):
    yy, xx = np.mgrid[0:size, 0:size]
    c = size / 2
    r = np.sqrt((xx - c) ** 2 + (yy - c) ** 2) / radius_px
    halo = np.exp(-np.clip(r - 1.0, 0, None) * 9.0) * (r > 0.985)
    inner = np.exp(-np.clip(1.0 - r, 0, None) * 14.0) * (r <= 0.985)
    a = np.clip((halo + inner * 0.7) * strength, 0, 1)
    out = np.zeros((size, size, 4), dtype=np.float32)
    out[..., :3] = np.array(color); out[..., 3] = a
    return out

# --- compose plate ---
PLATE_W, PLATE_H = 3600, 2000
R = 730
plate = np.zeros((PLATE_H, PLATE_W, 3), dtype=np.float32)
plate[...] = np.array([0.015, 0.014, 0.022])
rng = random.Random(63)
for _ in range(1400):
    x = rng.randrange(PLATE_W); y = rng.randrange(PLATE_H)
    m = rng.random() ** 3.5 * 0.75 + 0.05
    tint = np.array([0.9 + rng.random() * 0.1, 0.9 + rng.random() * 0.1, 1.0])
    plate[y, x] = np.clip(plate[y, x] + m * tint, 0, 1)
    if m > 0.6 and x + 1 < PLATE_W and y + 1 < PLATE_H:
        plate[y, x + 1] += m * 0.25; plate[y + 1, x] += m * 0.25

def paste(rgba, cx, cy):
    s = rgba.shape[0]
    x0 = cx - s // 2; y0 = cy - s // 2
    reg = plate[y0:y0 + s, x0:x0 + s]
    a = rgba[..., 3:]
    reg[...] = reg * (1 - a) + rgba[..., :3] * a

day, ds = render_disc(sub, R, True)
night, ns = render_disc(-sub, R, False)
cxd, cxn, cyc = 950, 2650, 1000
paste(atmosphere(ds, R, (0.95, 0.75, 0.45), 0.8), cxd, cyc)
paste(day, cxd, cyc)
paste(atmosphere(ns, R, (0.30, 0.45, 0.75), 0.35), cxn, cyc)
paste(night, cxn, cyc)

img = Image.fromarray((np.clip(plate, 0, 1) * 255).astype(np.uint8))
img = img.filter(ImageFilter.GaussianBlur(0.65))
img.save(OUT)
print("wrote", OUT, img.size)
