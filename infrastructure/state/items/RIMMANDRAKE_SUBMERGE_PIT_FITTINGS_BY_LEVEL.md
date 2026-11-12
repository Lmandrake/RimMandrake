# RIMMANDRAKE_SUBMERGE_PIT_FITTINGS_BY_LEVEL

## spec

Owner 2026-11-12 (approving EXCAVATION_WALL_ART_1): "The art all looks good... except that a ladder hanging into water is
shown entirely over the water regardless of depth. The water really should go up to some level on the ladder as though it
is part submerged. Same for spikes and other pit installations."

Conductor brief (owner authority): one general mechanism; the covered share follows liquid level against pit depth (fill 0
whole; brim-full only what stands above the surface; depth 4 at fill 1 about the bottom quarter covered); every FlowWorks
liquid; both ladder kinds and the spikes; nothing when dry, no per-frame allocation; a Mod Settings toggle, default on.

## state

Built, live proof and owner's look owed. Leave open until the live `submerge` rows pass and the owner has looked.

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
  - "level" is the TRUE level in notches (whole notch + the cell's part-notch, `WaterDlAt / RM_LevelSolve.U`; one notch
    = 0.5 m), kept to quarter notches (`RM_SubmergeMath.LevelNote`); the face tables are read straight-line between whole
    notches (`FaceAt`), so at a whole notch the ladder's waterline is exactly the wall's. Between notches the wall face
    (integer fill) can sit up to half a notch lower than the ladder's waterline.
- `Superdeep/RM_SubmergeDraw.cs`: partial `Print` overrides for `RM_Building_Ladder` and `RM_Building_PitRamp`, mirroring
  vanilla `Graphic.Print` (atlas uvs lerped, flip, shadow, static buffers).
- Redraw on a level change: `RM_MapComponent_Excavation.submergeDrawn` notes cell -> printed level note. `ApplyFillTerrain`
  (called by every write of a dug square's liquid) re-meshes a noted cell only when its note moved. While nothing is noted
  it does no work.
- `Building_RM_Spikes.DrawAt` cuts each stake (mesh key carries the step).
- Composes with f565f1793cac (ladder climb fix): that moved the climbing PAWN's draw and added `climbSpan*` to the ladder
  defs; this cuts only the ladder's own sprite in its Print, reads none of those fields and changes neither.
- Setting `pitSubmergeCutEnabled` (How cuts and liquids look), default on; off = the old drawing.

Covered defNames:
- RM_Ladder, RM_LadderSteel, RM_LadderPortable;
- RM_Spikes;
- RM_PitRamp.

Not covered (they do not stand in the liquid):
- RM_Swale (a liner);
- RM_PitCover, the suspension deck, tower and jetty (over the pit);
- RM_LiquidDrill and the tap (outside it).

## proof

- Offline: `winbuild.py FlowWorks`; FlowWorks SelfTest `SubmergeDrawChecks` (7 cases, one on the part-notch level);
  `selftest_settings_search.py`.
- Live (owed): `python.exe src/RimMandrake/FlowWorks/northstar/wall_art_scene.py <repo_win> <out_win> submerge`.
  - Six D4 pits: ladder and spikes at fill 0/2/4.
  - Each reads `RM_SubmergeDraw.ProofSubmerge`, with these rows: found at depth 4 and the fill; share in range; ladder
    printedLevel == level (the level change re-meshed it); setting on.
  - Then the captures `submerge_*.png` for the owner's look.
