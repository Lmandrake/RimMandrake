# FOUNDRY_HANDOFF_202610190749 — READ FIRST on wake

Follows `FOUNDRY_HANDOFF_202610190435`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

The world save itself is damaged, not just the art: 1,903 tiles (RUT_ForsakenCrags 1135, RUT_PoisonForest 546, ZBiome_Grasslands 222) fell back to TemperateForest on load because the save still held three renamed biome hashes, and the new placeholder world-map textures make the rest look mountainous (hilliness is byte-identical to 09-12). Filed for BENCH as WORLDMAP_REPAIR_LOST_BIOMES_ROCKY_TEXTURES (owner relays it).

## What the owner should see

- Owner kept Alpha Memes and Vanilla Genetics Expanded on the list (cards 2026-10-19); retired from src/ tonight: Alpha Genes, VFE Insectoids 2, ReGrowth, Isopoda, GrimTerra, Horrors, Cockroach (XML and C# refs outside FlowWorks are zero; only vanilla Wall path 'aoba' row remains, vanilla art).
- Owner picked NO PRECIPITATION AT ALL for the Sump (against my recommendation): tar rain deleted, acceptances A1-A5 of SUMP_TAR_LIVING_SYSTEMS_1 voided.
- Contagion: I invented heat kind overhead, heatOffsetC 10 and sunExposureFactor 0.2 for the Bloom; item marked for his review (0.2 or 0?).
- 149 finished renders blocked on his KEPT pictures; he chose to protect keeps. Hourly timer rm-donor-regen-install installs the rest and pushes (dies on WSL restart).
- Three scratch clones (26 GB) deleted after a check; rebase_clone had broken refs so its contents could not be inspected.
- The four biomes he meant: Pyrelands, Leaning Scrub, Cauldron, Contagion (not the terminal four): north-star bars for Leaning Scrub, Cauldron, Contagion are his to sign off.

## What is half-done, and where it stops

- `WORLDMAP_REPAIR_LOST_BIOMES_ROCKY_TEXTURES` — filed for BENCH, not started; NEXT: BENCH repoints the three hash groups live (confirm RM_ vs RUT_ twin first) and flattens the rocky world-map textures via Transient/biome_worldtex_2026-10-18/gen.py.
- `DONOR_FOUR_RETIRE_JUST_GET_IT_DONE` — src refs zero outside FlowWorks, texture gaps closed (36baf80a8), nothing deployed; NEXT: deploy (deploy_custom_mods.py --apply and --compose biomes --apply; plan in design/RimMandrake/donor_save_residue_2026-10-19.md), restart on the 542 list, run harvest_donor_free.py expecting texOurs 0 and xref 0.
- `FLOWWORKS_AB_FINDMOD_DELETE_LAST_HOLDOUT` — last Alpha Biomes FindMod in FlowWorks/Patches/Machinery/RM_PipeNetAdapters.xml fails selftest_retired_mods; NEXT: Bench deletes that block.
- `DONOR_COATS_REDRAW_SIX_HUNDRED_TO_GO` — hourly install timer live, feeder timer live, ~330 dregen jobs plus 227 SWBestiary jobs queued; NEXT: re-arm rm-donor-regen-feeder.timer and rm-donor-regen-install.timer if WSL restarted (systemctl --user list-timers).
- `JAWABENCH_BRIDGETOOLS_DLL_REBUILD_OWED` — donor-name strings in the companion DLL source edited, DLL not rebuilt (build.py needs game down); NEXT: rebuild at the next game-down window via rimbridge-companion skill.
- `CONTAGION_HEAT_JUDGE_SUN_KIND_UNSAID` / `SCRUB_SETTINGS_WIRE_MASTER_CANNOT_GREY` — built, live rows owed; NEXT: run each item's owed rows on the next bridge sitting and ask him about the Bloom 0.2.
- `SUMP_TAR_LIVING_SYSTEMS_1` — rain removed, A6 live chain still owed; NEXT: run the living-map chain on the next load.
- `PYRELANDS_LEANINGSCRUB_CAULDRON_CONTAGION_NORTHSTAR` — readiness report design/RimMandrake/four_biomes_readiness_2026-10-19.md, deploy owed; NEXT: after deploy run each biome's owed live rows from the run-sheet in that report.
- `MODSET_BUILDER_RETIRED_MODS` — insectoid2 removed from tiers, plant_tolerances.py filter untested; NEXT: run plant_tolerances.py once defs.sqlite exists and confirm it removes only donor rows.
- `DONOR_TAIL_MODS_DECIDE_STAY_OR_GO` — owner decided: Alpha Memes and VGE stay; NEXT: none (close it).

## Traps learned

- The artpipe slowdown guard compared 80-210 s renders to a 62 s baseline and ratcheted N 5 to 1 one-way; baseline now 140 s in artpiped.py (filed: LESSONS).
- A commit of an art-ledger shard before the PNGs it records are staged is refused at push by ART_VERSION_WRANGLING_1; stage the Textures with the ledger (filed: LESSONS).
- A save written through a renamed biome defName loads the tiles as TemperateForest and the game re-saves that: compare tileBiome grids by hash after any biome rename (see: design/RimMandrake/four_biomes_readiness_2026-10-19.md and WORLDMAP_REPAIR_LOST_BIOMES_ROCKY_TEXTURES).
- `donor_retire_census` labels vanilla Core paths served by a retired mod as DONOR (the Aoba Wall row); check the path is not Core before porting (see: tail_mods_art_retirement_2026-10-18.md).
- Agent commits sweep other agents' uncommitted edits when they share a file (three tolerance/yield files in c5731f724); give concurrent agents disjoint files (filed: LESSONS).

## Commits

```
658730864 code review: mark 4 LeaningScrub/Contagion/Cauldron files clean after full review
cd048f60d Contagion validation: add draftprint/helix settings to defaults, round-trip rows and reset
e8a7b5a0a LeaningScrub settings: sweetline stations and Lean master switches grey their dependents
0306439a1 ledger: SUSPENSION_LIVE_DIAGNOSE_FIRST_REAL_RUN note (three oddities classified)
288209c54 FlowWorks live pass 2 runbook: changed rows only (B4 covers, hose realflow, suspension proof)
a61f35722 review wave 7: 3 reopened files clean; stale selftests fixed; settings_audit check (3) sees Source/<Sub> DLLs
85a4a1351 FlowWorks suspension: a deck built over the hole puts the pawns on its floor under it (MOD: 816 kg with one rider)
4aabcf84d code review: mark 74 Pyrelands/LeaningScrub/Cauldron/Contagion files clean after full review
c8f702504 LeaningScrub/Cauldron review fixes: edge-cell ash crash, hoard null-key save, harness gates
706606b0a Contagion review: Unfinished emerge falls back to the patient cell when no standable cell is near
54c670062 ledger: implemented CONTAGION_HEAT_JUDGE_SUN_KIND_UNSAID, SCRUB_SETTINGS_WIRE_MASTER_CANNOT_GREY
5f39eca04 code review: mark 11 LeaningScrub C# files clean (7 kernels, CallingPyre, SweetlineTrees GenStep, RunwayBloom, SmotherCraft)
d322f5f86 CONTAGION_HEAT_JUDGE_SUN_KIND_UNSAID: record judgment, owner review owed
31578071d LeaningScrub settings: declare SettingDependencies so Mod enabled greys its dependents
d3ab7d497 Contagion declares sun heat kind overhead (RM_SunHeatExtension, heatOffsetC 10)
49d5faf8c lesson: helpers re-mark edited files clean after hunk-only reads
8090441be code review: reopen 6 files marked clean after hunk-only review
71608c218 ledger: real landing sha for the two settings items
b2f82ff0e ledger + code_review: settings items closed, 6 files marked clean
428556511 FlowWorks settings: guarded main-screen draw shows its own failure; Suspension registered; main screen + audit sentinel in harness
... 124 more: git log --oneline ec1f6185e..HEAD
```

## Tree state at wrap

- upstream: origin/main, pushed

Uncommitted (replace each marker below with whose it is — yours, another agent's, generated):

```
M Transient/biome_ffar/phase0_remaining_art_sheet_2026-10-16.decisions.json   generated (untracked Transient/deployed scratch, not pinned; Bench/other agents)
 M Transient/modcheck/fixtures.json   generated (untracked Transient/deployed scratch, not pinned; Bench/other agents)
 M conversations/2026-10-18-1908-49cf35a0.md   generated (untracked Transient/deployed scratch, not pinned; Bench/other agents)
 M deployed/config/ModsConfig.before-tier-fw_gss_sitting.xml   generated (untracked Transient/deployed scratch, not pinned; Bench/other agents)
?? Transient/fw_scenes/live/S1_20261017T084726.txt   generated (untracked Transient/deployed scratch, not pinned; Bench/other agents)
?? Transient/fw_scenes/live/S1_20261017T084802.txt   generated (untracked Transient/deployed scratch, not pinned; Bench/other agents)
?? Transient/fw_scenes/live/S1_20261017T092155.txt   generated (untracked Transient/deployed scratch, not pinned; Bench/other agents)
?? Transient/fw_scenes/live/S1_20261017T110253.txt   generated (untracked Transient/deployed scratch, not pinned; Bench/other agents)
?? Transient/fw_scenes/live/S1_p00.png   generated (untracked Transient/deployed scratch, not pinned; Bench/other agents)
?? Transient/fw_scenes/live/S1_p03.png   generated (untracked Transient/deployed scratch, not pinned; Bench/other agents)
?? Transient/fw_scenes/live/S1_p10.png   generated (untracked Transient/deployed scratch, not pinned; Bench/other agents)
?? Transient/fw_scenes/live/S1_p14.png   generated (untracked Transient/deployed scratch, not pinned; Bench/other agents)
?? Transient/fw_scenes/live/S2_20261017T084824.txt   generated (untracked Transient/deployed scratch, not pinned; Bench/other agents)
?? Transient/fw_scenes/live/S2_20261017T092355.txt   generated (untracked Transient/deployed scratch, not pinned; Bench/other agents)
?? Transient/fw_scenes/live/S2_20261017T110404.txt   generated (untracked Transient/deployed scratch, not pinned; Bench/other agents)
?? Transient/fw_scenes/live/S2_p00.png   generated (untracked Transient/deployed scratch, not pinned; Bench/other agents)
?? Transient/fw_scenes/live/S2_p10.png   generated (untracked Transient/deployed scratch, not pinned; Bench/other agents)
?? Transient/fw_scenes/live/S2_p30.png   generated (untracked Transient/deployed scratch, not pinned; Bench/other agents)
?? Transient/fw_scenes/live/S2_p60.png   generated (untracked Transient/deployed scratch, not pinned; Bench/other agents)
?? Transient/fw_scenes/live/S3A_p20.png   generated (untracked Transient/deployed scratch, not pinned; Bench/other agents)
... 136 more uncommitted paths (by top-level dir: Transient 126, deployed 5, src 2, (root) 1, conversations 1, infrastructure 1): git status --short
```

