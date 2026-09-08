# RAIN_BAN_SCOPE_DRIFTED_1 — the 2026-08-21 rain-ban ruling's scope no longer matches the world

Discovered 2026-09-07 (FOUNDRY, code-review sweep of `ashkarr_dry_jungle.py`).

## spec
- **The original ruling** (`RAIN_BAN_SCOPE_1`, 2026-08-21, `ashkarr_dry_jungle.py`'s own
  docstring): zero `rain_mm` on every tile below `hilliness` 4, no biome exempted.
  Measured that day: 363 tiles matched, and **every one of them was
  `AB_FeraliskInfestedJungle`** — the reasoning that made this costless was specific to
  that biome ("fed by rivers, not sky").
- **Measured today** (running `ashkarr_dry_jungle.py` report-only against the current,
  post-rebase `world/ASHKARR_WORLDMAP_tiles.csv`): 364 tiles now match the same selector,
  spanning **17 different biomes** — `Desert` (41), `BiomeCypreJungle` (43),
  `ExtremeDesert` (63), `ZBiome_DesertOasis` (11), `AB_FeraliskInfestedJungle` (36, down
  from 363), `AridShrubland` (16), `ZBiome_Badlands` (30), `AB_MycoticJungle` (3),
  `AB_PropaneLakes` (42), `PoisonForest` (1), `AB_RockyCrags` (36), `RUT_NightsideIce` (5),
  `ZBiome_Grasslands` (19), `AB_MechanoidIntrusion` (10), `BMT_FungalForest` (3),
  `Wasteland` (2), `AB_MiasmicMangrove` (1), `RUT_PropaneLake` (2).
- **Why**: `world/ASHKARR_WORLDMAP_tiles.csv.frozen.json` records a 2026-09-07 full
  savegame rebase (the CSV is now exported from the save, not hand-painted) that changed
  `hilliness` on 7,275 tiles and `biome` on 5,411 tiles — the world composition under the
  same selector has genuinely shifted since the ruling.
- 🔴 **`ashkarr_dry_jungle.py` now refuses to `--apply`** against this drifted selection
  (a new `--i-know-the-world-has-moved-on` flag is required) rather than silently drying
  rain across biomes the original "costs the fiction nothing" reasoning never considered
  (a Desert or a propane lake is not river-fed the way the jungle is).
- **This needs an owner call, not a guess**: does the rain ban still apply to the WIDER
  set (rule again, deliberately, that hilliness<4 has no rain regardless of biome — the
  original text of option (a)), or does the ban now need re-scoping to stay
  jungle-specific given the new biome mix? Either answer is legitimate; picking one here
  would be re-litigating a ruling that belongs to the owner.

## verify
The owner (or whoever escalates to them) decides the scope; `ashkarr_dry_jungle.py --apply
--i-know-the-world-has-moved-on` (if the wider scope stands) or a narrower selector fix
(if not) runs cleanly; a fresh report-only pass shows the selector converging to 0.
