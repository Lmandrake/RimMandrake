## State (2026-10-31)
**The 2026-09-27 finding (2 of 29 own faces) is history: `python3 src/RimMandrake/Utils/art/biome_face_census.py` reads
61 of 61 owned**, 0 vanilla/donor, with no patch rewriting a biome texture; `--deployed` also reads 61 of 61 in the game.
Faces come from `src/RimMandrake/Utils/art/biome_worldfaces.py` and `world_water_variants.py`. They are throwaway-grade:
the redo after the Baroque Biomes is `WORLD_GLYPHS_SKETCH_EVERY_BIOME_FIRST_STAB` (owner, 2026-10-24).

Beauty set: `D:\ClaudeWork\rimmandrake\art\world_beauty_2026-10-31\` (`world_beauty_render.py`). These are OFFLINE renders
of the tile record, not game screenshots: no ring, rivers or icons. Judge verdict PASS: `judge_gpt.txt` there. The owner's
look is delegated (note 2026-10-29); it reaches him in the daily digest.

Beautification mods: `zal.worldmapenhanced` and `grimterra.worldmap` were cut by owner card 2026-10-10 and stay out (card
2026-10-23), so no retirement is left to file. No third-party mod in the audit facts ships World textures alone;
those with biome faces are biome-content mods, retired on their own items. No face shares bytes with a mod's World png.

## spec (executes after the repaint)

1. Per-biome worldmap texture + tile-color pass: one texture per shipped biome,
   derived from its sheet's palette and register (the frozen sheets are the
   authority for what each biome "really looks like"), named
   `World/Biomes/RM_<Biome>` in the Baroque Biomes mod.
2. Judged by LOOKING at fresh planet renders/screenshots after the repaint —
   worldview-style iteration, the owner rules.
3. **Worldmap beautification mods**: examine which of the active beautification
   mods this obsoletes — they likely become droppable once our biomes carry real
   faces, but their look is USEFUL GUIDANCE for the textures we author (owner's
   words). Enumerate them at execution and file the retirement separately.
4. Regenerate the planet beauty-shot screenshot set afterwards — those renders
   feed `PLANETARY_LOADSCREEN_RENDERS_2` (blocked on this).

## verify
- Every shipped biome's worldmap texture is our own (0 vanilla/donor faces on
  our defNames — re-run the census above and it reads 29/29 owned).
- The owner has looked at the repainted planet with the new faces and ruled it.
