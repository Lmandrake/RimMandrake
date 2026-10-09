# ASTEROID_DESERT_ORES_1 — doonium ore on asteroids, phrikite in the desert, both smelted aboard

## spec
Spec: `design/RimMandrake/canon_materials_design_2026-10-09.md` §3.5. Owner, typed 2026-10-09, on doonium:
*"Also asteroid ore"*; phrik by question card (owner typed *"Both"*: trade and a rare desert deposit); glower
crust as a doonium ingredient (owner: *"More lore than anything else but connects them"*). Canon homes:
`design/RimMandrake/canon_metal_fabrication_2026-10-09.md` §3–§4. Parent: CANON_MATERIALS_BUILD_1 (which
defines `RSW_Doonium` and `RSW_Phrik`).

1. **Doonium ore:** a mineable placed on Odyssey asteroid maps only, never the planet surface (patch the same
   two generation paths CANON_MATERIALS_BUILD_1's L4 allowlists). Smelt aboard: doonium ore + `RM_GlowerCrust`
   → `RSW_Doonium`. Traders buy glower crust as doonium feedstock.
2. **Phrikite:** a rare deep deposit in one desert biome, placed through
   `design/RimMandrake/mineral_abundance_registry_2026-10-03.csv` (candidates: `RM_Stillsand`, `RM_BlueDesert`,
   `RUT_ExtremeDesert`); smelted aboard into `RSW_Phrik`.
3. Both smelts run on the ship's smelter (`VFEFactory_AutomatedSmelter`, VFE ProcessDefs).
4. Amounts go in the registry, not in this item. Mod Settings toggle per ore.

## criteria
- L1 L0: doonium ore generates on asteroid maps and on no planet biome; it smelts with glower crust into `RSW_Doonium` aboard
- L2 L0: phrikite is placed in one desert biome per the registry; it smelts into `RSW_Phrik` aboard
- L3 L0: glower crust carries trade value as a doonium feedstock
- L4 L1: a minimal-list load shows both mineables and both smelts with no config errors

## verify
Record with `rimflow verify ASTEROID_DESERT_ORES_1 --criterion <ID> ...`.
