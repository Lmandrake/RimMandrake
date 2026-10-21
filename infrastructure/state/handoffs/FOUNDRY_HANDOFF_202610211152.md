# FOUNDRY_HANDOFF_202610211152 — READ FIRST on wake

Follows `FOUNDRY_HANDOFF_202610210531`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next session hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
**Owner order 2026-10-20 night (AFK): "keep your subagents going as long as you can ... get this new world up to full par and snuff ... then return to the modwork with the four biomes and GSS, flowworks, large animals, and art regen." It ENDS when he next writes.** Cap 2 subagents + a periodic art helper; run as a light orchestrator.

World look is built AND deployed AND live-read on the full list (R3 loaded, nothing saved over R3): peaks, Abyss/Rot swirls, Rust Cathedral, Rings, sun-flare fix, roads/rivers, feature import. He still has not SEEN the look; promotion of CANONICAL_ASHKARR_START waits for his eye. Cold-start doc: design/Jawa/worldbuilding/planet_state_2026-10-20.md. Flier rebuild is architecture-changed (GPT consult): one body plate + extracted wings; read design/RimMandrake/flier_authoring_architecture_2026-10-21.md first.

## What the owner should see

<!-- Findings that need the owner's eye or decision: a number nobody ruled on, a change they can veto, anything shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- Flier eye/shoulder-line sheet (all 18 facings LEVEL): D:\ClaudeWork\scratch\flier_lines\flier_lines_all.png. 12 flier sets stay HELD until he sees it; Sketto south eye points are hand-placed (least certain).
- Uvak south layered experiment preview: D:\ClaudeWork\scratch\uvak_south_experiment\uvak_south_preview.html (8 frames vs installed 4 is his call; wing top-of-stroke drapes).
- Uvak canon recolour + defect fix: D:\ClaudeWork\scratch\uvak_canon\fix\uvak_fix_before_after.png (grounded Uvak still red wings: decision).
- World look shots: D:\ClaudeWork\rimmandrake\scratch\live8\ (b_*, d_*, e_*, a_flare_8427_crop.png); faces preview D:\ClaudeWork\rimmandrake\scratch\faces_redraw\final_preview.png; peaks D:\ClaudeWork\rimmandrake\scratch\peakdecals\dewhorn_before_after.png.
- RustPuff B-D live shot (C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Screenshots\rustpuff_ABCD_live_20261021.png); art-regen review sheet D:\ClaudeWork\scratch\art_regen_night\art_regen_night_sheet_2026-10-21.html.
- Decisions: TITAN_PASSAGE_PRUNE_WHALES_ON_FOOT (exclude sea creatures/juveniles?); CANAL_OVERFLOW_BUILD_EVERY_PUDDLE_AUDITED (10 decisions, D1: fill-in water destroyed vs spill; doc design/RimMandrake/canal_overflow_flooding_2026-10-21.md); PIPE_POLE_SWITCH_DECIDE_HOSTAGE_TO_WIRES; RM_MothersPrice self-tamed young goes wild (bug or intended); JAWA_DROWNING_PROVE_RAT_SIZED_IN_SHALLOWS (should a 0.5 m Jawa drown in shallows); BIOME_DEFNAME_MIGRATION_WAVE_1 (dev saves carry RM_Wasteland/RM_NightsideIce on 3359 tiles: stub, re-point, or drop); 152 held DONOR art slots he kept.
- Flagged: biomes deploy also pushed BENCH's committed CreatureBehaviors/GelatinousSlime/Webwork DLLs (ruled not a seat violation; lesson filed). GPT flier answer: D:\ClaudeWork\rimmandrake\scratch\gpt_flier\gpt_answer.md.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_OR_TOPIC — state; NEXT: <one imperative action>`. A pointer without a NEXT: measured ~0% pickup; with one, near-100%. -->
- `FLIER_AFTERNOON_EXPERIMENT_PROVE_STILL_TORSO` — Uvak south built offline, all gates pass, look is his call, nothing installed; NEXT: wait for his word on the preview, then rebuild the other held sets by the layered pipeline.
- `FLIER_FRAMES_AUDIT_BODY_NOT_WING_EXTREMES` — tooling fixed (02931e44f), 12 sets HELD; NEXT: show him flier_lines_all.png and ask to release the held sets.
- `FLIER_FRAMES_FILL_FIVE_GHOST_FLOCKS` — donor frames installed, not flight-tested; NEXT: queue Brezak/Drexl/Thranta/Tibidee for the layered rebuild after his line test.
- `SHIP/LANDED/FOUNDERS dev saves` — still lack faction cleanup; NEXT: regenerate from the final R3-derived world once he has seen the look.
- `CANAL_OVERFLOW_BUILD_EVERY_PUDDLE_AUDITED` — design done and GPT-reviewed, proposed; NEXT: put the 10 decisions (D1 first) to him on a question card.
- `TITAN_CAMPS_SCAVENGERS_EVENTS_1` — A2-A5 passed live; NEXT: leave A6 (feel) for him; decide whale pruning via card.
- `PYRELANDS_STRUCK_GLASS_RITE_BUILD_1` — A1 passed, A2 partial (ritual button and completed rite not driven); NEXT: drive a completed rite on a quicktest Pyrelands map and verify one strike plus letter.
- `SCRUB_WILDLIFE_PROVE_NOBODY_CAME` — zero animals not reproduced on the full list (20 spawned); NEXT: on the next biomes_sprint load rebuild the Scrub site and read wildlife density if it gives 0.
- `JAWA_DROWNING_PROVE_RAT_SIZED_IN_SHALLOWS` — no repro; NEXT: with the theft save and StarWarsRaces loaded log pawn cell, lying/standing and water depth.
- `StarWarsRaces dd394d076` (BENCH DLL) and newest FlowWorks DLL 93a8b8c0b and later — NOT deployed; NEXT: run deploy_custom_mods.py dry-run at the next game-down and apply FOUNDRY's files.
- `DIRTY_CODE_REVIEW_STANDING_LOOP_1` — GSS/Pyrelands/Contagion/Scrub/HugeThings/FlowWorks partly done tonight; NEXT: review the remaining FlowWorks water-engine files (RM_MapComponent_Excavation, RM_LiquidNet, RM_LiquidNetKernel) and the 4 NORTHSTAR files.
- `SELFTEST_SWEEP_FIX_FOUR_REDS_REMAIN` — NEXT: with the game down run refresh.py then rerun the nightly reds.
- `HEADS_VERIFY_SHRUNK_TO_FIT_THE_HATS` — NEXT: ask him to look at D:\ClaudeWork\rimmandrake\scratch\live6\PHONE_lineup_hat.png and close.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives — append it to the lessons file the moment it is learned, then cite `(filed: LESSONS)` or `(see: <doc>)`. Never re-explain a trap that is already recorded. -->
- The deploy tool has no ownership markers; the biomes deploy ships every folded folder or nothing, so BENCH's committed DLLs ride along. (filed: LESSONS)
- required_checks.py ignores --help and rewrites the whole manifest (~90 s). (filed: LESSONS)
- python.exe from WSL does not see data-root env unless passed via WSLENV; bridge replies carry DurationMs, so ignore timing fields when comparing. (filed: LESSONS)
- Test-list biomes_sprint lacked VEF core, silently dropping defs; the site picker read waterCovered 1/0 as land (selftest fixture used True/False). (filed: LESSONS)
- jawa/list_pawns faction=none returned 0 on a map with 20 animals; filter from an unfiltered list. (filed: LESSONS)
- 'RM_PitDrowning' is not evidence of a pit: natural brine pools plus 0.5 m Jawa height drown colonists. (filed: LESSONS)
- Flier body-stabilize: failed estimator must be UNMEASURED not RE-POSED; exported-PNG equality gate counts only fully opaque pixels. (see: design/RimMandrake/flier_authoring_architecture_2026-10-21.md)

