# RimFlow v3 risk review: the Opus response (2026-10-29)

Item: V3_WORKFLOW_AUDIT_EVERY_CLOCK_AND_DOOR, step 3 of 3. Responds to `design/RimMandrake/rimflow_v3_gpt_risk_review_2026-10-29.md` (GPT, verbatim) which reviewed `design/RimMandrake/rimflow_v3_workflow_as_built_2026-10-29.md`. DESIGN ONLY: nothing here is ticketed yet.

## Executive summary for the owner

GPT is right on the main point: v3 is good at recording work and weak at proving it. Checked against code and
ledger: `close` accepts unmet criteria and silently uses HEAD; a failing check never demotes "validated"; alarms
are filed to BENCH, a seat nothing rings, and six sit unclaimed now.
GPT was wrong or overstated on four points: QUARRY had 3 passes before its 26 fails (not 0); the Steve repeats are
explained by the code (one designed retry, then manual resumes that left the dead game running); the steward does
wake BENCH headlessly for Steve incidents; and the FOUNDRY idle-wait and helper-limit risks were fixed today.
It understated two: 626 lessons arrived this week and 2 were folded (not 40), and process-only commits are 96%
of the last 24 h against your 61% target.
The five most important moves:
1. Route every alarm to a rung seat, plus a phone path with no AI.
2. Make `close` and `verify` tell the truth: no owed criteria, explicit sha, a current fail demotes.
3. End a Steve incident only on a green canary, not on RUNNING.
4. Retire the lessons inbox as a queue; freeze new process work until the share falls.
5. Prove the daylight-saving fallback before Sunday 01:00 PDT.
18 draft tickets (9 P0, 9 P1) plus 2 raises on existing items; six calls are yours (§6).

## 0. How this response was checked

GPT read only the documents. This response re-checked its load-bearing claims against code, config and the
ledger on the bench clone at 2026-10-29 ~20:30Z (HEAD 8abeab6784). The probes:

| Probe | What it read | Result |
|---|---|---|
| `rimflow/cli.py` `cmd_close` (l. 1807-1845) | the close verb | `--sha` defaults to `git rev-parse HEAD`; owed criteria print a **warning, not a refusal** (comment: "step 3's call"); no reviewer record is checked |
| `rimflow/model.py` `_criterion_passed` / verify (l. 2036-2070) | the acceptance state machine | a `fail` verify is recorded but never demotes `validated`; a pass is not tied to the current `built_sha` |
| `model.replay()` over the whole ledger | 5,341 items | 1,525 open (FOUNDRY 1,471, OWNER 30, BENCH 24); open `built` 348, `validated` 175, `doing` 103; 12 of the 523 built/validated items have more failing than passing runs; `FLOWWORKS_QUARRY_DIGGING_1` = **3 passes, 26 fails**, still `validated` |
| `Utils/testq/steward.py` | the SteveDesktop steward | RUNNING is "the only state that ends an incident" (l. 17, 527); a claim with a live lease pauses the clock without limit (l. 338); escalations spawn `--for BENCH` (l. 473); a headless **BENCH** LLM wake exists at T+30 (l. 46-60) |
| `Utils/testq/testq.py` l. 325-340 | canary handling | the first canary red **auto-resumes once by design**; only a second consecutive red pauses |
| `Utils/ops_watch_rules.json` `alarm.for` | ops_watch alarm routing | `"for": "BENCH"` |
| `Utils/deadman_check.py` header | the outside dead-man | files its alarm "the same way ops_watch does", so also to BENCH |
| `rimflow/role_launch.py` l. 1187-1192 | the launch gate | a non-MEASURED ops reading refuses **every** role, Operations included; no degraded mode |
| ledger, BENCH open items | alarm receivers | `OPS_DEADMAN_REVIVE_17EC/_AEA3/_129E`, `OPS_STEVE_UNSTICK_UNCLAIMED_7C91/_0B75`, `OPS_STEVE_DIAGNOSE_INVALID_CE0E` all `proposed`, unclaimed |
| `infrastructure/state/lessons/` + git log 7 d | lessons queue | 1,096 files; 626 added and **2** deleted in 7 days |
| `ops_watch/status.json` at 20:07Z | live KPIs | process-only share **96.4% (502 of 521 commits) over 24 h**, 73.6% over 7 d; untriaged findings 131; Steve "nothing" hours 32.9 h/7 d (301 of 409 jobs) |
| `AUDITPRESCREEN_FIX_WAVED_THE_FAKE_THROUGH` | known gate defect | still `proposed`, unclaimed, 20 h after filing |
| `rimflow/roles/operations.md` header vs schedule | config split | header says "written, NOT enabled"; `dispatcher_schedule.json` says `enabled: true` |
| `date` | clocks | the host is on PDT; US daylight saving ends **Sunday 2026-11-01** (01:00-02:00 repeats); `testq-sweep` runs at 01:30 local |

