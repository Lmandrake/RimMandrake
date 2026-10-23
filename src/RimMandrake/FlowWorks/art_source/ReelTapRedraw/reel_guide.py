#!/usr/bin/env python3
"""REEL_TAP_CAMERA_REDRAW_STILL_SIDE_ON: grey camera blockouts for the hose reel (and the bleed well) at the measured
building camera (orthographic, ~35 deg; design/RimMandrake/building_camera_perspective_2026-10-14.md, art judge brief C3)
with every pipe in its true perspective plane (C6: a bore shows only on a pipe that really points at the camera).

World axes in cells: x east, z north, h up; origin the footprint centre on the ground. Projection: screen_x = x,
screen_up = 0.57 z + 0.82 h (sin/cos 35). Painter's order by depth toward the camera (-0.82 z + 0.57 h).
The reel is modelled once, outlet WEST; the north/south pictures are the same reel turned (outlet north / south).
The outlet is a gooseneck from the axle swivel down to a ground-level coupling, so the coupling is the outermost thing
on the outlet side in every frame (reel_intake_geometry.py measures the outlet tip as that extreme).

usage: reel_guide.py reel <frame west|north|south> <state stored|laid> <build frame|pedestal> <out.png> [--json]
       reel_guide.py tap <out.png>
Canvas 1024 = drawSize (2.15 reel, 1 tap) cells; the drawing is shifted vertically so its bbox is centred."""
import json
import math
import sys
from PIL import Image, ImageDraw

S, C = math.sin(math.radians(35)), math.cos(math.radians(35))
N = 1024


def proj(p):
    x, z, h = p
    return x, S * z + C * h


def depth(p):
    x, z, h = p
    return -C * z + S * h


def hull(pts):
    pts = sorted(set((round(a, 5), round(b, 5)) for a, b in pts))
    if len(pts) < 3:
        return pts
    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0:
            up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]


AX = {"x": (1, 0, 0), "z": (0, 1, 0), "h": (0, 0, 1)}


def basis(a):
    if a == (1, 0, 0) or a == (-1, 0, 0):
        return (0, 1, 0), (0, 0, 1)
    if a[2] == 0:
        return (1, 0, 0), (0, 0, 1)
    return (1, 0, 0), (0, 1, 0)


def circle(c, a, r, n=48):
    u, v = basis(a)
    return [tuple(c[i] + r * (math.cos(t) * u[i] + math.sin(t) * v[i]) for i in range(3))
            for t in (2 * math.pi * k / n for k in range(n))]


