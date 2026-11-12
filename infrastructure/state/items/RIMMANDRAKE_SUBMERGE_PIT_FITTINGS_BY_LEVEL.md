# RIMMANDRAKE_SUBMERGE_PIT_FITTINGS_BY_LEVEL

## spec

Owner 2026-11-12 (approving EXCAVATION_WALL_ART_1): "The art all looks good... except that a ladder hanging into water is
shown entirely over the water regardless of depth. The water really should go up to some level on the ladder as though it
is part submerged. Same for spikes and other pit installations."

Conductor brief (owner authority): one general mechanism; the covered share follows liquid level against pit depth (fill 0
whole; brim-full only what stands above the surface; depth 4 at fill 1 about the bottom quarter covered); every FlowWorks
liquid; both ladder kinds and the spikes; nothing when dry, no per-frame allocation; a Mod Settings toggle, default on.

## state

Built; live matrix 2204 rows, 0 FAIL (2026-11-12). Owner's look owed on save SUBMERGE_PIT_FITTINGS_MATRIX_20261112
(report: D:\ClaudeWork\rimmandrake\conductor\submerge_matrix_20261112\REPORT.md). His look closes it.

Owner's look 2026-11-12 ~10:40 PST on EWA_SUBMERGE_REVIEW_20261112: "Looks great at 1m water depth, but 2m water depth
put the northern ladder behind the pit wall art for some reason, silly looking. Southern ladder works correctly."
Cause (MEASURED on that save, cell 113,104): fill grid 3, true level 4.00 notches. The wall face is drawn from the fill
grid (a notch of dry wall still showed); the ladder was cut at the true level (waterline at the rim), so it vanished
under the visible band. Fixed 029034d0efce: a hung ladder is cut at its wall face's fill.

## diagnosis

Pit liquid is a base-terrain swap (`RM_MapComponent_Excavation.ApplyFillTerrain`, AltitudeLayer.Terrain). Wall faces show
the liquid by being drawn shorter (`RM_WallFaceMath.ExposedDrop`). Nothing did the same for fittings:
- ladders printed whole at Building altitude (vanilla `Thing.Print`; `RM_Building_Ladder` had no Print, Superdeep/RM_LadderUtility.cs:508);
- the ramp printed whole at FloorEmplacement (Superdeep/RM_PitRamp.cs:21);
- spikes only faded by alpha (Superdeep/RM_Spikes.cs, `RM_SpikeDrawMath.SubmergedAlpha`).

## mechanism

The submerged part of each sprite is cut away, so the liquid's own terrain shows there. Works for every liquid, with no
colour lookup.
- `Superdeep/RM_SubmergeMath.cs` (Verse-free; SelfTest `SubmergeDrawChecks`):
  - ladder waterline = its wall face's waterline (N: z = 1 - NorthFaceHeight(exposed); E/W: the side face width);
  - hung south: never cut; lying flat (portable): hidden from fill 1;
  - ramp: covered from its downhill end by level / rise;
  - stake: covered from its foot by level metres / 1 m.
  - gate (sluice, grate): covered from its foot by level / (depth + 1), frame and lifted panel at one waterline
    (`GateShare`; realtime cut meshes cached per step, `RM_SubmergeDraw.CutMesh`), added 9a0a6daa0385;
  - a hung ladder takes the whole-notch fill its wall face is drawn with (`HungLadderLevel(FillAt)`), so its waterline
    is always the wall's; the ramp, stakes and gates take the TRUE level in notches (whole notch + part-notch,
    `WaterDlAt / RM_LevelSolve.U`; one notch = 0.5 m), kept to quarter notches (`RM_SubmergeMath.LevelNote`).
- `Superdeep/RM_SubmergeDraw.cs`: partial `Print` overrides for `RM_Building_Ladder` and `RM_Building_PitRamp`, mirroring
  vanilla `Graphic.Print` (atlas uvs lerped, flip, shadow, static buffers).
- Redraw on a level change: `RM_MapComponent_Excavation.submergeDrawn` notes cell -> printed key (`DrawnKey`: a ladder's
  face fill, the ramp's quarter-notch level). `ApplyFillTerrain`
  (called by every write of a dug square's liquid) re-meshes a noted cell only when its note moved. While nothing is noted
  it does no work.
- `Building_RM_Spikes.DrawAt` cuts each stake (mesh key carries the step).
- Composes with f565f1793cac (ladder climb fix): that moved the climbing PAWN's draw and added `climbSpan*` to the ladder
  defs; this cuts only the ladder's own sprite in its Print, reads none of those fields and changes neither.
- Setting `pitSubmergeCutEnabled` (How cuts and liquids look), default on; off = the old drawing.

Covered defNames:
- RM_Ladder, RM_LadderSteel, RM_LadderPortable;
- RM_Spikes;
- RM_PitRamp;
- RM_Sluice, RM_SecurityGrateDoor.

Not covered:
- RM_Swale (a liner on the floor) and goods on the floor: drawn over the liquid at every depth; the owner decides
  (RIMMANDRAKE_DECIDE_GOODS_AND_SWALE_UNDER_LIQUID);
- RM_PitCover, the suspension deck, tower and jetty (over the pit);
- RM_LiquidDrill and the tap (outside it).

## proof

- Offline: `winbuild.py FlowWorks`; FlowWorks SelfTest `Submerge_*` (9 cases; `Submerge_hung_ladder_meets_its_drawn_wall_face`
  kills the true-level-ladder mutant); `selftest_settings_search.py`.
- Live acceptance matrix: `python.exe src/RimMandrake/FlowWorks/northstar/pit_fittings_matrix.py <repo_win> <out_win> all`
  (then `sheets` under WSL python3). One prepared pit (N/E/W/S ladders wood + steel, portable, ramp on a step, spikes,
  sluice, grate, swale, cover, guardrail, steel, a minified table) over D1-D6, D8 x every fill, plus tar. Rows per fitting:
  found, share, hung ladder cutZ == faceZ, gate share, printed at its level, placement refused only by design.
- First live proof (21/21 PASS 2026-11-12, before the matrix): `python.exe src/RimMandrake/FlowWorks/northstar/wall_art_scene.py <repo_win> <out_win> submerge`.
  - Six D4 pits: ladder and spikes at fill 0/2/4.
  - Each reads `RM_SubmergeDraw.ProofSubmerge`, with these rows: found at depth 4 and the fill; share in range; ladder
    printedLevel == level (the level change re-meshed it); setting on.
  - Then the captures `submerge_*.png` for the owner's look.
