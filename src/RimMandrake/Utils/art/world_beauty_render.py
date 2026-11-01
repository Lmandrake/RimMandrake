#!/usr/bin/env python3
"""WORLDMAP_BIOME_APPEARANCE_1 step 4: offline planet beauty set, the installed biome faces on the Ash'karr globe.

Reads the tile RECORD (world/ASHKARR_WORLDMAP_tiles.csv: the planet on its export date, not the live world) and the face
pngs in src/. Each pixel takes its three nearest tiles (soft borders, like worldBorderBlend), samples each tile's face
triplanar at about 3.2 hexes per face repeat, darkens with hilliness, and is lit from the fixed substellar point (0,0).
The night side view is flat-lit, or the Chill could not be judged at all. No ring, stars, rivers or icons: these seed colour work, they are not screenshots and do not prove what the game draws.
usage: python3 world_beauty_render.py <outdir> [--size 1400]   -> <outdir>/<view>.png, sheet.png, coverage.json
"""
import argparse, csv, json, os, sys
import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import biome_worldfaces as B

REPO = B.REPO
HEXES_PER_REPEAT = 3.2
RENAMED = {"RUT_Wasteland": "Wasteland", "RUT_NightsideIce": "SleepingIce", "RUT_ForsakenCrags": "Abyss", "RUT_PoisonForest": "Cauldron", "ZBiome_Grasslands": "Pyrelands"}


class Nearest:
    """k nearest tiles to many points: tiles binned into a 3D grid, each occupied cell searched against its 27 neighbours."""

    def __init__(self, xyz, cell=0.06):
        self.xyz, self.cell, self.bins = xyz, cell, {}
        for t, c in enumerate(map(tuple, np.floor(xyz / cell).astype(int))): self.bins.setdefault(c, []).append(t)

    def query(self, pts, k=3):
        cells = np.floor(pts / self.cell).astype(int)
        uniq, inv = np.unique(cells, axis=0, return_inverse=True); inv = inv.ravel()
        order = np.argsort(inv, kind="stable"); ends = np.cumsum(np.bincount(inv)); start = 0
        d = np.zeros((len(pts), k), np.float32); idx = np.zeros((len(pts), k), int)
        for c, end in zip(map(tuple, uniq), ends):
            members = order[start:end]; start = end
            cand = np.array([t for dx in (-1, 0, 1) for dy in (-1, 0, 1) for dz in (-1, 0, 1)
                             for t in self.bins.get((c[0] + dx, c[1] + dy, c[2] + dz), ())])
            dist = np.linalg.norm(pts[members, None, :] - self.xyz[cand][None, :, :], axis=2)
            near = np.argsort(dist, axis=1)[:, :k]
            idx[members] = cand[near]; d[members] = np.take_along_axis(dist, near, axis=1)
        return d, idx


def to_xyz(lat, lon):
    la, lo = np.radians(lat), np.radians(lon)
    return np.stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)], -1)


def load_tiles():
    """-> xyz, face index per tile, hilliness, water flag, face keys, and {biome name: face key or None}."""
    with open(os.path.join(REPO, "world/ASHKARR_WORLDMAP_tiles.csv"), newline="") as f: rows = list(csv.DictReader(f))
    keys = sorted(B.F); index = {k: i for i, k in enumerate(keys)}; biome_map = {}
    for n in {r["biome"] for r in rows}:
        k = RENAMED.get(n) or B.RECORD.get(n) or next((c for c in (n.split("_", 1)[-1], n.split("_", 1)[-1].replace("The", "", 1)) if c in index), None)
        biome_map[n] = k
    lat = np.array([float(r["lat"]) for r in rows]); lon = np.array([float(r["lon"]) for r in rows])
    face = np.array([index.get(biome_map[r["biome"]], -1) for r in rows])
    hills = np.array([int(float(r["hilliness"])) for r in rows]); return to_xyz(lat, lon), face, hills, keys, biome_map


def load_faces(keys):
    out = []
    for k in keys:
        mod, name = B.F[k][6][0]
        out.append(np.asarray(B.Image.open(os.path.join(REPO, "src", mod, "Textures/World/Biomes", name + ".png")).convert("RGB")).astype(np.float32))
    return np.stack(out)


