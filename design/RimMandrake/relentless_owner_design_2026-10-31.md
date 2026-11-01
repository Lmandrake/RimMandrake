# Relentless owner: the item is the owner, workers are replaceable

Item: RELENTLESS_OWNER_DESIGN_NEVER_LETS_GO. Folds CLOSED_LOOP_PROVE_EDIT_RUN_LOOK_AGAIN (same goal, FOUNDRY's copy).
Owner, 2026-10-31: "assign a subagent to this item that gets followed relentlessly until it's done, no matter how many
times it needs rebuilding, debugging, redesign, live testing... WHATEVER... just don't let go until it's done." and
"Maybe half the items are assigned the "perpetual worker" idea that goes back to the TOP of the queue when they hit a
snag/need restart, not whatever happens now." and "treat this as a parameter to tune in the future."
And on the blind check: "at the end of the cycle there must be a blind checker, that makes sense, just not inside the
debugging loop."

Status: LIVE on this host since 2026-10-31 (`rm-relentless.timer`, store `/home/mandrake/rm/relentless/store`). See section 12 for what was built differently from this text. Inputs read:
`parallel_review_2026-10-31/` (arms, handoff_context, use_now, codex_review, folded_into_operations),
`rimflow/lease.py`, `role_launch.py`, `dispatcher.py`, `testpilot_route.py`, `Utils/arena/ralph_a_loop.py` (`_recover`:
rebuild state from a signed record, never from memory), `Utils/scratch_clone.py`.

## 1. The shape

- **The owner is the item, on disk.** One record per item in a host-wide store: goal, proof of done, attempts, what was
  learned, spend, fencing generation. Nothing about the item lives only in a worker's head.
- **A worker is one replaceable process** (a headless `claude -p` in a transient systemd unit, the role launch pattern).
  It may die, fill up or wedge. The next worker reads the record, sits in the same clone with the same uncommitted work,
  and carries on.
- **A program follows it.** `relentless.py tick` runs from its own timer, `rm-relentless.timer`, every 2 minutes (a
  program, no AI), out of its own clone, `/home/mandrake/rm/relentless/books`, which it fast-forwards itself. A fault
  here cannot harm the Dispatcher, and a push to main deploys it. It decides nothing about the work; it follows
  `relentless_rules.json`.
- **Done is proven in operation**, by a blind checker at the end of the cycle, on the exact commit, never during the
  debugging loop.
- **A snag, a restart or a lost worker returns the item to the TOP.** There is no parked state and no back of the queue.

## 2. Where things live

| Thing | Where | Why |
|---|---|---|
| Rules (share and every limit) | `src/RimMandrake/rimflow/relentless_rules.json` | Data, not code. The parameter the owner wants to tune |
| Store | `/home/mandrake/rm/relentless/store/` (ext4, host-wide) | One arbiter for every clone on this host. flock works here, not on drvfs |
| Per-item clone | `/home/mandrake/rm/relentless/clones/<ITEM>/` from `scratch_clone.py` | Keeps WIP across workers, isolates candidates, outside `scratch_reap`'s candidates, never the FOUNDRY tree |
| Ledger | `start`, `note`, `needs`, `close` written as BENCH by the supervisor, in the books clone | The public record. Not the lease: 10-minute renewals in git would be noise |

Store layout: `items/<ID>/state.json` (written atomically, under the lock), `items/<ID>/attempts.jsonl`,
`items/<ID>/learned.md`, `items/<ID>/receipts/gen<G>.json`, `journal.jsonl`, `reading.json`, `.lock`.

**Threat model.** A worker is honest but may be stale: a process that outlived its lease, or a resumed session. Fencing
stops it landing or completing anything by accident. It is not a sandbox against a hostile agent, and the Codex review's
points about `--no-verify`, an agent editing the store, or candidate code attacking its checker are accepted on that
basis (`design_review.md` findings 1, 2, 4). A commit from a stale worker can reach main only in the check-then-push
window, and it cannot complete the item.

## 3. State machine

```
           enroll (share)
              |
              v
   +------> queued  (fresh: back of the fresh tier; returned: TOP tier)
   |          | lease: gen += 1, launch worker
   |          v
   |       running ---- finish(sha, proof, live) --> candidate --> checking --> closing --> done
   |          |                                                        |
   |          | snag | lost | stale | full                             | FAIL, or live check broken
   |          v                                                        |
   +------ stopping  <-------------------------------------------------+
           (gen += 1 FIRST, then stop the unit, then confirm it is gone)

   held: spend limit or a delegation_policy.md §2 call. Only these two ever reach the owner.
   retired: the ledger closed the item from outside (his drop, a supersede).
```

**Queue order:** returned items first, oldest return first (so two bouncers cannot starve each other), then fresh items
in enrol order. An item the machine cannot run right now (bridge held) keeps its place and the next item runs in this
tick; it is not sent back.

## 4. Fencing and receipts (Codex review finding 3, a requirement)

- `gen` is an integer in `state.json`, bumped under the store lock at every lease and at every return. Every worker
  action (`beat`, `learn`, `contract`, `snag`, `finish`, push) names `--gen`. A wrong gen exits 3, FENCED, and writes
  nothing.
- **Fence first, kill second, re-lease third.** `stopping` bumps gen at once, so a live old worker is already refused
  while it is being stopped. A new worker is launched only after the old unit reads inactive and no process carrying
  its marker remains (`role_launch.stop`, `scan_marked`). KILL after `stop_force_s`. After `stop_quarantine_s` the old
  unit and clone are quarantined and journalled, and the next worker gets a NEW clone, from what was pushed. Two workers
  in one clone is the failure this prevents, and it never parks the item.
- **Publish is fenced at git level.** `prepare` writes `.git/relentless.json` (item, gen) in the item clone, and the
  tracked `infrastructure/githooks/pre-push` asks the store. A stale generation's push is refused. This binds without
  an env var and without the worker's cooperation.
  Residual, stated: check-then-push has a window. A push that lands in it adds commits to main but cannot complete the
  item, because only `finish` under the lock can, and the unit is being killed.
- **`rimflow` is fenced.** `close`, `implemented`, `renew`, `release`, `reclaim`, `claim`, `start` on an item with a live
  relentless lease are refused from any caller but the supervisor. His own `--owner-said` passes; the tick then retires.
- **Durable completion receipts.** `finish` writes `receipts/gen<G>.json` (item, gen, sha, contract hash, evidence, live
  line) under the lock and moves the item to `candidate`. The result never depends on a final notification. The
  supervisor picks it up by reading the store, so a dead parent loses nothing; a receipt whose status write was lost is
  recovered by the tick. Close is idempotent: `closing` is
  persisted first, and a replay finds the ledger already closed.
- **Cross-clone exclusion.** The store's flock is host-wide, so every clone on this machine shares the arbiter (the gap
  `lease.py` names). Off-host clones never hold items in this pool: the pool is the seats in `pool_seats`, on this host.

