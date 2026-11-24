# RIMMANDRAKE_BUILD_VISIT_AND_CYCLE_KITS_SEVENTEEN_COPIES_TODAY

One kit opens a live visit, runs its scenes and writes its rows; one kit runs lane 2 of a blind round.

Filed by `RIMMANDRAKE_TICKET_TEN_AGENT_WORK_TO_CODE_CHANGES_SMALL_ONES_FIRST`. The owner, 2026-11-23, evening PST: *"let's please
ticket each of these as work items fully including what metrics that would answer to (how to know they're written
well and improving), how to measure that they helped vs. the past, what they must do, what they must not do, etc. Then
let's accept the small ones into the build pipeline, while postponing the medium and large items until we learn from
the small ones."*

## Finding

The finding is from the agent-work census of 2026-11-23 (item
`RIMMANDRAKE_FIND_AGENT_WORK_THAT_PYTHON_CAN_DO_TOKEN_FREE`). The week is the 7 days to 2026-11-23, 7:56 PM PST. M is
million weighted tokens (`weighted_v2`: 1 is one uncached Opus 5.5 input token). The whole analysis:
`design/specs/2026-11-23-agent-work-to-code/analysis.md`; the one page: `one_page.md` beside it; the scripts: `census/`
beside it.

- The week cost 1,718.7M in 1,908 transcripts with a priced turn (1,935 parsed) `[measured]`; 731 detached run records,
  1,373.8M `[measured]`. The records and the transcripts are 3% and 5% apart `[measured]`.
- Paperwork turns (land, ledger, stage tools, state reads, game lock, waits, build and deploy) cost 398.5M, 23% of the
  week `[measured by the act rules]`. The ten changes together save about 120M a week, 7% `[guess ~50%]`. The ten pools
  overlap, so their savings do not add up.
- An act rule gives a turn to one act (the first rule that matches), so each pool has an error; an act that shares a
  turn with other work is under-counted `[measured: publish is in 4,022 commands, only 2,312 show PUBLISHED]`. A run is
  put in a role by its item name; about 5% may be in the wrong row `[guess]`.
