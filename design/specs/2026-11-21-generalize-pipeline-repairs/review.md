# Review: the general faults behind the pipeline's repairs since 2026-11-13

Item `RIMMANDRAKE_GENERALIZE_PIPELINE_REPAIRS_INTO_FEW_PRINCIPLES`. The owner's words, 2026-11-21 about 1:10 AM PST:
"I need you to review the repairs that have been made that should have been form rather than a specific fix. Find
those since maturation pipeline turned on and find the form, then fix it. I don't want this pipeline turning into a
complex expert system or tree of descriptions and specific rules. Fix the principles. Generalize."

Each claim is tagged `[measured]` or `[guess ~N%]`. A number that could not be counted reads UNMEASURED.

## Questions for the owner

None. No principle below needs one of his five acts, and none changes what a mod must pass.

## Terms

- **Repair**: a commit that changes pipeline machinery because the machinery did a wrong thing.
- **Pipeline machinery**: files under `src/RimMandrake/rimflow`, `.claude/hooks` and `src/RimMandrake/Utils`.
- **General fault**: one design fault of which many repairs were single cases.
- **Per-case repair**: a repair that makes one case right and leaves the general fault in place.
- **Live effect**: an act that changes the real system: it starts a real run, writes the real ledger, or drives a real
  game.

## The nine principles

The order is by the number of repairs that each one explains, largest first. Counts are in the next section. A fresh
reader read this file once on 2026-11-21. Its answer was applied: the first draft's "one home" and "identity"
principles are one (principle 2), and the first draft's "named target" principle was two (principles 4 and 8).

1. **A stop that the work did not cause costs the work nothing and starts its own repair.** A run that was killed,
   refused, held or never started spends no trial of the mod. The program that sees the stop starts the next act
   itself. It does not write a hand step.
2. **One home for a fact, identity included.** A fact is written in one durable place. Every other place reads it
   there, or is a copy that a program makes and checks. The mod, item, stage, game and run of a piece of work are such
   facts: the launch writes them as fields, and no reader builds a name again or infers them from a title, a note or
   a path.
3. **A fault of form is repaired at the gate.** The gate repairs the input, or it returns the exact repair to the same
   agent in the same run. A program never sends refused input again unchanged.
4. **A test makes no live effect.** The launcher and the ledger writer refuse a test process. A test does not have
   to isolate itself from each real store.
5. **"Could not look" is its own answer.** An unreadable source gives UNMEASURED. It never gives 0, empty, dead or
   "none found".
6. **Validity follows the relation.** A result stays valid until something that its check reads or exercises changes.
   A whole-artifact hash does not decide validity when a per-part relation can be read.
7. **A limit names its danger.** A cap, timeout, count or text cut names the danger and the evidence. A limit that
   cannot name both is removed.
8. **A program acts only on a target that was named.** A tool with no named game, clone or store stops. It does not
   fall back to a default one.
9. **A rule that a tool can do is done by the tool.** The test for one rule line: on the input that the rule guards,
   does a tool do the act, or return the repair to the agent? If yes, delete the rule line. Done means: the sections
   listed under "The rule tree, measured" hold fewer lines, and no section restates what a gate prints.

Principles 1 and 3 belong to the live run `RIMMANDRAKE_REPAIR_AT_THE_REFUSAL_NO_STOP_FOR_UNTIED_SHOES`. Principle 6
belongs to the live run `RIMMANDRAKE_RERUN_ONLY_CHECKS_THE_CHANGE_TOUCHES_NOT_ALL_203`. This item owns 2, 4, 5, 7, 8
and 9.

## How the repairs were counted

- Population: 967 commits since 2026-11-13 that touch pipeline machinery (`git log --since=2026-11-13 --no-merges`
  over the three paths) `[measured]`.
- Step 1, patterns: a script (`classify_subjects.py` beside this file) matched each commit subject against one ordered list of patterns, one list entry per
  class. 503 subjects matched a class. 464 matched none `[measured]`.
