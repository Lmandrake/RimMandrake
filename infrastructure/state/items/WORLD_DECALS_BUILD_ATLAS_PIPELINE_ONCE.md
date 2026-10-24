# WORLD_DECALS_BUILD_ATLAS_PIPELINE_ONCE

Program step 4a (design/Jawa/worldbuilding/world_look_program_2026-10-24.md). Replaces WORLD_DECALS_BUILD_SEPTEMBER_CHARM_REDRAWN (that was conditional on look C; the owner picked C on 2026-10-24).

## spec
Generic infrastructure so per-biome art can be swapped cheaply at the Baroque redo:
1. `RM_WorldLook` per-tile decal submesh: 2-3 unrotated glyphs per flat land tile, chosen by a stable hash of the tile id, from one atlas per biome (`World/Decals/<Biome>` 2x2 or 4x4), lit from one side with a soft shadow baked in.
2. LOD: fade by camera altitude (full at close, gone past mid zoom) via material alpha set per frame, not by mesh rebuild.
3. A biome with no atlas draws nothing (no error), so the roster fills in gradually.
4. Draw order between the blend (3505) and hills (3510).
5. Atlas spec + generator contract written down (size, cell count, shadow, palette source = the biome sheet) so the redo is "re-run the generator".

## kind
C# (BiomesShell `RM_WorldLook`, winbuild + .srchash). Art only as a test atlas.

## toggles
Proposed "Planet: biome decals" (new bool) and a fade-altitude tunable via `Set`.

## art routing
Test atlas only; real atlases are WORLD_GLYPHS_SKETCH_EVERY_BIOME_FIRST_STAB.

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
