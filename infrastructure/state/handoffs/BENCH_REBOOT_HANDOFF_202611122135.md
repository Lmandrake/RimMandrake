# BENCH_REBOOT_HANDOFF_202611122135 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202611121724`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
The owner has turned FlowWorks toward a ground-up water redesign, decided in one afternoon and all on disk: (1) water is true height / true decilitres only, every whole-step "fill N" for water is deleted (history `D:\ClaudeWork\rimmandrake\conductor\fill_history_20261112\HISTORY.md`); (2) FULL conversion of natural water to filled pits with a bed map (`design/specs/2026-11-12-flowworks-natural-water-as-pits-feasibility.md`); (3) rivers by the per-square level model with the current read from real flux (`design/specs/2026-11-12-flowworks-rivers-design.md`, solver cost is the open risk, offline first); (4) things in liquid "stand on their bottom", seen through clear liquids; (5) a whole-map elevation study is running detached. NOTHING of this is built; builds of (1) and (4) wait on the redesign. His words for every ruling are verbatim and dated in the Conductor log (tail it first). Second thing: he works by looking at MATRIX scenes (one cell replicated over the variables) and a fresh open-question judge ("does anything look odd?") pre-looks them; a builder's "by design" never overrules the judge.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- Looks owed, saves ready: pit fittings matrix `SUBMERGE_PIT_FITTINGS_MATRIX_20261112` (44 pits; report + two judges' doubts in `D:\ClaudeWork\rimmandrake\conductor\submerge_matrix_20261112\`); Explosive Knockback round 2: `EK_LOOK_CONTAINER_MATRIX_20261112` (loaded, paused), `EK_LOOK_GAS_CLUMPS_MATRIX_20261112`, `EK_LOOK_HEAVY_GOODS_MATRIX_20261112`, `EK_LOOK_LANDING_MATRIX_20261112` (report + judge doubts in `...\conductor\ek_round2_20261112\`; worth his eye: closed-container contents drawn outside the container after the throw; contents never visible in any capture).
- Question sets unanswered (card them, one topic at a time): natural water (6, feasibility doc), fill history (5, HISTORY.md), rivers (3: upstream edge, carry speed, waves; `...\conductor\rivers_20261112\FINAL_REPORT.md`), clear water (object heights, how clear, findable at 5 m+).
- Whole-map elevation study (he expects "do not do"): detached Fable 5.2 run, report to `D:\ClaudeWork\rimmandrake\conductor\elevation_20261112\FINAL_REPORT.md`. Read it, look at its mock-ups, bring it to him.
- Fleet monitor: he chose panel B, dense, percent LEFT, Codex as 4th tile, no notifications, reopen always, front page; "Port Augur now" with the Dashboard as an optional add-on (decisions `D:\ClaudeWork\claude-dash-design\DECISIONS.md`). Merging branch `augur-wsl` to main is his call after a Mac check.
- claude-dash hooks were applied to the global settings through Lodestar (`52106ce1`); backups `D:\ClaudeWork\backups\claude-settings\settings.json.20261112T115926`. The usage header of the old terminal tool reads 0% and is wrong.
- By card today: Exposed Prisoner mood stays -3, cap 5. Earlier asks still open from the morning: the "one mod, one agent, one checklist" loop offer; 24 Designer questions (Pyrelands worldgen switch ON conflicts with the no-worldgen ruling); Lexicon grill on done/closed/accepted/shipped; the ladder-slowdown look (RIMMANDRAKE_FIX_CLIMB_SLOW_OUTLASTS_LADDER).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `RIMMANDRAKE_STUDY_WHOLE_MAP_ELEVATION_OWNER_EXPECTS_A_NO` -- detached Fable 5.2 run rm-detached-bench-rimmandrake-study-whole-map-elevation-ow-1794519164 ($80) working; NEXT: run `python3 src/RimMandrake/rimflow/detached_helper.py status`, and when it ends read `D:\ClaudeWork\rimmandrake\conductor\elevation_20261112\FINAL_REPORT.md` and its mock-ups, then bring him the verdict.
- `MANDRAKEWORKFLOWS_PORT_AUGUR_TO_WSL_WITH_FLEET_DASHBOARD` -- Opus helper building in clone /home/mandrake/mw/augur-wsl, branch augur-wsl (in-process: dies with this window; owner said do not interrupt, he reboots after it finishes); no Lodestar ticket exists (ticket.py hung); NEXT: read `D:\ClaudeWork\claude-dash-design\BUILD_PROGRESS.md`; if the build is unfinished, relaunch it from its last pushed commit with the brief in this session's log, and file the ticket-tool hang.
- `RIMMANDRAKE_SUBMERGE_PIT_FITTINGS_BY_LEVEL` -- north-ladder fix 029034d0efce and gate cut 9a0a6daa0385 landed, matrix 2204 rows 0 FAIL, his look owed; NEXT: load save SUBMERGE_PIT_FITTINGS_MATRIX_20261112 for him, give him the two VERDICT.md doubt lists, close with --owner-said or file what he confirms.
- `RIMMANDRAKE_LAND_KNOCKBACK_GOODS_NEVER_BUMP_RESIDENTS` -- fixed in round 2 (code 0808c553030c, 35/35, release build deployed), his look owed with the other three matrices; NEXT: show him the four EK_LOOK_* saves with `D:\ClaudeWork\rimmandrake\conductor\ek_round2_20261112\prelook_open\VERDICT.md`, then close each item on his words.
- `RIMMANDRAKE_THROW_CLOSED_CRATES_WHOLE_CONTENTS_RIDE_SAFE` -- built; judge saw contents drawn outside the crock and locker; NEXT: have an Opus rm-builder check by state read whether contents really stay inside after a throw and add a capture that shows it.
- `RIMMANDRAKE_DESIGN_NATURAL_WATER_AS_PITS_NOT_FLAT_PONDS` -- feasibility and rivers designs published, full conversion ruled, questions unanswered; NEXT: card him the natural-water questions, then the rivers three, then file build tickets (first one: the offline Python fix of the river solver's 1,600 iterations per pulse, trying his conserving smoothing pass).
- `RIMMANDRAKE_REMOVE_FILL_STEPS_EXACT_WATER_ONLY_EVERYWHERE` -- ruled, not built (about 40 code readers, every bridge tool, 68 test scripts); NEXT: card him HISTORY.md's five questions, then split into build tickets.
- `RIMMANDRAKE_DRAW_PIT_CONTENTS_STANDING_ON_THEIR_BOTTOM` -- ruled, not built; see-through fix is half a day to a day (extend the 2026-10-06 see-through layer to vanilla water on dug squares); NEXT: ask him object heights and clarity, then file the see-through fix as its own ticket.
- `RIMMANDRAKE_FIX_CAPTURE_ZOOM_WONT_TIGHTEN_ON_SCENES` -- filed, untouched; NEXT: give it to a Sonnet rm-fixer with the bridge when the game is free.
- `RIMMANDRAKE_INVENTORY_VALIDATION_SCHEMES_BEFORE_ANY_LADDER` -- inventory published a7fc3698698d (55 schemes), UNREAD by the Conductor and not shown to him; NEXT: read `design/RimMandrake/validation_inventory_2026-11-12.md`, then card him the stage ladder and rules (he chose "map plus rules").
- `SCENE_LOOK_JUDGE_BRIEF` -- `design/RimMandrake/scene_look_judge_brief.md` still has the checklist-first shape; the calibration RESULT.md and its lesson score the judges against the WRONG pit (the fault was the brim pit; both naive judges caught it); NEXT: correct RESULT.md and that lesson, reshape the brief to an open first pass by one judge and the checklist by a different judge, add "by design never overrules a judge".
- `WHITTLE_PAGE_ACCOUNT_LINE` -- owner chose the fleet page as front page, so the account line must come off the Whittle page (RimMandrake code); NEXT: file it and give it to a Sonnet rm-fixer once the Augur dashboard draws accounts.
- The morning's pointers not touched this session are unchanged in `BENCH_REBOOT_HANDOFF_202611121724` (TICKBURST, GSS switchboard, Pyrelands scenes, FlowWorks toggles, HugeThings scenes, testq preflight, SteveDesktop second reboot check, EK first-touch certification card, FLOWWORKS_STOCK selftest, Pyrelands text) -- state as written there; NEXT: run `handoff.py --wake` output against that file and pick each up or close it.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- The CLI alias `--model fable` is Fable 5.1 here; pass the full id and read the transcript's model field (filed: lessons/20261112T213340Z-CONDUCTOR-cli-alias-fable-5-1).
- He edits files on the D: mirror by hand (LEXICON.md); the mirror sync overwrites it. Carry his copy into the clone and publish at once (see: Conductor log 2026-11-12 18:1x Z).
- Global Claude config is Lodestar-managed: `claudeconf.py settings --apply` writes nothing when live has drifted; `--adopt` is the route (see: `D:\ClaudeWork\claude-dash-design\AUGUR_SPRITES_FEASIBILITY.md` and Lodestar 52106ce1).
- A staged look is a matrix, pre-looked by a fresh open-question judge who saves the exact images judged (filed: lessons/20261112T184403Z-CONDUCTOR-owner-looks-are-matrix-not-one; memory owner-looks-are-a-matrix-not-one-case).
- Anything he must look at is opened for him and named by full Windows path (filed: memory open-what-he-must-look-at).
- Detached helpers cannot receive messages; in-process ones can but die with the window (see: `src/RimMandrake/rimflow/roles/conductor.md` Goodbye section).

## Closed since the last handoff (4)

- `RIMMANDRAKE_STAGE_KNOCKBACK_CONTAINER_SURVIVES_BLAST` — bb195048ac51
- `STEVE_LANE_UNSTICK_PAUSED_UNOWNED_0196` — 4a69e3571f
- `RIMMANDRAKE_LAND_KNOCKBACK_GOODS_NEVER_BUMP_RESIDENTS` — 0808c553030c
- `RIMMANDRAKE_LIFT_KNOCKBACK_THROW_CAPS_PLAN_SAYS_GONE` — done by verify, no close

## Filed and still open (14) — the next seat's queue

- `RIMMANDRAKE_INVENTORY_VALIDATION_SCHEMES_BEFORE_ANY_LADDER` — Inventory every verification and validation scheme (what it proves, cost, machine, LLM need, last run) so the owner can argue a stage ladder and rules
- `RIMMANDRAKE_REPAIR_FRAME_HIST_READS_THREE_WAYS_WRONG` — jawa/health tps.frame-hist: (1) the session/merged JSON string is malformed (the slow array is never closed before p50RangeMs), so json.loads fails; (
- `RIMMANDRAKE_FIX_CAPTURE_ZOOM_WONT_TIGHTEN_ON_SCENES` — Scene captures do not tighten when the helper sets camera zoom, so an agent's pre-look of a staged scene cannot see detail (reported by the EK finish 
- `RIMMANDRAKE_THROW_CLOSED_CRATES_WHOLE_CONTENTS_RIDE_SAFE` — EK: a blast-hit closed container (crate, chest, locker) is THROWN as one unit, shorter than loose goods by mass, its contents inside and taking no bla
- `RIMMANDRAKE_SHADE_GATE_SHADOW_SPILLS_OUT_OF_THE_PIT` — A sluice or grate standing on a pit floor casts its full static sun shadow across the pit and onto the bank, unchanged when the gate is mostly under l
- `RIMMANDRAKE_FADE_DEEP_PIT_HALO_DARKENS_THE_BANK` — A pit holding 3.5 m or more of liquid (water or tar) gets a dark halo on the ground round its rim, about a cell wide; at 3 m there is none (matrix D:/
- `RIMMANDRAKE_FIX_LIP_COVER_STRIPES_A_SWIMMER` — A colonist standing in a 4 m pit holding 2.5 m of water was drawn as a dark striped staircase block (the near-lip cover pieces in the wrong material) 
- `RIMMANDRAKE_ALIGN_FILL_GRID_LAGS_TRUE_BRIM` — A pit can read fill grid 3 with a true level of 4.00 notches (EWA_SUBMERGE_REVIEW_20261112, 113,104): the wall faces (drawn from the fill grid) then s
- `RIMMANDRAKE_DECIDE_GOODS_AND_SWALE_UNDER_LIQUID` — Goods (a steel stack, a minified table) and the swale liner lying on a pit floor draw on top of the liquid at every depth, even 4 m. Cut or hide them 
- `RIMMANDRAKE_DRAW_PIT_CONTENTS_STANDING_ON_THEIR_BOTTOM` — Every object in a liquid stands on its bottom: a split line rises up it by its drawn size until it is under; clear liquids show the lower part through
- `RIMMANDRAKE_REMOVE_FILL_STEPS_EXACT_WATER_ONLY_EVERYWHERE` — Water is stored and spoken only as true height / true decilitres; delete every whole-step fill N for water in code, bridge tools, readouts and tests; 
- `RIMMANDRAKE_DESIGN_NATURAL_WATER_AS_PITS_NOT_FLAT_PONDS` — Redesign with the owner how FlowWorks handles large natural bodies: at map load they become real pits with a bottom altitude map, filled to match, kee
- `RIMMANDRAKE_POINT_SEAL_FOODS_AT_REAL_TEXTURES_SEVEN_BLANKS` — Cold Storage: 7 sealed foods (RM_SandDried{Meat,Fruit,Fungus}, RM_TarSealed{Meat,Fish,Egg,Produce}, Defs/Seals/Seals_Items.xml) point at Things/Item/R
- `RIMMANDRAKE_STUDY_WHOLE_MAP_ELEVATION_OWNER_EXPECTS_A_NO` — Design study: one altitude value for every map tile, pits extended above zero, hills and mountains as raised land (Fable design, GPT teardown and rebu

## Commits

```
cdda8e7a3d conversations: catch-up 3 record(s)
eabe08255e lesson: CLI alias 'fable' is Fable 5.1; pass the full id and read the transcript's model field
450c6e99de detached_helper: 'fable' passes the full claude-fable-5-2 id
6be934c577 ledger: RIMMANDRAKE_STUDY_WHOLE_MAP_ELEVATION_OWNER_EXPECTS_A_NO clone bundled
8d101dd62c ledger: detached run on RIMMANDRAKE_STUDY_WHOLE_MAP_ELEVATION_OWNER_EXPECTS_A_NO ended
e576488477 detached_helper: accept --model fable, drop banned haiku; ledger: file whole-map elevation study, note smoothing idea
0b7aa4aea3 ledger: owner signs up for full conversion of natural water to filled pits; rivers design pass
9bb7d4e57e design: FlowWorks rivers, final design report (RIMMANDRAKE_DESIGN_NATURAL_WATER_AS_PITS_NOT_FLAT_PONDS)
050cfb0cd3 ledger: RIMMANDRAKE_LAND_KNOCKBACK_GOODS_NEVER_BUMP_RESIDENTS clone bundled
bdeeea6515 conversations: catch-up 1 record(s)
4f1a4ba71a ledger: detached run on RIMMANDRAKE_LAND_KNOCKBACK_GOODS_NEVER_BUMP_RESIDENTS ended
e261ef4a71 ledger: EK round 2 done
26224ca4ba ledger: file Cold Storage seal-food texture bug
6288546d5e lessons: EK round 2 (capture lag, multi-tick blast wave, Cauldron gas chain density, undestroyable staging, perf flag)
548a931f10 ledger: EK round 2 runs; bump and caps items closed
0808c55303 EK round 2: no throw caps, landings never shove residents, closed containers thrown whole, heavy goods knock, Cauldron gas bursts Cause of the bump: GenPlace Direct spawns a stackLimit-1 thing into a full cell and GenSpawn moves the resident. Proofs: container_thrown, heavy_knock, land_no_bump(_pit), gas_clumps, all_fly_no_cap; each red under its planted break.
7a7d2ad7ec design: FlowWorks natural water as pits, feasibility study (RIMMANDRAKE_DESIGN_NATURAL_WATER_AS_PITS_NOT_FLAT_PONDS)
4c635b3806 ledger: RUNNER ingest of 0 testq job(s)
6fca372754 ledger: owner rulings 2026-11-12: contents stand on their bottom; exact water only, no fill N; open the natural-water-as-pits redesign
7ca339f546 ledger: steward retired a recovered incident
... 44 more: git log --oneline cb1a4c8e21..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-11-12T20:31:48Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/biome_ffar/scale_ground_measured.json   -- not this window's: already dirty at the 09:51 wake (older seats' leftovers)
 M deployed/config/ModsConfig.before-tier-pyrelands.xml   -- not this window's: already dirty at the 09:51 wake (older seats' leftovers)
 M infrastructure/state/art_eval/briefs/RM_Chellow.json   -- not this window's: already dirty at the 09:51 wake (older seats' leftovers)
 M infrastructure/state/art_eval/briefs/RM_Gembug.json   -- not this window's: already dirty at the 09:51 wake (older seats' leftovers)
 M infrastructure/state/art_eval/briefs/RM_Krissek.json   -- not this window's: already dirty at the 09:51 wake (older seats' leftovers)
 M infrastructure/state/art_eval/briefs/RM_Lirrith.json   -- not this window's: already dirty at the 09:51 wake (older seats' leftovers)
 M infrastructure/state/art_eval/briefs/RM_TheUnfinished.json   -- not this window's: already dirty at the 09:51 wake (older seats' leftovers)
 M infrastructure/state/art_eval/briefs/RM_Wuum.json   -- not this window's: already dirty at the 09:51 wake (older seats' leftovers)
 M infrastructure/state/art_eval/briefs/RM_Ysvaltha.json   -- not this window's: already dirty at the 09:51 wake (older seats' leftovers)
 M infrastructure/state/art_eval/briefs/RM_Zrrik.json   -- not this window's: already dirty at the 09:51 wake (older seats' leftovers)
 M infrastructure/state/art_eval/briefs/SWPotF_RaceDef_ysalamir.json   -- not this window's: already dirty at the 09:51 wake (older seats' leftovers)
 M src/RimMandrake/FlowWorks/Tools/native_water_audit.md   -- not this window's: already dirty at the 09:51 wake (older seats' leftovers)
 M src/RimMandrake/FlowWorks/northstar/review/scenarios/map_r_placed.json   -- not this window's: already dirty at the 09:51 wake (older seats' leftovers)
 M src/RimMandrake/HugeThings/Source/Kernel/RM_HugeTitanKernel.cs   -- not this window's: already dirty at the 09:51 wake (older seats' leftovers)