Probe scripts: `/home/mandrake/.seat-tmp/BENCH/.../scratchpad/probe*.py` (session scratch, not kept).

## 1. Fixes already in flight (not duplicated below)

| Item | State | Which GPT risks it covers | What this response adds on top |
|---|---|---|---|
| `FOUNDRY_IDLE_REWIRE_PARKS_ON_LANE_WAITS` | **done**, 53da033d1b: a no-hand-off wake re-rings at 300/900/1800 s then escalates; FOUNDRY.md says a lane wait is not idle | R03, §3.5 wait-cooldown loop | Nothing new. Its proof still owed: a live day with slow jobs and no ~70 min idle gap (tripwire in §2 R03) |
| `CONDUCTOR_HELPERS_UNIFY_FOUR_LIMITS` + ae46aea917 | **done**: one enforced number; no cap 1:1 with the owner | R10 helper half, R15 helper half | Nothing new |
| `STEVE_LANE_FIX_DEAD_COLONY_CANARY_RED` | doing (OWNER seat): find why the colony dies, make a canary red restart the game, invalid-canary counts as wasted (regression) | R02 root cause and the waste metric | Only the **steward's** incident-end rule (RUNNING is not recovery) and the claim pause. Not the runner |
| `FINDINGS_FOLD_BUILD_QUARRY_SAID_IT_23X` | proposed | R04 findings half (131 untriaged), §3.2 | It must be the findings' consumer, so it moves to P0, and it needs the build-scope rule GPT asks for in §3.2 (retire a failure only on passes of the same build/scenario/environment) |
| `TESTLANE_PLAN_WIRE_PRODUCER_PICKS_UNHEARD` | proposed | R13 | Its Done-when should include a readback: testq's applied fill/sweep mods printed next to the plan's |
| `FLOWWORKS_OWNER_RECONCILE_CUTOVER_STALE` | proposed | R15 ownership text | The routing half (alarms still filed for BENCH) is code, not prose; that is ticket T2 |
| `V3_HEALTH_BUILD_DAILY_PULSE_DAY_ONE` | proposed, owner role choice pending | R12, §3.4, GPT §7 "prove usefulness" (planted faults, output tracing) | Sequence it AFTER the P0 fixes: planting faults into paths that are known to drop alarms measures nothing new |
| `OPS_MODEL_BUILD_V3_TWIN_FIT_DAILY` | ready | R12 | Recommend deferring (decision D5): GPT §3.2/§7 and this response agree it is lower value than the missing guarantees |
| `PRODUCER_CADENCE_DESIGN_MORE_THAN_WEDNESDAYS` | ready | §5 Producer 1 event/day | Design it as **carry-over of unmet events**, not more clock slots (decision D5) |

## 2. Risk by risk: agree?, remedy, cost

Cost columns: **build** (lines of code, rough), **tokens/day** (steady-state AI spend the change adds or removes),
**process share** (does it add process commits, or remove them). The process-only commit share is 73.6% over 7 days
and 96.4% over the last 24 h against a 61% target, so a remedy that removes process wins any tie.

### R01: completion cannot be trusted. AGREE, and it is the top risk

Verified in code: `close` takes `HEAD` when `--sha` is omitted; owed criteria only warn; a failing verify never
demotes `validated`; nothing checks a reviewer record. GPT's one factual slip: QUARRY was not "26 fails, 0 passes". It
had **3 passes** (that is how it legitimately reached `validated`) and then 26 fails that changed nothing. That makes
the defect sharper, not weaker: the state machine records history, not current truth. Scale: 12 of 523 open
built/validated items have more fails than passes. It is a narrow hole today, but the hole is in the gate itself.

**Remedy: FIX, in two small code changes, and leave the full "acceptance event" GPT designs for later.**
1. `close` refuses owed criteria (the warning becomes a refusal; the existing `drop`/`supersede` remain for
   abandoned work) and refuses an implicit `HEAD`: `--sha` must be explicit, or `--no-code "<what was verified>"`.
   A close whose sha touches none of the item's cited paths prints the files and needs `--why`. (T1)
2. A `fail` verify on an item whose `built_sha` is the current build demotes `validated` to `built` and marks the
   criterion owed again; a pass counts only against the current `built_sha`. (T3)
   L0: selftest_cli + selftest_model cases: unreviewed-owed close refused; bare close refused; fail-after-pass
   demotes; pass on a stale build_sha refused; a genuine full pass still closes.

The independent-review half (who must sign) is an owner call: decision D1.
**Cost:** ~120 lines + tests in `cli.py`/`model.py`; 0 tokens/day; one-off process commits, then fewer reopen tickets.

### R02: Steve burns hours on invalid evidence. AGREE; the mechanism is not a mystery

