# BRIDGE v2.0, pass 1: the census of environment influences on live tests

Item `RIMMANDRAKE_DESIGN_BRIDGE_TWO_WHAT_LIVE_TESTING_NEEDS_FABLE_PASS_ONE`. Written 2026-11-23.
This file is the evidence. The design that answers it is `02_needs_design.md`.

An **environment influence** is anything outside the behaviour under test that changed the result of a live run, or made
the result unreadable. A **live run** is a test, a proof run, an in-game visit, or a look by the owner in a running game.

## How the census was made

Four Sonnet helpers read records, each with one narrow source set. Two Opus helpers read the designs of the mods we are
building. One Sonnet helper listed what the present bridge can do. Their full tables, with every path and quoted
phrase, are committed beside this file in `census_sources/`:

| file in `census_sources/` | what it read |
|---|---|
| `census_knockback_flowworks.md` | Explosive Knockback visits 1 to 4 and FlowWorks visits 1 to 8: every `SUMMARY.md`, `strange.jsonl` (29 and 50 lines), `unrun.jsonl`, `polish.md`, and the FlowWorks test-pilot record of 2026-11-23 |
| `census_pyrelands_others.md` | Pyrelands visits 1 to 7 (80 `strange.jsonl` lines), Gimme Some Slack visits (two versions), Graffiti, a word search of `design/concepts/` and `design/RimMandrake/` |
| `census_lessons_traps.md` | `infrastructure/state/lessons/` by word search (129 hits, about 85 read by their first lines), `instrument_traps.md`, `tool_traps.md`, and the trap references of the `rimbridge`, `rimbridge-companion` and `live-debugging-proof-harness` skills |
| `census_ledger_ops.md` | item prose by word search (about 25 items read), the ledger by word count, the SteveDesktop test lane's job records through `invalid_class.py`, the void records in each mod's `stage.json` and `rows.jsonl` |
| `mods_hypotheses_a.md`, `mods_hypotheses_b.md` | the designs of 20 mods and cross-mod systems, for what their live tests will need |
| `bridge_existing_capabilities.md` | the present bridge's tool list and skills, as an inventory only |

Counting rules. A count is the number of records that a helper listed, never a count of game events. "At least N" means
N records were found and more are likely. A word count over the ledger is a count of mentions and is used nowhere below
as a count of incidents. I read RimWorld 1.6 code myself through RimSage for the engine facts; they are in
`02_needs_design.md` under "Engine facts the design stands on".

## The numbers that frame the problem `[measured, from records]`

- **51 of 73** past live-proof runs that ended as a mod FAIL were not mod faults (24 could not read their value, 22 were
  harness faults; 22 were real). Source: `skills/live-debugging-proof-harness/references/traps.md` line 10.
- **11 of 12** findings of one full-mod-list run on 2026-10-11 were not mod bugs: harness 8, site 2, not ours 1, mod 1.
  Source: `skills/live-debugging-proof-harness/references/classifying-and-learning.md` lines 23 to 56.
- **187 of 1,164** rows in the 19 in-game visits of FlowWorks, Pyrelands and Explosive Knockback ended UNMEASURED
  (all causes). **101** checks are written and never ran (`unrun.jsonl` of five mods).
- The Pyrelands walk check on the owner's full mod list **was never counted as passed in 7 visits**.
- SteveDesktop test lane: **163 of 1,278** jobs INVALID (game or machine 72, delivery of the build 40, unknown 51). In
  the measured window 2026-11-06 to 2026-11-14: 85 of 261 jobs, 11.8 of 43.1 lane-hours.
- Speed today: one bridge call is 4 to 17 ms on the game's main thread and about 50 ms round trip in a tight sequence.
  One batched call did in 14 ms what 421 single calls did in 7.0 s. A stepped advance runs about 50 game ticks per
  second on the full list ("about 4 real minutes per 15,000 ticks"). A cold load is 22 s on 13 mods and 14 to 25 min on
  the full list.

## Measured influences

