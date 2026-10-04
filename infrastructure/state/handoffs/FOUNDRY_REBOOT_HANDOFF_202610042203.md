# FOUNDRY_REBOOT_HANDOFF_202610042203 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202610040745`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
This window finished ONE mod's Northstar checkout end to end (MessyConduit, now to be renamed Gimme Some Slack): live proof on the 9-mod `messyconduit` tier takes ~10 min total (core 84 s, matrix 338 s) after one bridge-tool cache fix (matrix 2,640 s -> 610 s -> 338 s), the matrix is recorded GREEN (121 PASS, 1 deliberate SKIP) and core is REFUSED only on 4 non-build scope rows, and the owner's 'for the human' review map (gallery of 18 labelled stations + free build area, `python.exe src/RimMandrake/MessyConduit/human_review.py --goto N`) is the right way to review: every owner finding became a numbered bar B1-B27 on MESSYCONDUIT_REVIEW_ROUND1_1 and was built and live-checked. Keep scope to ONE mod at a time (owner: doing too much at once caused divergence) and keep every Northstar test few and multi-coverage.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- The review map is LIVE in the running game (Industrial look, paused, camera on station 1): `D:\Luke\dev\RimMandrake\Transient\mc_human_review\keysheet.html` is the numbered station guide; ask him station by station (`--goto N`, `--style StarWars|StarWarsJawa|ExtensionCord|Cybertek`), do not fullscreen or focus the game (he said it is disruptive).
- Decisions recorded by card: style is chosen PER BUILD (architecture B, one building with style stored on it, 4-item build menu, largest run wins on merge, free 'Restyle this run' button, Modern cord colour per run incl. a 'random' mixture) in `design/RimMandrake/messyconduit_style_per_build_design.md`; hoses do not branch (crossings only); mod renamed to **Gimme Some Slack** (RimMandrake tier).
- Defaults I chose that he may veto: `--no-shots` emits I0_screenshots as SKIP not UNMEASURED (screenshots are never a pass bar); neither Scrapper nor Industrial draws power strips; merge tie goes to the older run; extended-concerns tier lives in each walk's `## extended` section (nothing built).
- He still owes: approve `design/RimMandrake/northstar_human_review.md` (turn it into a general Northstar rule), the 4 scope rows (`U_motion_look`, `U_style_missing_art`, M4 merge, M9 paused), the junk-reskin sheet (`Transient/junk_reskin_review_2026-10-04/sheet.html`), Swale art v2, Sanguophage (SANGUOPHAGE_KEPT_UNREACHABLE_1).
- Residual flaws I know: east-west spans cross in an X at each pole (crossarm art faces the camera; needs end-on pole art); the reel needs a `Reel_Deployed` sprite (1.4 x 1.4 cells, hose visibly entering the reel).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `ART_OVERRIDE_FAMILY_SCRIPT_1` — offline checks for 48 mods (46 pass), live run still owed; NEXT: run the art-override suite live on a tier that loads the 48 mods and record it
- `EVENT_TRACE_PROPS_LIBRARY_1` — step-0 spike mod src/RimMandrake/Traces and its first script built, never run live; NEXT: run the Traces spike live to settle whether a mark can spawn on a wall cell
- `FLAME_STATUES_MOD_BUILD_1` — mod built, DLL built not deployed, art done; NEXT: deploy FlameStatues and run its first script live
- `GREATBOLE_ATMOSPHERE_AND_CROSSOVERS_1` — engine check done (dryad system accepts a building host; two ritual classes need small C#); NEXT: make the two ritual-class C# changes then run the dryad-on-building check
- `LASSO_CHERRYPICKER_REMOVAL_1` — cuts are in the SHIP profile only; NEXT: at game-down apply the SHIP Cherry Picker profile and set Melee Animation LassoSpawnChance to 0
- `MESSYCONDUIT_REVIEW_ROUND1_1` — bars B1-B27 built, deployed and live-checked; matrix GREEN; owner review of the result pending; NEXT: walk the live review map with the owner station by station and file each new finding as B28 onward on this item
- `REPO_RENAME_SYMLINK_RETIRE_1` — 42 live files moved, csproj/Source lines remain; NEXT: finish the csproj and Source path lines on each mod's next rebuild then remove the symlink
- `STARWARS_JUNK_RESKIN_1` — 171 of 184 images generated, owner sheet prefilled and waiting; NEXT: have the owner curate Transient/junk_reskin_review_2026-10-04/sheet.html via serve_sheet.py run from the seat clone

- `GIMMESOMESLACK_RENAME_1` — filed with the owner's name ruling; NEXT: do the one mechanical rename sweep per the item note (packageId mandrake.rm.gimmesomeslack, namespaces, folder, tier, walk keys, settings migration) with selftests green, then re-record Northstar under the new key
- `MESSYCONDUIT_STYLE_PER_BUILD_BUILD_1` — design decided, nothing built; NEXT: build stage 1 (poles end to end, style stored on the building) per the design doc
- `MESSYCONDUIT_CABLE_PILE_LOOK_1` — piles and strips rebuilt in round 1, owner has not re-reviewed; NEXT: judge the three rules at station 4 with the owner and close or reopen
- `FLOWWORKS_HOSE_DEPLOY_DRAG_1` — owner's deploy/drag/drop/retract sketch recorded, no FlowWorks pump or job exists; NEXT: hold until the FlowWorks pump and spool job are scheduled
- `FRAMERATE_DURING_NORMAL_PLAY_1` — filed from the owner's low-frame-rate observation; NEXT: have the owner play normally with no bridge session and report the frame rate

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- A powershell kill matched on CommandLine silently missed UNC-launched python.exe, so 'stopped' runs kept driving the game and poisoned results; count processes after every kill (filed: lessons)
- `jawa/mod_settings_field` scanned every loaded type on every call (0.74 s; 88% of matrix time), now cached in the companion (filed: lessons)
- I hand-edited a result JSON to test a status once and recorded it; rerun from a fixed harness instead, never edit results (filed: lessons)
- `launch_and_wait.sh` gives up at ~5 min but the full 638-mod cold load is ~13 min: wait for the Bridge token line (filed: lessons)
- A zsh `$L "args"` command variable did not word-split again and ran nothing; write commands out directly (see: CLAUDE.md zsh word-split trap)
- Do not maximize or focus the RimWorld window for screenshots (see: memory dont-fullscreen-or-focus-the-game)

## Closed since the last handoff (21)

- `ANIMAL_TOLERANCES_DONOR_NOMATCH_1` — 65180d7e9
- `VFET_RETAG_ROWS_NOT_HELD_1` — b5b140267
- `DIVINGINTERACTION_COVERAGE_GAPS_1` — d278a8f8b
- `LONGSHADE_COVERAGE_GAPS_1` — d278a8f8b
- `RIMPROPERTY_COVERAGE_GAPS_1` — d278a8f8b
- `ENVIRONMENTALHAZARDS_COVERAGE_GAPS_1` — d278a8f8b
- `STRUCTUREINJECTIONSRUT_COVERAGE_GAPS_1` — d278a8f8b
- `CREATUREBEHAVIORS_COVERAGE_GAPS_1` — d278a8f8b
- `VANILLA_XENOTYPE_DEFCUT_1` — ecd9944e3
- `NORTHSTAR_BRIDGE_UTILIZATION_1` — c94d93527
- `SUMP_CAPSTAN_DRAWJOINT_RESEARCH_1` — 8abdffa57
- `ADHOC_BRIDGE_CALL_LOG_1` — be5c77b6a
- `GRAFFITI_WALL_LINKED_CROP_1` — d457c0ba6
- `SUMP_CAPSTAN_LOCAL_RECIPE_1` — 6ad918e08
- `FORGE_MISSING_ART_1` — b4966c0df
- `WARCASKET_CASK_ART_1` — 01b3d50d3
- `CONTAGION_GROWN_LIMBS_ART_1` — d570e5e7e
- `FALL_LINE_WRECKAGE_CREATURES_PORT_1` — df2efc796
- `SPECULATIVE_ART_COMMISSION_1` — fa6bcf684
- `CUT_BY_NOBODY_SOURCE_1` — 3a88ebb6b
- `AQUALISH_NAME_WORDLISTS_1` — b80d5967b

## Filed and still open (19) — the next seat's queue

- `SANGUOPHAGE_KEPT_UNREACHABLE_1` — Owner card: Sanguophage cannot be deleted (XenotypeDefOf binding) - keep the def but make it unreachable (suppress Sanguophages faction, Sanguophage s
- `GRAFFITI_LINKED_MARK_FIX_1` — Graffiti marks draw a 3.5% atlas crop (Scratches invisible on any single wall): either author real 4x4 link atlases per mark, or drop linkType and dra
- `TILE_TEMP_CACHE_RESET_TOOL_1` — JawaBench: world_tile_set (or a new jawa/tile_cache_reset) nulls Tile.cachedMinTemp/cachedMaxTemp/hillinessLabelCached by reflection, so a retiled tem
- `BURROW_TIMER_SAVE_LOAD_1` — RM_JobDriver_Burrow: the safety-cap start tick is a closure local, so after a save/load mid-burrow the cap never fires (startTick stays -1); persist i
- `LUMINOUS_PIGMENT_STARTUP_NRE_1` — LuminousPigmentMod.ApplyClusterBlockToMaps NREs at startup (Player.log post-long-event): Find.Maps with Current.Game null; guard 'if (Current.Game == 
- `MYCOID_ART_OVERRIDE_DEAD_1` — MycoidColossusArtOverride is dead art: TheRot/Patches/RotSpecies_NamesAndSizes.xml repoints AA_MycoidColossus to RotSpecies/MycoidColossus/MycoidColos
- `MANTISTANIS_DONOR_ABSENT_1` — MantistanisArtOverride: GR_Mantistanis (VGeneticsE) is absent from the 2026-10-04 def dump, so its art binds nothing; check whether VGeneticsE is acti
- `WEEPINGSTONES_STOCK_JOB_LOOP_1` — WeepingStones: bland colonists restart RM_StockPoolPen up to 10x per tick (JobGiver_Work) and the stock/net/feed/harvest/cull proofs read job-never-ra
- `ARMOURY_JUMPPACK_INVALID_IL_1` — Armoury JumppackForMeleeAI transpiler on JobGiver_AIFightEnemy.TryGiveJob throws InvalidProgramException at load; the patch never applies (belt Armour
- `JAWABENCH_DLL_STALE_REBUILD_1` — Rebuild/deploy the JawaBench companion DLL: deployed build is 2026-10-02 05:37 and lacks 8 tools added since (jawa/flowworks_pulse, jawa/static_call, 
- `SELFTEST_RUNNER_SILENT_OOM_1` — run_selftests.py: three patch selftests (StarWars/Utinni/Mandrake) pass alone but fail or get OOM-killed (rc=137) in the parallel run, and the runner 
- `FRAMERATE_DURING_NORMAL_PLAY_1` — Confirm the game runs smooth in normal play: owner saw heavy low-frame-rate stretches during bridge test runs (2026-10-04), assumed bridge writing/scr
- `MESSYCONDUIT_STYLED_POLES_1` — Power poles follow the cable style: Cybertek gets a sleek modern pole, Star Wars (thick black cables) gets a grungy industrial steel pole; 4 cells tal
- `MESSYCONDUIT_CABLE_PILE_LOOK_1` — Cable and hose pile look: power strips always have cables plugged in, cables read as one flowing run except at nodes/strips/joiners (like the T juncti
- `MESSYCONDUIT_REVIEW_ROUND1_1` — MessyConduit human review round 1: 10 findings from the owner at the review map (Star Wars style art, stations 4,5,6,7,9,10,12, plug-in-here marker, p
- `FLOWWORKS_HOSE_DEPLOY_DRAG_1` — Hose deploy interaction: 'deploy to this location' from the pump side, a colonist drags the free end out with the hose shown unrolling live, an interr
- `MESSYCONDUIT_STYLE_PER_BUILD_DESIGN_1` — Design: replace the global art-style setting with a per-build art-style choice (Scrapper / Industrial / Modern / Futuristic) for conduit, poles, hose 
- `MESSYCONDUIT_STYLE_PER_BUILD_BUILD_1` — Build per-build art style choice (stage 1 poles end to end, 2 conduit runs, 3 reels and hoses, 4 art fill) per design/RimMandrake/messyconduit_style_p
- `GIMMESOMESLACK_RENAME_1` — Rename MessyConduit to 'Gimme Some Slack' (RimMandrake-level mod): packageId mandrake.rm.gimmesomeslack, namespaces RimMandrake.GimmeSomeSlack, folder

## Commits

```
f3bf4d8fc MessyConduit Northstar: round-2 runs at 8a8a6a00ba47 - matrix GREEN (109/109 scenes; catalog regenerated after B17), core REFUSED on 4 scope rows, aerial GREEN
797aba07e Trio gap-fill: no in-scope gaps (desert/deep_desert RUT-only; blue_desert RM_ rows had art or donor art)
3857b33aa biome_census.py: rescope to the Baroque Biomes RM_ defs (from Biomes.compose.json), per-row layer
7b5eceb89 ledger: BIOME_FLORAFAUNA_ART_REVIEW_1 scope is Baroque Biomes only
5f5682c4e ledger: MESSYCONDUIT_REVIEW_ROUND1_1 round-2 note
daa4a7af6 MessyConduit validation: strip rows read the Modern look (owner B1), Modern span expected black (owner B12); human_review --shot (game render, no window focus)
11c42922e biome_census.py: per-biome flora/fauna art + canon census (BIOME_FLORAFAUNA_ART_REVIEW_1)
e7f9f25a6 Desert gap-fill: 7 droid art jobs queued at priority 10; 10 of 17 no-graphic rows already had art
0f59d02b9 MessyConduit round 2 T5-T9: one wire per measured insulator tip, cast span shadow, hookups in the look's cable, deployed-reel switch (stand-in), one Mod Settings entry with tabs, roofless review shed
24950e8b1 MessyConduit style-per-build design: record owner decisions (B, largest run wins, free restyle button, per-run cord colour incl. random mixture)
c8ae1923f MessyConduit: design pass for choosing art style at build time (per-run style, 3 architectures, owner questions)
0a14ee45d ledger: BIOME_FLORAFAUNA_ART_REVIEW_1 rulings note
8ac23ee0f MessyConduit round 2 live fixes: hose fittings drawn bare under the wrap, aged wrap tint, open-end wrap to the cut; review map settles power before freezing (T4), --sub close framing, spare N bracket outside
e7d0b7946 MessyConduit: modern wall bracket art wired (v2; its north/south renders were drawn for the opposite wall, swapped)
6ebc84361 MessyConduit round 2: one-piece fallen wire to the break, span fan to insulators, hose binding wraps, per-facing bracket art, st.9 lamp inside shed
f37d7f6f5 ledger: owner event for BIOME_FLORAFAUNA_ART_REVIEW_1
245ccc970 ledger: file BIOME_FLORAFAUNA_ART_REVIEW_1 (BENCH priority wave)
e5576276b MessyConduit: pole_shots.py (per-look pole station screenshots), pole wiring log
15535d8bb BENCH handoff 2026-10-04 + three lessons
67a3cfee0 desert sitting 1: owner decisions snapshot (101 of 102 rows decided; not yet applied)
... 117 more: git log --oneline 383f15d0f..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-10-04T22:03:13Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
A  Transient/belt_rerun_FeverWood_20261004c.txt   FOUNDRY (this window and its subagents)
A  Transient/belt_rerun_FeverWood_20261004d.txt   FOUNDRY (this window and its subagents)
A  Transient/belt_rerun_KeelWeep_20261004e.txt   FOUNDRY (this window and its subagents)
A  Transient/belt_rerun_MovingDunes_20261004g.txt   FOUNDRY (this window and its subagents)
A  Transient/belt_rerun_WS_20261004f.txt   FOUNDRY (this window and its subagents)
A  Transient/belt_rerun_batch_20261004h.txt   FOUNDRY (this window and its subagents)
 M Transient/mc_human_review/KEYSHEET.md   FOUNDRY (this window and its subagents)
 M Transient/mc_human_review/keysheet.html   FOUNDRY (this window and its subagents)
 M Transient/mc_human_review_build_log_20261004.md   FOUNDRY (this window and its subagents)
 M Transient/mc_matrix_live_20261002/image_sanity.json   FOUNDRY (this window and its subagents)
 M Transient/mc_matrix_live_20261002/review.html   FOUNDRY (this window and its subagents)
 M Transient/mc_matrix_live_20261002/sheet_aerial_01.png   FOUNDRY (this window and its subagents)
 M Transient/mc_matrix_live_20261002/sheet_aerial_02.png   FOUNDRY (this window and its subagents)
 M Transient/mc_matrix_live_20261002/sheet_controls_01.png   FOUNDRY (this window and its subagents)
 M Transient/mc_matrix_live_20261002/sheet_density_01.png   FOUNDRY (this window and its subagents)
 M Transient/mc_matrix_live_20261002/sheet_floor_01.png   FOUNDRY (this window and its subagents)
 M Transient/mc_matrix_live_20261002/sheet_floor_02.png   FOUNDRY (this window and its subagents)
 M Transient/mc_matrix_live_20261002/sheet_floor_03.png   FOUNDRY (this window and its subagents)
 M Transient/mc_matrix_live_20261002/sheet_floor_04.png   FOUNDRY (this window and its subagents)
 M Transient/messy_conduit_live_20261002/aerial_01_lines_up.png   FOUNDRY (this window and its subagents)
 M Transient/messy_conduit_live_20261002/aerial_02_dead_pole_fallen_cords.png   FOUNDRY (this window and its subagents)
 M Transient/messy_conduit_live_20261002/aerial_03_explosion_cut_halves.png   FOUNDRY (this window and its subagents)
 M Transient/messy_conduit_live_20261002/aerial_04_power_tap_clamp.png   FOUNDRY (this window and its subagents)
 M Transient/messy_conduit_live_20261002/aerial_05_after_save_load.png   FOUNDRY (this window and its subagents)
 M Transient/messy_conduit_live_20261002/hose_01_flat.png   FOUNDRY (this window and its subagents)
 M Transient/messy_conduit_live_20261002/hose_02_plump.png   FOUNDRY (this window and its subagents)
 M Transient/messy_conduit_live_20261002/hose_03_after_save_load.png   FOUNDRY (this window and its subagents)
 M Transient/messy_conduit_live_20261002/p1b_01_wide.png   FOUNDRY (this window and its subagents)
 M Transient/messy_conduit_live_20261002/p1b_02_tangle_lit_and_downed_wire.png   FOUNDRY (this window and its subagents)
 M Transient/messy_conduit_live_20261002/p1b_04_far_zoom_lod.png   FOUNDRY (this window and its subagents)
 M Transient/messy_conduit_live_20261002/p1b_05_downed_wire_close.png   FOUNDRY (this window and its subagents)
 M Transient/messy_conduit_live_20261002/p1b_06_tangle_dark.png   FOUNDRY (this window and its subagents)
 M Transient/modcheck/live_queue/situational_rerun/Abyss_summary.json   FOUNDRY (this window and its subagents)
 M Transient/modcheck/live_queue/situational_rerun/Aftermath_summary.json   FOUNDRY (this window and its subagents)
 M Transient/modcheck/live_queue/situational_rerun/Armoury_summary.json   FOUNDRY (this window and its subagents)
 M Transient/modcheck/live_queue/situational_rerun/Bacta_summary.json   FOUNDRY (this window and its subagents)
 M Transient/modcheck/live_queue/situational_rerun/BlueDesert_summary.json   FOUNDRY (this window and its subagents)
 M Transient/modcheck/live_queue/situational_rerun/BrainWorms_summary.json   FOUNDRY (this window and its subagents)
 M Transient/modcheck/live_queue/situational_rerun/Cauldron_summary.json   FOUNDRY (this window and its subagents)
 M Transient/modcheck/live_queue/situational_rerun/Contagion_summary.json   FOUNDRY (this window and its subagents)
 M Transient/modcheck/live_queue/situational_rerun/FeverWood_summary.json   FOUNDRY (this window and its subagents)
 M Transient/modcheck/live_queue/situational_rerun/GizkaStowaway_summary.json   FOUNDRY (this window and its subagents)
 M Transient/modcheck/live_queue/situational_rerun/LeaningScrub_summary.json   FOUNDRY (this window and its subagents)
 M Transient/modcheck/live_queue/situational_rerun/MovingDunes_summary.json   FOUNDRY (this window and its subagents)
 M Transient/modcheck/live_queue/situational_rerun/NightsideIce_summary.json   FOUNDRY (this window and its subagents)
 M Transient/modcheck/live_queue/situational_rerun/TerminalBiomes_summary.json   FOUNDRY (this window and its subagents)
 M Transient/modcheck/live_queue/situational_rerun/TheForge_summary.json   FOUNDRY (this window and its subagents)
 M Transient/modcheck/live_queue/situational_rerun/TheRot_summary.json   FOUNDRY (this window and its subagents)
 M Transient/modcheck/live_queue/situational_rerun/TheSump_summary.json   FOUNDRY (this window and its subagents)
 M Transient/modcheck/live_queue/situational_rerun/UnfinishedLine_summary.json   FOUNDRY (this window and its subagents)
 M Transient/modcheck/live_queue/situational_rerun/WeepingStones_summary.json   FOUNDRY (this window and its subagents)
 M Transient/modcheck/live_queue_results.jsonl   FOUNDRY (this window and its subagents)
 M infrastructure/state/ledger/events/FOUNDRY.jsonl   FOUNDRY (this window and its subagents)
 M infrastructure/state/ledger/events/OWNER.jsonl   FOUNDRY (this window and its subagents)
 M src/RimMandrake/MovingDunes/Assemblies/RimMandrakeMovingDunes.dll   FOUNDRY (this window and its subagents)
 M src/RimMandrake/MovingDunes/Assemblies/RimMandrakeMovingDunes.dll.srchash   FOUNDRY (this window and its subagents)
 M src/RimMandrake/Utils/modcheck/required_checks.json   FOUNDRY (this window and its subagents)
?? deployed/config/ModsConfig.before-tier-builds_biomes.xml   FOUNDRY (this window and its subagents)
?? deployed/config/ModsConfig.before-tier-flowworks.kept-20261002.xml   FOUNDRY (this window and its subagents)
?? deployed/config/ModsConfig.before-tier-flowworks.xml   FOUNDRY (this window and its subagents)
?? deployed/config/ModsConfig.before-tier-messyconduit.xml   FOUNDRY (this window and its subagents)
?? deployed/config/ModsConfig.pre-ns-flowworks.20261002T070221.xml   FOUNDRY (this window and its subagents)
?? deployed/config/ns_flowworks_backup.20261002T070221.json   FOUNDRY (this window and its subagents)
?? src/RimMandrake/MessyConduit/northstar/matrix_live_20261004T104900.json   FOUNDRY (this window and its subagents)
?? src/RimMandrake/MessyConduit/northstar/matrix_live_20261004T111300.json   FOUNDRY (this window and its subagents)
?? src/RimMandrake/MessyConduit/northstar/validation_aerial_live_20261004T084830.json   FOUNDRY (this window and its subagents)
?? src/RimMandrake/MessyConduit/northstar/validation_aerial_live_20261004T085649.json   FOUNDRY (this window and its subagents)
?? src/RimMandrake/MessyConduit/northstar/validation_aerial_live_20261004T090138.json   FOUNDRY (this window and its subagents)
?? src/RimMandrake/MessyConduit/northstar/validation_aerial_live_20261004T105819.json   FOUNDRY (this window and its subagents)
?? src/RimMandrake/MessyConduit/northstar/validation_aerial_live_20261004T110845.json   FOUNDRY (this window and its subagents)
?? src/RimMandrake/MessyConduit/northstar/validation_aerial_save-load_20261004T084920.json   FOUNDRY (this window and its subagents)
?? src/RimMandrake/MessyConduit/northstar/validation_aerial_save-load_20261004T085739.json   FOUNDRY (this window and its subagents)
?? src/RimMandrake/MessyConduit/northstar/validation_aerial_save-load_20261004T090236.json   FOUNDRY (this window and its subagents)
?? src/RimMandrake/MessyConduit/northstar/validation_aerial_save-load_20261004T105830.json   FOUNDRY (this window and its subagents)
?? src/RimMandrake/MessyConduit/northstar/validation_aerial_save-load_20261004T110854.json   FOUNDRY (this window and its subagents)
?? src/RimMandrake/MessyConduit/northstar/validation_hose_live_20261004T085236.json   FOUNDRY (this window and its subagents)
?? src/RimMandrake/MessyConduit/northstar/validation_hose_live_20261004T105934.json   FOUNDRY (this window and its subagents)
?? src/RimMandrake/MessyConduit/northstar/validation_hose_live_20261004T110908.json   FOUNDRY (this window and its subagents)
?? src/RimMandrake/MessyConduit/northstar/validation_hose_save-load_20261004T085316.json   FOUNDRY (this window and its subagents)
?? src/RimMandrake/MessyConduit/northstar/validation_hose_save-load_20261004T105944.json   FOUNDRY (this window and its subagents)
?? src/RimMandrake/MessyConduit/northstar/validation_hose_save-load_20261004T110918.json   FOUNDRY (this window and its subagents)
?? src/RimMandrake/MessyConduit/northstar/validation_result_20261004T084401.json   FOUNDRY (this window and its subagents)
?? src/RimMandrake/MessyConduit/northstar/validation_result_20261004T105710.json   FOUNDRY (this window and its subagents)
?? src/RimMandrake/MessyConduit/northstar/validation_result_20261004T110816.json   FOUNDRY (this window and its subagents)
?? src/RimMandrake/MessyConduit/northstar/validation_result_20261004T144404.json   FOUNDRY (this window and its subagents)
?? src/RimMandrake/MessyConduit/northstar/validation_save-load_20261004T084454.json   FOUNDRY (this window and its subagents)
?? src/RimMandrake/MessyConduit/northstar/validation_save-load_20261004T105719.json   FOUNDRY (this window and its subagents)
?? src/RimMandrake/MessyConduit/northstar/validation_save-load_20261004T110824.json   FOUNDRY (this window and its subagents)
```