?? cards.json   -- not this window's: already dirty at the 09:51 wake (older seats' leftovers)
?? deployed/config/ModsConfig.before-tier-mods__mandrake_rm_explosiveknockback__mandrake_rm_flowworks__mandrake_rm_gimmesomeslack__mandrake_rm_patches.xml   -- not this window's: already dirty at the 09:51 wake (older seats' leftovers)
?? deployed/config/ModsConfig.before-tier-weepingstones_solo.xml   -- not this window's: already dirty at the 09:51 wake (older seats' leftovers)
?? deployed/config/ModsConfig.swap-active.pyrelands.stale-20261112.json   -- not this window's: already dirty at the 09:51 wake (older seats' leftovers)
?? deployed/config/ModsConfig.swap-active.weepingstones_solo.stale-20261108.json   -- not this window's: already dirty at the 09:51 wake (older seats' leftovers)
?? design/RimMandrake/designer_drawing_out.md   -- not this window's: already dirty at the 09:51 wake (older seats' leftovers)
?? design/concepts/Pyrelands/coverage_verdict.json   -- not this window's: already dirty at the 09:51 wake (older seats' leftovers)
?? infrastructure/state/lessons/20261105T024235Z-CONDUCTOR-tmp-full-alarm-2026-11-05.md   -- not this window's: already dirty at the 09:51 wake (older seats' leftovers)
?? infrastructure/state/queue/BENCH.md.tmp.1153431.1794098233190787055   -- not this window's: already dirty at the 09:51 wake (older seats' leftovers)
?? infrastructure/state/queue/CLAUDE_ARCHMAGI_FWLIVE.md   -- not this window's: already dirty at the 09:51 wake (older seats' leftovers)
?? infrastructure/state/queue/CLAUDE_ARCHMAGI_OFFLINE1.md   -- not this window's: already dirty at the 09:51 wake (older seats' leftovers)
?? infrastructure/state/queue/CLAUDE_ARCHMAGI_OFFLINE2.md   -- not this window's: already dirty at the 09:51 wake (older seats' leftovers)
?? infrastructure/state/queue/CLAUDE_ARCHMAGI_OFFLINE3.md   -- not this window's: already dirty at the 09:51 wake (older seats' leftovers)
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_FWLIVE.md   -- not this window's: already dirty at the 09:51 wake (older seats' leftovers)
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE1.md   -- not this window's: already dirty at the 09:51 wake (older seats' leftovers)
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE2.md   -- not this window's: already dirty at the 09:51 wake (older seats' leftovers)
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE3.md   -- not this window's: already dirty at the 09:51 wake (older seats' leftovers)
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE4.md   -- not this window's: already dirty at the 09:51 wake (older seats' leftovers)
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE5.md   -- not this window's: already dirty at the 09:51 wake (older seats' leftovers)
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE6.md   -- not this window's: already dirty at the 09:51 wake (older seats' leftovers)
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE7.md   -- not this window's: already dirty at the 09:51 wake (older seats' leftovers)
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE8.md   -- not this window's: already dirty at the 09:51 wake (older seats' leftovers)
?? infrastructure/state/queue/CODEX_ARCHMAGI_FWDRAIN.md   -- not this window's: already dirty at the 09:51 wake (older seats' leftovers)
?? infrastructure/state/queue/CODEX_STEVEDESKTOP_HUGETHINGS.md   -- not this window's: already dirty at the 09:51 wake (older seats' leftovers)
?? ralph/.context_warned   -- not this window's: already dirty at the 09:51 wake (older seats' leftovers)
?? shortcuts.ps1.txt   -- not this window's: already dirty at the 09:51 wake (older seats' leftovers)
```

