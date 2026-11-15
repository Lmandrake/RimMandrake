# Census: every time the Conductor stepped into the Maturation Pipeline

Item `RIMMANDRAKE_BUILD_CONDUCTOR_INTERVENTIONS_INTO_PIPELINE_ITSELF`. Owner's order, Sun 2026-11-15 about 1:45 PM PST:
"examine every time Conductor intervened in the pipeline so far and ensure that the wisdom of what it had to fix has
been built into the Pipeline itself so that it will do the right thing from now on, NOT merely rely on Conductor/Owner
to notice and request an inspection."

Covers 2026-11-13 (the hand pilot) to 2026-11-15 1:45 PM PST. All times local Pacific.

## How it was counted

Sources read, all of them: the 32 `CONDUCTOR INTERVENED` lines in the six `design/concepts/*/journal.md`; ledger events
since 2026-11-13 (4,042, read through `model.read()`), filtered to hand acts on pipeline work; the Conductor log from
line 2395 on (362 `DETACHED RUN ENDED` lines, the escalation lines); the five `BENCH_REBOOT_HANDOFF_2026111[35]*`
handoffs; the Dispatch step's own books (`state.json`: 2 hand `clear`s; `releases.jsonl`: 1 release); each concept's
`stage.json` coverage releases; the commit history of the pipeline's code; the list of "Needs Conductor" kinds on
`RIMMANDRAKE_HARDEN_PIPELINE_WHERE_HANDS_CLEANED_UP`.

Counts are of acts found in those sources [measured]; a row marked "about" groups acts the sources name without
listing each one. Total: **about 134 interventions, 42 distinct lessons.**

States: **ALREADY BUILT** (the code and its test were read, not the commit message) · **BUILD NOW** (this run builds
it; the sha is written in when it lands) · **CANNOT BE BUILT** (why) · **NEEDS OWNER RULING** (with the evidence).
A row with an open ledger item names it.

## Launching and moving

