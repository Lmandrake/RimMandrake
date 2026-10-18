# FOUNDRY_HANDOFF_202610180022 — READ FIRST on wake

Follows `FOUNDRY_HANDOFF_202610170618`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next session hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
Order (owner, Sat 2026-10-17 ~10:5x AM PDT, AFK all day): "As long as bridge is available (set up a watcher to check) it can be yours yes. You don't need to restore my modlist EVER unless you yourself need it. There's no live game right now." Plus: proceed on recommended defaults, FlowWorks plus donor retirement offline work, stay silent until he returns, cap 3 helpers; ENDS when he next writes. Everything built today (P3 exact-level water, P4/P8 metres+readout, P5/P6 deeper digs, P7 relative pit rules, P11 lake floors, P12 deep swimming, P13 fish/reeds, pump/hose/fill-in fixes, river-sweep identity fix) is OFFLINE-ONLY: only P3+P4 (DLL 79ac42417) ever ran live. BENCH held the bridge all evening for its thirst rounds and drives it with unattributed scripts, so `driver lock: FREE` + idle hold is NOT proof it is free: check D:\Luke\dev\_rmscratch\bridge_calls.jsonl for calls in the last ~10 min before taking it. The first live job is agent a54a76818724030e7's brief (deploy origin DLL, validation_v2 61/0/0 baseline, S1-S6 walk, all owed proofs, lake-floor look); the whole day's value is unproven until it runs.

## What the owner should see

