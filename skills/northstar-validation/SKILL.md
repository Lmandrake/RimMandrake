---
name: northstar-validation
description: Run a mod's north-star suites live without the harness eating the sitting — the bland world (generated per game, or the saved BLAND_NORTHSTAR_BASE), the situational envelope (`modcheck run --situational`, watch.Watch, clockgate, surprise evidence, declared expectations), the live_queue jobs (run_next.py, preflight..bland_base, rollout_gate), the companion-reading detectors (pawn_census, damage_log, incident_queue_peek), the playbook for interference (naming dialogs, focus theft, late bridge replies, dirty worlds, extra maps, starvation, the test's own events), and the time ledger of where a live pass's minutes went. Use before any northstar or situational run, when a chain aborts on a surprise and you must decide whether it is the mod, the world or the test's own act, when a live pass is slow or keeps dying on harness defects, when choosing between reset, a saved world and a relaunch, and before flipping --situational to the default.
---

# North-star validation: make the world boring, then let the detectors speak

A north-star suite proves the lines of the `## north star` section of a mod against the running game. The suite is
`src/Rim*/<Mod>/validation.py`. `src/RimMandrake/Utils/modcheck/runner.py` runs the suite. The usual trouble of a live
pass is not the mod. In the live pass of 2026-10-01, a clean run of all suites took **8% of 210 minutes**. The rest went
to harness defects, a dirty world and a tick rate that collapsed (§6). The owner's answer, 2026-10-01:

> *"We need to establish testing worlds and make them as static and boring as possible. We're being
> eaten alive by random events, naming dialogs, the lot. Every time we encounter these things, let's
> upgrade the Northstar system and testing scripts so they handle anything, go faster, etc."*

Two rules follow. An interference is anything that is not the test and disturbs the test.

- **Every interference you meet is fixed in the tooling, with a selftest, the first time.** Never click past an
  interference for one run.
- **Every threat that appears during a test is logged and gets a test-environment item** (owner, 2026-10-13, by card).
  The job of the item is to stop that threat next time.

For related work, read the neighbour skill:

| work | skill |
|---|---|
| write or read the rows of a proof | `live-debugging-proof-harness` |
| start a throwaway map | `rimworld-debug-testing` |
| drive the bridge | `rimbridge` |
| deploy before a test | `rimworld-deploy` |

The design of record is `design/RimMandrake/northstar_helpers_plan.md` (§10 overrides §§3–8 where they differ). Evidence
and old lines that left this file are in `references/history.md`.

## 1. The bland saved world

A bland world is a test world with no features. The bland world:

- is flat, dry and temperate;
- has no ruins, no wildlife, no strangers and no queued incidents;
- has a named colony, three colonists and one map.

There are two ways to get a bland world. Both live in `src/RimMandrake/Utils/modcheck/`.

**Generated per game — `bland_world.py`.** `runner.run_suite` uses this path when it gets `bland_world=True`. The caller
that passes it is `live_queue/situational_rerun.py --bland-world`. `modcheck run` has no such flag.

| call | does | when |
|---|---|---|
| `setup(session)` | does the steps below | once per game |
| `reset(session, expected_ids)` | removes hostiles, wildlife, strangers, hives, corpses, fires, queued incidents, injuries, hunger, a pending retile or pond. **Then the call reads the world back** and returns the problems that are left | between suites (`runner.run_suite(bland_world=True)`) |
| `assert_world(session, ruins_too=False)` | only verifies; `[]` means bland | after a suite |
| `feed_colonists(session)` | tops up Food only when it is LOW; also tops up FlowWorks' `RM_Thirst` when it is low | every Watch chunk |
| `retile(session, biome)` / `paint_pond` | gives a suite its biome, or open water, while the suite runs. The change is restored after the suite | `--retile`, or the suite sets `suite.biome` / `suite.water` (both need `bland_world=True`) |

`setup` does these steps in this order:

