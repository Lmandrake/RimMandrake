# Costly test acts in four in-game visits: the tables

Item `RIMMANDRAKE_CENSUS_COSTLY_TEST_ACTS_REPEATED_HE_SAW_SHIP_FLY`. The summary is `one_page.md` beside this file.
Written 2026-11-24 (local Pacific time). No test, scene, mod or game was touched.

Tags: `[measured]` is read from a record. `[guess ~N%]` is our estimate with a rough confidence. `UNMEASURED` names its cause.

## 1. How the numbers were read

| source | what it gave |
|---|---|
| `E:\telemetry\raw\bridge\2026-11-23.jsonl.gz` and `2026-11-24.jsonl.gz` | each bridge call: script, process run, start, length. 355,284 calls |
| `E:\telemetry\raw\tps`, `E:\telemetry\raw\tps.archmagi.b` | each game process (a new session id is a restart), and game ticks in 5 s windows |
| `E:\telemetry\raw\changes` | each mod-list change |
| the visit folders under `design/concepts/<Mod>/version/in_game/` | rows, seconds per row, runner logs, summaries |

The visit windows (local time) and the game:

| visit | game | bridge port | window | wall |
|---|---|---|---|---|
| Gimme Some Slack visit 1 (the latest finished; visit 2 runs now) | ArchBig | 5174 | 11-23 13:13 to 15:36 | 143 min |
| Pyrelands visit 7 (the latest finished; visit 8 runs now) | ArchSmall | 5175 | 11-23 05:00 to 08:56 | 236 min |
| FlowWorks visit 9 | ArchSmall | 5175 | 11-23 14:32 to 17:31 | 179 min |
| Explosive Knockback visit 5 | ArchBig | 5174 | 11-23 16:12 to 17:52 | 100 min |
| Explosive Knockback, the small-list rerun after visit 5 (gas-corner fix) | ArchSmall | 5175 | 11-23 18:27 to 19:21 | 54 min |

Visit 5 ran 5 checks only, so the rerun of 54 checks is counted beside it. Port 5174 is ArchBig and port 5175 is ArchSmall
in these windows: each visit's own scripts appear only on its port [measured].

Definitions:
- **A load act** is one unbroken group of menu, load and ready-poll calls of one process. It ends at the next other call.
- **A restart** runs from the last record of the old game process to the first working call on the new one. It includes a
  deploy or a build that was made while the game was down.
- **A wait** is the length of a call that lets the game run (`safe_advance`, `step_game_ticks`, `order_pawn`, `ordered_job`).
- A call's arguments are not recorded (only a hash). A wait was classed by ticks in the 5 s windows around it.

## 2. Counts and wall time by kind [measured unless tagged]

| kind | Slack v1 | Pyrelands v7 | FlowWorks v9 | Knockback v5 | Knockback rerun |
|---|---|---|---|---|---|
| gravship flight | **2**, 256 s with staging | 0 | 0 | 0 | 0 |
| new map | 8, 199 s | 3, 28 s (one took 1 s) | 0 | 3, 181 s | 2, 67 s |
| save load | 26, 249 s | 67, 676 s | 122, 674 s | 29, 537 s | 0 |
| game restart | 7, 2,312 s; and 1,140 s waiting for the first load | 1, 163 s | 5, 1,113 s | 3, 3,194 s | 2, 391 s |
| wait for game time | 341 s | 8,367 s (ticks: section 4) | 2,669 s (663,393 ticks) | 126 s | 304 s |
| staged raid | 0 | 0 | 13 | 15 | 0 |
| staged incident | 0 | 14, 0.2 s | 0 | 0 | 0 |
| mod-list change | 4 recorded; the full list came back twice | 1 | 4 | 1 recorded; the full list came back once | 1 |
| some script drove the game | 53.5 min | 186.5 min | 108.4 min | 24.9 min | 17.0 min |

Notes:
- The Knockback rerun's first restart is 175 s from the list change to the first call. The game was down 1,395 s before it,
  with a build inside; how much of that was the rerun's is UNMEASURED (no record says who stopped the game).
- The Knockback `fire_raid` calls took 9 s together. What the raids cost in scene time is UNMEASURED: no record splits a
  scene's length by cause.
