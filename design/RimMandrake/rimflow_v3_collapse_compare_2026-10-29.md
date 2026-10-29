# RimFlow v3 collapse: two blind minimal designs compared, 2026-10-29

Item: `RIMFLOW_V3_SHRINK_FEWER_CHAIRS_SAME_JOBS` (needs owner). DESIGN COMPARISON ONLY: no code, role file or item
was changed.

**What this is.** You asked for fewer parts without losing any function. Two models answered the same brief
(`D:\ClaudeWork\rimmandrake\v3_collapse\brief.md`), each without seeing the other:

- **Opus** could read the code. Its answer is saved verbatim at
  `D:\Luke\dev\RimMandrake\design\RimMandrake\rimflow_v3_minimal_opus_2026-10-29.md`.
- **GPT** had the design documents only. Its answer is saved verbatim at
  `D:\Luke\dev\RimMandrake\design\RimMandrake\rimflow_v3_minimal_gpt_2026-10-29.md`.

This page sets them side by side, checks what they say about today's code against the code, and proposes one design
to freeze. Code checks were made on the bench clone at `efb3330455`.

**The short version.**
- Both designs land in the same place on the thing that matters most: **the rules move out of role prose and into
  programs**. `close` refuses a dishonest done, `next` refuses to go wide, and a program, not the maker, sends every
  finished piece to GPT.
- Both cut the five scheduled managers (Producer, Operations, Innovator, Arbiter, Auditor) down to at most two.
- They differ mainly on **how far to go**. Opus keeps today's programs and adds gates to them. GPT merges everything
  AI into one Operator and rewrites the plumbing into one Controller service.
- My recommendation is Opus's shape (4 AI actors, today's programs plus gates), with three of GPT's ideas adopted:
  - a much tighter focus limit (one item, plus one only while it is blocked);
  - acceptance criteria frozen **before** building starts;
  - a watcher on SteveDesktop that notices if the main PC dies.

---

## 1. Who does what: the two rosters, function by function

The function list merges both inventories. Opus listed 32 functions, GPT 60. Rows where both say the same thing are
combined.

**Opus's roster:**
- Conductor: your conversation, only while you are present.
- FOUNDRY: the builder.
- Planner: Producer + Operations + Innovator, once a day plus events.
- Judge: Arbiter + Auditor, a Claude model that samples GPT's verdicts once a day.
- GPT: the blind reviewer of every close and, weekly, of the whole system.
- Programs: Dispatcher, ops_watch, testq, rimflow.

**GPT's roster:**
- Operator: Conductor + Producer + Operations + Innovator + FOUNDRY. It can run up to three contexts at once:
  conversation, work and judgment.
- GPT Judge: Arbiter + Auditor + the interim reviewer.
- Programs: a single **Controller** service on the main PC, and a **Steve worker** service on SteveDesktop.