1. Export the tiles. Keep the Flat tiles of `DRY_BIOMES` at 15–30 °C.
2. Skip a tile that has mutators, roads or rivers.
3. Call `colony_found`. Skip a tile that an earlier call settled in this game.
4. Call `world_tile_map_generate`, then `set_current_map`.
5. Call `destroy_bulk nonColonists` **before** the colonists spawn.
6. Destroy the ruins with `destroy_batch` (5 passes at most).
7. Spawn the colonists.
8. Name the colony and close the naming dialogs. `setup` also does this before and after it generates the map.
9. Call `reset`, then `assert_world(ruins_too=True)`. The result holds the problems that are left.

The code already handles these traps. Do not find them again:

- **The quicktest world is re-rolled every launch.** A tile number is a preference (`HINT_TILE`), never a fact.
- The campaign world has no vanilla AridShrubland or Desert tile. So `DRY_BIOMES` also holds `ZBiome_Grasslands`.
- `destroy_bulk factionlessAnimals` misses the **hostile-faction insects** that a generated map can arrive with. Use
  `nonColonists`, and use it before the colonists exist.
- `SteamGeyser` and `VHGE_GasGeyser` are in the `BuildingArtificial` group, but both are natural and cannot be destroyed.
  The code calls them `NATURAL_SCENERY`, not ruins.
- The ruins of a quicktest map are not residue of a hazard. So only `setup()` checks ruins.
- `colony_found` refuses a tile that is already settled. One game cannot found the same tile again.
- When no unsettled candidate is left, `setup()` uses the current map again, if that map is on a candidate tile. `setup()` then keeps
  the oldest three colonists, destroys the other player pawns and calls `reset`.

**Saved — `saved_base.py` + `live_queue/bland_base.py`.** The owner's target: *"name the colony once and SAVE; load the
save per suite"*.

- `bland_base` builds the world once. Then `bland_base` calls `induce_and_finish_naming`, so no naming dialog can come
  back. Then `bland_base` proves `assert_bland`.
- `save_base` backs up Saves and writes `BLAND_NORTHSTAR_BASE`. `save_base` then **proves that a NEW file appeared and
  that no other save changed** (autosaves are not checked). The reason: `save_game` has written the wrong slot.
- `world_reset()` loads that save. A load replaces the game, so no stale map survives. When the load fails,
  `world_reset()` falls back to a cleanup of the current world and says so (`method`).
- ⚠️ Before you rely on the saved world, check two things:
  - Is `world_reset` wired into `runner.py`? Use `grep`. When this line was written, it was not.
  - Does the save exist already? `bland_base` is write-once: the job refuses when the save exists.
- These saves are disposable test saves, not canonical world saves (`infrastructure/state/CANONICAL_SAVE.md`).

## 2. The situational envelope

`modcheck run <Mod> --situational [--policy abort|record]` wraps every chain in a `watch.Watch`
(`src/RimMandrake/Utils/modcheck/watch.py`). A chain is one named group of checks in a suite. A component is one check in
a chain. Python enforces the envelope. No code asks a model when to stop.

- **Time moves only through `clockgate.step`** (`clockgate.py`).
  - The gate charges the MEASURED `ticksGame` delta, never the requested n.
  - A request over `remaining()` raises `BudgetExceeded` **before** the clock moves.
  - `Watch` cuts a long wait into chunks (`DEFAULT_CHUNK = 600`).
  - Each chain has a tick budget (`watch.DEFAULT_SESSION_CAP`, 60000). A wait of 95 000 ticks is over that budget. Such
    a chain declares its own budget with `tick_cap=` on `@suite.chain`. Without `tick_cap`, the
    component reads UNMEASURED by budget.
  - `clockgate.step` and `B.ticks` both go through `clockgate.advance_chunk`. That function prefers `jawa/safe_advance`
    (many ticks per frame).
  - Do not add raw `step_game_ticks` calls beside `clockgate.advance_chunk`. Do not add a loop of "advance, then read".
