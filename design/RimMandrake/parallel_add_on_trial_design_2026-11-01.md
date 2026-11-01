# Parallel add-on trial: design (TRIAL_PARALLEL_DESIGN_ADD_ON_EQUAL_ALLOWANCE)

Owner: "Yes add-on trial." This is the run that follows the serial replay. It answers the open question in
`parallel_review_2026-10-31/arms.md`: what happens to each arm's acceptance, speed and cost once it may work in
parallel. It is built to meet all seven fairness conditions in `parallel_review_2026-10-31/codex_review.md`
(lines 109-117). The checklist at the end maps each condition to its evidence. Where a condition is not yet
evidenced, the checklist says so and names the launch blocker that closes it.

Status: designed, rehearsed offline, revised after a fresh-Opus audit (PARALLEL_TRIAL_AUDIT_BY_FRESH_OPUS,
`D:\ClaudeWork\rimmandrake\parallel_add_on\naive_audit.md`, verdict "fix first"). Not launched. It launches only
after the running replay ends, and only once every launch blocker in section 9 is green. It never touches the
replay's root, its logs or `/home/mandrake/rm/trial_pin`.

## 1. Facts that shape the design (measured)

**The 25 replay tasks cannot be run side by side.** Each later task's starting tree already holds every earlier
task's real fix. Sibling containment holds for 300 of 300 pairs: 25 levels, one task per level. So running two
replay tasks at once would hand one of them the other's answer. The replay set can test only parallel work inside a
single task (helpers), not parallel work across tasks (streams).
Evidence: `D:\ClaudeWork\rimmandrake\parallel_add_on\evidence\trial25_sibling_relation.json`. The probe saw both
True and False answers before the count was trusted.

**A cumulative workload can be built from one snapshot, textually.** Taking pin
`5330ddf9b5837294344e557e6801767700b52c2e`, 13 of the 25 fixes revert cleanly both one at a time and all together.
Those 13 touch no file in common, pair by pair. The other 12 conflict or overlap, and are left out.
Evidence: `D:\ClaudeWork\rimmandrake\parallel_add_on\evidence\snapshot_revert_probe.json`.

The 13 are: RP_TESTENV_GUARD_UNSTICK_BLOCKS_ITS_OWN_SEQUEL, RP_ROSTERS_RENAME_MOVED_PORT_NAMES,
RP_SAVE_GUARD_FIX_BOM_READ_AS_BROKEN, RP_ENACT_STALE_KEY_FIX_UNREVIEWED,
RP_VALIDATE_PATCH_DESCENDANT_FIX_FALSE_ZERO, RP_RIMBRIDGE_DEADLINE_FIX_NAN_FAILS_OPEN,
RP_SEAT_SYNC_HARDEN_LITERAL_PATHSPECS, RP_CONVERSATIONS_LAND_FIX_STALE_TRAILER,
RP_SITHLINE_ROUNDTRIP_FIX_INT_WRITTEN_AS_FLOAT, RP_SARLACC_UNMEASURED_FIX_BORROWED_REASON,
RP_BRAINWORMS_VALIDATION_FIX_BORROWED_REASON, RP_GRAFFITIIMPERIAL_VALIDATION_FIX_LOST_REASON,
RP_MODCHECK_HARDEN_RESTORE_RAISE_LOSES_SHEET.

What the revert probe does NOT show, and what is done about it:

- **That each bug comes back.** A clean textual revert onto a pin that sits after many later commits does not
  prove the old bug reproduces. Launch blocker P8 (section 9) tests each task on the reverted tree. Any task
  that fails P8 is dropped from the workload before block 1, by the rule in P8, and the workload size in the rule
  file is then wrong, so the rule is re-declared and re-hashed before launch.
- **Disjointness holds only among the 13.** Three of them share files with fixes that stay applied: ENACT_STALE_KEY
  shares `enact.py` with 4 kept enact fixes; MODCHECK shares FlowWorks `validation.py` with 2 kept fixes;
  SEAT_SYNC shares `seat_sync.py` and `selftest_seat_sync.py` with SAVES_PRUNE. All the kept fixes are earlier
  levels, so a revert leaves them in place. P8's per-task green check is what shows they do not interfere.
- **Selection bias.** The 13 were chosen because they revert cleanly and touch disjoint files. So real textual
  conflicts will be rare, and the trial measures parallel work on an easy-to-integrate workload. Every result
  states this limit (rule file `claims.external_validity`).
- **A related family.** SARLACC and BRAINWORMS are both "..._FIX_BORROWED_REASON", GRAFFITIIMPERIAL is
  "..._LOST_REASON", and each touches a sibling mod's `validation.py`. Run one at a time, a later sibling may start on
  a base that already holds the pattern fix; at N>1 it often does not. One arm may also fix all three in one task.
  Section 6 handles this with a seeded dispatch order, a "green at dispatch" rule and a family sensitivity check in
  the rule.

