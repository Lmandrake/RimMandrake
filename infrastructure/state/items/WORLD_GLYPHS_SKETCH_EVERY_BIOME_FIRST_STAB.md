# WORLD_GLYPHS_SKETCH_EVERY_BIOME_FIRST_STAB

Program step 4b (design/Jawa/worldbuilding/world_look_program_2026-10-24.md). Replaces WORLD_FACES_INSTALL_OUR_OWN_AT_LAST. Owner, 2026-10-24: "a clean background with icons drawn from the dominant land and life forms of the region. Colors drawn from actual biome colors ... take a stab at them all now to gain skill in this."

## spec
For EVERY biome in `biome_worldfaces.py`'s table (land; water and seabed faces belong to the water/seabed tickets):
1. A clean near-flat face in the biome's real colour (palette from its `the_*.md` sheet; owner overrides stand: Abyss near-black + swirls, Rot wild-colour swirls, Rust Cathedral harsh machinery).
2. One glyph atlas: the biome's dominant landforms and life forms as small icons, unrotated, never white.
3. Checker bounds for look C written into `biome_worldfaces.py check` (the old calm bounds refuse it).
Throwaway-grade on purpose: the goal is skill and a full first pass; the redo comes after the Baroque Biomes.

## kind
Art (faces + atlases); install needs WORLD_DECALS_BUILD_ATLAS_PIPELINE_ONCE for the glyphs.

## toggles
"Planet: biome decals" (from 4a).

## art routing
Generator -> art ledger -> art-eval (canvas rules) -> one sheet per batch of biomes, prereviewed.

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
