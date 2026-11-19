# Every counter a Maturation Pipeline run can consume, and whether a system death spends it (2026-11-18)

Item RIMMANDRAKE_VOID_SYSTEM_KILLED_RUNS_NO_TRIAL_SPENT. The owner, 2026-11-18 ~10:30 AM PST, about Graffiti: *"Ensure
it didn't use up it's turns, trials, whatever... I will not accept ANY system that pointlessly expends such statistical
measurements based on failed system calls or behavior. You know that. Fix the system such that it's easy to indicate
this to it. And NEVER tell me "I can't that's frozen" or "it's a write only ledger" or bullshit like that."*

The rule in code is `src/RimMandrake/rimflow/run_void.py` (selftest `selftest_run_void.py`). A run is **void** two
ways: a **hand void** (`maturation_dispatch.py void <unit>... | --item ID | --mod MOD --since TIME --why "..."
[--owner-said "..."]`, reversed by `unvoid`; listed by `voids`), or **void_system**, classed automatically when its run
record's own `result` (written at finish) shows a cause the machine can see: killed, its unit dead with its finish
never run, timed out, the CLI exiting with no result of its own, a launch that never started and has no retry left.
"success" counts; "exit-code/claude-error" (claude's own error: a cap, or the agent's) counts; "unknown (...)" counts (a
finish run without systemd's variables that read the agent's own result JSON: 13 of 618 records on 2026-11-19, 12 with
a success JSON still on disk); no result is UNMEASURED and left as the books had it. 🔴 Never re-read the output file for "no result JSON": a detached run's out is
not one JSON document, and reading it that way classed four old success runs void on the first live tick (2026-11-18
~11:10 AM PST; healed by `heal_system`, nothing launched: every mod read ceiling or owner_hold). A void run's book entries are
moved to the mod's `voided` list in `state.json`, never deleted; a Designer `stage.json` is made to agree by
`run_void.sync_stage`. System faults are counted on the mod's own `system_faults`, never on a trial; at 3 since the last
`clear` the mod reads `system_fault` (alarm `OPS_MATURATION_SYSTEM_FAULT_LOOP`) and nothing launches on it.

"Before" is the code at 1caaeb7ba4's parent (origin/main 2026-11-18 ~10:30 AM PST); "after" is f93b15709a and later.
Where a reading was measured it says `[measured]`; a guess carries its confidence.

## The dispatch books (`state.json`, `<dispatch state dir>/maturation/state.json`)

