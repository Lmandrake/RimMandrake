# FEVER_WOOD_FIRST_SCRIPT_1 worker note (first north-star script for FeverWood)

Status: AUTHORED, READY TO RUN. Offline proofs: selftest 100% (healthy world 62/62 PASS; 44 deliberate breaks each
redden exactly the component named for them), `lint_calls.py` 0 problems over 67 literal calls, `cli.py run --mock
--mod FeverWood --mock-skip-site` runs to completion, `modcheck floor --all` shows FeverWood `ok`, 62 components,
nine toggles all covered; `modcheck lint` clean for the walk.

## What was delivered (all under the worktree, explicit paths)
- `src/RimMandrake/FeverWood/validation.py` : modcheck Suite, 18 chains, 62 components, 9 toggles.
- `src/RimMandrake/FeverWood/northstar_plan.py`, `northstar_site.py` : USE_SUITE=True, EXPECT_MODS=`mandrake.rm.biomes`
  (the mod ships COMPOSED, `Biomes.compose.json` wave 2; `mandrake.rm.feverwood` is never in ModsConfig).
- `src/RimMandrake/FeverWood/selftest_feverwood.py` : fake game that proves each check can fail.
- `design/validation_walks/RimMandrake/FeverWood.md` : 50 `## must be true` lines, 38 covered, 12 named UNCOVERED.
- Tier: `baroque_wave0` (the narrowest existing tier that loads the composed mod; same list as `weepingstones_solo`).
  No new tier was added, so `modset_builder.py` is untouched.