- A north-star script follows the Lightspeed contract (exit 0/1/2, deterministic rows, named UNMEASURED reasons):
  `skills/live-debugging-proof-harness/references/lightspeed-authoring.md`.
- **After every chunk, the envelope takes a full snapshot and runs a detector sweep** (`snapshot.py`,
  `detectors.sweep`).
- **The first SURPRISE/FATAL captures evidence before anything else** (`surprise.py`). SURPRISE and FATAL are the two
  highest severities of a detector hit. The capture has three steps:
  1. Pause the game and verify the pause. Never step a tick to refresh the frame, because a step changes the evidence.
  2. Write the sidecar atomically. The sidecar is the JSON file that holds the structured evidence.
  3. Take one screenshot.
- Then the policy applies. `abort` raises `SurpriseAbort`. The component is **UNMEASURED with the evidence named — never
  FAIL against the mod**. `record` is for diagnostics only. The visitor rule below is the exception to the abort.
- **When the world cannot be made bland, every component of the chain is recorded UNMEASURED.**
- **Visitor rule** (owner card 2026-10-10). The visitor detectors are `contract.VISITOR_DETECTORS`.
  - No evidence that a visitor disrupted a colonist or a subject: the visitor is recorded, then removed by id. The run
    stays clean.
  - Evidence of disruption: the chain aborts.
- **Disturbance verdicts** (owner card 2026-10-13): *"if telemetry detected an anomaly that was corrected
  and there is no evidence of damage to the test, it can PASS still. If there's any sign of damage to the
  test itself … test is restarted."* Damage to the test is a restart, never a FAIL.
  - Class the spoiled run. The class is ENVIRONMENT FAULT only when the record shows that something outside the tested behaviour
    did the damage. If the mod could have done the damage, the run is UNRESOLVED. If our script, tool or
    staging did the damage, the run is an APPARATUS FAULT.
  - A forbidden effect is a MOD FAILURE, even in a spoiled run.
  - Full text: `design/RimMandrake/standing_rulings.md` §Live tests have three kinds; `design/RimMandrake/debug_process.md`
    § "Test disturbances".
- Every exit path pauses the game, verifies the pause and restores the settings. A step that fails is in
  `close_problems` of the summary. Read that field.

**Declare what the test causes itself**, or the envelope aborts on it (`detectors.Expectations`).

- In a suite, call `t.expect(kind, matcher, until_tick=, max_count=)`. The kinds are `hostile pawn letter condition fire
  litter mental incident raid`.
- On the watch itself, `w.expect` also takes `phase=`. `t.expect` does not.
- For anything that the test spawned, also call `w.expect_fixture(pid)`.
- Bound each expectation (`max_count`, `phase` or `until_tick`). Never declare by mod package.
- An expectation quiets the detectors only. The latch of `jawa/safe_advance` can still stop the clock (§5).

These four false surprises were measured. A declared expectation cures each one:

- the mental break that Ninefold induces;
- the wild droid of Droidworks that goes ManhunterPermanent;
- the hostiles that Aftermath makes itself;
- the death in the birth outcome of Ninefold.

The item `NORTHSTAR_SITUATIONAL_ROLLOUT_1` covers the flip to `--situational` by default. Its gate is
`python3 src/RimMandrake/Utils/modcheck/live_queue/rollout_gate.py`. The gate reads the latest abort-only pass. Exit 0
needs all of these:

- the pass is MEASURED PASS;
- the pass ran at or after the newest commit of the gate file. A later change of the envelope is a note, not a failure;
- the pass covers every suite on disk that composes onto the minimal list (`suite_set.py`);
- the status registry (`infrastructure/state/modcheck_status.json`) holds no key without a mod folder. To clear such a
  key, use `rename-key` or `forget-key` of `modcheck/cli.py`.

