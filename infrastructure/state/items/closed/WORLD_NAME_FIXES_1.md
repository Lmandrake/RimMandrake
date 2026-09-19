# WORLD_NAME_FIXES_1 — seven ruled renames, one bridge pass

All names RULED (owner cards 2026-09-12; proposals + rulings in
design/Jawa/world_rename_proposals.md). Game is UP.

## The renames
| current | new | kind |
|---|---|---|
| Colony (PlayerColony settlement) | Zeddo's Salvage Yard | settlement (owner verbatim) |
| Specimen Hall (Helix) | Site Aurek | settlement |
| The Revision (Helix) | Farside Station | settlement |
| The Fair Copy (Helix) | Site Cresh | settlement |
| Cold Archive (Helix, tile 17901) | Cold Stores | settlement |
| Fall Line Barrens | The Breaks | WorldFeature |
| Scald Spine | Cratercrown | WorldFeature |

## spec
- One bridge pass, freeze discipline: Saves backup + stat-after, renames via
  the world/settlement tools, world_commit, read every name back, deliberate
  canonical re-save. Batch with any other pending world edits
  (SARLACC_WORLDMAP_RELOCATE_1, VAPOR_PLACEMENT_CLEANUP_1) if practical.
- The two FEATURE renames change the CSV's region column values → re-run the
  region comparison and re-stamp world/ASHKARR_WORLDMAP_tiles.csv.frozen.json
  in the same change (approved mechanism, CSV_REGION_SYNC_1 precedent).
- Check inbound doc references to the six old names post-rename
  (delete-don't-supersede: fix in the same change; fall_line.md is frozen —
  amend-under-freeze note if it names the Barrens).

## verify
All seven new names read back live; old names return zero hits in a live
feature/settlement read; CSV↔save comparison clean; frozen.json stamp
matches bytes.

## done — 2026-09-13, FOUNDRY bridge pass

**All seven rows now hold.** Row 1 (`Colony` → `Zeddo's Salvage Yard`) was already
applied by the 2026-09-12 pass and verified here, not re-written: world object 277,
tile 17007, `namedByPlayer: true`. The six outstanding renames were applied this pass:

| new name | kind | id | tile |
|---|---|---|---|
| Site Aurek | Settlement | 251 | 12082 |
| Farside Station | Settlement | 250 | 8200 |
| Site Cresh | Settlement | 252 | 5912 |
| Cold Stores | Settlement | 249 | 17901 |
| The Breaks | WorldFeature | 63 | 153 tiles |
| Cratercrown | WorldFeature | 67 | 174 tiles |

- `jawa/world_objects_set` (one call per object, `changed: 1`, `notFound: []`,
  `errors: []`) and `jawa/world_features_set` (`action: update`, which also sets
  `textsCreated = false` so the drawn label is rebuilt), then one `jawa/world_commit`
  (all draw layers `ok`).
- **Read back on an independent channel, not on `success: true`:** a fresh
  `jawa/world_objects_get` (196 objects, 96 named) and `jawa/world_features_get`
  (71 features) — all seven NEW names present at the ids above, all seven OLD names
  return **zero** hits in both reads. `jawa/world_objects_validate` clean
  (0 null-faction, 0 bad tile, 0 stacked, 0 on water/impassable).
- **Backup before any edit:** `CANONICAL_ASHKARR_START_2026-09-12.rws.bak-pre-world-name-fixes-2026-09-13`,
  byte-identical to the pre-pass canonical at 16,459,357 B (`stat` on both).
- **Deliberate canonical re-save** to `CANONICAL_ASHKARR_START_2026-09-12` —
  16,459,357 → **16,466,734 B**. Saves-folder `stat` before/after: 31 files before,
  31 after, **exactly one line changed** (the intended slot); no new file, no other
  file's size moved, so `saveName` was honoured. The written `.rws` carries all seven
  new names and none of the six old ones.
- **Frozen CSV region column re-stamped:** 327 rows changed in
  `world/ASHKARR_WORLDMAP_tiles.csv` (153 `The Breaks` + 174 `Cratercrown`, matching
  the live `tileCount` for features 63 and 67 exactly); bytes 1,795,221 → 1,794,150,
  which is exactly 153 × −7 for the shorter name and 0 for the same-length one.
  `verify_frozen.py --restamp` → ✅ CURRENT, sha `9fad81980ea4`, 21,872 rows.
- **Inbound references fixed in the same change** — listed in
  `design/Jawa/campaign/CAMPAIGN_ARC_GATHER.md` ¶ at G81. `fall_line.md` does not
  exist and no biome sheet carries a freeze marker, so no amend-under-freeze note
  was owed; `world/ASHKARR_WORLDMAP_tiles.csv` is the repo's only frozen artifact.

**Not done here, deliberately:** dated provenance was left carrying the old names —
`design/Jawa/world_rename_proposals.md` (the proposal record the owner picked from),
closed item records and reboot handoffs, `Transient/`, `infrastructure/state/backups/`,
and `data/river_graph_2026-09-07.csv`. Rewriting those would falsify what was true
when they were written.

⚠️ Note for whoever reads the canonical save next: this re-save promoted the live
world into `CANONICAL_ASHKARR_START_2026-09-12.rws`, which means that slot now also
carries `BIOME_WORLD_SWITCH_WAVE_1`'s 17,667-tile repaint (the previous pass saved
that to its own slot and left canonical behind). The canonical CSV was already
rebased onto those biomes, so save and CSV now agree; the pre-pass canonical is in
the `.bak-pre-world-name-fixes-2026-09-13` file above if that promotion needs undoing.
