"""build_mod_previews.py -- Steam preview images (About/Preview.png) for the release-packaged mods.

Composes REAL in-game captures already in the repo with the mod's own shipped textures and a title. Generates no
art and touches no texture the game loads. Re-run to rebuild: python3 src/RimMandrake/Utils/build_mod_previews.py [--only Mod]
Sources are Transient/ captures (~14-day shelf life): if one is gone, the committed Preview.png stays as the record.
"""
import argparse
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SRC = os.path.join(REPO, "src", "RimMandrake")
W, H = 640, 360
FONTS = "/mnt/c/Windows/Fonts"


def font(name, size):
    for n in (name, "arialbd.ttf"):
        p = os.path.join(FONTS, n)
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def crop_fill(path, box, size):
    im = Image.open(os.path.join(REPO, path)).convert("RGB")
    if box:
        im = im.crop(box)
    tw, th = size
    s = max(tw / im.width, th / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    l, t = (im.width - tw) // 2, (im.height - th) // 2
    return im.crop((l, t, l + tw, t + th))


def band(canvas, y0, y1, alpha=170):
    ov = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(ov).rectangle((0, y0, canvas.width, y1), fill=(20, 14, 8, alpha))
    return Image.alpha_composite(canvas.convert("RGBA"), ov)


def title(canvas, tier, name, tag, y):
    d = ImageDraw.Draw(canvas)
    d.text((22, y), tier, font=font("bahnschrift.ttf", 16), fill=(230, 190, 120))
    d.text((20, y + 18), name, font=font("georgiab.ttf", 40), fill=(250, 240, 222))
    d.text((22, y + 66), tag, font=font("bahnschrift.ttf", 17), fill=(225, 214, 196))


def sprite(path, h):
    im = Image.open(os.path.join(SRC, path)).convert("RGBA")
    bb = im.getbbox()
    im = im.crop(bb) if bb else im
    s = h / im.height
    return im.resize((max(1, round(im.width * s)), h), Image.LANCZOS)


def shadowed(canvas, im, xy):
    a = im.split()[3].point(lambda v: 160 if v > 20 else 0)
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sh.putalpha(a)
    sh = sh.filter(ImageFilter.GaussianBlur(4))
    canvas.alpha_composite(sh, (xy[0] + 3, xy[1] + 4))
    canvas.alpha_composite(im, xy)


def gss():
    c = Image.new("RGB", (W, H))
    c.paste(crop_fill("Transient/messy_conduit_live_20261002/mc_01_wide.png", (200, 260, 1300, 740), (W, 230)), (0, 0))
    c.paste(crop_fill("Transient/messy_conduit_live_20261002/style_jawa_aerial.png", (0, 150, 1184, 470), (W, 130)), (0, 230))
    ImageDraw.Draw(c).line((0, 230, W, 230), fill=(20, 14, 8), width=3)
    c = band(c, 0, 100, 160)
    title(c, "RIMMANDRAKE", "Gimme Some Slack", "Messy floor cords  ·  sagging overhead power lines  ·  four looks", 4)
    return c


FW_REELS = ["Hose/Reel_Deployed.png", "Hose/Styles/Industrial/Reel_Deployed.png",
            "Hose/Styles/Modern/Reel_Deployed.png", "Hose/Styles/Futuristic/Reel_Deployed.png"]


def flowworks():
    c = crop_fill("Transient/bench_live_20261011/shots/L1_lake_pump_outflow_canal.png", (760, 300, 1960, 975),
                  (W, H)).convert("RGBA")
    c = band(c, 252, H)
    title(c, "RIMMANDRAKE", "FlowWorks", "Dig canals and pits  ·  liquids that flow  ·  rivers that push", 258)
    x = W - 4 * 74 - 10
    for p in FW_REELS:
        s = sprite(os.path.join("FlowWorks", "Textures", "RimMandrake", "FlowWorks", p), 58)
        shadowed(c, s, (x + (70 - s.width) // 2, 14))
        x += 74
    return c


PYRE_CAST = ["Things/Pawn/Animal/Pyrelands/FurnaceBeast/FurnaceBeast_Giant_south.png",
             "Things/Pawn/Animal/Pyrelands/Ullai/Ullai_south.png",
             "Things/Pawn/Animal/Pyrelands/Emberscythe/Emberscythe_south.png",
             "Things/Pawn/Animal/Pyrelands/Barbslinger/Barbslinger_south.png",
             "Things/Pawn/Animal/Pyrelands/FireHawk/FireHawk_south.png",
             "Things/Pawn/Animal/Pyrelands/Flamefang/Flamefang_south.png"]


def pyrelands():
    c = crop_fill("Transient/pyrefinal_150450_sm.png", (30, 30, 1290, 740), (W, H)).convert("RGBA")
    c = band(c, 0, 108, 150)
    title(c, "RIMMANDRAKE", "Pyrelands", "A savanna that burns on a cycle of its own", 8)
    heights = [118, 78, 72, 70, 58, 62]
    x = 18
    for p, h in zip(PYRE_CAST, heights):
        s = sprite(os.path.join("Pyrelands", "Textures", p), h)
        shadowed(c, s, (x, H - 14 - h))
        x += s.width + 14
    return c


MODS = {"GimmeSomeSlack": gss, "FlowWorks": flowworks, "Pyrelands": pyrelands}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--only")
    ap.add_argument("--out-dir", help="write <Mod>_Preview.png here instead of the mod's About/")
    a = ap.parse_args()
    for mod, fn in MODS.items():
        if a.only and a.only != mod:
            continue
        im = fn().convert("RGB")
        out = (os.path.join(a.out_dir, mod + "_Preview.png") if a.out_dir
               else os.path.join(SRC, mod, "About", "Preview.png"))
        im.save(out, optimize=True)
        print("%s  %dx%d  %d KB" % (out, im.width, im.height, os.path.getsize(out) // 1024))


if __name__ == "__main__":
    sys.exit(main())
