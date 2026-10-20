#!/usr/bin/env python3
"""rhossak_art.py — give RM_Rhossak and RM_GalledRhossak (RimMandrake: Cauldron) their own copy of the art the owner picked.

    python3 src/RimMandrake/Utils/art/rhossak_art.py            dry run
    python3 src/RimMandrake/Utils/art/rhossak_art.py --apply

RHOSSAK_MIGRATE_ROOTS_TAKE_HOLD (owner by card 2026-10-19: "Make them animals and make them bind."). The two creatures were Alpha
Memes dryads (AM_Dryad_Corruptor / AM_Dryad_Tumorous) whose art the owner ruled "art is good" on the Cauldron sheet
(2026-10-09, pick B each); those picks live in the UtinniPatches art fold. The Cauldron is the RimMandrake tier and may not
draw a RimUtinni texture path, so the same pictures are copied into the Cauldron's own Textures through the art ledger.
No picture is new or altered (no cosmetic change). The dessicated bodies are vanilla Ideology dryad pictures (every DLC
is assumed), so nothing is copied for them.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(HERE))
from artwrite import TextureWriter  # noqa: E402

FOLD = REPO / "src/RimUtinni/UtinniPatches/Textures/RimUtinni/UtinniPatches"
DEST = REPO / "src/RimMandrake/Cauldron/Textures/Things/Pawn/Animal"
PAIRS = (("DryadCorruptor", "AM_Dryad_Corruptor", "RM_Rhossak"),
         ("DryadTumorous", "AM_Dryad_Tumorous", "RM_GalledRhossak"))
WHY = "owner-picked art (Cauldron sheet 2026-10-09, pick B) copied for our own def; RHOSSAK_MIGRATE_ROOTS_TAKE_HOLD"


def main() -> int:
    do = "--apply" in sys.argv
    refusals, counts = [], []
    for folder, donor, ours in PAIRS:
        tw = TextureWriter(__file__, dry_run=not do, provenance={
            "kind": "derived", "from": str((FOLD / folder).relative_to(REPO)), "donor_pkg": "sarg.alphamemes",
            "orig_texpath": f"Things/Pawn/Animal/{donor}/{donor}", "why": WHY})
        for f in ("east", "north", "south"):
            tw.copy(FOLD / folder / f"{donor}_{f}.png", DEST / ours / f"{ours}_{f}.png")
        counts.append(f"{ours}={tw.counts}")
        refusals += tw.refusals
    print(f"{'APPLIED' if do else 'DRY'} " + " ".join(counts))
    for r in refusals:
        print("   REFUSED", r)
    return 1 if refusals else 0


if __name__ == "__main__":
    raise SystemExit(main())
