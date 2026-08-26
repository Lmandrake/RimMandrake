"""Art direction for every world landmark icon Ash'karr draws, and the painter that
executes it.

WHY THIS SHAPE.  Ludeon's landmark icons are not pictures, they are stamps: a flat
palette, a hard black rim and -- on the good ones -- a TRANSLUCENT body (Cliffs and
Valley cap at alpha 128) so the planet's terrain reads through.  Vanilla Landmarks
Expanded copied only the opaque half, which is why its desert set reads as coloured
paper cutouts.  Every treatment below repaints the MATERIAL inside a silhouette that
is lifted unchanged from the shipping icon, so layout, footprint and atlas geometry
stay byte-compatible and only the surface changes.

WHY NOT AN IMAGE MODEL.  These are read at 64 px on the globe.  Photographic detail
dissolves into noise at that size -- measured on this project's own sprite pilot --
while flat tone steps, directional grain and a hard rim survive.  So the prompts below
are executed by the procedural treatments in this file rather than by a diffusion
model.  They are still written as prompts, because the prompt IS the design: material,
orientation, alignment, palette, and the words that fix the mood.
"""
import os
import numpy as np
from PIL import Image, ImageFilter

SS = 2
CELL = 512                    # 1024x1024 per file, 2x2 atlas -- 4x Ludeon's density
OUTLINE_PX = 3.0


# ---------------------------------------------------------------- shared machinery

def _noise(shape, rng, scale, amp):
    """Smooth low-frequency value noise.  Blurred after upscaling because a small grid
    stretched bicubic keeps AXIS-ALIGNED edges, and thresholding that paints
    straight-sided rectangles -- how a brine patch once shipped as a grey bar."""
    n = max(3, int(shape[0] / scale))
    f = rng.random((n, n)).astype("float32")
    im = Image.fromarray((f * 255).astype("uint8")).resize(shape, Image.BICUBIC)
    im = im.filter(ImageFilter.GaussianBlur(max(1, shape[0] / (n * 3))))
    return (np.asarray(im, dtype="float32") / 255.0 - 0.5) * 2 * amp


def _fbm(shape, rng, scale, amp, octaves=3):
    out = np.zeros(shape, "float32")
    a, s = amp, scale
    for _ in range(octaves):
        out += _noise(shape, rng, s, a)
        a *= 0.5
        s *= 0.45
    return out


def _erode(m, k):
    e = m.copy()
    for _ in range(int(k)):
        e = e & np.roll(e, 1, 0) & np.roll(e, -1, 0) & np.roll(e, 1, 1) & np.roll(e, -1, 1)
    return e


def _dist_in(mask, cap):
    """Cheap distance-from-edge, in pixels, saturating at cap.  Drives every rim and
    every depth gradient in this file."""
    d = np.zeros(mask.shape, "float32")
    cur = mask.copy()
    for i in range(int(cap)):
        cur = _erode(cur, 1)
        d += cur
        if not cur.any():
            break
    return d


def _grad(t, stops):
    """t in 0..1 -> RGB, piecewise-linear through (pos, rgb) stops."""
    t = np.clip(t, 0, 1)
    out = np.zeros(t.shape + (3,), "float32")
    for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
        m = (t >= p0) & (t <= p1)
        k = ((t[m] - p0) / max(1e-6, p1 - p0))[:, None]
        out[m] = np.array(c0, "float32") * (1 - k) + np.array(c1, "float32") * k
    return out


def _axis(mask):
    """Angle of the silhouette's long axis.  Grain is aligned to this rather than to
    the canvas, so a braided channel runs ALONG its own channel and dune ripples lie
    across the dune instead of across the picture."""
    ys, xs = np.nonzero(mask)
    if len(ys) < 8:
        return 0.0
    p = np.stack([xs - xs.mean(), ys - ys.mean()]).astype("float32")
    w, v = np.linalg.eigh(np.cov(p))
    vx, vy = v[:, int(np.argmax(w))]
    return float(np.arctan2(vy, vx))


# ---------------------------------------------------------------- treatments
# Each returns (rgb, alpha) as float arrays over the whole cell.  `P` is the icon's
# own parameter block from SPECS.

