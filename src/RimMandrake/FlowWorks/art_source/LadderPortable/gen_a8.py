"""Option A8: follows the GPT v4 reading (gpt/v4_all_four_thinkfaces.png, gpt_experiment.md). Height is drawn UP the screen on every wall,
so west/east are the north ladder UPRIGHT and turned three-quarter (near rail lower, rungs as short diagonals), ~0.93 cell long, top at the
rim line leaning a touch toward its wall; (Owner 2026-10-23: E/W leaned the wrong way, so the drawn image is the EAST file and WEST is its mirror.) South is an upright stub (top ~0.4 of the ladder) whose foot is hidden by the near
lip. North = A7 north (A4 length, faint foot shadow). A2's thickness/keyline/4x-supersample crispness; no baked shadow on west/east/south
(a small attached one is the owner-allowed option; not needed here).   python3 gen_a8.py OUTDIR
North is rebuilt here exactly as gen_a7.py draws it (it used to be read back from OUTDIR/optA7_north.png, so gen_a8 failed
unless gen_a7 had run into the same folder first)."""
import sys
from pathlib import Path
from PIL import Image
import gen as G
import gen_a2 as A2
import gen_a4 as A4
import gen_a7 as A7

# src TL,TR,BR,BL on the 384 canvas; west = wall at the left (cell edge x=64); right rail starts ~0.16 cell lower
W = [(64, 50), (168, 96), (176, 344), (70, 296)]
S = [(124, 150), (260, 150), (266, 280), (118, 280)]   # drawn to y=280, cut at 270: no keyline across the hidden foot

TARGET = (122, 88, 58)   # RM_Ladder's wood mean; ours is greyer


def warm(im):
    import numpy as np
    a = np.array(im, float); m = (a[..., 3] > 200) & (a[..., :3].sum(-1) > 150)
    mean = a[m][:, :3].mean(0)
    g = np.clip(np.array(TARGET) / mean, 0.8, 1.6)
    rgb = a[..., :3] * g
    lum = rgb.mean(-1, keepdims=True); rgb = lum + (rgb - lum) * 1.25      # a little more saturation
    a[..., :3] = np.clip(rgb, 0, 255)
    return Image.fromarray(a.astype("uint8"), "RGBA")


if __name__ == "__main__":
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    L = G.upright()
    A2.THICK = 2
    north = A7.shade(A2.facing(L, A4.N), "y", 170, 100, 0.38, (4, 9), 4)      # = gen_a7.py's north
    A2.THICK = 4
    south = A2.facing(L, S, (0.0, 0.46))
    a = south.getchannel("A"); a.paste(0, (0, 270, 384, 384)); south.putalpha(a)
    A2.THICK = 6
    west = A2.facing(L, W)
    north, south, west = warm(north), warm(south), warm(west)
    for f, im in {"north": north, "south": south, "east": west, "west": G.mirror(west)}.items():
        im.save(out / f"optA8_{f}.png")