- Step 2, precision: 56 pattern matches in four classes were read by hand. 31 were true cases of their class
  `[measured]`. The other six classes were not read; their precision is taken as 0.7 `[guess ~60%]`.
- Step 3, the unmatched 464: a random sample of 120 was read and classed by hand `[measured]`. Each sample count is
  scaled by 464/120.
- Each commit is classed once. A commit that shows two faults is cited under both below, and counted under one.
- The estimate for a class of general fault is (pattern matches × precision) + (scaled sample count). The rule-text
  row and the not-a-repair row are not scaled by a precision: their patterns match a file prefix or a mod name. Each estimate is a
  `[guess ~65%]` to within one third of its value. No diff was opened to make these counts.
- Not counted: the Conductor log (7,562 lines) and the closed items (2,671 files) were not read in full: their counts
  per class are UNMEASURED. The census of 2026-11-15 gives about 134 hand interventions and 42 lessons `[measured by
  that document]`. `maturation_hands.py list --all` gives 90 lines `[measured]`.

| what the 967 commits are | pattern matches | scaled sample | estimate |
|---|---|---|---|
| cases of one of the nine general faults (rule text apart) | 335 | 170 | about 375 |
| rule text added or moved (principle 9) | 44 | 12 | about 56 |
| a new gate, tool, page or stage (not a repair) | not matched | 135 | about 135 |
| a single bug with no general fault found | not matched | 73 | about 73 |
| mod work, an owner setting, removal of a retired era, bookkeeping | 124 | 73 | about 197 |

The rows do not sum to 967: the first row carries the precision factor. About 375 of 967 commits (39%) were per-case
repairs of nine general faults `[guess ~65%]`.

## Evidence for each principle

### 2. One home for a fact, identity included — about 83 repairs

- `97f0cc2819` His hold: the control store is the one writer and `mod_owner_hold.json` its mirror.
- `a29c004373` The plan timer read a stale week drop-in, not `switching_plan.json`.
- `c5e3cae1fa` The in-game brief disagreed with the exit reader about a FAIL.
- `1b79ae76b0` `pipe next` had its own forecast; now it runs the live tick tree's forecast.
- `a84613e77e` The judge pre-step checked the stage as it was when the run was asked.
- `0c320de76d`, `864fc98a51` The hand-act record and the tick's books disagreed about one run.
- `65e95f5a90` Positive steps text: seven copies became one source.
- `c32e228e91`, `774dff5a6e`, `45e3f2d4c7` State that lived only in a clone was lost or stranded.
- `f34e6e7228` The tick's item name lost its visit word; the spawn guard refused it three times.
- `c8e06b5d31`, `5e6f692d65` A run was placed on the mod that its notes cited, not the mod that its launch recorded.
- `551b86c17d` A manual account switch was attributed by a time window, not by the switcher log.
- `6ddd8a7517`, `3043049714`, `e85a351a54` Examiner, cleanse marks and progress were matched by label, not by id.
- `839d7e1393`, `29c5f7491e` The model was named by tier in one place and by full id in another.
- `4f12b10443` (the model case done right) A launch names its unit as a field; the reader of systemd-run options went.
- `938880262a`, `da889bc937` A session and a parent were found by search, then recorded as fields.
- What the per-case repairs left: mirror files, "agrees with" selftests, rule lines that say which copy wins, a
  parser for each name shape, and a name builder in each caller.
- The one change: a copy is made by a program and carries a `GENERATED from <home>` line. One publish check makes each
  copy again and compares. A file with that line that differs fails. A fact with no generator is read from its home.
  For identity the home exists: the control store's run record holds unit, family, mod, item, stage, role and model.
  Add the game. Every reader takes identity from that record. One function builds an item name; nothing parses one.

### 1. A stop the work did not cause — about 90 repairs (live run)

