#!/usr/bin/env python3
"""floodedcanyon_kept_art_move.py — move the owner-kept Cracked Lands pictures out of the old FloodedCanyon stub
into src/RimMandrake/CrackedLands at the same Textures-relative path (CRACKEDLANDS_FULL_RENAME_1), through the art
ledger, then retire the stub copies. Both folders compose into mandrake.rm.biomes, so every texPath resolves the same.

Owner, typed 2026-10-18 (relayed by the FOUNDRY coordinator): "Yes. Simply accept all art as currently rendered to get
this done. We will re review at a later time. No more art blockers." — the authorization to release the keep guard
for this move.

    python3 src/RimMandrake/Utils/art/floodedcanyon_kept_art_move.py [--apply]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(HERE))
import artledger as L  # noqa: E402

OWNER = ("Yes. Simply accept all art as currently rendered to get this done. We will re review at a later time. "
         "No more art blockers.")
SRC = REPO / "src/RimMandrake/FloodedCanyon/Textures"
DST = REPO / "src/RimMandrake/CrackedLands/Textures"
REASON = "script:src/RimMandrake/Utils/art/floodedcanyon_kept_art_move.py"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args(argv)
    bad = 0
    for f in sorted(SRC.rglob("*.png")):
        rel = f.relative_to(SRC)
        dest = DST / rel
        if dest.exists():
            same = dest.read_bytes() == f.read_bytes()
            print(f"{'SAME' if same else 'CLASH'} {rel}")
            if not same:
                bad += 1
                continue
        elif a.apply:
            L.install_bytes(dest, f.read_bytes(), reason=REASON,
                            provenance={"kind": "move", "from": str(f.relative_to(REPO)), "owner_said": OWNER})
        if a.apply:
            L.retire(f, reason=REASON + " moved to CrackedLands", owner_said=OWNER)
        print(f"{'MOVED' if a.apply else 'WOULD MOVE'} {rel}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
