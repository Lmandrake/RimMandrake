# PIT_DEPTH_DRAW_OFFSET_1 — Pawns visibly sink and rise with canal depth; superdeep walls 20% above the head

Part of the pit collapse (`PIT_SUPERDEEP_COLLAPSE_1` carries the rulings; `design/RimMandrake/flowworks_pits_unified_model_2026-10-02.md` is the one model). A pit is a canal cell dug to SUPERDEEP (D=4) and nothing else.

## spec
His ruling: *"The pawn should visibly rise up and lower down as they move over the depths… the walls are higher than their head by 20%"*. A pawn's vertical draw offset varies with the D of its cell; at D=4 the wall art rises 20% above the occupant's head. Code (render), not art. Applies to fluid occupants too (`slime_occupant_below_surface`).

## verify
Frame + state: a pawn walked across D=0→4 shows a monotonic offset by D (state read of the offset), and a D=4 frame measures wall top ≥ 1.2× head height.

## criteria
`pawn_height_ladder_legible`, `pawn_lowers_on_deeper_cell`, `pawn_rises_on_shallower_cell`, `pit_trapped_reads_as_trapped` have something to judge.

## depends
`SUPERDEEP_HOLDER_RETIRE_1` (occupants must be spawned to be drawn). Wall art: `EXCAVATION_WALL_ART_1`.

## northstar
State component reads the draw offset per D (a companion `[Tool]`), so the bars are not frame-only.
