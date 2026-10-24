#!/usr/bin/env python3
"""Offline pit-spike scenes and checks (PIT_SPIKES_FIX_OVER_WALL_AND_SUBMERGE).

Owner 2026-10-24: "you can see the spi[k]es aren't right. They should not be showing drawn over the paler walls, right?
And I needed deeper water to test the spikes. They should be shown as submerged rapidly."

What it emulates (read from the C#, not guessed):
  * RM_ExcavationWalls (TerrainScatter + 0.003): per dug cell of depth d, neighbour levels by NeighbourLevel (off-grid =
    level); the far-wall face band z in [1 - NorthFaceHeight(ExposedDrop(d, n, f)), 1], the side faces SideFaceWidth wide,
    and the black outline (RimLine on the north, SideLine on west/east, SouthLining(d - s) on the south) from the DRY
    drop. Colours are stand-ins (pale face, paler-than-floor bevels, black outline); the checks read masks, not colours.
  * RM_LiquidSurface (TerrainScatter + 0.01): a translucent water film over a cell with fill > 0.
  * the spikes (Building altitude, above all of that): BEFORE = the shipped Graphic_Random sprite on the whole 1x1 cell at
    full opacity; AFTER = Building_RM_Spikes: RM_SpikeDrawMath.Layout's stakes (sampled from the variant's stake atlas,
    art_source/Spikes/atlas/ == the installed RM_SpikeStakes textures) inside FloorRect, opacity
    SubmergedAlpha(fill) quantised to 1/32 as the C# does. The math below mirrors RM_SpikeDrawMath bit for bit (Hash) and
    to float precision (Layout); SpikeDrawChecks.Spikes_parity_fixture_matches_python holds the two together with
    PARITY below.

Floors (PIT_SPIKES_FIX_READ_AS_FUZZ_LIVE): render(floor="standin") is the flat grey the owner-approved sheet was drawn on;
floor="real" is the game's dug-floor terrain (vanilla Gravel x RM_Channel_* <color>), which live fwclose_03 matches.
  floor_matches_live(floor) -> the D4 floor's luminance == live's: FAILS on "standin", PASSES on "real"/"real_flat"

Checks (each FAILS on the shipped drawing and PASSES on the fix; selftest_fw_offline_art.py runs both):
  spikes_over_wall(res)  -> 0 spike pixels on the dry face bands or the outline
  spikes_submerged(res)  -> per spiked cell: visible dry, fading with every level of water, gone (alpha 0) from 1 m
  same_as_approved(after, clean, approved) -> the owner approved the 4f12810a3e render ("spikes look great!": the same
                            layout sampling the sprite through approved/RM_SpikeStakes_4f12810a3e.cs.txt). AFTER must equal,
                            at EVERY pixel, that render with only the slivers' alpha cleared (mode "approved_clean"), and
                            that one may differ from the approved render only inside the slivers' footprint (["sliver"])

    python3 fw_scenes_spikes.py <out_dir>     # owner sheet SHEET_spikes.png + before/after scenes
"""
import math
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
FW = HERE.parent
sys.path.insert(0, str(FW / "art_source" / "Spikes"))
import stakes as STAKES  # noqa: E402

TEXDIR = FW / "Textures/Things/Building/FlowWorks/Canals/RM_Spikes"
MATH_CS = FW / "Source/Superdeep/RM_SpikeDrawMath.cs"
WALL_CS = FW / "Source/RM_WallFaceMath.cs"
APPROVED_CS = FW / "art_source/Spikes/approved/RM_SpikeStakes_4f12810a3e.cs.txt"   # the library the owner approved
APPROVED_PNG = FW / "art_source/Spikes/approved/RM_Spikes_4f12810a3e.sha256"       # ... and the sprites it sampled
SLIVER_REACH = 4                # scene px a sliver texel reaches: PIL's Lanczos has a 3-dest-px radius when downscaling, + 1


