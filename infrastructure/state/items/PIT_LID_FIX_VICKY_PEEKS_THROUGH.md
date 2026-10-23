# PIT_LID_FIX_VICKY_PEEKS_THROUGH

Owner, 2026-10-22, walk: *"Vicky standing "beneath" a covered pit just gets a funny dark square around her but
otherwise is still "over" the cover."* Screenshot (pinned):
`Transient/pile_2026-10-22/walk_owner_shots/20261022184503_s.jpg` — concealed pit at centre, Vicky in a covered
cell, drawn over the lid with the pit-depth dark square behind her.

Ruling it builds on: PIT_COVER_FIX_OCCUPANT_STAYS_BELOW (card 2026-10-21 "Stays below, hidden"); covered cells are
walkable floor (card 2026-10-22).

## Watch out
A pawn walking ON the lid (surface) must still draw normally; only a pawn down in the pit under the lid hides.

## Cause (found 2026-10-22, BENCH helper)
Vicky was a WALKER on the lid (the C12 walk orders her across the planks; beneath-set pawns were already hidden by the
deployed DLL, so she was not one). `RM_SuspensionUnderpass.DrawDepth` handled only suspension decks ("Covers keep their
old read"), so on a pit lid the sink read the hole's full depth: drawn sunk toward the D floor, ground shadow skipped, and
`RM_PitLipOcclusion` drew lip-ground squares round her (the "funny dark square") — all above the lid's ground print.

## Decision (delegated: render detail)
Per the cards: covered = floor, so a walker on a lid is drawn at the lid's walking height (ground, no sink, no shadow
skip, no lip squares); a pawn beneath a lid (PIT_COVER_FIX_OCCUPANT_STAYS_BELOW) keeps the hole's depth and is not drawn.
A lid square is also the near lip for a pawn in an open part of the same pit, drawn in the ground the lid prints.

## criteria
- A1 L0: FlowWorks builds; SelfTest `LidWalker_drawn_at_ground_not_sunk` and `Beneath_wired_at_the_call_sites` pass; validation_v2 O-LIVE-NEG green with faults `lid_walker_sunk` -> X8c red and `beneath_drawn` -> X8b red.
- A2 L1: validation_v2 live X8c_lid_walker_drawn_at_ground PASS (a colonist on the laid lid: beneath/hidden False, sink 0, drawDz ~0) and X8b PASS with drawPatch=True, hidden=True.
- A3 L2: on C12 a colonist walking the planks reads "On the floor": no dark square, shadow shown, not sunk; a colonist under a lid is not seen at all.
