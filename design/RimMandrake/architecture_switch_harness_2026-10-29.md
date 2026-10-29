# Build them all and switch: a harness that answers architecture questions in days (2026-10-29)

Item `TESTPILOT_DESIGN_PROOF_BEFORE_RELOAD`. Status: DESIGN ONLY. No code, unit, role file or config was changed to
write it. Scratch for this design (the variance script and its output): `D:\ClaudeWork\rimmandrake\harness_design\`.

## 0. The question and the goal

The owner, verbatim, 2026-10-29: "I think we really need some modelling. Maybe some scaled experiments even. Although
these re now so simple maybe we just build them all and see as long s we can easily switch."

And, the same day: "Please do a design pass on how we can best obtain architectural decisions like this without
waiting weeks. I would like to spend days not week nd get rel day driven answers sand guidance."

**The goal of this harness is a real-data answer in three days, not three weeks.** It replaces the simulator's
assumed parameters with measurements, and lets every architecture run for real under one setting, judged by one
acceptance check.

**The five arms:**

| arm id | architecture | source |
|---|---|---|
| `v3` | v3 as it runs today: the control | `rimflow_v3_workflow_as_built_2026-10-29.md` |
| `v3c` | collapsed v3: 4 actors, a done gate, GPT reviews every finished sha | `rimflow_v3_collapse_compare_2026-10-29.md` §6 |
| `ralph_a` | one `loop.sh` on Archmagi, gate run by the loop | `ralph_loop_design_2026-10-29.md` §1 |
| `ralph_c` | two builder loops split by area, plus fixed-SHA live runners on both machines | same doc, §3 (it has landed) |
| `trio` | Conductor + FOUNDRY running a Ralph builder and a blind critic as subagents + a TestPilot per machine | `D:\ClaudeWork\rimmandrake\testpilot\brief.md` |

**Three ideas make days possible. Without them the trial takes weeks:**

1. **The task is the unit, not the day.** Daily closes in the v2 week ran 13, 45, 28, 54, 113, 92 and 446
   (2026-10-20 to 10-26, UTC; mean 113, SD 151, CV 1.34). The 446 is a bulk-close day. With a CV like that, comparing
   arm-days takes months. Comparing matched tasks takes days. (Measured with
   `D:\ClaudeWork\rimmandrake\harness_design\v2_variance.py` over the five ledger shards, 21,948 events read.)
2. **Historical replay pairs each task with itself.** Every arm re-does the SAME past item in a throwaway clone
   checked out at the commit before the original fix. The result is scored against the outcome we already know:
   accepted clean, or shipped with a defect found later. Task difficulty then cancels out of the comparison. That
   is the biggest variance cut available (section 3.5).
3. **The arms run side by side, not one after another.** Replay arms need no live game, so they run in parallel
   in separate clones. The two live arms take one machine each and swap halfway (a crossover). A sequential stopping
   rule ends the trial as soon as the evidence is enough.

**The build half and the live half are measured separately.** The five architectures differ in two places: how
work gets built and judged, and how it gets live-tested. Replay measures the build half in parallel and fast.
Two machines measure the live half. The result for a whole architecture combines the two halves. This
combination is a model, and section 4.4 checks it against v3's production record.

## 1. The shared substrate

Everything here is shared by every arm. No arm may replace any part of it. All of it lives under one root:
`/home/mandrake/rm/arena` for clones (ext4, beside `bench` and `foundry`; drvfs is too slow for git) and
`D:\ClaudeWork\rimmandrake\arena\` for control, logs and events (outside git, so no arm can edit them).

### 1.1 Task specs: frozen before assignment

One file per task, `D:\ClaudeWork\rimmandrake\arena\tasks\<TASK>.json`, with these fields:

- `id`, `source_item` (the ledger id), and `kind` (python-util, xml-def-patch, csharp, live-verify, tooling);
- `size`: 1, 2 or 4 points. It comes from the original diff (files and lines) and is fixed at freeze. Accepted
  work is counted in points, so splitting a task does not inflate the count. That was the 10-27 backtest failure;
- `area`: the path globs the task may touch. The gate refuses anything outside them;
- `prompt`: the item text as it read when the original work was claimed. For replay it is taken from the ledger
  `file` event and the item prose at the parent sha;
- `criteria`: the acceptance criteria, written plainly, and `proof`: the command that proves them;
- `live`: `none`, `minimal` (the 13-mod list, about 22 s cold) or `minimal+deps` (the 13 mods plus only the mods
  the item cannot load without; its load time is measured, never assumed). The trial has no `full` tier: the owner
  ruled the trial runs on the minimal list only, for fast cycling (2026-10-29);
- `hidden_checks`: held only in the judge's directory, never in an arm's clone. For replay they are the tests the
  accepted fix added, and, for items whose defect escaped, a check for that defect, written from the later
  rework item;
- `base_sha`: the original fix's parent, for replay. For live tasks, the candidate sha under test.

**Freezing.** `arena_tasks.py freeze` writes the sha256 of every task file into the event log BEFORE the
randomiser assigns anything. The judge refuses a task whose hash has changed. The criteria cannot drift toward
whatever an arm produced.

### 1.2 The one gate: run by the harness, never self-reported

`arena_gate.py --task T --base <sha> --head <sha> --arm X` runs after an arm says it is done, in a clean checkout of
the arm's head, as a separate process. Arms keep their own internal checks: Ralph's `ralph_gate.py`, v3c's done
gate, the trio's critic. Only this gate counts, and it is identical for all five arms. In order:

1. **Scope:** every changed path is inside `area`. Edits to an arm's own bookkeeping (its plan, `AGENTS.md`, its
   ledger shard) are stripped before judging, not refused.
2. **Non-empty and no placeholders:** an empty diff, `TODO`/`pass`/`NotImplemented` stubs in changed code, or a
   deleted test are refused (Huntley's named failure mode).
3. **Tests:** `run_selftests.py --only <tests for changed paths>`, plus every test the diff added.
4. **XML:** `validate_patch.py --live --defs` on changed patches and defs. An empty def-type file counts as
   UNMEASURED, not passed (rimworld-deploy skill).
5. **C#:** `winbuild.py`; a build failure refuses.
6. **Deploy plan:** `deploy_custom_mods.py --mod <m>` (plan only). The gate refuses a plan that touches a mod
   outside the task's area.
7. **The task's own `proof` command.**
8. **Live tasks only:** the live verdict comes from the lane (section 1.5), and the gate checks its record. The sha
   must match `head`. `modcheck` must have run with that deploy. **The canary** must have passed: a live colonist,
   a fresh Player.log, the expected game and mod versions, a map that is not the canonical world save. A failed
   canary gives `invalid`, never `fail`, and the run is re-queued.
9. **Different-agent test record (section 1.8):** a `test_start` event for this sha from an agent id other than the
   builder's, and its verdict. No record refuses.

The output is one JSON record: `pass`, `fail` or `invalid`, with each step's result and log paths. A gate that
cannot run a step writes UNMEASURED for that step, never a pass (instrument_traps).

### 1.3 The acceptance judge: blind

The gate is mechanical. The judge decides acceptance:

- **What the judge sees:** the task's `criteria`, the gate record, and the **neutralised diff**. That diff is the
  arm's head minus base, over `area` only. Commit messages, trailers and branch names are stripped, and the
  paths are re-rooted. For replay, the judge also runs the `hidden_checks`.
- **What the judge does not see:** which arm made it. The harness assigns a random judge id per submission and
  keeps the arm map in a file the judge process cannot read.
- **Who judges:** an Opus judge plus a GPT judge (`gpt_consult.py`), each blind to the other. Both must accept. A
  split verdict goes to a third, fresh Opus run, and the majority stands. Today the only blind check that stuck
  was an independent one, which is why the judge is two models.
- **Testing the blinding:** each judge also guesses the arm. If the guess rate is clearly above chance (binomial,
  p < 0.05 over the day), blinding is reported as leaky in the result. Residual tells are expected: Ralph and v3
  write code differently.

### 1.4 Git and clone layout

- **One long-lived clone per arm:** `/home/mandrake/rm/arena/<arm>`, plus throwaway replay clones at
  `/home/mandrake/rm/arena/replay/<arm>/<task>`. These are full clones, not worktrees: worktrees are OFF (owner
  ruling, 2026-10-02).
- **Replay clones have no future in them:** `git init`, then `git fetch /home/mandrake/rm/bench <base_sha>`. Only
  the history up to the parent sha arrives, so the original fix cannot be read from a later commit.
  `rm-scratch-reap` already reports on scratch clones. The `arena/replay` tree is added to its roots, and the replay runner deletes each clone after judging.
- **Branch namespaces:** each arm pushes only to `arena/<arm>/*`. A pre-push hook installed in each arm clone
  refuses any other ref and any path outside the arm's areas for that day. **No arm merges to `main`.**
  `arena land <submission>` merges an accepted live-half result to main after judging. Replay results never land:
  the work already exists.
- **The control is the exception:** `v3` keeps running production in `bench`/`foundry`/`dispatch` as it does
  today. That is the point of a control. Its trial tasks are ordinary queue items in its own areas.

### 1.5 The live lanes

There are two live lanes, one per machine: SteveDesktop and Archmagi. Each lane has one game and one bridge
driver, through the existing `rimflow bridge take/release`. Each lane has a wrapper, `arena_lane.py`, that logs
take, release, deploy, reload and canary for whichever arm holds it. The wrapper also enforces:

- **Archmagi:** the 20-minute idle rule (`--idle-ok`) whenever the owner plays. He said "I don't play right now so
  no need to wait", so while he is not playing it is a config flag, `owner_playing=false`. The rule comes back
  the moment he plays.
- **Never a flyer's flight.** Never a canonical world save.
- **No C# deploy while the game runs:** the DLL is locked.
- **Restore the owner's mod list after a test:** `modlist_swap.py restore`. Ralph §3.2 left this uncharged; the
  harness charges its minutes to the arm that swapped.

### 1.6 Token metering: by clone path, not by agent report

Claude transcripts are stored per working directory (`~/.claude/projects/<cwd-slug>/`). Each arm's agents run with
their cwd in their own clone, so `spend_census.py` can attribute spend to an arm by the transcript's project slug,
helpers included. GPT calls go through `gpt_consult.py`, and a small proposed change makes it tag each call from `RM_ARM` in the environment. The judge
and the gate run from `/home/mandrake/rm/arena/judge` and are billed to the harness, not to any arm. **Unit:** ITE,
as in the 10-26 baseline (M1). **Sanity probe (owed):** run a known 1-pass job in a fresh arm clone and check
that the census sees it before trusting a zero.

### 1.7 One event log, one format

There is one file per arm, `D:\ClaudeWork\rimmandrake\arena\events\<arm>.jsonl`. Records are written only by
harness code (the loop wrappers, the gate, the judge, the lane wrapper and the switch), never by an agent. The
schema, one line per event:

```
{ts, arm, lane, run_id, task, event, sha?, verdict?, ite?, minutes?, rule?, detail?}
event ∈ freeze | assign | pass_start | pass_end | build_end | test_start | test_end | gate | judge
        | critic_round | live_take | live_release | reload | canary | card | owner_touch | defect | invalid
        | switch | stop
```

`v3` writes nothing natively. A small adapter, `arena_v3_adapter.py`, translates its ledger events (start, close,
verify) and testq records into the same schema, so the control is measured the same way.

**Owner minutes, per arm.** The owner's ruling (2026-10-29): every arm may send him design-decision cards, through
the Conductor, on equal terms; he does not debug or nudge any arm. Each `card` event carries the arm, and rm-pulse
dwell time on that card is his measured minutes for it. A typed message to an arm counts 1 minute (assumed) and is
logged as `owner_touch`. A phone button, `arena owner +N`, covers anything else. Each card answer also tags the
tasks it unblocked, so every arm's output is reported twice: with and without owner-unblocked work. This is the
weakest instrument in the harness, and section 5 says so.

### 1.8 Binding on every arm: a different agent tests what was built, promptly

The owner, 2026-10-29: "I definitely do want to enforce a different agent tests what was built... but I just don't
want to wait for that to happen far later than the build. So whatever designs we implement, they must have that
property." The rule and how each arm meets it are in `testpilot_merged_2026-10-29.md` section 2.3. In short: a
tester with a fresh context, other than the builder, starts testing each candidate before the builder's next build
pass begins, and the harness gives a builder no new item until it has. The harness enforces it from `build_end`
and `test_start` (tester agent id differs from the builder's), reports the latency per arm, and the gate refuses a
candidate with no such record (section 1.2 step 9). `trio` already had the property (critic, then TestPilot);
`ralph_a`, `ralph_c`, `v3` and `v3c` were adapted with a fresh blind tester pass or tester helper after each build.

## 2. The switch

### 2.1 What the single value changes

There is one file outside git, `D:\ClaudeWork\rimmandrake\arena\arm.toml`:

```toml
mode = "ralph_a"          # v3 | v3c | ralph_a | ralph_c | trio | trial
[trial]                   # read only when mode = "trial"
steve_lane   = "trio"     # who holds SteveDesktop's game
archmagi_lane = "ralph_c" # who holds Archmagi's game
replay_arms  = ["ralph_a", "trio", "v3", "v3c"]
areas_day    = "D:/ClaudeWork/rimmandrake/arena/areas/2026-10-31.json"
```

Each arm is a systemd user target, `rm-arm-<arm>.target`. Its units are `PartOf=` the target, so stopping the
target stops them. Each target lists every other arm's target in `Conflicts=`, so systemd itself refuses two
targets at once. The 25-odd existing timers are split into two groups:

| group | units | in which target |
|---|---|---|
| substrate (always on) | account-usage, account-capture, deadman, memwatch, mirror, pulse-*, codebase-health, scratch-reap, selftests-nightly, objstore | none; they run under every arm |
| v3's machinery | rm-dispatcher, the role units it launches, rm-ops-watch's dispatch triggers, testq-tick, testq-steward-watch, artpipe-idle-fill, arteval-autojudge | `rm-arm-v3.target` |
| v3c | the same programs with the collapsed schedule file (I7) | `rm-arm-v3c.target` |
| ralph_a | `rm-ralph-loop@a.service` (the supervisor that restarts `loop.sh`, which alternates a build pass with a fresh blind tester pass) | `rm-arm-ralph_a.target` |
| ralph_c | `rm-ralph-loop@a1`, `@a2` (each alternating build and tester passes), `rm-runner@steve`, `rm-runner@archmagi` | `rm-arm-ralph_c.target` |
| trio | the FOUNDRY loop with its builder and critic subagents, `rm-testpilot@steve`, `rm-testpilot@archmagi`; the Conductor stays the owner-present window | `rm-arm-trio.target` |

`mode = "trial"` starts no single target. Instead it starts the replay runner (`rm-arena-replay.service`) and puts
one arm on each live lane. `v3` keeps production running, confined to that day's areas by `areas_day`.

### 2.2 Switching with no collisions

`arena switch <mode>` does, in order:

1. Writes `STOP` for the running arm. Every loop honours it at its next pass boundary, and so do the pilots at
   their next test boundary.
2. Waits until the arm's status file reads idle, at most 90 minutes (the per-pass timeout). After that it stops
   the target: SIGTERM, then the EXIT trap releases the bridge.
3. Releases the bridge on both lanes and runs `modlist_swap.py restore`. The owner's `ModsConfig.xml` is the state
   of his NEXT load, so it is parsed and compared with his saved list, never grepped.
4. Checks git. Every arm clone must have no unpushed commit outside its namespace. Unpushed work stays on its
   `arena/<arm>/*` branch, which is never deleted.
5. Writes the `switch` event, starts the new target, and runs `arena who`.

**Collisions are prevented by construction, not by care:**

- **git:** separate clones, separate namespaces, the pre-push hook, and no arm merges to main.
- **areas:** each arm's area list for the day is disjoint from every other's, and the gate refuses edits outside it.
- **the live game:** one lane per arm, and the bridge lock carries the arm tag.
- **the Mods folder:** the deploy plan refuses mods outside the arm's areas.

### 2.3 Proving only one architecture is live

`arena who` exits non-zero, and ops_watch raises `ARENA_TWO_LIVE`, if any of these fails:

- (a) `systemctl --user list-units 'rm-arm-*'` shows exactly the expected targets active;
- (b) no live process has its cwd inside a stopped arm's clone (read from `/proc/*/cwd`);
- (c) each bridge lock's holder tag names that lane's arm;
- (d) no stopped arm has written an event, and no stopped arm's ref has been pushed, since the `switch` timestamp.

It runs after every switch and on ops_watch's 15-minute tick.

## 3. The experiment

### 3.1 Two experiments, run in parallel

| | build half: historical replay | live half: crossover on two machines | production control |
|---|---|---|---|
| what it compares | how each arm BUILDS and has its build tested by a different agent: `ralph_a` (no critic; a fresh blind tester pass after each build pass), `trio` (builder + blind critic, round cap per testpilot_merged §2.1 L4), `v3` (today's FOUNDRY procedure: a seat brief, helpers, plus a fresh tester helper after each close), `v3c` (`v3` + tester helper + done gate + a GPT review per sha) | how each arm LIVE-TESTS: the `trio` TestPilot (fixes in place, written reload rule) against the `ralph_c` fixed-SHA runner | v3 on the real queue, judged by sampling |
| where | throwaway clones, no game | SteveDesktop and Archmagi | today's seats |
| tasks | past items with a known outcome | real candidates from the verify backlog (M11: 521 built items waiting at 10-26), plus planted known defects | its normal queue |
| why this split | `ralph_c` builds exactly as `ralph_a` does, twice over, so it is not replayed separately | the live half is the only place `trio` and `ralph_c` differ from the others | free: it runs anyway |

### 3.2 Picking the tasks

**Replay pool.** `arena_tasks.py census` scans closed ledger items from 10-12 to 10-27 and keeps those with:

- a start and a close event;
- a closing sha that resolves, with a diff of 1-8 files;
- a kind the gate can judge offline (Python, XML, C#, tooling);
- an objective proof: the fix added or changed a test, an XML validation or a build.

Each kept item gets a label. **Clean** means a verify pass and no `caused_by` rework item within 7 days.
**Escaped** means a later rework item names it as the cause; that rework's fix becomes a hidden check. How many
items qualify is not known yet. The census is the first thing built, and it reports the count with a sanity probe
(a hand-picked item it must find).

**Stratifying.** Tasks are grouped by kind × size, with Escaped items over-sampled to about a third, so that defect
detection is measured at all. Inside each group the draw is random, seeded by the freeze event's hash.

**Pairing.** Every replay task goes to every replay arm, so each task is paired with itself four ways. What gets
randomised is the ORDER and the time slot of each arm's run, so quota pressure and time of day do not line up with
one arm.

**Live pool.** Candidates come from the verify backlog. They are matched in pairs by verify level (L1-L4), live
need (minimal or full) and mod family. A coin flip sends one of each pair to each lane. Then the lanes swap
machines at the half-day: an AB/BA crossover, so a machine effect cancels. **Planted defects:** about one candidate
in five is a past Escaped fix with its defect re-introduced. It is the same sha for both pilots, in different
halves. This measures sensitivity, which a pilot's fail rate alone cannot (Ralph §8 point 7).

**Freezing.** Criteria, hidden checks and size are frozen and hashed before assignment (section 1.1). The judge
never sees the assignment.

### 3.3 Measures, in rank order

1. **Accepted work per day:** judge-accepted points per arm per day at an equal token allowance and equal wall
   clock. For replay this is reported as accepted points per arm-hour of serial runtime, so arms are not rewarded
   for the parallelism the harness lends them. Each arm's own native concurrency (C's two loops, the trio's
   subagents) stays inside its run.
2. **Tokens per accepted point:** ITE, metered by clone (section 1.6).
3. **Owner minutes per accepted point, per arm:** measured from the cards each arm sent him (section 1.7), with
   every arm's output reported with and without the work his answers unblocked.
4. **Productive live-game minutes share:** minutes in a test whose canary passed and whose verdict the gate used,
   divided by lane wall-clock minutes. Lane minutes not in any test are counted, not hidden.
5. **Reloads per accepted live item,** each with the rule it met (trio) or the reason (others).
6. **Defects found later:** hidden-check failures at judging, then a 72-hour re-run of the gate and hidden checks
   on day-1 accepted work, then 14 days of `caused_by` rework items against accepted live-half work.

**Leading indicators,** logged per pass so the day can be read by the afternoon:

- gate pass rate on the first try;
- tokens per gate pass;
- rework rounds per accepted task (loop retries, critic rounds);
- time to first gate pass;
- the judge accept rate given a gate pass.

They multiply out to the forecast:
`accepted/day ≈ passes/day × P(gate pass) × P(judge accept | gate pass) × points/task`.
Section 4 checks that forecast against the day's actual count.

### 3.4 Blinding

- **The judge** is blind to the arm (section 1.3), and its arm-guess rate is reported.
- **The arms** are blind to the trial. Their prompts are their ordinary ones, with no mention of a comparison.
- **The owner** sees live-half results, and every design card, without arm labels until the decision is written.
  His minutes are measured, not asked.
- **The analyst** writes the decision rule (section 4) before day 1. The analysis script runs on the event log
  with arm ids hashed, and is unhashed only after the rule fires.

### 3.5 How many tasks: the power arithmetic

Inputs from the v2 week (measured, `v2_variance.py`):

- Per-item start-to-close time: n = 176, median 0.20 h, p10 0.02 h, p90 4.87 h, **log-SD 2.33**. That spread
  includes idle waiting and unlike items.
- Verify results 10-20..10-26: 320 pass, 130 partial, 52 fail. **First-try pass share 0.64.**
- Daily closes: **CV 1.34**. The day is not a usable unit.

Formulas (two-sided α 0.05, power 0.8, so z-sum 2.8; δ = ln(ratio); 1.5× is δ 0.405, 2× is δ 0.693):
paired, n = (2.8 σ_d / δ)², where σ_d is the SD of the within-task log ratio between two arms; unpaired,
n per arm = 2 (2.8 σ / δ)². All counts are rounded up.

| design | σ (log) | tasks for 1.5× | tasks for 2× |
|---|---|---|---|
| unpaired, raw v2 spread | 2.33 (measured) | 520 per arm | 178 per arm |
| unpaired, micro-tasks matched by kind and size | 1.0-1.5 (assumed) | 96-215 per arm | 33-74 per arm |
| **replay, same task in each arm** | **σ_d 0.5-0.8 (assumed; measured on day 1)** | **12-31** | **5-11** |

**Acceptance rate**, paired (McNemar): to tell a 0.64 first-try acceptance from 0.85, with about 25% of pairs
flipping one way and 4% the other, takes about **49 paired tasks**. Unpaired it takes about 66 per arm.

**What that means:**

- **Speed and tokens:** replay detects a 1.5× difference in 12-31 tasks per arm. Without replay the same answer
  needs 100-500 tasks per arm: weeks.
- **Acceptance rate:** a 20-point difference needs about 50 tasks per arm.
- **Escaped defects:** these cannot be powered in days (section 5).

The day-1 duplicates (section 4) replace the assumed σ with a measured one. The task counts are then recomputed
before day 2.

**The budget is the binding constraint, not the calendar.** At about 2-3M ITE per micro-task attempt (v2 spent
about 1.9G ITE a week over about 928 closes, so about 2M a close), 4 replay arms × 25 tasks costs 200-300M ITE.
That is about a day of today's spend (M1: 270M ITE/day). The owner allowed 1.5× normal spend for the three
measuring days (2026-10-29), which fits 50 replay tasks per arm into days 1-2. After the trial the steady budget is
set from the measured cost per accepted item.

## 4. Day-by-day plan and decision rules

### 4.1 The stopping rule, written before day 1

The trial uses a Bayesian sequential rule. It is checked after every block of 5 completed tasks per arm, and the
trial stops the moment a rule fires. Fixed-length trials waste days once the answer is clear.

- **The model:**
  - Each arm's log time-to-acceptance and tokens per accepted point get a hierarchical normal model with a task
    effect, so replay pairs each task with itself.
  - Acceptance is Beta-binomial per arm.
  - Priors are weak and centred on the simulator, with a wide spread: `ralph_a` at 0.5× `v3`'s capacity per token
    (Ralph §10), the others at 1×.
- **Decide for X:** P(X's accepted points per token ≥ 1.25 × the best other arm's) > 0.95, AND X's judge accept
  rate is not credibly worse than the control's (P(worse by ≥ 0.10) < 0.2).
- **Futility, drop X:** P(X ≥ 1.1 × control) < 0.05. The arm stops getting new tasks, and its budget goes to the
  arms still in contention.
- **Tie:** P(|difference| < 15%) > 0.9 between the leading arms. Then the **simpler arm wins**: fewer running
  units and fewer files of state. The order is fixed now: `ralph_a` < `ralph_c` < `trio` < `v3c` < `v3`.
- **Minimum before any stop:** 10 tasks per arm across at least 2 kinds. This keeps an early fluke from deciding.
- **Disqualification, at any time:** an arm publishes work the gate did not pass, edits outside its areas, holds a
  lane without a canary, lets a builder start a new build pass before a different agent has started testing its
  last candidate (section 1.8), or breaks a standing ruling. A loop that publishes unchecked work is not a candidate at
  any speed.
- **Hard cap:** the end of day 3. Whatever has not separated by then is reported as "no difference detectable
  in days", with the intervals.

### 4.2 Day 0: build and freeze (not a trial day)

- The substrate, Ralph A and the replay runner are built (section 6, steps 1-3).
- The census picks the replay pool. Tasks are frozen and hashed.
- The decision rule above is committed in the analysis script before any arm runs.
- **Failure-path drill,** carried over from Ralph §8 point 4. Plant a failing check in one task, kill one pass
  mid-run, and kill the gate mid-run. Proven when nothing unchecked reaches an `arena/*` branch the judge reads,
  and the next pass recovers.

### 4.3 Day 1: replay block 1 (all four build arms in parallel)

- **Morning:** 4 arms × 12 tasks, interleaved in random order.
- **Duplicates:** 6 of those tasks are run twice in the same arm. That measures run-to-run spread, which gives
  σ_d and how much of an arm difference is just noise.
- **Production:** v3 runs as usual. The judge samples 10 of its closes from the day.

**Known by early afternoon (about 4 hours):** the leading indicators per arm, from about 10-15 passes each. Each
arm gets a first forecast of accepted/day.

**Known by the end of day 1:**

- accepted points, tokens per accepted point and accept rate per arm, about 12 tasks each;
- the measured σ_d, with the section 3.5 task counts recomputed from it;
- whether the leading indicators predicted the day's accepted count. The check: within the 80% interval of the
  noon forecast.

**Decision rule at the end of day 1:**

- Apply futility and disqualification only; no arm is declared the winner yet (the minimum is 10 tasks per arm,
  and a full block is needed).
- Calibrate the simulator. The measured `r_dur_mult`, `r_p_off`, `r_ctx_ite`, tokens per pass and critic rounds go
  into `ralph_loop_sim.py`. It then forecasts day 2's leading indicators and accepted points per arm, written
  down before day 2 starts.

### 4.4 Day 2: replay block 2, and the live crossover starts

- **Replay:** 12-25 more tasks per surviving arm. The sizes come from the recomputed power numbers, and the
  budget goes to the arms still in contention.
- **Live, first half:**
  - The `trio` TestPilot takes SteveDesktop, and the `ralph_c` runner takes Archmagi. Each gets about 8-10
    matched candidates, 2 of them planted defects.
  - Swap machines at midday.
  - The live tests run on the minimal list only, plus an item's load dependencies where it needs them. There is no
    full-list check inside the trial (owner, 2026-10-29).
  - Reloads follow the owner's cost-scaled rule (`testpilot_merged_2026-10-29.md` M1): with the 22-second minimal
    list, a few more unrelated tests and then reload; never exhaustive; only the scenarios a change touches are
    re-run (L9a).
- **Simulator check:** compare day 2's actual numbers with the day-1-calibrated forecast.
  - If accepted points per arm fall inside the 80% intervals for at least 3 of 4 arms, the simulator is trusted
    for what days cannot measure: week-scale quota, a full-queue backlog, the combination of the build half and
    the live half.
  - If not, it is not used for this decision, and the report says so.

**Known by the end of day 2:**

- **The build-half verdict:** most likely decided by then, at about 24-37 tasks per arm. That covers a 1.5×
  difference at σ_d up to about 0.8.
- **First live-half numbers:** candidates resolved per lane-hour, reloads per resolved candidate, productive
  live-minute share, planted defects caught, invalid runs.

**Decision rule at the end of day 2:**

- Apply the section 4.1 rule to the build half.
- For the live half, it is still too early to stop (about 16-20 candidates). Its only outcome now is
  disqualification: a pilot that misses both planted defects, or a reload that logged no rule.

### 4.5 Day 3: the live swap completes, and the combined verdict

- **Live, second half:** the AB/BA crossover finishes, for about 30-40 live candidates in total.
- **Combining the halves:** the build-half winner and the live-half winner give each whole architecture's
  accepted work per day, using the calibrated simulator, if it passed on day 2.
- **Checking the combination:** the whole-architecture estimate for `v3` must match v3's sampled production
  record within its interval. If it does not, the combination is wrong, and only the separate half verdicts are
  reported.
- **Retest:** the 72-hour retest of day-1 accepted work starts. It reports on day 4.

**Decision rule at the end of day 3:**

- One recommendation: the architecture whose build half and live half both win or tie, with ties going to the
  simpler arm. If the halves disagree (say, Ralph builds better but the TestPilot tests better), the
  recommendation is the hybrid. That is what the trio already is, with a Ralph builder.
- **A win switches production at once.** The owner ruled (2026-10-29) that a trial win authorises switching
  production to the winner immediately, so `arena switch <winner>` runs the day the rule fires. The owner gets one
  page: the verdict, the intervals, what was not measurable, and the switch that was made.

## 5. What days cannot tell us, and the watch after deciding

These cannot be learned in three days. Saying otherwise would be false:

- **Rare defects.** An escape rate of 5% per item needs about 60 accepted items per arm just to see 3 escapes, and
  escapes surface days after the close (Ralph §7.3: 14 days for quality). Planted defects measure sensitivity to
  KNOWN defect types only.
- **Long-run drift:** a plan or `AGENTS.md` that bloats, a prompt that rots, a TestPilot that degrades over days of
  handoffs, the queue mix changing.
- **The weekly quota:** a three-day spend rate does not show behaviour near the weekly cap.
- **Owner supervision cost:** the minutes he spends tuning, reading and correcting grow or shrink over weeks. Three
  days with an owner who knows a trial is on are not typical. The owner-minutes instrument is also the weakest
  (section 1.7).
- **The owner playing:** the Archmagi lane under the 20-minute rule, bumps, and cold loads of his full list after a
  test. This is measured only if he plays during the trial.
- **Rare failures:** a game crash mid-test, a dead machine, a bad merge.

**The watch after deciding (champion and challenger):**

- **Challenger lane:** for 14 days after the switch, 10% of new tasks still go to the runner-up arm, under the same
  gate and judge. A reversal shows up as the challenger's interval crossing the champion's.
- **CUSUM alarms:**
  - on daily accepted points;
  - on tokens per accepted point;
  - on `caused_by` rework items against accepted work, using the ledger's existing cause field.
  ops_watch raises `ARENA_DRIFT` when a CUSUM crosses its threshold. The thresholds are set from the trial's own
  intervals.
- **Planted defects keep coming:** one per day into the live lane, to keep measuring sensitivity.
- **Weekly:** a GPT whole-system review, as the owner set for every finished system.
- **Reversal is one command:** `arena switch <runner-up>`. Nothing about the losing arms is deleted for 14 days.

## 6. Build order and cost

Depth first and small. Each step is built, proven by its own forced failure, blind-reviewed by GPT
(`gpt_consult.py`, fresh context, sees the code and the step's acceptance criteria), fixed, and committed before the
next starts. Hours are ESTIMATES of builder working time, including the review round, not wall-clock time.

| step | what | hours | proof (forced failure) |
|---|---|---|---|
| 1 | **Task census and freeze** (`arena_tasks.py census/freeze`): replay pool, labels, hidden checks, hashes | 5 | a hand-picked item is found; a changed task file is refused by its hash |
| 2 | **Event log library and the `v3` adapter** | 4 | an agent-written event is rejected; adapter output matches `rimflow_metrics.py` close counts for one day |
| 3 | **`arena_gate.py`** wrapping the existing tools, with UNMEASURED steps | 6 | a placeholder diff, an out-of-area edit, a red test and a dead-colony canary are each refused or marked invalid |
| 4 | **The judge:** neutraliser, Opus and GPT blind judging, arm guessing | 5 | a diff containing the arm name is caught by the neutraliser; a known-bad replay output is rejected |
| 5 | **Replay clone builder and runner** (fetch to the parent sha, interleaved scheduling, reaper roots) | 4 | the clone cannot `git show` the original fix sha |
| 6 | **Metering by clone path,** with the sanity probe | 2 | the probe job's spend is seen; a zero is refused as a result |
| 7 | **The switch:** `arm.toml`, `rm-arm-*.target` with `Conflicts=`, `arena switch/who`, pre-push hooks, ops_watch rule | 6 | starting two targets fails; a push from a stopped arm is refused and alarmed |
| | *Substrate subtotal* | *32* | *plus the day-0 failure drill* |
| 8 | **`ralph_a`:** `loop.sh`, `PROMPT.md`, `POLICY.md`, the fresh blind tester pass that follows every build pass (`TESTER.md`, section 1.8), and the owed small parts (`run_selftests --quick`, `bridge release --mine`, runway check) | 8 | Ralph §8's planted failing check and killed pass; a planted defect the gate passes is caught by the tester pass; the loop refuses a second build pass with no `test_start` |
| 9 | **The `v3` replay procedure** (today's FOUNDRY brief, in a throwaway clone, plus a fresh tester helper after each close) and **`v3c`** (plus the done gate and a GPT review per sha, reusing collapse step 1 if it has landed) | 7 | v3c refuses a close without a review record and a tester record bound to the sha; the v3 procedure briefs no new build before the tester helper starts |
| 10 | **`trio` builder and critic:** Ralph builder and blind critic subagents, round cap and simplify-or-split per `testpilot_merged_2026-10-29.md` §2.1 L4 (2 rounds, one simplify/split, 2 more, then park) | 6 | a task built to never satisfy the critic ends in simplify/split after round 2 and park after round 4, not a loop |
| | **Build-half path: steps 1-10** | **53** | **then days 1-2 of replay can run** |
| 11 | **The formal model** of the live-resource handoff (section 7) | 8 | TLC finds the known goodbye interleaving in the unfixed model |
| 12 | **The `ralph_c` fixed-SHA runner and the lane wrapper** (`arena_lane.py`: canary, minimal or minimal+deps profile, `modlist_swap` restore, take/release logging) | 6 | a result for a stale sha is refused; a dead colony gives `invalid`; a request for the full list is refused in trial mode |
| 13 | **The `trio` TestPilot:** the written reload rule scaled by measured reload cost (testpilot_merged M1), affected-scenario re-test (L9a), hot-load classes, a session file, handoff to a fresh pilot while the game stays up, subagent fixes landing only if hot-loadable | 14 | an owner return mid-test yields within the bound; a C# fix forces a logged reload; a pilot handoff loses no queued candidate; a rebuild touching one footprint re-runs only that scenario |
| 14 | **`ralph_c` assembly:** two loops, area ownership, both runners, the tester pass per loop and runner back-pressure (section 1.8) | 3 | a stolen item's out-of-area edit is refused; a builder whose live candidate waits for a runner is given no new live item |
| | **Live-half path: steps 11-14** | **31** | **then days 2-3 live** |
| | **Total** | **about 84** | |

**What that means on the calendar:**

Assume an autonomous builder delivers about 12 effective hours a day, after review waits (ASSUMED).

- **One builder:** the build half is ready after 53 hours, about day 5. Replay then runs on days 5-6. The live half
  is built after that and runs about days 9-11.
- **Two builders:** the substrate comes first (32 hours, about day 3). Then one builder takes steps 8-10 while the
  other takes 11-14. Replay starts about day 5, and the live crossover about day 6. **The full answer comes in
  about 8 days from the go, and the build-half answer in about 6.**
- **The 3-day trial in section 4 is the measuring time.** The build time above comes before it.

**The cheapest useful slice:** steps 1-8 plus the `v3` half of step 9, about 43 hours. That gives Ralph A against
today's FOUNDRY procedure on replayed tasks, the question the Ralph design doc's §8 trial asked. On these numbers
it gives a 1.5× answer in about two trial days. Built by one builder, that answer is ready about day 5 from the go.

**GPT's review before each arm runs.** Each arm, and the substrate as a whole, gets a blind GPT review before its
first counted task. The review covers the code, the frozen tasks and this decision rule. A P0 finding stops that
arm from running until it is fixed and re-reviewed. Lesson from today: at most 2 review rounds, then simplify or
split.

## 7. Formal models before building

Today gave two warnings:

- **The goodbye race.** A message arrives while the Conductor's close-out and kill are under way. Three blind
  reviews left it at P0. The owner then ruled that the kill stays on, with concurrent typing an accepted risk.
- **The findings fold.** It did not converge in 4 review rounds, and converged only when simplified.

These are different kinds of problem, and only the first one is a job for a formal model.

**Worth a model (TLA+, checked with TLC): the handing-over of a live resource.** The goodbye restart, the
TestPilot's handoff to a fresh pilot while the game stays up, and the arena switch have the same shape: a
resource (a window, the bridge and game, the arm's units) passes from a context that is ending to a fresh one
while inputs keep arriving. One parameterised spec covers all three. Its variables are:

- the owner's messages;
- candidate arrivals;
- subagent fixes that become ready;
- the owner returning to Archmagi;
- a game crash;
- the bridge lock and its holder tag;
- the deployed sha and the game's loaded sha;
- the old context's and the new context's states;
- the `STOP`/`switch` file.

Safety invariants to check:

- **S1:** at most one live driver per game, and at most one live arm target per lane.
- **S2:** no verdict is recorded for sha X while the game has sha Y loaded.
- **S3:** no C# deploy while the game process lives. A fix is applied to a running game only if its class is
  hot-loadable: a savegame edit, a bridge-injected structure, or a def change the bridge can reload.
- **S4:** every reload is preceded by a logged rule (the burden of proof).
- **S5:** no owner message and no queued candidate is lost across a handoff. Each one is either handled by the old
  context or delivered to the new.
- **S6:** no event and no push from an arm after its `switch` timestamp.

Liveness properties, under weak fairness:

- **L1:** every candidate is eventually resolved, marked invalid or parked.
- **L2:** an owner return frees the Archmagi game within the bound.

The model's first job is to reproduce today's goodbye interleaving in the unfixed protocol. A model that cannot
find a bug we already know cannot be trusted to find new ones. Then it checks the fixed protocol. Cost: about 8
hours, including installing tla2tools (Java), which has not been checked on this machine. P language would let us
generate tests against the real code later, but it costs more to learn. Start with TLA+, and take up P only if the
TestPilot implementation keeps diverging from the spec.

**Model lightly: the builder/critic ping-pong.** The fold's non-convergence was not a protocol bug. The critic
kept finding real problems in an over-large module. No formal model can prove that judgement converges. What can
be enforced is the protocol shape:

- the round counter is at most 3;
- every accept is bound to the sha the critic actually saw;
- round 2 without an accept ends in one `simplify`/`split`; round 4 without an accept ends in `park`, never another round (testpilot_merged §2.1 L4).

Those are three invariants. A forced-failure test (step 10) covers them, and a model would add nothing. About 1
hour if it is written as a small extra TLA+ module anyway.

**No model: the gate, the judge, the event log and the metering.** They are deterministic functions of their
inputs. Tests are the right tool for them.

## 8. Owner decisions

Decided on 2026-10-29:

1. **Token allowance:** 1.5× normal for the three measuring days, then a steady budget set from the measured cost
   per accepted item.
2. **Mod list:** minimal list only, plus an item's load dependencies; no full-list check in the trial.
3. **His role:** design-decision cards from every arm equally; no debugging; minutes measured per arm.
4. **A win:** production switches to the winner immediately.
5. **Binding on every arm:** a different agent tests what was built, promptly (section 1.8).

The build is ticketed for FOUNDRY at top priority with two builders, in the order of `testpilot_merged_2026-10-29.md`
section 6.3.

Still open:

1. **Planted defects in the live lane:** about 1 candidate in 5 during the trial and 1 a day after. They cost pilot
   time but are the only way to measure sensitivity.
2. **The simplicity tiebreak order** in section 4.1. It decides ties, so he should agree to it before the first
   counted task.
