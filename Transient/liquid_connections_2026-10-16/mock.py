#!/usr/bin/env python3
"""mock.py -- composite mock frames of each liquid join, TODAY (top) vs PROPOSED (bottom), at 128 px per cell.

Today   : the shipped pump (1x1, drawSize 1), hose at visible 0.465 (plump), pipe atlas as the game links it (a pipe beside a
          tank/pump ends in its cap; a hose end on a pipe just lies on it), no fittings.
Proposed: the hefty pump candidate (footprint 2x1, drawSize 2x2), hose at 0.65 x = 0.30 (plump), the pipe's arm running on
          to the shared edge (pipeLinksIntoMachines), a flange at each pipe/building join, a flange pair where a pump touches
          a tank, a saddle where a hose couples onto a pipe.
Geometry from the code: hose mesh width = visible / PlumpBand (62/64); the end coupling Coupling_Bare drawn at ~2.43 x
visible (FittingSize at plump 1); pipe atlas tiles 1 cell, Basic-link index N1 E2 S4 W8, col i%4, row-from-top 3-i//4.
    python3 mock.py [look]     -> mock/<join>_<look>.png (768 x 768: 6 x 6 cells)
"""
import math
import os
import sys

from PIL import Image, ImageDraw

H = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(H, "../../src/RimMandrake/FlowWorks/Textures/")
FW = TEX + "RimMandrake/FlowWorks/"
PX = 128
GROUND = (122, 94, 64, 255)
HSUB = {"Scrapper": "", "Industrial": "Styles/Industrial/", "Modern": "Styles/Modern/", "Futuristic": "Styles/Futuristic/"}


def load(p):
    return Image.open(p).convert("RGBA")


def fit(im, w, h):
    return im.convert("RGBa").resize((max(1, round(w)), max(1, round(h))), Image.LANCZOS).convert("RGBA")