Exit 1 prints each reason. Exit 2 means that no record exists. Read the item's state. Never say from memory that the
flip is done.

## 3. live_queue: bridge work ready the moment you hold the bridge

The jobs are in `src/RimMandrake/Utils/modcheck/live_queue/`. The doc is
`design/RimMandrake/northstar_live_queue_2026-10-01.md`.

```
python.exe src/RimMandrake/Utils/modcheck/live_queue/run_next.py --list | --all | --job <id> | --dry-run
```

- **Use `python.exe`, from the repo root.** The bridge binds Windows loopback.
- One process can hold one Session. So `--all` runs each job in its own process.
- Exit 0 PASS · 1 FAIL · 2 UNMEASURED · 3 queue done (or an unknown job id).
- A job is **done once its latest live record is MEASURED** (PASS or FAIL). A measured FAIL is a finding to file. A
  measured FAIL is not a reason to run the job again.
- `run_next.py` offers an UNMEASURED job again.
- Each record is appended to `Transient/modcheck/live_queue_results.jsonl`. Job state lives there, never in a doc.
- Every job is rehearsed offline on `rimdrive.fake.FakeWorld`. `selftest_live_queue.py` proves that every criterion can
  FAIL.

`jobs.py` is the list of jobs:

| job | what it does |
|---|---|
| `preflight` | checks that a map is Playing, every tool is in the live census, the recorder hooks are in, and the suite mods are in the parsed ModsConfig |
| `situational_rerun` | runs every suite that composes onto the minimal list, with `--situational --policy abort`. Run the file directly for `--bland-world`, `--retile`, or `--mods A,B` (a subset): `run_next.py` passes only `--dry-run` |
| `abort_proof` | one hazard per case. Each hazard must abort on the RIGHT detector, with its sidecar and the game paused. The harmless visitor case (`hostile_raid`) must be recorded and removed, with no abort. The controls must not abort |
| `bland_tile` | builds a bland tile map and proves it bland |
| `companion_live` | proves the detectors of §4 live |
| `motion_frames` | captures frames; judges nothing |
| `bland_base` | one-time: writes the saved world of §1 |

Set up the session in this order:

1. Run `rimflow bridge take`.
2. Quit the game.
3. Run `python3 …/live_queue/prep_wsl.py --apply`. This script swaps to the minimal list, deploys every suite mod and composes
   their packageIds. With no flags, it only prints the plan.
4. Launch the game through Steam.

## 4. Companion detectors

The detectors are `detectors.py`: pure functions over a snapshot. The severities live only in `SEVERITY` and
`LETTER_SEVERITY` there. The detectors read the JawaBench companion **directly** instead of inferring
(`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchSituationalTools.cs`):

| detector | reads now | read before |
|---|---|---|
| `mental_break` | `jawa/pawn_census` mentalState + isAggro | letters only (`list_pawns` has no mentalState) |
| `predator_hunting` | census isPredatorHunting + preyId on a player pawn | proximity, in place of intent |
| `colonist_damaged` | `jawa/damage_log` damageDef, instigator, weapon | inference from hediffs (`colonist_injured_unexpectedly` infers, and now skips an injury that a damage event explains) |
| `colonist_died` | corroborated by `damage_log` kill events | row / Death letter / story stats |
| `incident_queued` | `jawa/incident_queue_peek`: the incident is seen before it fires. A threat is SURPRISE, else WARN | nothing |

`Watch` probes the companion once, at enter. When the companion is absent, the detectors fall back to inference. The
summary then says `companion: false`, never silence. The offline proof is `selftest_companion_detectors.py` and
`selftest_detectors.py`. The live proof is the `companion_live` job. That job checks the **evidence** of each detector, not only
the name.

A direct read shows **new** surprises in suites that hurt or break their own colonists. Before you file a
`colonist_damaged`, `predator_hunting`, `mental_break` or `incident_queued` hit, ask if the chain caused the hit. If the
chain caused it, the fix is a declared expectation in that suite (§2). The fix is not a detector change.

