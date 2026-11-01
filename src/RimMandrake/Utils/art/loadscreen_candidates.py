#!/usr/bin/env python3
"""PLANETARY_LOADSCREEN_RENDERS_2: geometric seeds for the Ash'karr loadscreen planet, and the check that a generated
candidate still sits where the planet's own record puts things.

The seed is the offline globe (world_beauty_render.py: real tiles, real faces, sun at the substellar point) on a 1.6:1
canvas, with the real ring drawn: RW Planet Atmosphere settings, deployed/config/...TRUE-GLORIOUS-RING.xml, planet radius
1e7, ring 1.4-2.0 R, normal on the spin axis; texture deployed/atmosphere_ring/ring_debris.png. A sentence does not hold a
camera; the seed does, so codex receives it as image 1 and every region mask here is computed from the same camera.

usage: loadscreen_candidates.py seed <dir>      write seed_<shot>.png + prompt_<shot>.txt
       loadscreen_candidates.py check [<dir>]   exit 0 only if table, candidates, registration and judge file all hold
       loadscreen_candidates.py selftest        seeds pass, mirrored seeds fail
"""
import argparse, csv, json, os, sys
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import world_beauty_render as W

REPO = W.REPO
DEFAULT = os.path.join(REPO, "Transient/planetary_loadscreen_2026-11-01")
TABLE = os.path.join(REPO, "design/RimMandrake/loadscreen_colour_reality_2026-11-01.md")
RING_TEX = os.path.join(REPO, "deployed/atmosphere_ring/ring_debris.png")
W_, H_ = 1600, 1000
RING = (1.4, 2.0)
SCALD = W.to_xyz(-0.8, -35.5)   # centroid of RUT_TheScald on the record
SHOTS = {  # centre (lat, lon) of the camera, planet radius px, disk centre px
    "crater_ring": dict(cam=(30, -38), R=390, at=(800, 490)),
    "twilight_terminator": dict(cam=(26, -70), R=430, at=(900, 480)),
    "grey_sea_limb": dict(cam=(24, 62), R=400, at=(700, 480)),
}
MIN_CANDIDATES, MAX_CANDIDATES = 3, 5
MIN_WIDTH = 1536
JUDGED = ("ring", "not_mars", "one_sun", "no_text")

PROMPT = """Image 1 is the exact camera, composition and geography of a real planet, ASH'KARR, from a false-colour map render. \
Keep every landmass boundary, the planet's size and position on the canvas, the ring's ellipse and the day/night line exactly where they are in image 1. \
Repaint image 1 as a photograph taken from orbit by a real spacecraft, for a game loading screen: real terrain with depth, wind-streaked dune fields, canyons, thin dust haze, a thin pale atmosphere rim.

What each colour in image 1 really is, seen from orbit:
{colours}

The planet is a tidally locked desert world: the sunward face is scorched ochre sand, the seas lie torn and elongated near the terminator, the far side is frozen dark under faint green and violet aurora. One small hard white sun lights everything from the right direction in image 1, and the sun itself stays out of frame. \
The ring is a vast thin sheet of fine grey-brown dust and pulverised wreckage circling the equator, seen from thousands of kilometres away: smooth soft translucent bands with dark gaps, an airbrushed continuous haze with stars faintly visible through it, exactly like Saturn's rings photographed by the Cassini probe but dustier and grey-brown. Its surface is a smooth gradient: at this distance it holds zero separate rocks, boulders or objects. It casts no broad shadow because the sun lies in its plane. The part of the ring inside the planet's shadow is dark. \
Black space with a few faint real stars. Every border between terrains is an irregular natural transition feathered by dust and erosion, with continuous natural ground from edge to edge at planetary scale. This is one planet with one sun. Wide landscape composition, full bleed, pure image with no lettering."""


def camera(cam):
    f = W.to_xyz(*cam); up = np.array([0, 0, 1.0]) - f * f[2]; up /= np.linalg.norm(up)
    return f, up, np.cross(up, f)


def grid(shot, w=W_, h=H_):
    """canvas pixel -> (u, v) in planet radii, plus the camera basis."""
    s = shot; sx = w / W_; px, py = np.meshgrid(np.arange(w), np.arange(h))
    return (px / sx - s["at"][0]) / s["R"], -(py / sx - s["at"][1]) / s["R"], camera(s["cam"])


