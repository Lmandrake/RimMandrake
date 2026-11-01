# RimFlow v3 audit: where it stands, re-measured (2026-10-31)

Item: `V3_WORKFLOW_AUDIT_EVERY_CLOCK_AND_DOOR`. Measured at commit 9611cb2af7, Sat 2026-10-31 ~18:30 PDT.
Re-measures every draft ticket and decision of `design/RimMandrake/rimflow_v3_risk_response_2026-10-29.md` against
today's code. Nothing is ticketed yet, by the owner's order on the item: *"before that is taken into tickets, I would
like to hear about the analysis myself here, and if there are any questions to decide upon, be presented with them."*

## Where the item is

| Step | State | Evidence |
|---|---|---|
| Document the workflow | done 10-29 | `design/RimMandrake/rimflow_v3_workflow_as_built_2026-10-29.md` (stale on one point: it predates the relentless lane) |
| GPT skeptical review, literature | done 10-29 | `design/RimMandrake/rimflow_v3_gpt_risk_review_2026-10-29.md` |
| Opus response | done 10-29 | `design/RimMandrake/rimflow_v3_risk_response_2026-10-29.md` |
| He hears it, decides | **half** | A chat summary went to him 10-29 20:31Z. He redirected at 20:38Z to collapsing the design, then to Ralph loops. D1-D6 never reached a card; the Conductor's 20:41Z message still listed D1, D2 and D6 as owed. |
| Ticket out at max priority | **not done** | All 18 names: `rimflow show <name>` says "has never been filed". |

## What changed since the response

1. **The relentless lane drains BENCH.** `src/RimMandrake/rimflow/relentless_rules.json` has `pool_seats: ["BENCH"]`,
   `pool_needs: ["offline"]`. The response's top complaint, alarms filed to a seat nothing rings, is no longer true for
   offline alarms: an `OPS_` item filed for BENCH is enrolled and a worker takes it. `OPS_STEVE_DIAGNOSE_INVALID_CE0E`
   ran this way. Limit: one worker (`max_workers: 1`) and 8 queued, so an alarm can wait behind other items.
2. **Relentless has a blind checker.** A worker's `finish` is rerun by a checker that does not see its notes. For
   items in that lane, "close without proof" is gone. Seats still use `rimflow close`, which is unchanged.
3. **Steve's invalid hours count as wasted, not productive** (`59ba780056`, reported to him 10-29). This is the
   owner's own example from the item.
4. **Done-when additions lost their homes.** `TESTLANE_PLAN_WIRE_PRODUCER_PICKS_UNHEARD` and
   `PRODUCER_CADENCE_DESIGN_MORE_THAN_WEDNESDAYS` were dropped on 10-29, so the response's additions to them have no
   target. `FINDINGS_FOLD_BUILD_QUARRY_SAID_IT_23X` is done, so its raise is moot.

## An error in the response

**D3/T7 missed an owner answer.** At 2026-10-29 15:53Z, five hours before the response, he answered a card on who
keeps the lessons emptied: *"The Auditor once a week."* `src/RimMandrake/rimflow/roles/auditor.md` l.163 carries it.
The response's recommendation D3(a), retire the queue, and T7 would overturn that answer, and the response does not
say so. D3 therefore needs putting to him as "you ruled weekly Auditor; intake is 626 a week against a 40-per-pass
budget; keep it or change it".

## The 18 draft tickets, measured

