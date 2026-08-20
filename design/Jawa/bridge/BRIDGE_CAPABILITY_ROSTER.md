# The live-bridge capability roster — what is POSSIBLE, for the owner to cull

**Queue item:** `dll-capability-roster-and-cull-a41c02`. Owner, 2026-08-18: *"Produce the
FULL roster of RimWorld functionality we could implement as companion [Tool] methods —
not what is built, what is POSSIBLE — then have the owner select down from it."*
**The roster is the deliverable; the cull is his.**

Every line carries an **exact API anchor read from 1.6 source through RimSage**, not from
memory. Anything unverified is marked UNCERTAIN. Nothing here is built unless it says so.

**What a tool costs, measured during W1–W8 on 2026-08-19:** ~10 minutes to write, and a
**~1 minute** edit → build → deploy → launch → test cycle on the 13-mod list. That is why
this roster is worth culling rather than admiring.

**Already built: 57 tools** — 32 map/pawn/terrain in `JawaBenchTerrainTools.cs`, 25 world
tools in `JawaBenchWorldTools.cs`. Nothing below duplicates those.

Risk key: **low** = read or trivially reversible · **med** = mutates state, reversible by
reload · **high** = irreversible on a live campaign, or can wedge/end the game.
**PLAYER** = acts on the live colony, so it belongs behind the `--gm` build flag.

---

## ⭐ THE HEADLINE ANSWER: pawns that live on the map, happily, around a territory

**YES, and it needs no custom `LordJob`.**

```csharp
LordMaker.MakeNewLord(
    faction,
    new LordJob_DefendPoint(center, wanderRadius, defendRadius,
                            isCaravanSendable: false, addFleeToil: false),
    map, pawns);
```

`LordJob_DefendPoint` builds a state graph with **ONE toil and ZERO transitions** — there
is no trigger that can ever turn it into an assault or an exit. Its toil gives every pawn
`PawnDuty(DutyDefOf.Defend, center)`, and the `Defend` duty runs the
`SatisfyBasicNeedsAndWork` subtree inside `ThinkNode_ForbidOutsideFlagRadius`. So they
**eat, sleep, socialise and do work jobs** near the point, wander within `wanderRadius`,
and shoot only what is hostile to their faction. Make the faction neutral to the player
and that is literally "living there happily, indefinitely".
`addFleeToil:false` stops them running off the map when hurt.

🔴 **Do NOT use `LordJob_DefendBase` for this.** It carries six triggers into
`LordToil_AssaultColony`, including `Trigger_ChanceOnTickInterval(2500, 0.03f)` — it will
turn into a raid **on its own, unprompted**.

🔴 **A duty without a lord is inert.** `ThinkNode_ConditionalHasLordDuty` returns false
when `pawn.GetLord() == null`, so hand-setting `mindState.duty` does nothing. **Do not
expose a `pawn_set_duty` tool** — it would look like it worked and never run.

🔑 **Territory confinement for non-colonists** is `Pawn_MindState.maxDistToSquadFlag` +
`LordToil.FlagLoc` via `ThinkNode_ForbidOutsideFlagRadius` (default 16).
⚠️ UNCERTAIN whether `playerSettings.AreaRestrictionInPawnCurrentMap` constrains a lorded
non-player pawn — no non-player caller was found.

**Populating a settlement on a LIVE map is possible two ways:**
* `BaseGen.globalSettings.map = map; BaseGen.symbolStack.Push("settlement", rect); BaseGen.Generate();`
  — the full thing, buildings + inhabitants + lord. `SymbolResolver_Settlement` uses
  `LordJob_DefendBase` + `PawnGroupKindDefOf.Settlement`, ~1150–1600 points. **HIGH RISK**,
  irreversible, mutates terrain and buildings.
* `MapGenUtility.GeneratePawns(map, rect, faction, lord, PawnGroupKindDefOf.Settlement, …)`
  — inhabitants only, each `lord.AddPawn`ed. Lighter and safer.

| tool | what it does | anchor | risk |
|---|---|---|---|
| `pawns_settle_area` | ⭐ spawn/collect pawns under one lord; they live, work and defend a radius forever | `LordMaker.MakeNewLord` + `LordJob_DefendPoint` | low |
| `lord_create` | generic: any LordJob by class name + ctor args | `LordMaker.MakeNewLord` | med |
| `lord_add_pawns` | move already-spawned pawns into an existing lord | `Lord.AddPawn/AddPawns` | low |
| `lord_list` / `lord_destroy` | inspect or clear lords | `map.lordManager.lords`, `Lord.Destroy()` | low |
| `lord_set_point` | move the territory centre live | `LordToil_DefendPoint.SetDefendPoint` | low |
| `settlement_generate` | full BaseGen settlement into a rect | `BaseGen.symbolStack.Push("settlement", rp)` | **high** |
| `settlement_populate` | inhabitants only, joined to a lord | `MapGenUtility.GeneratePawns` | med |
| `pawn_set_guest_status` | guest / prisoner / slave | `Pawn_GuestTracker.SetGuestStatus` | med |
| `pawn_force_job` | one-shot order | `Pawn.jobs.TryTakeOrderedJob` | med |
| `pawn_mental_state` | panic / berserk / wander | `MentalStateHandler.TryStartMentalState` | med |
| `wildlife_spawn` | herd at a cell, or force ambient density | `map.wildAnimalSpawner.SpawnRandomWildAnimalAt` | low |

