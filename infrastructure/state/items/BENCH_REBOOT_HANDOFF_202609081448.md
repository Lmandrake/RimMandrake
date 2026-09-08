# BENCH_REBOOT_HANDOFF_202609081448 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202609072200`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

🔴 **The canon CSV's `biome` column is the PRE-REBAND world. The current biome of any tile
is `world/ASHKARR_WORLDMAP_tiles.csv` OVERLAID, in order, with these plan JSONs:**
`backside_reband_full.json` → `pf_terminator_plan.json` → `wasteland_reclaim_plan.json` →
`crag_meander_plan.json` → `pf_meander_plan.json` → `graycrags_coldonly_plan.json` →
`fungalforest_dissolve_plan.json` → `straggler_cleanup_plan.json` (all in `world/`).
A reader who measures from the CSV alone gets a world two dozen repaints out of date and
**will be wrong** — that is exactly how FungalForest (425), SeaIce (262) and Lake (10)
"dissolved" in a doc but sat live on the map for days. **Measure LIVE via the bridge, or
reconstruct with the overlays. Never trust the CSV's biome column.** The save is the world;
current is **`WORLDMAP_V23_dense_biomes_2026-09-08.rws`**.

## What the owner should see

He signed off the map ("looks good!") and the maturity website ("looks great!") at wrap, so
V12→V23 and the dashboard rework are approved. Three things still want HIS eye:
1. **`BLUE_PROPANE_RING_RULING_1`** — blue desert & propane now sit in all 12 bearing sectors,
   which their own sheets' anti-bullseye rulings forbid ("never a ring"). My read is it's a
   metric artifact — the bands are lobed, not a clean bullseye, and he approved the backside
   look at V13 — but it is HIS ruling: re-de-circle, or soften the ruling text.
2. **`BIOME_LANDMARK_REFINEMENT_1`** — the V23 landmark passes on the 8 dense biomes are BENCH
   **first-pass drafts** shipped with the flag raised: I guessed the defs and ~26% density per
   biome. They read fine but are not curated to each sheet's flagship (the crags' LIGHTFALL is
   the standard). Each wants his per-sheet eye.
3. **The maturity seed** (`Transient/maturity_seed_proposal.md`, 78 systems) is a PROPOSAL —
   he may adjust rungs before it is written to the registry.

## What is half-done, and where it stops

**The reboot's two jobs, owner's words: "continue the biome work and populate the maturity product."**

### A. Continue the biome work
1. 🔴 **All biome sheets EXCEPT ice/blue/propane still need the golden stat-refresh against V23.**
   The early-session refresh of ~18 sheets (arid_shrubland, desert, deep_desert, forsaken_crags,
   the_greentide, the_contagion, etc.) was **REVERTED at wrap** — it was measured against V12
   (stale after the reband) AND re-added the "MEASURED (V12 canon)" provenance tags the owner
   ruled out. Next action: for each sheet, recompute its stats from the LIVE world (or CSV+8
   overlays), write current numbers as plain fact, strip provenance — exactly the treatment
   `nightside_ice.md`/`the_blue_desert.md`/`the_propane_lakes.md` got (commit 7bbd4b6a is the
   worked example). Only those three are golden so far.
2. **`BIOME_LANDMARK_REFINEMENT_1`** — curate the 8 dense-biome landmark passes per sheet.
3. **`BLUE_PROPANE_RING_RULING_1`** — get the ruling, then act (repaint or amend).
4. Crags + the Rot are the two done-well examples (LIGHTFALL + obsidian teeth; fungal density).

### B. Populate the maturity product
Seed the rimflow capability registry from **`Transient/maturity_seed_proposal.md`** (78 systems,
each row has an exact `rimflow capability set <sys> --function-rung <r> --content-rung <r>
--evidence-ref "…" --date 2026-09-08` line). The command + 6-rung schema (validated/played) are
already built and selftested. After seeding: `python3 src/RimMandrake/Utils/project_maturity_dashboard.py`
renders the live dashboard. ⚠️ Confirm the owner's rung adjustments first, or seed the proposal
as-is if he says go.

**Exact next action on wake:** re-take the bridge WITH a heartbeat plan, confirm the game is
Playing (V23 loaded — it stays up across the agent reboot), then start with the sheet golden-refresh
OR the maturity seed, owner's pick.

## Traps learned

1. 🔴 **The canon CSV lied about biomes** — see "the one thing to carry forward." FungalForest/
   SeaIce/Lake were "dissolved" in docs+a save but persisted live for days. Measure live.
