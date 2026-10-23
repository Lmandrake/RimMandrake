"""Phone images for A8 on a 2x2 D4 pit drawn like gpt/ref_north_2x2.png (same RM_WallFaceMath numbers as gpt_reference.py).
python3 compose_a8.py OPTDIR OUTDIR"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont
HERE = Path(__file__).resolve().parent
TEX = HERE.parents[1] / "Textures" / "Things" / "Building" / "FlowWorks" / "Canals"
HUM = Path("/mnt/d/ClaudeWork/scratch/ladder_human")
opt, out = Path(sys.argv[1]), Path(sys.argv[2])
SHOT = HERE.parents[4] / "Transient/pile_2026-10-22/walk_owner_shots/20261022184400_s.jpg"
try: FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
except Exception: FONT = None
BG = (110, 84, 58, 255)

def pit(P, M=1, N=2):
    W = (N + 2 * M) * P
    src = Image.open(SHOT).convert("RGB").crop((300, 90, 700, 330)); k = 1.9 * P / 128
    src = src.resize((int(400 * k), int(240 * k)), Image.LANCZOS)
    ground = Image.new("RGBA", (W, W))
    for x in range(0, W, src.width):
        for y in range(0, W, src.height): ground.paste(src, (x, y))
    im = ground.copy(); d = ImageDraw.Draw(im)
    x0 = y0 = M * P; x1 = y1 = (M + N) * P
    nf, sw, rl, sl = int(.50 * P), int(.23 * P), max(2, int(.04 * P)), int(.08 * P)
    floor = Image.new("RGBA", (x1 - x0, y1 - y0), (44, 33, 26, 255))
    vig = Image.new("L", floor.size, 0); ImageDraw.Draw(vig).rectangle([P // 7, P // 7, floor.width - P // 7, floor.height - P // 7], fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(max(1, P // 6)))
    floor = Image.composite(floor, Image.new("RGBA", floor.size, (24, 18, 14, 255)), vig); im.alpha_composite(floor, (x0, y0))
    tex = lambda box, k: ground.crop(box).point(lambda v: min(255, int(v * k)))
    face = tex((x0, y0, x1, y0 + nf), 1.0).convert("RGBA"); grad = Image.new("RGBA", face.size); gd = ImageDraw.Draw(grad)
    for yy in range(face.height):
        t = yy / max(1, face.height); gd.line([(0, yy), (face.width, yy)], fill=(255, 236, 200, int(70 * (1 - t))) if t < .5 else (0, 0, 0, int(150 * (t - .5) * 2)))
    face = Image.alpha_composite(face, grad)
    im.alpha_composite(tex((x0, y0, x0 + sw, y1), 0.62).convert("RGBA"), (x0, y0)); im.alpha_composite(tex((x1 - sw, y0, x1, y1), 1.18).convert("RGBA"), (x1 - sw, y0))
    mask = Image.new("L", (x1 - x0, nf), 255); md = ImageDraw.Draw(mask)
    md.polygon([(0, 0), (sw, nf), (0, nf)], fill=0); md.polygon([(x1 - x0, 0), (x1 - x0 - sw, nf), (x1 - x0, nf)], fill=0)
    im.paste(face, (x0, y0), mask)
    blk = (6, 5, 4, 255)
    d.rectangle([x0 - rl, y0 - rl, x1 + rl, y0], fill=blk); d.rectangle([x0 - rl, y0, x0, y1], fill=blk); d.rectangle([x1, y0, x1 + rl, y1], fill=blk)
    lining = lambda dd: dd.rectangle([x0 - rl, y1 - sl // 2, x1 + rl, y1 + sl // 2], fill=blk)
    lining(d)
    return im, (x0, y0, x1, y1), lining

def load(n): return Image.open(opt / f"optA8_{n}.png").convert("RGBA")

def place(im, art, P, cx, cy, size=1.5):
    n = round(P * size); a = art.resize((n, n), Image.LANCZOS); im.alpha_composite(a, (round(cx - n / 2), round(cy - n / 2)))

def scene(P, arts=None, human=False, which=("north", "west", "east", "south")):
    arts = arts or {k: load(k) for k in which}
    im, (x0, y0, x1, y1), lining = pit(P)
    spots = {"north": (x0 + P, y0 + P / 2 - P / 4), "west": (x0 + P / 2, y0 + 1.5 * P - P / 4),
             "east": (x1 - P / 2, y0 + 1.5 * P - P / 4), "south": (x0 + P, y1 - P / 2 + P / 4)}
    for k in which:
        if k in arts and arts[k] is not None: place(im, arts[k], P, *spots[k], size=arts.get("_size", 1.5))
    lining(ImageDraw.Draw(im))     # the near lip hides the south ladder's foot
    if human:
        def tint(t, c=(224, 172, 132)):
            r, g, b, a = t.split(); return Image.merge("RGBA", (*[x.point(lambda v, k=k: v * k // 255) for x, k in zip((r, g, b), c)], a))
        body = tint(Image.open(HUM / "Naked_Male_south.png").convert("RGBA")); head = tint(Image.open(HUM / "Male_Average_Normal_south.png").convert("RGBA"))
        n = P; cx, cy = x0 + P, y0 + int(1.1 * P)
        im.alpha_composite(body.resize((n, n), Image.LANCZOS), (cx - n // 2, cy - n // 2)); im.alpha_composite(head.resize((n, n), Image.LANCZOS), (cx - n // 2, cy - n // 2 - int(.30 * P)))
    return im

def cap(im, t, w=1560):
    c = Image.new("RGBA", (im.width, im.height + 28), (34, 30, 26, 255)); ImageDraw.Draw(c).text((6, 4), t, fill=(240, 230, 210), font=FONT); c.alpha_composite(im, (0, 28))
    return c.resize((w, round(c.height * w / c.width)), Image.LANCZOS) if c.width > w else c

# 1 full res
c = Image.new("RGBA", (384 * 3, 384 + 30), BG); ImageDraw.Draw(c).text((8, 4), "A8 full-res: north | south | west (384 px)", fill=(240, 230, 210), font=FONT)
for i, n in enumerate(["north", "south", "west"]): c.alpha_composite(load(n), (i * 384, 30))
c.save(out / "optA8_1_full.png")
# 2 true scale: 2x2 pit, 128 px/cell, all four mounts plus vanilla human; shown at 2x for the phone
cap(scene(128, human=True).resize((1024, 1024), Image.LANCZOS), "A8 true scale (shown 2x of 128 px/cell), vanilla human, all four mounts", 1024).save(out / "optA8_2_truescale.png")
# 3 facings
c = Image.new("RGBA", (384 * 4, 384 + 30), BG); ImageDraw.Draw(c).text((8, 4), "A8 facings: north | south | west | east", fill=(240, 230, 210), font=FONT)
for i, n in enumerate(["north", "south", "west", "east"]): c.alpha_composite(load(n), (i * 384, 30))
c.resize((1536, round(c.height * 1536 / c.width)), Image.LANCZOS).save(out / "optA8_3_facings.png")
# 4 compare 64/32: west mount in the same pit; current portable (Flat, drawSize 1), fixed RM_Ladder, A7, A8
cur = Image.open(TEX / "RM_LadderPortableFlat.png").convert("RGBA"); fx = Image.open(TEX / "RM_Ladder_west.png").convert("RGBA")
a7 = Image.open(opt / "optA7_west.png").convert("RGBA")
for P in (64, 32):
    cols = []
    for name, art, size in [("current portable", cur, 1.0), ("fixed RM_Ladder", fx, 1.5), ("A7 west", a7, 1.5), ("A8 west", load("west"), 1.5)]:
        cols.append((name, scene(P, {"west": art, "_size": size}, which=("west",))))
    w = sum(i.width for _, i in cols) + 10 * len(cols); h = cols[0][1].height + 28
    c = Image.new("RGBA", (w, h), (34, 30, 26, 255)); x = 0
    for n, i in cols:
        ImageDraw.Draw(c).text((x + 6, 4), n, fill=(240, 230, 210), font=FONT); c.alpha_composite(i, (x, 28)); x += i.width + 10
    c.save(out / f"compare_{P}ppc_west_A8.png")
