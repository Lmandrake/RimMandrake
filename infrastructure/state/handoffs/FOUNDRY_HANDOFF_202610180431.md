# FOUNDRY_HANDOFF_202610180431 — READ FIRST on wake

Follows `FOUNDRY_HANDOFF_202610180022`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next session hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
Order (owner, Sat 2026-10-17 ~10:5x AM PDT, AFK all day): "As long as bridge is available (set up a watcher to check) it can be yours yes. You don't need to restore my modlist EVER unless you yourself need it. There's no live game right now." Proceed on recommended defaults; FlowWorks plus donor offline work; silent until he returns; cap 3 helpers; ENDS when he next writes. STATE: the whole FlowWorks one-big-rebuild (P3 exact-level water, P4/P8 metres+readout, P5/P6 deeper digs, P7 relative pit rules, P11 lake floors, P12 deep swimming, P13 fish/reeds, pump/hose/fill-in/prisoner-sweep/dug-reservoir-swim fixes) is now BUILT AND LIVE-PROVEN on DLL 487e9161d except the rows listed below: validation_v2 is back at 61/0/0 on RM_TestSite_calm_v2 (the 24-FAIL regression was an old 22-mod saved test map + a stale reference model + the P11 shore shelf on painted ponds, NOT product regressions; saved map `RM_TestSite_calm_v1` is poisoned on the 11-mod list, v2 is the good one). Bridge: BENCH drives it with unattributed scripts, so `driver lock: FREE` + idle hold is NOT proof it is free: check D:\Luke\dev\_rmscratch\bridge_calls.jsonl for calls in the last ~10 min before taking it (filed: LESSONS). The game is left running on the 11-mod flowworks list; BENCH's 22-mod list was saved by the live driver, not restored.

## What the owner should see