def _cs_array(name):
    m = re.search(r"%s\s*=\s*\{([^}]*)\}" % name, WALL_CS.read_text())
    return [float(v.strip().rstrip("f")) for v in m.group(1).split(",")]


def _cs_const(path, name):
    return float(re.search(r"const float %s\s*=\s*([0-9.]+)f" % name, path.read_text()).group(1))


# ---- RM_WallFaceMath, read from the C# source so the tables cannot drift --------------------------------------------
NORTH = _cs_array("NorthByDrop")
SIDE = _cs_array("SideByDrop")
SOUTH = _cs_array("SouthLiningByDrop")
RIM_LINE = _cs_const(WALL_CS, "RimLine")
SIDE_LINE = _cs_const(WALL_CS, "SideLine")
MARGIN = _cs_const(MATH_CS, "Margin")
SUBMERGE_M = _cs_const(MATH_CS, "SubmergeMetres")
METRES_PER_LEVEL = 0.5          # RM_Volume.MetresPerLevel (SelfTest VolumeChecks asserts 0.5)
ALPHA_STEPS = 32                # Building_RM_Spikes.AlphaSteps


def _tab(t, k):
    return 0.0 if k <= 0 else t[min(k, len(t) - 1)]


def exposed_drop(d, n, f):
    drop = d - n
    return 0 if drop <= 0 else max(0, drop - max(0, f))


def floor_rect(d, n, s, w, e, faces=True, outline=True):
    lines = faces and outline
    top = left = right = bottom = 0.0
    if faces:
        top, left, right = _tab(NORTH, exposed_drop(d, n, 0)), _tab(SIDE, exposed_drop(d, w, 0)), _tab(SIDE, exposed_drop(d, e, 0))
    if lines:
        if d - n > 0:
            top = max(top, RIM_LINE)
        if d - w > 0:
            left = max(left, SIDE_LINE)
        if d - e > 0:
            right = max(right, SIDE_LINE)
        if d - s > 0:
            bottom = _tab(SOUTH, d - s)
    return left, bottom, 1 - right, 1 - top


def submerged_alpha(fill):
    if fill <= 0:
        return 1.0
    t = 1 - fill * METRES_PER_LEVEL / SUBMERGE_M
    return 0.0 if t <= 0 else t * t


def hash32(seed, k):
    M = 0xFFFFFFFF
    x = ((seed & M) * 0x9E3779B1 + (k & M) * 0x85EBCA77) & M
    x ^= x >> 15
    x = (x * 0x2C1B3C6D) & M
    x ^= x >> 12
    x = (x * 0x297A2D39) & M
    x ^= x >> 15
    return x


_LIB = {}
_r6 = lambda q: float(np.float32(float("%.6f" % q)))     # the C# reads these as %.6f float literals


def library(variant):
    if variant not in _LIB:
        lib, pitch = STAKES.library(STAKES.VARIANTS[variant])
        _LIB[variant] = [tuple(_r6(q) for q in st) for st in lib], tuple(_r6(q) for q in pitch)
    return _LIB[variant]


def approved_library(variant):
    """The owner-approved (4f12810a3e) stakes and pitch of variant index `variant`, read from the pinned C#: UVs into the
    shipped sprite, boxes carrying the neighbours' slivers."""
    t = APPROVED_CS.read_text()
    blocks = re.findall(r"new float\[\] \{(.*?)\}", t, re.S)
    pitch = re.findall(r"\{ ([0-9.]+)f, ([0-9.]+)f \}", t)[variant]
    lib = [tuple(_r6(float(q)) for q in re.findall(r"-?[0-9]+\.[0-9]+", ln)) for ln in blocks[variant].strip().split("\n")]
    return lib, tuple(_r6(float(q)) for q in pitch)


