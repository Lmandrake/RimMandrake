#!/usr/bin/env python3
"""True-scale offline look at the ullai beside vanilla animals, for an art judge (item
RIMMANDRAKE_JUDGE_PYRE_ULLAI_HERD_READS_AS_GREY_RUBBLE).

Each sprite is drawn the way RimWorld draws a body graphic: a square of drawSize cells, the 256 px texture
resampled to it. A lying (sleeping, not downed) animal is the same sprite turned 90 degrees
(PawnRenderer.BodyAngle: an animal lying returns West or East by thingIDNumber parity). The ground is a
patch of the real Pyrelands map from the visit-5 walk capture, resampled to the same px per cell.

Numbers and where they come from:
  drawSize: RM_Ullai adult 2.0 (src/RimMandrake/Pyrelands/Defs/ThingDefs_Races/RM_Ullai.xml); Muffalo 3,
  Dromedary 3 (Core Races_Animal_CowGroup.xml); Ostrich 1.8, female tint (133,107,96) (Races_Animal_BigBirds.xml).
  px per cell: 20 is the measured default map zoom of these captures (visit 5 herd_look crop: 866 px over
  44 cells = 19.7; modcheck/play_zoom.py: rootSize 24 = 19.7 px per cell); 48 is a close play zoom.
Untrue to the game: no shadow, no lighting tint, Lanczos instead of the GPU's mip filter.

usage: [ULLAI_DIR=<dir>] python3 compose.py <out_dir> [tag]   (ULLAI_DIR: other ullai textures; vanilla textures from $VANILLA_TEX or the ClaudeWork scratch dump)"""
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, *[".."] * 6))
VAN = os.environ.get("VANILLA_TEX", "/mnt/d/ClaudeWork/rimmandrake/scratch/vanilla_tex/ludeon.rimworld.core")
ULLAI = os.path.join(os.environ.get("ULLAI_DIR") or os.path.join(REPO, "src/RimMandrake/Pyrelands/Textures/Things/Pawn/Animal/Pyrelands/Ullai"), "Ullai_{}.png")
GROUND = os.path.join(REPO, "design/concepts/Pyrelands/version/in_game/visit_5/screenshots/walk_station_creatures.jpg")
GROUND_PPC = 22.0   # walk capture: the 2.0-cell ullai stand ~44 px tall in it (measured on the image)

ANIMALS = [  # (label, path pattern, drawSize, tint or None)
    ("ullai", ULLAI, 2.0, None),
    ("ostrich", os.path.join(VAN, "Ostrich_{}.png"), 1.8, (133, 107, 96)),
    ("dromedary", os.path.join(VAN, "Dromedary_{}.png"), 3.0, None),
    ("muffalo", os.path.join(VAN, "Muffalo_{}.png"), 3.0, None),
]
POSES = [("south", "south", 0), ("east", "east", 0), ("north", "north", 0), ("lying", "east", 90)]


def sprite(path, facing, draw_size, tint, ppc, angle):
    im = Image.open(path.format(facing)).convert("RGBA")
    if tint:
        r, g, b, a = im.split()
        r = r.point(lambda v: v * tint[0] // 255)
        g = g.point(lambda v: v * tint[1] // 255)
        b = b.point(lambda v: v * tint[2] // 255)
        im = Image.merge("RGBA", (r, g, b, a))
    px = max(1, int(round(draw_size * ppc)))
    im = im.resize((px, px), Image.LANCZOS)
    return im.rotate(angle, expand=False) if angle else im


def ground(w, h, ppc):
    g = Image.open(GROUND).convert("RGB")
    crop = g.crop((0, 520, 860, 700))  # grass and ash below the station, no creature in it
    k = ppc / GROUND_PPC
    crop = crop.resize((max(1, int(crop.width * k)), max(1, int(crop.height * k))), Image.LANCZOS)
    out = Image.new("RGB", (w, h))
    for y in range(0, h, crop.height):
        for x in range(0, w, crop.width):
            out.paste(crop, (x, y))
    return out


def panel(ppc):
    cell = int(3.4 * ppc)
    lab = 14
    w, h = cell * len(POSES) + 70, (cell + lab) * len(ANIMALS) + lab
    bg = ground(w, h, ppc)
    d = ImageDraw.Draw(bg)
    for j, (pose, _, _) in enumerate(POSES):
        d.text((70 + j * cell + 4, 1), pose, fill=(255, 255, 255))
    for i, (name, path, ds, tint) in enumerate(ANIMALS):
        y0 = lab + i * (cell + lab)
        d.text((4, y0 + cell // 2), f"{name}\n{ds:g} cells", fill=(255, 255, 255))
        for j, (_, facing, ang) in enumerate(POSES):
            s = sprite(path, facing, ds, tint, ppc, ang)
            x = 70 + j * cell + (cell - s.width) // 2
            bg.paste(s, (x, y0 + (cell - s.height) // 2), s)
    return bg


def main(out, tag=""):
    os.makedirs(out, exist_ok=True)
    for ppc in (20, 48):
        p = os.path.join(out, f"ullai_vs_vanilla_{ppc}ppc{tag}.png")
        panel(ppc).save(p)
        print("WROTE", p)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else HERE, sys.argv[2] if len(sys.argv) > 2 else "")