- Not seen: Codex and GPT tokens, SteveDesktop and the Macs: UNMEASURED. A real saving is UNMEASURED until this is built.
- What a pasted text costs: a packet of 3,000 tokens that stays for 60 turns costs about 9,000 weighted tokens plus a
  first load of about 6,000; one turn that it removes costs 15,000 to 30,000 (the analysis's arithmetic).

The row of the one page:

| rank | what moves to code | saved in a week | build | risk in one line |
|---|---|---|---|---|
| 2 | **Live visits and blind rounds.** One kit opens the game, runs scenes, writes rows. The agent still classes failures and looks. | 22M `[guess ~55%]` | large | A kit can hide a dead scene. It must write "could not look". |

The row of the ranked table:

| rank | candidate | pool `[measured]` | saved in a week `[guess]` | build |
|---|---|---|---|---|
| 2 | A visit kit and a cycle kit | 41.6M driver turns that are setup, waits, records + 9.5M copied cycle scripts and records | ~22M ~55% | large |

The paragraph of the analysis:

> 2. **Visit and cycle kits.** One `visit.py` opens, launches, runs scenes, writes rows and the SUMMARY, makes the sheets.
> One `cycle.py` runs lane 2 over the judge's fault files. The agent then repairs checks, judges looks and classes
> strange rows. 17 of 17 cycle folders hold their own `rerun_offline.py` and `plant_faults.py` `[measured]`; visit
> scripts differ from the last visit by 4 to 26 lines of 40 to 151 `[measured: Pyrelands 5 to 7]`. Risk: a kit that
> hides a death; and the drift between mods (each mod's entry point differs).

The finding that no earlier study named: *"An agent copies last time's scripts and changes the names. Each in-game visit
copies its scripts from the visit before. All 17 blind-test rounds that have these scripts hold their own copies"*
`[measured]`.

Runs that were read:
- In-game driver (28 sessions, 114.1M). Read: Pyrelands visit 6 run 2, FlowWorks visit 8, GimmeSomeSlack visit 3 run 2 (whole timelines).
- In-game fixer, and mod fixes and traces (172 sessions, 256M). Read: HOLD_FLOWWORKS_PIT_PRISONERS (two sessions), TRACE_FLOWWORKS_MOAT_SWIMMERS, TRACE_PYRE_FIREHAWK.
- Blind challenge judge (20 sessions, 31.8M). Read: Pyrelands cycle 5, FlowWorks cycle 4, ExplosiveKnockback cycle 6, Graffiti cycle 2.

More readings `[measured]`:

- The driver's mechanical turns: 1,706 turns, 41.6M (`p5.py`). Getting or keeping the game up: 752 turns, 18.2M. Visit and
  cycle records: 1,446 turns, 34.6M (driver 20.7M, mod fixes 5.4M, fixer at in_game 3.3M, blind judge 3.1M). Copied scripts:
  657 turns, 15.4M (driver 7.7M, blind judge 6.4M). Throwaway scripts of the live and judge roles: 589 turns, 18.0M (mod
  fixes 6.9M, driver 5.7M, fixer 2.2M). Pictures with inline PIL: 516 turns, 12.6M (`p4.py`).
- The driver phases (`drv.py`, 27 runs, 113.8M): before the first scene 46.0M, other 29.6M, records 11.2M, landing 7.2M,
  start 5.5M, waits 4.8M, repair edits 4.2M, tests 3.8M, stage tools 1.6M. The phase rule fails on FlowWorks.
- On 2026-11-23 the repo holds 26 files named `rerun_offline.py` and 26 named `plant_faults.py` under `design/`, past
  versions included `[measured by this filing]`. ExplosiveKnockback cycle 6: 53 and 145 lines. Its `plant_faults.py` holds
  a restore on signals, a build-error rule ("a build error is not a catch"), and a baseline run: the kit must keep these.

**What the Bridge 2 scene library already covers** (`design/specs/2026-11-23-bridge-v2/contracts/README.md`; items
`RIMMANDRAKE_BUILD_SCENE_LIBRARY_TEN_NAMES_FIVE_LAYERS_TODAY`, proposed, and
`RIMMANDRAKE_CONVERT_THREE_SCENES_SHOW_IF_TEN_NAMES_HELP`, blocked on it): what happens **inside one scene**. It states the
claim (`scene.contract`), takes one game and checks its build (`scene.open`), stages, runs to a tick and records, acts, reads,
shoots, judges a kept run into one of seven outcomes, takes over a dead session (`scene.attach`), and runs a script that can
count (`scene.py accept`). Every answer carries a receipt with the build that was loaded.

**What is left for this item:** what happens **around the scenes**. Open a visit (claim, sync, stage, the last visit's
summary, folder skeleton). Choose the checks (`rerun_relation.py` as it is). Bring the game up once for a list of scenes
(lock, tier, deploy, launch, the loaded receipt). Run the list one after another and leave a row for each, the dead ones
included. Write rows and the SUMMARY skeleton. Cut the sheets. Run lane 2 of a blind round over the judge's own faults.
Do not build anything that a name of the scene library does. If the library has landed when this item starts, the kit calls
`scene.py accept` for each scene and reads its outcome, and the fixed sitting kit (`b.py`, `shot.py`, `exp.py`) is
`scene.py explore`, not a thing of ours.

From `In-game driver (28 sessions, 114.1M)`:

| job | in → out | class | the program, and does it exist | load | risk |
|---|---|---|---|---|---|
| Open the visit: claim, sync, stage, last visit's summary, folder skeleton | stage record, last visit → visit folder | M | `visit.py open M`: makes the folder, copies nothing, prints the plan. Not built | part of 41.6M | A new mod has no last visit: the program must say so, not copy another mod's |
| Choose the checks | commit delta → list | M | `rerun_relation.py` exists and is used (348 turns) | UNMEASURED | It errs to "run again" by design |
| Get a game: lock, tier, deploy, launch, readiness | tier → a live game | M | `game_instance.py`, `modset_builder.py`, `deploy_custom_mods.py` exist; nobody calls them as one | 18.2M | The wrong mod list gives a green scene on the wrong build; the loaded receipt must be read back |
| Run scenes one after another | list → rows | M | Each visit copies `runner.sh` and `make_rows.py` from the last visit by `sed` (4 to 26 lines change). `scene_runner.py` exists for C# scenes only | 7.7M copied scripts | A scene that dies must leave a row that says COULD NOT LOOK |
| Wait for scenes | runner log → finished | M | `waitfor.py` exists; each wait is capped by the 10-minute call limit | 6.9M | A hung game looks like a long scene |
| Repair a wrong check, classify a failure | log, code → fix | J | stays | large | A program cannot say if the mod, scene or environment spoiled the run |
| Plant a fault and show red, then green | fault patch, test → two readings | X | `maturation.py red-seen` runs it; the agent writes the patch | 14.0M (all roles) | An equivalent mutant reads green and means nothing |
| Rows, SUMMARY, polish and strange records | component verdicts → JSON and prose | X | `make_rows.py` per visit; a shared one is not built | 20.7M | The strange row's class and the "why" are judgement |
| Crop pictures and contact sheets | screenshots → one picture | M | inline PIL each time; two sheet tools exist for other uses | 3.2M | Which part to crop is judgement; the cut is not |
| Look at pictures | picture → what it shows | J | stays | 3.1M | — |
| Exit: build match, next, advance ask | rows → exit state | M | `build_match.py`, `maturation.py next` exist | in stage tools | Covered by the program already |

From `In-game fixer, and mod fixes and traces (172 sessions, 256M)`:

| job | class | the program, and does it exist | load | risk |
|---|---|---|---|---|
| Set up a sitting (`b.py`, `shot.py`, `exp.py`, `run.sh` written again in each run) | M | `bridge_call` and the `rimbench` scripts exist; a fixed sitting kit is not built | 18.0M of throwaway scripts (all live and judge roles) | An experiment that the kit cannot express; keep the free script |
| Read the failing row and its evidence (`rows.jsonl`, scene JSON) | M | a query command: `visit.py row M CHECK`. Not built | part of 24.7M | Rows of old shapes |

From `Blind challenge judge (20 sessions, 31.8M)`:

| job | class | the program, and does it exist | load | risk |
|---|---|---|---|---|
| Run lane 2: rerun every decider, plant each fault, log red or green | M | `rerun_offline.py` and `plant_faults.py` exist 17 times in 17 cycles, a new copy each time | 6.4M copied scripts | A generated fault that the judge did not choose would weaken blindness; only the runner moves, never the faults |
| Write lane-1 cases and the planted faults | J | stays; a program cannot know a good fault | — | — |
| Census of kernels, settings and rows with inline Python | M | a query command, not built | part of 24.7M | — |
| File the tickets and write SUMMARY | X | template from the fault rows; the hole text stays with the judge | 3.1M records | A program could file a wrong class; the judge names the class |

## spec

### What it must do

- `src/RimMandrake/rimflow/visit_kit.py` opens a visit: it makes the folder, prints the plan and the last visit's summary of
  the same mod, and copies no script.
- It brings one game up through the tools that exist (`game_lock.py run`, `game_instance.py`, `modset_builder.py`,
  `deploy_custom_mods.py`) and reads the loaded build back.
- It runs the chosen scenes in order. Each scene leaves at least one row. A scene that died, hung, could not start, printed
  no row or ran on another build leaves COULD NOT LOOK with the cause.
- It writes `rows.jsonl`, a SUMMARY skeleton with blank lines for the class and the why, and the picture sheets.
- `src/RimMandrake/rimflow/cycle_kit.py` runs lane 2: each decider on the clean tree, then each of the judge's faults, planted
  and reversed, with one row per pair. The tree is as it was after each fault, also after a kill.
- The free script stays: an experiment that the kit cannot express is written by the agent.
- The agent repairs checks, judges looks, classes strange rows and writes the why.

## What it must not do

- It must not take a judgement from an agent. Finding a cause, designing a fix, choosing words, judging a picture,
  choosing a planted fault, naming a hole, classing a failure (MOD, SITE, HARNESS, ENVIRONMENT, COULD NOT LOOK), and
  deciding if a ticket is worth doing stay with agents. Talk with the owner and his five acts stay with him.
- It must not hide a failure. A failed step reads failed, with its cause, where the agent looks first.
- It must keep "could not look", "failed", "zero" and "empty" apart in every return value, line and exit code. A step
  that gave no reading is never an answer.
- It must not tell a launched agent its spend: no token figure, budget, cap or price in a brief, a packet, a note that an
  agent reads, or a tool's output. Text that people wrote goes through `spend_talk.strip`.
- It must not refuse an act for a fault of form that it can repair itself.
- The risk (one page): *"A kit can hide a dead scene. It must write 'could not look'."* The guard: the number of rows
  is at least the number of scenes, and a scene with no row of its own gets COULD NOT LOOK. Exit 0 with no row is never PASS.
- It must never set a class, join two failures, or choose which picture to look at.
- It must write no fault. The judge's faults come in by file; a generated fault would weaken the blindness. Only the runner
  moves.
- It must not copy another mod's folder for a mod with no last visit: it says "no last visit".
- It must not touch the game's focus, the owner's hold or a game that another holder drives. It must never fly a flyer.

## verify

### Acceptance test

```
python3 design/specs/2026-11-23-agent-work-to-code/acceptance/rank2_visit_and_cycle_kits_accept.py
```

Expected today: FAIL. Seen failing on 2026-11-23 on base `9d89f50304`: `FAIL 0/19`, exit 1. Expected on a correct build:
`PASS 19/19`, exit 0. The script's head holds the contract: the module, the functions, the arguments and the return values.
The test was also run against a throwaway stub outside the repo: every check passed except the checks that need the page,
the listed selftest and the wiring, so the contract can be met `[measured]`. Do not edit the script to pass it. If one of
its checks is wrong, repair the check with a planted fault that it catches and a correct build that it passes, and put
both readings on this item. Do not move the script: the outcome check of this item runs it at this path.

It covers: died, hung, missing, wrong build, unreadable build, no row, empty list, a fault that does not apply, a hung decider,
a decider that is red on the clean tree.

Acceptance test of the live part (one real visit through the kit, the game bring-up, the sheets): none offline, because it
needs a running game. It is read on the first visit that uses the kit: the same mod's visit before is the comparison, and
one scene is killed on purpose to see its COULD NOT LOOK row. Until then: UNRUN.

## How we know it is written well

The builder writes the boundary page before any code (`design/RimMandrake/standing_rulings.md` §A boundary page before
pipeline code): ACCEPTS, DOES NOT SURVIVE, PROMISES (each promise has a test of its name), LIMITS (each number names its
danger and its evidence). The selftest goes in `src/RimMandrake/Utils/pipeline_tests.json`, and so does the acceptance
script when it is green. One fresh reader who did not make the change reads the changed pipeline files once.

Page: `design/specs/2026-11-23-visit-and-cycle-kits/boundary.md`. Selftests: `selftest_visit_kit.py`,
`selftest_cycle_kit.py` in `src/RimMandrake/rimflow/`. Planted faults that the tests must catch:

- a scene that exits 0 with no row reads PASS; a hung scene is dropped; a dead scene stops the list;
- the build is read once and not before each scene; an unreadable build counts as a match;
- the fault is left in the tree after a hang or a SIGTERM; a build error counts as a catch;
- a decider that is red on the clean tree counts as a catch;
- a class is written by the kit.

## How we measure that it helped

The baseline below is the week to 2026-11-23, 7:56 PM PST. On 2026-11-23, about 8:30 PM PST, the report commands were run
again over the kept census data and gave the same numbers `[measured]`. The command that made them:

```
cd /mnt/d/ClaudeWork/rimmandrake/scratch/a2c && python3 p5.py; python3 p4.py; python3 drv.py
```

The kept data is `scan3.pkl` (and `scan2.pkl`, `rows.pkl`) in that folder, made once by `runs.py`, `scan.py`, `det.py`,
`scan3.py`. Never write over that folder. The scripts themselves are in the repo (`census/`).

**The census must change before the comparison is possible** `[measured]`: the scripts have no upper time bound, their
output folder is fixed (a second run destroys the baseline), and `scan.py`, `scan3.py` and `outc.py` import from a clone
that is gone (`outc.py` fails today with ModuleNotFoundError). That change, `census/window.py`, is the second part of
`RIMMANDRAKE_FILL_COMMANDS_INTO_BRIEFS_HELP_ASKED_2807_TIMES`. If it has not landed when this item is measured, build
it here first, to the contract in `design/specs/2026-11-23-agent-work-to-code/acceptance/census_window_accept.py`.

The same reading again, 7 days after the change is live (put the time in the close of this item):

```
python3 design/specs/2026-11-23-agent-work-to-code/census/window.py --end <live time + 7 days, ISO> --days 7 \
    --out /mnt/d/ClaudeWork/rimmandrake/scratch/a2c_<date>
```

Read `rates.json`. A week differs from another week in size, so compare turns **per 100 runs** and weighted tokens **per
100 runs**, never the bare weekly sum. The baseline has 1,908 runs. `RIMMANDRAKE_READ_SMALL_ITEM_MEASUREMENTS_THEN_PICK_OF_FIVE` reads these numbers.

- Must fall: the driver's mechanical turns (1,706 turns, 41.6M in 28 driver runs: 1.49M a run) and the copied scripts (657
  turns, 15.4M). Guess: about 22M less a week, of a pool of 51.1M (41.6M and 9.5M) `[guess ~55%]`. Compare weighted tokens
  per driver run and per blind cycle. `window.py` has no key for these two: this item adds `driver_mechanical` and
  `copied_scripts` (the rules of `p5.py` and `p4.py`) to it, with their checks.
- Must not get worse: mod faults that a visit missed and the owner's walk or a later visit found, per visit; and the share
  of rows that read COULD NOT LOOK (a kit that cannot run scenes would raise it). Baselines: UNMEASURED; the builder counts
  both over the visits of the baseline week before the change lands.

## How it keeps improving

- A new `rerun_offline.py`, `plant_faults.py`, `runner.sh` or `make_rows.py` in a visit or cycle folder that was made after
  the kit: an agent copied again, and the folder's SUMMARY says why.
- Free scripts (`cat > x.py <<`) per driver run (`p4.py`): when one shape returns in two visits, the kit lacks it.

## Size and order

Rank 2. Size: large. **This item waits.** Its reason: waits until the small items are built and their 7-day measurement is
read. `RIMMANDRAKE_READ_SMALL_ITEM_MEASUREMENTS_THEN_PICK_OF_FIVE` reads the measurements and decides which waiting item
goes next. The small items are ranks 3, 5, 6, 7 and 10. A builder does not start this item before that decision.

## criteria

- The acceptance test prints PASS 19/19.
- One real visit ran through the kit, with a killed scene that left COULD NOT LOOK, or the live part is recorded UNRUN with its command.
- Nothing of the scene library was built again.