## 5. Interference playbook

Every row was measured live and is fixed in code. If one comes back, the fix regressed. Find the regression; do not work
around it.

| symptom | cause | fix in the tooling |
|---|---|---|
| `modal_open` aborts every chain after a colony is founded | `Dialog_NamePlayerFactionAndSettlement` / `Dialog_NamePlayerSettlement` force a pause. They come back every ~1000 ticks until the colony is named. Closing one never sticks | `jawa/name_colony` at setup (`bland_world.close_naming_dialogs`, `saved_base.induce_and_finish_naming`); `modal_open` ignores `Dialog_NamePlayer*` |
| a suite and every later one die on `unexpected response id` | a heavy step outlives the client timeout. Its late reply lands on the same socket | `rimbridge_client.py` drops the late replies of timed-out requests. ⚠️ Still: **no side-connection probes while a runner drives**. One driver means one connection |
| UNMEASURED "could not bring RimWorld forward" | the owner's browser was in front; `AttachThreadInput` was refused | Turn on Options > Run in background. `game_focus.preflight` checks that preference. `game_focus.focus_game` refuses to take the focus unless `RM_FOCUS_OPT_IN` is set. With the opt-in, it has an Alt-tap + AppActivate fallback. Never fullscreen the game or take the focus |
| tick rate collapses 416 → 50 ticks/s | each `setup()` generated a new map and kept the old ones (the focus is also suspect) | one map: load the saved base, or relaunch (36–38 s) between full runs. Compare TPS only between equal map counts (`src/RimMandrake/Utils/sim/csuite_tps.py --compare` refuses unlike scenes) |
| `colonist_injured_unexpectedly` Malnutrition on long chains | a bland map has no food | Watch calls `feed_colonists` each chunk (summary `fed`). Support colonists may be protected only in tests that are not about health, needs, damage or death |
| a leftover bite, corpse or dead colonist poisons the next job | residue of the previous hazard job | `reset()` reads back; `restore_colonists` retries by def |
| `colonist_died` FATAL for "Marina (husky) (bonded)" | the death letter of an animal was read as a colonist | a letter with a species in parentheses is ignored; `is_colonist` ≠ `isPlayer` |
| hostile insects on a "bland" map | the `factionlessAnimals` filter | `nonColonists` before the colonists spawn |
| result lost after a 30-minute suite | the runner crashed in `emit_verify` (the seat was not visible through python.exe) | `modcheck run --seat <SEAT>`. Check that the summaries are written before the ledger step |
| the test's own raid, break or incident aborts the test | it was not declared | `t.expect(...)` in that suite |
| rain fills an excavation, cold freezes a liquid, an autosave stalls | weather, season or prefs | pinned and read back at preflight (the interference table of the FlowWorks plan, `design/RimMandrake/flowworks_northstar_script_plan_2026-10-02.md` §2) |

When you meet a new interference:

1. Fix it in `bland_world.py`, `saved_base.py`, `runner.py` or `detectors.py`, with a selftest.
2. Add a row to this table.
3. File the test-environment item.

Two more traps:

- **`northstar_driver run --mod <Mod>` without `--plan <path to the mod's northstar_plan.py>` does an EMPTY run** with 0
  rows. No error names the missing plan. The last line reads NOT GREEN with zero counts (or REFUSED, when preflight
  fails). Always pass `--plan` (e.g.
  `--plan src/RimMandrake/Pyrelands/northstar_plan.py`). Treat a 0-row result as UNMEASURED.
- **The modcheck governor stops on `hostile_arrival` before the detector sweep.** The stop comes from the latch of
  `jawa/safe_advance`, as `clockgate.GovernorStop`. So a raid that fires records no `raid_arrived`, unless the sweep runs
  immediately after the raid. Run the sweep right after you trigger a raid. Two things let the clock resume: a fixture
  that the test declared, and `clockgate.expected_disturbance`.

