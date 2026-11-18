# Every counter a Maturation Pipeline run can consume, and whether a system death spends it (2026-11-18)

Item RIMMANDRAKE_VOID_SYSTEM_KILLED_RUNS_NO_TRIAL_SPENT. The owner, 2026-11-18 ~10:30 AM PST, about Graffiti: *"Ensure
it didn't use up it's turns, trials, whatever... I will not accept ANY system that pointlessly expends such statistical
measurements based on failed system calls or behavior. You know that. Fix the system such that it's easy to indicate
this to it. And NEVER tell me "I can't that's frozen" or "it's a write only ledger" or bullshit like that."*

The rule in code is `src/RimMandrake/rimflow/run_void.py` (selftest `selftest_run_void.py`). A run is **void** two
ways: a **hand void** (`maturation_dispatch.py void <unit>... | --item ID | --mod MOD --since TIME --why "..."
[--owner-said "..."]`, reversed by `unvoid`; listed by `voids`), or **void_system**, classed automatically when its run
record shows a cause the machine can see (killed with no result JSON, its unit dead with its finish never run, a
finished run with no result JSON, a launch that never started and has no retry left). A void run's book entries are
moved to the mod's `voided` list in `state.json`, never deleted; a Designer `stage.json` is made to agree by
`run_void.sync_stage`. System faults are counted on the mod's own `system_faults`, never on a trial; at 3 since the last
`clear` the mod reads `system_fault` (alarm `OPS_MATURATION_SYSTEM_FAULT_LOOP`) and nothing launches on it.

"Before" is the code at 1caaeb7ba4's parent (origin/main 2026-11-18 ~10:30 AM PST); "after" is f93b15709a and later.
Where a reading was measured it says `[measured]`; a guess carries its confidence.

## The dispatch books (`state.json`, `<dispatch state dir>/maturation/state.json`)

| counter | stored | read by | a system death BEFORE | AFTER |
|---|---|---|---|---|
| blind cycles per visit (`blind_auto_cycles_per_visit` 3; `maturation.CYCLE_LIMIT` 3) | `mods.<Mod>.blind_auto` (visit_id, cycle, unit, failed, tries, killed_before) | `decide_blind` (`ours` → `auto_spent`, `mine` → `stopped`), `retriable`, `reserve_refused`, `_clear` | a kill was retried up to `launch_tries` (3) and then **stopped**, spent; a never-started launch on a non-transient fault: **"stopped, never a second automatic try"**, spent; a transient one retried 3 then stopped; a run that ended with no record: stopped. Only a hand `clear` gave it back | kills still resume a half-written cycle (up to 3); past that, and every never-started launch with no retry left, and a finished run with no result JSON: **void_system**, the cycle unspent, the next tick relaunches; 3 faults → `system_fault`. Hand void: yes |
| in-game runs per visit (`ingame_auto_runs_per_visit` 1) | `mods.<Mod>.ingame_auto` | `decide_ingame`, `retriable`, `_clear` | as for blind | as for blind |
| hand runs seen on a cycle or visit (`hand_run_seen`) | recomputed each tick from the run records (`add_blind` `blind_runs`, `add_ingame` `ingame_runs`) | `decide_blind`, `decide_ingame` | a killed hand run was already excluded (`killed`); a hand run that ended with no record stopped the mod | a hand-voided run is excluded too |
| killed-run retries | recomputed (`killed_runs`) | `retriable`, `reap_wait` | — | a hand-voided run is no kill to retry |
| steward once per state key | `mods.<Mod>.steward` (key → item, unit, failed, tries) | `maturation_autonomy._gate` (`steward_spent`), `releasable`, `autonomy_book`, `_clear` | a killed steward read "ended and the state has not moved": **steward_spent**, the mod PAUSED; a non-transient launch failure: spent | killed / no result JSON / never started with no retry left: **void_system**, the key free, relaunched; hand void: yes |
| steward runs per version (`steward_max_per_version` 12) | the count of `steward` keys on the version | `_gate` | every killed or failed entry counted toward the 12 | void entries are not in the book, so not counted |
| fixer once per road-back item (`fix_cap_usd`) | `mods.<Mod>.fixers` | `_gate` (`fixer_spent`) | as for the steward | as for the steward |
| road back (`caused_by`) | `mods.<Mod>.road_back` | `_road_back`, `holder_spent`, `stop_tickets` | a route steward killed at launch still opened it | it goes with its steward's entry (hand or system void) |
| holder one run per set of road-back items | `mods.<Mod>.holder_road_back`, `pilot_launches` | `holder_spent` | a killed holder "ended with them still open": no second automatic try; one that never started: spent | **void_system** (never started, or killed); hand void: yes |
| offline builder progress (one builder per refused set; a run that did not reduce the refusals stops the mod) | `mods.<Mod>.launches`, `last_run`, `stopped` | `decide`, `progressed` | a killed builder was judged as not progressing: **stopped** | a killed builder's launch and `last_run` are void_system: never judged. A `stopped` already written before this change is not undone (`clear` it) |
| launch tries (`launch_tries` 3, `launch_failed`, `launch_retry`) | `tries` on each entry | `retriable`, `_gate`, `spent_tries` | the retry count of never-started launches; at 3 the trial was spent | it is the system-fault count: at 3 the entry is void_system, the faults are counted, and `system_fault` stops the mod without spending the trial |
| certificate rerun (one zero-token rerun per build key) and red-decider builder | `mods.<Mod>.cert_rerun`, `cert_red` | `cert_rerun_decide`, `cert_red_decide`, `_clear` | a dead run spent it | hand void: yes. Automatic: **UNBUILT** (the rerun is a zero-token systemd unit with no detached run record) |
| ceiling releases | `mods.<Mod>.releases_used` (release id → unit) | `ceiling_gate` | a launch that died spent the release | hand void and void_system: the release is unspent again |
| stage spend ceiling (`stage_ceiling_usd` 100) | run records' `cost_usd`, `run_spend.json` | `stage_spent`, `ceiling_gate`, `reserve_refused` | dead runs' dollars count (a run with no measured dollars counts at its cap) | **unchanged**: void spend is true spend, shown apart in `status` and on the page as "void spend". Whether it should stop counting toward the ceiling is the owner's call (proposal in the item's report) |