def approved_foreign(variant):
    """{approved UV box: its foreign (sliver) mask in sprite px} for variant index `variant`. Raises unless the approved
    boxes are exactly stakes._cut's windows, in order (the masks would otherwise sit on the wrong box)."""
    lib, _ = approved_library(variant)
    cut, _, S = STAKES._cut(STAKES.VARIANTS[variant])
    uv = [tuple(_r6(q) for q in (X0 / S, 1 - (Y1 + 1) / S, (X1 + 1) / S, 1 - Y0 / S)) for X0, Y0, X1, Y1, _, _ in cut]
    if [st[2:] for st in lib] != uv:
        raise ValueError("variant %s: the approved boxes are not stakes._cut's windows (%d vs %d)"
                         % (STAKES.VARIANTS[variant], len(lib), len(uv)))
    return {u: c[5] for u, c in zip(uv, cut)}


def layout(variant, seed, x0, z0, x1, z1, lib=None):
    """RM_SpikeDrawMath.Layout: [(x, z, w, h, u0, v0, u1, v1)] far (north) first. lib: (stakes, pitch) to lay out instead
    of the current library (the approved one, for the comparison render)."""
    lib, (ppx, ppz) = lib or library(variant)
    n = len(lib)
    wmax, hmax = max(s[0] for s in lib), max(s[1] for s in lib)
    fw, fh = x1 - x0 - 2 * MARGIN, z1 - z0 - 2 * MARGIN
    if n == 0 or fw <= 0 or fh <= 0:
        return []
    sc = min(1.0, fh / hmax, fw / wmax)
    px, pz = ppx * sc, ppz * sc
    lo, hi, bot, top = x0 + MARGIN, x1 - MARGIN, z0 + MARGIN, z1 - MARGIN
    clamp = lambda v, a, b: a if v < a else (b if v > b else v)
    out, k, r = [], 0, 0
    while bot + r * pz <= top - hmax * sc * 0.5:
        zb = bot + r * pz
        x00 = lo + (px * 0.5 if r & 1 else 0.0)
        col = 0
        while x00 + col * px <= hi:
            xc = x00 + col * px
            h = hash32(seed, k)
            st = lib[h % n]
            w, ht = st[0] * sc, st[1] * sc
            jx = (((h >> 8) & 0xFF) / 255 - 0.5) * 0.5 * px
            jz = (((h >> 16) & 0xFF) / 255 - 0.5) * 0.5 * pz
            out.append((clamp(xc + jx - w * 0.5, lo, hi - w), clamp(zb + jz, bot, top - ht), w, ht) + tuple(st[2:]) + (k,))
            col += 1
            k += 1
        r += 1
    out.sort(key=lambda q: (-q[1], q[8]))
    return [q[:8] for q in out]


# Parity fixture: SpikeDrawChecks.Spikes_parity_fixture_matches_python asserts the same numbers from the C#.
PARITY_HASHES = ((0, 0), (12345, 7), (-3, 99))
PARITY_LAYOUT = (1, 42, 0.04, 0.065, 0.96, 0.5)     # variant b, seed 42, a D4-under-the-north-rim floor


def parity():
    """(hashes, (count, first quad, last quad)) for the fixture."""
    q = layout(*PARITY_LAYOUT)
    return [hash32(s, k) for s, k in PARITY_HASHES], (len(q), q[0], q[-1])


# ---- the scene ---------------------------------------------------------------------------------------------------------
SOIL = (108, 86, 62)
FACE = (176, 152, 120)      # the pale far wall (RM_WallFaceMath.WallFaceLight 1.85 x a dark top)
BEVEL = (138, 118, 94)      # side bevels (WallSideLight 1.29)
WATER = (52, 92, 120, 150)


def _floor(d):
    """The STAND-IN floor the owner-approved 4f12810a3e sheet was composited on: a flat grey that darkens with depth.
    It is NOT what the game draws (see real_floor) -- PIT_SPIKES_FIX_READ_AS_FUZZ_LIVE."""
    k = max(0.45, 1 - 0.08 * d)
    return tuple(int(c * k) for c in (92, 82, 70))


