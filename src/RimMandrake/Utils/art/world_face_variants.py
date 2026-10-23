#!/usr/bin/env python3
"""World-face VARIATIONS for the owner to choose between (WORLDMAP_FACES_DECIDE_SEPTEMBER_WAS_PRETTIER, owner card
2026-10-23: "Do a background deep dive for (3) [make our own face textures] right now ... inspire yourself by World Map
Enhanced's approaches and make variations to try out, then a sheet to select for the user. We definitely should own our own
world art").  Design and findings: design/Jawa/worldbuilding/world_faces_own_art_2026-10-23.md.

Everything is procedural and periodic (seamless at 512); NO donor bytes are read or copied. World Map Enhanced was studied
for technique only (Transient/wme_analysis_2026-10-20.md + the doc above).

Approaches (each makes a face for the four shipping biomes plus Stillsand, the Dune Sea they sit in):
  today    the installed faces (src/**/Textures/World/Biomes/RM_<X>.png), for comparison
  painted  WME-style painterly mottle: 2-3 close hues, soft lichen/crust patches, a pale+dark crease network, one tell
  relief   a shaded heightfield (satellite look): colour by height, lit relief, biome-specific landform
  decals   a clean bright field plus our own small drawn glyphs per tile (tufts, leaning shrubs, vents, pustules)
           -- needs a new per-tile decal pass in RM_WorldLook (cost noted in the doc)
Hills:  soft  = the installed RM_Hills atlases (vanilla quads, random rotation)
        drawn = our own lit low-poly mountain clumps, unrotated, tinted by the biome (needs our own hill pass)

The scene renderer is an APPROXIMATION of the game, not the WorldTerrain shader: flat hex grid, world-space planar
projection of each face, ~1-tile soft borders (as RM_WorldLook draws), mip-like box downsampling. The face scale (how many
hexes one 512 face spans) is UNMEASURED in the game (worldmap_in_game_audit_2026-10-20.md §6); TEX_PER_HEX is the assumption.

usage:  python3 world_face_variants.py gen [--out DIR]      faces, scenes, sheet thumbs, stats.json
        python3 world_face_variants.py sheet [--out DIR]    the owner's review page in Transient/ (keeps his decisions file)
DIR defaults to <agent storage>/rimmandrake/scratch/worldfaces_variants.  Installs nothing.
"""
import argparse, json, math, os, re, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import biome_worldfaces as BW  # noqa: E402  (periodic noise helpers, stats)

N = BW.N
band, warped, emboss, ridge, gblur, z, H, stats = BW.band, BW.warped, BW.emboss, BW.ridge, BW.gblur, BW.z, BW.H, BW.stats
REPO = BW.REPO
TEX_PER_HEX = 160.0          # ASSUMPTION: one 512 face spans ~3.2 hexes (UNMEASURED in game)
BIOMES = ["Pyrelands", "LeaningScrub", "Cauldron", "Contagion"]
CONTEXT = ["Stillsand"]
INSTALLED = {"Pyrelands": "src/RimMandrake/Pyrelands/Textures/World/Biomes/RM_Pyrelands.png",
             "LeaningScrub": "src/RimMandrake/LeaningScrub/Textures/World/Biomes/RM_LeaningScrub.png",
             "Cauldron": "src/RimMandrake/Cauldron/Textures/World/Biomes/RM_Cauldron.png",
             "Contagion": "src/RimMandrake/Contagion/Textures/World/Biomes/RM_Contagion.png",
             "Stillsand": "src/RimMandrake/Stillsand/Textures/World/Biomes/RM_Stillsand.png",
             "Sea": "src/RimUtinni/UtinniPatches/Textures/World/Biomes/RUT_TwilightSea.png"}
HILL_ATLAS = "src/RimMandrake/TerminalBiomes/Textures/World/RM_Hills/{}.png"

# palettes from the biome sheets (design/Jawa/worldbuilding/biomes/*): dark, mid, light, accent, accent2
P = {
 # the burning savanna: golden straw, black ash bands, ember line (the_pyrelands.md; 70s gold-brown)
 "Pyrelands":    ["#3b2f25", "#a8834a", "#d0ac6c", "#c2602a", "#6e5a40"],
 # silver-green fuzz, grey darkward, waxy gold sunward, near-black venomvine islands (arid_shrubland.md)
 "LeaningScrub": ["#3a3d30", "#8a916c", "#b6b28a", "#c4a24e", "#6f7462"],
 # wet black and slate; sulfur yellow, bruised blue crystal, red-purple films, no warm light (cauldron.md)
 "Cauldron":     ["#1f2122", "#45494a", "#696f6f", "#c4ac3e", "#4d5878"],
 # red water and fog, pink-and-blue aberrations, grey-white husks (the_contagion.md)
 "Contagion":    ["#4a1d22", "#954848", "#c79c98", "#d6cec4", "#6878a6"],
 # the Dune Sea: warm sand (context only)
 "Stillsand":    ["#8a6c46", "#c2a06c", "#dcc394", "#a27c4c", "#b49464"],
}
SEED = {"Pyrelands": 101, "LeaningScrub": 202, "Cauldron": 303, "Contagion": 404, "Stillsand": 505}


