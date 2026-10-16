#!/usr/bin/env python3
"""Census: every flyer (race ThingDef with MaxFlightTime, or a PawnKind with a flying frame prefix) in src/,
its idle north/south texture, the north/south opaque-area ratio (folded wings invisible from the north reads
as a low ratio) and whether a flip-book prefix is set and its frames exist. Writes CSV + north contact sheet."""
import re, glob, csv, sys
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image, ImageDraw
R = Path(__file__).resolve().parents[2]; SRC = R / "src"
tex = {}
for p in SRC.rglob("Textures/**/*.png"):
    rel = str(p).split("/Textures/", 1)[1][:-4]
    tex.setdefault(rel, p)
races, kinds = {}, {}
for f in SRC.rglob("*.xml"):
    if "/Textures/" in str(f): continue
    try: root = ET.parse(f).getroot()
    except Exception: continue
    for d in root:
        dn = d.findtext("defName")
        if not dn: continue
        if d.tag == "ThingDef" and d.find("race") is not None:
            mft = d.findtext("statBases/MaxFlightTime")
            races[dn] = dict(file=str(f.relative_to(R)), mft=mft, mod=str(f.relative_to(SRC)).split("/Defs")[0].split("/Patches")[0])
        elif d.tag == "PawnKindDef":
            tp = [e.text for e in d.iter("texPath") if e.text and "essicated" not in e.text]
            fp = [e.text for e in d.iter("flyingAnimationFramePathPrefix") if e.text]
            kinds[dn] = dict(race=d.findtext("race") or dn, tex=tp, prefix=fp)
def area(p):
    a = np.array(Image.open(p).convert("RGBA"))[..., 3] > 128
    ys, xs = np.nonzero(a)
    return a.sum(), (xs.max()-xs.min()+1 if len(xs) else 0), (ys.max()-ys.min()+1 if len(ys) else 0)
rows = []
for kn, k in kinds.items():
    r = races.get(k["race"])
    if not r: continue
    if not (r["mft"] or k["prefix"]): continue
    t = k["tex"][-1] if k["tex"] else None
    n = tex.get(t + "_north") if t else None; s = tex.get(t + "_south") if t else None
    row = dict(kind=kn, race=k["race"], mod=r["mod"], mft=r["mft"] or "", texPath=t or "", north=str(n.relative_to(R)) if n else "", prefix=(k["prefix"][-1] if k["prefix"] else ""))
    pf = row["prefix"]; row["frames_north"] = len([x for x in tex if pf and x.startswith(pf) and x.endswith("_north")])
    if n and s:
        an, wn, hn = area(n); as_, ws, hs = area(s)
        row.update(n_over_s_area=round(an/max(as_,1),2), north_w_over_h=round(wn/max(hn,1),2), south_w_over_h=round(ws/max(hs,1),2))
    rows.append(row)
rows.sort(key=lambda r: (r["mod"], r["kind"]))
out = Path(__file__).with_name("flyer_north_census.csv")
keys = ["kind","race","mod","mft","texPath","north","prefix","frames_north","n_over_s_area","north_w_over_h","south_w_over_h"]
with open(out, "w", newline="") as fh:
    w = csv.DictWriter(fh, keys); w.writeheader(); [w.writerow({k: r.get(k, "") for k in keys}) for r in rows]
# contact sheet: north idle beside south idle, 128px each
cells = [r for r in rows if r["north"]]
C = 8; cw = 280; ch = 150
sheet = Image.new("RGBA", (C*cw, ((len(cells)+C-1)//C)*ch), (80,80,80,255)); dr = ImageDraw.Draw(sheet)
for i, r in enumerate(cells):
    x, y = (i % C)*cw, (i//C)*ch
    for j, f in enumerate([R/r["north"], Path(str(R/r["north"]).replace("_north.png","_south.png"))]):
        try: im = Image.open(f).convert("RGBA").resize((128,128))
        except Exception: continue
        sheet.alpha_composite(im, (x+4+j*132, y))
    dr.text((x+4, y+130), f"{i} {r['kind'][:34]}", fill=(255,255,255,255))
sheet.save(Path(__file__).with_name("flyer_north_sheet.png"))
print(len(rows), "flyer kinds;", sum(1 for r in rows if r["north"]), "with idle north;", sum(1 for r in rows if r["prefix"]), "with prefix", file=sys.stderr)
