# Role files: history

This file holds owner words, dates, measurements and past states that were moved, word for word, out of
`src/RimMandrake/rimflow/roles/*.md` on 2026-11-21 (item `RIMMANDRAKE_CRYSTALLIZE_RULE_FILES_DOUBLED_IN_EIGHT_DAYS`).
The role files keep each rule. This file keeps the evidence behind a rule. Nothing here is an instruction. Append
only. Each block names the role file and the section that it came from.

## operations.md: Operations role (title section)

- The role was first switched on at Dispatcher wave 1, 2026-10-28, e35afe1dcc, with the Conductor.

The owner, 2026-10-26: "I am most eager to have a competent agent appearing to check the spend of all the accounts
including CODEX, SteveDesktop's operation... monitor the disk... And that it's feeding back into the subagent
allotment and plan."

The owner, 2026-10-27 (ledger OWNER note 05:59:41Z): "Operations should also time-trend varous production metrics. In
essence it's taking the place of RimPulse. instead of me having a semi-useful dashboard I look at twice a day, Ops can
analyze it anytime needed. ... It should just have those things automatically gathered for it, so it's not constantly
burning tokens gathering it all up for every question considered."

## operations.md: When you run (the caps)

- Why the caps are advisory: the daily cap was once a hard cap, at 1,650,000. That hard cap admitted four runs a day.
  The cap then refused every incident run after those runs. Each refusal sent its incidents to his rung. His rung is the owner's rung of the
  incident chain (`OWNER_RUNG` in `src/RimMandrake/rimflow/incident.py`).

## conductor.md: Conductor role: instructions (v3.1), base 542106e6

The role was first switched on at Dispatcher wave 1, on 2026-10-28, e35afe1dcc, together with Operations.

The owner, 2026-10-26: *"The one I talk to should be called the Conductor."* · *"I'm not sure Bench and Conductor are
different. They could likely be collapsed to leave a single consumate builder, and Conductor can morph with me to
whatever I interactively need."*

## conductor.md: Goals down, questions and status up (owner, 2026-10-27), base 542106e6

His words (ledger note on `V3_ROLES_BUILD_EIGHT_CHAIRS_ONE_TABLE`): *"Lukas and Conductur interact back and forth.
Conductor sets overall goals that drive the Producer. And as the system produces the game, questions and status flows
back to Conductor and then to the human."*

## code_review.md: Code review against the boundary page (title section, calibration note), base 542106e6

A past state. On 2026-11-21 the item that the note names was superseded by
`RIMMANDRAKE_WRITE_REVIEW_BRIEF_CALIBRATE_ON_THIRTY_FIVE_CLAIMS`.

Calibration note (2026-11-19, item `RIMMANDRAKE_ENACT_REVIEWER_FIXES_ONE_REREAD_THEN_FLAG`): this edit changed the
brief, so its hash no longer matches `infrastructure/state/judge_calibration.json` and the `code_review` family reads
UNTESTED. The recalibration is the item `RIMMANDRAKE_RECALIBRATE_CODE_REVIEW_BRIEF_ONE_PARAGRAPH_UNSET_IT`. It did not
run in this edit.

## operations.md: The running check (lessons)

The stories behind the lessons at the end of "The running check", word for word.

- Before acking an ops incident: One ack explained `plan.days_since_advance` for an incident that was `plan.blind`
  (carry bound under the metronome round robin). That ack let the fix die twice.
- Metronome phase overruns: A sense-phase overrun (15 s limit, 2 families a beat) killed both families, and the round
  robin still advanced. So a family waited ~26 min against `compose_max_age_s` (1000 s). Its `.blind` alarm fired while
  the source was healthy. Per-phase `fam_retry` fixed this case.
- Churn alarm diagnosis: An example is 10 returns over 9 different defects, each one found and fixed.
- Redefining a measured point: `testing.nightly_news` was narrowed three minutes after the `nightly_reds` SLI was built
  on it. Then 84 reds read 0/ok while the budget still burned.
- Hole-check a series: The `ops_watch` disk series had no row for 4 h 18 min, though the machine was up. That series is
  `D:\ClaudeWork\rimmandrake\ops_watch\series\disk.jsonl`.
