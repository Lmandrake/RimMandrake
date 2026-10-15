"""TANK_TALL_BUILD_TWICE_THE_DRINK v2 review scene: CURRENT installed vs v2 candidates at game scale (96 px/cell),
on ground, in front of a vanilla brick wall run, beside vanilla's refinery and deep drill and a vanilla colonist.
Placement is the engine's: texture drawn drawSize x ppc, centred on footprint centre + drawOffset; south drawn last.
usage: scene.py <out.png>"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw
sys.path.insert(0, "src/RimMandrake/Utils/art")
import scale_panel as sp
P = 96
CACHE = Path("/mnt/d/Luke/dev/RimMandrake/observed/inventory/bundle_textures/ludeon.rimworld.core")
TEX = Path("src/RimMandrake/FlowWorks/Textures/Things/Building/FlowWorks")
V2 = Path("src/RimMandrake/FlowWorks/art_source/TankTall/v2")
FONT = sp._font(22); SMALL = sp._font(16)

def thing(png, draw, foot, off=0.0):
    return dict(img=Image.open(png).convert("RGBA"), draw=draw, foot=foot, off=off)

def wall_cell():
    a = Image.open(CACHE / "Wall_Atlas_Bricks.png").convert("RGBA")
    return a.crop((160, 80, 240, 160))            # a horizontal run piece (linked east + west)

def panel(title, tall, xtall):
    cols = 21; rows = 6
    W, H = cols * P, rows * P + 60
    im = Image.new("RGBA", (W, H), (139, 118, 88, 255)); d = ImageDraw.Draw(im)
    for gx in range(cols + 1): d.line([gx * P, 60, gx * P, H], fill=(129, 109, 81, 255))
    for gz in range(rows + 1): d.line([0, 60 + gz * P, W, 60 + gz * P], fill=(129, 109, 81, 255))
    d.text((12, 14), title, fill=(255, 255, 255, 255), font=FONT)
    def place(t, x, z, label=None):          # x, z = footprint SW cell (z counted up from the bottom row)
        fw, fh = t["foot"]; dw, dh = t["draw"]
        cx = (x + fw / 2) * P; cz = H - (z + fh / 2) * P - t["off"] * P
        w, h = round(dw * P), round(dh * P)
        img = t["img"].convert("RGBa").resize((w, h), Image.BOX).convert("RGBA")
        im.alpha_composite(img, (round(cx - w / 2), round(cz - h / 2)))
        if label:
            d.text((x * P + 4, H - z * P + 2 - 22), label, fill=(255, 255, 230, 255), font=SMALL)
    wc = wall_cell()
    for x in range(cols):                       # wall run along the back (north) row
        place(dict(img=wc, draw=(1, 1), foot=(1, 1), off=0), x, rows - 1)
    items = [  # (thing, x, label) - all stand on row z=1, so their south edges share one ground line
        (thing(TEX / "RM_LiquidTank.png", (2, 2), (2, 2)), 0, "LiquidTank 80"),
        (tall, 3, "LiquidTankTall 160"),
        (thing(TEX / "RM_UniversalCargoTank.png", (2, 2), (2, 2)), 6, "CargoTank 160"),
        (xtall, 9, "CargoTankXTall 320"),
        (thing(CACHE / "Refinery_south.png", (3, 2), (3, 2)), 12, "vanilla refinery"),
        (thing(CACHE / "DeepDrill.png", (2, 2), (1, 1)), 16, "deep drill"),
    ]
    for t, x, lab in sorted(items, key=lambda r: -r[0]["foot"][1]):
        place(t, x, 1)
    for t, x, lab in items:
        d.text((x * P + 4, H - 1 * P + 6), lab, fill=(255, 255, 230, 255), font=SMALL)
    hum, m, hoff = sp.human_sprite(P)
    im.alpha_composite(hum, (round(18.5 * P - m / 2), round(H - 1.5 * P - m / 2 - hoff)))
    d.text((18 * P + 4, H - 1 * P + 6), "colonist", fill=(255, 255, 230, 255), font=SMALL)
    return im

cur = panel("CURRENT (installed 53dadcf232cc / 9fece3b324): side-elevation tall tanks",
            thing(TEX / "RM_LiquidTankTall.png", (2, 3), (2, 2), 0.5), thing(TEX / "RM_UniversalCargoTankXTall.png", (2, 4), (2, 2), 1.0))
new = panel("v2 CANDIDATE (not installed): ~34 deg orthographic, top ellipse 0.56-0.57, defs unchanged (2x3 +0.5 / 2x4 +1.0)",
            thing(V2 / "RM_LiquidTankTall_v2.png", (2, 3), (2, 2), 0.5), thing(V2 / "RM_UniversalCargoTankXTall_v2.png", (2, 4), (2, 2), 1.0))
out = Image.new("RGB", (cur.width, cur.height * 2 + 10), (40, 36, 32))
out.paste(cur, (0, 0)); out.paste(new, (0, cur.height + 10)); out.save(sys.argv[1]); print(sys.argv[1], out.size)
