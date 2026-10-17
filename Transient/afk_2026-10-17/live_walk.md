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
| ExplosiveGrowth | probe_rules.ruled_rate_table_on_live_plants | PASS | - | twice (old + rebuilt proof DLL) |
| ExplosiveGrowth | probe_tree_burst_off.tree_burst_off_trees_die_of_age | PASS | - | |
| ExplosiveGrowth | probe_tree_life.trees_live_by_litres_and_burst_at_their_end | UNMEASURED | HARNESS | every arm in bar (jungle x4/x1 + end burst 10 logs 4 seedlings; AB_GiantStikehr dry x0.1 / wet x1, 400 L = 10 days, young gain 0.667, water burst 25 logs 4 seedlings; natural death falls, no burst) EXCEPT immortal=NONE: proof's FirstOf skipped interferesWithRoof, which Core TreeBase sets on every tree, so RM_Ollim never qualified. Fixed f6da84ad3c, deploys at next restart |
| ExplosiveGrowth | 74 other suite rows (all chains) | 67 PASS first run | - | |
| ExplosiveGrowth | vanilla_normal_ignores_water, master_off_refuses_soak | FAIL -> PASS | HARNESS | an arm that lifts the x0.1 dry penalty moves the control too (10 -> 100); now soaked vs control under the same arm (abae3c87e7) |
| ExplosiveGrowth | ground_tell_on/off, suppression_dries_and_defuses | FAIL -> PASS | HARNESS | the ruled rewrite arms from a full-map wave (1/8 of plants per 250-tick pass); a 700-tick wait missed it; now polls to 2,450 ticks |
| ExplosiveGrowth | churn_cycle, churn_off | FAIL -> PASS | HARNESS | the dry-native subject was AB_Slimecasia, a Slime-top row (churn off cannot stop its own top: live LastOutcome=OwnTop, ground -> RM_Slime_Rich); proof now picks a Churn-top plant (DLL rebuilt, restart 3) |
| ExplosiveGrowth | top_burst x2, burst_hurts_pawns x2 | UNMEASURED | SITE | donor RG_Plant_AridGrass not on the walk list |
| ExplosiveGrowth | scope_native_only.default_runs_only_in_baroque_biomes_biomes | UNMEASURED | SITE | UtinniPatches' campaign roster forces every biome in scope on this list (by design) |
| SWBestiary | defs_resolve x2 | PASS | - | |
| SWBestiary | taozin_brine_tank_infuses_and_whitens x2 | PASS | - | off moves nothing; on 2 jars, 1 brine, grub pale |
| SWBestiary | dragonsnake_pair.canon_dragonsnake_spawns | PASS | - | |
| SWBestiary | dragonsnake_pair.albino_roster_follows_toggle | UNMEASURED -> PASS | MOD | RSW_Dragonsnake was never on the Greentide roster: WildAnimals_Greentide.xml's FindMod named the packageId (FindMod matches the mod NAME); the whole 21-row RSW_ cast never applied, likewise its Alpha Animals / VFE Insectoids blocks and TheRot's Alpha Animals wound-sharing block. Fixed 98f9074bcd |

## 4. Bugs fixed
- MOD `98f9074bcd`: FindMod by packageId (Greentide RSW_ cast, Alpha Animals, VFE Insectoids, TheRot wound sharing). Lesson filed.
- HARNESS `abae3c87e7`, `f6da84ad3c`: ExplosiveGrowth suite + proof DLL (see rows).
- HARNESS `98f9074bcd`: northstar preflight deployed_matches_repo ignored src/DEPLOY_HOLD.txt and the deploy's folded-id MayRequire rewrite (100 false diffs on SWBestiary).
- HARNESS (commit 1): deploy_all.sh's game check matched `NOT RUNNING`.

## 5. Keeper saves (RM_walk_20261017_<scene>)
(pending)

## 6. Left over
(pending)
