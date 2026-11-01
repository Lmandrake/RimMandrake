# The one plan: 8-10 helpers per seat, safely

Checked against live code and `rimflow show`, 31 October, about 18:30 PDT. Not yet safe at 8-10: the lanes still lack a way to test exact work, and a dead helper's result can still be lost. Nothing below is filed by this plan.

## 1. Still open

Removed as shipped: publish lock, rm-deadman, relentless worker, unwakeable alarm fixes, scratch expiry timer (item still `doing`, uncommitted).

- **Replay needs attention now.** Its watchdog timer stopped at 17:15 when the arms were relaunched; the arms have run unwatched for over an hour. The last reading was 1 of 29 accepted; trio died of out-of-memory twice. It very likely misses the 07:00 stop line (ESTIMATE). Its code changed mid-run, on top of the unpinned tree.
- **Close-out still refuses** while any helper lives; no drain state or spawn freeze exists (`seat_restart.py:1808`).
- **Nothing on disk knows the helpers.** No registry, no receipts for seat helpers, no reclaim of a dead helper's lease. An unread final message loses the result.
- **The lease lock is per clone** (`lease.py`), and a reclaimed item has no generation number, so an old holder could still close it.
- **No seat helper tests an exact, stable candidate.** Tests can run on a peer's half-written file.
- **Also open:** 4 of 4 fixes spawned by Ops are unbuilt; nightly reds unhandled; review and test queues unmeasured.
- **Budget:** the session meter has been blank since 00:37. Spend has no per-call key. Automatic account failover can still close every window.

## 2. Ordered work

| # | Step | Filed? | Unlocks | Live proof |
|---|---|---|---|---|
| 0 | Restart the replay watchdog today; read the replay as serial evidence only | No item | Honest replay | Ticks resume |
| 1 | Land shard appends without blocking; stop a peer's dirty file jamming the pull | PUBLISH_SHARDS_FIX_APPENDS_BLOCK_LANDING (shards only; **the code half is unfiled**) | Clones stay level | A clone with dirty peer hunks and shard appends lands |
| 2 | Close-out always records; deferred, not refused; drain and spawn freeze | CLOSEOUT_TRAP_FIX_HELPERS_ALWAYS_ALIVE | Restart at full belt | A real restart with 4 helpers alive loses nothing |
| 3 | Helper registry and durable receipts, read by wake and handoff | **Unfiled** | Survive a dead parent | Kill a parent; its successor collects the result |
| 4 | Fencing generations; host-wide lease lock; auto-reclaim of a dead lease | LEDGER_LEASE_HARDEN_ATTEMPT_TOKEN; **the lock and reclaim are unfiled** | 6 helpers | Old holder refused on close; two clones race `next`, one wins |
| 5 | Exact stable candidate: each writer tests and is accepted at one sha, the relentless pattern | **Unfiled for seats**; relentless has it | 8 helpers | A planted peer edit cannot enter a tested sha |
| 6 | Declared write paths at spawn and commit | **Unfiled** | Fewer collisions | Overlap refused at spawn |
| 7 | One liveness rule (900 s against 1800 s); slot enforcement; shared cap | HELPERS_BUILD_SHARED_CAP_ACROSS_ROLES, HELPER_BUDGET_GATE_ENFORCE_NOT_ASKING_NICELY, SLOT_STREAMS_BUILD_SPLIT_R1_R7, SLOT_HOOK_MEASURE_REFUSALS_AND_PEAK; **liveness unfiled** | Trustworthy slots | Refusals and peak measured |
| 8 | Completion capacity: lighter returns, batched judging, queue lengths for review, tests, Windows builds | **Unfiled** | Checks keep pace | No queue grows for 2 hours |
| 9 | Spend: meter repaired, outstanding spend counted at admission, failover made safe | SESSION_METER_DIAGNOSE_SYSTEM_BLANK; **the rest unfiled** | Budget stop line is real | Meter matches account total |
| 10 | Work supply wide enough for 8 | FOUNDRY_FANOUT_DESIGN_NO_MORE_SINGLE_FILE | Full belts | 8 unrelated items ready |
| 11 | Measured runs at 6, 8, 10, two nights each | **Unfiled** | The ceiling, defended | Collisions, lost commits, accepted per hour, restart success |

Steps 1-4 come before any standing run above 4. Stop lines: burn over 3%/h, an out-of-memory kill, host memory under 3 GB.

## 3. Add-on trial

Filed: TRIAL_PARALLEL_DESIGN_ADD_ON_EQUAL_ALLOWANCE, TRIAL_TREE_PIN_LIVE_CODE_NO_HASH. The N=1 control and spend reconciliation are not in them.

