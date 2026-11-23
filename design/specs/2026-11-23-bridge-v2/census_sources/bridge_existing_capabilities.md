# Bridge existing capabilities (census, skeleton)
Sources: skills/rimbridge/references/tool_census.txt = 547 tools (live list 2026-11-01: deepfire 8, jawa 413, rimbridge 16, rimworld 110). Companion C# source is NOT in this repo (grep of [Tool( in src/ finds only python/test mentions, ~10 distinct strings).
(progress: read tool_census, capability-matrix, rimbridge SKILL, performance, flight, pawn-authoring, map-authoring(grep), live-debugging-proof-harness. Remaining: companion, live-review, load-round, test-pilot, lightspeed-authoring/references for calm+telemetry)
Source count (this clone, src/RimMandrake/bridgetools/JawaBench.BridgeTools/*.cs, [Tool( names only, no bodies read): 435 jawa/+deepfire/ names. 16 are in source but NOT in the 2026-11-01 census: alloc_probe cond_eval debug_action_menu game_comp_timing get_pawns_batch get_power_nets_batch heap_census heat_events list_things_batch map_seed_foil mod_settings_fields nulltex_probe run_scenes settle_tweens texture_memory thing_read.
(progress: read companion, telemetry, harness refs; remaining live-review, load-round, test-pilot, quiet/calm greps in silent-failures/traps)
(progress: read all assigned except load-round detail done via grep; now calm/quiet greps, silent-failures/traps for time limits/errors/safety)

---
# THE SIX SECTIONS (inventory only; no code-quality judgement)
Skills root: `/home/mandrake/rm/relentless/clones/RIMMANDRAKE_DESIGN_BRIDGE_TWO_WHAT_LIVE_TESTING_NEEDS_FABLE_PASS_ONE.det/skills/` (abbrev `S/`).
Counts: 547 tools in the live census of 2026-11-01 (`S/rimbridge/references/tool_census.txt`: deepfire 8, jawa ~413, rimbridge 16, rimworld ~110). Source `src/RimMandrake/bridgetools/JawaBench.BridgeTools/*.cs` has 435 `[Tool]` names (jawa/ + deepfire/; found with a multiline grep, because the brief's one-line grep matches only 10 junk lines). 16 are in source but not in the census: alloc_probe, cond_eval, debug_action_menu, game_comp_timing, get_pawns_batch, get_power_nets_batch, heap_census, heat_events, list_things_batch, map_seed_foil, mod_settings_fields, nulltex_probe, run_scenes, settle_tweens, texture_memory, thing_read.
Namespaces: `rimworld/*`, `rimbridge/*` are stock RimBridgeServer; `jawa/*` and `deepfire/*` are our companion DLL (registered only at server startup).

## 1. Tool inventory by area
**Environment control**
- Incidents/storyteller: jawa/fire_incident, fire_quest, fire_raid, raid_preview, raid_shape_fire, incident_schedule, incident_journal, incident_parms_preview, incident_queue_clear|peek|remove, forecast_incidents, manhunter_preview, storyteller_comps|fire|swap, quest_lifecycle, send_letter, letter_send_delayed, letter_list.
- Weather/conditions/temperature: weather_get|set|roll_next, set_weather_buildup, rain_suppress, game_condition, cell_temperature, thing_ambient_temp, room_heat, sky_glow_set, glow_at, set_gas, set_pollution.
- Needs/mental/health: pawn_need, pawn_refresh_needs, pawn_mental, pawn_force_mental_break, pawn_break_thresholds, pawn_health, health_profile, pawn_severity_adjust, pawn_force_incapacitate, pawn_resurrect, pawn_restore_part, restore_needs.
- Animals: animal_bond|resource_force|stats|train|train_wanted|trainable_visibility, pen_pin|release, wild_spawner_block.
- Visitors: spawn_pawn (faction chosen), lord_* tools (below). No dedicated "visitor" tool named in the census.
- Factions: faction_create|flags_set|goodwill_check|goodwill_situations|ideo_get|ideo_set|leader_get|name_get|name_set|relations_get|relations_set|territory_settings, list_factions, set_faction_relation.
- Fire/damage: damage, damage_log, explosion_at, map_explosion, map_fire, projectile_damage, kill_hostiles, roof_collapse; rimworld debug actions `Actions\Explosion...`.
- Plants: set_plants, set_crop, scatter_at.
**Scene preparation**
- Map/world: map_info, map_commit, map_drop, map_zones, set_current_map, world_tile_map_generate, colony_found, make_empty_room, clear_area, wipe_cell, destroy_batch|bulk, refresh_rect, rebuild_dirty_regions, fix_floating_roofs, large world_* family (incl. world_view).
- Terrain/structures: set_terrain, set_terrain_batch, get_terrain_batch, set_terrain_layer, get_terrain_layers, set_roof_batch, get_roof_batch, set_substructure_batch, paint_area, paint_building, canal_dig, set_fog, set_deep_resource, blueprint_place, build_batch, build_check, prefab_capture|list|place, kcsg_place, rimworld/apply_architect_designator, designate_batch.
- Things: spawn_batch, spawn_fill_area, spawn_pawn, spawn_variant, spawn_mech_cluster, rimworld/spawn_thing, set_stuff, set_quality, set_thing_props, container_fill, split_stack, thing_minify, thing_refuel, list_things, list_pawns.
- Pawns: pawn_gear, pawn_genes, pawn_traits, set_pawn_skill|backstory|identity|appearance|age|gender|faction|ideo|style|xenotype|rotation, grant_xp, grant_ability, pawn_psychic|pregnancy|romance|relations|thoughts|memory|roles|stats|portrait|atlas|origin|census|get|flight, pawn_use_ability|verb, instant_recruit, lock_apparel, inventory_transfer.
- Debug-menu reach: rimworld/execute_debug_action (whole dev menu), list_debug_action_roots, list_debug_action_children (safe), search_debug_actions (DANGEROUS on full stack).
**Pawn guiding**
- order_pawn, ordered_job, stop_job, set_draft (jawa/ and rimworld/), pawns_patrol_route, lord_assault_spawn|defend_spawn|destroy|pawn_move|poke|set_job|set_point|travel_to, set_work_priority, prioritized_work, timetable, bill_*, workgiver_probe, rimworld/select_pawn, right_click_cell, drag_cell (times out). Teleport: via spawn/move tools (lord_pawn_move, debug actions); no single named "teleport" confirmed in what I read.
**Time advance**
- jawa/safe_advance (client `B.ticks`), rimworld/step_game_ticks, jawa/time_set_ticks, time_clock, time_date_at, time_perf, time_pin_normal_speed, set_game_speed, set_time_speed, pause_game, play_for, play_until_letter.
- Limits: see section 5. safe_advance: paused, DoSingleTick in chunks of <=60 inside a 40 ms frame budget, vitals latch checked after every chunk, may stop early (read `executed` vs `requested`). step_game_ticks: one tick per frame, >~2000 ticks frame-times out. time_set_ticks simulates nothing, ages absolute-tick timers; refused with a spawned colonist unless `timeException=true` + `why`. Advances >30,000 ticks need a safe colony (owner 2026-11-23). `B.until` / `B.watch` PLANNED, not built; safe_advance has no `until`.
**Observation and telemetry**
- Reads: comp_read, map_comp_read, get_def, get_defs, inspect_string, thing_explain, stat_explain, thing_stats, get_cell_info, get_cells_info, list_things_batch/get_pawns_batch/get_power_nets_batch/thing_read (source only), rimworld/list_colonists, get_game_info.
- Logs/journals: drain_log, rimbridge/list_logs, list_operation_events, damage_log, incident_journal, tale_list|record, health, vitals, heat_events (source only).
- Perf: map_comp_timing, game_comp_timing (source only), tps_report, tps_test_attribution|block, time_perf, load_stall_probe, alloc_probe/heap_census/texture_memory/nulltex_probe (source only).
- Recording control: telemetry_mark, telemetry_tier, awareness, set_colonist_job_logging, rimworld/dpa_snapshot|status|patch_methods|stop|reset|cleanup (never explored).
- Playtests: playtest_start|status|collect, gss_playtest_*, run_scenes (shared [RMTest] scene runner, source only).
- Scripted/eval: jawa/static_call (PUBLIC STATIC method by type FullName + method name, '|'-separated args); rimbridge/run_lua, compile_lua, get_lua_reference, run_script (a Lua-shaped DSL, not general Lua); jawa/cond_eval (condition-tree dry run; built, source only, no live pass recorded). No general C# or expression evaluator.
**Screenshots and camera**
- rimworld/take_screenshot, screenshot_cell_rect, jawa/take_screenshot (fileName), clear_ui, window_list_close, screenshot_mode, frame_cell_rect, frame_pawns, jump_camera_to_cell|pawn, set_camera_zoom, move_camera, get_camera_state, thing_screen_rects, artboard_stage|capture, review_label|sign, set_pawn_rotation, settle_tweens (source only), set_hover_target/clear_hover_target (no tooltip read).
**Save/load and snapshots**
- rimworld/save_game, load_game, load_game_ready, list_saves, start_debug_game(_ready), go_to_main_menu, jawa/autosave_now; prefab_capture|list|place (structure snapshots); get_terrain_batch (terrain snapshot/restore).
**Mod list and build identity**
- jawa/running_mods, mod_inventory, savegame_mod_match, companion_handshake, harmony_patches, dlc_status, mod_settings_fields (source only); rimworld/list_mods, get_mod_configuration_status, set_mod_enabled, reorder_mod; rimbridge/get_bridge_status, get_game_info. Offline: modset_builder, preflight_bridge.py; ModsConfig.xml describes the NEXT load, not the running one.
**Errors and safety**
- jawa/drain_log, log_autoopen_suppress, health (log.state must be `emitting`), vitals/safe_advance latch, rimworld/pause_game, set_god_mode, set_debug_setting, Verse.Log Clear via static_call, rimbridge/wait_for_game_loaded, wait_for_long_event_idle, wait_for_operation; host side: game_lock.py / `rimflow bridge take`, game_focus.preflight (Run in background must be on).
- NO first-exception tool: the first exception comes from Player.log, jawa/health `exc` counts (test tier), or the journal.

## 2. Cannot do / unreliable (quote + path)
General (`S/rimbridge/SKILL.md`):
- "`success: true` means the tool RAN, not that the game CHANGED."
- "A timeout is fatal to the CONNECTION, not to the call." Open a fresh connection, poll the post-condition.
- "The bridge answering is NOT the game being reactive" (~40 s after load).
- jawa/hot_reload_defs RETIRED (owner 2026-09-03); XML change needs a minimal-list restart.
- "NEVER call `search_debug_actions` against the full mod stack."
- ResolvePawn accepts player colonists only (hostiles unreachable via stock pawn tools).
- "`Actions\T: Destroy` targeted by x/z destroys EVERY thing in that cell."
- spawn_thing cannot set stuff; saveName honoured 2026-08-20 but not 2026-08-24; get_cell_info does not list pawns.
- spawn_thing/spawn_batch NPE on a Pawn defName on a VEF list. Two drivers on one game leave the bridge STUCK. All-null get_bridge_status = Run in background off. Inhabited leave/re-enter silently no-ops on player settlements.
- An unknown parameter name is silently dropped.
`S/rimbridge/references/capability-matrix.md`: "Apply damage..." inert (45 applications, 0 injuries); "Set terrain (rect)" / "Clear area (rect)" are drag tools, inert; drag_cell timeout; play_for "returned success:false once, unexplained"; save_game "ignores fileName"; "No hover/tooltip READ is known."; Lua is a "lowered DSL" (static indexes only); "Seven tools have never been driven in a live game" (set_roof_batch, get_roof_batch, list_factions, set_pawn_rotation, set_pawn_style, set_pawn_xenotype, order_pawn, as of that doc); Not-yet-explored: zones, mod settings read/write, UI clicking, saves beyond save_game, dpa_*; terrain restore does not restore destroyed plants.
`S/rimbridge/references/pawn-authoring.md`: "NOTES DO NOT EXIST."; pawn_refresh_needs fills nothing; set_work_priority number is a no-op when useWorkPriorities is off; backstory refreshes nothing; TryStartMentalState returns false silently; opinion is computed; ChangePsylinkLevel reaches only level 1 on first call; a spawned non-player pawn has no lord; spawn_pawn animal with no faction goes into Mechanoid; jawa/set_draft "no overseer" is a guess.
`S/rimworld-live-review/SKILL.md`: take_screenshot silently ignores x/z/zoom; frame_cell_rect does not zoom in past current zoom; jump_camera_to_cell can leave world view up; sky_glow_set does not survive to the shutter; "some generated maps render PURE BLACK, with no known bridge fix"; clear_log does not close the window; engine culls a non-home settlement map once time steps; save_game has written the current slot instead of the given name; start_debug_game_ready times out at 30 s and succeeds late.
`S/live-debugging-proof-harness/SKILL.md` (+references/sites-and-timing.md): B.until/B.watch PLANNED; 259 lines in 139 files still call step_game_ticks directly; ~57 copy-pasted ready loops; BATCHREADS planned; `lost>0` journal = UNMEASURED; a freshly built powered consumer reads PowerOn=false ~100 to 170 ticks; "The map is not calm on the full list" (wild animals respawn, a predator downed two colonists 2026-10-11); jawa/damage skips player pawns unless allowCol onists=true; bridge-spawned colonists can arrive with work types at priority 0, downed, or Mining-disabled; process-wide statics survive a scene change.
`S/telemetry/` traps: no pawn-vitals series, "A colony can die mid-pass with every telemetry row green".
`S/rimworld-load-round/SKILL.md`: minimal list cannot reproduce 21,872-tile geometry (Worldbuilder absent); ModsConfig not authoritative while game runs; hot_reload_defs clean-passed on 19 mods, destroyed pawn generation on 589.
`S/rimbridge-companion/SKILL.md`: a duplicate [Tool] name kills the whole provider; a build cannot overwrite the DLL of a running game; companions load only at server startup.
`S/rimworld-modding/references/flight.md` and owner rulings: see section 6.

## 3. Existing telemetry (what records over time)
- **Verse.Log** (game): stops ALL logging at 10,000 messages. `validation_core.log_revive` (static_call Verse.Log Clear + sentinel) and `log_alive` (sentinel check). LogMessageQueue holds 1000 entries, repeats counted to 99. `[Ref XXXXXXXX] Duplicate stacktrace` has no frames.
- **RimBridge journal**: ring of last 1,000 entries, all levels; a repeat is one row with RepeatCount. Read via rimbridge/list_logs / jawa/drain_log (`errorsOnly`, `contains`; contains has returned a STALE first message). Evicts after ~3,400 ticks (~0.3 info lines/tick); a save load writes ~1,000 lines.
- **validation_core.LogTap** (`tap_start`, `tap_after`, TAP_TOOLS): polls after tool calls, counts `lost`; lost>0 means UNMEASURED.
- **effects.logs** per-call capture: "structurally cannot see anything logged during step_game_ticks".
- **jawa/health**: frame-interval histogram, GC-spike coincidence, log counts per type + cap/logger state, bridge main-thread occupancy; observer producer "health_observer" off until an overhead test.
- **TPS record** (jawa/tps_report): standing, starts at game load, one window per ~5 real s; ratio, raw tps, paused/explained/stall seconds, fps, tick-work share, coarse attribution. Files in `...\JawaBench\tps`.
- **Test tier** (jawa/telemetry_tier; CLI `telemetry tier test --ttl 60`): 1 s windows with tick-duration histogram, log error/warning counts ahead of the 10,000 cap (exc), bridge occupancy (br); per-tick flight ring dumped to tps/flight/*.jsonl.gz on incident / tick over 250 ms; jawa/telemetry_mark (marker row; dump=true asks for last 8,192 ticks, only if armed, at most once per 30 s).
- **telemetryd** (Windows, E:\telemetry): VictoriaMetrics (8428), SQLite events.db, raw JSONL kept 90 days; CLI verbs health, at, events, around, bridge, disk, flight, exc, runs, series, query, mark, tier test|campaign, up|down. Producers: TPS record, health_observer, rimbridge_client (`scratch/bridge_calls.jsonl`, ~10 h / ~20 MB, tool names + timings only, no args/results), artpipe, deploy/winbuild/modset_builder change events. `rm_game_exc_suppressed` counts what the cap swallowed.
- **Event journals in game**: incident_journal (every IncidentWorker.TryExecute with outcome fields), damage_log (ring of every TakeDamage and real Kill: victim, def, amount, instigator, weapon, part, hediffs), tale_list|record, heat_events (source only), map_comp_timing / game_comp_timing (timed over N ticks, then unpatched), set_colonist_job_logging, playtest_*/gss_playtest_* collect, run_scenes.
- **Not built / planned**: cond_watch (CONDWATCH_BUILD_OWNED_RINGS), RINGPROBES_WIRE_EVENT_CURSORS, B.watch, a pawn vitals/colonist/hostile series.

## 4. Calm / quiet controls
- jawa/quiet_site: action=status lists hostile threat structures (turret, pawn spawner, dormant, condition causer, non-humanlike faction) and unsent proximity letters (e.g. Anomaly monolith); action=apply clearThreats etc. (rest of parameters unread). Reapply after load: not stated.
- jawa/rain_suppress: DisableRainFor(N ticks); does not stop rain already falling; deadline based.
- jawa/wild_spawner_block (block|release|get): blocks ongoing wild-animal replenishment; mapgen animals and deliberate spawns untouched; "GAME-SCOPED and DEAD-MAN" (releases itself), so reapply after a load.
- jawa/incident_queue_clear: clears the whole queue (no selective cancel); does not stop new incidents. storyteller_swap/storyteller_comps can change the storyteller.
- jawa/weather_set with lockWeather; jawa/time_pin_normal_speed (holds Normal ~800 ticks via SignalForceNormalSpeed, does not unpause).
- jawa/log_autoopen_suppress (Harmony prefix; suppressed by default).
- jawa/kill_hostiles; `jawa/destroy_bulk filter=nonColonists dryRun=false`. Harness rule: "Re-calm before every block, not once per run" (`S/live-debugging-proof-harness/references/sites-and-timing.md`, run-checklists.md).
- Drafting idle colonists, pawn_need set levels, set_pawn_rotation lock, set_god_mode.
- Pausing keeps a map alive (no ticks). Reapply-after-load is documented for none of the above except the dead-man wild block; weather/clock state is save-scoped, pins and Harmony toggles are session-scoped.

## 5. Measured costs (each carries its colony/tier)
- ping 0.3 ms; `hello` 0.8 ms; python.exe spawn 38 ms.
- Main-thread call 4 to 17 ms; median 16.7 ms at 568/593 mods on a 21-colonist colony; 5.8 ms on a quiet quicktest at 573 (the "16.7 ms frame gate" is refuted: it is workload). ~50 ms (53 ms) per poll round trip in a tight sequence; ~20 unbatched calls/s.
- Terrain: 421 cells one by one ~7.0 s; per-rect 124 calls 1,611 ms; set_terrain_batch 1 call 14.0 ms (115x); get_terrain_batch 17.5 ms vs 6,086 ms per cell (348x); 6x6 rect 15 ms; 2,601 cells reverted in one call each way; whole crater 0.52 s. Formation calls: crater 199 to 2, cavern 49 to 1, geyser field 67 to 2.
- save_game 13.9 MB in 0.5 s (14.9 MB rws elsewhere).
- Cold load: minimal list 22 s (13 mods; 27 mods later); quicktest world 5 s; full list ~25 min (2026-08-19), ~15 min (09-07), 18.5 to 21 min (10-03), ~14.5 min (11-21). Edit-build-deploy-test ~60 s. launch_and_wait + RimDefDump ~27 s, 1.2 GB.
- step_game_ticks over ~2,000 ticks frame-times out; client timeout 30 s; start_debug_game_ready up to 280 s. 2,500 ticks = 1 game hour. Speed 3 is CPU-bound, ratio ~0.05.
- list_debug_action_children on `Actions` (596 children) ~1 s. hot_reload_defs 0.04 s (minimal) vs hung 5 min (589 mods).
- Hose perf 0.152 ms/tick live vs 0.001 offline. 176 log lines per 600 ticks.
- safe_advance chunks <=60 ticks in a 40 ms frame budget. Power-on delay 100 to 170 ticks.
- Call counts: ~2,000 calls for one row in a poll loop; FlowWorks L_preflight 371 reads; a biome stage review ~50 calls; companion cycle 59 tools in one day.
- Tool counts: 141 (2026-08-12), 547 (2026-11-01), 435 in source now.
- Screenshot cost: no ms figure found; take_screenshot returns an absolute path; a screenshot is a cache until looked at.

## 6. Flight testing facts
- Owner 2026-09-25, three times: "For the third time, do not do live testing of flyers without a human present. It doesn't work." and "Don't try to capture images of flight. It doesn't work." Standing ruling: never live-test a flyer's flight.
- FIREHAWK hunt: ~35 min, ~25 screenshots, dozens of checks, caught nothing (inconclusive).
- Verification route: deterministic state read jawa/pawn_flight (reads Pawn_FlightTracker; JawaBenchFlightTools.cs). Live visual flight bars wait for a joint session (FLYERFRAMES_PROVE_JOINT_SESSION); the proof-line lint refuses flyer words unless the item is a vehicle.
- Engine facts (`S/rimworld-modding/references/flight.md`): CanEverFly is MaxFlightTime > 0 (a stat); flight animation is a separate flip-book (flyingAnimationFramePathPrefix, FrameCount); frame directions north/east/south only; ForceLand starts Landing at lerpTick 25 where LandingCurve is 0.4 (computed 0.36-cell drop in one tick, not seen running); durationTicks = (frames+1)*ticksPerFrame so the last pose holds double; AlternateGraphic has no flying field.
- Why capture fails (docs, mostly indirect): raw step is one tick per frame so frame timing against step_game_ticks cannot catch a short pose; a screenshot is a cache until looked at; take_screenshot ignores framing args; pawns are drawn at old spots after a paused step until settle_tweens / settled_shot; no doc names a single root cause beyond the owner's word "It doesn't work".
