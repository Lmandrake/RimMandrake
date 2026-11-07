---
name: northstar-validation
description: Run a mod's north-star suites live without the harness eating the sitting — the bland world (generated per game, or the saved BLAND_NORTHSTAR_BASE), the situational envelope (`modcheck run --situational`, watch.Watch, clockgate, surprise evidence, declared expectations), the live_queue jobs (run_next.py, preflight..bland_base, rollout_gate), the companion-reading detectors (pawn_census, damage_log, incident_queue_peek), the playbook for interference (naming dialogs, focus theft, late bridge replies, dirty worlds, extra maps, starvation, the test's own events), and the time ledger of where a live pass's minutes went. Use before any northstar or situational run, when a chain aborts on a surprise and you must decide whether it is the mod, the world or the test's own act, when a live pass is slow or keeps dying on harness defects, when choosing between reset, a saved world and a relaunch, and before flipping --situational to the default.
---

# North-star validation: make the world boring, then let the detectors speak

A north-star suite (`src/Rim*/<Mod>/validation.py`, run by `src/RimMandrake/Utils/modcheck/runner.py`)
proves a mod's `## north star` lines against the running game. Its enemy is rarely the mod. On the
2026-10-01 live pass, **8% of 210 minutes** was a clean full-suite run; the rest went to harness
defects, a dirty world and a collapsing tick rate (§6). The owner's answer, 2026-10-01:

> *"We need to establish testing worlds and make them as static and boring as possible. We're being
> eaten alive by random events, naming dialogs, the lot. Every time we encounter these things, let's
> upgrade the Northstar system and testing scripts so they handle anything, go faster, etc."*

So: **every interference you meet is fixed in the tooling, with a selftest, the first time** — never
clicked past for one run. And (owner, 2026-10-13, by card) **every threat that appears during a test is
logged and gets a test-environment item** whose job is to stop it next time.

Neighbours: writing or reading a proof's rows → `live-debugging-proof-harness`; starting a throwaway
map → `rimworld-debug-testing`; driving the bridge → `rimbridge`; deploying first → `rimworld-deploy`.
Design of record: `design/RimMandrake/northstar_helpers_plan.md` (§10 overrides §§3–6).

## 1. The bland saved world

A test world is featureless: flat, dry, temperate, no ruins, no wildlife, no strangers, no queued
incidents, a named colony, three colonists, one map. Two ways to get one; both live in
`src/RimMandrake/Utils/modcheck/`.

**Generated per game — `bland_world.py`** (the path the runner uses today):

| call | does | when |
|---|---|---|
| `setup(session)` | export tiles → Flat, `DRY_BIOMES`, 15–30 °C, no mutators/roads/rivers → `colony_found` (skips tiles already settled this game) → `world_tile_map_generate` → `set_current_map` → `destroy_bulk nonColonists` **before** colonists spawn → ruin `destroy_batch` (5 passes) → spawn colonists → name the colony | once per game |
| `reset(session, expected_ids)` | removes hostiles, wildlife, strangers, corpses, fires, queued incidents, injuries, hunger, a pending retile or pond — **then reads the world back** and returns residual problems | between suites (`runner.run_suite(bland_world=True)`) |
| `assert_world(session, ruins_too=False)` | verification only; `[]` means bland | after a suite |
| `feed_colonists(session)` | tops up only LOW Food | every Watch chunk |
| `retile(session, biome)` / `paint_pond` | a suite that needs its biome or open water gets it for its duration, restored after | `--retile` |

Traps it already encodes (do not rediscover them):
- **The quicktest world is re-rolled every launch.** Tile numbers are preferences (`HINT_TILE`), never
  facts; the campaign world has no vanilla AridShrubland/Desert tile, hence `ZBiome_Grasslands`.
- `destroy_bulk factionlessAnimals` misses **hostile-faction insects** a generated map can arrive with;
  use `nonColonists`, and before the colonists exist.
- `SteamGeyser` / `VHGE_GasGeyser` sit in the `BuildingArtificial` group but are natural and
  indestructible — `NATURAL_SCENERY`, not ruins. A quicktest map's own ruins are not hazard residue, so
  only `setup()` checks ruins.
