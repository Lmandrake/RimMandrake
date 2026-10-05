# FOUNDRY_HANDOFF_202610051553 — READ FIRST on wake

Follows `FOUNDRY_HANDOFF_202610040742`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next session hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
GimmeSomeSlack is at DRAFT-CHECKLIST, the highest status reachable without the owner: live proof 143 PASS + 1 SKIP (P1 reel-couples-to-tank, FlowWorks absent) recorded at mod hash c63d7aab544e. Green needs HIS typed validation of the seeded 17-bar checklist plus one view of the sheet; never self-validate. Any edit to a file in the mod folder (everything except validation.py, human_review.py, northstar/) stales the recorded run, so finish edits first.

## What the owner should see

<!-- Findings that need the owner's eye or decision: a number nobody ruled on, a change they can veto, anything shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- The seeded `## north star` in `design/validation_walks/RimMandrake/GimmeSomeSlack.md` is MY guess (17 must-show, 2 cannot-show); the brass joiner, reel nozzle and deflated-unless-pump bars are relayed paraphrase, not his verbatim words; he should replace them before validating.
- Review sheet: `D:\Luke\dev\RimMandrake\src\RimMandrake\GimmeSomeSlack\review\keysheet.html` (mirror path after the next sync; clone path `/home/mandrake/rm/foundry/src/RimMandrake/GimmeSomeSlack/review/keysheet.html`) plus savegame `RM_gss_review_20261005.rws` in the game's Saves folder.
- Shipped this window and needs his eyes in game: joiner halves now mesh shoulder-to-shoulder; the 2x2 reel's hose starts at the brass outlet nozzle with a coupling on it; reels have a free 'Choose style' button. None judged by a human yet.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_OR_TOPIC — state; NEXT: <one imperative action>`. A pointer without a NEXT: measured ~0% pickup; with one, near-100%. -->
- - `GIMMESOMESLACK_NORTHSTAR_VALIDATE_1` — checklist is DRAFT; NEXT: ask the owner to read the 17 bars, correct them, and validate with his typed words via `modcheck/cli.py validate GimmeSomeSlack --owner-said "<his words>"`, then `modcheck/cli.py owner-review`
- `NORTHSTAR_PROCESS_RETRO_1` — filed and blocked until Green; NEXT: after GimmeSomeSlack is GREEN, claim it and run the process retro (helpers listed in its criteria)
- `PROOF_ALL_MAZE_P1_TANK_1` — P1 is now a declared SKIP; NEXT: add mandrake.rm.flowworks to the proof tier or leave the skip until FlowWorks has tanks
- Pump bar — no proof_all row emits the UNBUILT pump row; NEXT: add it AFTER recording, then re-run proof_all and record again
- `STATION25_ROOFED_LINK_EXPECTATION_1`, `HOSE_WATER_END_LIVE_1`, `HOSE_WIND_POLISH_1`, `LASSO_CHERRYPICKER_REMOVAL_1` — unchanged from the 2026-10-05 08:45 handoff; NEXT: see that handoff
- Reel nozzle and joiner art — code done, not seen live by him; NEXT: build the review map (`python.exe src/RimMandrake/GimmeSomeSlack/human_review.py --build --fresh-map` from the repo root) and check stations with the reel and joiners

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives — append it to the lessons file the moment it is learned, then cite `(filed: LESSONS)` or `(see: <doc>)`. Never re-explain a trap that is already recorded. -->
- A proof run goes stale on any mod-folder edit and SL4 flakes when a fresh map yields under 2 free colonists (filed: lessons 20261005T155316Z-FOUNDRY-proof-run-goes-stale-when-any)
- `human_review.py` and `proof_all.py` must run from the repo root with `--live` (relative log path; bare run prints usage) (see: this handoff)
- `modcheck` counts a RECORD row as RED; only PASS/SKIP/UNCOVERED/UNBUILT are OK (see: Utils/modcheck/record.py OK_ROWS)
- The blind-scan hook refuses even a literal wait on Player.log unless MEASURE_ALLOW_SCAN=1 (I set it for the 'Bridge token' wait) (see: NORTHSTAR_PROCESS_RETRO_1)


## Commits