class Scene:
    def __init__(self):
        self.prims = []   # (depth, kind, data)

    def box(self, x0, x1, z0, z1, h0, h1, tone=150, bias=0.0):
        cs = [(x, z, h) for x in (x0, x1) for z in (z0, z1) for h in (h0, h1)]
        top = [(x0, z0, h1), (x1, z0, h1), (x1, z1, h1), (x0, z1, h1)]
        front = [(x0, z0, h0), (x1, z0, h0), (x1, z0, h1), (x0, z0, h1)]
        d = depth(((x0 + x1) / 2, (z0 + z1) / 2, (h0 + h1) / 2)) + bias
        self.prims.append((d, "box", (cs, top, front, tone)))

    def cyl(self, p0, p1, r, tone=140, rings=0, bias=0.0, cap="auto"):
        a = tuple(p1[i] - p0[i] for i in range(3))
        L = math.sqrt(sum(t * t for t in a))
        an = tuple(t / L for t in a)
        e0, e1 = circle(p0, an, r), circle(p1, an, r)
        cam = (0, -C, S)
        caps = []
        for pc, ring, sgn in ((p0, e0, -1), (p1, e1, 1)):
            if sum(sgn * an[i] * cam[i] for i in range(3)) > 0.02:
                caps.append(ring)
        rl = []
        for k in range(1, rings + 1):
            t = k / (rings + 1)
            c = tuple(p0[i] + a[i] * t for i in range(3))
            rl.append((c, circle(c, an, r)))
        d = depth(tuple((p0[i] + p1[i]) / 2 for i in range(3))) + bias
        self.prims.append((d, "cyl", (e0 + e1, caps if cap == "auto" else [], rl, tone, an)))

    def render(self, out, centre=True, pad=0.0):
        allp = []
        for _, kind, data in self.prims:
            allp += [proj(p) for p in data[0]]
        ys = [p[1] for p in allp]
        oy = -(max(ys) + min(ys)) / 2 if centre else 0.0
        im = Image.new("RGB", (N, N), (255, 255, 255))
        dr = ImageDraw.Draw(im)
        def px(p):
            x, y = proj(p)
            return (N / 2 + x * self.ppc, N / 2 - (y + oy) * self.ppc)
        for _, kind, data in sorted(self.prims, key=lambda t: t[0]):
            if kind == "box":
                cs, top, front, tone = data
                dr.polygon(hull([px(p) for p in cs]), fill=(tone,) * 3, outline=(40, 40, 40))
                dr.polygon([px(p) for p in front], fill=(int(tone * 0.7),) * 3, outline=(40, 40, 40))
                dr.polygon([px(p) for p in top], fill=(min(250, tone + 50),) * 3, outline=(40, 40, 40))
            else:
                pts, caps, rings, tone, an = data
                dr.polygon(hull([px(p) for p in pts]), fill=(tone,) * 3, outline=(40, 40, 40))
                cam = (0, -C, S)
                for c, ring in rings:
                    vis = [px(p) for p in ring if depth(p) >= depth(c) - 1e-6]
                    seg = []
                    for p in ring + ring[:1]:
                        if depth(p) >= depth(c) - 1e-6:
                            seg.append(px(p))
                        elif seg:
                            if len(seg) > 1:
                                dr.line(seg, fill=(70, 70, 70), width=3)
                            seg = []
                    if len(seg) > 1:
                        dr.line(seg, fill=(70, 70, 70), width=3)
                for ring in caps:
                    dr.polygon([px(p) for p in ring], fill=(min(250, tone + 45),) * 3, outline=(40, 40, 40))
        im.save(out)
        return oy


def turn(p, frame):
    """Rotate the west-outlet model about the footprint centre so the outlet points `frame`."""
    x, z, h = p
    if frame == "west":
        return (x, z, h)
    if frame == "north":
        return (z, -x, h)      # west (-x) -> north (+z); the crank (east) -> south
    return (-z, x, h)          # south: west -> south (-z)


