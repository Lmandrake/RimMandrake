"""TANK_TALL_BUILD_TWICE_THE_DRINK v3: the tank family review scene - four tanks x the four Gimme Some Slack looks, one row per
look, at game scale on ground, in front of a vanilla brick wall run, beside vanilla's refinery and a colonist. Placement is
the engine's: drawSize x ppc centred on footprint centre + drawOffset. Reads the fitted candidates in v3/<Look>/<Tank>.png.
usage: scene_family.py <out.png> [ppc] [looks dir: <dir>/<Look>/<Tank>.png, default v3; the installed art is
src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Tank]"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw
sys.path.insert(0, "src/RimMandrake/Utils/art")
import scale_panel as sp
P = int(sys.argv[2]) if len(sys.argv) > 2 else 80
CACHE = Path("/mnt/d/Luke/dev/RimMandrake/observed/inventory/bundle_textures/ludeon.rimworld.core")
V3 = Path(sys.argv[3]) if len(sys.argv) > 3 else Path("src/RimMandrake/FlowWorks/art_source/TankTall/v3")
LOOKS = ["Scrapper", "Industrial", "Modern", "Futuristic"]
TANKS = [("RM_LiquidTank", (2, 2), 0.0, "liquid tank 80"), ("RM_LiquidTankTall", (2, 3), 0.5, "tall liquid tank 160"),
         ("RM_UniversalCargoTank", (2, 2), 0.0, "cargo tank 160"), ("RM_UniversalCargoTankXTall", (2, 4), 1.0, "extra-tall cargo 320")]
FONT, SMALL = sp._font(24), sp._font(15)
COLS, ROWS = 19, 6

def wall_cell():
    return Image.open(CACHE / "Wall_Atlas_Bricks.png").convert("RGBA").crop((160, 80, 240, 160))

def row(look):
    W, H = COLS * P, ROWS * P + 44
    im = Image.new("RGBA", (W, H), (139, 118, 88, 255)); d = ImageDraw.Draw(im)
    for gx in range(COLS + 1): d.line([gx * P, 44, gx * P, H], fill=(129, 109, 81, 255))
    for gz in range(ROWS + 1): d.line([0, 44 + gz * P, W, 44 + gz * P], fill=(129, 109, 81, 255))
    d.text((10, 8), look, fill=(255, 255, 255, 255), font=FONT)
    def place(img, draw, foot, off, x, z):
        cx = (x + foot[0] / 2) * P; cz = H - (z + foot[1] / 2) * P - off * P
        w, h = round(draw[0] * P), round(draw[1] * P)
        im.alpha_composite(img.convert("RGBa").resize((w, h), Image.BOX).convert("RGBA"), (round(cx - w / 2), round(cz - h / 2)))
    wc = wall_cell()
    for x in range(COLS): place(wc, (1, 1), (1, 1), 0, x, ROWS - 1)
    x = 0
    for tank, draw, off, lab in TANKS:
        place(Image.open(V3 / look / f"{tank}.png").convert("RGBA"), draw, (2, 2), off, x, 1)
        d.text((x * P + 2, H - P + 4), lab, fill=(255, 255, 230, 255), font=SMALL); x += 3
    place(Image.open(CACHE / "Refinery_south.png").convert("RGBA"), (3, 2), (3, 2), 0, 12, 1)
    d.text((12 * P + 2, H - P + 4), "vanilla refinery", fill=(255, 255, 230, 255), font=SMALL)
    hum, m, hoff = sp.human_sprite(P)
    im.alpha_composite(hum, (round(16.5 * P - m / 2), round(H - 1.5 * P - m / 2 - hoff)))
    d.text((16 * P + 2, H - P + 4), "colonist", fill=(255, 255, 230, 255), font=SMALL)
    return im

rows = [row(l) for l in LOOKS]
out = Image.new("RGB", (rows[0].width, sum(r.height for r in rows) + 8 * 3 + 50), (40, 36, 32))
ImageDraw.Draw(out).text((10, 12), "FlowWorks tanks x Gimme Some Slack looks - " + ("installed (Textures)" if "Textures" in str(V3) else "staged candidates (v3)") + " - measured building camera (~35 deg, top rim 0.56)",
                         fill=(255, 255, 255), font=sp._font(22))
y = 50
for r in rows: out.paste(r, (0, y)); y += r.height + 8
out.save(sys.argv[1]); print(sys.argv[1], out.size)
