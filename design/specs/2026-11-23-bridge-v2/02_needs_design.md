# BRIDGE v2.0, pass 1: what live testing needs from the bridge (the needs design)

Item `RIMMANDRAKE_DESIGN_BRIDGE_TWO_WHAT_LIVE_TESTING_NEEDS_FABLE_PASS_ONE`. Written 2026-11-23.
This file says WHAT is needed. HOW to build it, and whether to rebuild or improve the present bridge, is the second
designer's question. The evidence is `01_census.md`. The policy that this design serves is
`../2026-11-23-three-test-kinds/rule_draft3.md`. Open decisions are in `03_open_questions.md`.

**The bridge** is how a program outside RimWorld drives a running game: it places things, gives orders, lets time run,
and reads what happened.

## The one change that the rest depends on

Today the unit of work is **one tool call**. A live test is a script outside the game that makes hundreds of calls and
decides between them. Every call is a gap in which the game may move, the caller may time out, and a short event may
be missed. Five of the ten most damaging influences in the census are faults of that gap (`01_census.md`, the ranking).

In v2 the unit of work is **one scene run**. The caller sends a whole scene as data. The game side prepares it, checks
it, watches it, lets time run, decides the result against the scene's contract, and returns one receipt. No decision
waits on a round trip. The single tools still exist, for exploring and for a test pilot, but no acceptance test is
built from them.

Every capability below is either a part of the scene run, or a thing that the scene run stands on.

## Words used here

| word | what it means |
|---|---|
| **scene** | one live test: a prepared place, a cast, an act, and a contract |
| **contract** | the scene's claim, entry point, valid opportunity, success, forbidden effects and end (policy §1) |
| **cast** | the pawns and things that the scene placed and named. Everything else on the map is a **bystander** |
| **alias** | the scene's own name for a cast member ("carrier", "raider1"). Results use aliases, never raw game ids |
| **station** | a rectangle of a test map that one scene owns for one run, with a margin round it |
| **deciding window** | the ticks from the act to the end, in which the contract is decided |
| **control** | one thing that the calm environment holds or watches (for example "no unasked incident") |
| **calm profile** | a named set of controls, switched on in one call |
| **breach** | something that a control exists to stop, which happened or tried to happen |
| **probe** | a declared observation that runs inside the game: a **track** (a value sampled every tick) or a **tap** (an event caught at the moment it happens) |
| **trace** | what the probes of one run recorded |
| **receipt** | the compact result of one run: the outcome, the first failed condition, what was loaded, what was on |
| **force level** | how hard the scene pushed an actor, on the Minimum Force ladder (policy §7) |
| **sample** | one run whose random draws were its own. A **replay** repeats the draws of an earlier sample |
| **twin** | a second copy of a scene's start state, built beside its aftermath for the owner to compare |
| **test game** | ArchSmall, Steve1, Steve2, or ArchBig on a disposable save. **His game** is ArchBig on a save of his |

## Engine facts the design stands on

READ means I read the named symbol in the RimWorld 1.6 code through RimSage in this run. GUESS carries a confidence.
A GUESS that decides a design choice is repeated in `03_open_questions.md` for the second designer to read.

| fact | status |
|---|---|
| One simulation tick is `TickManager.DoSingleTick()`. It is public. `TickManagerUpdate()` calls it in a loop, at most `TickRateMultiplier * 2` times per frame, and stops after 45.45 ms. | READ |
| The order inside a tick: each map's `MapPreTick` (which runs `PathFinder.PathFinderTick`), the tick counter, the three tick lists, then world, storyteller, quests, each map's `MapPostTick` (wild animals, weather, game conditions, fire watch, map components), game components, letters, autosave. | READ `TickManager.DoSingleTick`, `Map.MapPreTick`, `Map.MapPostTick` |
| Each map also does simulation work once per FRAME, outside the tick: `Map.MapUpdate` updates power nets, rebuilds dirty regions and rooms, updates the glow grid and pawn groups, and processes "post-tick visuals". | READ `Map.MapUpdate` |
| How often a thing runs its interval work depends on the camera. `Thing.DoTick` calls `TickInterval(delta)` every `UpdateRateTicks` ticks, and `GenTicks.GetCameraUpdateRate` returns 15 for a thing on a map that is not shown or outside the camera's view, and (zoom level + 1) for a thing in view. Animals always use 15. | READ `Thing.DoTick`, `GenTicks.GetCameraUpdateRate`, `Pawn.UpdateRateTicks` |
| A path request is computed by Unity jobs that `PathFinderTick` schedules. The next `PathFinderTick` first calls `ForceCompleteScheduledJobs` and then hands each result to its request. So a path result arrives on a tick boundary, not on a frame. | READ `PathFinder.PathFinderTick`, `FinalizeRecyclePathJobData`. That `PathRequest.ResultIsReady` is set only there: GUESS 80% |
| `Verse.Rand` is one global stream. Its whole state is two numbers, `seed` and `iterations`. It is seeded from the clock when the process starts. `PushState` and `PopState` exist. | READ `Rand` |
| The global random state is not written into a savegame. | GUESS 85% (a search for a save site of the state found none) |
| The storyteller makes incidents every 1,000 ticks, only while `DebugSettings.enableStoryteller` is true. The incident queue ticks every tick, whatever that switch says. | READ `Storyteller.StorytellerTick`, `IncidentQueue.IncidentQueueTick` |
| `IncidentWorker.TryExecute` is public and not virtual. The storyteller, quest parts, scenario parts, signals, site parts, world raids, rituals and abilities all call it (27 call sites). | READ (search of call sites) |
| Other switches that exist: `enableRandomMentalStates` (read in `MentalBreaker` and in social fights), `enableRandomDiseases`, `enableDamage`, `pauseOnError`, `fastEcology`, and `noAnimals`, which destroys EVERY spawned animal on its next tick. | READ `DebugSettings` and its users |
| Wild animals are replenished by `WildAnimalSpawner.WildAnimalSpawnerTick`: a check every 1,213 ticks, a chance scaled by the biome's density, entry at a map edge or from the air. | READ |
| The weather changes when `curWeatherAge` passes a duration. A game condition can force a weather (`WeatherDecider.ForcedWeather`). A large fire shortens the duration to a quarter and multiplies the chance of rain by 15. `DisableRainFor(ticks)` exists. | READ `WeatherDecider` |
| Needs change every 150 ticks per pawn (`Pawn_NeedsTracker.NeedsTrackerTickInterval`). A need has a protected `IsFrozen`. | READ |
| A pawn's job tracker asks its constant think tree every 30 ticks, and looks for a new job whenever it has none. | READ `Pawn_JobTracker.JobTrackerTickInterval` |
| Every mental state starts through `MentalStateHandler.TryStartMentalState`. | signature READ; "every": GUESS 85% |
| An exception in a thing's tick is caught by `TickList.Tick` and sent to `Log.Error`; outside dev mode it is logged once per thing. | READ |
| The game log stops at 10,000 messages. `Log.ResetMessageCount()` starts it again. `DebugSettings.pauseOnError` pauses on an error. | READ `Log` |
| A load of a savegame queues a long event that loads the "Play" scene and builds a new `Game`. Static fields of mods are not touched by this. | READ `GameDataSaveLoader.LoadGame`; statics: GUESS 90% |
| Flight is a state machine in `Pawn_FlightTracker`: Grounded, TakingOff (50 ticks), Flying, Landing (50 ticks), with private `lerpTick`, `flyingTicks`, `flightCooldownTicks`. A takeoff is a random chance at the start of a job that allows flight. `StartFlying()` and `ForceLand()` are public. | READ |
| The frame of a pawn's animation is `PawnRenderTree.AnimationTick`: the game tick minus the tick the animation started, wrapped by the animation's length. It is a function of game ticks only. | READ |
| A jumping or thrown pawn (`PawnFlyer`) computes its position from its own tick count. | READ `PawnFlyer.RecomputePosition` |
| The smoothing of a pawn's drawn position (`PawnTweener`) reads real time and frame counts. So does the age of flecks, every sound, tooltips, and the rule that hides a repeated message (`MessagesRepeatAvoider`). | READ (search for real-time reads in `Verse`) |
| The game has `PrefabUtility.SpawnPrefab` and `PocketMapUtility.GeneratePocketMap`. | names READ; what they cost and copy: not read |
| Projectiles, fire spread, plant growth, quests, inspirations, goodwill drift, map temperature, `SteadyEnvironmentEffects`, the UI's structure: not read in this run. | every statement about them below is a GUESS and says so |

## 1. Environment control: the calm profile

**What it is.** A calm profile is a named, versioned list of controls. One call switches a profile on for one game.
The call returns one line per control. A scene names the profile it needs and the exceptions it takes.

**What each control must say.** For every control the answer is one of:
- **HELD**: the thing is stopped at its source. The control also counts each attempt that it stopped.
- **WATCHED**: the thing cannot be stopped (or stopping it would change the game too much), but the control sees it
  the moment it happens and records a breach.
