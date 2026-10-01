# Worker note WASTELAND_FIRST_SCRIPT_1 — Wasteland first north-star script (READY TO RUN)

Mod: `src/RimMandrake/Wasteland` (packageId `mandrake.rm.wasteland`; ships COMPOSED in `mandrake.rm.biomes`, wave 2).
Tier: **`baroque_wave0`** (existing: BRIDGE + Harmony + Vanilla Expanded Framework + Alpha Biomes + FlowWorks + Luminous Pigment + `mandrake.rm.biomes` + the five DLCs, 13 mods). No new tier added.
Files: `validation.py` (22 chains, 154 components), `northstar_plan.py` (`USE_SUITE=True`, `EXPECT_MODS=("mandrake.rm.biomes",)`), `northstar_site.py`, `selftest_wasteland.py`, walk `design/validation_walks/RimMandrake/Wasteland.md` (DRAFT, blank hash; 37 `## must be true` lines, 24 covered and 13 UNCOVERED with a named reason, every one carrying an arrow).

## Offline proof (all run clean)
- `python3 src/RimMandrake/Wasteland/selftest_wasteland.py`: a healthy mock world passes all 154 components, and **more than 50 deliberate breaks** each redden exactly the components named for them (the break names are the "how to break it" for every check; a few listed below). Also tests `ensure_wasteland_map` (re-tile, found, generate, home) and its failure modes, and that every walk arrow names a real component.
- `python3 src/RimMandrake/Utils/northstar_driver/lint_calls.py src/RimMandrake/Wasteland`: 0 problems (every tool and parameter literal, checked against the declared schemas).
- `python3 src/RimMandrake/Utils/northstar_driver/cli.py run --mock --mod Wasteland --plan src/RimMandrake/Wasteland/northstar_plan.py --mock-skip-site`: runs to completion.
- `modcheck floor --all`: `Wasteland  walk yes  subj ok  DRAFT  no bar` (no hashed north star, so nothing to refuse); the Mod Settings toggle floor is met (all 23 bool toggles have a covering component; selftest asserts it). walklint clean.

## LIVE-RUN SHEET (bridge held; run from WSL, repo root)
One command (stops the game, applies `baroque_wave0`, composes + deploys `mandrake.rm.biomes`, launches, starts a quicktest world, runs the driver):

    python3 src/RimMandrake/Utils/northstar_driver/live_session.py --mod Wasteland --tier baroque_wave0 --plan src/RimMandrake/Wasteland/northstar_plan.py --compose

- Launch wait: the script's own (up to 15 min to `Bridge token:` on the 13-mod list is far less than the 599-mod cold load; expect a few minutes).
- Driver only (game already up on the tier, composed mod deployed, a quicktest world running): `python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Wasteland --plan src/RimMandrake/Wasteland/northstar_plan.py`. Results JSON in `Transient/northstar/Wasteland_<ts>.json`; per-component progress echoes to stderr as `[wl] hh:mm:ss <component> <verdict>`.
- Tick budget: about **28,000 game ticks** of waiting in total (storms 9.5k, smolderback 3.2k, flora 4k, casks 3.1k, Middenshell body 2.4k and procession 3.6k, the rest small). Budget 10-20 minutes of driving.
- Site prerequisites (`northstar_site.preflight` does them, none by hand): game on the tier with all five DLCs; settings at shipped defaults (it reads all 33); the composed mod in the game folder equals source (plan-only `deploy_custom_mods.py --compose biomes`, refuses on drift; that is what `--compose` fixes); a quiet storyteller (`Tutor`) and an empty incident queue; **a map whose biome is `RM_Wasteland`**, built on the scratch quicktest world: it picks the first flat dry riverless tile 20..260 ids from the colony tile, re-tiles it to `RM_Wasteland` (10 C, rainfall 0, flat), clears its mutators, founds a player colony, generates 150x150, makes it current and spawns 3 `PlayerColony` colonists. If that build fails the error is printed (`[wl-site] SITE NOT BUILT`) and kept in `northstar_site.LAST_SITE_ERROR`; the eight biome-gated chains then record UNMEASURED (never PASS) and the rest still run. No god mode needed (`NEED_GOD=False`). The scratch world is discarded; nothing here chooses a seed or produces a player-facing world.
- Do not run `modcheck run Wasteland` (it swaps the mod list and appends a packageId that is not in ModsConfig).

### What a PASS / FAIL of each chain means
| chain | PASS means | FAIL means |
|---|---|---|
| log_clean | no Player.log error line names any Wasteland def | a def was dropped or misconfigured at load |
| defs_resolve (16) | all 79 shipped defs resolve, from this mod | a def is missing/shadowed (silently dropped whole) |
| settings_defaults (34) | all 33 fields at their C# defaults | a default drifted or the assembly is not loaded |
| biome_roster (8) | densities, 12 animals, 12 plants, no donor rows, storm opt-in, no cinderwire, no rain | roster drift, zero density, missing extension |
| patches_landed (4) | MovingDunes binding and brine scatter registration landed | a patch matched nothing (**expected RED, see below**) |
| flyer_state | Grimewing `canEverFly` true, walker false | MaxFlightTime is 0 or the read cannot say False |
| storm_ash_on / _off | dose, fall pollution and cinderfelt germination each present with the toggle on and each absent with it off | the storm layer is inert or a toggle gates nothing |
| named_storm_halo / _cinderwire / _phases_off | warning message, dose held, unleashed message, dose; and strike-at-once when off | the phase controller or its hold is broken |
| smolderback_room | doses its own room only, heats it, each OFF arm and the master switch stop it | dose leaks across rooms / no heat / a toggle gates nothing |
| processor_animals | feed-ground gate shows on the inspect pane, gather places bezoar/soot brick, toggle hides growth | gate not gating / gather places nothing |
| gripper | spawns carrying, forced steal swaps scrap for gold, hurt drops haul, OFF arms empty-handed, tame never steals | any of those wrong |
| flora_harvest | four plants yield their items | a yield never arrives |
| brine_deposits | scatter places each deposit, deposits name their item, drazz gives brine shock | wiring broken |
| cask_leaks / cask_bay / launch_check_patch | leak never silent, bay holds/leaks/powered readouts, Harmony postfix installed | containment or readout broken |
| middenshell_body | 20 wide, crawls, wake crushes bait, trail, off stands still, aura, death quarry | any of those wrong (a width under 20 is a REPORT, never a shrink) |
| middenshell_procession | incident gating, omen letter + creeping metal, arrival in procession, trail, procession-off arrives at once | any of those wrong |
| rite_of_tipping | pad unlicensed then licensed, quest Ongoing, toggle refuses | contract wiring broken |

