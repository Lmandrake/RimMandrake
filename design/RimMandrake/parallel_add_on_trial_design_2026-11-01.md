# Parallel add-on trial: design (TRIAL_PARALLEL_DESIGN_ADD_ON_EQUAL_ALLOWANCE)

Owner: "Yes add-on trial." This is the run that follows the serial replay. It answers the open question in
`parallel_review_2026-10-31/arms.md`: what happens to each arm's acceptance, speed and cost once it may work in
parallel. It is built to meet all seven fairness conditions in `parallel_review_2026-10-31/codex_review.md`
(lines 109-117). The checklist at the end maps each condition to its evidence.

Status: designed and rehearsed offline. Not launched. It launches only after the running replay ends. It never
touches the replay's root, its logs or `/home/mandrake/rm/trial_pin`.

## 1. Two facts that shape the design (both measured)

**The 25 replay tasks cannot be run side by side.** Each later task's starting tree already holds every earlier
task's real fix. Sibling containment holds for 300 of 300 pairs: 25 levels, one task per level. So running two
replay tasks at once would hand one of them the other's answer. The replay set can test only parallel work inside a
single task (helpers), not parallel work across tasks (streams).
Evidence: `D:\ClaudeWork\rimmandrake\parallel_add_on\evidence\trial25_sibling_relation.json`. The probe saw both
True and False answers before the count was trusted.

**A cumulative workload can be built from one snapshot.** Taking pin `5330ddf9b5837294344e557e6801767700b52c2e`,
13 of the 25 fixes revert cleanly both one at a time and all together. Those 13 touch no file in common, pair by
pair. Reverting all 13 gives one starting tree that holds 13 open bugs whose real fixes are known. The other 12
conflict or overlap, and are left out.
Evidence: `D:\ClaudeWork\rimmandrake\parallel_add_on\evidence\snapshot_revert_probe.json`.

The 13 are: RP_TESTENV_GUARD_UNSTICK_BLOCKS_ITS_OWN_SEQUEL, RP_ROSTERS_RENAME_MOVED_PORT_NAMES,
RP_SAVE_GUARD_FIX_BOM_READ_AS_BROKEN, RP_ENACT_STALE_KEY_FIX_UNREVIEWED,
RP_VALIDATE_PATCH_DESCENDANT_FIX_FALSE_ZERO, RP_RIMBRIDGE_DEADLINE_FIX_NAN_FAILS_OPEN,
RP_SEAT_SYNC_HARDEN_LITERAL_PATHSPECS, RP_CONVERSATIONS_LAND_FIX_STALE_TRAILER,
RP_SITHLINE_ROUNDTRIP_FIX_INT_WRITTEN_AS_FLOAT, RP_SARLACC_UNMEASURED_FIX_BORROWED_REASON,
RP_BRAINWORMS_VALIDATION_FIX_BORROWED_REASON, RP_GRAFFITIIMPERIAL_VALIDATION_FIX_LOST_REASON,
RP_MODCHECK_HARDEN_RESTORE_RAISE_LOSES_SHEET.

**The snapshot leaks task names, not fixes.** A line unique to a fix never appears outside that fix's own files: 0
hits. The same search does find those lines in 28 files once the fixes' own files are included, so the instrument
works. But each task's ID appears in 5 to 12 other files. They are in `conversations/`; in the ledger shards,
handoffs and items under `infrastructure/state/`; and in the arena's `trial_tasks.json`,
`gate_reference_reds.lock.json`, `prompt_rewrites.json`, `trial_exclusions.json` and `selftest_arena_trial.py`. The
snapshot builder must delete or redact all of these and then rerun the probe until it reads 0.
Evidence: `D:\ClaudeWork\rimmandrake\parallel_add_on\evidence\snapshot_leak_probe.json`. Probe:
`D:\ClaudeWork\rimmandrake\parallel_add_on\leak_probe2.py`, sha256 2e7a1e3b...6904.

## 2. Shape of the trial

Two parts. Each changes one thing, so neither part's effect is mixed into the other (condition 2).