def render(tree, face, hills, faces, centre, size, repeats, lit=True):
    """orthographic globe, north up, looking down at centre=(lat, lon); lit=False shows the faces in flat light (the night side)."""
    v = np.linspace(-1.02, 1.02, size); x, y = np.meshgrid(v, -v)
    r2 = x ** 2 + y ** 2; disk = r2 <= 1; z = np.sqrt(np.clip(1 - r2, 0, 1))
    f = to_xyz(*centre); up = np.array([0, 0, 1.0]) - f * f[2]
    if np.linalg.norm(up) < 1e-6: up = np.array([-1.0, 0, 0])
    up /= np.linalg.norm(up); right = np.cross(up, f)
    p = x[..., None] * right + y[..., None] * up + z[..., None] * f; pts = p[disk]
    d, i = tree.query(pts, k=3)
    w = 1 / (d + 1e-4) ** 4; w /= w.sum(1, keepdims=True)
    n = faces.shape[1]; col = np.zeros((len(pts), 3), np.float32)
    tri = np.abs(pts) ** 4; tri /= tri.sum(1, keepdims=True)
    for k in range(3):
        fi = face[i[:, k]]; ok = fi >= 0
        for a, b, axis in ((1, 2, 0), (0, 2, 1), (0, 1, 2)):
            u = ((pts[:, a] * repeats) % 1 * n).astype(int) % n; t = ((pts[:, b] * repeats) % 1 * n).astype(int) % n
            s = np.full((len(pts), 3), 60, np.float32); s[ok] = faces[fi[ok], t[ok], u[ok]]
            col += s * (w[:, k] * tri[:, axis])[:, None]
    relief = (hills[i[:, 0]] - 1).clip(0, 4) * w[:, 0] + (hills[i[:, 1]] - 1).clip(0, 4) * w[:, 1] + (hills[i[:, 2]] - 1).clip(0, 4) * w[:, 2]
    sun = to_xyz(0.0, 0.0); lambert = pts @ sun
    light = 0.10 + 1.05 * np.clip(lambert, 0, 1) ** 0.6 + 0.08 * np.clip(lambert + 0.18, 0, 0.18) / 0.18
    if not lit: light = np.full(len(pts), 1.0, np.float32)
    limb = 1 - 0.28 * (1 - z[disk]) ** 2.5
    rgb = col * (1 - 0.055 * relief)[:, None] * (light * limb)[:, None]
    img = np.zeros((size, size, 3), np.float32) + np.array([5, 6, 10], np.float32); img[disk] = rgb
    return np.clip(img, 0, 255).astype(np.uint8)


def views(xyz, face, keys):
    """fixed cameras, plus the crater and the seas taken from where those biomes actually sit."""
    def centroid(*names):
        m = np.isin(face, [keys.index(k) for k in names]); c = xyz[m].mean(0); c /= np.linalg.norm(c)
        return float(np.degrees(np.arcsin(c[2]))), float(np.degrees(np.arctan2(c[1], c[0])))
    return {"dayside": (0, 0), "terminator_east": (5, 75), "terminator_west": (5, -75), "cap_north": (72, 0), "cap_south": (-72, 0),
            "seas": centroid("GreySea", "TwilightSea", "Scald"), "chill_flatlight": centroid("Chill")}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0]); ap.add_argument("out"); ap.add_argument("--size", type=int, default=1400)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    xyz, face, hills, keys, biome_map = load_tiles(); faces = load_faces(keys); tree = Nearest(xyz)
    spacing = float(np.median(tree.query(xyz[::40], k=2)[0][:, 1])); repeats = 1 / (HEXES_PER_REPEAT * spacing)
    missing = sorted(k for k, v in biome_map.items() if v is None or v not in keys)
    cover = {"tiles": len(face), "tiles_without_face": int((face < 0).sum()), "biomes_without_face": missing, "hex_spacing": round(spacing, 5)}
    json.dump(cover, open(os.path.join(a.out, "coverage.json"), "w"), indent=1); print(cover)
    V = views(xyz, face, keys); thumbs = []
    for name, c in V.items():
        im = Image.fromarray(render(tree, face, hills, faces, c, a.size, repeats, lit=name != "chill_flatlight")); im.save(os.path.join(a.out, name + ".png"), optimize=True)
        t = im.resize((480, 480), Image.LANCZOS); ImageDraw.Draw(t).text((6, 4), f"{name} {c[0]:.0f},{c[1]:.0f}", fill=(230, 230, 230)); thumbs.append(t); print(name, c)
    cols = 4; sh = Image.new("RGB", (cols * 480, 480 * ((len(thumbs) + cols - 1) // cols)), (5, 6, 10))
    for j, t in enumerate(thumbs): sh.paste(t, ((j % cols) * 480, (j // cols) * 480))
    sh.save(os.path.join(a.out, "sheet.png"))