def ramp(t, cols):
    """t in ~[0,1] -> colour through dark, mid, light (piecewise linear)."""
    d, m, l = (H(c) for c in cols[:3]); t = np.clip(t, 0, 1)[..., None]
    lo = d * (1 - t / 0.5) + m * (t / 0.5); hi = m * (1 - (t - 0.5) / 0.5) + l * ((t - 0.5) / 0.5)
    return np.where(t < 0.5, lo, hi)


def tint(img, col, a):
    return img * (1 - a[..., None]) + H(col)[None, None, :] * a[..., None]


def sstep(x, a, b):
    t = np.clip((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t)


def finish(img):
    return np.clip(np.rint(img), 0, 255).astype(np.uint8)


# ---------------- approach: painted (WME-inspired technique, our own colours and tells) ----------------
def painted(b):
    c = P[b]; s = SEED[b] * 1000
    big = z(0.5 * band(1.5, 4, s) + 0.5 * warped(4, 10, s + 1, 8))       # 50-120 px colour fields
    mid = z(warped(10, 26, s + 2, 4))                                      # 20-50 px mottle
    t = 0.52 + 0.07 * big + 0.09 * mid
    img = ramp(t, c)
    lich = sstep(z(warped(18, 45, s + 3, 3)), 0.7, 1.6)                    # soft lichen/crust patches 8-25 px
    img = tint(img, c[2], 0.2 * lich)
    cre = ridge(warped(6, 14, s + 4, 7), 1.2)                              # crease network, pale on one side, dark on the other
    e = emboss(gblur(cre, 1.0))
    img = img + (np.clip(e, 0, None) * 4 - np.clip(-e, 0, None) * 5)[..., None] * (0.4 + 0.6 * cre)[..., None]
    grain = gblur(band(40, 110, s + 5), 1.3)                               # no sub-3-px sparkle
    img = img + (z(grain) * 3.0)[..., None]
    if b == "Pyrelands":   # diagonal ash smears over the straw, ember flecks along their edges
        yy, xx = np.mgrid[0:N, 0:N]
        sm = warped(1.5, 5, s + 6, 14, ax=0.35, ay=1.0)
        ash = sstep(sm, 0.2, 1.4)
        img = tint(img, c[0], 0.30 * gblur(ash, 2.0))
        edge = np.clip(ash * (1 - ash) * 4, 0, 1) * sstep(z(warped(30, 70, s + 7, 2)), 0.6, 1.6)
        img = tint(img, c[3], 0.4 * gblur(edge, 1.2))
    elif b == "LeaningScrub":   # waxy gold sunward patches, wind streaks all leaning one way, venomvine islands
        gold = sstep(z(warped(3, 8, s + 6, 8)), 0.4, 1.4)
        img = tint(img, c[3], 0.35 * gold)
        st = warped(14, 40, s + 7, 3, ax=0.25, ay=1.0)
        img = img + (z(gblur(st, 1.0)) * 4.5)[..., None]
        vv = sstep(z(warped(10, 24, s + 8, 4)), 1.5, 2.2)
        img = tint(img, c[0], 0.6 * vv)
    elif b == "Cauldron":   # sulfur seams, bruised-blue crystal patches, wet black pools
        seam = ridge(warped(4, 10, s + 6, 8), 1.4)
        img = tint(img, c[3], 0.25 * gblur(seam, 0.8) * sstep(z(warped(2, 6, s + 9, 6)), -0.3, 0.8))
        blue = sstep(z(warped(6, 16, s + 7, 5)), 1.2, 2.0)
        img = tint(img, c[4], 0.22 * blue)
        pool = sstep(z(warped(5, 14, s + 8, 6)), 1.0, 1.8)
        img = tint(img, c[0], 0.55 * pool)
    elif b == "Contagion":   # red vein network, grey-white husk crusts, blue aberrations
        vein = ridge(warped(5, 12, s + 6, 8), 1.1)
        img = tint(img, "#5a1418", 0.35 * gblur(vein, 0.8))
        husk = sstep(z(warped(4, 12, s + 7, 6)), 1.3, 2.0)
        img = tint(img, c[3], 0.4 * husk)
        blue = sstep(z(warped(3, 8, s + 8, 8)), 1.5, 2.2)
        img = tint(img, c[4], 0.25 * blue)
    elif b == "Stillsand":   # dune ripple
        yy = np.mgrid[0:N, 0:N][0]
        rip = np.sin(2 * np.pi * 40 * yy / N + band(3, 8, s + 6) * 1.8)
        img = img + (gblur(rip, 0.8) * 3.5)[..., None]
    return finish(img)


# ---------------- approach: relief (shaded heightfield) ----------------
def hillshade(h, light=(-0.6, -0.8), k=1.0):
    gx = (np.roll(h, -1, 1) - np.roll(h, 1, 1)) * 0.5; gy = (np.roll(h, -1, 0) - np.roll(h, 1, 0)) * 0.5
    nx, ny, nz = -gx * k, -gy * k, np.ones_like(h)
    n = np.sqrt(nx * nx + ny * ny + nz * nz)
    lx, ly, lz = light[0], light[1], 0.9
    ln = math.sqrt(lx * lx + ly * ly + lz * lz)
    return (nx * lx + ny * ly + nz * lz) / (n * ln)


def relief(b):
    c = P[b]; s = SEED[b] * 1000 + 7
    base = z(0.55 * warped(2, 6, s, 10) + 0.30 * warped(6, 16, s + 1, 5) + 0.15 * warped(16, 40, s + 2, 3))
    extra = np.zeros((N, N)); colt = 0.5 + 0.16 * base
    img = None
    if b == "Pyrelands":    # rolling grass, burn scars as dark sunk patches with an ember rim
        h = base * 6
        scar = sstep(z(warped(2.5, 7, s + 3, 12)), 0.3, 1.0)
        h = h - 3 * scar
        img = ramp(colt + 0.1 * z(warped(10, 30, s + 4, 3)), c)
        img = tint(img, c[0], 0.6 * scar)
        rim = gblur(np.clip(scar * (1 - scar) * 4, 0, 1), 1.0)
        img = tint(img, c[3], 0.5 * rim)
    elif b == "LeaningScrub":   # wind-combed ridges leaning one way, shrub clumps as fine bumps
        yy, xx = np.mgrid[0:N, 0:N]
        ph = 2 * np.pi * (14 * (xx + 0.5 * yy) / N) + band(2, 6, s + 3) * 2.2
        h = base * 4 + 2.2 * np.sin(ph) + 1.2 * gblur(z(band(30, 80, s + 4)), 1.4)
        img = ramp(colt + 0.07 * np.sin(ph), c)
        gold = sstep(z(warped(2, 6, s + 5, 8)), 0.3, 1.3)
        img = tint(img, c[3], 0.32 * gold)
    elif b == "Cauldron":   # pocked crust: soft basins, sulfur on the rims, wet black in the hollows
        pits = gblur(np.clip(z(warped(5, 12, s + 3, 4)) - 0.8, 0, None), 2.0)
        h = base * 4 - 5 * pits
        img = ramp(colt - 0.25 * z(pits), c)
        rim = gblur(np.clip(-(gblur(pits, 3) - pits), 0, None), 1.0)
        img = tint(img, c[3], np.clip(0.5 * z(gblur(rim, 2.0)), 0, 0.3))
        blue = sstep(z(warped(5, 14, s + 6, 5)), 1.3, 2.0)
        img = tint(img, c[4], 0.2 * blue)
    elif b == "Contagion":   # bulbous swollen growths, red veins in the valleys, pale husk caps
        blob = gblur(np.clip(z(warped(6, 14, s + 3, 4)) + 0.2, 0, None), 2.2)
        h = base * 3 + 6 * blob
        img = ramp(colt + 0.18 * z(blob), c)
        vall = ridge(z(blob) + 0.3, 1.6)
        img = tint(img, "#5a1418", 0.55 * vall)
        cap = sstep(z(gblur(blob, 2.0)), 1.6, 2.6)
        img = tint(img, c[2], 0.25 * cap)
    else:                   # Stillsand: dunes
        yy = np.mgrid[0:N, 0:N][0]
        ph = 2 * np.pi * 10 * yy / N + band(2, 5, s + 3) * 2.5
        h = base * 3 + 3 * np.abs(np.sin(ph))
        img = ramp(colt + 0.05 * np.sin(ph), c)
    hs = hillshade(gblur(h, 2.0), k=1.1)
    hs = (hs - hs.mean())
    img = img * (1 + (0.16 if b == "Contagion" else 0.24) * hs[..., None])
    return finish(img)


# ---------------- approach: decals (clean field + our own per-tile glyphs) ----------------
def decal_face(b):
    c = P[b]; s = SEED[b] * 1000 + 13
    big = z(0.5 * band(1.5, 4, s) + 0.5 * warped(4, 10, s + 1, 8))
    t = 0.56 + 0.08 * big + 0.03 * z(gblur(band(20, 60, s + 2), 1.5))
    img = ramp(t, c)
    if b == "Cauldron": img = tint(img, c[4], 0.08 * sstep(big, 0.5, 1.5))
    if b == "Contagion": img = tint(img, c[3], 0.15 * sstep(big, 0.6, 1.6))
    return finish(img)


def _glyph_canvas(n=96):
    return Image.new("RGBA", (n, n), (0, 0, 0, 0))


def glyphs(b, rng):
    """A small set of 96 px RGBA glyphs for biome b, lit from upper-left, soft drop shadow, never white."""
    c = [tuple(int(x) for x in H(k)) for k in P[b]]
    out = []
    for v in range(4):
        im = _glyph_canvas(); d = ImageDraw.Draw(im)
        sh = _glyph_canvas(); ds = ImageDraw.Draw(sh)
        if b == "Pyrelands":   # straw tufts with a char base; every other one an ember-lit burn line
            if v % 2 == 0:
                for k in range(7):
                    x0 = 30 + k * 6 + rng.integers(-2, 3); h_ = rng.integers(18, 34)
                    lean = rng.integers(-6, 7)
                    d.line([(x0, 70), (x0 + lean, 70 - h_)], fill=c[2] + (255,), width=3)
                    d.line([(x0 + 1, 70), (x0 + lean + 1, 70 - h_ * 0.5)], fill=c[1] + (255,), width=2)
                ds.ellipse((24, 64, 76, 78), fill=(0, 0, 0, 120))
            else:
                pts = [(18 + i * 6, 58 + 8 * math.sin(i * 0.7 + v)) for i in range(11)]
                ds.line([(x, y + 5) for x, y in pts], fill=(0, 0, 0, 120), width=9)
                d.line(pts, fill=c[0] + (255,), width=8)
                d.line([(x, y - 3) for x, y in pts], fill=c[3] + (255,), width=3)
        elif b == "LeaningScrub":   # shrubs leaning with the wind; one dark venomvine clump
            dark = v == 3
            for k in range(3):
                cx = 28 + k * 18 + rng.integers(-3, 4); cy = 52 + rng.integers(-6, 7); r = rng.integers(9, 14)
                col = c[0] if dark else (c[1] if k % 2 else c[4])
                d.line([(cx - 6, cy + r + 10), (cx, cy)], fill=(60, 50, 38, 255), width=3)
                ds.ellipse((cx - r + 4, cy - r + 6, cx + r + 6, cy + r + 8), fill=(0, 0, 0, 110))
                d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col + (255,))
                hl = c[3] if (not dark and k == 1) else c[2]
                d.ellipse((cx - r + 2, cy - r + 2, cx + r * 0.2, cy + r * 0.1), fill=hl + (200 if not dark else 90,))
        elif b == "Cauldron":   # dark vent mound, sulfur rim, a grey steam wisp
            ds.ellipse((22, 58, 80, 80), fill=(0, 0, 0, 120))
            d.polygon([(20, 74), (48, 44), (76, 74)], fill=c[0] + (255,))
            d.polygon([(20, 74), (48, 44), (44, 74)], fill=c[1] + (255,))
            d.ellipse((40, 40, 56, 50), fill=c[3] + (255,))
            if v % 2 == 0:
                for k in range(5):
                    r = 6 + k * 2; cx = 50 + k * 4 + rng.integers(-2, 3); cy = 34 - k * 7
                    d.ellipse((cx - r, cy - r * 0.7, cx + r, cy + r * 0.7), fill=(168, 172, 170, 110 - k * 15))
            else:
                d.polygon([(60, 70), (66, 54), (72, 70)], fill=c[4] + (255,))
        elif b == "Contagion":   # a cluster of swollen pustules
            for k in range(rng.integers(3, 6)):
                r = rng.integers(7, 14); cx = 48 + rng.integers(-22, 23); cy = 54 + rng.integers(-14, 15)
                ds.ellipse((cx - r + 3, cy - r + 5, cx + r + 5, cy + r + 7), fill=(0, 0, 0, 110))
                d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(c[1] if k % 3 else c[4]) + (255,))
                d.ellipse((cx - r * 0.6, cy - r * 0.6, cx + r * 0.1, cy), fill=c[2] + (220,))
        else:   # Stillsand: small dune crest arcs
            pts = [(20 + i * 6, 60 - 10 * math.sin(i * 0.33)) for i in range(11)]
            ds.line([(x, y + 4) for x, y in pts], fill=(0, 0, 0, 80), width=6)
            d.line(pts, fill=c[2] + (255,), width=4)
            d.line([(x, y + 3) for x, y in pts], fill=c[0] + (200,), width=2)
        sh = sh.filter(ImageFilter.GaussianBlur(3))
        out.append(Image.alpha_composite(sh, im))
    return out


