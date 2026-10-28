# Live Fixer: one seat, one ticket, one rig, no shuttle (proposal, 2026-10-28)

Status: **PROPOSAL** for `LIVE_FIXER_DESIGN_ONE_SEAT_NO_SHUTTLE`. Nothing here edits the v3 design of record or the
responsibilities doc; §8 drafts the lines to add there once the owner rules. Author: BENCH design helper.
Evidence folder: `D:\ClaudeWork\rimmandrake\live_fixer\` (`jobs_all.tsv`, `roundtrips_items.txt`, `show_*.txt`).

## 0. The brief, in his words

> *"Agreed. Foundry mode, it does NOT require me to be sitting there. Conductor can do it with me live when I need it
> as a human, as is it's function. That isn't what I'm talking about: this is an automated process for the toughest
> bugs that keep getting sent around, or do get something done swiftly. I'm intrigue about it happening on
> SteveLaptop to be honest. A second Foundry appearing to do some aggressive debugging might be very handy. Something
> for you to think about."* (ledger OWNER note 2026-10-28T01:43:50Z) — and *"Yes SteveDesktop sorry."* (01:47:17Z)

So: unattended (never needs him), for (a) bugs that keep round-tripping and (b) work wanted swiftly. The Conductor's
session mode stays the human-live version and is out of scope.

## 1. What tonight actually cost (MEASURED unless labelled)

Sources: testq `done/` records (246 jobs, 2026-10-26T00:35Z..10-28T01:48Z, extracted to `jobs_all.tsv`) and the
ledger history of `EXCAVATION_COMPONENT_DIAGNOSE_TICK_SPIKES` (`show_EXCAVATION_*.txt`).

**The excavation loop, r12..r18.** Seven live rounds; every one failed the item's own bars (r18: mean 0.66-0.88
ms/tick against <0.2; max 143.9 dry / 161.9 setup against <20), and every round ended with notes and new child items
(r18 filed `LEVELLING_TICK_DIAGNOSE_DRY_GC_SPIKE` and `SHEETRAIN_DOPULSE_TAME_DELUGE_SPIKE`).

| round | offline fix published | live verdict | fix → verdict | verdict → next verdict |
|---|---|---|---|---|
| r12 | 07:22 (990e5e7de6) | 08:01 | 39 min | — |
| r13 | 17:37 (3cd6c1a3bd) | 18:20 | 43 min | (10 h gap, seat elsewhere) |
| r14 | 19:06 (8b694dddba) | 19:54 | 48 min | 94 min |
| r15 | 20:30 (ca52660b44) | 21:08 | 38 min | 74 min |
| r16 | 21:53 (3654f0046c) | 22:51 | 58 min | 103 min |
| r17 | 23:35 (f7ab43142a) | 00:19 | 44 min | 88 min |
| r18 | 01:44 (b1cc4c3409) | 02:25 | 41 min | 126 min |

- **Verdict-to-verdict, r13→r18: median 94 min, 8 h 05 min for five rounds** (MEASURED).
- Of each fix→verdict, the **cold full-list (321 mods) Steam relaunch costs 12-13 min** (MEASURED from
  `bench_live_r16/r17/r18\PROGRESS.md`: 15:15→15:27, 23:39→23:51, 02:03→02:16); the rest is the measurement windows
  (four to six windows of ~4000 ticks).
- Correction to the framing of the brief: these live rounds were **already one seat** (BENCH on Archmagi, holding the
  bridge). What shuttled was everything around them: each round also sent a testq `guard` job to SteveDesktop
  (5 jobs, submit→ingest 10, 11, 30, 20 and **105** min; the last finished at 00:06 and was ingested at 01:20, a 74 min
  ingest stall, the night the sparse dispatch clone broke the tick), and each verdict became notes plus new child
  items that waited for the next pickup. The 10 h r12→r13 gap is the seat doing other work.

**The testq shuttle in general** (item-attached jobs, `roundtrips_items.txt`):
- rig turnaround, submit→ingest: **median 19.8 min** (n=50, p25 9.9, p75 38.1, max 104.8).
- builder turnaround, ingest of job n → submit of job n+1 at a new sha: **median 63 min** (n=16, p25 13, p75 111,
  max 374).
- So one shuttle round trip is **~83 min median** (MEASURED sum of the two medians; ESTIMATE as a typical trip, the
  two distributions are not joined per trip). 14 items had ≥2 testq jobs in 50 h.
- Lane load: 114 jobs started on 10-27 (105 `guard` filler, 6 `fix`, 3 `sweep`), 19.0 busy h, **6.0 jobs per busy
  hour** (MEASURED). That is lane capacity a lease withholds; how much work it really displaces (filler that is simply
  not run vs fix jobs delayed) is UNMEASURED.

## 2. Shape: Fixer mode

One headless Claude session holds **one ticket + one rig lease + one timebox** and runs the debugging ladder
(`design/RimMandrake/debug_process.md` §3) itself: edit → build → deploy → load → measure → read → fix, with no ticket,
ingest or Dispatcher hop between iterations. It ends in one of three ways: **done claim to the Arbiter**, **timebox
handoff**, or **abort** (§5). It never closes its own item.

Two placements, one mode:
- **Steve fixer (the default, the owner's "second Foundry on SteveDesktop").** The session runs ON SteveDesktop, next
  to the game it drives. Archmagi and his game are untouched; he can be playing.
- **Archmagi fixer.** Same mode on Archmagi's game, only under the existing rules: never while he plays, Dispatcher
  fences it before his session writes (responsibilities doc, orphan home #4). Use only when the bar needs Archmagi
  (§4.4) or SteveDesktop is down.

Lane: the fixer inherits the lane of its ticket. A FlowWorks/GSS ticket (`flowworks_lane.json`) makes it a
**bench-lane fixer**, accountable to the Conductor, never Foundry (standing 10-23 ruling); any other ticket makes it a
Foundry-lane fixer. Its seat stamp is its own (`FIXER`, §4.6) so its commits and events are never confused with the
watched BENCH window or the continuous Foundry.

## 3. Trigger and selection

**Candidates (no AI; the Dispatcher computes them each pass from data it already has):**
1. **Bounced through the rig:** ≥2 testq jobs for the item at different `source_sha` whose ingested result is not
   `pass` (testq `done/`), or ≥2 `verify result=fail` events at L2+ on the item within 48 h (ledger).
   Excavation would have been a candidate at 19:54 (r13, r14 fails), four rounds before r18; it would have been
eligible only once its perf contract existed (§4.4), which it still lacks.
2. **Reopened:** the item is in `rimflow_metrics.py` `bounce.items_3plus` (reopened 3+ in 7 d; F4, MEASURED 7 items).
3. **Swift:** the Producer or the Conductor puts a `swift` note on the item (a rimflow note with `--why`, or the
   Conductor relaying his words with `--owner-said`).

**Eligibility (all must hold, else the candidate waits):** the item has an approved measurement contract (§5.4: the
bar plus what produces the number, with the movement threshold), so "done" is not a judgement made up mid-loop; a
perf item also needs the sampling method of §4.4; the item needs a live game
(`needs bridge`); it is not a flyer-flight item; no other fixer lease is live on the chosen rig; an allowed account
has budget (§4.5).

**Selection:** the Producer orders the candidate list (it owns work order); the Dispatcher grants the lease to the
top eligible one. A `swift` note from the Conductor would jump the Producer's order; that is new scheduling authority over the
Producer's work order and WIP, so it is **the owner's call** (§9); until he rules, `swift` only adds the item to the
candidates. No AI decides whether a lease exists; an AI only orders.
Until the Producer runs (Fri), BENCH orders (holder of the Producer's duties in the activation table).

## 4. Running on SteveDesktop

### 4.1 The rig lease (Dispatcher-granted, time-boxed, one per rig)

Each lease has an id (`L-<item>-<UTC>`); every write below carries it, and nothing undoes state another lease owns.
Grant is a small state machine run by the Dispatcher on Archmagi, reconciled every pass (a crash between steps is
resumed or rolled back from the ledger, never left as a phantom):
1. **requested:** ledger event `lease` on the item with `lease_id`, `host=stevedesktop`, `mode=fixer`, `until=<UTC>`,
   `contract_sha` (§5.4).
2. **draining:** `testq.py pause --reason "fixer lease <lease_id> until <UTC>" --hours H`. This is an intentional
   manual pause with an expiry: the steward's `lane_state()` reports PAUSED-intentional and does not escalate before
   `until` (steward.py header, existing). Genuine faults still win (UNREACHABLE and QUARANTINE are checked first,
   rightly). Pausing stops admission only: an attempt already running finishes. The Dispatcher waits until no
   attempt is running (the worker has released the machine's guard) before step 3.
3. **active:** start the session as ONE process tree under the guard:
   `systemd-run --user --unit rm-fixer-<lease_id> ... host_guard.py run --seat FIXER --for <lease_id> -- <session>`.
   `run` holds the guard for that process tree and frees it when the tree exits. (A CLI `take` would NOT do this: it
   holds for the calling window, host_guard.py `main`.) A worker start that finds the guard held answers exit 75 busy
   and the job stays pending (worker.py). If the guard is taken between drain and `run` (a race), the grant goes back
   to draining; it is a deferral, not a failure. **Handover race (owed fix):** today a worker start can pass its
   guard check and then lose the guard, and it publishes a terminal `REFUSED/GUARD_HELD` instead of leaving the job
   pending (worker.py `cmd_start` / `Attempt.run`). Worker admission and lease activation must take the same
   host-local admission lock, and a late guard refusal must requeue the job (§7).

**Yield is belt and braces:** the pause stops admission; the guard stops driving. New testq code is needed only for
the lease state machine and ownership checks, not for yield.

**Release** (any end, in this order): the session tree exits, which frees the guard; the Dispatcher confirms the
guard is free and the game is idle or stopped (`rw_game.sh` status; a Windows game process left by a killed WSL tree is
stopped before the lane reopens); only then does it clear the pause, and only if the pause still names its own
`lease_id` (a later pause by someone else is left alone); it writes `lease released`. **Expiry fences driving:** the
unit's `RuntimeMaxSec` is the time REMAINING to `until` at activation (draining eats into the lease, not past it).
The guard only tracks the WSL tree, not a Windows game or driver it started, so the lane is fenced by a host-local
admission fence file (`QHOME`-style, on SteveDesktop) that the worker honours and that only the Dispatcher clears,
after it has seen the tree dead, no Windows game or driver process left, and the game reconciled; the testq pause
then no longer needs to be the fence (it stays, for the steward's view). If the tree is still alive at `until + 5 min`, the Dispatcher stops the
unit and records `lease revoked`. The steward wake's brief must forbid `resume` of a pause that names a live
`lease_id` (owed change, §7).

**What the lease costs the lane:** ~6 jobs per busy hour displaced (§1), almost all `guard` filler. A 3 h lease is
~18 filler jobs (ESTIMATE). Fix and sweep jobs queued for OTHER items wait; the Dispatcher should not grant a lease
while a `fix`-purpose job is pending at priority ≥60 (ESTIMATE rule, owner's call, §9).

### 4.2 Account (never Steven's)

The session runs under **lukas or system**, chosen by the Dispatcher as for any new work (v3 §3: the Dispatcher picks
the account before releasing work). **`steven` is excluded by rule** (memory rule: hands off this week; at most 50%
early in his week and never below 10%). Account switching on SteveDesktop is whole-machine (`claude-account-switch`),
so the Dispatcher must not switch accounts during a lease; it starts the fixer only if the active account is allowed,
else waits. The account name comes from the environment, never from code.

### 4.3 Clone, platform, build, deploy, measure

- **Clone:** a new full, non-sparse clone `~/rm/fixer` on SteveDesktop's WSL ext4, never `~/rm/runner` (the runner
  is detached per attempt and never commits code) and never a sparse clone (the sparse `~/rm/dispatch` clone made the
  filler and gap scan blind tonight: testq.py names `modcheck` and each mod's source as required). Push uses the
  existing write deploy key (`github-rimmandrake-write`; owner card 2026-10-25 *"Push to RimMandrake only"*).
  Before each lease: `git pull --ff-only`; refuse to start on a dirty tree.
- **Windows vs WSL:** the session lives in **WSL** (Claude Code, git, python and systemd are already there per
  `bootstrap_wsl.sh`); the game and `dotnet.exe` are Windows, reached through interop exactly as on Archmagi. No
  Windows-native agent.
- **Build:** `winbuild.py` hard-codes `C:\Users\Mandrake\.dotnet\dotnet.exe` and stages under
  `/mnt/d/ClaudeWork/rimmandrake/build`. SteveDesktop's .NET SDK 8 came from winget (bootstrap.ps1), its Windows
  user differs, and its data root is its own. **Owed build:** read the dotnet path and the build root through
  `rmpaths`/env (item below). Until then the fixer cannot build C# on SteveDesktop.
- **Deploy:** `deploy_custom_mods.py --apply` locally against `$STEVE_GAME_WSL`
  (`/mnt/d/SteamLibrary/steamapps/common/RimWorld`), plan first, as the runner does. A companion or mod DLL needs the
  game down; `rw_game.sh` already stops and starts it there.
- **Bridge:** SteveDesktop's own RimBridgeServer and JawaBench companion (installed by `sync_test_mods.py`). The
  fixer drives only that game; the Archmagi `infrastructure/state/BRIDGE` lock is irrelevant to it. host_guard is
  per machine already.
- **Measure:** modcheck rows and the mod's own proof scripts, and for perf bugs the same profiler windows BENCH used
  (`win.sh`/`win2.sh` method in `bench_live_r1x\PROGRESS.md`). Big artifacts stay on SteveDesktop's storage root;
  only summaries and paths are committed.

### 4.4 What SteveDesktop can and cannot prove (the hard limits)

- **Mod list:** SteveDesktop has the **MINIMAL** list only. Its Steam login has none of our Workshop subscriptions;
  `sync_test_mods.py` copies only `ModsConfig.MINIMAL.xml`'s third-party mods. A bar defined on the full 321-mod list
  (the excavation bars are) **cannot be measured there** until the full list is copied (several GB, plain file copy;
  owed item).
- **Hardware:** SteveDesktop is weaker than Archmagi (owner, 2026-10-24, specs UNMEASURED). **A millisecond bar
  measured on Archmagi does not transfer.** Two routes: (a) calibrate: run one sha's windows on both machines and
  carry a per-window ratio with the bar; (b) iterate on SteveDesktop against relative targets (e.g. "max/mean halved
  against the lease-start baseline on this machine") and do **one** confirmation run on the bar's own machine and
  list before the done claim. Route (b) is proposed; the confirmation run is a normal testq/Archmagi-backfill job or a
  BENCH live round, and the Arbiter rules only on it.
- **Perf bugs are outside the debugging ladder today** (debug_process §4: "performance, intermittent, statistical —
  none yet"). So a perf item is eligible for a lease only once its measurement contract (§5.4) names the workload,
  save, seed, window length, repetitions and the statistical test for "met" and for "moved", approved before the
  grant. Until such a contract exists, perf items stay with BENCH live rounds.
- **DLCs:** every DLC is assumed; whether SteveDesktop's Steam account owns all five is still unverified (bring-up
  plan). The first lease must check it.
- **Behaviour bugs on the minimal list** (most FlowWorks rows) have none of these limits: load is the minimal-list
  cold start, and the same rows testq runs are the bar.

### 4.5 Budget

Hard caps on the unit: `RuntimeMaxSec` = the timebox exactly (the unit ends at `until`, §4.1), and `--max-budget-usd` from the Dispatcher's caps
(precedent: the steward wake, `TESTQ_WAKE_BUDGET_USD` 5 and `TESTQ_WAKE_MAX_S` 2700). Proposed starting values are
the owner's (§9).

### 4.6 Ledger and push

- Its own seat **`FIXER`**, registered like RUNNER, with **one shard per rig**
  (`infrastructure/state/ledger/events/FIXER-<host>.jsonl`): one lease per rig means one writer per shard, and a
  second rig later gets its own shard. Every event carries `lease_id` and `lane=bench|foundry`, so concurrent leases
  and per-lane metrics stay separable.
- **Staying in sync:** it pulls (`--ff-only`, then rebase of its own commits only) before every iteration and checks
  three things on the item before driving: the lease is still live (not revoked), the item is still open and not
  claimed by another seat, and `contract_sha` is unchanged. Any of them false → stop, hand off, exit. A push that
  conflicts is rebased once; a second conflict stops the iteration and is reported in the handoff.
- **Evidence the Arbiter can read:** artifacts stay on SteveDesktop's storage root, but each `verify` event names
  host, path, byte size and sha256, and the summary the claim rests on (rows, window stats) is committed in the item's
  evidence file. The Arbiter rules on committed summaries plus hashes, never on a path it cannot open.
- It commits explicit paths in `~/rm/fixer` and pushes with `./publish` after each green step and at the end (pre-push
  hooks installed in that clone: the dispatch clone lacked them, `TESTQ_DISPATCH_PUSH_ENFORCE_LINT`).
- Events it writes: `start` (lease taken), `note` per iteration (sha, what changed, measured result, evidence path),
  `verify` for each measured run, `file` for findings outside its ticket (never fixes them), and a final `note`
  handing the done claim or the timebox handoff. It never writes `close`.

## 5. Loop guardrails

1. **Timebox:** default 3 h per lease (ESTIMATE from §1: ~2 live rounds at today's 94 min, or ~6-8 minimal-list
   iterations). On the minute, the session stops its iteration, commits what is committable, writes the handoff.
2. **Iteration cap:** 8 build-deploy-measure iterations per lease; also stop at **3 consecutive iterations with no
   movement**, where "movement" is defined in the contract (§5.4) before the grant: a change beyond the run-to-run
   noise measured at lease start, against the **best** result so far, not the previous one, so alternating tiny gains
   cannot reset the count. New diagnostic evidence (a cause located) is logged separately and does not count as
   movement. The debugging ladder applies unchanged inside the lease: GPT consults as early as debug_process §5 says,
   two GPT rounds with no new evidence end the lease (rung 8), and a prior-pass-now-fail STOPs the loop.
3. **Red first, left behind:** before the final fix (debug_process §3 rung 3), it commits a check that reads the bar
   quantity and goes **red for the reported reason** at the lease-start sha (debug_process §0.4). The done claim must cite the red
   run and the green run of the same check. Dead theories become guards or notes in the script. No red check, no done
   claim.
4. **No lowering a bar: the measurement contract is fixed before the grant, and not by the fixer.** The contract
   is the bar text plus what produces the number: the check script and the helpers, selectors, fixtures, save, mod
   list, settings and sampling it runs with. The Producer (BENCH until the Producer runs) writes or approves it;
   the grant records `contract_sha` over those files. The fixer's own red check (item 3) is extra evidence, not the
   bar. At the done claim the **Arbiter, not the fixer, runs the contract at `contract_sha`** against the lease-start
   build and the fixed build (on the bar's own config, §4.4). Any commit in the lease that touches a contract file
   makes the claim **NOT ELIGIBLE** (deterministic gate). The only exception is a correction that keeps or
   tightens what the check detects (rung 5: the old predicate was wrong), reviewed by the Arbiter; any change that
   could loosen the bar needs the owner's word, and either way a new `contract_sha` is pinned before the lease
   continues. A builder lowering its own bar happened this week (recall 0.9→0.8, v3 §1).
5. **Forbidden live actions:** no flyer flight live tests (standing ruling; flyer items are ineligible); no worldgen;
   no edits to Archmagi's game, saves or ModsConfig; no account switching; no Steam UI.
6. **Scope:** one ticket. A finding outside it is filed (`--for` its lane owner), not fixed. FlowWorks findings go to
   BENCH even from a Foundry-lane lease.
7. **Arbiter judges done:** the fixer hands a done claim with: red and green runs of its own check, shas, evidence
   hashes; the Arbiter runs the contract (item 4) and rules (GPT reviewer until it runs). A fail does not extend the
   lease.
8. **Lifetime ceiling, every outcome:** each item carries a count of leases, lease hours and spend across ALL
   outcomes (timebox, abort, Arbiter fail, failed confirmation). Default ceiling: **2 leases** per item, ever. Any end
   short of an Arbiter pass writes a handoff note (cause found or not, best hypothesis, what was ruled out, red check
   path, next experiment). A second lease needs the first to have moved the contract quantity (item 2); at the
   ceiling, or after a lease with no movement, the item is **blocked from automatic regrant** and goes to the
   Conductor as a question for him (the normal channel up, never a page). Only the owner, via the Conductor, lifts
   the ceiling on an item. Two leases without movement = the bug needs design, not more rig time.

## 6. Cost: the fixer against the shuttle

| path | per iteration | label |
|---|---|---|
| testq shuttle (fix → rig → ingest → pickup) | ~83 min median (19.8 rig + 63 builder) | MEASURED medians, sum ESTIMATE |
| BENCH live round on Archmagi, full list (excavation) | 94 min verdict→verdict; 12-13 min of it cold load | MEASURED |
| Steve fixer, behaviour bug, minimal list | ~10-20 min (build+deploy ~3, minimal cold load under a minute on Archmagi, slower here, one run of the rows, reading) | ESTIMATE |
| Steve fixer, full-list perf bug | ~60-80 min (cold load ≥12-13 min on a weaker box, the same measure windows, no pickup wait) | ESTIMATE, and needs §4.4's full-list copy first |

The gain is largest for behaviour bugs on the minimal list (≈4-8× per iteration, ESTIMATE) and smallest for
full-list perf bugs, where the load and the measure windows dominate and the saving is the pickup gap and the guard
job's ingest stall (ESTIMATE 14-34 min per round: 94 MEASURED minus 60-80 ESTIMATE). These comparisons set
unmatched populations side by side (rig times, builder gaps, one item's live rounds); they bound the gain, they do
not measure it. The guard jobs ran beside the live rounds, so their delay was not all on the critical path. The trial
measures it properly: matched items, timed from "ready to fix" to Arbiter pass, confirmation and failures included.

Tokens: a 3 h headless Opus session is the main new cost; it is UNMEASURED. **Trial design:** a fixed cohort (the
first 6 eligible items, ESTIMATE), each item charged with ALL its costs (every lease including failed ones, the
Arbiter runs, confirmations, and any work after a reopen) over a 14-day follow-up from its first lease, against
shuttled items of the same class over the same period. Operations measures wall hours from "ready to fix" to Arbiter
pass, reopens and false passes in the follow-up, tokens per accepted fix (the bring-up plan's Phase 0 metric), and
lane jobs actually delayed. Every enrolled item counts at the 14-day horizon: one still unresolved counts its full
14 days as its wall time, and the share of items reaching an Arbiter pass is reported. Passes if that pass share does
not fall, wall hours fall, reopens and false passes do not rise, and tokens per accepted fix stay within 1.5x the
shuttle's (ESTIMATE threshold, the owner's to set).

## 7. Build list (items to file after the owner rules)

1. Dispatcher: candidate scan (§3 rules), the lease state machine with `lease_id` and reconciliation (§4.1),
   `contract_sha`, the per-item lifetime ceiling (§5.8).
2. testq: the host-local admission fence and the shared admission lock (§4.1), late `GUARD_HELD` refusals requeued;
   `resume` that clears only a pause naming the caller's `lease_id`; steward wake brief forbids clearing a
   live lease's pause; ops_watch `steve` family reports `leased` as its own non-fault state.
3. SteveDesktop: `~/rm/fixer` full clone with hooks; `FIXER` seat and per-rig shard registration; systemd unit
   template; a **startup attestation** written before the first drive of each lease (game and Mods paths, bridge
   identity and port, deployed DLL hashes, mod order, owned DLCs, dotnet version), refusing to start on a mismatch.
4. `winbuild.py` and the build root portable to SteveDesktop (dotnet path, Windows user, data root via `rmpaths`).
5. Full-list mod copy to SteveDesktop (only if full-list perf bugs are to be fixed there) and a calibration run.
6. Measurement contracts: a template (bar, check, helpers, save, mod list, sampling, movement threshold) and the
   Arbiter gate that runs it at `contract_sha` on the lease-start and fixed builds; NOT ELIGIBLE when a contract file
   changed in the lease.
7. Fixer brief (the session prompt): this doc's §4-§5 as rules, the debugging ladder, the handoff format.

## 8. Drafted lines for the design of record (not applied; the owner rules first)

Fixer is an **execution mode with its own row**, not a Foundry duty: its lane comes from the ticket, so it can never
make Foundry hold FlowWorks work, and v3's "the one autonomous builder" stays true of Foundry (the fixer is
lease-bound, one ticket, not continuous).

**`design/RimMandrake/rimflow_v3_2026-10-26.md`, §2 roles table, add a row after Foundry:**

`| **Fixer** (mode) | one ticket + one Dispatcher-granted rig lease + a timebox, iterating live until the Arbiter's contract is met or the lease ends; SteveDesktop by default (design/RimMandrake/live_fixer_2026-10-28.md) | on a lease only; its lane is the ticket's (FlowWorks/GSS → bench lane, accountable to the Conductor; else Foundry lane) | — | the next experiment inside its ticket | close its own item; touch its measurement contract; work outside its ticket; regrant itself |`

**Same doc, §3, after "events (feature claims done → Arbiter; ...)":**

`Fixer leases: the Dispatcher lists candidates by rule (≥2 failed rig round trips or ≥2 L2 fails in 48 h, reopened 3+, or a swift note), only items with an approved measurement contract are eligible, the Producer orders them, and the Dispatcher grants one lease per rig (at most 2 per item, ever, without the owner); testq on that rig pauses for the lease.`

**`design/RimMandrake/rimflow_v3_responsibilities_2026-10-26.md`, new § "Fixer (mode)" after Foundry:**

`- **Duties:** on a Dispatcher lease, run the debugging ladder end to end on one rig (SteveDesktop by default) under seat FIXER: red check before the final fix, at most 8 iterations or the timebox, no change to the measurement contract, findings outside the ticket filed not fixed, a handoff note on every end short of a pass, done claim to the Arbiter, who runs the contract. Lane is the ticket's: a FlowWorks/GSS ticket is bench-lane work accountable to the Conductor.`
`- **Metrics:** | X1 | fixer yield | leases ending in an Arbiter pass ÷ leases; wall hours from ready-to-fix to pass; tokens per accepted fix (all lease costs charged) vs shuttled fixes; reopens in 14 d | ledger lease + verdict events; account_usage per unit | UNMEASURED: not built |`