GPT lists six explanations for the repeats and says the evidence cannot pick. The code can: `testq.py` auto-resumes
the lane once after a first canary red **by design** ("an idle SteveDesktop costs more than one more attempt"), and
the 18:15 and 18:54 manual resumes left the dead 08:49 game running (ledger note on the in-flight item). The steward
then saw RUNNING and closed its incident each time. So the repeats are: one designed retry + manual resumes that
did not restart the game + an incident rule that treats RUNNING as recovery.

**Remedy: FIX the steward only (the runner side is in flight).** The steward ends an incident on the first
**DONE job with canary on** after the incident began, not on RUNNING. `testq.py` already has that predicate
(`lane_proven_after`, l. 1085-1110, used for the filler brake); reuse it. (T4)
L0: selftest_testq_steward: RUNNING-then-INVALID/CANARY keeps the incident open and its clock running; a DONE+canary
closes it.
**Cost:** ~40 lines; 0 tokens/day; removes repeat OPS_STEVE_* spawns.

On GPT's aside that "caught nothing" punishes passing tests: agree, and the in-flight item's split (invalid =
wasted, valid-and-green = assurance) is the right fix. No new ticket.

### R03: FOUNDRY stops when it waits. AGREE; FIXED TODAY

53da033d1b (after GPT's evidence window) adds bounded re-ring (300/900/1800 s) and an escalation, and FOUNDRY.md now
says a lane wait is not idle. **ACCEPT the residual** with a tripwire: any FOUNDRY idle gap > 30 min while
`rimflow next --seat FOUNDRY` would offer an item, measured by ops_watch, reopens it. GPT's open question (does a
blocked top item stop the Dispatcher seeing lower work?) gets a cheap L0 proof: T15.

### R04: work filed for receivers that do not exist. AGREE, worse than stated, one detail wrong

Verified: `ops_watch_rules.json` files alarms `for: BENCH`, the dead-man files the same way, and the steward spawns
`--for BENCH`. Six such items sit unclaimed (three dead-man revivals, two Steve unsticks, one invalid-diagnose).
GPT is wrong that BENCH is "never automatically rung": the steward starts one capped headless BENCH session at T+30
(one per incident, 4 h cooldown). That covers only Steve incidents; ops_watch and dead-man alarms reach nobody.

**Remedy: FIX the routing, RETIRE the dead receiver.** Every RUNNER-filed alarm goes to FOUNDRY (the seat the
Dispatcher rings) with `needs offline`, and Operations' alarm trigger reads the ledger OPS_* items as well as
status.json; `rimflow spawn/file` from RUNNER **refuses** a seat with no autonomous ring (BENCH) unless `--why`.
The six stranded items are reassigned in the same change. (T2) Findings: the in-flight FINDINGS_FOLD item is the
consumer; move it to P0.
L0: a selftest that spawns a test alarm from each producer (ops_watch, deadman, steward) and asserts the receiver
is a rung seat; a selftest that a RUNNER spawn for BENCH is refused.
**Cost:** ~60 lines across three files; adds work to FOUNDRY's queue that today silently rots (this is visible cost,
not new cost). Who repairs alarms is decision D2.

### R05: the monitor can block its own recovery. AGREE; and the dead-man shares the blind spot

Verified: `role_launch.py` refuses every role, Operations included, on a stale or unreadable ops reading. The
dead-man is a separate timer, which GPT could not see, but its only output is a ledger item for BENCH, and when the
Dispatcher is the thing that died, no role can be launched to read it. So the "outside" dead-man is outside the
Dispatcher's process but inside its delivery path.

**Remedy: FIX twice, both mechanical.**
1. Operations is exempt from the ops gate: it launches in a **degraded** mode with the reading marked UNMEASURED and
   a one-line brief "the watch is stale: diagnose the watch first". Other roles stay gated. (T5)
2. The dead-man (and any Dispatcher/ops_watch staleness) writes straight to the owner's phone brief through the
   existing no-AI pulse path, not only to the ledger. (T6)
L0: role_launch selftest with a stale status.json: Operations launches, Producer refuses; deadman selftest asserts
the phone-brief line.
**Cost:** ~50 lines; tokens only when the watch is actually stale (rare); 0 process added in steady state.
GPT's machine-down and systemd-down cases: ACCEPT (one PC; tripwire: a second whole-timer stop like AB §8.30 means
an off-box heartbeat, e.g. the Mac or SteveDesktop pinging a file, becomes P1).

### R06: incidents stop at a claim, a cap or a suppressed alarm. AGREE, partly

Verified: a claim with a live lease pauses the steward clock indefinitely; alarms repeat no more than every 6 h by
kind. The Operations "two alarm runs a day" did starve a diagnosis on day one.
**Remedy: FIX two, ACCEPT one.**
- The steward's claim pause is capped at 2 h of cover per incident regardless of lease renewals, and the incident's
  elapsed-impact clock never pauses (folded into T4).
- A repeat alarm of the same kind breaks the 6 h suppression when its severity worsens or the impact grows by a
  stated step (e.g. Steve idle doubling). (T12)
