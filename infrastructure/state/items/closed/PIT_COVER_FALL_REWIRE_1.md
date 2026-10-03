# PIT_COVER_FALL_REWIRE_1 — Pit cover rehoused: multi-cell terrain-mimic cover that drops pawns into a superdeep cell

Part of the pit collapse (`PIT_SUPERDEEP_COLLAPSE_1` carries the rulings; `design/RimMandrake/flowworks_pits_unified_model_2026-10-02.md` is the one model). A pit is a canal cell dug to SUPERDEEP (D=4) and nothing else.

## spec
- A cover Thing over one or more D=4 cells, drawn with `TerrainMimicPrinter` (kept), with `CompPitCoverTrigger` summing mass over **the cover's cells** every 30 ticks.
- On trigger the cover gives way and the pawns on it **descend** (the holder-retire item's descent event: fall damage, then spikes). No despawn.
- Cover tiers unchanged: `PitCoverTier` 40/120/220 kg (220 is his number). Own-faction carve-out stays a setting.

## verify
Bridge: a hostile heavier than the tier's threshold walking onto a covered pit ends spawned on the D=4 cell with fall damage; a lighter one does not trigger; the cover is gone or shows sprung.

## criteria
`pit_covered_invisible` and `pit_covered_seam_at_max_zoom` have a real cover to look at.

## depends
`SUPERDEEP_HOLDER_RETIRE_1`, `PIT_LEGACY_CODE_RETIRE_1`.

## northstar
State component: trigger mass vs tier threshold, pawn position/D after trigger. The seam bar stays a frame-judged bar.