def t_crust(mask, rng, P):
    N = mask.shape[0]
    gy, gx = np.mgrid[0:N, 0:N].astype("float32")
    wy = gy + _noise((N, N), rng, N / 5.5, N * 0.06)
    wx = gx + _noise((N, N), rng, N / 5.5, N * 0.06)
    ys, xs = np.nonzero(mask)
    k = min(P.get("plates", 11), max(3, len(ys) // 400))
    pts = np.stack([ys, xs], 1)[rng.choice(len(ys), k, replace=False)].astype("float32")
    d = (wy[..., None] - pts[:, 0]) ** 2 + (wx[..., None] - pts[:, 1]) ** 2
    lab = d.argmin(2)
    near = np.sort(d, 2)[..., :2]
    seam = np.sqrt(near[..., 1]) - np.sqrt(near[..., 0])

    rgb = np.zeros(mask.shape + (3,), "float32")
    base = np.array(P["base"], "float32")
    for i in range(k):
        rgb[lab == i] = base - rng.uniform(0, P.get("plate_var", 12)) * np.array((1.0, .96, .86))
    dip = _fbm((N, N), rng, N / 3.0, 1.0)
    rgb[dip > 0.52] = P.get("damp", P["base"])

    w = N * P.get("seam_w", 0.009)
    ridge = seam < w * (1.0 + 0.9 * _noise((N, N), rng, N / 7, 1.0))
    crest = seam < w * 0.40
    rgb[ridge] = P["seam"]
    rgb[crest] = P.get("seam_lit", P["seam"])

    a = np.full(mask.shape, float(P.get("alpha", 190)), "float32")
    if P.get("bloom", True):
        bloom = (_noise((N, N), rng, N / 26, 1.0) > 0.30) & (seam < w * 4.5)
        bloom |= (_noise((N, N), rng, N / 40, 1.0) > 0.52) & (seam < w * 9)
        rgb[bloom] = P.get("bloom_col", P["seam"])
        a[bloom] = float(P.get("alpha", 190)) + 18
        glint = (rng.random(mask.shape) < 0.004) & bloom
        glint = np.asarray(Image.fromarray((glint * 255).astype("uint8"))
                           .filter(ImageFilter.MaxFilter(2 * int(0.004 * N) + 1))) > 128
        rgb[glint] = P.get("glint", (255, 255, 255))
        a[glint] = float(P.get("alpha", 190)) + 50
    a[ridge] = float(P.get("alpha", 190)) + 32
    a[crest] = float(P.get("alpha", 190)) + 40
    return rgb, a


def t_storm(mask, rng, P):
    N = mask.shape[0]
    gy, gx = np.mgrid[0:N, 0:N].astype("float32")
    cy, cx = N * (0.32 + 0.36 * rng.random()), N * (0.32 + 0.36 * rng.random())
    r = np.maximum(np.hypot(gy - cy, gx - cx) + _noise((N, N), rng, N / 3.5, N * 0.10), N * 0.10)
    th = np.arctan2(gy - cy, gx - cx)
    arms = P.get("arms", 2 if rng.random() < 0.5 else 3)
    twist = (1.15 + 0.55 * rng.random()) * (1 if rng.random() < 0.5 else -1)
    ph = arms * (th + twist * np.log(r))
    ph += 1.3 * _noise((N, N), rng, N / 5.5, 1.0) + 0.7 * _noise((N, N), rng, N / 13, 1.0)
    band = (0.5 + 0.5 * np.sin(ph)) * (0.62 + 0.38 * np.clip(r / (N * 0.42), 0, 1))
    band += 0.09 * _noise((N, N), rng, N / 30, 1.0)
    t = np.clip(band, 0, 1)
    rgb = _grad(t, [(0.0, P["dark"]), (0.5, P["base"]), (1.0, P["lit"])])
    wisp = (rng.random(mask.shape) < 0.003) & (band > 0.74)
    rgb[wisp] = P.get("glint", P["lit"])
    a = float(P.get("alpha_lo", 92)) + (float(P.get("alpha", 214)) - float(P.get("alpha_lo", 92))) * t
    a[wisp] = 234.0
    return rgb, a


def t_ripples(mask, rng, P):
    """Wind-built bedforms.  Crests run ACROSS the prevailing wind, so the grain is
    laid perpendicular to the silhouette's own long axis, not to the canvas."""
    N = mask.shape[0]
    gy, gx = np.mgrid[0:N, 0:N].astype("float32")
    ang = _axis(mask) + np.pi / 2 + P.get("skew", 0.0)
    v = -gx * np.sin(ang) + gy * np.cos(ang)
    v = v + _fbm((N, N), rng, N / 3.0, N * P.get("sinuosity", 0.13))
    band = (v / (N * P.get("wave", 0.14))) % 1.0
    # sharp lee face, long stoss slope -- what makes a dune read as a dune
    t = np.where(band < 0.72, band / 0.72, 1.0 - (band - 0.72) / 0.28)
    rgb = _grad(t, [(0.0, P["dark"]), (0.55, P["base"]), (1.0, P["lit"])])
    a = np.full(mask.shape, float(P.get("alpha", 200)), "float32")
    if P.get("clast", 0):
        sp = rng.random(mask.shape) < P["clast"]
        sp = np.asarray(Image.fromarray((sp * 255).astype("uint8"))
                        .filter(ImageFilter.MaxFilter(2 * int(0.004 * N) + 1))) > 128
        rgb[sp] = P.get("clast_col", P["dark"])
    return rgb, a


def t_clasts(mask, rng, P):
    """Loose angular debris: a granular bed of overlapping stones, each with its own
    tone, lit from the upper left so the field reads as three-dimensional rubble."""
    N = mask.shape[0]
    gy, gx = np.mgrid[0:N, 0:N].astype("float32")
    ys, xs = np.nonzero(mask)
    n = P.get("stones", 90)
    pts = np.stack([ys, xs], 1)[rng.choice(len(ys), min(n, len(ys)), replace=False)].astype("float32")
    wy = gy + _noise((N, N), rng, N / 9, N * 0.02)
    wx = gx + _noise((N, N), rng, N / 9, N * 0.02)
    d = (wy[..., None] - pts[:, 0]) ** 2 + (wx[..., None] - pts[:, 1]) ** 2
    lab = d.argmin(2)
    near = np.sort(d, 2)[..., :2]
    seam = np.sqrt(near[..., 1]) - np.sqrt(near[..., 0])
    rgb = np.zeros(mask.shape + (3,), "float32")
    base, lit, dark = (np.array(P[k], "float32") for k in ("base", "lit", "dark"))
    for i in range(len(pts)):
        f = rng.random()
        rgb[lab == i] = base + (lit - base) * f if f > 0.5 else base + (dark - base) * (1 - 2 * f)
    rgb[seam < N * 0.0035] = P.get("seam", P["dark"])
    return rgb, np.full(mask.shape, float(P.get("alpha", 198)), "float32")


def t_pool(mask, rng, P):
    """Standing liquid: colour deepens away from the shore, with a wet margin ring and
    a slack, unlit surface.  Depth is the whole read -- a pool painted at one tone is
    a puddle of paint."""
    N = mask.shape[0]
    dep = np.clip(_dist_in(mask, N * 0.30) / (N * 0.30), 0, 1)
    dep = np.clip(dep + _fbm((N, N), rng, N / 4.0, 0.16), 0, 1)
    rgb = _grad(dep, [(0.0, P.get("shore", P["lit"])), (0.22, P["lit"]),
                      (0.60, P["base"]), (1.0, P["dark"])])
    if P.get("scum", 0):
        s = _fbm((N, N), rng, N / 7.0, 1.0)
        m = (s > P["scum"]) & (dep > 0.10)
        rgb[m] = P.get("scum_col", P["lit"])
    a = float(P.get("alpha", 206)) - 26 * (1 - dep)
    return rgb, a.astype("float32")


def t_crater(mask, rng, P):
    """An impact or collapse: raised rim catching the light, shadowed inner wall, flat
    floor.  Concentric about the mark's own centroid, warped so no ring is a circle."""
    N = mask.shape[0]
    ys, xs = np.nonzero(mask)
    cy, cx = ys.mean(), xs.mean()
    gy, gx = np.mgrid[0:N, 0:N].astype("float32")
    r = np.hypot(gy - cy, gx - cx) + _fbm((N, N), rng, N / 4.0, N * 0.05)
    R = np.sqrt(mask.sum() / np.pi)
    t = np.clip(r / max(R, 1), 0, 1.4)
    rgb = _grad(np.clip((t - 0.0) / 1.2, 0, 1),
                [(0.0, P["dark"]), (0.42, P.get("floor", P["base"])),
                 (0.66, P["base"]), (0.80, P["lit"]), (1.0, P["dark"])])
    a = np.full(mask.shape, float(P.get("alpha", 202)), "float32")
    return rgb, a


def t_strata(mask, rng, P):
    """Bedded rock seen from above: layers exposed along the scarp, running parallel to
    the landform's own strike, each bed a slightly different age and tone."""
    N = mask.shape[0]
    gy, gx = np.mgrid[0:N, 0:N].astype("float32")
    ang = _axis(mask) + P.get("skew", 0.0)
    v = -gx * np.sin(ang) + gy * np.cos(ang)
    v = v + _fbm((N, N), rng, N / 3.5, N * 0.09)
    band = (v / (N * P.get("bed", 0.075))) % 1.0
    idx = np.floor(v / (N * P.get("bed", 0.075))).astype(int)
    tone = (np.sin(idx * 12.9898) * 43758.5453) % 1.0
    rgb = _grad(np.clip(tone * 0.75 + 0.25 * band, 0, 1),
                [(0.0, P["dark"]), (0.5, P["base"]), (1.0, P["lit"])])
    rgb[band < 0.07] = P.get("seam", P["dark"])            # bedding plane
    edge = _dist_in(mask, N * 0.06) < N * 0.018
    rgb[edge] = np.array(P.get("scarp", P["lit"]), "float32")
    return rgb, np.full(mask.shape, float(P.get("alpha", 196)), "float32")


def t_masonry(mask, rng, P):
    """Made, not grown: flat roof planes and slabs, panel seams on a rectilinear grid
    aligned to the structure itself, oxidised where the weather gets in."""
    N = mask.shape[0]
    gy, gx = np.mgrid[0:N, 0:N].astype("float32")
    ang = _axis(mask)
    u = gx * np.cos(ang) + gy * np.sin(ang)
    v = -gx * np.sin(ang) + gy * np.cos(ang)
    p = P.get("panel", 0.085) * N
    cell_u, cell_v = np.floor(u / p), np.floor(v / p)
    h = (np.sin(cell_u * 12.9898 + cell_v * 78.233) * 43758.5) % 1.0
    rgb = _grad(h, [(0.0, P["dark"]), (0.5, P["base"]), (1.0, P["lit"])])
    seam = ((u % p) < p * 0.07) | ((v % p) < p * 0.07)
    rgb[seam] = P.get("seam", P["dark"])
    rust = _fbm((N, N), rng, N / 6.0, 1.0) > 0.42
    rgb[rust] = np.array(P.get("rust", P["dark"]), "float32")
    lip = _dist_in(mask, N * 0.05) < N * 0.012
    rgb[lip] = np.array(P.get("lit", P["lit"]), "float32")
    return rgb, np.full(mask.shape, float(P.get("alpha", 210)), "float32")


def t_organic(mask, rng, P):
    """Alive, or lately so: wet radial folds converging on a maw, gullet-dark at the
    centre and blooming to raw membrane at the rim."""
    N = mask.shape[0]
    ys, xs = np.nonzero(mask)
    cy, cx = ys.mean(), xs.mean()
    gy, gx = np.mgrid[0:N, 0:N].astype("float32")
    r = np.hypot(gy - cy, gx - cx)
    th = np.arctan2(gy - cy, gx - cx)
    R = max(np.sqrt(mask.sum() / np.pi), 1)
    folds = 0.5 + 0.5 * np.sin(P.get("folds", 11) * th + 2.0 * _noise((N, N), rng, N / 6, 1.0))
    t = np.clip(r / R, 0, 1) * (0.75 + 0.25 * folds)
    rgb = _grad(t, [(0.0, P["dark"]), (0.45, P["base"]), (1.0, P["lit"])])
    wet = _fbm((N, N), rng, N / 8.0, 1.0) > 0.46
    rgb[wet] = np.array(P.get("sheen", P["lit"]), "float32")
    return rgb, np.full(mask.shape, float(P.get("alpha", 212)), "float32")


def t_lava(mask, rng, P):
    """Chilled black crust cracked open over incandescent rock: the glow lives in thin
    branching veins and in the shear zones, never as a flat orange fill."""
    N = mask.shape[0]
    v = _fbm((N, N), rng, N / 4.0, 1.0, octaves=4)
    veins = np.abs(v) < P.get("vein_w", 0.055)
    hot = np.abs(v) < P.get("vein_w", 0.055) * 0.45
    rgb = np.zeros(mask.shape + (3,), "float32")
    rgb[:] = P["dark"]
    crust = _fbm((N, N), rng, N / 9.0, 1.0) > 0.5
    rgb[crust] = P["base"]
    rgb[veins] = P["lit"]
    rgb[hot] = P.get("glint", P["lit"])
    a = np.full(mask.shape, float(P.get("alpha", 214)), "float32")
    a[veins] = 240.0
    return rgb, a


def t_ice(mask, rng, P):
    """Frozen and fractured: pale blue-white facets meeting along straight shear lines,
    with a colder, denser core where the ice is thickest."""
    N = mask.shape[0]
    P2 = dict(P); P2.setdefault("plates", 14); P2.setdefault("seam_w", 0.006)
    P2["bloom"] = False
    rgb, a = t_crust(mask, rng, P2)
    dep = np.clip(_dist_in(mask, N * 0.22) / (N * 0.22), 0, 1)
    rgb = rgb * (1 - 0.30 * dep[..., None]) + np.array(P.get("core", P["base"]), "float32") * (0.30 * dep[..., None])
    return rgb, a


def t_canopy(mask, rng, P):
    """Living cover seen from orbit: clumped crowns of varying age, darker in the
    hollows where the canopy closes, with no straight line anywhere in it."""
    N = mask.shape[0]
    c = _fbm((N, N), rng, N / 9.0, 1.0, octaves=4)
    t = np.clip(0.5 + c, 0, 1)
    rgb = _grad(t, [(0.0, P["dark"]), (0.5, P["base"]), (1.0, P["lit"])])
    return rgb, np.full(mask.shape, float(P.get("alpha", 200)), "float32")


def t_channel(mask, rng, P):
    """Water's leftovers: braided threads running the length of the course, pale
    dried bar between them, aligned to the channel's own axis."""
    N = mask.shape[0]
    gy, gx = np.mgrid[0:N, 0:N].astype("float32")
    ang = _axis(mask)
    v = -gx * np.sin(ang) + gy * np.cos(ang)
    v = v + _fbm((N, N), rng, N / 2.6, N * 0.10)
    band = (v / (N * P.get("braid", 0.05))) % 1.0
    t = np.abs(band - 0.5) * 2
    rgb = _grad(t, [(0.0, P.get("thread", P["dark"])), (0.45, P["base"]), (1.0, P["lit"])])
    return rgb, np.full(mask.shape, float(P.get("alpha", 200)), "float32")


TREATMENTS = {"crust": t_crust, "storm": t_storm, "ripples": t_ripples, "clasts": t_clasts,
              "pool": t_pool, "crater": t_crater, "strata": t_strata, "masonry": t_masonry,
              "organic": t_organic, "lava": t_lava, "ice": t_ice, "canopy": t_canopy,
              "channel": t_channel}


# ---------------------------------------------------------------- art direction
# One entry per landmark Ash'karr draws.  `prompt` is the brief -- material,
# orientation, alignment, palette, mood -- and it is the thing to argue with when an
# icon reads wrong.  `treat` and `p` are how it gets executed.
#
# The four oceanic icons (Bay, Peninsula, CoastalIsland, Archipelago) are deliberately
# ABSENT: they ship as pure white silhouettes so the engine can tint them the ocean's
# own colour, and painting them would break that tint.

def S(prompt, treat, **p):
    return {"prompt": " ".join(prompt.split()), "treat": treat, "p": p}


SPECS = {

# ---- salt, mud and dust -------------------------------------------------------
"VEE_SaltPlains": S("""A blinding playa crust seen from directly overhead. Break it into large
    irregular polygons and make the SEAMS THE BRIGHT PART -- brine wicks up the fissures and
    crystallises there, so the joints stand proud as ruffled white ridges while the plate interiors
    sit duller and faintly warm. Scatter crystal bloom clustered along the seams, never as even
    dots. Cold blue-white in the damp low spots. Words: caustic, bone-dry, glittering, alkali,
    blinding.""",
    "crust", base=(236, 236, 231), seam=(243, 243, 239), seam_lit=(254, 254, 252),
    damp=(214, 222, 226), bloom_col=(249, 249, 245), alpha=196, plates=11),

"DryLake": S("""The opposite reading to the salt pan, and the contrast is the point: cracked
    mud, so the SEAMS ARE DARK -- shrinkage cracks opening into shadow between curled plates of
    dried silt. Warm mid-brown, each plate a slightly different age and tone, edges of the larger
    plates lifting pale where they have peeled. No sparkle anywhere. Words: baked, curled,
    shrunken, silted, abandoned by water.""",
    "crust", base=(150, 122, 92), seam=(84, 64, 45), seam_lit=(70, 52, 36),
    damp=(133, 110, 84), plate_var=22, seam_w=0.011, bloom=False, alpha=198),

"VEE_DustBowl": S("""A dust storm caught mid-turn, from above. Two or three loose logarithmic
    spiral arms winding about an off-centre eye, broken up by turbulence so the curl reads as
    weather and never as a logo. Dense tan in the arms, thin enough between them that the ground
    shows through, with blown grit picked out bright along the leading edges. Words: scouring,
    ochre, airborne, blinding, restless.""",
    "storm", base=(190, 166, 120), lit=(233, 215, 177), dark=(146, 120, 82),
    glint=(246, 232, 199), alpha=214, alpha_lo=92),

"VEE_QuicksandDunes": S("""Treacherous ground pretending to be ordinary dune field. Pale sulphur-
    cream bedforms lying across the wind, but slack and rounded rather than crisp, with darker
    saturated hollows between crests where the sand is holding water. Crests aligned across the
    landform's long axis. Words: soft, waterlogged, deceitful, sallow, unset.""",
    "ripples", base=(206, 196, 133), lit=(232, 226, 170), dark=(150, 141, 88),
    wave=0.17, sinuosity=0.17, alpha=198),

"AB_QuicksandPits": S("""Discrete sink pits rather than a field: each one a slack cream-grey
    disc darkening steeply to a saturated throat, with a wet collar where the sand has slumped
    inward. Nothing about it should look firm. Words: slumping, sodden, throat, quiet, hungry.""",
    "pool", base=(178, 166, 122), lit=(214, 205, 162), dark=(104, 95, 66),
    shore=(226, 218, 182), alpha=200),

# ---- sand and stone -----------------------------------------------------------
"Dunes": S("""A barchan dune field from orbit. Long low stoss slopes rising to a sharp lee break
    -- an asymmetric wave, not a sine -- laid ACROSS the prevailing wind, aligned to the field's
    own long axis. Warm apricot sand, the crests catching light, the troughs holding a cooler
    shadow. Words: migrating, wind-combed, sinuous, sun-warmed.""",
    "ripples", base=(214, 168, 118), lit=(243, 210, 165), dark=(163, 120, 79),
    wave=0.13, sinuosity=0.12, alpha=204),

"VEE_PebbleDunes": S("""Sand that has run out of sand. The same wind-laid bedforms as an open
    dune field, but with a lag of small dark pebbles left standing on the crests where the fines
    have blown away -- a stony sheen over a pale ground. Words: winnowed, gritty, armoured,
    lag-strewn.""",
    "ripples", base=(198, 186, 158), lit=(226, 217, 193), dark=(146, 135, 110),
    wave=0.12, sinuosity=0.10, clast=0.0022, clast_col=(96, 88, 74), alpha=198),

"VEE_RedDesert": S("""Iron-stained sand at its most saturated. Deep oxide red bedforms with an
    almost violet shadow in the troughs and a hot, bright rust on the crests -- the colour of a
    place that rusted rather than weathered. Words: ferrous, oxidised, smouldering, ancient.""",
    "ripples", base=(158, 84, 60), lit=(206, 122, 84), dark=(104, 52, 40),
    wave=0.15, sinuosity=0.14, alpha=206),

"VEE_GravelBeach": S("""A bed of loose water-rounded clasts, each stone its own tone, packed
    edge to edge with dark shadow in the interstices. Read as GRANULAR: the eye should be able to
    count individual stones at full size and see texture at map size. Cool grey-buff, faintly
    damp. Words: rattling, sorted, water-rolled, shingle.""",
    "clasts", base=(178, 170, 152), lit=(214, 208, 192), dark=(118, 112, 98),
    seam=(78, 74, 64), stones=140, alpha=200),

"VEE_JaggedRocks": S("""Shattered, unweathered rock -- angular blades and shards standing at
    every angle, nothing rounded, hard shadow on the lee faces. Cold slate grey with a bluish
    cast where the fresh fracture shows. Words: splintered, knife-edged, frost-riven, brutal.""",
    "clasts", base=(138, 138, 144), lit=(184, 186, 194), dark=(78, 78, 86),
    seam=(44, 44, 50), stones=60, alpha=206),

"VEE_StoneForest": S("""A karst pinnacle field: tall isolated stone towers seen from directly
    above, so each reads as a bright cap with a deep shadow moat around it. Pale weathered
    limestone, cream to grey. Words: fluted, tapering, cathedral, silent.""",
    "clasts", base=(186, 178, 160), lit=(228, 222, 206), dark=(96, 92, 82),
    seam=(56, 54, 48), stones=45, alpha=206),

# ---- relief -------------------------------------------------------------------
"Cliffs": S("""Bedded rock cut by a scarp. Layers run parallel to the landform's own strike, each
    bed a different age and tone, with a hard bright lip along the exposed edge where the light
    catches and shadow immediately below it. Warm sandstone browns over a cooler basement. Words:
    stratified, sheer, layered, sun-struck.""",
    "strata", base=(150, 118, 82), lit=(206, 176, 132), dark=(94, 72, 50),
    seam=(66, 50, 34), scarp=(224, 200, 160), bed=0.075, alpha=198),

"Valley": S("""Two facing slopes and a floor between them. Bedding runs along the valley axis;
    the flanks step down in tonal bands to a darker, flatter floor, one flank lit and the other
    held in shadow. Words: incised, flanking, sheltered, graded.""",
    "strata", base=(146, 116, 84), lit=(198, 168, 128), dark=(88, 68, 48),
    seam=(62, 48, 34), scarp=(212, 188, 150), bed=0.10, alpha=196),

"VEE_RockRidge": S("""A single hard spine standing above softer ground. Strata run the length of
    the ridge, tightest and brightest along the crest line, falling away into shadow on both
    flanks. Dry grey-brown, unvegetated. Words: resistant, keeled, backbone, wind-scoured.""",
    "strata", base=(140, 124, 100), lit=(196, 182, 156), dark=(82, 72, 58),
    seam=(54, 48, 38), scarp=(214, 202, 178), bed=0.055, alpha=198),

"Plateau": S("""A flat-topped mesa: an even, bright, almost featureless cap of hard rock ringed
    by a stepped scarp dropping into shadow. The top should read as CALM and the edge as abrupt.
    Words: tabular, capped, abrupt, elevated.""",
    "strata", base=(158, 132, 100), lit=(210, 186, 148), dark=(92, 74, 54),
    seam=(66, 52, 38), scarp=(226, 206, 172), bed=0.16, alpha=200),

"Chasm": S("""A rift with no visible bottom. Near-black in the throat, walls stepping up through
    cold greys in tight bedded bands, a thin bright lip where the light just reaches the rim.
    Words: bottomless, fractured, cold, vertiginous.""",
    "strata", base=(84, 82, 86), lit=(142, 140, 146), dark=(28, 28, 32),
    seam=(18, 18, 22), scarp=(178, 176, 182), bed=0.045, alpha=210),

"VEE_SerpentineCanyons": S("""A maze of narrow winding slot canyons. Bright rims and floors
    threaded by dark sinuous cuts that follow the landform's own meander, never straight. Warm
    desert varnish on the rock. Words: labyrinthine, slotted, meandering, shaded.""",
    "channel", base=(168, 132, 94), lit=(216, 186, 144), dark=(70, 52, 36),
    thread=(52, 38, 26), braid=0.045, alpha=202),

"Cavern": S("""A mouth in the ground seen from above: a bright rock collar falling steeply into
    a dark void, with the void taking most of the area. The interior should read as ABSENCE, not
    as a dark colour. Words: yawning, hollow, cool, unlit.""",
    "crater", base=(126, 112, 92), lit=(198, 182, 156), dark=(30, 28, 26),
    floor=(46, 42, 38), alpha=208),

"Hollow": S("""A shallow closed depression. A soft bright rim, a gently graded inner slope, a
    flat floor a shade darker and warmer than the surrounding ground. Nothing sheer. Words:
    scooped, gentle, sheltered, sun-trapped.""",
    "crater", base=(160, 138, 106), lit=(212, 194, 160), dark=(104, 88, 66),
    floor=(134, 114, 86), alpha=194),

"VEE_MeteorCrater": S("""An impact structure: a raised rim catching hard light, a steep shadowed
    inner wall, a flat floor of shocked debris, and the ground outside faintly bruised by ejecta.
    Concentric but never circular. Words: shocked, ramparted, violent, glassy.""",
    "crater", base=(140, 124, 104), lit=(210, 194, 166), dark=(62, 54, 46),
    floor=(108, 96, 82), alpha=204),

"LavaCrater": S("""A vent that has cooled. Black chilled crust cracked over incandescent rock,
    the glow surviving only in thin branching veins and down in the throat. Words: quenched,
    fissured, glowing, sullen.""",
    "lava", base=(72, 56, 52), lit=(232, 122, 44), dark=(34, 28, 28),
    glint=(255, 206, 108), vein_w=0.06, alpha=216),

"VEE_ToxicCrater": S("""A crater that has gone wrong. Sickly yellow-green residue pooled in the
    floor and crusted up the inner wall, a bleached dead rim, and a faint bloom of contamination
    on the ground outside. Words: leached, acrid, stained, quarantined.""",
    "crater", base=(126, 138, 82), lit=(186, 198, 132), dark=(52, 62, 38),
    floor=(96, 118, 62), alpha=206),

"TerraformingScar": S("""Machine work, not weather. A spiral trench cut into the ground in
    regular passes, the spoil banked bright along one side of every pass and the cut itself in
    shadow -- the only landform on the planet with a repeating, deliberate rhythm. Words:
    industrial, ploughed, geometric, unfinished.""",
    "crater", base=(132, 122, 112), lit=(196, 188, 176), dark=(66, 62, 58),
    floor=(104, 98, 92), alpha=204),

"AncientQuarry": S("""A stepped excavation. Benches cut in regular terraces down to a flat
    floor, each bench face bright and each tread in shadow, with pale crushed spoil at the lip.
    Words: benched, cut, abandoned, dusty.""",
    "strata", base=(158, 148, 132), lit=(214, 206, 190), dark=(88, 82, 72),
    seam=(58, 54, 48), scarp=(230, 224, 210), bed=0.07, alpha=204),

"VEE_AlluvialFan": S("""Sediment spilling out of a mountain front and spreading. Distributary
    threads radiating downslope from a single apex, coarse and bright at the head, fining and
    darkening toward the toe. Aligned to the fan's own axis. Words: spreading, graded, braided,
    outwash.""",
    "channel", base=(178, 156, 122), lit=(222, 206, 176), dark=(114, 98, 76),
    thread=(140, 122, 96), braid=0.055, alpha=198),

# ---- water and what is left of it ---------------------------------------------
"VEE_DryRiver": S("""A watercourse with the water taken out. Braided pale threads of sorted sand
    running the LENGTH of the course, dark abandoned channels between them, everything aligned to
    the river's own meander. Words: braided, stranded, bleached, ghost-course.""",
    "channel", base=(172, 148, 112), lit=(218, 202, 172), dark=(104, 86, 64),
    thread=(88, 72, 54), braid=0.05, alpha=196),

"Oasis": S("""The one green thing for a hundred miles. Deep still water at the centre, a bright
    mineral shore ring, and a dense dark band of palm and reed crowding the margin. The contrast
    between the water and the desert around it is the entire read. Words: fed, shaded, precious,
    improbable.""",
    "pool", base=(56, 92, 108), lit=(112, 146, 96), dark=(30, 54, 70),
    shore=(196, 178, 118), scum=0.34, scum_col=(84, 122, 74), alpha=214),

"VEE_StagnantRivulet": S("""Water that has stopped moving and knows it. Flat olive-green,
    skinned over with algal scum in irregular rafts, no reflection, a dark saturated margin where
    the mud is always wet. Words: brackish, skinned, motionless, fetid.""",
    "pool", base=(96, 116, 74), lit=(140, 158, 102), dark=(52, 66, 42),
    shore=(120, 118, 82), scum=0.30, scum_col=(158, 176, 116), alpha=206),

"VEE_Cenotes": S("""Collapse sinkholes flooded with groundwater. A hard bright limestone collar
    dropping abruptly to water of an intense, almost unreal blue that darkens fast with depth.
    The abruptness of the edge is the point. Words: sheer, sapphire, cold, fathomless.""",
    "pool", base=(38, 96, 132), lit=(96, 168, 196), dark=(14, 44, 72),
    shore=(206, 196, 168), alpha=216),

"VEE_SulfuricLake": S("""Mineral water at its most poisonous. Acid yellow-green shallows banded
    into a hotter core, ringed by a crust of sulphur precipitate so pale it looks bleached. Words:
    acrid, precipitated, luminous, corrosive.""",
    "pool", base=(178, 176, 74), lit=(226, 220, 122), dark=(112, 108, 44),
    shore=(232, 224, 168), scum=0.40, scum_col=(240, 232, 150), alpha=212),

"ToxicLake": S("""Runoff that never drained. Dense opaque green, darkening steeply toward the
    middle, with a dead bleached margin where nothing will grow and an oily film catching light in
    slicks. Words: opaque, chemical, still, poisoned.""",
    "pool", base=(74, 108, 76), lit=(120, 156, 112), dark=(34, 56, 40),
    shore=(146, 148, 118), scum=0.42, scum_col=(126, 168, 118), alpha=214),

"AB_TarLakes": S("""Cold asphalt pooled in a hollow. Near-black, viscous, with a dull sheen
    rather than a reflection and a sticky crusted margin where dust has blown onto the surface.
    Words: viscous, sucking, lightless, slow.""",
    "pool", base=(36, 32, 32), lit=(72, 66, 62), dark=(16, 14, 14),
    shore=(104, 92, 76), scum=0.46, scum_col=(58, 52, 48), alpha=222),

"AB_MagmaticQuagmire": S("""Ground that has half melted. Black chilled crust broken into rafts
    floating on incandescent rock, the glow bleeding up through every crack and widening where the
    rafts have pulled apart. Words: molten, foundering, radiant, unstable.""",
    "lava", base=(66, 50, 46), lit=(238, 116, 38), dark=(28, 24, 24),
    glint=(255, 214, 122), vein_w=0.075, alpha=220),

"LavaLake": S("""An open lake of molten rock. A thin dark skin constantly tearing apart to show
    the orange beneath, brightest at the centre where the convection rises, with a hard black
    levee at the shore. Words: churning, incandescent, skinned, seething.""",
    "lava", base=(78, 58, 50), lit=(244, 132, 44), dark=(30, 24, 22),
    glint=(255, 224, 140), vein_w=0.085, alpha=222),

"HotSprings": S("""Mineral terraces built by hot water. Concentric rimstone pools stepping
    downhill, each holding water of a different temperature and therefore a different colour --
    white-hot centre through turquoise to a rusty bacterial fringe. Words: terraced, steaming,
    depositing, banded.""",
    "pool", base=(96, 168, 172), lit=(206, 226, 222), dark=(46, 108, 118),
    shore=(202, 150, 92), scum=0.38, scum_col=(226, 236, 232), alpha=212),

"Basin": S("""A closed lowland holding what little water reaches it. A broad pale evaporite
    margin grading inward to a shallow blue-grey centre; the gradient should be gentle everywhere.
    Words: enclosed, evaporating, shallow, patient.""",
    "pool", base=(96, 116, 132), lit=(158, 174, 182), dark=(58, 74, 90),
    shore=(196, 184, 152), alpha=204),

# ---- structures ---------------------------------------------------------------
"Ruins": S("""Concrete that outlived its city. Broken slabs and stubs of wall lying at angles,
    flat grey planes with a hard shadow on one side of each, panel seams still visible where the
    formwork was, rust bleeding from the reinforcement. Words: fallen, spalled, rectilinear,
    outlasted.""",
    "masonry", base=(140, 138, 136), lit=(190, 188, 186), dark=(80, 78, 78),
    seam=(52, 50, 50), rust=(126, 100, 82), panel=0.085, alpha=210),

"AncientGarrison": S("""A hardened military post. Heavy armoured plate, flat roof planes on a
    strict rectilinear grid aligned to the structure, deep seams between panels, and a cold
    gun-metal cast under the dust. Words: fortified, armoured, deliberate, shut.""",
    "masonry", base=(120, 124, 126), lit=(168, 172, 176), dark=(66, 70, 72),
    seam=(40, 42, 44), rust=(112, 88, 70), panel=0.075, alpha=214),

"AncientWarehouse": S("""Storage at industrial scale. Long uniform roof bays with ribbed panel
    lines running one way only, a lighter weathered sheen along the ridge, corrosion streaking
    down from every seam. Words: cavernous, ribbed, utilitarian, corroding.""",
    "masonry", base=(146, 142, 132), lit=(196, 192, 182), dark=(84, 82, 76),
    seam=(50, 48, 44), rust=(138, 100, 70), panel=0.11, alpha=212),

"AncientChemfuelRefinery": S("""Process plant. Cylindrical tank tops and pipe runs, flat oily
    greys shot through with heavy rust, dark stains spreading from the tank bases where something
    leaked and was never cleaned up. Words: petrochemical, stained, tangled, shut down.""",
    "masonry", base=(124, 120, 114), lit=(172, 168, 160), dark=(70, 66, 62),
    seam=(42, 40, 38), rust=(150, 92, 54), panel=0.065, alpha=214),

"AncientLaunchSite": S("""A pad built for one enormous departure. Vast flat blast-scoured
    concrete aprons, a few heavy structures, scorch blackening radiating from the centre. Words:
    scorched, monumental, abandoned mid-purpose.""",
    "masonry", base=(150, 148, 144), lit=(198, 196, 192), dark=(74, 72, 70),
    seam=(46, 44, 44), rust=(96, 82, 74), panel=0.12, alpha=212),

"AncientHeatVent": S("""Deep machinery still running. Grilled vent housings in dull alloy with
    a hot glow escaping between the louvres, aligned to the housing, and the ground around them
    bleached by decades of exhaust. Words: humming, louvred, thermal, still-powered.""",
    "masonry", base=(118, 116, 118), lit=(206, 148, 84), dark=(58, 56, 58),
    seam=(36, 34, 36), rust=(170, 104, 52), panel=0.06, alpha=216),

"FrozenRuins": S("""The same fallen concrete, taken by ice. Slabs glazed and rounded under old
    snowpack, seams filled white, everything shifted toward cold blue-grey with a hard glare on
    the upper faces. Words: glazed, entombed, blue-shadowed, silent.""",
    "masonry", base=(176, 186, 196), lit=(226, 234, 240), dark=(104, 116, 130),
    seam=(74, 86, 100), rust=(150, 160, 172), panel=0.09, alpha=210),

"AbandonedColonyTribal": S("""A settlement built from what was to hand. Thatch and timber roofs
    in warm organic browns, irregular rather than gridded, weathered pale on the weather side,
    already half returning to the ground. Words: woven, sun-bleached, humble, reclaimed.""",
    "masonry", base=(148, 116, 78), lit=(200, 172, 128), dark=(88, 66, 44),
    seam=(58, 42, 28), rust=(132, 98, 62), panel=0.055, alpha=206),

"AbandonedColonyOutlander": S("""A frontier town left standing. Prefab roofs and sheet siding in
    faded paint colours, laid out on a loose grid, sun-faded on top and rust-streaked below. Words:
    prefabricated, faded, orderly, emptied.""",
    "masonry", base=(150, 140, 124), lit=(200, 192, 176), dark=(88, 82, 72),
    seam=(54, 50, 44), rust=(146, 96, 66), panel=0.07, alpha=208),

# ---- alive, or lately so ------------------------------------------------------
"VEE_FleshPits": S("""Something biological has taken the ground. Wet radial folds of raw
    membrane converging on dark gullet openings, gullet-dark at the centre and blooming to angry
    pink at the rim, with a sheen that says WET. Words: peristaltic, raw, glistening, wrong.""",
    "organic", base=(178, 92, 96), lit=(224, 148, 148), dark=(72, 30, 36),
    sheen=(238, 176, 172), folds=13, alpha=216),

"sw_Sarlacc": S("""A living pit predator seen from above. A ring of inward-curving barbs around
    a beaked maw, folds of leathery hide radiating outward and sand drifted against them, the
    throat black and bottomless. Words: barbed, patient, cavernous, waiting.""",
    "organic", base=(154, 122, 88), lit=(202, 176, 138), dark=(22, 18, 16),
    sheen=(216, 194, 156), folds=15, alpha=218),

"sw_DeadSarlacc": S("""The same creature, long dead. Hide gone grey and papery, folds collapsed
    inward, barbs snapped and bleached, sand filling the throat -- everything that was wet in the
    live one now dry. Words: desiccated, collapsed, bleached, hollow.""",
    "organic", base=(160, 152, 136), lit=(206, 200, 186), dark=(84, 78, 70),
    sheen=(220, 214, 200), folds=15, alpha=204),
}


# ---------------------------------------------------------------- the painter

def _source_cells(path, atlas):
    """Silhouettes from a shipping icon, at CELL*SS.  The mask is LIFTED, never
    invented, so layout and footprint stay byte-compatible with the def's atlasSize."""
    im = Image.open(path).convert("RGBA")
    ax, ay = atlas
    w, h = im.size[0] // ax, im.size[1] // ay
    out = []
    for y in range(ay):
        for x in range(ax):
            a = im.crop((x * w, y * h, (x + 1) * w, (y + 1) * h)).getchannel("A")
            a = a.resize((CELL * SS, CELL * SS), Image.LANCZOS)
            a = a.filter(ImageFilter.GaussianBlur(SS * 0.8))
            out.append(np.asarray(a) > 120)
    return out


def paint(name, src_path, atlas, out_path):
    spec = SPECS[name]
    fn = TREATMENTS[spec["treat"]]
    ax, ay = atlas
    sheet = Image.new("RGBA", (CELL * ax, CELL * ay), (0, 0, 0, 0))
    for i, mask in enumerate(_source_cells(src_path, atlas)):
        x, y = i % ax, i // ax
        if mask.sum() < 200:
            continue
        rng = np.random.default_rng(abs(hash((name, i))) % (2 ** 32))
        rgb, a = fn(mask, rng, spec["p"])
        a = np.broadcast_to(np.asarray(a, "float32"), mask.shape).copy()
        inner = _erode(mask, OUTLINE_PX * SS)
        a = np.where(inner, a, 208.0)
        rgb = rgb.copy()
        rgb[mask & ~inner] = spec["p"].get("rim", (0, 0, 0))   # Ludeon's hard rim
        a[~mask] = 0
        rgb[~mask] = 0
        cell = Image.fromarray(np.dstack([rgb, a]).clip(0, 255).astype("uint8"), "RGBA")
        cell = cell.resize((CELL, CELL), Image.LANCZOS)
        ca = np.array(cell)
        ca[..., 3][ca[..., 3] < 26] = 0        # kill the LANCZOS fringe; see landmark_icon_paint
        sheet.paste(Image.fromarray(ca, "RGBA"), (x * CELL, y * CELL))
    sheet.save(out_path)
    return out_path


def paint_all(dest, only=None):
    import landmark_icon_sheet as L
    defs, idx = L.landmark_defs(), L.texture_index()
    os.makedirs(dest, exist_ok=True)
    done, skipped = [], []
    for name in (only or SPECS):
        d = defs.get(name)
        key = (d["icon"] if d else f"World/Landmarks/{name}").lower()
        src = idx.get(key)
        if not src:
            skipped.append((name, f"no texture for {key}")); continue
        atlas = (d or {}).get("atlas") or (2, 2)
        try:
            paint(name, src, atlas, f"{dest}/{name}.png")
            done.append(name)
        except Exception as e:                                  # noqa: BLE001
            skipped.append((name, f"{type(e).__name__}: {e}"))
    return done, skipped


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    dest = sys.argv[1]
    only = sys.argv[2:] or None
    done, skipped = paint_all(dest, only)
    print(f"painted {len(done)}")
    for n, why in skipped:
        print(f"  SKIP {n}: {why}")
