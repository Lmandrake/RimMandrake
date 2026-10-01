# Worker note THE_FORGE_FIRST_SCRIPT_1

status: DONE offline, READY TO RUN. Authored by a FOUNDRY subagent, never live. No ledger event written.

Mod: `src/RimMandrake/TheForge` (packageId `mandrake.rm.theforge`, composed into `mandrake.rm.biomes`).
Tier: `baroque_wave0` (existing; nothing added to `modset_builder.py`).
Files: `src/RimMandrake/TheForge/validation.py` (75 components in 13 chains), `northstar_plan.py`, `northstar_site.py`,
`selftest_theforge.py`, walk `design/validation_walks/RimMandrake/TheForge.md` (DRAFT, blank hash, 75 of 75 components carry an arrow).

## Offline proof (all run from the repo root)

- `python3 src/RimMandrake/TheForge/selftest_theforge.py` -> healthy world: 75/75 PASS; 52 single breaks each redden exactly the
  components named in the table below; 3 log-line breaks, 1 cap-line (UNMEASURED) and 1 cross-mod control. "all passed (58 breaks)".
- `python3 src/RimMandrake/Utils/northstar_driver/lint_calls.py --summary src/RimMandrake/TheForge` -> 0 problems over 55 literal calls.
- `cd src/RimMandrake/Utils && python3 -m modcheck.cli floor --all` -> `TheForge  walk yes  subj ok  DRAFT  0 bars` (the same
  "no bar" row as every DRAFT sibling: the owner's `## north star` is untouched, blank hash). Toggle floor: all 15 wired toggles covered
  (`suite.toggles`), checked by the selftest.
- `northstar_driver/cli.py run --mock --mod TheForge --plan ... --mock-skip-site` runs to completion on the driver's generic mock
  (exit 1, NOT GREEN, like every sibling: that mock does not know the mod's tools). The real offline proof is the selftest's `FGame`.

## Live-run sheet

Prerequisite: the bridge is HELD (`python3 src/RimMandrake/rimflow/cli.py bridge who`), this commit is on `origin/main` and the shared
tree is synced (the run reads the repo's `TheForge/validation.py` and composes the biome from the repo's `src/RimMandrake/*`).

One command, from the repo root under WSL python3 (stop game, apply tier, compose-deploy, launch, quicktest world, run):

    python3 src/RimMandrake/Utils/northstar_driver/live_session.py --mod TheForge --tier baroque_wave0 --plan src/RimMandrake/TheForge/northstar_plan.py --compose

- Tier `baroque_wave0` = Harmony, five DLCs, RimBridgeServer, VEF, Alpha Biomes, FlowWorks, Luminous Pigment, `mandrake.rm.biomes` (13 mods).
  Launch wait: a 13-mod list loads in ~1 to 2 minutes (the live_session budget is 900 s); the quicktest world adds ~90 s.
  `--compose` is needed once (the game must be closed; live_session closes it): `deploy_custom_mods.py --compose biomes --apply`.
  The plan's `preflight` also runs the compose plan read-only and refuses on drift in TheForge / EnvironmentalHazards files.
- Driver alone, game already up on that tier with a FRESH quicktest map: `python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod TheForge --plan src/RimMandrake/TheForge/northstar_plan.py`
  (results JSON in `Transient/northstar/TheForge_<ts>.json`).
- Tick budget (from the offline model): ~12,500 stepped ticks, ~178 debug-action calls, plus clock JUMPS of ~360,000 ticks
  (the hiss chain jumps ~147,000; the dormancy chain jumps 170,000 to clear stale flash windows; two small ones). Expect minutes,
  not an hour; `step_game_ticks` truncates under load and `t.wait_ticks` loops until the real clock moved.
- Site prerequisites (preflight checks the first four): quicktest map >= 160x160 (the pad is 30 cells off the centre and ~54 wide);
  all five DLCs active; RM_TheForgeSettings and the shared hazard settings at shipped defaults; the bridge companion declares the
  tools in `northstar_site.TOOLS_NEEDED`; **a FRESH game** (spunstone not revealed, no temp terrain on the pad, Player.log below the
  10,000-message cap). No god mode needed. The suite builds its own pad (a 12x12 LavaDeep square on soil and a 10x10 yard).
- Side effects on the sandbox colony (a quicktest map is disposable): the gas wash lights REAL fires on unroofed flammable ground
  somewhere on the map (the wave centre is random); floods are released; a rat and some steel are burned; the clock moves forward ~2.5
  in-game days in total. The shared hazard `environmentalDamageEnabled` is switched OFF for the long Rain windows so the start colonists
  are not scalded (restored in a finally); only the voices chain's short Rain window runs with scald ON.
- What a PASS / FAIL / UNMEASURED means, per chain:
  - `log_clean`: FAIL = a Player.log line names this mod's content in an error (MOD, load class: read the FIRST exception);
    UNMEASURED = the log hit the 10,000-message cap (relaunch; every debug-action chain would be silent).
  - `defs_resolve` / `def_wiring` / `biome_wiring`: FAIL = the def did not load, a field is wrong, a patch matched nothing (MOD or STATIC:
    fix offline). UNMEASURED = `get_defs` cannot serialise `comps` / `modExtensions` / `terrainPatchMakers` / `statBases` under deep
    (HARNESS: those shapes are unproven live).
  - `settings`: FAIL = a field is not at its source default (a previous run left it, or the C# default changed).
  - `cycle_walk`: FAIL names the phase and the counter that disagrees with an independent read (terrain layers, list_things,
    list_pawns, weather_get, letter_list): MOD. UNMEASURED with "debug action ... logged no [RMTheForgeDebug] line" = the log cap or the
    action tree did not enumerate (HARNESS). `crust_is_walkable` is expected UNMEASURED if `get_cell_info` has no walkability key.
  - `cycle_arms`: each arm is independent. FAIL = that toggle does not do what its label says (MOD).
  - `dormancy`: FAIL on `natives_seal_in_still_heat` after a clean fresh start = MOD; UNMEASURED "random burst running" = rerun.
  - `voices`: FAIL = the visual cue is wrong or leaks with the voices off. `list_messages` shape is unproven (UNMEASURED if empty).
  - `spunstone`: UNMEASURED "already revealed" = the game is not fresh (SITE). `keelwork.keel_off_zeroes_saving` UNMEASURED = the Mod Settings
    dialog did not reach `RM_TheForgeMod.WriteSettings` (HARNESS) OR `ApplySetting` is broken (MOD): inspect, see FOLLOW-UP 4.
  - `floatstone_harvest`: FAIL = no `RM_Floatstone` after a forced harvest; first check `set_plants` placed a garden (terrain/temperature).

## Bars (75 components) and how each is broken to prove it can fail

The selftest breaks a mocked world; the live equivalent is in the right-hand column (what to edit or toggle to see the same red).
"Components" are `<chain>.<name>`.

| break (selftest key) | reddens | live equivalent |
|---|---|---|
| missing_def | defs_resolve.defs_resolve_items | delete or misspell the last item def in `RM_TheForgeItems.xml` |
| donor_shadow | defs_resolve.defs_resolve_plants | a donor def with a Forge plant's defName loading later |
| bad_mesh | defs_resolve.plants_mesh_count_is_perfect_square | set a plant's `maxMeshCount` to 6 |
| terrain_not_temporary | defs_resolve.cycle_terrains_are_temporary | drop `<temporary>true</temporary>` from `RM_PumiceRubble` |
| no_scald_def | defs_resolve.scald_damage_def_resolves | run on a tier without TerminalBiomes' `RUT_Scald` |
| no_jobdormancy / no_forge_comp | def_wiring.native_dormancy_comps_wired | remove `jobDormancy` / the Forge comp from a native |
| flyer_no_stat | def_wiring.flyers_carry_flight_stat | set `MaxFlightTime` to 0 on the jossur |
| floatstone_generated | def_wiring.floatstone_only_from_gardens | set `generateCommonality` above 0 |
| brace_no_research / engine_unlinked | def_wiring.keel_brace_needs_spunstone_research / engine_links_keel_brace | drop the research prerequisite / break the patch xpath |
| zero_density, roster_zero, plant_row_missing | biome_wiring.biome_densities_live / wild_animals_wired / wild_plants_wired | zero `animalDensity`, set a row to 0, delete a row |
| no_map_condition, no_heat_ext, no_lava_patch | biome_wiring.biome_map_condition_is_forge_pulse / biome_declares_ambient_heat / biome_lava_patchmakers | remove the `biomeMapConditions` item, the `RM_SunHeatExtension`, the LavaDeep threshold |
| settings_drift | settings.settings_at_shipped_defaults | change a C# default |
| no_gas | cycle_walk.gas_wash_ignites | remove all flammable plants, or break `GasWashWave` |
| no_flood, rain_wrong_weather | cycle_walk.rain_forces_boiling_weather_and_floods | break `TryFloodRelease` (FlowWorks def); change the burst weather |
| freeze_partial, lava_touched | cycle_walk.freeze_crusts_lava (+ cycle_arms.bloom_off_no_gardens reads the crust count too) | cap `maxFrozenCells`; make the crust replace the top terrain |
| no_gardens | cycle_walk.growth_blooms_floatstone | null `gardenDef` |
| garden_vanish | cycle_walk.cracks_drift_gardens_and_glow | `Destroy` gardens without counting |
| melt_keeps_crust | cycle_walk.melt_restores_lava_and_counts_losses (and every later chain's site setup) | skip `RemoveTempTerrain` |
| melt_silent | the same | kill things without `AddLoss` |
| no_letters | cycle_walk.telegraph_letters_sent (+ the hiss comp) | `cycleTelegraphLetters` ignored |
| gas_off_ignored, flood_off_ignored, freeze_off_ignored, bloom_off_ignored, melt_gentle_ignored, telegraph_off_ignored | the matching `cycle_arms.*_off_*` | stop reading the toggle |
| gate_pulse_ignored, gate_grand_ignored | cycle_arms.cycle_gate_off_* (and cycle_off_melts_back_gently) | stop reading the gate / `CycleActive` |
| no_hiss, hiss_ignores_gas_toggle | still_heat_hiss.hiss_letter_sent_before_gas_wash / hiss_not_sent_with_gas_wash_off | drop the letter / the `gasWashEnabled` test |
| never_seal | dormancy.natives_seal_in_still_heat (+ fresh_natives_seal) | `jobDormancy` false |
| dormancy_off_ignored | dormancy.dormancy_off_clears_sealed_line | `CompInspectStringExtra` ignores the toggle |
| rain_not_waking | dormancy.rain_wakes_all_natives | break `RainingNow` for a native |
| no_clock_text, clock_off_ignored | dormancy.dhuvvox_clock_shows_countdown_and_slows / clock_off_removes_slowing | drop the countdown / ignore `dhuvvoxClockEnabled` |
| dhokkur_stays_awake_dry, julmox_seals_flash | dormancy.dry_growth_seals_dhokkur_only | dhokkur flagged awake in the flash window / julmox flag cleared |
| voices_off_ignored, no_cue | voices.voices_off_no_cue / visual_cue_message_names_phase | cue ignores `forgeVoicesEnabled` / never shown |
| project_visible, reveal_noop | spunstone.project_hidden_until_studied / reveal_opens_project | break the Harmony postfix / `Reveal` |
| harvest_noop | floatstone_harvest.floatstone_garden_yields_floatstone | clear `harvestedThingDef` |
| keel_wrong, keel_apply_garbled | keelwork.keel_default_saving / keel_off_zeroes_saving | change the brace's saving / break `ApplySetting` |
| log lines (3), log cap | log_clean.player_log_names_no_forge_error (FAIL / UNMEASURED) | a config error naming a Forge def; the mesh error; 10,000 messages |

Checks that are NOT able to fail for the reason a reader might assume (honest limits, all in the walk as UNCOVERED or in the
component's own comment): `dormancy_off_clears_sealed_line` proves the toggle is read, not that a pawn woke (the inspect string is
null with the toggle off; no tool reads dormant state); `crust_is_walkable`, `keel_off_zeroes_saving` and several `deep` reads go UNMEASURED
rather than PASS when their shape is missing.

## Findings the offline model made (suite defects fixed, plus mod notes)

1. A debug-stepped Rain leaves its forced burst running 6-9 h, so the freeze's Fog never shows after `advance one phase`: the suite moves
   the clock past the burst before reading the weather. (Walk: RULED OUT.)
2. A debug-stepped Growth leaves its flash window open (up to 66 h): julmox and dhuvvox stay awake in it. Dormancy runs last and jumps
   170,000 ticks first. (Walk: RULED OUT.)
3. Ending a condition does not melt the crust; every cycle chain winds the cycle down in a finally, and `_reset_pad` refuses leftover crust.
4. `RM_CompForgeCycleDormancy.CompInspectStringExtra` returns null with the toggle off, so the sealed line cannot prove a wake.
5. Mod-side observations, not defects proven live: `RM_ForgePulse`'s scald def `RUT_Scald` lives in TerminalBiomes (an RM-tier def with a
   campaign prefix; it resolves because TerminalBiomes is composed, but a tier without it silently disables scald); `DebugAdvancePhase`
   is not faithful to a natural cycle (see FOLLOW-UP 6).

## Unproven shapes (UNMEASURED if wrong, never PASS)

`get_defs` deep serialisation of `comps`, `modExtensions`, `terrainPatchMakers`, `statBases` (key names `value` / `stat`);
`research_availability.isHidden`; `list_pawns(includeHealth).health` hediff rows (the suite flattens the block and looks for the defName);
`list_messages` rows; `get_cell_info` walkability key; `inspect_string` on a pawn id; the debug-action label flattening under `Actions`
(copied from the Deepfire suite, which ran live); `open_mod_settings modId=mandrake.rm.biomes` reaching the Forge's `Mod` among the
composed pack's many.

## FOLLOW-UP ITEMS

1. `FORGE_PAWN_DORMANT_STATE_TOOL_1` - a companion `[Tool]` `jawa/pawn_dormant` returning `CompCanBeDormant.Awake` and the current job def for
   given pawn ids, so a sealed/woken state does not depend on an inspect string that the toggle itself nulls.
2. `FORGE_KEEL_GRAVSHIP_SITE_1` - a site recipe that builds a minimal gravship (grav engine on substructure, N keel braces) and reads the
   pilot console's fuel per tile (expect 10 -> 9.5 per brace, toggle off -> 10), skills/gravship-layout.
3. `FORGE_SPUNSTONE_STUDY_LOOP_1` - a site recipe with a researcher, a mature garden and the Anomaly study work giver, asserting the
   colony study counter rises and reveals the project at 12 points.
4. `NORTHSTAR_SETTINGS_WRITE_TOOL_1` - a companion `[Tool]` that runs a NAMED `Mod` class's `WriteSettings` (the dialog route opens the
   composed pack, which hosts many `Mod`s); needed by `keelwork.keel_off_zeroes_saving` and every composed biome with WriteSettings effects.
5. `NORTHSTAR_TEMP_TERRAIN_CLEAR_1` - a verb that clears the TerrainGrid temp layer over a rect, so a site reset is robust after a failed run
   (today a leaked crust refuses the next chain's setup).
6. `FORGE_DEBUG_ADVANCE_FAITHFUL_1` - make `RMTheForge: Forge cycle: advance one phase` end the Rain burst when leaving Rain and close the
   flash window when leaving Growth (what a natural cycle does), which removes the 170,000-tick jump and the burst-weather workaround; and
   have the report action also print through a `[Tool]` JSON read (`FORGE_CYCLE_STATE_TOOL_1`) so cycle reads stop depending on `Log.Message`
   and RimWorld's 10,000-message cap.
