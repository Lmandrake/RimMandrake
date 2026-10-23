# FOUNDRY_REBOOT_HANDOFF_202610231441 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202610230722`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
BENCH now owns ALL FlowWorks and GSS (owner 2026-10-23: "I want Bench owning all Flowworks from now on to prevent mutual waiting"; rimflow routes them via infrastructure/state/flowworks_lane.json): FOUNDRY files a finding --for BENCH and moves on, never waits. FOUNDRY's lanes are the four biomes (Pyrelands, Leaning Scrub, Cauldron, Contagion), RimPulse (live and improved, runs from D:\ClaudeWork\rimmandrake\pulse-deploy), and dirty code outside FlowWorks (0 DIRTY there). The game is UP on the biomes_sprint tier with the biomes, Nine-ritual removal and fluff cuts DEPLOYED but no biome row has run: BENCH holds the bridge for the owner's walk of save e. (filed: lessons)

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- Fluff cuts (design/RimMandrake/fluff_cuts_2026-10-23.md): 19 cut, 5 simplified; he may veto; 8 'ask' rows are item FLUFF_ASKS_DECIDE_EIGHT_UNDER_VETO. The Fever Wood kurreth theft cut and Blue Desert north-star rime-road text are flagged for him.
- Nine rituals deferred to v2 and removed (design/RimMandrake/v2_nine_rituals.md); ambiguous kept-in-v1 cases listed there.
- World faces sheet (own art, three looks): http://localhost:37507/?t=oJLl04winy31_F4Mz9mxQg ; digest of art judgements Transient/art_judgments_2026-10-23.md (RustPuff B/C/D kept, Gale dust art installed).
- RimPulse: ↻ refresh, 'to rule / to look / to provide' split live; 3 live checks await real data (LOOKS A4, ALERTS A2, FAILURES A3).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `HOSE_BUILDINGS_FIX_BATTERY_HIDE_AND_SEEK` — built 5547ca7a0, now BENCH's; NEXT: none for FOUNDRY; BENCH runs it in the FlowWorks sitting
- `HOSE_CROSSING_FIX_FLAT_AS_A_PANCAKE` — built 5547ca7a0, now BENCH's; NEXT: none for FOUNDRY; BENCH captures the map R crossing live
- `JOINT_GATE_HARDEN_TRUST_THE_DRAWN_BOX` — built, gate not yet green live, now BENCH's; NEXT: none for FOUNDRY; BENCH runs joint_check.py --all-maps --crops on maps C and R
- `RIMPULSE_ALERTS_FIX_TELEMETRY_CRIES_WOLF` — built, A2 needs a day of telemetry; NEXT: after 24 h of runtime check /api/now alerts and rimflow verify A2
- `RIMPULSE_DEPLOY_FIX_RUNS_THE_BENCH_CLONE` — done, daemon runs from pulse-deploy; NEXT: close it if the ledger still shows it open
- `RIMPULSE_DIGEST_REBUILD_THREE_QUESTIONS` — built, digest rebuilt; NEXT: read the next scheduled digest at D:\ClaudeWork\rimmandrake\dashboard\digests and close if it reads right
- `RIMPULSE_FAILURES_BUILD_ONLY_THE_STUCK` — built, A3 needs the 03:00 sweep; NEXT: after the next 03:00 nightly check pulse.py report output and rimflow verify A3
- `RIMPULSE_LOOKS_BUILD_UNREAD_NEVER_LISTED` — built, A4 needs a real recorded hand; NEXT: hand one review with --read-by/--caught and check it lists under 'to look at'
- `RIMPULSE_REFRESH_BUILD_EIGHT_WERE_ANSWERED` — built and live; NEXT: close it once he confirms the widget no longer shows answered items under 'to rule'
- `RIMPULSE_STATE_FIX_TWO_WRITERS_ONE_FILE` — done; NEXT: close it if still open
- `SESSION_HURT_DIAGNOSE_BRUISED_AT_THE_BELL` — fixed in live_session (teleport to dry spot), now BENCH's; NEXT: none for FOUNDRY; BENCH confirms no bruises in the next live session
- `WET_FOXHOLE_BUILD_COLD_FEET_SHAKY_AIM` — built c414cbc02, now BENCH's; NEXT: none for FOUNDRY; BENCH runs northstar/wet_costs_live.py

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
The game's ModsConfig is the biomes_sprint tier from the stager's swap (deployed/config/ModsConfig.swap-active.json): restore the owner's list with modlist_swap before his next normal launch (see: rimworld-load-round).
The pulse-deploy checkout auto-fast-forwards origin/main every 10 min, so a broken pulse commit goes live in minutes: run selftest_pulse.py before pushing RimPulse changes (see: RIMPULSE_REFRESH_BUILD_EIGHT_WERE_ANSWERED).
A bare git commit --amend sweeps a neighbour's staged files (filed: lessons, AMEND_HOOK_HARDEN_SWEPT_A_NEIGHBOUR).

