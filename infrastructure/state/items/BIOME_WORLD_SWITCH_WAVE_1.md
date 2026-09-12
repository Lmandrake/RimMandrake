# BIOME_WORLD_SWITCH_WAVE_1 — repaint the planet onto the owned BiomeDefs

Owner, 2026-09-12, at the bench reading the world map at tile 17007: *"We have
tickets out to make ALL biomes on the Worldmap our own, right? This one still says
GRINDTerra Deep Desert."* Answer: no — `BIOME_OWNERSHIP_WAVE_1` closed at `cc11aee6e`
on **def authoring only** ("world-tile switch is a separate, later bridge" item, per its
own commit message) and that later item was never filed. Its verify line ("zero defs
from the donor list remain painted") was therefore never met.

## MEASURED 2026-09-12 (live `jawa/world_tile_export`, 21,872 tiles)
- **Ours: 3,983 tiles / 6 defs. Donor or vanilla: 17,889 tiles / 23 defs (82%).**
- ExtremeDesert 3969 · AB_PropaneLakes 2531 · Desert 2390 · AB_MycoticJungle 2204 ·
  Wasteland 1853 · AB_RockyCrags 1135 · ZBiome_Badlands 970 · AridShrubland 628 ·
  PoisonForest 546 · AB_MechanoidIntrusion 236 · BiomeCypreJungle 235 ·
  ZBiome_DesertOasis 223 · ZBiome_Grasslands 222 · AB_OcularForest 179 ·
  AB_FeraliskInfestedJungle 161 · AB_GelatinousSuperorganism 96 · AB_MiasmicMangrove 93 ·
  Scarlands 90 · COMIGO_GreaterSwamp_Tropical 43 · AB_TarPits 41 ·
  AB_PyroclasticConflagration 31 · LavaField 8 · Volcano 5.
- Why the owner sees "GRINDTerra": vanilla `ExtremeDesert`/`Desert`/`AridShrubland` are
  RE-DECLARED by `grimterra.terrainretexturemod` (live `get_defs` reports that mod as the
  def's source), so the tile card credits GRiNDTerra even though our campaign label
  ("the Deep Desert") is applied. Owning the tile with `RUT_ExtremeDesert` is the only
  fix; relabelling cannot change the source mod.

## spec
- Template: `PYRELANDS_WORLD_SWITCH_1` (batches, getter read-back, CSV re-export + LOSS
  diff, R36 backup bar). Map donor def → owned def from `BIOME_OWNERSHIP_WAVE_1`'s
  commit (`RUT_Desert`, `RUT_ExtremeDesert`, `RUT_AridShrubland`, `RUT_Wasteland`,
  `RUT_PoisonForest`, `RUT_Scarlands`, `RUT_Contagion`, `RUT_Webwork`, `RUT_Slime`,
  `RUT_TheRot`, `RUT_TheForge` (LavaField/Volcano/AB_PyroclasticConflagration),
  `RUT_RustCathedral`, `RUT_Umbra`, `RUT_CrackedLands`, `RUT_ForsakenCrags`,
  `RUT_FeverWood`, `RUT_Greentide`, `RUT_Miasma`, `RUT_Sump`, `RUT_WeepingStones`;
  `ZBiome_Grasslands` → `RM_FE_Pyrelands` rides `PYRELANDS_WORLD_SWITCH_1`;
  `BiomeGRimond` is already switched).
- Order: biome before links (a repaint over a river hides it — re-read
  `rimbridge/references/world-authoring.md`); one `world_commit` at the end; deliberate
  CANONICAL re-save with the Saves backup + stat-after discipline.
- Regenerate the de-dup union and the animal-side `wildBiomes` strip against the new
  defNames as each batch lands; `WORLDMAP_BIOME_ICONS_REGEN_1` afterwards.

## verify
- Fresh live tile export: **zero** of the 23 donor/vanilla defs above remain painted;
  every painted def is `RUT_`/`RM_`-tier. Say the count.
- Tile 17007's card reads an owned def (no donor mod credited) — the owner looks.
- Full-list load, zero new Config errors; one quicktest map per switched batch.

## traps
- The frozen world CSV (`world/ASHKARR_WORLDMAP_tiles.csv` + `.frozen.json` stamp) must
  be re-exported and re-stamped in the same change, or the next fingerprint check fails.
- `world_tile_set` on a river/road tile: check `allowRivers`/`allowRoads` on the OWNED
  def first — a def that forbids them silently drops the link.