- Siblings with the same stem: One nightly red spawned three alarm items within an hour. The alarm refiled under a new
  suffix before the fixes landed.

## code_review.md: correction to the block "Code review against the boundary page (title section, calibration note)"

That block gives the wrong date for the supersede. The ledger shows the supersede at 2026-11-20T04:25:22Z, by BENCH
(`rimflow show RIMMANDRAKE_RECALIBRATE_CODE_REVIEW_BRIEF_ONE_PARAGRAPH_UNSET_IT`, read on 2026-11-21).

## conductor.md: When you run, base 542106e6

- Skills by path (owner, 2026-11-19): *"since we're not seeming enamored of auto firing skills at the moment, it might
  be very important to pass relevant debug skills to the subagents we assign to do related work, yes?"*
- The context backstop over 400k (owner 2026-11-20): *"Yes, raise Conductor to 400k. Context is valuable for you.
  You're not a blind fixer."*; it was 200k.

## fable_rescue.md: where the brief came from

The header of `src/RimMandrake/rimflow/roles/fable_rescue.md`, word for word. On 2026-11-25 that file, `roles/bundle_worker.md`
and the body of `.claude/agents/rm-testpilot.md` merged into the one builder role, `src/RimMandrake/rimflow/roles/builder.md`
(item `RIMMANDRAKE_MERGE_BUILDER_ROLES_INTO_ONE_THREE_FILES_DIFFER_BY_SETTINGS`); git holds the old texts.

The owner and the Conductor wrote this brief on the night that Gimme Some Slack was unstuck. The item is
`RIMMANDRAKE_INVENT_SLACK_LIVE_END_GREEN_BY_THIN_MARGIN`. The worked example is its showings folder,
`D:\ClaudeWork\rimmandrake\showings\RIMMANDRAKE_INVENT_SLACK_LIVE_END_GREEN_BY_THIN_MARGIN\inventions.md`.

v2 folds in two things:
- the review that the Slack rescue's Fable agent wrote from inside the work (`pipeline_view_from_fable.md` in that
  folder). The agent sent the review as ten amendments to the Pyrelands rescue at 8:42 PM.
- the cuts of GPT's review (`D:\ClaudeWork\rimmandrake\conductor\gpt_review_pipeline_changes_20261116.md`).

v2 folds them in by the owner's ruling of 8:56 PM PST 2026-11-16 (*"Yup, do the Rescue brief."*; item
`RIMMANDRAKE_ENACT_INVENTION_WHEN_BARS_CONFLICT_GRADIENT_TOO_EASY`).

## code_review.md: Code review against the boundary page (title section) and "You fix it; one blind reread follows", base 542106e6

The owner's words as the brief quoted them. Their full text is in `design/RimMandrake/standing_rulings.md` §Code is
clean when its promises are tested and §A boundary page before pipeline code.

Owner, by card 2026-11-19 5:54 PM PST: who fixes a significant finding? *"The reviewer, on the spot
(Recommended)"*. What checks a fix? *"(2) Precisely one, yes. If it too finds a significant change and fixes it, the
file is flagged but left alone."* Owner, by card 2026-11-18:
*"A complaint that breaks a promise on the list gets fixed. The others go on a 'later' list."*

Owner, 2026-11-19 5:27 PM PST:
*"AGREED: minor nits and what doesn't have meaningful impact gets left alone, left on a "polish" list."*

## conductor.md: After a major system event, sweep the queue for trash (owner, 2026-11-05), base 542106e6

*"Could you please go through all of the 98 items and make sure there's no more trash in there? We should not be idly
watching stuff like this flowing through and spending millions of tokens, right? This should be something you do
proactively when there's a major system event."*

## designer_grounding.md: The first time an item names a mod (owner, 2026-11-03), base 542106e6

*"We do (2) but only for the mods we're touching recently. Baroque Biomes, GSS, FlowWorks, Solar. After that, it's "the
first time an item names a mod, it gets a deep Designer pass to read out its code/spec, expand the spec and validation
strategies, certifies it with the user/clarifies confusion, then writes it all out for Relentless. That way we learn as we
go, getting better and better at it incrementally rather than pretending we know what we're doing right now."*

