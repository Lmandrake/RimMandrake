#!/usr/bin/env python3
"""ExplosiveGrowth offline preflight for the biomes_sprint round (kickoff packet §1.4, shared lines M1/M2). Thin wrapper
over src/RimMandrake/Utils/northstar_driver/biome_preflight.py. ExplosiveGrowth is a composed member of Baroque Biomes,
not a biome: it has no BiomeDef roster, so O-ROSTER and O-TEX do not apply and are left out of the default rows.
Offline only -- no bridge, no game, no ModsConfig.
    python3 src/RimMandrake/ExplosiveGrowth/preflight_explosivegrowth.py [--json OUT] [--allow-unmeasured] [--rows ...]"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Utils"))
from northstar_driver import biome_preflight  # noqa: E402

BIOME = "ExplosiveGrowth"
ROWS = "O-TIER,O-PLAN,O-DEPLOY,O-SUITE,O-MANIFEST,O-SITE"

if __name__ == "__main__":
    argv = sys.argv[1:]
    if "--rows" not in argv:
        argv += ["--rows", ROWS]
    sys.exit(biome_preflight.main(BIOME, argv))
