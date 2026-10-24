#!/usr/bin/env python3
"""World WATER variations for the owner to choose between (WORLD_WATER_REDRAW_SEAS_THAT_READ_DEEP; owner 2026-10-24:
"Especially important is to get the water right too").  Program: design/Jawa/worldbuilding/world_look_program_2026-10-24.md.

What is varied, per the ticket: the water FACE (colour and ripple; the texture Custom/WorldOcean draws) and the two sea FILMS
RM_WorldLook lays over every water tile (src/RimMandrake/BiomesShell/Source/RM_WorldLook.cs, BuildSea). Depth can come only
from the films: the ocean shader ignores UV0 (measured 2026-10-20), so a face cannot carry it.

How faithful the render is to the game's inputs:
  face     made by biome_worldfaces' own pipeline (make()); the "row" colour with the "wavelets" ripple is asserted
           byte-identical to biome_worldfaces.make(<sea>), i.e. the RUT twin face as installed.
  films    rebuilt the way BuildSea builds them: every water hex is a 13-point mesh (centre, half-way ring, corners); each
           point's distance to the nearest COAST VERTEX (a corner shared with a land hex) is measured in tiles
           (tile spacing = sqrt(hex area), as the C# takes sqrt(4 pi r^2 / tiles)) and capped at the films' reach; the
           alpha is computed per point (shore a*(1-d/tiles)^2, deep a*smoothstep(d/tiles)) and interpolated linearly
           across the mesh's 18 triangles, as vertex colours are; then the shore film and the deep film are alpha-blended
           over the face in that order (queues 3502, 3503).
  coast    a hard hex edge: the soft-border pass never blends a water tile (Blends() excludes the WorldOcean shader).
  NOT modelled: the planet's sun lighting (both the ocean and the lit films are drawn unlit here), the real _MacroTex
           (a 10 % random stand-in, as world_face_variants), the sphere's curvature, and the face scale in game, which is
           UNMEASURED (TEX_PER_HEX = 160 assumes ~3.2 hexes per face, as world_face_variants).

usage:  python3 world_water_variants.py gen [--out DIR]      faces, scenes, stats.json, prereview contact strips
        python3 world_water_variants.py gen2|sheet2 [--out DIR]   round 2 (Twilight stained glass, still dark Chill); DIR gets _r2
        python3 world_water_variants.py gen3|sheet3|faces [--out DIR]  round 3 (panes quartered, Chill abyss; faces = the 512 px files to install); DIR gets _r3
        python3 world_water_variants.py sheet [--out DIR]    the owner's review page in Transient/ (keeps his decisions file)
DIR defaults to <agent storage>/rimmandrake/scratch/worldwater_variants.  Installs nothing.
"""
import argparse, colorsys, json, math, os, re, shutil, sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import biome_worldfaces as BW            # noqa: E402  face pipeline, noise, stats, verdict
import world_face_variants as WF         # noqa: E402  hex grid, caption/stack helpers, sheet template hooks

N, SQ3, TEX_PER_HEX = BW.N, math.sqrt(3), WF.TEX_PER_HEX
band, warped, gblur, z = BW.band, BW.warped, BW.gblur, BW.z
SEAS = ["GreySea", "TwilightSea", "Scald", "Chill", "MineralWater"]
SEA_LABEL = {"GreySea": "Grey Sea", "TwilightSea": "Twilight Sea", "Scald": "The Scald", "Chill": "The Chill",
             "MineralWater": "Mineral water (lake)"}
LAND = "Stillsand"                       # the Dune Sea every shipping biome sits in: one neutral coast for all renders
RIPPLE_SEA = "TwilightSea"               # the ripple options are shown on this sea's own colour row

# ---------------------------------------------------------------- films (RM_WorldLook settings defaults, read 2026-10-24)
FILMS = {
    "today": {"shore": ((0.40, 0.62, 0.72), 0.40, 1.0), "deep": ((0.05, 0.09, 0.20), 0.50, 4.0),
              "label": "Films as installed: pale shore film over 1 tile, dark deep film rising over 4 tiles",
              "effect": "Keep the defaults in RM_WorldLook (seaShore 0.40 over 1 tile, seaDeep 0.50 over 4). No work."},
    "shelf": {"shore": ((0.40, 0.62, 0.72), 0.45, 2.0), "deep": ((0.05, 0.09, 0.20), 0.62, 6.0),
              "label": "Wider shelf: shore film over 2 tiles, deep film darker and rising over 6",
              "effect": "Same mechanism, new tunables (seaShoreAlpha 0.45, seaShoreTiles 2, seaDeepAlpha 0.62, seaDeepTiles 6). Settings only."},
    "off":   {"shore": None, "deep": None,
              "label": "No films: the face alone (the 'sea depth' Mod Setting off)",
              "effect": "What a sea looks like with the depth shading switched off; shown so the films' share is visible."},
}

# ---------------------------------------------------------------- face options
def hsv_shift(hexcol, sat_k, val_k, val_cap=None):
    r, g, b = (BW.H(hexcol) / 255).tolist()
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    s = min(s * sat_k, 0.56); v = v * val_k   # capped so the face mean stays under the water rule's 60 % saturation
    if val_cap is not None: v = min(v, val_cap / 255)
    return "#%02x%02x%02x" % tuple(int(round(c * 255)) for c in colorsys.hsv_to_rgb(h, s, v))


COLOURS = {   # (sat factor, value factor, value cap): applied to the row's base and accent alike
    "row":   (1.00, 1.00, None),
    "clear": (1.15, 1.16, 136),          # lighter, clearer water; capped under the water rule (mean value <= 140)
    "deep":  (1.10, 0.80, None),         # darker, richer
}
COLOUR_LABEL = {"row": "today's colour row (the RUT twin face)", "clear": "lighter and clearer", "deep": "darker and richer"}


def ripple_fields(kind, s):
    """(A short crossing "chop" was tried 2026-10-24 and dropped at prereview: at every blur it read as cellular noise.)
    (mix weight toward the accent 0..1, zero-mean detail) for a ripple style; s = the row's seed * 1000."""
    if kind == "wavelets":               # biome_worldfaces' own water style: one-direction wavelet streaks 15-40 px
        w, det, _ = BW.style_fields("water", s)
        return w, det
    w = np.clip(0.5 + 0.15 * band(3, 8, s + 121), 0, 1)
    if kind == "calm":                   # no streaks: soft blots 30-90 px, low-passed so nothing speckles
        det = z(0.75 * z(gblur(band(6, 16, s + 130), 2.5)) + 0.25 * z(band(3, 6, s + 131)))
        return w, det
    if kind == "swell":                  # long parallel swell bands ~40 px apart, stretched far along x, gently warped
        sw = warped(9, 15, s + 140, 6, ax=0.12, ay=1.0)
        det = 0.70 * z(sw) + 0.20 * z(np.clip(sw - 1.1, 0, None)) + 0.10 * band(40, 90, s + 141)
        return np.clip(w + 0.08 * z(sw), 0, 1), z(det)
    raise ValueError(kind)


RIPPLES = {
    "wavelets": ("Wavelets (today): one-direction streaks 15-40 px", "The installed ripple of the RUT twin faces. No work."),
    "calm": ("Calm: no streaks, soft blots only", "Quietest; the sea reads by colour and films alone."),
    "swell": ("Long swell: parallel bands ~40 px apart", "Open-ocean read; bands may show as stripes at far zoom."),
}


def make_water(key, colour="row", ripple="wavelets"):
    """biome_worldfaces.make() with the colour and ripple swapped in; identical to make(key) for row + wavelets."""
    base, sec, style, tsd, s, _p, _f = BW.F[key]
    assert style == "water" and key not in BW.CALM, key
    sk, vk, cap = COLOURS[colour]
    if colour != "row": base, sec = hsv_shift(base, sk, vk, cap), hsv_shift(sec, sk, vk, cap)
    b = BW.H(base); m = BW.H(sec)
    w, det = ripple_fields(ripple, s * 1000)
    img = b[None, None, :] * (1 - w[..., None]) + m[None, None, :] * w[..., None]
    lum = det[..., None] * (0.35 + 0.65 * img / max(img.mean(), 1))
    lo, hi = 0.0, 40.0
    for _ in range(30):
        a = (lo + hi) / 2
        sd = (img + lum * a).reshape(-1, 3).std(0).mean()
        lo, hi = (a, hi) if sd < tsd else (lo, a)
    out = img + lum * ((lo + hi) / 2)
    out += (b - out.reshape(-1, 3).mean(0))[None, None, :] * 0.5
    return np.clip(np.rint(out), 0, 255).astype(np.uint8), (base, sec)


