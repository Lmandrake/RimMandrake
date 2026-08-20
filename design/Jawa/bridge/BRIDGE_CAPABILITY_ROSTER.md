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


---

## 3. DEEP PAWN EDITING

🔴 **"Notes" DO NOT EXIST — NOT FOUND, and this is a definite negative, not a gap in the
search.** There is no free-text note field on `Pawn` or any `Pawn_*Tracker` in 1.6/Odyssey.
`Pawn` does not implement `IRenameable`; there is no `Dialog_Note`. `Pawn_RecordsTracker`
is a `DefMap<RecordDef,float>` — numeric and RecordDef-keyed only.
**The only writable free text on a pawn is `pawn.story.title`** (the custom title after the
name), which is unvalidated when set from code. The other option is
`TaleRecorder.RecordTale(TaleDef, args).customLabel` — free text, but it lives on a *Tale*,
not on the pawn. ⇒ If the owner wants per-pawn notes we must **build the storage
ourselves** (a `GameComponent` keyed by pawn id); nothing in the game will carry it.

| tool | what it does | anchor | risk |
|---|---|---|---|
| `set_pawn_name` | first / nick / last, or single | `pawn.Name = new NameTriple(f,n,l)` — props are get-only, build a new object. Check `name.IsValid` | low |
| `set_pawn_title` | ⭐ the only free text on a pawn | `pawn.story.Title` (setter drops a value equal to the default) | low |
| `set_pawn_backstory` | childhood / adulthood | `pawn.story.Childhood/Adulthood = BackstoryDef` | **med** |
| `add_pawn_trait` / `remove_pawn_trait` | | `story.traits.GainTrait(new Trait(def,degree,forced))` / `RemoveTrait` | low |
| `set_pawn_skill` | level + passion + xp | `skills.GetSkill(def).Level / .passion / .xpSinceLastLevel` | med |
| `set_pawn_appearance` | head, body, hair, beard, fur, tattoos, hair + skin colour | `story.headType/bodyType/hairDef/furDef/HairColor/skinColorOverride`, `style.beardDef/FaceTattoo/BodyTattoo` | low |
| `set_pawn_faction` | | `pawn.SetFaction(faction, recruiter)` | **med** |
| `recruit_pawn` | prisoner/guest → player, properly | `RecruitUtility.Recruit(pawn, faction, recruiter)` | low |
| `set_pawn_ideo` / `set_pawn_certainty` | | `pawn.ideo.SetIdeo(ideo)`; certainty via `OffsetCertainty/Reassure` | med |
| `assign_ideo_role` | | `Precept_Role.Assign(pawn, addThoughts)` / `Unassign` | med |
| `add_pawn_relation` | | `relations.AddDirectRelation(def, other)` | low |
| `add_pawn_gene` / `remove_pawn_gene` | | `pawn.genes.AddGene(GeneDef, xenogene)` / `RemoveGene` | low |
| `give_pawn_equipment` | | `ThingMaker.MakeThing` + `CompQuality.SetQuality` → `equipment.AddEquipment` | med |
| `give_pawn_apparel` | | `PawnApparelGenerator.GenerateApparelOfDefFor(pawn, def)` → `apparel.Wear(...)` | low |
| `clear_pawn_gear` | | `equipment.DestroyAllEquipment()`, `apparel.DestroyAll()`, `inventory.DestroyAll()` | low |
| `add_pawn_inventory` | | `inventory.innerContainer.TryAddOrTransfer` | low |
| `add_pawn_hediff` / `remove_pawn_hediff` | | `health.AddHediff(def, part, dinfo, result)` / `RemoveHediff` | med |
| `install_bionic` | ⭐ no RecipeDef needed | `health.RestorePart(part); health.AddHediff(bionicDef, part)` | med |
| `restore_body_part` | | `health.RestorePart(part)` | **high** |
| `set_pawn_need` | | `needs.TryGetNeed(def).CurLevel` | low |
| `add_pawn_thought` | | `needs.mood.thoughts.memories.TryGainMemory(def, otherPawn, sourcePrecept)` | low |
| `set_pawn_age` | | `ageTracker.DebugSetAge(ticks)` — 1 yr = 3,600,000 | **high** |
| `set_pawn_gender` | | `pawn.gender` — plain field | med |
| `give_pawn_ability` / `set_pawn_psylink` | | `abilities.GainAbility(def)`; `pawn.ChangePsylinkLevel(offset, sendLetter)` | med |

