"""Option A4 = A3's thickness/keyline/crispness and south; north a touch longer; WEST redrawn as a ladder leaning toward the
viewer from the west wall: the top end touches the wall face (narrow, short rungs), the foot lies out on the floor (wider),
rails converge toward the wall, projected length shorter than north. East = mirror.   python3 gen_a4.py OUTDIR"""
import sys
from pathlib import Path
import gen as G
import gen_a2 as A2

N = [(136, 24), (248, 24), (264, 272), (120, 272)]
# src TL,TR,BR,BL: top (wall) end x=64 is the cell's west edge; foot at x~290
W = [(64, 172), (64, 224), (292, 270), (292, 130)]

if __name__ == "__main__":
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    L = G.upright()
    A2.THICK = 2
    north = A2.facing(L, N); south = A2.facing(L, A2.QUADS["S"], (0.0, 0.30))
    A2.THICK = 3
    west = A2.facing(L, W)
    for f, im in {"north": north, "south": south, "west": west, "east": G.mirror(west)}.items():
        im.save(out / f"optA4_{f}.png")
