# SLUICE_OUTLINE_FIX_GREY_NORTH_LIP

Cause: NOT the gate PNG (RM_Sluice_east.png edge pixels are clean: top row alpha 166-181 dark wood, bottom (2,2,0)). The grey
line is the excavated canal's north RIM LINE, drawn by RM_ExcavationWalls.Outline. Crop pixels: north rim band (85,80,72) over
8px; south lining (0,0,0). Outline used ShadeMat (queue 2441), the same material/queue as the north face's cream light poly
(255,248,232 at alpha ~0.33), drawn after it, blending over black: 0.33*(255,248,232) = (84,82,77) = measured. South has no face over it.
Fix: new RM_FaceMaterial.OutlineMat at queue 2443 (after Shade 2441/Detail 2442); Outline uses it. Source only.
Owed: C# build (winbuild) + commit DLL+srchash together (push guard DLL_SOURCE_STAMP_GUARD_1 refused the source-only push; the 2 source edits are UNCOMMITTED in this clone), deploy, then a live look at a canal north rim.
