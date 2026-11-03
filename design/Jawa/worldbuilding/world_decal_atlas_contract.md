# Biome decal atlases: the contract (world look 4a)

Item `WORLD_DECALS_BUILD_ATLAS_PIPELINE_ONCE`. Program: `design/Jawa/worldbuilding/world_look_program_2026-10-24.md`.
The infrastructure is kept; the per-biome art is throwaway and is redone after the Baroque Biomes by editing a row and
re-running the generator. Nothing here needs a code change for that redo.

## What the game reads (`src/RimMandrake/BiomesShell/Source/RM_WorldDecals.cs`)

| | |
|---|---|
| path | `Textures/World/Decals/<BiomeDef defName>.png` in any loaded mod (we ship it in the biome's own mod) |
| shape | square RGBA; cells of **256 px**; the grid side is `width / 256`: 256 px = 1 cell, **512 px = 2x2**, **1024 px = 4x4**. Anything else is refused with one warning and that biome draws nothing |
| cell order | left to right, top row first (cell 0 is top-left) |
| margin | zero alpha on the outer 8 px of every cell; the game also insets each cell's UVs by one texel |
| glyph | one per cell, **upright** (the game turns every glyph so its top points to planet north), drawn inside the inner 86% of the cell |
| light | from the **upper left**, baked into the colour; a **soft shadow** offset down-right, baked into the alpha |
| colour | the glyph's own colours; the material is white, so nothing tints it in game |
| missing | a biome with no atlas draws nothing and logs nothing |

How the game uses it: every FLAT land tile of that biome gets 2 or 3 glyphs (a stable hash of the tile id picks the
count, the cells and where on the tile), each `decalSize` = 0.30 tile spacings wide, `decalSpread` 0.22 (+ up to
`decalJitter` 0.06) from the centre. Queue 3507 at +0.0045: over the border blend (3505) and swirls (3506), under the
hills (3510, +0.005) and rivers (3520, +0.01). They fade by camera altitude: full at or below `decalFullAlt` 380, gone
at or above `decalGoneAlt` 620 (the camera runs 125 to 1100), by material alpha set per frame. Toggle: Mod Settings
"Planet: biome decals" (`worldBiomeDecals`, default on). Live tuning: `jawa/static_call RimMandrake.Biomes.RM_WorldDecals
Set "decalGoneAlt|700"` then `jawa/world_commit`; `RM_WorldDecals.Info` reports what was built and the current alpha; `RM_WorldDecals.Probe "<defName>"` says whether that biome has an atlas and its grid (both reviewed read-only static calls; live proof `src/RimMandrake/BiomesShell/live_world_decals.py`).
`decalFlipX` mirrors every glyph if a live look shows the light on the wrong side.

## The generator (`src/RimMandrake/Utils/art/world_decal_atlas.py`)

One row per biome in `design/Jawa/worldbuilding/world_decal_rows.json`:

- `mod`: the mod folder that ships it (`RimMandrake/<Biome>`);
- `sheet`: the biome sheet the palette and glyphs were read from (path first, then the line it rests on);
- `grid`: 1, 2 or 4;
- `palette.body`: `[dark, mid, light]` hex, the light ramp of the glyph; `palette.shadow`: hex of the baked shadow.
  **Palette source = the biome's sheet** (its §Artistic theme), never invented;
- `glyphs`: names from the generator's bank (`rock dune shrub tuft crater spire crystal crack frond puff`), cycled over
  the cells. A new shape is a new function in the bank, nothing else.

The redo, per biome:

    python3 src/RimMandrake/Utils/art/world_decal_atlas.py gen --biome RM_X        # writes to agent scratch, checks the contract
    (art-eval and a prereviewed sheet, as for any art)
    python3 src/RimMandrake/Utils/art/world_decal_atlas.py install --biome RM_X    # art-ledger install into the row's mod

`check PNG...` runs the contract check on any atlas (square, cell size, RGBA, clean margins, no empty or solid cell).
The offline proof is `src/RimMandrake/Utils/selftest_world_decals.py` (source, a Python mirror of the C# arithmetic
over 200,000 tiles, and the generator's light and shadow).

## Unmeasured (the first live look sets these)

- Hex scale (`TEX_PER_HEX`), so glyph size on screen: `decalSize` is relative to the tile spacing, so the glyph-to-hex
  ratio holds whatever the scale is; its pixel size does not.
- Which side is lit on screen: the right vector is `n x up` for a camera outside the planet; if the live look shows the
  light on the right, set `decalFlipX`.
- The fade band (380 to 620) against the 18-point grid at altitude 900 and close-ups at 320.

## Atlases shipped

| biome | atlas | status |
|---|---|---|
| RM_BlueDesert | `src/RimMandrake/BlueDesert/Textures/World/Decals/RM_BlueDesert.png` (2x2: frond, puff, shrub, dune) | **test atlas** for 4a; real art is `WORLD_GLYPHS_SKETCH_EVERY_BIOME_FIRST_STAB` |
