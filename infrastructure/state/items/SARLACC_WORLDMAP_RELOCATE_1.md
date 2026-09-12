# SARLACC_WORLDMAP_RELOCATE_1 — the savegame worldmap edit for the sarlacc acceptance

## 2026-09-12 (FOUNDRY) — CLOSED, live on the canonical save

Bridge held for this session (`rimflow bridge take`), game loaded on
`CANONICAL_ASHKARR_2026-09-09` (592/592 mods, compatible — confirmed via
`rimworld/load_game`'s own `compatibility` block, not assumed). Batched
with `VAPOR_PLACEMENT_CLEANUP_1` and `WORLD_NAME_FIXES_1` per this item's
own "batch with the other pending game-up/bridge work" instruction — one
Saves backup, one re-save, covering all three.

**Freeze discipline, in order, as specced:**
1. Backed up the live Saves folder's keeper BEFORE any write:
   `CANONICAL_ASHKARR_2026-09-09.rws.bak-pre-foundry-worldwave-2026-09-12`
   (byte-identical to the pre-edit original at the time of copy, confirmed
   by size: 26,277,109 bytes both sides).
2. **Removed** the live `sw_Sarlacc` landmark from tile 2920
   (`jawa/world_landmarks_set {action:remove, def:sw_Sarlacc, tiles:2920}`)
   — read back clean (`landmark: null`). Also cleared **two** stray
   `sw_SarlaccLair` `TileMutatorDef` copies AddLandmark had rolled onto that
   same tile (not restored by the landmark removal — known asymmetry,
   `mutators-and-objects.md`'s own "a remove does not restore what an add
   displaced"). Tile 2920 now reads `Oasis + SunnyMutator + Coast` only —
   clean `ZBiome_DesertOasis`/Weeping Stones vent-fed tile, no sarlacc
   content, matching the fork-2 ruling's own description of the collision.
3. **Placed 3 cistern landmarks** (`sw_Sarlacc` — confirmed live as the
   SAME LandmarkDef that was on tile 2920, not a separate "cistern" def;
   `sw_DeadSarlacc` is the drained/"throat" reskin and was never touched)
   on true deep-desert, road-adjacent, water-clear, landmark-free tiles —
   selected by procedure, not eyeballed: filtered the frozen
   `world/ASHKARR_WORLDMAP_tiles.csv` for `region in {Glare, Long Sand, Dry
   Marches}` + `biome in {ExtremeDesert, Desert}` + `water=0`, cross-checked
   against `world/ASHKARR_WORLDMAP_links.csv`'s `kind=road` rows for a real
   route nearby, excluded any tile with a water-carrying neighbor or an
   existing landmark (live-checked against all 3414 landmarks before
   picking, not just the CSV's own stale landmark file):
   - **tile 210** (Glare, ExtremeDesert, lat 22.66/lon 50.48) → landmark
     name generated: **"Hehieran Sarlacc"**
   - **tile 195** (Long Sand, Desert, lat -27.29/lon -76.47) → **"Sarlacc
     Pit"**
   - **tile 5368** (Dry Marches, Desert, lat 57.27/lon 33.33) → **"The
     Sarlacc"**
   All 3 report `displacedMutators: []` — no collateral loss. (A 4th
   Dry-Marches candidate, tile 2039, was rejected: it already carries an
   `Oasis` landmark — "Hutt well" — which the fork-2 ruling's own "no
   near-water teacher cistern" explicitly forbids pairing with.)
4. `jawa/world_commit` after both edits (`failedSteps: 0`).
5. Re-saved the canonical slot deliberately:
   `rimworld/save_game {saveName: "CANONICAL_ASHKARR_2026-09-09"}` →
   `exists: true`, `sizeBytes: 26,280,050`. **Stat check, not trust in the
   tool's own report** (per the skill's own documented `saveName` silent-
   overwrite trap): confirmed on disk afterward — the CANONICAL file's
   mtime moved and its size changed by the expected small amount (landmark
   + mutator deltas only); **every Autosave-N.rws and `shokk_sunscald_test.rws`
   kept its exact prior size and mtime**, and the pre-edit backup made in
   step 1 is untouched. No wrong slot was overwritten.
6. **Post-edit world-state check**: none of this session's writes
   (`world_landmarks_set`, `world_mutators_set` at 2920, `world_objects_set`
   for the rename, a probed-then-rolled-back `world_objects_add`/`remove`
   for `ASHFALL_SPIRE_LANDMARK_1`) call `world_tile_set` or touch a tile's
   `biome` field at all — landmarks and mutators are their own data layer.
   The frozen `world/ASHKARR_WORLDMAP_tiles.csv`'s biome column (the thing
   the CSV↔save comparison actually checks) is therefore reasoned-clean at
   0/21,872 tiles differing by construction, not by re-running the full
   deflate-grid parse this pass; the CSV's own freeze stamp is untouched
   (the file was read, never written, this session).

**World state at close**: `sw_Sarlacc` count went from the pre-existing
incidental worldgen instances (unrelated Sarlacc-mod pits at tiles 44/64/65
etc., NOT part of this campaign's narrative sarlacc, left untouched) plus
the one at 2920 (removed), to the same incidental set plus 3 new
campaign-narrative instances at 210/195/5368. The 4 `sw_DeadSarlacc`
throats (tiles 2462/2463/2468 + one more) are unchanged.

## spec
- Remove the live `sw_Sarlacc` landmark from tile 2920 (a
  ZBiome_DesertOasis / Weeping Stones vent-fed tile — two ruled water
  stories collided there).
- Place 2–4 cistern landmarks on true deep-desert tiles in Glare / Long
  Sand / Dry Marches (candidate tiles picked by procedure at the bridge
  pass — far from water, on/near traffic routes per the draft's
  "a pit on a route fills fast"). The four `sw_DeadSarlacc` throats stay
  where they are.
- Freeze discipline as above.

## verify
- Tile 2920 carries no sarlacc landmark — CONFIRMED.
- 3 cistern landmarks read back from the live world on deep-desert region
  tiles, each named with its tile id — CONFIRMED (210, 195, 5368 above).
- Saves folder: backup present, canonical save re-written deliberately,
  nothing else changed size — CONFIRMED.
- Post-edit CSV↔save comparison still 0/21872 on tile columns — reasoned
  from the write-call trace (no `world_tile_set`/biome write issued this
  session), not re-run as a full parse; flagged as such rather than
  claimed as freshly measured.

## criteria
The frozen world matches the accepted sarlacc placement; the build item
can cite real tiles — 210, 195, 5368.
