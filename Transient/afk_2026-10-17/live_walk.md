# Live review walk 2026-10-17 — BENCH live driver (progress)

Plan: `Transient/review_walk_2026-10-17/` (deploy_all.sh, walk_modlist.py, modset.md, STAGING.md, stage_extra.py).
Bridge: BENCH holds it for this walk.

## 1. Deploy + mod list
- 18:30Z game closed (idle; Player.log copied to `Transient/review_walk_2026-10-17/live/Player.prewalk.log`).
- `deploy_all.sh`: FlowWorks 34, composed biomes 104 (incl. all tree-burst flora members), UtinniPatches 3, SWBestiary 83, StarWarsPatches 3; Doctrine/Armoury/PawnFlavor in sync. Cuisine deployed by hand (2 files).
- HARNESS bug fixed in deploy_all.sh: its `grep -q RUNNING` matched `NOT RUNNING`, so it refused to write ModsConfig with the game down.
- walk_modlist.py: added `mandrake.rsw.cuisine` (taozin food + brine tank need it). Load 1 (21 mods) threw 332x `ResolveIcon -> RaceProperties.AnyPawnKind` NRE: StarWarsPatches' `RSW_Jawa_Spawn_*` kinds lose their parent `RimMandrake_ColonyPawnKind` (lives in StarWarsRaces, not on the walk list). No walk creature lives in StarWarsPatches, so it was DROPPED; load 2 = 20 mods. Backup of the owner's list: `Transient/review_walk_2026-10-17/ModsConfig.PRE_WALK_20261017T113110.xml`.

## 2. Load + Player.log harvest (first exception first)
Load 2 (20 mods, via Steam): bridge token at 85 s; log 312 lines (`Transient/review_walk_2026-10-17/live/Player.walk2.log`). No exception from our code.
- First errors: 7 `Could not find a type named` (BiomesPlus/VanillaBiomes/ReGrowth/AlphaBehaviours workers) - tier absence, not ours to fix.
- Patch no-ops: UtinniPatches xenotype gene Conditionals, RG_Plant_* statBases, Zakkeg sequence; SWBestiary `Silooth` bodyGraphic replace; Biomes `AA_AngelMoth` remove - all target mods off the walk list (tier).
- `PatchOperationFindMod(RimMandrake: Baroque Biomes) failed` in `UtinniPatches/Patches/RUT_VaporDrifter_AerofleetWiring.xml`: Biomes IS loaded, so an inner op missed - presumed tier (Aerofleet target absent), unproven.
- Texture misses on OUR plants: RUT_LungerFry (Echeveria), RM_Glasskelle + RM_Rimebeard (SnakePlant), RM_Pulsebead (PincushionPlant) point at donor-mod plant art not on the walk list - MOD-adjacent (donor art dependency), filed below.
- Config errors: RUT_Jawa_* weaponMoney < cheapest tagged weapon on this tier (tier: fewer weapons loaded).

## 3. Live rows (MOD / SITE / HARNESS)
| build | row | status | class | note |
|---|---|---|---|---|

## 4. Bugs fixed
(pending)

## 5. Keeper saves (RM_walk_20261017_<scene>)
(pending)

## 6. Left over
(pending)
