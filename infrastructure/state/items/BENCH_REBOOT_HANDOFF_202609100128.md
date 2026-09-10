# BENCH_REBOOT_HANDOFF_202609100128 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202609091702`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

A fixed finding is not a clean file, and the loop proves it: twelve whole-file
adversarial waves on `code_review_status.py` (now CLEAN) and five on `artpipe/`
each found real defects that the PREVIOUS wave's fixes introduced or exposed —
my own wave-4 fix made a branch unreachable, the wave-5 prune extension lied
"dropped" while removing nothing. Never mark-clean on "findings fixed"; re-review
whole, fresh-eyes, until a pass demonstrates nothing. The converging finding
count (8→7→4→2→3→2→1→2→0) is what convergence actually looks like.

## What the owner should see

- **The two verdict sittings are live and UNTOUCHED** (artifact db empty as of
  wrap). Fauna: https://claude.ai/code/artifact/db81dd60-d603-43e4-ae6c-fe2156411385
  Flora: https://claude.ai/code/artifact/c17f933f-e912-4684-aa5a-95e9eeed2131
  The whole art pipeline's queue waits on these verdicts.
- **The channel call**: contrast sheet at
  `D:\Luke\dev\Rimworld\Transient\gemini_contrast_2026-09-09\CONTRAST_sheet.png`
  (also sent to his phone). Gemini image-conditioned 8/8 validator pass vs
  Codex 0/32; ~$0.134/img worst case. His approval makes Gemini the scale
  channel and kills the ChatGPT plan-upgrade question ($100/$200 Pro tiers
  researched, Codex credits ruled out as unbounded).
