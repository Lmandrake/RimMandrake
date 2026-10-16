"""Old vs new RM_PitRamp at game scale: each facing in a pit at 64 px/cell, then each facing at 2 cells.

    python3 sheet_v2.py OUT.png ROW_LABEL=DIR [ROW_LABEL=DIR ...]   (DIR holds RM_PitRamp_<facing>.png)
Pit scene as ../sheet.py: flat-tinted ground and floor, the pit's north wall drawn with RM_WallFace_North.
"""
import random
import sys
from pathlib import Path
from PIL import Image, ImageDraw

TEX = Path(__file__).resolve().parents[3] / "Textures" / "Things" / "Building" / "FlowWorks"
C = 64
GROUND, FLOOR = (170, 138, 96), (112, 86, 58)
FACINGS = (("north", 2, 1), ("east", 3, 2), ("south", 2, 3), ("west", 1, 2))


def noisy(w, h, rgb, seed):
    r = random.Random(seed)
    im = Image.new("RGBA", (w, h))
    im.putdata([tuple(max(0, min(255, v + k)) for v in rgb) + (255,) for k in (r.randint(-7, 7) for _ in range(w * h))])
    return im


def sprite(p, cells=1):
    return Image.open(p).convert("RGBA").convert("RGBa").resize((C * cells, C * cells), Image.BOX).convert("RGBA")


def scene(path, cx, cy, seed):
    im = noisy(5 * C, 5 * C, GROUND, seed)
    im.alpha_composite(noisy(3 * C, 3 * C, FLOOR, seed + 1), (C, C))
    wall = Image.open(TEX / "Excavation" / "RM_WallFace_North.png").convert("RGBA").resize((C, C // 2), Image.BOX)
    for x in (1, 2, 3):
        im.alpha_composite(wall, (x * C, C))
    im.alpha_composite(sprite(path), (cx * C, cy * C))
    return im


def main(out, rows):
    pad, lab = 12, 22
    W = pad + 4 * (5 * C + pad) + 4 * (2 * C + pad)
    rh = lab + 5 * C + pad
    sheet = Image.new("RGBA", (W, len(rows) * rh + pad), (40, 36, 32, 255))
    d = ImageDraw.Draw(sheet)
    for r, (label, folder) in enumerate(rows):
        y = pad + r * rh
        for i, (f, cx, cy) in enumerate(FACINGS):
            x = pad + i * (5 * C + pad)
            d.text((x, y), f"{label}: uphill {f}", fill=(235, 225, 210, 255))
            sheet.alpha_composite(scene(Path(folder) / f"RM_PitRamp_{f}.png", cx, cy, 3 + i), (x, y + lab))
        x0 = pad + 4 * (5 * C + pad)
        for i, (f, _, _) in enumerate(FACINGS):
            t = noisy(2 * C, 2 * C, FLOOR, 20 + i)
            t.alpha_composite(sprite(Path(folder) / f"RM_PitRamp_{f}.png", 2))
            sheet.alpha_composite(t, (x0 + i * (2 * C + pad), y + lab + (i // 2) * 0))
            d.text((x0 + i * (2 * C + pad), y + lab + 2 * C + 4), f"2x {f}", fill=(235, 225, 210, 255))
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    sheet.convert("RGB").save(out)
    print(out, sheet.size)


if __name__ == "__main__":
    main(sys.argv[1], [a.split("=", 1) for a in sys.argv[2:]])
