# SCARLANDS_RENAME_OURS_1 — our Scarlands collides with vanilla Odyssey's

## the ask

🔴 **Owner ruling, 2026-09-21 (BENCH question card): rename OURS.**

MEASURED: vanilla Odyssey ships a `Scarlands` biome whose player-facing label is *"the
Scarlands"*, and our `RUT_Scarlands` carries the identical label. Since the 2026-09-19
ruling that **all test mod lists include all five expansions**, both are always loaded, so
the biome list shows the same name twice.

⛔ Not "keep the name". ⛔ Not patching the DLC's label — ours moves.

## spec

1. Take the replacement name from `WORLD_LABEL_SIZE_HIERARCHY_1`'s sibling draft file
   `Transient/biome_name_drafts_2026-09-21.md` once the owner picks a row, or put a fresh
   card to him. **Do not invent one and ship it.**
2. Rename the defName and the label together; check `texPath`s and any C# string literals.
3. Blocks `design/RimMandrake/biome_mod_architecture.md` §7 Q5 until done.

## Watch out

- ⛔ Do not cite a tile count as evidence about this biome. The planet is painted once at
  the end.

## criteria

Our biome carries a defName and a player-facing label that neither collides with vanilla
Odyssey's nor reads as the same place, and §7 Q5 is marked answered.
