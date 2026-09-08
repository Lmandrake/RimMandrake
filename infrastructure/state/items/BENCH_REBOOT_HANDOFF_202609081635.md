# BENCH_REBOOT_HANDOFF_202609081635 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202609081448`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

🔴 **/mnt/d (drvfs) served STALE reads cross-process for minutes**: after a peer's
git activity, `grep`, `tail` AND `git status` all agreed my uncommitted dashboard
work was reverted — it never was; the writes were durable all along. Before ANY
recovery action on a "my changes vanished" signal on this mount, wait a minute
and re-read from a fresh process; several stale readers agreeing is one reader,
not corroboration. (In memory as drvfs-stale-reads-mimic-revert; LESSONS_INBOX'd.)

## What the owner should see

1. **The maturity dashboard is the product now**: 77 systems, 55/77 runnable+
   (34 runnable / 21 validated) after his 4 rulings landed —
   https://claude.ai/code/artifact/f42444c1-f577-4a28-8e58-a157575cb204
2. **Nine review packets await his decisions** (all parked needs=owner, each with
   the recommendation drafted): mutation deck, Alpha mechanics picks, ancient-ruins
   cut, crystal ingest, gizka spec, brain-worm spec (living-only vs corpse-walker
   fork), staged-lore go/no-go, memory-reduction options A–F, flora rosters at the
   assignment sitting.
3. **Shipped with a flag raised**: 27 UNCERTAIN→runnable promotions carry his
   ruling verbatim in their evidence refs; the Webwork amendment only settles
   what the Rakata did NOT make (identity was already standing ruling).
4. **Thornbelt is no longer far-ring by water** (38.7°→13.7°, a meandered river
   runs close) — deep_desert.md table updated, his eye wanted if the region's
   character mattered to him.

## What is half-done, and where it stops

<!-- Anything left mid-flight, and the exact next action. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and the exact next action,
     or close/block it. --check refuses while any is unaccounted
     for, so deleting a line here is not a way past it. -->
- `ALPHA_FAMILY_SOURCE_REVIEW_1` — review written+committed; parked needs=owner for mechanic picks (no license on either repo — clean-room only). Next action: his picks at a sitting.
- `ANCIENT_RUINS_MOD_AUDIT_1` — audit written+committed; verdict cut-family-via-Cherry-Picker; parked needs=owner. Next: his ruling, then a separate removal ticket (read the ComplexLayout extension first).
- `BIOME_FLORA_ROSTER_GAP_1` — stale half DONE (2 dead biomes superseded in biome_flora.py); roster half waits for BIOME_FAUNA_ASSIGNMENT_SITTING_1 by the sheet-drives-roster ruling. Parked needs=owner.
- `CRYSTAL_MODS_INGEST_1` — inventory written+committed (orange = KOTOR_SmallCrystal_orange, ours); parked needs=owner for ingest decisions. Sibling drift filed: KOTOR_CRYSTAL_GENSTEP_DRIFT_1.
- `GEONOSIAN_BRAINWORM_MORPH_1` — both research halves done, spec committed (design/RimStarWars/brain_worm_spec.md); parked needs=owner on the living-only vs corpse-walker fork.
- `GIZKA_TRIBBLE_ADAPTATION_1` — spec committed (design/RimStarWars/gizka_ship_pest_spec.md), donor examined inactive, art absence MEASURED; parked needs=owner for review.
- `MUTATION_MODIFIERS_SURVEY_1` — survey committed (mutation_modifiers_survey.md); Contagion-touched deck proposed; parked needs=owner. Key law: never split boon/cost across two hediffs.
- `STAGED_LORE_DESCRIPTIONS_1` — FEASIBLE verdict committed on the item (def-field mutation route, one cache trap named); parked needs=owner for go/no-go.

## Traps learned

1. The drvfs stale-read trap above — the wave's big one.
2. **A peer's `git reset --hard HEAD` appeared in reflog mid-session** (harmless
   this time only because my files were already written). The forbidden
   destructive act in a shared tree; in LESSONS_INBOX.
