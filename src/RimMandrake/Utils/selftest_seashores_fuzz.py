#!/usr/bin/env python3
"""Approach B fuzz of the SeaShores kernel (src/RimMandrake/SeaShores/Source/Kernel/RM_SeaKernel.cs), no game.

Seeded fuzz against brute-force restatements: the terrain -> sea key map (exclusive terrain only, order independent), the sea a tile faces
(most neighbours, lowest ordinal on a tie, order independent), which sea a cell's water is, the empty-band fallback that keeps RUT_TheScald
fishable, the frozen-world healer (exhaustive, with its safety properties), distinct coast directions and the setting / catch predicates.
Built through winbuild.stage_build (dotnet.exe is Windows-native), then run. The older def-typed check is selftest_seashores.py (net472) and
the static / mirror proof is SeaShores/selftest_seashores_proofs.py.

    python3 src/RimMandrake/Utils/selftest_seashores_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only keys|primary|cell|band|heal|coast|gates]

A failing case is shrunk by seed: `family seed N: message`; --fuzz-seed N replays it.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import winbuild  # noqa: E402

MOD = os.path.join(REPO, "src", "RimMandrake", "SeaShores", "Source")
SELFTEST = os.path.join(MOD, "SelfTest", "Fuzz")
CSPROJ = os.path.join(SELFTEST, "RimMandrakeSeaShores.Fuzz.csproj")


def main(argv):
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="SeaShoresFuzz", extra_dirs=[os.path.join(MOD, "Kernel")])
    if rc:
        print("selftest build FAILED")
        return rc
    dll = winbuild.staged_win(rec, SELFTEST) + "\\bin\\Release\\net8.0\\RimMandrakeSeaShores.Fuzz.dll"
    args = [winbuild.dotnet_exe(), dll]
    for i, a in enumerate(argv):
        if a.startswith("--fuzz") and i + 1 < len(argv):
            args += [a, argv[i + 1]]
    return subprocess.run(args, cwd="/mnt/d/Luke/dev").returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
