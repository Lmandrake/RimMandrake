# FOUNDRY_REBOOT_HANDOFF_202609080546 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609072130`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

The 2026-09-07 savegame-export rebase (biome changed on 5,411 tiles, hilliness on 7,275)
plus the sea rename (`LIQUID_BIOMES_MAP_1`: Ocean → `RUT_TwilightSea`/`RUT_GreySea`) and
the HorrorWastes/BMT_CrystalCaverns dissolves together broke a WHOLE CLASS of `ashkarr_*`
one-shot map-edit scripts that hardcode a pre-rebase biome-composition premise into their
`--apply` control flow, not just their docstrings. Three of them (`ashkarr_layer_nightside.py`,
`ashkarr_nightside_pass.py`, `ashkarr_shore_and_ice.py`) would have silently written a
dissolved or banned biome back onto the worldmap if re-run today — the worst, `ashkarr_shore_and_ice.py`,
would have repainted 503+ tiles of the CURRENTLY LIVE Twilight/Grey Sea to desert. All three
now hard-refuse `--apply` with a clear message instead. **If you find another `ashkarr_*`
script with a hardcoded biome name and a 2026-08-2x docstring, re-derive its premise LIVE
against the current CSV before trusting it — don't assume the docstring.** Full list of
what's fixed vs. what's still an open owner question is in the `DIRTY_CODE_REVIEW_STANDING_LOOP_1`
wave notes and the items listed below.

## What the owner should see

Three real decision forks filed, not guessed at:
- `RAIN_BAN_SCOPE_DRIFTED_1` — the 2026-08-21 rain-ban ruling ("no rain below hilliness 4")
  now matches 364 tiles across 17 biomes on live data, not the original 363
  `AB_FeraliskInfestedJungle`-only tiles the ruling reasoned about. Needs a call: apply the
  wider scope as originally worded, or re-scope to jungle-only.
- `ASHKARR_NIGHTSIDE_LAYER_SUPERSEDED_1` — the "eliminate RockyCrags above freezing" ruling
  looks currently VIOLATED on live data (samples up to +15°C found), but the script that
  used to enforce it wrote to two now-dead/banned biomes and can't just be re-run. Needs a
  fresh mechanism, and the owner's call on what above-freezing RockyCrags should become now.
