"""render_skeleton.py — draw the #15 hull with the systems/flow skeleton overlaid.
Base hull tiles dimmed; skeleton elements (corridors, doors, switches, thermal
spine, vents, belt trunks) drawn bright on top. Usage: python3 render_skeleton.py"""
import numpy as np, json, math
from PIL import Image, ImageDraw, ImageFont
from ship_designs import COL, LABEL

g = np.load('design_15_falcon_halo_hollow.npy'); H, W = g.shape
sk = json.load(open('skeleton_15.json'))
TS = 16
def font(sz, bold=True):
    base = "/usr/share/fonts/truetype/dejavu/DejaVuSans"
    for p in ([base+"-Bold.ttf"] if bold else [])+[base+".ttf"]:
        try: return ImageFont.truetype(p, sz)
        except: pass
    return ImageFont.load_default()
fTit = font(42); fLeg = font(26, False); fSub = font(22, False)

Wp, Hp = W*TS, H*TS
panel = Image.new('RGB', (Wp, Hp), (0, 0, 0))
d = ImageDraw.Draw(panel)
# base hull, DIMMED (so skeleton pops)
def dim(c, f=0.42):
    return tuple(int(v*f) for v in c)
for y in range(H):
    for x in range(W):
        c = g[y, x]
        if c == '': continue
        d.rectangle([x*TS, y*TS, x*TS+TS, y*TS+TS], fill=dim(COL[c]), outline=(30, 30, 34), width=1)

def cell(x, y): return (x*TS, y*TS, x*TS+TS, y*TS+TS)
def ctr(x, y): return (x*TS+TS//2, y*TS+TS//2)

# belts first (under corridors)
BELTCOL = {1:(120,120,128), 2:(150,110,80), 3:(240,210,90), 4:(150,220,180),
           5:(200,170,235), 6:(150,150,155), 7:(210,90,190)}
for e in sk['elements']:
    if e['type'] != 'belt': continue
    col = BELTCOL.get(e['cls'], (200,200,200))
    pts = [ctr(*p) for p in e['pts']]
    if len(pts) >= 2:
        d.line(pts, fill=col, width=5)
# corridors
for e in sk['elements']:
    if e['type'] != 'corridor': continue
    pts = [ctr(*p) for p in e['pts']]
    col = (235,235,240) if e['role']=='ring_spine' else (200,200,255)
    if len(pts) >= 2: d.line(pts, fill=col, width=3)
# thermal spine
for e in sk['elements']:
    if e['type'] == 'booster':
        x, y, w, h = e['rect']
        d.rectangle([x*TS, y*TS, (x+w)*TS, (y+h)*TS], fill=(255,120,40), outline=(0,0,0), width=2)
    if e['type'] == 'heatsink':
        x, y, w, h = e['rect']
        d.rectangle([x*TS, y*TS, (x+w)*TS, (y+h)*TS], fill=(70,150,255), outline=(0,0,0), width=2)
    if e['type'] == 'vent':
        X, Y = ctr(*e['at']); d.polygon([(X,Y-8),(X-8,Y+7),(X+8,Y+7)], fill=(255,60,60), outline=(0,0,0))
# doors + switches
for e in sk['elements']:
    if e['type'] == 'door':
        X, Y = ctr(*e['at']); d.rectangle([X-7,Y-7,X+7,Y+7], fill=(255,235,60), outline=(0,0,0), width=2)
    if e['type'] == 'switch':
        X, Y = ctr(*e['at']); d.ellipse([X-6,Y-6,X+6,Y+6], fill=(60,230,120), outline=(0,0,0), width=2)

# wing labels
for code in ['A','B','C','D','E','F','R']:
    yy, xx = np.where(g == code); X, Y = int(xx.mean())*TS, int(yy.mean())*TS
    d.text((X-6, Y-14), code, font=fTit, fill=(255,255,255))

# ---- sheet with legend
pad = 30; titleH = 70; legW = 560
sheetW = pad + Wp + 30 + legW + pad; sheetH = titleH + Hp + pad
sheet = Image.new('RGB', (sheetW, sheetH), (0,0,0)); dc = ImageDraw.Draw(sheet)
dc.text((pad, 20), "#15 Falcon Halo (hollow) — systems / flow SKELETON  (machines = later pass)",
        font=fTit, fill=(238,238,242))
sheet.paste(panel, (pad, titleH))
dc.rectangle([pad-1, titleH-1, pad+Wp, titleH+Hp], outline=(110,110,118), width=2)
lx = pad + Wp + 30; yy = titleH
leg = [("ring maintenance corridor (keel spine)", (235,235,240)),
       ("rear causeway -> hollow core", (200,200,255)),
       ("pod airlock / isolation door", (255,235,60)),
       ("cell power switch", (60,230,120)),
       ("Factory Booster (3x1)", (255,120,40)),
       ("Factory Heatsink (2x2)", (70,150,255)),
       ("hot-wing heat vent", (255,60,60)),
       ("belt 1 raw minerals+chunks", BELTCOL[1]),
       ("belt 2 organic+corpses", BELTCOL[2]),
       ("belt 3 food ingredients", BELTCOL[3]),
       ("belt 4 textile crops", BELTCOL[4]),
       ("belt 5 components+adv-mat", BELTCOL[5]),
       ("belt 6 finished goods -> cargo", BELTCOL[6]),
       ("belt 7 chemfuel", BELTCOL[7])]
for txt, col in leg:
    dc.rectangle([lx, yy, lx+30, yy+22], fill=col, outline=(150,150,158), width=1)
    dc.text((lx+42, yy), txt, font=fLeg, fill=(224,224,228)); yy += 32
yy += 16
th = sk['thermal']
dc.text((lx, yy), "9.9-tile link check (Factory_lore §5):", font=fSub, fill=(180,180,186)); yy += 30
for code, r in th.items():
    ok = "OK" if r['within_link'] else "EXCEEDS"
    col = (90,220,120) if r['within_link'] else (240,80,80)
    dc.text((lx, yy), f"  wing {code}: {r['worst_machine']} @ {r['worst_dist']}t  [{ok}]",
            font=fSub, fill=col); yy += 28
yy += 10
dc.text((lx, yy), "7 filtered belt classes per Factory_lore §1.1;", font=fSub, fill=(170,164,150)); yy += 26
dc.text((lx, yy), "hot wings B,E vent outboard to the rim.", font=fSub, fill=(170,164,150))
sheet.save('skeleton_15.png'); print("saved skeleton_15.png", sheet.size)
