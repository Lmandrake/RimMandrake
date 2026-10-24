# RIVERS_ROADS_REDESIGN_WORTH_LOOKING_AT

Program step 1c, in the FIRST (water) group by card 2026-10-24 07:55 PDT ("1 AND ..."), (design/Jawa/worldbuilding/world_look_program_2026-10-24.md). Owner, 2026-10-24: "I wonder about making the rivers and roads more beautiful too".

## spec
Today: `RM_WorldPaths` (BiomesShell) draws rivers on the road material, hard-edged, with a dark bank (water x 0.22); FlowWorks `RM_RiverColors` (BENCH) colours rivers per tile. Roads use RoadWorldLayerDef colours; owner rulings: earth tones, never blue; the ancient highway is "old asphalt broken from long ago".
This ticket is the LOOK side only; colour (any colour per tile, the red -> bluish -> green -> death ramp) is BENCH's RIVER_COLORS_WIDEN_RED_BLUE_GREEN_DEATH.
Proposed look (price before building):
- Rivers: width tapering from head to mouth, a soft pale bank line instead of the dark one, a faint highlight down the middle, mouths fanning into the shore film; the "death" end drawn as a thinning dry trace.
- Roads: dirt as a worn dashed track, stone/gravel lighter and solid, the ancient highway broken into segments with gaps.
Cost guess: taper + banks + highlight about a day of C# in `RM_WorldPaths`; roads are colour/texture work.

## kind
C# (BiomesShell `RM_WorldPaths`; winbuild + .srchash) + small textures.

## toggles
Existing "Planet: readable roads and rivers"; proposed "Planet: drawn rivers" (taper/banks).

## art routing
Path textures through the art ledger + art-eval; offline renders on a sheet.

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