| # | Function | Today | Opus design | GPT design |
|---|---|---|---|---|
| 1 | Talk with you while you are present; record rulings | Conductor (BENCH) | Conductor, session only | Operator, in a foreground context |
| 2 | Tell you things while you are away (brief, digest, urgent) | pulse timers plus Conductor checks at 08:00 and 20:00 | pulse digest (no AI), now listing your open asks with age and what each blocks | Controller briefs; your decisions are held as records with age and blocked cost |
| 3 | Make the weekly and daily plan; cut list | Producer | Planner, 07:30 daily | Operator, in the 09:00 daily bundle |
| 4 | Track the day against the plan; replan | Producer cadence (designed) | ops_watch detects a slip and starts a Planner event run (at most 2 a day) | Controller checks at 12:00 and 18:00 and wakes the Operator only on a real deviation |
| 5 | Limit unfinished work (current focus) | Producer's "WIP cap" text, which **no code reads** | `rimflow next`: 3 focus items, plus up to 2 waiting | Controller: 1 item, plus 1 more only while the first is blocked; never a third |
| 6 | Write acceptance criteria | maker, at `implemented` (after the build) | as today | frozen **before** the build; any revision is a visible event |
| 7 | Build | FOUNDRY | FOUNDRY | Operator |
| 8 | Test until it passes, then fix | FOUNDRY, by habit | FOUNDRY; enforced because `close` refuses | Operator; enforced because the Controller refuses |
| 9 | Blind review of every finished component | maker-invoked GPT ritual; advisory Arbiter | `review_gate` program called by `close`, which sends GPT the sha, criteria and evidence | Controller requests GPT Judge |
| 10 | Re-check the judges; calibrate | Auditor | Claude Judge, 13:00 daily: samples GPT's PASSes, re-runs evidence, re-opens defects | GPT Judge re-checks in a fresh context that does not see the earlier verdict |
| 11 | Get review defects fixed | nobody | the defect re-opens the same item into focus | the rejection returns to the same focus |
| 12 | Whole-system GPT review | nobody | weekly, plus on any change to a gate, the roster or the alarm routes | on every integrated release |
| 13 | Wake an idle builder | Dispatcher doorbell | Dispatcher, as today | Controller dispatch; the doorbell is deleted |
| 14 | Fresh context and dead-seat recovery | seat_restart (live); recover_dead OFF | keep seat_restart; recover_dead stays OFF | delete seat lifecycles; work runs as bounded jobs with checkpoints |
| 15 | Run game tests on SteveDesktop | testq | testq | Controller (queue) plus the Steve worker (runs) |
| 16 | Keep test evidence valid (steward, canary) | steward; RUNNING ends an incident | an incident ends only on a DONE job with a fresh green canary | the same, plus a stated recovery check |
| 17 | Choose what Steve tests | Producer → Conductor → (lost) | Planner writes testq's config; testq reads it back. Focus first, then recent regressions | a versioned allocation the worker acknowledges; coverage-based; Steve may sit idle |
| 18 | Turn results into item state | ingest → verify | the same, plus a fail demotes | the same, plus a later failure removes the green status |
| 19 | Fold findings | findings_fold.py (built) | inside the testq tick | Controller, straight after ingest |
| 20 | Measure machine, accounts, burn | ops_watch | ops_watch | Controller |
| 21 | Route alarms to someone who is woken | all routes go to BENCH, which nothing wakes | one routing table: containment, a FOUNDRY P0, a Planner event, or your phone | every obligation has an owner, deadline and escalation; a claim does not stop the clock |
| 22 | Watch the watchers | deadman (which files to BENCH) | deadman → phone brief, with no AI in the path | the Steve worker watches the main PC and notifies you directly |
| 23 | Lessons into skills and memory | Auditor fold (2 of 626) | Judge weekly; promote only lessons that recur | Judge weekly; promote novel severe lessons at once and recurring ones as rules |
| 24 | Propose improvements | Innovator | Planner weekly, plus the GPT system review | Operator, in the weekly pass |
| 25 | v3 against v2; daily health; process model | designed or OFF | ops_watch families; process model OFF | modules in the daily bundle; the fit OFF until its inputs can be trusted |
| 26 | Spend and helper caps | role_launch, helper_budget | as today, plus a hard stop at 2x allowance | one capacity reservation; helpers OFF at first |
| 27 | Live-game grant, owner presence, bridge lock | partly manual | as today (grant check not addressed) | checked at admission **and** at the action |
| 28 | One config truth; PAUSE | schedule plus role prose that drifts | schedule only, with a lint test | one policy document, with scoped and expiring overrides |
| 29 | Publish and mirror | timers | as today | acknowledged delivery jobs; git is never the work-queue transport |

---

## 2. Agreements: the candidate to lock in

Both designs propose all of the following. Each was reached independently.

1. **A program enforces done, not a role.**
   - Done needs an explicit sha, never an implicit HEAD.
   - Every criterion must pass against **that** build.
   - A later failure takes away the green status.
   - No-code work must name its deliverable.
2. **A program, not the maker, sends every finished component to GPT.** GPT sees the artifact, the criteria and the
   raw evidence. It does not see the maker's own story. Cost pressure never lowers the bar: a review may wait, but it
   is never skipped.
3. **A rejection goes back into the same item, which stays in focus.** It does not become a new ticket at the back of
   the queue.
4. **Current focus is enforced by a program.** The next step on a fresh build (test, fix, review) always outranks new
   work.
5. **Arbiter and Auditor merge into one judging role** (your original idea). Both designs drop the separate per-close
   Arbiter batch.
6. **Producer, Operations and Innovator stop being three scheduled roles.** Planning becomes cost-aware. Innovation
   becomes a weekly question, not a role.
7. **The Conductor's scheduled runs go.** Your conversation stays light. Reporting while you are away comes from a
   program that lists your open asks with their age and what each one blocks.
8. **Replanning is triggered by events, not clock slots.** A cheap program check wakes the planner only on a real slip
   or a dry queue. An owed run is never silently dropped.
