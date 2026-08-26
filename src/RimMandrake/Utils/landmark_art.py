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
import zlib

import numpy as np
from PIL import Image, ImageFilter

SS = 2
CELL = 512                    # 1024x1024 per file, 2x2 atlas -- 4x Ludeon's density
OUTLINE_PX = 3.0


# ---------------------------------------------------------------- shared machinery

def _seed(name, i):
    """zlib.crc32, NOT hash().  Python salts string hashing per process (PYTHONHASHSEED),
    so hash((name, i)) hands back a different number every run -- which silently rerolled
    every icon's four variants on each regeneration and threw away art that had already
    been approved.  This is the whole reason the output is reproducible at all."""
    return zlib.crc32(f"{name}/{i}".encode()) & 0xFFFFFFFF


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
    # The eye is where a log-spiral betrays itself: every arm converges on one point and
    # the result reads as a pinwheel logo.  Two defences, and BOTH are needed -- floor the
    # radius well out so log() stops steepening, and scale turbulence UP toward the centre
    # so the convergence is torn apart exactly where it would otherwise be sharpest.
    r = np.maximum(np.hypot(gy - cy, gx - cx) + _noise((N, N), rng, N / 3.5, N * 0.10),
                   N * P.get("eye", 0.13))
    th = np.arctan2(gy - cy, gx - cx)
    arms = P.get("arms", 2)
    twist = (1.15 + 0.55 * rng.random()) * (1 if rng.random() < 0.5 else -1)
    ph = arms * (th + twist * np.log(r))
    # keep this modest: crank it and the arms themselves dissolve into a soft blob,
    # which is a worse failure than the pinwheel it was added to cure
    near = 1.0 + P.get("break_eye", 1.4) * np.exp(-np.hypot(gy - cy, gx - cx) / (N * 0.16))
    ph += near * (1.3 * _noise((N, N), rng, N / 5.5, 1.0) + 0.7 * _noise((N, N), rng, N / 13, 1.0))
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
        # correlated to t, because a lag deposit sits on the crest where the wind stripped
        # the fines -- scattered mask-wide it is just a uniform dot field, the classic tell
        sp = (rng.random(mask.shape) < P["clast"]) & (t > P.get("clast_from", 0.62))
        sp = np.asarray(Image.fromarray((sp * 255).astype("uint8"))
                        .filter(ImageFilter.MaxFilter(2 * int(P.get("clast_px", 0.006) * N) + 1))) > 128
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
    # warp harder than feels necessary: an unwarped Voronoi has DEAD STRAIGHT seams and
    # reads as crazy paving, which is the opposite of water-rounded
    wy = gy + _fbm((N, N), rng, N / 7, N * P.get("round", 0.045))
    wx = gx + _fbm((N, N), rng, N / 7, N * P.get("round", 0.045))
    d = (wy[..., None] - pts[:, 0]) ** 2 + (wx[..., None] - pts[:, 1]) ** 2
    lab = d.argmin(2)
    near = np.sort(d, 2)[..., :2]
    seam = np.sqrt(near[..., 1]) - np.sqrt(near[..., 0])
    rgb = np.zeros(mask.shape + (3,), "float32")
    base, lit, dark = (np.array(P[k], "float32") for k in ("base", "lit", "dark"))
    for i in range(len(pts)):
        f = rng.random()
        rgb[lab == i] = base + (lit - base) * f if f > 0.5 else base + (dark - base) * (1 - 2 * f)
    a = np.full(mask.shape, float(P.get("alpha", 198)), "float32")
    moat = P.get("moat", 0.0)
    if moat:
        # isolate each clast in its own shadow, so a pinnacle field reads as separate
        # towers rather than as one tessellated rubble bed
        m = seam < N * moat
        rgb[m] = P.get("moat_col", (32, 30, 28))
        a[m] = float(P.get("alpha", 198)) + 26
    rgb[seam < N * 0.0035] = P.get("seam", P["dark"])
    return rgb, a


def t_pool(mask, rng, P):
    """Standing liquid: colour deepens away from the shore, with a wet margin and a
    slack, unlit surface.  Depth is normalised to THIS pool's own radius, not to the
    canvas -- a fixed cap leaves every small or thin pool stalled in shore tones, which
    is why the tar lakes came out grey instead of black."""
    N = mask.shape[0]
    R = max(np.sqrt(mask.sum() / np.pi), 4.0)
    cap = max(N * 0.05, R * P.get("reach", 0.85))
    dep = np.clip(_dist_in(mask, cap) / cap, 0, 1)
    dep = np.clip(dep + _fbm((N, N), rng, N / 4.0, P.get("rough", 0.16)), 0, 1)
    if P.get("terrace"):
        # rimstone: hot water depositing in stepped pools, each step its own temperature
        k = P["terrace"]
        dep = np.floor(dep * k) / (k - 1)
        dep = np.clip(dep, 0, 1)
    rgb = _grad(dep, [(0.0, P.get("shore", P["lit"])), (0.22, P["lit"]),
                      (0.60, P["base"]), (1.0, P["dark"])])
    if P.get("scum", 0):
        s_ = _fbm((N, N), rng, N / 7.0, 1.0)
        m = (s_ > P["scum"]) & (dep > P.get("scum_from", 0.10)) & (dep < P.get("scum_to", 1.01))
        rgb[m] = P.get("scum_col", P["lit"])
    a = float(P.get("alpha", 206)) - 26 * (1 - dep)
    return rgb, a.astype("float32")


