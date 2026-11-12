# BENCH_REBOOT_HANDOFF_202611121724 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202611121350`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
Sittings beat pipelines today, and the reason is on disk: `design/RimMandrake/agent_systems_assessment_2026-11-12.md` (no builder loop has delivered an owner-accepted mod; 65% of commits are process). The working pattern this sitting: he looks at a staged scene, each remark becomes a fix by a helper, the helper TESTS IT ITSELF in the game before he sees it (an untested station cost his trust at 06:40), and long work goes to `detached_helper.py` so a reset loses nothing. Live proofs are now ~7x faster: paused steps over 60 ticks use `jawa/safe_advance` by default (pit exposure 457 s -> 63.8 s, `D:\ClaudeWork\rimmandrake\conductor\speed_20261112\results.md`). Every owner ruling of the sitting is quoted, dated, in `D:\ClaudeWork\rimmandrake\conductor\log.md` (tail it first).

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- A DETACHED Opus helper ($40 cap) is finishing Explosive Knockback on the Archmagi game (his approved items 1-7: surviving container, incendiary half strength, gas clumps, heavy-goods stagger, perf, tuning approved as is, release build + review) and deploying/proving the submerged pit fittings; its report for him lands at `D:\ClaudeWork\rimmandrake\conductor\ek_finish_20261112\REPORT.md` with saves to look at. Read it, look at its captures yourself, then bring him the looks.
- His looks today, all PASS in his words (log has them verbatim): EK flagship storeroom blast; EK flying goods ("Full pass I believe"; "No noticable delay"; "Tuning looks good"); pit retrieval by hauling; wall art ("The art all looks good") with one defect (fittings not submerged: built 2988a6ae234c, his look owed).
- One colonist (Georgette Dixon) died to the plain blast 2 cells from 25 shells in his run; told to him; no ruling asked.
- Pit contents under rising liquid (his inquiry): furniture can be built in a DRY pit, is refused in a wet one, and anything already there floods in place drawn dry; goods and minified items sit on top of the water and rot 3x faster; only ladders/ramp/spikes get the waterline cut. UNRULED. Options A rule only / B generic waterline cut for everything from fillPercent+drawSize / C B plus flooded-furniture and corrosion rules; helper recommends B. Put this to him by question card: `D:\ClaudeWork\rimmandrake\conductor\pit_contents_20261112\answer.md`.
- Open question for him: should "set fill to N" clear a cell's hidden part-notch (exact N x 0.5 m) or keep it (today)? (`D:\ClaudeWork\rimmandrake\conductor\fill_depth_20261112\table.md`).
- 24 Designer questions across four mods, by card, one mod at a time: `D:\ClaudeWork\rimmandrake\conductor\proofs_20261112\<Mod>\inventory.md`. First: Pyrelands ships its worldgen switch ON (conflicts with the no-worldgen ruling); HugeThings' 7 north-star bars are unvalidated agent drafts.
- Lexicon draft (`LEXICON.md`, audit `design/RimMandrake/lexicon_audit_2026-11-12.md`) has 11 unsettled word groups; he was offered a 15-minute grill on done/closed/accepted/shipped first. Map: `design/RimMandrake/production_system_map_2026-11-12.md`.
- He was offered and has NOT yet answered: building the at-work "one mod, one agent, one checklist" loop (assessment section 4; I proposed EK, $60/day, $8/line).
- Pit-exposure mood question (-3 per exposed prisoner, cap 5) still unanswered; save RM_PitExposure_Review_20261112T014420; worker recommends keep.
- Proof state measured today (lines proven/weak/none): FlowWorks 2/84/155 of 241, HugeThings 6/26/8, GSS 15/12/6, Pyrelands 2/19/4. GSS proof_all: 139 PASS / 7 FAIL (names in the speed results file), unread.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `RIMMANDRAKE_STAGE_KNOCKBACK_CONTAINER_SURVIVES_BLAST` -- detached run rm-detached-bench-rimmandrake-stage-knockback-container-su-1794504239 working EK items 1-7 + submerged fittings on the Archmagi game; NEXT: run `python3 src/RimMandrake/rimflow/detached_helper.py status`, read `D:\ClaudeWork\rimmandrake\conductor\ek_finish_20261112\REPORT.md` when it ends, check its captures, then show him its saves.
- `RIMMANDRAKE_LAND_KNOCKBACK_GOODS_NEVER_BUMP_RESIDENTS` -- real bug found in his frozen blast (a landing stack shoves the resident stack, unrecorded; one pushed out of the pit); the detached helper does not know of it; NEXT: give it to an Opus rm-builder after the detached run ends (same files).
- `RIMMANDRAKE_SUBMERGE_PIT_FITTINGS_BY_LEVEL` -- built 2988a6ae234c, offline green, live proof + his look owed (in the detached run's step B); NEXT: confirm the detached report covers it, else deploy FlowWorks and run `wall_art_scene.py ... submerge`.
- `RIMMANDRAKE_FIX_CLIMB_SLOW_OUTLASTS_LADDER` -- live rows pass (18/18 required), his look owed (ladder pits in save EK_SITTING_STATION4_FLYING_SHELVES_20261112: depth 1 at x118-120 z111-113, depth 4 at x125-127 z111-113); NEXT: ask him to order a climb and say if the slow part matches the ladder, then close with --owner-said.
- `RIMMANDRAKE_BUILD_WHITTLE_ADMISSION_AND_HARD_STOPS` -- built b86911a24e, selftests only; all Whittle units stopped+disabled on his order ("Stop the Whittle now"); NEXT: do NOT restart Whittle unasked; when he asks, read the 122 refusals in `D:\ClaudeWork\rimmandrake\conductor\whittle_admission_20261112.md` for over-strict rules first, then one worker to see the $20 cap work.
- `TICKBURST_PROVE_MANY_TICKS_ONE_FRAME` -- fast path landed and default, measured; close refused (owes criteria A1, A2, A6, A7, A8 incl. the 250/2,500/25,000 timing table); NEXT: have a Sonnet rm-fixer run `tickburst_bench.py` on SteveDesktop between queue jobs and close it with the table.
- `RIMMANDRAKE_PROVE_GSS_SWITCHBOARD_DENSE` -- GSS proof_all takes ~670 s with 3,402 single setting reads left and 7 FAIL rows unread; NEXT: read the 7 FAIL names in `D:\ClaudeWork\rimmandrake\conductor\speed_20261112\results.md` (mod bug or weak proof?), then route the remaining reads through `jawa/mod_settings_fields`.
- `RIMMANDRAKE_PROVE_PYRELANDS_IN_FOUR_SCENES` -- four scenes queued on SteveDesktop; first Pyrelands verdict today was FAIL (3 FAIL, 12 NOT_RUN) on a job predating the map-lookup fix; NEXT: regenerate `python3 src/RimMandrake/Utils/testq/steve_results.py` and read the Pyrelands rows run after 4418fd6809.
- `RIMMANDRAKE_PROVE_FLOWWORKS_TOGGLES_DENSE` -- 3 jobs queued on SteveDesktop; `selftest_flowworks_northstar` red because 285a403024 added mandrake.rm.patches to two tiers; NEXT: fix that selftest's expectation (Sonnet rm-fixer) and read the three job verdicts.
- `RIMMANDRAKE_PROVE_HUGETHINGS_DENSE_SCENES` -- one job queued; mod needs his Designer sitting before more proof work; NEXT: read the job verdict only; put HugeThings' 5 Designer questions on a card when he has time.
- `RIMMANDRAKE_TESTQ_PREFLIGHT_REFUSE_BEFORE_THE_GAME` -- preflight + deploy memo landed (5b84a35699, 6f4c65fc7f), no live hit measured yet; NEXT: after a few SteveDesktop jobs, read one job record for a memo skip and close both testq items with it.
- `STEVE_CRASHES_DIAGNOSE_DEFENDER_FALLS_TOO` -- by his ruling SteveDesktop's fault window is ADVISORY (results not quarantined, 12 h reboot between jobs, `D:\ClaudeWork\rimmandrake\testq\fault_advisory.json`); last night's Steve closes stand ("do not rerun them, use them"); NEXT: do not reopen a hardware diagnosis unasked; check the second 12 h reboot happened (~20:00 PST).
- `RIMMANDRAKE_PROVE_FLOWWORKS_FILL_AGAINST_DEPTH_METRES` -- no bug (0.5 m notch, card 2026-10-17); NEXT: ask him the part-notch question, record, close.
- `RIMMANDRAKE_DESIGN_KNOCKBACK_FIRST_TOUCH` -- superseded in practice by today's sitting (he chose live debugging); gate still refused; NEXT: when the detached run is in and he has seen the remaining scenes, put "certify the Explosive Knockback Designer pass / ship it?" to him by card.
- `SELFTEST_FIX_FLOWWORKS_STOCK_ELFQ` -- its selftest timed out under load, never read; NEXT: run `python3 src/RimMandrake/Utils/selftest_flowworks_stock.py` alone when the machine is quiet; pass closes it and FLOWWORKS_SELFTEST_FIX_FOUR_RED_AT_BASE.
- `PYRELANDS_TEXT_FIX_ENGINEERED_NEVER_SAID` -- stale per the Pyrelands helper (text already says "genetically engineered"); NEXT: verify in the def and `rimflow close` it with the proof.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- A staged scene handed to the owner untested shows nothing; every showing is detonated/exercised by the helper first (see: `infrastructure/state/lessons/`, today's EK staging lessons; rule already in conductor.md "Showings are pre-built").
- SteveDesktop's fault monitor quarantined every result silently; check `D:\ClaudeWork\rimmandrake\testq\fault_state.json` before promising validation there (see: `design/RimMandrake/testq_preflight_2026-11-12.md`).
- `rimworld/step_game_ticks` is one tick per frame (~55/s); never use it for long steps (see: `design/RimMandrake/live_test_speed_assessment_2026-11-12.md`).
- A helper that lands from `/home/mandrake/rm/bench` instead of a scratch clone leaves duplicate commits and stray DLLs here; every brief must say "scratch clone" (see: `design/RimMandrake/GIT_WORKFLOW.md`).
- A first proof brief of "one proof per ticket" is the week-per-mod trap; the dense rules are in `D:\ClaudeWork\rimmandrake\conductor\proofs_20261112\BRIEF.md` addendum (see: `design/RimMandrake/live_test_speed_assessment_2026-11-12.md` "The standard for new proofs").
- The fill number hides a part-notch: "fill 1" can be 0.9988 m (see: `infrastructure/state/lessons/` lesson of dbea087292).

## Closed since the last handoff (2)

- `RIMMANDRAKE_FIX_PARKED_WHITTLE_RUN_READS_AS_FAILED` — 6bdf5bc28f
- `RIMMANDRAKE_SPARE_THROWN_GOODS_SO_THEY_SCATTER` — a593f1668f1a

## Filed and still open (16) — the next seat's queue

- `RIMMANDRAKE_BUILD_WHITTLE_ADMISSION_AND_HARD_STOPS` — Whittle admission script (no model) and hard stops: $20 round cap, one rerun, close-ends-round, $3 broaden cap, park on cap
- `RIMMANDRAKE_PROVE_GSS_SWITCHBOARD_DENSE` — GSS dense proofs 2026-11-12: switchboard rows SW1-SW6 in proof_all core (highlight, lod, breakReadout, sparksOnlyOverlay, hideHookupWires, needlessLoo
- `RIMMANDRAKE_PROVE_PYRELANDS_IN_FOUR_SCENES` — Pyrelands: four dense live scenes proven; read results, compress slow rows
- `RIMMANDRAKE_PROVE_HUGETHINGS_DENSE_SCENES` — Prove HugeThings in 3 dense live scenes (plants --no-door, titan with untiered control, footprint) on one tier, exit 0/1/2
- `RIMMANDRAKE_FIX_CLIMB_SLOW_OUTLASTS_LADDER` — FlowWorks: ladder climb drawn slow along the whole floor-to-lip step (1+sink cells, 2.2 at D4), not just across the ladder art
- `RIMMANDRAKE_SUBMERGE_PIT_FITTINGS_BY_LEVEL` — FlowWorks: pit liquid covers ladders, spikes and the ramp up to its level
- `RIMMANDRAKE_PROVE_FLOWWORKS_FILL_AGAINST_DEPTH_METRES` — Check pit fill N vs depth M vs metres: table of every depth x fill (answer: 1 notch=0.5 m, consistent; F hides part-notch)
- `RIMMANDRAKE_PROVE_FLOWWORKS_TOGGLES_DENSE` — FlowWorks dense proofs 2026-11-12: pit rules (shooting/ladder/fall), liquids (ignition/corrosion), S3 re-run; built 13b5f96dbd, awaiting SteveDesktop 
- `RIMMANDRAKE_FIX_TICKBENCH_WSL_PATHS_UNDER_PYTHONEXE` — tickburst_bench.py out_root and tickburst_step.evidence_adoption_path ran ~/dev/Lodestar/bin/lib/agent_storage.py, absent under python.exe on SteveDes
- `RIMMANDRAKE_TESTQ_PREFLIGHT_REFUSE_BEFORE_THE_GAME` — testq worker refuses what would end INVALID before the job takes the game (stale swap marker, DLL older than C#, missing proof line)
- `RIMMANDRAKE_TESTQ_DEPLOY_MEMO_SKIP_UNCHANGED` — testq skips deploy plan and attest hashing when mods and game files are unchanged since the lane's previous job (TESTQ_DEPLOY_MEMO=1)
- `RIMMANDRAKE_STAGE_KNOCKBACK_CONTAINER_SURVIVES_BLAST` — Closed-container knockback cannot be shown in the 25-HE-shell storeroom: vanilla blast destroys every steel Hopper within r6 (measured d3.2-5.8, KB of
- `RIMMANDRAKE_WAIT_LOAD_READY_UNTIL_CURRENTMAP_SET` — rimworld/load_game_ready says 'map data available' before Find.CurrentMap is set: the first jawa/map_info reads 'No current map', and a resume raced i
- `RIMMANDRAKE_BATCH_PIT_REPORT_READS_IN_PIT_EXPOSURE` — pit_exposure_live makes 450-500 jawa/flowworks_pit_report calls (~25 s of a 64 s fast run) and 54 jawa/static_call: batch them (one report per sample 
- `RIMMANDRAKE_REVIEW_SPEED_BATCH_CODE_STILL_DIRTY` — Code review owed on speed_20261112 commits 0867cb89214f and c464224ff46e (validation_core, wrapup_debt, rimbridge_client, modcheck/suite, tickburst_st
- `RIMMANDRAKE_LAND_KNOCKBACK_GOODS_NEVER_BUMP_RESIDENTS` — EK: a landing knockback carrier places its stack Direct on an occupied cell, so vanilla GenSpawn shoves the resident stack aside unjournaled (and woul

## Commits

```
4fecd40d87 conversations: catch-up 2 record(s)
a9ba109c9e ledger: EK station4 frozen-blast read - owner look PASSED on RIMMANDRAKE_FLY_KNOCKBACK_GOODS_WILD, file RIMMANDRAKE_LAND_KNOCKBACK_GOODS_NEVER_BUMP_RESIDENTS, lesson list_things group All is blind
55586ec5f5 ledger: speed_20261112 - file three follow-ups, note measured evidence on TICKBURST and the tickbench WSL fix (closes refused by gate)
d5fabafef7 ledger: RIMMANDRAKE_SUBMERGE_PIT_FITTINGS_BY_LEVEL built at 2988a6ae234c (live proof and owner's look owed)
2a1d78b2cd EXCAVATION_WALL_ART_1: drop the open item copy (moved to closed/ in 2988a6ae234c)
2988a6ae23 RIMMANDRAKE_SUBMERGE_PIT_FITTINGS_BY_LEVEL: cut ladders, ramp and spikes at the true liquid level
45baadb467 ledger: EK station4 sitting - file RIMMANDRAKE_STAGE_KNOCKBACK_CONTAINER_SURVIVES_BLAST, note storage proof live result
c464224ff4 speed_20261112 2a/2b: jawa/mod_settings_fields (batched reads + one set) and probe_of on it
e306b332fb design: production system map, initial project LEXICON.md and its audit (owner request 2026-11-12)
16903276c6 ledger: testq preflight and deploy memo built, live proof owed
2403c7466b ledger: RUNNER ingest of 1 testq job(s)
686b042a17 tickburst_bench: throughput --arms narrows the run (A vs B40 at 25,000 ticks fits one sitting)
6f4c65fc7f testq deploy memo: lane switch file deploy_memo.on in TESTQ_HOME (env unset), env 0/1 still wins
0867cb8921 speed_20261112 1d/2c: one shared clock advance; client reroutes long step_game_ticks onto safe_advance
1156d7017e ledger: file testq preflight and deploy memo items (per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM)
5b84a35699 testq: preflight refuses what would end INVALID before the game (swap marker, DLL stamp, proof line); opt-in deploy memo skips unchanged deploy+attest
52694f1af1 ledger: RIMMANDRAKE_FLY_KNOCKBACK_GOODS_WILD built at 92e65812cbc8 (live proof and owner's look owed)
92e65812cb RIMMANDRAKE_FLY_KNOCKBACK_GOODS_WILD: thrown goods fly (arc, spin, ~70% rebound, settings); proof code fenced behind RM_PROOFS
e51e288739 RIMMANDRAKE_FIX_TICKBENCH_WSL_PATHS_UNDER_PYTHONEXE: tickburst bench/stepper resolve the out root through rmpaths (RM_DATA_ROOT) and the game dir through game_paths, not ~/dev/Lodestar (died under python.exe); selftest rows fail on the old code
0225a4eef5 ledger: RUNNER ingest of 1 testq job(s)
... 46 more: git log --oneline 6bdf5bc28f..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : GOING_DOWN
- Bridge: FREE    since 2026-11-12T17:22:16Z

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
 M src/RimMandrake/FlowWorks/Tools/native_water_audit.md   -- not mine: present at this session's start (earlier seat/helpers), left untouched
 M src/RimMandrake/FlowWorks/northstar/review/scenarios/map_r_placed.json   -- not mine: present at this session's start (earlier seat/helpers), left untouched
 M src/RimMandrake/HugeThings/Source/Kernel/RM_HugeTitanKernel.cs   -- today's HugeThings proof helper (worked in this clone); leftover, NOT verified against origin: diff before discarding
?? cards.json   -- not mine: present at this session's start (earlier seat/helpers), left untouched
?? deployed/config/ModsConfig.before-tier-mods__mandrake_rm_explosiveknockback__mandrake_rm_flowworks__mandrake_rm_gimmesomeslack__mandrake_rm_patches.xml   -- today's live staging helpers (tier swap backups); disposable
?? deployed/config/ModsConfig.before-tier-weepingstones_solo.xml   -- not mine: present at this session's start (earlier seat/helpers), left untouched
?? deployed/config/ModsConfig.swap-active.pyrelands.stale-20261112.json   -- today's live staging helpers (tier swap backups); disposable
?? deployed/config/ModsConfig.swap-active.weepingstones_solo.stale-20261108.json   -- not mine: present at this session's start (earlier seat/helpers), left untouched
?? design/RimMandrake/designer_drawing_out.md   -- not mine: present at this session's start (earlier seat/helpers), left untouched
?? design/concepts/Pyrelands/coverage_verdict.json   -- not mine: present at this session's start (earlier seat/helpers), left untouched
?? infrastructure/state/lessons/20261105T024235Z-CONDUCTOR-tmp-full-alarm-2026-11-05.md   -- not mine: present at this session's start (earlier seat/helpers), left untouched
?? infrastructure/state/queue/BENCH.md.tmp.1153431.1794098233190787055   -- not mine: present at this session's start (earlier seat/helpers), left untouched
?? infrastructure/state/queue/CLAUDE_ARCHMAGI_FWLIVE.md   -- not mine: present at this session's start (earlier seat/helpers), left untouched
?? infrastructure/state/queue/CLAUDE_ARCHMAGI_OFFLINE1.md   -- not mine: present at this session's start (earlier seat/helpers), left untouched
?? infrastructure/state/queue/CLAUDE_ARCHMAGI_OFFLINE2.md   -- not mine: present at this session's start (earlier seat/helpers), left untouched
?? infrastructure/state/queue/CLAUDE_ARCHMAGI_OFFLINE3.md   -- not mine: present at this session's start (earlier seat/helpers), left untouched
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_FWLIVE.md   -- not mine: present at this session's start (earlier seat/helpers), left untouched
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE1.md   -- not mine: present at this session's start (earlier seat/helpers), left untouched
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE2.md   -- not mine: present at this session's start (earlier seat/helpers), left untouched
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE3.md   -- not mine: present at this session's start (earlier seat/helpers), left untouched
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE4.md   -- not mine: present at this session's start (earlier seat/helpers), left untouched
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE5.md   -- not mine: present at this session's start (earlier seat/helpers), left untouched
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE6.md   -- not mine: present at this session's start (earlier seat/helpers), left untouched
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE7.md   -- not mine: present at this session's start (earlier seat/helpers), left untouched
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE8.md   -- not mine: present at this session's start (earlier seat/helpers), left untouched
?? infrastructure/state/queue/CODEX_ARCHMAGI_FWDRAIN.md   -- not mine: present at this session's start (earlier seat/helpers), left untouched
?? infrastructure/state/queue/CODEX_STEVEDESKTOP_HUGETHINGS.md   -- not mine: present at this session's start (earlier seat/helpers), left untouched
?? ralph/.context_warned   -- not mine: present at this session's start (earlier seat/helpers), left untouched
?? shortcuts.ps1.txt   -- not mine: present at this session's start (earlier seat/helpers), left untouched
```