## Commits

```
1fe520982 lesson: defName rename tile check covers every keeper save
11ffe035c ledger: BIOME_DEFNAME_MIGRATION_WAVE_1 note - dev saves carry 3359 tiles on the old names; owner call owed
466dbf870 ledger: NORTHSTAR_FAST_DRIVER_1 done at 5e068bd4a; lesson: WSLENV for python.exe, DurationMs in replies
e22b375ca BENCH handoff 2026-10-21: night offline pile (pipe poles, cord, drawbridge proofs, Webwork, FA opt-out, stars), all undeployed
5e068bd4a northstar_driver: pipecheck proves pipelining correct live but no faster (1 reply/frame)
3a32a2529 conversations: catch-up 2 record(s)
0f8524893 Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com> Claude-Session: https://claude.ai/code/session_018tfAs1dZz6hkrRKynaSovR
b9b53e924 ledger: DIRTY_CODE_REVIEW_STANDING_LOOP_1 note (HugeThings pass)
5c7940949 HugeThings: WarningTicks clamps hours before the long cast; review marks 6 titan files clean
2a3364b27 code review: titanoslime_gates.py CLEAN after independent full read
268367220 titanoslime gates sweep spawns; Webwork harvest fog timeout UNMEASURED; Joining Water WORLDGEN label
870058d2f ledger + lessons: SCRUB_WILDLIFE full-list Scrub map has wildlife; site picker ocean bug fixed 283644b90
94a27aa4f Site picker: read waterCovered as the export's 1/0; ocean tiles were taken as land
fcd0d3b14 lesson: a refusal in a built hook needs its mirror in the lost hook
08d8f8563 titanoslime_gates: g3 gearless arm and g4 cut slimes are cleaned up, not leaked
230a4b268 titanoslime_gates: blind shed counts and gearless victims are UNMEASURED, not MOD FAIL
add600a73 Webwork ProofHarvest: refuse a node gone mid-wait; never report a stale yield
2de274da4 Suspension: losing a tower that never held the bridge swings nothing down
1db86ec52 lesson: OWNER ledger note text= is a gloss; only ownerSaid/byCard are verbatim
21011a5c6 ledger: close CRADLE_STRIKE_RECONCILE_WITH_LAB_DIVE; notes on breakout and sekkulaath items
... 137 more: git log --oneline 02c27d905..HEAD
```

