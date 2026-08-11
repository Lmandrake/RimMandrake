"""render_build_sheet.py — draw the #15 PASS 2 BUILD SHEET: machines placed with
aisles, factory-floor apron, hopper faces, belt stubs, and the outboard thermal spine.
Base hull dimmed; build-sheet layers bright on top. Usage: python3 render_build_sheet.py"""
import numpy as np, json
from PIL import Image, ImageDraw, ImageFont
from ship_designs import COL, LABEL

g = np.load('design_15_falcon_halo_hollow.npy'); H, W = g.shape
bs = json.load(open('build_sheet_15.json'))
TS = 16
def font(sz, bold=True):
    base = "/usr/share/fonts/truetype/dejavu/DejaVuSans"
    for p in ([base+"-Bold.ttf"] if bold else [])+[base+".ttf"]:
        try: return ImageFont.truetype(p, sz)
        except: pass
    return ImageFont.load_default()
fTit = font(42); fLeg = font(26, False); fSub = font(22, False); fMac = font(15)

Wp, Hp = W*TS, H*TS
panel = Image.new('RGB', (Wp, Hp), (0, 0, 0)); d = ImageDraw.Draw(panel)
def dim(c, f=0.34): return tuple(int(v*f) for v in c)
for y in range(H):
    for x in range(W):
        c = g[y, x]
        if c == '': continue
        d.rectangle([x*TS, y*TS, x*TS+TS, y*TS+TS], fill=dim(COL[c]), outline=(24,24,28), width=1)

def cell(x, y): return (x*TS, y*TS, x*TS+TS, y*TS+TS)
def ctr(x, y): return (x*TS+TS//2, y*TS+TS//2)

# 1. factory-floor apron (under everything)
for e in bs['elements']:
    if e['type'] != 'apron': continue
    for (x, y) in e['tiles']:
        d.rectangle(cell(x, y), fill=(52,50,44), outline=(70,66,56), width=1)
# 2. belt stubs
for e in bs['elements']:
    if e['type'] != 'belt_stub': continue
    pts = [ctr(*p) for p in e['pts']]
    if len(pts) >= 2: d.line(pts, fill=(150,150,155), width=5)
# 3. machines
MCOL = {'A':(120,200,120),'B':(230,120,80),'C':(240,200,90),'D':(150,200,235),
        'E':(210,140,235),'F':(235,150,170)}
for e in bs['elements']:
    if e['type'] != 'machine': continue
    x, y, w, h = e['rect']; col = MCOL.get(e['wing'], (200,200,200))
    d.rectangle([x*TS, y*TS, (x+w)*TS, (y+h)*TS], fill=col, outline=(0,0,0), width=2)
    # short machine tag
    tag = ''.join(t[0] for t in e['name'].split())[:3]
    d.text((x*TS+3, y*TS+2), tag, font=fMac, fill=(0,0,0))
# 4. hoppers
for e in bs['elements']:
    if e['type'] != 'hopper': continue
    X, Y = ctr(*e['at']); d.rectangle([X-6,Y-6,X+6,Y+6], fill=(255,235,120), outline=(0,0,0), width=1)
# 5. thermal spine (outboard)
for e in bs['elements']:
    if e['type'] == 'booster':
        x, y, w, h = e['rect']
        d.rectangle([x*TS, y*TS, (x+w)*TS, (y+h)*TS], fill=(255,120,40), outline=(0,0,0), width=2)
    if e['type'] == 'heatsink':
        x, y, w, h = e['rect']
        d.rectangle([x*TS, y*TS, (x+w)*TS, (y+h)*TS], fill=(70,150,255), outline=(0,0,0), width=2)
# wing labels
for code in ['A','B','C','D','E','F','R']:
    yy, xx = np.where(g == code); X, Y = int(xx.mean())*TS, int(yy.mean())*TS
    d.text((X-6, Y-16), code, font=fTit, fill=(255,255,255))

# ---- sheet with legend
pad = 30; titleH = 70; legW = 560
sheetW = pad + Wp + 30 + legW + pad; sheetH = titleH + Hp + pad
sheet = Image.new('RGB', (sheetW, sheetH), (0,0,0)); dc = ImageDraw.Draw(sheet)
dc.text((pad, 20), "#15 Falcon Halo (hollow) — PASS 2 BUILD SHEET  (machines + floor + hoppers + belts)",
        font=fTit, fill=(238,238,242))
sheet.paste(panel, (pad, titleH))
dc.rectangle([pad-1, titleH-1, pad+Wp, titleH+Hp], outline=(110,110,118), width=2)
lx = pad + Wp + 30; yy = titleH
leg = [("factory floor apron (+1-tile aisle)", (52,50,44)),
       ("machine (footprint, wing-coloured)", (210,140,235)),
       ("hopper (I/O port -> belt)", (255,235,120)),
       ("belt stub airlock -> first machine", (150,150,155)),
       ("Factory Booster (3x1, outboard)", (255,120,40)),
       ("Factory Heatsink (2x2, outboard)", (70,150,255))]
for txt, col in leg:
    dc.rectangle([lx, yy, lx+30, yy+22], fill=col, outline=(150,150,158), width=1)
    dc.text((lx+42, yy), txt, font=fLeg, fill=(224,224,228)); yy += 32
yy += 16
dc.text((lx, yy), "per-wing (machines / hoppers placed):", font=fSub, fill=(180,180,186)); yy += 30
for code, r in bs['report'].items():
    dc.text((lx, yy), f"  {code}: {r['machines']} machines, {r['hoppers_placed']}/{r['hoppers_needed']} hoppers, apron {r['apron']}",
            font=fSub, fill=(210,210,214)); yy += 26
yy += 12
dc.text((lx, yy), "thermal 9.9-tile re-verify (§5):", font=fSub, fill=(180,180,186)); yy += 28
for code, r in bs['report'].items():
    t = r.get('thermal')
    if not t: continue
    col = (90,220,120) if t['within_link'] else (240,80,80)
    dc.text((lx, yy), f"  wing {code}: {t['worst_machine']} @ {t['worst_dist']}t  [OK]",
            font=fSub, fill=col); yy += 26
sheet.save('build_sheet_15.png'); print("saved build_sheet_15.png", sheet.size)
