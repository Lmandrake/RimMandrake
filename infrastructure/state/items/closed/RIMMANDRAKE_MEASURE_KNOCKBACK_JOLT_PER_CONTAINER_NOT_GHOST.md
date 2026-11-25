## spec
Explosive Knockback, Design Version 0.1.0 (current version). Filed by the ticket sweep
RIMMANDRAKE_SWEEP_KNOCKBACK_TICKETS_MERGE_TO_MODERN_BUILD_THE_VALUABLE (2026-11-22). It merges two older tickets on one file
group: the drawn jolt of a blocked closed container (`RM_MapComponent_Knockback.cs` StartJolt and MapComponentUpdate,
`RM_KnockbackMath.JoltOffset`) and the proof row that reads it (`RM_KnockbackProof_StageThree.cs`, the jolt rows of
sc_closed_containers).

1. **The row is undecided** (from RIMMANDRAKE_READ_CONTAINER_JOLT_OFFSET_IN_PROOF, filed 2026-11-15). sc_closed_containers
   (`design/concepts/ExplosiveKnockback/scenes.json`) expects "a drawn offset above zero on at least one tick in the thing
   trace" for each jolted container. The sheet says a blocked container jolts. Journal question 13 was answered on
   2026-11-15 11:45 AM PST under the Evidence-for-Ask ruling (per-ruling RIMMANDRAKE_ENACT_EVIDENCE_FOR_ASK_VERSION_ASKED_EVERY_TIME):
   a jolt that draws nothing is a build Problem, so 0.1.0 owes this row. The jolt has been drawn since 587529cee1, but every
   jolt row still prints the literal `drawnOffset=UNMEASURED`. The rescue's run of 2026-11-17 shows this for wall, pawn,
   pit and safe (`version/rescue_2026-11-17/live/all_scenes_300_ticks.txt`, line 111). The only counters,
   `RM_MapComponent_Knockback.JoltFrames` and `JoltMaxOffset`, are map-wide and count per frame. Fix: under `#if RM_PROOFS`,
   keep the largest drawn offset per container (thingIDNumber), and make the row read it and require it above zero.
   MapComponentUpdate runs per drawn frame, so the scene must let frames draw while a jolt is live (JoltTicks = 20).
2. **The jolt may read as a ghost** (from RIMMANDRAKE_DRAW_CONTAINER_JOLT_AS_MOVE_NOT_GHOST, filed 2026-11-15 in Stage 6
   visit 1). MapComponentUpdate draws a second copy of the graphic at the offset over the unmoved original
   (`b.Graphic.Draw(at, ...)`). A paused frame then shows a doubled outline (`version/in_game/visit_1/screenshots/jolt_*.jpg`,
   the t8 panel doubled by about 0.1 cell). Nobody has judged whether it reads as a shake in motion. When the row runs
   live, a judge that did not make the build watches one jolt in motion. If the judge rules the ghost strange, draw the
   container itself at the offset (no second copy). If not, write one line on `version/polish.md`.

This needs the proof build and a free game, not the owner's full list (tier list). The mod is switched OFF in the pipeline
(pipe act ct_000026, 2026-11-18). Run it with the next live pass of the mod.

## verify
Acceptance test (offline, today red): `grep -c 'drawnOffset=UNMEASURED' src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof_StageThree.cs`
prints 1 on today's tree (watched 2026-11-22). After the fix it prints 0, and the proof build compiles
(`python3 src/RimMandrake/Utils/winbuild.py ExplosiveKnockback -- -p:RmProofs=true`; never commit that DLL).
Live: `python.exe src\RimMandrake\ExplosiveKnockback\knockback_runner.py --scenes closed_containers,closed_containers_control --ticks 300`
on the proof build. Every jolted container (wall, pawn, pit, safe) prints `drawnOffset=` a value above 0, and the
control still passes.

## criteria
- Each jolt row of sc_closed_containers reads a per-container drawn offset above zero, live.
- A planted fault (StartJolt removed) turns those rows FAIL.
- One judge ruling on the ghost draw, recorded beside the row.
