# Parallel review: the arms (PARALLEL_BUILD_REVIEW_DEFEND_EVERY_LIMIT)

STATUS: complete. Read-only review, not committed. Replay was running and was not touched.
Evidence window: 2026-10-31, about 15:54 to 16:15 PDT, arms started 15:47:33. All arms were still on task 1 of 25,
so every run measurement below is an early sample, and is labelled as one.

Owner's test, applied to every limit: "any decision we make that is shown to simply limit progress, productivity, or
parallel construction should be immediately attacked to force it to defend its requirement."

Code paths are under `src/RimMandrake/Utils/arena/` unless given in full. Design paths are under `design/RimMandrake/`.

## Verdict in brief

1. **The running replay has no parallel construction in any arm.** One task at a time per arm (enforced), one agent at
   a time per task (by loop structure and practice). 0 Agent calls and 0 subagent transcripts in 62 main transcripts.
   The one arm designed to run in parallel, ralph_c, is not in the replay.
2. **The verdict cannot see parallelism, and would punish it.** The rule scores acceptance and accepted points per
   token; the clock is never read. The design's rank-1 measure, accepted points per arm-hour, is not computed. A
   parallel design would pay the extra tokens and earn nothing for the speed.
3. **The reason for serial running is the meter, not any design need.** It can be removed with a per-call task key.
   The rest of the serial machinery is arm-wide scoping that has per-stream forms already in the repo.
4. **Nobody has measured merge cost.** Every arm works from a separate fresh clone with publishing stubbed out, so no
   collision can occur. Any parallel throughput figure is overstated until a fan-in step is measured.

The replay's result is valid as an answer to a narrower question: which architecture gives the best serial accepted
work per token. It must not be read as the answer to the owner's question. **A win must not switch production on its
own** (the design says a win switches at once: `ralph_loop_design_2026-10-29.md:514`, `testpilot_merged_2026-10-29.md:417`).

## Levels of parallelism used here

| Level | Meaning |
|---|---|
| L1 within-task | agents working at once on one task (subagents, or two builders) |
| L2 across-task | tasks in flight at once within one arm |
| L3 across-arm | arms running at once. Harness concurrency, not an architecture property |

## A. Did the test include parallelism?

| Design | Where it was tested | L1 within-task | L2 across-task | Designed or side effect |
|---|---|---|---|---|
| ralph_a | replay, running | 1 in practice. No code block; `ralph_a/PROMPT.md` says no "another model" | 1 | L2 harness-imposed. L1 is mixed: policy "One item per build pass" (`ralph_a/POLICY.md:4`) is designed, no subagent is a side effect of prompt wording |
| trio | replay, running | 1 at a time: builder then critic in sequence. `architecture_switch_harness_2026-10-29.md:26` describes them "as subagents", but `trio_loop.py` runs them as serial processes | 1 | L1 designed as separate roles, serial as a side effect of the loop |
| v3 (control) | replay, running | 1 by practice. `v3/BRIEF.md` is silent on subagents | 1, enforced by arm lock `v3_control.py:317-318,485-529` | Side effect. Production v3 is parallel (see below), so this control is not production's shape |
| ralph_c | excluded: `REPLAY_ARMS = ("ralph_a","trio","v3")` `arena_replay_run.py:50`. Era-0 log has 27 live-only events and no scored replay | Designed 1 builder + up to 4 read-only subagents: `ralph_c_loop.py:36-38,78`; `ralph_c/PROMPT_C.md:10` | Designed 2 builders, Board with stealing `ralph_c_loop.py:145-265` | Parallelism designed, never scored |
| v3c | dropped 2026-10-31, owner decision (`architecture_switch_harness_2026-10-29.md:24-26`) | not tested | not tested | n/a |
| A+sub, C+sub | simulator only (`ralph_loop_design_2026-10-29.md:411-413`, `:461-462`) | assumed factor r_par 1.2-2.5, r_par_ite 1.0-1.3 | n/a | Assumption, not measurement: "Whether r_par is 1.2 or 2.5 is unknown" (`:511`) |
| B, AB_test, AB_build | simulator only (same doc, `:246`, about `:408`) | AB_test splits build and test | AB_build two builders on one plan, collisions assumed b_collide 0-8% | Assumption. Two builders about 1.8x A is flagged low trust by the doc itself |