def t_crater(mask, rng, P):
    """An impact or collapse: raised rim catching the light, shadowed inner wall, flat
    floor.  Concentric about the mark's own centroid -- and concentric is EXACTLY the
    procedural tell here, so the radius is both noise-warped and lobed by a few angular
    harmonics.  A ring-shaped silhouette needs the strongest warp of all, because the
    source outline is already a circle and a weak warp leaves a dartboard."""
    N = mask.shape[0]
    ys, xs = np.nonzero(mask)
    cy, cx = ys.mean(), xs.mean()
    gy, gx = np.mgrid[0:N, 0:N].astype("float32")
    th = np.arctan2(gy - cy, gx - cx)
    lobe = np.zeros(mask.shape, "float32")
    for k in (2, 3, 5):
        lobe += (P.get("lobe", 0.13) / k) * np.sin(k * th + rng.uniform(0, 6.283))
    r = np.hypot(gy - cy, gx - cx) * (1.0 + lobe) + _fbm((N, N), rng, N / 4.0, N * P.get("warp", 0.11))
    R = max(np.sqrt(mask.sum() / np.pi), 1)
    t = np.clip(r / R, 0, 1.4)
    if P.get("rings"):
        # machine work, not weather: regular passes cut into the ground, spoil banked
        # bright on one side of every pass
        t = t + P.get("rings_amp", 0.22) * np.sin(r / (N * P["rings"]) * 6.283)
    rgb = _grad(np.clip(t / 1.2, 0, 1),
                [(0.0, P["dark"]), (0.42, P.get("floor", P["base"])),
                 (0.66, P["base"]), (0.80, P["lit"]), (1.0, P["dark"])])
    a = np.full(mask.shape, float(P.get("alpha", 202)), "float32")
    core = P.get("core")
    if core:
        # a crater is a rim AND what is lying in the bottom of it; painting the floor with
        # a second treatment is the only way to get lava or standing water inside a wall
        cm = mask & (t < core.get("r", 0.55))
        if cm.sum() > 200:
            crgb, ca = TREATMENTS[core["treat"]](cm, rng, core)
            ca = np.broadcast_to(np.asarray(ca, "float32"), mask.shape)
            rgb[cm], a[cm] = crgb[cm], ca[cm]
    return rgb, a


def t_strata(mask, rng, P):
    """Bedded rock seen from above: layers exposed along the scarp, running parallel to
    the landform's own strike, each bed a slightly different age and tone."""
    N = mask.shape[0]
    gy, gx = np.mgrid[0:N, 0:N].astype("float32")
    ang = _axis(mask) + P.get("skew", 0.0)
    v = -gx * np.sin(ang) + gy * np.cos(ang)
    v = v + _fbm((N, N), rng, N / 3.5, N * 0.09)
    # bed width scales with the LANDFORM, not the canvas.  A constant spacing puts three
    # or four alternating bands across a narrow ridge, which reads as a barber pole.
    span = max(mask.sum() ** 0.5, 8.0)
    bw = max(N * 0.02, span * P.get("bed", 0.075) * 2.2)
    band = (v / bw) % 1.0
    idx = np.floor(v / bw).astype(int)
    tone = (np.sin(idx * 12.9898) * 43758.5453) % 1.0
    rgb = _grad(np.clip(tone * 0.75 + 0.25 * band, 0, 1),
                [(0.0, P["dark"]), (0.5, P["base"]), (1.0, P["lit"])])
    rgb[band < 0.07] = P.get("seam", P["dark"])            # bedding plane
    if P.get("floor"):
        # a valley is two flanks and a floor, which uniform bedding cannot express:
        # darken toward the shape's own centreline
        u2 = gx * np.cos(ang) + gy * np.sin(ang)
        ys2, xs2 = np.nonzero(mask)
        mid = (-xs2 * np.sin(ang) + ys2 * np.cos(ang)).mean()
        w = np.clip(np.abs(v - mid) / (span * 0.55), 0, 1)
        rgb = rgb * w[..., None] + np.array(P["floor"], "float32") * (1 - w[..., None])
    edge = _dist_in(mask, N * 0.06) < N * 0.018
    rgb[edge] = np.array(P.get("scarp", P["lit"]), "float32")
    return rgb, np.full(mask.shape, float(P.get("alpha", 196)), "float32")