# ---------------- hills ----------------
def hills_soft():
    out = {}
    for k in ("SmallHills", "LargeHills", "Mountains", "Impassable"):
        a = Image.open(os.path.join(REPO, HILL_ATLAS.format(k))).convert("RGBA")
        out[k] = [a.crop((x, y, x + 128, y + 128)) for y in (0, 128) for x in (0, 128)]
    return out


def mountain_clump(b, level, rng, n=128):
    """Our own lit low-poly mountain clump: 2-4 peaks, lit face / shade face, tinted toward the biome's dark colour."""
    c = P[b]; base = (H(c[0]) * 0.55 + H(c[1]) * 0.30 + H("#5a4632") * 0.15)
    lit = tuple(int(x) for x in np.clip(base * 1.55 + 18, 0, 255)); shade = tuple(int(x) for x in base * 0.75)
    im = _glyph_canvas(n); d = ImageDraw.Draw(im); sh = _glyph_canvas(n); ds = ImageDraw.Draw(sh)
    peaks = {"SmallHills": 2, "LargeHills": 3, "Mountains": 3, "Impassable": 4}[level]
    hmul = {"SmallHills": 0.45, "LargeHills": 0.65, "Mountains": 0.85, "Impassable": 1.0}[level]
    spots = sorted([(rng.integers(26, n - 26), rng.integers(60, n - 22)) for _ in range(peaks)], key=lambda p: p[1])
    for cx, cy in spots:
        w = rng.integers(26, 38) * (0.7 + 0.3 * hmul); h = rng.integers(22, 34) * hmul
        top = (cx + rng.integers(-4, 5), cy - h)
        ds.polygon([(cx - w + 6, cy + 4), (top[0] + 6, top[1] + 8), (cx + w + 6, cy + 4)], fill=(0, 0, 0, 70))
        d.polygon([(cx - w, cy), top, (cx + w, cy)], fill=shade + (255,))
        d.polygon([(cx - w, cy), top, (cx + rng.integers(-6, 4), cy)], fill=lit + (255,))
        if level in ("Mountains", "Impassable"):      # pale (not white) rock crest on the lit face
            cap = tuple(int(x) for x in np.clip(np.array(lit) * 1.12 + 10, 0, 225))
            d.polygon([top, (top[0] - w * 0.3, top[1] + h * 0.3), (top[0] + 1, top[1] + h * 0.22)], fill=cap + (255,))
    sh = sh.filter(ImageFilter.GaussianBlur(3))
    return Image.alpha_composite(sh, im)


