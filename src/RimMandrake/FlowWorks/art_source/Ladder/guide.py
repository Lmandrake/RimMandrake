"""Grey camera blockouts for the wall-hung ladder (PIT_LADDER_REDRAW_HUNG_ON_THE_WALL), one per look.

Image 1 of each codex edit. The ladder is a 1x1 building on the PIT cell; its rotation names the pit wall it hangs on.
The canvas is that one cell, seen from the RimWorld building camera (orthographic, ~35 deg, light overhead-front).

  hung_north   slid DOWN on the far wall: upright, rungs face-on, hooks over the TOP edge, foot ~70% down
  hung_south   slid DOWN on the near wall: only the hook ends + top rungs show at the BOTTOM edge, the rest
               fades into the shadow behind the near lip (the engine does not occlude buildings there)
  hung_east    slid DOWN on the east wall: edge-on side profile against the RIGHT edge, hooks over it
  stowed_north slid UP: lying flat on the rim parallel to the wall (horizontal), hooks + rope coil toward the pit (down)
  stowed_south same, hooks + coil toward the pit (up)
  stowed_east  vertical, hooks + coil toward the pit (left)

    python3 guide.py OUTDIR      -> guide_<look>.png (1024 px)
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

N = 1024
RAIL, RUNG, HOOK, ROPE = (185, 185, 185, 255), (150, 150, 150, 255), (70, 70, 70, 255), (125, 125, 125, 255)


def upright(d, x0, x1, ytop, ybot, rungs=6, rail=46):
    """Face-on ladder: two vertical rails x0..x0+rail and x1-rail..x1, rungs between."""
    span = (ybot - ytop) / (rungs + 0.6)
    for i in range(rungs):
        y = int(ytop + span * (i + 0.8))
        d.rectangle([x0 + rail - 6, y, x1 - rail + 6, y + 28], fill=RUNG)
    d.rectangle([x0, ytop, x0 + rail, ybot], fill=RAIL)
    d.rectangle([x1 - rail, ytop, x1, ybot], fill=RAIL)


def hung_north():
    im = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x0, x1 = 300, 724
    upright(d, x0, x1, 40, 740)
    for x in (x0, x1 - 46):                       # iron hooks curling over the top edge (the far rim)
        d.rectangle([x - 4, 0, x + 50, 60], fill=HOOK)
    return im


def hung_south():
    im = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x0, x1 = 300, 724
    upright(d, x0, x1, 640, 1000, rungs=3)
    for x in (x0, x1 - 46):                       # hooks over the near rim at the bottom edge
        d.rectangle([x - 4, 960, x + 50, 1020], fill=HOOK)
    # fade: the ladder descends behind the near lip, darker and then gone toward the top
    a = im.getchannel("A")
    px = a.load()
    rgb = im.load()
    for y in range(600, 820):
        t = (y - 600) / 220
        for x in range(N):
            if px[x, y]:
                r, g, b, _ = rgb[x, y]
                k = 0.35 + 0.65 * t
                rgb[x, y] = (int(r * k), int(g * k), int(b * k), int(255 * t))
    return im


def hung_east():
    im = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # side profile: rails nearly overlap (near rail bright, far rail darker just behind), narrow, against the right edge
    xf, xt = 800, 900                             # foot x, top x (leans into the east wall)
    yt, yf = 50, 760
    d.line([(xf - 70, yf - 10), (xt - 70, yt - 10)], fill=(120, 120, 120, 255), width=38)    # far rail
    for i in range(8):                            # rungs: short stubs between the rails
        t = (i + 0.7) / 8.4
        x = xt + (xf - xt) * t
        y = yt + (yf - yt) * t
        d.line([(x - 70, y - 10), (x, y)], fill=RUNG, width=22)
    d.line([(xf, yf), (xt, yt)], fill=RAIL, width=44)                            # near rail
    d.rectangle([xt - 20, 20, 1020, 70], fill=HOOK)                               # hook over the right edge
    d.rectangle([980, 20, 1020, 110], fill=HOOK)
    return im


def stowed(pit_side):
    """Flat on the rim. Drawn for the north wall (horizontal, pit side = down) and rotated for the others."""
    im = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    y0, y1 = 400, 600                             # rails top/bottom of the lying ladder
    d.rectangle([90, y0, 934, y0 + 46], fill=RAIL)
    d.rectangle([90, y1 - 46, 934, y1], fill=RAIL)
    for i in range(6):
        x = 170 + i * 130
        d.rectangle([x, y0 + 40, x + 34, y1 - 40], fill=RUNG)
    # hooked (top) end at the right: hooks bend toward the pit side
    d.rectangle([920, y0, 975, y0 + 46], fill=HOOK)
    d.rectangle([920, y1 - 46, 975, y1], fill=HOOK)
    d.rectangle([950, y0, 985, y0 + 110], fill=HOOK)
    d.rectangle([950, y1 - 46, 985, y1 + 70], fill=HOOK)
    # short rope coil lying on the pit side
    d.ellipse([430, y1 + 30, 600, y1 + 130], outline=ROPE, width=26)
    d.line([(515, y1), (515, y1 + 40)], fill=ROPE, width=18)
    if pit_side == "down":
        return im
    if pit_side == "up":
        return im.transpose(Image.FLIP_TOP_BOTTOM)
    return im.rotate(-90)                         # pit side left: ladder vertical, coil + hooks to the left


def main(out: Path):
    out.mkdir(parents=True, exist_ok=True)
    looks = {"hung_north": hung_north(), "hung_south": hung_south(), "hung_east": hung_east(),
             "stowed_north": stowed("down"), "stowed_south": stowed("up"), "stowed_east": stowed("left")}
    for k, im in looks.items():
        im.save(out / f"guide_{k}.png")
    print(" ".join(looks))


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else "."))