Measured from the running replay:

- All three arms logged `plan 25 tasks` and started task 1 `RP_DEPLOY_PRUNE_DELETED_FILES_STALE_ASH_LADDER` at
  15:47:48-49, same order.
- `arena_replay_run.py:4-5`: "the replay arms run in parallel; the spend meter attributes calls by per-arm task spans,
  so WITHIN an arm the tasks run strictly one after another." L3 = 3, L2 = 1, stated cause: the meter.
- `v3.jsonl`, 22:49:29Z to 22:53:31Z, 6 events. `ctl/v3/log` holds build.0, test.1.*, build.2: strictly serial, and
  `pass.pid` showed one role at a time.
- Transcript census over `/home/mandrake/rm/arena/sandbox` (22 scratch dirs) plus meter helpers: 62 main transcripts;
  Bash 474, Read 16, Write 14, Edit 6; 36 multi-tool turns; **Agent/Task calls 0; subagent files 0**. Sanity probe: the
  same tool on a FOUNDRY session saw Agent 1 and 7 subagent files, so the instrument can see. Sample is small and early.
- `ralph_a`/`trio`: no era-1 events file at 15:53 although `loop.lock` existed from 15:49. Cause UNMEASURED.
- No tool restriction exists: a search for disallow/allowedTools/tools across loops, sandbox, replay and judge found
  nothing. `arm_sandbox.py:99` even passes `RALPH_C_MAX_SUBAGENTS`. So the Agent tool is not disabled in code. Whether
  it would actually work inside the bubblewrap sandbox is UNMEASURED.

Production v3 against the control:

- `rimflow_v3_workflow_as_built_2026-10-29.md:173`: 2 helpers at once across all roles; `:174`: headless roles run none
  until `HELPERS_BUILD_SHARED_CAP_ACROSS_ROLES` closes; Conductor unlimited for 20 minutes after the owner's last word;
  FOUNDRY gets the machine's helper budget from `slot_allocator`; `:290` full belt.
- `testpilot_merged_2026-10-29.md:227`: launches ran about 3x higher while the owner was present.
- The replay control runs none of that. If v3 loses, it may have lost as a serialised version of itself.

## B. Would each design hold up under parallel build and fix?

| Concern | ralph_a | trio | v3 control | ralph_c |
|---|---|---|---|---|
| Worktree | Own clone per task, single `ralph/wip` branch per clone. Safe across tasks, unsafe for two builders in one clone | Same | Own clone; one `Procedure.work` per clone (`v3_control.py:15`) | Own clone per member. Built for this |
| Lock | `loop.lock` per ctl (`ralph_a_loop.py:1077`); replay uses a per-task ctl, so it does not block | `trio_loop.py` same family | **One lock per arm whatever `--ctl` says** (`:317-318`, `:485-529`): a second stream is refused outright | Per member, Board flock |
| Test-before-next-build gate | `require_tested` over the records it is handed (`ralph_a_loop.py:192-203`). `untested_builds` itself is per task+build; the arm-wide scope is the loop's filter | All-arm scope (`trio_loop.py:84`) | **Arm-global** (`v3_control.py:143-155`): one untested build anywhere refuses every brief; a procedure killed between build_end and test_start blocks the arm | Per member (`ralph_c_loop.py:279-290`). The correct model |
| Merge | Production: `default_sync` pull --rebase and ff-only publish (`ralph_a_loop.py:708-758,1101-1103`). Replay: `publish_cmd="true"`, `sync=None`, so unused | Same stub | Separate path, unused in replay | No merge code found; the area split avoids merges and the gate refuses out-of-area edits. Collisions on steals are assumed, unmeasured |
| Verdict ordering | `arena_eventlog.py:1418` orders by 1 s timestamp, ties by file order | Same | Same | Runner uses file position, not ts (`ralph_c_runner.py:81-106`). Correct pattern |
| Event log | Appends are flock'd (`arena_eventlog.py:1353-1354`), safe for concurrent writers | Same | Same; single counter `ctl/v3/n` and single `pass.pid` assume one stream | Stream-aware run_ids |
| Spend | L1 is safe: census counts `/subagents/` transcripts (`sim/spend_census.py:11,98,154,392`). L2 is NOT: overlapping spans go `ambiguous`, task refused | Same | Same | Same break: `arena_spend.py:47-49` names this arm |
| Checker independence | Per build; fresh tester, different agent id. Survives parallelism unchanged | Plus blind critic. Survives | Tester per build. Survives | Survives. Tester dq is per stream (`arena_analysis.py:143`) |
| One-at-a-time assumption | `CmdModel.spawn` single pidfile (`:450-471`) | Same base | Strongest: lock, counter, pidfile | Lowest |

