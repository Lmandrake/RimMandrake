"""Option A5 = A4 with WEST redrawn so the top end crosses the west rim and rests on the ground outside the pit while the foot
stands on the pit floor (bridges the edge like north). Canvas 384 / drawSize 1.5: the cell's west edge is x=64, so at most 64 px
(0.25 cell) of overhang fits; the top end is at x=6. More overhang needs drawOffsetWest x<0 or a larger canvas.  East = mirror."""
import sys
from pathlib import Path
import gen as G
import gen_a2 as A2
import gen_a4 as A4

W = [(6, 164), (6, 238), (250, 264), (250, 136)]

if __name__ == "__main__":
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    L = G.upright()
    A2.THICK = 2
    north = A2.facing(L, A4.N); south = A2.facing(L, A2.QUADS["S"], (0.0, 0.30))
    A2.THICK = 3
    west = A2.facing(L, W)
    for f, im in {"north": north, "south": south, "west": west, "east": G.mirror(west)}.items():
        im.save(out / f"optA5_{f}.png")
