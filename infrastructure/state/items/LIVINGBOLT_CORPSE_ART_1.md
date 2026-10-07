# LIVINGBOLT_CORPSE_ART_1

## What
`RM_LivingBolt` (RustCathedral) has no corpse render. Its PawnKindDef named
`Things/Pawn/Animal/RM_LivingBolt/RM_LivingBoltCorpse` with no PNGs behind it; on death
`PawnRenderNode_AnimalPart` swaps to `corpseGraphicData`, so a dead bolt drew magenta.
Searched 2026-10-07: no file in `src/`, no artpipe job (`artpipe_state.py find livingbolt corpse`),
no ruling in `infrastructure/state/art_rulings/`.

## Done so far
`corpseGraphicData` removed, so a dead bolt draws its body graphic (vanilla behaviour for a
kind with no corpse art). No magenta.

## Owed
A dedicated "spent/stilled bolt" corpse render, briefed against the redo body art the owner
asked for (RUSTCATHEDRAL_SHEET_ART_REDO_1: "a large chrome nut with a bolthead above"), so
it should wait for that redo to be ruled. Install through `art install`, then restore
`corpseGraphicData` (Graphic_Multi, drawSize 0.1) pointing at it.