# ---- the REAL dug floor (PIT_SPIKES_FIX_READ_AS_FUZZ_LIVE) -----------------------------------------------------------
# A dry dug cell's terrain is RM_ExcavationDepth.DryTerrainFor(d): RM_Channel_Empty / _Mid / _Deep / _Superdeep (d >= 4),
# every one the vanilla Terrain/Surfaces/Gravel texture times the def's <color> (read from the XML below, never typed in).
# Gravel lives in the base game's resources.assets; the extract is read from $RM_VANILLA_TEX (a directory holding
# Gravel.png). Without it the floor is the texture's measured mean, flat (GRAVEL_MEAN; the checks use only that).
# Calibration, live fwclose_03 (3x3 D4 pit, 83 px/cell): floor lum 27.7 (rgb 36,26,16) against GRAVEL_MEAN x Superdeep
# = lum 28.1 (rgb 35,27,19); the stand-in drew lum 56 grey there.
TERRAIN_XML = FW / "Defs/Canals/TerrainDefs/FlowWorks_Terrain.xml"
FLOOR_DEFS = ("RM_Channel_Empty", "RM_Channel_Mid", "RM_Channel_Deep", "RM_Channel_Superdeep")   # d = 1, 2, 3, >= 4
GRAVEL_MEAN = (91.2, 73.6, 57.3)       # vanilla Gravel.png (1024 px), mean rgb over every pixel
GRAVEL_CELLS = 10                      # cells one texture repeat spans: of 1..16 the closest to the live floor's grain
VANILLA_TEX_DEFAULT = "/mnt/d/ClaudeWork/rimmandrake/scratch/vanilla_tex/ludeon.rimworld.core"


def floor_tints():
    """{d: (r, g, b) multiplier} from the terrain defs; a def with no <color> is white (TerrainDef's default)."""
    import xml.etree.ElementTree as ET
    found = {}
    for t in ET.parse(TERRAIN_XML).getroot().iter("TerrainDef"):
        name = t.findtext("defName")
        if name in FLOOR_DEFS:
            c = t.findtext("color")
            found[name] = tuple(float(v) for v in c.strip("() ").split(",")[:3]) if c else (1.0, 1.0, 1.0)
    missing = [n for n in FLOOR_DEFS if n not in found]
    if missing:
        raise SystemExit("fw_scenes_spikes: %s has no %s" % (TERRAIN_XML, missing))
    return {i + 1: found[n] for i, n in enumerate(FLOOR_DEFS)}


_GRAVEL = {}


def gravel(P, flat=False):
    """The Gravel texture at P px/cell, one repeat per GRAVEL_CELLS cells (float rgb), or None (flat / not extracted)."""
    if flat:
        return None
    if P not in _GRAVEL:
        import os
        f = Path(os.environ.get("RM_VANILLA_TEX", VANILLA_TEX_DEFAULT)) / "Gravel.png"
        side = round(GRAVEL_CELLS * P)
        _GRAVEL[P] = np.asarray(Image.open(f).convert("RGB").resize((side, side), Image.LANCZOS), np.float32) \
            if f.is_file() else None
    return _GRAVEL[P]


def real_floor_rgb(d):
    t = floor_tints()[min(max(d, 1), 4)]
    return tuple(m * k for m, k in zip(GRAVEL_MEAN, t))


class Pit:
    """depth[z][x] / fill[z][x] grids given NORTH ROW FIRST (as drawn); spikes = set of (x, z) cell coords (z north)."""

    def __init__(self, depth_rows, fill_rows=None, spikes=(), seeds=None, variant_of=None):
        self.H, self.W = len(depth_rows), len(depth_rows[0])
        self.d = [list(r) for r in reversed(depth_rows)]
        self.f = [list(r) for r in reversed(fill_rows)] if fill_rows else [[0] * self.W for _ in range(self.H)]
        self.spikes = set(spikes)
        self.seeds = seeds or {}
        self.variant_of = variant_of or {}

    def depth(self, x, z):
        return self.d[z][x]

    def level(self, x, z, mine):
        """NeighbourLevel: off-grid is level with this cell."""
        return mine if not (0 <= x < self.W and 0 <= z < self.H) else self.d[z][x]

    def nbrs(self, x, z):
        d = self.d[z][x]
        return d, self.level(x, z + 1, d), self.level(x, z - 1, d), self.level(x - 1, z, d), self.level(x + 1, z, d)