## Tree state at wrap

- upstream: origin/main, pushed

Uncommitted (replace each marker below with whose it is — yours, another agent's, generated):

```
M Transient/biome_ffar/flowworks_owner_walk_art_sheet_2026-10-11.decisions.json   generated or another seat's (FlowWorks/BENCH scenes, modcheck, swap backups): not mine, left untouched
 M Transient/biome_ffar/phase0_remaining_art_sheet_2026-10-16.decisions.json   generated or another seat's (FlowWorks/BENCH scenes, modcheck, swap backups): not mine, left untouched
 M Transient/modcheck/fixtures.json   generated or another seat's (FlowWorks/BENCH scenes, modcheck, swap backups): not mine, left untouched
 M conversations/2026-10-20-1408-182141ac.md   generated or another seat's (FlowWorks/BENCH scenes, modcheck, swap backups): not mine, left untouched
 M deployed/config/ModsConfig.before-tier-fw_gss_sitting.xml   generated or another seat's (FlowWorks/BENCH scenes, modcheck, swap backups): not mine, left untouched
?? "D:\\ClaudeWork\\rimmandrake/"   generated or another seat's (FlowWorks/BENCH scenes, modcheck, swap backups): not mine, left untouched
?? Transient/fw_scenes/live/S1_20261017T084726.txt   generated or another seat's (FlowWorks/BENCH scenes, modcheck, swap backups): not mine, left untouched
?? Transient/fw_scenes/live/S1_20261017T084802.txt   generated or another seat's (FlowWorks/BENCH scenes, modcheck, swap backups): not mine, left untouched
?? Transient/fw_scenes/live/S1_20261017T092155.txt   generated or another seat's (FlowWorks/BENCH scenes, modcheck, swap backups): not mine, left untouched
?? Transient/fw_scenes/live/S1_20261017T110253.txt   generated or another seat's (FlowWorks/BENCH scenes, modcheck, swap backups): not mine, left untouched
?? Transient/fw_scenes/live/S1_p00.png   generated or another seat's (FlowWorks/BENCH scenes, modcheck, swap backups): not mine, left untouched
?? Transient/fw_scenes/live/S1_p03.png   generated or another seat's (FlowWorks/BENCH scenes, modcheck, swap backups): not mine, left untouched
?? Transient/fw_scenes/live/S1_p10.png   generated or another seat's (FlowWorks/BENCH scenes, modcheck, swap backups): not mine, left untouched
?? Transient/fw_scenes/live/S1_p14.png   generated or another seat's (FlowWorks/BENCH scenes, modcheck, swap backups): not mine, left untouched
?? Transient/fw_scenes/live/S2_20261017T084824.txt   generated or another seat's (FlowWorks/BENCH scenes, modcheck, swap backups): not mine, left untouched
?? Transient/fw_scenes/live/S2_20261017T092355.txt   generated or another seat's (FlowWorks/BENCH scenes, modcheck, swap backups): not mine, left untouched
?? Transient/fw_scenes/live/S2_20261017T110404.txt   generated or another seat's (FlowWorks/BENCH scenes, modcheck, swap backups): not mine, left untouched
?? Transient/fw_scenes/live/S2_p00.png   generated or another seat's (FlowWorks/BENCH scenes, modcheck, swap backups): not mine, left untouched
?? Transient/fw_scenes/live/S2_p10.png   generated or another seat's (FlowWorks/BENCH scenes, modcheck, swap backups): not mine, left untouched
?? Transient/fw_scenes/live/S2_p30.png   generated or another seat's (FlowWorks/BENCH scenes, modcheck, swap backups): not mine, left untouched
... 153 more uncommitted paths (by top-level dir: Transient 149, deployed 3, src 1): git status --short
```

