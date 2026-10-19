#!/usr/bin/env python3
"""True-scale (128 px per cell) previews of linked suspension decks, drawn with the game's own selection logic
(build_deck_atlas.bridge_image = RM_SuspensionDeckLink.TileMask + the quarter turn). Usage: preview_decks.py <outdir>"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_deck_atlas as B

PX = 128
BG = (62, 52, 44, 255)


def sheet(rows, out):
    """rows: [(label, atlas path)]; each row: 6x1, 6x3 N-S and 6x3 E-W."""
    pad = 24
    h = 6 * PX + 2 * pad + 20
    img = Image.new("RGBA", (PX + 3 * PX + 6 * PX + 4 * pad + 120, h * len(rows)), BG)
    d = ImageDraw.Draw(img)
    for r, (label, path) in enumerate(rows):
        a = Image.open(path).convert("RGBA")
        y = r * h + pad + 14
        d.text((pad, r * h + 6), f"{label}   6 long x 1 wide | 6 x 3 N-S | 6 x 3 E-W   ({PX} px = 1 cell)", fill=(240, 230, 210, 255))
        x = pad
        for (length, width, horiz) in ((6, 1, False), (6, 3, False), (6, 3, True)):
            b = B.bridge_image(a, length, width, horiz, PX)
            img.alpha_composite(b, (x, y))
            x += b.width + pad
        d.rectangle((x, y, x + PX, y + PX), outline=(240, 230, 210, 255))
        d.text((x + 4, y + 4), "1 cell", fill=(240, 230, 210, 255))
    img.convert("RGB").save(out)
    print("wrote", out, img.size)


def main():
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    t = B.TEXROOT
    sheet([(f"{n} deck (type art)", t / f"Things/Building/FlowWorks/SuspensionBridge/RM_SuspensionDeck_{n}_Atlas.png")
           for n in ("Rope", "Timber", "Steel", "Heavy")], out / "suspension_decks_linked_types_2026-10-18.png")
    rows = [(f"{lk} deck", t / f"RimMandrake/FlowWorks/SuspensionBridge/{lk}/RM_SuspensionDeck_Atlas.png") for lk in B.LOOKS]
    sheet(rows, out / "suspension_decks_linked_looks_2026-10-18.png")
    sheet([(f"{lk} grated", t / f"RimMandrake/FlowWorks/SuspensionBridge/{lk}/RM_SuspensionDeckGrated_Atlas.png") for lk in B.LOOKS],
          out / "suspension_decks_linked_grated_2026-10-18.png")


if __name__ == "__main__":
    main()
