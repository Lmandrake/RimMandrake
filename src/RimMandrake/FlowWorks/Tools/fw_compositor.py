#!/usr/bin/env python3
"""Offline FlowWorks compositor: draw our real textures the way the game layers them, so a join, a seat or a cover can be
rendered and judged without a game load (owner 2026-10-24: "I think you could work out most of this is Python too without
wasting game time").

What it emulates (read from the defs and C#, not guessed):
  * the cell grid: x east, z north, cell (x, z) spans [x, x+1] x [z, z+1]; image y grows DOWN, so image row = (H - z) * P.
  * altitude: every draw carries its AltitudeLayer (order below) plus the small y offsets the C# adds (FloorEmplacement
    + 0.02 for the flange, - 0.002 for the stub layer); draws are sorted by that, ties keep call order (as a section mesh).
  * Graphic_Linked (Basic): mask = Up 1 | Right 2 | Down 4 | Left 8 of the cells it links with; the tile is
    MaterialAtlasPool.SubMaterialFromAtlas: block (mask % 4, mask // 4) counted from the atlas's BOTTOM-left, of which the
    inner 3/16 (1/32 inset each side of the 1/4 block) is drawn on a 1x1 plane (same crop as art_source/Pump/preview_pipes.py).
  * Graphic_Single / Graphic_Multi: the texture on a drawSize plane centred on the thing's footprint centre + drawOffset
    (drawSize and drawOffset are passed by the scene, copied from the def; RM_LiquidTank is (2,2), no offset).
  * Printer_Plane rotation: Quaternion.Euler(0, a, 0) turns CLOCKWISE on screen for positive a (Unity's y-up, z-north).
  * curved pipe: a strip that carries the straight E-W tile's cross-section along a path of lines and arcs (u = distance
    along the path, v = signed offset across it) -- the same mapping the C# riser bend prints as a mesh strip.

Usage (library): from fw_compositor import Scene; s = Scene(w, h, px=96); s.pipe(...); s.render().save(path)
Scenes: fw_scenes_pipejoins.py beside this file (pipe joins); machine checks on the renders: fw_offline_checks.py.
"""
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
FW = HERE.parent
TEX = FW / "Textures"
LOOKS = ("Futuristic", "Industrial", "Modern", "Scrapper")

# AltitudeLayer order (Verse.AltitudeLayer, relative order only matters here)
ALT = {name: i for i, name in enumerate((
    "Terrain", "TerrainScatter", "Floor", "FloorEmplacement", "Filth", "FloorCoverings", "Conduits", "LayingPawn",
    "Shadows", "SmallWire", "Item", "ItemImportant", "BuildingBelowTop", "Building", "BuildingOnTop", "Pawn",
    "PawnUnused", "Projectile", "Weather", "MetaOverlays"))}
UP, RIGHT, DOWN, LEFT = 1, 2, 4, 8
DIRS = {UP: (0, 1), RIGHT: (1, 0), DOWN: (0, -1), LEFT: (-1, 0)}

_cache = {}


def tex(rel):
    """A texture by its texPath (no extension), RGBA, cached."""
    if rel not in _cache:
        p = TEX / (rel + ".png")
        _cache[rel] = Image.open(p).convert("RGBA")
    return _cache[rel]


def atlas_tile(atlas, mask):
    """SubMaterialFromAtlas: the inner 3/16 of block (mask % 4, mask // 4) from the bottom-left."""
    t = atlas.width / 4
    x, y = mask % 4, mask // 4
    left, top = x * t + t / 8, (3 - y) * t + t / 8
    return atlas.crop((round(left), round(top), round(left + t * 0.75), round(top + t * 0.75)))


def pipe_atlas(look):
    return tex("RimMandrake/FlowWorks/Pipe/%s/UniversalPipe_Atlas" % look)


