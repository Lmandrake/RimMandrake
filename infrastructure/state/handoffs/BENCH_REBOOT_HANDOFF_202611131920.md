# BENCH_REBOOT_HANDOFF_202611131920 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202611130629`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
**Exact water (fill-N deleted) is on main as `4ffef4c98f` but NOT deployed, and deploying it makes every existing pit save load its dug squares DRY** (one save grid `RM_excavationWaterGrid`, no migration by his 2026-11-08 ruling). The owner finished his look at `UNDER_LIQUID_LAW_AFK_20261112c` at 11:10 AM PST 2026-11-13 ("Done"), so that save may now go dry: bundle ONE deploy + restart (fill-N, furniture `676c5cd131`, the six look fixes once built, EK's retired closed-container patch removal) and restage the review save in metres with `setBodyWaterM`, never `setFill`.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- **Overnight stall, 01:48:59 to 09:38 PST:** a Cloudflare "403 Attention Required" page, which Claude Code labels "Please run /login", stopped this window although the login was fine (a `claude -p` 30 s earlier answered). login_watch skipped its stranded-window check under the Dispatcher PAUSE and only alarmed a Conductor window anyway. Fixed and live in `/home/mandrake/rm/dispatch` (`90a3c4b8ec`): a stuck Conductor window gets a broadcast message (a new turn, never a restart) plus a phone push via Todoist; Cloudflare 403 is no longer a dead login.
- **Paused work is running again, Whittle and Relentless excluded by his word** ("NO! No Whittle, Relentless please. Those aren't validated yet."; memory `whittle-relentless-stay-off-until-validated`). Dispatcher PAUSE removed; role runs now carry `--max-budget-usd` about 2x their highest measured cost (`f04f03a6`), Designer coverage judge capped at $8 (`c4b6842f`). The restore helper set HOLD on the old Conductor window (312k context) so the Dispatcher would not restart it under him.
- **Explosive Knockback:** exam 119/119, the one judge run refused with 5 new small scene gaps; re-parked. One agent call he may flip: a gas shove onto an open pit DROPS the pawn in (helper followed his 2026-10-06 words "Only if they get blown/forced in do they fall"; I had told him the opposite). Mass limit 150 kg (muffalo 144 flies, rhino 180 does not); vanilla grenade/mortar/IED all deal 50, so blast power only changes rockets, antigrain, modded weapons.
- **Season on the Pyre census:** 3 beats exist, 4 partial, 1 missing (no Pyrelands smoke weather). The Firehawk only SPREADS fire under an earlier spread-only ruling; ask whether he meant it starts fires.
- **Water models:** winner refined to local-inertial with a Froude 0.544 cap (dam breach 1.48x -> 1.09x of the referee); pipes cut; compare page re-rendered, `D:\ClaudeWork\mandrakemodels\compare\index.html`. C# timing: 0.163 ms/tick at 325 on Mono 6.13 (bar 0.5), without the cap yet.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `RIMMANDRAKE_PROVE_UNDER_LIQUID_LAW_LIVE` — his live look recorded (holding store `owner_look_defects_2026-11-13.md`, items a-i in `D:\ClaudeWork\rimmandrake\conductor\owner_look_20261113\FILED.md`, published `ca5b7aa70acf`); NEXT: launch one Opus rm-builder ($15) on the build items in FILED.md (geyser must be BENEATH the water, hot-tub alignment, G2 vent and bubbles, G2 entry, drafted-move target in big pits, willing-entry pit exposure, Cooler arrow over tar), on main after fill-N.
- `RIMMANDRAKE_DELETE_FILL_N_ONE_WATER_NUMBER_SEVEN_FIXES` — chunks 1-2 landed `4ffef4c98f`, FlowWorks C# 1335/1335, not deployed; chunk 3 open (kernel int[] water, delete the ~1000-line whole-notch kernel and its exact=false tests, Python oracle, slime int); NEXT: launch chunk 3 (Opus, $15) from `D:\ClaudeWork\rimmandrake\conductor\cards_20261112_late\filln2_STATE_AT_STOP.md`.
- `RIMMANDRAKE_ALLOW_MEDIUM_FURNITURE_ON_PIT_FLOOR` — four fixes landed `676c5cd131`, not deployed; NEXT: deploy it in the one bundled restart and walk `D:\ClaudeWork\rimmandrake\conductor\afk_20261112_night\build\LIVE_LOOK_CHECKLIST.md`.
- `RIMMANDRAKE_BUILD_KNOCKBACK_CREATURE_MASS_AND_BLAST_POWER` — filed with defaults in `D:\ClaudeWork\rimmandrake\conductor\ek_mass_20261113\DEFAULTS.md`; NEXT: launch Opus ($15) with `D:\ClaudeWork\rimmandrake\conductor\ek_mass_20261113\brief_B_build.md`.
- `RIMMANDRAKE_DESIGN_KNOCKBACK_FIRST_TOUCH` — exam passed, judge refused 5 small scene gaps, parked at ceiling; NEXT: card him: fix the 5 then one more judge, or certify on his word, and confirm the gas-shove-drops-in call.
- `HUGETHINGS_DESIGN_FIRST_TOUCH` — he chose "sit the pass now" and the door seal "live with me ... OR Conductor should peek in"; NEXT: when he is at the machine, put the 7 bars in `design/validation_walks/RimMandrake/HugeThings.md` (must-show section) to him by card, folding his crowd (3+ in 1 day), destruction (walls, trees, crates) and proven-rows (hitbox + save/load) answers.
- `RIMMANDRAKE_PROVE_PYRELANDS_IN_FOUR_SCENES` — his cards enacted (`9102b5b960`), season walk beats and census in `D:\ClaudeWork\rimmandrake\conductor\cards_20261113_am\walk_season_criteria.md`; NEXT: apply its proposed `walk_season_on_the_pyre` leaf text to the Pyrelands tree.
- `RIMMANDRAKE_PORT_FROUDE_CAP_TO_CSHARP_WATER_DECIDED_TWICE` — Python winner has the cap, the C# port does not; NEXT: port the cap into MandrakeModels `csharp/` and re-time at 250/325.
- `RIMMANDRAKE_BUILD_SETTLED_WATER_SLEEP_BAR_STILL_RED` — settled-water bar fails (still stepped); NEXT: build sleep in the C# port after the Froude cap lands.
- `RIMMANDRAKE_RESCUE_STRANDED_CONDUCTOR_CLOUDFLARE_SAID_LOGIN` — fix live `90a3c4b8ec`, helper was finishing at wrap; NEXT: read `D:\ClaudeWork\rimmandrake\conductor\stranded_20261113\STATE_AT_STOP.md` and make sure the item is closed with a --live promise.
- `RIMMANDRAKE_RESTORE_PAUSED_WORK_KEEP_EVERY_SPEND_CAP` — done, 20-min watch clean; NEXT: close it with --live on rm-metronome.timer if the helper did not, and check the Pyrelands Designer stage-5 judge (started before the $8 cap) for its spend.
- `RIMMANDRAKE_SET_CONDUCTOR_WINDOW_TO_FABLE_POLICY_ALREADY_SAID` — landed `972aa893df` (WT tile + seat_restart relaunch); NEXT: confirm the next Conductor window reports Fable 5.2 as its model, then close.
- `RIMMANDRAKE_DESIGN_MELEE_SHOVE_INTO_PIT_CONTEST_FLOWWORKS` — filed from his EK card; NEXT: give it to the Designer with his words on the item.
- `RIMMANDRAKE_FIND_RIVER_SWIM_BRUISES_FUEGO_HURT_FIVE_TIMES` — cause still unknown, vanilla or ours; NEXT: one Opus offline diagnosis (read the damage source on the river cells) before any live run.
- `RIMMANDRAKE_INVENTORY_VALIDATION_SCHEMES_BEFORE_ANY_LADDER` — 30 reds listed, ops-watch now runs under rm-metronome (on since 00:23 PST 11-13, health.json fresh); NEXT: close the ops-watch part with --live "unit=rm-metronome.timer reading=D:\ClaudeWork\rimmandrake\ops_watch\health.json max_age=1h".
- `BENCH_REBOOT_HANDOFF_202611130629` — its other pointers (water-model card, EK card, preflight card, player-truth sweep, climb close, tint close) were all answered or closed this session; the rest (BIND_REFUSALS T5/T7/T8, PIN_OWNER_LOOK holding, swale repaint, artpipe find hang) stand as written there; NEXT: settle each against the ledger with `handoff.py --wake`.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- Claude Code labels a Cloudflare "403 Attention Required" as authentication_failed / "Please run /login" although the login works (see: RIMMANDRAKE_RESCUE_STRANDED_CONDUCTOR_CLOUDFLARE_SAID_LOGIN).
- login_watch's stranded-window check never ran while the Dispatcher PAUSE file existed (see: RIMMANDRAKE_RESCUE_STRANDED_CONDUCTOR_CLOUDFLARE_SAID_LOGIN, fixed 90a3c4b8ec).
- Dispatcher role runs had no hard dollar cap, only time limits and token caps that never stop a run (see: f04f03a6).
- A card asked him a design question he had already ruled (Pyrelands dry ash); grep owner_rulings first (filed: lessons).
- A helper's `taskkill /IM dotnet.exe` killed another process, PID 35220 (filed: lessons).
- A hand-stopped detached helper stays "running" in detached_helper.py status until `finish --unit` (filed: lessons).

## Closed since the last handoff (8)

- `RIMMANDRAKE_TIME_LOCAL_INERTIAL_IN_CSHARP_FIGURES_STILL_GUESSES` — dcd98f86f328
- `STEVE_LANE_UNSTICK_BRAKED_UNOWNED_0692` — 0aac11a0d6
- `STEVE_LANE_UNSTICK_BRAKED_UNOWNED_0A05` — 9de470b7c3
- `RIMMANDRAKE_RESCUE_STRANDED_CONDUCTOR_CLOUDFLARE_SAID_LOGIN` — 90a3c4b8ec05283977cd18992f525f5f033e8b32
- `RIMMANDRAKE_DECIDE_OPS_WATCH_RUNS_VIA_METRONOME_ONLY` — done by verify, no close
- `LIVE_RESTORE_OPERATIONS` — done by verify, no close
- `LIVE_RESTORE_CONDUCTOR` — done by verify, no close
- `PYRE_WORLDSWITCH_DECIDE_ON_BY_DEFAULT` — done by verify, no close

## Filed and still open (53) — the next seat's queue

- `RIMMANDRAKE_LOAD_PYRELANDS_SITE_IN_TESTQ_CHAINS_RAN_BOREAL` — Pyrelands testq jobs never load the Pyrelands site: every site chain runs on a foreign map and ends UNMEASURED SITE
- `RIMMANDRAKE_KEEP_WSLENV_IN_LIVE_PROOFS_TWENTY_SEVEN_DROP` — 27 live-proof lines replace WSLENV, so python.exe on SteveDesktop loses RM_DATA_ROOT and every clause dies RmDataRootUnset
- `RIMMANDRAKE_REPAIR_CODEX_SEATS_FIXTURE_UNLISTED_RED_TWIST` — selftest_codex_seats dies on its bridge take fixture
- `RIMMANDRAKE_REFUSE_GSS_GATE_UNDER_PYTHON_EXE_ALWAYS_RED` — GSS proof_all's offline gate under python.exe is always red: O3's C# SelfTest dies on 'No module named fcntl', charged as MOD; refuse as HARNESS or ru
- `RIMMANDRAKE_DELETE_FILL_N_ONE_WATER_NUMBER_SEVEN_FIXES` — FlowWorks: store and speak water only as exact dL/metres; delete fill N (fillGrid+partGrid -> one grid), the whole-notch 'Water stands exactly level' 
- `RIMMANDRAKE_LIGHT_FUEL_SAP_TERRAIN_FIRES_STARTED_ZERO` — FlowWorks liquid ignition ON never lights fuel sap terrain (firesStarted=0): vanilla FireUtility refuses 0-flammability terrain
- `RIMMANDRAKE_CHECK_SHOOTING_RULE_OFF_PICKS_FARTHER_PIT_FOE` — Superdeep shooting rule OFF: the shooter picks a farther target than the nearer pit enemy; MOD or expectation unknown
- `RIMMANDRAKE_BUILD_PREFLIGHT_SPINE_TIMED_FROM_BIRTH` — Preflight spine: rimflow preflight <ID>, report-only, B1 B4 B5 C1 C2 C10, timed every run
- `RIMMANDRAKE_EXTEND_PREFLIGHT_CORE_KINDS_IDS_SHAS_FULL_REASON` — Preflight CORE rest: strict refs parse, kinds, item ids, shas, Full Mod reason, declared block, sweep
- `RIMMANDRAKE_BACKTEST_PREFLIGHT_OVER_REAL_PAST_TICKETS` — Preflight shadow at file/claim/start/helper launch (not Relentless) and the section 8 backtest
- `RIMMANDRAKE_RESEAT_HEEMIN_FACINGS_DROPS_WHEN_IT_TURNS` — RM_Heemin (Things/Pawn/Animal/RM_Heemin/RM_Heemin) breaks the facing truth (same size from every side, no hop on turning): severity 0.238, plan serpen
- `RIMMANDRAKE_RESCALE_HARVESTER_FACINGS_TALLER_FROM_BEHIND` — RUT_HorrorHarvester (RimUtinni/UtinniPatches/NightHorrors/Harvester/Harvester) breaks the facing truth (same size from every side, no hop on turning):
- `RIMMANDRAKE_RESCALE_SKERREL_FACINGS_WINGS_SPREAD_TOO_BIG` — RM_Skerrel (Things/Pawn/Animal/RM_Skerrel/RM_Skerrel) breaks the facing truth (same size from every side, no hop on turning): severity 0.173, plan ins
- `RIMMANDRAKE_RESEAT_VIZHIK_FACINGS_SINKS_WHEN_FACING_YOU` — RM_Vizhik (Things/Pawn/Animal/RM_Vizhik/RM_Vizhik) breaks the facing truth (same size from every side, no hop on turning): severity 0.168, plan serpen
- `RIMMANDRAKE_RESEAT_MURRIN_FACINGS_BATCH_ACCEPT_DROPPED_IT` — RM_Murrin (Things/Pawn/Animal/RM_Murrin/RM_Murrin) breaks the facing truth (same size from every side, no hop on turning): severity 0.164, plan serpen
- `RIMMANDRAKE_RESEAT_DRAZZIK_NORTH_THIRTEEN_PERCENT_DROP` — RM_Drazzik (Things/Pawn/Animal/RM_Drazzik/RM_Drazzik) breaks the facing truth (same size from every side, no hop on turning): severity 0.133, plan qua
- `RIMMANDRAKE_RESEAT_MYNOCK_FACINGS_SINCE_GRAPHIC_MULTI_SWAP` — RSW_Mynock (RimStarWars/SWBestiary/ShipVermin/Mynock/Mynock) breaks the facing truth (same size from every side, no hop on turning): severity 0.125, p
- `RIMMANDRAKE_REDRAW_NEEBRAY_NORTH_TOO_SMALL_TO_STRETCH` — RSW_Neebray (swanimals/Neebray/Neebray) breaks the facing truth (same size from every side, no hop on turning): severity 0.112, plan flyer; north: reg
- `RIMMANDRAKE_RESEAT_TARRUQ_NORTH_TEN_PERCENT_DROP` — RM_Tarruq (Things/Pawn/Animal/Monkey/RM_Tarruq/RM_Tarruq) breaks the facing truth (same size from every side, no hop on turning): severity 0.105, plan
- `RIMMANDRAKE_REDRAW_FANBACK_V_C_NORTH_AUTO_ACCEPTED_SMALL` — RSW_Fanback (swanimals/Fanback/FanbackV_C) breaks the facing truth (same size from every side, no hop on turning): severity 0.105, plan quadruped; nor
- `RIMMANDRAKE_RESEAT_BRATHEK_NORTH_BATCH_ACCEPT_DROPPED_IT` — RM_Brathek (Things/Pawn/Animal/RM_Brathek/RM_Brathek) breaks the facing truth (same size from every side, no hop on turning): severity 0.102, plan ser
- `RIMMANDRAKE_RESEAT_BULWARK_NORTH_SEVEN_PERCENT_HOP` — RUT_HorrorBroodLord (RimUtinni/UtinniPatches/NightHorrors/Bulwark/Bulwark) breaks the facing truth (same size from every side, no hop on turning): sev
- `RIMMANDRAKE_RESEAT_DROMMATH_NORTH_OLDEST_OF_SIXTEEN_FLAGS` — RM_Drommath (Things/Pawn/Animal/RM_Drommath/RM_Drommath) breaks the facing truth (same size from every side, no hop on turning): severity 0.047, plan 
- `RIMMANDRAKE_RESEAT_MIRRIK_NORTH_RISES_WHEN_IT_TURNS` — RM_Mirrik (Things/Pawn/Animal/Spelopede/RM_Mirrik/RM_Mirrik) breaks the facing truth (same size from every side, no hop on turning): severity 0.047, p
- `RIMMANDRAKE_RESEAT_PROWLER_NORTH_JUST_PAST_TOLERANCE` — RUT_HorrorProwler (RimUtinni/UtinniPatches/NightHorrors/Prowler/Prowler) breaks the facing truth (same size from every side, no hop on turning): sever
- `RIMMANDRAKE_RESEAT_VHAKK_NORTH_SMALLEST_OF_SIXTEEN_HOPS` — RM_Vhakk (Things/Pawn/Animal/RM_Vhakk/RM_Vhakk) breaks the facing truth (same size from every side, no hop on turning): severity 0.035, plan quadruped
- `RIMMANDRAKE_HARDEN_FAST_WATER_SOLVERS_VIA_GPT_PIPES_RING` — Send MandrakeModels water code + results to GPT for clever fixes (oscillation in pipes and other fast solvers, boundary conditions), skeptical review 
- `RIMMANDRAKE_FIT_SENSE_V3_WRAPUP_NEVER_FINISHED_IN_FIFTEEN` — Metronome sense: v3 and wrapup families never finished inside the 15 s limit in the first hour after cutover (killed alone too), so they go blind
- `RIMMANDRAKE_BUILD_SETTLED_WATER_SLEEP_BAR_STILL_RED` — Local-inertial: settled water must sleep (stage C settled bar 0.05 ms/tick fails: settled water is still stepped); also the two port rules: equal subs
- `RIMMANDRAKE_AUDIT_FOREIGN_DEF_ROWS_FAIL_IN_THREE_MODS` — Auditor rule candidate: a validation row that asks get_defs for a def defined in a mod its own About.xml does not name must return UNMEASURED on notFo
- `RIMMANDRAKE_LET_FOLD_MEMORY_KEEP_THE_WORK_COVER` — findings_fold.py decide: the latest decision wins (latest_decision, findings_fold.py:391), so a weekly-sweep 'memory' decision on a signature already 
- `RIMMANDRAKE_DIAGNOSE_STEVE_GAME_VANISHES_FIVE_BEFORE_BREAKFAST` — SteveDesktop test game dies or half-starts with no crash record, braking the lane twice on 2026-11-13. Measured (PST): silent GAME_DIED at 01:57 (J202
- `RIMMANDRAKE_DESIGN_MELEE_SHOVE_INTO_PIT_CONTEST_FLOWWORKS` — FlowWorks: a melee 'shove into pit' — one pawn shoves another into an open pit as a contest of both masses and both melee skills / agility (dodge)
- `RIMMANDRAKE_SET_CONDUCTOR_WINDOW_TO_FABLE_POLICY_ALREADY_SAID` — Every launcher that starts or restarts the Conductor window starts it on Fable 5.2 (policy already says so; this window woke on Opus 5.5)
- `RIMMANDRAKE_RESTORE_PAUSED_WORK_KEEP_EVERY_SPEND_CAP` — Lift every pause (Dispatcher PAUSE, testq, Relentless, Whittle, disabled roles and timers) and keep every spend cap (concept ceilings, 2x-cap park, pe
- `RIMMANDRAKE_BUILD_KNOCKBACK_CREATURE_MASS_AND_BLAST_POWER` — Explosive Knockback: a creature mass limit (150 kg, Mod Setting) replaces the body-size 2.5 cutoff; throw force = type force x this blast's damage / t
- `RIMMANDRAKE_FIX_PYRE_GRASS_CRAWLS_ON_DRY_ASH` — Pyrelands grasses grow at x0.1 on dry ash; owner: swift on dry ash, faster watered, crops as before
- `RIMMANDRAKE_BUILD_GSS_FLOOR_END_SHOCK_ANSWERED_WEEK_AGO` — GSS: every sparking floor-cord end shocks crossers, with a None/Only downed lines/All shock-reach setting (default All), and proof rows for both tree 
- `RIMMANDRAKE_ASK_PYRE_ROOT_STILL_PROMISES_PAVING_HOLDS` — Pyrelands root still promises paving stops the fire; its leaf is deleted
- `RIMMANDRAKE_BUILD_PYRE_SMOKE_WEATHER_ONLY_LONGSHADE_HAS_ONE` — Pyrelands has no choking-smoke weather; owner: it comes as its own weather
- `RIMMANDRAKE_BUILD_BLACK_RAIN_FILLS_MOATS_TANKS_STAY_DRY` — Black rain fills no moat or tank; owner: a rare chance to fill both
- `RIMMANDRAKE_BUILD_DEEP_TRIBES_TRADE_CODE_SAYS_NO_TRADE` — Deep Tribes offer no trade and no share rule; owner: trade, leave their share
- `RIMMANDRAKE_MEASURE_SCORCHFRUIT_FREEZER_FILL_CAPPED_AT_FORTY` — Scorch-fruit abundance unmeasured (cap 40 pods); owner: freezer stuffed
- `RIMMANDRAKE_ALIGN_HOT_TUB_VENT_BUBBLES_AND_WATER_SQUARE` — Hot tub misaligned: geyser vent, bubbles and dark-blue hot-tub square sit in three different places; soaker pit sat in an existing lake
- `RIMMANDRAKE_RESTRICT_HEAT_TO_GEYSER_BENEATH_PIT_WATER_ONLY` — RULE CHANGE: a geyser heats pit water only when the vent is beneath the pit water (a vent cell inside the pit), not merely within a radius
- `RIMMANDRAKE_PORT_FROUDE_CAP_TO_CSHARP_WATER_DECIDED_TWICE` — Port the Froude 0.544 face cap (local_inertial_frcap) into the C# local-inertial and re-time stage C
- `RIMMANDRAKE_SHOW_VENT_UNDER_ONE_METRE_BUBBLES_ON_IT` — Geyser vent invisible under 1 m of water in the G2 scene; bubbles drawn in the wrong (southern) area
- `RIMMANDRAKE_FIX_GEYSER_PIT_G2_SCENE_NEEDS_A_LADDER` — Geyser pit scene G2 had no way in (colonists could not enter); the scene staging lacks a ladder
- `RIMMANDRAKE_FIX_G8_SCENE_LABELS_SHOW_NO_PIT` — G8/G8b scene does not show what its labels claim: no pit or water visible; owner cannot tell what it measures
- `RIMMANDRAKE_FIX_DRAFTED_MOVE_IN_BIG_PIT_WALKS_SOUTH` — Drafted pawn ordered to a cell in a large pit: the target preview is right but the pawn walks to a different cell, usually further south
- `RIMMANDRAKE_FIX_PIT_EXPOSURE_THOUGHT_ON_LADDER_ENTRY` — 'Pit exposure' thought appears though the pawn entered willingly by a lowered ladder, and it stacks with soaking in a hot pool
- `RIMMANDRAKE_SINK_COOLER_ARROW_UNDER_TAR` — The Cooler's direction arrow still draws crisp above tar while the battery indicator is submerged
- `RIMMANDRAKE_DESIGN_LIQUID_DIRT_AS_CONDITION_NOT_GRAPHICS` — DESIGN pass (Designer, not a build): liquid dirtying of pawns (blood, oil, tar coverings) is graphically crude; should likely be a Condition (hediff);

## Commits

```
ffacaa0e3c conversations: catch-up 12 record(s)
799c55e4a7 ledger: detached run on RIMMANDRAKE_RESTORE_PAUSED_WORK_KEEP_EVERY_SPEND_CAP ended
c0e56f166c ledger: RIMMANDRAKE_PROVE_UNDER_LIQUID_LAW_LIVE clone bundled
cc0dcc4eea conversations: catch-up 1 record(s)
8ae0e89bf1 ledger: detached run on RIMMANDRAKE_PROVE_UNDER_LIQUID_LAW_LIVE ended
ca5b7aa70a owner look 2026-11-13: holding rows, items filed, two approvals closed
90b6b6c271 ledger: RIMMANDRAKE_HARDEN_FAST_WATER_SOLVERS_VIA_GPT_PIPES_RING clone bundled
a1aed88977 conversations: catch-up 1 record(s)
165f768a8f ledger: detached run on RIMMANDRAKE_HARDEN_FAST_WATER_SOLVERS_VIA_GPT_PIPES_RING ended
1c01f755b7 lesson: playwright headless chrome needs a libasound path on Archmagi WSL
546650c8d5 ledger: DISPATCHER notes (0)
cb9cda743a ledger: RUNNER ingest of 0 testq job(s)
4649aef280 ledger: RIMMANDRAKE_HARDEN_FAST_WATER_SOLVERS_VIA_GPT_PIPES_RING note; port-cap item; dt lesson
556d5d0f16 water decision: winner refined to local-inertial with a Froude 0.544 face cap; pipes cut; stage-2 figures
95eae30821 ledger: RUNNER ingest of 1 testq job(s)
973022c8d5 ledger: DISPATCHER notes (0)
e28aba373d Designer: RimMandrake/Pyrelands stage 3 done (run rm-role-designer-1794596464), harvest lands its own state
a0d5452ac6 Designer: Pyrelands stage 3 done (run rm-role-designer-1794596464), worldgen card cited
5746d33fb9 ledger: DISPATCHER notes (1)
199a10f056 ledger: RIMMANDRAKE_PROVE_PYRELANDS_IN_FOUR_SCENES clone bundled
... 314 more: git log --oneline 36e9b470ce..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-11-13T06:28:39Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/biome_ffar/scale_ground_measured.json   (pre-existing at this session's start (earlier seats/sweeps; not this window's))
 M deployed/config/ModsConfig.before-tier-pyrelands.xml   (pre-existing at this session's start (earlier seats/sweeps; not this window's))
 M design/concepts/GimmeSomeSlack/exam.json   (Dispatcher Designer role run rm-role-designer-1794595998 (GSS stage 3), writing in this clone since the PAUSE lift; leave it to that run)
 M design/concepts/GimmeSomeSlack/stage.json   (same Designer role run)
 M infrastructure/state/art_eval/briefs/RM_Chellow.json   (pre-existing at this session's start (earlier seats/sweeps; not this window's))
 M infrastructure/state/art_eval/briefs/RM_Gembug.json   (pre-existing at this session's start (earlier seats/sweeps; not this window's))
 M infrastructure/state/art_eval/briefs/RM_Krissek.json   (pre-existing at this session's start (earlier seats/sweeps; not this window's))
 M infrastructure/state/art_eval/briefs/RM_Lirrith.json   (pre-existing at this session's start (earlier seats/sweeps; not this window's))
 M infrastructure/state/art_eval/briefs/RM_TheUnfinished.json   (pre-existing at this session's start (earlier seats/sweeps; not this window's))
 M infrastructure/state/art_eval/briefs/RM_Wuum.json   (pre-existing at this session's start (earlier seats/sweeps; not this window's))
 M infrastructure/state/art_eval/briefs/RM_Ysvaltha.json   (pre-existing at this session's start (earlier seats/sweeps; not this window's))
 M infrastructure/state/art_eval/briefs/RM_Zrrik.json   (pre-existing at this session's start (earlier seats/sweeps; not this window's))
 M infrastructure/state/art_eval/briefs/SWPotF_RaceDef_ysalamir.json   (pre-existing at this session's start (earlier seats/sweeps; not this window's))
 M src/RimMandrake/FlowWorks/Tools/native_water_audit.md   (pre-existing at this session's start (earlier seats/sweeps; not this window's))
 M src/RimMandrake/FlowWorks/northstar/review/scenarios/map_r_placed.json   (pre-existing at this session's start (earlier seats/sweeps; not this window's))
?? cards.json   (pre-existing at this session's start (earlier seats/sweeps; not this window's))
?? deployed/config/ModsConfig.before-tier-mods__mandrake_rm_explosiveknockback__mandrake_rm_flowworks__mandrake_rm_gimmesomeslack__mandrake_rm_patches.xml   (pre-existing at this session's start (earlier seats/sweeps; not this window's))
?? deployed/config/ModsConfig.before-tier-weepingstones_solo.xml   (pre-existing at this session's start (earlier seats/sweeps; not this window's))
?? deployed/config/ModsConfig.swap-active.pyrelands.stale-20261112.json   (pre-existing at this session's start (earlier seats/sweeps; not this window's))
?? deployed/config/ModsConfig.swap-active.weepingstones_solo.stale-20261108.json   (pre-existing at this session's start (earlier seats/sweeps; not this window's))
?? design/RimMandrake/designer_drawing_out.md   (pre-existing at this session's start (earlier seats/sweeps; not this window's))
?? design/concepts/GimmeSomeSlack/result.json   (same Designer role run)
?? design/concepts/GimmeSomeSlack/result.rm-role-designer-1794595998.json   (same Designer role run)
?? design/concepts/Pyrelands/coverage_verdict.json   (Designer (Pyrelands), untracked since 2026-11-06 per the biomes helper; not this window's)
?? infrastructure/state/queue/BENCH.md.tmp.1153431.1794098233190787055   (pre-existing at this session's start (earlier seats/sweeps; not this window's))
?? infrastructure/state/queue/CLAUDE_ARCHMAGI_FWLIVE.md   (pre-existing at this session's start (earlier seats/sweeps; not this window's))
?? infrastructure/state/queue/CLAUDE_ARCHMAGI_OFFLINE1.md   (pre-existing at this session's start (earlier seats/sweeps; not this window's))
?? infrastructure/state/queue/CLAUDE_ARCHMAGI_OFFLINE2.md   (pre-existing at this session's start (earlier seats/sweeps; not this window's))
?? infrastructure/state/queue/CLAUDE_ARCHMAGI_OFFLINE3.md   (pre-existing at this session's start (earlier seats/sweeps; not this window's))
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_FWLIVE.md   (pre-existing at this session's start (earlier seats/sweeps; not this window's))
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE1.md   (pre-existing at this session's start (earlier seats/sweeps; not this window's))
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE2.md   (pre-existing at this session's start (earlier seats/sweeps; not this window's))
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE3.md   (pre-existing at this session's start (earlier seats/sweeps; not this window's))
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE4.md   (pre-existing at this session's start (earlier seats/sweeps; not this window's))
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE5.md   (pre-existing at this session's start (earlier seats/sweeps; not this window's))
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE6.md   (pre-existing at this session's start (earlier seats/sweeps; not this window's))
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE7.md   (pre-existing at this session's start (earlier seats/sweeps; not this window's))
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE8.md   (pre-existing at this session's start (earlier seats/sweeps; not this window's))
?? infrastructure/state/queue/CODEX_ARCHMAGI_FWDRAIN.md   (pre-existing at this session's start (earlier seats/sweeps; not this window's))
?? infrastructure/state/queue/CODEX_STEVEDESKTOP_HUGETHINGS.md   (pre-existing at this session's start (earlier seats/sweeps; not this window's))
?? ralph/.context_warned   (pre-existing at this session's start (earlier seats/sweeps; not this window's))
?? shortcuts.ps1.txt   (pre-existing at this session's start (earlier seats/sweeps; not this window's))
```