72 `LordJob_*` classes ship. Peaceful-settle candidates besides `DefendPoint`:
`SitePawns`, `WanderNest` (Odyssey), `VoidAwakeningWander`, `CreepJoiner`,
`DefendAndExpandHive`, `ManTurrets`, `StructureThreatCluster`.

---

## 1. MAP TERRAIN, GRIDS AND SUBSTRUCTURE

🔑 **SUBSTRUCTURE IS NOT A GRID.** It is a **foundation-layer `TerrainDef`** —
`TerrainDefOf.Substructure`, `isFoundation=true`, `IsSubstructure => HasTag("Substructure")`
— living in `TerrainGrid.foundationGrid`. `Map.substructureGrid` is **only an overlay
drawer**; its sole state-changing method is `MarkDirty()`. All Odyssey-gated.

🔑 **1.6 has FIVE terrain layers, not two**: top · under · **foundation** · **temp**
(ice/mud, with a scheduled-expiry manager) · plus a **colour** grid.

| tool | what it does | anchor | risk |
|---|---|---|---|
| `get_terrain_layers` | all 5 layers + colour at a cell | `TerrainGrid.TopTerrainAt/UnderTerrainAt/FoundationAt/TempTerrainAt/BaseTerrainAt/ColorAt` | low |
| `set_under_terrain` | terrain beneath a floor | `TerrainGrid.SetUnderTerrain` | low |
| `remove_top_layer` | strip floor → under → foundation, one step | `RemoveTopLayer`; guard `CanRemoveTopLayerAt` | med |
| `set_substructure_batch` | ⭐ paint substructure over a rect | `SetFoundation(c, TerrainDefOf.Substructure)` — errors if `underGrid[c] != null` | med |
| `remove_substructure` | strip the foundation layer | `RemoveFoundation`; guard `CanRemoveFoundationAt` | med |
| `substructure_refresh` | re-dirty engines + overlay after bulk paint | `Map.substructureGrid.MarkDirty()` | low |
| `get_gravship_substructure` | connected/valid cell sets + support budget | `Building_GravEngine.ValidSubstructure`, `.AllConnectedSubstructure`, `StatDefOf.SubstructureSupport` | low |
| `set_temp_terrain` | Odyssey temporary terrain | `SetTempTerrain`; `TempTerrainManager.QueueRemoveTerrain(c, tick)` | med |
| `set_terrain_color` | recolour floors (Ideology dye) | `SetTerrainColor(c, ColorDef)` | low |
| `unfog_rect` / `unfog_all` / `refog_rect` | reveal or re-hide | `FogGrid.Unfog/ClearAllFog/FloodUnfogAdjacent/Refog` | low |
| `set_snow` / `add_snow_radial` | depth 0–1 | `SnowGrid.SetDepth/AddDepth`, `WeatherBuildupUtility.AddSnowRadial` | low |
| `set_sand` / `add_sand_radial` | ⭐ **Odyssey dune painting** | `SandGrid.SetDepth/AddDepth`, `AddSandRadial` | low |
| `set_deep_resource` | buried ore for drills | `DeepResourceGrid.SetAt(c, ThingDef, count)` | low |
| `set_pollution` | Biotech-gated | `PollutionGrid.SetPolluted` | low |
| `add_gas` / `clear_gas` | tox / smoke / rotstink / deadlife | `GasGrid.AddGas/SetDirect/ClearCellUnsafe` | med |
| `create_zone` / `paint_zone_cells` / `delete_zone` | stockpile + growing zones | `new Zone_Stockpile(...)`, `ZoneManager.RegisterZone`, `Zone.AddCell` + `CheckContiguous()` | med |
| `paint_area` / `create_allowed_area` | home / no-roof / allowed (max 10) | `Area[IntVec3] = bool`, `AreaManager.TryMakeNewAllowed` | low |
| `run_genstep` | any `GenStep` subclass on a live map | `((GenStep)Activator.CreateInstance(t)).Generate(map, default)` | **high** |
| `scatter_at` | force one scatterer at a cell | `GenStep_Scatterer.ForceScatterAt` | med |
| `run_basegen_symbol` | ruins / rooms into a rect | `BaseGen.symbolStack.Push(symbol, rect)` | **high** |
| `flood_fill` | region select by predicate | `Map.floodFiller.FloodFill` — ⛔ not reentrant | low |
| `drop_roof` | collapse + crush damage | `RoofCollapserImmediate.DropRoofInCells` | **high** |
| `fix_floating_roofs` | remove unsupported roof after demolition | `RoofCollapseCellsFinder.CheckAndRemoveCollpsingRoofs` (typo is real) | med |

