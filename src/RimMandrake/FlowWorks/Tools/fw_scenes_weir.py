#!/usr/bin/env python3
"""Offline weir scenes and checks (WEIR_LOOKS_REDRAW_ONE_PER_PIPE_STYLE).

Owner 2026-10-24: "Weirs by look: scavver/crude, industrial, modern, futuristic." -- one weir per pipe style, each from one
of his four photos (art_source/Weir/weir_by_photo.py draws them): Scrapper rubble, Industrial stepped concrete, Modern
smooth curtain, Futuristic labyrinth.

Scenes (what RM_Building_BankWeir.Print / DrawWhiteWater draw, read from RM_Weir.cs, not guessed): three 1x2 sections
in a run across a river -- body plane (drawSize turned for E/W art) at Building, the crest sheet <look>Spill_<facing> one
cell per WATER cell at +0.25 AltInc, the free-end posts <look>Cap (0.7 cell, lifted 0.08) at +0.5 AltInc, and the
look-free white water RM_WeirWhiteWater_00 at FloorEmplacement, one cell downstream of each wet cell (lane length 1).
  ew: the run E-W across a river flowing SOUTH (ArtRot East: the spill face toward the camera)
  ns: the run N-S across a river flowing EAST (ArtRot North: the apron to the right)
The ground is the GAME's (lesson offline-sheet-floor-standin): vanilla Riverbank.png on the banks and the vanilla
moving-shallow-water colour (WaterShallowRamp.png's mean, modulated by WaterRipple.png) in the river, read from
$RM_VANILLA_TEX. The water shader's motion and reflections are not emulated; terrain_is_vanilla() pins the colours.

Checks (each look's IDENTITY check FAILS on the timber set shipped before this item and PASSES on the redraw;
selftest_weir_looks.py runs both):
  rubble_not_timber   Scrapper: low-saturation stone (not warm brown boards) and a lumpy crest (top edge std > 3 px)
  three_steps         Industrial: >= 3 tread edges down the spill face; no hazard yellow
  smooth_no_red       Modern: no red; pale (median luminance > 150); a smooth face (few hard edges)
  zigzag_crest        Futuristic: the crest edge oscillates at two teeth a cell (period 64 px +- 4), amplitude >= 10 px,
                      and the north art's cyan crest repeats every 64 rows +- 4 (two teeth a cell along a N-S run too)
and on every look: canvases, clean alpha, seamless joins (E/W left == right column, N/S top == bottom row), the crest
sheet on the wall (every sheet pixel inside the body's column span) with no bright bar across it (spill_no_white_bar),
the north art's section ends at most 12 lum darker than the darkest interior 16-row window (north_ends_drawn: else a grey
bar every 2 cells along a N-S run),
south == north mirrored, and facing
(Industrial/Modern/Futuristic: in the east art the upstream crest rises higher on screen than in the west art; in the
north art the crest sits on the upstream, left, half; Futuristic's falling-water bays lie downstream: lower in the east art
than the west, right of centre in the north art).

    python3 fw_scenes_weir.py <out_dir> [--after DIR]   # before/after scenes per look + SHEET_weir.png
"""
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fw_compositor as fc  # noqa: E402

LOOKS = ("Scrapper", "Industrial", "Modern", "Futuristic")
INSTALLED = fc.TEX / "RimMandrake/FlowWorks/Weir"
FOAM = INSTALLED / "WhiteWater/RM_WeirWhiteWater_00.png"
VANILLA_TEX_DEFAULT = "/mnt/d/ClaudeWork/rimmandrake/scratch/vanilla_tex/ludeon.rimworld.core"
TERRAIN_CELLS = 10      # cells one terrain texture repeat spans (fw_scenes_spikes.GRAVEL_CELLS, calibrated live)
CAP_SIZE, CAP_LIFT = 0.7, 0.08   # RM_WeirArt.CapSize / CapLift
ALT_INC = 0.05          # fraction of a layer step standing in for Altitudes.AltInc (order only)


def _vanilla(name):
    f = Path(os.environ.get("RM_VANILLA_TEX", VANILLA_TEX_DEFAULT)) / name
    if not f.is_file():
        raise SystemExit("fw_scenes_weir: no %s (set RM_VANILLA_TEX to the extracted core textures)" % f)
    return Image.open(f).convert("RGB")


def water_rgb():
    """The vanilla moving-shallow-water colour: WaterShallowRamp.png's mean (87.4, 96.4, 98.8 measured)."""
    return tuple(np.asarray(_vanilla("WaterShallowRamp.png"), np.float32).reshape(-1, 3).mean(0))