2. **Bridge lock heartbeat is not optional** — driving does NOT refresh the lock (only rimflow
   ledger events do). Emit a `rimflow bridge take --for "…"` note every few minutes while driving,
   or the other window reads it stale. (The 2026-09-08 crash itself was FOUNDRY's cold-load
   tilegen ntdll crash, `BRIDGE_NTDLL_CRASH_TILEGEN_1`, not a lock collision — but the stale lock
   is what let two drivers coexist. Both in LESSONS_INBOX.)
3. **Deserts/wasteland/seas SHOULD read barren** — do not blanket-landmark them; sparse is correct.
   Only dense/dramatic biomes want density.
4. **Bridge tool param names bite:** `jawa/world_landmarks_get` takes `limit`, NOT `range`; the
   world_features objects key the id as **`uniqueID`**, not `featureId` (the client's param guard
   catches the first; the second fails silently returning None). `world_features_set action=assign/
   update/delete` needs that `uniqueID`.
5. **Never re-run the whole-planet `world_mutators_get` harvest as one tight loop** on the full
   modlist — it returned ConnectionReset as the game died under FOUNDRY's concurrent tilegen; use
   targeted tile reads.

## Closed since the last handoff (0)

Nothing closed in this window.

## Filed and still open (10) — the next seat's queue

- `UNDERWATER_BIOME_SUPPORT_1` — Underwater biome support: land on the three seas -- looks like ocean, playable seafloor beneath (owner 2026-09-07, later modification)
- `WORLD_LINT_WATER_HARDCODE_1` — world_lint hard-codes Ocean/SeaIce as the only water biomes -- reports all 1135 custom-sea tiles as landBiomeSubmerged
- `PROJECT_MATURITY_DASHBOARD_1` — Project maturity dashboard: two spines (systems function x content, and the GOAL_SHEET content inventory), rimflow-owned, rendered as an Artifact -- t
- `WORLD_FEATURE_LABELS_OVERSIZED_1` — World feature labels render HUGE and overlap the globe -- our maxDrawSizeInTiles multiplier is 1.63x vanilla's
- `MOD_VALIDATION_PLAN_AUTHORING_1` — Author a per-mod automated validation walk for all 76 mods -- a scripted string of checks exercising most of each mod's behaviour, written NOW while c
- `MOD_HUMAN_EXPLORATION_PASS_1` — Human-executable exploration pass: per mod, a scripted in-game walkthrough the owner runs to confirm it looks and feels right -- runs AFTER the art/no
- `BIOME_LABEL_CAMPAIGN_NAMES_1` — Relabel the 26 donor biomes to their campaign names -- the planet currently shows 'Cypre Jungle', 'Mycotic Jungle', 'GRimond' instead of the Greentide
- `RIMWORLD_MEMORY_FOOTPRINT_AUDIT_1` — Deep-dive: RimWorld 18GB+ memory footprint, crash correlation, worst-offender mods, reduction options
- `BLUE_PROPANE_RING_RULING_1` — Blue desert & propane now occupy all 12 bearing sectors — their 'never a ring' anti-bullseye rulings are contradicted by the paint; re-de-circle or am
- `BIOME_LANDMARK_REFINEMENT_1` — First-pass landmark density on 8 dense biomes (Greentide/Contagion/Webwork/Weeping Stones/Slime/Scarlands/Pyrelands/Cracked Lands) needs per-biome ref

## Commits

