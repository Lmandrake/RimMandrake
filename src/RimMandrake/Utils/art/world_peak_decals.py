#!/usr/bin/env python3
"""Sun-lit mountain peaks for the world map (WORLD_MOUNTAINS_REDRAW_PEAKS_NOT_FIELDS). Procedural, no donor bytes.

Owner 2026-10-20: "Mountains dont look like mountains they look like farm fields ... Any chance mountains could actually
look like mountains?" Card answer the same evening: "Peaks lit toward the sun". Study:
design/Jawa/worldbuilding/worldmap_mods_study_2026-10-20.md (silhouette, hard lit/shade split along ONE sun direction,
clusters of 3-5 peaks, snow on cold lit faces, denser Impassable).

What is drawn: each cell is a PLAN-VIEW height field (we look down from orbit) of a cluster of faceted pyramids, shaded by
a sun that sits toward the TOP of the image (+V in Unity UV). The shading is quantised into three hard tones (lit facet,
mid facet, shaded facet) plus a cast shadow thrown away from the sun. RM_WorldPeaks.cs turns every quad so that its +V
axis points along the ground toward the substellar point, so every lit face on the planet faces the one sun (the "One
Direct Sun, a pure function of geometry" ruling, on the world map).

Atlas layout, 2x2 (the vanilla hill UV call, PrintTextureAtlasUVs):
  indexY 0 = the PNG's BOTTOM half = HIGH sun (elevation 60 deg, short shadows; tiles within 40 deg arc of the substellar
             point, and the night side, which has no direct sun to cast a shadow)
  indexY 1 = the PNG's TOP half    = LOW sun  (elevation 18 deg, long shadows; the terminator country)
  indexX 0/1 = two different drawings.
Colour: lit facets are a pale warm overlay and shade a near-black one, both partly transparent, so the biome face shows
through and the range takes its hue from the land under it. "<Kind>_Snowy" adds snow on the upper lit and mid facets
(RM_WorldPeaks uses it where the tile's mean temperature is below its snow line).

usage:
  python3 world_peak_decals.py gen     [--out DIR]           write 8 atlases + sheet + stats.json to DIR
  python3 world_peak_decals.py check   [--src]               spec check on DIR (default) or the installed files
  python3 world_peak_decals.py preview [--save RWS] [--center TILE] [--radius DEG] [--out DIR]
                                                              before/after render of a region (default: Dew Horn)
  python3 world_peak_decals.py install [--dry-run]           art-ledger install (art.py install)
DIR defaults to <agent storage>/rimmandrake/scratch/peakdecals.
"""
import argparse, glob, json, math, os, subprocess, sys
import numpy as np
from PIL import Image

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../.."))
MOD = "RimMandrake/TerminalBiomes"          # ships World/RM_Hills already; a member of the composed RimMandrake.Biomes
REL = "World/RM_Peaks/{}.png"
OWNER = "Peaks lit toward the sun"
N, CELL = 512, 256
SUN_ELEV = {0: 60.0, 1: 15.0}               # atlas row (indexY) -> sun elevation, degrees
KINDS = ["SmallHills", "LargeHills", "Mountains", "Impassable"]
# kind: seed, peaks (lo, hi), peak radius (lo, hi, in cell half-widths), height (lo, hi), spread (centre scatter),
#       facets (lo, hi), relief (vertical exaggeration), alpha scale
SPEC = {
    "SmallHills": dict(seed=21, peaks=(4, 6), rad=(0.20, 0.30), hgt=(0.30, 0.45), spread=0.50, facets=(5, 7), relief=1.3, a=0.62),
    "LargeHills": dict(seed=22, peaks=(4, 6), rad=(0.26, 0.38), hgt=(0.45, 0.70), spread=0.45, facets=(4, 6), relief=1.8, a=0.80),
    "Mountains":  dict(seed=23, peaks=(3, 5), rad=(0.34, 0.50), hgt=(0.75, 1.00), spread=0.40, facets=(3, 5), relief=2.6, a=1.00),
    "Impassable": dict(seed=24, peaks=(6, 8), rad=(0.36, 0.52), hgt=(0.85, 1.10), spread=0.48, facets=(3, 5), relief=3.0, a=1.00),
}
# tone: RGB, alpha at a = 1
LIT = ((238, 224, 198), 0.50)
MID = ((112, 94, 76), 0.38)
SHADE = ((26, 19, 14), 0.74)
CAST = ((18, 13, 10), 0.40)
SNOW_LIT = ((250, 251, 255), 0.88)
SNOW_SHADE = ((150, 162, 186), 0.72)
SNOWLINE = 0.52                              # fraction of the cell's highest peak
HIGH_SUN_SHADE = 0.70                        # shaded-facet alpha factor under a high sun
SHADOW_H = 0.42                              # true peak height (cell half-widths) for cast shadows


