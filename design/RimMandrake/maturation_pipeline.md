# The Maturation Pipeline, as built

The operating doc: what the pipeline is today, read from its code and tools on 2026-11-15. The design and Mandrake's
words are in the spec, `design/specs/2026-11-13-maturation-pipeline.md`; the build plan is
`design/plans/2026-11-14-maturation-pipeline-build.md`. Where this doc and the code disagree, the code is right and this
doc is wrong: fix this doc. Where the spec and the code disagree, this doc says what the code does and lists the
disagreement in section 9.

## 1. What it is for, and what it replaced

The Maturation Pipeline takes one mod, at one Design Version, from an argued design to Mandrake's own pass. The unit is
the whole mod at one version, not a ticket. Tickets stay in RimFlow, the ledger (`src/RimMandrake/rimflow/cli.py`); the
pipeline is not RimFlow.

It replaced three loops, retired on 2026-11-13 (`design/RimMandrake/retired_loops_2026-11-13.md`):

- **Relentless** (the deleted `src/RimMandrake/rimflow/relentless.py`): ticket-by-ticket build and judge.
- **Artisan** (retired): art making and judging.
- **Whittle** (retired): small-fix grinding.

They stay off. The pipeline does not start them.

## 2. Words used here

- **Mod**: one RimMandrake mod, for example Explosive Knockback.
- **Design Version**: the numbered design a mod is being built towards, `MAJOR.MINOR.PATCH`, for example 0.1.0 (owner
  ruling 2026-11-13, `design/RimMandrake/standing_rulings.md`, "Mod Design Versions use Semantic Versioning").
- **Bar**: one plain sentence that must be true for a version to pass: an acceptance criterion.
- **Check**: the code that decides a bar. A bar may have several checks; each is a **decider**.
- **Lock**: Mandrake's word that a version's bars are settled. After it, a bar changes only as the lock rule allows
  (section 5).
- **Stage**: one step of the pipeline. The program's names are `intake`, `designer`, `preflight`, `offline_build`,
  `blind_challenge`, `in_game`, `pre_human`, `his_walk`, `passed`.
- **Stage record**: the file that says which stage a mod version is at, `design/concepts/<Mod>/version/stage_record.json`.
  Only `maturation.py` writes it.
- **Advance**: moving a mod from one stage to another with `maturation.py advance`. Only the Conductor runs it.
- **Exit test**: a condition `maturation.py` checks before it allows an advance.
- **Hand step**: an exit condition no program checks; a person (the steward) confirms it in words.
- **Steward**: the Conductor, acting as the one who keeps a mod's journal and confirms hand steps.
- **Blind judge**: a fresh agent that did not build the mod and is not told what any earlier judge found.
- **Cycle**: one blind judge's run on a mod at the blind challenge.
- **Visit**: one stay at a stage; a mod sent back and returning makes a new visit.
- **Problem**: a defect, or something a player would reject as strange or disappointing. It must be fixed in this version.
- **Polish**: an improvement the version passes without. It goes to the mod's Polish list; the Conductor decides each move and tells him after.
- **Convergent** change: brings the mod closer to its written vision. **Divergent** change: extends or shifts the vision;
  it goes to the next Design Version.
- **Refusal record**: a refusal in the shape `refusal_contract.py check` accepts: what was observed, what would pass,
  the smallest fix.
- **Detached run**: an agent run in its own systemd unit, started by `src/RimMandrake/rimflow/detached_helper.py`, with a
  dollar cap and no wall-time limit.

## 3. The stages at a glance

Forward moves go one stage at a time. Backward moves go only along these roads (`maturation.py`, `ROADS_BACK`):

| from | may go back to |
|---|---|
| preflight | designer |
| blind_challenge | blind_challenge (one more cycle) |
| in_game | offline_build, blind_challenge |
| his_walk | offline_build, blind_challenge, in_game |

`pre_human` has no road back (his ruling of 2026-11-17, item `RIMMANDRAKE_FOLD_STAGE_SEVEN_INTO_WALK_BRIEF_NO_VETO`:
Stage 7 judges nothing).

A fourth blind cycle in one visit is refused without `--conductor-decision` (`CYCLE_LIMIT` = 3).
Any move is refused while a `kind hold` line in the mod's journal has no later `kind release`, and while the stage
record's version is not the version in `version/VERSION.json`.

| # | stage (program name) | who runs it | launched by | gate the program checks to leave it |
|---|---|---|---|---|
| - | Intake (`intake`) | nobody yet | nobody | some mod's record has reached `his_walk`, and `--owner-said` |
| 1 | Designer (`designer`) | the Designer role, with Mandrake | the Conductor, by hand | `VERSION.json` state starts with `locked` |
| 2 | Preflight (`preflight`) | a Python script, no model | by hand | `version/preflight.json` exists for this version; if it is not a pass, `--steward-confirms` |
| 3 | Offline build (`offline_build`) | builder agents | Dispatch, automatically | every bar in `version/test_table.json` has `every_decider_runnable_today` true, and the table is for this version |
| 4+5 | Blind challenge, tests first (`blind_challenge`) | one blind judge per cycle | Dispatch (one cycle per visit) or by hand | `--steward-confirms` (any non-empty text) |
| 6 | In-game acceptance (`in_game`) | one live-game driver | Dispatch, one run per owed visit (`ingame_enabled` true since 2026-11-15) | `--steward-confirms` (any non-empty text), and the build match: every check's last row made on the build he walks (`build_match.py`) |
| 7 | Walk brief (`pre_human`) | one fresh reader, no veto (`roles/walk_brief.md`) | Dispatch's steward line | `version/walk_brief/arrival_<N>.md` written, its four headings filled, its `written_by` a unit that made no move and no in-game row of this version |
| 8 | His walk (`his_walk`) | Mandrake | him | `--owner-said` |