def bank_rgb():
    return tuple(np.asarray(_vanilla("Riverbank.png"), np.float32).reshape(-1, 3).mean(0))


def terrain(w, h, P, wet):
    """Ground W x H cells at P px/cell; wet(x, z) -> True = river water. Returns RGBA."""
    side = TERRAIN_CELLS * P
    bank = np.asarray(_vanilla("Riverbank.png").resize((side, side), Image.LANCZOS), np.float32)
    rip = np.asarray(_vanilla("WaterRipple.png").convert("L").resize((side, side), Image.LANCZOS), np.float32)
    rip = (rip - rip.mean()) / max(rip.std(), 1e-6)
    W, H = w * P, h * P
    tile = lambda a: np.tile(a, (H // side + 1, W // side + 1) + (1,) * (a.ndim - 2))[:H, :W]
    bank, rip = tile(bank), tile(rip)
    water = np.array(water_rgb(), np.float32) * (1 + 0.04 * rip)[..., None]
    mask = np.zeros((H, W), bool)
    for x in range(w):
        for z in range(h):
            if wet(x, z):
                mask[(h - 1 - z) * P:(h - z) * P, x * P:(x + 1) * P] = True
    rgb = np.where(mask[..., None], water, bank)
    return Image.fromarray(np.dstack([np.clip(rgb, 0, 255), np.full((H, W), 255.0)]).astype(np.uint8), "RGBA")


def art(d, look, name):
    return Image.open(Path(d) / look / (name + ".png")).convert("RGBA")


def scene(look, d, kind="ew", P=128, foam=True):
    """(rgba, meta): a run of three sections across a 4-cell river. d = a folder holding <look>/RM_BankWeir*.png."""
    if kind == "ew":
        w, h = 8, 5
        wet = lambda x, z: 2 <= x <= 5
    else:
        w, h = 5, 8
        wet = lambda x, z: 2 <= z <= 5
    sc = fc.Scene(w, h, px=P, ground=False)
    ground = terrain(w, h, P, wet)
    body = art(d, look, "RM_BankWeir_" + ("east" if kind == "ew" else "north"))
    spill = art(d, look, "RM_BankWeirSpill_" + ("east" if kind == "ew" else "north"))
    capi = art(d, look, "RM_BankWeirCap")
    fo = Image.open(FOAM).convert("RGBA")
    if kind == "ew":
        z0 = 2
        for x0 in (1, 3, 5):
            sc.plane(body, x0 + 1.0, z0 + 0.5, 2, 1)
            for x in (x0, x0 + 1):
                if wet(x, z0):
                    sc.plane(spill, x + 0.5, z0 + 0.5, 1, 1, dy=ALT_INC * 0.25)
                    if foam:
                        sc.plane(fo, x + 0.5, z0 - 0.5, 1, 1, alt="FloorEmplacement")
        for cx in (1, 7):
            sc.plane(capi, cx, z0 + 0.5 + CAP_LIFT, CAP_SIZE, CAP_SIZE, dy=ALT_INC * 0.5)
    else:
        x0 = 2
        for zz in (1, 3, 5):
            sc.plane(body, x0 + 0.5, zz + 1.0, 1, 2)
            for z in (zz, zz + 1):
                if wet(x0, z):
                    sc.plane(spill, x0 + 0.5, z + 0.5, 1, 1, dy=ALT_INC * 0.25)
                    if foam:  # the frames fall south; the game turns them 270 deg (y) to fall east
                        sc.plane(fo.rotate(90, expand=True), x0 + 1.5, z + 0.5, 1, 1, alt="FloorEmplacement")
        sc.plane(capi, x0 + 0.5, 1 + CAP_LIFT, CAP_SIZE, CAP_SIZE, dy=ALT_INC * 0.5)
        sc.plane(capi, x0 + 0.5, 7 + CAP_LIFT, CAP_SIZE, CAP_SIZE, dy=ALT_INC * 0.6)
    cv = ground.copy()
    cv.alpha_composite(sc.render())
    return cv, dict(w=w, h=h, P=P, wet=wet, kind=kind)


# ---- checks: helpers -------------------------------------------------------------------------------------------------
SOLID = 128


def _a(im):
    return np.asarray(im.convert("RGBA"), np.float32)


def _hsv(rgb):
    mx, mn = rgb.max(-1), rgb.min(-1)
    s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    return s, mx


def _lum(rgb):
    return rgb @ np.array([0.299, 0.587, 0.114], np.float32)


def top_edge(im):
    """Per column: the first opaque row (or -1)."""
    m = _a(im)[..., 3] >= SOLID
    any_ = m.any(0)
    return np.where(any_, m.argmax(0), -1)


def band_rows(im):
    t = top_edge(im)
    m = _a(im)[..., 3] >= SOLID
    b = np.where(m.any(0), m.shape[0] - 1 - m[::-1].argmax(0), -1)
    ok = t >= 0
    return int(np.median(t[ok])), int(np.median(b[ok]))


def opaque_rgb(im):
    a = _a(im)
    return a[..., :3][a[..., 3] >= SOLID]


# ---- identity checks (FAIL on the timber set) -----------------------------------------------------------------------
def rubble_not_timber(d):
    east = art(d, "Scrapper", "RM_BankWeir_east")
    rgb = opaque_rgb(east)
    s, _ = _hsv(rgb)
    warm = float(np.median(rgb[:, 0] - rgb[:, 2]))
    sat = float(np.median(s))
    t = top_edge(east)
    lump = float(np.std(t[t >= 0]))
    ok = sat < 0.22 and warm < 26 and lump > 2.0
    return ok, "median sat %.2f (<0.22), r-b %.0f (<26), crest std %.1f px (>2)" % (sat, warm, lump)


def three_steps(d):
    east = _a(art(d, "Industrial", "RM_BankWeir_east"))
    al = east[..., 3] >= SOLID
    rgb = east[..., :3]
    top, bot = band_rows(Image.fromarray(east.astype(np.uint8), "RGBA"))
    # per row, the luminance of the middle half of the wall, between the crest and the toe
    cols = slice(32, 224)
    rows = np.arange(top, bot + 1)
    lum = np.array([np.median(_lum(rgb[r, cols][al[r, cols]])) if al[r, cols].sum() > 64 else np.nan for r in rows])
    jumps = np.abs(np.diff(lum))
    edges = rows[1:][jumps > 10]
    # count distinct edges (merge neighbours within 2 rows)
    n = 0
    last = -99
    for e in edges:
        if e - last > 2:
            n += 1
        last = e
    hz = (rgb[..., 0] > 150) & (rgb[..., 1] > 120) & (rgb[..., 2] < 90) & al
    yel = float(hz.sum()) / max(1, int(al.sum()))
    ok = n >= 3 and yel < 0.005
    return ok, "%d tread edges (>=3), hazard yellow %.3f (<0.005)" % (n, yel)


def smooth_no_red(d):
    bad = []
    worst = 0.0
    for name in ("RM_BankWeir_east", "RM_BankWeir_west", "RM_BankWeir_north", "RM_BankWeirCap"):
        rgb = opaque_rgb(art(d, "Modern", name))
        red = (rgb[:, 0] > rgb[:, 1] + 40) & (rgb[:, 0] > rgb[:, 2] + 40)
        frac = float(red.mean())
        worst = max(worst, frac)
        if frac > 0.002:
            bad.append(name)
    east = _a(art(d, "Modern", "RM_BankWeir_east"))
    al = east[..., 3] >= SOLID
    lum = _lum(east[..., :3])
    med = float(np.median(lum[al]))
    gy = np.abs(np.diff(lum, axis=0))[al[1:] & al[:-1]]
    gx = np.abs(np.diff(lum, axis=1))[al[:, 1:] & al[:, :-1]]
    hard = float(((gx > 25).mean() + (gy > 25).mean()) / 2)
    ok = not bad and med > 150 and hard < 0.06
    return ok, "red px worst %.4f %s; median lum %.0f (>150); hard edges %.3f (<0.06)" % (worst, bad or "", med, hard)


def zigzag_crest(d):
    east = art(d, "Futuristic", "RM_BankWeir_east")
    t = top_edge(east).astype(np.float32)
    if (t < 0).any():
        return False, "gaps in the wall"
    x = t - t.mean()
    amp = float(t.max() - t.min())
    ac = np.array([np.dot(x, np.roll(x, k)) for k in range(1, 129)]) / max(np.dot(x, x), 1e-6)
    lag = int(np.argmax(ac[32:]) + 33)
    ok = abs(lag - 64) <= 4 and ac[lag - 1] > 0.6 and amp >= 10
    # the N-S art carries the same two teeth a cell: the cyan crest strip's x along the rows repeats every 64 rows
    na = _a(art(d, "Futuristic", "RM_BankWeir_north"))
    cy = (na[..., 3] >= SOLID) & (na[..., 1] > 180) & (na[..., 2] > 180) & (na[..., 0] < 140)
    rows = cy.any(1)
    xs = np.array([np.nonzero(r)[0].mean() if r.any() else np.nan for r in cy])
    nlag, nr = None, 0.0
    if rows.mean() > 0.8:
        xs = np.where(np.isnan(xs), np.nanmean(xs), xs)
        y = xs - xs.mean()
        acn = np.array([np.dot(y, np.roll(y, k)) for k in range(1, 129)]) / max(np.dot(y, y), 1e-6)
        nlag = int(np.argmax(acn[32:]) + 33)
        nr = float(acn[nlag - 1])
    ok_n = nlag is not None and abs(nlag - 64) <= 4 and nr > 0.6
    return ok and ok_n, ("crest period %d px (64+-4, r %.2f > 0.6), amplitude %.0f px (>=10); north crest period %s rows"
                         " (64+-4, r %.2f > 0.6)" % (lag, ac[lag - 1], amp, nlag, nr))


IDENTITY = {"Scrapper": rubble_not_timber, "Industrial": three_steps, "Modern": smooth_no_red, "Futuristic": zigzag_crest}


# ---- every look ------------------------------------------------------------------------------------------------------
SIZES = {"RM_BankWeir_east": (256, 128), "RM_BankWeir_west": (256, 128), "RM_BankWeir_north": (128, 256),
         "RM_BankWeir_south": (128, 256), "RM_BankWeirCap": (128, 128), "RM_BankWeirSpill_east": (128, 128),
         "RM_BankWeirSpill_west": (128, 128), "RM_BankWeirSpill_north": (128, 128), "RM_BankWeirSpill_south": (128, 128)}


def common(d, look):
    """[(name, ok, detail)] for one look's set."""
    out = []
    ims = {n: art(d, look, n) for n in SIZES}
    bad = [n for n, s in SIZES.items() if ims[n].size != s]
    out.append(("canvas", not bad, "wrong size: %s" % bad if bad else "9 files at their canvases"))
    soft = []
    for n in SIZES:
        if n.startswith("RM_BankWeirSpill"):
            continue
        al = _a(ims[n])[..., 3]
        frac = float(((al > 0) & (al < 24)).sum()) / max(1, int((al > 0).sum()))
        if frac > 0:
            soft.append("%s %.3f" % (n, frac))
    out.append(("clean_alpha", not soft, "faint px: %s" % soft if soft else "no alpha below 24"))
    seam = []
    for n in ("RM_BankWeir_east", "RM_BankWeir_west", "RM_BankWeir_north", "RM_BankWeir_south"):
        a = _a(ims[n])
        e0, e1 = (a[:, 0], a[:, -1]) if a.shape[1] == 256 else (a[0], a[-1])
        m0, m1 = e0[:, 3] >= SOLID, e1[:, 3] >= SOLID
        iou = (m0 & m1).sum() / max(1, (m0 | m1).sum())
        both = m0 & m1
        dc = float(np.abs(e0[both, :3] - e1[both, :3]).mean()) if both.any() else 0.0
        if iou < 0.85 or dc > 30:
            seam.append("%s iou %.2f dc %.0f" % (n, iou, dc))
    out.append(("seamless", not seam, "; ".join(seam) or "joins match (alpha IoU >= 0.85, colour within 30)"))
    # a N-S run is sections end to end: the art's first and last 16 rows must not carry a darker band (the last plan
    # row's face left showing, which in game is a grey bar every 2 cells along the run)
    na = _a(ims["RM_BankWeir_north"])
    nl, nm = _lum(na[..., :3]), na[..., 3] >= SOLID
    wins = [float(nl[r:r + 16][nm[r:r + 16]].mean()) if nm[r:r + 16].any() else 0.0 for r in range(0, na.shape[0], 16)]
    # against the DARKEST interior window, not the median: a labyrinth's windows vary with the tooth phase (177..155
    # over each 64-row tooth), and an end that is only one phase of that cycle is drawn, not a band
    ref = float(min(wins[1:-1]))
    dark = [k for k, w in ((0, wins[0]), (len(wins) - 1, wins[-1])) if ref - w > 12]
    out.append(("north_ends_drawn", not dark, "16-row windows at the section ends vs the darkest interior lum %.0f: first "
                "%.0f, last %.0f (<= 12 darker)" % (ref, wins[0], wins[-1])))
    mir = (np.asarray(ims["RM_BankWeir_south"]) == np.asarray(ims["RM_BankWeir_north"])[:, ::-1]).all()
    out.append(("south_mirrors_north", bool(mir), "south == north mirrored" if mir else "south is not north mirrored"))
    # the crest sheet lies on the wall it pours over: drawn once per water cell, so every opaque sheet pixel must fall
    # inside the body's column span (top..toe, either half of the 2-cell section, 4 px slack), and it must cover some
    t, b = band_rows(ims["RM_BankWeir_east"])
    body = _a(ims["RM_BankWeir_east"])[..., 3] >= SOLID
    rr = np.arange(body.shape[0])[:, None]
    top = np.where(body, rr, body.shape[0]).min(0)
    bot = np.where(body, rr, -1).max(0)
    top, bot = np.minimum(top[:128], top[128:256]), np.maximum(bot[:128], bot[128:256])
    sp = _a(ims["RM_BankWeirSpill_east"])[..., 3] > 0
    ys, xs = np.nonzero(sp)
    off = float(((ys < top[xs] - 4) | (ys > bot[xs] + 4)).mean()) if ys.size else 1.0
    cover = float(sp.any(0).mean())
    ok = ys.size > 0 and off <= 0.02 and cover >= 0.9
    # judge 2026-10-24 on v6: "a thin bright white line crosses every look, only where the wall is over water" --
    # build.spill_south's flat 2-row lip (alpha 150, 245 grey). No sheet row may be a near-opaque white bar.
    bars = []
    for n in ("RM_BankWeirSpill_east", "RM_BankWeirSpill_west", "RM_BankWeirSpill_north"):
        q = _a(ims[n])
        if n.endswith("north"):
            q = q.transpose(1, 0, 2)
        hot = (q[..., 3] >= 120) & (_lum(q[..., :3]) >= 230)
        if (hot.mean(1) >= 0.9).any():
            bars.append(n)
    out.append(("spill_no_white_bar", not bars, "white bar rows in %s" % bars if bars else
                "no sheet row >= 90 % bright and alpha >= 120"))
    out.append(("spill_fitted", bool(ok), "body rows %d-%d; sheet px off the wall %.3f (<= 0.02), columns covered %.2f "
                "(>= 0.9)" % (t, b, off, cover)))
    return out


def _slab_mask(a):
    """weir_by_photo's labyrinth downstream bays (the falling water, 150,176,192 .. 214,232,242 before light): bluer than
    the white teeth (r/b 0.96), far less blue than the cyan strip (r/b 0.28)."""
    r, b = a[..., 0].astype(np.float32), a[..., 2].astype(np.float32)
    return (r < 0.92 * b) & (r > 0.6 * b) & (a[..., 3] >= 60)


def _slab_row(d, name):
    m = _slab_mask(_a(art(d, "Futuristic", name)))
    rows = np.nonzero(m.sum(1) > 20)[0]
    return float(np.average(rows, weights=m.sum(1)[rows])) if rows.size else None


def facing(d, look):
    """(ok, detail) or None where the look is symmetric across the wall (rubble)."""
    if look == "Scrapper":
        return None
    te, _ = band_rows(art(d, look, "RM_BankWeir_east"))
    tw, _ = band_rows(art(d, look, "RM_BankWeir_west"))
    north = _a(art(d, look, "RM_BankWeir_north"))
    al = north[..., 3] >= SOLID
    cols = np.nonzero(al.any(0))[0]
    c0, c1 = cols.min(), cols.max()
    lum = _lum(north[..., :3])
    # the crest is the highest, flattest top: brightest columns (Industrial's crest slab); the
    # labyrinth's teeth are one height both ways: its downstream bays carry the falling water
    colmean = np.array([np.median(lum[al[:, c], c]) if al[:, c].any() else 0 for c in range(north.shape[1])])
    if look == "Futuristic":
        sm = _slab_mask(north)
        cols_w = sm.sum(0)
        where = float(np.average(np.arange(sm.shape[1]), weights=cols_w)) if cols_w.sum() else float(c0)
        # E/W: the water-filled bays lie downstream: near (low) in east, far (high) in west
        se, sw = _slab_row(d, "RM_BankWeir_east"), _slab_row(d, "RM_BankWeir_west")
        rel = (where - c0) / max(1, c1 - c0)
        ok = se is not None and sw is not None and se > sw + 8 and rel >= 0.55
        return ok, "water bays centre row east %s vs west %s (east >= 8 lower); north bays centre at %.2f of the band" \
                   " (>= 0.55, downstream right)" % (None if se is None else round(se), None if sw is None else round(sw), rel)
    elif look == "Modern":
        # the crest is the warm dry slab; the curtain below it is a blue-white water sheet, often brighter (v12), so
        # the crest is the column whose median is least blue, not the brightest
        warm = north[..., 0].astype(np.float32) - north[..., 2].astype(np.float32)
        colwarm = np.array([np.median(warm[al[:, c], c]) if al[:, c].any() else -999 for c in range(north.shape[1])])
        where = float(np.argmax(colwarm))
    else:
        where = float(np.argmax(colmean))
    rel = (where - c0) / max(1, c1 - c0)
    ok = te <= tw - 8 and rel <= 0.45
    return ok, "east crest row %d vs west %d (>= 8 higher); north crest at %.2f of the band (<= 0.45, upstream left)" % (
        te, tw, rel)


def terrain_is_vanilla(img, meta):
    """The ground in an open water cell and an open bank cell matches the vanilla colours (no stand-in floor)."""
    a = np.asarray(img.convert("RGB"), np.float32)
    P, h = meta["P"], meta["h"]
    cell = lambda x, z: a[(h - 1 - z) * P + P // 4:(h - z) * P - P // 4, x * P + P // 4:(x + 1) * P - P // 4]
    if meta["kind"] == "ew":
        wc, bc = cell(3, 4), cell(0, 4)
    else:
        wc, bc = cell(0, 3), cell(0, 0)
    wm, bm = wc.reshape(-1, 3).mean(0), bc.reshape(-1, 3).mean(0)
    dw = float(np.abs(wm - np.array(water_rgb())).max())
    db = float(np.abs(bm - np.array(bank_rgb())).max())
    return dw < 6 and db < 12, "water %s vs vanilla %s (d %.1f); bank d %.1f" % (
        tuple(int(v) for v in wm), tuple(int(v) for v in water_rgb()), dw, db)


def check_all(d):
    """{look: [(name, ok, detail)]} -- identity, common, facing."""
    res = {}
    for look in LOOKS:
        ok, det = IDENTITY[look](d)
        rows = [(IDENTITY[look].__name__, ok, det)] + common(d, look)
        f = facing(d, look)
        if f is not None:
            rows.append(("facing", f[0], f[1]))
        res[look] = rows
    return res


# ---- the owner sheet ------------------------------------------------------------------------------------------------
def sheet(before, after, out, P=96):
    """SHEET_weir.png: per look, BEFORE (E-W) | AFTER (E-W) | AFTER (N-S), on the game's river and bank."""
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    tiles = []
    for look in LOOKS:
        row = []
        for d, kind, tag in ((before, "ew", "BEFORE"), (after, "ew", "AFTER"), (after, "ns", "AFTER")):
            im, _ = scene(look, d, kind, P=P)
            im.save(out / ("%s_%s_%s.png" % (look, tag.lower(), kind)))
            row.append((im, "%s %s %s" % (look, tag, "E-W run, river flows south" if kind == "ew" else
                                           "N-S run, river flows east")))
        tiles.append(row)
    pad, lab = 12, 22
    colw = [max(r[i][0].width for r in tiles) for i in range(3)]
    rowh = [max(t[0].height for t in r) for r in tiles]
    W = sum(colw) + pad * 4
    H = sum(rowh) + (pad + lab) * len(tiles) + pad
    cv = Image.new("RGB", (W, H), (30, 30, 30))
    dr = ImageDraw.Draw(cv)
    f = fc.font(16)
    y = pad
    for r, hgt in zip(tiles, rowh):
        x = pad
        for (im, txt), cw in zip(r, colw):
            dr.text((x, y), txt, fill=(235, 235, 235), font=f)
            cv.paste(im.convert("RGB"), (x, y + lab))
            x += cw + pad
        y += hgt + lab + pad
    cv.save(out / "SHEET_weir.png")
    return out / "SHEET_weir.png"


def main(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--before", default=str(INSTALLED))
    ap.add_argument("--after", default=str(INSTALLED))
    a = ap.parse_args(argv)
    for name, d in (("before", a.before), ("after", a.after)):
        for look, rows in check_all(d).items():
            for n, ok, det in rows:
                print("%-6s %-10s %-20s %s %s" % (name, look, n, "PASS" if ok else "FAIL", det))
    print(sheet(a.before, a.after, a.out))


if __name__ == "__main__":
    main(sys.argv[1:])