# ---------------------------------------------------------------- the coast scene
ISLANDS = [(-4.0, -2.0, 0.6), (-7.0, 3.0, 1.4), (-18.0, -9.0, 2.5), (-28.0, 12.0, 3.5), (-33.0, -18.0, 1.2), (-12.0, 16.0, 1.0)]


def is_land(X, Y):
    """X, Y in tile spacings from the scene centre: a wavy mainland coast on the right, an inlet, and a few islands."""
    main = X > 2.0 + 1.6 * np.sin(Y * 0.45) + 0.8 * np.sin(Y * 1.3 + 1.0)
    inlet = ((X - 9.0) / 5.0) ** 2 + ((Y + 12.0) / 2.2) ** 2 < 1.0
    land = main & ~inlet
    for ix, iy, ir in ISLANDS: land |= (X - ix) ** 2 + (Y - iy) ** 2 < ir * ir
    return land


ZOOMS = {  # hex circumradius on screen, supersample, output size, scene centre offset (tiles)
    "close": (TEX_PER_HEX / SQ3, 1.0, (1024, 640), (-2.2, 0.0)),
    "mid": (34.0, 2.0, (1100, 640), (0.0, 0.0)),
    "far": (7.5, 4.5, (1100, 640), (0.0, 0.0)),
}
CORNER = [(math.cos(math.radians(-30 + 60 * j)), math.sin(math.radians(-30 + 60 * j))) for j in range(6)]
SPACING = math.sqrt(1.5 * SQ3)          # sqrt(hex area) for circumradius 1: the C#'s tileSpacing


def _bary(a, b, P):
    """barycentric weights of (a, b) in triangle P = [(a1,b1), (a2,b2), (a3,b3)]."""
    (x1, y1), (x2, y2), (x3, y3) = P
    det = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3)
    l1 = ((y2 - y3) * (a - x3) + (x3 - x2) * (b - y3)) / det
    l2 = ((y3 - y1) * (a - x3) + (x1 - x3) * (b - y3)) / det
    return l1, l2, 1 - l1 - l2


