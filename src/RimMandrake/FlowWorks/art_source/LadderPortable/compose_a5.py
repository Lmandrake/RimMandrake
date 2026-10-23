"""Phone images for option A2: python3 compose_a2.py OPTDIR OUTDIR  (writes optA5_1_full/2_truescale/3_facings, compare_*_A2)."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
TEX = Path(__file__).resolve().parents[2] / "Textures" / "Things" / "Building" / "FlowWorks" / "Canals"
opt, out = Path(sys.argv[1]), Path(sys.argv[2])
BG = (110, 84, 58, 255)
f = lambda n: Image.open(opt / f"optA5_{n}.png").convert("RGBA")
try: FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
except Exception: FONT = None

def lab(im, t):
    ImageDraw.Draw(im).text((8, 4), t, fill=(240, 230, 210), font=FONT)

def scaled(im, ppc, size=1.5):
    n = round(ppc * size); return im.resize((n, n), Image.LANCZOS)

HUM = Path("/mnt/d/ClaudeWork/scratch/ladder_human")  # vanilla Naked_Male_south + Male_Average_Normal_south, extracted from resources.assets

def tint(im, c=(224, 172, 132)):
    r, g, b, a = im.split()
    ch = [x.point(lambda v, k=k: v * k // 255) for x, k in zip((r, g, b), c)]
    return Image.merge("RGBA", (*ch, a))

def human(d, cx, cy, ppc):  # vanilla body + head sprites (128 px = 1 cell at 128 px/cell), skin-tinted
    body = tint(Image.open(HUM / "Naked_Male_south.png").convert("RGBA")); head = tint(Image.open(HUM / "Male_Average_Normal_south.png").convert("RGBA"))
    n = round(ppc * 1.0)
    body = body.resize((n, n), Image.LANCZOS); head = head.resize((n, n), Image.LANCZOS)
    im = d._image
    im.alpha_composite(body, (int(cx - n / 2), int(cy - n / 2)))
    im.alpha_composite(head, (int(cx - n / 2), int(cy - n / 2 - 0.30 * ppc)))

def scene(ppc, facing, human_on=True, cur=None, cells=(4, 3)):
    W, H = cells[0] * ppc + 2 * ppc // 2, cells[1] * ppc + ppc
    im = Image.new("RGBA", (W, H), (150, 122, 88, 255)); d = ImageDraw.Draw(im); d._image = im
    x0, y0 = ppc // 2, ppc // 2
    rim = max(3, int(.3 * ppc)); ow = max(2, ppc // 40)
    PW, PH = cells[0] * ppc, cells[1] * ppc
    d.rectangle([x0 - ow, y0 - ow, x0 + PW + ow, y0 + PH + ow], fill=(8, 6, 5, 255))                 # black pit outline
    d.rectangle([x0, y0, x0 + PW, y0 + PH], fill=(112, 80, 52, 255))                                   # rim/wall band (lighter dirt)
    d.rectangle([x0 + rim, y0 + rim, x0 + PW - rim, y0 + PH - rim], fill=(38, 28, 22, 255))           # dark pit floor
    d.rectangle([x0, y0, x0 + PW, y0 + int(.45 * ppc)], fill=(128, 92, 58, 255))                      # north wall face reads taller
    d.rectangle([x0 + rim, y0 + int(.45 * ppc), x0 + PW - rim, y0 + int(.45 * ppc) + rim // 2], fill=(70, 50, 36, 255))
    if facing == "west": cx, cy = x0 + ppc // 2, y0 + int(1.5 * ppc)
    else: cx, cy = x0 + int(1.5 * ppc), y0 + ppc // 2
    cy -= int(.25 * ppc)   # drawOffset (0,0,0.25)
    art = cur if cur is not None else scaled(f(facing), ppc)
    if cur is not None: art = scaled(cur, ppc, 1.0)
    if cur is not None and facing == "west": cx -= 0
    im.alpha_composite(art, (cx - art.width // 2, cy - art.height // 2))
    if human_on: human(d, x0 + int(2.8 * ppc), y0 + int(1.9 * ppc), ppc)
    return im

# 1 full-res alone: north + west on a tile, 2 widths
c = Image.new("RGBA", (384 * 2, 384 + 30), BG); lab(c, "A5 full-res: north | west (384 px)")
c.alpha_composite(f("north"), (0, 30)); c.alpha_composite(f("west"), (384, 30)); c.save(out / "optA5_1_full.png")
# 2 true scale 128 px/cell beside human
a = scene(128, "west"); b = scene(128, "north"); W = a.width + b.width + 20
c = Image.new("RGBA", (W, a.height + 30), (34, 30, 26, 255)); lab(c, "A5 true scale, 128 px/cell, vanilla human sprite: west mount | north mount")
c.alpha_composite(a, (0, 30)); c.alpha_composite(b, (a.width + 20, 30))
c = c.resize((1560, round(c.height * 1560 / c.width)), Image.LANCZOS); c.save(out / "optA5_2_truescale.png")
# 3 facings
c = Image.new("RGBA", (384 * 4, 384 + 30), BG); lab(c, "A5 facings: north | south | west | east")
for i, n in enumerate(["north", "south", "west", "east"]): c.alpha_composite(f(n), (i * 384, 30))
c = c.resize((1536, round(c.height * 1536 / c.width)), Image.LANCZOS); c.save(out / "optA5_3_facings.png")
# 4 compare at 64 and 32 ppc: current portable, fixed RM_Ladder, A, A5 (west mount and north mount)
cur = Image.open(TEX / "RM_LadderPortableFlat.png").convert("RGBA")
fixed = {k: Image.open(TEX / f"RM_Ladder_{k}.png").convert("RGBA") for k in ("west", "north")}
A4 = {k: Image.open(opt / f"optA4_{k}.png").convert("RGBA") for k in ("west", "north")}
A = {k: Image.open(opt / f"optA_{k}.png").convert("RGBA") for k in ("west", "north")}
for ppc in (64, 32):
    for facing in ("west", "north"):
        cols = [("current", scene(ppc, facing, False, cur=cur)), ("fixed RM_Ladder", scene(ppc, facing, False))]
        cols[1] = ("fixed RM_Ladder", None)
        # fixed + A via direct art swap
        def sc(art):
            im = scene(ppc, facing, False); return im
        outs = []
        for name, art in [("current portable", None), ("fixed RM_Ladder", fixed[facing]), ("A (old)", A[facing]), ("A4", A4[facing]), ("A5", f(facing))]:
            if name == "current portable": im = scene(ppc, facing, False, cur=cur)
            else:
                im = scene(ppc, facing, False, cur=Image.new("RGBA", (4, 4)))
                a2 = scaled(art, ppc)
                x0, y0 = ppc // 2, ppc // 2
                cx, cy = (x0 + ppc // 2, y0 + int(1.5 * ppc)) if facing == "west" else (x0 + int(1.5 * ppc), y0 + ppc // 2)
                cy -= int(.25 * ppc)
                im.alpha_composite(a2, (cx - a2.width // 2, cy - a2.height // 2))
            outs.append((name, im))
        w = sum(i.width for _, i in outs) + 10 * len(outs); h = outs[0][1].height + 28
        c = Image.new("RGBA", (w, h), (34, 30, 26, 255)); x = 0
        for n, i in outs:
            ImageDraw.Draw(c).text((x + 6, 4), n, fill=(240, 230, 210), font=FONT); c.alpha_composite(i, (x, 28)); x += i.width + 10
        if c.width > 1600: c = c.resize((1600, round(c.height * 1600 / c.width)), Image.LANCZOS)
        c.save(out / f"compare_{ppc}ppc_{facing}_A5.png")
