# Northstar live job queue — 2026-10-01

Bridge work that is ready to run, so the next agent holding the bridge can start at once and never
sit idle. Each job is a script under `src/RimMandrake/Utils/modcheck/live_queue/`. Each job prints one
verdict line and appends one JSON record to `Transient/modcheck/live_queue_results.jsonl`.

The verdict is one of:

- `MEASURED PASS`: every check was answered and passed.
- `MEASURED FAIL`: the game was read, and the failing checks are findings to file.
- `UNMEASURED`: the job could not ask the game (bridge down, tool missing, setup refused). This is
  never a verdict.

What is known so far: the scripts were built and tested **offline only**, against `rimdrive.fake.FakeWorld`.
All jobs pass their dry runs, and `selftest_live_queue.py` proves that every criterion can FAIL. **No job has
run live.** The results file is where job state lives. This doc never records it.

## How to start

```
python.exe src/RimMandrake/Utils/modcheck/live_queue/run_next.py --all
```

- `run_next.py` runs the next unfinished job. With `--all` it works through every remaining job in order,
  each in its own process (rimdrive allows one Session per process).
- A job counts as **done** once its latest live record is `MEASURED`, whether PASS or FAIL. A measured FAIL
  is a finding, not a reason to re-run.
- An `UNMEASURED` job is offered again. `--all` moves past it instead of idling on it.
- `--list` shows the queue state. `--job bland_tile` runs one job regardless of state. `--dry-run` rehearses on
  FakeWorld, and its results and outputs go to the temp dir, never to the repo.
- Exit codes: 0 PASS, 1 FAIL, 2 UNMEASURED, 3 queue done.

Run it from the repo root under **`python.exe`**. The bridge binds Windows loopback, and WSL python cannot
reach it.

## Session setup (once, before launch; WSL `python3`)

1. `rimflow bridge who`, then `rimflow bridge take --for "northstar live queue preflight..motion_frames"`.
2. If RimWorld is running, quit it. The next step refuses while it runs.
3. `python3 src/RimMandrake/Utils/modcheck/live_queue/prep_wsl.py --apply`. This does three things:
   - runs `modlist_swap --minimal --apply`, which captures FULL first;
   - deploys every suite mod with `deploy_custom_mods --apply`;
   - composes every suite mod's packageId onto the end of `activeMods`.

   The suite set is **derived** from `infrastructure/state/modcheck_status.json`. On 2026-10-01 that was 13
   mods: Aftermath, Antiquities, Droidworks, FlowWorks, Inhabited, JawaIonWeapons, Ninefold, PawnFlavor,
   Pyrelands, ResearchRetag, ShipMemory, StarWarsRaces, StructureInjections. Run it with no flags to see the
   plan only.
4. Check the companion DLL is the one carrying `JawaBenchSituationalTools.cs` (it is deployed from
   `bridgetools/build.py --gm --apply`). preflight checks this live and FAILs if it is not.
5. Launch through Steam, never the bare exe:
   `powershell.exe -NoProfile -Command "Start-Process 'steam://rungameid/294100'"`. Then run the queue.
   preflight starts the quicktest map itself if none is Playing.

## Jobs

The jobs run in this order, all inside one game session. bland_tile leaves the bland map **current**, so companion_live and motion_frames
run on it.

### preflight preflight — `preflight.py`
Checks that this game session is the one the queue needs:
- a Playing map exists (it runs `runner.ensure_playing_map`, which starts the quicktest world if needed);
- every tool the queue drives is in the live tool census, including motion_frames's FlowWorks reads;
- `jawa/pawn_census` answers;
- the damage recorder has both its hooks installed;
- every suite mod is in the live `ModsConfig` activeMods (parsed with ElementTree, never grepped).

**Fails when** a tool is missing, the recorder is not installed, or a suite mod is not active. If so, the
deploy or the compose did not take: fix that, then re-launch.

### situational_rerun situational re-run of every suite — `situational_rerun.py`
Runs `runner.run_suite(..., situational=True, policy="abort")` for every suite. It calls it directly,
because the swap, deploy and compose already happened in setup. This uses the fixed runner (`f9d1b4c70`),
under which python.exe runs end to end and Antiquities' reading chain declares `tick_cap`. Each mod's
summary goes to `Transient/modcheck/live_queue/situational_rerun/<Mod>_summary.json`, and the record
carries a digest per mod (refused, verdict counts, surprises, serious detectors).