class Scene:
    """Everything about one zoom that does not depend on the face: hexes, land mask, texture coords, macro, film alphas."""

    def __init__(self, zoom):
        size_out, ss, (Wo, Ho), (ox, oy) = ZOOMS[zoom]
        size = size_out * ss
        W, Hh = int(Wo * ss), int(Ho * ss)
        self.zoom, self.size, self.W, self.H, self.out = zoom, size, W, Hh, (Wo, Ho)
        qs, rs = WF.hex_ids(W, Hh, size)
        x0, y0 = W / 2 + ox * SQ3 * size, Hh / 2 + oy * SQ3 * size        # scene centre in pixels
        self.x0, self.y0 = x0, y0
        # every hex in view plus a 7-tile margin, so coast vertices just outside the frame still count
        q0, q1, r0, r1 = qs.min() - 7, qs.max() + 7, rs.min() - 7, rs.max() + 7
        Q, R = np.meshgrid(np.arange(q0, q1 + 1), np.arange(r0, r1 + 1), indexing="ij")
        cx = size * (SQ3 * Q + SQ3 / 2 * R); cy = size * 1.5 * R
        land = is_land((cx - x0) / (SQ3 * size), (cy - y0) / (SQ3 * size))
        self.q0, self.r0, self.land = q0, r0, land
        iq, ir = qs - q0, rs - r0
        self.pix_land = land[iq, ir]
        # coast vertices: corners shared by a land hex and a water hex (unit circumradius, world coords)
        def corners(mask):
            keys = set()
            for q, r in zip(Q[mask].tolist(), R[mask].tolist()):
                ccx, ccy = SQ3 * q + SQ3 / 2 * r, 1.5 * r
                for cxo, cyo in CORNER: keys.add((round((ccx + cxo) * 1000), round((ccy + cyo) * 1000)))
            return keys
        coast = np.array(sorted(corners(land) & corners(~land)), np.float64) / 1000.0
        self.coast = coast
        # mesh points of every water hex in view: centre, 6 half-way points, 6 corners (unit circumradius)
        uq = sorted(set(zip(iq[~self.pix_land].tolist(), ir[~self.pix_land].tolist())))
        self.hidx = -np.ones(land.shape, np.int32)
        for n_, (a, b) in enumerate(uq): self.hidx[a, b] = n_
        hq = np.array([a + q0 for a, _ in uq], np.float64); hr = np.array([b + r0 for _, b in uq], np.float64)
        hc = np.stack([SQ3 * hq + SQ3 / 2 * hr, 1.5 * hr], 1)                       # (n, 2)
        off = np.array([(0.0, 0.0)] + [(0.5 * c, 0.5 * s) for c, s in CORNER] + CORNER)  # (13, 2)
        pts = hc[:, None, :] + off[None, :, :]                                      # (n, 13, 2)
        flat = pts.reshape(-1, 2); d = np.full(len(flat), np.inf)
        for i in range(0, len(coast), 64):                                         # chunked nearest-coast-vertex
            c = coast[i:i + 64]
            d = np.minimum(d, np.sqrt(((flat[:, None, :] - c[None, :, :]) ** 2).sum(2)).min(1))
        self.pt_tiles = (d / SPACING).reshape(-1, 13)                               # distance in tiles, per mesh point
        self.pt_tiles[:, 7:][np.isclose(d.reshape(-1, 13)[:, 7:], 0, atol=1e-6)] = 0.0  # a coast corner is exactly 0
        # per water pixel: which hex, which sector, and the (a, b) coordinates inside that sector
        yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float64)
        pcx = size * (SQ3 * qs + SQ3 / 2 * rs); pcy = size * 1.5 * rs
        dx, dy = (xx - pcx) / size, (yy - pcy) / size
        sect = (np.floor(((np.degrees(np.arctan2(dy, dx)) + 30.0) % 360.0) / 60.0).astype(int)) % 6
        cA = np.array([c for c, _ in CORNER]); sA = np.array([s for _, s in CORNER])
        c0, s0, c1, s1 = cA[sect], sA[sect], cA[(sect + 1) % 6], sA[(sect + 1) % 6]
        det = c0 * s1 - c1 * s0
        a = np.clip((dx * s1 - dy * c1) / det, 0, 1); b = np.clip((dy * c0 - dx * s0) / det, 0, 1)
        sab = np.maximum(a + b, 1e-9); over = sab > 1; a = np.where(over, a / sab, a); b = np.where(over, b / sab, b)
        self.a, self.b, self.sect = a, b, sect
        self.hpix = self.hidx[iq, ir]
        # texture coordinates (world-planar projection, as world_face_variants) and the macro stand-in
        hexw = size * SQ3
        self.u = ((xx / hexw) * TEX_PER_HEX).astype(np.int64) % N
        self.v = ((yy / hexw) * TEX_PER_HEX).astype(np.int64) % N
        self.X = ((xx - x0) / hexw).astype(np.float32); self.Y = ((yy - y0) / hexw).astype(np.float32)   # tiles, world-planar
        cell = max(int(size * 6), 1)
        mac = np.random.default_rng(5).random((max(Hh // cell, 2), max(W // cell, 2)))
        self.macro = np.asarray(Image.fromarray((mac * 255).astype(np.uint8)).resize((W, Hh), Image.BICUBIC), np.float32) / 255 - 0.5
        self.alpha = {}

    def film_alpha(self, fn):
        """per-pixel alpha of one film: fn(distance in tiles) evaluated at the 13 mesh points, rounded to a byte as a
        Color32 is, then interpolated linearly over the triangle the pixel falls in."""
        A = np.round(np.clip(fn(self.pt_tiles), 0, 1) * 255) / 255                 # (n, 13)
        out = np.zeros((self.H, self.W), np.float32)
        wm = ~self.pix_land
        h, j, a, b = self.hpix[wm], self.sect[wm], self.a[wm], self.b[wm]
        Ac = A[h, 0]; Am0 = A[h, 1 + j]; Am1 = A[h, 1 + (j + 1) % 6]; Ao0 = A[h, 7 + j]; Ao1 = A[h, 7 + (j + 1) % 6]
        inner = (a + b) <= 0.5
        v = np.empty_like(a)
        v[inner] = (1 - 2 * a[inner] - 2 * b[inner]) * Ac[inner] + 2 * a[inner] * Am0[inner] + 2 * b[inner] * Am1[inner]
        t1 = ~inner & (2 * a + b >= 1)                                              # triangle (m0, o0, o1)
        l1, l2, l3 = _bary(a[t1], b[t1], [(0.5, 0), (1, 0), (0, 1)])
        v[t1] = l1 * Am0[t1] + l2 * Ao0[t1] + l3 * Ao1[t1]
        t2 = ~inner & ~(2 * a + b >= 1)                                             # triangle (m0, o1, m1)
        l1, l2, l3 = _bary(a[t2], b[t2], [(0.5, 0), (0, 1), (0, 0.5)])
        v[t2] = l1 * Am0[t2] + l2 * Ao1[t2] + l3 * Am1[t2]
        out[wm] = np.clip(v, 0, 1)
        return out

    def films(self, key):
        if key not in self.alpha:
            f = FILMS[key]; res = []
            if f["shore"]:
                col, al, tl = f["shore"]
                res.append((np.array(col, np.float32) * 255, self.film_alpha(lambda d: al * (1 - np.clip(d / max(0.01, tl), 0, 1)) ** 2)))
            if f["deep"]:
                col, al, tl = f["deep"]
                def ss(x): x = np.clip(x, 0, 1); return x * x * (3 - 2 * x)          # Mathf.SmoothStep(0, 1, x)
                res.append((np.array(col, np.float32) * 255, self.film_alpha(lambda d: al * ss(d / max(0.01, tl)))))
            self.alpha[key] = res
        return self.alpha[key]

    def glass_alpha(self):
        """vertex alpha of a swirl-layer overlay on a water biome: 1 inside, about half at a corner shared with land
        (BuildSwirls: strength x share of the biome among the tiles meeting at the corner)."""
        if "_glass" not in self.alpha: self.alpha["_glass"] = self.film_alpha(lambda d: np.where(d <= 1e-6, 0.5, 1.0))
        return self.alpha["_glass"]

    def sample(self, tex, period_tiles):
        """bilinear, wrapping sample of an N x N texture laid world-planar over the scene, one repeat per period_tiles."""
        fx = (self.X / period_tiles * N) % N; fy = (self.Y / period_tiles * N) % N
        x0 = np.floor(fx).astype(np.int64); y0 = np.floor(fy).astype(np.int64)
        ax = (fx - x0)[..., None]; ay = (fy - y0)[..., None]; x1 = (x0 + 1) % N; y1 = (y0 + 1) % N
        t = tex if tex.ndim == 3 else tex[..., None]
        out = (t[y0, x0] * (1 - ax) + t[y0, x1] * ax) * (1 - ay) + (t[y1, x0] * (1 - ax) + t[y1, x1] * ax) * ay
        return out if tex.ndim == 3 else out[..., 0]

    def render(self, sea_face, land_face, film="today", glass=None, films_on_sea=True):
        img = np.where(self.pix_land[..., None], land_face[self.v, self.u], sea_face[self.v, self.u]).astype(np.float32)
        img = img * (1 + 0.10 * self.macro[..., None])
        for col, al in (self.films(film) if films_on_sea else []):                 # shore (3502) then deep (3503)
            img = img * (1 - al[..., None]) + col[None, None, :] * al[..., None]
        if glass is not None:                                                      # swirl layer, queue 3506, over the films
            rgb, a, period = glass
            ga = (self.sample(a, period) * self.glass_alpha())[..., None]
            img = img * (1 - ga) + self.sample(rgb, period) * ga
        im = Image.fromarray(np.clip(np.rint(img), 0, 255).astype(np.uint8))
        return im.resize(self.out, Image.BOX) if im.size != self.out else im


# ---------------------------------------------------------------- generation
def items():
    """(id, sea, colour, ripple, film, group) for every row of the sheet."""
    rows = [(f"film_{k}", RIPPLE_SEA, "row", "wavelets", k, "1. Depth films (every sea)") for k in ("today", "shelf", "off")]
    rows += [(f"ripple_{k}", RIPPLE_SEA, "row", k, "today", "2. Ripple (every sea)") for k in RIPPLES]
    for s in SEAS:
        rows += [(f"{s}_{c}", s, c, "wavelets", "today", f"3. Colour: {SEA_LABEL[s]}") for c in COLOURS]
    return rows


JPG = dict(quality=95, subsampling=0)


def gen(out):
    os.makedirs(os.path.join(out, "sheet"), exist_ok=True)
    land = BW.make(LAND)
    # fidelity: the row + wavelets face must be the face biome_worldfaces installs for that sea
    for s in SEAS:
        mine, _ = make_water(s)
        assert np.array_equal(mine, BW.make(s)), f"{s}: make_water(row, wavelets) differs from biome_worldfaces.make"
    print("fidelity: row+wavelets == biome_worldfaces.make for", ", ".join(SEAS))
    scenes = {zm: Scene(zm) for zm in ZOOMS}
    for zm, sc in scenes.items():
        print(f"scene {zm}: {sc.W}x{sc.H} internal, {len(sc.coast)} coast vertices, {sc.pt_tiles.shape[0]} water hexes")
    stats = {}
    faces = {}
    for iid, sea, colour, ripple, film, _g in items():
        fk = (sea, colour, ripple)
        if fk not in faces: faces[fk] = make_water(sea, colour, ripple)
        face, (base, sec) = faces[fk]
        st = BW.stats(face); bad = BW.verdict(sea, st, face.shape)
        stats[iid] = {"stats": st, "check": bad, "base": base, "accent": sec}
        sh = os.path.join(out, "sheet")
        WF.tiled(face).save(os.path.join(sh, f"{iid}_file.png"))
        for zm, sc in scenes.items():
            sc.render(face, land, film).save(os.path.join(sh, f"{iid}_{zm}.jpg"), **JPG)
        mid = Image.open(os.path.join(sh, f"{iid}_mid.jpg"))
        mid.crop((80, 120, 80 + 420, 120 + 280)).save(os.path.join(sh, f"{iid}.jpg"), **JPG)
        print(iid, st["mean"], "sd", st["sd"], "blk", st["blk"], "val", st["val"], "CHECK " + "; ".join(bad) if bad else "ok")
    json.dump(stats, open(os.path.join(out, "stats.json"), "w"), indent=1)
    prereview(out)


def prereview(out):
    """Contact strips for the agent's own look (not for the owner): 1:1 crops, never resized, <= 1500 px wide."""
    sh, pr = os.path.join(out, "sheet"), os.path.join(out, "prereview")
    os.makedirs(pr, exist_ok=True)
    groups = {}
    for iid, _s, _c, _r, _f, g in items(): groups.setdefault(g, []).append(iid)
    for g, ids in groups.items():
        for zm, (x, y) in (("close", (300, 120)), ("mid", (60, 60)), ("far", (100, 80))):
            box = (x, y, x + 320, y + 300)          # 320 wide so seven crops stay under 1500 px
            strip = WF.hstack([WF.caption(Image.open(os.path.join(sh, f"{i}_{zm}.jpg")).crop(box), f"{i} {zm}", 14) for i in ids])
            strip.save(os.path.join(pr, f"{g.split('.')[0]}_{g.split(': ')[-1].replace(' ', '')[:14]}_{zm}.jpg"), **JPG)


# ---------------------------------------------------------------- the review sheet
STEM = "world_water_review_2026-10-24"
PREFILL = {"film_today": "maybe", "film_shelf": "pick", "film_off": "no",
           "ripple_wavelets": "pick", "ripple_calm": "maybe", "ripple_swell": "maybe"}
FILE_CAP = "the face FILE, 2x2 tiled, 1:1 pixels (1024 px; each 512 px tile is the whole texture)"
CLOSE_CAP = "close zoom at a coast, one texel per screen pixel (not resampled)"
MID_CAP = "mid zoom, offline render (face ~0.37x; ~19 tiles across)"
FAR_CAP = "far zoom, offline render (face ~0.08x; ~85 tiles across)"


def copy_images(out, stem):
    img = os.path.join(BW.REPO, "Transient", stem + "_img")
    if os.path.isdir(img):
        for f in os.listdir(img): os.remove(os.path.join(img, f))
    os.makedirs(img, exist_ok=True)
    for f in os.listdir(os.path.join(out, "sheet")): shutil.copy(os.path.join(out, "sheet", f), os.path.join(img, "ww_" + f))


def build_sheet(out):
    copy_images(out, STEM)
    st = json.load(open(os.path.join(out, "stats.json")))
    rel = STEM + "_img/ww_"
    rows = []
    for iid, sea, colour, ripple, film, g in items():
        s = st[iid]["stats"]
        if iid.startswith("film_"):
            label, effect = FILMS[film]["label"], FILMS[film]["effect"]
        elif iid.startswith("ripple_"):
            label, effect = RIPPLES[ripple]
        else:
            label = f"{SEA_LABEL[sea]}: {COLOUR_LABEL[colour]} ({st[iid]['base']} / {st[iid]['accent']})"
            effect = ("New face texture for this sea's RUT twin (and, once installed, the RM_ sea itself, which borrows "
                      "vanilla Ocean today). Texture only." if colour != "row" else
                      "The colour the RUT twin already carries. The RM_ sea still draws vanilla Ocean until a face is installed.")
        rows.append({"id": iid, "label": label, "group": g, "effect": effect, "thumb": rel + f"{iid}.jpg",
                     "prefill": PREFILL.get(iid, "pick" if colour == "row" else "maybe"),
                     "views": [WF._view(rel + f"{iid}_file.png", FILE_CAP, 2 * N, 2 * N),
                               WF._view(rel + f"{iid}_close.jpg", CLOSE_CAP, *ZOOMS["close"][2]),
                               WF._view(rel + f"{iid}_mid.jpg", MID_CAP, *ZOOMS["mid"][2]),
                               WF._view(rel + f"{iid}_far.jpg", FAR_CAP, *ZOOMS["far"][2])],
                     "meta": {"face mean RGB": ",".join(map(str, s["mean"])), "value": str(s["val"]), "sd": str(s["sd"]),
                              "films": film, "ripple": ripple},
                     "trueSize": {"none": "a world face has no in-game size; the file is shown 1:1, tiled 2x2, plus close/mid/far zoom"}})
    brief = (
        "<p><b>You, 2026-10-24:</b> <i>\"Especially important is to get the water right too, then the sea floors on their own "
        "layers.\"</i> This sheet is the first stab at the water: the colour and the ripple of each sea's face, and the two "
        "depth films the mod lays over every sea.</p>"
        "<p><b>How the sea is drawn in game.</b> The ocean shader cannot take depth from the texture, so depth comes from two "
        "films: a pale one along the coast and a dark one that rises away from it. Group 1 is those films (one setting for every "
        "sea). Group 2 is the ripple drawn into the face (one style for every sea). Group 3 is each sea's colour.</p>"
        "<p><b>These are offline renders, not the game</b>, built from the same inputs: the face is the very file that would be "
        "installed, and the films are rebuilt from the mod's own mesh and numbers. Not shown: the planet's sun lighting, the "
        "game's large-scale variation texture (a stand-in is used), and the true face scale, which is still unmeasured "
        "(assumed ~3 tiles per face). The coast is the Dune Sea in every picture so only the water changes. Click any picture to "
        "open it alone at 1:1 (browser zoom 100%, Ctrl+0).</p>"
        "<p>Pick per group: <b>Pick</b> = this one, <b>Maybe</b> = try it live too, <b>No</b> = drop. "
        "Program: <code>design/Jawa/worldbuilding/world_look_program_2026-10-24.md</code>.</p>")
    cfg = {"sheetId": STEM, "title": "World water: films, ripple, colour per sea",
           "subtitle": "2026-10-24 · first stab · WORLD_WATER_REDRAW_SEAS_THAT_READ_DEEP",
           "briefHtml": brief,
           "criterion": "The prefill is the agent's lean from looking at every render: does the sea read as deep water, open to shallow, at all three zooms, without sparkle.",
           "invented": ["The colour options (lighter/clearer, darker/richer) are the agent's shifts of each sea's existing colour row.",
                        "The wider-shelf film numbers are the agent's proposal; the installed numbers are read from RM_WorldLook.",
                        "The coast layout, the islands and the Dune Sea land are a test scene, not a real place on the planet."],
           "posture": {"mode": "whitelist", "explain": "Only rows marked Pick are built. Maybe = try live alongside the pick. No / blank = not built."},
           "options": [{"key": "pick", "label": "Pick", "hotkey": "1", "color": "#5ac37f", "counts": "in"},
                       {"key": "maybe", "label": "Maybe", "hotkey": "2", "color": "#d6b84a", "counts": "in"},
                       {"key": "no", "label": "No", "hotkey": "3", "color": "#e06c6c", "counts": "out"}],
           "groupLabel": "group", "media": False, "trueSize": "optional",
           "decisionsFile": STEM + ".decisions.json", "decisionsPath": "", "sheetPath": ""}
    write_sheet(STEM, cfg, rows)


def write_sheet(stem, cfg, rows):
    """the review-sheets template with CONFIG + ITEMS + the 1:1 view hooks, declared non-art; never overwrites his picks."""
    import nonart_sheet
    tdir = os.path.join(BW.REPO, "Transient")
    tpl = open(os.path.expanduser("~/.claude/skills/review-sheets/assets/sheet_template.html")).read()
    tpl = re.sub(r'(<script id="CONFIG" type="application/json">)(.*?)(</script>)',
                 lambda m: m.group(1) + "\n" + json.dumps(cfg, indent=1).replace("</", "<\\/") + "\n" + m.group(3), tpl, count=1, flags=re.S)
    tpl = re.sub(r'(<script id="ITEMS" type="application/json">)(.*?)(</script>)',
                 lambda m: m.group(1) + "\n" + json.dumps(rows, indent=1).replace("</", "<\\/") + "\n" + m.group(3), tpl, count=1, flags=re.S)
    tpl = tpl.replace("</head>", WF.RENDER_CSS + "\n</head>", 1)
    tpl = tpl.replace('<script>\n"use strict";', '<script id="RENDER">' + WF.RENDER_JS + '</script>\n<script>\n"use strict";', 1)
    assert 'id="RENDER">' in tpl and 'id="WFVIEWS"' in tpl, "template changed: RENDER/CSS hook not inserted"
    html = os.path.join(tdir, stem + ".html")
    open(html, "w").write(nonart_sheet.declare(tpl))
    dec = os.path.join(tdir, stem + ".decisions.json")
    if not os.path.exists(dec):          # never overwrite his picks
        json.dump({"sheetId": stem, "posture": "whitelist", "criterion": cfg["criterion"],
                   "reviewStatus": {"state": "prefill", "by": None, "at": None, "evidence": "agent variations; no human has ruled"},
                   "decisions": {r["id"]: {"decision": "", "prefill": r["prefill"], "note": ""} for r in rows}},
                  open(dec, "w"), indent=2, sort_keys=True)
    print("SHEET", html); print("DECISIONS", dec)


# ================================================================ round 2 (owner, 2026-10-24, on the round-1 sheet)
# "Grey Sea: lighter and clearer chosen. Twilight Sea: Darker and Richer (but see note below). The Scald: Today's colour
# row. The Chill should have no waves and be ominously dark compared to other bodies. The Twilight Sea has this concept of
# a stained glass window-like layer of life growing just below it's surface everywhere, so adding subtle large patches of
# beautiful primary colors in organic shapes would be welcome and unique too."
# His round-1 decisions file carried no clicks, so films and ripple stay at that sheet's prefills (shelf, wavelets) and the
# lake at its prefill (today's row) until he says otherwise.
STEM2 = "world_water_review_r2_2026-10-24"
CHOSEN = {"GreySea": "clear", "TwilightSea": "deep", "Scald": "row", "MineralWater": "row"}
FILM2 = "shelf"
GLASS_PERIOD = 40.0                      # tiles per repeat of the glass texture (the swirl layer's world-planar UV scale)
PRIMARY = {"crimson": (222, 42, 74), "gold": (246, 192, 52), "azure": (40, 168, 246)}   # azure, not cobalt: cobalt vanished into the blue sea (prereview)
SINK = 0.22                              # share of the sea's own colour mixed into a glass colour: lit from under water


def _ss(x): x = np.clip(x, 0, 1); return x * x * (3 - 2 * x)


def _palette(sea_hex):
    b = BW.H(sea_hex)
    return [np.array(c, float) * (1 - SINK) + b * SINK for c in PRIMARY.values()]


def glass_tex(style, sea_hex, seed=7, scale=1, info=None, rim=1.0):
    """(rgb N x N x 3, alpha N x N) of a seamless stained-glass layer; one texture repeat covers GLASS_PERIOD tiles
    (12.8 px per tile at N=512), so a 'large' patch of 6-15 tiles is 75-190 px.
    scale: linear shrink of the panes (round 3: 2 = a quarter of the area, four times as many; every length - cell size,
    warp, rim, glow - divides by it, so the shape language stays the r2 one). scale=1 is byte-identical to round 2.
    rim: the soft rim's width divides by scale * rim (rim > 1 = a thinner rim, so more of a small pane shows).
    info: if a dict, gets 'idx' (pane id per px) and 'on' (lit per pane) for pane_metrics()."""
    pal = _palette(sea_hex); rng = np.random.default_rng(seed)
    rgb = np.zeros((N, N, 3)); alpha = np.zeros((N, N))
    life = np.clip(0.80 + 0.20 * z(BW.gblur(band(4 * scale, 10 * scale, seed + 9), 1.5)), 0.5, 1.2)    # slow glow inside a patch
    if style == "bloom":                 # three independent slow fields, one per colour; a patch where its field leads
        f = np.stack([z(warped(1, 3, seed + 10 * k, 14)) for k in range(3)])
        lead = f.argmax(0); top = f.max(0)
        a = 0.24 * _ss((top - 0.85) / 0.75)
        for k in range(3): rgb[lead == k] = pal[k]
        rgb = np.stack([BW.gblur(rgb[..., c], 3) for c in range(3)], -1)              # colour meets colour softly
        return rgb, np.clip(a * life, 0, 1)
    # panes / jewel: Voronoi on the torus, its coordinates warped so cells grow organic, not polygonal
    k = 6 * scale; cell = N / k
    seeds = np.array([((i + rng.uniform(0.15, 0.85)) * cell, (j + rng.uniform(0.15, 0.85)) * cell) for i in range(k) for j in range(k)])
    yy, xx = np.mgrid[0:N, 0:N].astype(float)
    wx = xx + 26 / scale * band(2 * scale, 4 * scale, seed + 3); wy = yy + 26 / scale * band(2 * scale, 4 * scale, seed + 4)
    d1 = np.full((N, N), np.inf); d2 = np.full((N, N), np.inf); idx = np.zeros((N, N), int)
    for n, (sx, sy) in enumerate(seeds):
        dx = np.abs(wx - sx) % N; dx = np.minimum(dx, N - dx); dy = np.abs(wy - sy) % N; dy = np.minimum(dy, N - dy)
        d = np.sqrt(dx * dx + dy * dy)
        closer = d < d1
        d2 = np.where(closer, d1, np.minimum(d2, d)); idx = np.where(closer, n, idx); d1 = np.where(closer, d, d1)
    edge = (d2 - d1) / 2                                                               # px to the cell border
    # (A "leaded" style - panes nearly everywhere with faint dark seams - was dropped at prereview 2026-10-24: at far zoom
    #  the seams read as cracked mud, not a window.)
    present = {"panes": 0.55, "jewel": 0.40}[style]
    on = rng.random(len(seeds)) < present
    colour = rng.permutation(np.arange(len(seeds)) % 3)                               # each primary gets a third
    for n in range(len(seeds)): rgb[idx == n] = pal[colour[n]]
    if style == "panes":                 # even panes, a soft rim
        a = np.where(on[idx], 0.28 * _ss((edge - 3 / (scale * rim)) / (14 / (scale * rim))), 0.0) * life
    else:                                # jewel: fewer, stronger, brightest at the heart, as if lit from below
        a = np.where(on[idx], 0.38 * _ss((edge - 2 / (scale * rim)) / (34 / (scale * rim))), 0.0) * life
    if info is not None: info.update(idx=idx, on=on)
    return rgb, np.clip(a, 0, 1)


def pane_metrics(a, info):
    """pane sizes in HEX CELLS. The render's world-planar unit (Scene.X/Y, GLASS_PERIOD) is one hex centre-to-centre
    distance (hexw = sqrt(3) x circumradius), and a hex covers sqrt(3)/2 of hexw^2, so one hex = 0.866 x (N/GLASS_PERIOD)^2 px.
    cell = the whole Voronoi pane; lit = the part of a lit pane at >= half its own peak alpha (what the eye calls the pane)."""
    px_per_hex = (N / GLASS_PERIOD) ** 2 * SQ3 / 2
    idx, on = info["idx"], info["on"]
    cells = np.bincount(idx.ravel(), minlength=len(on)) / px_per_hex
    lit = []
    for n in np.flatnonzero(on):
        m = idx == n; pk = a[m].max()
        if pk > 0: lit.append(float((a[m] >= 0.5 * pk).sum()) / px_per_hex)
    if not lit: raise ValueError("pane_metrics: no lit pane in this texture (seed/present gave none)")
    lit = np.array(lit); srt = np.sort(lit); cum = np.cumsum(srt) / srt.sum()
    aw = float(srt[np.searchsorted(cum, 0.5)])   # half the lit glass sits in panes at least this big: what the eye sees
    return {"panes per repeat": int(len(on)), "lit panes": int(on.sum()), "lit share": round(float(on.mean()), 2),
            "pane cell area (hex), mean": round(float(cells.mean()), 1),
            "lit pane visible area (hex), median": round(float(np.median(lit)), 1),
            "lit pane visible area (hex), p10-p90": f"{np.percentile(lit, 10):.1f}-{np.percentile(lit, 90):.1f}",
            "lit pane visible area (hex), area-weighted median": round(aw, 1)}


# (Glass painted INTO the face, under the ripple - the data-only route - was dropped at prereview 2026-10-24: a face
#  spans ~3 tiles, so its patches were small and repeated every face, a camouflage speckle at far zoom.)


CHILL_LEVELS = {   # face mean value (HSV V x 255) a still Chill face is built to; today's Chill row is ~93
    "dusk": 50, "night": 34, "abyss": 22}


def make_still(key, value, sat=0.42, seed=5):
    """no waves: the sea's hue at a set darkness, with only a very slow, very faint swell of tone (no streaks, no blots)."""
    base = BW.F[key][0]
    r, g, b = (BW.H(base) / 255).tolist(); h, _s, _v = colorsys.rgb_to_hsv(r, g, b)
    col = np.array(colorsys.hsv_to_rgb(h, sat, value / 255)) * 255
    slow = z(BW.gblur(band(1, 3, seed), 4))
    img = col[None, None, :] * (1 + 0.035 * slow[..., None])
    return np.clip(np.rint(img), 0, 255).astype(np.uint8), ("#%02x%02x%02x" % tuple(int(round(c)) for c in col),) * 2


def still_check(st):
    """the water rule with the owner's Chill exception: darker than the 60 floor and no ripple are what he asked for."""
    bad = []
    if st["seam"] > 2 * st["nbr"] + 0.5: bad.append(f"seam {st['seam']}")
    if st["sat"] > 60: bad.append(f"sat {st['sat']}%")
    if not 12 <= st["val"] <= 60: bad.append(f"val {st['val']} not in 12-60 (Chill exception)")
    if not (st["mean"][2] > st["mean"][0]): bad.append("water not cool")
    return bad


GLASS = {
    "bloom":  ("Stained glass, bloom: soft organic patches 6-15 tiles, colour meeting colour softly",
               "A swirl-layer texture over Twilight Sea tiles (World/RM_Swirls/TwilightGlass, one repeat per ~40 tiles). Texture + one entry in the swirl list."),
    "panes":  ("Stained glass, panes: organic panes ~7 tiles, about half of them lit, plain sea between",
               "Same swirl-layer route as bloom, a different texture."),
    "jewel":  ("Stained glass, jewel: fewer panes, stronger, brightest at the heart as if lit from below",
               "Same swirl-layer route, a different texture."),
}
REF_NOTE = {"GreySea": "Grey Sea: lighter and clearer (your pick)", "TwilightSea": "Twilight Sea: darker and richer (your pick), no glass",
            "Scald": "The Scald: today's colour row (your pick)", "MineralWater": "Mineral water (lake): today's colour row (prefill; you did not rule it)"}


def items2():
    """(id, group, kind, arg) for every row of the round-2 sheet."""
    rows = [(f"TwilightSea_glass_{g}", "1. Twilight Sea: darker and richer, stained glass below the surface", "glass", g) for g in GLASS]
    rows += [(f"Chill_still_{lv}", "2. The Chill: no waves, ominously dark (each row ends with every sea side by side)", "still", lv) for lv in CHILL_LEVELS]
    rows += [("Chill_still_night_nofilm", "2. The Chill: no waves, ominously dark (each row ends with every sea side by side)", "still_nofilm", "night")]
    rows += [(f"{s}_{c}_ref", "3. Already chosen, shown for reference (same films)", "ref", s) for s, c in CHOSEN.items()]
    return rows


def _water_value(img, sc):
    """mean HSV value (0-255) of the water pixels of a rendered frame (after films and glass, before the box resize)."""
    a = np.asarray(img, np.float32)
    m = ~np.asarray(Image.fromarray((sc.pix_land * 255).astype(np.uint8)).resize(img.size, Image.BOX), bool)
    return int(round(float(a[m].max(1).mean()))) if m.any() else -1


def gen2(out):
    sh = os.path.join(out, "sheet"); os.makedirs(sh, exist_ok=True)
    land = BW.make(LAND)
    scenes = {zm: Scene(zm) for zm in ZOOMS}
    tw_base = hsv_shift(BW.F["TwilightSea"][0], *COLOURS["deep"])
    stats, water_val = {}, {}
    for iid, _g, kind, arg in items2():
        glass, films_on = None, True
        if kind == "glass":
            face, (base, sec) = make_water("TwilightSea", "deep", "wavelets")
            rgb, a = glass_tex(arg, tw_base)
            glass = (rgb.astype(np.float32), a.astype(np.float32), GLASS_PERIOD)
            Image.fromarray(np.dstack([np.clip(np.rint(rgb), 0, 255), np.rint(a * 255)]).astype(np.uint8), "RGBA").save(os.path.join(sh, f"{iid}_glass.png"))
            bad = BW.verdict("TwilightSea", BW.stats(face), face.shape)
        elif kind.startswith("still"):
            face, (base, sec) = make_still("Chill", CHILL_LEVELS[arg]); films_on = kind == "still"
            bad = still_check(BW.stats(face))
        else:
            face, (base, sec) = make_water(arg, CHOSEN[arg], "wavelets")
            bad = BW.verdict(arg, BW.stats(face), face.shape)
        st = BW.stats(face)
        stats[iid] = {"stats": st, "check": bad, "base": base, "accent": sec}
        WF.tiled(face).save(os.path.join(sh, f"{iid}_file.png"))
        for zm, sc in scenes.items():
            im = sc.render(face, land, FILM2, glass=glass, films_on_sea=films_on)
            im.save(os.path.join(sh, f"{iid}_{zm}.jpg"), **JPG)
            if zm == "far": water_val[iid] = _water_value(im, sc)
        Image.open(os.path.join(sh, f"{iid}_mid.jpg")).crop((80, 120, 500, 400)).save(os.path.join(sh, f"{iid}.jpg"), **JPG)
        print(iid, st["mean"], "sd", st["sd"], "val", st["val"], "water-after-films", water_val[iid], "CHECK " + "; ".join(bad) if bad else "ok")
    for k in stats: stats[k]["water_value_far"] = water_val[k]
    # the lineup: every sea's far render side by side, 1:1 crops of open water, the chosen looks + one Chill level
    refs = [f"{s}_{c}_ref" for s, c in CHOSEN.items()]
    names = {f"{s}_{c}_ref": SEA_LABEL[s] for s, c in CHOSEN.items()}
    box = (40, 150, 40 + 270, 150 + 420)                     # open water + a coast strip, left of the mainland
    for iid, _g, kind, arg in items2():
        if not kind.startswith("still"): continue
        panels = [WF.caption(Image.open(os.path.join(sh, f"{r}_far.jpg")).crop(box), f"{names[r].replace(' (lake)', '')} {water_val[r]}", 14) for r in refs]
        panels.append(WF.caption(Image.open(os.path.join(sh, f"{iid}_far.jpg")).crop(box), f"The Chill {water_val[iid]}", 14))
        WF.hstack(panels).save(os.path.join(sh, f"{iid}_lineup.jpg"), **JPG)
    json.dump(stats, open(os.path.join(out, "stats.json"), "w"), indent=1)
    # agent's own look: contact strips of 1:1 crops (never resized), <= 1500 px wide
    pr = os.path.join(out, "prereview"); os.makedirs(pr, exist_ok=True)
    groups = {}
    for iid, g, _k, _a in items2(): groups.setdefault(g[0], []).append(iid)
    for g, ids in groups.items():
        for zm, (x, y) in (("close", (300, 120)), ("mid", (60, 60)), ("far", (60, 100))):
            strip = WF.hstack([WF.caption(Image.open(os.path.join(sh, f"{i}_{zm}.jpg")).crop((x, y, x + 340, y + 330)), f"{i[:30]} {zm}", 13) for i in ids])
            strip.save(os.path.join(pr, f"g{g}_{zm}.jpg"), **JPG)


LINEUP_CAP = ("every sea side by side at far zoom: 1:1 crops of the far renders above (open water and a strip of coast); "
              "the number is the mean brightness (HSV value, 0-255) of the water after the films, unlit")


def build_sheet2(out):
    copy_images(out, STEM2)
    st = json.load(open(os.path.join(out, "stats.json")))
    rel = STEM2 + "_img/ww_"
    rows = []
    for iid, g, kind, arg in items2():
        s = st[iid]["stats"]; wv = st[iid]["water_value_far"]
        views = [WF._view(rel + f"{iid}_file.png", FILE_CAP, 2 * N, 2 * N),
                 WF._view(rel + f"{iid}_close.jpg", CLOSE_CAP, *ZOOMS["close"][2]),
                 WF._view(rel + f"{iid}_mid.jpg", MID_CAP, *ZOOMS["mid"][2]),
                 WF._view(rel + f"{iid}_far.jpg", FAR_CAP, *ZOOMS["far"][2])]
        if kind == "glass":
            label, effect = GLASS[arg]
            views.insert(1, WF._view(rel + f"{iid}_glass.png", "the glass layer's own texture (RGBA, 1:1; one repeat = ~40 tiles); the face under it is the darker-and-richer Twilight face", N, N))
            prefill = "maybe"
        elif kind.startswith("still"):
            lv = CHILL_LEVELS[arg]
            label = (f"The Chill, still water, '{arg}' (face value {lv}; today's Chill row is ~93)"
                     + (" with the sea films switched OFF on The Chill only" if kind == "still_nofilm" else ""))
            effect = ("A new still face for The Chill (texture only: RM_TheChill draws Jawa_SickWater today; its RUT twin draws the Chill face)."
                      + (" Plus: the depth films would have to skip The Chill, which they cannot today (one film setting for every sea): C#." if kind == "still_nofilm"
                         else " The global films still lighten it near coasts and pull it toward the deep-film colour offshore."))
            views.append(WF._view(rel + f"{iid}_lineup.jpg", LINEUP_CAP, 5 * 270 + 4 * 8, 420 + 26))
            prefill = "pick" if arg == "night" and kind == "still" else "maybe"
        else:
            label = REF_NOTE[arg]
            effect = "Reference only: the look already chosen, with the working films. Mark No if it is wrong."
            prefill = "pick"
        rows.append({"id": iid, "label": label, "group": g, "effect": effect, "thumb": rel + f"{iid}.jpg", "prefill": prefill,
                     "views": views,
                     "meta": {"face mean RGB": ",".join(map(str, s["mean"])), "face value": str(s["val"]), "sd": str(s["sd"]),
                              "water value after films (far)": str(wv), "films": FILM2 + ("" if kind != "still_nofilm" else " (off on this sea)"),
                              "ripple": "none (still)" if kind.startswith("still") else "wavelets"},
                     "trueSize": {"none": "a world face has no in-game size; the file is shown 1:1, tiled 2x2, plus close/mid/far zoom"}})
    brief = (
        "<p><b>You, 2026-10-24:</b> <i>\"Grey Sea: lighter and clearer chosen. Twilight Sea: Darker and Richer (but see note below). "
        "The Scald: Today's colour row. The Chill should have no waves and be ominously dark compared to other bodies. The Twilight "
        "Sea has this concept of a stained glass window-like layer of life growing just below it's surface everywhere, so adding "
        "subtle large patches of beautiful primary colors in organic shapes would be welcome and unique too.\"</i></p>"
        "<p><b>Working defaults (not your picks):</b> your round-1 file had no clicks, so the films are that sheet's lean "
        "(<i>wider shelf</i>), the ripple is today's wavelets, and the lake keeps today's colour. Group 3 shows them; mark No to change.</p>"
        "<p><b>Group 1, the glass.</b> Three ways to lay large primary-colour patches across the Twilight Sea using the mod's existing "
        "biome-wide overlay (the same layer that puts the swirls in the Abyss; drawn over the sea films, under hills and rivers). It "
        "can be truly large (one texture repeat covers ~40 tiles) and lies over the ripple at low strength, so the ripple still shows "
        "through. (Painting the glass into the face itself was tried and dropped: a face spans ~3 tiles, so the patches came out small "
        "and repeating, a speckle at far zoom.) Colours are crimson, gold and azure, each mixed a fifth toward the sea's own blue, as if "
        "lit from below the surface.</p>"
        "<p><b>Group 2, The Chill.</b> No ripple at all, three darknesses, plus one with the depth films kept off The Chill. The last "
        "picture in each row puts every sea side by side with its brightness number, so 'darker than all the others' can be checked.</p>"
        "<p><b>Offline renders, not the game</b> (same inputs: the face file, the films rebuilt from the mod's own mesh and numbers, "
        "the overlay laid world-planar). Not shown: the planet's sun lighting, the true face scale (unmeasured; ~3 tiles per face "
        "assumed), the true tile count per glass repeat. Click any picture to open it alone at 1:1 (browser zoom 100%, Ctrl+0).</p>")
    cfg = {"sheetId": STEM2, "title": "World water, round 2: Twilight stained glass, a still dark Chill",
           "subtitle": "2026-10-24 · round 2 · WORLD_WATER_REDRAW_SEAS_THAT_READ_DEEP",
           "briefHtml": brief,
           "criterion": "The prefill is the agent's lean after looking at every picture at every zoom: glass reads as large soft colour under water without speckle; The Chill reads darkest of all seas.",
           "invented": ["The glass layouts, the three primaries and their strength are the agent's.",
                        "The three Chill darknesses and the no-film variant are the agent's.",
                        "The coast layout, islands and Dune Sea land are a test scene."],
           "posture": {"mode": "whitelist", "explain": "Only rows marked Pick are built. Maybe = try live alongside the pick. No / blank = not built."},
           "options": [{"key": "pick", "label": "Pick", "hotkey": "1", "color": "#5ac37f", "counts": "in"},
                       {"key": "maybe", "label": "Maybe", "hotkey": "2", "color": "#d6b84a", "counts": "in"},
                       {"key": "no", "label": "No", "hotkey": "3", "color": "#e06c6c", "counts": "out"}],
           "groupLabel": "group", "media": False, "trueSize": "optional",
           "decisionsFile": STEM2 + ".decisions.json", "decisionsPath": "", "sheetPath": ""}
    write_sheet(STEM2, cfg, rows)


# ================================================================ round 3 (owner, 2026-10-24 ~09:50 PDT, on the r2 sheet)
# "Stained glass, panes: organic panes ~7 tiles, about half of them lit, plain sea between is good, but the panels need to
# be 1/4th the size and x4 in number. They should be roughly 4-5 cells in area. The Chill, still water, 'abyss' (face
# value 22; today's Chill row is ~93). Others confirm. [...] Grey sea looking bluish is ok."
STEM3 = "world_water_review_r3_2026-10-24"
PANES3 = dict(scale=2, rim=1.15, seed=7)   # 144 panes per 40-hex repeat; lit-pane median 4.5 hexes (r2: 24.7) - pane_metrics
PANES3S = dict(scale=3, rim=1.0, seed=5)   # alternative: 324 panes, seed 5 = 53% lit (seed 7 lit 60%); area-weighted lit pane ~3 hexes (v3 reads ~7.5 by area)
CONFIRMED = {"GreySea": "clear", "TwilightSea": "deep", "Scald": "row", "MineralWater": "row"}   # "Others confirm"


def items3():
    """(id, group, kind, arg): r2 panes as 'before', the quartered v3, and the picked Chill abyss with and without films."""
    g1, g2 = "1. Twilight Sea stained glass: panes, before and after", "2. The Chill: still 'abyss' (your pick)"
    return [("TwilightSea_glass_panes_r2", g1, "glass", dict(scale=1, rim=1.0, seed=7)),
            ("TwilightSea_glass_panes_v3", g1, "glass", PANES3),
            ("TwilightSea_glass_panes_v3_small", g1, "glass", PANES3S),
            ("Chill_abyss", g2, "still", "abyss"),
            ("Chill_abyss_nofilm", g2, "still_nofilm", "abyss")]


def export_faces(out):
    """the 512 px faces to install (not tiled): the four confirmed seas + the Chill abyss + the v3 glass texture."""
    fd = os.path.join(out, "faces"); os.makedirs(fd, exist_ok=True)
    for s, c in CONFIRMED.items():
        face, _ = make_water(s, c, "wavelets")
        Image.fromarray(face).save(os.path.join(fd, f"{s}_{c}.png"))
    face, _ = make_still("Chill", CHILL_LEVELS["abyss"])
    Image.fromarray(face).save(os.path.join(fd, "Chill_abyss.png"))
    rgb, a = glass_tex("panes", hsv_shift(BW.F["TwilightSea"][0], *COLOURS["deep"]), **PANES3)
    Image.fromarray(np.dstack([np.clip(np.rint(rgb), 0, 255), np.rint(a * 255)]).astype(np.uint8), "RGBA").save(os.path.join(fd, "TwilightGlass_panes_v3.png"))
    print("FACES", fd, sorted(os.listdir(fd)))


def gen3(out):
    sh = os.path.join(out, "sheet"); os.makedirs(sh, exist_ok=True)
    land = BW.make(LAND)
    scenes = {zm: Scene(zm) for zm in ZOOMS}
    tw_base = hsv_shift(BW.F["TwilightSea"][0], *COLOURS["deep"])
    stats, water_val = {}, {}
    refs = [(f"{s}_{c}_ref", "ref", s) for s, c in CONFIRMED.items()]
    for iid, _g, kind, arg in [(i, None, k, a) for i, _g, k, a in items3()] + [(i, None, k, a) for i, k, a in refs]:
        glass, films_on, extra = None, True, {}
        if kind == "glass":
            face, (base, sec) = make_water("TwilightSea", "deep", "wavelets")
            info = {}
            rgb, a = glass_tex("panes", tw_base, info=info, **arg)
            extra = pane_metrics(a, info)
            glass = (rgb.astype(np.float32), a.astype(np.float32), GLASS_PERIOD)
            Image.fromarray(np.dstack([np.clip(np.rint(rgb), 0, 255), np.rint(a * 255)]).astype(np.uint8), "RGBA").save(os.path.join(sh, f"{iid}_glass.png"))
            bad = BW.verdict("TwilightSea", BW.stats(face), face.shape)
        elif kind.startswith("still"):
            face, (base, sec) = make_still("Chill", CHILL_LEVELS[arg]); films_on = kind == "still"
            bad = still_check(BW.stats(face))
        else:
            face, (base, sec) = make_water(arg, CONFIRMED[arg], "wavelets")
            bad = BW.verdict(arg, BW.stats(face), face.shape)
        st = BW.stats(face)
        stats[iid] = {"stats": st, "check": bad, "base": base, "accent": sec, "panes": extra}
        if kind != "ref": WF.tiled(face).save(os.path.join(sh, f"{iid}_file.png"))
        for zm, sc in scenes.items():
            if kind == "ref" and zm != "far": continue
            im = sc.render(face, land, FILM2, glass=glass, films_on_sea=films_on)
            im.save(os.path.join(sh, f"{iid}_{zm}.jpg"), **JPG)
            if zm == "far": water_val[iid] = _water_value(im, sc)
        if kind != "ref":
            Image.open(os.path.join(sh, f"{iid}_mid.jpg")).crop((80, 120, 500, 400)).save(os.path.join(sh, f"{iid}.jpg"), **JPG)
        print(iid, st["mean"], "val", st["val"], "water-after-films", water_val[iid], extra or "", "CHECK " + "; ".join(bad) if bad else "ok")
    for k in stats: stats[k]["water_value_far"] = water_val[k]
    names = {r: SEA_LABEL[s] for r, _k, s in refs}
    box = (40, 150, 40 + 270, 150 + 420)
    for iid, _g, kind, _a in items3():
        if not kind.startswith("still"): continue
        panels = [WF.caption(Image.open(os.path.join(sh, f"{r}_far.jpg")).crop(box), f"{names[r].replace(' (lake)', '')} {water_val[r]}", 14) for r, _k, _s in refs]
        panels.append(WF.caption(Image.open(os.path.join(sh, f"{iid}_far.jpg")).crop(box), f"The Chill {water_val[iid]}", 14))
        WF.hstack(panels).save(os.path.join(sh, f"{iid}_lineup.jpg"), **JPG)
    for r, _k, _s in refs: os.remove(os.path.join(sh, f"{r}_far.jpg"))        # lineup inputs only, not sheet rows
    json.dump(stats, open(os.path.join(out, "stats.json"), "w"), indent=1)
    pr = os.path.join(out, "prereview"); os.makedirs(pr, exist_ok=True)
    ids = [i for i, *_ in items3()]
    for zm, (x, y) in (("close", (300, 120)), ("mid", (60, 60)), ("far", (60, 100))):
        WF.hstack([WF.caption(Image.open(os.path.join(sh, f"{i}_{zm}.jpg")).crop((x, y, x + 340, y + 330)), f"{i[:30]} {zm}", 13) for i in ids]).save(
            os.path.join(pr, f"r3_{zm}.jpg"), **JPG)
    export_faces(out)


def build_sheet3(out):
    copy_images(out, STEM3)
    st = json.load(open(os.path.join(out, "stats.json")))
    rel = STEM3 + "_img/ww_"
    rows = []
    for iid, g, kind, arg in items3():
        s = st[iid]["stats"]; wv = st[iid]["water_value_far"]; pm = st[iid]["panes"]
        views = [WF._view(rel + f"{iid}_file.png", FILE_CAP, 2 * N, 2 * N),
                 WF._view(rel + f"{iid}_close.jpg", CLOSE_CAP, *ZOOMS["close"][2]),
                 WF._view(rel + f"{iid}_mid.jpg", MID_CAP, *ZOOMS["mid"][2]),
                 WF._view(rel + f"{iid}_far.jpg", FAR_CAP, *ZOOMS["far"][2])]
        meta = {"face value": str(s["val"]), "water value after films (far)": str(wv),
                "films": FILM2 + (" (off on this sea)" if kind == "still_nofilm" else ""),
                "ripple": "none (still)" if kind.startswith("still") else "wavelets"}
        if kind == "glass":
            v3 = arg["scale"] > 1
            med = pm["lit pane visible area (hex), median"]
            label = {1: "Stained glass, panes as on round 2 (before; lit pane ~%s hexes)",
                     2: "Stained glass, panes v3: a quarter the size, four times as many (lit pane ~%s hexes)",
                     3: "Stained glass, panes v3 smaller: a ninth the size, nine times as many (lit pane ~%s hexes)"}[arg["scale"]] % med
            effect = {1: "Shown only so the change is visible. Not built.",
                      2: "Your numbers taken literally: 1/4 the size, x4 in number; the typical lit pane is 4-5 hexes, the big ones "
                         "that catch the eye are 7-10. Same swirl-layer route, a new texture; colours, strength and the half-lit rule unchanged.",
                      3: "In case the panes above still read too big: here even the big lit panes are ~3-5 hexes. Busier at far zoom."}[arg["scale"]]
            views.insert(1, WF._view(rel + f"{iid}_glass.png", "the glass layer's own texture (RGBA, 1:1; one repeat = 40 hexes across)", N, N))
            meta.update({k: str(v) for k, v in pm.items()})
            prefill = {1: "no", 2: "pick", 3: "maybe"}[arg["scale"]]
        else:
            label = ("The Chill, still water, 'abyss' (face value 22), with the sea films as every other sea has them" if kind == "still" else
                     "The Chill, still water, 'abyss' (face value 22), sea films switched OFF on The Chill only")
            effect = ("Your pick as you saw it. Texture only: installs the still face on The Chill and its twin." if kind == "still" else
                      "Same face; the films (pale coast band, dark offshore film) would skip The Chill. Needs a small code change "
                      "(SEA_FILMS_TUNE_PER_SEA_CHILL_UNLIT). Without it the films lift the face (see the number) and leave a dark ring round islands.")
            views.append(WF._view(rel + f"{iid}_lineup.jpg", LINEUP_CAP, 5 * 270 + 4 * 8, 420 + 26))
            prefill = "pick" if kind == "still" else "maybe"
        rows.append({"id": iid, "label": label, "group": g, "effect": effect, "thumb": rel + f"{iid}.jpg", "prefill": prefill,
                     "views": views, "meta": meta,
                     "trueSize": {"none": "a world face has no in-game size; the file is shown 1:1, tiled 2x2, plus close/mid/far zoom"}})
    vs = st["TwilightSea_glass_panes_v3_small"]["panes"]
    v3 = st["TwilightSea_glass_panes_v3"]["panes"]; r2 = st["TwilightSea_glass_panes_r2"]["panes"]
    brief = (
        "<p><b>You, 2026-10-24:</b> <i>\"Stained glass, panes: organic panes ~7 tiles, about half of them lit, plain sea between "
        "is good, but the panels need to be 1/4th the size and x4 in number. They should be roughly 4-5 cells in area. The Chill, "
        "still water, 'abyss' (face value 22; today's Chill row is ~93). Others confirm.\"</i></p>"
        f"<p><b>Group 1.</b> The panes, before and after. Measured on the glass texture: round 2 had {r2['panes per repeat']} panes "
        f"per repeat, a lit pane showing ~{r2['lit pane visible area (hex), median']} hexes; v3 has {v3['panes per repeat']} "
        f"({v3['lit panes']} lit), a lit pane showing ~{v3['lit pane visible area (hex), median']} hexes (most between "
        f"{v3['lit pane visible area (hex), p10-p90']}); but half the lit glass sits in panes of "
        f"{v3['lit pane visible area (hex), area-weighted median']}+ hexes, so the eye reads them bigger. The smaller row "
        f"(v3 smaller) brings that to {vs['lit pane visible area (hex), area-weighted median']}. One repeat of the glass spans 40 hexes; a sea face spans ~3 (assumed).</p>"
        "<p><b>Group 2.</b> Your Chill pick as shown on round 2, and the same face with the depth films kept off The Chill. "
        "The last picture in each row puts every sea side by side with its brightness number.</p>"
        "<p><b>Installed on your word ('Others confirm'):</b> Grey Sea lighter and clearer, Twilight Sea darker and richer (both "
        "twins); The Scald and the lake keep today's colour. The wider-shelf films are a code default, ticketed. The Twilight glass "
        "and The Chill wait for this sheet.</p>"
        "<p><b>Offline renders, not the game</b> (same inputs as round 2). Not shown: the planet's sun lighting, the true face scale. "
        "Click any picture to open it alone at 1:1 (browser zoom 100%, Ctrl+0).</p>")
    cfg = {"sheetId": STEM3, "title": "World water, round 3: smaller panes, The Chill abyss",
           "subtitle": "2026-10-24 · round 3 · WORLD_WATER_REDRAW_SEAS_THAT_READ_DEEP",
           "briefHtml": brief,
           "criterion": "The prefill is the agent's lean: v3 panes match your numbers and read as glass, not speckle, at every zoom; the abyss is your pick.",
           "invented": ["The pane layout (seeded), its rim width and the 4.5-hex target inside your 4-5 are the agent's.",
                        "The coast layout, islands and Dune Sea land are a test scene."],
           "posture": {"mode": "whitelist", "explain": "Only rows marked Pick are built. Maybe = try live alongside the pick. No / blank = not built."},
           "options": [{"key": "pick", "label": "Pick", "hotkey": "1", "color": "#5ac37f", "counts": "in"},
                       {"key": "maybe", "label": "Maybe", "hotkey": "2", "color": "#d6b84a", "counts": "in"},
                       {"key": "no", "label": "No", "hotkey": "3", "color": "#e06c6c", "counts": "out"}],
           "groupLabel": "group", "media": False, "trueSize": "optional",
           "decisionsFile": STEM3 + ".decisions.json", "decisionsPath": "", "sheetPath": ""}
    write_sheet(STEM3, cfg, rows)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["gen", "sheet", "gen2", "sheet2", "gen3", "sheet3", "faces"])
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    out = a.out or os.path.join(os.path.dirname(BW.storage_root()), "worldwater_variants")
    if a.cmd in ("gen2", "sheet2") and not a.out: out += "_r2"
    if a.cmd in ("gen3", "sheet3", "faces") and not a.out: out += "_r3"
    if a.cmd == "gen3":
        gen3(out); print("OUT", out)
    elif a.cmd == "sheet3":
        build_sheet3(out)
    elif a.cmd == "faces":
        export_faces(out)
    elif a.cmd == "gen":
        gen(out); print("OUT", out)
    elif a.cmd == "gen2":
        gen2(out); print("OUT", out)
    elif a.cmd == "sheet2":
        build_sheet2(out)
    else:
        build_sheet(out)


if __name__ == "__main__":
    main()
