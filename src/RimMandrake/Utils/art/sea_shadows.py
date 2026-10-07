#!/usr/bin/env python3
"""sea_shadows.py — fit each creature's engine shadow to its installed art (owner, 2026-10-07).

Owner: "most of the shadows in the sea need to be regenerated after a sheet is worked due to the new
art having differing shadows than the basic shapes that once held there."

How RimWorld draws a pawn's shadow (decompiled 1.6, PawnRenderer.DrawShadowInternal): only from
`race.specialShadowData` or the life stage's `bodyGraphicData/shadowData`. It is a soft box, not a
texture: ShadowData.volume = (width x, tallness y, depth z), drawn unrotated (Rot4.North) at
`offset` from the pawn's centre. No volume -> no shadow. So "regenerating" a shadow means measuring
the installed sprite and writing a volume that sits under THAT silhouette, not under the old shape.

Deterministic rule, per life stage (D = that stage's drawSize, sprite canvas = D x D cells):
  alpha mask = pixels with alpha >= 128 on the _east and _south facings (or the single texture);
  w, h      = mean bbox width / height of the two facings, as canvas fractions;
  width x   = WIDTH_K * w * D
  depth z   = clamp(DEPTH_K * h * D, 0.25 x, 0.6 x)
  tallness y = TALLNESS (shadow strength)
  offset z  = world z of the east sprite's lowest opaque row + 0.3 * depth  (shadow under the base)
  offset x  = 0 (east/west mirror; the shadow does not)
Existing shadowData in the stage is replaced; nothing else in the def is touched.

    python3 src/RimMandrake/Utils/art/sea_shadows.py apply <Defs xml> <PawnKind defName>... [--dry-run]
    python3 src/RimMandrake/Utils/art/sea_shadows.py contact <out.png> <Defs xml>:<defName>...

Rerun it after every sheet close that installs creature art (art-close procedure step).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

WIDTH_K, DEPTH_K, TALLNESS, ALPHA_MIN = 0.7, 0.3, 0.35, 128


def _mod_root(defs_xml: Path) -> Path:
    for p in defs_xml.resolve().parents:
        if p.name == "Defs":
            return p.parent
    raise SystemExit(f"{defs_xml} is not under a Defs/ folder")


def _bbox(png: Path):
    a = Image.open(png).convert("RGBA").getchannel("A").point(lambda v: 255 if v >= ALPHA_MIN else 0)
    b = a.getbbox()
    if not b:
        raise SystemExit(f"{png}: no opaque pixels")
    W, H = a.size
    return (b[0] / W, b[1] / H, b[2] / W, b[3] / H)


def facings(textures: Path, tex: str):
    east, south, single = (textures / f"{tex}_east.png", textures / f"{tex}_south.png", textures / f"{tex}.png")
    if east.is_file() and south.is_file():
        return east, south
    if single.is_file():
        return single, single
    raise SystemExit(f"no texture for {tex} under {textures}")


def fit(textures: Path, tex: str, D: float) -> dict:
    e, s = facings(textures, tex)
    be, bs = _bbox(e), _bbox(s)
    w = ((be[2] - be[0]) + (bs[2] - bs[0])) / 2
    h = ((be[3] - be[1]) + (bs[3] - bs[1])) / 2
    x = WIDTH_K * w * D
    z = min(max(DEPTH_K * h * D, 0.25 * x), 0.6 * x)
    bottom = (0.5 - be[3]) * D
    return {"x": round(x, 3), "y": TALLNESS, "z": round(z, 3), "oz": round(bottom + 0.3 * z, 3)}


def _kind_block(text: str, defname: str):
    m = re.search(r"<PawnKindDef\b[^>]*>(?:(?!</PawnKindDef>).)*?<defName>" + re.escape(defname)
                  + r"</defName>.*?</PawnKindDef>", text, re.S)
    if not m:
        raise SystemExit(f"PawnKindDef {defname} not found")
    return m.start(), m.end()


BGD = re.compile(r"<bodyGraphicData>(.*?)</bodyGraphicData>", re.S)


def apply(defs_xml: Path, defnames: list[str], dry: bool = False) -> list[dict]:
    textures = _mod_root(defs_xml) / "Textures"
    text = defs_xml.read_text()
    out = []
    for dn in defnames:
        a, b = _kind_block(text, dn)
        block = text[a:b]

        def one(m):
            body = m.group(1)
            tex = re.search(r"<texPath>([^<]+)</texPath>", body).group(1).strip()
            dm = re.search(r"<drawSize>\(?\s*([0-9.]+)", body)
            D = float(dm.group(1)) if dm else 1.0
            f = fit(textures, tex, D)
            out.append({"def": dn, "drawSize": D, **f})
            body = re.sub(r"\s*<shadowData>.*?</shadowData>", "", body, flags=re.S)
            sd = (f"<shadowData><volume>({f['x']}, {f['y']}, {f['z']})</volume>"
                  f"<offset>(0, 0, {f['oz']})</offset></shadowData>")
            sep = "\n          " if "\n" in body else ""
            return f"<bodyGraphicData>{body.rstrip()}{sep}{sd}{chr(10) + '        ' if sep else ''}</bodyGraphicData>"

        new_block = BGD.sub(one, block)
        text = text[:a] + new_block + text[b:]
    if not dry:
        defs_xml.write_text(text)
    return out


def contact(out_png: Path, specs: list[str], cell_px: int = 160) -> None:
    """Before (no box) / after (fitted box) for each def's adult stage, on sea-floor grey."""
    tiles = []
    for spec in specs:
        xml, dn = spec.rsplit(":", 1)
        xml = Path(xml)
        text = xml.read_text()
        a, b = _kind_block(text, dn)
        stages = BGD.findall(text[a:b])
        body = stages[-1]
        tex = re.search(r"<texPath>([^<]+)</texPath>", body).group(1).strip()
        D = float(re.search(r"<drawSize>\(?\s*([0-9.]+)", body).group(1))
        vm = re.search(r"<volume>\(([^)]+)\)</volume>\s*<offset>\(([^)]+)\)</offset>", body)
        e, _ = facings(_mod_root(xml) / "Textures", tex)
        tiles.append((dn, e, D, [float(v) for v in vm.group(1).split(",")] if vm else None,
                      [float(v) for v in vm.group(2).split(",")] if vm else None))
    cols = 8
    rows = (len(tiles) + cols - 1) // cols
    W = Image.new("RGBA", (cols * cell_px * 2, rows * (cell_px + 18)), (96, 104, 104, 255))
    dr = ImageDraw.Draw(W)
    for i, (dn, png, D, vol, off) in enumerate(tiles):
        ox, oy = (i % cols) * cell_px * 2, (i // cols) * (cell_px + 18)
        spr = Image.open(png).convert("RGBA").resize((cell_px, cell_px))
        for j in range(2):
            x0 = ox + j * cell_px
            if j == 1 and vol:
                s = cell_px / D  # px per cell
                sh = Image.new("RGBA", (cell_px, cell_px), (0, 0, 0, 0))
                sd = ImageDraw.Draw(sh)
                cx, cz = cell_px / 2, cell_px / 2 - off[2] * s
                hw, hd = vol[0] * s / 2, vol[2] * s / 2
                sd.ellipse([cx - hw, cz - hd, cx + hw, cz + hd], fill=(0, 0, 0, int(255 * min(1, vol[1] * 1.6))))
                W.alpha_composite(sh.filter(ImageFilter.GaussianBlur(max(1, hd / 2))), (x0, oy))
            W.alpha_composite(spr, (x0, oy))
        dr.text((ox + 4, oy + cell_px + 3), f"{dn}  before | after", fill=(235, 235, 225, 255))
    W.convert("RGB").save(out_png)


def main(argv):
    if len(argv) >= 3 and argv[0] == "apply":
        dry = "--dry-run" in argv
        for r in apply(Path(argv[1]), [a for a in argv[2:] if a != "--dry-run"], dry):
            print(f"{r['def']:22s} D={r['drawSize']:<5} volume=({r['x']}, {r['y']}, {r['z']}) offset z={r['oz']}")
        return 0
    if len(argv) >= 3 and argv[0] == "contact":
        contact(Path(argv[1]), argv[2:])
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
