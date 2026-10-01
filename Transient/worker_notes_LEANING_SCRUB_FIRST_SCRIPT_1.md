# Worker note: LEANING_SCRUB_FIRST_SCRIPT_1 (LeaningScrub first north-star script)

Status: AUTHORED, offline-proven, READY TO RUN (needs the bridge). Not run live.

## Files
- `src/RimMandrake/LeaningScrub/validation.py`: modcheck Suite, 43 components in 12 chains, 15 toggles in `suite.toggles`.
- `src/RimMandrake/LeaningScrub/northstar_plan.py` (USE_SUITE, EXPECT_MODS = `mandrake.rm.biomes`) and `northstar_site.py` (preflight).
- `design/validation_walks/RimMandrake/LeaningScrub.md`: 48 `## must be true` lines (38 -> component, 10 -> UNCOVERED with reason). State: no north-star section at all (owner layer untouched, no `modcheck validate`).
- `src/RimMandrake/LeaningScrub/selftest_leaningscrub.py`: fake game, healthy run 43/43 PASS and 32 single-defect runs each turning exactly the named component red (this is the "every check can fail" proof, per bar, in the table below).

## Tier
`baroque_wave0` (13 mods: Core + 5 DLC + Harmony + RimBridge + VEF core + Alpha Biomes + FlowWorks + LuminousPigment + the composed Baroque Biomes). LeaningScrub ships INSIDE `mandrake.rm.biomes` (Biomes.compose.json, key LeaningScrub), so the dev folder's own packageId is never loaded; that is why EXPECT_MODS is `mandrake.rm.biomes` (same as Pyrelands). No new tier added. The older `leaningscrub` tier (21 mods incl. SWBestiary/Utinni patches/mlie) is for the Utinni roster layer and is not needed here.

## Live-run sheet (Windows-side seat, holds the bridge)
1. `python3 src/RimMandrake/Utils/modset_builder.py --tier baroque_wave0 --apply` (kill the game first; refuses while Player.log is <3 min old).
2. Launch via Steam. Wait for `Bridge token:` in Player.log (cold load ~15 min on this 13-mod list is far less: minutes). Start a quicktest map (`rimworld/start_debug_game_ready`; the map must be >= 150 cells on both axes: preflight checks it; pads sit +-45 cells from the centre). God mode not needed (NEED_GOD False). All 5 DLC active (preflight reads dlc_status).
3. `rimflow bridge take --for "LeaningScrub first script"` then
   `python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod LeaningScrub --plan src/RimMandrake/LeaningScrub/northstar_plan.py`
   Results JSON: `Transient/northstar/LeaningScrub_<utc>.json`; per-component progress lines `[lscrub] ...` stream to stderr.
4. Budget: ~38,000 game ticks in total (stall 4.5k, gale 10.5k, lash 1k, smother ~13.5k, dripping 1.2k, crown 3k, bloom 1k, sweetline 2.1k + a 5.5-day clock jump, refuel 0.9k). Waits of 4000 ticks or less run via step_game_ticks (~53 ticks/s measured), longer ones at Ultrafast with a real-clock stall guard. Expect roughly 15-25 minutes.
5. Site prerequisites: none beyond the map. The suite builds its own pads (soil), colonists, plants, animals, a campfire, a wind turbine and a roofed room; clears each pad on exit; locks vanilla `Clear` between chains. The sweetline chain runs LAST because it jumps the clock forward 5.5 days (`jawa/time_set_ticks`); do not reorder it.
6. Every Mod Settings field a chain flips is restored in a `finally` and re-read; if a run dies, run the preflight again (it fails on any setting off its shipped default).

## What each result means (PASS / FAIL / UNMEASURED)
UNMEASURED always means the instrument or fixture could not ask (never counts as PASS); FAIL means the question was asked and the answer was wrong. Classify each non-pass HARNESS / SITE / MOD per debug_process section 3.

