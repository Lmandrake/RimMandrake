# RimFlow v3 collapse: how it was settled (2026-10-31)

Item: `RIMFLOW_V3_SHRINK_FEWER_CHAIRS_SAME_JOBS`. Measured at commit 1195f7cc54, Sat 2026-10-31 19:15 PDT.

**Verdict.** The collapse is decided but not built, and nothing was built under this item. No role, schedule or code
changed here. The fewest-parts question is answered by the arena trial and its rules, which he accepted. What the trial
does not settle is carried by one blocked item, `V3_COLLAPSE_BUILD_AFTER_THE_QUIET_MONTH`.

## What decides it

His ask of 10-29 was to settle one stable design together, with fewer parts. Two blind minimal designs were compared in
`D:\Luke\dev\RimMandrake\design\RimMandrake\rimflow_v3_collapse_compare_2026-10-29.md`. That page's rulings D1-D6 never
reached him, because he moved to the trial the same day.

On 2026-10-30 he gave GO for the trial with the Conductor's three pre-committed rules (note on
`TESTPILOT_DESIGN_PROOF_BEFORE_RELOAD`, seat OWNER, 00:37:35Z):

1. A day-2 critic measurement that shows an unreliable critic settles it: the simplest critic-free arm.
2. No clear winner at the day-3 hard cap: the simplest arm, in the tie order of
   `D:\Luke\dev\RimMandrake\design\RimMandrake\architecture_switch_harness_2026-10-29.md` section 4.1, with no further
   round.
3. Then no architecture work for about a month. FlowWorks gets the time.

So "fewest parts" is now a test result, not a design argument: the fixed order is `ralph_a` < `ralph_c` < `trio` <
`v3c` < `v3`, and `v3c` was dropped on 10-31. The result reaches him through the trial report (BENCH note on this item,
10-31 16:55Z). Rule 3 is also why the compare page's build order must not start now. A separate ruling stands whatever
the trial says: the Test Pilot is adopted (OWNER note, 10-31 17:16:42Z).

## The item's four asks, as they stand

| Ask | State | Evidence |
|---|---|---|
| Fewest parts, settled before freezing | **Decided by rule, result pending.** Today all six roles are still `enabled` in `src/RimMandrake/rimflow/dispatcher_schedule.json`: Conductor, Arbiter, Auditor, Operations, Producer, Innovator. Nothing has been removed. | The rules above. The frozen design is the trial's winner, not the compare page's section 6. |
| Test until pass, then blind review | **Enforced in one lane only.** A relentless worker cannot finish without a blind rerun of its proof by a checker that sees no notes. Seat closes are unchanged: `close` still defaults to HEAD (`cli.py` `cmd_close`, `sha = args.sha or head_sha()`) and owed criteria are "a WARNING, not a refusal". The relentless pool is `["BENCH"]` until `RELENTLESS_FOUNDRY_WIDEN_AFTER_TRIAL_ENDS`, so FOUNDRY, the seat he named, has no such loop yet. | `src/RimMandrake/rimflow/relentless.py`, `relentless_rules.json` `pool_seats` |
| Every finished component and the whole system to GPT | **Not enforced.** The relentless checker is `rm-judge`, which is Opus (`.claude/agents/rm-judge.md`), so a blind rerun there is not a GPT review. In `src/RimMandrake/rimflow/` the only production caller of `gpt_consult` is `arbiter_tiers.py`. GPT reviews of components and of the system were done by hand for particular pieces, such as `design/RimMandrake/rimflow_v3_gpt_risk_review_2026-10-29.md`. No rule makes them happen. | This is the largest gap against his words. |
| "Current focus": depth before breadth | **Partly.** `seat_focus` in the schedule filters what `next` offers by id prefix, when set. Relentless holds one item until it is proven, with `max_workers: 1`. No program limits how many items a seat has started, and no code reads a WIP cap. | `cli.py` `_seat_focus`; `relentless_rules.json` |

## What this changes on the older pages

- **D1-D6 of the compare page are retired as questions to him.** D1 (planner separate from builder), D2 (a Claude
  judge) and D4 (gates or rewrite) depend on which arm wins. D3 (focus limit), D5 (when criteria freeze) and D6 (who sees
  a dead main PC) survive as inputs to the carrier item, with the page's recommendations. These are different questions
  from the D1-D6 of `design/RimMandrake/rimflow_v3_audit_remeasure_2026-10-31.md`, which are still his and are untouched.
- **The five parked items wait on the carrier.** `V3_HEALTH_BUILD_DAILY_PULSE_DAY_ONE`, `OPS_MODEL_BUILD_V3_TWIN_FIT_DAILY`,
  `AUDITOR_BUILD_WAITING_INDEX_REQUEUE_SCAN`, `INNOVATOR_BUILD_EXPIRY_WATCHDOG_REVERTS` and
  `HELPERS_BUILD_SHARED_CAP_ACROSS_ROLES` still read `doing` with no lease. That state keeps them out of the relentless
  pool, so they stay where they are. If the winner has no such role, each is dropped. If `v3` stands, each is judged
  against the compare page.
- **The verify hole is still open.** The last passing `verify` makes an item `done` with no `close` and no review
  (`model.py` `_criterion_passed`). Any done gate has to sit in that transition, not only in `close`. It was found on the
  compare page and had no item of its own; the carrier now holds it.

## What the carrier item does

`V3_COLLAPSE_BUILD_AFTER_THE_QUIET_MONTH` is blocked on `TESTPILOT_DESIGN_PROOF_BEFORE_RELOAD`, and rule 3 holds it
further, until about 2026-12-01. When it opens, it applies the trial's winner and closes the gaps above against that
winner, depth first, with each step blind-reviewed by GPT.

The 18 draft tickets of the audit re-measure stay unfiled by his order on `V3_WORKFLOW_AUDIT_EVERY_CLOCK_AND_DOOR`. The
carrier does not file them.
