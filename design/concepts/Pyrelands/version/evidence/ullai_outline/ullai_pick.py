"""Builds PICK_ullai_outline.png: herd on real ember grass at default zoom (32 px/cell) for today + options A/B/C,
and one animal close with a true-scale colonist (1.5 cells tall). Usage: ullai_pick.py <evidence_dir> <grass_capture> <out.png>"""
import sys, os
from PIL import Image, ImageDraw, ImageFont
ev, cap, out = sys.argv[1:4]
SRC = os.path.join(ev, '..', '..', '..', '..', '..', '..', 'src/RimMandrake/Pyrelands/Textures/Things/Pawn/Animal/Pyrelands/Ullai')
HUM = os.path.join(ev, '..', '..', '..', '..', '..', 'Jawa/worldbuilding/review/assets/human_anchor_south.png')
PX = 32
def tex(opt, f):
    d = SRC if opt == 'today' else os.path.join(ev, opt)
    return Image.open(os.path.join(d, 'Ullai_%s.png' % f)).convert('RGBA')
def get(opt, f):
    if f == 'west': return tex(opt, 'east').transpose(Image.FLIP_LEFT_RIGHT)
    return tex(opt, f)
def draw(canvas, opt, f, size, cx, by, zoom=1):
    im = get(opt, f); n = int(round(size * PX * zoom))
    im = im.resize((n, n), Image.LANCZOS)
    canvas.alpha_composite(im, (int(cx - n / 2), int(by - n * 0.85)))
cap_im = Image.open(cap).convert('RGBA')
GW, GH = 400, 250
grass = cap_im.crop((1536, 900, 1536 + GW, 900 + GH))     # real ember grass, no labels/creatures
# herd: (facing, drawSize, x, base y)
HERD = [('east', 2.0, 70, 120), ('west', 2.0, 190, 100), ('south', 1.6, 300, 140), ('north', 2.0, 130, 205), ('east', 1.1, 250, 215), ('south', 1.1, 345, 200)]
BG = (50, 33, 24, 255)
OPTS = [('today', 'in game today'), ('A', 'A thin outline'), ('B', 'B medium outline'), ('C', 'C heavy outline')]
try: font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 18)
except Exception: font = ImageFont.load_default()
pad = 16; lab = 30
panels = []
for o, name in OPTS:
    p = grass.copy()
    for f, s, x, y in sorted(HERD, key=lambda h: h[3]): draw(p, o, f, s, x, y)
    panels.append(p)
# close: 3x zoom of one adult beside colonist at same scale
Z = 3
CW, CH = GW, 250 + 50
closes = []
hum = Image.open(HUM).convert('RGBA')
hh = int(1.5 * PX * Z); hum = hum.resize((int(hum.width * hh / hum.height), hh), Image.LANCZOS)
for o, name in OPTS:
    c = Image.new('RGBA', (GW, 480), BG)
    gcap = cap_im.crop((1700, 900, 1700 + GW, 900 + 480)).resize((GW, 480))
    c = cap_im.crop((1536, 880, 1536 + GW // Z, 880 + 480 // Z)).resize((GW, 480), Image.LANCZOS)
    n = int(2.0 * PX * Z); im = get(o, 'east').resize((n, n), Image.LANCZOS)
    c.alpha_composite(im, (40, 440 - int(n * 0.97)))
    c.alpha_composite(hum, (40 + n - 20, 440 - hh))
    closes.append(c)
W = pad + 2 * (GW + pad)
H = pad + 2 * (lab + GH + pad) + (lab + 480 + pad) * 1
# 2x2 herds on top, then 4 closes? keep it light: one close row of 4 is wide; use second block 2x2 of closes
H = pad + 2 * (lab + GH + pad) + 2 * (lab + 480 + pad)
sheet = Image.new('RGBA', (W, H), BG); d = ImageDraw.Draw(sheet)
y = pad
for blk, items in ((0, panels), (1, closes)):
    h = GH if blk == 0 else 480
    for r in range(2):
        for c in range(2):
            i = r * 2 + c; x = pad + c * (GW + pad)
            d.text((x, y + r * (lab + h + pad)), OPTS[i][1], fill=(240, 220, 190, 255), font=font)
            sheet.alpha_composite(items[i], (x, y + r * (lab + h + pad) + lab))
    y += 2 * (lab + h + pad)
sheet.convert('RGB').save(out)
print(out, sheet.size)