| Part | What changes | Workload | Cells | Control |
|---|---|---|---|---|
| One: helpers inside a task | helper allowance H = 0 vs H = 2, with N = 1 stream | the 25 replay tasks, same order and serial constraint | 4 arms x (H = 0, H = 2) | H = 0 is a fresh N=1 run under the new pin; the old replay is shown for reference only |
| Two: streams across tasks | streams N = 1, then 2, then 4 by rule; H = 2 throughout | the 13-task snapshot workload | 4 arms x (N = 1, 2, then 4 if the rule allows) | N = 1 with H = 2: the same helper permissions and the same acceptance as N>1 |

The arms are `ralph_a_par`, `trio_par`, `v3_par` and `ralph_c`. They get a new root and new arm names, never the
replay's.

**Equal allowance.** Every arm gets the same paragraph, word for word, appended to its builder prompt:
"You may start up to H helper agents at a time. Helpers may read, search and edit files you name. Only you run the
build and the tests, and only you commit." The tester, judge and critic prompts do not change; they stay
helper-free, as in the replay. An arm may decline to use helpers, but it is never denied them. Helper use is
recorded per call (section 5), so a decline shows up as a measured zero.

If runway is short, Part One runs a smaller set that is declared now: the last 10 tasks in the total order. No
subset may be picked after launch.

## 3. Pin (condition 1)

The trial runs from a dedicated harness clone, `/home/mandrake/rm/parallel_trial_pin`, at a recorded commit. It
never runs from FOUNDRY's live tree. Before each run and after it, the harness writes a pin manifest holding:

- the git commit and tree hash of the harness clone, plus the sha256 of `git diff HEAD`, which must be empty;
- the sha256 of every file under `src/RimMandrake/Utils/arena/`, including every prompt (`*/PROMPT.md`,
  `TESTER.md`), `trial_tasks.json` and the workload manifest;
- configuration: the environment keys the harness reads (`TRIO_RIMFLOW_CMD`, `V3_LOCK_DIR`, `ARENA_ROOT`,
  `RM_EXEC_KEY` scheme), the sandbox profile, and the slice limits;
- tool versions: the `claude` CLI (`claude_sha.txt` style), python, git, bubblewrap;
- task inputs: the snapshot commit and the hash of the redacted tree; for Part One, the 25 base revisions;
- the decision rule's sha256 (section 7).

If the manifest at the end differs from the one at the start, the run is invalid and is rerun, not scored.
Rehearsed: a pin mutated in the middle of a run is refused (`pin_mutation_refused`).
Evidence: `D:\ClaudeWork\rimmandrake\parallel_add_on\evidence\rehearsal\pin_manifest.json`.

## 4. Resource envelope (condition 3)

Each cell counts every role, not just builders:

| Role | Slots per cell |
|---|---|
| builder | N |
| builder helpers | N x H (H = 2) |
| tester / critic / judge | 1 per stream, as each arm's own loop starts them |
| fan-in merger (section 6) | 1 shared per arm, charged to the arm |
| controller / dispatcher | 1, with no model calls except keyed ones |
| heavy selftest lane | the existing one-at-a-time lane, shared fairly across arms through one queue |

Cross-arm contention is handled by blocks. One block runs all four arms at the same N together, with equal CPU and
memory shares: four equal child slices under `rm-harness.slice`. Block order is randomized with a fixed seed, and
there are at least 2 blocks per N. So every arm meets the same contention, and repeating blocks gives the spread
the rule uses. Each run records queue length and service time for the test lane, the judge and the fan-in step,
so a cap from the completion side shows up as a wait and not as an unexplained slowdown (codex finding 8).

Runway: the existing floor of 0.15 stays. At admission, each stream reserves its expected next-call spend, so N
streams cannot all pass the same floor check at once (codex finding 4). Before launch, also measure peak anonymous
memory and look at the account failover state; both are listed in section 9.

## 5. Spend: keyed per call and reconciled to the account total (condition 6)

- **Execution key.** The harness sets `RM_EXEC_KEY=arm/stream/task/attempt/role` for every model call, and child
  processes inherit it: helpers, testers, critics and the fan-in merger. Every call writes one keyed record:
  `keyed_calls.jsonl`.
