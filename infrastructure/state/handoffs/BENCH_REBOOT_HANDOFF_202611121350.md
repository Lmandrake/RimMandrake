# BENCH_REBOOT_HANDOFF_202611121350 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202611111355`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
Claude Whittle pays only on bounded, live-provable tickets, and only if tickets are checked by script before any model call. Last night's fleet (2026-11-11 19:48 PST on): ~$250 for 5-6 ledger closes; the offline lane picked epics and burned ~$165 for 1 close (owner stopped it: "No offline agents for now"). Live FW closes cost $16-18 each; one failed ticket cost $44.52. Measure in DOLLARS (cost_usd in loop.log) — raw token counts are ~90% cache reads and mislead. Status page: D:\ClaudeWork\rimmandrake\conductor\WHITTLE_NOW.md (open in Typora).

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- Owner rulings this session (by card unless quoted): engine for Whittle = "All Claude (System account)"; Archmagi account: "Use Steven until it is down to 60%, then switch to system please." (switching_plan_week_2026-11-05.json steven leave_pct_left 62, bdc3a94c45); Steve WSL disk "Keep it on the hard disk" (vhdx at Steve D:\WSL\Ubuntu, HDD); offline Whittles "No offline agents for now"; live FW Whittles "No cap, watch them" (he later asked "Why would a $25 cap help if $30-40 is what it took to close real tickets?" — answer: real closes cost $16-18; the $30-40 was an average incl. failures; no cap set).
- Explosive Knockback Designer pass: north star VALIDATED by card (4b405aa3d0); his flagship verbatim: "Just put a bomb into a storeroom with people in it beside a pit. Shows some items falling into the pit and some people as well."; all answers in D:\ClaudeWork\rimmandrake\designer\ExplosiveKnockback\sitting_2026-11-11.md. Gate still REFUSED (4 stage-3 gaps, coverage_verdict.json). He chose: "Let's do some live debugging runs together with me instead." then stopped the staging helper to try a new Conductor.
- Wall-art look waiting for him: EXCAVATION_WALL_ART_1 parked on A5 (his look), save EWA_WALL_ART_REVIEW_20261112.
- SteveDesktop FW Whittle closed PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL (ledger done) but its round kept working ~1.5 h past the close (transcript live 05:50 PST).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `CLAUDE_STEVEDESKTOP_FWLIVE` -- round 3 still running after its item closed in the ledger (PIPE_LEVELLING done); NEXT: read its last progress line; if it is broadening a closed item, touch D:\ClaudeWork\rimmandrake\whittle_claude\CLAUDE_STEVEDESKTOP_FWLIVE\STOP and ask the owner whether to keep the live lane.
- `CLAUDE_ARCHMAGI_FWLIVE` -- stopped by Conductor 05:5x PST for the owner's sitting (STOP file present; EXCAVATION_WALL_ART_1 parked on his look); NEXT: ask the owner whether to restart it (rm STOP; systemctl --user start whittle-claude@CLAUDE_ARCHMAGI_FWLIVE).
- `RIMMANDRAKE_DESIGN_KNOCKBACK_FIRST_TOUCH` -- Designer pass at stage 4 closed, gate REFUSED (no coverage signature; 4 gaps in design/concepts/ExplosiveKnockback/coverage_verdict.json); NEXT: run the owner's live debugging sitting on Explosive Knockback (Archmagi game, paused, he controls the clock) when he asks, then one capped (~10M) fix pass on the 4 gaps and put "certify the Explosive Knockback Designer pass?" to him.
- `RIMMANDRAKE_FIX_PARKED_WHITTLE_RUN_READS_AS_FAILED` -- a parked Whittle round reruns up to 3x (hook moves BLOCKED.md first); NEXT: fix it before restarting any live Whittle worker.
- `RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE` -- 97 FW ledger-open ids with no item file; NEXT: reconcile (close/drop with reason), owner not needed.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- Offline Whittle picker took epics (CATHEDRAL_*_1, WORLD_REMAKE_FINAL_STEP_1) (filed: infrastructure/state/lessons/20261112T063155Z-BENCH-claude-whittle-offline-lane-2026-11.md)
- Ghost tickets (ledger-open, no items/<ID>.md) cost ~$2 each to discover by model (filed: infrastructure/state/lessons/20261112T042646Z-BENCH-claude-whittle-loops-2026-11-11.md)
- Steve C: filled by a growing WSL vhdx -> WSL read-only (filed: infrastructure/state/lessons/20261112T052305Z-BENCH-steve-wsl-vhdx-moved-hdd.md)
- Dialog_NamePlayerFactionAndSettlement force-pauses a test game and re-raises; fix jawa/name_colony then close_window (see: skills/northstar-validation/SKILL.md modal_open row)
- Designer coverage judge loops (gaps 19,11,6,9,7,6,4,4; 90M tokens vs 4M cap) (filed: lesson 19110ef95b)