9. **SteveDesktop's time must buy valid evidence.**
   - An incident ends on a proven recovery, never on RUNNING.
   - The first red canary contains the lane. There is no free automatic retry.
   - Test time goes to the focus item first. Filling idle CPU is no longer a goal.
   - Your choice of mods actually reaches testq, which confirms it back.
10. **Stale monitoring must not block the recovery from it.** A blind reading starts a recovery run. It no longer
    refuses every role.
11. **Every alarm and finding lands on an owner that is actually woken.** BENCH, which nothing wakes, stops receiving
    automated work.
12. **Configuration has one source.** Numbers and slots live only in config; role files stop restating them.
13. **The lessons fold stops being a quota.** Lesson files stay as a searchable library, and the judge promotes the
    ones that matter.
14. **Keep OFF, and keep the depth-first migration** (see §5). Acceptance machinery goes first, and each step is
    proven before the next starts.

### Claims about today's code, checked

**Opus's probes (it read the code at an earlier HEAD, `c2dfc21445`).** All of them still hold at `efb3330455`, with
three corrections.

Confirmed:
- `close` takes an implicit HEAD and only warns about owed criteria (`src/RimMandrake/rimflow/cli.py`, `cmd_close`).
- A fail never demotes, and a pass is not tied to `built_sha` (`model.py` `_verify_target` / `_criterion_passed`).
- Every ops_watch alarm goes `"for": "BENCH"`, and BENCH is `wake: false`.
- The steward's RUNNING state ends an incident, and its escalations spawn `--for BENCH` (`testq/steward.py:17,473`).
- A stale ops_watch refuses **every** role launch, with no exemption for Operations (`role_launch.py:54`).
- No code reads "WIP cap".
- `gpt_consult` is called only from `arbiter_tiers.py`.
- `findings_fold.py` and `audit_hardflag_file.py` exist.
- The throttle bands are all neutral (×1.0, all slots).
- `seat_restart` is live.
- The ledger counts match: FOUNDRY has 82 `doing`, 343 `built` and 172 `validated`.
  `AUDITPRESCREEN_FIX_WAVED_THE_FAKE_THROUGH` is still `proposed`.

Corrections:
- **Stale.** `PRODUCER_CADENCE_DESIGN_MORE_THAN_WEDNESDAYS` is now `dropped`, not `doing`.
- **Partly wrong.** Opus says the steward fix was "never filed". Two routing items do exist, both `proposed`:
  - `STEWARD_ESCALATION_REWIRE_TO_ENGINE` (FOUNDRY);
  - `TESTQSTEWARD_FIX_ESCALATES_TO_A_GHOST` (BENCH).

  The RUNNING-ends-incident fix itself is not filed.
- **Overstated.** "597 started and not finished" counts every `built` and `validated` item. Most of those are waiting
  on owed live criteria, not being worked on. The number is real, but it is a backlog of unproven work, not 597 things
  in someone's hands.

**A hole both designs miss.** The last passing `verify` makes an item `done` by itself, with no `close` and no review
(`model.py` `_criterion_passed`, where the last outstanding criterion goes straight to `done`). So a gate placed only
on `close` can be walked around. The done gate must sit in the model's transition to `done`, not only in the `close`
verb.

**GPT's claims (it had documents only).** Three are wrong about today:
- **Wrong.** "Findings fold: planned, not operating." It is built (`src/RimMandrake/Utils/findings_fold.py`).
- **Wrong.** "Hard-flag filer: proposed." It is built (`src/RimMandrake/rimflow/audit_hardflag_file.py`).
- **Wrong.** "The later response says seat_restart is dry." It is live: `seat_restart.dry` is `false` in
  `dispatcher_schedule.json`.

Confirmed:
- "One red canary retries by design" is right. The first red canary auto-resumes once, and the second pauses the lane
  (testq selftest).
- The doorbell works today (53da033d1b). GPT proposes deleting it because it did not know that.

---

## 3. Disagreements: six real decisions

**D1. Should the planner be a separate AI from the builder?**
- **Opus:** a separate headless Planner (one run a day plus events), with FOUNDRY building only.
- **GPT:** one Operator that plans, operates, innovates, builds and talks with you, with the Controller enforcing the
  limits.
- **Trade-off.** GPT has one fewer role. But the builder would then choose its own focus and its own priorities, and
  a program can count focus items without being able to judge which ones should be in focus. One headless planning
  run a day is cheap.