# ---------------- scene renderer ----------------
SQ3 = math.sqrt(3)


def hex_ids(W, Hh, size):
    """pointy-top hexes of circumradius `size`; per pixel the axial (q, r) of its hex."""
    yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float64)
    q = (SQ3 / 3 * xx - yy / 3) / size; r = (2 / 3 * yy) / size
    x, zc = q, r; y = -x - zc
    rx, ry, rz = np.rint(x), np.rint(y), np.rint(zc)
    dx, dy, dz = np.abs(rx - x), np.abs(ry - y), np.abs(rz - zc)
    m1 = (dx > dy) & (dx > dz); m2 = ~m1 & (dy > dz)
    rx = np.where(m1, -ry - rz, rx); rz = np.where(~m1 & ~m2, -rx - ry, rz)
    return rx.astype(int), rz.astype(int)


def layout(qs, rs, seed=7):
    """Assign each hex a biome: Voronoi of fixed seeds in axial space, with a sea basin on the left."""
    uq = sorted(set(zip(qs.ravel().tolist(), rs.ravel().tolist())))
    rng = np.random.default_rng(seed)
    pts = np.array([(q + r / 2, r * SQ3 / 2) for q, r in uq])
    lo, hi = pts.min(0), pts.max(0); span = hi - lo
    centres = {"Sea": [(0.02, 0.5), (0.08, 0.1)], "Stillsand": [(0.55, 0.06), (0.95, 0.5), (0.5, 0.95), (0.75, 0.82)],
               "Pyrelands": [(0.30, 0.25)], "LeaningScrub": [(0.62, 0.35)], "Cauldron": [(0.33, 0.72)],
               "Contagion": [(0.78, 0.18)]}
    names, cs = [], []
    for k, v in centres.items():
        for c in v: names.append(k); cs.append(lo + np.array(c) * span)
    cs = np.array(cs)
    jit = (np.sin(pts[:, 0] * 0.9) + np.cos(pts[:, 1] * 0.7)) * span.min() * 0.03
    d = np.linalg.norm(pts[:, None, :] - cs[None, :, :], axis=2) + jit[:, None]
    d[:, [i for i, n in enumerate(names) if n == "Sea"]] *= 1.25
    lab = {t: names[i] for t, i in zip(uq, d.argmin(1))}
    hill = {}
    for t in uq:
        if lab[t] == "Sea": hill[t] = None; continue
        u = rng.random()
        hill[t] = None if u < 0.55 else "SmallHills" if u < 0.75 else "LargeHills" if u < 0.88 else "Mountains" if u < 0.97 else "Impassable"
    return lab, hill


