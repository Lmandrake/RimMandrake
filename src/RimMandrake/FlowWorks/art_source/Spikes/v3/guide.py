"""Grey blockout for the v3 pit spikes (PIT_SPIKES_REDRAW_SPOKES_NOT_LOGS, owner walk 2026-10-21).

Owner: "the spikes need to look much less chonky: spokes pointing up, not solid logs taking up every volume in a pit
with some cones at the top. SPIKES, that you can slide down. More like that please." (reference:
Transient/pile_2026-10-21/walk/spikes_reference_owner_2026-10-21.png - many thin sharpened stakes over the pit floor)

1024 px = the shipped 256 px canvas (drawSize 1, Graphic_Single). A jittered grid of thin stakes standing upright,
seen from the RimWorld building camera: each a narrow tapered spike, tip up (north), base a small dark dot. The floor
between them stays transparent (the pit floor terrain shows through).

    python3 guide.py OUTDIR [COUNT_PER_SIDE]
"""
import random
import sys
from pathlib import Path
from PIL import Image, ImageDraw

N = 1024


def stakes(per_side=6, seed=7):
    rnd = random.Random(seed)
    im = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pts = []
    step = (N - 160) / per_side
    for j in range(per_side):
        for i in range(per_side):
            x = 80 + step * (i + 0.5) + rnd.uniform(-step * 0.3, step * 0.3)
            y = 200 + (N - 240) * (j + 0.5) / per_side + rnd.uniform(-step * 0.25, step * 0.25)
            pts.append((x, y))
    pts.sort(key=lambda p: p[1])                     # back to front
    for x, y in pts:
        h = rnd.uniform(130, 175)
        w = rnd.uniform(16, 22)
        lean = rnd.uniform(-14, 14)
        d.ellipse([x - w * 0.8, y - 6, x + w * 0.8, y + 6], fill=(80, 80, 80, 255))
        d.polygon([(x - w / 2, y), (x + w / 2, y), (x + lean, y - h)], fill=(175, 175, 175, 255))
    return im


if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parent / "guides")
    out.mkdir(parents=True, exist_ok=True)
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    stakes(n).save(out / f"guide_stakes_{n}.png")
    print("wrote", out)