| component | PASS means | FAIL means (likely class) | proven red offline by |
|---|---|---|---|
| defs.defs_resolve | all 54 parsed shipped defs resolve, absent-probe works | a shipped def was discarded (MOD) | missing_def |
| defs.biome_weather_table | table has the 4 owned weathers, no stock calm/rain | wiring regression (MOD) | no_weather_entry |
| defs.biome_density_and_flora | animalDensity > 0, flora rows present | roster dead / row lost (MOD) | (field-shape guarded; UNMEASURED if unreadable) |
| defs.biome_lean_extension | `modExtensions` lists RM_LeanExtension | extension lost (MOD) | no_lean_ext |
| patches.rules_armed | all 5 Harmony rules listed, owner mandrake.rm.leaningscrub | an engine signature moved, rule NOT armed (MOD) | rule_unarmed |
| patches.thicket_smotherable | thicket `comps` carries the smotherable comp | patch matched nothing (MOD) | thicket_unpatched |
| patches.dead_venomvine_fuels_fire | a colonist burned >= 1 dead venomvine in a campfire | fuel patch not applied (MOD) | fuel_unpatched |
| settings.defaults | 25 fields at shipped defaults, bogus field fails | renamed/missing/changed field (MOD or saved config) | setting_missing |
| settings.*_roundtrip (5) | field exists, default, writable | missing field (MOD) | (setting_missing path) |
| fauna.fauna_spawns | 13 kinds each spawn a live wild pawn | raceless/broken kind (MOD) | (spawn path) |
| fauna.dustflutter_can_fly | `pawn_flight report` canEverFly true | MaxFlightTime 0 (MOD) | no_fly |
| flora.flora_spawns | 12 plants stand after set_plants | a plant def cannot stand (MOD or SITE terrain) | set_plants_drops |
| stall.stall_freezes_small | 0.4-body animal static in the Stall while a 0.7 one moves | freeze not working (MOD); control static = UNMEASURED | no_freeze |
| stall.stall_toggle_off_wanders | toggle off releases it | toggle gates nothing (MOD) | freeze_ignores_toggle |
| stall.stall_master_off_wanders | master off releases it | master gate missing (MOD) | master_ignored |
| gale.gale_deafens_outdoors | unroofed colonist gets RM_GaleDeafened | not applied (MOD) | no_deafen |
| gale.gale_spares_roofed | roofed colonist stays clean | roof ignored (MOD); room unroofed = UNMEASURED | deafen_ignores_roof |
| gale.gale_deafen_toggle_off | toggle off: not re-applied | toggle gates nothing (MOD) | deafen_ignores_toggle |
| gale.gale_turbine_surge | output ratio on/off in [1.2, 1.4] (shipped 1.3) | no surge (MOD); no "Power output" line = UNMEASURED (HARNESS) | no_surge |
| gale.gale_turbine_breakdown | turbine reads "Broken down" after two rolls at a 0.01-day mean | no breakdown (MOD) | no_breakdown |
| lash.lash_toggle_off_quiet | toggle off: no strike, no lash line | toggle gates nothing (MOD) | lash_ignores_toggle |
| lash.lash_strikes_once | one strike, reads Spent, none again in 600 ticks | no strike or repeat (MOD) | no_lash, lash_repeats |
| smother.smother_claims_stands | job banks claim on both stands, 2 blankets used | job/driver broken (MOD) | no_smother_bank |
| smother.smother_off_holds_claims | feature off: due claims wait, stands remain, read "ready to fall" | matures anyway (MOD) | smother_ignores_toggle |
| smother.smother_matures_to_dead_wood | feature on: stands gone, >= 20 dead venomvine | no maturation (MOD) | no_mature |
| dripping.dripping_survives_harvest | venom yielded, stand still standing (<= 60% grown) | harvest destroys it (MOD); no yield = UNMEASURED | regrow_broken |
| crown.crown_toggle_off_stays_away | toggle off: flutters stay > 6 cells away | gates nothing (MOD) | crown_ignores_toggle |
| crown.crown_mob_gathers | >= 2 of 3 flutters within 6 cells in the Stall | no mob (MOD); < 2 survive = UNMEASURED | no_crown |
| bloom.bloom_toggle_off_quiet | toggle off: no Flee in any species, no arms | gates nothing (MOD) or vanilla animals do flee people (assumption, see walk) | bloom_ignores_toggle |
| bloom.bloom_answers_a_walker | all 4 species seen on a Flee job, >= 1 vissler arm | a species is silent (MOD) | no_bloom |
| sweetline.station_named_and_timed | label `<name> (sweetline tree)` and a wool-timer line | not named/timed (MOD) | no_name |
| sweetline.station_toggle_off_plain | toggle off: plain label, no timer line | gates nothing (MOD) | station_ignores_toggle |
| sweetline.station_sheds_wool | >= 5 wool after a 5.5-day jump + 2100 ticks | no shed (MOD) | no_wool |
| log.log_clean | no LeaningScrub error, no xref error naming our defs | load-time defect (MOD) | log_error |

`*_site_ready` components (5): fixture build; a FAIL or UNMEASURED there marks the rest of that chain UNMEASURED (SITE/HARNESS).

## Live shapes this script assumes and has NOT seen (each reads UNMEASURED if absent, never PASS)
wind-turbine inspect "Power output" line; `get_def` comps as a list; `get_roof_batch.roofedCells`; `pawn_flight report` rows with `canEverFly`; `harmony_patches` naming the `get_DesiredPowerOutput` getter and `owner` = mandrake.rm.leaningscrub; `list_pawns includeHealth` hediff rows; `site_state` job strings ("Flee", "Wait_Wander"); `inspect_string` label for a named tree; `list_things` rows carrying `stackCount`; `designate_batch` + `ordered_job` Harvest/Refuel/RM_SmotherVenomvine shapes. First run settles them; fix as HARNESS, then rerun.

## Not covered (walk says UNCOVERED, with reason)
The Lean (3 lines): needs a Scrub-biome map (the Lean caches `Applies` on first use). Filed as the suggested follow-up `LEANING_SCRUB_LEAN_SITE_1` (a Pyrelands-style site recipe: re-tile a scratch-world tile to RM_LeaningScrub, generate, home, reload). Not filed in the ledger by this subagent. Also: Gale raid weighting (statistical; patch armed only), dripping OFF arm (def mutation at startup), venomvine passability effect, recipe/bill flow, History panel text, save/load name persistence, visual canopy.

## Offline proof
- `python3 src/RimMandrake/LeaningScrub/selftest_leaningscrub.py`: healthy 43/43 PASS; 32 breaks each red exactly the named component.
- `python3 src/RimMandrake/Utils/northstar_driver/lint_calls.py` over the 3 files: 0 problems (59 literal calls).
- `northstar_driver/cli.py run --mock --mod LeaningScrub --plan ... --mock-skip-site`: runs to completion (the stock MockGame lacks most tools, so its components read FAIL/UNMEASURED on "mock: unknown tool"; that proves the plumbing, the selftest above proves the predicates).
- `modcheck floor --all`: LeaningScrub row is `no bar` (the verdict `bar met` exists only for a VALIDATED north-star walk; this walk deliberately has no north-star section). Walk lints clean (`walklint`).