def t_masonry(mask, rng, P):
    """Made, not grown: flat roof planes and slabs, panel seams on a rectilinear grid
    aligned to the structure itself, oxidised where the weather gets in.

    Two scale traps live here.  The rust field must be sized to the MARK, not the canvas
    -- an fbm lobe wider than a small housing swallows it whole and the piece renders as
    one solid orange blot.  And seams on both axes always read as a checkerboard, so a
    long-span roof wants `ribs` and its one direction only."""
    N = mask.shape[0]
    gy, gx = np.mgrid[0:N, 0:N].astype("float32")
    ang = _axis(mask)
    u = gx * np.cos(ang) + gy * np.sin(ang)
    v = -gx * np.sin(ang) + gy * np.cos(ang)
    span = max(mask.sum() ** 0.5, 8.0)
    p_ = max(N * 0.02, span * P.get("panel", 0.085) * 1.9)
    cu, cv = np.floor(u / p_), np.floor(v / p_)
    h = (np.sin(cu * 12.9898 + cv * 78.233) * 43758.5) % 1.0
    rgb = _grad(h, [(0.0, P["dark"]), (0.5, P["base"]), (1.0, P["lit"])])
    seam = ((v % p_) < p_ * 0.09) if P.get("ribs") else \
           (((u % p_) < p_ * 0.07) | ((v % p_) < p_ * 0.07))
    rgb[seam] = P.get("seam", P["dark"])
    rust = _fbm((N, N), rng, max(N / 14.0, span * 0.35), 1.0) > P.get("rust_amt", 0.46)
    rgb[rust & ~seam] = np.array(P.get("rust", P["dark"]), "float32")
    if P.get("scorch"):
        ys, xs = np.nonzero(mask)
        d0 = np.hypot(gy - ys.mean(), gx - xs.mean())
        # normalise to the mark's OWN extent, and cap the blend: span is sqrt(area) and
        # ran smaller than the true spread, so every pixel scored "centre" and the whole
        # launch site rendered near-black instead of scorched at the middle
        far = max(np.hypot(ys - ys.mean(), xs - xs.mean()).max(), 1.0)
        k = np.clip(d0 / far, 0, 1)[..., None]
        k = 1.0 - P.get("scorch_amt", 0.6) * (1.0 - k)
        rgb = rgb * k + np.array(P["scorch"], "float32") * (1 - k)
    lip = _dist_in(mask, N * 0.05) < N * 0.012
    rgb[lip] = np.array(P["lit"], "float32")
    return rgb, np.full(mask.shape, float(P.get("alpha", 210)), "float32")


