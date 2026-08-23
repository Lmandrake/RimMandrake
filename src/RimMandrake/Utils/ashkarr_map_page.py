#!/usr/bin/env python3
"""ashkarr_map_page.py — one self-contained page showing the planet AS THE CSV HAS IT NOW.

🔑 **Why a page and not a render.** `worldview.py` portrays a SAVEGAME. The planet we are
authoring lives in `world/ASHKARR_WORLDMAP_tiles.csv`, and the only route from one to the
other regenerates and regresses the CSV. So the authored map had no picture. This makes one,
straight from the CSV, every time it is run — five views and a legend that counts tiles.

⛔ Read-only. It writes an HTML file and nothing else.

    python3 src/RimMandrake/Utils/ashkarr_map_page.py
    python3 src/RimMandrake/Utils/ashkarr_map_page.py --out world/view/ASHKARR_MAP.html
"""
from __future__ import annotations
import argparse, base64, collections, csv, io, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import worldview  # noqa: E402

TILES = os.path.join(ROOT, 'world', 'ASHKARR_WORLDMAP_tiles.csv')
OUT = os.path.join(ROOT, 'world', 'view', 'ASHKARR_MAP.html')

VIEWS = [
    ('Substellar — the day face', 0.0, 0.0,
     'The point the star is fixed above. Arc 0. Everything here is noon, forever.'),
    ('Terminator west — the Twilight Sea', 17.7, -91.0,
     'The bigger of the two seas, its drained floor, and the ice margin.'),
    ('Terminator east — the Grey Sea', 7.7, 89.5,
     'The salt-encrusted shrinking sea and its own drained shelf.'),
    ('Antistellar — the night face', 0.0, 180.0,
     'Arc 180. The Crags, the mycoid belt, the horror pockets and the ancient ice.'),
]


def colour(b: str) -> str:
    c = worldview.BIOME_COLOR.get(b)
    if c is None:
        return '#ff00ff'
    return c if isinstance(c, str) else '#%02x%02x%02x' % tuple(c[:3])


def png_b64(draw_fn, w: int, h: int) -> str:
    from PIL import Image, ImageDraw
    im = Image.new('RGB', (w, h), '#0a0c10')
    draw_fn(ImageDraw.Draw(im))
    buf = io.BytesIO()
    im.save(buf, format='PNG')
    return base64.b64encode(buf.getvalue()).decode('ascii')


def ortho(rows, clat_d, clon_d, W=760):
    clat, clon = math.radians(clat_d), math.radians(clon_d)
    R = W / 2 - 6

    def draw(dr):
        dr.ellipse([W / 2 - R, W / 2 - R, W / 2 + R, W / 2 + R], fill='#05070a')
        r = max(1.0, R * 0.0125)
        for t in rows:
            la, lo = math.radians(float(t['lat'])), math.radians(float(t['lon']))
            if (math.sin(clat) * math.sin(la)
                    + math.cos(clat) * math.cos(la) * math.cos(lo - clon)) <= 0:
                continue
            x = W / 2 + R * math.cos(la) * math.sin(lo - clon)
            y = W / 2 - R * (math.cos(clat) * math.sin(la)
                             - math.sin(clat) * math.cos(la) * math.cos(lo - clon))
            dr.ellipse([x - r, y - r, x + r, y + r], fill=colour(t['biome']))
    return png_b64(draw, W, W)


