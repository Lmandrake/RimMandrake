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

The order is by the number of repairs that each one explains. Counts are in the next section.

1. **One home for a fact.** A fact is written in one durable place. Every other place reads it there, or is a copy
   that a program makes and checks. Nobody keeps a second copy by hand.
2. **A stop that the work did not cause costs the work nothing and starts its own repair.** A run that was killed,
   refused, held or never started spends no trial of the mod. The program that sees the stop starts the next act
   itself. It does not write a hand step.
3. **A program acts only on a target that was named; a test cannot make a live effect.** A tool with no named game,
   clone, store or ledger stops. It does not fall back to the real one. The launcher and the ledger writer refuse a
   test process.
4. **A fault of form is repaired at the gate.** The gate repairs the input, or it returns the exact repair to the same
   agent in the same run. A program never sends refused input again unchanged.
5. **An identity is recorded once, as a field, and read.** The mod, item, stage, game and run of a piece of work are
   fields that the launch writes. No reader builds a name again or infers identity from a title, a note or a path.
6. **"Could not look" is its own answer.** An unreadable source gives UNMEASURED. It never gives 0, empty, dead or
   "none found".
7. **Validity follows the relation.** A result stays valid until something that its check reads or exercises changes.
   A whole-artifact hash does not decide validity when a per-part relation can be read.
8. **A limit names its danger.** A cap, timeout, count or text cut names the danger and the evidence. A limit that
   cannot name both is removed.
9. **A rule that a tool can do is done by the tool.** A rule line for agents is written only when no tool can do the
   act or repair the fault. When the tool does it, the rule line is deleted.

Principles 2 and 4 belong to the live run `RIMMANDRAKE_REPAIR_AT_THE_REFUSAL_NO_STOP_FOR_UNTIED_SHOES`. Principle 7
belongs to the live run `RIMMANDRAKE_RERUN_ONLY_CHECKS_THE_CHANGE_TOUCHES_NOT_ALL_203`. This item owns 1, 3, 5, 6, 8
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
- The estimate for a class is (pattern matches × precision) + (scaled sample count). Each estimate is a
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

The rows do not sum to 967: the estimates carry the precision factor. About 375 of 967 commits (39%) were per-case
repairs of nine general faults `[guess ~65%]`.

## Evidence for each principle

### 1. One home for a fact — about 44 repairs

- `97f0cc2819` His hold: the control store is the one writer and `mod_owner_hold.json` its mirror.
- `a29c004373` The plan timer read a stale week drop-in, not `switching_plan.json`.
- `c5e3cae1fa` The in-game brief disagreed with the exit reader about a FAIL.
- `1b79ae76b0` `pipe next` had its own forecast; now it runs the live tick tree's forecast.
- `a84613e77e` The judge pre-step checked the stage as it was when the run was asked.
- `0c320de76d`, `864fc98a51` The hand-act record and the tick's books disagreed about one run.
- `65e95f5a90` Positive steps text: seven copies became one source.
- `c32e228e91`, `774dff5a6e`, `45e3f2d4c7` State that lived only in a clone was lost or stranded.
- What the per-case repairs left: mirror files, "agrees with" selftests, and rule lines that say which copy wins.
- The one change: a copy is made by a program and carries a `GENERATED from <home>` line. One publish check makes each
  copy again and compares. A file with that line that differs fails. A fact with no generator is read from its home.

### 2. A stop the work did not cause — about 90 repairs (live run)

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

### 3. A named target; no live effect from a test — about 64 repairs

- Tonight: a selftest of a live run reached the real launcher, started two real runs on fixture mod `A`, and filed
  real items (ledger notes of 2026-11-21 08:56Z and 09:04Z on `RIMMANDRAKE_REPAIR_A_FAULT_LOOP_AT_THE_RUN_TWO`).
- `5f1df790a8`, `b28d8d018f`, `8716c3bcdd`, `328611932d`, `1fe595f83e` Five selftests read the live void store, the
  live bridge or the live ledger.
