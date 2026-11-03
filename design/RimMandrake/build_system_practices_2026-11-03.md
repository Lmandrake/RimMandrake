# What mature build systems do that we could adopt (2026-11-03)

Owner ask, 2026-11-03: "what are other things mature build systems do? Please do some research on this now and see if we can't get some even better ideas across the board to level up our performance."

Method: BENCH read our own machinery first (rimflow, Utils, relentless_*), then had GPT do an independent open-web survey with primary sources (prompts and answers in BENCH scratch, not kept). GPT then gave this note an adversarial read, and its six findings are fixed in the text. The tokens and hours in "expected value" are estimates. The only measured numbers are today's incidents (a)-(f) and the subprocess-timeout count in idea 2. This is research only. No items are filed here.

Today's failures, which every idea below is scored against:
- (a) The clone pool filled because trailing state-only commits pinned clones (6 of 8 places live).
- (b) The /tmp tmpfs filled with agent scratch, and 58 nightly tests went red.
- (c) Some live-proof FAILs were really harness faults: a preflight refusal labelled FAIL, WSL python unable to reach the bridge on loopback, and a proof run on a game where the mod was never deployed. Each cost about 1M tokens.
- (d) A hung robocopy, left on its default of 1,000,000 retries, blocked a seat restart for 4 hours.
- (e) About 44 real nightly reds sat with no one working on them.
- (f) Recurring alarms got patched one instance at a time instead of by class.

## Two-minute read

Mature systems (Google, Meta, Uber, Android device labs, Linaro's LAVA) share one habit we mostly lack: **they never let the machinery's failure count as the product's failure, and they put a hard limit on everything.** Every expensive run gets one of three verdicts, not two: PASS, FAIL, or "the infrastructure broke, this run says nothing" (LAVA's `InfrastructureError`, AWS Device Farm's `ERRORED` against `FAILED`, Firebase's `INCONCLUSIVE`). Every external call has a deadline. Every job has a disk quota, and its scratch dies with the job. Every red test has a named owner with a deadline. Pipeline health is tracked as a service with an error budget, and when the budget runs out, feature work stops until the pipeline is fixed.

We already have more than most hobby systems: a content-hashed selftest cache (Bazel-style), leases with TTLs, a PID-proof game lock, isolated re-runs of checks at the close sha, a known-reds list, a strike ladder, an alarm census, and UNMEASURED in place of a fake 0. What is missing is the habit of turning each of those into a **rule enforced in code for the whole class**.