- **Hestia's Certanum ingestion carries 10 confirmed content defects**
  (deliberately NOT touched — another window's knowledge base): a
  compliance-sensitive Summary now contradicts the Advisory-only posture;
  Marcus's sector-sequencing proposal is recorded as a finalized decision
  ahead of the 09-11 meeting; six raw email bodies sit untracked OUTSIDE
  git-crypt coverage in that repo (one broad git add there would push
  plaintext). Awaiting his word on who fixes.
- **~30 queued Windows UAC prompts** are safe to decline wholesale (setup
  requests for deleted calibration worker homes; told him, may be done).
- **Dialexis ultra review still owed**: unreachable — G: (Google Drive) is not
  mounted and no local copy exists; needs Drive started or a path from him.

## What is half-done, and where it stops

<!-- Anything left mid-flight, and the exact next action. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and the exact next action,
     or close/block it. --check refuses while any is unaccounted
     for, so deleting a line here is not a way past it. -->
- `ART_PIPELINE_DAEMON_1` — daemon BUILT and hardened through five fresh review
  waves (last fixes `16192667`; selftests 327 assertions/83 fns; both channels:
  codex leased-pool + detector, gemini budget/intent-journal/quota-backoff).
  It stops exactly here, in order:
  1. **Sixth fresh review** — wave 5's fixes are themselves unreviewed; loop
     until a zero pass, then `mark-clean` every `src/RimMandrake/Utils/artpipe/`
     file (none is CLEAN yet).
  2. **Queue fill** — after the owner's verdicts: dump the artifact db
     (`Artifact read_db` with `out_dir`), merge via
     `/mnt/d/Luke/dev/review-sheets/assets/merge_artifact_db.py` (report first,
     `--apply` second; REFUSES an empty dump by design), run the sheets'
     applier, then `fill_queue.py` from the resulting art list.
  3. **Projection** — backlog count × MEASURED 0.19%/img (Codex) and $0.134/img
     (Gemini) → the reskin calendar he asked for.
  4. 🔴 **Gate**: `CODEX_UAC_STORM_1` must be resolved and the first live daemon
     run SUPERVISED before any unattended operation — the daemon must be
     UAC-silent and its first real spend watched against `throughput.jsonl`.

## Traps learned

All filed to LESSONS_INBOX.md or fixed-with-guards; the four that bit hardest:
- **FOUNDRY's stash dance dropped two waves of other agents' uncommitted work**
  (696-line review-status wave + 13 fuel-src files); both recovered from
  dangling stash commits via `git fsck --unreachable`. Never stash over foreign
  dirty state; after any pop, diff the tree against what was stashed.
- **Edit calls can report success while the file keeps its old content** on
  /mnt/d (drvfs) — a subagent caught it only by re-grepping its own markers.
  After a heavy edit wave, grep for what you claim to have written.
- **`os.path.isfile` False means ignorance, not absence** (EACCES/EIO/drvfs
  stale read) — it nearly let `prune` permanently destroy valid clean entries.
  The `proven_gone` stat-errno pattern is now the repo's discipline.
- **`$?` after a pipe reads the pipe's LAST command** — two of my own probe
  loops silently tested `tail`'s exit code; assert exit codes without pipes.

## Closed since the last handoff (3)

- `GRAPHICS_GEMINI_BILLING_DECISION_1` — e97591ce3b28f68048c42b8bd6eb49bf040a9625
- `DUMPDB_MANIFEST_SHORTFALL_1` — d09744bd63138b59bdc718c934461fade6a3cff9
- `GEMINI_WORKER_BACKEND_1` — 477dfb06f3761403de9604661cd1dec4c95668aa

## Filed and still open (3) — the next seat's queue

- `DROIDWORKS_PERSONALITY_VERIFY_1` — Live-verify chassis personality bias: 20 spawns per family show the forced traits + protocol pedantry
- `ART_PIPELINE_DAEMON_1` — Constant background art pipeline: dumb daemon + N codex exec receiving-agent workers, seats fill the queue
- `CODEX_UAC_STORM_1` — ~30 UAC prompts queued by calibration's fresh codex homes DESPITE a valid .codex_sandbox_seed template — root-cause the template bypass (codex version

## Commits

```
16192667 artpipe: fifth review fixes — gemini budget/billing edge cases (7e874fdd)
d4a7c902 Ledger sync: flush pending events ahead of reboot
dc933df1 INHABITED_AUGMENTATION_BUILD_1: build structure_procedural_spec §8.14 (storage cache)
f0db7609 DROID_ORACLE_VOICE_DESIGN_1: reconcile the four droid consumers against the built claude -p client
a0af9567 TILEGEN_SILENT_REUSE_1: closed-source SDK/transport layers read directly, no root cause found
24dedc40 Lesson: throwaway codex homes queue UAC prompts despite the seed template
65fef933 Ledger: CODEX_UAC_STORM_1 filed (calibration's throwaway homes queued ~30 UAC prompts past the seed template)
5cd78cb9 PLANETARY_BEAUTY_LOADSCREENS_1: mechanism identified, two beauty-shot candidates
fc43a426 SHIELD_MODS_LEVERAGE_1: bespoke building-scale shield generator v1 slice
b9520e45 INHABITED_STOCK_ONTO_MAP_AND_FATE_1: reachability gaps confirmed closed, fate live-check still owed
d810ddb9 Ledger sync: CODEX_EDIT_TIMEOUT_1 close + bridge release + concurrent FOUNDRY note
6b62f3de PLOT_MECHANISM_MODS_WAVE_1: wire Aftermath rule 6 (Zizzik's aftermath) trigger
5d58e484 CODEX_EDIT_TIMEOUT_1: root-cause the 3/3 edit-mode timeouts, fix orphan leak
bb95160c PITCELL_PRISONER_BED_BRIDGE_GAP_1: live-proof attempt crashed the game before the tool could be called
7e874fdd ART_PIPELINE_DAEMON_1: fix fourth review's 4 findings + 2 lower notes
dfb22d9a DOORSEXPANDED_SAVE_COMPAT_REGRESSION_1: scope root cause (metadata gate, not placed doors)
9001d4bd Ledger sync: WORLD_FEATURE_LABELS_OVERSIZED_1 closed
2fbb7973 WORLD_FEATURE_LABELS_OVERSIZED_1: visual verify -- labels read fine, closing
b12222a7 Ledger sync: flush pending close/note events
bff84af8 SELFTEST_RENDER_FLAKE_1: decouple render bench()'s wall-clock budget from selftest correctness
b7e7d6af DROID_DONOR_SAVE_COMPAT_REGRESSION_1: root-cause found — Asimov Need_Energy on 78 non-droid pawns, not placed droid content
ea283906 SYSTEM_TOOLS_SELFTEST_1: guard ctypes.windll behind a Windows check
05d846f7 MODLIST_RESTORE_AND_BATCH_DEPLOY_1: campaign restored and LOADED on 581; ManyWaters excluded, its blocker filed
de58a58f ART_PIPELINE_DAEMON_1: fix third review's 7 findings + 4 lower notes
0791bc3d code_review_status.py marked CLEAN after 12 adversarial waves; 181 dead entries pruned
a3b2ffc2 Rerun codebase health visualization
85b206bd code_review_status: eleventh review wave — phantom reason wins, NUL-safe census
6fac2cd1 Add system_screenshot.py/system_click.py: OS-level desktop capture and click tools
2005115a code_review_status: tenth review wave — reopen refuses on canonicalization ignorance
e626969c Ledger: GEMINI_WORKER_BACKEND_1 closed at 477dfb06
477dfb06 ART_PIPELINE_DAEMON_1: fix fresh review's 9 findings; add GEMINI_WORKER_BACKEND_1
ae1cfa3c Ledger: DUMPDB_MANIFEST_SHORTFALL_1 reassigned to BENCH and closed
d09744bd Ledger: DUMPDB_MANIFEST_SHORTFALL_1 closed (rebuild + full_name split, both live cases pass)
f5637051 code_review_status: ninth review wave — check's last ignorance-as-absence, precheck traceback
e3aff63c code_review_status: eighth review wave — prune never drops on ignorance
9224996a Ledger: DUMPDB_MANIFEST_SHORTFALL_1 root-caused, live db rebuilt; GEMINI_WORKER_BACKEND_1 to BENCH
a0dca2d9 code_review_status: seventh review wave — decode degradation, check/list agree on dirs
2e70b29b gitignore artpipe worker codex-homes: they seed auth.json (public repo)
4f550f29 MODLIST_RESTORE_AND_BATCH_DEPLOY_1: full-list cold load was failing on STALE DEPLOYED DLLs, not the mod list
be65992d Ledger: Gemini billing decision closed on contrast proof; GEMINI_WORKER_BACKEND_1 filed
e97591ce Gemini image-conditioned contrast batch for ART_PIPELINE_DAEMON_1
3ef38055 Owner ruling: art route = Gemini billing + Codex edit-mode debug in parallel
4d3f22b5 Codex calibration: linear to N=4 (95 img/h), native alpha YES, ~526 img/week ceiling at $20; edit mode dead 3/3
53e7097b Ledger sync: artpipe state note; SELFTEST_RENDER_FLAKE_1 + DUMPDB_MANIFEST_SHORTFALL_1 filed
25dd46e6 File MODLIST_RESTORE_AND_BATCH_DEPLOY_1: the campaign has been abandoned at a 6-mod vanilla menu for 80+ minutes
0705b62f STAT_NORM_WAVE1_RETIRE_1: checks pass, execution blocked on a vanilla-only modlist
cf488dd8 ART_PIPELINE_DAEMON_1: fix all 10 ultra-review findings plus below-cap notes
13584e06 NINEFOLD_ENGINE_M0_1: wire 7/9 first-contact chains on owner's own provisional-text authority
86d55a3e MAPGEN_PAINTER_V1_1 round 3: point hydrology was stamped inside its own rock, not just too small
8f4bdbef STAT_NORM_WAVE1_RETIRE_1: fresh dependency + save re-checks, all 13 pass
2b62fc0b code_review_status: sixth review wave — prune --apply actually drops phantoms
e6d79ac2 code_review_status: fifth review wave — drvfs case-rename phantoms killed
99839340 ART_PIPELINE_DAEMON_1: art-pipeline daemon, worker contract, and mock-driven selftest
4dedcfba selftest: enforce the one hook-log path across both writers
5a70ad9e File STAT_NORM_WAVE1_RETIRE_1: execute Wave 1 of the stat-normalization mod audit (owner go-ahead)
8cd6d041 rimflow: note MLIE_FAUNA_ABSORPTION_1 Wave B pass
a68df824 code_review_status: fourth review wave — literal pathspecs, honest unreadable answer
d75b0609 MLIE_FAUNA_ABSORPTION_1: Wave B (Dewback/Vulptex/Porg/Nuna/Wampa/Acklay), Wave A wiring fix, license verified
62e60697 Fleet: add the Artist window (purple, top-right above EMERGENCY)
fe9bf2c2 code_review_status: third review wave — quoted paths, sandbox escape, honest list reasons
93917385 File ART_PIPELINE_DAEMON_1: constant background art pipeline (owner directive), replaces CODEX_PARALLEL_WORKERS_1
bad5c469 rimflow: note on STAT_NORMALIZATION_AUDIT_1 (census delivered, stays doing)
f1485451 STAT_NORMALIZATION_AUDIT_1: full-stack stat-conflict census + 4 waves (plan only)
a45e4cd0 code_review_status: second review wave — 7 more findings fixed
233503ae gen_flora_distribution_portfolio: DEFDB via game_paths, not a LocalLow literal
8aecef33 code_review_status: fix wave from the adversarial full-file review
6c9287cb STAT_NORMALIZATION_AUDIT_1: record owner rulings (widen scope, split cosmetic/content-adding buckets) and the temp-minimal-modlist hazard
aea71526 ANCIENT_WAR_LAB_1: three-band KCSG dungeon authored offline (approach/lab interior/core)
05f67a48 LANTERN_DEEPS_INJECTION_1: crystal-fauna eviction patch, kyber verified inherited
5579e3db File STAT_NORMALIZATION_AUDIT_1: census third-party fauna/flora balance mods before the owned-content normalization pass
c7b8515d rimflow close W9_RUN_STAGE_RESULTS_UNCHECKED_1: fix already landed, ledger wasn't updated
9f0dd897 NINEFOLD_FIRE_HOOK_RATELIMITED_1: offline re-verify, rate-limit logic confirmed correct
a18db8d4 SETTLEMENT_VERBS_WAVE_1: offline re-verify after Sprint wave A merge, still doing
4a0fc3a2 LIVESTOCK_STARTER_TRIO_1: onnik built and offline-verified, karrask Mass fix
bf669503 File DROID_DONOR_SAVE_COMPAT_REGRESSION_1: droid donor retirement broke the canonical save load
3020dd6a VAULT_THAW_QUEST_FAMILY_1: re-verified offline, no rebuild, left doing
7982a712 Revert DROID_RETIRE_DEPOT_ASIMOV_1: restore MSEDroidFix + related patches
e696e277 BUILDING_THEFT_HAULER_1: re-verify offline after RimProperty merge, Droidworks now live
dabe8418 BIOME_ENRICHMENT_POISON_FOREST_1: doorsexpanded fixed, but 3 more mods missing on retry
f90feb8b SETTLEMENT_VISIT_LOOP_1: offline re-verify after sibling-item fixes, still doing
03d45d31 Ledger sync: HELIX_TELLUROX_BUILD_1 offline re-verification note
bfb1f47f HELIX_TELLUROX_BUILD_1: offline re-verification, no rebuild needed
5edacb13 DROID_REPAIR_FOR_PROFIT_EVENTS_1: re-verify offline, record ModsConfig drop
4a9dc230 VAULT_DUNGEON_BUILD_1: author V5's landmark offline, fix stale item-file path
4b7a16a1 File DOORSEXPANDED_SAVE_COMPAT_REGRESSION_1: donor retirement broke the canonical save load
26f2387d BIOME_ENRICHMENT_POISON_FOREST_1: real defNames confirmed + verified plan; blocked by a live crash, not content
aa2bcc91 Closes: DROID_HUTT_CAPTIVES_1
41c5c7f3 DROID_HUTT_CAPTIVES_1: re-verify offline on current main, close
c54d9d14 Ledger sync: DROID_FDE_GOODWILL_CAP_1 verify+close, plus queued prior writes
61789b97 DROID_FDE_GOODWILL_CAP_1: re-verify offline, close
169574cb SANDWORM_MYTHOS_BUILD_1: re-verify and close the Long Hunger (v1)
cd50911a PITCELL_PRISONER_BED_BRIDGE_GAP_1: write item file, confirm still blocked on live proof
cdb773ab MACRO_GENERATOR_V0_1: re-verify pipeline end-to-end (offline), leave doing pending owner grade
ce04b993 JAWA_PATCHES_SPLIT_1: re-verify, 0 files remain (tombstone confirmed)
63d09a03 DROIDWORKS_FORMAT_TIERS_1: independently re-confirm root cause, offline verify clean
78cf5b09 FLUID_CANAL_MECHANIC_1: rework reservoir to drip+re-flood per owner ruling
70c4af42 rimflow ledger sync: TILE_STRUCTURE_DESIGNS_1 note + queue re-render
f6116f97 DROID_RETIRE_DEPOT_ASIMOV_1 (wave R3): retire Droid Depot + Asimov + MSEDroidFix
e528a153 TILE_STRUCTURE_DESIGNS_1: coverage lint built, precise 16/22 promise state
10b0a793 rimflow: close DISTRICT_TEMPLATE_LIBRARY_1
a0816bec DISTRICT_TEMPLATE_LIBRARY_1: fix real aisle-blocked bug in junkers_dwelling_cluster, close v1
2423eac8 DROID_RETIRE_ABF_SYNCORE_1: blocked on Site 1's ParentName chain, no mod-list change made
355ab188 LANDMARK_NAMING_PASS_1: confirmed tool+names already built, checked namer-variety route
79b599d8 SEA_ENRICHMENT_LANDMARKS_1: verified plan, measured fresh, game went down before any write
b9344a89 Closes: BIOMESKIT_RENDER_LAYER_MISSING_1
dace71e0 BIOMESKIT_RENDER_LAYER_MISSING_1: worldmap decoration icons traced to ReGrowthCore, non-issue
cbc6f8f1 Lesson: a gate needing an unloaded mod is a load round, not a quicktest
2847f418 rimflow ledger sync: MOVING_DUNES_BUILD_1 note + pending queue events
11115218 MOVING_DUNES_BUILD_1: the dunes engine — Werner transport on Odyssey's sandGrid
781732a6 Ledger sync: GRAFFITI_FRAMEWORK_BUILD_1 close event
4f3b67a3 GRAFFITI_FRAMEWORK_BUILD_1: reconcile against R7/R8, close
663465cf BIOME_ENRICHMENT_DESERT_WASTELAND_1: measured, left doing — no concrete kit
865cd609 FUNGALFOREST_RAID_MERGE_1 offline half: ingest the spore kit, discover the merge already painted
d9b909c8 ORACLE_CLIENT_CLAUDE_CODE_REWRITE_1: re-verify claude -p transport, rebuild clean, live verify owed
d85c26c2 BRIDGETOOLS_DLL_GM_DRIFT_1: rebuild companion with --gm, confirm 41-tool gap closed (plan-only, no deploy)
58abbd44 MANYWATERS_COLOR_SUPPORT_1: record the mod-activation blocker found live
49195cc4 Ledger sync: flush pending close/note events (BELT fanout wave)
b2ebdfdb Fix Pyrelands doc naming drift: RSW_FE_ -> RM_FE_
d672d781 rimflow: close WORLD_BOUNDARY_LAND_AT_SEA_ELEVATION_1
ec8e4670 WORLD_BOUNDARY_LAND_AT_SEA_ELEVATION_1: fix 181 landBiomeSubmerged tiles, real defect confirmed live
448e87d7 MANYWATERS_COLOR_SUPPORT_1: v1 coloured water/slime offline slice, live step owed
620bc909 DESERT_WRAPS_ART_COMMISSION_1: candidate contact sheet (4 wrap styles, 2 head shapes)
31df09de WORLD_FEATURE_LABELS_OVERSIZED_1: reconcile the duplicate maxDrawSizeInTiles formula
f23f11cd INHABITED_INJECTIONS_DECOUPLE_1: Inhabited decoupled from StructureInjections via reflection
5854de5b Lesson: stash pop over foreign dirty state dropped two waves; fsck recovered both
4e560f01 Ultra review fixes: verify gates restored, art candidates archived, hook log out of the repo
669b30d4 Ledger sync: STARWARS_DONOR_SUNSET_1 close note
a54d8b0d Ledger sync: STARWARS_DONOR_SUNSET_1 closed
c16fd4f0 STARWARS_DONOR_SUNSET_1 wave 4: retire lumi.doorsexpanded
0d234e12 GRAFFITI_PUNK_IDEOLIGION_SCOPE_1: item spec/verify/criteria + owner questions; fix design doc's stale premise
e672bdc4 Law-1 sweep resolved: Inhabited confirmed, SacredGraffiti false positive
02201563 Restore 116-entry mark-clean wave lost in FOUNDRY's stash dance
0b505f1c Ledger sync: WORLDMAP_DESERT_BAND_REPAIR_1 close + note
d2f0e37d WORLDMAP_DESERT_BAND_REPAIR_1: retype bands A and D, band C left for the owner
c1acd765 Owner rulings via question cards: doorsexpanded port-then-retire, Chronicle spine-kind nod, ManyWaters skip-gate-test + bottled-water scope, Horrors gating confirmed/hold-whole-item; file Pyrelands doc-drift fix
b466539b Ledger sync: PYRELANDS_SELF_CONTAINED_BIOME_1 note+close events
14c9a03d Ledger sync: NAMESPACE_RETIER_PASS_1 closed
c614c1da Block KOTOR_CRYSTAL_GENSTEP_DRIFT_1: not a repo bug, donor MayRequire gate
89ca638a NAMESPACE_RETIER_PASS_1: re-tier two C# namespaces to the nested grammar
01687ccb PYRELANDS_SELF_CONTAINED_BIOME_1: record verify criteria and close on authoring
c8b4ad38 Block ASHKARR_FLORA_SWEETLINE_ART_UNWIRED_1: duplicate of tracked owner art-pick
e5c3bc33 global: Fetcher is usually fast — check back in ~1 min, don't park it as a long background job
ad32ca63 FOUNDRY handoff: BELT wave complete, offline queue exhausted
a6a74c7a Droid service-record drift (E2): idiosyncrasies accrete unwiped, wipe erases them
a64a1022 Droidworks chassis personality (E1): per-family forced traits + protocol pedantry
```

## Game / bridge / tree state at wrap

- running   : NOT RUNNING   (tasklist.exe lists no RimWorldWin64)
- recorded  : DOWN
- Bridge: FREE    since 2026-09-10T01:02:42Z

Uncommitted (ownership): the three mod DLLs, `StructureInjectionsRUT/Source/Defs/`
and the `modlists/*.xml` snapshot are FOUNDRY's live work — leave them. The
`codebase_health*` files are hook churn. `events.jsonl` + the two queue renders
are synced in this handoff's own commit.

```
M Transient/codebase_health.html
 M Transient/codebase_health.json
 M Transient/codebase_health_artifact.html
 M infrastructure/state/codebase_health_last.json
 M infrastructure/state/ledger/events.jsonl
 M infrastructure/state/queue/BENCH.md
 M infrastructure/state/queue/FOUNDRY.md
 M src/RimMandrake/Graffiti/Assemblies/RimMandrakeGraffiti.dll
 M src/RimMandrake/Inhabited/Assemblies/Inhabited.dll
 M src/RimMandrake/SacredGraffiti/Assemblies/SacredGraffiti.dll
?? infrastructure/state/modlists/ModsConfig_before_doorsexpanded_fix_2026-09-09.xml
?? src/RimUtinni/StructureInjectionsRUT/Source/Defs/
```