- `WORLDMAP_BIOME_ICONS_REGEN_1` (earlier this window) — the little per-biome worldmap icons
  (e.g. Blue Desert's saguaro) were never wired to `wildPlants`/`wildAnimals` at all — there's
  no "regenerate" fix, only a manual retuning pass once the owner says which icon sets should
  change.

Also worth his eye: `BIOME_FLORA_ROSTER_GAP_1` — `biome_flora.py`'s own `--check` found 8
currently-placed biomes (including `RUT_TheScald`, the three seas, `BiomeGRimond`/"Blue
Desert") with zero flora roster assigned through that pipeline at all.

Filed a memory-footprint deep-dive per his own request (`RIMWORLD_MEMORY_FOOTPRINT_AUDIT_1`,
for BENCH) — disk-side legwork done (peak RSS 20.17GB confirmed; the actual crash looked
like a native access-violation, not OOM), live RSS profiling still owed.

## What is half-done, and where it stops

<!-- Anything left mid-flight, and the exact next action. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and the exact next action,
     or close/block it. --check refuses while any is unaccounted
     for, so deleting a line here is not a way past it. -->
- `LANTERN_DEEPS_INJECTION_1` — the injection mechanism is BUILT and committed
  (`src/RimUtinni/LanternDeeps/`: MapGeneratorDef, entrance ThingDef with collapse hazard,
  a new C# GenStep that self-gates placement to the three correct host biomes, all
  validated 0 errors). First quicktest attempt crashed the game because I forgot Biomes!
  Caverns' own hard dependency, `BiomesTeam.BiomesCore`, when hand-editing the minimal
  test mod list — RimWorld's own recovery reset kicked in, no save/data lost, only the
  live mod list was affected (already restored). **Exact next action**: next time the
  bridge is free, add `BiomesTeam.BiomesCore` alongside `m00nl1ght.GeologicalLandforms` +
  `BiomesTeam.BiomesCaverns` + `mandrake.rut.lanterndeeps` to the mod list, restart, and
  run the actual quicktest (reach a Deep through the entrance, confirm enclosed/dark,
  kyber spawns via the already-absorbed `BMT_CrystalsGenerator` patch, persists across two
  visits). The ruined-mineshaft second entrance type (item spec 2b) is still unbuilt —
  deferred, needs KCSG/scene-composition authoring, not started.

## Traps learned

- **`TaskOutput(block=false)` on a running local_agent subagent dumps the FULL raw JSONL
  transcript into your context, not a status summary, even though `retrieval_status` reads
  `not_ready`.** Cost several thousand tokens across 4 tasks in one call. Sent as product
  feedback this session. Do not poll subagent status this way — wait for the
  `<task-notification>`, or check a plain Bash `run_in_background` task's output file
  instead (that's fine to Read directly).
- **Re-running a generator against a much-newer live capture produces a diff dominated by
  capture drift, not your fix.** Verifying the `gen_cast_patch.py` PAWNKINDS fix produced a
  20,484-line diff on `BiomeCast_Ashkarr.xml` — almost entirely from a newer/larger def dump
  than whatever last generated the committed file, not from the one-line fix. Reverted the
  regenerated output, kept only the code fix. Always diff a generator's live-verification
  output to a scratch path (`--out <tmp>`), never let it overwrite the real committed
  artifact in place.
- **`git commit` can hit `index.lock` mid-session from a genuinely concurrent peer (BENCH)
  writing to the same working tree** — happened twice this window. Don't force-remove the
  lock; wait ~5s and retry, then re-check `git status` before re-committing (staged changes
  usually survive).
- **A recursive `glob('**/*.frozen.json')` over the repo root can go from instant to a full
  30s+ timeout depending on concurrent filesystem load on this Windows-mounted drive** —
  observed while BENCH was actively writing many files into `world/_roads/meander_v12/`.
  Confirmed environmental (still slow after removing the test file that triggered the
  first observation), not a code bug — don't mistake it for a regression if you see it again.
- **`biome_flora.py`'s own `--check`/`--doc`/`--write` and `w9_run.py` etc. all resolve paths
  relative to CWD in places** — always `cd` to the repo root before running any of these
  Utils scripts directly; running one from inside a subdirectory (e.g. `design/Jawa/mods/`)
  silently breaks the NEXT script you invoke in the same shell if you forget to `cd` back.

## Closed since the last handoff (2)

- `VEHICLE_FUEL_PATCH_UNFILTERED_1` — d4fcfcf2760e968b144d332c6435908fe2af8884
- `CODEX_PARALLEL_WORKERS_1` — 855cb4e6d4b0a2c944c1a64a56864c82d4ec1718

## Filed and still open (19) — the next seat's queue

- `ARMOURY_DECLARER_ATTRIBUTION_FLIP_1` — gen_armour_patch.py's declarer() flips guy762_*/KotOR* ops between own-mod (Conditional) and donor (FindMod) attribution run-to-run
- `IKEE_MYNOCK_ART_REGEN_1` — Regenerate Ikee (AA_Eyeling) and Mynock art via the improved Codex/native-transparency pipeline
- `SCALD_RIVER_REPAINT_1` — Redirect the Scald's rivers outward on the painted worldmap to match R1 -- R18 step 2, blocked on ASHKARR_RIVER_LEDGER_1, verify tile-by-tile
- `BLIZZARISK_DONOR_CUT_1` — Cherry Picker cut of the Blizzarisk donor def -- R20, owner: donor creature not our canon, remove it from the game
- `GEOTHERMAL_DENSITY_FIELD_1` — Geothermal vent/geyser density field: high at dayside mountain ranges, decaying with distance, zero at the terminator -- R12, stop geysers spawning on
- `ARMOURY_CROSSFILE_ADD_REPLACE_ORDER_1` — Armoury_RangedDamage.xml's Replace on OuterRim_Proj_ProtonArtillery/ProtonMortar damageAmountBase runs before Turrets_DamageDoctrine.xml's Add creates
- `ARMOURY_PATCH_INNER_MISS_1` — Jawa Armoury Rebalance: 3 FindMod blocks report failure though all 3 mods are ACTIVE -- an inner xpath is missing (patch failures 8 vs baseline 5)
- `ORACLE_CLIENT_CLAUDE_CODE_REWRITE_1` — Rewrite OracleHttpClient to shell out to claude -p, per owner's 2026-09-05 in-game-LLM ruling (never tracked as an item)
- `UNDERWATER_BIOME_SUPPORT_1` — Underwater biome support: land on the three seas -- looks like ocean, playable seafloor beneath (owner 2026-09-07, later modification)
- `WORLD_LINT_WATER_HARDCODE_1` — world_lint hard-codes Ocean/SeaIce as the only water biomes -- reports all 1135 custom-sea tiles as landBiomeSubmerged
- `WORLD_FEATURE_LABELS_OVERSIZED_1` — World feature labels render HUGE and overlap the globe -- our maxDrawSizeInTiles multiplier is 1.63x vanilla's
- `BIOME_LABEL_CAMPAIGN_NAMES_1` — Relabel the 26 donor biomes to their campaign names -- the planet currently shows 'Cypre Jungle', 'Mycotic Jungle', 'GRimond' instead of the Greentide
- `SCALD_DARK_TOWER_1` — Dark tower in the Scald: Rakatan high command, Rust Cathedral control systems, ocular warped Assailant intrusion
- `WORLDMAP_BIOME_ICONS_REGEN_1` — Worldmap biome decoration icons (e.g. Blue Desert saguaro) don't auto-update with plant/animal reassignment
- `BIOME_FLORA_ROSTER_GAP_1` — biome_flora.py's own --check finds 2 stale + 8 unrostered placed biomes (HorrorWastes, BMT_CrystalCaverns dead; BiomeGRimond/RUT_TheScald/RUT_PropaneL
- `RAIN_BAN_SCOPE_DRIFTED_1` — The 2026-08-21 rain-ban ruling's scope no longer matches the world (364 tiles across 17 biomes now, was 363 AB_FeraliskInfestedJungle-only)
- `ASHKARR_NIGHTSIDE_LAYER_SUPERSEDED_1` — ashkarr_layer_nightside.py's carve targets (HorrorWastes, BMT_CrystalCaverns) are both dead/banned; owner's above-freezing RockyCrags ruling may still
- `ASHKARR_REGATE_RAIN_DEAD_1` — ashkarr_regate_rain.py is a permanently non-viable dead-file candidate (99% reproduction gate can never pass; replacement already shipped)
- `W9_RUN_STAGE_RESULTS_UNCHECKED_1` — w9_run.py logs stage bridge-call results but never checks success before continuing to the next stage

## Commits

```
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
c7cec91e BENCH reboot handoff 202609072200: the savegame is the world
5cc2750f LANTERN_DEEPS_INJECTION_1: ship the injected cave-map layer mechanism
bcccb196 File RIMWORLD_MEMORY_FOOTPRINT_AUDIT_1 and WORLDMAP_BIOME_ICONS_REGEN_1
492df215 Record allocate_cast.py clean mark in CODE_REVIEW_STATUS.json
9f9a2e77 Recover the live 599-mod list from the savegame itself, and keep it durably
582e9432 Remove dead median() helper and unused math import from allocate_cast.py
c77a003b ANCIENT_WAR_LAB_1: record map-mutation engine scoping research
052b07b5 The Rust Cathedral gets its icons; the propane lake stops being invisible
bdaaf62a LANTERN_DEEPS_INJECTION_1: record MEASURED BMT_CrystalCaverns placement finding
34bb9156 Reconcile ANCIENT_WAR_LAB_1 with wasteland §10; split out SCALD_DARK_TOWER_1
12e0766f Deep Desert Tribes scattered across the desert instead of strung along it
aa0380ce No modern road past -10 C: the cold half of the net becomes ancient asphalt
9ec29669 The intended biomes land on the real planet: three seas, Blue Desert, Contagion, propane lake
5b0fb464 The savegame is the world: canonical CSVs rebased from WORLDMAP_V1_original_e
0b1ad5a5 Skills: the five world-repaint lessons from the vanilla-water closeout
361dddfd The last two vanilla water biomes leave Ash'karr: 262 SeaIce and 10 Lake tiles
466e7595 Restamp the tiles CSV freeze marker after the oasis edit
4b164065 BENCH reboot handoff 202609072318: worldmap complete, three seas live, four fixes riding this restart
f9717f5a Oasis line broken up: 32 of 51 road-hugging oasis tiles replaced by their dry neighbours
3e063c2f Note on OASIS_LANDMARK_PLACEMENT_1: roads follow oases by design, measured 3.5x
78697ca1 BIOME_LABEL_CAMPAIGN_NAMES_1: 26 of 30 painted biomes show donor labels, not campaign names
864ac9a5 All our biomes allow roads (owner ruling); world-feature label multiplier 2.2 -> 1.35
6733b891 Retrospective filed as TWO items per owner ruling: automated walk + human exploration
ac8ae245 WORLD_FEATURE_LABELS_OVERSIZED_1: filed -- our label multiplier is 1.63x vanilla
234da798 PROJECT_MATURITY_DASHBOARD_1 filed; cold-load figure corrected to ~15 min on 599 mods
77752af7 Worldmap redo COMPLETE: 21872/21872 tiles, 0 mismatches, the three seas are on the planet
ea547771 WORLD_LINT_WATER_HARDCODE_1: filed -- lint hard-codes Ocean/SeaIce, flags all 1135 custom-sea tiles
ccbe3809 RUST_CATHEDRAL_MECHANICS_1: owner rules the roaches out of the hum mechanics
dfa58f0e RUST_CATHEDRAL_MECHANICS_1: enhanced with the roach reskin (owner 2026-09-07)
931dde5a Decision strings for the GravTide + three-seas load, written before launch
8e4bce2b Sea biomes drafted for GravTide: terrainsByFertility, weather, wander ban; Scald description to R1
b110e188 Worldmap redo: session outcome -- merge complete, rivers laid, new colony, R36 diff passed
ed79d53a UNDERWATER_BIOME_SUPPORT_1: the mechanism exists -- GravTide, subscribed but inactive
20477dce UNDERWATER_BIOME_SUPPORT_1: filed -- land on the three seas, seafloor beneath
9897eb63 Worldmap: FungalForest merged into 5 neighbours (425 tiles); all 16 rivers reordered mouth-first
7d5bc53c Rulings R37-R39: Scald sources at the shore; riverDist is noise not a direction; tile 16869 ruling
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: for     BENCH: V10 loaded post-restart; placing 261 complex-structures landmarks, then per-biome worldmap passes

Uncommitted (say for each whether it is yours or another seat's):

**None of the below is mine.** Every biome `.md`, `ModsConfig.FULL.LATEST.xml`,
`queue/BENCH.md`, the `world/_roads/meander_v12/*` and `world/backside_reband*` files, and
the various `Transient/`/lock/fact files are BENCH's live in-progress work (the 261
landmarks + per-biome worldmap passes mentioned in the bridge line above) or pre-existing
session noise from before this window started. I did not touch any of it — do not let a
future seat assume it's FOUNDRY's to clean up or revert.

```
M design/Jawa/worldbuilding/biomes/arid_shrubland.md
 M design/Jawa/worldbuilding/biomes/deep_desert.md
 M design/Jawa/worldbuilding/biomes/desert.md
 M design/Jawa/worldbuilding/biomes/forsaken_crags.md
 M design/Jawa/worldbuilding/biomes/poison_forest.md
 M design/Jawa/worldbuilding/biomes/the_blue_desert.md
 M design/Jawa/worldbuilding/biomes/the_contagion.md
 M design/Jawa/worldbuilding/biomes/the_cracked_lands.md
 M design/Jawa/worldbuilding/biomes/the_fever_wood.md
 M design/Jawa/worldbuilding/biomes/the_forge.md
 M design/Jawa/worldbuilding/biomes/the_greentide.md
 M design/Jawa/worldbuilding/biomes/the_miasma.md
 M design/Jawa/worldbuilding/biomes/the_propane_lakes.md
 M design/Jawa/worldbuilding/biomes/the_pyrelands.md
 M design/Jawa/worldbuilding/biomes/the_rust_cathedral.md
 M design/Jawa/worldbuilding/biomes/the_scarlands.md
 M design/Jawa/worldbuilding/biomes/the_slime.md
 M design/Jawa/worldbuilding/biomes/the_sump.md
 M design/Jawa/worldbuilding/biomes/the_webwork.md
 M design/Jawa/worldbuilding/biomes/wasteland.md
 M design/Jawa/worldbuilding/biomes/weeping_stones.md
 M infrastructure/state/codebase_health_last.json
 M infrastructure/state/items/IKEE_MYNOCK_ART_REGEN_1.md
 M infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml
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
?? world/backside_reband.py
?? world/backside_reband_plan.json
```

