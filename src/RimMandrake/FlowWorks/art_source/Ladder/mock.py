"""In-pit mock at game scale: a 4x4-cell pit with ladders hung on its N, S, E, W walls and stowed ones on the rim.

64 px per cell (normal play zoom), plus a 2x crop. The pit's far (north) wall face is FlowWorks' RM_WallFace_North on
the top pit row; the side and near edges are thin dark lips as in game. Stowed art is drawn offset 0.55 cell toward its
wall, as the code will. The near lip does NOT occlude buildings in game, so nothing here occludes either.

    python3 mock.py <dir with RM_Ladder*.png> OUT.png
"""
import random
import sys
from pathlib import Path
from PIL import Image, ImageDraw

TEX = Path(__file__).resolve().parents[2] / "Textures" / "Things" / "Building" / "FlowWorks"
C = 64
GROUND, FLOOR = (150, 122, 88), (52, 44, 36)


def noisy(w, h, rgb, seed):
    r = random.Random(seed)
    im = Image.new("RGBA", (w, h), rgb + (255,))
    px = im.load()
    for y in range(h):
        for x in range(w):
            k = r.randint(-6, 6)
            px[x, y] = tuple(max(0, min(255, v + k)) for v in rgb) + (255,)
    return im


def scene(src: Path, c=C):
    W = H = 6
    im = noisy(W * c, H * c, GROUND, 1)
    im.alpha_composite(noisy(4 * c, 4 * c, FLOOR, 2), (c, c))
    wall = Image.open(TEX / "Excavation" / "RM_WallFace_North.png").convert("RGBA").resize((c, c // 2), Image.BOX)
    for x in range(1, 5):
        im.alpha_composite(wall, (x * c, c))
    d = ImageDraw.Draw(im)
    d.rectangle([c, c, 5 * c - 1, 5 * c - 1], outline=(30, 26, 22, 255), width=max(2, c // 24))
    d.rectangle([c, 5 * c - c // 10, 5 * c - 1, 5 * c - 1], fill=(28, 24, 20, 255))  # near lip

    def put(name, cx, cy, dx=0.0, dy=0.0):
        s = Image.open(src / name).convert("RGBA").convert("RGBa").resize((c, c), Image.BOX).convert("RGBA")
        im.alpha_composite(s, (int((cx + dx) * c), int((cy + dy) * c)))

    put("RM_LadderHung_north.png", 2, 1)
    put("RM_LadderHung_south.png", 3, 4)
    put("RM_LadderHung_east.png", 4, 2)
    put("RM_LadderHung_west.png", 1, 3)
    put("RM_LadderStowed_north.png", 3, 1, dy=-0.55)
    put("RM_LadderStowed_south.png", 2, 4, dy=0.55)
    put("RM_LadderStowed_east.png", 4, 3, dx=0.55)
    put("RM_LadderStowed_west.png", 1, 2, dx=-0.55)
    return im


def main(src, out):
    a, b = scene(Path(src), C), scene(Path(src), 2 * C)
    pad = 16
    sheet = Image.new("RGBA", (a.width + b.width + 3 * pad, b.height + 2 * pad + 20), (36, 32, 28, 255))
    d = ImageDraw.Draw(sheet)
    d.text((pad, 4), "game scale 64 px/cell: hung N (top), S (bottom), E (right), W (left); stowed on the rim beside each",
           fill=(235, 225, 210, 255))
    sheet.alpha_composite(a, (pad, pad + 20))
    sheet.alpha_composite(b, (a.width + 2 * pad, pad + 20))
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    sheet.convert("RGB").save(out)
    print(out, sheet.size)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
