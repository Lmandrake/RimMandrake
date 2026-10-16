"""Grey camera blockouts for the RM_PitRamp redraw (owner by card 2026-10-15: "Redraw as a visible slope").

v1 (../guide.py) read as a flat boarded crate: a full-cell rectangle with a timber frame on all sides. v2 carries
the slope in SHAPE as well as light, so it survives 64 px:
  * trapezoid plan: the toe (pit end) is a wide, ragged earth spill that melts into the pit floor; the head (rim end)
    is narrower and ends in one crisp, bright timber header beam -- no frame around the other three sides;
  * luminance runs dark at the toe to light at the head;
  * cleats across the run; uphill-north shows each cleat's lit riser (stairs climbing away), uphill-south a dark drop;
  * east/west is a true wedge: the raised (high) end lifts on screen, so the top surface is a sheared band and the
    near (south) side face is a triangle of earth growing from nothing at the toe to ~0.3 cell at the head.
Building camera: design/RimMandrake/building_camera_perspective_2026-10-14.md.

    python3 guide_v2.py OUTDIR   -> guide_{north,south,east,west}.png (1024 px, RGBA)
"""
import random
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

N = 1024
M = 28


def lerp(a, b, t):
    return int(round(a + (b - a) * t))


def ragged_toe_mask(poly, toe_axis, toe_at, inward, seed=3):
    """Polygon mask whose toe edge is torn into an irregular spill, feathered."""
    m = Image.new("L", (N, N), 0)
    ImageDraw.Draw(m).polygon(poly, fill=255)
    r = random.Random(seed)
    d = ImageDraw.Draw(m)
    # bite and blob the toe so it reads as dumped earth, not a sawn edge
    for k in range(26):
        u = r.randint(M, N - M)
        depth = r.randint(10, 60)
        rad = r.randint(18, 46)
        c = toe_at - inward * rad + inward * depth
        xy = (u, c) if toe_axis == "y" else (c, u)
        d.ellipse([xy[0] - rad, xy[1] - rad, xy[0] + rad, xy[1] + rad], fill=0)   # bites only
    return m.filter(ImageFilter.GaussianBlur(6))


def north_south(uphill_north: bool) -> Image.Image:
    im = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    head_y, toe_y = (M, N - M) if uphill_north else (N - M, M)
    hw, tw = 0.36 * N, 0.48 * N          # half widths at head / toe
    cx = N / 2

    def half(y):
        t = abs(y - toe_y) / abs(head_y - toe_y)     # 0 toe .. 1 head
        return tw + (hw - tw) * t, t

    for y in range(N):
        h, t = half(y)
        if not (min(head_y, toe_y) <= y <= max(head_y, toe_y)):
            continue
        g = lerp(70, 190, t)
        d.line([(cx - h, y), (cx + h, y)], fill=(g, g, g, 255))
        # edge boards along the two long sides, slightly brighter
        e = lerp(95, 215, t)
        d.line([(cx - h, y), (cx - h + 44, y)], fill=(e, e, e, 255))
        d.line([(cx + h - 44, y), (cx + h, y)], fill=(e, e, e, 255))
    span = abs(head_y - toe_y)
    for i in range(1, 6):
        t = i / 6.4
        y = int(toe_y + (head_y - toe_y) * t)
        h, _ = half(y)
        top = lerp(120, 225, t)
        d.rectangle([cx - h + 44, y - 14, cx + h - 44, y + 14], fill=(top, top, top, 255))
        if uphill_north:     # riser faces the camera, lit, below the tread
            r = lerp(105, 175, t)
            d.rectangle([cx - h + 44, y + 14, cx + h - 44, y + 44], fill=(r, r, r, 255))
        else:                # drop on the far (north) side, dark
            d.rectangle([cx - h + 44, y - 40, cx + h - 44, y - 14], fill=(40, 40, 40, 255))
    # crisp header beam at the head
    hy0, hy1 = (head_y, head_y + 70) if uphill_north else (head_y - 70, head_y)
    d.rectangle([cx - hw - 8, hy0, cx + hw + 8, hy1], fill=(240, 240, 240, 255))
    d.rectangle([cx - hw - 8, hy1 - 16, cx + hw + 8, hy1] if uphill_north else [cx - hw - 8, hy0, cx + hw + 8, hy0 + 16],
                fill=(170, 170, 170, 255))
    poly = [(cx - tw, toe_y), (cx + tw, toe_y), (cx + hw + 8, head_y), (cx - hw - 8, head_y)]
    inward = -1 if uphill_north else 1
    mask = ragged_toe_mask(poly, "y", toe_y, inward)
    # keep the header crisp: no feathering at the head
    ImageDraw.Draw(mask).rectangle([cx - hw - 8, min(hy0, hy1), cx + hw + 8, max(hy0, hy1)], fill=255)
    im.putalpha(mask)
    return im


def east() -> Image.Image:
    im = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x0, x1 = M, N - M
    lift = int(0.30 * N)
    yt0, yb0 = M + lift - 40, N - M         # top surface north / south edge at the toe (west)
    yt1, yb1 = M, N - M - lift              # ... at the head (east), lifted

    def edges(x):
        t = (x - x0) / (x1 - x0)
        return lerp(yt0, yt1, t), lerp(yb0, yb1, t), t

    for x in range(x0, x1):
        yt, yb, t = edges(x)
        g = lerp(70, 190, t)
        d.line([(x, yt), (x, yb)], fill=(g, g, g, 255))
        e = lerp(95, 215, t)
        d.line([(x, yt), (x, yt + 40)], fill=(e, e, e, 255))           # far edge board
        d.line([(x, yb - 40), (x, yb)], fill=(e, e, e, 255))           # near edge board
        f = lerp(85, 135, t)
        d.line([(x, yb), (x, N - M)], fill=(f, f, f, 255))             # near side face: the earth triangle
    for i in range(1, 6):
        t = i / 6.4
        x = int(x0 + (x1 - x0) * t)
        yt, yb, _ = edges(x)
        top = lerp(120, 225, t)
        d.rectangle([x - 12, yt + 40, x + 12, yb - 40], fill=(top, top, top, 255))
        d.rectangle([x - 34, yt + 40, x - 12, yb - 40], fill=(lerp(95, 160, t),) * 3 + (255,))  # riser facing the toe
    for k in (0.4, 0.75):                                              # strata on the side face
        pts = []
        for x in range(x0 + 60, x1 - 8, 8):
            yt, yb, _ = edges(x)
            pts.append((x, yb + int((N - M - yb) * k)))
        d.line(pts, fill=(60, 60, 60, 255), width=5)
    # header beam: a vertical post-and-beam at the head end, crisp
    d.rectangle([x1 - 64, yt1, x1, N - M], fill=(235, 235, 235, 255))
    d.rectangle([x1 - 64, yb1, x1, N - M], fill=(175, 175, 175, 255))
    poly = [(x0, yt0), (x1, yt1), (x1, N - M), (x0, N - M)]
    mask = ragged_toe_mask(poly, "x", x0, 1)
    ImageDraw.Draw(mask).rectangle([x1 - 64, yt1, x1, N - M], fill=255)
    im.putalpha(mask)
    return im


def main(out: Path):
    out.mkdir(parents=True, exist_ok=True)
    north_south(True).save(out / "guide_north.png")
    north_south(False).save(out / "guide_south.png")
    e = east()
    e.save(out / "guide_east.png")
    e.transpose(Image.FLIP_LEFT_RIGHT).save(out / "guide_west.png")


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else "."))