```
9f431c305 GimmeSomeSlack: modcheck recorded DRAFT-CHECKLIST (proof 143 PASS + 1 SKIP at hash c63d7aab544e); the seeded north star awaits the owner
e89d7621a Sheet join: route render matching through subject.py; badge failed_canon renders
ae82f33a3 Gapfill blind spots: 12 rows (16 jobs) queued; sheet join bug filed
180ab5515 Art daemon failure triage 2026-10-05: requeue 61 recoverable failed jobs; fix Vrekka facing prompt; file ARTPIPE_REQUEUE_AUTOMATION_1
b9e310644 Tonight: four in-progress biome sheets rebuilt (Abyss new names + crags sets, latest renders), per-biome TOC
f97cfe726 GimmeSomeSlack: provisional DRAFT north star (17 must-show, 2 cannot-show; agent guesses from the owner's words) + shows= wiring in validation.py
15caf5fd7 Gapfill-all: 94 donor-only/missing-facing rows queued (196 jobs)
17e8fddf3 NORTHSTAR_PROCESS_RETRO_1 item prose (spec/verify/criteria)
610729177 File NORTHSTAR_PROCESS_RETRO_1: process retro, gated on GimmeSomeSlack Green
d08c8223d GimmeSomeSlack: review sheet + key filed in the mod's review/ folder with save_review_map.py; map saved as RM_gss_review_20261005; review/ and northstar/ held from deploy
a5e813376 Khorrak steel diet: owner chose to move it to RM_Khorrak (question card)
b30349fc3 Queue new art job for ancient shielded turret (its texture was the purged Vhaulk render)
c4dc6fcd1 GimmeSomeSlack self-test: two assertions moved to the nozzle start (hose leaves the west outlet; walked-hose apex 20.6)
92aa4b660 Abyss dark family: plain plant names, ombrathia + saevitha, lineage hints, 30 black many-eyed v2 jobs
f023e5302 GimmeSomeSlack review map: sweep all non-colonist pawns (mechanoids) at build end and on every goto
7cee1690c Lesson corrected: the sibilant name style is one Abyss family's, not a general preference
8d31f10b8 GimmeSomeSlack: 2x2 reel's hose starts at its brass outlet nozzle with a coupling on it (reverses round 5 hide-under-drum); self-test updated
66880939b Ledger: Abyss crags_* art mapping for the next sitting
7c2713d54 Abyss names re-authored in the owner's new sibilant style; skarnix label now ishvarith
dba4db2ae RUT_Abyss: cut dusk rat, frostling, night ave and sand prowler (vosska), matching RM_Abyss
... 393 more: git log --oneline edeabab6d..HEAD
```

## Tree state at wrap

- upstream: origin/main, pushed