**The snapshot leaks task names, not fixes.** A line unique to a fix never appears outside that fix's own files: 0
hits. The same search finds those lines in 28 files once the fixes' own files are included, so the instrument
works. But each task's ID appears in 5 to 12 other files. They are in `conversations/`; in the ledger shards,
handoffs and items under `infrastructure/state/`; and in the arena's `trial_tasks.json`,
`gate_reference_reds.lock.json`, `prompt_rewrites.json`, `trial_exclusions.json` and `selftest_arena_trial.py`. The
snapshot builder must delete or redact all of these and then rerun the probe until it reads 0. This probe covers IDs
and fix lines only; it is a floor, not a proof that nothing else leaks.
Evidence: `D:\ClaudeWork\rimmandrake\parallel_add_on\evidence\snapshot_leak_probe.json`. Probe:
`D:\ClaudeWork\rimmandrake\parallel_add_on\leak_probe2.py`, sha256 2e7a1e3b...6904.

## 2. Shape of the trial

Two parts. Each changes one thing, so neither part's effect is mixed into the other (condition 2).

| Part | What changes | Workload | Runs per block | Control |
|---|---|---|---|---|
| One: helpers inside a task | helper allowance H = 0 vs H = 2, with N = 1 | the 25 replay tasks, same order and serial constraint | 4 arms x (H=2 run + H=0 run) = 8 | the H = 0 run in the same block; the old replay is shown for reference only |
| Two: streams across tasks | streams N = 2, then 4 by rule; H = 2 throughout | the 13-task snapshot workload | 4 arms x (N run + N=1 run) = 8 | the N = 1, H = 2 run in the same block: same helpers, same acceptance, same fan-in |

The arms are `ralph_a_par`, `trio_par`, `v3_par` and `ralph_c_par`. They get a new root and new arm names, never
the replay's. The replay did not run ralph_c, so ralph_c has no reference row; its Part One H = 0 run is its only
baseline.

**What N means for each arm.** N is the number of builder processes working on different tasks at once. For
ralph_a, trio and v3 it is N streams, each a full copy of the arm's own loop with its own tester, critic and judge.
ralph_c is natively two builders split by area (`ralph_c_loop.py` R1, R2), so for ralph_c:

- N = 1 is member `a1` alone. Its `areas.json` homes every task on `a1`; `a2` gets a glob that matches nothing
  (R1 needs two non-empty, non-overlapping lists), and no `a2` process starts.
- N = 2 is its native `a1` and `a2`, run as two real processes (the rehearsal interleaved them in one). The
  `areas.json` splits the 13 tasks by a seeded assignment, 7 and 6, using each task's fix files as its area.
- N = 4 needs `ralph_c_loop`'s fixed two-member list generalised to N members (code change 12). If that change
  is not built with its selftest green before block 1, `ralph_c_par@N4` reads not_measured. That is never a fail
  and never a ceiling (rule `part_two.ralph_c_N4`).
- Part One uses the N = 1 form, with an `areas.json` that homes all 25 tasks on `a1`.

Launch blocker P10 checks that every task is homed and none is refused at load.

**Equal allowance.** Every arm gets the same paragraph, word for word, appended to its builder prompt:
"You may start up to H helper agents at a time. Helpers may read, search and edit files you name. Only you run the
build and the tests, and only you commit." H is filled in per cell (0 or 2). The tester, judge and critic prompts do
not change; they stay helper-free, as in the replay. An arm may decline to use helpers, but it is never denied them.
Helper use is recorded per call (section 5), so a decline shows up as a measured zero.

ralph_c's own prompt already grants helpers: `PROMPT_C.md` R6 allows up to `$RALPH_C_MAX_SUBAGENTS` (default 4)
read/search subagents that never edit. That would give ralph_c a different allowance from the other arms, and its
H = 0 control would not be H = 0. Settled this way: the trial's pinned copy of `PROMPT_C.md` drops the R6 sentence,
so the common paragraph is ralph_c's only helper grant, and the harness sets `RALPH_C_MAX_SUBAGENTS=H` for the
cell. The live `PROMPT_C.md` does not change. The trial copy is hashed in the pin manifest. Launch blocker P10
checks both.

**Part One blocks and cutoff.** Part One runs at least 2 blocks. Each block runs all 8 runs at once, and the seed
`20261101` shuffles the arm-to-slice assignment per block. The cutoff per run is max(12 h, 1.5 x that arm's
measured replay wall time for the same tasks). The replay figure is written into the pin manifest before block 1;
ralph_c, which has no replay row, uses the largest of the other three. If runway is short, Part One runs a smaller
set that is declared now: the last 10 tasks in the total order. No subset may be picked after launch.

