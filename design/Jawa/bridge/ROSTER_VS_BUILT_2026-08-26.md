> 🔴 **SUPERSEDED IN PART, later the same day (2026-08-26), by BUILD.** The census below reads
> **163**; it is now **198**. The 32 remaining EASY capabilities shipped at `948c3399`
> (`JawaBenchPawnKitTools.cs` 10 · `JawaBenchGroupTools.cs` 11 · `JawaBenchSystemTools.cs` 11),
> plus `jawa/thing_stats` at `70b3b117`. ⛔ **Every "not built" verdict below is therefore
> suspect** — check the live list before acting on one:
> `grep -rho '"jawa/[a-z_]*"' src/RimMandrake/bridgetools/JawaBench.BridgeTools --include=*.cs | sort -u`
> The still-open block is MEDIUM: `infrastructure/state/work/BRIDGE_TOOLS_MEDIUM_REMAINING.md`.
> The method in this file — walk the roster against the SOURCE, never the roster's own
> annotations — is exactly right and is why the stale flags were caught at all.

# Roster vs. built — the 2026-08-26 walk

Walks every candidate row in `design/Jawa/bridge/BRIDGE_CAPABILITY_ROSTER.md` (103
capability rows) against the companion source as it stands today, not the roster's own
stale annotations.

**Built-tool census, from `src/RimMandrake/bridgetools/JawaBench.BridgeTools/*.cs`,
every `[Tool(` attribute, counted 2026-08-26:**

| file | tools |
|---|---|
| JawaBenchWorldTools.cs | 33 |
| JawaBenchTerrainTools.cs | 32 |
| JawaBenchPawnTools.cs | 18 |
| JawaBenchMapTools.cs | 16 |
| JawaBenchSimTools.cs | 12 |
| JawaBenchResearchTimeTools.cs | 11 |
| JawaBenchJobTools.cs | 10 |
| JawaBenchNeedsTools.cs | 9 |
| JawaBenchEventTools.cs | 13 |
| JawaBenchDiagnosticTools.cs | 4 |
| JawaBenchFactionTools.cs | 3 |
| JawaBenchVehicleTools.cs | 1 |
| JawaBenchCacheTools.cs | 1 |
| JawaBenchInit.cs | 0 |
| **TOTAL** | **163** |

163 unique `jawa/…` names, no duplicates. This is higher than the roster's own
"~119–121" estimate (itself already flagged stale) — six whole files
(Job/Needs/ResearchTime/Sim/Diagnostic/Faction/Vehicle/Cache) did not exist as
categories in the 2026-08-22 pass and between them close several rows the roster
still lists as open or partial (`pawn_force_job` → `jawa/ordered_job`; `create_allowed_area`
→ `jawa/new_allowed_area`; the storyteller-write half of `set_storyteller` →
`jawa/difficulty_tune`). One previously-BUILT row was also found to be **overstated**
on re-check: `jawa/fire_raid` does not carry `kind`/`count`/age-restriction/steal-kidnap-flee,
so it is downgraded to PARTIAL here.

## Summary

| verdict | count |
|---|---|
| BUILT | 58 |
| PARTIAL | 11 |
| NOT BUILT | 34 |
| **TOTAL rows** | **103** |

No row was too vague to judge — every row had an anchor specific enough to grep for
(a class, method or field name), so there are no UNCLEAR verdicts this pass.

**Five most valuable NOT BUILT rows, my judgement:**

1. **`pawns_settle_area` / `lord_create` / `lord_add_pawns` / `lord_set_point`** —
   the roster's own headline answer to "can pawns live happily on a map around a
   territory": `LordMaker.MakeNewLord` + `LordJob_DefendPoint` is a ~10-line tool and
   nothing built today creates or manipulates a `Lord` at all (only
   `jawa/social_cancel` clears one, and only two specific kinds).
2. **`pawns_patrol_route` / `lord_travel_to`** — the roster calls this "the single
   highest-value custom class on the whole roster," LOW effort (one `LordJob`
   subclass, no Harmony), and it is still completely absent.
3. **`settlement_generate` / `settlement_populate`** — turns an empty rect into an
   inhabited base (`BaseGen` or `MapGenUtility.GeneratePawns`); nothing spawns a
   populated settlement on a live map today.