| T | Name | Verdict | Measured |
|---|---|---|---|
| T18 | `CLOCKS_PROVE_DST_FALLBACK_NOV_FIRST` | **NOT NEEDED: proven tonight** | No role slot lies in 01:00-02:00 (schedule walk: earliest 07:30). `systemd-analyze calendar '*-*-* 01:30:00'` from 18:00 PDT gives Sun 01:30 PDT; from that instant the next is Mon 01:30 PST, so `testq-sweep.timer` fires once. No other daily timer is in the hour (05:45, 06:00, 03:00, 04:20, 17:15, 17:30). `role_launch.prev_day` is noon-based; day keys are date strings, so a 25-hour day counts as one day. |
| T1 | `CLOSE_ENFORCE_NO_OWED_NO_IMPLICIT_HEAD` | OPEN | `cli.py` `cmd_close`: `sha = args.sha or head_sha()`; owed criteria still print "A WARNING, not a refusal". A live-promise gate was added; these two were not. |
| T2 | `ALARMS_REWIRE_OFF_RETIRED_BENCH` | **MOSTLY OVERTAKEN** | `ops_watch_rules.json` l.83 still says `"for": "BENCH"`, and steward's docstring still files `--for BENCH`, but relentless now drains that pool. 8 `OPS_` items proposed and 2 doing for BENCH. What remains: non-offline alarms have no receiver, and `relentless.py` `pool_order` gives an alarm no precedence unless it is raised, so `ops_watch` should raise what it files. |
| T3 | `VALIDATED_FIX_DEMOTE_ON_CURRENT_FAIL` | OPEN | `model.py` verify branch: only `result == "pass"` changes state. A fail records a run and nothing else. |
| T4 | `STEWARD_FIX_ENDS_ON_GREEN_NOT_RUNNING` | OPEN | `testq/steward.py` l.17 "the only state that ends an incident" is RUNNING; l.650 acts on it. A live lease pauses the clock with no cap. |
| T5 | `OPERATIONS_FIX_RUNS_BLIND_WHEN_STALE` | OPEN | `role_launch.py` gate 2 refuses every role on a stale reading, Operations included. |
| T6 | `DEADMAN_WIRE_PHONE_WITHOUT_AI` | OPEN | `deadman_check.py` has no phone or pulse-brief write; it reads items through pulse_core and files to the ledger. |
| T7 | `LESSONS_RETIRE_INBOX_AS_QUEUE` | **HIS CALL** | Conflicts with his 10-29 card answer; see above. The 40-per-pass and 14-day rules stand in `auditor.md`. |
| T16 | `PROCESS_WORK_SHRINK_TO_SIXTY_ONE` | HIS CALL (D5) | No such gate in `rimflow file`. Today's share not re-measured. |
| T8 | `ROLE_DUTIES_FIX_CARRY_MISSED_SLOTS` | OPEN | No `owed` slot key in `role_launch.py` or the schedule. |
| T9 | `SCHEDULE_HARDEN_FAIL_CLOSED_NO_DEFAULTS` | OPEN | `dispatcher.py` l.100-105 `DEFAULTS` and `CAP_DEFAULTS` (3/30/80/3), applied with `setdefault` at l.121. |
| T10 | `ROLE_RUNS_ENFORCE_STOP_AT_TWICE_CAP` | OPEN | No budget-stop flag in `role_launch.py` or `dispatcher.py`. |
| T11 | `OWNER_ASKS_MEASURE_AGE_IN_DIGEST` | OPEN, narrower | `pulse/pulse.py` l.672-700 lists asks with an old/new split; the digest has no age or waiters-on count. |
| T12 | `ALARM_REPEAT_FIX_BREAK_ON_WORSE` | OPEN | No severity or worsening test in the ops_watch repeat path. |
| T13 | `BRIDGE_ITEMS_ENFORCE_GRANT_PREFLIGHT` | **DONE ELSEWHERE** | `cli.py` `_apply_grant_preflight` withholds live items when the grant is not OK; `companion.grant_hours_left` raises an early alarm. Drop it. |
| T14 | `ROLE_HEADERS_RETIRE_ENABLED_PROSE` | OPEN, smaller | `innovator.md` and `operations.md` headers still say "enabled"; the schedule sits one line below. |
| T15 | `DISPATCHER_PROVE_BLOCKED_TOP_AND_CURSOR` | OPEN, smaller | Rearm is covered (`test_review_w_alarm_rearm`). No test named for a blocked top item; the 7 h cursor case not found. |
| T17 | `INNOVATOR_RETIRE_TWO_WEEKLY_SLOTS` | HIS CALL (D5) | Schedule still has `Tue,Fri 15:00` and `Sun 15:00`. |

Raises: `AUDITPRESCREEN_FIX_WAVED_THE_FAKE_THROUGH` is still `proposed`, raise stands.

**Count:** 1 proven unneeded, 1 done elsewhere, 1 mostly overtaken, 3 his call, 12 still true.

## The six decisions, as they stand

| D | Question | Change since 10-29 | Recommendation |
|---|---|---|---|
| D1 | Who may block a close? | Relentless already gives its items a blocking blind checker. The question now covers only seat closes. | Unchanged: (b) an Arbiter FAIL blocks. |
| D2 | Who repairs alarms? | Overtaken: relentless workers do. A fourth answer the response did not offer. | Ratify that; keep T2 only for non-offline alarms. |
| D3 | The lessons queue | He ruled weekly Auditor on 10-29. | Put the numbers to him; do not assume T7. |
| D4 | Owner asks that age | None. | (a) visibility only. |
| D5 | "Maximum priority" against the 61% target | Still a conflict: relentless takes only one item at a time, so the order matters more. | (b) P0 at max, P1 behind it. |
| D6 | When v3 is judged keep or kill | The Ralph and relentless arms changed what "v3" means. | Name the date, or retire the question if relentless replaced v3. His. |

## After he answers

For each surviving name, file with the "Done when" from §5 of the response, adjusted by this file:
`python3 src/RimMandrake/rimflow/cli.py file <NAME> --for <SEAT> ...`, then raise it to maximum priority. Drop T18 and
T13. Shrink T2, T11, T14 and T15 to the "remaining" text above.