**Same doc, Producer duties, append:** `write or approve the measurement contract of each fixer candidate; order the fixer candidates.`

**Same doc, Dispatcher duties, append:** `compute fixer candidates by rule; grant, release, revoke and reconcile fixer leases (one per rig, lease_id, contract_sha, lifetime ceiling); pause and reopen the rig's testq lane for its own lease only.`

**Same doc, Part 3 gap check, add row:** `| tight live fix loop on one ticket | nobody (shuttles through testq and pickups) | Fixer mode: contract by Producer, lease by Dispatcher, verdict by Arbiter |`

## 9. The owner's decisions

1. **Lane:** a FlowWorks ticket in Fixer mode runs as a bench-lane fixer (seat FIXER, accountable to the Conductor),
   not Foundry. Does that satisfy the 10-23 "BENCH owns all FlowWorks" ruling, or must FlowWorks never go to a fixer?
2. **Full-list perf on SteveDesktop:** copy the full mod list there (several GB) and accept relative targets plus one
   confirmation run on Archmagi, or keep full-list perf bugs on the Archmagi fixer (only while he is away)?
3. **Starting caps:** timebox 3 h, 8 iterations, 2 leases per item, the USD cap per lease, and how many leases per
   day may pause the testq lane (each 3 h lease ≈ 18 filler jobs).
