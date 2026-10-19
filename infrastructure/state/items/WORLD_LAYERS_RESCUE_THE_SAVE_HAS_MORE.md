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
