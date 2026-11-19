# RIMMANDRAKE_HARDEN_PIPELINE_WHERE_HANDS_CLEANED_UP

## ruling

Owner, 2026-11-15 (this item's ledger events, OWNER shard): "Fix the process wherever it didn't work, ok? Make the
pipeline better, don't keep cleaning up after it and leaving it alone". Then: "the Pipeline fixes its own issues
once detected ... it's a ticket to file then do yourself." The rule is written once, in
`design/RimMandrake/standing_rulings.md` §The pipeline fixes its own defects (ef0eff1e54); spec
`design/specs/2026-11-13-maturation-pipeline.md` §5 and every launched brief point at it (`maturation.SELF_FIX_RULE`).

## needs-conductor lines

Every kind of line the Dispatch tick (`maturation_dispatch.py` decide / decide_blind / decide_ingame / execute) and its
autonomy layer (`maturation_autonomy.py`) still write as "Needs Conductor", or as a pause, measured 2026-11-15 on
455fb5eec8. Each one is marked SELF-FIXES NOW or STILL NEEDS A HAND, with the reason.

### Self-fixes now

- **ready / hand_step / exit_met / exit_not_met**: SELF-FIXES NOW. The steward (`maturation_autonomy.STEWARD_ON`)
  launches on them within max_live and the caps. It advances, confirms, or files each failed line down its road
  back.
- **blind or in-game launch that never started on a transient fault** (git lock, item not yet on origin):
  SELF-FIXES NOW. The same item is retried up to launch_tries (0258fe7637,
  RIMMANDRAKE_RETRY_JUDGE_LAUNCH_GIT_LOCK_SPENT_THE_CYCLE).
- **a run killed before it wrote a result** (an account switch): SELF-FIXES NOW. The tick finishes the run, returns
  its clone and relaunches (ca68431994, RIMMANDRAKE_RETRY_RUN_KILLED_BY_ACCOUNT_SWITCH_CYCLE_KEPT).
- **Stage 3 (offline build) launch that never started on a transient fault**: SELF-FIXES NOW (455fb5eec8,
  RIMMANDRAKE_RETRY_STAGE_THREE_LAUNCH_TRANSIENT_FAULT_NOT_STOPPED). Before this fix, a lock while filing stopped the mod
  for good, and the line was lifted only by a hand `clear`.
- **a helper clone whose selftests crash on `contracts`**: SELF-FIXES NOW. The package is in the default cone
  (RIMMANDRAKE_ADD_CONTRACTS_TO_SCRATCH_CLONE_DEFAULT_CONE). It was worked around by hand before.
- **stopped, written on a steward or fixer run**: SELF-FIXES NOW
  (RIMMANDRAKE_EXEMPT_STEWARD_RUNS_FROM_BUILDER_PROGRESS_STOP). The progress test judged any run that was live on an
  offline-build mod, so Graffiti's preflight steward got "stopped, 33 -> 33". It now judges only builders, and a stop
  that was already written that way lifts itself on the next tick. The reading's `stop_lifted` shows the lift.

- **launch_failed, not transient**: SELF-FIXES NOW (c269d7039e, RIMMANDRAKE_RETRY_FAILED_LAUNCH_ONCE_CODE_CHANGES). The
  failed launch records the pipeline code it failed on and is tried again once that code changes, within launch_tries.
  A launch that fails three times, or on code that never changes, still needs a hand.
- **stopped: a builder run ended and resolved none of its refused bars**: SELF-FIXES NOW (9eac6686d3,
  RIMMANDRAKE_TRIAGE_STALLED_BUILDER_GRAFFITI_WAITED_ON_HELPERS). One steward run reads the builder's run and files
  the cause as named items that fixers build; the stop lifts when a refused bar is resolved. Never a second builder at
  the same refusals, never a second steward for the same stall: then it is a hand's. A run first seen with no refused
  bars writes no stop at all (c269d7039e, RIMMANDRAKE_SKIP_BUILDER_STOP_ON_ZERO_REFUSED_BARS).
- **ceiling, when a killed run's dollars are what holds its own retry**: SELF-FIXES NOW (c269d7039e,
  RIMMANDRAKE_REFUND_KILLED_RUN_DOLLARS_AT_THE_CEILING). Those dollars come back once, as an automatic release his
  daily digest reads, unless the stage reads DIVERGING.
