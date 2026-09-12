# SARLACC_WORLDMAP_RELOCATE_1 — the savegame worldmap edit for the sarlacc acceptance

The live-world half of SARLACC_HABITAT_BUILD_1, split out because it touches
the CANONICAL frozen save. Owner acceptance 2026-09-12 (rulings in
`design/Jawa/worldbuilding/sarlacc_native_habitat_draft.md` §8, fork 2).

## spec
- Remove the live `sw_Sarlacc` landmark from tile 2920 (a
  ZBiome_DesertOasis / Weeping Stones vent-fed tile — two ruled water
  stories collided there).
- Place 2–4 cistern landmarks on true deep-desert tiles in Glare / Long
  Sand / Dry Marches (candidate tiles picked by procedure at the bridge
  pass — far from water, on/near traffic routes per the draft's
  "a pit on a route fills fast"). The four `sw_DeadSarlacc` throats stay
  where they are.
- 🔴 Freeze discipline, in order: back up the Saves folder's keepers and
  stat afterwards (a NEW file must appear, no existing one changes size);
  bridge edits + `world_commit`; read back via `jawa/world_*` (100-row cap);
  re-save the canonical slot deliberately; re-run the CSV↔save comparison —
  landmarks are not a CSV column, so the CSV should be UNCHANGED (0/21872
  tiles differ) and its freeze stamp untouched; if anything tile-level DID
  move, stop and diff before any re-stamp.
- ⚠️ Batch with the other pending game-up/bridge work rather than spending
  a lone session: the Abandoned Mines per-tile query (CSV_REGION_SYNC_1),
  VAPOR_TERMINATOR_GEYSER_FIX_1 / VAPOR_PLACEMENT_CLEANUP_1, and
  BIOME_OWNERSHIP_WAVE_1's repaints all want the same open save.

## verify
- Tile 2920 carries no sarlacc landmark; N (2-4) cistern landmarks read
  back from the live world on deep-desert region tiles, each named with its
  tile id on this item.
- Saves folder: backup present, canonical save re-written deliberately,
  nothing else changed size.
- Post-edit CSV↔save comparison still 0/21872 on tile columns.

## criteria
The frozen world matches the accepted sarlacc placement; the build item can
cite real tiles.
