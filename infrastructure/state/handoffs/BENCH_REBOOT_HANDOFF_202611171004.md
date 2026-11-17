# BENCH_REBOOT_HANDOFF_202611171004 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202611170706`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

The owner is on his phone (last typed about 11:36 PM PST 2026-11-16, "I'm on my phone. Do 1"). ONE question is staged and waiting for his "yes": the art judge's facing-size rule. He was sent three picture strips (Peeper r2, Durrok r2, live Gawpsack) and asked "After you look at those, are you ready for a question card?". Send NO card until he says yes. The card asks why he purged Peeper r2: if not size, the size sentence comes out of rule C2 of `design/RimMandrake/art_judge_brief.md`; if size, which of his picks (Durrok r2 1.45x, DecayDrake r2 1.40x, Gawpsack live) he would now refuse. TWO FIRST ACTS, as before: (1) re-arm the question watcher (Monitor, 30 min, on `questions.md` in `D:\ClaudeWork\rimmandrake\showings\RIMMANDRAKE_INVENT_SLACK_LIVE_END_GREEN_BY_THIN_MARGIN\` and on Conductor log lines DETACHED RUN ENDED / RESCUE PROPOSED / DESIGNER WINDOW; anchor the log grep to lines that START with a timestamp and exclude `restart:BENCH`, because an escalation line quotes the watcher's own command and matches itself). (2) When the resumed Slack Fable run ends (rm-detached-bench-rimmandrake-lay-slack-close-fittings-twe-1794902099, session 0f924521-1b2a-4e01-8482-87e58a50c67f), read every open or untested line of its report as work: resume it if any case is open, else RELEASE the Conductor hold on GimmeSomeSlack (stages 6, 3, 4+5).

## What the owner should see