- **COULD NOT ARM**, with the cause. A scene that needs this control does not start.
- **NOT IN THIS PROFILE**.

A control is never reported HELD because a setting was written. It is HELD when the control has read back that its
mechanism is in place (policy §6: "a line in a list is not proof").

**Properties that the census demands** (each answers a measured failure):
1. **One call arms all, one call reports all.** Today the controls are seven separate tools.
2. **Armed again after every load, by the bridge itself.** Today the controls are lost on a load and each agent must
   remember to apply them again.
3. **A breach log.** Every held attempt and every watched event is recorded with its tick, its source and the entities
   involved. Today no control reports anything.
4. **Exceptions by scene.** A scene about a raid allows one incident, named, fired by the scene itself, and nothing
   else. The exception is part of the scene, is written on the receipt, and ends with the run.
5. **Scope.** A control acts on the whole game, on one map, on one station, or on a set of pawns, and says which.
6. **Restore.** When the profile is switched off, every value that it changed returns to what it was. The restore
   reports what it could not put back. The restore also runs when the driver dies (a lease that must be renewed), so
   that a calm profile is never left on in a game by accident.
7. **Never destructive on his game.** A control that destroys or removes (kill the wild animals, end a game condition,
   clear the incident queue) is marked as such. It runs freely in a test game. On his game it is refused unless the
   scene carries the Conductor's or his word.

**The controls.** "Held", "watched" and "unknown" are what I believe the engine allows; the status column says how I
know. The breach watchers (below the table) work whatever the hold mechanism is.

| influence | hold | watch | status of the claim |
|---|---|---|---|
| Incidents that the storyteller schedules | HELD: the engine's own switch | every incident that tries to run is logged | READ |
| Incidents already queued | HELD: the queue is frozen, kept, and given back at restore (not cleared) | each queued incident with its fire tick is listed at arm time | READ that the queue ignores the storyteller switch; freeze: GUESS 85% |
| Incidents from any other caller (quests, scenario parts, signals, sites, rituals, abilities, other mods that use the incident system) | HELD at the one method that all 27 callers use, with the scene's allow list | every attempt logged with its caller | READ for the choke point |
| Pawns that arrive without an incident (a mod that spawns raiders itself, map portals, drop pods) | cannot be held in general | WATCHED: every pawn that appears on the map and is not cast is a breach, with its kind, faction and the tick | GUESS 80% that a spawn tap sees all of them |
| Quests offered and quest scripts that run | new offers HELD (GUESS 70%: offers are incidents) | running quests listed at arm time; their signals WATCHED | not read |
| Weather | HELD by a forced weather, the engine's own route, with "settled" reported only when the rain rate has reached its target | every weather change logged | READ `ForcedWeather`; the settle rule is from the census |
| Game conditions (eclipse, heat wave, toxic fallout) | active ones listed; ended only in a test game (destructive) | every start and end logged | GUESS 80% |
| Outdoor temperature | HELD at a stated value (GUESS 60% that one override point exists) | a drift outside the scene's stated range is a breach | not read |
| Hour and season | SET at prepare, never frozen: jobs need ticks | a run that leaves the scene's stated hour range is a breach | by design (review §5.3) |
| Needs of bystanders | HELD at a comfortable level | none needed | READ (interval); freeze per pawn: GUESS 80% |
| Needs of the cast | SET at prepare. HELD only when the scene asks, and then the receipt says "needs held" | a cast need that crosses a threshold in the window is recorded | by design: a held need changes behaviour |
| Random mental breaks and social fights | HELD: the engine's own switch | each attempt counted | READ |
| Mental states from any other cause | HELD at the one entry method, with the scene's allow list | each attempt logged with its cause | GUESS 85% |
| Inspirations | HELD (GUESS 75%: one entry method) | logged | not read |
| Random diseases | HELD: the engine's own switch | none | READ |
| Wild animal replenishment | HELD at the spawner's tick | each held spawn counted | READ |
| Wild animals already on the map | removed or penned at arm time, in a test game; never with `noAnimals`, which would also destroy the scene's own animals | an animal that comes within reach of a station is a breach | READ for `noAnimals` |
| Visitors, traders, caravans, orbital traders | HELD: they are incidents (orbital traders: GUESS 70%) | arrivals WATCHED by the pawn-arrival watch | partly read |
| Faction relations | SET at prepare | a change of relation in the window is a breach | not read |
| Fire outside the scene's own fire cells | cannot be held in general. The preparer builds a firebreak when the scene declares fire | WATCHED: a fire on a cell that the scene did not declare is a breach; the reassert call puts it out | by design |
| Plant growth and wild plant spawning in a station | HELD (GUESS 60%) | a new plant in a station is a breach | not read |
| Roofs: the home area's automatic roofing, and collapse | stations are placed outside the home area and under no rock roof | a roof change over a station is a breach | READ that auto-roofing runs each tick; the rest by design |
| Autosave, and windows that force a pause (the colony-name dialog, research complete) | autosave HELD; the known dialogs dismissed or pre-answered | any window that opens in the window is logged; a pausing one is a breach | READ for autosave in the tick; dialogs from the census |
| Other mods' spawners and tickers | UNKNOWN by nature. Three answers, cheapest first: a smaller mod list; a named suppressor for one mod, added to the profile the first time that mod spoils a run; a quiet hook that each of OUR mods offers for its own machinery | WATCHED always: a thing of another mod that appears in a station, or changes a station cell, is a breach that names the mod | by design |
| The camera: where it points and how far it is zoomed changes how often things run their interval work | HELD: the update rate is pinned to a stated value for the run (§7) | the pinned rate is on the receipt; a camera move by anyone in the window is logged | READ |
| Processes that need no incident: illness stages, infection, withdrawal, food poisoning, pregnancy and birth, hatching eggs, predators hunting, revenge after a failed taming or a hit, lightning from the weather, explosive things, a short circuit from rain, dormant things waking | not held as a class. Each is removed at prepare where the scene's data allows it (healthy cast, no eggs, no wild predators, a weather with no lightning) | WATCHED by their effects: the taps for damage, fire, explosion, health change, job interruption and arrival (§6) name the cause | from GPT's review §8; routes not read by me |
| A second program driving the same game | HELD: one session per game, tied to the game's driver lock; a call from anyone else is refused | each refused call is a breach of class APPARATUS | by design, from the census |

**A gate on incidents is not a boundary round the scene.** Many things act with no incident at all (the last row but
one). So the profile does not claim isolation because its gates are armed. It claims isolation only for a window in
which the watchers below recorded no breach.

**The breach watchers** are five groups of taps that run for the whole deciding window, whatever was held:
1. **Arrival watch**: a pawn appears on the map that is not cast.
2. **Station watch**: anything that is not cast enters a station or its margin, or a station cell changes (terrain,
   roof, fire, a new thing) by something that is not cast.
3. **Cast watch**: a cast member leaves its station, dies, is downed, changes faction, enters a mental state, takes
   a job that the scene did not list as expected, or takes damage or a health change from a source that is not cast.
4. **Sky watch**: weather, game condition, temperature range, hour range.
5. **Game watch**: an error in the log, a window opened, a setting changed, time speed or pause changed by someone
   else, a refused foreign call.

Each breach names what happened in the words of the contract: "a non-cast pawn (wild boar, no faction) entered the
station margin at tick 412, before the opportunity was decided". The run's classifier uses exactly these records
(§7).

**What stays unknown until the engine is read**: temperature override, plant growth hold, quest offers, inspirations,
orbital traders, goodwill drift, and whether the spawn tap sees every arrival route.

- **For:** every scene; it makes ENVIRONMENT FAULT decidable by a program (policy §2 asks for "the record shows").
- **It works when:** in a test game with the profile on, a planted incident, a planted wild animal at the station edge
  and a planted weather change each produce one breach record that names them, and a load in the middle changes
  nothing in the status.
- **Value / effort:** high / medium.

## 2. Scene preparation

**Stations.** A test map is cut into stations. A scene asks for a station by what it needs: a size, a margin (the
blast radius, the flee radius, the reach of a shade strip), the ground (open, a terrain, no roof, no water within N),
and the distance from the map edge. The allocator gives a free one or says why none fits. A station records what was
put in it, so that it can be cleaned and so that leftovers are known and not guessed.

