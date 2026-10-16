#!/usr/bin/env python3
"""Contagion offline preflight for the biomes_sprint round (kickoff packet §1 M1/M2). Thin wrapper: every row lives in
src/RimMandrake/Utils/northstar_driver/biome_preflight.py. Offline only -- no bridge, no game, no ModsConfig.

    python3 src/RimMandrake/Contagion/preflight_contagion.py [--json OUT] [--allow-unmeasured] [--rows O-TEX,O-SUITE]
The LIVE preflight (map, settings defaults, storyteller) is northstar_site.preflight, run by the driver."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Utils"))
from northstar_driver import biome_preflight  # noqa: E402

BIOME = "Contagion"

if __name__ == "__main__":
    sys.exit(biome_preflight.main(BIOME))