## 3. Pin (condition 1)

The trial runs from a dedicated harness clone, `/home/mandrake/rm/parallel_trial_pin`, at a recorded commit. It
never runs from FOUNDRY's live tree. Before each run and after it, the harness writes a pin manifest holding:

- the git commit and tree hash of the harness clone, plus the sha256 of `git diff HEAD` over the WHOLE tree and of
  `git status --porcelain --untracked-files=all`, which must both be empty;
- the sha256 of every file under `src/RimMandrake/Utils/arena/`, including every prompt (`*/PROMPT.md`,
  `TESTER.md`, the trial copy of `PROMPT_C.md`), `trial_tasks.json`, the workload manifest and each arm's
  `areas.json`;
- configuration: the environment keys the harness reads (`TRIO_RIMFLOW_CMD`, `V3_LOCK_DIR`, `ARENA_ROOT`,
  `RALPH_C_MAX_SUBAGENTS`, `RM_EXEC_KEY` scheme), the sandbox profile, and the slice limits;
- tool versions: the `claude` CLI (`claude_sha.txt` style), python, git, bubblewrap;
- task inputs: the snapshot commit and the hash of the redacted tree; for Part One, the 25 base revisions and the
  replay wall times used for the cutoff;
- the decision rule's sha256 (section 7) and the account in use with its usage at start (launch probe 5).

If the manifest at the end differs from the one at the start, the run is invalid and is rerun, not scored.

What has been exercised so far is narrower. The rehearsal's `pin_mutation_refused` and `pin_unchanged_over_run`
checks ran a smaller manifest: its `runner_head` was FOUNDRY's live tree (62a8abb), because the dedicated clone does
not exist yet; it dirty-checked only `src/RimMandrake/Utils/arena`; and it held no tool versions, environment keys,
sandbox profile or slice limits. It shows the refuse-on-change logic works, nothing more. The full manifest is
launch blocker P0.

## 4. Resource envelope (condition 3)

Each run counts every role, not just builders:

| Role | Slots per run |
|---|---|
| builder | N (Part One: 1) |
| builder helpers | N x H |
| tester / critic / judge | 1 per stream, as each arm's own loop starts them |
| fan-in merger (section 6) | 1 per run, charged to the arm |
| controller / dispatcher | 1 per block, with no model calls except keyed ones (role=controller) |
| heavy selftest lane | the existing one-at-a-time lane, shared across the block's 8 runs through one queue |

**Blocks.** A block runs, for every arm, the cell and its control at the same moment, so both meet the same
machine, heavy-lane and account load. This replaces the first draft, which ran the N = 1 control in its own,
lighter block and so confounded speedup with contention. The control now carries the block's load, not the
load of a block at N = 1. That makes a cell's speedup a measure of "N streams beside other work" against
"1 stream beside the same work". This is the honest comparison for a machine that is shared anyway.

- **Slices.** Under `rm-harness.slice` there is one child slice per arm, of equal CPU weight and equal memory
  limit, and inside it one sub-slice for the cell and one for the control. The CPU weights are N : 1 and the memory
  limits are proportional, so the control is not starved by its own arm's cell.
- **Order.** The seed `20261101` shuffles the arm-to-slice assignment per block. The N ladder runs 2 then 4. There
  are at least 2 blocks per N.
- **Heavy lane.** Round-robin across the block's 8 runs, FIFO within a run, so no run can queue ahead of the
  others by submitting first.
- **Waits.** Each run records queue length and service time for the test lane, the judge and the fan-in step,
  so a cap from the completion side shows up as a wait and not as an unexplained slowdown (codex finding 8).

**Fan-in cost.** Fan-in reruns the hidden check of every task landed so far on each landing (section 6). That is
at most 13 x 14 / 2 = 91 hidden-check runs per run, plus rework, and 8 runs share the block. The hidden checks run on
the arm's own fan-in lane, not on the shared heavy lane, and their time is a reported fan-in wait. P8 measures each
check's time. Launch blocker P13 requires the estimated fan-in check time per run to be under 10% of the cutoff.
If it is not, the design changes before launch (for example, rerun every landed check only at drain and on
conflicts), and that change is re-declared.

**Runway.** The existing floor of 0.15 stays. At admission, each stream reserves its expected next-call spend, so N
streams cannot all pass the same floor check at once (codex finding 4). Wall time is bounded by blocks x cutoff:
Part One at most 2 x max(12 h, 1.5 x replay wall), and Part Two at most 4 x 12 h = 48 h. Account burn per block is
not known: P11 measures it at the N = 4 load. The N = 4 blocks run only if, after the N = 2 blocks, the measured burn
fits the remaining runway for 2 blocks. Otherwise every arm's N = 4 reads not_measured. That gate is a formula in
the rule file (`part_two.n4_runway_gate`), not a judgement call after launch. Launch blocker P14 is the total
runway estimate, written before block 1.