| lesson | times | what the pipeline did or did not do | what the Conductor did by hand | the judgement applied | state |
|---|---|---|---|---|---|
| Every stage launch was a hand step | 10 (11-14 12:15 PM to 11-15 2:55 AM; all four mods, the Knockback pilot) | No stage had a launcher. All four mods sat at the offline build 6 to 9 hours | Launched each Stage 3 builder, each blind judge, the first in-game visit | A mod with build work owed and nothing live on it gets one capped run | ALREADY BUILT `475fbef600` (builders), `40af31f851` (blind judge), `5f0a9dfca1` + `09dfe2536a` (in-game); `selftest_maturation_dispatch` |
| Advance only after reading the judge's record | 5 (11-15 1:40 to 3:40 AM: Knockback, FlowWorks, Pyrelands, Gimme Some Slack) | Printed "exit met" and waited | Read SUMMARY.md and the rows, then `advance --steward-confirms` | The program's "met" is evidence; the rows must bear it out before a move | ALREADY BUILT `5193f09586` (steward run on `exit_met`), `ef6a38dbb6` (stricter readers). Open beside it: `RIMMANDRAKE_BIND_ADVANCE_TO_EXIT_READINGS` |
| Send each failed line down its road back | 4 (Pyrelands visit 1, Knockback visit 1, Gimme Some Slack cycle 1 twice) | Wrote "NEXT (hand step)" | Read the record, filed each failed or unmeasured line, moved the mod back | One named item per failed line, each with its test, then one fixer each | ALREADY BUILT `5193f09586`, `76c578b59e` (fixers before the next cycle), `10e1fafbf9` (fixed Problems owe a new judge) |
| A neutral fixer checks every judge run before anyone advances | 4 (night of 11-14: Pyrelands, FlowWorks, Knockback cycle 2, Pyrelands visit 1) | Nothing: a judge's record went straight to a hand reading | Launched a reconcile run from a hand template: sort each not-met reason into record gap, criterion flaw or real miss; redo red-then-green proofs for real; read the judge's test edits for weakened assertions | The judge is judged first; a flawed criterion goes to a neutral fixer, never the builder | BUILT NOW `c269d7039e` (`RIMMANDRAKE_CARRY_NIGHT_RECONCILE_RULES_INTO_BRIEFS`): the triage (record gap, criterion flaw, real miss) and the test-edit read are in `STEWARD_RULES`, carried by every steward run; `selftest_maturation_hands.py --only briefs`. UNRUN live until the next cycle or visit ends |
| Re-pin a locked file only for test text or bookkeeping; a changed bar is never re-pinned | 13 (11 re-pins and 2 standing decisions, 11-14 12:15 PM to 11-15 2:08 AM, all four mods) | The changed-files check refused | Decided each: test wording or record-keeping is re-pinned with a journal line saying what changed; a bar's meaning is his | Bar meaning unchanged = re-pin and say so; anything else = his card | BUILT NOW `c269d7039e` (same item): the re-pin rule is in `STEWARD_RULES` |
| Answer the builder's journal questions | about 10 (Knockback 1, 3, 4, 6, 9; Pyrelands 2, 4, 8; FlowWorks stage files) | Builders stopped on a question | Answered in the next brief | Take the obvious answer; ask him only with evidence against it | ALREADY BUILT `5193f09586` (`hand_step` steward) with the Evidence-for-Ask rule in `STEWARD_RULES` |
| His card decisions carried into the record | about 11 (4 bars added, 1 eased, 3 deferrals, 3 picks; 11-14 2:05 to 10:05 PM) | Nothing: bars are his | Wrote his card into the record, tests and pins | None of ours | CANNOT BE BUILT: adding, easing or moving a bar and calling a change Convergent or Divergent are his (`delegation_policy.md` section 2). Built around it: the steward writes the card text and the tick posts it (`3c5464e627`) |
| No builder on a mod while another run edits its code | 2 (FlowWorks held 12:15 PM, released 2:16 PM on 11-14) | Would have launched beside the look-fix builder | Held the stage, released it when that run ended | Two writers in one mod's code collide | ALREADY BUILT for a run whose item names the mod or whose notes cite its concept folder (`maturation_now.item_mod`, read as `live`). CANNOT BE BUILT for a run under an unrelated name: what it edits is unknowable until it publishes |
| Record files that drifted from the truth | 3 (FlowWorks `stage.json` read blocked a day after its lock; two "files disagree" labels) | Showed the stale state | Corrected the files by hand | A lifted block takes its reason with it; a locked change is a re-exam | ALREADY BUILT `b3d6f3104f`, `1b2f800b8d`, `84993ce73e` |
| A run's own "exit met" and the reader's disagreed on format | 4 (three reconciles and `b76c90524a`, 11-15 1:45 to 3:40 AM) | The reader said not met for a missing file or key | Paid a reconcile run each time (one measured 3.0M tokens) | The run that wrote the record can check it with the same reader before it stops | BUILT NOW `c269d7039e` (same item): `maturation.SELF_CHECK_RULE` in both briefs: read your own record with `maturation.py next`, repair form, never a verdict |
| His card recorded on the wrong item | 2 (Pyrelands exam 9:42 PM 11-14; Knockback re-certify 5:14 AM 11-15) | The run refused: his event was on the asking item, not the concept's | Recorded the card `--by-card` on the concept's item, relaunched | His word counts where he gave it | CANNOT BE BUILT in this run: how his certificate is proven is his short list (certifying), and `RIMMANDRAKE_BIND_CERTIFICATE_TO_WHAT_HE_SAW` (decided `876b15fe6a`) rebuilds that code; open item `RIMMANDRAKE_CARRY_OWNER_CERTIFICATE_THROUGH_HIS_OWN_CARD_EDIT` |
| Fix a known defect before spending a judge on the mod | 1 (asked 11-15 11:56 AM) | Unchecked | Promised to check | A judge look on a mod with an open road back is wasted | ALREADY BUILT `76c578b59e` (an open road back gets its fixers first) |
| The Designer fixes gaps it can fix alone | 2 (Graffiti gaps g1, g18; Pyrelands 17 gaps, 12:38 PM 11-15) | Parked on the second refusal | Launched the fix run by hand | A refusal with an attainable fix is work, not a stop | ALREADY BUILT `f9436a1fee`, `5f21e51e44` (a stopped mod's fix tickets get one fixer each). The no-park branch is UNRUN live |
| A failing exam was skipped in silence | 1 (Pyrelands, 11-15 5:25 AM) | The coverage judge skipped; nothing said why | Decided one exam retake | A locked tree that changed owes its exam again | ALREADY BUILT `5f21e51e44` (`exam_retake` steward) |
| A builder that resolved nothing: read the run before anything else | 1 (Graffiti, 2:07 PM 11-15: the 33-bar builder ended "Waiting for the helpers to report", USD 7.15, nothing landed; found while this census was built, before a hand touched it) | Paused: "never a second automatic try" | Would have read the run and filed the cause | The cause is unknown only until someone reads the run: it stopped early, the work is not a builder's, a pipeline defect, or too big for one run | BUILT NOW `9eac6686d3` (`RIMMANDRAKE_TRIAGE_STALLED_BUILDER_GRAFFITI_WAITED_ON_HELPERS`): one steward run reads the builder's run and files the cause as named items that fixers build; never a second steward for the same stall, never a `clear`. Every detached run's brief now says the run ends with its turn. RUN LIVE: the tick launched it on Graffiti at 2:16 PM PST; it read the run, ruled STOPPED EARLY, filed the 33 bars as six fixer items (USD 1.58), and the tick had the first fixer running at 2:27 PM PST, with no hand |
| A new mod's Design Version asked every time | 1 (Graffiti, 11-15 8:02 AM) | Carded him | Carded him | A new mod is 0.1.0 | ALREADY BUILT `6321db9aac`, `ca5dbe81f4` |
| The next mod admitted by hand | 1 (Contagion, 11-15 6:01 AM) | Intake closed until one full pass | Admitted it on his words | His order is the admission | ALREADY BUILT `b38ed346e9`, `f2c998c131` |

## Stops, money and retries

| lesson | times | what the pipeline did or did not do | what the Conductor did by hand | the judgement applied | state |
|---|---|---|---|---|---|
| A launch that never started is not a spent try | 4 (steward 8:12 AM, blind judge 10:27 AM, Stage 3 1:00 PM on 11-15; one `clear` that cleared nothing) | A git lock at publish counted as the visit's one run | `maturation_dispatch.py clear`, then a fix | Nothing was judged, so nothing was spent | ALREADY BUILT `79a4ef9107`, `0258fe7637`, `455fb5eec8`, `c77730479f` |
| A launch that failed on a defect is retried once the fix lands | 2 (FlowWorks in-game spawn refused 11:41 AM; hand `clear` 12:18 PM after `3a1480a047`) | Stopped on `launch_failed` for good | Fixed the cause, then cleared by hand | The stop was about the code; new code deserves one try | BUILT NOW `c269d7039e` (`RIMMANDRAKE_RETRY_FAILED_LAUNCH_ONCE_CODE_CHANGES`): a failed launch records the pipeline code it failed on (the git tree of `src/RimMandrake/rimflow`) and is retried once that code changes, within three tries; Stage 3, blind, in-game, steward and fixer launches alike. UNRUN live until a launch next fails on a defect |
| A run killed from outside is not a failed run | 3 (two judges killed by the account switch 12:00 PM 11-15; the tick paused by hand for the switch) | Counted the cycle spent | Relaunched; filed the fix | A run with no result and a dead unit judged nothing | ALREADY BUILT `ca68431994`. Open, outside the pipeline's tools: `RIMMANDRAKE_DRAIN_LIVE_RUNS_BEFORE_ACCOUNT_SWITCH_NOT_AFTER` (`claude-account` lives outside this repository) |
| A killed run's dollars should not hold the mod at the ceiling | 3 (global raise tried and reverted 9:28 AM; his card raised it to USD 100 at 11:33 AM; Knockback released USD 20 at 12:25 PM) | Paused at the ceiling with the killed cycle's cap charged | Released: "cycle 3 was killed mid-run, not failed; the mod is converging" | Dollars a kill threw away bought no judging; the retry is the same run | BUILT NOW, narrowly, `c269d7039e` (`RIMMANDRAKE_REFUND_KILLED_RUN_DOLLARS_AT_THE_CEILING`): the tick gives back the killed run's own dollars (never more, never twice, never while the stage reads DIVERGING) as a release record marked automatic, which his daily digest reads. UNRUN live until a run is next killed at the ceiling. Any other release past his USD 100 stays the Conductor's hand: CANNOT BE BUILT (a spend bar he set by card) |
| A run that was not a builder is not judged as one | 4 (Graffiti steward, Knockback steward; FlowWorks and Pyrelands hand fix runs read "0 -> 0") | Wrote "stopped, never a second try" on a run that had no refused bars to resolve | `clear`, or left it | Progress is judged only where there was build work | ALREADY BUILT `9b63a203c3` (steward and fixer runs); BUILT NOW `c269d7039e` (`RIMMANDRAKE_SKIP_BUILDER_STOP_ON_ZERO_REFUSED_BARS`): a run seen with 0 refused bars writes no stop, and a stop on an empty set lifts itself (Pyrelands holds one; it lifts when Pyrelands next stands at the offline build with work owed) |
| Coverage judging stopped: fix first, then exactly one look | 7 (Explosive Knockback three times on 11-13 in the pilot; Pyrelands 10:01 PM 11-14, 5:32 and 5:56 AM 11-15; one grant 1:11 PM 11-15: read from each `stage.json`) | Paused on `REFUSAL_NOTHING_COULD_EVER_PASS` | Fixed the gaps, re-pinned, released one look | A release is spent only on a concept the judge can pass | ALREADY BUILT `6a0e5b7a13` (grant takes effect after the fixes close), `0289f8f3a5`, `2826ca6878`. The release word itself: CANNOT BE BUILT (his) |
| A malformed judge verdict cost the look | 1 (11-15 5:43 AM) | Stopped judging | Fixed the tool, released again | Re-ask only the broken rows | ALREADY BUILT `03e2a1a241`, `bf830aa827` |
| A judge that does not converge | 1 (Pyrelands: 14, 5, then 18 gaps) | Nothing measured it | Told him; carded him | New gaps each round is a design question | ALREADY BUILT as a reading `899aeb728f` (DIVERGING is a Needs Conductor line). Whether the gaps belong to this version: CANNOT BE BUILT (his) |
| The Designer's daily chain cap pressed past by hand | 3 (Graffiti stages 3, 4, 5 from 6:23 AM 11-15) | Stopped at 8 chained runs a day | Pressed run-now for each next stage | Each press followed an accepted stage that moved forward; the cap is a brake on loops | BUILT NOW `2bcce1d526` (`RIMMANDRAKE_PASS_FORWARD_STAGES_PAST_DESIGNER_CHAIN_CAP`), a delegated call under Evidence-for-Ask: past the cap a stage not chained today still chains, up to twice the cap (16); a stage chained before is the loop the alarm names. Evidence for not asking: `chain_max_per_day` 8 was set by its builder ("stages 0-5 plus two returns"), not by his card, and each chained run keeps its USD 8 hard stop. His to reverse: one line in `role_launch.chain_ask`. UNRUN live (needs a full day's stage history) |