- `RIMMANDRAKE_ISOLATE_SEAT_RESTART_D1_FROM_REAL_UNPUSHED_COMMITS` A test read the clone's real unpushed commits.
- `08b3ba8881`, `e400c1b366` A game-b tool with no port in its environment drove game a, with no error.
- `4ee4209d57` A tool watched game a's Saves folder while it drove game b.
- `b5c602d88d`, `98ba034b57` A gate read Archmagi's bridge for a SteveDesktop act.
- `e8dbd5efb3` The harness wrote during a dry run.
- What the per-case repairs left: an isolation fix inside each selftest, an environment variable per store
  (`RM_CONTROL_DB`, `RM_OWNER_HOLD_FILE`, `RM_DISPATCHER_STATE` and others), and rule lines such as "`RM_GAME_INSTANCE=b`
  alone does not reach a `python.exe` tool".
- The one change: one predicate says "this is a test process" (`control.test_process()` exists). The launch primitive
  (`control.launch_unit`) and the ledger writer (`model.append`) refuse a live effect from a test process. A tool that
  is given a game name with no port stops and names `game_instance.py env <name>`.

### 4. A fault of form is repaired at the gate — about 57 repairs (live run)

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

### 5. An identity is recorded once and read — about 39 repairs

- `f34e6e7228` The tick's item name lost its visit word; the spawn guard refused it three times.
- `c8e06b5d31`, `5e6f692d65` A run was placed on the mod that its notes cited, not the mod that its launch recorded.
- `551b86c17d` A manual account switch was attributed by a time window, not by the switcher log.
- `6ddd8a7517`, `3043049714`, `e85a351a54` Examiner, cleanse marks and progress were matched by label, not by id.
- `839d7e1393`, `29c5f7491e` The model was named by tier in one place and by full id in another.
- `4f12b10443` (the model case done right) A launch names its unit as a field; the reader of systemd-run options went.
- `938880262a`, `da889bc937` A session and a parent were found by search, then recorded as fields.
- What the per-case repairs left: a parser for each name shape, and a name builder in each caller.
- The one change: the control store's run record already holds unit, family, mod, item, stage, role and model. Add
  the game. Every reader takes identity from that record. One function builds an item name, and nothing parses one.

### 6. "Could not look" is its own answer — about 38 repairs

- `a79ad5e7bb` `read_version_bugs` answered a bare None.
- `1a51e02130`, `f1c99aefbb` A spend field and a proof log with no reading read 0.
- `20fd500307` Three health targets read dead when no verdict was made.
- `dd2f57e81e` A pid whose reading failed was treated as dead.
- `d8a52e54c4`, `dd37ba2758` An unmeasured login was paced on the previous account.
- This principle is already in the machinery: `0c6b1d6326` (the four-answer type `probe_result`) and `9a14f32660` (a
  lint at `./publish`). It is the pattern for the others: one type and one check replaced the per-case repairs.
- What is left: 62 places on the lint's allowlist `[measured by 9a14f32660]`. No new machinery is needed.

### 7. Validity follows the relation — about 25 repairs (live run)

- `453e648953`, `84ef53b231` After a coverage repair, only the touched exam scenarios run again.
- `0957677739`, `cd86ab4735`, `5880cdb533` Re-pin rules, one per case.
- `ac9a5418ce` An uncovered line refuses the full run only.
- The census of 2026-11-15: 13 hand re-pins of locked files for test text or bookkeeping.
- The one change: the shared relation module of the live run.

### 8. A limit names its danger — about 18 repairs

- `321aee60b5` The launcher had a $15 default with no danger named.
- `87fb5ccdd2` A 240 s default timeout crashed a 273 s test.
- `f2fa414861` A 1G memory cap was met by the first tick.
- `6a41100464` Bare text cuts.
- The census of 2026-11-15: the Designer's chain cap of 8 was pressed past by hand three times.
- The rule exists (`9f6d6fe34c`). The pattern search found more limits added (about 34 commits) than limits repaired
  `[guess ~55%]`.