def t_organic(mask, rng, P):
    """Alive, or lately so: wet folds converging on a maw, gullet-dark at the centre and
    blooming to raw membrane at the rim.  A single sin(n*theta) makes a FLOWER -- perfectly
    periodic petals -- so the folds are three harmonics at random phase plus noise, and the
    maw is a hard-edged irregular aperture rather than a gradient reaching a point."""
    N = mask.shape[0]
    ys, xs = np.nonzero(mask)
    cy, cx = ys.mean(), xs.mean()
    gy, gx = np.mgrid[0:N, 0:N].astype("float32")
    r = np.hypot(gy - cy, gx - cx)
    th = np.arctan2(gy - cy, gx - cx)
    R = max(np.sqrt(mask.sum() / np.pi), 1)
    n = P.get("folds", 11)
    f = np.zeros(mask.shape, "float32")
    for k, w in ((n, 1.0), (max(2, n // 2), 0.55), (max(3, int(n * 1.7)), 0.35)):
        f += w * np.sin(k * th + rng.uniform(0, 6.283))
    f = np.tanh(f * 0.8 + 1.6 * _noise((N, N), rng, N / 6, 1.0))
    t = np.clip(r / R, 0, 1) * (0.72 + 0.28 * (0.5 + 0.5 * f))
    t = np.clip((t - P.get("maw", 0.20)) / max(1e-3, 1 - P.get("maw", 0.20)), 0, 1)
    rgb = _grad(t, [(0.0, P["dark"]), (0.45, P["base"]), (1.0, P["lit"])])
    aperture = r < R * P.get("maw", 0.20) * (1.0 + 0.40 * np.sin(4 * th + rng.uniform(0, 6.283))
                                             + 0.6 * _noise((N, N), rng, N / 8, 1.0))
    rgb[aperture] = P.get("gullet", P["dark"])
    wet = _fbm((N, N), rng, N / 8.0, 1.0) > 0.46
    rgb[wet & ~aperture] = np.array(P.get("sheen", P["lit"]), "float32")
    a = np.full(mask.shape, float(P.get("alpha", 212)), "float32")
    a[aperture] = float(P.get("alpha", 212)) + 22
    return rgb, a


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
    if P.get("fan"):
        # a fan radiates from ONE apex; parallel stripes along an axis are not a fan
        ys, xs = np.nonzero(mask)
        pr = -xs * np.sin(ang) + ys * np.cos(ang)
        k = int(np.argmin(pr))
        v = np.arctan2(gy - ys[k], gx - xs[k]) * (N * P.get("braid", 0.05) * 3.4)
    else:
        v = -gx * np.sin(ang) + gy * np.cos(ang)
    v = v + _fbm((N, N), rng, N / 2.6, N * 0.10)
    band = (v / (N * P.get("braid", 0.05))) % 1.0
    # cube the ramp so the dark cut is a thin vein, not a third of the fill
    t = (np.abs(band - 0.5) * 2) ** P.get("cut", 3.0)
    rgb = _grad(t, [(0.0, P.get("thread", P["dark"])), (0.45, P["base"]), (1.0, P["lit"])])
    return rgb, np.full(mask.shape, float(P.get("alpha", 200)), "float32")


def t_maw(mask, rng, P):
    """A pit that is also a mouth.  Read from the outside in: a drifted collar of ground,
    then the funnel wall falling away, then a ring of inward-pointing TEETH whose tips
    reach toward the middle, then the beak, then black.

    The teeth are what make it a maw rather than a crater, so they are cut as a radius
    threshold that varies with angle -- long tips, wide gullets -- and not as a texture.
    The centre is a hard black aperture with no gradient into it: a gullet is an absence,
    and any falloff turns it back into a dent."""
    N = mask.shape[0]
    ys, xs = np.nonzero(mask)
    cy, cx = ys.mean(), xs.mean()
    gy, gx = np.mgrid[0:N, 0:N].astype("float32")
    th = np.arctan2(gy - cy, gx - cx)
    R = max(np.sqrt(mask.sum() / np.pi), 4.0)
    r = np.hypot(gy - cy, gx - cx) + _fbm((N, N), rng, N / 5.0, R * P.get("warp", 0.10))
    t = np.clip(r / R, 0, 1.3)

    rgb = _grad(np.clip(t / 1.15, 0, 1),
                [(0.0, P["throat"]), (0.30, P["wall"]), (0.62, P["base"]),
                 (0.86, P["lit"]), (1.0, P["collar"])])

    # Teeth must be INDIVIDUAL: one cosine gives a cog wheel -- every tooth the same
    # length, the same width, evenly spaced, and no dark gullet showing between them.
    # Each tooth therefore gets its own length and width from a per-tooth table.
    n = P.get("teeth", 9)
    u = ((th + np.pi + rng.uniform(0, 6.283)) / (2 * np.pi) * n) % n
    idx = np.floor(u).astype(int) % n
    lens = rng.uniform(0.70, 1.32, n).astype("float32")
    wids = rng.uniform(0.34, 0.72, n).astype("float32")
    frac = u - np.floor(u)
    prof = np.clip(1.0 - np.abs(frac - 0.5) * 2.0 / np.maximum(wids[idx], 1e-3), 0, 1)
    prof = prof ** P.get("taper", 1.5)
    tip = P.get("tip", 0.20) + P.get("reach", 0.34) * (1.0 - prof * lens[idx])
    gum = P.get("gum", 0.66)
    gap = (t < gum) & (t > P.get("beak_at", 0.30))
    rgb[gap] = np.array(P.get("gullet_wall", P["throat"]), "float32")   # dark between teeth
    # A tooth also has to taper IN RADIUS, or it is a spoke: widest where it leaves the
    # gum, narrowing to a point at the tip.  Without this the ring reads as a ship's wheel.
    q = np.clip((gum - t) / np.maximum(gum - tip, 1e-3), 0, 1)
    tooth = (t < gum) & (t > tip) & (prof > q * P.get("point", 0.92) + 0.05)
    rgb[tooth] = np.array(P["tooth"], "float32")
    edge = tooth & ~_erode(tooth, max(1, int(N * 0.005)))
    rgb[edge] = np.array(P.get("tooth_edge", P["wall"]), "float32")

    # beak_at is a RADIUS; "beak" is the colour.  One key cannot be both, and the
    # collision only shows up as a broadcast error at paint time.
    beak = (t < P.get("beak_at", 0.30)) & (t > P.get("mouth", 0.17))
    rgb[beak] = np.array(P["beak"], "float32")
    black = t < P.get("mouth", 0.17) * (1.0 + 0.30 * np.sin(3 * th + rng.uniform(0, 6.283)))
    rgb[black] = P.get("gullet", (6, 5, 5))

    a = np.full(mask.shape, float(P.get("alpha", 216)), "float32")
    a[black] = 252.0
    return rgb, a


def t_oasis(mask, rng, P):
    """The one green thing for a hundred miles, and it must look like it.  Three CRISP
    zones, not a gradient: vivid open water with a hard shoreline, a dense ring of
    vegetation crowding that shore, and a dry mineral fringe outside it.  Flowers are
    single saturated flecks scattered in the greenery -- few, small, and never regular."""
    N = mask.shape[0]
    R = max(np.sqrt(mask.sum() / np.pi), 4.0)
    dep = np.clip(_dist_in(mask, R * 1.1) / (R * 1.1), 0, 1)
    dep = np.clip(dep + _fbm((N, N), rng, N / 5.0, P.get("rough", 0.10)), 0, 1)

    rgb = np.zeros(mask.shape + (3,), "float32")
    rgb[:] = P["fringe"]
    veg = dep > P.get("veg_at", 0.10)
    rgb[veg] = P["veg"]
    shade = veg & (_fbm((N, N), rng, N / 11.0, 1.0) > 0.48)
    rgb[shade] = P.get("veg_dark", P["veg"])
    water = dep > P.get("water_at", 0.40)
    rgb[water] = P["water"]
    deep = dep > P.get("deep_at", 0.62)
    rgb[deep] = P["deep"]
    shal = water & ~deep & (_fbm((N, N), rng, N / 14.0, 1.0) > 0.55)
    rgb[shal] = P.get("shallow", P["water"])

    band = veg & ~water
    for col, dens in P.get("flowers", ()):
        f = (rng.random(mask.shape) < dens) & band
        f = np.asarray(Image.fromarray((f * 255).astype("uint8"))
                       .filter(ImageFilter.MaxFilter(2 * int(0.0035 * N) + 1))) > 128
        rgb[f] = col

    a = np.full(mask.shape, float(P.get("alpha", 214)), "float32")
    a[water] = float(P.get("alpha", 214)) + 24
    return rgb, a


TREATMENTS = {"crust": t_crust, "storm": t_storm, "ripples": t_ripples, "clasts": t_clasts,
              "pool": t_pool, "crater": t_crater, "strata": t_strata, "masonry": t_masonry,
              "organic": t_organic, "lava": t_lava, "ice": t_ice, "canopy": t_canopy,
              "channel": t_channel, "maw": t_maw, "oasis": t_oasis}


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
    glint=(246, 232, 199), alpha=218, alpha_lo=74, arms=2, eye=0.13, break_eye=1.4),

"VEE_QuicksandDunes": S("""Treacherous ground pretending to be ordinary dune field. Pale sulphur-
    cream bedforms lying across the wind, but slack and rounded rather than crisp, with darker
    saturated hollows between crests where the sand is holding water. Crests aligned across the
    landform's long axis. Words: soft, waterlogged, deceitful, sallow, unset.""",
    "ripples", base=(206, 196, 133), lit=(232, 226, 170), dark=(150, 141, 88),
    wave=0.17, sinuosity=0.17, alpha=198),

"AB_QuicksandPits": S("""Discrete sink pits rather than a field: each one a slack cream-grey
    disc darkening steeply to a saturated throat, with a wet collar where the sand has slumped
    inward. Nothing about it should look firm. Words: slumping, sodden, throat, quiet, hungry.""",
    "pool", base=(168, 152, 108), lit=(206, 194, 150), dark=(70, 58, 38),
    shore=(214, 202, 168), scum=0.30, scum_col=(96, 82, 56), alpha=204),

# ---- sand and stone -----------------------------------------------------------
"Dunes": S("""A barchan dune field from orbit. Long low stoss slopes rising to a sharp lee break
    -- an asymmetric wave, not a sine -- laid ACROSS the prevailing wind, aligned to the field's
    own long axis. Warm apricot sand, the crests catching light, the troughs holding a cooler
    shadow. Words: migrating, wind-combed, sinuous, sun-warmed.""",
    "ripples", base=(214, 168, 118), lit=(243, 210, 165), dark=(163, 120, 79),
    wave=0.20, sinuosity=0.20, alpha=204),

"VEE_PebbleDunes": S("""Sand that has run out of sand. The same wind-laid bedforms as an open
    dune field, but with a lag of small dark pebbles left standing on the crests where the fines
    have blown away -- a stony sheen over a pale ground. Words: winnowed, gritty, armoured,
    lag-strewn.""",
    "ripples", base=(198, 186, 158), lit=(226, 217, 193), dark=(146, 135, 110),
    wave=0.17, sinuosity=0.16, clast=0.012, clast_px=0.008, clast_col=(88, 80, 68), alpha=200),

"VEE_RedDesert": S("""Iron-stained sand at its most saturated. Deep oxide red bedforms with an
    almost violet shadow in the troughs and a hot, bright rust on the crests -- the colour of a
    place that rusted rather than weathered. Words: ferrous, oxidised, smouldering, ancient.""",
    "ripples", base=(162, 82, 58), lit=(219, 128, 78), dark=(88, 44, 52),
    wave=0.18, sinuosity=0.17, alpha=208),

"VEE_GravelBeach": S("""A bed of loose water-rounded clasts, each stone its own tone, packed
    edge to edge with dark shadow in the interstices. Read as GRANULAR: the eye should be able to
    count individual stones at full size and see texture at map size. Cool grey-buff, faintly
    damp. Words: rattling, sorted, water-rolled, shingle.""",
    "clasts", base=(178, 170, 152), lit=(214, 208, 192), dark=(118, 112, 98),
    seam=(78, 74, 64), stones=220, round=0.055, alpha=200),

"VEE_JaggedRocks": S("""Shattered, unweathered rock -- angular blades and shards standing at
    every angle, nothing rounded, hard shadow on the lee faces. Cold slate grey with a bluish
    cast where the fresh fracture shows. Words: splintered, knife-edged, frost-riven, brutal.""",
    "clasts", base=(132, 136, 148), lit=(180, 188, 204), dark=(68, 72, 86),
    seam=(38, 40, 52), stones=60, round=0.02, alpha=206),

"VEE_StoneForest": S("""A karst pinnacle field: tall isolated stone towers seen from directly
    above, so each reads as a bright cap with a deep shadow moat around it. Pale weathered
    limestone, cream to grey. Words: fluted, tapering, cathedral, silent.""",
    "clasts", base=(186, 178, 160), lit=(228, 222, 206), dark=(96, 92, 82),
    seam=(56, 54, 48), stones=38, round=0.03, moat=0.012, moat_col=(46, 42, 38), alpha=206),

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
    seam=(62, 48, 34), scarp=(212, 188, 150), bed=0.17, floor=(96, 76, 54), alpha=196),

"VEE_RockRidge": S("""A single hard spine standing above softer ground. Strata run the length of
    the ridge, tightest and brightest along the crest line, falling away into shadow on both
    flanks. Dry grey-brown, unvegetated. Words: resistant, keeled, backbone, wind-scoured.""",
    "strata", base=(140, 124, 100), lit=(196, 182, 156), dark=(82, 72, 58),
    seam=(54, 48, 38), scarp=(214, 202, 178), bed=0.22, alpha=198),

"Plateau": S("""A flat-topped mesa: an even, bright, almost featureless cap of hard rock ringed
    by a stepped scarp dropping into shadow. The top should read as CALM and the edge as abrupt.
    Words: tabular, capped, abrupt, elevated.""",
    "strata", base=(158, 132, 100), lit=(210, 186, 148), dark=(92, 74, 54),
    seam=(66, 52, 38), scarp=(226, 206, 172), bed=0.16, alpha=200),

"Chasm": S("""A rift with no visible bottom. Near-black in the throat, walls stepping up through
    cold greys in tight bedded bands, a thin bright lip where the light just reaches the rim.
    Words: bottomless, fractured, cold, vertiginous.""",
    "crater", base=(46, 44, 48), lit=(168, 166, 172), dark=(16, 16, 20),
    floor=(22, 22, 26), warp=0.16, lobe=0.18, alpha=214),

"VEE_SerpentineCanyons": S("""A maze of narrow winding slot canyons. Bright rims and floors
    threaded by dark sinuous cuts that follow the landform's own meander, never straight. Warm
    desert varnish on the rock. Words: labyrinthine, slotted, meandering, shaded.""",
    "channel", base=(168, 132, 94), lit=(216, 186, 144), dark=(70, 52, 36),
    thread=(52, 38, 26), braid=0.085, cut=3.4, alpha=202),

"Cavern": S("""A mouth in the ground seen from above: a bright rock collar falling steeply into
    a dark void, with the void taking most of the area. The interior should read as ABSENCE, not
    as a dark colour. Words: yawning, hollow, cool, unlit.""",
    "crater", base=(126, 112, 92), lit=(198, 182, 156), dark=(30, 28, 26),
    floor=(46, 42, 38), alpha=208),

"Hollow": S("""A shallow closed depression. A soft bright rim, a gently graded inner slope, a
    flat floor a shade darker and warmer than the surrounding ground. Nothing sheer. Words:
    scooped, gentle, sheltered, sun-trapped.""",
    "crater", base=(160, 138, 106), lit=(212, 194, 160), dark=(104, 88, 66),
    floor=(134, 114, 86), warp=0.20, lobe=0.22, alpha=194),

"VEE_MeteorCrater": S("""An impact structure: a raised rim catching hard light, a steep shadowed
    inner wall, a flat floor of shocked debris, and the ground outside faintly bruised by ejecta.
    Concentric but never circular. Words: shocked, ramparted, violent, glassy.""",
    "crater", base=(140, 124, 104), lit=(210, 194, 166), dark=(62, 54, 46),
    floor=(108, 96, 82), warp=0.26, lobe=0.26, alpha=204),

"LavaCrater": S("""A proper crater with lava in the bottom of it. The structure comes first
    and it is ROUND: a raised ring of ridged spoil outside, catching hard light on its outer
    slope, then a steep shadowed inner wall, and only then the lava -- a pool of black chilled
    crust cracked open over incandescent rock, contained well inside the rim rather than spilling
    to the outline. Words: ramparted, contained, glowing, sullen, circular.""",
    "crater", base=(122, 104, 92), lit=(196, 176, 152), dark=(58, 48, 42),
    floor=(88, 72, 62), warp=0.04, lobe=0.05, alpha=212,
    core={"treat": "lava", "r": 0.52, "base": (72, 56, 52), "lit": (238, 124, 44),
          "dark": (30, 25, 24), "glint": (255, 214, 120), "vein_w": 0.085, "alpha": 230}),
"VEE_ToxicCrater": S("""A crater with something hideous lying in it. Ridged grey-tan walls
    like any impact rim, bleached dead where the fumes reach, and inside them a pool of brackish
    green liquid actively bubbling -- opaque, sickly, with paler rafts of scum breaking the
    surface and a rusty tidemark where the level has dropped. The rim should read as ROCK and the
    contents as LIQUID; the contrast between them is the whole icon. Words: leached, bubbling,
    acrid, quarantined, wrong.""",
    "crater", base=(148, 140, 118), lit=(206, 198, 172), dark=(70, 66, 54),
    floor=(120, 112, 92), warp=0.06, lobe=0.08, alpha=208,
    core={"treat": "pool", "r": 0.74, "base": (92, 138, 52), "lit": (140, 182, 66),
          "dark": (38, 78, 34), "shore": (150, 124, 58), "scum": 0.16,
          "scum_col": (188, 220, 104), "rough": 0.30, "reach": 1.25, "alpha": 228}),
"TerraformingScar": S("""Machine work, not weather. A spiral trench cut into the ground in
    regular passes, the spoil banked bright along one side of every pass and the cut itself in
    shadow -- the only landform on the planet with a repeating, deliberate rhythm. Words:
    industrial, ploughed, geometric, unfinished.""",
    "crater", base=(132, 122, 112), lit=(196, 188, 176), dark=(66, 62, 58),
    floor=(104, 98, 92), rings=0.030, rings_amp=0.30, warp=0.05, lobe=0.05, alpha=204),

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
    thread=(140, 122, 96), braid=0.055, cut=2.2, fan=True, alpha=198),

