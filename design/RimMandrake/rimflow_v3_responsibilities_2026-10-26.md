# RimFlow v3 — responsibilities, metrics, and the north-star checks and balances (2026-10-26)

Status: **DESIGN, companion to `design/RimMandrake/rimflow_v3_2026-10-26.md`** (the design of record). Part 1 is the
review of Lukas's north-star proposal (his to read; under two pages). Part 2 is the responsibilities register with
metrics. Part 3 is the gap check of today's duties against the v3 roles.

Rulings this answers (owner, by card on `RIMFLOW_V3_BUILD_DISPATCHER_FIRST`, 2026-10-26 22:38 PDT):
- Start shape: *"Run it, then right things, then learning (Operations → Producer+Arbiter → Auditor+Innovator)"*.
- Roles and names: *"Confirm as drawn, and I'm very eager to write down the actual responsibilities so we don't miss
  anything / metrics to care about"*.
- Arbiter limits, his proposal for review (verbatim in Part 1).

Value conventions: **MEASURED** values are as of 2026-10-26/27 with the command that reproduced them; **UNMEASURED**
names the instrument that is missing. A metric belongs to exactly one role; other roles may read it.

---

## Part 1. Review of the north-star checks-and-balances proposal

His proposal (2026-10-26 22:38 PDT) is quoted verbatim in `design/RimMandrake/rimflow_v3_2026-10-26.md` §6.

**Who the "Efficiency Agent" is.** The economy duty of Operations, since v3 merged the Economist into Operations.
Keep it there. Operations *never lowers a test bar*, so this duty **proposes** cuts and never enacts one. If the
north-star review and the machine economy pass crowd each other out (one skipped twice running, the v3 §5 trigger),
split the Economist out. The north-star review needs mod knowledge; the machine pass does not.

Scale today (MEASURED, `modcheck floor --all`, 2026-10-26): 5 mods have VALIDATED bars, 117 bars in all
(FlowWorks 75, Pyrelands 20, GimmeSomeSlack 9, Graffiti 8, and FireEcology 5, which floor REFUSES because all 5 are
uncovered). 132 walks are DRAFT.

### What it gets right
1. **The one who sets the bar is not the one who grades it.** That is maker ≠ checker applied to the bar itself,
   and the 10-26 evidence says we need it: a builder lowered its own recall bar from 0.9 to 0.8.
2. **A fail gets a cause.** Asking "was it the script or the module?" turns "flaky" into a ticket on the right side.
3. **Escapes close the loop.** It extends his 10-24 rule (every defect he finds becomes a permanent test) to defects
   anyone finds.
4. **Two pressures pull against each other.** Without one force cutting checks, suites only grow, and so do the test
   hours that catch nothing.

### Where it has holes
1. **Bars and checks are two layers; the proposal treats them as one.** A *bar* is a line of his hash-bound
   `## north star` section — the contract. A *check* is a `validation.py` component that claims bars through `shows=`;
   checks are already agents' work (debug_process §6). **Most escapes need no new bar:** a defect that breaks an
   existing bar needs a new *check* (a regression check), not a contract change. **"Do we NEED this bar?" removes a
   bar**, which lowers it — his. **Merging correlated checks** changes no bar, but `modcheck floor` only proves the
   bars are *claimed*, not that the merged check still *detects* what the old ones did: a merge must show that every
   failure the old checks caught (their recorded reds and the seeded defects of the mod's `mutate_*_fuzz.py`, where
   one exists) still turns the merged check red.