- **Recommend Opus.** The maker should not pick its own work as well as do it, and the extra role costs one run a
  day.

**D2. Is there a Claude judge as well as GPT?**
- **Opus:** GPT reviews every close. A Claude Judge samples GPT's PASSes (about 1 in 3, plus every hard flag),
  re-runs evidence and re-opens defects.
- **GPT:** GPT is the only judge. Re-checks are run by GPT in a fresh context. GPT itself says shared blind spots
  "remain a real risk".
- **Trade-off.** Opus's design checks one model with a different one, at about 700k tokens a day. GPT's is cheaper,
  but its re-checks share GPT's blind spots.
- **Recommend Opus, made cheaper.** Keep the Claude Judge as a sampler that runs only on days with new closes. A
  different model is the only check that does not share GPT's blind spots.

**D3. How many items may be in focus?**
- **Opus:** 3 focus items, plus up to 2 waiting.
- **GPT:** 1 item, plus 1 more only while the first is genuinely blocked and has no useful next action; never a
  third. A builder left idle is an explicit, accepted cost.
- **Trade-off.** Opus's limit keeps FOUNDRY busy through long Steve jobs. GPT's is closer to what you asked for
  ("depth before breadth") and makes stalls visible rather than hiding them in breadth. Today FOUNDRY has 82 items
  `doing`.
- **Recommend GPT's 1+1, as a config number.** Raise it only if the "idle with focus blocked" count proves it costs
  more than it saves. A tight limit is easy to loosen on evidence; a loose one is never tightened.

**D4. Add gates to today's programs, or rewrite them into one Controller?**
- **Opus:** keep the Dispatcher, ops_watch, testq and rimflow, and add the gates and the routing table to them.
- **GPT:**
  - a single Controller service with a transactional work store;
  - git is no longer the work-queue transport;
  - delete the doorbell and the seat lifecycle in favour of bounded jobs with checkpoints;
  - a separate Steve worker service.
- **Trade-off.** GPT's version is cleaner on paper. In practice it is a rewrite: every working part (the doorbell,
  testq, ingest, the fold) would have to be proven again from zero. That is breadth, not depth. GPT did not know these
  parts already work.
- **Recommend Opus.** Take one idea from GPT as a later, separate item: queue delivery must not depend on a git push
  succeeding.

**D5. When are acceptance criteria fixed?**
- **Opus:** as today, where the maker declares criteria at `implemented`, after building.
- **GPT:** freeze the criteria when work starts. A bad criterion becomes a visible revision; the maker cannot quietly
  weaken it.
- **Trade-off.** Freezing early costs one step at claim time. Without it, the maker writes the exam after seeing its
  answers.
- **Recommend GPT.** Criteria declared at claim; any later change is a ledger event that the reviewer sees.

**D6. Who notices that the main PC itself has died?**
- **Opus:** the deadman writes to your phone brief with no AI in the path. But the deadman runs on the same PC.
- **GPT:** SteveDesktop watches the main PC and notifies you directly.
- **Trade-off.** Opus's version is nearly free and covers stopped timers. GPT's version also covers a dead machine,
  which is a new small part.
- **Recommend both, in that order.** Use the deadman → phone now. Later add a Steve-side check that alerts when the
  main PC's heartbeat goes quiet, because it is the only alarm that survives a dead machine.

Not counted as disagreements:
- **The GPT-down case.** Opus holds the item as `done:unreviewed` in a focus slot; GPT says reviews may wait but the
  bar never drops. These are the same rule.
- **When the whole-system review runs.** Opus says weekly plus on gate changes; GPT says per release. Take both: run
  it on any change to gates, roster or routes, and weekly otherwise.

---

## 4. Merged invariants (7), each with its forced-failure test

All are run as selftests on a fixture ledger or clock. Live drills are marked.