- ACCEPT the Operations alarm-run cap (2/day) once T2 and T4 exist: containment becomes mechanical (pause, restart,
  escalate) and no longer needs an AI run. Tripwire: an alarm held by the cap for > 6 h with its impact still
  growing.
**Cost:** ~60 lines; 0 tokens/day (fewer redundant alarm runs, if anything).

### R07: the learning queue cannot drain. AGREE; GPT understated it

Measured: 626 lessons added and 2 deleted in 7 days, not 40 folded. At that rate no cadence or cap will drain it, and
folding 600 lessons a week would itself be pure process.
**Remedy: RETIRE the inbox as a queue.** Lessons stay as a searchable corpus (the skill and grep paths already use
them); nothing counts them as owed; the 14-day inbox expectation and the 40/week fold quota are deleted. A lesson
earns work only when it **recurs**: the findings fold (in flight) and the Auditor's existing recurrence check promote
a repeated class to one rule or one ticket. (T7; owner decision D3 because the fold duty is in role files he set up.)
For the Auditor's inherited backlog (826 closes, 489 verifies, not re-measured here): ACCEPT sampling with known
probability over exhaustive review; tripwire: an escaped defect found by the random slice in two consecutive weeks.
**Cost:** a deletion: role-file lines and one counter; saves Auditor tokens weekly; removes process.

### R08: review finds defects but cannot get them fixed. AGREE

Verified: the fake-close prescreen defect is still `proposed` 20 h on, and the Arbiter's `_why` says "verdicts
advisory: blocks nothing".
**Remedy: FIX by priority, not by new authority.** Defects in acceptance machinery (prescreen, close gate, verify,
steward) get `raise` (first in `rimflow next`) on filing; the existing prescreen ticket is raised now. Who may block a
close is D1. No new reviewer role.
**Cost:** one raise and one line in auditor.md; 0 tokens/day.

### R09: the owner is still the exception processor. AGREE in direction; partly by his design

Thirty items wait on the owner. Some of that is his chosen control (north-star bars, outward acts, delegation
policy §2), which this response does not try to remove. What is fixable is that nothing ages: an owner ask can sit
for days with no blocking cost shown.
**Remedy: FIX the visibility, mechanically.** The delegated digest (no AI) lists each open OWNER item with age, what
it blocks (count of items whose chain waits on it) and the recommended default. (T11) A default-on-timeout is his
call: D4.
**Cost:** ~40 lines in `delegated_digest.py`; 0 tokens/day; may reduce Conductor relay runs.

### R10: resource caps are partly fictional. AGREE on the token half; the helper half is fixed

Helper limits were unified today. Token "caps" are admission checks: the Arbiter ran ~1.02M on a 500k cap. The
steward already launches its headless session with `--max-budget-usd`; role runs do not.
**Remedy: FIX cheaply.** `role_launch` passes a hard stop at **2x** the run allowance (converted to the CLI's budget
flag) so an overshoot ends the run instead of doubling it again; the docs call the number an "allowance".
(T10) ACCEPT the rest (no global atomic reservation): with one autonomous builder and helpers unified, the
reservation system GPT designs would be process for its own sake. Tripwire: two runs in 7 days hit the hard stop.
**Cost:** ~20 lines; reduces worst-case spend.

### R11: supervision perpetuates itself. AGREE, and the live number is worse

The 24 h process-only share is 96.4% (502 of 521 commits). GPT calls causation unproven; fair, but the target is a
ruling and the system is far over it. Every FIX in this response is small and most remove something; the larger
lever is to stop adding process while the P0 list lands.
**Remedy: RETIRE, by rule.** While the 7-day share is above 61%, a new process ticket needs to name the process it
replaces or deletes, except P0 safety fixes from this list (decision D5, ticket T16). Retire candidates: Innovator
to one slot a week (T17), `v3_vs_v2` stays off and its role in the kill test moves to the health check (in flight),
lessons queue (T7), the twin model deferred (D5).
**Cost:** negative.

### R12: success and kill criteria cannot govern. AGREE

`v3_vs_v2` is disabled; keep-going and accepted-output are unmeasured. The in-flight V3_HEALTH item (owner-message
tagging, planted faults, output tracing) is the measurement plan; T1/T3 make "accepted" countable.
**Remedy: ACCEPT the in-flight plan, with one change: a date.** The keep/kill reading happens on a fixed date with
missing primaries counted as **not shown** (against v3), so missing data cannot defer the decision. Which date is
the owner's (D6).

### R13: tests run on the wrong work. AGREE; in flight (TESTLANE_PLAN_WIRE_PRODUCER_PICKS_UNHEARD)

Add the readback to its Done-when (see §1). No new ticket.

### R14: grant expiry wastes builder attempts. AGREE

