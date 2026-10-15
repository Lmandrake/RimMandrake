"""Grey camera blockouts for RM_PitRamp, one per facing (rotation = uphill).

Image 1 of each codex edit (editing-images: a camera is held by a picture). Building camera:
design/RimMandrake/building_camera_perspective_2026-10-14.md -- ground grid unforeshortened, light
overhead-front, top faces brightest, a vertical face shown as a band <= ~1/3 cell, no painted shadow.

The ramp fills its 1x1 cell: two timber side stringers along the uphill direction, a packed-earth
running surface between them, timber cleats across it. Higher = brighter. North (uphill away from the
camera): each cleat shows its lit riser below it, a stair climbing away. South (uphill toward the
camera): risers face away, each cleat shows a dark drop line on its far side. East/West: the south
side of the wedge is a visible face that grows from nothing at the low end to ~0.3 cell at the high end.

    python3 guide.py OUTDIR      -> guide_north.png guide_east.png guide_south.png guide_west.png (1024 px)
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

N = 1024
M = 24                       # margin inside the cell
RAIL = 80                   # stringer width
CLEATS = 5


def lerp(a, b, t):
    return int(round(a + (b - a) * t))


def north_or_south(uphill_north: bool) -> Image.Image:
    im = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x0, x1, y0, y1 = M, N - M, M, N - M
    # running surface: brighter toward the high end
    for y in range(y0, y1):
        t = (y - y0) / (y1 - y0)                 # 0 at north edge, 1 at south edge
        hi = 1 - t if uphill_north else t        # 1 at the high end
        g = lerp(95, 185, hi)
        d.line([(x0 + RAIL, y), (x1 - RAIL, y)], fill=(g, g, g, 255))
    # cleats
    span = (y1 - y0) / CLEATS
    for i in range(CLEATS):
        cy = int(y0 + span * (i + 0.5))
        t = (cy - y0) / (y1 - y0)
        hi = 1 - t if uphill_north else t
        top = lerp(130, 215, hi)
        d.rectangle([x0 + RAIL, cy - 12, x1 - RAIL, cy + 6], fill=(top, top, top, 255))
        if uphill_north:     # lit riser below the tread: stairs climbing away
            r = lerp(150, 200, hi)
            d.rectangle([x0 + RAIL, cy + 6, x1 - RAIL, cy + 66], fill=(r, r, r, 255))
        else:                # drop on the far (north) side: stairs descending away
            d.rectangle([x0 + RAIL, cy - 40, x1 - RAIL, cy - 12], fill=(55, 55, 55, 255))
    # stringers: top face + a thin inner face
    for (a, b) in ((x0, x0 + RAIL), (x1 - RAIL, x1)):
        for y in range(y0, y1):
            t = (y - y0) / (y1 - y0)
            hi = 1 - t if uphill_north else t
            g = lerp(150, 230, hi)
            d.line([(a, y), (b, y)], fill=(g, g, g, 255))
    d.rectangle([x0 + RAIL - 14, y0, x0 + RAIL, y1], fill=(110, 110, 110, 255))
    d.rectangle([x1 - RAIL, y0, x1 - RAIL + 14, y1], fill=(110, 110, 110, 255))
    return im


def east() -> Image.Image:
    """Uphill east. Stringers along north and south edges; the wedge's south side face is visible."""
    im = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x0, x1, y0, y1 = M, N - M, M, N - M
    face = int(0.30 * (y1 - y0))           # side face height at the high (east) end

    def bottom(x):                          # screen y of the top surface's south edge at column x
        t = (x - x0) / (x1 - x0)
        return y1 - int(face * t)

    for x in range(x0, x1):
        t = (x - x0) / (x1 - x0)
        g = lerp(95, 185, t)
        d.line([(x, y0 + RAIL), (x, bottom(x) - RAIL)], fill=(g, g, g, 255))
        s = lerp(150, 230, t)
        d.line([(x, y0), (x, y0 + RAIL)], fill=(s, s, s, 255))                    # north stringer top
        d.line([(x, bottom(x) - RAIL), (x, bottom(x))], fill=(s, s, s, 255))      # south stringer top
        f = lerp(120, 150, t)
        d.line([(x, bottom(x)), (x, y1)], fill=(f, f, f, 255))                    # wedge side face
    span = (x1 - x0) / CLEATS
    for i in range(CLEATS):
        cx = int(x0 + span * (i + 0.5))
        t = (cx - x0) / (x1 - x0)
        top = lerp(130, 215, t)
        d.rectangle([cx - 10, y0 + RAIL, cx + 22, bottom(cx) - RAIL], fill=(top, top, top, 255))
        d.rectangle([cx - 24, y0 + RAIL, cx - 10, bottom(cx) - RAIL], fill=(lerp(120, 170, t),) * 3 + (255,))
    # earth layering lines on the side face
    for k in (0.33, 0.66):
        pts = [(x, bottom(x) + int((y1 - bottom(x)) * k)) for x in range(x0 + 40, x1, 8)]
        d.line(pts, fill=(100, 100, 100, 255), width=4)
    return im


def main(out: Path):
    out.mkdir(parents=True, exist_ok=True)
    north_or_south(True).save(out / "guide_north.png")
    north_or_south(False).save(out / "guide_south.png")
    e = east()
    e.save(out / "guide_east.png")
    e.transpose(Image.FLIP_LEFT_RIGHT).save(out / "guide_west.png")


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else "."))