| counter | stored | read by | a system death BEFORE | AFTER |
|---|---|---|---|---|
| blind cycles per visit (`blind_auto_cycles_per_visit` 3; `maturation.CYCLE_LIMIT` 3) | `mods.<Mod>.blind_auto` (visit_id, cycle, unit, failed, tries, killed_before) | `decide_blind` (`ours` → `auto_spent`, `mine` → `stopped`), `retriable`, `reserve_refused`, `_clear` | a kill was retried up to `launch_tries` (3) and then **stopped**, spent; a never-started launch on a non-transient fault: **"stopped, never a second automatic try"**, spent; a transient one retried 3 then stopped; a run that ended with no record: stopped. Only a hand `clear` gave it back | kills still resume a half-written cycle (up to 3); past that, and every never-started launch with no retry left, a timeout and a CLI exit with no result: **void_system**, the cycle unspent, the next tick relaunches; 3 faults → `system_fault`. Hand void: yes |
| in-game runs per visit (`ingame_auto_runs_per_visit` 1) | `mods.<Mod>.ingame_auto` | `decide_ingame`, `retriable`, `_clear` | as for blind | as for blind |
| hand runs seen on a cycle or visit (`hand_run_seen`) | recomputed each tick from the run records (`add_blind` `blind_runs`, `add_ingame` `ingame_runs`) | `decide_blind`, `decide_ingame` | a killed hand run was already excluded (`killed`); a hand run that ended with no record stopped the mod | a hand-voided run is excluded too |
| killed-run retries | recomputed (`killed_runs`) | `retriable`, `reap_wait` | — | a hand-voided run is no kill to retry |
| steward once per state key | `mods.<Mod>.steward` (key → item, unit, failed, tries) | `maturation_autonomy._gate` (`steward_spent`), `releasable`, `autonomy_book`, `_clear` | a killed steward read "ended and the state has not moved": **steward_spent**, the mod PAUSED; a non-transient launch failure: spent | killed, timed out, CLI exit with no result, or never started with no retry left: **void_system**, the key free, relaunched; hand void: yes |
| steward runs per version (`steward_max_per_version` 12) | the count of `steward` keys on the version | `_gate` | every killed or failed entry counted toward the 12 | void entries are not in the book, so not counted |
| fixer once per road-back item (`fix_cap_usd`) | `mods.<Mod>.fixers` | `_gate` (`fixer_spent`) | as for the steward | as for the steward |
| road back (`caused_by`) | `mods.<Mod>.road_back` | `_road_back`, `holder_spent`, `stop_tickets` | a route steward killed at launch still opened it | it goes with its steward's entry (hand or system void) |
| holder one run per set of road-back items | `mods.<Mod>.holder_road_back`, `pilot_launches` | `holder_spent` | a killed holder "ended with them still open": no second automatic try; one that never started: spent | **void_system** (never started, or killed; a hand `pilot-launch` too, `pilot_launches` scanned since RIMMANDRAKE_CLOSE_VOID_GAPS_REVIEW_FOUND_SIX_MORE); hand void: yes |
| offline builder progress (one builder per refused set; a run that did not reduce the refusals stops the mod) | `mods.<Mod>.launches`, `last_run`, `stopped` | `decide`, `progressed` | a killed builder was judged as not progressing: **stopped** | a killed builder's launch and `last_run` are void_system: never judged. A `stopped` already written before this change is not undone (`clear` it) |
| launch tries (`launch_tries` 3, `launch_failed`, `launch_retry`) | `tries` on each entry | `retriable`, `_gate`, `spent_tries` | the retry count of never-started launches; at 3 the trial was spent | it is the system-fault count: at 3 the entry is void_system, the faults are counted, and `system_fault` stops the mod without spending the trial |
| certificate rerun (one zero-token rerun per build key) and red-decider builder | `mods.<Mod>.cert_rerun`, `cert_red` | `cert_rerun_decide`, `cert_red_decide`, `_clear` | a dead run spent it | hand void: yes. Automatic: a red-decider builder whose `launches` entry is **void_system** takes `cert_red` out with it (and back on a heal); a rerun with no result of its own `RERUN_MAX_S` after its start (killed or timed out; its unit has no detached record) is started again within `launch_tries` (RIMMANDRAKE_CLOSE_VOID_GAPS_REVIEW_FOUND_SIX_MORE) |
| ceiling releases | `mods.<Mod>.releases_used` (release id → unit) | `ceiling_gate` | a launch that died spent the release | a **void_system** run's release is given back (`run_void.sync_system`; the Conductor's decision of 2026-11-18 1:05 PM PST, delegated, he may overrule); a run that heals spends it again; a hand void leaves it spent (e391a63413) |
| stage spend ceiling (`stage_ceiling_usd` 100) | run records' `cost_usd`, `run_spend.json` | `stage_spent`, `offline_usd`, `ceiling_gate`, `reserve_refused` | dead runs' dollars counted (a run with no measured dollars at its cap); a killed run's dollars were refunded once when they alone held its retry | **off the ceiling** by his card of 2026-11-18 11:06 AM PST ("Does not count"): `void_units` (standing hand voids, the mod's `voided` list, runs killed before a result) are taken out; shown apart as `void_usd`; the killed-run refund is retired with it |

## The Designer and the coverage judge (`design/concepts/<Mod>/stage.json`)

