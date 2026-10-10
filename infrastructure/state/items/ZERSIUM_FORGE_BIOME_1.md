# ZERSIUM_FORGE_BIOME_1 — zersium lives in the Forge

## spec
Parent: `SHIP_ALLOY_FORGE_1` (its spec point 3). Design: `design/RimMandrake/canon_materials_design_2026-10-09.md`
§2b, §3.2, §3.4, §6. Owner, question cards 2026-10-09: zersium is **a rare local ore in ONE home biome**, and that
biome is **The Forge**. Owner, typed 2026-10-09: *"I like the forge makes that mineral. We had also said asteroids.
It's ok if it's both or another minerals in space either way."* The asteroid side is left to
`ASTEROID_DESERT_ORES_1`; this item builds the Forge source only.

Built:
- `RSW_Zersium` (item, `ResourcesRaw`) and `RSW_MineableZersium` (ore rock, yields 20/cell), in
  `src/RimStarWars/Armoury/Defs/ThingDefs/RSW_Zersium.xml` (`mandrake.rsw.armoury`). Zersium is canon IP, so it is RSW
  tier and the RimMandrake Forge mod never names it (biome_mod_architecture.md §7 Q11).
- The ore has scatter and deep commonality 0 and `mineablePreventMeteorite`, so no vanilla scatter, deep drill,
  quarry weight or meteorite places it. The only placement is `RUT_ZersiumForgeLumps`
  (`src/RimUtinni/UtinniPatches/Defs/MapGeneration/`, C# `RUT_GenStep_ZersiumForgeLumps`): vanilla
  `GenStep_ScatterLumpsMineable` with `forcedDefToScatter`, registered on `Base_Player`, gated on
  `RM_TheForge` / `RUT_TheForge` and on Mod Settings **"Zersium ore in the Forge"** (`zersiumForgeEnabled`,
  default on, worldgen-affecting: new Forge maps only).
- **PROVISIONAL numbers** (no calibration, no ruling): 0.3–0.5 lumps per 10k cells (~2–3 lumps on 250×250),
  lump 8–14 cells, yield 20 per cell ⇒ ~660 per standard map. MarketValue 5, Mass 0.6. Registry row added to
  `design/RimMandrake/mineral_abundance_registry_2026-10-03.csv` (Forge columns 660 EPM).
- Art: none existed (`artpipe_state.py find zersium`, 0 hits; probe `mindstone` found). Job `RSW_Zersium` queued
  (install_to `src/RimStarWars/Armoury/Textures/Things/Item/Resource/RSW_Zersium.png`). Until it is installed
  through `art.py install`, the item draws vanilla Steel's stack sprites tinted grey-green; on install, switch
  `texPath` to `Things/Item/Resource/RSW_Zersium` with `Graphic_Single`. The ore uses the vanilla rock-fleck atlas
  recoloured (no art owed).
- Not here: the consumer recipe, steel + zersium → `RSW_Durasteel` on the alloy forge (`SHIP_ALLOY_FORGE_1`), and
  `RSW_Durasteel` itself (`CANON_MATERIALS_BUILD_1`).

## criteria
- L1 L0: `RSW_Zersium` and `RSW_MineableZersium` exist in the RSW tier; the ore yields `RSW_Zersium`, has scatter and deep commonality 0 (validation.py `zersium_forge.zersium_wiring_static`)
- L2 L0: `RUT_ZersiumForgeLumps` forces `RSW_MineableZersium` on exactly `RM_TheForge` + `RUT_TheForge`, is registered on `Base_Player`, and the assembly builds 0W/0E
- L3 L0: Mod Settings toggle `zersiumForgeEnabled` exists, defaults on, is Scribed, and is in `suite.toggles`
- L4 L1: on a full-list load the three defs load with no config or cross-reference errors (`zersium_forge.zersium_defs_loaded`)
- L5 L1: a newly generated Forge map carries zersium ore cells; any non-Forge map carries 0 (`zersium_forge.zersium_only_in_forge`); with the toggle off a new Forge map carries 0
- L6 L1: our zersium render is installed through the art ledger and the placeholder texPath replaced

## verify
Record with `rimflow verify ZERSIUM_FORGE_BIOME_1 --criterion <ID> --result pass|fail|partial --evidence <path>`.
L0 offline (done 2026-10-09: winbuild 0W/0E; static chain PASS and a break case caught). L1 needs a full-list
bridge session and a freshly generated Forge map (an old Forge map predates the GenStep and reads 0 cells).

## live read (2026-10-09, bridge7, full-565)
L4 PASS. L5 PARTIAL: the biome gate and the toggle read correctly, but the PROVISIONAL density places far less than
the "~2-3 lumps / ~660 zersium per map" estimate above: four fresh RM_TheForge player-home maps (250x250, LargeHills)
carried 24, 0, 0, 0 ore cells; a 150x150 flat one 0. Most Forge maps get none, so toggle-off cannot be told apart.
Likely CanScatterAt finding little natural rock on Forge maps at 0.3~0.5 per 10k cells. Retune (count or lump
placement), then re-read L5 on new home maps. Only player-home maps run the GenStep (Base_Player); a faction-less
`scenelib.biome_map` settlement generates with Base_Faction and always reads 0.
