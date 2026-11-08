#!/usr/bin/env python3
"""The Pyrelands' footprints in ash: the track grid's own print sprites, darkened for ash, installed through the art ledger.

Owner, 2026-11-08: "I don't see any footprints, alas." The CreatureBehaviors track sprites (Textures/Things/Tracks) were made
for pale sand (mean luma 99 human, 58 the rest, alpha 170 at most) and vanish on the ash cover (RM_FE_AshCover x tint 0.48 dry,
0.30 wet). Each is copied with its shape and inner structure kept: RGB x RGB_SCALE, alpha x ALPHA_SCALE (clamped). The
BiomeDef's RM_TrackSurfaceExtension names them; Utils/selftest_pyrelands_track_contrast.py is the check that they read.

Derived art, not through the art pipeline's judging: a placeholder until the owner sees it in game.

    python3 src/RimMandrake/Pyrelands/ash_print_gen.py [--dry]
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
RM = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(RM, "Utils", "art"))

SRC = os.path.join(RM, "CreatureBehaviors", "Textures", "Things", "Tracks")
DST = os.path.join(HERE, "Textures", "Things", "Tracks")
REASON = "script:src/RimMandrake/Pyrelands/ash_print_gen.py"
RGB_SCALE = 0.35
ALPHA_SCALE = 1.4
PAIRS = (("RM_TrackPrint_Human", "RM_AshPrint_Human"), ("RM_TrackPrint_Animal", "RM_AshPrint_Animal"),
         ("RM_TrackPrint_Large", "RM_AshPrint_Large"), ("RM_TrackDrag", "RM_AshDrag"))


def derive(src_png):
    a = np.asarray(Image.open(src_png).convert("RGBA")).astype(np.float64)
    a[..., :3] *= RGB_SCALE
    a[..., 3] *= ALPHA_SCALE
    return Image.fromarray(np.clip(np.round(a), 0, 255).astype(np.uint8), "RGBA")


def main(argv):
    dry = "--dry" in argv
    import artledger
    for src, dst in PAIRS:
        im = derive(os.path.join(SRC, src + ".png"))
        dest = os.path.join(DST, dst + ".png")
        if dry:
            print("would install", dest, im.size)
            continue
        os.makedirs(DST, exist_ok=True)
        r = artledger.install_image(dest, im, reason=REASON)
        print(r.get("status"), dst, im.size)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
