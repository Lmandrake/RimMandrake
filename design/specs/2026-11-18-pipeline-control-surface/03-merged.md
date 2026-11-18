# Pipeline control surface: merged design (Deep-Design-3x2, 2026-11-18)

Inputs: `00-problem.md` (his words), `01-design.md` (pass 1), `02a-gpt-blind.md` (blind external answer),
`02-gpt.md` (external critique, 24 findings), `02m-remeasure.md` (starred claims re-measured). Merge by the
Conductor. Design Version of the control surface: **0.1.0**.

## 1. What every pass agrees on

1. Control state must leave git. A stop order took **21 min 27 s** to bind today (10:20 stop, 10:41:27 first held
   tick) because a hold is a repo file and the live tick runs from another clone (`/home/mandrake/rm/dispatch`)
   [measured twice, two methods].
2. There must be ONE admission point at the place runs start. Today there are **18** `systemd-run` launch sites
   in 12 files, 7 families; the launch functions read no hold, pause or on/off flag [re-measured; pass 1 said
   "about 10"].
3. Consumables are per-run charges that can be released, never bare counters that get decremented.
4. The forecast must call the scheduler's own decision code.

## 2. The options after review

| | Option | Strongest case after review | Came from |
|---|---|---|---|
| B | One control store as JSONL acts + folded view, `admit()` inside the launch primitives, counters as `raw - voids + adjustments` | Smallest build; no new dependency | pass 1 |
| S | One supervised control **service** that owns authorization and launch; reserve-then-settle in one SQLite file; schedulers submit proposals | Closes the pause-versus-launch race and double-spend by serialising everything in one process | GPT blind + critique |
| M | **B's shape with S's substance, no daemon**: one SQLite file (WAL) on ext4, a library every launcher calls, reserve-then-settle typed accounts, a launch-intent row checked again by the unit itself at start, systemd drop-in as containment | Transactions without a new process that must stay alive | this merge |
| E | Migrate ALL pipeline state into one database | Cleanest end state; 2-3 weeks | pass 1 (deferred by all) |

