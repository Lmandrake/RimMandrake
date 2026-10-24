# CONTAGION_PEAKS_REDRAW_AS_RAIN_MAKERS

Program step 1b, with the water (design/Jawa/worldbuilding/world_look_program_2026-10-24.md). Owner, 2026-10-24: "Contagion-stained mountains (the only place we use Contagion) is particularly important, and to draw those as wet/water generators (about the only places that are, so important!)". Ruled by card 2026-10-24 07:55 PDT, Contagion-stained mountains -> "Look only: they weep": a LOOK only, no river-rule change now (rules wiring = CONTAGION_PEAKS_WIRE_WEEPING_RULES_LATER).

## spec
Canon (the_contagion.md R-H1, R-H7; contagion_placement_candidates.md): rain falls only at the greatest altitudes; the ocular forests on the peaks excrete red, spore-laden water. The Contagion sits on 179 peak tiles (Dew Horn 87, Cratercrown 44, Ashfall Range 24, Dune Sea 17, Fall Line 5, Anvil 2); 23 carry rivers.
Draw "they weep":
1. The big-mountain treatment (MOUNTAINS_REDRAW_BIG_NOT_LITTLE_PICS) in its Contagion variant FIRST: dark stained rock, wet sheen on the shade faces.
2. Seeping streaks running down the flanks (red-dark, thin, downhill), and small spring glints where they break out.
3. Optional: cloud caps or haze on the highest summits (the swirl submesh exists for Abyss/Rot).
No river colour or river rule change in this ticket.

## kind
Art (Contagion mountain variant, streak/glint atlas) + C# only if the streaks need their own overlay in BiomesShell `RM_WorldLook` (winbuild + .srchash).

## toggles
Rides "Planet: drawn mountains"; proposed "Planet: weeping Contagion peaks" if it gets its own overlay.

## art routing
Art ledger + art-eval; sheet together with the water options.

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