**Top 5 now (all five are cheap, and each would have prevented at least one of today's failures):**
1. **Three-way live verdict plus a health check before each proof.** A live run reads PASS, FAIL or INFRA. Before spending a proof, three things are checked on the game: the bridge answers from the interpreter that will drive it, the deployed hash matches the built hash, and the site preflight passes. If the check fails, the run is INFRA: no strike, no review, retried on a healthy game, with a cap on retries. Anything that goes wrong after the check passed stays FAIL. Prevents (c), about 3M tokens today.
2. **A deadline on every external call, enforced by a lint.** 130 of our 325 blocking `subprocess` calls have no timeout. robocopy runs with no `/R` `/W` limits. Prevents (d).
3. **Per-place quotas and scratch that dies with the job.** Each place gets its own TMPDIR inside its own budget. The supervisor measures that budget every tick and stops a place that goes over, the way Borg kills a task over its limit. The TMPDIR is deleted when the place is released. Nothing launches without disk headroom. A clone is kept only because of the work it holds, never because of commits trailing behind it. Prevents (a) and (b).
4. **A "build cop" rule for reds.** Every new nightly red gets an item and an owner (Relentless itself) within one night, at top priority, with a deadline. A red still unfixed past its deadline alarms, whether or not someone owns it. The known-reds list is the only way to park a red, and entries expire. Prevents (e).
5. **Pipeline SLOs and an error budget, with postmortems that fix a class.** About four numbers measure pipeline health. When the budget is spent, Relentless works only on pipeline repair. Every postmortem action ships a guard test for the class. Prevents (f), and stops (c)-(e) from piling up again.

## Top 5 now

| # | Idea | Prevents | Cost here | Expected value |
|---|------|----------|-----------|----------------|
| 1 | Three-way verdict (PASS/FAIL/INFRA) plus a health check on the game before each proof | (c) | Small to medium: the `refused` kind, UNMEASURED and the UNDEPLOYED retry already exist | High: about 1M tokens per harness fault avoided, about 3M today, and FAIL becomes trustworthy |
| 2 | Deadline on every external call (lint plus wrapper) | (d), and future hangs anywhere | Small: one AST selftest and one helper | High: one 4 h seat stall today, and an unknown number of silent stalls |
| 3 | Per-place quota and ephemeral scratch; clones kept only by explicit roots | (a), (b) | Medium: relentless_disk and scratch_reap already hold most of the parts | High: today 6 of 8 places were idle and 58 tests went falsely red |
| 4 | Build cop: every new red gets an owner and a deadline | (e) | Small: known_reds and ops_watch exist; only the auto-file and priority are missing | High: 44 reds are real defects that nobody is working on |
| 5 | Pipeline SLOs, error budget, class-fix postmortems | (f), plus (c)-(e) piling up | Medium: rimflow_metrics, incident.py and alarm_census exist | Medium to high: this is what keeps 1-4 from rotting |

## Next 5

| # | Idea | Prevents | Cost here | Expected value |
|---|------|----------|-----------|----------------|
| 6 | Test the tester: a known-good canary proof plus fault injection into the harness | (c), (f) | Medium | Medium: catches the next new harness fault before a real item pays for it |
| 7 | Flakiness score with rerun-on-fail and expiring quarantine | (e) noise, (b)-type false reds | Small to medium | Medium |
| 8 | Test impact selection by inverting the selftest cache's declared inputs | Slow feedback, token spend | Small | Medium: faster builder pre-commit and fewer irrelevant reds in an item's run |
| 9 | Treat the game as a lab device: an explicit state machine and fencing tokens | (c), stale-holder overlap | Medium | Medium |
| 10 | Light merge-queue check: test the integrated main after landings | Semantic conflicts between 8 parallel places | Small to medium | Low to medium today, and rising as throughput grows |

## Considered and rejected

- **Adopting Bazel, Buck2 or Pants wholesale.** Our build is Python plus RimWorld XML plus a Windows C# build, and the thing under test (a running RimWorld) can never be hermetic. Migrating would cost weeks. We already have the one piece that pays, content-hashed action caching (`selftest_cache.py`). Rejected: the cost is huge and the marginal gain is small.
- **Remote execution or a build farm.** We run on one machine. The bottleneck is the single game and the token budget, not CPU. Rejected.
- **ML predictive test selection** (Meta 2019, Launchable). It needs large volumes of change and failure history, and 945 tests is small. Idea 8, the cheap dependency-graph version, gets most of the benefit. Rejected for now.
- **A full speculative SubmitQueue** (Uber). It is built for thousands of changes a day. Ours are tens. Speculation needs extra clones, which is exactly what failure (a) ran out of. Rejected. Idea 10 is the right size.
- **Chaos Monkey against the live game.** The game is the scarce resource, and random kills would burn 15-minute cold loads. Faults are injected only into harness tests and quicktests (idea 6). Rejected for production.
- **Docker or OpenHands containers per agent.** Our agents drive Windows `python.exe`, drvfs paths and a Windows game over WSL interop. Containers break those paths and add another failure surface. Idea 3 gets the isolation that matters (a private, bounded TMPDIR and a quota) without them. Rejected.
- **Google's 50% toil cap as written.** It is a cap on human engineers' time, and we have none. Idea 5's error budget, counted in tokens and place-hours, is the translation. Rejected as written, folded into idea 5.

## Detail per idea

### 1. Three-way verdict plus a health check before each proof

**What it is.** Device labs keep "the lab broke" apart from "the test failed".
- LAVA has `InfrastructureError`, `JobError` and `TestError`, and it takes a device out of scheduling when a golden "health job" fails ([LAVA health checks](https://docs.lavasoftware.org/lava/technical-references/configuration/health-check.html), [LAVA error types](https://docs.lavasoftware.org/lava/technical-references/job-definition/actions/test.html)).
- Android Tradefed moves a device through `CHECKING_AVAILABILITY` before `ALLOCATED`, and reports invocation failures separately from test failures ([Tradefed device manager](https://source.android.google.cn/docs/core/tests/tradefed/architecture/device-manager?hl=en)).
- AWS Device Farm reports `ERRORED` apart from `FAILED` ([API](https://docs.aws.amazon.com/devicefarm/latest/APIReference/API_Test.html)).
- Firebase Test Lab retries infrastructure errors and marks a run `INCONCLUSIVE` ([FAQ](https://firebase.google.com/docs/test-lab/troubleshooting?hl=en)).
- OpenHTF separates `FAIL` (a measurement) from `ERROR` (execution) and `TIMEOUT` ([outcomes](https://github.com/google/openhtf/blob/master/openhtf/core/test_state.py)).

**What we have.** `relentless_live.py` already returns a `refused` kind for proof and site refusals, prints UNMEASURED instead of 0, and retries an UNDEPLOYED result "on another game only". `relentless_live.py` line 621 already treats a plan that failed or timed out as the harness's fault ("it may pass in a minute, so no game stamp"). The live-debugging skill already teaches MOD/SITE/HARNESS. So the idea is partly in place, but it is not one enforced verdict type. Today three harness faults still reached the item as FAIL.

**What to add.**
- (i) One verdict enum on every live result: PASS, FAIL or INFRA. FAIL is allowed only after the health check passed. INFRA covers health-check failures, refusals, an unreachable bridge, a deploy mismatch, and exceptions raised in harness code before the item's first proof step. That rule is applied by construction, never by a worker's judgement. Anything after the first proof step stays FAIL, including a game or bridge crash, because a mod can cause those. At most, the crash case gets one re-run on a fresh game before it counts.
- (ii) A health check before each proof, run by the same interpreter that will drive the game: bridge ping, deployed-hash-equals-built-hash for every mod the item's commit touched, and the site preflight.
- (iii) INFRA charges no strike in `relentless_strikes`, starts no review and pays no worker. It retries on the next healthy game, at most twice. After that it becomes a harness item rather than looping. Every INFRA result counts against the pipeline's error budget (idea 5).
- (iv) Two INFRA results in a row take the game out of scheduling until a canary passes (idea 6), as LAVA does.

**Expected value.** About 1M tokens for each fault this would have caught. There were three today. Just as important, a FAIL becomes far more likely to mean the mod is wrong. It cannot prove that, because a mod can still break the harness after the check. But the strike ladder and blind review would stop arguing with the commonest harness noise.

### 2. A deadline on every external call

**What it is.** Google SRE's rule is that every RPC carries a deadline and the deadline propagates to whatever it calls ([SRE book, cascading failures](https://sre.google/sre-book/addressing-cascading-failures/); [gRPC deadlines](https://grpc.io/docs/guides/deadlines/)). A job's deadline also bounds its retries and its cleanup, and the whole process tree gets killed when it expires.

**What we have.** Many callers do pass `timeout=`. `role_launch.py` stops a run at `run_max_s`. There is a lesson on the robocopy default (`infrastructure/state/lessons/20261103T091148Z-BENCH-robocopy-s-default-r-1000000-w.md`). But nothing enforces any of this.

**Measured today.** An AST scan of non-selftest `.py` under `rimflow/` and `Utils/` counts **325** blocking `subprocess.run/check_output/check_call/call` calls, of which **130** pass no `timeout=`.
- The top files are `seat_sync.py` (8), `publish.py` (6), `winbuild.py` (5) and `rimflow/cli.py` (3).
- The scan does not count `Popen`, `os.system` or PowerShell. The real number of unbounded calls is therefore higher.
- Many of the 130 are local git calls that rarely hang. The ones that cross into Windows or the network (git push, `python.exe`, robocopy, codex) are the ones that matter.

**What to add.**
- (i) A selftest that fails on any new `subprocess` call without `timeout=`. The existing 130 calls go on an allowlist that has a burn-down date. The external-facing calls (push, `python.exe`, robocopy, codex) come off it first.
- (ii) A `run_bounded()` helper that kills the whole process tree on expiry and reports a timeout as INFRA.
- (iii) A lint that refuses `robocopy` in any `.py` or `.ps1` unless it has small `/R:` and `/W:` values (for example `/R:2 /W:5`). The call must also run inside a total deadline, because a bounded retry count alone does not bound the copy.
- (iv) The Dispatcher's restart gets its own total deadline. A restart that has not finished in N minutes kills the stuck process tree, recovers the seat and alarms, instead of waiting.

**Expected value.** The 4 h seat stall today. Hangs never announce themselves, so the true count is unknown and likely larger.

### 3. Per-place quotas and ephemeral scratch

**What it is.**
- Ephemeral runners: a GitHub Actions `--ephemeral` runner deregisters after one job, and the operator's own automation wipes the machine ([docs](https://docs.github.com/en/actions/reference/runners/self-hosted-runners)). Buildkite `disconnect-after-job` plus lifecycle hooks does the same, and its docs warn that cleanup in `pre-exit` can be interrupted, so a supervisor must reconcile afterwards ([Buildkite hooks](https://buildkite.com/docs/agent/hooks)).
- Admission and quotas: Borg admits a job only against quota and kills a task that exceeds its disk or RAM limit ([Borg paper](https://research.google.com/pubs/archive/43438.pdf)). A per-job tmpfs takes a byte and inode cap and vanishes on unmount ([kernel tmpfs](https://www.kernel.org/doc/html/v6.4/filesystems/tmpfs.html)).
- Explicit retention: Nix keeps a store path alive only while an explicit GC root points at it ([Nix GC roots](https://nix.dev/manual/nix/2.35/package-management/garbage-collector-roots)).

**What we have.**
- The pool cap (16 clones / 70 GB, owner card 2026-11-02).
- `min_mem_available_gb` admission and the `step_back_mem_gb` step-back.
- `relentless_disk.py` warm clones.
- `scratch_reap.py`, which runs hourly, bundles before it deletes, and already scans `/tmp`.
- Per-session scratchpad dirs for seats.

What is missing:
- The reaper works after the fact and runs hourly, while /tmp filled in less than that.
- Admission checks memory but not free `/tmp` or the pool's GB.
- A clone is held by what its history looks like (trailing commits) rather than by an explicit root.

**What to add.**
- (i) Each place's process tree gets `TMPDIR` set to a directory inside its own clone or scratch. The directory is deleted when the place is released, the way an ephemeral runner is.
- (ii) Enforcement while running, not only at launch: every tick the supervisor measures each place's TMPDIR and clone, and stops any place over its byte budget. A per-place tmpfs with byte and inode caps would be the stronger version, but it needs root. Before every launch there is also an admission check: free space on `/tmp`, on the VHDX and in the pool budget must each stay above a reserve floor. Otherwise nothing launches, and an alarm says why.
- (iii) Clone retention by explicit root, Nix-style. A clone is kept only while a lease, an unpushed bundle or a quarantined check names it. Trailing state-only commits are pushed or bundled at release and never pin the clone.
- (iv) The reaper stays as the reconciler, not the primary cleanup.

**Expected value.** Failures (a) and (b) both happened today. (a) left 2 of 8 places idle. (b) made 58 nightly tests red, which hides real reds and feeds (e).

### 4. Build cop: every red gets an owner and a deadline

**What it is.**
- Google's TAP keeps presubmit fast and tests affected targets afterwards. A named Build Cop drops everything else to get a broken build green, preferably by rollback ([Software Engineering at Google, ch. 23](https://abseil.io/resources/swe-book/html/ch23.html)).
- Uber's Testopedia files a ticket with a deadline to the owning team for every unhealthy test ([Uber](https://www.uber.com/es/en/blog/flaky-tests-overhaul/)).
- Meta files tickets to declared owners when a test's flakiness score regresses ([Meta PFS](https://engineering.fb.com/2020/12/10/developer-tools/probabilistic-flakiness/)).

**What we have.** `known_reds.py` lets a red be parked only after `known_red_after_nights` consecutive red nights, only with an OPEN item, and only with an expiry. That is good, Uber-like discipline for parking a red. What is missing is the other half: nothing forces a new red to get an item, and nothing makes that item jump the queue.

**What to add.**
- (i) The nightly auto-files one item per new red. A batch with one root cause, such as (b), files one item: group by first error line, the way Uber groups by target or regex.
- (ii) Those items sit at top priority for Relentless. Any red still unfixed past its deadline alarms by class, owned or not. Filing an item makes a red owned, but it does not count as fixed.
- (iii) When a red came from a known commit, try rollback first, the Build Cop rule.

**Expected value.** About 44 real defects get worked, and the nightly RED means something again. The `known_reds.py` docstring says RED was red "14 of 14 nights".

### 5. Pipeline SLOs, error budget, class-fix postmortems

**What it is.**
- SLOs with an error-budget policy: when the budget is spent, feature work stops and reliability work runs ([SRE workbook, error budget policy](https://sre.google/workbook/error-budget-policy/)).
- The toil cap: operational work is held to 50% of an engineer's time ([SRE book](https://sre.google/sre-book/service-best-practices/)).
- Blameless postmortems: each action item has an owner, a tracking id and a verifiable end state ([SRE workbook, postmortem culture](https://sre.google/workbook/postmortem-culture/)).

**What we have.**
- `rimflow_metrics.py` (flow, wait and heat from the ledger).
- `incident.py` (told-to-recovered records).
- `alarm_census.py` (every alarm kind the source can raise).
- `lessons.py`.
- No design doc defines an SLO or an error budget.

**What to add.**

Four SLIs, each computed from the ledger:
- the INFRA share of live runs, from idea 1;
- tokens spent on INFRA or harness-caused work per day;
- the count and oldest age of open nightly reds, owned or not, from idea 4;
- pool and disk headroom at launch time, from idea 3.

The rules that go with them:
- When any SLI is over budget for 24 h, Relentless staffs only pipeline items until it recovers. This replaces "the owner notices".
- An incident or a twice-seen alarm is closed only with a class fix: a guard test or lint that fails on the whole class, and is shown failing on the instance before the fix lands. `alarm_census.py` can then flag an alarm kind that keeps recurring without a guard.

**Expected value.** This is what turns (f) into a rule. Without it, ideas 1-4 slowly lose to new instances.

### 6. Test the tester: canary plus fault injection

**What it is.** Google's DiRT runs deliberate, controlled outages to prove that recovery works ([Google Cloud blog](https://cloud.google.com/blog/products/management-tools/shrinking-the-time-to-mitigate-production-incidents)). LAVA's golden health job is a known-good job that has to pass before a device takes work. The SRE book's testing chapter asks that the tooling itself be tested ([SRE book, testing for reliability](https://sre.google/sre-book/testing-reliability/)).

**What we have.** `selftest_preflight_bridge.py` and `selftest_proof_preconditions.py`, plus many mutation and fuzz selftests for mods. What is missing is a planted-fault suite for the live harness and a canary proof.

**What to add.**
- (i) Offline harness tests with planted faults: bridge down, mod not deployed, preflight refuses, `/tmp` full, robocopy hangs. Each must yield INFRA, not FAIL.
- (ii) A tiny known-good canary proof (a 90 s quicktest) run when a game comes up and after any two INFRA results in a row.

**Expected value.** The next new harness fault gets caught before a real item pays 1M tokens for it.

### 7. Flakiness score, rerun-on-fail, expiring quarantine

**What it is.** Meta's probabilistic flakiness score estimates how likely a test is to fail on a good commit, and it uses only ordinary CI history ([Meta](https://engineering.fb.com/2020/12/10/developer-tools/probabilistic-flakiness/)). Google auto-quarantines very flaky tests out of the critical path and files a bug, and it warns that quarantine can hide real bugs ([Google Testing Blog](https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html)).

**What we have.** `known_reds.py`, which works by nights and not by probability. `run_selftests.py` runs the timing-sensitive `selftest_render.py` in isolation after the parallel pool. Relentless has a narrow retry for the WSL `accept4` flake.

**What to add.** Rerun a nightly red once, in isolation. Red twice means broken: send it to idea 4. Red then green means flaky: give it a score and a quarantine with an expiry, owned by an item.

**Expected value.** Medium. It separates noise from real reds before idea 4 assigns them.

### 8. Test impact selection from declared inputs

**What it is.** Bazel `rdeps` selects the tests whose declared dependencies include a changed file ([Bazel query](https://bazel.build/query/language#rdeps)). Bazel then skips tests whose inputs did not change (`--cache_test_results`) ([reference](https://bazel.build/reference/command-line-reference#flag--cache_test_results)).

**What we have.** `selftest_cache.py`'s `DECLS` already lists every cached test's inputs, and `run_selftests.py --only` exists.

**What to add.** Invert `DECLS` into `run_selftests.py --affected <paths|sha>`, which picks the tests whose declared inputs a change touches. Undeclared tests still run. This gives builders and checkers the right test set without guessing.

**Expected value.** Medium. Faster pre-commit, fewer tokens per item, and fewer "ran the wrong tests" closes.

### 9. Treat the game as a lab device

**What it is.**
- Tradefed's explicit device states: `AVAILABLE`, `CHECKING_AVAILABILITY`, `ALLOCATED` and `UNAVAILABLE`.
- Chubby's sequencers, also called fencing tokens: a lock holder passes a token that the resource checks, so a stale holder is refused ([Chubby](https://research.google.com/archive/chubby-osdi06.pdf); [Kubernetes Lease](https://kubernetes.io/docs/concepts/architecture/leases/)).

**What we have.** `driver_lock.py` (an O_EXCL PID lock that holds only one winner) and ledger leases with a 45-minute TTL.

**What to add.** One recorded game state (UP and healthy, LOADING, DEPLOYING, SICK or DOWN) that live rounds read before they spend anything, plus a lock generation number that the bridge client sends and the driver checks.

**Expected value.** Medium. It removes another class of "ran against the wrong or sick game".

### 10. A light merge-queue check

**What it is.**
- bors' "not rocket science" rule: test the merged result, then advance main ([bors](https://bors.tech/)).
- The GitHub merge queue ([docs](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue)).
- Uber's SubmitQueue ([EuroSys 2019](https://lethain.com/static/blog/2019/eurosys19uber.pdf)).
- Chromium's CQ ([docs](https://chromium.googlesource.com/chromium/src/+/HEAD/docs/infra/cq.md)).

**What we have.** `land.sh` replays one commit onto `origin/main`, path-checked and conflict-refusing. `isolated_evidence.py` re-runs checks at the item's close sha. Nobody tests the integrated main that results from 8 places landing side by side.

**What to add.** After each batch of landings, a check run (idea 8's affected set) on the new `origin/main`. A red here is filed against the landing pair, with rollback first. Do not build a pre-merge queue yet.

**Expected value.** Low to medium today, and rising with throughput.

### Also seen, not ranked

LLM-agent harnesses (SWE-agent and SWE-bench containers, OpenHands sandboxes, Codex cloud environments checked out at a fixed sha) verify agent output by applying the patch in a clean environment and running the repository's tests ([SWE-agent paper](https://papers.nips.cc/paper_files/paper/2024/file/5a7c947568c1b1328ccc5230172e1e7c-Paper-Conference.pdf); [SWE-bench reporting](https://github.com/SWE-bench/SWE-bench/blob/main/swebench/harness/reporting.py)). We do a version of this: `isolated_evidence.py` re-runs checks in a private checkout of the close sha, from a non-builder seat, with no AI. That pins the source and the seat. It does not isolate host tools or outside state, so it is not hermetic in Bazel's sense.

The lesson from Anthropic's and OpenAI's agent-eval guidance is idea 1 again: score only valid trials, and publish the infrastructure-invalid rate beside the score ([Anthropic](https://www.anthropic.com/research/demystifying-evals-for-ai-agents); [OpenAI](https://developers.openai.com/api/docs/guides/agent-evals)). GPT notes that SWE-bench's own infrastructure flags are advisory and are not removed from scoring. That is the trap idea 1 avoids.

## What we already have (checked in the repo, 2026-11-03)

| Practice | Our partial version |
|---|---|
| Content-addressed action cache (Bazel) | `src/RimMandrake/Utils/selftest_cache.py`: a declared-input sha256 PASS cache |
| Leases with TTL (Chubby, Kubernetes) | `src/RimMandrake/rimflow/lease.py`: 45 min TTL, renew about every 10 min |
| Exclusive device lock | `src/RimMandrake/rimflow/driver_lock.py`: O_EXCL file plus PID liveness |
| Independent verification of output (source pinned, not hermetic) | `src/RimMandrake/rimflow/isolated_evidence.py`: private checkout of the close sha |
| Flaky and red quarantine with expiry | `src/RimMandrake/Utils/known_reds.py` |
| Post-crash integrity | `src/RimMandrake/rimflow/relentless_integrity.py` |
| Circuit breaker on repeated failure | `src/RimMandrake/rimflow/relentless_strikes.py`, `src/RimMandrake/rimflow/circling.py` |
| Build-farm GC | `src/RimMandrake/Utils/scratch_reap.py` (hourly, bundles before deleting), `src/RimMandrake/rimflow/relentless_disk.py` (warm clones) |
| Admission control | pool cap 16 / 70 GB and the memory floors in `src/RimMandrake/rimflow/relentless_rules.json` |
| Incident tracking and alarm inventory | `src/RimMandrake/rimflow/incident.py`, `src/RimMandrake/rimflow/alarm_census.py`, `src/RimMandrake/Utils/lessons.py` |
| Pipeline metrics | `src/RimMandrake/Utils/rimflow_metrics.py` (no SLO or budget defined on them) |
| Infra-vs-test separation | `refused` kind, UNMEASURED, and UNDEPLOYED retry in `src/RimMandrake/rimflow/relentless_live.py` (not yet one enforced verdict) |

## Sources

All of these were opened or confirmed by GPT's web survey on 2026-11-03. Where GPT could not verify a detail, it says so in the text above.

- Bazel caching and sandboxing: https://bazel.build/remote/caching, https://bazel.build/docs/sandboxing, https://bazel.build/query/language#rdeps, https://bazel.build/reference/command-line-reference#flag--cache_test_results
- Buck2 remote execution: https://github.com/facebook/buck2/blob/main/docs/users/remote_execution.md
- Pants: https://www.pantsbuild.org/dev/docs/introduction/how-does-pants-work
- Google CI and TAP (Software Engineering at Google, ch. 23): https://abseil.io/resources/swe-book/html/ch23.html
- Google flaky tests: https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html
- Meta probabilistic flakiness: https://engineering.fb.com/2020/12/10/developer-tools/probabilistic-flakiness/
- Meta predictive test selection: https://arxiv.org/abs/1810.05286
- Uber flaky-test overhaul: https://www.uber.com/es/en/blog/flaky-tests-overhaul/
- Uber SubmitQueue: https://lethain.com/static/blog/2019/eurosys19uber.pdf
- bors: https://bors.tech/
- GitHub merge queue: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue
- Chromium CQ: https://chromium.googlesource.com/chromium/src/+/HEAD/docs/infra/cq.md
- GitHub ephemeral runners: https://docs.github.com/en/actions/reference/runners/self-hosted-runners
- Buildkite hooks: https://buildkite.com/docs/agent/hooks
- Nix GC roots: https://nix.dev/manual/nix/2.35/package-management/garbage-collector-roots
- Chubby: https://research.google.com/archive/chubby-osdi06.pdf
- Kubernetes Lease: https://kubernetes.io/docs/concepts/architecture/leases/
- Borg: https://research.google.com/pubs/archive/43438.pdf
- tmpfs: https://www.kernel.org/doc/html/v6.4/filesystems/tmpfs.html
- SRE error budget policy: https://sre.google/workbook/error-budget-policy/
- SRE toil and service practices: https://sre.google/sre-book/service-best-practices/
- SRE postmortems: https://sre.google/workbook/postmortem-culture/
- SRE cascading failures and deadlines: https://sre.google/sre-book/addressing-cascading-failures/
- gRPC deadlines: https://grpc.io/docs/guides/deadlines/
- SRE testing for reliability: https://sre.google/sre-book/testing-reliability/
- DiRT: https://cloud.google.com/blog/products/management-tools/shrinking-the-time-to-mitigate-production-incidents
- Tradefed device manager: https://source.android.google.cn/docs/core/tests/tradefed/architecture/device-manager?hl=en
- Firebase Test Lab: https://firebase.google.com/docs/test-lab/troubleshooting?hl=en
- AWS Device Farm: https://docs.aws.amazon.com/devicefarm/latest/APIReference/API_Test.html
- OpenHTF: https://github.com/google/openhtf/blob/master/openhtf/core/test_state.py
- LAVA: https://docs.lavasoftware.org/lava/technical-references/configuration/health-check.html, https://docs.lavasoftware.org/lava/technical-references/job-definition/actions/test.html
- SWE-agent: https://papers.nips.cc/paper_files/paper/2024/file/5a7c947568c1b1328ccc5230172e1e7c-Paper-Conference.pdf
- SWE-bench reporting: https://github.com/SWE-bench/SWE-bench/blob/main/swebench/harness/reporting.py
- Anthropic, agent evals: https://www.anthropic.com/research/demystifying-evals-for-ai-agents
- OpenAI, agent evals: https://developers.openai.com/api/docs/guides/agent-evals