def storage_root():
    r = subprocess.run([sys.executable, os.path.expanduser("~/dev/Lodestar/bin/lib/agent_storage.py")],
                       capture_output=True, text=True, check=True).stdout.strip()
    return os.path.join(r, "rimmandrake", "scratch", "peakdecals")


def noise(rng, n, octaves=3, k0=6):
    out = np.zeros((n, n)); amp = 1.0; tot = 0.0
    for o in range(octaves):
        k = k0 * 2 ** o
        g = rng.random((k + 1, k + 1))
        img = Image.fromarray((g * 255).astype(np.uint8)).resize((n, n), Image.BICUBIC)
        out += amp * np.asarray(img, float) / 255.0; tot += amp; amp *= 0.5
    return out / tot


def height(kind, col):
    """Height field of one drawing (column) of a kind; u right, v UP (toward the sun), both in [-1, 1]."""
    s = SPEC[kind]
    rng = np.random.default_rng(s["seed"] * 10 + col)
    y, x = np.mgrid[0:CELL, 0:CELL]
    u = (x + 0.5) / CELL * 2 - 1; v = 1 - (y + 0.5) / CELL * 2
    H = np.zeros((CELL, CELL))
    n = int(rng.integers(s["peaks"][0], s["peaks"][1] + 1))
    for i in range(n):
        if i == 0:
            cu, cv = rng.uniform(-0.1, 0.1), rng.uniform(-0.1, 0.1)
        else:
            r = s["spread"] * math.sqrt(rng.uniform(0.25, 1.0)); a = rng.uniform(0, 2 * math.pi)
            cu, cv = r * math.cos(a), r * math.sin(a)
        R = rng.uniform(*s["rad"]) * (1.0 if i == 0 else 0.85)
        h0 = rng.uniform(*s["hgt"]) * (1.0 if i == 0 else rng.uniform(0.65, 0.95))
        k = int(rng.integers(s["facets"][0], s["facets"][1] + 1)); ph = rng.uniform(0, 2 * math.pi)
        d = np.full_like(u, -9.0)
        for j in range(k):                                   # polygonal cone: flat facets meeting in sharp ridges
            t = ph + 2 * math.pi * j / k + rng.uniform(-0.35, 0.35)
            stretch = rng.uniform(0.75, 1.35)                # uneven facets, spurs
            d = np.maximum(d, ((u - cu) * math.cos(t) + (v - cv) * math.sin(t)) / (R * stretch))
        H = np.maximum(H, h0 * np.clip(1 - d, 0, None) ** 0.95)
    crag = noise(rng, CELL, 3, 10)                           # small broken relief, more of it high up
    H = H * (1 + 0.05 * (crag - 0.5)) + 0.006 * (crag - 0.5) * (H > 0)
    # round fade well inside the cell: no square silhouette, and room for the cast shadow below
    rr = np.hypot(u, v)
    H *= np.clip((0.88 - rr) / 0.22, 0, 1) ** 0.7
    return np.clip(H, 0, None), u, v


