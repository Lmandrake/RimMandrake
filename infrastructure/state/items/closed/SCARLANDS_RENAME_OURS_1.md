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

## 🔴 Owner ruling 2026-09-21, and closed on it

**Name: `Warscar`, article dropped** — owner, verbatim: *"Wars[c]ar. Drop the 'the'"*, in
answer to the drafts sheet's recommended row 1 (`the Warscar`). Every other biome label in
`biome_mod_architecture.md`'s table keeps the house `the Xxx` form; this one deliberately
does not.

**What shipped:** `RUT_Scarlands`'s own `<label>` changed from `the Scarlands` to `Warscar`
(`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Scarlands.xml`). Zero live-tile risk —
MEASURED via `worldmap.py` against `CANONICAL_ASHKARR_START_2026-09-12.rws`: `RUT_Scarlands`
carries exactly 90 live tiles, all keyed by defName/shortHash, untouched by a label edit.
This alone resolves the measured collision: the biome list no longer shows the same label
twice.

**Found and deliberately NOT touched:** `BiomeNames_Ashkarr.xml` / `BiomeDescriptions_Ashkarr.xml`
separately patch the VANILLA `Scarlands` defName (bare, Odyssey's own) with `the Scarlands`
label plus our own flavor description/settleWarning (`BIOME_TEXT_PORT_1`) — a second, older,
0-live-tile entry carrying near-identical Jawa lore text to `RUT_Scarlands`. This item's own
spec ruled out fixing the collision by patching the DLC's def, so it stands untouched; it is
now a live-but-unused near-duplicate of our own biome's flavor, which the row-20 migration
below should account for (does the mod set still need to carry the vanilla-Scarlands text
port once `RM_Warscar` exists, or does that patch become dead weight?).

**Not done here, tracked separately:** the defName move (`RUT_Scarlands` → `RM_Warscar`) and
absorbing `mandrake.rut.scarlandsladder` is `biome_mod_architecture.md` row 20's own
twin-pair migration — the same weight of work Pyrelands and GelatinousSlime got as their own
items, not a rename-item afterthought. Filed as `SCARLANDS_STANDALONE_MOD_1`.

Criteria met for the immediate collision (label no longer duplicates vanilla's); closing.


🔴 **REVERSED 2026-09-26 — the label is now `the Warscar`.** The owner ruled by question card that the house `the Xxx` form applies to every biome with no exceptions, overturning the article-dropping call recorded above. All 27 RM-tier biome labels now carry the article (MEASURED 2026-09-26). The live authority is `design/RimMandrake/biome_mod_architecture.md` §7 Q5. This item stays closed; only the article changed, not the name.