3. **The canon CSV biome column trap is now instrumented**: `biome_sheet_stats.py`
   applies the 8 overlays and is calibrated (3/3 golden sheets exact); its
   `--from-water` metric reproduced 5/6 pre-repaint values. Use it, never the
   bare CSV.
4. **biome_flora.py --check's tile counts are for gap-detection only** — they
   disagree with the V23 mosaic (it reads a pre-overlay source); don't cite them.
5. `rimflow capability retire` now exists (removes a row; ledger keeps history) —
   added for the Spikes fold; `played` stays owner-only.

## Closed since the last handoff (8)

- `PROJECT_MATURITY_DASHBOARD_1` — 78fe3b38
- `MATURITY_DASHBOARD_DENSITY_1` — 80e38de9
- `LANES_DOCTRINE_PARAGRAPH_1` — 71753752
- `RAKATAN_LEGACY_INDEX_1` — 6180f961
- `GOLDEN_SHEET_REFRESH_1` — b8b65eb4
- `WATER_KINDS_TAXONOMY_1` — cb7c9057
- `MOD_VALIDATION_PLAN_AUTHORING_1` — cb7c9057
- `SHEET_SUBMEASURE_REFRESH_1` — 4de53d06

## Filed and still open (7) — the next seat's queue

- `BRIDGETOOLS_DLL_GM_DRIFT_1` — JawaBench DLL is 41 tools behind source (built without GM pair); selftest_tool_metadata FAILs until companion rebuild+redeploy on a game-down window
- `UTINNI_SHELL_DEFNAME_BUG_1` — UtinniShell emits Config error every full-list load: defName 'Utinni Shellmandrake.rut.shell' — name and packageId concatenated somewhere in its def a
- `STARWARSRACES_TOOLBOX_SOFT_DEP_1` — StarWarsRaces DefModExt_HeadTypeStuff depends on neronix17.toolbox with no MayRequire — every HeadTypeDef silently vanishes if Tabula Rasa goes inacti
- `RAIDREDESIGNER_HARD_PROPERTY_REF_1` — RaidRedesigner DLL hard-references RimMandrakeProperty (PropertyEngine.Fire) but About.xml declares only soft loadAfter — declare the hard dep or guar
- `ASHKARR_FLORA_SWEETLINE_ART_UNWIRED_1` — AshkarrFlora RUT_SweetlineTree texture folder is empty; 11 candidate PNGs sit unmoved in _artsrc — wire or cut (walk-authoring find)
- `LANTERNDEEPS_GENSTEP_ALLOWLIST_DEAD_1` — LanternDeeps GenStep biome allowlist names biomes from mods its About.xml never declares — on most lists the scatter step silently never fires (walk-a
- `KOTOR_CRYSTAL_GENSTEP_DRIFT_1` — Deployed KOTOR_CrystalFormation genstep scatters only Stygium; repo's absorbed copy lists 12 crystal variants — diff repo vs deployed, redeploy or pul

## Commits

```
8d64f329 Crystal mods inventory: orange crystal = KOTOR_SmallCrystal_orange (ours via Armoury); 6 systems catalogued
c13d35c0 biome_flora.py: supersede HorrorWastes + BMT_CrystalCaverns entries (BIOME_FLORA_ROSTER_GAP_1)
4de53d06 from-water metric calibrated + deep_desert far-ring table refreshed; ancient-ruins audit landed
2a76e9e0 Staged lore descriptions: FEASIBLE verdict, def-field mutation route, one cache trap named
a5cae96c Alpha family source review: no license = no code reuse; 6 mechanics to reimplement
46cafe02 Memory-audit synthesis digest + mutation modifiers survey
2175f938 Ledger sync: gizka + brainworm specs claimed/parked on owner; sub-measure notes
acfdbd05 Brain worm design spec: Space Worms donor read + canon cited, def plan for owner review
804a817c Gizka ship-pest design spec: Tribble module examined, donor art absence MEASURED
a9d5d251 Live-verify B1/B2 on the redeployed build: B1's need-gating fails live, B2 root-caused to a platform-wide apparelMoney gap
4ae1ac59 Sub-measure refresh: hilliness/rain-zero/per-region stats in the instrument; 5 sheets' flagged fractions fixed
fbd74868 rimflow: claim/start/block DROIDWORKS_MODULE_ABSORB_1
c6b9b7d9 DROIDWORKS_MODULE_ABSORB_1: absorb KotOR droid module apparel (hardware/software/sensor + armor)
2f60c5dc Close DROIDWORKS_DETONATION_REVIEW_1 (ledger sync)
72c58ea2 Ledger sync: sitting closes (ring, water, walks) + 4 walk-finding items filed
cb7c9057 Validation walks for all 77 systems + four owner rulings (2026-09-08 sitting)
7c5f48b2 ARMOURY_CROSSFILE_ADD_REPLACE_ORDER_1: close as resolved by 1974a7c6
e3333bed Sync ledger: DROIDWORKS_FORMAT_TIERS_1 claimed, started, blocked on live quicktest
b81a023b Droidworks B1: format tiers (blank/mindless/programmable/sapient)
b380f413 Water taxonomy as data: 19 kinds, 3 not-water, transmutations pending owner ruling (WATER_KINDS_TAXONOMY_1)
b8b65eb4 Golden stat-refresh: 18 biome sheets re-measured against the V23 world
1974a7c6 Fix ARMOURY_PATCH_INNER_MISS_1: 3 FindMod inner-match failures, 2 root causes
6180f961 Rakatan engineered-legacy index: 5 ruled + 1 open (the Webwork question)
71753752 Lanes doctrine paragraph in the biome grammar README (LANES_DOCTRINE_PARAGRAPH_1)
80e38de9 Dashboard pass 3 (review-agent findings): stale loses the reserved yellow, DATA.weighting rendered, needs-owner tile, GOAL_SHEET per-box tooltips, updated-by in hover card, unknown-review tile when nonzero
a7c1dc2c biome_sheet_stats.py: V23 per-biome stats via CSV + 8 overlay plans
e4e32de0 Dashboard pass 2: ladders read most-mature-first, matching the matrix
cbc0a871 DROIDWORKS_LIVE_LOOP_PROOF_1: live-prove the five-state loop on GNK + KotOR kind
03c9db14 LESSON: drvfs stale reads mimic a hard revert; peer reset --hard in reflog
c8c206a9 Maturity dashboard v2: dense rework + 28 evidence-based rung promotions
cbd371cc Resolve KOTORCORE_ADAPTIVESTORAGE_PARENTNAME_1: false alarm, no fix needed
807ce1c9 Fold Spikes into their mods; add rimflow 'capability retire' (owner ruling)
f56dc9d4 world_lint: fix landBiomeSubmerged hard-coded water biome check
77dccf02 Maturity grid: real mod names, tier colors, hover cards, progress chips
c672bfda Maturity dashboard: restore the 70s brown palette from the seed-proposal page
6b8739da Ledger sync: close PROJECT_MATURITY_DASHBOARD_1 at 78fe3b38
78fe3b38 Seed maturity capability registry: 78 systems from the folder survey
0057dd3c FOUNDRY reboot handoff 202609081453: fill in judgment sections
076f2185 Mark handoff.py + selftest_handoff.py CLEAN; sync ledger
6204e16b Fix handoff.py: since_ts compared a local-offset git timestamp against UTC ledger timestamps
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running; BRIDGE NOT PROBED — no port found in the environment or in Player.log, so LOADING here is a DEFAULT, not a reading.)
- recorded  : LOADING
- Bridge: for     full-list cold load to verify ARMOURY_PATCH_INNER_MISS_1 (patchfail 8->5) and WORLD_LINT_WATER_HARDCODE_1 (landBiomeSubmerged 1135->0)

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