4. **Account:** lukas or system for SteveDesktop fixer sessions (steven excluded).
5. **Trial pass bar:** fewer wall hours to an Arbiter pass, no rise in reopens, token cost per accepted fix at most
   1.5× the shuttle's — or his number.
6. **Swift:** may a Conductor `swift` note jump the Producer's order (new scheduling authority over work order and
   WIP), or does it only make the item a candidate?

## 10. Sources

- Item and his words: `rimflow show LIVE_FIXER_DESIGN_ONE_SEAT_NO_SHUTTLE` (OWNER notes 01:43:50Z, 01:47:17Z).
- `design/RimMandrake/rimflow_v3_2026-10-26.md` §2-§3; `design/RimMandrake/rimflow_v3_responsibilities_2026-10-26.md`
  (Dispatcher, Foundry, orphan home #4); `design/RimMandrake/debug_process.md` §0, §3, §5.
- `src/RimMandrake/Utils/testq/steward.py` (states, intentional pause, the LLM wake caps), `testq.py` (dispatch clone
  requirements, pause), `infrastructure/stevedesktop/worker.py` (guard-held → exit 75), `src/RimMandrake/rimflow/host_guard.py`.
- `infrastructure/stevedesktop/RUNBOOK.md` (A3 write deploy key, A6 accounts), `sync_test_mods.py` (minimal list),
  `design/RimMandrake/stevedesktop_bringup_plan_2026-10-24.md`; `src/RimMandrake/Utils/winbuild.py`.
- testq `D:\ClaudeWork\rimmandrake\testq\done\` (246 records); `D:\ClaudeWork\rimmandrake\bench_live_r16..r18\PROGRESS.md`.