<!-- Findings that need the owner's eye or decision: a number nobody ruled on, a change they can veto, anything shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- FlowWorks plan: `D:\Luke\dev\RimMandrake\design\RimMandrake\flowworks_one_rebuild_plan_2026-10-17.md` (epic FLOWWORKS_DEPTH_REBUILD_ONE_BIG_DIG; ticket table in flowworks_ticket_consolidation_2026-10-17.md).
- RE-VALIDATE five north-star bars in ONE sitting (his only): still_water_one_surface_height (new draft), fill_tier_legible, depth_and_fill_jointly_legible, pit_depth_ladder_legible, pawn_height_ladder_legible (FLOWWORKS_BARS_JUDGE_FIVE_IN_ONE_SITTING).
- Rulings needing his veto (defaults taken): P7 V2-V6 (V6 pit room = person-height pocket at any depth CONFLICTS with his 2026-10-16 card 'Superdeep only'; setting pitRoomMinDepthMetres=2 restores it); P12 swim defaults; P11 lake roughness table/shelf/50 m ceiling; P13 fish/reeds defaults; the 11 vetoes in DEPTH_DEFAULTS_ASK_ELEVEN_VETOES; the 5 consolidation calls (absorb FLOWWORKS_BUILD_PROGRAM_1, DEEP_DIG droids, POND stages, RM_WaterThin is the 0.5 m band not the under-25 cm look, litres migration absorbed unproven).
- DROWNING IN SHALLOWS: with swimming ON (default) a downed person drowns in ~1 h in any 0.5 m natural shallows; small animals tire and drown there. Setting RM_SwimSettings.shallowWaterDrowningEnabled switches it off alone. Needs his ruling before ship.
- RAIDERS vs SHEER TRENCH: live proof showed a gunner shooting across a 2 m trench downed all colonists; no raider entered; the scaling-ladder question is unasked (DEPTH_QUESTIONS_ASK_RAIDERS_FIRST). P5/P6 must not ship before P7 + the climb proof pass.
- Water art candidates sheet (nothing installed): `D:\Luke\dev\RimMandrake\Transient\biome_ffar\water_art_candidates_sheet_2026-10-17.html` (images exist only under the scratch clone /home/mandrake/rm/scratch/FOUNDRY/art/Transient/ until make_water_art.py regenerates them). Lake floor preview: Transient\fw_scenes\lake_floors\index.html. Canal objects/rivers/water-scene sheets: Transient\fw_scenes\live\{objects,rivers,annotated}\index.html.
- Donor: DONOR_SUCCULENT_ART_DECIDE_A_STAND_IN (13 plants + lunger fry need art, his permission) and DONOR_ROSTER_GUARDS_FIX_WRONG_PACKAGE_ID (Bileworm guard packageId typo mandrake.rm.scarlands; Zrrik inside a donor-only block) wait for his sitting.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_OR_TOPIC — state; NEXT: <one imperative action>`. A pointer without a NEXT: measured ~0% pickup; with one, near-100%. -->
- `BRIDGE_LIVE_ROUND_P10` (owner brief in agent a54a76818724030e7) — nothing run live since 79ac42417; NEXT: when bridge_calls.jsonl is quiet >10 min and `rimflow bridge who` is FREE, resume agent a54a76818724030e7 (or re-brief) to deploy the origin DLL and run validation_v2, S1-S6, swim/pit/dig/pump/river-sweep proofs, lake-floor staging and the P13 proofs.
- `FLOWWORKS_DEPTH_REBUILD_ONE_BIG_DIG` — P3,P4,P5,P6,P7,P8-data,P11,P12,P13 built offline, P9 art sheet drafted, P14 is BENCH's, P10 deploy+walk waits on the bridge; NEXT: after live proof, `rimflow verify` each child with evidence files only.
- `DIRTY_CODE_REVIEW_STANDING_LOOP_1` — 22+ files CLEAN today, about 50 FlowWorks files still DIRTY (Hose/*, RM_LiquidHeat.cs, RM_LiquidBody.cs, RiverColors/*, Designator_DigCanal.cs, PondReturnChecks.cs); NEXT: run a whole-file review round on those in a scratch clone using the procedure in Transient/fw_scenes/review_day3_log.md.
- `WATER_SCENES_S5_JUDGE_THIRD_DRAFT` — S5 doc rows S5.a/c/G assume whole notches, sealed json untouched; NEXT: redraw S5 for level water and ask him to approve it.
- `PIT_CLIMB_PROVE_RAIDERS_VS_SHEER_TRENCH` — 12 PASS plus a partial trench-raid run; NEXT: rerun raid_trench_proof.py with the relative rules live.
- `CANAL_OBJECTS_SHEET_BUILD_POSES_AND_STYLES` and `RIVER_SCENES_BUILD_WALKTHROUGH_WITH_CAPTIONS` — run live once (objects 38/38, rivers 15 match/1 differ/1 unmeasured); NEXT: let him judge the looks, then rerun rivers R3 after the river-sweep deploy.
- `DONOR_PHASE0_FINISH_AWAITING_HIS_RULINGS` — texture, save-copy and roster proposals done offline, rulings his; NEXT: at his sitting fix the Bileworm/Zrrik guards and run the ikee swap on the FULL list.
- The 9 older pointers from FOUNDRY_HANDOFF_202610161835.md (ART_QUEUE_DRAIN_AND_SHEETS, PACK_OVERLAYS_BUILD_SHARED_SADDLEBAGS, ALPHA_BIOMES_CENSUS_THE_REST_OF_IT, SUCCULENT_PLANTS_REDRAW_BORROWED_WARDROBE, ZISSKA_FIRESPIT_PROVE_LIVE, ARTPIPED_BENCH_CLONE_PULL, DHOGGUR_STATUS_REPORT_SWOLLENART, GPT_EDGE_CASE_ITEMS_25_OWE_LIVE, BIOME_SPRINT_ROUND3) were not touched; NEXT: wake them one by one from that file once FlowWorks live proof is done.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives — append it to the lessons file the moment it is learned, then cite `(filed: LESSONS)` or `(see: <doc>)`. Never re-explain a trap that is already recorded. -->
- Bridge idle time counts ledger silence only; unattributed live scripts (thirst_live, sprinkler_live, load_walk) keep BENCH driving while the lock reads FREE (filed: LESSONS).
- ./publish and ./sync refuse when another helper has uncommitted edits to a file origin changed (BENCH commits FlowWorks DLLs all day): publish from a scratch clone under /home/mandrake/rm/scratch/FOUNDRY/<name>, rebuild the DLL on the merged tree, never hand-merge a binary (see: Transient/fw_scenes/p4_build_log.md).
- The bridge test profile (companion_profile.json) expires silently and every static_call is then REFUSED: a walk that measures nothing is this, not the game (see: Transient/fw_scenes/live_day_report.md).
- Offline oracles share the author's assumptions: the S2 [4 0 4 0] pattern and whole-square pond recession only showed live, and the deployed DLL was a day stale (see: Transient/fw_scenes/p3_build_log.md).

## Commits

```
11c2d2f5a lesson: bridge idle time ignores unattributed live script calls
83fa83337 ledger: game-state events from the credited rerun
6b26634e8 credited rerun: thirst_live + sprinkler_live full at FlowWorks 8b8aa4a2 (DLL 05fabdc5); ledger, lesson
6fb91887a FlowWorks DLL rebuilt on bf1e344d1 (RIVER_SWEEP_FIX_COLONISTS_RETURN_AS_NPCS)
bf1e344d1 RIVER_SWEEP_FIX_COLONISTS_RETURN_AS_NPCS: held pawns are not Free world pawns; state restored on return
0fe44a6ea ARTPIPE_FACING_COHERENCE_1: AFK check, S2 live, backlog already regenerated/scoped
8cdc885d9 lesson: a 'none left' predicate measures the last item
a52619494 code review: thirst_live.py, ThirstChecks.cs CLEAN at 43a993be3d
43a993be3 thirst_live review: T25 full-run FAIL was the harness (waited for the last of 4 snow buckets); follow by ID
dfba5a285 ledger: thirst live round 2 outcome
f35aefed8 thirst live round 2: credit note (FOUNDRY's P11/P12 moved the mod hash)
5ae7e99ef thirst live round 2: credited thirst/sprinkler results on 3b33f2bbfe, T25 leftover-bucket clear, lessons, ledger stamps
d0b05a33d walks: water scenes read decilitres + level rows, indexes accumulate, annotate prints readout and surface gap
54fe4ef75 ledger: FOUNDRY shard events (P11/P12/bugs builders)
d5e1fbd8f ledger: FOUNDRY P11 built offline (0b30f2a02, DLL 645684ed2)
dfaadda10 P11 build log and lake floor preview (8 lakes)
645684ed2 FlowWorks DLL rebuilt on P11 (0b30f2a02)
0b30f2a02 P11: lake floors per lake and biome roughness, recorded at map creation
6955ddf0a ledger: FOUNDRY pump-feed, hose-leftover, sheet fill-in fixes built offline (b5459caa0, DLL e40b3d972)
e40b3d972 FlowWorks DLL rebuilt on the decilitre pour/fill-in fixes (b5459caa0)
... 196 more: git log --oneline 4725df80d..HEAD
```

## Tree state at wrap

- upstream: origin/main, pushed

Uncommitted (replace each marker below with whose it is — yours, another agent's, generated):

```
M Transient/biome_ffar/abyss_sheet_2026-10-04.html   generated/other (sheet tooling, mod-list tier backups, another seat; not mine)
 M Transient/biome_ffar/aiwha_wingfirst_sheet_2026-10-15.html   generated/other (sheet tooling, mod-list tier backups, another seat; not mine)
 M Transient/biome_ffar/phase0_remaining_art_sheet_2026-10-16.decisions.json   generated/other (sheet tooling, mod-list tier backups, another seat; not mine)
 M Transient/biome_ffar/scale_ground_measured.json   generated/other (sheet tooling, mod-list tier backups, another seat; not mine)
 M Transient/mc_human_review/KEYSHEET.md   generated/other (sheet tooling, mod-list tier backups, another seat; not mine)
 M Transient/mc_human_review/keysheet.html   generated/other (sheet tooling, mod-list tier backups, another seat; not mine)
 M Transient/modcheck/fixtures.json   generated/other (sheet tooling, mod-list tier backups, another seat; not mine)
 M Transient/phase0_p6_save_renames.md   generated/other (sheet tooling, mod-list tier backups, another seat; not mine)
 M conversations/2026-10-16-0549-c453ca3a.md   generated/other (sheet tooling, mod-list tier backups, another seat; not mine)
 M conversations/2026-10-16-1218-9a5985c9.md   generated/other (sheet tooling, mod-list tier backups, another seat; not mine)
 M conversations/2026-10-16-1839-6972cfb2.md   generated/other (sheet tooling, mod-list tier backups, another seat; not mine)
 M infrastructure/state/ledger/events/FOUNDRY.jsonl   generated/other (sheet tooling, mod-list tier backups, another seat; not mine)
?? Transient/ModsConfig.owner.547.bak   generated/other (sheet tooling, mod-list tier backups, another seat; not mine)
?? Transient/biome_ffar/img/00063bfc98bbf60c00c9.webp   generated/other (sheet tooling, mod-list tier backups, another seat; not mine)
?? Transient/biome_ffar/img/004678d5bc522129f222.webp   generated/other (sheet tooling, mod-list tier backups, another seat; not mine)
?? Transient/biome_ffar/img/0052887ea95ee55cb4ce_full.png   generated/other (sheet tooling, mod-list tier backups, another seat; not mine)
?? Transient/biome_ffar/img/0099e32f18695cf71e35.webp   generated/other (sheet tooling, mod-list tier backups, another seat; not mine)
?? Transient/biome_ffar/img/012b0e9de80257c66cba.webp   generated/other (sheet tooling, mod-list tier backups, another seat; not mine)
?? Transient/biome_ffar/img/012c446f56fabd4bd893_full.png   generated/other (sheet tooling, mod-list tier backups, another seat; not mine)
?? Transient/biome_ffar/img/0139244f2dcf4a25b9e9.webp   generated/other (sheet tooling, mod-list tier backups, another seat; not mine)
... 1494 more uncommitted paths (by top-level dir: Transient 1483, deployed 6, src 2, (root) 1, conversations 1, infrastructure 1): git status --short
```

