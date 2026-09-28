# WORLDMAP_BIOME_APPEARANCE_1 — regenerate our biomes' worldmap tile appearance (AFTER the repaint)

Commissioned by the owner's typed message, 2026-09-27 (arrived mid-turn, recorded
under BENCH): *"please examine the current worldmap imagery for our many custom
biomes. They don't really look anything like what they should given what we're
filling them with. Please file a future ticket blocked by the worldmap
remake/repaint to regenerate the appearance of our biomes. This will also likely
undo the need for some of our worldmap beautification mods (they will provide
useful guidance though!)"*

🔴 **BLOCKED on the terminal repaint** (`BIOME_PAINT_ONCE_AT_THE_END_1` — the planet
is painted once, at the end, after every biome's content is mod-migrated). Do not
start this before that pass; biome-to-tile assignment changes wholesale there and
any appearance work done earlier is judged against tiles that will move.

## The measured finding (2026-09-27)

Of **29 BiomeDefs in src/** (MEASURED, regex over every mod's Defs), only **2**
carry their own worldmap texture: `World/Biomes/RM_FeverWood` and
`World/Biomes/RM_GelatinousSlime`. The rest wear someone else's face on the
planet:

- 4× vanilla `ExtremeDesert` · 4× vanilla `Ocean` · 3× vanilla `IceSheet` ·
  2× vanilla `TropicalRainforest` · 1× each `AridShrubland`, `Desert`
- 3× **donor Alpha Biomes textures** (`Biomes/AB_OcularForest`,
  `AB_RockyCrags`, `AB_MiasmicMangrove`) and 1× `Biomes/PoisonForest` (donor)

So the worldmap shows a boiling sea as vanilla ocean, the Grey/Twilight/Propane
seas identically, and rich custom biomes as generic desert — nothing like what
we fill them with.

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
