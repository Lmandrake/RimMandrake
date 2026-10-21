# Bridge debugging, observability, testing and process

Status: DRAFT for GPT deep review — 2026-10-10, FOUNDRY (offline pass; no bridge taken, no game touched). Complete: sections 0–7.
Companion doc: `design/RimMandrake/bridge_system.md` (architecture and control, written by a sibling pass). This doc
is the **debugging, observability, testing and process** half. Owner order, 2026-10-10: *"document the ENTIRE
bridge system and intention... all of it. Debugging, control, everything."* Aim: **predict problems now instead of
slowly iterating on debugging live.**

## 0. Scope and evidence labels

- **MEASURED** = read from code, a file on disk, or a command run during this pass; the source is cited.
- **UNVERIFIED** = asserted by a doc, lesson or memory note and not re-checked here; treat as a lead.
- **DOC-ROT** = two sources disagree; both are cited and the code (where there is code) wins.
- Paths are repo-relative to `/home/mandrake/rm/foundry` (the read-only Windows mirror is
  `D:\Luke\dev\RimMandrake`). Live record directories are on Windows:
  `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\` (`Player.log`, `JawaBench\tps\`,
  `JawaBench\health\`), `D:\ClaudeWork\rimmandrake\obs\runs\` (per-call telemetry), `D:\ClaudeWork\rimmandrake\scratch\bridge_sessions.jsonl`
  (session log).

The one-paragraph intention: **a cold load costs ~15–25 minutes, so everything that can be known offline must be
known offline; everything learned live must leave a rerunnable check behind; and no instrument may report
"clean" when it actually means "could not ask".** Nearly every tool below is a scar from a specific incident in
§4.

---

## 1. Debugging philosophy and process

### 1.1 The rules (MEASURED: `design/RimMandrake/debug_process.md`, OFFICIAL, owner rulings 2026-10-01)

1. **Every mod has a functional script** (`src/<tier>/<Mod>/validation.py`, a modcheck `Suite`), and bugs are
   debugged by rerunning it and watching it get further. Script and code evolve together.
2. **Source first.** A live run must be proven needed (memory note `live-check-must-be-proven-needed.md`).
3. A live **behaviour** bug starts with the mod's script.
4. If the script cannot see the bug, **poke live as long as it takes, then write what was learned into the
   script**: a check that goes **red for the reported reason** before the final fix, plus guards for informative
   false theories (`## anti-guessing notes`: `RULED OUT: <theory> — <check that killed it>`). Nothing that found a
   bug may live only in `Transient/` or a conversation. (Evidence it matters: the 2026-10-01 `ns_probe_*` scratch
   files vanished and survived only in commit messages — `debug_process.md` §3 rung 3.)
5. **Stuck → GPT early** (trigger: 20 min without hypothesis-separating evidence, OR two refuted theories, OR a
   result that contradicts the model of the system). GPT's answer is a **hypothesis, never a verdict**.

### 1.2 The debugging ladder (MEASURED: `debug_process.md` §3)

| rung | action | instrument |
|---|---|---|
| 0 classify | LOAD / STATIC / BEHAVIOUR / VISUAL / HARNESS | LOAD → Player.log **first** exception; STATIC → source, def dump, `validate_patch.py`, RimSage; BEHAVIOUR → the mod's script; VISUAL → screenshot + judge/owner; HARNESS → driver selftest + `lint_calls.py` |
| 1 source | write down what source cannot tell you | RimSage (Desktop only), decompiled engine, our C#/XML |
| 2 run script | red on symptom → repro; **prior-pass-now-fail → STOP** (the regression is the finding); green while symptom real → script is blind | `modcheck`, `northstar_driver`, live_queue |
| 3 poke | no clock; ends when the cause is known and a red check exists | `python.exe` + bridge lease |
| 4 fix | MOD / SITE / HARNESS; a new assembly always goes alone | winbuild, deploy |
| 5 rerun | until green; read the whole result; never weaken a predicate to pass | |
| 6 commit | commit names class + check id | |
| 7–8 | GPT; two GPT rounds without new evidence → owner | `gpt_consult.py` / codex.exe |

Observed (MEASURED, `debug_process.md` §8, 2026-10-01): **most early findings were HARNESS, not MOD** — of one
day's findings, 5 were harness (`draft=` vs `drafted=`; a ~10 s `step_game_ticks` give-up; a no-op `waitTicks` on a
paused site; a 10/10 state PASS hiding 76/79 unjudgeable frames; 22 call sites with undeclared params) and 1 was a
mod defect (`RUT_Barbslinger`'s duplicate turret comps).

### 1.3 First-look protocol (MEASURED: `skills/rimbridge/references/first_look.md`, 2026-10-10)

Seven steps before any theory: (1) identity/timing + take the lease; (2) **capture the scene before touching
anything** (`modcheck/scene_report.py`); (3) resolve the subject by id and read back the ACTUAL kind (E5: 4 of 80
spawns came back a vanilla Colonist); (4) receipts — `ourInvolvement` and `expectation` are independent;
(5) facts and uncertainty separately — "origin unknown" where nothing recorded it; (6) validity
(CLEAN/DISRUPTED/INDETERMINATE); (7) only then a hypothesis. A **forbidden-upgrade table** bans e.g. "raid-style
lord → created by a storyteller raid" or "no event rows → no arrivals occurred" (enforced in code by
`JawaBenchAwarenessCore.IsForbidden()` — UNVERIFIED live, built not deployed).

### 1.4 Evidence discipline (cross-cutting)

- **"Could not ask" is UNMEASURED, never PASS and never FAIL.** Implemented in `northstar_driver/preflight.py`
  (`Check` → PASS/FAIL/UNMEASURED), `modcheck/launch_gate.py` (no readable log → exit 2, ok False),
  `required_checks_report.py` ("Unknown is never clean"), `health_observer.py` (unavailable is never 0). MEASURED in
  each module docstring.
- **Read the tool's own `success`/`foundCount`/`notFound`, never substring a payload** (CLAUDE.md: a
  `jawa/get_defs` list-arg call failed and a substring check read it as ABSENT for 22 biomes).
- **A search that finds nothing must first prove it can find something** (sanity probe; CLAUDE.md zsh word-split
  incident 2026-09-23; `launch_gate` requires `Bridge token:` as its probe).
- **A number about a large artifact comes from `measure`, never a scan** (`.claude/hooks/block_blind_scan.py`
  refuses; skill `measuring-large-artifacts`).
- **Bridge success ≠ effect.** `skills/rimbridge/references/silent-failures.md` holds four tables (≈30 rows,
  MEASURED by `grep -c '^|'` = 30 incl. headers): calls that silently don't redraw, calls that refuse silently,
  calls that report success falsely (`rimworld/save_game` wrote the CURRENT slot), and getters that lie
  (`SkillRecord.Level` adds aptitudes).
- **A screenshot is a cache, not an observation** (`skills/rimworld-debug-testing/SKILL.md` §4a; a paused
  screenshot can be the previous frame — `traps.md`).
- **Name which map a result came from** (`rimworld-debug-testing` §3) — quicktest vs campaign vs bland base.

### 1.5 Who owns what (MEASURED: `design/RimMandrake/rimflow_validation_levels_addendum_2026-10-07.md`, `src/RimMandrake/rimflow/model.py:215`)

- Functional scripts: **written and approved by agents**; green → the mod passes, no owner step
  (`debug_process.md` §6).
- Owner's hash-bound `## north star` bars: **only his** `modcheck validate --owner-said` binds them; correcting
  prose in that section reverts it to DRAFT and must be re-validated the same sitting (CLAUDE.md).
- **FOUNDRY owns acceptance L0 → GREEN-FULL and L3; BENCH owns only L4** (owner 2026-10-06, typed: *"Foundry is
  supposed to own automated processes. Bench is about human interaction, design work, and emergency response."*;
  `rimflow/priority.py:291` `ACCEPTANCE_SEAT = {"L4": "BENCH"}`).
- **Whoever proves it closes it**; the evidence is a red→green pair and a commit.
- One bridge driver at a time; the lease is `infrastructure/state/BRIDGE` via `rimflow bridge take/release`; a hold
  idle 45 min is stale and may be taken; holding it is blanket authorization to launch/kill the game.

### 1.6 The load-round doctrine (MEASURED: `skills/rimworld-load-round/SKILL.md`, `infrastructure/GAME_STATE_WORKFLOW.md`)

- Never "restart and see"; **write the Player.log decision strings before launching**; batch by ambiguity.
- Prefer the minimal list (13–14 mods, ~22 s) via `modlist_swap.py`/`modset_builder.py`; every tier includes all
  five DLCs (owner 2026-09-19) and the camera-zoom mod `ray1203.simplecamerasetting` (owner 2026-10-04,
  `modset_builder.resolve_tier`).
- Launch via Steam, never the bare exe (memory `launch-rimworld-via-steam-not-bare-exe.md`: intermittent Harmony
  breakage).
- DLLs deploy only while the game is DOWN; the state machine is DOWN → DEPLOYING → LOADING → UP → GOING_DOWN, and a
  reboot is the agent's own call.
- **DOC-ROT, full-list cold-load time:** `GAME_STATE_WORKFLOW.md` says **~25 min / 578 mods**; CLAUDE.md says
  **~15 min MEASURED 2026-09-07 on 599 mods**; the observatory baseline observed **18.5–21 min** for five loads on
  2026-10-03 (`bridge_validation_observatory.md` §1.2). `belt_watchdog.LOAD_BUDGET_S = 25*60`. None of these is
  a current measurement; the observer's `bridge.token` milestone (`health_observer.py`) can now measure it.

---

## 2. The observability stack, layer by layer

Maturity scale: **built** (code exists, selftests offline) → **deployed** (in the game folder / scheduled) →
**live-proven** (seen working on a real game with a cited record) → **owed** (designed, not built).

### 2.1 Player.log (engine)

- **Answers:** load errors (first exception), `Could not find type named …`, ConfigErrors, patch failures that do
  log, NRE storms, our `[JawaBench]` init lines and TPS markers (`[JawaBench] TPS marker` joins the log to the TPS
  record — `tps_record.md`).
- **Blind:** no incident firing, no pawn arrival (MEASURED over three logs, `map_awareness.md`); a patch that
  matches nothing logs nothing (`PatchOperationConditional`/`FindMod` return true); **after 10,000 messages Verse.Log
  stops emitting** (`StopLoggingAtMessageCount = 10000`, RimSage 2026-10-10, `game_health_record.md` rule 7 — the
  older "1,000" figure was DOC-ROT and corrected); rotated to `Player-prev.log` at every launch, so the previous
  session's log is lost on a second relaunch unless archived.
- **Traps:** a stale log from the previous process matches readiness greps (`bridgetools/launch_and_wait.sh` waits
  for truncation first); the loudest exception is usually a cascade (CLAUDE.md, 2026-09-27: `WorldPathGrid` spam
  after one `BiomeWorker.GetScore` NRE).
