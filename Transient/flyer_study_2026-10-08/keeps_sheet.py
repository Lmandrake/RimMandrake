#!/usr/bin/env python3
"""Static E/S/N of every owner-KEPT flyer (last ruling = keep) -> keeps_contact.png. Read-only."""
import csv, pathlib, xml.etree.ElementTree as ET
from PIL import Image, ImageDraw
REPO = pathlib.Path(__file__).resolve().parents[2]; SRC = REPO / "src"
idx = {}
for p in SRC.rglob("*.png"):
    s = str(p); i = s.find("/Textures/")
    if i >= 0: idx.setdefault(s[i+10:-4], p)
R = [r for r in csv.DictReader(open(REPO / "Transient/flyer_census_2026-10-08.csv"))
     if r["last_ruling"] and r["last_ruling"].split(" ")[1] == "keep"]
want = {r["defName"] for r in R}; tex = {}
for p in SRC.rglob("*.xml"):
    try: root = ET.parse(p).getroot()
    except Exception: continue
    for e in root.iter("PawnKindDef"):
        rc = e.findtext("race")
        if rc in want and rc not in tex:
            ts = [x.text.strip() for x in e.iter("texPath") if x.text and "essicated" not in x.text]
            if ts: tex[rc] = ts[-1]  # adult = last lifestage
C = 120
sheet = Image.new("RGB", (3 * (170 + 3 * C), ((len(R) + 2) // 3) * (C + 4)), (60, 44, 32))
d = ImageDraw.Draw(sheet)
for n, r in enumerate(R):
    col, row = n % 3, n // 3; x0 = col * (170 + 3 * C); y = row * (C + 4)
    d.text((x0 + 4, y + 4), r["defName"], fill="white"); d.text((x0 + 4, y + 20), str(n + 1), fill=(230, 200, 150))
    for c, f in enumerate(("east", "south", "north")):
        p = idx.get(f"{tex.get(r['defName'], '')}_{f}")
        x = x0 + 170 + c * C
        d.rectangle([x, y, x + C - 2, y + C - 2], fill=(120, 110, 100))
        if p:
            im = Image.open(p).convert("RGBA"); im.thumbnail((C - 2, C - 2))
            sheet.paste(im, (x, y), im)
out = pathlib.Path(__file__).with_name("keeps_contact.png"); sheet.save(out); print("wrote", out, len(R))
