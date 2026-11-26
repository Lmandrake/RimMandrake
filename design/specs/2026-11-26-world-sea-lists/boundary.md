# Boundary for the per-sea planet looks: The Chill unlit, the Twilight Sea glass

Code: `src/RimMandrake/BiomesShell/Source/RM_WorldLookLists.cs`, `src/RimMandrake/BiomesShell/Source/RM_WorldLook.cs`.
Selftest: `python3 src/RimMandrake/BiomesShell/selftest_world_sea_lists.py` (`--part chill` or `--part glass` for one item).

Items: `SEA_FILMS_TUNE_PER_SEA_CHILL_UNLIT`, `TWILIGHT_GLASS_WIRE_INTO_SWIRL_LAYER`. The owner approved both looks on the
round-3 sheet (`WORLD_WATER_REDRAW_SEAS_THAT_READ_DEEP`, 2026-10-25). This page covers only these two looks. The rest of
`RM_WorldLook.cs` (border blend, shared films, hills, land swirls) has no page yet.

## ACCEPTS

- `seaFilmOverrides`: `<biome>=off` or `<biome>=<factor>` pairs, comma separated. The factor multiplies the alpha of both
  sea films on that biome's water tiles.
- `glassBiomes` and `swirlBiomes`: `<biome>=<texture>[@<widths>]` pairs, comma separated. `<widths>` is the number of tile
  widths (centre to centre) in one repeat of the texture.
- Both lists can be set live through `RM_WorldLook.Set` (bridge `jawa/static_call`).

## DOES NOT SURVIVE

- A biome with 0 tiles on the planet draws nothing. This is the expected state until the planet paint
  (`BIOME_PAINT_ONCE_AT_THE_END_1`).
- The selftest does not read rendered pixels. The rendered look on a painted planet is judged when the planet is painted.

## PROMISES

- **chill-unlit-by-default.** The shipped film list gives The Chill a film scale of 0 and every other sea a scale of 1.
- **film-override-grammar.** `off` gives 0, a factor of 0 or more is kept, a malformed or negative value is ignored, an
  unlisted biome reads 1, and the last entry for a biome wins.
- **chill-films-skipped.** `BuildSea` reads the film scale while `worldChillUnlit` is on, skips a tile whose scale is 0,
  and multiplies both film alphas by the scale.
- **twilight-glass-listed.** The shipped glass list holds `RM_TwilightSea`, the texture `TwilightGlass`, at 40 tile widths
  per repeat. The shipped swirl list keeps its two land entries on the global scale.
- **glass-scale-per-biome.** An entry with `@<widths>` repeats once per that many tile widths. An entry without it, or a
  planet whose tile width cannot be read, takes the global swirl scale.
- **glass-draws-on-water.** The glass list is drawn while `worldTwilightGlass` is on, with water biomes allowed. The swirl
  list is still drawn with water biomes excluded.
- **toggles-scribed-and-drawn.** `worldChillUnlit` and `worldTwilightGlass` default to on, are scribed, are reset, are drawn
  as Mod Settings checkboxes, and are part of the key that redraws the planet when a setting changes.
- **glass-texture-is-the-pick.** `World/RM_Swirls/TwilightGlass.png` in TerminalBiomes holds the same pixels that the sheet
  generator makes for the picked look (`world_water_variants.py`, `PANES3`).
- **dll-built-from-source.** The committed `RimMandrake.Biomes.dll` is the one that its `.srchash` stamped, built from these
  sources.
