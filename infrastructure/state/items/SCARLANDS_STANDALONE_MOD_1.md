# SCARLANDS_STANDALONE_MOD_1 — Scarlands biome-mod split: RM_Warscar, absorb ScarlandsLadder

## the ask

`biome_mod_architecture.md` §7 Q5 / row 20's own twin-pair migration, unblocked now that
`SCARLANDS_RENAME_OURS_1` closed the naming pick: owner ruled `Warscar`, article dropped.
`RUT_Scarlands`'s `<label>` already carries the new name (immediate collision fix, done);
this item is the rest of row 20 — the actual defName move and mod consolidation, the same
weight of work Pyrelands (`PYRELANDS_DEFNAME_RENAME_1`, and its own earlier standalone-mod
landing) and Greentide (`GREENTIDE_STANDALONE_MOD_1`) already got.

## spec

- **New biome def:** `RM_Warscar`, label `Warscar` (no article — deliberate, per the
  owner's ruling; every other row in the architecture table keeps `the Xxx`), tier
  RimMandrake, packageId `mandrake.rm.warscar`. Same content as `RUT_Scarlands` carries
  today (crater fields/slag hills flavor, `RimWorld.BiomeWorker_Scarlands` reused per the
  architecture table's existing note, settleWarning, terrain).
- **Absorb `mandrake.rut.scarlandsladder`** (the `ScarlandsLadder` mod, currently its own
  package under `src/RimUtinni/ScarlandsLadder/` — `RUT_ScarlandsLadder.xml` lore stage
  table) into the new RimMandrake mod, per the architecture table's row-20 note.
- **Live-tile safety — MEASURED 2026-09-21:** `RUT_Scarlands` carries 90 live tiles on
  `CANONICAL_ASHKARR_START_2026-09-12.rws` (`worldmap.py` census, cross-checked against the
  def dump's shortHash table). Follow the exact `UMBRA_IS_A_REGION_NOT_A_BIOME_1` pattern —
  do NOT delete `RUT_Scarlands` outright. Either keep it as a compatibility duplicate
  (old name, old content) until the terminal repaint reassigns those 90 tiles to
  `RM_Warscar`, or repoint them live via the bridge if that is judged lower-risk this time —
  the Umbra item's own addendum explains why the duplicate was chosen there.
- **The satellite `RUT_Scarlands*` defs** (`RUT_ScarlandsMark` hediff, `RUT_ScarlandsMarkLock`
  / `RUT_ScariaOnsetArming` game conditions, `RUT_ScarlandsSprungDangers` genstep+prefab,
  `RUT_ScarlandsMarkThoughts`) do NOT need renaming for this item's criteria — they are not
  part of the measured collision and are not referenced by name anywhere outside their own
  patches. Rename them only if the row-20 migration's own naming consistency demands it;
  don't invent extra scope.
- **Found and unresolved, worth checking here:** `BiomeNames_Ashkarr.xml` /
  `BiomeDescriptions_Ashkarr.xml` separately patch the VANILLA Odyssey `Scarlands` defName
  (bare) with our own flavor text (`BIOME_TEXT_PORT_1`) — a second, 0-live-tile entry
  carrying near-identical lore to ours. Once `RM_Warscar` exists and (eventually) owns all
  90 tiles, decide whether that vanilla-biome text-port patch is still doing anything or is
  dead weight to retire.

## Watch out

- Don't cite a tile count as evidence about paint-readiness — the planet is painted once at
  the end (`BIOME_PAINT_ONCE_AT_THE_END_1`).
- `validate_patch.py --live --defs` after any defName move; the xpaths in
  `BiomeNames_Ashkarr.xml`/`BiomeDescriptions_Ashkarr.xml` target `Scarlands` (vanilla,
  unrelated to this rename) and `RUT_Scarlands`'s own satellite patches — check each still
  resolves.

## criteria

`RM_Warscar` exists as a real RimMandrake-tier biome, `mandrake.rut.scarlandsladder` is
absorbed into it, the 90 live tiles on the canonical save are not orphaned (re-measure with
`worldmap.py`, not trusted from this note), and row 20 in `biome_mod_architecture.md` reads
DONE instead of PROPOSED.