class Panel:
    def __init__(self, look, label):
        self.look = look
        self.im = Image.new("RGBA", (6 * PX, 3 * PX), GROUND)
        self.label = label
        self.atlas = load(FW + f"Pipe/{look}/UniversalPipe_Atlas.png")

    # cell (cx, cz): x right, z UP from the panel's bottom-left; pixel y = (3 - z) * PX
    def at(self, x, z):
        return x * PX, (3 - z) * PX

    def put(self, im, x, z, w, h, rot=0):
        """Centre im at world (x, z), drawn w x h cells, rotated rot degrees counter-clockwise."""
        s = fit(im, w * PX, h * PX)
        if rot:
            s = s.rotate(rot, expand=True, resample=Image.BICUBIC)
        px, py = self.at(x, z)
        self.im.alpha_composite(s, (round(px - s.width / 2), round(py - s.height / 2)))

    def pipe(self, cx, cz, links):
        i = sum(v for k, v in (("N", 1), ("E", 2), ("S", 4), ("W", 8)) if k in links)
        T = self.atlas.width // 4
        tile = self.atlas.crop(((i % 4) * T, (3 - i // 4) * T, (i % 4 + 1) * T, (4 - i // 4) * T))
        self.put(tile, cx + 0.5, cz + 0.5, 1, 1)

    def hose(self, x0, z0, x1, z1, vis):
        """A straight hose from (x0, z0) to (x1, z1), plump strand at visible width vis."""
        st = load(FW + "Hose/" + HSUB[self.look] + "Strand_Plump.png")
        mw = vis / (62 / 64)
        L = math.hypot(x1 - x0, z1 - z0)
        seg = fit(st, st.width * mw * PX / st.height, mw * PX)
        strip = Image.new("RGBA", (max(1, round(L * PX)), seg.height), (0, 0, 0, 0))
        x = 0
        while x < strip.width:
            strip.alpha_composite(seg, (x, 0))
            x += seg.width
        rot = math.degrees(math.atan2(z1 - z0, x1 - x0))
        s = strip.rotate(rot, expand=True, resample=Image.BICUBIC)
        px, py = self.at((x0 + x1) / 2, (z0 + z1) / 2)
        self.im.alpha_composite(s, (round(px - s.width / 2), round(py - s.height / 2)))

    def hose_to(self, x0, z0, fx, fz, vis):
        """A hose from (x0, z0) ending in its coupling whose face is at (fx, fz), pointing along the hose."""
        rot = math.degrees(math.atan2(fz - z0, fx - x0))
        back = 0.42 * 2.43 * vis
        ex, ez = fx - back * math.cos(math.radians(rot)), fz - back * math.sin(math.radians(rot))
        self.hose(x0, z0, ex, ez, vis)
        self.coupling(fx, fz, vis, rot)

    def coupling(self, x, z, vis, rot=0):
        """The hose's end coupling, its face at (x, z) pointing east (rot rotates)."""
        c = load(FW + "Hose/" + HSUB[self.look] + "Coupling_Bare.png")
        size = 2.43 * vis
        # Coupling_Bare's brass face is the canvas's right side (opaque x 58..124 of 128): centre sits 0.47 size back
        dx = -0.47 * size * math.cos(math.radians(rot))
        dz = -0.47 * size * math.sin(math.radians(rot))
        self.put(c, x + dx, z + dz, size, size, rot)

    def done(self):
        d = ImageDraw.Draw(self.im)
        d.rectangle((0, 0, 6 * PX - 1, 3 * PX - 1), outline=(60, 45, 30, 255), width=2)
        d.text((8, 6), self.label, fill=(255, 255, 255, 255))
        return self.im


def pump_today(p, x, z):          # 1x1 at cell (x, z)
    p.put(load(TEX + "Things/Building/FlowWorks/Machinery/RM_LiquidPump.png"), x + 0.5, z + 0.5, 1, 1)


def pump_new(p, x, z):            # footprint 2x1 at cells (x..x+1, z), drawSize 2x2 offset north 0.5
    p.put(load(os.path.join(H, "cand", f"{p.look}_pump.png")), x + 1, z + 1, 2, 2)


def tank(p, x, z):                # 2x2 at (x..x+1, z..z+1)
    p.put(load(FW + f"Tank/{p.look}/RM_LiquidTank.png"), x + 1, z + 1, 2, 2)


def reel(p, x, z):
    p.put(load(FW + "Hose/" + HSUB[p.look] + "Reel_Deployed.png"), x + 1, z + 1, 2.8, 2.8)


def flange(p, x, z, rot):          # face at (x, z), facing rot
    f = load(os.path.join(H, "cand", f"{p.look}_flange.png"))
    p.put(f, x - 0.25 * math.cos(math.radians(rot)), z - 0.25 * math.sin(math.radians(rot)), 0.5, 0.5, rot)


def saddle(p, cx, cz):
    p.put(load(os.path.join(H, "cand", f"{p.look}_saddle.png")), cx + 0.5, cz + 0.5, 1, 1)


VIS_NOW, VIS_NEW = 0.465, 0.465 * 0.65

JOINS = {}


def join(name):
    def deco(f):
        JOINS[name] = f
        return f
    return deco


@join("hose_to_pump")
def _(p, new):
    if new:
        pump_new(p, 3, 1)
        # the pump's left inlet flange: face at x 3 + 13/256, height = flange centre (canvas y ~355 of 512 -> z 1 + (512-355)/256)
        zf = 1 + (512 - 355) / 256
        p.hose_to(0, zf, 3.05, zf, VIS_NEW)
    else:
        pump_today(p, 3, 1)
        p.hose_to(0, 1.5, 3.0, 1.5, VIS_NOW)


@join("hose_to_tank")
def _(p, new):
    tank(p, 3, 0.5)
    v = VIS_NEW if new else VIS_NOW
    if new:
        flange(p, 3.0, 1.5, 180)      # the tank's own port flange on its west edge
    p.hose_to(0, 1.5, 3.0 - (0.06 if new else 0), 1.5, v)


@join("hose_to_reel")
def _(p, new):
    reel(p, 3, 0.5)
    v = VIS_NEW if new else VIS_NOW
    # the reel's laid inlet sits on its west side, art v 135/256 of 2.8 cells
    z = 0.5 + 1 + (128 - 135) / 256 * 2.8
    x = 3 + 1 - 1.4 + 9 / 256 * 2.8
    p.hose_to(0, z, x + 0.07, z, v)


@join("hose_to_pipe")
def _(p, new):
    for cx in range(2, 6):
        p.pipe(cx, 1, ("W" if cx > 2 else "") + ("E" if cx < 5 else ""))
    v = VIS_NEW if new else VIS_NOW
    if new:
        saddle(p, 3, 1)
        p.hose(0.3, 0.35, 3.5, 0.35, v)
        p.hose_to(3.5, 0.35, 3.5, 1.2, v)     # up into the saddle's spigot
    else:
        p.hose_to(0, 1.5, 3.9, 1.5, v)        # today: the end just lies on the pipe


@join("pipe_to_tank")
def _(p, new):
    tank(p, 3, 1)
    for cx in range(0, 3):
        links = ("W" if cx > 0 else "") + ("E" if (cx < 2 or new) else "")
        p.pipe(cx, 1, links)
    if new:
        flange(p, 3.0, 1.5, 0)


@join("pipe_to_pump")
def _(p, new):
    if new:
        pump_new(p, 3, 1)
    else:
        pump_today(p, 3, 1)
    for cx in range(0, 3):
        p.pipe(cx, 1, ("W" if cx > 0 else "") + ("E" if (cx < 2 or new) else ""))
    if new:
        flange(p, 3.0, 1.5, 0)


@join("pump_to_tank")
def _(p, new):
    if new:
        pump_new(p, 0.5, 1)
        tank(p, 2.5, 1)
        flange(p, 2.5, 1.5, 0)
        flange(p, 2.5, 1.5, 180)
    else:
        pump_today(p, 1.5, 1)
        tank(p, 2.5, 1)


@join("reel_to_tank")
def _(p, new):
    reel(p, 0.5, 0.5)
    tank(p, 2.5, 0.5)
    if new:
        flange(p, 2.5, 1.5, 0)
        flange(p, 2.5, 1.5, 180)


@join("pipe_to_pipe")
def _(p, new):
    for cx in range(0, 6):
        p.pipe(cx, 1, ("W" if cx > 0 else "") + ("E" if cx < 5 else ""))


def frame(name, look):
    f = Image.new("RGBA", (6 * PX, 6 * PX), GROUND)
    for k, new in enumerate((False, True)):
        p = Panel(look, f"{name.replace('_', ' ')} - {'PROPOSED' if new else 'today'} ({look})")
        JOINS[name](p, new)
        f.alpha_composite(p.done(), (0, k * 3 * PX))
    return f


if __name__ == "__main__":
    looks = sys.argv[1:] or ["Scrapper"]
    os.makedirs(os.path.join(H, "mock"), exist_ok=True)
    for look in looks:
        for name in JOINS:
            out = os.path.join(H, "mock", f"{name}_{look}.png")
            frame(name, look).save(out)
            print(out)
