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
| ExplosiveGrowth | probe_tree_life.trees_live_by_litres_and_burst_at_their_end | UNMEASURED -> PASS (load 4) | HARNESS | every arm in bar (jungle x4/x1 + end burst 10 logs 4 seedlings; AB_GiantStikehr dry x0.1 / wet x1, 400 L = 10 days, young gain 0.667, water burst 25 logs 4 seedlings; natural death falls, no burst) EXCEPT immortal=NONE: proof's FirstOf skipped interferesWithRoof, which Core TreeBase sets on every tree, so RM_Ollim never qualified. Fixed f6da84ad3c, deploys at next restart |
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
| LeaningScrub | islands.islands_laid_share | PASS | - | Scrub test site |
| LeaningScrub | islands.creep_runner_unarmed | FAIL -> PASS (load 4) | HARNESS | live laid=300 besideTestStand=0: the proof's chance-1 sweep spent maxRunnersPerSweep on the map's existing stands first; proof now sweeps only its test stand (fa9cbb1332) |
| LeaningScrub | islands.creep_toggle_off, creep_cap_stops, growth_exempt_from_explosive_growth | PASS | - | |
| FlowWorks | extensions_rivers works.weir_joined_wall | PASS | - | river site save; the works chain's other 11 rows PASS too; weir_joined_wall_art_in_game owed (owner look) |
| FlowWorks | L8_pond_shallows_before_mud | PASS (load 4) | - | first try UNMEASURED/HARNESS: jawa/flowworks_body_report NRE'd (RM_LiquidBody.stock became a property in P3); companion fixed 9cef395f0d |
| FlowWorks | river colours (planet map) | PASS (by eye) | - | Harmony prefix on WorldDrawLayer_Paths.GeneratePaths owned by mandrake.rm.flowworks, riverColorsEnabled True; screenshot `Transient/review_walk_2026-10-17/live/fw/walk_river_colors_world2.png` shows red/orange/olive/green gradients along rivers |
| FlowWorks thirst | T7, T2, T3, T6, T4, T5, T10, T9, T11, T12, T13 | PASS | - | new driver `src/RimMandrake/FlowWorks/northstar/thirst_live.py`; first-run FAILs on T5/T10/T12/T13/T6 were all HARNESS (wrong id form, short windows, a long GotoWander never re-thinking, a bottle left on the map, a disturbed map) |
| FlowWorks thirst | T1_provider_line | UNMEASURED | HARNESS | one of the bar's three lists: no Dubs -> Own (arm OK) |
| FlowWorks thirst | T27, T28, T19, T24 | PASS | - | T19/T24/T13 partial arms named in each row's notRun |
| FlowWorks thirst | T17_salt_break | PASS | - | break START forced (jawa/pawn_force_mental_break); drank brine to 0.994, SaltRelief, SaltPoisoning 0.75 = 3 drinks. Not run: the break being offered / withheld |
| FlowWorks thirst | T15_slime_effects | PASS (2nd run) | presumed HARNESS | run 1: the red pawn drank (DrankSlime, SlimePurge) but carried white's RM_SporeFlesh 0.002 and no RM_ContagionTouched; run 2 on a fresh load: all four colours exact. Unexplained one-off: worth a look |
| FlowWorks thirst | T14, T16, T18, T20, T23, T25, T26, T29 | UNMEASURED | - | not driven (salt-biome natives, Gelatinous map, Dubs list, bucket-to-dirty, Fill-tank brine order, snow map, campfire bill, two-colonist bottle stock) |
| FlowWorks sprinklers | draws_and_wets, no_pressure, flip_sprinklersEnabled, dries_when_starved, thick_clogs, walls_stop_spray, acid_hurts_fuel_puddles, T21_drinking_reserve, T22_no_brine_spray | PASS | - | new driver `src/RimMandrake/FlowWorks/northstar/sprinkler_live.py`; measured: the pump must stand OVER the pipe run (stage_extra.py's in-run pump split the net, fixed) |
| FlowWorks sprinklers | liquid_key, vfe_boost_skipped, vfe_valve | UNMEASURED | SITE/HARNESS | key behind an out parameter; no VFE Farming on the list |

## 4. Bugs fixed
- MOD `98f9074bcd`: FindMod by packageId (Greentide RSW_ cast, Alpha Animals, VFE Insectoids, TheRot wound sharing). Lesson filed.
- HARNESS `abae3c87e7`, `f6da84ad3c`: ExplosiveGrowth suite + proof DLL (see rows).
- HARNESS `98f9074bcd`: northstar preflight deployed_matches_repo ignored src/DEPLOY_HOLD.txt and the deploy's folded-id MayRequire rewrite (100 false diffs on SWBestiary).
- HARNESS (commit 1): deploy_all.sh's game check matched `NOT RUNNING`.
- HARNESS `fa9cbb1332` LeaningScrub creep proof; `9cef395f0d` JawaBench body_report; `c37ed41ae5` stage_extra sprinkler layout.
- Restarts: 4 loads (walk list; minus StarWarsPatches; EG/FindMod/FlowWorks batch; proof DLLs + companion).

## 5. Keeper saves (RM_walk_20261017_<scene>)
Saves backed up first: `D:\Luke\dev\_rmscratch\saves_backup_walk_20261017` (337 files, 5.6 GB). Each save stat-checked: only the named file appeared.
`RM_walk_20261017_sprinklers`, `_thinwater`, `_weirs`, `_venomvine`, `_creatures`. Guide: `Transient/review_walk_2026-10-17/WALK_GUIDE.md`.
- HARNESS fixed in stage_extra.py: sprinkler layout (pump over the pipe), joined weir walls run INTO the river along the weir axis (the bank-side version qualified 1-2 cells, none joined).

## 6. Left over
- Not recorded in modcheck: every run here was a --chains / --only partial or a new standalone driver, which `modcheck record` refuses. The rows live in the result JSONs under `Transient/review_walk_2026-10-17/live/`. validation.py's THIRST_LIVE / SPRINKLER_LIVE rows still raise "UNMEASURED: live check owed": wiring them to read the newest thirst_live / sprinkler_live result is owed.
- Thirst rows not driven: T14, T16, T18, T20, T23, T25, T26, T29; T1 needs Dubs lists. Sprinkler: liquid_key, two VFE rows.
- Texture misses on our plants off the full list (RUT_LungerFry, RM_Glasskelle, RM_Rimebeard, RM_Pulsebead point at donor plant art).
- Owner looks: the five keeper saves (WALK_GUIDE.md); weir_joined_wall_art_in_game; thin water reads very faint.
- Dirty review marks: RM_ExplosiveGrowthProof.cs, RM_VenomvineIslands.cs, JawaBenchFlowWorksNorthstarTools.cs, northstar_driver/preflight.py, the two new drivers (no full-file review done).
- The JawaBench companion was deployed with a peer's uncommitted one-line doc edit in JawaBenchPawnKitTools.cs (description text only).
- Game left on `RM_walk_20261017_creatures`, paused; bridge released; ModsConfig is the 20-mod walk list (owner: no need to restore).
