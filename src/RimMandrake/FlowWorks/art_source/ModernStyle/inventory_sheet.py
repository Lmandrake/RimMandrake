#!/usr/bin/env python3
"""Inventory composites for MODERN_LOOK_REDESIGN_BEYOND_RED_ENAMEL: every Modern-look texture in FlowWorks
and GimmeSomeSlack beside its Scrapper / Industrial / Futuristic siblings, on a game-dirt ground.
Usage: inventory_sheet.py OUTDIR"""
import sys, re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
REPO = Path(__file__).resolve().parents[5]
ROOTS = [REPO / "src/RimMandrake/FlowWorks/Textures", REPO / "src/RimMandrake/GimmeSomeSlack/Textures"]
LOOKS = ["Modern", "Scrapper", "Industrial", "Futuristic"]
GROUND = (112, 86, 62, 255)
CELL = 200

def files():
    out = []
    for r in ROOTS:
        for p in sorted(r.rglob("*.png")):
            rel = p.relative_to(r).as_posix()
            if "Modern" not in rel or rel.endswith("_m.png"):
                continue
            out.append((r, rel))
    return out

def sib(root, rel, look):
    cand = rel.replace("/Modern/", f"/{look}/").replace("_Modern", f"_{look}")
    p = root / cand
    return p if p.exists() else None

def thumb(p):
    im = Image.open(p).convert("RGBA")
    im.thumbnail((CELL - 10, CELL - 30), Image.LANCZOS)
    return im

def group(rel):
    m = re.search(r"FlowWorks/([A-Za-z]+)/|GimmeSomeSlack/([A-Za-z]+)/|Resource/FlowWorks|Drawbridge", rel)
    if "Resource" in rel: return "Containers"
    if "Drawbridge" in rel: return "Drawbridge"
    return (m.group(1) or m.group(2)) if m else "Other"

def main(out):
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    font = ImageFont.load_default()
    groups = {}
    for root, rel in files():
        groups.setdefault(group(rel), []).append((root, rel))
    for g, rows in groups.items():
        W = 260 + CELL * 4; H = 24 + CELL * len(rows)
        sheet = Image.new("RGBA", (W, H), (40, 30, 22, 255)); d = ImageDraw.Draw(sheet)
        for i, look in enumerate(LOOKS):
            d.text((260 + i * CELL + 6, 6), look, fill=(240, 220, 180, 255), font=font)
        for j, (root, rel) in enumerate(rows):
            y = 24 + j * CELL
            d.text((6, y + 6), "\n".join([rel.split("/")[-1]] + rel.split("/")[-3:-1]), fill=(240, 220, 180, 255), font=font)
            for i, look in enumerate(LOOKS):
                p = root / rel if look == "Modern" else sib(root, rel, look)
                x = 260 + i * CELL
                sheet.paste(Image.new("RGBA", (CELL - 6, CELL - 6), GROUND), (x + 3, y + 3))
                if p:
                    t = thumb(p)
                    sheet.alpha_composite(t, (x + (CELL - t.width) // 2, y + (CELL - t.height) // 2))
                else:
                    d.text((x + 10, y + 10), "(none)", fill=(200, 200, 200, 255), font=font)
        sheet.convert("RGB").save(out / f"inventory_{g}.png")
        print(g, len(rows), out / f"inventory_{g}.png")

if __name__ == "__main__":
    main(sys.argv[1])
