# WORLD_MAP_POLISH_THE_REST_LATER

Program step 6 of 6 (design/Jawa/worldbuilding/world_look_program_2026-10-24.md). Owner, 2026-10-24: "the whole map needs love. We'll eventually get to the tile contents too (mutators, etc.) but for now let's just stick with major landforms and such."

## spec
Placeholder for what is left after steps 1-5: the terminator / night side read (Ash'karr is tidally locked; sun at lat 0, long 0), ice and snow caps, coastlines, the planet's atmosphere rim, feature labels. Tile contents (mutators, landmarks icons) are OUT of scope until he says.
Re-scope after steps 1-3 have had an owner look.

## kind
Mixed; decided per sub-item when split.

## toggles
Per sub-item.

## art routing
Art ledger + art-eval for every picture.

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
