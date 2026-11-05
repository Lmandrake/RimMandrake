## spec
Minerals R5: one adapter per mineable source that the policy's scatter/deep weights do not reach. Design:
`design/RimMandrake/mineral_abundance_registry_design_2026-10-03.md` (C5, R5). Already built: the meteorite whitelist
(`src/RimMandrake/Minerals/Source/RM_MineralMeteorite.cs`) and the explicit-list pruner
(`src/RimMandrake/Minerals/Source/RM_MineralExplicitLists.cs`). MineralsFramework is retired, so its adapter is moot.

## scope (from the census, MINERAL_SCATTERERS_AUDIT_OUTSIDE_ROCKS, 2026-11-05)
Census of every mineable scatterer outside GenStep_RocksFromGrid: `design/RimMandrake/mineral_scatterers_census_2026-11-05.tsv`
(one row each, with its cover; method and evidence in `design/RimMandrake/mineral_scatterers_census_2026-11-05.md`).
`src/RimMandrake/Minerals/selftest_mineral_scatterer_census.py` fails if a row is added there and not named here.

Still OWED by this item (cover `r5_owed`):
- `odyssey_mineral_rich`: TileMutatorWorker_MineralRich. Drop governed defs that are not local to the map's biome from its
  private `cachedMineables` (reflection), or substitute the biome's own pool, so a zeroed weight never reaches its
  `<2` lump fallback; keep the label in step with the def it places.
- `vee_meteorite_shower`: VEE `StaticCollections.nonSmoothedMineables` (ThingSetMaker_MeteoriteShower). Apply the same
  meteoritic whitelist as RM_MineralMeteorite, by reflection, refreshed with it.
- `vexp_mineral_devoid`: Vanilla Exploration Expanded TileMutatorWorker_MineralDevoid. It force-scatters every other
  isResourceRock mineable; skip governed defs the map's biome does not allow.
- `vge_asteroid_boon`: VGE LaunchBoonWorker_AsteroidDiscovery picks `preciousResource` from every isResourceRock def in
  code. Re-pick (postfix) from the pruned asteroid list when it landed on a disabled ore.

Covered elsewhere (no work here; named so the census stays whole):
- explicit-list pruner: `core_precious_lump`, `core_longrange_scanner`, `odyssey_asteroid_genstep`,
  `odyssey_generated_locations`, `odyssey_quest_asteroid`.
- meteorite whitelist: `core_meteorite`.
- surface placer inside RocksFromGrid: `biomescore_scatterat_repick`.
- own item: `rm_deepdrill_mineral_devoid` is MINERAL_DEVOID_FIX_ZEROED_VEINS_SLIP_THROUGH.
- nothing owed: `core_glaciers`, `core_obsidian_deposits`, `core_tutorial_mine_steel`, `rm_deepdrill_spacer_deposits`,
  `rut_forced_lumps`, `kcsg_post_generate_ore` (latent), `biomescore_island_cavern_rocks` (latent), `rm_mineshaft_bill_order`,
  `readers_not_scatterers`, `off_list_mods`.
- VOE mining outpost (`vanillaexpanded.outposts` is on the full list) yields ore off-map (C7); it is not a map scatterer,
  so the census does not list it, but its adapter stays in this item's original scope.
