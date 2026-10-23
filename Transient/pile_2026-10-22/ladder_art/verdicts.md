# Self-judged against design/RimMandrake/art_judge_brief.md (maker = judge; the brief wants a fresh judge, so these are advisory)
Inputs: def RM_LadderPortable (FlowWorks_PitAccess.xml, Graphic_Single 256 px, drawSize 1, rotatable; flat art RM_LadderPortableFlat when too short).
Options are Graphic_Multi-ready: 384 px canvas, drawSize 1.5 + RM_Ladder offsets (north/east/west +0.25 z, south -0.25), north/south/east/west files.
Source art: our own RM_LadderPortableFlat.png rotated upright and perspective-projected (art_source/LadderPortable/gen.py); not donor.
- A plumb (west lean ~18 deg, north taper 0.8): KEEP. E4 yes ("much more vertical"); B1 painterly; D2-D4 ok (real alpha, no shadow, edges clear). Flag B2: rails ~5 px at 32 px/cell, legible as a ladder but thin.
- B steep, narrowest (west lean ~12 deg, strong taper): KEEP-but-flagged. E4 yes, the most vertical; B2 weakest: at 32 px/cell it is a dark hairline.
- C plumb + baked soft contact shadow: REDO under D4 "Real alpha: no backdrop, halo, ground shadow or scenery" (seen: blurred dark ellipse in the PNG). Kept only because the owner asked for a floor shadow in the brief given to me; split call, his to rule.
- South facing (all): the top 30% of the ladder poking over the near rim, as RM_Ladder_south does. East = mirror of west (C2 west mirrors east).
- E2 UNSURE: a projected copy of our own art may trip placeholder_detect.py; not run.
- Softness: source ladder is 232 px long, upscaled ~1.4x to 1.5 cells x 256 px/cell; UnsharpMask applied. A native high-res redraw would beat it (D2).
- Install, if picked: def graphicClass Graphic_Single -> Graphic_Multi, drawSize (1.5,1.5), drawOffset N/E/W (0,0,0.25), S (0,0,-0.25); keep uiIconPath Flat and shortGraphicData. NOT installed.