- `7db1e1b33e` A `launch_failed` record is `void_system`, never charged.
- `2d58382ecc` A refused launch that waits is no fault.
- `8b055e3018` A launch refused by a deliberate control OFF is a planned hold.
- `4fe2af3f9e` A Designer run that the machine stopped: no retry spent, no rejection.
- `aea6ee2885` A FAIL classed HARNESS or SITE spends nothing.
- `cdfab28b7b`, `b917039b17`, `994f9807c1` The tick takes an exit, launches a proof run, lifts a block itself.
- `ec49db3c3a`, `b08f107a1c` An owed run end is continued by a program.
- The census of 2026-11-15: about 134 hand interventions, most of them "wrote NEXT (hand step)".
- What the per-case repairs left: one branch per cause in `run_void.py` and `maturation_dispatch.py`, one counter per
  kind of trial, and a rule section per kind of stop (`No trial is spent`, `The pipeline fixes its own defects`).
- The one change: each run end carries one class (the work failed; the system stopped it; it was held; form). Every
  counter reads that class. A stop with a class other than "the work failed" starts its repair or its retry.

### 4. A test makes no live effect — about 50 repairs

- Tonight: a selftest of a live run reached the real launcher, started two real runs on fixture mod `A`, and filed
  real items (ledger notes of 2026-11-21 08:56Z and 09:04Z on `RIMMANDRAKE_REPAIR_A_FAULT_LOOP_AT_THE_RUN_TWO`).
- `5f1df790a8`, `b28d8d018f`, `8716c3bcdd`, `328611932d`, `1fe595f83e` Five selftests read the live void store, the
  live bridge or the live ledger.
- `RIMMANDRAKE_ISOLATE_SEAT_RESTART_D1_FROM_REAL_UNPUSHED_COMMITS` A test read the clone's real unpushed commits.
- `conductor_log_guard.py`: two selftests rang fake alarms in the real Conductor log (422 and 18 lines). "Each test was
  redirected in turn; this closes the class", for the log only.
- What the per-case repairs left: an isolation fix inside each selftest, an environment variable per store
  (`RM_CONTROL_DB`, `RM_OWNER_HOLD_FILE`, `RM_DISPATCHER_STATE` and others), and three separate definitions of "a test
  process" (`control.test_process`, `conductor_log_guard.under_test`, `RM_UNDER_SELFTEST` readers).
- The one change: one definition of "this is a test process". The three doors to a live effect refuse it: the launch
  primitive (`control.launch_unit`), the ledger writer (`model.append`) and the Conductor log writers.

### 8. A program acts only on a target that was named — about 14 repairs

- `08b3ba8881`, `e400c1b366` A game-b tool with no port in its environment drove game a, with no error.
- `4ee4209d57` A tool watched game a's Saves folder while it drove game b.
- `b5c602d88d`, `98ba034b57` A gate read Archmagi's bridge for a SteveDesktop act.
- `11a050e9d8`, `9eb814c040` A gate read the Dispatcher's clone, not the concept's own clone.
- `e8dbd5efb3` The harness wrote during a dry run.
- What the per-case repairs left: rule lines such as "`RM_GAME_INSTANCE=b` alone does not reach a `python.exe` tool".
- The one change: the bridge client stops when a game is named and its port is not in the environment. The stop names
  the repair (`game_instance.py env <name>`).

### 3. A fault of form is repaired at the gate — about 57 repairs (live run)

- `9e5768e86f` A 66-character item name was refused three times; names now never refuse a filing.
- `29c5f7491e` A full model id is repaired to its tier.
- `7ecf4a9e73`, `d354ed250e` A card too big for one ledger line is fitted or split.
- `489968e096` A brief without its card text was refused three times.
- `342f94a8f8` A step tried to commit an ignored lock file three times.
- `2024d9b916` His "Afk. Goodnight." was refused all night.
- `84ca416f3a`, `b7916ccd00` A file identical to origin's copy was a refusal.
- `3e224420d1` His word was refused for a missing provenance flag.
- What the per-case repairs left: one "never refused" branch per gate and one rule line per gate. The Conductor counted
  333 refusal lines in 48 `rimflow` files `[measured by the Conductor]`.
- The one change: the shared answer for a fault of form that the live run builds (`form_fault.py` in its clone).