⚠️ Most `GenStep_*` read `MapGenerator.Elevation/Fertility/Caves` and `PlayerStartSpot`,
which are **null/invalid outside generation** — expect nulls or silent no-ops. UNCERTAIN
which subset is safe post-generation; needs a quicktest.
⛔ `TerrainGrid.RemoveGravshipTerrainUnsafe` and `RoofGrid.RemoveRoofUnsafe` skip all
notifications — **do not expose**.

---

## 2. WEATHER, INCIDENTS, RAIDS, STORYTELLER

🔴 **`TransitionTo` does not hold.** `WeatherDecider` rolls a new weather once
`curWeatherAge > curWeatherDuration`. The only durable lock is a
`GameCondition_ForceWeather`; `WeatherDecider.ForcedWeather` scans active conditions and wins.
🔴 **No `EndNow()` on a condition.** Safe early end is `cond.Duration = cond.TicksPassed`
(the setter clears `permanent`), then it expires next tick.
🔴 **Full-control raids are real:** `IncidentWorker_RaidEnemy` auto-resolves faction /
strategy / arrival **only when they are null**, so every field is overridable.
⛔ **`Planetkiller` ends the game.** Hard-block it.

Counts: 24 `WeatherDef` · 38 `GameConditionDef` · 11 `RaidStrategyDef` ·
13 `PawnsArrivalModeDef` · 131 `IncidentDef` · 4 `StorytellerDef`.

| tool | what it does | anchor | risk |
|---|---|---|---|
| `get_threat_points` | ⭐ what the storyteller thinks you are worth + wealth split | `StorytellerUtility.DefaultThreatPointsNow`, `map.wealthWatcher` | low |
| `forecast_incidents` | ⭐ dry-run N days of the storyteller's plan, no game time spent | `StorytellerUtility.DebugGetFutureIncidents` | low |
| `list_weather` / `get_weather` | defs, current, age, rain/snow/wind rates | `Map.weatherManager` | low |
| `set_weather` **PLAYER** | transition now (reverts in ≤ duration) | `weatherManager.TransitionTo` | low |
| `lock_weather` **PLAYER** | ⭐ the only durable weather control | `GameConditionMaker.MakeConditionPermanent(WeatherController)` | med |
| `list_game_conditions` | 38 defs + active, ticksLeft, permanent | `GameConditionManager.ActiveConditions` | low |
| `start_game_condition` **PLAYER** | any def, map- or world-scoped | `GameConditionMaker.MakeCondition` + `RegisterCondition` | med |
| `end_game_condition` **PLAYER** | end early | `Duration = TicksPassed` | low |
| `list_raid_options` | strategies × arrival modes, `CanUseWith`-filtered | `RaidStrategyDef.Worker.CanUseWith` | low |
| `preview_raid` | resolve parms without executing | `Worker.CanFireNow` + `DefaultParmsNow` | low |
| `fire_raid` **PLAYER** | ⭐ every parm: points, faction, strategy, arrival, spawnCenter, kind, count, age restriction, steal/kidnap/flee | `new IncidentParms{…}; IncidentDefOf.RaidEnemy.Worker.TryExecute` | **high** |
| `fire_incident_full` **PLAYER** | generalises the existing `fire_incident` to the whole IncidentParms surface | `incidentDef.Worker.TryExecute` | **high** |
| `spawn_mech_cluster` **PLAYER** | sketch to a point value | `MechClusterGenerator.GenerateClusterSketch` | high |
| `get_storyteller` / `set_storyteller` **PLAYER** | def, difficulty, ~50 fields, incident queue | `Find.Storyteller`, `Notify_DefChanged()` | med |
| `queue_incident` / `clear_incident_queue` **PLAYER** | schedule or suppress | `Find.Storyteller.incidentQueue` | med |
| `get_time` / `get_local_date` / `set_time_speed` | clock, season, quadrum | `Find.TickManager`, `GenLocalDate` | low |
| `set_ticks_game` **PLAYER** | the ONLY way to force a season/year | `DebugSetTicksGame` | **high** — skips all ticking; growth/rot/ages desync |
| `list_letters` / `show_message` / `send_letter_delayed` | | `Find.LetterStack`, `Messages.Message`, `LetterMaker` | low |
| `force_song` / `screen_shake` / `spawn_fleck` **PLAYER** | audio-visual | `Find.MusicManagerPlay.ForcePlaySong`, `CameraDriver.shaker.DoShake`, `FleckMaker` | low |

⚠️ Full storyteller suppression is not one flag. The clean lever is
`difficulty.threatScale` + `allowBigThreats=false`.
⚠️ `AlertsReadout.activeAlerts` is **private** — `list_alerts` needs reflection. UNCERTAIN.