```
9609eb9d Sync queue renders + full mod-list capture (599 active) for reboot
ea1ac484 Mark mapgen_paint.py CLEAN
68a09c9a mapgen_paint.py: remove dead _rock_terraces, fix its stale docstring claim
64eb8f3e V23: first-pass landmark density on 8 dense/dramatic biomes
cc18032c Mark 3 more files CLEAN: compose_gl_vs_painter.py, GenStep_ScatterCavePortal.cs, make_complex_structures_icon.py
f658d7a0 Write up BRIDGETOOLS_CSHARP_SWEEP_BUGS_1; mark 3 big C# files CLEAN
0850ef10 V22: the Rot landmark density (891 fungal caverns/cenotes/valleys, 3.6%->42%)
2691a1e3 Context for BLUE_PROPANE_RING_RULING_1
7bbd4b6a Golden canon: strip provenance from the three dark-side sheets
c323e30a V21: clear SeaIce+Lake stragglers (272 tiles) - planet clean of vanilla water leftovers
edd54728 V20: dissolve leftover FungalForest (425 tiles), straighten ancient roads
aa15a74c Mark 6 ashkarr_*.py world-authoring scripts CLEAN
f020cfc6 Mark 3 more bridgetools C# files CLEAN (standing code-review loop)
2aeb5193 Maturity dashboard rework: 6-rung function ladder (validated/played), progress-bar rungs, compressed, legend split
435b69dc Mark 4 more bridgetools files CLEAN (standing code-review loop)
2174503f V19: rename 4 nightside labels to match rebanded terrain
51e7846d Mark 5 more Utils files CLEAN (standing code-review loop)
e3212aae Refresh ice/blue-desert/propane sheet stats to V18 canon (frozen amendment)
29101eae Write up DROIDWORKS_FULL_LIST_COEXIST_1 findings; sync ledger
a35e4f62 DROIDWORKS_FULL_LIST_COEXIST_1: fix def-authoring errors surfaced by first full-list load
9e901b86 Re-center Twilight Crags label onto its crag body (tile 17537)
c69177b8 V18: merge Level into Knuckles (one polar region), re-center label
c66f9f47 V17: Gray Crags->crags (cold biomes), LIGHTFALL enlarged 7->15 tiles; save TRUE-GLORIOUS-RING config
328b4b65 Fix rimflow sweep --transient: one git log call, not one per file
97794051 Mark handoff.py + selftest_handoff.py CLEAN
b9a1d9a2 Fix handoff.py: a prior block/close no longer hides a later restart
c4ce219a Deploy war-debris ring texture; ringMapPath -> Ring/ring_debris
37c96a19 Correct the crash note: FOUNDRY tilegen ntdll crash, not my mutator call or a lock collision
0c9f0618 LESSON: repeated the stale-bridge-lock trap; heartbeat is not optional
738795eb FOUNDRY reboot handoff 202609081318
859f4533 V16: Crags sheet applied to map - LIGHTFALL chasm + obsidian-teeth landmarks; PF stripe meandered; ring altitude fix
2fc434a8 File NINEFOLD_GRAVSHIP_HOOK_SCOPE_1: owner decision fork on gravship hook scope
09041ee2 BRIDGE_NTDLL_CRASH_TILEGEN_1: close, root cause + bug-separation done
2038f864 DROID_ORACLE_VOICE_DESIGN_1: four droid Oracle consumers, dormant (design for owner review)
f8c40667 CODE_REVIEW_STATUS.json: record Oracle mod fully clean (7/7 files)
06da6f34 Oracle About.xml: flag the stale OpenAI-HTTP transport description
547d1c2b DEV_LOG_AUTOOPEN_SUPPRESS_1: close out the live testerror verify
3537473e Atmosphere ring fix: set ringMapPath to the Saturn-banding texture
b65f3cd0 ANCIENT_WAR_LAB_1: consolidated build spec + criteria; split off WAR_LAB_CRATER_HOOK_1
e67982b0 V15: wasteland reclaimed from shadow, crag stripe meandered (owner rulings)
c195170c V14: Poison Forest confined to terminator, regrown as groves (owner ruling)
5fa1c5d7 Backside temperature-band reband (V13): crags>ice>blue>propane, anti-bullseye
d712072d FOUNDRY reboot handoff 202609080546
fd42abf0 Wave note: close this session's ashkarr_* code-review sweep
b8ec4d2a ashkarr_settle.py: document the fifth stale item (BARREN_REGIONS article mismatch)
7d0a56cf File W9_RUN_STAGE_RESULTS_UNCHECKED_1; mark w9_run.py clean
9cf1c2ed w9_run.py: always write the report, and fix a stale comment
5fd66fbb ashkarr_shore_zonation.py: add missing warn_if_stale() guard
4bba5f26 ashkarr_shore_and_ice.py: refuse --apply, it would repaint 503+ live sea tiles
07e9ab0e Record wave note; mark ashkarr_paint.py, selftest_codebase_health.py clean
9698e721 Fix two real bugs in verify_frozen.py found by code review
5f75d12d ashkarr_nightside_pass.py: refuse --apply now that HorrorWastes is dissolved
7bedead6 File ASHKARR_NIGHTSIDE_LAYER_SUPERSEDED_1 and ASHKARR_REGATE_RAIN_DEAD_1
279e2e00 Fix stale --show cross example in harvest_log.py's own header
2861b94d ashkarr_layer_nightside.py: refuse --apply now that both carve targets are dead
09ce5b8f Close CORRECT_ASHKARR_IDEOLOGY_1 at 22e91195
22e91195 V12: twelve faction ideoligions live via faction_ideo_set; meander ruling measured already satisfied
7d70dfae Record codex_image.py clean mark and wave note
f8f51187 Fix two real bugs in codex_image.py found by code review
a1653e02 File RAIN_BAN_SCOPE_DRIFTED_1; mark ashkarr_dry_jungle.py clean
4e707a01 ashkarr_dry_jungle.py: add staleness guard and a real world-drift refusal
a181ce51 Mark ashkarr_fix_impassable.py and ashkarr_clamp_rain.py clean
9d53fe45 Fix unhonoured owner decisions in gen_pawn_flavor_phase2_apply.py
5932b583 Fix two real bugs in codebase_health.py found by code review
7c295d7d Fix single-capture PAWNKINDS/ANIMALPKG undercount in gen_cast_patch.py
ed29e8c3 WORLDMAP V11: place 136 ComplexStructures landmarks, verify propane texture
7e861e9c Record first_light.py clean mark and gen_cast_patch.py fix status
8f031a0b Fix doubled jawa/world_info_get bridge call in first_light.py
7c25926e Wave: biome_flora.py + chroma_key.py clean, roster gap filed, lesson logged
a0e9f2d6 Fix two real bugs in validate_sprite.py found by code review
56b17db2 Mark plant_harvest_coverage.py clean
a0728d4b WORLDMAP_BIOME_ICONS_REGEN_1: MEASURED - icons never wired to plant/animal roster
e373ce75 RIMWORLD_MEMORY_FOOTPRINT_AUDIT_1: record disk-side legwork findings
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-09-08T14:48:41Z

Uncommitted (say for each whether it is yours or another seat's):

```
M infrastructure/state/codebase_health_last.json
 M infrastructure/state/items/IKEE_MYNOCK_ART_REGEN_1.md
 M infrastructure/state/ledger/events.jsonl
 M infrastructure/state/queue/BENCH.md
 M infrastructure/state/queue/FOUNDRY.md
 M src/RimStarWars/BeastLairs/About/About.xml
 M src/RimStarWars/BeastLairs/Defs/ThingDefs_Buildings/RSW_BeastLairs_Buildings.xml
