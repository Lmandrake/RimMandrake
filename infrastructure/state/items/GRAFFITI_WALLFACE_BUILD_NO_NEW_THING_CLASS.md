# GRAFFITI_WALLFACE_BUILD_NO_NEW_THING_CLASS

Owner, by card 2026-10-22: "Q9 → Graffiti floor cell drawn offset facing wall"
(`design/RimMandrake/gpt_review_findings_2026-10-22.md`, Q9 and "Owner answers").

## spec
Marks stay `Filth_Mark` on the floor cell beside a wall (placement, cleaning and going-over unchanged). Each mark records
`wallSide` (Rot4 int, saved `rmMarkWallSide`, read at first spawn so marks from older saves gain it on load; north
beats east beats west beats south: `RM_GraffitiKernel.WallSide`). `Filth_Mark.Print` draws both the plain and the
tier-A sigil mark pushed `WallFaceOffsetCells` (0.5) toward that wall and turned so its top points into the wall
(`WallFaceOffset`, `WallFaceAngle`). A mark with no wall draws exactly as before. Art is not changed; only draw offset
and rotation. Probe: `Filth_Mark.ProbeWallFaces` (`marks=;onWall=;sides=n,e,s,w;mismatch=`).

## verify
Offline: `selftest_graffiti_fuzz.py` (family `wall`: all 16 neighbour masks), `mutate_graffiti_fuzz.py wall` (6 of 6
caught), Graffiti/SacredGraffiti lint selftests.

## criteria
- A1 L0: Graffiti fuzz OK incl. `wall`; mutate_graffiti_fuzz wall 6/6 caught; RimMandrakeGraffiti.dll builds.
- A2 L1: deploy: the Graffiti DLL reaches the game's Mods folder (dry run clean, then --apply).
- A3 L2: live: after painting marks beside walls on all four sides, `Filth_Mark.ProbeWallFaces` reads onWall == marks, mismatch=0, and each side's count matches where they were painted; an older save's marks load with a side.
- A4 L4: owner looks in game: marks on north, east, west and south walls read as painted on the wall face, not on the floor; offset (0.5 cell) and the facing (top into the wall, so a south-wall mark is upside down from the camera) are his call.
