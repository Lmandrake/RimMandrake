"""Raised-state rail ladder pictures for set v3a (sheet spikes_ladders_redraw column B; owner by card 2026-10-21:
"Install B, judge in game"). Derived deterministically from the shipped lowered pictures, so the two states share
every pixel that does not move:

  north  the outer rail strips (with their brackets) stay fixed; the ladder (poles, rungs, hooks) slides up
         RAISE_N px, poking above the far rim, leaving the empty rails below.
  east   no rails are drawn on this facing; the ladder slides out of the pit along its own axis (up-right) by
         RAISE_E px, so its foot leaves the floor and its hooks stand past the rim.
  west   east mirrored (as the lowered set).
  south  unchanged (set v3a keeps today's south, so today's RM_LadderRaised_south stays).

    python3 raised.py   -> out/a/RM_LadderRaised_{north,east,west}.png
"""
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
OUT = HERE / "out" / "a"
RAISE_N = 80                 # px on the 384 canvas (256 px per cell): ~0.31 cell, top stays on the canvas
RAIL_X = (111, 274)          # north: columns left of / right of these are the fixed rail strips
RAIL_TOP = 124               # north: above this row everything belongs to the ladder (hooks, top rung)
RAISE_E = (44, -10)          # east: along the ladder's axis (top rail slope ~ -0.23)


def north():
    im = Image.open(OUT / "RM_Ladder_north.png").convert("RGBA")
    w, h = im.size
    rails = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ladder = im.copy()
    px, rp, lp = im.load(), rails.load(), ladder.load()
    for y in range(RAIL_TOP, h):
        for x in range(w):
            if x < RAIL_X[0] or x >= RAIL_X[1]:
                rp[x, y] = px[x, y]
                lp[x, y] = (0, 0, 0, 0)
    out = rails.copy()
    out.alpha_composite(ladder.crop((0, RAISE_N, w, h)), (0, 0))   # ladder slid up RAISE_N, over the rails
    return out


def east():
    im = Image.open(OUT / "RM_Ladder_east.png").convert("RGBA")
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    dx, dy = RAISE_E
    out.alpha_composite(im.crop((0, -dy, im.width - dx, im.height)), (dx, 0))
    return out


def main():
    n, e = north(), east()
    assert n.getbbox()[1] > 0 and e.getbbox()[2] < e.width, "raised picture clipped at the canvas edge"
    n.save(OUT / "RM_LadderRaised_north.png")
    e.save(OUT / "RM_LadderRaised_east.png")
    e.transpose(Image.FLIP_LEFT_RIGHT).save(OUT / "RM_LadderRaised_west.png")
    print("ok", n.getbbox(), e.getbbox())


if __name__ == "__main__":
    main()