- Seconds do not add to the window. A visit also spends time on deploys, builds, offline gates and the agent's reading.
- Slack's 341 s of waiting holds 167 s of boarding (section 3).
- Not split: how much of a FlowWorks scene's time is raid fighting and how much is staging. UNMEASURED, same cause.
- The restart at 14:33 to 14:38 in the Slack visit (290 s) has no purpose in the visit's summary. Purpose UNMEASURED.

Restarts one by one (seconds from the old process's last record to the first working call):

| visit | restarts |
|---|---|
| Slack v1 | 13:44 first list 77 · 14:09 fixed build 292 · 14:33 290 · 14:41 FlowWorks list 290 · 15:00 bridge list 36 · 15:01 planted fault 170 · 15:05 full list 1,155 |
| Pyrelands v7 | 05:13 pyrelands list 163 |
| FlowWorks v9 | 14:30 308 · 15:09 new build 247 · 15:53 `fw_gss_sitting` list 273 · 16:00 back 51 · 17:19 `evening` list 234 |
| Knockback v5 | 16:09 tier list 371 · 16:19 full list 1,178 · 17:07 full list again for one planted fault 1,645 |

## 3. Gimme Some Slack: the gravship flights

**How many flights did the latest finished visit make? Two [measured].** At 14:24:17 with the keep-wires switch on, and at
14:26:26 with it off. Each flight was launched once for real and asked once as a dry run, so four launch calls were logged.
Visit 2, which he watched, also made two: 23:37:46 and 23:40:15 [measured]. Six real flights are in the records since
11-22 16:30: three visits, two each [measured].

What each flight cost [measured, visit 1 and visit 2, four runs]:

| part of one run of 127 to 152 s | seconds |
|---|---|
| menu, new quicktest map, site scan, ship built, fuel | about 19 to 32 |
| **boarding: one `order_pawn` with a limit of 5,000 ticks** | **83.4 in every one of the six runs** |
| masts, cords, links | about 4 to 8 |
| take-off, travel, landing, reading | about 20 to 28 |

The boarding wait is not walking time. `order_pawn` never returns on arrival: its loop ends only at the tick limit or the
time limit (`JawaBenchTerrainTools.cs`, the wait loop) [measured, read]. It plays at normal speed, 60 ticks a second.
5,000 ticks take 83.3 s. So the wait ends at 83.4 s whether the colonists arrive in 5 s or never [measured].

**How many flights does deciding the bars need?**
- The bars are `gravship_keeps_connections`, `gravship_connectivity`, and the keep-wires part of `mod_settings`. One
  check decides all three: `sc_gravship`. `sc_owner_change` and `sc_settings` need no flight.
- **Two flights is the least today.** The mod reads the switch once, inside the engine's lift loop, for every anchor in
  the same instant (`CompAerialAnchor.GravshipAboardIds`). One flight has one switch value. The scene's text asks for both.
- **One flight is possible only if the Conductor accepts an offline test for "off".** "Off" returns a null aboard set, which
  is the ordinary removal path, and `AerialSelfTest` already tests that plan with null. What is left is one line: the
  switch guard. A test that fails when that guard is removed would decide it [guess ~70% that it is enough]. No such
  test exists. So the answer is two, and one is the Conductor's call. Landing cannot be skipped: the census reads the
  anchors on a map.
- **The two flights must share one staging.** Save the boarded ship, fly with the switch on, reload that save, fly with it
  off. The scene text asks for this save (`restore` in `scenes.json`); the driver builds the whole ship twice instead.
  A second lift from the landing tile would not do: the launch sets an engine cooldown, and `launch_check` refuses in it [guess ~85%].

**Does the ship-to-ground wire exist today? Half.** The driver already strings one mast on the ground to a mast aboard
and reads, after landing, that the ship keeps no link to it [measured, `gravship_scene.py`]. It does not read the ground
mast's end, because the origin map is destroyed at take-off. A `GravAnchor` left on the ground keeps the origin map
(`JawaBenchGravshipTools.cs`) [guess ~85%; no flight of ours used one].

**He asked to see the wire break. The mod does not break it: the design takes it down and coils it, and shows one message**
("Overhead wires to anchors left on the ground were taken down and coiled at launch", `CompAerialAnchor.cs`) [measured,
read]. `PlanRemoval` drops no cable at a launch, and the offline test holds that ("nothing falls"). A wire that snaps and lies on the ground would be a
change to the mod, not to the test. That is a design question for the Conductor. This study filed no ticket for it.

**One ship, one staging, both flights. What it carries:**

| on the ship | reading it serves |
|---|---|
| two wall-bracket anchors joined by a span (the scene text; today: masts) | switch on: link up after landing; off: link gone |
| a pair of masts with a second span; one span cut before take-off | a cut span aboard is kept too (the offline plan says so); no live reading today |
| battery and two consumers on floor conduit, one net asserted (scene text; today: 7 conduits and one lamp) | one net after landing; cords lie on the new net |
| a wall lamp, a styled lamp, a wall plug, a switch, a tangle and a run in each look | true-to-grid after landing, stub joins, looks, on the landed map |
| a floor conduit run that crosses the ship's edge to the ground | the run is two nets after take-off; no cord crosses the edge on the landed map |
| a mast on the ground strung to the ship; a second ground mast; a `GravAnchor` on the ground | link gone, ground end reads coiled (nothing fallen), origin map kept to be read |
| the pre-launch cord set, saved by the probe | the scene's own control: the old cord set must fail against the landed map. **Not run today** (below) |
| two picture points: take-off at the edge, and the landed ship | the pictures for his look |

**The scene that ran is thinner than its text.** `scenes.json` asks for brackets, a battery, two consumers and the planted
control; `gravship_scene.py` stages masts, one lamp and no battery, and runs no control. The PASS of visit 1 rests on the
thinner scene [measured, read]. The grouped scene must add them.

Cost: 256 s now. With the save, about 24 s of ship building, about 25 s of flight and reading, about 10 s of load and
second flight staging, about 25 s again: about 80 s. Saving about 175 s [guess ~70%]. Of that, 167 s is the
boarding wait alone [measured], and a wait that ends on arrival saves it without any grouping.
Conclusion in one line: **the flights were already the fewest, the staging was not, and the staging is small: 3 minutes of
143.** Other things in the same visit cost far more (section 8).

## 4. Pyrelands: what each long wait served [measured]

Waits inside the long checks (game ticks and seconds of `safe_advance`; a day is 60,000 ticks):

| check (chain) | ticks | game days | wait s | bars served |
|---|---|---|---|---|
| burn_line | 729,500 | 12.2 | 1,373 | `burn_line_walks`, `inv_burn_line_fire_clock` |
| ash_fertility_watered | 304,600 | 5.1 | 653 | `ash_fertile_when_watered`, `inv_ash_field` |
| fresh_burn_bonus | 527,500 | 8.8 | 1,019 (again 1,041 in a rerun) | `fresh_burn_compounds_with_black_rain`, `ash_fertility_probe` |
| grass_cover + embergrass_regrow | 1,155,100 | 19.3 | 1,505 | `grass_carpets_and_regreens`, `inv_embergrass_regrow` |
| scorchfruit_spoils | 270,160 | 4.5 | 353 | `scorchfruit_born_of_fire` |
| plant_census, then plant_census + scorchfruit | 59,860 then 81,160 | 2.4 together | 96 then 121 | `populations_are_the_biomes_own`, `scorchfruit_born_of_fire` |
| flamefang_venom (3 runs: 1 spoiled, 1 real, 1 planted) | 433,060 in the two long ones | 7.2 | 640 | `flamefang_bite_carries_venom` |

Repeats found [measured]:
- **`embergrass_regrow` waits 7 days for its first patch, then 7 days for three burned patches to age, then 5 days of growth.**
  The two 7-day waits are one after the other on different pads. They could be one wait.
- **`ash_fertility_watered` waits 5 days for crop rows on dry and wet strips.** That is the same kind of wait as regrow's
  5 growth days, on another pad, in clear weather.
- **`fresh_burn_bonus` burns a pad, waits a day, rains, then burns two more pads and waits 7 days.** The bonus fades
  on its own clock, so the second burn can share the first wait.
- **`plant_census` ran alone (109 s of process), then again inside `plant_census,scorchfruit_fire_born` (163 s).** The second
  holds the first. `grass_cover` ran alone (25 s with its reload), then again with `embergrass_regrow`.
- **48 site reloads, 718 s, about 15 s each**, one before every check. Most checks work on their own pad.
- `scorchfruit_spoils` polls nine half days and has its own pad.

The rerun of 08:13 to 08:49 asked again for three checks because the tier list gained one mod.

## 5. FlowWorks: what the acts served [measured]

**The visit measured the mod on three builds.** Build A (recorded sha 209d57476d) 17 rows, 1,273 s. Build B (recorded sha bc7dd578fd) 15 rows, 1,884 s.
Build C (f4971d58fa) 32 rows, 3,824 s. No row of A or B is the last row of its check. 26 of A's and B's 32 rows
were PASS, 2,541 s, and every one of those 26 checks ran again. The other 6 rows found scene faults and are not waste. The mod's source moved at 14:54 and 15:16, pump looks
and tank tables, while the visit ran (commits 6447d14771, f4971d58fa). The relation program reads a C# change as touching every check.

**Waits that staged nothing.** `ordered_job` and `order_pawn` wait in game ticks. With the game paused, no tick passes and
the call sits until its time limit, 15 s for `ordered_job` and 30 s for `order_pawn` (the tool's own page says "no ticks passed").

| caller | calls where the clock stood still | seconds |
|---|---|---|
| `concept_scenes.py`, `ordered_job` (default waitTicks 60, game paused) | 30 | 479 |
| `extension_proof.py`, `ordered_job` | 2 | 33 |
| `live_session.py`, `order_pawn` (waitTicks 1, `unpause=False`) | 8 | 245 |
| **total** | **40** | **757** |

The clock-still class is [measured] from 5 s tick windows for calls over 3 s. Four calls by hand showed 0 to 60 ticks in 15 s.

**Waits at normal speed (60 ticks a second):** 1,022 s in 128 calls. `sc_pawn_height` holds 620 s of it in two runs: one
colonist is ordered over 17 pads one cell at a time, out and back, with a fixed wait of 400 ticks (6.7 s) for each cell
(46 orders a run). One pad takes a colonist about 15 to 60 ticks [guess ~80%].

Loads: 122 in the visit, 674 s. One of them (inside `sc_source_pays`, 15:16) took 231 s; the cause was not looked for. A
scene loads the clean save, writes its own snapshot, plays, and loads the snapshot again. So the last load of one scene
and the first of the next restore the same clean save.

Raids: 13 in `sc_trench_cover`, `sc_pit_trap_raid`, `sc_fetch_fallen`. Raid tests are paused now.

Tier lists: `sc_source_pays` needed `fw_gss_sitting`: two restarts, 324 s, one check. `OL_OWNER_LOOK_READS` needed the
evening list: 234 s, one check.

Which check served which bars: `design/concepts/FlowWorks/version/test_table.json`, key `bars`. The map of scene to bars
was read for all 34 stage-6 checks; `sc_garden` (8 bars) and `sc_moat_raid` (16 bars) serve the most.

## 6. Explosive Knockback: what the acts served [measured]

- The two full-list restarts of visit 5 (1,178 s and 1,645 s) served `sc_barrage_perf` and `sc_walk_raid`, and then one
  planted fault. `sc_walk_raid` is gone. `sc_walk_blasts` and `sc_barrage_perf` now run on the small list, with no raid
  (commit 661658cd6b, 2026-11-23 22:55). So 2,823 s is already saved from the next visit [guess ~85%].
- 20 loads by the walk script (341 s) and 15 raids served `walk_storeroom_raid` and its planted fault. Replaced, as above.
- The rerun: 55 scene processes, 11.8 s start to start, 9.0 s each (median). Each process reads and writes the whole settings
  set: 96 `mod_settings_field` calls a process, 187 s in the 55. The waits cost 225 s, most of it in `sc_pit_fetch` [guess ~85%]. The scene
  process takes a comma list (`--scenes a,b,c`), so one process can stage several.
- One load, one map, 55 scenes: a good shape already. Only the process start and the settings set repeat.

## 7. Gimme Some Slack: other repeats [measured]

- **The proof was run twice on two mod lists.** `runC` (110 rows) on the 12-mod list took 259 s, `runE` (the same 110 rows) on
  the 13-mod list took 609 s. `runB` and `runF` (62 rows) took 169 s and 163 s. The table gives 4 scenes to the 13-mod list
  (`sc_true_to_grid`, `sc_cords_under_items`, `sc_shock_reach`, `sc_settings`). The second run also covered 106 rows that the first had read.
  On the 12-mod list two rows read UNMEASURED because they need FlowWorks.
- **The full list was loaded twice.** The first load and its rows (13:15 to 13:43, about 28 min) were voided by a mod
  fix found at 14:06; the second load took 1,155 s. Visit 2 started on the small list [measured, list change at 22:40], so it
  already has the better order.
- **10,792 `mod_settings_fields` calls, 345 s**: the probe mailbox. A nit (last section).
- `quick2.py` built a map on the full list in 100 s and `human_review.py` in 45 s.

## 8. The grouped design, with the cost of bundling

A bundle has one price: one spoiled staging loses all its readings. And a bundle must still name which reading failed. A third price:
our rule says that after a change only the touched checks run again, so each part of a bundle must stay runnable alone.

| group | fewest stagings that decide every bar, and what each carries | cost of bundling |
|---|---|---|
| Gravship (Slack) | 1 boarded-ship save; 2 flights from it; contents in section 3 | a spoiled save is remade in about 30 s; each reading has its own row; a bad ship costs both flights |
| Field weeks (Pyrelands) | 1 map, about 14.6 game days: day 0 burn pads, rain, read on day 1 to 7; regrow patches from day 2.6; 7-day reads; crop strips and growth from day 9.6. Serves `fresh_burn_bonus`, `embergrass_regrow`, `ash_fertility_watered`, `scorchfruit_spoils` | a wild animal, a stray fire or a raid spoils a long run (visits 7 and 8 lost several). Save on day 2.6 and day 9.6, so a spoil costs one part. Rain must be over before the dry patches start. Setting switches flipped in one chain (fresh-burn bonus, water fertility) must be flipped back while paused, or be a separate part. `burn_line` stays alone: it drives the burn switches |
| Short chains (Pyrelands) | about 5 shared site loads for the short chains on separate pads; the long and the map-wide chains keep their own (about 20 loads in all, 48 today) | a chain that leaves fire, weather or a setting spoils the next. Each chain's own teardown must be read before the next starts; else reload. `fire_incident`, weather and letter chains stay alone |
| Repeated chains (Pyrelands) | run `plant_census` only inside the scorchfruit chain; `grass_cover` only inside regrow | none: the second run reads the same rows again |
| Rerun only on the changed list (Slack) | on the 13-mod list run only its 4 scenes and the 2 FlowWorks rows | if the 13-mod list breaks something else, it is found only by the 12-mod run or the walk |
| Walk one colonist once (FlowWorks) | one walk over 17 pads and back, every value read on every tick | a stuck colonist loses 34 readings; the per-tick record names the pad |
| Waits (FlowWorks, Slack) | no grouping: an order with no wait, then a fast advance that ends on the state | none |
| Scene batch (FlowWorks) | one clean load between scenes, not two | a dirty snapshot reaches the next scene. Read the fingerprint before each scene (the code has one) |
| One process for many scenes (Knockback) | groups of 8 to 10 small scenes, one settings set | one crash loses the group; each scene still prints its own verdict |

## 9. Ranking by wall time saved per visit

| rank | group | mod | saved per visit | basis | build |
|---|---|---|---|---|---|
| 1 | Hold the mod still during a visit; a C# change must not void every row | FlowWorks | up to 42 min | 26 superseded PASS rows, 2,541 s [measured]; that the change could have waited for the visit's end [guess ~70%] | small (a rule); medium (the relation program reads C# by member) |
| 2 | Field weeks | Pyrelands | about 36 min | 3,530 s of waits for 2,257,360 ticks (37.6 days) in the four checks [measured]; about 14.6 days and 1,380 s at the same 640 ticks/s [guess ~55%] | large |
| 3 | Run the full-list part last | Slack | about 28 min in a visit with a fix | first load and rows voided [measured]; visits 1 and 2 each had a fix [measured] | none: visit 2 does this |
| 4 | Full-list loads retired | Knockback | 47 min | 1,178 + 1,645 s [measured]; already changed tonight | none: done |
| 5 | Waits that stand still or that play slowly | FlowWorks | about 12 min (clock still, 757 s) | [measured]; saving the whole of it [guess ~85%] | small |
| 6 | Walk one colonist once | FlowWorks | about 9 min | 620 s in two runs [measured]; about 80 s after [guess ~70%] | medium |
| 7 | Rerun only on the changed list | Slack | about 11 min | 609 + 163 s [measured]; about 100 s after [guess ~65%] | medium (the proof has only block selection, "for debugging") |
| 8 | Short chains share a site load | Pyrelands | about 5 min | 718 s [measured]; 48 loads to about 20 [guess ~50%] | medium |
| 9 | One process for many scenes | Knockback | about 5 min | 150 s of process gaps and 187 s of settings [measured]; saved [guess ~60%] | small |
| 10 | One list for `sc_source_pays` and the owner-look check | FlowWorks | about 4 min | 324 + 234 s [measured]; one list can hold both [guess ~40%] | small |
| 11 | Gravship, one staging | Slack | about 3 min | 256 s [measured] to about 80 s [guess ~70%] | small to medium |
| 12 | Repeated chains | Pyrelands | about 2.5 min | 127 s and 25 s [measured] | small |
| 13 | Scene batch | FlowWorks | about 2 min | 95 loads, 335 s without the 231 s hang [measured]; a third of it [guess ~50%] | medium |

Ranks 3 and 4 need no work. Ranks 1, 2 and 5 are the largest open ones. Rank 1 is not a shared staging: it is a visit
that staged everything twice. Planted-fault reruns were left out: they belong to the checker, not the mod.

## 10. What the scene library can express today

Built today: `scene.open`, `s.run`, `s.raw` (`scene.py help`, read 2026-11-24). The other seven names answer `NOT_BUILT`. A run
that used a changing `s.raw` call is stamped EXPLORED and counts for no bar. So **no group can give a counting verdict
through the library yet**: `contract` and `judge` are `NOT_BUILT`. The column says what is missing beyond those two.

| group | expressible now | needs |
|---|---|---|
| Waits (rank 5) | yes: `s.run(until, limit, speed)` ends on the state, at any of the four speeds | the order itself: `s.act` (`order`, `job`), `NOT_BUILT`; `s.raw` until then |
| Walk one colonist once (rank 6) | the walk: `s.run(record=...)` keeps a value for every tick | `s.stage` for the pads and the colonist, `s.act` |
| Gravship (rank 11) | the boarded ship as a fixture save: `scene.open(needs={"map": ...})`; each flight's waits: `s.run` | `s.stage`; a launch verb and a land verb (the verb list of `s.act` has none); `s.shot`; `s.read` |
| Field weeks (rank 2) | the 14.6 days: `s.run` with limits, and daily records of named fields; checkpoints by a fixture save | `s.stage` (pads, terrain, plants), `s.act` (`weather`, `tune` for the switch readings), `s.read` for the fertility probe |
| Short chains (rank 8), repeated chains (12) | no need of the library: they run in `northstar_driver` | - |
| Scene batch (13) | partly: one `open` and several runs in one session | `s.stage` cleans a station between scenes |
| One process for many scenes (9) | no need: `knockback_runner.py --scenes a,b,c` | - |
| Rerun only on the changed list (7) | no need: a row filter in `proof_all.py` | - |
| Ranks 1, 3, 10 | not a scene matter: order and lists | - |

The library can have a direct effect on ranks 2, 5, 6 and 11 [guess ~75%].

## 11. UNMEASURED, with the cause

- Where the visit agents' own time went between scripts (Slack 89 min, FlowWorks 71 min, Knockback 75 min): no record of
  an agent's reading, building or deploying is keyed to a visit. It is not test time, so this study does not class it.
- What each raid cost in scene time: no record splits a scene's length by cause.
- The bars each act served on Slack's proof: 170 of the 206 rows are support rows mapped to bars in `test_table.json`; this study
  did not read all 206 one by one. It read those of `sc_gravship` and the named scenes.
- The wall time of the Knockback rerun's first restart before the list change.
- What the 231 s load and the 290 s restart were for.
- Which FlowWorks and Pyrelands groups keep every verdict: shown by no run. Each group's saving is an estimate.
- Pictures during a take-off: none was ever taken. UNMEASURED if they come out.

## 12. Nits (one line each, no ticket)

- `mod_settings_fields`, 10,792 calls in Slack visit 1, 345 s, is the probe mailbox; a direct call would cost a quarter or less [guess ~60%].
- `order_pawn` and `ordered_job` read "waited and stood still" only after they end; the result has `pausedDuringWait`, and no script reads it.
- `gravship_scene.py` writes `status PASS` with no control row.
- The visit summary of Slack visit 1 does not say why the game was restarted at 14:33.
- The 12-mod and 13-mod list runs use the same row ids, so a reader of the table cannot tell which list a row came from without its environment lines.
