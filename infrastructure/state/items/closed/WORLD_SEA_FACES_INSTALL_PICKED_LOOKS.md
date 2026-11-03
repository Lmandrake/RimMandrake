# WORLD_SEA_FACES_INSTALL_PICKED_LOOKS

Parent: WORLD_WATER_REDRAW_SEAS_THAT_READ_DEEP. DATA only (no C#).

## spec
Picks (owner, 2026-10-24, round 1) and the sheet that shows them:
Grey Sea = lighter and clearer; Twilight Sea = darker and richer; The Scald = today's colour row; The Chill = no waves,
ominously dark (level from the round-2 sheet `Transient/world_water_review_r2_2026-10-24.html`); Mineral water (lake)
= today's row (prefill, he has not ruled it). Faces: `D:\ClaudeWork\rimmandrake\scratch\worldwater_variants_r2\sheet\<row>_file.png`
(generator `src/RimMandrake/Utils/art/world_water_variants.py`).

## what is data
- The ripple lives in the face texture: Custom/WorldOcean reads only _MainTex/_MacroTex and has no wave animation, so
  "no waves" for The Chill is a still face texture.
- RM_GreySea / RM_TwilightSea / RM_TheScald use `World/Biomes/Ocean`; RM_TheChill uses `World/Biomes/Jawa_SickWater`
  (TerminalBiomes BiomeDefs). The RUT twins use biome_worldfaces faces. Install = png + the texture path on BOTH twins.
- The Chill's still dark face breaks the biome_worldfaces water rule (val 60-140, sd 3-9) on the owner's order: record
  the exception in the art-eval criteria before the verdict refuses it.

## verify
Deploy plan/--apply, then the owner-attended world look (18 grid points at 900 + close-ups at 320).
