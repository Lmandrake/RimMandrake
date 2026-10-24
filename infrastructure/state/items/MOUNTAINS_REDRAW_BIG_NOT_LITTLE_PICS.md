# MOUNTAINS_REDRAW_BIG_NOT_LITTLE_PICS

Program step 3 of 6 (design/Jawa/worldbuilding/world_look_program_2026-10-24.md). Owner, 2026-10-24: "make mountains look BIG/mountainous rather than just little pics of mountains". This is Hills 2 (our own drawn mountain pass) scaled to read big. Contagion variant first (CONTAGION_PEAKS_REDRAW_AS_RAIN_MAKERS).

## spec
Today: vanilla `WorldDrawLayer_Hills` draws one small rotated quad per hilly tile; we only swap the four shared hill materials (`RM_Hills` soft atlas). A one-tile sprite per tile cannot look big.
Options (pick after offline renders):
- A. Range mesh: our own hills layer that merges adjacent Mountainous/LargeHills tiles into ranges and draws ridgelines across tiles (lit face + shade face, unrotated, light from one side), with snow/biome caps.
- B. Oversized sprites: per-tile peaks 2-3x a hex, sorted back to front so neighbours overlap into a massif.
- C. Relief shading: a per-tile height film (light/dark slope from neighbours' hilliness) under smaller peaks.
Silhouette at every zoom: peaks at close/mid, shaded massif at far. Scale, shading, height cues (cast shadow toward the night side fits a tidally locked sun), silhouette.

## kind
C# (BiomesShell: own hills draw layer or a `WorldDrawLayer_Hills` replacement; winbuild + .srchash) + art (peak atlases per biome family). Generic: atlas + mesh code reused at the Baroque redo.

## toggles
Existing "Planet: soft hills" (`worldSoftHills`); proposed "Planet: drawn mountains" (new bool, off = vanilla quads).

## art routing
Peak atlases via a generator (`world_peak_decals.py` / `world_hill_decals.py` base) -> art ledger -> art-eval -> sheet.

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
