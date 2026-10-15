"""TANK_TALL_BUILD_TWICE_THE_DRINK phase 1: measure each reference collected by collect_refs.py.
Per row: canvas, px/cell, subject span in cells, overhang of the subject past the footprint (south/north, cells),
and for upright cylinders the brightest body column (light side). Writes measurements.json + references.png.
usage: measure_refs.py <refs dir> <out png>"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont
D, OUT = sys.argv[1], sys.argv[2]
rows = json.load(open(os.path.join(D, "refs.json")))
ELL = json.load(open(os.path.join(D, "ellipse.json"))) if os.path.exists(os.path.join(D, "ellipse.json")) else {}
res = []
for r in rows:
    im = Image.open(os.path.join(D, r["defName"] + ".png")).convert("RGBA")
    W, H = im.size; dw, dh = r["drawSize"]; fw, fh = r["size"]; oz = r.get("drawOffsetZ", 0) or 0
    a = im.getchannel("A").point(lambda v: 255 if v >= 128 else 0); bb = a.getbbox()
    ppc = W / dw
    # world z (cells, 0 = footprint centre, +north) of subject top/bottom
    top_z = oz + dh / 2 - bb[1] / H * dh
    bot_z = oz + dh / 2 - bb[3] / H * dh
    m = dict(defName=r["defName"], mod=r["mod"], canvas=f"{W}x{H}", footprint=f"{fw}x{fh}", drawSize=f"{dw}x{dh}",
             drawOffsetZ=oz, px_per_cell=round(ppc), subject_cells=[round((bb[2]-bb[0])/ppc, 2), round((bb[3]-bb[1])/ppc, 2)],
             south_overhang=round(-fh/2 - bot_z, 2), north_overhang=round(top_z - fh/2, 2),
             height_over_depth=round(((bb[3]-bb[1])/ppc) / fh, 2))
    # light side: mean luminance of the left vs right third of the subject's middle band
    px = im.load(); y0, y1 = bb[1] + (bb[3]-bb[1])*2//5, bb[1] + (bb[3]-bb[1])*3//5
    def lum(x0, x1):
        v = [sum(px[x, y][:3]) / 3 for x in range(x0, x1) for y in range(y0, y1) if px[x, y][3] >= 200]
        return sum(v) / len(v) if v else 0
    w3 = (bb[2]-bb[0]) // 3
    m["lum_left_mid_right"] = [round(lum(bb[0], bb[0]+w3)), round(lum(bb[0]+w3, bb[2]-w3)), round(lum(bb[2]-w3, bb[2]))]
    if r["defName"] in ELL: m["top_ellipse_minor_over_major"] = ELL[r["defName"]]
    res.append(m)
json.dump(res, open(os.path.join(D, "measurements.json"), "w"), indent=1)
# contact sheet at 48 px/cell, footprint outlined yellow, drawSize box dashed grey
P = 48; pad = 14; tiles = []
for r, m in zip(rows, res):
    im = Image.open(os.path.join(D, r["defName"] + ".png")).convert("RGBA")
    dw, dh = r["drawSize"]; fw, fh = r["size"]; oz = r.get("drawOffsetZ", 0) or 0
    W, H = int(dw*P), int(dh*P); im = im.convert("RGBa").resize((W, H), Image.LANCZOS).convert("RGBA")
    top_cells = max(dh/2 + oz, fh/2); bot_cells = max(dh/2 - oz, fh/2)
    cw = int(max(dw, fw)*P) + 2*pad; ch = int((top_cells + bot_cells)*P) + 2*pad + 64
    t = Image.new("RGBA", (max(cw, 190), ch), (122, 112, 96, 255)); dr = ImageDraw.Draw(t)
    cx = t.width/2; cz = pad + top_cells*P
    for gx in range(-8, 9):
        for gz in range(-10, 10):
            dr.rectangle([cx+gx*P, cz+gz*P, cx+(gx+1)*P, cz+(gz+1)*P], outline=(112, 102, 88, 255))
    t.alpha_composite(im, (int(cx-W/2), int(cz - oz*P - H/2)))
    dr.rectangle([cx-fw*P/2, cz-fh*P/2, cx+fw*P/2, cz+fh*P/2], outline=(255, 230, 0, 255), width=2)
    y = ch - 60
    lines = [r["defName"][:26], f"{m['canvas']} draw {m['drawSize']} foot {m['footprint']}",
             f"N overhang {m['north_overhang']:+} S {m['south_overhang']:+} cells"]
    if "top_ellipse_minor_over_major" in m: lines.append(f"top ellipse b/a {m['top_ellipse_minor_over_major']}")
    for i, s in enumerate(lines): dr.text((6, y + i*14), s, fill=(255, 255, 255, 255))
    tiles.append(t)
per = 9; rowsI = [tiles[i:i+per] for i in range(0, len(tiles), per)]
WW = max(sum(t.width for t in rr) for rr in rowsI); HH = sum(max(t.height for t in rr) for rr in rowsI) + 40
c = Image.new("RGB", (WW, HH), (50, 46, 42)); d2 = ImageDraw.Draw(c)
d2.text((8, 8), "Building camera references, 2026-10-14 - 48 px/cell, yellow = footprint, grid = cells. Measurements: design/RimMandrake/building_camera_perspective_2026-10-14.md", fill=(255, 255, 255))
y = 40
for rr in rowsI:
    x = 0; h = max(t.height for t in rr)
    for t in rr: c.paste(t, (x, y + h - t.height)); x += t.width
    y += h
# wall atlases: front band vs top, measured by luminance runs down one column of a horizontal run (WALLS in refs.json side file)
WALLS = json.load(open(os.path.join(D, "walls.json"))) if os.path.exists(os.path.join(D, "walls.json")) else []
if WALLS:
    strip = Image.new("RGB", (WW, 250), (50, 46, 42)); x = 8; d3 = ImageDraw.Draw(strip)
    for w in WALLS:
        a = Image.open(os.path.join(D, w["file"])).convert("RGBA"); a = a.resize((180, 180), Image.NEAREST)
        bg = Image.new("RGBA", a.size, (122, 112, 96, 255)); bg.alpha_composite(a); strip.paste(bg, (x, 8))
        for i, s_ in enumerate([w["name"], f"front {w['front']}px : top {w['top']}px", f"front = {w['front']/(w['front']+w['top']):.0%} of wall depth"]):
            d3.text((x, 194 + i*14), s_, fill=(255, 255, 255))
        x += 230
    c2 = Image.new("RGB", (WW, HH + 250)); c2.paste(c, (0, 0)); c2.paste(strip, (0, HH)); c = c2
c.save(OUT); print(OUT, c.size)
for m in res: print(m)