<!-- Findings that need the owner's eye or decision: a number nobody ruled on, a change they can veto, anything shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- FlowWorks plan + ticket table: `D:\Luke\dev\RimMandrake\design\RimMandrake\flowworks_one_rebuild_plan_2026-10-17.md` and flowworks_ticket_consolidation_2026-10-17.md (epic FLOWWORKS_DEPTH_REBUILD_ONE_BIG_DIG). Day reports: Transient\fw_scenes\live_day3_report.md and live_day4_report.md; lake-floor panels Transient\fw_scenes\lake_floors\live\index.html; canal objects/rivers/water-scene sheets Transient\fw_scenes\live\{objects,rivers,annotated}\index.html; water art candidates (nothing installed; images now committed): Transient\biome_ffar\water_art_candidates_sheet_2026-10-17.html.
- RE-VALIDATE five north-star bars in ONE sitting (his only): still_water_one_surface_height (new draft; selftest_human_review flags it as uncovered by any walk row: add the covering row), fill_tier_legible, depth_and_fill_jointly_legible, pit_depth_ladder_legible, pawn_height_ladder_legible (FLOWWORKS_BARS_JUDGE_FIVE_IN_ONE_SITTING).
- RULINGS HE OWES: (1) DROWNING IN SHALLOWS: with swimming ON (default) a downed colonist in 1 m shallows drowns in about 1.15 game hours (MEASURED), OFF = no drowning in an hour; setting RM_SwimSettings.shallowWaterDrowningEnabled. (2) P7 V6 pit room = person-height pocket at any depth conflicts with his 2026-10-16 'Superdeep only' card (pitRoomMinDepthMetres=2 restores). (3) P11_FLOOR_ON_PAINTED_PONDS (should painted ponds get a lake floor at all) and LAKE_FLOORS_SHALLOW_LAKES_STAY_ONE_METRE (flat/hill maps' lakes are all shallow: only mountain chasm lakes are deep). (4) Raiders vs sheer trench: day-4 run had raiders stall far out; scaling-ladder question unasked (DEPTH_QUESTIONS_ASK_RAIDERS_FIRST). (5) The 11 vetoes in DEPTH_DEFAULTS_ASK_ELEVEN_VETOES and the 5 consolidation calls; P12/P11/P13 defaults in their build logs. (6) Is a filth puddle an allowed home for hose leftover (default conserving).
- ART he must LOOK at before anything ships: the water candidates sheet above (wall band, very-shallow look, canal-vs-lake blue, deep tints); lake floor variety panels.
- Donor: DONOR_SUCCULENT_ART_DECIDE_A_STAND_IN and DONOR_ROSTER_GUARDS_FIX_WRONG_PACKAGE_ID wait for his sitting.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_OR_TOPIC — state; NEXT: <one imperative action>`. A pointer without a NEXT: measured ~0% pickup; with one, near-100%. -->
- `FLOWWORKS_DEPTH_REBUILD_ONE_BIG_DIG` — built and live-proven except: P13 fish rows (the bridge cannot read pond fish), reeds grace (untested), river extension chain (needs a river site), P5 dig by designator (3.3 colonist-days; drive tool used), raid-trench mask-swap row, drafted-drowning row; NEXT: add a bridge fish-read surface, stage a river site, then run those rows and `rimflow verify` each child with evidence files only.
- `VALIDATION_V2_RECONCILE_AFTER_THE_BIG_DIG` — 61/0/0 on calm_v2 with DLL 487e9161d; NEXT: close it citing live_day4/day5 evidence once he has seen the report.
- `DIRTY_CODE_REVIEW_STANDING_LOOP_1` — ~22+ files CLEAN today, about 45 FlowWorks files still DIRTY (Hose/*, RM_LiquidHeat.cs, RM_LiquidBody.cs, RiverColors/*, Designator_DigCanal.cs, PondReturnChecks.cs); NEXT: run a whole-file review round on those in a scratch clone using Transient/fw_scenes/review_day3_log.md's procedure.
- `WATER_SCENES_S5_JUDGE_THIRD_DRAFT` — S5 runs 12 MATCH/1 DIFFER live (the DIFFER is the doc's whole-notch wording); sealed scenes json untouched; NEXT: redraw S5 for level water and ask him to approve.
- `PIT_CLIMB_PROVE_RAIDERS_VS_SHEER_TRENCH` — 12 PASS + trench-raid runs inconclusive; NEXT: rerun raid_trench_proof.py with the relative rules and a raid that actually reaches the trench.
- `CANAL_OBJECTS_SHEET_BUILD_POSES_AND_STYLES` and `RIVER_SCENES_BUILD_WALKTHROUGH_WITH_CAPTIONS` — run live once; NEXT: let him judge the looks.
- `DONOR_PHASE0_FINISH_AWAITING_HIS_RULINGS` — offline proposals done, rulings his; NEXT: at his sitting fix Bileworm/Zrrik guards and run the ikee swap on the FULL list.
- The 9 older pointers from FOUNDRY_HANDOFF_202610161835.md (ART_QUEUE_DRAIN_AND_SHEETS, PACK_OVERLAYS_BUILD_SHARED_SADDLEBAGS, ALPHA_BIOMES_CENSUS_THE_REST_OF_IT, SUCCULENT_PLANTS_REDRAW_BORROWED_WARDROBE, ZISSKA_FIRESPIT_PROVE_LIVE, ARTPIPED_BENCH_CLONE_PULL, DHOGGUR_STATUS_REPORT_SWOLLENART, GPT_EDGE_CASE_ITEMS_25_OWE_LIVE, BIOME_SPRINT_ROUND3) were not touched; NEXT: wake them one by one from that file.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives — append it to the lessons file the moment it is learned, then cite `(filed: LESSONS)` or `(see: <doc>)`. Never re-explain a trap that is already recorded. -->
- Bridge idle time counts ledger silence only; BENCH's unattributed live scripts keep it busy while the lock reads FREE (filed: LESSONS).
- ./publish and ./sync refuse when another helper has uncommitted edits to a file origin changed (BENCH commits FlowWorks DLLs all day): publish from a scratch clone under /home/mandrake/rm/scratch/FOUNDRY/<name>, rebuild the DLL on the merged tree, never hand-merge a binary (see: Transient/fw_scenes/p4_build_log.md).
- A saved test map from another mod list loads with missing-corpse NREs and the clock never advances: every pawn row fails; remake the site on the current list (see: Transient/fw_scenes/live_day4_report.md).
- The bridge test profile (companion_profile.json) expires silently and every static_call is then REFUSED; only expiresUtc may be extended (see: Transient/fw_scenes/live_day_report.md).
- Offline oracles share the author's assumptions: whole-square pond recession and S2 [4 0 4 0] only showed live; the deployed DLL was a day stale (see: Transient/fw_scenes/p3_build_log.md).

## Commits

```
01f420156 water art candidates: commit the sheet images
d219a67c2 ledger: FOUNDRY bridge take/release, live day 5
299f54ecf ledger: FOUNDRY live day 5 verifies
5360cda86 Live day 5 on DLL 487e9161d: v2 calm2 61/0/0, prisoner sweep returns and stays, S5 12/1 (S5.i only vs whole-notch doc)
a3ab75fd5 prisoner return log: published
487e9161d FlowWorks DLL: prisoner return fix
0bf02772a Returned prisoner comes back to a cell that holds it, not an edge cell
0e8ce7dab water_scenes_walk: pin deepBedsEnabled off per scene run (restored in finally); pristine = nothing dug
6902efb9a ledger: FOUNDRY bridge take/release, live day 4
97292148b ledger: FOUNDRY live day 4 verifies
b8975c229 v2 61/0/0 on fresh map and calm v2; calm v1 was the pawn block; fix3 proofs
46730dbd3 v2 rerun after triage on the calm site: 46/9/6; ledger game stamps
6186002a5 ledger: fix3 build notes (swim dug, sweep prisoner, hose leftover)
6699957b8 FlowWorks DLL: fix3 (built on 47b1a5045)
47b1a5045 FlowWorks fix3: dug water >= 2 m is swum; prisoner escape into a current is a sweep; hose leftover finds a home map-wide
33461177a ledger: v2 triage note (VALIDATION_V2_RECONCILE_AFTER_THE_BIG_DIG)
c38ffbe8e validation_v2: exact-level oracle, site pins lake floors off; day-3 triage
e23ef031a ledger: validation_v2 reconcile item
41634ac37 ledger: four live-found bug items (P10 round)
ff21fd684 ledger: FOUNDRY bridge take/release for the live day 3 round
... 7 more: git log --oneline 37a292b62..HEAD
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
?? Transient/ModsConfig.owner.547.bak   generated/other (sheet tooling, mod-list tier backups, another seat; not mine)
?? Transient/biome_ffar/img/00063bfc98bbf60c00c9.webp   generated/other (sheet tooling, mod-list tier backups, another seat; not mine)
?? Transient/biome_ffar/img/004678d5bc522129f222.webp   generated/other (sheet tooling, mod-list tier backups, another seat; not mine)
?? Transient/biome_ffar/img/0052887ea95ee55cb4ce_full.png   generated/other (sheet tooling, mod-list tier backups, another seat; not mine)
?? Transient/biome_ffar/img/0099e32f18695cf71e35.webp   generated/other (sheet tooling, mod-list tier backups, another seat; not mine)
?? Transient/biome_ffar/img/012b0e9de80257c66cba.webp   generated/other (sheet tooling, mod-list tier backups, another seat; not mine)
?? Transient/biome_ffar/img/012c446f56fabd4bd893_full.png   generated/other (sheet tooling, mod-list tier backups, another seat; not mine)
?? Transient/biome_ffar/img/0139244f2dcf4a25b9e9.webp   generated/other (sheet tooling, mod-list tier backups, another seat; not mine)
?? Transient/biome_ffar/img/0172b49133d12ef1a9d8.webp   generated/other (sheet tooling, mod-list tier backups, another seat; not mine)
... 1535 more uncommitted paths (by top-level dir: Transient 1524, deployed 6, src 2, (root) 1, conversations 1, infrastructure 1): git status --short
```