### 5. "Could not look" is its own answer — about 38 repairs

- `a79ad5e7bb` `read_version_bugs` answered a bare None.
- `1a51e02130`, `f1c99aefbb` A spend field and a proof log with no reading read 0.
- `20fd500307` Three health targets read dead when no verdict was made.
- `dd2f57e81e` A pid whose reading failed was treated as dead.
- `d8a52e54c4`, `dd37ba2758` An unmeasured login was paced on the previous account.
- This principle is already in the machinery: `0c6b1d6326` (the four-answer type `probe_result`) and `9a14f32660` (a
  lint at `./publish`). It is the pattern for the others: one type and one check replaced the per-case repairs.
- What is left: 62 places on the lint's allowlist `[measured by 9a14f32660]`. No new machinery is needed.

### 6. Validity follows the relation — about 25 repairs (live run)

- `453e648953`, `84ef53b231` After a coverage repair, only the touched exam scenarios run again.
- `0957677739`, `cd86ab4735`, `5880cdb533` Re-pin rules, one per case.
- `ac9a5418ce` An uncovered line refuses the full run only.
- The census of 2026-11-15: 13 hand re-pins of locked files for test text or bookkeeping.
- The one change: the shared relation module of the live run.

### 7. A limit names its danger — about 18 repairs

- `321aee60b5` The launcher had a $15 default with no danger named.
- `87fb5ccdd2` A 240 s default timeout crashed a 273 s test.
- `f2fa414861` A 1G memory cap was met by the first tick.
- `6a41100464` Bare text cuts.
- The census of 2026-11-15: the Designer's chain cap of 8 was pressed past by hand three times.
- The rule exists (`9f6d6fe34c`). The pattern search found more limits added (about 34 commits) than limits repaired
  `[guess ~55%]`.
- The one change: none is proposed. Two lints exist (`no_bare_cuts`, the call-deadline lint), and each boundary page
  has a LIMITS section. A separate registry of limits would be a new framework. The next step is a count: `git grep`
  the numeric defaults of timeouts and caps in pipeline files. A default with no danger named beside it and no entry
  under LIMITS on its page is deleted, and its caller runs with no limit.

### 9. A rule that a tool can do is done by the tool — about 56 commits added rule text

- `c0d720ea79` Five briefs each got the same three rules pasted.
- `f48b559cd5` "a stop rule in each judging brief".
- `e400c1b366` A rule line "say `env b`" where the tool could stop on a missing port.
- `4f9e45812e` "define the several live games ... in every top document".
- This is the growth that the owner names. The next section measures it.

## The rule tree, measured

| file | lines 2026-11-13 | lines 2026-11-20 | lines now |
|---|---|---|---|
| root `CLAUDE.md` | 390 | 638 | 736 |
| `design/RimMandrake/standing_rulings.md` | 623 | 1,553 | 1,734 |
| `infrastructure/agents/CHARTER.md` | 207 | 282 | 300 |
| `src/RimMandrake/rimflow/roles/*.md` (all) | 2,336 | 4,024 | 4,096 |
| `rimflow` Python files (count) | 407 | 455 | 468 |
| `selftest_*.py` files (count) | 1,492 | 1,600 | 1,627 |

All cells `[measured]` with `git show <commit of that date>:<file> | wc -l`. The four rule files grew from 3,556 to
6,866 lines in eight days. Trap lists now: `tool_traps.md` 139 lines, `instrument_traps.md` 237 lines `[measured]`.

Root `CLAUDE.md`, sections classed by hand against the nine principles:

| principle | sections of the root `CLAUDE.md` that are cases of it | lines |
|---|---|---|
| 1 and 3 | A fault of form (19); No trial is spent (9); The pipeline fixes its own defects (12); A refusal carries its path (6); His word is not refused (8); the refusal lines of Queue items are NAMED (5); the fix-in-the-sitting half of Touching code (about 25); Evidence-for-Ask (11) | about 95 |
| 8 | There are several live games (27); about 10 lines of The bridge; 5 lines of Facts you cannot guess | about 42 |
| 6 | After a change (14) | 14 |
| 7 | No limit without the danger (17); A limit from before the Maturation Pipeline (6) | 23 |
| 2 | the clone-state lines of Git (6); Transient (9) | about 15 |
| 9 | lines that only restate what a hook does (blanket stage, worktree, compound command) | about 10 |
| 5 | two lines of Facts you cannot guess | 2 |

