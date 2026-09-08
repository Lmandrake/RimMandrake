#!/usr/bin/env python3
"""Composite the MenuShell background PNGs: letterbox the pantheon slide and
each of the nine god icons onto a 2560x1440 indigo-black canvas, no upscaling.
Per ui_appearance_spec.md section 2 and UI_APPEARANCE_BUILD_1's letterbox route.
"""
from PIL import Image
import os

REPO = "/mnt/d/Luke/dev/Rimworld"
ART = os.path.join(REPO, "design/Jawa/art")
OUT = os.path.join(REPO, "src/RimUtinni/MenuShell/Textures/RimUtinni/MenuShell")
FALLBACK_OUT = os.path.join(REPO, "src/RimUtinni/MenuShell/Textures/UI/HeroArt")

CANVAS = (2560, 1440)
INDIGO_BLACK = (18, 16, 22)

GODS = [
    ("god1_ishko.png", "BG_God_Ishko.png"),
    ("god2_ohm.png", "BG_God_Ohm.png"),
    ("god3_oomo.png", "BG_God_Oomo.png"),
    ("god4_mobunloo.png", "BG_God_Mobunloo.png"),
    ("god5_rekko.png", "BG_God_Rekko.png"),
    ("god6_tabaa.png", "BG_God_Tabaa.png"),
    ("god7_zizzik.png", "BG_God_Zizzik.png"),
    ("god8_shkaar.png", "BG_God_Shkaar.png"),
    ("god9_ozzik.png", "BG_God_Ozzik.png"),
]


def letterbox(src_path, dst_path):
    im = Image.open(src_path).convert("RGB")
    canvas = Image.new("RGB", CANVAS, INDIGO_BLACK)
    x = (CANVAS[0] - im.width) // 2
    y = (CANVAS[1] - im.height) // 2
    canvas.paste(im, (x, y))
    canvas.save(dst_path)
    print(f"{dst_path}: {im.size} centered on {CANVAS} at ({x},{y})")


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(FALLBACK_OUT, exist_ok=True)

    pantheon_src = os.path.join(ART, "pantheon_slide.png")
    pantheon_dst = os.path.join(OUT, "BG_PantheonSlide.png")
    letterbox(pantheon_src, pantheon_dst)

    for src_name, dst_name in GODS:
        letterbox(os.path.join(ART, "gods", src_name), os.path.join(OUT, dst_name))

    # Tier-1 fallback: same pantheon composite at Core's own planet-background path.
    fallback_dst = os.path.join(FALLBACK_OUT, "BGPlanet.png")
    Image.open(pantheon_dst).save(fallback_dst)
    print(f"{fallback_dst}: fallback copy written")


if __name__ == "__main__":
    main()
