# Northstar live pass 2026-10-01: time ledger

Owner, 2026-10-01: *"research where the time went so we can make them faster."*

Scope: **pass 2**, 18:33 to 22:03:11 PDT, which is **210 min**. That is the period the queue logs cover. 22:03 to ~22:30 is **UNMEASURED**: no runner output exists for it, and commit `b3b4290c4` (21:59) says the agent stopped mid-situational_rerun. Pass 1 (17:57 to 18:19, 14 suites in about 20 min) is used here only as a comparison.
Read-only research. No bridge calls were made.

**Instruments, cited by tag in the tables below**
- **[Q]** The `=== Jn hh:mm:ss` stamps in `wt_live2/Transient/modcheck/pass2_queue*.out`, plus `started`/`finished` in `live_queue_results*.jsonl` (26 + 23 rows, de-duplicated). These are runner wall clocks. MEASURED.
- **[F]** File mtimes under `D:\Luke\dev\wt_live2\Transient\modcheck\` (summaries, sidecars, sheets). MEASURED, to the second.
- **[T]** The `__t<tick>__` field in sidecar filenames, paired with the file's mtime. These give the tick and wall-clock time at the same moment. MEASURED.
- **[O]** 950 bridge `operation` records (`StartedAtUtc`, `DurationMs`, `ticksGame`) harvested from the evidence JSON of this pass. MEASURED.
- **[P]** `Player.log` / `Player-prev.log` `STARTUP_TIMING` lines. MEASURED.
- **[S]** `Saves\Autosave-*.rws` mtimes and sizes, plus `Config\Prefs.xml`. MEASURED.
- **[N]** Timestamps written in the agent's notes. These are approximate: several were written after the event. Example: the "20:55 BUILT bland_world" note describes work that the queue log places before 20:36:58. Where [N] and [Q] disagree, [Q] wins.

## 1. Timeline (MEASURED [Q][F] unless marked)

| # | wall | min | what | category |
|---|---|---|---|---|
| 1 | 18:33:00–18:40:00 | 7.0 | worktree, /tmp full (~1 min stall [N]), bridge take, MINIMAL swap + 13 deploys + compose | prep / agent |
| 2 | 18:40–18:41 | 0.6 | cold launch (32-mod list): 36.0 s to `bridge-start.total` [P] | launch |
| 3 | 18:41:00–18:47:49 | 6.8 | `modcheck run ResearchRetag --game-up`: the suite runs, then the runner crashes in `emit_verify` (RIMFLOW_SEAT not visible to python.exe), so the **result is lost** | lost run |
| 4 | 18:47:49–18:52:33 | 4.7 | gap [F] | agent |
| 5 | 18:52:33–19:21:36 | 29.0 | FlowWorks, situational. Ran at **36–65 ticks/s** [T][N]. Same seat crash, so the **summary is lost**. Only the html sheet survived | lost run |
| 6 | 19:21:36–19:23:33 | 1.9 | rebase wt_live2, start queue | agent |
| 7 | 19:23:33–19:27:33 | 4.0 | preflight abort_proof bland_tile companion_live motion_frames (abort_proof/bland_tile FAIL, companion_live UNMEASURED) | harness self-test |
| 8 | 19:27:33–19:38:31 | 11.0 | situational_rerun: after 3 suites, FlowWorks dies on `unexpected response id`, and so does every later suite | lost run |
| 9 | 19:38:31–19:39:41 | 1.2 | gap | agent |
| 10 | 19:39:41–19:42:45 | 3.1 | bland_tile companion_live abort_proof again (settlement exists, modal_open) | harness self-test |
| 11 | 19:42:45–19:44:48 | 2.1 | situational_rerun started, then killed (modal_open would abort every chain) | lost run |
| 12 | 19:44:48–19:46:59 | 2.2 | bland_tile companion_live abort_proof again | harness self-test |
| 13 | 19:46:59–19:49:43 | 2.7 | situational_rerun started, then killed | lost run |
| 14 | 19:49:43–19:53:45 | 4.0 | bland_tile companion_live PASS, abort_proof FAIL (modal reopens) | harness self-test |
| 15 | 19:53:45–19:58:15 | 4.5 | situational_rerun started, then killed; agent fixes | lost run |
| 16 | 19:58:15–20:01:05 | 2.8 | abort_proof PASS 10/10 | harness self-test |
| 17 | 20:01:05–20:08:58 | 7.9 | situational_rerun dies on `unexpected response id` again | lost run |
| 18 | 20:08:58–20:14:30 | 5.5 | game relaunch (38.3 s to bridge-start [P]), then 2× preflight/situational_rerun UNMEASURED "could not bring RimWorld forward" (20:11:48, 20:12:53) | relaunch + focus |
| 19 | 20:14:30–20:30:51 | **16.4** | **preflight + situational_rerun MEASURED PASS: all 13 suites on a fresh 1-map game** | productive |
| 20 | 20:30:51–20:36:58 | 6.1 | agent builds `bland_world.py` | agent |
| 21 | 20:36:58–20:37:59 | 1.0 | abort_proof with reset proof | harness self-test |
| 22 | 20:37:59–21:03:27 | 25.5 | situational_rerun `--bland-world` #1: suites run, but the setup gate FAILs (hostile insects on map 1) | gated-out run |
| 23 | 21:03:27–21:03:57 | 0.5 | gap | agent |
| 24 | 21:03:57–22:03:11 | **59.2** | situational_rerun `--bland-world` #2 on map 2 (3 maps alive): the setup gate FAILs (Stab), and 7 suites end UNMEASURED or not bland | gated-out run |
| 25 | 22:03–22:30 | ~27 | **UNMEASURED** (no runner output) | — |

## 2. Ledger by category (210 min, 18:33–22:03)

| category | min | share | basis |
|---|---|---|---|
| Runs that FAILed their own bland-world setup gate (situational_rerun bw #1, #2) | 84.7 | 40% | MEASURED [Q] |
| ↳ of which slowdown versus the clean pass (59.2 − 16.4 for the same 13 suites) | 42.8 | 20% | MEASURED [Q]; cause UNMEASURED (§3) |
| Runs lost or voided by harness defects (rows 3, 5, 8, 11, 13, 15, 17) | 64.0 | 30% | MEASURED [Q][F] |
| ↳ rimflow seat crash in `emit_verify` (rows 3, 5) | 35.8 | 17% | MEASURED |
| ↳ `unexpected response id`: late reply of a timed-out step (rows 8, 17) | 18.9 | 9% | MEASURED |
| ↳ colony-naming dialog → modal_open: situational_rerun runs killed (rows 11, 13, 15) | 9.3 | 4% | MEASURED |
| Agent gaps: prep, fixing and building between jobs (rows 1, 4, 6, 9, 20, 23) | 21.4 | 10% | MEASURED [Q][F]; row 1 start from [N] |
| Harness self-test jobs preflight/abort_proof/bland_tile/companion_live/motion_frames, including 5 fail-and-rerun rounds | 17.1 | 8% | MEASURED [Q] |
| Clean, productive full-suite run (row 19) | 16.4 | 8% | MEASURED [Q] |
| Relaunch + focus failures (row 18) | 5.5 | 3% | MEASURED [Q][P] |
| ↳ of which the cold launch itself | 0.6 | 0.3% | MEASURED [P] |
| World / map setup: bland_tile ×4 (≈0.8 min each) + bland_world setup (≤13 s per situational_rerun bw, first op 21:04:10 after start 21:03:57 [O]) | ≈3.5 | 2% | MEASURED; already counted inside the self-test and situational_rerun bw rows |

**Cold launches are not the problem.** Pass 2 had two launches (18:40 and ~20:09), and each took **36–38 s** to bridge-start on the 32-mod list [P]. Pass 1 recorded "game up (35s)", and the companion proof launched at 18:25 and was up by 18:26 [N]. All four launches that day together came to about **2.5 min**.

**What one clean pass actually costs: 16.4 min** for all 13 suites on a fresh game (row 19). Every other minute went to harness defects, to setup gates, or to a throughput collapse.

## 3. Throughput: ticks simulated vs wall time

Ticks simulated in pass 2, MEASURED [T][O]:
- Game 1 (18:40–~20:07): tick 1 → ≥323,100.
- Game 2 (~20:09–22:03): tick 501 → ≥652,200.
- Total: about **975,000 ticks in 210 min**, which averages **~77 ticks/s** of wall time.

At the clean-pass rate below, the same ticks would take about 39 min.

Measured rates [T][O], by segment:

| segment | ticks/s | context |
|---|---|---|
| 20:14:49→20:17:03 (situational_rerun PASS, Aftermath→Antiquities) | **416** | fresh game, 1 map, game focused (right after the Alt-tap focus fix) |
| 20:17:52→20:22:59 (situational_rerun PASS, Droidworks→FlowWorks) | 109–307 | same |
| 20:45→20:56 (situational_rerun bw #1, Droidworks/FlowWorks) | 114–217 | 2 maps |
| **21:04:10→21:35:42 (situational_rerun bw #2, Antiquities chain)** | **50** | 3 maps. 95,000 ticks in 1,892 s, 166 sweeps, **11.6 s per 600-tick chunk** |
| 21:41→21:46 (situational_rerun bw #2, FlowWorks excavation) | 33 | 799 `flow-works-excavation-report` polls [O] |
| 18:52→19:15 (first FlowWorks run) | 36–65 | 1 map, before the focus fix; the "~57 ticks/s" note |

- **Settings, MEASURED [S]:** `runInBackground True`, `devMode True`, `autosaveIntervalDays 0.25`, `pauseOnLoad True`.
- **Speed setting:** `step_game_ticks` advances the clock without unpausing (skill `rimbridge`), so the in-game speed setting is not obviously the limiter. Its actual tick loop is in RimBridgeServer, not in our source: **UNMEASURED**.
- **The ~50 ticks/s collapse has two candidate causes, and they are not yet separated (UNMEASURED):**
  - (a) Every bland-world setup generates a new map and never removes the old ones. Map 0 (quicktest), map 1 (tile 254) and map 2 (tile 255) all keep simulating. The rate fell 416 → ~150 → 50 as maps went 1 → 2 → 3. Autosaves grew to **~11 MB** [S].
  - (b) Window focus. The harness grabs focus once per job process, and the owner was working in Chrome (note, 20:30). The two slow regimes (18:52 FlowWorks at ~57 ticks/s on one map, and 21:04 at 50 ticks/s) both fall outside a fresh focus grab, while the fastest segment came right after one.
  - Pure CPU cost per tick does not explain it: the same Antiquities chain ran at 416 ticks/s at 20:15.
- **Per-sweep overhead.**
  - **Median bridge call: 48 ms.** MEASURED across 950 operations [O]. The figure is suspiciously close to one frame, which points to calls being serviced once per frame.
  - **What a sweep makes:** every 600-tick chunk, `watch._on_chunk` runs one full snapshot of 13 calls (`snapshot.take_snapshot` tier `full` + companion). It also runs the food feed, which makes 1 + (1–2 per colonist) `pawn_need` calls. That comes to roughly **17–20 calls per chunk**, about **0.8–1.0 s per 600 ticks**.
  - **Effect at full speed:** at 416 ticks/s the step itself takes about 1.4 s per chunk, so the sweeps add roughly 40–70% on top. This is ESTIMATED from the measured call median, not timed per chunk.
  - **In situational_rerun bw #2:** 166 + 253 + 18 + 19 + 5 = 461 sweeps, so about **6–8 min of pure sweep calls**. ESTIMATED.
- **Autosave:**
  - Interval: every 0.25 day, i.e. every 15,000 ticks, so about **65 autosaves** over the pass. ESTIMATED as 975k / 15k.
  - Size and spacing: ~11 MB each by the end; 10 autosaves landed between 21:30 and 22:01 [S].
  - Cost per save: **UNMEASURED**, since Player.log logs no save timing. A guess of 1–3 s each gives 1–3 min in total.
- **Tick cost by suite (situational_rerun bw #2, MEASURED summary `ticks_spent` + mtime [F]):**
  - Antiquities: 95,600 ticks, 32.1 min.
  - FlowWorks: 112,921 ticks, 21.4 min.
  - These two are **94% of the ticks and 91% of the wall time** of a full situational_rerun run.
  - The other 11 suites together: ~12,300 ticks, under 6 min. Inhabited, PawnFlavor, ResearchRetag, StarWarsRaces and StructureInjections spend 0 ticks and finish in 5–12 s each.

## 4. Per-suite wall time and wait budget

Columns:
- **literal wait ticks:** sum of the integer literals and module constants passed to `wait_ticks`/`wait`, plus `waitTicks=`/`ticks=` keywords, found by AST over each `validation.py`.
- **measured:** `ticks_spent` and `sweeps` summed from `live_queue\situational_rerun\<Mod>_summary.json` (situational_rerun bw #2).
- **wall:** the gap between consecutive summary mtimes [F].

| suite | literal wait ticks | non-literal waits | ticks_spent | sweeps | wall (situational_rerun bw #2) |
|---|---|---|---|---|---|
| Aftermath | 500 | 0 | 0 | 1 | 0:20 |
| **Antiquities** | 780 + `READ_WAIT_TICKS` chunks (95,000) | 1 | **95,600** | 166 | **32:05** |
| Droidworks | 4,880 | 0 | 2,880 | 19 | 3:14 |
| **FlowWorks** | 0 (all waits come from plot parameters) | 2 | **112,921** | 253 | **21:24** |
| Inhabited | 0 | 0 | 0 | 2 | 0:06 |
| JawaIonWeapons | 0 | 0 | 0 | 5 | 0:12 |
| Ninefold | 43,600 | 0 | 9,399 (aborted early) | 18 | 0:54 |
| PawnFlavor | 0 | 0 | 0 | 0 | 0:07 |
| Pyrelands | 1,020 | 2 | 0 | 0 | 0:34 |
| ResearchRetag | 0 | 0 | 0 | 0 | 0:03 |
| ShipMemory | 1,000 | 0 | 0 | 0 | 0:05 |
| StarWarsRaces | 0 | 0 | 0 | 0 | 0:05 |
| StructureInjections | 0 | 0 | 0 | 0 | 0:05 |

Single longest waits:
1. **Antiquities `reading_completes_and_advances_research`: 95,000 ticks.**
   - Sized for the worst case: skill 0, skillFactor 1.5, which gives 90,000 ticks plus a buffer. The suite's own docstring says a higher-skill colonist finishes early and the rest of the wait is idle.
   - Every run pays the full worst case, because the wait is a fixed count rather than a wait-until.
2. **FlowWorks plots: 112,921 ticks in total**, spread across about 20 toggles of settle waits plus the excavation drive loop (799 report polls at about 33 ticks/s).
3. **Ninefold: 43,600 literal ticks.** It aborted at 9,399 in this run, so its true cost is UNMEASURED and could be about 4× higher once it stops aborting.

## 5. Ranked fix list

| rank | fix | addresses | saving per full pass | basis |
|---|---|---|---|---|
| 1 | **Never lose a run to a post-step crash.** Write `<Mod>_summary.json` *before* `emit_verify`, and make `emit_verify` non-fatal (warn, keep the result). Also keep the late-reply drop, the naming-dialog ignore and the focus fallback; all three are already fixed in wt_live2 and need to stay. | 64 min of lost or voided runs | **~64 min** (≈54 min already banked by the fixes; the seat-crash fix is 36 min of it) | MEASURED loss |
| 2 | **One bland map, not one per run.** `bland_world.setup` should remove earlier generated maps (or reuse the tile-254 map and only `reset()` it). Better still, relaunch between full runs: a launch costs 36–38 s [P] and buys a 1-map, 416-ticks/s game. Run the 3-minute A/B probe first (§6) to tell maps from focus. | the 416 → 50 ticks/s collapse; situational_rerun bw #2 took 59.2 min vs 16.4 clean | **~40 min** per full situational_rerun | MEASURED delta, cause UNMEASURED |
| 3 | **Re-assert focus per chunk, not per job.** In `watch._on_chunk`, re-check the foreground window cheaply and re-run `game_focus.focus_game()` only if RimWorld lost it. Then **rate-gate inside the runner**: if measured ticks/s over the last 5 chunks drops below 150, log `THROUGHPUT_DEGRADED` with map count and foreground window, so the next ledger is measured, not inferred. | candidate (b) for the collapse; it was invisible this time | part of rank 2's 40 min, plus diagnosability | hypothesis |
| 4 | **Antiquities: wait-until instead of wait-for-worst-case.** Poll research progress or the `Catalogued` inspect string each chunk and stop when done. Also set the reader's Intellectual skill high in setup, so the job needs the minimum ticks. | 95,000 fixed idle ticks: 32 min at 50 ticks/s, ~4 min at 416 | **3–28 min** depending on the rate regime (ESTIMATED: skill-20 reading is well under the skill-0 90,000 ticks) | MEASURED cost, saving ESTIMATED |
| 5 | **Cheaper sweeps on idle waits.** Use the `tripwire` tier (4 calls) per chunk and escalate to `full` + companion only on a tripwire hit. Raise the chunk from 600 to 2,000–2,500 for waits with no declared hazard. Run `feed_colonists` every 5th chunk, not every chunk. | ~17–20 calls × 48 ms per 600 ticks; 461 sweeps in situational_rerun bw #2 | **~5–7 min** per full situational_rerun | ESTIMATED from the MEASURED call median |
| 6 | **Don't rerun the self-tests after every fix.** preflight/abort_proof–motion_frames are harness proofs. Cache a PASS keyed on the hash of `modcheck/*.py` + `live_queue/*.py`, and rerun only the job whose code changed. Batch fixes, then relaunch once, instead of four queue relaunches in 35 min (19:23–19:58). | 17.1 min of self-test jobs, ~10 min of them reruns | **~10 min** | MEASURED |
| 7 | **Skip suites whose result is cached by source hash.** Key: hash(mod `validation.py` + deployed mod files + harness). Only Antiquities and FlowWorks are worth it. The other 11 cost under 6 min together. | the cost of unchanged suites | 0–50 min, only when FlowWorks/Antiquities are unchanged | MEASURED per-suite costs |
| 8 | **Turn off autosave for harness runs.** Set `autosaveIntervalDays` very high through `prefs-tool` at preflight and restore it after. Autosaves are ~11 MB every 15k ticks, ~65 per pass. | autosave stalls | **1–3 min** (UNMEASURED per-save cost) | ESTIMATED |
| 9 | **One prep script.** Worktree + swap + deploy + compose + launch + bridge take as one command (`prep_wsl.py` is most of it). Also keep worktrees off `/tmp`: it filled twice that day. | 7 min prep, 4.7 + 1.9 min gaps | **~8 min** | MEASURED [N][F] |
| — | Not worth doing: faster cold launch (0.6 min each), parallel suites (one bridge, one socket: the side-connection calls are what mixed replies), world setup (≤13 s on the bland_world path). | — | ~0 | MEASURED |

**Net, after fixes 1–6:**
- A full 13-suite pass should run in about **15–20 min of game time plus ~5 min of prep**, against the 210 min this pass took.
- Its floor is the clean row-19 run (16.4 min), made shorter again by fixes 4 and 5.
- **Caveat:** in row 19 Antiquities aborted at 56,400 ticks (starvation) rather than running all 95,000. A non-aborting full Antiquities at 416 ticks/s adds about 1.5 min, so the floor is about **18 min**.

## 6. Instruments and gaps

- **The A/B probe that settles rank 2 vs rank 3: ~3 min.** On a fresh game, time `step_game_ticks` over 6,000 ticks in four cases: 1 map focused, 1 map with Chrome in front, 3 maps focused, 3 maps unfocused. Read `ticksGame` and wall time per chunk. Until that runs, the cause of the collapse stays **UNMEASURED**.
- **Per-call and per-sweep timing is not recorded.** The runner should log one line per chunk with `wall_ms_step`, `wall_ms_sweep`, `ticks`, `maps` and `foreground` to `Transient/modcheck/<run>_timing.jsonl`. With that, this ledger becomes a script rather than an archaeology pass.
- **Player.log has no wall-clock stamps**, only `STARTUP_TIMING` elapsed times. Launch wall times come from [Q]/[N] and the `Player-prev.log` mtime (20:07:01, the last write of game 1).
- **Not covered:** 22:03–22:30, and pass 1 (except as a comparison).