def _dilate(m, r):
    out = m.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            sh = np.zeros_like(m)
            sh[max(0, dy):m.shape[0] + min(0, dy), max(0, dx):m.shape[1] + min(0, dx)] = \
                m[max(0, -dy):m.shape[0] + min(0, -dy), max(0, -dx):m.shape[1] + min(0, -dx)]
            out |= sh
    return out


def render(pit, mode="after", P=160, faces=True, outline=True, atlases=None, floor="standin"):
    """-> dict(img, spike_a (H,W float 0..1 spike-layer alpha), wall (H,W bool dry face bands + outline), cells, sliver,
    used {variant index: UV boxes drawn}). mode: "before" the shipped sprite on the whole cell; "after" the fix (stake
    atlas, or atlases[name] when given); "approved" the owner-approved layout sampling the sprite through the pinned
    library, its `sliver` mask every scene pixel a neighbour's sliver inside a box can reach (dilated by SLIVER_REACH);
    "approved_clean" the same with each box's slivers' alpha cleared. floor: "standin" (the approved sheet's grey),
    "real" (the game's dug-floor terrain: Gravel x the depth's def colour), "real_flat" (that, at the texture's mean)."""
    W, H = pit.W * P, pit.H * P
    rgb = np.zeros((H, W, 3), np.float32)
    wall = np.zeros((H, W), bool)
    rgb[:] = SOIL
    box = lambda x, z, a0, b0, a1, b1: (round((pit.H - z - b1) * P), round((pit.H - z - b0) * P), round((x + a0) * P), round((x + a1) * P))

    def fill_box(x, z, a0, b0, a1, b1, col=None, mark=False):
        r0, r1, c0, c1 = box(x, z, a0, b0, a1, b1)
        if col is not None:
            rgb[r0:r1, c0:c1] = col
        if mark:
            wall[r0:r1, c0:c1] = True

    for z in range(pit.H):
        for x in range(pit.W):
            d, n, s, w, e = pit.nbrs(x, z)
            if d <= 0:
                continue
            f = pit.f[z][x]
            if floor == "standin":
                fill_box(x, z, 0, 0, 1, 1, _floor(d))
            else:
                tex, tint = gravel(P, floor == "real_flat"), floor_tints()[min(d, 4)]
                r0, r1, c0, c1 = box(x, z, 0, 0, 1, 1)
                if tex is None:
                    rgb[r0:r1, c0:c1] = real_floor_rgb(d)
                else:
                    n = tex.shape[0]
                    rr, cc = np.arange(r0, r1) % n, np.arange(c0, c1) % n
                    rgb[r0:r1, c0:c1] = tex[np.ix_(rr, cc)] * np.array(tint, np.float32)
            if not faces:
                continue
            # the faces as drawn (wet: water covers the foot) and as the wall really stands (dry: the check's mask)
            for drop_fill, paint in ((0, False), (f, True)):
                h = _tab(NORTH, exposed_drop(d, n, drop_fill))
                ww, ew = _tab(SIDE, exposed_drop(d, w, drop_fill)), _tab(SIDE, exposed_drop(d, e, drop_fill))
                if h > 0:
                    fill_box(x, z, 0, 1 - h, 1, 1, FACE if paint else None, mark=not paint)
                if ww > 0:
                    fill_box(x, z, 0, 0, ww, 1, BEVEL if paint else None, mark=not paint)
                if ew > 0:
                    fill_box(x, z, 1 - ew, 0, 1, 1, BEVEL if paint else None, mark=not paint)
            if outline:
                k = (0, 0, 0)
                if d - s > 0:
                    fill_box(x, z, 0, 0, 1, _tab(SOUTH, d - s), k, True)
                if d - n > 0:
                    fill_box(x, z, 0, 1 - RIM_LINE, 1, 1, k, True)
                if d - w > 0:
                    fill_box(x, z, 0, 0, SIDE_LINE, 1, k, True)
                if d - e > 0:
                    fill_box(x, z, 1 - SIDE_LINE, 0, 1, 1, k, True)
    for z in range(pit.H):
        for x in range(pit.W):
            if pit.f[z][x] > 0 and pit.d[z][x] > 0:
                r0, r1, c0, c1 = box(x, z, 0, 0, 1, 1)
                a = WATER[3] / 255
                rgb[r0:r1, c0:c1] = rgb[r0:r1, c0:c1] * (1 - a) + np.array(WATER[:3]) * a
    spike = np.zeros((H, W, 4), np.float32)
    sliver = np.zeros((H, W), bool)
    cells, used = {}, {}
    for (x, z) in sorted(pit.spikes):
        v = pit.variant_of.get((x, z), (x * 7 + z * 3) % 3)
        name = STAKES.VARIANTS[v]
        if mode == "after":
            src = (atlases or {}).get(name)
            if src is None:
                src = Image.open(STAKES.ATLAS_SRC / (STAKES.atlas_name(name) + ".png")).convert("RGBA")
        else:
            src = Image.open(TEXDIR / ("RM_Spikes_%s.png" % name)).convert("RGBA")
        lib = approved_library(v) if mode.startswith("approved") else None
        foreign = approved_foreign(v) if lib else {}
        SW, SH = src.size
        quads, alpha, laid = [], 1.0, 0
        if mode == "before":
            quads = [(0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0)]
            laid = 1
        else:
            d, n, s, w, e = pit.nbrs(x, z)
            a = round(submerged_alpha(pit.f[z][x]) * ALPHA_STEPS)
            alpha = a / ALPHA_STEPS
            if d > 0:
                quads = layout(v, pit.seeds.get((x, z), x * 1000 + z), *floor_rect(d, n, s, w, e, faces, outline), lib=lib)
                laid = len(quads)          # the stakes the cell has dry: a deep cell must have some to hide
            if a <= 0:
                quads = []
        cells[(x, z)] = dict(alpha=alpha, quads=len(quads), laid=laid, fill=pit.f[z][x])
        for (qx, qz, qw, qh, u0, v0, u1, v1) in quads:
            crop = src.crop((round(u0 * SW), round((1 - v1) * SH), round(u1 * SW), round((1 - v0) * SH)))
            fm = foreign.get((u0, v0, u1, v1))
            if mode == "approved_clean":
                c = np.asarray(crop).copy()
                c[fm, 3] = 0
                crop = Image.fromarray(c, "RGBA")
            r0, r1, c0, c1 = box(x, z, qx, qz, qx + qw, qz + qh)
            if r1 <= r0 or c1 <= c0:
                continue
            used.setdefault(v, set()).add((u0, v0, u1, v1))    # laid out with scene px (may still sit under a later stake)
            t = np.asarray(crop.resize((c1 - c0, r1 - r0), Image.LANCZOS), np.float32) / 255
            if fm is not None and fm.any():
                fr = np.asarray(Image.fromarray(fm.astype(np.uint8) * 255).resize((c1 - c0, r1 - r0), Image.BOX)) > 0
                sliver[r0:r1, c0:c1] |= fr
            t[..., 3] *= alpha
            dst = spike[r0:r1, c0:c1]
            a_new = t[..., 3:4]
            dst[..., :3] = t[..., :3] * a_new + dst[..., :3] * (1 - a_new)
            dst[..., 3:4] = a_new + dst[..., 3:4] * (1 - a_new)
    sa = spike[..., 3:4]
    out = rgb * (1 - sa) + spike[..., :3] * 255 * sa
    img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGB")
    return dict(img=img, spike_a=spike[..., 3], wall=wall, cells=cells, P=P, pit=pit, sliver=_dilate(sliver, SLIVER_REACH),
                used=used)


