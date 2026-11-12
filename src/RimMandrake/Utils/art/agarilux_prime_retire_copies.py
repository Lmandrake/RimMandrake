#!/usr/bin/env python3
"""AGARILUX_PRIME_COPIES_RECONCILE_SPLIT: retire the two Textures files at RM_AgariluxPrime's old donor slot.

RM_AgariluxPrime (grath elder) draws RotSpecies/AgariluxPrime, TheRot's v3 render (owner-approved 2026-09-20; the
2026-11-02 live def dump reads that texPath). Its base def used to name the Alpha Biomes slot
Things/Plants/AB_AgariluxPrime and a TheRot patch repointed it, so two of our mods shipped a picture at that slot that
nothing drew: TheRot's donor-regen render (2026-10-19) and UtinniPatches' 2026-09-13 render. Alpha Biomes is retired
(AB_AgariluxPrime is in no live dump), so the slot has no reader. The base def now names RotSpecies/AgariluxPrime and
the repoint is gone. Each retire archives the bytes in the art store first (artledger.retire). Dry run by default;
--apply retires.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(HERE))
import artledger as L  # noqa: E402

REASON = "script:src/RimMandrake/Utils/art/agarilux_prime_retire_copies.py"
FILES = [
    "src/RimMandrake/TheRot/Textures/Things/Plants/AB_AgariluxPrime.png",
    "src/RimUtinni/UtinniPatches/Textures/Things/Plants/AB_AgariluxPrime.png",
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
        print(L.retire(f, reason=REASON + " shadowed donor-slot copy, no reader"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