## 5. Taking FOUNDRY's items without its tree

FOUNDRY may hold an old ledger and an old `rimflow`, and a pull there is not ours to ask. Its code does hold the guard:
`_relentless_guard` refuses `claim`, `start`, `close`, `renew`, `release`, `reclaim` and `implemented` on any status in
its hard-coded `LEASED`, reading the host-wide store with no pull. So the store is the one word both trees hear at once,
and section 13 gives the order that makes it enough.

Deployment meanwhile: the supervisor runs from its own books clone, so a push to main reaches it on the next tick.
Nothing touches `/home/mandrake/rm/foundry`. No code under `src/RimMandrake/Utils/arena/` is changed.

## 6. Failure, then change of approach

Every return names a class: `worker_lost` (unit gone, no receipt), `worker_stale` (silent past `stale_s`, unit up),
`worker_full` (hit `run_max_s`), `no_receipt` (clean exit, nothing reported), `blind_fail`, `live_broken`, or a slug the
worker gave `snag --class`.

- `same_failure_limit` (3) of the same class forces a **change of approach**, never a stop. Order: `pilot` when the item
  needs the live game or the Test Pilot rule routes it (`testpilot_route.judge`, ticket from `rimflow pilot`), else
  `redesign`. The next one flips. The count for that class restarts. The new worker is told the failed approach and
  must write a different one into `learned.md` before it edits.
- `pilot` runs the `rm-testpilot` agent. Flyers' flight is never live-tested: the worker brief says so and the pilot
  brief does.
- A launch that dies at once with no spend (`launch_fail`: auth, quota) is not the item's fault and counts nothing
  against it. `launch_breaker` such failures in a row hold all launches for `breaker_cool_s` and alarm once. Items keep
  their place.
- `blind_fail`'s reasons go to the next worker, because a reason a worker has not seen is not a fix it can make.

## 7. Done means live

The contract (`contract --proof ... [--live ...]`) is set by the first worker before it edits, from the item's text and
criteria, and may be changed only by a `redesign`, which records why. `finish` names a published sha.

The `live` line has the grammar of `folded_into_operations.md` §5:

```
unit=rm-foo.timer reading=<path> max_age=6h
hook=block_foo.py
once: one-off data repair
```

The supervisor decides from the diff, not from the worker: a commit touching a hook, a systemd unit,
`dispatcher_schedule.json` or `ops_watch_rules.json` must carry a `live` line. `live_line.py` is the parser and the
check; LIVE_PROOF_ENFORCE_DONE_MEANS_RUNNING builds `close --live` and the recheck sweep on the same module. The
supervisor runs the check itself after the blind PASS and before the close. A broken line returns the item to the top
as `live_broken`. Ordinary code and game work carries no line, and its proof is the contract.

### The blind checker

One headless unit, `rm-judge`, in its own clean clone at exactly the receipt's sha. It receives the item's text and
criteria, the contract, the diff range and the live line. It never receives `attempts.jsonl`, `learned.md` or the
worker's notes. It reruns the proof, judges the contract against the item's text (a too-easy contract is a FAIL), and
writes its verdict with `verdict --nonce`, where the nonce exists only in its own launch. A verdict for an old nonce or
another sha is refused, so a test is tied to one candidate (Codex finding 5).

## 8. Limits, and what reaches the owner

All in `relentless_rules.json`.

| Rule | Start | Why this number, and when to reconsider |
|---|---|---|
| `share` | 0.5 | Owner: "maybe half". Raise it when closed-per-day from `stats` beats the old route |
| `max_workers` | 10 | The ceiling only: the plan's `total_max` test ceiling. What runs is `staffing.stages` under the budget (section 13) |
| `pool_seats` | BENCH, FOUNDRY | §5, §13 |
| `same_failure_limit` | 3 | Owner-approved safeguard. Pilot cliff: 3 misses, `testpilot_route.py` header |
| `run_max_s` | 3600 | Long enough for a build pass. A full worker is replaced, not lost |
| `stale_s` | 1500 | Silent by beat AND transcript. The 600 s silence rule is per call, so a long test does not trip this |
| `item_spend_limit` | 8M weighted | A set spend limit, approved. Reaching it holds the item and tells the Conductor |
| `day_spend_limit` | 24M weighted | Daily. Reaching it holds launches. Items keep their place |
| `run_reserve` | 1.2M weighted | Outstanding spend is reserved at admission, so two launches cannot pass one floor (Codex finding 4). A run with no measured usage is charged this reserve, never less |
| `min_mem_available_gb` | 6 | Host admission (Codex finding 4) |

**Waste.** `unchanged_returns_limit` (9) returns of any class change the approach too, so rotating slugs do not evade it.
Every run (worker, pilot, checker) is charged. Strict top-of-queue can only keep fresh items waiting as long as a
bouncer's `item_spend_limit` lasts; that bound is deliberate, the owner asked for the top.
`held` is the one stated exception to "never parked": it waits for his word, and its delivery is retried until written.

**Selection.** `target = ceil(share × pool)`, counting items already enrolled. The pool is open, unblocked, not needing
the owner, in `pool_needs`, and not in `pool_kinds_exclude`. Chosen first: raised, then Test Pilot bouncers, then this
deployment, then row order, then oldest. 0 enrols nothing; 1 enrols the whole pool, `enrol_per_tick` at a time and at most `max_queued` waiting (the rest follow as
places free). An item enrolled but not yet started
stays open to the seats: nothing is reserved until a lease is taken, and an item a seat took is skipped.

**Reaching him.** Only two paths, and both go through the Conductor (nothing reaches him unread):
1. `held` for `item_spend_limit`: `rimflow needs <ID> owner`, a line in the Conductor's log.
2. `held` for a §2 call: a worker runs `snag --class owner_call --section <n>`. A §2 line number is required: without
   one it is an ordinary snag, and the item goes to the top.

`--owner-said` lifts a hold (`relentless.py unhold`). Nothing else parks an item.

## 9. Concurrency

Many items, many workers, one lease each. Every transition is a compare-and-set of (status, gen) under the one flock.
Each item has its own clone, unit, marker and session. The tick takes a non-blocking lock, so a second tick exits. The
state file is written by temp and rename. Workers never touch the ledger or each other's files. Clones remove the
shared-tree hazards of `handoff_context.md` Finding 5 and the first Codex finding for this lane: a candidate is the
exact sha a checker reran in a clean tree.

## 10. How it replaces CLOSED_LOOP_PROVE_EDIT_RUN_LOOK_AGAIN