def equirect(rows, W=1560):
    H = W // 2

    def draw(dr):
        r = max(1.0, W * 0.0034)
        for t in rows:
            x = (float(t['lon']) + 180.0) / 360.0 * W
            y = (90.0 - float(t['lat'])) / 180.0 * H
            dr.ellipse([x - r, y - r, x + r, y + r], fill=colour(t['biome']))
    return png_b64(draw, W, H)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--csv', default=TILES)
    ap.add_argument('--out', default=OUT)
    a = ap.parse_args()

    rows = list(csv.DictReader(open(a.csv, encoding='utf-8')))
    counts = collections.Counter(r['biome'] for r in rows)
    regions = collections.Counter(r['region'] for r in rows)
    stamp = os.path.getmtime(a.csv)
    import datetime
    when = datetime.datetime.fromtimestamp(stamp).strftime('%Y-%m-%d %H:%M')

    unknown = sorted(b for b in counts if b not in worldview.BIOME_COLOR)

    cards = []
    for title, la, lo, blurb in VIEWS:
        cards.append(f'''<figure><img src="data:image/png;base64,{ortho(rows, la, lo)}" alt="{title}">
<figcaption><b>{title}</b><br><span>{blurb}</span><br><code>lat {la} · lon {lo}</code></figcaption></figure>''')

    legend = "".join(
        f'<li><i style="background:{colour(b)}"></i><span>{b}</span>'
        f'<b>{n:,}</b><em>{100.0*n/len(rows):.1f}%</em></li>'
        for b, n in counts.most_common())

    html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Ash'karr — the map as it stands</title>
<style>
*{{box-sizing:border-box}} body{{margin:0;background:#0f1115;color:#d8dbe0;
font:14px/1.5 -apple-system,Segoe UI,Roboto,sans-serif}}
header{{padding:18px 26px;background:#161a20;border-bottom:1px solid #262c36}}
h1{{margin:0 0 4px;font-size:20px;color:#fff}} .sub{{color:#8b929e;font-size:13px}}
main{{padding:22px 26px;display:grid;gap:20px;grid-template-columns:repeat(auto-fit,minmax(360px,1fr))}}
figure{{margin:0;background:#161a20;border:1px solid #262c36;border-radius:10px;padding:12px}}
figure img{{width:100%;height:auto;display:block;border-radius:8px;background:#05070a}}
figcaption{{margin-top:10px;font-size:12.5px;color:#c3c8d0}}
figcaption b{{color:#fff;font-size:14px}} figcaption span{{color:#8b929e}}
figcaption code{{color:#7fa8d0;font-size:11.5px}}
section{{padding:0 26px 40px}} h2{{font-size:15px;color:#fff;margin:26px 0 10px}}
.wide img{{width:100%;border-radius:8px;background:#05070a}}
ul.legend{{list-style:none;margin:0;padding:0;columns:3;column-gap:26px}}
ul.legend li{{display:flex;align-items:center;gap:8px;padding:2px 0;font-size:12.5px;
break-inside:avoid}}
ul.legend i{{width:13px;height:13px;border-radius:3px;flex:none;border:1px solid #0006}}
ul.legend span{{flex:1;color:#c3c8d0}} ul.legend b{{color:#fff}}
ul.legend em{{color:#8b929e;font-style:normal;width:44px;text-align:right}}
.warn{{background:#2a1a1a;border-left:3px solid #d4574e;padding:10px 12px;border-radius:6px;
margin:12px 0;color:#e0b3ae}}
@media (max-width:700px){{ul.legend{{columns:1}}}}
</style></head><body>
<header><h1>Ash'karr — the map as it stands</h1>
<div class="sub">Drawn straight from <code>world/ASHKARR_WORLDMAP_tiles.csv</code>,
last edited <b>{when}</b> · {len(rows):,} tiles · {len(counts)} biomes · {len(regions)} named regions.
Regenerate with <code>python3 src/RimMandrake/Utils/ashkarr_map_page.py</code>.</div></header>
<main>{"".join(cards)}</main>
<section>
<h2>The whole planet, flattened</h2>
<div class="wide"><img src="data:image/png;base64,{equirect(rows)}" alt="equirectangular"></div>
{'<div class="warn">🔴 <b>' + str(len(unknown)) + ' biome(s) have no colour in the palette and are drawn MAGENTA:</b> ' + ", ".join(unknown) + '</div>' if unknown else ''}
<h2>Every biome on the planet</h2>
<ul class="legend">{legend}</ul>
</section></body></html>'''

    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    open(a.out, 'w', encoding='utf-8').write(html)
    print(f"wrote {a.out}  ({len(rows):,} tiles · {len(counts)} biomes · {len(regions)} regions"
          + (f" · 🔴 {len(unknown)} uncoloured: {', '.join(unknown)}" if unknown else "") + ")")
    return 0


if __name__ == '__main__':
    sys.exit(main())
