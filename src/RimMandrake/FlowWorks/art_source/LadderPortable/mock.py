"""Phone collection for the portable-ladder options: full-res, true-scale pit beside a vanilla human, facings, compare.
   python3 mock.py OPTDIR OUTDIR     (OPTDIR from gen.py)"""
import sys, random
from pathlib import Path
from PIL import Image, ImageDraw
TEX = Path(__file__).resolve().parents[2] / "Textures" / "Things" / "Building" / "FlowWorks"
HUM = Path("/mnt/d/ClaudeWork/rimmandrake/build/doortex")
GROUND, FLOOR = (150, 122, 88), (52, 44, 36)


def noisy(w, h, rgb, seed):
    r = random.Random(seed); im = Image.new("RGBA", (w, h), rgb + (255,)); px = im.load()
    for y in range(h):
        for x in range(w):
            k = r.randint(-6, 6); px[x, y] = tuple(max(0, min(255, v + k)) for v in rgb) + (255,)
    return im


def human(c):
    b = Image.open(HUM / "Naked_Male_south.png").convert("RGBA"); h = Image.open(HUM / "Male_Average_Normal_south.png").convert("RGBA")
    from PIL import ImageChops
    tint = lambda im: Image.merge("RGBA", (*[ImageChops.multiply(ch, Image.new("L", im.size, v)) for ch, v in zip(im.split()[:3], (222, 170, 132))], im.getchannel("A")))
    b = tint(b); h = tint(h)
    b.alpha_composite(h, (0, -22))
    k = 1.5 * c / 128
    return b.resize((int(128 * k), int(128 * k)), Image.LANCZOS)


def pit(opt, c, mount, art, with_human=True):
    """pit interior 4x3 cells, one ring of ground; ladder on the mount wall."""
    W, H = 6, 5
    im = noisy(W * c, H * c, GROUND, 1)
    im.alpha_composite(noisy(4 * c, 3 * c, FLOOR, 2), (c, c))
    wall = Image.open(TEX / "Excavation" / "RM_WallFace_North.png").convert("RGBA").resize((c, c // 2), Image.BOX)
    for x in range(1, 5):
        im.alpha_composite(wall, (x * c, c))
    d = ImageDraw.Draw(im)
    d.rectangle([c, c, 5 * c - 1, 4 * c - 1], outline=(30, 26, 22, 255), width=max(2, c // 24))
    d.rectangle([c, 4 * c - c // 10, 5 * c - 1, 4 * c - 1], fill=(28, 24, 20, 255))
    cell = {"north": (2, 1), "west": (1, 2)}[mount]
    s = art.resize((int(art.width * c / 256), int(art.height * c / 256)), Image.LANCZOS)  # 384 canvas = 1.5 cells = 256 px/cell
    cx, cy = (cell[0] + .5) * c, (cell[1] + .5) * c - .25 * c
    im.alpha_composite(s, (int(cx - s.width / 2), int(cy - s.height / 2)))
    if with_human:
        hm = human(c); hx, hy = (3 if mount == "north" else 3, 3 if mount == "north" else 2)
        im.alpha_composite(hm, (int((hx + .5) * c - hm.width / 2), int((hy + .5) * c - hm.height / 2 - .15 * c)))
    return im


def label(im, text):
    out = Image.new("RGBA", (im.width, im.height + 22), (36, 32, 28, 255)); out.alpha_composite(im, (0, 22))
    ImageDraw.Draw(out).text((8, 5), text, fill=(235, 225, 210, 255)); return out


def hstack(ims, pad=12, bg=(36, 32, 28, 255)):
    w = sum(i.width for i in ims) + pad * (len(ims) + 1); h = max(i.height for i in ims) + 2 * pad
    o = Image.new("RGBA", (w, h), bg); x = pad
    for i in ims:
        o.alpha_composite(i, (x, pad)); x += i.width + pad
    return o


def on_brown(im):
    b = Image.new("RGBA", im.size, (110, 84, 56, 255)); b.alpha_composite(im); return b


if __name__ == "__main__":
    src, out = Path(sys.argv[1]), Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
    cur = Image.open(TEX / "Canals" / "RM_LadderPortable.png").convert("RGBA")
    for k in "ABC":
        f = {n: Image.open(src / f"opt{k}_{n}.png").convert("RGBA") for n in ("north", "south", "west", "east")}
        hstack([label(on_brown(f["north"]), f"option {k} north (far wall), 384 px = 1.5 cells"), label(on_brown(f["west"]), f"option {k} west (west wall)")]).convert("RGB").save(out / f"opt{k}_1_full.png")
        hstack([label(on_brown(f[n]), n) for n in ("north", "south", "west", "east")], pad=6).convert("RGB").save(out / f"opt{k}_3_facings.png")
        a = label(pit(k, 128, "west", f["west"]), f"option {k}: west mount, 128 px/cell, vanilla human 1.5 cells")
        b = label(pit(k, 128, "north", f["north"]), "north mount")
        hstack([a, b], pad=8).convert("RGB").save(out / f"opt{k}_2_truescale.png")
    # compare at 64 px/cell: current (Graphic_Single 1x1, 256 px, rotated for west) vs options; plus 32 px/cell play zoom
    cw = cur.rotate(90, expand=True); cw = Image.new("RGBA", (384, 384)); cw.alpha_composite(cur.rotate(90), (64, 64))
    row = [label(pit("cur", 64, "west", cw, False), "current")]
    for k in "ABC":
        row.append(label(pit(k, 64, "west", Image.open(src / f"opt{k}_west.png").convert("RGBA"), False), f"option {k}"))
    hstack(row, pad=6).convert("RGB").save(out / "compare_64ppc_west.png")
    row = [label(pit("cur", 32, "west", cw, False), "current")]
    for k in "ABC":
        row.append(label(pit(k, 32, "west", Image.open(src / f"opt{k}_west.png").convert("RGBA"), False), f"option {k}"))
    hstack(row, pad=6).convert("RGB").save(out / "compare_32ppc_west.png")