Four overnight bounces. `rimflow next` should not offer a `needs bridge` item when the grant has less than its
minimum (45 min) left; it offers the next offline item instead, and one line says why. Never auto-renew (his
consent). (T13) L0: a next-selftest with an expiring grant fixture. **Cost:** ~30 lines; saves bounced runs.

### R15: configuration split across versions. AGREE

New evidence: `operations.md` still says "written, NOT enabled" while the schedule enables it. The helper and
FlowWorks halves are fixed or in flight.
**Remedy: RETIRE the duplicate.** Role headers stop stating enabled/disabled, times or caps; they point at
`dispatcher_schedule.json`, the one source. (T14) Plus T9: required schedule keys fail closed instead of silently
taking the 3/30/80/3 defaults GPT flags in §5. L0: a lint that a role file containing "enabled" or a clock time
fails selftest; schedule load with a missing key refuses.
**Cost:** a deletion plus ~30 lines; removes doc-sync work forever.

### R16: duties vanish in outages. AGREE for mandatory duties only

Slot lateness 1 h with no catch-up is right for snapshots (a stale 07:30 digest is worthless at 11:00) and wrong for
owed duties (Auditor pass, Operations morning check). **FIX:** a missed slot of a role marked `owed: true` writes a
carry-over that the next eligible tick runs, once; snapshot slots keep dropping. (T8) L0: role_launch selftest with
a 3 h outage. **Cost:** ~50 lines; tokens only on recovery.

### R17: restart duplicates or strands work. AGREE it is unproven; ACCEPT while it stays dry

`seat_restart` runs `dry: true`. GPT itself says leaving it off is defensible. Tripwire: before anyone sets it live,
the three interruption cases GPT lists (local edits, pending remote job, held lock) pass as selftests.

### R18: git, evidence and state publication diverge. PARTLY AGREE; ACCEPT with tripwire

Publish errors exist (18 on day one) but `./publish` retries and the ledger is append-only per seat, so divergence
heals on the next publish. Tripwire: a ledger event that exists locally > 1 h without reaching origin (ops_watch can
count it), or a consumer acting on an unpublished state.

### R19: reviewers share the maker's blind spots. AGREE in principle; ACCEPT for now

The Arbiter's binding rule "1 week / 30 verdicts" is weak, as GPT's binomial point shows. It is folded into D1. The
interim GPT reviewer is a different model family, which is real independence of judgment, if not of evidence.

### R20: maintenance automation could widen an outage. ACCEPT with tripwire

Scratch reaping and timer guards are narrow programs. Tripwire: any reap or timer action that touches an item's
cited evidence path, or a second all-timers stop.

## 3. Section 3 and section 5 items that matter

GPT's §3 tables and its §5 list of about 120 parameters are mostly correct as observations. Most need no action:
a number that is provisional but harmless stays as it is. Only the items below change the plan.