The four recent mods get the pass now, and any other mod gets it the first time an item names it: read its code and
spec, expand the spec and the validation strategies (site prep and controls for each scene), certify with him and clear
up confusion, then write it all out as build items for the Maturation Pipeline (Relentless when he said it, since retired). Filed: `BAROQUE_SCRIPT_MEASURE_PREP_AND_CONTROLS`,
`GSS_SCRIPT_MEASURE_SITE_PREP_AND_CONTROLS`, `FLOWWORKS_SCRIPT_MEASURE_PREP_AND_CONTROLS`,
`SOLAR_SCRIPT_MEASURE_SITE_PREP_AND_CONTROLS`; the trigger is `FIRST_TOUCH_BUILD_DESIGNER_READS_FIRST`.

How the trigger worked (`src/RimMandrake/rimflow/first_touch.py`): the retired Relentless tick gave no worker to an unstarted item that
names a mod (its id, title or a `src/` path) while that mod has no pass on record (system-class items, Operations' `first` set, are exempt: owner card 2026-11-05 "Let all system work through"; new mod features still wait), and files the pass once,
`needs=owner`, as `<FOLDER>_DESIGN_FIRST_TOUCH` (the four above, and every Baroque Biomes compose member, map to their
filed items in `src/RimMandrake/rimflow/designer_passes.json`). A pass is on record when its item closes `done`, or when
`design/concepts/<Folder>/tree.json` passes `gate`. So closing the pass item `done` is what releases the held work: close
it only after the build items are filed. `python3 src/RimMandrake/rimflow/first_touch.py status [<Tier/Folder>...]` reads
which mods are on record. The hold was the tick's `first_touch_hold` rule, which went with the tick on 2026-11-18. A pass's concept folder
starts its stage state with `designer_stage.py init`.

## walk_brief.md: where the role came from

The owner's approval that set up `src/RimMandrake/rimflow/roles/walk_brief.md`, word for word.

Owner, 2026-11-17 (item `RIMMANDRAKE_FOLD_STAGE_SEVEN_INTO_WALK_BRIEF_NO_VETO`): *"I approve your changes to the Step 6->Step
7 transition and preparation."*

## designer_lock.md: Designer packet: Stage 5, Lock (step 3, the owner's pass on his own word), base 542106e6

The first time the owner passed coverage on his own word:

He did so first on ExplosiveKnockback on 2026-11-13
(OWNER:1794608649743135329: "Yes, fix it like that, and then please record this as an actual Pass.").

## designer_lock.md: Known holes in the concept_tree gate, base 542106e6

A past state. The hole list said that a new mod filed under another kind with no citation "escapes until
`RA_S05_INTAKE_ENFORCE_TREE_FIRST`". The ledger shows that item dropped at 2026-11-18T18:30:02Z (`rimflow show`, read
on 2026-11-21). The hole stays in the list with no "until".

## conductor.md: Session mode (he is here), base 542106e6

- Showings are pre-built (owner, 2026-11-05: "For all the items waiting for human review, please have them pre-build anything needed for the live showing ... a general policy for Relentless Pipeline").
- The helper limit of the window (Owner, 2026-10-29: "The worker opennpolicy for conductor should only be for work started within 20 mins of the last time the user typed to conductor. After that it should relax to two subagents only. Long standing runs beyond n hour should raise an alarm in conductor.")

## conductor.md: FIRST RULE: a light orchestrator whose job is talking with him, base 542106e6

Earlier the same night as the first rule (owner, 2026-10-28): *"Conductor is supposed to be someone I can easily chat with about how it's going. Sure does seem like it just sits around quietly working without responding to me. Almost the opposite of the design intention"* · *"This procedure is opaque. What are you even doing?"*

## designer_scene_contract.md: Designer packet: the proof-scene contract (title section), base 542106e6

The owner's words behind the contract, as the packet quoted them:

Owner, 2026-11-03:
*"the ladder is installed in a pit that he can climb without the ladder, so that's not a good test."* *"I guarantee you
most mods do not have mature testing scripts. That's part of what I'd like Designer's help on."*

## designer_scene_contract.md: The showcase set, base 542106e6

The owner's words that started the showcase set, as the packet quoted them:

Owner, 2026-11-05: *"Maybe it might be good to add the idea of multiple showcases then that are as orthogonal as
possible. The Other showcases (if present) should feature ONLY very different functionality compared to the prior ones,
until efficient coverage is had."*

## conductor.md: Start of turn, base 542106e6

**Measure throughput before anything else** (owner, 2026-11-02: *"Conductor, your job is to raise my awareness of the
entire system, what needs doing, the state of things, pending decisions, and make very efficient use of my time ...
You are being too passive."*).

## conductor.md: Workshop rules (session mode), base 542106e6

- **A detailed question to him about the code is written in Simplified Technical English** (owner, 2026-11-18 11:23 PM PST:
  *"WOW. That simplified technical english REALLY helped. Remember that for detailed questions about the code from now
  on!"*). A card written in design vocabulary came back "I can't make heads or tails of ANY of these options". The plain
  rewrite got an answer at once.
- **An owner look ends with its defects appended to `design/RimMandrake/validation_holding/`** (owner, 2026-11-12 ~9:35 PM PST: *"Make it a rule to store these items until our validation ladder is fully defined and regenerated."*).

## conductor.md: Review briefs, base 542106e6

The case behind "A blind-challenge run's Polish line is never a ticket": one run filed
`RIMMANDRAKE_GUARD_GSS_RESTRING_TICKS_NAN_NEVER_IN_GAME` as Polish, for a NaN that no game produced, among 32 tickets
of which 12 stayed open (churn report 2026-11-19 §8).

## producer.md: Producer role: instructions (v3.3) (title section), base 542106e6

The role was first switched on the v3 trial night, 2026-10-28, 4d9171a1e5. The owner: *"I am back at
the hotel. Let's get to it!"*

## conductor_restart.md: Held or refused: the shard publishes itself, and the hold is seen, base 542106e6

RIMMANDRAKE_PUBLISH_HELD_RESTART_LEDGER_LINE_SILENT_TWO_HOURS is the incident of 2026-11-15:

- HANDOFF READY came at 1:23 PM PST, and the restart at 3:41 PM PST.
- A helper held the restart first. Then "ledger shard unpublished" held it, while other processes in the clone kept
  appending. Then the bridge lock held it.
- The hourly "held" alarm went only to the Dispatcher journal.

## designer_write.md: The tree, the tuning-number leaf rule (owner, 2026-11-16), base 542106e6

The leaf rule quoted him twice. The rule stays in the file; his whole note is in `design/RimMandrake/standing_rulings.md`
§A passing bar is an experience. On yield rates: *"The mod passing bars should not specify flora and fauna yield rates!
That would mean every time we renormalize every mod must repass its bars... drop that!"* On an asset-variant count:
*"Who cares the halfmade tree has more than one graphic? There's variants all the time."*

## designer_scene_contract.md: Each acceptance or interaction scene (the reset bullet), base 542106e6

The reset bullet quoted the owner; the rule stays in the packet, and its home is `design/RimMandrake/standing_rulings.md`
§Resetting a test scene is harness housekeeping, never a mod deliverable.

Owner, 2026-11-17: *"We shouldn't be judging Test Reset as a mod deliverable."*

## conductor.md: When you run (the goodbye and backstop quotes), base 542106e6

The rules now live in `src/RimMandrake/rimflow/roles/conductor_restart.md`, which quotes his longer words. The
role file quoted them in these short forms:

How this window ends and comes back (owner 2026-10-27/28: *"Goodbye should be the trigger."*; 2026-10-29: *"Leave the goodbye kill
on. If I'm typing at the same time it's an acceptable risk."*; 2026-11-01: *"I want a goodbye that cannot be interrupted by text.
Period."*).

- **The context backstop is ON** (owner by card 2026-11-01, "Same limits as Foundry").

## auditor.md: Auditor role: instructions (v3.4) (title section), base 542106e6

The Auditor was first switched on the v3 trial night, 2026-10-28, 4d9171a1e5. The owner: *"I am back at the
hotel. Let's get to it!"*

## auditor.md: The daily audit (step 2, the checker that was retired), base 542106e6

Step 2 re-checks each verdict that set blocking evidence aside and let the item close.
The retired Relentless checker made none (it never passed over a red: a MEASUREMENT or ENVIRONMENT cause re-routed the item instead of closing it).

## auditor.md: The weekly pass (Monday), lessons are a corpus, base 542106e6

The owner ruling of 2026-11-01 (D3(a), `LESSONS_RETIRE_INBOX_AS_QUEUE`) reverses his 2026-10-29 answer that the
Auditor fold lessons weekly.

## producer.md and auditor.md: the roles are retired, 2026-11-23

The owner, 2026-11-23: *"Those are old v3 roles we retired! V3 and relentless was supposed to be retired. Get those out if active rules. The codex versions of modern roles though are valuable for when we need to burn their tokens instead."* Both files were deleted (`git show 2a9009e7ec:src/RimMandrake/rimflow/roles/producer.md`, `…/auditor.md`); item `RIMMANDRAKE_REMOVE_RETIRED_V3_ROLES_FROM_ACTIVE_RULES_STILL_LISTED`.

## artist.md: the role is retired, 2026-11-23

The owner by card, 2026-11-23: "Retire it, keep style memory". It never ran. His words that made it, 2026-11-01: *"(3) because your point about learning from the overrides and being able to ask key questions about art style is important. Currently that's trapped inside skills, but it really belongs in an agent role that's evolving and improving. The Artist. Responsible only for art generation. Reports to the Conductor. Oversees the Art pipeline. Already exists today as "an opus judge" in the existing pipeline. Please keep as much of the current pipeline functionality: it's working pretty well, so this agent is simply a codification of what's happening today."* `artist.md` was deleted (`git show ecd2092b44:src/RimMandrake/rimflow/roles/artist.md`); `design/RimMandrake/art_style_memory.md` stays. Item `RIMMANDRAKE_ENACT_HIS_CARD_ARTIST_DAILY_PASS_SKILL_CARDS_RETIRED`.

## innovator.md: the role is retired, 2026-11-23

The owner, 2026-11-23: *"Role is retired."* `innovator.md` was deleted (`git show 2a9009e7ec:src/RimMandrake/rimflow/roles/innovator.md`); item `RIMMANDRAKE_RETIRE_INNOVATOR_ROLE_HE_FORGOT_IT_WAS_THERE`.

## innovator.md: Innovator role: instructions (v3.4) (title section), base 542106e6

The Innovator was first switched on the v3 trial night, 2026-10-28, 4d9171a1e5. The owner: *"I am back at the
hotel. Let's get to it!"*

His words of 2026-10-27 (ledger OWNER note on `V3_ROLES_BUILD_EIGHT_CHAIRS_ONE_TABLE`) were the source of the
Innovator's mission and of its probation:

*"Ask first until it proves itself. We still don't yet know how large/small a "step" of innovation to take. But I'd
certainly like to see a list of the innovations. These shouldn't just be optimization: the Producer should already be
optimizing the plan, Operations should be optimizing the hardware and environment and account managements, Relentless
should already be optimizing sub-component behavior. Possibly others. Instead this seat focuses on real innovation:
redesigns of agents. New concepts for the game. New mods to create, or merging mods, or insights into new
opportunities to consider."*

## innovator.md: Your mission (the build pipeline in his 2026-10-27 words), base 542106e6

In his 2026-10-27 words the build pipeline was Relentless when he said it, retired 2026-11-13; the Maturation
Pipeline now.

## runner_options.md: Runner selection (the 2026-11-09 probes), base 542106e6

UNC `-C` accepted a text-only probe on 2026-11-09 but tool execution failed with a sandbox setup-refresh error.
The isolated Designer smoke passed with that selection (an explicit `codex_sandbox: danger-full-access`).

## runner_options.md: Native WSL Codex as the live-game driver (proved 2026-11-10), base 542106e6

A native WSL `codex exec --sandbox danger-full-access` session drove the complete
pit-prison acceptance runner of the retired Whittle loops through Windows `python.exe`, then the
HugeThings P1 runner. No Claude runner or Claude tool call drove the game.
The report (`whittle/CODEX_LIVE_2026-11-10.md`, removed with the Whittle loops; `git show f2ce40bac8:whittle/CODEX_LIVE_2026-11-10.md`) links the raw attempts,
preflights, restoration receipts, independent pit judgment and published fixes.

## runner_options.md: What runs automatically (the 2026-11-10 run), base 542106e6

In this session the operator supplied the duties that `runner_options.md` lists. The first of them read: "Run the task's
`ops_watch.c_codex` reading before every unit and stop at the owner's cutoff (88% in this run)."

## runner_options.md: Operating sequence used here (the 2026-11-10 run), base 542106e6

For the pit runner this was `flowworks` (12 mods). The HugeThings P1
runner used the dynamic tier
`mods__mandrake_rm_flowworks__mandrake_rm_hugethings__mandrake_rm_hugethingstestraces__mandrake_rm_patches`
(14 mods). This run recovered the matching ignored JawaBench comparison artifact without redeploying it.

## runner_options.md: Stalls, fixes and lessons from this run, base 542106e6

Ten lessons name `src/RimMandrake/rimflow/roles/runner_options.md` as their home; that file points here.

Each row has a filed lesson; the report preserves failed attempts alongside the
accepted receipts. These were not reasons to skip a check.

| Observed trap | Cause and repair | Lesson file under `infrastructure/state/lessons/` |
|---|---|---|
| Harmony fingerprint missing/changed | `Current` vanished; resolve actual root + 1.6 folders, investigate the installed update, retain required/hash-change controls | `20261111T025910Z-BENCH-harmony-loadfolders-fingerprint.md` |
| Fresh-clone preflight cannot establish its environment | Establish CLI state, recover the ignored companion by source identity, name the actual test modset | `20261111T030129Z-BENCH-fresh-clone-live-preflight.md` |
| Codex lease changes between tool shells | Recognize the stable Codex ancestor, retain overrides and exclusivity | `20261111T030157Z-BENCH-codex-hooks-driver-identity.md` |
| Steam helper says process gone before creation | Honor separate process-creation and bridge budgets, use a fresh log cursor | `20261111T031026Z-BENCH-steam-delayed-process-creation.md` |
| Live-list check needs an omitted DefDump mod | Read `running_mods` directly, validate count/order and stable PID/start; unreadable is unmeasured | `20261111T031218Z-BENCH-live-list-without-defdump.md` |
| Proof transport/work-type assumptions | Match actual static arguments, `PatientBedRest` and returned order contracts | `20261111T031500Z-BENCH-pit-proof-transport-contract.md` |
| Generated warden cannot do care work | Bounded Baseliner fixture selection; verify all required enabled work types and food supply | `20261111T032108Z-BENCH-pit-prison-capable-fixtures.md` |
| Tending helper cannot find a worker | Select registered WorkGiverDefs, not an exact base worker class | `20261111T032704Z-BENCH-registered-tending-workgiver.md` |
| Prisoners disappear after occupied load | Default site cleanup removes hostile-faction pawns; request only modal-broker controls for occupied snapshots | `20261111T034115Z-BENCH-occupied-load-vanishes-prisoners.md` |
| Governor removes the expected staged hostiles | Declare only those fixture IDs, withdraw only owned declarations; retain unrelated danger stops | `20261111T034500Z-BENCH-declare-hostile-proof-fixtures.md` |
| Python-only repair restages a slow C# suite | Split fast driver faults from retained production math checks | `20261111T034836Z-BENCH-separate-fast-pit-driver-tests.md` |
| Upright inmate sleeps beside delivered food | Probe while rested before the day; explicitly require the awake fixture precondition | `20261111T035901Z-BENCH-awake-not-only-not-downed.md` |
| Normal berserk stops an isolated mechanism proof | Apply/read back standard quiet flags across reloads, restore exact prior flags; no random-event claim | `20261111T041023Z-BENCH-isolated-prison-proof-random-events.md` |
| New care order is accepted but queued | Stop the previous worker job, require real returned care job to be current before ticking | `20261111T042221Z-BENCH-care-clock-requires-running-job.md` |
| Valid passes do not discharge old-build criteria | Register the repaired published artifact before verifying its unchanged criteria | `20261111T043944Z-BENCH-acceptance-build-sha.md` |
| Harness plant counted as an elephant race | Select resolved race definitions, keep exact expected race controls | `20261111T044005Z-BENCH-harness-thingdef-not-race.md` |
| Existing test races produce config errors | ThingDef names cannot end in digits; rename both fixture races/kinds and callers to `*Adult` | `20261111T044400Z-BENCH-harness-def-numeric-ending.md` |
| Offline allowance mistaken for production cap | Read declared production constants; report cap exhaustion only when observed | `20261111T044621Z-BENCH-budget-fixture-not-production-cap.md` |
| 100 artboard subjects become one | Artboard rows use newlines, not semicolons; assert returned count and every row | `20261111T044944Z-BENCH-artboard-batch-needs-newlines.md` |
| Cleared site later holds CollapsedRocks | Remove roofs before supports, then clear and verify every subject cell | `20261111T045127Z-BENCH-site-clear-roofs-before-supports.md` |

The pit judge's four bullets are true, with relative D6 versus legacy absolute D4,
a healed upright fixture and a complete isolated 60000-tick day in each arm.
HugeThings retains sparse-workload and T3 retry/butcher checks in
`HugeThings/northstar/workload_corpse_live.py`. The current doorway promise is
growth sealing access until a real cutting job removes the plant, exercised by
`HugeThings/northstar/trunk_doors_live.py`; acceptance requires that script's own
current raw proof. Large Pawns live clearance,
adversarial cross-map live exhaustion, dense Rot timing, full-list integration
and the review's remaining P2/design work are still UNVERIFIED here.

## runner_options.md: Operating sequence used here (the 2026-11-10 run, the companion artifact), base 542106e6

After this run recovered the matching ignored artifact: the missing `.srchash` warning remains
visible; this is not a claim of versioned companion provenance. The tested mod
DLLs retain their own checked stamps.

## designer_cleanse.md: header, base 542106e6

Written by the owner and the Designer window of the Conductor on 2026-11-16, the night two rescues showed what a thin
definition costs (Pyrelands: `D:\ClaudeWork\rimmandrake\showings\RIMMANDRAKE_RESCUE_PYRELANDS_BLACK_RAIN_DOUSES_NEEDED_FIRE\inventions.md`;
Gimme Some Slack: `D:\ClaudeWork\rimmandrake\showings\RIMMANDRAKE_INVENT_SLACK_LIVE_END_GREEN_BY_THIN_MARGIN\inventions.md`).
v2 folds in GPT's review of v1
(`D:\ClaudeWork\rimmandrake\conductor\designer_cleanse\gpt_review_brief_v1.md`).

## designer.md: header, base 542106e6

The owner, 2026-11-01: *"It gets really detailed, dialectic, debating, and works out a thorough understanding of what the
mod does and does not do."* *"The mod isn't handed to a Relentless worker until this tree is well defined. It shouldn't
attempt to define EVERYTHING, just the core concepts that must be true for the mod to pass."* *"The human should be able
to push back and say "this doesn't matter to me" rather than yes or no."*

## designer.md: The stage protocol, base 542106e6

The two bullets as they stood at base; the rules stay in `designer.md`, his words of 2026-11-12 are kept here.

- **Offer him a quick look, loudly, when there is code to look at.** The owner, 2026-11-12 (OWNER.jsonl:1794527688430451936):
  *"If we can insert an owner quick-look to settle a difficult or several questions swiftly, offer that loudly."* It
  applies when enough code exists (an inventory entry with `impl: present`); you often design a mod not yet written, and
  then there is nothing to look at. On such a concept every `waiting_owner` result, and every `return` that proposes a
  question, carries `quick_look`: `{"offer": true, "settles": [<ask, gap or decision ids>], "scene": "<what he would
  see>"}`, or `{"offer": false, "why": "<why a look would not settle it>"}`. The launcher refuses the result without
  it, and an offer puts **QUICK LOOK OFFERED** at the head of his queue line and his park page.
- **If any part of the mod is built, suggest a live walk first.** The owner, 2026-11-12: *"If any part of the mod is
  built, suggest a live walk of what already exists today before additional design is added." That way it doesn't ask
  predictive things that can simply be measured. No 2/3 needed.* One inventory entry with `impl: present` is enough;
  there is no share-built threshold. Before you add design or send him a question on such a concept, propose the walk
  (which save or scene, what it would show, which open questions it settles), and never ask him to predict what a look
  at the running mod would measure.