| # | Invariant | Forced failure | Pass |
|---|---|---|---|
| I1 | **Done is earned.** An item becomes `done` only with an explicit, non-ledger sha (or a named no-code deliverable), every criterion frozen at claim and passed against that sha, a program-requested blind GPT PASS on that sha, and no newer fail. A fail demotes the item. The gate sits in the model's transition to `done`, so `verify` cannot walk around it. | Each of these is attempted: close with owed criteria; close with no sha; close with a ledger-only sha; close with no GPT record; GPT PASS on S but built at S'; a fail after `validated`; the last `verify` pass with no review; a quiet weakening of a criterion; one plausible defective candidate. | Every one is refused or demoted. A good candidate passes. A replay of the real ledger lists today's demotions, and QUARRY appears in it. |
| I2 | **Depth before breadth.** At most 1 focus item, plus 1 only while the focus is blocked with no next action. A rejection or a Judge defect re-opens the same item and ranks first. | Ask for a 2nd item while the focus is workable; then a 3rd while blocked; then deliver a focus failure; then re-open by the Judge. | 2nd refused; 3rd refused; the focus fix ranks first; the re-opened item ranks first. |
| I3 | **Every obligation has a woken owner until its outcome is proven.** That covers alarms, findings, review requests, plan slips and your asks. Nothing is filed for an unwoken seat. A claim does not stop the impact clock. An idle builder with workable focus is rung. | Fire one synthetic alarm of every kind in the routing table. Spawn `--for BENCH` without `--needs owner`. Claim an incident and renew it without progress. Idle FOUNDRY with work. Restore after a 7-hour outage. | Each alarm reaches its routed owner (a new kind with no route fails the test). The spawn is refused. Escalation continues after the claim. A ring arrives within 1 tick. Nothing is lost to a missed slot. |
| I4 | **Test time buys valid evidence, on what is in focus.** An incident ends only on a DONE job with a green canary started after the incident began. The first red canary pauses the lane. Allocation follows the plan and is read back. | The sequence RUNNING → INVALID → RUNNING. One red canary. Mods requested that differ from the old default. A queue holding a focus chain and an older chain. **Live drill:** kill the colony on Steve once. | The incident stays open through RUNNING. The lane pauses on the first red. The applied mods match the plan. The focus chain is admitted first. |
| I5 | **A watcher's failure cannot silence recovery.** A stale ops_watch starts a degraded Planner run marked UNMEASURED. The deadman reaches your phone with no AI and no ledger in the path. Later, Steve alerts on the main PC's silence. | **Live drill:** stop ops_watch past its limit. Delete status.json in a fixture. Later, stop the main PC's heartbeat. | The phone carries the deadman line. The Planner launches degraded; other roles wait. Steve alerts. |
| I6 | **Authority and restarts are safe.** The live-game grant and your presence are checked at admission and again at the action, and an unknown grant blocks. A restarted seat's old attempt cannot change state. A duplicate result is ingested once. | Expire the grant mid-ticket. Come back during live work. Kill FOUNDRY holding local edits and the bridge lock. Ingest the same result twice. | Live work refuses or yields; offline work continues; the grant does not renew silently. The lock is released and the edits recoverable. The result has one effect. |
| I7 | **One truth, and no flattering silence.** Every number and switch lives in the schedule, a missing key refuses to load, and role files restate none of them. Your asks show their age and what they block. A missing metric stays UNMEASURED and can never produce "healthy" or "v3 wins". | Remove a required key. Add "runs at 13:00" to a role file. Create a 5-day-old owner item that blocks 2 items. Remove a v3_vs_v2 input. | The load refuses. The lint fails. The digest shows the age and the blocked count. The verdict reads UNMEASURED. |

Whole-system proof, after all seven pass: a 48-hour unattended run with one planted fault per invariant. You or GPT
choose and log the faults, not the system. Pass means every fault is caught by its own enforcer, without you
discovering it.

---

## 5. What both would delete, and what both would keep OFF

**Delete (both agree):**
- **Roles.** The separate Producer, Operations, Innovator, Arbiter and Auditor launches, schedules, budgets and role
  files, and the Conductor's scheduled quick checks.
- **Review machinery.** The advisory verdict stream, and the maker-invoked GPT ritual (replaced by the
  program-called gate).
- **Steward and test-lane behaviour.**
  - RUNNING counting as recovery.
  - The free automatic retry after a red canary.
  - Oldest-chain filler and sweeps whose only purpose is to keep CPU busy.
- **Routing.** Every automated path that files `--for BENCH`, and the idea of an autonomous BENCH queue.
- **Owed work.** Clock slots that expire owed work; an owed run is run late, never dropped.
- **Monitoring gate.** The rule that a stale ops_watch refuses every launch.
- **Lessons.** The fold quota and the rule that every lesson file is a debt (the files stay).
- **Config.** Numbers and schedules restated in role prose.
- **Timers.** The separate v3_vs_v2 and process-model timers (the work moves into the daily batch).
- **Handoffs.** The REPLAN REQUEST relay and the Producer → Conductor test-mods relay.