- **designer_chain_cap, on a stage not chained that day**: SELF-FIXES NOW (2bcce1d526,
  RIMMANDRAKE_PASS_FORWARD_STAGES_PAST_DESIGNER_CHAIN_CAP). The cap brakes loops; forward stages chain up to twice it.
- **cycle_unfinished** (a blind cycle's record with no exit block, nothing live): SELF-FIXES NOW
  (RIMMANDRAKE_COMPLETE_UNFINISHED_BLIND_CYCLE_RECORD_BY_STEWARD). One steward run completes the record from its
  files (a record gap), or says exactly which lanes are missing; then it is a hand's.

### Still needs a hand

- **ceiling, any other case** (the stage's dollars plus the next cap pass stage_ceiling_usd): STILL NEEDS A HAND. It
  is a spend bar he set by card; money past it is released by `maturation_dispatch.py release`, the Conductor's call.
- **blind (run records, test table or a stage's state unreadable)**: STILL NEEDS A HAND. The cause is a broken file
  or a blind instrument, and which one it is takes reading. Writing past it would launch on a blind reading.
- **visit_unfinished** (an in-game visit's record with no exit block, nothing live): STILL NEEDS A HAND. The game the
  dead run left needs a look, and a steward never takes the bridge.
- **hand_run_seen** (a hand-launched run worked here and wrote no record): STILL NEEDS A HAND. It is a person's
  run, and what it left is theirs to read.
- **auto_spent** (the visit's automatic run is spent): STILL NEEDS A HAND. The owner set one automatic run per visit.
  More is his bar to change.
- **blind_off / ingame_off / steward_off / disabled**: STILL NEEDS A HAND. They are settings the Conductor holds; the
  in-game launches stay off until the first visit is run by hand (spec §2 item 10: done by hand first, then automated).
- **cycle_limit** (three blind cycles): STILL NEEDS A HAND. The spec's bar is that the Conductor decides.
- **steward_spent / fixer_spent**: STILL NEEDS A HAND. The automatic runs are spent within their caps.
- **coverage PAUSED** (coverage judging stopped, REFUSAL_NOTHING_COULD_EVER_PASS): STILL NEEDS A HAND. Only
  `coverage_judge.py release` un-pauses it, on the owner's word. The paused mod's fix ticket is another helper's
  item.
- **a killed run whose return KEPT its clone**: STILL NEEDS A HAND. The kept clone may hold unpublished work, and
  returning it would throw that away. A program cannot tell work worth keeping.
- **designer_blocked / designer_unreadable / seed_refused**, and **designer_chain_cap** on a stage already chained that
  day or past twice the cap: STILL NEEDS A HAND. The Designer stays the owner's, and a return past the cap is a loop.
- **held / blocked** (a Conductor hold, a non-build refusal): not a defect. The hold is the Conductor's own act.

## children

- RIMMANDRAKE_RETRY_STAGE_THREE_LAUNCH_TRANSIENT_FAULT_NOT_STOPPED: fixed 455fb5eec8. Unrun live: it proves itself
  the first time a Stage 3 filing meets a lock.
- RIMMANDRAKE_ADD_CONTRACTS_TO_SCRATCH_CLONE_DEFAULT_CONE: fixed cb0affc152. Only clones made after it get the wider
  cone.
- RIMMANDRAKE_EXEMPT_STEWARD_RUNS_FROM_BUILDER_PROGRESS_STOP: fixed, see its close sha. The next tick lifts Graffiti's
  live false stop.

## every hand act is now recorded

RIMMANDRAKE_BUILD_CONDUCTOR_INTERVENTIONS_INTO_PIPELINE_ITSELF (census
`design/RimMandrake/pipeline_interventions_census_2026-11-15.md`): the tick records each hand act on the pipeline
(`maturation_hands.py list`); one with no follow-up item or census row for a day raises
OPS_MATURATION_HAND_ACT_UNFOLDED.