def ring_hits(shot, w=W_, h=H_):
    """-> ring radius (nan off the ring), front flag, lit flag, per pixel."""
    u, v, (f, up, right) = grid(shot, w, h)
    o = u[..., None] * right + v[..., None] * up
    t = -o[..., 2] / f[2]; hit = o + t[..., None] * f; r = np.hypot(hit[..., 0], hit[..., 1])
    on = (r >= RING[0]) & (r <= RING[1])
    sun = W.to_xyz(0.0, 0.0); along = hit @ sun; perp = np.linalg.norm(hit - along[..., None] * sun, axis=-1)
    disk = u ** 2 + v ** 2 <= 1
    visible = on & ((t > 0) | ~disk)
    return np.where(visible, r, np.nan), t > 0, np.where(along < 0, np.clip((perp - 0.92) / 0.2, 0, 1), 1.0)


class Warped:
    """nearest-tile lookup through a smooth 3D warp, so no biome border keeps the hexagon of its tile. Amplitude about one
    and a half hexes: far below the Scald's radius, so the crater stays a circle."""

    def __init__(self, tree, spacing, seed=11, waves=48):
        r = np.random.default_rng(seed); self.tree = tree
        d = r.normal(size=(waves, 3)); d /= np.linalg.norm(d, axis=1, keepdims=True)
        self.k = d * np.exp(r.uniform(np.log(6), np.log(70), (waves, 1))); self.ph = r.uniform(0, 6.283, (waves, 3))
        self.amp = 1.5 * spacing / np.sqrt(waves) / (np.linalg.norm(self.k, axis=1, keepdims=True) / 14) ** 0.5

    def query(self, pts, k=3):
        out = np.zeros_like(pts)
        for j in range(3):
            out[:, j] = (np.sin(pts @ self.k.T + self.ph[:, j]) * self.amp.T).sum(1)
        rim = np.clip((np.degrees(np.arccos(np.clip(pts @ SCALD, -1, 1))) - 16) / 6, 0.2, 1)[:, None]   # the Scald stays a circle (owner 2026-08-25)
        q = pts + out * rim; return self.tree.query(q / np.linalg.norm(q, axis=1, keepdims=True), k=k)


def strip_profile():
    """the texture's radial profile: rows or columns, whichever axis is the long one holds the radius."""
    a = np.asarray(Image.open(RING_TEX).convert("RGBA")).astype(np.float32)
    return a[..., :3].mean(0) if a.shape[1] > a.shape[0] else a[..., :3].mean(1), (a[..., 3] / 255).mean(0)


def seed_image(shot, tree, face, hills, faces, repeats):
    s = shot; size = int(round(2 * s["R"] * 1.02)); g = W.render(tree, face, hills, faces, s["cam"], size, repeats, lit=True)
    canvas = np.zeros((H_, W_, 3), np.float32) + np.array([3, 4, 8], np.float32)
    x0 = s["at"][0] - size // 2; y0 = s["at"][1] - size // 2
    u, v, _ = grid(s); disk = u ** 2 + v ** 2 <= 1
    for y in range(max(0, y0), min(H_, y0 + size)):
        sel = disk[y, max(0, x0):min(W_, x0 + size)]
        src = g[y - y0, max(0, x0) - x0:min(W_, x0 + size) - x0]
        canvas[y, max(0, x0):min(W_, x0 + size)][sel] = src[sel]
    r, _, lit = ring_hits(s); col, alpha = strip_profile(); n = len(alpha)
    m = ~np.isnan(r); i = ((r[m] - RING[0]) / (RING[1] - RING[0]) * (n - 1)).astype(int)
    grey = col[alpha > 0.05].mean(0)   # the strip's own bands, muted: at seed scale raw they read as painted hoops
    a = alpha[i][:, None] * 0.8; c = (0.35 * col[i] + 0.65 * grey * col[i].mean(1, keepdims=True) / grey.mean()) * (0.08 + 0.57 * lit[m])[:, None]
    canvas[m] = canvas[m] * (1 - a) + c * a
    return np.clip(canvas, 0, 255).astype(np.uint8)


def tile_records():
    with open(os.path.join(REPO, "world/ASHKARR_WORLDMAP_tiles.csv"), newline="") as f: return list(csv.DictReader(f))