**Fails when** any of these happens:
- a suite raises out of `run_suite`;
- **FlowWorks is refused** (its validated floor was 38/38, so it should now run);
- any component is UNMEASURED by `BudgetExceeded` (the Antiquities chunking did not hold);
- a chain could not establish a bland map;
- a recorded surprise has no sidecar or png on disk.

Surprises are **listed, not failed**. Deciding whether a hit is the chain's own act is a reading of that
chain. For example, Ninefold's induced mental break was a false surprise on 10-01. The fix for that is a
declared expectation in the suite: `t.expect("mental", {...})`, or `"incident"` for a scheduled incident.
Both kinds are new and come from companion_live.

⚠️ The detectors now read the companion directly (companion_live). That can surface **new** surprises in suites that
damage or break their own colonists on purpose. Before filing any surprise from the `colonist_damaged`,
`predator_hunting`, `mental_break` or `incident_queued` detectors, check whether the chain caused it.
`--mods A,B` re-runs a subset after a fix.

### abort_proof abort-path proof — `abort_proof.py`
The abort path has never fired live: no real hazard occurred in the 10-01 pass. Each case opens its own
Watch, which does the bland prep and takes a baseline. The case then applies ONE hazard and sweeps, either
with `check()` or a short wait. The next case's bland prep cleans up after it: it kills hostiles and
wildlife, extinguishes fires, calms pawns and resurrects the dead.

| case | hazard | must abort via |
|---|---|---|
| control_quiet | nothing; wait 1200 | must NOT abort, and no SURPRISE/FATAL hit |
| hostile_raid | 3 `Tribal_Warrior` spawned hostile at the anchor | `hostile_pawns` |
| fire_near_colonist | `map_fire` on a 3x1 rect 4 cells from a colonist; wait 60 | `fire_on_map` |
| colonist_killed | a player `Colonist` spawned after the baseline, then killed | `colonist_died` (FATAL) |
| predator_hunts_colonist | `Wolf_Timber` 15 cells away, `ordered_job PredatorHunt` on a colonist | `predator_hunting` |
| colonist_berserk | `pawn_force_mental_break Berserk` on a colonist | `mental_break` (FATAL) |
| raid_queued | `incident_schedule RaidEnemy` with a delay of 30000 | `incident_queued` |
| control_declared | far hostile + benign incident, both declared by the test; wait 60 | must NOT abort |
| runner path | a Suite whose component meets a hostile, run through `runner.run_suite` | component UNMEASURED naming `hostile_pawns` |
| control_after_cleanup | nothing; wait 600 | must NOT abort (cleanup worked) |

**Fails when** a hazard does not abort, aborts with kind `harness`, aborts on the wrong detector, leaves no
sidecar json, or leaves the game unpaused. It also fails when any control aborts. The evidence is under
`Transient/modcheck/live_queue/abort_proof/<case>/`.

### bland_tile bland tile — `bland_tile.py` (NORTHSTAR_BLAND_TILE_1)
**The quicktest world is re-rolled every launch.** Tile 4375 was bland on 10-01, but that is only a
preference. Each run picks the tile again:

1. `world_tile_export`, then filter for Flat terrain, AridShrubland or Desert biome, swampiness 0,
   elevation 0 to 400, and temperature 15 to 30 C. (On 10-01 that filter left 89 candidates.)
2. `world_tile_get` must show mutatorCount, roadCount and riverCount all 0.
3. `colony_found(tile)`, then `world_tile_map_generate(tile)`, then `set_current_map(mapIndex)`.
4. `destroy_bulk factionlessAnimals`. The map arrived with 47 wildlife on 10-01.
5. Spawn 3 player colonists at the map centre.

**Fails when** any of these holds:
- no candidate is free of mutators, roads and rivers;
- the colony or map step refuses;
- finalize steps failed;
- the map is not current;
- wildlife remains;
- fewer than 3 `isColonist` pawns are in the census;
- `list_things group=BuildingArtificial` finds non-player buildings (ruins);
- `helpers.assert_bland` reports problems;
- a 2000-tick idle Watch sees any SURPRISE/FATAL.

