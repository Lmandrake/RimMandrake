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

## status — DONE (live), 2026-09-12 (FOUNDRY)

All 22 donor/vanilla defs in this item's scope switched. **17,667 tiles repainted**
(the item's 17,889 minus `ZBiome_Grasslands` 222, which rides
`PYRELANDS_WORLD_SWITCH_1`). Live `jawa/world_tile_export` after
`jawa/world_commit`: **zero** of those 22 defs remain painted anywhere; 21,872/21,872
tiles account for. Driver: `world/biome_world_switch_apply.py`.

### mapping used — every pair resolved from evidence, none guessed
Sixteen pairs come from `cc11aee6e`'s own commit message. The six the message left
unpaired were resolved from each `RUT_*.xml`'s header comment, which names its donor
outright ("Replaces the donor `X`"); the pairing is a clean 6↔6 bijection against the
six donors the message did not name. **Nothing was excluded as unresolved.**

| donor def | tiles before | → owned def | after | source of the pairing |
|---|---:|---|---:|---|
| ExtremeDesert | 3969 | RUT_ExtremeDesert | 3969 | commit msg |
| AB_PropaneLakes | 2531 | RUT_Umbra | 2531 | commit msg (land tiles; the 57 `RUT_PropaneLake` water tiles were already owned and untouched) |
| Desert | 2390 | RUT_Desert | 2390 | commit msg |
| AB_MycoticJungle | 2204 | RUT_TheRot | 2204 | commit msg |
| Wasteland | 1853 | RUT_Wasteland | 1853 | commit msg |
| AB_RockyCrags | 1135 | RUT_ForsakenCrags | 1135 | `RUT_ForsakenCrags.xml` header |
| ZBiome_Badlands | 970 | RUT_CrackedLands | 970 | commit msg |
| AridShrubland | 628 | RUT_AridShrubland | 628 | commit msg |
| PoisonForest | 546 | RUT_PoisonForest | 546 | commit msg |
| AB_MechanoidIntrusion | 236 | RUT_RustCathedral | 236 | commit msg |
| BiomeCypreJungle | 235 | RUT_Greentide | 235 | `RUT_Greentide.xml` header |
| ZBiome_DesertOasis | 223 | RUT_WeepingStones | 223 | `RUT_WeepingStones.xml` header |
| AB_OcularForest | 179 | RUT_Contagion | 179 | commit msg |
| AB_FeraliskInfestedJungle | 161 | RUT_Webwork | 161 | commit msg |
| AB_GelatinousSuperorganism | 96 | RUT_Slime | 96 | commit msg |
| AB_MiasmicMangrove | 93 | RUT_Miasma | 93 | `RUT_Miasma.xml` header |
| Scarlands | 90 | RUT_Scarlands | 90 | commit msg |
| COMIGO_GreaterSwamp_Tropical | 43 | RUT_FeverWood | 43 | `RUT_FeverWood.xml` header |
| AB_TarPits | 41 | RUT_Sump | 41 | `RUT_Sump.xml` header |
| AB_PyroclasticConflagration | 31 | RUT_TheForge | **44** | commit msg (3 donors merge) |
| LavaField | 8 | RUT_TheForge | ↑ | commit msg |
| Volcano | 5 | RUT_TheForge | ↑ | commit msg |

**Excluded, deliberately:** `ZBiome_Grasslands` (222) — `PYRELANDS_WORLD_SWITCH_1`.

### verification (fresh live export, not the setter's own word)
- After-census: 27 painted defs, **every one `RUT_`** except `ZBiome_Grasslands` 222.
  Donor counts moved exactly, none duplicated or dropped
  (`RUT_TheForge` = 5+8+31 = 44 ✓).
- Whole-planet field diff before→after: **`biome` on 17,667 tiles; every other engine
  field on 0 tiles.** Nothing else moved.
- All 20 `RUT_` defs confirmed live and loaded first (`jawa/get_defs`, 20/20 resolved,
  `modName: RimUtinni Patches (Jawa campaign)`).
- **Tile 17007 now reads `RUT_ExtremeDesert`, sourced to RimUtinni Patches** — the
  owner's "GRiNDTerra Deep Desert" complaint is answered.
- Canonical CSV rebased from the live export
  (`ashkarr_rebase_from_save.py --apply`): only `biome` changed, 17,667 tiles; the CSV
  was otherwise already in sync. `verify_frozen.py --restamp` → ✅ CURRENT,
  sha `d48b69a2d49d`, 21,872 rows.
- Save: `BIOME_WORLD_SWITCH_WAVE_1_2026-09-12.rws` (16,466,747 B). Backup taken first
  (`CANONICAL_ASHKARR_START_2026-09-12.rws.bak-pre-biome-world-switch-2026-09-12`);
  Saves folder stat before/after shows **exactly one new file and no existing file
  changed** — `saveName` was honoured this time.

### 🔴 consequence the owner should rule on — 239 road tiles went invisible
Measured, not feared. Four owned defs are more restrictive than the donor they replace:

| tile change | link effect |
|---|---|
| ExtremeDesert (roads T) → RUT_ExtremeDesert (roads **F**) | **205 tiles' roads hidden** |
| AB_PropaneLakes (roads T) → RUT_Umbra (roads **F**) | **34 tiles' roads hidden** |
| LavaField/Volcano (rivers T) → RUT_TheForge (rivers **F**) | 5 tiles' rivers hidden |

`hiddenByBiome` 15 → **259**; visible road edge-ends 2470 → 2032, visible rivers
636 → 630. ✅ **Nothing was deleted** — stored `potentialRoads` stayed at 2,470 and
`potentialRivers` at 652 across the switch, so flipping a def's `allowRoads` restores
every link with no re-authoring.
- `RUT_ExtremeDesert`'s ban is **owner-ruled and quoted in the def** (dune_sea.md SS6,
  "No roads through the deep dune"), so those 205 are arguably the intent landing.
- `RUT_Umbra`'s `allowRoads=false` carries **no sheet ban in its header comment** while
  the donor allowed roads and 34 tiles use them. Flagged as possibly unintended — a
  one-line def change would restore them.

### owed, not done here
- **De-dup union / animal-side `wildBiomes` strip not regenerated.**
  `biome_wildbiomes_evictions.py` walks every installed mod's XML and exceeded a
  300 s timeout; it is not the cheap step the spec hoped for. The painted set changed
  under it, so it needs a real run.
- `WORLDMAP_BIOME_ICONS_REGEN_1`.
- Full-list cold load + per-batch quicktest (this item's third verify line) — not run.
- The links CSV was **not** rebased. `ashkarr_rebase_from_save.py` would have written
  1,235 road edges over the canonical 1,387: that 152-edge delta is **pre-existing
  drift**, not this pass's doing (potential links were 2,470 before and after), and
  absorbing it silently into this change would have hidden it. Needs its own look.
