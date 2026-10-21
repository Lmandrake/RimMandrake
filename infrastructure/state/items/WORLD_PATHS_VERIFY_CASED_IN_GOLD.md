# WORLD_PATHS_VERIFY_CASED_IN_GOLD

Built offline in `fe729e485`: `src/RimMandrake/BiomesShell/Source/RM_WorldPaths.cs` (Baroque Biomes shell DLL). Design and
values: `design/Jawa/worldbuilding/world_paths_readable_2026-10-20.md`. NOT deployed.

`WORLD_PATHS_VERIFY_CASED_IN_GOLD` — built, undeployed; NEXT: deploy Baroque Biomes (`deploy_custom_mods.py --compose biomes`, then `--apply`), load `ASHKARR_DEV_START_2026-10-20_RECORDLINKS.rws`, and confirm three things. (1) Player.log has `readable world paths ON (startup): 5 road layer colours, 12 road widths, 4 river widths, river material swap on`. (2) The world map at the worldlook3 desert-roads and coast-close framings shows the dark casing, umber dirt, slate stone, the gold highway, and rivers with dark banks. (3) Toggling the setting off redraws the vanilla look.

Things a passing check could still miss:
- **Harmony order.** `GeneratePathsPrefix` runs at `Priority.Last`, so it sees FlowWorks' River Colours (`RM_RiverColors.cs`,
  same method). If FlowWorks' prefix runs after it anyway, the banks take the gradient colour, not the dark shade. To
  check, the bank should be visibly darker than the water.
- **The swapped river material.** Rivers use a copy of `WorldMaterials.Roads` at queues 3520/3530. The offline model
  assumes the Roads shader draws hard-edged and unlit-alike, as it does for roads. Specular and the `_Alpha` falloff are
  gone on purpose.
- **The night side** is not modelled. Check one frame of the terminator.
- **FlowWorks River Colours' biome anchors are stale.** `AB_OcularForest`, `AB_FeraliskInfestedJungle` and `Wasteland`
  match no dev-world river tile, so the gradient runs on elevation only. Re-pointing them (perhaps RM_Contagion /
  RM_Greentide / RM_Wasteland) is a FlowWorks mapping question. Its middle and terminus colours stay within ΔE 9.5-19 of
  the faces, so only the bank carries those stretches. Darker anchors are an owner palette decision (design note §3).
- **The highway reads as dashes because the record has it in 46 pieces.** Fixing that means routing the record, not
  styling it.
