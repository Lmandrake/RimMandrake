# Post-event recovery mode: a design, replayed on 2026-11-04 (OPS_RECOVERY_DESIGN_POST_EVENT_MODE)

Status: DESIGN. Nothing here is built. This is step 7 of `design/RimMandrake/relentless_recovery_plan_2026-11-05.md`.
Steps 2, 3, 5 and 6 of that plan are parts of this design, and each is already filed as its own item. Inputs:
GPT consult B (`design/RimMandrake/relentless_failure_review_gpt_2026-11-05.gpt_read.md` l.225-300), the failure catalog
(`design/RimMandrake/relentless_failure_catalog_2026-11-05.md`, classes c, i and j), and the readings cited in §7.

The owner's ask (2026-11-05, `--owner-said` on the item): *"How can we make this system much more robust, sane, and
self-recovering after a major event? How can we teach it to self-judge how to arbitrate a bunch of semi-defective queue
items incoming after, say, Steve Desktop barfs out a bunch or tokens run out?"*

## 0. The idea in five lines

1. A major event becomes **one incident record** with a phase. It does not become N tickets and N strikes.
2. The phases are **QUARANTINE → RECONCILE → VERIFY → RAMP → NORMAL**. **STALLED** is an explicit exit that has an age
   alarm, so a recovery can never become the next silent hold.
3. Whether a failure is an event artefact or a real defect is decided **per sighting**: drop, merge, park or keep.
   It is never decided per ticket or by filing time. A park always names a wake condition.
4. Measurements are **re-baselined in a versioned correction view**. Raw history is never rewritten, and a real outage
   stays on the record.
5. Programs run the deterministic parts. **Operations** owns measurement validity, source recovery and alarms. The
   **Conductor** owns arbitration that a rule cannot settle. Neither one accepts its own repair.

## 1. What exists today, and the gap this fills

The search came first (CLAUDE.md: "this project keeps having already built it"). The design rebuilds none of these:

| Piece | File | What it already does | What it lacks for recovery |
|---|---|---|---|
| Ops incidents | `src/RimMandrake/rimflow/incident.py` | One incident per cause, with an ack chain up to him, a relapse count, and a close that happens only on a sane reading. | No phase and no affected-attempt inventory. It never touches the items an event produced. |
| Instrument incident | `src/RimMandrake/rimflow/relentless_incident.py` | One record per broken shared instrument. Parents wait on it. It is released only after a good fixture and a bad fixture both run and behave. | Keyed per repair item. Nothing opens one from a host or account signal. |
| Capability incidents | `relentless_breakers` (`incidents.json`) | One capability signature that failed three items. | No disposition for the items. |
| Steve fault gate | `src/RimMandrake/Utils/testq/fault_monitor.py`, `ingest.py` | Fault windows from the SIMD canary (`fault_windows.json`). Holds a result until a clean canary cycle is read (`gate` l.238-253). `quarantine_one` (ingest l.498). | Retroactive for tickets already filed: it writes prose notes and recomputes nothing (catalog class i). |
| Account breaker | `relentless.py` `launch_failed` l.3464, `account_lost` l.492, `relentless_account.py` | No strike for an account death. Opens after 3 failures, cools 900 s doubling to a 1800 s cap (`relentless_rules.json` l.105-107). | When it cools, every queued item launches again. There is no single probe first (§7.2). |
| Health | `ops_health.verdict` | SLI budgets and the content pause. | Broken rules read as healthy (plan step 2). |

**The gap:** each book sees its own slice. None of them owns the *aftermath*, meaning the items, tickets, verdicts and
charges that the event produced while it was still unnoticed. Recovery mode is a thin controller that sits over these
books. It adds one record type and one phase field, and it adds no new store of truth.

## 2. The incident record

One JSON object per event, in a new `recovery.json` beside `incidents.json` in the Relentless store, written under
`Store.lock`. It links to the existing books by id and never copies them. Fields:

| Field | Meaning |
|---|---|
| `id` | `R<onset-utc>-<source>`, for example `R20261103T224702Z-steve`. The id is fixed once it is made. A repeat sighting joins the record; it never makes a new one. |
| `source` | `host:<machine>` · `account:<pool>` (the pool's *role*, never an account name) · `harness:<signature>` |
| `kind` | `host_fault_wave` · `account_wave` · `harness_burst` |
| `onset` | `{earliest, latest}`. An **interval**, because onset is uncertain. For Steve: earliest = the last clean cycle before `first_bad`, latest = `first_bad`. |
| `end` | `null` until the source is known healthy (for Steve: the reboot plus a clean canary cycle). |
| `scope` | The lanes, profiles and items that depend on the source. The **barrier** applies only inside the scope, and its meaning depends on the kind. For a host: no result counts and no paid check is leased, while running stays the existing gate's business. For an account: no item launches on the pool. For a harness: no derivative ticket is spawned as an item. |
| `phase` | `QUARANTINE` · `RECONCILE` · `VERIFY` · `RAMP` · `NORMAL` · `STALLED` |
| `phase_since`, `deadline` | When the phase began, and the time by which it must move (§3 table). |
| `owner`, `next_observation` | Who acts next (Operations, the Conductor or a program), and the one reading that would move it. |
| `sightings[]` | One row per attempt the event may have touched: `{attempt, item, at, signature, validity, disposition, why, wake}`. |
| `repair` | The single source-repair obligation (a rimflow item id). The derivative noise must never drop this. |
| `controls` | `{good, bad}` fixtures for VERIFY. These are the same shape as `relentless_incident` fixtures, and they reuse its runner. |
| `links` | Ids in `incident.py`, `relentless_incident` and `incidents.json` that describe the same fault. |
| `adjustments[]` | Re-baseline entries (§6), each `{view_version, attempt, field, raw, corrected, basis}`. |
| `history[]` | Every phase transition and disposition: `{at, from, to, by, evidence}`. |
| `probes` | `{used, max}`. Paid item runs used as probes are bounded, and one on a timer with no new evidence is refused. A **source liveness probe** (a zero-cost call on the source itself, §7.2) is not an item run: it runs at most once per cooling interval, and its result is the new evidence. |

Every transition is **idempotent**: replaying `history` rebuilds the same record. A restart at any phase resumes that
phase. Fencing: a transition checks `(id, phase, phase_since)` under the lock, so two ticks cannot both advance it.

## 3. The state machine

```
 NORMAL --signal--> QUARANTINE --inventory recorded--> RECONCILE --source testable & all sightings disposed-->
 VERIFY --good passes & bad fails--> RAMP --one job, then a batch, healthy for the window--> NORMAL
   any phase --deadline missed, or a needed capability is unavailable--> STALLED --new evidence / repaired / ruled--> that phase
```

| Phase | Entry | What the controller does | Exit | Deadline |
|---|---|---|---|---|
| **QUARANTINE** | An entry signal (§4). | Writes the record. Bars admission **in scope only**: no lease, no retry, no paid check on an item whose next run needs the source. Results and tickets that arrive are kept *unleased* (the testq `gate` "hold" already does this for Steve results). Running items in scope are fenced: they finish, and their verdicts are marked `sighting:provisional`. Takes the inventory: every attempt and auto-filed ticket whose interval overlaps `[onset.earliest, now]` on the source. | The inventory is written. | 15 min |
| **RECONCILE** | The inventory exists. | Groups sightings by signature and gives each one a disposition (§5). Retracts invalid readings **structurally** (plan step 6: a ticket's support is recomputed, prose is not enough). Sets one `repair` obligation for the source itself. Writes re-baseline adjustments (§6). | The source can be tested (for a host, rebooted with a clean canary; for an account, the liveness probe passes, its stated reset time has passed, or a change-over is logged), and every sighting has a disposition or a parked reason. | 2 h |
| **VERIFY** | RECONCILE is done. | Runs `controls.good` and `controls.bad` through the **affected path**: the real lane, launcher or account. The runner is `relentless_incident.check`. Checks that the readings are fresh and that the health verdict is not `unmeasured` (plan step 2). | Good passes, bad fails, both printed `FIXTURE_VERDICT`. A fixture that could not measure keeps VERIFY open. It is never a pass. | 1 h, max 2 probes |
| **RAMP** | VERIFY held. | Releases **one** affected job, then a batch of `min(3, places)`. Checks measured usage (not estimated), a real verdict, and the source staying healthy. | The batch succeeds and the source is healthy for the observation window (Steve: one clean canary hour; account: 2 runs with non-zero measured usage). | 2 h |
| **NORMAL** | RAMP held. | The scope is released. Parked sightings stay visible with their wake conditions. The record stays open for `relapse_h` (incident.py's own relapse window), so a recurrence **reopens this record** and its age is not reset. | — | — |
| **STALLED** | A deadline missed, the probe budget spent, or a capability that only hands can supply (for example a RAM test). For a host: 3 fault windows within `relapse_h` (counting windows, joins and reopens alike), with a hands-only repair. | Keeps the barrier **on the affected scope only** and releases everything outside it. Keeps running the source liveness probe if the source has one. Raises **one** alarm, `OPS_RECOVERY_STALLED_<source>`, to the running board and his daily digest (no LLM needed), then to Operations and the Conductor, naming the scope, the owner and the one next observation. Unresolved sightings become parked records. They are never a reason to hold unrelated work. | New evidence, a repaired capability, or a ruling (Conductor `--per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM`). Each returns the record to the phase it left. | — |

**The STALLED age alarm** is the guard against "recovery becomes the next silent hold". `ops_watch` reads
`recovery.json` each tick. The alarm fires when (a) any record has had no `history` row for 30 min while not in NORMAL,
(b) `now > deadline`, or (c) runnable content inside a scope has waited more than 60 min. It has one fixed alarm id per
source, so a repeat reopens the same item (CLAUDE.md, "an alarm has one fixed item id"). The plan's step 3 fix also
applies here: closing the alarm's ticket while the record is still not NORMAL reopens it.

The liveness of the controller itself is watched from **outside** the impaired source. During an account wave, the
watcher must not be a `claude -p` run on the same pool. The `rm-deadman` / `ops_watch` timers are plain Python and need
no LLM, so they qualify.

## 4. Entry signals

All thresholds are starting values (GPT's own wording: "not demonstrated optimal"), and they live in
`relentless_rules.json` under `recovery`.

| Kind | Signal | Source of the reading |
|---|---|---|
| **host_fault_wave** | A new window in `fault_windows.json`, or a red canary (`fault_state.json`), or an INVALID streak of 3 or more in testq. Enter at once. | `fault_monitor.py` |
| **account_wave** | The `account_lost` end with kind `account_error` (rate_limit, authentication_failed) on **2 or more distinct items within 10 min**, or the launch breaker opening on an account error. A single transient 429 with a stated backoff is not a wave. | `relentless.py account_lost`, `breaker.json` |
| **harness_burst** | Fast: the same normalized failure signature on 3 or more attempts across 2 or more items within 15 min, or 3 or more auto-filed repair tickets from one lane within 1 h. **Slow burn:** 3 or more auto-filed tickets in one lane and one signature family (`ingest.CLASS_PRIOR` class, for example SITE) within 24 h. A slow burn never bars admission. It only collects the tickets into one record and a merge proposal. | testq `ingest.repair`, `relentless_breakers` signatures |

A config change to judging, walls or accounting does **not** enter recovery. It starts a re-baseline (§6) only.

## 5. Per-sighting arbitration: drop, merge, park, keep

The rule is decided per **sighting** (one attempt, one reading). A ticket's fate follows from its sightings. Cheap
evidence is tried before paid evidence: existing receipts, then later fixes and supersessions, then a controlled
reproduction, then builder work.

| Evidence on the sighting | Disposition | What it writes |
|---|---|---|
| The claimed test never ran, or its observation is demonstrably invalid. That means a zero-usage account death, or a sighting inside a fault window on the same host **whose signature is in the fault's own class** (for a Steve SIMD fault: CLR or mono death, access violation, `no_game`, or the test never ran). Every supporting sighting is invalid, and no independent evidence remains. | **drop** | `rimflow drop` with `--why "recovery <id>: unsupported event artefact"`, plus a **reopen signature** (the raw failure string and the lane). A later identical sighting outside any event reopens it. A drop does **not** certify the product good. |
| Same invariant, a compatible reproduction, and the **same demonstrated cause** across several tickets. | **merge** | `rimflow supersede --by <canonical>`. Distinct acceptance clauses are copied onto the canonical item. Shared timing alone is not a cause. |
| Correlation with the window only (a sighting inside the window whose signature is *not* in the fault's class, for example a site_hold surprise); an in-class signature within the **lookback** before `onset.earliest` (10 min, two canary cycles of 300 s, because the canary bounds onset only to its cycle); an onset that is ambiguous; an intermittent failure not reproduced, a source still untrusted, or a reproduction that needs hardware we cannot reach. | **park** | Item status `parked` with `{owner, missing_observation, wake}`. The `wake` is a predicate that a program can evaluate, for example `canary_clean_h>=24 and rerun(job)`. A park with no `wake` is refused at write. A park is never classed as false. |
| It reproduces on a healthy source with working controls, or it has valid pre-event evidence, or it has independent defect evidence. | **keep** | Unchanged. It gains a `links` entry to the record. |
| The host, account or harness failure itself. | **keep, once** | That is `repair`. Exactly one per record. |

Rules that apply to every disposition:

- **A change to existing behaviour:** today `gate` quarantines every Steve result whose span overlaps a known window, whatever its signature (`fault_monitor.py` l.246-247), and files nothing. Recovery **wraps** gate: gate still quarantines, so no ticket is spawned, and recovery records each quarantined result as a sighting. An in-class one is dropped. An out-of-class one is **parked** with a wake (a rerun on a clean host), instead of vanishing silently.
- **A window overlap alone never makes a sighting invalid.** The overlap plus a signature in the fault's class does. The signature classes are a table in `relentless_rules.json` under `recovery.fault_classes`, beside the `ingest.py` `CLASS_PRIOR` they extend.
- **Validity is per sighting, and it is monotone in the evidence, not in the clock.** Late discovery of a fault window
  must reach the same end state as early discovery (plan step 6's property test).
- **Mixed support keeps a ticket.** If one sighting is invalid and one is valid, the ticket is kept.
- **A passing rerun does not disprove an intermittent defect.** It moves the sighting to park, never to drop.
- **Sunk spend is a diagnostic, never a reason to drop.** This keeps the Conductor's rule against trimming real work to
  save resources.
- **Who decides:** a program applies every row it can settle from the table. It writes the Conductor a list of only the
  sightings the table leaves ambiguous, and the Conductor rules each one by `--per-ruling`. The Conductor never rewrites
  the store by hand (catalog class m).
- **Builders get nothing from recovery** unless the disposition is keep *and* the cause is `product` (plan step 5).

## 6. Versioned re-baseline

- **Raw history is never edited.** `attempts.jsonl`, the ledger and the books stay as written.
- A **correction view** (`view_version` = an integer, plus the sha256 of the rules) applies the record's `adjustments[]`
  over the raw data. Every reader that reports spend or an SLI names the view it read, and the health verdict stamps it
  (plan step 2 adds the stamp fields).
- An adjustment replaces a charge only when the actual usage is established. A measured zero stays zero, and an unknown
  stays unknown, never zero (catalog class c: the reserve was charged on a measured zero).
- Aggregates are recomputed from the corrected attempts. A zero denominator reads UNMEASURED.
- **Outages stay on the record.** Host downtime and failed measurements remain in reliability history. The correction
  removes *mis-attribution* (a phantom spend charged to an item, a strike for a dead host). It never removes the event.
- **"Fit to resume" and "budget recovered" are separate readings.** RAMP needs the first. The SLI budget heals on its
  own clock.
- When a metric's meaning changes, a new epoch starts. Epochs are combined only through a validated transformation.

## 7. Replay on paper: the two events of 2026-11-04

All times are UTC. Each line cites its reading.

### 7.1 The Steve host fault wave (SteveDesktop SIMD faults, 2026-11-03 22:47Z to 2026-11-05)

**Readings.** `D:\ClaudeWork\rimmandrake\testq\fault_windows.json` (12 windows when read at 2026-11-05 05:30Z, the 12th still open). The ledger events for
`HARNESS_REPAIR_CAUSE_*` (spawn and supersede rows in `infrastructure/state/ledger/events/*.jsonl`). The triage commit
045724125c.

**What happened.**

- Window F20261103T195921Z ran 22:47Z to 02:45Z. Then six more windows fell on 11-04, at 03:38Z, 08:20Z, 09:23Z,
  12:20Z, 13:21Z and 15:22Z, each about 10-20 min long and ending in a reboot.
- 18 `HARNESS_REPAIR_CAUSE_*` tickets were spawned between 10-31 and 11-04, all `--for FOUNDRY` (catalog B6). Nine of
  them were spawned on 11-03 and 11-04.
- They sat until a hand triage at 11-05 04:39Z to 04:41Z (045724125c):
  - 6 superseded by SITE_QUIET_FIX_COLONISTS_HURT_DOWNED_DEAD
  - 1 superseded by 0CA2BE29
  - 4 superseded by STEVE_CRASHES_DIAGNOSE_DEFENDER_FALLS_TOO
  - 2 closed as fixed
  - FC103899 had been superseded on 11-03
  - 4 were still open after it: 0CA2BE29, 5F134E3C, E0B6DA41, EBC39CFA
- Meanwhile STEVE_CRASHES_DIAGNOSE_DEFENDER_FALLS_TOO was started at 03:37Z and noted by the supervisor through 11-05.
  The catalog (class j) counts 38 events and 1.07M tokens for it. Its real next step was a RAM test that only hands can
  do.

**Replay through the design.**

| Time | Phase | What recovery mode does | Reading it rests on |
|---|---|---|---|
| 11-03 22:52Z | → QUARANTINE | `fault_monitor` records first_bad 22:52Z. Record `R20261103T224702Z-steve` opens with onset `{22:47Z, 22:52Z}` and scope = the testq Steve lane. For a host, the **barrier** is: no result in the scope counts, and no paid LLM check is leased against it. Running the lane is still the existing gate's business. | `fault_windows.json` F20261103T195921Z |
| 22:52Z+ | QUARANTINE | Inventory: testq jobs overlapping `[22:47Z - lookback, now]` (§5, lookback 10 min). J20261103T233438Z-aa0482 is inside the window (99231A83, access violation). J20261103T224408Z-a1134d ran 22:44:49Z to 22:45:58Z, which is **61 s before onset.earliest** and inside the lookback (EBC39CFA, mono crash at LOAD). | spawn titles; `testq/done/J20261103T224408Z-a1134d.json` started/finished |
| 11-04 02:16Z | QUARANTINE | 0143E7AD (job 01:56Z, SelfTest did not run) arrives during the window. Today the window was written only at the 02:45Z reboot, so `gate` could not quarantine it and the ticket was spawned. Under the design the record already holds `onset` from 22:52Z, so the sighting joins the record **instead of spawning an item**. | `fault_monitor.py` l.238-253; spawn row 02:16Z |
| 02:45Z | → RECONCILE | Reboot. Dispositions: 99231A83 and 0143E7AD are inside the window with in-class signatures (access violation; test never ran) → **drop**, with a reopen signature. EBC39CFA is an in-class signature in the lookback → **park**, `wake: canary_clean_h>=24 and rerun(J20261103T224408Z-a1134d)`. `repair` = STEVE_CRASHES_DIAGNOSE_DEFENDER_FALLS_TOO (keep, once). That repair's next observation is a RAM test only hands can run, so it is **parked, not leased**, with `wake: a RAM-test result is recorded`. | windows; spawn rows; catalog class j |
| 03:37Z (real) | — | **What actually happened:** the supervisor started STEVE_CRASHES at 03:37Z and kept spending checks on it (catalog class j: 38 events, 1.07M). **Under the design** it is parked from 02:45Z and never leased. | ledger start row 03:37Z |
| 03:38Z | RECONCILE (no reset) | F20261104T024513Z: the record is not yet NORMAL, so this window **joins** it. It is not a relapse, its age is not reset, and no new record is made. The **fault-window count** is now 2 within 6 h. | windows |
| ~03:57Z to 08:20Z | VERIFY → RAMP → NORMAL | Reboot plus clean canary. `controls.good` = a known-good FlowWorks testq job. `controls.bad` = a job with a planted failing expectation. Both behave, the lane ramps, NORMAL. | windows (no fault 03:57Z to 08:20Z) |
| 05:46Z, 06:06Z | NORMAL | E0B6DA41 (job 05:34Z, site_hold) and 5F134E3C (job 05:54Z, driver undelivered) ran outside any window: **keep**, not this event's. | spawn rows |
| 08:20Z | → RECONCILE (reopen) | F20261104T035722Z reopens the record (relapse 1, `relapse_h` = 6 h). Window count within 6 h: 2 (03:38Z, 08:20Z). | windows |
| 08:23Z, 12:12Z | — | 4AFBF8A2 (job 08:02Z, 18 min before the 08:20Z window, signature dead colonists) and FCC08D84 (job 11:58Z, Stillsand, downed) are out-of-class signatures outside the window and lookback: **keep**. | spawn rows |
| 09:23Z | → STALLED | F20261104T083546Z. Window count within 6 h: 3 (03:38Z, 08:20Z, 09:23Z), and the repair is hands-only. That meets the host STALLED entry (§3). One alarm: "Steve lane: intermittent host fault, 3 windows in 6 h. Next observation: a RAM test (hands)." The lane keeps running under the existing gate. The barrier still holds: results are not counted and no paid checks run. | windows |
| 12:20Z, 13:21Z, 15:22Z, 11-05 00:44Z, 03:04Z | STALLED | Each window joins. Its sightings are disposed by the §5 table, and the record stays STALLED. No paid probe runs. | windows |
| slow burn, 10-31 to 11-04 | separate record | The site_quiet tickets (4D2C5B87, 5495932D, 8A6B00BD, FA96BB79, E0B6DA41, 4AFBF8A2, FCC08D84) are hours apart, so the 15-min burst test never fires. The **slow-burn** harness signal (§4: 3 or more auto-filed tickets in one lane and one signature family within 24 h) fires at 12:12Z on 11-04 on E0B6DA41 (05:46Z), 4AFBF8A2 (08:23Z) and FCC08D84 (12:12Z). All three are SITE-family tickets from the Steve testq lane, though from different mods. It opens `harness:site_quiet`, and the older SITE-family tickets still open (the 11-01 trio and 4D2C5B87) join it by family. The program cannot prove a shared cause, so it writes a **merge proposal** listing the seven, and the Conductor rules it. The hand triage did exactly this, about 16 h later (SITE_QUIET_FIX_COLONISTS_HURT_DOWNED_DEAD). | spawn rows; 045724125c |

**Difference from what happened.**

- 4 tickets would never have become items: 99231A83 (access violation) and 0143E7AD (SelfTest never ran) are dropped,
  and C1644394 (CLR death at LOAD) and 4E52E202 (modcheck exit, no sheet) are dropped by the 11-01 record
  (F20261101T164245Z, 17:30Z to 00:38Z) on the same rules.
- 8A6B00BD, 5495932D and FA96BB79 (job J20261101T083051Z) also fall inside an 11-01 window (F20261101T035219Z), but
  their signatures (colony_loss, hostile_arrival) are not in the SIMD class. So they are **not** dropped: they join the
  site_quiet proposal, which matches the hand triage.
- 1 ticket (EBC39CFA) would be parked by the lookback rule with a wake condition, instead of sitting open and
  unexplained.
- The site_quiet merge comes as a program-written proposal at 12:12Z on 11-04 for the Conductor to rule. It is not a
  program merge, because the program cannot prove a shared cause. The real hand sweep came about 16 h later (11-05 04:39Z).
- STEVE_CRASHES is parked from 02:45Z and never leased. In reality it ran 38 events and 1.07M tokens.
- **What the design would NOT have fixed:** 2E27AD17 (TestqResult contract) and 3A38C661 (stale_load) were real harness
  bugs outside any window. They stay keep and go to their own repairs, which is what happened (closed fixed).

### 7.2 The 429 / account wave (2026-11-04 14:50Z to 19:36Z)

**Readings.**

- 55 `end: account_lost` rows on 2026-11-04 in `/home/mandrake/rm/relentless/store/items/*/attempts.jsonl`, scanned by
  end field and detail text, 2026-11-05. Of these, 10 are change-overs and 45 are rate_limit.
- The account log `~/.claude-accounts/log.jsonl` (`op=use changed=true` rows; account names not read).
- `relentless_rules.json` l.105-107: `launch_breaker` 3, `breaker_cool_s` 900, `breaker_cool_max_s` 1800.
- Catalog class c: 48 runs (25 work, 23 check) charged 57.6M of phantom spend across 6 items. Fixed in b902ac4ec9 at
  11-05 03:58Z.
- The 48 charged runs and the 45 rate_limit attempt rows come from different instruments: charges count check runs, and
  attempts count run ends. This doc does not reconcile them. Build step 2's replay test owes that reconciliation.

**What happened.**

- 02:55:27Z: 8 items `account_lost` within one second, each with detail "account change-over at 02:54:23Z".
- 09:27Z: 2 items, one minute after the change-over logged at 09:26:38Z.
- These 10 rows are the `change_over` kind, not `account_error`. Both bursts exceed the 2-in-10-min count, so the **kind
  filter**, not the threshold, keeps them out of recovery (`account_lost` l.510 calls `launch_failed` only for
  `account_error`).
- 14:50Z to 19:36Z: **45 rate_limit rows on the same 6 items, in 9 waves about 35 min apart** (14:50, 15:25, 16:02,
  16:38, 17:13, 17:48, 18:24, 19:01, 19:36).
- Each wave is the breaker's 1800 s cap plus a tick, after which every queued item launched again into the same limit.
  Each zero-usage run was charged the 1.2M reserve.
- None of the 55 rows carries a session, so no item lost resumable work.

**The account liveness probe.** An account record needs a way out of STALLED that runs on its own, because Operations
and the Conductor are `claude -p` runs on the same impaired pool (`roles/operations.md`). So the controller, which is
plain Python, owns one **liveness probe**:

- It is a minimal `claude -p` call on the pool, classified by the existing `relentless_account` rules.
- A refused probe measures zero usage and costs nothing. A passing one costs a trivial amount.
- It runs at most once per `max(1800 s, the stated reset)`.
- It is a probe of the *source*, not a paid run of an item, so §2's "no timer probe without new evidence" rule does not
  apply to it. That rule bars re-running items on a timer.
- The probe's result is the evidence that moves the record.

The STALLED alarm also goes to channels that need no LLM: the running board (`RUNNING_NOW.md`) and his daily digest. A
pool-bound reader that cannot run is then not the only way he hears of it.

**Replay through the design.**

| Time | Phase | What recovery mode does | Reading |
|---|---|---|---|
| 14:50Z | → QUARANTINE → RECONCILE | 4 items end `account_error` (rate_limit) within one tick, which is 2 or more distinct items in 10 min. Record `R20261104T1450Z-account` opens with scope = every lane that launches `claude -p` on the active pool. **Item launches on that pool stop. There is no cool-and-retry.** Inventory: the 4 runs, all at measured zero usage. Each sighting is an account artefact (drop as a sighting, no strike, as `account_lost` already does). The 6 items are **keep**: the event says nothing about their work. Adjustment: each charge is corrected from the 1.2M reserve to the measured 0 (§6), and the raw charge row stays. | attempts rows 14:50Z |
| 15:20Z, 15:50Z | RECONCILE | Liveness probes 1 and 2 are refused. No item launches (reality launched 3, then 6). | attempts 15:25Z, 16:02Z |
| 15:50Z | → STALLED | The probe budget (2 in RECONCILE) is spent and no reset is stated. One alarm `OPS_RECOVERY_STALLED_account` goes to the board and the digest, and to Operations and the Conductor once they can run. It reads: "account pool refusing since 14:50Z. Next observation: the liveness probe every 30 min, or a change-over." Non-LLM work (testq, ops_watch, timers) is outside the scope and keeps running. | §3 STALLED entry ("the probe budget spent"); attempts 16:02Z (reality relaunched 6 items into the same limit) |
| every 30 min | STALLED | The liveness probe keeps running at zero cost while it is refused. No item launches. | cadence `max(1800 s, stated reset)` (§7.2 liveness probe, `relentless_rules.json` l.107 `breaker_cool_max_s` 1800); attempts 16:38Z to 19:36Z (6 waves still refused) |
| first passing probe (after 19:36Z) | → VERIFY | The attempts do not say when the pool came back: the next account_lost row is not until 11-05, and none follows 19:36Z on 11-04. The first probe that passes is the new evidence. `controls.good` = a trivial run with non-zero measured usage. `controls.bad` = the classifier on a recorded 429 transcript, which must read `account_error`. | attempts gap after 19:36Z |
| then | RAMP → NORMAL | 1 item, then 3, each with non-zero measured usage. | §3 RAMP row (one job, then `min(3, places)`; exit on 2 runs with non-zero measured usage). Projected, not replayed: no attempts row follows 19:36Z on 11-04 |

**Difference from what happened.**

- **45 dead item launches → 4** (only the wave that opened the record). In their place come about 10 liveness probes at
  zero measured usage.
- The phantom 57.6M is corrected in a **view** on the day it happens. In reality it was found when the owner asked about
  JAM's cost, and fixed in code afterwards (b902ac4ec9). Under §6 the raw rows stay on the books but are no longer
  counted.
- **What the design would NOT change:** the two change-over bursts (02:55Z, 09:27Z) stay outside recovery by kind. That
  is correct: a change-over is over by the time it is read.

## 8. Ownership

| Who | Owns |
|---|---|
| Program (the controller in the Relentless tick, plus `ops_watch`) | Entry signals, the record, the inventory, table-settled dispositions, adjustments, the probe budget, phase moves, the STALLED alarm. |
| Operations (`src/RimMandrake/rimflow/roles/operations.md`) | Measurement validity, the source repair, the controls, the account circuit, alarm delivery. Answers a STALLED alarm with the next observation. |
| Conductor (`src/RimMandrake/rimflow/roles/conductor.md`) | The ambiguous sightings the table leaves, merges disputed by grouping, and anything a delegation_policy §2 says is his. It rules by `--per-ruling`, never by store edit. |
| Neither | Accepting its own repair. A source repair's close still goes through the independent check. |

## 9. Build order, and what this design does not change

1. The plan's steps 2 (health reads unmeasured), 3 (closed ticket cannot silence), 5 (cause before return) and 6
   (quarantine recomputes support) come first. They are already filed, and recovery mode reads their outputs.
2. Then the record plus QUARANTINE and RECONCILE for **account_wave** only: the smallest source with the clearest
   win (§7.2: 45 → 4 item launches). Proof: a replay test over the 11-04 attempt rows that must produce at most 4 item
   launches, a STALLED alarm, and an exit on the first passing liveness probe. It also reconciles the 48 charged runs
   against the 45 attempt rows.
3. Then host_fault_wave over `fault_windows.json`. Proof: a replay of the 18 tickets, which must reach the dispositions
   in §7.1, and the same result when the windows are learned late.
4. Then harness_burst, VERIFY/RAMP and the STALLED alarm in `ops_watch` (with `--live` on the timer at close).

It does **not** change the content pause (plan §3, step 8). A scope barrier here bars only items that need the failed
source. The global pause rule is left exactly as it is until he or the Conductor rules on step 8.

## 10. Design review

A fresh Opus agent (rm-consult) that did not write this doc reviewed it against its inputs, the code it cites and
the raw readings. It ran 2026-11-05 and wrote its findings to
`D:\ClaudeWork\rimmandrake\relentless\OPS_RECOVERY_DESIGN_POST_EVENT_MODE\review.md`. The builder re-measured every
factual finding before changing the text. All eight held.

- **R1 [BLOCKER] account STALLED had no exit that runs on its own.** The only thing that could move it was an LLM
  reader on the impaired pool. Answer: §7.2 adds the controller-owned **liveness probe**, a zero-cost call on the source,
  at most once per cooling interval, whose result is the new evidence. §2 `probes` separates it from paid item probes,
  and the STALLED alarm now also goes to the running board and his digest, which need no LLM.
- **R2 [MAJOR] the 429 replay broke its own probe rules.** Answer: probes now belong to the liveness probe in RECONCILE
  and STALLED (2 refusals in RECONCILE → STALLED). The §7.2 timeline was re-run on that rule: STALLED at 15:50Z, not
  16:38Z.
- **R3 [MAJOR] change-over rows were miscounted and mis-explained.** It was 55 rows, not 57. 8 items at 02:55:27Z and 2
  at 09:27Z are change-overs, kept out by kind, not by threshold. Answer: §7.2 readings and "what happened" corrected,
  with the kind filter named (`account_lost` l.510).
- **R4 [MAJOR] harness_burst would not fire on the site_quiet tickets, and a program cannot merge on a shared cause.**
  Answer: §4 adds a **slow-burn** signal (3 SITE-family tickets in one lane within 24 h, which never bars admission).
  §7.1 now has it fire at 12:12Z and write a **merge proposal** for the Conductor, not a program merge.
- **R5 [MAJOR] the Steve STALLED entry was undefined, the relapse count was wrong, and the barrier contradicted the
  lane running.** Answer: §3 STALLED gains a host entry (3 fault windows within `relapse_h` with a hands-only repair).
  §7.1 counts windows: STALLED at 09:23Z, not 08:20Z. §2 `scope` defines the barrier per kind (host: nothing counts and no
  paid check is leased; the lane may run).
- **R6 [MAJOR] EBC39CFA ran wholly before onset, so no rule settled it.** Answer: §5 park gains an explicit **lookback**
  (10 min, two canary cycles) for in-class signatures before `onset.earliest`. §7.1 cites the job's own started/finished
  times (61 s before onset).
- **R7 [MINOR] gate already quarantines every overlapping result, and the doc misread it as "hold".** Answer: §5 now
  states the behaviour change. Recovery wraps gate, and an out-of-class quarantined result is parked with a wake instead
  of vanishing. §7.1 says why 0143E7AD leaked today (its window was written only at the 02:45Z reboot).
- **R8 [MINOR] window count and 48-vs-45 runs.** Answer: the window count is stamped with its read time (12, one still
  open). The 48-vs-45 gap is stated as unreconciled, and its reconciliation is put on build step 2's proof.
