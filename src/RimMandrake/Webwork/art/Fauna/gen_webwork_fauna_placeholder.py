#!/usr/bin/env python3
"""WEBWORK_FAUNA_ROSTER_1 — flat-colour placeholder art for the 5 invented
Webwork fauna (quarrok/vennick/skennet/cravvet/sivvern).

⚠️ THIS IS A PLACEHOLDER AND IS MEANT TO BE REPLACED. It exists so none of the
five renders magenta and so the defs can be loaded/tested, not because a
filled ellipse is shipping-quality RimWorld art. Real art is OWED — see
infrastructure/artpipe/art_lists/webwork_fauna.csv, filed this same pass
(0 hits for all 5 names in registry.jsonl/done/_artsrc at authoring time,
sanity-probed against "graniteslug"/"korrum" per confident-wrong-numbers).
When real art lands, delete this script with the PNGs it made.

Same flat-fill-plus-outline shape as the sibling flora roster's own
placeholders (e.g. Textures/Things/Plant/RM_Fellome/RM_Fellome_a.png — 3
distinct colours: transparent, fill, outline) — deliberately not the
ScrapNest-style procedural texture, since these are animal SILHOUETTES read
at a glance (roster doc §6's own legibility matrix), not a scattered building.

One simple silhouette per creature, oriented per facing (south/east/north;
west is engine-mirrored from east, standard RimWorld convention — no west
file needed). Canvas 256x256, matching the sibling roster's own placeholder
size and the queued art job's canvas_w/h.

    python3 src/RimMandrake/Webwork/art/Fauna/gen_webwork_fauna_placeholder.py
"""

import os

from PIL import Image, ImageDraw

SIZE = 256
TEX_ROOT = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..",
    "Textures", "Things", "Pawn", "Animal",
))

# (defName, fill, outline, aspect w/h of the body ellipse as a fraction of
# canvas, per the roster doc's own silhouette FORM line)
CREATURES = [
    # broad low-slung beetle, mandibles wider than its head
    ("RM_Quarrok", (58, 46, 30, 255), (20, 16, 10, 255), 0.78, 0.42),
    # fist-sized dot with legs, pale grey / bone-white back
    ("RM_Vennick", (196, 192, 186, 255), (90, 88, 84, 255), 0.30, 0.26),
    # long-legged pale runner, neck low
    ("RM_Skennet", (214, 204, 184, 255), (110, 100, 84, 255), 0.34, 0.62),
    # squat domed sheller, mud-dark
    ("RM_Cravvet", (74, 62, 46, 255), (30, 24, 16, 255), 0.56, 0.48),
    # narrow swept crescent, membranous grey
    ("RM_Sivvern", (150, 150, 158, 255), (70, 70, 78, 255), 0.82, 0.30),
]


def draw_facing(fill, outline, aw, ah, facing: str) -> Image.Image:
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = cy = SIZE / 2.0
    w = SIZE * aw
    h = SIZE * ah

    # A cheap facing cue: east/north nudge and squash the body slightly so
    # the three files are not byte-identical, matching the "reads from a
    # top-down sprite" brief just enough to tell facings apart at a glance.
    if facing == "east":
        w *= 0.85
        cx += SIZE * 0.04
    elif facing == "north":
        h *= 0.92
        cy -= SIZE * 0.03

    box = [cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2]
    d.ellipse(box, fill=fill, outline=outline, width=4)

    # A small directional nose/head blob so "which way is it facing" reads
    # even on a flat placeholder.
    head_r = min(w, h) * 0.16
    if facing == "south":
        hx, hy = cx, cy + h / 2 - head_r * 0.6
    elif facing == "north":
        hx, hy = cx, cy - h / 2 + head_r * 0.6
    else:  # east
        hx, hy = cx + w / 2 - head_r * 0.6, cy
    d.ellipse([hx - head_r, hy - head_r, hx + head_r, hy + head_r],
              fill=outline)

    return img


def main() -> None:
    for name, fill, outline, aw, ah in CREATURES:
        out_dir = os.path.join(TEX_ROOT, name)
        os.makedirs(out_dir, exist_ok=True)
        for facing in ("south", "east", "north"):
            path = os.path.join(out_dir, f"{name}_{facing}.png")
            draw_facing(fill, outline, aw, ah, facing).save(path)
            print("wrote", path)


if __name__ == "__main__":
    main()
