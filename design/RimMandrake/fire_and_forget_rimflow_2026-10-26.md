# Fire-and-forget RimFlow — second GPT perspective (2026-10-26)

Owner, 2026-10-26: *"How can we make this into more of a Devin-style fire-and-forget building system that uses human review time as rare and valuable. That understands testing is vital to get things done, but testing itself is valueless in terms of productivity. What would fire-and-forget RimFlow look like?"*

Inputs: `orchestration_design_record_2026-10-26.md`, `baseline_two_seat_system_2026-10-26.md`, `D:\ClaudeWork\rimmandrake\orch_record\friction_census.md`, `D:\ClaudeWork\rimmandrake\orch_record\gpt_against.md`.
Raw answer: `D:\ClaudeWork\rimmandrake\orch_record\gpt_fire_and_forget.md`. Fact-check sheet: `D:\ClaudeWork\rimmandrake\orch_record\ff\factcheck.md`. Prompt: `...\orch_record\ff\prompt.md`.

## Summary (15 lines)
1. GPT's thesis: optimise **accepted outcomes per owner interruption**; the system builds faster than it finishes and the owner supplies the continuation logic.
2. Keep both seats and their ownership (BENCH: all FlowWorks/GSS, acceptance); change their operating contract, not the architecture.
3. Every seat must end a turn in RUNNING / READY / WAITING(on whom, until when) / PAUSED(why). "I answered the owner" is not a stop.
4. A small deterministic supervisor (proposed `rimflow_cycle.py`, timer) fires the learn -> next -> plan cycle on events plus a 15-min reconcile; Opus in the seats does the planning.
5. The idle-wake channel is unproven (the record says untested; the owner declined the `/clear` test) and must be demonstrated before unattended use.
6. Goals live on disk in one plan file (proposed `infrastructure/state/plans/current.yaml`) that references ledger items rather than duplicating status.
7. "Done" is executable: rimflow already has per-item criteria and `verify --criterion`; `close` only WARNS on owed criteria. Make it refuse.
8. Testing: shared result cache keyed by test+code+fixture content hash (none exists today), plus stop rules: same failure on unchanged input = diagnose, not rerun.
9. Nightly (red 12/12): known-failure fingerprints with owner and expiry; a separate "no new regression" verdict; never relabel it green.
10. Art: a hard per-subject budget with the best candidate kept; every REGEN must name a fixable defect; after repeated facing failure, change the method, not the dice.
11. Human time: a short prepared sit-down (GPT: 20 min weekdays, 30 Monday), at most 5 agent-read decisions each, replacing the dead `HUMAN.md`.
12. Stop: treating filing/testing/occupancy as progress, admitting new work while the focus has acceptance debt, unchanged-input reruns, and further context-economics redesign.
13. GPT reconciles with its own "argue against change" answer: the evidence caveats stand, but the census justifies bounded operational changes now.
14. Our assessment: the proposal fits the measured friction; three points overlap existing code (criteria, art cap, digest) and one (art resets) conflicts with an owner card.
15. Ranked first steps below: continuation gate, close-refuses-owed, art budget covering owner-note regens, test cache for `flowworks_stock`, sit-down packet.

## GPT's proposal (condensed, fact-checked)
Marks: [C] checked against census/record/repo, [U] unchecked/proposal, [W] wrong or incomplete.