## Records, money read-outs and the page

| lesson | times | what the pipeline did or did not do | what the Conductor did by hand | the judgement applied | state |
|---|---|---|---|---|---|
| A run that ends well but leaves its item open | 5 (Gimme Some Slack exam item; three hardening items and the Pyrelands ticket closed by hand, `8510908174`) | Said success | Closed the items | A run closes its item or says what is left | ALREADY BUILT `0c28b2596e` (flagged in the log and the page), `2826ca6878` |
| Run dollars read back by hand | 1 and one more owed (`backfill-cost --apply`, 1:05 PM 11-15) | New runs measure themselves (`af092d0349`); older ones wait for a hand | Ran the backfill | The tick can run the same command | BUILT NOW `c269d7039e` (`RIMMANDRAKE_SWEEP_RUN_DOLLARS_AND_DEAD_RUNS_ON_TICK`): the tick runs it every 30 minutes; the first live pass ran 2:09 PM PST 11-15 |
| A dead run whose finish never ran | 2 (11-13 and 11-15) | Read "running" forever | `detached_helper.py finish --unit` | A dead unit with no finish is ended, not live | ALREADY BUILT `ca68431994` (killed blind and in-game runs), `c876bed239` (status says DEAD); BUILT NOW `c269d7039e` (same item): every 30 minutes the tick finishes and returns any run on an advancing mod dead 10 minutes with its finish never run. UNRUN live (none is dead now) |
| The dispatch clone ran 47 commits stale | 1 (11:41 AM to 12:20 PM 11-15) | Ticked on old code, every reading sane | Noticed by a helper | Measure the clone's distance each tick | ALREADY BUILT `c876bed239`, `8586d42006`, alarm `OPS_DISPATCH_CLONE_BEHIND_UNSTICK` |
| A selftest read the shipped knob | 1 (the 9:28 AM ceiling raise turned it red) | Refused the raise | Reverted | A test pins a fixture, not his tunable | ALREADY BUILT for the dispatch tests `948d214cdf`, `78654445c9`; the wider sweep is open: `RIMMANDRAKE_PIN_TUNABLES_OUT_OF_SELFTESTS` |
| Publish checks blind in a sparse clone | 1 | Whole-tree checks failed in pool clones | Worked around | Run tree checks on a full HEAD | ALREADY BUILT (`RIMMANDRAKE_RUN_TREE_CHECKS_ON_FULL_HEAD`, done) |
| Stale labels on the status page | 3 (PyrelandsMechanics, "files disagree", Graffiti on his list) | Showed him work that was not his | Corrected | A label is derived, never typed | ALREADY BUILT `1b2f800b8d`, `c5c259f906`, `19cda97745` |
| The status page made by hand | 1 (11-13 3:11 PM) | None existed | A helper wrote it | A page a program writes cannot go stale by itself | ALREADY BUILT (`maturation_now.py`, regenerated by every tick) |
| Launcher traps on hand launches | 3 (item not yet on origin; the USD 15 default bound; a launch counting against the slots) | Refused or under-budgeted | Published first; passed a budget | The tick files, publishes and budgets its own launches | ALREADY BUILT for the tick (`file_and_publish`, `publish_filed`, `ddc1e44a72`); a hand launch is now itself a recorded hand act (below) |
| Settings turned by hand | 4 (in-game launches on and cap 20 to 30 at 5:30 AM; blind cycles 1 to 3; slots 2 to 4 and ceiling 60 to 100 by his cards) | Nothing | Edited `maturation_dispatch.json` | His caps are his; the first in-game visit is run by hand by the spec | CANNOT BE BUILT (bars and caps set by his card or his spec). Each edit is now a recorded hand act (below) |