**Clean.** One call returns a station to bare ground: things, pawns, corpses, filth, gas, snow, fire, blueprints,
designations, zones, areas, reservations, temporary terrain, roof, and the per-scene state of our own mods (through
each mod's reset hook). The clean ends with a read-back. A station that could not be cleaned is retired for the
session and reported, never reused in silence. Census: leftovers and bystanders are rank 7.

**Build.** One call builds the start state from the scene's data: terrain, structures (with stuff and health), things
(with stack counts and forbidden state), and the cast. For a pawn the data can fix: kind, faction, age, gender, body
and exact health (each injury and its part), gear and weapon, skills, traits, work types that must be enabled and
their priorities, needs, position, facing, drafted or not, and its starting job, duty or group.
Every write is read back from the game, and the reply gives what the game holds, never an echo of the request. The
census has a spawn tool that replaced the asked kind by a vanilla colonist in 4 of 80 spawns and still said 5 of 5.

**Capability asserts.** The scene states what each actor must be able to do: "can do Mining", "has a ranged attack",
"can reach the pit rim", "is hostile to the colony", "is awake and not downed". The preparer checks these before the
run. A failed assert ends the run as APPARATUS FAULT before a tick is spent. Census: "a staged actor lacks what the
scene assumed", 16 records.

**Fixtures.** A named piece that many scenes use (a 4 m pit with a lid, a powered line with a span, a pen) is written
once and called by name with parameters. A mod owns its fixtures.

**The map.** A test map kind is a named recipe with fixed properties: flat open ground of one terrain, a temperate
tile, no ruins, ponds, geysers or rock roofs, a known size. It is made once per mod list and kept as a fixture save.
This is developer tooling on disposable saves; it is not a worldgen feature and makes no planet.
A scene whose subject is map-wide (weather, sun, a sand state) asks for **a second small map** as its control arm
(the engine has pocket maps; their cost is not read).

**Isolation of one scene from the next on a shared map.** Four rules together:
- stations do not overlap, margins included;
- every bystander pawn of the test colony is kept out of every station (the "fence": §5, hold);
- a scene's things are marked so that no bystander may haul, use, eat or reserve them;
- map-wide state that a scene changes (weather, a setting, a faction relation) is written on the station record and
  put back at clean.

**The start state twin** (the owner's request of 2026-11-23). When a scene's aftermath is kept for his walk, the
preparer builds the same start state a second time in the neighbouring station, at the moment the walk save is
written, while the game is paused. Both stations get a sign that names the scene and says START or AFTER. Because the
twin is built at save time and not before the run, nothing has to hold it still while the scene runs. Its pawns are
held in place and kept comfortable, so that it is still a start state when he unpauses to look.

**Speed target** `[guess ~70% reachable; today one batched call wrote 2,601 terrain cells]`: clean and build of a
station of up to 400 cells and 10 pawns in one call and under 200 ms.

- **For:** every scene; it makes "a valid opportunity on demand" possible, which is what makes a scene kind A.
- **It works when:** the same scene data built twice gives two stations whose read-back digests are equal, and a
  scene run after a deliberately dirty scene (corpses, a reservation, a fire) passes exactly as on a fresh map.
- **Value / effort:** high / medium (the twin: medium / low once build exists).

## 3. Reassert the environment

One call, **reassert**, checks every declared condition and repairs what drifted. The conditions are: the calm
profile's controls, the map-wide state that the session set (hour window, weather, settings, relations), the fence
round every station, the health of the standing test colony (fed, rested, sane, alive), and the bridge's own state
(the log is counting, the probes are armed, the session owns the game).

The reply has three lists: **held** (a count), **repaired** (what had drifted, and what was done), **could not
repair** (with the cause). Only the third list stops a scene.

The profile is a statement of the wanted state, so reassert is a comparison of wanted against actual. It is safe to
call at any time and any number of times.

It runs by itself: when the profile is armed, after every load, before every scene run, and between repeats.

**Cost budget** `[targets; nothing is measured yet]`: one call; under 30 ms when nothing drifted; under 150 ms with
repairs; zero tool calls from the scene's author, who never calls it by hand. For scale, one call today is 4 to 17 ms
and a repeat of the present re-calm steps is about ten calls.

- **For:** repeats of kind B and C; long visits; every scene after a load.
- **It works when:** after a deliberate drift (weather changed, a colonist starved to 10%, the profile's incident gate
  removed, a fire lit beside a station) one reassert reports each under "repaired" and a second reassert reports none.
- **Value / effort:** high / low, once §1 and §2 exist.

## 4. Confounder sweep

A sweep looks for anything that could spoil a scene. It runs **before** the act (and can refuse to start), **during**
the window (the breach watchers of §1), and **after** the end (what drifted). The before-sweep is the new part.

It looks at these, each for the scene's own window of ticks:

| where | what it looks for |
|---|---|
| pawns | every non-cast pawn that could reach the station within the window at its speed; its job and its job's targets; hostile or predator status; a group that it belongs to |
| the cast | a health state that will act in the window (bleeding, an illness stage, a labour, a withdrawal); a need that will cross a threshold; a break risk; a disabled work type; a job that is not the expected one; a group or duty left from before |
| reservations and claims | a reservation on a cast thing or a station cell by a non-cast pawn; designations, blueprints, zones, stockpiles, growing zones, the home area and its roofing over the station |
| the schedule | incidents queued to fire in the window; quests with a part due; a weather change due; an autosave due; a game condition ending or starting |
| the sky | weather and rain rate not settled; temperature and hour outside the scene's range; fire anywhere on the map |
| the station | a thing of a mod that the scene does not name; fog; a roof that can collapse; water, a geyser or a slope where the scene assumes open ground; the map edge inside the margin |
| the game | an open window, float menu or armed designator; a pause or a forced speed that the scene did not set; errors in the log since the profile was armed; a log close to its cap; a second driver |
| identity | a loaded assembly whose file on disk has changed since the game loaded it; a mod list that is not the one the scene names |

Each finding is written in the contract's words and carries one of three weights:
- **BLOCKS**: the valid opportunity cannot hold. The sweep repairs it if the profile says how (move the bystander,
  clear the reservation), or the run ends as APPARATUS FAULT before the act, with the finding.
- **RISK**: it may spoil the run. It goes on the receipt, and the classifier may use it if the opportunity fails.
- **NOTE**: recorded only.

- **For:** it turns "the scene failed for a site reason" from a diagnosis after the run into a refusal before it; it
  gives the classifier the earlier state that it needs to call a cause external (review §3).
- **It works when:** a planted confounder of each row of the table is named by the sweep with the right weight, and a
  clean station gives an empty BLOCKS list.
- **Value / effort:** high / medium.

## 5. Guiding and forcing, by the Minimum Force ladder

The bridge offers every level of force, refuses none, and **records the level used for each actor** on the receipt,
next to the scene's own line "decisions left to the mod". The ladder, from least force to most:

| level | what the bridge does | what it steps past (outside the scene's evidence) |
|---|---|---|
| **0 NATURAL** | arranges the world and waits | nothing. Cost: the opportunity may never come (1 of 18 in the census) |
| **1 LURE** | places bait: a target, food, a prisoner, a thing of value; or shapes the ground so that one route is cheapest | the actor's free choice among many targets and routes; danger and congestion that a real base has |
| **2 MOTIVE** | sets what the actor wants: a duty or a group with a goal, hostility, a need level, a work priority | how the actor came to want it (the raid's own strategy, the need's own decay) |
| **3 ORDER, through the giver** | asks the same job-giver or work-giver that a player's order or the AI would use to make the job for this actor and this target, and starts the job only if the giver makes it | when and whether the actor would have chosen this job by itself. The giver's own eligibility checks still run, ours included |
| **4 ORDER, raw** | builds the job and starts it | the giver and every eligibility check, vanilla and ours. The job may be one that no real game state can produce: the receipt marks this "not shown reachable in play" |
| **5 PATH** | makes the actor walk a given route, cell by cell, by real movement | route choice and path cost, ours included. Entering each cell is still real, so entry effects still run |
| **6 PLACE** | puts the actor on a cell at once | movement, entry and exit effects, doors, falling in. Anything that our mod does when a pawn ENTERS a cell did not run |
| **7 STATE WRITE** | writes inner state: start flying, set an illness stage, set a fill level, down a pawn | the whole cause of that state |

**Hold in place** is a separate axis, because most scenes need it for someone:
- **a wait job of the game** (the pawn stands as a drafted pawn stands): steps past the pawn's job choice; the pawn
  still reacts as the game makes a waiting pawn react. Note from the census: a drafted idle pawn is undrafted by the
  game after 10,000 ticks.
- **a pin** (the pawn cannot leave the cell or the rectangle, whatever its job says): steps past movement and fleeing.
- **a fence** (bystanders may do anything except enter a station or touch cast things): steps past nothing that the
  scene tests. This is the default for every bystander.
Every hold reports a pawn that left anyway, as a breach.

**Per kind of actor**, what differs:

| actor | what the levels need |
|---|---|
| colonist | level 3 is the player's order (the float menu's choice for that target) or the work giver; a work type must be enabled first (capability assert) |
| enemy humanlike | does nothing without a group and a duty (census: a hostile with no group stood for 1,260 ticks). Level 2 gives the group and duty that a raid would give; a raid fired through its own incident is level 0 or 1 |
| animal | wild or tame; no draft; level 2 is hunger, a predator's prey, a manhunter state; level 3 is the training or handling job |
| mechanoid | an enemy needs a group as a raider does; a player's needs its overseer and work mode set at prepare |
| droid of our mods | not designed in detail: Droidworks' experience is not yet dictated. The same ladder applies through whatever think tree a droid has |

A scene that tests a decision of our mod sets its entry point **before** that decision. The pit rescue has two
scenes: "an ordered rescue completes" (level 3, kind A) and "a raider with a downed comrade in a pit chooses to
rescue" (level 2: both pawns in a raid group beside the pit, kind A if the choice is certain by design, else kind B).

- **For:** making the valid opportunity happen on demand at the least force (census rank 1); the receipt line that
  the policy's §7 asks for.
- **It works when:** for one actor and one target, each level 1 to 7 produces the movement or state it names, the
  receipt shows that level, and a level-3 order to an actor that the giver refuses returns the giver's refusal and
  starts nothing.
- **Value / effort:** high / medium (levels 4 to 7 mostly exist as tools today; 2, 3 and the fence are the new work).

## 6. Scripted in-game telemetry

**What it is.** The scene declares what to observe. The game side records it on the simulation thread while the scene
runs, with tick stamps and aliases, into a bounded trace that outlives a crash. The scene's contract is then decided
from that trace by a program.

### Three shapes, and the one picked

| shape | what it buys | what it costs |
|---|---|---|
| **A. Declared probes from a fixed vocabulary.** The scene names values and events; the bridge knows how to read each. | Safe in any game. Fast. Every probe has a schema, so a checker can be written against it and validated once. Nothing an agent wrote runs inside the game. | Every new kind of value needs bridge work, unless values can be reached by a path (below). |
| **B. Sent programs.** The agent sends source code or a script that runs inside the game. | Any state, any logic, at once. | A program written during a run is a checker that nobody validated and that no receipt can name by version. An exception inside it breaks the run it watches. It can change the game. On his game it is a risk. The present bridge already has a restricted script front end; a general one needs a compiler or interpreter inside the game. |
| **C. Trace points inside each mod.** Our mods emit their own events ("eligibility refused because X") through a small shared interface. | Sees the reasons inside a decision, which no outside probe can. | "The mod said it worked" is evidence of a branch, never of the result (review §3). Third-party mods have none. It adds code to shipped mods. |

**Picked: A as the base, with value paths; C as a second channel that is labelled; B only as named probe plug-ins.**
- **Value paths** remove most of A's cost. A track names a value by a path from an alias: `carrier.health.summary`,
  `raider1.job.def`, `pit.comp(PitComp).fillLitres`, `hawk.flight.state`. The bridge resolves the path once when the
  probe is armed (and refuses a path that does not resolve, by name), then reads it every tick at the cost of a field
  read. A new mod's values need no bridge work.
- **Mod trace points (C)** are recorded in the same trace under their own type, "mod says". A success condition may
  use them only together with a condition on game state. The checker language enforces this.
- **Probe plug-ins (B, tamed)** cover what paths cannot: a computed value (the drawn curve of a cord, the litres in a
  connected body of liquid). A plug-in is compiled code with a name and a version, shipped with the mod's tests or
  with the bridge, built and reviewed like any code, and listed on the receipt. No source code is sent at run time.
  Reason: a checker must be something that a planted fault has been seen to turn red; a program written inside the
  run cannot be.

GPT's review agreed with one observer after the whole tick and warned against reflection on hot paths; value paths are
resolved to direct reads at arm time for that reason.

### What a trace holds

- **Tracks.** A value sampled after every complete tick (or every N ticks), stored only when it changes. About 20
  values on 10 aliases is the normal size.
- **Taps.** An event caught where it happens, not by polling. Each record has the tick, the phase inside the tick,
  a sequence number, the aliases involved, and the fields of that event. The base list:

| tap | fields that matter | note from the review |
|---|---|---|
| damage | victim, amount asked, amount dealt, kind, part, instigator, weapon | asked and dealt are different facts (census: "success" with 0 dealt) |
| death, downing, destruction, despawn, spawn | who, where, the mode (killed, vanished, moved to a container, loaded) | position is taken before the removal |
| job start, job end | pawn, old job, new job, end condition, who gave it (think tree, order, queue) | several can happen in one tick |
| toil change | pawn, toil index and name | answers "which step stalled" (census) |
| reservation made, refused, released | claimant, target, kind | include the bulk releases |
| path request, path result, path failed | pawn, destination, cost, found or not | |
| cell entered | pawn, cell | the trigger of every pit and trap |
| mental state attempt and start, inspiration | pawn, state, cause, result | an attempt is not a start |
| incident attempt | worker, target, caller, held or run, result | |
| hediff added, removed, stage changed | pawn, hediff, part, severity | |
| fire started, spread, went out; explosion started, cell affected | cell, source, instigator | answers "what lit it" |
| weather, game condition, temperature range, roof, terrain change | old, new, cell | |
| letter, message, alert | type, label, text, targets, before any rule that hides repeats | the hide rule reads real time (READ) |
| window opened, closed | class, title | opening is not drawing (§6, UI) |
| sound asked, effect asked (fleck, mote, effecter) | def, cell | asked is not heard or seen |
| error, warning, exception | text, stack, phase, the alias whose tick threw | |
| mod says | mod, name, fields | never enough alone |

- **Marks.** The runner writes a mark at each phase change (prepared, opportunity decided, act, end).
- **A heartbeat.** Each armed probe writes one record that proves it is alive, and the runner fires one synthetic
  event through each tap at arm time. "No event" then means that nothing happened, and not that the probe was blind.
  A tap whose synthetic event did not arrive is COULD NOT ARM. (Review §4: "no tripwire fired is uninformative if it
  never armed".) Known ways a tap goes blind, to test at arm time: the method was inlined, a subclass overrides it
  without calling the base, another mod's patch skips it.

### Bounds, and surviving the failure it watches

- Each probe has a stated budget of records and bytes. The scene chooses, per probe, "keep the newest" or "keep the
  oldest and stop". A probe that dropped records says how many and from which tick. If the checker needed a dropped
  span, the run is COULD NOT LOOK, never a pass or a fail.
- The trace is written out in small batches to a file while the scene runs, not only at the end. When the game throws
  its first exception, stalls, or is about to be stopped, the trace so far is already on disk. A program outside the
  game can read it after a crash.
- Aliases are stable. An alias stays bound to its thing through a save and a load inside one scene. (Whether the
  game's own thing ids survive a load is disputed between a census record and the review; the alias is the contract,
  and the binding mechanism is the second designer's.)

### The hard cases

**A flyer's flight, and the flapping, frame by frame.** The owner's ruling stands: no agent hunts a flight with
screenshots. This design makes the flapping bird testable in three layers, and the first two need no image.
1. **Flight as state, every tick** `[READ]`. A track on the flight tracker gives, per tick: the state (grounded,
   taking off, flying, landing), the lerp tick, the height factor, the flying ticks left, the cooldown. A checker
   asserts the whole flight: a takeoff of 50 ticks, a height that rises along its curve, flight no longer than the
   stat allows, a landing of 50 ticks, a cooldown, the forced-landing jump that the flight reference predicts.
2. **The flap as draw intent, every tick.** The animation clock is a function of game ticks `[READ]`. Which picture
   the animation shows at that clock value is decided by the animation's own data and worker, which I did not read,
   and GPT could not confirm a formula. So the probe does not compute the frame. It asks the renderer's own resolver,
   for this pawn at this tick and facing, which graphic and which transform it would draw, and records that
   (the "draw intent" below). A checker asserts: while flying, the pictures cycle through every frame of the flip-book
   in order, each held for the declared ticks; each facing uses its own set; the west view is the mirrored east view;
   on landing the grounded picture returns. That is a flapping test, tick by tick, repeatable, with no screenshot.
3. **The flap as pixels, for his eye only.** A filmstrip: one image that tiles N consecutive ticks of the flyer,
   rendered tick by tick by the program (§6, pixels). It is made after layers 1 and 2 pass, for the owner or an art
   judge to look at once. It changes what his ruling of 2026-09-25 forbids, so it is an open question for him and is
   not assumed.
A takeoff is a random chance at each job start `[READ]`. Least force: give the animal many ordinary job starts and
count takeoffs (level 2, kind B, and the rate itself is checked offline). Most force: call the tracker's own start
(level 7), which tests the flight and not the trigger.

**A thing in mid-air during a throw.** A vanilla flyer computes its position from its own tick count `[READ]`, so a
track gives the exact arc: ground position, height, progress, per tick, and a tap gives the landing cell and what the
landing did. Our Knockback's thrown things use their own class (not read): the same track works through value paths,
or through one plug-in if the arc is computed at draw time only. Projectiles: not read; GUESS 80% the same holds.

**A one-tick event.** Taps record at the moment of the event, and the contract's conditions are evaluated inside the
game after every tick. Nothing polls. A mental state that lasts 50 ticks, a shock, a fall, a rebound cannot fall
between two reads.

**A draw-time-only effect (what is drawn, not what the state says).** Three separate facts, each its own probe
(the review's division, which I adopt):
1. **Draw intent**: what the game's drawing code resolves for a named thing at this tick: the graphic and texture,
   the position with its offset, the height layer, the rotation, the scale, the colour. Cheap, exact, tick-true for
   everything except the smoothing of a moving pawn's position, which reads real time `[READ]`.
2. **Draw submitted**: that the drawing code did hand that mesh and material to the engine in this frame. Needed for
   "the flame was not drawn" (census). A static thing is drawn into a shared mesh when its map section is rebuilt, not
   every frame, so its probe sits there. Attribution to a thing must be carried from the caller; the engine call
   itself does not name the thing (review §6).
3. **Pixels**: an image of a rectangle of the map at a fixed zoom, hour and light, without UI, taken by the program at
   a stated tick. Requirements: it does not move the player's camera where he can see it and never needs focus; the
   smoothing of moving pawns is settled first; the file name is unique; the receipt records the tick and frame. The
   known prior art moves the player's camera for an instant and puts it back (review §7), so "never moves his camera"
   is either new work or is relaxed to "restores it within the same frame": an open question for the second designer.
   Flecks, motes and sounds age by real time `[READ]`: their creation is a tick-true tap; their look is pixels only.

**A UI window's content.** The game's windows are drawn by code every frame; there is no stored tree of widgets
(GUESS 90%). So the probe records, during one frame's drawing of a named window, every text, button, check box and
slider that the window drew, with its rectangle and state: a **window transcript**. A scene asserts on the transcript
("the trade window lists item X at price Y", "the settings page has a switch labelled Z, and it is on") and can act on
an entry (press this button) through the same names. A tooltip appears after a real-time delay `[READ]`; the
transcript can ask for a tooltip's text directly.

**Sound.** A tap records that a sound was asked for: which, where, at which tick. Whether it was heard is not
designed (testing horizon).

**Frame time.** Not a probe of state. The runner offers a real-time mode (§7) and reports frame and tick durations;
a quiet machine and a like-for-like comparison stay the method's business (testing horizon).

- **For:** it makes SUCCESS readable from game state (policy §1), makes COULD NOT LOOK a real, separate outcome, and
  gives a hunt (kind C) its trace. Census ranks 2, 5 and 10.
- **It works when:** in one run a planted 1-tick event is in the trace with its tick; a probe with a path that does
  not resolve is refused by name; a deliberately crashed game leaves a readable trace up to the crash; a tap that was
  made blind on purpose is reported COULD NOT ARM; and for a vanilla flying animal the per-tick record shows every
  flip-book frame in order.
- **Value / effort:** high / high (tracks and the base taps: high / medium; draw intent and the window transcript:
  high / medium; draw submitted: medium / high; pixels and the filmstrip: medium / medium).

## 7. Atomic scene execution

**One call runs one scene and returns one receipt.** Inside the call, in this order:

| phase | what happens | how it can end the run |
|---|---|---|
| admit | the session owns this game; the loaded build and mod list are what the scene names; the scene's data is valid against the loaded defs | APPARATUS FAULT (or COULD NOT LOOK if identity cannot be read) |
| calm | reassert (§3) | APPARATUS FAULT if a needed control cannot arm |
| prepare | station, clean, build, read-back, capability asserts (§2) | APPARATUS FAULT |
| sweep | the before-sweep (§4) | APPARATUS FAULT on a BLOCKS finding that cannot be repaired |
| arm | probes on, heartbeat seen (§6); the random state and a start digest recorded (§8) | COULD NOT LOOK if a needed probe cannot arm |
| act | the scene's timeline: each step is tied to a tick or to a condition ("at +0 order the rescue", "when raider1 is on the lid, drop the lid") | APPARATUS FAULT if a step is refused |
| run | the game side lets time pass and, after every tick, evaluates the opportunity, the forbidden effects, the success and the end | see the classifier |
| settle | the after-sweep; the trace closed; the outcome decided | |
| leave | the game is paused; the station is cleaned, or kept (with its twin) if the scene says "keep on this outcome" | |

**Time inside the run belongs to the game side.** The caller never steps ticks. Two modes:
- **burst**: as many ticks as fit in a work budget per frame, with drawing reduced to what the game needs to stay
  responsive. For every scene that reads state.
- **real time**: normal speed with normal drawing. For frame-time scenes, pixel captures and anything he watches.

**The tick driver is a real component, not a loop** `[READ, and corrected by GPT's review]`. Calling the game's tick
method in a bare loop is not the same as play, for four reasons that I confirmed in the code:
1. Each map does simulation work once per **frame**, outside the tick: region and room rebuilding, power-net updates,
   the glow grid, a per-frame update of pawn groups, and "post-tick visuals" (`Map.MapUpdate`). The driver must do
   that work between ticks as play does.
2. **How often a thing runs its interval work depends on the camera** (`GenTicks.GetCameraUpdateRate`): every 15
   ticks when the thing is on a map that is not shown or is outside the camera's view, and every (zoom level + 1)
   ticks when it is in view. Animals always use 15. So today the same scene can run differently when the camera
   points elsewhere. No record in the census names this influence; it is new. The driver **pins the update rate** to
   a declared value for the whole run (default: the rate of a thing in view at the closest zoom, which is what a
   player watching would get), and writes it on the receipt.
3. Path computation runs on worker threads and reads live map state; the Multiplayer mod had to force its completion
   before pawns tick to remove a race (review §1). The driver does the same or reports that it could not.
4. Long events (a load), windows and input are served per frame. The driver stops ticking while one is pending, and
   honours the game's own stop requests (pause on error, a forced pause).
The driver is never entered from inside a tick.

**Long scenes.** A scene of days cannot hold a caller's connection open. The call starts a run and returns a handle;
the deciding still happens entirely inside the game; the receipt is written to disk when the run ends and can be
fetched by anyone who has the handle. A caller that dies loses nothing.

**The classifier.** The outcome is decided by this table, in this order. It is the policy's seven outcomes (§2) made
mechanical; the two rules in bold are the policy's own.

| # | condition, from the record | outcome |
|---|---|---|
| 1 | **a forbidden effect was observed** (in any phase, even in a spoiled run) | MOD FAILURE |
| 2 | the game died or stalled; or a probe that a condition needs was blind or dropped records in the span it needs; or identity could not be read | COULD NOT LOOK |
| 3 | prepare, a capability assert, an act step, the tick driver or the session failed; or a foreign call touched the game | APPARATUS FAULT |
| 4 | the valid opportunity failed, and a breach record or a sweep finding shows a cause that (a) came before the failure, (b) names an entity that is neither cast nor a thing of the mod under test, and (c) is of a kind that the contract lists as external | ENVIRONMENT FAULT |
| 5 | **the valid opportunity failed and row 4 does not hold** (the mod could have spoiled it, or nobody knows) | UNRESOLVED |
| 6 | the opportunity held to the end and success is true | SUCCESS |
| 7 | the opportunity held, success is false, and the contract declares this miss allowed (a random result by design) | RANDOM MISS |
| 8 | the opportunity held, success is false, kind A | MOD FAILURE |
| 9 | the opportunity held, success is false, kind B or C, no allowed miss declared | UNRESOLVED |

Notes. The opportunity is not one moment: a contract can state conditions "at the act", "throughout the window" and
"at each of these steps" (review §3: a rescue has several boundaries). The receipt always gives the **first** failed
condition with the values that were observed, so that an agent reads only what a program could not decide.

- **For:** every scene and every outcome of the policy; it removes the gap between calls, which is the cause behind
  census ranks 2, 5 and 9.
- **It works when:** a scene whose deciding event lasts one tick gives the same outcome in ten runs out of ten in
  burst mode; a planted fault of each row of the classifier table gives that row's outcome; and the game is paused
  when the call returns, in every one of those cases.
- **Value / effort:** high / high. It is the keystone.

## 8. Fast repeats for kind B and kind C

Kind B needs several independent tries at low cost. Kind C needs many exposures, and, once the fault shows, the same
moment again.

### Shapes

| shape | what it buys | what it costs and what it cannot do |
|---|---|---|
| **1. Save and reload for each repeat** | The most complete return to a start state that the game offers. Works for map-wide state. | A reload rebuilds the whole game (seconds on a test list, minutes on the full list). It is not a process snapshot: static state of mods survives, loading itself draws random numbers, a warm run and a reloaded run start differently (review §3). The global random state is not in the save `[GUESS 85%]`, so each reload is a new sample unless the state is put back. |
| **2. Stamp again**: clean the station and build the start state again from the scene's data (§2) | Milliseconds. Each stamp is an honest new sample. What it resets is exactly what the contract calls the valid opportunity. | It does not reset what is outside the scene's data: world pawns, quests, relations, memories, a mod's static counters, the id allocator (review §4). So it needs **reset verification**: a digest of the station and of the declared mod state, compared with the first stamp. |
| **3. Copies side by side**: N stations, one stretch of ticks | N samples for the price of one advance. The owner already reviews matrices. | Copies share one random stream, one weather, one room and region graph, one set of map-wide lists. A map-wide event spoils all of them at once. The copies are a **cluster**, not N independent runs (review §4). |
| **4. A snapshot of a region in memory** (write a rectangle's things out and read them back) | Would be exact inside the rectangle and fast. | A rectangle is not a closed set of objects: jobs, relations, gear, owners and targets cross its edge (review §4). No engine feature does this for arbitrary content. High effort, high risk. |
| **5. A fresh small map per scene** | A clean spatial boundary; a control arm for map-wide state. | Still one world, one process, one random stream. The cost to make and to remove a pocket map with 300 mods' components is unknown. |
| **6. Capture and replay of the random state** | The same draws again, for diagnosis. | Only meaningful on top of shape 1, and only if everything that draws numbers is in the same state. |

### Picked

- **The workhorse for kinds B and C: stamp again (2), in copies side by side (3) when the scene allows it.** These are
  cheap and are real samples. The scene states how far apart copies must stand (its margin) and whether it may share a
  map with others at all (a map-wide scene may not).
- **For diagnosis in a hunt: a keeper save plus the random state (1 + 6), with a divergence finder.** When a fault
  shows, the runner writes a save of the failing run's START (taken at arm time, cheap: a save of 14 MB took 0.5 s)
  together with the random state at the act. Replaying is: reload, wait for the same settle point, put the random
  state back, run the same timeline on the same ticks.
- **For map-wide scenes: a fresh small map (5)** as the control arm, if its cost proves acceptable; else arms in
  sequence.
- **Not designed: the region snapshot (4).** See the testing horizon.

### How a replay is told apart from a new sample

Every run records a **sample identity**: the random state at the act, and a digest of the start state. During the
run a **trajectory fingerprint** is recorded per tick: how many random numbers were drawn in that tick (the stream's
counter makes this a subtraction `[READ]`), and the positions and jobs of the cast.
- Two runs with the same sample identity and the same fingerprint on every tick are one sample, counted once.
- A replay whose fingerprint leaves the original at tick T is reported as "diverged at tick T, first difference:
  <which value>". That report is itself the diagnosis of what is not deterministic, and it is how the replay rate
  gets measured instead of promised.
- Repeats are counted three ways, kept apart: launches, valid opportunities, exposures to the suspected trigger
  (review §3 and §4). A cluster of side-by-side copies is marked as one cluster.
- No scene may put the random state back to search for the result it wants and then call that a rate (review §5.7).

### What determinism can honestly be promised

| claim | status |
|---|---|
| Across process starts or machines, the same seed gives the same run | **Not promised.** The stream is seeded from the clock at start `[READ]`; nothing here changes that |
| In one process, on a test list of about 13 to 30 mods: reload, settle, restore the random state, same timeline, pinned update rate, driver that completes path work before pawns tick. A window of about 2,000 ticks replays exactly | **Unknown; GUESS 50%.** Nobody has measured it here (census: looked, found none). The divergence finder measures it in the first week |
| The same on the full list of about 300 mods | **Unknown; GUESS 20%.** Any mod with its own random source, a static cache, a thread or a real-time read breaks it. GPT found no published replay rate for any large list |
| A stamped scene behaves as the same scene on a fresh map | **To be shown per scene** by reset verification; expected for scenes whose mods offer a reset hook |

Sources of difference that are confirmed: the random state is not saved and loading draws numbers; update rates depend
on the camera `[READ]`; frame-level work between ticks `[READ]`; path jobs reading live state (review, from the
Multiplayer source); real-time reads in smoothing, flecks, sound, repeated-message hiding `[READ]`; static state of
mods across a load. Whether iteration order of hashed collections differs after a reload: GUESS 40% that it matters
in one process.

### High tick rate with no rendering, and long processes

Burst mode (§7) gives the highest tick rate the simulation allows. On the full list the cost of a tick itself is the
limit (the census has about 50 ticks per second by stepped calls; the game's own fastest speed is called "CPU-bound"
there). What burst mode gains on each list is **unmeasured**; my guess is a large gain on a test list and a small one
on the full list `[guess ~60%]`.

A process of days is not made faster by moving the clock: a clock jump simulates nothing and fires every timer that
compares against the clock (census). The receipt carries a **time compression** line with one of: none; a rate setting
of the mod under test, named with its factor; an engine switch, named (the plant-growth switch exists `[READ]`); a
clock jump. A scene that used compression proves the compressed behaviour, and says so.

- **For:** kind B budgets that are affordable; kind C hunts; the count rules of the policy. Census rank 1 and the
  "same build, different result" row.
- **It works when:** 20 stamped copies of one kind B scene on a test list finish in less wall time than 3 single
  runs do today; a planted cross-talk between two copies (one copy's pawn reserving the other's thing) is caught by a
  breach; and a replay of a keeper save either matches its fingerprint or names its first diverging tick.
- **Value / effort:** stamp and copies: high / low after §2 and §7. Keeper save, random state and divergence finder:
  medium / medium. Fresh small map: medium / unknown.

## 9. Receipts and identity

A receipt is the one record of a run. A program reads it; a person can read its first lines. It holds:

| part | content |
|---|---|
| verdict | the outcome (one of seven); the first failed condition with observed values; the classifier row that decided |
| counts | launches, valid opportunities, exposures; the cluster id for side-by-side copies; the sample identity; replay of which sample, if any |
| what ran | scene id and the hash of its data; contract (checker) hash; kind and tag evidence; the force level per actor and the "decisions left to the mod" line; time compression |
| what the game had loaded | for every loaded assembly: name, version, and the hash of the file **as it was when the game loaded it**, with a flag if the file on disk has changed since. The active mod list in order, with package ids. The DLC. The game version. The settings of the mods that the scene names, and every setting the run changed, before and after |
| the apparatus | bridge and tick-driver version; the probe plug-ins with versions; the calm profile's name and version, the status of every control, the scene's exceptions; the pinned update rate; burst or real time |
| the place | the game by name (ArchBig, ArchSmall, Steve1, Steve2); the save; the map (kind, size, biome, tile); the station; tick range; wall time |
| evidence | the breach list; the sweep findings; records lost per probe; the path and hash of the trace; the keeper save, if one was written |
| reach | which defs and assemblies the cast and the probes touched. A program can use this to decide which scenes a later change touches (policy §8, and the rule "only the checks that the change touches run again") |

"The build the game had loaded, not only the build on disk" is a rule of the policy (§8). Today it is checked for our
own mod only; the census has a whole visit run on stale DLLs of two other mods that no gate saw.

- **For:** verdicts that keep (policy §8); census rank 3; the hunt record that policy §5 asks for.
- **It works when:** a DLL replaced on disk while the game runs is flagged on the next receipt; and two receipts of
  the same scene on different builds differ in exactly the hash that changed.
- **Value / effort:** high / low.

## 10. Errors and safety

**The first exception.** An error tap sits where the game logs. It keeps the first N errors and warnings of the
session and of each run, each with tick, phase, stack and the thing whose tick threw. It does not depend on the
game's log window, which stops at 10,000 messages `[READ]`, nor on the bridge's journal, which keeps the last 1,000.
It re-arms the game's log when the cap is reached and says that it did. It also listens to the engine's own log
channel for errors that never reach the game's log (GUESS 85% that one exists). The game logs some errors once and
then stays silent `[READ]`; the tap counts a silenced repeat as "seen again" where it can, and says where it cannot.

**A broken game is detected, reported, and not left running.** The game side writes a heartbeat (tick count, frame
count, wall clock, phase). A watcher outside the game reads it. States, each told apart: ticking; paused; frames
stopped; an exception on every frame; stuck in a load; at the main menu; no map; process gone. On a broken state the
watcher saves the last words (the trace so far, the first exception, the tail of the game's log), ends the run as
COULD NOT LOOK or APPARATUS FAULT with the state's name, and stops a test game. For his game it reports and follows
the rules of `./game` (an open question: whether a broken ArchBig is stopped while his hold is on).
The census has 29 blind repeats of a job on a game that had died, of which 16 died again: a run never starts on a game
whose last state was broken until someone has cleared that state.

**The owner's game.**
- The bridge never gives the game window focus and never makes it fullscreen.
- The bridge never moves the camera that he sees, or restores it in the same frame (§6, pixels).
- **Sitting mode.** When he sits down to look (his hold on ArchBig, or a walk), the session is in sitting mode: no
  call advances time, unpauses, changes speed, opens a window or moves the camera, unless the call carries his ask.
  His presence is not sensed (a rule of this repo); sitting mode is a state that his hold or the Conductor sets.
- Every scene run returns the game paused.
- A save of his is never written over. Test saves live under their own names; a write to a canonical save is refused.

**Calls tell the truth** (each line answers a census record):
- An unknown parameter is an error, never dropped in silence.
- A changing call returns what the game holds after the call, read back, never the request repeated.
- Every reply keeps four answers apart: zero, none found, could not look, failed (with its cause).
- A window that takes the input or forces a pause is detected before and after each call and named.
- One session drives one game. A second driver is refused and recorded.

**What a run changed is put back.** Settings, switches, the calm profile, the speed, the camera of a test game: each
change is a debt written to disk under the run's id. The debt is repaid at the end of the run, when the run's lease
runs out, and at the next start of the bridge. A debt is repaid only by its own run or after that run is known dead.
(The census has a restore replayed by another process in the middle of the run that owned it.)

- **For:** COULD NOT LOOK and APPARATUS FAULT as true outcomes; census ranks 2 and 6; his game.
- **It works when:** a planted exception at tick T is the first error on the receipt with tick T; a game killed in
  mid-run gives a receipt with the state "process gone" and a readable trace; in sitting mode a call that would
  advance time is refused by name; and a run killed half way leaves no changed setting after the next bridge start.
- **Value / effort:** high / medium.

## 11. Authoring cost and the scene language

**The aim:** a mod builder writes a scene and its contract in minutes, in one short file, and never learns the
bridge.

**A scene file** is data with these parts. Only `claim`, `cast`, `act`, `success` and `end` are always needed; the
rest have defaults.

```
scene:    an id and a title
kind:     A (default) | B | C, with the tag's evidence for B and C, and the budget of repeats
needs:    mods, map kind, station size and margin, shares a map or not
calm:     profile name (default: standard), and exceptions
stage:    terrain, structures, things; fixtures by name
cast:     alias -> what it is and its exact state; what it must be able to do
entry:    the force level per actor, and which decisions are left to the mod (one line)
opportunity:  conditions that must hold: at the act, throughout, at named steps; and which causes count as external
act:      a timeline: at a tick or when a condition holds, do this
observe:  extra tracks and taps (the conditions' own needs are added by the runner)
success:  conditions on game state at the end or at a step
forbidden: conditions that must never hold (defaults below)
end:      a condition, and a tick limit
keep:     on which outcomes to keep the station, its twin and a save
```

**Conditions** are a small language over aliases, value paths and the trace: comparisons; `at(step)`,
`throughout(window)`, `within(ticks)`, `before(event)`, `after(event)`; `count(event where ...)`; geometry
(`in_station`, `distance`, `inside_radius_of(event)`). A condition cannot be built from a "mod says" record alone.

**Defaults that every scene gets without writing them:** forbidden: an exception or error from the mod under test; a
cast member lost or doubled; a cast thing destroyed that the scene did not say may be destroyed. The standard calm
profile. Bystanders fenced. Needs of bystanders held. The breach watchers. A tick limit.

**What the builder never has to learn:** tool names; ticks per call; pause and speed; polling; waits; the log cap;
load races; the camera; how a control is held; how an alias is bound; how the outcome is classified; how to restore.

### Worked example 1: the spared carrier in a blast (Explosive Knockback)

The case from 2026-11-23: the carrier walked out of the blast once, and that one failure blocked a visit.

```
scene: knockback.spared_carrier        kind: A
needs: { mods: [ExplosiveKnockback], station: 21x21, margin: 12 }
cast:
  carrier: { pawn: Colonist, at: center, carrying: {thing: Steel, count: 40}, hold: pin, health: full }
  victim:  { pawn: Colonist, downed: true, carried_by: carrier }
entry: "pin (hold) the carrier; place the blast; leave to the mod: who is spared, who is thrown, what is dropped"
opportunity:
  at(act):   [ carrier.position inside_radius_of(blast), carrier.carried == victim, victim.alive ]
  external:  [ non-cast pawn in station, weather change ]
act:
  - at +30: explosion { kind: Bomb, cell: carrier.cell + (2,0), radius: 3.9 }
success:
  - count(damage where victim == carrier and instigator == blast) >= 1      # the threat was real
  - victim.health unchanged since act                                        # the spared one was spared
  - at(end): victim.spawned and victim.alive
forbidden: [ count(spawn where thing is duplicate_of(victim)) > 0 ]
end: { after: explosion.finished, plus: 120, limit: 600 }
```

What the pieces buy. The pin removes the walk-out, so the scene is kind A; it steps past the carrier's own movement,
which this scene does not claim to test. The first success line rules out "survived because nothing hit" (review §3).
If a boar had wandered in, the station watch would have recorded it before the act, and a failed opportunity would
be ENVIRONMENT FAULT by row 4. If the carrier had still left the radius while pinned, that is not external: UNRESOLVED.

### Worked example 2: a raider rescued from a pit (FlowWorks)

Two scenes, because there are two claims (review §6).

```
scene: flowworks.rescue_ordered        kind: A
needs: { mods: [FlowWorks], station: 15x15 }
stage: { fixture: pit { depth_m: 4, at: center, size: 3x3, lid: none } }
cast:
  fallen:  { pawn: Pirate, faction: hostile, at: pit.floor, downed: true }
  rescuer: { pawn: Pirate, faction: hostile, at: pit.rim, group: with(fallen), can: [reach(pit.rim)] }
entry: "order (through the giver) RM_RaiderFetchFallen on fallen; leave to the mod: the giver's eligibility, the path, the lift"
opportunity:
  at(act):     [ fallen.downed, fallen.cell in pit.floor, rescuer.awake ]
  throughout:  [ fallen.alive, rescuer.alive ]
act:   [ at +0: order { actor: rescuer, giver: RM_RaiderFetchFallen, target: fallen } ]
success:
  - count(job_start where pawn == rescuer and job == RM_RaiderFetchFallen) == 1
  - at(end): fallen.cell not in pit.cells and fallen.spawned
  - at(end): count(things like fallen) == 1                                 # not lost, not doubled
  - at(end): rescuer.job != RM_RaiderFetchFallen                            # the job finished and let go
end: { when: rescuer.job != RM_RaiderFetchFallen after(job_start), plus: 60, limit: 3000 }

scene: flowworks.rescue_chosen         kind: B
tag: { spoils: "the group's own target choice; other raid duties", tried: "calm profile; pin of the colony; one raider only", budget: "12 copies, one cluster" }
  (same stage and cast, no order)
entry: "motive: both in an assault group with the colony out of reach; leave to the mod: whether and when the rescuer chooses the rescue"
success: [ count(job_start where pawn == rescuer and job == RM_RaiderFetchFallen and given_by == think_tree) >= 1, ...as above ]
allowed_miss: "the rescuer chose another duty for the whole window"
```

The first scene passes on one run. The second passes on one SUCCESS among its copies; a copy where the rescuer never
chose is a RANDOM MISS; a copy where the fallen raider vanished is a MOD FAILURE whatever else happened.

### Worked example 3: a flyer taking off

```
scene: flight.takeoff_and_flap         kind: B
tag: { spoils: "takeoff is a chance at each job start, by design", tried: "many job starts per animal; 16 animals side by side", budget: "one cluster of 16, 2,500 ticks" }
needs: { station: 25x25, margin: 10, far_from_map_edge: 20 }
cast: { bird[1..16]: { pawn: <the flyer's kind>, wild: true, needs: held } }
entry: "natural job starts (wander); leave to the mod and the game: the takeoff chance, the whole flight, the animation"
opportunity: { throughout: [ bird.alive, bird.in_station ] }
observe:
  - track bird.flight: [ state, lerp_tick, height_factor ]            every tick
  - track bird.draw_intent: [ graphic, facing, offset ]               every tick while flying
success:                                                              # for at least one bird:
  - sequence(bird.flight.state) contains [Grounded, TakingOff x50, Flying, Landing x50, Grounded]
  - while Flying: bird.draw_intent.graphic cycles through all frames of its flip-book in order
  - at Grounded after Landing: bird.draw_intent.graphic == the grounded graphic
allowed_miss: "no bird took off in the window"
end: { limit: 2500 }
```

This is the flapping bird test. It reads state and draw intent; it takes no picture; it respects the standing ruling.
The start chance itself (how often) is checked offline, where runs are free (policy §3).

### How a scene is checked before it is trusted, and how a program reads the result

- **Lint, with no game:** the file is valid; every def name exists in the frozen def dump; every path's first step is
  a known alias; no success stands on "mod says" alone.
- **Shown both ways, once** (the repo's rule for a deciding test): the scene runs against a planted fault and gives
  MOD FAILURE, and against the real build and gives SUCCESS. A scene file can name its own plant ("with setting X
  off", "with mutant build Y").
- **The result** is the receipt (§9): one file, a fixed schema, and a distinct exit code for each of the seven
  outcomes, so that a caller which loses the file still has the outcome.

- **For:** the cost of every future scene; the policy's "a program decides each run from the contract".
- **It works when:** a builder who has never used the bridge writes the spared-carrier scene from this page in under
  15 minutes, and the lint catches a misspelt def and a success built only from "mod says".
- **Value / effort:** high / medium.

## Every capability, with its value and effort

Value: how much instability it removes, from the census. Effort: my estimate of the build, without reading the present
code (the second designer will correct it). Three levels each.

| capability | section | value | effort |
|---|---|---|---|
| Scene runner: one call, in-game deciding, the classifier | 7 | high | high |
| Tick driver: frame-level duties, pinned update rate, burst and real time | 7 | high | medium |
| Tracks with value paths and aliases | 6 | high | medium |
| Base event taps with heartbeat and synthetic test | 6 | high | medium |
| Trace written out while running, bounded, crash-safe | 6 | high | low |
| Receipt with loaded-build identity | 9 | high | low |
| Calm profile: one call, status per control, re-armed after load, restore, lease | 1 | high | medium |
| Breach watchers (arrival, station, cast, sky, game) | 1 | high | medium |
| Scene exceptions in the profile | 1 | medium | low |
| Stations: allocator, clean with read-back, retire | 2 | high | medium |
| Build from data with read-back and capability asserts | 2 | high | medium |
| Fixtures | 2 | medium | low |
| Start state twin and signs | 2 | medium | low |
| Second small map as a control arm | 2, 8 | medium | unknown |
| Reassert | 3 | high | low |
| Before-sweep with weights | 4 | high | medium |
| Fence for bystanders; pin and wait holds | 5 | high | low |
| Order through the giver (level 3); motive (level 2) | 5 | high | medium |
| Force level on the receipt | 5 | medium | low |
| Draw intent | 6 | high | medium |
| Window transcript | 6 | high | medium |
| Draw submitted | 6 | medium | high |
| Pixels off the player's camera; filmstrip | 6 | medium | medium |
| Stamp again with reset verification; copies side by side | 8 | high | low |
| Sample identity and trajectory fingerprint | 8 | medium | low |
| Keeper save, random state, divergence finder | 8 | medium | medium |
| First-exception tap; log re-arm | 10 | high | low |
| Heartbeat and broken-game watcher | 10 | high | medium |
| Sitting mode; truthful calls; debts repaid | 10 | high | medium |
| Scene language, lint, shown-both-ways | 11 | high | medium |
| Probe plug-ins | 6 | medium | low |
| Mod trace points and reset hooks (in our mods) | 6, 2 | medium | low per mod |

## The first ten capabilities to build

Ranked by stability gained per unit of effort. Each line says which census ranks it answers.

1. **The receipt with loaded-build identity.** Low effort, and it ends a whole class (rank 3: at least 28 visit
   records and 40 lane jobs). Everything later writes into it.
2. **The first-exception tap, log re-arm, heartbeat and broken-game watcher.** Low to medium effort; it makes COULD
   NOT LOOK and APPARATUS FAULT real outcomes and stops blind repeats on a dead game (ranks 2 and 6).
3. **The tick driver and the scene runner with in-game conditions** (the keystone). High effort and the largest gain:
   it removes the gap between calls (ranks 2, 5, 9) and pins the camera-dependent update rate, an influence that no
   record had named.
4. **Tracks and the base taps, with aliases, heartbeat, and the trace written out while running.** With the runner,
   this is what makes a contract decidable by a program (ranks 2, 5).
5. **Stations with clean and read-back, and build-from-data with capability asserts.** Ends leftovers and
   mis-staged actors (rank 7 and the "staged actor" row), and makes kind A reachable.
6. **The fence and the holds, and the order through the giver.** The least force that makes the opportunity arrive
   (rank 1), and the most common spoiler removed (bystanders).
7. **The calm profile as one call with status, breach watchers, re-arm after load and restore.** Most of its controls
   exist as single tools today; the gain is that they become one verified state (ranks 4 and 8).
8. **Reassert and the before-sweep.** Low effort once 5 and 7 exist; they turn a spoiled run into a refused start.
9. **Stamp again and copies side by side, with sample identity.** Low effort once 3 and 5 exist; it is what makes
   kind B budgets affordable.
10. **Draw intent and the window transcript.** They open the two blind areas that the coming mods lean on most (what
    is drawn: 14 of 20 subjects; UI content: 8 of 11 in one group), and they carry the flapping bird test.

After these: the scene language's lint and plug-ins as scenes accumulate; the keeper save with the divergence finder
when the first hunt needs it; pixels and the filmstrip on the owner's word; the second small map when a map-wide mod
(Direct Sun, Stillsand) advances; draw submitted last.

Why the calm profile is seventh and not first `[my judgment, and the review's]`: its parts mostly exist, and the
census shows more loss from not seeing and from the gap between calls than from events that no control held. A calm
profile without the breach watchers and the runner would still leave a spoiled run looking like a mod failure.

## The testing horizon: what is not designed, and why

- **Exact replay as an acceptance tool.** Designed only as a diagnosis aid with a measured divergence. With 300 mods
  it cannot be promised, and no acceptance verdict may depend on it.
- **A snapshot of a region in memory.** A rectangle is not a closed set of objects. Stamp-again with reset
  verification covers the need at a fraction of the risk. Reopen it only if reset verification keeps failing for
  reasons a reset hook cannot fix.
- **Holding the hour or season still while ticks run.** It would need a false clock for part of the game, and would
  change schedules and timers. Scenes set the hour and stay short, or test the boundary on purpose.
- **Faster days by clock jump.** It simulates nothing. Compression is labelled and comes from rates.
- **What is heard.** Sound requests are recorded; the audio output is not judged.
- **Taste.** Whether a picture looks right stays with the art judge and the owner's walk. The bridge supplies clean,
  repeatable pictures and filmstrips; it does not judge them.
- **Frame-time method.** The runner offers a real-time mode and timings. A quiet machine, pairing and statistics stay
  in the performance method, not in the bridge.
- **Natural scenes at force level 0** (a real raid finds its own way) as acceptance tests. The policy already leaves
  these to the owner's walk and to real play.
- **A complete list of third-party suppressors.** The profile grows one named suppressor at a time, when a mod bites.
  The watchers catch what no suppressor holds.
- **The quality of an in-game LLM's reply.** The bridge can stub the reply and read the validator's verdict; it does
  not judge prose.
- **Scheduling across the four games.** Which game runs which scene is the test lane's and the pipeline's work. The
  bridge needs only that every capability here works the same on each game, by name.
- **Droids.** The ladder applies; the details wait for Droidworks' design.

## What GPT changed

Round 1 (engine facts, the Multiplayer mod's determinism work, the shapes for telemetry and repeats). Its full answer
is `census_sources/gpt_round1_answer.md`.

Folded in:
- **A bare tick loop is not play.** I had read that the tick method is public and concluded that the runner could
  loop it. GPT pointed at the Multiplayer mod's tick code: per-frame region, power and glow work, and a
  camera-dependent update rate. I then read `Map.MapUpdate` and `GenTicks.GetCameraUpdateRate` and confirmed both.
  The tick driver in §7 and the pinned update rate are the result, and the camera is now a named influence.
- **Tick-locked path results are not deterministic path results.** Added to §7 and §8.
- **An incident gate is not an environment boundary.** Health processes, births, hatching eggs, predators, revenge,
  lightning, explosive things and Anomaly entities act with no incident. The breach watchers of §1 observe effects
  and causes for that reason; the taps list in §6 gained fire, explosion and hediff events.
- **Reload both runs, not one,** and expect loading to draw random numbers. §8's replay procedure.
- **Side-by-side copies are a cluster.** §8 and the receipt's cluster id.
- **Draw truth is three facts** (resolved, submitted, pixels), and a mesh submission does not name its thing. §6.
- **The flap frame cannot be computed from the tick alone**; the probe must ask the game's own resolver. §6.
- **The known off-screen renderer moves the player's camera and restores it.** §6 and an open question.
- **Missing render evidence is COULD NOT LOOK; lost telemetry or a bad tick driver is APPARATUS FAULT.** Classifier
  rows 2 and 3.

Rejected, with the reason:
- **"Thing ids are not renumbered by a load."** GPT cites the engine saving ids. A census record of ours says ids
  shifted by 1000 after a load in one walk. I did not settle it; the design depends on aliases and not on either
  claim. It is listed for the second designer.
- **Reuse of a general in-game script front end as the probe mechanism.** GPT notes that the upstream bridge has a
  restricted script language. I keep sent programs out of acceptance tests for the reason in §6 (an unvalidated,
  unversioned checker); whether the tool list keeps a script front end for exploring is the second designer's call.