### 🔴 The refresh and silent-failure traps — these are what make pawn editing dangerous

* **`set_pawn_backstory` refreshes NOTHING for you.** The setters only null
  `backstoriesCache`. You must call `pawn.Notify_DisabledWorkTypesChanged()`,
  `pawn.skills.Notify_SkillDisablesChanged()`, `pawn.skills.DirtyAptitudes()` and
  `MeditationFocusTypeAvailabilityCache.ClearFor(pawn)`. **The game's own debug tool only
  does the last one.**
* **`GainTrait` does NOT check conflicts, and there is no trait cap in `TraitSet`.** We must
  check `TraitDef.ConflictsWith(TraitDef)` (conflictingTraits + exclusionTags) and
  `BackstoryDef.DisallowsTrait(def, degree)` ourselves. A duplicate def logs a warning and
  silently does not add.
* **`SkillRecord.Level` read-back ≠ what you wrote** — the getter returns `GetLevel()`
  *including aptitudes*. Verify against `levelInt` / `GetLevel(false)`. And the setter does
  **not** reset `xpSinceLastLevel`, so a pawn can insta-level after a write.
* **`equipment.AddEquipment` `Log.Error`s and does nothing if a Primary already exists.**
  Call `MakeRoomFor(eq)` first, or the tool reports success having changed nothing.
* **Appearance changes do not dirty the renderer.** Call
  `pawn.Drawer.renderer.SetAllGraphicsDirty()` (or `style.Notify_StyleItemChanged()`).
* **`health.RestorePart` is RECURSIVE into child parts**, wipes their hediffs, and does not
  drop the bionic it removed. Destructive and silent.
* **`ChangePsylinkLevel` 0 → N needs TWO calls** — the first creates the hediff at level 1
  and returns. Each level grants a **random** psycast.
* **`SetIdeo` randomises certainty**, unclaims ideo-forbidden beds, and may strip spouse or
  bond relations and send a letter. It is not a quiet field write.
* ✅ **Self-refreshing and safe:** `GainTrait`/`RemoveTrait`, `AddGene`/`RemoveGene`,
  `apparel.Wear`, `pawn.SetFaction` (handles lord loss, jobs, drafter, guest status,
  mapPawns, needs, relations, colonist bar, surgery bills).
* ⚠️ Nothing guards direct appearance assignment — off-gender head types, gene-requiring
  heads and an adult body on a child all "work". Child body is forced only at load.

---

## 4. CONDUITS, WATER AND FUEL PIPES

Vanilla RimWorld has **power conduits only**. Everything else is modded. Measured against
the owner's real 578-mod list, there are exactly **three resource-network runtimes active**:

| framework | packageId | assembly | manager type |
|---|---|---|---|
| **VEF PipeSystem** | `oskarpotocki.vanillafactionsexpanded.core` | `…\2023507013\1.6\Assemblies\PipeSystem.dll` | `PipeSystem.PipeNetManager` |
| **Rimefeller** (oil/fuel) | `dubwise.rimefeller` | `…\1321849735\1.6\Assemblies\Rimefeller.dll` | `Rimefeller.MapComponent_Rimefeller` |
| **Dubs Bad Hygiene Lite** | `dubwise.dubsbadhygiene.lite` | `…\2570319432\1.6\Assemblies\BadHygiene.dll` | `DubsBadHygiene.MapComponent_Hygiene` |

Consumers riding on VEF PipeSystem: Vanilla Chemfuel Expanded, Vanilla Helixien Gas
Expanded, Reel's Turret Pipeline. `PipeSystem.PipeNetDef`, `Building_Pipe` and
`Building_PipeValve` are **CONFIRMED public** — they appear as XML `<thingClass>` and def
root nodes in those mods' Defs.

🔴 **DBH is the LITE package and plumbing is behind a runtime flag.** The DLL carries
`DBHLiteMode`, `LiteMode`, `Plumbing_Active` and a check on `Dubwise.DubsBadHygiene.Plumbing`.
**Water pipes may be disabled in this install even though the types load.** Verify
`Plumbing_Active` at runtime before shipping any water tool. The full DBH
(`dubwise.dubsbadhygiene`, 836308268) is present but **INACTIVE**.

