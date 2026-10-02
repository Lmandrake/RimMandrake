# CANAL_BOTTOM_SPIKES_1 — Spikes as per-cell hardware on a superdeep canal bottom (RM_Spikes)

Part of the pit collapse (`PIT_SUPERDEEP_COLLAPSE_1` carries the rulings; `design/RimMandrake/flowworks_pits_unified_model_2026-10-02.md` is the one model). A pit is a canal cell dug to SUPERDEEP (D=4) and nothing else.

## spec
- `RM_Spikes` ThingDef + `PlaceWorker_SpikesOnExcavation` + `RM_SpikeUtility.HasSpikes(map, cell)`, mirroring the ladder's shape. Placement: **D=4 only** (DEFAULT — owner question on spike depth may widen it).
- Fires on **any descent** into that cell ([G]); never on walking up to it, never on moving between two D=4 cells.
- Massive **Sharp** damage through the normal pipeline (armour applies; no instant death), **proportional to BodySize**. Propose the number with the reasoning shown and get his word; start from the old `spikeDamage = 25f` Stab only as a reference point.
- Art must show *some* spike at the pit's viewing angle; never `TrapSpikeArmed`.
- Mod Settings toggle + damage multiplier.

## verify
Bridge: a pawn descending into a spiked D=4 cell takes Sharp injuries scaled with body size (two sizes compared); a pawn moving along a spiked D=4 floor from a D=4 neighbour takes none; a pawn standing at the lip takes none.

## criteria
Spikes are a buildable on a canal bottom, with a cell scope, and no other "fitting" exists.

## depends
`SUPERDEEP_HOLDER_RETIRE_1` (descent event).

## northstar
State component: injuries by damage def after a forced descent; a twin cell without spikes shows only blunt fall damage. Bar `spikes_read_distinct` stays art-gated.