## Around the pipeline

| lesson | times | state |
|---|---|---|
| The Conductor window could not see detached runs end, and its log watch blocked its own restart | 2 | ALREADY BUILT `03aefb9edb`; lessons filed. Not pipeline behaviour |
| SteveDesktop's lane paused and proven by hand | 3 | CANNOT BE BUILT: a failing CPU; his BIOS visit (`STEVE_LANE_UNSTICK_BRAKED_UNOWNED_EB2A`) |
| A heap alarm paged on a staged test | 1 | Open: `RIMMANDRAKE_SCOPE_HEAP_GROWTH_TO_ONE_GAME_SIX_LOADS` |
| A Designer run left files in the bench clone that blocked publishing | 1 | Open: `RIMMANDRAKE_LAND_DESIGNER_OWNER_SHARD_ITEMS_WITH_HARVEST` |
| The Designer asked for gaps a later judge had superseded | 1 | Open: `RIMMANDRAKE_CLEAR_PENDING_DECISION_ON_ACCEPT_ROUND_ONE_LINGERS` |
| The tick ran over its beat and its publish was cut | 1 | Open: `RIMMANDRAKE_FIT_DISPATCH_TICK_IN_ITS_BEAT` |

## Not built, and why, in one place

- **His, by the short list** (`delegation_policy.md` section 2), so CANNOT BE BUILT: adding, easing or moving a bar and
  calling a change Convergent or Divergent; the coverage release word; whether a non-converging judge's gaps belong
  to this version; how his certificate is proven; any release past his USD 100 ceiling other than a killed run's own
  dollars; the caps and switches in `maturation_dispatch.json`; SteveDesktop's CPU.