📌 `flangopink.metalpipe` / `metalpipehorseshoe` are **decorative textures, not networks**.
No Project RimFactory, no SRTS.

| tool | what it does | anchor | risk |
|---|---|---|---|
| `power_net_info` | vanilla: nets, gen/consumption/stored, connectivity | `Map.powerNetManager`, `PowerNet`, `CompPower` | low |
| `place_conduit_line` | vanilla conduits along a path | `GenSpawn.Spawn(ThingDefOf.PowerConduit, …)` | low |
| `pipe_net_info` | ⭐ generic reflective reader over all three frameworks | `map.GetComponent<PipeSystem.PipeNetManager>()` etc. | med |
| `place_pipe_line` | lay a modded pipe along a path, any framework | `Building_Pipe` via `GenSpawn.Spawn`, then dirty the grid | med |
| `pipe_grid_rebuild` | after bulk placement | `Rimefeller.RebuildPipeGrid` / `DirtyAllPipeGrids`; DBH `DirtyPipeGrid` | low |

⚠️ **UNCERTAIN and must be settled before writing these:** whether the correct handle is
`map.GetComponent<PipeSystem.PipeNetManager>()` or the static `CachedPipeNetManager`, and
whether `MapComponent_Rimefeller` is `public`. The type NAMES are read from the binaries;
the IL was not.
🔑 **A `strings` caveat that would have misled us:** plain `strings` shows ZERO standalone
`PipeNetManager` / `PipeNet` / `CompResource` lines — only `CachedPipeNetManager`,
`get_PipeNetManager`, `<PipeNetManager>k__BackingField`. That is .NET `#Strings` heap
**suffix compression**, not absence. Raw byte counts: `PipeNetManager` 4, `PipeNet` 14,
`CompResource` 11. **Absent from `strings` is not absent from the assembly.**

---

## 5. ⭐ CAN LORDED PAWNS WALK A PATROL ROUTE? — owner's question, 2026-08-19

**YES, BUT only by writing our own `LordJob`. Nothing shipped patrols a route.**
Every piece exists; none of them is assembled that way in the base game.

**What ships and is NOT what we want:**
* `CompSentryDrone` (Odyssey) is the only thing actually named "patrol" — and it is **not
  lord-driven at all.** It is a `ThingComp` doing a *random room-to-room walk*:
  `GetNextPatrolDest()` picks a random cell in a random adjacent room, avoids
  `lastPatrolDest`, 10% chance to backtrack. No waypoint list, no ordering. Its
  `JobGiver_SentryPatrol` hard-checks `comp.Mode`, so it is useless without forcing the
  comp onto the pawn's ThingDef.
* Mechanoids reporting "Patrolling." are **cosmetic** — `JobGiver_WanderColony` with a
  `<reportStringOverride>` in `Mechanoid.xml`.

**`PawnDuty` has NO `List<IntVec3>`.** The ceiling is three focus slots — `focus`,
`focusSecond`, `focusThird` — which `JobGiver_GotoTravelDestination` switches between via
`destinationFocusIndex`. So a route cannot be expressed as a duty; it has to be expressed
as a **graph of toils**.

**The two facts that make it easy:**
1. `LordToil_Travel.LordToilTick()` already fires `lord.ReceiveMemo("TravelArrived")` every
   205 ticks once all pawns are within `AllArrivedCheckRadius` (virtual, 10f) and can reach.
   `LordJob_TravelAndExit` is the shipped two-node example.
   ⚠️ **`Trigger_PawnArrivedNearDestination` does not exist** — the mechanism is that memo,
   caught by `new Trigger_Memo("TravelArrived")`.
2. **`StateGraph` has no acyclic constraint.** `ErrorCheck()` only complains about
   *unregistered* toils, never about cycles. **A ring of travel toils is legal.**

```csharp
public class LordJob_Patrol : LordJob {
    private List<IntVec3> waypoints;            // ExposeData: Scribe_Collections.Look
    public override StateGraph CreateGraph() {
        var g = new StateGraph();
        var toils = waypoints.Select(w => new LordToil_Travel(w)).ToList();
        g.StartingToil = toils[0];
        for (int i = 1; i < toils.Count; i++) g.AddToil(toils[i]);
        for (int i = 0; i < toils.Count; i++)                     // ring: i -> (i+1) % N
            g.AddTransition(new Transition(toils[i], toils[(i + 1) % toils.Count])
                { triggers = { new Trigger_Memo("TravelArrived") } });
        return g;
    }
}
```