def table_rows():
    """the machine half of the colour table: lines `| RUT_x | face | seen from orbit | sheet |`."""
    out = {}
    for line in open(TABLE, encoding="utf-8"):
        c = [p.strip(" `") for p in line.strip().strip("|").split("|")]
        if len(c) >= 5 and c[0].startswith(("RUT_", "ZBiome_")): out[c[0]] = dict(face=c[1], hex=c[2], orbit=c[3], sheet=c[4])
    return out


def colour_lines():
    """prompt lines: one per visible colour family, biggest first, from the table only."""
    rows = table_rows(); count = {}
    for r in tile_records(): count[r["biome"]] = count.get(r["biome"], 0) + 1
    return "\n".join(f"- {v['hex']}: {v['orbit']}" for k, v in sorted(rows.items(), key=lambda kv: -count.get(kv[0], 0)))


def region_mask(shot, biomes, tiles_xyz, tile_biome, w=W_, h=H_):
    """canvas mask of the tiles of `biomes`, visible hemisphere only (grown to the hex spacing on the disk)."""
    f, up, right = camera(shot["cam"]); m = np.isin(tile_biome, biomes); p = tiles_xyz[m]; p = p[p @ f > 0.25]
    mask = np.zeros((h, w), bool); sc = w / W_
    if not len(p): return mask
    px = ((p @ right) * shot["R"] + shot["at"][0]) * sc; py = (-(p @ up) * shot["R"] + shot["at"][1]) * sc
    rad = max(1, int(0.0252 * shot["R"] * sc / 1.5))
    for x, y in zip(px.astype(int), py.astype(int)):
        if 0 <= x < w and 0 <= y < h: mask[max(0, y - rad):y + rad + 1, max(0, x - rad):x + rad + 1] = True
    return mask