4. **`run_basegen_symbol` / `run_genstep`** — programmatic ruins/rooms/scatterers
   into an arbitrary rect on a live map; `BaseGen`/`GenStep` never appear as an
   exposed tool, only in comments.
5. **`set_pawn_gender`** — the single missing field in an otherwise essentially
   complete pawn-editing suite (23 of 24 rows in §3 are BUILT). `gender` is read in
   `jawa/pawn_get` (`p.gender.ToString()`) and never written anywhere. Trivial fix,
   closes the section.

---

## 0. Pawns living on a map / lords / settlements

| roster row | verdict | built tool(s) |
|---|---|---|
| `pawns_settle_area` — spawn pawns under one lord that live/work/defend a radius forever | NOT BUILT | none — no `LordMaker.MakeNewLord` call anywhere in source |
| `lord_create` — generic: any LordJob by class name + ctor args | NOT BUILT | none |
| `lord_add_pawns` — move spawned pawns into an existing lord | NOT BUILT | none |
| `lord_list` / `lord_destroy` — inspect or clear lords | PARTIAL | `jawa/social_cancel` — clears gathering/ritual lords only (matched by `LordJob_VoluntarilyJoinable` or class name containing "Ritual"); no listing of arbitrary lords, no arbitrary destroy |
| `lord_set_point` — move a defend-point lord's territory centre live | NOT BUILT | none |
| `settlement_generate` — full BaseGen settlement (buildings + inhabitants + lord) into a rect | NOT BUILT | none — no `BaseGen` usage anywhere |
| `settlement_populate` — inhabitants only, joined to a lord | NOT BUILT | none — no `MapGenUtility.GeneratePawns` |
| `pawn_set_guest_status` — guest / prisoner / slave | NOT BUILT | none — no `Pawn_GuestTracker`/`SetGuestStatus` reference in source |
| `pawn_force_job` — one-shot order, ANY JobDef | BUILT | `jawa/ordered_job` — "Issue ANY JobDef through Pawn_JobTracker.TryTakeOrderedJob... opened up to arbitrary jobs (hauling, cleaning, sowing, using a bill giver, ...)." Supersedes the roster's own PARTIAL note (which only knew about `jawa/order_pawn`, Goto-only) |
| `pawn_mental_state` — panic / berserk / wander | BUILT | `jawa/pawn_mental` — "Force or end a mental state." |
| `wildlife_spawn` — herd at a cell, or force ambient density | PARTIAL | `jawa/spawn_pawn` / `jawa/spawn_batch` place animal things at a cell; no `wildAnimalSpawner` ambient-density control anywhere in source |

## 1. Map terrain, grids and substructure

