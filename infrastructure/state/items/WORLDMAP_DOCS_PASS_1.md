# WORLDMAP_DOCS_PASS_1 — worldmap canonical-docs pass: the one remainder

Rulings 1-9 of the 2026-09-18 sitting all landed (ledger notes on this item, 2026-09-18). The only
work left is ruling (h), the owner's card answer of 2026-09-18: *re-audit REGIONS_THAT_LIE against
today's world, then card only still-true rows.* Triage 2026-10-29 (Conductor): this is agent work.

## spec

1. Re-audit `design/Jawa/worldbuilding/REGIONS_THAT_LIE.md` (2026-08-23, 13 of 71 regions "lie")
   against **the painted worldmap**, which is the 2026-10-20 dev world:
   `world/paint_inputs_2026-10-20/ASHKARR_WORLDMAP_tiles.csv` plus its render report
   (`design/RimMandrake/biome_rulings.md`, "The painted worldmap answers which biomes exist",
   owner 2026-10-28). Not the 09-12 record, not a live tile count.
2. For each row: STILL TRUE / FIXED / MOOT, with the measured number that decides it.
3. A still-true row is fixed in prose (rename the region or reword its lore so the name tells the
   truth) under `delegation_policy.md` §1 `design` (prose and labels a player reads), judge-checked
   per §4, logged `--why "delegated: design"`. That replaces "card the rows": the 2026-10-22
   delegation retired taste cards. No owner card.

## Out of bounds (standing rulings)

- No worldgen of any kind, and no repaint: tiles change only at the one final paint
  (`BIOME_PAINT_ONCE_AT_THE_END_1`, owner 2026-09-20). A row whose only fix is repainting tiles is
  marked "waits for the final paint" and handed to that item, not fixed here.
- A biome of ours on 0 tiles is expected, not a lie.

## criteria

- `REGIONS_THAT_LIE.md` carries a dated re-audit table (every row has a verdict and a measured number
  from the painted map) and its status line says which rows remain.
- Every renamed region or reworded lore line is a commit with a `Delegated: design` body line and a
  judge verdict under `infrastructure/state/delegated/<date>/`.
- Repaint-only rows are listed on `BIOME_PAINT_ONCE_AT_THE_END_1` by note.
