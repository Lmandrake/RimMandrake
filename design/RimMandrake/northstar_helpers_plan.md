# Northstar situational helpers — plan (not built)

Status: PLAN, 2026-10-01. Nothing here is built. Every bridge shape below is quoted from the
companion C# (`src/RimMandrake/bridgetools/JawaBench.BridgeTools/*.cs`) or from a recorded
run (`Transient/modcheck/*_summary.json`). Anything not read from one of those is marked
**UNMEASURED**.

Problem (owner): northstar/modcheck scripts fail for reasons that have nothing to do with the
mod: bad startup (map not cleared), or the game left running long enough that raids,
predators, fires and letters take over. The report that comes back is "everyone is dead and
I don't know why" or "all the meat disappeared". The goal is fewer "needs a human present"
tests, through three things: **detectors** a script can call, **helpers** a script can call
again and again to get through, and a **tick budget enforced in Python**, with a screenshot
taken on every surprise.

## 1. Evidence: real failure modes in past runs

| # | what happened | where | what it teaches |
|---|---|---|---|
| E1 | **7 colonists died during one modcheck session**, at ticks 302, 302, 903, 1504, 2698, 3298, 3298. There was also an "Insulting spree", two "Roof collapse" letters and a birth. The component's FAIL message talks only about a missing mod letter. | `Transient/modcheck/ShipMemory_summary.json`, component `reveals_on_stockpile`, evidence `jawa/letter_list` (21 letters) | This is exactly "everyone is dead and I don't know why". The evidence **was captured but never read**: nothing looked at `defName == "Death"`. The deaths come about 601 ticks apart, which matches a 600-tick cadence, so the cause is probably mechanical rather than random. The real cause is **UNMEASURED**. The letter stack is shared across the suites run on one map (`arrivalTick` 0 to 3298), so a detector must diff by `arrivalTick > chain_start_tick`, not read the whole stack. |
| E2 | Colonist `Justice` (Human966) carried 6 **Burn** hediffs, Moving 0.73, during an ion-weapon suite that deals no fire damage | `Transient/modcheck/JawaIonWeapons_summary.json`, `default_severity_matches_xml_rate`, `jawa/list_pawns` row | An environmental fire hurt a bystander, and nothing flagged it. A colonist health detector would have. |
| E3 | `Human53729 not found in jawa/list_pawns` and `Human53736 not found`. The list read `"50 pawn(s), 3 beyond the limit"`. | same file, `buildup_downs_alive_no_injury` / `default_severity_matches_xml_rate` | This is not a vanished pawn. It is **truncation at limit=50**: 46 factionless pawns (accumulated test litter or wildlife) pushed the target past the cap. A "pawn disappeared" detector has to rule this out before it raises the alarm. `suite._pawn_pos` uses `limit=500`, but suites' own `bridge_call`s do not. |
| E4 | A scratch map raided within seconds by the tile's resident faction ("Totharth Mechhive"). The owner first read it as an attack on his real campaign. | `infrastructure/state/handoffs/FOUNDRY_REBOOT_HANDOFF_202609251942.md` lines 10-18 | Raids are not only storyteller rolls. The map's parent and its neighbours matter. `rimworld/list_letters` carries a `mapId`, which is how the attack was attributed. |
| E5 | An unpaused test after hostile droids spawned: 2 colonists dead and several downed about 2 in-game hours later | `skills/rimbridge/SKILL.md` §4b (2026-08-12) | The combination of calls is the hazard. The defence is a pre-unpause census of hostiles. |
| E6 | `order_pawn` unpaused by default and ran the clock from tick 1035 to 19634 | `skills/rimbridge/references/traps.md` (order_pawn bullet) | Time passes behind a verb that does not look like a wait. The budget must be **measured off `ticksGame`**, not counted from `wait_ticks` calls. |
| E7 | A 90k-tick blind run in which colonists minified and hauled off two gravship fuel tanks | `skills/rimbridge/SKILL.md` §4b | This is the "meat disappeared" shape: colony AI hauls, eats and reorganises anything that is not forbidden. |
| E8 | A fresh quicktest map seeds wildlife and sometimes wandering or joining humans near the start | `.claude/skills/rimworld-debug-testing/SKILL.md` (~l.190) | The map is never bland by default. It has to be made bland. |
| E9 | `step_game_ticks` silently truncates (600-2800 ticks per call) while reporting success | `src/RimMandrake/Utils/modcheck/suite.py` `wait_ticks` docstring | This is already handled: `wait_ticks` chunks at 2000 and verifies `ticksGame`. That loop is the natural place for the detector sweep. |
| E10 | Raid census immediately after `fire_raid` reads 0; 19 pawns arrive by +300 ticks | `traps.md` §"A raid census taken immediately…" | Threats arrive in flight. One sweep after a chunk can miss a raid that lands mid-chunk, so sweeps must repeat at every chunk boundary. |
| E11 | `step_game_ticks` runs turret AI and explosions under a stepped pause | `traps.md` (turret notes) | "Paused" is not "inert". Detectors must run after stepped ticks too, not only after real unpauses. |

**Scale of ticks requested.** `wait_ticks` literals across all `validation.py` add up to about 130k
requested ticks. One of them is `Antiquities` `wait_ticks(95000)`, about 1.6 in-game days, which
is ample time for raids, starvation and rot. The other 30 calls are each 5000 ticks or fewer.

**What modcheck does NOT do today** (grep of `src/**/*.py`): no suite or the runner calls
`jawa/debug_settings`, `jawa/incident_queue_clear`, `jawa/storyteller_swap`, `jawa/destroy_bulk` or
`jawa/alerts_list` for hygiene. Only `prove_venomvine_flyer.py` calls `destroy_bulk`, and only
`EmpirePursuit` and `ShipMemory` read `letter_list`, both as the subject of the test. **No run
is ever made bland, and no run ever looks at what else happened.**

## 2. Bridge tool inventory (detectors and helpers)

Every name below was read from a `[Tool("jawa/...")]` attribute. `rimworld/*` tools are the core
RimBridgeServer tools, named in `skills/rimbridge/SKILL.md`.

### Read (detector inputs)

| tool | params | returns (real keys) | traps |
|---|---|---|---|
| `jawa/list_pawns` | `rect`, `faction` (`player`/`hostile`/`nonplayer`/defName), `includeHealth`, `includeCorpses`, `limit=500` | `success, count, message, ticksGame, pawns[]`. Each row has `id, name, kind, kindDef, def, xenotype, faction, factionName, isPlayer, hostile, x, z, spawned, dead, downed, stunned, stunTicksLeft, fleshType, isMechanoid, isFlesh, intelligence, bodySize`, and with health also `health.{hediffs[{def,label,severity,part,partLabel}], capacities{}, capacityErrors, painTotal, bleedRate}` | 🔴 health is NESTED (`row["health"]["hediffs"]`); the flat key reads empty for every pawn. Read `message` for "N beyond the limit" (E3). No `mentalState`, no `curJob` field. **Faction is `None` for wild animals** (46 rows in E3). |
| `jawa/letter_list` | none | `success, count, letters[{label:{RawText,…}, defName, arrivalTick, lookTargets}]` | `label` is a TaggedString object, so read `label["RawText"]`. `defName` is the LetterDef (`Death`, `NegativeEvent`, `ThreatBig`/`ThreatSmall` **UNMEASURED** in our runs, `NeutralEvent`, `PositiveEvent`). It carries no mapId, while `rimworld/list_letters` does (E4); that tool's shape is **UNMEASURED**. Letters persist, so diff by `arrivalTick`. |
| `jawa/alerts_list` | none | `success, count, alerts[{type, label, priority, explanation}]` | Live shape was confirmed only by EmpirePursuit's own read, so treat it as **UNMEASURED** until one row is captured. |
| `jawa/weather_get` | `listDefs` | `weather, conditions[{def, scope, affectsThisMap, permanent, ticksLeft}], threatPoints, wealth, storyteller, readErrors[]` | A non-empty `readErrors` means unread, not zero. An ended condition still lists while paused (`traps.md` l.300). |
| `jawa/story_stats` | none | `numRaidsEnemy, numThreatBigs, colonistsKilled, colonistsLaunched, greatestPopulation, adaptDays, totalThreatPointsFactor` | Counters are cumulative: compare a before/after delta, never the absolute value. `colonistsKilled` delta is the cheapest "someone died" tripwire there is. |
| `jawa/forecast_incidents` | `numTestDays=15`, `currentMapOnly` | `threatBigCount, totalIncidents, byIncidentDef[], incidents[]` | No game time spent. Uses a forecast RNG, so it predicts nothing exactly; use it only as a pre-flight "storyteller is live" check. |
| `jawa/list_things` | `defName`, `rect`, `group` (ThingRequestGroup, e.g. `Corpse`, `Plant`, …), `includePawns`, `limit=200` | `things[{id, def, label, position, rotation, stackCount, hitPoints, maxHitPoints, faction, stuff, quality}], scanned, countReturned, countMatched, isCompleteList` | Zero with `scanned>0` means the filter excluded everything. The key is `faction`, not `factionName`. Whether `Fire` is a findable def with group `Fire` is **UNMEASURED** (try `defName="Fire"`). |
| `jawa/pawn_mental` `action=list` | `pawn` | `current state` + def list | One pawn per call, so it is expensive across a roster. |
| `jawa/pawn_break_thresholds` | `pawn` | `curMood, thresholdMinor/Major/Extreme, marginTo*, Break*IsImminent` | One pawn per call. |
| `jawa/pawn_need` `action=list` | `pawn` | `needs after` | Shape of the needs list is **UNMEASURED**. |
| `jawa/time_clock` | none | `ticksGame, paused, curTimeSpeed, …` | This is the budget instrument (`Session._ticks()` uses `rimworld/get_game_info.ticksGame`, which throws at the world screen). |
| `jawa/drain_log` | `limit=50`, `errorsOnly`, `contains` | `messages[{text, type, …}]` with repeat count | It is the only window onto log lines emitted during `step_game_ticks`. |
| `jawa/window_list_close` `list` | | `windows[{index,type,optionalTitle,isDebug,forcePause}]` | A forcePause modal silently blocks later calls and can kill `start_debug_game_ready` (traps.md l.737). |
| `rimworld/get_ui_state` | | `windowsForcePause` … | Used in `prove_contagion_burn.py`. |
| `jawa/map_info` | | `sizeX, sizeZ, mapBiome, outdoorTempNow, mapParent{defName,faction}, playerSettlementsOnThisTile, ticksGame` | `mapParent` non-null with a non-player faction is the E4 hazard. |

