#!/usr/bin/env python3
"""kit_art_derive.py - build the Slime free kit's last stand-in replacements (GELATINOUSSLIME_KIT_ART_1).

    python3 src/RimMandrake/GelatinousSlime/kit_art_derive.py --masters DIR --out DIR

Two kinds of output, written under --out as Textures-relative paths (install each with `art.py install`):

* CONFORMED renders (Codex $imagegen masters in --masters): the slime pit south/east and the archive vat south. Each is
  trimmed to its alpha box and fitted, aspect kept, onto the canvas that drawSize x 128 px/cell asks for
  (pit drawSize 3.5x1.5 -> 448x192 south, 192x448 east, since Graphic.MeshAt swaps the mesh for a horizontal
  rotation; vat 2x2 -> 256x256). The pit's north falls back to south (Graphic_Multi), which a symmetric trough allows.
* DERIVED from our own shipped art, so nothing vanilla is drawn:
  - the gelatid's desiccated body (was the vanilla tortoise skeleton): each facing slumped to 55 % height on its
    base line, dried to a dull amber husk, slightly translucent. A jelly animal leaves a dried film, not bones.
  - slime-grass leafless (was vanilla Grass_Leafless): each slime-grass variant dried to a brown-amber husk.

Resizing works in premultiplied alpha (PIL "RGBa"), so cut-out edges do not pick up a dark halo.
"""
import argparse
from pathlib import Path

from PIL import Image

MOD = Path(__file__).resolve().parent
TEX = MOD / "Textures"

RENDERS = [  # (master file, Textures-relative output, canvas)
    ("pit_south_raw.png", "Things/Building/RM_SlimePit/RM_SlimePit_south.png", (448, 192)),
    ("pit_east_raw.png", "Things/Building/RM_SlimePit/RM_SlimePit_east.png", (192, 448)),
    ("vat_south_raw.png", "Things/Building/RM_ArchiveVat/RM_ArchiveVat_south.png", (256, 256)),
]
MARGIN = 0.02  # fraction of the canvas left clear on each side


def resize(im, size):
    return im.convert("RGBa").resize(size, Image.LANCZOS).convert("RGBA")


def fit(master, canvas):
    im = master.convert("RGBA")
    im = im.crop(im.split()[-1].getbbox())
    cw, ch = canvas
    avail_w, avail_h = cw * (1 - 2 * MARGIN), ch * (1 - 2 * MARGIN)
    scale = min(avail_w / im.width, avail_h / im.height)
    size = (max(1, round(im.width * scale)), max(1, round(im.height * scale)))
    out = Image.new("RGBA", canvas, (0, 0, 0, 0))
    out.paste(resize(im, size), ((cw - size[0]) // 2, (ch - size[1]) // 2))
    return out


def dry(im, tint=(150, 112, 62), alpha=0.9, sat_keep=0.15):
    """Dull a jelly sprite to a dried amber husk: mostly-grey luminance times a warm tint, alpha scaled."""
    px = im.convert("RGBA").load()
    w, h = im.size
    out = Image.new("RGBA", (w, h))
    po = out.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a == 0:
                po[x, y] = (0, 0, 0, 0)
                continue
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            rgb = []
            for c, t in zip((r, g, b), tint):
                grey = lum * (1 - sat_keep) + c * sat_keep
                rgb.append(max(0, min(255, round(grey * t / 160))))
            po[x, y] = (*rgb, round(a * alpha))
    return out


def slump(im, keep=0.55):
    """Squash the subject vertically onto its own base line (the lowest opaque row stays put)."""
    im = im.convert("RGBA")
    l, t, r, b = im.split()[-1].getbbox()
    body = im.crop((l, t, r, b))
    new_h = max(1, round(body.height * keep))
    body = resize(body, (body.width, new_h))
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.paste(body, (l, b - new_h))
    return out


def derived():
    gel = TEX / "Things/Pawn/Animal/RM_Gelatid"
    for facing in ("south", "east", "north"):
        src = Image.open(gel / f"RM_Gelatid_{facing}.png")
        yield f"Things/Pawn/Animal/RM_Gelatid/RM_Gelatid_Dessicated_{facing}.png", dry(slump(src))
    grass = TEX / "Things/Plant/RM_SlimeGrass/RM_SlimeGrass"
    for p in sorted(grass.glob("RM_SlimeGrass_*.png")):
        letter = p.stem.rsplit("_", 1)[1]
        yield (f"Things/Plant/RM_SlimeGrass_Leafless/RM_SlimeGrass_Leafless_{letter}.png",
               dry(Image.open(p), tint=(140, 118, 80), alpha=0.95, sat_keep=0.25))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--masters", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    a = ap.parse_args()
    jobs = [(rel, fit(Image.open(a.masters / m), canvas)) for m, rel, canvas in RENDERS]
    jobs += list(derived())
    for rel, im in jobs:
        dst = a.out / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        im.save(dst)
        print(f"{rel}  {im.size[0]}x{im.size[1]}")


if __name__ == "__main__":
    main()
