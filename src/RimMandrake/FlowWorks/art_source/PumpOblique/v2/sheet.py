"""sheet.py <showing dir> <dated dir> <out.png>: the owner's pick sheet, one row per look, one true relative scale.
Columns: tank | installed | 5 Nov candidate | new | new joined to the look's pipes (mock-up, pipes drawn under) | tank."""
import os, sys
from PIL import Image, ImageDraw, ImageFont
D, N, OUT = sys.argv[1:4]
HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.normpath(os.path.join(HERE, "../../../Textures/RimMandrake/FlowWorks"))
BG, INK, MARK = (176, 150, 112), (40, 24, 12), (110, 52, 14)
C = 400                                     # px per cell
J = int(C * 1.5)                            # joined mock-up: 1.5 cells square
font = lambda s: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", s)
cols, x = [], 40
for name, w in (("tank", 2 * C), ("installed now", C), ("5 Nov (rejected)", C), ("NEW", C), ("NEW, joined to pipes (mock-up)", J), ("tank", 2 * C)):
    cols.append((name, x, w)); x += w + 60
W = x - 20
RH, TOP = J + 100, 190
im = Image.new("RGBA", (W, TOP + 4 * RH), BG + (255,)); d = ImageDraw.Draw(im)
d.text((40, 24), "Liquid pump, four looks. Everything at one scale: the tank is 2x2 cells, the pump 1x1.", INK, font(44))
for t, cx, w in cols:
    d.text((cx + w / 2 - d.textlength(t, font(38)) / 2, 112), t, INK, font(38))


def atlas(look, i):
    a = Image.open(os.path.join(TEX, "Pipe", look, "UniversalPipe_Atlas.png")).convert("RGBA"); c = a.width / 4
    ax, ay = (i % 4) * c + c * .125, a.height - (i // 4 + 1) * c + c * .125
    return a.crop((int(ax), int(ay), int(ax + c * .75), int(ay + c * .75))).resize((C, C), Image.LANCZOS)


for k, l in enumerate(("Scrapper", "Industrial", "Modern", "Futuristic")):
    y = TOP + k * RH; mid = y + RH // 2 + 20
    d.line((40, y, W - 40, y), fill=(130, 105, 72), width=3)
    d.text((40, y + 14), l, INK, font(48))
    tank = Image.open(os.path.join(TEX, "Tank", l, "RM_LiquidTank.png")).convert("RGBA").resize((2 * C, 2 * C), Image.LANCZOS)
    bb = tank.getbbox()
    tank = tank.crop((0, bb[1], 2 * C, bb[3]))
    for c in (cols[0], cols[5]):
        im.alpha_composite(tank, (c[1], mid - tank.height // 2))
    new = Image.open(os.path.join(N, "candidates", l + ".png")).convert("RGBA").resize((C, C), Image.LANCZOS)
    for c, p in ((cols[1], os.path.join(HERE, "..", "plan", l + ".png")), (cols[2], os.path.join(D, "candidates", l + ".png"))):
        im.alpha_composite(Image.open(p).convert("RGBA").resize((C, C), Image.LANCZOS), (c[1], mid - C // 2))
    d.rounded_rectangle((cols[3][1] - 16, mid - C // 2 - 16, cols[3][1] + C + 16, mid + C // 2 + 16), 18, outline=MARK, width=6)
    im.alpha_composite(new, (cols[3][1], mid - C // 2))
    j = Image.new("RGBA", (3 * C, 3 * C), (0, 0, 0, 0))
    for dx, dy, i in ((1, 0, 5), (1, 2, 5), (0, 1, 10), (2, 1, 10), (1, 1, 15)):
        j.alpha_composite(atlas(l, i), (dx * C, dy * C))
    j.alpha_composite(new, (C, C)); g = (3 * C - J) // 2
    im.alpha_composite(j.crop((g, g, g + J, g + J)), (cols[4][1], mid - J // 2))
im.convert("RGB").save(OUT)
