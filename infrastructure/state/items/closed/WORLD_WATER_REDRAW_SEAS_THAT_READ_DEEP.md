# WORLD_WATER_REDRAW_SEAS_THAT_READ_DEEP

Program step 1 of 6 (design/Jawa/worldbuilding/world_look_program_2026-10-24.md). Owner, 2026-10-24: "Especially important is to get the water right too".

## spec
What the sea draws from today (measured in source, 2026-10-24):
- Water biomes point their `<texture>` at vanilla `World/Biomes/Ocean` (RM_GreySea, RM_TwilightSea, RM_TheScald) or `Jawa_SickWater` (RM_TheChill). Our own water faces RUT_{GreySea,TwilightSea,Scald,Chill,MineralWater} exist (`biome_worldfaces.py` 'water' style) on the RUT twins only.
- `Custom/WorldOcean` takes only `_MainTex` and `_MacroTex`; it ignores UV0, so it cannot shade depth. Depth comes only from `RM_WorldLook` sea films: a pale shore film (0.40,0.62,0.72) at alpha 0.40 over 1 tile and a dark deep film (0.05,0.09,0.20) at alpha 0.5 rising over 4 tiles.
Work:
1. Offline: water options true to those inputs (face tiled + macro + both films), several colours and ripple styles per sea, at three zooms. First deliverable of the program.
2. Pick per sea: face colour, ripple (direction, length, contrast), shore band, deep tone. Lakes (MineralWater, PropaneLake) get the same treatment.
3. Install: one face per sea on BOTH twins (RM_ and RUT_), film tunables set from the pick (they are public statics; `Set "key|value"` live).
4. River water colour is out of this ticket (RIVERS_ROADS_REDESIGN_WORTH_LOOKING_AT; FlowWorks belongs to BENCH).

## kind
Art first (faces), small C# second (film defaults in `RM_WorldLook.cs`, BiomesShell; winbuild + .srchash). No new shader.

## toggles
Existing: "Planet: deep-sea shading" (`worldSeaDepth`). Proposed: none new; the faces are the default look.

## art routing
Faces via `biome_worldfaces.py` / a water-variant generator -> art ledger -> art-eval (water faces: mean value <= 140, cool, seamless) -> sheet.

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
