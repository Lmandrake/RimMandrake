#!/usr/bin/env python3
"""ashkarr_csv_view.py — LOOK at the authored CSV without going through a savegame.

⚠️ **READ THIS BEFORE REACHING FOR IT — it is NOT the map viewer.**

🔴 **`worldview.py` already renders the CSV bundle and this file's first docstring said it
could not.** That was wrong: its `save` argument takes *"a .rws savegame, **or a bundle stem
like world/ashkarr**"*, and `class BundlePlanet` reads `<stem>_tiles.csv` directly. The real
map — hexes, region labels, settlements, rivers, roads, the terminator circle, the biome
legend with percentages and the faction roster — comes from:

    python3 src/RimMandrake/Utils/worldview.py world/ASHKARR_WORLDMAP \
        --layer biome --projection equirect --png --out world/view/ASHKARR_current

**Use that for looking at the planet. Always.**

✅ **What this file is still for:** a fast A/B of ONE edit. It draws a bare dot map in a
second or two from any CSV you point it at, including a backup copy, so a before/after pair
of the same view can be put side by side while iterating. `worldview.py` takes minutes and
7 MB per render, which is the right price for the real map and the wrong one for a diff.

It borrows `worldview.BIOME_COLOR` so the colours match the renders already in
`world/view/` and nothing has to be re-learned.

⛔ Read-only. It never writes the map, only an SVG beside it.

    python3 src/RimMandrake/Utils/ashkarr_csv_view.py --out world/view/now.svg
    python3 src/RimMandrake/Utils/ashkarr_csv_view.py --csv <other.csv> --out before.svg
    ... --ortho 90,0        # look straight down at a point, for coastlines
"""
from __future__ import annotations
import argparse, csv, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import worldview  # noqa: E402

TILES = os.path.join(ROOT, 'world', 'ASHKARR_WORLDMAP_tiles.csv')


def colour(b: str) -> str:
    c = worldview.BIOME_COLOR.get(b)
    if c is None:
        return '#ff00ff'          # 🔴 magenta = a biome the palette has never heard of
    return c if isinstance(c, str) else '#%02x%02x%02x' % tuple(c[:3])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--csv', default=TILES)
    ap.add_argument('--out', required=True)
    ap.add_argument('--ortho', help='lat,lon to centre an orthographic view on')
    ap.add_argument('--width', type=int, default=1800)
    ap.add_argument('--title', default='')
    ap.add_argument('--png', action='store_true',
                    help='also write a PNG beside the SVG — PIL is here, no rasteriser is')
    a = ap.parse_args()

    rows = list(csv.DictReader(open(a.csv, encoding='utf-8')))
    W = a.width
    parts = []

    if a.ortho:
        clat, clon = (math.radians(float(x)) for x in a.ortho.split(','))
        R = W / 2 - 10
        H = W
        parts.append(f'<circle cx="{W/2}" cy="{H/2}" r="{R}" fill="#0a0c10"/>')
        r = R * 0.012
        for t in rows:
            la, lo = math.radians(float(t['lat'])), math.radians(float(t['lon']))
            cosc = (math.sin(clat) * math.sin(la)
                    + math.cos(clat) * math.cos(la) * math.cos(lo - clon))
            if cosc <= 0:                      # 🔑 the far side of the globe
                continue
            x = W / 2 + R * math.cos(la) * math.sin(lo - clon)
            y = H / 2 - R * (math.cos(clat) * math.sin(la)
                             - math.sin(clat) * math.cos(la) * math.cos(lo - clon))
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" '
                         f'fill="{colour(t["biome"])}"/>')
    else:
        H = W // 2
        parts.append(f'<rect width="{W}" height="{H}" fill="#0a0c10"/>')
        r = W * 0.0035
        for t in rows:
            la, lo = float(t['lat']), float(t['lon'])
            x = (lo + 180.0) / 360.0 * W
            y = (90.0 - la) / 180.0 * H
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" '
                         f'fill="{colour(t["biome"])}"/>')

    if a.title:
        parts.append(f'<text x="14" y="26" fill="#e8ecf2" font-family="sans-serif" '
                     f'font-size="18">{a.title}</text>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
           f'viewBox="0 0 {W} {H}">' + "".join(parts) + '</svg>')
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    open(a.out, 'w', encoding='utf-8').write(svg)
    print(f"wrote {a.out}  ({len(rows)} tiles)")

    if a.png:
        # 🔑 No rasteriser is installed on this machine — no rsvg, no inkscape, no
        # cairosvg — so the PNG is drawn directly rather than converted. Same geometry,
        # same palette; it exists because an agent can LOOK at a PNG and cannot look at
        # an SVG.
        from PIL import Image, ImageDraw
        im = Image.new('RGB', (W, int(H)), '#0a0c10')
        dr = ImageDraw.Draw(im)
        for el in parts:
            m = re.match(r'<circle cx="([-\d.]+)" cy="([-\d.]+)" r="([\d.]+)" fill="(#[0-9a-fA-F]{6})"', el)
            if not m:
                continue
            x, y, rr, col = float(m[1]), float(m[2]), max(1.0, float(m[3])), m[4]
            dr.ellipse([x - rr, y - rr, x + rr, y + rr], fill=col)
        png = os.path.splitext(a.out)[0] + '.png'
        im.save(png)
        print(f"wrote {png}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
