"""Grey blockout for the wall rails of the rail-mounted pit ladder (PIT_LADDER_RAILS_ON_THE_WALL, owner 2026-10-18).

Only the RAILS are generated: the ladder is the existing master (../raw/B_hung_north.png) and every facing/state is
composited from these two flat parts by compose.py, so the rails cannot move between lowered and raised.

    python3 guide.py OUTDIR   -> guide_rails_front.png (1024 px)
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

N = 1024
RAIL, PLATE, BOLT = (175, 175, 175, 255), (80, 80, 80, 255), (40, 40, 40, 255)
X_RAILS = (320, 704)          # rail centre lines; the ladder's two poles ride in these channels
W = 64                        # channel width


def rails_front():
    im = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for cx in X_RAILS:
        d.rectangle([cx - W // 2, 24, cx + W // 2, 1000], fill=RAIL)
        d.rectangle([cx - 8, 40, cx + 8, 985], fill=(120, 120, 120, 255))          # the groove the pole rides in
        for y in (90, 380, 670, 930):                                               # bracket plates bolted to the wall
            d.rectangle([cx - W // 2 - 30, y - 34, cx + W // 2 + 30, y + 34], fill=PLATE)
            for bx in (cx - W // 2 - 16, cx + W // 2 + 16):
                for by in (y - 18, y + 18):
                    d.ellipse([bx - 8, by - 8, bx + 8, by + 8], fill=BOLT)
        d.rectangle([cx - W // 2 - 6, 960, cx + W // 2 + 6, 1010], fill=PLATE)     # foot stop block
    return im


if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parent / "guides")
    out.mkdir(parents=True, exist_ok=True)
    rails_front().save(out / "guide_rails_front.png")
    print(out / "guide_rails_front.png")
