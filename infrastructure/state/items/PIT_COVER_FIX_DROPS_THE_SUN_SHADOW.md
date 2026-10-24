## spec
found-by: BENCH helper on PIT_SINK_FIX_SOIL_STRIP_OVER_WALL (2026-10-23), reading `Transient/bridge_run_1_20261023/captures/br1d3_c3_boar_s300.png` (contrast-boosted crop).
Class: MOD (look). After e4036c2441 the near-lip cover (Superdeep/RM_PitLipOcclusion.cs) no longer paints soil over the wall,
but the cover over the ground band between the lip and the wall (save e C3: x ~37.2-39.8, z 21..22) still reads LIGHTER than the
ground beside it: the cover is drawn above pawns (queue 3050) and so hides SectionLayer_SunShadows' wall shadow that lies on that
ground (83bd3c2bbf already carries the EDGE shadow; its message records sun shadows as not carried). The rounded light patch under
the boar is the boar's own 15 % ghost (pitLipOcclusion 0.85, assumption A2), not soil.
Mechanism to read before fixing (needs the decompile: RimSage on the Windows desktop): SectionLayer_SunShadows' mesh (vertex alpha =
staticSunShadowHeight, displaced by the _CastVect global from GenCelestial.CurShadowVector) and MatBases.SunShadowFade's queue/colour;
then either re-draw the clipped shadow over each cover piece (as DrawEdgeShade does for the edge shadow) or derive per-vertex shade.
Done when: save e C3 re-capture (paused, step 120/+300), the ground between the pit's south lip and the wall shows no box brighter
than its surroundings; the wall stays wall.