Untested live: whether `world_tile_map_generate` builds the map for the Settlement that `colony_found`
just placed. If it refuses, the job reports UNMEASURED with the tool's message. Next step after that: run
`world_tile_map_generate` first and settle second.

### companion_live companion detectors live — `companion_live.py`
This is the live half of the companion detector work. The offline half is
`modcheck/selftest_companion_detectors.py` (16/16 on FakeWorld).

The detectors now read `jawa/pawn_census`, `jawa/damage_log` and `jawa/incident_queue_peek` **directly**,
where they used to infer:
- **mental_break**: the census `mentalState` and its `isAggro`. `list_pawns` has no mentalState at all, so
  before this only the letter path could see a break.
- **predator_hunting** (new): census `isPredatorHunting` + `preyId` on a player pawn. Proximity no longer
  stands in for intent.
- **colonist_damaged** (new): damage events with the game's own damageDef, instigator and weapon. The
  hediff-inference detector skips any injury a damage event already explains.
- **colonist_died**: now corroborated by `damage_log` kill events.
- **incident_queued** (new): a queued incident is seen before it fires. A threat is SURPRISE; anything
  else is WARN.

`Watch` probes for the companion once, at enter. If it is absent, the detectors fall back to inference.
That is reported as `companion: false` in the chain summary, never as silence.

This job checks each detector's **evidence**, not just its name:
- census and `list_pawns` agree on the living pawns;
- a Cut 3 yields `colonist_damaged` via damage_log with damageDef Cut, and no duplicate inference hit;
- Wander_Sad yields `mental_break` via the census, with isAggro false, at SURPRISE (not FATAL);
- a hunting wolf yields `predator_hunting` with preyIsColonist true;
- a benign queued incident yields `incident_queued` WARN and does **not** abort;
- a kill puts `damage_log_kill` among colonist_died's sources.

**Fails when** a direct-read detector does not fire, or fires without its direct-read evidence.

### motion_frames FlowWorks motion-frames capture (stub) — `motion_frames.py`
This job **captures only. Nothing is judged.** The owner deferred the frame-sequence judge on 2026-09-17,
as recorded in `NORTHSTAR_MOTION_FRAMES_1`: *"file it as TBD ... until we can play with it live first"*.

The setup is FlowWorks plot C, built through the suite's own helpers (`_prep_plot`, `_limitless_source`,
`_channel_from`, `_dig_run`): a 1x10 D=1 channel dug from a limitless WaterDeep body. The job then takes
8 frames of the same cell rect, one per engine pulse (250 ticks), and reads each frame's fill vector from
`flowworks_excavation_report`.

It writes `Transient/modcheck/live_queue/motion_frames/motion_manifest.json` for the owner to look at.
That file holds the frames, ticks and fill vectors, and names the bars
`canal_fill_front_watchable` and `canal_fill_spreads_along_itself`.

**Fails when** there are fewer than 8 valid PNGs, all frames are byte-identical, the fill vector did not
advance between the first and last frame (the engine's state is the motion witness), or a surprise aborted
the capture. The other motion bars reuse the same loop with their own plot once this one has run live:
reservoir draw-down, shoreline recession, tar lagging water, and a pawn lowering into a deeper cell.

## Teardown

1. Look at the queue state with `run_next.py --list`. File each MEASURED FAIL as a finding against its item:
   situational_rerun against NORTHSTAR_SITUATIONAL_ROLLOUT_1, bland_tile against NORTHSTAR_BLAND_TILE_1, abort_proof and companion_live against
   NORTHSTAR_COMPANION_GAPS_1.
2. Quit the game, then `python3 src/RimMandrake/Utils/modcheck/live_queue/prep_wsl.py --restore`.
3. `rimflow bridge release`.
4. Commit `Transient/modcheck/live_queue_results.jsonl` and the job folders under
   `Transient/modcheck/live_queue/` with explicit paths.

Flip `--situational` to the default (NORTHSTAR_SITUATIONAL_ROLLOUT_1) only once all of these hold:
- abort_proof is MEASURED PASS (the abort path is proven live);
- situational_rerun is MEASURED with every surprise attributed;
- companion_live is MEASURED PASS.