| roster row | verdict | built tool(s) |
|---|---|---|
| `get_terrain_layers` — all 5 layers + colour at a cell | BUILT | `jawa/get_terrain_layers` |
| `set_under_terrain` — terrain beneath a floor | BUILT | `jawa/set_terrain_layer` (`layer=under`) |
| `remove_top_layer` — strip floor → under → foundation | BUILT | `jawa/set_terrain_layer` (`layer=removeTop`) — confirmed present with `doLeavings` param |
| `set_substructure_batch` — paint substructure over a rect | BUILT | `jawa/set_substructure_batch` (`action=set`) |
| `remove_substructure` — strip the foundation layer | BUILT | `jawa/set_substructure_batch` (`action=remove`) |
| `substructure_refresh` — re-dirty engines/overlay after bulk paint | BUILT | `jawa/map_commit` |
| `get_gravship_substructure` — connected/valid cell sets + support budget | NOT BUILT | none — no `Building_GravEngine`, `ValidSubstructure`, `AllConnectedSubstructure` reference anywhere |
| `set_temp_terrain` — Odyssey temporary terrain | BUILT | `jawa/set_terrain_layer` (`layer=temp`) |
| `set_terrain_color` — recolour floors | BUILT | `jawa/set_terrain_layer` (`layer=color`) |
| `unfog_rect` / `unfog_all` / `refog_rect` | BUILT | `jawa/set_fog` |
| `set_snow` / `add_snow_radial` | BUILT | `jawa/set_weather_buildup` (`kind=snow`) |
| `set_sand` / `add_sand_radial` — Odyssey dune painting | BUILT | `jawa/set_weather_buildup` (`kind=sand`) |
| `set_deep_resource` — buried ore for drills | BUILT | `jawa/set_deep_resource` |
| `set_pollution` — Biotech `PollutionGrid.SetPolluted` (map-level) | NOT BUILT | none — the only pollution setter in source is `jawa/world_tile_set`, which writes the **planet-tile** pollution scalar, a different system entirely; no `PollutionGrid` reference anywhere |
| `add_gas` / `clear_gas` — tox / smoke / rotstink / deadlife | BUILT | `jawa/set_gas` |
| `create_zone` / `paint_zone_cells` / `delete_zone` | BUILT | `jawa/map_zones` |
| `paint_area` / `create_allowed_area` | BUILT | `jawa/paint_area` (paints home/roof/noroof/snow/pollution or a named Allowed area) **+** `jawa/new_allowed_area` (`AreaManager.TryMakeNewAllowed`) — new since the roster's PARTIAL note; together this is full coverage |
| `run_genstep` — any GenStep subclass on a live map | NOT BUILT | none — `GenStep` appears only in a code comment in `JawaBenchMapTools.cs` |
| `scatter_at` — force one scatterer at a cell | NOT BUILT | none |
| `run_basegen_symbol` — ruins/rooms into a rect | NOT BUILT | none — no `BaseGen` reference |
| `flood_fill` — region select by predicate | NOT BUILT | `map.floodFiller` is used, but only internally inside `jawa/connect_cells`' pathing — not exposed as a general-purpose region-select tool |
| `drop_roof` — collapse + crush damage | PARTIAL | `jawa/set_roof_batch` removes roof cleanly; no `RoofCollapserImmediate.DropRoofInCells` crush-damage path anywhere in source |
| `fix_floating_roofs` — remove unsupported roof after demolition | NOT BUILT | none — no `RoofCollapseCellsFinder` reference |

## 2. Weather, incidents, raids, storyteller

| roster row | verdict | built tool(s) |
|---|---|---|
| `get_threat_points` — storyteller's threat sizing + wealth split | BUILT | `jawa/weather_get` |
| `forecast_incidents` — dry-run N days of the storyteller's plan | NOT BUILT | none — no `StorytellerUtility.DebugGetFutureIncidents` reference; `jawa/incident_parms_preview` only resolves parms for ONE named incident, not a multi-day forecast |
| `list_weather` / `get_weather` | BUILT | `jawa/weather_get` |
| `set_weather` **PLAYER** | BUILT | `jawa/weather_set` |
| `lock_weather` **PLAYER** — the only durable weather control | BUILT | `jawa/weather_set` (`lockWeather=true` registers `GameCondition_ForceWeather`; `unlock=true` removes it) |
| `list_game_conditions` — 38 defs + active | BUILT | `jawa/weather_get` (`listDefs=true`) |
| `start_game_condition` **PLAYER** | BUILT | `jawa/game_condition` |
| `end_game_condition` **PLAYER** | BUILT | `jawa/game_condition` |
| `list_raid_options` — strategies × arrival modes | BUILT | `jawa/raid_preview` |
| `preview_raid` — resolve parms without executing | BUILT | `jawa/raid_preview` |
| `fire_raid` **PLAYER** — "every parm: points, faction, strategy, arrival, spawnCenter, kind, count, age restriction, steal/kidnap/flee" | PARTIAL | `jawa/fire_raid` covers points/faction/strategy/arrivalMode/spawnCenter/friendly + dryRun; **no `kind`, `count`, age-restriction or steal/kidnap/flee parameters exist** — downgraded from the roster's own BUILT mark on re-check |
| `fire_incident_full` **PLAYER** — generalise to the full IncidentParms surface | PARTIAL | `jawa/fire_incident` (GM-gated, `#if JAWA_GM_TOOLS`) takes only `incidentDef`, `points`, `faction`, `dryRun` — not generalised |
| `spawn_mech_cluster` **PLAYER** | NOT BUILT | none — no `MechClusterGenerator` reference |
| `get_storyteller` / `set_storyteller` **PLAYER** — def, difficulty, ~50 fields, incident queue | PARTIAL | `jawa/weather_get` reads def/difficulty/threatScale/allowBigThreats; `jawa/difficulty_tune` now **writes** `threatScale`, `allowBigThreats`, `adaptationEffectFactor`, `colonistMoodOffset`, `tradePriceFactorLoss` — a real writer that did not exist at the roster's last pass, but well short of ~50 fields, no storyteller-def switch, no incident-queue view |
| `queue_incident` / `clear_incident_queue` **PLAYER** | PARTIAL | `jawa/incident_schedule` adds to `Storyteller.incidentQueue`; no clear/cancel action exists |
| `get_time` / `get_local_date` / `set_time_speed` | PARTIAL | `jawa/time_clock` (TicksGame/CurTimeSpeed/Paused, read-only) + `jawa/time_date_at` (date/season/quadrum at a location, read-only) cover the reads; no tool sets an arbitrary game speed — `jawa/time_pin_normal_speed` only forces Normal for ~800 ticks |
| `set_ticks_game` **PLAYER** — the only way to force a season/year | BUILT | `jawa/time_set_ticks` |
| `list_letters` / `show_message` / `send_letter_delayed` | PARTIAL | `jawa/send_letter` (GM-gated) sends one letter now; no letter-stack read, no delayed letter, no `Messages.Message` |
| `force_song` / `screen_shake` / `spawn_fleck` **PLAYER** | NOT BUILT | none — no `ForcePlaySong`, `CameraDriver.shaker`, or `FleckMaker` reference (`jawa/sky_glow_set` covers lighting only, a different capability) |