| GPT item | Verdict | Disposition |
|---|---|---|
| §3.3 "Commit SHA present: any commit, including ledger-only" | AGREE | T1 (explicit sha, cited-path check). |
| §3.3 "Low process share: reclassify, squash, add product commits" | AGREE, a Goodhart risk for T16 | Tripwire: ops_watch counts the product/process split by **paths touched**, not by commit message, and a week where the share falls with no rise in product paths changed is flagged. Folded into T16. |
| §3.4 "Stronger test is an end-to-end transaction to the consumer" | AGREE | This is V3_HEALTH's planted faults (in flight). Sequence it **after** P0: a planted fault today would land on BENCH and rot, which proves only R04 again. |
| §3.4 "Interim reviewer: invocation optional, absence invisible" | AGREE | D1. |
| §3.5 "Hard flags displace random sampling" | AGREE | The Auditor's 1-in-5 random slice runs **first** in each pass, before mandatory work, so the unbiased sample is never the part that gets cut. One line in auditor.md, folded into T7. |
| §3.5 single points (one PC, FOUNDRY, Dispatcher, ops_watch) | AGREE, ACCEPT | Hobby scale and one machine. T5/T6 remove the worst: ops_watch as a universal gate, and the Dispatcher as the dead-man's only delivery path. Tripwire in R05. |
| §5 "Defaults 3/30/80/3 silently change policy" | AGREE | T9. |
| §5 "Alarm repeat 21600 s hides worsening" | AGREE | T12. |
| §5 "Run-now TTL 3600 s: a request may expire silently" | AGREE | Folded into T8: an expired run-now or a missed owed slot writes one acknowledged-miss line in the Operations brief. |
| §5 "Doorbell 23 h expiry without demonstrated rearm" | PARTLY. The Dispatcher already alarms when no doorbell is armed (dispatcher l. 562-565) | ACCEPT. T15 adds the expiry-then-rearm case to its proofs. |
| §5 "Local-midnight accounting ... the coming daylight-saving transition" | AGREE, and it has a date | **T18, before Sun 2026-11-01 01:00 PDT.** The host is on PDT, 01:00-02:00 repeats that night, and testq-sweep runs at 01:30 local. Prove with a faked clock that the daily caps, the slot lateness and the sweep each run once and attribute to the right day. If the proof cannot land in time, the cheap containment is to move the sweep to 03:30 for that one night. |
| §5 "Future tolerance 300 s vs helper 5 s" | Overstated | ACCEPT. The 300 s tolerates ops status written across the WSL/Windows boundary; the 5 s guards local helper files. Tripwire: a measured clock skew above 5 s between the two (ops_watch can read both clocks). |
| §5 "Arbiter binding after 1 week / 30 verdicts is weak" | AGREE | D1. |
| §5 "Lessons 40 weekly; inbox <= 14 days" incompatible with intake | AGREE, worse (626 a week) | T7. |
| §5 "Innovator three runs weekly; one observed proposal" | AGREE | T17 (one slot a week). |
| §5 "Producer one event a day; shared signals displace each other" | AGREE | In flight (PRODUCER_CADENCE). This response recommends that item build **carry-over of an unsatisfied request**, not a third clock slot (D5). |
| §5 "Daily 06:30 model ... none of these values establishes useful prediction" | AGREE | OPS_MODEL (ready) is deferred until P0 lands (D5). |
| §5 "DRY after 2 unmeasured runs; retry after 3 days" | AGREE | Add to TESTLANE_PLAN's Done-when: an UNMEASURED result is an owned gap with a named receiver, not a 3-day silence. No new ticket. |
| §5 "Nothing-tests > 18 h: flag only" | AGREE | In flight (the dead-colony item splits invalid from valid-green). |
| §5 "Disk thresholds absolute, not growth-rate" | AGREE in principle | ACCEPT. Tripwire: if daily growth on the scratch disk exceeds 50 GB for 3 days, ops_watch adds time-to-full. |
| §5 allocator modes (BURN, CRUISE, account switch) | Overstated as risk | ACCEPT. `account_pick` is recommend-only; nothing acts on it. Tripwire: the day any mode becomes a control, it needs the forecast-error measurement GPT asks for. |
| §5 restart parameters (fence, grace, SIGKILL) | AGREE they are unproven | ACCEPT while `seat_restart` is dry (R17). |
| §5 "Missing primaries must not postpone the decision indefinitely" | AGREE | D6 (a fixed reading date). |

## 4. Priority order

The order follows one rule: **first make failures reach someone, then make "done" mean done, then cut process.**
Nothing else on the list can be trusted while alarms land on a seat nobody rings and a close can skip its criteria.

**P0, this week (in this order):**
1. T18 DST proof. It is first only because of its date: it must land before Sun 2026-11-01 01:00 PDT.
2. T2 alarm routing off BENCH, including the six stranded items.
3. T4 steward ends an incident on green, and the claim pause is capped.
4. T1 close refuses owed criteria and an implicit HEAD.
5. T3 a current fail demotes `validated`.
6. `AUDITPRESCREEN_FIX_WAVED_THE_FAKE_THROUGH` (existing, raised) and `FINDINGS_FOLD_BUILD_QUARRY_SAID_IT_23X` (existing, raised, plus the build-scope rule).
7. T5 Operations launches degraded on a stale watch; T6 the dead-man reaches the phone with no AI.
8. T7 retire the lessons queue; T16 the process-share rule (subject to D3 and D5).

**P1, next week:** T8 duty carry-over, T9 schedule keys fail closed, T10 hard stop at 2x, T11 owner asks aged in
the digest, T12 alarm repeat breaks on worse, T13 grant preflight, T14 role headers stop restating the schedule,
T15 Dispatcher proofs, T17 Innovator to one slot a week.

**P2, after P0 is green for 7 days:** V3_HEALTH planted faults (in flight), the restart exercise (R17, before
anyone sets it live), publish divergence (R18 tripwire), reviewer calibration (inside D1).

**Size:** P0 is 9 new tickets plus 2 raises, roughly 450 lines of code and tests; P1 is 9 tickets, roughly 300
lines. Three of the 18 tickets are pure deletions (T7, T14, T17) and none adds a scheduled AI run. Net steady-state
tokens go **down**: fewer repeat steward and alarm runs, a capped worst-case run, two fewer Innovator runs a week,
and less Auditor fold work.

**The tension with "maximum priority":** filing all 18 at maximum priority puts about 18 process tickets in front
of product work when the process share is already 96% for the day. This response suggests P0 at maximum priority and
P1 at normal priority behind it. That is D5.

## 5. Draft ticket list (not filed)

All 18 names passed `rimflow namecheck` (2026-10-29). Seat is FOUNDRY for all: they are code or config in the
bench-owned workflow, and FOUNDRY is the rung builder. T16's freeze rule is enforced in code, but the Producer
applies it in triage if D5 is approved. Parent for all: `V3_WORKFLOW_AUDIT_EVERY_CLOCK_AND_DOOR`.

