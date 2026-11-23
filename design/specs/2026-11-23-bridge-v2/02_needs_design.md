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
| A second program driving the same game | HELD: one session per game, tied to the game's driver lock; a call from anyone else is refused | each refused call is a breach of class APPARATUS | by design, from the census |

**The breach watchers** are five taps that run for the whole deciding window, whatever was held:
1. **Arrival watch**: a pawn appears on the map that is not cast.
2. **Station watch**: anything that is not cast enters a station or its margin, or a station cell changes (terrain,
   roof, fire, a new thing) by something that is not cast.
3. **Cast watch**: a cast member leaves its station, dies, is downed, changes faction, enters a mental state, or takes
   a job that the scene did not list as expected.
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