def render(faces, sea, hills_kind, decals, zoom, W_out, H_out, fbiome=None):
    """faces: biome -> 512 RGB uint8.  Returns an RGB PIL image at (W_out, H_out)."""
    size_out = 34.0 if zoom == "mid" else 7.5            # hex circumradius on screen
    ss = 4 if zoom == "mid" else 9                          # supersample factor (mip-like box downsample)
    size = size_out * ss / 2 if zoom == "mid" else size_out * ss / 2
    ssf = 2                                                 # internal = 2x out for mid, 4.5x for far: keep memory sane
    size = size_out * ssf if zoom == "mid" else size_out * 4.5
    fac = size / size_out
    W, Hh = int(W_out * fac), int(H_out * fac)
    qs, rs = hex_ids(W, Hh, size)
    lab, hill = layout(qs, rs)
    keys = sorted(set(lab.values()))
    yy, xx = np.mgrid[0:Hh, 0:W]
    hexw = size * SQ3
    u = ((xx / hexw) * TEX_PER_HEX).astype(np.int64) % N; v = ((yy / hexw) * TEX_PER_HEX).astype(np.int64) % N
    q0, r0 = qs.min(), rs.min()
    lut = np.zeros((qs.max() - q0 + 1, rs.max() - r0 + 1), np.int16)
    for (q, r), k in lab.items(): lut[q - q0, r - r0] = keys.index(k)
    tile_lab = lut[qs - q0, rs - r0]
    acc = np.zeros((Hh, W, 3), np.float32); wsum = np.zeros((Hh, W), np.float32)
    blur = size * 0.22                                      # ~1-tile soft border like RM_WorldLook
    for i, k in enumerate(keys):
        m = Image.fromarray(((tile_lab == i) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(blur))
        m = np.asarray(m, np.float32) / 255.0
        if k == "Sea":
            tex = sea[v, u].astype(np.float32)
        else:
            tex = faces[k][v, u].astype(np.float32)
        acc += tex * m[..., None]; wsum += m
    img = acc / np.maximum(wsum, 1e-6)[..., None]
    macro = np.asarray(Image.fromarray((np.random.default_rng(5).random((max(Hh // int(size * 6), 2), max(W // int(size * 6), 2))) * 255).astype(np.uint8)).resize((W, Hh), Image.BICUBIC), np.float32) / 255 - 0.5
    img = img * (1 + 0.10 * macro[..., None])                # stand-in for the game's _MacroTex (World/WorldMacro)
    # sea: deepen away from the coast (RM_WorldLook films, approximated)
    sea_i = keys.index("Sea")
    seam = Image.fromarray(((tile_lab == sea_i) * 255).astype(np.uint8))
    deep = np.asarray(seam.filter(ImageFilter.MinFilter(int(size) | 1)).filter(ImageFilter.GaussianBlur(size * 1.5)), np.float32) / 255
    img = img * (1 - 0.35 * deep[..., None]) + np.array([13, 23, 51], np.float32) * 0.35 * deep[..., None]
    out = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")
    rng = np.random.default_rng(11)
    soft = hills_soft()
    if zoom == "far" and hills_kind == "drawn": hills_kind = "soft"     # LOD: drawn clumps hand over to soft relief past mid zoom
    gcache = {}
    for (q, r), lv in sorted(hill.items(), key=lambda t: t[0][1]):
        cx = size * (SQ3 * q + SQ3 / 2 * r); cy = size * 1.5 * r
        if cx < -size or cy < -size or cx > W + size or cy > Hh + size: continue
        b = lab[(q, r)]
        if decals and zoom == "mid" and b != "Sea" and lv is None:   # decals fade out past mid zoom
            gl = gcache.setdefault(b, glyphs(b, np.random.default_rng(SEED[b])))
            for _ in range(2 + int(rng.integers(0, 2))):
                g = gl[int(rng.integers(0, len(gl)))]
                gs = int(size * 1.3); gi = g.resize((gs, gs), Image.LANCZOS)
                ox = int(cx + rng.uniform(-0.55, 0.55) * size - gs / 2); oy = int(cy + rng.uniform(-0.5, 0.5) * size - gs / 2)
                out.alpha_composite(gi, (max(ox, 0), max(oy, 0))) if ox > -gs and oy > -gs else None
        if lv is None: continue
        if hills_kind == "soft":
            cell = soft[lv][int(rng.integers(0, 4))]
            sc = 2 * size * rng.uniform(0.9, 1.1)
            ci = cell.resize((int(sc), int(sc)), Image.LANCZOS).rotate(float(rng.uniform(0, 360)), Image.BICUBIC)
        else:
            ci = mountain_clump(b, lv, rng)
            sc = 2 * size * (1.25 if lv in ("Mountains", "Impassable") else 1.0)
            ci = ci.resize((int(sc), int(sc)), Image.LANCZOS)
        ox = int(cx - ci.width / 2 + rng.uniform(-0.1, 0.1) * size); oy = int(cy - ci.height / 2 + rng.uniform(-0.1, 0.1) * size)
        if ox >= 0 and oy >= 0 and ox + ci.width <= W and oy + ci.height <= Hh:
            out.alpha_composite(ci, (ox, oy))
    out = out.convert("RGB").resize((W_out, H_out), Image.BOX)
    return out, lab


FONT = None


def font(sz):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"):
        if os.path.exists(p): return ImageFont.truetype(p, sz)
    return ImageFont.load_default()


def caption(im, text, sz=18):
    bar = Image.new("RGB", (im.width, sz + 12), (24, 22, 20))
    ImageDraw.Draw(bar).text((8, 5), text, fill=(235, 228, 214), font=font(sz))
    o = Image.new("RGB", (im.width, im.height + bar.height)); o.paste(bar, (0, 0)); o.paste(im, (0, bar.height)); return o


def hstack(ims, gap=8, bg=(24, 22, 20)):
    h = max(i.height for i in ims); w = sum(i.width for i in ims) + gap * (len(ims) - 1)
    o = Image.new("RGB", (w, h), bg); x = 0
    for i in ims: o.paste(i, (x, 0)); x += i.width + gap
    return o


def vstack(ims, gap=8, bg=(24, 22, 20)):
    w = max(i.width for i in ims); h = sum(i.height for i in ims) + gap * (len(ims) - 1)
    o = Image.new("RGB", (w, h), bg); y = 0
    for i in ims: o.paste(i, (0, y)); y += i.height + gap
    return o


def load_installed(k):
    return np.asarray(Image.open(os.path.join(REPO, INSTALLED[k])).convert("RGB").resize((N, N)))


APPROACHES = {"today": None, "painted": painted, "relief": relief, "decals": decal_face}
LABEL = {"today": "Today (installed calm faces)", "painted": "A. Painted (WME-style mottle)",
         "relief": "B. Relief (shaded landform)", "decals": "C. Clean field + our own decals"}


CENTRE = {"Pyrelands": (0.27, 0.27), "LeaningScrub": (0.60, 0.40), "Cauldron": (0.30, 0.74), "Contagion": (0.82, 0.20)}
SEPT_SHOT = os.path.join(os.path.dirname(BW.storage_root()), "worldlook2", "CMP1_twilight_sea_before_after.png")


def biome_crop(scene, b, w=400, h=280):
    cx, cy = CENTRE[b]; x = int(cx * scene.width - w / 2); y = int(cy * scene.height - h / 2)
    x = min(max(x, 0), scene.width - w); y = min(max(y, 0), scene.height - h)
    return scene.crop((x, y, x + w, y + h))


def tiled(face, n=2, px=200):
    im = Image.fromarray(face); o = Image.new("RGB", (N * n, N * n))
    for i in range(n):
        for j in range(n): o.paste(im, (i * N, j * N))
    return o.resize((px, px), Image.LANCZOS)


def thumbs(out, sets):
    """Sheet pictures (opaque RGB composites, no cut-out alpha): one per approach and one per approach x biome."""
    th = os.path.join(out, "sheet"); os.makedirs(th, exist_ok=True)
    for ap in APPROACHES:
        d = os.path.join(out, ap)
        mid = Image.open(os.path.join(d, "scene_mid.png")); far = Image.open(os.path.join(d, "scene_far.png"))
        im = hstack([caption(far.resize((660, 384), Image.LANCZOS), "far zoom"), caption(mid.resize((660, 384), Image.LANCZOS), "mid zoom")])
        caption(im, LABEL[ap], 22).save(os.path.join(th, f"approach_{ap}.jpg"), quality=90)
        for b in BIOMES:
            im = hstack([caption(tiled(sets[ap][b], 2, 280), "face, 2x2 tiled"), caption(biome_crop(mid, b), "mid zoom"),
                         caption(biome_crop(far, b), "far zoom")])
            caption(im, f"{b}: {LABEL[ap]}", 20).save(os.path.join(th, f"{b}_{ap}.jpg"), quality=90)
    for hk in ("soft", "drawn"):
        mid = Image.open(os.path.join(out, f"hills_{hk}_mid.png"))
        far = Image.open(os.path.join(out, f"hills_{hk}_far.png"))
        lab = {"soft": "Hills 1: soft relief (built, installed)", "drawn": "Hills 2: our own drawn mountain clumps (soft past mid zoom)"}[hk]
        caption(hstack([caption(far.resize((660, 384), Image.LANCZOS), "far zoom"), caption(mid.resize((660, 384), Image.LANCZOS), "mid zoom")]), lab, 22).save(os.path.join(th, f"hills_{hk}.jpg"), quality=90)
    if os.path.exists(SEPT_SHOT):     # an in-game SCREENSHOT of 2026-09-11 (reference only; no donor texture is read)
        s = Image.open(SEPT_SHOT).convert("RGB")
        caption(s.crop((60, 60, 1460, 1054)).resize((1100, 781), Image.LANCZOS), "Reference: September 2026-09-11 in game (WME era), Twilight Sea / Pyrelands", 22).save(os.path.join(th, "reference_september.jpg"), quality=90)


def gen(out):
    os.makedirs(out, exist_ok=True)
    sea = load_installed("Sea")
    st = {}
    sets = {}
    for ap, fn in APPROACHES.items():
        d = os.path.join(out, ap); os.makedirs(d, exist_ok=True)
        faces = {}
        for b in BIOMES + CONTEXT:
            faces[b] = load_installed(b) if fn is None else fn(b)
            Image.fromarray(faces[b]).save(os.path.join(d, f"face_{b}.png"))
            st[f"{ap}/{b}"] = stats(faces[b])
        sets[ap] = faces
        hk = "drawn" if ap == "decals" else "soft"
        mid, _ = render(faces, sea, hk, ap == "decals", "mid", 1100, 640)
        far, _ = render(faces, sea, hk, ap == "decals", "far", 1100, 640)
        mid.save(os.path.join(d, "scene_mid.png")); far.save(os.path.join(d, "scene_far.png"))
        print(ap, "scenes done", flush=True)
    # hills comparison on today's faces' Stillsand + painted others (hills independent of the face)
    for hk in ("soft", "drawn"):
        mid, _ = render(sets["painted"], sea, hk, False, "mid", 1100, 640)
        mid.save(os.path.join(out, f"hills_{hk}_mid.png"))
        far, _ = render(sets["painted"], sea, hk, False, "far", 1100, 640)
        far.save(os.path.join(out, f"hills_{hk}_far.png"))
    json.dump(st, open(os.path.join(out, "stats.json"), "w"), indent=1)
    thumbs(out, sets)
    return sets


# ---------------- the owner's review page (non-art route: opaque renders, no cut-out sprites, no in-game size) ----------------
STEM = "world_faces_review_2026-10-23"
EFFECT = {
 "today": "Keep the installed calm faces. Costs nothing; reads flat and muddy at mid zoom.",
 "painted": "New face textures only: soft mottle, crust patches, a faint crease net, one tell per biome. Install + deploy, no code.",
 "relief": "New face textures only: a lit heightfield per biome. No code, but busiest at far zoom (repeats show).",
 "decals": "Calm bright faces + our own small glyphs drawn per tile (tufts, shrubs, vents, pustules). Needs a decal pass in RM_WorldLook.",
}
PREFILL = {"today": "no", "painted": "maybe", "relief": "no", "decals": "pick"}
HILLS = {"soft": ("Hills 1: soft relief (installed)", "Keep the built RM_Hills soft shading (vanilla quads, random rotation). No new work.", "pick"),
         "drawn": ("Hills 2: our own drawn mountain clumps", "Lit low-poly clumps tinted by biome, unrotated; soft relief past mid zoom. Needs our own hill pass.", "maybe")}


def build_sheet(out):
    import shutil
    tdir = os.path.join(REPO, "Transient"); img = os.path.join(tdir, STEM + "_img"); os.makedirs(img, exist_ok=True)
    src = os.path.join(out, "sheet")
    for f in os.listdir(src):
        shutil.copy(os.path.join(src, f), os.path.join(img, "wf_" + f))
    st = json.load(open(os.path.join(out, "stats.json")))
    rel = STEM + "_img/wf_"
    items = []
    for ap in APPROACHES:
        items.append({"id": f"look_{ap}", "label": LABEL[ap], "group": "1. The whole look (one approach for every biome)",
                      "effect": EFFECT[ap], "thumb": rel + f"approach_{ap}.jpg", "prefill": PREFILL[ap],
                      "trueSize": {"none": "a world face texture has no in-game size; shown at far and mid zoom"}})
    for hk, (lab, eff, pf) in HILLS.items():
        items.append({"id": f"hills_{hk}", "label": lab, "group": "2. Hills and mountains", "effect": eff,
                      "thumb": rel + f"hills_{hk}.jpg", "prefill": pf,
                      "trueSize": {"none": "a world hill decal has no in-game size; shown at far and mid zoom"}})
    for b in BIOMES:
        for ap in APPROACHES:
            s = st[f"{ap}/{b}"]
            items.append({"id": f"{b}_{ap}", "label": f"{b}: {LABEL[ap]}", "group": f"3. Per biome: {b}",
                          "effect": EFFECT[ap], "thumb": rel + f"{b}_{ap}.jpg", "prefill": PREFILL[ap],
                          "meta": {"mean RGB": ",".join(map(str, s["mean"])), "sd": str(s["sd"]), "blockiness": str(s["blk"]),
                                   "seam/nbr": f'{s["seam"]}/{s["nbr"]}'},
                          "trueSize": {"none": "a world face texture has no in-game size; shown tiled, at mid and at far zoom"}})
    brief = (
        "<p><b>Your order (card, 2026-10-23):</b> <i>\"Do a background deep dive for (3) [make our own face textures] right now "
        "... inspire yourself by World Map Enhanced's approaches and make variations to try out, then a sheet to select for the "
        "user. We definitely should own our own world art.\"</i> So World Map Enhanced stays out; every picture here is our own, "
        "made by code (no donor bytes).</p>"
        "<p><b>What made September pretty</b> (the screenshot below, 2026-09-11): light, clearly different colours per biome, and "
        "small drawn marks on almost every hex. Approach <b>C</b> rebuilds that with our own art; <b>A</b> gets part of the way with "
        "textures alone; <b>B</b> is the photographic route. Pick per group: <b>Pick</b> = this one, <b>Maybe</b> = worth a live try, "
        "<b>No</b> = drop. Group 3 lets one biome differ from the whole-look pick; leave it alone to follow group 1.</p>"
        "<p><b>These are offline renders, not the game.</b> A flat hex patch with each face projected, ~1-tile soft borders and a "
        "stand-in for the game's large-scale variation. How many hexes one face spans in game is unmeasured (assumed ~3), so the "
        "repeat at far zoom may look different live. Nothing is installed until you pick; the pick is tried on the planet first.</p>"
        f"<p><img src=\"{rel}reference_september.jpg\" style=\"max-width:100%\" alt=\"September reference\"></p>"
        "<p>Design notes: <code>design/Jawa/worldbuilding/world_faces_own_art_2026-10-23.md</code>.</p>")
    cfg = {"sheetId": STEM, "title": "Our own world faces: pick a look",
           "subtitle": "2026-10-23 · 4 looks × 4 shipping biomes + hills · WORLDMAP_FACES_DECIDE_SEPTEMBER_WAS_PRETTIER",
           "briefHtml": brief,
           "criterion": "Rows are in the order today → A → B → C; the prefill is the agent's lean (C, then A), judged by fit to the September look and the biome sheets, not by cost.",
           "invented": ["The four tells per biome (ash smears, leaning shrubs, vents with steam, pustule clusters) are the agent's reading of the biome sheets.",
                        "Face scale (~3 hexes per face), the soft-border width and the macro variation are assumptions of the offline renderer.",
                        "Decals and drawn hills fade out past mid zoom (an LOD rule the agent proposes; at far zoom they become speckle)."],
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
                 lambda m: m.group(1) + "\n" + json.dumps(items, indent=1).replace("</", "<\\/") + "\n" + m.group(3), tpl, count=1, flags=re.S)
    html = os.path.join(tdir, STEM + ".html")
    open(html, "w").write(tpl)
    dec = os.path.join(tdir, STEM + ".decisions.json")
    if not os.path.exists(dec):       # never overwrite his picks
        json.dump({"sheetId": STEM, "posture": "whitelist", "criterion": cfg["criterion"],
                   "reviewStatus": {"state": "prefill", "by": None, "at": None, "evidence": "agent variations; no human has ruled"},
                   "decisions": {it["id"]: {"decision": "", "prefill": it["prefill"], "note": ""} for it in items}},
                  open(dec, "w"), indent=2, sort_keys=True)
    print("SHEET", html); print("DECISIONS", dec)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["gen", "sheet"])
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    out = a.out or os.path.join(os.path.dirname(BW.storage_root()), "worldfaces_variants")
    if a.cmd == "gen":
        gen(out); print("OUT", out)
    else:
        build_sheet(out)


if __name__ == "__main__":
    main()
