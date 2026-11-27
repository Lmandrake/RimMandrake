# Scheduled infrastructure: one row per piece (2026-11-27)

Item `RIMMANDRAKE_READY_ALL_SCHEDULED_INFRASTRUCTURE_HE_SAID_MAX_SPEED`. The owner's order of about 9:57 AM PST
2026-11-27: *"We need to complete all currently scheduled infrastructure at max speed to that we can truly test the
system as intended. Do not lose any work. Park only at natural pipeline breakpoints."* This run makes each piece ready
for the ticket lane (`src/RimMandrake/rimflow/list_dispatch.py`). It builds no piece.

Sources, each read once: the nine owed items that the brief names; block 11 of
`infrastructure/state/CONDUCTOR_GOALS.md`; the plan pages under `design/specs/` of the last 14 days
(`2026-11-22-coordination-every-agent-must-use/plan.md`, `2026-11-23-sort-old-list-tickets/plan.md`,
`2026-11-24-monitors-consolidated/plan.md`, `2026-11-19-plain-english-rule-docs/batch_plan.md`).

States: **a run works it** · **ready for the ticket lane** · **waits on a named condition** · **needs the Conductor** ·
**done**.

## The pieces

| piece | ticket or tickets | state | the act of this run |
|---|---|---|---|
| Delete the old account engine: split the account-end actuator out of `switching_plan.py`, then delete its decision half | `RIMMANDRAKE_SPLIT_ACTUATOR_OUT_SO_OLD_ENGINE_CAN_GO_AFTER_FIRST_REAL_SWITCH` | ready for the ticket lane | Its gate held: the plan switched lukas to system at 7:51 AM PST 2026-11-27 (plan log `do=switch`, rev 4), `./acct driver` reads new, `./acct status` reads SteveDesktop "on system; nothing is refused". Lifted the Conductor's wait (`unwait`, what held written on it, 6e49e1e42b) and ran `list_dispatch.py clear` for its one Work run. |
| Cut the three pilot mods over to their mod ledgers | `RIMMANDRAKE_CUTOVER_PILOT_MODS_TO_LEDGER_SAME_DAY` | waits on a named condition: the study of 2026-11-29 (`RIMMANDRAKE_STUDY_WHAT_ONE_WEEK_OF_MODS_TAUGHT_ON_NOV_TWENTY_NINE`) answers the cutover question, by the Conductor's ruling of 2026-11-24; its wait ends 2026-11-30 | None on the ticket: its home is `pipeline:maturation`, which the run on `RIMMANDRAKE_SWEEP_PIPELINE_TICKETS_HE_ORDERED_ONE_MOD_ONLY` sweeps. My TAKEN note is corrected on the item. The lane row reads `adopt_too_heavy` (its acceptance script runs over 120 s); the wait ends first, so no lighter check is owed today. |
| Carry out the GPT streamline review of 2026-11-20 | `RIMMANDRAKE_ENACT_GPT_STREAMLINE_REVIEW_TRUST_NOT_SUSPICION` | waits on a named condition: the owner's ruling on a rule-file length ceiling (`RIMMANDRAKE_REVIEW_RULE_FILE_LENGTH_CEILING_HE_LEFT_OFF`, deferred by him to about 2026-12-05); batches one and two and the ten contradictions are done (`design/specs/2026-11-23-streamline-review-state/state.md`) | None on the ticket: its home is `pipeline:docs` (the sweep run's). My TAKEN note is corrected on the item. |
| Make the pipeline ready for Wrecked Machines | `RIMMANDRAKE_READY_PIPELINE_FOR_WRECKED_MACHINES_HE_HOLDS_GO` | a run works it: his go of 2026-11-26 is done; the Fable build run `rm-detached-bench-rimmandrake-autobuild-wreckedmachines-se-1795802462` (item `RIMMANDRAKE_AUTOBUILD_WRECKEDMACHINES_SEVEN_BARS_LEFT_RUN_TWO`) is live; the mod parks at its Stage 3 exit by block 12 | None: a mod ticket; this run changes the wait of no mod ticket. |
| Work bundles, all seven parts, and the first real bundle (block 11, goal 1) | `RIMMANDRAKE_BATCH_ONE_MODS_OPEN_WORK_INTO_ONE_RUN_PIPELINE_SPLITS_PER_TICKET`, `RIMMANDRAKE_RELAUNCH_BUNDLE_BUILD_IF_IT_DIES_PROGRAM_SKIPS_DEATHS` | done (01630f9219; 06466f7a67) | Read the closes. |
| Onboarding launches of work bundles (the repair that two pieces below waited for) | `RIMMANDRAKE_REPAIR_ONBOARDING_LAUNCH_SO_BUNDLES_FILL_MEDIAN_ONE` | waits on a named condition: the repair landed (bd590ba35f); only part 3 is left, one program-launched onboarding bundle of 5 or more after the repair, and no pipeline home holds 5 ready old tickets until the sweep run or the Conductor frees some; its wait ends 2026-12-03 | None. The tickets that this run files below give the pipeline homes new ready members. |
| SteveDesktop works from its SSD; one kept check tree per publish (block 11, goal 2) | `RIMMANDRAKE_MOVE_STEVEDESKTOP_CLONES_TO_SSD_LINUX_DRIVE_SITS_ON_HARD_DISK`, `RIMMANDRAKE_REUSE_TREECHECK_TREE_EACH_PUBLISH_WRITES_THREE_GIG` | done (4997a6d33b, live `rm-ssd-check.timer`; 46d2b57a56) | Read the closes. |
| Stale leftovers of retired eras removed on both machines (block 11, goal 4) | `RIMMANDRAKE_CLEAN_STALE_LOCKS_AND_LEFTOVERS_OF_RETIRED_ERAS` | done (573be9c027) | Read the close. |
| Plan pages of the last 14 days: the List Pipeline plan (steps 1 to 4), the old-ticket sort (30 batches), the consolidated pages (4 owed tickets), the plain-English batches | `RIMMANDRAKE_SORT_OLD_TICKETS_BEFORE_SHAPE_971_WAIT_UNNAMED` and its 30 batch items, `RIMMANDRAKE_DRAW_STEVE_SERVICES_ON_FLEETNOW_JSON_HAS_THEM`, `RIMMANDRAKE_CLEAR_RETIRED_ALARMS_OPS_MEMORY_OPEN_SINCE_NOV`, `RIMMANDRAKE_DIAGNOSE_RUNP_TIMERS_PILING_ON_IDLE_DISPATCHER`, `RIMMANDRAKE_RESTYLE_FLEET_NOW_IN_BROWN_LIKE_ITS_PEERS`, `RIMMANDRAKE_LAUNCH_REMAINING_PLAIN_ENGLISH_BATCHES_ELEVEN_LEFT` | done or superseded; step 5 of the List Pipeline plan is the study of 2026-11-29 (the Conductor's, not machinery to build); step 6 is "later, each after its evidence" | Read each state. |

## Calls for the Conductor

(none yet)

## What this run did not test

(filled at the end)