## 3. Deep pawn editing

| roster row | verdict | built tool(s) |
|---|---|---|
| `set_pawn_name` | BUILT | `jawa/set_pawn_identity` |
| `set_pawn_title` | BUILT | `jawa/set_pawn_identity` |
| `set_pawn_backstory` | BUILT | `jawa/set_pawn_backstory` |
| `add_pawn_trait` / `remove_pawn_trait` | BUILT | `jawa/pawn_traits` |
| `set_pawn_skill` — level + passion + xp | BUILT | `jawa/set_pawn_skill` |
| `set_pawn_appearance` | BUILT | `jawa/set_pawn_appearance` |
| `set_pawn_faction` | BUILT | `jawa/set_pawn_faction` |
| `recruit_pawn` — prisoner/guest → player | BUILT | `jawa/set_pawn_faction` |
| `set_pawn_ideo` / `set_pawn_certainty` | BUILT | `jawa/set_pawn_ideo` |
| `assign_ideo_role` | BUILT | `jawa/set_pawn_ideo` |
| `add_pawn_relation` | BUILT | `jawa/pawn_relations` |
| `add_pawn_gene` / `remove_pawn_gene` | BUILT | `jawa/pawn_genes` |
| `give_pawn_equipment` | BUILT | `jawa/pawn_gear` |
| `give_pawn_apparel` | BUILT | `jawa/pawn_gear` |
| `clear_pawn_gear` | BUILT | `jawa/pawn_gear` |
| `add_pawn_inventory` | BUILT | `jawa/pawn_gear` |
| `add_pawn_hediff` / `remove_pawn_hediff` | BUILT | `jawa/pawn_health` |
| `install_bionic` — no RecipeDef needed | BUILT | `jawa/pawn_health` |
| `restore_body_part` | BUILT | `jawa/pawn_health` (1-arg `RestorePart`) **+** `jawa/pawn_restore_part` (new — full `RestorePart(BodyPartRecord, Hediff, bool)` signature) |
| `set_pawn_need` | BUILT | `jawa/pawn_need` |
| `add_pawn_thought` | BUILT | `jawa/pawn_need` (blunt, add-only) **+** `jawa/pawn_memory` (new — full `MemoryThoughtHandler` signature with otherPawn/Precept and clear) |
| `set_pawn_age` | BUILT | `jawa/set_pawn_age` |
| `set_pawn_gender` | NOT BUILT | none — `gender` is read in `jawa/pawn_get` (`p.gender.ToString()`) and never written anywhere in source; the roster's own 2026-08-22 note about this gap is still true today |
| `give_pawn_ability` / `set_pawn_psylink` | BUILT | `jawa/pawn_psychic` |

## 4. Conduits, water and fuel pipes