?? "D:\\Luke\\dev\\Rimworld\\Transient\\bench_tools_dump.json"
?? claude_sha.txt
?? design/Jawa/art/gods/busts/.gitignore
?? "design/Jawa/worldbuilding/lua suggestions/"
?? design/Jawa/worldbuilding/review/creature_art/
?? design/Jawa/worldbuilding/review/creature_register.fiftyone_export.json
?? design/Jawa/worldbuilding/review/deck/creature_deck.pptx
?? design/Jawa/worldbuilding/review/deck/creature_deck_manifest.json
?? design/Jawa/worldbuilding/review/furniture_art/
?? infrastructure/state/CODE_REVIEW_STATUS.json.lock
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260902_181509.xml
?? infrastructure/state/codebase_health_last.json.lock
?? infrastructure/state/facts/mlie_creature_defname_map_wave_a.json
?? infrastructure/state/items/FOUNDRY_REBOOT_HANDOFF_202609081447.md
?? infrastructure/state/modlists/ModsConfig.FULL.PRECAPTURE.20260907_215737.xml
?? research/RimMandrake/inspiration/map_injection_2026-09-06/p2_createprefab_export.xml
?? src/RimMandrake/LoadTracer/Assemblies/
?? world/_lightfall_read.py
?? world/_load16.py
?? world/_poll16.py
?? world/_ready_ring.py
?? world/_roads/meander_v12/_tools_world.json
?? world/_roads/meander_v12/ancient_edges.json
?? world/_roads/meander_v12/harvest.py
?? world/_roads/meander_v12/landmarks_before.json
?? world/_roads/meander_v12/objects_before.json
?? world/_roads/meander_v12/probe.py
?? world/_roads/meander_v12/probe2.py
?? world/_roads/meander_v12/rerouted_v12.json
?? world/_roads/meander_v12/roads_import.csv
?? world/_roads/meander_v12/world_info.json
?? world/_settle_shot.py
?? world/_shot_globe.py
?? world/_shot_lightfall.py
?? world/graycrags_to_crags_plan.json
```