LIVE_FLOOR_D4 = (36, 26, 16)    # live fwclose_03 (2026-10-24, 83 px/cell): median of the 3x3 D4 pit's floor between stakes
LIVE_FLOOR_TOL = 3.0            # luminance steps


def floor_matches_live(floor):
    """(ok, detail): the compositor's dry D4 floor (no stakes) has the live floor's luminance. FAILS on the stand-in the
    approved sheet used (lum 56 grey vs live 28 brown: why stakes that read on the sheet read as fuzz in the game)."""
    rows = [[4] * 3] * 3
    img = np.asarray(render(Pit(rows), "after", P=83, floor=floor)["img"], np.float32)
    lum = lambda c: float(np.dot(c, (0.299, 0.587, 0.114)))
    got, want_l = float(np.median(img.reshape(-1, 3) @ np.array((0.299, 0.587, 0.114)))), lum(LIVE_FLOOR_D4)
    return abs(got - want_l) <= LIVE_FLOOR_TOL, "floor=%s lum %.1f vs live %.1f (tol %.0f)" % (floor, got, want_l, LIVE_FLOOR_TOL)


# ---- checks ------------------------------------------------------------------------------------------------------------
VISIBLE = 8 / 255   # a spike pixel counts as drawn from this alpha (an offline convention: the Transparent shader draws any alpha)