## 6. The time ledger

`design/RimMandrake/northstar_time_ledger_2026-10-01.md` reconstructs pass 2 of 2026-10-01 (210 min). Its sources are
runner stamps, file mtimes, sidecar ticks, 950 bridge operation records and Player.log. The ledger teaches:

- **Cold launches are not the problem.** A launch took 36–38 s on the 32-mod minimal list. To relaunch for a clean
  one-map game is cheap. A dirty world is not cheap.
- **Lost or voided runs: 30%.** Runs that failed their own bland-world gate: 40%. The clean productive run took **16.4
  min for 13 suites**. Fix the harness before you run anything again.
- **Two suites are ~94% of the ticks**: Antiquities and FlowWorks. Antiquities has a fixed 95 000-tick worst-case wait;
  make it a wait-until. The other eleven suites finish in under 6 minutes together.
- **Median bridge call 48 ms** (about one frame). A full sweep is ~17–20 calls. So sweeps add 40–70% at full speed
  (estimated). To go faster, make idle sweeps cheaper, and use longer chunks on waits with no hazard.
- **Don't rerun the self-test jobs after every fix.** Batch the fixes, then relaunch once.
- The ledger had to be reconstructed, because no log holds the time of each chunk. Before you say that a pass is faster
  or slower, measure it (map count, focus, ticks/s per chunk). A cause that nobody measured stays UNMEASURED.

The ranked fix list of the ledger (§5 there) is a backlog, not a record of what was built. Grep the code before you
say that a fix is done.

## Keeping this skill honest

- `python3 skills/northstar-validation/scripts/check_paths.py` checks the paths that this skill cites. Exit 0 means that
  every repo path exists.
- This skill never holds a state as a fact. Examples of a state: which item is done, if the flip happened, if the saved
  base is wired. Read the ledger and the code.

## The scoreboard counts only what it can read

- `required_checks_report.py` counts the required checks that are proven, per mod. The report reads
  `Transient/modcheck/live_queue/*/<Mod>_summary.json`. The report also reads the live results of a `checkout:` script. The header of
  the mod's validation walk (`design/validation_walks/<tier>/<Mod>.md`) names that script.
- A mod with no readable record counts as unproven, even when its suite passes live. The report once read "proven 0 of
  1543" while FlowWorks ran 59/59.
- The report names the unreadable mods under NOT IN THE TOTAL. Never cite a proven-count without that line beside it.
- **A north star reads DRAFT when its recorded hash no longer matches disk, even for a trim that loosens nothing.** The
  hash covers the whole `## north star` section. So a trim of stale status prose also returns it to DRAFT. The example
  is in `references/history.md`.
- A reworded line counts as a loosening for the delegated route (`modcheck validate --delegated` refuses it). Such a line
  needs a re-validation on the owner's words, his card, or the Conductor's `--per-ruling`.
- To measure, use `northstar.validated_baseline` + `northstar.loosenings`.

## A new north-star bar stays DRAFT

A new north-star bar stays DRAFT until `modcheck/cli.py validate` records a validation. For `--owner-said` and `--by-card`, he must hear or
read the lines first. `validate` with no flag prints the lines and writes nothing. One of these routes records it:

- `--owner-said`: his words.
- `--by-card`: a decision that he took by card.
- `--per-ruling` with `--why`: the Conductor's act.
- `--delegated --judge-verdict <json>`: an agent's route, for new bars only. The tool refuses it when the section loosens
  its last validated version (`design/RimMandrake/delegation_policy.md` §1). The verdict file must be under
  `infrastructure/state/delegated/`, with the verdict PASS.

Then a component in the mod's `src/Rim*/<Mod>/validation.py` must claim each must-show line with `shows=`. A full run of
the suite refuses while a validated must-show line has no claim.
