import re, glob, os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT = Path('/home/mandrake/rm/bench')
item = (ROOT / 'infrastructure/state/items/TINT_ON_COLOUR_ART_1.md').read_text()
rows = re.findall(r'^\| (R[MSU]\w*_\w+) \| (\w+) \| `\(([\d ,]+)\)` \| ([^|]+)\| [^|]+\| ([\d.]+) \| `([^`]+)` \|', item, re.M)
print(len(rows), 'rows parsed')
def texpath(defname, xmlfile):
    t = open(ROOT / xmlfile, encoding='utf-8', errors='replace').read()
    i = t.find('<defName>%s</defName>' % defname)
    if i < 0:
        return None
    m = re.search(r'<texPath>([^<]+)</texPath>', t[i:i + 8000])
    return m.group(1).strip() if m else None
def find_png(mod_root, tp):
    for root in [mod_root] + sorted(Path(x).parent for x in glob.glob(str(ROOT / 'src/*/*/Textures'))):
        hit = _find(root, tp)
        if hit:
            return hit
def _find(mod_root, tp):
    for suf in ('_south.png', '.png', '_east.png', 'A.png', '_a.png'):
        hits = glob.glob(str(mod_root / 'Textures' / (tp + suf)))
        if hits:
            return hits[0]
    hits = glob.glob(str(mod_root / 'Textures' / tp / '*.png'))
    hits = [h for h in hits if not h.endswith('m.png')]
    return sorted(hits)[0] if hits else None
S = 160
font = ImageFont.load_default()
cells, missing = [], []
for d, kind, col, shader, sat, xml in rows:
    mod_root = ROOT / Path(xml).parts[0] / Path(xml).parts[1] / Path(xml).parts[2]
    tp = texpath(d, xml)
    png = find_png(mod_root, tp) if tp else None
    if not png:
        missing.append(d); continue
    im = Image.open(png).convert('RGBA'); im.thumbnail((S, S))
    c = [int(x) for x in col.split(',')][:3]
    r, g, b, a = im.split()
    tinted = Image.merge('RGBA', (r.point(lambda v, k=c[0]: v * k // 255), g.point(lambda v, k=c[1]: v * k // 255),
                                  b.point(lambda v, k=c[2]: v * k // 255), a))
    cells.append((d, kind, col, im, tinted))
W, H = 2 * S + 30, S + 34
cols = 4
sheet = Image.new('RGB', (cols * W, ((len(cells) + cols - 1) // cols) * H), (58, 44, 32))
dr = ImageDraw.Draw(sheet)
for i, (d, kind, col, im, tinted) in enumerate(cells):
    x, y = (i % cols) * W + 10, (i // cols) * H + 4
    bg = Image.new('RGBA', (S, S), (120, 104, 84, 255))
    for j, img in enumerate((im, tinted)):
        tile = bg.copy(); tile.alpha_composite(img, ((S - img.width) // 2, (S - img.height) // 2))
        sheet.paste(tile.convert('RGB'), (x + j * (S + 8), y))
    dr.text((x, y + S + 4), '%d. %s  (%s)  painted | in game x(%s)' % (i + 1, d, kind, col.replace(' ', '')), fill=(240, 226, 200), font=font)
out = ROOT / 'Transient/tint_review_2026-10-06/tint_before_after.png'
sheet.save(out)
print('cells', len(cells), 'missing', missing, out)