def spikes_over_wall(res):
    """No spike pixel on the pit's far-wall face, side bevels or outline (the dry geometry: where the wall stands)."""
    if not res["cells"]:
        return False, "no spikes in the scene"
    drawn = res["spike_a"] > VISIBLE
    if not drawn.any():
        return False, "no spike pixel drawn at all (vacuous)"
    if not res["wall"].any():
        return False, "scene has no wall face (vacuous)"
    bad = int((drawn & res["wall"]).sum())
    return bad == 0, "%d spike px over the wall faces/outline (of %d spike px)" % (bad, int(drawn.sum()))


def spikes_submerged(res):
    """Per spiked cell, its brightest spike pixel's alpha against the water depth: 1 dry, strictly less with every level,
    0 from SUBMERGE_M. Needs a dry cell and a cell at or past SUBMERGE_M in the scene."""
    P, pit = res["P"], res["pit"]
    by_fill = {}
    for (x, z), c in res["cells"].items():
        r0, c0 = (pit.H - z - 1) * P, x * P
        a = float(res["spike_a"][r0:r0 + P, c0:c0 + P].max())
        by_fill.setdefault(c["fill"], []).append(a)
    fills = sorted(by_fill)
    deep = [f for f in fills if f * METRES_PER_LEVEL >= SUBMERGE_M]
    if 0 not in by_fill or not deep:
        return False, "scene needs a dry spiked cell and one under >= %.1f m (has fills %s)" % (SUBMERGE_M, fills)
    peak = {f: max(v) for f, v in by_fill.items()}
    why = ["%.1f m cell %s has no stakes even dry (nothing to submerge)" % (c["fill"] * METRES_PER_LEVEL, xz)
           for xz, c in sorted(res["cells"].items()) if c["fill"] in deep and not c["laid"]]
    if peak[0] < 0.99:
        why.append("dry spikes not fully visible (%.2f)" % peak[0])
    for a, b in zip(fills, fills[1:]):
        if peak[b] >= peak[a] and peak[a] > 0:
            why.append("no fade from %.1f m to %.1f m (%.2f -> %.2f)" % (a * METRES_PER_LEVEL, b * METRES_PER_LEVEL, peak[a], peak[b]))
    for f in deep:
        if peak[f] > 0:
            why.append("still drawn under %.1f m (alpha %.2f)" % (f * METRES_PER_LEVEL, peak[f]))
    table = ", ".join("%.1f m %.2f" % (f * METRES_PER_LEVEL, peak[f]) for f in fills)
    return not why, ("; ".join(why) + " | " if why else "") + table