def shade_cell(kind, col, row, snowy):
    s = SPEC[kind]
    H, u, v = height(kind, col)
    e = math.radians(SUN_ELEV[row])
    px = 2.0 / CELL
    z = H * s["relief"]
    gy, gx = np.gradient(z, px)             # gy is d/dy (y grows DOWN the image) = -d/dv
    dzdu, dzdv = gx, -gy
    nrm = np.stack([-dzdu, -dzdv, np.ones_like(z)], -1)
    nrm /= np.linalg.norm(nrm, axis=-1, keepdims=True)
    L = np.array([0.0, math.cos(e), math.sin(e)])
    lam = nrm @ L
    # cast shadow from the TRUE (unexaggerated) height, marched toward the sun (up the image); its darkness fades with
    # the distance from the casting slope so it never ends in a hard cut at the cell rim
    zt = H * SHADOW_H
    tan_e = math.tan(e); steps = int(min(CELL * 0.40, (zt.max() / max(tan_e, 1e-3)) / px + 2))
    cast = np.zeros_like(z); 
    for k in range(1, steps):
        shifted = np.zeros_like(zt)
        shifted[k:, :] = zt[:-k, :]        # pixel (y) sees the terrain at (y - k), i.e. k px toward the sun
        hit = shifted > zt + k * px * tan_e + 1e-4
        cast = np.where(hit & (cast == 0), 1.0 - k / (CELL * 0.40), cast)
    on = H > 0.012
    # facets classed by which way they FACE in plan (towards the sun, across it, away from it), so steep side facets
    # read as a mid tone instead of all going black; near-flat ground is mid too
    slope = np.hypot(dzdu, dzdv); face = np.degrees(np.arctan2(dzdu, -dzdv))   # 0 = facing the sun (downhill toward +v)
    steep = slope > 0.25
    lit = on & steep & (np.abs(face) < 62)
    shade = on & steep & (np.abs(face) > 118)
    mid = on & ~lit & ~shade
    incast = on & (cast > 0) & ~lit
    shade |= incast; mid &= ~incast
    rgb = np.zeros((CELL, CELL, 3)); a = np.zeros((CELL, CELL))
    for m, (c, al) in ((lit, LIT), (mid, MID), (shade, SHADE)):
        rgb[m] = c; a[m] = al * s["a"]
    if row == 0: a[shade & ~incast] *= HIGH_SUN_SHADE      # sun nearly overhead: the far facets are only dimmer
    ground_cast = (cast > 0) & ~on
    rgb[ground_cast] = CAST[0]; a[ground_cast] = CAST[1] * s["a"] * np.clip(cast[ground_cast] * 1.6, 0, 1)
    if snowy:
        hi = on & (H > SNOWLINE * H.max())
        sl = hi & (lit | mid); ss = hi & shade
        rgb[sl] = SNOW_LIT[0]; a[sl] = SNOW_LIT[1]
        rgb[ss] = SNOW_SHADE[0]; a[ss] = SNOW_SHADE[1] * s["a"]
    # soft silhouette foot (2-3 px), crisp facets
    a[on] *= np.clip(H[on] / 0.04, 0, 1)
    rr = np.maximum(np.abs(u), np.abs(v))
    a *= np.clip((0.965 - rr) / 0.03, 0, 1)                 # zero alpha on the last 3 px of the cell
    out = np.zeros((CELL, CELL, 4), np.uint8)
    out[..., :3] = np.clip(rgb, 0, 255).astype(np.uint8)
    out[..., 3] = np.clip(np.round(a * 255), 0, 255).astype(np.uint8)
    out[out[..., 3] == 0, :3] = 0
    return out


def atlas(kind, snowy):
    img = np.zeros((N, N, 4), np.uint8)
    for row in (0, 1):
        py = CELL if row == 0 else 0            # indexY 0 is the PNG's bottom half
        for col in (0, 1):
            img[py:py + CELL, col * CELL:(col + 1) * CELL] = shade_cell(kind, col, row, snowy)
    return Image.fromarray(img, "RGBA")


def names():
    return [k + sfx for k in KINDS for sfx in ("", "_Snowy")]