def reel(frame, state, build):
    sc = Scene()
    sc.ppc = N / 2.15
    T = lambda p: turn(p, frame)
    def box(x0, x1, z0, z1, h0, h1, **k):
        cs = [T((x, z, 0)) for x in (x0, x1) for z in (z0, z1)]
        xs, zs = [c[0] for c in cs], [c[1] for c in cs]
        sc.box(min(xs), max(xs), min(zs), max(zs), h0, h1, **k)
    def cyl(p0, p1, r, **k):
        sc.cyl(T(p0), T(p1), r, **k)
    H = 0.52 if build == "frame" else 0.95   # axle height (the pedestal lifts the drum so its single post shows)
    R = 0.42           # flange radius
    if build == "frame":
        box(-0.62, 0.62, -0.40, 0.40, 0.0, 0.08, tone=120)                       # skid
        for sx in (-0.50, 0.50):
            box(sx - 0.035, sx + 0.035, -0.30, 0.30, 0.08, 0.16, tone=110)       # frame foot rail
            box(sx - 0.035, sx + 0.035, -0.05, 0.05, 0.08, H + 0.04, tone=115)   # upright to the axle
        cyl((-0.56, 0, H), (0.56, 0, H), 0.05, tone=90)                          # axle
    else:
        # judge 2026-10-23: the owner's 2026-10-15 Modern pick is a single-post pedestal - keep it in every facing
        box(-0.30, 0.30, -0.30, 0.30, 0.0, 0.05, tone=120)                       # square foot plate
        cyl((0, 0, 0.05), (0, 0, H - R - 0.06), 0.075, tone=140)                 # the single round post
        box(-0.50, 0.50, -0.06, 0.06, H - R - 0.10, H - R - 0.04, tone=112)      # yoke crossbar on the post
        for sx in (-0.47, 0.47):
            box(sx - 0.035, sx + 0.035, -0.06, 0.06, H - R - 0.10, H + 0.04, tone=115)
        cyl((-0.53, 0, H), (0.53, 0, H), 0.05, tone=90)
    for fx in (-0.40, 0.40):                                                     # flanges
        cyl((fx - 0.025, 0, H), (fx + 0.025, 0, H), R, tone=150)
    if state == "stored":
        cyl((-0.375, 0, H), (0.375, 0, H), 0.355, tone=175, rings=9)             # hose wound full
    else:
        cyl((-0.375, 0, H), (0.375, 0, H), 0.13, tone=110)                       # bare drum core
        cyl((-0.20, 0, H), (0.20, 0, H), 0.19, tone=95, rings=3)                 # a few turns left on it
    # outlet gooseneck: swivel at the west hub, down to the ground, then west to the coupling
    cyl((-0.44, 0, H), (-0.58, 0, H), 0.055, tone=130)
    cyl((-0.58, 0, H + 0.02), (-0.58, 0, 0.10), 0.055, tone=130)
    cyl((-0.58, 0, 0.10), (-0.80, 0, 0.10), 0.055, tone=130)
    cyl((-0.80, 0, 0.10), (-0.95, 0, 0.10), 0.075, tone=165)                     # ground-level coupling (nozzle)
    # east: crank (frame build) or the valve wheel (pedestal build), both on the hub
    if build == "frame":
        cyl((0.44, 0, H), (0.60, 0, H), 0.04, tone=120)
        box(0.58, 0.63, -0.04, 0.04, H - 0.02, H + 0.26, tone=125)              # crank arm
        cyl((0.60, 0, H + 0.24), (0.76, 0, H + 0.24), 0.03, tone=130)            # handle
    else:
        cyl((0.44, 0, H), (0.62, 0, H), 0.045, tone=140)
        cyl((0.62, 0, H - 0.05), (0.62, 0, H + 0.08), 0.06, tone=150)            # valve body
        cyl((0.62, 0, H + 0.08), (0.62, 0, H + 0.20), 0.025, tone=140)           # valve stem up
        cyl((0.62, 0, H + 0.20), (0.62, 0, H + 0.23), 0.13, tone=165)            # spoked handwheel, lying flat
    return sc


def tap():
    sc = Scene()
    sc.ppc = N / 1.0
    sc.cyl((0, 0, -0.02), (0, 0, 0.03), 0.17, tone=120)                          # ground collar
    sc.cyl((0, 0, 0.0), (0, 0, 0.62), 0.085, tone=150)                           # the driven pipe
    sc.cyl((0, 0, 0.30), (0, 0, 0.36), 0.115, tone=160)                          # flange band
    sc.cyl((0, 0, 0.50), (0, 0, 0.62), 0.11, tone=165)                           # valve body
    sc.cyl((0, 0, 0.62), (0, 0, 0.72), 0.025, tone=120)                          # stem
    sc.cyl((0, 0, 0.72), (0, 0, 0.75), 0.21, tone=150)                           # handwheel lying flat
    sc.cyl((0.08, 0, 0.55), (0.30, 0, 0.55), 0.055, tone=150)                    # side outlet, east
    sc.cyl((0.30, 0, 0.58), (0.30, 0, 0.40), 0.06, tone=155)                     # spout turned down (bore hidden)
    return sc


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "reel":
        oy = reel(a[1], a[2], a[3]).render(a[4])
    else:
        oy = tap().render(a[1])
    print(a[-1] if a[-1] != "--json" else a[-2], "offset_up_cells=%.3f" % oy)
