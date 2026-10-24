"""Ladder art v4 (RAIL_LADDER_REDRAW_FAT_RUNG_FENCE, PORTABLE_LADDER_REDRAW_NORTH_TOO_FLAT; owner 2026-10-23:
"The ladder-on-rails on the northern wall of a pit is very fat and dense with rungs. Needs redraw to look more like a
real fire-escape-style ladder at proper perspective." / "Northern set portable ladder likewise needs steeper
perspective.").

Drawn procedurally rather than generated: the complaint is geometry (width, rung count, perspective), which a
parametric drawing gets exactly and an image model does not.

Rig (both ladders, unchanged defs): Graphic_Multi, 384 px canvas, drawSize 1.5 -> 256 px per cell, offsets N/E/W
(0,0,+0.25), S (0,0,-0.25). On the NORTH canvas the far rim is row 128; the wall face hangs below it
(RM_WallFaceMath.NorthByDrop: D3 0.35 cell -> foot row 218, D4 0.50 -> row 256). On the SOUTH canvas the near rim is
row 256. The camera looks down from the south, so on the north face "lower on screen" = deeper = farther: rails
converge slightly with depth and rung spacing shrinks downward.

  rail ladder (RM_Ladder / RM_LadderRaised): painted steel fire-escape ladder. North: two fixed guide rails bolted to
      the face with goosenecks over the rim; a narrow ladder of flat-bar stringers and thin round rungs slides in them.
      Raised = the ladder slid up RAISE_N px, empty rails below. East: the same ladder leaning on the side wall, in the
      v3 pose (west = east mirrored). South: only the gooseneck tops above the near rim (raised: the ladder top too).
  portable ladder north (RM_LadderPortable_north): the shipped redraw-8 art re-projected steeper (see P_DST): top
      just past the rim, foot on the floor just off the face. Other portable facings are unchanged.

    python3 draw.py   -> out/RM_Ladder_{north,east,west,south}.png, out/RM_LadderRaised_{...}.png,
                         out/RM_LadderPortable_north.png
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
SS = 4                      # supersample
C = 384                     # canvas
RAISE_N = 96                # north raised slide, px on the 384 canvas (0.375 cell)
RAISE_E = (26, -6)          # east raised slide along the ladder axis

# painted steel (fire-escape black, worn)
OUTL = (14, 14, 16, 255)
RAIL = (52, 54, 58, 255)
RAIL_HI = (118, 122, 128, 255)
STR = (66, 68, 73, 255)
STR_HI = (146, 150, 156, 255)
RUNG = (88, 88, 90, 255)
RUNG_HI = (190, 186, 178, 255)
BOLT = (150, 146, 138, 255)


def S(v):
    return v * SS


class Pen:
    def __init__(self):
        self.im = Image.new("RGBA", (S(C), S(C)), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)

    def quad(self, p0, p1, w0, w1, col, nudge=0.0):
        """A bar from p0 to p1, width w0 at p0 and w1 at p1 (384-space), shifted sideways by nudge*width."""
        (x0, y0), (x1, y1) = p0, p1
        dx, dy = x1 - x0, y1 - y0
        L = max((dx * dx + dy * dy) ** 0.5, 1e-6)
        nx, ny = -dy / L, dx / L
        pts = [(x0 + nx * (nudge - .5) * w0, y0 + ny * (nudge - .5) * w0),
               (x1 + nx * (nudge - .5) * w1, y1 + ny * (nudge - .5) * w1),
               (x1 + nx * (nudge + .5) * w1, y1 + ny * (nudge + .5) * w1),
               (x0 + nx * (nudge + .5) * w0, y0 + ny * (nudge + .5) * w0)]
        self.d.polygon([(S(x), S(y)) for x, y in pts], fill=col)

    def disc(self, p, r, col):
        x, y = p
        self.d.ellipse([S(x - r), S(y - r), S(x + r), S(y + r)], fill=col)

    def poly(self, pts, w, col):
        for a, b in zip(pts, pts[1:]):
            self.quad(a, b, w, w, col)
        for p in pts:
            self.disc(p, w / 2, col)


def bar(pen, p0, p1, w0, w1, fill, hi, outl, ol=1.4, hi_side=-1):
    """Outlined, lit bar: dark outline, body, a highlight strip on the lit (left/top) side."""
    pen.quad(p0, p1, w0 + 2 * ol, w1 + 2 * ol, outl)
    pen.quad(p0, p1, w0, w1, fill)
    pen.quad(p0, p1, w0 * .32, w1 * .32, hi, nudge=hi_side * .22 / .32)


def rung(pen, xl, xr, y, d, fill=RUNG, hi=RUNG_HI, outl=OUTL, ol=1.2):
    """A thin round rung seen from above-front: outline, body, a bright worn top line."""
    pen.quad((xl, y), (xr, y), d + 2 * ol, d + 2 * ol, outl)
    pen.quad((xl, y), (xr, y), d, d, fill)
    pen.quad((xl, y - d * .22), (xr, y - d * .22), d * .34, d * .34, hi)


def gooseneck(pen, x, ytop, side, w, fill, hi, outl, rise=12, reach=11):
    """Fire-escape gooseneck: the bar rises above (x, ytop) and curls outward (side=-1 left, +1 right) and down."""
    import math
    r = reach / 2
    cx, cy = x + side * r, ytop - rise
    pts = [(x, ytop)] + [(cx - side * r * math.cos(math.pi * i / 12), cy - r * math.sin(math.pi * i / 12))
                         for i in range(13)]
    pts.append((pts[-1][0], pts[-1][1] + 7))
    pen.poly(pts, w + 2.8, outl)
    pen.poly(pts, w, fill)
    hp = [(px - side * w * .2, py - w * .15) for px, py in pts[1:8]]
    pen.poly(hp, w * .3, hi)


def lerp(a, b, t):
    return a + (b - a) * t


def rung_rows(y0, y1, n, ratio):
    """n rows from y0 to y1, each gap `ratio` times the one above (ratio < 1: closer together lower down)."""
    gaps = [ratio ** i for i in range(n - 1)]
    k = (y1 - y0) / sum(gaps)
    ys, y = [y0], y0
    for g in gaps:
        y += g * k
        ys.append(y)
    return ys


def shadowed(layer, dx=3, dy=4, alpha=95, blur=1.6):
    """Layer over its own soft contact shadow (offset down-right, onto the face behind it)."""
    a = layer.getchannel("A").point(lambda v: v * alpha // 255)
    sh = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    sh.putalpha(a)
    sh = sh.filter(ImageFilter.GaussianBlur(S(blur)))
    out = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    out.alpha_composite(sh, (S(dx), S(dy)))
    out.alpha_composite(layer)
    return out


def finish(im):
    """Premultiplied BOX downscale to 384, alpha < 32 cleared (no faint fringe)."""
    import numpy as np
    a = np.asarray(im, dtype=np.float64) / 255.0
    a[..., :3] *= a[..., 3:4]
    small = np.asarray(Image.fromarray((a * 255).round().astype(np.uint8)).resize((C, C), Image.BOX), dtype=np.float64)
    al = small[..., 3:4]
    rgb = np.where(al > 0, small[..., :3] * 255.0 / np.maximum(al, 1), 0)
    out = np.concatenate([np.clip(rgb, 0, 255), al], axis=-1)
    out[out[..., 3] < 32] = 0
    return Image.fromarray(out.round().astype(np.uint8), "RGBA")


# ---------------------------------------------------------------- rail ladder, north
CX = 192
RIM = 128
FOOT = 252                     # between the D3 (218) and D4 (256) face foot
RAIL_HALF = (63, 50)           # guide rail centre offset at rim / at foot
LAD_HALF = (50, 38)            # ladder stringer centre offset at rim / at foot


def x_at(half, y, y0=RIM, y1=FOOT):
    t = (y - y0) / (y1 - y0)
    return lerp(half[0], half[1], t)


def north_rails():
    pen = Pen()
    top, bot = RIM - 6, FOOT + 2
    for side in (-1, 1):
        xt, xb = CX + side * x_at(RAIL_HALF, top), CX + side * x_at(RAIL_HALF, bot)
        bar(pen, (xt, top), (xb, bot), 6.6, 5.8, RAIL, RAIL_HI, OUTL)
        for yb in (RIM + 12, (RIM + FOOT) / 2 + 4, FOOT - 8):     # wall brackets
            xr = CX + side * x_at(RAIL_HALF, yb)
            bar(pen, (xr - 6.5, yb), (xr + 6.5, yb), 4.2, 4.2, RAIL, RAIL_HI, OUTL, hi_side=1)
            pen.disc((xr + side * 4.5, yb), 1.1, BOLT)
        gooseneck(pen, xt, top, side, 5.4, RAIL, RAIL_HI, OUTL, rise=10, reach=12)
    return pen.im


def north_ladder(dy=0):
    """The sliding ladder; dy < 0 lifts it (raised state). Width/spacing keep the lowered perspective."""
    pen = Pen()
    top, bot = RIM - 8, FOOT - 2
    ys = rung_rows(RIM + 7, FOOT - 10, 7, 0.88)
    for y in ys:
        xl, xr = CX - x_at(LAD_HALF, y), CX + x_at(LAD_HALF, y)
        rung(pen, xl, xr, y + dy, 3.8)
    for side in (-1, 1):
        xt, xb = CX + side * x_at(LAD_HALF, top), CX + side * x_at(LAD_HALF, bot)
        bar(pen, (xt, top + dy), (xb, bot + dy), 5.4, 4.8, STR, STR_HI, OUTL)
        pen.disc((xb, bot + dy + 1), 3.0, OUTL)                   # foot shoe
        pen.disc((xb, bot + dy + 1), 1.9, STR)
        # stringer top: a short rounded grab end
        pen.disc((xt, top + dy), 3.6, OUTL)
        pen.disc((xt, top + dy), 2.3, STR_HI)
    return pen.im


def rail_north(raised):
    im = shadowed(north_rails())
    im.alpha_composite(shadowed(north_ladder(-RAISE_N if raised else 0)))
    return finish(im)


# ---------------------------------------------------------------- rail ladder, east (v3 pose)
E_FOOT = ((126, 240), (126, 314))     # upper/lower stringer at the floor end (left)
E_TOP = ((318, 193), (328, 287))      # upper/lower stringer at the rim end (right)


def rail_east(raised):
    pen = Pen()
    ox, oy = RAISE_E if raised else (0, 0)
    (fu, fl), (tu, tl) = E_FOOT, E_TOP
    P = lambda p: (p[0] + ox, p[1] + oy)
    n = 6
    ts = rung_rows(0.0, 1.0, n, 1.12)                 # gaps grow toward the rim end (nearer the camera)
    for t in [lerp(0.05, 0.93, v) for v in ts]:
        a = (lerp(fu[0], tu[0], t), lerp(fu[1], tu[1], t))
        b = (lerp(fl[0], tl[0], t), lerp(fl[1], tl[1], t))
        pen.quad(P(a), P(b), lerp(5.4, 6.2, t), lerp(5.4, 6.2, t), OUTL)
        pen.quad(P(a), P(b), lerp(3.0, 3.8, t), lerp(3.0, 3.8, t), RUNG)
        pen.quad(P(a), P(b), 1.2, 1.2, RUNG_HI, nudge=-0.25)
    for f, t_ in ((fu, tu), (fl, tl)):
        bar(pen, P(f), P(t_), 4.0, 4.8, STR, STR_HI, OUTL)
        pen.disc(P(f), 2.6, OUTL)
        pen.disc(P(f), 1.4, STR)
    for t_ in (tu, tl):                                # goosenecks over the east rim
        x, y = P(t_)
        pts = [(x, y), (x + 6, y - 3), (x + 11, y - 2), (x + 14, y + 2), (x + 14, y + 8)]
        pen.poly(pts, 7.4, OUTL)
        pen.poly(pts, 4.6, STR)
        pen.poly(pts[:3], 1.4, STR_HI)
    return finish(shadowed(pen.im, dx=2, dy=4))


# ---------------------------------------------------------------- rail ladder, south (near rim at row 256)
S_RIM = 256
S_HALF = 62


def rail_south(raised):
    pen = Pen()
    if raised:
        top = S_RIM - 112
        ys = rung_rows(S_RIM - 6, top + 10, 6, 1.06)
        for y in ys:
            k = (S_RIM - y) / (S_RIM - top)
            h = lerp(LAD_HALF[0], LAD_HALF[0] + 4, k)
            rung(pen, CX - h, CX + h, y, 3.6)
        for side in (-1, 1):
            bar(pen, (CX + side * LAD_HALF[0], S_RIM + 1), (CX + side * (LAD_HALF[0] + 4), top), 4.6, 5.0,
                STR, STR_HI, OUTL)
            pen.disc((CX + side * (LAD_HALF[0] + 4), top), 3.8, OUTL)
            pen.disc((CX + side * (LAD_HALF[0] + 4), top), 2.4, STR_HI)
    for side in (-1, 1):
        gooseneck(pen, CX + side * S_HALF, S_RIM + 1, side, 5.4, RAIL, RAIL_HI, OUTL, rise=11, reach=12)
    return finish(shadowed(pen.im, dx=2, dy=3))


# ---------------------------------------------------------------- portable ladder, north (wood, steep lean)
# Owner asked for perspective only, so the art itself is kept: the shipped "redraw 8" north (src_portable_north_redraw8.png,
# owner by card 2026-10-22) is re-projected by a true homography from its measured rail quad onto a steeper trapezoid.
# A homography onto a trapezoid narrowing downward also closes the rung gaps toward the foot, so rails converge and
# rungs crowd with depth from one transform, and the style matches the unchanged E/W/S facings exactly.
P_SRC = ((134, 24), (219, 24), (225, 276), (118, 276))      # the redraw-8 ladder's rails, TL TR BR BL (measured, alpha>200)
P_DST = ((134, 70), (250, 70), (233, 284), (151, 284))      # top just past the rim, foot on the floor off a D4 face


def homography(src, dst):
    """Coefficients for Image.transform(PERSPECTIVE): maps OUTPUT (dst) points back to INPUT (src) points."""
    import numpy as np
    A, B = [], []
    for (x, y), (u, v) in zip(dst, src):
        A += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]
        B += [u, v]
    return list(np.linalg.solve(np.array(A, float), np.array(B, float)))


def portable_north():
    import numpy as np
    src = Image.open(HERE / "src_portable_north_redraw8.png").convert("RGBA")
    sq = [(S(x), S(y)) for x, y in P_SRC]
    dq = [(S(x), S(y)) for x, y in P_DST]
    a = np.asarray(src, dtype=np.float64)
    a[..., :3] *= a[..., 3:4] / 255.0                       # premultiply BEFORE any resampling: no dark halo
    pm = Image.fromarray(a.round().astype(np.uint8), "RGBA").resize((S(C), S(C)), Image.BICUBIC)
    w = pm.transform(pm.size, Image.PERSPECTIVE, homography(sq, dq), Image.BICUBIC)
    b = np.asarray(w, dtype=np.float64)
    al = b[..., 3:4]
    b[..., :3] = np.where(al > 0, b[..., :3] * 255.0 / np.maximum(al, 1), 0)
    return finish(Image.fromarray(np.clip(b, 0, 255).round().astype(np.uint8), "RGBA"))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    outs = {
        "RM_Ladder_north": rail_north(False), "RM_LadderRaised_north": rail_north(True),
        "RM_Ladder_east": rail_east(False), "RM_LadderRaised_east": rail_east(True),
        "RM_Ladder_south": rail_south(False), "RM_LadderRaised_south": rail_south(True),
        "RM_LadderPortable_north": portable_north(),
    }
    outs["RM_Ladder_west"] = outs["RM_Ladder_east"].transpose(Image.FLIP_LEFT_RIGHT)
    outs["RM_LadderRaised_west"] = outs["RM_LadderRaised_east"].transpose(Image.FLIP_LEFT_RIGHT)
    for k, im in outs.items():
        bb = im.getchannel("A").getbbox()
        assert bb and bb[0] > 0 and bb[1] > 0 and bb[2] < C and bb[3] < C, (k, bb)
        im.save(OUT / f"{k}.png")
        print(k, bb)


if __name__ == "__main__":
    main()