def stats(path, name):
    a = np.asarray(Image.open(path).convert("RGBA"), float); al = a[..., 3] / 255; bad = []
    if a.shape[:2] != (N, N): bad.append("size %s" % (a.shape[:2],))
    lum = 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]
    on = al > 0.02
    for r in (0, 1):
        for c in (0, 1):
            cc = al[r * CELL:(r + 1) * CELL, c * CELL:(c + 1) * CELL]
            rim = np.concatenate([cc[:3].ravel(), cc[-3:].ravel(), cc[:, :3].ravel(), cc[:, -3:].ravel()])
            if rim.max() > 0: bad.append("cell r%dc%d edge alpha %.3f" % (r, c, rim.max()))
            if (cc > 0.02).mean() < 0.05: bad.append("cell r%dc%d nearly empty" % (r, c))
    litf = float(((lum > 150) & on).sum() / max(on.sum(), 1)); shf = float(((lum < 50) & on).sum() / max(on.sum(), 1))
    if not name.startswith("SmallHills") and (litf < 0.08 or shf < 0.08):
        bad.append("no lit/shade split (lit %.2f shade %.2f)" % (litf, shf))
    return {"cov": round(float(on.mean()), 3), "lit_frac": round(litf, 3), "shade_frac": round(shf, 3), "bad": bad}