About 200 of 736 lines (27%) are cases of the nine principles `[guess ~70%]`. The other lines are game facts, design
rulings, authority rules and pointers: they are not pipeline repairs. The same classing of `standing_rulings.md`, by
section title: 16 sections with 592 of 1,734 lines are cases of the principles `[measured line counts, classed by
title: guess ~65%]`. The role files and the trap lists were not classed line by line: UNMEASURED.

What can be deleted, and when:

- Now, with principles 4 and 8 in the machinery: the rule lines about a bare `RM_GAME_INSTANCE=b`, and the second and
  third definitions of a test process.
- After the two live runs land: the root sections of principles 1, 3 and 6 can become one short section each. Today
  they are nine sections with about 109 lines.
- Not deletable by a principle: his five acts, his holds, the OWNER bridge hold, `./pipe` stops, the spend stop, the
  account order and leave lines, the machine-safety brakes, the blind boundaries of judges, and the north-star bars.

## The two live runs, judged against this review

Read twice: at 2026-11-21 about 1:15 AM PST (nothing landed) and at 2:15 AM PST (both had landed parts; both still
live). This item did not edit their files.

- `RIMMANDRAKE_REPAIR_AT_THE_REFUSAL_NO_STOP_FOR_UNTIED_SHOES` (principles 1 and 3), commit `1e91cc0953`.
  - It is the principle: `form_fault.py` (177 lines) states "There is no table of refusal kinds", and the fault loop
    counts only a run that started and died `[measured: the file's text]`.
  - It is not yet a deletion: +856 and -76 lines in that commit `[measured]`. Two non-test files call `form_fault`
    (`maturation_dispatch.py`, `run_void.py`) `[measured]`. The gates in the other files with refusal lines still
    refuse in their own way.
  - The specific rule to watch: its census converts gate by gate. Exact next step after it ends: make `form_fault`
    the only way for a pipeline file to refuse (one lint at `./publish` that fails a bare `sys.exit(2)` or a bare
    `REFUSED` print), then delete the per-cause branches of `run_void.py` that the started-and-died rule covers.
  - Its fix for tonight's test leak inside one function ("the real launcher only when the fixture list is empty") is
    now unnecessary: `control.launch_unit` refuses a test process (Results, principle 4). It can be deleted when the
    run ends.
- `RIMMANDRAKE_RERUN_ONLY_CHECKS_THE_CHANGE_TOUCHES_NOT_ALL_203` (principle 6), commits `b23dbf2b12`, `d8a8a48ef4`,
  `fe98fec94d`.
  - It is the principle: one module, `rerun_relation.py`, and the certificate and Stage 6 read it `[measured: the
    commit file lists]`.
  - The risk: the module is 603 lines and follows Python symbols and JSON keys to decide what a change touches
    `[measured: line count and function names]`. That is a large new mechanism. A relation that reads only what each
    check declares (`reads`, `exercises`) and file paths is smaller. Whether the symbol reach is needed is not
    measured here: `[guess ~50%]` that the declared relation alone decides the same reruns.
  - Exact next step after it ends: count how many reruns the symbol reach saves beyond the declared relation on the
    three live mods. If few, delete the symbol reach. Then delete the older freshness rules that the module covers
    (the exam retake map of `453e648953`, the re-pin rules of `0957677739`, `cd86ab4735`, `5880cdb533`).
  - `standing_rulings.md` grew by 47 lines in `fe98fec94d` and the root `CLAUDE.md` by 14 for this rule. No older
    rule text was deleted for it yet.

## Part 2

What was fixed, what was deleted, the counts and each exact next step: `results.md` beside this file.