Rejected: A (thin front door over today's stores: keeps publish latency and partial multi-store writes), C as a
whole (its idea, declared limits and order, is kept inside M for the queue and limits; GPT is right that pass 1
rejected it on a false coupling), D alone (containment only: a blocked unit reports success to its launcher
[measured]).

## 3. Recommendation: M

- **Store.** `~/.local/state/rimmandrake/control/control.db` (SQLite, WAL), env `RM_CONTROL_DB` for tests. Native
  ext4, reachable by every clone [measured]. Not on `D:\`: locking there passed inside WSL but is unmeasured from
  the Windows side, and nothing needs it there. Tables: `acts` (append-only audit: id, revision, who, at UTC +
  Pacific, why, owner_said, kind, scope, before, after, idempotency key), `switches`, `queue`, `accounts`
  (mod, design version, stage visit, resource), `grants`, `runs` (unit name fixed BEFORE launch, declared mod, item,
  stage, family, model), `reservations`, `charges`, `voids`.
- **Admission.** `control.admit(spec)` in ONE transaction: check switches by scope (all, mod, stage, item, family,
  role), check every applicable account, reserve, write the run and its launch intent. Refusal consumes nothing
  and raises no failed-launch alarm. All 18 sites go through one `launch_unit()`; a selftest enumerates
  `systemd-run` call sites and fails on any not routed; a mutant launcher must turn it red.
- **The pause race (critique 2), closed by an ordering contract.** `pipe off` commits a new revision and cancels
  every unstarted reservation in the same transaction. Each unit starts with an `ExecCondition` that asks the
  store "is my intent still authorised at the current revision"; if not it exits as REFUSED and its reservation is
  released. So: after `pipe off` returns, nothing that had not already begun executing its payload can begin.
- **Allowances (critiques 3, 8).** `available = grants + adjustments - settled charges - outstanding
  reservations`. A reservation becomes a charge only at **validated settlement**: the run ended and its result
  counts on the mod's merits. Launch failure, kill, stop, no result file, account or harness fault, timeout,
  condition-skip: the reservation is released, the run is classed `fail_system`, and a separate system-fault meter
  (with its own alarm) counts it so a relaunch loop is still caught. Never charge on a launcher exit code
  [confirmed by the re-measure: a skipped unit returns rc 0]. Streaks (Test Pilot's three non-pass in a row) are
  derived from the ordered valid runs, so voiding a middle one is well defined. Existing counters enter as
  explicit opening balances, reconciled against the old readers until those are deleted.
- **Void, grant, set.** `pipe void <run>` releases that run's charges exactly once; `pipe grant <Mod> <resource>
  +N`; `pipe set <Mod> <resource> <N>` writes an adjustment at a revision. "Frozen" and "append-only" are never
  an answer: every change is a later row every reader honours.
- **Undo (critique 16).** `pipe undo <act>` is a compensating act, refused with the list of dependent later acts
  when it is not cleanly invertible. Voiding a run does NOT move a stage back (critique 17): `pipe show` flags
  "stage advanced on a voided run" and the stage move stays a separate, explicit command.
- **Reads.** `pipe show [Mod]` one screen from the store plus the live tick's last reading; `pipe why <Mod>` one
  line: what blocks it or what will start it. Today `rimflow queue CONDUCTOR` prints 1.57 MB and helper status
  83 KB [measured]; both get a compact default (running and today only) and a `--full` flag.
- **Forecast.** `pipe next [30m]`: the tick's own decide/prioritise/admit, imported from the tree the live unit
  runs from, dry, with a simulated clock. Stated limit (critique 19): it forecasts what the scheduler will decide
  from current state; an agent's future result is not knowable and is shown as a branch, not a prediction.
- **Containment.** A systemd prefix drop-in on the run units checks a store-written permit file; unreadable store
  = closed [works on systemd 259, probed on a test prefix; the live prefix is still to probe].
- **Fail closed, with a recovery contract (critique 14).** Unreadable store: nothing launches, `pipe show` says
  `CONTROL UNREADABLE: <cause>`, `pipe doctor` names the fix; damaged evidence is preserved, never trimmed.
- **Record.** A belt exports `acts` to the repo ledger for history; effect never waits on a publish. The owner's
  published hold list becomes a mirror of the store.
- **Honest guarantee (critique 5).** "No bypass" means: no cooperating code path bypasses it, proven by the
  call-site test and the mutant, with the drop-in as a net. It is not a security boundary against an agent
  deliberately calling `systemd-run` by absolute path under the same user.

### Where the passes disagree (not smoothed)

- **Daemon or library.** GPT picks a supervised service; this merge picks a library over SQLite. Reason: SQLite
  already serialises writers across processes, the ExecCondition re-check closes the race without a broker, and a
  daemon is one more thing that must stay alive and whose death stops the factory. What would change this: a
  measured race the transaction + re-check cannot close, or a need to keep launch credentials away from agents.
  The library's API is the service's API, so moving later is a transport change.
- **JSONL or SQLite.** Pass 1 picked JSONL + a folded view; critique 7 is right that this is a hand-built
  transaction system. SQLite is in the Python standard library. Pass 1's pick is overruled on this point.
- **First slice in an hour.** Pass 1's estimate; GPT says accept evidence over the deadline. The pause builder's
  different slice landed in 18 minutes; the control builder landed nothing in 50. Unmeasured for M.

## 4. Claims after the re-measure

| Claim | Pass 1 | Re-measured | Trusted |
|---|---|---|---|
| Tick's tree | dispatch clone | same, from a live process cwd | re-measure |
| Launch primitives read no hold | true | true; role_launch reads only the quota gate | re-measure |
| Launch paths | about 10 | **18 sites, 12 files, 7 families** | re-measure |
| Hold latency | about 22 min | 21 min 27 s | re-measure |
| Journal hold blocks launches | no | **yes in the tick**; the 10:25 launch was latency | re-measure (reverses pass 1 and the Conductor's report) |
| systemd drop-in blocks `systemd-run` units | unmeasured | yes; launcher still sees rc 0 | re-measure; version note from GPT (v252, not 246) |
| Locking on `D:\` | guess 85% | passes inside WSL; Windows side unmeasured | moot: store moves to ext4 |
| A running helper re-reads its notes | unmeasured | no mechanism | re-measure |

Reviewer findings: 2, 3, 7, 8, 12 (critique numbers) are adopted on their logic and partly confirmed by the
re-measure (rc 0 on a skipped unit). 4, 15, 16, 17, 23 are adopted as acceptance tests, unverified until those
tests run. 5 is adopted as a wording change. 13 is moot.

## 5. Build order

1. **Core** (one Opus builder, sequential, tests first): store, `pipe on|off|show|why|log`, `admit` +
   `launch_unit` on all 18 sites, reserve/settle/void for the granted coverage look, the ExecCondition re-check,
   acceptance tests: both pause-race orderings, two callers for one look, duplicate settle and void, unreadable
   store, crash before and after the unit starts, status from two clones. Cut over with new starts off.
2. Every other resource as a typed account with opening balances; `grant`, `set`, `undo`; delete the old readers.
3. `queue` verbs; compact read defaults.
4. `next` on the shared planner; containment drop-in on the live prefix; mirror belt; deadman promise.

In-flight work (measured 11:10 AM): the pause builder landed `maturation_dispatch.py pause|resume|next`
(b206c0d34f), a repo-side switch, kept as the interim pause until slice 1 absorbs it. The void builder keeps
going: its counter census and the Graffiti restore are needed under any design; its void record is imported as
opening balances. The `pipe` builder (JSONL design, wrong tree in its brief, nothing landed) is stopped and
relaunched on this document.

## 6. Decisions

Taken by the Conductor (delegated, evidence-for-ask): the store is the truth for holds and the published list
mirrors it (evidence: 21 min latency); acts that need his words are a grant of a look, raising a ceiling,
lifting his own hold, voiding a run that failed on the mod's merits; library not daemon; SQLite not JSONL.

For the owner: (a) does a void run's spend count toward the stage spend ceiling; (b) what `pipe off` does to a
run already live by default.

## Rulings

(his answers, verbatim, go here)