# ---- water and what is left of it ---------------------------------------------
"VEE_DryRiver": S("""A watercourse with the water taken out. Braided pale threads of sorted sand
    running the LENGTH of the course, dark abandoned channels between them, everything aligned to
    the river's own meander. Words: braided, stranded, bleached, ghost-course.""",
    "channel", base=(172, 148, 112), lit=(218, 202, 172), dark=(104, 86, 64),
    thread=(88, 72, 54), braid=0.085, cut=2.6, alpha=196),

"Oasis": S("""The one green thing for a hundred miles. Crisply defined vibrant blue water at
    the centre -- a hard shoreline, not a fade -- surrounded by a dense ring of green vegetation
    crowding right up to the edge, with bits of colour peeking through it like flowers. Outside
    that, a dry mineral fringe where the greenery gives up. Three distinct zones with clean
    boundaries; the improbability of it against the desert is the entire read. Words: fed, vivid,
    shaded, flowering, precious.""",
    "oasis", fringe=(196, 178, 122), veg=(78, 134, 62), veg_dark=(48, 98, 48),
    water=(44, 134, 190), deep=(24, 88, 148), shallow=(96, 182, 214),
    flowers=(((236, 96, 128), 0.00040), ((246, 214, 82), 0.00034), ((238, 146, 68), 0.00022)),
    veg_at=0.08, water_at=0.42, deep_at=0.66, rough=0.09, alpha=214),