| counter | stored | read by | BEFORE | AFTER |
|---|---|---|---|---|
| the granted coverage look (`coverage_release_granted` → one `coverage_releases` entry, `final`) | stage.json | `coverage_judge.release`, `grant_waits`, `stop_reason`, autonomy `chain_owed`, `coverage_stopped` | a chain run that applied the grant spent it whatever became of the run | a hand void of the run un-applies it: the grant stands again, the stop and block it lifted are back (`sync_stage`, in `designer_stage.load_state` and `maturation_autonomy.designer_state`); unvoid re-applies it |
| judge looks (`JUDGE_RUNS_MAX` 4, `NOT_COVERED_LIMIT`, `MALFORMED_LIMIT`, `JUDGE_SPEND_MAX`) | `coverage_rounds`, plus legacy rounds rebuilt from `budget.charges` refs | `coverage_judge.rounds`, `stop_reason`, `_caps` | every round counts, an errored or malformed one too; an unmeasured judge counts at the p90 | a hand-voided judge's round is out, as before. Automatic (ad019a7e19): a round whose call died (`error_kind` "system": no answer, a timeout, output that is no result; before error_kind, the error text) is **void_system**: no run, look, spend or malformed verdict; `rounds(voids=True)` shows it apart; `JUDGE_FAULT_LIMIT` (8) since the last release stop judging as a system fault. A judge that answered with no well-formed verdict counts |
| Designer retries per stage | `history` `retry` rows, `results` `rejected` | `designer_stage` packet (retries), two rejections in a row | a killed stage run's "no result.json" rejection counts | hand void moves them out; automatic (4fe2af3f9e): a rejection whose every reason is "no result.json" and whose run left no claude result of its own (stopped at run_max_s, or the unit ended; an unreadable output file is not "no result") is **void_system** (`role_launch.void_cause`, `designer_stage.void_rejection`): no retry, no rejection for parking, none remembered |
| Designer stage budget (`budget.cap`) | `budget.charges` | `over_budget` | spend | **unchanged** (true spend); void refs listed in `voided.spend_refs` |
| Designer loop ceiling (`LOOP_CEILING_FACTOR` x the cap, then park) | `budget.charges` since `loop_start` | `designer_stage.loop_ceiling`, `ceiling_crossed_at` | a void run's or void judge's charge counted, and a void judge round could start the loop | no void charge counts toward the ceiling, its crossing or its start (`designer_stage.loop_void_refs`: hand voids, void_system judge rounds and readers, void_system Designer rejections); the void spend is shown apart in the ceiling's line (RIMMANDRAKE_CLOSE_VOID_GAPS_REVIEW_FOUND_SIX_MORE) |
| Designer chain cap (`chain_max_per_day`, `role_launch.CHAIN_MAX_PER_DAY` 8) | Dispatcher `state.json` `roles.<Designer>.chain_day` ("day concept" → count) | `role_launch.chain_ask`, `maturation_autonomy.designer_chain` | a killed chain counts | each chained launch is recorded against its unit (`chain_units`); a void_system end gives that chain back and chains the stage again; 3 void runs on one concept in a day stop as `role:<Role>:system_fault`, nothing chained (4fe2af3f9e); a run-now consumed with no launch because it expired, the pipeline is paused, the owner holds it or the role is off gives its chain back, and the sweep asks nothing while the role is off; a gate refusal (the stage machine, band, caps, ops reading) keeps its chain as the brake on an ask-and-refuse loop (RIMMANDRAKE_CLOSE_VOID_GAPS_REVIEW_FOUND_SIX_MORE) |

## Counters outside the books

| counter | stored | BEFORE and AFTER |
|---|---|---|
| refusal-contract counters (per-item refusals, per-family malformed, alarm `trips`, `FAMILY_ALL_WINDOW`) | `refusal_contract` counters and alarms files | a malformed verdict left by a dead re-ask is not submitted (`contract.submitted` False, the round void_system), so it counts no malformed verdict (ad019a7e19); a judge's own malformed verdict counts |
| calibration tallies (`coverage_calibration`, `art_calibration`, refusal_contract `status`) | their stores | built from planted cases; a killed calibration run writes no tally `[guess ~70%]`; not reached by a void |
| Test Pilot streak (3 non-pass runs in a row, `testpilot_route.streaks`) | ledger `verify` events | a verify recorded `fail` because of a harness fault is hand-voided by its run name (`maturation_dispatch.py void "<ID>/run-N@<config>" --why ...`) and is in no streak (`testpilot_route.judge`, 8d746c2519); no automatic class: a harness fault is not visible in a verify event |
| advance refusals (`maturation.ADVANCE_FAMILY`) | refusal_contract | a gate's verdict, not a run: a killed run spends none `[guess ~80%]` |

## What is UNBUILT, and where it is filed

Item RIMMANDRAKE_EXTEND_VOID_TO_JUDGE_DESIGNER_AND_PILOT_COUNTERS. A void's children are the Designer runs and judges its run launched, by the `parent` a run-now from a detached run
records (`role_launch.with_parent`, into the run, stage.json and the judge's round; da889bc937); an entry written before
that, with no parent, still goes by time.
The six gaps a Codex review of that item named were checked one by one in RIMMANDRAKE_CLOSE_VOID_GAPS_REVIEW_FOUND_SIX_MORE,
each against a test run on the base first (`design/specs/2026-11-19-void-counters/boundary.md`, tests
`src/RimMandrake/rimflow/selftest_void_counters.py`). Not real: an "unknown" result is a run with its own answer, and
`ledger_runs` is bookkeeping, not a counter. Not handled, by the owner's card of 2026-11-19 (a rare failure): a void
mark on stage.json that itself raises leaves that one rejection counted, said by its alarm. The rest are built (rows
above).
