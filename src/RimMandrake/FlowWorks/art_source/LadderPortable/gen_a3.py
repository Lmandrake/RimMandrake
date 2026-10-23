"""Option A3 = A2 (thickness, keyline, crispness; north/south unchanged) with a steeper, taller west/east: ~12 deg lean,
strong foreshortening (top rungs narrower, foot wider), ~340 px tall so it spans the pit wall.   python3 gen_a3.py OUTDIR"""
import sys
from pathlib import Path
import gen as G
import gen_a2 as A2

W = [(80, 22), (164, 22), (264, 362), (132, 362)]

if __name__ == "__main__":
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    L = G.upright()
    A2.THICK = 2
    north = A2.facing(L, A2.QUADS["N"]); south = A2.facing(L, A2.QUADS["S"], (0.0, 0.30))
    A2.THICK = 3
    west = A2.facing(L, W)
    for f, im in {"north": north, "south": south, "west": west, "east": G.mirror(west)}.items():
        im.save(out / f"optA3_{f}.png")