Model tiers for every role are in `infrastructure/agents/Agent_Policy.md`; this doc does not restate them.

## 4. Each stage

### The spine: four commands

All in `src/RimMandrake/rimflow/maturation.py`:

- `maturation.py show <Mod>`: the stage record.
- `maturation.py next <Mod> [--json]`: reads the record and the mod's files, runs the current stage's exit tests, reads
  any judge or driver record as evidence, names the hand steps, and ends with one `NEXT` line. Writes nothing.
- `maturation.py advance <Mod> --to <stage> --by <seat> --why "..." [--steward-confirms "..."]
  [--conductor-decision "..."] [--owner-said "..."]`: moves the mod, or refuses with a refusal record (exit 1;
  a malformed refusal exits 3). A good move writes the record and one journal entry with a new "Stage now" line.
- `maturation.py spend <Mod> --stage <stage> ...`: adds a spend row (tokens, dollars, wall time, source).
- Also `seed` (build a record from a mod's journal and files), `brief` (write a stage's brief from the mod's files) and
  `launch <Mod> --budget-usd <cap> --item <ID> [--model] [--seat]` (start a detached run on the brief; a cap is
  required, there is no default).

### Intake

- **Input**: an idea for a mod. Today one mod waits here: Pyrelands Mechanics (the Deep Desert Tribes), which by his card
  of 2026-11-13 starts only after the Pyrelands biome passes.
- **Gate**: `advance --to designer` is refused (`intake_closed`) while no mod's record has reached `his_walk`. After
  that it needs `--owner-said`: how waiting mods enter is his question again at that point.

### Stage 1: Designer

- **Who**: the Designer role (`src/RimMandrake/rimflow/roles/designer.md` and the `designer_*.md` files beside it),
  talking with Mandrake. It is launched by hand: `role_launch.py run-now --role Designer --concept design/concepts/<Mod>`.
  Its schedule row in `dispatcher_schedule.json` is `enabled: false`, so it never runs on a timer. Each run is capped at
  `run_budget_usd` 8.
- **Inner steps**, held by `src/RimMandrake/rimflow/designer_stage.py` in `design/concepts/<Mod>/stage.json`:
  0 Read, 1 Argue the idea, 2 Argue the edge, 3 Write, 4 Exam, 5 Lock. Only steps 1 and 2 send him questions. Each run
  writes `result.json`; only `designer_stage.py close` reads it and advances. A run's whole task has a weighted-token
  budget, `DEFAULT_CAP` 4,000,000 (advisory).
- **What each inner step must show before it is accepted** (`designer_stage.result_errors`):
  - Step 0: an inventory in `record.json` accounting for every built thing the program finds, and three ways the mod
    could fail him.
  - Step 1: a root (the core of the design) his words approve.
  - Step 2: every owner word that reopened the concept is cited; no question to him still unanswered; no core
    contradiction unresolved. Silence never advances.
  - Step 3: `concept_tree.py lint` passes on `sheet.md`, `tree.json` and `floor.json`; `scenes.json` meets the scene
    contract; the showcase set covers every capability.
  - Step 4, the Cold Reader exam (`exam.json`): at least 10 frozen scenarios, each distinct and sourced on a leaf or his
    OWNER event, some written by a named fresh Challenger, scored at least 90% right, by two named
    fresh Readers who are not the tree's author, examiner, challenger or a Designer run; zero "accepts where the core
    rejects"; and a control Reader, given the copy the program made with one core leaf removed (`designer_stage.py
    exam-control`, checked to hold the tree's other leaves and name the removed one nowhere), must miss a scenario
    sourced on that leaf. Mandrake may waive the exam in his
    words (`exam_waived`).
  - Step 5, Lock: `concept_tree.py gate` passes: lint, the root VALIDATED at its hash, and a valid coverage signature.
- **The coverage judge** (`src/RimMandrake/rimflow/coverage_judge.py`): before every Designer run at step 5, the role
  launcher runs `coverage_judge.py run <dir>`. A fresh Opus run that did not make the tree reads the tree, sheet and
  scenes and answers `covered` or `not_covered` with a list of gaps, into `coverage_verdict.json`. `covered` with no gaps
  and an unchanged tree signs the tree (`concept_tree.py sign`: a stamp in `tree.json` plus a ledger note). Each judge
  run is capped at USD 8. The third `not_covered`, a fourth run, or judge spend past its limit stops judging and raises
  `REFUSAL_NOTHING_COULD_EVER_PASS`.
- **Calibration**: `refusal_contract.py` keeps a registry of judge briefs, `infrastructure/state/judge_calibration.json`.
  An edited brief resets to `UNTESTED`. Only a `CALIBRATED` brief's verdict has a consequence, either way: its refusal
  sends the Designer back and its `covered` signs; under an `UNTESTED` brief both are stored and shown, nothing is signed,
  and an advisory refusal raises no repair and no alarm. A brief is `CALIBRATED` only when a check on its current hash
  shows every planted case ran and came out as planted, good and bad both (`refusal_contract.judge_cases`); the coverage
  judge's planted cases are `coverage_calibration.py`, run by `refusal_contract.py calibrate --model coverage_judge`
  (it spends). `calibrate --no-run` is a read-only status; it flags signatures made under an unproven brief, never
  voiding them.
- **Artifacts**: the concept folder (section 7) and, at the lock, the version folder: `vision.md`, `bars.md`,
  `VERSION.json` (state, version, who locked it, when, his words, token spend), `polish.md`, `next_version/`.
- **Gate to leave**: `VERSION.json` state starts with `locked` and its version is the record's. `VERSION.json` is
  written by hand on his word. The program does not check that `stage.json` reached step 5 or that the coverage gate
  passes (Pyrelands is locked while its `stage.json` reads blocked at step 5; see section 9).

### Stage 2: Preflight

- **Who**: a Python script, no model, no tokens. There is no common preflight program: each mod has its own throwaway
  script (`design/concepts/<Mod>/version/preflight*.py` or `version/advance_scripts/`), named in its `preflight.json`.
- **Artifact**: `version/preflight.json`: the version, a verdict, and the refusals.
- **Gate**: `preflight.json` exists and its version is the record's. If its verdict is not `pass`, `--steward-confirms`
  must say why the refusals left are build work and not a spec fault. The program cannot tell the two apart.
- **Refusal**: back to the Designer for the refused lines only.

### Stage 3: Offline build

- **Who**: capped Opus builders, launched automatically by Dispatch (section 8) through `maturation.py launch`.
- **Input**: the brief `maturation.py brief <Mod>` writes from the mod's own files: the refused exit tests, the bars not
  runnable and which decider does not run, the in-game checks still UNRUN, the journal's "Waiting on" and "Next" lines,
  and the Conductor's decisions from `version/steward_decisions.md` when he has written one (a blank one is a standing
  default, never a refusal).
- **Artifact**: code, defs, tests, and the test table `version/test_table.json` (with `test_table.md`): per bar, its
  deciders, the stage each proves at, and whether each runs today. The table is written by a per-mod throwaway script
  (`make_test_table.py`), not a common program.
- **Gate**: every bar's `every_decider_runnable_today` is true and the table is for this version. A bar partly decided by
  his Stage 8 look needs `--steward-confirms` that its other checks run.
- **Shown, not enforced**: whether every offline check passes, and the builder's list of what it could not test.
- **Refusal**: Dispatch launches the next builder only if the count of refused bars fell (section 8).

### Stages 4 and 5: Blind challenge, tests first

One stage, by his card of 2026-11-13 ("One stage, tests first").

- **Who**: one blind judge per cycle (Opus; `JUDGE_MODELS` allows opus or fable). Dispatch launches at most three cycles per visit
  (`blind_auto_cycles_per_visit` 3 since 2026-11-15, cap `blind_cap_tokens`, now 50,000,000 weighted tokens), each under an item named
  `RIMMANDRAKE_JUDGE_<MOD>_BLIND_CYCLE_<N>_TESTS_FIRST`; any further cycle is the Conductor's.
- **Input**: the brief `maturation.py brief <Mod>` writes. It lists what is closed to the judge until its lane 1 is
  committed (the journal, `exam.json`, `version/evidence/`, the test table, the mod's selftests and validation scripts,
  builder reports, ledger notes, the steward's section). The closing is an instruction in the brief; no program stops
  the judge from reading those files.
- **Order**: lane 1 first: the judge writes and runs its own game-logic tests from the bars alone. Then lane 2: it opens
  the code and the builder's tests for review, planted faults (deliberate bugs, to see whether a test catches them) and
  reruns.
- **The judge may**: fix the mod's code, each fix shown failing first (red) then passing (green). **It may not**: edit a
  bar, the locked tree or a test's assertions, change which stage a check proves at, or run `advance`. A criterion it
  thinks wrong goes in a `NOTED_FOR_CONDUCTOR` line.
- **Artifact**: `version/blind_challenge/cycle_<N>/` (layout: `design/concepts/ExplosiveKnockback/version/blind_challenge/FORMAT_NOTES.md`):
  `SUMMARY.md` with an Exit block (`offline_bars`, `problems_open`, `exit_met`), `lane2/reruns.jsonl` (and
  `reruns_after_fix.jsonl`), `faults.json`, `fixes.jsonl`, `tests_edited.json`, `planted_results.jsonl`, and lane 1 rows.
- **What `next` reads** (`maturation.read_exit`): "exit met" needs the Exit block plus: every offline bar's deciders PASS
  on rerun; every fault classed Problem or Polish; every Problem FIXED, each with a `fixes.jsonl` row red then green and no
  placeholder command; lane 1 FAIL rows cleared after the fix or named by a Polish fault; `tests_edited.json` present;
  the planted-fault results ending with the tree clean. All of these are files the judge (or a later fixer) wrote.
- **Gate to leave**: only a non-empty `--steward-confirms`. `next`'s reading is evidence for the Conductor; `advance`
  does not require it to say "met".
- **After an ended cycle**: one "Needs Conductor" line. The program never opens the next cycle or advances.

### Stage 6: In-game acceptance

- **Who**: one live-game driver (Opus, cap `ingame_cap_tokens`, now 75,000,000 weighted tokens) on Archmagi through the bridge.
  Only one in-game run per game at a time, and only when `rimflow bridge idle` says that game's bridge can be taken.
  `ingame_enabled` in `maturation_dispatch.json` shipped false (the Conductor ran the first visit by hand with
  `maturation.py launch`, which refuses a held bridge); the Conductor set it true on 2026-11-15 about 13:30 UTC after
  Pyrelands visit 1 (cap 20 -> 30 to match the hand launches; that visit spent about USD 18). From then on Dispatch
  launches at most `ingame_auto_runs_per_visit` (1) run per owed visit. A flyer's flight is never tested live
  without him.
- **SteveDesktop**: its test queue runs modcheck chains: the `testq` block of a stage-6 `test_table.json` entry names a
  check's chain. `src/RimMandrake/Utils/testq/pipeline_admit.py` refuses a mod on his hold, and every mod job while the
  host work switch (`src/RimMandrake/rimflow/host_work_switch.py`, his order of 2026-11-24) puts SteveDesktop on
  pipeline work only; testq's `fill.stop` stops the visit feed. The tick line and the driver's brief name whichever
  stands (`maturation.steve_mod_off`).
- **Artifact**: `version/in_game/visit_<N>/`: `rows.jsonl`, `strange.jsonl`, a savegame, `SUMMARY.md` with an Exit
  block (`ingame_rows`, `strange_open`, `savegame`, `exit_met`).
- **What `next` reads** (`maturation.read_ingame_exit`): each stage-6 check of the table has a PASS row with
  `site_checked` true, a game (`archmagi` or `stevedesktop`) and a `mod_sha`; every strange thing explained or filed; the
  savegame file exists; and the **build match** (his ruling of 2026-11-17): `src/RimMandrake/rimflow/build_match.py`
  compares each check's last row (its `mod_hash`, `game_build` and `active_mods`, from `build_match.py identity --mod
  <Mod> --tier <T>` or `--full`) with the build he walks (the deployed folder hash, `Version.txt` and the labelled walk
  savegame's mod list, read on Archmagi). A row on another build does not count: the exit names it "re-run it".
  `build_match.py check --mod <Mod> [--visit N]` reads that part alone. Selftest: `selftest_build_match.py`.
- **Gate to leave**: a non-empty `--steward-confirms` and the `build_match` clause.

### Stage 7: Walk brief (the pre-human check)

His ruling of 2026-11-17: Stage 7 judges nothing; one fresh read writes his walk brief and has no veto (a finding goes
into the brief or onto a ticket). Role: `src/RimMandrake/rimflow/roles/walk_brief.md`. Dispatch's steward line names
the job. `advance --to his_walk` checks only the brief (`maturation.read_walk_brief`):
`version/walk_brief/arrival_<N>.md` (N = `pre_human_arrivals`), its four headings filled (what to open; what changed
since his last look; known, not fixed: you need not report these; what I noticed first), and a `written_by` unit that
made no stage move and no in-game row of this version (`maturation.evidence_writers`). No `--steward-confirms`, no
road back. Arrivals are still counted. No mod has reached it.

### Stage 8: His walk

`advance --to passed` needs `--owner-said` (his words). The pass record (date, commit, bars, evidence, cost, cycles) is
not built; it is to be written by hand the first time.

## 5. Acts only Mandrake performs

- **Lock** a Design Version: his word, written into `VERSION.json` (`locked_by`, `owner_words`).
- **Certify coverage** past a judge: `concept_tree.py certify <dir> --owner-event OWNER:<tsn>`. The certificate
  (`signed_by: owner`) holds only while: the event exists in `infrastructure/state/ledger/events/OWNER.jsonl`, carries
  his words (`ownerSaid`) or a card (`byCard`), is on the concept's own ledger item (`stage.json` `item`), and is newer
  than the judge verdict on file; that verdict is unchanged; `coverage_fixes.json` is unchanged; and the tree and sheet
  hashes are the ones he certified. Any later edit to the tree or sheet, including one his own card asks for, voids it.
- **Change a locked bar**: the lock rule (spec §4 Stage 1, agreed 2026-11-14): a wrong check whose bar keeps its meaning
  is fixed and re-pinned by the steward; a bar may be added on a discovery; a bar made easier or deleted is his call; a
  bar deferred is the Conductor's call, told to him after (a trial he may withdraw); a change to what the mod is goes to
  the next version. A change he makes by card to a locked tree is re-pinned with `designer_stage.py repin <dir> --source
  OWNER:<tsn> --why ...`.
- **Divergent or Convergent, and Polish moves, are not his to wait on**: the Conductor decides each when the ticket is
  filed as active, and he reads it in his daily digest (card 2026-11-23, `standing_rulings.md` §Mod Design Versions).
- **Pass** a version at his walk.
- **Lift a park**: a Designer loop parked for him (`park_summary.md`) lifts only on his own word on the item.

## 6. How the Design Version moves

- A mod in the Designer enters as `0.1.0`. A version before release is `0.x`; `1.0.0` is the version shipped to
  players. MAJOR is a redesign, MINOR a Divergent addition, PATCH Convergent polish after a pass.
- **Release candidates**: the ruling says a judge round is `-rc.N`. The code counts arrivals at Stage 7
  (`pre_human_arrivals`) and writes no rc number. What counts as a round is open question 13 of the spec.
- The record's version must equal `VERSION.json`'s; otherwise every advance is refused.
- Nothing yet opens a new version: no mod has passed.

## 7. Files

### The concept folder, `design/concepts/<Mod>/` (the Designer's)

| file | what it is | written by |
|---|---|---|
| `stage.json` | the Designer's inner step, status, budget and charges, the open run, accepted results, coverage rounds | `designer_stage.py` only |
| `record.json` | the working record: scope, decisions, questions to him, inventory, contradictions, failure modes, root; every entry source-linked | the Designer |
| `log.md` | the verbatim record of the argument; never injected into a run | the Designer |
| `sheet.md` | the plain-words design sheet | the Designer |
| `tree.json` | the design tree (leaves, root reference, coverage stamp); format `design/RimMandrake/concept_tree_schema.md` | `concept_tree.py write`, `sign`, `certify` |
| `scenes.json` | the proof-scene contract | the Designer |
| `floor.json` | per floor line (`concept_floor.json`): applicable, not applicable with evidence, or disabled by him | the Designer |
| `exam.json` | the Cold Reader exam, frozen against the tree and sheet hashes | the examiner |
| `coverage_verdict.json` | the coverage judge's last verdict | `coverage_judge.py` |
| `coverage_fixes.json` | claims that judge gaps were fixed | the Designer |
| `result.json`, `result.<run>.json` | what a run says it did | the run; read by `designer_stage.py close` |
| `turn_NN.md` | a turn that waits on his answer | the Designer |
| `park_summary.md` | why a loop was parked for him | `designer_stage.py park` |
| `journal.md` | the steward's journal: "Stage now" and "Waiting on" lines on top, dated history, `### Conductor interventions` | `maturation.py advance` and the Conductor |

A Conductor intervention line has this form, and the program reads it:
`- CONDUCTOR INTERVENED (stage N, <time> PST, kind hold|release|decision|re-pin|relaunch|brief|bar-added): ... Source: ...`.
A `hold` blocks every advance until a later `release`.

### The version folder, `design/concepts/<Mod>/version/` (the pipeline's)

| file | what it is |
|---|---|
| `VERSION.json` | version, state (`locked`), who locked it and when, his words, bars met of total, tokens spent and how measured |
| `vision.md`, `bars.md` | the version's vision and its bars |
| `polish.md`, `next_version/` | the Polish list; the next version's file |
| `stage_record.json` | the stage record: stage, since, moves (from, to, when, by, why, what was confirmed), cycles, pre-human arrivals, spend rows |
| `preflight.json` | the preflight record |
| `test_table.json`, `test_table.md` | bars, deciders, stages, runnable today |
| `steward_decisions.md` | the Conductor's decisions for a builder's brief (optional) |
| `blind_challenge/cycle_<N>/` | one blind cycle's records (section 4) |
| `in_game/visit_<N>/` | one in-game visit's records (section 4) |
| `criterion_repairs/` | the neutral fixer's repairs of acceptance criteria |
| `evidence/` | evidence closed to the blind judge |

## 8. Dispatch, the status page and the alarms

- **Dispatch**: `src/RimMandrake/rimflow/maturation_dispatch.py tick --apply`, on `rm-maturation-dispatch.timer` every
  60 s, from the dispatch clone. Settings: `src/RimMandrake/rimflow/maturation_dispatch.json`. No model, no tokens.
  The advancing list: `advancing` in that file (Explosive Knockback, FlowWorks, Gimme Some Slack, Pyrelands, Graffiti,
  Contagion). A mod on his hold (`mod_owner_hold.json`) gets nothing.
  - At the offline build it launches one capped builder (Opus, `cap_tokens`, now 37,500,000 weighted tokens) when the mod has build work owed and
    nothing live on it. After a run ends, the next starts only if the count of refused bars fell. It stops on a mod, with
    one "Needs Conductor" line, when the count did not fall, when the mod's weighted tokens at the stage pass
    `stage_ceiling_tokens` (now 250,000,000; USD 100 by his card of 2026-11-15; figures moved to weighted tokens
    2026-11-26 at 250,000 per list dollar, `RIMMANDRAKE_KEEP_STAGE_CEILING_IN_TOKENS_NOT_LIST_DOLLARS`), or when a launch failed; it never retries the same refusals.
    `maturation_dispatch.py clear <Mod> --why "..."` is the Conductor's lift. A ceiling pause at any of the three
    automatic stages names its own lift, `maturation_dispatch.py release <Mod> --stage <stage> --read-tokens <spend>
    --tokens <tokens> --why "..."`: one more launch on that mod at that stage, then it pauses at the next ceiling. The
    Conductor releases without asking, told after (owner, by card 2026-11-15); `releases` lists each with its spend,
    and each reaches the daily digest as a `ceiling release` line (mod, stage, who; the page is token-blind).
  - At the blind challenge: one judge per owed cycle (section 4). At in-game acceptance: one driver per owed visit (section 4), on since
    2026-11-15 about 13:30 UTC.
  - At most `max_live` live runs on advancing mods (the settings file holds the number and each change), the Conductor's own included; the Dispatcher's account hold stops it.
  - It never judges, rejects, sends a mod back, advances, takes the bridge or runs a game.
- **Status page**: `src/RimMandrake/Utils/maturation_now.py` writes `D:\ClaudeWork\rimmandrake\conductor\MATURATION_NOW.md`
  (regenerated every Dispatch tick): where each mod stands, its "Needs Conductor" list, files that disagree. It reads
  each mod's stage from the journal's "Stage now" line, not from the stage record.
- **Alarms**:
  - `OPS_MATURATION_IDLE_ADVANCING_MOD` (`src/RimMandrake/Utils/ops_watch_rules.json`, key
    `maturation.idle_owed_max_min` > 60): an advancing mod at the offline build has had work owed with nothing running
    for over 60 minutes. Routed by `alarm_routes.json` (`maturation.*`) to Operations.
  - `REFUSAL_NOTHING_COULD_EVER_PASS` (`refusal_contract.py`): a judge or gate refusing the same thing again and again.
    The coverage judge raises it; `maturation.py advance` does not (its refusals are checked by `refusal_contract.check`,
    not counted by `submit`).

## 9. Built, and designed but not built

### Built (code and selftest exist)

| piece | code | selftest |
|---|---|---|
| Stage record, `next`, `advance`, `spend`, `seed` | `maturation.py` | `selftest_maturation.py` |
| Offline-build brief and capped launch | `maturation.py brief`, `launch` | `selftest_maturation.py --launch` |
| Dispatch step, idle alarm, cap reserved before launch, spend rows of ended runs | `maturation_dispatch.py` | `selftest_maturation_dispatch.py` |
| Blind challenge brief, launcher (up to three cycles per visit), exit reader | `maturation.py`, `maturation_dispatch.py` | `selftest_maturation.py` |
| In-game brief, launcher (shipped off; on since 2026-11-15), exit reader | `maturation.py`, `maturation_dispatch.py` | `selftest_maturation.py`, `selftest_maturation_dispatch.py` |
| SteveDesktop owner-hold refusal | `Utils/testq/pipeline_admit.py` | `Utils/testq/selftest_testq_pipeline_admit.py` |
| Status page | `Utils/maturation_now.py` | `Utils/selftest_maturation_now.py` |
| Designer inner steps, exam, coverage judge, owner certificate, repin | `designer_stage.py`, `concept_tree.py`, `coverage_judge.py` | `selftest_designer_*.py`, `selftest_concept_*.py`, `selftest_coverage_*.py` |
| Refusal records, judge calibration registry, neutral fixer | `refusal_contract.py` | `selftest_refusal_contract.py`, `selftest_judge_calibration.py` |
| Program-checked exits of the blind challenge and in-game acceptance: `advance` refuses a forward move whose exit reading is not met; a steward's word alone moves nothing; his newer OWNER event is the only override (clause `exit_met`) | `maturation.py` (`exit_met_clause`) | `selftest_maturation.py` |

### Designed but not built

- **A common preflight** that tags each refusal as build work or a spec fault (plan slice 3). Each mod has a throwaway
  script, and the steward's word stands in for the tag.
- **A common test-table maker**: each mod has its own, and they disagree on whether his Stage 8 look counts as a check.
- **`advance` refusals counted by `refusal_contract.submit`** (plan slice 2), so a stage refused again and again raises
  an alarm. (The status page reads the stage record since 84993ce73e.)
- **The identity fields in the live drivers**: the in-game brief tells the runner to merge `build_match.py identity`
  into every row; no SteveDesktop queue job records them yet.
- **The pass record** and anything after a pass (re-running a passed version on change).
- **Routing a stage-6 check to SteveDesktop** when it is the free game: the admission rule exists, no check carries a
  `testq` block, nothing routes.

### Where the spec and the code disagree

1. **A new blind judge after a fix.** His words (spec §4 Stages 4 and 5, Road back): fix it right there, "then send it
   back to just before Stage 4 again for a new blind judgement pass". Since 10e1fafbf9 a cycle whose Problems were FIXED reads
   "a new blind judge is owed", not met, and since 2026-11-18 `advance` refuses to leave on it (clause `exit_met`).
   Pyrelands (cycle 1) and FlowWorks (cycle 1) went to in-game acceptance on 2026-11-15 after a neutral fixer's
   reconcile in the same cycle, with no new blind judge, before that refusal existed.
2. Resolved 2026-11-18: the blind and in-game exits are program-checked (the Built table, `exit_met`).
3. **Blindness**: the spec says the judge "is not told" what earlier judges found and works "from the bars alone"
   first. The code's brief tells it which files are closed; nothing enforces it.
4. **Designer exit**: the spec's exit is his word to lock; the code checks only `VERSION.json`, so a mod can be locked
   while the Designer's own lock gate refuses (Pyrelands: `VERSION.json` locked, `stage.json` blocked at step 5, coverage
   judge `not_covered` with 14 gaps written 2026-11-15T06:07Z, after the lock).