1. **Pin:** one frozen clone, hash recorded for runner, patches, prompts, configuration, inputs, tools and starting revisions. No edits during the run.
2. **Control:** a fresh N=1 at the same time, with the same helper permissions and final acceptance. Effects inside a task are reported apart from parallel tasks.
3. **Envelope:** each arm gets the same role slots (critics, testers and mergers count) and equal CPU and memory. Order is randomised, and cells are repeated where results are close.
4. **Workload:** six tasks with declared dependencies from the two newest eras, landed in dependency order with a final check on the integrated result, N=1 included. Count rejects, conflicts, rework and abandoned attempts.
5. **Throughput:** accepted work per hour from first spawn to drain. Waits are shown, not subtracted. Unfinished work at the cutoff counts as not accepted.
6. **Spend:** an identity on every call, children attributed, shared overhead shown, the sum reconciled to the account total.
7. **Decision, written first:** a level passes if acceptance is within a margin of N=1 that the owner sets, with an uncertainty interval, and accepted per hour rises by more than cost does. Passing at 4 moves that arm to 8; passing at 8 moves it to 10. Failure stops that arm. A win does not switch production alone.

**Cost (ESTIMATE):** 4 arms × N=1, 2, 4 × 6 tasks is 72 task-runs. The power card gives about 2.3-3.5M ITE per serial task-run (174-261M over 75). With helper overhead: 170-500M ITE, one to two normal days of spend. Escalation adds up to 200M. **Time (ESTIMATE):** 2-3 days of harness work, then two to three nights. No measured task rate exists.

**Wait for tonight's replay?** Not for its verdict; it answers a serial question. Wait for two things only: the arms stop changing, and its faults (memory, invalid verdict halts) are fixed.

## 4. Worktree question (for an owner card)

His ruling stands (owner, 2026-10-02, by card): worktrees off. His reasons: duplicate 4 GB checkouts by the hundred, and work stranded on side branches.

**Evidence from tonight (MEASURED, 12:00 to 18:20 PDT):**
- Helpers per clone: 23 in bench, 27 in FOUNDRY; peak 4 writing at once in bench.
- Same file while both helpers were alive: 20 pairs across 9 files, 8 pairs of them on `cli.py` in FOUNDRY. This counts edits and commit commands, so it is a floor.
- Commits lost: 0. All reflog commits since noon appear in history by subject.
- Publish refused on ledger shards about 8 times; none on code.
- One real jam: a helper committed its hunks and left a peer's in `ops_watch.py`. Those hunks are still uncommitted, `./publish` then failed twice, and bench now sits ahead 1, behind 11. One dirty file stopped a whole clone from landing.
- Relentless per-item clones: 9 items done; 7.1 GB now.

| | A. Keep shared clones | B. Bounded pool of about 10 reused clones |
|---|---|---|
| Method | Declared paths, landing fixes | Relentless pattern; sparse; expiry; close requires the sha on origin |
| For | No rule change; deploys and C# builds work as they do | Gives the stable candidate; one helper's dirt cannot jam others; both old failures answered |
| Against | Paths do not isolate tests or shared build outputs; tonight's jam type stays possible | Needs host-wide lease; ledger arrives late; deploys and builds assume the seat clone; about 3.6 GB each until sparse lands (SCRATCH_CLONES_SHRINK_SPARSE_NOT_FULL) |

`git clone` passes the hook, so B needs his word, not a workaround.

**Recommendation: B, narrowly.** Keep `git worktree` banned. Approve the pool for writing helpers above 4, seats unchanged. Stop-condition: revert if a clone strands work or the pool passes 40 GB. No code was lost tonight; the case is exact-candidate testing and the jam.

## 5. Limits still undefended

| Limit | Prevents | Verdict | Revisit when |
|---|---|---|---|
| Relentless `max_workers`. **Live value is 1, not 2**, during the trial | Trial contention | **Loosen:** 2 at trial end, 4 after a clean week | Tick memory peak measured (RELENTLESS_TICK_MEASURE_CLONE_MEMORY_PEAK) |
| `total_max` 10 (never ruled, "never paid") | Unknown | **Keep as test ceiling** | Step 11 passes 10: try 12 |
| Owner cap 2 helpers across roles; headless none | Memory | Keep until the shared cap closes, then **remove** | Step 7 |
| Cruise 6 | Unknown | **Loosen** to 8 after step 5 | Step 11 |
| `session_helpers_max` 3 | Nothing; dead setting | **Remove** | Now |
| FOUNDRY fallback 3 | Silent narrowing | **Loosen:** alarm when in force | Step 7 |
| "Writing helpers one at a time" (hook text) | Overlap | **Replace** with declared paths | Step 6 |
| Close-out needs zero helpers | Lost results | **Remove** after registry | Step 3 |
| Nesting ban; retry caps 4/2/3 | Runaway spend | Keep; measure slots held | Rework share over 25% |
| Harness slice 12 GB; 6 selftest workers; runway floor 0.15 | Out-of-memory, exhaustion | Keep until peaks are measured (ARM_MEMORY_MEASURE_NO_CEILING_SHARED_SLICE) | A combined-load peak exists |
| Spawn hook fails open; never kill mid-turn | Blocked work | **Decide:** reconcile with the watchdog | Step 7 |
