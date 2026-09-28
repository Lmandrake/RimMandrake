# CHILL_RENAME_FULL_1 — full RM-tier rename: the Propane Lake becomes the Chill

## what

Owner typed this session (2026-09-27): *"And it needs a new name. Let's call it
the Chill."* Scope ruled by question card same sitting: **full RM-tier rename** —
defNames, terrain defs and references move to `RM_TheChill*` now, before more
content accretes; player-facing label "the Chill"; descriptions and design docs
updated (deletion rule: old name removed, git is provenance).

- `RM_PropaneLake` (BiomeDef, `src/RimMandrake/TerminalBiomes/Defs/BiomeDefs/RM_PropaneLake.xml`)
  → `RM_TheChill`. Terrains `RM_PropaneLakeDeep`/`RM_SolidPropane`
  (`RM_PropaneLakeTerrains.xml`) move with it; exact terrain names are the
  builder's choice inside the tier grammar.
- Patches referencing the RM def (`MechClusterBiomes_AmbientDoctrine.xml`) move too.
- Update the paint list entry (`BIOME_PAINT_ONCE_AT_THE_END_1`) to the new defName.

## hard boundaries

- ⛔ **`RUT_PropaneLake` is FROZEN carrying the live save — do not touch its
  defName until the terminal repaint.** Its label/prose may say "the Chill"
  only if that is save-safe; when in doubt leave the RUT twin entirely alone.
- The substance is still propane — descriptions keep the fuel-lake fiction;
  only the *place* is named the Chill.

## found while filing — fix during the rename

The RM tier's catch wiring references campaign-tier defs: `fishTypes` rows
`RUT_Fessu/RUT_Krellik/RUT_Oddu/RUT_Oovu/RUT_Iliss/RUT_Tarnn/RUT_Zhiil` and
`rareCatchesSetMaker RUT_RarePropaneCatches`. Per Q11a the RM_ biome must stand
alone without the campaign layer — audit these while renaming and give the RM
tier its own catch items/set maker (e.g. `RM_RareChillCatches`), with the RUT
layer patching its campaign versions on top.

## provenance

Name: owner typed. Scope (full rename incl. defNames/terrains): decision taken
by question card 2026-09-27. Filed by BENCH out of the Chill concept sitting.
