#!/usr/bin/env python3
"""Mutation proof for the GravshipLanding fuzz: plants each defect in the production kernel, runs the fuzz wrapper, demands a FAIL,
restores the file byte-identical (engine: mutate_explosivegrowth_fuzz.run_mutations).

    python3 src/RimMandrake/Utils/mutate_gravshiplanding_fuzz.py [name-substring]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mutate_explosivegrowth_fuzz import run_mutations  # noqa: E402

MUTATIONS = [
    ("gate: Odyssey not required", "return odysseyActive && arrivalMap && settingOn;", "return arrivalMap && settingOn;"),
    ("gate: any map, not only arrivals", "return odysseyActive && arrivalMap && settingOn;", "return odysseyActive && settingOn;"),
    ("gate: setting ignored", "return odysseyActive && arrivalMap && settingOn;", "return odysseyActive && arrivalMap;"),
    ("root: roofed cells seed floods", "return inBounds && fogged && !roofed && !blocksFog;", "return inBounds && fogged && !blocksFog;"),
    ("root: unfogged cells re-flooded", "return inBounds && fogged && !roofed && !blocksFog;", "return inBounds && !roofed && !blocksFog;"),
    ("root: fog-making edifice seeds a flood", "return inBounds && fogged && !roofed && !blocksFog;", "return inBounds && fogged && !roofed;"),
    ("root: bounds ignored", "return inBounds && fogged && !roofed && !blocksFog;", "return fogged && !roofed && !blocksFog;"),
    ("walk skips the last row", "z < minZ + height;", "z < minZ + height - 1;"),
    ("walk skips the last column", "x < minX + width;", "x < minX + width - 1;"),
    ("walk starts one cell late", "for (int x = minX; x < minX + width; x++)", "for (int x = minX + 1; x < minX + width; x++)"),
    ("bounds check dropped", "if (!inb) continue;", ""),
    ("roots not counted", "w.FloodUnfog(x, z);\n                    roots++;", "w.FloodUnfog(x, z);"),
    ("roots counted twice", "w.FloodUnfog(x, z);\n                    roots++;", "w.FloodUnfog(x, z);\n                    roots += 2;"),
]

if __name__ == "__main__":
    sys.exit(run_mutations("src/RimMandrake/GravshipLanding/Source/Kernel/RM_LandingKernel.cs",
                           "selftest_gravshiplanding_fuzz.py", MUTATIONS, sys.argv[1] if len(sys.argv) > 1 else None))