- `colony_found` on an already-settled tile refuses: one game cannot re-run the same tile.

**Saved — `saved_base.py` + `live_queue/bland_base.py`** (the owner's target: *"name the colony once
and SAVE; load the save per suite"*). `bland_base` builds the world once, calls
`induce_and_finish_naming` (no naming dialog can ever re-raise), proves `assert_bland`, and `save_base`
writes `BLAND_NORTHSTAR_BASE` after backing up Saves and **proving a NEW file appeared and no other save
changed size** (`save_game` has written the wrong slot). `world_reset()` loads it; loading replaces the
game, so no stale map survives. ⚠️ Before relying on it, check: `world_reset` is not wired into
`runner.py` (grep it), and `bland_base` is write-once (refuses if the save exists). These saves are
disposable test saves, not canonical world saves (`infrastructure/state/CANONICAL_SAVE.md`).

## 2. The situational envelope

`modcheck run <Mod> --situational [--policy abort|record]` wraps every chain in a
`watch.Watch` (`src/RimMandrake/Utils/modcheck/watch.py`). All of it is enforced in Python; nothing
asks a model when to stop.

- **Time moves only through `clockgate.step`** (`clockgate.py`), charged from the MEASURED
  `ticksGame` delta, never the requested n; a request over `remaining()` raises `BudgetExceeded`
  **before** the clock moves. A long wait is chunked (`DEFAULT_CHUNK = 600`); a 95 000-tick wait that is
  not chunked is UNMEASURED by budget.
  `clockgate.step` and `B.ticks` both go through `clockgate.advance_chunk`, which prefers
  `jawa/safe_advance` (many ticks per frame). Do not add raw `step_game_ticks` or advance-read-repeat
  loops beside it. A north-star script is written to the Lightspeed contract (exit 0/1/2, deterministic
  rows, named UNMEASURED reasons): `skills/live-debugging-proof-harness/references/lightspeed-authoring.md`.
- **Every chunk: full snapshot + detector sweep** (`snapshot.py`, `detectors.sweep`).
- **The first SURPRISE/FATAL captures evidence before anything else** (`surprise.py`): verified pause
  (never a refresh tick — stepping mutates the evidence), sidecar JSON written atomically first, then one
  screenshot. Then policy: `abort` raises `SurpriseAbort` and the component is **UNMEASURED with the
  evidence named — never FAIL against the mod**. `record` is diagnostics only.
- **A chain whose world cannot be made bland records every component UNMEASURED.**
- **Visitor rule** (owner card 2026-10-10): visitors with no evidence of disrupting a colonist or
  subject are recorded, removed by id, and the run stays clean; evidence of disruption aborts.
- **Disturbance verdicts** (owner card 2026-10-13): *"if telemetry detected an anomaly that was corrected
  and there is no evidence of damage to the test, it can PASS still. If there's any sign of damage to the
  test itself … test is restarted."* Damage to the test is a restart, never a FAIL.
- The game is left verified-paused and settings restored on every exit path.

**Declare what the test causes itself**, or the envelope aborts on it
(`detectors.Expectations`): `t.expect(kind, matcher, until_tick=, phase=, max_count=)`, kinds
`hostile pawn letter condition fire litter mental incident raid`, plus `w.expect_fixture(pid)` for
anything the test spawned. Bound it (`max_count`, `phase`); never declare by mod package. The measured
false surprises this cures: Ninefold's induced break, Droidworks' wild droid going ManhunterPermanent,
Aftermath's own hostiles, Ninefold's birth-outcome death.

The flip to `--situational` by default is `NORTHSTAR_SITUATIONAL_ROLLOUT_1`; its gate is
`python3 src/RimMandrake/Utils/modcheck/live_queue/rollout_gate.py` (exit 0 = latest abort-only pass is
MEASURED PASS, on the current envelope, covering every on-disk suite). Read the item's state; never
cite the flip as done from memory.

## 3. live_queue: bridge work ready the moment you hold the bridge

`src/RimMandrake/Utils/modcheck/live_queue/`, doc `design/RimMandrake/northstar_live_queue_2026-10-01.md`.

```
python.exe src/RimMandrake/Utils/modcheck/live_queue/run_next.py --list | --all | --job <id> | --dry-run
```

- **`python.exe`, from the repo root** — the bridge binds Windows loopback. One Session per process,
  so `--all` runs each job in its own process. Exit 0 PASS · 1 FAIL · 2 UNMEASURED · 3 queue done.
- A job is **done once its latest live record is MEASURED** (PASS or FAIL — a measured FAIL is a finding
  to file, not a reason to rerun). UNMEASURED is offered again. Records append to
  `Transient/modcheck/live_queue_results.jsonl`; job state lives there, never in a doc.
- Jobs (`jobs.py` is the list): `preflight` (map Playing, every tool in the live census, recorder
  hooks, suite mods in parsed ModsConfig) · `situational_rerun` (every suite, `--situational
  --policy abort`, `--bland-world`, `--mods A,B` for a subset) · `abort_proof` (one hazard per case,
  each must abort on the RIGHT detector with sidecar and the game paused; controls must not) ·
  `bland_tile` · `companion_live` · `motion_frames` (captures, judges nothing) · `bland_base` (one-time).
- Setup: `rimflow bridge take`, quit the game, `python3 …/live_queue/prep_wsl.py --apply` (minimal swap,
  deploy every suite mod, compose their packageIds; no flags = plan only), launch through Steam. Every
  job is rehearsed offline on `rimdrive.fake.FakeWorld`; `selftest_live_queue.py` proves every criterion
  can FAIL.

## 4. Companion detectors

The detectors (`detectors.py`, pure functions over a snapshot; severities live only in `SEVERITY`)
read the JawaBench companion **directly** instead of inferring
(`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchSituationalTools.cs`):

| detector | reads | was |
|---|---|---|
| `mental_break` | `jawa/pawn_census` mentalState + isAggro | letters only (`list_pawns` has no mentalState) |
| `predator_hunting` | census isPredatorHunting + preyId on a player pawn | proximity standing in for intent |
| `colonist_damaged` | `jawa/damage_log` damageDef, instigator, weapon | hediff inference (now skips injuries a damage event explains) |
| `colonist_died` | corroborated by `damage_log` kill events | row / Death letter / story stats |
| `incident_queued` | `jawa/incident_queue_peek` — seen before it fires; a threat is SURPRISE, else WARN | nothing |

`Watch` probes the companion once at enter; absent, the detectors fall back to inference and the
summary says `companion: false` — never silence. Offline proof:
`selftest_companion_detectors.py` and `selftest_detectors.py`; live: the `companion_live` job, which
checks each detector's **evidence**, not just its name.

🔑 A direct read surfaces **new** surprises in suites that hurt or break their own colonists. Before
filing any `colonist_damaged`, `predator_hunting`, `mental_break` or `incident_queued` hit, ask whether
the chain caused it; if so the fix is a declared expectation in that suite (§2), not a detector change.

## 5. Interference playbook

Every row was measured live and is fixed in code; if one recurs, the fix regressed — find it, don't
work around it.

| symptom | cause | fix in the tooling |
|---|---|---|
| `modal_open` aborts every chain after a colony is founded | `Dialog_NamePlayerFactionAndSettlement` / `Dialog_NamePlayerSettlement` force-pause and re-raise every ~1000 ticks until named; closing never sticks | `jawa/name_colony` at setup (`bland_world.close_naming_dialogs`, `saved_base.induce_and_finish_naming`); `modal_open` ignores `Dialog_NamePlayer*` |
| a suite and every later one die on `unexpected response id` | a heavy step outlives the client timeout; its late reply lands on the same socket | `rimbridge_client.py` drops late replies of timed-out requests. ⚠️ Still: **no side-connection probes while a runner drives** — one driver means one connection |
| UNMEASURED "could not bring RimWorld forward" | owner's browser in front; `AttachThreadInput` refused | `game_focus.focus_game` Alt-tap + AppActivate fallback. Never fullscreen or steal focus beyond that |
| tick rate collapses 416 → 50 ticks/s | each `setup()` generated a new map and kept the old ones (also suspect: focus) | one map — load the saved base, or relaunch (36–38 s) between full runs; key any TPS comparison by map count (`src/RimMandrake/Utils/sim/csuite_tps.py --compare` refuses unlike scenes) |
| `colonist_injured_unexpectedly` Malnutrition on long chains | a food-less bland map | Watch `feed_colonists` each chunk (summary `fed`); support colonists may be protected only in tests not about health, needs, damage or death |
| leftover bite / corpse / dead colonist poisons the next job | previous hazard job's residue | `reset()` reads back; `restore_colonists` retries by def |
| `colonist_died` FATAL for "Marina (husky) (bonded)" | a death letter of an animal read as a colonist | species parenthetical ignored; `is_colonist` ≠ `isPlayer` |
| hostile insects on a "bland" map | `factionlessAnimals` filter | `nonColonists` before colonists spawn |
| result lost after a 30-minute suite | runner crashed in `emit_verify` (seat not visible through python.exe) | `modcheck run --seat <SEAT>`; check that summaries are written before the ledger step |
| the test's own raid / break / incident aborts it | undeclared | `t.expect(...)` in that suite |
| rain fills an excavation, cold freezes a liquid, an autosave stalls | weather / season / prefs | pinned and read back at preflight (FlowWorks plan's interference table, `design/RimMandrake/flowworks_northstar_script_plan_2026-10-02.md` §2) |

New interference: fix it in `bland_world.py` / `saved_base.py` / `runner.py` / `detectors.py` with a
selftest, add a row here, and file the test-environment item.
- **`northstar_driver run --mod <Mod>` without `--plan <path to the mod's northstar_plan.py>` does an EMPTY run** with 0 rows and no error (e.g. `--plan src/RimMandrake/Pyrelands/northstar_plan.py`). Always pass `--plan`, and treat a 0-row result as UNMEASURED.
- **The modcheck governor stops on `hostile_arrival` before the detector sweep.** A raid that fires records no `raid_arrived` unless the sweep runs immediately after the raid, so run the sweep right after triggering one.

## 6. The time ledger

`design/RimMandrake/northstar_time_ledger_2026-10-01.md` reconstructed pass 2 (210 min) from runner
stamps, file mtimes, sidecar ticks, 950 bridge operation records and Player.log. What it teaches:

- **Cold launches are not the problem**: 36–38 s on the 32-mod minimal list. Relaunching for a clean
  one-map game is cheap; a dirty world is not.
- **Lost or voided runs: 30%**; runs that failed their own bland-world gate: 40%; clean productive
  run: **16.4 min for 13 suites**. Fix the harness before rerunning anything.
- **Two suites are ~94% of the ticks**: Antiquities (a fixed 95 000-tick worst-case wait — make it a
  wait-until) and FlowWorks. The other eleven finish in under 6 minutes together.
- **Median bridge call 48 ms** (about one frame); a full sweep is ~17–20 calls, so sweeps add 40–70% at
  full speed. Cheaper idle sweeps and longer chunks on hazard-free waits are the lever.
- **Don't rerun the self-test jobs after every fix**: batch fixes, relaunch once.
- The ledger was archaeology because per-chunk timing is not logged. Before claiming a pass is faster
  or slower, measure it (map count, focus, ticks/s per chunk) — an unmeasured cause stays UNMEASURED.

Its ranked fix list (§5 there) is a backlog, not a record of what was built: grep the code before
citing any fix as done.

## Keeping this skill honest

Paths cited here are checked by `python3 skills/northstar-validation/scripts/check_paths.py` (exit 0 =
every repo path exists). States (which item is done, whether the flip happened, whether the saved base
is wired) are never written here as facts: read the ledger and the code.

## The scoreboard counts only what it can read
`required_checks_report.py` reads only `Transient/modcheck/live_queue/*_summary.json`, so a mod with no readable record counts as unproven even when its suite passes live (it once read "proven 0 of 1543" while FlowWorks ran 59/59). The report names the unreadable mods under NOT IN THE TOTAL: never cite a proven-count without that line beside it.

## A new north-star bar stays DRAFT
A new north-star bar added on the owner's word stays DRAFT: `modcheck/cli.py validate` needs him to hear the lines, then `--owner-said` or `--by-card`; the loop then needs `shows=` claims in `validation.py`.
