## Source
Review B2 (`design/Jawa/worldbuilding/review/WORLDMAP_FINAL_REVIEW_2026-09-08.md`
line ~154): landmark names reused on 2+ landmarks, "Dead Sarlacc" x7 worst.
Corrective: hand-name the ones that matter in faction/region voice, variety for the rest.

## Done 2026-11-03 — offline, in the canonical start save
The world was remade after the 09-09 pass, so its 18-row list was stale: only the seven
Dead sarlacc tiles (1837, 2462, 2463, 2468, 15623, 15905, 20456) survived; the other rows'
tiles carry unique names now. The list was deleted. Measured on
`ASHKARR_DEV_START_2026-10-20_PARITY_QUIET_R3.rws` (canon.yml `planet.start_savegame`):
3008 landmarks, 24 names held by 2+ landmarks (56 rows), and tile 2403's `RUT_GapingDoom`
named "Asonistia City" (its def's `NamerLandmark_Ruins` rolled a city name at the remake).

- **Route:** `Landmark.name` is a plain scribed string, so the rename is an offline text
  edit of one `<name>` element, no live game: `src/RimMandrake/Utils/landmark_rename_save.py`
  (every row guarded by tile + def + old name; plans and verifies all saves before writing any;
  backup `<save>.bak-pre-<tag>`). The live tool `jawa/world_landmark_rename` still exists for a
  running game.
- **Table:** `infrastructure/state/items/LANDMARK_NAMING_PASS_1.renames.json`, 33 rows: The
  Gaping Doom, six Dead sarlacc in regional voice (15623 keeps the name), and one row per extra
  holder of the other 23 names, named from the tile's region in `world/ASHKARR_WORLDMAP_tiles.csv`.
  The first holder of each name keeps it. Delegated: naming (not on delegation_policy.md §2).
- **Applied** to the Saves file and its repo copy `world/` (both sha256 `cfeb45446ff2f188…`);
  only those 33 lines changed. Backups: `Saves\…R3.rws.bak-pre-landmark-names-2026-11-03` and
  `D:\ClaudeWork\backups\saves_pre_landmark_names_2026-11-03\`.
- **Proof:** `python3 src/RimMandrake/Utils/landmark_names_check.py` exits 0: both copies
  identical, no name held twice, 2403 = The Gaping Doom, every table row reads back.

## Left for later
- A running game that already has R3 loaded holds the old names in memory; saving it over R3
  would undo this. Load R3 fresh before any re-save.
- The final repaint (`BIOME_PAINT_ONCE_AT_THE_END_1`) saves a new start; if it is not built on
  this R3, rerun the tool with the same table (its guards refuse any tile that changed).