def same_as_approved(after, clean, approved):
    """AFTER == the approved render but for the slivers: AFTER equals `clean` (render "approved_clean") at every pixel,
    and `clean` differs from `approved` (render "approved") only inside approved["sliver"]. Refuses a scene with no
    sliver or one that does not lay out every stake of every variant it draws (a stake never drawn is never compared)."""
    sl = approved["sliver"]
    if not sl.any():
        return False, "scene has no sliver (vacuous)"
    unused = ["%s %d/%d" % (STAKES.VARIANTS[v], len(u), len(approved_library(v)[0])) for v, u in sorted(approved["used"].items())
              if len(u) != len(approved_library(v)[0])]
    if unused or after["used"].keys() != approved["used"].keys():
        return False, "scene does not draw every stake (%s)" % (", ".join(unused) or "variants drawn differ: %s vs %s"
                                                               % (sorted(after["used"]), sorted(approved["used"])))
    diff = lambda r, q: (np.asarray(r["img"], np.int16) != np.asarray(q["img"], np.int16)).any(-1) | \
        (r["spike_a"] != q["spike_a"])
    exact, near = int(diff(after, clean).sum()), diff(clean, approved)
    out_n = int((near & ~sl).sum())
    return exact == 0 and out_n == 0, ("%d px differ from the approved render minus slivers; vs the approved render %d px "
                                       "differ outside the slivers, %d inside (footprint %d px)"
                                       % (exact, out_n, int((near & sl).sum()), int(sl.sum())))


# ---- scenes ------------------------------------------------------------------------------------------------------------
def check_pit():
    """A 4 m-deep pit (8 levels) with a 2 m shelf on the east and a 0-4 level water series along its south row, spikes
    everywhere the walls give a drop: the far wall, both side walls, corners, the shelf step, open floor, the near edge."""
    depth = [
        [0, 0, 0, 0, 0, 0, 0],
        [0, 8, 8, 8, 8, 4, 0],
        [0, 8, 8, 8, 8, 4, 0],
        [0, 8, 8, 8, 8, 8, 0],
        [0, 0, 0, 0, 0, 0, 0],
    ]
    fill = [
        [0] * 7,
        [0] * 7,
        [0] * 7,
        [0, 0, 1, 2, 3, 4, 0],
        [0] * 7,
    ]
    spikes = [(x, z) for x in range(1, 6) for z in range(1, 4)]
    return Pit(depth, fill, spikes)


def compare_pit():
    """A 4 m pit, 5 x 4 cells, spiked everywhere, its south row under 0.5 m: big enough that the layout draws every stake
    of every variant (same_as_approved refuses a scene that does not), with the walls' cut and a half-faded row."""
    depth = [[0] * 7] + [[0, 8, 8, 8, 8, 8, 0] for _ in range(4)] + [[0] * 7]
    fill = [[0] * 7 for _ in range(4)] + [[0, 1, 1, 1, 1, 1, 0], [0] * 7]
    return Pit(depth, fill, [(x, z) for x in range(1, 6) for z in range(1, 5)])


if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    out.mkdir(parents=True, exist_ok=True)
    res = {}
    for mode in ("before", "approved", "approved_clean", "after"):
        res[mode] = r = render(check_pit(), mode)
        r["img"].save(out / ("spikes_%s.png" % mode))
        print(mode, spikes_over_wall(r), spikes_submerged(r))
    cmp = {m: render(compare_pit(), m) for m in ("after", "approved_clean", "approved")}
    print("after vs approved", same_as_approved(cmp["after"], cmp["approved_clean"], cmp["approved"]))