## 5. Spend: keyed per call, reconciled where a second source exists (condition 6)

**Unit.** Spend is ITE, Opus-input-equivalent tokens, weighted by `arena_analysis.py` at the pinned commit from raw
per-model counts. It is never the account's percent-of-window figure.

**Execution key.** The harness sets `RM_EXEC_KEY=arm/stream/task/attempt/role` on every `claude -p` process it
starts: builder, tester, critic, judge, fan-in merger, controller.

**Helpers are not child processes.** An Agent-tool helper runs as a sidechain inside the builder's own `claude`
process, so an inherited environment variable cannot tag it. Helper calls are keyed from the transcript:

1. After each builder pass, the harness reads that session's transcript from the sandbox HOME (the
   `helper_capture` mirror, which already walks `<sid>.jsonl`, its `~mN` segments and `<sid>/subagents/*`).
2. Every assistant message in the main session file is keyed with the pass's own key (role=builder).
3. Every assistant message in `<sid>/subagents/<agent>.jsonl` is keyed as role=helper, with
   `helper=<agent file stem>`, `parent=<sid>`, and arm, stream, task and attempt copied from the pass's key.
4. The call id is the message id, counted once (the `session_input` rule).

**What can be reconciled, and how far.**

- **Record level, per pass.** For each pass, the CLI's own result envelope (`--output-format json`, `modelUsage`)
  is held against the transcript census of that session, helpers included. The input-side shortfall may be at
  most 0.05 (`helper_capture.RECONCILE_SHORT_MAX`), and no message id may be counted twice. The two sources are
  written by different code (the CLI's accounting and the transcript writer), but both are in the same process.
  So this check catches erased or missing transcript lines, not a CLI that miscounts. Whether the envelope's
  `modelUsage` includes helper sidechains is NOT known. Launch blocker P7 measures it. If it does not, helper
  spend has only the transcript as its source, and the design says so in every result.
- **Critic gap.** The trio and ralph_a critics run under the real HOME (commit 8ab6ab3eb0,
  TRIO_CRITIC_FIX_HOME_SWAP_HIDES_CLAUDE). The meter reads their transcripts there too. Launch blocker P3 sends one
  keyed call through each critic and checks that it reconciles.
- **Account level, per block only.** The account's usage view gives a percent of the 5-hour and weekly windows. It
  has no per-call ids and no tokens, and every other Claude window on the account (FOUNDRY, BENCH) spends from it
  too. So it cannot match record for record and cannot split spend by arm. It is recorded at each block's start
  and end and reported beside the block's keyed ITE. It voids runs only when it shows an account switch or a usage
  reset (failover; launch probe 5).

**Unkeyed calls void the run.** A call with any empty key field, or a transcript message that no pass claims,
makes the run invalid. There is no shared-overhead bucket inside a run. (The first draft said both, which
contradicted itself; the audit's finding A3.) The controller's own calls carry role=controller and are charged to
no arm. An invalid run is rerun once; invalid twice, its cell reads unmeasured.

**Helpers that overstep.** The rule "only you build, test and commit" is prompt-only, like ralph_c R6. Detection is
by transcript: the harness scans every helper sidechain's tool calls. A `git commit` or `git push` from a helper
voids the run. A helper build or test command is counted and reported per arm, and it does not void the run.

**What the rehearsal showed about spend.** Only the reconcile LOGIC. The stub's `Meter.call` wrote the keyed record
and the "independent" record in the same function with the same call id (`rehearse.py:121-138`), so green on clean
data was tautological. The red cases (dropped critic record, duplicate, empty key) do test `reconcile()`. Real
independence and real call-id availability are launch blockers P3 and P7.

## 6. Workload, fan-in and scoring (conditions 4 and 5)

**Building the snapshot.** The snapshot is a FRESH repository, not a squashed branch: `git init`, then one commit
of the redacted reverted tree. It has no alternates (the revert probe used alternates to the bench clone, which
would expose full history), no reflog, no other packs and no remote. The builder then runs these vets and refuses
on any hit:

- the leak probe reads 0 task IDs and 0 fix lines outside the reverted files, and sees them in an unredacted
  control copy;
- an object-level vet: `git cat-file --batch-all-objects --batch-check` lists every object, and no blob equals the
  post-image of any reverted file (sha comparison against each fix's post-image blobs);
- `.git/objects/info/alternates` is absent and `git remote` is empty.

Redaction deletes ledger shards, handoffs, items and arena `trial_tasks.json` / `selftest_arena_trial.py` from the
snapshot. That may break tools the arms run (trio's `TRIO_RIMFLOW_CMD`) and selftests. Launch blocker P8 checks
that the snapshot's own suite and rimflow still run.

**Dependencies and dispatch order.** The 13 tasks touch disjoint files, so none needs another's fix to start. Every
task's base is the redacted snapshot plus whatever has already landed on integration main when the task is handed
out. A dependency declared in the workload manifest makes a task givable only once its dependency has LANDED on
integration main; finishing on a stream is not enough. There is one seeded permutation of the 13 tasks (seed
`20261101`). It is the same for every arm, every N and the control. A stream takes the first givable task in that
order. Part One keeps the replay's serial order.

**A task already green at dispatch.** Before handing a task out, the dispatcher runs its hidden check on the
current integration main. If it is already green (a sibling's fix closed it), the task is not dispatched and is
recorded `pre_green`. It scores as accepted only if it is green on the final integrated tree. The family
sensitivity in the rule keeps this from deciding a verdict on its own: the verdict is computed on all 13 tasks and
on the 10 without the family, and if the two differ the cell reads hold, flagged `family_confounded`.

**Fan-in.** Every accepted commit is landed on one integration repo per run, in completion order:

1. Cherry-pick `base..sha` onto a candidate branch.
2. On a conflict, a keyed `fanin_merge` model call resolves it. If the result is empty, the step skips it.
3. Rerun the hidden check of every task landed so far on the candidate tree, not only the new one.
4. Fast-forward main only if every check is green. Otherwise the new task is marked a semantic regression and gets
   one keyed rework attempt.

The same fan-in runs at N = 1, so the control pays the same integration cost.

**Counting.** For each run: tasks offered, accepted, pre_green, judge-rejected, abandoned, attempts, rework,
textual conflicts, semantic regressions, and every merge and rework call's tokens and time. All of it is charged to
the arm.

**Accepted per hour, end to end.** An accepted point is a task that has landed on integration main and whose hidden
check is green on the final integrated tree at drain. Acceptance is accepted points divided by the WORKLOAD SIZE
(13, or 10 without the family; 25 or 10 in Part One), never by the tasks offered. So a run cut off at 12 h does not
shrink its own denominator. The clock runs from the first dispatch to drain or to the cutoff, whichever comes first.

**Cutoff and drain.** At the cutoff the dispatcher stops handing out work, every in-flight model pass is killed,
and nothing more is landed. Drain means: the final integrated tree is exported, and every task's hidden check is
run on it once. Work unfinished at the cutoff scores 0.

Waits are reported separately and never subtracted: fan-in queue, judge queue, test queue, dependency idle (a stream
with no givable task) and runway wait (a stream refused at admission).

## 7. Decision rule, declared before launch (condition 7)

The rule is
`D:\Luke\dev\RimMandrake\design\RimMandrake\parallel_add_on_decision_rule_2026-11-01.json`, version 2, sha256
`fc78e3632c9f0cb94e23f480e6611f850516ce7cfb32d1a60668c5fe2128c817`. The hash is recorded in the ledger. It supersedes version 1
(sha256 6f63f192...ba6dc), which the audit found had no Part One rule and an ambiguous shape; the trial had not
launched. The analysis refuses to score against any rule whose hash differs.

Aggregation (both parts). The cell and its control are paired within each block. Pooled figures are ratios of
sums over the blocks: acceptance = sum accepted / sum workload size; accepted per hour = sum accepted / sum wall
hours; cost per point = sum ITE / sum accepted. The speedup and the cost ratio are cell over control, both pooled.
The worst-block drop is the largest per-block drop. An invalid run is rerun once; invalid twice, the cell is
unmeasured.

**Part Two, per (arm, N) against that arm's same-block N = 1 control:**

- **Escalate to the next N** when all hold: pooled acceptance drop at most 0.10, worst-block drop at most 0.20,
  speedup at least 1.30, cost ratio at most 1.50. At 13 tasks and 2 blocks, one task is 0.077, so the pooled bound
  allows at most 2 lost task-slots of 26, and the worst-block bound at most 2 lost tasks of 13.
- **Stop** when the pooled acceptance drop is more than 0.20, or the speedup is below 1.10.
- **Otherwise hold:** report the previous passing N as the measured setting and go no higher.
- **Family sensitivity:** if the verdict on all 13 tasks differs from the verdict on the 10 without the family, the
  cell holds.

Only escalate counts as a pass; hold and stop are both not-pass. A ceiling is claimed only when one N passes and the
next one stops. A hold at the next N reads "highest passing N = k; next N held; no ceiling claim". A pass at N = 4
reads "no ceiling found up to 4", never "4 is the ceiling".

**Part One, per arm, H = 2 against the same-block H = 0 control:**

- **Helpers help** when all hold: pooled acceptance drop at most 0.04 (one task in 25), worst-block drop at most
  0.12, either a speedup of at least 1.20 or an acceptance gain of at least 0.08, and a cost ratio of at most 1.50.
- **Helpers hurt** when any holds: pooled acceptance drop more than 0.08, cost ratio more than 2.00, or speedup
  below 0.80.
- **Otherwise:** no measured effect.

Part One does not gate Part Two. Part Two keeps H = 2 for every arm.

The owner may change any threshold before launch only, which changes the hash, and the new hash is recorded in the
ledger. The 1.50 cost bound is the throughput-against-cost tradeoff that `arms.md` said the old rule lacked.

## 8. Offline rehearsal

### 8a. Machinery (all four arms, N = 1 and 2, six toy tasks, stubbed models)

**Driver.** `D:\ClaudeWork\rimmandrake\parallel_add_on\rehearsal\rehearse.py`, sha256 1dca7b8c...fa5fd2. It drives
the real loop classes on throwaway roots: `ralph_a_loop.Loop`, `trio_loop.TrioLoop` (stub critic),
`v3_control.Procedure`, and `ralph_c_loop.LoopC` with its `Board`. Model calls are stubbed. Each stub sleeps, then
writes both the keyed record and the meter record.

**Toy workload.** Six tasks: a pair that conflicts textually (TOY_HELLO and TOY_BYE); a pair that conflicts
semantically (TOY_UNITS_CM and TOY_LABEL); and a dependency (TOY_TOTAL depends on TOY_PARSE, whose first build is
wrong). All 15 checks passed
(`D:\ClaudeWork\rimmandrake\parallel_add_on\evidence\rehearsal\rehearsal_report.json`):

| Arm | N=1 accepted | N=2 accepted | N=2 conflicts | N=2 speedup | N=2 cost per point |
|---|---|---|---|---|---|
| ralph_a | 6/6 | 6/6 | 1 textual (fixed), 1 semantic (rework) | 1.52 | 1.18 |
| trio | 6/6 | 6/6 | 1 textual (fixed), 1 semantic (rework) | 1.57 | 1.18 |
| v3 | 6/6 | 6/6 | 1 textual (fixed), 1 semantic (rework) | 1.43 | 1.16 |
| ralph_c | 6/6 | 6/6 | none: its areas keep HELLO and BYE on one member | 0.98 | 1.00 |

These numbers test the machinery, not the arms. Its limits, which the audit found:

- It never varied H. The stub helper returns "no idea" (`rehearse.py:176`), so Part One was not exercised.
- It ran ralph_c's two members interleaved in one process, so ralph_c's 0.98 means nothing.
- Its spend check is circular (section 5).
- Its `unfinished_at_cutoff_scored` is the constant 0 (`rehearse.py:550`); the cutoff path never ran.
- Its waits cover only the fan-in queue and the judge.
- It ran blocks of one, with the control in its own block.
- It applied a toy rule (`evidence\rehearsal\decision_rule.json`, binary escalate/stop). That is why 8b exists.

Bugs it found, each now a spec item in section 10: **(a)** if the integration repo is cloned while HEAD sits on the
candidate branch, the clone has no `main`, so always clone with `-b main`; **(b)** a ralph_c member stays on
`ralph/wip` after a publish, so its base goes stale (5 false conflicts at N = 1), and it needs a sync that resets wip
to main when nothing is unpublished; **(c)** the board's "done" must mean landed; **(d)** `v3_control.Procedure`
takes one flock per arm, so a second v3 stream is refused (`v3_shared_lock_refuses_second_stream`), and each stream
needs its own `V3_LOCK_DIR` and `ARENA_ROOT`; **(e)** the cherry-pick continue step fails on an empty pick, so skip it.

### 8b. The real rule file, offline

`D:\ClaudeWork\rimmandrake\parallel_add_on\rehearsal\rule_rehearse.py`, sha256 8bf3f2ab...3758f7. It reads the
launch rule file itself (every threshold, workload size and family list) and refuses if its sha256 differs from the
declared one. It feeds the rule synthetic multi-block summaries, each built to land one branch. All 25 checks
passed (`D:\ClaudeWork\rimmandrake\parallel_add_on\evidence\rehearsal\rule_rehearsal_report.json`).

The cases cover:

- Part Two escalate; hold on speed; hold on cost; stop on speed; stop on drop.
- A worst-block hold (one block loses 3 of 13); one lost task per block still escalates.
- A cut-off control whose denominator stays 13.
- An invalid run that is rerun and scored; a run invalid twice, so its cell is unmeasured.
- The family sensitivity turning an escalate into a flagged hold.
- Fewer than 2 blocks, refused; ralph_c N = 4, not measured.
- Ladder wording: green at 4 is "no ceiling found", hold is not a pass, and a ceiling is claimed only on a stop.
- Part One help by speed, help by acceptance, hurt by drop, hurt by cost, and no effect.
- A mutated rule file, refused.

This proves the rule's shape and branches. It does not prove the real analysis module, which does not exist yet.

## 9. Launch blockers (run on the real machine before block 1; any red one blocks launch)

0. **Pin.** The dedicated clone exists. The full section 3 manifest is written at start and end of a dry run and is
   identical. A one-byte change anywhere in the tree, a changed env key or a changed tool version is refused.
1. **Agent tool in the sandbox.** The Agent tool works inside the bubblewrap arm sandbox. Without it, H = 2 is a
   promise nothing can keep.
2. **No slot hook.** `.claude/hooks/block_agent_over_slots.py` does not fire inside the trial clones.
3. **Critic spend.** The critic's real-HOME transcripts are counted. One keyed call through each critic reconciles.
4. **Memory at N = 2.** Peak anonymous memory of one block at N = 2 (8 runs) under heavy tests fits the slices.
   Measure anon memory, not page cache.
5. **Account.** Account failover is not set to switch accounts automatically during the run; an automatic switch
   closes every Claude window. Record the starting account and its usage, so a mid-run switch is detected
   afterwards.
6. **Leak.** The snapshot leak probe reads 0 task IDs and 0 fix lines outside the reverted files, and the same
   probe sees them in an unredacted control copy.
7. **Helper keying.** One Agent-tool helper call inside the sandbox lands as role=helper with a full key and its
   parent id, and reconciles at record level. Record whether the CLI envelope's `modelUsage` includes the
   sidechain (section 5).
8. **Snapshot reproduction.** On the 13-revert tree, for each task:
   - its hidden check is RED;
   - it is GREEN with only its own fix re-applied;
   - it is still RED with every OTHER fix applied (leave-one-out, which catches the family and the shared-file
     cases);
   - all 13 fixes together turn all 13 GREEN;
   - the remaining selftests are unchanged between the pin and the reverted tree.

   Also run the object-level vet and the fresh-repo checks (section 6), and confirm the snapshot's own suite and
   rimflow still run after redaction. A task that fails a per-task step is dropped, and the rule is re-declared
   with the new workload size before launch.
9. **Sandbox reach.** From inside the arm sandbox, `/home/mandrake/rm/parallel_trial_pin` (which holds full
   history), every integration repo, every other run's root and the replay root are invisible.
10. **ralph_c.** `RALPH_C_MAX_SUBAGENTS` equals H for each cell; the trial copy of `PROMPT_C.md` has no R6 grant;
    `areas.json` homes all 13 (and, for Part One, all 25) tasks with no refusal at load.
11. **Load at N = 4.** Probe 4 repeated at the N = 4 block load (4 x 5 builders plus helpers), for memory. Measure
    account burn (percent of the 5-hour window per hour) at that load too.
12. **Real modules.** The rehearsal is rerun against the real modules of section 10 in place of the scratch
    driver, and 8b is rerun against `arena_analysis.py`'s implementation of the rule. Both green.
13. **Fan-in cost.** The estimated fan-in hidden-check time per run (from P8's check timings) is under 10% of the
    cutoff.
14. **Runway estimate.** The total wall and account burn for Part One and Part Two, from P11 and the replay's wall
    times, written down. Part One's fallback subset is used if Part One does not fit.

## 10. Code changes needed (spec only; this item edits no harness code)

1. **Execution key.** `RM_EXEC_KEY` is set on every `claude -p` process by every loop, and written to each spend
   record (in `arena_spend.py` and the model callables in `ralph_a_loop`, `trio_loop`, `v3_control` and
   `ralph_c_loop`).
2. **Helper keying and overstep scan.** Transcript sidechain keying (section 5) in `arena_spend.py` /
   `helper_capture.py`. The scan voids a run on a helper commit and counts helper build/test calls.
3. **Reconcile.** Record level per pass (envelope against census) and account level per block (report only).
4. **Per-stream v3 scope.** Per-stream `V3_LOCK_DIR`, `ARENA_ROOT`, `require_tested` state and pidfile. Each
   transition carries an explicit task, attempt and build id, and completion is idempotent (codex finding 5).
5. **Event order.** A sequence number in every event (`arena_eventlog.py`, after its current owner commits), so
   order does not rest on file position.
6. **Add `ralph_c` to `REPLAY_ARMS`** (`arena_replay_run.py:69`), with `_par` arm names for the trial.
7. **Snapshot builder.** It reverts the 13 fixes onto the pin, writes a fresh one-commit repo, deletes or redacts
   the ID-leak files of section 1, and refuses on any vet hit (section 6).
8. **Fan-in module** (`arena_fanin.py`): cherry-pick, keyed merge, rerun every landed check, fast-forward only when
   green. Clone with `-b main` (bug a); skip empty picks (bug e).
9. **Dispatcher.** It follows the seeded order. A task is givable only when its dependencies have landed (bug c).
   It runs the pre-green check, and each stream reserves runway spend at admission.
10. **ralph_c sync hook.** When a member is on wip and nothing is unpublished, rebase it onto integration main
    (bug b). Run members as real separate processes.
11. **Analysis** (`arena_analysis.py`): the rule loaded and checked by hash. It must cover pairing, pooled ratios of
    sums, workload-size denominators, family sensitivity, hold-is-not-pass, accepted per hour end to end, and waits
    broken out. `rule_rehearse.py` (8b) is the reference implementation and its cases are the selftest.
12. **ralph_c N members.** Generalise `ralph_c_loop`'s two-member list to N members (areas, board, R2 steal, R4
    back-pressure). Without it, ralph_c@N4 reads not_measured.
13. **Pin manifest** written at the start and end of each run (section 3). A mismatch makes the run invalid.
14. **Block scheduler.** It starts the block's 8 runs at once, in the seeded slice assignment. It sets up the
    per-arm child slices and their cell/control sub-slices under `rm-harness.slice`, and applies the N = 4 runway
    gate.
15. **Heavy-lane queue.** Round-robin across the runs of a block, FIFO within a run.
16. **Wait instrumentation.** Queue length and service time for the test lane, the judge and fan-in; dependency idle
    and runway wait per stream.
17. **Cutoff and drain** (section 6): stop dispatch, kill in-flight passes, export the final tree, run every hidden
    check once.

## 11. Checklist: the seven conditions

"Exercised" lists only evidence that actually ran the thing. Every gap is a launch blocker from section 9.

| # | Condition (codex_review.md:111-117) | Designed in | Exercised so far | Status | Owed before launch |
|---|---|---|---|---|---|
| 1 | Pin the experiment | Section 3 | Refuse-on-change logic, on a narrower manifest (live tree, arena-only dirty check, no tools or env): `pin_mutation_refused`, `pin_unchanged_over_run` | PARTIAL | P0 |
| 2 | Fresh control; helper effects split from stream effects | Sections 2, 7 | Part Two machinery at N = 1 vs 2 on toy tasks (`every_arm_both_n_ran`). Part One rule branches offline (8b `p1_*`). H was never varied with a real helper | PARTIAL (Two) / NOT EXERCISED (One) | P1, P7, P10, P12 |
| 3 | Resource envelope; contention controlled | Section 4 (same-block control, slices, round-robin heavy lane, waits, N = 4 runway gate) | Nothing: no scheduler, slices or shared queue ran | NOT EXERCISED | P4, P11, P12, P13, P14; code changes 14-16 |
| 4 | Valid cumulative workload with integration | Sections 1, 6 | Textual revert (13, one at a time and together), disjointness among the 13, leak floor (`snapshot_revert_probe.json`, `snapshot_leak_probe.json`). Fan-in on toy tasks (`textual_conflict_seen_and_fixed`, `semantic_regression_seen_somewhere`). Reproduction NOT shown | PARTIAL | P6, P8, P9 |
| 5 | Accepted per hour end to end | Section 6 (workload-size denominator, cutoff/drain, five waits) | Accepted per hour and two of five waits on toy runs. Cutoff path never ran (constant 0). Workload denominator for a cut-off run, offline (8b `p2_cutoff_denominator_is_workload`) | WEAK | P12; code changes 16, 17 |
| 6 | Spend reconciled completely, critic gap included | Section 5 (transcript keying of helpers, record-level envelope check, per-block account check, unkeyed voids) | `reconcile()` logic only: the red cases for a dropped critic record, a duplicate and an empty key. The green case is circular (same writer) | LOGIC ONLY | P3, P5, P7 |
| 7 | Decision rule declared and hashed | Section 7: rule v2 with both parts, pooling, worst block, hold-is-not-pass, family sensitivity | The real rule file, all branches, offline, with hash refusal (8b, 25/25: `rule_rehearsal_report.json`). Hash in the ledger | DONE offline; real module owed | P12 |

Evidence paths are under `D:\ClaudeWork\rimmandrake\parallel_add_on\evidence\`.

## 12. Owed

- Launch blockers P0 to P14 (section 9).
- The code spec in section 10.
- If P8 drops a task, or the owner changes a threshold: re-declare the rule, re-hash it and record the new hash in
  the ledger, before launch.