UNMEASURED means the check could not ask (a missing tool shape, a non-Wasteland map, no usable faction for the tipping contract); it is never a pass. The tipping contract needs a non-hostile humanlike faction on the quicktest world: if there is none, `quest_fires_and_is_ongoing` is UNMEASURED with that reason and the two components that depend on it follow.

### Expected first-run REDs (known defects, found by reading, each has a check that goes red for its reason)
1. `patches_landed.dune_field_binding_on_the_biome`, `dune_weather_binding_on_the_ash_storm`, `dune_material_def_exists` (MOD): `RM_Wasteland_MovingDunesBinding.xml` is wrapped in `PatchOperationFindMod` on the name 'Moving Dunes', which does not exist once MovingDunes is composed into `mandrake.rm.biomes` (`biomes_compose_sweeps.py` finding 3 already lists it). The whole ash-drift binding is dark.
2. `cask_leaks.breached_cask_text_does_not_claim_a_bay_that_is_not_there` (MOD, cosmetic): `RM_CompWasteCask.CompInspectStringExtra` prints "Breached, but held by a sealed cask bay." for any breached cask that is not leaking, which includes leaks switched OFF with no bay anywhere.

### Unproven shapes the first live run settles (each records UNMEASURED if absent, never PASS)
`rimworld/list_messages` and `jawa/alerts_list` rows (read with a recursive string scan), `jawa/room_get.rooms[].temperature`, `jawa/harmony_patches` rows, `jawa/get_defs` serialising `baseWeatherCommonalities` / `extraGenSteps` / `modExtensions` / a building's `mineableThing`, `jawa/letter_list` labels, `jawa/animal_resource_force.gatheredThing.resourcePlacedOnMap`, `jawa/ordered_job` accepting an animal as the pawn, `rimworld/spawn_thing` placing a 3x2 bay and a 20x20 body, `jawa/world_tile_get` row keys (`tile`/`biome`/`hilliness`/`riverCount`...), a stuck `world_tile_map_generate`. Live messages expire in seconds, so every message read sits right after its event and the cask-leak message is a note, not an assertion.

### Known low-probability false reds
`gripper.hurt_gripper_drops_its_haul` (ten hits at 50% each: 0.1%), `storm_ash_on.ash_storm_end_germinates_cinderfelt` (needs a few of ~7 fresh-fall cells to be plantable: well under 1%), `middenshell_body` crawl bait (the body also turns at 4% per step; the bait ring covers all four headings).

## FOLLOW-UP ITEMS
- `WASTELAND_MOVINGDUNES_BINDING_DARK_1` (MOD, bug fix, allowed in the pause): re-guard `Patches/RM_Wasteland_MovingDunesBinding.xml` so it lands in the composed mod (FindMod on 'RimMandrake: Baroque Biomes', or a `PatchOperationConditional` on the dune def existing); done when the three `patches_landed.dune_*` components go green.
- `WASTELAND_CASK_TEXT_LIES_1` (MOD, cosmetic): test `Bay != null` before printing "held by a sealed cask bay" in `RM_CompWasteCask.CompInspectStringExtra`; done when the guard component goes green.
- `WASTELAND_BRINE_TOGGLE_WIRE_1` (MOD): `brineDepositsEnabled` gates nothing (its own C# header says scaffolding); wire it into a `GenStep_ScatterThings` subclass or drop the toggle (CLAUDE.md "superb Mod Settings"). Then add the effect arm.
- `WASTELAND_STORM_STATE_READ_1` (companion `[Tool]`): read `RM_MapComponent_StormPhases` (phase weather, unleashed, EMP and strike counts) and `RM_MapComponent_WastelandStorms.FreshFallCount`, so the warning-phase checks stop leaning on the expiring message list and the EMP/lightning bar becomes measurable (needs the C# to count pulses).
- `NORTHSTAR_TERRAIN_CENSUS_TOOL_1` (companion `[Tool]`): `jawa/terrain_census rect defs` returning per-TerrainDef cell counts, so the Middenshell's pressed track and edge scar and the brine terrain are read directly instead of through filth counts.
- `WASTELAND_BAY_GIZMO_SCRIPT_1` (script): cover bay processing and illegal reburial by selecting the thing and `rimworld/execute_gizmo` on its `Command_Toggle`, then reading the product / the vanished cask.
- `WASTELAND_PROCESSION_CROSSING_SCRIPT_1` (script, long): one full 150-cell crossing (about 60,000 ticks at 400 per cell) for the exit scar, a waste-stockpile lure bend and the tentacle grab count.
- `WASTELAND_TIPPING_DELIVERY_DRIVE_1`: a way to advance the contract to its first delivery (time skip that ticks the quest part, or a debug action) so deliveries, the evidence ask and the containment grant can be read.
