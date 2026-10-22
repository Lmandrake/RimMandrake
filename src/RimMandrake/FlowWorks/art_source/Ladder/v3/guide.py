"""Grey blockouts for the v3 rail-ladder redraw (RAIL_LADDER_REDRAW_CLIMB_NOT_CRAWL, owner walk 2026-10-21).

Owner: "North needs to hug the wall perspective tighter and come up along the wall (compress north/south perspective
direction). The East/West ones are hugely wrong: they need to go up/down but they are shown to be going horizontally
along the wall rather than out/in the pit."

Guides are 1024 px = the shipped 384 px canvas (drawSize 1.5, offset z +0.25 on N/E/W), so the cell occupies
x 171..853, y 341..1024 and the far rim is y 341, the east rim x 853.

  north  ladder flat on the far wall, rising up it, foreshortened to ~0.4 cell tall; wall rails beside the poles;
         hooks over the rim at the top
  east   ladder leaning from the east rim (hooks at x 853) down and out into the pit: rails run right -> left
         (top -> foot), slightly downward, rungs as short vertical bars; foot near the cell's middle
  stake  (spikes: see ../../Spikes/v3/guide.py)

    python3 guide.py OUTDIR
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

N = 1024
RAIL, RUNG, HOOK, WALLRAIL = (185, 185, 185, 255), (150, 150, 150, 255), (70, 70, 70, 255), (110, 110, 110, 255)


def north():
    im = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x0, x1, ytop, ybot, rail = 310, 714, 300, 610, 40
    for x in (x0 - 34, x1 + 4):                      # fixed wall rails just outside each pole
        d.rectangle([x, ytop + 30, x + 30, ybot + 6], fill=WALLRAIL)
        for y in (ytop + 60, (ytop + ybot) // 2, ybot - 20):
            d.rectangle([x - 8, y, x + 38, y + 16], fill=HOOK)
    for i in range(7):                               # rungs close together: foreshortened wall face
        y = int(ytop + 30 + (ybot - ytop - 50) * (i + 0.5) / 7)
        d.rectangle([x0 + rail - 6, y, x1 - rail + 6, y + 14], fill=RUNG)
    d.rectangle([x0, ytop, x0 + rail, ybot], fill=RAIL)
    d.rectangle([x1 - rail, ytop, x1, ybot], fill=RAIL)
    for x in (x0, x1 - rail):                        # hooks over the far rim
        d.rectangle([x - 4, ytop - 40, x + rail + 6, ytop + 10], fill=HOOK)
    return im


def east():
    im = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    top_x, foot_x = 850, 430                          # top at the east rim, foot out on the pit floor
    yc_top, yc_foot = 640, 720                        # foot sits lower on screen (deeper)
    half_top, half_foot = 120, 100                    # rail separation (ladder width, N-S on screen)
    rails = [((top_x, yc_top - half_top), (foot_x, yc_foot - half_foot)),
             ((top_x, yc_top + half_top), (foot_x, yc_foot + half_foot))]
    for i in range(6):                                # rungs: short vertical bars, parallel to the wall
        t = (i + 0.6) / 6.4
        x = top_x + (foot_x - top_x) * t
        ya = rails[0][0][1] + (rails[0][1][1] - rails[0][0][1]) * t
        yb = rails[1][0][1] + (rails[1][1][1] - rails[1][0][1]) * t
        d.line([(x, ya), (x, yb)], fill=RUNG, width=20)
    for (a, b) in rails:
        d.line([a, b], fill=RAIL, width=34)
    for (a, _) in rails:                              # hooks gripping the east rim
        d.rectangle([a[0] - 10, a[1] - 22, a[0] + 60, a[1] + 22], fill=HOOK)
    return im


if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parent / "guides")
    out.mkdir(parents=True, exist_ok=True)
    north().save(out / "guide_north.png")
    east().save(out / "guide_east.png")
    print("wrote", out)