- **Archive:** `JawaBench\tps\logs\` — Player-prev copied by every `belt_watchdog`/`tps_observer` pass and at
  companion start, deduped by sha; Player.log copied at clean shutdown. MEASURED: 15 entries in `tps\logs` today.
- **Maturity:** engine-native; archive **deployed + live** (files exist).

### 2.2 Launch gate (`src/RimMandrake/Utils/modcheck/launch_gate.py`)

- Refuses to start a map when Player.log holds `Could not find type named (RimMandrake|RimStarWars|RimUtinni)…`;
  requires `Bridge token:` as sanity probe. Born of 2026-10-01: a stale-checkout deploy shipped old DLLs → ~64
  type errors → `Error while generating map`. **Built, live** (it refused 3 jobs on 2026-10-03 —
  observatory §1.2).
- **Blind:** type errors from *other* namespaces, XML ConfigErrors, cross-reference failures, missing textures.

### 2.3 TPS record (in-game companion, `JawaBenchTps*.cs`; reader `tps_record.py`; doc `tps_record.md`)

- **Answers:** "was it slow at 3 pm yesterday, and why" — per-window `ratio` (dTicks/expected, frame-integrated at
  effective multiplier over unpaused time), stalls (`incident` rows for gaps > 2 s with `quietPhase` = where the
  main thread was blocked), long events/saves, per-map `context` every 60 s, coarse stage attribution
  (`tl:Normal|Rare|Long`, world, mapPre/Post, mapComp, gameComp), GC count, heap, focus.
- **Starts** at RimBridgeServer companion registration (main menu, no bridge call) because `JawaBenchTpsTools` is an
  instance tool with a public parameterless constructor (decompiled chain cited in `tps_record.md`). ⛔ Making that
  tool static silently reverts to "starts on first `jawa/` call".
- **Watchdog thread** writes `hb_<session>.json` every 5 s with `mainBeatUtc` vs `watchdogUtc`; `silence` rows when
  the main thread is quiet > 10 s.
- **Blind:** anything before companion registration (**the whole cold load until play data loads** — `spike.early-load`
  owed); per-mod/per-method cost (ruled SKIP from always-on); presentation FPS (unsupported); the cause of a stall
  ("why" is a lead); data still queued when the process is killed (C3 unmeasured).
- **Cost:** `profEstMs` is an incomplete estimator, not a bound; real overhead is owed (C4, MUST 17,
  `RECORDER_OVERHEAD_MEASURE_SIX_CONFIGS_DEEP`). Disk: ~1–2 KB per window line, "tens of MB per day"; retention 7 d /
  256 MB. MEASURED today: `tps\` = 4.9 MB, 28 entries.
- **Maturity:** built + deployed + partly live (session rows and `exited-without-shutdown` findings exist on disk);
  acceptance C3/C4 **not passed**; Harmony safety gate **FAIL until `TPS_HOOKS_HARDEN_REENTRY_AND_LATE_GUARDS`**
  (`game_health_record.md` contracts table).

### 2.4 External observers

| piece | answers | cadence / maturity |
|---|---|---|
| `tps_observer.py` (Windows scheduled task `RimMandrake\TPS Observer`, `pythonw.exe` on the mirror) | did a game exit without shutdown; is a main thread silent; heartbeat stale while process alive; preserves Player-prev.log | every 2 min. **Deployed + live**: MEASURED `schtasks /Query` → `Ready`, next run 12:26 PM; `observer_last.json` written 19:24Z today with two `exited-without-shutdown` findings |
| `health_observer.py` (`GAME_OBSERVER_BUILD_OUTSIDE_LOOKING_IN`) | game identity (pid + creation time, held handle → real exit code), process CPU, assumed-main-thread CPU, memory, system memory, Player.log growth/rotation/truncation, startup milestones (`engine.init`, `bridge.token`, `log.cap-reached`…) | 5 s with game / 30 s without. **Built; NOT installed as a standing task on purpose** (would contaminate C1 of the overhead protocol). Self-cost MEASURED 0.30 % of a core. One live exit observed (exit code 1, 17:28:13Z) |
| `health_forensics.py` | offline: DeepProfiler load tree (needs `Prefs.LogVerbose`), streaming save census | built; load-tree UNMEASURED on real data (0 of 18 archived logs hold a tree) |
| `bridgetools/crash_watch.sh` | 2026-09-05 passive RSS + Event Viewer crash capture | built, ad hoc, superseded in practice by the observers |

### 2.5 belt_watchdog and run supervision (`belt_watchdog.py`, `belt_heartbeat.py`, `focus_heal.py`, `game_focus.py`)

- **belt_watchdog** — one line per signal, verdict HEALTHY/STALLED/WEDGED/DEAD = exit 0/1/2/3 (MEASURED module
  docstring). Signals: `game` (process, CPU, Not Responding ≥ 240 s), `player_log` (age, loop detector = same
  normalised error ≥ 20× in the tail and still at its end, `KNOWN_LOOPS`, 10,000-cap warning), `bridge`
  (python.exe probe: ping, programState, a **main-thread** call `rimworld/get_ui_state`), `foreground`,
  `modals` (`BAD_MODALS` regex; WEDGED after > 2 heartbeats), `runner`, `heartbeat`, `run_output`, `belt_logs`
  (subagent silence 20 min), `modcheck`, `tps`, `tps-observer`. Constants MEASURED: `LOG_FROZEN_S=300`,
  `LOOP_MIN_REPEATS=20`, `NOT_RESPONDING_WEDGE_S=240`, `LOAD_BUDGET_S=1500`, `MODAL_WEDGE_BEATS=2`. Doctrine: run it
  every ~5 min of any live run (`infrastructure/agents/FOUNDRY.md` § Hangs).
- **belt_heartbeat** — runner writes `.belt_state/heartbeat_<job>.json` every ≤ 30 s from a daemon thread;
  per-step budget (`BELT_SUITE_BUDGET_S`, default 1500 s) and job budget; on overrun records UNMEASURED(BUDGET) and
  `os._exit` (exit 4) because a Windows socket read cannot be interrupted otherwise.
- **focus** — RimWorld does not render unfocused (MEASURED in `game_focus.py` docstring: 0.5 % of a core in
  background); `ping` still answers in 0.5 ms while main-thread calls time out at 30 s. **The real fix is the
  `runInBackground` preference**; `focus_heal.py` escalates (minimise blocker → minimise/restore game) and raises
  `FocusLost` → exit 3. Memory note `dont-fullscreen-or-focus-the-game.md` (owner: never steal focus for
  screenshots) is in tension with this — see §6.
- **Runbook:** `design/RimMandrake/live_test_hang_runbook.md`, 8 symptom→cause→remedy rows.
- **Maturity:** built + used live since 2026-10-03; selftests `selftest_belt_watchdog.py`.

### 2.6 Bridge-call telemetry (observatory S2)

| piece | what | MEASURED state |
|---|---|---|
| `rimbridge_client.py` evidence log (`bridge_calls.jsonl`) | `start`/`end` per call; `end` carries `outcome`, `timeout`, `transport` | **RETIRED 2026-10-21 (design 08 P5):** `rimdrive/obs_events.py` is a no-op shim; its fields moved into the evidence log, read by `telemetry bridge`. Old run files in `D:\ClaudeWork\rimmandrake\obs\runs` stay readable |
| `modcheck/obs_summary.py` | calls/min by tool and outcome, p50/p95, UNFINISHED calls, timeline setup/ticks/tool/idle | built, offline |
| `rimbridge_client.py` session log `bridge_sessions.jsonl` | one row per client session (script, calls, seconds) | live: 1,259 rows; 151 today |
| `northstar_driver/bridge_utilization.py` | ACTIVE ∩ HELD / HELD | built |
| `JawaBenchArgGuard.cs` | server-side record of argument keys matching no declared parameter | live |
| `northstar_driver/lint_calls.py` + `tool_schemas.json` | offline static lint of call sites vs schemas | built; **snapshot dated 2026-10-03 (`a6bbcbb29`) — 26 declared companion tools are missing from it**, incl. `jawa/thing_explain`, `jawa/pawn_origin`, `jawa/awareness`, `jawa/incident_journal`, `jawa/kill_hostiles`, `jawa/playtest_*` (MEASURED: regex over `bridgetools/JawaBench.BridgeTools/*.cs`, 398 declared vs 496 in snapshot) |

**Finding (MEASURED):** since 2026-10-07 the bridge session log's top clients are ad-hoc scripts — `rimbridge_client.py`
direct 294, `_kb_call_tmp.py` 133, `cli.py` 79, `run_live_suite.py` 74, `l2sweep_run.py` 37, `l2p3_reset.py` 36 — and
the per-call telemetry and `live_queue_results.jsonl` (last row 2026-10-06T06:04) have recorded **nothing** since.
Most live work of the last four days is invisible to the observatory.

### 2.7 Map awareness (`map_awareness.md`; companion `JawaBenchAwareness*.cs`; Python `modcheck/detectors.py`, `contract.py`, `watch.py`, `scene_report.py`)

- **Answers:** who is on the map and what we actually know about why: `jawa/incident_journal` (incidents CALLED,
  any route through `IncidentWorker.TryExecute`), `jawa/pawn_origin` (generation/spawn under which operation
  chain), `jawa/thing_explain` ("what is that": def owners, texture providers OBSERVED vs CANDIDATE),
  `jawa/wild_spawner_block` (quiet world), disk rows only while ARMED (TTL 30 min, max 240).
- **Laws:** origin unknown unless observed; context chains carried explicitly (thread-static token + parms);
  hooks never throw; game-scoped epochs (provenance does not survive save/load); installed at bridge registration.
- **Maturity:** phases 1–3 **built, NOT deployed** (MEASURED: repo companion DLL sha `54ed9331…` built 11:27 today
  ≠ game copy `87b7370b…` deployed 09:50; commits `7eb8d02ca`, `8d5f64275`). Live acceptance =
  `MAP_AWARENESS_PROVE_ON_A_QUIET_MAP`. Phase-1 Python (detectors, CLEAN/DISRUPTED/INDETERMINATE, scene report)
  is offline-selftested (`selftest_awareness.py`).
- ⚠️ MEASURED: the companion artifact folder holds **no `.srchash`** beside `JawaBench.BridgeTools.dll`, unlike mod
  DLLs (CLAUDE.md `DLL_SOURCE_STAMP_GUARD_1`) — so "deployed companion == source" cannot be proven by stamp.

### 2.8 Scene report and screenshots

- `scene_report.py`: ~10 batched bridge reads, **not atomic** (states its start/end tick); decomposed hostility
  (faction relation, mental state, target, capability — `list_pawns.hostile` misses factionless manhunters);
  declared coverage gaps (held pawns, dormant, letter look-targets "unavailable" until companion deploy).
- Screenshots: `rimworld/take_screenshot`, `screenshot_cell_rect`; `system_screenshot.py` (OS-level, always
  allowed). Traps (MEASURED in `skills/rimbridge/references/traps.md`): files named by the second (bursts
  collapse); paused shot can be the previous frame; a modal freezes and corrupts the frame; zoom below the engine
  floor renders flat red; a stale mesh cannot be photographed. `surprise.py` verifies a PNG is real and stable and
  hash-compares with the previous shot.
- **Owner rulings that bound it:** never live-hunt flyer flight on camera (said 3×); visuals reviewed in game, not
  browser sheets (2026-10-05); screenshot and read your own graphics before human review.

### 2.9 Coverage matrix — symptom × instrument × time-to-diagnosis

Time-to-diagnosis (TTD) "today" is an estimate from the incidents in §4 and the 2026-10-03 recovery intervals
(observatory §1.2: 24–31 min per hang class); labelled UNVERIFIED unless a record is cited.

| symptom | catches it now | blind spot | TTD today |
|---|---|---|---|
| main-thread hang (exception loop) | belt_watchdog `player_log` loop + `game` Not Responding; TPS `silence` rows + hb `mainBeatUtc` frozen; tps_observer `silent` | first 25 min of a cold load (watchdog suppresses NR); a hang with no log output | 5–25 min (runbook rows 2/8; 2026-10-03 quest-loop 24 min) |
| per-frame exception storm (RealFoW) | `player_log` loop; `step_game_ticks` failing | the 10,000-message cap silences it afterwards (`log.cap-reached` milestone only in the uninstalled health_observer) | ~27 min (2026-10-03) |
| slow TPS | TPS record `ratio`, `SUSTAINED LOW`, attribution `top` | which mod/method (ruled out of always-on); frame-bound vs sim-bound only a hypothesis | minutes if recorder covered the time; ∞ if NO COVERAGE |
| crash / process death | tps_observer `exited-without-shutdown`; health_observer exit code; Player.log archive | native crash cause (no minidump: `spike.minidump` owed) | minutes to name, cause often never |
| cold-load stall | belt_watchdog `LOAD_BUDGET_S` (25 min); Player.log tail; health_observer milestones (not installed) | everything before companion registration; which mod is loading | 25+ min by construction |
| load failure / mod list reset to Core | Player.log first exception; `launch_gate`; parse `ModsConfig.xml` | patch that matched nothing; `MayRequire` on `<Operation>` ignored (CLAUDE.md 2026-09-27) | one cold load each (hit twice in one night) |
| stale DLL / stale deploy | `launch_gate` (our namespaces only); `run_identity.py` fingerprints start+end; `.srchash`; `deploy_custom_mods.py` plan | textures compared by size only; companion has no `.srchash`; ad-hoc scripts record no fingerprint | 30 min (2026-10-03 08:36→09:06) |
| modal block | belt_watchdog `modals`; runner closes `Dialog_ModSettings`/naming at job start/end; `saved_base.induce_and_finish_naming` | modals not in `BAD_MODALS`; taint on results already written (manual amendment) | minutes, but taint discovered after the fact (rerun3/5) |
| focus loss | belt_watchdog `foreground`; `focus_heal` → exit 3; TPS `focused` field | `runInBackground` pref state is not asserted by any preflight (UNVERIFIED) | <1 min now; 5+ min before (rerun13) |
| zombie game state (`game_loaded` true, no usable map) | preflight `Playing` map check; `prove_quicktest_world.py` | a load that aborted after "loaded" (memory `rimworld-zombie-game-state.md`) | UNVERIFIED |
| NRE storm from our content | Player.log; TPS `error`; launch_gate (type errors only) | NRE in a tick → log cap; NRE inside `Game` constructor → no game | one load |
| save failure / wrong slot | `saved_base.save_base` backs up and proves NEW file; TPS `save` rows with `threw` | `rimworld/save_game` reports success on wrong slot (silent-failures) | caught if the wrapper is used; silent otherwise |
| wrong creature / wrong kind | spawn receipts `readBackKinds`; first-look step 3; `thing_explain` (not deployed) | kind substitution by spawn tool (memory `census-requested-vs-actual-kind.md`) | per-call if receipts read |
| missing art (magenta / invisible) | screenshot + human/agent eye; `art_fold_check.py`; memory `prove-art-missing-before-generating.md` | texPath binds, not defName (`texture-binds-by-texpath-not-defname.md`); byte-identical deploy can render nothing | minutes–hours |
| unexpected visitors / raids during a run | `detectors.py` + `contract.py` → CLEAN/DISRUPTED/INDETERMINATE; `incident_journal` (not deployed) | origin before deploy; held pawns | per chunk sweep |
| silent-success bridge call | read-back discipline; `silent-failures.md`; `PASS(UNVERIFIED n)` taint | any tool not in the table | per call if read back; else forever |
| harness bug (wrong param) | `lint_calls.py`; `JawaBenchArgGuard` | 26 tools missing from the schema snapshot (MEASURED) | minutes |
| subagent died silently | belt_watchdog `belt_logs` (20 min) | agents not writing belt logs | 10–20 min |
| WSL → bridge unreachable | traps doc; all bridge calls under `python.exe` | none (by design) | seconds once known |
| disk / record growth | retention caps in writer; `observer_last.json` age | bytes/day UNMEASURED | — |

---

## 3. Test harness and acceptance machinery

### 3.1 Worlds and maps

| world | how | proves / cannot prove | maturity |
|---|---|---|---|
| **quicktest** (`rimworld/start_debug_game_ready`) | ~90 s map; `bridgetools/prove_quicktest_world.py` proves `Playing` with a world | defs resolve, spawn/tick behaviour; NOT campaign world, NOT save migration | live-proven on the full 629-mod list 2026-09-27 (CLAUDE.md) after three content bugs were fixed; memory note `quicktest-crashes-full-modlist-use-cheap-mechanism-list.md` records the earlier crash era |
| **bland world** (`modcheck/bland_world.py`) | flat dry 15–30 °C tile, no mutators/roads/rivers; colony_found → generate → destroy wildlife and ruins → spawn colonists → close naming; `reset()` reads back and returns residual problems | a featureless stage where any intruder is a surprise | built, live since 2026-10-01 (`NORTHSTAR_BLAND_TILE_1`); campaign world had **0** vanilla arid candidates (2026-10-03 note in module) |
| **saved bland base** (`modcheck/saved_base.py`) | build once, name the colony (naming dialogs re-raise every 1000 ticks until named: `Faction.FactionTick`, `TicksGame % 1000 == 200`), save `BLAND_NORTHSTAR_BASE`, `world_reset()` = load it | removes dirty-world drift between suites | built; save step proves a NEW file appeared and no keeper changed size |
| **quiet world** (`helpers.quiet_world`, `jawa/wild_spawner_block`) | read-back profile: incidents off, wild spawner blocked | event control | Python built; companion half not deployed |
| **static boring test worlds** (memory `static-boring-test-worlds-upgrade-northstar-on-every-interference.md`) | one saved, pre-named bland world per suite; every interference is fixed in tooling | | principle; partially realised by saved_base |
| **review maps / keeper saves** | owner-facing (`northstar_human_review.md`) | L4 only | per review |

### 3.2 Mod lists

- `modset_builder.py` tiers (bridge/pits/graffiti/oracle/…; `dlc: True` everywhere since 2026-09-19; camera-zoom
  forced), `modlist_swap.py --minimal/--restore` (FULL = `infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml`).
- `modset_builder.py --apply` refuses while Player.log was touched in the last 3 min (kill first, then swap).
- 🔴 `modcheck run <Mod>` **rewrites the live `ModsConfig.xml`** (swaps to MINIMAL; FULL restore is in a `finally`).
  Its swap path was fixed after a crash but **not re-exercised live** (MEASURED, `modcheck/runner.py` docstring).
- `modcheck record` is the sanctioned way to record a run on a tier the seat set up, refusing unless `mod_hash` ==
  now and `env.running` (read live via `jawa/running_mods`) equals the tier's resolved set.

### 3.3 Runners and drivers

| runner | role | record |
|---|---|---|
| `modcheck/live_queue/run_next.py` (+ `jobs.py`, `common.py`) | one job per process (rimdrive allows one Session per process); exit 0/1/2/3 | `Transient/modcheck/live_queue_results.jsonl` (MEASURED 89 rows: 71 MEASURED, 18 UNMEASURED; last 2026-10-06) |
| `live_queue/situational_rerun.py` | every registered suite, one session, `--situational --policy abort`; FAILs if a suite raised, FlowWorks refused, a BudgetExceeded, a chain without a bland map, or a surprise without evidence on disk | `<Mod>_summary.json` |
| `live_queue/preflight.py` | Playing map, required tools in live census, companion answers + damage recorder installed, suite mods in live `activeMods` (parsed) | job row |
| `northstar_driver` (`cli.py`, `preflight.py`, `bars.py`, `judge_cli.py`) | owner bars; preflight refuses on any non-PASS required check; fixes (pause/god mode) only with read-back | `Transient/northstar/*.json` (MEASURED 7 files) |
| `modcheck/runner.py` (`modcheck run`) | swap → quicktest → suites → restore | `modcheck_status.json` |
| `src/RimMandrake/Utils/scenes/` (`l1_*`, `l2_*` 2026-10-10) and ad-hoc `Transient/*.py` | the actual bulk of recent live work | **no standard record** (see §2.6 finding) |
| `bridgetools/prove_*.py` (≈30) | per-feature live proofs | stdout |
| `bridgetools/load_session.py` | a whole live session scripted before boot; visual checks end in `NEEDS EYES` | stdout + screenshots |

### 3.4 Watch, clock and evidence (`modcheck/watch.py`, `clockgate.py`, `surprise.py`)

- Game time moves **only** through `clockgate.step`, charged from MEASURED `ticksGame` deltas; one `last_seen_tick`;
  a negative delta opens a new epoch (never charged negative); one hard `session_cap` over component and overhead
  ledgers.
- Every chunk → full snapshot + detector sweep; the first SURPRISE/FATAL captures evidence **before action**
  (verified pause, atomic sidecar JSON, one screenshot, PNG verified) then policy: `abort` (UNMEASURED with
  evidence) or `record`.
- **Owner visitor rule (card, 2026-10-10):** a visitor with no evidence of disruption is recorded and removed and the
  run stays **CLEAN** with a note; evidence it attacked/targeted/hunted a protected pawn → **DISRUPTED** (redo);
  a failed observation → **INDETERMINATE**. Visible evidence: damage_log instigator→victim, pawn_census
  enemyTarget/meleeThreat/prey/job targetA. **Not visible:** food/bed competition, path blocking, scaring, psychic
  effects (MEASURED, `contract.py` docstring).
- The game is left verified-paused on every exit path; debug/difficulty settings restored.
- `abort_proof.py`: deliberate hazards must trip their detector with evidence; controls must not.

### 3.5 Verdict vocabularies (MEASURED in code)

- Component: PASS / FAIL / UNMEASURED(cause: cascade, surprise, bland, budget, clock, precondition, harness,
  unjudgeable); `PASS(UNVERIFIED n)` taints.
- Run validity: CLEAN / DISRUPTED / INDETERMINATE (`contract.py`).
- Mod registry (`modcheck/status.py`): GREEN / RED / REFUSED / NEVER RUN / STALE (hash, not timestamp) /
  ORPHANED; DRAFT-CHECKLIST and PENDING-OWNER-REVIEW count as passing.
- Required-checks report (`required_checks_report.py`, observatory §2.4 NORMATIVE): ran × result × evidence-holds;
  **proven = completed ∧ PASS|FAIL ∧ evidence-holds yes**; taints `modal-open`, `stale-deploy`, `log-blind`,
  `focus-lost`, `upstream-failure`, `precondition`, `unverified-calls`, `stale-result`; amendments in
  `Transient/modcheck/obs_amendments.jsonl`. "Unknown is never clean": without a deploy fingerprint, every check is
  at best *pending deploy proof*.
- Watchdog: HEALTHY / STALLED / WEDGED / DEAD (exit 0–3); runner exit 3 FOCUS_LOST, 4 BUDGET.

### 3.6 Static gates that guard the live run (offline)

`validate_patch.py --live --defs`, `lint_calls.py`, `vacuity.py` (components that assert nothing — PASS = "setup
did not throw"), `walklint.py`, `doctor.py` (five registries agree; reports, never repairs), `floor.py` (every Mod
Settings toggle covered), `required_checks.py --check` (manifest drift), `mod_static.py`, `shipped_defs.py`,
`patch_targets.py`, `run_identity.py`, `run_selftests.py` (all selftests, parallel, explicit N/N),
`code_review_status.py`.

### 3.7 The acceptance ladder (MEASURED: `rimflow/model.py:215`, `LEVEL_NEEDS`)

| level | meaning | needs | cost |
|---|---|---|---|
| L0 | offline: XML lint, `validate_patch.py`, selftests, static bars — **attested, never owed** | offline | seconds |
| L1 | resolved-live: defs resolve in the engine (`jawa/get_defs` vs a manifest) | bridge | ~22 s minimal-list cycle |
| L2 | behaviour gauntlet: spawn, tick, harvest log; art presence by machine | bridge | minutes per sitting |
| GREEN-MIN | every north-star bar PASS on the minimal list (UNMEASURED ≠ green) | bridge | minutes per mod |
| GREEN-FULL | same on the full canonical list, all DLCs | bridge + full list | ~15–25 min cold load |
| L3 | Opus evaluation of art/style/theme | bridge | one evaluator pass |
| L4 | human: fun, coherence, UI | owner | owner time |

`model.cheapest_level` / `needs_for_levels` pick the cheapest outstanding level (selftest_built.py:167–171). An item
is `built` when every L0 criterion passes; `implemented` must be run after building (memory
`rimflow-redesign-built-validated-leases-2026-10-07.md`).

North-star ladder per mod (`debug_process.md` §6a): DRAFT → VALIDATED (owner word, hash-bound) → WIRED (`shows=`
claims every line; `modcheck floor`) → GREEN minimal → GREEN full → SHIPPED (deploy == repo with `.srchash`,
Mod Settings, art, review CLEAN). MEASURED 2026-10-03: 3 of 110 `validation.py` carry `shows=`.

### 3.8 Determinism assumptions (and where they break)

- Assumed: a bland map + paused-between-chunks + clock-gated ticks make a chain reproducible. **Not assumed by the
  code:** RNG seeds are not pinned anywhere in the harness (UNVERIFIED — no seed field in `run_identity.py`'s
  fingerprint; the observatory's "outcome discordance" metric requires "seed/state where known").
- Memory `spawn-many-for-bridge-tests.md`: one pawn's result can be pure RNG → spawn many.
- Storyteller, wild-animal replenishment and quest generators run unless the quiet world is applied; the naming
  dialog re-raises on a 1000-tick cadence; `Faction.FactionTick` and the incident queue are live.
- A load is a new awareness epoch: provenance does not survive save/load.
- Comparability between runs requires artifact + suite hash + mod list + fixtures (observatory §2.3); today only
  `modcheck record` and `run_identity` capture part of that, and only on the live_queue path.

### 3.9 Run budgets

`BELT_SUITE_BUDGET_S` 1500 s per suite (exit 4); job budget in `belt_heartbeat`; `clockgate` session cap and
per-frame caps (`tick_cap` declared per chain — Antiquities' 95,000-tick chain); `LOAD_BUDGET_S` 25 min; bridge
call timeout 30 s main-thread (`game_focus.py`); a backgrounded agent dies at 600 s of silence.

### 3.10 What historically invalidated runs (MEASURED from the 2026-10-03 baseline unless noted)

- **1,830 component verdicts on 2026-10-03: 41.3 % UNMEASURED**; of those, surprise ended the chain 345 (46 %),
  upstream cascade 282 (37 %), no bland map 60, clock 2, other 66 (`bridge_validation_observatory.md` §1.2).
- 2 of 16 reruns produced 0 rows (launch-gate refusal, focus loss); 6 of 20 jobs ended in ≤ 23 s (launch gate ×3,
  bland world, focus, smoke).
- Taint: rerun3 and rerun5 recorded 2–3 suites each while `Dialog_ModSettings` was open; rerun7 killed because the
  map carried `RM_WS_TerminatorFront` (a world mutator on the test tile).
- 27 components UNMEASURED in every one of ≥ 3 appearances (suite-defect candidates); 23 components PASSed in
  every one of ≥ 5 appearances (regression value unmeasured).
- Recovery ≈ 2.4 h of a 9.7 h window; cold loads ≥ 101 min observed.
- Further cases from the incident mining are in §4.

---

## 4. History of failure

**Method.** Two read-only sweeps (2026-10-10) over `infrastructure/state/lessons/*.md` (259 files), the auto-memory
notes in `~/.claude/projects/-home-mandrake-rm-foundry/memory/` (193 notes, ~60 incident-shaped ones read),
`infrastructure/state/items/closed/*.md`, `infrastructure/state/handoffs/`, and `Transient/` reports produced 183 raw
rows (102 + 81), which overlap. They were deduplicated by hand into the table below: **one row per distinct
incident**, the earliest dated occurrence, later recurrences named in the row. "Time lost" is quoted only where a
source states it; otherwise `unstated` (most sources state none, which is itself a finding: §6 G7). The class
counts at the end are computed by a script over this table's `class` column, not hand-tallied. Sources are
abbreviated: `L:` = `infrastructure/state/lessons/`, `M:` = memory note, `I:` = `infrastructure/state/items/closed/`,
`T:` = `Transient/`.

Classes: **SILENT** (bridge call reports success, nothing changed) · **HANG** (main thread stalled/looped, or a
false hang) · **MODAL** (dialog/focus/UI state blocks input) · **ZOMBIE** (game "loaded" but unusable, map culled)
· **MODLIST** (load failure, ModsConfig reset or drift) · **STALE** (repo ≠ game, stale DLL/deploy/process code)
· **LIE** (an instrument returns a confident wrong answer) · **ENV** (WSL/Windows/platform) · **SAVE** · **INVALID**
(run contaminated by events, visitors, staging, RNG) · **CONTENT** (our def/C# broke the game, often silently) ·
**PROCESS** (agent/coordination waste).

| # | date | class | symptom | real cause | time lost | durable fix, or MISSING | source |
|---|---|---|---|---|---|---|---|
| 1 | 2026-08 | MODAL | same 772-item job run 5× gave 759, 448, 0, 384, 384 while `execute_debug_action` reported success throughout | a leftover FloatMenu modal absorbed input; three wrong theories coded first | 5 runs + 3 rewrites | rule "assert UI state before each iteration"; **MISSING** as an enforced guard outside `watch.py` | M:stale-modal-blocks-every-later-call |
| 2 | 2026-08-20 | ZOMBIE | status `game_loaded` for hours; bridge answered plausible numbers from a dead load | save aborted in `ScribeLoader.FinalizeLoading` (a Harmony postfix threw *Collection modified*); engine bailed to menu | hours | `ErrorWhileLoadingGame` canary after settle (`first_light.py`) — **not** in today's preflights (UNVERIFIED) | M:rimworld-zombie-game-state |
| 3 | 2026-08-20 | STALE | an Ideology meme "dropped in both places" diverged for a day | game reads the AppData `Ideos` folder, not the repo `.rid` | ~1 day | skill `rimworld-deploy`; no `.rid` sync script (**MISSING**) | M:jawa-patches-deploy-path |
| 4 | 2026-08-21 | LIE | seven instruments gave confident wrong numbers in one session | tools return numbers, never errors | unstated | `measure`, `block_blind_scan.py` hook, skill `measuring-large-artifacts` | M:instruments-that-lie-with-a-number |
| 5 | 2026-08-23 | LIE | `./game` printed "bridge silent" and forced LOADING while the bridge was up | probe returned None when `GABP_SERVER_PORT` was unset | unstated | rule; probe fix state UNVERIFIED | M:game-probe-reports-ignorance-as-silence |
| 6 | 2026-08-23 | STALE | `[JawaBench]` ready lines absent from a 10,358-line log; looked like a failed deploy | module initializer was lazy (first tool call) | unstated | TPS constructor now runs the initializer at registration (`tps_record.md`) | M:jawabench-init-line-is-lazy |
| 7 | 2026-08-23 | SILENT | `PatchOperationRemove` of an inherited Gun tag matched nothing; clean log; shipped for days | inheritance resolves after patches; Conditional returns true on no match | days | `Inherit=False` pattern; **MISSING** a "patch matched nothing" detector | M:inherited-list-items-cannot-be-patched-away |
| 8 | 2026-08-24 | STALE | new Bantha/Eopie art invisible though repo == game by hash | art bound to a different `texPath` (life-stage `_j`, foreign defName) | unstated | rule "texture binds by texPath"; `art_fold_check.py` for folds | M:texture-binds-by-texpath-not-defname |
| 9 | 2026-08-26 | HANG | two bridge drivers at once wedged the bridge; one bulk op removed 50 unrelated placements | concurrent bridge calls, no lock | ~54 agent-min | lease `rimflow bridge take` | M:one-bridge-driver-at-a-time |
| 10 | 2026-08-26 | CONTENT | four tattoo GeneDefs vanished | a ModExtension type from an absent mod discards the whole def | unstated | `MayRequire` on `<li>`; `harvest_log` DEFS DISCARDED | M:modextension-missing-type-discards-def |
| 11 | 2026-08-26 | LIE | 251 tiles ran default Earth rosters; every pipeline stage reported success on zero rows | biomes missing from `biome_terrain.csv` | unstated | rule "zero rows is a failure" | M:zero-rows-is-a-failure-not-a-footnote |
| 12 | 2026-08-27 | SILENT | `spawn_pawn` "5/5" but 4 of 80 spawns were vanilla Colonists; a nonexistent weaponMoney defect was chased for days | silent kind substitution | days | spawn receipts with `readBackKinds` (2026-10-10) | M:census-requested-vs-actual-kind; T:foundry_map_awareness_design_20261010 E5 |
| 13 | 2026-08-27/30 | SILENT | `jawa/fire_raid` returned `executed:true, arrived:[]` for authored factions | `Leo.RaidProtectionFee` prefix replaced the raid with a modal and set `__result=true` | three retracted evidence tables | tool diffs the window stack, returns `blockedByDialog` | I:SIX_FACTIONS_NEVER_RAID_1 |
| 14 | 2026-08-30 | MODLIST | "Recovered from incompatible or corrupted mods" three times after a bare-exe relaunch | stale bundled `0Harmony.dll` path when bypassing Steam | 3 relaunch cycles | launch via Steam (`rimworld-load-round` §10) | M:launch-rimworld-via-steam-not-bare-exe |
| 15 | 2026-08-31 | SAVE | agent unpaused the real campaign ~8 s; a colonist died | live process on the persistent save | ~8 s game | owner: saves cover it; never save over keepers | M:save-states-cover-live-testing |
| 16 | 2026-09-02 | HANG | `COLD_LOAD_STALL_INTERMITTENT_1`: "4 stalls in 5 launches" | a healthy idle main menu (frozen log, busy CPU, no game) misread; processes killed | 4 false repros; ~70 min waited past a checkpoint in `COLD_LOAD_STATIC_CTOR_STALL_1` | closed NOT A BUG; `jawa/load_stall_probe` | M:idle-menu-looks-like-load-stall; I:COLD_LOAD_STALL_INTERMITTENT_1; I:COLD_LOAD_STATIC_CTOR_STALL_1 |
| 17 | 2026-09-02 | CONTENT | build passed `validate_patch` + `harvest_log`; the live load had 9+ `Config error in` lines | `Def.ConfigErrors()` is invisible to `validate_patch` | unstated | rule grep `^Config error in`; **MISSING** as a gate | M:config-errors-are-invisible-to-validate-patch |
| 18 | 2026-09-05 | SILENT | `rimworld/click_ui_target` `success:true`, selection unchanged | IMGUI synthetic input lost in nested groups | unstated | real OS click `system_click.py` | M:rimbridge-click-fails-silently-use-real-os-click |
| 19 | 2026-09-05 | MODLIST | `jawa/harmony_patches` showed 0/16 Ninefold patches; a defect was nearly filed | ModsConfig said 601 mods; the running process had 22 (another seat's minimal launch) | unstated | read the running set (`jawa/running_mods`, `jawa/mod_inventory`) | M:modsconfig-describes-the-next-load |
| 20 | 2026-09-05 | ENV | a seat window died | heavy ML from a subagent filled the 10 GB seat cgroup (OOM) | window lost | rule; also a python.exe driver OOM-killed during a load spike (2026-09-11) | M:heavy-ml-in-seat-cgroup-kills-window; T:handoff_harvest_20260918 |
| 21 | 2026-09-05+ | PROCESS | subagents deadlocked waiting on their own backgrounded commands — 2026-09-05, 09-18, 09-24 (≥6×), 09-27 (3 of 4 worktree agents), 09-29 (2× despite the brief) | only the parent gets notifications | whole agent runs | verbatim brief line; **MISSING** a hook | M:subagents-must-run-commands-foreground; L:20260924T183724Z…; L:20260929T164805Z… |
| 22 | 2026-09-11 | MODLIST | five parallel subagents relaunched RimWorld on their own ModsConfig; one stepped on another; list left unrestored | no serialisation | unstated | lease; rule only | M:parallel-subagents-must-not-all-drive-bridge |
| 23 | 2026-09-11 | MODAL | queued loads never ran; bridge answered but the main loop was frozen | unfocused RimWorld with `runInBackground` off; a "queued" load from an unfocused Entry is a no-op (3× measured) | unstated | `game_focus.focus_game()` first | T:handoff_harvest_20260918 |
| 24 | 2026-09-11 | CONTENT | `start_debug_game_ready` on the full ~590-mod list crashed natively (log stops mid-line, no exception), hit twice | null-`workerClass` biomes, a drug without `CompProperties_Drug`, a raceless PawnKindDef (CLAUDE.md, fixed by 2026-09-27) | unstated | `prove_quicktest_world.py` harness | M:quicktest-crashes-full-modlist-use-cheap-mechanism-list; T:handoff_harvest_20260918 |
| 25 | 2026-09-11 | INVALID | a Settlement quicktest arrived mid-raid with 100+ hostiles | quicktest scenario | unstated | sweep hostiles before testing; `bland_world` | T:handoff_harvest_20260918 |
| 26 | 2026-09-12 | LIE | a crash was attributed to 13 RSW animals | the filed description read a stale Player.log generation | unstated | corrected diagnosis; log archive by sha now exists | I:CORRECT_GIDDYUP_NULLKEY_1 |
| 27 | 2026-09-12 | SAVE | a save edit shrank ~500 KB for a ~50 B change | text-mode CRLF translation | unstated | rule: binary mode, check size delta | M:rimworld-savegame-text-mode-crlf-trap |
| 28 | 2026-09-13 | PROCESS | a second FOUNDRY window duplicated live-verify work on the same item and map | two windows, same role | unstated | **MISSING** (role per window by convention) | M:foundry-window-collision-202609130445 |
| 29 | 2026-09-18 | ZOMBIE | generated maps culled silently (2 lost); phantoms render; view wedged on the planet | no living colonists; mapgen left `RegionAndRoomUpdater` disabled | 2 maps | `map_commit`, `spawn_test_colonists.py`, `colony_found`; recurred 09-25, 09-30, 10-01 | M:generated-map-culled-unless-home; L:20260930T133957Z… |
| 30 | 2026-09-18 | MODLIST | RimWorld reset the live ModsConfig to Core + DLCs; recurred twice in one night (2026-09-27) | `MayRequire` on a top-level `<Operation>` is inert; the recipe ingredient resolved null | "an hour" | `01eca070e`; sweep: 0 live top-level `<Operation MayRequire>` (2026-10-09) | T:handoff_harvest_20260918; CLAUDE.md |
| 31 | 2026-09-18 | STALE | 6 of 65 repo DLLs differed from the deployed copies | deployed-DLL drift | with #30 | `.srchash` + `DLL_SOURCE_STAMP_GUARD_1` (push hook); `run_identity.py` | T:handoff_harvest_20260918 |
| 32 | 2026-09-1x | MODLIST | ModsConfig fell back to 6 mods mid-load | a sibling DLL (CreatureBehaviors) 6 h stale → TypeLoadException → "Resetting mods config" | unstated | deploy dependencies explicitly; `launch_gate` | T:handoff_harvest_20260918 |
| 33 | 2026-09-1x | CONTENT | every map-add crashed for the rest of the session | an abstract Alert subclass became a reflection leaf in the `AlertsReadout` ctor | unstated | sealed inert subclass | T:handoff_harvest_20260918 |
| 34 | 2026-09-1x | PROCESS | three backgrounded subagents died at 600 s of silence leaving nothing on disk; recurred 2026-09-23 | stream watchdog | whole runs | skeleton-file-first brief | T:handoff_harvest_20260918; CLAUDE.md |
| 35 | 2026-09-20 | SAVE | the canonical save refused to load (14 divergences after scrubbing 5) | the save's recorded 630-mod list diverged from the live list | unstated | partial scrub on the owner's word | I:CANONICAL_SAVE_MODLIST_DIVERGENCE_1 |
| 36 | 2026-09-2x | MODLIST | a session looked healthy but none of our defs loaded | a biome mod without its dependencies NRE'd `ThingDefGenerator_Corpses.CalculateMarketValue` → "Resetting mods config" | unstated | content fix | I:BAROQUE_CORPSE_MARKETVALUE_CRASH_1 |
| 37 | 2026-09-2x | MODLIST | a full-list load aborted and reset to Core-only; game non-responsive ~2 h before the log was read | a third unrelated root cause (`RecipeDefGenerator`) behind two real defects | ~2 h | `73c920d7a` | I:BLUEDESERT_ORPHAN_LOAD_CRASH_1 |
| 38 | 2026-09-2x | ENV | RimWorld crashed twice in one session (full 595 list) | ntdll fault near `world_tile_map_generate`; no managed exception | unstated | **MISSING** (no minidump: `spike.minidump` owed) | I:BRIDGE_NTDLL_CRASH_TILEGEN_1 |
| 39 | 2026-09-24/25 | HANG | a Player.log watcher matched the PREVIOUS session's `Bridge token:` (0 s false ready) | log not yet truncated by the new process | unstated | `launch_and_wait.sh` waits for truncation; **MISSING** in other wait loops (UNVERIFIED) | L:20260925T150224Z-BENCH…; L:20260924T183825Z-FOUNDRY… |
| 40 | 2026-09-24 | PROCESS | a subagent spawned children per checklist item; killing the parent left children driving the live game 10–20+ min | unprompted sub-spawning | 10–20+ min | brief rule forbids Agent/Task | L:20260924T021505Z-FOUNDRY… |
| 41 | 2026-09-25 | CONTENT | campaign save loaded with 0 pawns; all pawn creation broken | three creature defs with invalid diet values crashed GeneticRim; `validate_patch` passed | unstated | **MISSING** (only a load proves it) | L:20260925T143203Z-FOUNDRY-foundry-2026-09-25-def-that |
| 42 | 2026-09-25 | SILENT | `jawa/set_current_map` failed silently; a later `set_time_speed` ran the owner's real Map_3 ~10 min; 0 colonists + GameEnded | auto-culled map; a failed call does not stop later calls | ~10 min game time | rule re-check `map_info.mapId`; **MISSING** as a guard | L:20260925T230954Z-FOUNDRY-jawa-set-current-map… |
| 43 | 2026-09-25 | PROCESS | flyer flight hunted by screenshot: ~35 min, ~25 shots, nothing | screenshots cannot catch mid-flight | ~35 min | owner ruling (said 3×): state read of `Pawn_FlightTracker` only | L:20260925T041445Z…; CLAUDE.md |
| 44 | 2026-09-25 | LIE | a subagent with 90+ bridge calls showed "idle 58 min" | ledger idle counts rimflow events, not bridge calls | unstated | `bridge_sessions.jsonl` (2026-10-04) | L:20260925T143203Z-FOUNDRY-…bridge-lock |
| 45 | 2026-09-25 | INVALID | a real raid within seconds of unpausing a scratch map | `world_tile_map_generate` defaulted to a Settlement parent → resident faction base | unstated | check `world_tile_get` first; bland recipe | L:20260925T194434Z-FOUNDRY… |
| 46 | 2026-09-25 | STALE | `deploy_custom_mods --apply` (full sweep) exit 0 but `CreatureBehaviors.dll` still drifted | not isolated | unstated | `CREATUREBEHAVIORS_DLL_DEPLOY_DRIFT_1` (cause open) — **MISSING** | L:20260925T222002Z-FOUNDRY… |
| 47 | 2026-09-26 | MODLIST | `modlist_swap --restore` silently dropped SeaShores and Bacta | the restore source `ModsConfig.FULL.LATEST.xml` was stale after hand edits | unstated | rule; **MISSING** a freshness check | L:20260926T005413Z-BENCH… |
| 48 | 2026-09-26 | SILENT | `jawa/world_neighbors path=` wrote an 840 KB dump into the game install root | the param is an output path | unstated | lesson only | L:20260926T065152Z-UNSEATED… |
| 49 | 2026-09-26 | LIE | five identical wrong screenshots of moved pawns | `step_game_ticks` while paused leaves stale tween positions | 5 shots | unpause 1 s then re-pause | L:20260926T042423Z-UNSEATED… |
| 50 | 2026-09-27 | INVALID | lock-respecting FOUNDRY lost a live verify three times | BENCH worktree agents swapped ModsConfig and restarted the game every 10–15 min without taking the lease | 3 verifies | worktrees OFF (2026-10-02); **MISSING**: the lease does not gate ModsConfig writes | L:20260927T043135Z-FOUNDRY-bridge-lock… |
| 51 | 2026-09-27 | STALE | a live verify read old code as a clean pass | stale deployed DLL: its startup self-test line was simply absent | unstated | rule "confirm the self-test line is present" | L:20260927T043135Z-FOUNDRY-stale-deployed-dll… |
| 52 | 2026-09-28 | STALE | `load_game_ready` refused the save; sat broken 2 days | deployed `About.xml` packageId drifted from ModsConfig (half-executed tier migration); the deploy tool compares repo vs deployed only | 2 days | `12f180372` (one case); **MISSING** generally | L:20260928T032040Z-FOUNDRY… |
| 53 | 2026-09-28 | CONTENT | 15 FeverWood plants present, deployed, active, unresolvable | `<purpose>None</purpose>` invalid enum discards the whole ThingDef | unstated | grep rule; **MISSING** a lint | L:20260928T042821Z-FOUNDRY… |
| 54 | 2026-09-29 | MODLIST | the owner's "game is loading" relay was a subagent quicktest; ModsConfig left on a stray 13-mod tier; recurred 2026-10-07 (11-mod KineticArms tier after bridge release) | tier swaps are not restored on release | one wasted restart | parse `activeMods` vs FULL.LATEST; **MISSING** restore-on-release | L:20260929T164805Z-FOUNDRY-cross-session…; L:20261007T211316Z-BENCH… |
| 55 | 2026-09-29 | HANG | `Player.log.WARDEN_MOTHER_hang_2026-09-29` captured | not analysed (the scan hook blocked a blind scan) | unstated | **MISSING** analysis | T:Player.log.WARDEN_MOTHER_hang_2026-09-29 |
| 56 | 2026-10-01 | INVALID | hours of a live pass lost to naming dialogs, random events, focus theft, dirty maps; "burned 3h+ on harness" | non-static test worlds | 3 h+ | `bland_world.py`, detectors, `saved_base.py` | M:static-boring-test-worlds…; T:foundry_map_awareness_design_20261010 E6 |
| 57 | 2026-10-01 | STALE | ~64 `Could not find type named RimMandrake.*`; quicktest died in `GenerateStartingPolicies` | a deploy from a stale checkout shipped old DLLs | 30 min (08:36→09:06 on 10-03 for the same class) | `launch_gate.py` | `modcheck/launch_gate.py` docstring; observatory §1.2 |
| 58 | 2026-10-01 | MODLIST | 27 gates named retired packageIds and were silently dead; 26 more `MayRequire` sites on 2026-10-09 | biome mods composed into `mandrake.rm.biomes`; member ids have no runtime packageId | until found | `MayRequireAnyOf`; consult `Biomes.compose.json` | L:20261001T115528Z…; L:20261009T100707Z… |
| 59 | 2026-10-03 | MODAL | rerun13 died in < 1 s ("could not bring RimWorld forward"); polled 5+ min as running | focus refusal; a process-alive poll cannot see a dead run | 5+ min (and 15:23→15:28) | `focus_heal.py` exit 3; `belt_heartbeat`; `belt_watchdog` | L:20261003T223850Z-FOUNDRY-belt-hang-classes; runbook row 1 |
| 60 | 2026-10-03 | HANG | game hung in a `QuestNode_TradeRequest` test-run exception loop, log frozen 14:59; again twice in Bacta `tank_scar` | `search_debug_actions` / `execute_debug_action` expand every debug node → quest-gen test loops on the main thread | ~24 + ~28 min | ban from suites; `jawa/pawn_health action=permanent`; watchdog `KNOWN_LOOPS` | runbook rows 2, 8; T:belt_bridge_log_20261003 |
| 61 | 2026-10-03 | HANG | `bland_world.setup` on the full list wedged the game; every `step_game_ticks` "DoSingleTick failed" | `mlie.nwnrealfogofwar` IndexOutOfRange every Update after ruins were destroyed on a second map | ~27 min | drop RealFoW from test lists | L:20261003T200004Z…; runbook row 3 |
| 62 | 2026-10-03 | MODAL | rerun3/rerun5 suites recorded RED while `Dialog_ModSettings` was open; Aftermath raid `Dialog_NodeTree` 23:37–23:47 tainted four suites | stale settings poke; raid letter with forcePause | one clean rerun each | runner closes ModSettings/naming at job start/end; `modal-open` taint; **MISSING**: closing arbitrary new modal types | runbook row 4; T:belt_bridge_log_20261003 |
| 63 | 2026-10-03 | LIE | Player.log and `drain_log` went blind while the game ran (MCR mood-chain logger, 16:54) | Verse.Log stops at 10,000 messages (lesson title says 1,000: DOC-ROT) | unstated | `runner.py` `ResetMessageCount` per chain; watchdog names it; health_observer `log.cap-reached` | L:20261004T001940Z… |
| 64 | 2026-10-03 | MODLIST | repeated tier swaps destroyed the first ModsConfig backup | `modset_builder --apply` overwrites the before-tier backup | unstated | rule copy aside; **MISSING** in the tool | L:20261003T032811Z… |
| 65 | 2026-10-03 | OTHER | our two trader rows absent from the live `Base_Outlander_Standard` | `JM.betterTraders` full-def replace; a runtime remover trims 69 → 64 rows | several hours, unresolved | **MISSING** | T:belt_bridge_log_20261003 |
| 66 | 2026-10-04 | CONTENT | a hidden faction never existed; its raid never arrived; bare NullReferenceException | FactionDef lacked `factionNameMaker`/`fixedName`; the NRE also left 6 edge-spawned ants that bit colonists in later chains | two loads | `jawa/static_call` returns 6 stack frames; defs fixed | L:20261004T064814Z-FOUNDRY-factiondef…; T:belt_bridge_log_20261003 |
| 67 | 2026-10-04 | MODAL | the clock force-paused mid-chain every ~600 ticks; a dryRun `fire_incident success=false` misread | an unnamed colony re-raises `Dialog_NamePlayerFactionAndSettlement` (TicksGame % 1000 == 200) | unstated | `jawa/name_colony`; `saved_base.induce_and_finish_naming` | L:20261004T012758Z… |
| 68 | 2026-10-04 | LIE | suites scored FAIL on correctly loaded defs (Armoury ×5, LanternDeeps ×1) | `get_defs` cannot read `System.Type` fields / GenStep class | unstated | assert from XML + `foundCount` | L:20261004T064815Z… |
| 69 | 2026-10-04 | LIE | a modal sweep marked every verdict "unknown" | `window_list_close` `success:false` "No open window" is the CLEAN answer; python.exe cannot run git on `\\wsl.localhost` so run identity was unknown | unstated | lesson; run identity now from the mirror's `MIRROR_HEAD` | L:20261004T064814Z-FOUNDRY-modal-sweep… |
| 70 | 2026-10-04 | INVALID | "stopped" matrix runs kept driving the game; three concurrent drivers corrupted results | `Stop-Process` CommandLine match silently matched nothing for UNC-launched python.exe | unstated | kill by PID, count afterwards | L:20261004T220351Z-FOUNDRY-powershell… |
| 71 | 2026-10-04 | HANG | `launch_and_wait.sh` gave up at ~5 min; the full 638-mod cold load took ~13 min | timeout too short | unstated | wait for a truncation-checked `Bridge token` | L:20261004T220351Z-FOUNDRY-launch-wait… |
| 72 | 2026-10-04 | MODAL | the owner objected to the game being fullscreened/focused for review screenshots | agent used ShowWindow + `game_focus.py` | owner attention | rule; **MISSING** a guard; conflicts with `focus_heal` | M:dont-fullscreen-or-focus-the-game |
| 73 | 2026-10-05 | INVALID | mechanoids wandering a hand-walked review map | no hostile sweep | owner review spoiled | `sweep_hostiles` in `human_review.py` | M:kill-hostiles-on-review-maps; E2 |
| 74 | 2026-10-05 | INVALID | a proof run went STALE; SL4 UNMEASURED | any mod-folder change stales the proof; a fresh map with < 2 free colonists | unstated | finish edits before proof | L:20261005T155316Z… |
| 75 | 2026-10-05 | STALE | an art redo rendered without canon guidance all day | `artpiped` loads its code once; ran 2026-10-03 code all of 10-04 | one day | compare process start vs commit | L:20261005T034233Z-BENCH… |
| 76 | 2026-10-06 | MODAL | an OS screenshot captured the owner's terminals | `system_screenshot.py` grabs the top window | unstated | use `rimworld/take_screenshot` for game frames | L:20261006T162331Z… |
| 77 | 2026-10-07 | STALE | a mutation test looked like no effect | the staged build reused a stale DLL within ~1 s | unstated | sleep, touch, confirm `.srchash` | L:20261007T220228Z-FOUNDRY-mutation-build-stale-dll |
| 78 | 2026-10-07 | HANG | another window took the bridge after 45 idle min and killed a helper's live session | the lease goes stale at 45 min of ledger silence, not bridge silence | unstated | rule: an event per 45 min | L:20261007T220228Z-FOUNDRY-bridge-hold-stale-45min |
| 79 | 2026-10-08 | HANG | a helper declared the game hung (Player.log silent 17+ min); the owner found it responsive; same misread in BENCH's handoff | log mtime is not liveness | unstated | `./game` bridge round-trip; `BRIDGE_STALL_DIAGNOSTIC_1`; TPS heartbeat `mainBeatUtc` | L:20261009T024339Z-BENCH…; handoffs/BENCH_REBOOT_HANDOFF_202610090437 |
| 80 | 2026-10-08 | MODLIST | the weepingstones tier was BROKEN | missing `mandrake.rut.rotsporekit`; its owner folded into `mandrake.rm.biomes` | unstated | use `acc_green_min` | T:belt_bridge_sweep_20261008 |
| 81 | 2026-10-08 | SAVE | `rimworld/save_game` wrote the CURRENT slot rather than `saveName` (again; once it wrote 0 bytes) | bridge tool | unstated | `saved_base.save_base` proves a new file | T:belt_bridge_sweep_20261008; T:handoff_harvest_20260918 |
| 82 | 2026-10-09 | CONTENT | a native Burst-job crash with no managed exception, Stillsand 100×100, 4 of 4 | `RM_MapComponent_ShadeGrid` freed a sun-cost array one rebuild early | unstated | `RM_DeferredDisposal` (60 ticks) | L:20261009T100707Z-FOUNDRY-native-burst… |
| 83 | 2026-10-09 | INVALID | `scenelib.run` polling scored a behaviour FAIL on a ~50-tick mental state | `run()` overshoots by ~100+ ticks | unstated | poll with `step_game_ticks` | L:20261010T051816Z-FOUNDRY-short-mental-state… |
| 84 | 2026-10 | INVALID | bland-world run #1 setup gate FAILed; run #2 on map 2 also gated out | hostile insects arrive with a fresh map via mapgen | 25.5 min of a 210-min pass | setup gate; mapgen-origin recorder (not deployed) | T:foundry_map_awareness_design_20261010 E1 |
| 85 | 2026-09 | INVALID | a hostile-AI test was inconclusive over 1,260 ticks | the test subject wandered in via a wanderer-join event | one criterion unproven | detectors `player_joiner` | E3, same source |

### 4.1 Class counts (MEASURED: computed over the `class` column above)

| class | rows | share |
|---|---|---|
| MODLIST | 12 | 14 % |
| STALE | 10 | 12 % |
| INVALID | 10 | 12 % |
| LIE | 9 | 11 % |
| HANG | 9 | 11 % |
| CONTENT | 8 | 9 % |
| MODAL | 7 | 8 % |
| SILENT | 6 | 7 % |
| PROCESS | 5 | 6 % |
| SAVE | 4 | 5 % |
| ZOMBIE | 2 | 2 % |
| ENV | 2 | 2 % |
| OTHER | 1 | 1 % |
| **total** | **85** | |

Raw sweep tallies before dedup, for comparison (subagent counts, not re-verified): lessons+memory 102 rows (PROCESS 15, LIE 13, MODLIST 10, INVALID 9, SILENT 8, CONTENT 8, STALE 8, HANG 7, MODAL 7, ENV 6, ZOMBIE 5, SAVE 4, OTHER 2); items+Transient 81 rows (INVALID 14, MODLIST 12, HANG 9, SILENT 8, STALE 7, MODAL 6, LIE 6, CONTENT 6, OTHER 4, SAVE 3, ENV 3, ZOMBIE 2, PROCESS 1).

### 4.2 What the history says

- **The expensive classes are the quiet ones.** Rows with "days" or "hours" lost (#2, #3, #7, #12, #13, #16, #37,
  #52, #56, #65) are almost all SILENT, STALE, LIE or MODLIST, where nothing errored. Loud failures (hangs) cost
  minutes to ~30 min each once the watchdog existed (2026-10-03).
- **Recurrence is the norm, not the exception.** Rediscovered 2+ times: background-wait deadlock (≥ 5 dates),
  ModsConfig left on a test tier / clobbered by another driver (2026-09-11, 09-26, 09-27, 09-29, 10-07), stale DLL
  read as success (≥ 6 dates), Player.log misused as a liveness or readiness oracle (09-02, 09-24/25, 10-03,
  10-08), map culling (4 dates), `save_game` wrong slot (≥ 3), modal stalls (≥ 6 dialog types). **A rule in prose
  did not stop any of these; a tool or a hook stopped several** (launch gate, watchdog, `saved_base`, receipts).
- **The bridge lease protects the bridge, not the game's configuration.** Five MODLIST/INVALID rows are other
  agents changing `ModsConfig.xml` or relaunching while the lease was held correctly (#22, #50, #54, #64, plus the
  parallel build agents of 2026-09-26).
- **Two kinds of "hang" are not hangs**: a healthy idle main menu (#16) and a quiet log on a responsive game (#79).
  False hangs led to killed processes and false items.
- **Content defects surface as engine-wide symptoms** (#24, #30, #32, #36, #37, #41, #33): a single bad def
  resets the mod list, empties pawn creation, or crashes every map-add. The first exception names it; the
  loudest does not.

---

## 5. Prediction

### 5.1 Measurements taken for this section (2026-10-10, offline, read-only)

| # | measurement | result |
|---|---|---|
| P-a | live `ModsConfig.xml` vs `infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml` (parsed `activeMods`) | live = **67** (a test tier is active now); FULL.LATEST = **551**; **14 of the live tier's mods are absent from FULL.LATEST**, including `mandrake.rm.bazaar`, `.warcasket`, `.watchers`, `.keelhoist`, `.raidredesigner`, `.solarmirrors`, `.acousticscanner`, `mandrake.rsw.trophycraft` |
| P-b | FULL.LATEST performance/tick mods | `taranchuk.performanceoptimizer` and `mlie.nwnrealfogofwar` (the 2026-10-03 wedge, #61) are both on the full list |
| P-c | companion: repo vs game | repo DLL sha `54ed9331…` (11:27) ≠ game `87b7370b…` (09:50); **no `.srchash`** for the companion |
| P-d | lint schema snapshot | `tool_schemas.json` from 2026-10-03; **26** declared companion tools missing |
| P-e | per-call telemetry | newest `_obs/runs` file 2026-10-06; 151 bridge sessions today, top clients ad-hoc scripts |
| P-f | WSL vs Windows UTC clock | 1 s apart now (`date -u` vs PowerShell `UtcNow`) |
| P-g | scheduled observers | `RimMandrake\TPS Observer` installed (Ready); `health_observer` not installed (deliberate) |
| P-h | stale runner state | `.belt_state/heartbeat_situational_rerun.json` from 2026-10-06, `heartbeat_preflight.json` from 2026-10-03 |
| P-i | "prior-pass-now-fail diff" (`debug_process.md` §1 item 2) | no module found by `grep -rl 'prior.pass\|now.fail'` in `Utils/` → UNVERIFIED as built; treat as owed |

### 5.2 Ranked predictions

P = probability it bites within ~2 weeks (judgement, 0–1); C = expected cost when it bites, in agent/bridge minutes
(judgement, anchored to §4 rows); **score = P × C**. Rows are in rough order; the **score column is the ranking**. Top five by score: **1** (144), **3** (48), **2** (42), **4** (42), **6** (30), then 5 (27), 12 (21). Every row names a pre-emptive check that can be built or run
**offline now**. "Class" links to §4.

| id | prediction | class (history) | P | C | score | pre-emptive check (offline, now) |
|---|---|---|---|---|---|---|
| 1 | **The MUST 17 overhead test (C0–C5) is confounded** by a mid-protocol companion redeploy (map-awareness DLL is built, not deployed — P-c), by `taranchuk.performanceoptimizer` changing what `TickManagerUpdate` costs, or by the `health_observer` running unannounced in a configuration that forbids it | STALE (#31, #51, #77) | 0.6 | 240 | 144 | Freeze a **run manifest** per configuration: companion sha (needs a `.srchash`), `modOrderDigest` from the TPS `session` row, observer task state. Refuse to start a configuration whose manifest differs from C0's except in the one declared variable |
| 2 | **GREEN-FULL / full-list runs test the wrong mod set**: FULL.LATEST lacks 14 of our own newer mods (P-a), so a `--restore` silently drops them (recurrence of #47) and a GREEN-FULL claims coverage of mods that never loaded | MODLIST (#47, #54) | 0.7 | 60 | 42 | Offline: diff FULL.LATEST against every `src/*/*/About/About.xml` packageId that is meant to ship (and against `Biomes.compose.json` members, which must NOT appear). Live: `jawa/running_mods` set == declared tier set, as `modcheck record` already does — make every runner do it |
| 3 | **Harmony hazards in the recorders on the 550-mod list** (GPT 2.3 FAIL stands, `TPS_HOOKS_HARDEN_REENTRY_AND_LATE_GUARDS`): reentrancy, late install, another mod's prefix/transpiler on `DoSingleTick`, `TickManagerUpdate`, `IncidentWorker.TryExecute`, `PawnGenerator.GeneratePawn` | CONTENT/STALE | 0.4 | 120 | 48 | Offline: a patch-target census — for each method we patch, list every other mod that patches it (from the last `session_<id>.json` `patchChains`, or `jawa/harmony_patches` output archived), flag prefixes that can return false and transpilers; a C# selftest that re-enters each hook |
| 4 | **Performance Optimizer distorts or blinds the TPS record only on the full list** (it patches tick paths); minimal-list proofs pass, full-list attribution reads `attrValid:false` or `profSkipped` high, or windows are miscounted | LIE | 0.35 | 120 | 42 | Read its patch list offline (its assemblies are on disk) and intersect with our ten attribution targets; add `profSkipped`/`attrValid` rates to the C4 acceptance limits declared before the run |
| 5 | **Most live evidence stays unrecordable**: ad-hoc scripts (`_kb_call_tmp.py`, `l2sweep_run.py`, `scenes/*`) bypass `rimdrive.Session` telemetry, `run_identity`, the heartbeat and the results file (P-e) | PROCESS | 0.9 | 30 | 27 | Move the telemetry hook down into `rimbridge_client.py` (the one client every script uses — it already writes `bridge_sessions.jsonl`); make it stamp script name, deploy fingerprint and companion sha on session open |
| 6 | **Observer effect during cold load and world gen**: the awareness `GeneratePawn` hook (the hottest hook, `game_health_record.md`) and stage timers add time exactly where loads already stall; a slower load then trips `LOAD_BUDGET_S` or looks like a regression | HANG | 0.5 | 60 | 30 | Ship awareness switched OFF for generation until measured; an offline microbenchmark of the hook body (`AwarenessSelfTest` already builds the core); record load duration per launch from `health_observer` milestones (`engine.init` → `bridge.token`) so a delta is visible |
| 7 | **New-content load killers recur** as biome mods merge into `RimMandrake.Biomes`: drug without `CompProperties_Drug`, FactionDef without a name maker, `BiomeWorker` touching `SurfaceTile.Rivers`, abstract Alert subclass, invalid enum (`<purpose>None`), ModExtension of an absent type, `MayRequire` on `<Operation>`, member-id `MayRequire` | CONTENT/MODLIST (#24, #30, #33, #41, #53, #58, #66) | 0.5 | 40 | 20 | One offline **load-killer lint** over `src/` XML + C#: each of these eight patterns is a regex/XPath or Roslyn-free text check with a sanity probe. Each cost a cold load at least once |
| 8 | **RealFoW wedges a GREEN-FULL bland-world run** — the remedy was "drop it from test lists" but the full list still carries it (P-b) | HANG (#61) | 0.6 | 30 | 18 | Either declare the bland recipe incompatible with RealFoW and refuse up front, or skip ruin destruction on the full list; preflight checks `activeMods` for known wedgers (a list kept beside `KNOWN_LOOPS`) |
| 9 | **The companion deployed ≠ the companion Python expects**: `scene_report`/detectors expect awareness fields (`lookTargetIds`, `pawn_origin`) the deployed DLL lacks; results go `unavailable`/INDETERMINATE and get misread as findings | STALE | 0.6 | 30 | 18 | Give the companion a `.srchash` and a `jawa/version` answer (build sha + tool count); preflight compares it with the repo artifact and with the Python's expected capability list |
| 10 | **A visitor run is CLEAN while disrupted invisibly** (food, bed, path blocking, psychic effects — stated blind spots of `contract.py`), producing a false PASS on mood/need/job criteria | INVALID | 0.3 | 60 | 18 | Per-component declaration `sensitive_to_visitors=True` for need/mood/job criteria → any visitor makes those components INDETERMINATE rather than CLEAN; offline lint lists components touching needs/mood without the flag |
| 11 | **Native crash with no managed trace** (Burst #82, ntdll #38) recurs with nothing to diagnose | ENV/CONTENT | 0.3 | 60 | 18 | `spike.minidump` (owed): Windows Error Reporting LocalDumps registry key for `RimWorldWin64.exe` is a one-time, offline-installable setting; verify headroom on C: |
| 12 | **Subagent deaths and background deadlocks recur** (≥ 5 dates, §4 #21, #34) | PROCESS | 0.7 | 30 | 21 | A `PreToolUse` hook in subagent context refusing `run_in_background` on Bash, and a brief linter refusing a bridge-driving brief without "skeleton first" + "watchdog every 5 min" |
| 13 | **First real `modcheck run` after the swap-path fix** leaves the owner's list on MINIMAL or crashes (never re-exercised live, `runner.py` docstring) | MODLIST | 0.5 | 40 | 20 | Offline rehearsal on a copy of `ModsConfig.xml` in a temp dir (swap → simulated crash → `finally` restore → parse-compare); make `modlist_swap` accept a target path for the test |
| 14 | **RimBridgeServer or a workshop mod updates overnight** (Steam auto-update): extension discovery changes (the TPS record's autostart depends on `TryCreateInstance` of an instance tool), or the mod set changes and runs become incomparable | STALE/MODLIST | 0.3 | 60 | 18 | Record server version + `modOrderDigest` per run (already in the TPS `session` row) and diff it against the last green run in preflight; refuse "comparable" when they differ |
| 15 | **Load-time hang hidden by the 25-minute grace**: the watchdog suppresses Not Responding for the first 25 min and the TPS recorder does not exist yet | HANG (#16, #71) | 0.4 | 40 | 16 | Install `health_observer` as the standing early-load witness after MUST 17 (its `log.growth` + milestones see the load); set `LOAD_BUDGET_S` from measured load times per tier, not a constant |
| 16 | **Verse.Log cap reached sooner** because our own lines (`[JawaBench]` markers, init lines, scene/awareness diagnostics) plus 550 mods' noise count toward 10,000 | LIE (#63) | 0.5 | 30 | 15 | Count our own Player.log lines per hour offline from the archived logs in `JawaBench\tps\logs`; budget them; `runner.py` resets per chain but ad-hoc scripts do not |
| 17 | **Unknown modal types** from new mods (Bazaar trade window, raid redesigner letters) are not in `BAD_MODALS` and silently freeze/pause runs | MODAL (#1, #62, #67) | 0.5 | 30 | 15 | Invert the rule: any window not in an allow-list (`HARMLESS`) during a run is a modal; collect the allow-list from `window_list` on a clean bland map once |
| 18 | **Workshop-mod drift breaks a full-list load** (reset to Core) between two cold loads | MODLIST | 0.5 | 30 | 15 | Snapshot workshop `About.xml` versions + mtimes at each green load; preflight lists changed mods before the next cold load is spent |
| 19 | **Lint gives false confidence or gets ignored**: 26 tools missing from the snapshot (P-d) produce UNKNOWN_TOOL on legitimate calls | HARNESS | 0.8 | 15 | 12 | Regenerate `tool_schemas.json` from the C# `[Tool(` declarations offline (as measured here) plus the RimBridgeServer list; a selftest fails when declared ⊄ snapshot |
| 20 | **`search_debug_actions` / `execute_debug_action` re-enter a suite** (runbook row 8) | HANG (#60) | 0.3 | 30 | 9 | Add a BANNED list to `lint_calls.py` (none today, MEASURED grep) |
| 21 | **Two game processes at once** (owner's + agent's, or a zombie) confuse pid matching, the bridge port and retention | ZOMBIE | 0.3 | 30 | 9 | Preflight counts `RimWorldWin64` processes and refuses > 1 |
| 22 | **Daylight-saving end (Sunday 2026-11-01, America/Los_Angeles)**: `tps_record.py --at "01:30"` is ambiguous; `bridge_utilization.py` reads python.exe's *naive local* stamps | LIE | 0.9 | 10 | 9 | A selftest with a 01:30 fold; make every writer stamp UTC with offset |
| 23 | **Lease taken from a live helper** because the lease measures ledger events, not bridge activity (#78) | HANG | 0.3 | 30 | 9 | `rimflow bridge who` consults `bridge_sessions.jsonl` (activity in the last 10 min) before declaring a hold stale |
| 24 | **Wild-spawner block or quiet-world settings leak** into the owner's play after a run (patched on first block, until release) | INVALID | 0.3 | 30 | 9 | `Watch.__exit__` asserts release with a read-back; preflight and `belt_watchdog` report "quiet world ARMED" as a WARN |
| 25 | **`save_game` writes the wrong slot** from a script that does not use `saved_base.save_base` (#81) | SAVE | 0.4 | 20 | 8 | Route all saves through one wrapper; lint flags direct `rimworld/save_game` calls |
| 26 | **`runInBackground` reverts per launch** (set in memory via `static_call`) and focus starvation returns; meanwhile `focus_heal` minimising the owner's windows breaks the owner's ruling (#72) | MODAL | 0.5 | 15 | 8 | Preflight reads `Prefs.RunInBackground` live and refuses if false; offline check of `Prefs.xml` after a clean exit |
| 27 | **False hang still triggers a kill** (healthy idle menu, quiet log) — the TPS heartbeat now distinguishes, but agents still read log mtime | HANG (#16, #79) | 0.4 | 20 | 8 | `belt_watchdog` verdict text cites `mainBeatUtc` age first; the runbook's first line says "log mtime is not liveness" |
| 28 | **Retention evicts evidence before it is asked for**: 256 MB caps with awareness rows armed, or several heavy days | LIE | 0.2 | 30 | 6 | Measure bytes/day from the existing 4.9 MB record; alert when projected eviction age < 7 days |
| 29 | **Provenance epoch reset on every `saved_base.world_reset`** (a load = new epoch) makes every baseline pawn "origin unknown"; readers treat unknown as absent | LIE | 0.6 | 10 | 6 | The scene report prints the epoch start tick next to every "unknown"; contract treats baseline-unknown as expected, not INDETERMINATE |
| 30 | **WSL clock drift after host sleep** mis-orders joins between WSL-written and Windows-written records (1 s now, P-f) | ENV | 0.3 | 20 | 6 | Preflight prints the skew; refuse a join when > 2 s |
| 31 | **Stale `.belt_state` heartbeats** (P-h) are read as a current runner by a later watchdog pass | LIE | 0.3 | 10 | 3 | Heartbeat carries a run id + start time; watchdog ignores heartbeats with no matching process |
| 32 | **Mirror refresh races the scheduled `tps_observer`** (runs from `D:\Luke\dev\RimMandrake`, rewritten every 5 min) → transient import errors; Windows observer runs origin/main code while the WSL reader runs the seat clone | ENV | 0.3 | 10 | 3 | Observer catches ImportError into `observer_last.json`; reader prints the observer's code sha |
| 33 | **The "instance tool, public ctor" invariant is broken** by a refactor and TPS autostart silently reverts to first-call | STALE | 0.15 | 60 | 9 | Offline source check in `selftest_tps_record.py`: `JawaBenchTpsTools` has a public parameterless non-static ctor and `tps_report` is an instance method |
| 34 | **A run is judged on a mod edited mid-run** (proof STALE, #74) or a DLL rebuilt during a run | STALE | 0.4 | 20 | 8 | `run_identity` start/end fingerprint already exists on live_queue — extend to every runner (prediction 5) |

### 5.3 The pre-flight (proposed design, `src/RimMandrake/Utils/preflight_bridge.py`, NOT BUILT)

**Goal:** before a 15–25 min cold load or a bridge session is spent, catch the top classes (MODLIST, STALE,
CONTENT load killers, HANG wedgers, ENV) in under a minute offline, then confirm the first five live minutes.
**Contract:** every check returns PASS / FAIL / UNMEASURED with evidence; UNMEASURED refuses unless
`--allow-unmeasured`; a refusal names the §4 row it prevents. Reuse the existing pieces; build no parallel system.

**Phase A — offline (game down or up; no bridge; < 60 s)**

| id | check | reuses | catches |
|---|---|---|---|
| A1 | intended tier resolved (`modset_builder.resolve_tier`) == the `ModsConfig.xml` that the NEXT load will read (parsed) | modset_builder | #19, #54 |
| A2 | FULL.LATEST ⊇ every shipping `mandrake.*` packageId; no composed-member ids in any tier | About.xml glob, `Biomes.compose.json` | P-a, #47, #80 |
| A3 | known wedgers on the list (`mlie.nwnrealfogofwar` with bland_world; others from `KNOWN_LOOPS`) | belt_watchdog | #61 |
| A4 | every deployed mod DLL `.srchash` == repo; companion sha == repo artifact; `deploy_custom_mods.py` plan empty for the tier's mods; deployed `About.xml` packageIds == ModsConfig ids | run_identity, deploy tool | #31, #46, #51, #52, #57 |
| A5 | load-killer lint (the eight patterns in §5.2 prediction 7) over the tier's mods | new | #24, #30, #33, #41, #53, #58, #66 |
| A6 | `validate_patch.py --live --defs` for changed mods since the last green load | existing | #7, #17 |
| A7 | `lint_calls.py` over the scripts about to run, with a regenerated schema snapshot and a BANNED list | lint_calls | #60, P-d |
| A8 | workshop + RimBridgeServer version diff since the last green load | TPS `session` row | prediction 14, 18 |
| A9 | environment: one or zero `RimWorldWin64` processes; WSL/Windows clock skew < 2 s; free disk on C: and D:; `observer_last.json` age < 5 min; no stale `.belt_state` heartbeat without a process | tps_observer, belt_watchdog | prediction 21, 30, 31 |
| A10 | `--vacuity` and `--mock` selftest of the suites about to run exit clean | vacuity.py, run_selftests | §1.2 harness class |
| A11 | the decision strings for this load are written (file exists, non-empty) | load-round doctrine | process |

**Phase B — first five live minutes (bridge held; read-only except the named fixes)**

| id | check | reuses | catches |
|---|---|---|---|
| B1 | launch observed fresh: Player.log truncated after launch, then `Bridge token:` of THIS process (pid + start time) | launch_and_wait.sh logic | #39 |
| B2 | `launch_gate` over the new log (type errors) + `Config error in` count + `ErrorWhileLoadingGame` / "Resetting mods config" absent + first exception printed | launch_gate | #2, #17, #30, #32, #57 |
| B3 | running set (`jawa/running_mods`) == A1's tier set | modcheck.record | #19, #54 |
| B4 | `jawa/version` (to build) == repo companion; the TPS `session` row `startedBy: bridge-registration`, `install.sampler: complete`, `attrValid` not false in the first windows | TPS record | prediction 1, 9, 33 |
| B5 | main thread turning over: `get_ui_state` round trip < 2 s; `Prefs.RunInBackground` true; foreground irrelevant | belt_watchdog bridge probe | #23, #59 |
| B6 | no modal outside the allow-list; colony named; game paused | belt_watchdog modals, saved_base | #1, #62, #67 |
| B7 | map is `Playing`, has colonists, is home (not culled), quiet-world read back if the suite needs it | live_queue preflight, bland_world.assert_world | #29, #42, #84 |
| B8 | Verse.Log message count headroom (or a `Log.Clear` reset) | runner.py reset | #63 |
| B9 | `belt_watchdog` HEALTHY and a heartbeat file for this run exists | belt_watchdog, belt_heartbeat | #59 |

Output: one line per check plus a single verdict `GO` / `NO-GO <ids>`, written to the per-call telemetry run
file so the run report carries it. Build order by score: A4 + B4 (prediction 1, 9), A1 + A2 + B3 (prediction 2), A5 (prediction 7),
A3 (prediction 8), B2.

---

## 6. Gaps in the debugging discipline itself

| # | gap | evidence | proposed change |
|---|---|---|---|
| G1 | **The sanctioned harness is not where the work happens.** Telemetry, run identity, heartbeats and result records live on the live_queue path; recent live work runs through ad-hoc scripts | P-e: newest `_obs` run 2026-10-06; `_kb_call_tmp.py` 133 sessions since 10-07; `live_queue_results.jsonl` last row 2026-10-06 | put telemetry and fingerprinting in `rimbridge_client.py` so every script gets them for free; make "a scratch script" a recorded run too |
| G2 | **Rules in prose do not stop recurrences; tools and hooks do.** | §4.2: background deadlock (brief rule only) recurred on ≥ 5 dates; ModsConfig left on a tier (rule only) 5 dates; the launch gate, `saved_base` and receipts stopped their classes | every lesson that names a recurrence must end in a hook, a gate or a check, or say why it cannot; lessons count (259) far exceeds checks written from them |
| G3 | **The bridge lease does not cover the game's configuration or lifecycle.** | #22, #50, #54, #64; `modcheck run` and `modset_builder --apply` write `ModsConfig.xml` without consulting the lease | make `ModsConfig.xml` writes and game launches/kills lease-checked operations (refuse without the lease), and restore-on-release a declared tier |
| G4 | **Time lost is not recorded**, so classes cannot be ranked by cost | most §4 rows say `unstated`; only the 2026-10-03 bridge log carried minute stamps | lessons template gets `time_lost_min:` and `durable_fix:` fields; `observatory` "recovery minutes" per class (designed §2.3, unbuilt) |
| G5 | **Five overlapping observers with no single timeline** | `belt_watchdog`, `tps_observer`, `health_observer`, `crash_watch.sh`, observatory telemetry, `bridge_sessions.jsonl`, the ledger | one read-only `timeline.py --at <time>` that merges them (TPS reader already does `--health`); retire `crash_watch.sh` |
| G6 | **Numbers in docs rot and are re-quoted** | cold load: 13 (lesson 10-04), ~15 (CLAUDE.md), 18.5–21 (observatory), ~25 (GAME_STATE_WORKFLOW, watchdog budget); log cap 1,000 vs 10,000 | numbers that a tool measures are printed by the tool, never written in prose (the `modlist_swap.py` header already follows this rule) |
| G7 | **Binding design rests on Transient files with a 14-day shelf life** | `map_awareness.md`, `game_health_record.md`, `tps_record.md` cite `Transient/foundry_*_20261010.md` (they say they restate what binds) | keep the restating discipline; add a check that no committed design doc links a Transient path as its only source |
| G8 | **Harness defects dominate early findings, and the harness has no own regression suite run live** | `debug_process.md` §8; `abort_proof.py` exists but the abort path "never fired live" until built | a nightly offline `--mock` run of every suite plus `abort_proof` on the first live session of each day |
| G9 | **"Prior pass now fails" is a STOP rule without an instrument** | P-i | build the diff over the required-checks report (proven verdicts by check id, last vs now) |
| G10 | **Focus doctrine conflicts with an owner ruling** | `focus_heal.py` minimises the blocking window; owner 2026-10-04: never fullscreen/steal focus | `runInBackground` as a preflight requirement (B5) makes focus irrelevant; demote `focus_heal` to a last resort that asks first |
| G11 | **Liveness is still judged from Player.log by habit** | #16, #79 (two false hangs, one killed process) | the watchdog prints `mainBeatUtc` age as the first liveness fact; the runbook leads with it |
| G12 | **Escalation to GPT has no recorded trigger usage** | `debug_process.md` §5 triggers exist; no count of consults per incident found (UNVERIFIED) | the GPT wrapper logs each consult with the item id, so "stuck time before GPT" becomes measurable |
| G13 | **Owner-facing results are not tied to the deploy that produced them** | observatory §2.4: "today no record carries a deploy fingerprint", so every check is at best *pending deploy proof* | finish `run_identity` on every runner (prediction 5/34) — it is the one missing instrument the report itself names |

---

## 7. Open questions for the reviewer

1. Is a **single pre-flight** (§5.3) the right shape, or should its checks live inside each runner's existing
   preflight (`live_queue/preflight.py`, `northstar_driver/preflight.py`) to avoid a third preflight?
2. Should **`ModsConfig.xml` writes and game launch/kill** require the bridge lease (G3)? What breaks if they do
   (the owner's own launches, Steam)?
3. Where should per-call telemetry live: `rimbridge_client.py` (every script) or `rimdrive.Session` (structured
   runs only)? What is the right unit of a "run" for an ad-hoc script?
4. Is the **visitor rule's CLEAN-with-note** acceptable for need/mood/job criteria, or should those components be
   visitor-sensitive by declaration (prediction 10)?
5. For MUST 17, how should `taranchuk.performanceoptimizer` be handled — measured as part of the full list, or
   ablated in an extra configuration to separate its effect on our hooks?
6. Is **`GeneratePawn` hooking** acceptable always-on, given it is the hottest path during world gen and cold
   loads — or should origin-generation arm only after the first map exists?
7. Which **probabilities and costs in §5.2** look wrong to you, and which classes are missing entirely
   (e.g. GPU/driver, Windows Update reboots, antivirus file locks on `LocalLow`)?
8. Is an **allow-list modal detector** (prediction 17) safe, given mods add harmless windows (minimaps, overlays) that
   would then refuse runs?
9. Should **minidumps** (Windows LocalDumps) be enabled for `RimWorldWin64.exe` given disk cost and the owner's
   machine, and who reads them (no symbol server for Unity Mono)?
10. The history shows **prose rules fail to stop recurrences** (G2). Which of the recurring classes in §4.2 can be
    turned into hooks without blocking legitimate work, and which genuinely need judgement?
11. Is the **acceptance ladder** (L0 → GREEN-FULL → L3 → L4) missing a rung for "same artifact, same mod set,
    comparable run" — i.e. should comparability (artifact + suite hash + mod digest + seed) be a precondition of
    GREEN at all?
12. RNG seeds are not pinned anywhere in the harness (§3.8, UNVERIFIED). Is seeding worth doing for RimWorld (Rand
    state is global and touched by every mod), or is "spawn many" the only honest approach?
13. What should **time-to-diagnosis** be measured from — first symptom seen by an agent, first owner report, or first
    recorded evidence — and is it worth a field on every item?
14. Is it right that the **TPS and health recorders never change the watchdog's verdict** ("slow is not hung"), or
    should a SUSTAINED LOW during a suite taint tick-dependent checks?