def blur_box(m, k):
    a = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).resize((m.shape[1] // k, m.shape[0] // k), Image.BOX)).astype(np.float32) / 255
    return a


def register(path, shot, xyz, biomes):
    """measurements of one candidate against the record's geometry; each returns (value, pass)."""
    im = np.asarray(Image.open(path).convert("RGB").resize((W_, H_), Image.LANCZOS)).astype(np.float32)
    lum = im.mean(2); bluish = im[..., 2] - im[..., 0]; out = {}
    u, v, (f, up, right) = grid(shot); disk = u ** 2 + v ** 2 <= 0.97
    # terminator: lit hemisphere bright, night hemisphere dark, on the real sun vector
    z = np.sqrt(np.clip(1 - u ** 2 - v ** 2, 0, 1)); p = u[..., None] * right + v[..., None] * up + z[..., None] * f
    l = p @ W.to_xyz(0.0, 0.0); day, night = disk & (l > 0.25), disk & (l < -0.12)
    if night.sum() > 2000:
        ratio = float(lum[day].mean() / (lum[night].mean() + 1)); out["terminator_day_night_lum_ratio"] = (round(ratio, 2), ratio >= 2.5)
    # seas: a water body in the record is bluer than the ground around it, on the lit side
    land = disk & (l > 0.08)
    for name, bs in (("Scald", ["RUT_TheScald"]), ("TwilightSea", ["RUT_TwilightSea"]), ("GreySea", ["RUT_GreySea"])):
        m = region_mask(shot, bs, xyz, biomes) & land
        if m.sum() < 1500: continue
        ring_land = np.logical_and(land, ~m); ring_land &= np.asarray(Image.fromarray((blur_box(m, 9) > 0.02).astype(np.uint8) * 255).resize((W_, H_), Image.BILINEAR)) > 40
        delta = float(bluish[m].mean() - bluish[ring_land].mean()) if ring_land.sum() > 400 else 0.0
        out[f"sea_{name}_bluer_than_shore"] = (round(delta, 1), delta >= 8)
    # ring: the off-disk ring is brighter than empty space next to it
    r, _, lit = ring_hits(shot); off = ~(u ** 2 + v ** 2 <= 1.03); inside = ~np.isnan(r) & off & (lit > 0.9)
    u2, v2, _ = grid(shot); out_sky = np.isnan(r) & off & (np.hypot(u2, v2) > 1.1)
    c = float(np.median(lum[inside]) - np.median(lum[out_sky])); out["ring_vs_sky_lum"] = (round(c, 1), c >= 6)
    return out


def check(d):
    fails = []; rows = table_rows(); records = tile_records(); census = sorted({r["biome"] for r in records})
    missing = [b for b in census if b not in rows]; 
    for b, r in rows.items():
        if not os.path.exists(os.path.join(REPO, "design/Jawa/worldbuilding/biomes", r["sheet"])): fails.append(f"table: {b} cites missing sheet {r['sheet']}")
    if missing: fails.append(f"table misses biomes {missing}")
    print(f"table: {len(rows)} rows for {len(census)} biomes on the record")
    cands = sorted(n for n in os.listdir(d) if n.startswith("candidate_") and n.endswith(".png"))
    if not MIN_CANDIDATES <= len(cands) <= MAX_CANDIDATES: fails.append(f"{len(cands)} candidates, wanted {MIN_CANDIDATES}-{MAX_CANDIDATES}")
    xyz = W.to_xyz(np.array([float(r["lat"]) for r in records]), np.array([float(r["lon"]) for r in records]))
    biomes = np.array([r["biome"] for r in records]); result = {}
    judge_path = os.path.join(d, "judge.json"); judge = json.load(open(judge_path)) if os.path.exists(judge_path) else None
    if judge is None: fails.append("judge.json missing")
    for n in cands:
        key = next((k for k in SHOTS if n.startswith(f"candidate_{k}")), None)
        if key is None: fails.append(f"{n}: names no shot"); continue
        p = os.path.join(d, n); w = Image.open(p).size[0]
        if w < MIN_WIDTH: fails.append(f"{n}: {w} wide")
        res = register(p, SHOTS[key], xyz, biomes); result[n] = res
        if not any(k.startswith("sea_") for k in res): fails.append(f"{n}: no sea measurable")
        for k, (val, ok) in res.items():
            print(f"{n} {k} {val} {'ok' if ok else 'FAIL'}")
            if not ok: fails.append(f"{n}: {k} = {val}")
        v = (judge or {}).get(n, {})
        for q in JUDGED:
            if v.get(q) is not True: fails.append(f"{n}: judge {q} = {v.get(q)}")
    json.dump(result, open(os.path.join(d, "registration.json"), "w"), indent=1)
    for x in fails: print("FAIL", x)
    print("CHECK", "PASS" if not fails else "FAIL", len(cands), "candidates"); return 1 if fails else 0


def selftest():
    """the instrument must see: each shot's seed passes its registration, and the seed mirrored fails the terminator."""
    rec = tile_records(); xyz = W.to_xyz(np.array([float(r["lat"]) for r in rec]), np.array([float(r["lon"]) for r in rec])); b = np.array([r["biome"] for r in rec])
    for k, s in SHOTS.items():
        p = os.path.join(DEFAULT, f"seed_{k}.png"); assert all(ok for _, ok in register(p, s, xyz, b).values()), k
        m = "/tmp/loadscreen_mirror.png"; Image.open(p).transpose(Image.FLIP_LEFT_RIGHT).save(m)
        assert not register(m, s, xyz, b)["terminator_day_night_lum_ratio"][1], k
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0]); ap.add_argument("verb", choices=("seed", "check", "selftest")); ap.add_argument("dir", nargs="?", default=DEFAULT)
    a = ap.parse_args(); os.makedirs(a.dir, exist_ok=True)
    if a.verb == "check": sys.exit(check(a.dir))
    if a.verb == "selftest": return selftest()
    xyz, face, hills, keys, _ = W.load_tiles(); faces = W.load_faces(keys); tree = W.Nearest(xyz)
    spacing = float(np.median(tree.query(xyz[::40], k=2)[0][:, 1])); repeats = 1 / (W.HEXES_PER_REPEAT * spacing); tree = Warped(tree, spacing)
    for k, s in SHOTS.items():
        Image.fromarray(seed_image(s, tree, face, hills, faces, repeats)).save(os.path.join(a.dir, f"seed_{k}.png"), optimize=True)
        open(os.path.join(a.dir, f"prompt_{k}.txt"), "w", encoding="utf-8").write(PROMPT.format(colours=colour_lines())); print("seed", k)


if __name__ == "__main__": main()
