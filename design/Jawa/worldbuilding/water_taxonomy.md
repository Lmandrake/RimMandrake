# The waters of Ash'karr — taxonomy wrapper

_`WATER_KINDS_TAXONOMY_1`. **The data is `water_taxonomy.csv`** — one row per
kind, columns: id, name, source biome, is_water, contents/hazard, potable,
transmutations_out, sheet ref. This file only says how to read and change it._

- **The CSV is the taxonomy** (owner rule: rules are data, not prose). A water
  mentioned in any biome sheet must resolve to a row; a new water lands as a
  new row citing its sheet, or it is drift.
- **Three things that look like water are not**: the Sheen (fungal emission),
  hydrocarbon rime/etchfall (chemical frost), the propane lakes (cryogenic
  hydrocarbon). Their rows carry `is_water = NO` so nothing downstream treats
  them as a drink or a distillation input.
- **Transmutations** (`transmutations_out`) are the processes that move one
  kind toward another: sunning, cooling+sterilizing, distillation, melt/freeze,
  evaporation→fog→condensate, mineral concentration, the Slime's
  toxic-for-distillation carve-out, the Wasteland's sequestration.
  ⚠️ **The transmutation list is NOT yet owner-ruled** — the item's verify line
  requires his ruling; rows may gain/lose transmutations at that sitting. Two
  rulings already hard: **the Scald is never potable** (no transmutation ends
  there), and slime water counts as **toxic water for distillation purposes**.
- **Stack mapping (owed, before any item defs)**: Dubs Bad Hygiene is live in
  the stack (`DBH_` defs MEASURED 1,262 in the 2026-09-05 capture) and grades
  water in its C# — verify its actual grades (and FluidCanals, and the four
  liquid biomes of `LIQUID_BIOMES_MAP_1`) against this table before authoring
  any water item/terrain defs. Do not assume DBH's kinds are the ceiling.