"VEE_StagnantRivulet": S("""Water that has stopped moving and knows it. Flat olive-green,
    skinned over with algal scum in irregular rafts, no reflection, a dark saturated margin where
    the mud is always wet. Words: brackish, skinned, motionless, fetid.""",
    "pool", base=(104, 124, 78), lit=(146, 164, 106), dark=(58, 72, 46),
    shore=(58, 64, 42), scum=0.30, scum_col=(162, 180, 120), alpha=206),

"VEE_Cenotes": S("""Collapse sinkholes flooded with groundwater. A hard bright limestone collar
    dropping abruptly to water of an intense, almost unreal blue that darkens fast with depth.
    The abruptness of the edge is the point. Words: sheer, sapphire, cold, fathomless.""",
    "pool", base=(28, 104, 150), lit=(86, 176, 212), dark=(10, 40, 74),
    shore=(206, 196, 168), alpha=216),

"VEE_SulfuricLake": S("""Mineral water at its most poisonous. Acid yellow-green shallows banded
    into a hotter core, ringed by a crust of sulphur precipitate so pale it looks bleached. Words:
    acrid, precipitated, luminous, corrosive.""",
    "pool", base=(206, 196, 96), lit=(232, 226, 140), dark=(214, 142, 46),
    shore=(245, 238, 210), scum=0.40, scum_col=(244, 236, 168), alpha=212),