2. **The Arbiter must not be the only one who sees its own checks.** Designing a check is fine. Implementing it and
   then judging, alone, whether a fail was the check's fault is not: the incentive is to protect the check, and a
   weak check passing falsely is invisible to its designer. A builder implements, one independent reviewer reads
   each ordinary check change, and the Auditor reviews **every distinct decision that discards blocking evidence**
   (a FAIL ruled the check's fault, a run restarted as disturbed); identical incidents may be grouped only with
   evidence. Evidence is the preserved artifacts, a reproduction of the false red on behaviour shown correct by
   other means, the corrected check, and a rerun that passes — failing on an "old good build" is not enough, since
   it may share the bug.
3. **There are more outcomes than pass and fail-of-which.** A FAIL is caused by the *module*, the *check*
   (script or harness), the *environment*, or the *bar* (wrong or unreachable → Producer and him), and causes can
   coexist (a harness bug can hide a real defect). Add **UNRESOLVED**: it blocks acceptance, and it is not a pass.
   An environment restart is allowed only when the disturbance is outside what the bar promises (his 10-13 ruling:
   fire, a hurt colonist), with a bounded number of retries and every attempt kept. UNMEASURED and INFERRED are not
   PASS.
4. **Nothing breaks a deadlock.** Efficiency wants fewer checks, the Arbiter more, and the Producer cannot arbitrate
   because it wants the date. A budget frames the argument but does not settle it. The breaker is a **deadline**:
   one round each, then one card to him with both positions and a recommendation. Until he answers, the disputed
   check runs **and counts** (the safe direction). Cost is a measured **resource envelope** per mod (rig-minutes and
   tokens per full run, `testing_metrics.py`, revised monthly): an overrun triggers an optimisation ticket or a
   scope card, and never quietly drops a check.
5. **Which contract changes need him is unsaid.** Today **every** edit to a hashed section needs him (the hash covers
   the prose; only `modcheck validate --owner-said` binds). Delegating all "tightening" would ratchet scope: harmless
   additions pile up into an unaffordable or contradictory contract, and "tighter" can hide changed scope. What can
   be delegated: **regression checks against already-approved bars** (no contract change at all). **New bars** go to
   him, or only inside a scope and cost allowance he grants per mod. **Loosening** (remove, merge, relax a
   threshold) is always his. **Prose corrections** re-validate in the same sitting (his 2026-09-17 ruling).
6. **Three standing reviews per escape is too much loop.** A design, a Producer review, an Efficiency review, a rerun
   and maybe him, for every escape, costs tokens and days. Ordinary check changes get one independent reviewer;
   Producer and Efficiency review only contract changes, batched weekly per mod; contract changes reach him batched
   on one card. Targets: the regression check is running within 1 day of the escape. Every permanent check carries a
   reason to exist (the escape or bar it guards), so Efficiency can retire dead ones without touching a bar.
7. **Nobody is named to find escapes, and blame hides them.** The finders are him, the Auditor's samples, Player.log
   harvests and players. The Auditor tracks escapes weighted by severity. A check defect the Arbiter discloses
   itself is not counted against it, so disclosure pays and concealment does not.
8. **The Producer's review needs a scope.** Its first question is *"is any part of the vision un-barred?"*
   (coverage). It may also flag a threshold that misrepresents the vision, but only as a card to him; it never
   weakens a bar itself.

### Amended proposal
```
CONTRACT  Producer drafts bars from the vision ─► Efficiency: needed? combinable? ─► Arbiter: testable?
          ─► Lukas validates the hash (new bars: him, or inside his allowance; loosening: always him)
CHECKS    Arbiter specifies ─► builder implements ─► one independent reviewer
          merges: detection preserved (old reds + seeded defects still red) and floor fully covered
JUDGE     claim done ─► checks run ─► Arbiter: PASS | FAIL(module/check/environment/bar, may be several) | UNRESOLVED
          └─► Auditor: every distinct evidence-discarding decision + a sample of PASSes
LEARN     escape (him / Auditor / log / player) ─► regression check on an existing bar, running within 1 day
          └─► needs a new bar? ─► weekly Producer + Efficiency review ─► card to him (batched)
DEADLOCK  one round each ─► card to him; meanwhile the disputed check runs and counts
```
In one line, the separation is: **he owns a versioned contract; builders maintain checks; the Arbiter judges; the
Auditor reviews passes and anything that discards blocking evidence; the Producer advises on intent and Operations
on cost.** **For his ruling:** (a) may regression checks against approved bars land without him (they change no
bar)? (b) does he want a per-mod allowance for new bars, or should every new bar come to him? Nothing in this
review changes a bar or a hash.

GPT second opinion (`gpt_consult.py`, 2026-10-26; `D:\ClaudeWork\rimmandrake\resp_register\gpt_review.md`), folded
in above: `floor` coverage is not detection; delegating all tightening ratchets scope; the deadline, not the budget,
breaks deadlocks; blame-counting escapes rewards concealment; and the one-line separation is its wording.

---

## Part 2. Responsibilities register

Every AI role also carries the **cross-cutting rules**, which are rules and not duties (they are not doubles): hand
off at a wave boundary (`handoff.py`), file lessons (`lessons.py add`), fix a false line on sight, end a dead item
on sight, commit explicit paths, and log delegated calls `--why "delegated: <class>"`.

### Lukas — vision and taste
- **Duties:** hold the vision and taste; choose focus mods and freezes; validate north-star bars
  (`modcheck validate --owner-said`); rule on the `delegation_policy.md` §2 list (irreversible acts on others' work,
  re-freezing `official`, art purge, replacing kept art beyond the exceptions, overturning standing rulings, outward
  and paid acts, presence-bound acts: flyer flight, `broadcast.py`, `./bridge` assignment); set the starting schedule
  file; silence a role; review curated sets; overturn digest lines; release adversarial reviews when he wants to.
- **Inputs:** Conductor answers and the metrics pack, the daily digest, cards, review sheets and maps.
- **Outputs:** rulings (`--owner-said` / `--by-card`), validations, sheet marks.
- **Trigger:** whenever. **Decides alone:** all of the above. **Hands:** everything else, to the Conductor.

| # | metric | definition | measure | value |
|---|---|---|---|---|
| L1 | keep-going messages/day | his human-origin messages whose only content moves the machine (go, wake, keep going, status) ÷ days | `src/RimMandrake/Utils/sim/friction_census.py extract` → `D:\ClaudeWork\rimmandrake\orch_record\friction_census.md` | MEASURED ~31/day (10-05..10-26); target ≤26 after v3.0 |
| L2 | failure-signal share | share of his messages tagged broken/repeat/should-know/obvious-fix/ceremony/slow | `D:\ClaudeWork\rimmandrake\csuite\stats.txt` (model-tagged census of `owner_msgs.jsonl`) | MEASURED 27.5% of 2,114 (10-02..10-27); target ≤25% |
| L3 | decisions waiting on him > 3 d | open `--for OWNER` items older than 3 days | `rimflow_metrics.py --days 7` → `owner_wait_open.over_3d` | MEASURED 34 of 49 |
| L4 | his checking time | turns that are only "status?"/"what needs me?" plus digest visits per day | — | UNMEASURED (baseline M17): no turn classifier and no digest-visit log |

### Conductor — the one he talks to (quick mode on the phone; session mode at the bench)
- **Duties:** answer him from the metrics pack, every number with its MEASURED/UNMEASURED word; turn his words into
  Dispatcher instructions and tickets; record his rulings on the ledger with the right provenance flag and propagate
  them into every file that contradicts them (`deciding-and-superseding`); card him on §2 calls only; gate what
  reaches him (nothing unread: prereview through judges); deliver the daily digest and triage "what needs me?";
  `./game --said` on his game-state words; record a canon line in `canon.yml`. **Session mode** adds design work, the
  hardest bugs, live testing with him and, by his 10-23 ruling, the FlowWorks + GSS lane (see the Part 3 orphan O1).
- **Inputs:** his messages, the metrics pack (`rimflow_metrics.py`, pulse streams, `account_usage.py now`), the ledger.
- **Outputs:** answers, cards, tickets, ledger rulings, the digest.
- **Triggers:** every message (quick mode), his presence (session mode).
- **Decides alone:** what reaches him, when, and in what form; delegated §1 calls in session work.
- **Hands:** builds to the Arbiter; repeat errors to the Auditor; plan questions to the Producer; schedule changes to
  the Dispatcher's schedule file. **Never:** exempt its own builds from the Arbiter or Auditor.

| # | metric | definition | measure | value |
|---|---|---|---|---|
| C1 | "already ruled" messages | his messages matching an "already ruled/told/answered" pattern, per 14 days | `D:\ClaudeWork\rimmandrake\baseline_2026-10-26\already_ruled.py` | MEASURED 7 (10-11..10-25); target 0 |
| C2 | his answer turnaround | median days from `--for OWNER` filing to resolution | `rimflow_metrics.py` → `owner_wait_resolved.median_d` | MEASURED 1.59 d (n 61) |
| C3 | digest kept | days with `Transient/delegated_digest_<date>.md` written ÷ days | `ls Transient/delegated_digest_*` | MEASURABLE, not yet taken |
| C4 | answer corrections | share of Conductor answers with a number later corrected | — | UNMEASURED: no answer log with cited sources |

### Producer — what and when
- **Duties:** daily list and weekly plan; critical path per focus mod; named scenarios written before building (these
  become the acceptance targets); idea bank (`design/V2_DREAMS.md`); focus WIP cap; re-plan when a plan step fails;
  backlog hygiene (blocked items, stale items, `queue_staleness_review.py`); choose what the test lane runs
  (`TESTQ_FILL_MODS`/`TESTQ_SWEEP_MODS`); review bars for vision **coverage**; propose each mod's test budget.
- **Inputs:** his vision and focus, the ledger, the metrics, Arbiter verdicts. **Outputs:** the ordered plan, scenarios,
  coverage reviews.
- **Triggers:** daily, weekly, a failed plan step. **Decides alone:** work order and the WIP cap.
- **Hands:** bars to Efficiency and the Arbiter; budgets to him. **Never:** grade its own plan's work, or weaken a bar.

| # | metric | definition | measure | value |
|---|---|---|---|---|
| P1 | accepted items/day | items reaching done with a level-tagged `verify` pass on named scenarios, on a specific build, by a non-maker | ledger `verify` events with `level` (M8) | PARTIAL: level part MEASURED (only ~1% of closes since 10-19 carry one); non-maker part UNMEASURED: no verifier-role stamp on the events |
| P2 | net flow | filed − (done + dropped + superseded), 7 d | `rimflow_metrics.py` → `flow.net` | MEASURED +575 (1,544 filed / 927 done) |
| P3 | mods finished/week | mods reaching the SHIPPED rung (debug_process §6a) | — | UNMEASURED (M18): no "mod finished" event; proxy is `<MOD>_NORTHSTAR_SHIPPED_*` items closed |
| P4 | blocked work | blocked items, count and median age | `rimflow_metrics.py` → `blocked` | MEASURED 114, median 23.0 d |

### Arbiter — good enough
- **Duties:** rule PASS / FAIL-module / FAIL-check / RESTART-environment / BAR-defect on a feature that claims done,
  against its named scenarios and north-star bars, on a specific build, with evidence; work the verify backlog (L1–L3,
  GREEN-MIN/FULL; L4 is his); keep each mod's floor WIRED (every bar claimed by a check); run the judge protocol for
  taste calls (`delegation_policy.md` §4); the non-maker code-review gate (`code_review_status.py`); specify a check
  that is red on the old build for every escape; take his north-star calls as drafts for his validation.
- **Inputs:** builds, results JSON, the walks, the ledger. **Outputs:** verdicts with evidence paths, check specs.
- **Triggers:** a feature claims done (event); escapes. **Decides alone:** the verdict and its class (audited).
- **Hands:** check specs to builders; bar defects to the Producer and him. **Never:** build what it judges, care
  about the schedule, or validate a bar.

| # | metric | definition | measure | value |
|---|---|---|---|---|
| A1 | verify backlog | built items awaiting a verify level: count, median age | `rimflow_metrics.py` → `verify_backlog` | MEASURED 521, median 17.3 d (L2 327, L4 110, L1 134) |
| A2 | acceptance latency | median days from `implemented` to the last level passed | `rimflow_metrics.py` → `acceptance` | MEASURED 0.71 d (n 116) |
| A3 | escapes | defects filed against an item the Arbiter passed, per week | proxy: `rimflow_metrics.py` → `rework.cause_already_done` | PROXY 198 of 1,544 filed (12.8%); true value UNMEASURED until Arbiter verdicts carry a role stamp |
| A4 | check-defect share | FAIL-check verdicts ÷ all FAIL verdicts | `src/RimMandrake/Utils/pulse/testing_metrics.py` (harness vs mod failures) | MEASURABLE per day and machine, not yet taken |

### Auditor — "are you sure?"
- **Duties:** daily sample of closed items and Arbiter passes (≤4 investigations); re-check **every** check-defect
  verdict; repeat error → an enforced rule (a hook, or a charter line replacing one); curate lessons into skills in a
  fresh-context session; run the scheduled adversarial reviews of scripts (`NORTHSTAR_ADVERSARIAL_REVIEW_1`); spot
  check the delegated digest; instrument trust (a round, zero or alarming count is a query bug until probed,
  `infrastructure/state/facts/instrument_traps.md`).
- **Inputs:** the ledger, git, verdict files, his failure-tagged messages. **Outputs:** tickets, hooks, rules, audit
  notes.
- **Trigger:** daily. **Decides alone:** what to file. **Never:** close or accept anything.

| # | metric | definition | measure | value |
|---|---|---|---|---|
| AU1 | audit yield | sampled items where the re-check finds a defect ÷ items sampled | — | UNMEASURED: no audit record; instrument owed is a ledger note `--why "audit: PASS|DEFECT …"` |
| AU2 | repeat-error share | his messages tagged "repeat" ÷ all his messages | `D:\ClaudeWork\rimmandrake\csuite\stats.txt` (tag R) | MEASURED 9.4% (rising, 8.3% → 11.1%) |
| AU3 | lessons → rules | commits touching `.claude/hooks/` ÷ new files in `infrastructure/state/lessons/`, per week | `git log --since=7.days --name-only` | MEASURABLE, not yet taken |
| AU4 | unverified closes | closes since a date with no level-tagged verify event | `D:\ClaudeWork\rimmandrake\baseline_2026-10-26\ledger_measures.py 2026-10-19` (M8) | MEASURED 813 of 823 (98.8%) |

### Innovator — "what could be much better?"
- **Duties:** process experiments, each with a named metric and a keep/kill date (2×/week); a weekly design review
  of what the game design lacks, has out of place, misaligned, confusing, or an unneeded appendix; propose cadence
  changes as experiments; tend `design/V2_DREAMS.md` with the Producer reading it.
- **Decides alone:** reversible process experiments. **Hands:** design findings to him through the Conductor.
  **Never:** change a bar or the vision.

| # | metric | definition | measure | value |
|---|---|---|---|---|
| I1 | experiments | started / kept / killed per week | — | UNMEASURED: no experiment registry (`experiment_manifest.py` freezes measurement inputs; it is not a registry) |
| I2 | process-commit share | commits whose every path is under `infrastructure/ design/ conversations/ src/RimMandrake/Utils/ src/RimMandrake/rimflow/ .claude/ skills/ Transient/` or `CLAUDE.md`, ÷ commits with files | `D:\ClaudeWork\rimmandrake\resp_register\process_share.py <since>` (to move into the repo) | MEASURED 70.3% (721 of 1,026 since 10-26 00:00 PDT); target below 61% |
| I3 | design findings he takes | design findings he answers yes ÷ findings shown | — | UNMEASURED: findings are not tagged; instrument owed is `rimflow file --kind design` plus his ruling event |

### Operations — keeps it running and efficient
- **Running:** stuck processes and stale helpers; lapsed leases on doing items; disk (`scratch_reap.py`,
  `scratch_clone.py sample`); git health (locks, `mirror.py` sync, publish failures, `repair_torn_ledger.py`);
  reboots and game state and speed (never while he plays); memory (`memwatch.py`); the health of every timer and
  service (pulse, telemetry, `artpiped`, testq on SteveDesktop); nightly selftests red → tickets; leftovers
  archive-then-delete; compactions without a handoff.
- **Efficiency (the economy pass, daily):** tokens on every account including Codex; slot rules (`slot_rules.json`);
  test hours that catch nothing; art redraw loops; ceremony on his attention; **north-star skepticism** (Part 1:
  proposes cuts, and enacts check merges only when detection is preserved and the floor stays fully covered; a bar
  cut is always his).
- **Decides alone:** anything already ruled; resource budgets. **Never:** touch the game while he plays; lower a bar.

| # | metric | definition | measure | value |
|---|---|---|---|---|
| O1 | token runway | per account: hours of quota left at the current burn ÷ hours to the weekly reset (below 1 = runs out early) | `python3 src/RimMandrake/Utils/account_usage.py now`; Codex `src/RimMandrake/Utils/sim/csuite_codex_limits.py` | MEASURED 2026-10-26 22:33: system 30% left, 38 h to reset; lukas 7% (ESTIMATE) |
| O2 | test hours catching nothing | busy test-rig hours per week on runs with no finding, no regression and no close (including wasted runs) | `src/RimMandrake/Utils/pulse/testing_metrics.py` (USEFULNESS) | MEASURABLE; target ≤18 h/wk (v3 §6) |
| O3 | stale work | open items with a lapsed lease + doing items with no lease | `rimflow_metrics.py` → `leases.open_items_lapsed_now`; `baseline_2026-10-26\doing_leases.py` (M9) | MEASURED 166 lapsed; 123 doing, 0 with a live lease |
| O4 | scratch disk | GB under agent scratch eligible for the reaper | `scratch_reap.py` (dry run), `scratch_clone.py sample` | MEASURED 240 GB (csuite evidence) |

### Dispatcher — a program, not an AI
- **Duties:** run every role from the one schedule file; wake a stalled builder, hand it the next ticket, check that
  it happened, retry, record; lease-based "doing"; enforce caps (the slot allocator's N) and budgets; apply the
  token-pressure throttle order (v3 §3); one bridge holder at a time; never take the game while he plays; verify that
  a woken seat consumed its handoff; run the test lane (testq tick/steward/ingest is the RUNNER's Dispatcher
  instance on SteveDesktop).
- **Decides:** nothing; it follows the plan and the rules.

| # | metric | definition | measure | value |
|---|---|---|---|---|
| D1 | wake success | wakes verified within N min ÷ wakes issued | — | UNMEASURED: Dispatcher unbuilt |
| D2 | idle with work queued | builder minutes idle while a ready ticket exists, per day | — | UNMEASURED (M16); upper bound from ledger silences up to 23.2 h |
| D3 | leased doing | doing items with a live lease ÷ doing items | `baseline_2026-10-26\doing_leases.py` | MEASURED 0 of 123 (target: all) |
| D4 | cap breaches | peak helpers above N | `slot_allocator.py now` | UNMEASURED (M15): the over-N hook logs nothing |

### Foundry — the autonomous builder
- **Duties:** build the ticket the Dispatcher hands it; own `src/`, deploys and the game build (FlowWorks excepted
  while the 10-23 ruling stands); live testing through the bridge when the Dispatcher grants it; verify what lies
  (patches, setters, large-artifact counts, texPaths); ship each new mod with its first script; provisional numbers;
  feed approved art jobs to the pipeline.
- **Decides alone:** delegated §1 calls inside its ticket. **Hands:** the done claim to the Arbiter.

| # | metric | definition | measure | value |
|---|---|---|---|---|
| F1 | throughput and lead | done per day; median lead time from filing to done | `rimflow_metrics.py` → `flow`, `lead` | MEASURED 927 done/7 d; median lead 0.03 d, p90 1.56 d |
| F2 | rework | items filed whose cause is an already-done item ÷ items filed | `rimflow_metrics.py` → `rework` | MEASURED 198 / 1,544 (12.8%) |
| F3 | verify fail share | verify fail ÷ verify results, 7 d | `rimflow_metrics.py` → `verify_results` | MEASURED 56 of 603 (9.3%; 188 partial) |
| F4 | bounce | items reopened 3+ times, 7 d | `rimflow_metrics.py` → `bounce.items_3plus` | MEASURED 7 |

Per-seat splits (BENCH vs FOUNDRY) of F1–F4 are UNMEASURED by role until the Conductor's session work and Foundry's
are stamped apart; today the seat stamp is the proxy.

---

## Part 3. Gap check — today's duties → one v3 role

Swept: `infrastructure/agents/CHARTER.md`, `BENCH.md`, `FOUNDRY.md`, the user systemd timers (`systemctl --user
list-timers`, 2026-10-26), and the process scripts in `src/RimMandrake/Utils/`.

| today's duty | performed today by | v3 owner |
|---|---|---|
| talk with him, triage "what needs me", record and propagate rulings, cards, `./game --said` | BENCH | Conductor |
| design work, hardest bugs, live testing with him | BENCH | Conductor (session) |
| FlowWorks + GSS: code, art, live test, acceptance, review, deploy | BENCH (ruling 10-23) | Conductor (session) — **orphan O1** |
| pull the queue, build, deploy, `src/`, game build | FOUNDRY | Foundry (fed by Dispatcher) |
| full belt: bridge agent, art pipeline up, offline builder | FOUNDRY | Dispatcher (keeps slots full), Operations (pipeline up), Foundry (builds) |
| acceptance sweeps L1–L3, GREEN-MIN/FULL | FOUNDRY, BENCH (FlowWorks), RUNNER verify events | Arbiter — **double D2** |
| judge agent for taste calls | acting seat's helper | Arbiter |
| code review (DIRTY until reviewed) | each seat on its own work | Arbiter — **double D5** |
| daily delegated digest | BENCH at first sitting or FOUNDRY nightly | Conductor (program builds it) — **double D1** |
| pulse digests 06:00/17:30, pulse brief (`rm-pulse-digest`, `rm-pulse-brief`) | timers | Conductor's metrics pack — **double D1** |
| stale-drop and ending dead items | any seat | Producer (item sweep) / Operations (lease sweep) — **double D3** |
| end-of-wave handoff; wake consumption | each seat | each role (rule); Dispatcher verifies the wake |
| lessons filing | each seat | each role (rule) |
| lesson → hook / charter line; skill curation | nobody on a cadence | Auditor — **orphan O3** |
| owner-found defect → permanent test | the fixing seat | Arbiter specifies, builder writes |
| test disturbance → environment ticket | the testing seat | Arbiter (RESTART-environment class) files; Foundry fixes |
| adversarial review of scripts | him, on his clock | Auditor (scheduled); he may still release one |
| north-star DRAFT lines | any agent | Producer drafts; Arbiter checks testability; he validates |
| game restarts on bridge-idle delegation | any seat | Operations — **double D4** |
| slot allocator N per seat (`slot_allocator.py`, `rm-pulse-streams`) | program | Dispatcher applies; Operations sets `slot_rules.json` |
| token meter (`rm-account-usage`, `claude-account-capture/warm`) | timers | Operations (O1) |
| scratch reaper (`rm-scratch-reap`), object-store sample (`rm-objstore`) | timers | Operations |
| mirror sync (`rm-mirror`), memwatch (`rm-memwatch`) | timers | Operations |
| telemetry export/health (`rm-telemetry-*`), pulse update/health (`rm-pulse-*`) | timers | Operations |
| nightly selftests (`rm-selftests-nightly`) → red read and ticketed | timer; nobody reads `Transient/selftests_nightly.log` on a cadence | Operations — **orphan O2** |
| codebase health (`rm-codebase-health`) | timer | Auditor reads it |
| testq tick/sweep/steward/ingest on SteveDesktop (RUNNER) | timers | Dispatcher (runs), Producer (what to test), Operations (health) |
| art pipeline daemon (`rm-artpiped`) | service | Operations (up); Producer (which jobs) |
| leftovers archive-then-delete | any seat | Operations |
| compaction-without-handoff watch (`compaction_watch.py`) | hook; counter suspect | Operations — **orphan O4** (instrument broken) |
| instrument trust (zero/round counts probed) | whoever counts | Auditor |

**Orphans** (a duty today with no owner on a cadence):
- **O1 FlowWorks between sittings.** His 10-23 ruling gives FlowWorks + GSS to BENCH and forbids FOUNDRY; v3 folds
  BENCH into the Conductor's session mode, which exists only while he sits. FlowWorks would then wait between
  sittings, which is the mutual waiting he ruled against. **His call:** keep it session-only, or let the Dispatcher
  feed FlowWorks tickets to a builder under the Conductor's lane rules.
- **O2 nightly selftest reds.** They run at 03:00, and nothing reads them and files tickets. → Operations.
- **O3 lessons → rules and skill curation.** Lessons are filed; turning a repeat into a hook or a skill edit has no
  cadence. → Auditor (AU3 measures it).
- **O4 compactions without a handoff.** The logger counts helpers as the seat (`COMPACTION_LOG_FIX_HELPERS_COUNTED_AS_SEAT`),
  so the duty exists with a blind instrument. → Operations, after the fix.

**Doubles** (two performers today, one owner in v3):
- **D1 digests:** the delegated digest (two seats, two schedules) plus the pulse digests and brief → one Conductor
  delivery built by a program.
- **D2 acceptance:** FOUNDRY, BENCH and RUNNER all write verify events → the Arbiter.
- **D3 stale sweeps:** any seat ends dead items (that rule stays), but the sweep *duty* splits by kind: items →
  Producer, leases → Operations.
- **D4 game restarts:** any seat under the bridge-idle delegation → Operations, plus the Conductor on his words.
- **D5 code review:** today makers review their own files (maker = checker; FlowWorks 0 defects in 2,744 self-reviews
  versus 13 once independent) → the Arbiter.

**Metrics left UNMEASURED:** L4 his checking time · C4 answer corrections · P1 non-maker part · P3 mods finished ·
A3 true escapes (proxy only) · AU1 audit yield · I1 experiments · I3 design findings taken · D1 wake success ·
D2 idle with work queued · D4 cap breaches. Measurable but not yet taken: C3, A4, AU3, O2.
