# FlowWorks visuals pass — 2026-10-05 (FOUNDRY)

Owner principles 1-5 (2026-10-05). Status per principle below; filled as work lands.

## 1 Depth perspective
BUILT (offline; live owed). North face by exposed drop D1 0.10 / D2 0.18 / D3 0.30 (= vanilla wall face, measured ~0.25) / D4 0.50 cells; side faces 0.04/0.07/0.12/0.18. Lit like vanilla's camera-facing wall faces, dark rim line, contact shadow at the foot (RM_WallFaceMath table, RM_ExcavationWalls). Near-lip occluder: RM_PitLipOcclusion draws the lip cell's own ground over the part of a sunk pawn below the lip, render queue after pawns, 85% (Mod Setting).
## 2 Wall material
BUILT. Face = the neighbour ground's OWN terrain material (exact texture/colour), plus earth strata (dirt) or block joints (stone). Stone = terrains named by natural-rock ThingDefs (naturalTerrain/smoothed/leaveTerrain, set by TerrainDefGenerator_Stone) or a natural rock building beside the cut (RM_FaceMaterial). No per-biome data. Setting excavationWallMaterialEnabled off = old flat band.
## 3 Water motion
BUILT. RM_LiquidSurface: per visible filled cell, two additive procedural ripple layers drifting against each other (+ rainbow film where sheen>0), one mesh per look, motion by material offset; face band left uncovered. V-wakes: pairs of WaterRipple flecks thrown back-and-out behind any pawn moving through a cell with a look (wake strength per liquid). Vanilla water terrains never get the overlay (they animate already). Fill tiers keep their vanilla ramps, so depth still reads.
## 4 Tar as liquid
BUILT. Per-liquid look = DATA: LiquidDef.surfaceLook emitted by Tools/generate_liquid_suite.py (SURFACE_LOOKS table, 15 rows; regenerated output = additions only, otherwise byte-identical) and FluidDef.surfaceLook for oil/poison (no LiquidDef row). Tar: slow (0.05 c/s), broad gloss, stretched slicks, wake 0.15. Oil: gloss + rainbow sheen. Slime: soft slow blobs. Water family: fast fine glints.
## 5 Burned pit
BUILT. RM_PitScorch (MapComponent, cosmetic state) marked by a Harmony postfix on RM_LiquidFire.Extinguish(spent=true) — fire code untouched. Walls layer draws ash/char floor, soot on faces, scorch ring on the rim; same faces/depth as an unburned pit. Persists until refilled/filled-in, fades over pitScorchFadeDays (default 20, 0 = never; rain unroofed x3), quantised to quarters. RM_PitScorchProof.ProofScorch / ProofScorchAt for staging and state reads.
## Assumptions
- A1 Face height follows vanilla's wall face (measured: Wall_Atlas_Smooth/Rock_Atlas south face ~0.25 cell, side faces ~0.125): north face D1 0.10, D2 0.18, D3 0.30 (= a wall), D4 0.50; side faces 0.04/0.07/0.12/0.18. Face is LIT (vanilla convention: camera-facing faces are the light tone) with a dark rim line and a contact shadow at the foot. Replaces the provisional 0.225/level procedural band.
- A2 Pawn sink stays 0.3/level (PIT_DEPTH_DRAW_OFFSET_1, unchanged). The near (south) lip occludes the sunk part of a pawn at 85% opacity so a pawn at D4 is a faint ghost, never lost.
- A3 Face material = the ground beside the face (neighbour's terrain; the cell's recorded original terrain if the neighbour is itself dug). Stone = any terrain a natural-rock ThingDef names (naturalTerrain / its smoothedTerrain / leaveTerrain) or a natural rock building in the neighbour cell; everything else reads as dirt. No per-biome table.
- A4 Liquid motion is an animated overlay (two drifting procedural noise layers + highlights) drawn over the vanilla water terrain; no flow direction (the engine has no per-cell flow vector for canals). V-wakes: flecks behind a pawn moving through a filled cell.
- A5 Scorch persists until the cell is refilled or filled in; otherwise fades over pitScorchFadeDays (default 20; rain on an unroofed cell x3). PROVISIONAL, Mod Setting.
## Mockups / sheet
- Offline mockups (PIL, vanilla textures from resources.assets via UnityPy): src/RimMandrake/FlowWorks/art_source/visual_principles_2026-10-05/ (make_mockups.py -> *_before/*_after .png/.gif; make_sheet.py -> visual_principles_sheet.html + visual_principles_decisions.json, prefill only).
- Served: serve_sheet.py --port 8763 --no-open (token URL in Transient/fwvisuals_serve.log). Rendered headless Edge 1400/390 and looked: readable, images load.
## Live capture
Replaced (coordinator, 2026-10-05): no own review map. VISUALS STATIONS READY for the map agent:
- src/RimMandrake/FlowWorks/review_map_stations_visuals.json (34 stations: D1-D4 x dirt/stone x dry/water/tar/scorched + oil, slime)
- src/RimMandrake/FlowWorks/review_map_visuals.py: station_ops(station, base_x, base_z) -> bridge calls; --selftest.
In-game look of all five principles is UNSEEN until that map is built (the DLL with these layers must be deployed first).
## NEW ROWS NEEDED
For aa694 (owns northstar/*.py) — I did not edit them:
- 🔴 site_spec.py settings table (RimMandrakeFlowWorksSettings) must gain, or selftest_flowworks_northstar.py stays RED on the field-set parity check:
  "excavationWallMaterialEnabled": True, "pitLipOcclusionEnabled": True, "pitLipOcclusion": 0.85,
  "liquidSurfaceMotionEnabled": True, "liquidWakesEnabled": True, "pitScorchEnabled": True, "pitScorchFadeDays": 20.0,
- extensions.py FW_TOGGLES: + excavationWallMaterialEnabled, pitLipOcclusionEnabled, liquidSurfaceMotionEnabled, liquidWakesEnabled, pitScorchEnabled.
- Rows (state reads, no screenshot):
  V1 wall_face_heights_monotonic: ProofWallFaces on D1..D4 cells -> verts grow; D3 face >= 0.25 cell (math selftest already pins the table).
  V2 face_material_stone: a cut beside Granite_Rough draws with the granite material (needs a ProofWallMaterial read; owed).
  V3 lip_occludes_sunk_pawn: pawn at D4 near row -> occluder band > 0 (needs a proof read of RM_PitLipOcclusion; owed).
  V4 liquid_surface_has_look: RM_LiquidSurface.LookFor(RM_Fill_Tar_Brim) non-null, tar speed < water speed.
  V5 scorch_after_burnout: ignite a tar cut, burn dry -> ProofScorchAt strength 1.00; refill -> 0.00.
  V6 each toggle off -> flat look (layer verts drop / overlay not drawn).
## Commits