"ToxicLake": S("""Runoff that never drained. Dense opaque green, darkening steeply toward the
    middle, with a dead bleached margin where nothing will grow and an oily film catching light in
    slicks. Words: opaque, chemical, still, poisoned.""",
    "pool", base=(74, 108, 76), lit=(120, 156, 112), dark=(34, 56, 40),
    shore=(198, 196, 168), scum=0.42, scum_col=(126, 168, 118), alpha=214),

"AB_TarLakes": S("""Cold asphalt pooled in a hollow. Near-black, viscous, with a dull sheen
    rather than a reflection and a sticky crusted margin where dust has blown onto the surface.
    Words: viscous, sucking, lightless, slow.""",
    "pool", base=(30, 27, 27), lit=(46, 40, 38), dark=(12, 11, 11),
    shore=(70, 60, 48), scum=0.46, scum_col=(52, 46, 42), alpha=222),

"AB_MagmaticQuagmire": S("""Ground that has half melted. Black chilled crust broken into rafts
    floating on incandescent rock, the glow bleeding up through every crack and widening where the
    rafts have pulled apart. Words: molten, foundering, radiant, unstable.""",
    "lava", base=(66, 50, 46), lit=(238, 116, 38), dark=(28, 24, 24),
    glint=(255, 214, 122), vein_w=0.075, alpha=220),

"LavaLake": S("""An open lake of molten rock. A thin dark skin constantly tearing apart to show
    the orange beneath, brightest at the centre where the convection rises, with a hard black
    levee at the shore. Words: churning, incandescent, skinned, seething.""",
    "lava", base=(78, 58, 50), lit=(244, 132, 44), dark=(30, 24, 22),
    glint=(255, 224, 140), vein_w=0.105, alpha=222),

"HotSprings": S("""Mineral terraces built by hot water. Concentric rimstone pools stepping
    downhill, each holding water of a different temperature and therefore a different colour --
    white-hot centre through turquoise to a rusty bacterial fringe. Words: terraced, steaming,
    depositing, banded.""",
    "pool", base=(96, 176, 178), lit=(214, 232, 226), dark=(240, 246, 240),
    shore=(196, 132, 74), terrace=5, rough=0.05, reach=1.15, alpha=214),

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
    "masonry", base=(120, 124, 126), lit=(168, 172, 176), dark=(40, 44, 48),
    seam=(40, 42, 44), rust=(112, 88, 70), panel=0.075, alpha=214),

"AncientWarehouse": S("""Storage at industrial scale. Long uniform roof bays with ribbed panel
    lines running one way only, a lighter weathered sheen along the ridge, corrosion streaking
    down from every seam. Words: cavernous, ribbed, utilitarian, corroding.""",
    "masonry", base=(146, 142, 132), lit=(196, 192, 182), dark=(84, 82, 76),
    seam=(50, 48, 44), rust=(138, 100, 70), ribs=True, panel=0.13, alpha=212),

"AncientChemfuelRefinery": S("""Process plant. Cylindrical tank tops and pipe runs, flat oily
    greys shot through with heavy rust, dark stains spreading from the tank bases where something
    leaked and was never cleaned up. Words: petrochemical, stained, tangled, shut down.""",
    "masonry", base=(124, 120, 114), lit=(172, 168, 160), dark=(70, 66, 62),
    seam=(42, 40, 38), rust=(90, 60, 40), panel=0.065, alpha=214),

"AncientLaunchSite": S("""A pad built for one enormous departure. Vast flat blast-scoured
    concrete aprons, a few heavy structures, scorch blackening radiating from the centre. Words:
    scorched, monumental, abandoned mid-purpose.""",
    "masonry", base=(150, 148, 144), lit=(198, 196, 192),
    seam=(46, 44, 44), rust=(36, 32, 30), scorch=(44, 40, 38), dark=(50, 48, 46), panel=0.12, alpha=212),

