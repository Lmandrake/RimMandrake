"""Game-scale contact sheet: RM_PitRamp in each rotation inside a pit, RM_Ladder lowered vs raised.

64 px per cell (a normal play zoom), ground and pit floor flat-tinted, the pit's north wall drawn with
FlowWorks' own RM_WallFace_North, every sprite drawn from the installed Textures/ file at drawSize 1.

    python3 sheet.py OUT.png
"""
import random
import sys
from pathlib import Path
from PIL import Image, ImageDraw

TEX = Path(__file__).resolve().parents[2] / "Textures" / "Things" / "Building" / "FlowWorks"
C = 64
GROUND = (170, 138, 96)
FLOOR = (112, 86, 58)


def noisy(w, h, rgb, seed):
    r = random.Random(seed)
    im = Image.new("RGBA", (w, h), rgb + (255,))
    px = im.load()
    for y in range(h):
        for x in range(w):
            k = r.randint(-7, 7)
            px[x, y] = tuple(max(0, min(255, v + k)) for v in rgb) + (255,)
    return im


def sprite(rel, cells=1):
    return Image.open(TEX / rel).convert("RGBA").convert("RGBa").resize((C * cells, C * cells), Image.BOX).convert("RGBA")


def pit_scene(pit, things, w=5, h=5, seed=1):
    """pit = (x0, y0, x1, y1) cells, inclusive, screen rows from the top. things = [(rel, cx, cy)]."""
    im = noisy(w * C, h * C, GROUND, seed)
    x0, y0, x1, y1 = pit
    im.alpha_composite(noisy((x1 - x0 + 1) * C, (y1 - y0 + 1) * C, FLOOR, seed + 1), (x0 * C, y0 * C))
    wall = Image.open(TEX / "Excavation" / "RM_WallFace_North.png").convert("RGBA")
    wall = wall.resize((C, C // 2), Image.BOX)
    for cx in range(x0, x1 + 1):           # the pit's north wall: the face below the rim, drawn on the top pit row
        im.alpha_composite(wall, (cx * C, y0 * C))
    for rel, cx, cy in things:
        im.alpha_composite(sprite(rel), (cx * C, cy * C))
    return im


def main(out):
    ramp = "Excavation/RM_PitRamp_{}.png"
    # Each ramp sits on the pit square at the edge it climbs to.
    scenes = [
        ("ramp, uphill north", pit_scene((1, 1, 3, 3), [(ramp.format("north"), 2, 1)], seed=3)),
        ("ramp, uphill east", pit_scene((1, 1, 3, 3), [(ramp.format("east"), 3, 2)], seed=4)),
        ("ramp, uphill south", pit_scene((1, 1, 3, 3), [(ramp.format("south"), 2, 3)], seed=5)),
        ("ramp, uphill west", pit_scene((1, 1, 3, 3), [(ramp.format("west"), 1, 2)], seed=6)),
        ("ladder lowered | raised", pit_scene((1, 1, 3, 3), [("Canals/RM_Ladder.png", 1, 2),
                                                             ("Canals/RM_LadderRaised.png", 3, 2)], seed=7)),
    ]
    pad, lab = 12, 22
    W = len(scenes) * (5 * C + pad) + pad
    sheet = Image.new("RGBA", (W, 5 * C + lab + 2 * pad + 2 * C + pad), (40, 36, 32, 255))
    d = ImageDraw.Draw(sheet)
    for i, (name, sc) in enumerate(scenes):
        x = pad + i * (5 * C + pad)
        d.text((x, pad // 2), name, fill=(235, 225, 210, 255))
        sheet.alpha_composite(sc, (x, lab))
    # zoomed row: the four ramp facings and both ladders at 2 cells each on bare floor
    y = lab + 5 * C + pad
    zs = [ramp.format(f) for f in ("north", "east", "south", "west")] + ["Canals/RM_Ladder.png", "Canals/RM_LadderRaised.png"]
    for i, rel in enumerate(zs):
        tile = noisy(2 * C, 2 * C, FLOOR, 20 + i)
        tile.alpha_composite(sprite(rel, 2))
        sheet.alpha_composite(tile, (pad + i * (2 * C + pad), y))
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    sheet.convert("RGB").save(out)
    print(out, sheet.size)


if __name__ == "__main__":
    main(sys.argv[1])