def soil(w, h, seed=7):
    """A neutral soil-like ground (not vanilla's texture: a stand-in so contrast reads like the game's soil)."""
    rng = np.random.default_rng(seed)
    base = np.array([108, 86, 62], float)
    n = rng.normal(0, 9, (h // 4 + 1, w // 4 + 1, 1))
    n = np.kron(n, np.ones((4, 4, 1)))[:h, :w]
    a = np.clip(base + n + rng.normal(0, 5, (h, w, 1)), 0, 255).astype(np.uint8)
    return Image.fromarray(np.dstack([a, np.full((h, w), 255, np.uint8)]), "RGBA")


class Scene:
    def __init__(self, w, h, px=96, ground=True):
        self.w, self.h, self.P = w, h, px
        self.draws = []   # (altitude, seq, fn(canvas), meta dict or None)
        self.ground = ground
        self.labels = []
        self.risers = []  # (cell, path) of every riser drawn: what fw_offline_checks reads for geometry

    # ---- coordinates -------------------------------------------------------------------------------------------------
    def to_px(self, x, z):
        return x * self.P, (self.h - z) * self.P

    def _add(self, alt, fn, dy=0.0, meta=None):
        a = (ALT[alt] if isinstance(alt, str) else alt) + dy
        self.draws.append((a, len(self.draws), fn, meta))

    # ---- primitive draws ---------------------------------------------------------------------------------------------
    def plane(self, img, cx, cz, sw, sh, alt="Building", dy=0.0, rot=0.0, flip_x=False, meta=None):
        """Printer_Plane / Graphics.DrawMesh(plane10): img stretched to sw x sh cells, centred on (cx, cz), turned rot degrees
        clockwise on screen (the game's angle)."""
        def fn(cv):
            P = self.P
            im = img.transpose(Image.FLIP_LEFT_RIGHT) if flip_x else img
            im = im.resize((max(1, round(sw * P)), max(1, round(sh * P))), Image.LANCZOS)
            if rot:
                im = im.rotate(-rot, resample=Image.BICUBIC, expand=True)
            x, y = self.to_px(cx, cz)
            cv.alpha_composite(im, (round(x - im.width / 2), round(y - im.height / 2)))
        self._add(alt, fn, dy, meta)

    def thing(self, texpath, x, z, size=(1, 1), draw_size=None, offset=(0, 0), alt="Building", rot=0.0, flip_x=False,
              meta=None):
        """Graphic_Single at a footprint min (x, z) of `size`, drawSize, drawOffset (x, z)."""
        ds = draw_size or size
        cx, cz = x + size[0] / 2 + offset[0], z + size[1] / 2 + offset[1]
        img = tex(texpath) if isinstance(texpath, str) else texpath
        self.plane(img, cx, cz, ds[0], ds[1], alt=alt, rot=rot, flip_x=flip_x, meta=meta)

    def strip(self, tile, path, half_w=0.12, alt="FloorEmplacement", dy=0.0, u0=0.0, meta=None, west=None):
        """The straight E-W tile's cross-section carried along a path: a list of ('L', x0, z0, x1, z1) and
        ('A', cx, cz, r, a0_deg, sweep_deg) segments (angles CCW from east, image-independent). u = distance along the path
        (+u0, wrapped to the tile), v = the tile's image-row fraction (0 = top = north rim): v = 0.5 - t, t = offset to
        the LEFT of travel, so the left of an eastward run samples the tile's north (top) rows. A path that ends west of its start swaps the rims (LiquidJoinRule.TravelsWest), so the tile's north
        rim stays on the north. Blending is straight alpha "over" on a premultiplied-free canvas, as the game's
        Transparent shader does for one layer; overlapping segment ends blend twice (a hair darker at the seam)."""
        west = travels_west(path) if west is None else west   # west= forces it (a check's can-fail run)
        if meta is not None:
            meta = dict(meta, west_drawn=bool(west))          # what was actually drawn, for riser_rims_north
        T = np.asarray(tile, dtype=np.float32)
        th, tw = T.shape[:2]

        def fn(cv):
            P = self.P
            out = np.asarray(cv, dtype=np.float32).copy()
            H, W = out.shape[:2]
            s_acc = u0
            for seg in path:
                if seg[0] == "L":
                    _, x0, z0, x1, z1 = seg
                    L = math.hypot(x1 - x0, z1 - z0)
                    ux, uz = (x1 - x0) / L, (z1 - z0) / L
                    pts = [(x0, z0), (x1, z1)]
                else:
                    _, ccx, ccz, r, a0, sw = seg
                    L = abs(math.radians(sw)) * r
                    pts = [(ccx + r * math.cos(math.radians(a0 + sw * k / 8)), ccz + r * math.sin(math.radians(a0 + sw * k / 8)))
                           for k in range(9)]
                xs = [p[0] for p in pts]
                zs = [p[1] for p in pts]
                bx0, by0 = self.to_px(min(xs) - half_w, max(zs) + half_w)
                bx1, by1 = self.to_px(max(xs) + half_w, min(zs) - half_w)
                ix0, iy0, ix1, iy1 = max(0, int(bx0) - 1), max(0, int(by0) - 1), min(W, int(bx1) + 2), min(H, int(by1) + 2)
                if ix1 <= ix0 or iy1 <= iy0:
                    s_acc += L
                    continue
                yy, xx = np.mgrid[iy0:iy1, ix0:ix1].astype(np.float32)
                gx = (xx + 0.5) / P
                gz = self.h - (yy + 0.5) / P
                if seg[0] == "L":
                    s = (gx - x0) * ux + (gz - z0) * uz
                    t = -(gx - x0) * uz + (gz - z0) * ux      # left of travel positive
                    ok = (s >= 0) & (s <= L) & (np.abs(t) <= half_w)
                else:
                    ang = np.degrees(np.arctan2(gz - ccz, gx - ccx))
                    da = (ang - a0) if sw > 0 else (a0 - ang)
                    da = np.mod(da, 360.0)
                    rad = np.hypot(gx - ccx, gz - ccz)
                    s = np.radians(da) * r
                    # CCW sweep: left of travel is toward the centre; CW: away from it
                    t = (r - rad) if sw > 0 else (rad - r)
                    ok = (da <= abs(sw)) & (np.abs(t) <= half_w)
                u = np.mod(s + s_acc, 1.0)
                v = (0.5 + t) if west else (0.5 - t)   # image row fraction: the tile's north rim is the top
                fx = np.clip(u * tw - 0.5, 0, tw - 1.001)
                fy = np.clip(v * th - 0.5, 0, th - 1.001)
                x0i, y0i = fx.astype(int), fy.astype(int)
                ax, ay = (fx - x0i)[..., None], (fy - y0i)[..., None]
                c = (T[y0i, x0i] * (1 - ax) * (1 - ay) + T[y0i, x0i + 1] * ax * (1 - ay)
                     + T[y0i + 1, x0i] * (1 - ax) * ay + T[y0i + 1, x0i + 1] * ax * ay)
                a = (c[..., 3:4] / 255.0) * ok[..., None]
                reg = out[iy0:iy1, ix0:ix1]
                reg[..., :3] = c[..., :3] * a + reg[..., :3] * (1 - a)
                reg[..., 3:4] = np.maximum(reg[..., 3:4], a * 255)
                s_acc += L
            cv.paste(Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA"))
        self._add(alt, fn, dy, meta)

    def label(self, x, z, text, color=(255, 255, 255)):
        self.labels.append((x, z, text, color))

    # ---- render ------------------------------------------------------------------------------------------------------
    def render(self, grid=False, only=None):
        """The picture. only(meta) -> bool keeps just those draws, on a transparent canvas with no labels (for checks)."""
        W, H = self.w * self.P, self.h * self.P
        if only is not None:
            cv = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            for _, _, fn, meta in sorted(self.draws, key=lambda d: (d[0], d[1])):
                if meta is not None and only(meta):
                    fn(cv)
            return cv
        cv = soil(W, H) if self.ground else Image.new("RGBA", (W, H), (0, 0, 0, 0))
        for _, _, fn, _ in sorted(self.draws, key=lambda d: (d[0], d[1])):
            fn(cv)
        d = ImageDraw.Draw(cv)
        if grid:
            for i in range(self.w + 1):
                d.line([(i * self.P, 0), (i * self.P, H)], fill=(0, 0, 0, 40))
            for j in range(self.h + 1):
                d.line([(0, j * self.P), (W, j * self.P)], fill=(0, 0, 0, 40))
        f = font(max(12, self.P // 6))
        for x, z, t, col in self.labels:
            px, py = self.to_px(x, z)
            d.text((px + 1, py + 1), t, fill=(0, 0, 0, 255), font=f)
            d.text((px, py), t, fill=col + (255,), font=f)
        return cv


def font(sz):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if Path(p).exists():
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()


# ---- the pipe network ------------------------------------------------------------------------------------------------
class PipeNet:
    """Pipes (cell -> look) and partners (tanks/machines: footprint rects) as RM_LiquidNet sees them for drawing."""

    def __init__(self):
        self.pipes = {}
        self.partners = []   # dict(def, look, x, z, w, h, tex, draw_size, kind)

    def add_pipe(self, cells, look):
        for c in cells:
            self.pipes[tuple(c)] = look

    def add_partner(self, **kw):
        self.partners.append(kw)

    def partner_at(self, x, z):
        for p in self.partners:
            if p["x"] <= x < p["x"] + p["w"] and p["z"] <= z < p["z"] + p["h"]:
                if p.get("on_pipe") and (x, z) in self.pipes:
                    continue   # LiquidJoinRule.JoinsAsPartner: a fixture on a pipe is part of the run
                return p
        return None


def seg_end(seg, f):
    """The point at fraction f of a path segment (LiquidJoinRule.SegmentAt, position only)."""
    if seg[0] == "L":
        _, x0, z0, x1, z1 = seg
        return x0 + (x1 - x0) * f, z0 + (z1 - z0) * f
    _, ccx, ccz, r, a0, sw = seg
    a = math.radians(a0 + sw * f)
    return ccx + r * math.cos(a), ccz + r * math.sin(a)


def travels_west(path):
    return bool(path) and seg_end(path[-1], 1)[0] < seg_end(path[0], 0)[0]


TANK_PORT_DZ = {"Scrapper": 0.021, "Industrial": 0.025, "Modern": -0.016, "Futuristic": -0.057}   # TankPortGeometry.PortDz


def riser_into(net, c, d, b):
    """RM_LiquidJoins.RiserInto: a 2x2 RM_LiquidTank on the pipe's west or east -> port z, else None."""
    if b is None or d[1] != 0 or d[0] == 0 or b["def"] != "RM_LiquidTank" or b["w"] != 2 or b["h"] != 2:
        return None
    if not (b["z"] <= c[1] <= b["z"] + 1):
        return None
    return b["z"] + 1.0 + TANK_PORT_DZ.get(b["look"], 0.021)


def link_mask(net, c, riser_aware=True):
    m = 0
    for bit, (dx, dz) in DIRS.items():
        n = (c[0] + dx, c[1] + dz)
        if n in net.pipes:
            m |= bit
            continue
        b = net.partner_at(*n)
        if b is not None:
            if riser_aware and riser_into(net, c, (dx, dz), b) is not None:
                continue
            m |= bit
    return m