"AncientHeatVent": S("""Deep machinery still running. Grilled vent housings in dull alloy with
    a hot glow escaping between the louvres, aligned to the housing, and the ground around them
    bleached by decades of exhaust. Words: humming, louvred, thermal, still-powered.""",
    "masonry", base=(112, 112, 116), lit=(150, 148, 150), dark=(52, 52, 56),
    seam=(232, 152, 68), rust=(88, 84, 84), rust_amt=0.62, ribs=True, panel=0.10, alpha=216),

"FrozenRuins": S("""The same fallen concrete, taken by ice. Slabs glazed and rounded under old
    snowpack, seams filled white, everything shifted toward cold blue-grey with a hard glare on
    the upper faces. Words: glazed, entombed, blue-shadowed, silent.""",
    "masonry", base=(176, 186, 196), lit=(226, 234, 240), dark=(104, 116, 130),
    seam=(225, 235, 240), rust=(150, 160, 172), panel=0.09, alpha=210),

"AbandonedColonyTribal": S("""A settlement built from what was to hand. Thatch and timber roofs
    in warm organic browns, irregular rather than gridded, weathered pale on the weather side,
    already half returning to the ground. Words: woven, sun-bleached, humble, reclaimed.""",
    "clasts", base=(150, 116, 76), lit=(206, 176, 128), dark=(92, 68, 44),
    seam=(52, 38, 26), stones=55, round=0.075, alpha=206),

"AbandonedColonyOutlander": S("""A frontier town left standing. Prefab roofs and sheet siding in
    faded paint colours, laid out on a loose grid, sun-faded on top and rust-streaked below. Words:
    prefabricated, faded, orderly, emptied.""",
    "masonry", base=(150, 140, 124), lit=(200, 192, 176), dark=(88, 82, 72),
    seam=(54, 50, 44), rust=(160, 92, 58), panel=0.09, alpha=208),

# ---- alive, or lately so ------------------------------------------------------
"VEE_FleshPits": S("""Something biological has taken the ground. Wet radial folds of raw
    membrane converging on dark gullet openings, gullet-dark at the centre and blooming to angry
    pink at the rim, with a sheen that says WET. Words: peristaltic, raw, glistening, wrong.""",
    "organic", base=(178, 92, 96), lit=(224, 148, 148), dark=(72, 30, 36),
    sheen=(238, 176, 172), gullet=(48, 18, 26), folds=9, maw=0.34, alpha=216),

"sw_Sarlacc": S("""A gaping beaked maw at the bottom of a deep pit of teeth, with a dark
    black centre. Read it from the outside in: drifted sand banked around the lip, then the funnel
    wall dropping away in warm leathery tan, then a ring of long inward-pointing teeth whose pale
    tips reach toward the middle over dark gullets between them, then the hard chitinous beak, then
    nothing at all -- a flat black hole with no gradient into it, because a throat is an absence
    and any falloff turns it back into a dent. Words: beaked, toothed, funnelled, patient,
    bottomless.""",
    "maw", collar=(186, 160, 120), lit=(206, 180, 138), base=(150, 118, 84),
    wall=(96, 72, 50), throat=(38, 28, 22), tooth=(226, 212, 184), tooth_edge=(92, 74, 56),
    beak=(74, 56, 42), gullet=(6, 5, 5), gullet_wall=(52, 36, 26), teeth=11, taper=1.15, tip=0.20, reach=0.34,
    gum=0.72, beak_at=0.32, mouth=0.27, warp=0.13, point=0.92, alpha=218),
"sw_DeadSarlacc": S("""The same gaping beaked maw, desiccated -- at the bottom of a grey husk
    of a pit, still with a dark black centre. Everything that was leathery is now papery and
    bleached; the teeth are dulled and snapped, the beak cracked grey, the funnel wall the colour
    of old bone with sand drifting into it. Only the black centre is unchanged. Words: desiccated,
    husked, bleached, brittle, hollow.""",
    "maw", collar=(178, 172, 158), lit=(198, 192, 178), base=(160, 154, 140),
    wall=(112, 108, 98), throat=(58, 55, 50), tooth=(220, 216, 206), tooth_edge=(120, 116, 106),
    beak=(126, 122, 112), gullet=(8, 8, 8), gullet_wall=(86, 82, 74), teeth=11, taper=1.05, tip=0.24, reach=0.28,
    gum=0.70, beak_at=0.32, mouth=0.27, warp=0.17, point=0.86, alpha=206),}


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
        rng = np.random.default_rng(_seed(name, i))
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


# 🔒 Signed off by the owner on 2026-08-25 and NOT to be regenerated.  These two were
# approved from a specific roll of the RNG, and at the time the seed came from hash(),
# which Python salts per process -- so "regenerate" meant "reroll and lose them".  The
# seed is stable now, but the treatments have since been retuned, so a rerun would still
# produce different art.  paint_all skips them; pass force=True only if the owner asks.
APPROVED = {"VEE_SaltPlains", "VEE_DustBowl"}


def paint_all(dest, only=None, force=False):
    import landmark_icon_sheet as L
    defs, idx = L.landmark_defs(), L.texture_index()
    os.makedirs(dest, exist_ok=True)
    done, skipped = [], []
    for name in (only or SPECS):
        if name in APPROVED and not force:
            skipped.append((name, "APPROVED - not regenerated")); continue
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
    force = "--force" in sys.argv
    only = [a for a in (only or []) if not a.startswith("--")] or None
    done, skipped = paint_all(dest, only, force)
    print(f"painted {len(done)}")
    for n, why in skipped:
        print(f"  SKIP {n}: {why}")