def gen(out):
    os.makedirs(out, exist_ok=True); res = {}
    sheet = Image.new("RGBA", (N * 4 + 50, N * 2 + 30), (170, 135, 100, 255))
    for k, name in enumerate(names()):
        p = os.path.join(out, name + ".png"); im = atlas(name.split("_")[0], name.endswith("_Snowy")); im.save(p)
        sheet.alpha_composite(im, (10 + (k // 2) * (N + 10), 10 + (k % 2) * (N + 10)))
        res[name] = stats(p, name)
        print("gen", name, res[name], flush=True)
    sheet.save(os.path.join(out, "sheet.png"))
    json.dump(res, open(os.path.join(out, "stats.json"), "w"), indent=1)
    return res


def check(out, from_src):
    res = {}
    for name in names():
        p = (os.path.join(REPO, "src", MOD, "Textures", REL.format(name)) if from_src else os.path.join(out, name + ".png"))
        res[name] = stats(p, name) if os.path.exists(p) else {"bad": ["missing " + p]}
    return res


def report(res):
    fails = 0
    for k, s in res.items():
        print(("FAIL " if s["bad"] else "ok   ") + k, {x: y for x, y in s.items() if x != "bad"}, "; ".join(s["bad"]))
        fails += bool(s["bad"])
    return fails


def install(out, dry):
    if report(check(out, False)):
        print("install refused: the files in %s fail the spec check (run gen)" % out); return 1
    bad = 0
    for name in names():
        stage = os.path.join(REPO, "Transient", "peak_decals_stage", name + ".png")   # art.py wants a file inside the clone
        os.makedirs(os.path.dirname(stage), exist_ok=True)
        open(stage, "wb").write(open(os.path.join(out, name + ".png"), "rb").read())
        cmd = [sys.executable, os.path.join(REPO, "src/RimMandrake/Utils/art/art.py"), "install", MOD, REL.format(name),
               "--file", os.path.relpath(stage, REPO), "--owner-said", OWNER] + (["--dry-run"] if dry else [])
        x = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO)
        o = (x.stdout + x.stderr).strip().splitlines(); bad += x.returncode != 0
        print(x.returncode, MOD, REL.format(name), (o[-1] if o else "")[:140], flush=True)
    print("install failures", bad); return bad


# ---------------------------------------------------------------------------------------------------- offline preview
SAVES = "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Saves"
GAME_MODS = "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods"
SNOW_C = -8.0          # mirror of RM_WorldPeaks.snowBelowC
HIGH_SUN_ARC = 40.0    # mirror of RM_WorldPeaks.highSunArc
SIZES = {"SmallHills": 1.1, "LargeHills": 1.2, "Mountains": 1.32, "Impassable": 1.42}   # mirror of RM_WorldPeaks.size*


def face_colours():
    """BiomeDef -> mean face colour, from the def dump's texture path and the deployed loose PNG (Core faces are not
    loose: they fall back to a tan)."""
    sys.path.insert(0, os.path.join(REPO, "src/RimMandrake/Utils"))
    from game_paths import DEF_DUMP
    d = json.load(open(os.path.join(DEF_DUMP, "defs", "BiomeDef.json")))
    idx = {}
    for p in glob.glob(os.path.join(GAME_MODS, "*", "**", "Textures", "World", "**", "*.png"), recursive=True):
        rel = p.split("/Textures/", 1)[1][:-4]
        idx.setdefault(rel, p)
    out = {}
    for b in d["defs"]:
        tex = (b.get("fields") or {}).get("texture"); col = (150, 125, 95)
        if tex and tex in idx:
            im = np.asarray(Image.open(idx[tex]).convert("RGB").resize((16, 16)), float)
            col = tuple(int(x) for x in im.reshape(-1, 3).mean(0))
        water = str((b.get("fields") or {}).get("isWaterBiome")).lower() == "true"
        out[b["defName"]] = (30, 45, 70) if water else col
    return out


def preview(save, center, radius, out):
    sys.path.insert(0, os.path.join(REPO, "src/RimMandrake/Utils"))
    from worldmap import WorldGrid, DECODE
    import worldgeom
    from PIL import ImageDraw
    os.makedirs(out, exist_ok=True)
    print("preview: reading", save, flush=True)
    wg = WorldGrid(save); geo = worldgeom.Geometry(wg.tiles)
    hil = np.array(wg.arrays["tileHilliness"]); temp = np.array([DECODE["tileTemperature"][0](x) for x in wg.arrays["tileTemperature"]])
    biome = [wg.biome_by_hash.get(h, "?") for h in wg.arrays["tileBiome"]]
    cols = face_colours()
    V = geo.vec
    # substellar point (lat 0, lon 0) in this module's own frame (x = cos lat cos lon, y = sin lat, z = cos lat sin lon)
    S = np.array([1.0, 0.0, 0.0])
    c = V[center]
    e1 = np.cross([0, 1, 0], c); e1 /= np.linalg.norm(e1); e2 = np.cross(c, e1)     # east, north at the centre
    W = 1800; scale = W / (2 * math.radians(radius))
    def proj(p): return (W / 2 + (p @ e1) * scale, W / 2 - (p @ e2) * scale)
    near = np.where(V @ c > math.cos(math.radians(radius * 1.45)))[0]
    tile_px = math.radians(geo.mean_tile_arc()) * scale
    print("preview: %d tiles in view, tile ~%.1f px" % (len(near), tile_px), flush=True)
    base = Image.new("RGBA", (W, W), (8, 10, 16, 255)); dr = ImageDraw.Draw(base)
    rng = np.random.default_rng(7)
    for t in near:
        poly = [proj(q) for q in geo.corners(int(t))]
        col = cols.get(biome[t], (150, 125, 95))
        jit = rng.integers(-6, 7)
        dr.polygon(poly, fill=tuple(int(np.clip(x + jit, 0, 255)) for x in col) + (255,))
    old = {k: Image.open(os.path.join(REPO, "src", MOD, "Textures", "World/RM_Hills/%s.png" % k)).convert("RGBA") for k in KINDS}
    new = {n: Image.open(os.path.join(out, "atlas", n + ".png")).convert("RGBA") for n in names()}
    kind_of = {2: "SmallHills", 3: "LargeHills", 4: "Mountains", 5: "Impassable"}

    def stamp(img, atl, cells, col, row, centre_px, size_px, angle_deg):
        cpx = atl.size[0] // cells
        cell = atl.crop((col * cpx, (cells - 1 - row) * cpx, (col + 1) * cpx, (cells - row) * cpx))
        sz = max(2, int(round(size_px)))
        cell = cell.resize((sz, sz), Image.LANCZOS).rotate(angle_deg, Image.BICUBIC, expand=True)
        img.alpha_composite(cell, (int(centre_px[0] - cell.size[0] / 2), int(centre_px[1] - cell.size[1] / 2)))

    before = base.copy(); after = base.copy()
    r1 = np.random.default_rng(1)
    hilly = [t for t in near if int(hil[t]) in kind_of]
    for t in hilly:
        k = kind_of[int(hil[t])]; p = V[t]
        jitter = {"SmallHills": 0.37, "LargeHills": 0.2}.get(k, 0.08) * r1.random()
        ja = r1.uniform(0, 2 * math.pi)
        pj = p + (e1 * math.cos(ja) + e2 * math.sin(ja)) * jitter * math.radians(geo.mean_tile_arc())
        stamp(before, old[k], 2, int(r1.integers(0, 2)), int(r1.integers(0, 2)), proj(pj), r1.uniform(0.9, 1.1) * tile_px, r1.uniform(0, 360))
        # after: sun tangent at this tile, projected into the picture
        tvec = S - (S @ p) * p; nt = np.linalg.norm(tvec)
        if nt < 1e-6: ang = 0.0
        else:
            tvec /= nt; sx, sy = tvec @ e1, tvec @ e2            # picture: x right, y up
            ang = math.degrees(math.atan2(sx, sy))               # angle from picture-up to the sun, clockwise
        arc = math.degrees(math.acos(np.clip(S @ p, -1, 1)))
        row = 1 if HIGH_SUN_ARC <= arc <= 90 else 0
        name = k + ("_Snowy" if temp[t] < SNOW_C else "")
        size = SIZES[k] * tile_px
        stamp(after, new[name], 2, int(t) % 2, row, proj(p), size, -ang)
    fb, fa = os.path.join(out, "dewhorn_before.png"), os.path.join(out, "dewhorn_after.png")
    before.convert("RGB").save(fb); after.convert("RGB").save(fa)
    pair = Image.new("RGB", (W * 2 + 20, W), (0, 0, 0)); pair.paste(before.convert("RGB"), (0, 0)); pair.paste(after.convert("RGB"), (W + 20, 0))
    fp = os.path.join(out, "dewhorn_before_after.png"); pair.resize((1200 * 2 + 13, 1200)).save(fp)
    zc = W // 2; z = 380
    zoom = Image.new("RGB", (z * 4 + 20, z * 2), (0, 0, 0))
    zoom.paste(before.convert("RGB").crop((zc - z, zc - z, zc + z, zc + z)), (0, 0))
    zoom.paste(after.convert("RGB").crop((zc - z, zc - z, zc + z, zc + z)), (z * 2 + 20, 0))
    fz = os.path.join(out, "dewhorn_before_after_zoom.png"); zoom.save(fz)
    print("preview: %d hilly tiles drawn; sun at picture-angle of centre: see arrows in after" % len(hilly), flush=True)
    for f in (fb, fa, fp, fz): print("wrote", f)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["gen", "check", "install", "preview"])
    ap.add_argument("--out"); ap.add_argument("--src", action="store_true"); ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--save", default=os.path.join(SAVES, "ASHKARR_DEV_START_2026-10-20_PARITY_QUIET_R3.rws"))
    ap.add_argument("--center", type=int, default=3648)      # the Scald's centre; Dew Horn is its outer spurs
    ap.add_argument("--radius", type=float, default=34.0)
    a = ap.parse_args(); root = a.out or storage_root(); atl = os.path.join(root, "atlas")
    if a.cmd == "gen": sys.exit(1 if report(gen(atl)) else 0)
    if a.cmd == "check": sys.exit(1 if report(check(atl, a.src)) else 0)
    if a.cmd == "preview": preview(a.save, a.center, a.radius, root); sys.exit(0)
    sys.exit(1 if install(atl, a.dry_run) else 0)