5. **Spend tracked per stage** (spec: "tokens" tracked on the mod at Stages 3 to 5): no spend row at the blind challenge
   for any mod, though one blind reconcile run on Explosive Knockback measured 3,013,781 tokens (its ledger note,
   2026-11-15T10:13Z).
6. The spec's status line said that only the stage record and the queue admission were built. That was false by
   2026-11-15 and is corrected there.

Found by the skeptical review of 2026-11-15 and confirmed by reading the code (claims and where each was read:
`D:\ClaudeWork\rimmandrake\conductor\maturation_gpt_review_20261115\claims_checked.md`):

7. **The exit readers** (tightened ef6a38dbb6): the blind reader needs a command on every fix run, rerun PASS rows with
   their command and rc 0, a planted fault caught, no dirty planted row, a list in `tests_edited.json`, and treats
   UNSETTLED lane-1 rows as not passing; the in-game reader refuses an earlier non-PASS row, a bare `site_checked`, a
   non-hash `mod_sha`, rows on two builds (a3b3dead86), thin strange-thing entries and a file that is not a save. Read
   again on 2026-11-15, Explosive Knockback cycle 2, FlowWorks cycle 1 and Pyrelands cycle 1 read not met.
8. Resolved 2026-11-18: a steward's word no longer moves a mod past an unmet blind or in-game exit (`exit_met`). His
   walk to passed needs `OWNER:<tsn>`, his event on the OWNER shard that does not refuse the pass; the Designer gate
   needs state `locked` by `owner`; `--by` must name a seat (d5d5339d3b).