## Closed since the last handoff (1)

- `PUMP_OUTFLOW_FIX_PART_SOURCE_HOGS_DOOR` — e8d61372520ec131a22820837e03598825cabebf

## Filed and still open (26) — the next seat's queue

- `RIMMANDRAKE_FIX_ARTISANNOW_OLD_PASSES_DATED_TODAY` — ARTISAN_NOW passes table dates pyrelands passes 13-21 as today (Nov 10/11) but their head commits are Nov 7 19:40 to Nov 8 07:48; 'Tokens today ~23.92
- `RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE` — 97 FlowWorks/GSS items are open in the ledger with no items/<ID>.md and none in items/closed (54 proposed, 26 built, 10 validated, 5 doing, 2 ready; 5
- `RIMMANDRAKE_RETIRE_ROT_DONOR_SLOT_COPIES_ELEVEN_SHADOWED` — Retire the never-drawn donor-slot texture copies of 11 Rot ports (AgariluxPrime pattern)
- `RIMMANDRAKE_FIX_GIVEQUEST_DEFS_TWO_SILENT_LOAD_TRAPS` — KyberTradePlot quests: defaultChallengeRating on non-root quests (load config error); 11 RUT GiveQuest incidents keep World target (refused by storyte
- `RIMMANDRAKE_FIX_SLOT_SCAN_BLIND_TO_TEXPATH_PATCHES` — art_sheet IN GAME column shows the unpatched base texPath for patch-repointed defs (scan_def_slots ignores patches)
- `RIMMANDRAKE_BURY_GSS_CORDS_IN_FW_SUPERDEEP_PIT_WATER` — GSS lays a cord on FlowWorks' 2 m+ pit water (RM_Fill_Water_Superdeep is def-Standable) instead of diving
- `RIMMANDRAKE_HARDEN_ARC_LINT_PARAPHRASE_WALKS_PAST` — cathedral_arc_lint matches word patterns only: a paraphrased attribution passes ('The great machine beneath the dunes asks this of you.' --stage 2 -> 
- `RIMMANDRAKE_RESTORE_SEEPWAX_SOURCE_LOST_IN_TIER_MOVE` — RM_ThrummelSeepwax has no source since the Sump tier move deleted its RosterSource patch, so the weak tar solvent is uncraftable
- `RIMMANDRAKE_FIX_JAWABENCH_AWARENESS_INSTALL_CRASHES_START` — JawaBench awareness install crashes game start on 2 of 4 launches
- `RIMMANDRAKE_EXPLAIN_GSS_D2_SPLIT_ONCE_IN_TWELVE` — GSS D2 fresh-vs-incremental CordBuilder split once in 12 builds (B00, missing 1 + extra 1)
- `RIMMANDRAKE_FIX_CRITERIA_BULLETS_BREAK_PROOF_PARSE` — GSS_WATER_STUB_FIX_PASSED_LAST_WEEK.criteria uses '- ' bullets and a GREEN-MIN level; selftest_relentless_live_round 'every line parses' is RED since 
- `RIMMANDRAKE_MEASURE_HUGETHINGS_PLANT_PICTURE_SELECTION` — Give the plant showcase a real read of the giant plant's selection rect (row is UNMEASURED today)
- `RIMMANDRAKE_PAINT_SHIP_GIFTS_OWN_ART` — The 14 biome ship gifts still on stand-in art get their own textures
- `RIMMANDRAKE_DESIGN_KNOCKBACK_FIRST_TOUCH` — Explosive Knockback first-touch Designer pass (design/concepts/ExplosiveKnockback): stages 0-5 to a locked tree; owner certifies
- `RIMMANDRAKE_SLOW_RAIN_FILL_PIT_BRIMS_IN_ONE_NIGHT` — Rain fills a 4 m open pit to the brim in one night (~0.5 m/h); the prisoner swims out
- `RIMMANDRAKE_FLY_KNOCKBACK_GOODS_WILD` — Explosive Knockback: thrown goods truly fly (wild): arc, fast spin, rebound off walls until spent at ~70%; replaces the despawn-and-replace teleport a
- `RIMMANDRAKE_LIMIT_KNOCKBACK_STORAGE_CLOSED` — Explosive Knockback: drop the every-storage exemption (RM_MapComponent_Knockback.cs:399); only closed containers keep contents, and the container itse
- `RIMMANDRAKE_THROW_ALL_HARMFUL_BLASTS` — Explosive Knockback: every harmful explosion throws (bombs full, fire/incendiary half, other mods' damaging blasts too; not EMP/smoke/stun)
- `RIMMANDRAKE_CHAIN_FLAMMABLE_GAS_CLUMPS` — Explosive Knockback: flammable gas goes off clump by clump, each clump scattering goods and shoving people 1 cell (no damage, once per 2 s, never brea
- `RIMMANDRAKE_KNOCK_PEOPLE_HEAVY_GOODS` — Explosive Knockback: a flying heavy stack that hits a person gives a small blunt hit and a stagger; light goods pass through
- `RIMMANDRAKE_PROVE_KNOCKBACK_ALL_FLY_PERF` — Explosive Knockback: prove all-fly (no overflow cap) holds at most 50 ms per frame on a mortar barrage and a long gas chain on Archmagi; owns the walk
- `RIMMANDRAKE_PROVE_PIT_GOODS_RETRIEVABLE` — Explosive Knockback: prove goods thrown into a pit stay retrievable (a colonist fetches one from the pit floor down the ladder)
- `RIMMANDRAKE_REWRITE_KNOCKBACK_PROOFS_REAL_CONTROLS` — Explosive Knockback: rewrite the proof scenes so each asserts its start and runs a real control (17-row script audit)
- `RIMMANDRAKE_FIX_STRANDED_COLONIST_READS_UNTRAPPED_NO_RESCUE` — A colonist stranded in a sealed 4 m pit reads trapped=False; no rescue queues
- `RIMMANDRAKE_SCRUB_STEEL_LADDER_KEY_MAGENTA_FRINGE` — Steel fire-escape ladder E/W sprites carry near-invisible key-magenta fringe pixels (v5 side_from_north Lanczos ringing)
- `RIMMANDRAKE_FIX_PARKED_WHITTLE_RUN_READS_AS_FAILED` — A parked Whittle run reads as failed: the Stop hook files BLOCKED.md into history/ before run.py looks for it

## Commits

```
8f2643736a conversations: catch-up 12 record(s)
0a617382cc whittle setup: CLAUDE_ARCHMAGI_FWLIVE takes GSS_POWER_THEFT_FIX_WRONG_VICTIM
c063303e55 whittle wrap-up: EXCAVATION_WALL_ART_1 failed
b2ef27180e EXCAVATION_WALL_ART_1: still parked on A5 (owner's look); run 3 was the BLOCKED.md hook slip, nothing new
465e5da9dd EXCAVATION_WALL_ART_1: judge's half-covered pit was a harness fill-coordinate slip; still parked on A5 Filed RIMMANDRAKE_FIX_PARKED_WHITTLE_RUN_READS_AS_FAILED: the Stop hook moves BLOCKED.md before run.py reads it.
5c741eeaaf EXCAVATION_WALL_ART_1: judge would show; BLOCKED on A5 (the owner's look at EWA_WALL_ART_REVIEW_20261112)
76ba2ad188 EXCAVATION_WALL_ART_1: live A1-A4 evidence, BROADEN (fixed-camera change, staircases, trench spikes, fade, reload), DONE
7eff26d38e PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL: "checked on the next cycle" after any re-plumb, not only a load; doc says oil
e406c3fda2 EXCAVATION_WALL_ART_1: raised ladder E/W lose a key-magenta fringe pixel; spikes staged only where a player can build them
c7eea3291b PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL: judge (would show: yes); bridge released
210514fedb PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL: A5 on a real oil pit; A4 on unequal depths and a natural pond; walk caps fixed
da794ca755 ledger: live sweep LIVE_RESTORE_DISPATCHER broken
19de5cb09c whittle setup: CLAUDE_ARCHMAGI_FWLIVE takes EXCAVATION_WALL_ART_1
f9bbfe663c whittle wrap-up: PIT_TEMPERATURE_SOFTENING_1 failed
14cedf6170 PIT_TEMPERATURE_SOFTENING_1: judge would show: yes on wardened run 18; BLOCKED on A6 (the owner's look at run18_a6_panels.jpg)
62cc6b2390 PIT_TEMPERATURE_SOFTENING_1: BROADEN round 2 (roofing stops the pit's loss at once; the thought expires a day later); DONE on run 18
10edc11879 PIT_TEMPERATURE_SOFTENING_1: wardened A3 is UNMEASURED unless counted from placement, all three chatted, the pit no more
ce35035e14 ledger: live sweep LIVE_RESTORE_DISPATCHER kept
91394c79c9 Rebuild RimMandrakeFlowWorks.dll from committed source at landing
0bedc0e76e PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL: A3 rerun on two 40,000-square basins; reel says where a levelling end lies
... 454 more: git log --oneline 2c55c24396..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: other   stevedesktop  CLAUDE_STEVEDESKTOP_FWLIVE  since 2026-11-12T10:29:24Z  for: PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL: final evidence

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/biome_ffar/scale_ground_measured.json   -- not mine: present at this session's start (earlier seat/helpers), left untouched
 M deployed/config/ModsConfig.before-tier-pyrelands.xml   -- not mine: present at this session's start (earlier seat/helpers), left untouched
 M infrastructure/state/art_eval/briefs/RM_Chellow.json   -- not mine: present at this session's start (earlier seat/helpers), left untouched
 M infrastructure/state/art_eval/briefs/RM_Gembug.json   -- not mine: present at this session's start (earlier seat/helpers), left untouched
 M infrastructure/state/art_eval/briefs/RM_Krissek.json   -- not mine: present at this session's start (earlier seat/helpers), left untouched
 M infrastructure/state/art_eval/briefs/RM_Lirrith.json   -- not mine: present at this session's start (earlier seat/helpers), left untouched
 M infrastructure/state/art_eval/briefs/RM_TheUnfinished.json   -- not mine: present at this session's start (earlier seat/helpers), left untouched
 M infrastructure/state/art_eval/briefs/RM_Wuum.json   -- not mine: present at this session's start (earlier seat/helpers), left untouched
 M infrastructure/state/art_eval/briefs/RM_Ysvaltha.json   -- not mine: present at this session's start (earlier seat/helpers), left untouched
 M infrastructure/state/art_eval/briefs/RM_Zrrik.json   -- not mine: present at this session's start (earlier seat/helpers), left untouched
 M infrastructure/state/art_eval/briefs/SWPotF_RaceDef_ysalamir.json   -- not mine: present at this session's start (earlier seat/helpers), left untouched
 M infrastructure/state/ledger/events/BENCH.jsonl   -- mine (bridge take/release events), committed with this handoff
 M src/RimMandrake/FlowWorks/Tools/native_water_audit.md   -- not mine: present at this session's start (earlier seat/helpers), left untouched
 M src/RimMandrake/FlowWorks/northstar/review/scenarios/map_r_placed.json   -- not mine: present at this session's start (earlier seat/helpers), left untouched
?? cards.json   -- not mine: present at this session's start (earlier seat/helpers), left untouched
?? deployed/config/ModsConfig.before-tier-weepingstones_solo.xml   -- not mine: present at this session's start (earlier seat/helpers), left untouched
?? deployed/config/ModsConfig.swap-active.weepingstones_solo.stale-20261108.json   -- not mine: present at this session's start (earlier seat/helpers), left untouched
?? design/RimMandrake/designer_drawing_out.md   -- not mine: present at this session's start (earlier seat/helpers), left untouched
?? design/concepts/Pyrelands/coverage_verdict.json   -- not mine: present at this session's start (earlier seat/helpers), left untouched
?? infrastructure/state/lessons/20261105T024235Z-CONDUCTOR-tmp-full-alarm-2026-11-05.md   -- not mine: present at this session's start (earlier seat/helpers), left untouched
?? infrastructure/state/queue/BENCH.md.tmp.1153431.1794098233190787055   -- rimflow queue projections rendered by Whittle/Codex workers (generated, not committed)
?? infrastructure/state/queue/CLAUDE_ARCHMAGI_FWLIVE.md   -- rimflow queue projections rendered by Whittle/Codex workers (generated, not committed)
?? infrastructure/state/queue/CLAUDE_ARCHMAGI_OFFLINE1.md   -- rimflow queue projections rendered by Whittle/Codex workers (generated, not committed)
?? infrastructure/state/queue/CLAUDE_ARCHMAGI_OFFLINE2.md   -- rimflow queue projections rendered by Whittle/Codex workers (generated, not committed)
?? infrastructure/state/queue/CLAUDE_ARCHMAGI_OFFLINE3.md   -- rimflow queue projections rendered by Whittle/Codex workers (generated, not committed)
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_FWLIVE.md   -- rimflow queue projections rendered by Whittle/Codex workers (generated, not committed)
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE1.md   -- rimflow queue projections rendered by Whittle/Codex workers (generated, not committed)
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE2.md   -- rimflow queue projections rendered by Whittle/Codex workers (generated, not committed)
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE3.md   -- rimflow queue projections rendered by Whittle/Codex workers (generated, not committed)
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE4.md   -- rimflow queue projections rendered by Whittle/Codex workers (generated, not committed)
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE5.md   -- rimflow queue projections rendered by Whittle/Codex workers (generated, not committed)
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE6.md   -- rimflow queue projections rendered by Whittle/Codex workers (generated, not committed)
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE7.md   -- rimflow queue projections rendered by Whittle/Codex workers (generated, not committed)
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE8.md   -- rimflow queue projections rendered by Whittle/Codex workers (generated, not committed)
?? infrastructure/state/queue/CODEX_ARCHMAGI_FWDRAIN.md   -- rimflow queue projections rendered by Whittle/Codex workers (generated, not committed)
?? infrastructure/state/queue/CODEX_STEVEDESKTOP_HUGETHINGS.md   -- rimflow queue projections rendered by Whittle/Codex workers (generated, not committed)
?? ralph/.context_warned   -- not mine: present at this session's start (earlier seat/helpers), left untouched
?? shortcuts.ps1.txt   -- not mine: present at this session's start (earlier seat/helpers), left untouched
```

