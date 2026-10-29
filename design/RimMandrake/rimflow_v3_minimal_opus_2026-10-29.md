# RimFlow minimal design (Opus, written independently of GPT's version), 2026-10-29

Item: `RIMFLOW_V3_SHRINK_FEWER_CHAIRS_SAME_JOBS`. DESIGN ONLY: no code, item or role file was changed.
Inputs: `design/RimMandrake/rimflow_v3_workflow_as_built_2026-10-29.md` (AB), `rimflow_v3_gpt_risk_review_2026-10-29.md`
(GR), `rimflow_v3_risk_response_2026-10-29.md` (RR). Every "works / doesn't" below was re-checked on the bench clone
at HEAD c2dfc21445 on 2026-10-29 at about 21:00Z. The code probes:

| Probe | Finding |
|---|---|
| `rimflow/cli.py:1826-1855` `cmd_close` | `sha = args.sha or head_sha()`: an implicit HEAD is accepted. Owed criteria print "⚠️ A WARNING, not a refusal". No review record is checked. |
| `rimflow/model.py:2036-2072` verify / `_criterion_passed` | A `fail` result never demotes `validated`. A pass is checked against the state, not against the current `built_sha`. |
| `Utils/ops_watch_rules.json:67` | `"for": "BENCH"`: every ops_watch alarm item goes to a seat whose schedule entry says `wake: false`. |
| `Utils/testq/steward.py:17,473` | RUNNING is "the only state that ends an incident"; escalations spawn `--for BENCH`. |
| `rimflow/role_launch.py:206-219` | A stale, missing or future ops_watch status gives UNMEASURED, and that refuses every role launch, Operations included. |
| grep "WIP cap" over `rimflow/*.py`, `Utils/` | **No code reads it.** The Producer writes `WIP cap: <n>` into plan.md (`roles/producer.md:134`), and nothing enforces it. |
| `model.replay()` open items | FOUNDRY: **82 doing, 343 built, 172 validated**, 832 proposed. So 597 items are started and not finished. BENCH: 9 doing and 23 proposed, though no program rings BENCH. |
| `gpt_consult` references in `rimflow/*.py` | Only in `arbiter_tiers.py` and its selftest. **Nothing in the close path calls or checks a GPT review.** |
| ledger, RR's P0 tickets | T1 close, T2 alarms, T3 demote, T4 steward and T5 degraded Operations were **never filed**. `AUDITPRESCREEN_FIX_WAVED_THE_FAKE_THROUGH` is still `proposed`. Meanwhile `V3_HEALTH_BUILD_DAILY_PULSE_DAY_ONE`, `OPS_MODEL_BUILD_V3_TWIN_FIT_DAILY`, `PRODUCER_CADENCE_DESIGN_MORE_THAN_WEDNESDAYS` and `HELPERS_BUILD_SHARED_CAP_ACROSS_ROLES` are all `doing` at once. |
| commits 4c0b13067d, a0703d326d | `findings_fold.py` (the no-AI findings sorter) and `audit_hardflag_file.py` (the Auditor's no-AI hard-flag filer) are built. |

**The finding that shapes this whole design.** The owner says "depth before breadth". The ledger shows the opposite:
almost 600 items are started and not finished. Four new measurement builds are in progress while the five fixes that
would make "done" honest have not been filed. The Producer was supposed to cap WIP, but its cap is prose that no
program reads. **Adding chairs does not create focus; a gate in `rimflow next` and `rimflow close` does.** So the
minimal design moves the rules out of role prose and into those two verbs, and then removes the chairs whose only job
was to watch for the rules being broken.

---

## 1. Function inventory

"Works?" means it works today, checked against code, config or ledger. YES = it works. PART = it runs but has a known
hole. NO = it is broken or absent. OFF = it is built but switched off. DES = it is designed but not built.

| # | Function | Done today by | Works? | Evidence |
|---|---|---|---|---|
| F1 | Talk with the owner while he is present: answer, relay, record rulings | BENCH seat (Conductor, live) | YES | CONDUCTOR.md first rule |
| F2 | Tell the owner things while he is away: phone brief, digest | rm-pulse timers (no AI); Conductor quick checks 08:00 and 20:00 | PART | The Conductor missed both slots on 10-28. Owner asks have no age or timeout (AB §4) |
| F3 | Turn goals into ordered work: daily list, weekly plan, replan, cut list | Producer | PART | It writes plans. A run cost 595k plus an event run of 388k on day one |
| F4 | Limit work in progress: depth before breadth | Producer's "WIP cap" | **NO** | No code reads it. FOUNDRY has 82 doing and 515 built or validated |
| F5 | Track the day against the plan | Producer cadence | DES | `PRODUCER_CADENCE_*` is `doing` |
| F6 | Build | FOUNDRY | YES | 93% of rings verified (AB §8.22) |
| F7 | Wake an idle builder when it has work | Dispatcher doorbell; re-ring at 300, 900 and 1800 s | YES | 53da033d1b; `no_handoff` in the schedule |
| F8 | Keep the builder's context fresh | seat_restart backstop, plus restart per ticket | PART | Live; the kill path is unexercised (AB §8.24) |
| F9 | Recover a dead seat | Dispatcher `recover_dead` | OFF | false on both seats |
| F10 | Run game tests on the second PC (SteveDesktop) | testq tick, filler, sweep | PART | 301 of 409 jobs caught nothing (RR §0); FlowWorks only, because the mod variables are unset |
| F11 | Keep the test lane's evidence valid | steward | **NO** | RUNNING ends an incident (`steward.py:17`); a dead colony keeps running jobs |
| F12 | Turn test results into item state | `ingest.py` → verify events → model | **NO** | A fail never demotes (`model.py:2060`); QUARRY has 3 passes, 26 fails and still reads `validated` |
| F13 | Curate findings: fold repeats, surface new failures | `findings_fold.py` | PART | Built at 4c0b13067d; the item is `doing`; 131 untriaged |
| F14 | Make "done" mean done: real sha, criteria met | `rimflow close` / `implemented` / `verify` | **NO** | Implicit HEAD; owed criteria only warn (`cli.py:1828,1846`) |
| F15 | Judge each finished piece of work independently | interim GPT reviewer (a ritual) plus Arbiter (advisory) | **NO** | Nothing in the close path checks a review; Arbiter verdicts are `advisory`; its trial verdicts went to the wrong file |
| F16 | Check the judges: sample, calibrate, hard flags | Auditor plus `audit_prescreen` / `audit_hardflag_file` | PART | The filer is built (a0703d326d); the known fake-close defect has been unfixed for 20 h or more |
| F17 | Get the defects that review finds fixed | nobody | **NO** | DEFECT tickets join the same queue as everything else (GR R08) |
| F18 | GPT review of every finished component and of the whole system | ad hoc, by hand | **NO** | No program and no cadence. The owner "thought we were doing that" |
| F19 | Measure machine, accounts, runway and burn | ops_watch every 15 min | YES | Every point is MEASURED, ESTIMATE or UNMEASURED |
| F20 | Diagnose alarms and act on cost | Operations (2 clock runs plus 2 alarm runs a day) | PART | Its alarm runs ran out by midday; it is blocked by a stale watch |
| F21 | Route every alarm to someone who is woken | ops_watch, steward and deadman items | **NO** | All of them file `--for BENCH`, which is `wake: false`; 6 alarms sit stranded |
| F22 | Watch the watchers | deadman, timer-guard | PART | The deadman files to BENCH as well (RR §0) |
| F23 | Turn lessons into skills and memory | Auditor's Monday fold, 40 a pass | **NO** | 626 lessons arrived and 2 were folded in 7 days |
| F24 | Propose process improvements | Innovator, 3 runs a week | PART | One proposal in its life, superseded by the owner |
| F25 | Decide whether v3 beats v2 (the kill criterion) | `v3_vs_v2.py`, health check | OFF | The timer does not exist; the primary measures are UNMEASURED |
| F26 | Daily health check, planted faults, process model | designed | DES | 3 items `doing` |
| F27 | Spend control: token caps, helper caps, account choice | role_launch caps, helper_budget plus hook, account_pick | PART | Token caps are alarms after the fact (Arbiter used 1.02M against 500k). Helper caps are enforced. account_pick only recommends |
| F28 | Serialize the live game and respect the owner at the machine | bridge lock, idle_probe | YES | |
| F29 | Check the game grant before live work | by hand | **NO** | 5 tickets bounced when the grant lapsed |
| F30 | One config truth | `dispatcher_schedule.json`, role files, selftests | PART | Role headers and `_why` text drift from the config (AB §8.1-5) |
| F31 | Pause everything | Dispatcher `PAUSE` file, OFF files | YES | |
| F32 | Publish, mirror, telemetry | timers | PART | 18 publish errors on day one |

Count: 32 functions. Today 7 work, 13 work in part, 9 are broken or absent, 1 is off by design and 2 are only designed.
**The 9 broken ones are exactly the functions that close loops:** limit WIP, keep test evidence valid, turn results
into state, make "done" honest, judge independently, get defects fixed, run GPT reviews, route alarms, fold lessons.
The chairs exist; what is missing are the gates that would let a chair's output change anything.

---

## 2. Invariants (enforced by programs, not by role prose)

Each invariant has one enforcing program and one forced-failure test (§6).

- **I1. Done is earned.** An item reaches `done` only when all of these hold:
  - an explicit sha exists and touches something other than the ledger, or the close carries `--no-code "<what>"`;
  - every owed criterion passed against **that** `built_sha`;
  - a **blind GPT review of that sha** reads PASS;
  - no newer fail is recorded against that sha.
  A fail against the current `built_sha` demotes the item to `built` and owes the criterion again.
  Enforced by: `rimflow close`, `verify` and `model`.
- **I2. Depth before breadth (current focus).** FOUNDRY has at most **N = 3 focus items** (started, not done).
  `rimflow next` offers a new item only while focus is below N. For a focus item, the next step (fix a fail, answer a
  review, re-test) always ranks above new work. A Judge DEFECT re-opens the **same** item into focus, not a new ticket
  at the back of the queue. An item waiting on a slow external (a Steve job, the owner) moves to `waiting`. It leaves
  the focus count only while a dated wait is running. **At most 2 items may be waiting**, so the builder keeps moving
  without going wide. Enforced by: `rimflow next` and the item state model.
- **I3. No idle builder with workable work.** If FOUNDRY is idle while `next --peek` would give it something, it is
  rung. A wait is a state, not idleness. Enforced by: the Dispatcher (already true, 53da033d1b).
- **I4. Every alarm lands on a woken owner.** `rimflow file/spawn` refuses `--for` a seat that nothing wakes unless
  `--needs owner`. Every alarm kind maps in **one table** to exactly one of these:
  - program containment (pause the lane, re-ring);
  - a FOUNDRY focus item at P0;
  - a Planner event run;
  - the owner's phone.
  Enforced by: rimflow, plus a routing table checked by a selftest.
- **I5. Test time buys valid evidence, on what is in focus.**
  - A Steve incident ends only on a DONE job with a green canary that started after the incident began.
  - INVALID results do not count as lane activity.
  - The filler serves focus items' test chains first, then regressions of items closed in the last 7 days, and the
    oldest chains only after that.
  Enforced by: steward and testq.
- **I6. The watcher is watched from outside.**
  - A stale ops_watch still launches the Planner in degraded mode, marked UNMEASURED, with the instruction
    "diagnose the watch first".
  - The deadman writes to the owner's phone brief with no AI and no ledger in the path.
  Enforced by: role_launch, deadman and pulse.
- **I7. One config truth, fail-closed.** Every number, slot and on/off switch lives in `dispatcher_schedule.json`.
  Role files hold none of them. A missing key refuses to load (no code defaults). A lint selftest fails on a role file
  that restates a number. Enforced by: selftests.
- **I8. Nothing ages silently in front of the owner.** Every owner ask appears in the twice-daily phone digest with its
  age and with what it blocks. The digest is built by a program from the ledger. The Conductor reads before he does
  (standing rule). Enforced by: the pulse digest.

---

## 3. The minimal design

### 3.1 Roster: 4 AI actors (one of them external) and 4 programs

| Actor | Kind | Runs | One line |
|---|---|---|---|
| **Conductor** | AI seat (BENCH, opus) | only while the owner is present | Talks with the owner, records his rulings, and runs his helpers. **No scheduled runs.** |
| **FOUNDRY** | AI seat (sonnet, opus per item) | rung by the Dispatcher | The only autonomous builder. It works its focus items through the build loop (§3.3). |
| **Planner** | headless role (Producer + Operations + Innovator) | 07:30 daily, plus events | Orders the work, picks the focus, reads cost and health, diagnoses alarm residue, cuts. Once a week it asks "what should we do better?". Token-aware. |
| **Judge** | headless role (Arbiter + Auditor) | 13:00 daily | Token-blind and never the maker. It samples GPT's PASSes and a random slice, re-runs evidence, settles GPT/maker disputes, and re-opens defects into focus. Weekly, it calibrates and promotes recurring lessons. |
| **GPT reviewer** | external model, called by a program | every done claim, plus weekly | Gives a blind review of each finished component (sha + criteria + evidence, never the maker's story) and of the whole system each week. |
| **Dispatcher** | program, 2-min timer | always | Wakes FOUNDRY, launches the Planner and Judge, restarts seats, routes alarms through the one table. |
| **ops_watch** | program, 15-min timer | always | Measures everything, including the plan-vs-actual, health and v3-vs-v2 families. Files alarms through the routing table. |
| **testq** | program, 1-min timer | always | Runs SteveDesktop: admission, steward, filler, ingest, findings fold. |
| **rimflow** | CLI (no timer) | on call | The ledger. **I1 and I2 live here**: `next` enforces focus; `close` and `verify` enforce honest done and call `review_gate`. |

Kept as they are, outside the roster because they are plumbing that decides no work: pulse (phone brief and digest),
deadman and timer-guard, mirror, telemetry, scratch-reap, nightly selftests, the bridge lock, idle_probe and
helper_budget with its hook.

From **six scheduled AI roles to two**. From about 11 scheduled role runs a day to **2 plus at most 2 event runs**.

### 3.2 Merges, and what each merge costs

**M1. Operations + Producer + Innovator → Planner.**
- *What is lost.*
  - Operations was the only token-aware role, so the planner no longer plans blind to cost. That is a gain: a plan
    that ignores runway is the wrong plan.
  - The Innovator's independent "fresh eyes". This is accepted:
    - In its life it made one proposal, and the owner superseded it.
    - It cannot start a trial (the expiry watchdog is not built).
    - The weekly GPT system review (§3.4) is a **more** independent outside eye than another Claude run on the same
      prompts.
  - Operations' separate alarm runs. These are replaced by Planner event runs on alarm residue (§3.5), after a program
    has already contained the alarm.
- *What the merge removes.*
  - The `after_role` chain (Producer and Conductor waited on Operations).
  - The REPLAN REQUEST handoff between two AIs.
  - The Producer-to-Conductor relay of TESTQ mod choices. The Planner writes the mods straight into testq's config file,
    and testq prints back what it applied.
  - Three role files.
- *What the owner already ruled on.*
  - Operations owns the v3 health check. That stays as an ops_watch family, which the Planner reads.
  - The cadence ruling ("2-3 times a day ... a tuning parameter") is met by **event** runs, not by clock slots. The
    ops_watch plan tracker fires the Planner when the day is BEHIND, RUNNING_DRY, has a big slip, or a focus item is
    STUCK. That is at most 2 extra runs a day, so a quiet day costs 1 run and a bad day costs 3.

**M2. Arbiter + Auditor → Judge** (the merge the owner first asked for).
- *Why it was advised against before.* The Auditor checked the Arbiter. Merging them would have let a Claude judge
  audit itself.
- *Why that objection no longer holds.* In this design **GPT is the first-line judge** on every close. That is the
  interim reviewer, made binding and enforced by `close`. So the Judge is now the Claude model checking a GPT
  verdict: two different models, and the Judge never sees the maker's narrative. The independence the old split was
  protecting is kept, and it is stronger, because it is now cross-model and not two runs of the same model.
- *What is lost.* Nobody samples the Judge's own SOUND verdicts every day. Instead, the weekly GPT system review gets a
  random 5 of the Judge's verdicts to re-judge, and the Judge's false-accept rate is reported (§6).
- *What is gained.*
  - The Judge **may re-open** an item. It writes a `reopen` event: the item goes back to `built` with a new owed
    criterion, which puts it straight into FOUNDRY's focus. That closes GR R08 ("review finds defects, nobody fixes
    them") without a new ticket.
  - The 11:00/17:00 Arbiter batch disappears, and with it the 1.02M-token run.

**M3. Conductor quick checks → pulse digest (no AI).**
- The 08:00/20:00 headless Conductor runs mostly re-read things a program can list: owner asks, alarms, yesterday's
  closes.
- The pulse digest (05:45 and 17:15 today) gains three sections:
  - owner asks with their age and what each one blocks (RR T11);
  - open P0 alarms;
  - focus items and their state.
- *What is lost.* An AI summary twice a day. The digest is shorter and cannot hallucinate.
- When the owner opens BENCH, the Conductor reads the same digest first.

**M4. Dispatcher absorbs alarm routing.** A single `alarm_routes` table in the schedule says, for every alarm kind:
containment program, FOUNDRY P0, Planner event, or phone. ops_watch, steward and deadman call one function that reads
it. This replaces three separate `--for BENCH` paths.

**M5. testq absorbs the findings fold and the v3 health trace collector.** The fold already runs after each ingest
(4c0b13067d). Its new failures become FOUNDRY items; repeats are folded. Rig-health findings go through the routing
table, not to "Operations' lane item".

### 3.3 The build loop (FOUNDRY, enforced by rimflow)

```
claim (focus slot free?) ── no ──> work an existing focus item's next step
   │ yes
build → commit (real sha) → `implemented --sha S` (criteria L0-L4)
   │
   ├─> TEST: local selftests + testq jobs, each `verify` recorded against S
   │      fail ─> fix → new commit S' → `implemented --sha S'` (all criteria owed again) ─> TEST
   │      3 fails on the same criterion ─> item marked STUCK ─> Planner event (split / rescope / opus / cut)
   │      wait on Steve or owner ─> `waiting` (max 2) ─> take the next focus step meanwhile
   │
   ├─> all criteria ≤ L3 pass on S ─> `review_gate` sends a BLIND GPT review of S
   │      (diff, criteria, evidence paths, test logs; no maker summary, no item title prose)
   │      FAIL ─> each defect becomes an owed criterion on the SAME item ─> fix loop
   │      PASS ─> `close --sha S` is now allowed
   │
   ├─> L4 owed (owner look) ─> `waiting:owner`, shown in the digest with its age
   │
   └─> done ─> Judge may sample it (≈1 in 3, plus every hard flag) ─> DEFECT re-opens into focus
```

- **"Test repeatedly until it passes"** is the inner loop. It has no iteration cap. STUCK is a signal to the Planner,
  not an exit.
- **"Then a blind evaluation one more time"** is `review_gate`. It runs once per sha, and again after any fix, because
  a fix is a new sha.
- **"Every finished component to GPT"**: a finished component *is* a close, so I1 makes it unconditional.

### 3.4 GPT's two duties, both started by programs

1. **Component review** (`review_gate.py`, called by `close`).
   - It sends to `gpt_consult.py` the diff of the sha, the criteria manifest, the evidence files and the last test logs.
   - It writes `review/<item>/<sha>.json` with the verdict, the model and the input hash.
   - `close` refuses unless a PASS record exists for that exact sha.
   - The maker can request a review, but cannot write the record.
2. **System review** (weekly, Sunday 06:00, run by the Dispatcher as a program, not as a role).
   - It assembles the effective schedule, the role files, the alarm routing table, the week's ops_watch digest, the
     Judge's verdicts and 5 random Judge verdicts.
   - GPT reviews the packet.
   - The result is the Planner's Monday input. The Conductor shows it to the owner.
   - It also runs once whenever the roster or a gate changes, i.e. any commit to `rimflow/cli.py`, `model.py`,
     `dispatcher.py`, `role_launch.py` or the schedule's roles or routes block. The commit's own component review
     covers the code; this run covers the whole.

### 3.5 Alarm routing table (replaces `--for BENCH` everywhere)

| Alarm class | Containment (program, immediate) | Then |
|---|---|---|
| Steve lane INVALID or canary red | pause the lane (testq already does this on the second red; make it the first) | FOUNDRY P0 focus item; the incident stays open until green (I5) |
| Steve unreachable | stop admitting, re-probe | phone at T+30, Planner event at T+120 |
| Seat dead, ring undelivered, idle with a full queue | re-ring (exists) | Planner event; phone if it is still dead after 1 h |
| Timers stopped, ops_watch stale, Dispatcher stale | deadman → phone (no AI) | Planner degraded run (I6) |
| Disk, publish errors, evidence path | none | FOUNDRY P0 item |
| Accounts and runway | none (`account_pick` stays advisory) | Planner reads it at 07:30; an event run only on FLOOR |
| Overspend (a run over 2x its allowance) | hard stop at 2x (RR T10) | a line in the digest |

An alarm repeat is suppressed for 6 h **unless it got worse** (RR T12).

### 3.6 Each part of v3, and what happens to it

| v3 part | Fate | Why |
|---|---|---|
| Conductor | **Keep, session only.** Its scheduled runs are deleted (M3) | The owner's rule: a light orchestrator for talking with him. Away-time reporting is a program's job |
| Producer | **Merged** into the Planner (M1) | |
| Operations | **Merged** into the Planner (M1). Its alarm runs become Planner events after program containment | |
| Arbiter | **Merged** into the Judge (M2). Its per-close gate moves to GPT through `review_gate` | |
| Auditor | **Merged** into the Judge (M2). The hard-flag filer stays a program (a0703d326d) | |
| Innovator | **Deleted as a role.** Its question goes into the Planner's weekly run; outside eyes come from the GPT system review | |
| FOUNDRY | **Keep.** Gains the focus rule and the honest close | |
| Dispatcher | **Keep.** Gains alarm routing and the weekly system-review launch; 2 roles to launch, not 6 | |
| ops_watch | **Keep.** Gains plan-vs-actual, health trace and v3_vs_v2 as families, with no new timers | |
| seat restart | **Keep the FOUNDRY backstop ON** (the owner ordered a fresh context per ticket), with the forced-kill proof owed (§6). BENCH goodbye: as built | |
| testq / SteveDesktop | **Keep.** The steward ends incidents only on green; the filler serves focus first; the Planner's mods are written to the config and read back | |
| findings fold | **Keep** (built). It runs inside the testq tick; new failures become FOUNDRY items | |
| health check (`V3_HEALTH_*`) | **Shrink.** Keep output tracing and owner-message tagging as an ops_watch family. Planted faults stay **OFF** | Planting faults into paths known to drop alarms measures nothing until I4 holds |
| process model (`OPS_MODEL_*`) | **OFF**, parked. Not deleted, since the owner asked for it; un-parked only after I1-I8 have been green for 14 days | A 10-15 CPU-minute daily fit of a workflow that is still changing shape fits noise |
| Producer cadence | **Replaced** by Planner event runs on plan slips (M1). No `track_slots_local` key | |
| interim GPT reviewer | **Becomes binding** as `review_gate` (I1) | |
| account_pick, throttle bands | Bands **deleted** (neutralized since d92c4c825e, dead config). account_pick stays a reading inside ops_watch | |
| helper caps | Keep `helper_budget` plus the hook. Delete `helpers_max` on headless roles (unused) | |
| lessons fold | **Retired as a queue** (RR T7). The Judge's weekly run promotes a lesson only when the findings fold or a Judge DEFECT shows it recurring | |

### 3.7 Order of the build: depth applied to the redesign itself

The migration is itself depth-first. Do **one** step at a time. Each step goes through the build loop of §3.3 (test
until pass, then a blind GPT review, then close) before the next one starts.

1. **I1, honest done.** `close`/`verify`/`model` refusals and demotion, plus `review_gate.py`. It goes first because
   every later step's "done" depends on it. On landing, run a replay: list what would be demoted today (RR expects
   about 12).
2. **The roster flip.** This is a config and role-file change: Planner and Judge on; Conductor quick checks, Producer,
   Operations, Arbiter, Auditor and Innovator off; the digest gains its sections. It is cheap, and it removes noise
   before the gates go live.
3. **I4, the routing table.** Re-file the 6 stranded alarms and the 23 BENCH `proposed` items. FOUNDRY gets build
   work; the owner gets judgment calls.
4. **I2, the focus rule.** On landing, the Planner picks the 3 focus items. All other `doing` items go back to
   `proposed`, and their leases are released. `built` and `validated` items keep their state but are not focus; the
   Planner pulls them in by priority, oldest-built first.
5. **I5, the steward and filler.**
6. **I6, the degraded Planner and the deadman to the phone.**
7. **I7, the config lint.**
8. The first **weekly GPT system review**, of the system as it then stands.

---

## 4. A day in the life

| Time (PDT) | What happens | Actor |
|---|---|---|
| all day | FOUNDRY works its ≤3 focus items: build, test until pass, blind GPT review, close. When idle with work it is re-rung. It restarts fresh after each close | FOUNDRY, Dispatcher, rimflow |
| all day | Steve runs focus chains first, then recent-close regressions. A red canary pauses the lane and files a P0 focus item | testq |
| every 15 min | Measure; route alarms through the table; plan-vs-actual reading | ops_watch |
| 01:30 | Nightly sweep of the focus mods plus the mods of the last 7 days' closes | testq |
| 05:45 | Phone brief: focus items, P0 alarms, owner asks with age | pulse |
| 07:30 | **Planner**: reads cost, health and yesterday's closes; writes today's plan; picks or holds the focus; writes test-lane mods; diagnoses alarm residue; writes a cut list if needed. Weekly on Monday: "what should we do better", plus the GPT system review | Planner |
| 12:00-18:00 | *Only if* ops_watch reads BEHIND, RUNNING_DRY, STUCK or a big slip: a Planner event run (≤2 a day) | Planner |
| 13:00 | **Judge**: samples GPT PASSes since yesterday (≈1 in 3, all hard flags), plus a random calibration slice; re-runs evidence; re-opens DEFECTs into focus. Weekly on Monday: calibration report; promote recurring lessons | Judge |
| 17:15 | Phone digest | pulse |
| when he is present | Conductor: answer first; card for each ruling; relay the Planner's cut list and proposals, and the Judge's questions | Conductor |
| Sun 06:00 | Weekly GPT whole-system review packet | Dispatcher → GPT |

**The handoff list (10, down from about 30 rows in AB §4):**
1. Dispatcher → FOUNDRY: a doorbell ring.
2. Dispatcher → Planner / Judge: a launch.
3. rimflow `close` → GPT: `review_gate` (synchronous; the record is written by the program).
4. testq → ledger: verify events and findings (through the fold).
5. ops_watch / steward / deadman → the routing table → {containment, FOUNDRY P0, Planner event, phone}.
6. Planner → FOUNDRY: the focus pick and the queue order (ledger raises).
7. Planner → testq: the mods file, with a printed readback.
8. Judge → FOUNDRY: a `reopen` (the item re-enters focus).
9. Planner / Judge → owner: ledger items `--for OWNER`, shown in the digest with age and relayed by the Conductor.
10. Weekly GPT system review → Planner (Monday input) and → owner (through the Conductor).

---

## 5. Delete outright; keep OFF until stable

**Delete outright:**
- **Role files and schedule entries:**
  - The `operations.md`, `producer.md`, `arbiter.md`, `auditor.md` and `innovator.md` role files and their schedule
    entries. They are replaced by `planner.md` and `judge.md`, which together are expected to be shorter than any two
    of the five.
  - The Conductor's `quick_checks_local`, `quick_token_cap` and `pre_launch` `delegated_digest`. The digest program
    itself stays and pulse uses it.
- **Dead mechanisms:**
  - `after_role` chaining.
  - `throttle_bands` and `throttle_order`: neutralized and dead config.
  - The `golive` mirror of the roles list. It duplicates `enabled` and is a second place to forget.
  - `helpers_max` on the headless roles.
- **Dead or unbuilt features:**
  - The REPLAN REQUEST note protocol.
  - The Producer→Conductor TESTQ relay.
  - The `track_slots_local` cadence design.
  - Innovator probation, trials and the expiry-watchdog item (`INNOVATOR_BUILD_EXPIRY_WATCHDOG_REVERTS`).
  - The Arbiter `verdicts: advisory` switch and the binding criteria (≥30 verdicts, and so on): moot once GPT gates
    closes.
- **Lessons:** the lessons inbox as a counted queue (the 40-a-week fold quota and the 14-day rule). The files stay as a
  searchable corpus.
- **Stale routing:** every `--for BENCH` alarm path (ops_watch rules, steward, deadman), and the BENCH residue in
  `slot_rules.json` (`fallback_n` BENCH).
- **Separate timers:** `rm-v3-vs-v2.timer` (it never existed) and the designed `rm-process-model.timer`. Their work, if
  it comes back, is an ops_watch family.

**Keep OFF until I1-I8 have each passed their forced-failure test and the system has run 14 days green:**
- dead-seat auto-recovery (`recover_dead`);
- planted faults (`health_drill`);
- the process model;
- account_pick `hold` (act on SWITCH/HOLD);
- the Archmagi second lane;
- the v3-vs-v2 **kill verdict**. Its measurement is cheap, so compute it now as an ops_watch family; the *verdict*
  waits until "accepted items/day" exists, and I1 creates exactly that event;
- any new AI role or new timer.

**The freeze rule while this lands:** FOUNDRY's focus slots go to steps 1-8 of §3.7 and to P0 alarms. No new process
items are filed unless they replace something (RR T16).

---

## 6. Risks of the minimal design, and the forced-failure test for each invariant

**Risks:**
- **R-a. GPT becomes the single gate and a single point of failure.**
  - If Codex is down or out of budget, nothing closes. Mitigation: a close may go to `done:unreviewed`. That state
    counts as open for focus (it holds a slot), so the backlog is visible and cannot widen.
  - GPT can also be wrong in a systematic way. The Judge samples GPT PASSes, and its weekly report gives GPT's
    false-accept rate.
- **R-b. The Planner is a bigger chair.** One run now carries cost, plan, alarms and improvement. If it fails, all four
  are late.
  - Mitigation: alarms are contained by programs **before** the Planner sees them, and the plan of yesterday stays in
    force.
  - The run is capped at 2x its allowance, with a hard stop.
  - If the 07:30 run misses its window it is owed and runs late, once (RR T8). It is not dropped.
- **R-c. The focus cap of 3 is too tight.** FOUNDRY could stall when all 3 focus items wait on externals.
  - Mitigation: `waiting` (≤2) frees a slot.
  - Tune N from data, not by feeling. If the "idle with a full queue" alarm fires more than once a day in week 1,
    raise N to 4.
- **R-d. Merging the Arbiter and Auditor loses a check on the Judge.** Mitigation: the weekly GPT system review re-judges
  5 random Judge verdicts.
- **R-e. Re-opening items rewrites "done" history.** Mitigation: `reopen` is an event; the original close stays in the
  ledger. KPIs count first-time-right and re-opened separately.
- **R-f. Migration churn.** Mitigation: the steps are ordered (§3.7) and one is in flight at a time. Each step's off
  switch is its schedule flag.

**Forced-failure tests.** Each one is a selftest on a fixture ledger or clock, plus one live drill where marked.

| Invariant | Forced failure | Pass condition |
|---|---|---|
| I1 | Close with owed criteria; close with no `--sha`; close with a ledger-only sha; close with no GPT record; close with GPT PASS on S but built at S'; a fail verify after `validated` | Each is refused or demoted. A replay of the real ledger lists the items demoted today (QUARRY must be in it) |
| I2 | Give FOUNDRY 3 focus items and call `next`; re-open one by the Judge; mark one `waiting` 3 times | `next` offers only focus steps; the re-opened item ranks first; the third `waiting` is refused |
| I3 | A fixture with FOUNDRY idle, queue workable, doorbell armed; then a consumed ring with no handoff | A ring within 1 tick; a re-ring at 300 s; an `idle_full_queue` alarm after 3 |
| I4 | For every alarm kind in the rules, fire a synthetic alarm. `rimflow spawn --for BENCH` without `--needs owner` | Each lands on its routed owner (the selftest enumerates the table, so a new kind with no route fails). The spawn is refused |
| I5 | Steward sequence RUNNING → INVALID → RUNNING; a canary red; a queue with a focus chain and an older chain | The incident stays open through RUNNING; it closes only on DONE plus a green canary after the start. A red pauses the lane. The focus chain is admitted first. **Live drill:** kill the colony on Steve once |
| I6 | Stop ops_watch for longer than its limit (**live drill**); delete status.json in a fixture | The phone brief carries the deadman line with no AI run. The Planner launches degraded; the other roles are refused |
| I7 | Remove a required key from the schedule; add "runs at 13:00" to `judge.md` | The load refuses; the lint fails |
| I8 | A fixture with an OWNER item 5 days old blocking 2 items | The digest shows the age, the blocked count and a recommended default |
| whole | The 48-hour unattended proof (GR §8) after all of the above, with **one** planted fault per invariant, chosen and logged by the owner or by GPT (not by the system) | Every fault is caught by its invariant's enforcer within its stated time, with no manual discovery by the owner |

**Expected spend (ESTIMATE).** Day one cost about 4M weighted tokens of scheduled role runs:
- Conductor 2 × 233k
- Operations 373k + 257k + 320k
- Producer 595k + 388k
- Arbiter 1.02M
- Innovator 262k, every other day

The minimal design runs the Planner at about 600k a day plus ≤2 event runs, and the Judge at about 700k. That comes to
about **1.3-2.5M a day, roughly half**, plus GPT review calls on the Codex budget, one per close.
