"""v5 offline scenes at true in-game scale (v4/panel.py's cleaned live pit capture, 228 px per cell, beside a colonist).

    python3 scene.py <out.png> <set>...     # set = portable | wood | wood_raised | steel | steel_raised | portable_old
Each set is one 3x3 pit with the set's four facings on the four walls (N top, W left, E right, S bottom).
"""
import sys
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "v4"))
import panel as P4  # noqa: E402

PAD = 24                                   # v4's crop leaves 28 px past the side rims; a raised side ladder overhangs ~35


def _padded_pit(_clean=P4.clean_pit):
    """v4's cleaned pit with PAD px of mirrored outside ground added left and right (so side overhangs are not cut)."""
    im = _clean()
    w, h = im.size
    out = Image.new("RGBA", (w + 2 * PAD, h))
    out.paste(im, (PAD, 0))
    out.paste(im.crop((0, 0, PAD, h)).transpose(Image.FLIP_LEFT_RIGHT), (0, 0))
    out.paste(im.crop((w - PAD, 0, w, h)).transpose(Image.FLIP_LEFT_RIGHT), (w + PAD, 0))
    return out


P4.clean_pit = _padded_pit
P4.X0 += PAD

OUT = HERE / "out"
SETS = {
    "portable": "RM_LadderPortable", "wood": "RM_Ladder", "wood_raised": "RM_LadderRaised",
    "steel": "RM_LadderSteel", "steel_raised": "RM_LadderSteelRaised",
}


def scene(base, old=False):
    names = {f: f"{base}_{f}" for f in ("north", "east", "west", "south")}
    src = P4.TEX if old else OUT
    return P4.label(P4.scene(src, names), ("BEFORE " if old else "") + base)


def main():
    out = Path(sys.argv[1])
    tiles = []
    for s in sys.argv[2:]:
        old = s.endswith("_old")
        tiles.append(scene(SETS[s.replace("_old", "")], old))
    W = sum(t.width for t in tiles) + 10 * (len(tiles) - 1)
    sheet = Image.new("RGBA", (W, tiles[0].height), (30, 30, 30, 255))
    x = 0
    for t in tiles:
        sheet.alpha_composite(t, (x, 0))
        x += t.width + 10
    sheet.convert("RGB").save(out)
    print(out, sheet.size)


if __name__ == "__main__":
    main()