9. **The offline-build gate reads the builder's own flags.** Where the lock's bars are recorded
   (`version/locked_bars.json`, `maturation.py lock-bars`; the four locked mods since this change), a test table that
   drops or invents a bar fails the offline build's exit; a bar changes there only on his `OWNER:<tsn>` card. Dispatch's progress is a refused bar resolved by id
   since e85a351a54: a rename or a flag flipped with its checks unchanged is a stop, and a stop lifts only when the
   refused set shrinks.
10. **Dispatch's ceiling** reserves the run's cap since 780db1ef3e (spent plus cap must fit), at the offline build, the
    blind challenge and in-game acceptance; an unreadable occupancy launches nothing.
11. Resolved 2026-11-18 (RIMMANDRAKE_BIND_CERTIFICATE_TO_WHAT_HE_SAW): a new owner certificate binds the gap ids and
    gap text he passed past, its event cannot be replayed onto an edited tree or sheet, and an edit made under a later
    card of his is carried by `concept_tree.py carry <dir> --card OWNER:<tsn>` (its carry note cites the card;
    RIMMANDRAKE_CARRY_OWNER_CERTIFICATE_THROUGH_HIS_OWN_CARD_EDIT). A stamp written before this carries no gap ids and
    is read on run, verdict and count as it was written (Explosive Knockback's, OWNER:1794836946186553250).
12. **Calibration cut one way** until `RIMMANDRAKE_EARN_CALIBRATION_BOTH_WAYS`: `covered` signed under an UNTESTED brief,
    `calibrate` promoted on a bare exit 0 and always wrote the registry, and advisory refusals raised repair and alarms.
    Now symmetric (the Calibration bullet above). (The coverage judge's runner exit, all-input freshness and caps after a release
    were fixed in bf830aa827.)
13. **The refusal contract** (f4e4cda069) checks passed rows' evidence as refusals', needs two shared words in
    `observed`, binds a given `sha`, and stores an all-pass verdict whole; `given` still falls back to the verdict's
    own copy (the program builds both).
14. **Stage moves** are one locked write since 84993ce73e (the record first, rolled back on failure), with
    `maturation.py next-version` for a new version; a blind-to-blind self-move with no judge record does not count a
    cycle (10e1fafbf9).

## 10. Where each mod stands (snapshot, 2026-11-15 13:21 UTC, from `maturation.py next`)

This section goes stale. The live page is `D:\ClaudeWork\rimmandrake\conductor\MATURATION_NOW.md`.

| mod | version | stage, since (PST) | what `next` says | blind cycles |
|---|---|---|---|---|
| Explosive Knockback | 0.1.0 locked | in-game acceptance, 2026-11-15 02:14 | visit 1 owed, 56 stage-6 checks, none with a `testq` block | 2 |
| FlowWorks | 0.1.0 locked | in-game acceptance, 2026-11-15 03:42 | visit 1 owed, 31 stage-6 checks | 1 |
| Pyrelands | 0.1.0 locked | in-game acceptance, 2026-11-15 01:47 | visit 1 recorded, exit not met (`sc_ruins`, `sc_ullai` unmeasured) | 1 |
| Gimme Some Slack | 0.1.0 locked | blind challenge, 2026-11-14 21:28 | cycle 1 exit not met: 1 Problem not fixed, 6 lane-1 FAIL rows | 1 |
| Graffiti | none | no stage record (Designer step 5, waiting on him; coverage judge `not_covered`, 2 gaps) | "seed its record" | 0 |
| Pyrelands Mechanics | none | intake | refused `intake_closed` | 0 |

Coverage at the lock, from `coverage_verdict.json` and `concept_tree.py gate`: Gimme Some Slack signed by the judge
(`covered`, 2026-11-15); Explosive Knockback passed on his certificate past a `not_covered` with 6 gaps, and his card of
2026-11-15 rewording a locked bar voided that certificate until he certifies the new tree
(`RIMMANDRAKE_RECERTIFY_KNOCKBACK_TREE_AFTER_HIS_OWN_REWORDING`); FlowWorks signed under the retired Arbiter; Pyrelands
unsigned.

Measured spend on the record (`stage_record.json` spend rows, tokens): Explosive Knockback Designer 102,553,396 (mostly
estimated; `VERSION.json` `measured_from`), offline build 3,668,301; FlowWorks Designer 4,324,117, offline build
3,447,605; Gimme Some Slack Designer 14,557,296, offline build 8,795,422; Pyrelands Designer 13,713,774, offline build
2,846,344. Nothing is recorded for the blind challenge or in-game acceptance.

## 11. Proposed improvements (not yet decided)

From the skeptical review of 2026-11-15 (three GPT consults at xhigh; answers and the claim-by-claim check in
`D:\ClaudeWork\rimmandrake\conductor\maturation_gpt_review_20261115\`). Every claim below was read in the code; none
was found false. Nothing here is decided and no code or bar was changed by the review. Each is a ledger item filed for
the Conductor, with its acceptance test in the item.

**Convergent** means it makes the code do what the spec or his words already say; the Conductor can build it.
**Divergent** means it changes what he decided, or picks among choices the spec leaves open; it needs his word.
Effort: S is under half a day, M a day or two, L several days.

| item | change | evidence (section 9) | feasibility | build | test | kind |
|---|---|---|---|---|---|---|
| `RIMMANDRAKE_SEND_FIXES_TO_NEW_BLIND_JUDGE` | a FIXED Problem sends the mod back to a new blind judge, not out of the stage; the cycle counter counts judge runs | 1, 14 | easy | S | S | Convergent (his words) |
| `RIMMANDRAKE_CLOSE_EXIT_READER_LOOPHOLES` | fixes need commands, a planted fault must be caught, UNSETTLED refuses, the first FAIL for a test stands, the savegame must be the run's, `filed` must name an item | 7 | easy | M | M (fixtures rewritten) | Convergent |
| `RIMMANDRAKE_BIND_ADVANCE_TO_EXIT_READINGS` | `advance` refuses a forward move whose exit reading is not met, with an override carrying his word | 2, 8 | easy once 7 lands | S | S | Divergent: the exits are PROPOSAL in the spec |
| `RIMMANDRAKE_REQUIRE_OWNER_EVENT_TO_PASS` | his walk to passed, and the Designer lock, need an owner ledger event, not a string or a prefix | 8 | easy | S | S | Convergent |
| `RIMMANDRAKE_DERIVE_CHECKS_FROM_LOCKED_BARS` | the test table is compared with the locked bars; "progress" is measured from the checks, not the builder's flags; renames do not lift a stop | 9 | moderate | L | M | Convergent |
| `RIMMANDRAKE_RESERVE_CAP_BEFORE_LAUNCH` | launch only if spent plus the run's cap fits the ceiling; blind and in-game spend recorded; unknown occupancy fails closed | 5, 10 | easy | S | S | Convergent |
| `RIMMANDRAKE_BIND_STAGE_EVIDENCE_TO_ONE_BUILD` | the pass record (the build match at in-game acceptance and the walk brief are built by `RIMMANDRAKE_FOLD_STAGE_SEVEN_INTO_WALK_BRIEF_NO_VETO`) | 9, 7 | moderate | M | M | Convergent |
| `RIMMANDRAKE_BIND_CERTIFICATE_TO_WHAT_HE_SAW` | the certificate names the gaps he saw and the tree hash, and his event must post-date the tree edit | 11 | easy | M | S | Divergent: which words carry a certificate |
| `RIMMANDRAKE_HASH_EVERY_COVERAGE_INPUT` | the coverage judge's freshness covers every input it reads; a non-zero runner exit refuses; caps hold after a release | 12 | easy | S | S | Convergent |
| `RIMMANDRAKE_EARN_CALIBRATION_BOTH_WAYS` | a brief signs in either direction only when calibrated; `calibrate` checks its cases ran and has a read-only status; advisory refusals do not raise repair; fix the registry's FlowWorks text | 12 | moderate | M | M | Divergent: spec open question 7 |
| `RIMMANDRAKE_CHECK_PASSED_CONTRACT_EVIDENCE` | passed rows get the same evidence checks as refusals; `given` and `sha` are compared, not asserted; all-pass verdicts stored | 13 | easy | S | S | Convergent |
| `RIMMANDRAKE_WRITE_STAGE_MOVES_ATOMICALLY` | one locked write per move; a next-version operation; the status page reads the record | 14, slice 2 | easy | M | S | Convergent |
| `RIMMANDRAKE_RUN_DESIGNER_EXAM_BY_LAUNCHER` | the exam's scenarios, controls and Challenger are produced and checked by a launcher, not self-reported | spec §4 Stage 1 | moderate | L | M | Convergent; exam retention is open question 7 |

Order that pays first: the new-blind-judge rule and the reader loopholes (they decide whether a mod that reached
in-game acceptance on 2026-11-15 should have), then the ceiling reservation (money), then binding `advance` to the
readings once he rules on the exits. Routing Stage 6 checks to SteveDesktop is already filed as
`RIMMANDRAKE_AUTHOR_TESTQ_BLOCKS_STEVE_SITS_IDLE_BY_RULE`.