**Opus also deletes:**
- the neutral throttle bands;
- the `golive` duplicate roles list;
- `after_role` chaining.

These are dead config, and I agree.

**GPT also deletes:**
- the doorbell and seat restart (I disagree, see D4);
- helper borrow and payback.

**Keep OFF until every invariant has passed its forced failure and the system has run 14 days green (both agree):**
- planted faults;
- the daily process-model fit;
- automatic account switching or holds;
- the Archmagi second lane and extra autonomous helpers;
- innovation trials without a proven expiry and rollback.

Opus adds dead-seat auto-recovery to this list, and GPT adds broad automatic repair actions. Both belong on it.

The v3-against-v2 **measurement** starts now. The **verdict** waits. GPT sets a firm checkpoint 14 days after
acceptance that cannot be moved for missing data, and I recommend adopting it.

---

## 6. Proposed frozen design, and the cost of getting there

**The design.**
- **Four AI actors.**
  - The **Conductor**, only while you are present.
  - **FOUNDRY**, the one autonomous builder.
  - The **Planner** (Producer + Operations + Innovator): once a day at 07:30, plus at most two event runs when
    ops_watch sees a slip, a dry queue or a stuck focus item.
  - The **Judge** (Arbiter + Auditor): a Claude model that samples GPT's verdicts, only on days with new closes.
- **GPT is the binding blind reviewer.** A program sends it every finished component, and it reviews the whole system
  weekly and whenever a gate, the roster or the alarm routes change.
- **Today's programs stay.** These are the Dispatcher, ops_watch, testq and rimflow. Each gains one job:
  - rimflow: the done gate (I1) and the 1+1 focus rule (I2), with criteria frozen at claim;
  - the Dispatcher and ops_watch: a single alarm routing table (I3), plus a degraded Planner launch and a deadman that
    goes to your phone (I5);
  - testq: an honest steward and focus-first allocation (I4).
- **One schedule file is the only config** (I7).
- **Later, a small SteveDesktop heartbeat check** covers a dead main PC.
- **Size.** Two scheduled AI runs a day instead of about 11, ten handoffs instead of about 30, and roughly half
  today's token spend (ESTIMATE, from Opus's day-one figures).

**What it costs to get there.** These are ESTIMATES in FOUNDRY working time, assuming a test-until-pass loop and a
GPT review per step:
- Steps 1-3 are the bulk, about a day each.
- Steps 4 and 7 are about half a day each.
- Steps 5-6 are about a day each.
- Then the 48-hour proof.

That is about 1.5-2 weeks of wall-clock time with nothing else in focus.

**One-time effects.**
- The done gate's replay will demote some items. Opus's source expects about 12.
- The focus rule sends about 80 `doing` items back to `proposed`.
- About 500 `built` and `validated` items become ordinary backlog, which the Planner pulls in oldest first.
- The six stranded alarms and about 28 BENCH `proposed` items must be re-filed to woken owners.

**Build order.** Depth first. Each step is built, tested by its own forced failure until it passes, blind-reviewed by
GPT, fixed, and closed before the next one starts. During the migration, FOUNDRY's focus goes to these steps and to
P0 alarms only.

1. **Done gate (I1).** The gate sits in the model's transition to `done`. It also covers criteria frozen at claim,
   fail demotion, pass tied to the sha, and a `review_gate` that calls `gpt_consult` and writes one record per sha.
   On landing, run the demotion replay. This step comes first because every later "done" depends on it.
2. **Focus rule (I2)** in `rimflow next`: 1+1, re-opened items rank first, and the focus number lives in config.
3. **Alarm routing table (I3).** Re-file the stranded BENCH alarms and items.
4. **Roster flip.** Turn the Planner and Judge on, and turn off the five old roles and the Conductor's quick checks.
   The digest gains its asks, alarms and focus sections. This is a config and role-file change, and it lands only
   once steps 1-3 can gate the new roles' output.
5. **Honest steward and focus-first filler (I4)**, including the live colony-kill drill.
6. **Degraded Planner, deadman to the phone, and the grant and restart safety checks (I5, I6).**
7. **Config lint and fail-closed load (I7).**
8. **First whole-system GPT review, then the 48-hour unattended proof** with faults you or GPT choose. The
   SteveDesktop heartbeat and the git-independent queue delivery are filed as separate later items, each going
   through the same loop.

**What I need from you.** Rulings on D1-D6, or "take the recommendations". After that, the design above is frozen and
step 1 goes to FOUNDRY as the only item in focus.