- **Unknowable by a program**: what an unrelated-named run is editing before it publishes; whether a kept clone's
  unpublished work is worth keeping; what a dead in-game run left in the live game.
- **Open items this census did not build**, each already filed: `RIMMANDRAKE_BIND_ADVANCE_TO_EXIT_READINGS`,
  `RIMMANDRAKE_CARRY_OWNER_CERTIFICATE_THROUGH_HIS_OWN_CARD_EDIT`, `RIMMANDRAKE_DRAIN_LIVE_RUNS_BEFORE_ACCOUNT_SWITCH_NOT_AFTER`
  (`claude-account` is outside this repository), `RIMMANDRAKE_PIN_TUNABLES_OUT_OF_SELFTESTS`,
  `RIMMANDRAKE_LAND_DESIGNER_OWNER_SHARD_ITEMS_WITH_HARVEST`, `RIMMANDRAKE_CLEAR_PENDING_DECISION_ON_ACCEPT_ROUND_ONE_LINGERS`,
  `RIMMANDRAKE_FIT_DISPATCH_TICK_IN_ITS_BEAT`, `RIMMANDRAKE_SCOPE_HEAP_GROWTH_TO_ONE_GAME_SIX_LOADS`.
- **NEEDS OWNER RULING**: none. The one candidate, the Designer's daily chain cap, was taken as the obvious answer
  under Evidence-for-Ask and is in his digest as a delegated call.