That goal asks one agent to own a problem end to end: edit, run, look, edit again, with a blind check at the end, and to
compare closed items per day with the old route. Sections 1 and 7 are that loop. `relentless.py stats` prints closed per
day through this route against all other closes. CLOSED_LOOP_PROVE_EDIT_RUN_LOOK_AGAIN is superseded by this item.

## 11. Fault table (each has a planted selftest)

| Fault | Result |
|---|---|
| Worker dies | Fenced, `worker_lost`, TOP, fresh worker in the same clone with the same record |
| Same failure three times | Approach changes, pilot or redesign, it does not stop |
| Stale worker writes, pushes or closes after a reassign | Refused, exit 3, nothing written |
| Spend limit | `held`, needs owner, Conductor told, nothing else is held |
| Restart or snag | TOP, ahead of every fresh item, oldest return first |
| `share` 0 and 1 | None enrolled; the whole pool enrolled |
| Tick crash between steps | Receipts and persisted status replay; close is idempotent |
| Two workers race a lease | One wins; the other sees the CAS fail |

## 12. As built

- **The pool is the proposed backlog.** `rank()` offers only items already taken, so the supervisor reads the eligible
  proposed items itself (`pool_order`, priority sort) and enrols `share` of them. `relentless.py enrol --item X --why "..."`
  puts one named item in by hand. An item excluded in the rules leaves the queue at the next tick.
- **The tick itself peaked at 4 to 5 GB of host memory during clones;** see RELENTLESS_TICK_MEASURE_CLONE_MEMORY_PEAK.
- **A worker lives in its scope.** `role_launch` puts it in `claude-seat-BENCH-<unit>.scope`; the `.service` wrapper may
  die and the worker lives on. The supervisor's stop and every kill go to the scope.
