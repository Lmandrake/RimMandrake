"""Offline before/after panel for the v4 ladders, at true in-game scale beside a colonist.

Background: the live capture Transient/bridge_run_1_20261023/captures/br1d3_c12_ladders_ew.png (a 3x3 D4 pit with
portable ladders on all four walls and a colonist). Calibrated by template match of the shipped portable north
texture: 228 px per cell, pit rim at crop (30,126), cells 228 px. The four shipped ladders are painted out by
copying ladder-free stretches of the same wall/rim, then each set is drawn at its def's rig (drawSize 1.5,
offset N/E/W +0.25, S -0.25 cell).

    python3 panel.py <out.png> [before_dir]     # before_dir defaults to the installed Textures
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
R = HERE.parents[5]
CAP = R / "Transient/bridge_run_1_20261023/captures/br1d3_c12_ladders_ew.png"
TEX = R / "src/RimMandrake/FlowWorks/Textures/Things/Building/FlowWorks/Canals"
PPC = 228
X0, Y0 = 30, 126            # pit rim (top-left) in the crop
CROP = (1362, 445, 1362 + 742, 445 + 842)


def clean_pit():
    im = Image.open(CAP).convert("RGBA").crop(CROP)
    def cp(src, dst):
        im.paste(im.crop(src), dst)
    cp((420, 0, 530, 262), (300, 0))          # north wall + ground above it, beside the ladder
    for y in range(270, 600, 44):            # side faces: ladder-free rows above the colonist's head
        cp((0, 592, 120, 636), (0, y))
        cp((622, 592, 742, 636), (622, y))
    cp((486, 700, 640, 842), (296, 700))      # south rim
    return im


def place(bg, tex, col, row, facing):
    t = tex.resize((int(384 * PPC / 256),) * 2, Image.BOX)
    cx, cy = X0 + PPC * col + PPC // 2, Y0 + PPC * row + PPC // 2
    off = -PPC // 4 if facing != "south" else PPC // 4
    bg.alpha_composite(t, (cx - t.width // 2, cy - t.height // 2 + off))


def scene(src, names):
    """names: {facing: texture name}; facings sit N (1,0), W (0,1), E (2,1), S (1,2)."""
    bg = clean_pit()
    cells = {"north": (1, 0), "west": (0, 1), "east": (2, 1), "south": (1, 2)}
    for f, n in names.items():
        path = src / f"{n}.png"
        if not path.exists():
            path = TEX / f"{n}.png"          # facings v4 does not redraw keep the shipped art
        place(bg, Image.open(path).convert("RGBA"), *cells[f], f)
    return bg


def label(im, text):
    """A header bar ABOVE the picture (never over it)."""
    out = Image.new("RGBA", (im.width, im.height + 34), (20, 20, 20, 255))
    out.alpha_composite(im, (0, 34))
    d = ImageDraw.Draw(out)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 20)
    except OSError:
        font = ImageFont.load_default()
    d.text((8, 6), text, fill=(240, 240, 240, 255), font=font)
    return out


def main():
    out = Path(sys.argv[1])
    before = Path(sys.argv[2]) if len(sys.argv) > 2 else TEX
    after = HERE / "out"
    rail = {"north": "RM_Ladder_north", "east": "RM_Ladder_east", "west": "RM_LadderRaised_west",
            "south": "RM_Ladder_south"}
    raised = {"north": "RM_LadderRaised_north", "south": "RM_LadderRaised_south"}
    port = {"north": "RM_LadderPortable_north", "east": "RM_LadderPortable_east", "west": "RM_LadderPortable_west",
            "south": "RM_LadderPortable_south"}
    rows = [("rail ladder (N, E lowered; W raised)", rail), ("rail ladder raised (N, S)", raised),
            ("portable ladder", port)]
    tiles = []
    for title, names in rows:
        tiles.append((title, scene(before, names), scene(after, names)))
    TH = 842 + 34
    W = 742 * 2 + 484 * 2 + 30
    sheet = Image.new("RGBA", (W, TH * len(tiles)), (30, 30, 30, 255))
    for i, (title, b, a) in enumerate(tiles):
        y = TH * i
        sheet.alpha_composite(label(b, f"BEFORE  {title}"), (0, y))
        sheet.alpha_composite(label(a, f"AFTER  {title}"), (742 + 10, y))
        for j, (t, tag) in enumerate(((b, "before"), (a, "after"))):
            z = t.crop((250, 0, 492, 300)).resize((484, 600), Image.LANCZOS)
            sheet.alpha_composite(label(z, f"north wall x2 {tag}"), (742 * 2 + 20 + j * 494, y))
    sheet.convert("RGB").save(out)
    print(out, sheet.size)


if __name__ == "__main__":
    main()
