# BENCH_REBOOT_HANDOFF_202611072037 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202611071817`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
The owner wants fewer agents and more live games, and today's reading backs him for the Artisan loops: two games ran at once on SteveDesktop with Steam's blessing, while Graffiti has queued for a game since 08:34 PST. Tooling for game B is being built (`RIMMASTER_BUILD_SECOND_GAME_TOOLING_STEAM_SAID_YES`); putting Graffiti on B is the next lever. Artisan still runs by hand with the pipeline stopped ("Question Cards"). Re-arm the watch at once: a Monitor on `/mnt/d/ClaudeWork/rimmandrake/conductor/steve_watch.sh` covers the loops and SteveDesktop every 5 min, as he asked ("keep a regular check on it"); it doesn't report a detached helper ending, so read the Conductor log tail too. His fixed "Artisan watch" prompt is stale: GSS is rm-ralph-gss-steve, Graffiti is rm-ralph-graffiti3 with a validated north star and waits on a game, not the contrast sheet.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- **ARTISAN_NOW graphic is live and he hasn't seen the comparison:** `D:\ClaudeWork\rimmandrake\conductor\ARTISAN_NOW.md`, open in his Typora beside `RELENTLESS_NOW.md`. GPT's rival: `D:\ClaudeWork\rimmandrake\conductor\artisan_graphic_passes\gpt\gpt_render.png`; the helper's render is `final_in_typora.png` in the folder above it. My recommendation: keep the helper's, which has time split inside passes, game lanes and freezes, and take GPT's headline "0 accepted, N hours waiting for games". The helper's naive reader found the tiny marks and "met / failed / unseen" hard to decode.
- It shows Archmagi's game with 331 freezes of 1 s or more (MEASURED by the sheet), matching his "very fast, then pause"; the loop's commit at 11:50 says it fixed that stall. Check the count stops rising.
- He hasn't ruled on what happens at landing to the test grant, the bypassed art ledger and the full-list runs; card it when the first loop claims done. Mods accepted: 0 of 135 at the last handoff.
- Unread by him: growth assessment's remaining calls were all answered today; the other agent-can-do items in `D:\ClaudeWork\rimmandrake\conductor\growth_assessment_2026-11-07.md` aren't done (publish.py's OWNER.jsonl warning, memory cull, FOUNDRY sweep).
- Census of queue items owed to the mods is partial: 137 of about 607 checked, 120 candidates with changed files untriaged: `D:\ClaudeWork\rimmandrake\conductor\mod_owed_census_2026-11-07.tsv`. I told him I'd start with the 120 on a Sonnet helper unless he says otherwise; not started.
- FireHawk bird page still waits for his eight picks: `D:\ClaudeWork\rimmandrake\firehawk_replay\page\index.html`. The harness build stays stopped until then.
- Accounts at 12:18 PST: lukas 60% left, steven 34%, system 1%, all MEASURED. Codex last read 02:19Z, 32% of the week used, since monitoring stopped with the pipeline.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `RIMMASTER_RELEASE_POOL_FROZEN_ITEMS_HOLD_CLONES` — in-process helper at handoff writing: shutting down 27 frozen Relentless items by his order and bundling their clones, and fixing the return path; NEXT: read its report and the pool count, and tell him clones before and after.
- `RIMMASTER_BUILD_SECOND_GAME_TOOLING_STEAM_SAID_YES` — detached helper running, unit rm-detached-bench-rimmaster-build-second-game-tooling-stea-1794082514, trial result in design\RimMandrake\two_rimworld_instances_2026-11-07.md; NEXT: when it reports, put Graffiti on game B on SteveDesktop, which is the item's live proof.
- `PYRELANDS_FINISH_ARTISAN_THIRD_TIME_WISER` — pass 6 since 11:19 PST at medium, later passes xhigh from the clone's settings; limit raised to 20M, and unit rm-pyrelands-relaunch-at-limit restarts it within seconds when the old 10M limit pauses it; his card answers and grey-ground note are in its prompt, crops at a tenth of the rate unsolved; NEXT: on DONE.md run the blind judge, and check the grey ground before and after shots.
- `GSS_FINISH_RALPH_LOOP_WAITS_GAME_TURN` — pass 8 at xhigh, unit rm-ralph-gss-steve, 15.76M of 20M, about 1.7 h from its limit at 12:23 PST; NEXT: at DONE.md or 20M run the blind judge or card him, and launch the FlowWorks helper.
- `FLOWWORKS_FINISH_ARTISAN_LOOP_DREAD_FOURTH` — not started; NEXT: when GSS claims done or pauses, launch one opus helper to set it up from the Artisan template, gate ahead on graffiti3, pyrelands and gss-steve; his four-ways passage, xhigh and phone for help come with the template. Its source now holds four more fixes, unproven live.
- `GRAFFITI_FINISH_RALPH_LOOP_PLAYS_FIRST` — validated at 20 must-show and 2 cannot-show (in the loop's clone), waiting for a game at 8.13M of 20M, unit rm-ralph-graffiti3; NEXT: move it to game B when tooling lands, and on DONE.md run the blind judge with his words first.
- `RIMMASTER_WIRE_STEVEDESKTOP_TELEMETRY_FLYING_BLIND` — filed, not started; telemetry reads Archmagi only; NEXT: give SteveDesktop's game a query route when game B work settles.
- `RIMMASTER_TAME_EGROWTH_PASS_ONE_SECOND_FREEZE` — Pyrelands' loop committed "no stall every 250 ticks" at 11:50 PST; NEXT: confirm against the tps record, then close it with the sha.
- `HANDOFF_SHRINK_HALF_THE_BYTES_WERE_GIT` — wake trimmed, the one-screen state file remains and is in its prose; NEXT: build the generator.
- `GRAFFITI_TEMPER_RETHINK_RACES_BRING_TRAITS` — filed as his note; NEXT: revisit the table whenever personalities change.
- `STEVE_BUILD_ARTISAN_LOOPER_THIRTEEN_MINUTES` — works; test lane pause ends 2026-11-08 08:01 PST; NEXT: extend the pause before then if a loop is still on that game.
- `STEVE_CRASHES_DIAGNOSE_DEFENDER_FALLS_TOO` — turbo off since 08:00 PST, no fault window since (last began 07:56 PST), boot at 09:49 PST; NEXT: keep reading it through the watch, and restore turbo if faults return.
- `EMPIRE_SPLIT_DEPLOY_WAITS_FOR_FREE_GAME` — never run in game; NEXT: deploy both mods when a game is free and read back the Empire's label, icon and raid roster.
- `GRAFFITI_STARWARS_RESKIN_NOT_ONE_TERRAN_TAG` — plain Jawa marks are now this loop's; NEXT: start after Graffiti is accepted and landed.
- `SACRED_GRAFFITI_FINISH_NINE_GODS_WAIT_TURN` — gods both Form and figure, Dark Vigil and rites in; NEXT: start after the Star Wars loop lands, showing him the first four god marks first.
- `LUMINOUS_GRAFFITI_BUILD_SHIMMER_THAT_STAYS` — future; NEXT: after Graffiti lands, card him on what "permanent" means given paint dies with its wall.
- `FLOWWORKS_FIX_NATIVE_WATER_AUDIT_RED` — audit still red; NEXT: take it when FlowWorks's loop starts.
- `GRANT_RESTORE_CAMPAIGN_WHEN_HE_PLAYS` — NEXT: switch to campaign the day he starts playing.
- `PIPELINE_RETHINK_OWNER_STOPPED_BURN` — stopped, PAUSE set; his views and the numbers are notes on it, including effort: all 60 sampled Relentless transcripts ran medium; NEXT: keep it stopped until his in-person sitting, then use the item's undo list.
- `RELENTLESS_BUILD_DAILY_RELEASE_WITH_ROLLBACK` — frozen by his stop; NEXT: leave it for the first Relentless pass after his sitting.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- A loop launched with `--setting-sources project` silently ran at medium effort (filed: lessons)
- A running pass doesn't take a changed settings file, and a running loop doesn't take a changed loop.sh (filed: lessons)
- A stopped pipeline pins the clone pool: frozen items count as owned for good (filed: lessons)
- `known_items` didn't see spawned items, so detached runs refused them; fixed 5d8564c87d (filed: lessons)
- `--owner-said` refuses a question from him as authority; use `--why` (filed: lessons)
- A loop doesn't use an instrument its prompt doesn't name (filed: lessons)
- The Monitor doesn't report a detached helper ending, so the graphic finished at 12:24 PST unnoticed for 13 minutes (see: Conductor log tail)

## Closed since the last handoff (8)

- `SKILLS_BUILD_MUTATE_RELENTLESS_ARTISAN_NOW` — 823cb78e443c
- `RETURNED_PRISONER_FIX_GRACE_LOST_ON_LOAD` — 682e7b4e72a3
- `TRENCH_STRIDE_FIX_CROSS_MAP_INVALIDATION` — 682e7b4e72a3
- `CLIFF_MASK_TAME_PER_CELL_SCRATCH` — 682e7b4e72a3
- `COVER_SCAN_TAME_QUADRATIC_ID_MINIMA` — 682e7b4e72a3
- `RIMMASTER_BUILD_ARTISAN_NOW_SHEET` — cdc016b13494
- `LIVELANE_PROBE_SECOND_GAME_INSTANCE` — 01b88e2ca9da
- `RIMMASTER_DESIGN_ARTISAN_NOW_GRAPHIC_AT_A_GLANCE` — 740b8f8cea29

## Filed and still open (1) — the next seat's queue

- `RIMMASTER_BUILD_SECOND_GAME_TOOLING_STEAM_SAID_YES` — Second game tooling: the first list in design/RimMandrake/two_rimworld_instances_2026-11-07.md, so one loop can run on game B on SteveDesktop

## Commits

```
79fbb3638f conversations: catch-up 2 record(s)
86c9b8e4cc conversations: six session records the SHOWINGS pool clone held, landed so it can go back
33f6d5bcd7 conversations: catch-up 1 record(s)
f17c688289 conversations: catch-up 1 record(s)
fb8bb92881 conversations: catch-up 1 record(s)
f2de9bf5e8 ledger: Artisan broaden
c0193a4621 ledger: detached run on RIMMASTER_DESIGN_ARTISAN_NOW_GRAPHIC_AT_A_GLANCE ended
59a4a3ad16 ledger: RIMMASTER_DESIGN_ARTISAN_NOW_GRAPHIC_AT_A_GLANCE closed, final note; lesson on his real column width
6a23ea85ad ledger: Artisan phone for help
740b8f8cea ARTISAN_NOW: a picture at the top, every pass on one clock, split by where its time went
fceb3a3c98 ledger: RIMMASTER_DESIGN_ARTISAN_NOW_GRAPHIC_AT_A_GLANCE note
1f9ee9571f ledger: Pyrelands limit 20M, clone pool item
b8cdf96413 ledger: owner's Pyrelands and GSS cards
8dab026302 ledger: detached run on LIVELANE_PROBE_SECOND_GAME_INSTANCE ended
034de596ea ledger: LIVELANE_PROBE_SECOND_GAME_INSTANCE closed, trial passed; tooling item filed
01b88e2ca9 Second game trial: rung one passed on SteveDesktop; result and recipe fixes in the design
ca518fef4d ledger: ARTISAN_NOW graphic filed
a5fd88dad2 ledger: Artisan loops xhigh, ARTISAN_NOW graphic
a03d210198 ledger: LIVELANE_PROBE_SECOND_GAME_INSTANCE note
0731d94bb4 ledger: RIMMASTER_BUILD_ARTISAN_NOW_SHEET filed and closed live
... 32 more: git log --oneline 0bcd731141..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-11-07T13:34:17Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/biome_ffar/scale_ground_measured.json   not mine; seen dirty at wrap, not touched
 M infrastructure/state/art_eval/briefs/RM_Chellow.json   the art auto-judge's, still running
 M infrastructure/state/art_eval/briefs/RM_Gembug.json   the art auto-judge's, still running
 M infrastructure/state/art_eval/briefs/RM_Krissek.json   the art auto-judge's, still running
 M infrastructure/state/art_eval/briefs/RM_Lirrith.json   the art auto-judge's, still running
 M infrastructure/state/art_eval/briefs/RM_TheUnfinished.json   the art auto-judge's, still running
 M infrastructure/state/art_eval/briefs/RM_Wuum.json   the art auto-judge's, still running
 M infrastructure/state/art_eval/briefs/RM_Ysvaltha.json   the art auto-judge's, still running
 M infrastructure/state/art_eval/briefs/RM_Zrrik.json   the art auto-judge's, still running
 M infrastructure/state/art_eval/briefs/SWPotF_RaceDef_ysalamir.json   the art auto-judge's, still running
 M src/RimMandrake/FlowWorks/Tools/native_water_audit.md   not mine; seen dirty at wrap, not touched
 M src/RimMandrake/FlowWorks/northstar/review/scenarios/map_r_placed.json   not mine; seen dirty at wrap, not touched
 M src/RimMandrake/rimflow/detached_helper.py   the pool helper's, mid-work on RIMMASTER_RELEASE_POOL_FROZEN_ITEMS_HOLD_CLONES
 M src/RimMandrake/rimflow/relentless.py   the pool helper's, mid-work on RIMMASTER_RELEASE_POOL_FROZEN_ITEMS_HOLD_CLONES
?? cards.json   not mine; seen dirty at wrap, not touched
?? deployed/config/ModsConfig.before-tier-weepingstones_solo.xml   not mine; seen dirty at wrap, not touched
?? design/RimMandrake/designer_drawing_out.md   not mine; seen dirty at wrap, not touched
?? design/concepts/Pyrelands/coverage_verdict.json   not mine; seen dirty at wrap, not touched
?? infrastructure/state/art_eval/runs/audit_auto_20261107_1236/   the art auto-judge's, still running
?? infrastructure/state/lessons/20261105T024235Z-CONDUCTOR-tmp-full-alarm-2026-11-05.md   not mine; seen dirty at wrap, not touched
?? shortcuts.ps1.txt   not mine; seen dirty at wrap, not touched
?? src/RimMandrake/rimflow/selftest_relentless_park_stopped.py   the pool helper's, mid-work on RIMMASTER_RELEASE_POOL_FROZEN_ITEMS_HOLD_CLONES
```