| T | Order | Name | Seat | Done when |
|---|---|---|---|---|
| T18 | P0-1 | `CLOCKS_PROVE_DST_FALLBACK_NOV_FIRST` | FOUNDRY | A faked-clock selftest over 2026-11-01 00:00-03:00 PDT shows each role slot, daily cap and testq-sweep runs exactly once and is counted to the right local day, or the sweep is moved for that night with the reason in the schedule. Lands before 11-01 01:00 PDT. |
| T2 | P0-2 | `ALARMS_REWIRE_OFF_RETIRED_BENCH` | FOUNDRY | ops_watch, deadman and steward alarms file for a rung seat; a RUNNER spawn for BENCH is refused without `--why`; Operations' alarm trigger reads open OPS_* ledger items; the six stranded BENCH alarms are reassigned; selftest per producer. |
| T4 | P0-3 | `STEWARD_FIX_ENDS_ON_GREEN_NOT_RUNNING` | FOUNDRY | A steward incident closes only on a DONE job with the canary on after the incident's start (`lane_proven_after`); the claim pause is capped at 2 h per incident; the impact clock never pauses; selftest RUNNING-then-INVALID keeps it open. |
| T1 | P0-4 | `CLOSE_ENFORCE_NO_OWED_NO_IMPLICIT_HEAD` | FOUNDRY | `close` refuses owed criteria and a missing `--sha` (or `--no-code "<what>"`); a sha that touches none of the cited paths needs `--why`; selftests for each refusal and for a clean close. |
| T3 | P0-5 | `VALIDATED_FIX_DEMOTE_ON_CURRENT_FAIL` | FOUNDRY | A fail verify against the current `built_sha` demotes `validated` to `built` and re-owes the criterion; a pass on a stale `built_sha` does not count; selftest_model cases; a one-off replay lists the items this would demote today (expect about 12). |
| T5 | P0-7 | `OPERATIONS_FIX_RUNS_BLIND_WHEN_STALE` | FOUNDRY | With a stale or unreadable status.json, role_launch starts Operations in degraded mode (reading marked UNMEASURED, brief "diagnose the watch first") and still refuses the other roles; selftest. |
| T6 | P0-7 | `DEADMAN_WIRE_PHONE_WITHOUT_AI` | FOUNDRY | A dead-man finding (Dispatcher, ops_watch or timer stale) writes a line to the owner's phone brief through the no-AI pulse path as well as the ledger; selftest asserts the line; one live drill by stopping ops_watch for its limit. |
| T7 | P0-8 | `LESSONS_RETIRE_INBOX_AS_QUEUE` | FOUNDRY | No role file, KPI or Auditor duty treats the lessons count or age as owed work; the 40/week fold quota and 14-day inbox rule are deleted; recurrence promotion goes through the findings fold; the Auditor's random slice runs first. Subject to D3. |
| T16 | P0-8 | `PROCESS_WORK_SHRINK_TO_SIXTY_ONE` | FOUNDRY (Producer applies) | While the 7-day process share is above 61%, `rimflow file` of a process ticket needs `--replaces <item or path>` or a P0 tag; ops_watch classifies by paths touched; the Producer's triage line reports the share. Subject to D5. |
| T8 | P1 | `ROLE_DUTIES_FIX_CARRY_MISSED_SLOTS` | FOUNDRY | A role slot marked `owed: true` that misses its window runs once on the next eligible tick; snapshot slots still drop; an expired run-now or dropped owed slot writes one acknowledged-miss line; selftest with a 3 h outage. |
| T9 | P1 | `SCHEDULE_HARDEN_FAIL_CLOSED_NO_DEFAULTS` | FOUNDRY | Loading `dispatcher_schedule.json` with a required key missing refuses (no 3/30/80/3 fallback); the list of required keys lives in one place; selftest. |
| T10 | P1 | `ROLE_RUNS_ENFORCE_STOP_AT_TWICE_CAP` | FOUNDRY | Every role launch passes a hard budget stop at 2x its run allowance; docs say "allowance"; a selftest asserts the flag on each role's command line. |
| T11 | P1 | `OWNER_ASKS_MEASURE_AGE_IN_DIGEST` | FOUNDRY | The delegated digest (no AI) lists each open OWNER item with age, the number of items waiting on it and the recommended default; selftest on a fixture ledger. |
| T12 | P1 | `ALARM_REPEAT_FIX_BREAK_ON_WORSE` | FOUNDRY | A repeat alarm of the same kind inside the 6 h window is re-raised when its severity rises or its impact metric crosses the rule's stated step; selftest. |
| T13 | P1 | `BRIDGE_ITEMS_ENFORCE_GRANT_PREFLIGHT` | FOUNDRY | `rimflow next` skips a `needs bridge` item when the grant has under 45 min left and says why in one line; it never renews; selftest with an expiring grant fixture. |
| T14 | P1 | `ROLE_HEADERS_RETIRE_ENABLED_PROSE` | FOUNDRY | No `rimflow/roles/*.md` states enabled/disabled, a clock time or a cap; each points at `dispatcher_schedule.json`; a selftest lint fails on a role file that does. |
| T15 | P1 | `DISPATCHER_PROVE_BLOCKED_TOP_AND_CURSOR` | FOUNDRY | Selftests show that a blocked top item does not hide a lower offline item from the Dispatcher, that the event cursor survives a 7 h outage without dropping unread events, and that an expired doorbell is re-armed or alarmed within one tick. |
| T17 | P1 | `INNOVATOR_RETIRE_TWO_WEEKLY_SLOTS` | FOUNDRY | The Innovator has one scheduled slot a week in `dispatcher_schedule.json`; its budget per run is unchanged; tripwire: a proposal the owner marks urgent waits more than 7 days for its slot. Subject to D5. |