1. **Loop and ownership.** BENCH owns the sprint outcome and acceptance scheduling; FOUNDRY owns execution and local replanning. A planning cycle fires on worker completion/failure, new owner input, acceptance becoming possible (bridge free), a seat idle with eligible work, or a 15-min deadline. It writes a checkpoint: learned, plan revision, next action, owner, expected next event. [U — proposal] Build the three filed compaction-restore fixes first (`COMPACTION_RESTORE_OPEN_ITEMS_FROM_LEDGER`, `OWNER_RULINGS_HARDEN_DATES_ON_DISK`, `HELPER_IDS_RESTORE_AFTER_COMPACTION`) [C: filed, none built, record §table l.337]. Do not auto-requeue expired leases (107 lease-less "doing" rows) without reconciling [C: census l.101]. Wake channel unknown [C: record l.395].
2. **Goals/DoD.** One plan file referencing rimflow IDs; owner controls outcomes, scope, any relaxation of acceptance; `close` should require evidence matching the item's acceptance contract; "L0–L4 meanings unknown". [W] Criteria with levels (L0..L4, GREEN-FULL) and `rimflow verify --criterion --result --evidence` already exist; BENCH holds L4 (`src/RimMandrake/rimflow/priority.py:421`). `close` warns but does not refuse on owed criteria (`src/RimMandrake/rimflow/cli.py:1811-1819`, comment "step 3's call"). The gap is one refusal, not a new contract system. Triage the 496 BUILT / 470 bridge-owed [C: census l.100].
3. **Testing.** Changed-file -> test map; shared result index keyed by test identity + test-code hash + implementation/fixture hashes + runtime (dirty tree counts); identical concurrent requests share one run. Stop rules: valid matching pass ends the obligation; same failure on unchanged inputs -> diagnose; third run needs a recorded change; infra failures get one retry. Start with `selftest_flowworks_stock` (563 runs, 18.6 h) [C: census l.79]. `--only` already cut full-suite runs from 32/day to ~0 [C: l.78]. 33% repeats include legitimate red->green loops [C: l.81]. 3.3 h/day is agent-hours, not wall [C: l.17]. No content-hash result cache exists today [C: `run_selftests.py` `run_cache` (l.625) is a per-run scratch dir removed at run end; `Utils/testq/` is the live-test RUNNER queue].
4. **Human time.** 20 min each weekday, 30 Monday; at most 5 decisions, each agent-read with recommendation, alternatives, cost of deferral and the exact question. Queue only scope/acceptance-policy changes, taste/canon ambiguity, conflicting rulings, permissions, demos needing judgment. Replace `HUMAN.md` with a generated ledger projection shown in RimPulse with freshness; deliver via the 06:00/17:30 digest [C: `src/RimMandrake/Utils/pulse/systemd/rm-pulse-digest.timer`]; record enactment receipts via `art.py enact` [C: `src/RimMandrake/Utils/art/art.py:443`]. `HUMAN.md` stale, says "NOTHING IS WAITING" [C: census l.103]. Absence is not approval.
5. **Art.** Subject-level budget: initial + 2 corrective rounds + 1 infra retry; keep the best valid candidate; at cap: accept against criteria, change method, or hold for the sit-down. Separate hard defects from preferences; every REGEN names a defect and an intervention. Facing is the largest failure class (558 hits) [C: census l.93] — after repeated facing failure, use derivation/editing/retained facings. Calibrate Opus/GPT judges on owner keeps/cuts; use the second judge for ambiguity, not serial veto. [W/partial] A cap of 3 rounds then ESCALATE with reason-driven REGEN already exists (`src/RimMandrake/Utils/art_eval/policy.py:16`, `round_series.py`). What escapes it: the 25 series resets (owner-authorised, `round_series.py:205`) and owner-note regens (1,012 jobs, 15%) plus other non-judge jobs, which is how `RM_HoseReel` reached 40 [C: census l.89-90]. GPT's "resets cannot reset subject history" contradicts the owner card of 2026-10-24 06:29 ("After round 3 fate -> 1 + user improved prompts").
6. **Stop.** Treating filing/publishing/testing/helper occupancy as progress; admitting new work while the focus has acceptance debt; unchanged-input retests; unbounded art resets; owner-facing raw output; stale status docs; unfenced reassignment; re-asking enacted rulings; more orchestrator context-economics work (helpers are 83.7% of spend [C: record l.267]).
7. **Build order (GPT's targets, all [U]).** (1) continuation gate + one proven idle-wake path: b+g+h ~31/day -> <=10/day over 14 active days; (2) acceptance contracts + close gate: original 496 cohort -20% by evidence-backed acceptance in 14 days, backlog must not grow; (3) art subject cap: no subject >3 rounds without a budget decision, REGEN per accepted subject -30% in 7 days; (4) test cache + stop rules from `flowworks_stock`: selftest agent-hours -30% vs 3.3/day in 14 days; (5) appointment packet + receipts: needs-owner median age 28 d -> <7 d.
8. **Versus "argue against change".** Still agrees: idle hours are not recoverable capacity, quota does not settle productivity, faster dispatch can grow the unfinished pile. Disagrees with using those caveats to defer a continuation-and-acceptance loop. Reconciliation: keep the seats, change the contract, prove fewer interventions plus more acceptances before any architecture change.

## Our assessment

### Where it fits the measured friction
- **Owner driving (~31/day, 64% of seat runs end <5 min after he speaks):** the turn-end state gate is the only proposal that attacks this directly. It is cheap (a Stop hook that refuses a bare stop without a RUNNING/READY/WAITING/PAUSED line) and testable without the unproven wake channel; the wake channel matters only for a seat that is already idle.
- **496 BUILT, 470 bridge-owed:** fits the owner's "REALLY ticked off" and one-or-two-mods focus (record §2). The criteria machinery exists; the cheapest lever is making `close` refuse owed criteria and having BENCH run batched bridge acceptance sessions. Caveat: many of the 470 may carry a blanket inherited `bridge` level; triage must not lower a level just to empty the queue (GPT says the same).
- **Selftests:** the payoff is concentrated. `flowworks_stock` alone was 3.8 h on 10-26. A content-hash cache with a "same failure, same inputs -> no rerun" refusal is the right shape; GPT is right that the 33% repeat share overstates waste.
- **Art 74% REGEN:** the round cap exists, so "add a cap" is not the fix. The leaks are owner-note regens and resets outside the cap, and the facing class (558 hits), which the census calls a generation-model limit. Changing method after facing failure (keep the good facing, derive or edit the others) is the real lever.
- **Dead inbox:** fits exactly; the digest timers exist, the inbox content does not.

### Where it conflicts with standing owner rulings
- **Art series resets:** GPT says resets must not reset a subject's budget. The owner card 2026-10-24 06:29 ("After round 3 fate -> 1 + user improved prompts") grants fresh rounds after his prompt. Keep his resets; count non-judge and owner-note regens against a separate visible budget instead.
- **Nothing reaches the owner unread** (CLAUDE.md l.245, owner 2026-10-22): GPT's packet respects it (agent-read artifacts only). Keep `prereview.py` as the gate for anything art in the packet.
- **Never live-test a flyer's flight without the owner present** (CLAUDE.md l.211): batch bridge acceptance must exclude flyer flight; flight checks are exactly what the sit-down is for, so they belong in the packet, not the autonomous lane.
- **BENCH owns all FlowWorks/GSS** (CLAUDE.md l.61, owner 2026-10-23): GPT keeps it. The `flowworks_stock` cache work is therefore BENCH's.
- **Wrong material is deleted, not superseded** (CLAUDE.md l.226): GPT applies it to art and review-sheet references. Consistent.
- **No worldgen / every DLC assumed:** nothing in the proposal touches either.
- **Owner declined the `/clear` test** (record l.129): GPT does not use it. Consistent.
- **"Stop admitting new work while the focus has acceptance debt"** is a scope change for the owner to rule on, not a seat decision.

### Where we think GPT is weak
- 20 min every weekday is a guess; the owner asked for "a periodic opportunity". Start with the cadence he picks; measure decisions per sit-down.
- `infrastructure/state/plans/current.yaml` risks a second status source next to the queue projections. Hold only goal, focus, constraints and step order there; status stays in the ledger.
- The supervisor + wake channel is the largest unknown and should not gate steps 2-4.

## Ranked first steps (ours)
| # | Step | Owner | Payoff metric (census baseline) | Target / window |
|---|------|-------|-------------------------------|----------------|
| 1 | Turn-end state gate (Stop hook: no bare stop; every stop names RUNNING/READY/WAITING-on/PAUSED-why) + build the 3 filed compaction-restore fixes | BENCH | owner b+g+h messages ~31/day (hand-labelled, n=140); seat runs ending <5 min after owner msg 64%, median 1.8 min | <=15/day and <40% in 14 active days, accepted items not falling |
| 2 | `rimflow close` refuses owed criteria (warning -> refusal, owner override recorded) + BENCH batched bridge-acceptance sessions on the focus mods | BENCH | 496 BUILT (470 bridge-owed), FOUNDRY median age 17 d | original cohort -20% by `verify` evidence in 14 days; BUILT total not growing |
| 3 | Content-hash selftest result cache + rerun refusal on unchanged inputs, starting with `selftest_flowworks_stock` | BENCH | 3.3 agent-h/day selftests; flowworks_stock 18.6 h / 563 runs (3.8 h on 10-26) | selftest agent-h/day -30%; stock-test runs with identical input hash = 0 |
| 4 | Art budget that also counts owner-note and non-judge regens; after 2 facing failures switch to keep-best-facing + derive/edit | BENCH | 74% REGEN, max 40 jobs/subject, 558 facing hits, 1,012 owner-note regens | no subject >6 jobs without a recorded decision; REGEN per accepted subject -30% in 7 days |
| 5 | Sit-down packet replacing `HUMAN.md` (generated, <=5 agent-read decisions, delivered by the digest timer, receipts via `art.py enact`) | BENCH | needs-owner median age 28 d; card pulls by hand 6% of owner msgs | median age <7 d; hand card pulls -> 0 in 14 days |

Owed to the owner (for the sit-down): cadence of the sit-down; whether to freeze new-work admission while the focus has acceptance debt; whether owner-note regens count against the art budget.