Told to him this window (phone): the goodbye restart defect and its fix (a6279cfd2dc3); his four judge calls landed and the coverage judge reads CALIBRATED 8 of 8 (e7d577eb, 14065a48); the four-question card stamp fix (d354ed250e96); two games side by side proven live (b541e5dc39); the Slack close fittings (a2de43e4bdd1) and the resume; the art calibration 10 of 13 and the stuck size rule.
Still waiting for him, in value order:
- The facing-size card (above), after his "yes".
- One look at the desktop: a lone conduit cell beside a battery hides a small turn of spare cord under the battery art; `D:\ClaudeWork\rimmandrake\showings\RIMMANDRAKE_INVENT_SLACK_LIVE_END_GREEN_BY_THIN_MARGIN\placements_laid.png`, second panel.
- The card on bars that pin numbers (Graffiti; Pyrelands six; three proposed Pyrelands bars; black rain fills moats and tanks in 0.1.0 or not). Next in his list after the judge calls.
- Ticket sweeps `D:\ClaudeWork\rimmandrake\conductor\ticket_sweep_gss_20261116.md` and `ticket_sweep_pyrelands_20261116.md`, and the polish-list proposal.
- Which mod Fable builds from the start (the experiment against Opus 5.5).
- Pyrelands live week passed both bars (worst day 3.5 percent of open ground, grass 87.8 percent on day 7, measured by the run); eight pictures in `D:\ClaudeWork\rimmandrake\showings\RIMMANDRAKE_RUN_PYRELANDS_WEEK_SKY_FREE_NEVER_ONCE_SEEN\` NOT looked at by this window; the comb-lanes finding is filed (RIMMANDRAKE_WIDEN_PYRE_BURN_FRONT_COMB_LANES_NOT_SWATHE).
- The visit 1 full-mod-list walk was probably spoiled by the two-games defect and has not been re-run; it waits for the hold release.

## What is half-done, and where it stops

- `RIMMANDRAKE_LAY_SLACK_CLOSE_FITTINGS_TWENTY_ONE_UNLAID` — item closed at a2de43e4bdd1, but the same Fable was RESUMED on it at 11:56 PM PST with the whole-mod order (brief `D:\ClaudeWork\rimmandrake\conductor\brief_slack_resume_whole_mod.md`); live, holds the driver lock; latest state: box-arm refusals 713 to 57 of 1,723 crowded worlds, unpublished; NEXT: read its DETACHED RUN ENDED report; resume if any case is open, else release the hold
- `RIMMANDRAKE_RELEASE_SLACK_PIPELINE_HOLD_WHEN_FABLE_ENDS` — owed, open; the hold stands; NEXT: when the resumed run ends with no open case, append the three `kind release` lines to design/concepts/GimmeSomeSlack/journal.md, ./publish, check `maturation.py next GimmeSomeSlack`, close `--no-code` naming the sha
- `RIMMANDRAKE_RECONCILE_ART_BRIEF_SIZE_RULE_THREE_PICKS_REFUSED` — D4 reworded and landed 2a65767e; C2 cannot be reworded (Peeper r2 purged at 1.45x, Durrok r2 picked at 1.45x); waits on his card; NEXT: on his "yes" send the card, record his answer by card, launch the criteria fixer with it, then rerun `calibrate --model art_judge_brief`
- `RIMMANDRAKE_BUILD_ART_BRIEF_CALIBRATION_NOTHING_TO_RUN` — the check exists (12ee3bf48472), brief reads FAILED 10 of 13 (11 with the fixed scorer, not rerun); NEXT: close it when the rerun after the C2 answer reads CALIBRATED
- `RIMMANDRAKE_FREE_HANDOFF_GATE_FROM_DETACHED_RUNS_DRIVER_LOCK` — filed this window: handoff.py refused "BRIDGE still held by BENCH" on a detached run's driver lock (pid 2360170, the Slack Fable), the same class seat_restart had before a6279cfd2dc3; this handoff was written with --force; NEXT: read its fixer's ended line, or launch one if none ran
- `RIMMANDRAKE_DRIVE_GIMMESOMESLACK_IN_GAME_VISIT_ONE` — visit 1 recorded, not passed; NEXT: leave it to the pipeline after the hold release
- `RIMMANDRAKE_WEIGH_TOKENS_BY_MODEL_OPUS_INPUT_UNIT` — code landed 381db58f59, still open; NEXT: name the criterion (the model-weights selftest) and close it
- `RIMMANDRAKE_ENACT_INVENTION_WHEN_BARS_CONFLICT_GRADIENT_TOO_EASY` — judge half landed by RIMMANDRAKE_LAND_JUDGE_PROMPT_CALLS_FOUR_ANSWERED_BY_CARD (closed); offline and in-game tester prompt changes are still proposals; NEXT: bring him the tester proposals from role_prompt_upgrades_20261116.md sections 2b and 2c, or close if he declines
- `RIMMANDRAKE_PIN_FABLE_ALIAS_TO_FIVE_TWO_FOR_SPAWNS` — untouched; NEXT: measure one spawn's model id from its transcript
- `RIMMANDRAKE_UNSTICK_DISPATCH_BLIND_CYCLES_WAITED_SIX_HOURS` — two ceiling releases still unfolded; NEXT: file the RAISE FIRST item and fold both acts before the one-day alarm
- `RIMMANDRAKE_RELEASE_CONTAGION_JUDGE_ONE_LOOK_HIS_WORD_GIVEN` — parked under his Contagion hold; NEXT: leave it parked until he lifts the hold

## Traps learned

- The question watcher matched itself: a `restart:BENCH:held` escalation line quotes the watcher's command, which contains the words the watcher greps for. Anchor the grep to the line's leading timestamp and exclude `restart:BENCH`. (filed: lessons)
- The watcher itself holds the context backstop restart (a background command of the window). Before HANDOFF READY, stop it (TaskStop). (filed: lessons, same entry as the line above)
- `rimflow bridge who` and the BRIDGE file read FREE while a detached run held the shared bridge under the seat's name (fixed a6279cfd2dc3); a record written before the fix still holds until the next take. (see: the fixer's lesson published 07d0b100b2dd)
- A closing report that never mentions an order is an order not read: the Slack Fable ended on the close fittings without touching the 10:41 PM whole-mod order. Check the report against the order, not against the item. (filed: lessons)

## Closed since the last handoff (9)

- `RIMMANDRAKE_FREE_GOODBYE_RESTART_HELD_BY_DETACHED_HELPERS_LOCK` — a6279cfd2dc3
- `RIMMANDRAKE_KEEP_BRIDGE_HEARTBEAT_TO_HOLDER_CLONE_ONLY` — a6279cfd2dc3
- `RIMMANDRAKE_SPLIT_CARD_STAMP_FOUR_QUESTIONS_OVERFLOW_LEDGER_LINE` — d354ed250e96
- `RIMMANDRAKE_LAY_SLACK_CLOSE_FITTINGS_TWENTY_ONE_UNLAID` — a2de43e4bdd1
- `RIMMANDRAKE_LAUNCH_BOTH_GAMES_STEAM_REFUSES_A_BESIDE_B` — b541e5dc39c2
- `RIMMANDRAKE_LAND_JUDGE_PROMPT_CALLS_FOUR_ANSWERED_BY_CARD` — 14065a48104785ad719f80acb5d7f151a401d0c4
- `RIMMANDRAKE_TEACH_CONTRACT_CHECK_PICTURES_ARE_NOT_TEXT` — 12ee3bf48472
- `RIMMANDRAKE_SEAL_PILOT_GUARD_TEST_FROM_THE_LIVE_GAME` — 12ee3bf48472
- `RIMMANDRAKE_FIX_REAR_CHECK_NEGATED_FLIP_READ_AS_ROTATION` — 49d7f196affe4d91df89d6544f0380092408f3f4

## Filed and still open (2) — the next seat's queue

- `RIMMANDRAKE_BUILD_ART_BRIEF_CALIBRATION_NOTHING_TO_RUN` — Build a runnable calibration check for the art judge brief (its registry row has none, so it stays UNTESTED)
- `RIMMANDRAKE_RECONCILE_ART_BRIEF_SIZE_RULE_THREE_PICKS_REFUSED` — Art judge brief calibration FAILED 10/13: C2 and D4 refuse three pictures he picked

## Commits

```
8856b2392a seat_dirt: land 1 safe path(s) left in the seat clone (conversation records, filed item prose)
3c39e0e0fa ledger: RUNNER ingest of 0 testq job(s)
11ef6444eb designer cleanse: LongShade proposal (proposed)
a43ba6e9c4 ledger: RUNNER ingest of 0 testq job(s)
e8bd46e616 ledger: DISPATCHER notes (1)
7f1f03a504 ledger: DISPATCHER notes (1)
fc49fc1181 seat_dirt: land 1 safe path(s) left in the seat clone (conversation records, filed item prose)
6e34f3ddd2 ledger: RUNNER ingest of 0 testq job(s)
ce8a12e81e designer cleanse: LanternDeeps review (refused-after-second-look)
b7d516bd34 designer cleanse: Greentide review (refused-after-second-look)
cac18fc911 designer cleanse: CrackedLands review (refused-after-second-look)
0bd7a119d5 ledger: RUNNER ingest of 0 testq job(s)
522bda973a designer cleanse: LanternDeeps proposal (proposed)
81afa6b009 designer cleanse: BlueDesert review (refused-after-second-look)
aa4b0ded8b designer cleanse: Abyss review (refused-after-second-look)
e80b55865c designer cleanse: CrackedLands proposal (proposed)
5424d9190a designer cleanse: Greentide proposal (proposed)
bf31c16dd2 designer cleanse: Abyss proposal (proposed)
87f52524fe designer cleanse: BlueDesert proposal (proposed)
de6a1d1eee seat_dirt: land 1 safe path(s) left in the seat clone (conversation records, filed item prose)
... 97 more: git log --oneline 0e765ea9d2..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : DOWN  → corrected to UP, measured now
- Bridge: for     Gimme Some Slack: reproduce visit 1's reds (dead end missing, fresh builder differs, box leads off slope) on the current build

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M infrastructure/state/ledger/events/BENCH.jsonl   mine: this window's ledger events, published with this handoff
```