Plus two **raises** on existing items, no new tickets: `AUDITPRESCREEN_FIX_WAVED_THE_FAKE_THROUGH` and
`FINDINGS_FOLD_BUILD_QUARRY_SAID_IT_23X` (add: a standing failure is retired only on passes of the same build,
scenario and environment). Two **Done-when additions** to existing items: TESTLANE_PLAN (readback; UNMEASURED is an
owned gap) and PRODUCER_CADENCE (carry-over, not more slots).

## 6. Owner decisions

Six calls, each one his under `delegation_policy.md` §2 or a real trade-off between his own stated priorities.
Everything else in this response is within delegation and can be ticketed as written.

**D1. Who may block a close? (§2 #4: it overturns the standing "Arbiter verdicts are advisory" ruling)**
- (a) Keep the Arbiter advisory; T1/T3 make the *mechanical* gate honest, and that is all. Cheapest; a maker can
  still close work that no one else looked at.
- (b) An Arbiter **FAIL** blocks the close until a new build passes or the owner overrides; no verdict blocks
  nothing. Small cost (one check in `close`); stops the "review found it, nobody fixed it" loop for known defects.
- (c) Fully binding: every close of L2+ work needs a non-maker review record. Strongest; it puts the Arbiter's
  twice-daily slots on the critical path of every close, which slows throughput by up to a day.
- **Recommend (b)**, plus calibration on false *accepts* (the Auditor's random slice), not on verdict count.

**D2. Who receives and repairs alarms now that BENCH is retired?**
- (a) FOUNDRY receives every alarm as a normal item. Simple; costs builder time, and the builder repairs its own
  supervision.
- (b) Operations gets repair authority for alarms (it may edit and commit inside the ops paths). Keeps FOUNDRY on
  product; gives an AI role write access it does not have today.
- (c) Containment first by machine (pause the lane, restart the game, re-ring), then FOUNDRY for the residue.
- **Recommend (c)**, which T2 and T4 already build toward; (b) only if the residue is still large after two weeks.

**D3. The lessons queue (§2 #4: the fold duty is a standing practice in his role files)**
- (a) Retire it as a queue (T7): keep the files as a searchable corpus, promote a lesson only when it recurs, and
  stop counting the backlog.
- (b) Fund a real weekly fold: about 600 lessons a week means a dedicated role run of several hours, all process.
- (c) Retire it, and also archive the existing ~1,100 files out of the tree.
- **Recommend (a).** (c) loses grep hits for no gain; (b) is the opposite of the 61% target.

**D4. Owner asks that age (§2 #4/#6: a default would act in his name)**
- (a) Visibility only (T11): the digest shows each ask's age and what it blocks. He still decides everything.
- (b) Visibility, plus a stated default that applies after N days unless he objects, **only** for asks the
  delegation policy does not reserve to him.
- (c) No change.
- **Recommend (a) now**, and revisit (b) after two weeks of age data.

**D5. "Maximum priority" against the 61% process target (his two stated priorities conflict)**
- (a) File all 18 at maximum priority as he said. Fast on safety; product work stalls for about two weeks and the
  share stays near 90%.
- (b) P0 (9 tickets + 2 raises) at maximum; P1 at normal priority behind it; a process freeze (T16) while the share
  is above 61%; defer OPS_MODEL; PRODUCER_CADENCE as carry-over; the Innovator to one slot a week.
- (c) As (b), but without the freeze rule: rely on judgment.
- **Recommend (b).** It honours "maximum priority" for the items that fix real failure paths and still moves the
  share toward his target.

**D6. When v3 is judged keep or kill (§2 #1: a north-star bar)**
- (a) A fixed reading date, for example 2026-11-19 (three weeks after P0), with any missing primary counted as
  "not shown" against v3.
- (b) Read it when the data is complete (the current design). Defensible, but missing inputs can postpone the
  decision forever, as GPT notes.
- (c) No formal reading; he judges by feel.
- **Recommend (a)**, with the date his.
