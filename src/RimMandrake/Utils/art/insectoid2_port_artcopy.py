#!/usr/bin/env python3
"""insectoid2_port_artcopy.py - one-off (2026-10-18, insectoid2 donor retirement): copy the two redraws the game
showed on VFE Insectoids 2 creatures (UtinniPatches Swarmling ArtFold, UtinniPatches same-path Megathrips) to the
own paths of their RM_ twins, RM_Saluksis (Greentide) and RM_Kasselith (FeverWood), through the art ledger."""
import sys
from pathlib import Path
R=Path("/home/mandrake/rm/foundry")
sys.path.insert(0,str(R/"src/RimMandrake/Utils/art"))
from artwrite import TextureWriter
tw=TextureWriter(__file__,provenance={"kind":"copy","note":"insectoid2 donor retirement 2026-10-18: our redraw moved to the RM_ twin's own path"},quiet=False)
U=R/"src/RimUtinni/UtinniPatches/Textures"
jobs=[(U/"RimUtinni/UtinniPatches/Swarmling/Swarmling", R/"src/RimMandrake/Greentide/Textures/Things/Pawn/Animal/RM_Saluksis/RM_Saluksis"),
      (U/"Things/Pawn/Animal/Megathrips/Megathrips", R/"src/RimMandrake/FeverWood/Textures/Things/Pawn/Animal/RM_Kasselith/RM_Kasselith")]
for s,d in jobs:
    for f in ("_east","_north","_south"):
        tw.copy(str(s)+f+".png", str(d)+f+".png")
print(tw.counts); sys.exit(tw.report())
