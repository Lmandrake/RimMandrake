# WORLDMAP_BIOME_ICONS_REGEN_1 — worldmap biome decoration icons don't auto-update with plant/animal reassignment

Owner, 2026-09-07 (screenshot attached showing a Blue Desert world-map tile with small
saguaro-cactus and dark tree/coral icons scattered on it): *"Add a ticket to regenerate
the worldmap biome graphics such as that for Blue Desert that shows little saugharo
icons. I assume these won't auto-update when we change its plant load, yet they should.
This should happen after reassignment of plants and animals per biome."*

## spec
- **Identify the mechanism first** (MEASURE, don't guess): find what actually draws
  these small per-biome decoration icons on the zoomed-in world map (the screenshot
  shows a cactus icon and a separate dark branching icon scattered across a Blue
  Desert tile, distinct from the tile's own base texture/atlas). Candidates to check:
  Geological Landforms' `worldTileGraphicAtlas`/decoration system (already seen on
  `BMT_CrystalCaverns`'s own BiomeDef — `GeologicalLandforms.BiomeProperties`), a
  vanilla or modded "biome decorations" layer keyed off `BiomeDef.wildPlants`/
  `wildAnimals`, or a separate icon-atlas mod. Confirm with `rimsage`/live inspection
  before assuming which system owns it — do not file the fix against the wrong
  producer.
- **Confirm the staleness**: once the mechanism is identified, check whether it reads
  the biome's CURRENT plant/animal roster live (in which case the graphics may
  already be correct and the owner's "little saguaro icon" observation is about
  Blue Desert specifically still carrying an unassigned/donor roster) or whether it
  caches/derives from a baked list that needs manual regeneration after a roster
  edit (in which case this is a real staleness bug, matching the project's general
  "derived artifacts decay" pattern — `[[currency-fingerprint-not-timestamp]]`).
- **Fix**: whichever it is, make the icon set track the biome's actual
  `wildPlants`/`wildAnimals` roster — either confirm it already does (nothing to
  build, just verify and close) or build the regeneration step and wire it to run
  **after** the plant/animal-per-biome reassignment pass, not as a separate manual
  step someone has to remember.
- Blue Desert is the example in the screenshot but this should be checked/fixed
  generally — any biome whose roster has been reassigned since its icon set was
  last (baked/verified) is a candidate for the same staleness.

## verify
Blue Desert's world-map decoration icons match its current (post-reassignment)
wildPlants/wildAnimals roster, confirmed by a live world-map screenshot; the fix (or
the "already live, no fix needed" finding) is wired to run as part of, or
immediately after, the plant/animal-per-biome reassignment pass so it can't be
forgotten on the next biome that gets reassigned.
