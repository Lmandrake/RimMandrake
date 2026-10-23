"""GPT perspective experiment reference: a 2x2 superdeep (D4) pit as RM_ExcavationWalls draws it, 128 px/cell,
with the A7 north-mount ladder. python3 gpt_reference.py OPTDIR OWNER_SHOT OUT.png [--noladder OUT2.png]
Numbers from RM_WallFaceMath (D4): north face 0.50 cell, side strips 0.23 (west shaded, east lit x1.29),
rim line 0.04, south lining 0.08; ladder drawSize 1.5, drawOffset (0,0,0.25)."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
P = 128; M = 1; N = 2  # px/cell, margin cells, pit cells
opt, shot, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
W = (N + 2 * M) * P
src = Image.open(shot).convert("RGB").crop((300, 90, 700, 330)).resize((int(400 * 1.9), int(240 * 1.9)), Image.LANCZOS)
ground = Image.new("RGBA", (W, W))
for x in range(0, W, src.width):
    for y in range(0, W, src.height): ground.paste(src, (x, y))
im = ground.copy(); d = ImageDraw.Draw(im)
x0 = y0 = M * P; x1 = y1 = (M + N) * P
nf, sw, rl, sl = int(.50 * P), int(.23 * P), max(2, int(.04 * P)), int(.08 * P)
# floor: dark earth, darker toward the walls
floor = Image.new("RGBA", (x1 - x0, y1 - y0), (44, 33, 26, 255))
vig = Image.new("L", floor.size, 0); ImageDraw.Draw(vig).rectangle([18, 18, floor.width - 18, floor.height - 18], fill=255)
vig = vig.filter(ImageFilter.GaussianBlur(22))
floor = Image.composite(floor, Image.new("RGBA", floor.size, (24, 18, 14, 255)), vig)
im.alpha_composite(floor, (x0, y0))
def tex(box, k):  # the ground's own texture, lit by factor k
    c = ground.crop(box).point(lambda v: min(255, int(v * k)))
    return c
# north face (lit, the face the camera sees), darkening toward its foot
face = tex((x0, y0, x1, y0 + nf), 1.0)
grad = Image.new("RGBA", face.size)
gd = ImageDraw.Draw(grad)
for yy in range(face.height):
    t = yy / face.height
    gd.line([(0, yy), (face.width, yy)], fill=(255, 236, 200, int(70 * (1 - t))) if t < .5 else (0, 0, 0, int(150 * (t - .5) * 2)))
face = Image.alpha_composite(face.convert("RGBA"), grad)
# side strips with 45-degree mitre at the face's foot
west = tex((x0, y0, x0 + sw, y1), 0.62).convert("RGBA"); east = tex((x1 - sw, y0, x1, y1), 1.18).convert("RGBA")
im.alpha_composite(west, (x0, y0)); im.alpha_composite(east, (x1 - sw, y0))
mask = Image.new("L", (x1 - x0, nf), 255); md = ImageDraw.Draw(mask)
md.polygon([(0, 0), (sw, nf), (0, nf)], fill=0); md.polygon([(x1 - x0, 0), (x1 - x0 - sw, nf), (x1 - x0, nf)], fill=0)
im.paste(face, (x0, y0), mask)
# outline: rim line on north/sides, thicker dark lining on the near (south) edge
d.rectangle([x0 - rl, y0 - rl, x1 + rl, y0], fill=(6, 5, 4, 255))
d.rectangle([x0 - rl, y0, x0, y1], fill=(6, 5, 4, 255)); d.rectangle([x1, y0, x1 + rl, y1], fill=(6, 5, 4, 255))
d.rectangle([x0 - rl, y1 - sl // 2, x1 + rl, y1 + sl // 2], fill=(6, 5, 4, 255))
base = im.copy()
lad = Image.open(opt / "optA7_north.png").convert("RGBA").resize((int(1.5 * P),) * 2, Image.LANCZOS)
cx = x0 + P            # pit centre column line: centred on the north wall, between the two cells
cy = y0 + P // 2 - P // 4  # north-row cell centre, drawOffset +0.25 north
im.alpha_composite(lad, (cx - lad.width // 2, cy - lad.height // 2))
im.convert("RGB").save(out)
if "--noladder" in sys.argv: base.convert("RGB").save(sys.argv[sys.argv.index("--noladder") + 1])
