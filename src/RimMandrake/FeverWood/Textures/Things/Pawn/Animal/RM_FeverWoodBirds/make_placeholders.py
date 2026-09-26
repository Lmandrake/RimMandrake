#!/usr/bin/env python3
"""FEVERWOOD_ALIEN_BIRD_CHORUS_1 placeholder art.

Generates flat-colour, fully-opaque 128x128 RGBA PNGs for the four crown
birds, one colour per species, _south/_east/_north facings (Graphic_Multi
mirrors west from east) -- same posture as this biome's own
RM_Vaulm/RM_Ollareth/RM_Drommath/RM_Sekkulaath_Juvenile placeholders.
Registry.jsonl shows every real artpipe attempt for these four (queued
under FEVERWOOD_RM_MOD_BUILD_1) has failed and _artsrc/ is empty, so this
is not a duplicate job -- it is what ships until the generator succeeds.
Real bespoke art (membranous/hairy/strange brief) is owed to the standing
art pipeline. Run from repo root: python3 <this file>.
"""
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent

SPECIES = {
    "RM_Chellow": (196, 150, 90, 255),     # warm lamp-glow tan (throat-fan)
    "RM_Murrelith": (200, 210, 220, 255),  # pale translucent ribbon-blue
    "RM_Thavrik": (120, 95, 70, 255),      # coarse furred brown
    "RM_Skellick": (110, 120, 95, 255),    # mottled crumpled grey-green
}

FACINGS = ("south", "east", "north")

for name, color in SPECIES.items():
    im = Image.new("RGBA", (128, 128), color)
    for facing in FACINGS:
        out = HERE / f"{name}_{facing}.png"
        im.save(out)
        print("wrote", out)