Conclusions:

- **Fair checking is not what stops parallelism.** Tester independence, signed logs and the gate are per-build and
  carry over unchanged. This is the owner's condition ("so long as it's reliable, work is fairly checked") and it holds.
- **Already parallel-safe:** fresh clones per arm and task with a lock per arm+task (`arena_replay.py:259-299,592`),
  log appends, within-task spend capture, judge flock (`arena_judge.py:295`), dynamic planner guard treating held
  tasks as not done (`arena_rounds.py:8-14`).
- **Breaks under L2:** spend attribution (all arms), v3 arm lock and arm-global gate, single counter and pidfile per
  ctl, 1 s ordering across streams.
- **Unknown under L2:** real merge conflicts and rebase-and-retest cost. No arm has ever produced that data.

## C. Could the verdict mislead?

Yes, in five ways, stated plainly.

1. **The score reads no clock.** `arena_analysis.py:96,105,1578` say the wall clock is never read; a search for
   arm-hour, serial, runtime, duration, per_hour found no throughput measure. Yet
   `architecture_switch_harness_2026-10-29.md:299-302` ranks accepted points per arm-hour first. The stated measure
   is unimplemented. Two arms with equal tokens and acceptance tie even if one finishes in a third of the time.
2. **The score is structurally anti-parallel.** Subagent tokens are charged, speed is not credited. Any duplicated
   context lowers points per token. An arm that used helpers well would look worse than if it had not.
3. **An arm that ran tasks concurrently would be voided.** `arena_analysis.py:643-647` refuses tasks with ambiguous
   calls; `:170` and `arena_spend.py:47-49` say so outright. That is why ralph_c cannot be scored as designed.
4. **Allowance is not equal across arms.** ralph_a and trio are told no "another model"; v3's brief is silent. Effect
   so far: none (0 calls). If a v3 builder uses helpers later, v3 bears the token cost alone.
5. **The control is not production, and the tie-break leans serial.** Control v3 is serialised. On a tie the simpler
   arm wins, in the order ralph_a < ralph_c < trio < v3c < v3 (`arena_analysis.py:235`). Simplicity is measured with
   parallelism out of the picture, and the prior adds to this only through capacity (`RALPH_A_CAPACITY=0.5`, `:250`),
   which comes from the serial simulator.

What the verdict still supports: accept rate and serial token cost per task are honest, since all three arms get
identical tasks, order and serial constraint. Serial skill may also predict parallel skill, but that is UNMEASURED.

Also unequal: all three arms share one memory slice and one account runway (L3). Whether contention hits arms unequally
is UNMEASURED; the wall clock is not scored, so a slowdown does not change the score unless a task times out or an arm
hits the runway wait.

## Limits attacked