## The Designer and the coverage judge (`design/concepts/<Mod>/stage.json`)

| counter | stored | read by | BEFORE | AFTER |
|---|---|---|---|---|
| the granted coverage look (`coverage_release_granted` → one `coverage_releases` entry, `final`) | stage.json | `coverage_judge.release`, `grant_waits`, `stop_reason`, autonomy `chain_owed`, `coverage_stopped` | a chain run that applied the grant spent it whatever became of the run | a hand void of the run un-applies it: the grant stands again, the stop and block it lifted are back (`sync_stage`, in `designer_stage.load_state` and `maturation_autonomy.designer_state`); unvoid re-applies it |
| judge looks (`JUDGE_RUNS_MAX` 4, `NOT_COVERED_LIMIT`, `MALFORMED_LIMIT`, `JUDGE_SPEND_MAX`) | `coverage_rounds`, plus legacy rounds rebuilt from `budget.charges` refs | `coverage_judge.rounds`, `stop_reason`, `_caps` | every round counts, an errored or malformed one too; an unmeasured judge counts at the p90 | a hand-voided judge's round is out and its charge rebuilds no round; its `coverage_verdict.json` is kept as `coverage_verdict.void.<judge>.json` and the verdict before it put back (`swap_verdict`), and a void judge's verdict is never `prior_verdict`. Automatic class for an errored judge round: **UNBUILT** |
| Designer retries per stage | `history` `retry` rows, `results` `rejected` | `designer_stage` packet (retries), two rejections in a row | a killed stage run's "no result.json" rejection counts | hand void moves them out; automatic: **UNBUILT** |
| Designer stage budget (`budget.cap`) | `budget.charges` | `over_budget` | spend | **unchanged** (true spend); void refs listed in `voided.spend_refs` |
| Designer chain cap (`chain_max_per_day`, `role_launch.CHAIN_MAX_PER_DAY` 8) | Dispatcher `state.json` `roles.<Designer>.chain_day` ("day concept" → count) | `role_launch.chain_ask`, `maturation_autonomy.designer_chain` | a killed chain counts | **UNBUILT**: the count has no unit to void. Graffiti today reads `{}` (no chain counted) `[measured 2026-11-18 ~10:50 AM PST]` |

## Counters outside the books

| counter | stored | BEFORE and AFTER |
|---|---|---|
| refusal-contract counters (per-item refusals, per-family malformed, alarm `trips`, `FAMILY_ALL_WINDOW`) | `refusal_contract` counters and alarms files | a dead judge call's malformed verdict counts as malformed. **UNBUILT**, filed |
| calibration tallies (`coverage_calibration`, `art_calibration`, refusal_contract `status`) | their stores | built from planted cases; a killed calibration run writes no tally `[guess ~70%]`; not reached by a void |
| Test Pilot streak (3 non-pass runs in a row, `testpilot_route.streaks`) | ledger `verify` events | a killed run usually records no verify `[guess ~70%]`; a verify recorded `fail` because of a harness fault counts. **UNBUILT**: no void for a verify event, filed |
| advance refusals (`maturation.ADVANCE_FAMILY`) | refusal_contract | a gate's verdict, not a run: a killed run spends none `[guess ~80%]` |

## What is UNBUILT, and where it is filed

The automatic class for errored coverage-judge rounds, Designer stage-run rejections, refusal-contract malformed counts,
the Designer chain count, certificate reruns, and a void for a Test Pilot verify event are filed as one item,
RIMMANDRAKE_EXTEND_VOID_TO_JUDGE_DESIGNER_AND_PILOT_COUNTERS, with its acceptance test.
