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
