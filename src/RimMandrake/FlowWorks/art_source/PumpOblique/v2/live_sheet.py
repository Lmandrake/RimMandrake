"""live_sheet.py <raw capture dir> <out.png>: the owner's picture from pump_look_live.py's captures, one row per look."""
import os, sys
from PIL import Image, ImageDraw, ImageFont
RAW, OUT = sys.argv[1:3]
font = lambda s: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", s)
LOOKS = ("Scrapper", "Industrial", "Modern", "Futuristic")
P = 94                          # captured px per cell


def close(look, state):
    return Image.open(os.path.join(RAW, "pump_%s_%s_close.png" % (look, state))).convert("RGB")


def at(im, dx, dy, w, h, W, H):
    x, y = im.width / 2 + dx * P, im.height / 2 - dy * P
    return im.crop((int(x - w * P / 2), int(y - h * P / 2), int(x + w * P / 2), int(y + h * P / 2))).resize((W, H), Image.LANCZOS)


cols = (("no pipe", 40, 470), ("pipe on every side, with its tank", 540, 1070), ("south arm, no pipe", 1640, 420), ("south arm, piped", 2090, 420))
RH, TOP = 500, 150
im = Image.new("RGB", (2550, TOP + 4 * RH), (236, 228, 214)); d = ImageDraw.Draw(im)
d.text((40, 20), "Liquid pump, in the game (94 px per cell, enlarged). South pipe covers the cap; the rim stays.", (40, 24, 12), font(38))
for t, x, w in cols:
    d.text((x, 90), t, (40, 24, 12), font(32))
for k, l in enumerate(LOOKS):
    y = TOP + k * RH
    a, p = close(l, "alone"), close(l, "piped")
    im.paste(at(a, 0, 0, 1.6, 1.4, 470, 411), (40, y + 40))
    im.paste(at(p, 2.0, 0, 5.6, 2.15, 1070, 411), (540, y + 40))
    im.paste(at(a, 0, -0.42, .62, .60, 420, 411), (1640, y + 40))
    im.paste(at(p, 0, -0.42, .62, .60, 420, 411), (2090, y + 40))
    d.text((40, y + 2), l, (110, 52, 14), font(32))
im.save(OUT)