| # | Limit | What it limits | Requirement claimed | Survives? | Ruling |
|---|---|---|---|---|---|
| 1 | Tasks strictly serial per arm (`arena_replay_run.py:4-5`) | L2 in every arm | Spend meter needs non-overlapping spans | No. Measurement convenience, and sessions already record their clone (`spend_census.py:62,77-79,375-382`; scratch dirs carry task+sha) | **Remove** in add-on, via limit 2 |
| 2 | Spend attribution by time span (`arena_spend.py:16-17,47-49`) | Any scored concurrency | Calls have no task key | No. Doc itself calls it residual "until calls carry a task/execution key" | **Remove**: attribute by clone/sandbox owner of the session |
| 3 | No clock in the rule (`arena_analysis.py:96,105,1578`) | Any credit for speed | Clock independence, so harness delays cannot sway the score | Partly: raw wall clock is noisy under shared capacity. Design's rank-1 measure still has to exist | **Loosen**: report accepted points per hour alongside, with test-queue and runway waits broken out. Leave the current trial's rule frozen |
| 4 | v3 one lock per arm (`v3_control.py:317-318`) | L2 in v3 | require_tested → brief → test must not interleave in one signed log (review r2) | Only the ordering need. Appends are already flock'd; interleaving matters only within a stream | **Loosen** to per stream |
| 5 | Arm-global require_tested (`v3_control.py:143-155`, `trio_loop.py:84`, ralph_a's filter) | L2; one dead pass blocks an arm | Nothing builds on untested work | Yes per stream, no arm-wide. ralph_c already scopes per member | **Loosen** to per task/stream. Keep the test-first rule itself |
| 6 | Fresh, separate tester | Nothing in throughput except queue depth | Checker independence | Yes | **Keep**. Owner's condition |
| 7 | Single `n` counter and `pass.pid` per ctl | L2 in one ctl | One pass at a time | No; a local assumption | **Loosen**: per stream or per-task ctl |
| 8 | 1 s event ordering (`arena_eventlog.py:1418`) | Reliability under concurrency | Timestamps suffice | No for concurrent streams | **Loosen**: sequence or file position, as `ralph_c_runner.py:81-106` does |
| 9 | ralph_c absent from replay (`arena_replay_run.py:50`) | The only designed-parallel arm is unscored | Meter cannot score it; live-only design | No, once 2 is fixed | **Remove** in add-on |
| 10 | "Do exactly one thing"; "no another model" (`ralph_a/PROMPT.md`, `trio/PROMPT.md`, `TESTER.md`) | L1 in ralph_a, trio | One task per loop keeps context clean (Huntley, `ralph_loop_design:44`) | One item: yes. No helpers: no. Huntley: "Many subagents may search and write, but only one runs build and test", `:38-41` | **Keep** one item; **remove** the helper reading for builders. Tester: keep alone, UNMEASURED whether helpers would harm it |
| 11 | ralph_c subagents read/search only, max 4 (`PROMPT_C.md:10`, `ralph_c_loop.py:36-38`) | Parallel writing | Builder alone edits, builds, tests | Narrower than the source design; prompt-level only. No evidence either way | **Loosen** in the add-on: test write subagents, one runner of build/test. Keep 4 as a test value, not a rule |
| 12 | Two builders, area split (`ralph_loop_design:279`) | L2 to 2, and to work by area | Avoid collisions | Collision rate assumed 0-2%, never measured | **Loosen**: test N = 2 and 4; let the conflict data set N |
| 13 | Sibling order (`arena_rounds.py:8-14`) | L2 on related tasks only | A task must not run before the fix it builds on | Yes: base-commit validity, and limited to siblings | **Keep** |
| 14 | One live driver per game (`architecture_switch:239,624`) | Live lanes | Physical: one game per machine | Yes | **Keep**. Not in the replay. It must stay out of the offline build limit |
| 15 | ralph_a loop WAITS on lane (`ralph_a/POLICY.md` rule 7) | The whole loop while a lane is busy | Live test before proceeding | Applies to that task, not the loop | **Loosen**: park the task, take another. Not exercised in replay |
| 16 | `rm-harness.slice` 12G | Total concurrent test load | Protect seats from OOM (`single tests reach 5.1 GB`) | Purpose yes; number untested. Slice sits at its cap, but anon was 0.37G, file cache 11.7G: the pressure is reclaimable cache. `oom_kill` 38 unchanged through 12:06 and now. Peak anon under test: UNMEASURED | **Keep** the guard; **loosen** the number only from measured peak anon, not from page cache. The cap is not the limit today |
| 17 | Runway floor 0.15, wait 600 s (`ralph_a_loop.py:533-550`, `arena_replay_run.py:54`) | All work when the account is low | Do not exhaust the owner's account | Purpose yes. Effect on parallel burn UNMEASURED; parallel arms hit it faster | **Keep**; re-test once N > 1 |
| 18 | Selftests one-at-a-time heavy lane, 6 workers (`run_selftests.py:139,166-169`) | Test speed | 8 workers no faster (MEASURED 2026-10-08, 298 s against 307 s); timeouts under load | Yes for one run. Concurrent runs across streams UNMEASURED | **Keep**; measure in add-on, as it may be the real choke |
| 19 | Owner's cap of 2 helpers; headless roles none until `HELPERS_BUILD_SHARED_CAP_ACROSS_ROLES` closes (`rimflow_v3_workflow_as_built:173-174`) | Production L1 | Shared capacity. His own ruling, though the blanket headless zero is a pending-build state, not a need | The cap needs evidence under his new ruling; the zero does not survive | **Attack**: Conductor to put the add-on's numbers against it. Do not change it from this review |
| 20 | `session_helpers_max` 3, read by no program (`rimflow_v3...:175`) | Nothing | None | Dead setting | **Remove** or wire |
| 21 | Task caps: `ROUND_CAP=4`, `CRITIC_TRIES=2`, `MAX_TRIES=3` | Retries, not concurrency | Bound spend per task | Yes. Not a parallel limit | **Keep** |
| 22 | Replay publish stubbed (`arena_replay_run.py:11-16`) | Hides merge cost; flatters parallel | Keeps tasks independent and comparable | Yes for the serial trial; fails for any parallel claim | **Keep** here; add a fan-in step in the add-on |
| 23 | `.claude/hooks/block_agent_over_slots.py` | Helpers in seats | Seat budget | Should not apply: replay cwd is not `/rm/bench` or `/rm/foundry`, and other seats are allowed. Whether the hook loads in clones: UNMEASURED | **Keep**; add-on must confirm it does not fire |

## Smallest fix

Do not touch the current replay. Let it finish and read it as serial evidence only.

**1. Label now.** Report the replay verdict as "serial accepted work per token". Hold any production switch until the
add-on reports. This costs nothing.

**2. Add-on run.** After the replay ends, or alongside it only if peak anon headroom and runway are measured first.
Use a new root and new arm names (`ralph_a_par`, `trio_par`, `v3_par`, `ralph_c`), never the existing root or logs.
Harness changes need to wait for the replay to end, or live on a separate clone the running arms do not import from.

Required:

- **Same allowance for every arm:** same N streams (start at 2, then 4), same helper allowance and the same wording in
  every prompt. An arm may decline to use it, but it may not be denied it. Probe first that the Agent tool works in
  the sandbox.
- **Same tasks** as the replay, so a task-paired comparison with serial exists. If capacity is short, use the two newest
  eras at N=2 first.
- **Per-call task key** (limits 1, 2): attribute by the session's clone. Ambiguous calls should fall to about zero; if
  not, the fix has failed.
- **Per-stream scope** (limits 4, 5, 7, 8) in the harness's v3 arm.
- **Fan-in step** (limit 22): land each arm's accepted commits onto one main in completion order, rebasing and
  retesting. Record conflict rate and tokens and time of the rework. Charge these to the arm.
- **Checking unchanged:** same gate, judge and tester independence. Any drop in accept rate against the serial replay
  on paired tasks is the reliability price of parallel, and is the key result.

Report per arm and N: accepted points per token, accepted points per hour, accept rate, conflict rate, time in test
queue, and runway burn. The decision then weighs throughput against the accept margin that the rule already sets. The
owner has to set the weight; the existing rule has no term for it.

## UNMEASURED

- Whether the Agent tool works inside the bubblewrap sandbox.
- Why `ralph_a` and `trio` had no era-1 events at 15:53.
- Whether L3 contention affects arms unequally.
- Real r_par, collision rates, merge and rebase-retest cost, in any arm.
- Peak anon memory of the three arms during heavy tests; usable headroom on the 14-core, 35G machine.
- `oom baseline 59` in the replay `progress.md` against the slice's `oom_kill 38`. Unreconciled.
- Parallel runway burn; concurrent selftest behaviour.
- Whether serial rank predicts parallel rank.
- Whether a helper would harm or help the fresh tester.
- Subagent use across the later 24 tasks. The zero here covers task 1 only.
