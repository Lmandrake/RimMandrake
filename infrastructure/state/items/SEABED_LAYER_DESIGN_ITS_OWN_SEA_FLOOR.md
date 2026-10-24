# SEABED_LAYER_DESIGN_ITS_OWN_SEA_FLOOR

Program step 2 of 6 (design/Jawa/worldbuilding/world_look_program_2026-10-24.md). Owner, 2026-10-24: "then the sea floors on their own layers".

## spec
Measured: `RM_SeabedLayer` (DivingInteraction) is a geometric twin of the surface (radius 100, tile N under tile N), drawLayers include `WorldDrawLayer_Terrain` and `WorldDrawLayer_Hills` only. `RM_WorldLook` adds films/blend/swirls to the ROOT SURFACE only (`IsRootSurface`), so the floor view is bare faces with hard hex edges. Floor faces: RM_SeabedFloor_{TheScald,GreySea,TwilightSea,TheChill}, RM_SeabedFloor, RM_SeabedBedrock, RM_SeabedUnavailable (crust/crack style, `biome_worldfaces.py`). The view gizmo is still `PlaceholderImage`.
Work:
1. Decide what the floor view shows per layer: floor faces per sea, a depth tint (deep basins darker), dry land drawn as a dim "continent above" mask, not as bedrock noise.
2. Let `RM_WorldLook` run on the seabed layer too (blend + a depth film keyed off the surface twin's depth), behind its own toggle.
3. Real gizmo icon (art) replacing PlaceholderImage.
4. Seabed Phase 5 (depth/geology) stays with the world remake; this ticket is look only.

## kind
Art (floor faces, gizmo icon) + C# (BiomesShell `RM_WorldLook` gate widened to the seabed layer; winbuild + .srchash).

## toggles
Proposed "Planet: sea-floor shading" (new bool).

## art routing
Art ledger + art-eval (canvas rules; icon at gizmo size) -> sheet.

## risks (shared by the whole world-look program)
- Hex scale is UNMEASURED: offline renders assume ~3.2 hexes per 512 px face (`TEX_PER_HEX = 160`). The first live look at three zooms sets it; every offline verdict is provisional until then.
- Speckle: at far zoom the white confetti on Rust Cathedral was Odyssey landmark icons (`LANDMARK_ICONS_DECIDE_THE_REAL_SPECKLE`), not faces. Judge any new mark at far zoom with landmarks on, or the decal gets blamed for the icons (or the reverse).
- Hard vs soft hex edges: September had hard edges; we ship soft borders ("Planet: soft borders between biomes"). Every live look tries both (a settings flip).
- Throwaway-grade: per-biome art is redone after the Baroque Biomes are done (owner, 2026-10-24). Spend on infrastructure that makes the redo cheap, not on polishing per-biome pixels.
- Draw order: overlays must stay below hills (+0.005, queue 3510) and rivers (+0.01, 3520/3530) or rivers break into dashes (`RIVER_DASHES_MEASURE_MORSE_CODE_WATER`).

## verify (shared)
1. Offline render review at full resolution, 1:1, no upscaling, three zooms (close / mid / far), every image prereviewed by the seat (fix or drop broken ones) before a sheet is served.
2. Art goes through the art ledger and the art-eval pipeline (canvas rules, `rimworld-art-evaluation`), then the review sheet (`art_sheet.py` + `serve_gated.py`).
3. Owner look in game, planned as an owner-attended or bridge-holding session (FOUNDRY is offline): 18 grid points at altitude 900 plus close-ups at 320 (the worldmap studio method), soft and hard edges both.