## Closed since the last handoff (6)

- `COALESCENCE_REPORT_PROVE_THING_ARG_BINDS` — 553ac949d
- `REEL_OUTLET_DECIDE_ALWAYS_GOES_WEST` — 73b880575
- `FLOOD_STATION_REWIRE_DRY_CANAL_STAYS_DRY` — 747999af5
- `SWIM_TABLE_FIX_FIVE_FIELDS_UNLISTED` — 7f585adf7
- `LADDER_ROWS_WIDEN_STILL_COUNT_TO_TWO` — 7f585adf7
- `ABLATION_SOUNDS_FIX_CUT_LEFT_AN_ECHO` — 23ce5f907820

## Filed and still open (24) — the next seat's queue

- `CONTAGION_STRAYS_HARDEN_ZHOOL_WANDERS_OFF` — Contagion sweep 2026-10-23 leftovers: zhool_haze off arm UNMEASURED (zhool wandered to 12,117, likely sun escape) and sunbeam_hit_arrests UNMEASURED (
- `CONTAGION_REVIEW_STAGE_JUDGE_LOOKS_FIRST` — Contagion owner review prep: judge-agent LOOK at Coalescence stages, drawn tells, Burn vs Bloom, grown limbs x4 facings, cast at density; then one rev
- `CONTAGION_SUNDASH_DECIDE_UNDER_THE_BLOOM` — Design call: CreatureBehaviors sun escape fires on RM_Contagion under the standing Bloom (overlaps the Burn dive); does weather cover reduce Direct Su
- `HOSE_BUILDINGS_FIX_BATTERY_HIDE_AND_SEEK` — FlowWorks hose (audit F2, D2): a laid hose prices walk-over buildings (battery, connector, sandbags) as ground and draws under them; cost them like re
- `HOSE_CROSSING_FIX_FLAT_AS_A_PANCAKE` — FlowWorks hose (audit F8, D11): two laid hoses cross flat, no lift or shadow; the upper hose casts a crossing shadow over the lower one, and joint_che
- `JOINT_GATE_HARDEN_TRUST_THE_DRAWN_BOX` — FlowWorks joint gate (audit F9): measure the AS-DRAWN collar box against each nozzle/port point, add under-building and through-wall rows, a zoomed cr
- `UNDER_COUPLER_DECIDE_CORNER_CROWDING` — Modern tall/XTall tanks: south lane-0 and west lane-0 under-coupler pipes meet on open ground below-left of the body (no base plate), even clipped
- `CARGO_UPPER_PORT_DECIDE_NOTHING_UNDER` — RM_UniversalCargoTank Scrapper/Industrial/Futuristic upper W/E hose port (z 1.5): no opaque body on the axis, so no under-coupler is drawn
- `SESSION_HURT_DIAGNOSE_BRUISED_AT_THE_BELL` — FlowWorks live_session B3: colonists Elisa/Godders hurt mid-script (Bruise = FlowWorks Blunt fall damage, ToxicBuildup = toxic pit fill?) so GovernorS
- `AMEND_HOOK_HARDEN_SWEPT_A_NEIGHBOUR` — The commit-pathspec PreToolUse hook lets a bare 'git commit --amend' through; in a shared seat clone it sweeps the whole index (67633f878 took another
- `SINK_CAP_WIDEN_PAWNS_SINK_TO_FOUR` — Pawn draw sink stops at SinkCapLevels 4 (2 m); pawn_height_ladder_legible says it keeps sinking to 4 m (D=8); v2 X1 reads red (KNOWN_MOD_RED)
- `WORLD_FACES_INSTALL_OUR_OWN_AT_LAST` — Install the world-face look he picks on world_faces_review_2026-10-23 (four shipping biomes first, then the roster): fold the picked approach into bio
- `WORLD_DECALS_BUILD_SEPTEMBER_CHARM_REDRAWN` — Only if he picks look C and/or Hills 2: RM_WorldLook per-tile decal submesh (our own glyph atlas per biome, unrotated, altitude fade past mid zoom, Mo
- `ASHPULSE_READERS_PRUNE_NOBODY_LEFT` — Prune inert ash-pulse/sand-lock readers left after the Long Shade ash-act cut (CreatureBehaviors RM_AshPulse.cs extensions + RM_CompSandSwim/RM_SandBu
- `SCENARIO_ONLY_FIX_SWEEPS_THE_WHOLE_ZOO` — scenarios_map --build --only X sweeps every other plot's animals and prisoners: run_build sweeps with keep_rects of the --only plots, so --only C5 rem
- `PAUSE_ARG_FIX_PAUSED_NEVER_PAUSED` — rimworld/pause_game takes pause=, not paused= (unknown arg silently dropped): objects_sheet.py:367, river_scenes_walk.py:441,511, ladder_wall_proof.py
- `FW_SELFTESTS_MEND_TWO_RED_AFTER_PARITY` — Two FlowWorks selftests red: northstar/selftest_drawbridge_proof.py (validation.DRAWBRIDGE_CASES missing Drawbridge_raised_leaf_draws_without_its_winc
- `SELFTEST_SOURCE_POLISH_STALE_SEVENTY_SUITES` — SelfTest source tidy (C#, needs a rebuild with a .srchash): Program.cs header says ~70 suites (about 110 run); dead locals pumped/tank/held in Liquid_
- `WATER_LOOK_DIAGNOSE_GREY_ON_THE_ROT` — Dug water (0.2-5 m ladder, canals) and a painted vanilla WaterDeep lake all draw as flat grey/brown, no water look, on a biomes_sprint quicktest (RM_T
- `RIMPULSE_REFRESH_BUILD_EIGHT_WERE_ANSWERED` — RimPulse: refresh button (forced re-collect, says refreshed hh:mm:ss or why it failed); every row shows source+age; to rule / to provide / to look spl
- `FLUFF_ASKS_DECIDE_EIGHT_UNDER_VETO` — Fluff review follow-through under his 'I cut, you veto' card: decide the 8 rows left as asks in design/RimMandrake/fluff_cuts_2026-10-23.md (Abyss #6,
- `UNDERCOUPLER_GIRTH_TUNE_PEEKS_PAST_NECK` — Hose under-coupler drawn beneath a connected port (UnderCouplerGeometry collar 0.3125, pipe 0.219 + Joins/*/UnderCollar,UnderPipe) is now wider than t
- `ANCHOR_BOLLARD_REDRAW_LIES_DOWN_ON_DUTY` — Styled suspension-anchor bollards read as flat fixtures turned to the rope (art-eval CAM_WRONG, Opus+GPT run drawbridge_cables_20261023b), not upright
- `RAISED_LEAF_FIX_HIDES_ITS_OWN_ANCHORS` — A raised leaf whose span runs south draws north-up from the hinge edge over its own hinge anchors and their slack ropes (art-eval DESC_MISS, run drawb

## Commits

```
82475391c flowworks_lane: GSS goes to BENCH too (owner card 2026-10-23), add bollard/leaf patterns
0b766ca61 Ledger: reassign ANCHOR_BOLLARD_REDRAW, RAISED_LEAF_FIX to BENCH (owner 2026-10-23)
9efbca13f BENCH owns all FlowWorks: docs, flowworks_lane.json routing in rimflow file/--acceptance, selftest
acc289506 Ledger: reassign 75 FlowWorks items to BENCH, file 2 BENCH handoff items (owner 2026-10-23)
d5a6104e9 DRAWBRIDGE_CABLES_FIX_STOP_SHORT: anchor ropes reach the deck; raised leaf leaves them slack
e0f2ff981 Ledger: reassign 71 FlowWorks/GSS items FOUNDRY to BENCH (owner 2026-10-23)
3713dd99f Seats: Gimme Some Slack moves to BENCH with FlowWorks (owner card 2026-10-23)
138b6c943 Ledger: weir flotsam + auto-rotate built at aed440b5945f (by card); live checks owed
575795bb4 Seats: BENCH owns all FlowWorks work; FOUNDRY does none (owner 2026-10-23)
aed440b59 Rebuild RimMandrakeFlowWorks.dll from committed source at landing
eaaeee252 FlowWorks DLL: river flotsam + weir auto-rotate
08a8e67cc River flotsam enters upstream and leaves downstream; weirs auto-rotate across the current (owner card 07:19)
53c496908 Ledger: CORD_PLUG_FIX_FINDS_THE_PIPE_SLOT built at 0959a81688
382df705c Ledger: PUMP_PORTS_REDRAW_SIZED_FOR_FAT_PIPES built (live look owed) + 3 follow-ups filed
0959a8168 CORD_PLUG_FIX_FINDS_THE_PIPE_SLOT: GSS cords slide under buildings at a diagonal Plug point sits 0.18 into the hookup cell (never a side midpoint, where pipe/hose ports are), arrives at 45 deg and runs under the art to the centroid; setting slideUnder (default on). Tap clamps keep the straight plug (CordWorldAdapter.TapIds).
36a4c4e65 PUMP_PORTS: hold the UnderCouplerReach.cs regen until the FlowWorks DLL can be rebuilt clean Peers' uncommitted FlowWorks C# leaks into every rebuild now; the regenerated table rides UNDERCOUPLER_GIRTH_TUNE_PEEKS_PAST_NECK.
37938c2a0 Revert "Rebuild RimMandrakeFlowWorks.dll from committed source at landing"
a8b327410 Rebuild RimMandrakeFlowWorks.dll from committed source at landing
c10fa6c81 PUMP_PORTS_REDRAW_SIZED_FOR_FAT_PIPES: pump side ports shrunk to the modern girth (Scrapper/Industrial/Futuristic) Neck 0.15 / flange 0.205 cell, flange faces still on the footprint edge; UnderCouplerReach.cs regenerated for the new art (DLL rebuild owed). Replaces owner-kept art on his word; pipeline HELD (needs in-game capture), live look owed.
af4cdab91 Ledger: live-sitting triage (sink cap + water look implemented, ablation echo closed, five FAIL rows classified)
... 313 more: git log --oneline f0d416220..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: for     OWNER is walking save e — hold so no agent drives the game (owner: someone automated is moving around the map)

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M deployed/config/ModsConfig.before-tier-flowworks.xml   the stager subagent's tier-swap backup
 M src/RimMandrake/FlowWorks/Source/SelfTest/RimMandrakeFlowWorks.SelfTest.csproj   a FlowWorks helper's edit, now BENCH's
?? deployed/config/ModsConfig.swap-active.json   the stager subagent's active-swap marker
?? src/RimMandrake/FlowWorks/northstar/live_session_result_20261023T044826.json   the stager subagent's FlowWorks live-session result, BENCH's
```

