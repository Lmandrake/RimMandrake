#!/usr/bin/env python3
"""SUCCULENT_PLANTS_REDRAW_BORROWED_WARDROBE: retire three Textures files that wore another def's picture.

RUT_LungerFry_StandIn.png and RM_NoothelmPlant_StandIn.png were byte copies of RM_Pitchpearl.png (a berry
bush on a fish and on the noothelm); RM_NoothelmPlant_StandIn_south.png was never read (Graphic_Single reads
the bare path). Both defs now point at their own renders, so these slots have no reader. Each retire archives
the bytes in the art store first (artledger.retire). Dry run by default; --apply retires.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(HERE))
import artledger as L  # noqa: E402

REASON = "script:src/RimMandrake/Utils/art/succulent_wardrobe_retire_copies.py"
FILES = [
    "src/RimUtinni/UtinniPatches/Textures/Things/Plant/RUT_LungerFry/RUT_LungerFry_StandIn.png",
    "src/RimMandrake/TerminalBiomes/Textures/Things/Plant/RM_NoothelmPlant/RM_NoothelmPlant_StandIn.png",
    "src/RimMandrake/TerminalBiomes/Textures/Things/Plant/RM_NoothelmPlant/RM_NoothelmPlant_StandIn_south.png",
]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args(argv)
    for rel in FILES:
        f = REPO / rel
        if not a.apply:
            print("would retire" if f.is_file() else "absent", rel)
            continue
        print(L.retire(f, reason=REASON + " copied picture, no reader"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