Uncommitted (replace each marker below with whose it is — yours, another agent's, generated):

```
A  Transient/belt_rerun_FeverWood_20261004c.txt   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
A  Transient/belt_rerun_FeverWood_20261004d.txt   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
A  Transient/belt_rerun_KeelWeep_20261004e.txt   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
A  Transient/belt_rerun_MovingDunes_20261004g.txt   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
A  Transient/belt_rerun_WS_20261004f.txt   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
A  Transient/belt_rerun_batch_20261004h.txt   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
 M Transient/mc_hose_carry_s5_report.md   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
 M Transient/mc_human_review_build_log_20261004.md   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
 M Transient/mc_matrix_live_20261002/image_sanity.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
 M Transient/mc_matrix_live_20261002/review.html   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
 M Transient/mc_matrix_live_20261002/sheet_aerial_01.png   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
 M Transient/mc_matrix_live_20261002/sheet_aerial_02.png   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
 M Transient/mc_matrix_live_20261002/sheet_controls_01.png   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
 M Transient/mc_matrix_live_20261002/sheet_density_01.png   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
 M Transient/mc_matrix_live_20261002/sheet_floor_01.png   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
 M Transient/mc_matrix_live_20261002/sheet_floor_02.png   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
 M Transient/mc_matrix_live_20261002/sheet_floor_03.png   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
 M Transient/mc_matrix_live_20261002/sheet_floor_04.png   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
 M Transient/messy_conduit_live_20261002/aerial_01_lines_up.png   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
 M Transient/messy_conduit_live_20261002/aerial_02_dead_pole_fallen_cords.png   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
 M Transient/messy_conduit_live_20261002/aerial_03_explosion_cut_halves.png   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
 M Transient/messy_conduit_live_20261002/aerial_04_power_tap_clamp.png   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
 M Transient/messy_conduit_live_20261002/aerial_05_after_save_load.png   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
 M Transient/messy_conduit_live_20261002/hose_01_flat.png   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
 M Transient/messy_conduit_live_20261002/hose_02_plump.png   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
 M Transient/messy_conduit_live_20261002/hose_03_after_save_load.png   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
 M Transient/messy_conduit_live_20261002/p1b_01_wide.png   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
 M Transient/messy_conduit_live_20261002/p1b_02_tangle_lit_and_downed_wire.png   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
 M Transient/messy_conduit_live_20261002/p1b_04_far_zoom_lod.png   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
 M Transient/messy_conduit_live_20261002/p1b_05_downed_wire_close.png   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
 M Transient/messy_conduit_live_20261002/p1b_06_tangle_dark.png   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
 M Transient/modcheck/live_queue/situational_rerun/Abyss_summary.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
 M Transient/modcheck/live_queue/situational_rerun/Aftermath_summary.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
 M Transient/modcheck/live_queue/situational_rerun/Armoury_summary.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
 M Transient/modcheck/live_queue/situational_rerun/Bacta_summary.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
 M Transient/modcheck/live_queue/situational_rerun/BlueDesert_summary.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
 M Transient/modcheck/live_queue/situational_rerun/BrainWorms_summary.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
 M Transient/modcheck/live_queue/situational_rerun/Cauldron_summary.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
 M Transient/modcheck/live_queue/situational_rerun/Contagion_summary.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
 M Transient/modcheck/live_queue/situational_rerun/FeverWood_summary.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
 M Transient/modcheck/live_queue/situational_rerun/GizkaStowaway_summary.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
 M Transient/modcheck/live_queue/situational_rerun/LeaningScrub_summary.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
 M Transient/modcheck/live_queue/situational_rerun/MovingDunes_summary.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
 M Transient/modcheck/live_queue/situational_rerun/NightsideIce_summary.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
 M Transient/modcheck/live_queue/situational_rerun/TerminalBiomes_summary.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
 M Transient/modcheck/live_queue/situational_rerun/TheForge_summary.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
 M Transient/modcheck/live_queue/situational_rerun/TheRot_summary.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
 M Transient/modcheck/live_queue/situational_rerun/TheSump_summary.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
 M Transient/modcheck/live_queue/situational_rerun/UnfinishedLine_summary.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
 M Transient/modcheck/live_queue/situational_rerun/WeepingStones_summary.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
 M Transient/modcheck/live_queue_results.jsonl   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
 M infrastructure/state/ledger/events/FOUNDRY.jsonl   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
 M src/RimMandrake/MovingDunes/Assemblies/RimMandrakeMovingDunes.dll   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
 M src/RimMandrake/MovingDunes/Assemblies/RimMandrakeMovingDunes.dll.srchash   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/ModsConfig_before_d.xml   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/Player_load13_20261004.log   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/belt_bridge_log_20261004d.md   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/belt_deep_proto.py   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/belt_deploy_d_biomes.txt   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/belt_deploy_d_plain.txt   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/belt_deploy_done   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/belt_deploy_plan_d.txt   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/belt_deploy_prune.txt   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/belt_deploy_prune_c.txt   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/belt_deploy_r5_biomes.txt   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/belt_deploy_r5_plain.txt   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/belt_deploy_r5_plain2.txt   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/belt_deploy_r5_plain3.txt   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/belt_deploy_r6_biomes.txt   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/belt_deploy_r6_done   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/belt_deploy_r6_plain.txt   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/belt_first_errors_d.txt   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/belt_gitprobe.py   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/belt_harvest10_20261003.txt   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/belt_harvest11_20261003.txt   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/belt_harvest3_20261003.txt   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/belt_harvest5_20261003.txt   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/belt_harvest6_20261003.txt   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/belt_harvest7_20261003.txt   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/belt_harvest8_20261003.txt   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/belt_harvest9_20261003.txt   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/belt_probe.py   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/belt_probe2.py   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/belt_probe_pawns.py   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/belt_probe_rr.py   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/belt_probe_ruins.py   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/belt_probe_size.py   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/belt_rerun19a_20261003.txt   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/belt_rerun19b_20261003.txt   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/belt_rerun20a_20261003.txt   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/belt_rerun20b_20261003.txt   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/belt_rerun20c_20261003.txt   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/belt_rerun_TheSump_20261004i.txt   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/belt_rerun_TheSump_20261004j.txt   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/belt_rerun_b1_20261004k.txt   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/belt_rerun_b2_20261004l.txt   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/belt_rerun_b3_20261004m.txt   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/belt_setbg.py   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/belt_sum.py   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/list_tools.py   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/mc_art_poles_20261004/   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/mc_densify_human_review_notes.md   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/mc_full_plan_run2_20261004.txt   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/mc_full_plan_run3_20261004.txt   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/mc_full_plan_run_20261004.txt   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/mc_live_run2_20261004.txt   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/mc_matrix_fast_20261004.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/mc_matrix_fast_run_20261004.txt   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/mc_matrix_live_20261002/shots/   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/mc_matrix_live_20261002/shots_pass1/   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/mc_matrix_noshots2_run_20261004.txt   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/mc_matrix_noshots3_20261004.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/mc_matrix_noshots3_run_20261004.txt   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/mc_matrix_noshots_run_20261004.txt   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/mc_matrix_rec2_20261004.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/mc_matrix_rec3_20261004.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/mc_matrix_rec4_20261004.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/mc_matrix_rec_20261004.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/mc_matrix_run_20261004.txt   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/mc_owner_shots_r4/   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/mc_owner_shots_r5/   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/mc_owner_shots_r6/   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/mc_owner_shots_r7/   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/mc_probe_aerial_after_load.py   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/mc_read_settings.py   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/mc_relaunch2_20261004.txt   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/mc_relaunch_20261004.txt   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/mc_scenes_20261004.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/mc_time_calls.py   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/mc_time_calls2.py   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/messy_conduit_live_20261002/maze_01_open.png   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/messy_conduit_live_20261002/maze_02_gap_walled.png   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/messy_conduit_live_20261002/maze_04_unreachable.png   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/messy_conduit_live_20261002/ports_01_reel_tank.png   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/modcheck/fixtures.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/modcheck/live_queue/J1_situational_rerun/   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/modcheck/live_queue/J2_abort_proof/   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/modcheck/live_queue/situational_rerun/FlameStatues_summary.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/modcheck/live_queue/situational_rerun/ResearchRetag_summary.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/modcheck/surprises/20261004T023842/   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/modcheck/surprises/20261004T030802/   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/modcheck/surprises/20261004T032016/   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/modcheck/surprises/20261004T035902/   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/modcheck/surprises/20261004T050655/   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/modcheck/surprises/20261004T053947/   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/modcheck/surprises/20261004T055717/   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/modcheck/surprises/20261004T060347/   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/modcheck/surprises/20261004T062227/   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/modcheck/surprises/20261004T063127/   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/modcheck/surprises/20261004T064738/   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/modcheck/surprises/20261004T064928/   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/modcheck/surprises/20261004T071347/   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/modcheck/surprises/20261004T072546/   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/modcheck/surprises/20261004T074823/   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/northstar/ArtOverrideFamily_static_20261004T101503Z.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/northstar/ExplosiveGrowth_20261003T101654Z.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/northstar/FloodedCanyon_20261003T101943Z.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? Transient/northstar/Greentide_20261003T102251Z.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? conversations/   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? deployed/config/ModsConfig.before-tier-builds_biomes.xml   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? deployed/config/ModsConfig.before-tier-flowworks.kept-20261002.xml   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? deployed/config/ModsConfig.before-tier-flowworks.xml   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? deployed/config/ModsConfig.before-tier-gimmesomeslack.xml   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? deployed/config/ModsConfig.before-tier-messyconduit.xml   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? deployed/config/ModsConfig.pre-ns-flowworks.20261002T070221.xml   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? deployed/config/ns_flowworks_backup.20261002T070221.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? infrastructure/state/lessons/20261005T155316Z-FOUNDRY-proof-run-goes-stale-when-any.md   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? src/RimMandrake/GimmeSomeSlack/northstar/matrix_live_20261004T104900.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? src/RimMandrake/GimmeSomeSlack/northstar/matrix_live_20261004T111300.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? src/RimMandrake/GimmeSomeSlack/northstar/proof_all_20261005T010730.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? src/RimMandrake/GimmeSomeSlack/northstar/proof_all_20261005T012345.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? src/RimMandrake/GimmeSomeSlack/northstar/proof_all_20261005T012712.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? src/RimMandrake/GimmeSomeSlack/northstar/proof_all_20261005T082415.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? src/RimMandrake/GimmeSomeSlack/northstar/proof_all_20261005T084118.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_live_20261004T084830.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_live_20261004T085649.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_live_20261004T090138.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_live_20261004T105819.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_live_20261004T110845.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_save-load_20261004T084920.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_save-load_20261004T085739.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_save-load_20261004T090236.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_save-load_20261004T105830.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_save-load_20261004T110854.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_hose_carry_20261004T233651.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_hose_carry_20261005T001134.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_hose_live_20261004T085236.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_hose_live_20261004T105934.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_hose_live_20261004T110908.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_hose_maze_20261004T234830.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_hose_maze_20261004T235220.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_hose_maze_20261004T235328.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_hose_relay_20261004T225835.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_hose_save-load_20261004T085316.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_hose_save-load_20261004T105944.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_hose_save-load_20261004T110918.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_result_20261004T084401.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_result_20261004T105710.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_result_20261004T110816.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_result_20261004T144404.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_save-load_20261004T084454.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_save-load_20261004T105719.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_save-load_20261004T110824.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_style_hose_live_20261004T212855.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_style_hose_live_20261004T212933.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_style_live_20261004T175845.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_style_live_20261004T180716.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_style_live_20261004T212841.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_style_live_20261004T212919.json   FOUNDRY (generated evidence or earlier belt/mc runs; nothing source-critical, not committed by design)
```