- **Independent total.** A separate meter reads the account's own usage, the transcript census under each run's
  HOME and the critic's real HOME, without trusting the keys: `account_meter.jsonl`.
- **Reconcile.** The keyed records must equal the meter record for record, by call id, with no record missing, no
  duplicate and no key field empty. Calls with no key go to a shared-overhead bucket. That bucket is reported, and
  is charged to arms only by their own measured share. Any mismatch makes the run invalid.
- **Critic gap.** The trio and ralph_a critics run under the real HOME (commit 8ab6ab3eb0,
  TRIO_CRITIC_FIX_HOME_SWAP_HIDES_CLAUDE). Their transcripts are outside the run's HOME, so the meter must read them
  as well. The rehearsal deliberately dropped a critic record, and reconciliation went red.

Rehearsed: reconciliation is green on clean data. It goes red on a dropped critic record, on a duplicated record and
on an empty key field.
Evidence: `rehearsal_report.json` checks `spend_*` and `every_summary_spend_reconciled`, plus the per-arm
`*_keyed_calls.jsonl` and `*_account_meter.jsonl` in `D:\ClaudeWork\rimmandrake\parallel_add_on\evidence\rehearsal\`.

## 6. Workload, fan-in and scoring (conditions 4 and 5)

**Dependencies.** The 13 snapshot tasks touch disjoint files, so none needs another's fix to start. Every task's
base is the redacted snapshot plus whatever has already landed on integration main when the task is handed out. A
dependency declared in the workload manifest makes a task givable only once its dependency has LANDED on
integration main. Finishing on a stream is not enough. Part One keeps the replay's serial order.

**Fan-in.** Every accepted commit is landed on one integration repo per arm, in completion order:

1. Cherry-pick `base..sha` onto a candidate branch.
2. On a conflict, a keyed `fanin_merge` model call resolves it. If the result is empty, the step skips it.
3. Rerun the hidden check of every task landed so far on the candidate tree, not only the new one.
4. Fast-forward main only if every check is green. Otherwise the new task is marked a semantic regression and gets
   one keyed rework attempt.

The same fan-in runs at N=1, so the control pays the same integration cost.

**Counting.** For each run: tasks offered, accepted, judge-rejected, abandoned, attempts, rework, textual conflicts,
semantic regressions, and every merge and rework call's tokens and time. All of it is charged to the arm.

**Accepted per hour, end to end.** An accepted point is a task that has landed on integration main and whose hidden
check is green on the final integrated tree at drain. The clock runs from the first dispatch to drain or to the
12-hour cutoff, whichever comes first. Waits are reported separately and never subtracted: fan-in queue, judge
queue, test queue, dependency idle and runway wait. Work unfinished at the cutoff scores 0.

## 7. Decision rule, declared before launch (condition 7)

The rule is
`D:\Luke\dev\RimMandrake\design\RimMandrake\parallel_add_on_decision_rule_2026-11-01.json`, sha256
`6f63f192dfb4b6c35835e4ca2b4247886afe4a1ba6b013a1b360b0c4b80ba6dc`. This hash is also written to the ledger. The
analysis refuses to score against any rule whose hash differs (rehearsed: `decision_rule_mutation_refused`).

The rule is applied to each (arm, N) cell against that arm's own N=1 control:

- **Escalate to the next N** when all of these hold:
  - the acceptance drop is at most 0.10, and in the worst block at most 0.20;
  - the speedup in accepted points per hour is at least 1.30;
  - the cost per accepted point is at most 1.50 times the control's.
- **Stop** when the acceptance drop is more than 0.20, or the speedup is below 1.10.
- **Otherwise hold:** report this N as the measured setting and go no higher.

A ceiling is claimed only when one N passes and the next one fails. A green result at N=4 reads "no ceiling found up
to 4", never "4 is the ceiling". The owner may change any threshold before launch only, which changes the hash. The
1.50 cost bound is the throughput-against-cost tradeoff that `arms.md` said the old rule lacked.

## 8. Offline rehearsal (all four arms, both N, six tasks, stubbed models)

**Driver.** `D:\ClaudeWork\rimmandrake\parallel_add_on\rehearsal\rehearse.py`, sha256 1dca7b8c...fa5fd2. It drives
the real loop classes on throwaway roots:

- `ralph_a_loop.Loop`;
- `trio_loop.TrioLoop`, with a stub critic;
- `v3_control.Procedure`;
- `ralph_c_loop.LoopC`, with its `Board`.

Model calls are stubbed. Each stub sleeps, then writes both the keyed record and the independent meter record.

**Toy workload.** Six tasks:

- a pair that conflicts textually: TOY_HELLO and TOY_BYE;
- a pair that conflicts semantically: TOY_UNITS_CM and TOY_LABEL;
- a dependency: TOY_TOTAL depends on TOY_PARSE, and its first build is wrong.

The rehearsal passed all 15 of its checks
(`D:\ClaudeWork\rimmandrake\parallel_add_on\evidence\rehearsal\rehearsal_report.json`):

| Arm | N=1 accepted | N=2 accepted | N=2 conflicts | N=2 speedup | N=2 cost per point | Rule |
|---|---|---|---|---|---|---|
| ralph_a | 6/6 | 6/6 | 1 textual (fixed), 1 semantic (rework) | 1.52 | 1.18 | escalate |
| trio | 6/6 | 6/6 | 1 textual (fixed), 1 semantic (rework) | 1.57 | 1.18 | escalate |
| v3 | 6/6 | 6/6 | 1 textual (fixed), 1 semantic (rework) | 1.43 | 1.16 | escalate |
| ralph_c | 6/6 | 6/6 | none: its areas keep HELLO and BYE on one member | 0.98 | 1.00 | stop |

These numbers test the machinery, not the arms: the model calls are stubs. The rehearsal ran ralph_c's two members
interleaved in one process, so its speedup of 0.98 means nothing about ralph_c's real concurrency.

Bugs the rehearsal found. Each is now a spec item in section 10:

- **(a)** If the integration repo is cloned while HEAD sits on the candidate branch, the clone has no `main`. Always
  clone with `-b main`.
- **(b)** A ralph_c member stays on `ralph/wip` after a publish, so its base goes stale. It caused 5 false conflicts
  at N=1. It needs a sync that resets wip to main when nothing is unpublished.
- **(c)** The board's "done" must mean landed, or a dependent task starts on a base that lacks its dependency.
- **(d)** `v3_control.Procedure` takes one flock per arm, so a second v3 stream is refused
  (`v3_shared_lock_refuses_second_stream`). Each stream needs its own `V3_LOCK_DIR` and `ARENA_ROOT`.
- **(e)** The cherry-pick continue step fails on an empty pick. Skip it.

## 9. Launch-time probes (run on the real machine before block 1; any red one blocks launch)

1. The Agent tool works inside the bubblewrap arm sandbox. Without it, H=2 is a promise nothing can keep.
2. `.claude/hooks/block_agent_over_slots.py` does not fire inside the trial clones.
3. The critic's real-HOME transcripts are counted by the meter. Send one keyed call through each critic and check
   that it reconciles.
4. Peak anonymous memory of one block at N=2 under heavy tests fits the slice. Measure anon memory, not page cache.
5. Account failover is not set to switch accounts automatically during the run. An automatic switch closes every
   Claude window.
6. The snapshot leak probe reads 0 task IDs and 0 fix lines outside the reverted files, and the same probe sees them
   in an unredacted control copy.

## 10. Code changes needed (spec only; this item edits no harness code)

1. **Execution key.** `RM_EXEC_KEY` is set per call by every loop, inherited by children, and written to each spend
   record (in `arena_spend.py` and the model callables in `ralph_a_loop`, `trio_loop`, `v3_control` and
   `ralph_c_loop`).
2. **Account meter and reconcile.** An independent meter, including the critic's real HOME, and an exact record
   reconciliation (`arena_spend.py`).
3. **Per-stream v3 scope.** Per-stream `V3_LOCK_DIR`, `ARENA_ROOT`, `require_tested` state and pidfile. Each
   transition carries an explicit task, attempt and build id, and completion is idempotent (codex finding 5).
4. **Event order.** A sequence number in every event (`arena_eventlog.py`, after its current owner commits), so
   order does not rest on file position.
5. **Add `ralph_c` to `REPLAY_ARMS`** (`arena_replay_run.py:69`), with `_par` arm names for the trial.
6. **Snapshot builder.** It reverts the 13 fixes onto the pin, squashes history, deletes or redacts the ID-leak
   files listed in section 1, then runs the leak vet and refuses on any hit.
7. **Fan-in module** (`arena_fanin.py`): cherry-pick, keyed merge, rerun every landed check, fast-forward only when
   green. Clone with `-b main` (rehearsal bug a); skip empty picks (bug e).
8. **Dispatcher.** A task is givable only when its dependencies have landed (bug c). Each stream reserves runway
   spend at admission.
9. **ralph_c sync hook.** When a member is on wip and nothing is unpublished, rebase it onto integration main
   (bug b). Run members as real separate processes.
10. **Analysis** (`arena_analysis.py`): accepted per hour end to end, waits broken out, unfinished work scored 0, and
    the rule loaded and checked by hash. The rehearsal's `reconcile`, `accepted_per_hour`, `decide` and
    `pin_manifest` are the reference implementation.
11. **Pin manifest** written at the start and end of each run (section 3). A mismatch makes the run invalid.

## 11. Checklist: the seven conditions

| # | Condition (codex_review.md:111-117) | How this design meets it | Evidence |
|---|---|---|---|
| 1 | Pin the experiment | Dedicated clone; manifest of commit, tree, dirty patch (must be empty), prompts, config, tools, inputs and rule hash, checked at start and end (section 3) | `...\evidence\rehearsal\pin_manifest.json`; checks `pin_unchanged_over_run`, `pin_mutation_refused` |
| 2 | Fresh N=1 control; split helper effects from stream effects | Part One varies only H at N=1; Part Two varies only N, with H=2 throughout and the same acceptance and fan-in at N=1 (section 2) | `rehearsal_report.json` checks `every_arm_both_n_ran`; `*_N1_summary.json` for every arm |
| 3 | Resource envelope; contention controlled | Every role counted; blocks run all four arms at the same N with equal slices, randomized order, at least 2 blocks; queues measured (section 4) | Section 4 table; launch probe 4 (OWED) |
| 4 | Valid cumulative workload with integration | 13 fixes reverted onto one pin, clean one at a time and all together, disjoint files; dependency-aware dispatch; fan-in reruns every landed check; rejects, conflicts, rework and abandons counted (sections 1 and 6) | `...\evidence\snapshot_revert_probe.json`, `trial25_sibling_relation.json`, `snapshot_leak_probe.json`; checks `textual_conflict_seen_and_fixed`, `semantic_regression_seen_somewhere` |
| 5 | Accepted per hour end to end | First dispatch to drain or cutoff; waits reported, not subtracted; unfinished work scores 0 (section 6) | `*_summary.json` fields `accepted_per_hour`, `waits`, `unfinished_at_cutoff_scored` |
| 6 | Spend reconciled completely, critic gap included | Per-call key inherited by children; independent account meter including the critic's real HOME; exact reconcile; shared bucket reported (section 5) | Checks `spend_green_unmutated`, `spend_red_when_critic_record_dropped`, `spend_red_when_record_duplicated`, `spend_red_when_key_field_missing`, `every_summary_spend_reconciled` |
| 7 | Decision rule declared and hashed | Rule file plus its sha256 in the ledger before launch; reliability margin, worst-block bound, speed and cost terms, escalation ladder 1, 2, 4, honest ceiling wording (section 7) | `parallel_add_on_decision_rule_2026-11-01.json` (sha256 6f63f192...ba6dc); checks `decision_rule_applied`, `decision_rule_mutation_refused` |

`...` stands for `D:\ClaudeWork\rimmandrake\parallel_add_on`.

## 12. Owed

- A review by a fresh Opus that did not write this document. It is not done, because the builder could not start
  subagents.
- Launch probes 1 to 6 (section 9).
- The code spec in section 10, then a rehearsal rerun against the real modules in place of the scratch driver.
- A real concurrency run of ralph_c. The rehearsal interleaved its members.
- Recording the rule hash in the ledger at launch, if the owner changes any threshold before then.
