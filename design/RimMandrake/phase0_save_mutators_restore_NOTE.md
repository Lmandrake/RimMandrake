# Donor tile mutators stripped from the donor-free save — where to put them back

## README — read this at the repaint

Owner, 2026-10-15 (Q3, by card on the Phase 0 P6 census): strip the Star Wars Animal Collection
mutators from the donor-free copy now, *"but make a clear note of where to put things back later
once we regenerate."*

**What was removed:** 1,429 mutator entries on 1,419 world tiles of
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\CANONICAL_ASHKARR_START_2026-09-12_donorfree.rws`
— `WildTattooinePlants` 1,403 · `sw_DeadSarlaccCave` 12 · `sw_SarlaccLair` 8 · `WildDantooinePlants` 4 ·
`WildGalacticPlants` 2. Every tile, its old mutator and its new name is in the data file
`design/RimMandrake/phase0_save_mutators_to_restore.json` (`entries[]`). The `sarg.alphabiomes`
`AB_*` mutators were left in place (that mod is still in the save's mod list).

**Where they go back — the one-time planet repaint (`BIOME_PAINT_ONCE_AT_THE_END_1`):**

1. The repaint is `design/Jawa/worldbuilding/WORLD_REDRAFT.md` step 4,
   `src/RimMandrake/Utils/w9_run.py`. Its **stage 4b ("the derived mutators", after landmarks)**
   reads `world/ASHKARR_WORLDMAP_mutators.csv` (`tile,mutators`, `;`-separated) and adds each row
   through `jawa/world_mutators_set`. **That CSV is the place to restore them**, before the run.
2. **Sarlacc mutators:** add `RSW_SarlaccLair` / `RSW_DeadSarlaccCave` to the tiles listed in the
   JSON (16 tiles; 15 of them carry an `RSW_Sarlacc`/`RSW_DeadSarlacc` landmark, which stage 4
   re-stamps and which rolls its own required mutator — check for doubles). The CSV still spells 5
   of its own rows `sw_SarlaccLair`/`sw_DeadSarlaccCave`; rename those to the `RSW_` names at the
   same time.
3. **Wild-plant mutators** were ported 2026-10-19 (owner: *"Reproduce the mutators into our own code, then
   proceed with deprecation of the donors."*): `WildTattooinePlants` -> `RSW_WildTattooinePlants`,
   `WildGalacticPlants` -> `RSW_WildGalacticPlants` (3 of the donor's 5 plant kinds), both in
   `src/RimStarWars/SWBestiary/Defs/DonorPackPort/RSW_DonorPack_WildPlantMutators.xml`. `WildDantooinePlants`
   (4 tiles) has **no port** (no RSW_ dantuber plant): the owner decides at the repaint. The JSON's
   `new_mutator` now carries these names. They were never in the authoring CSV: add the JSON's tiles to the CSV
   under the ported name, or decide placement by looking; the owner chooses at the repaint.
3b. **Alpha Biomes mutators and landmarks** (this file never held them; they were stripped in the 2026-10-18
   donor-free copy) map to our ports in `design/RimMandrake/retired_mutators_port_map.json`, explained in
   `design/RimMandrake/retired_mutators_port_2026-10-19.md`. `src/RimMandrake/Utils/save_donor_rewrite.py
   --mutators-only` renames them (and the five above) in a save copy.
4. Then `jawa/world_commit`, save, and confirm with a grid decode (`tileMutatorDefsDeflate`) that the
   restored names are present.

⚠️ Tile ids are the save's planet geometry (`world/world_tiles_sub7b.csv`); lat/lon/biome in the JSON
come from `world/ASHKARR_WORLDMAP_tiles.csv`, a record exported 2026-09-12, not the live planet.

## How the strip was done (2026-10-15, FOUNDRY)

- Format, from the engine (`RimWorld.SurfaceLayer.SerializeMutators`): two parallel raw-DEFLATE +
  base64 arrays, `tileMutatorDefsDeflate` (ushort shortHash per entry) and
  `tileMutatorTilesDeflate` (int32 tile id per entry), sorted by tile. Stripping = deleting the
  same index from both; nothing else in the file changed (verified byte-identical outside the two
  elements, CRLF kept).
- shortHashes: all 162 distinct hashes resolved uniquely against all four DefDump captures; the five
  donor hashes equal `StableStringHash(defName) % 65535`.
- Checks: donor entries 1,429 → 0; controls `Caves` 1,568 and `AB_DerelictClusters` 171 unchanged;
  418,354 XML elements before and after, no tag-count difference; `<def>Human</def>` 75 → 75.
- Backup (byte-exact, sha256 `dadf2996…3b31`):
  `D:\Luke\dev\_rmscratch\save_backups\CANONICAL_ASHKARR_START_2026-09-12_donorfree.rws.bak-pre-mutator-strip-20261015`.
  New file sha256 `de54dd3e9f2e5e2b11daa97432dc0f1bb423d929f400dc1675bb96ec9aba3a51`.
- Not yet load-tested in game (the save must reload once before it is trusted; the L1 round does that).
