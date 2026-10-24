#!/usr/bin/env python3
"""Owner sheet for MODERN_PIPE_REDRAW_FIRETRUCK_RED_RETIRED: every recoloured Modern piece BEFORE (red) | AFTER (blue),
numbered stations on game-dirt ground, the in-context scene before and after (scene.py, an OFFLINE mock, not in game),
and the owner's reference photo beside it. The photo is passed in by path and never copied into the repo.

Usage: blue_sheet.py CAND_DIR HEADS_DIR OUT.png [--ref PHOTO]
  CAND_DIR   waterworks_blue.py output (same relative paths as PIECES)
  HEADS_DIR  squat_heads.py --out output (Modern/RM_SprinklerHead.png)"""
import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import waterworks_blue as wb  # noqa: E402

GROUND = (112, 86, 62, 255)
TILE, PAD, LABEL = 150, 10, 26
COLS = 5


def font(sz):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(p, sz)
        except OSError:
            continue
    return ImageFont.load_default()


def on_ground(im, size):
    im = im.convert("RGBA")
    k = size / max(im.size)
    im = im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS)
    cv = Image.new("RGBA", (size, size), GROUND)
    cv.alpha_composite(im, ((size - im.width) // 2, (size - im.height) // 2))
    return cv


def scenes(cand, heads, tmp):
    out = {}
    for tag, root, head in (("before", wb.RED, wb.TEX / wb.SPRINKLER), ("after", cand, heads / "Modern/RM_SprinklerHead.png")):
        flat = tmp / tag
        flat.mkdir()
        for rel in wb.PIECES:
            shutil.copy(root / rel, flat / Path(rel).name)
        shutil.copy(head, flat / "RM_SprinklerHead.png")
        png = tmp / ("scene_%s.png" % tag)
        subprocess.run([sys.executable, str(HERE / "scene.py"), str(png), "--over", str(flat)], check=True,
                       stdout=subprocess.DEVNULL)
        out[tag] = Image.open(png).convert("RGBA")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cand")
    ap.add_argument("heads")
    ap.add_argument("out")
    ap.add_argument("--ref")
    a = ap.parse_args(argv)
    cand, heads = Path(a.cand), Path(a.heads)
    rows = [(rel, wb.RED / rel, cand / rel) for rel in wb.PIECES]
    rows.append((wb.SPRINKLER + " (squat head)", wb.TEX / wb.SPRINKLER, heads / "Modern/RM_SprinklerHead.png"))
    sw, sh = 2 * TILE + 3 * PAD, TILE + LABEL + 2 * PAD
    grid_w = COLS * sw
    grid_h = -(-len(rows) // COLS) * sh
    with tempfile.TemporaryDirectory() as t:
        sc = scenes(cand, heads, Path(t))
    scene_w = sc["before"].width
    ref_w = 520
    W = ref_w + PAD + max(grid_w, 2 * scene_w + 3 * PAD)
    H = 60 + grid_h + LABEL + sc["before"].height + 3 * PAD
    sheet = Image.new("RGBA", (W, H), (34, 34, 38, 255))
    d = ImageDraw.Draw(sheet)
    f, fs = font(15), font(12)
    d.text((PAD, 12), "MODERN_PIPE_REDRAW_FIRETRUCK_RED_RETIRED - Modern pipe system: firetruck red (BEFORE) -> "
           "weathered waterworks blue (AFTER). Recolour only: every piece's alpha is unchanged, so fits do not move.",
           fill=(235, 235, 235), font=f)
    d.text((PAD, 34), "Stations 1-%d: BEFORE left, AFTER right. %d-%d: offline scene mock (NOT in game). R: owner's reference."
           % (len(rows), len(rows) + 1, len(rows) + 2), fill=(200, 200, 200), font=fs)
    x0, y0 = ref_w + PAD, 60
    if a.ref:
        ref = Image.open(a.ref).convert("RGBA")
        ref = ref.resize((ref_w - PAD, round(ref.height * (ref_w - PAD) / ref.width)), Image.LANCZOS)
        sheet.alpha_composite(ref, (PAD, y0 + LABEL))
        d.text((PAD, y0 + 4), "R  owner's reference (stock photo, not in repo)", fill=(255, 220, 120), font=f)
    for i, (rel, before, after) in enumerate(rows):
        x, y = x0 + (i % COLS) * sw, y0 + (i // COLS) * sh
        d.text((x + PAD, y + 4), "%d  %s" % (i + 1, rel.replace("/Modern/", "/").replace(".png", "")), fill=(255, 220, 120), font=fs)
        sheet.alpha_composite(on_ground(Image.open(before), TILE), (x + PAD, y + LABEL))
        sheet.alpha_composite(on_ground(Image.open(after), TILE), (x + 2 * PAD + TILE, y + LABEL))
    ys = y0 + grid_h + PAD
    for k, tag in enumerate(("before", "after")):
        x = x0 + k * (scene_w + PAD)
        d.text((x + PAD, ys + 4), "%d  scene %s" % (len(rows) + 1 + k, tag.upper()), fill=(255, 220, 120), font=f)
        sheet.alpha_composite(sc[tag], (x + PAD, ys + LABEL))
    sheet.convert("RGB").save(a.out)
    print(a.out, sheet.size)


if __name__ == "__main__":
    main()
