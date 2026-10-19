"""True-scale preview: the rail-mounted ladder on all four walls of a mock pit, lowered and raised, beside a vanilla colonist.

Each texture is drawn as the engine does: the full 384 px canvas on a 1.5-cell quad centred on the cell plus the def's
per-rotation drawOffset (compose.OFFSETS). The pit (far wall face on the top row, thin side/near lips) is a mock, as in
../mock.py; nothing occludes, as in game.

    python3 preview.py TEXDIR OUT.png
"""
import random
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[3] / "Utils" / "art"))
import compose                          # noqa: E402
import scale_panel                      # noqa: E402

TEX = HERE.parents[2] / "Textures" / "Things" / "Building" / "FlowWorks"
GROUND, FLOOR = (150, 122, 88), (52, 44, 36)
W, H = 7, 6                                         # cells; pit interior x 1..5, y 1..4 (rows from the top)
SPOTS = {"north": (2, 1), "east": (5, 3), "west": (1, 2), "south": (4, 4)}


def noisy(w, h, rgb, seed):
    r = random.Random(seed)
    im = Image.new("RGB", (w, h), rgb)
    px = im.load()
    for y in range(h):
        for x in range(w):
            k = r.randint(-6, 6)
            px[x, y] = tuple(max(0, min(255, v + k)) for v in rgb)
    return im.convert("RGBA")


def scene(tex: Path, raised: bool, c: int):
    im = noisy(W * c, H * c, GROUND, 1)
    im.alpha_composite(noisy(5 * c, 4 * c, FLOOR, 2), (c, c))
    wall = Image.open(TEX / "Excavation" / "RM_WallFace_North.png").convert("RGBA").resize((c, c // 2), Image.BOX)
    for x in range(1, 6):
        im.alpha_composite(wall, (x * c, c))
    d = ImageDraw.Draw(im)
    d.rectangle([c, c, 6 * c - 1, 5 * c - 1], outline=(30, 26, 22, 255), width=max(2, c // 24))
    d.rectangle([c, 5 * c - c // 10, 6 * c - 1, 5 * c - 1], fill=(28, 24, 20, 255))      # near lip
    name = "RM_LadderRaised" if raised else "RM_Ladder"
    q = round(1.5 * c)
    for fac, (cx, cy) in SPOTS.items():
        t = Image.open(tex / f"{name}_{fac}.png").convert("RGBa").resize((q, q), Image.BOX).convert("RGBA")
        ox, oz = compose.OFFSETS[fac]
        px = (cx + 0.5 + ox) * c - q / 2
        py = (cy + 0.5 - oz) * c - q / 2
        im.alpha_composite(t, (round(px), round(py)))
    hum, m, hoff = scale_panel.human_sprite(c)
    hx, hy = 3, 3                                                                       # a colonist on the pit floor
    im.alpha_composite(hum, (round((hx + 0.5) * c - m / 2), round((hy + 0.5) * c - m / 2 - hoff)))
    return im


def main(tex, out):
    tex = Path(tex)
    pad, lab = 16, 22
    rows = []
    for c in (128, 64):
        rows.append([scene(tex, False, c), scene(tex, True, c)])
    wtot = max(sum(s.width for s in r) + pad * (len(r) + 1) for r in rows)
    htot = sum(r[0].height + lab + pad for r in rows) + pad + lab
    sheet = Image.new("RGBA", (wtot, htot), (36, 32, 28, 255))
    d = ImageDraw.Draw(sheet)
    try:
        f = ImageFont.truetype("DejaVuSans.ttf", 15)
    except OSError:
        f = ImageFont.load_default()
    d.text((pad, 6), "RM_Ladder on rails (owner spec 2026-10-18). Walls: N top row, E right, W left, S bottom row. "
           "Vanilla colonist for scale.", fill=(220, 210, 190), font=f)
    y = pad + lab
    for r, c in zip(rows, (128, 64)):
        x = pad
        for s, st in zip(r, ("LOWERED (slid down)", "RAISED (slid up; empty rails below)")):
            d.text((x, y), f"{st} - {c} px/cell", fill=(220, 210, 190), font=f)
            sheet.alpha_composite(s, (x, y + lab))
            x += s.width + pad
        y += r[0].height + lab + pad
    sheet.save(out)
    print(out, sheet.size)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
