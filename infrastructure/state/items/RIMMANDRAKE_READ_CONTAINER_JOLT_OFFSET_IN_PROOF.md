# RIMMANDRAKE_READ_CONTAINER_JOLT_OFFSET_IN_PROOF

## spec

Explosive Knockback, sc_closed_containers (`design/concepts/ExplosiveKnockback/scenes.json`) expects "a drawn offset above
zero on at least one tick in the thing trace" for each jolted container. The jolt is drawn since steward decision 6 of
blind cycle 2 (587529cee1; `RM_MapComponent_Knockback.cs` MapComponentUpdate, `RM_KnockbackMath.JoltOffset`), so 0.1.0
owes this row (journal question 13, answered 2026-11-15 11:45 AM PST under the Evidence-for-Ask ruling).

The scene still prints `drawnOffset=UNMEASURED` for every jolt row (`RM_KnockbackProof_StageThree.cs`, the jolt rows'
`rows.Add(...)`). The only instrument is `RM_MapComponent_Knockback.JoltFrames` / `JoltMaxOffset`: map-wide statics,
updated per drawn frame, not per container or per tick.

Build: a per-container read (container id -> max drawn offset while its jolt lasts) the proof can read for each row, and
replace `drawnOffset=UNMEASURED` with the measured value; the row passes only when it is above zero. Watch it fail on a
planted break (jolt drawn at zero) before trusting it.

Not this item: the doubled-outline look (RIMMANDRAKE_DRAW_CONTAINER_JOLT_AS_MOVE_NOT_GHOST).

Acceptance: the sc_closed_containers jolt rows report a measured `drawnOffset` above zero on a live run, and below/at zero
under the planted break.
