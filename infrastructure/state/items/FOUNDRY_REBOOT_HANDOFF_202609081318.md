# FOUNDRY_REBOOT_HANDOFF_202609081318 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609080546`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

Before restarting the game or swapping the mod list for ANY bridge-needing item
(this wave's DROIDWORKS_LIVE_LOOP_PROOF_1/A1 among them), check whether the live
session is genuinely stale before trusting `rimflow bridge`'s 45-min staleness
rule alone: `rimworld/get_game_info` + Player.log's own mtime can show a session
that is very much alive (fresh ticksGame, log touched seconds ago, a concurrent
git commit landing mid-turn) even when the bridge ledger says idle for hours.
The ledger measures event silence, not game activity — they can disagree.

## What the owner should see

- `BRIDGE_NTDLL_CRASH_TILEGEN_1` (closed): root cause of the two ntdll.dll crashes
  is Steam Overlay interacting with Mono's heap allocator under memory pressure on
  the full mod list — turning off "Enable the Steam Overlay while in-game" for
  RimWorld in Steam's own settings is the one actionable mitigation, needs his
  hands, not a repo change.
- `NINEFOLD_GRAVSHIP_HOOK_SCOPE_1` (new, filed for OWNER): `Patch_GravshipLaunched`
  has never fired on a real gravship launch — Odyssey's `Building_GravEngine` has
  no `CompLaunchable`, so the patch only ever catches ordinary pods/shuttles.
  Needs his ruling: rescope the existing item as pod/shuttle-only (and file a
  fresh item for real gravship coverage), or retarget the patch to
  `Building_GravEngine`'s own takeoff path.
- `DROID_ORACLE_VOICE_DESIGN_1`: Fable-drafted design for the 4 droid Oracle
  consumers is done and pushed (`design/RimMandrake/droid_oracle_voice_design.md`),
  gated entirely on his read — nothing closes it but that.

## What is half-done, and where it stops

<!-- Anything left mid-flight, and the exact next action. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and the exact next action,
     or close/block it. --check refuses while any is unaccounted
     for, so deleting a line here is not a way past it. -->
- `DROID_ORACLE_VOICE_DESIGN_1` — design complete, pushed (`2038f864`), stays
  `doing` on purpose: the only remaining gate is the owner's read. No next action
  for FOUNDRY/BENCH unless he redlines something.
- `LANTERN_DEEPS_INJECTION_1` — **not touched this window**, carried over from a
  prior FOUNDRY window (claimed 2026-09-08T04:01, before this session started).
  Per its own item file: `RUT_LanternDeepGenerator` + the natural-emergence
  entrance are built and pass `validate_patch.py` clean; the ruined-mineshaft
  entrance is deliberately deferred (needs KCSG/scene-composition authoring).
  **A 2026-09-07 quicktest attempt crashed the game and wiped ModsConfig.xml**
  (recovered via `modlist_swap.py`, no save/world data lost) because the minimal
  test list added `BiomesTeam.BiomesCaverns` without its hard dependency
  `BiomesTeam.BiomesCore`. Exact next action: add `BiomesTeam.BiomesCore` to the
  minimal list alongside the other two Deeps mods, then retry the quicktest.
  Needs a bridge session; ordinary game-up work, no special risk once the
  dependency is added.

## Traps learned

- `git commit`/`add` can hit `.git/index.lock` mid-turn when BENCH's own session
  is committing concurrently in the same shared worktree — not a stale lock to
  force-remove, just retry once it clears (confirmed: `ls .git/index.lock`
  returned "No such file" seconds later). Never `rm` a lock file you haven't
  confirmed is abandoned.
- `python.exe` (WSL calling into Windows Python for bridge scripts) cannot open a
  script path under `/tmp/...` or the scratchpad — it needs a path under
  `D:\Luke\dev\Rimworld`. Write bridge test scripts into `Transient/` and run
  with a repo-relative path, not the scratchpad dir.

## Closed since the last handoff (2)

- `DEV_LOG_AUTOOPEN_SUPPRESS_1` — 547d1c2b4695f5d6f72d33aadaa24682391e79cc
- `BRIDGE_NTDLL_CRASH_TILEGEN_1` — 09041ee2a85a46c2bbf300b1c0291bbb9301c3fa

## Filed and still open (11) — the next seat's queue

- `WORLD_FEATURE_LABELS_OVERSIZED_1` — World feature labels render HUGE and overlap the globe -- our maxDrawSizeInTiles multiplier is 1.63x vanilla's
- `BIOME_LABEL_CAMPAIGN_NAMES_1` — Relabel the 26 donor biomes to their campaign names -- the planet currently shows 'Cypre Jungle', 'Mycotic Jungle', 'GRimond' instead of the Greentide
- `SCALD_DARK_TOWER_1` — Dark tower in the Scald: Rakatan high command, Rust Cathedral control systems, ocular warped Assailant intrusion
- `WORLDMAP_BIOME_ICONS_REGEN_1` — Worldmap biome decoration icons (e.g. Blue Desert saguaro) don't auto-update with plant/animal reassignment
- `BIOME_FLORA_ROSTER_GAP_1` — biome_flora.py's own --check finds 2 stale + 8 unrostered placed biomes (HorrorWastes, BMT_CrystalCaverns dead; BiomeGRimond/RUT_TheScald/RUT_PropaneL
- `RAIN_BAN_SCOPE_DRIFTED_1` — The 2026-08-21 rain-ban ruling's scope no longer matches the world (364 tiles across 17 biomes now, was 363 AB_FeraliskInfestedJungle-only)
- `ASHKARR_NIGHTSIDE_LAYER_SUPERSEDED_1` — ashkarr_layer_nightside.py's carve targets (HorrorWastes, BMT_CrystalCaverns) are both dead/banned; owner's above-freezing RockyCrags ruling may still
- `ASHKARR_REGATE_RAIN_DEAD_1` — ashkarr_regate_rain.py is a permanently non-viable dead-file candidate (99% reproduction gate can never pass; replacement already shipped)
- `W9_RUN_STAGE_RESULTS_UNCHECKED_1` — w9_run.py logs stage bridge-call results but never checks success before continuing to the next stage
- `WAR_LAB_CRATER_HOOK_1` — Ignition->crater world-tile mutation C# hook for the war lab, blocked on LIQUID_BIOMES_MAP_1's frozen footprint
- `NINEFOLD_GRAVSHIP_HOOK_SCOPE_1` — Patch_GravshipLaunched never fires on a real gravship launch (CompLaunchable isn't on Building_GravEngine) -- rescope as pod/shuttle-only, or retarget

## Commits

```
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
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-09-08T13:11:58Z

Uncommitted (say for each whether it is yours or another seat's):

```
M deployed/config/Mod_3272330410_AtmosphereMod.RINGTEX-fixed-20260908.xml
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
?? world/_crags_now.py
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
?? world/crag_landmarks.py
?? world/crag_landmarks_plan.json
?? world/pf_meander.py
?? world/pf_meander_plan.json
?? world/pfm_apply.py
```