Each row: what it was, where it was seen, how often, what it cost, how it was handled, and the class of that handling.
**CONTROL** means a tool or setting removed the cause. **WORKAROUND** means a rerun, a hand repair of one scene, or a
rule for agents. **NOTHING** means it was named and left. Paths are in the `census_sources/` file named in the last
column; this table merges the four.

### Group 1: the world acts on the scene

| influence | seen (records) | cost | handling then | class | source |
|---|---|---|---|---|---|
| A pawn dies, is downed, panics or falls ill during a long advance, and the advance stops or the row is void (heart attack of an off-map colonist, Plague, a predator kill, a starving bystander, heat stroke at 55.8 C) | at least 14 events in 6 of 7 Pyrelands visits; about 7 runs voided; 3 lessons on colony death in long runs (heat wave killed 6 of 8; starvation at tick 55,500; a berserk at tick 59,007) | the most reruns of any single cause; one wrong-verdict risk (a dead venom subject would have read "venom gone") | fixtures fed daily, a heat guard, "resume past harm to pawns that are not the player's" | WORKAROUND | pyrelands, lessons |
| Idle colonists, haulers and leftover test colonists act in the scene (73 colonists on one map; a hauler took a scene's stack; a thirsty colonist drank 15 units from the tank under test; colonists pack the bottles of an earlier row) | at least 6 in Knockback and FlowWorks; 3 harness trap entries | wrong FAILs; `sc_pawn_arc` failed 7 of 10 on a crowded map and passed 10 of 10 on a fresh one | forbid every haulable that is not the scene's; draft every colonist not in use; fresh map | CONTROL for hauling; WORKAROUND for the rest | knockback_flowworks, lessons |
| Needs of the actors (hunger, thirst, rest) change the run (a worker starved, food 0.79 to 0, while it held the job under test) | 3 in FlowWorks; 1 Pyrelands | a stalled scene, a failed staging | the proof tops up food and rest | CONTROL late | knockback_flowworks |
| A raid, a visitor, a hostile arrival, a manhunter, a guard patrol of another mod arrives unasked | one run lost 29 rows (19 "surprise", 7 "hostile arrival", 3 "hurt") on 2026-10-24; 8 lines in 3 Pyrelands visits; at least 5 lessons | the 29-row loss; the full-list walk never passing | a calm storyteller, a sweep of hostiles before each block, a rule to re-calm "before every block, not once per run" | CONTROL in part; the controls drop after a load | ledger_ops, pyrelands, lessons |
| Wild animals come back after a sweep; a map-generated hive or turret keeps the map hostile | 4 harness trap entries; 18 wild predators appeared in about 1,300 ticks that ran by accident | downed colonists, a map that the game then removed | `wild_spawner_block`, sweeps | CONTROL, but it releases itself and is gone after a load | lessons |
| Weather: rain filled the pits under test; "Clear" did not stop rain already falling; a storyteller pinned Clear for 40 rolls; a tile below 0 C | 2 Knockback visits; 4 Pyrelands records; 2 harness entries | one real FlowWorks defect was hidden for a whole visit behind rain | weather forced with a lock; rain suppressed for N ticks | CONTROL in part | knockback_flowworks, pyrelands |
| Fire and heat that the test did not place (a fire spreads to the waiting cells after about 1,250 ticks; relit gas; fires on the firebreak 11,600 ticks later; heatstroke counted as an injury) | 9 items in 5 Pyrelands visits; 3 in Knockback | the sprayer control could not be counted in 3 visits | hand repairs per scene | WORKAROUND | pyrelands, knockback_flowworks |
| Another mod's object, ticker or error acts on the thing under test (a titan's wake thins the roof of the pen under test; a FlowWorks error fails Gimme Some Slack's log budget in 4 visit-runs; a suspension wreck pushes the pawn off its cell in 10 ticks; another mod's flee rule) | 6 distinct in Pyrelands and Gimme Some Slack; 2 harness entries; the flaky gas chain of Knockback (4 to 5 of 16 to 17 runs) was Cauldron's fire scan | wrong FAILs; one real cross-mod fault found late | classed and left | NOTHING | pyrelands, lessons |
| A second process acts on the same game (another agent's restore reset the setting under test at tick 18,000; a peer pushed the mod mid-run and voided a 25-minute rerun twice in one day; a script without its instance variable drove the wrong game) | 3 in FlowWorks; 5 lessons on the wrong game | voided rows, the owner's campaign advanced about 10 game-minutes once | per-game driver lock; two code fixes | CONTROL for the lock; the wrong-game case is a WORKAROUND | knockback_flowworks, lessons |

### Group 2: the scene is not what the test assumed

| influence | seen (records) | cost | handling then | class | source |
|---|---|---|---|---|---|
| The valid opportunity never arose (the raid refused to fire; no raider fell; raiders never came within 3 squares; one raider was held where two were owed; raiders had no motive to cross; the scene killed its own actor) | at least 12 in Knockback and FlowWorks; 8 road-back items; 8 Pyrelands controls removed as "no tool can run them" | UNMEASURED rows and whole scenes rebuilt; the pit rescue was seen once in 18 free runs | reruns; scene rebuilds; in the end, a direct order (2 of 2) | WORKAROUND | knockback_flowworks, ledger_ops, pyrelands |
| Leftovers of an earlier scene on the same map (corpses, a hostile, a cell reservation, fallen wires, stale ice, a pinned counter, a downed animal) | at least 6 in Knockback and FlowWorks; 11 site items in Pyrelands and Gimme Some Slack; 3 false tickets from fallen wires | wrong FAILs "for site reasons"; three tickets filed against a mod that was correct | destroy non-colonists before each check; fresh map | WORKAROUND | all four |
| Process-wide state of a mod survives a scene change or a load (theft counters; an overflow total; a 60-tick cache read 4 ticks later; a per-tick cache of `CanFireNow`) | 4 harness trap entries | "one day read -4 instead of -2" | per-mod reset calls where someone wrote one | WORKAROUND | lessons |
| A staged actor lacks what the scene assumed (no gun, no shovel, a backstory that disables the work type, an ideology that disables Mining for every colonist of the saved site, work priority 0, a spawn that arrives downed, a requested kind replaced by a vanilla colonist in 4 of 80 spawns) | at least 5 in FlowWorks, 6 in Pyrelands, 4 harness entries, 1 instrument trap | "nobody does the job" read as a mod FAIL; "for days" a count blamed a defect that did not exist | each scene repaired by hand | WORKAROUND | all four |
| The site is wrong (a pond bed under the origin, marble under a rock roof, a geyser in the rect, fog, giant plants, a mountain roof that collapses for 99,999 damage, no water cell on the map) | 2 in Knockback, 11 in Pyrelands, 5 harness entries | INVALID rows; checks removed from the table as "site" | origins that skip ponds; an "open ground" preparer | CONTROL for two cases; else WORKAROUND | knockback_flowworks, pyrelands, lessons |
| A fixed wait that should have been a condition (a wait of 2,500 ticks for a job that takes 16,000 at skill 0; a census one poll early; a read 3 ticks after the act) | 7 clock races in Pyrelands and Gimme Some Slack; 6 timing entries in the harness skill | a wrong verdict each time | the harness learned to wait on the game's own state | CONTROL where repaired | pyrelands, lessons |

### Group 3: the test could not see, or saw wrongly

| influence | seen (records) | cost | handling then | class | source |
|---|---|---|---|---|---|
| The instrument reads wrong and reports success (a frame timer read 0 on a paused clock and scored PASS in 9 runs; a scene passed with no raid on the map; an all-zero vector passed; a pawn list always returns job = null; a damage call reports success with 0 damage; a judge on an empty list returns PASS) | at least 8 in Knockback and FlowWorks, 7 in Pyrelands, 10 in the ledger, about 25 "engine setter is advisory" entries | false PASSes; "a full 7,200-tick run" read wrong | each instrument repaired singly | WORKAROUND | all four |
| No tool reads the value (which toil a hauler is on and why it stalled; why a raider left a 4 m pit; what lit a fire; plant growth; sky colour; the drawn position of a pawn against its logical position) | 14 "could not observe" items in Knockback and FlowWorks, 12 in Pyrelands; 592 UNMEASURED rows across 264 keys in one tally | hunts that end "cause UNMEASURED"; three test-pilot sittings | theories; a new tool per case | NOTHING | knockback_flowworks, pyrelands, lessons |
| One-tick and short events fall between polls (a 50-tick mental state starts and ends between two reads; a raid census reads 0 at +60 ticks and 19 at +300; a stepper overshoots by 100 ticks) | 4 lifecycle trap entries | "reads as a behaviour FAIL"; a working tool filed as broken | staged censuses | WORKAROUND | lessons |
| The log goes blind (the game stops logging at 10,000 messages; the bridge's journal keeps the last 1,000 entries and lost a warning after about 3,400 ticks; `Player.log` has no level marker) | 2 cap hits, 3 ring losses, 4 other entries | every end-of-run log check blind | a tap that counts lost entries and turns the row UNMEASURED; a log re-arm | CONTROL in part | lessons |
| Pictures are wrong (a stale frame while paused; a file name reused within one second returns the old image; a 24 MB capture of the owner's desktop; 10 of 24 hourly fire captures with no fire; zoom and UI state left over; a draw-only effect that was not drawn) | about 30 lines in 6 of 7 Pyrelands visits; 7 lessons; 6 visual-limit items in Knockback and FlowWorks | pictures for the owner and for judges void; 14 owed re-shots | file names made unique; frame-on-subject checks | CONTROL for three causes; NOTHING for draw-only effects | pyrelands, lessons |
| Motion cannot be judged (a jolt draws as a doubled ghost in stills; a shake "needs a look in motion"; flight) | 3 in Knockback; the fire-hawk hunt (about 35 minutes, about 25 screenshots, nothing caught) | open "look" rows; the owner's ruling against live flight tests | left for the owner | NOTHING | knockback_flowworks, bridge_existing |
| Frame time measured on a noisy machine and list (mod-off baselines of 35 to 151 ms against a 50 ms bar; 3 native crashes) | at least 4 visits and 1 test-pilot sitting of about 4 hours | one visit and one sitting | interleaved pairs, 21 pre-registered pairs | CONTROL plus WORKAROUND | knockback_flowworks |
| Planted faults that no live check sees | 5 in Knockback, 3 to 4 in FlowWorks | checks that cannot fail | listed as blind | NOTHING | knockback_flowworks |

### Group 4: the bridge and the game process

| influence | seen (records) | cost | handling then | class | source |
|---|---|---|---|---|---|
| The game ran a build or a mod list that the test did not mean (a stale companion DLL, a stale mod DLL through a whole visit, a tier marker of an older run, a save that will not load on this list, a list file that names 544 mods while 26 run) | at least 11 in Knockback and FlowWorks; about 17 lines in Pyrelands and Gimme Some Slack; 40 SteveDesktop jobs; 5 lessons | refused visits; rows void; "no tool tells in-run that another mod's DLL is stale" | gates on our own mod's build; nothing for other mods' DLLs | CONTROL in part | all four |
| Time does not advance as told (a step call stops short and still says success; a speed call reports set while the game stays paused; closing the menu resumes time; a wait on a paused clock burns 17 s per order, "72 orders ate 20 of 25 minutes"; a clock jump fires every absolute timer) | at least 9 trap entries | a finding of "263,701 ticks, zero spawns" withdrawn; a false FAIL from a clock jump | rules for agents | WORKAROUND | lessons |
| A call reports success and the game did not change (a modal window swallowed a raid, "cost days"; a stale float menu made five identical runs paint 759, 448, 0, 384, 384 walls; an unknown parameter is dropped silently; a spawned hostile with no group does nothing for 1,260 ticks) | about 20 entries in the silent-failure reference | days, in the worst case | fixed tool by tool | CONTROL per tool | lessons |
| Load races (the old map answers for 3 to 8 s after a load; things are not spawned yet; controls must be applied again after every load) | 7 in Pyrelands and Gimme Some Slack; 4 lifecycle entries | "3 colonists died" read off the old map | a load helper that settles first | CONTROL where the helper is used | pyrelands, lessons |
| The game hangs, crashes, or will not reach a map | 9 in Knockback and FlowWorks; 72 SteveDesktop jobs (17 "world start gave no map", 9 native crashes in load, 7 died mid-run, 6 would not start); 2 sessions died of a per-frame exception storm | 9.3 lane-hours in one 9-day window; 29 blind repeats of which 16 died again | retry; a 12-hour reboot; logs now kept per attempt | WORKAROUND | knockback_flowworks, ledger_ops |
| A long advance outlives the caller (a 160 s or 250 s shell bound kills a row that needs 338 s; a monitor that expires after 60 minutes; a runner killed at 2 hours) | at least 6 in FlowWorks, 6 in Pyrelands | killed rows, requeues | longer bounds, resumable chains | WORKAROUND | knockback_flowworks, pyrelands |
| The run leaves the game changed (a mod setting left on; live fallen wires; a save slot overwritten) | 2 settings, 3 wire tickets, 1 overwritten world save | later runs fail for the earlier run's reason | a restore in a `finally` block where someone wrote one | WORKAROUND | lessons |
| Same build, different result, no cause found (burn counts 8, 9, 6 then 1, 3, 0; a coin-flip grate; a raider left a trench once) | at least 6 in FlowWorks; 3 in the ledger | "rerun until three in a row"; hunts | rerun | WORKAROUND | knockback_flowworks, ledger_ops |

### The ten most damaging, ranked by recorded cost

1. **The valid opportunity never arose**: at least 12 scenes, 8 road-back items, 8 controls removed; 1 success in 18
   free runs against 2 of 2 when ordered.
2. **The instrument read wrong and said PASS or FAIL**: 51 of 73 historical FAILs were not mod faults; a false PASS in
   9 runs.
3. **The game ran a build or list the test did not mean**: at least 28 visit records and 40 lane jobs.
4. **A pawn died, was downed or starved in a long advance**: at least 14 events, about 7 voided runs, the full-list walk
   never passed in 7 visits.
5. **No tool reads the value**: 26 "could not observe" items; 592 UNMEASURED rows across 264 keys in one tally.
6. **The game hung, crashed or never reached a map**: 72 lane jobs, 9.3 lane-hours in 9 days.
7. **Leftovers of an earlier scene, and bystanders in the scene**: at least 23 records; three false tickets.
8. **Unasked raids, visitors, animals, and other mods' events**: 29 rows lost in one run; controls that vanish on load.
9. **Time did not advance as told, and fixed waits**: at least 22 records; 20 of 25 minutes burnt in one case.
10. **Pictures wrong, motion and draw-only effects unseen**: about 40 records; flight has no live check at all.

Reading of the ranking `[my judgment]`: four of the ten (ranks 1, 4, 7, 8) are the environment proper. Five (ranks 2,
5, 9, 10 and part of 6) are faults of **observation and timing**: the test could not see, or looked at the wrong
moment. Rank 3 is identity. This matches the GPT review's ordering, which put atomic execution and structured
observation above further environment suppression (`../2026-11-23-three-test-kinds/gpt_review.md` section 5).

### What the handling classes say

Of the 31 merged rows above `[counted]`: CONTROL (whole or in part) 14, WORKAROUND 13, NOTHING 4. Almost every CONTROL was made
for one scene or one tool, after the fault. Three properties recur in the controls that exist `[measured, from the
inventory]`: they are **separate calls** (weather lock, rain suppress, wild-spawner block, incident-queue clear,
hostile sweep, draft, forbid), they are **lost on a load or expire by themselves**, and **none reports a breach**:
nothing says "an incident tried to fire and was held". No profile turns them on together or says which are on.

## Influences found in the engine that no record names

Two influences came from reading the RimWorld 1.6 code in this run (after GPT's review pointed at the Multiplayer
mod's patches). No visit, lesson or item names either. They may be behind some of the "same build, different result"
rows above; that link is a guess `[guess ~40%]`, and nothing measured it.

| influence | the engine fact `[read]` | why it can spoil a live test |
|---|---|---|
| **The camera.** Where the camera points and how far it is zoomed changes how often a thing runs its interval work | `GenTicks.GetCameraUpdateRate`: 15 ticks for a thing outside the camera's view or on a map that is not shown, (zoom level + 1) ticks for a thing in view; `Thing.DoTick` passes the elapsed ticks to `TickInterval` | the same scene runs with different timing of needs, job checks and comp intervals when it is on screen, off screen, or at another zoom. A screenshot helper that moves the camera changes the run that it photographs |
| **Frames between ticks.** Each map does simulation work once per frame, outside the tick | `Map.MapUpdate`: power nets, dirty regions and rooms, glow grid, pawn groups, post-tick visuals | a stepped advance, a high game speed and normal play do this work at different points between ticks. A read of a room, a region or a power state right after a change can differ with the frame rate |

## Hypothesized influences, per mod we are building

From the mods' designs (`census_sources/mods_hypotheses_a.md` and `_b.md`; each line there is marked DESIGN with its
path, or GUESS). Three columns: what a live test must hold still, must force, and must observe. The pipeline's mod
list was read from `./pipe show` on 2026-11-23.

| mod or system | hold still | force | observe (the hard part) |
|---|---|---|---|
| **FlowWorks** (pits, liquids, canals, bridges, raids) | rain and other liquids' tickers; bystanders who drink, haul or fall in; reservations on pit cells; fire on decks | a raider that chooses to cross a covered pit, to rescue a comrade, to swim; a pit drained or filled to a level; a lid that drops on a tick | which job and toil each raider and warden holds per tick; the one-tick fall; litres per cell over ticks; drawn against logical position of a pawn in a pit; pictures of water |
| **Pyrelands** and its mechanics mod (fire, heat, ash, fire animals, the furnace-beast) | weather, wind, stray fire, heat on bystanders, other mods' roofs and titans, plant regrowth, wild predators over days | a fire on a chosen cell on open ground; a black-rain or ash weather; a bite; a hawk that seeks fire; days of game time | fire front per cell over ticks; what lit a fire; sky colour; plant growth; flight of the fire-hawk; creatures at zoom |
| **Explosive Knockback** (blasts throw pawns, corpses, goods) | the carrier walking out of the blast; haulers; gas and fire relighting; frame-time noise | a blast of a kind on a cell on a tick, with the carrier in it at that tick | the thrown thing in mid-air per tick; the landing cell; damage events with parts; shake and jolt as drawn; frame time |
| **Gimme Some Slack** (cords, spans, power, shocks) | weather on wires, geysers, other mods' log errors, leftover fallen wires | a cut, a short, a shock on a named pawn; a roof change; a save and load mid-span | the drawn curve of a cord; the one-tick shock; power live or dead per tick |
| **Graffiti** | raids (the mod's raider-pressure scene IS a raid), mood drift, goodwill drift | a painting spree (a mental state of the mod); raider tags; days of soak | thoughts and mood over days; what is drawn on a wall; rates |
| **Contagion, Fever Wood** | weather, wildlife, bystanders, the storyteller's own diseases | exposure, progression over days, a save mid-illness | hediff severity per pawn over time; dose and chance values; rare branches; per-cell clouds |
| **Cauldron, Gelatinous Slime, Stillsand, Leaning Scrub** | weather and wind, temperature, plant growth, bystanders, wildlife | a gas or sand or slime state on cells; a pawn that walks in by its own choice; a flee | per-cell grids over ticks; sink offsets as drawn; job and path traces; letters counted exactly |
| **Pits as superdeep cells; Direct Sun and shade** | time of day, season, cloud, roofs, other heaters | a collapse; a pawn entering; a sun angle at a chosen hour | per-cell shade and heat over an hour sweep; a second map as a control |
| **Wrecked Machines, droids, Machine Looks, Cold Storage** | haulers, power, temperature, goodwill | a repair job through the normal work giver; a look chosen in a UI; a chill over hours | UI choices and their drawn result; room temperature over time; job uptake |
| **The Bazaar trade window; in-game LLM wiring** | traders (the scene needs exactly one), the network, the model's own randomness | a trader arriving through its worker; a UI click path; a stubbed model reply | the content of a window; letters and messages counted; the validator's verdict |
| **Creature flight** (every flyer) | job starts (takeoff is a chance at each job start), map edges, predators | a takeoff by many job starts, or by the tracker; a landing; a save in mid-air | the flight state per tick; the animation frame per tick and per facing; the drawn height; the one-tick landing drop |

The needs that most of the 20 subjects share, by count of subjects `[measured over the two helper tables]`:
repeatable randomness or enough trials for a rare branch (10 of 11 in group b); long game time compressed and labelled
(10 of 11; 6 of 9 in group a); orders given the way a player gives them (9 and 7); events fired through their normal
worker with every unplanned one held (9 and 6); hidden values read without changing them (9); weather held (8 and 6);
save and reload mid-process (8 and 6); bystanders kept out without freezing the actors (8 and 7); UI content read (8);
what is drawn, not only the state (7 and 7); per-cell grids over ticks (7); matched arms side by side (7 and 6);
a live flip of a mod setting with restore (6 and 6).

New influences that the past records do not show but the designs predict `[guess ~70% each will bite]`:
- **Days-long scenes** (illness, growth, soak, seasons) make rank 4 worse: every scene of Contagion, Fever Wood,
  Graffiti and Pyrelands regrowth runs 60,000 ticks or more, about 20 real minutes each at today's 50 ticks per second.
- **Scenes whose subject IS an event** (Graffiti's raid, the Bazaar's trader, Pyrelands' weather) need the calm
  environment with one named exception, not a calm that is switched off.
- **Rates by design** (a start chance per job for flight, an infection chance, a drop chance) need many independent
  opportunities; one global random stream makes side-by-side copies share draws in order, not in value.
- **Map-wide states** (Direct Sun, weather-driven mods, Stillsand) cannot be isolated in one corner of a map; they need
  a second map or sequential arms.
- **UI-borne features** (Bazaar, Machine Looks, Mod Settings of every mod) need window content as data.
- **The in-game LLM** brings an influence from outside the game: latency and a non-deterministic reply.

## Blind spots

**Could not look** (kept apart from "looked and found none"):
- The evidence folders of every visit (JSON up to 3 MB each), the screenshots, and `rows.jsonl` line by line. Counts
  come from summaries.
- About 540 of 669 lesson files (not matched by the word search) and about 3,700 of 3,786 item files. The item search
  was by words; an influence written in other words was missed. Searches for "dropped to menu" and "bridge hung" found
  0 while the same events exist under "no_game" and "main menu not confirmed": those zeros are phrase misses.
- The raw logs of the SteveDesktop jobs. 51 of 163 INVALID jobs have no known cause at all.
- Conductor log lines about voided visits: `./pipe log` (last 200 lines) held none; older lines were not read.
- The owner's own looks: no record lists what spoiled a look of his, except where a visit summary mentions it.
- Designs that do not exist yet: Machine Looks (a proposal), Cold Storage (no bars, no scenes), Droidworks ("not yet
  dictated"), the Bazaar past slice 1, the LLM consumers. Their rows above are GUESS.
- The game itself. Nothing in this census was measured in a running game; this run touches no game.

**Looked and found none:**
- Graffiti has no in-game visit yet. Pyrelands visit rows name no raid, trader or mental break of a colonist as the
  spoiler (deaths and downings, yes).
- No record of a determinism measurement: nobody has run one scene twice from one save and compared.
- No record of what each control costs in milliseconds, or of a breach report from any control.