## The "Needs Conductor" kinds, after this census

The full list with reasons is on `RIMMANDRAKE_HARDEN_PIPELINE_WHERE_HANDS_CLEANED_UP`. What this census changes:

- `launch_failed`, not transient: was STILL NEEDS A HAND; now retried once when the pipeline's code changes (`c269d7039e`).
- `ceiling`: was STILL NEEDS A HAND; now self-released for a killed run's own dollars only (`c269d7039e`); every other release stays a hand.
- `stopped` on a run with no refused bars: no such stop is written; one already written lifts (`c269d7039e`).
- `stopped`, a builder that resolved nothing: was STILL NEEDS A HAND; now one steward run reads the run and files the cause (`9eac6686d3`); a hand only if that steward's filings change nothing.
- `designer_chain_cap`: now only for a stage already chained that day, or past twice the cap (`2bcce1d526`).
- `cycle_unfinished` (a blind cycle's record with no exit block): was STILL NEEDS A HAND; now one steward run completes
  the record from its files or says what judging is missing (`RIMMANDRAKE_COMPLETE_UNFINISHED_BLIND_CYCLE_RECORD_BY_STEWARD`).
- Unchanged and still a hand, each for the reason on the parent item: an unreadable
  input, an unfinished in-game visit, a hand run that wrote no record, the visit's one automatic run, the three-cycle
  limit, the settings, a spent steward or fixer, the coverage release, a kept clone, the Designer's blocks.

## From now on

Built `c269d7039e` (`RIMMANDRAKE_RECORD_HAND_ACTS_TICK_ONLY_SAW_ITS_OWN`), live since the 2:09 PM PST tick of 11-15.

Every applied tick, `src/RimMandrake/rimflow/maturation_hands.py` records each hand act on the pipeline once, in
`D:\ClaudeWork\rimmandrake\dispatcher\maturation\hand_acts.jsonl`: a ceiling release, a `clear`, a coverage
release or grant, a run launched by hand that does a stage's work on an advancing mod (a blind judge, an in-game
driver, a fix on one of the tick's own tickets, a builder the tick did not launch), a stage moved by hand (a move now
carries its run's unit; one without is a hand's), a tick-launched item closed from a window, a changed value in
`maturation_dispatch.json`, and a gap of 15 minutes or more in the tick. `release` and `clear` say so when used.

An act is followed up ("folded") when its reason names an item on the ledger, or by
`python3 src/RimMandrake/rimflow/maturation_hands.py fold <act> --item <ID>` (the item must exist) or
`--census "<row>"` (the row's name must be in a census file like this one). Acts older than this census are folded
by it: the first live pass recorded 9 (1 release, 2 clears, 6 coverage releases), all folded.

An act left a day with neither is a Needs Conductor line naming the act and the command, and the reading's
`hand_acts.overdue` count raises one alarm with a fixed id, `OPS_MATURATION_HAND_ACT_UNFOLDED`
(`ops_watch_rules.json`, key `maturation.hand_acts_overdue`). `maturation_hands.py list` shows the open ones.

Not seen by the tick, and so still a person's to record (`maturation_hands.py record`): a timer paused by hand (the
gap it leaves is seen), and a run stopped by hand.