## Bars (components) and how each is made to fail
Defs and wiring (read from the mod's own XML at import, floors pinned):
| chain.component | break that reddens it (selftest case) |
|---|---|
| log_clean.player_log_names_no_feverwood_error | an error line naming `RM_LureStake` in Player.log (an unrelated mod's error stays green) |
| source_guards (2) | a `MayRequire` naming a folded standalone mod; a top-level `<Operation MayRequire>` (synthetic tree) |
| defs_resolve.* (15 groups + probe + by-name) | a def removed; a def shadowed by a donor packageId; `RM_LureStaked` renamed |
| biome_roster.* (6) | `generatesNaturally` true; zero density; commonality zeroed; a modExtension dropped |
| registrations.* (5) | genstep not on `Base_Player`; Orders designators missing; recipe off the machining table; no Harmony owner |
| settings.* (10) | a field drifted from its C# default; a toggle that ignores `set` |
| bough_soil / rottable_items_tick | fertility 0; Heavy affordance; tickerType Never |
Behaviour, each in a clean pad, with `_teardown` always running:
| chain.component | what proves it | break |
|---|---|---|
| tentacle_ladder.severe_damage_severs... | feeler takes hp*0.6+5, gone, `RM_SeveredTentacleFlesh` appears | never severs; no flesh |
| tentacle_ladder.mild_damage_retreats... | graze 30% of the severe amount, still there, gone after 180+120 ticks, no flesh | never retreats; retreat drops flesh |
| tentacle_porter.unmolested... | porter gone within max delay+600, one of the five loot defs on the pad | no loot |
| tentacle_porter.a_hit_porter... | 1 damage, gone at once, no loot after the max delay | survives; still deposits |
| tentacle_lash.lash_spares / lash_cuts | far arm alone first (the lash cuts the FIRST pawn in range), then a near pawn gains `Cut` | dead lash; infinite range |
| tank.* (4) | read fed; light hit shut; heavy hit (risk multiplier 0.01 forces chance to 1) breaches, one juvenile with `RM_CaptivityMemory`; toggle off keeps it shut | unbreakable; light breaks; no memory; ignores toggle |
| foul_pool.* (2) | stack of 15, one RM_FoulPool use leaves 10, message `clouds and stills` on / absent with toggle off | no consume; no message; message ignores toggle |
| sap_RM_Vaulm, sap_RM_Drommath (2 each) | hurt gains hediff; hediff removed then re-hit inside cooldown stays off; re-hit after 2600 ticks returns | no hediff; no cooldown; one-shot |
| lure_stake.* (4) | empty reads "No bait staked."; haul of a downed pawn gives `RM_LureStaked`; reads "Baited with"; destroying frees | no chain; wrong text; hediff left |
| flora_harvest.* | four plants grown, harvest queued, each of the four RM_ products appears | harvest yields nothing |
| lure_raid.* (2) | OFF arm 15000 ticks no swarm pawn; ON arm swarm pawn appears (MTB forced to floor) | raid ignores toggle; raid never |

## LIVE-RUN SHEET
Prerequisite: bridge HELD (`rimflow bridge who`), owner's pre-session ModsConfig gets copied by live_session.py itself.
One command from WSL, repo root as cwd (cold start, stops the game, writes the tier, composes, launches, runs):

    python3 src/RimMandrake/Utils/northstar_driver/live_session.py --mod FeverWood --tier baroque_wave0 --plan src/RimMandrake/FeverWood/northstar_plan.py --compose

Game already up on `baroque_wave0` with the composed mod current: skip the restart and run only the driver (python.exe):

    python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod FeverWood --plan src/RimMandrake/FeverWood/northstar_plan.py

- Launch wait: the `baroque_wave0` tier is the composed mod plus Alpha Biomes/FlowWorks/LuminousPigment closure, far fewer than 599 mods; the driver waits for `Bridge token:` itself (live_session step 4, budget 900 s).
- Site: a quicktest map at least 150x150 (`northstar_site.preflight` refuses otherwise), all five DLCs active, settings at shipped defaults (read from the C#, numeric compare), weather locked Clear, and the composed copy in the game folder identical to source (`composed_deploy_drift`; `--compose` applies it, game closed). No god mode needed (NEED_GOD False). The suite clears and rebuilds its own 29x29 pad 45 cells off the map centre per chain.
- Tick budget (ESTIMATE, not measured): about 30000 ticks typical and 55000 worst case, of which `lure_raid` is two 15000-tick windows. `rimworld/step_game_ticks` truncates to 600-2800 ticks per call, so expect several minutes of wall time; `lure_raid` is declared last so everything else lands first.
- Pass/fail meaning: PASS = the state read back matched. FAIL = a read that could ask came back wrong (file it against the mod unless it is the 0.7% false RED named below). UNMEASURED = the instrument could not ask (a shape the script assumes is not what the live tool returns): that is a HARNESS finding, not a mod finding.
- Known statistical edge: `lure_raid.a_staked_lure_draws_the_swarm` has about a 0.7% chance of a false RED (about 6 hourly rolls at about 0.56); rerun once before believing a lone RED there.
- Shapes UNPROVEN until the first live run (each yields UNMEASURED, never PASS, if wrong): `jawa/inspect_string` and `rimworld/list_messages` row shapes (read as flattened text), `jawa/get_defs` serialising `modExtensions`, `genSteps`, `fertility`, `affordances`, `jawa/harmony_patches` row keys, a stack-size key on `list_things` rows, `jawa/list_pawns includeHealth` hediff nesting (read as flattened text).
- A job the live game does not run would show as FAIL with "was not accepted and running"; the first run should record whether `ordered_job` accepts `RM_FoulPool` and `RM_HaulToStake` with `targetBId` for a Building.
- Harness trap avoided: `Suite.set_setting` reads back and compares to `str(value)`, so a Python `1.0` fails against the C# `"1"`. The script passes ints for integral floats. See follow-up `NORTHSTAR_SET_SETTING_NUMERIC_COMPARE_1`.

## What was NOT done (and why)
- No live game, bridge, ModsConfig or deploy access was used.
- No ledger item was filed (rimflow untouched); no `modcheck validate`; no edit of any owner `## north star` section (this walk's is `DRAFT`, blank hash).
- `modcheck doctor` reports `WALK_WITHOUT_CAPABILITY FeverWood` (a WARN shared by 7 other mods): the rimflow capability row is the seat's to file.

## FOLLOW-UP ITEMS
- `FEVERWOOD_LIVE_MAP_SITE_1`: a site or tool that gives the suite a REAL `RM_FeverWood` map (registered pool water via the scatter-pools genstep), so the six uncovered chains can run: ambient limbs and `tentacleBestiaryEnabled`, the Great Emergence, the snare grab, the sentinel chorus hush, the ant-hive genstep with `antHiveDungeonEnabled`/`antHiveChanceMultiplier`, `GetScore` with `naturalPlacementEnabled`.
- `FEVERWOOD_WATCH_STATE_TOOL_1`: a JawaBench `[Tool]` reading `RM_MapComponent_TentacleWatch` (blockedUntilTick, porterAngeredForever, sentinelCount, encounterPressure, permanentlyKilled) so the porter's anger and the suppression clock become Boolean checks instead of a UI message.
- `FEVERWOOD_FORCE_FAILED_TAME_TOOL_1`: a `[Tool]` that forces `Pawn_MindState.CheckStartMentalStateBecauseRecruitAttempted` to fail on a given animal, so `sapSuckerMishandleRefusalEnabled` and the ollareth alarm get an effect check.
- `NORTHSTAR_SET_SETTING_NUMERIC_COMPARE_1`: `modcheck.suite.Suite.set_setting` compares the read-back to `str(value)`; make it compare numerically for float and int fields (a Python `1.0` against a C# `"1"` raises ExpectationFailed).
- `BRIDGE_READ_SHAPES_MEASURE_1`: after the first live run, pin the real shapes of `jawa/inspect_string`, `rimworld/list_messages` and `jawa/harmony_patches` in `tool_schemas` result notes so the flattened-text reads can be tightened.
