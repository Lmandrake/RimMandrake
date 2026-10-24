#!/usr/bin/env python3
"""swb_rm_rehome_art_move.py — move the pictures of non-Star-Wars ports from SWBestiary to the franchise-free
RimMandrake tier through the art ledger (SWB_RM_FAUNA_DECIDE_HOME_LIKE_CHIKKA), then retire the SWBestiary copies.

Owner 2026-10-24 ~07:40 PDT: "Yes, it appears that a lot of alpha animal ports got classified as Star Wars. We should
move all of those. Durrok and Mullgoth and Vura do need moving out of Star Wars, yes."  Same playbook as the chikka
(chikka_rehome_art_move.py): the defs move to an RM_ biome mod, the bytes are copied unchanged so every owner keep
(held by sha) follows the picture; the new slot is installed first, then the old slot is retired as a duplicate held
elsewhere. Identical bytes delete+add, so git sees a rename and `git log --follow` keeps the history.

Each batch maps a SWBestiary texture folder (Textures-relative) to its destination mod and, for a defName rename
RSW_X -> RM_X, the new folder; every PNG in the folder moves, with the old folder name in its filename rewritten.

    python3 src/RimMandrake/Utils/art/swb_rm_rehome_art_move.py --batch 1 [--apply]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(HERE))
import artledger as L  # noqa: E402

OWNER_SAID = ("Yes, it appears that a lot of alpha animal ports got classified as Star Wars. We should move all of "
              "those. Durrok and Mullgoth and Vura do need moving out of Star Wars, yes.")
SRC = REPO / "src/RimStarWars/SWBestiary/Textures"
REASON = "script:src/RimMandrake/Utils/art/swb_rm_rehome_art_move.py"
ANIMAL = "Things/Pawn/Animal"

# batch -> [(old folder, destination mod folder under src/RimMandrake, new folder)]
BATCHES = {
    "1": [(f"{ANIMAL}/RM_Durrok", "LeaningScrub", f"{ANIMAL}/RM_Durrok"),
          (f"{ANIMAL}/RM_Mullgoth", "LeaningScrub", f"{ANIMAL}/RM_Mullgoth"),
          (f"{ANIMAL}/RM_Vurra", "LeaningScrub", f"{ANIMAL}/RM_Vurra")],
    # run 2: defName renames RSW_X -> RM_X, so the folder and filename stems follow
    "2": [(f"{ANIMAL}/RSW_Ikee", "Stillsand", f"{ANIMAL}/RM_Ikee"),
          ("swanimals/Korrum", "Scarlands", f"{ANIMAL}/RM_Korrum")],
}


def moves(batch: str):
    for old_dir, mod, new_dir in BATCHES[batch]:
        old_stem, new_stem = old_dir.rsplit("/", 1)[1], new_dir.rsplit("/", 1)[1]
        dst_root = REPO / "src/RimMandrake" / mod / "Textures"
        src_dir = SRC / old_dir
        dst_dir = dst_root / new_dir
        names = sorted({p.name for p in src_dir.glob("*.png")} if src_dir.is_dir() else set())
        if not names and dst_dir.is_dir():
            names = sorted(p.name for p in dst_dir.glob("*.png"))  # already moved: report, do nothing
        if not names:
            yield None, None, f"{old_dir} (no PNGs at source or destination)"
        for n in names:
            yield src_dir / n, dst_dir / n.replace(old_stem, new_stem, 1), f"{mod}/{new_dir}/{n.replace(old_stem, new_stem, 1)}"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", required=True, choices=sorted(BATCHES))
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args(argv)
    bad = 0
    for f, dest, label in moves(a.batch):
        if f is None:
            print(f"MISSING {label}")
            bad += 1
            continue
        if not f.is_file():
            same = dest.is_file()
            print(f"{'ALREADY MOVED' if same else 'MISSING'} {f.relative_to(REPO)}")
            bad += 0 if same else 1
            continue
        data = f.read_bytes()
        if dest.exists() and dest.read_bytes() != data:
            print(f"CLASH {label}")
            bad += 1
            continue
        if a.apply:
            if not dest.exists():
                L.install_bytes(dest, data, reason=REASON,
                                provenance={"kind": "move", "from": str(f.relative_to(REPO)), "owner_said": OWNER_SAID})
            L.retire(f, reason=REASON + " moved to the RimMandrake tier")
        print(f"{'MOVED' if a.apply else 'WOULD MOVE'} {f.relative_to(SRC)} -> {label}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
