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

    def render(self, sea_face, land_face, film="today"):
        img = np.where(self.pix_land[..., None], land_face[self.v, self.u], sea_face[self.v, self.u]).astype(np.float32)
        img = img * (1 + 0.10 * self.macro[..., None])
        for col, al in self.films(film):                                           # shore (3502) then deep (3503)
            img = img * (1 - al[..., None]) + col[None, None, :] * al[..., None]
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


def build_sheet(out):
    import nonart_sheet                  # the non-art declaration, or serve_gated refuses the page
    tdir = os.path.join(BW.REPO, "Transient"); img = os.path.join(tdir, STEM + "_img")
    if os.path.isdir(img):
        for f in os.listdir(img): os.remove(os.path.join(img, f))
    os.makedirs(img, exist_ok=True)
    for f in os.listdir(os.path.join(out, "sheet")): shutil.copy(os.path.join(out, "sheet", f), os.path.join(img, "ww_" + f))
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
    tpl = open(os.path.expanduser("~/.claude/skills/review-sheets/assets/sheet_template.html")).read()
    tpl = re.sub(r'(<script id="CONFIG" type="application/json">)(.*?)(</script>)',
                 lambda m: m.group(1) + "\n" + json.dumps(cfg, indent=1).replace("</", "<\\/") + "\n" + m.group(3), tpl, count=1, flags=re.S)
    tpl = re.sub(r'(<script id="ITEMS" type="application/json">)(.*?)(</script>)',
                 lambda m: m.group(1) + "\n" + json.dumps(rows, indent=1).replace("</", "<\\/") + "\n" + m.group(3), tpl, count=1, flags=re.S)
    tpl = tpl.replace("</head>", WF.RENDER_CSS + "\n</head>", 1)
    tpl = tpl.replace('<script>\n"use strict";', '<script id="RENDER">' + WF.RENDER_JS + '</script>\n<script>\n"use strict";', 1)
    assert 'id="RENDER">' in tpl and 'id="WFVIEWS"' in tpl, "template changed: RENDER/CSS hook not inserted"
    html = os.path.join(tdir, STEM + ".html")
    open(html, "w").write(nonart_sheet.declare(tpl))
    dec = os.path.join(tdir, STEM + ".decisions.json")
    if not os.path.exists(dec):          # never overwrite his picks
        json.dump({"sheetId": STEM, "posture": "whitelist", "criterion": cfg["criterion"],
                   "reviewStatus": {"state": "prefill", "by": None, "at": None, "evidence": "agent variations; no human has ruled"},
                   "decisions": {r["id"]: {"decision": "", "prefill": r["prefill"], "note": ""} for r in rows}},
                  open(dec, "w"), indent=2, sort_keys=True)
    print("SHEET", html); print("DECISIONS", dec)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["gen", "sheet"])
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    out = a.out or os.path.join(os.path.dirname(BW.storage_root()), "worldwater_variants")
    if a.cmd == "gen":
        gen(out); print("OUT", out)
    else:
        build_sheet(out)


if __name__ == "__main__":
    main()