| roster row | verdict | built tool(s) |
|---|---|---|
| `power_net_info` — nets, gen/consumption/stored, connectivity | NOT BUILT | none — `powerNetManager` is only ever called to trigger a reconnect (inside `jawa/map_commit`), never to read net state out |
| `place_conduit_line` — vanilla conduits along a path | BUILT | `jawa/connect_cells` (default `thing=PowerConduit`) |
| `pipe_net_info` — generic reflective reader over VEF/Rimefeller/DBH | NOT BUILT | none — no `PipeSystem`/`PipeNetManager`/`Rimefeller`/`DubsBadHygiene` reference anywhere in source |
| `place_pipe_line` — lay a modded pipe along a path, any framework | PARTIAL | `jawa/connect_cells` is genuinely def-generic (`thing` parameter accepts any ThingDef, not just PowerConduit), so it CAN lay a modded pipe; but it performs no modded pipe-grid dirty step afterward |
| `pipe_grid_rebuild` — after bulk placement | NOT BUILT | none |

## 5. Lorded pawns walking a patrol route

| roster row | verdict | built tool(s) |
|---|---|---|
| `pawns_patrol_route` — lord walks a closed circuit of waypoints | NOT BUILT | none — needs a custom `LordJob_Patrol`; no `LordJob` creation tool exists at all |
| `pawns_roam_district` — roaming beat, no fixed route | NOT BUILT | none |
| `lord_travel_to` — move a travelling lord's destination live | NOT BUILT | none — no `LordToil_Travel.SetDestination` reference |

## 7. Buildings and construction

| roster row | verdict | built tool(s) |
|---|---|---|
| `build_batch` — god-mode instant build: stuff, rot, faction, style | BUILT | `jawa/build_batch` |
| `build_check` — pre-flight a cell without placing | BUILT | `jawa/build_check` |
| `wipe_cell` — clear what a placement would overwrite, with/without refund | PARTIAL | `jawa/build_batch` has `wipeExisting` (plain `DestroyMode.Vanish`); no refund path, no `WouldWipeAnythingWith` pre-query anywhere in source |
| `set_thing_props` — quality/HP/faction/style on already-spawned things | PARTIAL | `jawa/build_batch` and `jawa/spawn_batch` set quality/HP/faction/stuff, but only **at spawn time**; no tool edits the properties of a thing that is already on the map |
| `place_blueprint_batch` — leave real blueprints for colonists to build | NOT BUILT | none — no `GenConstruct.PlaceBlueprintForBuild` reference |
| `frame_complete` — finish a frame as a colonist would | NOT BUILT | none — no `Frame.CompleteConstruction` reference |
| `minify` / `uninstall` — pop a building into a haulable crate | NOT BUILT | none — no `MinifyUtility` reference |
| `designate_batch` — Mine/Deconstruct/Harvest/Haul/Plan… with no cursor | BUILT | `jawa/designate_batch` |
| `designation_clear` / `designation_query` | BUILT | `jawa/designate_batch` — `action='remove'` and `action='query'` are both first-class actions on the same tool |
| `prefab_capture` — capture a CellRect into a PrefabDef | BUILT | `jawa/prefab_capture` |
| `prefab_place` — stamp a prefab down | BUILT | `jawa/prefab_place` (a new sibling, `jawa/prefab_list`, also lists what is available) |
| `layout_generate` — a whole multi-room complex | NOT BUILT | none — no `LayoutWorker` reference |
| `sketch_spawn` — ruins / monuments | NOT BUILT | none — no `SketchGen` reference |
| `gravship_place` — drop a lifted gravship | NOT BUILT | none — no `GravshipUtility.GenerateGravship` reference |
| `kcsg_place` — place a VE structure layout | NOT BUILT | none — no `KCSG` reference anywhere in source |
| `power_net_query` — net at a cell, gain rate, stored, members | NOT BUILT | none — no `TransmittedPowerNetAt`/`CurrentEnergyGainRate` reference |
| `battery_set` — force-charge / drain | NOT BUILT | none — no `CompPowerBattery` reference |
| `power_reconnect` — flush queued net rebuilds after bulk spawn | BUILT | `jawa/map_commit` (calls `powerNetManager.UpdatePowerNetsAndConnections_First()`) |
