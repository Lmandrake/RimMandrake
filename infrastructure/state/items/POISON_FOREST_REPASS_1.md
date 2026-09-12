# POISON_FOREST_REPASS_1 — poison_forest.md second pass

Filed thin; this file written with the work, 2026-09-11.

## spec

`design/Jawa/worldbuilding/biomes/poison_forest.md` second pass, in the register the
sibling sheets set (nightside_ice §0 measurements; blue_desert/propane_lakes/
forsaken_crags §4b weather). Sheet is FROZEN under `BIOME_FREEZE_FABLE_REVIEW_1`:
amendments add detail, no ruling changes; R13
(`_freeze_rulings_2026-09-07.md`) itself orders the temperature/vent amendment.

1. **§0 MEASURED block** — tiles, arc, temp, elevation, rain, water, hilliness,
   spread, def binding, weather record; every number from a named instrument
   (`world/ASHKARR_WORLDMAP_tiles.csv`; `infrastructure/state/canon.yml`;
   `_def_bindings_2026-09-09.md`; DefDump `defs.sqlite` capture 2026-09-11);
   UNMEASURED labelled honestly.
2. **§4b weather table** — sibling register; grounded in the def's one real record
   (`PoisonForestSpores` × 18), R-H1 (no rain), R-H2b (condensation), R13 (vapour).
3. **R13 written through** — chemical venting replaces the thermal-boundary pump;
   temperate/stable replaces the cold/freezing framing; §2 header, §2 bullets, §3,
   §5, §6 ban amended.
4. **Struck phrasing deleted** — the R13-struck lines ("vents keep the ground just
   above freezing", "cold gas vents", "cold but not frozen", "cold stable ceiling",
   "just above freezing and humming", "the vents are COLD") removed outright;
   strike-reason lives in `_freeze_rulings_2026-09-07.md` R13, git is provenance.
   The sheet held no `~~` markup. Kept: the owner-accepted arc-tails ruling
   (moved into §0 — its evidence would otherwise mislead on the band envelope).

## verify

- `grep -in "just above freezing\|cold gas vent\|cold but not frozen\|cold stable ceiling" design/Jawa/worldbuilding/biomes/poison_forest.md` → no hits.
- §0 exists; each line names its instrument; tile-count disagreement (546/557/604)
  is stated, not smoothed.
- §4b exists in the sibling table register; no water rain; no ruling contradicted.
- No edit outside the sheet and this file. No worldgen. No defNames guessed
  (`PoisonForest`, `PoisonForestSpores` read from the DefDump sqlite).

## criteria

- All four asks landed as amendments-adding-detail; zero frozen rulings changed.
- Contradictions carded, not resolved in place:
  - **CARD** — PoisonForest tile-count instruments disagree: CSV 546 (read
    2026-09-11) vs live V26 census 557 (owner-accepted 2026-09-08) vs canon.yml
    `biome_tile_counts` 604 (2026-08). One census needs declaring current for the
    frozen world; sheet §0 states all three.
  - **CARD** — §4b weather names (scatter-dusk, vent bloom, vapour bank, dewfall)
    are BENCH-drafted; sibling tables were owner-ratified, so these are owed a
    sitting. Def work (weather defs beyond `PoisonForestSpores`) owed with them.
