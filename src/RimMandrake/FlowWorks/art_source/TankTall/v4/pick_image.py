#!/usr/bin/env python3
"""The one pick image for RIMMANDRAKE_DRAW_TALL_CARGO_XTALL_TANKS_IN_HIS_PICKED_DESIGNS: per look (Industrial, Futuristic),
his picked base tank, then each of the tall, cargo and extra-tall tanks as it ships today (kept 2026-10-15) beside the new
drawing in his picked design, at 64 px/cell on ground at the engine's placement (drawSize x ppc centred on the footprint
centre + drawOffset), beside a vanilla colonist. usage: pick_image.py <out.png>"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw
REPO = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(REPO / "src/RimMandrake/Utils/art"))
import scale_panel as sp  # noqa: E402
P = 64
TEX = REPO / "src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Tank"
NEW = Path(__file__).resolve().parent
SIZES = [("RM_LiquidTankTall", (2, 3), 0.5, "tall liquid tank"), ("RM_UniversalCargoTank", (2, 2), 0.0, "cargo tank"),
         ("RM_UniversalCargoTankXTall", (2, 4), 1.0, "extra-tall cargo tank")]
F, S = sp._font(22), sp._font(15)


def row(look):
    cols, rows = 20, 6
    W, H = cols * P, rows * P + 70
    im = Image.new("RGBA", (W, H), (139, 118, 88, 255)); d = ImageDraw.Draw(im)
    for gx in range(cols + 1): d.line([gx * P, 70, gx * P, H], fill=(129, 109, 81, 255))
    for gz in range(rows + 1): d.line([0, 70 + gz * P, W, 70 + gz * P], fill=(129, 109, 81, 255))
    d.text((10, 8), f"{look}", fill=(255, 255, 120, 255), font=sp._font(30))

    def place(path, draw, off, x, lab, col=(255, 255, 230, 255)):
        img = Image.open(path).convert("RGBA")
        cx = (x + 1) * P; cz = H - 2 * P - off * P
        w, h = round(draw[0] * P), round(draw[1] * P)
        im.alpha_composite(img.convert("RGBa").resize((w, h), Image.BOX).convert("RGBA"), (round(cx - w / 2), round(cz - h / 2)))
        d.text((x * P + 2, H - P + 4), lab, fill=col, font=S)
    place(TEX / look / "RM_LiquidTank.png", (2, 2), 0, 0, "his pick (base)", (255, 255, 120, 255))
    x = 3
    for tank, draw, off, lab in SIZES:
        d.text((x * P + 2, 76), lab, fill="white", font=F)
        place(TEX / look / f"{tank}.png", draw, off, x, "ships now")
        place(NEW / look / f"{tank}.png", draw, off, x + 2, "NEW", (140, 255, 140, 255))
        d.line([(x + 4.5) * P, 70, (x + 4.5) * P, H], fill=(60, 50, 40, 255), width=3); x += 5
    hum, m, hoff = sp.human_sprite(P)
    im.alpha_composite(hum, (round((x + 0.5) * P - m / 2), round(H - 1.5 * P - m / 2 - hoff)))
    d.text((x * P + 2, H - P + 4), "colonist", fill=(255, 255, 230, 255), font=S)
    return im


rs = [row(l) for l in ("Industrial", "Futuristic")]
out = Image.new("RGB", (rs[0].width, sum(r.height for r in rs) + 8 + 60), (40, 36, 32))
ImageDraw.Draw(out).text((10, 14), "FlowWorks tanks, true scale (64 px/cell). Left: your picked base tank. Each size: what ships now (kept "
                         "2026-10-15) | NEW, drawn in your pick.", fill="white", font=sp._font(17))
y = 60
for r in rs: out.paste(r, (0, y)); y += r.height + 8
out.save(sys.argv[1]); print(sys.argv[1], out.size)
