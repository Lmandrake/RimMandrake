# WARSCAR_REWIRE_SCARLANDS_KIT_TWIN_GONE

Found while deleting the 25 frozen twin BiomeDefs (`BIOME_TWINS_RETIRE_TWENTY_FIVE_FROZEN`).

## What is unwired

The deleted Scarlands twin's own BiomeDef carried wiring that `RM_Warscar` never had. No live biome runs this today, and none ran it before the deletion either, because the world paints `RM_Warscar`.

- `extraGenSteps`: `RUT_ScarlandsSprungDangers`, `RUT_ScarlandsGraveWardScatter`
- `biomeMapConditions`: `RUT_ScarlandsMarkLock`, `RUT_ScariaOnsetArming`

Decide whether `RM_Warscar` should run them, through a patch in `src/RimUtinni/UtinniPatches`. They were not moved during the deletion because arming scaria and a permanent map condition are gameplay changes on a painted biome.

## Moved during the deletion, unproven in game

- Pilgrim camps and the Scarlands ladder now target `RM_Warscar`.
- `RUT_ContagionRingScatter`, the Foundry floor and the tower scatter now target `RM_TheForge`.
- The Sarlacc seeker's `rootingBiomes` and the mutator whitelists in `RUT_RetiredMutatorPorts_Biomes.xml` swapped to the RM_ partners.

## Orphans left behind

Defs and art no biome uses any more; delete them after the ruling above.

- `RUT_ForgePulse`, `RUT_ScaldSteamLock`
- `RUT_WastesBrine*` terrain, deposits and scatters; `RUT_TwilightFish_*`
- `src/RimUtinni/UtinniPatches/Textures/World/Biomes/RUT_*` world faces for the deleted twins
