#!/usr/bin/env python3
"""chikka_rehome_art_move.py — move the chikka's owner-kept pictures from SWBestiary to LeaningScrub through the art
ledger (CHIKKA_HOME_DECIDE_NOT_STAR_WARS), then retire the SWBestiary copies.

Owner, by question card 2026-10-24 07:15 PDT: "Where should Chikka live? → Move it now" (the chikka is not a Star Wars
creature; it moves from the Star Wars layer to the franchise-free RimMandrake tier). The defs moved to
src/RimMandrake/LeaningScrub/Defs/ThingDefs_Races/RM_Chikka.xml and .../ThingDefs_Items/RM_ChikkaSupport.xml.

The bytes are copied unchanged, so every owner keep (held by sha) follows the picture: the new slot is installed first,
then the old slot is retired as a duplicate held elsewhere. The body texPath is unchanged (same Textures-relative
path); the meat icon follows its def rename RSW_CactusMeat -> RM_CactusMeat (subject key 'cactusmeat' either way).
git sees each delete+add of identical bytes as a rename, so `git log --follow` keeps the history.

    python3 src/RimMandrake/Utils/art/chikka_rehome_art_move.py [--apply]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(HERE))
import artledger as L  # noqa: E402

BY_CARD = "Where should Chikka live? → Move it now"
SRC = REPO / "src/RimStarWars/SWBestiary/Textures"
DST = REPO / "src/RimMandrake/LeaningScrub/Textures"
REASON = "script:src/RimMandrake/Utils/art/chikka_rehome_art_move.py"
MOVES = [(f"Things/Pawn/Animal/RM_Chikka/RM_Chikka_{f}.png",) * 2 for f in ("east", "north", "south")] + [
    ("Things/Item/Resource/RSW_CactusMeat.png", "Things/Item/Resource/RM_CactusMeat.png")]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args(argv)
    bad = 0
    for old_rel, new_rel in MOVES:
        f, dest = SRC / old_rel, DST / new_rel
        if not f.is_file():
            same = dest.is_file()
            print(f"{'ALREADY MOVED' if same else 'MISSING'} {old_rel}")
            bad += 0 if same else 1
            continue
        data = f.read_bytes()
        if dest.exists() and dest.read_bytes() != data:
            print(f"CLASH {new_rel}")
            bad += 1
            continue
        if a.apply:
            if not dest.exists():
                L.install_bytes(dest, data, reason=REASON,
                                provenance={"kind": "move", "from": str(f.relative_to(REPO)), "by_card": BY_CARD})
            L.retire(f, reason=REASON + " moved to LeaningScrub")
        print(f"{'MOVED' if a.apply else 'WOULD MOVE'} {old_rel} -> LeaningScrub/{new_rel}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