**Three real gotchas:**
1. **`LordToil_Travel` waits for the WHOLE GROUP** — all pawns within 10f and all reachable.
   Fine for a solo guard; for a squad **one blocked pawn stalls the circuit forever**.
   Override `AllArrivedCheckRadius` or put a `Trigger_TicksPassed` escape on each leg.
2. **`DutyDefOf.TravelOrLeave` carries leave-the-map behaviour.** For a perimeter guard,
   author our own `DutyDef` (XML: `ThinkNode_Priority` → `JobGiver_GotoTravelDestination`
   + `JobGiver_WanderNearDutyLocation`) and override `LordToil_Travel.UpdateAllDuties()`,
   **or the pawn walks off the map.**
3. The ring's closing transition has different source and target, so `canMoveToSameState`
   stays false. Only a single-waypoint "patrol" would need it true.

⚠️ **UNCERTAIN — a cyclic StateGraph is untested in game.** The code path reads clean and
nothing forbids it, but **no shipped `LordJob` contains a cycle**, so this is a hypothesis
until a quicktest runs it. That test costs ~1 minute on the minimal list.

📌 **Queued goto jobs are NOT a patrol.** `TryTakeOrderedJob(job, tag, requestQueueing:true)`
does beat the lord duty — `ThinkNode_QueuedJob` sits at line 89 of `Humanlike.xml` and the
`LordDuty` subtree at ~116 — but the queue **drains and never repeats**, and any
interruption above line 89 (combat, needs, mental state) clears it. One-shot route, not a beat.

📌 **A roaming beat with no fixed route is easier and IS shipped-adjacent:**
`LordToil_VoidAwakeningWander.LordToilTick()` reassigns each pawn a fresh
`PawnDuty(DutyDefOf.VoidAwakeningWander, newSpot)` every 1800 ticks within 50 cells. Copy
that pattern for "wander this district", no custom graph needed.

| tool | what it does | anchor | risk |
|---|---|---|---|
| `pawns_patrol_route` | ⭐ lord walks a closed circuit of waypoints | **our own `LordJob_Patrol`** + `Trigger_Memo("TravelArrived")` | med — needs the cycle proven |
| `pawns_roam_district` | roaming beat, no fixed route, reassigned periodically | `LordToil` reassigning `PawnDuty` on a tick, per `VoidAwakeningWander` | low |
| `lord_travel_to` | move a travelling lord's destination live | `LordToil_Travel.SetDestination` (public) | low |

**Effort: LOW.** One `LordJob`, optionally one `DutyDef` in XML. No Harmony, no new Trigger
class. This is the single highest-value custom class on the whole roster.

---

## 6. ALREADY BUILT — do not re-roster these

**Roofs are DONE and more complete than they look.** `jawa/set_roof_batch` /
`get_roof_batch` resolve **any** `RoofDef` by name through
`DefDatabase<RoofDef>.GetNamedSilentFail` — not just the three named in the docstring — and
the literal `None` / `Clear` removes a roof (open sky). Every cell is read back off
`roofGrid` after writing and reported as `cellsFailedVerify`, so it cannot claim a success
it did not get. Six RoofDefs live on the owner's stack:

| def | thick? | natural? | |
|---|---|---|---|
| `RoofConstructed` | thin | no | player-built |
| `RoofRockThin` | thin | yes | |
| `RoofRockThick` | **THICK** | yes | drop-pod-proof; leaves `CollapsedRocks` |
| `VoidmetalRoof` | **THICK** | yes | Anomaly |
| `VGE_VacBarrierRoof` | thin | no | modded |
| `BMT_RockRoofStable` | **THICK** | yes | modded |

⚠️ `isThickRoof` lives under the `fields` sub-object in the def dump, not at top level —
easy to read as absent and conclude the dump does not carry it. It does.

Also already built: terrain painting, plants, thing spawning (incl. vehicles), destroy,
damage, pawn spawn/style/xenotype/rotation, faction relations, quests, letters, incidents,
and the whole 25-tool world surface.