- **A worker that reported and then died is lost,** `worker_lost`, not a failed launch: `launch_fail` needs no `last_beat`.
- **The fence carries the session generation** (`RELENTLESS_GEN` in the worker's environment, read by `hook_fence`); a
  checker's nonce expires with its run, and a run is charged once even when it crosses midnight.
- **Alarm items.** An `OPS_` or `LIVE_RESTORE_` item needs a live line in its contract, as `close` would refuse it
  after the blind pass. The candidate gate says so before the check is spent, as `bad_candidate`.
- **Rejected review findings.** Second review, finding 7 (a lease could lose the top place): rejected, a fresh item
  never precedes a returned one in the queue order. A revocation landing after the hook has passed: accepted under the
  honest-but-stale threat model of section 2.

Evidence: `D:\ClaudeWork\rimmandrake\relentless\` (`design_review.md`, `code_review.md`, `code_review2.md`).

## 13. The filler: staffing that needs no head to remember

Owner, 2026-10-31: *"So why is it so hard to keep Foundry staffed?"* Nothing refused it: its budget was 8, it ran one
helper for hours, then seven in three minutes once told. Staffing lived in a head's attention; the Dispatcher rings only
an idle seat, and a seat with one helper reads as busy. Helpers as subagents also grow the head's context and block its
close-out. Workers here are units outside any head, so the fix is to let the tick fill them.

**What it does each tick** (no AI, `relentless.py`, rules block `staffing`):

- **Places:** the current stage under the published budget (`helper_budget.read`, FOUNDRY's N) less the helpers FOUNDRY's
  head runs itself (`allocation.json`). Budget unreadable: the lowest stage, marked `budget_measured: false`. Budget 0: no
  new run; checks of finished work still run. Under 8 GB available: 1. Under 6 GB: none. Share 0 stays his off switch.
- **Enrols by need:** a free place enrols work whatever `share` says of the backlog, under `enrol_per_tick` and `max_queued`.
- **Launches** at most `launch_per_tick` (2), as `prepare` blocks and the tick has a timeout, and none while more than
  `check_backlog_max` (2) candidates wait: verification goes first (Codex finding 8). A candidate already holds a place, so
  a check is never starved of one. The check itself is unchanged and blind: the filler neither reads nor feeds it.

**Staged rise: 3, 5, budget.** A stage rises only with, in that stage's own window: `hold_s` (1 h) at full stage, at least
3 blind verdicts, at most 34% rejected, memory never under 8 GB (a dip restarts the window), no OOM kill (`/proc/vmstat oom_kill`, host-wide, so a
kill by anything counts), burn at most 3%/h if the allocator's reading is fresh. An OOM kill steps one down at once.
Stage state is `store/staffing_state.json`.

**Why above 4 is allowed before plan steps 1-4.** Those guard seat helpers. A worker already has what they build:
receipts on disk, generation fencing, a host-wide store, an exact candidate in its own clone, and a landing path a peer's
dirty file cannot jam. The plan's stop lines stay, in the rise.

**The classes it must not take from FOUNDRY** (`foreign_kinds_exclude`, `foreign_exclude`). `needs` other than offline
never reach the pool, so the bridge and the game are out at the door. Beyond that:

| Class | Why |
|---|---|
| `ready` or `doing`, any lease | Its `next` offers these with no guarded step on some paths. Only `proposed` is safe: a head reaches it through `claim`, which the guard refuses |
| ARENA, TRIAL, TRIO, REPLAY, ARM, RALPH | That tree's live experiment; arena code is not to change under it |
| FLOWWORKS, GSS, HOSE | FOUNDRY's active campaign, in flight in that tree, and it owns FlowWorks and GSS |
| ART, ARTEVAL, SHEET, art kind, sprite, redraw, review sheet | Pipeline and owner-facing; nothing reaches him unread |
| OWNER, LIVE, bridge, in game, cold load | Words in the title that say the game or he is needed, whatever `needs` says |
| design, decision, card, review, finding, trial | A head's judgment, not a worker's. Filing rulings is the head's job |

A worker who finds live need hands back through `needs`, as any worker does. Excluded classes stay with FOUNDRY's head
and its own helpers.

**Exclusion across trees** (Codex finding 3). In the tick, for an item whose owner is FOUNDRY:

1. Pool: refused while its tree has any line about the id that the books lack (raw line difference of its FOUNDRY and
   OWNER shards). A tree that cannot be read or holds a torn line refuses all of that seat's items.
2. Reserve: under the lock the store says `running` with no run. From here its guard refuses claim and start.
3. Wait `settle_s` (15), so a claim that passed the guard just before reaches its shard.
4. Read the unpublished lines again. A word on the id, or a blind tree: back out, `retired`, never taken again. Once the
   ledger already says ours (a crash or a failed launch brought it back), either only waits in `queued`: retired, it would
   strand as ours. Once the word is published the ledger says what it was.
5. `reassign --to BENCH`, then `start`, then launch. A refused take backs out; a refused start stays `queued` under the launch breaker. A crash inside the reservation returns the
   item to the line at the next tick.
6. At the end: closed on the ledger, the store stays `closing` (`tomb_since`, no place held, clones gone) until its tree
   shows that close (parsed: this id, event close, newer than the run), or 48 h pass. Without this a stale head reads `proposed` and no guard, the moment we say done.

Left open, knowingly: an item we gave back after `reassign`, or `retired` while its tree is stale, is unguarded there.
Nobody is working it, so the worst case is a contested claim `next` already names. A queued item returning from a failed
launch, or a take cut short by a crash, goes through steps 2 to 4 again; every launch rechecks the whole eligibility.
Three gaps remain and are accepted. A claim suspended between its guard and its append for longer than `settle_s` lands after
ours; the ledger's earliest claim wins and `next` names the contest. A foreign item waiting `queued` for a retry has no
guard while its tree is stale. After 48 h an unheard tree could claim a closed item, and a head silent for two days is not
racing anyone.

**The reading** is `store/staffing.json`, each tick logged to `store/staffing.jsonl`: budget, stage, target, running k,
ready m, live runs, minutes under, why, check queue, spend. Under means `k < min(target, k + m)`, and also: every place is
a check that cannot start, or the other seat's tree is unreadable with places free. Minutes are watched minutes: a gap
counts at most `tick_gap_max_s`, a pause none. Head helpers unmeasured or budget unreadable mean the lowest stage and no rise. RimPulse shows one health line; a
stale reading says the filler is silent. After `alarm_after_min` (30) one fixed item, OPS_STAFFING_RESTORE_UNDER_BUDGET, is
filed, noted while open, or reopened through RUNNER `live` if done, once per episode. Paused, budget 0 and share 0 are
no alarm: nothing is wrong. A filled stage ends the episode; a done alarm item with no live line just reopens.

**Limits this build did not lift.** `day_spend_limit` stays 24M: a choice for him and the Conductor, and measured 14.4M in
2.7 h at 3 workers (1.8M per worker-hour), 3 workers end it in about 4.5 h of a UTC day, 8 in under 2. When it stops the filler, the reading says
`day_spend_limit` and the alarm goes. Burn at 8 may pass the 3%/h stop line, so the rise may stop at 5, by design.
Queues for heavy tests and Windows builds are not measured (plan step 8). The memory low is sampled at each tick and after
each clone, not continuously; the OOM count catches what it misses.
