#!/usr/bin/env python3
"""garsulix_standin.py — install RM_Garsulix's stand-in art into the Cauldron member (owner, 2026-10-18: "Just put in
placeholder art for now or donor copies and retire these mods!!! Just get it done.").

    python3 src/RimMandrake/Utils/art/garsulix_standin.py            dry run
    python3 src/RimMandrake/Utils/art/garsulix_standin.py --apply

RM_Garsulix is our port of vanillaexpanded.vgeneticse's GR_Beetlefleet (an Alpha-Animals-compat def that dies with
sarg.alphaanimals). Body: the redraw the owner picked on the Cauldron sheet (pick B; B's north was ✕'d "needs regen",
so only east+south exist and Graphic_Multi draws south for north), copied from the UtinniPatches art fold. Dessicated:
the donor's own picture. Both land under Textures/StandIn/<donor texPath> through the art ledger, standin=true, so a
regenerated render replaces them through `art install`.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(HERE))
from artwrite import TextureWriter  # noqa: E402

DONOR = Path("/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/2801160906/Textures")
ORIG = "Things/Pawn/Animal/AlphaAnimals/Insectoid"
FOLD = REPO / "src/RimUtinni/UtinniPatches/Textures/RimUtinni/UtinniPatches/Beetlefleet"
DEST = REPO / "src/RimMandrake/Cauldron/Textures/StandIn" / ORIG
WHY = "donor-retirement stand-in until regenerated (owner 2026-10-18)"


def main() -> int:
    do = "--apply" in sys.argv
    body = TextureWriter(__file__, dry_run=not do, provenance={
        "kind": "derived", "from": str(FOLD.relative_to(REPO)), "donor_pkg": "vanillaexpanded.vgeneticse",
        "standin": True, "orig_texpath": f"{ORIG}/GR_Beetlefleet", "why": WHY + "; owner-picked redraw (sheet pick B)"})
    for f in ("east", "south"):
        body.copy(FOLD / f"GR_Beetlefleet_{f}.png", DEST / f"GR_Beetlefleet_{f}.png")
    dess = TextureWriter(__file__, dry_run=not do, provenance={
        "kind": "donor", "donor_pkg": "vanillaexpanded.vgeneticse", "standin": True,
        "orig_texpath": f"{ORIG}/GR_Dessicated_Beetlefleet", "why": WHY})
    dess.copy(DONOR / ORIG / "GR_Dessicated_Beetlefleet_east.png", DEST / "GR_Dessicated_Beetlefleet_east.png")
    print(f"{'APPLIED' if do else 'DRY'} body={body.counts} dessicated={dess.counts}")
    for r in body.refusals + dess.refusals:
        print("   REFUSED", r)
    return 1 if (body.refusals or dess.refusals) else 0


if __name__ == "__main__":
    raise SystemExit(main())
