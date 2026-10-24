# FOUNDRY_HANDOFF_202610241937 — READ FIRST on wake

Follows `FOUNDRY_HANDOFF_202610241805`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next session hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
Every DIRTY *code* file is now CLEAN (enact, art_sheet, deploy_custom_mods, art_eval runner/shadow, fauna_drive, round_series, world_face_variants, art.py, artledger, the 59-file SWB/tuning cluster); reviewers found 6 severe defects this sitting and filed ~25 lesser items. What remains DIRTY is ~200 XML defs 'dirty by design + owner decisions' and 2916 never-reviewed files: the standing loop item DIRTY_CODE_REVIEW_STANDING_LOOP_1 has nothing code-shaped left. (filed: items)

## What the owner should see

<!-- Findings that need the owner's eye or decision: a number nobody ruled on, a change they can veto, anything shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- Savegames: Saves folder cut 5.2G->1.1G; current world save recorded as ASHKARR_DEV_START_2026-10-20_PARITY_QUIET_R3 (section in infrastructure/state/CANONICAL_SAVE.md); canon.yml still names the frozen 09-12 save and six tools default to it: your call whether to repoint.
- Transient/: 2,246 tracked files released (modcheck, old pins); 31 cited-but-unpinned paths remain.
- leaningscrub_2 TunnelSnake B / Vurra B still blocked by a newer card-installed keep: need his word.
- (Companion mail ledger unreadable at wake; no draft is carried by this seat.)

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_OR_TOPIC — state; NEXT: <one imperative action>`. A pointer without a NEXT: measured ~0% pickup; with one, near-100%. -->
- `LADDERCLIMBERS_RENAME_MOVED_RM_DEFS` — filed for BENCH (5 creatures lost ladder climbing); NEXT: BENCH to claim it.
- `WORLD_WATER_REDRAW_SEAS_THAT_READ_DEEP` — Chill/Twilight faces wait on his picks of the r3 sheet; NEXT: collect his picks, install them, then build SEA_FILMS_TUNE_PER_SEA_CHILL_UNLIT.
- `SWB_BIOMESTEAM_MIGRATE_AS_ONE_FOLDER` — not started; NEXT: design the one-folder migration as a builder item with a C# rebuild.
- `ENACT_KEPT_CONFLICT_FIX_PARTIAL_PLAN` — open (and ENACT_APPLY_REFUSED_HARDEN_PARTIAL_PICK, ENACT_VARIANT_TICK_FIX_MOVED_LANE); NEXT: fix PARTIAL_PLAN first with one rm-builder.
- `ARTPIPE_FOREIGN_COPY_AUDIT_111_DONE_JOBS` — series stopped; NEXT: re-judge Crustweevil/Dustflutter/Fuzzrunner/Surrik/Peeper round-1 renders.
- `FUNGALWEEVIL_LABEL_JUDGE_PROPOSES_NEW` — NEXT: spawn a judge agent to propose the Grellik label.
- New lesser items (ART_*, ARTEVAL_*, DEPLOY_PLAN_*, FAUNA_*, SHADOW_*, 7 SWB) have titles but no spec sections; NEXT: write specs when each is claimed.
- Earlier pointers (water r3, world look program, ATMOSPHERIC_BASE_BUILD_PROGRAM_1, RIMPULSE_*) unchanged; NEXT: reread FOUNDRY_HANDOFF_202610241805 pointers.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives — append it to the lessons file the moment it is learned, then cite `(filed: LESSONS)` or `(see: <doc>)`. Never re-explain a trap that is already recorded. -->
- Reviewers each edit the shared ledger file, so one reviewer's commit swept another's events (harmless, but expect cross-attribution) (filed: commit 5f8c61efef).
- `transient_pin.py rm <files>` builds its commit subject from every path; unpin dirs by name instead (see: transient_pin.py).
- zsh does not word-split `$(git diff --name-only)` into pathspecs: use an array `"${(@f)...}"`  (filed: lessons).

## Commits

```
563c31dd3d review marks: art.py, artledger.py, selftest_enact_stale_lane.py CLEAN; ledger: file ART_ROTATE_FIX_LATE_APPEND_LOST, ART_INDEX_CACHE_FIX_ABSORB_RACE, ENACT_STALELANE_TEST_FIX_FIXTURE_LEAK, ART_INSTALL_DRYRUN_FIX_STORE_WRITE
613c42e09d artledger.canonical_mod: refuse a nonexistent mod, a bare tier or a mod subfolder (installed art at a dead slot no deploy reads); selftest
90c93815a2 code review wave 2026-10-24: 10 previously-CLEAN files re-reviewed since their clean marks, 0 severe, 3 items filed (REVIEW_SIGN_FIX_DOC_NAMES_NOVEL, RIMFLOW_LANE_HARDEN_BAD_JSON, SCALE_PANEL_FIX_THREE_AXIS_OFFSET)
972bb752ab ledger: game stamps from the live session; FlowWorks redeploy (tar glass, dug fill, plank/sprinkler/reel/pail art)
4e1dc866fb BENCH live session end: game down, bridge released
0b4ea2b747 FW art review: file PIT_SPIKES_FIX_READ_AS_FUZZ_LIVE, PIT_WALL_FIX_TAN_WEST_STRIP, LADDER_PORTABLE_FIX_SOUTH_INVISIBLE, RAIL_LADDER_FIX_UP_DOWN_ALIKE (live captures)
1777bb8ccf ledger sync: close DEPLOY_GUARD/ARTEVAL_TUNING/SWB_MOVE _VET_UNREVIEWED at 57da2d3b79
7b8089ee21 code review: SWB move + art_eval tuning + deploy guard cluster CLEAN (59 files, full-file review, 0 severe, 8 items filed)
f8de3ae546 MODCHECK_RUN_DIAGNOSE_TICK_ONE_STALL: close (prose to closed/, ledger close event)
f17e02293b MODERN_BOTTLE_REDRAW_SODA_AND_ORANGE_PAIL: Modern bottle label repainted as soda trade dress (cola red, white S-swoosh, no text) and Modern bucket body blue->orange, liquid/trim/alpha/masks byte-identical (modern_soda_pail.py); bottle_reads_as_soda + pail_is_orange FAIL on the pilots, PASS installed; selftest soda_pail; owner sheet still owed
87998efd85 MODCHECK_RUN_DIAGNOSE_TICK_ONE_STALL: stall was the offline rivers_switch_flips chain waiting ~9 min on the C# SelfTest (py-spy); runner prints per-chain START/END lines, _selftest_cases announces itself; file MODCHECK_SITE_FIX_RAIDS_KILL_THE_RUN + FLOWWORKS_MODCHECK_FIX_SIX_STANDING_FAILS
3f4678815b HOSE_REEL_REDRAW_FIREHOSE_ON_THE_DRUM: code review marks + note (held for owner's frame-colour call); lesson art_sheet RM_HoseReel set overflow
1550161415 HOSE_REEL_REDRAW_FIREHOSE_ON_THE_DRUM: the Modern reel's drum hose redrawn as a red woven-canvas firehose on the unchanged waterworks-blue frame (firehose_reel.py: per-texture coil-stack masks, matte canvas ramp, twill); drum_hose_reads_as_firehose FAILS on the all-blue reel and the glossy red original; frame pinned to the blue recolour outside the hose; owner sheet hose_reel_firehose_on_the_drum
89d41ff8b7 SPRINKLER_HEAD_REDRAW_SEEN_FROM_ABOVE: code review marks + close
cb78420900 SPRINKLER_HEAD_REDRAW_SEEN_FROM_ABOVE: sprinkler heads drawn seen from above, one per look cut from its pump hub (nozzle plate, drawOffset 0); checks head_top_down (FAILS on the squat side-view heads) + head_seat_on_centreline (the owed centreline check) replace the clamp check; owner sheet sprinkler_head_seen_from_above
71c5054a2c code review: RM_FlowTaps, RM_MapControlMath, RM_LevelHolder, MapControlChecks, Flood_FlowWorks, RM_StockMath, RM_LiquidBottleUtility CLEAN (full-file review); DUG_FILL_FIX_WALKS_TO_SHEET close
c42010afd3 DUG_FILL_FIX_WALKS_TO_SHEET: the liquid-cell search skips a dug cell whose water cannot pay one container (pawns no longer loop on a thin sheet); review marks for batch A files
4169fce376 TAR_GLASS_FLOOD_FIX_UNREACHABLE_PATH: a tar release's undug bank hardens to glass (every reached cell is dug and dug cells never cool, so the glass edge was never written)
bff6e57c4a PLANK_COVER_REDRAW_READS_AS_EMPTY_PIT: code review marks + ledger note
223f7c9f8b PLANK_COVER_REDRAW_READS_AS_EMPTY_PIT: offline cover compositor + checks (shipped ground print FAILS reads-as-material on the owner's centre-lid shot; drawn/edge-to-edge tier art PASSES); owner sheet plank_cover_reads_as_planks (pick: drawn covers vs pit_covered_invisible); files WOVEN_SCRAP_COVER_REDRAW_FILLS_ITS_CELL, PIT_OCCLUDER_LID_FIX_DRAWS_COVER_ART
... 28 more: git log --oneline b94bd84d84..HEAD
```

## Tree state at wrap

- upstream: origin/main, pushed

Uncommitted (replace each marker below with whose it is — yours, another agent's, generated):

```
M deployed/config/ModsConfig.before-tier-flowworks.xml   BENCH/generated: not mine
 M infrastructure/state/ledger/events/FOUNDRY.jsonl   mine (ledger shard)
?? Transient/fw_scenes/live/S1_20261017T084726.txt   BENCH/generated: not mine
?? Transient/fw_scenes/live/S1_20261017T084802.txt   BENCH/generated: not mine
?? Transient/fw_scenes/live/S1_20261017T092155.txt   BENCH/generated: not mine
?? Transient/fw_scenes/live/S1_20261017T110253.txt   BENCH/generated: not mine
?? Transient/fw_scenes/live/S1_p00.png   BENCH/generated: not mine
?? Transient/fw_scenes/live/S1_p03.png   BENCH/generated: not mine
?? Transient/fw_scenes/live/S1_p10.png   BENCH/generated: not mine
?? Transient/fw_scenes/live/S1_p14.png   BENCH/generated: not mine
?? Transient/fw_scenes/live/S2_20261017T084824.txt   BENCH/generated: not mine
?? Transient/fw_scenes/live/S2_20261017T092355.txt   BENCH/generated: not mine
?? Transient/fw_scenes/live/S2_20261017T110404.txt   BENCH/generated: not mine
?? Transient/fw_scenes/live/S2_p00.png   BENCH/generated: not mine
?? Transient/fw_scenes/live/S2_p10.png   BENCH/generated: not mine
?? Transient/fw_scenes/live/S2_p30.png   BENCH/generated: not mine
?? Transient/fw_scenes/live/S2_p60.png   BENCH/generated: not mine
?? Transient/fw_scenes/live/S3A_p20.png   BENCH/generated: not mine
?? Transient/fw_scenes/live/S3B_p06.png   BENCH/generated: not mine
?? Transient/fw_scenes/live/S3B_p16.png   BENCH/generated: not mine
... 116 more uncommitted paths (by top-level dir: Transient 115, deployed 1): git status --short
```

