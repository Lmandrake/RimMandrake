# NIGHTSIDE_ICE_DESIGN_SITTING_1 — the Nightside Ice design sitting

BENCH picked the Nightside Ice as the next biome to refine to full mod glory
(owner directive, typed 2026-09-24: "Wake bench. Pick the next biome to
bedazzle!"). Follows the sitting pattern of Weeping Stones
(`WEEPING_STONES_DESIGN_SITTING_1`, closed 2026-09-24), the Sump and Webwork
before it.

## why the Nightside Ice

- **Thinnest clean candidate left, and 100% donor cast**: 10 fauna, every one
  an `AA_*` donor import, 0 owned defs (MEASURED 2026-09-24,
  `design/Jawa/worldbuilding/biomes/rosters/nightside_ice.json`). Under Q11a
  the `RM_NightsideIce` mod must stand alone rich; today it owns nothing.
- **Big canvas**: 1,506 tiles on the frozen worldmap record — 5th largest land
  biome (row 5, `biome_mod_architecture.md` §5). Note: tile counts are the
  2026-09-12 CSV record, cited for relative size only, not live state.
- **The sheet is FROZEN and strong** (`nightside_ice.md`, second pass
  2026-09-06, freeze 2026-09-07): the drain of the atmosphere — dirty white
  ice on the highest ground of the night, under the aurora, with something
  moving inside it. §6's laws bind hard: no liquid water ever, no
  photosynthesis, flora ships EMPTY by law (the roster's `flora_purged`
  records it), no fish. The bestiary carries the whole biome.
- **Not entangled**: no kit spec, no mechanics item in flight, no art in the
  pipe. Blue Desert (the only thinner roster, 3/2) stays excluded — its life
  pass closed 2026-09-21 (`BLUE_DESERT_LIFE_AUTHORING_1`, dorrak/krissek/
  vekkit + fractal flora) with 11 art jobs still in the artpipe queue; sitting
  on it now would judge art that hasn't landed. Pyrelands is a reconciliation
  case (content lives on `RM_FE_Pyrelands`, donor def row), not a bedazzle.
  Rust Cathedral has the open wall-tier GenStep bug
  (`RUST_CATHEDRAL_MECHANICS_1`); Warscar has `SCARLANDS_MECHANICS_2` doing;
  seas belong to `SEA_FLOOR_AND_CATCH_PASS_1`.
- **Synergy with the rename gate**: `NONCANON_BEAST_RENAME_1` Phase 1 sheets
  are gated on the owner, and
  `noncanon_beast_names_crags_nightside_contagion_slime.md` covers this
  biome's cast — the sitting can rule the Nightside rows in the same breath.
- Sittings already done: Greentide, Fever Wood, Miasma, Webwork, Sump,
  Weeping Stones.

## spec

Run the sitting with the owner, Weeping Stones pattern: walk the frozen sheet
biome-by-section, enrich the bestiary to a cast the `RM_` mod can own outright
(invented names live in the RM tier per Q11a; genuine canon routes through the
Utinni patch layer), rule the donor imports (port / replace / cut, per-biome
per Q12's ruling: invented-name moves happen at THIS sitting), rule the
Nightside rows of the noncanon-rename sheet, and land every ruling as
amendments on the sheet + roster JSON. Output feeds
`NIGHTSIDEICE_RM_MOD_BUILD_1`.

## verify

Sheet amendments committed; roster JSON updated with owned cast; every donor
row carries an owner ruling; rename-sheet Nightside rows ruled.

## criteria

The owner has ruled the full Nightside Ice cast and the build item's input is
complete enough that FOUNDRY needs no design decisions.
