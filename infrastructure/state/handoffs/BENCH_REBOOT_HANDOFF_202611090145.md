# BENCH_REBOOT_HANDOFF_202611090145 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202611081918`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
A detached run finishes into the Conductor log, NOT into this window: the old window failed to relay three finished runs for hours (Artisan review 11:50 AM, Pyrelands landing 11:55 AM, GSS method review 1:33 PM) and the owner had to ask. Every turn, grep `DETACHED RUN ENDED` in `/mnt/d/ClaudeWork/rimmandrake/conductor/log.md` since your last look and relay each to him. And never show him a live scene from one zoomed-out desktop capture: a zoomed crop of every connection, judged by a fresh agent, first (he caught GSS strips, wall plugs and solar panels the window had not looked at).

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- GSS round 2 was shown and failed his eye (28 defects, GPT list `D:\ClaudeWork\rimmandrake\gss_sitting\gpt_physical\ANSWER.md`); round 3 is building (pointer below). He is waiting to see it.
- GSS method review with GPT: `design/RimMandrake/gss_cabling_method_review_2026-11-08.md` section 7. One dissent for him to rule: GPT says "one sweep, then one port" must not be absolute; we hold it for the plug-exit kernel. GPT's strongest point: self-certification (the audit excuses bends from the builder's own routes); tie loops must not become an exemption label.
- Artisan card answered 5:20 PM (six `--by-card` notes on RIMMASTER_REDESIGN_ARTISAN_JUDGMENT_NOT_CHECKLIST_GRIND). Owed to him: `D:\ClaudeWork\rimmandrake\conductor\pyrelands_what_got_better_20261108.md` (what got better in the "wasted" passes) for his wasted/worth-it verdict, and the GPT agent-readability refinement result.
- Phone alerts design done: `D:\ClaudeWork\rimmandrake\conductor\phone_alerts_design_20261108.md` (Pushover primary, Todoist urgent backup, outside watchdog); item RIMMASTER_DESIGN_PHONE_ALERTS_THAT_ACTUALLY_RING; put its card to him.
- Pyrelands landed 8fb9f7f2b695. The one selftest failure he asked about: `selftest_natives_drink_own_water.py`, already failing on main's nightly, flags Miasma and Chill water, not Pyrelands (told him).
- He said: "Definitely let that detached run finish, don't kill it for budget." Detached runs carry a hard `--max-budget-usd 15` set at launch and cannot be raised mid-run.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `GSS_FINISH_RALPH_LOOP_WAITS_GAME_TURN` — detached round 3 running in /home/mandrake/rm/scratch/BENCH/ralph_gss (brief: no wires in textures, plugs from above, Modern wall plugs, endpoints, solar connectivity, kinks, lab learns these classes, live zoomed-crop judge, leave Modern staged); progress in `D:\ClaudeWork\rimmandrake\gss_sitting\FIXES_20261108.md` "Round 3"; NEXT: when its DETACHED RUN ENDED line appears, read the report, and if it stopped on the $15 budget relaunch a continuation with `--budget-usd 60 --clone /home/mandrake/rm/scratch/BENCH/ralph_gss` (owner: don't kill it for budget); then look at its zoomed crop sheet yourself before showing him.
- `RIMMASTER_REDESIGN_ARTISAN_JUDGMENT_NOT_CHECKLIST_GRIND` — detached adoption run: Part A partly landed (4457608bde), Part B what-got-better lists and Part C GPT refinement for agent readers in progress; NEXT: on its DETACHED RUN ENDED line, bring him the Part B list on a card (wasted / worth it / partly per group) and one line on what GPT's refinement changed.
- `RIMMASTER_DESIGN_PHONE_ALERTS_THAT_ACTUALLY_RING` — design written; NEXT: read the doc's draft card and put it to him with the question-card skill.
- `RIMMASTER_FIX_ASH_FOOTPRINTS_AND_SAND_LABEL_AFTER_CLOSE` — code now on main via the Pyrelands landing; NEXT: at the next Pyrelands load (after the GSS sitting) deploy Pyrelands and read footprints and the ash label by bridge.
- `RIMMASTER_SETTLE_ART_BRIEFS_V2_TWO_CAME_BACK_EMPTY` — 9 dirty briefs in the bench clone; NEXT: judge each v2 brief against its v1 in HEAD, commit the good, restore RM_Wuum and ysalamir if empty is wrong.
- `RIMMASTER_FIX_AGENT_GAME_EVENTS_FILED_AS_OWNER` — filed; NEXT: trace why the helper's ./game events landed in OWNER.jsonl and make agent events carry the acting seat.
- `FLOWWORKS_FINISH_ARTISAN_LOOP_DREAD_FOURTH` — untouched today; NEXT: after GSS, prepare a FlowWorks live sitting (offline plan first).
- `RIMMASTER_WEIGH_POCOCK_SKILLS_TRIAL_BEFORE_INSTALL` — NEXT: write the first seed-set scenario test under the real-types pattern; recheck 2026-11-22.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- `rimflow bridge take --owner-said` records an OWNER hold that nobody can release for 45 min; carry out his "it's yours" with `bridge give BENCH --seat OWNER --owner-said` (filed: lessons 20261108T193920Z).
- Detached run completions only reach the Conductor log; this window does not get a notification (see: carry-forward above; file as lesson at next wake).
- The GSS lab is production C# headless but draws no art, plugs, poles or decals, so lab counts said 2 while live showed dozens of defects (see: design/RimMandrake/gss_cabling_method_review_2026-11-08.md).
- Deploying FlowWorks from ralph/gss would overwrite the Pyrelands-closed thirst build (filed: lessons, 54b20172d3).
- `selftest_gss_proof_drivers` M21d hardcodes 36 vs formula 48, pre-existing (filed: lessons gss-proof-drivers-m21d-literal).

## Closed since the last handoff (2)

- `RIMMASTER_LAND_PYRELANDS_BRANCH_397_COMMITS_BEHIND` — 8fb9f7f2b695
- `RIMMASTER_TRACE_PYRELANDS_PROOF_ROWS_THE_LOOP_DROPPED` — 8fb9f7f2b695

## Filed and still open (4) — the next seat's queue

- `RIMMASTER_SETTLE_ART_BRIEFS_V2_TWO_CAME_BACK_EMPTY` — 9 art-eval briefs (RM_Chellow..SWPotF ysalamir) sit uncommitted in the bench clone as a departures@v2 regeneration dated 2026-11-05; RM_Wuum (0 depart
- `RIMMASTER_FIX_AGENT_GAME_EVENTS_FILED_AS_OWNER` — A Conductor helper's ./game up/down events (GSS staging 2026-11-08 ~11:45 AM PST, published cb497082d8) landed in ledger shard OWNER.jsonl, not BENCH:
- `RIMMASTER_BRIEF_BUILDERS_REUSE_BEFORE_BUILDING` — Relentless worker brief gets the reuse-first rule: add one line to worker_prompt() in src/RimMandrake/rimflow/relentless.py: 'Before a new system, a n
- `RIMMASTER_DESIGN_PHONE_ALERTS_THAT_ACTUALLY_RING` — Phone alerts that actually ring: Pushover primary, Todoist urgent backup, outside watchdog; design at D:\ClaudeWork\rimmandrake\conductor\phone_alerts

## Commits

```
ea1c07466e conversations: catch-up 3 record(s)
0e077bc248 item: RIMMASTER_DESIGN_PHONE_ALERTS_THAT_ACTUALLY_RING filed with prose (phone alerts design)
4457608bde rimworld-artisan: bars, flags and sittings here (owner's card 2026-11-08); file RIMMASTER_BRIEF_BUILDERS_REUSE_BEFORE_BUILDING
cc29b17ae4 ledger: RIMMASTER_REDESIGN_ARTISAN_JUDGMENT_NOT_CHECKLIST_GRIND note
54b20172d3 ledger+lesson: GSS redeploy game events; FlowWorks deploy held (game copy is the Pyrelands-closed build)
7f565ef410 ledger: GSS_FINISH_RALPH_LOOP_WAITS_GAME_TURN clone bundled
7ab7b9bb1c conversations: catch-up 1 record(s)
dcc999f865 ledger: detached run on GSS_FINISH_RALPH_LOOP_WAITS_GAME_TURN ended
0461378d02 GSS cabling method review for the owner, with GPT's second opinion verbatim
3d653df6bf art_eval: GSS power strip runs gss_strip_r1 (REGEN PORT_MISFIT) / r2 (ACCEPT) + lesson on plug placement
81b1e08904 ledger: GSS_FINISH_RALPH_LOOP_WAITS_GAME_TURN note
d61963a071 ledger: GSS_FINISH_RALPH_LOOP_WAITS_GAME_TURN note
dd37aa05a6 ledger: live sweep SPAWN_HOOK_FIX_TYPING_BEATS_OWNER_CAP broken, STATION_NOTEBOX_BUILD_WHISPER_AT_NEXT_TURN broken, LIVE_RESTORE_DISPATCHER broken
114166e082 ledger: live sweep DELEGATED_CARDS_FIX_HELD_OUT_RECALL broken, GOODBYE_CANCEL_FIX_PEER_ATE_THE_NIGHT broken, HANDOFF_HOOK_FIX_QUOTED_READY_COUNTS broken, HANDOFF_RESTART_AUDIT_FILES_OWED broken, HOOKS_BLINDSCAN_TUNE_DRIVE_D_IMPORT_TOLL broken, HOOKS_SCANGUARD_FIX_QUOTED_PIPE_SLIPS_PAST broken, HOOKS_VERIFY_TRUE_SUFFIX_MAY_MUTE_REFUSALS broken, MODCHECK_VALIDATE_BUILD_DELEGATED_NEW_BARS broken, NIGHTLY_COP_FIX_RED_ATJKEB_FBYD broken, SEAT_BENCH_RENAME_WORD_OUTLIVED_ITS_WORKSHOP broken
c29a27766a ledger: live sweep LIVE_RESTORE_SET_SESSION_TITLE broken, LIVE_RESTORE_WARN_SKILL_UNWIRED broken, LIVE_RESTORE_WARN_UNCLOSED_QUEUE_ITEM broken, AGENT_WRAPUP_ENFORCE_ASKING_NEVER_WORKED broken, AMEND_HOOK_HARDEN_SWEPT_A_NEIGHBOUR broken, CALL_DEADLINES_ENFORCE_130_OPEN_ENDED broken, CLOSEOUT_TRAP_FIX_HELPERS_ALWAYS_ALIVE broken, CONDUCTOR_CLOSEOUT_BUILD_LEDGER_CHECK broken, CONDUCTOR_REBOOT_FIX_THREE_WASTED_MINUTES broken, CONDUCTOR_RESET_FIX_KILLED_MID_READ broken
13660201e4 ledger: live sweep LIVE_RESTORE_BLOCK_HAND_EDITED_SHEET broken, LIVE_RESTORE_BLOCK_LEDGER_LINT broken, LIVE_RESTORE_BLOCK_PASTE_HANDOFF broken, LIVE_RESTORE_BLOCK_SHARED_TREE_MERGE broken, LIVE_RESTORE_BLOCK_TMPFS_CLONE broken, LIVE_RESTORE_BLOCK_UNBOUNDED_AGENT broken, LIVE_RESTORE_BLOCK_UNLEDGERED_TEXTURE broken, LIVE_RESTORE_BLOCK_WORKTREES broken, LIVE_RESTORE_CONDUCTOR_GOODBYE broken, LIVE_RESTORE_QUEUE_LINT broken
86fb846fbb ledger: live sweep LIVE_RESTORE_AUTO_ALLOW_BASH_PERMISSION broken, LIVE_RESTORE_BENCH_MODE broken, LIVE_RESTORE_BLOCK_AGENT_OVER_SLOTS broken, LIVE_RESTORE_BLOCK_AGENT_WITHOUT_MODEL broken, LIVE_RESTORE_BLOCK_BLANKET_GIT_STAGE broken, LIVE_RESTORE_BLOCK_BLIND_SCAN broken, LIVE_RESTORE_BLOCK_CANON_CONTRADICTION broken, LIVE_RESTORE_BLOCK_DELEGATED_CARDS broken, LIVE_RESTORE_BLOCK_DLL_SOURCE_MISMATCH broken, LIVE_RESTORE_BLOCK_FORGED_VALIDATION broken
770b5d6c40 ledger: RIMMASTER_LAND_PYRELANDS_BRANCH_397_COMMITS_BEHIND clone bundled
666dca9777 conversations: catch-up 1 record(s)
b831092743 ledger: detached run on RIMMASTER_LAND_PYRELANDS_BRANCH_397_COMMITS_BEHIND ended
... 12 more: git log --oneline e8f8b016fe..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-11-08T19:50:55Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/biome_ffar/scale_ground_measured.json   — not this window's (predates session; FFAR biome work)
 M deployed/config/ModsConfig.before-tier-pyrelands.xml   — modset_builder backup from the GSS tier switch (helper); derived
 M infrastructure/state/art_eval/briefs/RM_Chellow.json   — art_eval run 2026-11-05 (item RIMMASTER_SETTLE_ART_BRIEFS_V2_TWO_CAME_BACK_EMPTY)
 M infrastructure/state/art_eval/briefs/RM_Gembug.json   — art_eval run 2026-11-05 (item RIMMASTER_SETTLE_ART_BRIEFS_V2_TWO_CAME_BACK_EMPTY)
 M infrastructure/state/art_eval/briefs/RM_Krissek.json   — art_eval run 2026-11-05 (item RIMMASTER_SETTLE_ART_BRIEFS_V2_TWO_CAME_BACK_EMPTY)
 M infrastructure/state/art_eval/briefs/RM_Lirrith.json   — art_eval run 2026-11-05 (item RIMMASTER_SETTLE_ART_BRIEFS_V2_TWO_CAME_BACK_EMPTY)
 M infrastructure/state/art_eval/briefs/RM_TheUnfinished.json   — art_eval run 2026-11-05 (item RIMMASTER_SETTLE_ART_BRIEFS_V2_TWO_CAME_BACK_EMPTY)
 M infrastructure/state/art_eval/briefs/RM_Wuum.json   — art_eval run 2026-11-05 (item RIMMASTER_SETTLE_ART_BRIEFS_V2_TWO_CAME_BACK_EMPTY)
 M infrastructure/state/art_eval/briefs/RM_Ysvaltha.json   — art_eval run 2026-11-05 (item RIMMASTER_SETTLE_ART_BRIEFS_V2_TWO_CAME_BACK_EMPTY)
 M infrastructure/state/art_eval/briefs/RM_Zrrik.json   — art_eval run 2026-11-05 (item RIMMASTER_SETTLE_ART_BRIEFS_V2_TWO_CAME_BACK_EMPTY)
 M infrastructure/state/art_eval/briefs/SWPotF_RaceDef_ysalamir.json   — art_eval run 2026-11-05 (item RIMMASTER_SETTLE_ART_BRIEFS_V2_TWO_CAME_BACK_EMPTY)
 M infrastructure/state/ledger/events/OWNER.jsonl   — this window (owner-said/by-card notes); committed with this handoff
 M src/RimMandrake/FlowWorks/Tools/native_water_audit.md   — not this window's (FlowWorks loop, predates session)
 M src/RimMandrake/FlowWorks/northstar/review/scenarios/map_r_placed.json   — not this window's (FlowWorks loop, predates session)
?? cards.json   — not this window's (predates session)
?? deployed/config/ModsConfig.before-tier-weepingstones_solo.xml   — not this window's (predates session, modset swap backup)
?? deployed/config/ModsConfig.swap-active.weepingstones_solo.stale-20261108.json   — not this window's (predates session)
?? design/RimMandrake/designer_drawing_out.md   — not this window's (predates session, Designer)
?? design/concepts/Pyrelands/coverage_verdict.json   — not this window's (predates session, Pyrelands loop)
?? infrastructure/state/lessons/20261105T024235Z-CONDUCTOR-tmp-full-alarm-2026-11-05.md   — not this window's (Conductor 2026-11-05, never committed)
?? infrastructure/state/queue/BENCH.md.tmp.1153431.1794098233190787055   — stray rimflow temp file (predates session)
?? ralph/.context_warned   — game_gate hook marker (this window's hook), untracked by design
?? shortcuts.ps1.txt   — not this window's (predates session)
```

