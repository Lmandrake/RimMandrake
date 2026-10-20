# WORLD_LAYERS_RESCUE_THE_SAVE_HAS_MORE — offline exporter: save → w9 stamp files, with identity comparison

## why

World remake option D (owner, by question card 2026-10-19; `design/RimMandrake/world_remake_2026-10-19/PLAN.md`
§4 option D and §5a). The w9 stamp files are stale against the save: the 09-12 save holds 27,856 mutator
entries vs 10,084 in `world/ASHKARR_WORLDMAP_mutators.csv` (08-23), 3,008 landmarks vs 563, and the links CSV
(09-07) shares only 77 of the save's 1,399 road edges (`02_world_pipeline.md` §3). No tool writes the save's
layers back into stamp files. A remake from today's files silently loses most authored layers.

## spec

Scope = PLAN.md §5a "export the authoritative layers".


1. **Offline only**, reading a `.rws` through `src/RimMandrake/Utils/worldmap.py` (extend it; do not fork a
   second decoder). Never writes a save.
2. **Name the authoritative save first**, in this file: the 09-12 canonical or a later one carrying post-09-12
   edits. The shortHash table must come from a def dump of the SAME mod set as the save
   (`rimworld-savegame` skill).
3. Write one file per layer, in the shape `w9_run.py` stamps from:
   - **roads and rivers** (edges by tile-ID pair + def) → links file;
   - **mutators** (tile ID + mutator defName, every entry) → mutators file;
   - **landmarks** (tile ID + defName + name) → landmarks file;
   - **settlements** (tile ID, faction defName, settlement name, faction identity) → settlements file;
   - **factions** (defName, name, ideo, relations as needed to recreate) → factions file;
   - **features / region labels and worldTags** → features file.
4. **Compare by identity, not counts**: per layer, a diff of tile IDs, edge topology (road/river graph edges,
   not totals), settlement identity (tile + faction + name) and faction roster against the existing CSVs and,
   once one exists, against a freshly stamped world. Report adds / losses / moves per layer.
5. Names that no longer resolve on the candidate profile
   (`deployed/config/ModsConfig.CANDIDATE_2026-10-19.xml`) are listed, not dropped silently; the port map
   `design/RimMandrake/retired_mutators_port_map.json` is applied as a separate, reported step.
6. Ships with its functional script (debug-process rule) and a selftest on a small fixture save.

## criteria

Running it on the named save writes the six files; the identity diff against the save itself is empty
(round trip), and against the current CSVs it reports the known gaps (≥ 27,856 mutator entries, ≥ 3,008
landmarks, the save's road edges).

## watch out

- Settlements: 121 CSV rows vs 96 canonical NPC settlements — the live roster is canon (owner: *"Live roster
  is canon."*).
- `RUT_Umbra` tiles (2,531) are exported as-is; the paint list moves them onto `RUT_FuelSnows` at the paint.
- Do not use this to generate any alternative planet (CLAUDE.md, no worldgen).

## progress (FOUNDRY helper, 2026-10-19)

- **Authoritative save named:** `Saves/CANONICAL_ASHKARR_START_2026-09-12.rws` as on disk today (sha256/16
  `1ff329161abeaa8c`, mtime 2026-10-09: carries the post-09-12 in-place edits, e.g. the 09-18 Pyrelands switch and
  the 10-09 label curve). Decoded against all four DefDump captures, ranked by share of the save's 616 modIds.
- **Built:** `src/RimMandrake/Utils/world_layers_export.py` (CLI, `--dry-run`), decoders added to `worldmap.py`
  (`WorldGrid.mutator_entries`, `WorldObjects.factions/ideos`), selftest
  `src/RimMandrake/Utils/selftest_world_layers_export.py` (22 PASS). Output `world/rescue_2026-10-19/` (`raw/`,
  `ported/`, `REPORT.md`, `diff.json`); the committed `world/ASHKARR_WORLDMAP_*.csv` are untouched.
- **Measured (tool + `measure csv`):** 27,856 mutator entries on 14,421 tiles · 3,008 landmarks · 326 river and
  1,242 road edges · 95 NPC + 1 player settlements · 26 factions · 71 features · 64 landform overrides. Round
  trip raw and ported: identical.
- **Identity vs the record CSVs:** rivers 326/326 shared · roads 1,177 of the save's 1,242 shared with the
  record (65 new, 210 record-only; the "77 of 1,399" figure was a 09-07 measurement, not today's save) ·
  mutators +18,384 / −612 · landmarks +2,462 / −17 · settlements 27 moved, 60 names only in the save.
- 🔴 **ShortHash collision found:** biome hash 56104 is `RUT_TheForge` in the save (44 tiles, record agrees) but
  `RM_FloodedCanyon` in every current capture (`RUT_TheForge` bumped to 56105). Any decode or load through
  today's table reads those 44 tiles as Flooded Canyon. The exporter settles it; 7 mutator hashes stay
  ambiguous (listed in REPORT.md). Hash 58457 is `RM_FE_Pyrelands` (exact raw hash), not the record's
  `ZBiome_Grasslands`.
- **Not resolvable on `ModsConfig.CANDIDATE_2026-10-19.xml`:** 5 names, 49 entries: the five unported mutators
  (`AB_AncientDeathPallVent` ×33, `AB_DerelictKemeticTemple` ×5, `AB_DerelictBioLab` ×5,
  `WildDantooinePlants` ×4, `AB_DerelictArchonexus` ×2). `08_wave2_prep.md` lists were still pending; re-run
  with `--profile` on the final list.
