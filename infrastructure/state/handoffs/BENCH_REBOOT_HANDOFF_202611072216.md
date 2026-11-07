# BENCH_REBOOT_HANDOFF_202611072216 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202611072037`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
Three loops now run on three games: Pyrelands on Archmagi, GSS on SteveDesktop game A (`rm-ralph-gss-steve`), and Graffiti on SteveDesktop game B (`rm-ralph-graffiti3`, proven and closed). His standing "Artisan watch" order still reads "one game", `rm-ralph-gss2` and "Graffiti waits on the contrast sheet". He ruled by card at 13:48 PST to apply it to what runs now, so map it onto the live units and never stop Graffiti because of that text.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- **FireHawk candidate S is ready for his look:** `D:\ClaudeWork\rimmandrake\firehawk_replay\page2\index.html`. A naive judge passed it after three fixes. Ask: "Play S at 1x, then 1/4x and step it: does the east now read as one bird flapping, and may we install S?" His eye-level idea worked on the east and failed on north and south, which stay A's.
- **The Porg he accepted on 2026-11-06 from stills ("good enough from here") is his terrifying Bird G:** the live flip-book is byte-identical. Rebuilding art he kept is his call. Item `RIMMASTER_FIX_PORG_WINGS_RIP_BELLY_ACCEPTED_FROM_STILLS`.
- **Pyrelands' early look is held:** the grey squares are still unidentified and cinderfall isn't re-shot. Bring it once LOOK.md answers, after viewing the new shots.
- **Graffiti's landing debt:** the art guard refused 394 of its PNGs, so they go through art install at landing. The landing card (test grant, bypassed art ledger, full-list runs) is still owed when the first loop claims done. Mods accepted: 0.
- **Still to reach him:** the spring cleaning's `PROPOSED_FRAGMENTS.md` (rules widened to every project) and anything for the public MandrakeWorkflows repo, on a card. Also the Pocock design pass's decisions, as a short card, not the draft.
- **Shipped on a delegated call, which he may veto:** ARTISAN_NOW's summary line now carries "Accepted" and "Waited for a game" (`0b1d6735f0`, his verdict "vastly superior" recorded).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `RIMMASTER_PROMOTE_SKILLS_SPRING_CLEAN_HANDOFFS_TO_LESSONS` — detached opus, unit rm-detached-bench-rimmaster-promote-skills-spring-clean-ha-1794085355, 4 h bound from 13:03 PST, unit 1 (three Artisan skills) done; progress `D:\ClaudeWork\rimmandrake\conductor\spring_clean_2026-11-07\PROGRESS.md`; NEXT: when it ends, read REPORT.md, relaunch it from PROGRESS.md with the same brief if work remains, and card him PROPOSED_FRAGMENTS.md.
- `RIMMASTER_WEIGH_POCOCK_SKILLS_TRIAL_BEFORE_INSTALL` — detached opus, unit rm-detached-bench-rimmaster-weigh-pocock-skills-trial-befo-1794087756, pass 1 and GPT's blind answer and critique landed in `design/RimMandrake/2026-11-07-pocock-design/`; NEXT: when it ends, read MERGE_DRAFT.md and `design/RimMandrake/mattpocock_design_suggestions.md`, then bring him a short card.
- `RIMMASTER_INSTALL_FIREHAWK_S_EAST_WAITS_ON_HIS_LOOK` — page2 built and judged; NEXT: show him page2 with the question above, and install S through art install only on his yes.
- `RIMMASTER_FIX_FIREHAWK_EAST_SHOWS_TWO_WINGS_AT_ONCE` — helper done, skill landed de8bbfd1eb, last commit 977496ab53; NEXT: close it with 977496ab53, since the install item carries the rest.
- `FLOWWORKS_FINISH_ARTISAN_LOOP_DREAD_FOURTH` — setup brief written at `D:\ClaudeWork\rimmandrake\conductor\briefs\flowworks_artisan_setup_2026-11-07.md`, his card on the item; NEXT: when ralph_gss shows PAUSED_FOR_REVIEW or DONE_CLAIMED, run `detached_helper.py launch --seat CONDUCTOR --item FLOWWORKS_FINISH_ARTISAN_LOOP_DREAD_FOURTH --brief-file <that brief> --model opus --max-s 7200 --budget-usd 40`.
- `GSS_FINISH_RALPH_LOOP_WAITS_GAME_TURN` — pass 10 since 14:04 PST at 18.94M of 20M; NEXT: on DONE_CLAIMED start a background rm-judge (opus), blind to its verdicts, writing blind_judge_verdict_pass<N>.md in `D:\ClaudeWork\rimmandrake\ralph_gss`; on the 20M pause card him on more tokens with what they bought.
- `PYRELANDS_FINISH_ARTISAN_THIRD_TIME_WISER` — pass 8 since 13:32 PST at 11.06M of 20M, early look held; NEXT: when LOOK.md names the grey squares, view the new shots and bring him the early look.
- `GRAFFITI_FINISH_RALPH_LOOP_PLAYS_FIRST` — pass 5 on game B since 13:44 PST at 9.95M of 20M; NEXT: on DONE_CLAIMED run the blind judge with his words first.
- `RIMMASTER_TRIAGE_MOD_OWED_CENSUS_120_STILL_UNREAD` — done: 208 rows (PROOF_ONLY 110, APPLY_NOW 44, UNVERIFIED 35, ALREADY_DONE_OR_DECAYED 19) in `D:\ClaudeWork\rimmandrake\conductor\mod_owed_census_120_2026-11-07.tsv`; NEXT: close the 19 on their evidence, hand each loop its APPLY_NOW rows at its next send-back, and close this item.
- `RIMMASTER_TAME_EGROWTH_PASS_ONE_SECOND_FREEZE` — ARTISAN_NOW still showed 3 stall incidents in 10 min at 13:05 PST; NEXT: read the tps record after Pyrelands' pass 8 deploys, and close with the sha if the stalls are gone.
- `STEVE_BUILD_ARTISAN_LOOPER_THIRTEEN_MINUTES` — test lane pause ends 2026-11-08 08:01 PST; NEXT: extend it before then while any loop is on SteveDesktop.
- `STEVE_CRASHES_DIAGNOSE_DEFENDER_FALLS_TOO` — turbo off, two games up with no fault reported by the watch today; NEXT: keep reading fault_monitor through the watch and restore turbo only if faults return.
- `RIMMASTER_WIRE_STEVEDESKTOP_TELEMETRY_FLYING_BLIND` — filed, not started; NEXT: give SteveDesktop's games a query route now that game B has landed.
- `HANDOFF_SHRINK_HALF_THE_BYTES_WERE_GIT` — wake trimmed; NEXT: build the one-screen state generator after the spring cleaning reports.
- `GRAFFITI_TEMPER_RETHINK_RACES_BRING_TRAITS` — his note; NEXT: revisit the table whenever personalities change.
- `EMPIRE_SPLIT_DEPLOY_WAITS_FOR_FREE_GAME` — never run in game; NEXT: deploy both mods when a game is free and read back the Empire's label, icon and raid roster.
- `GRAFFITI_STARWARS_RESKIN_NOT_ONE_TERRAN_TAG` — NEXT: start after Graffiti is accepted and landed.
- `SACRED_GRAFFITI_FINISH_NINE_GODS_WAIT_TURN` — NEXT: start after the Star Wars loop lands, showing him the first four god marks first.
- `LUMINOUS_GRAFFITI_BUILD_SHIMMER_THAT_STAYS` — NEXT: after Graffiti lands, card him on what "permanent" means given paint dies with its wall.
- `FLOWWORKS_FIX_NATIVE_WATER_AUDIT_RED` — NEXT: take it when FlowWorks' loop starts.
- `GRANT_RESTORE_CAMPAIGN_WHEN_HE_PLAYS` — NEXT: switch to campaign the day he starts playing.
- `PIPELINE_RETHINK_OWNER_STOPPED_BURN` — stopped, PAUSE set; NEXT: keep it stopped until his in-person sitting, then use the item's undo list.
- `RELENTLESS_BUILD_DAILY_RELEASE_WITH_ROLLBACK` — frozen by his stop; NEXT: leave it for the first Relentless pass after his sitting.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- `rimflow file` or `note` with `--owner-said` or `--by-card` writes `events/OWNER.jsonl`, so publishing only BENCH.jsonl strands the item from a helper's clone; launch now refuses such an item (filed: lessons 20261107T214121Z, fix c9e4d25f10).
- A new rm-ralph unit with no `Environment=PATH` ends its pass rc 127 in a second (filed: lessons).
- `show.sh` selects a file in Explorer and doesn't open it; open images for him with `powershell.exe Start-Process` (filed: lessons).
- A selftest asserting the bare word RED fails on every UNMEASURED row (filed: lessons 20261107T214121Z).
- The Lodestar checkout `~/dev/Lodestar` is ahead 24 and behind 72, so nothing in this session was written to it; the spring cleaning lands its rows from a throwaway clone (see: spring_clean PROGRESS.md).