- The one change: none is proposed. Two lints exist (`no_bare_cuts`, the call-deadline lint). A registry of limits
  would be a new framework. The next step is a count: `git grep` the numeric defaults of timeouts and caps in pipeline
  files, and remove each one that has no LIMITS row.

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
| 2 and 4 | A fault of form (19); No trial is spent (9); The pipeline fixes its own defects (12); A refusal carries its path (6); His word is not refused (8); the refusal lines of Queue items are NAMED (5); the fix-in-the-sitting half of Touching code (about 25); Evidence-for-Ask (11) | about 95 |
| 3 | There are several live games (27); about 10 lines of The bridge; 5 lines of Facts you cannot guess | about 42 |
| 7 | After a change (14) | 14 |
| 8 | No limit without the danger (17); A limit from before the Maturation Pipeline (6) | 23 |
| 1 | the clone-state lines of Git (6); Transient (9) | about 15 |
| 9 | lines that only restate what a hook does (blanket stage, worktree, compound command) | about 10 |
| 6 | two lines of Facts you cannot guess | 2 |

About 200 of 736 lines (27%) are cases of the nine principles `[guess ~70%]`. The other lines are game facts, design
rulings, authority rules and pointers: they are not pipeline repairs. The same classing of `standing_rulings.md`, by
section title: 16 sections with 592 of 1,734 lines are cases of the principles `[measured line counts, classed by
title: guess ~65%]`. The role files and the trap lists were not classed line by line: UNMEASURED.

What can be deleted, and when:

- Now, with principle 3 in the machinery: the rule lines about a bare `RM_GAME_INSTANCE=b`, and the per-selftest
  isolation code that the launcher and ledger guards make unnecessary.
- After the two live runs land: the root sections of principles 2, 4 and 7 can become one short section each. Today
  they are eight sections with about 109 lines.
- Not deletable by a principle: his five acts, his holds, the OWNER bridge hold, `./pipe` stops, the spend stop, the
  account order and leave lines, the machine-safety brakes, the blind boundaries of judges, and the north-star bars.

## The two live runs, judged against this review

Read at 2026-11-21 about 2:00 AM PST. Neither run has landed machinery yet `[measured: git log origin/main]`.

- `RIMMANDRAKE_REPAIR_AT_THE_REFUSAL_NO_STOP_FOR_UNTIED_SHOES` (principles 2 and 4). Its brief asks for one shared
  answer for a fault of form, and a class on every refusal that reaches the fault loop. That is the principle. Two
  parts of its brief can become per-case rules:
  - Its census writes one row per refusal site, and it converts site by site. If the shared answer is not the only
    way for a gate to refuse, a new gate brings the old behaviour back. The check to make after it lands: does one
    function own "refuse", and does a lint fail a bare `sys.exit(2)` in a pipeline file?
  - Its fix for tonight's test leak is "the real launcher only when the fixture list is empty", inside one function.
    That is a per-case repair of principle 3. This item makes the general repair at the launch primitive.
- `RIMMANDRAKE_RERUN_ONLY_CHECKS_THE_CHANGE_TOUCHES_NOT_ALL_203` (principle 7). Its plan has one shared relation
  module, then five places that use it. That is the principle. The check to make after it lands: do the certificate,
  the exam retake map and the re-pin rules read that one module, and are their own freshness rules deleted?

## Part 2 plan, for the principles this item owns

| principle | repairs | the change | state |
|---|---|---|---|
| 1 one home for a fact | about 44 | `GENERATED from` line and one compare check | next step below |
| 3 named target, no live effect from a test | about 64 | guards at `control.launch_unit` and `model.append`; a named game with no port stops | this run |
| 5 identity as a field | about 39 | readers take identity from the run record | next step below |
| 6 could not look | about 38 | already in the machinery | no change |
| 8 a limit names its danger | about 18 | count the unnamed numeric defaults, remove them | next step below |
| 9 a rule a tool can do | about 56 | delete the rule lines that principle 3 covers; merge sections after the live runs land | this run, in part |

Results and counts are written below as each one lands.

## Results

(none yet)
