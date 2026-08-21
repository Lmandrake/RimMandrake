## spec
Two facts about the LIVE mod stack are load-bearing for any DLL that stamps
`world/ASHKARR_WORLDMAP_tiles.csv` into a world, and neither is written down
anywhere else. Both measured 2026-08-19 off the installed mods.

1. 🔴 **THE TILE IDs ARE NOT VANILLA.** `My Little Planet` (`1117406550`,
   ACTIVE) Harmony-patches `Page_CreateWorldParams.DoWindowContents` to write
   `subdivisions` on `PlanetLayerSettingsDef`, and the Alien Worlds
   `TidallyLocked` preset on disk sets `<myLittlePlanetSubcount>7</...>` with
   `planetCoverage 1`. That is what produces 21,872 tiles — matching the CSV
   exactly. ⇒ **If MLP is deactivated, reordered out of effect, or the
   subcount is anything but 7, EVERY tile ID in the CSV shifts and the import
   silently paints the wrong planet.** The importer must ASSERT
   `grid.TilesCount == 21872` and refuse, loudly, otherwise.
2. **Other mods write this same grid — worth knowing, no longer worth
   ordering against.** Geological Landforms (`2773943594`, ACTIVE, packageId
   `m00nl1ght.GeologicalLandforms`) Harmony-patches vanilla's
   `WorldGenStep_Terrain` in `1.6/Lunar/Components/GeologicalLandforms.dll`,
   and four mods register their own WorldGenStepDefs — BiomesKit Continued
   (`3333951497`, `zal.biomeskit`, ACTIVE), Vanilla Expanded Framework
   (`2023507013`, `KCSG.WorldGenStep_SpawnWorldObjects`), Fortified Features
   Framework (`3498575851`), GravTide (`3779600989`). **All of them are things
   that ran BEFORE we arrive**, which is what we overwrite.
   🔑 **The bridge import is last by construction.** It runs against a world
   the game has already finished generating and before any map exists, so
   every step above has had its turn and there is nothing to sort ours against.
   ~~ORDER RULING: give our own `WorldGenStepDef` order 20 — above Geological
   Landforms at 0, below the 700s.~~ ⛔ DEAD — owner ruled 2026-08-19, all in-game worldgen hooks stripped; the route is the live bridge, see `ASHKARR_WORLD_DEFINITION.md` §12.
   We register no step, so there is no order.
~~3. `JawaSeaShaper` is installed and active; copy its WorldGenStepDef +
   `PatchOperationConditional` registration pattern.~~ ⛔ DEAD — owner ruled 2026-08-19, all in-game worldgen hooks stripped; the route is the live bridge, see `ASHKARR_WORLD_DEFINITION.md` §12. The mod is
   deleted from the repo, from the game's Mods folder and from `ModsConfig.xml`
   (584 → 583). There is no registration pattern to copy — the route is the two
   companion `[Tool]` methods that write the 21,872 tiles into a generated world.

## verify
offline, before any load: `grep -c . world/ASHKARR_WORLDMAP_tiles.csv` is
21873 (header + 21872), and the `myLittlePlanetSubcount` in the preset is 7.

## criteria
on the load that first runs the import, the companion tools return success
against a world whose `grid.TilesCount` is 21872, and a spot-check of five tile
IDs drawn from the CSV has the biome the CSV says. 🔑 Then LOOK at the world map and
compare it against `world/view/ASHKARR_WORLDMAP.biome.equirect.png`. Every
defect that has mattered in this work passed its numeric check while the
picture was obviously wrong.

## notes
**Imported from `queue/CHECK_CLOSED.md`. Its `state:` read, verbatim:**

⛔ FOLDED IN 2026-08-19. It was never a task - it is a PRECONDITION, and it
would have sat "ready" forever having no action of its own. Both assertions
(TilesCount == 21872; MLP active at subcount 7 / coverage 1) are now written
into W9 as refuse-loudly gates, and MLP is item 13 of the minimal mod list in
W1 for exactly this reason. Offline half re-verified 2026-08-19: the CSV is
21,873 lines, and the repo copy of the preset reads subcount 7, coverage 1.