## Closed since the last handoff (1)

- `RIMMASTER_BUILD_SECOND_GAME_TOOLING_STEAM_SAID_YES` — 5e3b8d75cb13

## Filed and still open (13) — the next seat's queue

- `RIMMASTER_REPAIR_SEAT_FILE_CHECK_RED_BEFORE_THIS_TOO` — selftest_bridge_seat_relentless: 'nobody files for RELENTLESS' is red on main
- `RIMMASTER_FIX_FIREHAWK_EAST_SHOWS_TWO_WINGS_AT_ONCE` — FireHawk review: his eight verdicts go into the flying art skill, then one offline fix attempt (east double wing, eyes level)
- `RIMMASTER_PROMOTE_SKILLS_SPRING_CLEAN_HANDOFFS_TO_LESSONS` — Spring cleaning: extract and promote skills across agents, handoffs, memory and CLAUDE.md; artisan and Relentless especially; clean and repoint
- `RIMMASTER_TRIAGE_MOD_OWED_CENSUS_120_STILL_UNREAD` — Finish the mod-owed census: triage the 120 queue items whose cited files changed since filing
- `RIMMASTER_FIX_PORG_WINGS_RIP_BELLY_ACCEPTED_FROM_STILLS` — Porg live flip-book carries belly away with its wings; accepted from stills, terrifying in motion
- `RIMMASTER_AUDIT_CUTOUT_EASTS_THIRTEEN_SHARE_SQUASH_NOISE` — Thirteen other cut-out flyer sets have east poses under |sy| 0.5, the recipe behind FireHawk's static noise
- `RIMMASTER_TEACH_FLYER_JUDGE_PARTS_SHEET_STILLS_MISSED_IT` — Art-eval flyer module: give judges the parts sheet and the C5a checks, severity codes, regress
- `RIMMASTER_FIX_REMOTE_TAKE_HOLDS_LOCK_NOBODY_READS` — A remote take of stevedesktop.b reports held but writes a lock file nobody reads
- `RIMMASTER_WEIGH_POCOCK_SKILLS_TRIAL_BEFORE_INSTALL` — Assess mattpocock/skills design skills into mattpocock_design_suggestions.md, then a deep design pass on where they help RimMandrake and Artisan's cod
- `RIMMASTER_TRIAGE_ORPHAN_POINTERS_FROM_CULLED_HANDOFFS` — 334 pointers that only culled handoffs named, carried to one table: close, drop or file each
- `RIMMASTER_MOVE_IMAGE_SKILLS_OUT_PAST_CODE_PATHS` — Move generating-images and editing-images to MandrakeWorkflows once code reaches them through one path
- `RIMMASTER_FIX_GAMEB_TIER_REFUSES_AFTER_ITS_OWN_SYNC` — Game B's tier refused on a swap marker after a sync; the marker is per clone and tracked
- `RIMMASTER_INSTALL_FIREHAWK_S_EAST_WAITS_ON_HIS_LOOK` — FireHawk flip-book S (A's north and south, east rebuilt from D with eyes level and one belly edit): install only after his look at page2

## Commits

```
9e973563ad conversations: catch-up 2 record(s)
bb7f4332ff lessons folded into active files: left_harness
70f543dfbe lessons folded into active files: left_modding
c1ed3c3921 pocock design: second model's critique; pass 1 header time corrected
7e5f8b46b9 lessons folded into active files: windows_0
9ef9006357 lessons folded into active files: arena_0
2fb1229019 ledger: RIMMASTER_PROMOTE_SKILLS_SPRING_CLEAN_HANDOFFS_TO_LESSONS note
84b8c2e14c lessons folded into active files: steve_0
6744e479d9 skills: second relocation of folded-in lessons from five SKILL.md files to references/traps.md
2a4b9a9cb9 rimworld-load-round: the minimal list is a file to parse, not a number (13 then, 27 now); two conflicting lessons resolved
b753499f0e pocock design: pass 1, trials ranked and four Artisan options
574f4a1a4a lessons folded into active files: world_0
807d09e6cc lessons folded into active files: agents_0
8bafe7fae3 lessons folded into active files: deploy_0
38b9091d13 lessons folded into active files: art_eval_0
f87a1ba73d lessons folded into active files: harness_1
5087c83c86 pocock design: second model's blind answer
bb180c5bf8 lessons folded into active files: modding_1
f47176db59 ledger: RIMMASTER_WEIGH_POCOCK_SKILLS_TRIAL_BEFORE_INSTALL note
d6f0afa0c5 lessons folded into active files: harness_2
... 66 more: git log --oneline 7f69b2218d..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running; BRIDGE NOT PROBED — no port found in the environment or in Player.log, so LOADING here is a DEFAULT, not a reading.)
- recorded  : UP
- Bridge: FREE    since 2026-11-07T21:49:44Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/biome_ffar/scale_ground_measured.json   not this window's: dirty at session start, an earlier helper's
 M infrastructure/state/art_eval/briefs/RM_Chellow.json   not this window's: the art-eval pipeline's, dirty at session start
 M infrastructure/state/art_eval/briefs/RM_Gembug.json   not this window's: the art-eval pipeline's, dirty at session start
 M infrastructure/state/art_eval/briefs/RM_Krissek.json   not this window's: the art-eval pipeline's, dirty at session start
 M infrastructure/state/art_eval/briefs/RM_Lirrith.json   not this window's: the art-eval pipeline's, dirty at session start
 M infrastructure/state/art_eval/briefs/RM_TheUnfinished.json   not this window's: the art-eval pipeline's, dirty at session start
 M infrastructure/state/art_eval/briefs/RM_Wuum.json   not this window's: the art-eval pipeline's, dirty at session start
 M infrastructure/state/art_eval/briefs/RM_Ysvaltha.json   not this window's: the art-eval pipeline's, dirty at session start
 M infrastructure/state/art_eval/briefs/RM_Zrrik.json   not this window's: the art-eval pipeline's, dirty at session start
 M infrastructure/state/art_eval/briefs/SWPotF_RaceDef_ysalamir.json   not this window's: the art-eval pipeline's, dirty at session start
 M src/RimMandrake/FlowWorks/Tools/native_water_audit.md   not this window's: a FlowWorks helper's, dirty at session start (FLOWWORKS_FIX_NATIVE_WATER_AUDIT_RED)
 M src/RimMandrake/FlowWorks/northstar/review/scenarios/map_r_placed.json   not this window's: a FlowWorks helper's, dirty at session start
?? cards.json   not this window's: untracked at session start, an earlier Conductor window's card scratch
?? deployed/config/ModsConfig.before-tier-weepingstones_solo.xml   not this window's: a modlist tier swap's backup, untracked at session start
?? design/RimMandrake/designer_drawing_out.md   not this window's: a stale copy; origin moved it under roles/design at 80f917b48a
?? design/concepts/Pyrelands/coverage_verdict.json   not this window's: a Pyrelands helper's, untracked at session start
?? infrastructure/state/lessons/20261105T024235Z-CONDUCTOR-tmp-full-alarm-2026-11-05.md   not this window's: an earlier Conductor window's lesson, untracked at session start
?? shortcuts.ps1.txt   not this window's: untracked at session start
```