### Write (helper levers)

| tool | effect | traps |
|---|---|---|
| `jawa/debug_settings set` | `enableStoryteller`, `enableRandomMentalStates`, `enableRandomDiseases`, `noAnimals`, `enableDamage`, `enablePlayerDamage`, `godMode`, … | **RimSage-read 2026-10-01:** `Storyteller.StorytellerTick` returns early on `!enableStoryteller` only AFTER `incidentQueue.IncidentQueueTick()`, so incidents already queued still fire. Clear the queue too. `noAnimals` **destroys every spawned animal on its TickInterval** (`Pawn.TickInterval` l.2878), test animals included, so never use it in a creature test. `enableRandomMentalStates` gates `MentalBreaker` and social fights. Whether DebugSettings persist across a save/load is **UNMEASURED** (they are static, so probably reset on restart). |
| `jawa/incident_queue_clear` | `IncidentQueue.Clear()`, listing what it cleared | All or nothing. |
| `jawa/difficulty_tune` | `threatScale`, `allowBigThreats` | Belt and braces; a mod's own forced raid ignores it. |
| `jawa/destroy_bulk` | `filter = factionlessAnimals / playerAnimals / nonColonists`, `dryRun=true` default | **No exclusion list.** `nonColonists` would also destroy test-spawned hostiles and test animals, so a helper must kill by tracked id instead (below). |
| `jawa/damage` | `thingId` or `x,z`, `damageDef`, `amount`, `allowColonists` | Works on hostiles (the debug menu's ResolvePawn cannot). `Session.sweep` already kills with `Bomb 99999`. A kill leaves a Corpse, which is an Item. |
| `jawa/pawn_force_incapacitate` | `downed / dead / kill` | Reads `Downed`/`Dead` back; `kill` leaves no damage source. |
| `jawa/pawn_resurrect` | `restoreMissingParts`, `removeDiedThoughts`, … | Returns the real bool; early-outs FALSE on a non-dead pawn. |
| `jawa/pawn_health` | `add/remove/bionic/restore(confirmDestructive)` | A hediff at a time; **there is no "heal all" tool.** |
| `jawa/pawn_restore_part` | regrow one part, recursive | |
| `jawa/pawn_severity_adjust` | offset a hediff, then `CheckForStateChange` | Refuses offset 0 and negative-on-absent. |
| `jawa/pawn_need action=need` | `CurLevel` 0-1 per NeedDef | Mood is derived from thoughts, so a mood write is likely overwritten next tick (**UNMEASURED**). Fix thoughts or lower `colonistMoodOffset`. |
| `jawa/pawn_mental action=end` | `RecoverFromState` | Works on the permanent states too. |
| `jawa/map_fire action=extinguish` | destroys every Fire in a rect | |
| `jawa/weather_set lockWeather=true` | `GameCondition_ForceWeather`, the only durable weather | Plain transitions re-roll. |
| `jawa/game_condition action=end` | sets Duration = TicksPassed | It still lists until one tick passes (paused). |
| `jawa/rain_suppress` | blocks rain rolls for N ticks | |
| `jawa/clear_area` (`dryRun` default true) / `jawa/destroy_batch` (never pawns) | strip a rect | `clear_area` CAN destroy pawns whose def is destroyable. |
| `jawa/set_fog unfog` | | 🔴 `unfogAll` has wedged the game (memory: real-fog-of-war). Unfog rects only. |
| `jawa/set_faction_relation` | | 🔴 cannot make neutral hostile (traps.md l.670); use `jawa/faction_relations_set`. |
| `jawa/clear_ui`, `jawa/screenshot_mode`, `jawa/log_autoopen_suppress`, `jawa/window_list_close close` | screenshot hygiene | `log_autoopen_suppress`: read `installed` first. |
| `jawa/take_screenshot` / `rimworld/take_screenshot` / `rimworld/screenshot_cell_rect` | | `verified=false` always: stat the file. Names are per-second, so a burst collapses (traps.md l.117). A paused screenshot can be the previous frame (traps.md l.31). |

### Gaps: tools that do not exist (companion work, `rimbridge-companion` skill)

- **G1 `jawa/pawn_census`**: one call returning, per pawn, `mentalState`, `curJob` def + target,
  `inMentalBreakImminent`, `needs{food,rest,mood}`, `lord`/`duty`, `isPrey/isPredatorHunting`.
  `list_pawns` has none of these today, and the per-pawn tools cost N calls.
- **G2 `jawa/pawn_heal_full`**: remove every injury/disease hediff (keep implants/genes), restore
  missing parts, refill food/rest/joy, `RecoverFromState`, clear bad memories. It returns the before/after
  hediff and need sets. The debug menu probably has equivalents (`T: Heal random injury`,
  `T: Restore body part`?), but the paths are **UNMEASURED**, and `search_debug_actions` must not run on the full stack.
- **G3 `jawa/thing_fate`**: for a list of thing ids, report spawned / carried-by (pawn id) /
  in-container / destroyed, plus `CompRottable` stage and `RotProgress`. Without it, "where did the
  meat go" is unanswerable except by elimination.
- **G4 `jawa/letter_list` `sinceTick` + `mapId`**: diff letters cheaply and attribute them to a map (E4).
- **G5 `jawa/destroy_bulk` `exceptIds`**: lets "kill all wildlife" spare tracked test animals in one call.

## 3. Detector catalogue

Every detector is a pure function over a **Snapshot** (one dict of bridge reads taken once per
sweep), so the same detector runs offline against a recorded snapshot. The return shape is:

```python
@dataclass
class Hit:
    detector: str          # "hostile_pawns"
    severity: str          # INFO | WARN | SURPRISE | FATAL
    summary: str           # one line, templated, no LLM
    evidence: dict         # the exact rows that fired it (ids, defs, coords, ticks)
    suggest: list[str]     # helper names, e.g. ["kill_hostiles"]
    focus: tuple | None    # (x, z) for the surprise screenshot, else None
```

`SURPRISE` and `FATAL` trigger §6. `FATAL` also aborts the chain: its components are recorded
UNMEASURED with the hit's summary as `detail`, which is the "everyone died" verdict made legible.

**Expected sets.** A chain declares what it expects, so its own subject does not fire a detector:
`t.expect_presence(hostile=["Human53729"], animals=[...], letters=["She remembers the chains"],
conditions=["RM_FE_AshFall"])`. Tracked litter (`Session.litter`) is expected automatically.
Detectors fire only on what falls **outside** the expected set.

### Snapshot (one sweep)

`ticksGame` (`jawa/time_clock`) · `jawa/list_pawns includeHealth=true includeCorpses=true limit=500`
· `jawa/letter_list` · `jawa/alerts_list` · `jawa/weather_get` · `jawa/story_stats` ·
`jawa/list_things defName=Fire` (**UNMEASURED** that this finds fires; fallback `group=Fire`) ·
`jawa/list_things` over tracked thing ids (G3 when it exists) · `jawa/drain_log errorsOnly limit=50`
· `jawa/window_list_close list`. That is about 9 calls; per-call latency on the minimal list is
**UNMEASURED**, but the 2026-09-12 Pits run's call counts suggest well under a second each.
Two tiers keep it cheap:
- **tripwire tier** (every chunk): `time_clock`, `story_stats`, `list_pawns` (no health), `letter_list`.
- **full tier** (on any tripwire hit, at component end, and at chain end): everything above.

### Catalogue

| detector | reads | fires when | sev | suggest | FP / FN notes |
|---|---|---|---|---|---|
| `colonist_died` | `story_stats.colonistsKilled` delta; letters `defName=="Death"` since t0; `list_pawns` player rows `dead` | any delta > 0 for a non-expected pawn | FATAL | `restore_colonists` (resurrect) and re-run the chain | FP: a test that kills its own player-faction walker. That pawn is in litter, so it is excluded. E1 is the canonical true positive. |
| `colonist_downed` | player rows `downed`, `health.bleedRate>0`, `painTotal` | downed or bleeding and not expected | SURPRISE | `restore_colonists` | FN: an incapacitated pawn inside a container is not spawned. |
| `colonist_injured_unexpectedly` | player rows `health.hediffs` diffed against chain-start hediffs | a new injury hediff (Burn, Cut, Bite, Scratch, Gunshot…) | SURPRISE | `restore_colonists` | E2. Classifying the hediff def into fire / animal / weapon is a lookup table in code, not Jev. |
| `hostile_pawns` | rows `hostile==true`, not in the expected set | count > 0 | SURPRISE (WARN when > 40 cells from anchor and not moving) | `kill_hostiles` | `hostile` is relative to the player. A manhunter animal reads hostile (**UNMEASURED**: the flag is computed via `HostileTo(Faction.OfPlayer)`, so a factionless manhunter *should* read true). |
| `raid_arrived` | letters since t0 with `defName` in {ThreatBig, ThreatSmall} or label match; `story_stats.numRaidsEnemy` delta | delta > 0 | SURPRISE | `kill_hostiles`, then `storyteller_off` | E10: pawns may arrive a chunk later. Keep the hit "open" until `hostile_pawns` sees them or 600 ticks pass. LetterDef names for threats are **UNMEASURED** in our runs. |
| `predator_hunting` | factionless animal rows near player rows plus new Bite/Scratch hediffs on colonists or test pawns | an injury from an animal attack | SURPRISE | `kill_wildlife` | Without G1 (`curJob=PredatorHunt`) this fires only after the bite. With G1 it fires on intent. |
| `manhunter` | letters since t0 with label containing "Manhunter" (localised, so fragile), or G1 `mentalState=Manhunter*` | | SURPRISE | `kill_hostiles` | The label match is a string check in code. |
| `mental_break` | letters `NegativeEvent` with labels like "spree", "Berserk", "Mental break" (E1 had "Insulting spree"); G1 `mentalState` | a non-expected state | SURPRISE (FATAL if a Berserk-type state is aggressive) | `calm_colonists` | Per-pawn `pawn_mental list` covers it without G1, at N calls. |
| `need_critical` | `pawn_need list` per colonist (or G1) | food < 0.1 / rest < 0.1 / mood under `thresholdMinor` | WARN, SURPRISE at Malnutrition or Exhaustion hediff | `restore_needs` | A long `wait_ticks` (95000) will trip this legitimately. Restore pre-emptively per chunk (§5). |
| `fire_on_map` | `list_things defName=Fire` | any Fire whose cell is outside the expected rect | SURPRISE | `extinguish` | Pyrelands and Deepfire tests EXPECT fire, so their expected set lists the rect. |
| `item_vanished` | tracked thing ids/cells vs now: `list_things defName=<d> rect=<cell>` | a tracked thing gone, or `stackCount` dropped | SURPRISE | `forbid_and_wall` | Before firing, rule out E3 (`isCompleteList==false`) and "hauled" (same def elsewhere on the map with a summed stack). Without G3 the cause is classified by elimination: same def elsewhere means hauled; a Filth_* or Rotten nearby means rot (**UNMEASURED**); a colonist with an Ate thought means eaten (`pawn_thoughts`); otherwise destroyed. |
| `letter_unexpected` | letters since t0 minus the expected labels | any | INFO (NeutralEvent/PositiveEvent), WARN (NegativeEvent), SURPRISE (Death/Threat*) | none | This is the catch-all and the place where the E1 deaths would have surfaced. |
| `alert_unexpected` | `alerts_list` diffed against the chain-start set | new alert types such as `Alert_ColonistsIdle` (harmless) and `Alert_StarvationColonists` | per type, from a small table | | Alert type names are **UNMEASURED**; capture a set from a bland map first. |
| `condition_unexpected` | `weather_get.conditions` with `affectsThisMap` diffed against chain-start | new: Flashstorm, ToxicFallout, Eclipse, HeatWave… | WARN, SURPRISE for toxic/flashstorm | `end_conditions` | |
| `weather_changed` | `weather_get.weather` | changed and the chain did not lock it | INFO | `lock_weather` | |
| `modal_open` | `window_list_close list` rows with `forcePause` and not `isDebug` | any | SURPRISE | `close_modals` | It blocks later calls silently (memory: stale modal). |
| `log_errors` | `drain_log errorsOnly` since the last drain | a new Error type | WARN | none; this is triage input for Jev §7 | Repeat counts; the log is noisy on the full list. |
| `listing_truncated` | any read whose `message` says "beyond the limit" or `isCompleteList==false` | any | WARN; it suppresses every absence-based hit from that read | re-read with a rect or a higher limit | E3. It runs **first**, so that "missing" never comes from a capped list. |
| `clock_runaway` | `ticksGame` delta against the budget ledger | more ticks passed than any `wait_ticks` asked for | FATAL | `pause` | E6. This is the detector that enforces §5. |
| `strangers_near_anchor` | non-player, non-expected pawns within R of the anchor (wanderers, E8) | any | WARN | `clear_strangers` | It fires at chain start and gates `prepare_bland_map`. |
| `map_parent_hostile` | `map_info.mapParent.faction` not player and not null | | WARN at start | none; choose another map | E4. |

Severity is a lookup in one table (`detectors.SEVERITY`), not logic scattered across functions.
Each detector carries a **sanity probe** in its selftest: a recorded snapshot where it MUST fire.
E1's ShipMemory letters, E2's Burn row and E3's truncation message are the first three fixtures,
cut from the real summaries.

## 4. Helper catalogue and prepare_bland_map()

Every helper is **idempotent** (calling it twice is the same as once), **scoped** (it never touches
tracked litter or anything in the expected set), and **verified by a positive read-back**, never by
`success:true`. Each returns `HelperResult(name, acted: int, verified: bool, residue: list, evidence)`.
A helper that cannot verify raises `HelperUnverified`, which the context records like an UNVERIFIED
mutation (it will not silently pass).

| helper | does | verify by |
|---|---|---|
| `pause()` | `rimworld/pause_game pause=True` | `Session.paused()` logic: `ticksGame` read twice, equal |
| `storyteller_off()` | `debug_settings set enableStoryteller=false`; `incident_queue_clear`; `difficulty_tune threatScale=0, allowBigThreats=false` | `debug_settings list` shows false; `incident_queue_clear` returns `clearedCount` (0 on the second call); `difficulty_tune` `after` |
| `random_events_off()` | `enableRandomMentalStates=false`, `enableRandomDiseases=false` | `debug_settings list` |
| `kill_hostiles(exclude=expected)` | for each `list_pawns faction=hostile` row not excluded: `jawa/damage thingId Bomb 99999`; then `destroy_batch` corpse cell `categories=Item` | re-read: no hostile row outside the expected set. A hostile still alive after 2 passes goes into `residue`. Damage is applied while paused, so a step of 1 tick may be needed (traps.md: a paused explosion is a no-op; whether `jawa/damage` applies immediately is **UNMEASURED**; Session.sweep assumes it does) |
| `kill_wildlife(exclude=expected)` | factionless animal rows (`faction is None and intelligence=="Animal"`, **UNMEASURED** field value) not excluded, same kill route; `destroy_bulk factionlessAnimals` only when nothing is excluded | re-read |
| `clear_strangers()` | non-player humanlike rows not excluded | re-read |
| `restore_colonists(ids=all player)` | dead: `pawn_resurrect restoreMissingParts removeDiedThoughts`; then G2 `pawn_heal_full` (or, until G2: `pawn_health remove` per injury hediff at the chain-start diff); `pawn_mental end`; `restore_needs` | `list_pawns includeHealth`: not dead, not downed, hediff set equal to the chain-start baseline, `bleedRate==0` |
| `restore_needs(ids)` | `pawn_need need=Food/Rest/Joy level=1.0` | `pawn_need list` at ≥0.95 (Mood is excluded: it is derived) |
| `calm_colonists(ids)` | `pawn_mental end` for any non-null state | `pawn_mental list` shows current state null |
| `extinguish(rect=map)` | `map_fire extinguish` over the whole map rect from `map_info` | `list_things defName=Fire` returns 0 with `isCompleteList` |
| `end_conditions(keep=expected)` | `game_condition end` per unexpected condition | `weather_get` after a **1-tick step** (it lists while paused, traps.md l.300) |
| `lock_weather(def="Clear")` | `weather_set lockWeather=true` | `weather_get.weather` |
| `close_modals()` | `window_list_close close` per forcePause non-debug row, then `clear_ui` | `list` shows none; never `clear_ui all=true` blindly |
| `forbid_and_wall(thing_ids)` | stop colony AI eating or hauling test items. Forbid via debug action or `set_thing_props` (**UNMEASURED** whether either can set `forbidden`), or build the test in a `make_empty_room` with no door access | `item_vanished` stays silent over the next chunk |
| `clear_area(rect)` | existing `TestContext.clear_area` | existing read-back |

### `prepare_bland_map(t, radius=40)`

A fixed order, because each step protects the next:

1. `close_modals()`: a forcePause modal blocks or kills later calls.
2. `pause()`: verified.
3. `storyteller_off()` then `random_events_off()`: stop new causes before removing the present ones.
4. `extinguish()`, `end_conditions()`, `lock_weather("Clear")`, `rain_suppress(ticks=budget)`.
5. `kill_hostiles()`, `kill_wildlife()`, `clear_strangers()`, all with `exclude=litter` (empty at start).
6. `restore_colonists()`: the baseline for the colonist detectors is taken **after** this.
7. `t.clear_area(size=radius)` around the anchor (existing).
8. `log_autoopen_suppress suppress` and `drain_log` (flush), `clear_ui`.
9. **Baseline snapshot** (full tier). It records `t0 = ticksGame`, the letter count, the alert set,
   the condition set, colonist hediffs, and `story_stats` counters.
10. `assert_bland()`: run every detector against the baseline with an empty expected set; any
    SURPRISE means the map could not be made bland. Take the §6 screenshot and refuse the chain
    (UNMEASURED: "could not establish a bland map", never FAIL against the mod).

The runner calls `prepare_bland_map` before **every chain** (not once per suite), because E1's
letters show state leaking between suites on one map. Opt-outs are explicit per chain:
`@suite.chain("ashfall", keep={"storyteller": False, "conditions": ["RM_FE_AshFall"]})`. A suite
that tests a raid mod says `keep={"storyteller": True}` and declares the raid as expected.

**Teardown mirror.** At chain end, `Session.sweep()` (existing) runs, then
`restore_debug_settings()` puts back what `prepare_bland_map` changed. It reads the values from
the baseline, so a human who then plays the map gets their storyteller back.

## 5. Tick-budget design

**The rule:** game time is spent only through `TickBudget.spend()`, and the budget is checked
against the **measured** `ticksGame`, never against a Python counter of requests. No LLM decides
when to stop. The code does.

```python
class TickBudget:
    def __init__(self, suite_cap, chain_cap, component_cap, chunk=600):
        ...                      # caps in ticks; chunk = sweep interval
    def open(self, scope, ticks_now)      # suite / chain / component frames, stacked
    def charge(self, ticks_now)           # measured delta since the last read, charged to every open frame
    def remaining(self) -> int            # min over the open frames
    def check(self)                       # raises BudgetExceeded(scope, spent, cap) at > cap
```

- **Declared, not guessed.** Each `wait_ticks(n)` call is the request. The component's cap
  defaults to `1.25 × Σ requested` within it (declaration probe: `components_declared()` already walks
  every chain offline, so it can sum literal `wait_ticks` args; non-literals like `wait_ticks(ticks)` need
  an explicit `budget=` on the component, and lint refuses a component whose budget is unknown).
  Chain cap = Σ component caps. Suite cap = Σ chain caps, plus a hard ceiling (`MAX_SUITE_TICKS =
  60000`, one in-game day, which is a starting value and **must be re-set from measured runs**).
  `Antiquities.wait_ticks(95000)` exceeds it by design. That forces a conversation: a mechanism that needs
  1.6 days of game time should get a debug action that advances its own clock instead.
- **Chunked stepping with sweeps.** `TestContext.wait_ticks(n)` becomes:
  ```
  while advanced < n:
      step = min(budget.chunk, n - advanced, budget.remaining())
      if step <= 0: raise BudgetExceeded
      step_game_ticks(step, pauseFirst=True)      # existing call
      now = ticks(); budget.charge(now); budget.check()
      hits = sweep(tier="tripwire")               # §3
      if any surprise: escalate to full tier, screenshot (§6), apply policy
  ```
  The existing truncation and stall handling stay as they are. `chunk` defaults to 600 (E1's deaths came
  about 600 ticks apart; one sweep per 600 ticks localises a cause to one chunk). Raise it to 2000 for
  long waits once the bland-map tripwire rate is measured.
- **Every other clock mover is charged too.** `order_pawn` (E6), `walk_over`, `bridge_call` and
  anything else: the context reads `ticksGame` before and after **every** verb and charges the delta.
  A verb that moved the clock when it was not supposed to (`order_to` without `unpause:false`)
  raises the `clock_runaway` hit.
- **Policy on a surprise mid-wait**, chosen per chain (default `"heal_and_continue"`):
  - `"abort"`: FATAL; the component is UNMEASURED with the hit summary.
  - `"heal_and_continue"`: run the suggested helpers, verify them, and continue. **The component is
    then marked `PASS(INTERVENED n)`**, never a clean PASS, and the interventions are listed on the
    sheet (same rule as `PASS(UNVERIFIED n)`). Helper time is not charged (helpers run paused).
  - Death of a colonist **always aborts** the component. A resurrect mid-test changes the
    mechanism's inputs.
- **Pause guarantee.** `wait_ticks` ends with a verified pause in a `finally`, so an exception
  mid-wait cannot leave the game running. The runner's `finally` adds a verified pause before
  `sweep()`. A game left running after a script ends is the second root cause the owner named.
- **Watchdog outside the game.** A wall-clock guard in the runner (`signal.alarm` is not available on
  Windows `python.exe`, so use a `threading.Timer` that sets a flag checked between calls) gives each
  chain `max(120 s, budget_ticks / 60 × 2)` of wall time. On expiry: pause, screenshot, abort.
  Wall-clock per-tick cost on the minimal list is **UNMEASURED**; record it per run in the summary
  (`ticks_per_wall_second`) so the guard can be set from data.

## 6. Surprise -> screenshot protocol

On any `SURPRISE`/`FATAL` hit, **before** any helper runs (the helper would erase the evidence):

1. **Pause**, verified.
2. **Clear the view.** `window_list_close list`, then close debug windows (`isDebug`) via
   `jawa/clear_ui devWindows=true clearSelection=true`. `log_autoopen_suppress` stays on for the run.
   Record `remaining` from `clear_ui`, so an obscured frame names its culprit.
3. **Step 1 tick** so the frame is current (traps.md l.31: a paused shot can be the previous frame).
   Charge it to the budget.
4. **Frame the cause.** Use `hit.focus` (the dead pawn's cell, the fire, the hostile cluster centroid); if
   none, the anchor. Prefer `rimworld/screenshot_cell_rect` with `paddingCells` around the evidence
   cells (it frames and crops). Fall back to `jump_camera_to_cell` + `jawa/take_screenshot`.
   A second, **wide** shot covers the anchor area plus the focus.
5. **Unique filename**: `<mod>__<chain>__<component>__<detector>__t<ticksGame>__<seq>.png`, where `seq`
   is a per-run counter. That defeats the per-second collapse (traps.md l.117) and makes a sheet
   sortable by game time.
6. **Verify the file**: stat it, require size > 0.5 MB (traps.md l.112: a flat red frame was 0.49 MB),
   and md5 it against the previous shot of this run (identical means stale; retry once after another
   tick). If verification fails, use the `system_screenshot.py` fallback (already in `TestContext.screenshot`).
7. **Write a sidecar** `<same>.json`: the hit, the snapshot that fired it, the last 20 `drain_log` lines,
   the letters since t0, and the budget ledger. The sidecar is what Jev (§7) and a human read; the image is
   for a human.
8. Then apply the policy (§5).

**Why a bland map matters here:** after `prepare_bland_map`, the frame holds only colonists, the
test subject, and the intruder. A raider, a fire or a corpse stands out. On a raw quicktest
map the same frame is full of trees and wildlife, and the cause has to be hunted for.

The surprise shots land in `Transient/modcheck/surprises/<run>/`, and the HTML sheet
(`report.render`) gets a "Surprises" section per component: thumbnail, one-line summary, and
the helper that ran.

## 7. Jev integration

### Constraints that shape everything (from `~/.claude/skills/consult-jev/SKILL.md` and TypeSafe docs)

- 🔴 **Jev is text-only.** `docs/typesafe_snapshot/llms-full.txt` l.908: *"Images, audio, and
  video are not supported."* **Jev cannot judge a screenshot.** Image judgment stays with
  `modcheck/judge.py` (`claude -p`, one narrow yes/no per must-show line). Jev judges the
  **sidecar JSON** (§6 step 7) and other text.
- It cannot count, do arithmetic or compare ticks. All counts, deltas and "since t0" filtering are done
  in code before Jev sees the state.
- It reads literally, and a large or irrelevant state degrades accuracy. Send small named fields.
- **Never one question alone.** Each verdict question has a guard that cannot see the biasing input.
- **Confidence is a gate, never a ranker.** Below the gate, a human sees it; above, the code may act,
  **but only on things that are reversible and labelled** (a finding's routing tag, never a PASS).
- **Jev never drives and never decides to stop time** (owner: "the LLM never drives"). It runs
  after a sweep has already paused the game, or after the run, over recorded evidence.

### Candidate uses, ranked by value

| rank | use | why it is worth it | where it runs |
|---|---|---|---|
| 1 | **Unknown-def harm classifier**: classify a defName code does not recognise (a modded GameCondition, hediff, mental state, letter def, PawnKind) into a closed harm vocabulary, **once per def, cached** | The detectors' severity tables can only list defs someone wrote down, and this stack has 600+ mods. `RM_FE_AshFall` or `Archotechnic Requiem` are invisible to a fixed table. Feed the def's label and description from `jawa/get_defs`. The cache makes it nearly free, and every answer is a reviewable row in a file. | offline or between chunks; the answer is stored in `modcheck/harm_vocab.json` |
| 2 | **Failure attribution**: route a FAIL to {mod defect, harness defect, bridge-tool defect, environment intrusion, unknown} | It cuts the "needs a human" flood at its source. About 20 labelled FAILs already exist in `Transient/modcheck/*_summary.json`: Aftermath's `UnknownParameterError` (harness), ResearchRetag's `'700'` vs `700.0` (harness), the E3 truncation (harness), ShipMemory with 7 deaths (environment). | post-run, over `component.detail` plus the surprise hits during that component |
| 3 | **Cause-of-surprise classification**: "what killed / downed / injured this pawn" from a compact pawn record | It answers the owner's literal complaint. **Code goes first**: a hediff-to-cause table (Burn→fire, Bite/Scratch→animal, Gunshot/Cut+hostile nearby→raid, Malnutrition→starvation, mental state present→break). Jev runs only when the table returns 0 or ≥2 causes. | in the §6 sidecar step, paused |
| 4 | **Letter / alert triage** over labels since t0 | Letter labels are mod-authored prose ("She remembers the chains", "Archotechnic Requiem opportunity"), so a keyword list will rot. | per sweep (tripwire tier, new letters only, so usually 0 calls) |
| 5 | **Log-line triage** for `drain_log` errors: {from the mod under test, from another mod, engine/bridge noise, harmless} | Useful, but the namespace or packageId substring answers most of it exactly, and a string match beats a model. Jev is only for lines with no namespace. | post-run |
| 6 | **Before/after regression oracle**: code diffs two state dicts; Jev judges "is this change plausibly caused by `mod` (given its About description)?" per diff row | It attributes side effects (e.g. "all the meat disappeared" while a cooking mod is under test). It depends on rank 1's vocabulary. | post-run |
| 7 | "Is this a normal state for a bland map" tripwire per chunk | **Rejected as stated.** It needs counting ("no hostiles", "3 colonists"), which Jev cannot do, and code detectors answer it exactly. It survives only as rank 1 applied to unknown defs seen in a sweep. | n/a |

### Question battery (all in one file: `src/RimMandrake/Utils/modcheck/jev_questions.py`)

**Rank 1: unknown-def harm** (state: `{def_type, def_name, label, description}` only):
```python
DEF_HARM = {"type": "choice",
  "instructions": "What does the thing described in `description` do to colonists on the map?",
  "criteria": {
    "injures_or_kills": "It directly damages, injures, sickens or kills pawns.",
    "hostile_arrival": "It brings hostile people, animals or machines onto the map.",
    "mood_or_mind": "It changes mood, causes mental breaks, or alters behaviour, without injury.",
    "environment": "It changes weather, temperature, terrain, light or plants, without directly hurting pawns.",
    "item_loss": "It destroys, steals, spoils or removes items.",
    "harmless": "It has no meaningful effect on pawns or items, e.g. a notification or flavour text.",
    "not_stated": "The description does not say what it does."}}
DEF_IS_DESCRIBED = {"type": "noul",   # GUARD: never sees the harm options
  "instructions": "Does `description` say what this thing does in the game, rather than only naming it?"}
DEF_HURTS_DIRECTLY = {"type": "noul", # second, independent guard on the dangerous branch
  "instructions": "Does `description` state that pawns can be hurt, sickened or killed?"}
```
Combination (code): accept `DEF_HARM` only if `DEF_IS_DESCRIBED ≥ T_desc` **and**
`DEF_HARM.confidence ≥ T_gate`, **and** (`injures_or_kills` ⇔ `DEF_HURTS_DIRECTLY ≥ T_hurt`).
On disagreement, write the row as `REVIEW` and treat the def as SURPRISE-severity until a
human labels it (it fails safe).

**Rank 2: failure attribution** (state: `{component, failure_message, surprises_during:[summaries],
verbs_called:[names]}`):
```python
FAIL_ROUTE = {"type": "choice", "instructions": "Why did the check in `failure_message` fail?",
  "criteria": {
    "mod_behaviour": "The game ran the check correctly and the mod's content or behaviour differed from what was expected.",
    "harness_mistake": "The test script asked the wrong question: a wrong parameter, a wrong type comparison, a truncated list, a wrong field name.",
    "bridge_tool": "A bridge tool refused, crashed, or returned a malformed result.",
    "outside_event": "Something unrelated to the mod (a raid, an animal, a fire, a death, a mental break) changed the state first.",
    "not_stated": "The message does not give enough to tell."}}
MSG_NAMES_PARAM_OR_TYPE = {"type": "noul",   # guard for harness_mistake, sees only failure_message
  "instructions": "Does `failure_message` mention a parameter, a field name, a data type, or a list limit?"}
SURPRISE_PRESENT = None   # NOT a Jev question: `bool(surprises_during)` is code.
```
Code combination: `outside_event` requires a code-side surprise in the same component; Jev may not
assert it alone. `harness_mistake` requires the guard to be ≥ T. Output is a routing **tag on the
rimflow finding** (`--type modcheck-harness` vs `modcheck-failure`), reversible and visible.

**Rank 3: cause classification** (state: the pawn record reduced in code to named fields:
`{new_hediffs:[{def,label,part}], mental_state, hostiles_within_15:[kindDef], animals_within_15:[kindDef],
fires_within_10: bool, letters_since_t0:[label], conditions:[label]}`):
```python
CAUSE = {"type": "choice", "instructions": "What most likely harmed the pawn described in the state?",
  "criteria": {"fire": "...", "animal_attack": "...", "raid_or_hostile_people": "...",
    "starvation_or_exposure": "...", "mental_break_or_social_fight": "...",
    "disease_or_toxin": "...", "test_action": "A deliberate test action listed in `test_actions`.",
    "not_stated": "The fields do not point to any cause."}}
GUARD_HEDIFF_IS_INJURY = {"type":"noul", "instructions":"Is any entry in `new_hediffs` a physical wound?"}  # sees only new_hediffs
GUARD_THREAT_PRESENT  = {"type":"noul", "instructions":"Does `letters_since_t0` mention an attack, raid or hunting animal?"}  # sees only letters
```
Only the state fields named in a question's instruction are sent with that question, so the guards
are blind to the verdict question's inputs. **Implementation note:** a Jev call shares one `state`
across its questions, so a blind guard needs **its own call** with its own reduced state. That is
~150 ms extra, which is acceptable.

### Thresholds: measured, not preset

Every `T_*` starts as `None` and Jev's answers are **logged only** (shadow mode) until a sweep exists:
- **Rank 2 labels exist now:** about 20 FAILs in `Transient/modcheck/*_summary.json`, each
  labelable in seconds by reading the detail, plus their rimflow finding resolutions. Label them once into
  `modcheck/testdata/jev_fail_route_labels.jsonl` and sweep the gate.
- **Ranks 1 and 3 get self-inflicted ground truth**, the cheapest labels possible. On a bland map, *cause* each
  event on purpose and record the resulting sidecar with the known cause: `map_fire start` near a
  colonist (fire), `spawn_pawn` a predator kind hostile (animal_attack), `fire_raid` (raid),
  `pawn_force_mental_break` (mental), `pawn_need Food 0` plus ticks (starvation),
  `game_condition ToxicFallout` (toxin). One scripted session of about 30 events gives a labelled
  set where the label is a fact, not a judgment. Run it twice with different seeds for a holdout.
- For rank 1, the vanilla defs are free labels: every Core GameConditionDef, HediffDef and
  MentalStateDef has a known effect. Label ~60 vanilla defs, measure, then apply to modded ones.
- Record each sweep beside its constant (TypeSafe/ConsultJev rule: every threshold cites its measurement).

### What NOT to use Jev for

Counting hostiles, colonists or items; any tick/budget arithmetic; deciding to pause or stop;
deciding a component PASSes; judging a screenshot (it cannot see one); picking which helper to run
(a code table answers that exactly); matching a log line to a namespace (substring); detecting
whether a letter is "new" (`arrivalTick` comparison).

### Where the call lives

`jev_triage.py` imports `consultjev.ask` from `~/dev/ConsultJev` (path from env `CONSULTJEV_PATH`).
The key comes from `TYPESAFE_API_KEY` / `~/.config/consultjev/env`. **MEASURED 2026-10-01 on archmagi WSL:
`~/.config/consultjev/env` does not exist and `TYPESAFE_API_KEY` is unset**, so Jev cannot be called
from this machine today. The skill doc's paths are the Mac's (`/Users/mandrake`). Provisioning the key
here is the owner's call (it is a credential). All
calls are wrapped so that **Jev absent means a field `jev: "UNAVAILABLE"`**, never a failure: the
harness must be whole without it, the same law as the in-game LLM. Runs where the bridge
lives under `python.exe` call Jev **post-run from WSL python3**, over the sidecars. That avoids putting a
network client in the bridge process and keeps Jev out of the tick loop entirely, except for rank
4, which is optional.

## 8. Module layout, API, selftests, build order

### Files (all under `src/RimMandrake/Utils/modcheck/` unless noted)

| file | holds | game? |
|---|---|---|
| `snapshot.py` | `take_snapshot(session, tier, tracked) -> dict` (the reads in §3), `Baseline` | bridge |
| `detectors.py` | `Hit`, `SEVERITY` table, `HEDIFF_CAUSE` table, every `detect_*(snap, baseline, expected) -> list[Hit]`, `sweep(snap, baseline, expected)` | **pure** |
| `helpers.py` | `HelperResult`, `HelperUnverified`, every helper in §4, `prepare_bland_map`, `restore_debug_settings` | bridge |
| `budget.py` | `TickBudget`, `BudgetExceeded`, ledger serialisation | **pure** |
| `surprise.py` | the §6 protocol: `capture(session, hit, ctx) -> {png, sidecar}`, filename builder, the md5/size verifier | bridge plus fs |
| `jev_questions.py` | every Jev question and `T_*` constant, each citing its sweep or saying `UNMEASURED` | **pure** |
| `jev_triage.py` | `classify_def`, `route_failure`, `classify_cause`, `triage_letters`; the cache `harm_vocab.json`; Jev-absent degrades to `UNAVAILABLE` | network |
| `suite.py` (edit) | `TestContext` gets `budget`, `expected`, `expect_presence()`, sweep inside `wait_ticks`, before/after tick charge on every verb, `PASS(INTERVENED n)` | |
| `runner.py` (edit) | `prepare_bland_map` before each chain, verified pause in `finally`, wall-clock watchdog, `surprises` in the summary, a post-run Jev pass | |
| `report.py` (edit) | "Surprises" section per component | |
| `selftest_detectors.py`, `selftest_budget.py`, `selftest_helpers.py`, `selftest_jev.py` | offline | none |
| `src/RimMandrake/Utils/rimdrive/fake.py` | `FakeSession`: a scripted bridge | none |

`rimdrive` stays L1/L2 (connection, mutate/verify). The situational layer is modcheck's, because it
needs the expected-set and component bookkeeping that only `TestContext` has. Standalone `prove_*.py`
scripts can still use it: `helpers.prepare_bland_map(session)` takes a bare Session plus an optional
expected set.

### API sketch (what a suite author writes)

```python
@suite.chain("ashfall", keep={"conditions": ["RM_FE_AshFall"]}, policy="heal_and_continue")
def ashfall(t):
    t.clear_area(40)                                  # prepare_bland_map already ran
    t.bridge_call("jawa/game_condition", action="start", condition="RM_FE_AshFall")
    t.expect_presence(conditions=["RM_FE_AshFall"], fire_rect=None)
    with t.component("ashfall_accumulates", budget=3000):
        t.wait_ticks(2600)                            # chunked, swept every 600, budget-enforced
        ...
```
At any point: `t.sweep()` returns the hits; `t.heal()` runs the policy's helpers; `t.surprises`
lists what was captured.

### FakeSession: making most of this offline-testable

`FakeSession(script)` answers `call(tool, **params)` from a world model, not canned replies:
- `world = {ticks, paused, pawns:{id: row}, things:{id: row}, letters:[...], conditions:[...],
  debug:{...}, log:[...], windows:[...]}`. The rows are **copied from real recorded results**
  (`Transient/modcheck/JawaIonWeapons_summary.json` for list_pawns rows,
  `ShipMemory_summary.json` for letters), so key names cannot drift from the real bridge.
- Tools mutate the model: `step_game_ticks` advances `ticks`, and runs **scheduled events**
  (`fake.at(tick=900, kill="Human966", letter=("Death","Death: Justice"))`), with optional
  truncation (`truncate_to=700`) to reproduce E9. `jawa/damage Bomb` marks a row dead, and so on.
- **Adversarial modes** reproduce each known lie: `success:true` with no effect (for helper
  verification), `list_pawns` honouring `limit` with a "beyond the limit" message (E3), and
  `step_game_ticks` moving 0 ticks (stall).
- Each tool's fake is checked against the companion's own `ResultDescription` keys via
  `bridgetools/tool_metadata.py`, so a key the fake invents and the real tool lacks fails the selftest.

Selftests then assert behaviour, not names:
- a raid scheduled at tick 1000 inside a 2600 wait yields exactly one `raid_arrived` hit with
  `t_chunk ≤ 1200`, a surprise capture call sequence `pause → clear_ui → step 1 → screenshot`, and
  `PASS(INTERVENED 1)`;
- a colonist death scheduled anywhere aborts the component as UNMEASURED with "colonist_died" in `detail`;
- `order_pawn` moving the clock 18,000 ticks raises `clock_runaway` (E6);
- E3's truncation yields **no** `item_vanished` / "pawn missing" hit, but a `listing_truncated` WARN;
- every helper whose fake returns `success:true` with no effect raises `HelperUnverified`;
- the budget refuses `wait_ticks(95000)` under a 60000 suite cap before any tick is spent;
- the **sanity probes**: E1, E2 and E3 fixtures each fire their detector.

Registered in `run_selftests.py` (CLAUDE.md: run every selftest before a commit).

### Build order (each step has a checkable outcome)

1. **`detectors.py` + E1/E2/E3 fixtures + `selftest_detectors.py`.** Done when E1's letters yield 7
   `colonist_died`/`letter_unexpected(Death)` hits, E2 yields `colonist_injured_unexpectedly(Burn→fire)`,
   and E3 yields `listing_truncated` and nothing louder. Fully offline, Sonnet-sized.
2. **`budget.py` + `selftest_budget.py`.** Done when the ledger charges measured deltas and refuses
   over-cap requests in fake runs.
3. **`rimdrive/fake.py`.** Done when the fake replays a recorded summary's calls and returns the same
   keys (tool_metadata cross-check passes).
4. **`suite.py` wiring** (sweep in `wait_ticks`, per-verb tick charge, `expect_presence`,
   `PASS(INTERVENED)`). Done when every existing selftest still passes and the new behavioural ones pass.
5. **`helpers.py` + `prepare_bland_map`**, offline against the fake. Done when every helper raises on a
   no-effect fake.
6. **First live proof** (needs the bridge; minimal list, quicktest map): run `prepare_bland_map`, then
   `assert_bland()`; then cause one of each event on purpose (§7's self-inflicted set) and confirm each
   detector fires **and** each surprise PNG passes the md5/size check. This is also where the UNMEASURED
   rows in §2 get measured (`Fire` lookup, alert type names, threat LetterDef names,
   `rimworld/list_letters` shape, `jawa/damage` while paused, mood write persistence, per-call latency).
   Record them back into §2 of this file.
7. **Companion tools G1-G5** (rimbridge-companion skill, one build/deploy cycle each, on the minimal list).
   Done when the selftest for `predator_hunting`/`item_vanished` switches from inference to a direct read.
8. **Re-run the RED suites** of 2026-09-13 (ShipMemory, JawaIonWeapons, Pyrelands, Inhabited) under
   the new harness. Done when every FAIL either reproduces with zero surprises (it is a real mod finding)
   or turns into a surprise-attributed UNMEASURED (a harness or environment finding). Either way a human
   no longer has to sit and watch.
9. **Jev shadow mode**: build `jev_questions.py`/`jev_triage.py`, label the ~20 FAILs, run the
   self-inflicted event session, and sweep thresholds. Done when each `T_*` cites a sweep. Only then does
   routing go live (a tag on the finding).

## 9. Open questions

1. **Policy default**: should `heal_and_continue` be the default, or `abort`? Healing makes more runs
   finish but marks them `PASS(INTERVENED)`. Does a PASS with an intervention count toward GREEN in
   `modcheck status`? (Proposed: no. It counts as GREEN-with-caveat, shown separately.)
2. **Storyteller-off by default for every chain?** It removes the main noise source but hides
   interactions between a mod and real incidents. Proposed: off by default, plus an opt-in nightly
   "storyteller on" pass for mods that touch incidents.
3. **`MAX_SUITE_TICKS`**: 60000 is a placeholder. Antiquities wants 95000. Should long-clock
   mechanisms be forced to expose a debug "advance my clock" action instead?
4. **E1's cause.** Seven deaths about 601 ticks apart is a pattern, not noise. Is it a mod under
   test in that multi-suite session (ShipMemory's 600-tick check interval? Ninefold?), or a quicktest
   artefact? Worth one targeted look before the harness hides such events behind `heal`. A harness that
   heals over a real mod bug that kills colonists every 600 ticks would be the worst outcome. That is
   why `colonist_died` always aborts and is never healed past.
5. **Map choice**: a quicktest map, or a dedicated flat "bland test map" save (one biome, no
   wildlife spawns, all-DLC, a walled pen)? A save loads faster than a quicktest regenerates
   (**UNMEASURED**) and starts bland, so `prepare_bland_map` becomes a verifier, not a fixer.
6. **Companion tools G1-G5**: build them all up front (one deploy cycle) or on demand?
7. **Jev key on the Desktop**: provisioning `TYPESAFE_API_KEY` here is the owner's decision.
8. **Wildlife exclusion**: until G5 exists, `kill_wildlife` must kill per id (N calls). Acceptable on
   a bland map (few animals). Is it acceptable on a quicktest map with 40+ animals?

## 10. Revisions after the GPT review (BINDING — these override §§3–8 where they differ)

Source: `design/RimMandrake/northstar_helpers_gpt_review.md` (codex, gpt-5.6-sol xhigh, 2026-10-01).
Every item below was checked against the plan and accepted; the review's other points stay as reading.

1. **Default surprise policy is `abort`**, not `heal_and_continue`. Healing is opt-in per chain and only for
   declared nuisance classes before the component's decisive observation. `PASS(INTERVENED)` never counts GREEN.
2. **One clock gate.** A single `ClockGate` owns `last_seen_tick`; every tick-moving verb goes through it, every
   observation re-bases it, and the delta since the last seen tick is charged — including ticks that passed between
   calls. **Helper and evidence-refresh ticks are charged to an overhead ledger** under the same hard session cap
   (the old "helper time is free" line is wrong). A negative or discontinuous delta starts a new **epoch**
   (save/load, map change); it is never free time. No readable clock ⇒ refuse tick-moving verbs.
3. **Evidence before action.** On a surprise: freeze ONE shared pre-intervention snapshot, write the sidecar
   atomically, capture every hit, and only then run a helper. **No refresh tick just to take a screenshot** — pause,
   capture, record; stepping a tick is allowed only after a live probe proves it harmless. Dedup surprises by stable
   event fingerprint with a cooldown (no screenshot storm).
4. **Helpers are exact-ID and transactional.** No `Bomb 99999` (it hurts neighbours and lights fires): use
   `pawn_force_incapacitate kill` on the exact pawn, else a single-target non-explosive `jawa/damage`. No category
   destroy at a corpse cell; dispose exact ids only. "Idempotent" is replaced by "converges to a verified
   postcondition and records side effects". Settings are a **transaction**: record pre-mutation values FIRST,
   restore exactly in `finally` (the plan's "restore from the post-prepare baseline" was wrong).
5. **Restore is baseline-delta, not perfect health.** Reverse only post-baseline deltas (per-instance hediff id +
   part + severity), never blanket-remove disease/addiction/implant hediffs, never wipe memories — only exact
   post-baseline nuisance thoughts. Mood is derived: write nothing to it; `colonistMoodOffset` raises mood when
   positive (the plan had the sign backwards).
6. **Detector corrections.** `isPlayer` ≠ colonist (need `isColonist/isSlave/isPrisoner`; use the roster until G1
   exists). `hostile` ≠ threat (predator targeting, berserk colonists, inbound pods). Manhunter comes from mental
   state, never localized letter text. Letters are fingerprinted (label+defName+arrivalTick multiset against the
   baseline), not `arrivalTick > t0`. An item id vanishing is not a quantity vanishing (stack merges): track total
   quantity per def/tag. Add detectors: `evidence_truncated_or_stale` (runs FIRST, invalidates absence-based hits),
   `map_context_changed`, `settings_drift`, `expected_contract_broken`, `health_progression`, `pawn_roster_transition`.
   Expectations suppress only the PRESENCE alarm, have a lifetime/phase, and are registered atomically with the
   mutation (`with t.expecting(...): spawn`).
7. **Checkpoint beats sanitising.** Prefer a dedicated pristine bland save, reloaded per isolated chain, verified by
   fingerprint; `prepare_bland_map` becomes a verifier that REFUSES on unknown hazards rather than erasing them.
   `incident_queue_clear` is global — add selective peek/remove (companion gap G6) before routine use.
8. **Watchdog is a separate supervisor** (a `Timer` flag cannot interrupt a blocked bridge call): wall-clock guard in a
   sibling thread that opens its OWN connection to request pause, and kills the worker on expiry.
9. **Screenshot verification:** PNG decodes, dimensions sane, non-uniform — not a fixed 0.5 MB threshold; wait for
   stable file size; discover the actual returned path; system_screenshot only as an explicit opt-in, cropped to the
   game window. Never auto-close a non-debug choice dialog (abort with window metadata instead).
10. **Companion gaps added:** G6 incident-queue peek/selective-remove, G7 damage-event ring buffer
    (victim, def, amount, instigator, weapon, tick), G8 holder/stack lineage, G9 pawn roles + lord/duty + map id.
11. **E1 is investigated, not suppressed:** the 7-deaths-at-~601-ticks event is reproduced on a disposable map as the
    first live probe and becomes a fixture. The ~601 cadence could be the harness's own sweep rhythm.
12. **Build order (supersedes §8):** safety semantics → E1/contract live probe → ClockGate+supervisor → snapshot/event
    contracts + fixtures → minimal FakeSession → pure detectors → evidence capture → exact-ID helpers → verifier-style
    bland setup → companion tools → abort-only pilot → self-inflicted threat cases → progressive integration → Jev
    shadow mode.
13. **Jev additions (shadow mode, review flags only, never PASS/heal/stop):** vacuous-test lint over a validation
    script's `(test_intent, stimulus, observed_assertion)`; expected-set overbreadth auditor; semantic oracle beside
    exact checks; duplicate-failure clustering; tool-mutation-risk lint (once per bridge tool, cached). The first of
    these needs no game at all and is the cheapest first Jev win.

## 11. MEASURED live, 2026-10-01 (minimal 26-mod list, quicktest `TemperateSwamp`, fixture `src/RimMandrake/Utils/modcheck/testdata/contract_probe_2026-10-01.json`)

Settles most §2 UNMEASURED rows. Read these before trusting any detector written from the older prose.

- **Latency is negligible:** every read 4–50 ms; `step_game_ticks` 60 ticks = 385 ms, 300 ticks = 875 ms (~340 ticks/s).
  A full snapshot is ~150 ms. The budget guard exists for game-TIME contamination, not wall-clock cost; sweep freely.
- **Cold start measured:** launch→`Bridge token:` 48 s; `start_debug_game_ready` → map readable ~12 s after the call returns.
- **Fresh quicktest map is NOT bland** (screenshot read): dense forest + ancient ruins + 58 wild animals + 2 factionless
  humanlike strangers at t=0 (E8 confirmed). A colonist had **Frostbite within 60 ticks** (swamp tile, 40 °F) — environment
  hurts people with no raid involved. A flat dry tile is needed (`jawa/world_tile_map_generate`; not yet driven here).
- `isPlayer` is true for the colony **Husky**: a colonist is `isPlayer and intelligence=="Humanlike"`. Dead pawns keep
  `isPlayer`, `faction`, and have `spawned:false`; dead rows include pre-seeded dead Drifters.
- **A factionless wolf reads `hostile:false`** (`faction:None`). `hostile` finds raiders only; predators need
  `kindDef`/`intelligence=="Animal"` + `faction None` + proximity, or a manhunter mental state. Mental state is
  NOT in `list_pawns` rows (needs `pawn_mental list`, or companion G1).
- **`list_pawns` truncation fields:** `returned`, `truncated` (count cut), `totalOnMap`, plus the `message`. Test `truncated>0`.
- **Paused mutations are IMMEDIATE:** `jawa/damage` hediffs, `pawn_force_incapacitate kill` (Death letter + `colonistsKilled`
  +1 with no step), and `fire_raid` (2 hostile rows at once, `numRaidsEnemy` +1) are all readable with zero ticks spent.
  A fire started while paused spreads on the next step (3→4 fires in 60 ticks).
- **Letters:** `jawa/letter_list` `label` is a dict (`RawText`); `rimworld/list_letters` gives `id`, `type`
  (`Verse.DeathLetter`), `letterDef`, plain `label`, `text`, `arrivalTick`, `ageTicks`, `lookTargets` (no `mapId` seen).
  Real defNames: `Death`, `ThreatBig` ("Raid: <name>"), `NegativeEvent` ("Sad wander: <pawn>" for a forced mental break),
  `NeutralEvent`. A death also spawns a companion `NeutralEvent` ("Mourning of Nature opportunity for X") — dedupe.
- **`jawa/alerts_list` stayed EMPTY** after a death, a raid and a mental break within 371 ticks: alerts are throttled, so
  never use them as a tripwire (detector `alert_unexpected` is demoted to INFO-only).
- **Fire:** `jawa/list_things defName=Fire` works (`scanned` 43183, `isCompleteList`); `group="Fire"` scans 0 — do not use it.
- **Settings:** `jawa/debug_settings action=list` → `fields:[{name,value}]` (47). `jawa/weather_get` →
  `weather.current`, `conditions[]`, `storyteller{def,difficulty,threatScale,allowBigThreats}`, `readErrors[]`.
  `jawa/story_stats` is cheap and instantaneous. `jawa/incident_queue_clear` → `clearedCount`, `cleared[]`.
- **Screenshot:** `rimworld/take_screenshot` 262 ms, 3.4 MB, returns the Windows `path` + `sizeBytes`; the result also embeds
  the UI state (`Dialog_DevPalette` was open and top window — `clear_ui` is needed to get a clean frame).
- **`time_clock`:** `{ticksGame, ticksAbs, curTimeSpeed:"Normal", paused:true}` — `curTimeSpeed` is **not** `"Paused"` while
  paused; the `paused` flag is the truth (clockgate's verify_pause must not require a speed string).

## 12. BUILT and PROVEN live, 2026-10-01 (what shipped, what it found)

Code (`src/RimMandrake/Utils/modcheck/` unless noted): `clockgate.py` (python-enforced tick budget, epochs, pause
verification, supervisor) · `snapshot.py` + `detectors.py` (20 detectors, one severity table, fixture/expectation
model) · `helpers.py` (exact-id, read-back-verified helpers, settings transaction, `prepare_bland_map`, `safe_anchor`) ·
`surprise.py` (evidence-first capture: sidecar, one screenshot copied beside it) · `watch.py` (the per-chain envelope) ·
`jev_questions.py` + `jev_triage.py` (shadow-mode Jev, every threshold None) · `vacuity.py` (code-first lint) ·
`rimdrive/fake.py` (a world-model fake with the measured lies). Selftests: clockgate 41, detectors 85, helpers 40,
watch 31, jev 19, vacuity 8 (all offline, all with negative controls); the existing suites still pass.
Use: `python.exe src/RimMandrake/Utils/modcheck/cli.py run <Mod> --situational [--policy abort|record]`; in a script,
`t.expect(kind, matcher)` declares what the chain causes on purpose, `t.check_surroundings()` sweeps now.

**The "everyone is dead / the meat vanished / no one knows why" causes, measured not guessed:**
1. **The harness killed its own fixtures.** `Session.sweep` tears down test-spawned player-faction walkers with
   `Bomb 99999`; each becomes a dead colonist with a Death letter that the NEXT suite reads as a casualty. This is
   ShipMemory E1 (7 "colonist deaths", two "Roof collapse" letters). Re-run on a bland map the same suite spent 700
   ticks with zero deaths. Fix: fixtures are registered (even when spawned through raw `bridge_call`), carried across
   chains and runs (`Transient/modcheck/fixtures.json`, reset when the clock goes backwards).
2. **The harness set the map on fire.** Killing ONE Boomalope = 25 fires in 5 ticks (39 by 30). A fresh quicktest map
   carries explosive wildlife; the old "122 fires in 120 ticks" and a Droidworks fire surprise were `kill_wildlife`.
   Fix: wildlife is removed with `jawa/destroy_bulk` (no death, no corpse, no fire).
3. **The test explodes next to the colonists.** The default anchor is the map centre, where the colony spawns; a droid
   detonation test killed two starting colonists. Fix: `safe_anchor` picks the point farthest from every colonist.
4. **The map is not bland.** The quicktest tile is random (swamp/forest/tundra), with ruins, dense plants, 58 wild
   animals, 2 strangers, and a colonist with Frostbite or an old gunshot at tick 60 (`NORTHSTAR_BLAND_TILE_1`).
5. **Time runs where nobody asked.** `order_pawn` can run the clock 18,000 ticks; now charged and aborted at 1500.

**Live pilot results (abort policy, one fresh map, suites back to back):** ShipMemory 700 ticks, no surprise; a real
FAIL remains (the letter never arrives: a mod/suite finding on a clean map). JawaIonWeapons: genuine FAILs now free of
"pawn not found / E3" noise. Droidworks: 12 PASS, 0 surprises, 5 real FAILs, 4 UNMEASURED by cascade. FlowWorks 3 PASS.
`vacuity.py` over 280 components found exactly 1 that asserts nothing (Ninefold `mood_walk_advances`, self-declared
"UNVERIFIED BY DESIGN"); the first, naive pass flagged 48, 28 of them helpers: calibration the Jev lint will need.

**Still UNMEASURED / owed:** whether stepping 1 tick before a screenshot is harmless (policy stays "never step");
how often a bland tile changes results (`NORTHSTAR_BLAND_TILE_1`); a manhunter's mental state without the pawn census
(`NORTHSTAR_COMPANION_GAPS_1`); Jev's actual accuracy (no key on Archmagi: `JEV_KEY_ARCHMAGI_1`; every threshold is None,
so it logs to `Transient/modcheck/jev_shadow.jsonl` and acts on nothing); wall-clock ticks/second under the full list.
Rollout: `NORTHSTAR_SITUATIONAL_ROLLOUT_1` (flip the default after an abort-only pass over every suite).
